"""
Course Recommender Agent (ADK Version)
======================================

Recommends courses based on student interests, goals, and academic history.

INSTRUCTIONS:
-------------
1. Deploy the Course Recommender agent in Vertex AI Agent Designer
2. Click "Get Code" in Agent Designer
3. Copy the generated code and replace the _create_agent() method below
4. Update the resource ID in config.py
"""

from .base import BaseADKAgent


class CourseRecommenderADK(BaseADKAgent):
    """
    Course Recommender agent using Google ADK.

    Specializes in:
    - Course suggestions based on interests
    - Elective recommendations
    - Course sequences and pathways
    - Skill development planning
    """

    def __init__(self):
        super().__init__("course_recommender")

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
            name="course_recommender",
            model="gemini-2.5-flash",
            instruction=\"\"\"You are the Course Recommender for Morgan State University
            Computer Science department. You help students choose courses by:
            - Understanding their interests and career goals
            - Recommending relevant electives
            - Suggesting course sequences
            - Identifying skill development opportunities

            Ask clarifying questions about interests if needed.\"\"\"
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
