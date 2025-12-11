import asyncio
import json
import logging
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
            self.scanner.scan()