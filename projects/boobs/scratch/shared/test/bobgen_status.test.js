// BobGen Status API scaffold tests (no external test runner required)
const http = require('http');
const assert = require('assert');
const path = require('path');

// Resolve the bobgen_status.js path robustly
const appPath = path.resolve(__dirname, '..', 'src', 'bobgen_status.js');
const app = require(appPath);

function request(port, path) {
  return new Promise((resolve, reject) => {
    const req = http.get({ hostname: '127.0.0.1', port, path, agent: false }, (res) => {
      let data = '';
      res.on('data', (chunk) => (data += chunk));
      res.on('end', () => {
        resolve({ statusCode: res.statusCode, body: data });
      });
    });
    req.on('error', (e) => reject(e));
  });
}

(async () => {
  const server = app.listen(0, async () => {
    const port = server.address().port;
    try {
      const r1 = await request(port, '/bobgen/status');
      if (r1.statusCode !== 200) throw new Error('GET /bobgen/status failed with ' + r1.statusCode);
      const list = JSON.parse(r1.body);
      if (!Array.isArray(list)) throw new Error('Body is not an array');
      if (list.length > 0) {
        const first = list[0];
        if (first.id === undefined) throw new Error('Missing id on first item');
      }

      const r2 = await request(port, '/bobgen/status/1');
      if (r2.statusCode === 200) {
        const item = JSON.parse(r2.body);
        if (item.id !== '1') throw new Error('Incorrect id in response');
      } else if (r2.statusCode === 404) {
        // acceptable if item missing
      } else {
        throw new Error('Unexpected status for /bobgen/status/1: ' + r2.statusCode);
      }

      await new Promise((r) => server.close(r));
      console.log('BobGen status API tests passed');
      process.exit(0);
    } catch (err) {
      await new Promise((r) => server.close(r));
      console.error('BobGen status API tests failed:', err.message || err);
      process.exit(1);
    }
  });
})().catch((e) => {
  console.error('Startup error', e);
  process.exit(1);
});
