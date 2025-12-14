# Handoff

## Summary

This change adds an interactive **story interview** workflow that captures story preferences (genre, tone, characters, arcs, plot beats/twists, ending) and persists them into the active project’s **Story Bible** so the existing pipeline (Architect → Narrator → Editor) reliably uses them.

Key idea: store the interview’s “creative blueprint” in `data/story_bible/story_brief.json`, and auto-inject it into service prompts (even if persona prompts don’t explicitly include `{{story_brief}}`).

This change also adds an engine-side **project/seed chooser** and an interactive **Director Console** (`director>`) so you can steer the swarm while the engine loop is running.

## How to run

### 1) Run interactive interview

```bash
python main.py --interview
```

Optional:

```bash
python main.py --interview --project <project_id>
python main.py --interview --interview-chapter ch04 --project <project_id>
python main.py --interview --interview-model <model>
python main.py --interview --interview-temperature 0.6 --interview-turns 16
```

Interview controls:
- Type `done` to finalize and extract JSON
- Type `exit` to abort without saving

### 2) Start the engine

```bash
python main.py
```

On startup (TTY only), you will be prompted to:
- continue an existing project
- start a new project from a `storyseed_*.json`
- start a blank project

Flags:
- `--project <project_id>`: run a specific project (engine or interview)
- `--no-project-prompt`: skip the chooser
- `--no-director-console`: disable the interactive `director>` console
- `--inject-interview <JSON_PATH>`: import interview/storyseed JSON directly into a project (no Q&A)
- `--interview-chapter <CHAPTER>`: focus the interview on a specific chapter (e.g. `ch04` or `4`) and queue a targeted revision override

(Optional) Start the dashboard in another terminal:

```bash
python dashboard.py
```

## Outputs / persisted artifacts

The interview extracts structured JSON and merges it into the active project’s Story Bible:

- `projects/<project_id>/data/story_bible/project_conf.json`
- `projects/<project_id>/data/story_bible/story_brief.json` (new / primary blueprint)
- `projects/<project_id>/data/story_bible/characters.json`
- `projects/<project_id>/data/story_bible/locations.json`
- `projects/<project_id>/data/story_bible/timeline.json`
- `projects/<project_id>/data/story_bible/interview_output.json` (raw extracted payload snapshot)
- `projects/<project_id>/data/story_bible/chapter_revisions_chXX.json` (chapter-specific interview output; only written when using `--interview-chapter`)

Additional artifact:
- `projects/<project_id>/data/storyseed/storyseed_YYYYMMDD_HHMMSS.json` (timestamped seed snapshot)

When you start a new project from a seed, the seed is copied into the new project’s `data/storyseed/` and used to populate the Story Bible.

## Interaction model (how the user steers the swarm)

The engine is file-driven and reacts to the active project’s `data/control.json`.

Primary controls:
- `system_status`: `RUNNING | PAUSED | STOP`
- `architect_override`:
  - `active`: boolean
  - `instruction`: string
  - `force_target`: optional manuscript filename

In engine mode (TTY), `main.py` also starts an interactive **Director Console**:
- Type `help` to see commands.
- Any freeform line becomes an override instruction.
- Example:
  - `director> target ch02_Rising_Action.md`
  - `director> override continue drafting chapter 2, increase tension and foreshadow betrayal`

Recent UX improvements:
- `start` is accepted as an alias for `resume`.
- Short aliases: `p`/`pa` (pause), `r`/`re` (resume), `st`/`s` (stop), `q` (quit).
- Queuing an override now also sets `system_status` to `RUNNING` so you don't need a separate `resume`.
- Stray short inputs (e.g. `t`) no longer get treated as overrides.

## Runtime tuning

Environment flags:
- `INTERVIEW_EXTRACTION_MAX_TOKENS`: sets extraction `max_tokens` for the interview JSON extraction call (clamped for safety).
- `AUTO_CONTINUE_DRAFTING=1`: legacy toggle for continuing `DRAFTING` chapters toward word targets (the orchestrator now continues drafting by default).

