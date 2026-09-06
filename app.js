const STORAGE_KEY = "fantacalcio-asta-2026-27-v5";
const ASSET_V = "20260906e";
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
const COLUMNS = [
  { key: "priority", label: "Pri", type: "num", title: "Priorità dinamica" },
  { key: "role", label: "Ruolo", type: "text" },
  { key: "name", label: "Giocatore", type: "text" },
  { key: "team", label: "Sq", type: "text" },
  { key: "fvm", label: "FVM", type: "num" },
  { key: "cap", label: "Cap", type: "num" },
  { key: "fmPrev", label: "FM 25/26", type: "num", title: "Fantamedia 2025/26" },
  { key: "starterProb", label: "Tit%", type: "num", title: "Probabilità titolare" },
  { key: "fitness", label: "Forma", type: "num", title: "Affidabilità fisica" },
  { key: "age", label: "Età", type: "num" },
  { key: "penalty", label: "Rigori", type: "num" },
  { key: "tier", label: "Fascia", type: "tier" },
  { key: "note", label: "Nota", type: "text" },
];

const state = {
  meta: null, players: [], plan: "modificatore_first", roleFilter: "P", query: "",
  onlyTiered: false, onlyPenalties: false, hideTaken: true, ownership: {}, pendingId: null,
  sortKey: "priority", sortDir: "desc", auctionRole: "P", roleLock: true,
};

const els = Object.fromEntries([
  "budgetPlan","resetBtn","exportBtn","stats","search","roleChips","onlyTiered","onlyPenalties",
  "hideTaken","roleLock","resultCount","playerHead","playerTable","roster","buyDialog","buyForm",
  "buyTitle","buyPrice","buyHint","auctionBanner","priorityBox","strategyBox",
].map((id) => [id, document.getElementById(id)]));

function loadSaved() {
  try {
    const saved = JSON.parse(localStorage.getItem(STORAGE_KEY) || "null");
    if (!saved) return;
    Object.assign(state, {
      plan: saved.plan || state.plan,
      ownership: saved.ownership || {},
      onlyTiered: saved.onlyTiered ?? false,
      onlyPenalties: saved.onlyPenalties ?? false,
      hideTaken: saved.hideTaken ?? true,
      sortKey: saved.sortKey || "priority",
      sortDir: saved.sortDir || "desc",
      auctionRole: saved.auctionRole || "P",
      roleLock: saved.roleLock ?? true,
    });
    state.roleFilter = state.roleLock ? state.auctionRole : (saved.roleFilter || state.auctionRole);
  } catch {}
}
function persist() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify({
    plan: state.plan, ownership: state.ownership, onlyTiered: state.onlyTiered,
    onlyPenalties: state.onlyPenalties, hideTaken: state.hideTaken, sortKey: state.sortKey,
    sortDir: state.sortDir, auctionRole: state.auctionRole, roleLock: state.roleLock,
    roleFilter: state.roleFilter,
  }));
}

const currentBudget = () => state.meta.budgets[state.plan];
const rosterSlots = () => state.meta.roster;
const teamsCount = () => Number(state.meta.teams || 6);
const mineByRole = (role) => state.players.filter((p) => p.role === role && state.ownership[p.id]?.status === "mine");
const spentByRole = (role) => mineByRole(role).reduce((s, p) => s + Number(state.ownership[p.id]?.price || 0), 0);
const totalSpent = () => ROLES.reduce((s, r) => s + spentByRole(r), 0);
const remainingBudget = () => Number(state.meta.budget) - totalSpent();
const remainingSlots = (role) => Number(rosterSlots()[role]) - mineByRole(role).length;
const marketTaken = (role) => state.players.filter((p) => p.role === role && ["mine","taken"].includes(state.ownership[p.id]?.status)).length;
const marketTarget = (role) => Number(rosterSlots()[role]) * teamsCount();
const roleBudgetLeft = (role) => Number(currentBudget()[role]) - spentByRole(role);
function safeSpend(role) {
  const slots = remainingSlots(role);
  const left = roleBudgetLeft(role);
  if (slots <= 0) return 0;
  return Math.max(1, left - Math.max(0, slots - 1));
}

