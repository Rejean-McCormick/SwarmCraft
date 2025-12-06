Staging dry-run guide

Purpose
- Validate wiring for log-sink audit integration against a Vault-backed secret store in a safe staging environment.
- Exercise end-to-end flow using a mock Vault endpoint before moving to prod.

What this covers
- Schema validation of the wiring config
- mTLS-based authentication to Vault (mocked in staging)
- End-to-end delivery to log-sink.internal/audit with request_id propagation
- 1-year retention (config-driven)
- Safe rollback and observability hooks for staging

How to run
- Prerequisites: Python 3.8+, virtualenv
- Create and activate venv: python -m venv venv && source venv/bin/activate
- Install requirements (if any): pip install -r requirements.txt (if present)
- Run MVP dry-run using the sample config:
  - python3 staging/dry_run.py --config staging/config.sample.json
  - or: bash staging/dry_run.sh --config staging/config.sample.json

What you’ll see
- Validation output for the wiring config
- A simulated Vault call path using a mock endpoint
- Logs showing delivery to log-sink.internal/audit with request_id
- Summary: success/failure, and a plan to promote to prod after staging checks

Notes
- This is a non-destructive dry-run intended to catch vault/endpoint access issues and misconfigurations before prod.
- When switching to real Vault, ensure VAULT_ADDR, TLS certs, and role-based access are provisioned.
- Update config.sample.json with real values only in prod-ready environments.
