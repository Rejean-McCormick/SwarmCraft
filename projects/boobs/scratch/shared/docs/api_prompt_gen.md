# Educational Anatomy Prompt Generator API

Endpoints:
- POST /prompts
  - Body: { seed: integer }
  - Creates a single prompt deterministically from seed.
- GET /prompts
  - Query: page, limit
  - Returns paginated list with total count
- GET /prompts/:id
  - Returns a single prompt
- DELETE /prompts/:id
  - Deletes a prompt by id

Admin:
- POST /admin/prompts/generate?count=N
  - Header: X-Admin-Token: <token>
  - Starts background generation of N prompts (default 100000)
- GET /admin/prompts/stats
  - Returns total count

Notes:
- Content is unique due to seed-based generation and content text.
- Rate limiting is applied perIP on public endpoints.
