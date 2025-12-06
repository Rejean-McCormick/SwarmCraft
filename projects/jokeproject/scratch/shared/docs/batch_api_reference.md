# Batch API Reference for JokeGen

Purpose: Provide a precise contract for batch-based joke generation endpoints. This document describes the request/response payloads, error semantics, and examples for the batch workflow. The MVP uses an in-memory BatchStore; a durable store is planned for production.

## Endpoints

### 1) POST /api/jokes/batches

Create and start a batch of jokes.

- Summary: Initiates batch generation of N jokes and returns a batchId for progress tracking.
- Request body (JSON):
  - batchSize: integer, 1-1000
  - prompts?: string[] (optional seeds/prompts for generation)

- Responses:
  - 202 Accepted
    - Example:
      {
        "batchId": "batch-abc-123",
        "status": "in_progress",
        "total": 5,
        "createdIds": []
      }
  - 400 Bad Request: Invalid payload (e.g., missing batchSize, out-of-range batchSize)
  - 429 Too Many Requests: Rate limited
  - 500 Internal Server Error: Server-side failure

- Behavior:
  - Batch is created and tracked in MVP in-memory store.
  - The API returns immediately with status in_progress and a batchId; the actual joke creation happens asynchronously in the background.
  - createdIds is populated as jokes are persisted; initial response may show an empty list.

- Notes:
  - For production, batch state should be persisted in a durable store.

- Example (curl):
  curl -X POST \
    -H "Content-Type: application/json" \
    -d '{"batchSize": 5, "prompts": ["seed one", "seed two"]}' \
    http://localhost:8080/api/jokes/batches

- Response (202):
  {
    "batchId": "batch-abc-123",
    "status": "in_progress",
    "total": 5,
    "createdIds": []
  }

---

### 2) GET /api/jokes/batches/{batchId}/status

Poll the status of a previously created batch.

- Path parameter:
  - batchId: string (opaque identifier; e.g., batch-abc-123)

- Responses:
  - 200 OK
    - Example 1 (in progress):
      {
        "batchId": "batch-abc-123",
        "status": "in_progress",
        "total": 5,
        "createdIds": ["id-1", "id-2"],
        "startedAt": "2025-12-05T12:00:00Z",
        "completedAt": null,
        "error": null
      }
    - Example 2 (completed):
      {
        "batchId": "batch-abc-123",
        "status": "completed",
        "total": 5,
        "createdIds": ["id-1", "id-2", "id-3", "id-4", "id-5"],
        "startedAt": "2025-12-05T12:00:00Z",
        "completedAt": "2025-12-05T12:01:30Z",
        "error": null
      }
  - 404 Not Found: Batch not found for the given batchId
  - 400 Bad Request: Invalid batchId format (if enforced)
  - 500 Internal Server Error: Server-side failure

- Fields:
  - batchId: string
  - status: string (enum: pending | in_progress | completed | failed)
  - total: integer (total number of jokes intended for this batch)
  - createdIds: string[] (list of IDs created so far; grows as jokes are created)
  - startedAt?: string (ISO timestamp)
  - completedAt?: string (ISO timestamp when completed)
  - error?: string (present if status is failed)

- Notes:
  - MVP tracks status in-memory; this will become a durable store in a future version.

- curl example:
  curl http://localhost:8080/api/jokes/batches/batch-abc-123/status | jq

---

### 3) Optional: Health and related endpoints (out of scope for primary batch API)
- You may want to add /healthz and /metrics in production; describe in a separate doc.

## Payload Schemas

### JokeBatchInput
- batchSize: integer [1, 1000]
- prompts?: string[]

### BatchStatusResponse
- batchId: string
- status: string enum: pending | in_progress | completed | failed
- total: integer
- createdIds: string[]
- startedAt?: string (ISO 8601)
- completedAt?: string
- error?: string

### CreateBatchResponse (202)
- batchId: string
- status: string (in_progress or similar)
- total: integer
- createdIds?: string[]

## Examples (Quick Reference)
- Create batch:
  POST /api/jokes/batches
  {
    "batchSize": 3,
    "prompts": ["seed1", "seed2"]
  }
  Response 202:
  {
    "batchId": "batch-xyz-789",
    "status": "in_progress",
    "total": 3,
    "createdIds": []
  }

- Check status:
  GET /api/jokes/batches/batch-xyz-789/status
  Response (in_progress):
  {
    "batchId": "batch-xyz-789",
    "status": "in_progress",
    "total": 3,
    "createdIds": ["joke-1"],
    "startedAt": "2025-12-05T12:00:00Z",
    "completedAt": null,
    "error": null
  }

- Completed:
  Response (completed):
  {
    "batchId": "batch-xyz-789",
    "status": "completed",
    "total": 3,
    "createdIds": ["joke-1", "joke-2", "joke-3"],
    "startedAt": "2025-12-05T12:00:00Z",
    "completedAt": "2025-12-05T12:01:15Z",
    "error": null
  }

## Notes
- This document is part of the MVP. Durable batch state persistence and production-grade reliability will be introduced in a follow-up release.
- OpenAPI spec should be kept in sync with this contract. See jokegen.yaml for the concrete schema definitions.
