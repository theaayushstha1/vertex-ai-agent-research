"""Scholarship & Internship Bot V2 - flat agent, Tavily web search.

V2 differences from V1:
  - Tavily web_search replaces google_search grounding. Search call itself
    is faster (~1-2s vs 4-8s), which offsets gemini-2.5-flash's thinking
    overhead. Net: V2 should still be faster than V1 on search-heavy turns.
  - Package exposes `agent` and `root_agent` for cs_navigator reuse.

Model notes:
  - gemini-2.5-flash is used (V1's model, confirmed available in project).
  - flash-lite is faster but has a function-call name-resolution bug
    (returns "run" instead of the tool's real name).
  - 2.0-flash is not enabled in this Vertex project.
  - Disabling 2.5-flash's thinking_budget requires generate_content_config,
    which routes through direct Gemini API and demands GOOGLE_API_KEY
    (no free tier available to the current developer).
"""

from datetime import date

from dotenv import load_dotenv
from google.adk.agents import LlmAgent

from .tools.web_search import web_search

load_dotenv()

MODEL = "gemini-2.5-flash"


def _build_instruction(ctx) -> str:
    today = date.today()
    today_iso = today.strftime("%Y-%m-%d")
    today_human = today.strftime("%B %d, %Y")
    if today.month >= 8:
        semester = "Fall"
    elif today.month >= 6:
        semester = "Summer"
    else:
        semester = "Spring"

    return f"""
You are the Morgan State Scholarship & Internship Bot helping CS students find funding and career opportunities. Today is {today_human} ({today_iso}), semester: {semester} {today.year}.

DEADLINE RULE: Compare every deadline to {today_iso}. NEVER show expired ones. Flag <7d "URGENT", <30d "UPCOMING", else "OPEN". Sort soonest first.

SEARCH: Use `web_search` for time-sensitive info. Start with ONE broad query covering the student's year+major (e.g. "HBCU CS scholarships 2026 junior"). Then ONE narrower follow-up for Morgan State-specific or highly targeted hits (e.g. "Morgan State scholarship computer science GPA 3.5"). Stop at 2 searches unless a specific fact is still missing. If the tool errors, say search is down and fall back to general knowledge.

WHAT YOU DO:
1. SCHOLARSHIPS: search morgan.edu/financial-aid, ScholarshipUniverse, plus fastweb/scholarships.com/bold.org/uncf.org/thurgoodmarshallfund.org. Filter by student's GPA/year/major if given. Always remind them to check morgan.scholarshipuniverse.com.
2. INTERNSHIPS: prioritize HBCU-recruiting companies (Google STEP, Microsoft Explore, Meta University, Amazon Propel, Apple, IBM, NASA, NSA, Capital One, JPMorgan). Also check morgan.edu/career-center and Handshake.
3. COACHING: help with personal statements, cover letters, resumes, interview prep. Rank applications by deadline + fit.

PER OPPORTUNITY, SHOW: Name (bold), award/pay, eligibility, deadline + days remaining, apply link.

Ask year/focus/GPA/timeline only if needed to filter. Be encouraging and concise.
"""


agent = LlmAgent(
    name="Scholarship_Bot_V2",
    model=MODEL,
    tools=[web_search],
    instruction=_build_instruction,
)

root_agent = agent
