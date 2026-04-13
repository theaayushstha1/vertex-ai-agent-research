# Tutor V2 + Scholarship V2 — Speed Architecture Design

**Date:** 2026-04-13
**Status:** Draft for review
**Author:** Julian + Claude

## Problem

The current `adk_deploy/tutor/` and `adk_deploy/scholarship_internship_bot/` agents feel slow when run locally via `adk run` / `adk web`. Both first-token latency and tool-heavy query latency are noticeable. Root causes:

1. **Tutor** uses a root `LlmAgent` that routes to 6 sub-agents. Each user turn requires at minimum 2 LLM round-trips from laptop to Vertex AI (root classifies → sub-agent responds), plus tool calls that go through the sub-agent. Every hop is network latency.
2. Both bots use `gemini-2.5-flash`, which has reasoning / thinking mode on by default. This silently adds 2–5s of hidden reasoning per turn before the first token.
3. **Scholarship** uses `google_search` grounding, which runs search + re-ranking + large context injection server-side. Typical latency: 4–8s before any tokens stream.
4. `google_search` grounding is mutually exclusive with custom function tools on the same agent. This is why scholarship is a separate bot today — it can't coexist with the tutor's function tools.
5. Long instructions are re-sent on every turn; no prompt caching is in use.

## Goals

- Cut end-to-end latency ~2–3x and first-token latency ~3–5x on typical turns.
- Preserve functional behavior: same tools, same knowledge bases, same student experience.
- Keep current agents intact for A/B comparison; ship V2 as parallel files.
- Stay on the ADK so agents remain deployable to Vertex AI Agent Engine.
- **Design V2 agents so they can later be imported into `cs_navigator` as sub-agents or `AgentTool`s without rework** — clean imports, no hidden module-level state, no `root_agent`-only assumptions.

## Non-Goals

- Rewriting or refactoring the current V1 agents.
- Merging into `cs_navigator` (that is a separate, already-planned integration).
- Changing the Canvas integration or Vertex AI Search datastores.
- Caching tool responses beyond what already exists (out of scope for this pass).

## Approach

Flatten the architecture, disable thinking, and replace `google_search` grounding with Tavily as a function tool. Specifically:

1. **Flatten.** One `LlmAgent` per bot. No sub-agents, no `AgentTool` wrapping. The six tutor personalities become labeled sections of a single instruction the model selects from based on question type.
2. **Disable thinking.** Set `thinking_config={"thinking_budget": 0}` on both V2 agents so `gemini-2.5-flash` skips internal reasoning and starts streaming tokens immediately.
3. **Replace grounding with Tavily.** The scholarship V2 agent uses a custom `web_search` function tool backed by the Tavily API. This unblocks colocation with other function tools (relevant for future merges) and drops search latency from 4–8s to 1–2s.
4. **Parallel files only.** V1 stays untouched. V2 lives in `adk_deploy/tutor_v2/` and `adk_deploy/scholarship_internship_bot_v2/`.

### Expected speed wins (rough, per turn)

| Path                         | V1        | V2 target | How                                        |
|------------------------------|-----------|-----------|--------------------------------------------|
| Tutor "explain recursion"    | 6–10s     | 1.5–3s    | No routing hop + no thinking               |
| Tutor code-debug w/ search   | 10–18s    | 4–7s      | Single hop + no thinking + same tools      |
| Scholarship search           | 12–25s    | 4–8s      | Tavily instead of grounding + no thinking  |
| Scholarship chat (no search) | 6–10s     | 1.5–3s    | No thinking, same model                    |

These are estimates based on typical ADK latency profiles, not measurements. Post-implementation we will measure against V1 on the same prompts.

## Architecture

### Tutor V2 (`adk_deploy/tutor_v2/`)

One flat `LlmAgent` with the union of all current tools:

