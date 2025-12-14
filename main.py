import asyncio
import os
import sys
import logging
from pathlib import Path
import argparse
import json
import re
from datetime import datetime
from dotenv import load_dotenv
from rich.console import Console
from rich.logging import RichHandler
from rich.panel import Panel
from rich.text import Text

# --- Constants ---
VERSION = "3.0.0"
BANNER = f"""
TextCraft Engine v{VERSION}
---------------------------
The Data-Driven AI Storyteller
"""

# Initialize Rich Console
console = Console()

def _read_json(path: Path, default=None):
    try:
        if not path.exists():
            return default
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default

def _write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    tmp.replace(path)

def _deep_merge(base, patch):
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
    return patch

def _slugify_project_id(text: str) -> str:
    text = (text or "").strip().lower()
    text = re.sub(r"[^a-z0-9_\-]+", "_", text)
    text = re.sub(r"_+", "_", text).strip("_")
    return text or f"project_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

def _list_storyseeds(projects_root: Path):
    seeds = []
    try:
        for seed_path in projects_root.glob("*/data/storyseed/*.json"):
            project_id = seed_path.parts[-4] if len(seed_path.parts) >= 4 else "?"
            seeds.append((project_id, seed_path))
    except Exception:
        return []
    return sorted(seeds, key=lambda x: (x[0], x[1].name))

def _import_storyseed_into_project(seed_path: Path, project_root: Path) -> str:
    seed = _read_json(seed_path, default=None)
    if not isinstance(seed, dict):
        raise ValueError(f"Invalid storyseed JSON: {seed_path}")

    bible_dir = project_root / "data" / "story_bible"
    project_conf_path = bible_dir / "project_conf.json"
    story_brief_path = bible_dir / "story_brief.json"
    characters_path = bible_dir / "characters.json"
    locations_path = bible_dir / "locations.json"
    timeline_path = bible_dir / "timeline.json"

    existing_project_conf = _read_json(project_conf_path, default={})
    merged_project_conf = _deep_merge(existing_project_conf, seed.get("project_conf_patch") or {})
    _write_json(project_conf_path, merged_project_conf)

    if isinstance(seed.get("story_brief"), dict):
        _write_json(story_brief_path, seed.get("story_brief") or {})
    if isinstance(seed.get("characters"), dict):
        _write_json(characters_path, seed.get("characters") or {})
    if isinstance(seed.get("locations"), dict):
        _write_json(locations_path, seed.get("locations") or {})
    if isinstance(seed.get("timeline"), dict):
        _write_json(timeline_path, seed.get("timeline") or {"events": []})

    # Preserve the seed snapshot inside the new project as well.
    seed_dir = project_root / "data" / "storyseed"
    seed_dir.mkdir(parents=True, exist_ok=True)
    seed_copy_path = seed_dir / seed_path.name
    try:
        if seed_copy_path.resolve() != seed_path.resolve():
            _write_json(seed_copy_path, seed)
    except Exception:
        pass

    # Ensure the initial manuscript is eligible for generation (avoid [TODO] marker which marks it DRAFTING).
    manu_path = project_root / "data" / "manuscripts" / "ch01_Start.md"
    manu_path.parent.mkdir(parents=True, exist_ok=True)
    with open(manu_path, "w", encoding="utf-8") as f:
        f.write("# Chapter 1: Start\n")

    director_override = seed.get("director_override")
    if isinstance(director_override, str) and director_override.strip():
        control_path = project_root / "data" / "control.json"
        control = _read_json(control_path, default={})
        if not isinstance(control, dict):
            control = {}
        control.setdefault("system_status", "RUNNING")
        control["architect_override"] = {
            "active": True,
            "instruction": director_override.strip(),
            "force_target": "ch01",
        }
        control.setdefault("runtime_settings", {"global_temperature": 0.7, "model_override": None})
        _write_json(control_path, control)

    return str(seed_copy_path)

