"""
Career Guidance Agent (ADK Version)
===================================

Helps students with career planning, job searches, and professional development.

INSTRUCTIONS:
-------------
1. Deploy the Career Guidance agent in Vertex AI Agent Designer
2. Click "Get Code" in Agent Designer
3. Copy the generated code and replace the _create_agent() method below
4. Update the resource ID in config.py
"""

from .base import BaseADKAgent


class CareerGuidanceADK(BaseADKAgent):
    """
    Career Guidance agent using Google ADK.

    Specializes in:
    - Job search strategies
    - Internship opportunities
    - Resume and cover letter tips
    - Interview preparation
    - Career paths in CS
    """

    def __init__(self):
        super().__init__("career_guidance")

    def _create_agent(self):
        """
        Create the ADK agent instance.

        ============================================================
        PASTE YOUR "GET CODE" OUTPUT FROM AGENT DESIGNER BELOW
        ============================================================

        Example structure (replace with actual code):

        from google.adk import Agent
        from google.adk.tools import VertexAISearch

        agent = Agent(
            name="career_guidance",
            model="gemini-2.5-flash",
            instruction=\"\"\"You are the Career Guidance Counselor for Morgan State
            University Computer Science department. You help students with:
            - Job search strategies and industry insights
            - Internship opportunities
            - Resume and cover letter writing
            - Interview preparation
            - Career paths in computer science

            Be encouraging and provide actionable advice.\"\"\"
            tools=[
                VertexAISearch(
                    data_store_id="csnavigator-kb-uscentral_1768951850167"
                )
            ]
        )
        return agent

        ============================================================
        """
        # TODO: Replace with actual ADK code from "Get Code"
        return None
