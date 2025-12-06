# JokeGen MVP Pathwork

This repository houses the MVP v2 batch endpoints for JokeGen, kept behind a feature flag behind the main API lock.

What’s included:
- MVP v2 batch endpoints: POST /api/jokes/batches, GET /api/jokes/batches/:batchId/status
- SQLite-backed JokeStore with dedupe
- In-memory BatchStore for MVP batch tracking
- Lightweight worker pool for joke generation
- Batch status dashboard docs and simple UI scaffold

When the main API lock is released, we’ll merge the v2 MVP into the main API surface and align docs accordingly.
