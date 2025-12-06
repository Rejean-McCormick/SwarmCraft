Master Plan: Mock E-commerce MVP

Overview
- Objective: Build a local, goofy mock e-commerce MVP with a front-end, back-end, store, promotions, about-us, and admin store management. It will include a full mock checkout with a fake payment flow and an issued invoice. No real authentication; everything runs locally via Docker Compose. The tone will be absurd and humorous.

Technical Architecture
- Frontend: React (Vite)
- Backend: Node.js (Express)
- Database: SQLite (local MVP)
- Deployment: Docker Compose (local)
- API surface summary: /api/products, /api/products/:id, /api/promotions, /api/pages/home, /api/checkout, /api/invoice/:id, and admin endpoints for frontpage updates

File Structure (high level)
- scratch/shared/frontend/
- scratch/shared/backend/
- scratch/shared/db/
- scratch/shared/utils/
- scratch/shared/docs/

Implementation Phases (numbered)
1) Phase 1: Scaffolding
2) Phase 2: Store, Promotions, About Us, Homefront, Admin panel UI
3) Phase 3: Checkout flow and invoice generation
4) Phase 4: Frontpage updates & copy
5) Phase 5: QA, docs, and polish

Task Breakdown per Phase
Phase 1
- File: scratch/shared/backend/server.js
- File: scratch/shared/db/schema.sql
- File: scratch/shared/db/seeds.sql
- File: scratch/shared/frontend/src/main.jsx

Phase 2
- File: scratch/shared/backend/routes/products.js
- File: scratch/shared/frontend/src/pages/Store.jsx
- File: scratch/shared/frontend/src/pages/AdminStore.jsx

Phase 3
- File: scratch/shared/backend/utils/mockPayment.js
- File: scratch/shared/backend/routes/checkout.js
- File: scratch/shared/utils/invoice.js

Phase 4
- File: scratch/shared/frontend/src/pages/Home.jsx
- File: scratch/shared/frontend/src/components/AdminFrontpageEditor.jsx

Phase 5
- File: scratch/shared/tests/
- File: scratch/shared/docs/API.md
