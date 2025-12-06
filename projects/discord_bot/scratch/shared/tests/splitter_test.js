const fs = require('fs');
const path = require('path');
const assert = require('assert');
const { execSync } = require('child_process');

function base() {
  return path.resolve(__dirname, '..', '..'); // scratch/shared
}

function ensureCleanModule(name) {
  const modPath = path.join(base(), 'src', 'modules', name);
  if (fs.existsSync(modPath)) {
    // remove recursively
    fs.rmSync(modPath, { recursive: true, force: true });
  }
}

function readJson(fp) {
  return JSON.parse(fs.readFileSync(fp, 'utf8'));
}

function run() {
  // Prepare test spec
  const testSpecDir = path.join(base(), 'qa', 'specs');
  if (!fs.existsSync(testSpecDir)) {
    fs.mkdirSync(testSpecDir, { recursive: true });
  }
  const testSpecPath = path.join(testSpecDir, 'qa_split_spec_test.json');
  const spec = {
    modules: [
      { name: 'testmodAlpha', apis: [ { path: '/ping', method: 'GET' } ] },
      { name: 'testmodBeta', apis: [ { path: '/echo', method: 'POST' } ] }
    ]
  };
  fs.writeFileSync(testSpecPath, JSON.stringify(spec, null, 2) + '\n', 'utf8');

  // Ensure clean state
  ensureCleanModule('testmodAlpha');
  ensureCleanModule('testmodBeta');

  // Run splitter
  try {
    execSync(`node scratch/shared/tools/split_codebase_agent.js --spec ${testSpecPath}`, { stdio: 'inherit' });
  } catch (e) {
    console.error('Splitter failed to run', e);
    process.exit(2);
  }

  // Validate outputs
  const modA = path.join(base(), 'src', 'modules', 'testmodAlpha');
  const modB = path.join(base(), 'src', 'modules', 'testmodBeta');

  assert.ok(fs.existsSync(modA), 'module testmodAlpha should be created');
  assert.ok(fs.existsSync(modB), 'module testmodBeta should be created');

  // Check files in modA
  const cfgA = path.join(modA, 'module.config.json');
  const idxA = path.join(modA, 'index.js');
  const routeA = path.join(modA, 'routes.js');
  const pkgA = path.join(modA, 'package.json');
  const readmeA = path.join(modA, 'README.md');

  [cfgA, idxA, routeA, pkgA, readmeA].forEach(p => {
    assert.ok(fs.existsSync(p), `Expected file ${p} to exist`);
  });

  const cfgAObj = readJson(cfgA);
  assert.equal(cfgAObj.module, 'testmodAlpha');
  assert.ok(Array.isArray(cfgAObj.apis));
  assert.equal(cfgAObj.apis.length, 1);
  assert.equal(cfgAObj.apis[0].path, '/ping');
  assert.equal(cfgAObj.apis[0].method, 'GET');

  // Check index.js contains http server and port
  const idxAContent = fs.readFileSync(idxA, 'utf8');
  assert.ok(idxAContent.includes('http.createServer') || idxAContent.includes('require(\'http\')'));
  assert.ok(idxAContent.includes('MODULE_NAME') || idxAContent.includes('Module'));

  // Check routes.js exports
  const routeAContent = fs.readFileSync(routeA, 'utf8');
  assert.ok(routeAContent.includes('module.exports'));

  const pkgAObj = readJson(pkgA);
  assert.ok(pkgAObj.name);
  // Read README
  const readmeAContent = fs.readFileSync(readmeA, 'utf8');
  assert.ok(readmeAContent.includes('Module testmodAlpha'));

  // Similar checks for modB
  const cfgB = path.join(modB, 'module.config.json');
  const idxB = path.join(modB, 'index.js');
  const routeB = path.join(modB, 'routes.js');
  const pkgB = path.join(modB, 'package.json');
  const readmeB = path.join(modB, 'README.md');
  [cfgB, idxB, routeB, pkgB, readmeB].forEach(p => {
    assert.ok(fs.existsSync(p), `Expected file ${p} to exist`);
  });
  const cfgBObj = readJson(cfgB);
  assert.equal(cfgBObj.module, 'testmodBeta');
  assert.equal(cfgBObj.apis[0].path, '/echo');
  assert.equal(cfgBObj.apis[0].method, 'POST');

  const readmeBContent = fs.readFileSync(readmeB, 'utf8');
  assert.ok(readmeBContent.includes('Module testmodBeta'));

  console.log('Splitter tests: PASS');
}

try {
  run();
} catch (err) {
  console.error('Splitter tests: FAIL', err);
  process.exit(3);
}
