# Master Plan - Modular Backend for Discord Bot

Overview
- Build a modular backend split into Auth, Wallet, Shop, and Games services with clear API contracts and per-service SQLite databases.
- Provide a shared infra layer and a code generator to scaffold new services.
- Ensure strong QA coverage, security posture, and observability while keeping CI/CD out of scope for now (per Kyle).

System Architecture
- Services: Auth, Wallet, Shop, Games (standalone REST services)
- Shared Infra: API gateway (routing), common error handling, validation, and contract tests
- Data: SQLite per-service databases, isolated data stores, with migration-friendly approach
- Interaction: REST-based contracts between services and a lightweight API gateway for clients

Service Modules (scaffolds to deliver)
- Auth Service
  - Endpoints: POST /login, POST /signup, GET /me, POST /refresh
  - DB: auth.db with users, sessions, tokens
- Wallet Service
  - Endpoints: GET /balance, POST /transfer, POST /wallets/:id/deposit
  - DB: wallet.db with accounts, balances, transactions
- Shop Service
  - Endpoints: GET /items, POST /purchase, GET /orders/:id
  - DB: shop.db with products, orders, inventory
- Games Service
  - Endpoints: GET /games, POST /games/:id/play, GET /games/:id/score
  - DB: games.db with sessions, scores, results

Shared Infra & Tooling
- API Contracts: API contract specs per service (OpenAPI-ish docs in scratch/shared/contracts)
- Code Generator: Tool to scaffold new services with standard folders, routes, and tests
- Observability: Basic health checks for each service; centralized loggable events

Data & Security
- Data: SQLite per service; no cross-service DB sharing by default
- Security: Input validation, auth-layer enforcement, and basic rate limiting considerations (policy TBD by human)

Testing & QA
- QA harness to test per-service and end-to-end flows (Bugsy McTester leads)
- Include security-focused tests and integration tests for service composition

Milestones & Deliverables
- Milestone 1: Service scaffolds and API contracts drafted
- Milestone 2: Per-service REST servers with SQLite DBs wired
- Milestone 3: QA harness extended for cross-service flows
- Milestone 4: Live Dev Plan dashboard wired to reflect progress

Risks & Mitigations
- R1: Incomplete API contracts delaying integration tests. Mitigation: Install a contract review checkpoint with Checky.
- R2: Environmental provisioning delays. Mitigation: Mocked environments and local DBs for initial testing.

Owner and Accountability
- Product Owner: Kyle (for priorities and gating)
- Lead Architect: Bossy McArchitect (this swarm)
- Implementation: Codey McBackend (per-service code), Bugsy McTester (QA harness), Checky McManager (dashboard)
