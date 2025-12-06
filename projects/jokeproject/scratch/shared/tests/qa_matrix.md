JokeGen QA Matrix

Goal: Validate JokeGen API endpoints (GET /api/jokes?count=N and POST /api/jokes), security basics, load/concurrency, dedup behavior, and test artifact generation.

Test Matrix and Pass/Fail Criteria
- TM-01: GET /api/jokes?count=N returns up to N jokes. count validations enforce 1 <= count <= 1000.
  - Pass: 200 and correct array length.
  - Fail: 400 for invalid count, 500 for server error.
- TM-02: GET /api/jokes without count returns 1 joke.
  - Pass: returns 1 joke.
- TM-03: POST /api/jokes with valid payload creates a joke (201) and returns id.
  - Pass: 201 and id present.
- TM-04: POST /api/jokes with missing required fields returns 400.
  - Pass: 400 and error message.
- TM-05: Deduplication on content_hash
  - Pass: Posting identical setups+punchlines yields an existing record (existing: true) or consistent dedupe behavior.
  - Fail: Duplicate is inserted again as separate record without dedupe indicator.
- TM-06: Concurrency GETs
  - Pass: 100 parallel GETs complete within acceptable latency; no failures.
- TM-07: Concurrency POSTs (batch generation prep)
  - Pass: 40 concurrent POSTs succeed; dedup risk observed only if content is identical (unique payloads avoid duplicates).
- TM-08: Boundary checks for count (0, 1001, non-numeric)
  - Pass: 400 for invalid values
- TM-09: Security baseline
  - Pass: Rate limiter blocks bursts and returns 429 where implemented; if not implemented yet, document as a known limitation and plan for future hardening.
- TM-10: OpenAPI/docs alignment sanity
  - Pass: OpenAPI draft surface aligns with runtime behavior. Basic doc endpoints accessible.

Test Artifacts
- qa_matrix.md is the canonical matrix document.
- Notes: See integration tests and load tests in scratch/shared/tests/ for automated coverage.
