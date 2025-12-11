import json
import logging
import shutil
from pathlib import Path
from typing import List, Optional, Dict, Any

# --- Constants ---
DEFAULT_PROJECTS_ROOT = Path("projects")
TEMPLATE_DIR = Path("templates") # Optional, for future use

logger = logging.getLogger(__name__)

class ProjectManager:
    """
    The Librarian.
    Manages the lifecycle of project directories.
    """

    def __init__(self, root_dir: Path = DEFAULT_PROJECTS_ROOT):
        self.root = root_dir
        self.state_file = self.root / ".last_project"
        self._ensure_root()

    def _ensure_root(self):
        """Creates the projects root folder if missing."""
        self.root.mkdir(parents=True, exist_ok=True)

    def list_projects(self) -> List[str]:
        """Returns a list of valid project IDs (folder names)."""
        if not self.root.exists():
            return []
        
        projects = []
        for item in self.root.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                # Basic validation: does it look like a TextCraft project?
                if (item / "data" / "matrix.json").exists():
                    projects.append(item.name)
        return sorted(projects)

    def get_last_active_project(self) -> Optional[str]:
        """Reads the persistent state to find the last active project ID."""
        try:
            if self.state_file.exists():
                return self.state_file.read_text(encoding="utf-8").strip()
        except Exception as e:
            logger.warning(f"Failed to read last project state: {e}")
        return None

    def set_active_project(self, project_id: str) -> None:
        """Persists the currently active project ID."""
        try:
            self.state_file.write_text(project_id, encoding="utf-8")
        except Exception as e:
            logger.error(f"Failed to save active project state: {e}")

    def get_project_path(self, project_id: str) -> Optional[Path]:
        """Resolves the absolute path for a project ID."""
        target = self.root / project_id
        if target.exists() and target.is_dir():
            return target.resolve()
        return None

    def create_project(self, project_id: str, title: str = "Untitled Project") -> bool:
        """
        Scaffolds a new project directory structure with default files.
        Returns True if successful, False if project already exists.
        """
        target_dir = self.root / project_id
        if target_dir.exists():
            logger.warning(f"Project '{project_id}' already exists.")
            return False

        try:
            logger.info(f"Scaffolding new project: {project_id}...")
            
            # 1. Create Directory Hierarchy
            data_dir = target_dir / "data"
            bible_dir = data_dir / "story_bible"
            manu_dir = data_dir / "manuscripts"
            
            manu_dir.mkdir(parents=True, exist_ok=True)
            bible_dir.mkdir(parents=True, exist_ok=True)

            # 2. Create Default Matrix (The State)
            matrix = {
                "meta": {
                    "title": title,
                    "project_status": "ACTIVE",
                    "version": "1.0",
                    "created_at": "now" # In real app, use datetime
                },
                "metrics": {
                    "total_word_count": 0,
                    "chapter_count": 0,
                    "narrative_integrity_score": 100
                },
                "content": {},
                "active_task": {}
            }
            self._write_json(data_dir / "matrix.json", matrix)

            # 3. Create Default Control (The Bridge)
            control = {
                "system_status": "RUNNING",
                "architect_override": {"active": False, "instruction": None, "force_target": None},
                "runtime_settings": {"global_temperature": 0.7, "model_override": None}
            }
            self._write_json(data_dir / "control.json", control)

            # 4. Create Default Story Bible (The Knowledge)
            self._scaffold_bible(bible_dir, title)

            # 5. Create Initial Chapter
            initial_chapter = f"# Chapter 1: The Start\n\n[TODO: Write the opening hook for {title}]"
            with open(manu_dir / "ch01_Start.md", "w", encoding="utf-8") as f:
                f.write(initial_chapter)

            logger.info(f"Project '{project_id}' created successfully.")
            return True

        except Exception as e:
            logger.error(f"Failed to create project {project_id}: {e}")
            # Cleanup partial creation
            if target_dir.exists():
                shutil.rmtree(target_dir)
            return False

    def _scaffold_bible(self, bible_dir: Path, title: str):
        """Helper to populate the Story Bible with default templates."""
        
        # Project Config
        conf = {
            "meta": {"title": title, "author": "AI & User"},
            "style": {"genre": "General Fiction", "tone": "Balanced", "tense": "Past"},
            "constraints": {"chapter_target_word_count": 2000, "forbidden_tropes": ["Deus Ex Machina"]}
        }
        self._write_json(bible_dir / "project_conf.json", conf)

        # Personas (System Prompts)
        personas = {
            "architect": {
                "model": "gpt-4-turbo",
                "system_prompt": "You are the Architect. You plan the novel structure based on {{genre}} and {{style_guide}}."
            },
            "narrator": {
                "model": "gpt-4-turbo", 
                "temperature": 0.8,
                "system_prompt": "You are the Narrator. You write vivid prose for {{title}} in a {{tone}} tone."
            },
            "editor": {
                "model": "gpt-4-turbo",
                "system_prompt": "You are the Editor. You check for continuity errors and style violations."
            }
        }
        self._write_json(bible_dir / "personas.json", personas)

        # Stubs for other files
        self._write_json(bible_dir / "characters.json", {})
        self._write_json(bible_dir / "locations.json", {})
        self._write_json(bible_dir / "timeline.json", {"events": []})

    def _write_json(self, path: Path, data: Dict[str, Any]):
        """Helper for atomic JSON writing."""
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)