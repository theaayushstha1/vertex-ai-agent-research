"""
Example: Ask a Simple Question
==============================

This example shows how to use the CS Navigator to ask a question
and get the best answer from the appropriate agent.

Run with:
    python examples/ask_question.py
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path (for running as script)
sys.path.insert(0, str(Path(__file__).parent.parent))

from langchain_google_vertexai import ChatVertexAI
from src.orchestrator.cs_navigator import CSNavigator
from src.config.settings import get_settings


async def main():
    # Get settings
    settings = get_settings()

    print("=" * 60)
    print("CS Navigator - Ask a Question")
    print("=" * 60)

    # Check if Google Cloud is configured
    if not settings.google_cloud_project:
        print("\nERROR: GOOGLE_CLOUD_PROJECT not set!")
        print("Create a .env file with:")
        print("  GOOGLE_CLOUD_PROJECT=your-project-id")
        return

    print(f"\nUsing project: {settings.google_cloud_project}")
    print(f"Using model: {settings.vertex_ai_model}")

    # Initialize the LLM
    print("\nInitializing Vertex AI...")
    llm = ChatVertexAI(
        model_name=settings.vertex_ai_model,
        project=settings.google_cloud_project,
        location=settings.vertex_ai_location,
        temperature=0.7,
    )

    # Initialize the navigator
    print("Initializing CS Navigator...")
    navigator = CSNavigator(llm=llm)

    # Example questions
    questions = [
        "What courses should I take next semester if I'm interested in AI?",
        # "How do I apply for internships?",
        # "What are the graduation requirements for CS?",
    ]

    for question in questions:
        print("\n" + "-" * 60)
        print(f"Question: {question}")
        print("-" * 60)

        # Ask the question
        response = await navigator.ask(question)

        # Display the response
        print(f"\nAgent: {response.agent_name}")
        print(f"Confidence: {response.confidence:.0%}")
        print(f"\nAnswer:\n{response.answer}")

        # Check if MCP action is needed
        if response.needs_action:
            print(f"\n[MCP Action Suggested]")
            print(f"  Type: {response.action_type}")
            print(f"  Params: {response.action_params}")


if __name__ == "__main__":
    asyncio.run(main())
