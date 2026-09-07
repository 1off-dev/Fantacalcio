/* Asta Scientifica Fantacalcio 2026/27 — 6 squadre, priorità adattiva */
const STORAGE_KEY = "fantacalcio-asta-2026-27";
const LEGACY_STORAGE_KEYS = [
  "fantacalcio-asta-2026-27-v6",
  "fantacalcio-asta-2026-27-v5",
  "fantacalcio-asta-2026-27-v4",
];
const IDB_NAME = "fantacalcio-asta";
const IDB_STORE = "snapshots";
const IDB_KEY = "current";
const SNAPSHOT_KIND = "fantacalcio-asta-snapshot";
const ASSET_V = "20260907b";
const ROLES = ["P", "D", "C", "A"];
const ROLE_LABEL = { P: "Portieri", D: "Difensori", C: "Centrocampisti", A: "Attaccanti" };
const TIER_LABEL = {
  super_top: "Super top", top: "Top", top_bonus: "Top bonus", modificatore: "Modificatore",
  affidabile: "Affidabile", bonus: "Bonus", semi: "Semi", interessante: "Interessante",
  value: "Value", lowcost: "Low cost", pool: "Pool",
};
const TIER_RANK = {
  super_top: 10, top: 9, top_bonus: 9, modificatore: 8, affidabile: 7, bonus: 7,
  semi: 6, interessante: 5, value: 5, lowcost: 3, pool: 1,
};
const TRAFFIC_LABEL = {
  value: "Value", fair: "Fair", rich: "Ricco", overpay: "Overpay",
};
const COLUMNS = [
  { key: "priority", label: "Pri", type: "num", title: "Priorità dinamica vs rivali + fit rosa" },
  { key: "role", label: "Ruolo", type: "text" },
  { key: "name", label: "Giocatore", type: "text" },
  { key: "team", label: "Sq", type: "text" },
  { key: "fvm", label: "FVM", type: "num" },
  { key: "fair", label: "Fair", type: "num", title: "Fair market stimato" },
  { key: "leave", label: "Leave", type: "num", title: "Tetto leave mock a 6" },
  { key: "traffic", label: "Semaforo", type: "text", title: "Value / Fair / Ricco / Overpay vs FVM" },
  { key: "cap", label: "Cap", type: "num" },
  { key: "fmPrev", label: "FM 25/26", type: "num", title: "Fantamedia 2025/26" },
  { key: "starterProb", label: "Tit%", type: "num", title: "Probabilità titolare" },
  { key: "fitness", label: "Forma", type: "num", title: "Affidabilità fisica" },
  { key: "age", label: "Età", type: "num" },
  { key: "penalty", label: "Rigori", type: "num" },
  { key: "tier", label: "Fascia", type: "tier" },
  { key: "owner", label: "Owner", type: "text" },
  { key: "note", label: "Nota", type: "text" },
];

const state = {
  meta: null,
  players: [],
  plan: "modificatore_first",
  roleFilter: "P",
  query: "",
  onlyTiered: false,
  onlyPenalties: false,
  hideTaken: true,
  ownership: {},
  teams: [],
  myTeamId: "t1",
  selectedTeamId: "t1",
  pendingId: null,
  pendingMode: "buy",
  sortKey: "priority",
  sortDir: "desc",
  auctionRole: "P",
  roleLock: true,
};

const $ = (id) => document.getElementById(id);
const els = {
  budgetPlan: $("budgetPlan"),
  resetBtn: $("resetBtn"),
  exportBtn: $("exportBtn"),
  importBtn: $("importBtn"),
  importFile: $("importFile"),
  saveStatus: $("saveStatus"),
  teamsBar: $("teamsBar"),
  auctionBanner: $("auctionBanner"),
  stats: $("stats"),
  search: $("search"),
  roleChips: $("roleChips"),
  roleLock: $("roleLock"),
  onlyTiered: $("onlyTiered"),
  onlyPenalties: $("onlyPenalties"),
  hideTaken: $("hideTaken"),
  resultCount: $("resultCount"),
  playerHead: $("playerHead"),
  playerTable: $("playerTable"),
  priorityBox: $("priorityBox"),
  scenarioBox: $("scenarioBox"),
  strategyBox: $("strategyBox"),
  roster: $("roster"),
  buyDialog: $("buyDialog"),
  buyForm: $("buyForm"),
  buyTitle: $("buyTitle"),
  buyTeam: $("buyTeam"),
  buyPrice: $("buyPrice"),
  buyHint: $("buyHint"),
};

let lastSavedAt = null;
let persistTimer = null;
let idbReady = null;

function defaultTeams() {
  const fromMeta = state.meta?.defaultTeams;
  if (Array.isArray(fromMeta) && fromMeta.length === 6) {
    return fromMeta.map((t, i) => ({
      id: t.id || `t${i + 1}`,
      name: t.name || `Squadra ${i + 1}`,
      isMe: Boolean(t.isMe) || i === 0,
    }));
  }
  return [
    { id: "t1", name: "La mia squadra", isMe: true },
    { id: "t2", name: "Riva 2", isMe: false },
    { id: "t3", name: "Riva 3", isMe: false },
    { id: "t4", name: "Riva 4", isMe: false },
    { id: "t5", name: "Riva 5", isMe: false },
    { id: "t6", name: "Riva 6", isMe: false },
  ];
}

function openIdb() {
  if (idbReady) return idbReady;
  idbReady = new Promise((resolve, reject) => {
    if (!window.indexedDB) {
      resolve(null);
      return;
    }
    const req = indexedDB.open(IDB_NAME, 1);
    req.onupgradeneeded = () => {
      const db = req.result;
      if (!db.objectStoreNames.contains(IDB_STORE)) db.createObjectStore(IDB_STORE);
    };
    req.onsuccess = () => resolve(req.result);
    req.onerror = () => resolve(null);
  });
  return idbReady;
}

async function idbGet() {
  const db = await openIdb();
  if (!db) return null;
  return new Promise((resolve) => {
    try {
      const tx = db.transaction(IDB_STORE, "readonly");
      const req = tx.objectStore(IDB_STORE).get(IDB_KEY);
      req.onsuccess = () => resolve(req.result || null);
      req.onerror = () => resolve(null);
    } catch {
      resolve(null);
    }
  });
}

async function idbPut(payload) {
  const db = await openIdb();
  if (!db) return false;
  return new Promise((resolve) => {
    try {
      const tx = db.transaction(IDB_STORE, "readwrite");
      tx.objectStore(IDB_STORE).put(payload, IDB_KEY);
      tx.oncomplete = () => resolve(true);
      tx.onerror = () => resolve(false);
    } catch {
      resolve(false);
    }
  });
}

function snapshotPayload() {
  return {
    kind: SNAPSHOT_KIND,
    version: 1,
    savedAt: new Date().toISOString(),
    plan: state.plan,
    ownership: state.ownership,
    teams: state.teams,
    myTeamId: state.myTeamId,
    selectedTeamId: state.selectedTeamId,
    onlyTiered: state.onlyTiered,
    onlyPenalties: state.onlyPenalties,
    hideTaken: state.hideTaken,
    sortKey: state.sortKey,
    sortDir: state.sortDir,
    auctionRole: state.auctionRole,
    roleLock: state.roleLock,
    roleFilter: state.roleFilter,
  };
}

