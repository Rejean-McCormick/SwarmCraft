const http = require('http');
const assert = require('assert');

function request(opts, body) {
  return new Promise((resolve, reject) => {
    const req = http.request(opts, (res) => {
      let data = '';
      res.on('data', (chunk) => { data += chunk; });
      res.on('end', () => {
        resolve({ statusCode: res.statusCode, body: data });
      });
    });
    req.on('error', reject);
    if (body) req.write(JSON.stringify(body));
    req.end();
  });
}

async function run() {
  // Ensure splitter run already happened and modules exist
  // Test testmodAlpha GET /ping
  let r = await request({ hostname: 'localhost', port: 3100, path: '/ping', method: 'GET' });
  const objA = JSON.parse(r.body);
  assert.ok(objA.module === 'testmodAlpha' && objA.api === '/ping' && objA.method === 'GET');

  // Test testmodBeta POST /echo
  r = await request({ hostname: 'localhost', port: 3101, path: '/echo', method: 'POST', headers: { 'Content-Type': 'application/json' } }, { hello: 'world' });
  const objB = JSON.parse(r.body);
  assert.ok(objB.module === 'testmodBeta' && objB.api === '/echo' && objB.method === 'POST' && objB.received.hello === 'world');

  // 404 test
  r = await request({ hostname: 'localhost', port: 3100, path: '/notfound', method: 'GET' });
  assert.strictEqual(r.statusCode, 404);

  console.log('QA plan tests: PASS');
}

run().catch(err => {
  console.error('QA plan tests: FAIL', err);
  process.exit(1);
});
