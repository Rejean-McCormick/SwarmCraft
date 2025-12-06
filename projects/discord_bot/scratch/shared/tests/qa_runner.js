#!/usr/bin/env node
/**
 * QA Runner orchestrator:
 * - Runs the splitter against qa_split_spec.json
 * - Boots two module servers (testmodAlpha on 3100, testmodBeta on 3101)
 * - Runs the QA plan tests
 * - Tears down servers
 */

const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

async function run(cmd, args, opts = {}) {
  return new Promise((resolve, reject) => {
    const p = spawn(cmd, args, { stdio: 'inherit', shell: true, ...opts });
    p.on('error', reject);
    p.on('close', (code) => resolve(code));
  });
}

async function main() {
  const base = path.resolve(__dirname, '..'); // scratch/shared
  const specPath = path.join(base, 'qa', 'specs', 'qa_split_spec.json');

  // Step 1: Run splitter
  console.log('QA Runner: Starting splitter...');
  const splitterCode = path.join(base, 'tools', 'split_codebase_agent.js');
  const exitSplitter = await run('node', [splitterCode, '--spec', specPath]);
  if (exitSplitter !== 0) {
    console.error('Splitter failed. Aborting QA run.');
    process.exit(exitSplitter || 1);
  }

  // Step 2: Start module servers
  console.log('QA Runner: Starting module servers...');
  const alphaIndex = path.join(base, 'src', 'modules', 'testmodAlpha', 'index.js');
  const betaIndex = path.join(base, 'src', 'modules', 'testmodBeta', 'index.js');

  const serverAlpha = spawn('node', [alphaIndex], { stdio: 'inherit' });
  const serverBeta = spawn('node', [betaIndex], { stdio: 'inherit' });

  // Give servers a moment to start
  await new Promise(r => setTimeout(r, 800));

  // Step 3: Run QA plan tests
  console.log('QA Runner: Running QA plan tests...');
  const qaTestsCode = path.join(base, 'tests', 'qa_plan_tests.js');
  const exitTests = await run('node', [qaTestsCode], { cwd: base });

  // Step 4: Tear down
  console.log('QA Runner: Shutting down servers...');
  serverAlpha.kill('SIGTERM');
  serverBeta.kill('SIGTERM');

  // Wait for servers to exit
  await new Promise(resolve => {
    serverAlpha.on('exit', () => resolve());
  });
  await new Promise(resolve => {
    serverBeta.on('exit', () => resolve());
  });

  process.exit(exitTests || 0);
}

main().catch(err => {
  console.error('QA Runner: FAIL', err);
  process.exit(1);
});
