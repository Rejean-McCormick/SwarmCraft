// Simple mock API server (Express-like) for local testing
const http = require('http');
const url = require('url');
const port = process.env.MOCK_API_PORT || 3001;

const data = {
  welcome: { message: 'Welcome to Anchor-First' },
  features: [
    { id: 'feature-1', title: 'Fast & Lightweight' },
    { id: 'feature-2', title: 'Accessible' },
    { id: 'feature-3', title: 'Responsive' },
  ],
};

function respond(res, body, status=200, headers={}){
  res.writeHead(status, { 'Content-Type': 'application/json', ...headers });
  res.end(JSON.stringify(body));
}

const server = http.createServer((req, res)=>{
  const u = url.parse(req.url, true);
  if(u.pathname === '/api/anchors/welcome'){
    respond(res, data.welcome);
  } else if(u.pathname === '/api/anchors/features'){
    respond(res, { items: data.features });
  } else {
    respond(res, { ok: false, error: 'unknown' }, 404);
  }
});

server.listen(port, ()=>{
  console.log(`Mock API listening on http://localhost:${port}`);
});
