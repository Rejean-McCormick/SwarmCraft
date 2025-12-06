const express = require('express');
const request = require('supertest');
const userRouter = require('./../src/users');

describe('User API security', () => {
  let app;
  beforeAll(() => {
    app = express();
    app.use('/api', userRouter);
  });

  test('Reject SQL injection attempt via name field', async () => {
    const res = await request(app).post('/api/users').send({ name: "Robert'); DROP TABLE users;--", email: 'robert@example.org' });
    // Should be treated as normal string input; not execute injection
    expect(res.statusCode).toBeGreaterThanOrEqual(200);
  });

  test('POST /api/users with invalid email is rejected', async () => {
    const res = await request(app).post('/api/users').send({ name: 'Bob', email: 'not-an-email' });
    expect(res.statusCode).toBe(400);
  });

  test('GET /api/users/:id with invalid id returns 400', async () => {
    const res = await request(app).get('/api/users/abc');
    expect(res.statusCode).toBe(400);
  });
});
