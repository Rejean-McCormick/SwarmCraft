const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const path = require('path');
const fs = require('fs');

// DB path resolution: SCRATCH_DB_PATH env var takes precedence; otherwise use on-disk path under scratch/shared/data/users.db
const DB_PATH = process.env.SCRATCH_DB_PATH || path.join(__dirname, '../data/users.db');
let db = null;
let initPromise = null;

function getDb() {
  if (initPromise) return initPromise;
  initPromise = new Promise((resolve, reject) => {
    try {
      // Ensure directory exists
      const dir = path.dirname(DB_PATH);
      if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
      }
      const sqlite3 = require('sqlite3').verbose();
      const database = new sqlite3.Database(DB_PATH, (err) => {
        if (err) return reject(err);
        db = database;
        // Ensure table exists
        const createSql = `CREATE TABLE IF NOT EXISTS users (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          name TEXT NOT NULL,
          email TEXT UNIQUE NOT NULL,
          created_at TEXT NOT NULL
        )`;
        db.run(createSql, (err2) => {
          if (err2) return reject(err2);
          resolve(db);
        });
      });
    } catch (e) {
      reject(e);
    }
  });
  return initPromise;
}

function isValidEmail(email) {
  if (typeof email !== 'string') return false;
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return re.test(email);
}

function mapUser(row) {
  if (!row) return null;
  const { id, name, email, created_at } = row;
  return { id, name, email, created_at };
}

const router = express.Router();
router.use(express.json());

// GET /users - list all users
router.get('/', async (req, res) => {
  try {
    await getDb();
    db.all('SELECT id, name, email, created_at FROM users', [], (err, rows) => {
      if (err) {
        console.error('Error fetching users', err);
        return res.status(500).json({ error: 'Internal Server Error' });
      }
      res.json(rows.map(mapUser));
    });
  } catch (e) {
    console.error('GET /users init error', e);
    res.status(500).json({ error: 'Internal Server Error' });
  }
});

// POST /users - create a new user
router.post('/', async (req, res) => {
  try {
    const { name, email } = req.body || {};
    if (typeof name !== 'string' || name.trim().length === 0) {
      return res.status(400).json({ error: 'Invalid or missing name' });
    }
    if (!isValidEmail(email)) {
      return res.status(400).json({ error: 'Invalid or missing email' });
    }

    const trimmedName = name.trim();
    const trimmedEmail = email.trim();
    const created_at = new Date().toISOString();

    await getDb();
    db.run(
      'INSERT INTO users (name, email, created_at) VALUES (?, ?, ?)',
      [trimmedName, trimmedEmail, created_at],
      function (err) {
        if (err) {
          if (err.message && err.message.toLowerCase().includes('unique') || err.code === 'SQLITE_CONSTRAINT') {
            return res.status(409).json({ error: 'User with this email already exists' });
          }
          console.error('Error inserting user', err);
          return res.status(500).json({ error: 'Internal Server Error' });
        }
        const id = this.lastID;
        res.status(201).json({ id, name: trimmedName, email: trimmedEmail, created_at });
      }
    );
  } catch (e) {
    console.error('Unhandled error in POST /users', e);
    res.status(500).json({ error: 'Internal Server Error' });
  }
});

// GET /users/:id - fetch by id
router.get('/:id', async (req, res) => {
  try {
    const id = parseInt(req.params.id, 10);
    if (Number.isNaN(id)) {
      return res.status(400).json({ error: 'Invalid user id' });
    }
    await getDb();
    db.get('SELECT id, name, email, created_at FROM users WHERE id = ?', [id], (err, row) => {
      if (err) {
        console.error('Error fetching user by id', err);
        return res.status(500).json({ error: 'Internal Server Error' });
      }
      if (!row) {
        return res.status(404).json({ error: 'User not found' });
      }
      res.json(mapUser(row));
    });
  } catch (e) {
    console.error('Unhandled error in GET /users/:id', e);
    res.status(500).json({ error: 'Internal Server Error' });
  }
});

// Test helper: reset database contents (for unit tests to isolate state)
async function resetDatabase() {
  try {
    await getDb();
    return new Promise((resolve, reject) => {
      db.run('DELETE FROM users', [], function (err) {
        if (err) return reject(err);
        resolve();
      });
    });
  } catch (e) {
    // ignore
  }
}

router.resetDatabase = resetDatabase;

module.exports = router;
