#!/usr/bin/env node
// Batch endpoint QA test: create batch, poll status, verify jokes exist
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
          // leave raw
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
  console.log('Starting Batch Endpoints QA test...');
  const child = spawn(SERVER_CMD, [SERVER_SCRIPT], {
    stdio: ['ignore', 'pipe', 'pipe']
  });

  try {
    await waitForServerReady(child);

    // 1) Create a batch
    const batchPayload = { batchSize: 3, prompts: ['seedA', 'seedB'] };
    let res = await httpRequest('POST', '/api/jokes/batches', batchPayload);
    assert.strictEqual(res.statusCode, 202, 'Batch creation should return 202');
    const batchId = res.body && res.body.batchId ? res.body.batchId : null;
    assert.ok(batchId, 'Response should include batchId');

    // 2) Poll status until completion
    let statusRes = null;
    let attempts = 0;
    while (attempts < 30) {
      statusRes = await httpRequest('GET', `/api/jokes/batches/${batchId}/status`, null);
      if (statusRes.statusCode === 200 && statusRes.body) {
        const s = statusRes.body.status;
        if (s === 'completed') break;
        if (s === 'failed') throw new Error('Batch failed on processing');
      }
      await new Promise(r => setTimeout(r, 200));
      attempts++;
    }
    assert.ok(statusRes && statusRes.body, 'Status response should exist');
    assert.strictEqual(statusRes.body.status, 'completed');
    const createdIds = statusRes.body.createdIds;
    assert.ok(Array.isArray(createdIds), 'createdIds should be an array');
    assert.strictEqual(createdIds.length, 3, 'Batch should create 3 joke IDs');

    // 3) Verify jokes exist in /api/jokes?count=3
    res = await httpRequest('GET', '/api/jokes?count=3', null);
    assert.strictEqual(res.statusCode, 200, 'GET jokes should succeed');
    assert.ok(res.body.jokes && Array.isArray(res.body.jokes));
    assert.strictEqual(res.body.jokes.length, 3, 'Should fetch 3 jokes');

    // 4) Invalid batch payload
    res = await httpRequest('POST', '/api/jokes/batches', { batchSize: 0 });
    assert.strictEqual(res.statusCode, 400, 'Invalid batch should return 400');

    console.log('Batch Endpoints QA tests PASSED');
  } catch (err) {
    console.error('Batch Endpoints QA tests FAILED:', err);
    process.exit(1);
  } finally {
    try { child.kill('SIGINT'); } catch (e) { /* ignore */ }
  }
}

runTests();
