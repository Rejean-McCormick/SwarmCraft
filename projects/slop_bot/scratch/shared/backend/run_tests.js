// Simple test runner for the security tests

const { execSync } = require('child_process');
try {
  // Execute test file in a separate node process to isolate
  execSync('node shared/backend/tests/test_security.js', { stdio: 'inherit' });
  console.log('Tests completed.');
} catch (e) {
  console.error('Tests failed.');
  process.exit(1);
}
