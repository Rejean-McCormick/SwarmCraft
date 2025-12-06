# Swarm Knowledge Contracts

This document defines structured payloads and contracts used by all bots in the swarm. The goal is to enforce strict schemas, traceability, and secure handling of secrets.

## Core Payloads
- Trace: trace_id (string), span_id (string), timestamp (ISO8601)
- Message envelope: payload_type (string), payload_version (string), trace (Trace), payload (object)

## Task Payload
- payload_type: "task"
- payload_version: "v1"
- task_id: string
- objective: string
- acceptance_criteria: string[]
- constraints: string[]
- deadline: ISO8601 string (optional)
- metadata: object (optional)
- secrets_handling: boolean (default true)

## Milestone Payload
- payload_type: "milestone"
- milestone_id: string
- task_id: string
- description: string
- due_date: ISO8601 string (optional)
- status: ["planned", "in_progress", "completed", "blocked"]
- assigned_to: string (bot id)

## Artifact Payload
- payload_type: "artifact"
- artifact_id: string
- task_id: string
- artifact_type: string (e.g., "log", "report", "model")
- location: string (path or URL)
- metadata: object
- created_at: ISO8601 string

## Audit Payload
- payload_type: "audit"
- audit_id: string
- artifact_id: string
- findings: array of { category: string, description: string, severity: ["info","low","medium","high","critical"], remediation: string }
- timestamp: ISO8601 string
- redacted: boolean

## Command Payload
- payload_type: "command"
- command_id: string
- action: string
- parameters: object
- source_bot: string
- trace_id: string
- timestamp: ISO8601 string

## Security & Redaction Rules
- Any field marked as sensitive should be redacted in outputs unless explicitly allowed.
- All logs and artifacts must be stored with access controls and encryption at rest.

## Versioning & Compatibility
- Contracts are versioned via payload_version fields.
- Backwards compatibility should be preserved for minor versions where feasible.

## Example Payload (JSON)
{
  "payload_type": "task",
  "payload_version": "v1",
  "task_id": "TASK-0001",
  "objective": "Orchestrate MVP of bot swarm",
  "acceptance_criteria": ["planner creates plan","executors run tasks","auditor verifies outputs"],
  "constraints": ["idempotent", "traceable"],
  "deadline": "2025-12-31T23:59:59Z",
  "metadata": {"priority": "high"},
  "secrets_handling": true
}
