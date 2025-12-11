# TextCraft UI Layout Specification (`docs/10_UI_LAYOUT_SPEC.md`)

**Version:** 2.1.0
**Status:** Draft
**Role:** The Director's Monitor (TUI Design)

-----

## 1\. Design Philosophy

The TextCraft Interface is designed as a **Mission Control Center** (The Director's Monitor). Unlike a standard text editor, it focuses on high-level orchestration rather than character-level typing.

  * **Metaphor:** You are the Director; the AI is the Cast & Crew.
  * **Aesthetic:** "Cyberpunk Terminal." High contrast, neon accents on dark backgrounds, monospaced fonts.
  * **Framework:** Built using the `textual` Python library.

-----

## 2\. The Screen Layout (Grid System)

The main screen (`DirectorScreen`) uses a **3-Column Grid** layout with a persistent **Footer Bar**.

### ASCII Wireframe

```text
+---------------------+---------------------------------------------------+------------------------+
|  COLUMN 1 (20%)     |                 COLUMN 2 (60%)                    |    COLUMN 3 (20%)      |
|   CONTEXT PANEL     |                  ACTION PANEL                     |    PROGRESS PANEL      |
|                     |                                                   |                        |
| [ CAST LIST       ] |  [ PROSE STREAM (Scrollable)                    ] |  [ MATRIX TABLE      ] |
| > Kael Voss         |  The neon rain slicked the pavement...            |  Ch 1: LOCKED          |
| > Mara Syn          |                                                   |  Ch 2: REVIEW          |
|                     |                                                   |  Ch 3: DRAFT           |
| [ LOCATION        ] |                                                   |                        |
| > Sector 4          |---------------------------------------------------|  [ INTEGRITY GAUGE   ] |
|                     |  [ SYSTEM LOG (Collapsible)                     ] |  [||||||||||  ] 85%     |
| [ ACTIVE TOOL     ] |  > [ARCHITECT] Plan: Edit Ch 2                    |                        |
| > write_file        |  > [EDITOR] Found plot hole...                    |  [ COST TRACKER      ] |
|                     |                                                   |  $0.45 / $5.00         |
+---------------------+---------------------------------------------------+------------------------+
|  INPUT BAR: > "Architect, make the tone darker."                                    [STATUS]     |
+---------------------+---------------------------------------------------+------------------------+
```

### CSS Grid Definition

```css
Screen {
    layout: grid;
    grid-size: 3 2;
    grid-columns: 20% 60% 20%;
    grid-rows: 1fr 3; /* Main Content takes space, Input bar takes 3 lines */
}

#context-panel {
    dock: left;
    width: 100%;
    height: 100%;
    border-right: solid $accent;
}

#action-panel {
    width: 100%;
    height: 100%;
}

#progress-panel {
    dock: right;
    width: 100%;
    height: 100%;
    border-left: solid $accent;
}

#director-input {
    column-span: 3;
    dock: bottom;
    height: 3;
    border-top: solid $accent;
}
```

-----

## 3\. Widget Hierarchy

The UI is composed of the following `textual` widget tree:

  * **`App`** (`TextCraftApp`)
      * **`Screen`** (`DirectorScreen`)
          * **`Container`** (`#context-panel`)
              * `Header` ("CAST IN SCENE")
              * `Markdown` (`#cast-list`) - *Dynamic list of active characters.*
              * `Header` ("LOCATION")
              * `Static` (`#location-card`) - *Current setting description.*
              * `Header` ("ACTIVE TOOL")
              * `Static` (`#tool-card`) - *Flashes when tools are used.*
          * **`Container`** (`#action-panel`)
              * `RichLog` (`#prose-stream`) - *The main reading area.*
              * `RichLog` (`#system-log`) - *Technical logs (Orchestrator steps).*
          * **`Container`** (`#progress-panel`)
              * `DataTable` (`#matrix-table`) - *Clickable chapter list.*
              * `ProgressBar` (`#integrity-gauge`)
              * `Static` (`#cost-tracker`)
          * **`Input`** (`#director-input`) - *Command line.*
      * **`Footer`** - *Keybindings display.*

-----

## 4\. Component Details

### A. The Context Panel (Left)

  * **Purpose:** Shows *Inputs*. What data is the AI currently looking at?
  * **Data Source:** Parsed from the Orchestrator's `active_task` context.
  * **Styling:**
      * Alive Characters: Green text.
      * Dead Characters: Red strikethrough.
      * Active Tool: Flashes Yellow when `write_file` is executing.

### B. The Action Panel (Center)

  * **Purpose:** Shows *Outputs*.
  * **`#prose-stream`:**
      * Displays the content of `.md` files as they are written.
      * Uses Markdown rendering for bold/italics.
      * Auto-scrolls to bottom.
  * **`#system-log`:**
      * Displays high-level Orchestrator moves (PLAN -\> ACT).
      * Filters out raw API debug noise.

### C. The Progress Panel (Right)

  * **Purpose:** Shows *State*.
  * **`#matrix-table`:**
      * **Columns:** ID, Status, Words.
      * **Interaction:** Clicking a row triggers an `assign_task` event to prioritize that chapter.
      * **Color Coding:**
          * `LOCKED`: Green
          * `REVIEW_READY`: Cyan
          * `DRAFTING`: Yellow
          * `FAIL`: Red

### D. The Director Input (Bottom)

  * **Purpose:** "God Mode" intervention.
  * **Functionality:**
      * Input starts with `/` -\> System Command (e.g., `/quit`, `/restart`).
      * Input starts with text -\> Intercepts the Architect loop (e.g., "Add a plot twist here.").

-----

## 5\. Modal Definitions (Popups)

### A. Vibe Check (`Ctrl+S`)

A dialog to adjust `project_conf.json` on the fly.

  * **Layout:** Vertical Container.
  * **Fields:**
      * `Select`: Genre (Cyberpunk / Fantasy / Noir).
      * `Input`: Tone (Free text field).
      * `Slider`: Temperature (0.1 to 1.0).
  * **Buttons:** [Apply], [Cancel].

### B. Cast Manager (`Ctrl+C`)

A dialog to view and tweak `characters.json`.

  * **Layout:** Sidebar List (Characters) + Detail View.
  * **Functionality:**
      * Quickly toggle `is_alive`.
      * Add item to `inventory`.
      * Edit `motivation` string.

-----

## 6\. Color Palette (CSS Variables)

```css
$background: #0a0a0f;
$surface: #121216;
$accent: #00ff9d; /* Cyberpunk Green */
$warning: #f1c40f;
$error: #e74c3c;
$text: #ecf0f1;
$dim: #7f8c8d;

Screen {
    background: $background;
    color: $text;
}

Header {
    background: $surface;
    color: $accent;
    text-style: bold;
    border-bottom: solid $dim;
}

#prose-stream {
    background: $background;
    border: solid $dim;
    padding: 1;
}

.locked { color: $accent; }
.drafting { color: $warning; }
.fail { color: $error; }
```

-----

## 7\. Key Bindings

| Key | Action | Scope |
| :--- | :--- | :--- |
| `Ctrl+C` | Open **Cast Manager** | Global |
| `Ctrl+S` | Open **Vibe Check** (Settings) | Global |
| `Space` | Pause/Resume Orchestrator | Global |
| `Q` | Quit Application | Global |
| `Enter` | Submit Director Input | Input Bar |