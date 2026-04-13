# Tutor V2 + Scholarship V2 Speed Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship faster V2 versions of the tutor and scholarship+internship ADK agents as parallel packages, without touching V1, so they can be A/B compared and later dropped into `cs_navigator` as sub-agents.

**Architecture:** One flat `LlmAgent` per bot (no sub-agents, no `AgentTool` wrapping). Disable `gemini-2.5-flash` thinking via `thinking_config={"thinking_budget": 0}`. Replace `google_search` grounding in the scholarship bot with a custom `web_search` function tool backed by the Tavily API.

**Tech Stack:** Python 3.10+, Google ADK (`google-adk`), Tavily Python SDK (`tavily-python`), pytest for tool unit tests, `python-dotenv` for env loading.

**Spec:** `docs/superpowers/specs/2026-04-13-tutor-scholarship-v2-speed-design.md`

---

## File Structure

**New files (creates):**
- `adk_deploy/scholarship_internship_bot_v2/__init__.py` — exposes `root_agent` and `agent`
- `adk_deploy/scholarship_internship_bot_v2/agent.py` — flat `LlmAgent` with `web_search` tool
- `adk_deploy/scholarship_internship_bot_v2/tools/__init__.py` — empty package marker
- `adk_deploy/scholarship_internship_bot_v2/tools/web_search.py` — Tavily-backed function tool
- `adk_deploy/scholarship_internship_bot_v2/tools/test_web_search.py` — pytest unit tests
- `adk_deploy/tutor_v2/__init__.py` — exposes `root_agent` and `agent`
- `adk_deploy/tutor_v2/agent.py` — flat `LlmAgent` importing V1 tools via `sys.path` shim
- `.env.example` — documents required env vars (TAVILY_API_KEY, etc.)

**Modifies:**
- `pyproject.toml` — add `tavily-python>=0.3.0` dependency

**V1 files are NOT modified.** `adk_deploy/tutor/` and `adk_deploy/scholarship_internship_bot/` remain byte-for-byte identical.

---

## Task 1: Add Tavily dependency

**Files:**
- Modify: `pyproject.toml`

- [ ] **Step 1: Add tavily-python to dependencies**

Open `pyproject.toml` and add this line inside the `dependencies = [...]` list, after the existing Google ADK line:

```toml
    # Web search for scholarship V2 (replaces google_search grounding)
    "tavily-python>=0.3.0",
```

- [ ] **Step 2: Install the new dependency**

Run from repo root:
```bash
cd /Users/juliangordon/Documents/vertex-ai-agent-research
pip install -e .
```

Expected output: `Successfully installed tavily-python-0.x.x` (and no errors on existing deps).

- [ ] **Step 3: Verify import works**

Run:
```bash
python -c "from tavily import TavilyClient; print('ok')"
```

Expected: `ok`

- [ ] **Step 4: Commit**

```bash
cd /Users/juliangordon/Documents/vertex-ai-agent-research
git add pyproject.toml
git commit -m "deps: add tavily-python for scholarship V2 web search"
```

---

## Task 2: Document env vars in .env.example

**Files:**
- Create: `.env.example`

- [ ] **Step 1: Create .env.example at repo root**

Create `/Users/juliangordon/Documents/vertex-ai-agent-research/.env.example` with this content:

```bash
# Google Cloud / Vertex AI
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=us-central1
GOOGLE_GENAI_USE_VERTEXAI=TRUE

# Vertex AI Search datastores (used by tutor)
VERTEX_AI_DATASTORE_ID=
SYLLABI_DATASTORE_ID=

# Canvas LMS (used by tutor)
CANVAS_BASE_URL=https://canvas.instructure.com
CANVAS_ACCESS_TOKEN=

# Tavily web search (used by scholarship_internship_bot_v2)
# Get a free key at https://app.tavily.com
TAVILY_API_KEY=tvly-...
```

- [ ] **Step 2: Add real key to local .env (done by user, not in plan)**

If your local `.env` already has `TAVILY_API_KEY=...`, skip this. Otherwise append it. `.env` is gitignored and will never be committed.

- [ ] **Step 3: Commit .env.example**

```bash
cd /Users/juliangordon/Documents/vertex-ai-agent-research
git add .env.example
git commit -m "docs: add .env.example with TAVILY_API_KEY placeholder"
```

---

## Task 3: Scaffold scholarship_internship_bot_v2 package

**Files:**
- Create: `adk_deploy/scholarship_internship_bot_v2/__init__.py`
- Create: `adk_deploy/scholarship_internship_bot_v2/tools/__init__.py`

- [ ] **Step 1: Create package directory and empty tools package marker**

```bash
cd /Users/juliangordon/Documents/vertex-ai-agent-research
mkdir -p adk_deploy/scholarship_internship_bot_v2/tools
```

- [ ] **Step 2: Create `tools/__init__.py` as empty file**

