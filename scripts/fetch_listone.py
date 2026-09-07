#!/usr/bin/env python3
"""Scarica listone Classic e genera board asta con note scientifiche + rigoristi."""

from __future__ import annotations

import csv
import json
import re
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date
from html import unescape
from pathlib import Path

from science_data import (
    AGES,
    BUDGET_TOTAL,
    FVM_SCALE,
    OUT_OF_SERIE_A,
    SCENARIO_PLANS,
    TEAM_OVERRIDES,
    advanced_profile,
    assign_gk_depth,
    build_scientific_note,
    fair_price,
    injury_profile,
    minutes_model,
    parse_mantra,
    production_metrics,
    scenario_plans,
    score_fitness,
    team_context,
    to_auction_credits,
    traffic_light,
)

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
PUBLIC = ROOT / "public"
URL = "https://www.fantacalcio.it/quotazioni-fantacalcio/2026-27"
STATS_URL = "https://www.fantacalcio.it/statistiche-serie-a/2025-26"
PREV_SEASON = "2025/26"
PREV_MATCHES = 38
REF_YEAR = 2026
ROLE_MAP = {"p": "P", "d": "D", "c": "C", "a": "A"}
MONTHS_IT = {
    "gen": 1,
    "feb": 2,
    "mar": 3,
    "apr": 4,
    "mag": 5,
    "giu": 6,
    "lug": 7,
    "ago": 8,
    "set": 9,
    "ott": 10,
    "nov": 11,
    "dic": 12,
}

TIERS = {
    "P": {
        "super_top": ["Svilar"],
        "top": ["Vicario", "Martinez Jo.", "Carnesecchi", "Maignan", "Butez"],
        "affidabile": [
            "Meret",
            "Mandas",
            "Skorupski",
            "De Gea",
            "Okoye",
            "Perri",
            "Falcone",
            "Caprile",
        ],
    },
    "D": {
        "super_top": ["Dimarco"],
        "top_bonus": ["Wesley", "Molina N.", "Bremer", "Pavlovic", "Mancini", "Solet"],
        "modificatore": [
            "Akanji",
            "Bastoni",
            "Rrahmani",
            "Kalulu",
            "N'Dicka",
            "Di Lorenzo",
        ],
        "value": ["Ostigard", "Spence", "Bisseck", "Chalobah T.", "Gila", "Scalvini"],
    },
    "C": {
        "super_top": ["Paz N.", "Calhanoglu", "McTominay"],
        "top": ["Orsolini", "Pulisic", "Rabiot", "De Bruyne", "Baturina", "Mora"],
        "bonus": [
            "Da Cunha",
            "Zaccagni",
            "Barella",
            "Zaniolo",
            "Atta",
            "Frattesi",
            "Vlasic",
            "McKennie",
            "Conceicao",
            "Kessie",
            "Samardzic",
        ],
    },
    "A": {
        "super_top": ["Malen", "Martinez L."],
        "top": [
            "Hojlund",
            "Thuram",
            "Ramos G.",
            "Douvikas",
            "Kean",
            "Kolo Muani",
            "Woltemade",
        ],
        "semi": [
            "Scamacca",
            "Davis K.",
            "Berardi",
            "Esposito F.P.",
            "Yildiz",
            "Dybala",
            "Krstovic",
            "De Ketelaere",
            "Laurientè",
            "Simeone",
            "Raspadori",
            "Castro S.",
            "Leao",
            "Colombo",
        ],
    },
}

