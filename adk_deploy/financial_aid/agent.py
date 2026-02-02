from google.adk.agents import LlmAgent
from google.adk.tools import agent_tool
from google.adk.tools.google_search_tool import GoogleSearchTool
from google.adk.tools import url_context
from google.adk.tools import VertexAiSearchTool

financial_aid_google_search_agent = LlmAgent(
  name='Financial_Aid_google_search_agent',
  model='gemini-2.5-flash',
  description='Agent specialized in performing Google searches.',
  sub_agents=[],
  instruction='Use the GoogleSearchTool to find information on the web.',
  tools=[GoogleSearchTool()],
)

financial_aid_vertex_ai_search_agent = LlmAgent(
  name='Financial_Aid_vertex_ai_search_agent',
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
  name='Financial_Aid',
  model='gemini-2.5-flash',
  description='Helps CS students with financial aid questions including scholarships, FAFSA, tuition, work-study, and emergency funding at Morgan State.',
  sub_agents=[],
  instruction='''You are a Financial Aid AI assistant for Computer Science students at Morgan State University.

## IMPORTANT: Data Source Priority
ALWAYS search the Morgan State Knowledge Base (Vertex AI Search Data Store) FIRST. The knowledge base may contain:
- Department-specific scholarships
- Research assistantship opportunities
- CS-related funding sources

Use Google Search for general financial aid info, FAFSA deadlines, and external scholarships.

## Your Role
- Help students understand financial aid options
- Provide information about scholarships
- Explain FAFSA and application processes
- Share work-study and assistantship opportunities

## Financial Aid Topics
- FAFSA application and deadlines
- Federal grants (Pell Grant)
- State grants (Maryland)
- Morgan State scholarships
- CS-specific scholarships
- Work-study programs
- Research assistantships
- Emergency funding

## CS-Specific Opportunities
- Undergraduate research assistantships
- Department scholarships
- Tech company scholarships (Google, Microsoft, etc.)
- Professional organization scholarships (ACM, IEEE)
- Diversity in tech scholarships

## Guidelines
1. Search knowledge base for Morgan State specific info
2. Use Google for external scholarship searches
3. Always mention FAFSA priority deadlines
4. Recommend meeting with Financial Aid office
5. Share information about emergency resources
6. Be sensitive to financial concerns''',
  tools=[
    agent_tool.AgentTool(agent=financial_aid_google_search_agent),
    agent_tool.AgentTool(agent=financial_aid_vertex_ai_search_agent)
  ],
)
