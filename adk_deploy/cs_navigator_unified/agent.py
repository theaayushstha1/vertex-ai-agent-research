# -*- coding: utf-8 -*-
"""
CS Navigator - Agentic RAG with Specialized Sub-Agents
For ADK Deployment to Vertex AI Agent Engine

ARCHITECTURE: 1 router + 7 specialists invoked via AgentTool.
Each specialist has native VertexAiSearchTool (automatic grounding — KB searched on every query).
AgentTool avoids ADK injecting transfer_to_agent that conflicts with search tools.

Original (14 agents, ~40s):
  root → sub_agent → AgentTool(KB_wrapper) → VertexAiSearchTool  (6 LLM calls)

Now (8 agents, ~6-10s):
  root → AgentTool(specialist with native VertexAiSearchTool)     (3 LLM calls)
  LLM #1: router picks specialist                                 (~1-2s)
  LLM #2: specialist answers WITH automatic KB grounding           (~3-5s)
  LLM #3: router returns answer                                    (~1-2s)

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
from google.adk.tools import VertexAiSearchTool

# =============================================================================
# CONFIGURATION
# =============================================================================
KNOWLEDGE_BASE_ID = os.getenv(
    'VERTEX_AI_DATASTORE_ID',
    'projects/YOUR_PROJECT_ID/locations/us/collections/default_collection/dataStores/YOUR_DATASTORE_ID'
)

MODEL_ID = os.getenv('VERTEX_AI_MODEL', 'gemini-2.0-flash')

# Native VertexAiSearchTool — automatic grounding, KB searched on every query.
kb_search = VertexAiSearchTool(data_store_id=KNOWLEDGE_BASE_ID)

# Every specialist gets this rule: only answer from KB, never fabricate.
GROUNDING_RULE = """STRICT RULE: ONLY use information from the knowledge base search results to answer.
NEVER fabricate or guess any facts — no made-up names, courses, emails, numbers, or details.
If the knowledge base does not have the answer, honestly say you could not find it and suggest the student contact the department directly."""


# =============================================================================
# SPECIALIST AGENTS
# =============================================================================

academic_advisor = LlmAgent(
    name='Academic_Advisor',
    model=MODEL_ID,
    description='Academic advising: course selection, degree requirements, faculty info, academic policies, prerequisites.',
    instruction=f'''{GROUNDING_RULE}
You are an Academic Advisor AI for the CS Department at Morgan State University.
Help students with academic planning, course selection, degree requirements, prerequisites, and faculty info.''',
    tools=[kb_search],
)

career_guidance = LlmAgent(
    name='Career_Guidance',
    model=MODEL_ID,
    description='Career paths, internships, job opportunities, resume tips, industry trends, networking.',
    instruction=f'''{GROUNDING_RULE}
You are a Career Guidance AI for CS students at Morgan State University.
Help students explore career paths, internships, job opportunities, and industry trends.''',
    tools=[kb_search],
)

course_recommender = LlmAgent(
    name='Course_Recommender',
    model=MODEL_ID,
    description='Course suggestions based on interests, career goals, prerequisites, and degree tracks.',
    instruction=f'''{GROUNDING_RULE}
You are a Course Recommender AI for CS students at Morgan State University.
Recommend courses based on student interests, career goals, and prerequisites found in the knowledge base.''',
    tools=[kb_search],
)

degreeworks = LlmAgent(
    name='DegreeWorks',
    model=MODEL_ID,
    description='Degree progress tracking, remaining requirements, prerequisite chains, graduation planning.',
    instruction=f'''{GROUNDING_RULE}
You are a DegreeWorks AI for CS students at Morgan State University.
Help students understand degree progress, remaining requirements, prerequisite chains, and graduation planning.''',
    tools=[kb_search],
)

general_qa = LlmAgent(
    name='General_QA',
    model=MODEL_ID,
    description='General questions: CS department info, campus resources, building locations, student organizations, university policies, faculty, chair.',
    instruction=f'''{GROUNDING_RULE}
You are a General Q&A AI for CS students at Morgan State University.
Answer general questions about the CS department, campus resources, contacts, locations, and policies.''',
    tools=[kb_search],
)

schedule_builder = LlmAgent(
    name='Schedule_Builder',
    model=MODEL_ID,
    description='Class scheduling: conflict-free schedules, workload balance, prerequisites, course times.',
    instruction=f'''{GROUNDING_RULE}
You are a Schedule Builder AI for CS students at Morgan State University.
Help students build conflict-free schedules and balance their workload using courses from the knowledge base.''',
    tools=[kb_search],
)

financial_aid = LlmAgent(
    name='Financial_Aid',
    model=MODEL_ID,
    description='Financial aid: scholarships, FAFSA, tuition, work-study, research assistantships, emergency funding.',
    instruction=f'''{GROUNDING_RULE}
You are a Financial Aid AI for CS students at Morgan State University.
Help with scholarships, FAFSA, tuition, work-study, and funding using information from the knowledge base.''',
    tools=[kb_search],
)


# =============================================================================
# CS NAVIGATOR - ROUTER
# =============================================================================
root_agent = LlmAgent(
    name='CS_Navigator',
    model=MODEL_ID,
    description='Main AI assistant for Morgan State University CS students.',
    instruction='''You are CS Navigator for Computer Science students at Morgan State University.
Your ONLY job is to route questions to the right specialist. NEVER answer directly.

- **Academic_Advisor** — course selection, faculty, academic policies, prerequisites
- **Career_Guidance** — jobs, internships, career paths, resume tips
- **Course_Recommender** — course suggestions based on interests/goals
- **DegreeWorks** — degree progress, remaining requirements, graduation
- **General_QA** — department info, locations, contacts, general questions
- **Schedule_Builder** — class schedules, workload balance
- **Financial_Aid** — scholarships, FAFSA, tuition, funding

Call the right specialist and return their answer as-is.''',
    tools=[
        agent_tool.AgentTool(agent=academic_advisor),
        agent_tool.AgentTool(agent=career_guidance),
        agent_tool.AgentTool(agent=course_recommender),
        agent_tool.AgentTool(agent=degreeworks),
        agent_tool.AgentTool(agent=general_qa),
        agent_tool.AgentTool(agent=schedule_builder),
        agent_tool.AgentTool(agent=financial_aid),
    ],
)
