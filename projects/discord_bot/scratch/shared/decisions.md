# Decisions / Tech Log

- Decision: Plan to modularize services with per-service DBs and a shared API client. Rationale: isolation and easier QA.
- Decision: Use SQLite for per-service DBs in early MVP phase; rationale: simplicity and speed of iteration.
- Decision: Expose REST endpoints under /api/{service} with standard input validation and JSON response shapes.
- Decision: Implement QA harness to cover per-service interactions and end-to-end flows.
