const STORAGE_KEY = "fantacalcio-asta-2026-27-v2";
const ROLES = ["P", "D", "C", "A"];
const ROLE_LABEL = {
  P: "Portieri",
  D: "Difensori",
  C: "Centrocampisti",
  A: "Attaccanti",
};
const TIER_LABEL = {
  super_top: "Super top",
  top: "Top",
  top_bonus: "Top bonus",
  modificatore: "Modificatore",
  affidabile: "Affidabile",
  bonus: "Bonus",
  semi: "Semi",
  value: "Value",
  pool: "Pool",
};

const state = {
  meta: null,
  players: [],
  plan: "modificatore_first",
  roleFilter: "ALL",
  query: "",
  onlyTiered: true,
  hideTaken: false,
  ownership: {},
  pendingId: null,
};

const els = {
  budgetPlan: document.getElementById("budgetPlan"),
  resetBtn: document.getElementById("resetBtn"),
  exportBtn: document.getElementById("exportBtn"),
  stats: document.getElementById("stats"),
  search: document.getElementById("search"),
  roleChips: document.getElementById("roleChips"),
  onlyTiered: document.getElementById("onlyTiered"),
  hideTaken: document.getElementById("hideTaken"),
  resultCount: document.getElementById("resultCount"),
  playerTable: document.getElementById("playerTable"),
  roster: document.getElementById("roster"),
  buyDialog: document.getElementById("buyDialog"),
  buyForm: document.getElementById("buyForm"),
  buyTitle: document.getElementById("buyTitle"),
  buyPrice: document.getElementById("buyPrice"),
  buyHint: document.getElementById("buyHint"),
};

function loadSaved() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return;
    const saved = JSON.parse(raw);
    state.plan = saved.plan || state.plan;
    state.ownership = saved.ownership || {};
    state.onlyTiered = saved.onlyTiered ?? true;
    state.hideTaken = saved.hideTaken ?? false;
  } catch {
    /* ignore */
  }
}

function persist() {
  localStorage.setItem(
    STORAGE_KEY,
    JSON.stringify({
      plan: state.plan,
      ownership: state.ownership,
      onlyTiered: state.onlyTiered,
      hideTaken: state.hideTaken,
    })
  );
}

function currentBudget() {
  return state.meta.budgets[state.plan];
}

function rosterSlots() {
  return state.meta.roster;
}

function mineByRole(role) {
  return state.players.filter(
    (p) => p.role === role && state.ownership[p.id]?.status === "mine"
  );
}

function spentByRole(role) {
  return mineByRole(role).reduce(
    (sum, p) => sum + Number(state.ownership[p.id]?.price || 0),
    0
  );
}

function totalSpent() {
  return ROLES.reduce((sum, role) => sum + spentByRole(role), 0);
}

function remainingBudget() {
  return Number(state.meta.budget) - totalSpent();
}

function remainingSlots(role) {
  return Number(rosterSlots()[role]) - mineByRole(role).length;
}

function filteredPlayers() {
  const q = state.query.trim().toLowerCase();
  return state.players
    .filter((p) => (state.roleFilter === "ALL" ? true : p.role === state.roleFilter))
    .filter((p) => (state.onlyTiered ? p.tier !== "pool" : true))
    .filter((p) => {
      if (!state.hideTaken) return true;
      return state.ownership[p.id]?.status !== "taken";
    })
    .filter((p) => {
      if (!q) return true;
      return (
        p.name.toLowerCase().includes(q) ||
        String(p.team || "")
          .toLowerCase()
          .includes(q) ||
        String(TIER_LABEL[p.tier] || "")
          .toLowerCase()
          .includes(q)
      );
    })
    .sort((a, b) => b.fvm - a.fvm || a.name.localeCompare(b.name, "it"));
}

