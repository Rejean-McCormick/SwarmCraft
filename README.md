# TextCraft (Fork of Swarmussy) - v3.0.0

## The Multi-Project and RAG Architecture

[](https://opensource.org/licenses/MIT)
[](https://www.python.org/downloads/)
[](https://www.google.com/search?q=https://github.com/Rejean-McCormick/swarmussy)

-----

### **Credit and Acknowledgements**

This repository is a **Major Architectural Rewrite (Fork)** of the original Swarmussy project.

  * **Original Code and Inspiration:** **[mojomast/swarmussy](https://github.com/mojomast/swarmussy)**
  * **Rewrite Author (v3.0):** **[Rejean-McCormick](https://github.com/Rejean-McCormick)**

-----

## 🚀 Architectural Philosophy: The AWA Influence

TextCraft v3.0 moves away from the multi-agent *Chatroom* model to a **Deterministic Pipeline** influenced by the architecture principles of the **Abstract Wikipedia Architect (AWA)**.

AWA seeks to decouple abstract concepts from their language-specific implementations. TextCraft applies this to **decouple the Novel's State from the Agents' Logic**.

### AWA Principles Applied to TextCraft:

| AWA Principle | TextCraft Implementation | Benefit |
| :--- | :--- | :--- |
| **Decoupling (Statelessness)** | **Agents are Stateless Services** (`ai_services/`). They are pure functions (`narrator.execute(context)`) that perform a task and terminate, instead of persistent objects in a chat session. | Dramatically reduces complexity, eliminates race conditions, and improves crash recovery. |
| **Central Data Model** | The **Matrix (`matrix.json`)** acts as the central, machine-readable source of truth (similar to AWA's Central Data Index). | Ensures all components (Agents, Scanner, Dashboard) share the exact same, version-controlled view of the project state. |
| **Functional Monotonicity** | The **Orchestrator** enforces a strict, atomic cycle: **SCAN $\rightarrow$ PLAN $\rightarrow$ EXECUTE**. No agent can interrupt another's process, mirroring the predictable update sequence required by large, stable data systems like AWA. | Guarantees deterministic output and simplifies debugging. |
| **Data Immutability** | Agents modify the world **only** through controlled file operations (`agent_tools`), which triggers re-indexing by the `Scanner`. | The file system is the ultimate source of truth, preventing state drift between the database and the physical world. |

-----

## ✨ Core Features of TextCraft v3.0

The entire system is redesigned for stability, long-form narrative coherence, and enterprise-grade project management.

| Feature | Description | Enabled by Module |
| :--- | :--- | :--- |
| **Multi-Project System** | Manage multiple isolated novel universes simultaneously. The system can be switched between projects without restarting the engine. | `core/project_manager.py` |
| **RAG Long-Term Memory** | Utilizes **ChromaDB** to index every paragraph written. Agents can query this memory to maintain continuity over hundreds of thousands of words, solving the plot-hole problem in long novels. | `core/memory_store.py` |
| **TUI Dashboard** | Replaced the complex Web UI with a robust, low-latency Terminal User Interface (TUI) powered by `textual`. This acts as a real-time Mission Control. | `dashboard.py` / `ui/` |
| **Decoupled Architecture** | Moteur (Engine) and Moniteur (Dashboard) run as separate processes, ensuring the UI never freezes, even if the AI is running a 5-minute task. | `core/orchestrator.py` |

-----

## ⚙️ Installation and Launch Guide

The system runs as two decoupled processes. You will need **two separate terminal windows**.

### 1\. Setup

1.  Clone the repository and access the folder.
2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3.  Configure your API Key. Copy the example file and fill in your key:
    ```bash
    cp .env.example .env
    # Open .env and fill in LLM_API_KEY
    ```

### 2\. Launch

Start the processes in this order:

#### **Terminal 1: The Engine (Moteur)**

*Role: The Brain. Runs the Orchestrator, Planning, and Execution Loop.*

```bash
python main.py
```

#### **Terminal 2: The Monitor (Moniteur)**

*Role: The View. Runs the real-time Dashboard (TUI).*

```bash
python dashboard.py
```

The Dashboard will launch in full-screen TUI mode, displaying the status of the project being processed by the Engine. Press **`q`** on the dashboard and **`Ctrl+C`** on the engine log to stop the system gracefully.

-----

*For a deeper dive into the architectural flow, see [docs/13\_ARCHITECTURE\_ADVANCED.md](https://www.google.com/search?q=./docs/13_ARCHITECTURE_ADVANCED.md).*