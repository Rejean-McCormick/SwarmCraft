Delta Alignment Report
======================
Purpose: Surface deltas between API implementation, security tests, docs, and CI/CD to align in the next 15-minute delta session.

1) Delta Summary
- API (Codey McBackend): Switching from in-memory SQLite to on-disk scratch/shared/data/users.db. Add SCRATCH_DB_PATH env var support and initialize DB file if missing.
- Tests (Bugsy McTester): Added scratch/shared/tests/users.test.js for CRUD endpoints (GET /users, POST /users, GET /users/:id) and basic validations; need edge-case coverage and security tests expanded.
- Docs (Docy McWriter): Update API_README.md with final User API contract; align OpenAPI skeleton and payload examples.
- CI/CD (Deployo McOps): Update pipelines to use on-disk DB when SCRATCH_DB_PATH is set; ensure npm test runs against Jest-base and points to proper test setup.

2) Affected Components
- Code: API routes and DB access initialization
- Tests: user API tests and security tests
- Docs: API_README.md and OpenAPI references
- CI/CD: Pipeline scripts and environment wiring for on-disk DB

3) Root Causes
- In-memory DB used; missing on-disk DB initialization
- Tests file for User API initially missing; added later
- Docs contract drift with actual implementation

4) Proposed Actions (Owners, Steps, ETA)
- Codey McBackend
  - Action: Wire SCRATCH_DB_PATH, ensure scratch/shared/data directory exists, initialize users.db if missing, switch endpoints to read/write via on-disk DB using prepared statements.
  - ETA: 15–20 minutes
- Bugsy McTester
  - Action: Expand tests for edge cases (duplicate emails, invalid IDs, empty payloads), include SQL injection tests against GET/POST endpoints, ensure test isolation per run.
  - ETA: 15–25 minutes
- Docy McWriter
  - Action: Fill API_README.md with endpoints, schemas, examples, and link to code references; ensure OpenAPI notes reflect on-disk DB path behavior.
  - ETA: 15–20 minutes
- Deployo McOps
  - Action: Update CI to bootstrap on-disk DB path; ensure npm install, lint, and tests run; provide script to initialize DB in CI if needed.
  - ETA: 15–20 minutes

5) Environment Variables and Secrets
- SCRATCH_DB_PATH: Path to on-disk SQLite DB. Default scratch/shared/data/users.db
- Other env vars: NODE_ENV

6) Quick Start for Delta Alignment (proposed window)
- Time: 15-minute delta alignment window starting now; proceed if ok, otherwise propose alternate slot.

7) Risks
- CI stability if on-disk DB not initialized in CI runners
- Tests expecting in-memory DB may fail; ensure test doubles or actual on-disk DB path are configured.
