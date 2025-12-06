// Simple smoke test to ensure CommonJS modules load correctly

test('CommonJS module loads without throwing', () => {
  const usersRouter = require('../src/users.js');
  expect(usersRouter).toBeDefined();
  expect(typeof usersRouter).toBe('function');
});
