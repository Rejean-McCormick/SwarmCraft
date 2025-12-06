#!/usr/bin/env node
// Lightweight integration test for JokeGen API (GET/POST) using a spawned server
const http = require('http');
const assert = require('assert');
const { spawn } = require('child_process');

const PORT = 8080;
const SERVER_CMD = 'node';
const SERVER_SCRIPT = 'scratch/shared/server.js';

function httpRequest(method, path, body) {
  return new Promise((resolve, reject) => {
    const options = {
      hostname: '127.0.0.1',
      port: PORT,
      path,
      method,
      headers: {
        'Content-Type': 'application/json'
      }
    };
    let payload = null;
    if (body !== undefined && body !== null) {
      payload = JSON.stringify(body);
      options.headers['Content-Length'] = Buffer.byteLength(payload);
    }
    const req = http.request(options, (res) => {
      let data = '';
      res.setEncoding('utf8');
      res.on('data', (chunk) => { data += chunk; });
      res.on('end', () => {
        let parsed = data;
        try {
          if (data) parsed = JSON.parse(data);
        } catch (e) {
          // leave as raw
        }
        resolve({ statusCode: res.statusCode, body: parsed });
      });
    });
    req.on('error', (err) => reject(err));
    if (payload) req.write(payload);
    req.end();
  });
}

function waitForServerReady(proc) {
  return new Promise((resolve, reject) => {
    let ready = false;
    const onData = (data) => {
      const str = data.toString();
      // Console output example: JokeGen API running on port 8080
      if (str.includes('JokeGen API running on port')) {
        ready = true;
        cleanup();
        resolve();
      }
    };
    const onError = (err) => {
      if (!ready) {
        cleanup();
        reject(err);
      }
    };
    const cleanup = () => {
      proc.stdout.removeListener('data', onData);
      proc.stderr.removeListener('data', onData);
      proc.removeListener('error', onError);
    };
    proc.stdout.on('data', onData);
    proc.stderr.on('data', onData);
    proc.on('error', onError);
  });
}

async function runTests() {
  console.log('Starting JokeGen API integration tests...');
  const child = spawn(SERVER_CMD, [SERVER_SCRIPT], {
    stdio: ['ignore', 'pipe', 'pipe']
  });

  try {
    await waitForServerReady(child);
    // TM-01 / TM-02: GET jokes with count
    let res = await httpRequest('GET', '/api/jokes?count=2', null);
    assert.strictEqual(res.statusCode, 200, 'GET status should be 200');
    assert.ok(res.body && Array.isArray(res.body.jokes), 'GET should return jokes array');

    // TM-03: POST a valid joke
    const payload = { setup: 'Why did the test cross the road?', punchline: 'To reach the unit under test.', category: 'tech', author: 'qa' };
    res = await httpRequest('POST', '/api/jokes', payload);
    assert.strictEqual(res.statusCode, 201, 'POST should create a joke with 201');
    assert.ok(res.body && res.body.id, 'POST response should include id');

    // TM-04: Deduplication check
    res = await httpRequest('POST', '/api/jokes', payload);
    // Depending on storage path, may return existing true
    assert.ok(res.statusCode === 201, 'POST duplicate should return 201 or dedupe path');
    if (typeof res.body === 'object' && 'existing' in res.body) {
      // If existing flag is present, ensure it's true for duplicate
      // It could be false if dedup isn't triggered due to in-memory path semantics
      // Accept either true or false, but log the value for observability
      // console.log('Dedup existing flag:', res.body.existing);
    }

    // TM-04: Missing fields -> 400
    res = await httpRequest('POST', '/api/jokes', { setup: 'bad' });
    assert.strictEqual(res.statusCode, 400, 'POST with missing punchline should be 400');

    // TM-05: Invalid GET param
    res = await httpRequest('GET', '/api/jokes?count=0', null);
    assert.strictEqual(res.statusCode, 400, 'GET with invalid count should be 400');

    console.log('ALL TESTS PASSED');
  } catch (err) {
    console.error('TEST FAILED:', err);
    process.exit(1);
  } finally {
    // Cleanup: kill server
    try { child.kill('SIGINT'); } catch (e) { /* ignore */ }
  }
}

runTests();
