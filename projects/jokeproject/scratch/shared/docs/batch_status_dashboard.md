# Batch Status Dashboard (MVP)

Overview:
- Visualize the progress of async batch joke generation.
- Designed to work with the v2 MVP batch endpoints behind the feature flag.

API surface:
- POST /api/jokes/batches
  - Request body example:
    - { "batchSize": 5, "prompts": [] }
  - Response example:
    - { "batchId": "batch_12345", "status": "in_progress" }
- GET /api/jokes/batches/{batchId}/status
  - Response example:
    - {
        "batchId": "batch_12345",
        "total": 5,
        "remaining": 2,
        "createdIds": ["j1", "j2", "j3"],
        "status": "in_progress",
        "startedAt": "2025-01-01T12:00:00Z",
        "completedAt": null,
        "error": null
      }

Data model:
- BatchStore (in memory / persisted):
  - batchId: string
  - total: int
  - remaining: int
  - createdIds: string[]
  - status: string
  - startedAt: timestamp
  - completedAt: timestamp | null
  - error: string | null
- Jokes (storage):
  - IDs persisted; dedupe is based on content hash in the SQLite JokeStore

Polling strategy:
- Client polls the status endpoint every 2-3 seconds until a terminal state is reached (completed or failed), or a timeout is hit (e.g., 60 seconds).
- Optional: implement exponential backoff in the client if desired.

UI hooks:
- batch_dashboard.html / batch_dashboard.js provide hooks to:
  - Create a new batch via POST /api/jokes/batches
  - Poll GET /api/jokes/batches/{batchId}/status and refresh the UI
  - Render a dashboard grid of cards per batch with progress bars and counts
  - Show createdIds in a compact list or chips; allow loading more details on demand

Sample UI layout (HTML skeleton):
- The UI is scaffolded and ready to wire to the API; this is a minimal sketch that can be wired to the status endpoint.

/OpenAPI alignment notes:
- Align the OpenAPI spec with the posted paths and payload shapes for the v2 MVP batch surface behind a feature flag.

Roadmap (future enhancements):
- Real-time updates via WebSocket or Server-Sent Events (SSE)
- Sorting, filtering, and batch-level analytics
- Stronger typing of batch state and error handling
