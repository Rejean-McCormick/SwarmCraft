// Shop module index

const express = require('express');
const router = express.Router();

router.get('/items', (req, res) => {
  res.status(501).json({ error: 'not_implemented' });
});

module.exports = router;