## Code changes

### New
- `ai_services/interviewer.py`
  - Runs the interview loop.
  - Runs a second “extractor” model call that outputs strict JSON.
  - Merges extracted payloads into Story Bible JSON files.
  - Chapter interview mode (`--interview-chapter`) reads the target chapter content + editor notes, extracts revision JSON, and queues a targeted override in `data/control.json`.

### Updated
- `main.py`
  - Added flags: `--interview`, `--interview-chapter`, `--interview-model`, `--interview-temperature`, `--interview-turns`, `--inject-interview`, `--project`.
  - Interview requires TTY.

- `core/project_manager.py`
  - New projects now scaffold `data/story_bible/story_brief.json` with a stable default structure.

- `ai_services/architect.py`
  - Loads `story_brief.json` (optional) and injects it into the system prompt.

- `ai_services/narrator.py`
  - Loads `story_brief.json` and injects it into the system prompt.
  - Iteration behavior: if the target manuscript already has content, the narrator now writes an addendum/continuation intended to be appended (instead of overwriting the file).
  - For "improve"/"revise" requests on existing chapters, the addendum begins with a brief reiteration/recap before applying the requested improvement.

- `core/agent_tools.py`
  - Added `append_file` to support safe iterative continuation without overwriting manuscripts.

- `main.py`
  - Director Console improvements: `start` alias for resume, short aliases, override auto-resume, and guardrails against accidental short-input overrides.

- `core/orchestrator.py`
  - Improved idle log messaging with explicit tips on how to continue drafting via Director Console (`override ...`, `target ...`, then `start`).
  - Applies editor verdicts to `matrix.json` (PASS -> `LOCKED`, FAIL -> `continuity_check=FAIL` with `editor_notes`).
  - Auto-creates the next chapter when all existing chapters are `LOCKED`.
  - Derives chapter titles from `story_brief.structure.chapters` when available; otherwise falls back to `story_brief.structure.acts[].beats[]`.
  - Avoids idle loops when `DRAFTING` chapters exist by continuing to plan/write until they reach review.

## Quick verification

1. Start the engine:

```bash
python main.py
```

2. In `director>` queue a follow-up change to an existing chapter:

```text
override improve chapter 1 with mention of tokens and its impact on the environment
```

3. Confirm `projects/<project_id>/data/manuscripts/ch01_Start.md` keeps existing text and appends a new addendum.

- `ai_services/editor.py`
  - Loads `story_brief.json` and injects it into the system prompt.

## Notes / assumptions

- The interview writes into the **project-scoped** directory under `projects/<project_id>/...`, not `SwarmCraft/data/...`.
- The injection behavior is resilient: if persona prompts omit `{{story_brief}}`, the services append a `STORY BRIEF (Source of Truth)` block.
- Merging behavior:
  - dicts are deep-merged
  - lists are union-merged (dedup by equality)
  - timeline events are appended if the `id` is new

## Loop / convergence fix (post-handoff)

This update addresses an engine behavior where the Orchestrator could loop indefinitely on the same chapter (e.g. `ch04_Continuation.md`) after an Editor `FAIL`.

Key changes:
- Orchestrator treats Architect `action_type=wait` as a real idle by sleeping `IDLE_DELAY_SECONDS` (reduces tight-loop model spam when Architect can’t produce valid JSON or has no work).
- After a successful Narrator fix pass (`action_type=edit`), Orchestrator clears `continuity_check` from `FAIL` -> `PENDING` so the chapter can return to Editor review instead of being endlessly re-assigned to Narrator.
- Narrator now respects Architect intent: `action_type=edit` forces REVISE mode (targeted `edit_file`) rather than appending continuation text.
- Narrator success reporting is stricter: in REVISE mode it must perform at least one `edit_file` call, and any failed file operation causes Narrator to return `status=error` (prevents false “success” loops).

## Known limitations

- ChromaDB is optional; if it is not installed, RAG memory is disabled and the engine logs that it is offline.
