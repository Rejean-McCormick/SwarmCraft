# JokeGen API (Draft Documentation)

This document describes the JokeGen API endpoints, data model, and usage examples. It is aligned with an OpenAPI draft for API consumers and UI integration.

## Endpoints
- GET /api/jokes?count=N
  - Returns an array of N jokes (default 1, max 100)
- POST /api/jokes
  - Creates a new joke with payload { setup, punchline, category?, author? }
  - Returns 201 Created with the created joke including id and created_at

## Data Model
- Joke: id, setup, punchline, category, author, created_at
- JokeInput: setup, punchline, category?, author?

## OpenAPI Draft
- See scratch/shared/openapi/jokegen.yaml for the OpenAPI draft. Keep in sync with runtime behavior.

## Batch API (MVP v2)
- The MVP v2 surface introduces batch creation and batch status endpoints behind a feature flag. This provides end-to-end batch generation workflow.

### Batch Endpoints (MVP v2 behind feature flag)
- POST /api/jokes/batches
  - Payload: { batchSize: integer (1-1000), prompts?: string[] }
  - Responses:
    - 202: { batchId: string, status: string, total: integer }
    - 400: { error: string }
- GET /api/jokes/batches/{batchId}/status
  - Responses:
    - 200: { batchId: string, status: string, total: integer, createdIds?: integer[], startedAt?: string, completedAt?: string, error?: string }

### Batch Status & Polling
- Poll the status endpoint until status === 'completed' or 'failed'.
- See the separate batch_status_polling.md for polling guidance.

## Usage Examples
- GET example:
  - GET http://localhost:8080/api/jokes?count=3
- POST example:
  - POST http://localhost:8080/api/jokes
  - {
      "setup":"A joke?",
      "punchline":"Yes!"
    }

## Batch API Examples (MVP v2 behind feature flag)
- Create batch (examples only, payloads may vary by runtime):
  - POST http://localhost:8080/api/jokes/batches
  - {"batchSize": 3}
  - Response: {"batchId":"b123","status":"in_progress","total":3}
- Check status:
  - GET http://localhost:8080/api/jokes/batches/b123/status
  - Response: {"batchId":"b123","status":"in_progress","total":3}

## Error Handling
- 400: Missing required fields or invalid payload (e.g., batchSize outside 1-1000)
- 404: Batch not found
- 429: Rate limit exceeded (to be implemented in production)
- 500: Internal server error

## Environment Variables
- PORT: Server port (default 8080)
- JOKE_DB_PATH: Path for SQLite database (optional)
- AUTH_ENABLED: Enable authentication (future)
- ENABLE_V2_BATCH: Enable MVP v2 batch endpoints behind feature flag (default: true for MVP docs)

## Deployment Notes
- Containerized with multi-stage Dockerfile
- CI/CD: Run tests, build image, run smoke tests

## Security
- Input validation and deduplication by content hash
- CORS and authentication to be added for production

## Cross-reference
- jokegen_batch_api.md: Batch API reference for endpoints and payloads
- batch_status_dashboard.md: Dashboard guidance
- API_DOCS.md: API navigation and surface descriptions
