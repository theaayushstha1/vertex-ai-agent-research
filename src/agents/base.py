"""
Base Agent Class
================

All specialized agents inherit from this class. It provides:
1. Common interface for asking questions
2. Vertex AI LLM integration
3. Response formatting with confidence scores
4. Optional MCP tool bindings

DESIGN DECISIONS:
-----------------

Why a base class instead of functions?
- Agents need state (conversation history, loaded knowledge)
- Easier to test and mock
- Clear interface for all agents

Why async?
- Enables parallel execution
- Non-blocking while waiting for LLM responses
- Scales better with multiple simultaneous requests

Why confidence scores?
- Helps consensus algorithm pick best response
- Agents can express uncertainty
- Users know when to trust vs verify
"""

import asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from langchain_google_vertexai import ChatVertexAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage


@dataclass
class AgentResponse:
    """
    Structured response from an agent.

    This dataclass ensures all agents return responses in the same format,
    making it easy for the consensus algorithm to compare them.

    Attributes:
        agent_name: Which agent produced this response (e.g., "Academic Advisor")
        answer: The actual response text
        confidence: 0.0-1.0 score of how confident the agent is
        sources: List of sources cited (if any)
        metadata: Additional info (timestamps, processing time, etc.)
        needs_action: Whether this response requires MCP action (email, calendar)
        action_type: Type of MCP action needed (e.g., "send_email", "create_event")
        action_params: Parameters for the MCP action
    """
    agent_name: str
    answer: str
    confidence: float = 0.8
    sources: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    # MCP action fields
    needs_action: bool = False
    action_type: Optional[str] = None
    action_params: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        """Add timestamp to metadata."""
        self.metadata["timestamp"] = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "agent_name": self.agent_name,
            "answer": self.answer,
            "confidence": self.confidence,
            "sources": self.sources,
            "metadata": self.metadata,
            "needs_action": self.needs_action,
            "action_type": self.action_type,
            "action_params": self.action_params,
        }


class BaseAgent(ABC):
    """
    Abstract base class for all agents.

    To create a new agent:
    1. Inherit from BaseAgent
    2. Set name and description in __init__
    3. Implement get_system_prompt()
    4. Optionally override process_response() for custom logic

    Example:
        class MyAgent(BaseAgent):
            def __init__(self, llm):
                super().__init__(
                    name="My Agent",
                    description="Does something specific",
                    llm=llm
                )

            def get_system_prompt(self) -> str:
                return "You are an expert in..."
    """

    def __init__(
        self,
        name: str,
        description: str,
        llm: ChatVertexAI,
        knowledge_base: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize the agent.

        Args:
            name: Display name of the agent (e.g., "Academic Advisor")
            description: Brief description of what this agent does
            llm: LangChain ChatVertexAI instance for LLM calls
            knowledge_base: Optional dict of domain knowledge
        """
        self.name = name
        self.description = description
        self.llm = llm
        self.knowledge_base = knowledge_base or {}
        self.conversation_history: List[Dict[str, str]] = []

    @abstractmethod
    def get_system_prompt(self) -> str:
        """
        Return the system prompt for this agent.

        This defines the agent's personality, expertise, and behavior.
        Must be implemented by each specific agent.

        Returns:
            System prompt string
        """
        pass

    def get_relevant_knowledge(self, query: str) -> str:
        """
        Extract relevant knowledge for the given query.

        Override this in subclasses for smarter knowledge retrieval.
        Default implementation returns all knowledge as a string.

        Args:
            query: The user's question

        Returns:
            String of relevant knowledge to include in context
        """
        if not self.knowledge_base:
            return ""

        # Simple implementation: just stringify the knowledge base
        # Subclasses can implement smarter retrieval (embeddings, etc.)
        return f"\n\nRelevant Knowledge:\n{self.knowledge_base}"

    async def ask(self, query: str) -> AgentResponse:
        """
        Ask this agent a question and get a response.

        This is the main method to interact with an agent.
        It handles:
        1. Building the prompt with system message and knowledge
        2. Calling the LLM
        3. Processing the response
        4. Calculating confidence

        Args:
            query: The user's question

        Returns:
            AgentResponse with the answer and metadata
        """
        # Build messages
        system_prompt = self.get_system_prompt()
        knowledge = self.get_relevant_knowledge(query)

        # Include knowledge in system prompt if available
        full_system_prompt = system_prompt
        if knowledge:
            full_system_prompt += f"\n\n{knowledge}"

        messages = [
            SystemMessage(content=full_system_prompt),
            HumanMessage(content=query),
        ]

        # Add conversation history for context
        for msg in self.conversation_history[-5:]:  # Last 5 messages
            if msg["role"] == "user":
                messages.insert(-1, HumanMessage(content=msg["content"]))
            else:
                messages.insert(-1, AIMessage(content=msg["content"]))

        try:
            # Call the LLM
            response = await self.llm.ainvoke(messages)
            answer = response.content

            # Process the response (subclasses can customize)
            processed = self.process_response(query, answer)

            # Calculate confidence
            confidence = self.calculate_confidence(query, answer)

            # Store in history
            self.conversation_history.append({"role": "user", "content": query})
            self.conversation_history.append({"role": "assistant", "content": answer})

            return AgentResponse(
                agent_name=self.name,
                answer=processed["answer"],
                confidence=confidence,
                sources=processed.get("sources", []),
                metadata={
                    "query": query,
                    "raw_response": answer,
                },
                needs_action=processed.get("needs_action", False),
                action_type=processed.get("action_type"),
                action_params=processed.get("action_params"),
            )

        except Exception as e:
            # Return error response
            return AgentResponse(
                agent_name=self.name,
                answer=f"I encountered an error: {str(e)}",
                confidence=0.0,
                metadata={"error": str(e)},
            )

    def process_response(self, query: str, raw_response: str) -> Dict[str, Any]:
        """
        Process the raw LLM response.

        Override this in subclasses to:
        - Extract structured data
        - Parse citations
        - Detect action requests (emails, events)

        Args:
            query: Original query
            raw_response: Raw text from LLM

        Returns:
            Dict with at least "answer" key, optionally "sources", "needs_action", etc.
        """
        # Default implementation: return as-is
        return {"answer": raw_response}

    def calculate_confidence(self, query: str, response: str) -> float:
        """
        Calculate confidence score for a response.

        Factors that increase confidence:
        - Longer, more detailed responses
        - Presence of specific data/numbers
        - Relevance to the query
        - No hedging language

        Factors that decrease confidence:
        - Short responses
        - "I'm not sure" type language
        - Generic answers

        Args:
            query: Original query
            response: The response text

        Returns:
            Float between 0.0 and 1.0
        """
        confidence = 0.7  # Base confidence

        # Longer responses are usually more complete
        if len(response) > 200:
            confidence += 0.1
        if len(response) > 500:
            confidence += 0.1

        # Check for hedging language (decreases confidence)
        hedging_phrases = [
            "i'm not sure",
            "i don't know",
            "maybe",
            "possibly",
            "i think",
            "it might be",
            "i'm uncertain",
        ]
        response_lower = response.lower()
        for phrase in hedging_phrases:
            if phrase in response_lower:
                confidence -= 0.15
                break

        # Check for specific data (increases confidence)
        specificity_indicators = [
            any(char.isdigit() for char in response),  # Contains numbers
            "http" in response_lower,  # Contains links
            "%" in response,  # Contains percentages
        ]
        for indicator in specificity_indicators:
            if indicator:
                confidence += 0.05

        # Clamp between 0.0 and 1.0
        return max(0.0, min(1.0, confidence))

    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history = []

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}')"
