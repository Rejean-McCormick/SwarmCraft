"use strict";

const express = require('express');
const helmet = require('helmet');
const cors = require('cors');

// Routers
const authRouter = require('./auth/authRouter');
const walletRouter = require('./wallet/walletRouter');
const shopRouter = require('./shop/shopRouter');
const gamesRouter = require('./games/gamesRouter');

// Simple in-memory rate limiter per IP (for demo purposes)
const rateLimiter = (() => {
  const hits = new Map();
  const WINDOW_MS = 15 * 60 * 1000; // 15 minutes
  const MAX_HITS = 100; // per window
  return (req, res, next) => {
    const ip = (req.ip || req.connection?.remoteAddress || req.headers['x-forwarded-for'] || 'unknown').toString();
    const now = Date.now();
    const entry = hits.get(ip) || { t: now, c: 0 };
    if (now - entry.t > WINDOW_MS) {
      // reset window
      hits.set(ip, { t: now, c: 1 });
    } else {
      entry.c += 1;
      hits.set(ip, entry);
    }
    if (entry.c > MAX_HITS) {
      res.status(429).json({ error: 'rate_limited', retry_after_ms: WINDOW_MS });
    } else {
      next();
    }
  };
})();

function createApp() {
  const app = express();
  app.use(helmet());
  app.use(cors());
  app.use(express.json());
  app.use(express.urlencoded({ extended: true }));

  // Simple health check
  app.get('/health', (req, res) => req ? res.json({ status: 'ok' }) : res.json({ status: 'ok' }));

  // Rate limit middleware for all API routes
  app.use('/api', rateLimiter);

  // Mount modular routers under /api
  app.use('/api/auth', authRouter);
  app.use('/api/wallet', walletRouter);
  app.use('/api/shop', shopRouter);
  app.use('/api/games', gamesRouter);

  // Global error handler
  app.use((err, req, res, next) => {
    console.error('Unhandled error:', err);
    res.status(500).json({ error: 'internal_server_error', detail: err?.message || 'unknown' });
  });

  return app;
}

module.exports = { createApp };
