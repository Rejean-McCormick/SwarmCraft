// Simple load test for Educational Anatomy Prompt Generator API
// This script performs a configurable number of POST /prompts requests to create prompts
// and reports success/failure counts. It supports basic concurrency control.

const http = require('http');
const https = require('https');
const url = require('url');

const TARGET = process.env.API_BASE_URL || 'http://localhost:3000';
const NUM_REQUESTS = parseInt(process.env.N_REQS) || 50;
const CONCURRENCY = parseInt(process.env.N_CONCURRENCY) || 5;
const ADMIN_TOKEN = process.env.ADMIN_TOKEN || '';

function doPost(seed) {
  return new Promise((resolve, reject) => {
    const parsed = url.parse(TARGET + '/prompts');
    const data = JSON.stringify({ seed: seed });
    const options = {
      hostname: parsed.hostname,
      port: parsed.port || (parsed.protocol === 'https:' ? 443 : 80),
      path: parsed.path,
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(data),
      },
    };
    const lib = parsed.protocol === 'https:' ? https : http;
    const req = lib.request(options, (res) => {
      let body = '';
      res.on('data', (chunk) => body += chunk);
      res.on('end', () => {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve({ code: res.statusCode, body: body || '{}' });
        } else {
          resolve({ code: res.statusCode, body: body || '{}' });
        }
      });
    });
    req.on('error', (e) => reject(e));
    req.write(data);
    req.end();
  });
}

async function run() {
  let inFlight = 0;
  let started = 0;
  let success = 0;
  let failures = 0;

  function next() {
    if (started >= NUM_REQUESTS) return;
    if (inFlight >= CONCURRENCY) return;
    const seed = 1000 + started; // varied seeds
    started++;
    inFlight++;
    doPost(seed).then((r) => {
      inFlight--;
      if (r.code >= 200 && r.code < 300) success++; else failures++;
      if (started < NUM_REQUESTS || inFlight > 0) next();
    }).catch((err) => {
      inFlight--;
      failures++;
      if (started < NUM_REQUESTS || inFlight > 0) next();
    });
  }

  // kick off initial batch
  for (let i = 0; i < Math.min(CONCURRENCY, NUM_REQUESTS); i++) next();

  // wait for completion
  while (started < NUM_REQUESTS || inFlight > 0) {
    await new Promise(r => setTimeout(r, 100));
  }
  console.log(`Load test finished. Started=${started}, Success=${success}, Failures=${failures}`);
}

run().catch((e) => {
  console.error('Load test failed:', e);
  process.exit(1);
});
