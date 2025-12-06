A0382c3a Minimal Test Plan - Discord Bot Backend (Node.js)

Objective
- Provide a lightweight, automated set of tests validating security, resilience, and basic functionality expectations for the Discord bot backend.

Scope
- Unit tests for security utilities, input sanitization, and retry/backoff logic.
- Lightweight integration stubs for LLM wrapper and Discord command flow using mocks.
- No tests depend on live Discord network connectivity; tests run in isolation with mocks.

Test plan
- Security:
  - Validate that sensitive fields do not appear in logs (redaction test).
  - Validate secret handling utilities redact secrets from objects/logs.
  - Basic input sanitization to prevent leaking tokens in prompts.
- Stability/Resilience:
  - Validate exponential backoff function increases delay with attempts and caps.
  - Validate retry behavior respects cap and jitter (where applicable).
- Input handling:
  - Validate input sanitization removes emails and API keys in prompts.
- Observability (static checks):
  - Ensure services expose deterministic health endpoints (conceptual in this plan).

Environment
- Node.js 18+ runtime assumed.
- No external service keys required to run unit tests; tests use local utilities.

Acceptance criteria
- All test files exist under shared/backend/tests and can be discovered by a simple test runner.
- run_tests.js can execute all tests and report PASS/FAIL.
- Tests cover at least: redactSecretsInObject, sanitizePromptInput, and exponentialBackoff.

Non-functional considerations
- Tests are lightweight and deterministic.
- Tests do not require network access or Discord login.
- Tests avoid touching real tokens or credentials.
