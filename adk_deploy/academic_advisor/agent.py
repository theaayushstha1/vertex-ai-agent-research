# -*- coding: utf-8 -*-
"""
Academic Advisor Agent - For ADK Deployment
"""

from google.adk.agents import LlmAgent
from google.adk.tools import agent_tool
from google.adk.tools import VertexAiSearchTool

academic_advisor_vertex_ai_search_agent = LlmAgent(
    name='Academic_Advisor_vertex_ai_search_agent',
    model='gemini-2.5-flash',
    description='Agent specialized in performing Vertex AI Search.',
    sub_agents=[],
    instruction='Use the VertexAISearchTool to find information using Vertex AI Search.',
    tools=[
        VertexAiSearchTool(
            data_store_id='projects/csnavigator-vertex-ai/locations/us/collections/default_collection/dataStores/csnavigator-kb-uscentral_1768951850167'
        )
    ],
)

root_agent = LlmAgent(
    name='Academic_Advisor',
    model='gemini-2.5-flash',
    description='AI advisor for Morgan State University Computer Science students. Helps with course selection, degree requirements, faculty information, and academic planning.',
    sub_agents=[],
    instruction='You are an Academic Advisor AI for the Computer Science Department at Morgan State University. Help CS students with academic planning and course selection. Answer questions about degree requirements, prerequisites, and course sequences. Provide information about faculty members and their research areas. Guide students on academic policies and procedures.',
    tools=[
        agent_tool.AgentTool(agent=academic_advisor_vertex_ai_search_agent)
    ],
)
