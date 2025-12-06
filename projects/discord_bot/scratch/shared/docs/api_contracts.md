Module API Contracts and Data Models

Overview
- This document enumerates the per-module API contracts and the data models they manipulate. Each module exposes its endpoints, the expected request shapes, and the response payloads. All services use JSON over HTTP.

Auth (authentication / user accounts)
- Endpoints:
  - POST /auth/register
    - Request: { "username": "string", "password": "string" }
    - Response: { "id": "string", "username": "string" }
  - POST /auth/login
    - Request: { "username": "string", "password": "string" }
    - Response: { "token": "string", "user": { "id": "string", "username": "string" } }
- Data Models:
  - User: { id: string, username: string, password_hash: string, created_at: string }
  - Wallet: { user_id: string, balance: integer }

Wallet
- Endpoints:
  - GET /balance
    - Response: { "balance": integer }
- Data Models:
  - Wallet: { user_id: string, balance: integer }

Shop
- Endpoints:
  - GET /items
    - Response: [ { "id": integer, "name": string, "price": integer, "stock": integer } ]
- Data Models:
  - Item: { id: integer, name: string, price: integer, stock: integer }
  - Inventory: { user_id: string, item_id: integer, quantity: integer }

Games
- Endpoints:
  - POST /blackjack/start
    - Response: { "sessionId": "string" }
- Data Models:
  - Session: { session_id: string, type: string, user_id: string, state: string, data: string, created_at: string, updated_at: string }

Notes
- These contracts are intended to be reified by code in the modules and may be extended as new features are added.
