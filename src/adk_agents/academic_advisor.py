"""
Academic Advisor Agent (ADK Version)
====================================

Helps students with course selection, faculty information, and degree requirements.

INSTRUCTIONS:
-------------
1. Deploy the Academic Advisor agent in Vertex AI Agent Designer
2. Click "Get Code" in Agent Designer
3. Copy the generated code and replace the _create_agent() method below
4. Update the resource ID in config.py
"""

from .base import BaseADKAgent


class AcademicAdvisorADK(BaseADKAgent):
    """
    Academic Advisor agent using Google ADK.

    Specializes in:
    - Course selection and prerequisites
    - Faculty information and office hours
    - Degree requirements and academic policies
    - Major/minor declarations
    """

    def __init__(self):
        super().__init__("academic_advisor")

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
            name="academic_advisor",
            model="gemini-2.5-flash",
            instruction=\"\"\"You are the Academic Advisor for Morgan State University
            Computer Science department. You help students with:
            - Course selection and prerequisites
            - Faculty information and office hours
            - Degree requirements and academic policies
            - Major/minor declarations

            Be helpful, accurate, and encouraging to students.\"\"\"
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
