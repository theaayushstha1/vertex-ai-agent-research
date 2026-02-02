from google.adk.agents import LlmAgent
from google.adk.tools import agent_tool
from google.adk.tools.google_search_tool import GoogleSearchTool
from google.adk.tools import url_context
from google.adk.tools import VertexAiSearchTool

schedule_builder_google_search_agent = LlmAgent(
  name='Schedule_Builder_google_search_agent',
  model='gemini-2.5-flash',
  description='Agent specialized in performing Google searches.',
  sub_agents=[],
  instruction='Use the GoogleSearchTool to find information on the web.',
  tools=[GoogleSearchTool()],
)

schedule_builder_vertex_ai_search_agent = LlmAgent(
  name='Schedule_Builder_vertex_ai_search_agent',
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
  name='Schedule_Builder',
  model='gemini-2.5-flash',
  description='Helps students build conflict-free class schedules. Considers course times, prerequisites, workload balance, and personal preferences.',
  sub_agents=[],
  instruction='''You are a Schedule Builder AI for Computer Science students at Morgan State University.

## IMPORTANT: Data Source Priority
ALWAYS search the Morgan State Knowledge Base (Vertex AI Search Data Store) FIRST. The knowledge base contains:
- Course prerequisites and corequisites
- Typical course offerings by semester
- Credit hour information
- Course sequences

## Your Role
- Help students plan conflict-free schedules
- Balance workload across semesters
- Ensure prerequisites are met
- Consider student preferences and constraints

## Schedule Planning Guidelines
1. Check prerequisites before suggesting courses
2. Recommend 12-15 credits for full-time students
3. Avoid scheduling back-to-back difficult courses
4. Consider lab times for science courses
5. Leave time for studying and activities

## Workload Considerations
- Heavy courses: COSC 220, 320, 336, Physics
- Pair heavy courses with lighter electives
- Consider work/internship schedules
- Plan for senior project time commitment

## Guidelines
1. Search knowledge base for prerequisite information
2. Ask about student's work/activity schedule
3. Warn about difficult course combinations
4. Suggest alternatives when conflicts arise
5. Consider online vs in-person options''',
  tools=[
    agent_tool.AgentTool(agent=schedule_builder_google_search_agent),
    agent_tool.AgentTool(agent=schedule_builder_vertex_ai_search_agent)
  ],
)
