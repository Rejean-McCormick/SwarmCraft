"""
TextCraft UI Package
--------------------
The Director's Monitor: A Textual-based TUI for orchestrating AI agents.

This package separates the Visual Layer (Screens/Widgets) from the 
Application Logic (Dashboard).

Components:
- DirectorScreen: The primary 3-column mission control layout.
- SettingsModal: The configuration popup.
- Specialized Widgets: ProseStream, CastList, MatrixTable, ToolCard.
"""

from .screens import DirectorScreen, SettingsModal
from .widgets import ProseStream, CastList, MatrixTable, ToolCard, SystemLog

__all__ = [
    "DirectorScreen", 
    "SettingsModal", 
    "ProseStream", 
    "CastList", 
    "MatrixTable", 
    "ToolCard", 
    "SystemLog"
]