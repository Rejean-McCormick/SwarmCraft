// Smoke test to ensure CommonJS module system remains in backend
const { execSync } = require('child_process');

test('CommonJS module system check runs', () => {
  // Run the checker script; expect exit code 0
  try {
    execSync('node ./scripts/check_module_system.js', { stdio: 'inherit' });
  } catch (e) {
    throw new Error('Module system check failed: ' + e.message);
  }
});
