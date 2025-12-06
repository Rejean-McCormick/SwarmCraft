# Batch MVP Test Plan

This document outlines the test strategy for the MVP v2 batch endpoints.

- Happy path: POST /api/jokes/batches with valid payload; receive 202 with batchId; poll until status becomes completed; verify createdIds length equals total.
- Validation: Missing payload → 400; invalid batchSize (0, >1000) → 400.
- Unknown batchId → 404 on status query.
- Polling timeout handling: timeout if status does not reach terminal state within X seconds.
- Deduplication: ensure repeated jokes are deduped via storage.js; same content should map to the same joke ID.
- Concurrency: verify up to 4 workers (or configured max) run in parallel.

Notes:
- This test plan assumes the v2 MVP endpoints are accessible behind the feature flag.
