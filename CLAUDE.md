# Google AI Engine Research - Complete Documentation

## What Is This Project?

This is a **local multi-agent AI system** that mirrors your Vertex AI Agent Designer setup but runs on your own machine. Instead of relying solely on Google Cloud, you can now:

1. Run agents locally with the same logic
2. Connect to Gmail and Google Calendar via MCP
3. Save everything to GitHub
4. Customize and extend without touching Google Cloud console

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         YOUR MACHINE                                 │
│                                                                      │
│   ┌─────────────────────────────────────────────────────────────┐   │
│   │                    CS NAVIGATOR                              │   │
│   │            (Main Orchestrator Agent)                         │   │
│   │                                                              │   │
│   │  1. Receives your question                                   │   │
│   │  2. Decides which sub-agents to ask                          │   │
│   │  3. Runs them IN PARALLEL (faster!)                          │   │
│   │  4. Compares answers and picks the best one                  │   │
│   │  5. Uses MCP tools if needed (send email, create event)      │   │
│   └─────────────────────────────────────────────────────────────┘   │
│                              │                                       │
│         ┌────────────────────┼────────────────────┐                 │
│         ▼                    ▼                    ▼                 │
│   ┌───────────┐       ┌───────────┐       ┌───────────┐            │
│   │ Academic  │       │  Career   │       │  Course   │    ...     │
│   │  Advisor  │       │ Guidance  │       │Recommender│            │
│   └───────────┘       └───────────┘       └───────────┘            │
│                                                                      │
│   ┌─────────────────────────────────────────────────────────────┐   │
│   │                    MCP TOOLS                                 │   │
│   │                                                              │   │
│   │  ┌─────────────┐    ┌──────────────────┐                    │   │
│   │  │  Gmail MCP  │    │  Calendar MCP    │                    │   │
│   │  │             │    │                  │                    │   │
│   │  │ - Send mail │    │ - Create events  │                    │   │
│   │  │ - Draft     │    │ - Check free     │                    │   │
│   │  │ - Search    │    │ - Set reminders  │                    │   │
│   │  └─────────────┘    └──────────────────┘                    │   │
│   └─────────────────────────────────────────────────────────────┘   │
│                              │                                       │
│                              ▼                                       │
│                    ┌─────────────────┐                              │
│                    │  Google Cloud   │                              │
│                    │   Vertex AI     │                              │
│                    │  (Gemini LLM)   │                              │
│                    └─────────────────┘                              │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Why These Tools? (Detailed Explanations)

### 1. LangGraph (instead of raw code or other frameworks)

**What it is:** A library from LangChain for building AI "graphs" - workflows where agents can loop, branch, and run in parallel.

**Why we chose it:**
- **Native parallel execution** - Run Academic Advisor + Career Guidance + Course Recommender simultaneously
- **State management** - Keeps track of conversation history across agents
- **Human-in-the-loop** - Can pause for your approval before sending emails
- **Checkpointing** - Save/resume conversations

**Alternatives we didn't choose:**
| Alternative | Why we didn't use it |
|-------------|---------------------|
| Raw Python async | Too much boilerplate, no state management |
| AutoGen (Microsoft) | More complex setup, less Google Cloud integration |
| CrewAI | Good but less flexible for custom routing |
| OpenAI Assistants | Locked to OpenAI, not Vertex AI |

---

### 2. LangChain (instead of direct API calls)

**What it is:** A framework that standardizes how you talk to different AI models.

**Why we chose it:**
- **Unified interface** - Same code works with Vertex AI, OpenAI, Anthropic
- **Prompt templates** - Easy to manage agent prompts
- **Tool integration** - Built-in support for MCP
- **Memory** - Conversation history out of the box

**Alternatives we didn't choose:**
| Alternative | Why we didn't use it |
|-------------|---------------------|
| Direct google.cloud.aiplatform | More code, harder to switch models |
| Haystack | Less mature Vertex AI support |
| LlamaIndex | Better for RAG, less for agents |

---

### 3. Vertex AI Gemini (instead of other models)

**What it is:** Google's latest AI model, accessed through your existing Google Cloud project.

**Why we chose it:**
- **Your existing setup** - Same model as your Vertex AI agents
- **Same billing** - Uses your current Google Cloud credits
- **Grounding** - Can connect to Google Search for real-time info
- **Long context** - Handles large documents well

