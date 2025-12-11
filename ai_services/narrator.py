import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

from ai_services import client
from core import agent_tools
from core.memory_store import MemoryStore

logger = logging.getLogger(__name__)

class NarratorError(Exception):
    """Custom exception for generation failures."""
    pass

def _load_json_config(path: Path) -> Dict[str, Any]:
    """Helper to safely load configuration files."""
    try:
        if not path.exists():
            logger.warning(f"Config file missing: {path}")
            return {}
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load config {path}: {e}")
        return {}

def _get_active_characters(context_notes: str, all_characters: Dict[str, Any]) -> str:
    """
    Filters the full character database to include only those mentioned in the prompt.
    """
    active_context = []
    for char_id, char_data in all_characters.items():
        names_to_check = [char_data.get("name", "")] + char_data.get("aliases", [])
        if any(name.lower() in context_notes.lower() for name in names_to_check if name):
            active_context.append(json.dumps(char_data, indent=2))
    
    if not active_context:
        return "No specific characters detected in instructions. Use general archetype knowledge."
    
    return "\n\n".join(active_context)

def _get_active_location(context_notes: str, all_locations: Dict[str, Any]) -> str:
    """Similar to character filtering, but for settings."""
    for loc_id, loc_data in all_locations.items():
        if loc_data.get("name", "").lower() in context_notes.lower():
            return json.dumps(loc_data, indent=2)
    return "Location context not specified."

def _hydrate_prompt(template: str, project_conf: Dict[str, Any], char_context: str, rag_context: str) -> str:
    """Injects dynamic variables (including RAG memory) into the system prompt."""
    replacements = {
        "{{title}}": project_conf.get("meta", {}).get("title", "Untitled"),
        "{{genre}}": project_conf.get("style", {}).get("genre", "Fiction"),
        "{{tone}}": project_conf.get("style", {}).get("tone", "Standard"),
        "{{style_guide}}": json.dumps(project_conf.get("style", {}), indent=2),
        "{{character_context}}": char_context,
        "{{rag_context}}": rag_context or "No relevant long-term memory retrieved."
    }
    
    hydrated = template
    for key, value in replacements.items():
        hydrated = hydrated.replace(key, str(value))
    
    return hydrated

# --- Main Service Logic ---

async def execute(task_payload: Dict[str, Any], project_root: Path, memory_store: Optional[MemoryStore] = None) -> Dict[str, Any]:
    """
    Main entry point for the Narrator Service.
    
    Args:
        task_payload: From Architect (target_file, context_notes).
        project_root: The active project directory.
        memory_store: RAG interface (optional).
        
    Returns:
        Dict: Status report (files modified, cost).
    """
    target_file = task_payload.get("target_file")
    instructions = task_payload.get("context_notes", "")
    
    logger.info(f"Narrator Service: Starting job for {target_file}")

    # 1. Calculate Paths
    bible_dir = project_root / "data" / "story_bible"
    
    # 2. Load Configurations
    personas = _load_json_config(bible_dir / "personas.json")
    project_conf = _load_json_config(bible_dir / "project_conf.json")
    characters = _load_json_config(bible_dir / "characters.json")
    locations = _load_json_config(bible_dir / "locations.json")
    
    narrator_config = personas.get("narrator")
    if not narrator_config:
        raise NarratorError("Narrator persona definition missing.")

    # 3. Build Context
    char_context = _get_active_characters(instructions, characters)
    loc_context = _get_active_location(instructions, locations)
    
    # 3b. RAG Retrieval
    rag_context = ""
    if memory_store:
        # Query memory for relevant past events based on the instructions
        query_text = f"{instructions} {char_context}"[:500] # Truncate query
        rag_context = memory_store.query(query_text)
        logger.info(f"Narrator RAG: Retrieved {len(rag_context)} chars of context.")

    # 4. Hydrate System Prompt
    system_prompt_template = narrator_config.get("system_prompt", "")
    system_prompt = _hydrate_prompt(system_prompt_template, project_conf, char_context, rag_context)

    # 5. Check for Existing Content (Continuity)
    current_content = ""
    read_path = f"manuscripts/{target_file}"
    read_result = await agent_tools.read_file(read_path, project_root)
    if read_result["status"] == "success":
        current_content = read_result["data"]

    user_message = f"""
    TASK: Write/Continue the file '{target_file}'.
    
    INSTRUCTIONS FROM ARCHITECT:
    {instructions}
    
    SETTING CONTEXT:
    {loc_context}
    
    EXISTING CONTENT (The Story So Far):
    {current_content[-2000:] if current_content else "(New File)"}
    
    REQUIREMENTS:
    1. Use the 'write_file' tool to save the output.
    2. Do NOT output the text in the chat. Use the tool.
    3. Adhere strictly to the character voices and setting details provided.
    """

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message}
    ]

    # 6. Prepare Tools
    tools_schema = [
        {
            "type": "function",
            "function": {
                "name": "write_file",
                "description": "Writes the generated story content to the target manuscript file.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": f"Must be 'manuscripts/{target_file}'"
                        },
                        "content": {
                            "type": "string",
                            "description": "The full markdown content of the chapter/scene."
                        }
                    },
                    "required": ["path", "content"]
                }
            }
        }
    ]

    # 7. Call The Brain
    try:
        response = await client.generate(
            messages=messages,
            model=narrator_config.get("model", "gpt-4"),
            temperature=narrator_config.get("temperature", 0.9),
            max_tokens=narrator_config.get("max_tokens", 4000),
            tools=tools_schema
        )
    except Exception as e:
        logger.error(f"Narrator Brain Failure: {e}")
        return {"status": "error", "message": str(e)}

    # 8. Handle Tool Execution
    if response["status"] == "success":
        data = response["data"]
        tool_calls = data.get("tool_calls", [])
        
        if not tool_calls:
            logger.warning("Narrator produced text but called no tools.")
            return {"status": "warning", "message": "No file written.", "raw_output": data.get("content")}

        results = []
        for tool in tool_calls:
            if tool["name"] == "write_file":
                args = tool["arguments"]
                # Enforce path security - overwrite hallucinated path
                safe_path = f"manuscripts/{target_file}"
                
                logger.info(f"Narrator writing to {safe_path}...")
                # Pass project_root to tool for secure sandboxed writing
                result = await agent_tools.write_file(safe_path, args["content"], project_root)
                results.append(result)

        return {
            "status": "success",
            "modified_files": [target_file],
            "tool_results": results,
            "cost_metrics": response.get("usage", {})
        }
    else:
        return {"status": "error", "message": "Brain returned failure status."}