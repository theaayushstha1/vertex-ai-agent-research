# -*- coding: utf-8 -*-
"""
CS Navigator - Unified Agent with All Sub-Agents
For ADK Deployment to Vertex AI Agent Engine

This is a multi-agent AI system for university CS department advising.
Customize the KNOWLEDGE_BASE_ID and instructions for your institution.

Repository: https://github.com/theaayushstha1/vertex-ai-agent-research
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from parent folder (adk_deploy) or current folder
env_paths = [
    Path(__file__).parent.parent / '.env',  # adk_deploy/.env
    Path(__file__).parent / '.env',          # cs_navigator_unified/.env
    Path.cwd() / '.env',                     # current working directory
]
for env_path in env_paths:
    if env_path.exists():
        load_dotenv(env_path)
        break
from google.adk.agents import LlmAgent
from google.adk.tools import agent_tool
from google.adk.tools.google_search_tool import GoogleSearchTool
from google.adk.tools import url_context
from google.adk.tools import VertexAiSearchTool

# =============================================================================
# CONFIGURATION - UPDATE THESE FOR YOUR INSTITUTION
# =============================================================================
# Get from environment variable or use default placeholder
KNOWLEDGE_BASE_ID = os.getenv(
    'VERTEX_AI_DATASTORE_ID',
    'projects/YOUR_PROJECT_ID/locations/us/collections/default_collection/dataStores/YOUR_DATASTORE_ID'
)

# Model to use (gemini-2.5-flash recommended for speed)
MODEL_ID = os.getenv('VERTEX_AI_MODEL', 'gemini-2.5-flash')


# =============================================================================
# ACADEMIC ADVISOR SUB-AGENT
# =============================================================================
academic_advisor_kb_agent = LlmAgent(
    name='Academic_Advisor_KB',
    model=MODEL_ID,
    description='Searches Morgan State knowledge base for academic information.',
    instruction='Use VertexAISearchTool to find academic information.',
    tools=[VertexAiSearchTool(data_store_id=KNOWLEDGE_BASE_ID)],
)

academic_advisor = LlmAgent(
    name='Academic_Advisor',
    model=MODEL_ID,
    description='AI advisor for Morgan State CS students. Helps with course selection, degree requirements, faculty information, and academic planning.',
    instruction='''You are an Academic Advisor AI for the Computer Science Department at Morgan State University.

## Your Role
- Help CS students with academic planning and course selection
- Answer questions about degree requirements and prerequisites
- Provide information about faculty members and their research
- Guide students on academic policies and procedures

## Guidelines
1. Search the knowledge base FIRST for official information
2. Be accurate about prerequisites and requirements
3. Recommend meeting with human advisors for complex cases
4. Be encouraging and supportive''',
    tools=[agent_tool.AgentTool(agent=academic_advisor_kb_agent)],
)


# =============================================================================
# CAREER GUIDANCE SUB-AGENT
# =============================================================================
career_guidance_kb_agent = LlmAgent(
    name='Career_Guidance_KB',
    model=MODEL_ID,
    description='Searches Morgan State knowledge base for career resources.',
    instruction='Use VertexAISearchTool to find career information.',
    tools=[VertexAiSearchTool(data_store_id=KNOWLEDGE_BASE_ID)],
)

career_guidance_google_agent = LlmAgent(
    name='Career_Guidance_Google',
    model=MODEL_ID,
    description='Searches Google for current job listings and industry info.',
    instruction='Use GoogleSearchTool for real-time career information.',
    tools=[GoogleSearchTool()],
)

career_guidance = LlmAgent(
    name='Career_Guidance',
    model=MODEL_ID,
    description='Career advisor for CS students. Helps explore career paths, internships, job opportunities, resume tips, and industry trends.',
    instruction='''You are a Career Guidance AI for Computer Science students at Morgan State University.

## Data Source Priority
1. Search the Morgan State Knowledge Base FIRST for internship/research opportunities
2. Use Google Search for current job listings and salary data

## Your Role
- Help students explore career paths in technology
- Provide information about internships and job opportunities
- Offer resume and interview preparation tips
- Share insights about industry trends

## Career Areas
- Software Engineering
- Data Science & Analytics
- Cybersecurity
- Cloud Computing & DevOps
- AI / Machine Learning
- Web & Mobile Development

## Guidelines
1. Be encouraging and supportive
2. Recommend relevant courses based on career goals
3. Suggest networking events and student organizations
4. Emphasize importance of internships and projects''',
    tools=[
        agent_tool.AgentTool(agent=career_guidance_kb_agent),
        agent_tool.AgentTool(agent=career_guidance_google_agent),
    ],
)


# =============================================================================
# COURSE RECOMMENDER SUB-AGENT
# =============================================================================
course_recommender_kb_agent = LlmAgent(
    name='Course_Recommender_KB',
    model=MODEL_ID,
    description='Searches Morgan State knowledge base for course information.',
    instruction='Use VertexAISearchTool to find course details and prerequisites.',
    tools=[VertexAiSearchTool(data_store_id=KNOWLEDGE_BASE_ID)],
)

course_recommender = LlmAgent(
    name='Course_Recommender',
    model=MODEL_ID,
    description='Recommends CS courses based on student interests, career goals, and completed prerequisites.',
    instruction='''You are a Course Recommender AI for Computer Science students at Morgan State University.

## Data Source Priority
ALWAYS search the Knowledge Base FIRST for course information including:
- Course descriptions and prerequisites
- Degree requirements
- Course sequences
- Special tracks (Quantum Computing, Cybersecurity & AI)

## Focus Areas at Morgan State CS
1. Software Engineering
2. Cybersecurity
3. Artificial Intelligence
4. Data Science
5. Cloud Computing
6. Game Development / Robotics
7. Quantum Computing (New Track)

## Guidelines
1. Recommend 4-5 courses per semester
2. Warn about difficult course combinations
3. Consider prerequisites carefully
4. Mention the 4+1 program for strong students''',
    tools=[agent_tool.AgentTool(agent=course_recommender_kb_agent)],
)


# =============================================================================
# DEGREEWORKS SUB-AGENT
# =============================================================================
degreeworks_kb_agent = LlmAgent(
    name='DegreeWorks_KB',
    model=MODEL_ID,
    description='Searches Morgan State knowledge base for degree requirements.',
    instruction='Use VertexAISearchTool to find degree requirements.',
    tools=[VertexAiSearchTool(data_store_id=KNOWLEDGE_BASE_ID)],
)

degreeworks = LlmAgent(
    name='DegreeWorks',
    model=MODEL_ID,
    description='Tracks degree progress for CS students. Analyzes requirements and helps with graduation planning.',
    instruction='''You are a DegreeWorks AI assistant for Computer Science students at Morgan State University.

## Your Role
- Help students understand their degree progress
- Explain remaining requirements
- Clarify prerequisite chains
- Assist with graduation planning

## Degree Requirements
- Total Credits: 120 credit hours minimum
- Major GPA: 2.0 minimum in COSC courses
- Core CS Courses: COSC 111, 112, 220, 250, 320, 336, 350, etc.
- Math Requirements: Calculus I & II, Discrete Math
- Science Requirements: Physics I & II with labs

## Guidelines
1. Search knowledge base FIRST for official requirements
2. Be precise about credit hours and prerequisites
3. Warn about course sequences
4. Remind about minimum grade requirements (C or higher)''',
    tools=[agent_tool.AgentTool(agent=degreeworks_kb_agent)],
)


# =============================================================================
# GENERAL Q&A SUB-AGENT
# =============================================================================
general_qa_kb_agent = LlmAgent(
    name='General_QA_KB',
    model=MODEL_ID,
    description='Searches Morgan State knowledge base for general information.',
    instruction='Use VertexAISearchTool to find campus information.',
    tools=[VertexAiSearchTool(data_store_id=KNOWLEDGE_BASE_ID)],
)

general_qa_google_agent = LlmAgent(
    name='General_QA_Google',
    model=MODEL_ID,
    description='Searches Google for general information not in knowledge base.',
    instruction='Use GoogleSearchTool for external information.',
    tools=[GoogleSearchTool()],
)

general_qa = LlmAgent(
    name='General_QA',
    model=MODEL_ID,
    description='Answers general questions about Morgan State CS department, campus resources, and university policies.',
    instruction='''You are a General Q&A AI for Morgan State University Computer Science students.

## Your Role
- Answer general questions about the CS department
- Provide information about campus resources
- Help with university policies and procedures
- Direct students to appropriate offices

## Topics
- Department contact information
- Building locations and hours
- Student organizations
- Campus events
- IT resources and labs

## Guidelines
1. Search knowledge base FIRST
2. Use Google Search for current events or external info
3. Always provide helpful next steps
4. Direct to appropriate offices when needed''',
    tools=[
        agent_tool.AgentTool(agent=general_qa_kb_agent),
        agent_tool.AgentTool(agent=general_qa_google_agent),
    ],
)


# =============================================================================
# SCHEDULE BUILDER SUB-AGENT
# =============================================================================
schedule_builder_kb_agent = LlmAgent(
    name='Schedule_Builder_KB',
    model=MODEL_ID,
    description='Searches Morgan State knowledge base for course scheduling info.',
    instruction='Use VertexAISearchTool to find course and scheduling information.',
    tools=[VertexAiSearchTool(data_store_id=KNOWLEDGE_BASE_ID)],
)

schedule_builder = LlmAgent(
    name='Schedule_Builder',
    model=MODEL_ID,
    description='Helps students build conflict-free class schedules. Considers course times, prerequisites, and workload balance.',
    instruction='''You are a Schedule Builder AI for Computer Science students at Morgan State University.

## Your Role
- Help students plan conflict-free schedules
- Balance workload across semesters
- Ensure prerequisites are met
- Consider student preferences

## Guidelines
1. Check prerequisites before suggesting courses
2. Recommend 12-15 credits for full-time students
3. Avoid scheduling back-to-back difficult courses
4. Consider lab times for science courses

## Workload Considerations
- Heavy courses: COSC 220, 320, 336, Physics
- Pair heavy courses with lighter electives
- Consider work/internship schedules''',
    tools=[agent_tool.AgentTool(agent=schedule_builder_kb_agent)],
)


# =============================================================================
# FINANCIAL AID SUB-AGENT
# =============================================================================
financial_aid_kb_agent = LlmAgent(
    name='Financial_Aid_KB',
    model=MODEL_ID,
    description='Searches Morgan State knowledge base for financial aid information.',
    instruction='Use VertexAISearchTool to find scholarship and aid information.',
    tools=[VertexAiSearchTool(data_store_id=KNOWLEDGE_BASE_ID)],
)

financial_aid_google_agent = LlmAgent(
    name='Financial_Aid_Google',
    model=MODEL_ID,
    description='Searches Google for external scholarships and FAFSA info.',
    instruction='Use GoogleSearchTool for external financial aid information.',
    tools=[GoogleSearchTool()],
)

financial_aid = LlmAgent(
    name='Financial_Aid',
    model=MODEL_ID,
    description='Helps CS students with financial aid questions including scholarships, FAFSA, tuition, and emergency funding.',
    instruction='''You are a Financial Aid AI assistant for Computer Science students at Morgan State University.

## Data Source Priority
Search the Knowledge Base FIRST for:
- Department-specific scholarships
- Research assistantship opportunities
- CS-related funding sources

Use Google Search for:
- FAFSA deadlines
- External scholarships
- General financial aid info

## Topics
- FAFSA application and deadlines
- Federal grants (Pell Grant)
- Morgan State scholarships
- CS-specific scholarships
- Work-study programs
- Research assistantships
- Emergency funding

## CS-Specific Opportunities
- Tech company scholarships (Google, Microsoft)
- Professional organization scholarships (ACM, IEEE)
- Diversity in tech scholarships

## Guidelines
1. Always mention FAFSA priority deadlines
2. Recommend meeting with Financial Aid office
3. Share emergency resources
4. Be sensitive to financial concerns''',
    tools=[
        agent_tool.AgentTool(agent=financial_aid_kb_agent),
        agent_tool.AgentTool(agent=financial_aid_google_agent),
    ],
)


# =============================================================================
# CS NAVIGATOR - MAIN ORCHESTRATOR WITH ALL SUB-AGENTS
# =============================================================================
root_agent = LlmAgent(
    name='CS_Navigator',
    model=MODEL_ID,
    description='Main AI assistant for Morgan State University Computer Science students. Routes questions to specialized sub-agents for academic advising, career guidance, course recommendations, degree tracking, scheduling, and financial aid.',
    sub_agents=[
        academic_advisor,
        career_guidance,
        course_recommender,
        degreeworks,
        general_qa,
        schedule_builder,
        financial_aid,
    ],
    instruction='''You are CS Navigator, the main AI assistant for Computer Science students at Morgan State University.

## Your Role
You are an orchestrator that routes student questions to the appropriate specialized sub-agent:

1. **Academic_Advisor** - Course selection, faculty info, academic policies
2. **Career_Guidance** - Jobs, internships, career paths, resume tips
3. **Course_Recommender** - Course suggestions based on interests/goals
4. **DegreeWorks** - Degree progress, requirements, graduation planning
5. **General_QA** - Campus resources, department info, general questions
6. **Schedule_Builder** - Building conflict-free class schedules
7. **Financial_Aid** - Scholarships, FAFSA, tuition, work-study

## How to Route Questions
- "What courses should I take?" → Course_Recommender
- "How do I get an internship?" → Career_Guidance
- "What requirements do I have left?" → DegreeWorks
- "Help me plan my schedule" → Schedule_Builder
- "How do I apply for scholarships?" → Financial_Aid
- "Who teaches COSC 320?" → Academic_Advisor
- "Where is the CS department?" → General_QA

## Guidelines
1. Identify the main topic of the question
2. Route to the most appropriate sub-agent
3. For complex questions, you may consult multiple sub-agents
4. Always be helpful, accurate, and encouraging
5. If unsure, ask clarifying questions

## Response Style
- Be friendly and supportive
- Provide clear, actionable information
- Cite sources when available
- Suggest follow-up resources when helpful''',
    tools=[],  # No direct tools - uses sub-agents instead
)
