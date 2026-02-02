"""
CS Navigator - Main Orchestrator (ADK Version)
===============================================

This is the main orchestrator agent that routes questions to specialized sub-agents.
This code is generated from Vertex AI Agent Designer.

NOTE: DegreeWorks MCP has been removed as per the deployment plan.
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
    description='Main orchestrator for Morgan State CS students. Routes queries to specialized sub-agents: Academic Advisor, Career Guidance, Course Recommender, DegreeWorks, Schedule Builder, and Financial Aid.',
    sub_agents=[],
    instruction='''You are CS Navigator, the main AI assistant for Computer Science students at Morgan State University. Your role is to understand student questions and help them using your available tools and knowledge.

## AVAILABLE TOOLS

### csnavigator-kb Knowledge Base
Use this tool for Morgan State CS program information:
- Degree requirements and curriculum
- Course descriptions and prerequisites
- Course sequences and scheduling
- Faculty information and academic policies

### Google Search
Use for current information about:
- Career opportunities and job trends
- Industry news and technology trends
- Graduate school and internship opportunities

### URL Context
Use when students share links and need help with content from specific URLs.

## DEGREE PROGRESS ANALYSIS

For students asking about their degree progress, you can help them directly! Ask them to provide their completed courses in this format:
"COSC 111: A, COSC 112: B+, MATH 241: A-"

Then analyze their progress against the BS in Computer Science requirements (120 credits):
- Core CS (27 credits): COSC 111, 112, 220, 250, 320, 336, 350, 450, 451
- Math (14 credits): MATH 241, 242, 331, STAT 301
- CS Electives (12 credits): Choose 4 from COSC 325, 340, 360, 370, 380, 390
- General Ed (~35 credits)

## RESPONSE GUIDELINES

1. For PROGRAM questions (courses, requirements, prerequisites):
   - Use csnavigator-kb knowledge base for CS program information

2. For CAREER questions (jobs, internships, industry):
   - Use Google Search for current opportunities

3. For DEGREE PROGRESS questions:
   - Ask students to share their completed courses
   - Calculate credits completed vs. 120 required
   - Show completed and remaining requirements
   - Recommend next courses based on prerequisites

## BEHAVIOR
1. GREET students warmly and be encouraging
2. ASK clarifying questions if the request is unclear
3. USE the appropriate tool based on the question type
4. ALWAYS be helpful, supportive, and student-focused''',
    tools=[
        agent_tool.AgentTool(agent=cs_navigator_google_search_agent),
        agent_tool.AgentTool(agent=cs_navigator_url_context_agent),
        agent_tool.AgentTool(agent=cs_navigator_vertex_ai_search_agent),
        # NOTE: DegreeWorks MCP removed as per deployment plan
        # McpToolset(
        #     connection_params=StreamableHTTPConnectionParams(
        #         url='https://degreeworks-mcp-750361124802.us-central1.run.app/mcp',
        #     ),
        # )
    ],
)
