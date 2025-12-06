#!/usr/bin/env node
/**
 * Codey Splitter - generates per-module microservice skeletons from a spec.
 *
 * This implementation creates per-module servers using a lightweight HTTP
 * approach suitable for CI/test environments.
 *
 * Spec format (JSON):
 * {
 *   "modules": [
 *     {
 *       "name": "shop",
 *       "apis": [
 *         { "path": "/items", "method": "GET" },
 *         { "path": "/buy",  "method": "POST" }
 *       ]
 *     },
 *     ... more modules ...
 *   ]
 * }
 *
 * Output (under scratch/shared/src/modules/<moduleName>):
 *   index.js            - tiny HTTP server launcher
 *   routes.js           - router with API endpoints
 *   module.config.json   - config describing APIs
 *   package.json         - minimal package (no deps; not strictly required)
 *   README.md            - module overview
 *
 * Notes:
 *   - Basic validation to prevent path traversal or invalid module names.
 *   - Ports start at 3100 and increment by module index.
 */

const fs = require('fs');
const path = require('path');

function log(msg) { console.log(`[splitter] ${msg}`); }

function safeModuleName(name) {
  // Allow alphanumeric and underscore only
  if (!name || typeof name !== 'string') return null;
  const ok = /^[A-Za-z0-9_]+$/.test(name);
  return ok ? name : null;
}

function ensureDir(p) {
  if (!fs.existsSync(p)) {
    fs.mkdirSync(p, { recursive: true });
  }
}

function writeJson(p, obj) {
  fs.writeFileSync(p, JSON.stringify(obj, null, 2) + '\n', 'utf8');
}

function main() {
  const args = process.argv.slice(2);
  let specPath = null;
  for (let i = 0; i < args.length; i++) {
    if ((args[i] === '--spec' || args[i] === '-s') && i + 1 < args.length) {
      specPath = args[i+1];
      break;
    }
  }
  if (!specPath) {
    log('No spec provided. Use --spec <path> to specify the spec JSON.');
    process.exit(2);
  }

  // Base path: scratch/shared
  const baseRoot = path.resolve(__dirname, '..'); // scratch/shared
  const modulesRoot = path.join(baseRoot, 'src', 'modules');
  ensureDir(modulesRoot);

  let specRaw;
  try {
    specRaw = fs.readFileSync(specPath, 'utf8');
  } catch (e) {
    log(`Failed to read spec at ${specPath}: ${e.message}`);
    process.exit(3);
  }

  let spec;
  try {
    spec = JSON.parse(specRaw);
  } catch (e) {
    log(`Invalid JSON in spec: ${e.message}`);
    process.exit(4);
  }

  // Basic spec validation
  if (!spec || !Array.isArray(spec.modules)) {
    log('Spec must contain an array "modules".');
    process.exit(5);
  }

  const modules = spec.modules;
  if (modules.length === 0) {
    log('No modules defined in spec.');
    process.exit(6);
  }

  const created = [];
  modules.forEach((m, idx) => {
    const rawName = m && typeof m.name === 'string' ? m.name : null;
    const name = safeModuleName(rawName);
    if (!name) {
      log(`Skipping invalid module name: ${rawName}`);
      return;
    }

    const modDir = path.join(modulesRoot, name);
    ensureDir(modDir);

    // config
    const configPath = path.join(modDir, 'module.config.json');
    const config = {
      module: name,
      apis: Array.isArray(m.apis) ? m.apis : []
    };
    writeJson(configPath, config);

    // index.js - small HTTP server
    const port = 3100 + idx; // simple port allocation
    const indexPath = path.join(modDir, 'index.js');

    const indexCode = `const http = require('http');
const { createRouter } = require('./routes');
const apiSpec = require('./module.config.json');
const MODULE_NAME = '${name}';

const router = createRouter(MODULE_NAME, apiSpec);

const PORT = ${port};

const server = http.createServer((req, res) => {
  const key = (req.method || 'GET') + ' ' + (req.url || '/');
  // Direct match (path + method)
  const handler = router[key];
  if (handler) {
    return handler(req, res);
  }
  // Try path without query string
  const cleanPath = req.url ? req.url.split('?')[0] : '/';
  const fallback = router[req.method + ' ' + cleanPath];
  if (fallback) {
    return fallback(req, res);
  }
  res.statusCode = 404;
  res.setHeader('Content-Type', 'application/json');
  res.end(JSON.stringify({ module: MODULE_NAME, path: cleanPath, error: 'not_found' }));
});

server.listen(PORT, () => {
  console.log(`Module ${MODULE_NAME} listening on ${PORT}`);
});
`;

    fs.writeFileSync(indexPath, indexCode, 'utf8');

    // routes.js
    const routesPath = path.join(modDir, 'routes.js');
    const routesCode = `function createRouter(moduleName, apiSpec) {
  const router = {};
  const apis = Array.isArray(apiSpec && apiSpec.apis) ? apiSpec.apis : [];
  for (const api of apis) {
    const method = (api.method || 'GET').toUpperCase();
    const path = api.path || '/';
    const key = method + ' ' + path;
    router[key] = (req, res) => {
      if (method === 'POST' || method === 'PUT' || method === 'PATCH') {
        let body = '';
        // safe body size limit: 1MB
        req.on('data', chunk => {
          body += chunk;
          if (body.length > 1024 * 1024) {
            req.destroy();
          }
        });
        req.on('end', () => {
          let payload = {};
          try { payload = body ? JSON.parse(body) : {}; } catch { payload = {}; }
          res.setHeader('Content-Type', 'application/json');
          res.end(JSON.stringify({ module: moduleName, api: path, method, received: payload }));
        });
      } else {
        res.setHeader('Content-Type', 'application/json');
        res.end(JSON.stringify({ module: moduleName, api: path, method }));
      }
    };
  }
  return router;
}

module.exports = { createRouter };
`;
    fs.writeFileSync(routesPath, routesCode, 'utf8');

    // module.config.json should reflect apis; already written
    const genPackagePath = path.join(modDir, 'package.json');
    const packageJson = {
      name: name.toLowerCase(),
      version: '1.0.0',
      description: `Module ${name} microservice scaffold (no deps)`,
      main: 'index.js',
      private: true
    };
    fs.writeFileSync(genPackagePath, JSON.stringify(packageJson, null, 2) + '\n', 'utf8');

    // README
    const readmePath = path.join(modDir, 'README.md');
    const readme = `# Module: ${name}\n\nThis is a minimal per-module microservice scaffold generated by the splitter. It exposes the APIs defined in module.config.json using a tiny Node HTTP server.\n`;
    fs.writeFileSync(readmePath, readme, 'utf8');

    created.push({ name, port, path: modDir });
    log(`Created module scaffold: ${name} at ${modDir} (port ${port})`);
  });

  if (created.length === 0) {
    log('No valid modules were created.');
    process.exit(0);
  }
}

if (require.main === module) {
  main();
}
