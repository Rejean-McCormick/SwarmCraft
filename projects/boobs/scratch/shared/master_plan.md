Phase 1 Production Readiness Plan: DB-backed storage with SQLite for BobGen

Goal
- Harden BobGen status path with a SQLite-backed persistence layer, seed 100k records, robust endpoints, migrations, test coverage, and developer/docs alignment.

Scope and Roles (max 4 workers)
- backend_dev (Codey McBackend): implement SQLite data model, repositories, endpoints, migrations, seed logic.
- qa_engineer (Bugsy McTester): define test matrix and implement/verify tests for DB-backed endpoints and health checks; load/scalability checks.
- devops (Deployo McOps): adjust CI/CD and docker-compose/setup to initialize SQLite DB, run migrations, seed data, and health checks; ensure production-like environment.
- tech_writer (Docy McWriter): update BobGen docs to include DB-backed storage, migrations, seeding, and operation notes.

What will be created or modified
- Backend and data layer
  - scratch/shared/src/db/status_repository.js
  - scratch/shared/src/models/status_model.js (data model shape)
  - scratch/shared/src/server.js or scratch/shared/src/app.js (Express app wiring) with routes
  - scratch/shared/src/routes/status_routes.js (GET /bobgen/status, GET /bobgen/status/:id, GET /health)
  - scratch/shared/migrations/001_create_status_table.sql (SQL migrations for SQLite)
  - scratch/shared/db_seed/seed_100k.js (seed script to insert 100,000 records)
  - scratch/shared/config/db_config.js (DB connection helper)
  - scratch/shared/tests/ (basic integration tests will be authored by QA in their scope)
- Documentation
  - scratch/shared/docs/bobgen_db_overview.md (DB-backed storage overview)
  - scratch/shared/docs/bobgen_runbook.md (operational runbook for DB-backed status service)
- CI/CD and Deployment
  - scratch/shared/docker-compose.yml (service updated to include SQLite persistence; migration/seed steps)
  - scratch/shared/.github/workflows/ (ci workflow references; ensure migrations and seed run during startup in test env)

Migration and Seeding strategy
- Migration: 001_create_status_table.sql to create the status table with fields: id, uptime, version, latency, error_rate, last_run, blocks, runbook_link, dashboard_link, created_at, updated_at
- Seeding: seed_100k.js creates 100,000 rows efficiently (batched inserts) and logs progress; startup code will run seed if table empty or admin seed endpoint can trigger on demand

Data access patterns
- GET /bobgen/status
  - Supports pagination via query params ?limit and ?offset; returns list of status rows with selected fields and links
- GET /bobgen/status/:id
  - Returns single status record or 404 if not found
- GET /health
  - Lightweight health indicator; ensures DB health and app uptime

Operational considerations
- Seed time estimates and CPU/memory budget; option to seed on startup in a background job if table empty
- Observability: basic metrics endpoints for latency and request counts
- Security: validation on inputs and safe defaults for queries

Timeline and success criteria
- Milestone 1: DB integration and migrations implemented
- Milestone 2: Seeded 100k records and verified endpoint behavior
- Milestone 3: Tests defined by QA and run in CI; docs updated
- Acceptance: Endpoints respond within acceptable latency; 100k records exist; no critical errors in CI

Notes
- We will proceed with a SQLite-based persistence approach as requested. All files to be created or updated under scratch/shared/ as described. The plan is iterative and can be refined by the team during execution.
