# TextCraft Character Schema (`data/story_bible/characters.json`)

**Version:** 2.1.0 (Refactored for Specialized Services)
**Status:** Core Definition
**Role:** The Narrative Source of Truth

-----

## 1\. Overview

The **Character Schema** (`data/story_bible/characters.json`) serves as the central registry for the story's cast. In the TextCraft architecture, this file replaces scattered notes or "memory streams" with a rigid, structured definition of every entity in the story.

This file acts as the **Constraint Mechanism** for the **Narrator Service** (ensuring consistent voices/descriptions) and the **Truth Table** for the **Editor Service** (flagging continuity errors like a character knowing a secret they shouldn't).

  * **Read By:** `ai_services/narrator.py` (Context Injection), `ai_services/editor.py` (Fact Checking).
  * **Modified By:** User (during world-building) or **The Architect Service** (if authorized to expand the cast).
  * **Role:** Consistency Enforcement. Ensures "Sarah" doesn't have blue eyes in Chapter 1 and brown eyes in Chapter 3.

-----

## 2\. JSON Structure

The file uses a dictionary format where the **Key** is a unique, immutable ID (slug) for the character.

```json
{
  "kael_voss": {
    "name": "Kael Voss",
    "aliases": ["The Ghost", "K"],
    "role": "Protagonist",
    "archetype": "Reluctant Hero",
    "appearance": {
      "age": 30,
      "features": "Scar above left eye, cybernetic right arm",
      "clothing": "Worn leather trenchcoat, military boots"
    },
    "psychology": {
      "traits": ["Cynical", "Protective", "Impulsive"],
      "fears": ["Betrayal", "Closed spaces"],
      "motivation": "To clear his name"
    },
    "voice": {
      "tone": "Gruff, concise, uses street slang",
      "catchphrases": ["Not my problem."]
    },
    "relationships": {
      "mara_syn": "Former Partner / Rival",
      "doc_riley": "Mentor"
    },
    "inventory": ["Plasma Revolver", "Encrypted Data Chip"]
  },
  "mara_syn": {
    "name": "Mara Syn",
    "role": "Antagonist",
    "archetype": "Femme Fatale",
    "appearance": { "age": 28, "features": "Neon blue hair" },
    "relationships": { "kael_voss": "Target" }
  }
}
```

-----

## 3\. Field Definitions

### I. Identity

| Field | Type | Description |
| :--- | :--- | :--- |
| `Key` (Root) | String | **Immutable ID.** Snake\_case unique identifier (e.g., `kael_voss`). Used by the logic layer to track entity presence in scenes. |
| `name` | String | The display name used in the prose. |
| `aliases` | Array\<String\> | Valid alternative names the Narrator can use to vary sentence structure. |
| `role` | **Enum** | • `Protagonist`<br>• `Antagonist`<br>• `Deuteragonist` (Secondary Main)<br>• `Supporting`<br>• `Minor` |
| `archetype` | String | A shorthand for the LLM to ground behavior (e.g., "The Mentor", "The Jester"). |

### II. Physicality (`appearance`)

These fields are injected into the **Narrator Service's** context to ensure descriptive consistency.

| Field | Type | Description |
| :--- | :--- | :--- |
| `age` | Integer/String | "30" or "Ancient". |
| `features` | String | Permanent physical markers (eye color, scars, height, build). |
| `clothing` | String | Default attire (unless overridden by the specific scene context). |

### III. Psychology (`psychology`)

These fields drive the **Narrator Service's** decision-making regarding dialogue and reaction.

| Field | Type | Description |
| :--- | :--- | :--- |
| `traits` | Array\<String\> | Adjectives defining personality (e.g., "Stoic", "Greedy"). |
| `fears` | Array\<String\> | Psychological weaknesses to be exploited by the **Architect**. |
| `motivation` | String | The "Want" vs "Need" driving the character through the plot. |

### IV. Dialogue (`voice`)

| Field | Type | Description |
| :--- | :--- | :--- |
| `tone` | String | Instructions for dialogue generation (e.g., "Formal", "Stutters when nervous"). |
| `catchphrases` | Array\<String\> | Specific phrases the character is known to use. |

### V. Graph Data

| Field | Type | Description |
| :--- | :--- | :--- |
| `relationships` | Dictionary | **Key:** Character ID of the target.<br>**Value:** Description of the dynamic (e.g., "Secretly in love with"). Used to color interactions. |
| `inventory` | Array\<String\> | Key items currently in possession. Checked by **The Editor** for continuity (e.g., "Did he drop the gun?"). |

-----

## 4\. Context Injection Strategy

The **Architect Service** determines which characters are present in a scene. The **Orchestrator** then passes this list to the **Narrator Service**, which extracts *only* those specific JSON objects to build the prompt.

**Scenario:** *Writing Chapter 2, Scene 1 (Kael meets Mara).*

**The Prompt Context Receives:**

```json
[
  { "name": "Kael Voss", "role": "Protagonist", "voice": "Gruff..." },
  { "name": "Mara Syn", "role": "Antagonist", "voice": "Seductive..." }
]
```

*(Minor characters not present in the scene are excluded to save context window tokens.)*

-----

## 5\. Logic Mapping

  * **`core/orchestrator.py`:** Reads the `relationships` graph (via Architect output) to determine scene conflict.
  * **`ai_services/editor.py`:** Uses the `appearance` and `inventory` fields to validate continuity. (e.g., *Error: Text says Kael has blue eyes, Schema says brown.*)
  * **`ai_services/narrator.py`:** Hydrates the `{{character_context}}` variable in the System Prompt.