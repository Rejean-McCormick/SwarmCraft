const { initDb, get, run } = require('../db');

async function getBalance(userId) {
  const db = await initDb();
  const row = await get(db, 'SELECT balance FROM wallets WHERE user_id = ?', [userId]);
  return row ? row.balance : 0;
}

async function modifyBalance(userId, delta) {
  const db = await initDb();
  const current = await getBalance(userId);
  const newBal = current + delta;
  if (newBal < 0) throw new Error('insufficient funds');
  await run(db, 'UPDATE wallets SET balance = ? WHERE user_id = ?', [newBal, userId]);
  return newBal;
}

module.exports = { getBalance, modifyBalance };
