# Vertex AI Agent Research

A production-ready **multi-agent AI system** built with Google's Agent Development Kit (ADK) and deployed to Vertex AI Agent Engine. This project demonstrates how to build a unified orchestrator agent with 7 specialized sub-agents.

![Vertex AI](https://img.shields.io/badge/Vertex_AI-Agent_Engine-4285F4?logo=google-cloud)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python)
![License](https://img.shields.io/badge/License-MIT-green)

## What This Project Does

```
┌─────────────────────────────────────────────────────────────────┐
│                    CS Navigator (Orchestrator)                   │
│                                                                  │
│   User: "What courses should I take for AI?"                    │
│                          ↓                                       │
│   Orchestrator routes to → Course_Recommender                   │
│                          ↓                                       │
│   Sub-agent searches Knowledge Base (Vertex AI Search)          │
│                          ↓                                       │
│   Returns personalized course recommendations                   │
└─────────────────────────────────────────────────────────────────┘
```

**7 Specialized Sub-Agents:**
| Agent | Purpose |
|-------|---------|
| Academic Advisor | Course selection, faculty info, policies |
| Career Guidance | Jobs, internships, career paths |
| Course Recommender | Personalized course suggestions |
| DegreeWorks | Degree progress, requirements |
| Schedule Builder | Conflict-free class schedules |
| Financial Aid | Scholarships, FAFSA, tuition |
| General Q&A | Campus resources, department info |

## Quick Start

### Prerequisites
- Python 3.10+
- Google Cloud account with billing enabled
- `gcloud` CLI installed

### 1. Clone & Install

```bash
git clone https://github.com/theaayushstha1/vertex-ai-agent-research.git
cd vertex-ai-agent-research
pip install -e .
```

### 2. Configure Google Cloud

```bash
# Login to Google Cloud
gcloud auth application-default login

# Set your project
gcloud config set project YOUR_PROJECT_ID
```

### 3. Set Up Environment

```bash
cp .env.example .env
# Edit .env with your project details
```

### 4. Deploy to Vertex AI Agent Engine

```bash
cd adk_deploy/cs_navigator_unified
adk deploy agent_engine --project=YOUR_PROJECT --region=us-central1
```

### 5. Test in Playground

1. Go to [Vertex AI Agent Engine](https://console.cloud.google.com/vertex-ai/agents/agent-engines)
2. Click on your deployed agent
3. Open Playground and start chatting!

## Project Structure

```
vertex-ai-agent-research/
│
├── adk_deploy/
│   └── cs_navigator_unified/     # THE DEPLOYED AGENT
│       ├── agent.py              # All 7 sub-agents + orchestrator
│       ├── deploy_wrapper.py     # Deployment script
│       └── .env                  # Local config
│
├── src/
│   ├── agents/                   # LangChain agent implementations
│   ├── adk_agents/               # ADK agent templates
│   ├── orchestrator/             # Parallel execution logic
│   ├── mcp/                      # Gmail/Calendar integrations
│   └── main.py                   # CLI entry point
│
├── examples/                     # Usage examples
├── CLAUDE.md                     # Full technical documentation
└── pyproject.toml                # Dependencies
```

## The Main Agent File

The heart of this system is `adk_deploy/cs_navigator_unified/agent.py`:

```python
from google.adk.agents import LlmAgent
from google.adk.tools import VertexAiSearchTool

# Connect to your knowledge base
KNOWLEDGE_BASE_ID = os.getenv('VERTEX_AI_DATASTORE_ID')

# Create specialized sub-agents
academic_advisor = LlmAgent(
    name='Academic_Advisor',
    model='gemini-2.5-flash',
    tools=[VertexAiSearchTool(data_store_id=KNOWLEDGE_BASE_ID)],
    instruction='Help students with academic planning...'
)

# Main orchestrator with all sub-agents
root_agent = LlmAgent(
    name='CS_Navigator',
    sub_agents=[
        academic_advisor,
        career_guidance,
        course_recommender,
        # ... 4 more sub-agents
    ],
    instruction='Route questions to the right sub-agent...'
)
```

## How to Customize for Your Institution

1. **Create a Knowledge Base:**
   - Go to [Vertex AI Search](https://console.cloud.google.com/vertex-ai/search)
   - Create a Data Store with your institution's documents
   - Copy the Data Store ID

2. **Update agent.py:**
   - Replace `Morgan State` references with your institution
   - Customize sub-agent instructions for your use case
   - Update course codes, degree requirements, etc.

3. **Set Environment Variable:**
   ```bash
   export VERTEX_AI_DATASTORE_ID="projects/YOUR_PROJECT/locations/us/collections/default_collection/dataStores/YOUR_DATASTORE"
   ```

4. **Deploy:**
   ```bash
   adk deploy agent_engine --project=YOUR_PROJECT --region=us-central1
   ```

## API Usage

Once deployed, you can call your agent programmatically:

```python
from google.cloud import aiplatform

# Initialize
aiplatform.init(project='YOUR_PROJECT', location='us-central1')

# Get your agent
agent = aiplatform.reasoning_engines.ReasoningEngine(
    'projects/YOUR_PROJECT/locations/us-central1/reasoningEngines/YOUR_AGENT_ID'
)

# Query the agent
response = agent.query(query="What courses should I take for AI?")
print(response)
```

## Local Development

```bash
# Run locally with ADK
cd adk_deploy/cs_navigator_unified
adk run .

# Or use the CLI
python -m src.main chat
```

## Technologies Used

| Technology | Purpose |
|------------|---------|
| [Google ADK](https://cloud.google.com/vertex-ai/docs/agent-engine) | Agent Development Kit for building AI agents |
| [Vertex AI Agent Engine](https://cloud.google.com/vertex-ai/docs/agent-engine) | Managed deployment platform |
| [Vertex AI Search](https://cloud.google.com/vertex-ai/docs/vector-search) | Knowledge base / RAG |
| [Gemini 2.5 Flash](https://cloud.google.com/vertex-ai/docs/generative-ai/gemini) | Fast LLM for agent responses |
| [LangChain](https://python.langchain.com/) | Alternative local implementation |
| [MCP](https://modelcontextprotocol.io/) | Gmail/Calendar tool integration |

## Documentation

For comprehensive documentation, see [CLAUDE.md](./CLAUDE.md) including:
- Full architecture explanation
- Step-by-step setup guide
- How each tool was chosen
- Troubleshooting

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## License

MIT License - see [LICENSE](./LICENSE) for details.

## Acknowledgments

- Built during research on Google Vertex AI Agent Engine
- Uses Google's Agent Development Kit (ADK)
- Originally designed for Morgan State University CS Department
