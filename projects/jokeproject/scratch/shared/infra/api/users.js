// Node.js Express-based User API with SQLite (on-disk) integration
// This file provides endpoints: GET / (list), POST / (create), GET /:id (retrieve by id)
// Uses a lightweight SQLite DB via sqlite and bcrypt for password hashing.

const express = require('express');
const bcrypt = require('bcrypt');
const path = require('path');
const sqlite3 = require('sqlite3');
const { open } = require('sqlite');

const router = express.Router();

// Environment-based DB path
const DB_PATH = process.env.SCRATCH_DB_PATH || path.join(__dirname, '../../../../scratch/shared/data/users.db');

let dbPromise = null;
async function getDb() {
  if (dbPromise) return dbPromise;
  // Ensure directory exists
  const fs = require('fs');
  const dir = path.dirname(DB_PATH);
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
  // Use sqlite with promises via sqlite package
  const db = await open({ filename: DB_PATH, driver: sqlite3.Database });
  // Initialize table if not exists
  await db.exec(`CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TEXT DEFAULT (datetime('now','localtime'))
  );`);
  dbPromise = db;
  return dbPromise;
}

// Helper: map user row to response (omit password_hash)
function mapUser(row) {
  if (!row) return null;
  const { id, name, email, created_at } = row;
  return { id, name, email, created_at };
}

// GET / - list users
router.get('/', async (req, res) => {
  try {
    const db = await getDb();
    const rows = await db.all('SELECT id, name, email, created_at FROM users');
    res.json(rows.map(row => mapUser(row)));
  } catch (err) {
    console.error('GET /users error:', err);
    res.status(500).json({ error: 'Internal Server Error' });
  }
});

// POST / - create user
router.post('/', async (req, res) => {
  try {
    const { name, email, password } = req.body || {};
    if (!name || typeof name !== 'string' || name.trim().length === 0) {
      return res.status(400).json({ error: 'Invalid or missing name' });
    }
    if (!email || typeof email !== 'string' || !/^([^\\s@]+)@([^\\s@]+)\\.[^\\s@]+$/.test(email)) {
      return res.status(400).json({ error: 'Invalid or missing email' });
    }
    if (!password || typeof password !== 'string' || password.length < 6) {
      return res.status(400).json({ error: 'Invalid or missing password' });
    }

    // Hash password
    const hash = await bcrypt.hash(password, 10);
    const db = await getDb();
    const created_at = new Date().toISOString();

    const result = await db.run(
      'INSERT INTO users (name, email, password_hash, created_at) VALUES (?, ?, ?, ?)',
      [name.trim(), email.trim(), hash, created_at]
    );
    const id = result.lastID;
    res.status(201).json({ id, name: name.trim(), email: email.trim(), created_at });
  } catch (err) {
    console.error('POST /users error:', err);
    if (err && (err.code === 'SQLITE_CONSTRAINT' || (err.message && err.message.toLowerCase().includes('unique')))) {
      return res.status(409).json({ error: 'User with this email already exists' });
    }
    res.status(500).json({ error: 'Internal Server Error' });
  }
});

// GET /:id - get user by id
router.get('/:id', async (req, res) => {
  try {
    const id = parseInt(req.params.id, 10);
    if (Number.isNaN(id)) {
      return res.status(400).json({ error: 'Invalid user id' });
    }
    const db = await getDb();
    const row = await db.get('SELECT id, name, email, created_at FROM users WHERE id = ?', id);
    if (!row) {
      return res.status(404).json({ error: 'User not found' });
    }
    res.json(mapUser(row));
  } catch (err) {
    console.error('GET /users/:id error:', err);
    res.status(500).json({ error: 'Internal Server Error' });
  }
});

module.exports = router;
