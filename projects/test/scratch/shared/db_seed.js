// Seed script for SQLite DB at scratch/shared/db.sqlite
const sqlite3 = require('sqlite3').verbose();
const path = require('path');
const DB_PATH = path.resolve(__dirname, 'db.sqlite');

const db = new sqlite3.Database(DB_PATH, (err)=>{
  if(err) { console.error('DB open error', err); process.exit(1); }
});

db.serialize(()=>{
  db.run(`CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    price REAL NOT NULL,
    stock INTEGER NOT NULL DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
  );`, (err)=>{
    if(err) { console.error('schema error', err); process.exit(1); }
  });
  db.run(`CREATE TABLE IF NOT EXISTS promotions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT NOT NULL UNIQUE,
    description TEXT,
    discount REAL NOT NULL,
    active INTEGER NOT NULL DEFAULT 1,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
  );`, (err)=>{ if(err){ console.error('schema error 2', err); } });
  const stmt = db.prepare('INSERT INTO products (name, description, price, stock) VALUES (?, ?, ?, ?)');
  stmt.run('Widget A', 'A goofy widget', 9.99, 100);
  stmt.run('Widget B', 'Another silly widget', 14.99, 50);
  stmt.finalize();
  const p2 = db.prepare('INSERT INTO promotions (code, description, discount, active) VALUES (?, ?, ?, ?)');
  p2.run('WELCOME10', '10% off first order', 10.0, 1);
  p2.run('SPRING5', '5% off spring sale', 5.0, 1);
  p2.finalize();
  console.log('Seeded products and promotions');
});

db.close();
