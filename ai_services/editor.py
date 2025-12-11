import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

from ai_services import client
from core import agent_tools
from core.memory_store import MemoryStore

logger = logging.getLogger(__name__)

class EditorError(Exception):
    """Custom exception for validation failures."""
    pass

def _load_json_config(path: Path) -> Dict[str, Any]:
    """Helper to safely load configuration files."""
    try:
        if not path.exists():
            # Timeline/Characters might be empty in early stages
            if path.name in ["timeline.json", "characters.json"]:
                return {}
            logger.warning(f"Config file missing: {path}")
            return {}
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load config {path}: {e}")
        return {}

def _hydrate_prompt(template: str, project_conf: Dict[str, Any]) -> str:
    """Injects project constraints into the system prompt."""
    replacements = {
        "{{title}}": project_conf.get("meta", {}).get("title", "Untitled"),
        "{{genre}}": project_conf.get("style", {}).get("genre", "General Fiction"),
        "{{style_guide}}": json.dumps(project_conf.get("style", {}), indent=2),
        "{{forbidden_tropes}}": json.dumps(project_conf.get("constraints", {}).get("forbidden_tropes", []), indent=2)
    }
    
    hydrated = template
    for key, value in replacements.items():
        hydrated = hydrated.replace(key, str(value))
    
    return hydrated

# --- Main Service Logic ---

