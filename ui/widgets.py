"""
TextCraft UI Widgets
--------------------
Custom Textual widgets specialized for the Director's Monitor.
These components encapsulate presentation logic (coloring, formatting, updates).
"""

from datetime import datetime
from typing import Dict, Any, List

from textual.widgets import RichLog, DataTable, Static, Markdown, ProgressBar
from textual.app import ComposeResult

class ProseStream(RichLog):
    """
    The main reading area. 
    Specialized RichLog that handles smooth scrolling and 'typewriter' appending.
    """
    
    def on_mount(self) -> None:
        self.markup = True
        self.wrap = True
        self.write("[bold dim italic]Waiting for Narrator stream...[/]")

    def append_content(self, text: str) -> None:
        """Appends new text and auto-scrolls to the latest content."""
        if text:
            self.write(text)
            # Auto-scroll is handled natively by RichLog if we don't interfere,
            # but we ensure it keeps up with the stream to maintain 'live' feel.
            self.scroll_end(animate=False)

class SystemLog(RichLog):
    """
    The Debug/Orchestrator log.
    Automatically timestamps entries and color-codes based on the Agent.
    """

    AGENT_COLORS = {
        "ARCHITECT": "magenta",
        "NARRATOR": "cyan",
        "EDITOR": "red",
        "SCANNER": "green",
        "DIRECTOR": "yellow", # User Input
        "SYSTEM": "dim white",
        "ERROR": "bold red"
    }

    def on_mount(self) -> None:
        self.markup = True
        self.write("[dim]System Log Initialized.[/]")

    def log_event(self, agent: str, message: str) -> None:
        """
        Formats a log entry: [HH:MM:SS] [AGENT] Message
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        color = self.AGENT_COLORS.get(agent.upper(), "white")
        
        formatted_message = (
            f"[dim]{timestamp}[/] "
            f"[bold {color}][{agent.upper()}][/] "
            f"{message}"
        )
        self.write(formatted_message)

class MatrixTable(DataTable):
    """
    The Project Status Table.
    Handles row coloring based on chapter status (LOCKED, DRAFTING, etc).
    """

    def on_mount(self) -> None:
        self.cursor_type = "row"
        self.add_columns("ID", "Status", "Words")

    def update_data(self, content: Dict[str, Any]) -> None:
        """
        Refreshes the table content from the Matrix JSON.
        """
        self.clear()
        
        # Sort keys to keep chapters in order (ch01, ch02...)
        sorted_keys = sorted(content.keys())

        for key in sorted_keys:
            item = content[key]
            status = item.get("status", "UNKNOWN").upper()
            words = f"{item.get('word_count', 0):,}"
            
            # Apply styling tags defined in ui/app.tcss
            status_styled = f"{status}"
            if status == "LOCKED":
                status_styled = f"[bold green]{status}[/]"
            elif status == "REVIEW_READY":
                status_styled = f"[bold cyan]{status}[/]"
            elif status == "DRAFTING":
                status_styled = f"[bold yellow]{status}[/]"
            elif status == "FAIL":
                status_styled = f"[bold red]{status}[/]"
            elif status == "MISSING":
                status_styled = f"[dim red]{status}[/]"

            self.add_row(key, status_styled, words, key=key)

class CastList(Markdown):
    """
    Displays the active characters in the scene.
    Updates dynamically based on the Orchestrator's active task context.
    """
    
    DEFAULT_TEXT = """
    *No Active Scene*
    
    _Waiting for Architect..._
    """

    def on_mount(self) -> None:
        self.update(self.DEFAULT_TEXT)

    def update_cast(self, active_characters: List[str]) -> None:
        """
        Receives a list of character names (e.g., ["Kael Voss", "Mara Syn"]).
        Formats them into a Markdown list.
        """
        if not active_characters:
            self.update(self.DEFAULT_TEXT)
            return

        md_lines = ["**CAST IN SCENE**"]
        for char in active_characters:
            md_lines.append(f"- {char}")
        
        self.update("\n".join(md_lines))

class ToolCard(Static):
    """
    Visual indicator of the current tool being used (Write, Edit, Search).
    Flashes color when active.
    """

    def set_idle(self) -> None:
        self.update("IDLE")
        self.remove_class("active")

    def set_active(self, tool_name: str, args: str = "") -> None:
        """
        Updates the card to show what the AI is doing physically.
        """
        display = f"{tool_name.upper()}\n[dim]{args}[/]"
        self.update(display)
        self.add_class("active")