**Alternatives we didn't choose:**
| Alternative | Why we didn't use it |
|-------------|---------------------|
| OpenAI GPT-4 | Different billing, different capabilities |
| Claude | Would need separate API key |
| Local Ollama | Less capable, slower |

---

### 4. MCP - Model Context Protocol (instead of custom integrations)

**What it is:** A standard protocol from Anthropic that defines how AI agents talk to external tools.

**Why we chose it:**
- **Standardized** - Works across different AI frameworks
- **Secure** - Tools run in isolated processes
- **Composable** - Mix and match tools easily
- **Growing ecosystem** - Gmail, Calendar, GitHub, Slack, etc.

**Alternatives we didn't choose:**
| Alternative | Why we didn't use it |
|-------------|---------------------|
| OpenAI Function Calling | OpenAI-specific |
| Custom REST APIs | More code, no standard |
| Zapier | External service, costs money |

---

## What You Need (Prerequisites)

### 1. Google Cloud Project
You already have this! It's where your Vertex AI agents live.

**To find your Project ID:**
1. Go to https://console.cloud.google.com
2. Look at the top bar - project name/ID is there
3. Example: `csnavigator-vertex-ai` (from your screenshot)

### 2. Authentication (2 options)

**Option A: gcloud CLI (Recommended for development)**
```bash
# Install gcloud CLI if you haven't
# Then run:
gcloud auth application-default login
```
This uses YOUR Google account. No files to manage.

**Option B: Service Account JSON (For production)**
1. Go to Google Cloud Console → IAM → Service Accounts
2. Create a new service account
3. Grant roles: `Vertex AI User`, `Gmail API`, `Calendar API`
4. Download JSON key file
5. Set environment variable:
```bash
export GOOGLE_APPLICATION_CREDENTIALS="path/to/key.json"
```

### 3. Enable APIs
In Google Cloud Console, enable these:
- Vertex AI API
- Gmail API
- Google Calendar API

### 4. OAuth Consent Screen (for Gmail/Calendar)
Since you'll be accessing YOUR OWN email:
1. Go to Google Cloud Console → APIs & Services → OAuth consent screen
2. Set to "Internal" (if using Google Workspace) or "External" (personal Gmail)
3. Add scopes: `gmail.send`, `gmail.compose`, `calendar.events`
4. Create OAuth 2.0 Client ID (Desktop application)
5. Download the credentials JSON

---

## Project Structure

```
google-ai-engine-research/
│
├── CLAUDE.md                    # This file - full documentation
├── README.md                    # Quick start guide
├── pyproject.toml               # Python dependencies
├── .env.example                 # Template for secrets
├── .gitignore                   # What NOT to commit
│
├── src/
│   ├── __init__.py
│   ├── main.py                  # CLI entry point
│   │
│   ├── orchestrator/            # The "brain" (LangChain version)
│   │   ├── __init__.py
│   │   ├── cs_navigator.py      # Main router + parallel execution
│   │   └── consensus.py         # Picks best answer from multiple agents
│   │
│   ├── agents/                  # Individual agents (LangChain version)
│   │   ├── __init__.py
│   │   ├── base.py              # Common agent code
│   │   ├── academic_advisor.py  # Course selection, faculty info
│   │   ├── career_guidance.py   # Jobs, internships, resume tips
│   │   ├── course_recommender.py # Course suggestions
│   │   ├── schedule_builder.py  # Class scheduling
│   │   ├── degreeworks.py       # Degree progress tracking
│   │   ├── general_qa.py        # General CS department questions
│   │   └── financial_aid.py     # FAFSA, scholarships, tuition
│   │
│   ├── adk_agents/              # Google ADK agents (NEW!)
│   │   ├── __init__.py          # Module exports
│   │   ├── config.py            # ADK configuration & resource IDs
│   │   ├── base.py              # ADK base agent class
│   │   ├── cs_navigator.py      # Main orchestrator (ADK)
│   │   ├── academic_advisor.py  # Academic Advisor (ADK)
│   │   ├── career_guidance.py   # Career Guidance (ADK)
│   │   ├── course_recommender.py # Course Recommender (ADK)
│   │   ├── degreeworks.py       # DegreeWorks (ADK)
│   │   ├── general_qa.py        # General Q&A (ADK)
│   │   ├── schedule_builder.py  # Schedule Builder (ADK)
│   │   └── financial_aid.py     # Financial Aid (ADK)
│   │
│   ├── mcp/                     # External tool integrations
│   │   ├── __init__.py
│   │   ├── gmail_server.py      # Gmail MCP server
│   │   └── calendar_server.py   # Calendar MCP server
│   │
│   └── config/
│       ├── __init__.py
│       ├── agents.yaml          # Agent prompts and settings
│       └── settings.py          # Environment config
│
├── data/                        # Knowledge base (JSON)
│   ├── courses.json             # Morgan State CS courses
│   ├── requirements.json        # Degree requirements
│   └── resources.json           # Campus resources
│
├── credentials/                 # OAuth files (gitignored!)
│   └── .gitkeep
│
└── examples/
    ├── ask_question.py          # Basic usage
    ├── parallel_demo.py         # Show parallel execution
    ├── email_demo.py            # Gmail MCP demo
    └── adk_demo.py              # ADK agents demo (NEW!)
```

