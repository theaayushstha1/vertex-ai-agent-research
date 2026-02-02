"""
ADK Configuration
=================

Configuration for Google Agent Development Kit agents.

After deploying agents to Vertex AI Agent Engine, update the AGENT_RESOURCE_IDS
dictionary with the actual resource IDs from the deployment.

Resource ID format:
    projects/{PROJECT_NUMBER}/locations/{REGION}/reasoningEngines/{RESOURCE_ID}
"""

import os
from dataclasses import dataclass, field
from typing import Optional
from functools import lru_cache
from pathlib import Path

# Load environment variables from .env file
from dotenv import load_dotenv
_env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(_env_path)


@dataclass
class ADKConfig:
    """Configuration for ADK agents."""

    # Google Cloud settings
    project_id: str = field(default_factory=lambda: os.getenv("GOOGLE_CLOUD_PROJECT", ""))
    project_number: str = field(default_factory=lambda: os.getenv("GOOGLE_CLOUD_PROJECT_NUMBER", "750361124802"))
    location: str = field(default_factory=lambda: os.getenv("VERTEX_AI_LOCATION", "us-central1"))

    # Model settings
    model_name: str = "gemini-2.5-flash"

    # Knowledge base
    knowledge_base_id: str = "csnavigator-kb-uscentral_1768951850167"

    # Agent resource IDs (update after deployment)
    # Format: projects/{PROJECT_NUMBER}/locations/{REGION}/reasoningEngines/{RESOURCE_ID}
    agent_resource_ids: dict = field(default_factory=lambda: {
        # Main orchestrator - DEPLOYED!
        "cs_navigator": "projects/750361124802/locations/us-central1/reasoningEngines/7546347424147570688",

        # Sub-agents - TODO: Deploy these
        "academic_advisor": "",  # TODO: Add after deployment
        "career_guidance": "",  # TODO: Add after deployment
        "course_recommender": "",  # TODO: Add after deployment
        "degreeworks": "",  # TODO: Add after deployment
        "general_qa": "",  # TODO: Add after deployment
        "schedule_builder": "",  # TODO: Add after deployment
        "financial_aid": "",  # TODO: Add after deployment
    })

    def get_resource_id(self, agent_name: str) -> Optional[str]:
        """Get the full resource ID for an agent."""
        resource_id = self.agent_resource_ids.get(agent_name)
        if not resource_id:
            return None
        # If it's already a full path, return as-is
        if resource_id.startswith("projects/"):
            return resource_id
        # Otherwise, construct the full path
        return f"projects/{self.project_number}/locations/{self.location}/reasoningEngines/{resource_id}"

    def validate(self) -> list[str]:
        """Validate configuration and return list of issues."""
        issues = []
        if not self.project_id:
            issues.append("GOOGLE_CLOUD_PROJECT not set")
        if not self.project_number:
            issues.append("GOOGLE_CLOUD_PROJECT_NUMBER not set")
        return issues


@lru_cache()
def get_adk_config() -> ADKConfig:
    """Get the ADK configuration (cached)."""
    return ADKConfig()


# Agent names and descriptions for reference
AGENT_INFO = {
    "cs_navigator": {
        "name": "CS Navigator",
        "description": "Main orchestrator that routes questions to specialized sub-agents",
        "is_orchestrator": True,
    },
    "academic_advisor": {
        "name": "Academic Advisor",
        "description": "Course selection, faculty information, degree requirements",
        "is_orchestrator": False,
    },
    "career_guidance": {
        "name": "Career Guidance",
        "description": "Jobs, internships, resume tips, career paths in CS",
        "is_orchestrator": False,
    },
    "course_recommender": {
        "name": "Course Recommender",
        "description": "Course suggestions based on interests and goals",
        "is_orchestrator": False,
    },
    "degreeworks": {
        "name": "DegreeWorks",
        "description": "Degree progress tracking and graduation planning",
        "is_orchestrator": False,
    },
    "general_qa": {
        "name": "General Q&A",
        "description": "Campus resources, policies, deadlines, general questions",
        "is_orchestrator": False,
    },
    "schedule_builder": {
        "name": "Schedule Builder",
        "description": "Conflict-free class scheduling and calendar optimization",
        "is_orchestrator": False,
    },
    "financial_aid": {
        "name": "Financial Aid",
        "description": "Scholarships, FAFSA, tuition assistance, payment plans",
        "is_orchestrator": False,
    },
}