function renderPlans() {
  els.budgetPlan.innerHTML = Object.entries(state.meta.budgets)
    .map(([key, b]) => {
      const selected = key === state.plan ? "selected" : "";
      return `<option value="${key}" ${selected}>${b.label} · P${b.P}/D${b.D}/C${b.C}/A${b.A}</option>`;
    })
    .join("");
}

function renderStats() {
  const plan = currentBudget();
  const rem = remainingBudget();
  const cards = [
    { label: "Budget residuo", value: rem, cls: rem < 50 ? "warn" : "ok" },
    { label: "Speso", value: totalSpent(), cls: "" },
    ...ROLES.map((role) => {
      const left = plan[role] - spentByRole(role);
      return {
        label: `${role} residuo piano`,
        value: `${left} · ${mineByRole(role).length}/${rosterSlots()[role]}`,
        cls: left < 0 ? "warn" : "",
      };
    }),
  ];
  els.stats.innerHTML = cards
    .map(
      (c) =>
        `<div class="stat ${c.cls}"><strong>${c.value}</strong><span>${c.label}</span></div>`
    )
    .join("");
}

function renderTable() {
  const rows = filteredPlayers();
  els.resultCount.textContent = `${rows.length} giocatori`;
  els.playerTable.innerHTML = rows
    .map((p) => {
      const own = state.ownership[p.id];
      const rowClass =
        own?.status === "mine" ? "mine" : own?.status === "taken" ? "taken" : "";
      const tier = TIER_LABEL[p.tier] || p.tier;
      const flags = (p.flags || []).length
        ? `<div class="meta">${p.flags.join(" · ")}</div>`
        : "";
      let actions = "";
      if (own?.status === "mine") {
        actions = `<button class="btn small danger" data-action="release" data-id="${p.id}">Rimuovi</button>`;
      } else if (own?.status === "taken") {
        actions = `<button class="btn small ghost dark" data-action="untake" data-id="${p.id}">Libera</button>`;
      } else {
        actions = `<button class="btn small" data-action="buy" data-id="${p.id}">Compra</button>
          <button class="btn small ghost dark" data-action="take" data-id="${p.id}">Preso</button>`;
      }
      return `<tr class="${rowClass}">
        <td><span class="badge role-${p.role}">${p.role}</span></td>
        <td><div class="name">${p.name}</div>${flags}</td>
        <td>${p.team || "-"}</td>
        <td>${p.fvm}</td>
        <td><strong>${p.cap}</strong></td>
        <td><span class="badge ${p.tier}">${tier}</span></td>
        <td class="actions">${actions}</td>
      </tr>`;
    })
    .join("");
}

function renderRoster() {
  const plan = currentBudget();
  els.roster.innerHTML = ROLES.map((role) => {
    const mine = mineByRole(role);
    const spent = spentByRole(role);
    const over = spent > plan[role];
    const list =
      mine.length === 0
        ? `<li><span class="meta">Nessuno</span><span></span></li>`
        : mine
            .map((p) => {
              const price = state.ownership[p.id].price;
              return `<li>
                <span>${p.name} <span class="meta">${p.team || ""}</span></span>
                <span>
                  <strong>${price}</strong>
                  <button class="btn small danger" data-action="release" data-id="${p.id}">×</button>
                </span>
              </li>`;
            })
            .join("");
    return `<div class="role-block">
      <h3>${ROLE_LABEL[role]}</h3>
      <div class="role-spent ${over ? "over" : ""}">${spent}/${plan[role]} crediti · ${mine.length}/${rosterSlots()[role]} slot</div>
      <ul>${list}</ul>
    </div>`;
  }).join("");
}

function render() {
  renderStats();
  renderTable();
  renderRoster();
  persist();
}

