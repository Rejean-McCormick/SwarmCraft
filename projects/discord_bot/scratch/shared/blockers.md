# Blockers and Ownership

Status: Open

Blocker 1: Standup scheduling alignment and owner assignment
- Description: Establish a regular standup cadence and participant list to accelerate blocker resolution.
- Owner: Checky McManager
- Proposed schedule: Daily at 09:00 UTC, 15 minutes
- Rationale: Synchronize across Auth, Wallet, Shop, Games, and Infra
- Resolution criteria: Cadence confirmed, attendees defined, daily updates captured in status_report

Blocker 2: API contracts alignment across per-service modules (auth, wallet, shop, games)
- Description: Ensure contracts are consistent across services to avoid integration drift.
- Owners: Auth Lead, Wallet Lead, Shop Lead, Games Lead
- Rationale: Prevent mid-sprint contract churn that breaks QA harness
- Resolution criteria: Finalized contract matrix published under scratch/shared/docs/api_contracts/

Blocker 3: CI/CD gating and live Dev Plan integration
- Description: Gate readiness of dashboards and artifact integration in CI/CD pipelines.
- Owner: Deployo McOps
- Rationale: Ensure end-to-end automation before Go
- Resolution criteria: CI gates exist, basic pipelines wired, dashboards update health checks

Blocker 4: Inter-service authentication wiring
- Description: Ensure JWT generation, validation, and propagation across services.
- Owner: Bossy McArchitect
- Rationale: Security and access control across modules
- Resolution criteria: Token lifecycle defined, middleware implemented consistently, test coverage in QA harness

Next steps
- Confirm standup cadence and owner assignments in this doc
- Publish final API contract alignment plan and matrix
- Prepare CI/CD scaffolding to align with Dev Plan readiness

Notes
- Update blockers.md as blockers are resolved and new blockers arise.