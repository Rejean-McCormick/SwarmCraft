import asyncio
import json
import logging
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from ai_services import client

logger = logging.getLogger(__name__)


def _load_json(path: Path, default: Any) -> Any:
    try:
        if not path.exists():
            return default
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    tmp.replace(path)


def _deep_merge(base: Any, patch: Any) -> Any:
    if patch is None:
        return base

    if isinstance(base, dict) and isinstance(patch, dict):
        merged = dict(base)
        for k, v in patch.items():
            if k in merged:
                merged[k] = _deep_merge(merged[k], v)
            else:
                merged[k] = v
        return merged

    if isinstance(base, list) and isinstance(patch, list):
        out = list(base)
        for item in patch:
            if item not in out:
                out.append(item)
        return out

    return patch


def _extract_json_object(text: str) -> Optional[Dict[str, Any]]:
    if not isinstance(text, str):
        return None

    text = text.strip()
    if not text:
        return None

    try:
        return json.loads(text)
    except Exception:
        pass

    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return None

    candidate = text[start : end + 1]
    candidate = re.sub(r"^```(?:json)?\s*", "", candidate.strip(), flags=re.IGNORECASE)
    candidate = re.sub(r"\s*```$", "", candidate.strip())

    try:
        return json.loads(candidate)
    except Exception:
        return None


def _print_header(title: str) -> None:
    print("\n" + ("=" * len(title)))
    print(title)
    print(("=" * len(title)) + "\n")


