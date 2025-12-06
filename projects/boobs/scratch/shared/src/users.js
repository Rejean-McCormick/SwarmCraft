/**
 * SQLite-backed Users API module
 * - Exposes DB helpers: initDb, createUser, getUsers, getUser
 * - Exposes Express router via createRouter(db) for integration
 * 
 * Notes:
 * - Passwords are hashed with bcrypt if available; otherwise stored as plaintext (fallback).
 * - Basic input validation included for API safety.
 */

let bcryptAvailable = false;
let bcryptHash = null;
try {
  // Try to load bcrypt; if unavailable, fall back gracefully
  // eslint-disable-next-line import/no-extraneous-dependencies
  const bcrypt = require('bcrypt');
  bcryptAvailable = true;
  const SALT_ROUNDS = 10;
  bcryptHash = async (pw) => bcrypt.hash(pw, SALT_ROUNDS);
} catch (e) {
  bcryptAvailable = false;
  bcryptHash = async (pw) => pw; // fallback: store plaintext
}

const sqlite3 = require('sqlite3');

// Simple ValidationError for controlled failures in DB/API layer
class ValidationError extends Error {
  constructor(errors) {
    super('Validation error');
    this.name = 'ValidationError';
    this.errors = errors;
    this.status = 400;
  }
}

// Initialize database and ensure table exists
async function initDb(dbPath) {
  return new Promise((resolve, reject) => {
    const db = new sqlite3.Database(dbPath, (err) => {
      if (err) return reject(err);
      // Create table if not exists
      const createTableSql = `
        CREATE TABLE IF NOT EXISTS users (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          name TEXT NOT NULL,
          email TEXT NOT NULL UNIQUE,
          password_hash TEXT NOT NULL,
          created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
      `;
      db.run(createTableSql, (err) => {
        if (err) return reject(err);
        resolve(db);
      });
    });
  });
}

// Promisified helpers for sqlite3
function promisifyDb(db) {
  return {
    all: (sql, params = []) => new Promise((resolve, reject) => {
      db.all(sql, params, (err, rows) => (err ? reject(err) : resolve(rows)));
    }),
    get: (sql, params = []) => new Promise((resolve, reject) => {
      db.get(sql, params, (err, row) => (err ? reject(err) : resolve(row)));
    }),
    run: (sql, params = []) => new Promise((resolve, reject) => {
      db.run(sql, params, function(err) {
        if (err) return reject(err);
        // this.lastID is available for INSERT
        resolve(this);
      });
    }),
  };
}

async function _validateInput({ name, email, password }) {
  const errors = [];
  if (typeof name !== 'string' || name.trim() === '') {
    errors.push({ field: 'name', message: 'Name is required' });
  }
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (typeof email !== 'string' || !emailRegex.test(email)) {
    errors.push({ field: 'email', message: 'Valid email is required' });
  }
  if (typeof password !== 'string' || password.length < 6) {
    errors.push({ field: 'password', message: 'Password must be at least 6 characters' });
  }
  return errors;
}

async function createUser(db, { name, email, password }) {
  const errors = await _validateInput({ name, email, password });
  if (errors.length) {
    throw new ValidationError(errors);
  }
  const store = promisifyDb(db);
  const hashed = await bcryptHash(password);
  try {
    const result = await store.run(
      'INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)',
      [name.trim(), email.trim(), hashed]
    );
    const newId = result.lastID;
    const row = await store.get('SELECT id, name, email, created_at FROM users WHERE id = ?', [newId]);
    return row;
  } catch (err) {
    // Unique constraint on email
    if (err && (err.code === 'SQLITE_CONSTRAINT' || (err.message || '').includes('UNIQUE'))) {
      const error = new Error('Email already exists');
      error.status = 409;
      throw error;
    }
    throw err;
  }
}

async function getUsers(db) {
  const store = promisifyDb(db);
  const rows = await store.all('SELECT id, name, email, created_at FROM users ORDER BY created_at DESC');
  return rows;
}

async function getUser(db, id) {
  const store = promisifyDb(db);
  const row = await store.get('SELECT id, name, email, created_at FROM users WHERE id = ?', [id]);
  return row;
}

// Express router for API endpoints
function createRouter(db) {
  const express = require('express');
  const router = express.Router();
  router.use(express.json());

  // GET /users
  router.get('/users', async (req, res) => {
    try {
      const users = await getUsers(db);
      res.json(users);
    } catch (err) {
      console.error(err);
      res.status(500).json({ error: 'Internal server error' });
    }
  });

  // GET /users/:id
  router.get('/users/:id', async (req, res) => {
    const id = parseInt(req.params.id, 10);
    if (Number.isNaN(id)) {
      return res.status(400).json({ error: 'Invalid id' });
    }
    try {
      const user = await getUser(db, id);
      if (!user) return res.status(404).json({ error: 'User not found' });
      res.json(user);
    } catch (err) {
      console.error(err);
      res.status(500).json({ error: 'Internal server error' });
    }
  });

  // POST /users
  router.post('/users', async (req, res) => {
    const { name, email, password } = req.body || {};
    try {
      const created = await createUser(db, { name, email, password });
      // Expose only non-sensitive fields
      const { id, name: uname, email: uemail, created_at } = created;
      res.status(201).json({ id, name: uname, email: uemail, created_at });
    } catch (err) {
      if (err instanceof ValidationError) {
        return res.status(400).json({ errors: err.errors });
      }
      if (err.status === 409) {
        return res.status(409).json({ error: 'Email already exists' });
      }
      console.error(err);
      res.status(500).json({ error: 'Internal server error' });
    }
  });

  return router;
}

module.exports = {
  initDb,
  createUser,
  getUsers,
  getUser,
  createRouter,
  ValidationError
};
