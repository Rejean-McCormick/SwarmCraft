import express from 'express';

const router = express.Router();

// Health check endpoint mounted at /health
router.get('/', (req, res) => {
  res.json({ status: 'ok' });
});

export default router;
