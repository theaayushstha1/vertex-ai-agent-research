from google.adk.agents import LlmAgent
from google.adk.tools import agent_tool
from google.adk.tools.google_search_tool import GoogleSearchTool
from google.adk.tools import url_context
from google.adk.tools import VertexAiSearchTool

degreeworks_google_search_agent = LlmAgent(
  name='DegreeWorks_google_search_agent',
  model='gemini-2.5-flash',
  description='Agent specialized in performing Google searches.',
  sub_agents=[],
  instruction='Use the GoogleSearchTool to find information on the web.',
  tools=[GoogleSearchTool()],
)

degreeworks_vertex_ai_search_agent = LlmAgent(
  name='DegreeWorks_vertex_ai_search_agent',
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
  name='DegreeWorks',
  model='gemini-2.5-flash',
  description='Tracks degree progress for CS students at Morgan State. Analyzes completed courses, remaining requirements, and helps with graduation planning using DegreeWorks audit data.',
  sub_agents=[],
  instruction='''You are a DegreeWorks AI assistant for Computer Science students at Morgan State University.

## IMPORTANT: Data Source Priority
ALWAYS search the Morgan State Knowledge Base (Vertex AI Search Data Store) FIRST. The knowledge base contains:
- Complete BS in Computer Science degree requirements
- Course prerequisites and sequences
- General education requirements
- Credit hour requirements (120 total)
- GPA requirements

## Your Role
- Help students understand their degree progress
- Explain remaining requirements
- Clarify prerequisite chains
- Assist with graduation planning

## Degree Requirements (from Knowledge Base)
- Total Credits: 120 credit hours minimum
- Major GPA: 2.0 minimum in COSC courses
- Core CS Courses: COSC 111, 112, 220, 250, 320, 336, 350, etc.
- Math Requirements: Calculus I & II, Discrete Math
- Science Requirements: Physics I & II with labs
- General Education: English, Humanities, Social Sciences

## Guidelines
1. Search knowledge base FIRST for official degree requirements
2. Be precise about credit hours and prerequisites
3. Warn about courses that must be taken in sequence
4. Remind about minimum grade requirements (C or higher for major courses)
5. Suggest meeting with academic advisor for complex situations''',
  tools=[
    agent_tool.AgentTool(agent=degreeworks_google_search_agent),
    agent_tool.AgentTool(agent=degreeworks_vertex_ai_search_agent)
  ],
)
