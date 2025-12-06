#!/usr/bin/env node
// Lightweight batch-endpoint integration test for JokeGen API
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
  console.log('Starting Batch integration tests...');
  const child = spawn(SERVER_CMD, [SERVER_SCRIPT], {
    stdio: ['ignore', 'pipe', 'pipe']
  });

  try {
    await waitForServerReady(child);

    // 1) Create a batch
    const batchPayload = { batchSize: 4, prompts: ['seedA', 'seedB'] };
    let res = await httpRequest('POST', '/api/jokes/batches', batchPayload);
    assert.strictEqual(res.statusCode, 202, 'Batch creation should return 202');
    const batchId = res.body && res.body.batchId ? res.body.batchId : null;
    assert.ok(batchId, 'Response should include batchId');

    // 2) Poll status until completion
    let statusRes = null;
    let attempts = 0;
    while (attempts < 60) {
      statusRes = await httpRequest('GET', `/api/jokes/batches/${batchId}/status`, null);
      if (statusRes.statusCode === 200 && statusRes.body) {
        const s = statusRes.body.status;
        if (s === 'completed') break;
        if (s === 'failed') throw new Error('Batch failed on processing');
      }
      await new Promise(r => setTimeout(r, 250));
      attempts++;
    }
    assert.ok(statusRes && statusRes.body, 'Status response should not be empty');
    assert.strictEqual(statusRes.body.status, 'completed', 'Batch should complete');
    const createdIds = statusRes.body.createdIds;
    assert.ok(Array.isArray(createdIds), 'createdIds should be an array');
    assert.strictEqual(createdIds.length, 4, 'Batch should create 4 joke IDs');

    // 3) Verify jokes exist in /api/jokes (count equals batchSize)
    res = await httpRequest('GET', '/api/jokes?count=4', null);
    assert.strictEqual(res.statusCode, 200, 'GET jokes after batch should succeed');
    assert.ok(res.body && Array.isArray(res.body.jokes), 'Should return jokes array');
    assert.strictEqual(res.body.jokes.length, 4, 'Should return 4 jokes');

    // 4) Invalid batch payload -> 400
    res = await httpRequest('POST', '/api/jokes/batches', { batchSize: 0 });
    assert.strictEqual(res.statusCode, 400, 'Invalid batchSize should return 400');

    console.log('Batch integration tests PASSED');
  } catch (err) {
    console.error('Batch integration test FAILED:', err);
    process.exit(1);
  } finally {
    try { child.kill('SIGINT'); } catch (e) { /* ignore */ }
  }
}

runTests();
