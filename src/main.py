"""
Main Entry Point
================

This is the CLI for the Google AI Engine Research project.
Run with: python -m src.main

USAGE:
------
# Ask a question
python -m src.main ask "What courses should I take next semester?"

# List available agents
python -m src.main agents

# Run in interactive mode
python -m src.main chat

# Check configuration
python -m src.main config
"""

import asyncio
import sys
from typing import Optional

import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table

from .config.settings import get_settings, ensure_directories
from .orchestrator.cs_navigator import CSNavigator

# ADK imports (lazy loaded to avoid import errors if google-adk not installed)
ADK_AVAILABLE = False
try:
    from .adk_agents import CSNavigatorADK, get_adk_config
    from .adk_agents.cs_navigator import create_navigator as create_adk_navigator
    ADK_AVAILABLE = True
except ImportError:
    pass

# Initialize CLI app
app = typer.Typer(
    name="google-ai-engine",
    help="Morgan State CS Multi-Agent System - Ask questions, get intelligent answers.",
    add_completion=False,
)

console = Console()


def get_llm():
    """
    Initialize the Vertex AI LLM.

    Returns a LangChain ChatVertexAI instance.
    """
    from langchain_google_vertexai import ChatVertexAI

    settings = get_settings()

    # Validate Google Cloud config
    settings.validate_google_cloud()

    return ChatVertexAI(
        model_name=settings.vertex_ai_model,
        project=settings.google_cloud_project,
        location=settings.vertex_ai_location,
        temperature=0.7,
        max_output_tokens=2048,
    )


def get_navigator() -> CSNavigator:
    """Get initialized CS Navigator."""
    llm = get_llm()
    return CSNavigator(llm=llm)


