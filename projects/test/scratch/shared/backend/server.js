// scratch/shared/backend/server.js
const express = require('express');
const app = express();
const port = 3001;

app.use(express.json());
app.use(require('cors')());

// In-memory seedable data placeholders (will be replaced by DB soon)
let products = [
  { id: 1, name: 'Snacky Sneakers', description: 'Cool kicks', price: 49.99, promo_price: 39.99, image: ' sneakers.jpg ', stock: 10, category: 'Footwear' },
  { id: 2, name: 'Nebula Tee', description: 'A shirt with vibes', price: 19.99, promo_price: 15.99, image: 'teeshirt.png', stock: 25, category: 'Apparel' }
];
let promotions = [
  { id: 1, title: 'Launch Discount', discount: 0.15, start_date: '2025-01-01', end_date: '2025-12-31' }
];

app.get('/api/products', (req, res) => res.json(products));
app.post('/api/products', (req, res) => { const p = req.body; p.id = products.length+1; products.push(p); res.json(p); });
app.get('/api/products/:id', (req, res) => { const p = products.find(x => x.id == req.params.id); res.json(p || { error: 'not found' }); });
app.get('/api/promotions', (req, res) => res.json(promotions));
// Simple pages API
app.get('/api/pages', (req, res) => res.json({ home: 'Welcome to Absurd MVP Store' }));

// Cart placeholder
let cart = [];
app.post('/api/cart', (req, res) => { cart.push(req.body); res.json({ cart }); });

// Checkout placeholder
app.post('/api/checkout', (req, res) => {
  const invoiceId = Math.floor(Math.random()*1000000);
  res.json({ status: 'ok', invoice_id: invoiceId, note: 'This is a mock checkout. No real payment processed.'});
});

app.listen(port, () => {
  console.log(`Backend mock listening at http://localhost:${port}`);
});
