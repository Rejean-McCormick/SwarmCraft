const request = require('supertest');
const express = require('express');
const createUsersRouter = require('../src/users');

// Helper to build a fresh app per test to isolate in-memory DB
function buildApp() {
  const app = express();
  app.use(express.json());
  app.use('/users', createUsersRouter());
  return app;
}

describe('Users API', () => {
  test('GET /users initially returns empty list', async () => {
    const app = buildApp();
    const res = await request(app).get('/users');
    expect(res.status).toBe(200);
    expect(res.body).toHaveProperty('users');
    expect(Array.isArray(res.body.users)).toBe(true);
    expect(res.body.users.length).toBe(0);
  });

  test('POST /users with valid data creates user', async () => {
    const app = buildApp();
    const payload = { name: 'Alice', email: 'alice@example.com' };
    const res = await request(app).post('/users').send(payload);
    expect(res.status).toBe(201);
    expect(res.body).toHaveProperty('id');
    expect(res.body.name).toBe(payload.name);
    expect(res.body.email).toBe(payload.email);
    expect(typeof res.body.created_at).toBe('string');
  });

  test('GET /users returns created user', async () => {
    const app = buildApp();
    const payload = { name: 'Bob', email: 'bob@example.com' };
    const postRes = await request(app).post('/users').send(payload);
    expect(postRes.status).toBe(201);
    const getRes = await request(app).get('/users');
    expect(getRes.status).toBe(200);
    expect(getRes.body.users.length).toBe(1);
    expect(getRes.body.users[0].email).toBe(payload.email);
  });

  test('POST /users with invalid name returns 400', async () => {
    const app = buildApp();
    const res = await request(app).post('/users').send({ name: '', email: 'a@b.c' });
    expect(res.status).toBe(400);
  });

  test('POST /users with invalid email returns 400', async () => {
    const app = buildApp();
    const res = await request(app).post('/users').send({ name: 'John', email: 'not-an-email' });
    expect(res.status).toBe(400);
  });

  test('POST /users with duplicate email returns 409', async () => {
    const app = buildApp();
    const payload = { name: 'Carol', email: 'carol@example.com' };
    const first = await request(app).post('/users').send(payload);
    expect(first.status).toBe(201);
    const second = await request(app).post('/users').send({ name: 'Carol2', email: payload.email });
    expect(second.status).toBe(409);
  });

  test('GET /users/:id returns user or 404', async () => {
    const app = buildApp();
    const payload = { name: 'Dave', email: 'dave@example.com' };
    const postRes = await request(app).post('/users').send(payload);
    expect(postRes.status).toBe(201);
    const id = postRes.body.id;
    const getRes = await request(app).get(`/users/${id}`);
    expect(getRes.status).toBe(200);
    expect(getRes.body.id).toBe(id);
    const notFound = await request(app).get('/users/99999');
    expect(notFound.status).toBe(404);
  });

  test('GET /users/:id with invalid id returns 400', async () => {
    const app = buildApp();
    const res = await request(app).get('/users/abc');
    expect(res.status).toBe(400);
  });

  test('SQL injection-like input is treated as data (not executed)', async () => {
    const app = buildApp();
    const payload = { name: 'Eve', email: "eve@example.com' OR '1'='1" };
    const res = await request(app).post('/users').send(payload);
    expect(res.status).toBe(201);
    const list = await request(app).get('/users');
    expect(list.status).toBe(200);
    const found = list.body.users.find(u => u.email === payload.email);
    expect(found).toBeTruthy();
  });
});
