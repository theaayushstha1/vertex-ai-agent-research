"""
ADK Demo
========

Demonstrates how to use Google ADK agents locally.

PREREQUISITES:
--------------
1. Install dependencies: pip install -e .
2. Authenticate: gcloud auth application-default login
3. Set GOOGLE_CLOUD_PROJECT environment variable
4. (Optional) Deploy agents and update resource IDs in config.py

USAGE:
------
python examples/adk_demo.py
"""

import asyncio
import os
import sys

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


async def demo_single_agent():
    """Demo: Query a single ADK agent."""
    print("\n" + "=" * 60)
    print("Demo 1: Single Agent Query")
    print("=" * 60)

    from src.adk_agents import CSNavigatorADK

    navigator = CSNavigatorADK()
    response = await navigator.run("What courses should I take for AI and machine learning?")

    print(f"\nAgent: {response.agent_name}")
    print(f"Confidence: {response.confidence:.0%}")
    print(f"\nAnswer:\n{response.answer}")


async def demo_orchestrator():
    """Demo: Use the full orchestrator with sub-agents."""
    print("\n" + "=" * 60)
    print("Demo 2: Orchestrator with Sub-Agents")
    print("=" * 60)

    from src.adk_agents.cs_navigator import create_navigator

    # Create navigator with all sub-agents registered
    navigator = create_navigator(register_all_agents=True)

    questions = [
        "What courses should I take next semester?",
        "How do I find internships in software engineering?",
        "What are the graduation requirements for CS?",
    ]

    for question in questions:
        print(f"\n[Question]: {question}")
        response = await navigator.run(question)
        print(f"[{response.agent_name}]: {response.answer[:200]}...")
        print()


async def demo_parallel_agents():
    """Demo: Query multiple agents in parallel."""
    print("\n" + "=" * 60)
    print("Demo 3: Parallel Agent Queries")
    print("=" * 60)

    from src.adk_agents.academic_advisor import AcademicAdvisorADK
    from src.adk_agents.career_guidance import CareerGuidanceADK
    from src.adk_agents.course_recommender import CourseRecommenderADK

    # Create agents
    agents = [
        AcademicAdvisorADK(),
        CareerGuidanceADK(),
        CourseRecommenderADK(),
    ]

    question = "What should I focus on for a career in data science?"

    print(f"\n[Question]: {question}")
    print("\nQuerying all agents in parallel...")

    # Run all agents in parallel
    tasks = [agent.run(question) for agent in agents]
    responses = await asyncio.gather(*tasks)

    for response in responses:
        print(f"\n[{response.agent_name}]:")
        print(f"  {response.answer[:150]}...")


def demo_sync():
    """Demo: Synchronous usage."""
    print("\n" + "=" * 60)
    print("Demo 4: Synchronous Usage")
    print("=" * 60)

    from src.adk_agents.general_qa import GeneralQAADK

    agent = GeneralQAADK()
    response = agent.run_sync("Where is the CS department office located?")

    print(f"\nAgent: {response.agent_name}")
    print(f"Answer: {response.answer}")


async def main():
    """Run all demos."""
    print("=" * 60)
    print("Google ADK Agents Demo")
    print("=" * 60)

    # Check if ADK is available
    try:
        from src.adk_agents import get_adk_config
        config = get_adk_config()
        print(f"\nProject: {config.project_id or '(not set)'}")
        print(f"Location: {config.location}")
        print(f"Model: {config.model_name}")
    except ImportError as e:
        print(f"\nError: Could not import ADK agents: {e}")
        print("Make sure you've installed the project: pip install -e .")
        return

    # Note about deployment
    print("\n" + "-" * 60)
    print("NOTE: Agents are not yet deployed to Vertex AI.")
    print("Until deployment, agents will return placeholder responses.")
    print("Follow these steps to deploy:")
    print("  1. Open Vertex AI Agent Designer")
    print("  2. Deploy each agent")
    print("  3. Copy 'Get Code' output to agent files")
    print("  4. Update resource IDs in config.py")
    print("-" * 60)

    # Run demos
    await demo_single_agent()
    await demo_orchestrator()
    await demo_parallel_agents()
    demo_sync()

    print("\n" + "=" * 60)
    print("Demo Complete!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
