import express from "express";
import http from "node:http";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { WebSocketServer } from "ws";
import {
  openDb,
  readState,
  writeState,
  createSession,
  getSession,
  deleteSession,
} from "./db.js";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, "../..");
const PUBLIC_DIR = path.join(ROOT, "public");

const PORT = Number(process.env.PORT || 3847);
const BASE = (process.env.BASE_PATH || "/fantacalcio").replace(/\/$/, "") || "";
const DB_PATH = process.env.ASTA_DB_PATH || path.join(ROOT, "server", "data", "asta.sqlite");
const SEED = process.env.ASTA_SEED_JSON || path.join(PUBLIC_DIR, "asta-live.json");

const USERS = {
  admin: { password: process.env.ASTA_ADMIN_PASSWORD || "admin", role: "admin", label: "Admin" },
  root: { password: process.env.ASTA_ROOT_PASSWORD || "admin", role: "admin", label: "Root" },
};

process.env.ASTA_SEED_JSON = SEED;
const db = openDb(DB_PATH);

const app = express();
app.disable("x-powered-by");
app.use(express.json({ limit: "2mb" }));

function bearer(req) {
  const h = req.headers.authorization || "";
  const m = /^Bearer\s+(.+)$/i.exec(h);
  return m?.[1] || req.headers["x-asta-token"] || "";
}

function requireWrite(req, res, next) {
  const session = getSession(db, bearer(req));
  if (!session || session.role !== "admin") {
    return res.status(401).json({ error: "Serve login admin per scrivere" });
  }
  req.astaSession = session;
  next();
}

const api = express.Router();

api.get("/health", (_req, res) => {
  const { rev, updatedAt } = readState(db);
  res.json({
    ok: true,
    service: "fantacalcio-asta",
    rev,
    updatedAt,
    base: BASE || "/",
  });
});

api.post("/login", (req, res) => {
  const user = String(req.body?.user || "").trim().toLowerCase();
  const pass = String(req.body?.password || "");
  if (!user && String(req.body?.role || "") === "readonly") {
    const session = createSession(db, { user: "guest", role: "readonly", ttlHours: 12 });
    return res.json({ ...session, label: "Sola lettura" });
  }
  const account = USERS[user];
  if (!account || account.password !== pass) {
    return res.status(401).json({ error: "Credenziali non valide" });
  }
  const session = createSession(db, { user, role: account.role, ttlHours: 24 });
  res.json({ ...session, label: account.label });
});

api.post("/logout", (req, res) => {
  deleteSession(db, bearer(req));
  res.json({ ok: true });
});

api.get("/state", (_req, res) => {
  const { state, rev, updatedAt } = readState(db);
  res.set("Cache-Control", "no-store");
  res.json({ ...state, rev, updatedAt });
});

api.put("/state", requireWrite, (req, res) => {
  const body = req.body;
  if (!body || typeof body !== "object") {
    return res.status(400).json({ error: "JSON non valido" });
  }
  const { state, rev, updatedAt } = writeState(db, body);
  broadcast({ type: "state", rev, updatedAt, payload: state });
  res.json({ ok: true, rev, updatedAt, state });
});

api.patch("/state", requireWrite, (req, res) => {
  const current = readState(db).state;
  const patch = req.body || {};
  const merged = {
    ...current,
    ...patch,
    ownership: patch.ownership ?? current.ownership,
    teams: patch.teams ?? current.teams,
  };
  const { state, rev, updatedAt } = writeState(db, merged);
  broadcast({ type: "state", rev, updatedAt, payload: state });
  res.json({ ok: true, rev, updatedAt, state });
});

if (BASE) {
  app.use(`${BASE}/api`, api);
  app.use(BASE, express.static(PUBLIC_DIR, { etag: false, maxAge: 0 }));
  app.get([BASE, `${BASE}/`], (_req, res) => {
    res.set("Cache-Control", "no-store");
    res.sendFile(path.join(PUBLIC_DIR, "index.html"));
  });
} else {
  app.use("/api", api);
  app.use(express.static(PUBLIC_DIR, { etag: false, maxAge: 0 }));
}

app.get("/healthz", (_req, res) => res.type("text").send("ok"));

const server = http.createServer(app);
const wss = new WebSocketServer({ server, path: `${BASE}/ws` });
const clients = new Set();

function broadcast(msg, except = null) {
  const data = JSON.stringify(msg);
  for (const ws of clients) {
    if (ws !== except && ws.readyState === 1) ws.send(data);
  }
}

wss.on("connection", (ws) => {
  clients.add(ws);
  const { state, rev, updatedAt } = readState(db);
  ws.send(JSON.stringify({ type: "hello", rev, updatedAt, payload: state, clients: clients.size }));
  broadcast({ type: "presence", clients: clients.size }, ws);

  ws.on("message", (raw) => {
    let msg;
    try {
      msg = JSON.parse(String(raw));
    } catch {
      return;
    }
    if (msg?.type === "ping") {
      ws.send(JSON.stringify({ type: "pong", t: Date.now() }));
      return;
    }
    if (msg?.type === "auth") {
      const session = getSession(db, msg.token || "");
      ws.astaSession = session;
      ws.send(JSON.stringify({ type: "auth", ok: Boolean(session), role: session?.role || null }));
      return;
    }
    if (msg?.type === "push") {
      const session = getSession(db, msg.token || "") || ws.astaSession;
      if (!session || session.role !== "admin") {
        ws.send(JSON.stringify({ type: "error", error: "write denied" }));
        return;
      }
      if (!msg.payload || typeof msg.payload !== "object") return;
      const { state, rev, updatedAt } = writeState(db, msg.payload);
      broadcast({ type: "state", rev, updatedAt, payload: state });
      return;
    }
  });

  ws.on("close", () => {
    clients.delete(ws);
    broadcast({ type: "presence", clients: clients.size });
  });
});

server.listen(PORT, "127.0.0.1", () => {
  console.log(`[asta] listening http://127.0.0.1:${PORT}${BASE || "/"}`);
  console.log(`[asta] db ${DB_PATH}`);
  console.log(`[asta] ws  ws://127.0.0.1:${PORT}${BASE}/ws`);
});
