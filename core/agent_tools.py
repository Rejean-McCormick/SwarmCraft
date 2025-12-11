import os
import aiofiles
import logging
import json
from pathlib import Path
from typing import Dict, Any, List, Optional

# Constants
# DATA_DIR removed in v3.0 to support Multi-Project Architecture
logger = logging.getLogger(__name__)

class SecurityError(Exception):
    """Raised when an agent attempts to access files outside the sandbox."""
    pass

def _resolve_path(path_str: str, project_root: Path) -> Path:
    """
    Securely resolves a path string relative to the active Project's DATA directory.
    Raises SecurityError if the resolved path escapes the sandbox.
    """
    # Define the sandbox dynamically based on the active project
    sandbox_root = (project_root / "data").resolve()

    try:
        # Prevent absolute paths or traversal attacks
        # Note: We strip leading slashes to treat everything as relative
        clean_path_str = path_str.lstrip("/\\")
        safe_path = (sandbox_root / clean_path_str).resolve()
        
        # Enforce sandbox containment
        if not str(safe_path).startswith(str(sandbox_root)):
            raise SecurityError(f"Access Denied: '{path_str}' resolves outside the project data directory.")
            
        return safe_path
    except Exception as e:
        logger.warning(f"Path resolution error for '{path_str}': {e}")
        raise SecurityError(f"Invalid path format: {path_str}")

def _format_result(status: str, data: Any, meta: Optional[Dict] = None) -> Dict[str, Any]:
    """Standardized response format for all tools."""
    return {
        "status": status,
        "data": data,
        "meta": meta or {}
    }

# --- File System Tools ---

async def read_file(path: str, project_root: Path) -> Dict[str, Any]:
    """
    Reads a file from the project sandbox and returns its content.
    Used by: All Agents.
    """
    try:
        target = _resolve_path(path, project_root)
        
        if not target.exists():
            return _format_result("error", f"File not found: {path}")
        
        if not target.is_file():
            return _format_result("error", f"Path is not a file: {path}")

        async with aiofiles.open(target, mode='r', encoding='utf-8') as f:
            content = await f.read()
            
        return _format_result("success", content, {"size": len(content)})

    except SecurityError as e:
        return _format_result("error", str(e))
    except Exception as e:
        logger.error(f"read_file failed for {path}: {e}")
        return _format_result("error", f"System error reading file: {str(e)}")

async def write_file(path: str, content: str, project_root: Path) -> Dict[str, Any]:
    """
    Writes content to a file, overwriting it completely. Creates dirs if needed.
    Used by: Architect (Plans), Narrator (Drafts).
    """
    try:
        target = _resolve_path(path, project_root)
        
        # Ensure parent directories exist
        target.parent.mkdir(parents=True, exist_ok=True)
        
        async with aiofiles.open(target, mode='w', encoding='utf-8') as f:
            await f.write(content)
            
        return _format_result("success", f"Successfully wrote {len(content)} characters to {path}.", {"bytes_written": len(content)})

    except SecurityError as e:
        return _format_result("error", str(e))
    except Exception as e:
        logger.error(f"write_file failed for {path}: {e}")
        return _format_result("error", f"System error writing file: {str(e)}")

async def edit_file(path: str, search_text: str, replace_text: str, project_root: Path) -> Dict[str, Any]:
    """
    Performs a strict find-and-replace operation.
    Used by: Editor.
    """
    try:
        target = _resolve_path(path, project_root)
        
        if not target.exists():
            return _format_result("error", f"File not found: {path}")

        # Read
        async with aiofiles.open(target, mode='r', encoding='utf-8') as f:
            original_content = await f.read()

        # Check existence
        if search_text not in original_content:
            return _format_result("error", "Search text not found in file. No changes made.")
        
        # Safety: We usually want to replace one specific instance to avoid accidents.
        count = original_content.count(search_text)
        if count > 1:
             return _format_result("error", f"Ambiguous edit: Search text found {count} times. Please provide context (more unique text) to isolate the edit.")

        # Modify
        new_content = original_content.replace(search_text, replace_text, 1)

        # Write
        async with aiofiles.open(target, mode='w', encoding='utf-8') as f:
            await f.write(new_content)

        return _format_result("success", "File updated successfully.")

    except SecurityError as e:
        return _format_result("error", str(e))
    except Exception as e:
        logger.error(f"edit_file failed for {path}: {e}")
        return _format_result("error", f"System error editing file: {str(e)}")

async def list_files(project_root: Path, directory: str = "manuscripts") -> Dict[str, Any]:
    """
    Lists files in a directory with basic metadata.
    Used by: Architect, Editor.
    """
    try:
        target = _resolve_path(directory, project_root)
        sandbox_root = (project_root / "data").resolve()
        
        if not target.exists() or not target.is_dir():
            return _format_result("error", f"Directory not found: {directory}")

        files = []
        for item in target.glob("*"):
            if item.is_file() and not item.name.startswith('.'):
                stat = item.stat()
                files.append({
                    "name": item.name,
                    # Return path relative to the project data root, not absolute system path
                    "path": str(item.relative_to(sandbox_root)),
                    "size": stat.st_size,
                    "modified": stat.st_mtime
                })
        
        return _format_result("success", files, {"count": len(files)})

    except SecurityError as e:
        return _format_result("error", str(e))
    except Exception as e:
        logger.error(f"list_files failed for {directory}: {e}")
        return _format_result("error", f"System error listing files: {str(e)}")

# --- Orchestration Tools ---

async def assign_task(target_agent: str, task_description: str, target_file: str) -> Dict[str, Any]:
    """
    Orchestration tool for The Architect to delegate work.
    This doesn't modify the filesystem, so it does NOT require project_root.
    """
    valid_agents = ["narrator", "editor", "architect"]
    if target_agent not in valid_agents:
        return _format_result("error", f"Invalid agent '{target_agent}'. Must be one of: {valid_agents}")

    # The Orchestrator will look for this 'success' status and specific data structure
    return _format_result("success", {
        "action_type": "delegate",
        "assigned_agent": target_agent,
        "context_notes": task_description,
        "target_file": target_file
    })