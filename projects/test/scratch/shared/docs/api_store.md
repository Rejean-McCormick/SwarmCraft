Store MVP API Endpoints

- Base: /api/store
- Products
  - GET /products
  - GET /products/:id
  - POST /products
  - PUT /products/:id
  - DELETE /products/:id
- Promotions
  - GET /promotions
  - GET /promotions/:id
  - POST /promotions
  - PUT /promotions/:id
  - DELETE /promotions/:id

Notes:
- This MVP uses a SQLite DB with tables: products, promotions.
- No authentication in MVP.
- Responses follow { ok: boolean, data? } pattern with standard HTTP status codes.