---

## How Each Component Works

### CS Navigator (orchestrator/cs_navigator.py)

The main "traffic controller". When you ask a question:

```python
# Simplified logic
class CSNavigator:
    def handle_query(self, question: str):
        # Step 1: Classify the question
        categories = self.classify(question)
        # Returns: ["academic", "career"] or ["schedule"] etc.

        # Step 2: Select relevant agents
        agents = [self.agents[cat] for cat in categories]

        # Step 3: Run in PARALLEL (not one by one!)
        responses = await asyncio.gather(*[
            agent.answer(question) for agent in agents
        ])

        # Step 4: Pick best answer (or combine them)
        best = self.consensus.select_best(responses)

        # Step 5: Check if MCP action needed
        if best.needs_email:
            await self.mcp.gmail.draft_email(best.email_content)

        return best.answer
```

### Agent Base Class (agents/base.py)

All agents share this structure:

```python
class BaseAgent:
    def __init__(self, name: str, system_prompt: str, llm):
        self.name = name
        self.prompt = system_prompt
        self.llm = llm  # Vertex AI Gemini

    async def answer(self, question: str) -> AgentResponse:
        messages = [
            {"role": "system", "content": self.prompt},
            {"role": "user", "content": question}
        ]
        response = await self.llm.generate(messages)
        return AgentResponse(
            agent=self.name,
            answer=response.text,
            confidence=self._calculate_confidence(response),
            sources=self._extract_sources(response)
        )
```

### Gmail MCP Server (mcp/gmail_server.py)

MCP servers expose "tools" that agents can use:

```python
# Tools this server provides:
@mcp.tool()
async def draft_email(to: str, subject: str, body: str):
    """Create a draft email (doesn't send yet)"""

@mcp.tool()
async def send_email(draft_id: str):
    """Send a previously created draft"""

@mcp.tool()
async def search_inbox(query: str):
    """Search your inbox for relevant emails"""
```

---

## Google ADK Agents (New!)

The project now includes Google Agent Development Kit (ADK) agents that mirror the Vertex AI Agent Designer setup.

### What is ADK?

Google ADK is Google's official framework for building AI agents that can be deployed to Vertex AI Agent Engine. It provides:
- **Direct deployment** to Vertex AI Agent Engine
- **Knowledge base integration** with Vertex AI Search
- **Tool support** for custom functions
- **Local development** with the same code that runs in production

### ADK Agent Files

Each agent has a template file in `src/adk_agents/`. After deploying agents in Vertex AI Agent Designer:

1. Click "Get Code" in Agent Designer
2. Copy the generated code
3. Paste it into the `_create_agent()` method in the corresponding file

### Using ADK Agents

```bash
# Ask a question using ADK agents
python -m src.main adk ask "What courses should I take?"

# Interactive chat with ADK agents
python -m src.main adk chat

# Check ADK configuration and deployment status
python -m src.main adk config

# List all ADK agents
python -m src.main adk agents
```

### ADK vs LangChain Agents

The project includes TWO agent implementations:

| Feature | LangChain Agents | ADK Agents |
|---------|-----------------|------------|
| Location | `src/agents/` | `src/adk_agents/` |
| Framework | LangChain + LangGraph | Google ADK |
| Deployment | Local only | Vertex AI Agent Engine |
| Command | `python -m src.main ask` | `python -m src.main adk ask` |
| Knowledge Base | Custom JSON | Vertex AI Search |

### Deploying ADK Agents to Vertex AI

1. **In Agent Designer:**
   - Open each agent
   - Remove DegreeWorks MCP (if present)
   - Click "Deploy"
   - Note the resource ID

2. **Update config.py:**
   ```python
   # src/adk_agents/config.py
   agent_resource_ids = {
       "cs_navigator": "your-resource-id-here",
       "academic_advisor": "your-resource-id-here",
       # ... etc
   }
   ```

3. **Copy agent code:**
   - Click "Get Code" in Agent Designer
   - Paste into `_create_agent()` method in each agent file

---

## Parallel Execution Explained

Traditional (slow):
```
Question → Agent 1 → wait... → Agent 2 → wait... → Agent 3 → Combine
Total time: 3 + 3 + 3 = 9 seconds
```

Our approach (fast):
```
           ┌→ Agent 1 ──┐
Question ──┼→ Agent 2 ──┼→ Combine
           └→ Agent 3 ──┘
Total time: 3 seconds (parallel!)
```

This is done with Python's `asyncio`:
```python
import asyncio

# Run all agents at the same time
responses = await asyncio.gather(
    academic_advisor.answer(question),
    career_guidance.answer(question),
    course_recommender.answer(question)
)
# All 3 run simultaneously!
```

---

## Consensus (Best Answer Selection)

When multiple agents respond, we need to pick the best one:

```python
class ConsensusSelector:
    def select_best(self, responses: List[AgentResponse]) -> AgentResponse:
        scores = []
        for response in responses:
            score = (
                response.confidence * 0.4 +      # Agent's self-reported confidence
                self.relevance_score(response) * 0.3 +  # How relevant to question
                self.completeness_score(response) * 0.2 +  # How complete the answer
                self.has_sources(response) * 0.1   # Does it cite sources?
            )
            scores.append((score, response))

        # Return highest scoring response
        return max(scores, key=lambda x: x[0])[1]
```

---

## Environment Variables Needed

```bash
# .env file (never commit this!)

# Google Cloud
GOOGLE_CLOUD_PROJECT=csnavigator-vertex-ai
GOOGLE_APPLICATION_CREDENTIALS=credentials/service-account.json

# Or use default credentials (gcloud auth application-default login)
# Then you don't need the above

# OAuth for Gmail/Calendar
GMAIL_OAUTH_CREDENTIALS=credentials/oauth.json
```

---

## How to Run (after setup)

```bash
# Install dependencies
pip install -e .

# Authenticate with Google
gcloud auth application-default login

# Run the CLI
python -m src.main

# Or run examples
python examples/ask_question.py "What courses should I take next semester?"
python examples/email_demo.py
```

---

## Session Log

### Session 1 - February 1, 2026

**Goal:** Create a downloadable multi-agent AI system that mirrors the Vertex AI Agent Designer setup, with Gmail and Calendar MCP integrations.

**Files Created:**
1. `pyproject.toml` - Python dependencies (LangChain, LangGraph, Vertex AI, MCP)
2. `src/agents/base.py` - Abstract base class for all agents
3. `src/agents/academic_advisor.py` - Course selection, faculty info
4. `src/agents/career_guidance.py` - Jobs, internships, career paths
5. `src/agents/course_recommender.py` - Course suggestions
6. `src/agents/schedule_builder.py` - Conflict-free scheduling
7. `src/agents/degreeworks.py` - Degree progress tracking
8. `src/agents/general_qa.py` - Campus resources, policies
9. `src/agents/financial_aid.py` - Scholarships, FAFSA, tuition
10. `src/orchestrator/cs_navigator.py` - Main orchestrator with parallel execution
11. `src/orchestrator/consensus.py` - Best-answer selection algorithm
12. `src/mcp/gmail_server.py` - Gmail MCP (draft, send, search)
13. `src/mcp/calendar_server.py` - Calendar MCP (create events, check availability)
14. `src/config/settings.py` - Environment configuration
15. `src/config/agents.yaml` - Agent prompts and settings
16. `src/main.py` - CLI entry point (ask, chat, config commands)
17. `examples/ask_question.py` - Basic usage example
18. `examples/parallel_demo.py` - Parallel execution demo
19. `examples/email_demo.py` - Gmail MCP demo
20. `README.md` - Quick start guide
21. `CLAUDE.md` - Comprehensive documentation
22. `.env.example` - Environment template
23. `.gitignore` - Git ignore rules

