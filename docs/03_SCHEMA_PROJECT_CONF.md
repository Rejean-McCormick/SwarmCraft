# TextCraft Project Configuration Schema (`data/story_bible/project_conf.json`)

**Version:** 2.1.0 (Refactored for Specialized Services)
**Status:** Core Definition
**Role:** The Creative Constraints Engine

-----

## 1\. Overview

The **Project Configuration** file (`data/story_bible/project_conf.json`) acts as the "Director" of the TextCraft engine. While the **Personas** define *who* is writing, this file defines *what* they are writing and *how* it should feel.

  * **Read By:** Specific AI Services (`ai_services/narrator.py`, `ai_services/architect.py`, etc.) and `core/orchestrator.py`.
  * **Modified By:** User (during project initialization).
  * **Role:** Global Context Injection. Every variable defined here is available to be injected into agent prompts via the `{{variable}}` syntax.

-----

## 2\. JSON Structure

This file defines the high-level creative direction.

```json
{
  "meta": {
    "title": "Neon Rain",
    "author": "User Name",
    "series": "The Cyberpunk Chronicles",
    "target_audience": "Adult Sci-Fi"
  },
  "style": {
    "genre": "Cyberpunk Noir",
    "tone": "Gritty, atmospheric, cynical but hopeful",
    "pov": "Third Person Limited",
    "tense": "Past Tense",
    "pacing": "Fast-paced action mixed with slow investigative beats"
  },
  "constraints": {
    "chapter_target_word_count": 2500,
    "forbidden_tropes": ["Deus Ex Machina", "Love Triangles"],
    "required_themes": ["Transhumanism", "Corporate Greed"]
  },
  "formatting": {
    "use_british_spelling": false,
    "chapter_header_format": "## Chapter {{n}}: {{title}}"
  }
}
```

-----

## 3\. Field Definitions

### I. Metadata (`meta`)

Bibliographic data used for file naming and context setting.

| Field | Type | Description |
| :--- | :--- | :--- |
| `title` | String | The working title of the book. Injected as `{{title}}`. |
| `series` | String | (Optional) Context for continuity if this is part of a larger work. |
| `target_audience` | String | Helps the AI adjust vocabulary complexity (e.g., "Middle Grade" vs "Adult"). |

### II. Style Guidelines (`style`)

These fields heavily influence the **Narrator Service's** output generation.

| Field | Type | Description |
| :--- | :--- | :--- |
| `genre` | String | The primary genre (e.g., "High Fantasy"). Sets the baseline for tropes and vocabulary. |
| `tone` | String | Adjectives describing the mood (e.g., "Whimsical", "Dark"). Injected into the Narrator's system prompt. |
| `pov` | **Enum** | • `First Person` ("I said")<br>• `Third Person Limited` ("He said", sticking to one head)<br>• `Third Person Omniscient` ("He said", knowing all thoughts) |
| `tense` | **Enum** | • `Past Tense` ("He walked")<br>• `Present Tense` ("He walks") |

### III. Structural Constraints (`constraints`)

Hard rules enforced by **The Architect Service** and **The Editor Service**.

| Field | Type | Description |
| :--- | :--- | :--- |
| `chapter_target_word_count` | Integer | The goal for the **Narrator**. The **Architect** uses this to determine when a chapter is "Drafting" vs "Review Ready". |
| `forbidden_tropes` | Array\<String\> | A blacklist for the **Editor**. If detected, the Editor will flag the chapter as `FAIL`. |
| `required_themes` | Array\<String\> | A whitelist for the **Architect**. Used to generate plot beats that adhere to the core message. |

### IV. Formatting Rules (`formatting`)

Mechanical rules for the text output.

| Field | Type | Description |
| :--- | :--- | :--- |
| `use_british_spelling` | Boolean | Toggles between "Color/Center" (False) and "Colour/Centre" (True). |
| `chapter_header_format` | String | Template string for the top of every generated `.md` file. |

-----

## 4\. Context Injection Strategy

The variables in this file are flattened and passed to the specific AI Service functions during execution.

**Example Mapping:**

If `personas.json` contains:

> *"You are a writer of {{genre}} fiction. Maintain a {{tone}} voice."*

And `project_conf.json` contains:

> `genre`: "Space Opera"
> `tone`: "Epic and Grandiose"

The final System Prompt sent to the Brain will be:

> *"You are a writer of Space Opera fiction. Maintain a Epic and Grandiose voice."*

-----

## 5\. Logic Mapping

  * **`ai_services/*.py`:** Parses this file to hydrate prompt templates before calling the Brain.
  * **`core/scanner.py`:** Uses `chapter_target_word_count` to calculate progress percentages for the Matrix.
  * **`core/orchestrator.py`:** Uses `chapter_header_format` when instructing the Narrator Service to initialize a new file.
  * **`ai_services/editor.py`:** Uses `forbidden_tropes` as negative constraints in its validation prompt.