"""
TextCraft Core Package
----------------------
The Logic Layer: Manages the central execution loop, file system scanning,
deterministic rule enforcement, and advanced project/memory management.

Components:
- Orchestrator: The main loop (Scan -> Plan -> Dispatch -> Execute).
- ProjectScanner: The sensory system that updates the Matrix.
- ProjectManager: Handles multi-project switching and isolation.
- MemoryStore: RAG system for long-term narrative retrieval.
"""

from .orchestrator import Orchestrator
from .scanner import ProjectScanner
from .project_manager import ProjectManager
from .memory_store import MemoryStore

__all__ = ["Orchestrator", "ProjectScanner", "ProjectManager", "MemoryStore"]