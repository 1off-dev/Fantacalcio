import Database from "better-sqlite3";
import fs from "node:fs";
import path from "node:path";

const DEFAULT_TEAMS = [
  { id: "t1", name: "La mia squadra" },
  { id: "t2", name: "Riva 2" },
  { id: "t3", name: "Riva 3" },
  { id: "t4", name: "Riva 4" },
  { id: "t5", name: "Riva 5" },
  { id: "t6", name: "Riva 6" },
];

export function emptyState() {
  return {
    kind: "fantacalcio-asta-snapshot",
    version: 2,
    shared: true,
    savedAt: new Date().toISOString(),
    ownership: {},
    teams: DEFAULT_TEAMS.map((t) => ({ ...t })),
    auctionRole: "P",
    roleLock: true,
    publishedVia: "server-db",
  };
}

export function openDb(dbPath) {
  fs.mkdirSync(path.dirname(dbPath), { recursive: true });
  const db = new Database(dbPath);
  db.pragma("journal_mode = WAL");
  db.exec(`
    CREATE TABLE IF NOT EXISTS asta_state (
      id INTEGER PRIMARY KEY CHECK (id = 1),
      payload TEXT NOT NULL,
      updated_at TEXT NOT NULL,
      rev INTEGER NOT NULL DEFAULT 1
    );
    CREATE TABLE IF NOT EXISTS sessions (
      token TEXT PRIMARY KEY,
      user TEXT NOT NULL,
      role TEXT NOT NULL,
      created_at TEXT NOT NULL,
      expires_at TEXT NOT NULL
    );
  `);

  const row = db.prepare("SELECT payload FROM asta_state WHERE id = 1").get();
  if (!row) {
    const seedPath = process.env.ASTA_SEED_JSON;
    let seed = emptyState();
    if (seedPath && fs.existsSync(seedPath)) {
      try {
        const parsed = JSON.parse(fs.readFileSync(seedPath, "utf8"));
        if (parsed && typeof parsed === "object") {
          seed = {
            ...emptyState(),
            ...parsed,
            shared: true,
            savedAt: parsed.savedAt || new Date().toISOString(),
            publishedVia: "server-db",
          };
        }
      } catch {
        /* keep empty */
      }
    }
    db.prepare(
      "INSERT INTO asta_state (id, payload, updated_at, rev) VALUES (1, ?, ?, 1)"
    ).run(JSON.stringify(seed), seed.savedAt);
  }

  return db;
}

export function readState(db) {
  const row = db.prepare("SELECT payload, updated_at, rev FROM asta_state WHERE id = 1").get();
  if (!row) return { state: emptyState(), rev: 0, updatedAt: null };
  return {
    state: JSON.parse(row.payload),
    rev: row.rev,
    updatedAt: row.updated_at,
  };
}

export function writeState(db, state) {
  const savedAt = new Date().toISOString();
  const next = {
    ...state,
    kind: "fantacalcio-asta-snapshot",
    version: 2,
    shared: true,
    savedAt,
    publishedVia: "server-db",
  };
  const info = db
    .prepare(
      `UPDATE asta_state
       SET payload = ?, updated_at = ?, rev = rev + 1
       WHERE id = 1`
    )
    .run(JSON.stringify(next), savedAt);
  if (info.changes === 0) {
    db.prepare(
      "INSERT INTO asta_state (id, payload, updated_at, rev) VALUES (1, ?, ?, 1)"
    ).run(JSON.stringify(next), savedAt);
  }
  return readState(db);
}

export function createSession(db, { user, role, ttlHours = 24 }) {
  const token = `asta_${role}_${Date.now().toString(36)}_${Math.random().toString(36).slice(2, 12)}`;
  const created = new Date();
  const expires = new Date(created.getTime() + ttlHours * 3600 * 1000);
  db.prepare(
    "INSERT INTO sessions (token, user, role, created_at, expires_at) VALUES (?, ?, ?, ?, ?)"
  ).run(token, user, role, created.toISOString(), expires.toISOString());
  return { token, user, role, expiresAt: expires.toISOString() };
}

export function getSession(db, token) {
  if (!token) return null;
  const row = db
    .prepare("SELECT token, user, role, expires_at FROM sessions WHERE token = ?")
    .get(token);
  if (!row) return null;
  if (new Date(row.expires_at).getTime() < Date.now()) {
    db.prepare("DELETE FROM sessions WHERE token = ?").run(token);
    return null;
  }
  return row;
}

export function deleteSession(db, token) {
  if (!token) return;
  db.prepare("DELETE FROM sessions WHERE token = ?").run(token);
}
