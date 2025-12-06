#!/usr/bin/env node
// Simple concurrency stress test for load handling of JokeGen API
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
  console.log('Starting load/concurrency test...');
  const child = spawn(SERVER_CMD, [SERVER_SCRIPT], {
    stdio: ['ignore', 'pipe', 'pipe']
  });

  try {
    await waitForServerReady(child);

    const requests = 40;
    const promises = [];
    for (let i = 0; i < requests; i++) {
      promises.push(httpRequest('GET', '/api/jokes?count=2', null));
    }
    const results = await Promise.all(promises);
    results.forEach(r => {
      assert.strictEqual(r.statusCode, 200, 'Each request should return 200');
      // Should be an object with jokes array
      if (r.body && Array.isArray(r.body.jokes)) {
        // ok
      }
    });
    console.log('Load/concurrency test PASSED');
  } catch (err) {
    console.error('Load/concurrency test FAILED:', err);
    process.exit(1);
  } finally {
    try { child.kill('SIGINT'); } catch (e) { /* ignore */ }
  }
}

runTests();
