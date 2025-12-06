# Test Plan - User API

- Verify GET /users returns list and 200
- Verify POST /users creates user and returns 201 with id
- Verify GET /users/:id returns 200 with user data
- Validate invalid input handling (400)
- Validate duplicate emails (409)
- Validate on-disk DB path SCRATCH_DB_PATH usage
