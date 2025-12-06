// Wallet module index

const express = require('express');
const router = express.Router();

router.get('/balance', (req, res) => {
  res.status(501).json({ error: 'not_implemented' });
});

module.exports = router;