function openBuy(id) {
  const player = state.players.find((p) => p.id === id);
  if (!player) return;
  if (remainingSlots(player.role) <= 0) {
    alert(`Rosa ${player.role} completa (${rosterSlots()[player.role]} slot).`);
    return;
  }
  state.pendingId = id;
  els.buyTitle.textContent = `Compra ${player.name}`;
  els.buyPrice.value = Math.min(player.cap, Math.max(1, remainingBudget()));
  els.buyHint.textContent = `FVM ${player.fvm} · Cap ${player.cap} · Residuo ${remainingBudget()} · Slot ${player.role} ${remainingSlots(player.role)}`;
  els.buyDialog.showModal();
  els.buyPrice.focus();
  els.buyPrice.select();
}

function confirmBuy(price) {
  const id = state.pendingId;
  const player = state.players.find((p) => p.id === id);
  if (!player) return false;
  if (!Number.isFinite(price) || price < 1 || price > remainingBudget()) {
    alert("Prezzo non valido rispetto al budget residuo.");
    return false;
  }
  if (price > player.cap * 1.15) {
    const ok = confirm(
      `Stai pagando ${price} oltre il cap ${player.cap} (+15%). Confermi?`
    );
    if (!ok) return false;
  }
  state.ownership[id] = { status: "mine", price };
  state.pendingId = null;
  render();
  return true;
}

function markTaken(id) {
  state.ownership[id] = { status: "taken", price: 0 };
  render();
}

function releasePlayer(id) {
  delete state.ownership[id];
  render();
}

function exportRoster() {
  const rosa = ROLES.flatMap((role) =>
    mineByRole(role).map((p) => ({
      role,
      name: p.name,
      team: p.team,
      price: state.ownership[p.id].price,
      fvm: p.fvm,
      cap: p.cap,
    }))
  );
  const payload = {
    exportedAt: new Date().toISOString(),
    plan: state.plan,
    budget: state.meta.budget,
    spent: totalSpent(),
    remaining: remainingBudget(),
    rosa,
  };
  const blob = new Blob([JSON.stringify(payload, null, 2)], {
    type: "application/json",
  });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
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
  els.budgetPlan.addEventListener("change", (e) => {
    state.plan = e.target.value;
    render();
  });
  els.search.addEventListener("input", (e) => {
    state.query = e.target.value;
    render();
  });
  els.onlyTiered.addEventListener("change", (e) => {
    state.onlyTiered = e.target.checked;
    render();
  });
  els.hideTaken.addEventListener("change", (e) => {
    state.hideTaken = e.target.checked;
    render();
  });
  els.roleChips.addEventListener("click", (e) => {
    const btn = e.target.closest("[data-role]");
    if (!btn) return;
    state.roleFilter = btn.dataset.role;
    [...els.roleChips.querySelectorAll(".chip")].forEach((c) =>
      c.classList.toggle("active", c === btn)
    );
    render();
  });
  els.playerTable.addEventListener("click", onAction);
  els.roster.addEventListener("click", onAction);
  els.resetBtn.addEventListener("click", () => {
    if (confirm("Azzerare rosa e giocatori presi?")) {
      state.ownership = {};
      render();
    }
  });
  els.exportBtn.addEventListener("click", exportRoster);
  els.buyForm.addEventListener("submit", (e) => {
    if (e.submitter?.value === "cancel") {
      state.pendingId = null;
      return;
    }
    e.preventDefault();
    if (confirmBuy(Number(els.buyPrice.value))) {
      els.buyDialog.close();
    }
  });
}

async function init() {
  loadSaved();
  const res = await fetch("./asta-board-2026-27.json", { cache: "no-store" });
  if (!res.ok) throw new Error("Impossibile caricare asta-board-2026-27.json");
  const data = await res.json();
  state.meta = data.meta;
  state.players = data.players;
  if (!state.meta.budgets[state.plan]) {
    state.plan = Object.keys(state.meta.budgets)[0];
  }
  els.onlyTiered.checked = state.onlyTiered;
  els.hideTaken.checked = state.hideTaken;
  renderPlans();
  bindEvents();
  render();
}

init().catch((err) => {
  document.body.innerHTML = `<pre style="color:#fff;padding:24px">Errore avvio tool: ${err.message}</pre>`;
});
