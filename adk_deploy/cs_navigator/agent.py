# -*- coding: utf-8 -*-
"""
CS Navigator Agent - For ADK Deployment
"""

from google.adk.agents import LlmAgent
from google.adk.tools import agent_tool
from google.adk.tools.google_search_tool import GoogleSearchTool
from google.adk.tools import url_context
from google.adk.tools import VertexAiSearchTool

# Sub-agent for Google Search
cs_navigator_google_search_agent = LlmAgent(
    name='CS_Navigator_google_search_agent',
    model='gemini-2.5-flash',
    description='Agent specialized in performing Google searches.',
    sub_agents=[],
    instruction='Use the GoogleSearchTool to find information on the web.',
    tools=[
        GoogleSearchTool()
    ],
)

# Sub-agent for URL Context
cs_navigator_url_context_agent = LlmAgent(
    name='CS_Navigator_url_context_agent',
    model='gemini-2.5-flash',
    description='Agent specialized in fetching content from URLs.',
    sub_agents=[],
    instruction='Use the UrlContextTool to retrieve content from provided URLs.',
    tools=[
        url_context
    ],
)

# Sub-agent for Vertex AI Search (Knowledge Base)
cs_navigator_vertex_ai_search_agent = LlmAgent(
    name='CS_Navigator_vertex_ai_search_agent',
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

# Main orchestrator agent
root_agent = LlmAgent(
    name='CS_Navigator',
    model='gemini-2.5-flash',
    description='Main orchestrator for Morgan State CS students.',
    sub_agents=[],
    instruction='You are CS Navigator, the main AI assistant for Computer Science students at Morgan State University. Help students with course selection, career guidance, degree progress, and general questions. Use the available tools to find information.',
    tools=[
        agent_tool.AgentTool(agent=cs_navigator_google_search_agent),
        agent_tool.AgentTool(agent=cs_navigator_url_context_agent),
        agent_tool.AgentTool(agent=cs_navigator_vertex_ai_search_agent),
    ],
)
