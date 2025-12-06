"use strict";

const express = require('express');
const request = require('supertest');
const path = require('path');

// Import the router (skeleton) implemented earlier
const userRouter = require('../src/users');

describe('User API integration tests', () => {
  let app;
  const DB_PATH = path.resolve(__dirname, '../data/users.db');

  beforeAll(() => {
    app = express();
    app.use(express.json());
    app.use('/api', userRouter);
  });

  afterAll(() => {
    // Cleanup the test DB file
    try {
      const fs = require('fs');
      if (fs.existsSync(DB_PATH)) {
        fs.unlinkSync(DB_PATH);
      }
    } catch (e) {
      // ignore cleanup errors
    }
  });

  test('GET /api/users returns an array', async () => {
    const res = await request(app).get('/api/users');
    expect(res.status).toBe(200);
    expect(res.body).toHaveProperty('success', true);
    expect(Array.isArray(res.body.users)).toBe(true);
  });

  test('POST /api/users creates a user', async () => {
    const payload = { name: 'Alice', email: 'alice@example.com' };
    const res = await request(app).post('/api/users').send(payload);
    expect(res.status).toBe(201);
    expect(res.body).toHaveProperty('success', true);
    expect(res.body).toHaveProperty('user');
    expect(res.body.user).toHaveProperty('id');
    expect(res.body.user.name).toBe(payload.name);
    expect(res.body.user.email).toBe(payload.email);
  });

  test('GET /api/users/:id returns the created user', async () => {
    const payload = { name: 'Bob', email: 'bob@example.com' };
    const create = await request(app).post('/api/users').send(payload);
    const id = create.body.user.id;
    const res = await request(app).get(`/api/users/${id}`);
    expect(res.status).toBe(200);
    expect(res.body).toHaveProperty('user');
    expect(res.body.user.id).toBe(id);
  });

  test('POST /api/users with invalid email returns 400', async () => {
    const res = await request(app).post('/api/users').send({ name: 'X', email: 'not-an-email' });
    expect(res.status).toBe(400);
    expect(res.body).toHaveProperty('success', false);
  });

  test('GET /api/users/:id for non-existent returns 404', async () => {
    const res = await request(app).get('/api/users/999999');
    expect([404, 400]).toContain(res.status);
  });
});
