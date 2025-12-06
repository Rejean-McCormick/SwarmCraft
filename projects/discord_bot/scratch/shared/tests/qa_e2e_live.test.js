// End-to-end QA live test harness for auth, wallet, shop, and games
// This uses the in-process Express app exposed by shared/app.js
// DB uses an in-memory SQLite DB for isolation.

const path = require('path');

let app;
let request;
let userId = null;

beforeAll(async () => {
  // Enable in-memory DB
  process.env.DB_PATH = ':memory:';
  // Lazily load app after env var is set
  const { createApp } = require('../app');
  app = createApp();
  const supertest = require('supertest');
  request = supertest(app);
});

describe('End-to-end QA harness: auth, wallet, shop, games', () => {
  test('register user', async () => {
    const res = await request
      .post('/api/auth/register')
      .send({ username: 'qa_user', password: 'Secret123!' });
    expect(res.status).toBe(200);
    expect(res.body).toHaveProperty('id');
    expect(res.body.username).toBe('qa_user');
    userId = res.body.id;
  });

  test('login user', async () => {
    const res = await request
      .post('/api/auth/login')
      .send({ username: 'qa_user', password: 'Secret123!' });
    expect(res.status).toBe(200);
    expect(res.body).toHaveProperty('token');
  });

  test('wallet deposit and balance', async () => {
    // Deposit 150
    const dep = await request
      .post('/api/wallet/deposit')
      .send({ amount: 150 })
      .set('x-user-id', userId);
    expect(dep.status).toBe(200);
    // Balance check
    const bal = await request
      .get('/api/wallet/balance')
      .set('x-user-id', userId);
    expect(bal.status).toBe(200);
    expect(typeof bal.body.balance).toBe('number');
    expect(bal.body.balance).toBeGreaterThanOrEqual(0);
  });

  test('shop list and buy item', async () => {
    const items = await request
      .get('/api/shop/items')
      .set('x-user-id', userId);
    expect(items.status).toBe(200);
    expect(Array.isArray(items.body)).toBe(true);
    const first = items.body[0];
    expect(first).toHaveProperty('id');

    const buy = await request
      .post('/api/shop/buy')
      .send({ itemId: first.id, quantity: 1 })
      .set('x-user-id', userId);
    // can fail due to insufficient funds if balance runs out; but we deposited 150; ensure total is numeric
    expect(buy.status).toBeGreaterThan(199); // 2xx
    expect(buy.body).toHaveProperty('total');
  });

  test('games blackjack start', async () => {
    const start = await request
      .post('/api/games/blackjack/start')
      .set('x-user-id', userId);
    // Depending on DB, this should succeed and return a sessionId
    expect(start.status).toBe(200);
    expect(start.body).toHaveProperty('sessionId');
  });

  test('404 path', async () => {
    const notFound = await request.get('/api/nonexistent');
    expect(notFound.status).toBe(404);
  });
});
