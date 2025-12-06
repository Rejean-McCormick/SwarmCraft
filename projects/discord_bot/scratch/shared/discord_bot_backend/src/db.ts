import sqlite3 from 'better-sqlite3';

// Singleton DB connection
class DB {
  private static instance: sqlite3.Database | null = null;

  static getInstance(): sqlite3.Database {
    if (!DB.instance) {
      const db = new sqlite3('discord_bot.db');
      // Initialize schema if needed
      db.exec(`
        CREATE TABLE IF NOT EXISTS users (
          id TEXT PRIMARY KEY,
          username TEXT NOT NULL,
          balance INTEGER NOT NULL DEFAULT 0,
          created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS items (
          id TEXT PRIMARY KEY,
          name TEXT NOT NULL,
          price INTEGER NOT NULL,
          description TEXT,
          stock INTEGER
        );
        CREATE TABLE IF NOT EXISTS rooms (
          id TEXT PRIMARY KEY,
          game TEXT NOT NULL,
          created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS room_players (
          room_id TEXT,
          user_id TEXT,
          PRIMARY KEY (room_id, user_id)
        );
      `);
      DB.instance = db;
    }
    return DB.instance;
  }

  static close(): void {
    if (DB.instance) {
      DB.instance.close();
      DB.instance = null;
    }
  }
}

export default DB;
