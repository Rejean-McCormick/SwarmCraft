"use strict";

const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
const path = require('path');
const fs = require('fs').promises;

let db;

// Resolve the on-disk database path.
// Priority: SCRATCH_DB_PATH env var > default scratch/shared/data/users.db
function resolveDbPath() {
  const envPath = process.env.SCRATCH_DB_PATH;
  if (envPath && envPath.trim()) {
    // Absolute path provided
    if (path.isAbsolute(envPath)) {
      return envPath;
    }
    // Relative path provided; resolve relative to scratch/shared
    return path.resolve(__dirname, '..', envPath);
  }
  // Default to scratch/shared/data/users.db
  return path.resolve(__dirname, '../data/users.db');
}

async function ensureDirForDb(dbPath) {
  const dir = path.dirname(dbPath);
  try {
    await fs.mkdir(dir, { recursive: true });
  } catch (e) {
    // ignore if already exists or cannot create (will throw later on actual DB ops)
  }
}

async function initDb() {
  const dbPath = resolveDbPath();
  await ensureDirForDb(dbPath);

  db = await open({ filename: dbPath, driver: sqlite3.Database });

  await db.exec(`CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    created_at TEXT DEFAULT (datetime('now','localtime'))
  );`);
}

async function getAllUsers(limit = 100, offset = 0) {
  const rows = await db.all('SELECT id, name, email, created_at FROM users ORDER BY id LIMIT ? OFFSET ?', limit, offset);
  return rows;
}

async function getUserById(id) {
  const row = await db.get('SELECT id, name, email, created_at FROM users WHERE id = ?', id);
  return row;
}

async function createUser(name, email) {
  const res = await db.run('INSERT INTO users (name, email) VALUES (?, ?)', name, email);
  // sqlite returns lastID
  const id = res.lastID;
  return getUserById(id);
}

module.exports = { initDb, getAllUsers, getUserById, createUser };