PENALTIES: dict[str, dict] = {
    "Calhanoglu": {"order": 1, "label": "1° rigorista", "detail": "Inter — designato"},
    "Zielinski": {"order": 2, "label": "2° rigorista", "detail": "Inter — backup"},
    "Martinez L.": {"order": 3, "label": "3° rigorista", "detail": "Inter — terza scelta"},
    "Nkunku": {"order": 1, "label": "1° rigorista", "detail": "Milan — gerarchia aperta, in pole"},
    "Ramos G.": {"order": 2, "label": "2° rigorista", "detail": "Milan — contendente"},
    "Pulisic": {"order": 3, "label": "3° rigorista", "detail": "Milan — terza opzione"},
    "Kolo Muani": {"order": 1, "label": "1° rigorista", "detail": "Juve — designato"},
    "Yildiz": {"order": 2, "label": "2° rigorista", "detail": "Juve — ha calciato nel 25/26"},
    "Locatelli": {"order": 3, "label": "3° rigorista", "detail": "Juve — terza scelta"},
    "De Bruyne": {"order": 1, "label": "1° rigorista", "detail": "Napoli — specialista"},
    "Hojlund": {"order": 2, "label": "2° rigorista", "detail": "Napoli — backup punta"},
    "Politano": {"order": 3, "label": "3° rigorista", "detail": "Napoli — terza scelta"},
    "Malen": {"order": 1, "label": "1° rigorista", "detail": "Roma — ha calciato nel 25/26"},
    "Dybala": {"order": 2, "label": "2° rigorista", "detail": "Roma — classico dal dischetto"},
    "Castro S.": {"order": 3, "label": "3° rigorista", "detail": "Roma — terza scelta"},
    "Scamacca": {"order": 1, "label": "1° rigorista", "detail": "Atalanta — in pole"},
    "Krstovic": {"order": 2, "label": "2° rigorista", "detail": "Atalanta — contendente"},
    "Samardzic": {"order": 3, "label": "3° rigorista", "detail": "Atalanta — terza scelta"},
    "Atta": {"order": 2, "label": "Possibile rigorista", "detail": "Fiorentina — upside piazzati"},
    "Zaccagni": {"order": 1, "label": "1° rigorista", "detail": "Lazio — gerarchia fluida"},
    "Taylor K.": {"order": 2, "label": "2° rigorista", "detail": "Lazio — ballottaggio"},
    "Cataldi": {"order": 3, "label": "3° rigorista", "detail": "Lazio — ha calciato nel 25/26"},
    "Orsolini": {"order": 1, "label": "1° rigorista", "detail": "Bologna — specialista"},
    "Bernardeschi": {"order": 2, "label": "2° rigorista", "detail": "Bologna — backup"},
    "Dovbyk": {"order": 3, "label": "3° rigorista", "detail": "Bologna — terza scelta"},
    "Da Cunha": {"order": 1, "label": "1° rigorista", "detail": "Como — designato"},
    "Douvikas": {"order": 2, "label": "2° rigorista", "detail": "Como — punta backup"},
    "Paz N.": {"order": 3, "label": "3° rigorista", "detail": "Como — occhio ai falli dal dischetto"},
    "Vlasic": {"order": 1, "label": "1° rigorista", "detail": "Torino — designato"},
    "Simeone": {"order": 2, "label": "2° rigorista", "detail": "Torino — backup punta"},
    "Kulenovic": {"order": 3, "label": "3° rigorista", "detail": "Torino — terza scelta"},
    "Davis K.": {"order": 1, "label": "1° rigorista", "detail": "Udinese — designato"},
    "Solet": {"order": 2, "label": "2° rigorista", "detail": "Udinese — backup"},
    "Zaniolo": {"order": 3, "label": "3° rigorista", "detail": "Udinese — terza scelta"},
    "Berardi": {"order": 1, "label": "1° rigorista", "detail": "Sassuolo — specialista"},
    "Laurientè": {"order": 2, "label": "2° rigorista", "detail": "Sassuolo — contendente"},
    "Esposito Se.": {"order": 3, "label": "3° rigorista", "detail": "Sassuolo — terza scelta"},
    "Colombo": {"order": 1, "label": "1° rigorista", "detail": "Genoa — eredita il ruolo"},
    "Ostigard": {"order": 2, "label": "2° rigorista", "detail": "Genoa — backup"},
    "Tourè E.": {"order": 1, "label": "Possibile rigorista", "detail": "Parma — punta candidata"},
    "Valeri": {"order": 3, "label": "3° rigorista", "detail": "Parma — terza scelta"},
    "Kevin Carlos": {"order": 1, "label": "1° rigorista", "detail": "Cagliari — gerarchia aperta"},
    "Maldini": {"order": 2, "label": "2° rigorista", "detail": "Cagliari — contendente"},
    "Mina": {"order": 3, "label": "3° rigorista", "detail": "Cagliari — terza scelta"},
    "Geubbels": {"order": 1, "label": "1° rigorista", "detail": "Lecce — in pole"},
    "Stulic": {"order": 2, "label": "2° rigorista", "detail": "Lecce — ha calciato nel 25/26"},
    "Berisha M.": {"order": 3, "label": "3° rigorista", "detail": "Lecce — terza scelta"},
    "Pessina": {"order": 1, "label": "1° rigorista", "detail": "Monza — designato"},
    "Cutrone": {"order": 2, "label": "2° rigorista", "detail": "Monza — backup"},
    "Petagna": {"order": 3, "label": "3° rigorista", "detail": "Monza — terza scelta"},
    "Adams A.": {"order": 1, "label": "1° rigorista", "detail": "Venezia — in pole"},
    "Adorante": {"order": 2, "label": "2° rigorista", "detail": "Venezia — testa a testa"},
    "Calò": {"order": 1, "label": "1° rigorista", "detail": "Frosinone — designato"},
    "Raimondo": {"order": 2, "label": "2° rigorista", "detail": "Frosinone — backup"},
    "Ghedjemis": {"order": 3, "label": "3° rigorista", "detail": "Frosinone — terza scelta"},
    "Kean": {"order": 2, "label": "Possibile rigorista", "detail": "Como — contendente/backup"},
}

