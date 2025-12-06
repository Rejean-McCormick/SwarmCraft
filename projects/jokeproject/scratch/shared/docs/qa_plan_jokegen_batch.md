# QA Plan for Jokegen Batch MVP (V2)

Objectives
- Validate batch creation, status progression, and final completion endpoints.
- Validate error paths (bad payload, non-existent batchId).
- Validate dedupe behavior and performance characteristics with small to medium batch sizes.

Test scope
- Unit tests: input validation, batch id generation, status computation
- Integration tests: end-to-end path using v2 MVP endpoints
- UI integration tests: polling cadence and status rendering hooks

Test data
- Batch sizes: 1, 5, 25, 100
- Prompts: varied length; ensure prompts influence and do not crash

Test environment
- Local dev environment with SQLite path for JokeStore
- Exit criteria: tests pass in CI with v2 MVP path enabled

Risks & mitigations
- Risk: Hidden behavior differences between v2 and main path might leak once unblocked. Mitigation: keep v2 isolated behind feature flag and maintain a close contract with main path for eventual merge.

Sign-off
- Owner: QA Team
- Date: TBD
