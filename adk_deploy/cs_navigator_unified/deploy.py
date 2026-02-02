# -*- coding: utf-8 -*-
"""
Deploy CS Navigator Unified Agent to Vertex AI Agent Engine
"""

import os
import sys

# Set environment variables
os.environ['GOOGLE_CLOUD_PROJECT'] = 'csnavigator-vertex-ai'
os.environ['GOOGLE_CLOUD_LOCATION'] = 'us-central1'
os.environ['GOOGLE_GENAI_USE_VERTEXAI'] = 'true'

def deploy_agent():
    """Deploy the unified CS Navigator agent to Vertex AI Agent Engine."""
    try:
        from google.adk.agents import LlmAgent
        from google.adk import deploy as adk_deploy
        from agent import root_agent

        print("=" * 60)
        print("Deploying CS Navigator (Unified) to Vertex AI Agent Engine")
        print("=" * 60)
        print(f"Project: {os.environ['GOOGLE_CLOUD_PROJECT']}")
        print(f"Location: {os.environ['GOOGLE_CLOUD_LOCATION']}")
        print(f"Agent: {root_agent.name}")
        print(f"Sub-agents: {[sa.name for sa in root_agent.sub_agents]}")
        print("=" * 60)

        # Deploy to Agent Engine
        result = adk_deploy.deploy(
            agent=root_agent,
            project=os.environ['GOOGLE_CLOUD_PROJECT'],
            location=os.environ['GOOGLE_CLOUD_LOCATION'],
            display_name='CS_Navigator_Unified',
        )

        print("\nDeployment successful!")
        print(f"Resource Name: {result.resource_name}")
        print(f"Resource ID: {result.resource_name.split('/')[-1]}")

        return result

    except ImportError as e:
        print(f"Import error: {e}")
        print("\nMake sure google-adk is installed:")
        print("  pip install google-adk")
        sys.exit(1)
    except Exception as e:
        print(f"Deployment error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    deploy_agent()
