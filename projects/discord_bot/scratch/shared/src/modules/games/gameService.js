const { initDb, get, run, all } = require('../../db');

async function startRouletteSession(userId) {
  const db = await initDb();
  const sessionId = require('uuid').v4();
  await run(db, 'INSERT INTO sessions (session_id, type, user_id, state, data, created_at, updated_at) VALUES (?, ?, ?, ?, ?, datetime("now"), datetime("now"))', [sessionId, 'roulette', userId, 'new', JSON.stringify({ bets: [] })]);
  return sessionId;
}

async function startBlackjackSession(userId) {
  const db = await initDb();
  const sessionId = require('uuid').v4();
  await run(db, 'INSERT INTO sessions (session_id, type, user_id, state, data, created_at, updated_at) VALUES (?, ?, ?, ?, ?, datetime("now"), datetime("now"))', [sessionId, 'blackjack', userId, 'new', JSON.stringify({ hand: [], deck: [] })]);
  return sessionId;
}

async function getSessionState(sessionId) {
  const db = await initDb();
  const s = await get(db, 'SELECT * FROM sessions WHERE session_id = ?', [sessionId]);
  return s ? JSON.parse(s.data) : null;
}

module.exports = { startRouletteSession, startBlackjackSession, getSessionState };
