Merge MVP v2 Batch Endpoints into Main API Path — Integration Plan (Option A)

Objective
- Validate and plan the end-to-end integration of MVP v2 batch endpoints into the main API surface once the exclusive lock on scratch/shared/src/joke_gen_api.js is released.
- Ensure the integration is covered by tests, docs, and a clear rollback plan.

High-level approach
- Merge v2 batch endpoints from scratch/shared/src/joke_gen_api_v2.js into scratch/shared/src/joke_gen_api.js, reusing the existing storage.js (JokeStore) and batch_store.js.
- Remove feature-flag gating for MVP batch endpoints on the main path.
- Update OpenAPI spec jokegen.yaml to reflect the merged endpoints:
  - POST /api/jokes/batches
  - GET /api/jokes/batches/{batchId}/status
- Extend tests to cover the merged path end-to-end:
  - Batch creation returns 202 with batchId and status
  - Status polling returns progress and final completed state
  - Correct createdIds length and data integrity
  - Input validation for invalid batchSize payloads
- Provide staging deployment plan with rollback steps.

Risk & Mitigations
- Risk: Merge conflicts and runtime regressions when unblocked. Mitigation: run full integration tests, implement a staged PR, and provide a rollback plan.
- Risk: Incomplete docs or test coverage. Mitigation: align docs with the merged implementation and extend tests accordingly.

Deliverables after lock release
- Merged code in scratch/shared/src/joke_gen_api.js
- Updated OpenAPI (jokegen.yaml)
- Expanded integration tests: batch_endpoints_integration_test.js plus merged_batch_integration_test.js
- Documentation updates: jokegen_batch_api.md, batch_status_dashboard.md, jokegen.md
- Deployment plan: staging target, secrets/registry strategy, rollback steps
