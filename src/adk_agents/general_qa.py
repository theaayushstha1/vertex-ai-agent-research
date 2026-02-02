"""
General Q&A Agent (ADK Version)
===============================

Handles general questions about the CS department, campus resources, and policies.

INSTRUCTIONS:
-------------
1. Deploy the General Q&A agent in Vertex AI Agent Designer
2. Click "Get Code" in Agent Designer
3. Copy the generated code and replace the _create_agent() method below
4. Update the resource ID in config.py
"""

from .base import BaseADKAgent


class GeneralQAADK(BaseADKAgent):
    """
    General Q&A agent using Google ADK.

    Specializes in:
    - Campus resources and facilities
    - Department policies and procedures
    - Important dates and deadlines
    - Contact information
    """

    def __init__(self):
        super().__init__("general_qa")

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
            name="general_qa",
            model="gemini-2.5-flash",
            instruction=\"\"\"You are the General Q&A Assistant for Morgan State
            University Computer Science department. You help students with:
            - Finding campus resources and facilities
            - Understanding department policies
            - Important dates and deadlines
            - Contact information for faculty and staff

            Be friendly and helpful with all questions.\"\"\"
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
