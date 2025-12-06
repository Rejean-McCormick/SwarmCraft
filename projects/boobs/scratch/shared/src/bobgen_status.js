// BobGen Status API with SQLite-backed persistence

const express = require('express');
const path = require('path');
let app = express();
app.use(express.json());

// Database setup (SQLite)
const sqlite3 = require('sqlite3');
let db = null;
let dbInitPromise = null;

function getDbPath() {
  // Prefer env var, otherwise a file inside data/ directory next to this file
  const envPath = process.env.BOBGEN_DB_PATH;
  if (envPath && envPath.trim()) return envPath;
  // Resolve to scratch/shared/data/bobgen.sqlite
  return path.resolve(__dirname, '..', 'data', 'bobgen.sqlite');
}

function ensureDbReady() {
  if (dbInitPromise) return dbInitPromise;
  dbInitPromise = new Promise((resolve, reject) => {
    const dbPath = getDbPath();
    const opened = new sqlite3.Database(dbPath, (err) => {
      if (err) return reject(err);
      db = opened;
      // Create table if not exists
      const createSql = `
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
        )
      `;
      db.run(createSql, (err) => {
        if (err) return reject(err);
        // Seed if empty
        db.get('SELECT COUNT(*) AS c FROM bobgen_status', [], (err, row) => {
          if (err) return reject(err);
          const count = row && row.c ? row.c : 0;
          if (count > 0) {
            return resolve();
          }
          // Seed a minimal initial row to satisfy legacy expectations
          const seed = {
            id: '1',
            uptime: '72h',
            version: '1.0.0',
            latency: 120,
            error_rate: 0.01,
            last_run: new Date().toISOString(),
            status: 'healthy',
            blocks: JSON.stringify([]),
            runbook_link: 'https://example.com/runbooks/bobgen',
            dashboard_link: 'https://example.com/dashboard/bobgen'
          };
          const insertSql = `
            INSERT INTO bobgen_status (id, uptime, version, latency, error_rate, last_run, status, blocks, runbook_link, dashboard_link)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
          `;
          db.run(insertSql, [seed.id, seed.uptime, seed.version, seed.latency, seed.error_rate, seed.last_run, seed.status, seed.blocks, seed.runbook_link, seed.dashboard_link], (err) => {
            if (err) return reject(err);
            resolve();
          });
        });
      });
    });
  });
  return dbInitPromise;
}

function formatStatusRow(row) {
  // Normalize blocks field to an array
  let blocks = [];
  if (row && typeof row.blocks === 'string') {
    try {
      blocks = JSON.parse(row.blocks);
    } catch (e) {
      blocks = [];
    }
  } else if (Array.isArray(row?.blocks)) {
    blocks = row.blocks;
  } else if (row?.blocks) {
    blocks = [row.blocks];
  }
  return {
    id: row.id,
    uptime: row.uptime,
    version: row.version,
    latency: row.latency,
    error_rate: row.error_rate,
    last_run: row.last_run,
    status: row.status,
    blocks,
    runbook_link: row.runbook_link,
    dashboard_link: row.dashboard_link
  };
}

async function getStatuses() {
  await ensureDbReady();
  return new Promise((resolve, reject) => {
    const sql = `SELECT id, uptime, version, latency, error_rate, last_run, status, blocks, runbook_link, dashboard_link FROM bobgen_status ORDER BY created_at DESC`;
    db.all(sql, [], (err, rows) => {
      if (err) return reject(err);
      const formatted = rows.map(formatStatusRow);
      resolve(formatted);
    });
  });
}

async function getStatusById(id) {
  await ensureDbReady();
  return new Promise((resolve, reject) => {
    const sql = `SELECT id, uptime, version, latency, error_rate, last_run, status, blocks, runbook_link, dashboard_link FROM bobgen_status WHERE id = ?`;
    db.get(sql, [id], (err, row) => {
      if (err) return reject(err);
      if (!row) return resolve(null);
      resolve(formatStatusRow(row));
    });
  });
}

// Start Express server as before, but DB is lazy-initialized
// Health check
app.get('/health', (req, res) => {
  let pkgVersion = '0.0.0';
  try {
    pkgVersion = require('../package.json').version || '0.0.0';
  } catch (e) {
    pkgVersion = '0.0.0';
  }
  res.json({ ok: true, uptime: process.uptime(), version: pkgVersion });
});

// GET /bobgen/status - list statuses
app.get('/bobgen/status', async (req, res) => {
  try {
    const list = await getStatuses();
    res.json(list);
  } catch (e) {
    console.error(e);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// GET /bobgen/status/:id - single status
app.get('/bobgen/status/:id', async (req, res) => {
  try {
    const id = req.params.id;
    const status = await getStatusById(id);
    if (!status) return res.status(404).json({ error: 'Not found' });
    res.json(status);
  } catch (e) {
    console.error(e);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Start server when run directly; ensure DB startup is wired so requests can wait
if (require.main === module) {
  const port = process.env.PORT || 3000;
  // Ensure DB on startup and then listen
  ensureDbReady().then(() => {
    const server = app.listen(port, () => {
      console.log(`BobGen status API listening on port ${port}`);
    });
    // Graceful shutdown on SIGTERM
    process.on('SIGTERM', () => server && server.close());
  }).catch((err) => {
    console.error('Failed to initialize database', err);
    process.exit(1);
  });
}

module.exports = app;
