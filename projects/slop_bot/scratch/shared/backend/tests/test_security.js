// Minimal unit tests for security utilities (Node.js, simple assertions)

const assert = require('assert');
const { redactSecretsInObject, sanitizePromptInput, exponentialBackoff } = require('../src/utils');

function testRedactSecretsInObject() {
  const input = { user: 'alice', password: 'secret', nested: { apiKey: 'not-shown' } };
  const redacted = redactSecretsInObject(input, ['password', 'apiKey']);
  assert.equal(redacted.password, '[REDACTED]');
  assert.equal(redacted.nested.apiKey, '[REDACTED]');
  // Ensure original not mutated
  assert.equal(input.password, 'secret');
  console.log('testRedactSecretsInObject passed');
}

function testSanitizePromptInput() {
  const input = 'Hello user@example.com. use api_key_123 and tokenABC to access.';
  const sanitized = sanitizePromptInput(input);
  if (!sanitized.includes('[REDACTED_EMAIL]')) throw new Error('Email not redacted');
  if (!sanitized.includes('[REDACTED]')) throw new Error('Secret tokens not redacted');
  console.log('testSanitizePromptInput passed');
}

function testExponentialBackoff() {
  const a0 = exponentialBackoff(0, 100, 1000, false);
  if (a0 !== 100) throw new Error('Backoff 0 failed');
  const a3 = exponentialBackoff(3, 100, 1000, false);
  if (a3 !== 800) throw new Error('Backoff 3 failed');
  console.log('testExponentialBackoff passed');
}

function runAll(){
  testRedactSecretsInObject();
  testSanitizePromptInput();
  testExponentialBackoff();
  console.log('ALL SECURITY TESTS PASSED');
}

runAll();
