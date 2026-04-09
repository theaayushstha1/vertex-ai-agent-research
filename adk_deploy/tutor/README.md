# AI Tutor

A multi-agent AI tutoring system built with Google ADK. 5 specialized sub-agents handle
CS concepts, Math, quizzing, code debugging, and walking through problem sets.

```
┌──────────────────────────────────────────────────────┐
│                   AI_Tutor (Orchestrator)             │
│                                                      │
│  "explain binary search" → CS_Tutor                  │
│  "quiz me on derivatives" → Quiz_Master              │
│  "debug my code" → Code_Debugger                     │
│  "walk me through this integral" → Problem_Solver    │
│  "what is an eigenvector" → Math_Tutor               │
└──────────────────────────────────────────────────────┘
```

## Sub-Agents

| Agent | What it handles |
|---|---|
| CS_Tutor | DSA, OS, systems, CS theory — intuition-first explanations |
| Math_Tutor | Calc, Linear Algebra, Discrete Math — step-by-step with CS connections |
| Quiz_Master | Interactive quizzes + flashcard decks on any topic |
| Code_Debugger | Finds bugs, explains why, teaches the lesson |
| Problem_Solver | Socratic walkthroughs with a hint system (won't just give the answer) |

## Setup

```bash
cd adk_deploy/ai_tutor
cp .env.example .env
# Fill in GOOGLE_CLOUD_PROJECT and STAGING_BUCKET
```

## Run Locally

```bash
cd adk_deploy/ai_tutor
adk run .
```

## Deploy to Vertex AI

```bash
cd adk_deploy/ai_tutor
python deploy_wrapper.py
```

Then go to **Vertex AI Console → Agent Engine → Playground** to chat with it.

## Optional: Add Your Own Course Materials (RAG)

Upload your notes, slides, or textbooks to Vertex AI Search, then set
`VERTEX_AI_DATASTORE_ID` in `.env`. The CS, Math, and Problem Solver agents
will automatically search your materials when answering questions.

## Example Interactions

```
You: "explain what a binary heap is"
→ CS_Tutor explains intuitively, then formally, with code example

You: "quiz me on sorting algorithms, intermediate level"
→ Quiz_Master runs a 10-question quiz with score tracking

You: "here's my code, it keeps giving index out of bounds: [code]"
→ Code_Debugger finds the bug, explains the off-by-one error, shows the fix

You: "walk me through finding the derivative of x²sin(x)"
→ Problem_Solver gives hints first, then full solution with product rule explained

You: "make me 15 flashcards on eigenvalues"
→ Quiz_Master generates a FRONT/BACK deck ready to study
```
