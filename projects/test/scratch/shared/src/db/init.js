// Simple DB init for local MVP
const sqlite3 = require('sqlite3').verbose();
const db = new sqlite3.Database('./db.sqlite3');

const seed = async () => {
  // Create tables if not exists (redundant with schema, but ensure)
  await new Promise(resolve => db.run(`CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    price REAL NOT NULL,
    description TEXT,
    stock INTEGER NOT NULL DEFAULT 0
  )`, (err)=>{ if(err) console.error(err); resolve(); }));
  await new Promise(resolve => db.run(`CREATE TABLE IF NOT EXISTS promotions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT UNIQUE NOT NULL,
    discount REAL NOT NULL,
    description TEXT
  )`, (err)=>{ if(err) console.error(err); resolve(); }));
  await new Promise(resolve => db.run(`CREATE TABLE IF NOT EXISTS invoices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    total REAL NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
  )`, (err)=>{ if(err) console.error(err); resolve(); }));
  await new Promise(resolve => db.run(`CREATE TABLE IF NOT EXISTS invoice_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    qty INTEGER NOT NULL,
    price REAL NOT NULL
  )`, (err)=>{ if(err) console.error(err); resolve(); }));

  // Seed a few products
  await new Promise(resolve => {
    db.run("INSERT INTO products (name, price, description, stock) VALUES ('Goofy Mug', 9.99, 'Humorous mug', 50)", ()=>{ resolve(); });
  });
  await new Promise(resolve => {
    db.run("INSERT INTO products (name, price, description, stock) VALUES ('Jest T-Shirt', 19.99, 'Funny t-shirt', 20)", ()=>{ resolve(); });
  });
};

seed().then(() => {
  console.log('DB seed complete');
}).catch(err => {
  console.error('DB seed error', err);
});

module.exports = db;
