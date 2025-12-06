Config Quality: Lint, Staging Dry-Run, and E2E Audit

Overview
- This repository houses artifacts for validating log-sink wiring to Vault-backed secrets.
- Includes lint checks, a staging dry-run scaffold, and an end-to-end audit test plan with request_id tracing and 1-year retention.

Directory layout
- lint/: schemas, checklists, and validation utilities
- staging/: dry-run scaffolds and sample configs
- tests/: end-to-end tests and mocks
- monitoring/: metrics definitions and dashboards
- ops/: rollback and rotation notes
- security/: Vault rotation guides and access controls

How to use
- Start with lint checks against a wiring config before staging
- Run the staging dry-run against a mock Vault endpoint
- Execute the end-to-end audit test in a staging environment before prod

Exported artifacts
- lint/checklist.md
- lint/schema.json
- staging/dry_run.py (Python MVP) or dry_run.sh
- staging/config.sample.json
- tests/e2e_audit_test.py
- ops/rollback_plan.md
- monitoring/metrics.md
- security/vault_rotation.md
