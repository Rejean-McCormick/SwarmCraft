Educational Anatomy Prompt Generator API - Test Plan

Objective
- Validate correctness, security, and performance of the prompt generator API.
- Cover functional correctness (CRUD, admin bulk generation), input validation, error handling, rate limiting, and basic security checks.
- Provide edge-case analysis and load testing guidelines.

Scope
- Endpoints under /prompts and admin endpoints under /admin/prompts as implemented by Codey McBackend.
- Health check endpoint /health.
- Database: SQLite-based prompts storage.
- Frontend integration surface: consumption of /prompts endpoints (high-level).

Assumptions
- API server runs on http://localhost:3000 by default; can be overridden via API_URL env var.
- Admin operations guarded by X-Admin-Token header; token provided via ADMIN_TOKEN env var in tests.
- Server supports basic pagination on GET /prompts with page and limit query params.

Test Deliverables
1. Functional test suite for CRUD behavior and admin bulk generation.
2. Negative/edge-case tests for input validation and security.
3. Simple load/test for bulk generation concurrency.
4. A test report summarizing results, failures, and recommendations.
5. Test scripts: unit-like tests (prompt_gen.test.js) and load tests (load_test_prompt_gen.js).

Test Scenarios
1. Health endpoint
2. Create prompt with valid seed -> expect success and content unique
3. Retrieve prompt by ID -> verify content matches
4. List prompts with pagination -> verify structure and counts
5. Duplicate seed -> expect conflict (409)
6. Seed validation -> negative seed or non-integer -> expect 400
7. Admin bulk generate unauthorized -> expect 401/403
8. Admin bulk generate authorized -> expect 202; verify new items via stats endpoint
9. Delete prompt by ID -> verify removal
10. Admin stats endpoint -> sanity check total count reflects operations

Edge Cases
- Very large seed value (e.g., 999999999) to test numeric handling
- Non-numeric seed in payload
- Empty/missing fields in POST /prompts
- Admin token case-sensitivity and header variations
- Concurrency: simultaneous create requests to test race conditions and duplicates

Performance/Load
- Bulk generate 5-50 prompts in test; observe response time and server blocking behavior.
- Optional: parallel burst test with 20-100 concurrent create requests.

Test Data Management
- Cleanup created prompts to prevent DB growth during CI.
- Ensure idempotency where applicable.

Environment & Prerequisites
- Node.js environment with network access to API.
- API_URL env variable can override base URL; default to http://localhost:3000.
- ADMIN_TOKEN env variable for admin tests.

Success Criteria
- All tests pass within the defined time limits and do not crash the API.
- Security tests validate admin-only endpoints are protected.
- No unhandled exceptions, and error messages are consistent.

Test Execution & Reporting
- Run: node scratch/shared/test/prompt_gen.test.js
- Optional: node scratch/shared/test/load_test_prompt_gen.js
- Report format: scratch/shared/test_reports/TEST_REPORT.md with a summary, list of failures, and recommended fixes.
