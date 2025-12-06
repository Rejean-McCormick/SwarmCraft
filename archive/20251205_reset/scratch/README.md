# Agent Scratch Workspace

This directory is the designated workspace for AI agents.

## How it works
- Agents can **read**, **write**, and **edit** files in this directory.
- Each agent may create its own subfolder (e.g., `scratch/HexMage/`).
- A `shared/` folder exists for collaborative work.

## Safety
- Agents are **sandboxed** to this directory. They cannot access files outside of `scratch/`.
- **File Locking**: Agents must "claim" a file before editing it to prevent collisions.

## Usage
- You can place files here for agents to analyze.
- Agents will output their code and artifacts here.