function priorityScore(p) {
  const role = state.auctionRole;
  if (p.role !== role) return -1;
  if (["mine","taken"].includes(state.ownership[p.id]?.status)) return -1;
  const slotsLeft = remainingSlots(role);
  if (slotsLeft <= 0) return -1;
  const roleLeft = roleBudgetLeft(role);
  const maxAfford = safeSpend(role);
  const mine = mineByRole(role);
  const hasElite = mine.some((m) => (TIER_RANK[m.tier] || 0) >= 9);
  const marketLeft = Math.max(0, marketTarget(role) - marketTaken(role));
  let s = 0;
  s += (p.starterProb || 0) * 0.3;
  s += (p.fitness || 50) * 0.24;
  s += Math.min(100, ((p.fmPrev || 5.8) / 9) * 100) * 0.12;
  s += (TIER_RANK[p.tier] || 1) * 7;
  if (p.penalty === 1) s += 11; else if (p.penalty === 2) s += 5; else if (p.penalty === 3) s += 2;
  const value = ((p.fmPrev || 6) * ((p.starterProb || 50) / 100) * ((p.fitness || 50) / 100)) / Math.max(p.cap, 1);
  s += Math.min(18, value * 35);
  if (p.cap > remainingBudget()) s -= 40;
  else if (p.cap > maxAfford) s -= 22;
  else if (slotsLeft > 1 && p.cap > roleLeft * 0.6) s -= 10;
  else if (p.cap <= maxAfford * 0.55 && (TIER_RANK[p.tier] || 0) >= 7) s += 6;
  if (hasElite && (TIER_RANK[p.tier] || 0) >= 9) s -= 18;
  if (hasElite && (p.fitness || 0) >= 75 && p.cap <= maxAfford) s += 8;
  if (role === "P" && mine.some((m) => (m.fitness || 0) >= 70) && (p.fitness || 0) < 60) s -= 8;
  if (slotsLeft > 0 && marketLeft <= slotsLeft * teamsCount() * 0.35) s += (p.starterProb || 0) * 0.08;
  if ((p.fitness || 100) < 40) s -= 10;
  if ((p.age || 0) >= 34) s -= 4;
  return Math.round(s * 10) / 10;
}

function priorityWhy(p) {
  const bits = [];
  if ((p.starterProb || 0) >= 80) bits.push("titolare");
  if ((p.fitness || 0) >= 75) bits.push("forma ok");
  if ((p.fitness || 0) < 45) bits.push("rischio fisico");
  if (p.penalty === 1) bits.push("1° rigore");
  if ((TIER_RANK[p.tier] || 0) >= 9) bits.push("fascia top");
  bits.push(p.cap <= safeSpend(p.role) ? "nel budget ruolo" : "oltre spend-safe");
  if ((p.age || 0) >= 33) bits.push(`età ${p.age}`);
  return bits.slice(0, 4).join(" · ");
}

function sortValue(p, key, type) {
  if (key === "priority") return priorityScore(p);
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
  let cmp = typeof av === "number" && typeof bv === "number" ? av - bv : String(av).localeCompare(String(bv), "it", { sensitivity: "base" });
  if (cmp !== 0) return cmp * dir;
  return priorityScore(b) - priorityScore(a) || b.fvm - a.fvm;
}

function activeRoleFilter() { return state.roleLock ? state.auctionRole : state.roleFilter; }

