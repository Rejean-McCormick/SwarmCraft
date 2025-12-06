# Dev Plan Dashboard

Overall Status: Waiting for 'Go' to start execution. Plan updated to reflect per-service modular backend with owner-specific tasks.

## Overall Progress
- [ ] Ready to start once approval is given

## Tasks by Owner
### Codey McBackend
- [ ] Implement per-service scaffolds (Auth, Wallet, Shop, Games) with REST servers and SQLite DBs
- [ ] Ensure API contracts and data models are defined and wired
- [ ] Provide a code generator for new services

### Bugsy McTester
- [ ] Extend QA harness to cover per-service module interactions
- [ ] Add end-to-end flow tests across services
- [ ] Implement security-focused tests

### Checky McManager
- [ ] Create and maintain live Dev Plan dashboard in scratch/shared/devplan.md
- [ ] Regularly update progress and blockers
- [ ] Ensure priority handling for Checky tasks

## Blockers & Risks
- ⚠️ Kyle paused CI/CD and Kubernetes efforts; integration work may rely on human gating
- ⚠️ API contracts definition and alignment required
- ⚠️ Resource availability for ongoing dashboard maintenance
