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

def _hydrate_prompt(template: str, project_conf: Dict[str, Any], story_brief: Dict[str, Any], char_context: str, rag_context: str) -> str:
    """Injects dynamic variables (including RAG memory) into the system prompt."""
    replacements = {
        "{{title}}": project_conf.get("meta", {}).get("title", "Untitled"),
        "{{genre}}": project_conf.get("style", {}).get("genre", "Fiction"),
        "{{tone}}": project_conf.get("style", {}).get("tone", "Standard"),
        "{{style_guide}}": json.dumps(project_conf.get("style", {}), indent=2),
        "{{story_brief}}": json.dumps(story_brief or {}, indent=2),
        "{{character_context}}": char_context,
        "{{rag_context}}": rag_context or "No relevant long-term memory retrieved."
    }
    
    hydrated = template
    for key, value in replacements.items():
        hydrated = hydrated.replace(key, str(value))

    if "{{story_brief}}" not in template:
        hydrated += f"\n\nSTORY BRIEF (Source of Truth):\n{replacements['{{story_brief}}']}"
    
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
    action_type = (task_payload.get("action_type") or "").strip().lower()
    
    logger.info(f"Narrator Service: Starting job for {target_file}")

    # 1. Calculate Paths
    bible_dir = project_root / "data" / "story_bible"
    
    # 2. Load Configurations
    personas = _load_json_config(bible_dir / "personas.json")
    project_conf = _load_json_config(bible_dir / "project_conf.json")
    story_brief = _load_json_config(bible_dir / "story_brief.json")
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
    system_prompt = _hydrate_prompt(system_prompt_template, project_conf, story_brief, char_context, rag_context)

    # 5. Check for Existing Content (Continuity)
    current_content = ""
    read_path = f"manuscripts/{target_file}"
    read_result = await agent_tools.read_file(read_path, project_root)
    if read_result["status"] == "success":
        current_content = read_result["data"]

    has_existing_content = bool((current_content or "").strip())
    
    # 5b. Detect operation type from instructions
    instructions_lower = instructions.lower()
    is_revision = any(kw in instructions_lower for kw in ["improve", "revise", "edit", "fix", "change", "modify", "rewrite", "enhance", "refine"])
    is_continuation = any(kw in instructions_lower for kw in ["continue", "next", "extend", "add more", "keep going", "draft"])

    # Determine the operation mode
    # Architect action_type is authoritative: edit => revise, generate => generate/continue.
    if action_type == "edit":
        operation_mode = "revise" if has_existing_content else "generate"
    elif action_type == "generate":
        operation_mode = "continue" if has_existing_content else "generate"
    else:
        if has_existing_content:
            if is_revision and not is_continuation:
                operation_mode = "revise"
            else:
                operation_mode = "continue"
        else:
            operation_mode = "generate"

    # Build operation-specific instructions
    if operation_mode == "generate":
        operation_instructions = """
    OPERATION: GENERATE NEW CHAPTER
    - This is a new/empty file. Write the complete chapter content.
    - Use the 'write_file' tool to create the chapter.
    - Include a proper chapter heading and opening hook.
    """
    elif operation_mode == "continue":
        operation_instructions = """
    OPERATION: CONTINUE/EXTEND CHAPTER  
    - There is existing content. Write ONLY NEW content that continues the story.
    - Do NOT repeat or rewrite existing content.
    - Use the 'append_file' tool to add your continuation.
    - Ensure smooth transition from existing content.
    """
    else:  # revise
        operation_instructions = f"""
    OPERATION: REVISE/IMPROVE EXISTING CONTENT
    - The instruction asks to improve/revise specific aspects of the existing content.
    - Use the 'edit_file' tool to make TARGETED changes.
    - Find the specific passage to change and provide the exact replacement.
    - Keep changes surgical - preserve surrounding context.
    - If the change is substantial, you may need multiple edit_file calls.
    
    FULL EXISTING CONTENT FOR REFERENCE:
    {current_content[:4000]}
    """

    user_message = f"""
    TASK: Work on file '{target_file}'.
    
    INSTRUCTIONS FROM ARCHITECT:
    {instructions}
    
    SETTING CONTEXT:
    {loc_context}
    
    {operation_instructions}
    
    EXISTING CONTENT (Last 2000 chars):
    {current_content[-2000:] if current_content else "(New File)"}
    
    REQUIREMENTS:
    1. Follow the OPERATION instructions above precisely.
    2. Do NOT output the text in the chat. Use the appropriate tool.
    3. Adhere strictly to the character voices and setting details provided.
    4. Maintain continuity with the story brief and existing narrative.
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
        },
        {
            "type": "function",
            "function": {
                "name": "append_file",
                "description": "Appends the generated story content to the target manuscript file.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": f"Must be 'manuscripts/{target_file}'"
                        },
                        "content": {
                            "type": "string",
                            "description": "Markdown content to append to the chapter."
                        }
                    },
                    "required": ["path", "content"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "edit_file",
                "description": "Make a targeted find-and-replace edit to improve/revise specific passages. Use for revisions.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": f"Must be 'manuscripts/{target_file}'"
                        },
                        "search_text": {
                            "type": "string",
                            "description": "The EXACT text passage to find and replace. Must match existing content exactly."
                        },
                        "replace_text": {
                            "type": "string",
                            "description": "The improved/revised text to replace the search_text with."
                        }
                    },
                    "required": ["path", "search_text", "replace_text"]
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
        performed_edit_call = False
        for tool in tool_calls:
            args = tool["arguments"]
            safe_path = f"manuscripts/{target_file}"
            
            if tool["name"] == "edit_file":
                # Handle targeted edits for revisions
                performed_edit_call = True
                logger.info(f"Narrator editing {safe_path}...")
                result = await agent_tools.edit_file(
                    safe_path, 
                    args.get("search_text", ""), 
                    args.get("replace_text", ""), 
                    project_root
                )
                results.append(result)
                
            elif tool["name"] in {"write_file", "append_file"}:
                logger.info(f"Narrator writing to {safe_path} (mode: {operation_mode})...")
                # Route based on operation mode, not just what model requested
                if operation_mode == "generate":
                    result = await agent_tools.write_file(safe_path, args["content"], project_root)
                else:
                    # For continue mode, always append
                    result = await agent_tools.append_file(safe_path, args["content"], project_root)
                results.append(result)

        all_ok = all(isinstance(r, dict) and r.get("status") == "success" for r in results)
        if operation_mode == "revise" and not performed_edit_call:
            return {
                "status": "error",
                "message": "Revision mode required an edit_file call, but none were executed.",
                "modified_files": [],
                "tool_results": results,
                "operation_mode": operation_mode,
                "cost_metrics": response.get("usage", {})
            }

        if not all_ok:
            return {
                "status": "error",
                "message": "One or more file operations failed.",
                "modified_files": [],
                "tool_results": results,
                "operation_mode": operation_mode,
                "cost_metrics": response.get("usage", {})
            }

        return {
            "status": "success",
            "modified_files": [target_file],
            "tool_results": results,
            "operation_mode": operation_mode,
            "cost_metrics": response.get("usage", {})
        }
    else:
        return {"status": "error", "message": "Brain returned failure status."}