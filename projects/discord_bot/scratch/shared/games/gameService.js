const { initDb, get, run, all } = require('../db');

async function startBlackjackSession(userId) {
  const db = await initDb();
  const sessionId = require('uuid').v4();
  await run(db, 'INSERT INTO sessions (session_id, type, user_id, state, data, created_at, updated_at) VALUES (?, ?, ?, ?, ?, datetime("now"), datetime("now"))', [sessionId, 'blackjack', userId, 'new', JSON.stringify({ hand: [], deck: [] })]);
  return sessionId;
}

async function joinGame(userId, sessionId) {
  // simplistic: ensure session exists
  const db = await initDb();
  const row = await get(db, 'SELECT * FROM sessions WHERE session_id = ?', [sessionId]);
  if (!row) throw new Error('session not found');
  // mark as joined by user
  await run(db, 'UPDATE sessions SET user_id = ?, updated_at = datetime("now") WHERE session_id = ?', [userId, sessionId]);
  return true;
}

async function getSessionState(sessionId) {
  const db = await initDb();
  const s = await get(db, 'SELECT * FROM sessions WHERE session_id = ?', [sessionId]);
  return s ? JSON.parse(s.data) : null;
}

module.exports = { startBlackjackSession, joinGame, getSessionState };
