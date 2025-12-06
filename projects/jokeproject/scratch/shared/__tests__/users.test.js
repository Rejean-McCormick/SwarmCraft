const request = require('supertest');
const express = require('express');

// Import the users router from the implemented API
const usersRouter = require('../src/users');

describe('User API - /users', () => {
  let app;

  beforeAll(() => {
    app = express();
    app.use('/users', usersRouter);
  });

  beforeEach(async () => {
    // Reset database state before each test for isolation
    if (typeof usersRouter.resetDatabase === 'function') {
      await usersRouter.resetDatabase();
    }
  });

  test('GET /users returns empty array initially', async () => {
    const res = await request(app).get('/users');
    expect(res.statusCode).toBe(200);
    expect(Array.isArray(res.body)).toBe(true);
    expect(res.body.length).toBe(0);
  });

  test('POST /users creates a new user', async () => {
    const payload = { name: 'Alice', email: 'alice@example.com' };
    const postRes = await request(app).post('/users').send(payload);
    expect(postRes.statusCode).toBe(201);
    expect(postRes.body).toHaveProperty('id');
    expect(postRes.body.name).toBe(payload.name);
    expect(postRes.body.email).toBe(payload.email);
    expect(postRes.body).toHaveProperty('created_at');

    // Verify in list
    const listRes = await request(app).get('/users');
    expect(listRes.statusCode).toBe(200);
    expect(listRes.body.length).toBe(1);
    expect(listRes.body[0].name).toBe(payload.name);
    expect(listRes.body[0].email).toBe(payload.email);
  });

  test('POST /users with invalid data returns 400', async () => {
    const res = await request(app).post('/users').send({ name: '', email: 'notanemail' });
    expect(res.statusCode).toBe(400);
  });

  test('GET /users/:id returns the user', async () => {
    const postRes = await request(app).post('/users').send({ name: 'Bob', email: 'bob@example.com' });
    expect(postRes.statusCode).toBe(201);
    const id = postRes.body.id;

    const getRes = await request(app).get(`/users/${id}`);
    expect(getRes.statusCode).toBe(200);
    expect(getRes.body.id).toBe(id);
    expect(getRes.body.name).toBe('Bob');
    expect(getRes.body.email).toBe('bob@example.com');
  });

  test('GET /users/:id with invalid id returns 400', async () => {
    const res = await request(app).get('/users/abc');
    expect(res.statusCode).toBe(400);
  });

  test('GET /users/:id for non-existent user returns 404', async () => {
    const res = await request(app).get('/users/99999');
    expect(res.statusCode).toBe(404);
  });
});