def _prompt_project_choice(pm, console: Console, allow_seed: bool = True) -> str:
    projects = pm.list_projects()
    last = pm.get_last_active_project()

    console.print("\nChoose a story to work on:")
    if last:
        console.print(f"[dim]Last active:[/dim] {last}")

    idx = 1
    choices = {}
    for pid in projects:
        console.print(f"{idx}. Continue: {pid}")
        choices[str(idx)] = ("project", pid)
        idx += 1

    if allow_seed:
        console.print(f"{idx}. Start new from storyseed")
        choices[str(idx)] = ("seed", None)
        idx += 1

    console.print(f"{idx}. Start new blank project")
    choices[str(idx)] = ("blank", None)

    raw = input("> ").strip()
    picked = choices.get(raw)
    if not picked:
        return last or (projects[0] if projects else "default_project")

    kind, value = picked
    if kind == "project":
        return value

    if kind == "blank":
        title = input("Project title: ").strip() or "Untitled Story"
        project_id = _slugify_project_id(title)
        pm.create_project(project_id, title=title)
        pm.set_active_project(project_id)
        return project_id

    # kind == "seed"
    seeds = _list_storyseeds(pm.root)
    if not seeds:
        console.print("No storyseed files found under ./projects/*/data/storyseed")
        title = input("Project title: ").strip() or "Untitled Story"
        project_id = _slugify_project_id(title)
        pm.create_project(project_id, title=title)
        pm.set_active_project(project_id)
        return project_id

    console.print("\nPick a seed:")
    seed_choices = {}
    for i, (pid, spath) in enumerate(seeds, start=1):
        seed_obj = _read_json(spath, default={})
        seed_title = None
        if isinstance(seed_obj, dict):
            meta = (seed_obj.get("project_conf_patch") or {}).get("meta") if isinstance(seed_obj.get("project_conf_patch"), dict) else {}
            if isinstance(meta, dict):
                seed_title = meta.get("title")
        label = f"{pid}/{spath.name}"
        if isinstance(seed_title, str) and seed_title.strip():
            label += f"  ({seed_title.strip()})"
        console.print(f"{i}. {label}")
        seed_choices[str(i)] = spath

    raw_seed = input("> ").strip()
    seed_path = seed_choices.get(raw_seed)
    if not seed_path:
        return last or (projects[0] if projects else "default_project")

    seed_obj = _read_json(seed_path, default={})
    suggested_title = None
    if isinstance(seed_obj, dict):
        meta = (seed_obj.get("project_conf_patch") or {}).get("meta") if isinstance(seed_obj.get("project_conf_patch"), dict) else {}
        if isinstance(meta, dict):
            suggested_title = meta.get("title")

    title = (input(f"New project title [{suggested_title or 'Untitled Story'}]: ").strip() or (suggested_title or "Untitled Story"))
    project_id = _slugify_project_id(title)
    ok = pm.create_project(project_id, title=title)
    if not ok:
        project_id = _slugify_project_id(project_id + "_" + datetime.now().strftime("%H%M%S"))
        pm.create_project(project_id, title=title)

    pm.set_active_project(project_id)
    project_root = pm.get_project_path(project_id)
    if project_root:
        seed_copy = _import_storyseed_into_project(seed_path, project_root)
        console.print(f"Imported seed -> {seed_copy}")
    return project_id