Create `adk_deploy/scholarship_internship_bot_v2/tools/__init__.py` with content:

```python
```

(A zero-byte file — just the package marker.)

- [ ] **Step 3: Create package `__init__.py` placeholder**

Create `adk_deploy/scholarship_internship_bot_v2/__init__.py` with content:

```python
"""Scholarship & Internship Bot V2 — flat agent with Tavily web search.

This module exposes `root_agent` (for `adk run`) and `agent` (for import
into cs_navigator) once agent.py is implemented.
"""
# agent.py is imported lazily by consumers (adk or cs_navigator).
# Importing this package does not eagerly construct the agent.
```

- [ ] **Step 4: Commit**

```bash
git add adk_deploy/scholarship_internship_bot_v2/__init__.py adk_deploy/scholarship_internship_bot_v2/tools/__init__.py
git commit -m "scaffold: scholarship_internship_bot_v2 package skeleton"
```

---

## Task 4: Write failing test for web_search happy path

**Files:**
- Create: `adk_deploy/scholarship_internship_bot_v2/tools/test_web_search.py`

- [ ] **Step 1: Write the failing test**

Create `adk_deploy/scholarship_internship_bot_v2/tools/test_web_search.py`:

```python
"""Unit tests for the Tavily-backed web_search function tool."""

from unittest.mock import patch, MagicMock

import pytest


def test_web_search_returns_normalized_results(monkeypatch):
    """Happy path: Tavily returns results, tool returns normalized list of dicts."""
    monkeypatch.setenv("TAVILY_API_KEY", "tvly-test-fake-key")

    fake_tavily_response = {
        "results": [
            {
                "title": "Morgan State CS Scholarships 2026",
                "url": "https://morgan.edu/financial-aid/scholarships",
                "content": "Scholarships available for CS students...",
                "published_date": "2026-02-01",
            },
            {
                "title": "UNCF STEM Scholars Program",
                "url": "https://uncf.org/programs/stem",
                "content": "Annual awards for HBCU STEM students...",
            },
        ]
    }

    with patch(
        "adk_deploy.scholarship_internship_bot_v2.tools.web_search.TavilyClient"
    ) as mock_client_cls:
        mock_client = MagicMock()
        mock_client.search.return_value = fake_tavily_response
        mock_client_cls.return_value = mock_client

        from adk_deploy.scholarship_internship_bot_v2.tools.web_search import web_search

        result = web_search(query="Morgan State CS scholarships", max_results=5)

    assert isinstance(result, dict)
    assert "results" in result
    assert len(result["results"]) == 2
    assert result["results"][0]["title"] == "Morgan State CS Scholarships 2026"
    assert result["results"][0]["url"] == "https://morgan.edu/financial-aid/scholarships"
    assert result["results"][0]["snippet"] == "Scholarships available for CS students..."
    assert result["results"][0]["published_date"] == "2026-02-01"
    assert result["results"][1]["published_date"] is None
    mock_client.search.assert_called_once_with(
        query="Morgan State CS scholarships",
        max_results=5,
        search_depth="basic",
        include_answer=False,
    )
```

- [ ] **Step 2: Run the test and confirm it fails**

Run from repo root:
```bash
cd /Users/juliangordon/Documents/vertex-ai-agent-research
pytest adk_deploy/scholarship_internship_bot_v2/tools/test_web_search.py::test_web_search_returns_normalized_results -v
```