BUDGETS = {
    "modificatore_first": {
        "P": 50,
        "D": 125,
        "C": 135,
        "A": 190,
        "label": "Modificatore first",
        "summary": "Difesa da modificatore + attacco value; Malen solo sotto leave.",
        "playbook": {
            "P": "1 cemento (Tit% alto) + 2 low-cost; non inseguire il secondo big.",
            "D": "Prima i voti mod, poi al massimo 1 esterno bonus sotto spend-safe.",
            "C": "Max uno tra Paz/Calha/McT, poi rigoristi/bonus Forma≥55.",
            "A": "Se Malen > leave (~230) passa al 2+2; altrimenti Malen + profondità.",
        },
    },
    "equilibrata_mod": {
        "P": 45,
        "D": 105,
        "C": 150,
        "A": 200,
        "label": "Equilibrata + mod",
        "summary": "Più peso al centrocampo, difesa snella, A flessibile.",
        "playbook": {
            "P": "Titolare affidabile low-mid, evita overpay sui big.",
            "D": "Cementi mod; esterno solo value (Wesley/Molina), niente Dimarco caro.",
            "C": "Puoi salire su un top C; tieni warchest per 1 bonus secondario.",
            "A": "Malen solo a sconto; altrimenti semi-top + depth.",
        },
    },
    "anti_malen": {
        "P": 40,
        "D": 100,
        "C": 160,
        "A": 200,
        "label": "Anti-Malen (2+2 attacco)",
        "summary": "Lascia Malen se gonfia; costruisci due+due in A e spingi sul C.",
        "playbook": {
            "P": "Tre titolari economici; non bruciare crediti in porta.",
            "D": "Solo modificatore e 1 esterno mid; zero elite di fascia.",
            "C": "Qui investi: 1 top + rigoristi/bonus (Orsolini/Zaccagni/Da Cunha).",
            "A": "2+2 (Lautaro/Thuram/Kean/Douvikas): niente inseguimento su Malen >210–230.",
        },
    },
    "malen_first": {
        "P": 40,
        "D": 90,
        "C": 110,
        "A": 260,
        "label": "Malen first",
        "summary": "Warchest A per prendere Malen; P/D/C snelli senza elite costosi.",
        "playbook": {
            "P": "Skip big se gonfiano: 1 titolare mid (Skorupski/Caprile/…) + 2 da 1–5. Obiettivo ≤40.",
            "D": "Solo cementi da modificatore (Bremer/Mancini/Bastoni a sconto). Niente Dimarco/Wesley elite: ti servono i crediti in A.",
            "C": "Niente Paz/Calha/McT. Max un bonus mid (Orsolini/Zaccagni) + volume di voti. Chiudi il ruolo sotto ~110.",
            "A": "Apri aggressivo su Malen: target mock 215, tetto soft leave 230, hard stop 245 (sotto cap 252). Se lo prendi ≤230 ti restano ~30 per 1 semi cheap + filler a 1. Se supera 245 → abort e ripiega su 2+2 con il warchest residuo (piano Anti-Malen).",
        },
        "malen": {
            "target": 215,
            "leave": 230,
            "hardStop": 245,
            "cap": 252,
            "afterWin": "Con Malen in rosa: 1 attaccante mid-low (Kean/Douvikas/Raspadori a sconto) e il resto a 1 credito. Non comprare un secondo listone.",
            "afterLose": "Se Malen esce ad altri ≤230, non inseguire il piano B a prezzo pieno: prendi Thuram/Lautaro + Kean/Douvikas. Se esce >245 a un rivale, il mercato A si sgonfia: alza aggressività sui semi-top value.",
        },
    },
}

