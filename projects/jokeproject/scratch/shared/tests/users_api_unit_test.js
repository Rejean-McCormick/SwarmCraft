// Unit tests for the User API router (Express + SQLite with fallback)
const http = require('http');
const express = require('express');
const assert = require('assert');

function httpRequest(options, data) {
  return new Promise((resolve, reject) => {
    const req = http.request(options, (res) => {
      let body = '';
      res.on('data', (chunk) => { body += chunk; });
      res.on('end', () => {
        let parsed = null;
        try { parsed = JSON.parse(body); } catch (e) { parsed = body; }
        resolve({ statusCode: res.statusCode, body: parsed });
      });
    });
    req.on('error', reject);
    if (data) {
      req.write(JSON.stringify(data));
    }
    req.end();
  });
}

async function test() {
  // Setup app and mount our users router
  const app = express();
  app.use(express.json());
  const router = require('../src/users.js');
  app.use('/api', router);
  const server = app.listen(0, async () => {
    const port = server.address().port;

    // 1) GET /api/users
    let res = await httpRequest({ hostname: '127.0.0.1', port, path: '/api/users', method: 'GET' }, null);
    assert.ok([200, 304].includes(res.statusCode));

    // 2) POST /api/users
    const user = { name: 'Unit Test User', email: 'unit@example.com' };
    res = await httpRequest({ hostname: '127.0.0.1', port, path: '/api/users', method: 'POST', headers: { 'Content-Type': 'application/json' } }, user);
    assert.strictEqual(res.statusCode, 201);
    const created = res.body && res.body.user;
    assert.ok(created && created.id);

    // 3) GET /api/users/:id
    res = await httpRequest({ hostname: '127.0.0.1', port, path: `/api/users/${created.id}`, method: 'GET' }, null);
    assert.strictEqual(res.statusCode, 200);
    assert.ok(res.body && res.body.user && res.body.user.id === created.id);

    // 4) POST /api/users with invalid input (missing name)
    res = await httpRequest({ hostname: '127.0.0.1', port, path: '/api/users', method: 'POST', headers: { 'Content-Type': 'application/json' } }, { email: 'no-name@example.com' });
    assert.strictEqual(res.statusCode, 400);

    server.close();
    console.log('User API unit tests passed');
  });
}

test().catch(err => {
  console.error('Unit test failed', err);
  process.exit(1);
});
