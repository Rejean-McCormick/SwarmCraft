const http = require('http');
const { router } = require('./routes');

const port = 3100;

const server = http.createServer((req, res) => {
  if (req.method === 'GET' && req.url === '/ping') {
    router(req, res, () => {});
  } else {
    res.statusCode = 404; res.end('Not Found');
  }
});
console.log('Alpha module ready on', port);
server.listen(port);
