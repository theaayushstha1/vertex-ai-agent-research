from google.adk.agents import LlmAgent
from google.adk.tools import agent_tool
from google.adk.tools.google_search_tool import GoogleSearchTool
from google.adk.tools import url_context
from google.adk.tools import VertexAiSearchTool

course_recommender_google_search_agent = LlmAgent(
  name='Course_Recommender_google_search_agent',
  model='gemini-2.5-flash',
  description='Agent specialized in performing Google searches.',
  sub_agents=[],
  instruction='Use the GoogleSearchTool to find information on the web.',
  tools=[GoogleSearchTool()],
)

course_recommender_url_context_agent = LlmAgent(
  name='Course_Recommender_url_context_agent',
  model='gemini-2.5-flash',
  description='Agent specialized in fetching content from URLs.',
  sub_agents=[],
  instruction='Use the UrlContextTool to retrieve content from provided URLs.',
  tools=[url_context],
)

course_recommender_vertex_ai_search_agent = LlmAgent(
  name='Course_Recommender_vertex_ai_search_agent',
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
  name='Course_Recommender',
  model='gemini-2.5-flash',
  description='Recommends CS courses based on student interests, career goals, and completed prerequisites. Helps plan semester schedules and course sequences.',
  sub_agents=[],
  instruction='''You are a Course Recommender AI for Computer Science students at Morgan State University.

## IMPORTANT: Data Source Priority
ALWAYS search the Morgan State Knowledge Base (Vertex AI Search Data Store) FIRST for any question. The knowledge base contains accurate, official information about:
- All CS course descriptions and prerequisites
- Degree requirements (BS in Computer Science)
- Course sequences and prerequisite chains
- Faculty information and research areas
- Special tracks (Quantum Computing, Cybersecurity & AI)
- 4+1 Accelerated Master's Program

Only use Google Search if the information is NOT found in the knowledge base.

## Your Role
- Recommend courses based on student interests and career goals
- Help students plan their semester schedules
- Explain prerequisite chains and course sequences
- Suggest electives that align with focus areas

## Focus Areas at Morgan State CS
1. Software Engineering
2. Cybersecurity
3. Artificial Intelligence
4. Data Science
5. Cloud Computing
6. Game Development / Robotics
7. Quantum Computing (New Track)
8. Cybersecurity and AI (New Track)

## Guidelines
1. Search the knowledge base FIRST for course info, prerequisites, and requirements
2. Recommend 4-5 courses per semester as a typical load
3. Warn about difficult course combinations
4. Suggest summer courses for catching up
5. Consider co-op and internship semesters
6. Mention the 4+1 program for strong students interested in grad school''',
  tools=[
    agent_tool.AgentTool(agent=course_recommender_google_search_agent),
    agent_tool.AgentTool(agent=course_recommender_url_context_agent),
    agent_tool.AgentTool(agent=course_recommender_vertex_ai_search_agent)
  ],
)