async def execute(task_payload: Dict[str, Any], project_root: Path, memory_store: Optional[MemoryStore] = None) -> Dict[str, Any]:
    """
    Main entry point for the Editor Service.
    Executes a reasoning loop to validate content against the Story Bible and RAG Memory.
    
    Args:
        task_payload: Contains 'target_file'.
        project_root: The active project directory.
        memory_store: Interface to the Vector DB for checking consistency.
        
    Returns:
        Dict: {"status": "success", "verdict": "PASS/FAIL", "notes": [...]}
    """
    target_file = task_payload.get("target_file")
    if not target_file:
        return {"status": "error", "message": "No target_file provided for editing."}

    logger.info(f"Editor Service: Reviewing {target_file}...")

    # 1. Calculate Paths
    bible_dir = project_root / "data" / "story_bible"
    
    # 2. Load Data
    personas = _load_json_config(bible_dir / "personas.json")
    project_conf = _load_json_config(bible_dir / "project_conf.json")
    characters = _load_json_config(bible_dir / "characters.json")
    timeline = _load_json_config(bible_dir / "timeline.json")
    
    editor_config = personas.get("editor")
    if not editor_config:
        raise EditorError("Editor persona definition missing.")

    # 3. Read Target Content
    read_result = await agent_tools.read_file(f"manuscripts/{target_file}", project_root)
    if read_result["status"] != "success":
        return {"status": "error", "message": f"Could not read draft: {read_result.get('data')}"}
    
    draft_content = read_result["data"]

    # 4. Build Truth Context (The Rules)
    # We provide the full character list and timeline for checking.
    truth_context = f"""
    CHARACTERS:
    {json.dumps(characters, indent=2)}

    TIMELINE:
    {json.dumps(timeline, indent=2)}
    """

    # 5. Prepare Prompts & Tool Loop
    system_prompt = _hydrate_prompt(editor_config.get("system_prompt", ""), project_conf)
    
    initial_user_msg = f"""
    REVIEW TASK:
    Analyze the following draft ('{target_file}') for continuity errors, forbidden tropes, and style violations.
    
    DRAFT CONTENT:
    {draft_content}
    
    REFERENCE DATA (The Source of Truth):
    {truth_context}
    
    INSTRUCTIONS:
    1. If you doubt a fact (e.g. "Is Kael left-handed?"), use 'check_memory' to search past chapters.
    2. If you need to verify a specific file, use 'read_file'.
    3. If you find small typos, you MAY use 'edit_file' to fix them immediately.
    4. If you find MAJOR plot holes or continuity errors, do NOT fix them. Flag them.
    5. FINAL OUTPUT must be a JSON object: {{"verdict": "PASS" | "FAIL", "notes": ["Error 1", "Error 2"]}}
    """

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": initial_user_msg}
    ]

    # Define Tools available to the Editor
    tools_schema = [
        {
            "type": "function",
            "function": {
                "name": "read_file",
                "description": "Read other files to verify cross-chapter continuity.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string"}
                    },
                    "required": ["path"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "check_memory",
                "description": "Search the RAG Memory (Long-term history) to verify facts from previous chapters.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The question or fact to check, e.g., 'What color are Kael's eyes?'"
                        }
                    },
                    "required": ["query"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "edit_file",
                "description": "Fix minor typos or grammatical errors in the target file.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string"},
                        "search_text": {"type": "string"},
                        "replace_text": {"type": "string"}
                    },
                    "required": ["path", "search_text", "replace_text"]
                }
            }
        }
    ]

    # 6. Execution Loop (The ReAct Cycle)
    max_turns = 5
    current_turn = 0

    while current_turn < max_turns:
        try:
            response = await client.generate(
                messages=messages,
                model=editor_config.get("model", "gpt-4-turbo"),
                temperature=editor_config.get("temperature", 0.2),
                max_tokens=editor_config.get("max_tokens", 2000),
                tools=tools_schema
            )
        except Exception as e:
            logger.error(f"Editor Brain Failure: {e}")
            return {"status": "error", "message": str(e)}

        if response["status"] != "success":
            return {"status": "error", "message": "Brain returned failure."}

        data = response["data"]
        response_msg = {"role": "assistant", "content": data.get("content")}
        
        tool_calls = data.get("tool_calls", [])
        
        if tool_calls:
            # 1. Append Assistant's tool call message
            response_msg["tool_calls"] = [
                {
                    "id": tc["id"],
                    "type": "function",
                    "function": {"name": tc["name"], "arguments": json.dumps(tc["arguments"])}
                } for tc in tool_calls
            ]
            messages.append(response_msg)

            # 2. Execute Tools
            for tool in tool_calls:
                func_name = tool["name"]
                args = tool["arguments"]
                call_id = tool["id"]
                
                logger.info(f"Editor Tool Call: {func_name}")
                
                result = {"status": "error", "data": "Tool not found"}
                
                if func_name == "read_file":
                    result = await agent_tools.read_file(args["path"], project_root)
                
                elif func_name == "check_memory":
                    if memory_store:
                        memory_context = memory_store.query(args["query"])
                        result = {"status": "success", "data": memory_context if memory_context else "No relevant memory found."}
                    else:
                        result = {"status": "error", "data": "RAG Memory is offline."}
                
                elif func_name == "edit_file":
                    # Security: Ensure Editor only edits the target file
                    if target_file not in args["path"]:
                        result = {"status": "error", "data": f"Access Denied: You may only edit the target file '{target_file}'."}
                    else:
                        result = await agent_tools.edit_file(args["path"], args["search_text"], args["replace_text"], project_root)

                # 3. Append Tool Output
                messages.append({
                    "role": "tool",
                    "tool_call_id": call_id,
                    "name": func_name,
                    "content": str(result["data"])
                })
            
            current_turn += 1
            continue
        
        else:
            # No tool calls -> Final Verdict
            content = data.get("content", "")
            try:
                # Attempt to parse JSON verdict
                start = content.find('{')
                end = content.rfind('}') + 1
                if start != -1 and end != -1:
                    json_str = content[start:end]
                    verdict_data = json.loads(json_str)
                    
                    return {
                        "status": "success",
                        "verdict": verdict_data.get("verdict", "FAIL"),
                        "editor_notes": verdict_data.get("notes", []),
                        "raw_output": content
                    }
                else:
                    logger.warning("Editor did not return strict JSON.")
                    return {
                        "status": "success",
                        "verdict": "FAIL" if "FAIL" in content else "PASS",
                        "editor_notes": [content],
                        "raw_output": content
                    }
            except Exception as e:
                return {"status": "error", "message": f"Failed to parse verdict: {e}"}

    return {"status": "error", "message": "Editor exceeded max turns without verdict."}