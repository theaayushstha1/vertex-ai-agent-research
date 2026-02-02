"""
Financial Aid Agent (ADK Version)
=================================

Helps students with scholarships, FAFSA, and financial planning.

INSTRUCTIONS:
-------------
1. Deploy the Financial Aid agent in Vertex AI Agent Designer
2. Click "Get Code" in Agent Designer
3. Copy the generated code and replace the _create_agent() method below
4. Update the resource ID in config.py
"""

from .base import BaseADKAgent


class FinancialAidADK(BaseADKAgent):
    """
    Financial Aid agent using Google ADK.

    Specializes in:
    - Scholarship opportunities
    - FAFSA assistance
    - Tuition and fee information
    - Payment plans and options
    """

    def __init__(self):
        super().__init__("financial_aid")

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
            name="financial_aid",
            model="gemini-2.5-flash",
            instruction=\"\"\"You are the Financial Aid Advisor for Morgan State
            University Computer Science department. You help students with:
            - Finding scholarship opportunities
            - Completing FAFSA applications
            - Understanding tuition and fees
            - Exploring payment plans and options

            Be sensitive and helpful with financial matters.\"\"\"
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
