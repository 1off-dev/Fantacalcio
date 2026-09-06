#!/usr/bin/env python3
"""Scarica il listone Classic 2026/27 da Fantacalcio.it e rigenera la board asta."""

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
        "value": ["Ostigard", "Spence"],
    },
    "C": {
        "super_top": ["Paz N.", "Calhanoglu", "McTominay"],
        "top": ["Orsolini", "Pulisic", "Rabiot", "De Bruyne", "Baturina", "Mora"],
        "bonus": ["Da Cunha", "Zaccagni", "Barella", "Zaniolo", "Atta", "Frattesi"],
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
        ],
    },
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


def fetch_html() -> str:
    req = urllib.request.Request(
        URL,
        headers={
            "User-Agent": "Mozilla/5.0 (compatible; FantacalcioAstaBot/1.0)",
            "Accept-Language": "it-IT,it;q=0.9",
        },
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read().decode("utf-8", errors="replace")


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
        players.append(
            {
                "id": f"{role}-{team}-{name}".replace(" ", "_"),
                "name": name,
                "team": team,
                "role": role,
                "qi": int(col("c_qi") or 0),
                "qa": int(col("c_qa") or 0),
                "fvm": int(col("c_fvm") or 0),
            }
        )
    return players


def tier_for(role: str, name: str) -> str:
    for tier, names in TIERS.get(role, {}).items():
        if name in names:
            return tier
    return "pool"


def flags_for(name: str) -> list[str]:
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


def enrich(players: list[dict]) -> list[dict]:
    out = []
    for p in players:
        out.append(
            {
                **p,
                "cap": cap_for(p["fvm"], p["qa"]),
                "tier": tier_for(p["role"], p["name"]),
                "flags": flags_for(p["name"]),
            }
        )
    return out


def main() -> None:
    DATA.mkdir(exist_ok=True)
    PUBLIC.mkdir(exist_ok=True)
    html = fetch_html()
    players = parse_players(html)
    if len(players) < 400:
        raise SystemExit(f"Parse fallito: solo {len(players)} giocatori")

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
            f, fieldnames=["id", "name", "team", "role", "qi", "qa", "fvm"]
        )
        w.writeheader()
        w.writerows(players)

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
            "updated": str(date.today()),
            "budgets": BUDGETS,
            "tiers": TIERS,
        },
        "players": enrich(players),
    }
    (DATA / "asta-board-2026-27.json").write_text(
        json.dumps(board, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (PUBLIC / "asta-board-2026-27.json").write_text(
        json.dumps(board, ensure_ascii=False), encoding="utf-8"
    )
    tiered = sum(1 for p in board["players"] if p["tier"] != "pool")
    print(f"OK {len(players)} giocatori, {tiered} in fascia → data/ + public/")


if __name__ == "__main__":
    main()
