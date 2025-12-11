# TextCraft Control Schema (`data/control.json`)

**Version:** 2.1.0
**Status:** Core Definition
**Role:** Inter-Process Communication (The Reins)

-----

## 1\. Overview

The `data/control.json` file serves as the **Command & Control** interface between the Frontend (TUI) and the Backend (Orchestrator).

Because the Orchestrator runs in a blocking or heavy async loop, it cannot easily listen for keyboard events directly. Instead, it implements a **Polling Interceptor** pattern. At the start of every `PLAN` phase, the Orchestrator checks this file for new orders.

  * **Written By:** The Director's Monitor (`dashboard.py`).
  * **Read By:** The Orchestrator (`core/orchestrator.py`).
  * **Behavior:** Volatile. Certain fields are "Read-Once," meaning the Orchestrator clears them after execution to prevent loops.

-----

## 2\. JSON Structure

```json
{
  "system_status": "RUNNING",
  "architect_override": {
    "active": false,
    "instruction": null,
    "force_target": null
  },
  "runtime_settings": {
    "global_temperature": 0.7,
    "model_override": null
  }
}
```

-----

## 3\. Field Definitions

### I. System Status (`system_status`)

Controls the main execution loop.

| Value | Behavior |
| :--- | :--- |
| `RUNNING` | Standard operation. The loop proceeds automatically. |
| `PAUSED` | The Orchestrator enters a `while True: sleep(1)` state. It does not terminate, but it takes no actions. Used when the Director is typing a complex command. |
| `STOP` | Signals the Orchestrator to save state, close connections, and exit the process. |

### II. Architect Override (`architect_override`)

The "God Mode" intervention mechanism. This allows the user to inject commands directly into the Architect's ear, bypassing the standard logic.

  * **`active`** (Boolean): Logic flag. If `false`, the Orchestrator ignores this block.
  * **`instruction`** (String | Null): The text from the Input Bar (e.g., *"Make Chapter 3 darker"*). If present, the Orchestrator appends this to the Architect's system prompt for **one turn only**.
  * **`force_target`** (String | Null): A specific Matrix ID (e.g., `ch03`). If present, the Architect is forced to return a payload targeting this file, ignoring its own priorities.

**Reset Protocol:**
Once the Orchestrator successfully dispatches a task based on an override, it **MUST** write back to this file setting `active: false` and `instruction: null`.

### III. Runtime Settings (`runtime_settings`)

Temporary tweaks applied via the "Vibe Check" modal. These are ephemeral and do not overwrite `project_conf.json` permanently, but modify the current session's behavior.

  * **`global_temperature`**: Overrides the `temperature` in `personas.json`. Useful for momentarily increasing creativity (1.0) or strictness (0.1).
  * **`model_override`**: If set (e.g., `claude-3-opus`), all Service calls use this model instead of their default.

-----

## 4\. Logic Mapping

### The Polling Implementation

In `core/orchestrator.py`:

```python
async def _check_control_signals(self):
    """
    Called at the start of every step().
    Reads control.json and adjusts state.
    """
    try:
        with open("data/control.json", "r") as f:
            signals = json.load(f)

        # 1. Check Status
        if signals["system_status"] == "STOP":
            self.stop()
        elif signals["system_status"] == "PAUSED":
            logger.info("Paused by Director.")
            while signals["system_status"] == "PAUSED":
                await asyncio.sleep(1)
                # Re-read file to check for resume
                signals = json.load(open("data/control.json"))

        # 2. Check Overrides
        override = signals.get("architect_override", {})
        if override.get("active"):
            logger.info(f"INTERCEPT: Injecting command '{override['instruction']}'")
            # Return the override data to be passed to architect.plan_next_step()
            return override

    except FileNotFoundError:
        pass # File hasn't been created by UI yet, proceed normally.
    
    return None
```

### The Writing Implementation

In `dashboard.py` (when User hits Enter):

```python
def submit_command(self, text):
    payload = {
        "system_status": "RUNNING",
        "architect_override": {
            "active": True,
            "instruction": text,
            "force_target": None
        }
    }
    # Atomic Write
    with open("data/control.json", "w") as f:
        json.dump(payload, f)
```

-----

## 5\. File Locking & Safety

Since two processes (UI and Core) access this file:

1.  **UI Priority:** The UI is the "Writer" of commands.
2.  **Core Priority:** The Core is the "Consumer" and "Resetter" of commands.
3.  **Conflict Resolution:** Standard OS file locking is usually overkill for this scale. We rely on **Atomic Writes** (write to temp file -\> rename) for the UI to ensure the Core never reads a half-written JSON string.