**Architecture Decisions:**
- **LangGraph** for orchestration (parallel execution, state management)
- **LangChain** for unified AI interface (works with Vertex AI)
- **MCP** for tool integration (standard protocol, isolated execution)
- **Consensus scoring** with weighted factors (relevance, completeness, confidence, specificity)

**Status:** Complete and ready for testing

### Session 2 - February 1, 2026

**Goal:** Deploy Vertex AI agents and set up local ADK (Agent Development Kit).

**Files Created:**
1. `src/adk_agents/__init__.py` - Module exports for ADK agents
2. `src/adk_agents/config.py` - ADK configuration with resource IDs
3. `src/adk_agents/base.py` - Base class for ADK agents
4. `src/adk_agents/cs_navigator.py` - Main orchestrator (ADK version)
5. `src/adk_agents/academic_advisor.py` - Academic Advisor (ADK)
6. `src/adk_agents/career_guidance.py` - Career Guidance (ADK)
7. `src/adk_agents/course_recommender.py` - Course Recommender (ADK)
8. `src/adk_agents/degreeworks.py` - DegreeWorks (ADK)
9. `src/adk_agents/general_qa.py` - General Q&A (ADK)
10. `src/adk_agents/schedule_builder.py` - Schedule Builder (ADK)
11. `src/adk_agents/financial_aid.py` - Financial Aid (ADK)
12. `examples/adk_demo.py` - ADK usage demonstration

**Files Modified:**
1. `pyproject.toml` - Added google-adk dependency
2. `src/main.py` - Added ADK commands (adk ask, adk chat, adk config, adk agents)
3. `CLAUDE.md` - Added ADK documentation

**Architecture Decisions:**
- **Template-based approach** - Agent files contain templates to paste "Get Code" output
- **Dual implementation** - LangChain agents (local) + ADK agents (Vertex AI deployable)
- **Parallel execution** - ADK orchestrator queries sub-agents in parallel using asyncio
- **Configuration-driven** - Resource IDs stored in config.py for easy updates

**Manual Steps Required:**
1. Remove DegreeWorks MCP from agents in Agent Designer
2. Deploy each agent to Vertex AI Agent Engine
3. Copy resource IDs to `src/adk_agents/config.py`
4. Copy "Get Code" output into each agent's `_create_agent()` method

**Status:** ADK structure complete, awaiting manual deployment and code copy

---

## Glossary

| Term | Meaning |
|------|---------|
| **Agent** | An AI with a specific role (like "Career Advisor") |
| **Orchestrator** | The main AI that routes questions to agents |
| **MCP** | Model Context Protocol - how AI uses external tools |
| **LangGraph** | Framework for building multi-agent workflows |
| **Vertex AI** | Google's AI platform (hosts Gemini) |
| **OAuth** | Authentication method for accessing your Gmail/Calendar |
| **Consensus** | Algorithm to pick the best answer from multiple responses |

---

## Troubleshooting

### "Default credentials not found"
```bash
gcloud auth application-default login
```

### "API not enabled"
Go to Google Cloud Console → APIs & Services → Enable the API

### "Permission denied for Gmail"
Need to complete OAuth flow. Run the app once and it will open browser for consent.

### "Model not found"
Make sure Vertex AI API is enabled and you're using the right model name (e.g., `gemini-1.5-pro`)

---

## Next Steps

### Initial Setup (if not done)
1. [ ] Get your Google Cloud Project ID
2. [ ] Enable Vertex AI, Gmail, Calendar APIs
3. [ ] Set up OAuth consent screen
4. [ ] Run `gcloud auth application-default login`

### ADK Agent Deployment
5. [ ] Remove DegreeWorks MCP from each agent in Agent Designer
6. [ ] Deploy CS Navigator to Vertex AI Agent Engine
7. [ ] Deploy Academic Advisor to Agent Engine
8. [ ] Deploy Career Guidance to Agent Engine
9. [ ] Deploy Course Recommender to Agent Engine
10. [ ] Deploy DegreeWorks to Agent Engine
11. [ ] Deploy General Q&A to Agent Engine
12. [ ] Deploy Schedule Builder to Agent Engine
13. [ ] Deploy Financial Aid to Agent Engine
14. [ ] Copy resource IDs to `src/adk_agents/config.py`
15. [ ] Copy "Get Code" output to each agent file

### Testing
16. [ ] Test with: `python -m src.main adk ask "What courses should I take?"`
17. [ ] Test chat: `python -m src.main adk chat`
18. [ ] Verify knowledge base queries work
