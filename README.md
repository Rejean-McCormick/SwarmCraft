# SwarmCraft (Fork of mojomast/swarmussy) — v3.0.0

## **POWERED BY GROK** ⚡️

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/downloads/)

---

## Credit and Acknowledgements

This repository is a **Major Architectural Rewrite (Fork)** of the original project:

- **Original Code and Inspiration:** **[mojomast/swarmussy](https://github.com/mojomast/swarmussy)**
- **Rewrite / Architecture (v3.0):** **[Rejean-McCormick](https://github.com/Rejean-McCormick)**

---

## What SwarmCraft Is

SwarmCraft is a **deterministic story-engine** for long-form writing: it plans, drafts, reviews, and iterates on narrative content using a strict pipeline and a central state model.

It is designed for:
- **multi-project** story universes
- **long-term continuity** via RAG memory
- **human-friendly story scaffolding** (templates + outline grid)
- reliable orchestration that is **restart-safe** and **debuggable**

---

## Architectural Philosophy: Derived from the “Architect” Meta-Structure (AWA Influence)

SwarmCraft moves away from the multi-agent *chatroom* model and into a **Deterministic Pipeline** guided by the meta-structure of an “Architect” system: decouple creative intent and project state from agent logic, and enforce predictable state transitions.

| Principle | SwarmCraft Implementation | Benefit |
| :--- | :--- | :--- |
| **Decoupling / Statelessness** | Agents are **stateless services** (`ai_services/`). They execute a task and terminate. | Less complexity, improved crash recovery, easier debugging. |
| **Central Data Model** | The **Matrix** (`data/matrix.json`) is the machine-readable source of truth. | Eliminates state drift; every module sees the same project state. |
| **Deterministic Update Cycle** | Orchestrator enforces: **SCAN → PLAN → EXECUTE** | Predictable behavior and reproducible runs. |
| **Controlled World Mutation** | Agents modify the world only through controlled file ops (`agent_tools`). | Clear audit trail; scanner re-indexes the world reliably. |

---

## Core Story System (Scaffold + Parts)

SwarmCraft separates **creative intent** from **runtime state**:

### Story Bible (Creative Intent)
- **Templates:** `data/story_bible/templates/<template_id>.json`  
  Define thread sets (Plot, Character Development, etc.), cadence rules, and default parts/chapter.
- **Outline:** `data/story_bible/outline.json`  
  The structured scaffold: **chapters → parts mapping**, per-part thread beats, and per-part “contract” (goal/obstacle/turn/outcome).
- **Grid Editing:** The outline is displayed as a **spreadsheet-like grid** for humans (rows=threads, columns=parts), with optional CSV round-trip.

### Matrix (Runtime State)
- `data/matrix.json` tracks what exists, what’s drafted, what needs revision, and what’s locked.

### Parts
A **Part** is the atomic unit of work the system drafts/revises.
- Children’s book templates can use **1 part = 1 chapter**
- Other templates can use **1–6 parts per chapter** (user-configurable)

---

## ✨ Core Features

| Feature | Description | Enabled by |
| :--- | :--- | :--- |
| **Powered by Grok** | All writing/planning services run through Grok (via provider adapter). | `core/ai_client.py` (adapter layer) |
| **Multi-Project System** | Multiple isolated story universes; switch projects without restarting. | `core/project_manager.py` |
| **RAG Long-Term Memory** | Indexes prose into ChromaDB to maintain continuity at scale. | `core/memory_store.py` |
| **TUI Dashboard** | Real-time mission control using `textual`. | `dashboard.py` / `ui/` |
| **Deterministic Orchestration** | Reliable scan/plan/execute loop; restart-safe. | `core/orchestrator.py` |
| **Story Scaffold Templates** | Genre templates + outline grid + wizard-generated first scaffold. | `data/story_bible/` + addendum docs |

---

## ⚙️ Installation and Launch Guide

SwarmCraft runs as two decoupled processes. Use **two terminal windows**.

### 1. Setup

1. Clone the repository and enter the folder.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
