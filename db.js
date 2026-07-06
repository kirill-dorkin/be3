import { Database } from "bun:sqlite";

// Open (or create) the database file
const db = new Database("database.sqlite");

// Enable foreign keys
db.exec("PRAGMA foreign_keys = ON;");

// Create tables if they don't exist
db.exec(`
  CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    price TEXT NOT NULL,
    image_url TEXT,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
  );
`);

db.exec(`
  CREATE TABLE IF NOT EXISTS posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    content TEXT,
    image_url TEXT,
    author TEXT DEFAULT 'Admin',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
  );
`);

export default db;
