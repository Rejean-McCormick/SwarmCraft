# Multi-Agent AI Swarm

A multi-agent AI development system where specialized AI agents collaborate to build software projects. Features an Architect who orchestrates a swarm of developers, testers, and other specialists.

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## Features

- **7 Specialized AI Agents** - Each with distinct roles and personalities
- **True Orchestration** - Architect delegates, workers execute (no micromanagement)
- **Role-Based Tools** - Architect gets orchestration tools, workers get coding tools
- **Rich Terminal Dashboard** - Real-time view of agents, tasks, tokens, and activity
- **Persistent Settings** - Preferences saved between sessions
- **Multi-Project Support** - Isolated workspaces for each project

## Agent Roster

| Agent | Role | Specialty |
|-------|------|-----------|
| **Bossy McArchitect** | Lead Architect | System design, task orchestration (DELEGATES, doesn't code) |
| **Codey McBackend** | Backend Dev | APIs, databases, server logic |
| **Pixel McFrontend** | Frontend Dev | UI/UX, React, web components |
| **Bugsy McTester** | QA Engineer | Testing, security, code review |
| **Deployo McOps** | DevOps | CI/CD, Docker, infrastructure |
| **Checky McManager** | Project Manager | Progress tracking, status reports |
| **Docy McWriter** | Tech Writer | Documentation, API docs, guides |

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Copy and configure environment
cp .env.example .env
# Edit .env with your REQUESTY_API_KEY

# Run the Textual TUI dashboard (recommended)
python main.py --tui

# Or run the Rich dashboard (legacy)
python main.py

# Or run the basic CLI
python main.py --cli
```

## How It Works

### Phase 1: Planning
1. Start the dashboard - only the Architect joins initially
2. Describe your project to the Architect
3. The Architect creates a master plan in `scratch/shared/master_plan.md`
4. Review and say "Go" to proceed

### Phase 2: Execution
1. Architect spawns workers (backend_dev, frontend_dev, etc.)
2. Architect assigns specific tasks to each worker
3. Workers write code to `scratch/shared/` using their tools
4. Architect monitors progress via `get_swarm_state()`

### Phase 3: Delivery
1. QA reviews and tests the code
2. Tech Writer creates documentation
3. DevOps creates deployment configs
4. All artifacts are in `scratch/shared/`

## Dashboard Commands

| Command | Description |
|---------|-------------|
| `/help` | Show all commands |
| `/settings` | Open settings screen (Ctrl+S) |
| `/agents` | Configure agents (Ctrl+A) |
| `/tasks` | View/control tasks (Ctrl+T) |
| `/stop` | Stop current task (Ctrl+X) |
| `/fix <reason>` | Stop and request a fix |
| `/spawn <role>` | Spawn a new agent |
| `/status` | Show swarm status |
| `/clear` | Clear chat history |
| `/quit` | Exit (Ctrl+Q) |

## Keyboard Shortcuts (TUI Mode)

| Shortcut | Action |
|----------|--------|
| `Ctrl+S` | Open Settings |
| `Ctrl+A` | Configure Agents |
| `Ctrl+T` | Task Control |
| `Ctrl+X` | Stop Current Task |
| `Ctrl+R` | Refresh Panels |
| `Ctrl+Q` | Quit |
| `F1` | Show Help |

## Display Modes

- **TUI Mode** (`--tui`, recommended) - Full Textual dashboard with panels, settings screens, API logging, and task control
- **Rich Mode** (default) - Rich terminal dashboard with live updates
- **CLI Mode** (`--cli`) - Basic scrolling chat interface

## TUI Dashboard Layout

The Textual TUI (`--tui`) features a 3-column layout:

**Left Column:**
- Agent cards showing status, tokens used, and recent accomplishments
- API Log panel with real-time request/response tracking (timestamps, elapsed time, token counts, input/output previews)

**Center Column:**
- Main chat log with word-wrapped messages
- Input box for commands and messages

**Right Column:**
- Token usage panel (totals and per-agent breakdown)
- Tool calls panel (real-time tool activity)
- DevPlan panel (scrollable master plan view)

## Architecture

### Tool Separation

The system uses role-based tool access to enforce proper orchestration:

**Orchestrator Tools** (Architect only):
- `spawn_worker` - Bring in team members
- `assign_task` - Delegate work to workers
- `get_swarm_state` - Check agent/task status
- `read_file`, `write_file` - For master plan only

**Worker Tools** (All other agents):
- `read_file`, `write_file`, `edit_file` - Code operations
- `list_files`, `search_code` - Navigation
- `run_command` - Safe shell commands
- `claim_file`, `release_file` - File locking

This ensures the Architect delegates work instead of doing it all.

### Conversation Flow

1. User sends message → Architect responds
2. Architect spawns workers and assigns tasks
3. Workers execute tasks (with configurable tool call depth, default 15)
4. Workers report completion
5. Architect assigns next tasks or reviews

### Tool Call Depth

Agents can chain multiple tool calls when working on complex tasks. The default limit is 50 consecutive tool calls, configurable in Settings → Advanced → Max Tool Depth. This allows agents to:
- Write multiple files in sequence
- Read, modify, and save files
- Create folder structures
- Run commands and process results

If an agent hits the limit, they'll pause and ask you to continue.

## Project Structure

```
zaiswarmchat/
├── agents/                 # AI agent implementations
│   ├── architect.py        # Orchestrator (delegates only)
│   ├── backend_dev.py      # Codey McBackend
│   ├── frontend_dev.py     # Pixel McFrontend
│   └── ...
├── core/                   # Core functionality
│   ├── chatroom.py         # Conversation orchestration
│   ├── agent_tools.py      # Tool definitions & execution
│   ├── project_manager.py  # Multi-project support
│   ├── task_manager.py     # Task tracking
│   ├── settings_manager.py # Persistent settings
│   └── token_tracker.py    # API usage tracking
├── projects/               # Project workspaces
│   └── <project_name>/
│       ├── scratch/shared/ # Agent output files
│       └── data/           # Memory & history
├── logs/                   # Session logs
├── main.py                 # CLI entry point
├── dashboard.py            # Rich terminal UI
└── requirements.txt
```

## Configuration

Settings in `data/settings.json` (also accessible via Ctrl+S in TUI):

| Setting | Default | Description |
|---------|---------|-------------|
| `auto_chat` | `true` | Auto-trigger architect on project load |
| `tools_enabled` | `true` | Enable agent tool usage |
| `default_model` | `openai/gpt-5-nano` | Default LLM model |
| `architect_model` | `openai/gpt-5-nano` | Model for Architect |
| `swarm_model` | `openai/gpt-5-nano` | Model for worker agents |
| `max_tokens` | `100000` | Max tokens per response |
| `temperature` | `0.8` | Response creativity (0-1) |
| `max_tool_depth` | `50` | Max consecutive tool calls per turn |

## Token Tracking

The dashboard shows real-time token usage:
- Prompt tokens (input)
- Completion tokens (output)
- Total tokens
- API call count

Use `/dashboard` to see a snapshot anytime.

## Logging

Logs are saved to `logs/dashboard_YYYYMMDD_HHMMSS.log` with:
- API requests/responses
- Tool calls and results
- Agent status changes
- Error details

## Requirements

- Python 3.9+
- Requesty API key (get one at https://requesty.ai)
- Rich library for terminal UI

## License

MIT License
