# TextCraft Personas Schema (`data/story_bible/personas.json`)

**Version:** 2.1.0 (Refactored for Specialized Services)
**Status:** Core Definition
**Role:** The AI Service Configuration

-----

## 1\. Overview

The **Personas Schema** (`data/story_bible/personas.json`) defines the "Cast" of AI agents that operate within the TextCraft system. Unlike the previous "Swarm" architecture where personas were hardcoded Python classes, TextCraft loads these definitions dynamically at runtime.

This file serves as the configuration source for the **Brain** (AI Services). It dictates *who* the AI is pretending to be, *what* tools it can use, and *how* creative or strict it should be.

  * **Read By:** Specific AI Services (`ai_services/architect.py`, `ai_services/narrator.py`, etc.).
  * **Modified By:** User (during initial project setup or tuning).
  * **Role:** Configuration Source for Stateless Services.

-----

## 2\. JSON Structure

The `personas.json` file must contain a root object where keys represent the unique `role_id` of the service.

```json
{
  "architect": {
    "name": "The Architect",
    "role_type": "orchestrator",
    "model": "gpt-4-turbo",
    "temperature": 0.7,
    "max_tokens": 2000,
    "system_prompt": "You are the Lead Architect...",
    "allowed_tools": ["read_file", "write_file", "assign_task"]
  },
  "narrator": {
    "name": "The Narrator",
    "role_type": "generator",
    "model": "gpt-4",
    "temperature": 0.9,
    "max_tokens": 4000,
    "system_prompt": "You are a creative writer...",
    "allowed_tools": ["read_file", "write_file"]
  }
}
```

-----

## 3\. Field Definitions

Each service object defines the following configuration variables used by the specific `ai_services` module.

### I. Identity Fields

| Field | Type | Description |
| :--- | :--- | :--- |
| `name` | String | The display name used in logs and the Matrix (e.g., "The Architect"). |
| `role_type` | **Enum** | Defines the service's function class:<br>• `orchestrator`: Can assign tasks and read the full Matrix.<br>• `generator`: Produces content (high creativity).<br>• `critic`: Validates content (low creativity). |

### II. Brain Configuration (AI Parameters)

| Field | Type | Description |
| :--- | :--- | :--- |
| `model` | String | The specific LLM ID to use (e.g., `gpt-4`, `claude-3-opus`). Maps to `ai_services/client.py`. |
| `temperature` | Float | **0.0 - 1.0**. Controls creativity/randomness.<br>• High (0.8-1.0): Narrator (Creative)<br>• Medium (0.5-0.7): Architect (Balanced)<br>• Low (0.0-0.3): Editor (Strict) |
| `max_tokens` | Integer | The limit for output generation. Narrators need high limits (4000+); Editors may need less. |

### III. The Soul (System Prompt)

| Field | Type | Description |
| :--- | :--- | :--- |
| `system_prompt` | String | The core instruction set injected into the context window. This string is the "personality." It supports mustache-style variable injection (e.g., `{{genre}}`) derived from `project_conf.json`. |

### IV. Capability Constraints

| Field | Type | Description |
| :--- | :--- | :--- |
| `allowed_tools` | Array\<String\> | A whitelist of tool names from `core/agent_tools.py` that this service is permitted to execute. Prevents the "Architect" from editing prose directly or the "Narrator" from deleting files. |

-----

## 4\. Standard Persona Definitions

The default installation of TextCraft requires these three core personas to function.

### A. The Architect (`architect`)

  * **Role:** The Manager.
  * **Responsibility:** Reads the Matrix, determines the next logical step (e.g., "Chapter 1 is done, start Chapter 2"), and assigns tasks.
  * **Prompt Strategy:** Focus on structure, pacing, and logical flow. **Never** writes prose.
  * **Tools:** `read_file`, `write_file` (for plans only), `assign_task`.

### B. The Narrator (`narrator`)

  * **Role:** The Writer.
  * **Responsibility:** Receives a task (e.g., "Write Scene 3 of Chapter 2") and generates raw text.
  * **Prompt Strategy:** Focus on sensory details, dialogue, character voice, and adherence to the `characters.json` profiles.
  * **Tools:** `read_file` (Memory), `write_file` (Manuscripts).

### C. The Editor (`editor`)

  * **Role:** The Critic.
  * **Responsibility:** Reads generated drafts and checks for continuity errors, plot holes, or style violations defined in `project_conf.json`.
  * **Prompt Strategy:** Analytical, critical, and detail-oriented.
  * **Tools:** `read_file`, `edit_file` (Limited corrections), `search_code` (Fact-checking).

-----

## 5\. Variable Injection (Context Hydration)

The `system_prompt` field in this schema is a template. At runtime, the specific AI Service injects variables from the **Story Bible** to create the final context.

**Template Example:**

```text
You are The Narrator writing a {{genre}} novel.
Your tone should be {{tone}}.
Target Audience: {{target_audience}}.
```

**Source Mapping:**

  * `{{genre}}` $\rightarrow$ `data/story_bible/project_conf.json["genre"]`
  * `{{tone}}` $\rightarrow$ `data/story_bible/project_conf.json["tone"]`
  * `{{target_audience}}` $\rightarrow$ `data/story_bible/project_conf.json["target_audience"]`

-----

## 6\. Logic Mapping

  * **`ai_services/*.py`:** Reads this file to configure the prompt and model parameters for the specific service call.
  * **`core/orchestrator.py`:** Uses the keys (e.g., `"narrator"`) to dispatch tasks to the correct service module.
  * **`ai_services/client.py`:** Uses `model` and `temperature` to configure the API request.