function filteredPlayers() {
  const q = state.query.trim().toLowerCase();
  const role = activeRoleFilter();
  return state.players
    .filter((p) => (role === "ALL" ? true : p.role === role))
    .filter((p) => (state.onlyTiered ? p.tier !== "pool" : true))
    .filter((p) => (state.onlyPenalties ? Boolean(p.penalty) : true))
    .filter((p) => (!state.hideTaken ? true : state.ownership[p.id]?.status !== "taken"))
    .filter((p) => !q || [p.name, p.team, TIER_LABEL[p.tier], p.note, p.penaltyLabel, p.fitnessLabel].some((x) => String(x || "").toLowerCase().includes(q)))
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

function renderPlans() {
  els.budgetPlan.innerHTML = Object.entries(state.meta.budgets).map(([key, b]) =>
    `<option value="${key}" ${key === state.plan ? "selected" : ""}>${b.label} · P${b.P}/D${b.D}/C${b.C}/A${b.A}</option>`
  ).join("");
}

function renderStats() {
  const plan = currentBudget();
  const rem = remainingBudget();
  const role = state.auctionRole;
  const cards = [
    { label: "Budget residuo", value: rem, cls: rem < 50 ? "warn" : "ok" },
    { label: `Tu · ${ROLE_LABEL[role]}`, value: `${mineByRole(role).length}/${rosterSlots()[role]}`, cls: "ok" },
    { label: "Mercato ruolo", value: `${marketTaken(role)}/${marketTarget(role)}`, cls: "" },
    ...ROLES.map((r) => {
      const left = plan[r] - spentByRole(r);
      return { label: `${r} piano`, value: `${left} · ${mineByRole(r).length}/${rosterSlots()[r]}`, cls: left < 0 ? "warn" : r === role ? "ok" : "" };
    }),
  ];
  els.stats.innerHTML = cards.map((c) => `<div class="stat ${c.cls}"><strong>${c.value}</strong><span>${c.label}</span></div>`).join("");
}

function renderAuctionBanner() {
  const role = state.auctionRole;
  els.auctionBanner.innerHTML = `
    <div class="auction-main">
      <p class="eyebrow">Asta a ruoli · motore scientifico</p>
      <h2>Fase <span>${ROLE_LABEL[role]}</span></h2>
      <p>Tu <strong>${mineByRole(role).length}/${rosterSlots()[role]}</strong> · Mercato <strong>${marketTaken(role)}/${marketTarget(role)}</strong> · Budget ruolo <strong>${roleBudgetLeft(role)}</strong> · spend-safe <strong>${safeSpend(role)}</strong></p>
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
  const role = state.auctionRole;
  const tips = {
    P: "1 cemento (Tit%+Forma alti), poi titolari low-cost. Non bruciare >55% del budget P sul primo se sei biporta.",
    D: "Prima voti mod (centrali solidi), poi 1 esterno bonus sotto spend-safe. Evita Vetro cari.",
    C: "Max uno tra Paz/Calha/McT. Poi rigoristi/bonus con Forma ≥55. Se i top scappano, ruota su value.",
    A: "Se Malen > cap, passa al 2+2. Preferisci FM+Tit%+Forma al nome. Mai Vetro a prezzo pieno.",
  };
  const eliteGone = state.players.filter((p) => p.role === role && (TIER_RANK[p.tier] || 0) >= 9 && ["taken","mine"].includes(state.ownership[p.id]?.status)).length;
  els.strategyBox.innerHTML = `
    <div class="panel-head"><h2>Strategia live</h2></div>
    <p class="strategy-lead">${tips[role]}</p>
    <ul>
      <li>Slot da riempire: <strong>${remainingSlots(role)}</strong></li>
      <li>Top già usciti nel ruolo: <strong>${eliteGone}</strong></li>
      <li>Spend-safe: <strong>${safeSpend(role)}</strong></li>
      <li>Pri ricalcolata a ogni Compra/Preso.</li>
    </ul>`;
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
        <span class="meta">${p.team} · cap ${p.cap} · Tit ${p.starterProb ?? "—"}% · Forma ${p.fitness ?? "—"}</span>
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
    const rowClass = own?.status === "mine" ? "mine" : own?.status === "taken" ? "taken" : "";
    const pri = priorityScore(p);
    const penHtml = p.penalty
      ? `<span class="badge pen pen-${p.penalty}" title="${p.penaltyLabel || ""}">${p.penalty}° ${p.penalty === 1 ? "rigorista" : "scelta"}</span>`
      : '<span class="muted">no</span>';
    let actions = "";
    if (own?.status === "mine") actions = `<button class="btn small danger" data-action="release" data-id="${p.id}">Rimuovi</button>`;
    else if (own?.status === "taken") actions = `<button class="btn small ghost dark" data-action="untake" data-id="${p.id}">Libera</button>`;
    else actions = `<button class="btn small" data-action="buy" data-id="${p.id}">Compra</button>
      <button class="btn small ghost dark" data-action="take" data-id="${p.id}">Preso</button>`;
    return `<tr class="${rowClass}">
      <td><strong class="pri">${pri < 0 ? "—" : pri}</strong></td>
      <td><span class="badge role-${p.role}">${p.role}</span></td>
      <td><div class="name">${p.name}</div></td>
      <td>${p.team || "-"}</td>
      <td>${p.fvm}</td>
      <td><strong>${p.cap}</strong></td>
      <td>${fmtFm(p.fmPrev)}</td>
      <td>${fmtTit(p)}</td>
      <td>${fmtFit(p)}</td>
      <td>${p.age ?? "—"}</td>
      <td>${penHtml}</td>
      <td><span class="badge ${p.tier}">${TIER_LABEL[p.tier] || p.tier}</span></td>
      <td class="note-cell"><div class="note">${p.note || "—"}</div></td>
      <td class="actions">${actions}</td>
    </tr>`;
  }).join("");
}

function renderRoster() {
  const plan = currentBudget();
  els.roster.innerHTML = ROLES.map((role) => {
    const mine = mineByRole(role);
    const spent = spentByRole(role);
    const list = mine.length === 0 ? '<li><span class="meta">Nessuno</span><span></span></li>' : mine.map((p) => `
      <li><span>${p.name} <span class="meta">${p.team || ""} · F${p.fitness ?? "—"}</span></span>
      <span><strong>${state.ownership[p.id].price}</strong>
      <button class="btn small danger" data-action="release" data-id="${p.id}">×</button></span></li>`).join("");
    return `<div class="role-block ${role === state.auctionRole ? "active-role" : ""}">
      <h3>${ROLE_LABEL[role]}</h3>
      <div class="role-spent ${spent > plan[role] ? "over" : ""}">${spent}/${plan[role]} · ${mine.length}/${rosterSlots()[role]}</div>
      <ul>${list}</ul></div>`;
  }).join("");
}

function render() {
  maybeAdvanceRole();
  renderAuctionBanner();
  renderStats();
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
    state.sortDir = (COLUMNS.find((c) => c.key === key)?.type === "text") ? "asc" : "desc";
  }
  render();
}

function openBuy(id) {
  const player = state.players.find((p) => p.id === id);
  if (!player) return;
  if (state.roleLock && player.role !== state.auctionRole) return alert(`Fase attuale: ${ROLE_LABEL[state.auctionRole]}`);
  if (remainingSlots(player.role) <= 0) return alert(`Rosa ${player.role} completa.`);
  state.pendingId = id;
  els.buyTitle.textContent = `Compra ${player.name}`;
  els.buyPrice.value = Math.min(player.cap, safeSpend(player.role), Math.max(1, remainingBudget()));
  els.buyHint.textContent = [
    `Pri ${priorityScore(player)}`, `FVM ${player.fvm}`, `Cap ${player.cap}`, `Spend-safe ${safeSpend(player.role)}`,
    player.fmPrev != null ? `FM ${Number(player.fmPrev).toFixed(2).replace(".", ",")}` : null,
    player.starterProb != null ? `Tit ${player.starterProb}%` : null,
    player.fitness != null ? `Forma ${player.fitnessLabel} ${player.fitness}` : null,
    player.age != null ? `Età ${player.age}` : null, `Residuo ${remainingBudget()}`, player.note || null,
  ].filter(Boolean).join(" · ");
  els.buyDialog.showModal();
  els.buyPrice.focus();
  els.buyPrice.select();
}

function confirmBuy(price) {
  const player = state.players.find((p) => p.id === state.pendingId);
  if (!player) return false;
  if (!Number.isFinite(price) || price < 1 || price > remainingBudget()) return alert("Prezzo non valido."), false;
  if (price > safeSpend(player.role) && !confirm(`Sopra spend-safe ${safeSpend(player.role)}. Confermi?`)) return false;
  if (price > player.cap * 1.15 && !confirm(`Oltre cap ${player.cap} (+15%). Confermi?`)) return false;
  state.ownership[state.pendingId] = { status: "mine", price };
  state.pendingId = null;
  render();
  return true;
}

function markTaken(id) {
  const player = state.players.find((p) => p.id === id);
  if (state.roleLock && player && player.role !== state.auctionRole) return alert(`Fase attuale: ${ROLE_LABEL[state.auctionRole]}`);
  state.ownership[id] = { status: "taken", price: 0 };
  render();
}
function releasePlayer(id) { delete state.ownership[id]; render(); }

function exportRoster() {
  const rosa = ROLES.flatMap((role) => mineByRole(role).map((p) => ({
    role, name: p.name, team: p.team, price: state.ownership[p.id].price,
    fvm: p.fvm, cap: p.cap, fmPrev: p.fmPrev, starterProb: p.starterProb, fitness: p.fitness, age: p.age,
  })));
  const payload = { exportedAt: new Date().toISOString(), plan: state.plan, auctionRole: state.auctionRole,
    budget: state.meta.budget, spent: totalSpent(), remaining: remainingBudget(), rosa };
  const a = document.createElement("a");
  a.href = URL.createObjectURL(new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" }));
  a.download = "rosa-asta-fantacalcio-2026-27.json";
  a.click();
  URL.revokeObjectURL(a.href);
}

function onAction(e) {
  const btn = e.target.closest("[data-action]");
  if (!btn) return;
  const { action, id } = btn.dataset;
  if (action === "buy") openBuy(id);
  if (action === "take") markTaken(id);
  if (action === "untake" || action === "release") releasePlayer(id);
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
  els.resetBtn.addEventListener("click", () => {
    if (!confirm("Azzerare rosa/presi e tornare ai Portieri?")) return;
    state.ownership = {};
    state.auctionRole = "P";
    state.roleFilter = "P";
    render();
  });
  els.exportBtn.addEventListener("click", exportRoster);
  els.buyForm.addEventListener("submit", (e) => {
    if (e.submitter?.value === "cancel") { state.pendingId = null; return; }
    e.preventDefault();
    if (confirmBuy(Number(els.buyPrice.value))) els.buyDialog.close();
  });
}

async function init() {
  loadSaved();
  const res = await fetch(`./asta-board-2026-27.json?v=${ASSET_V}`, { cache: "no-store" });
  if (!res.ok) throw new Error("Impossibile caricare asta-board-2026-27.json");
  const data = await res.json();
  state.meta = data.meta;
  state.players = data.players;
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
}

init().catch((err) => {
  document.body.innerHTML = `<pre style="color:#fff;padding:24px">Errore avvio tool: ${err.message}</pre>`;
});