```
tutor_v2 (LlmAgent, gemini-2.5-flash, thinking_budget=0)
├── tools:
│   ├── Canvas: connect_canvas, get_course_assignments,
│   │   sync_course_materials, sync_all_courses
│   ├── Search: search_course_materials (existing wrapper)
│   ├── Exam prep: find_upcoming_exams, generate_exam_prep_plan
│   ├── Progress: get_student_profile, update_quiz_score,
│   │   get_weaknesses, log_session
│   └── Knowledge bases:
│       ├── VertexAiSearchTool(KNOWLEDGE_BASE_ID)
│       └── VertexAiSearchTool(SYLLABI_DATASTORE_ID)
└── instruction: single prompt with six labeled "modes"
    (CS Tutor, Math Tutor, Quiz Master, Code Debugger,
     Problem Solver, Syllabus Advisor) that the model
     selects from based on question type
```

**Instruction structure:**

- Short opening: identity, Canvas integration rules, student profile rules.
- "Mode selection" block: "Pick the mode that matches the question type."
- Six mode sections, each with the teaching approach, tool-use guidance, and tone from the current sub-agent.
- Shared rules (concise, human, follow-up questions on conceptual answers) at the end.

**Personality preservation:** Each mode section keeps its existing tone and teaching rules verbatim (CS Tutor's intuitive → technical → example flow; Math Tutor's intuition-first rule; etc.). The model reads the full instruction each turn but only activates the matching mode.

**Tool coexistence:** All current tools are already function tools, so they fit on one agent. `VertexAiSearchTool` is a function tool, not grounding, so it coexists fine.

### Scholarship V2 (`adk_deploy/scholarship_internship_bot_v2/`)

One flat `LlmAgent` with a custom Tavily-backed web search tool replacing `google_search`:

```
scholarship_v2 (LlmAgent, gemini-2.5-flash, thinking_budget=0)
├── tools:
│   └── web_search (custom function tool, Tavily-backed)
└── instruction: current scholarship prompt, unchanged —
    V1 doesn't reference "google_search" by name; the
    model calls web_search instead of relying on grounding
```

**`web_search` tool contract:**

```
web_search(query: str, max_results: int = 5) -> list[dict]
  returns: [{title, url, snippet, published_date?}, ...]
```

Implementation: wraps `https://api.tavily.com/search` with `include_answer=False`, `search_depth="basic"` (fast tier), `max_results=5` by default. Reads `TAVILY_API_KEY` from env. No key ever committed.

**Instruction preservation:** The current scholarship instruction (deadline filtering rule, three modes, source prioritization, formatting rules) stays verbatim. Only swap out the grounding reference — the model already knows how to call a function tool.

### File layout

```
adk_deploy/
├── tutor/                              # V1 untouched
├── tutor_v2/
│   ├── __init__.py                     # exposes `root_agent` and `agent`
│   └── agent.py                        # flat LlmAgent, imports V1 tools
├── scholarship_internship_bot/         # V1 untouched
└── scholarship_internship_bot_v2/
    ├── __init__.py                     # exposes `root_agent` and `agent`
    ├── agent.py                        # flat LlmAgent
    └── tools/
        ├── __init__.py
        └── web_search.py               # Tavily-backed function tool
```

**Tool import pattern (Tutor V2):** V2 reuses V1's tool implementations by direct Python import — e.g., `from ..tutor.tools.canvas_tools import connect_canvas`. No copy, no re-export shim. Only `agent.py` changes; tool logic is shared source of truth.

**Scholarship V2** owns `web_search.py` outright; no shared code with V1 since V1 used grounding.

**cs_navigator readiness:** Each V2 package exposes the agent as both `root_agent` (for `adk run`) and `agent` (for import into `cs_navigator`). No module-level side effects on import beyond reading env vars. This lets `cs_navigator` later do `from adk_deploy.tutor_v2 import agent as tutor_agent` and wrap it in `AgentTool(agent=tutor_agent)` or add it to `sub_agents=[...]` without touching V2 internals.

## Data flow

### Tutor V2 turn (e.g., "Debug my COSC 251 code")

```
Student → tutor_v2 LLM call (1 round-trip)
         ├── instruction: all modes, Canvas rules, etc.
         ├── model selects "Code Debugger" mode internally
         ├── optionally calls search_course_materials(...) → tool result back
         └── streams reply
```

Compared to V1 which was: student → root LLM call → sub-agent LLM call → tool → streamed reply (2+ round-trips).

### Scholarship V2 turn (e.g., "Find CS scholarships for juniors")

```
Student → scholarship_v2 LLM call
         ├── instruction: deadline filter rule, modes, sources
         ├── calls web_search("Morgan State CS scholarships 2026") → Tavily JSON back
         ├── optionally calls web_search again for ScholarshipUniverse
         └── streams reply with verified deadlines
```

Compared to V1 which was: student → single LLM call with `google_search` grounding that does search + re-rank + injection server-side (slow).

## Error handling

- **Tavily failures** (network, 4xx, 5xx, rate-limit): the tool returns `{"error": "<message>", "results": []}` and the model tells the student search is temporarily unavailable and falls back to general knowledge. No retries in tool (keep it fast); the model can retry by calling the tool again if it wants.
- **Missing `TAVILY_API_KEY`**: `web_search` raises at import time with a clear message so the agent fails to start rather than failing silently per-turn.
- **Vertex AI Search datastore envs missing** (existing V1 behavior): tools list is empty, agent still works without knowledge base.
- **Canvas not connected**: existing V1 tool behavior, unchanged.

## Testing

Manual A/B comparison is the core test plan:

1. Run V1 tutor: `adk run adk_deploy/tutor`. Send 5 canonical prompts, record wall-clock time to first token and total time.
2. Run V2 tutor: `adk run adk_deploy/tutor_v2`. Same 5 prompts, record the same timings.
3. Repeat for scholarship V1 vs V2 with 3 canonical prompts (explain a scholarship topic, find CS scholarships, find summer internships).
4. Verify V2 preserves: deadline filtering, mode-appropriate tone, tool calls fire correctly.

Canonical tutor prompts:
- "Explain recursion like I'm a beginner"
- "Debug this Python function: <small buggy snippet>"
- "Quiz me on Big-O, 5 questions"
- "What's in the COSC 251 syllabus?" (requires syllabi datastore)
- "Walk me through this LeetCode two-sum problem"

Canonical scholarship prompts:
- "Find CS scholarships for junior year"
- "What are the Google STEP / Microsoft Explore deadlines?"
- "Help me write a personal statement for the UNCF scholarship"

Success criteria:
- V2 end-to-end time is ≤ 50% of V1 on at least 6 of the 8 combined prompts.
- V2 first-token time is ≤ 40% of V1 on the same prompts.
- No regression in correctness: tool calls fire, deadlines get filtered, modes pick the right teaching style.

If the speed targets miss, the fallback is a follow-up spec (not in scope): either downgrade to `gemini-2.5-flash-lite` or add prompt-level context caching.

## Environment and secrets

- Add `TAVILY_API_KEY` to `.env.example` (not `.env`) with placeholder value.
- `.env` remains gitignored as today.
- No API keys in any file committed to the repo, including this spec.

## Open questions

None blocking. Already-settled questions:
- Personality preservation: yes, keep six mode sections with their existing tones and teaching rules.
- Search provider: Tavily, free tier 1000/month; Serper is the paid upgrade if we outgrow it.
- Scholarship/internship split: keep combined for now; splitting only wins under parallel execution, which ADK local CLI doesn't provide without re-adding a routing hop. Revisit if/when cs_navigator orchestrates them as parallel sub-agents.

## Out of scope (followups)

- Prompt caching via Gemini context caching API.
- Streaming-first CLI wrapper that shows tokens faster.
- Migrating V2 into `cs_navigator` as sub-agents (separate integration spec already exists at `docs/superpowers/specs/2026-04-08-tutor-scholarship-integration-design.md`).
- Measuring and optimizing individual tool latencies (Canvas sync, Vertex AI Search).
- Downgrading some paths to `gemini-2.5-flash-lite`.
