# Dev Plan: Python AI Chatbot MVP

Goal: Build a robust, secure Python-based chatbot that chats with an AI via API, delivering a performant MVP and a clear path to production.

## 1) Purpose
- Align the team on goals, architecture, data handling, and delivery milestones.
- Establish ownership, responsibilities, and a measurable plan to iterate quickly.

## 2) Goals & Success Metrics
- Latency: target median round-trip time (RTT) <= 500 ms; 95th percentile <= 1 s.
- Reliability/Uptime: 99.5% monthly uptime.
- Cost: API calls per session under $0.05 (adjustable by plan).
- User Satisfaction: CSAT >= 4.5/5 or NPS >= 40 in early pilots.
- Security & Compliance: no leakage of PII, auditable logs, access control enforced.

## 3) Scope, MVP & Non-Goals
- MVP: core chat flow, prompt management, basic monitoring, error handling, secure data handling.
- Excluded (for now): custom model training, complex prompt tuning, multi-lingual support beyond English, on-device inference.

## 4) Architecture & Data Flow
- High-level components:
  - Frontend/UI
  - Backend API (FastAPI)
  - AI API interface (external AI provider)
  - Session store (Redis)
  - Postgres (audit/log storage)
  - Logging/Telemetry (Prometheus/Grafana, OpenTelemetry)
- Data flow (simplified):
  1. User message -> sanitize/validate -> prompt manager builds prompt.
  2. Backend calls AI API with prompt -> receives response.
  3. Backend formats response, applies policy/filters -> sends to UI.
  4. All messages stored in session store with minimal metadata (for privacy).
- Tech choices:
  - Backend: FastAPI (Python)
  - Session store: Redis
  - Persistence: Postgres for audit logs
  - AI interface: OpenAI-like API (token-based)
  - Observability: Prometheus + Grafana; structured logging

## 5) Security & Privacy
- Threat modeling and data minimization at every touchpoint.
- Access controls (RBAC); API keys stored in Secrets Manager.
- Encryption in transit (TLS) and at rest (db encryption).
- Data retention: default 30 days, configurable by policy; redact PII from logs.
- Audit logging: who, when, what was accessed; immutable logs where possible.
- Compliance checks integrated into the sprint reviews.

## 6) Data Model & Persistence
- Session: session_id, user_id, created_at, last_seen, status
- Messages: id, session_id, role (user/assistant/system), content (redacted if necessary), timestamp
- Prompts: template_id, content, version, created_at
- Audit Logs: event, payload, timestamp

## 7) Monitoring, Metrics & Retraining
- Baselines and dashboards for latency, error rate, success rate, API failure rate, and cost.
- Alerts for latency thresholds, error spikes, or API quota issues.
- Retraining/training drift triggers based on feedback loop and offline evaluation.
- Telemetry: request size, response size, token usage (for cost visibility).

## 8) Backlog, Milestones & Timeline
- MVP Milestones:
  - Week 1-2: Architecture finalization, API contracts, security controls, bootstrap backend.
  - Week 3-4: Frontend integration, basic prompt templates, session handling.
  - Week 5-6: Observability, error handling, basic CI/CD, initial user testing.
  - Week 7: Stabilize, docs, handoff, Prepare for v1.0.
- Release plan: feature flags for new AI prompts; canary deployment to early users.

## 9) Roles, Responsibilities & Ownership
- Morgan Chen (Security/Privacy Lead): architecture, data flow, threat modeling, security controls, privacy policy, audits.
- Casey Thompson (Dev Plan & Coordination): goals alignment, data/API choices, milestones, monitoring strategy, backlog grooming.
- Frontend Engineer: UI/UX implementation, accessibility, responsive design.
- Backend Engineer: API server, AI API integration, data persistence, performance tuning.
- Data Engineer / ML Liaison (as available): prompts, templates, evaluation hooks.
- QA / Testing: test strategy, automation, reliability checks.
- DevOps: deployment, CI/CD, monitoring integration.

## 10) API Contracts & Interfaces
- /chat (POST): session_id, user_message -> response
- /health, /metrics for observability
- Request/response schemas defined with JSON Schema; error codes documented
- Rate limits and retry/backoff policy documented

## 11) Security & Compliance Review Cadence
- Threat model updates at major milestones.
- Quarterly security reviews; immediate review for high-risk changes.

## 12) Testing Strategy
- Unit tests for prompt builder, formatting, and validation.
- Integration tests for AI API calls with stubs/mocks.
- End-to-end tests for the chat flow.

## 13) Deployment & CI/CD
- Git branching strategy, PR review checklist.
- CI: run unit + integration tests; linting; type checks.
- CD: canary deployment to limited user set; rollback plan.

## 14) Documentation & Handoff
- API docs, architectural diagrams, runbooks, and security controls docs.
- Quickstart guide for developers.

## 15) Initial Task Breakdown (Owner, Scope, Time)
- Task 1: Define business goals & metrics – Owner: Casey Thompson – 1-2 days
- Task 2: Architecture diagram & data flow – Owner: Morgan Chen – 3 days
- Task 3: Security/privacy controls spec – Owner: Morgan Chen – 2 days
- Task 4: Data model & persistence schema – Owner: Backend Engineer / Data Engineer – 3 days
- Task 5: AI API interface contracts & prompt templates – Owner: ML Liaison – 2 days
- Task 6: Backend prototype (FastAPI) – Owner: Backend Engineer – 7 days
- Task 7: Frontend prototype (React) – Owner: Frontend Engineer – 7 days
- Task 8: Monitoring dashboards & alerting – Owner: Casey Thompson / DevOps – 4 days
- Task 9: CI/CD & deployment plan – Owner: DevOps – 3 days
- Task 10: Testing strategy & automation – Owner: QA – 4 days
- Task 11: Security review & threat validation – Owner: Morgan Chen – ongoing
- Task 12: Documentation & handoff – Owner: All – ongoing

## 16) Meeting Cadence
- Weekly dev plan review; biweekly architecture review; ad-hoc issue triage as needed.

## 17) Assumptions & Constraints
- Access to AI API; secrets managed securely; cloud environment ready.
- Compliance and privacy controls can be implemented within sprint timelines.

> Note: This is the first draft. Morgan will circulate a first draft for review; Casey and the rest of the team should provide input and own the specific tasks as we align on the plan.