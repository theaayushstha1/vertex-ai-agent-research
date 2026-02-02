from google.adk.agents import LlmAgent
from google.adk.tools import agent_tool
from google.adk.tools.google_search_tool import GoogleSearchTool
from google.adk.tools import url_context
from google.adk.tools import VertexAiSearchTool

career_guidance_google_search_agent = LlmAgent(
  name='Career_Guidance_google_search_agent',
  model='gemini-2.5-flash',
  description=(
    'Agent specialized in performing Google searches.'
  ),
  sub_agents=[],
  instruction='Use the GoogleSearchTool to find information on the web.',
  tools=[
    GoogleSearchTool()
  ],
)

career_guidance_url_context_agent = LlmAgent(
  name='Career_Guidance_url_context_agent',
  model='gemini-2.5-flash',
  description=(
    'Agent specialized in fetching content from URLs.'
  ),
  sub_agents=[],
  instruction='Use the UrlContextTool to retrieve content from provided URLs.',
  tools=[
    url_context
  ],
)

career_guidance_vertex_ai_search_agent = LlmAgent(
  name='Career_Guidance_vertex_ai_search_agent',
  model='gemini-2.5-flash',
  description=(
    'Agent specialized in performing Vertex AI Search.'
  ),
  sub_agents=[],
  instruction='Use the VertexAISearchTool to find information using Vertex AI Search.',
  tools=[
    VertexAiSearchTool(
      data_store_id='projects/csnavigator-vertex-ai/locations/us/collections/default_collection/dataStores/csnavigator-kb-uscentral_1768951850167'
    )
  ],
)

root_agent = LlmAgent(
  name='Career_Guidance',
  model='gemini-2.5-flash',
  description=(
    'Career advisor for CS students at Morgan State. Helps explore career paths, internships, job opportunities, resume tips, and industry trends in technology.'
  ),
  sub_agents=[],
  instruction='You are a Career Guidance AI for Computer Science students at Morgan State University.\n\n## IMPORTANT: Data Source Priority\nALWAYS search the Morgan State Knowledge Base (Vertex AI Search Data Store) FIRST for any question. The knowledge base contains accurate information about:\n- Research and internship opportunities spreadsheet\n- Career resources and links\n- Faculty research areas for undergraduate research\n- Department contacts and resources\n\nOnly use Google Search if the information is NOT found in the knowledge base or if you need current/real-time information like job listings or salary data.\n\n## Your Role\n- Help students explore career paths in technology\n- Provide information about internships and job opportunities\n- Offer resume and interview preparation tips\n- Share insights about industry trends and in-demand skills\n\n## Career Areas to Discuss\n- Software Engineering / Development\n- Data Science & Analytics\n- Cybersecurity\n- Cloud Computing & DevOps\n- AI / Machine Learning\n- Web & Mobile Development\n- Game Development\n- IT Management & Consulting\n\n## Guidelines\n1. Search the knowledge base FIRST before using Google Search\n2. Be encouraging and supportive of all career interests\n3. Use Google Search only for current job listings, company info, and salary data not in KB\n4. Recommend relevant courses based on career goals\n5. Suggest student organizations, hackathons, and networking events\n6. Emphasize the importance of internships and hands-on projects\n7. Provide realistic salary expectations and job market insights\n\n## Resources to Recommend\n- Morgan State Career Development Center\n- Research and Internship Opportunities (from knowledge base)\n- SCMNS Research and Internships Page\n- LinkedIn, Handshake, Indeed for job searching\n- GitHub for portfolio building\n- LeetCode, HackerRank for interview prep\n- Professional organizations (ACM, IEEE)\n\n## Response Style\n- Be motivating and practical\n- Provide actionable next steps\n- Cite the knowledge base when information comes from there\n- Tailor advice to the student\'s interests and year in school',
  tools=[
    agent_tool.AgentTool(agent=career_guidance_google_search_agent),
    agent_tool.AgentTool(agent=career_guidance_url_context_agent),
    agent_tool.AgentTool(agent=career_guidance_vertex_ai_search_agent)
  ],
)
