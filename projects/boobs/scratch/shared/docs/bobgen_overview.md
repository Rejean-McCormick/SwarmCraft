# BobGen Overview

Mermaid diagram:

```
graph TD
  A[BobGen UI] -->|Calls| B[BobGen Status API]
  B --> C{Health}
  C -->|OK| D[(Healthy)]
```

## Endpoints
- GET /bobgen/status
- GET /bobgen/status/{id}
- GET /health

## Data model (response JSON)
- id
- uptime
- version
- latency
- error_rate
- last_run
- status
- blocks
- runbook_link
- dashboard_link

## Run locally
- Environment: PORT=3000
- Start: node scratch/shared/src/bobgen_status.js
- Tests: npm --prefix scratch/shared test

## DB-backed storage (Phase 1)

This phase introduces a SQLite-backed persistence layer for BobGen status.

### Why DB persistence
- Provides durable storage for statuses beyond in-memory lifecycle
- Enables migrations, seed data, and scalable querying

### Data model mapping to DB columns
- id -> TEXT PRIMARY KEY
- uptime -> TEXT
- version -> TEXT
- latency -> INTEGER (ms)
- latency_ms in code maps to latency in API
- error_rate -> REAL
- last_run -> TEXT (ISO8601 timestamp)
- status -> TEXT
- blocks -> TEXT (JSON array as string)
- runbook_link -> TEXT
- dashboard_link -> TEXT
- created_at -> DATETIME (defaults to CURRENT_TIMESTAMP)

### SQLite schema (example)

```
CREATE TABLE IF NOT EXISTS bobgen_status (
  id TEXT PRIMARY KEY,
  uptime TEXT,
  version TEXT,
  latency INTEGER,
  error_rate REAL,
  last_run TEXT,
  status TEXT,
  blocks TEXT,
  runbook_link TEXT,
  dashboard_link TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### Bootstrap / Seed instructions
- Environment variables:
  - BOBGEN_DB_PATH: path to SQLite database file (e.g., ./data/bobgen.sqlite)
  - ADMIN_TOKEN: Admin token for privileged endpoints (see docs for security)
- Seed options:
  1) Startup bootstrap (one-time): create DB and seed 100,000 records
  2) Admin seed on demand: expose a small seed script run via CLI

- Example seed script (Node):

```js
// scratch/shared/scripts/seed_bobgen_db.js
const sqlite3 = require('sqlite3');
const path = require('path');
const dbPath = process.env.BOBGEN_DB_PATH || path.resolve(__dirname, '../../data/bobgen.sqlite');

async function seed(count = 100000) {
  const db = new sqlite3.Database(dbPath);
  const run = (sql, params) => new Promise((resolve, reject) => {
    db.run(sql, params, function(err) { if (err) return reject(err); resolve(this); });
  });
  const all = (sql, params) => new Promise((resolve, reject) => {
    db.all(sql, params, (err, rows) => (err ? reject(err) : resolve(rows)));
  });
  await run(`CREATE TABLE IF NOT EXISTS bobgen_status (
    id TEXT PRIMARY KEY,
    uptime TEXT,
    version TEXT,
    latency INTEGER,
    error_rate REAL,
    last_run TEXT,
    status TEXT,
    blocks TEXT,
    runbook_link TEXT,
    dashboard_link TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
  )`);
  await run('DELETE FROM bobgen_status');
  await db.run('BEGIN TRANSACTION');
  for (let i = 1; i <= count; i++) {
    const blocks = JSON.stringify([]);
    await run(
      'INSERT INTO bobgen_status (id, uptime, version, latency, error_rate, last_run, status, blocks, runbook_link, dashboard_link) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
      [`${i}`, '24h', '1.0.0', Math.floor(Math.random() * 500) + 50, 0.01, new Date().toISOString(), 'healthy', blocks, 'https://example.com/runbooks/bobgen', 'https://example.com/dashboard/bobgen']
    );
    if (i % 1000 === 0) console.log('seed', i);
  }
  await db.run('COMMIT');
  db.close();
}
seed().catch(console.error);
```

- Run the seed:
  - ADMIN_TOKEN=seed npm run seed or node scratch/shared/scripts/seed_bobgen_db.js

### Migrations & Rollback notes
- Migrations should be versioned and applied in order. A simple pattern:
  - Create a migrations table bobgen_migrations (id INTEGER PRIMARY KEY, name TEXT, applied_at DATETIME)
  - Each migration adds a new schema change (e.g., ALTER TABLE bobgen_status ADD COLUMN last_run TEXT)
  - Rollback in SQLite is non-trivial; recommended approach is to:
    - Create a new table with updated schema
    - Copy data from old to new
    - Drop old table and rename new table
- Maintain a changelog entry per migration.

### Admin seed on demand
- Implement an endpoint protected by ADMIN_TOKEN to re-seed from a small script; document how to run.

### Troubleshooting
- If the database file path is not writable, adjust permissions or mount a volume.
- If migrations fail due to locked DB, ensure no other process is holding the DB handle during migration.

### Cross-references
- bobgen_api_reference.md for endpoint schemas and data model mapping
- bobgen_overview.md for overall architecture
