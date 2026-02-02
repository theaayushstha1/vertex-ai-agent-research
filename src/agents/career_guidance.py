"""
Career Guidance Agent
=====================

Career advisor for CS students at Morgan State.
Helps explore career paths, internships, job opportunities, and resume tips.

RESPONSIBILITIES:
- Career path exploration
- Internship and job search guidance
- Resume and cover letter tips
- Interview preparation
- Industry trends in technology

This agent mirrors your Vertex AI "Career Guidance" agent.
"""

from typing import Any, Dict, Optional

from langchain_google_vertexai import ChatVertexAI

from .base import BaseAgent


class CareerGuidance(BaseAgent):
    """
    Career Guidance agent for CS students.

    Helps students navigate their career journey from internships
    to full-time employment.
    """

    def __init__(
        self,
        llm: ChatVertexAI,
        knowledge_base: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            name="Career Guidance",
            description="Career advisor for CS students at Morgan State. Helps explore "
                       "career paths, internships, job opportunities, resume tips, "
                       "and industry trends in technology.",
            llm=llm,
            knowledge_base=knowledge_base,
        )

    def get_system_prompt(self) -> str:
        return """You are a Career Guidance Advisor for Computer Science students at Morgan State University.

## Your Role
You help CS students navigate their career journey, from first internship to full-time employment and beyond.

## Your Expertise
- Career paths in technology (Software Engineering, Data Science, Cybersecurity, etc.)
- Internship search strategies
- Job application best practices
- Resume and cover letter writing
- Technical interview preparation
- Salary negotiation basics
- Industry trends and in-demand skills

## Guidelines

### DO:
- Be encouraging and realistic about the job market
- Provide actionable advice they can implement today
- Share specific resources (job boards, tools, techniques)
- Acknowledge the challenges of job searching
- Celebrate their progress and efforts

### DON'T:
- Guarantee job placements or specific salaries
- Disparage any company or career path
- Make assumptions about their background or circumstances
- Provide outdated salary or job market data

## Key Resources to Mention
- Handshake (Morgan State's job portal)
- LinkedIn for networking
- LeetCode/HackerRank for technical practice
- Career Services office for resume reviews
- Alumni network for informational interviews

## Response Format
1. Address their specific question
2. Provide context on why this matters
3. Give 2-3 actionable next steps
4. Offer to help with related topics

Remember: Job searching is stressful. Be their supportive guide, not just an information source."""

    def process_response(self, query: str, raw_response: str) -> Dict[str, Any]:
        """
        Process response to detect career-related actions.

        Actions might include:
        - Sending resume templates via email
        - Scheduling mock interview practice
        - Setting job search reminders
        """
        result = {"answer": raw_response, "sources": []}

        query_lower = query.lower()
        response_lower = raw_response.lower()

        # Resume-related - might want to send template
        if "resume" in query_lower or "cv" in query_lower:
            if "template" in response_lower or "example" in response_lower:
                result["needs_action"] = True
                result["action_type"] = "offer_email"
                result["action_params"] = {
                    "subject": "Resume Resources from Career Guidance",
                    "context": "resume_help",
                }

        # Interview prep - might want to schedule practice
        if "interview" in query_lower:
            result["needs_action"] = True
            result["action_type"] = "suggest_calendar"
            result["action_params"] = {
                "event_type": "mock_interview",
                "context": "interview_prep",
            }

        return result
