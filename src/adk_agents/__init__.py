"""
ADK Agents
==========

Google Agent Development Kit (ADK) implementations of the CS Navigator agents.

These agents are designed to be deployed to Vertex AI Agent Engine and can also
run locally using the ADK framework.

USAGE:
------
After deploying agents to Vertex AI, get the resource IDs and update config.py.
Then copy the "Get Code" output from Agent Designer into each agent file.

To use locally:
    from src.adk_agents import CSNavigatorADK, create_navigator

    # Option 1: Use the orchestrator directly
    navigator = CSNavigatorADK()
    response = await navigator.run("What courses should I take?")

    # Option 2: Use the orchestrator with all sub-agents registered
    navigator = create_navigator(register_all_agents=True)
    response = await navigator.run("What courses should I take?")
"""

from .config import ADKConfig, get_adk_config, AGENT_INFO
from .base import BaseADKAgent, RemoteADKAgent, ADKResponse
from .cs_navigator import CSNavigatorADK, create_navigator
from .academic_advisor import AcademicAdvisorADK
from .career_guidance import CareerGuidanceADK
from .course_recommender import CourseRecommenderADK
from .degreeworks import DegreeWorksADK
from .general_qa import GeneralQAADK
from .schedule_builder import ScheduleBuilderADK
from .financial_aid import FinancialAidADK

__all__ = [
    # Configuration
    "ADKConfig",
    "get_adk_config",
    "AGENT_INFO",

    # Base classes
    "BaseADKAgent",
    "RemoteADKAgent",
    "ADKResponse",

    # Orchestrator
    "CSNavigatorADK",
    "create_navigator",

    # Sub-agents
    "AcademicAdvisorADK",
    "CareerGuidanceADK",
    "CourseRecommenderADK",
    "DegreeWorksADK",
    "GeneralQAADK",
    "ScheduleBuilderADK",
    "FinancialAidADK",
]
