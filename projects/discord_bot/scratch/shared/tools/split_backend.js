#!/usr/bin/env node
/**
 * Split the monolithic backend into modular services: auth, wallet, shop, games.
 * Generates standalone service folders under scratch/shared/services/{service} with a server.js and package.json.
 * Each service uses its own sqlite database and exposes a minimal API surface.
 */

const fs = require('fs');
const path = require('path');

function ensureDir(p) {
  fs.mkdirSync(p, { recursive: true });
}

function writeFile(p, content) {
  ensureDir(path.dirname(p));
  fs.writeFileSync(p, content, 'utf8');
}

function fileExists(p) {
  try { return fs.statSync(p).isFile(); } catch (e) { return false; }
}

function serviceServerAuth() {
  return `"use strict";
const express = require('express');
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const sqlite3 = require('sqlite3').verbose();
const path = require('path');
const { v4: uuidv4 } = require('uuid');

const app = express();
app.use(express.json());

const PORT = 3000; // auth
const DB_DIR = path.resolve(__dirname, 'db');
const DB_PATH = path.resolve(DB_DIR, 'app.db');
const JWT_SECRET = process.env.JWT_SECRET || 'change-me';
const TOKEN_EXPIRY = '7d';

function openDb() {
  const db = new sqlite3.Database(DB_PATH, (err) => {
    if (err) throw err;
  });
  return db;
}

function initDb(db) {
  return new Promise((resolve, reject) => {
    db.run(
      `CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        created_at TEXT
      )`,
      (err) => {
        if (err) return reject(err);
        db.run(
          `CREATE TABLE IF NOT EXISTS wallets (
            user_id TEXT PRIMARY KEY,
            balance INTEGER NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
          )`,
          (err2) => {
            if (err2) return reject(err2);
            resolve();
          }
        );
      }
    );
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

app.post('/register', async (req, res) => {
  const { username, password } = req.body || {};
  if (!username || !password) return res.status(400).json({ error: 'username and password required' });
  const db = openDb();
  try {
    await initDb(db);
    const hash = await bcrypt.hash(password, 10);
    const id = uuidv4();
    await new Promise((resolve, reject) => {
      db.run('INSERT INTO users (id, username, password_hash, created_at) VALUES (?, ?, ?, datetime("now"))', [id, username, hash], function(err){
        if (err) return reject(err);
        resolve();
      });
    });
    await new Promise((resolve, reject) => {
      db.run('INSERT INTO wallets (user_id, balance) VALUES (?, ?)', [id, 0], function(err){
        if (err) return reject(err);
        resolve();
      });
    });
    res.json({ id, username });
  } catch (e) {
    res.status(500).json({ error: 'register failed', detail: e.message });
  } finally {
    db.close();
  }
});

app.post('/login', async (req, res) => {
  const { username, password } = req.body || {};
  if (!username || !password) return res.status(400).json({ error: 'username and password required' });
  const db = openDb();
  try {
    await initDb(db);
    const user = await get(db, 'SELECT * FROM users WHERE username = ?', [username]);
    if (!user) return res.status(401).json({ error: 'invalid credentials' });
    const ok = await new Promise((resolve) => {
      bcrypt.compare(password, user.password_hash, (err, res) => resolve(res));
    });
    if (!ok) return res.status(401).json({ error: 'invalid credentials' });
    const token = jwt.sign({ id: user.id, username: user.username }, JWT_SECRET, { expiresIn: TOKEN_EXPIRY });
    res.json({ token, user: { id: user.id, username: user.username } });
  } catch (e) {
    res.status(500).json({ error: 'login failed', detail: e.message });
  } finally {
    db.close();
  }
});

app.listen(PORT, () => console.log('auth service listening on', PORT));
`;
}

