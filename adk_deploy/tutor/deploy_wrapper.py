"""
Deploy AI Tutor to Vertex AI Agent Engine
Run: python deploy_wrapper.py
"""

import os
import vertexai
from vertexai.preview import reasoning_engines
from dotenv import load_dotenv

load_dotenv()

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
STAGING_BUCKET = os.getenv("STAGING_BUCKET")  # e.g. gs://your-bucket-name

if not all([PROJECT_ID, STAGING_BUCKET]):
    raise ValueError("Set GOOGLE_CLOUD_PROJECT and STAGING_BUCKET in your .env")

vertexai.init(project=PROJECT_ID, location=LOCATION, staging_bucket=STAGING_BUCKET)

# Import after setting up environment
from agent import root_agent  # noqa: E402


def deploy():
    print(f"Deploying AI Tutor to {PROJECT_ID} / {LOCATION}...")

    remote_app = reasoning_engines.AdkApp(
        agent=root_agent,
        enable_tracing=True,
    )

    deployed = reasoning_engines.ReasoningEngine.create(
        remote_app,
        requirements=[
            "google-cloud-aiplatform[adk,reasoningengine]",
            "google-adk",
            "python-dotenv",
            "httpx",
            "google-cloud-storage",
            "google-cloud-discoveryengine",
            "google-cloud-firestore",
        ],
        display_name="AI Tutor",
        description="Multi-agent CS and Math tutor with quiz, debug, and problem-solving capabilities",
    )

    print("\n✅ Deployed successfully!")
    print(f"Resource name: {deployed.resource_name}")
    print(f"\nTo query your agent:")
    print(f'  agent = reasoning_engines.ReasoningEngine("{deployed.resource_name}")')
    print('  response = agent.query(query="Explain binary search")')
    print(f"\nOr open Vertex AI Console → Agent Engine → Playground")

    return deployed


if __name__ == "__main__":
    deploy()
