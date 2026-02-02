"""
DegreeWorks Agent (ADK Version)
===============================

Helps students track degree progress and plan for graduation.

INSTRUCTIONS:
-------------
1. Deploy the DegreeWorks agent in Vertex AI Agent Designer
2. Click "Get Code" in Agent Designer
3. Copy the generated code and replace the _create_agent() method below
4. Update the resource ID in config.py

NOTE: The DegreeWorks MCP has been removed from this agent. If you need to
integrate with actual DegreeWorks data, you can add it back later.
"""

from .base import BaseADKAgent


class DegreeWorksADK(BaseADKAgent):
    """
    DegreeWorks agent using Google ADK.

    Specializes in:
    - Degree progress tracking
    - Graduation requirements
    - Credit hour calculations
    - Prerequisite checking
    """

    def __init__(self):
        super().__init__("degreeworks")

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
            name="degreeworks",
            model="gemini-2.5-flash",
            instruction=\"\"\"You are the DegreeWorks Assistant for Morgan State
            University Computer Science department. You help students with:
            - Understanding their degree progress
            - Checking graduation requirements
            - Calculating remaining credit hours
            - Verifying prerequisites

            Be precise with degree requirements and deadlines.\"\"\"
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
