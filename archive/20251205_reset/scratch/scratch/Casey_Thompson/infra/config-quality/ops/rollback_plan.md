# Rollback Plan

- Revert config changes in config store
- Revoke test service accounts and credentials
- Point logs back to previous sink or introduce a safe dead-letter
- Validate with staging rollback before prod