function applySaved(saved) {
  if (!saved || typeof saved !== "object") return false;
  Object.assign(state, {
    plan: saved.plan || state.plan,
    ownership: saved.ownership || {},
    teams: Array.isArray(saved.teams) && saved.teams.length === 6 ? saved.teams : state.teams,
    myTeamId: saved.myTeamId || state.myTeamId,
    selectedTeamId: saved.selectedTeamId || saved.myTeamId || state.selectedTeamId,
    onlyTiered: saved.onlyTiered ?? state.onlyTiered,
    onlyPenalties: saved.onlyPenalties ?? state.onlyPenalties,
    hideTaken: saved.hideTaken ?? state.hideTaken,
    sortKey: saved.sortKey || state.sortKey,
    sortDir: saved.sortDir || state.sortDir,
    auctionRole: saved.auctionRole || state.auctionRole,
    roleLock: saved.roleLock ?? state.roleLock,
  });
  state.roleFilter = state.roleLock
    ? state.auctionRole
    : saved.roleFilter || state.auctionRole;
  if (saved.savedAt) lastSavedAt = saved.savedAt;
  return true;
}

function readLocalStorageSnapshot() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) return JSON.parse(raw);
  } catch { /* ignore */ }
  for (const key of LEGACY_STORAGE_KEYS) {
    try {
      const raw = localStorage.getItem(key);
      if (!raw) continue;
      const parsed = JSON.parse(raw);
      if (parsed) {
        // Migra sulla chiave stabile.
        localStorage.setItem(STORAGE_KEY, JSON.stringify({ ...parsed, savedAt: parsed.savedAt || new Date().toISOString() }));
        return parsed;
      }
    } catch { /* ignore */ }
  }
  return null;
}

function loadSaved() {
  const saved = readLocalStorageSnapshot();
  if (saved) applySaved(saved);
}

function updateSaveStatus(ok, detail = "") {
  if (!els.saveStatus) return;
  if (!ok) {
    els.saveStatus.textContent = detail || "Salvataggio non riuscito";
    els.saveStatus.classList.add("warn");
    return;
  }
  const when = lastSavedAt ? new Date(lastSavedAt) : new Date();
  const time = when.toLocaleTimeString("it-IT", { hour: "2-digit", minute: "2-digit", second: "2-digit" });
  const n = Object.keys(state.ownership || {}).length;
  els.saveStatus.textContent = `Salvato alle ${time} · ${n} giocatori assegnati${detail ? ` · ${detail}` : ""}`;
  els.saveStatus.classList.remove("warn");
}

function persistSync() {
  const payload = snapshotPayload();
  lastSavedAt = payload.savedAt;
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(payload));
    // Pulisci chiavi legacy dopo migrazione riuscita.
    for (const key of LEGACY_STORAGE_KEYS) localStorage.removeItem(key);
  } catch (err) {
    updateSaveStatus(false, "localStorage pieno o bloccato");
    console.warn("persist localStorage failed", err);
    return payload;
  }
  updateSaveStatus(true, "browser");
  return payload;
}

function persist() {
  const payload = persistSync();
  // IndexedDB in background (più resistente alla pulizia cache aggressiva).
  clearTimeout(persistTimer);
  persistTimer = setTimeout(() => {
    idbPut(payload).then((ok) => {
      if (ok) updateSaveStatus(true, "browser + IndexedDB");
    });
  }, 120);
  return payload;
}

async function hydrateFromIdbIfNeeded() {
  const hasLocal = Boolean(localStorage.getItem(STORAGE_KEY))
    || LEGACY_STORAGE_KEYS.some((k) => localStorage.getItem(k));
  if (hasLocal && Object.keys(state.ownership).length) return;
  const fromIdb = await idbGet();
  if (!fromIdb) return;
  // Preferisci IndexedDB se localStorage è vuoto o senza ownership.
  if (!hasLocal || Object.keys(state.ownership).length === 0) {
    applySaved(fromIdb);
    persistSync();
  }
}

