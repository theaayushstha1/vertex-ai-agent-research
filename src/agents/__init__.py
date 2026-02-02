"""
Agents Module
=============

Individual AI agents, each specialized for a specific domain:

- AcademicAdvisor: Course selection, degree requirements, faculty info
- CareerGuidance: Jobs, internships, resume tips, industry trends
- CourseRecommender: Suggests courses based on interests and completed prereqs
- ScheduleBuilder: Helps create conflict-free class schedules
- DegreeWorks: Tracks degree progress and remaining requirements
- GeneralQA: Answers general questions about the CS department
- FinancialAid: FAFSA, scholarships, tuition, work-study info

All agents inherit from BaseAgent which provides common functionality.
"""

from .base import BaseAgent, AgentResponse
from .academic_advisor import AcademicAdvisor
from .career_guidance import CareerGuidance
from .course_recommender import CourseRecommender
from .schedule_builder import ScheduleBuilder
from .degreeworks import DegreeWorks
from .general_qa import GeneralQA
from .financial_aid import FinancialAid

__all__ = [
    "BaseAgent",
    "AgentResponse",
    "AcademicAdvisor",
    "CareerGuidance",
    "CourseRecommender",
    "ScheduleBuilder",
    "DegreeWorks",
    "GeneralQA",
    "FinancialAid",
]
