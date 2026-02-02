"""
Example: Parallel Agent Execution
=================================

This example demonstrates how multiple agents run IN PARALLEL
and how the consensus algorithm selects the best answer.

The key insight:
- Traditional: Agent1 → wait → Agent2 → wait → Agent3 = 9 seconds
- Parallel:    Agent1 ─┐
               Agent2 ─┼→ Consensus = 3 seconds
               Agent3 ─┘

Run with:
    python examples/parallel_demo.py
"""

import asyncio
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from langchain_google_vertexai import ChatVertexAI
from src.orchestrator.cs_navigator import CSNavigator, QueryCategory
from src.config.settings import get_settings


async def main():
    settings = get_settings()

    print("=" * 60)
    print("Parallel Agent Execution Demo")
    print("=" * 60)

    if not settings.google_cloud_project:
        print("\nERROR: Set GOOGLE_CLOUD_PROJECT in .env")
        return

    # Initialize
    llm = ChatVertexAI(
        model_name=settings.vertex_ai_model,
        project=settings.google_cloud_project,
        location=settings.vertex_ai_location,
    )
    navigator = CSNavigator(llm=llm)

    # This question touches multiple domains - academic + career
    question = "What courses should I take to prepare for a software engineering career?"

    print(f"\nQuestion: {question}")

    # Show which categories this matches
    categories = navigator.classify_query(question)
    print(f"\nDetected categories: {[c.value for c in categories]}")

    # Time the parallel execution
    print("\nRunning agents in PARALLEL...")
    start_time = time.time()

    response = await navigator.ask(question)

    elapsed = time.time() - start_time
    print(f"Total time: {elapsed:.2f} seconds")

    # Show results
    print("\n" + "-" * 60)
    print(f"Selected Agent: {response.agent_name}")
    print(f"Confidence: {response.confidence:.0%}")
    print("-" * 60)
    print(f"\n{response.answer}")

    # Explain the selection
    print("\n" + "=" * 60)
    print("WHY THIS ANSWER WAS SELECTED")
    print("=" * 60)
    print("""
The consensus algorithm scored each agent's response on:

1. RELEVANCE (35%) - How well does it answer the question?
   - Keyword overlap between question and answer
   - Topic alignment

2. COMPLETENESS (25%) - How thorough is the answer?
   - Length and detail
   - Structured lists/sections
   - Examples provided

3. CONFIDENCE (25%) - How confident is the agent?
   - Self-reported confidence
   - Hedging language detection

4. SPECIFICITY (15%) - How concrete is the answer?
   - Contains numbers/dates
   - Course codes (COSC 301)
   - Named entities

The agent with the highest weighted score was selected.
""")


if __name__ == "__main__":
    asyncio.run(main())
