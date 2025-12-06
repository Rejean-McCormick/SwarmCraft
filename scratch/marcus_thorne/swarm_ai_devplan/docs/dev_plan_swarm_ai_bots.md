# Dev Plan: Swarm of AI Bots Orchestration

Goal
- Design and implement a scalable framework where multiple AI bots (agents) collaborate to complete complex tasks. Bots communicate through a central orchestrator, enabling planning, execution, evaluation, and governance with observable auditing.

Scope (MVP)
- Orchestrator service coordinating tasks among three bot roles:
  - PlannerBot: decomposes tasks into sub-tasks and assigns to Executors
  - ExecutorBot: performs actions/sub-tasks and returns results
  - EvaluatorBot: reviews outputs for quality, safety, and adherence to rules
- In-memory task store for MVP with a simple HTTP API for task submission and status checks.
- Bot SDK and sample bot to demonstrate registration, task polling, result reporting, and redaction/audit hooks.
- A lightweight harness to simulate bot interactions in-process.
- CI with PyTest tests for models, API endpoints, and end-to-end flow.

Architecture Overview
- Orchestrator Service (Python FastAPI):
  - REST API endpoints for task submission, status, and events
  - In-memory task registry with task state machine
  - Bot registry for Planner/Executor/Evaluator types
  - Message broker abstraction (in-process pub/sub) for task progress and events
  - Audit/logging hooks to redact sensitive fields
- Bot SDK (Python):
  - BaseBot: defines interface for registration, poll for tasks, submit results
  - SampleBot(s): implement a minimal planner/executor/evaluator
- Harness (Python):
  - Simulator that spins up in-process bot instances and drives a sample task flow
- Data Model (Pydantic):
  - TaskDefinition, SubTask, BotInfo, TaskStatus, BotMessage, AuditLog
- Security & Compliance:
  - API key guarded endpoints for MVP; plan to add JWT in later phases
- Observability:
  - Simple in-memory metrics and structured logs; optional integration with OpenTelemetry later

Key Data Models
- TaskDefinition: id, title, description, created_at, priority, subtasks (optional)
- SubTask: id, parent_task_id, description, required_skills, status
- BotInfo: id, type (Planner/Executor/Evaluator), version, endpoint
- TaskStatus: CREATED, PLANNED, IN_PROGRESS, COMPLETED, FAILED, ARCHIVED
- BotMessage: from_bot, to_bot, task_id, payload, timestamp
- AuditLog: id, task_id, event, payload, redacted_fields, timestamp

Communication Protocol (MVP)
- Client submits TaskDefinition via POST /tasks
- Orchestrator creates SubTasks and assigns to Planner/Executor bots
- Bots poll or subscribe for tasks, perform work, post results via POST /tasks/{task_id}/results
- EvaluatorBot reviews results and posts a final verdict
- Audit logs capture each step with redacted fields (configurable via redaction rules)

API Endpoints (MVP)
- POST /tasks: submit a new task definition
- GET /tasks/{task_id}: fetch task status and summary
- POST /tasks/{task_id}/results: submit results from a bot
- POST /bots/register: register a bot
- GET /health: basic health

Task Lifecycle
- CREATED -> PLANNED: Planner Bot decomposes into subtasks
- PLANNED -> IN_PROGRESS: Subtasks are assigned to Executors
- IN_PROGRESS -> COMPLETED/FAILED: Executors report status
- COMPLETED -> ARCHIVED: Evaluator Bot reviews and archives

Security & Compliance
- MVP: API key per client; header X-API-KEY
- Avoid leaking secrets via redaction hooks; track redacted_fields in audits
- Plan to integrate with Vault-like redaction module later

Observability & Testing
- Unit tests for data models (pydantic)
- API tests for endpoints using a test client
- End-to-end simulation tests with the Harness
- CI to run pytest on push/PR

Milestones & Timeline
- M1: Scaffolding (1 week)
- M2: MVP Orchestrator + Bot SDK + Sample Bots (2 weeks)
- M3: Harness + Basic End-to-End Flow (1 week)
- M4: Audit/Redaction & Security (1 week)
- M5: CI, Docs, and Handoff to Frontend/CLI (1 week)

Risks & Mitigations
- Complexity of bot coordination: start with in-process simulator
- Security exposure: implement API keys and restrict sensitive data via redaction
- Observability gaps: add structured logging and metrics early

Deployment & Operations
- Containerize orchestrator and bots for later K8s deployment
- Use a simple SQLite/in-memory store for MVP; plan for PostgresRedis later
- Emit audit logs and metrics to a central sink for analytics

How to Onboard Developers
- Repo layout, coding standards, and bot SDK API doc
- Quickstart guide to boot the simulator and run an example task flow

Next Steps
- Create repo scaffolding and MVP endpoints
- Implement BaseBot, SampleBots, and Harness
- Add tests and CI workflow
