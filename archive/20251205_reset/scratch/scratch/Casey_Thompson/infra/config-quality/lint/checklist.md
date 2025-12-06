Lint checklist for config wiring to log-sink audit

- [ ] Validate endpoint format and reachability
- [ ] Validate auth config (mtls) and TLS presence
- [ ] Validate Vault address, path, and secret name
- [ ] Validate IAM role/service account permissions (least privilege)
- [ ] Validate retention_days is a positive integer (default 365)
- [ ] Validate request_id tracing flag is enabled when required
- [ ] Check for rotation plan alignment with Vault certs
- [ ] Verify staging/dry-run scaffold exists and runs without destructive actions
- [ ] Confirm that secrets are not committed; placeholders only
- [ ] Verify end-to-end test exists (tests/e2e_audit_test.py)
- [ ] Confirm rollback_plan and monitoring metrics are documented