function serviceServerWallet() {
  return `"use strict";
const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const path = require('path');
const app = express();
app.use(express.json());
const PORT = 3001; // wallet
const DB_PATH = path.resolve(__dirname, 'db', 'app.db');

function openDb() {
  const db = new sqlite3.Database(DB_PATH, (err) => {
    if (err) throw err;
  });
  return db;
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

app.get('/balance', async (req, res) => {
  const userId = req.headers['x-user-id'];
  if (!userId) return res.status(400).json({ error: 'x-user-id header required' });
  const db = openDb();
  try {
    await new Promise((resolve, reject) => {
      db.get('SELECT balance FROM wallets WHERE user_id = ?', [userId], (err, row) => {
        if (err) return reject(err);
        res.json({ balance: row ? row.balance : 0 });
        resolve();
      });
    });
  } catch (e) {
    res.status(500).json({ error: e.message });
  } finally {
    db.close();
  }
});

app.post('/deposit', async (req, res) => {
  const userId = req.headers['x-user-id'];
  const amount = Number(req.body.amount);
  if (!userId) return res.status(400).json({ error: 'x-user-id header required' });
  if (!amount || amount <= 0) return res.status(400).json({ error: 'invalid amount' });
  const db = openDb();
  try {
    await new Promise((resolve, reject) => {
      db.run('UPDATE wallets SET balance = coalesce(balance, 0) + ? WHERE user_id = ?', [amount, userId], function(err){
        if (err) return reject(err);
        resolve();
      });
    });
    const row = await get(db, 'SELECT balance FROM wallets WHERE user_id = ?', [userId]);
    res.json({ balance: row ? row.balance : amount });
  } catch (e) {
    res.status(500).json({ error: e.message });
  } finally {
    db.close();
  }
});

app.listen(PORT, () => console.log('wallet service listening on', PORT));
`;
}

function serviceServerShop() {
  return `"use strict";
const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const path = require('path');
const app = express();
app.use(express.json());
const PORT = 3002; // shop
const DB_PATH = path.resolve(__dirname, 'db', 'app.db');

function openDb() {
  const db = new sqlite3.Database(DB_PATH, (err) => {
    if (err) throw err;
  });
  return db;
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

app.get('/items', async (req, res) => {
  const db = openDb();
  try {
    db.all('SELECT * FROM items', [], (err, rows) => {
      if (err) return res.status(500).json({ error: err.message });
      res.json(rows);
    });
  } catch (e) {
    res.status(500).json({ error: e.message });
  } finally {
    // db.close(); // keep alive
  }
});

app.post('/buy', async (req, res) => {
  const userId = req.headers['x-user-id'];
  const { itemId, quantity } = req.body || {};
  const qty = quantity || 1;
  if (!userId) return res.status(400).json({ error: 'x-user-id header required' });
  const db = openDb();
  try {
    const item = await new Promise((resolve, reject) => {
      db.get('SELECT * FROM items WHERE id = ?', [itemId], (err, row) => {
        if (err) return reject(err);
        resolve(row);
      });
    });
    if (!item) return res.status(404).json({ error: 'item not found' });
    const total = item.price * qty;
    // Deduct from wallet
    const walletDb = openDb();
    await new Promise((resolve, reject) => {
      walletDb.run('UPDATE wallets SET balance = balance - ? WHERE user_id = ?', [total, userId], function(err){
        if (err) return reject(err);
        resolve();
      });
    });
    // Update stock and inventories (simplified)
    await run(db, 'UPDATE items SET stock = stock - ? WHERE id = ?', [qty, itemId]);
    const existing = await new Promise((resolve, reject) => {
      db.get('SELECT quantity FROM inventories WHERE user_id = ? AND item_id = ?', [userId, itemId], (err, row) => {
        if (err) return reject(err);
        resolve(row);
      });
    });
    if (existing) {
      await run(db, 'UPDATE inventories SET quantity = quantity + ? WHERE user_id = ? AND item_id = ?', [qty, userId, itemId]);
    } else {
      await run(db, 'INSERT INTO inventories (user_id, item_id, quantity) VALUES (?, ?, ?)', [userId, itemId, qty]);
    }
    res.json({ itemId, quantity: qty, total });
  } catch (e) {
    res.status(500).json({ error: e.message });
  } finally {
    db.close();
  }
});

function ensureInitDb(db) {
  return new Promise((resolve) => {
    db.serialize(() => {
      db.run('CREATE TABLE IF NOT EXISTS items (id INTEGER PRIMARY KEY, name TEXT, price INTEGER, stock INTEGER)', () => {
        db.run('CREATE TABLE IF NOT EXISTS wallets (user_id TEXT PRIMARY KEY, balance INTEGER)');
        db.run('CREATE TABLE IF NOT EXISTS inventories (user_id TEXT, item_id INTEGER, quantity INTEGER, PRIMARY KEY (user_id, item_id))');
        // Seed if empty
        db.get('SELECT COUNT(*) AS c FROM items', [], (err, row) => {
          if (err || !row || row.c === 0) {
            db.run('INSERT INTO items (name, price, stock) VALUES (?, ?, ?)', ['Bronze Sword', 100, 10]);
            db.run('INSERT INTO items (name, price, stock) VALUES (?, ?, ?)', ['Health Potion', 50, 50]);
          }
          resolve();
        });
      });
    });
  });
}

const mainDb = openDb();
ensureInitDb(mainDb).then(() => {
  mainDb.close();
});

app.listen(PORT, () => console.log('shop service listening on', PORT));
`;
}

