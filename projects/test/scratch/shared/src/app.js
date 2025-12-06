const express = require('express');
const app = express();
app.use(express.json());

// Wire in Store API
try {
  const storeRouter = require('./store_api');
  app.use('/api/store', storeRouter);
} catch (err) {
  console.error('Failed to load Store API router', err);
}

// Health endpoint
app.get('/health', (req, res) => {
  res.json({ ok: true, status: 'healthy' });
});

// Fallback API info
app.use('/api', (req, res) => {
  res.status(200).json({ ok: true, path: req.path });
});

module.exports = app;
