"use strict";
const sqlite3 = require('sqlite3').verbose();
const path = require('path');

// Allow overriding DB path for tests and environments
const DB_PATH = process.env.DB_PATH || path.resolve(__dirname, 'app.db');

let dbInstance = null;

function openDb() {
  return new Promise((resolve, reject) => {
    if (dbInstance) return resolve(dbInstance);
    const db = new sqlite3.Database(DB_PATH, (err) => {
      if (err) return reject(err);
      dbInstance = db;
      resolve(dbInstance);
    });
  });
}

function run(db, sql, params = []) {
  return new Promise((resolve, reject) => {
    db.run(sql, params, function (err) {
      if (err) return reject(err);
      resolve(this);
    });
  });
}

function get(db, sql, params = []) {
  return new Promise((resolve, reject) => {
    db.get(sql, params, (err, row) => {
      if (err) return reject(err);
      resolve(row);
    });
  });
}

function all(db, sql, params = []) {
  return new Promise((resolve, reject) => {
    db.all(sql, params, (err, rows) => {
      if (err) return reject(err);
      resolve(rows);
    });
  });
}

async function initDb() {
  const db = await openDb();
  // Ensure schema
  await run(db, `CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TEXT
  )`);
  await run(db, `CREATE TABLE IF NOT EXISTS wallets (
    user_id TEXT PRIMARY KEY,
    balance INTEGER NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(id)
  )`);
  await run(db, `CREATE TABLE IF NOT EXISTS items (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    price INTEGER NOT NULL,
    stock INTEGER NOT NULL
  )`);
  await run(db, `CREATE TABLE IF NOT EXISTS inventories (
    user_id TEXT,
    item_id INTEGER,
    quantity INTEGER,
    PRIMARY KEY (user_id, item_id)
  )`);
  await run(db, `CREATE TABLE IF NOT EXISTS sessions (
    session_id TEXT PRIMARY KEY,
    type TEXT,
    user_id TEXT,
    bet INTEGER,
    state TEXT,
    data TEXT,
    created_at TEXT,
    updated_at TEXT
  )`);

  // Seed shop items if empty
  const count = await get(db, 'SELECT COUNT(*) AS c FROM items', []);
  if (!count || count.c === 0) {
    await run(db, 'INSERT INTO items (name, price, stock) VALUES (?, ?, ?)', ['Bronze Sword', 100, 10]);
    await run(db, 'INSERT INTO items (name, price, stock) VALUES (?, ?, ?)', ['Silver Shield', 250, 5]);
    await run(db, 'INSERT INTO items (name, price, stock) VALUES (?, ?, ?)', ['Health Potion', 50, 50]);
  }

  // Ensure admin seed user optional
  return db;
}

// Convenience to close and reset for tests
async function closeDb() {
  if (dbInstance) {
    return new Promise((resolve, reject) => {
      dbInstance.close((err) => {
        if (err) return reject(err);
        dbInstance = null;
        resolve();
      });
    });
  }
}

module.exports = { initDb, run, get, all, closeDb };
