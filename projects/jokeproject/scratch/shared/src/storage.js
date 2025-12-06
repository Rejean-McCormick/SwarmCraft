"use strict";
const sqlite3 = require('sqlite3').verbose();
const crypto = require('crypto');

// SQLite-backed JokeStore with content-hash dedupe
class JokeStore {
  constructor(dbPath) {
    this.dbPath = dbPath || ':memory:';
    this.db = null;
    this.useDb = false;
  }

  async init() {
    return new Promise((resolve, reject) => {
      // Open DB
      const db = new sqlite3.Database(this.dbPath, (err) => {
        if (err) {
          this.useDb = false;
          return reject(err);
        }
        this.db = db;
        // Ensure table exists
        const createSql = `CREATE TABLE IF NOT EXISTS jokes (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          setup TEXT NOT NULL,
          punchline TEXT NOT NULL,
          category TEXT,
          author TEXT,
          created_at TEXT,
          hash TEXT UNIQUE
        )`;
        this.db.run(createSql, [], (err2) => {
          if (err2) {
            this.useDb = false;
            return reject(err2);
          }
          this.useDb = true;
          resolve();
        });
      });
    });
  }

  getJokes(limit) {
    return new Promise((resolve, reject) => {
      if (!this.useDb) return reject(new Error('DB not initialized'));
      const q = `SELECT id, setup, punchline, category, author, created_at FROM jokes ORDER BY id DESC LIMIT ?`;
      this.db.all(q, [limit], (err, rows) => {
        if (err) return reject(err);
        resolve(rows);
      });
    });
  }

  addJoke(setup, punchline, category, author) {
    return new Promise((resolve, reject) => {
      if (!this.useDb) return reject(new Error('DB not initialized'));
      const hash = crypto.createHash('sha256').update((setup || '') + '|' + (punchline || '')).digest('hex');
      const created_at = new Date().toISOString();
      const sql = `INSERT INTO jokes (setup, punchline, category, author, created_at, hash) VALUES (?, ?, ?, ?, ?, ?)`;
      // Use 'self' to access lastID in callback
      const self = this;
      this.db.run(sql, [setup, punchline, category, author, created_at, hash], function(err) {
        if (err) {
          // If unique constraint on hash violated, fetch existing row
          if (err && (err.code === 'SQLITE_CONSTRAINT' || err.message.includes('UNIQUE'))) {
            self.db.get(`SELECT id, created_at FROM jokes WHERE hash = ? LIMIT 1`, [hash], (err2, row) => {
              if (err2) return reject(err2);
              resolve({ id: row ? row.id : null, created_at: row ? row.created_at : created_at, existing: true });
            });
          } else {
            reject(err);
          }
        } else {
          const id = this.lastID;
          resolve({ id, created_at, existing: false });
        }
      });
    });
  }

  close() {
    if (this.db) {
      this.db.close();
      this.db = null;
      this.useDb = false;
    }
  }
}

function hashContent(content) {
  return crypto.createHash('sha256').update(content || '').digest('hex');
}

module.exports = { JokeStore, hashContent };
