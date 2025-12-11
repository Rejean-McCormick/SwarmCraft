import json
import asyncio
import aiofiles
import logging
from pathlib import Path
from typing import Dict, Any, Optional

from textual.app import App
from textual import work
from textual.widgets import Input, ProgressBar, Static
from textual.binding import Binding

# --- Internal Imports ---
from ui.screens import DirectorScreen, SettingsModal
from ui.widgets import CastList, ToolCard, MatrixTable, ProseStream
from core.project_manager import ProjectManager

# Ensure logging doesn't interfere with TUI
logging.getLogger("textual").setLevel(logging.WARNING)

class TextCraftApp(App):
    """
    The Director's Monitor (TUI).
    Orchestrates the UI updates and user commands.
    """
    
    CSS_PATH = "ui/app.tcss"
    
    BINDINGS = [
        Binding("q", "quit", "Quit", show=True),
        Binding("space", "toggle_pause", "Pause/Resume", show=True),
        Binding("ctrl+s", "open_settings", "Vibe Check", show=True),
    ]

    def on_mount(self) -> None:
        """Initialize the Application with Project Awareness."""
        self.title = "TextCraft Director's Monitor v3.0"
        
        # 1. Initialize Project Manager
        self.pm = ProjectManager()
        
        # 2. Get Active Project
        self.project_id = self.pm.get_last_active_project()
        if not self.project_id:
            # Fallback if no project is active (e.g., first run)
            self.project_id = "default_project"
            self.pm.create_project(self.project_id, "Untitled Story")
            self.pm.set_active_project(self.project_id)
            
        self.sub_title = f"Connected to: {self.project_id}"

        # 3. Resolve Dynamic Paths
        self.project_root = self.pm.get_project_path(self.project_id)
        if not self.project_root:
            self.exit(message=f"CRITICAL: Could not resolve path for project '{self.project_id}'")
            return

        self.data_dir = self.project_root / "data"
        self.matrix_path = self.data_dir / "matrix.json"
        self.control_path = self.data_dir / "control.json"
        
        # 4. Launch GUI
        self.push_screen(DirectorScreen())
        
        # 5. Start watchers
        self.watch_matrix_loop()
        self.watch_stream_loop()

    # --- ACTION HANDLERS ---

    def action_open_settings(self) -> None:
        """Triggered by Ctrl+S. Opens the Vibe Check modal."""
        def on_settings_close(result: Optional[Dict]):
            if result:
                self.update_runtime_settings(result)
                self.log_system_event("DIRECTOR", f"Applied settings: {result}")
        
        self.push_screen(SettingsModal(), on_settings_close)

    async def action_toggle_pause(self) -> None:
        """Triggered by Space. Toggles system pause state."""
        try:
            if not self.control_path.exists():
                return

            async with aiofiles.open(self.control_path, "r") as f:
                content = await f.read()
                data = json.loads(content)
            
            new_status = "PAUSED" if data.get("system_status") == "RUNNING" else "RUNNING"
            data["system_status"] = new_status
            
            async with aiofiles.open(self.control_path, "w") as f:
                await f.write(json.dumps(data, indent=2))
            
            self.log_system_event("SYSTEM", f"System set to {new_status}")
            
        except Exception as e:
            self.log_system_event("ERROR", f"Failed to toggle pause: {e}")

    async def on_input_submitted(self, message: Input.Submitted) -> None:
        """Handle Director Commands from the bottom input bar."""
        instruction = message.value.strip()
        if not instruction:
            return

        input_widget = self.query_one("#director-input", Input)
        input_widget.value = ""  # Clear input immediately
        input_widget.placeholder = "Sending command..."

        try:
            # 1. Read Control File
            async with aiofiles.open(self.control_path, "r") as f:
                data = json.loads(await f.read())
            
            # 2. Inject Override
            data["architect_override"]["active"] = True
            data["architect_override"]["instruction"] = instruction
            
            # 3. Write Control File
            async with aiofiles.open(self.control_path, "w") as f:
                await f.write(json.dumps(data, indent=2))
                
            self.log_system_event("DIRECTOR", instruction)
            input_widget.placeholder = "> Director Override: Type instruction to Architect..."
            
        except Exception as e:
            self.log_system_event("ERROR", f"Command failed: {e}")
            input_widget.placeholder = "Error sending command."

    # --- BACKGROUND WORKERS (The Nervous System) ---

    @work(exclusive=True)
    async def watch_matrix_loop(self) -> None:
        """Polls matrix.json every 1s to update the state tables."""
        last_mtime = 0.0
        
        while True:
            try:
                if self.matrix_path.exists():
                    stat = self.matrix_path.stat()
                    if stat.st_mtime > last_mtime:
                        last_mtime = stat.st_mtime
                        
                        async with aiofiles.open(self.matrix_path, "r") as f:
                            content = await f.read()
                            if content:
                                matrix = json.loads(content)
                                self.update_ui_from_matrix(matrix)
            except Exception:
                pass  # Atomic read failure is expected occasionally
            
            await asyncio.sleep(1.0)

    @work(exclusive=True)
    async def watch_stream_loop(self) -> None:
        """Polls the active manuscript file to stream text to the prose window."""
        current_target = None
        file_cursor = 0
        
        while True:
            try:
                # 1. Get Target from active UI state (via matrix)
                if self.matrix_path.exists():
                    async with aiofiles.open(self.matrix_path, "r") as f:
                        content = await f.read()
                        if not content:
                            await asyncio.sleep(0.5)
                            continue
                        matrix = json.loads(content)
                    
                    target_id = matrix.get("active_task", {}).get("target")
                    
                    if target_id:
                        # Resolve path
                        file_data = matrix.get("content", {}).get(target_id, {})
                        rel_path = file_data.get("path") # e.g., "data/manuscripts/ch01.md"
                        
                        if rel_path:
                            # IMPORTANT: rel_path is relative to project root in v3.0
                            full_path = self.project_root / rel_path
                            
                            # Detect Context Switch
                            if target_id != current_target:
                                stream_widget = self.query_one("#prose-stream", ProseStream)
                                stream_widget.write(f"\n[bold yellow]--- SWITCHING CONTEXT TO: {target_id} ---[/bold yellow]\n")
                                current_target = target_id
                                file_cursor = 0 # Reset cursor for new file
                            
                            # Read Incremental Content
                            if full_path.exists():
                                async with aiofiles.open(full_path, "r", encoding="utf-8") as f:
                                    # Move to last known position
                                    await f.seek(file_cursor)
                                    new_content = await f.read()
                                    
                                    if new_content:
                                        self.query_one("#prose-stream", ProseStream).append_content(new_content)
                                        file_cursor += len(new_content.encode('utf-8')) # Byte cursor update

            except Exception:
                pass
            
            await asyncio.sleep(0.5)

    # --- UI UPDATERS ---

    def update_ui_from_matrix(self, matrix: Dict[str, Any]) -> None:
        """Dispatches data to the specialized widgets."""
        
        # 1. Update Matrix Table
        table = self.query_one("#matrix-table", MatrixTable)
        table.update_data(matrix.get("content", {}))
        
        # 2. Update Integrity Gauge
        score = matrix.get("metrics", {}).get("narrative_integrity_score", 100)
        self.query_one("#integrity-gauge", ProgressBar).update(total=100, progress=score)
        
        # 3. Update Active Tool Card
        task = matrix.get("active_task", {})
        agent = task.get("assigned_to")
        action = task.get("action")
        
        tool_card = self.query_one("#tool-card", ToolCard)
        if agent and action:
            tool_card.set_active(agent, action)
        else:
            tool_card.set_idle()
            
        # 4. Update Cost
        cost = matrix.get("metrics", {}).get("session_cost", 0.0)
        self.query_one("#cost-tracker", Static).update(f"${cost:.2f} / $5.00")

        # 5. Update Cast List
        cast_list = task.get("active_characters", [])
        
        if not cast_list:
            # Heuristic Fallback
            notes = str(task.get("action", "")) + " " + str(task.get("target", ""))
            # You can improve this regex/matching logic
            if "Kael" in notes: cast_list.append("Kael Voss")
            if "Mara" in notes: cast_list.append("Mara Syn")
            if "Doc" in notes: cast_list.append("Doc Riley")

        self.query_one("#cast-list", CastList).update_cast(cast_list)

    async def update_runtime_settings(self, settings: Dict[str, Any]) -> None:
        """Writes settings from Modal to control.json."""
        try:
            async with aiofiles.open(self.control_path, "r") as f:
                data = json.loads(await f.read())
            
            data["runtime_settings"]["global_temperature"] = settings.get("temperature", 0.7)
            data["runtime_settings"]["model_override"] = settings.get("model")
            
            async with aiofiles.open(self.control_path, "w") as f:
                await f.write(json.dumps(data, indent=2))
        except Exception as e:
            self.log_system_event("ERROR", f"Failed to save settings: {e}")

    def log_system_event(self, source: str, message: str) -> None:
        """Helper to push messages to the SystemLog widget."""
        log_widget = self.query_one("#system-log")
        log_widget.log_event(source, message)

if __name__ == "__main__":
    app = TextCraftApp()
    app.run()