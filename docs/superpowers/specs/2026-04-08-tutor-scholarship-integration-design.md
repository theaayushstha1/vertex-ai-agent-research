# Tutor & Scholarship Agent Integration into CS Navigator -- Design Spec

**Date:** 2026-04-08
**Status:** Approved

## Goal

Integrate the standalone Tutor (6 sub-agents) and Scholarship/Internship bot into the cs-navigator as nested sub-agents, sharing Canvas LMS and DegreeWorks data through the existing backend.

## Agent Hierarchy

```
CS_Navigator (root)
  |-- Tutor (sub-agent orchestrator)
  |     |-- CS_Tutor
  |     |-- Math_Tutor
  |     |-- Quiz_Master
  |     |-- Code_Debugger
  |     |-- Problem_Solver
  |     +-- Syllabus_Advisor
  |-- Scholarship_Agent (sub-agent)
  +-- [existing KB search via VertexAiSearchTool]
```

CS_Navigator keeps its current job (general advising via KB). Tutoring and scholarship questions get delegated to the nested sub-agents.

## Canvas Data Flow

**Pre-fetched by backend (injected into session state):**
- Current courses, grades, upcoming assignments, missing submissions (from CanvasStudentData)
- GPA, major, classification, completed/remaining courses (from DegreeWorksData)

**Active tools kept on Tutor agent:**
- `sync_course_materials(course_name)` -- calls new backend endpoint that uses student's Canvas session
- `search_course_materials(query, course_id)` -- hits Vertex AI Discovery Engine directly

**Removed from tutor:**
- `connect_canvas()`, `get_course_assignments()` -- pre-fetched by backend
- `canvas/client.py`, `canvas/auth.py` -- replaced by backend's `canvas_client.py`

## Student Context Injection

All agents inherit session state from root. Backend extends existing context building:
- `degreeworks`: stable, hashed for session reuse (existing)
- `canvas`: volatile, sent via state_delta (existing)
- `tutor_progress`: new -- weak/strong topics, quiz scores from Firestore
- `memory`: long-term user memory (existing)

Scholarship_Agent reads GPA/major/classification from DW context to auto-filter results.

## Student Progress Storage

Quiz scores, mastery tracking, and session logs stay in **Firestore**. Backend reads from Firestore when building `tutor_progress` context. Tutor tools write to Firestore directly mid-conversation.

## Decisions

| Question | Answer |
|----------|--------|
| Agent hierarchy | Nested: Tutor orchestrator + Scholarship as sub-agents of root |
| Canvas approach | Hybrid: pre-fetch basics, keep active tools for material sync/search |
| Progress storage | Keep Firestore (separate from MySQL) |
| Scholarship personalization | Yes, inject DW context for auto-filtering |
| Routing depth | 2-level: root -> Tutor -> specialists |
