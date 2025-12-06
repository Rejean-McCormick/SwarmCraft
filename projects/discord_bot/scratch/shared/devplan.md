# Master Dev Plan Dashboard (live)

Status: In Progress. Go signal received; tasks are being executed by the swarm.

Plan Overview
- Standup cadence locked and tracked
- Per-service scaffolding for authentication (auth) across four parallel tasks
- CI/CD infra scaffolding for per-service modules
- QA harness expansion to cover per-service interactions
- Documentation updates to contracts and blockers

Ownership & Tasks
- Codey McBackend 7: Implement per-service authentication scaffolding under scratch/shared/src/modules/auth with Express server exposing POST /api/auth/register and POST /api/auth/login; SQLite DB for users; bcrypt hashing; JWT issuance; validation; tests scaffold in tests/ (test_auth.py)
- Codey McBackend 8: Implement per-service authentication scaffolding (DB schema planning and wiring) - same endpoints and DB; ensure separation per service
- Codey McBackend 9: Implement per-service authentication scaffolding (JWT integration and token flows) - robust error payloads
- Codey McBackend 10: Implement per-service authentication scaffolding (validation and test scaffolding) - test_auth.py tests scaffold
- Deployo McOps: Prepare CI/CD scaffolding for per-service modules: Dockerfiles, Kubernetes skeletons, GitHub Actions workflows
- Bugsy McTester: Extend QA harness to cover per-service module interactions with end-to-end tests
- Docy McWriter: Update blockers/status docs, API contracts matrix, onboarding README for auth scaffolding
- Checky McManager: Lock standup cadence and ownership; coordinate blockers

Blockers & Risks
- ⚠️ Standup scheduling alignment and owner confirmation
- ⚠️ API contracts alignment across per-service modules (Auth/Wallet/Shop/Games)
- ⚠️ CI/CD gating and live Dev Plan integration
- ⚠️ Inter-service authentication wiring across modules

Next Steps
- Confirm standup times and owners; publish final contract matrix; begin per-service scaffolding work in parallel
- Iterate on QA harness to cover broader end-to-end scenarios and negative paths
- Ensure Dev Plan reflects blockers and decision points