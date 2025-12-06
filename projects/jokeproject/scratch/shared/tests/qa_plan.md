JokeGen QA Plan
================
Goal
- Validate core API endpoints: GET /api/jokes?count=N and POST /api/jokes
- Validate UI integration readiness (plan-based, not UI rendering here)
- Validate security surface (basic rate limiting and input validation)
- Validate load/concurrency and deduplication behaviors
- Produce test artifacts: integration tests, test data, run scripts, and a test matrix

Scope
- Functional tests for the current API surface using a running JokeGen API server
- Non-functional checks: basic load/concurrency tests, deduplication correctness, validation behavior, and error handling
- OpenAPI alignment sanity checks against runtime behavior

Test Matrix (high level)
- TM-01: GET /api/jokes?count=N with valid N (1-100)
- TM-02: GET /api/jokes?count=N with N omitted (default 1)
- TM-03: POST /api/jokes with valid payload
- TM-04: POST /api/jokes with missing fields (validation error 400)
- TM-05: Deduplication: POST the same joke payload twice and verify dedup behavior
- TM-06: Concurrency: perform multiple GET /api/jokes?count=1 in parallel
- TM-07: Concurrency: perform multiple POST /api/jokes with unique payloads in parallel (stress test)
- TM-08: Boundary: GET with invalid count value (e.g., 0, 9999) returns 400
- TM-09: Security: basic rate-limiting assertion (expects at least one 429 under rapid requests; if not observed, document as non-deterministic in current environment)
- TM-10: OpenAPI alignment: basic check that /api/jokes doc surface is discoverable (draft JSON can be retrieved if docs are served)

Test Environment
- Node.js runtime (nvm default)
- API server URL: http://localhost:8080
- Non-production environment: in-memory fallback should be exercised if DB is unavailable

Test Artifacts
- Integration tests: scratch/shared/tests/integration_joke_api_test.js
- Test data: seed payloads inside integration tests
- Run script: scratch/shared/tests/run_tests.sh

Run Rules
- All functional tests must pass to consider the API stable
- Deduplication tests rely on content_hash constraints in storage layer
- If the server is unavailable, tests must fail with a clear error
- Logs and artifacts should be clear and deterministic

Reporting
- Fail: Any test that does not meet expected Assertion
- Pass: All tests in TM-01..TM-10 pass

Notes
- For rate limiting (TM-09), behavior may vary by runtime; document the outcome and add a more robust test when a more deterministic limiter is in place.
