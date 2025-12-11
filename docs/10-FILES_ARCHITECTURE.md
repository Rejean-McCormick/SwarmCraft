You are absolutely right. To fully honor the **TextCraft 2.1.0 Architecture** (Specialized AI Services), we must move away from generic abstractions and list the specific service modules and tools required to build the system.

Here is the **True Complete Architecture** based on the Refactored Specialized Services model:

### **1. The Brain (`ai_services/`)**
*Refactored to match Version 2.1.0: Specialized functional modules.*
* **`ai_services/__init__.py`**
* **`ai_services/client.py`**
    * *Role:* The Gateway. Handles API keys, rate limits, and cost tracking.
* **`ai_services/architect.py`**
    * *Role:* The World Builder Service. Generates JSON data (Character Sheets) and Decision Payloads.
* **`ai_services/narrator.py`**
    * *Role:* The Writer Service. The "Surgeon" that fixes blank pages with prose based on Character Data.
* **`ai_services/editor.py`**
    * *Role:* The Judge Service. Validates continuity against the Story Bible and checks constraints.

### **2. The Logic (`core/`)**
* **`core/__init__.py`**
* **`core/orchestrator.py`**
    * *Role:* The Pipeline Manager. Implements **The Loop**: `Scan` $\rightarrow$ `Plan` $\rightarrow$ `Dispatch` $\rightarrow$ `Execute`.
* **`core/scanner.py`**
    * *Role:* The Dashboard Generator. Scans `data/manuscripts` to build `matrix.json`.
* **`core/agent_tools.py`**
    * *Role:* The Hands. Strictly typed file system operations (`read_file`, `write_file`) used by Services.

### **3. The Memory (`data/`)**
* **`data/matrix.json`**
    * *Role:* The Story Matrix. Tracks Narrative Completeness (Green/Yellow lights).
* **`data/story_bible/personas.json`**
    * *Role:* AI Identity Config. Defines the System Prompts and Models for the Services.
* **`data/story_bible/project_conf.json`**
    * *Role:* Project Config. Genre, Tone, and Constraints.
* **`data/story_bible/characters.json`**
    * *Role:* Character Truth (Inventory, Relationships).
* **`data/story_bible/locations.json`**
    * *Role:* World Data.
* **`data/manuscripts/`**
    * *Role:* The actual text content (Drafts, Outlines).

### **4. Root**
* **`main.py`**
    * *Role:* Entry point. Initializes the Scanner and Orchestrator.
* **`requirements.txt`**
    * *Role:* Dependencies.

---

### **Updated Documentation List**

To align with this architecture, the documentation suite maps exactly to the file structure and logic flow.

1.  **`docs/00_MASTER_ARCHITECTURE.md`** (The High-Level Map)
2.  **`docs/01_SCHEMA_MATRIX.md`** (The Dashboard Schema)
3.  **`docs/02_SCHEMA_PERSONAS.md`** (The AI Configuration Schema)
4.  **`docs/03_SCHEMA_PROJECT_CONF.md`** (The Constraints Schema)
5.  **`docs/04_SCHEMA_CHARACTERS.md`** (The World Data Schema)
6.  **`docs/05_CORE_ORCHESTRATOR.md`** (The Loop & Dispatch Logic)
7.  **`docs/06_CORE_SCANNER.md`** (The Status Heuristics)
8.  **`docs/07_AGENT_TOOLS_SPEC.md`** (The File System Safety Protocols)
9.  **`docs/08_AI_CLIENT_SPEC.md`** (The Brain API Contract)
10. **`docs/09_SERVICE_LIFECYCLE.md`** (The Execution Flow of a Service Module)