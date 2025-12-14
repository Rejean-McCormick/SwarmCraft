"""
TextCraft AI Services Package
-----------------------------
The Brain: Contains the specialized AI logic modules.
These services are stateless but context-aware. They accept a 'project_root' 
path to locate the specific Story Bible, Matrix, and Memory for the active project.

Modules:
- client: Unified API Gateway (LLM Interface).
- architect: The Planner (Strategic Decision Maker).
- narrator: The Writer (Content Generator & RAG Consumer).
- editor: The Critic (Quality Assurance & Continuity Checker).

"""

from . import client
from . import architect
from . import narrator
from . import editor
from . import interviewer

__all__ = ["client", "architect", "narrator", "editor", "interviewer"]