async def run_interview(
    project_root: Path,
    model: str,
    temperature: float = 0.5,
    max_turns: int = 12,
    focus_chapter: Optional[str] = None,
) -> Dict[str, Any]:
    bible_dir = project_root / "data" / "story_bible"
    project_conf_path = bible_dir / "project_conf.json"
    characters_path = bible_dir / "characters.json"
    locations_path = bible_dir / "locations.json"
    timeline_path = bible_dir / "timeline.json"
    story_brief_path = bible_dir / "story_brief.json"

    existing_project_conf: Dict[str, Any] = _load_json(project_conf_path, default={})
    existing_characters: Dict[str, Any] = _load_json(characters_path, default={})
    existing_locations: Dict[str, Any] = _load_json(locations_path, default={})
    existing_timeline: Dict[str, Any] = _load_json(timeline_path, default={"events": []})
    existing_story_brief: Dict[str, Any] = _load_json(story_brief_path, default={})

    # Load chapter content if focusing on a specific chapter
    chapter_content = ""
    chapter_info = {}
    if focus_chapter:
        manuscripts_dir = project_root / "data" / "manuscripts"
        matrix_path = project_root / "data" / "matrix.json"
        matrix = _load_json(matrix_path, default={})
        
        # Find the chapter file
        chapter_info = matrix.get("content", {}).get(focus_chapter, {})
        if chapter_info:
            chapter_path = project_root / chapter_info.get("path", "")
            if chapter_path.exists():
                chapter_content = chapter_path.read_text(encoding="utf-8")
        
        # Also check for file by pattern
        if not chapter_content:
            for f in manuscripts_dir.glob(f"{focus_chapter}*.md"):
                chapter_content = f.read_text(encoding="utf-8")
                break
        
        _print_header(f"Chapter Interview: {focus_chapter}")
        print(f"Focusing on chapter: {focus_chapter}")
        if chapter_content:
            print(f"Chapter has {len(chapter_content.split())} words.")
        print("Type 'done' to finalize, or 'exit' to abort without saving.")
    else:
        _print_header("Story Interview")
        print("Type 'done' to finalize, or 'exit' to abort without saving.")

    # Build appropriate system prompt based on mode
    if focus_chapter:
        system_prompt = f"""
You are a story development interviewer focusing on improving a SPECIFIC CHAPTER.

Target Chapter: {focus_chapter}
Current Chapter Content (first 2000 chars):
{chapter_content[:2000] if chapter_content else "(No content yet)"}

Editor Notes (if any):
{json.dumps(chapter_info.get("editor_notes", []), indent=2)}

Goal: Ask the user targeted questions to improve THIS SPECIFIC CHAPTER. Focus on:
1. What's working well in this chapter?
2. What needs to change or improve?
3. Specific scenes, dialogue, or descriptions to revise
4. Character voice/motivation issues
5. Pacing or structure problems
6. Missing details or context

Rules:
- Ask ONE question at a time.
- Reference specific parts of the chapter content when asking.
- Focus on actionable improvements.
- Never output JSON in the interview phase. Just the next question.
"""
    else:
        system_prompt = """
You are a story development interviewer.

Goal: Ask the user concise, high-leverage questions that produce a complete, usable story brief for a novel.

Rules:
- Ask ONE question at a time.
- Prefer multiple-choice when it helps, but allow freeform.
- Use the user's previous answers to drill deeper.
- Cover these topics IN ORDER:
  1. Premise/logline - what's the story about in one sentence?
  2. Genre/tone/style - what feel are we going for?
  3. POV/tense - who tells the story and how?
  4. Theme - what's the deeper meaning?
  5. Setting rules - magic systems, tech levels, world constraints
  6. Main cast - protagonist, antagonist, supporting characters with motivations
  7. Character arcs - how do main characters change?
  8. CHAPTER STRUCTURE - How many chapters? What happens in each? Get specific titles/summaries for each chapter.
  9. Major plot beats - inciting incident, midpoint turn, dark night, climax, resolution
  10. Plot twists - at least 2 surprising turns
  11. Ending - how does it conclude?
  12. Constraints - forbidden tropes, things to avoid
- For CHAPTER STRUCTURE, push for specifics: "Give me a title and 1-2 sentence summary for each chapter"
- Keep each question short.
- Never output JSON in the interview phase. Just the next question.
""".strip()

    seed_context = {
        "project_conf": existing_project_conf,
        "story_brief": existing_story_brief,
        "characters": list(existing_characters.keys())[:20],
        "locations": list(existing_locations.keys())[:20],
        "timeline_event_ids": [e.get("id") for e in (existing_timeline.get("events") or []) if isinstance(e, dict)][:20],
    }

    messages: List[Dict[str, str]] = [
        {"role": "system", "content": system_prompt},
        {
            "role": "user",
            "content": "Start the interview. Ask the first question. Here is existing context (may be empty):\n" + json.dumps(seed_context, indent=2),
        },
    ]

    transcript: List[Dict[str, str]] = []

    for _ in range(max_turns):
        resp = await client.generate(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=300,
        )

        if resp.get("status") != "success":
            return {"status": "error", "message": resp.get("message") or "Interview model call failed."}

        question = (resp.get("data") or {}).get("content") or ""
        question = question.strip()
        if not question:
            question = "What kind of story do you want to write?"

        print(question)
        answer = input("> ").strip()

        if answer.lower() in {"exit", "quit"}:
            return {"status": "aborted"}

        if answer.lower() in {"done", "finish", "finalize"}:
            break

        transcript.append({"question": question, "answer": answer})
        messages.append({"role": "assistant", "content": question})
        messages.append({"role": "user", "content": answer})

    _print_header("Extracting Story Brief" if not focus_chapter else f"Extracting {focus_chapter} Revisions")

    # Use different extractor for chapter-specific interviews
    if focus_chapter:
        extractor_system = f"""
You are a strict JSON generator for chapter revisions.

Target Chapter: {focus_chapter}

Task: Convert the chapter interview transcript into a JSON object with these keys:
- chapter_id: string (the chapter being revised, e.g. "{focus_chapter}")
- director_override: string (a command to queue for the narrator to revise this chapter based on the interview)
- revision_notes: array of strings (specific changes/improvements to make)
- character_updates: object (any character detail changes discovered, keyed by character_id)
- continuity_fixes: array of strings (any continuity issues to address)
- open_questions: array of strings (anything still ambiguous)

The director_override should be actionable, e.g.:
"revise {focus_chapter}: improve the dialogue between X and Y, add more sensory details to the office scene, fix the pacing in the second half"

Hard requirements:
- Output raw JSON only. No markdown.
- Focus only on changes for THIS chapter.
""".strip()
    else:
        extractor_system = """
You are a strict JSON generator.

Task: Convert the interview transcript into a single JSON object with EXACTLY these top-level keys:
- project_conf_patch: object (patch to merge into project_conf.json)
- story_brief: object (a complete story blueprint to write to story_bible/story_brief.json)
- characters: object (dictionary keyed by character_id in snake_case, values follow the characters.json schema)
- locations: object (dictionary keyed by location_id in snake_case)
- timeline: object with key events: array of objects {id,name,timestamp,description,participants,location,status}
- director_override: string (a short command the user could paste into the Director Override to start drafting)
- open_questions: array of strings (anything still ambiguous)

Hard requirements:
- Output raw JSON only. No markdown.
- Use snake_case IDs.
- Keep timeline timestamps ISO-8601 if possible; otherwise omit timestamp or use null.

Story brief requirements:
- Must be a JSON object suitable to write directly to story_bible/story_brief.json.
- MUST include:
  - logline: string
  - premise: string 
  - themes: array of strings
  - setting_rules: array of strings or object
  - structure: object with:
    - acts: array of {name, beats: array of strings}
    - chapters: array of {number, title, summary, key_events, characters_involved}
      (CRITICAL: Extract as many chapters as discussed, with specific titles and summaries)
  - plot_twists: array of strings
  - character_arcs: object keyed by character_id with arc descriptions
  - ending: string or object describing the resolution

Chapter extraction is CRITICAL for the writing engine to work properly. Each chapter should have:
- number: integer (1, 2, 3...)
- title: string (chapter title)
- summary: string (1-3 sentences describing what happens)
- key_events: array of strings (major plot points in this chapter)
- characters_involved: array of character_ids
""".strip()

    extractor_user = {
        "existing_project_conf": existing_project_conf,
        "existing_story_brief": existing_story_brief,
        "existing_characters": existing_characters,
        "existing_locations": existing_locations,
        "existing_timeline": existing_timeline,
        "interview_transcript": transcript,
    }

    extraction_max_tokens = int(os.getenv("INTERVIEW_EXTRACTION_MAX_TOKENS", "16000"))
    extraction_max_tokens = max(500, min(extraction_max_tokens, 20000))

    try:
        extract_resp = await client.generate(
            messages=[
                {"role": "system", "content": extractor_system},
                {"role": "user", "content": json.dumps(extractor_user, indent=2)},
            ],
            model=model,
            temperature=0.2,
            max_tokens=extraction_max_tokens,
        )
    except Exception as e:
        logger.error(f"Extraction model call failed: {e}")
        return {"status": "error", "message": f"Extraction model call failed: {e}"}

    if extract_resp.get("status") != "success":
        return {"status": "error", "message": extract_resp.get("message") or "Extraction call failed."}

    raw = (extract_resp.get("data") or {}).get("content") or ""
    extracted = _extract_json_object(raw)
    if not extracted:
        return {"status": "error", "message": "Could not parse JSON from interviewer extractor.", "raw": raw}

    # Handle chapter-specific interview results differently
    if focus_chapter:
        # Save the chapter revision notes
        revision_path = bible_dir / f"chapter_revisions_{focus_chapter}.json"
        _write_json(revision_path, extracted)
        
        # Update characters if any were discovered
        character_updates = extracted.get("character_updates") or {}
        if character_updates:
            merged_characters = _deep_merge(existing_characters, character_updates)
            _write_json(characters_path, merged_characters)
        
        # Queue the director override automatically
        director_override = extracted.get("director_override", "")
        if director_override:
            control_path = project_root / "data" / "control.json"
            control = _load_json(control_path, default={})
            if not isinstance(control, dict):
                control = {}
            control.setdefault("system_status", "RUNNING")
            control["architect_override"] = {
                "active": True,
                "instruction": director_override,
                "force_target": focus_chapter,
            }
            _write_json(control_path, control)
        
        return {
            "status": "success",
            "focus_chapter": focus_chapter,
            "written": {
                "revision_notes": str(revision_path),
                "characters": str(characters_path) if character_updates else None,
            },
            "director_override": director_override,
            "revision_notes": extracted.get("revision_notes", []),
            "open_questions": extracted.get("open_questions", []),
        }

    project_conf_patch = extracted.get("project_conf_patch") or {}
    story_brief_patch = extracted.get("story_brief") or {}
    characters_patch = extracted.get("characters") or {}
    locations_patch = extracted.get("locations") or {}
    timeline_patch = extracted.get("timeline") or {}

    merged_project_conf = _deep_merge(existing_project_conf, project_conf_patch)
    merged_story_brief = _deep_merge(existing_story_brief, story_brief_patch)
    merged_characters = _deep_merge(existing_characters, characters_patch)
    merged_locations = _deep_merge(existing_locations, locations_patch)

    existing_events = existing_timeline.get("events") if isinstance(existing_timeline, dict) else []
    if not isinstance(existing_events, list):
        existing_events = []

    patch_events = timeline_patch.get("events") if isinstance(timeline_patch, dict) else []
    if not isinstance(patch_events, list):
        patch_events = []

    existing_ids = {e.get("id") for e in existing_events if isinstance(e, dict) and e.get("id")}
    for e in patch_events:
        if not isinstance(e, dict):
            continue
        eid = e.get("id")
        if eid and eid in existing_ids:
            continue
        existing_events.append(e)
        if eid:
            existing_ids.add(eid)

    merged_timeline = dict(existing_timeline) if isinstance(existing_timeline, dict) else {}
    merged_timeline["events"] = existing_events

    _write_json(project_conf_path, merged_project_conf)
    _write_json(story_brief_path, merged_story_brief)
    _write_json(characters_path, merged_characters)
    _write_json(locations_path, merged_locations)
    _write_json(timeline_path, merged_timeline)

    interview_out_path = bible_dir / "interview_output.json"
    _write_json(interview_out_path, extracted)

    seed_dir = project_root / "data" / "storyseed"
    seed_name = f"storyseed_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    storyseed_path = seed_dir / seed_name
    _write_json(storyseed_path, extracted)

    return {
        "status": "success",
        "written": {
            "project_conf": str(project_conf_path),
            "story_brief": str(story_brief_path),
            "characters": str(characters_path),
            "locations": str(locations_path),
            "timeline": str(timeline_path),
            "interview_output": str(interview_out_path),
            "storyseed": str(storyseed_path),
        },
        "director_override": extracted.get("director_override"),
        "open_questions": extracted.get("open_questions") or [],
    }


def run_interview_sync(
    project_root: Path,
    model: str,
    temperature: float = 0.5,
    max_turns: int = 12,
) -> Dict[str, Any]:
    return asyncio.run(run_interview(project_root=project_root, model=model, temperature=temperature, max_turns=max_turns))
