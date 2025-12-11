import asyncio
import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv
from rich.console import Console
from rich.logging import RichHandler
from rich.panel import Panel
from rich.text import Text

# --- Internal Imports ---
from core.orchestrator import Orchestrator
from core.project_manager import ProjectManager

# --- Constants ---
VERSION = "3.0.0"
BANNER = f"""
TextCraft Engine v{VERSION}
---------------------------
The Data-Driven AI Storyteller
"""

# Initialize Rich Console
console = Console()

def setup_logging():
    """Configures a beautiful, readable log output using Rich."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True, console=console)]
    )
    # Silence noisy third-party libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("aiohttp").setLevel(logging.WARNING)
    logging.getLogger("chromadb").setLevel(logging.WARNING)

def check_environment():
    """Pre-flight checks to ensure the system is ready to launch."""
    load_dotenv()
    
    # 1. Check API Key
    if not os.getenv("LLM_API_KEY"):
        console.print("[bold red]CRITICAL ERROR:[/bold red] LLM_API_KEY not found in .env file.")
        console.print("Please create a .env file with your provider's API key.")
        sys.exit(1)

    # 2. Check Dependencies (Optional validation)
    # We no longer check for 'data/' because ProjectManager creates 'projects/' dynamically.

async def main():
    """The Main Application Loop."""
    setup_logging()
    check_environment()

    # Print Welcome Banner
    console.print(Panel(Text(BANNER, justify="center", style="bold cyan"), border_style="cyan"))

    try:
        # Step 1: Initialize the Librarian (Project Manager)
        console.print("[bold green]System:[/bold green] Initializing Project Manager...")
        pm = ProjectManager()
        
        # Step 2: Initialize the Nervous System (Orchestrator)
        # The Orchestrator will automatically load the last active project
        # and initialize the Scanner and MemoryStore for that specific context.
        console.print("[bold green]System:[/bold green] Awakening The Orchestrator...")
        orchestrator = Orchestrator(pm)

        # Display Loaded Context
        active_project = orchestrator.project_root.name
        console.print(f"[green]✔[/green] Active Universe: [bold cyan]{active_project}[/]")

        # Step 3: Ignite the Loop
        console.print("[bold yellow]>>> ENGINE START <<<[/bold yellow]")
        console.print("Press [bold red]Ctrl+C[/bold red] to stop the engine gracefully.\n")
        
        await orchestrator.start()

    except KeyboardInterrupt:
        console.print("\n[bold red]Shutdown Signal Received.[/bold red]")
        console.print("Saving state and terminating processes...")
    except Exception as e:
        console.print_exception()
        sys.exit(1)
    finally:
        console.print("[dim]TextCraft Session Ended.[/dim]")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass