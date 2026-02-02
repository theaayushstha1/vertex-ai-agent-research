"""
CS Navigator - Main Orchestrator
=================================

The "brain" of the agent system. CS Navigator:
1. Receives queries from users
2. Classifies what type of question it is
3. Routes to appropriate agent(s)
4. Runs agents IN PARALLEL for speed
5. Uses consensus to pick the best answer
6. Delegates MCP actions (email, calendar)

This mirrors your Vertex AI "CS Navigator" agent that routes queries
to specialized sub-agents.

LANGGRAPH INTEGRATION:
---------------------
We use LangGraph to build a graph-based workflow:

    START → classify → route → [parallel agents] → consensus → END
                                      ↓
                               [MCP actions]

LangGraph gives us:
- State management across the workflow
- Parallel execution support
- Easy debugging and visualization
- Checkpoint/resume capabilities
"""

import asyncio
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set

from langchain_google_vertexai import ChatVertexAI
from langgraph.graph import StateGraph, END

from ..agents.base import AgentResponse, BaseAgent
from ..agents.academic_advisor import AcademicAdvisor
from ..agents.career_guidance import CareerGuidance
from ..agents.course_recommender import CourseRecommender
from ..agents.schedule_builder import ScheduleBuilder
from ..agents.degreeworks import DegreeWorks
from ..agents.general_qa import GeneralQA
from ..agents.financial_aid import FinancialAid
from .consensus import ConsensusSelector


class QueryCategory(Enum):
    """
    Categories of queries that determine which agents to invoke.

    Each category maps to one or more agents.
    """
    ACADEMIC = "academic"  # Courses, requirements, faculty
    CAREER = "career"  # Jobs, internships, resume
    COURSES = "courses"  # Course recommendations
    SCHEDULE = "schedule"  # Class scheduling
    PROGRESS = "progress"  # Degree progress, DegreeWorks
    GENERAL = "general"  # General questions
    FINANCIAL = "financial"  # Financial aid, scholarships


# Map categories to agent classes
CATEGORY_AGENTS = {
    QueryCategory.ACADEMIC: ["AcademicAdvisor"],
    QueryCategory.CAREER: ["CareerGuidance"],
    QueryCategory.COURSES: ["CourseRecommender", "AcademicAdvisor"],
    QueryCategory.SCHEDULE: ["ScheduleBuilder"],
    QueryCategory.PROGRESS: ["DegreeWorks", "AcademicAdvisor"],
    QueryCategory.GENERAL: ["GeneralQA"],
    QueryCategory.FINANCIAL: ["FinancialAid"],
}

# Keywords for classification
CATEGORY_KEYWORDS = {
    QueryCategory.ACADEMIC: [
        "advisor", "faculty", "professor", "requirement", "prerequisite",
        "degree", "major", "minor", "gpa", "academic"
    ],
    QueryCategory.CAREER: [
        "job", "internship", "career", "resume", "interview", "salary",
        "company", "industry", "work", "employment", "hiring"
    ],
    QueryCategory.COURSES: [
        "course", "class", "recommend", "take", "next semester", "elective",
        "cosc", "what should i take"
    ],
    QueryCategory.SCHEDULE: [
        "schedule", "time", "conflict", "when", "morning", "afternoon",
        "mwf", "tth", "credits"
    ],
    QueryCategory.PROGRESS: [
        "degreeworks", "graduation", "graduate", "how many credits",
        "remaining", "completed", "audit"
    ],
    QueryCategory.GENERAL: [
        "where", "who", "office", "contact", "deadline", "registration",
        "drop", "add", "withdraw"
    ],
    QueryCategory.FINANCIAL: [
        "fafsa", "scholarship", "financial aid", "tuition", "payment",
        "loan", "grant", "work study", "money"
    ],
}


