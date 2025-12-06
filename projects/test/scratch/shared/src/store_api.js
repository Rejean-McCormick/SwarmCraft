// Store API - Node.js/Express using better-sqlite3 (synchronous DB access)
// Endpoints (relative to base mount /api/store):
// - GET /            -> store metadata
// - GET /products          -> list products
// - GET /products/:id      -> get product by id
// - POST /products         -> create product
// - PUT /products/:id      -> update product
// - DELETE /products/:id    -> delete product
// - GET /promotions        -> list promotions
// - GET /promotions/:id    -> get promotion by id
// - POST /promotions       -> create promotion
// - PUT /promotions/:id    -> update promotion
// - DELETE /promotions/:id  -> delete promotion
// This is wired into an Express app router in scratch/shared/src/app.js

const express = require('express');
const Database = require('better-sqlite3');
const path = require('path');

const router = express.Router();
const DB_PATH = process.env.DB_PATH || path.resolve(__dirname, '..', 'db.sqlite');
let db;
try {
  db = new Database(DB_PATH, { verbose: null });
} catch (e) {
  // Fall back to an in-session error; handle gracefully in routes
  db = null;
}

function ensureDb() {
  if (!db) {
    // Attempt to reopen
    try { db = new Database(DB_PATH, { verbose: null }); } catch (e) { db = null; }
  }
  return !!db;
}

function toErr(res, code, message) {
  return res.status(code).json({ ok: false, error: message });
}

// Store metadata
router.get('/', async (req, res) => {
  try {
    const store = { name: 'Mock Store', description: 'Goofy mock store' };
    res.json({ ok: true, store });
  } catch (e) {
    toErr(res, 500, 'internal_error');
  }
});

// List products
router.get('/products', (req, res) => {
  if (!ensureDb()) { return toErr(res, 500, 'db_error'); }
  try {
    const limitRaw = req.query.limit;
    const offsetRaw = req.query.offset;
    let limit = parseInt(limitRaw, 10);
    let offset = parseInt(offsetRaw, 10);
    if (Number.isNaN(limit)) limit = 25;
    if (Number.isNaN(offset)) offset = 0;
    if (limit < 1) limit = 25;
    const stmt = db.prepare('SELECT id, name, price, stock, description FROM products LIMIT ? OFFSET ?');
    const rows = stmt.all(limit, offset);
    res.json({ ok: true, products: rows });
  } catch (e) {
    toErr(res, 500, 'db_error');
  }
});

// Get product by id
router.get('/products/:id', (req, res) => {
  const id = parseInt(req.params.id, 10);
  if (!ensureDb()) { return toErr(res, 500, 'db_error'); }
  if (Number.isNaN(id)) { return toErr(res, 400, 'validation'); }
  try {
    const stmt = db.prepare('SELECT id, name, description, price, stock FROM products WHERE id = ?');
    const row = stmt.get(id);
    if (!row) return res.status(404).json({ ok: false, error: 'not_found' });
    res.json({ ok: true, product: row });
  } catch (e) {
    toErr(res, 500, 'db_error');
  }
});

// Create product
router.post('/products', (req, res) => {
  const { name, price, stock, description } = req.body || {};
  if (!name || price == null) {
    return toErr(res, 400, 'validation');
  }
  if (!ensureDb()) { return toErr(res, 500, 'db_error'); }
  try {
    const stmt = db.prepare('INSERT INTO products (name, price, stock, description) VALUES (?, ?, ?, ?)');
    const info = stmt.run(name, price, stock || 0, description || '');
    res.status(201).json({ ok: true, insertedId: info.lastInsertRowid });
  } catch (e) {
    toErr(res, 500, 'db_error');
  }
});

// Update product
router.put('/products/:id', (req, res) => {
  const id = parseInt(req.params.id, 10);
  const { name, price, stock, description } = req.body || {};
  if (Number.isNaN(id)) return toErr(res, 400, 'validation');
  if (!ensureDb()) { return toErr(res, 500, 'db_error'); }
  try {
    const fields = [];
    const vals = [];
    if (name != null) { fields.push('name = ?'); vals.push(name); }
    if (price != null) { fields.push('price = ?'); vals.push(price); }
    if (stock != null) { fields.push('stock = ?'); vals.push(stock); }
    if (description != null) { fields.push('description = ?'); vals.push(description); }
    if (fields.length === 0) return toErr(res, 400, 'validation');
    vals.push(id);
    const sql = `UPDATE products SET ${fields.join(', ')} WHERE id = ?`;
    const stmt = db.prepare(sql);
    const info = stmt.run(...vals);
    if (info.changes === 0) return res.status(404).json({ ok: false, error: 'not_found' });
    res.json({ ok: true, updated: id });
  } catch (e) {
    toErr(res, 500, 'db_error');
  }
});

