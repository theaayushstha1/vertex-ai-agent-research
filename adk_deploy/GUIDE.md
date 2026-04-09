# The Complete Guide: CS Navigator + Tutor + Scholarship Bot

This doc explains everything that's happening across the three pieces of this project, how they connect, and what your code actually does. Read this before touching the cs-navigator integration.

---

## Table of Contents

1. [The Big Picture](#the-big-picture)
2. [The Three Pieces](#the-three-pieces)
3. [How Google ADK Works](#how-google-adk-works)
4. [CS Navigator (the main app)](#cs-navigator-the-main-app)
5. [The Standalone Tutor Bot](#the-standalone-tutor-bot)
6. [The Standalone Scholarship Bot](#the-standalone-scholarship-bot)
7. [The Integration (what we just built)](#the-integration-what-we-just-built)
8. [How Data Flows End-to-End](#how-data-flows-end-to-end)
9. [The File Map](#the-file-map)
10. [Environment Variables](#environment-variables)
11. [Running Everything Locally](#running-everything-locally)
12. [The GitHub Situation](#the-github-situation)
13. [Glossary](#glossary)

---

## The Big Picture

You're building an AI assistant for Morgan State CS students. It does three things:

1. **Academic advising** -- "What courses do I need?" "Who is my advisor?" (CS Navigator)
2. **Tutoring** -- "Explain binary heaps" "Debug my code" "Quiz me on sorting" (Tutor)
3. **Scholarship/internship search** -- "Find scholarships for CS majors" (Scholarship Bot)

Originally these were three separate projects. Now they're being merged into one -- the Tutor and Scholarship Bot become **sub-agents** inside CS Navigator, so students get everything in one chat.

---

## The Three Pieces

### Where they live on your machine

```
vertex-ai-agent-research/
    adk_deploy/                        <-- YOUR repo (this folder)
        tutor/                         <-- Standalone tutor (DEPRECATED)
        scholarship_internship_bot/    <-- Standalone scholarship bot (DEPRECATED)
        .env.example                   <-- Environment variables template
        GUIDE.md                       <-- This file

    cs-chatbot-morganstate/            <-- YOUR TEAMMATE'S repo (cloned)
        frontend/                      <-- React web app (cs.inavigator.ai)
        backend/                       <-- FastAPI server (api.inavigator.ai)
        adk_agent/                     <-- Google ADK agent code
            cs_navigator_unified/      <-- The main agent
                agent.py               <-- Root agent definition
                sub_agents/            <-- NEW: your tutor + scholarship
                tools/                 <-- NEW: your tools (integrated)
```

### Who owns what

- **cs-chatbot-morganstate** -- Your teammate Aayush's repo. This is the production app at cs.inavigator.ai. You cloned it locally and made changes on a branch called `feat/tutor-scholarship-integration`.
- **adk_deploy** (this folder) -- Your repo. Contains the original standalone bots you built, plus earlier agent experiments. The standalone bots here are now deprecated because they've been integrated into cs-navigator.

---

## How Google ADK Works

Google ADK (Agent Development Kit) is Google's framework for building AI agents. Here's what you need to know:

### What's an agent?

An agent is just an AI with a specific job description (called an "instruction") and a set of tools it can use. In code:

```python
from google.adk.agents import LlmAgent

my_agent = LlmAgent(
    name="My_Agent",
    model="gemini-2.5-flash",         # Which AI model to use
    instruction="You are a helpful assistant that...",  # The job description
    tools=[some_function, another_function],            # Python functions it can call
)
```

When a student sends a message, Gemini reads the instruction, looks at the available tools, and decides how to respond. If it needs data (like the student's courses), it calls one of the tools.

### What's a sub-agent?

A sub-agent is an agent that lives inside another agent. The parent agent can **delegate** to sub-agents when a question matches their specialty.

```python
root_agent = LlmAgent(
    name="CS_Navigator",
    sub_agents=[tutor_agent, scholarship_agent],  # These are sub-agents
    instruction="...route tutoring questions to Tutor, scholarship questions to Scholarship_Agent..."
)
```

When a student asks "explain binary search", CS Navigator sees the routing rules in its instruction and hands the question to the Tutor sub-agent. The Tutor then handles it (or delegates further to CS_Tutor, Math_Tutor, etc.).

### What's a tool?

A tool is a regular Python function that the agent can call. You write a function, give it a docstring, and ADK automatically lets the AI call it when needed.

```python
def get_current_date() -> dict:
    """Get today's date."""
    return {"date": "2026-04-08"}
```

The agent sees the function name and docstring, and decides when to use it. The docstring is important because that's how the AI knows what the tool does.

### What's session state?

ADK keeps a "state" dict for each conversation session. The backend can inject data into this state before the agent sees the message. For example:

```python
state = {
    "degreeworks": "GPA: 3.4, Major: CS, ...",     # Student's academic record
    "canvas": "COSC 251: 89%, assignment due Apr 10...",  # Current grades
    "tutor_progress": "Weak topics: sorting...",     # Quiz history
}
```

The agent's instruction function reads this state and includes it in the prompt. So when a student asks "what's my GPA?", the agent already has the answer in its context.

### How ADK runs locally

When you run `adk web cs_navigator_unified`, ADK starts a web server (default port 8000) with a chat UI. Behind the scenes:

1. Student types a message
2. ADK creates a session (or reuses an existing one)
3. ADK sends the message + instruction + state to Gemini
4. Gemini responds (possibly calling tools along the way)
5. ADK streams the response back to the chat UI

In production, cs-navigator doesn't use `adk web`. Instead, the FastAPI backend sends messages to ADK's `/run_sse` endpoint programmatically.

---

## CS Navigator (the main app)

This is the production system at **cs.inavigator.ai**. It has three parts:

### Frontend (React)

A web app where students log in, chat with the AI, sync their Canvas/DegreeWorks data, and view their grades. Lives in `cs-chatbot-morganstate/frontend/`.

Key files:
- `Chat.jsx` -- The main chat interface
- `Login.jsx` / `SignUp.jsx` -- Authentication

### Backend (FastAPI)

A Python API server that handles authentication, data storage, Canvas sync, and talks to the ADK agent. Lives in `cs-chatbot-morganstate/backend/`.

Key things it does:
- **User auth** -- JWT-based login/signup (`/api/login`, `/api/register`)
- **DegreeWorks sync** -- Parses student academic records (`/api/degreeworks/sync`)
- **Canvas sync** -- Logs into Canvas via LDAP per student, fetches courses/grades/assignments (`/api/canvas/sync`)
- **Chat** -- Takes the student's message, fetches their DW/Canvas/memory data from the DB, injects it into ADK session state, and forwards the message to the ADK agent (`/chat`, `/chat/stream`)
- **New endpoints we added:**
  - `/api/tutor/progress/{user_id}` -- Gets a student's tutor quiz/progress data from Firestore
  - `/api/canvas/sync-materials` -- Syncs a Canvas course's files to Google Cloud Storage for the tutor to search

Key files:
- `main.py` -- All the API endpoints (~3000 lines)
- `vertex_agent.py` -- Talks to the ADK agent (sends messages, manages sessions)
- `models.py` -- Database models (User, DegreeWorksData, CanvasStudentData, etc.)
- `canvas_client.py` -- Canvas LDAP auth + data fetching
- `services/context_builders.py` -- Builds text context strings from DB data for injection into the agent
- `services/tutor_progress.py` -- Reads quiz/progress data from Firestore (NEW)
- `services/material_sync.py` -- Downloads Canvas files to GCS + creates search datastores (NEW)

### ADK Agent

The AI brain. Lives in `cs-chatbot-morganstate/adk_agent/cs_navigator_unified/`.

**Before our changes:** One single agent (`CS_Navigator`) with a knowledge base tool. It answers all questions itself using Vertex AI Search to look up info from 44+ uploaded documents (course catalogs, faculty info, policies, etc.).

**After our changes:** Same root agent, but now it has two sub-agents:
- `Tutor` -- Routes to 6 specialist sub-agents (CS_Tutor, Math_Tutor, Quiz_Master, Code_Debugger, Problem_Solver, Syllabus_Advisor)
- `Scholarship_Agent` -- Searches for scholarships/internships using Google Search, filters by the student's GPA/major/year

The root agent's instruction includes routing rules that tell it when to delegate vs handle directly.

---

## The Standalone Tutor Bot

**Location:** `adk_deploy/tutor/`
**Status:** DEPRECATED (integrated into cs-navigator)

This is the tutor you originally built as a standalone ADK agent. You'd run it with `adk web tutor` and it had its own chat UI.

### What it does

6 sub-agents, each specialized:

| Agent | Handles |
|-------|---------|
| CS_Tutor | DSA, OS, architecture, CS theory |
| Math_Tutor | Calc, linear algebra, discrete math |
| Quiz_Master | Quizzes, flashcards, exam prep |
| Code_Debugger | Bug finding, code review |
| Problem_Solver | Step-by-step problem walkthroughs |
| Syllabus_Advisor | Syllabus lookups (grading, dates, policies) |

A root `Tutor` agent routes questions to the right specialist.

### What's wrong with the standalone version

1. **Shared Canvas token** -- One `CANVAS_API_TOKEN` env var for everyone. Every student sees the same Canvas account's data. This is the tenant-isolation issue Codex flagged.
2. **Unprotected Firestore access** -- Progress tools take `canvas_user_id` as a free parameter. Any user ID works, no auth check.
3. **Shared course cache** -- A module-global dict that bleeds between sessions.

### What changed in the integration

All of these problems go away because:
- Canvas data is fetched by the backend per-user (LDAP auth) and injected into session state. The tutor never touches Canvas directly.
- The user ID comes from JWT auth in the backend, not from the model.
- No global caches -- each session has its own state.

---

## The Standalone Scholarship Bot

**Location:** `adk_deploy/scholarship_internship_bot/`
**Status:** DEPRECATED (integrated into cs-navigator)

A single agent with Google Search + deadline checking tools. Searches for scholarships and internships, filters by the student's profile (GPA, major, year), and checks if deadlines have passed.

### Tools

- `get_current_date()` -- Returns today's date + current semester
- `check_deadline(deadline_date)` -- Checks if a deadline is expired/today/urgent/upcoming/open
- `google_search` -- Built-in ADK tool for live web search

### Bug we fixed

`check_deadline` compared `datetime` objects instead of `date` objects. On deadline day, any time after midnight made the deadline look expired. Fixed by comparing `.date()` values so the full deadline day counts as valid.

---

## The Integration (what we just built)

Here's what the 12 commits on `feat/tutor-scholarship-integration` actually do:

### Phase 1: Backend (commits 1-5)

We added backend infrastructure so the tutor can access student data through cs-navigator's auth system:

1. **Firestore tutor progress service** (`backend/services/tutor_progress.py`) -- Reads a student's quiz history and weak/strong topics from Firestore. This is what powers "Last time you had trouble with sorting -- want to review that?"

2. **Material sync service** (`backend/services/material_sync.py`) -- Downloads files from a Canvas course to Google Cloud Storage, then creates a Vertex AI Search datastore so the tutor can search the professor's actual lecture notes/slides.

3. **CourseMaterialMapping model** -- A new DB table that tracks which courses have been synced and their datastore IDs.

4. **build_tutor_context()** -- A function that turns the raw Firestore progress data into a text string the agent can read.

5. **Two new API endpoints:**
   - `GET /api/tutor/progress/{user_id}` -- Returns progress data
   - `POST /api/canvas/sync-materials` -- Triggers a course file sync

6. **Tutor progress injection** -- Both `/chat` and `/chat/stream` now fetch tutor progress in parallel with DW/Canvas/memory data, build the context string, and pass it to the ADK agent via `state_delta`.

### Phase 2: Agent code (commits 6-10)

We ported the tutor and scholarship agents into cs-navigator's agent structure:

7. **Tools package** (`adk_agent/.../tools/`) -- `material_search.py`, `material_sync.py`, `progress.py`, `deadline.py`. These are cleaned-up versions of the standalone tools. The key difference: `material_sync` calls the backend API instead of hitting Canvas directly.

8. **6 tutor sub-agents** -- Ported from standalone, each in its own file under `sub_agents/tutor/`.

9. **Tutor orchestrator** (`sub_agents/tutor/orchestrator.py`) -- The routing agent that delegates to the 6 specialists.

10. **Scholarship agent** (`sub_agents/scholarship/agent.py`) -- Ported from standalone, reads DegreeWorks data from session state for auto-filtering.

11. **Root agent wiring** -- Added `sub_agents=[tutor_agent, scholarship_agent]` to the root CS_Navigator agent, plus routing rules in the instruction telling it when to delegate.

### Phase 3: Bug fixes (commits 11-12)

12. **Deadline date comparison** -- Fixed in both standalone and integrated versions.
13. **Assignment date filtering** -- Context builder now filters out past-due assignments so "what's my next assignment" doesn't show old ones.

---

## How Data Flows End-to-End

Here's what happens when a student asks "explain binary search trees":

```
Student types message in browser (cs.inavigator.ai)
    |
    v
Frontend sends POST /chat/stream with JWT token
    |
    v
Backend authenticates user via JWT
    |
    v
Backend fetches in parallel:
    - DegreeWorks data (from PostgreSQL)
    - Chat history (from PostgreSQL)
    - Long-term memory (from PostgreSQL)
    - Tutor progress (from Firestore)    <-- NEW
    - Canvas data (from PostgreSQL, if needed)
    |
    v
Backend builds context strings:
    - student_context = "GPA: 3.4, Major: CS, ..."
    - canvas_context = "COSC 251: 89%, ..."
    - memory_context = "Student prefers step-by-step..."
    - tutor_context = "Weak topics: sorting..."    <-- NEW
    |
    v
Backend sends to ADK agent via /run_sse:
    {
        message: "explain binary search trees",
        state_delta: {
            degreeworks: student_context,
            canvas: canvas_context,
            memory: memory_context,
            tutor_progress: tutor_context    <-- NEW
        }
    }
    |
    v
ADK agent (CS_Navigator) reads the message
    - Sees "explain" -> matches tutoring routing rule
    - Delegates to Tutor sub-agent
    |
    v
Tutor sub-agent reads the message
    - Sees "explain [CS concept]" -> routes to CS_Tutor
    |
    v
CS_Tutor generates a response using Gemini
    - Uses its instruction (ELI5 style, follow-up question, etc.)
    - May call search_course_materials if student mentioned a course
    |
    v
Response streams back: ADK -> Backend -> Frontend -> Student
```

For scholarship queries, the flow is the same except CS_Navigator routes to Scholarship_Agent instead of Tutor. The Scholarship_Agent uses `google_search` to find opportunities and `check_deadline` to filter expired ones.

---

## The File Map

### What we added/changed in cs-navigator

```
cs-chatbot-morganstate/
    backend/
        main.py                              # MODIFIED: +2 endpoints, +tutor progress fetch in chat
        vertex_agent.py                      # MODIFIED: +tutor_context param in all query functions
        models.py                            # MODIFIED: +CourseMaterialMapping table
        requirements.txt                     # MODIFIED: +google-cloud-firestore
        services/
            context_builders.py              # MODIFIED: +build_tutor_context(), fix assignment filtering
            tutor_progress.py                # NEW: reads from Firestore
            material_sync.py                 # NEW: Canvas files -> GCS -> Discovery Engine

    adk_agent/cs_navigator_unified/
        agent.py                             # MODIFIED: +sub_agent imports, +routing rules, +tutor_progress in instruction
        sub_agents/
            __init__.py                      # NEW
            tutor/
                __init__.py                  # NEW
                orchestrator.py              # NEW: routes to 6 specialists
                cs_tutor.py                  # NEW
                math_tutor.py                # NEW
                quiz_master.py               # NEW
                code_debugger.py             # NEW
                problem_solver.py            # NEW
                syllabus_advisor.py          # NEW
            scholarship/
                __init__.py                  # NEW
                agent.py                     # NEW
        tools/
            __init__.py                      # NEW
            material_search.py               # NEW: Discovery Engine search
            material_sync.py                 # NEW: calls backend API
            progress.py                      # NEW: Firestore quiz tracking
            deadline.py                      # NEW: date/deadline utils
```

### What's in adk_deploy (your repo)

```
adk_deploy/
    tutor/                          # DEPRECATED standalone tutor
        agent.py                    # Root agent + 6 sub-agents (all in one file)
        canvas/                     # DEPRECATED: direct Canvas API access
            client.py               # HTTP client for Canvas REST API
            sync.py                 # File download + GCS upload
            datastore.py            # Vertex AI Search datastore creation
            mapping.py              # Course-to-datastore mapping
        tools/
            canvas_tools.py         # DEPRECATED: shared token, global cache
            progress_tools.py       # DEPRECATED: unprotected Firestore access
            search_tools.py         # Discovery Engine search (still valid)
            exam_prep_tools.py      # Exam prep plan generation
        student/
            profile.py              # Firestore student profile CRUD
            tracker.py              # Mastery analysis from quiz history

    scholarship_internship_bot/
        agent.py                    # Single agent + tools (deadline fixed)

    .env.example                    # Environment variables template
    GUIDE.md                        # This file
```

---

## Environment Variables

Copy `.env.example` to `.env` in this folder:

```bash
cp .env.example .env
```

| Variable | What it's for | Where to get it |
|----------|--------------|-----------------|
| `GOOGLE_CLOUD_PROJECT` | Your GCP project ID | Google Cloud Console top bar |
| `AGENT_MODEL` | Which Gemini model to use | Default: `gemini-2.5-flash` |
| `VERTEX_AI_DATASTORE_ID` | Knowledge base for tutoring | Vertex AI Agent Builder > Data Stores |
| `SYLLABI_DATASTORE_ID` | Syllabi datastore for Syllabus Advisor | Same place |
| `CANVAS_API_TOKEN` | Canvas PAT (standalone only, deprecated) | Canvas > Settings > New Access Token |
| `BACKEND_URL` | cs-navigator backend URL | Default: `http://127.0.0.1:5000` |

The cs-navigator backend has its own `.env` in `cs-chatbot-morganstate/backend/.env` with database credentials, JWT secrets, etc. That's Aayush's config -- you don't need to set it up yourself unless you're running the full backend locally.

---

## Running Everything Locally

### Option 1: Just the standalone bots (for testing/development)

```bash
# Make sure you're authenticated with Google Cloud
gcloud auth application-default login

# Copy and fill in your .env
cp .env.example .env
# Edit .env with your values

# Run the tutor
cd adk_deploy
adk web tutor

# Or run the scholarship bot
adk web scholarship_internship_bot
```

Opens a chat UI at http://127.0.0.1:8000. Note: the standalone tutor's Canvas features use the shared token (deprecated).

### Option 2: The integrated version (cs-navigator)

This requires the full cs-navigator stack:

```bash
# 1. Start the backend (needs its own .env with DB creds)
cd cs-chatbot-morganstate/backend
python main.py

# 2. Start the ADK agent
cd cs-chatbot-morganstate/adk_agent
adk web cs_navigator_unified

# 3. Start the frontend
cd cs-chatbot-morganstate/frontend
npm run dev
```

Or just test the agent directly without the backend:

```bash
cd cs-chatbot-morganstate/adk_agent
adk web cs_navigator_unified
# Opens chat at http://127.0.0.1:8000
# Note: without the backend, no Canvas/DW data will be injected
```

---

## The GitHub Situation

There are two repos involved:

1. **Your repo** (`vertex-ai-agent-research` / `adk_deploy`) -- Where the standalone bots live. You have full push access.

2. **Aayush's repo** (`theaayushstha1/cs-chatbot-morganstate`) -- Where cs-navigator lives. You cloned it and made changes on a local branch (`feat/tutor-scholarship-integration`), but you don't have push access.

### To get your changes into cs-navigator:

**Option A: Fork and PR**
1. Fork `theaayushstha1/cs-chatbot-morganstate` on GitHub
2. Add your fork as a remote: `git remote add myfork https://github.com/YOUR_USERNAME/cs-chatbot-morganstate.git`
3. Push your branch: `git push -u myfork feat/tutor-scholarship-integration`
4. Open a PR from your fork to Aayush's repo

**Option B: Get collaborator access**
1. Ask Aayush to add you as a collaborator on his repo
2. Then push directly: `git push -u origin feat/tutor-scholarship-integration`

### Before merging, Aayush needs to:

1. **Enable Firestore** in the GCP project (`csnavigator-vertex-ai`) -- the tutor progress features need it
2. **Create the `students` collection** in Firestore (or it auto-creates on first write)
3. **Review the PR** -- 12 commits, ~30 files changed

---

## Glossary

| Term | What it means |
|------|--------------|
| **ADK** | Agent Development Kit -- Google's framework for building AI agents |
| **LlmAgent** | The main class in ADK. An AI with an instruction and tools. |
| **Sub-agent** | An agent nested inside another agent. Parent delegates to it. |
| **Tool** | A Python function the agent can call (search, save data, etc.) |
| **Session state** | Per-conversation dict where the backend injects student data |
| **state_delta** | Data sent with each message to update session state (volatile) |
| **Vertex AI Search** | Google's search engine for custom document collections |
| **Discovery Engine** | The API behind Vertex AI Search (same thing, different name) |
| **Datastore** | A collection of documents in Vertex AI Search |
| **Firestore** | Google's NoSQL database (stores tutor quiz/progress data) |
| **GCS** | Google Cloud Storage (where synced Canvas files go) |
| **DegreeWorks** | Morgan State's degree audit system (tracks academic progress) |
| **Canvas LMS** | The learning management system (courses, grades, assignments) |
| **LDAP** | How Canvas authenticates Morgan State students (username + password) |
| **JWT** | JSON Web Token -- how cs-navigator authenticates users |
| **PAT** | Personal Access Token -- a Canvas API key tied to one account |
| **SSE** | Server-Sent Events -- how streaming responses work |
| **FastAPI** | Python web framework the backend uses |
| **Gemini** | Google's AI model (like GPT but from Google) |
