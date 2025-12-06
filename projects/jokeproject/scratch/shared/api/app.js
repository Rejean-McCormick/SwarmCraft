const express = require('express');
const bodyParser = require('body-parser');
const { JokeStore } = require('./storage');

const app = express();
app.use(bodyParser.json({ limit: '1mb' }));

// In-memory placeholder; replace with storage.js integration
let store;
async function ensureStore() {
  if (!store) {
    store = new JokeStore(process.env.JOKE_DB_PATH || './scratch/shared/db/jokes.db');
    await store.init();
  }
}

// Basic rate limiter (per IP) for demo purposes
const rateLimitMap = new Map();
function rateLimiter(req, res, next) {
  const windowMs = 60 * 1000; // 1 minute window
  const limit = parseInt(process.env.JOKEGEN_RATE_LIMIT || '60');
  const ip = req.ip || req.connection.remoteAddress;
  const rec = rateLimitMap.get(ip) || { c: 0, t: Date.now() };
  if (Date.now() - rec.t > windowMs) {
    rec.c = 0; rec.t = Date.now();
  }
  rec.c += 1;
  rateLimitMap.set(ip, rec);
  if (rec.c > limit) {
    res.set('Retry-After', String(windowMs / 1000));
    return res.status(429).json({ error: 'Too many requests, please try again later.' });
  }
  next();
}

app.get('/api/jokes', rateLimiter, async (req, res) => {
  await ensureStore().catch(() => {});
  const count = parseInt(req.query.count) || 1;
  const limit = Math.max(1, Math.min(100, count));
  const jokes = [];
  // For demo: fetch from store in a loop
  for (let i = 0; i < limit; i++) {
    // Simple generation fallback if store is empty
    const joke = {
      id: i + 1,
      setup: 'Why did the server cross the network?',
      punchline: 'To fetch a response on the other side!',
      category: 'demo',
      author: 'system',
      created_at: new Date().toISOString(),
    };
    jokes.push(joke);
  }
  res.json({ jokes });
});

app.post('/api/jokes', rateLimiter, async (req, res) => {
  await ensureStore().catch(() => {});
  const { setup, punchline, category, author } = req.body || {};
  if (!setup || !punchline) {
    return res.status(400).json({ error: 'setup and punchline are required' });
  }
  const joke = { id: Date.now(), setup, punchline, category, author, created_at: new Date().toISOString() };
  // Persist if storage wired; for now, just return object
  res.status(201).json({ joke });
});

module.exports = app;
