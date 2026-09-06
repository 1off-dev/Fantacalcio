#!/usr/bin/env python3
"""Scarica listone Classic e genera board asta con note + rigoristi."""

from __future__ import annotations

import csv
import json
import re
import urllib.request
from datetime import date
from html import unescape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
PUBLIC = ROOT / "public"
URL = "https://www.fantacalcio.it/quotazioni-fantacalcio/2026-27"
STATS_URL = "https://www.fantacalcio.it/statistiche-serie-a/2025-26"
PREV_SEASON = "2025/26"
PREV_MATCHES = 38  # giornate Serie A
ROLE_MAP = {"p": "P", "d": "D", "c": "C", "a": "A"}

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

# Gerarchie rigoristi 2026/27 (sintesi guide FCO/SOS/Goal). Chiavi = nomi listone.
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
        "P": 100,
        "D": 250,
        "C": 270,
        "A": 380,
        "label": "Modificatore first",
    },
    "equilibrata_mod": {
        "P": 90,
        "D": 210,
        "C": 300,
        "A": 400,
        "label": "Equilibrata + mod",
    },
    "anti_malen": {
        "P": 85,
        "D": 200,
        "C": 315,
        "A": 400,
        "label": "Anti-Malen (2+2 attacco)",
    },
}


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
        role = ROLE_MAP.get((attr("role-classic") or "").lower(), "?")
        name = unescape(name_m.group(1)).strip() if name_m else (attr("keywords") or "")
        team = team_m.group(1) if team_m else "???"
        playeds = _parse_num(attr("playeds"))
        players.append(
            {
                "id": f"{role}-{team}-{name}".replace(" ", "_"),
                "name": name,
                "team": team,
                "role": role,
                "qi": int(col("c_qi") or 0),
                "qa": int(col("c_qa") or 0),
                "fvm": int(col("c_fvm") or 0),
                # Stima titolarità attesa Fantacalcio (0–100, spesso a scaglioni).
                "playedsExpected": int(playeds) if playeds is not None else None,
            }
        )
    return players


def parse_prev_stats(html: str) -> dict[str, dict]:
    """FM / presenze stagione precedente, indexate per nome listone."""
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
        out[name] = {
            "pgPrev": int(pg) if pg is not None else None,
            "mvPrev": mv,
            "fmPrev": fm,
        }
    return out


def starter_prob(playeds_expected: int | None, pg_prev: int | None) -> int | None:
    """Probabilità titolare 0–100: proiezione listone + storico presenze."""
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


def cap_for(fvm: int, qa: int) -> int:
    if fvm >= 200:
        factor = 1.12
    elif fvm >= 80:
        factor = 1.08
    elif fvm >= 30:
        factor = 1.05
    else:
        factor = 1.0
    cap = int(round(fvm * factor))
    if qa <= 1 and fvm <= 5:
        cap = max(1, min(cap, 5))
    return cap


def note_for(p: dict, tier: str, penalty: dict | None) -> str:
    role, fvm, name = p["role"], p["fvm"], p["name"]
    bits: list[str] = []
    if penalty:
        bits.append(f"{penalty['label']} ({penalty['detail']}).")

    if name == "Malen":
        bits.append("Hype post-gol: non far saltare il budget attacco.")
    elif name == "Dimarco":
        bits.append("Bonus da esterno: ok solo se restano crediti per i voti.")
    elif name == "Svilar":
        bits.append("Certezza porta con modificatore.")
    elif name in ("Paz N.", "Calhanoglu", "McTominay"):
        bits.append("Top C: prendine uno, non inseguirli tutti.")
    elif role == "P":
        bits.append(
            "Porta da modificatore."
            if tier in ("super_top", "top", "affidabile")
            else "Prendi solo titolari certi a 1–8."
        )
    elif role == "D":
        bits.append(
            "Priorità voto/bonus per il modificatore."
            if tier in ("super_top", "top_bonus", "modificatore", "value")
            else "Chiudi con titolari low-cost, evita ballottaggi cari."
        )
    elif role == "C":
        bits.append(
            "Investimento a centrocampo: fissa un max."
            if tier in ("super_top", "top", "bonus")
            else "Titolare da minutaggio per allungare la rosa."
        )
    else:
        bits.append(
            "Punta chiave: valuta piano anti-Malen 2+2."
            if tier in ("super_top", "top", "semi")
            else "Slot profondità: solo con minuti o upside chiaro."
        )

    note = " ".join(bits)
    if fvm and "FVM" not in note:
        note += f" FVM {fvm}, cap consigliato {cap_for(fvm, p['qa'])}."
    return note[:190]


def enrich(players: list[dict], prev_stats: dict[str, dict]) -> list[dict]:
    out = []
    for p in players:
        penalty = PENALTIES.get(p["name"])
        tier = tier_for(p["role"], p["name"], p["fvm"])
        prev = prev_stats.get(p["name"], {})
        pg_prev = prev.get("pgPrev")
        fm_prev = prev.get("fmPrev")
        mv_prev = prev.get("mvPrev")
        out.append(
            {
                **p,
                "cap": cap_for(p["fvm"], p["qa"]),
                "tier": tier,
                "flags": flags_for(p["name"], penalty),
                "penalty": penalty["order"] if penalty else None,
                "penaltyLabel": penalty["label"] if penalty else None,
                "note": note_for(p, tier, penalty),
                "pgPrev": pg_prev,
                "mvPrev": mv_prev,
                "fmPrev": fm_prev,
                "starterProb": starter_prob(p.get("playedsExpected"), pg_prev),
            }
        )
    return out


def main() -> None:
    DATA.mkdir(exist_ok=True)
    PUBLIC.mkdir(exist_ok=True)
    html = fetch_html(URL)
    players = parse_players(html)
    if len(players) < 400:
        raise SystemExit(f"Parse fallito: solo {len(players)} giocatori")

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
        w.writerows(players)

    enriched = enrich(players, prev_stats)
    board = {
        "meta": {
            "season": "2026/27",
            "mode": "Classic",
            "teams": 6,
            "budget": 1000,
            "roster": {"P": 3, "D": 8, "C": 8, "A": 6},
            "modifier": "difesa",
            "auction": "aperta",
            "source_listone": URL,
            "source_stats": STATS_URL,
            "prevSeason": PREV_SEASON,
            "updated": str(date.today()),
            "budgets": BUDGETS,
            "tiers": TIERS,
            "penaltiesSource": "Sintesi guide rigoristi Serie A 2026/27 (FCO/SOS/Goal)",
            "starterProbNote": (
                "Tit% = 70% stima titolarità listone Fantacalcio + 30% "
                f"presenze/{PREV_MATCHES} in {PREV_SEASON} (se disponibili)."
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
    missing = [n for n in PENALTIES if n not in {p["name"] for p in players}]
    print(
        f"OK {len(players)} giocatori | fasce {shown} | rigoristi {pens} | "
        f"FM {PREV_SEASON} {with_fm} | Tit% {with_tit} | missing pens {missing}"
    )


if __name__ == "__main__":
    main()
