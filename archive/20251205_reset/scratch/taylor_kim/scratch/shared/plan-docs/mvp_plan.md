# MVP Plan & Four-Epic Plan-Doc Mapping

Purpose
- Align MVP scaffolding, per-epic statuses, and the data path for reliable, observable MVP delivery.

Ladder (0–7) – gating and handoff states
- 0: not started
- 1: in progress
- 2: payload staged / dry-run
- 3: data checks in progress / validation in progress
- 4: ready for QA / validation kickoff
- 5: QA / validation complete (approved for next stage)
- 6: docs ready
- 7: ready for deploy / verification

Notes
- We extend the ladder to include 6 and 7 as final readiness gates; 5 remains QA/validation. A separate complete/deployed flag is discouraged to avoid drift.
- The four numbers correspond to four epics/tasks, tracked as per-epic statuses on a lightweight board or doc.

Four Epics / Per-Epic Status Board (template)
- Epic-1
  - Owner:
  - Current Status: (0-7)
  - Blockers:
  - Plan Highlights:
  - Links:
- Epic-2
  - Owner:
  - Current Status: (0-7)
  - Blockers:
  - Plan Highlights:
  - Links:
- Epic-3
  - Owner:
  - Current Status: (0-7)
  - Blockers:
  - Plan Highlights:
  - Links:
- Epic-4
  - Owner:
  - Current Status: (0-7)
  - Blockers:
  - Plan Highlights:
  - Links:

Data Path & MVP ETL Skeleton
- ETL: CSV source -> DuckDB in-memory (staging) -> Parquet (outputs) for analytics layer
- Star schema for MVP metrics (Fact: facts; Dimensions: Date, Product, Customer, Channel, etc.)
- Data quality checks: row counts, null rates, referential integrity checks
- Observability: lightweight health checks, simple dashboards via status board

Artifacts & Folder Map
- scratch/shared/mvp/etl/  (CSV -> DuckDB -> Parquet pipeline skeleton)
- scratch/shared/mvp/status.md  (per-epic status board)
- scratch/shared/mvp/plan-lite.md  (optional quick plan snapshot)
- scratch/shared/plan-docs/mvp_plan.md  (this document)

Next Actions
- Populate per-epic owners and initial statuses (2–3) per epic
- Implement ETL skeleton and basic data quality checks
- Wire in status links in the plan document and status.md
- Review and align on ticket IDs for triage