Expected: `FAILED` with `ModuleNotFoundError: No module named 'adk_deploy.scholarship_internship_bot_v2.tools.web_search'` (because `web_search.py` doesn't exist yet).

---

## Task 5: Implement web_search happy path to pass the test

**Files:**
- Create: `adk_deploy/scholarship_internship_bot_v2/tools/web_search.py`

- [ ] **Step 1: Write minimal implementation**

Create `adk_deploy/scholarship_internship_bot_v2/tools/web_search.py`:

```python
"""Tavily-backed web search tool for the scholarship V2 agent.

Replaces Gemini's `google_search` grounding with a regular function tool
so it can coexist with other function tools on the same LlmAgent.
"""

import os
from typing import Any

from tavily import TavilyClient


def _get_client() -> TavilyClient:
    api_key = os.environ.get("TAVILY_API_KEY")
    if not api_key:
        raise RuntimeError(
            "TAVILY_API_KEY not set. Add it to .env. "
            "Get a free key at https://app.tavily.com."
        )
    return TavilyClient(api_key=api_key)


def web_search(query: str, max_results: int = 5) -> dict[str, Any]:
    """Search the web for current scholarship, internship, and career info.

    Use this for questions about current opportunities, deadlines, company
    programs, or anything that changes week-to-week. Do NOT use for general
    CS concepts or historical facts.

    Args:
        query: What to search for. Be specific (e.g., "Google STEP 2026
            deadline" beats "Google internships").
        max_results: How many results to return, 1-10. Default 5.

    Returns:
        A dict with key "results" holding a list of
        {title, url, snippet, published_date} entries. On error, the dict
        has an "error" key and empty "results".
    """
    try:
        client = _get_client()
        raw = client.search(
            query=query,
            max_results=max_results,
            search_depth="basic",
            include_answer=False,
        )
    except Exception as exc:
        return {"error": str(exc), "results": []}

    normalized = [
        {
            "title": r.get("title", ""),
            "url": r.get("url", ""),
            "snippet": r.get("content", ""),
            "published_date": r.get("published_date"),
        }
        for r in raw.get("results", [])
    ]
    return {"results": normalized}
```

- [ ] **Step 2: Run the test and confirm it passes**

```bash
cd /Users/juliangordon/Documents/vertex-ai-agent-research
pytest adk_deploy/scholarship_internship_bot_v2/tools/test_web_search.py::test_web_search_returns_normalized_results -v
```

Expected: `PASSED`

- [ ] **Step 3: Commit**

```bash
git add adk_deploy/scholarship_internship_bot_v2/tools/web_search.py adk_deploy/scholarship_internship_bot_v2/tools/test_web_search.py
git commit -m "feat(scholarship_v2): add Tavily-backed web_search tool"
```

---

## Task 6: Add missing-API-key failing test and implementation check

**Files:**
- Modify: `adk_deploy/scholarship_internship_bot_v2/tools/test_web_search.py`

- [ ] **Step 1: Append a new failing test**

Append this test to `test_web_search.py`:

```python
def test_web_search_returns_error_dict_when_api_key_missing(monkeypatch):
    """If TAVILY_API_KEY is unset, web_search returns {'error': ..., 'results': []}."""
    monkeypatch.delenv("TAVILY_API_KEY", raising=False)

    from adk_deploy.scholarship_internship_bot_v2.tools.web_search import web_search

    result = web_search(query="anything", max_results=3)

    assert result["results"] == []
    assert "error" in result
    assert "TAVILY_API_KEY" in result["error"]


def test_web_search_returns_error_dict_on_tavily_exception(monkeypatch):
    """If Tavily raises (network/5xx/rate-limit), tool returns error dict, does not raise."""
    monkeypatch.setenv("TAVILY_API_KEY", "tvly-test-fake-key")

    with patch(
        "adk_deploy.scholarship_internship_bot_v2.tools.web_search.TavilyClient"
    ) as mock_client_cls:
        mock_client = MagicMock()
        mock_client.search.side_effect = RuntimeError("Rate limit exceeded")
        mock_client_cls.return_value = mock_client

        from adk_deploy.scholarship_internship_bot_v2.tools.web_search import web_search

        result = web_search(query="anything", max_results=3)

    assert result["results"] == []
    assert "error" in result
    assert "Rate limit exceeded" in result["error"]
```

- [ ] **Step 2: Run all three tests and confirm all pass**

```bash
cd /Users/juliangordon/Documents/vertex-ai-agent-research
pytest adk_deploy/scholarship_internship_bot_v2/tools/test_web_search.py -v
```

Expected: `3 passed` — the implementation in Task 5 already handles both error cases (missing key raises `RuntimeError` caught by the try block; Tavily exceptions caught by the same block).

- [ ] **Step 3: Commit**

```bash
git add adk_deploy/scholarship_internship_bot_v2/tools/test_web_search.py
git commit -m "test(scholarship_v2): cover missing-key and tavily-exception paths"
```

---

## Task 7: Implement scholarship_v2 agent.py

**Files:**
- Create: `adk_deploy/scholarship_internship_bot_v2/agent.py`

- [ ] **Step 1: Create the flat LlmAgent**

Create `adk_deploy/scholarship_internship_bot_v2/agent.py`:

```python
"""Scholarship & Internship Bot V2 — flat agent, Tavily web search, no thinking.

V2 differences from V1:
  - `web_search` (Tavily) replaces `google_search` grounding for lower
    latency and to unblock coexistence with future function tools.
  - `thinking_budget=0` skips internal reasoning on gemini-2.5-flash so
    tokens start streaming immediately.
  - Same instruction body as V1 (deadline rule, three modes, sources).
"""

import os
from datetime import date

from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.genai import types as genai_types

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
You are the Morgan State Scholarship & Internship Bot - helping CS students find funding and career opportunities.

TODAY IS {today_human} ({today_iso}). Current academic semester: {semester} {today.year}.

CRITICAL RULE - DEADLINE FILTERING:
- Compare every deadline you find against {today_iso}. Do the date math yourself.
- NEVER recommend opportunities with expired deadlines. Skip them entirely.
- Sort results by deadline (soonest first) so students can prioritize.
- Flag anything due within 7 days as "URGENT", within 30 days as "UPCOMING", otherwise "OPEN".

SEARCH TOOL:
- Use the `web_search` tool for anything time-sensitive (deadlines, current openings, new programs).
- Call it with a specific query - "Google STEP 2026 deadline" beats "Google internships".
- max_results defaults to 5; bump to 10 only if the first search is thin.
- If web_search returns an error, tell the student search is temporarily down and answer from general knowledge where you can.

You can help with three things:

**1. FINDING SCHOLARSHIPS**
When a student asks about scholarships:
- Search Morgan State's official pages first: morgan.edu/financial-aid, morgan.edu/financial-aid/scholarships
- Search ScholarshipUniverse for Morgan State: morgan.scholarshipuniverse.com (tell students to log in there to apply)
- Search external STEM/CS scholarships for HBCU students
- Search for scholarships on: fastweb.com, scholarships.com, bold.org, thurgoodmarshallfund.org, uncf.org
- For each scholarship provide:
  * Name
  * Award amount
  * Eligibility requirements
  * Deadline (verified against today's date)
  * How to apply (direct link if available)
  * Days remaining
- Filter by what they qualify for if they share their GPA, year, or major
- Group results: "Urgent (< 7 days)" > "Upcoming (< 30 days)" > "Open"

**2. FINDING INTERNSHIPS**
When a student asks about internships:
- Search for current CS internship openings relevant to Morgan State students
- Prioritize companies with HBCU recruiting programs:
  Google STEP/SWE, Microsoft Explore, Meta University, Amazon Propel,
  Apple, IBM, NASA, NSA, Lockheed Martin, Northrop Grumman,
  Capital One, JPMorgan, Bank of America, Deloitte, Accenture
- Check morgan.edu/career-center and Handshake for on-campus postings
- For each internship provide:
  * Company and role
  * Location (remote/hybrid/on-site)
  * Pay/stipend
  * Application deadline (verified against today's date)
  * Required skills and year
  * Application link
  * Days remaining
- Match to their year, interests (AI/ML, cybersecurity, web dev, etc.), and timeline

**3. APPLICATION COACHING**
When a student needs help applying:
- Help write personal statements and scholarship essays
- Help craft cover letters for internship applications
- Give resume tips specific to CS students (projects, GitHub, skills section)
- Prep for technical interviews (search for company-specific interview processes)
- Prioritize which opportunities to apply to first based on deadlines and fit

FORMAT YOUR RESPONSES CLEARLY:
- Use numbered lists for multiple opportunities
- Bold the scholarship/internship name
- Always show the deadline and days remaining
- Include a direct link where possible
- At the end, remind students to check morgan.scholarshipuniverse.com for institutional scholarships

Always ask clarifying questions to give better results:
- What year are you? (freshman/sophomore/junior/senior/grad)
- What's your focus area? (general CS, AI/ML, cybersecurity, data science, web dev, etc.)
- Any GPA or eligibility requirements to keep in mind?
- What semester/timeline are you looking for?
- Are you looking for need-based, merit-based, or both?

Opening message when a student connects:
"Hey! I'm here to help you find scholarships and internships at Morgan State and beyond. I can search for current opportunities, check deadlines, help you figure out what you qualify for, and coach you through applications. What are you looking for?"

Be encouraging and proactive - a lot of students don't know what's out there. Always use `web_search` to get the most current deadlines and openings. NEVER show expired opportunities.
"""


agent = LlmAgent(
    name="Scholarship_Bot_V2",
    model=MODEL,
    tools=[web_search],
    instruction=_build_instruction,
    generate_content_config=genai_types.GenerateContentConfig(
        thinking_config=genai_types.ThinkingConfig(thinking_budget=0),
    ),
)

root_agent = agent
```

- [ ] **Step 2: Update package `__init__.py` to re-export agent symbols**

Replace the content of `adk_deploy/scholarship_internship_bot_v2/__init__.py` with:

```python
"""Scholarship & Internship Bot V2 — flat agent with Tavily web search."""

from .agent import agent, root_agent

__all__ = ["agent", "root_agent"]
```

- [ ] **Step 3: Smoke-import the agent**

```bash
cd /Users/juliangordon/Documents/vertex-ai-agent-research
python -c "from adk_deploy.scholarship_internship_bot_v2 import root_agent; print(root_agent.name)"
```

Expected output: `Scholarship_Bot_V2`

If it errors on `ThinkingConfig` not existing, the installed `google-genai` is older than the ADK shipped with the repo — stop and flag; do not work around by removing the thinking config.

- [ ] **Step 4: Commit**

```bash
git add adk_deploy/scholarship_internship_bot_v2/__init__.py adk_deploy/scholarship_internship_bot_v2/agent.py
git commit -m "feat(scholarship_v2): flat LlmAgent, no thinking, Tavily search"
```

---

## Task 8: Manual smoke test scholarship_v2

**Files:** none modified.

- [ ] **Step 1: Launch adk run**

Run in a terminal (user-driven; if running this as an agent and you cannot drive an interactive terminal, skip this task and note that manual verification is required):

```bash
cd /Users/juliangordon/Documents/vertex-ai-agent-research
adk run adk_deploy/scholarship_internship_bot_v2
```

- [ ] **Step 2: Send the three canonical prompts, observe behavior**

Type each of these one at a time and watch for:
1. `Find CS scholarships for junior year` — expect: calls `web_search`, returns a numbered list with deadlines and days-remaining flags.
2. `What are the Google STEP / Microsoft Explore deadlines?` — expect: calls `web_search` once or twice, reports deadlines verified against today's date.
3. `Help me write a personal statement for the UNCF scholarship` — expect: no web_search call necessary (coaching mode), conversational response.

- [ ] **Step 3: Note wall-clock time to first token**

You don't need a stopwatch — a "feels faster than V1" read is enough for now. Formal A/B is Task 12.

- [ ] **Step 4: Commit a note if anything surprising showed up**

If the smoke test surfaces a bug, open a task in your backlog or note it inline here. No commit needed otherwise.

---

## Task 9: Scaffold tutor_v2 package

**Files:**
- Create: `adk_deploy/tutor_v2/__init__.py`

- [ ] **Step 1: Create package dir**

```bash
cd /Users/juliangordon/Documents/vertex-ai-agent-research
mkdir -p adk_deploy/tutor_v2
```

- [ ] **Step 2: Create placeholder `__init__.py`**

Create `adk_deploy/tutor_v2/__init__.py`:

```python
"""Tutor V2 — flat agent combining all six V1 sub-agents into one instruction."""
# agent.py imports V1 tools via sys.path shim; this package has no tools/ dir.
```

- [ ] **Step 3: Commit**

```bash
git add adk_deploy/tutor_v2/__init__.py
git commit -m "scaffold: tutor_v2 package skeleton"
```

---

## Task 10: Implement tutor_v2 agent.py

**Files:**
- Create: `adk_deploy/tutor_v2/agent.py`
- Modify: `adk_deploy/tutor_v2/__init__.py`

- [ ] **Step 1: Create the flat tutor LlmAgent**

Create `adk_deploy/tutor_v2/agent.py`:

```python
"""Tutor V2 — one flat LlmAgent with all V1 tools and all six sub-agent modes.

V2 differences from V1:
  - No sub-agents. The six V1 specialists (CS Tutor, Math Tutor, Quiz Master,
    Code Debugger, Problem Solver, Syllabus Advisor) become labeled sections
    of a single instruction. The model picks a mode based on the question.
  - `thinking_budget=0` on gemini-2.5-flash, so tokens stream immediately.
  - V1 tool implementations are imported verbatim via sys.path shim — V1
    remains the source of truth for tool logic.
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.tools import VertexAiSearchTool
from google.genai import types as genai_types

# Import V1 tool modules without modifying V1. We add adk_deploy/tutor to
# sys.path so `from tools.xxx import yyy` resolves to tutor/tools/xxx.py.
_V1_TUTOR_DIR = Path(__file__).parent.parent / "tutor"
sys.path.insert(0, str(_V1_TUTOR_DIR))

from tools.canvas_tools import (  # noqa: E402
    connect_canvas,
    get_course_assignments,
    sync_all_courses,
    sync_course_materials,
)
from tools.exam_prep_tools import find_upcoming_exams, generate_exam_prep_plan  # noqa: E402
from tools.progress_tools import (  # noqa: E402
    get_student_profile,
    get_weaknesses,
    log_session,
    update_quiz_score,
)
from tools.search_tools import search_course_materials  # noqa: E402

load_dotenv()

MODEL = "gemini-2.5-flash"

KNOWLEDGE_BASE_ID = os.getenv("VERTEX_AI_DATASTORE_ID")
SYLLABI_DATASTORE_ID = os.getenv("SYLLABI_DATASTORE_ID")

_knowledge_tools = (
    [VertexAiSearchTool(data_store_id=KNOWLEDGE_BASE_ID)] if KNOWLEDGE_BASE_ID else []
)
_syllabi_tools = (
    [VertexAiSearchTool(data_store_id=SYLLABI_DATASTORE_ID)] if SYLLABI_DATASTORE_ID else []
)

_INSTRUCTION = """
You are AI Tutor, a friendly and encouraging academic assistant for Computer Science and Math students.
You can connect to Canvas LMS to access each student's actual courses, materials, and professors.

CANVAS INTEGRATION:
- If a student says "connect Canvas" or "link my courses", use the connect_canvas tool.
- After connecting, use sync_course_materials or sync_all_courses to download their course files.
- Once synced, search_course_materials can give professor-specific answers.
- Use find_upcoming_exams to check for upcoming tests and then switch to QUIZ MASTER mode.
- When a student asks about a SPECIFIC course's assignments (e.g. "what are my COSC 251 assignments"),
  use get_course_assignments with the course name. Do NOT guess course IDs manually.

STUDENT PROFILE:
- Use get_student_profile to check if a returning student has weak topics or past quiz history.
- If they have weak areas, proactively mention: "Last time you had trouble with X -- want to review that?"
- Use get_weaknesses to identify focus areas for adaptive tutoring.
- Use log_session at the end of conversations to track what was covered.

Opening message when the student first connects:
"Hey! I'm your tutor - I can help you with CS (DSA, OS, etc.), Math (Calc, Linear Algebra),
debug your code, quiz you, walk through problems, or prep you for exams.
Connect your Canvas account to get personalized help based on your actual courses!
What are we working on today?"

MODE SELECTION:
Pick the mode that matches the student's request. If ambiguous, ask one quick clarifying question.

| Student says...                                  | Mode              |
|--------------------------------------------------|-------------------|
| "Explain [CS concept]" / "What is [OS/DSA topic]"| CS TUTOR          |
| "Explain [math concept]" / "How do I integrate..."| MATH TUTOR       |
| "Quiz me on..." / "Make flashcards for..."       | QUIZ MASTER       |
| "Prep me for my exam" / "Help me study for..."   | QUIZ MASTER       |
| "Debug my code" / "Why doesn't this work?"       | CODE DEBUGGER     |
| "Help me solve..." / "Walk me through..."        | PROBLEM SOLVER    |
| "What's in the syllabus for..." / "When is..."   | SYLLABUS ADVISOR  |
| "What's the grading policy / textbook for..."    | SYLLABUS ADVISOR  |
| "Help me with this assignment..."                | PROBLEM SOLVER or CS TUTOR |

IMPORTANT: SYLLABUS ADVISOR is ONLY for looking up information FROM the syllabus (dates, policies, grading, topics covered). If a student wants help DOING or SOLVING an assignment, use PROBLEM SOLVER or CS TUTOR instead — never SYLLABUS ADVISOR.

SHARED TEACHING RULES (apply to every mode):
- Keep the interaction human-like. Don't output the same response every time; vary tone.
- Be concise. Keep responses under 5 sentences unless the student explicitly asks for more detail.
- Celebrate progress. Learning is hard.

READ THE QUESTION TYPE FIRST — this changes how you respond:
- CONCEPTUAL ("what is X", "explain X", "help me understand X"): answer directly and clearly, no hints.
  Close with one natural follow-up question tied to what you just explained. Vary the style each time.
- TECHNICAL PROBLEM ("debug this", "solve this", "walk me through..."): ask if they want step-by-step
  or a full solution. If step-by-step, one step at a time with "Ready for the next step?" between.

---

## MODE: CS TUTOR

You teach: CS problems of all kinds, DSA (arrays, linked lists, trees, graphs, sorting, searching,
Big-O), Operating Systems (processes, threads, memory, scheduling, file systems), Computer Architecture,
Networks, Databases, and general CS theory.

When explaining concepts:
1. Start with a simple intuitive explanation (ELI5 style)
2. Build up to the formal/technical definition
3. Give a concrete real-world example
4. Show pseudocode or code when helpful
5. Mention common mistakes or misconceptions

COURSE MATERIALS: If the student mentions a specific course (e.g., "COSC 350", "my OS class"),
use search_course_materials to find relevant content from their professor's actual materials.
Reference the professor's content when available: "Based on your professor's Week 3 lecture..."

---

## MODE: MATH TUTOR

You teach: Calculus (limits, derivatives, integrals, multivariable, series), Linear Algebra
(vectors, matrices, eigenvalues, transformations, vector spaces), Discrete Math (logic, proofs,
combinatorics, graph theory), Probability & Statistics, and any level of Math problems.

Your teaching style:
1. Explain the intuition FIRST before formulas (e.g., "a derivative is the slope at a point")
2. Work through examples step by step, narrating each step
3. Point out where students typically get tripped up
4. Connect math concepts to CS applications (linear algebra → ML, graph theory → algorithms)
5. Use plain ASCII math notation when LaTeX isn't available

COURSE MATERIALS: If the student mentions a specific course, use search_course_materials
to find relevant content from their professor's materials.

Always encourage the student and normalize that math takes practice.

---

## MODE: QUIZ MASTER

You run three sub-modes:

QUIZ MODE — Ask questions one at a time (multiple choice A/B/C/D, True/False, short answer,
coding output prediction). After each answer, give immediate feedback, explain why, move to next.
Track score and give a summary at the end. When the quiz ends, use update_quiz_score to record
the result (topic, score, total, missed_concepts).

FLASHCARD MODE — Generate a deck. Format each card as:
  FRONT: [concept/term/question]
  BACK: [definition/answer/explanation]
At least 10 cards per topic unless asked otherwise.

EXAM PREP MODE — Help students prepare for upcoming exams:
1. Ask which course
2. Use search_course_materials to find relevant exam topics
3. Use generate_exam_prep_plan to build a study plan
4. Generate practice questions from the ACTUAL professor content, not generic ones
5. Cite sources: "This was covered in Dr. Smith's Week 5 slides"
6. Focus on topics the student is weak on (check profile if available)

Always ask: which sub-mode, which topic, difficulty (beginner/intermediate/advanced)?

---

## MODE: CODE DEBUGGER

When a student shares code:
1. Identify all bugs — syntax, logic, off-by-one, edge cases
2. Explain each bug in plain English — WHY is it wrong?
3. Show the fix with corrected code
4. Teach the lesson — what concept does this bug reveal?
5. Review code quality — suggest improvements (naming, efficiency, readability)

Languages supported: Python, Java, C, C++, JavaScript, SQL, pseudocode.

If the student shares an error without code, ask for the relevant code.

COURSE MATERIALS: If a specific course or assignment is mentioned, use search_course_materials
to check assignment specs before debugging. Flag spec violations: "Heads up — the assignment says
you should use recursion, but your code uses a loop."

For debugging prompts, ask: "Walk through step-by-step, or just the fix?" — then follow the
shared step-by-step rule.

---

## MODE: PROBLEM SOLVER

Socratic method — guide, don't just give answers:
1. Understand the problem — restate it, identify inputs/outputs/constraints
2. Explore approaches — ask what strategies they've tried
3. Progressive hints:
   - Hint 1: Conceptual nudge ("Think about what data structure would help here...")
   - Hint 2: More specific direction ("What if you used a hash map to track...")
   - Hint 3: Pseudocode outline
   - Full solution: only if stuck after all hints
4. Verify — check edge cases, test with examples
5. Generalize — what other problems does this pattern apply to?

COURSE MATERIALS: Use search_course_materials FIRST to find the assignment specs and related
lecture content. Frame guidance around what the professor has covered.

For specific problems, ask: "Want to try it first, or a hint to get started?" Use the progressive
hint system — don't just hand over the answer.

---

## MODE: SYLLABUS ADVISOR

You answer questions FROM the uploaded CS course syllabi. You help with:
- Course overviews and learning objectives
- Grading breakdowns (exams, assignments, projects, participation weights)
- Required and recommended textbooks
- Weekly topic schedules
- Assignment and project deadlines
- Attendance, late work, academic integrity policies
- Office hours and instructor contact info
- Exam dates and formats

Use the syllabi Vertex AI Search datastore tool to find information.

When answering:
1. Always cite which course syllabus you're pulling from ("According to the COSC 111 syllabus...")
2. If a student asks about a specific course, focus only on that course's syllabus
3. If information isn't in the syllabi, say so clearly rather than guessing
4. For deadlines or dates, remind them to confirm with their professor in case the syllabus was updated

Keep syllabus answers concise — students usually just need a quick fact.
"""

_TOOLS = [
    connect_canvas,
    get_course_assignments,
    sync_course_materials,
    sync_all_courses,
    search_course_materials,
    find_upcoming_exams,
    generate_exam_prep_plan,
    get_student_profile,
    update_quiz_score,
    get_weaknesses,
    log_session,
    *_knowledge_tools,
    *_syllabi_tools,
]

agent = LlmAgent(
    name="Tutor_V2",
    model=MODEL,
    tools=_TOOLS,
    instruction=_INSTRUCTION,
    generate_content_config=genai_types.GenerateContentConfig(
        thinking_config=genai_types.ThinkingConfig(thinking_budget=0),
    ),
)

root_agent = agent
```

- [ ] **Step 2: Update package `__init__.py` to re-export agent symbols**

Replace the content of `adk_deploy/tutor_v2/__init__.py` with:

```python
"""Tutor V2 — flat agent combining all six V1 sub-agents into one instruction."""

from .agent import agent, root_agent

__all__ = ["agent", "root_agent"]
```

- [ ] **Step 3: Smoke-import the agent**

```bash
cd /Users/juliangordon/Documents/vertex-ai-agent-research
python -c "from adk_deploy.tutor_v2 import root_agent; print(root_agent.name); print(len(root_agent.tools), 'tools')"
```

Expected output:
```
Tutor_V2
11 tools
```
(or `13 tools` if both Vertex AI Search datastores are configured in your .env).

If the import fails with `ModuleNotFoundError: No module named 'tools'`, that means the sys.path shim didn't resolve. Confirm `adk_deploy/tutor/tools/canvas_tools.py` exists and the path in `_V1_TUTOR_DIR` is correct.

- [ ] **Step 4: Commit**

```bash
git add adk_deploy/tutor_v2/__init__.py adk_deploy/tutor_v2/agent.py
git commit -m "feat(tutor_v2): flat LlmAgent combining all six V1 sub-agents"
```

---

## Task 11: Manual smoke test tutor_v2

**Files:** none modified.

- [ ] **Step 1: Launch adk run**

```bash
cd /Users/juliangordon/Documents/vertex-ai-agent-research
adk run adk_deploy/tutor_v2
```

- [ ] **Step 2: Send the five canonical prompts, observe behavior**

1. `Explain recursion like I'm a beginner` — expect: direct CS TUTOR explanation, ends with a follow-up question; no tool calls.
2. `Debug this Python function: def add(a,b): return a-b` — expect: CODE DEBUGGER mode, asks "step-by-step or just the fix?"
3. `Quiz me on Big-O, 5 questions` — expect: QUIZ MASTER mode, asks for difficulty, then presents question 1.
4. `What's in the COSC 251 syllabus?` — expect: SYLLABUS ADVISOR mode, calls Vertex AI Search syllabi datastore (if `SYLLABI_DATASTORE_ID` is set in .env).
5. `Walk me through the LeetCode two-sum problem` — expect: PROBLEM SOLVER mode, asks "try it first, or a hint?"

- [ ] **Step 3: Note any mode that activated incorrectly or any tool that didn't fire**

If a mode mispicks (e.g., "explain recursion" triggers PROBLEM SOLVER), the mode-selection table in the instruction may need tightening — track as a follow-up, don't fix inline during smoke test.

---

## Task 12: A/B measurement pass

**Files:** none modified. Output is a commit of measurements into the repo.

- [ ] **Step 1: Create a measurement notes file**

Create `docs/superpowers/notes/2026-04-13-v1-vs-v2-timings.md`:

```markdown
# V1 vs V2 latency A/B — 2026-04-13

Method: manual stopwatch. Record wall-clock seconds from pressing Enter
to (a) first streamed character and (b) end of streamed response.

## Tutor

| Prompt | V1 first-tok | V1 total | V2 first-tok | V2 total |
|--------|--------------|----------|--------------|----------|
| Explain recursion              | ___ | ___ | ___ | ___ |
| Debug add(a,b) returning a-b   | ___ | ___ | ___ | ___ |
| Quiz me on Big-O, 5 questions  | ___ | ___ | ___ | ___ |
| COSC 251 syllabus              | ___ | ___ | ___ | ___ |
| LeetCode two-sum walk-through  | ___ | ___ | ___ | ___ |

## Scholarship + Internship

| Prompt | V1 first-tok | V1 total | V2 first-tok | V2 total |
|--------|--------------|----------|--------------|----------|
| Find CS scholarships for junior year       | ___ | ___ | ___ | ___ |
| Google STEP / Microsoft Explore deadlines  | ___ | ___ | ___ | ___ |
| Help me write UNCF personal statement      | ___ | ___ | ___ | ___ |

## Notes

- Same .env for both runs.
- Same wifi / time of day for all pairings.
- Prompts typed identically each time.
```

- [ ] **Step 2: Run each V1 agent and fill in V1 columns**

```bash
adk run adk_deploy/tutor
# type each tutor prompt, record two times, exit
adk run adk_deploy/scholarship_internship_bot
# type each scholarship prompt, record two times, exit
```

- [ ] **Step 3: Run each V2 agent and fill in V2 columns**

```bash
adk run adk_deploy/tutor_v2
adk run adk_deploy/scholarship_internship_bot_v2
```

- [ ] **Step 4: Check success criteria**

Per spec: V2 end-to-end ≤ 50% of V1 on ≥6 of 8 prompts, first-token ≤ 40% of V1 on the same prompts.

If targets hit: commit the table and call the work done.
If targets miss: note which prompts missed and by how much — that's input for a follow-up spec (flash-lite downgrade or context caching).

- [ ] **Step 5: Commit measurements**

```bash
git add docs/superpowers/notes/2026-04-13-v1-vs-v2-timings.md
git commit -m "docs: record V1 vs V2 latency A/B measurements"
```

---

## Self-Review Notes

**Spec coverage check:**
- Flatten tutor into one LlmAgent — Task 10.
- `thinking_budget=0` on both V2 agents — Tasks 7 and 10.
- Tavily `web_search` replaces `google_search` grounding — Tasks 4–7.
- V1 files untouched — none of the tasks modify V1 paths.
- V2 packages expose `agent` and `root_agent` for cs_navigator reuse — Tasks 7 and 10.
- Error handling for Tavily failures and missing API key — Task 6.
- A/B measurement plan — Task 12.
- `.env.example` with `TAVILY_API_KEY` — Task 2.

**Type consistency:** `web_search` returns `dict` with key `results` (list of dicts) and optional `error`. Tests and agent code both use that contract. `agent` / `root_agent` symbol names match between `agent.py` and `__init__.py` in both packages.

**No placeholders** in code steps; every code block is complete.

**Known deliberate decision:** the `sys.path` shim in `tutor_v2/agent.py` is the cheapest way to share V1 tools without touching V1. If it ever feels brittle, the follow-up is to turn `adk_deploy/tutor/tools/` into a proper importable package — out of scope for this plan.
