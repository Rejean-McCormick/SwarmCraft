// Auth module index - wires to app routes in shared/app.js

const express = require('express');
const router = express.Router();

// Placeholder to show contract-driven interface per spec
router.post('/register', (req, res) => {
  res.status(501).json({ error: 'not_implemented' });
});

router.post('/login', (req, res) => {
  res.status(501).json({ error: 'not_implemented' });
});

module.exports = router;