function serviceServerGames() {
  return `"use strict";
const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const path = require('path');
const { v4: uuidv4 } = require('uuid');
const app = express();
app.use(express.json());
const PORT = 3003; // games
const DB_PATH = path.resolve(__dirname, 'db', 'app.db');

function openDb() {
  const db = new sqlite3.Database(DB_PATH, (err) => {
    if (err) throw err;
  });
  return db;
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

app.post('/blackjack/start', async (req, res) => {
  const userId = req.headers['x-user-id'];
  if (!userId) return res.status(400).json({ error: 'x-user-id header required' });
  const db = openDb();
  try {
    await new Promise((resolve, reject) => {
      db.run('INSERT INTO sessions (session_id, type, user_id, state, data, created_at, updated_at) VALUES (?, ?, ?, ?, ?, datetime("now"), datetime("now"))', [uuidv4(), 'blackjack', userId, 'new', JSON.stringify({ hand: [], deck: [] })], function(err){
        if (err) return reject(err);
        resolve();
      });
    });
    res.json({ sessionId: uuidv4() });
  } catch (e) {
    res.status(500).json({ error: e.message });
  } finally {
    db.close();
  }
});

app.post('/blackjack/join', async (req, res) => {
  const { sessionId } = req.body || {};
  const userId = req.headers['x-user-id'];
  if (!sessionId || !userId) return res.status(400).json({ error: 'sessionId and x-user-id required' });
  // simplistic join: mark a row
  const db = openDb();
  try {
    await run(db, 'UPDATE sessions SET user_id = ?, updated_at = datetime("now") WHERE session_id = ?', [userId, sessionId]);
    res.json({ joined: true });
  } catch (e) {
    res.status(500).json({ error: e.message });
  } finally {
    db.close();
  }
});

app.get('/blackjack/state/:sessionId', async (req, res) => {
  const sessionId = req.params.sessionId;
  const db = openDb();
  try {
    const row = await get(db, 'SELECT data FROM sessions WHERE session_id = ?', [sessionId]);
    res.json(row ? JSON.parse(row.data) : null);
  } catch (e) {
    res.status(500).json({ error: e.message });
  } finally {
    db.close();
  }
});

app.listen(PORT, () => console.log('games service listening on', PORT));
`;
}

function createService(name, code) {
  const dir = path.resolve(__dirname, '..', 'services', name);
  ensureDir(dir);
  const serverPath = path.resolve(dir, 'server.js');
  const packagePath = path.resolve(dir, 'package.json');
  const dbDir = path.resolve(dir, 'db');
  ensureDir(dbDir);
  const codeWrapper = code;
  writeFile(serverPath, codeWrapper);
  const pkg = {
    name: `${name}-service`,
    version: '1.0.0',
    main: 'server.js',
    scripts: {
      start: 'node server.js'
    },
    dependencies: {
      express: '^4.17.3',
      sqlite3: '^5.1.6',
      bcrypt: '^5.0.1',
      jsonwebtoken: '^9.0.0',
      uuid: '^9.0.0'
    }
  };
  writeFile(packagePath, JSON.stringify(pkg, null, 2));
}

function generateAll() {
  // Auth service
  createService('auth', serviceServerAuth());
  // Wallet service
  createService('wallet', serviceServerWallet());
  // Shop service
  createService('shop', serviceServerShop());
  // Games service
  createService('games', serviceServerGames());
}

function main() {
  const generate = process.argv.includes('--generate');
  if (!generate) {
    console.log('Usage: node split_backend.js --generate');
    process.exit(0);
  }
  // Remove existing services if any? We'll skip to avoid data loss; just create/overwrite server.js and package.json
  generateAll();
  console.log('Split complete: generated services/auth, services/wallet, services/shop, services/games');
}

main();
