const express = require('express');
const request = require('supertest');
const userRouter = require('../src/users');

describe('User API integration', () => {
  let app;
  beforeAll((done) => {
    // Simple express app mounting the router
    app = express();
    app.use('/api', userRouter);
    done();
  });

  afterAll(() => {
    // Optional: close any resources if needed
  });

  test('GET /api/users returns empty array initially', async () => {
    const res = await request(app).get('/api/users');
    expect(res.statusCode).toBe(200);
    expect(res.body).toHaveProperty('success', true);
    expect(Array.isArray(res.body.users)).toBe(true);
  });

  test('POST /api/users with valid data', async () => {
    const res = await request(app).post('/api/users').send({ name: 'Alice', email: 'alice@example.com' });
    expect(res.statusCode).toBe(201);
    expect(res.body).toHaveProperty('success', true);
    expect(res.body).toHaveProperty('user');
    expect(typeof res.body.user.id).toBe('number');
  });

  test('GET /api/users/:id returns the user', async () => {
    const res = await request(app).get('/api/users/1');
    expect(res.statusCode).toBe(200);
    expect(res.body).toHaveProperty('success', true);
    expect(res.body).toHaveProperty('user');
  });
});