@app.command()
def ask(
    question: str = typer.Argument(..., help="Your question for the CS agents"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed scoring info"),
):
    """
    Ask a question and get the best answer from specialized agents.

    Examples:
        python -m src.main ask "What courses should I take next semester?"
        python -m src.main ask "How do I apply for scholarships?" -v
    """
    console.print(f"\n[bold blue]Question:[/bold blue] {question}\n")

    with console.status("[bold green]Thinking...[/bold green]"):
        try:
            navigator = get_navigator()
            response = navigator.ask_sync(question)
        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {e}")
            raise typer.Exit(1)

    # Display response
    console.print(Panel(
        Markdown(response.answer),
        title=f"[bold green]{response.agent_name}[/bold green]",
        subtitle=f"Confidence: {response.confidence:.0%}",
        border_style="green",
    ))

    if verbose and response.metadata:
        console.print("\n[dim]Metadata:[/dim]")
        for key, value in response.metadata.items():
            console.print(f"  [dim]{key}:[/dim] {value}")


@app.command()
def chat():
    """
    Start an interactive chat session.

    Type your questions and get responses. Type 'quit' or 'exit' to end.
    """
    console.print(Panel(
        "[bold]Welcome to Morgan State CS Agent Office![/bold]\n\n"
        "I can help you with:\n"
        "- Course selection and scheduling\n"
        "- Career guidance and internships\n"
        "- Degree progress and requirements\n"
        "- Financial aid and scholarships\n"
        "- General CS department questions\n\n"
        "[dim]Type 'quit' or 'exit' to end the session.[/dim]",
        title="CS Navigator",
        border_style="blue",
    ))

    try:
        navigator = get_navigator()
    except Exception as e:
        console.print(f"[bold red]Setup Error:[/bold red] {e}")
        raise typer.Exit(1)

    while True:
        try:
            question = console.input("\n[bold blue]You:[/bold blue] ")

            if question.lower() in ["quit", "exit", "q"]:
                console.print("[dim]Goodbye![/dim]")
                break

            if not question.strip():
                continue

            with console.status("[bold green]Thinking...[/bold green]"):
                response = navigator.ask_sync(question)

            console.print(f"\n[bold green]{response.agent_name}:[/bold green]")
            console.print(Markdown(response.answer))

        except KeyboardInterrupt:
            console.print("\n[dim]Interrupted. Goodbye![/dim]")
            break


@app.command()
def agents():
    """
    List all available agents and their descriptions.
    """
    try:
        navigator = get_navigator()
        agent_info = navigator.get_agent_info()
    except Exception as e:
        # Show agents even without LLM connection
        agent_info = [
            {"name": "Academic Advisor", "description": "Course selection, faculty info, degree requirements"},
            {"name": "Career Guidance", "description": "Jobs, internships, resume tips, career paths"},
            {"name": "Course Recommender", "description": "Course suggestions based on interests and goals"},
            {"name": "Schedule Builder", "description": "Conflict-free class scheduling"},
            {"name": "DegreeWorks", "description": "Degree progress and graduation planning"},
            {"name": "General Q&A", "description": "Campus resources, policies, deadlines"},
            {"name": "Financial Aid", "description": "Scholarships, FAFSA, tuition help"},
        ]

    table = Table(title="Available Agents", show_header=True, header_style="bold blue")
    table.add_column("Agent", style="green")
    table.add_column("Description")

    for agent in agent_info:
        table.add_row(agent["name"], agent["description"])

    console.print(table)


@app.command()
def config():
    """
    Display current configuration and check setup.
    """
    settings = get_settings()

    table = Table(title="Configuration", show_header=True, header_style="bold blue")
    table.add_column("Setting", style="cyan")
    table.add_column("Value")
    table.add_column("Status")

    # Google Cloud Project
    project = settings.google_cloud_project or "(not set)"
    status = "[green]OK[/green]" if settings.google_cloud_project else "[red]MISSING[/red]"
    table.add_row("Google Cloud Project", project, status)

    # Vertex AI settings
    table.add_row("Vertex AI Model", settings.vertex_ai_model, "[green]OK[/green]")
    table.add_row("Vertex AI Location", settings.vertex_ai_location, "[green]OK[/green]")

    # OAuth credentials
    oauth_exists = settings.oauth_credentials_path.exists()
    oauth_status = "[green]Found[/green]" if oauth_exists else "[yellow]Not found[/yellow]"
    table.add_row("OAuth Credentials", str(settings.oauth_credentials_path), oauth_status)

    # MCP settings
    table.add_row("Gmail MCP", "Enabled" if settings.mcp_gmail_enabled else "Disabled", "[green]OK[/green]")
    table.add_row("Calendar MCP", "Enabled" if settings.mcp_calendar_enabled else "Disabled", "[green]OK[/green]")

    console.print(table)

    # Check Google auth
    console.print("\n[bold]Authentication Check:[/bold]")

    # Check gcloud CLI
    import shutil
    gcloud_path = shutil.which("gcloud")
    if gcloud_path:
        console.print("  [green]✓[/green] gcloud CLI found")
    else:
        console.print("  [yellow]![/yellow] gcloud CLI not found - install from cloud.google.com/sdk")

    # Check default credentials
    from pathlib import Path
    default_creds = Path.home() / ".config/gcloud/application_default_credentials.json"
    if default_creds.exists():
        console.print("  [green]✓[/green] Application default credentials found")
    else:
        console.print("  [yellow]![/yellow] Run: gcloud auth application-default login")


@app.command()
def setup():
    """
    Run initial setup - create directories and check requirements.
    """
    console.print("[bold]Running setup...[/bold]\n")

    # Create directories
    ensure_directories()
    console.print("  [green]✓[/green] Created required directories")

    # Check settings
    settings = get_settings()

    # Display next steps
    console.print("\n[bold]Next Steps:[/bold]")

    if not settings.google_cloud_project:
        console.print("  1. Set GOOGLE_CLOUD_PROJECT in .env file")

    console.print("  2. Run: gcloud auth application-default login")
    console.print("  3. Enable APIs: Vertex AI, Gmail, Calendar")
    console.print("  4. Download OAuth credentials for Gmail/Calendar")
    console.print("\n  Then run: python -m src.main chat")


# ==============================================================================
# ADK Commands (Google Agent Development Kit)
# ==============================================================================

adk_app = typer.Typer(
    name="adk",
    help="Google ADK agent commands - use deployed Vertex AI agents",
    add_completion=False,
)
app.add_typer(adk_app, name="adk")


@adk_app.command("ask")
def adk_ask(
    question: str = typer.Argument(..., help="Your question for the ADK agents"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed info"),
):
    """
    Ask a question using Google ADK agents.

    Examples:
        python -m src.main adk ask "What courses should I take?"
        python -m src.main adk ask "How do I apply for scholarships?" -v
    """
    if not ADK_AVAILABLE:
        console.print("[bold red]Error:[/bold red] Google ADK not installed.")
        console.print("Run: pip install google-adk")
        raise typer.Exit(1)

    console.print(f"\n[bold blue]Question:[/bold blue] {question}\n")

    with console.status("[bold green]Thinking (ADK)...[/bold green]"):
        try:
            navigator = create_adk_navigator(register_all_agents=True)
            response = navigator.run_sync(question)
        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {e}")
            raise typer.Exit(1)

    # Display response
    console.print(Panel(
        Markdown(response.answer),
        title=f"[bold green]{response.agent_name}[/bold green]",
        subtitle=f"Confidence: {response.confidence:.0%}",
        border_style="green",
    ))

    if verbose and response.metadata:
        console.print("\n[dim]Metadata:[/dim]")
        for key, value in response.metadata.items():
            console.print(f"  [dim]{key}:[/dim] {value}")


@adk_app.command("chat")
def adk_chat():
    """
    Start an interactive chat session using ADK agents.

    Type your questions and get responses. Type 'quit' or 'exit' to end.
    """
    if not ADK_AVAILABLE:
        console.print("[bold red]Error:[/bold red] Google ADK not installed.")
        console.print("Run: pip install google-adk")
        raise typer.Exit(1)

    console.print(Panel(
        "[bold]Welcome to CS Navigator (ADK Mode)![/bold]\n\n"
        "Using Google Agent Development Kit agents.\n\n"
        "I can help you with:\n"
        "- Course selection and scheduling\n"
        "- Career guidance and internships\n"
        "- Degree progress and requirements\n"
        "- Financial aid and scholarships\n"
        "- General CS department questions\n\n"
        "[dim]Type 'quit' or 'exit' to end the session.[/dim]",
        title="CS Navigator (ADK)",
        border_style="cyan",
    ))

    try:
        navigator = create_adk_navigator(register_all_agents=True)
    except Exception as e:
        console.print(f"[bold red]Setup Error:[/bold red] {e}")
        raise typer.Exit(1)

    while True:
        try:
            question = console.input("\n[bold cyan]You:[/bold cyan] ")

            if question.lower() in ["quit", "exit", "q"]:
                console.print("[dim]Goodbye![/dim]")
                break

            if not question.strip():
                continue

            with console.status("[bold green]Thinking (ADK)...[/bold green]"):
                response = navigator.run_sync(question)

            console.print(f"\n[bold green]{response.agent_name}:[/bold green]")
            console.print(Markdown(response.answer))

        except KeyboardInterrupt:
            console.print("\n[dim]Interrupted. Goodbye![/dim]")
            break


@adk_app.command("config")
def adk_config_cmd():
    """
    Display ADK configuration and deployment status.
    """
    if not ADK_AVAILABLE:
        console.print("[bold red]Error:[/bold red] Google ADK not installed.")
        console.print("Run: pip install google-adk")
        raise typer.Exit(1)

    config = get_adk_config()

    # Validate config
    issues = config.validate()

    table = Table(title="ADK Configuration", show_header=True, header_style="bold cyan")
    table.add_column("Setting", style="cyan")
    table.add_column("Value")
    table.add_column("Status")

    # Google Cloud settings
    project_status = "[green]OK[/green]" if config.project_id else "[red]MISSING[/red]"
    table.add_row("Project ID", config.project_id or "(not set)", project_status)
    table.add_row("Project Number", config.project_number, "[green]OK[/green]")
    table.add_row("Location", config.location, "[green]OK[/green]")
    table.add_row("Model", config.model_name, "[green]OK[/green]")
    table.add_row("Knowledge Base", config.knowledge_base_id, "[green]OK[/green]")

    console.print(table)

    # Agent deployment status
    console.print("\n[bold]Agent Deployment Status:[/bold]")

    agent_table = Table(show_header=True, header_style="bold cyan")
    agent_table.add_column("Agent", style="cyan")
    agent_table.add_column("Resource ID")
    agent_table.add_column("Status")

    from .adk_agents.config import AGENT_INFO

    for agent_name, info in AGENT_INFO.items():
        resource_id = config.agent_resource_ids.get(agent_name, "")
        if resource_id:
            status = "[green]Deployed[/green]"
            display_id = resource_id[:40] + "..." if len(resource_id) > 40 else resource_id
        else:
            status = "[yellow]Not deployed[/yellow]"
            display_id = "(not set)"

        agent_table.add_row(info["name"], display_id, status)

    console.print(agent_table)

    if issues:
        console.print("\n[bold yellow]Issues:[/bold yellow]")
        for issue in issues:
            console.print(f"  [yellow]![/yellow] {issue}")

    console.print("\n[bold]Next Steps:[/bold]")
    console.print("  1. Deploy agents in Vertex AI Agent Designer")
    console.print("  2. Copy resource IDs to src/adk_agents/config.py")
    console.print("  3. Copy 'Get Code' output to each agent file")
    console.print("  4. Run: python -m src.main adk chat")


@adk_app.command("agents")
def adk_agents():
    """
    List all ADK agents and their deployment status.
    """
    if not ADK_AVAILABLE:
        console.print("[bold red]Error:[/bold red] Google ADK not installed.")
        console.print("Run: pip install google-adk")
        raise typer.Exit(1)

    from .adk_agents.config import AGENT_INFO, get_adk_config

    config = get_adk_config()

    table = Table(title="ADK Agents", show_header=True, header_style="bold cyan")
    table.add_column("Agent", style="green")
    table.add_column("Description")
    table.add_column("Type")
    table.add_column("Status")

    for agent_name, info in AGENT_INFO.items():
        agent_type = "Orchestrator" if info.get("is_orchestrator") else "Sub-agent"
        resource_id = config.agent_resource_ids.get(agent_name, "")
        status = "[green]Ready[/green]" if resource_id else "[yellow]Pending[/yellow]"
        table.add_row(info["name"], info["description"], agent_type, status)

    console.print(table)


def main():
    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
