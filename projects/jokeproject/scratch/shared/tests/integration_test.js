const http = require('http');
const assert = require('assert');

function httpRequest(method, path, data) {
  return new Promise((resolve, reject) => {
    const options = {
      hostname: 'localhost',
      port: 8080,
      path: path,
      method: method,
      headers: {
        'Content-Type': 'application/json'
      }
    };
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

async function run() {
  // Start API server
  const { spawn } = require('child_process');
  const proc = spawn('node', ['server.js'], { cwd: 'scratch/shared', stdio: 'inherit' });
  await new Promise(r => setTimeout(r, 1000));
  const r1 = await httpRequest('GET', '/api/jokes?count=2');
  console.log('GET jokes:', r1.statusCode);
  const r2 = await httpRequest('GET', '/api/jokes?count=1');
  console.log('GET jokes one:', r2.statusCode);

  // Basic POST tests
  const jokeA = { setup: 'What runs but never walks?', punchline: 'A refrigerator.' };
  let res = await httpRequest('POST', '/api/jokes', jokeA);
  console.log('POST jokeA:', res.statusCode);
  const idA = res.body && res.body.id;

  const jokeB = { setup: 'Why did the tomato blush?', punchline: 'Because it saw the salad dressing!' };
  res = await httpRequest('POST', '/api/jokes', jokeB);
  console.log('POST jokeB:', res.statusCode);
  const idB = res.body && res.body.id;

  // Duplicate post for dedupe check
  res = await httpRequest('POST', '/api/jokes', jokeA);
  console.log('POST duplicate jokeA:', res.statusCode);
  const existing = res.body && res.body.existing;
  if (existing) {
    console.log('Duplicate detected as expected');
  }

  // Validation tests: missing fields -> expect 400
  res = await httpRequest('POST', '/api/jokes', { setup: 'Incomplete payload' });
  console.log('POST invalid (missing punchline):', res.statusCode);
  res = await httpRequest('POST', '/api/jokes', { punchline: 'Only punchline' });
  console.log('POST invalid (missing setup):', res.statusCode);

  // Get again to ensure API still works
  res = await httpRequest('GET', '/api/jokes?count=2');
  console.log('GET jokes after ops:', res.statusCode);

  // Cleanup: stop server
  proc.kill();
  console.log('Test sequence completed.');
}

run().catch(e => {
  console.error('Test failed', e);
  process.exit(1);
});
