import json
import os
import logging
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

# --- Internal Imports ---
from core.memory_store import MemoryStore

logger = logging.getLogger(__name__)

class ProjectScanner:
    """
    The Sensory System.
    Scans the file system to update the Matrix with real-time data.
    Also handles RAG ingestion for modified files.
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.data_dir = project_root / "data"
        self.root = self.data_dir / "manuscripts"
        self.matrix_path = self.data_dir / "matrix.json"
        self.conf_path = self.data_dir / "story_bible" / "project_conf.json"
        
        # Initialize Memory Store for RAG ingestion
        self.memory = MemoryStore(project_root)
        
        self._ensure_directories()

    def _ensure_directories(self):
        """Creates necessary directories if they don't exist."""
        self.root.mkdir(parents=True, exist_ok=True)
        if not self.matrix_path.parent.exists():
            self.matrix_path.parent.mkdir(parents=True, exist_ok=True)

    def _load_json(self, path: Path, default: Any = None) -> Any:
        """Safe JSON loader."""
        try:
            if not path.exists():
                return default if default is not None else {}
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load {path}: {e}")
            return default if default is not None else {}

    def _save_matrix(self, data: Dict[str, Any]):
        """Atomic write to matrix.json."""
        try:
            temp_path = self.matrix_path.with_suffix(".tmp")
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            temp_path.replace(self.matrix_path)
            logger.debug("Matrix updated successfully.")
        except Exception as e:
            logger.error(f"Failed to save Matrix: {e}")

    def _count_words(self, text: str) -> int:
        """Simple whitespace tokenizer."""
        return len(text.split())

    def _get_target_word_count(self) -> int:
        """Fetches the target word count from project config."""
        conf = self._load_json(self.conf_path)
        return conf.get("constraints", {}).get("chapter_target_word_count", 2000)

    def _determine_status(self, current_status: str, content: str, word_count: int, target_count: int) -> str:
        """
        Heuristic logic to infer chapter status.
        
        Rules:
        1. LOCKED chapters remain LOCKED (unless file is empty/deleted).
        2. < 50 words -> EMPTY.
        3. Contains '[TODO]' -> DRAFTING.
        4. > Target count -> REVIEW_READY.
        5. Else -> DRAFTING.
        """
        # Safety: If it was locked, but content was wiped, unlock it.
        if current_status == "LOCKED":
            if word_count < 50:
                return "EMPTY" # Physical reality overrides logical lock
            return "LOCKED"

        if word_count < 50:
            return "EMPTY"
        
        # Check for explicit agent markers
        if "[TODO]" in content or "