// Delete product
router.delete('/products/:id', (req, res) => {
  const id = parseInt(req.params.id, 10);
  if (Number.isNaN(id)) return toErr(res, 400, 'validation');
  if (!ensureDb()) { return toErr(res, 500, 'db_error'); }
  try {
    const stmt = db.prepare('DELETE FROM products WHERE id = ?');
    const info = stmt.run(id);
    if (info.changes === 0) return res.status(404).json({ ok: false, error: 'not_found' });
    res.json({ ok: true, deleted: id });
  } catch (e) {
    toErr(res, 500, 'db_error');
  }
});

// List promotions
router.get('/promotions', (req, res) => {
  if (!ensureDb()) { return toErr(res, 500, 'db_error'); }
  try {
    const limitRaw = req.query.limit;
    const offsetRaw = req.query.offset;
    let limit = parseInt(limitRaw, 10);
    let offset = parseInt(offsetRaw, 10);
    if (Number.isNaN(limit)) limit = 25;
    if (Number.isNaN(offset)) offset = 0;
    if (limit < 1) limit = 25;
    const stmt = db.prepare('SELECT id, code, description, discount, active FROM promotions LIMIT ? OFFSET ?');
    const rows = stmt.all(limit, offset);
    res.json({ ok: true, promotions: rows });
  } catch (e) {
    toErr(res, 500, 'db_error');
  }
});

// Get promotion by id
router.get('/promotions/:id', (req, res) => {
  const id = parseInt(req.params.id, 10);
  if (Number.isNaN(id)) return toErr(res, 400, 'validation');
  if (!ensureDb()) { return toErr(res, 500, 'db_error'); }
  try {
    const stmt = db.prepare('SELECT id, code, description, discount, active FROM promotions WHERE id = ?');
    const row = stmt.get(id);
    if (!row) return res.status(404).json({ ok: false, error: 'not_found' });
    res.json({ ok: true, promotion: row });
  } catch (e) {
    toErr(res, 500, 'db_error');
  }
});

// Create promotion
router.post('/promotions', (req, res) => {
  const { code, description, discount, active } = req.body || {};
  if (!code || discount == null) return toErr(res, 400, 'validation');
  if (!ensureDb()) { return toErr(res, 500, 'db_error'); }
  try {
    const stmt = db.prepare('INSERT INTO promotions (code, description, discount, active) VALUES (?, ?, ?, ?)');
    const info = stmt.run(code, description || '', discount, (active != null ? active : 1));
    res.status(201).json({ ok: true, insertedId: info.lastInsertRowid });
  } catch (e) {
    // If code unique constraint fails, return 400 with validation-like error
    toErr(res, 500, 'db_error');
  }
});

// Update promotion
router.put('/promotions/:id', (req, res) => {
  const id = parseInt(req.params.id, 10);
  const { code, description, discount, active } = req.body || {};
  if (Number.isNaN(id)) return toErr(res, 400, 'validation');
  if (!ensureDb()) { return toErr(res, 500, 'db_error'); }
  try {
    const fields = [];
    const vals = [];
    if (code != null) { fields.push('code = ?'); vals.push(code); }
    if (description != null) { fields.push('description = ?'); vals.push(description); }
    if (discount != null) { fields.push('discount = ?'); vals.push(discount); }
    if (active != null) { fields.push('active = ?'); vals.push(active); }
    if (fields.length === 0) return toErr(res, 400, 'validation');
    vals.push(id);
    const sql = `UPDATE promotions SET ${fields.join(', ')} WHERE id = ?`;
    const stmt = db.prepare(sql);
    const info = stmt.run(...vals);
    if (info.changes === 0) return res.status(404).json({ ok: false, error: 'not_found' });
    res.json({ ok: true, updated: id });
  } catch (e) {
    toErr(res, 500, 'db_error');
  }
});

// Delete promotion
router.delete('/promotions/:id', (req, res) => {
  const id = parseInt(req.params.id, 10);
  if (Number.isNaN(id)) return toErr(res, 400, 'validation');
  if (!ensureDb()) { return toErr(res, 500, 'db_error'); }
  try {
    const stmt = db.prepare('DELETE FROM promotions WHERE id = ?');
    const info = stmt.run(id);
    if (info.changes === 0) return res.status(404).json({ ok: false, error: 'not_found' });
    res.json({ ok: true, deleted: id });
  } catch (e) {
    toErr(res, 500, 'db_error');
  }
});

module.exports = router;
