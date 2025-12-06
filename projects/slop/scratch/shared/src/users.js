const express = require('express');
const sqlite3 = require('sqlite3').verbose();

/**
 * Creates an Express Router with in-memory SQLite-backed user endpoints:
 * - GET /users
 * - POST /users
 * - GET /users/:id
 *
 * Validation rules:
 * - POST /users requires { name, email } with valid formats
 * - GET /users/:id validates numeric id
 *
 * Note: This router maintains its own in-memory database instance.
 */
function createUsersRouter() {
  const router = express.Router();

  // Initialize in-memory SQLite database
  const db = new sqlite3.Database(':memory:');

  const initSql = `
    CREATE TABLE IF NOT EXISTS users (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL,
      email TEXT NOT NULL UNIQUE,
      created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
  `;

  // Promise that resolves once the schema is created
  const initPromise = new Promise((resolve, reject) => {
    db.run(initSql, (err) => {
      if (err) {
        reject(err);
      } else {
        resolve();
      }
    });
  });

  // Helper wrappers for sqlite3 with promises
  const dbAll = (sql, params = []) => new Promise((resolve, reject) => {
    db.all(sql, params, (err, rows) => {
      if (err) reject(err); else resolve(rows);
    });
  });

  const dbGet = (sql, params = []) => new Promise((resolve, reject) => {
    db.get(sql, params, (err, row) => {
      if (err) reject(err); else resolve(row);
    });
  });

  // Routes
  // GET /users
  router.get('/', async (req, res) => {
    try {
      await initPromise;
      const rows = await dbAll('SELECT id, name, email, created_at FROM users ORDER BY id ASC');
      res.json({ users: rows });
    } catch (err) {
      console.error(err);
      res.status(500).json({ error: 'Internal server error' });
    }
  });

  // POST /users
  router.post('/', async (req, res) => {
    try {
      await initPromise;
      const { name, email } = req.body || {};

      // Validation
      if (typeof name !== 'string' || name.trim().length === 0) {
        return res.status(400).json({ error: 'Invalid or missing name' });
      }
      if (typeof email !== 'string' || !/^[^@]+@[^@]+\\.[^@]+$/.test(email)) {
        return res.status(400).json({ error: 'Invalid or missing email' });
      }

      const sql = 'INSERT INTO users (name, email) VALUES (?, ?)';
      db.run(sql, [name.trim(), email.trim()], function (err) {
        if (err) {
          // Email must be unique
          if (err.message && err.message.toLowerCase().includes('unique')) {
            return res.status(409).json({ error: 'Email already exists' });
          }
          return res.status(500).json({ error: 'Internal server error' });
        }
        const id = this.lastID;
        res.status(201).json({ id, name: name.trim(), email: email.trim(), created_at: new Date().toISOString() });
      });
    } catch (e) {
      console.error(e);
      res.status(500).json({ error: 'Internal server error' });
    }
  });

  // GET /users/:id
  router.get('/:id', async (req, res) => {
    try {
      await initPromise;
      const id = parseInt(req.params.id, 10);
      if (Number.isNaN(id)) {
        return res.status(400).json({ error: 'Invalid id' });
      }

      const row = await dbGet('SELECT id, name, email, created_at FROM users WHERE id = ?', [id]);
      if (!row) {
        return res.status(404).json({ error: 'User not found' });
      }
      res.json(row);
    } catch (e) {
      console.error(e);
      res.status(500).json({ error: 'Internal server error' });
    }
  });

  return router;
}

module.exports = createUsersRouter;
