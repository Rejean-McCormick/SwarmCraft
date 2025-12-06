'use strict';

// Lightweight REST client for inter-service communication between modular services.
// Usage:
// const { createClient } = require('./infra/apiClient');
// const client = createClient('http://localhost:3100');
// client.request('GET', '/ping', null, {}).then(resp => ...)

const http = require('http');
const https = require('https');
const url = require('url');

function normalizeUrl(base) {
  try {
    const u = new URL(base);
    return u;
  } catch (e) {
    // Fallback for old Node.js versions
    return url.parse(base);
  }
}

function createClient(baseUrl) {
  if (!baseUrl) throw new Error('baseUrl is required');
  const u = normalizeUrl(baseUrl);
  const isHttps = (u.protocol || 'http:').startsWith('https');
  const port = u.port ? Number(u.port) : (isHttps ? 443 : 80);
  const host = u.hostname || 'localhost';
  const basePath = u.pathname || '/';

  async function request(method, path, body = null, headers = {}) {
    const fullPath = basePath.endsWith('/') ? basePath.slice(0, -1) + path : basePath + path;
    const options = {
      hostname: host,
      port: port,
      path: fullPath,
      method: (method || 'GET').toUpperCase(),
      headers: Object.assign({}, headers)
    };
    let bodyString = null;
    if (body && (typeof body === 'object')) {
      bodyString = JSON.stringify(body);
      if (!options.headers['Content-Type']) {
        options.headers['Content-Type'] = 'application/json';
      }
    } else if (typeof body === 'string') {
      bodyString = body;
    }
    if (bodyString) {
      options.headers['Content-Length'] = Buffer.byteLength(bodyString);
    }

    const transport = isHttps ? https : http;
    return new Promise((resolve, reject) => {
      const req = transport.request(options, (res) => {
        let data = '';
        res.setEncoding('utf8');
        res.on('data', (chunk) => { data += chunk; });
        res.on('end', () => {
          resolve({ statusCode: res.statusCode, headers: res.headers, body: data });
        });
      });
      req.on('error', (err) => reject(err));
      if (bodyString) req.write(bodyString);
      req.end();
    });
  }

  return { request };
}

module.exports = { createClient };
