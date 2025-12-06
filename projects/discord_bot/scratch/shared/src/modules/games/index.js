// Games module index for modular API
const express = require('express');
const router = express.Router();

router.post('/blackjack/start', (req, res) => {
  res.status(501).json({ error: 'not_implemented' });
});

router.post('/roulette/start', (req, res) => {
  res.status(501).json({ error: 'not_implemented' });
});

module.exports = router;
