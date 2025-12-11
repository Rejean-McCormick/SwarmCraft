# TextCraft Agent Tools Specification (`core/agent_tools.py`)

**Version:** 2.1.0 (Refactored for Specialized Services)
**Status:** Core Definition
**Role:** The Physical Manipulators (The Hands)

-----

## 1\. Overview

The **Agent Tools** module (`core/agent_tools.py`) defines the strictly typed functions that AI Services can execute. These tools serve as the bridge between the AI's intent and the physical file system or orchestration state.

  * **Invoked By:** Specific `ai_services` modules (e.g., `ai_services/narrator.py`) when the Brain requests a function call.
  * **Executed By:** Python runtime within the `core` context.
  * **Scope:** Strictly limited to the `data/` directory.

-----

## 2\. Global Constraints & Safety

To prevent the AI from damaging the system, all tools operate under a **Sandbox Protocol**.

1.  **Path Restriction:** All file paths must resolve to children of the `data/` directory. Attempts to access `../` or `/etc/` will raise a `SecurityError`.
2.  **Atomic Operations:** Writes are atomic where possible to prevent corruption during crashes.
3.  **Return Format:** All tools return a standardized dictionary:
    ```json
    {
      "status": "success|error",
      "data": "The actual content or error message",
      "meta": { "bytes_written": 1024, "execution_time": 0.05 }
    }
    ```

-----

## 3\. File System Tools

These tools allow Services to manipulate the **Memory** (Manuscripts and Story Bible).

### `read_file`

  * **Role:** The primary input mechanism for services.
  * **Allowed Services:** All (Architect, Narrator, Editor).
  * **Signature:** `read_file(path: str) -> dict`
  * **Arguments:**
      * `path`: Relative path from `data/` (e.g., `manuscripts/ch01.md`).
  * **Returns:** The UTF-8 string content of the file.
  * **Logic:**
      * Validates path existence.
      * Reads content.
      * *Implicit:* If file is a JSON, it is returned as a string (Service must parse).

### `write_file`

  * **Role:** Creation and Overwrite.
  * **Allowed Services:** Architect Service (Plans), Narrator Service (Drafts).
  * **Signature:** `write_file(path: str, content: str) -> dict`
  * **Arguments:**
      * `path`: Relative target path.
      * `content`: The full text to write.
  * **Returns:** Success status and new file size.
  * **Side Effects:**
      * Overwrites existing files completely.
      * Creates parent directories if missing.
      * Triggers a `last_modified` update in the OS (detected by Scanner).

### `edit_file`

  * **Role:** Surgical correction.
  * **Allowed Services:** Editor Service.
  * **Signature:** `edit_file(path: str, search_text: str, replace_text: str) -> dict`
  * **Arguments:**
      * `path`: Relative target path.
      * `search_text`: The exact string segment to find.
      * `replace_text`: The new string to insert.
  * **Returns:** Success status or "Text not found" error.
  * **Logic:**
      * Reads file.
      * Performs `text.replace(search_text, replace_text, 1)` (Single replacement to ensure precision).
      * Writes file back.

### `list_files`

  * **Role:** Exploration and verification.
  * **Allowed Services:** Architect Service, Editor Service.
  * **Signature:** `list_files(directory: str) -> dict`
  * **Arguments:**
      * `directory`: Relative path (e.g., `manuscripts/`).
  * **Returns:** A list of filenames with basic metadata (size, mod\_time).

### `search_code` (Text Search)

  * **Role:** Fact checking and cross-referencing.
  * **Allowed Services:** Editor Service, Architect Service.
  * **Signature:** `search_code(query: str, directory: str = "manuscripts") -> dict`
  * **Arguments:**
      * `query`: The string or regex to find.
      * `directory`: The scope of search.
  * **Returns:** A list of matches with file paths and line numbers.

-----

## 4\. Orchestration Tools

These tools do not touch the file system directly but manipulate the **Logic State**.

### `assign_task`

  * **Role:** Delegation.
  * **Allowed Services:** Architect Service.
  * **Signature:** `assign_task(target_agent: str, task_description: str, target_file: str) -> dict`
  * **Arguments:**
      * `target_agent`: Module key (e.g., `narrator`, `editor`).
      * `task_description`: Natural language instructions (e.g., "Write the fight scene").
      * `target_file`: The specific matrix ID or path to work on.
  * **Returns:** Confirmation payload.
  * **Side Effect:** The Orchestrator receives this payload and routes execution to the corresponding module in `ai_services/`.

-----

## 5\. Logic Mapping

  * **Scanner Integration:** When `write_file` or `edit_file` returns `status: success`, the Orchestrator knows the physical state has changed and may trigger an immediate partial scan or wait for the next loop.
  * **Brain Integration:** These tool definitions are converted into JSON Schemas (OpenAI Function Calling format) by the specific `ai_services` module before being sent to the LLM.

**Example JSON Schema generated for the Brain:**

```json
{
  "name": "write_file",
  "description": "Writes full content to a file. Overwrites existing content.",
  "parameters": {
    "type": "object",
    "properties": {
      "path": { "type": "string", "description": "Path relative to data/" },
      "content": { "type": "string", "description": "The full text content." }
    },
    "required": ["path", "content"]
  }
}
```