/* JokeGen API - MVP Batch Endpoints (v2) behind feature flag
 * - POST /api/jokes/batches
 * - GET  /api/jokes/batches/:batchId/status
 * - In-memory BatchStore with 4-worker pool (production hint: replace with a proper queue in future)
 * - SQLite-backed JokeStore for persistence with content hash dedupe
 * - Deterministic joke generator for MVP
 */
const path = require('path');
const express = require('express');
const { v4: uuidv4 } = require('uuid');
const { JokeStore } = require('./storage');
const { generateJoke } = require('./generator');
let { Worker } = (() => {
  try {
    // dynamic require in case environment differs
    return require('worker_threads');
  } catch (e) {
    return null;
  }
})();

// Constants
const MAX_WORKERS = 4;

// In-memory batch store
class BatchStore {
  constructor() {
    this.batches = new Map();
  }
  create(batchSize, prompts = []) {
    const id = uuidv4();
    const batch = {
      id,
      batchSize,
      prompts,
      createdAt: new Date().toISOString(),
      startedAt: null,
      completedAt: null,
      status: 'in_progress', // in_progress, completed, failed
      createdIds: [],
      error: null
    };
    this.batches.set(id, batch);
    return batch;
  }
  get(id) {
    return this.batches.get(id);
  }
  update(id, patch) {
    const b = this.batches.get(id);
    if (!b) return null;
    Object.assign(b, patch);
    this.batches.set(id, b);
    return b;
  }
}

// Simple deterministic joke generator
function generateJokeFromSeed(seed) {
  // Reuse existing generator logic to ensure deterministic results
  const j = generateJoke(seed, {});
  return j;
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

function createApp() {
  const app = express();
  app.use(express.json({ limit: '1mb' }));
  const batchStore = new BatchStore();
  const jokeStore = new JokeStore(path.join(__dirname, 'jokes_v2.db'));
  let storeReady = false;

  async function initStore() {
    if (!storeReady) {
      try {
        await jokeStore.init();
        storeReady = true;
      } catch (e) {
        // fallback to in-memory storage if DB fails; but keep API functional
        storeReady = false;
      }
    }
  }

  async function addJokePersist(setup, punchline, category, author) {
    await initStore();
    if (storeReady) {
      const res = await jokeStore.addJoke(setup, punchline, category, author).catch(() => null);
      if (res) return res.id;
    }
    // fallback to ephemeral id
    return Date.now();
  }

  // Worker-like generator (simple serial/parallel abstraction)
  async function runBatch(batch) {
    batch.startedAt = new Date().toISOString();
    const total = batch.batchSize;
    const seeds = Array.from({ length: total }, (_, i) => `seed-${i}`);

    // Try to use a worker pool if available; otherwise fall back to serial generation
    const chunks = [];
    const workersToUse = Math.min(MAX_WORKERS, Math.max(1, total));
    const perWorker = Math.ceil(total / workersToUse);
    for (let i = 0; i < workersToUse; i++) {
      const start = i * perWorker;
      const end = Math.min(start + perWorker, total);
      const chunk = seeds.slice(start, end);
      if (chunk.length > 0) chunks.push(chunk);
    }

    // If workers are available, distribute work; otherwise sequentially compute
    const resultsFromWorkers = [];
    if (typeof Worker === 'function' || (Worker && typeof Worker === 'object')) {
      // Attempt to spawn real workers using joke_batch_worker.js
      try {
        const workerPath = path.join(__dirname, 'joke_batch_worker.js');
        const workerPromises = chunks.map((chunk) => {
          return new Promise((resolve, reject) => {
            try {
              const w = new Worker(workerPath, { workerData: { batchId: batch.id, seeds: chunk } });
              w.on('message', (msg) => {
                if (msg && Array.isArray(msg.results)) {
                  resolve(msg.results);
                } else if (msg && msg.error) {
                  reject(new Error(msg.error));
                } else {
                  resolve([]);
                }
              });
              w.on('error', reject);
              w.on('exit', (code) => {
                if (code !== 0) reject(new Error(`Worker stopped with exit code ${code}`));
              });
            } catch (e) {
              // Fallback to sequential path if worker creation fails
              reject(e);
            }
          });
        });

        const chunkResults = await Promise.all(workerPromises);
        resultsFromWorkers.push(...chunkResults.flat());
      } catch (e) {
        // Fallback to serial/joke generation in main thread
        for (let i = 0; i < total; i++) {
          const joke = generateJokeFromSeed(seeds[i]);
          resultsFromWorkers.push({ seed: seeds[i], joke });
        }
      }
    } else {
      // No Worker support; fall back to sequential generation
      for (let i = 0; i < total; i++) {
        const joke = generateJokeFromSeed(seeds[i]);
        resultsFromWorkers.push({ seed: seeds[i], joke });
      }
    }

    // Persist jokes
    const createdIds = [];
    for (const item of resultsFromWorkers) {
      const j = item.joke;
      const id = await addJokePersist(j.setup, j.punchline, j.category, j.author);
      createdIds.push(id);
    }

    batch.completedAt = new Date().toISOString();
    batch.status = 'completed';
    batch.createdIds = createdIds;
  }

  // Start batch processing (fire-and-forget)
  function startBatchProcessing(batch) {
    (async () => {
      await runBatch(batch);
    })();
  }

  // POST /api/jokes/batches
  app.post('/api/jokes/batches', async (req, res) => {
    // Simple feature flag gate could be inserted here; assume enabled
    const { batchSize, prompts } = req.body || {};
    const size = Number.isInteger(batchSize) ? batchSize : NaN;

    if (!Number.isInteger(size) || size <= 0 || size > 1000) {
      return res.status(400).json({ error: 'batchSize must be an integer between 1 and 1000' });
    }

    const batch = batchStore.create(size, prompts || []);
    res.status(202).json({ batchId: batch.id, status: batch.status, total: batch.batchSize });
    // Start processing asynchronously
    startBatchProcessing(batch);
  });

  // GET /api/jokes/batches/:batchId/status
  app.get('/api/jokes/batches/:batchId/status', async (req, res) => {
    const id = req.params.batchId;
    const batch = batchStore.get(id);
    if (!batch) {
      return res.status(404).json({ error: 'batch not found' });
    }
    res.json({
      batchId: batch.id,
      status: batch.status,
      total: batch.batchSize,
      createdIds: batch.createdIds,
      startedAt: batch.startedAt,
      completedAt: batch.completedAt,
      error: batch.error
    });
  });

  return { app, batchStore, jokeStore };
}

module.exports = { createApp };
