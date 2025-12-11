# TextCraft Service Lifecycle

**Version:** 2.1.0 (Refactored for Specialized Services)
**Status:** Core Definition
**Role:** The Execution Flow for AI Modules

-----

## 1\. Overview

The **Service Lifecycle** describes the functional execution flow of the specialized AI modules in `ai_services/` (e.g., `narrator.py`, `architect.py`).

In the TextCraft 2.1 architecture, the concept of a persistent "Agent Class" (`GenericAgent`) has been removed. Instead, **AI Services** are stateless functional modules. They are invoked by the Orchestrator to perform a specific task, they execute their logic, and then they return control.

  * **Triggered By:** `core/orchestrator.py` (during the `DISPATCH` phase).
  * **Components:** `ai_services/*.py` modules.
  * **Result:** A deterministic modification of the Memory (Matrix or Manuscripts).

-----

## 2\. The Execution Flow

When `orchestrator.py` calls a service function (e.g., `ai_services.narrator.execute(task)`), the following lifecycle occurs:

### Step 1: Configuration Load

The Service module reads its specific configuration from `data/story_bible/personas.json`.

  * **Narrator Service** loads: "Creative Writer" prompt, Model `gpt-4`, Temperature `0.9`.
  * **Editor Service** loads: "Ruthless Critic" prompt, Model `gpt-4-turbo`, Temperature `0.2`.

### Step 2: Context Hydration

The Service reads `data/story_bible/project_conf.json` and `data/story_bible/characters.json`.

  * It injects global variables (Genre, Tone) into the `system_prompt` template.
  * It filters the Story Bible (e.g., selecting only characters present in the scene) to create a lean Context Window.

### Step 3: The Brain Call

The Service passes the fully hydrated context to `ai_services.client.generate()`.

  * It attaches the **Tool Schemas** specifically allowed for this service (e.g., Narrator gets `write_file`, Editor gets `edit_file`).
  * It handles the asynchronous API request.

### Step 4: Tool Execution (The Body)

If the Brain returns a Function Call (e.g., "I need to write to `ch01.md`"):

1.  The Service imports the specific function from `core.agent_tools`.
2.  It executes the function locally within the `data/` sandbox.
3.  It captures the result (Success/Error).
4.  *Optional:* It feeds the result back to the Brain for a final confirmation summary.

### Step 5: Termination

The Service returns a structured **Status Report** to the Orchestrator and finishes execution.

  * **Report Example:** `{"status": "success", "modified": ["ch01.md"], "cost": 0.04}`.
  * **Statelessness:** The Python module holds no memory of this interaction after the function returns. All persistent state is now in `matrix.json`.

-----

## 3\. Variable Injection Map

This table defines how JSON data maps to the Service execution variables during **Step 2**.

| JSON Source (`story_bible/`) | JSON Key | Service Variable | Usage |
| :--- | :--- | :--- | :--- |
| `personas.json` | `system_prompt` | `prompt_template` | The raw personality string. |
| `personas.json` | `allowed_tools` | `tool_list` | Filters which functions are sent to the API. |
| `project_conf.json` | `style.genre` | `{{genre}}` | Injected into `prompt_template`. |
| `project_conf.json` | `meta.title` | `{{title}}` | Injected into `prompt_template`. |
| `characters.json` | `{char_id}.voice` | `{{character_context}}` | Injected if character is in scene. |

-----

## 4\. Service Module Interface

Each module in `ai_services/` must implement a standard entry point to ensure the Orchestrator can call them uniformly.

```python
# ai_services/narrator.py (Example)

def execute(task_payload: dict, context: dict) -> dict:
    """
    Main entry point called by Orchestrator.
    
    Args:
        task_payload: From DecisionPayload (target file, instructions).
        context: Relevant matrix state injected by Orchestrator.
        
    Returns:
        Dict containing status, modified files, and usage metrics.
    """
    # 1. Load Persona Config
    # 2. Build Messages (System + User Task)
    # 3. Call Client
    # 4. Handle Tools
    # 5. Return Report
    pass
```

-----

## 5\. Lifecycle Termination

TextCraft Services are **ephemeral functions**.

  * They do not "sleep" or "wait."
  * **State Persistence:** If a Service needs to remember something for the next cycle (e.g., "I left a TODO in Chapter 1"), it **must** write that fact to `matrix.json` or the manuscript itself before returning.
  * Once the `execute()` function returns, the Orchestrator proceeds immediately to the **SCAN** phase to verify the work done.