def setup_logging():
    """Configures a beautiful, readable log output using Rich."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True, console=console)]
    )
    # Silence noisy third-party libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("aiohttp").setLevel(logging.WARNING)
    logging.getLogger("chromadb").setLevel(logging.WARNING)

def check_environment():
    """Pre-flight checks to ensure the system is ready to launch."""
    load_dotenv()
    
    # 1. Check API Key
    if not (os.getenv("LLM_API_KEY") or os.getenv("REQUESTY_API_KEY")):
        console.print("[bold yellow]No API key configured.[/bold yellow]")
        if sys.stdin.isatty():
            from setup_wizard import run_setup_wizard

            env_path = Path(__file__).resolve().parent / ".env"
            if run_setup_wizard(env_path):
                load_dotenv(override=True)
        
    if not (os.getenv("LLM_API_KEY") or os.getenv("REQUESTY_API_KEY")):
        console.print("[bold red]CRITICAL ERROR:[/bold red] No API key found in .env file.")
        console.print("Set LLM_API_KEY (standard) or REQUESTY_API_KEY (Requesty Router).")
        sys.exit(1)

    # 2. Check Dependencies (Optional validation)
    # We no longer check for 'data/' because ProjectManager creates 'projects/' dynamically.

async def _director_console(project_root: Path, console: Console) -> None:
    control_path = project_root / "data" / "control.json"
    console.print("\n[bold cyan]Director Console[/bold cyan] (type 'help' for commands)")
    console.print("[dim]Tip: Type any instruction and press Enter to queue it (e.g. 'continue the story into chapter 2').[/dim]")
    console.print("[dim]If the engine is paused, use 'resume' (or 'start').[/dim]")

    while True:
        try:
            raw = await asyncio.to_thread(input, "director> ")
        except (EOFError, KeyboardInterrupt):
            return

        cmd = (raw or "").strip()
        if not cmd:
            continue

        cmd = " ".join(cmd.split())
        lc = cmd.lower()
        lc_compact = lc.replace(" ", "")

        # Normalize common short aliases to avoid accidental override queuing.
        if lc in {"p", "pa"}:
            lc = "pause"
        elif lc in {"r", "re"}:
            lc = "resume"
        elif lc == "ru":
            lc = "run"
        elif lc in {"s", "st"}:
            lc = "stop"
        elif lc == "q":
            lc = "quit"

        if len(lc) <= 2 and lc not in {"h", "?"}:
            if lc not in {"pause", "resume", "run", "stop"}:
                console.print("Unrecognized short command. Type 'help' for commands or use 'override <instruction>'.")
                continue

        if lc in {"help", "h", "?"}:
            console.print("\nCommands:")
            console.print("- override <instruction>   (sets architect_override active)")
            console.print("- target <file>            (e.g. target ch03_Midpoint.md)")
            console.print("- pause | resume | start | stop")
            console.print("- status")
            console.print("- quit")
            console.print("\nExamples:")
            console.print("- override improve chapter 1 with more environmental stakes")
            console.print("- target ch02_RisingAction.md")
            console.print("- override draft the next scene and keep continuity")
            continue

        if lc in {"quit", "exit"}:
            return

        data = _read_json(control_path, default={})
        if not isinstance(data, dict):
            data = {}
        data.setdefault("system_status", "RUNNING")
        data.setdefault("architect_override", {"active": False, "instruction": None, "force_target": None})
        data.setdefault("runtime_settings", {"global_temperature": 0.7, "model_override": None})

        if lc == "status":
            console.print(json.dumps(data, indent=2))
            continue

        if lc == "pause":
            data["system_status"] = "PAUSED"
            _write_json(control_path, data)
            console.print("Paused.")
            continue

        if lc in {"resume", "run", "start"} or lc_compact in {"resume", "run", "start"}:
            data["system_status"] = "RUNNING"
            _write_json(control_path, data)
            console.print("Resumed.")
            continue

        if lc == "stop":
            data["system_status"] = "STOP"
            _write_json(control_path, data)
            console.print("Stop signaled.")
            continue

        if lc.startswith("target "):
            target = cmd[len("target "):].strip()
            if target.startswith("manuscripts/"):
                target = target[len("manuscripts/"):]
            if target.startswith("data/manuscripts/"):
                target = target[len("data/manuscripts/"):]
            data["architect_override"]["force_target"] = target
            _write_json(control_path, data)
            console.print(f"Target set: {target}")
            continue

        if lc.startswith("override "):
            instruction = cmd[len("override "):].strip()
            if not instruction:
                continue
            data["architect_override"] = {
                "active": True,
                "instruction": instruction,
                "force_target": data.get("architect_override", {}).get("force_target"),
            }
            data["system_status"] = "RUNNING"
            _write_json(control_path, data)
            console.print("Override queued.")
            continue

        # Convenience: treat any other input as an override.
        data["architect_override"] = {
            "active": True,
            "instruction": cmd,
            "force_target": data.get("architect_override", {}).get("force_target"),
        }
        data["system_status"] = "RUNNING"
        _write_json(control_path, data)
        console.print("Override queued.")

async def _inject_interview_data(json_path: Path, project_root: Path) -> dict:
    """Inject interview JSON directly into a project's story bible."""
    from ai_services.interviewer import _deep_merge, _write_json, _load_json
    
    seed = _read_json(json_path, default=None)
    if not isinstance(seed, dict):
        return {"status": "error", "message": f"Invalid JSON file: {json_path}"}
    
    bible_dir = project_root / "data" / "story_bible"
    bible_dir.mkdir(parents=True, exist_ok=True)
    
    # Load existing files
    project_conf_path = bible_dir / "project_conf.json"
    story_brief_path = bible_dir / "story_brief.json"
    characters_path = bible_dir / "characters.json"
    locations_path = bible_dir / "locations.json"
    timeline_path = bible_dir / "timeline.json"
    
    existing_project_conf = _read_json(project_conf_path, default={})
    existing_story_brief = _read_json(story_brief_path, default={})
    existing_characters = _read_json(characters_path, default={})
    existing_locations = _read_json(locations_path, default={})
    existing_timeline = _read_json(timeline_path, default={"events": []})
    
    # Merge data
    project_conf_patch = seed.get("project_conf_patch") or {}
    story_brief_patch = seed.get("story_brief") or {}
    characters_patch = seed.get("characters") or {}
    locations_patch = seed.get("locations") or {}
    timeline_patch = seed.get("timeline") or {}
    
    merged_project_conf = _deep_merge(existing_project_conf, project_conf_patch)
    merged_story_brief = _deep_merge(existing_story_brief, story_brief_patch)
    merged_characters = _deep_merge(existing_characters, characters_patch)
    merged_locations = _deep_merge(existing_locations, locations_patch)
    
    # Handle timeline events
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
    
    # Write files
    _write_json(project_conf_path, merged_project_conf)
    _write_json(story_brief_path, merged_story_brief)
    _write_json(characters_path, merged_characters)
    _write_json(locations_path, merged_locations)
    _write_json(timeline_path, merged_timeline)
    
    # Save the injected data as a storyseed snapshot
    seed_dir = project_root / "data" / "storyseed"
    seed_name = f"injected_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    storyseed_path = seed_dir / seed_name
    _write_json(storyseed_path, seed)
    
    return {
        "status": "success",
        "written": {
            "project_conf": str(project_conf_path),
            "story_brief": str(story_brief_path),
            "characters": str(characters_path),
            "locations": str(locations_path),
            "timeline": str(timeline_path),
            "storyseed": str(storyseed_path),
        },
        "director_override": seed.get("director_override"),
        "open_questions": seed.get("open_questions") or [],
    }

