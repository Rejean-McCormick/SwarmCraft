const http = require('http');
const { router } = require('./routes');

const port = 3101;
const server = http.createServer((req, res) => {
  if (req.method === 'POST' && req.url === '/echo') {
    let body = '';
    req.on('data', chunk => { body += chunk; });
    req.on('end', () => {
      let parsed = {};
      try { parsed = JSON.parse(body || '{}'); } catch (e) { parsed = {}; }
      req.body = parsed;
      router(req, res);
    });
  } else {
    res.statusCode = 404; res.end('Not Found');
  }
});
console.log('Beta module ready on', port);
server.listen(port);