DEFAULT_TEAMS = [
    {"id": "t1", "name": "La mia squadra", "isMe": True},
    {"id": "t2", "name": "Riva 2", "isMe": False},
    {"id": "t3", "name": "Riva 3", "isMe": False},
    {"id": "t4", "name": "Riva 4", "isMe": False},
    {"id": "t5", "name": "Riva 5", "isMe": False},
    {"id": "t6", "name": "Riva 6", "isMe": False},
]


def apply_roster_overrides(players: list[dict]) -> tuple[list[dict], list[dict]]:
    """Corregge maglie / esclude chi è uscito dalla Serie A (lag listone)."""
    caveats: list[dict] = []
    kept: list[dict] = []
    for p in players:
        name = p.get("name") or ""
        out = OUT_OF_SERIE_A.get(name)
        if out:
            caveats.append({
                "type": "removed",
                "name": name,
                "fromTeam": p.get("team"),
                **out,
            })
            continue
        ov = TEAM_OVERRIDES.get(name)
        if ov and ov.get("team") and ov["team"] != p.get("team"):
            caveats.append({
                "type": "team_override",
                "name": name,
                "fromTeam": p.get("team"),
                "toTeam": ov["team"],
                "asOf": ov.get("asOf"),
                "reason": ov.get("reason"),
            })
            p = {**p, "team": ov["team"], "id": f"{p.get('role')}-{ov['team']}-{name}".replace(" ", "_")}
        kept.append(p)
    return kept, caveats


def fetch_html(url: str = URL) -> str:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (compatible; FantacalcioAstaBot/1.0)",
            "Accept-Language": "it-IT,it;q=0.9",
        },
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read().decode("utf-8", errors="replace")


def _parse_num(raw: str | None) -> float | None:
    if raw is None:
        return None
    text = raw.strip().replace(",", ".")
    if not text or text in {"-", "—"}:
        return None
    if "/" in text:
        text = text.split("/", 1)[0].strip()
    try:
        return float(text)
    except ValueError:
        return None


def parse_players(html: str) -> list[dict]:
    rows = re.findall(r'<tr class="player-row"(.*?)</tr>', html, re.S)
    players: list[dict] = []
    for block in rows:

        def attr(name: str) -> str | None:
            m = re.search(rf'data-filter-{name}="([^"]*)"', block)
            return m.group(1) if m else None

        def col(key: str) -> str | None:
            m = re.search(rf'data-col-key="{key}">\s*([^<\s]+)', block)
            return m.group(1).strip() if m else None

        name_m = re.search(r"<span>([^<]+)</span>\s*</a>", block)
        team_m = re.search(r'data-col-key="sq">\s*([A-Z]{3})', block)
        href_m = re.search(r'href="(https://www\.fantacalcio\.it/serie-a/squadre/[^"]+)"', block)
        role = ROLE_MAP.get((attr("role-classic") or "").lower(), "?")
        name = unescape(name_m.group(1)).strip() if name_m else (attr("keywords") or "")
        team = team_m.group(1) if team_m else "???"
        playeds = _parse_num(attr("playeds"))
        mantra = parse_mantra(attr("role-mantra"))
        players.append(
            {
                "id": f"{role}-{team}-{name}".replace(" ", "_"),
                "name": name,
                "team": team,
                "role": role,
                "mantra": mantra,
                "qi": int(col("c_qi") or 0),
                "qa": int(col("c_qa") or 0),
                "fvm": int(col("c_fvm") or 0),
                "playedsExpected": int(playeds) if playeds is not None else None,
                "profileUrl": href_m.group(1) if href_m else None,
            }
        )
    return players


