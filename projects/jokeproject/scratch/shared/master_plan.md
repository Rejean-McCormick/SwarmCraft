# Master Plan: 100k Jokes Factory

Goal: Generate and store 100,000 jokes using a distributed swarm. The swarm will spawn multiple workers to collaboratively produce jokes in parallel, with a central store and an API to access them.

Assumptions
- Maximum active workers in this sprint: 4 (to align with orchestration rules)
- Jokes will be stored in a SQLite database for simplicity and portability. Access via a lightweight Express API.
- We will operate in batches to avoid overload and ensure quality checks.

System Architecture (high level)
- Joke Generator Engine (backend_dev)
  - Generates jokes from templates and word lists using seeds for reproducibility.
  - Exposes a batch generator to create N jokes per run.
- Joke Store (storage.js)
  - Lightweight DB layer: init schema, insert jokes, query jokes.
- API Layer (api/app.js)
  - Endpoints to trigger generation and fetch jokes:
    - POST /generate-jokes
    - GET /jokes
    - GET /jokes/:id
- QA & Validation (qa_engineer)
  - Validate data integrity, duplicates, and performance at scale.
- Deployment & Ops (devops)
  - Provide containerization, basic CI hints, and runbook.
- Documentation (tech_writer)
  - API docs, user guide, and runbook.

Files & Functions to be Created (Full, Working Implementations)
- scratch/shared/src/joke_templates.js
  - Exports TEMPLATE_SETS or similar structures for joke templates.
- scratch/shared/src/generator.js
  - function generateJoke(seed, templates) -> string
  - function generateBatch(count, seedBase, templates) -> string[]
- scratch/shared/src/storage.js
  - class JokeStore
  - async init()
  - async addJoke(text, category, seed)
  - async getJokes(offset, limit)
  - async getJoke(id)
- scratch/shared/api/app.js
  - Express app setup
  - POST /generate-jokes
  - GET /jokes
  - GET /jokes/:id
  - Basic error handling
- scratch/shared/config.js
  - TOTAL_JOKES = 100000
  - BATCH_SIZE = 2500
  - DB_PATH = 'sqlite3.db'
  - SEED_BASE_DEFAULT
- scratch/shared/docs/API_DOCS.md
  - Endpoint descriptions, request/response examples
- scratch/shared/tests/generator_smoke_test.js
  - Basic concurrency test scaffolding
- scratch/shared/runbooks/ops.md
  - How to run generation in batch, monitor progress

Data Model (SQLite)
- JOKES table:
  - id INTEGER PRIMARY KEY AUTOINCREMENT
  - text TEXT NOT NULL
  - category TEXT
  - created_at DATETIME
  - seed INTEGER
  - status TEXT (e.g., "generated", "verified")

Data Flow Outline
1) Client triggers POST /generate-jokes with { count, seed }.
2) API delegates to generator to produce a batch of jokes (split across workers if needed).
3) Generated jokes are persisted in the DB.
4) Client can page through jokes via GET /jokes.

Milestones
- Phase 1: Skeleton API + storage + templates outline.
- Phase 2: Batch generation, seeds, and dedup logic.
- Phase 3: QA, load testing, and optimization.

Risks & Mitigations
- Risk: Duplicates. Mitigation: Use unique constraint on text with optional hash.
- Risk: Generation quality. Mitigation: Run QA checks and template diversification.
- Risk: Large resource usage. Mitigation: Throttle and batch processing with progress tracking.
