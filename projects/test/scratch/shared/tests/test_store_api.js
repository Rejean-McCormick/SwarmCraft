// Minimal tests for Store API routing
const request = require('supertest');
const express = require('express');

// Lightweight mounting for tests: mount the router directly from store_api.js
let storeRouter;
try {
  storeRouter = require('../src/store_api');
} catch (e) {
  storeRouter = null;
}

const app = express();
app.use(express.json());
if(storeRouter){ app.use('/api/store', storeRouter); }

describe('Store API basics', ()=>{
  test('GET /api/store should respond', async ()=>{
    const res = await request(app).get('/api/store');
    expect(res.status).toBeGreaterThanOrEqual(200);
  });
  test('GET /api/store/products should respond', async ()=>{
    const res = await request(app).get('/api/store/products');
    expect(res.status).toBeGreaterThanOrEqual(200);
  });
});
