# Auth Module Contract (reified by code)

Endpoints:
- POST /auth/register
- POST /auth/login

Models:
- User (id, username, password_hash, created_at)
- Wallet (user_id, balance)

Errors: USER_EXISTS, INVALID_CREDENTIALS, INTERNAL
