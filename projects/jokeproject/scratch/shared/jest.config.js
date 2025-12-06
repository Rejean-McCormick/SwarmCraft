module.exports = {
  testEnvironment: 'node',
  testMatch: ['**/tests/**/*.test.js'],
  globals: {
    SCRATCH_DB_PATH: process.env.SCRATCH_DB_PATH
  }
};