def parse_prev_stats(html: str) -> dict[str, dict]:
    """Stats stagione precedente, indexate per nome listone."""
    rows = re.findall(r'<tr class="player-row"(.*?)</tr>', html, re.S)
    out: dict[str, dict] = {}
    for block in rows:

        def attr(name: str) -> str | None:
            m = re.search(rf'data-filter-{name}="([^"]*)"', block)
            return m.group(1) if m else None

        def col(key: str) -> str | None:
            m = re.search(rf'data-col-key="{key}">\s*([^<\s]+)', block)
            return m.group(1).strip() if m else None

        name = unescape(attr("keywords") or "").strip()
        if not name:
            continue
        pg = _parse_num(col("pg"))
        mv = _parse_num(col("mv"))
        fm = _parse_num(col("mfv"))
        gol = _parse_num(col("gol"))
        ass = _parse_num(col("ass"))
        rig = _parse_num(col("rig"))  # scored portion of "x / y"
        rp = _parse_num(col("rp"))  # rigori parati (portieri)
        gs = _parse_num(col("gs"))
        out[name] = {
            "pgPrev": int(pg) if pg is not None else None,
            "mvPrev": mv,
            "fmPrev": fm,
            "goalsPrev": int(gol) if gol is not None else None,
            "assistsPrev": int(ass) if ass is not None else None,
            "pensPrev": int(rig) if rig is not None else None,
            "rpPrev": int(rp) if rp is not None else None,
            "gsPrev": int(gs) if gs is not None else None,
        }
    return out


def age_from_birthdate(text: str) -> int | None:
    m = re.search(
        r"(\d{1,2})\s+(gen|feb|mar|apr|mag|giu|lug|ago|set|ott|nov|dic)\s+(\d{4})",
        text.lower(),
    )
    if not m:
        return None
    day, mon, year = int(m.group(1)), MONTHS_IT[m.group(2)], int(m.group(3))
    season_start = date(REF_YEAR, 8, 1)
    born = date(year, mon, day)
    years = season_start.year - born.year
    if (season_start.month, season_start.day) < (born.month, born.day):
        years -= 1
    return years if 15 <= years <= 45 else None


def scrape_age(url: str) -> int | None:
    try:
        html = fetch_html(url)
    except Exception:
        return None
    m = re.search(r'class="birthdate">\s*([^<]+)</dd>', html, re.I)
    if not m:
        m = re.search(r"Nato il</dt>\s*<dd[^>]*>\s*([^<]+)</dd>", html, re.I)
    if not m:
        return None
    return age_from_birthdate(unescape(m.group(1)).strip())


def load_age_cache() -> dict[str, int]:
    path = DATA / "ages-cache.json"
    if not path.exists():
        return {}
    try:
        return {k: int(v) for k, v in json.loads(path.read_text(encoding="utf-8")).items()}
    except Exception:
        return {}