@dataclass
class NavigatorState:
    """
    State object passed through the LangGraph workflow.

    This holds all information as the query flows through the system.
    """
    query: str = ""
    categories: List[QueryCategory] = field(default_factory=list)
    selected_agents: List[str] = field(default_factory=list)
    responses: List[AgentResponse] = field(default_factory=list)
    best_response: Optional[AgentResponse] = None
    mcp_actions: List[Dict[str, Any]] = field(default_factory=list)
    error: Optional[str] = None


class CSNavigator:
    """
    Main orchestrator that routes queries to specialized agents.

    Example usage:
        navigator = CSNavigator(llm=vertex_ai_llm)
        response = await navigator.ask("What courses should I take next semester?")
        print(response.answer)
    """

    def __init__(
        self,
        llm: ChatVertexAI,
        knowledge_base: Optional[Dict[str, Any]] = None,
        max_parallel_agents: int = 4,
        timeout_seconds: int = 30,
    ):
        """
        Initialize the CS Navigator.

        Args:
            llm: Vertex AI LLM instance
            knowledge_base: Optional dict with knowledge for all agents
            max_parallel_agents: Max agents to run simultaneously
            timeout_seconds: Timeout for each agent
        """
        self.llm = llm
        self.knowledge_base = knowledge_base or {}
        self.max_parallel_agents = max_parallel_agents
        self.timeout_seconds = timeout_seconds

        # Initialize consensus selector
        self.consensus = ConsensusSelector()

        # Initialize all agents
        self.agents: Dict[str, BaseAgent] = self._init_agents()

        # Build LangGraph workflow
        self.workflow = self._build_workflow()

    def _init_agents(self) -> Dict[str, BaseAgent]:
        """Initialize all specialized agents."""
        return {
            "AcademicAdvisor": AcademicAdvisor(
                llm=self.llm,
                knowledge_base=self.knowledge_base.get("academic"),
            ),
            "CareerGuidance": CareerGuidance(
                llm=self.llm,
                knowledge_base=self.knowledge_base.get("career"),
            ),
            "CourseRecommender": CourseRecommender(
                llm=self.llm,
                knowledge_base=self.knowledge_base.get("courses"),
            ),
            "ScheduleBuilder": ScheduleBuilder(
                llm=self.llm,
                knowledge_base=self.knowledge_base.get("schedule"),
            ),
            "DegreeWorks": DegreeWorks(
                llm=self.llm,
                knowledge_base=self.knowledge_base.get("degreeworks"),
            ),
            "GeneralQA": GeneralQA(
                llm=self.llm,
                knowledge_base=self.knowledge_base.get("general"),
            ),
            "FinancialAid": FinancialAid(
                llm=self.llm,
                knowledge_base=self.knowledge_base.get("financial"),
            ),
        }

    def _build_workflow(self) -> StateGraph:
        """
        Build the LangGraph workflow.

        The workflow is:
        START → classify → route → execute_agents → select_best → END
        """
        # Create the graph
        workflow = StateGraph(NavigatorState)

        # Add nodes (steps in the workflow)
        workflow.add_node("classify", self._classify_query)
        workflow.add_node("route", self._route_to_agents)
        workflow.add_node("execute", self._execute_agents)
        workflow.add_node("select", self._select_best)

        # Add edges (flow between steps)
        workflow.set_entry_point("classify")
        workflow.add_edge("classify", "route")
        workflow.add_edge("route", "execute")
        workflow.add_edge("execute", "select")
        workflow.add_edge("select", END)

        return workflow.compile()

    def classify_query(self, query: str) -> List[QueryCategory]:
        """
        Classify a query into categories based on keywords.

        This is a simple keyword-based classifier. A more sophisticated
        implementation could use embeddings or the LLM itself.

        Args:
            query: The user's question

        Returns:
            List of matching QueryCategory values
        """
        query_lower = query.lower()
        matches = []

        for category, keywords in CATEGORY_KEYWORDS.items():
            if any(kw in query_lower for kw in keywords):
                matches.append(category)

        # Default to GENERAL if no matches
        if not matches:
            matches.append(QueryCategory.GENERAL)

        return matches

    def _classify_query(self, state: NavigatorState) -> NavigatorState:
        """LangGraph node: Classify the query."""
        state.categories = self.classify_query(state.query)
        return state

    def _route_to_agents(self, state: NavigatorState) -> NavigatorState:
        """LangGraph node: Select which agents to invoke."""
        agents_to_use: Set[str] = set()

        for category in state.categories:
            agents_to_use.update(CATEGORY_AGENTS.get(category, []))

        # Limit to max parallel agents
        state.selected_agents = list(agents_to_use)[:self.max_parallel_agents]

        return state

    async def _execute_agents_async(self, state: NavigatorState) -> NavigatorState:
        """Execute selected agents in parallel (async version)."""
        if not state.selected_agents:
            state.error = "No agents selected"
            return state

        # Create tasks for parallel execution
        tasks = []
        for agent_name in state.selected_agents:
            agent = self.agents.get(agent_name)
            if agent:
                # Wrap in asyncio.wait_for for timeout
                task = asyncio.wait_for(
                    agent.ask(state.query),
                    timeout=self.timeout_seconds
                )
                tasks.append(task)

        # Execute all agents in parallel
        try:
            responses = await asyncio.gather(*tasks, return_exceptions=True)

            # Filter out exceptions and collect valid responses
            for response in responses:
                if isinstance(response, AgentResponse):
                    state.responses.append(response)
                elif isinstance(response, Exception):
                    print(f"Agent error: {response}")

        except Exception as e:
            state.error = f"Execution error: {str(e)}"

        return state

    def _execute_agents(self, state: NavigatorState) -> NavigatorState:
        """LangGraph node: Execute selected agents (sync wrapper)."""
        # Run the async version
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(self._execute_agents_async(state))
        finally:
            loop.close()

    def _select_best(self, state: NavigatorState) -> NavigatorState:
        """LangGraph node: Select the best response using consensus."""
        if not state.responses:
            state.error = "No responses received"
            return state

        # Use consensus selector
        best, scored = self.consensus.select_best(state.responses, state.query)
        state.best_response = best

        # Collect any MCP actions from the best response
        if best.needs_action:
            state.mcp_actions.append({
                "type": best.action_type,
                "params": best.action_params,
            })

        return state

    async def ask(self, query: str) -> AgentResponse:
        """
        Ask a question and get the best response from the appropriate agent(s).

        This is the main entry point for users.

        Args:
            query: The user's question

        Returns:
            AgentResponse with the best answer

        Example:
            response = await navigator.ask("What courses should I take?")
            print(response.answer)
        """
        # Initialize state
        initial_state = NavigatorState(query=query)

        # Run the workflow
        final_state = await self._run_workflow_async(initial_state)

        # Return the best response (or error)
        if final_state.error:
            return AgentResponse(
                agent_name="CS Navigator",
                answer=f"Error: {final_state.error}",
                confidence=0.0,
            )

        if final_state.best_response:
            return final_state.best_response

        return AgentResponse(
            agent_name="CS Navigator",
            answer="I couldn't find an answer to your question. Please try rephrasing.",
            confidence=0.0,
        )

    async def _run_workflow_async(self, state: NavigatorState) -> NavigatorState:
        """Run the workflow asynchronously."""
        # Classify
        state = self._classify_query(state)

        # Route
        state = self._route_to_agents(state)

        # Execute (async)
        state = await self._execute_agents_async(state)

        # Select best
        state = self._select_best(state)

        return state

    def ask_sync(self, query: str) -> AgentResponse:
        """
        Synchronous version of ask() for non-async contexts.

        Args:
            query: The user's question

        Returns:
            AgentResponse with the best answer
        """
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(self.ask(query))
        finally:
            loop.close()

    def get_agent_info(self) -> List[Dict[str, str]]:
        """
        Get information about all available agents.

        Returns:
            List of dicts with agent name and description
        """
        return [
            {"name": agent.name, "description": agent.description}
            for agent in self.agents.values()
        ]
