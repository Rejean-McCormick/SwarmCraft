#!/usr/bin/env node
// Integration test for MVP v2 batch endpoints (POST /api/jokes/batches, GET /api/jokes/batches/:batchId/status)
// This test starts the v2 API server and exercises the batch endpoints end-to-end.

const http = require('http');
const https = require('https');
const path = require('path');
const fs = require('fs');

// Helper to perform a JSON POST
function postJson(host, port, pathUrl, payload) {
  return new Promise((resolve, reject) => {
    const data = Buffer.from(JSON.stringify(payload || {}));
    const options = {
      host,
      port,
      path: pathUrl,
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': data.length
      }
    };
    const req = http.request(options, (res) => {
      let body = '';
      res.setEncoding('utf8');
      res.on('data', (chunk) => (body += chunk));
      res.on('end', () => {
        let parsed;
        try {
          parsed = body ? JSON.parse(body) : {};
        } catch (e) {
          // If body isn't JSON, still resolve with raw
          parsed = { raw: body };
        }
        resolve({ statusCode: res.statusCode, body: parsed });
      });
    });
    req.on('error', (e) => reject(e));
    req.write(data);
    req.end();
  });
}

// Helper to perform a JSON GET
function getJson(host, port, pathUrl) {
  return new Promise((resolve, reject) => {
    const options = {
      host,
      port,
      path: pathUrl,
      method: 'GET',
      headers: {
        'Accept': 'application/json'
      }
    };
    const req = http.request(options, (res) => {
      let body = '';
      res.setEncoding('utf8');
      res.on('data', (chunk) => (body += chunk));
      res.on('end', () => {
        let parsed;
        try {
          parsed = body ? JSON.parse(body) : {};
        } catch (e) {
          parsed = { raw: body };
        }
        resolve({ statusCode: res.statusCode, body: parsed });
      });
    });
    req.on('error', (e) => reject(e));
    req.end();
  });
}

// Start the v2 MVP server via require('./../src/joke_gen_api_v2.js')
async function startV2Server() {
  // Try to use the exported API to start a server
  const mod = require('../src/joke_gen_api_v2.js');
  // Support multiple possible export styles
  if (typeof mod.createApp === 'function') {
    const appBundle = mod.createApp();
    // If createApp returns { app, startServer }
    if (appBundle && typeof appBundle.startServer === 'function') {
      const server = await appBundle.startServer(0);
      const port = server.address().port;
      const host = '127.0.0.1';
      return { host, port, server };
    }
    // If it returns { app, listen }
    if (appBundle && appBundle.app && typeof appBundle.app.listen === 'function') {
      const port = 0;
      const server = appBundle.app.listen(port, () => {});
      // Obtain actual port after listen
      const actualPort = server.address().port;
      return { host: '127.0.0.1', port: actualPort, server };
    }
  }
  // Fallback: assume module exports an express app as module.exports = app
  if (mod && mod.app && typeof mod.app.listen === 'function') {
    const server = mod.app.listen(0);
    const actualPort = server.address().port;
    return { host: '127.0.0.1', port: actualPort, server };
  }
  throw new Error('Unable to start v2 MVP server from module exports');
}

async function run() {
  console.log('Starting MVP v2 batch endpoints integration test...');
  const { host, port, server } = await startV2Server();
  console.log(`v2 MVP server listening on ${host}:${port}`);

  // 1) Valid POST /api/jokes/batches
  const post1 = await postJson(host, port, '/api/jokes/batches', {
    batchSize: 3,
    prompts: ['alpha', 'beta', 'gamma']
  });
  if (post1.statusCode !== 202) {
    console.error('FAILED: POST /api/jokes/batches status', post1.statusCode, 'body', post1.body);
    process.exitCode = 1;
  }
  const batchId = post1.body && post1.body.batchId;
  if (!batchId) {
    console.error('FAILED: POST did not return batchId. Body:', post1.body);
    process.exitCode = 1;
  }

  // 2) Poll status until completed/failed
  let finalStatus = null;
  const maxPolls = 60;
  for (let i = 0; i < maxPolls; i++) {
    const statusRes = await getJson(host, port, `/api/jokes/batches/${batchId}/status`);
    if (statusRes.statusCode !== 200) {
      console.warn('Warning: status endpoint not ready yet, code', statusRes.statusCode);
    }
    const s = statusRes.body || {};
    finalStatus = s.status;
    if (finalStatus === 'completed' || finalStatus === 'failed') {
      console.log('Batch status reached:', finalStatus);
      break;
    }
    await new Promise((r) => setTimeout(r, 500));
  }

  if (finalStatus !== 'completed' && finalStatus !== 'failed') {
    console.error('FAILED: Batch did not reach terminal state in time. Last status:', finalStatus);
    process.exitCode = 1;
  }

  // 3) INVALID payload tests
  const postInvalid1 = await postJson(host, port, '/api/jokes/batches', {});
  if (postInvalid1.statusCode !== 400) {
    console.error('FAILED: POST /api/jokes/batches with empty payload should 400, got', postInvalid1.statusCode);
    process.exitCode = 1;
  }
  const postInvalid2 = await postJson(host, port, '/api/jokes/batches', { batchSize: 0 });
  if (postInvalid2.statusCode !== 400) {
    console.error('FAILED: POST /api/jokes/batches with batchSize=0 should 400, got', postInvalid2.statusCode);
    process.exitCode = 1;
  }

  // Clean up
  server.close(() => {
    console.log('v2 MVP test server closed.');
  });
  if (process.exitCode === undefined) process.exitCode = 0;
  process.exit(process.exitCode || 0);
}

run().catch((err) => {
  console.error('Integration test failed with error:', err);
  process.exit(1);
});
