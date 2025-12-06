"""
Project Manager for Multi-Agent Swarm.

Handles multiple project workspaces with isolated data, scratch folders,
and memory databases.
"""

import json
import shutil
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Projects directory at repo root
PROJECTS_DIR = Path(__file__).parent.parent / "projects"


class Project:
    """Represents a single project workspace."""
    
    def __init__(self, name: str):
        self.name = name
        self.root = PROJECTS_DIR / name
        self.scratch_dir = self.root / "scratch"
        self.data_dir = self.root / "data"
        self.shared_dir = self.scratch_dir / "shared"
        self.config_file = self.root / "project.json"
    
    def ensure_exists(self):
        """Create project directories if they don't exist."""
        self.scratch_dir.mkdir(parents=True, exist_ok=True)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.shared_dir.mkdir(parents=True, exist_ok=True)
        
        # Create project config if it doesn't exist
        if not self.config_file.exists():
            self._save_config({
                "name": self.name,
                "created_at": datetime.now().isoformat(),
                "description": "",
            })
    
    def _save_config(self, config: Dict[str, Any]):
        """Save project configuration."""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
    
    def _load_config(self) -> Dict[str, Any]:
        """Load project configuration."""
        if self.config_file.exists():
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"name": self.name}

    @property
    def memory_db_path(self) -> Path:
        """Path to the project's memory database."""
        return self.data_dir / "memory.db"
    
    @property
    def chat_history_path(self) -> Path:
        """Path to the project's chat history."""
        return self.data_dir / "chat_history.json"
    
    @property
    def master_plan_path(self) -> Path:
        """Path to the project's master plan."""
        return self.shared_dir / "master_plan.md"
    
    @property
    def settings_path(self) -> Path:
        """Path to project-specific settings."""
        return self.data_dir / "settings.json"
    
    def get_info(self) -> Dict[str, Any]:
        """Get project information."""
        config = self._load_config()
        return {
            "name": self.name,
            "path": str(self.root),
            "created_at": config.get("created_at", "Unknown"),
            "description": config.get("description", ""),
            "has_master_plan": self.master_plan_path.exists(),
        }
    
    def set_description(self, description: str):
        """Set project description."""
        config = self._load_config()
        config["description"] = description
        self._save_config(config)


class ProjectManager:
    """Manages multiple project workspaces."""
    
    _instance = None
    _current_project: Optional[Project] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            PROJECTS_DIR.mkdir(exist_ok=True)
        return cls._instance
    
    def list_projects(self) -> List[Project]:
        """List all existing projects."""
        if not PROJECTS_DIR.exists():
            return []
        projects = []
        for d in PROJECTS_DIR.iterdir():
            if d.is_dir() and (d / "project.json").exists():
                projects.append(Project(d.name))
        return projects
    
    def project_exists(self, name: str) -> bool:
        """Check if a project exists."""
        return (PROJECTS_DIR / name / "project.json").exists()
    
    def create_project(self, name: str, description: str = "") -> Project:
        """Create a new project."""
        # Sanitize name
        safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in name)
        
        project = Project(safe_name)
        project.ensure_exists()
        
        if description:
            project.set_description(description)
        
        logger.info(f"Created project: {safe_name}")
        return project
    
    def load_project(self, name: str) -> Project:
        """Load an existing project."""
        project = Project(name)
        if not project.root.exists():
            raise ValueError(f"Project '{name}' does not exist")
        return project
    
    def delete_project(self, name: str, confirm: bool = False):
        """Delete a project and all its data."""
        if not confirm:
            raise ValueError("Must confirm deletion")
        
        project = Project(name)
        if project.root.exists():
            shutil.rmtree(project.root)
            logger.info(f"Deleted project: {name}")
    
    def set_current(self, project: Project):
        """Set the current active project."""
        self._current_project = project
        self._save_last_project(project.name)
        logger.info(f"Switched to project: {project.name}")
    
    @property
    def current(self) -> Optional[Project]:
        """Get the current active project."""
        return self._current_project
    
    def _save_last_project(self, name: str):
        """Save the last used project name."""
        config_file = PROJECTS_DIR / ".last_project"
        with open(config_file, 'w') as f:
            f.write(name)
    
    def get_last_project(self) -> Optional[str]:
        """Get the last used project name."""
        config_file = PROJECTS_DIR / ".last_project"
        if config_file.exists():
            return config_file.read_text().strip()
        return None


def get_project_manager() -> ProjectManager:
    """Get the singleton project manager."""
    return ProjectManager()


def get_current_project() -> Optional[Project]:
    """Get the current active project."""
    return get_project_manager().current
