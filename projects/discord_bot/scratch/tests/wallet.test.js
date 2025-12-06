const { initDb, run, get } = require('../shared/db/index.js');
const { getBalance, modifyBalance } = require('../shared/wallet/walletService.js');
const { v4: uuidv4 } = require('uuid');

describe('Wallet service modular tests', () => {
  const USERNAME = 'testuser';
  let userId;
  let cleanupDb;

  beforeAll(async () => {
    // Use in-memory DB for tests
    process.env.DB_PATH = ':memory:';
    // Initialize DB and create baseline user/wiki
    const db = await initDb();
    cleanupDb = async () => {
      const { closeDb } = require('../shared/db/index.js');
      if (closeDb) await closeDb();
    };
    userId = uuidv4();
    // Insert user and wallet row
    await run(db, 'INSERT INTO users (id, username, password_hash, created_at) VALUES (?, ?, ?, datetime("now"))', [userId, USERNAME, 'hash']);
    await run(db, 'INSERT INTO wallets (user_id, balance) VALUES (?, ?)', [userId, 0]);
  });

  afterAll(async () => {
    if (cleanupDb) await cleanupDb();
  });

  test('initial balance is zero', async () => {
    const bal = await getBalance(userId);
    expect(bal).toBe(0);
  });

  test('deposit increases balance', async () => {
    const newBal = await modifyBalance(userId, 50);
    expect(newBal).toBe(50);
    const bal = await getBalance(userId);
    expect(bal).toBe(50);
  });

  test('withdraw decreases balance with validation', async () => {
    const after = await modifyBalance(userId, -20);
    expect(after).toBe(30);
    const bal = await getBalance(userId);
    expect(bal).toBe(30);
  });
});
