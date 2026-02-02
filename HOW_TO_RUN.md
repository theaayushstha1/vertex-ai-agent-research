# How to Run CS Navigator Locally

Quick guide to run the multi-agent AI system on your machine.

---

## Prerequisites

1. **Python 3.10+** installed
2. **Google Cloud authentication** configured:
   ```bash
   gcloud auth application-default login
   ```
3. **Dependencies installed:**
   ```bash
   pip install google-adk python-dotenv
   ```

---

## Option 1: Web Interface (Recommended)

The easiest way to interact with the agents through a browser UI.

```bash
# Navigate to the adk_deploy folder
cd adk_deploy

# Start the web server
python -m google.adk.cli web . --port 8080
```

Then open: **http://127.0.0.1:8080**

**Available agents in dropdown:**
- `cs_navigator_unified` - Main orchestrator (routes to all sub-agents)
- `academic_advisor` - Course selection, faculty info
- `career_guidance` - Jobs, internships, career paths
- `course_recommender` - Course suggestions
- `degreeworks` - Degree progress tracking
- `financial_aid` - Scholarships, FAFSA
- `general_qa` - Campus resources
- `schedule_builder` - Class scheduling

---

## Option 2: CLI Chat Interface

Interactive chat directly in your terminal.

```bash
# Navigate to the adk_deploy folder
cd adk_deploy

# Start CLI chat with specific agent
python -m google.adk.cli run cs_navigator_unified
```

Type your questions and press Enter. Type `exit` or `quit` to stop.

---

## Option 3: Single Agent CLI

Run a specific sub-agent directly:

```bash
cd adk_deploy

# Academic Advisor
python -m google.adk.cli run academic_advisor

# Career Guidance
python -m google.adk.cli run career_guidance

# Course Recommender
python -m google.adk.cli run course_recommender

# Financial Aid
python -m google.adk.cli run financial_aid

# DegreeWorks
python -m google.adk.cli run degreeworks

# Schedule Builder
python -m google.adk.cli run schedule_builder

# General Q&A
python -m google.adk.cli run general_qa
```

---

## Option 4: API Calls (Programmatic)

For integration with other applications:

```bash
# Start the server first
cd adk_deploy
python -m google.adk.cli web . --port 8080
```

Then in another terminal:

```bash
# List available agents
curl http://127.0.0.1:8080/list-apps?relative_path=./

# Create a session
curl -X POST "http://127.0.0.1:8080/apps/cs_navigator_unified/users/myuser/sessions" \
  -H "Content-Type: application/json" \
  -d "{}"

# Send a message (replace SESSION_ID with the id from above)
curl -X POST "http://127.0.0.1:8080/run_sse" \
  -H "Content-Type: application/json" \
  -d '{
    "app_name": "cs_navigator_unified",
    "user_id": "myuser",
    "session_id": "SESSION_ID",
    "new_message": {
      "role": "user",
      "parts": [{"text": "What courses should I take for AI?"}]
    }
  }'
```

---

## Environment Setup

Make sure you have a `.env` file in the `adk_deploy` folder:

```bash
# adk_deploy/.env
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=us-central1
GOOGLE_GENAI_USE_VERTEXAI=true
VERTEX_AI_DATASTORE_ID=projects/your-project/locations/us/collections/default_collection/dataStores/your-datastore-id
VERTEX_AI_MODEL=gemini-2.5-flash
```

---

## Troubleshooting

### "No agents found in current folder"
Make sure you're running from the `adk_deploy` folder, not from inside `cs_navigator_unified`:
```bash
# Correct
cd adk_deploy
python -m google.adk.cli web . --port 8080

# Wrong
cd adk_deploy/cs_navigator_unified
python -m google.adk.cli web . --port 8080
```

### "INVALID_ARGUMENT: Invalid Vertex AI datastore"
Your `.env` file is missing or has wrong values. Check `VERTEX_AI_DATASTORE_ID`.

### "Default credentials not found"
Run Google Cloud authentication:
```bash
gcloud auth application-default login
```

### Port already in use
Use a different port:
```bash
python -m google.adk.cli web . --port 8081
```

---

## Quick Start Summary

```bash
# Clone the repo
git clone https://github.com/theaayushstha1/vertex-ai-agent-research.git
cd vertex-ai-agent-research

# Install dependencies
pip install google-adk python-dotenv

# Authenticate
gcloud auth application-default login

# Create .env file in adk_deploy/ with your credentials

# Run web interface
cd adk_deploy
python -m google.adk.cli web . --port 8080

# Open http://127.0.0.1:8080
```

---

## Example Questions to Try

- "What courses should I take for AI and machine learning?"
- "How do I get a software engineering internship?"
- "What scholarships are available for CS students?"
- "Who are the CS faculty members?"
- "What are the degree requirements for Computer Science?"
- "Help me build a schedule for next semester"
