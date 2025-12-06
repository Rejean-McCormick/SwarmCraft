# Jokegen Batch API (MVP v2)

Endpoints:
- POST /api/jokes/batches
  - Payload: { batchSize: number, prompts?: string[] }
  - Responses: 202 with { batchId, status, total }
- GET /api/jokes/batches/{batchId}/status
  - Responses: 200 with { batchId, status, total, createdIds, startedAt, completedAt, error }

Notes:
- This surface is part of the MVP v2 path behind a feature flag. After the main path unlock, this will be merged into the main API surface.
