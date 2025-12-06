const express = require('express');
const router = express.Router();
router.get('/ping', (req, res) => {
  res.json({ module: 'testmodAlpha', api: '/ping', method: 'GET' });
});
module.exports = { router };
