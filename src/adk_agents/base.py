"""
ADK Base Agent
==============

Base class for Google ADK agents. Provides common functionality for all agents.

IMPORTANT: After deploying agents to Vertex AI Agent Engine, copy the "Get Code"
output from Agent Designer and paste it into the respective agent files. The
code below is a template that will be replaced with the actual ADK code.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Optional
import asyncio

from .config import get_adk_config, AGENT_INFO


@dataclass
class ADKResponse:
    """Response from an ADK agent."""
    agent_name: str
    answer: str
    confidence: float = 1.0
    metadata: dict = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class BaseADKAgent(ABC):
    """
    Base class for ADK agents.

    This provides a unified interface for both:
    1. Local execution using the ADK framework
    2. Remote execution via deployed Vertex AI Agent Engine

    Subclasses should implement the _create_agent() method with the actual
    ADK code copied from "Get Code" in Agent Designer.
    """

    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.config = get_adk_config()
        self.info = AGENT_INFO.get(agent_name, {})
        self._agent = None

    @property
    def display_name(self) -> str:
        """Get the display name for this agent."""
        return self.info.get("name", self.agent_name)

    @property
    def description(self) -> str:
        """Get the description for this agent."""
        return self.info.get("description", "")

    @property
    def is_orchestrator(self) -> bool:
        """Check if this agent is an orchestrator."""
        return self.info.get("is_orchestrator", False)

    @property
    def resource_id(self) -> Optional[str]:
        """Get the Vertex AI resource ID for this agent."""
        return self.config.get_resource_id(self.agent_name)

    @abstractmethod
    def _create_agent(self):
        """
        Create the ADK agent instance.

        This method should be implemented by subclasses with the actual ADK code
        copied from "Get Code" in Agent Designer.

        Returns:
            The ADK agent instance
        """
        pass

    def get_agent(self):
        """Get or create the ADK agent instance."""
        if self._agent is None:
            self._agent = self._create_agent()
        return self._agent

    async def run(self, query: str, **kwargs) -> ADKResponse:
        """
        Run the agent with a query.

        Args:
            query: The user's question
            **kwargs: Additional parameters for the agent

        Returns:
            ADKResponse with the agent's answer
        """
        agent = self.get_agent()

        if agent is None:
            # Agent not yet implemented - return placeholder
            return ADKResponse(
                agent_name=self.display_name,
                answer=f"[{self.display_name}] Agent not yet deployed. "
                       f"Please copy the 'Get Code' output from Agent Designer into "
                       f"src/adk_agents/{self.agent_name}.py",
                confidence=0.0,
                metadata={"status": "not_deployed"}
            )

        try:
            # Run the ADK agent
            # The actual implementation depends on the ADK code structure
            result = await self._execute_agent(agent, query, **kwargs)
            return ADKResponse(
                agent_name=self.display_name,
                answer=result,
                confidence=1.0,
                metadata={"status": "success"}
            )
        except Exception as e:
            return ADKResponse(
                agent_name=self.display_name,
                answer=f"Error running agent: {str(e)}",
                confidence=0.0,
                metadata={"status": "error", "error": str(e)}
            )

    async def _execute_agent(self, agent: Any, query: str, **kwargs) -> str:
        """
        Execute the ADK agent.

        This is the default implementation. Subclasses can override this
        if they need custom execution logic.

        Args:
            agent: The ADK agent instance
            query: The user's question
            **kwargs: Additional parameters

        Returns:
            The agent's response as a string
        """
        # Default ADK execution pattern
        # This will be customized based on the actual ADK code structure
        if hasattr(agent, 'run'):
            result = await agent.run(query)
        elif hasattr(agent, 'invoke'):
            result = agent.invoke(query)
        elif hasattr(agent, 'query'):
            result = await agent.query(query)
        else:
            # Try calling it directly
            result = agent(query)

        # Extract the response text
        if isinstance(result, str):
            return result
        elif hasattr(result, 'text'):
            return result.text
        elif hasattr(result, 'content'):
            return result.content
        elif isinstance(result, dict):
            return result.get('answer', result.get('response', str(result)))
        else:
            return str(result)

    def run_sync(self, query: str, **kwargs) -> ADKResponse:
        """
        Synchronous version of run().

        Args:
            query: The user's question
            **kwargs: Additional parameters

        Returns:
            ADKResponse with the agent's answer
        """
        return asyncio.run(self.run(query, **kwargs))


class RemoteADKAgent(BaseADKAgent):
    """
    Agent that calls a deployed Vertex AI Agent Engine.

    Use this when you want to call an already-deployed agent instead of
    running locally.
    """

    def _create_agent(self):
        """Create a client for the deployed agent."""
        resource_id = self.resource_id
        if not resource_id:
            return None

        # Import Vertex AI client
        try:
            from google.cloud import aiplatform
            from google.cloud.aiplatform import reasoning_engines

            # Initialize the client
            aiplatform.init(
                project=self.config.project_id,
                location=self.config.location,
            )

            # Get the deployed reasoning engine
            engine = reasoning_engines.ReasoningEngine(resource_id)
            return engine

        except ImportError:
            print("Warning: google-cloud-aiplatform not installed")
            return None
        except Exception as e:
            print(f"Warning: Could not connect to deployed agent: {e}")
            return None

    async def _execute_agent(self, agent: Any, query: str, **kwargs) -> str:
        """Execute the deployed agent."""
        # Vertex AI reasoning engine query
        response = agent.query(input=query)

        if isinstance(response, str):
            return response
        elif hasattr(response, 'output'):
            return response.output
        else:
            return str(response)