function downloadSnapshot(filename) {
  const payload = {
    ...snapshotPayload(),
    // Riepilogo leggibile (oltre allo state completo per restore).
    summary: state.teams.map((t) => ({
      id: t.id,
      name: t.name,
      isMe: t.id === state.myTeamId,
      spent: spentByTeam(t.id),
      remaining: remainingByTeam(t.id),
      rosa: ROLES.flatMap((role) => teamByRole(t.id, role).map((p) => ({
        id: p.id,
        role,
        name: p.name,
        club: p.team,
        price: state.ownership[p.id].price,
      }))),
    })),
  };
  const stamp = new Date().toISOString().slice(0, 19).replace(/[:T]/g, "-");
  const a = document.createElement("a");
  a.href = URL.createObjectURL(new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" }));
  a.download = filename || `asta-fantacalcio-backup-${stamp}.json`;
  a.click();
  URL.revokeObjectURL(a.href);
  updateSaveStatus(true, "file scaricato");
}

function ownershipFromSummary(summaryTeams) {
  const byId = Object.fromEntries(state.players.map((p) => [p.id, p]));
  const byNameRole = new Map(state.players.map((p) => [`${p.role}|${p.name}`.toLowerCase(), p]));
  const ownership = {};
  for (const t of summaryTeams || []) {
    for (const row of t.rosa || []) {
      let player = row.id ? byId[row.id] : null;
      if (!player && row.name) {
        player = byNameRole.get(`${row.role || ""}|${row.name}`.toLowerCase())
          || state.players.find((p) => p.name.toLowerCase() === String(row.name).toLowerCase());
      }
      if (!player) continue;
      const isMe = Boolean(t.isMe) || t.id === state.myTeamId;
      ownership[player.id] = {
        status: isMe ? "mine" : "taken",
        price: Number(row.price) || 1,
        teamId: t.id,
      };
    }
  }
  return ownership;
}

function importSnapshot(data) {
  if (!data || typeof data !== "object") throw new Error("File non valido");

  // Formato snapshot completo.
  if (data.kind === SNAPSHOT_KIND || data.ownership) {
    applySaved(data);
    // Se manca ownership ma c'è summary, ricostruisci.
    if ((!data.ownership || !Object.keys(data.ownership).length) && data.summary) {
      state.ownership = ownershipFromSummary(data.summary);
    }
  } else if (Array.isArray(data.teams)) {
    // Vecchio export “rosa” senza ownership map.
    if (data.teams.length === 6) {
      state.teams = data.teams.map((t, i) => ({
        id: t.id || `t${i + 1}`,
        name: t.name || `Squadra ${i + 1}`,
        isMe: Boolean(t.isMe),
      }));
      const me = state.teams.find((t) => t.isMe) || state.teams[0];
      state.myTeamId = me.id;
      state.selectedTeamId = me.id;
    }
    if (data.plan) state.plan = data.plan;
    if (data.auctionRole) state.auctionRole = data.auctionRole;
    state.ownership = ownershipFromSummary(data.teams);
  } else {
    throw new Error("JSON non riconosciuto come backup asta");
  }

  persist();
  render();
}

function exportRoster() {
  downloadSnapshot();
}

const budgetTotal = () => Number(state.meta.budget || 1000);
const rosterSlots = () => state.meta.roster;
const teamsCount = () => Number(state.meta.teams || 6);
const currentBudget = () => state.meta.budgets[state.plan];
const teamById = (id) => state.teams.find((t) => t.id === id);
const rivals = () => state.teams.filter((t) => t.id !== state.myTeamId);

function ownedByTeam(teamId) {
  return state.players.filter((p) => state.ownership[p.id]?.teamId === teamId);
}
function spentByTeam(teamId) {
  return ownedByTeam(teamId).reduce((s, p) => s + Number(state.ownership[p.id]?.price || 0), 0);
}
function remainingByTeam(teamId) {
  return budgetTotal() - spentByTeam(teamId);
}
function teamByRole(teamId, role) {
  return ownedByTeam(teamId).filter((p) => p.role === role);
}
function slotsLeftTeam(teamId, role) {
  return Number(rosterSlots()[role]) - teamByRole(teamId, role).length;
}
function mineByRole(role) {
  return teamByRole(state.myTeamId, role);
}
function spentByRole(role) {
  return mineByRole(role).reduce((s, p) => s + Number(state.ownership[p.id]?.price || 0), 0);
}
function remainingBudget() {
  return remainingByTeam(state.myTeamId);
}
function remainingSlots(role) {
  return slotsLeftTeam(state.myTeamId, role);
}
function marketTaken(role) {
  return state.players.filter((p) => p.role === role && state.ownership[p.id]).length;
}
function marketTarget(role) {
  return Number(rosterSlots()[role]) * teamsCount();
}
function roleBudgetLeft(role) {
  return Number(currentBudget()[role]) - spentByRole(role);
}
function safeSpend(role) {
  const slots = remainingSlots(role);
  const left = roleBudgetLeft(role);
  if (slots <= 0) return 0;
  return Math.max(1, left - Math.max(0, slots - 1));
}

function marketIntel(role = state.auctionRole) {
  const rivalRows = rivals().map((t) => {
    const rolePlayers = teamByRole(t.id, role);
    return {
      id: t.id,
      name: t.name,
      rem: remainingByTeam(t.id),
      spent: spentByTeam(t.id),
      roleCount: rolePlayers.length,
      roleSpent: rolePlayers.reduce((s, p) => s + Number(state.ownership[p.id]?.price || 0), 0),
      slotsLeft: slotsLeftTeam(t.id, role),
      hasElite: rolePlayers.some((p) => (TIER_RANK[p.tier] || 0) >= 9),
    };
  });
  const avgRivalRem = rivalRows.length
    ? rivalRows.reduce((s, r) => s + r.rem, 0) / rivalRows.length
    : budgetTotal();
  const avgRivalRoleSpent = rivalRows.length
    ? rivalRows.reduce((s, r) => s + r.roleSpent, 0) / rivalRows.length
    : 0;
  const hungryRivals = rivalRows.filter((r) => r.slotsLeft > 0 && r.rem >= 120).length;
  const brokeRivals = rivalRows.filter((r) => r.rem < 80 || (r.slotsLeft > 2 && r.rem < 150)).length;
  const eliteTaken = state.players.filter(
    (p) => p.role === role && (TIER_RANK[p.tier] || 0) >= 9 && state.ownership[p.id]
  );
  const myElite = mineByRole(role).some((p) => (TIER_RANK[p.tier] || 0) >= 9);
  const planSlice = Math.max(40, Number(currentBudget()[role]) * 0.35);
  const inflation = avgRivalRoleSpent > 0
    ? Math.min(1.35, Math.max(0.75, avgRivalRoleSpent / planSlice))
    : 1;
  return { rivalRows, avgRivalRem, avgRivalRoleSpent, hungryRivals, brokeRivals, eliteTaken, myElite, inflation };
}

function rosterFitDelta(p) {
  const role = p.role;
  const mine = mineByRole(role);
  const slotsLeft = remainingSlots(role);
  const eliteMine = mine.filter((m) => (TIER_RANK[m.tier] || 0) >= 9).length;
  const midMine = mine.filter((m) => (TIER_RANK[m.tier] || 0) >= 6 && (TIER_RANK[m.tier] || 0) < 9).length;
  const penMine = mine.filter((m) => m.penalty === 1).length;
  const isElite = (TIER_RANK[p.tier] || 0) >= 9;
  const isMid = (TIER_RANK[p.tier] || 0) >= 6 && (TIER_RANK[p.tier] || 0) < 9;
  let d = 0;

  // Schema alerts: fill holes first, avoid second elite when slots tight.
  if (slotsLeft <= 0) return -50;
  if (slotsLeft === 1 && isElite && eliteMine >= 1) d -= 14;
  if (slotsLeft <= 2 && !isElite && (p.starterProb || 0) >= 75) d += 8;
  if (eliteMine === 0 && isElite && slotsLeft >= 2) d += 6;
  if (eliteMine >= 1 && isElite) d -= 16;
  if (eliteMine >= 1 && isMid && (p.fitness || 0) >= 70) d += 7;
  if (midMine === 0 && isMid) d += 4;

  if (role === "P") {
    const solid = mine.some((m) => (m.fitness || 0) >= 70 && (m.starterProb || 0) >= 70);
    if (solid && (p.fitness || 0) < 55) d -= 10;
    if (!solid && (p.starterProb || 0) >= 80) d += 9;
  }
  if (role === "D") {
    const hasBonusWing = mine.some((m) => (TIER_RANK[m.tier] || 0) >= 8 || m.name === "Dimarco");
    if (!hasBonusWing && (p.name === "Dimarco" || (TIER_RANK[p.tier] || 0) >= 8)) d += 5;
    if (hasBonusWing && (TIER_RANK[p.tier] || 0) < 8 && (p.starterProb || 0) >= 75) d += 6;
    if (p.csProxy != null && p.csProxy >= 0.8) d += 3;
  }
  if (role === "C") {
    if (penMine === 0 && p.penalty === 1) d += 9;
    if (penMine >= 1 && p.penalty === 1) d -= 8;
    if (eliteMine >= 1 && p.penalty !== 1 && (p.starterProb || 0) >= 75) d += 5;
  }
  if (role === "A") {
    const hasTop = mine.some((m) => (TIER_RANK[m.tier] || 0) >= 9);
    if (!hasTop && isElite) d += 5;
    if (hasTop && isElite) d -= 14;
    if (hasTop && isMid) d += 8;
    if (mine.length >= 3 && (p.cap || 0) > roleBudgetLeft(role) * 0.45) d -= 6;
  }

  // Leave / traffic vs listone price.
  if (p.leave != null && p.fvm >= p.leave) d -= 10;
  if (p.traffic === "overpay") d -= 8;
  if (p.traffic === "value") d += 6;
  if (p.traffic === "fair") d += 2;
  if (p.injuryDaysOut != null && p.injuryDaysOut >= 60) d -= 7;
  else if (p.injuryMuscular) d -= 3;
  if (p.benchRate != null && p.benchRate >= 40) d -= 4;
  if (p.teamSched != null && p.teamSched >= 4 && role !== "P") d += 2;
  if (p.teamSched != null && p.teamSched <= 2 && (TIER_RANK[p.tier] || 0) >= 8) d -= 1;

  return d;
}

function priorityScore(p) {
  const role = state.auctionRole;
  if (p.role !== role) return -1;
  if (state.ownership[p.id]) return -1;
  const slotsLeft = remainingSlots(role);
  if (slotsLeft <= 0) return -1;

  const intel = marketIntel(role);
  const roleLeft = roleBudgetLeft(role);
  const maxAfford = safeSpend(role);
  const marketLeft = Math.max(0, marketTarget(role) - marketTaken(role));
  const fair = p.fair || p.cap || p.fvm || 1;

  let s = 0;
  s += (p.starterProb || 0) * 0.28;
  s += (p.fitness || 50) * 0.22;
  s += Math.min(100, ((p.fmPrev || 5.8) / 9) * 100) * 0.1;
  if (p.per90Prod != null) s += Math.min(14, p.per90Prod * 18);
  else if (p.bonusProxy != null) s += Math.min(10, p.bonusProxy * 0.35);
  if (p.per90ProdNoPen != null) s += Math.min(6, p.per90ProdNoPen * 10);
  if (p.bonusPure != null && p.bonusPure > 0.35) s += Math.min(5, p.bonusPure * 6);
  if (p.csProxy != null && role !== "A") s += Math.min(5, p.csProxy * 3);
  s += (TIER_RANK[p.tier] || 1) * 6.5;
  if (p.penalty === 1) s += 11;
  else if (p.penalty === 2) s += 5;
  else if (p.penalty === 3) s += 2;

  const value = ((p.fmPrev || 6) * ((p.starterProb || 50) / 100) * ((p.fitness || 50) / 100)) / Math.max(fair, 1);
  s += Math.min(16, value * 32);
  s += rosterFitDelta(p);

  if (p.cap > remainingBudget()) s -= 42;
  else if (p.cap > maxAfford) s -= 20;
  else if (slotsLeft > 1 && p.cap > roleLeft * 0.55) s -= 9;
  else if (p.cap <= maxAfford * 0.55 && (TIER_RANK[p.tier] || 0) >= 7) s += 7;

  if (p.fairHigh && p.fvm > p.fairHigh) s -= 6;
  if (p.fairLow && p.fvm < p.fairLow) s += 5;
  if (p.leave != null && p.cap > p.leave) s -= 7;

  if (intel.myElite && (TIER_RANK[p.tier] || 0) >= 9) s -= 20;
  if (intel.myElite && (p.fitness || 0) >= 75 && p.cap <= maxAfford) s += 7;

  if (intel.hungryRivals >= 3 && (p.starterProb || 0) >= 75) s += 8;
  if (intel.brokeRivals >= 3 && (TIER_RANK[p.tier] || 0) >= 8) s -= 6;
  if (intel.brokeRivals >= 3 && p.cap <= maxAfford * 0.7) s += 5;

  if (intel.eliteTaken.length >= 2 && (TIER_RANK[p.tier] || 0) >= 9) s -= 12;
  if (intel.eliteTaken.length >= 2 && (TIER_RANK[p.tier] || 0) >= 6 && (TIER_RANK[p.tier] || 0) < 9) s += 9;

  if (intel.inflation > 1.15 && p.cap >= fair * 1.05) s -= 8;
  if (intel.inflation > 1.15 && p.cap <= fair * 0.9) s += 6;

  const later = ROLES.slice(ROLES.indexOf(role) + 1);
  if (later.length) {
    const laterPlan = later.reduce((acc, r) => acc + Number(currentBudget()[r] || 0), 0);
    if (remainingBudget() < laterPlan * 0.85 && (TIER_RANK[p.tier] || 0) >= 9) s -= 10;
  }

  if (role === "P" && mineByRole("P").some((m) => (m.fitness || 0) >= 70) && (p.fitness || 0) < 60) s -= 8;
  if (role === "D" && p.name === "Dimarco" && intel.hungryRivals >= 2) s -= 4;
  if (role === "A" && p.name === "Malen") {
    if (intel.avgRivalRem > 700) s += 3;
    if ((p.cap || 0) > roleLeft * 0.7) s -= 5;
  }
  if (role === "C" && intel.myElite && p.penalty === 1) s += 6;

  if (slotsLeft > 0 && marketLeft <= slotsLeft * teamsCount() * 0.35) s += (p.starterProb || 0) * 0.08;
  if ((p.fitness || 100) < 40) s -= 10;
  if ((p.age || 0) >= 34) s -= 4;

  return Math.round(s * 10) / 10;
}

function priorityWhy(p) {
  const intel = marketIntel(p.role);
  const bits = [];
  if ((p.starterProb || 0) >= 80) bits.push("titolare");
  if ((p.fitness || 0) >= 75) bits.push("forma ok");
  if ((p.fitness || 0) < 45) bits.push("rischio fisico");
  if (p.penalty === 1) bits.push("1° rigore");
  if ((TIER_RANK[p.tier] || 0) >= 9) bits.push("fascia top");
  if (p.fairLow != null && p.fvm < p.fairLow) bits.push("sotto fair");
  if (p.traffic === "value") bits.push("semaforo value");
  if (p.traffic === "overpay") bits.push("semaforo overpay");
  if (p.leave != null) bits.push(`leave ${p.leave}`);
  if (rosterFitDelta(p) >= 6) bits.push("fit rosa+");
  if (rosterFitDelta(p) <= -8) bits.push("fit rosa−");
  if (intel.hungryRivals >= 3) bits.push("rivali affamati");
  if (intel.brokeRivals >= 3) bits.push("rivali corti");
  if (intel.eliteTaken.length >= 2) bits.push("top usciti→value");
  bits.push(p.cap <= safeSpend(p.role) ? "nel budget" : "oltre spend-safe");
  return bits.slice(0, 6).join(" · ");
}

function pickScenarioLetter(role) {
  const intel = marketIntel(role);
  const mine = mineByRole(role);
  const eliteMine = mine.some((m) => (TIER_RANK[m.tier] || 0) >= 9);
  const topStill = state.players.filter(
    (p) => p.role === role && (TIER_RANK[p.tier] || 0) >= 9 && !state.ownership[p.id]
  );
  const topLeaveRisk = topStill.filter((p) => p.leave != null && (p.fvm || p.cap || 0) >= p.leave * 0.95);

  if (eliteMine) return "B";
  if (intel.eliteTaken.length >= 2 || topStill.length === 0) return "C";
  if (intel.inflation > 1.18 || topLeaveRisk.length >= 2) return "B";
  if (intel.hungryRivals >= 4 && topStill.length) return "A";
  return "A";
}

function scenarioPlansFor(role) {
  const fromMeta = state.meta?.scenarioPlans?.[role];
  if (fromMeta && (fromMeta.A || fromMeta.B || fromMeta.C)) return fromMeta;
  const sample = state.players.find((p) => p.role === role && p.scenarios);
  return sample?.scenarios || {};
}

function adaptiveStrategyLines(role) {
  const intel = marketIntel(role);
  const lines = [];
  const base = {
    P: "Base: 1 cemento (Tit%+Forma), poi titolari low-cost.",
    D: "Base: voti mod prima, 1 esterno bonus sotto spend-safe.",
    C: "Base: max uno tra Paz/Calha/McT, poi rigoristi/bonus Forma≥55.",
    A: "Base: se Malen > fair/leave, piano 2+2 value.",
  };
  lines.push(base[role]);

  if (intel.eliteTaken.length === 0) {
    lines.push("Top ancora disponibili: non sparare il primo nome se i rivali hanno budget pieno.");
  } else if (intel.eliteTaken.length === 1) {
    const who = intel.eliteTaken[0];
    const own = state.ownership[who.id];
    const owner = teamById(own?.teamId);
    lines.push(`${who.name} preso da ${owner?.name || "?"} a ${own?.price ?? "?"}: rivaluta il piano B nello stesso tier.`);
  } else {
    lines.push(`${intel.eliteTaken.length} top già usciti: sposta Pri su semi/value con Tit%+Forma.`);
  }

  if (intel.hungryRivals >= 3) {
    lines.push(`${intel.hungryRivals} rivali ancora carichi: alza aggressività su titolari certi, evita aste lunghe su Vetro.`);
  }
  if (intel.brokeRivals >= 2) {
    lines.push(`${intel.brokeRivals} rivali corti di budget: puoi aspettare sconti e chiudere depth a 1–8.`);
  }
  if (intel.inflation > 1.18) {
    lines.push(`Inflazione ruolo alta (~${Math.round(intel.inflation * 100)}%): non inseguire sopra leave/fairHigh.`);
  } else if (intel.inflation < 0.9 && marketTaken(role) >= 3) {
    lines.push("Mercato freddo sul ruolo: puoi salire di uno scaglione sul target primario.");
  }

  const myRem = remainingBudget();
  const avgR = Math.round(intel.avgRivalRem);
  if (myRem > avgR + 120) lines.push(`Hai +${myRem - avgR} vs media rivali: puoi forzare 1 pezzo chiave ora.`);
  else if (myRem < avgR - 120) lines.push(`Sei −${avgR - myRem} vs media rivali: difendi il warchest dei ruoli successivi.`);

  if (intel.myElite) lines.push("Hai già un elite nel ruolo: priorità cemento/minuti, non un secondo listone.");

  const idx = ROLES.indexOf(role);
  if (idx >= 0 && idx < ROLES.length - 1) {
    const next = ROLES[idx + 1];
    const hot = intel.rivalRows.filter((r) => r.spent > budgetTotal() * 0.35).length;
    if (hot >= 2) {
      lines.push(`${hot} rivali hanno bruciato >35% budget: preparati a essere aggressivo su ${ROLE_LABEL[next]} value.`);
    }
  }

  lines.push(`Spend-safe ${safeSpend(role)} · slot ${remainingSlots(role)} · mercato ${marketTaken(role)}/${marketTarget(role)}.`);
  return lines;
}

function sortValue(p, key, type) {
  if (key === "priority") return priorityScore(p);
  if (key === "owner") {
    const o = state.ownership[p.id];
    return o ? (teamById(o.teamId)?.name || "") : "";
  }
  if (key === "traffic") {
    const rank = { value: 1, fair: 2, rich: 3, overpay: 4 };
    return rank[p.traffic] || 0;
  }
  if (type === "tier") return TIER_RANK[p.tier] || 0;
  if (key === "penalty") return p.penalty == null ? 99 : Number(p.penalty);
  if (type === "num") {
    const v = p[key];
    return v == null || Number.isNaN(Number(v)) ? -Infinity : Number(v);
  }
  return String(p[key] ?? "");
}

function comparePlayers(a, b) {
  const col = COLUMNS.find((c) => c.key === state.sortKey) || COLUMNS[0];
  const dir = state.sortDir === "asc" ? 1 : -1;
  const av = sortValue(a, col.key, col.type);
  const bv = sortValue(b, col.key, col.type);
  let cmp = typeof av === "number" && typeof bv === "number"
    ? av - bv
    : String(av).localeCompare(String(bv), "it", { sensitivity: "base" });
  if (cmp !== 0) return cmp * dir;
  return priorityScore(b) - priorityScore(a) || b.fvm - a.fvm;
}

function activeRoleFilter() {
  return state.roleLock ? state.auctionRole : state.roleFilter;
}

function filteredPlayers() {
  const q = state.query.trim().toLowerCase();
  const role = activeRoleFilter();
  return state.players
    .filter((p) => (role === "ALL" ? true : p.role === role))
    .filter((p) => (state.onlyTiered ? p.tier !== "pool" : true))
    .filter((p) => (state.onlyPenalties ? Boolean(p.penalty) : true))
    .filter((p) => {
      if (!state.hideTaken) return true;
      const o = state.ownership[p.id];
      return !o || o.teamId === state.myTeamId;
    })
    .filter((p) => {
      if (!q) return true;
      const owner = state.ownership[p.id] ? teamById(state.ownership[p.id].teamId)?.name : "";
      return [p.name, p.team, TIER_LABEL[p.tier], p.note, p.penaltyLabel, p.fitnessLabel, owner]
        .some((x) => String(x || "").toLowerCase().includes(q));
    })
    .sort(comparePlayers);
}

function topPriorities(limit = 8) {
  return state.players
    .filter((p) => p.role === state.auctionRole && !state.ownership[p.id])
    .map((p) => ({ p, score: priorityScore(p) }))
    .filter((x) => x.score >= 0)
    .sort((a, b) => b.score - a.score || b.p.fvm - a.p.fvm)
    .slice(0, limit);
}

function maybeAdvanceRole() {
  if (remainingSlots(state.auctionRole) > 0) return false;
  const idx = ROLES.indexOf(state.auctionRole);
  if (idx < 0 || idx >= ROLES.length - 1) return false;
  state.auctionRole = ROLES[idx + 1];
  if (state.roleLock) state.roleFilter = state.auctionRole;
  return true;
}

function syncRoleChips() {
  [...els.roleChips.querySelectorAll(".chip")].forEach((c) => {
    const role = c.dataset.role;
    c.classList.toggle("active", state.roleLock ? role === state.auctionRole : role === state.roleFilter);
    c.disabled = Boolean(state.roleLock && role !== "ALL" && role !== state.auctionRole);
  });
}

function escapeAttr(s) {
  return String(s).replace(/&/g, "&amp;").replace(/"/g, "&quot;").replace(/</g, "&lt;");
}

function renderPlans() {
  els.budgetPlan.innerHTML = Object.entries(state.meta.budgets).map(([key, b]) =>
    `<option value="${key}" ${key === state.plan ? "selected" : ""}>${b.label} · P${b.P}/D${b.D}/C${b.C}/A${b.A}</option>`
  ).join("");
}

function renderTeamsBar() {
  els.teamsBar.innerHTML = state.teams.map((t) => {
    const spent = spentByTeam(t.id);
    const rem = remainingByTeam(t.id);
    const role = state.auctionRole;
    const filled = teamByRole(t.id, role).length;
    const need = rosterSlots()[role];
    const isMe = t.id === state.myTeamId;
    const selected = t.id === state.selectedTeamId;
    return `<article class="team-card ${isMe ? "me" : ""} ${selected ? "selected" : ""}" data-team="${t.id}">
      <label class="team-name-field">
        <span class="sr-only">Nome squadra</span>
        <input type="text" data-team-name="${t.id}" value="${escapeAttr(t.name)}" maxlength="28" />
      </label>
      <div class="team-meta"><strong>${spent}</strong> spesi · <strong>${rem}</strong> residui</div>
      <div class="team-role">${role}: ${filled}/${need}</div>
      <div class="team-actions">
        ${isMe ? '<span class="me-tag">Tu</span>' : `<button type="button" class="btn tiny ghost dark" data-action="set-me" data-id="${t.id}">Segna come tu</button>`}
        <button type="button" class="btn tiny ghost dark" data-action="select-team" data-id="${t.id}">Rosa</button>
      </div>
    </article>`;
  }).join("");
}

function renderStats() {
  const plan = currentBudget();
  const rem = remainingBudget();
  const role = state.auctionRole;
  const intel = marketIntel(role);
  const cards = [
    { label: "Tuo residuo", value: rem, cls: rem < 50 ? "warn" : "ok" },
    { label: "Media rivali", value: Math.round(intel.avgRivalRem), cls: "" },
    { label: `Tu · ${ROLE_LABEL[role]}`, value: `${mineByRole(role).length}/${rosterSlots()[role]}`, cls: "ok" },
    { label: "Mercato ruolo", value: `${marketTaken(role)}/${marketTarget(role)}`, cls: "" },
    ...ROLES.map((r) => {
      const left = plan[r] - spentByRole(r);
      return {
        label: `${r} piano`,
        value: `${left} · ${mineByRole(r).length}/${rosterSlots()[r]}`,
        cls: left < 0 ? "warn" : r === role ? "ok" : "",
      };
    }),
  ];
  els.stats.innerHTML = cards.map((c) =>
    `<div class="stat ${c.cls}"><strong>${c.value}</strong><span>${c.label}</span></div>`
  ).join("");
}

function renderAuctionBanner() {
  const role = state.auctionRole;
  const intel = marketIntel(role);
  els.auctionBanner.innerHTML = `
    <div class="auction-main">
      <p class="eyebrow">Asta a ruoli · 6 squadre · motore adattivo</p>
      <h2>Fase <span>${ROLE_LABEL[role]}</span></h2>
      <p>Tu <strong>${mineByRole(role).length}/${rosterSlots()[role]}</strong>
        · Mercato <strong>${marketTaken(role)}/${marketTarget(role)}</strong>
        · Budget ruolo <strong>${roleBudgetLeft(role)}</strong>
        · spend-safe <strong>${safeSpend(role)}</strong>
        · rivali affamati <strong>${intel.hungryRivals}</strong></p>
    </div>
    <div class="auction-actions">
      <button type="button" class="btn ghost dark" id="advanceRoleBtn">Ruolo fatto → avanza</button>
    </div>`;
  document.getElementById("advanceRoleBtn")?.addEventListener("click", () => {
    if (remainingSlots(role) > 0 && !confirm(`Ti mancano ${remainingSlots(role)} ${ROLE_LABEL[role]}. Avanzare?`)) return;
    const idx = ROLES.indexOf(state.auctionRole);
    if (idx < ROLES.length - 1) {
      state.auctionRole = ROLES[idx + 1];
      if (state.roleLock) state.roleFilter = state.auctionRole;
      render();
    } else alert("Sei già sugli Attaccanti.");
  });
}

function renderStrategy() {
  const lines = adaptiveStrategyLines(state.auctionRole);
  els.strategyBox.innerHTML = `
    <div class="panel-head"><h2>Strategia live</h2></div>
    <p class="strategy-lead">${lines[0]}</p>
    <ul>${lines.slice(1).map((l) => `<li>${l}</li>`).join("")}</ul>`;
}

function renderScenarios() {
  if (!els.scenarioBox) return;
  const role = state.auctionRole;
  const plans = scenarioPlansFor(role);
  const active = pickScenarioLetter(role);
  const letters = ["A", "B", "C"];
  els.scenarioBox.innerHTML = `
    <div class="panel-head"><h2>Scenari ${ROLE_LABEL[role]}</h2></div>
    <p class="strategy-lead">Piano attivo: <strong>Scenario ${active}</strong></p>
    <ul class="scenario-list">${letters.map((L) => `
      <li class="${L === active ? "active" : ""}">
        <span class="scenario-letter">${L}</span>
        <span>${plans[L] || "—"}</span>
      </li>`).join("")}</ul>
    ${plans.pivot ? `<p class="scenario-pivot"><strong>Pivot:</strong> ${plans.pivot}</p>` : ""}`;
}

function renderPriorities() {
  const rows = topPriorities(8);
  if (!rows.length) {
    els.priorityBox.innerHTML = '<div class="panel-head"><h2>Priorità</h2></div><p class="muted">Nessuna priorità.</p>';
    return;
  }
  els.priorityBox.innerHTML = `
    <div class="panel-head"><h2>Priorità ${ROLE_LABEL[state.auctionRole]}</h2></div>
    <ol class="priority-list">${rows.map(({ p, score }) => `<li>
      <div><strong>${p.name}</strong>
        <span class="meta">${p.team} · fair ${p.fair ?? "—"} · leave ${p.leave ?? "—"} · Tit ${p.starterProb ?? "—"}%</span>
        <span class="meta">${priorityWhy(p)}</span></div>
      <div class="priority-side"><span class="pri-score">${score}</span>
        <button class="btn small" data-action="buy" data-id="${p.id}">Compra</button></div>
    </li>`).join("")}</ol>`;
}

function fmtFm(v) {
  if (v == null || Number.isNaN(Number(v))) return '<span class="muted">—</span>';
  return Number(v).toFixed(2).replace(".", ",");
}
function fmtTit(p) {
  if (p.starterProb == null) return '<span class="muted">—</span>';
  const n = Math.round(Number(p.starterProb));
  const cls = n >= 80 ? "tit-high" : n >= 55 ? "tit-mid" : "tit-low";
  return `<span class="tit ${cls}">${n}%</span>`;
}
function fmtFit(p) {
  if (p.fitness == null) return '<span class="muted">—</span>';
  const n = Math.round(Number(p.fitness));
  const cls = n >= 80 ? "fit-high" : n >= 55 ? "fit-mid" : "fit-low";
  return `<span class="fit ${cls}" title="${p.fitnessLabel || ""}">${p.fitnessLabel || n}<small>${n}</small></span>`;
}
function fmtTraffic(p) {
  const t = p.traffic;
  if (!t) return '<span class="muted">—</span>';
  return `<span class="traffic traffic-${t}" title="FVM vs fair/mock">${TRAFFIC_LABEL[t] || t}</span>`;
}
function fmtOwner(p) {
  const o = state.ownership[p.id];
  if (!o) return '<span class="muted">—</span>';
  const t = teamById(o.teamId);
  const me = o.teamId === state.myTeamId;
  return `<span class="owner ${me ? "mine" : "riv"}">${t?.name || "?"}<small>${o.price}</small></span>`;
}

function renderHead() {
  els.playerHead.innerHTML = `<tr>${COLUMNS.map((col) => {
    const active = state.sortKey === col.key;
    const arrow = !active ? "" : state.sortDir === "asc" ? " ▲" : " ▼";
    return `<th class="sortable ${active ? "sorted" : ""}" data-sort="${col.key}" title="${col.title || col.label}" scope="col">${col.label}<span class="sort-ind">${arrow}</span></th>`;
  }).join("")}<th aria-label="Azioni"></th></tr>`;
}

function renderTable() {
  const rows = filteredPlayers();
  els.resultCount.textContent = `${rows.length} in vista · sort ${state.sortKey}`;
  renderHead();
  els.playerTable.innerHTML = rows.map((p) => {
    const own = state.ownership[p.id];
    const rowClass = own?.teamId === state.myTeamId ? "mine" : own ? "taken" : "";
    const pri = priorityScore(p);
    const penHtml = p.penalty
      ? `<span class="badge pen pen-${p.penalty}" title="${p.penaltyLabel || ""}">${p.penalty}° ${p.penalty === 1 ? "rigorista" : "scelta"}</span>`
      : '<span class="muted">no</span>';
    const fairTitle = [
      p.fairLow != null || p.fairHigh != null ? `${p.fairLow ?? "?"}–${p.fairHigh ?? "?"}` : null,
      p.mockLow != null ? `mock ${p.mockLow}–${p.mockHigh}` : null,
    ].filter(Boolean).join(" · ");
    let actions = "";
    if (own) actions = `<button class="btn small danger" data-action="release" data-id="${p.id}">Libera</button>`;
    else actions = `<button class="btn small" data-action="buy" data-id="${p.id}">Compra</button>
      <button class="btn small ghost dark" data-action="take" data-id="${p.id}">Preso</button>`;
    return `<tr class="${rowClass}">
      <td><strong class="pri">${pri < 0 ? "—" : pri}</strong></td>
      <td><span class="badge role-${p.role}">${p.role}</span></td>
      <td><div class="name">${p.name}</div></td>
      <td>${p.team || "-"}</td>
      <td>${p.fvm}</td>
      <td title="${escapeAttr(fairTitle)}">${p.fair ?? "—"}</td>
      <td>${p.leave ?? "—"}</td>
      <td>${fmtTraffic(p)}</td>
      <td><strong>${p.cap}</strong></td>
      <td>${fmtFm(p.fmPrev)}</td>
      <td>${fmtTit(p)}</td>
      <td>${fmtFit(p)}</td>
      <td>${p.age ?? "—"}</td>
      <td>${penHtml}</td>
      <td><span class="badge ${p.tier}">${TIER_LABEL[p.tier] || p.tier}</span></td>
      <td>${fmtOwner(p)}</td>
      <td class="note-cell"><div class="note" title="${escapeAttr(p.note || "")}">${p.note || "—"}</div></td>
      <td class="actions">${actions}</td>
    </tr>`;
  }).join("");
}

function renderRoster() {
  const focusId = state.selectedTeamId || state.myTeamId;
  const focus = teamById(focusId) || teamById(state.myTeamId);
  const plan = currentBudget();
  const teamTabs = state.teams.map((t) =>
    `<button type="button" class="chip ${t.id === focusId ? "active" : ""}" data-action="select-team" data-id="${t.id}">${t.name}${t.id === state.myTeamId ? " ★" : ""}</button>`
  ).join("");

  const blocks = ROLES.map((role) => {
    const mine = teamByRole(focus.id, role);
    const spent = mine.reduce((s, p) => s + Number(state.ownership[p.id]?.price || 0), 0);
    const planAmt = focus.id === state.myTeamId ? plan[role] : null;
    const list = mine.length === 0
      ? '<li><span class="meta">Nessuno</span><span></span></li>'
      : mine.map((p) => `
        <li><span>${p.name} <span class="meta">${p.team || ""}</span></span>
        <span><strong>${state.ownership[p.id].price}</strong>
        <button class="btn small danger" data-action="release" data-id="${p.id}">×</button></span></li>`).join("");
    return `<div class="role-block ${role === state.auctionRole ? "active-role" : ""}">
      <h3>${ROLE_LABEL[role]}</h3>
      <div class="role-spent ${planAmt != null && spent > planAmt ? "over" : ""}">${spent}${planAmt != null ? `/${planAmt}` : ""} · ${mine.length}/${rosterSlots()[role]}</div>
      <ul>${list}</ul></div>`;
  }).join("");

  els.roster.innerHTML = `
    <div class="roster-tabs">${teamTabs}</div>
    <p class="roster-sum"><strong>${focus.name}</strong> · ${spentByTeam(focus.id)} spesi · ${remainingByTeam(focus.id)} residui</p>
    ${blocks}`;
}

function fillBuyTeamSelect(mode) {
  els.buyTeam.innerHTML = state.teams.map((t) => {
    const rem = remainingByTeam(t.id);
    return `<option value="${t.id}">${t.name} (${rem} residui)${t.id === state.myTeamId ? " · tu" : ""}</option>`;
  }).join("");
  if (mode === "take") {
    const rival = rivals().find((t) => slotsLeftTeam(t.id, state.auctionRole) > 0) || rivals()[0];
    if (rival) els.buyTeam.value = rival.id;
  } else {
    els.buyTeam.value = state.myTeamId;
  }
  const teamField = els.buyTeam.closest(".field");
  if (teamField) teamField.hidden = mode === "buy";
  els.buyTeam.disabled = mode === "buy";
}

function render() {
  maybeAdvanceRole();
  renderTeamsBar();
  renderAuctionBanner();
  renderStats();
  renderScenarios();
  renderStrategy();
  renderPriorities();
  renderTable();
  renderRoster();
  syncRoleChips();
  persist();
}

function setSort(key) {
  if (state.sortKey === key) state.sortDir = state.sortDir === "asc" ? "desc" : "asc";
  else {
    state.sortKey = key;
    state.sortDir = COLUMNS.find((c) => c.key === key)?.type === "text" ? "asc" : "desc";
  }
  render();
}

function openAssign(id, mode) {
  const player = state.players.find((p) => p.id === id);
  if (!player) return;
  if (state.roleLock && player.role !== state.auctionRole) {
    return alert(`Fase attuale: ${ROLE_LABEL[state.auctionRole]}`);
  }
  state.pendingId = id;
  state.pendingMode = mode;
  fillBuyTeamSelect(mode);
  els.buyTitle.textContent = mode === "buy" ? `Compra ${player.name}` : `Assegna ${player.name} a un rivale`;
  const teamId = els.buyTeam.value;
  const rem = remainingByTeam(teamId);
  const defaultPrice = Math.min(
    player.cap || player.fvm || 1,
    Math.max(1, rem),
    mode === "buy" ? (safeSpend(player.role) || rem) : Math.max(1, Math.round(player.fair || player.cap || 10))
  );
  els.buyPrice.value = defaultPrice;
  els.buyHint.textContent = [
    `Pri ${priorityScore(player)}`,
    `FVM ${player.fvm}`,
    `Fair ${player.fair ?? "—"} (${player.fairLow ?? "?"}–${player.fairHigh ?? "?"})`,
    player.leave != null ? `Leave ${player.leave}` : null,
    player.traffic ? `Semaforo ${TRAFFIC_LABEL[player.traffic] || player.traffic}` : null,
    `Cap ${player.cap}`,
    mode === "buy" ? `Spend-safe ${safeSpend(player.role)}` : null,
    player.starterProb != null ? `Tit ${player.starterProb}%` : null,
    player.fitness != null ? `Forma ${player.fitnessLabel || ""} ${player.fitness}` : null,
    player.minutesEst != null ? `Min~${player.minutesEst}'` : null,
    player.per90Prod != null ? `Prod/90 ${player.per90Prod}` : null,
    player.note ? `${player.note.slice(0, 180)}…` : null,
  ].filter(Boolean).join(" · ");
  els.buyDialog.showModal();
  els.buyPrice.focus();
  els.buyPrice.select();
}

function confirmAssign(price) {
  const player = state.players.find((p) => p.id === state.pendingId);
  if (!player) return false;
  const teamId = els.buyTeam.value;
  const team = teamById(teamId);
  if (!team) return alert("Squadra non valida."), false;
  if (!Number.isFinite(price) || price < 1) return alert("Prezzo non valido."), false;
  if (price > remainingByTeam(teamId)) return alert(`${team.name} non ha abbastanza crediti.`), false;
  if (slotsLeftTeam(teamId, player.role) <= 0) return alert(`${team.name}: rosa ${player.role} completa.`), false;

  const isMe = teamId === state.myTeamId;
  if (isMe && price > safeSpend(player.role) && !confirm(`Sopra spend-safe ${safeSpend(player.role)}. Confermi?`)) return false;
  if (player.leave != null && price > player.leave && !confirm(`Sopra leave mock ${player.leave}. Confermi?`)) return false;
  if (price > (player.cap || player.fvm) * 1.15 && !confirm(`Oltre cap ${player.cap} (+15%). Confermi?`)) return false;

  state.ownership[state.pendingId] = { status: isMe ? "mine" : "taken", price, teamId };
  state.pendingId = null;
  state.selectedTeamId = teamId;
  render();
  return true;
}

function releasePlayer(id) {
  delete state.ownership[id];
  render();
}

function onAction(e) {
  const btn = e.target.closest("[data-action]");
  if (!btn) return;
  const { action, id } = btn.dataset;
  if (action === "buy") openAssign(id, "buy");
  if (action === "take") openAssign(id, "take");
  if (action === "release") releasePlayer(id);
  if (action === "select-team") { state.selectedTeamId = id; render(); }
  if (action === "set-me") {
    state.myTeamId = id;
    state.selectedTeamId = id;
    state.teams = state.teams.map((t) => ({ ...t, isMe: t.id === id }));
    render();
  }
}

function bindEvents() {
  els.budgetPlan.addEventListener("change", (e) => { state.plan = e.target.value; render(); });
  els.search.addEventListener("input", (e) => { state.query = e.target.value; render(); });
  els.onlyTiered.addEventListener("change", (e) => { state.onlyTiered = e.target.checked; render(); });
  els.onlyPenalties.addEventListener("change", (e) => { state.onlyPenalties = e.target.checked; render(); });
  els.hideTaken.addEventListener("change", (e) => { state.hideTaken = e.target.checked; render(); });
  els.roleLock.addEventListener("change", (e) => {
    state.roleLock = e.target.checked;
    if (state.roleLock) state.roleFilter = state.auctionRole;
    render();
  });
  els.roleChips.addEventListener("click", (e) => {
    const btn = e.target.closest("[data-role]");
    if (!btn || btn.disabled || state.roleLock) return;
    state.roleFilter = btn.dataset.role;
    render();
  });
  els.playerHead.addEventListener("click", (e) => {
    const th = e.target.closest("[data-sort]");
    if (th) setSort(th.dataset.sort);
  });
  els.playerTable.addEventListener("click", onAction);
  els.roster.addEventListener("click", onAction);
  els.priorityBox.addEventListener("click", onAction);
  els.teamsBar.addEventListener("click", onAction);
  const renameTeamFromInput = (input) => {
    const id = input.dataset.teamName;
    if (!id) return;
    const name = input.value.trim() || "Squadra";
    const prev = state.teams.find((t) => t.id === id)?.name;
    if (prev === name) return;
    state.teams = state.teams.map((t) => (t.id === id ? { ...t, name } : t));
    persist();
    // Aggiorna solo etichette dipendenti dal nome, senza re-montare gli input (evita perdita focus/value).
    document.querySelectorAll(`#buyTeam option[value="${id}"]`).forEach((opt) => {
      const rem = remainingByTeam(id);
      opt.textContent = `${name} (${rem} residui)${id === state.myTeamId ? " · tu" : ""}`;
    });
    document.querySelectorAll(`#roster [data-action="select-team"][data-id="${id}"]`).forEach((btn) => {
      btn.textContent = `${name}${id === state.myTeamId ? " ★" : ""}`;
    });
  };
  els.teamsBar.addEventListener("input", (e) => {
    const input = e.target.closest("[data-team-name]");
    if (input) renameTeamFromInput(input);
  });
  els.teamsBar.addEventListener("change", (e) => {
    const input = e.target.closest("[data-team-name]");
    if (input) renameTeamFromInput(input);
  });
  els.teamsBar.addEventListener("focusout", (e) => {
    const input = e.target.closest("[data-team-name]");
    if (input) renameTeamFromInput(input);
  });
  els.buyTeam.addEventListener("change", () => {
    const rem = remainingByTeam(els.buyTeam.value);
    const cur = Number(els.buyPrice.value) || 1;
    if (cur > rem) els.buyPrice.value = Math.max(1, rem);
  });
  els.resetBtn.addEventListener("click", () => {
    if (!confirm("Azzerare tutti gli acquisti delle 6 squadre e tornare ai Portieri?")) return;
    state.ownership = {};
    state.auctionRole = "P";
    state.roleFilter = "P";
    state.selectedTeamId = state.myTeamId;
    render();
  });
  els.exportBtn.addEventListener("click", exportRoster);
  els.importBtn.addEventListener("click", () => els.importFile.click());
  els.importFile.addEventListener("change", async (e) => {
    const file = e.target.files?.[0];
    e.target.value = "";
    if (!file) return;
    try {
      const text = await file.text();
      const data = JSON.parse(text);
      if (!confirm(`Importare il backup "${file.name}"? Sovrascrive lo stato attuale dell'asta.`)) return;
      importSnapshot(data);
      alert(`Import ok: ${Object.keys(state.ownership).length} assegnazioni ripristinate.`);
    } catch (err) {
      alert(`Import fallito: ${err.message || err}`);
    }
  });
  window.addEventListener("beforeunload", () => {
    persistSync();
  });
  document.addEventListener("visibilitychange", () => {
    if (document.visibilityState === "hidden") persistSync();
  });
  els.buyForm.addEventListener("submit", (e) => {
    if (e.submitter?.value === "cancel") { state.pendingId = null; return; }
    e.preventDefault();
    if (confirmAssign(Number(els.buyPrice.value))) els.buyDialog.close();
  });
}

function normalizePlayer(raw) {
  const cap = raw.cap ?? raw.fvm ?? null;
  const fvm = raw.fvm ?? raw.cap ?? null;
  const fair = raw.fair ?? cap ?? fvm ?? null;
  const fairLow = raw.fairLow ?? (fair != null ? Math.round(fair * 0.88) : null);
  const fairHigh = raw.fairHigh ?? (fair != null ? Math.round(fair * 1.12) : null);
  return {
    id: raw.id,
    name: raw.name,
    team: raw.team,
    role: raw.role,
    fvm,
    cap,
    fair,
    fairLow,
    fairHigh,
    leave: raw.leave ?? null,
    mockLow: raw.mockLow ?? null,
    mockMid: raw.mockMid ?? null,
    mockHigh: raw.mockHigh ?? null,
    traffic: raw.traffic ?? null,
    fmPrev: raw.fmPrev ?? raw.fm_prev ?? null,
    starterProb: raw.starterProb ?? raw.starter_prob ?? raw.playedsExpected ?? null,
    fitness: raw.fitness ?? null,
    fitnessLabel: raw.fitnessLabel ?? raw.fitness_label ?? null,
    age: raw.age ?? null,
    penalty: raw.penalty ?? null,
    penaltyLabel: raw.penaltyLabel ?? raw.penalty_label ?? null,
    tier: raw.tier,
    note: raw.note || "",
    per90Prod: raw.per90Prod ?? raw.per90_prod ?? null,
    per90ProdNoPen: raw.per90ProdNoPen ?? null,
    bonusProxy: raw.bonusProxy ?? raw.bonus_proxy ?? null,
    bonusPure: raw.bonusPure ?? null,
    votePure: raw.votePure ?? null,
    csProxy: raw.csProxy ?? null,
    minutesEst: raw.minutesEst ?? null,
    appsEst: raw.appsEst ?? null,
    mpg: raw.mpg ?? null,
    startRate: raw.startRate ?? null,
    benchRate: raw.benchRate ?? null,
    injuryRisk: raw.injuryRisk ?? null,
    injuryDaysOut: raw.injuryDaysOut ?? null,
    injuryMuscular: raw.injuryMuscular ?? null,
    injuryMultiComp: raw.injuryMultiComp ?? null,
    teamAtt: raw.teamAtt ?? null,
    teamDef: raw.teamDef ?? null,
    teamStyle: raw.teamStyle ?? null,
    teamSched: raw.teamSched ?? null,
    teamModule: raw.teamModule ?? null,
    scenarios: raw.scenarios ?? null,
  };
}

async function init() {
  loadSaved();
  await hydrateFromIdbIfNeeded();
  const res = await fetch(`./asta-board-2026-27.json?v=${ASSET_V}`, { cache: "no-store" });
  if (!res.ok) throw new Error("Impossibile caricare asta-board-2026-27.json");
  const data = await res.json();
  state.meta = data.meta;
  state.players = data.players.map(normalizePlayer);

  if (!state.teams.length) state.teams = defaultTeams();
  if (!state.teams.some((t) => t.id === state.myTeamId)) {
    state.myTeamId = state.teams.find((t) => t.isMe)?.id || state.teams[0].id;
  }
  if (!state.teams.some((t) => t.id === state.selectedTeamId)) {
    state.selectedTeamId = state.myTeamId;
  }
  for (const [, o] of Object.entries(state.ownership)) {
    if (o && !o.teamId) {
      o.teamId = o.status === "mine" ? state.myTeamId : (rivals()[0]?.id || state.teams[1]?.id);
    }
  }
  if (!state.meta.budgets[state.plan]) state.plan = Object.keys(state.meta.budgets)[0];
  if (!ROLES.includes(state.auctionRole)) state.auctionRole = "P";
  if (state.roleLock) state.roleFilter = state.auctionRole;

  els.onlyTiered.checked = state.onlyTiered;
  els.onlyPenalties.checked = state.onlyPenalties;
  els.hideTaken.checked = state.hideTaken;
  els.roleLock.checked = state.roleLock;

  renderPlans();
  bindEvents();
  render();
  updateSaveStatus(true, Object.keys(state.ownership).length ? "ripristinato" : "pronto");
}

init().catch((err) => {
  document.body.innerHTML = `<pre style="color:#fff;padding:24px">Errore avvio tool: ${err.message}</pre>`;
});