def save_age_cache(cache: dict[str, int]) -> None:
    DATA.mkdir(exist_ok=True)
    (DATA / "ages-cache.json").write_text(
        json.dumps(cache, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )


def resolve_ages(players: list[dict]) -> dict[str, int]:
    cache = load_age_cache()
    for name, age in AGES.items():
        cache.setdefault(name, age)

    missing = [
        p
        for p in players
        if p["name"] not in cache and p.get("profileUrl") and (p.get("fvm") or 0) >= 1
    ]
    missing.sort(key=lambda p: p.get("fvm") or 0, reverse=True)
    # Completa copertura età: tutti i listati con profilo (fino a 400).
    missing = missing[:400]

    if missing:
        print(f"Scraping età per {len(missing)} profili…")
        with ThreadPoolExecutor(max_workers=14) as pool:
            futs = {
                pool.submit(scrape_age, p["profileUrl"]): p["name"] for p in missing
            }
            for fut in as_completed(futs):
                name = futs[fut]
                age = fut.result()
                if age is not None:
                    cache[name] = age
        save_age_cache(cache)

    return cache


def starter_prob(playeds_expected: int | None, pg_prev: int | None) -> int | None:
    hist = (
        min(100, round(100 * pg_prev / PREV_MATCHES)) if pg_prev is not None else None
    )
    if playeds_expected is not None and hist is not None:
        return int(round(0.7 * playeds_expected + 0.3 * hist))
    if playeds_expected is not None:
        return int(playeds_expected)
    return hist


def curated_tier(role: str, name: str) -> str | None:
    for tier, names in TIERS.get(role, {}).items():
        if name in names:
            return tier
    return None


def auto_tier(role: str, fvm: int) -> str:
    thresholds = {
        "P": ((40, "top"), (18, "affidabile"), (6, "lowcost")),
        "D": ((40, "top_bonus"), (22, "modificatore"), (10, "value"), (4, "lowcost")),
        "C": ((80, "top"), (35, "bonus"), (12, "interessante"), (5, "lowcost")),
        "A": ((120, "top"), (60, "semi"), (20, "interessante"), (6, "lowcost")),
    }
    for min_fvm, tier in thresholds.get(role, ()):
        if fvm >= min_fvm:
            return tier
    return "pool"


def tier_for(role: str, name: str, fvm: int) -> str:
    return curated_tier(role, name) or auto_tier(role, fvm)


def flags_for(name: str, penalty: dict | None) -> list[str]:
    flags: list[str] = []
    if name == "Malen":
        flags += ["hype_post_gol", "lasciare_se_overpay"]
    if name == "Dimarco":
        flags += ["mod_e_bonus", "costa_come_centrocampista"]
    if name == "Svilar":
        flags += ["unica_certezza_big"]
    if name in ("Paz N.", "Calhanoglu", "McTominay"):
        flags += ["sposta_asta_centrocampo"]
    if name in ("Butez", "Sanchez Ro.", "Martinez Jo.", "Meret"):
        flags += ["verificare_gerarchia"]
    if penalty:
        flags.append(f"rigorista_{penalty['order']}")
    return flags


def cap_for(fvm_auction: int, qa: int) -> int:
    """Cap in crediti asta (già riscalati a 6×500)."""
    if fvm_auction >= 100:
        factor = 1.12
    elif fvm_auction >= 40:
        factor = 1.08
    elif fvm_auction >= 15:
        factor = 1.05
    else:
        factor = 1.0
    cap = int(round(fvm_auction * factor))
    if qa <= 1 and fvm_auction <= 3:
        cap = max(1, min(cap, 3))
    return min(cap, BUDGET_TOTAL)


def enrich(
    players: list[dict], prev_stats: dict[str, dict], ages: dict[str, int]
) -> list[dict]:
    out = []
    for p in players:
        penalty = PENALTIES.get(p["name"])
        tier = tier_for(p["role"], p["name"], p["fvm"])
        prev = prev_stats.get(p["name"], {})
        pg_prev = prev.get("pgPrev")
        fm_prev = prev.get("fmPrev")
        mv_prev = prev.get("mvPrev")
        goals = prev.get("goalsPrev")
        assists = prev.get("assistsPrev")
        pens = prev.get("pensPrev")
        rp = prev.get("rpPrev")
        gs = prev.get("gsPrev")
        age = ages.get(p["name"])
        start = starter_prob(p.get("playedsExpected"), pg_prev)
        fitness, fit_label = score_fitness(p["name"], age, start)
        mins = minutes_model(p["role"], pg_prev, p.get("playedsExpected"), start)
        minutes = mins["minutesEst"]
        prod = production_metrics(
            p["role"], pg_prev, fm_prev, mv_prev, goals, assists, pens, gs, minutes
        )
        fvm_listone = int(p["fvm"] or 0)
        fvm_auction = to_auction_credits(fvm_listone)
        band = fair_price(fvm_auction, p["role"], start, fitness, prod, p["name"])
        light = traffic_light(fvm_auction, band)
        injury = injury_profile(p["name"])
        ctx = team_context(p["team"])
        scenarios = scenario_plans(p["role"])
        flags = flags_for(p["name"], penalty)
        if fitness is not None and fitness < 55:
            flags.append("rischio_fisico")
        if age is not None and age >= 33:
            flags.append("over_30")
        if light == "overpay":
            flags.append("listone_overpay")
        elif light == "value":
            flags.append("listone_value")
        if injury and (injury.get("daysOut") or 0) >= 40:
            flags.append("infortunio_fine")
        adv = advanced_profile(p["role"], p.get("mantra") or [])
        if adv:
            flags.append("gioca_avanzato")
            flags.append(f"avanzato_{adv['advancedKind']}")
        note = build_scientific_note(
            name=p["name"],
            role=p["role"],
            team=p["team"],
            fvm=fvm_auction,
            fvm_listone=fvm_listone,
            tier=tier,
            age=age,
            starter=start,
            fitness=fitness,
            fitness_lbl=fit_label,
            fm=fm_prev,
            mv=mv_prev,
            pg=pg_prev,
            playeds_expected=p.get("playedsExpected"),
            goals=goals,
            assists=assists,
            pens=pens,
            gs=gs,
            penalty_label=penalty["label"] if penalty else "—",
            flags=flags,
        )
        base = {k: v for k, v in p.items() if k != "profileUrl"}
        out.append(
            {
                **base,
                "fvmListone": fvm_listone,
                "fvm": fvm_auction,
                "cap": cap_for(fvm_auction, p["qa"]),
                "fair": band["fair"],
                "fairLow": band["low"],
                "fairHigh": band["high"],
                "leave": band.get("leave"),
                "mockLow": band.get("mockLow"),
                "mockMid": band.get("mockMid"),
                "mockHigh": band.get("mockHigh"),
                "traffic": light,
                "tier": tier,
                "flags": flags,
                "penalty": penalty["order"] if penalty else None,
                "penaltyLabel": penalty["label"] if penalty else None,
                "note": note,
                "pgPrev": pg_prev,
                "mvPrev": mv_prev,
                "fmPrev": fm_prev,
                "goalsPrev": goals,
                "assistsPrev": assists,
                "pensPrev": pens,
                "rpPrev": rp,
                "gsPrev": gs,
                "minutesEst": minutes,
                "appsEst": mins.get("appsEst"),
                "mpg": mins.get("mpg"),
                "startRate": mins.get("startRate"),
                "benchRate": mins.get("benchRate"),
                "minutesNote": mins.get("minutesNote"),
                "per90Prod": prod.get("per90Prod"),
                "per90ProdNoPen": prod.get("per90ProdNoPen"),
                "per90Goals": prod.get("per90Goals"),
                "per90Assists": prod.get("per90Assists"),
                "votePure": prod.get("votePure"),
                "bonusPure": prod.get("bonusPure"),
                "csProxy": prod.get("csProxy"),
                "bonusProxy": prod.get("bonusProxy"),
                "starterProb": start,
                "age": age,
                "fitness": fitness,
                "fitnessLabel": fit_label,
                "injuryRisk": injury.get("label") if injury else None,
                "injuryDaysOut": injury.get("daysOut") if injury else None,
                "injuryMuscular": injury.get("muscular") if injury else None,
                "injuryMultiComp": injury.get("multiComp") if injury else None,
                "teamAtt": ctx.get("att"),
                "teamDef": ctx.get("def"),
                "teamStyle": ctx.get("style"),
                "teamCs": ctx.get("cs"),
                "teamSched": ctx.get("sched"),
                "teamModule": ctx.get("module"),
                "scenarios": scenarios,
                "mantra": p.get("mantra") or [],
                "playAdvanced": bool(adv),
                "advancedKind": adv.get("advancedKind") if adv else None,
                "advancedLabel": adv.get("advancedLabel") if adv else None,
                "advancedHint": adv.get("advancedHint") if adv else None,
            }
        )
    assign_gk_depth(out)
    return out


def main() -> None:
    DATA.mkdir(exist_ok=True)
    PUBLIC.mkdir(exist_ok=True)
    html = fetch_html(URL)
    players = parse_players(html)
    if len(players) < 400:
        raise SystemExit(f"Parse fallito: solo {len(players)} giocatori")
    players, roster_caveats = apply_roster_overrides(players)

    stats_html = fetch_html(STATS_URL)
    prev_stats = parse_prev_stats(stats_html)
    if len(prev_stats) < 200:
        raise SystemExit(f"Parse stats fallito: solo {len(prev_stats)} record")

    listone = {
        "source": URL,
        "season": "2026/27",
        "updated": str(date.today()),
        "count": len(players),
        "players": players,
    }
    (DATA / "listone-2026-27.json").write_text(
        json.dumps(listone, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    with (DATA / "listone-2026-27.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "id",
                "name",
                "team",
                "role",
                "qi",
                "qa",
                "fvm",
                "playedsExpected",
            ],
        )
        w.writeheader()
        for row in players:
            w.writerow({k: row.get(k) for k in w.fieldnames})

    ages = resolve_ages(players)
    enriched = enrich(players, prev_stats, ages)
    board = {
        "meta": {
            "season": "2026/27",
            "mode": "Classic",
            "teams": 6,
            "budget": BUDGET_TOTAL,
            "fvmScale": FVM_SCALE,
            "fvmScaleNote": (
                f"FVM listone Fantacalcio riscalato ×{FVM_SCALE} per asta "
                f"6 squadre × {BUDGET_TOTAL} crediti (fair/cap/leave in crediti asta)."
            ),
            "roster": {"P": 3, "D": 8, "C": 8, "A": 6},
            "modifier": "difesa",
            "auction": "ruoli",
            "auctionOrder": ["P", "D", "C", "A"],
            "auctionNote": (
                "Asta a ruoli: si chiama un ruolo alla volta fino a quando "
                "tutte le 6 rose hanno completato gli slot di quel ruolo."
            ),
            "defaultTeams": DEFAULT_TEAMS,
            "source_listone": URL,
            "source_stats": STATS_URL,
            "prevSeason": PREV_SEASON,
            "updated": str(date.today()),
            "dataFreshness": (
                "Il board riparte dal listone ufficiale Fantacalcio.it (Classic). "
                "Può restare indietro sul calciomercato: applichiamo override curati "
                "(OUT_OF_SERIE_A / TEAM_OVERRIDES) per uscite ufficiali non ancora riflesse."
            ),
            "rosterCaveats": roster_caveats,
            "budgets": BUDGETS,
            "tiers": TIERS,
            "penaltiesSource": "Sintesi guide rigoristi Serie A 2026/27 (FCO/SOS/Goal)",
            "starterProbNote": (
                "Tit% = 70% stima titolarità listone Fantacalcio + 30% "
                f"presenze/{PREV_MATCHES} in {PREV_SEASON} (se disponibili)."
            ),
            "fitnessNote": (
                "Forma = disponibilità − fragilità curata − età. "
                "Età da profili Fantacalcio (cache) + hint guida."
            ),
            "scienceNote": (
                "Nota scientifica: fair/mock/leave, traffic light, minuti proxy "
                "(PG×mpg), prod/90 e no-rig, voto vs bonus, CS proxy, calendario "
                "apertura curato, infortuni fini, fit rosa, scenari A/B/C."
            ),
            "minutesNote": (
                "Minuti stimati da PG/playeds × mpg (no feed minuti ufficiali "
                "sul listone Fantacalcio)."
            ),
            "scenarioPlans": SCENARIO_PLANS,
            "notesSource": "Motore scientifico repo + guide SOS/Goal/FCO",
            "priorityNote": (
                "Pri dinamica: Tit% + Forma + FM + prod/90 + fascia + rigorista "
                "+ fit rosa (slot/schema) + traffic/leave + spese rivali."
            ),
        },
        "players": enriched,
    }
    payload = json.dumps(board, ensure_ascii=False)
    (DATA / "asta-board-2026-27.json").write_text(
        json.dumps(board, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (PUBLIC / "asta-board-2026-27.json").write_text(payload, encoding="utf-8")
    shown = sum(1 for p in enriched if p["tier"] != "pool")
    pens = sum(1 for p in enriched if p["penalty"])
    with_fm = sum(1 for p in enriched if p["fmPrev"] is not None)
    with_tit = sum(1 for p in enriched if p["starterProb"] is not None)
    with_age = sum(1 for p in enriched if p.get("age") is not None)
    with_gol = sum(1 for p in enriched if p.get("goalsPrev") is not None)
    with_rp = sum(1 for p in enriched if (p.get("rpPrev") or 0) > 0)
    fragile = sum(1 for p in enriched if (p.get("fitness") or 100) < 55)
    with_min = sum(1 for p in enriched if p.get("minutesEst") is not None)
    with_p90 = sum(1 for p in enriched if p.get("per90Prod") is not None)
    with_mock = sum(1 for p in enriched if p.get("mockMid") is not None)
    missing = [n for n in PENALTIES if n not in {p["name"] for p in players}]
    sample = next((p for p in enriched if p["name"] == "Malen"), enriched[0])
    print(
        f"OK {len(enriched)} giocatori | fasce {shown} | rigoristi {pens} | "
        f"FM {PREV_SEASON} {with_fm} | gol {with_gol} | RP>0 {with_rp} | Tit% {with_tit} | "
        f"età {with_age} | min {with_min} | /90 {with_p90} | mock {with_mock} | "
        f"fragili {fragile} | missing pens {missing}"
    )
    if roster_caveats:
        for c in roster_caveats:
            if c["type"] == "removed":
                print(f"Override REMOVE {c['name']} ({c.get('fromTeam')}→{c.get('to')}): {c.get('reason')}")
            else:
                print(f"Override TEAM {c['name']} {c.get('fromTeam')}→{c.get('toTeam')}: {c.get('reason')}")
    print(f"Sample note ({sample['name']}): {sample['note'][:220]}…")


if __name__ == "__main__":
    main()
