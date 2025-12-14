from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, Optional

from rich.console import Console
from rich.prompt import Confirm, IntPrompt, Prompt


console = Console()


def _format_env_value(value: Optional[str]) -> str:
    if value is None:
        value = ""
    if "\n" in value or "\r" in value:
        raise ValueError("Environment values must be single-line")
    if value == "":
        return ""

    if any(ch in value for ch in [" ", "\t", "#", "\"", "'"]):
        escaped = value.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'

    return value


def _update_env_file(env_path: Path, updates: Dict[str, str]) -> None:
    existing_text = ""
    if env_path.exists():
        existing_text = env_path.read_text(encoding="utf-8")

    lines = existing_text.splitlines(keepends=True) if existing_text else []

    formatted_updates = {k: _format_env_value(v) for k, v in updates.items()}

    applied = set()
    key_re = re.compile(r"^(\s*)([A-Za-z_][A-Za-z0-9_]*)\s*=.*$")

    new_lines = []
    for line in lines:
        m = key_re.match(line)
        if not m:
            new_lines.append(line)
            continue

        prefix_ws, key = m.group(1), m.group(2)
        if key in formatted_updates:
            new_lines.append(f"{prefix_ws}{key}={formatted_updates[key]}\n")
            applied.add(key)
        else:
            new_lines.append(line)

    if new_lines and not new_lines[-1].endswith("\n"):
        new_lines[-1] = new_lines[-1] + "\n"

    for key, value in formatted_updates.items():
        if key in applied:
            continue
        if new_lines and not new_lines[-1].endswith("\n"):
            new_lines[-1] = new_lines[-1] + "\n"
        new_lines.append(f"{key}={value}\n")

    env_path.write_text("".join(new_lines), encoding="utf-8")


def run_setup_wizard(env_path: Path) -> bool:
    console.print("\n[bold cyan]SwarmCraft Setup Wizard[/bold cyan]")
    console.print("Pick an API provider, then set your API key + default model.\n")

    console.print("[bold]Providers[/bold]")
    console.print("  1) Requesty Router (OpenAI-compatible)")
    console.print("  2) OpenAI")
    console.print("  3) OpenRouter")
    console.print("  4) Custom OpenAI-compatible")

    choice = IntPrompt.ask("Select provider", choices=["1", "2", "3", "4"], default="1")

    updates: Dict[str, str] = {}

    if choice == 1:
        key = Prompt.ask("Enter Requesty API Key", password=True)
        base_url = Prompt.ask("Requesty Base URL", default="https://router.requesty.ai/v1")
        default_provider = Prompt.ask("Default provider prefix for router models", default="openai")
        model = Prompt.ask("Default model (provider/model)", default=f"{default_provider}/gpt-4o")
        if "/" not in model:
            model = f"{default_provider}/{model}"

        updates["REQUESTY_API_KEY"] = key
        updates["REQUESTY_BASE_URL"] = base_url
        updates["DEFAULT_MODEL"] = model
        updates["ROUTER_DEFAULT_PROVIDER"] = default_provider

        if Confirm.ask("Apply this model globally (override personas.json models)?", default=True):
            updates["MODEL_OVERRIDE"] = model

        if Confirm.ask("Set optional Requesty headers (recommended for analytics)?", default=False):
            http_referer = Prompt.ask("REQUESTY_HTTP_REFERER (your site URL)", default="")
            x_title = Prompt.ask("REQUESTY_X_TITLE (your app name)", default="SwarmCraft")
            updates["REQUESTY_HTTP_REFERER"] = http_referer
            updates["REQUESTY_X_TITLE"] = x_title

        if Confirm.ask("Clear LLM_API_KEY/LLM_API_BASE_URL to avoid precedence over Requesty?", default=True):
            updates["LLM_API_KEY"] = ""
            updates["LLM_API_BASE_URL"] = ""

    elif choice == 2:
        key = Prompt.ask("Enter OpenAI API Key", password=True)
        base_url = Prompt.ask("OpenAI Base URL", default="https://api.openai.com/v1")
        model = Prompt.ask("Default model", default="gpt-4o")

        updates["LLM_API_KEY"] = key
        updates["LLM_API_BASE_URL"] = base_url
        updates["DEFAULT_MODEL"] = model

        if Confirm.ask("Apply this model globally (override personas.json models)?", default=False):
            updates["MODEL_OVERRIDE"] = model

        if Confirm.ask("Clear REQUESTY_API_KEY/REQUESTY_BASE_URL?", default=False):
            updates["REQUESTY_API_KEY"] = ""
            updates["REQUESTY_BASE_URL"] = ""

    elif choice == 3:
        key = Prompt.ask("Enter OpenRouter API Key", password=True)
        base_url = Prompt.ask("OpenRouter Base URL", default="https://openrouter.ai/api/v1")
        default_provider = Prompt.ask("Default provider prefix for router models", default="openai")
        model = Prompt.ask("Default model (provider/model)", default=f"{default_provider}/gpt-4o")
        if "/" not in model:
            model = f"{default_provider}/{model}"

        updates["LLM_API_KEY"] = key
        updates["LLM_API_BASE_URL"] = base_url
        updates["DEFAULT_MODEL"] = model

        updates["ROUTER_DEFAULT_PROVIDER"] = default_provider

        if Confirm.ask("Apply this model globally (override personas.json models)?", default=True):
            updates["MODEL_OVERRIDE"] = model

        if Confirm.ask("Clear REQUESTY_API_KEY/REQUESTY_BASE_URL?", default=False):
            updates["REQUESTY_API_KEY"] = ""
            updates["REQUESTY_BASE_URL"] = ""

    else:
        key = Prompt.ask("Enter API Key", password=True)
        base_url = Prompt.ask("Base URL prefix (e.g., https://host/v1)")
        model = Prompt.ask("Default model")

        updates["LLM_API_KEY"] = key
        updates["LLM_API_BASE_URL"] = base_url
        updates["DEFAULT_MODEL"] = model

        if Confirm.ask("Clear REQUESTY_API_KEY/REQUESTY_BASE_URL?", default=False):
            updates["REQUESTY_API_KEY"] = ""
            updates["REQUESTY_BASE_URL"] = ""

    if not Confirm.ask(f"Write settings to {env_path.name}?", default=True):
        console.print("[yellow]Setup canceled (nothing written).[/yellow]")
        return False

    _update_env_file(env_path, updates)
    console.print(f"[green]Saved configuration to {env_path}[/green]")
    console.print("Restart SwarmCraft for changes to take effect.\n")
    return True
