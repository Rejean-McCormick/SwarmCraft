import json
import logging
import re
from pathlib import Path
from typing import Dict, Any, Optional

from ai_services import client

logger = logging.getLogger(__name__)

class ArchitectError(Exception):
    """Custom exception for planning failures."""
    pass

def _load_json_config(path: Path) -> Dict[str, Any]:
    """Helper to safely load configuration files."""
    try:
        if not path.exists():
            logger.error(f"Config file missing: {path}")
            return {}
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load config {path}: {e}")
        return {}

def _hydrate_prompt(template: str, project_conf: Dict[str, Any], override_instruction: Optional[str] = None) -> str:
    """Injects project variables and User Overrides into the system prompt."""
    replacements = {
        "{{title}}": project_conf.get("meta", {}).get("title", "Untitled Project"),
        "{{genre}}": project_conf.get("style", {}).get("genre", "General Fiction"),
        "{{style_guide}}": json.dumps(project_conf.get("style", {}), indent=2)
    }
    
    hydrated = template
    for key, value in replacements.items():
        hydrated = hydrated.replace(key, str(value))
    
    # Inject Director Override if present (God Mode)
    if override_instruction:
        hydrated += f"\n\n[DIRECTOR OVERRIDE]: The User has issued a direct command. You MUST prioritize this instruction over standard logic: {override_instruction}"
    
    return hydrated

def _clean_json_response(content: str) -> str:
    """Removes Markdown code blocks (```json ... ```) often added by LLMs."""
    content = content.strip()
    if content.startswith("```"):
        lines = content.split('\n')
        # Robustly find start/end of json block
        if len(lines) >= 2:
            return "\n".join(lines[1:-1])
    return content

# --- Main Service Logic ---

async def plan_next_step(matrix_data: Dict[str, Any], project_root: Path, override_payload: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Analyzes the Matrix state and returns a DecisionPayload.
    
    Args:
        matrix_data: The current state of the project from matrix.json.
        project_root: The active project directory.
        override_payload: Optional command from control.json (User Override).
        
    Returns:
        Dict: A validated Decision Payload (action_type, target_file, etc.).
    """
    logger.info("Architect Service: Analyzing Matrix...")

    # 1. Calculate Paths Dynamically
    bible_dir = project_root / "data" / "story_bible"
    personas_path = bible_dir / "personas.json"
    project_conf_path = bible_dir / "project_conf.json"

    # 2. Load Configurations
    personas = _load_json_config(personas_path)
    project_conf = _load_json_config(project_conf_path)
    
    architect_config = personas.get("architect")
    if not architect_config:
        # Fallback config if file is broken
        architect_config = {"model": "gpt-4-turbo", "system_prompt": "You are the Architect."}

    # 3. Check for Forced Target (Override)
    # If the user forced a specific file (e.g., "ch03"), we skip logic and just build a plan for that.
    forced_target = None
    override_instruction = None
    
    if override_payload and override_payload.get("active"):
        forced_target = override_payload.get("force_target")
        override_instruction = override_payload.get("instruction")
        logger.info(f"Architect: Processing Override -> {override_instruction}")

    # 4. Build Context & Prompts
    system_prompt_template = architect_config.get("system_prompt", "")
    system_prompt = _hydrate_prompt(system_prompt_template, project_conf, override_instruction)

    user_message = f"""
    Here is the current Project State (The Matrix):
    {json.dumps(matrix_data, indent=2)}

    Analyze the 'content' list.
    1. Identify files with status 'EMPTY' or 'DRAFTING' -> Assign to 'narrator' to 'generate'.
    2. Identify files with status 'REVIEW_READY' -> Assign to 'editor' to 'edit'.
    3. Identify files with 'continuity_check': 'FAIL' -> Assign to 'narrator' to 'fix'.
    4. If a file is missing based on standard novel structure, create a plan to write it.
    """
    
    if forced_target:
        user_message += f"\n\n[PRIORITY]: You MUST generate a plan for file ID '{forced_target}' regardless of its status."

    user_message += "\nReturn ONLY the JSON Decision Payload."

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message}
    ]

    # 5. Call The Brain
    try:
        response = await client.generate(
            messages=messages,
            model=architect_config.get("model", "gpt-4-turbo"),
            temperature=0.3, # Low temp for logic
            max_tokens=1000
        )
    except Exception as e:
        logger.error(f"Architect Brain Failure: {e}")
        return {"action_type": "wait", "reason": "Brain connection error"}

    if response["status"] != "success":
        logger.error(f"Architect API Error: {response}")
        return {"action_type": "wait", "reason": "API returned error"}

    # 6. Parse & Validate Decision
    try:
        raw_content = response["data"]["content"]
        if not raw_content:
            raise ArchitectError("Architect returned empty content.")

        clean_content = _clean_json_response(raw_content)
        decision = json.loads(clean_content)
        
        # Basic Schema Validation
        required_keys = ["action_type", "target_file", "assigned_agent"]
        for key in required_keys:
            if key not in decision:
                raise ArchitectError(f"Missing key '{key}' in Decision Payload")

        logger.info(f"Architect Decision: {decision['action_type']} -> {decision['target_file']}")
        return decision

    except json.JSONDecodeError:
        logger.error(f"Architect Malformed JSON: {raw_content}")
        return {"action_type": "wait", "reason": "Architect produced invalid JSON"}
    except Exception as e:
        logger.exception(f"Architect Logic Failure: {e}")
        return {"action_type": "wait", "reason": str(e)}