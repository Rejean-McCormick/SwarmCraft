"""
TextCraft UI Screens
--------------------
Defines the high-level Screen layouts used by the App.
Connects the Grid layout (CSS) with the Custom Widgets.
"""

from textual.app import ComposeResult
from textual.screen import Screen, ModalScreen
from textual.containers import Container, Grid, Vertical, Horizontal
from textual.widgets import Input, Static, ProgressBar, Label, Button, Select, Slider

# Import custom components
from ui.widgets import ProseStream, SystemLog, MatrixTable, CastList, ToolCard

class DirectorScreen(Screen):
    """
    The Primary Interface (Mission Control).
    Implements the 3-Column 'Holy Grail' Layout.
    
    """

    def compose(self) -> ComposeResult:
        # --- COLUMN 1: CONTEXT (Inputs) ---
        with Container(id="context-panel"):
            yield Static("CAST IN SCENE", classes="header-text")
            yield CastList(id="cast-list")
            
            yield Static("LOCATION", classes="header-text")
            yield Static("Loading Setting...", id="location-card")
            
            yield Static("ACTIVE TOOL", classes="header-text")
            yield ToolCard("IDLE", id="tool-card")

        # --- COLUMN 2: ACTION (Outputs) ---
        with Container(id="action-panel"):
            # The Prose Stream takes up the top 75%
            yield ProseStream(id="prose-stream")
            # The System Log takes up the bottom 25%
            yield SystemLog(id="system-log")

        # --- COLUMN 3: PROGRESS (State) ---
        with Container(id="progress-panel"):
            yield Static("STORY MATRIX", classes="header-text")
            yield MatrixTable(id="matrix-table")
            
            yield Static("NARRATIVE INTEGRITY", classes="header-text")
            yield ProgressBar(total=100, show_eta=False, id="integrity-gauge")
            
            yield Static("SESSION COST", classes="header-text")
            yield Static("$0.00 / $5.00", id="cost-tracker")

        # --- FOOTER: COMMAND LINE ---
        yield Input(
            placeholder="> Director Override: Type instruction to Architect...", 
            id="director-input"
        )

class SettingsModal(ModalScreen):
    """
    The 'Vibe Check' Popup (Ctrl+S).
    Allows live adjustment of runtime settings.
    """
    
    # Note: Variables like $accent are resolved from app.tcss
    CSS = """
    SettingsModal {
        align: center middle;
    }
    
    #settings-dialog {
        padding: 1 2;
        width: 60;
        height: auto;
        border: thick $accent;
        background: $surface;
    }
    
    .label { padding: 1 0; color: $secondary; }
    """

    def compose(self) -> ComposeResult:
        with Vertical(id="settings-dialog"):
            yield Label("VIBE CHECK (Runtime Config)", classes="header-text")
            
            yield Label("Global Creativity (Temperature):", classes="label")
            yield Slider(min=0.1, max=1.0, step=0.1, value=0.7, id="temp-slider")
            
            yield Label("Model Override:", classes="label")
            yield Select.from_values(
                ["gpt-4-turbo", "gpt-4o", "claude-3-opus", "claude-3.5-sonnet"],
                prompt="Select Model",
                id="model-select"
            )
            
            with Horizontal():
                yield Button("Apply Changes", variant="primary", id="btn-apply")
                yield Button("Cancel", variant="error", id="btn-cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-cancel":
            self.dismiss()
        elif event.button.id == "btn-apply":
            temp = self.query_one("#temp-slider").value
            model = self.query_one("#model-select").value
            # Return dict to main app callback
            self.dismiss({"temperature": temp, "model": model})