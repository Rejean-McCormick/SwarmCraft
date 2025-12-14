# Changes

## Unreleased

### Pipeline & Orchestration Fixes
- Fixed orchestrator to properly process editor verdicts: chapters now get marked LOCKED after passing review, FAIL with notes if rejected.
- Added automatic chapter progression: when all chapters are LOCKED, the orchestrator creates the next chapter file based on story_brief structure.
- Orchestrator now reads chapter titles from `story_brief.structure.chapters` array to name new chapters appropriately.
- Improved idle detection: if any chapters are `DRAFTING`, the engine will keep planning/writing instead of idling.
- Fixed infinite revision loops: after a successful narrator fix pass (`action_type=edit`), orchestrator clears `continuity_check` from FAIL -> PENDING so the chapter can be re-reviewed.
- Made `wait` decisions actually idle: orchestrator now sleeps `IDLE_DELAY_SECONDS` when Architect returns `action_type=wait` to avoid tight-looping.
- Hardened narrator convergence: `action_type=edit` forces REVISE mode (targeted `edit_file`), and narrator now returns error if required edit calls are missing or any file operation fails.
- If `story_brief.structure.chapters` is missing, chapter titles are now derived from `story_brief.structure.acts[].beats[]` so filenames are more meaningful than `Continuation`.
- Auto-continue drafting is now enabled by default without requiring the `AUTO_CONTINUE_DRAFTING` environment variable.

### Narrator Improvements (File Overwriting Fix)
- Added operation mode detection: narrator now distinguishes between GENERATE (new file), CONTINUE (append), and REVISE (targeted edits).
- Added `edit_file` tool to narrator for surgical revisions instead of appending replacement content.
- Keywords like "improve", "revise", "edit", "fix" trigger REVISE mode which uses find-and-replace edits.
- Keywords like "continue", "next", "extend", "draft" trigger CONTINUE mode which appends new content.
- This fixes the issue where files were being overwritten instead of properly modified.

### Interview Enhancements
- Enhanced interview prompts to explicitly cover chapter structure with specific titles and summaries for each chapter.
- Updated extractor to require `structure.chapters` array with: number, title, summary, key_events, characters_involved.
- Chapter extraction is now critical for the writing engine to know what to write in each chapter.
- Added chapter-specific interview mode: `python main.py --interview --interview-chapter ch04` to iterate on a single chapter.
- Chapter interview extraction now produces revision JSON and queues an `architect_override` automatically to revise the targeted chapter.

### New: Inject Interview Command
- Added `--inject-interview <JSON_PATH>` flag to import interview/storyseed JSON directly into a project.
- Skips the Q&A phase and goes straight to merging data into story bible files.
- Useful for restoring from backups or importing externally-created story structures.

---

- Added Requesty Router support via `REQUESTY_API_KEY` and `REQUESTY_BASE_URL` (OpenAI-compatible `/chat/completions`).
- Added interactive setup wizard (`python main.py --setup`) to pick provider, key, base URL, and model; writes updates to `.env` and supports masked key entry.
- Added router model normalization so bare model IDs (e.g. `gpt-5-nano`) are automatically prefixed to `provider/model` using `ROUTER_DEFAULT_PROVIDER`.
- Added `MODEL_OVERRIDE` to force a single model across Architect/Narrator/Editor (useful when personas specify non-router model IDs).
- Improved OpenAI-compatible response normalization and error handling (detect upstream `error`, handle empty/variant response shapes, retry on invalid payloads).
- Added GPT-5 safeguards for Requesty router (`reasoning_effort` defaults and minimum token budget via `GPT5_MIN_MAX_TOKENS`) to prevent empty outputs.
- Fixed `core/scanner.py` truncation/syntax error and restored scanning logic to keep `matrix.json` consistent.
- Made ChromaDB optional; when not installed, RAG memory is disabled gracefully.
- Hardened Architect prompt and parsing (strict schema guidance, tolerant key normalization, fixed f-string JSON example escaping).
- Added interactive story interview mode (`python main.py --interview`) with selectable model/temperature/turn limits and optional `--project` targeting.
- Added `ai_services/interviewer.py` to run an AI-driven Q&A and extract a structured Story Bible from answers.
- Added `data/story_bible/story_brief.json` as a first-class story blueprint (logline/premise/themes/beats/twists/arcs/ending) and scaffolded it for new projects.
- Wired `story_brief.json` into Architect/Narrator/Editor prompt hydration (auto-injected even if persona prompts do not include `{{story_brief}}`).
- Interview now persists/merges `story_brief.json` alongside `project_conf.json`, `characters.json`, `locations.json`, and `timeline.json`.
- Improved robustness of interview extraction when providers return empty `message.content` (e.g. `finish_reason=length`): clearer errors and clean failure path instead of crashing.
- Added `INTERVIEW_EXTRACTION_MAX_TOKENS` to configure interview extraction output length (clamped for safety).
- Interview now writes a timestamped seed snapshot to `projects/<project_id>/data/storyseed/storyseed_YYYYMMDD_HHMMSS.json`.
- Engine startup now prompts to continue an existing project or start a new project from a storyseed (TTY only). Added `--no-project-prompt`.
- Added an interactive `director>` console (TTY only) to queue overrides/targets/pause/resume/stop while the engine runs. Added `--no-director-console`.
- Reduced idle-loop model spam by skipping Architect calls when there is no actionable work.
- Added `AUTO_CONTINUE_DRAFTING=1` option to allow the engine to continue drafting chapters toward target word count.

- Fixed Narrator iteration behavior so existing manuscript files are no longer overwritten during follow-up requests (e.g. "improve chapter 1..."); the engine now appends an addendum/continuation instead.
- Added `append_file` to `core/agent_tools.py` and exposed it to the Narrator as a tool.
- Updated Narrator prompt/tool handling to prefer `append_file` when a manuscript already has content and to include brief reiteration/recap when the user asks to improve/revise an existing chapter.
- Improved Director Console UX: added `start` alias for resume, added short command aliases (`p`/`r`/`st`/`q`), prevented stray short inputs from being treated as overrides, and auto-resume when queuing an override.
- Improved idle guidance messaging to show the user how to continue into the next phase/chapter from the Director Console.
