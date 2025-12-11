# TextCraft UI Event Loop & Data Flow (`docs/11_UI_EVENT_LOOP.md`)

**Version:** 2.1.0
**Status:** Draft
**Role:** The Asynchronous Nervous System

-----

## 1\. Architectural Overview

The TextCraft Interface operates on a **Decoupled Asynchronous Model**.
To prevent the UI from freezing while the AI is generating text (which can take 30-60 seconds), the **Rendering Loop** (UI) and the **Execution Loop** (Orchestrator) run as separate `asyncio` tasks.

  * **The Orchestrator:** Runs in the background, treating the file system (`data/`) as its absolute truth.
  * **The Interface:** Runs in the foreground, strictly observing `data/` and sending signals via `control.json`.

This ensures that even if the AI crashes or hangs, the Interface remains responsive and can issue a "Kill Signal."

-----

## 2\. The Watcher Pattern (Read Loop)

The UI does not query the Orchestrator object directly. Instead, it watches the artifacts the Orchestrator leaves behind. This allows the UI to be restarted without killing the running job.

### A. The Matrix Watcher

  * **Source:** `data/matrix.json`
  * **Frequency:** 1.0 seconds (1000ms)
  * **Logic:**
    1.  Check `st_mtime` of the file.
    2.  If changed, reload JSON.
    3.  Update the **Progress Panel** (`DataTable`).
    4.  Update the **System Status** header.

### B. The Stream Watcher

  * **Source:** `data/manuscripts/*.md`
  * **Frequency:** 0.5 seconds (500ms)
  * **Logic:**
    1.  Identify the `active_task.target` from the Matrix (e.g., `ch03`).
    2.  Read the corresponding file (`manuscripts/ch03.md`).
    3.  Compare with cached content.
    4.  If new content exists, append it to the **Action Panel** (`RichLog`).
    5.  *Visual Flair:* Auto-scroll to the bottom to create a "typewriter" effect.

### C. The Log Watcher

  * **Source:** `logs/orchestrator.log` (or internal deque if running in same process)
  * **Frequency:** Event-Driven
  * **Logic:**
    1.  When the Orchestrator emits a log (INFO/WARN), it is pushed to the **System Log** widget.

-----

## 3\. The Interceptor Pattern (Write Loop)

When the Director (User) types a command or changes a setting, the UI does not modify Python variables. It writes a **Control Signal**.

### A. The Control File (`data/control.json`)

This is a volatile file checked by the Orchestrator at the start of every **PLAN** phase.

```json
{
  "status": "RUNNING",       // RUNNING | PAUSED | STOP
  "override_prompt": null,   // String: Instructions to inject into Architect
  "priority_task": null      // String: "ch05" -> Forces next task target
}
```

### B. Command Injection Logic

When the user types: `> "Make Chapter 3 darker."`

1.  **UI Action:**

      * Parses input.
      * Locks `control.json`.
      * Writes:
        ```json
        {
          "status": "RUNNING",
          "override_prompt": "Immediate Instruction: Rewrite Chapter 3 with a darker tone.",
          "priority_task": "ch03"
        }
        ```
      * Clears input bar.

2.  **Orchestrator Action (Next Tick):**

      * Reads `control.json`.
      * Detects `override_prompt`.
      * **Bypasses Standard Architect Logic.**
      * Sends `override_prompt` directly to the Architect Service.
      * **Reset:** Clears `override_prompt` in `control.json` to prevent loops.

-----

## 4\. Async Implementation Strategy

The `dashboard.py` (Textual App) will manage the concurrency.

```python
# Pseudo-code Structure

class TextCraftApp(App):
    async def on_mount(self):
        # 1. Start the UI Watchers
        self.set_interval(1.0, self.watch_matrix)
        self.set_interval(0.5, self.watch_stream)
        
        # 2. Spawn the Orchestrator in a background thread/task
        self.orchestrator_task = asyncio.create_task(self.run_orchestrator())

    async def run_orchestrator(self):
        # Wraps the core logic to keep UI unblocked
        orch = Orchestrator()
        await orch.start()

    async def watch_matrix(self):
        # Non-blocking file read
        async with aiofiles.open("data/matrix.json") as f:
            data = json.loads(await f.read())
            self.update_progress_bars(data)
```

-----

## 5\. Failure Modes & Recovery

1.  **Orchestrator Freeze:**

      * *Detection:* `last_heartbeat` in Matrix is \> 30 seconds old.
      * *UI Action:* Flashes "CONNECTION LOST" in the header. Shows [FORCE RESTART] button.
      * *Resolution:* UI cancels the `orchestrator_task` and re-spawns it.

2.  **File Lock Contention:**

      * Since both processes read/write JSON, use atomic writes (write to `.tmp` then rename) in `core/agent_tools.py` to prevent the UI from reading half-written JSON.