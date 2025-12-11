# TextCraft Orchestrator Logic (`core/orchestrator.py`)

**Version:** 2.1.0 (Refactored for Specialized Services)
**Status:** Core Definition
**Role:** The Central Execution Loop (The Nervous System)

-----

## 1\. Overview

The **Orchestrator** is the logic engine of TextCraft. It is the "Game Loop" that drives the project forward. Unlike the previous "Swarm" architecture, which relied on random agent conversation, the Orchestrator executes a deterministic, finite state machine loop.

  * **Responsibility:** Manages the cycle of **Scan** $\rightarrow$ **Plan** $\rightarrow$ **Act** $\rightarrow$ **Verify**.
  * **Dependencies:**
      * Reads `data/matrix.json` (via Scanner) to know the "World State".
      * Reads `data/story_bible/` to know the "Rules".
      * Calls `ai_services/*.py` (Specialized Services) to "Do Work".
      * Uses `core/agent_tools.py` indirectly via services.

-----

## 2\. The Main Loop (State Machine)

The orchestrator runs an infinite loop until the project status is `COMPLETE` or `PAUSED`.

### State 1: SCAN (Sensory Input)

  * **Action:** Call `core.scanner.ProjectScanner.scan()`.
  * **Purpose:** Update `data/matrix.json` with the physical reality of the hard drive (word counts, file existence, modification timestamps).
  * **Transition:** Proceed to **PLAN**.

### State 2: PLAN (The Architect)

  * **Actor:** `ai_services.architect`.
  * **Action:** The Orchestrator passes the current `matrix.json` state to the Architect Service.
  * **Prompt:** "Analyze the Matrix. Identify the next logical step. Is a chapter empty? Does a draft need editing? Return a JSON Decision Payload."
  * **Output:** A `DecisionPayload` object (see Section 3).
  * **Transition:** Proceed to **DISPATCH**.

### State 3: DISPATCH (The Assignment)

  * **Action:** The Orchestrator parses the `DecisionPayload` and routes execution to the specific AI Service module.
  * **Routing Logic:**
      * If `assigned_agent == 'narrator'`: Import `ai_services.narrator` and call `.execute(task_payload)`.
      * If `assigned_agent == 'editor'`: Import `ai_services.editor` and call `.execute(task_payload)`.
      * If `assigned_agent == 'architect'`: Call recursively (rare, usually for sub-planning).
  * **Context Injection:** The Orchestrator prepares the `context` dictionary by reading `story_bible/` data relevant to the specific task.
  * **Transition:** Proceed to **ACT** (The Service takes over).

### State 4: EXECUTE (The Action)

  * **Actor:** The specific AI Service Module (Narrator/Editor).
  * **Action:**
    1.  The Service hydrates its own specific prompts (Character Sheets for Narrator, Rules for Editor).
    2.  The Service calls `ai_services.client` (The Brain) to generate content.
    3.  The Service calls `core.agent_tools` to write files (`manuscripts/*.md`) to disk.
  * **Output:** A status report returned to the Orchestrator (e.g., `{"status": "success", "files_modified": ["ch01.md"]}`).
  * **Transition:** Loop back to **SCAN**.

-----

## 3\. Data Structures

### The Decision Payload

The JSON object returned by **The Architect Service** during the PLAN phase.

```json
{
  "action_type": "generate",
  "target_file": "ch03_The_Reveal.md",
  "assigned_agent": "narrator",
  "context_notes": "Focus on the dialogue between Kael and Mara. Ensure the tone is tense."
}
```

  * `action_type`: Enum (`generate`, `edit`, `outline`, `stop`).
  * `target_file`: The specific file ID in `matrix.json`.
  * `assigned_agent`: The module key mapping to `ai_services/` (e.g., `narrator`, `editor`).
  * `context_notes`: Specific instructions passed to the worker service's system prompt.

-----

## 4\. Logic & Variable Mapping

### A. Context Hydration (The "Need to Know" System)

To save tokens and maintain focus, the Orchestrator/Service pipeline filters data.

| Source Data | Logic Variable | Injection Rule |
| :--- | :--- | :--- |
| `characters.json` | `active_characters` | **Narrator Service** extracts only characters explicitly named in the scene instructions. |
| `project_conf.json` | `style_guide` | **All Services** inject this into their System Prompt. |
| `matrix.json` | `project_state` | **Architect Service** analyzes the full tree.<br>**Narrator/Editor** receive only the target node context. |

### B. Error Handling & Guardrails

  * **Stuck Loop Detection:** If the Matrix state (word count/status) does not change after a cycle, the Orchestrator increments a `retry_count`. If `retry_count > 3`, it pauses execution and alerts the user.
  * **Hallucination Check:** If the Architect returns a `target_file` that is not in the Matrix, the Orchestrator rejects the payload.

-----

## 5\. Public Interface

```python
class Orchestrator:
    def __init__(self):
        self.scanner = ProjectScanner()
        self.brain = AIClient()
        self.matrix_path = Path("data/matrix.json")

    async def start(self):
        """Initializes the loop."""
        pass

    async def step(self):
        """Executes a single Scan-Plan-Dispatch-Execute cycle."""
        pass

    def dispatch_to_service(self, decision: dict) -> dict:
        """Dynamic import and execution of ai_services modules."""
        pass
```

-----

## 6\. Implementation Notes

  * **Asynchronous:** The Orchestrator must use `asyncio` to handle long-running AI requests.
  * **Statelessness:** The Orchestrator object should not hold state between cycles. It must reload `matrix.json` fresh every time to ensure sync with the file system.