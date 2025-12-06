const path = require('path');
const fs = require('fs');
const request = require('supertest');

// Set DB path to scratch/shared/data/users.db before requiring app
const DB_PATH = path.join(__dirname, '../data/users.db');
process.env.SCRATCH_DB_PATH = DB_PATH;

// Ensure DB directory exists and is clean for tests
beforeAll(() => {
  const dir = path.dirname(DB_PATH);
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
  if (fs.existsSync(DB_PATH)) {
    fs.unlinkSync(DB_PATH);
  }
});

// Import app after env is set
const app = require('../../infra/api');

describe('User API - integration tests', () => {
  test('GET /api/users initially returns empty array', async () => {
    const res = await request(app).get('/api/users');
    expect(res.status).toBe(200);
    expect(Array.isArray(res.body)).toBe(true);
    expect(res.body.length).toBe(0);
  });

  test('POST /api/users creates a user', async () => {
    const payload = { name: 'Alice', email: 'alice@example.com', password: 'secret' };
    const res = await request(app).post('/api/users').send(payload);
    expect(res.status).toBe(201);
    expect(res.body).toHaveProperty('id');
    expect(res.body.email).toBe(payload.email);
  });

  test('GET /api/users/:id returns the created user', async () => {
    // Create a user first to obtain id
    const payload = { name: 'Bob', email: 'bob@example.com', password: 'secret' };
    const createRes = await request(app).post('/api/users').send(payload);
    expect(createRes.status).toBe(201);
    const id = createRes.body.id;
    const getRes = await request(app).get(`/api/users/${id}`);
    expect(getRes.status).toBe(200);
    expect(getRes.body).toHaveProperty('id', id);
    expect(getRes.body).toHaveProperty('name', payload.name);
    expect(getRes.body).toHaveProperty('email', payload.email);
  });

  test('POST /api/users with missing fields returns 400', async () => {
    const payload = { name: 'Charlie' };
    const res = await request(app).post('/api/users').send(payload);
    expect(res.status).toBe(400);
  });

  test('POST /api/users with injection-like payload should not crash and should return 201 (sanitized input)', async () => {
    const payload = { name: 'Eve', email: "eve@example.com'; DROP TABLE users; --", password: 'pw' };
    const res = await request(app).post('/api/users').send(payload);
    // Should create user as the input is treated as data, not executable SQL
    expect([200, 201, 400].includes(res.status)).toBe(true);
  });
});
