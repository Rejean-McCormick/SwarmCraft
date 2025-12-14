import asyncio
import json
import logging
import os
import time
from pathlib import Path
from typing import Dict, Any, Optional

# --- Internal Imports ---
from core.scanner import ProjectScanner
from core.project_manager import ProjectManager
from core.memory_store import MemoryStore
from ai_services import architect, narrator, editor

# --- Configuration ---
MAX_CONSECUTIVE_ERRORS = 3
LOOP_DELAY_SECONDS = 2  # Breathing room between cycles
IDLE_DELAY_SECONDS = 10  # When there is no actionable work, avoid spamming model calls
AUTO_CONTINUE_DRAFTING = os.getenv("AUTO_CONTINUE_DRAFTING", "0").strip().lower() not in {"0", "false", "no", "off"}

logger = logging.getLogger(__name__)

class Orchestrator:
    """
    The Central Execution Loop.
    Manages the lifecycle of the active project by coordinating:
    1. Sensory Input (Scanner)
    2. User Control (Control Signals)
    3. Strategic Planning (Architect)
    4. Task Execution (Narrator/Editor)
    """

    def __init__(self, project_manager: ProjectManager):
        self.pm = project_manager
        self.error_count = 0
        self.is_running = False
        
        # Load the last active project or default
        project_id = self.pm.get_last_active_project()
        if not project_id:
            logger.info("No active project found. Creating default...")
            self.pm.create_project("default_project", "Untitled Story")
            project_id = "default_project"
            self.pm.set_active_project(project_id)
        
        self.project_root = self.pm.get_project_path(project_id)
        if not self.project_root:
             raise ValueError(f"CRITICAL: Could not resolve path for project {project_id}")

        logger.info(f"Orchestrator bound to project: {project_id} at {self.project_root}")
        
        # Initialize Components with Project Scope
        self.scanner = ProjectScanner(self.project_root)
        self.memory_store = MemoryStore(self.project_root)
        
        self.matrix_path = self.project_root / "data" / "matrix.json"
        self.control_path = self.project_root / "data" / "control.json"

    def _load_matrix(self) -> Dict[str, Any]:
        """Loads the freshest state of the Matrix from disk."""
        try:
            if not self.matrix_path.exists():
                logger.warning("Matrix not found. Triggering initial scan.")
                return self.scanner.scan()
            
            with open(self.matrix_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load Matrix: {e}")
            return {}

    def _update_active_task(self, agent: Optional[str], target: Optional[str], action: Optional[str], chars: Optional[list] = None):
        """Updates the 'active_task' field in Matrix to persist current intent."""
        try:
            matrix = self._load_matrix()
            matrix["active_task"] = {
                "assigned_to": agent,
                "target": target,
                "action": action,
                "active_characters": chars or [],
                "timestamp": time.time()
            }
            with open(self.matrix_path, 'w', encoding='utf-8') as f:
                json.dump(matrix, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to update active task: {e}")

    async def _check_control_signals(self) -> Optional[Dict]:
        """Reads data/control.json to check for PAUSE/STOP or Overrides."""
        if not self.control_path.exists():
            return None
            
        try:
            with open(self.control_path, "r") as f:
                signals = json.load(f)

            # 1. Handle System Status
            status = signals.get("system_status", "RUNNING")
            if status == "STOP":
                logger.info("Control Signal: STOP received.")
                self.stop()
                return None
            
            elif status == "PAUSED":
                logger.info("System PAUSED by User. Waiting...")
                while status == "PAUSED":
                    await asyncio.sleep(1)
                    # Re-read file
                    with open(self.control_path, "r") as f:
                        status = json.load(f).get("system_status", "RUNNING")
                logger.info("System RESUMED.")

            # 2. Handle Architect Override
            override = signals.get("architect_override", {})
            if override.get("active"):
                return override
                
        except Exception as e:
            logger.error(f"Control Signal Read Error: {e}")
        
        return None

    async def _reset_override_signal(self):
        """Acknowledges the override by setting active=False in control.json."""
        try:
            with open(self.control_path, "r") as f:
                data = json.load(f)
            
            data["architect_override"]["active"] = False
            data["architect_override"]["instruction"] = None
            data["architect_override"]["force_target"] = None
            
            with open(self.control_path, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to reset override signal: {e}")

    async def start(self):
        """Starts the infinite orchestration loop."""
        self.is_running = True
        logger.info("Orchestrator: Engine Online. Entering main loop.")

        while self.is_running:
            try:
                await self.step()
                self.error_count = 0
                await asyncio.sleep(LOOP_DELAY_SECONDS)

            except Exception as e:
                self.error_count += 1
                logger.critical(f"Orchestrator Loop Critical Failure ({self.error_count}/{MAX_CONSECUTIVE_ERRORS}): {e}", exc_info=True)
                
                if self.error_count >= MAX_CONSECUTIVE_ERRORS:
                    logger.fatal("Max errors reached. Shutting down system safety.")
                    self.stop()
                    break
                
                await asyncio.sleep(5)

    def stop(self):
        """Signals the loop to terminate gracefully."""
        self.is_running = False
        logger.info("Orchestrator: Shutdown signal received.")

    def _clear_continuity_flag(self, target_file: str):
        """After a narrator fix pass, clear continuity_check so the chapter can be re-reviewed."""
        try:
            matrix = self._load_matrix()
            content_map = matrix.get("content", {})
            if not isinstance(content_map, dict) or not target_file:
                return

            file_id = None
            for fid, entry in content_map.items():
                if not isinstance(entry, dict):
                    continue
                path = entry.get("path", "")
                if target_file in path or f"{fid}_" in target_file or target_file.startswith(fid):
                    file_id = fid
                    break

            if not file_id:
                return

            entry = content_map.get(file_id)
            if not isinstance(entry, dict):
                return

            if entry.get("continuity_check") == "FAIL":
                entry["continuity_check"] = "PENDING"
                with open(self.matrix_path, 'w', encoding='utf-8') as f:
                    json.dump(matrix, f, indent=2)
                logger.info(f"Cleared continuity_check FAIL -> PENDING for {file_id} after narrator fix.")
        except Exception as e:
            logger.error(f"Failed to clear continuity flag: {e}")

    async def step(self):
        """
        Executes a single atomic cycle of the TextCraft architecture.
        """
        
        # --- PHASE 0: CONTROL CHECK ---
        override_signal = await self._check_control_signals()
        if not self.is_running: return 

        # --- PHASE 1: SCAN ---
        logger.info("--- [Phase 1: SCAN] ---")
        matrix = self.scanner.scan()
        
        if matrix.get("meta", {}).get("project_status") == "COMPLETE":
            logger.info("Project marked COMPLETE. Orchestrator standing by.")
            await asyncio.sleep(10)
            return

        # If there's no override and nothing actionable, don't call the Architect every loop.
        if not override_signal:
            content_map = matrix.get("content")
            if isinstance(content_map, dict) and content_map:
                has_actionable = False
                for entry in content_map.values():
                    if not isinstance(entry, dict):
                        continue
                    status = entry.get("status")
                    continuity = entry.get("continuity_check")
                    if status in {"EMPTY", "REVIEW_READY"} or continuity == "FAIL" or (AUTO_CONTINUE_DRAFTING and status == "DRAFTING"):
                        has_actionable = True
                        break

                if not has_actionable:
                    # Check if there are any DRAFTING chapters that need to reach word count
                    drafting_chapters = [
                        fid for fid, entry in content_map.items()
                        if isinstance(entry, dict) and entry.get("status") == "DRAFTING"
                    ]
                    if drafting_chapters:
                        # Auto-continue drafting chapters instead of idling
                        has_actionable = True
                        logger.info(f"Auto-continuing DRAFTING chapters: {drafting_chapters}")
                    else:
                        logger.info("No actionable work detected. Idling without Architect call. (Tip: in Director Console, type an instruction like 'override continue into chapter 2', or set a file with 'target ch02_RisingAction.md', then 'start'.)")
                        await asyncio.sleep(IDLE_DELAY_SECONDS)
                        return

        # --- PHASE 2: PLAN ---
        logger.info("--- [Phase 2: PLAN] ---")
        try:
            # Pass override signal to Architect
            decision = await architect.plan_next_step(matrix, self.project_root, override_signal)
            
            # If we used an override, reset it now
            if override_signal:
                await self._reset_override_signal()
                
        except Exception as e:
            logger.error(f"Architect Service failed: {e}")
            return

        action = decision.get("action_type")
        target = decision.get("target_file")
        agent_role = decision.get("assigned_agent")
        
        logger.info(f"Architect Decision: {action.upper()} {target} via {agent_role}")

        if action == "stop":
            logger.info("Architect requested stop. Pausing loop.")
            self.stop()
            return
        
        if action == "wait":
             logger.info("Architect requested wait.")
             await asyncio.sleep(IDLE_DELAY_SECONDS)
             return

        # --- PHASE 3: DISPATCH ---
        logger.info("--- [Phase 3: DISPATCH] ---")
        
        # Extract implied characters for UI context (heuristic)
        notes = decision.get("context_notes", "")
        # This update helps the Dashboard show who is "in the scene"
        self._update_active_task(agent_role, target, action, chars=[]) 

        result = {"status": "error", "message": "No agent assigned"}
        
        try:
            if agent_role == "narrator":
                result = await narrator.execute(decision, self.project_root, self.memory_store)
                
            elif agent_role == "editor":
                result = await editor.execute(decision, self.project_root, self.memory_store)
                
            elif agent_role == "architect":
                logger.info("Architect assigned self-task.")
                result = {"status": "skipped", "message": "Self-assignment ignored."}
                
            else:
                logger.error(f"Unknown agent role: {agent_role}")
                result = {"status": "error", "message": f"Unknown agent: {agent_role}"}

        except Exception as e:
            logger.error(f"Service Execution Failed: {e}", exc_info=True)
            result = {"status": "error", "message": str(e)}

        # --- PHASE 4: UPDATE ---
        logger.info("--- [Phase 4: UPDATE] ---")
        logger.info(f"Result: {result.get('status')}")
        
        self._update_active_task(None, None, None)
        
        if result.get("status") == "success":
            # Handle Editor verdict: update matrix status based on pass/fail
            if agent_role == "editor":
                verdict = result.get("verdict", "FAIL")
                editor_notes = result.get("editor_notes", [])
                self._apply_editor_verdict(target, verdict, editor_notes)

            # If narrator performed an edit/fix pass, clear FAIL so the chapter can move back to review.
            if agent_role == "narrator" and action == "edit" and target:
                self._clear_continuity_flag(target)
            
            # Rescan to pick up file changes
            matrix = self.scanner.scan()
            
            # Check if we should auto-progress to next chapter
            self._maybe_create_next_chapter(matrix)

    def _apply_editor_verdict(self, target_file: str, verdict: str, notes: list):
        """Updates the matrix based on editor's verdict."""
        try:
            matrix = self._load_matrix()
            content_map = matrix.get("content", {})
            
            # Find the chapter entry by filename
            file_id = None
            for fid, entry in content_map.items():
                if isinstance(entry, dict):
                    path = entry.get("path", "")
                    if target_file in path or f"{fid}_" in target_file or target_file.startswith(fid):
                        file_id = fid
                        break
            
            if not file_id:
                logger.warning(f"Could not find matrix entry for {target_file}")
                return
            
            entry = content_map[file_id]
            if verdict == "PASS":
                entry["status"] = "LOCKED"
                entry["continuity_check"] = "PASS"
                logger.info(f"Chapter {file_id} LOCKED after passing editor review.")
            else:
                entry["continuity_check"] = "FAIL"
                entry["editor_notes"] = notes
                logger.info(f"Chapter {file_id} marked FAIL with {len(notes)} notes.")
            
            with open(self.matrix_path, 'w', encoding='utf-8') as f:
                json.dump(matrix, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to apply editor verdict: {e}")

    def _maybe_create_next_chapter(self, matrix: Dict[str, Any]):
        """Creates the next chapter if all existing chapters are LOCKED."""
        try:
            content_map = matrix.get("content", {})
            if not content_map:
                return
            
            # Check if all chapters are LOCKED
            all_locked = all(
                isinstance(entry, dict) and entry.get("status") == "LOCKED"
                for entry in content_map.values()
            )
            
            if not all_locked:
                return
            
            # Find the highest chapter number
            max_chapter = 0
            for file_id in content_map.keys():
                # Extract chapter number from IDs like "ch01", "ch02", etc.
                if file_id.startswith("ch"):
                    try:
                        num = int(file_id[2:].split("_")[0])
                        max_chapter = max(max_chapter, num)
                    except ValueError:
                        pass
            
            # Load story_brief to check if we should continue
            story_brief_path = self.project_root / "data" / "story_bible" / "story_brief.json"
            story_brief = {}
            if story_brief_path.exists():
                with open(story_brief_path, 'r', encoding='utf-8') as f:
                    story_brief = json.load(f)
            
            # Get expected chapter count from structure or default to 10
            structure = story_brief.get("structure", {})
            chapters = structure.get("chapters", [])
            acts = structure.get("acts", [])
            
            # If no explicit chapters, derive from acts/beats
            if not chapters and acts:
                chapters = []
                for act in acts:
                    if isinstance(act, dict):
                        act_name = act.get("name", "Act")
                        beats = act.get("beats", [])
                        for i, beat in enumerate(beats):
                            if isinstance(beat, str):
                                chapters.append({"title": f"{act_name} - {beat[:40]}", "summary": beat})
                            elif isinstance(beat, dict):
                                chapters.append(beat)
            
            expected_chapters = len(chapters) if chapters else 10
            
            if max_chapter >= expected_chapters:
                logger.info(f"All {max_chapter} chapters complete. Project may be finished.")
                return
            
            # Create next chapter
            next_num = max_chapter + 1
            next_id = f"ch{next_num:02d}"
            
            # Try to get chapter title from story_brief structure
            chapter_title = f"Chapter {next_num}"
            if chapters and next_num <= len(chapters):
                chapter_info = chapters[next_num - 1]
                if isinstance(chapter_info, dict):
                    chapter_title = chapter_info.get("title", chapter_title)
                elif isinstance(chapter_info, str):
                    chapter_title = chapter_info
            
            # Sanitize title for filename
            safe_title = "".join(c if c.isalnum() or c in " _-" else "" for c in chapter_title)
            safe_title = safe_title.replace(" ", "_")[:30]
            
            next_filename = f"{next_id}_{safe_title}.md"
            next_path = self.project_root / "data" / "manuscripts" / next_filename
            
            if not next_path.exists():
                next_path.parent.mkdir(parents=True, exist_ok=True)
                with open(next_path, 'w', encoding='utf-8') as f:
                    f.write(f"# Chapter {next_num}: {chapter_title}\n\n")
                logger.info(f"Created next chapter: {next_filename}")
            
        except Exception as e:
            logger.error(f"Failed to create next chapter: {e}")
