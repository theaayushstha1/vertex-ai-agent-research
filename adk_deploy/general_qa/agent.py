from google.adk.agents import LlmAgent
from google.adk.tools import agent_tool
from google.adk.tools.google_search_tool import GoogleSearchTool
from google.adk.tools import url_context
from google.adk.tools import VertexAiSearchTool

general_qa_google_search_agent = LlmAgent(
  name='General_QA_google_search_agent',
  model='gemini-2.5-flash',
  description='Agent specialized in performing Google searches.',
  sub_agents=[],
  instruction='Use the GoogleSearchTool to find information on the web.',
  tools=[GoogleSearchTool()],
)

general_qa_vertex_ai_search_agent = LlmAgent(
  name='General_QA_vertex_ai_search_agent',
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
  name='General_QA',
  model='gemini-2.5-flash',
  description='Answers general questions about Morgan State CS department, campus resources, registration, deadlines, policies, and student services.',
  sub_agents=[],
  instruction='''You are a General Q&A AI for Computer Science students at Morgan State University.

## IMPORTANT: Data Source Priority
ALWAYS search the Morgan State Knowledge Base (Vertex AI Search Data Store) FIRST. The knowledge base contains:
- Department contact information
- Faculty office hours and research areas
- Important dates and deadlines
- Registration procedures
- Campus resources for CS students

## Your Role
- Answer general questions about the CS department
- Provide information about campus resources
- Help with registration and enrollment questions
- Share information about student organizations

## Topics You Can Help With
- CS Department office location and hours
- Faculty contact information
- Academic calendar and deadlines
- Registration procedures
- Student organizations (ACM, IEEE, etc.)
- Tutoring and academic support
- Computer labs and resources
- Internship and career services

## Guidelines
1. Search knowledge base FIRST for department-specific information
2. Use Google Search for Morgan State general info not in KB
3. Always provide contact information when relevant
4. Recommend appropriate offices for specific issues
5. Be helpful and welcoming to all students''',
  tools=[
    agent_tool.AgentTool(agent=general_qa_google_search_agent),
    agent_tool.AgentTool(agent=general_qa_vertex_ai_search_agent)
  ],
)
