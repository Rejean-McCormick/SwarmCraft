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
        if "[TODO]" in content or "```" in content:
            return "DRAFTING"

        if word_count >= target_count:
            return "REVIEW_READY"

        return "DRAFTING"

    def scan(self) -> Dict[str, Any]:
        matrix = self._load_json(
            self.matrix_path,
            default={
                "meta": {"project_status": "ACTIVE", "last_scan_timestamp": "", "version": "2.1"},
                "metrics": {"total_word_count": 0, "chapter_count": 0, "narrative_integrity_score": 100},
                "content": {},
                "active_task": {}
            }
        )

        if not isinstance(matrix, dict):
            matrix = {}

        matrix.setdefault("meta", {})
        matrix.setdefault("metrics", {})
        matrix.setdefault("content", {})
        matrix.setdefault("active_task", {})

        content_map: Dict[str, Any] = matrix.get("content", {})
        if not isinstance(content_map, dict):
            content_map = {}
            matrix["content"] = content_map

        target_count = self._get_target_word_count()

        found_ids = set()
        total_word_count = 0

        for file_path in sorted(self.root.rglob("*.md")):
            try:
                file_id = file_path.stem.split("_")[0]
                title_part = file_path.stem[len(file_id):].lstrip("_")
                title = title_part.replace("_", " ") if title_part else file_id

                rel_path = file_path.relative_to(self.project_root).as_posix()
                last_modified = datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()

                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                word_count = self._count_words(content)
                found_ids.add(file_id)

                existing = content_map.get(file_id, {})
                if not isinstance(existing, dict):
                    existing = {}

                current_status = existing.get("status", "DRAFTING")
                status = self._determine_status(current_status, content, word_count, target_count)

                continuity_check = existing.get("continuity_check", "PENDING")
                editor_notes = existing.get("editor_notes", [])
                if not isinstance(editor_notes, list):
                    editor_notes = []

                prev_last_modified = existing.get("last_modified")
                content_map[file_id] = {
                    "title": title,
                    "path": rel_path,
                    "word_count": word_count,
                    "status": status,
                    "continuity_check": continuity_check,
                    "last_modified": last_modified,
                    "editor_notes": editor_notes
                }

                if prev_last_modified != last_modified:
                    try:
                        self.memory.ingest_manuscript(file_path, content)
                    except Exception:
                        pass

                total_word_count += word_count

            except Exception as e:
                logger.error(f"Scan failed for file {file_path}: {e}")

        for file_id, entry in list(content_map.items()):
            if file_id in found_ids:
                continue
            if not isinstance(entry, dict):
                continue

            current_status = entry.get("status", "DRAFTING")
            status = self._determine_status(current_status, "", 0, target_count)
            entry["word_count"] = 0
            entry["status"] = status
            if "continuity_check" not in entry:
                entry["continuity_check"] = "PENDING"
            if "editor_notes" not in entry or not isinstance(entry.get("editor_notes"), list):
                entry["editor_notes"] = []

        matrix["metrics"]["total_word_count"] = total_word_count
        matrix["metrics"]["chapter_count"] = len(content_map)
        matrix["meta"]["last_scan_timestamp"] = datetime.now().isoformat()

        if content_map and all(isinstance(v, dict) and v.get("status") == "LOCKED" for v in content_map.values()):
            matrix["meta"]["project_status"] = "COMPLETE"
        else:
            matrix["meta"].setdefault("project_status", "ACTIVE")
            if matrix["meta"].get("project_status") != "PAUSED":
                matrix["meta"]["project_status"] = "ACTIVE"

        self._save_matrix(matrix)
        return matrix