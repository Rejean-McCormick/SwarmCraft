/* JokeGen API - GET /jokes?count=N and POST /jokes
 * - uses SQLite-backed storage when available via scratch/shared/src/storage.js
 * - basic input validation and idempotent deduplication via content hash in storage
 */
const express = require('express');
const path = require('path');
const { JokeStore } = require('./storage');

const router = express.Router();

let store = null;
async function ensureStore() {
  if (!store) {
    const dbPath = process.env.JOKE_DB_PATH || path.join(__dirname, '..', 'db', 'jokes.db');
    store = new JokeStore(dbPath);
    try {
      await store.init();
    } catch (e) {
      // If init fails, fall back to in-memory
      store = null;
    }
  }
}

// Simple in-memory demo store used only if DB is unavailable
let inMemoryStore = [];
function addInMemory(joke) {
  inMemoryStore.unshift(joke);
}
function getInMemory(limit) {
  return inMemoryStore.slice(0, limit);
}

// Basic GET /jokes?count=N
router.get('/jokes', async (req, res) => {
  const raw = parseInt(req.query.count);
  const count = Number.isNaN(raw) ? 1 : raw;
  // Validation: positive integer up to 1000
  if (!Number.isInteger(count) || count <= 0 || count > 1000) {
    return res.status(400).json({ error: 'count must be an integer between 1 and 1000' });
  }
  try {
    await ensureStore();
    if (store && store.useDb) {
      const limit = Math.min(count, 1000);
      const rows = await store.getJokes(limit);
      const jokes = rows.map(r => ({ id: r.id, setup: r.setup, punchline: r.punchline, category: r.category, author: r.author, created_at: r.created_at }));
      return res.json({ jokes });
    }
  } catch (e) {
    // fall through to in-memory
  }
  // In-memory path
  const jokes = getInMemory(Math.min(count, 1000));
  res.json({ jokes });
});

// Basic POST /jokes
router.post('/jokes', async (req, res) => {
  const { setup, punchline, category, author } = req.body || {};
  if (!setup || !punchline) {
    return res.status(400).json({ error: 'setup and punchline are required' });
  }
  const created_at = new Date().toISOString();
  const joke = { id: Date.now(), setup, punchline, category, author, created_at };
  if (store && store.useDb) {
    try {
      const result = await store.addJoke(setup, punchline, category, author);
      const response = {
        id: result.id,
        setup,
        punchline,
        category,
        author,
        created_at: result.created_at || joke.created_at,
        existing: !!result.existing
      };
      return res.status(201).json(response);
    } catch (e) {
      // Fallback to in-memory on DB write failure
      addInMemory(joke);
      return res.status(201).json(joke);
    }
  }
  // In-memory path
  addInMemory(joke);
  res.status(201).json(joke);
});

module.exports = router;
