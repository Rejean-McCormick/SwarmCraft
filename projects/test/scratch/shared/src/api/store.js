const express = require('express');
const router = express.Router();

// Placeholder for Phase 2 endpoints; to be completed by Codey McBackend
router.get('/products', (req, res)=>{ res.json({products: []}); });
router.get('/products/:id', (req, res)=>{ res.json({product: null}); });
router.get('/promotions', (req, res)=>{ res.json({promotions: []}); });
router.get('/about', (req, res)=>{ res.json({about: 'This is a goofy mock e-commerce MVP'}); });
router.post('/checkout', (req, res)=>{ res.status(400).json({error:'Not implemented yet'}); });
router.get('/invoice/:id', (req, res)=>{ res.json({invoice: null}); });

module.exports = router;