async def main():
    """The Main Application Loop."""
    parser = argparse.ArgumentParser(add_help=True)
    parser.add_argument("--setup", action="store_true", help="Run the interactive setup wizard and exit")
    parser.add_argument("--interview", action="store_true", help="Run the interactive story interview and exit. Requires an interactive terminal (TTY).")
    parser.add_argument("--interview-chapter", default=None, metavar="CHAPTER", help="Interview about a specific chapter (e.g. 'ch02' or '2') to iterate on it")
    parser.add_argument("--interview-model", default=None, help="Model to use for interview/extraction (defaults to DEFAULT_MODEL/.env)")
    parser.add_argument("--interview-temperature", type=float, default=0.5, help="Interview creativity (0.0-1.0)")
    parser.add_argument("--interview-turns", type=int, default=12, help="Max number of interview questions")
    parser.add_argument("--inject-interview", default=None, metavar="JSON_PATH", help="Inject interview JSON directly into a project (skips Q&A, goes straight to merge)")
    parser.add_argument("--project", default=None, help="Project ID under ./projects to interview into (defaults to last active)")
    parser.add_argument("--no-project-prompt", action="store_true", help="Skip interactive project/seed chooser when starting the engine")
    parser.add_argument("--no-director-console", action="store_true", help="Disable the interactive Director Console in engine mode")
    args, _ = parser.parse_known_args()

    setup_logging()

    if args.setup:
        load_dotenv()
        from setup_wizard import run_setup_wizard

        env_path = Path(__file__).resolve().parent / ".env"
        ok = run_setup_wizard(env_path)
        raise SystemExit(0 if ok else 1)

    check_environment()

    # Handle --inject-interview
    if args.inject_interview:
        from core.project_manager import ProjectManager
        
        json_path = Path(args.inject_interview)
        if not json_path.exists():
            console.print(f"[bold red]ERROR:[/bold red] File not found: {json_path}")
            raise SystemExit(1)
        
        pm = ProjectManager()
        project_id = args.project or pm.get_last_active_project()
        if not project_id:
            project_id = "default_project"
        
        project_root = pm.get_project_path(project_id)
        if not project_root:
            pm.create_project(project_id, title=project_id)
            pm.set_active_project(project_id)
            project_root = pm.get_project_path(project_id)
        
        if not project_root:
            console.print(f"[bold red]CRITICAL ERROR:[/bold red] Could not resolve project path for '{project_id}'.")
            raise SystemExit(1)
        
        pm.set_active_project(project_id)
        
        result = await _inject_interview_data(json_path, project_root)
        
        if result.get("status") != "success":
            console.print(f"[bold red]Injection failed:[/bold red] {result.get('message')}")
            raise SystemExit(1)
        
        written = result.get("written", {})
        console.print(f"[bold green]Interview data injected into project '{project_id}'.[/bold green]")
        if written:
            console.print("\nFiles updated:")
            for k, v in written.items():
                console.print(f"- {k}: {v}")
        
        director_override = result.get("director_override")
        if director_override:
            console.print("\nDirector Override suggestion:")
            console.print(director_override)
        
        raise SystemExit(0)

    if args.interview:
        if not sys.stdin.isatty():
            console.print("[bold red]CRITICAL ERROR:[/bold red] --interview requires an interactive terminal (TTY).")
            raise SystemExit(1)

        from core.project_manager import ProjectManager
        from ai_services.interviewer import run_interview

        pm = ProjectManager()
        project_id = args.project or pm.get_last_active_project()
        if not project_id:
            project_id = "default_project"

        project_root = pm.get_project_path(project_id)
        if not project_root:
            pm.create_project(project_id, title=project_id)
            pm.set_active_project(project_id)
            project_root = pm.get_project_path(project_id)

        if not project_root:
            console.print(f"[bold red]CRITICAL ERROR:[/bold red] Could not resolve project path for '{project_id}'.")
            raise SystemExit(1)

        pm.set_active_project(project_id)

        interview_model = args.interview_model or os.getenv("INTERVIEW_MODEL") or os.getenv("DEFAULT_MODEL") or "gpt-4-turbo"
        
        # Normalize chapter argument (e.g., "2" -> "ch02", "ch02" -> "ch02")
        focus_chapter = None
        if args.interview_chapter:
            ch = args.interview_chapter.strip().lower()
            if ch.startswith("ch"):
                focus_chapter = ch
            else:
                try:
                    focus_chapter = f"ch{int(ch):02d}"
                except ValueError:
                    focus_chapter = ch
        
        result = await run_interview(
            project_root=project_root,
            model=interview_model,
            temperature=args.interview_temperature,
            max_turns=args.interview_turns,
            focus_chapter=focus_chapter,
        )

        if result.get("status") != "success":
            console.print(f"[bold red]Interview failed:[/bold red] {result.get('message', result.get('status'))}")
            raise SystemExit(1)

        written = result.get("written", {})
        console.print("[bold green]Interview complete.[/bold green]")
        if written:
            console.print("\nFiles updated:")
            for k, v in written.items():
                console.print(f"- {k}: {v}")

        director_override = result.get("director_override")
        if director_override:
            console.print("\nDirector Override suggestion:")
            console.print(director_override)

        open_q = result.get("open_questions") or []
        if open_q:
            console.print("\nOpen questions:")
            for q in open_q:
                console.print(f"- {q}")

        raise SystemExit(0)

    # Engine mode: optionally prompt for which project to run.
    from core.project_manager import ProjectManager
    pm = ProjectManager()
    if args.project:
        # Reuse --project in engine mode as an explicit selection.
        if not pm.get_project_path(args.project):
            pm.create_project(args.project, title=args.project)
        pm.set_active_project(args.project)
    elif sys.stdin.isatty() and not args.no_project_prompt:
        chosen = _prompt_project_choice(pm, console=console, allow_seed=True)
        if chosen:
            pm.set_active_project(chosen)

    from core.orchestrator import Orchestrator

    # Print Welcome Banner
    console.print(Panel(Text(BANNER, justify="center", style="bold cyan"), border_style="cyan"))

    try:
        # Step 1: Initialize the Librarian (Project Manager)
        console.print("[bold green]System:[/bold green] Initializing Project Manager...")
        # pm is already initialized above in engine mode
        
        # Step 2: Initialize the Nervous System (Orchestrator)
        # The Orchestrator will automatically load the last active project
        # and initialize the Scanner and MemoryStore for that specific context.
        console.print("[bold green]System:[/bold green] Awakening The Orchestrator...")
        orchestrator = Orchestrator(pm)

        director_task = None
        if sys.stdin.isatty() and not args.no_director_console:
            director_task = asyncio.create_task(_director_console(orchestrator.project_root, console))

        # Display Loaded Context
        active_project = orchestrator.project_root.name
        console.print(f"[green]✔[/green] Active Universe: [bold cyan]{active_project}[/]")

        # Step 3: Ignite the Loop
        console.print("[bold yellow]>>> ENGINE START <<<[/bold yellow]")
        console.print("Press [bold red]Ctrl+C[/bold red] to stop the engine gracefully.\n")
        
        await orchestrator.start()

        if director_task:
            director_task.cancel()

    except KeyboardInterrupt:
        console.print("\n[bold red]Shutdown Signal Received.[/bold red]")
        console.print("Saving state and terminating processes...")
    except Exception as e:
        console.print_exception()
        sys.exit(1)
    finally:
        console.print("[dim]TextCraft Session Ended.[/dim]")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
