"""
Schedule Builder Agent (ADK Version)
====================================

Helps students build conflict-free class schedules.

INSTRUCTIONS:
-------------
1. Deploy the Schedule Builder agent in Vertex AI Agent Designer
2. Click "Get Code" in Agent Designer
3. Copy the generated code and replace the _create_agent() method below
4. Update the resource ID in config.py
"""

from .base import BaseADKAgent


class ScheduleBuilderADK(BaseADKAgent):
    """
    Schedule Builder agent using Google ADK.

    Specializes in:
    - Building conflict-free schedules
    - Checking course availability
    - Optimizing class times
    - Managing waitlists
    """

    def __init__(self):
        super().__init__("schedule_builder")

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
            name="schedule_builder",
            model="gemini-2.5-flash",
            instruction=\"\"\"You are the Schedule Builder for Morgan State University
            Computer Science department. You help students with:
            - Building conflict-free class schedules
            - Checking course availability and sections
            - Optimizing class times for their preferences
            - Understanding registration procedures

            Consider time conflicts and prerequisites carefully.\"\"\"
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
