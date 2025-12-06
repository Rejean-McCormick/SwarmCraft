const express = require('express');
const router = express.Router();
router.post('/echo', (req, res) => {
  res.json({ module: 'testmodBeta', api: '/echo', method: 'POST', received: req.body || {} });
});
module.exports = { router };
