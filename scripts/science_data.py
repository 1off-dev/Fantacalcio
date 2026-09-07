"""Heuristic scientific signals for Fantacalcio Classic auction board.

Completes the 8-point reliability roadmap with best-available proxies when
true minutes/injury feeds are not on Fantacalcio listone pages.
"""

from __future__ import annotations

# Historical / curated fragility (0–5). Higher = more injury risk.
FRAGILE: dict[str, int] = {
    "Scalvini": 5, "Scamacca": 4, "Dybala": 4, "Chiesa": 4, "Zaniolo": 4,
    "Bremer": 3, "De Bruyne": 3, "Vlahovic": 3, "Leao": 2, "Lookman": 2,
    "Hojlund": 2, "Frattesi": 2, "Samardzic": 2, "Esposito F.P.": 2,
    "Conceicao": 2, "Bisseck": 2, "Ostigard": 2, "Thuram": 1, "Martinez L.": 1,
    "Calhanoglu": 1, "McTominay": 1, "Pulisic": 1, "Orsolini": 1, "Barella": 1,
    "Dimarco": 1, "Bastoni": 1, "Svilar": 0, "Vicario": 0, "Carnesecchi": 1,
    "Maignan": 1, "Malen": 1, "Kean": 1, "Douvikas": 1, "Paz N.": 1, "Yildiz": 1,
    "Wesley": 1, "Molina N.": 1, "Zaccagni": 1, "Da Cunha": 1, "Baturina": 1,
    "Mora": 1, "Ramos G.": 2, "Kolo Muani": 2, "Berardi": 2, "Davis K.": 1,
    "Lauriente": 1, "Castro S.": 1, "Colombo": 1, "Raspadori": 1, "Simeone": 1,
    "Atta": 1, "Vlasic": 1, "McKennie": 1, "Kessie": 1, "Akanji": 1,
    "Rrahmani": 1, "Kalulu": 1, "N'Dicka": 1, "Di Lorenzo": 1, "Pavlovic": 1,
    "Solet": 1, "Gila": 1, "Spence": 1, "Chalobah T.": 1, "Koopmeiners": 1,
    "Retegui": 1, "Soulè": 2, "Kessiè": 1,
}

# Fine injury profile: daysOut last 2 seasons (est.), muscular recurrence, multi-comp load 0–2.
INJURY_FINE: dict[str, dict] = {
    "Scalvini": {"daysOut": 180, "muscular": True, "multiComp": 1, "note": "ACL/storico grave"},
    "Scamacca": {"daysOut": 90, "muscular": True, "multiComp": 1, "note": "ricorrente muscolare"},
    "Dybala": {"daysOut": 70, "muscular": True, "multiComp": 1, "note": "flessori/disponibilità"},
    "Chiesa": {"daysOut": 100, "muscular": True, "multiComp": 2, "note": "storico grave + carico"},
    "Zaniolo": {"daysOut": 80, "muscular": True, "multiComp": 1, "note": "infortuni + gestione"},
    "Bremer": {"daysOut": 55, "muscular": True, "multiComp": 1, "note": "muscolare ripetuto"},
    "De Bruyne": {"daysOut": 60, "muscular": True, "multiComp": 1, "note": "età + carico"},
    "Vlahovic": {"daysOut": 45, "muscular": True, "multiComp": 1, "note": "muscolari"},
    "Leao": {"daysOut": 25, "muscular": False, "multiComp": 2, "note": "carico europeo"},
    "Lookman": {"daysOut": 30, "muscular": True, "multiComp": 1, "note": "disponibilità a tratti"},
    "Hojlund": {"daysOut": 35, "muscular": True, "multiComp": 1, "note": "giovane + carico"},
    "Ramos G.": {"daysOut": 40, "muscular": True, "multiComp": 2, "note": "rotazioni+muscolari"},
    "Kolo Muani": {"daysOut": 35, "muscular": False, "multiComp": 1, "note": "gestione minuti"},
    "Thuram": {"daysOut": 20, "muscular": False, "multiComp": 2, "note": "carico Inter/UE"},
    "Calhanoglu": {"daysOut": 15, "muscular": False, "multiComp": 2, "note": "carico UE"},
    "Dimarco": {"daysOut": 18, "muscular": False, "multiComp": 2, "note": "carico UE"},
    "Pulisic": {"daysOut": 22, "muscular": False, "multiComp": 2, "note": "carico UE"},
    "Malen": {"daysOut": 12, "muscular": False, "multiComp": 1, "note": "affidabile recente"},
    "Svilar": {"daysOut": 5, "muscular": False, "multiComp": 1, "note": "alta disponibilità"},
    "Vicario": {"daysOut": 8, "muscular": False, "multiComp": 0, "note": "continua"},
    "Soulè": {"daysOut": 25, "muscular": False, "multiComp": 1, "note": "monitorare"},
}

AGES: dict[str, int] = {
    "Malen": 27, "Martinez L.": 28, "Dimarco": 29, "Paz N.": 21, "Calhanoglu": 32,
    "McTominay": 29, "Svilar": 26, "Thuram": 28, "Hojlund": 23, "Kean": 26,
    "Leao": 27, "Dybala": 32, "Scamacca": 27, "De Bruyne": 35, "Barella": 29,
    "Orsolini": 29, "Pulisic": 28, "Bremer": 29, "Bastoni": 27, "Wesley": 22,
    "Molina N.": 28, "Yildiz": 21, "Douvikas": 27, "Ramos G.": 25, "Kolo Muani": 27,
    "Zaccagni": 31, "Frattesi": 27, "Samardzic": 24, "Baturina": 23, "Mora": 22,
    "Da Cunha": 24, "Vicario": 29, "Carnesecchi": 23, "Maignan": 31, "Butez": 30,
    "Pavlovic": 24, "Solet": 25, "Akanji": 31, "Rrahmani": 32, "Kalulu": 26,
    "N'Dicka": 26, "Di Lorenzo": 32, "Berardi": 32, "Davis K.": 28,
    "Esposito F.P.": 21, "Lauriente": 29, "Simeone": 31, "Raspadori": 26,
    "Castro S.": 22, "Colombo": 24, "Zaniolo": 27, "Atta": 23, "Vlasic": 28,
    "McKennie": 27, "Conceicao": 23, "Kessie": 29, "Scalvini": 22, "Ostigard": 26,
    "Spence": 25, "Bisseck": 25, "Chalobah T.": 27, "Gila": 26, "Lookman": 28,
    "Chiesa": 29, "Vlahovic": 26, "Koopmeiners": 28, "Retegui": 26,
    "Soulè": 22, "Kessiè": 29, "Konè M.": 23, "Tourè E.": 23, "Dodò": 27,
    "Calò": 28, "Konè I.": 22, "Lucumì": 27, "Bernabè": 22, "Tourè I.": 21,
    "Zè Pedro": 28, "Cissè A.": 22, "Traorè Hj.": 23, "Candè": 23,
}

# Club context + opening schedule ease (1=duro, 5=morbido) + module hint.
TEAM_CONTEXT: dict[str, dict] = {
    "INT": {"att": 5, "def": 5, "style": "top-attacco+mod", "cs": "alto", "sched": 2, "module": "3-5-2", "note": "UE carico; CS alto"},
    "NAP": {"att": 5, "def": 4, "style": "attacco alto", "cs": "medio-alto", "sched": 3, "module": "4-3-3", "note": "volume offensivo"},
    "MIL": {"att": 4, "def": 4, "style": "bilanciato big", "cs": "medio-alto", "sched": 3, "module": "4-2-3-1", "note": "rotazioni UE"},
    "JUV": {"att": 4, "def": 5, "style": "controllo+mod", "cs": "alto", "sched": 3, "module": "3-4-2-1", "note": "mod forte"},
    "ATA": {"att": 4, "def": 3, "style": "volume offensivo", "cs": "medio", "sched": 3, "module": "3-4-2-1", "note": "bonus C/A"},
    "ROM": {"att": 4, "def": 4, "style": "transizioni+mod", "cs": "medio-alto", "sched": 3, "module": "3-4-2-1", "note": "Malen focus"},
    "FIO": {"att": 3, "def": 3, "style": "possesso medio", "cs": "medio", "sched": 3, "module": "4-2-3-1", "note": "creazione"},
    "BOL": {"att": 3, "def": 4, "style": "solidità", "cs": "medio-alto", "sched": 4, "module": "4-2-3-1", "note": "CS value"},
    "LAZ": {"att": 3, "def": 3, "style": "fasce+rigori", "cs": "medio", "sched": 3, "module": "4-3-3", "note": "fasce bonus"},
    "TOR": {"att": 2, "def": 3, "style": "blocco basso", "cs": "medio", "sched": 4, "module": "3-5-2", "note": "low ceiling"},
    "GEN": {"att": 2, "def": 3, "style": "difensivo", "cs": "medio", "sched": 4, "module": "3-5-2", "note": "mod lowcost"},
    "UDI": {"att": 3, "def": 2, "style": "transizioni", "cs": "basso", "sched": 4, "module": "3-5-2", "note": "open games"},
    "COM": {"att": 3, "def": 3, "style": "possesso/creazione", "cs": "medio", "sched": 3, "module": "4-2-3-1", "note": "Paz/Kean upside"},
    "SAS": {"att": 3, "def": 2, "style": "open games", "cs": "basso", "sched": 4, "module": "4-3-3", "note": "rigori+bonus"},
    "CRE": {"att": 2, "def": 2, "style": "neopromossa", "cs": "basso", "sched": 3, "module": "3-5-2", "note": "volatilità"},
    "PAR": {"att": 2, "def": 2, "style": "neopromossa", "cs": "basso", "sched": 3, "module": "4-2-3-1", "note": "depth only"},
    "PIS": {"att": 2, "def": 2, "style": "neopromossa", "cs": "basso", "sched": 3, "module": "3-5-2", "note": "low floor"},
    "VER": {"att": 2, "def": 2, "style": "sopravvivenza", "cs": "basso", "sched": 4, "module": "3-4-2-1", "note": "avoid overpay"},
    "CAG": {"att": 2, "def": 2, "style": "sopravvivenza", "cs": "basso", "sched": 4, "module": "4-3-3", "note": "late targets"},
    "LEC": {"att": 2, "def": 2, "style": "sopravvivenza", "cs": "basso", "sched": 4, "module": "4-3-3", "note": "late targets"},
    "MON": {"att": 2, "def": 2, "style": "sopravvivenza", "cs": "basso", "sched": 4, "module": "3-4-2-1", "note": "low ceiling"},
    "VEN": {"att": 2, "def": 2, "style": "sopravvivenza", "cs": "basso", "sched": 4, "module": "3-4-2-1", "note": "volatilità"},
    "FRO": {"att": 2, "def": 2, "style": "neopromossa", "cs": "basso", "sched": 3, "module": "3-5-2", "note": "depth"},
}

# Mock/auction paid ranges at 6 teams × 1000 (guide/mock synthesis).
MOCK_RANGES: dict[str, dict] = {
    "Malen": {"low": 380, "mid": 430, "high": 480, "leave": 460},
    "Martinez L.": {"low": 280, "mid": 330, "high": 380, "leave": 370},
    "Thuram": {"low": 160, "mid": 200, "high": 240, "leave": 235},
    "Hojlund": {"low": 140, "mid": 180, "high": 230, "leave": 220},
    "Kean": {"low": 90, "mid": 120, "high": 150, "leave": 145},
    "Dimarco": {"low": 160, "mid": 200, "high": 240, "leave": 225},
    "Paz N.": {"low": 180, "mid": 230, "high": 290, "leave": 280},
    "Calhanoglu": {"low": 140, "mid": 180, "high": 220, "leave": 215},
    "McTominay": {"low": 130, "mid": 170, "high": 210, "leave": 205},
    "Svilar": {"low": 70, "mid": 95, "high": 120, "leave": 115},
    "Vicario": {"low": 45, "mid": 60, "high": 80, "leave": 78},
    "Orsolini": {"low": 70, "mid": 95, "high": 120, "leave": 118},
    "Pulisic": {"low": 80, "mid": 105, "high": 135, "leave": 130},
    "Wesley": {"low": 70, "mid": 95, "high": 125, "leave": 120},
    "Bremer": {"low": 55, "mid": 75, "high": 100, "leave": 95},
    "Bastoni": {"low": 40, "mid": 55, "high": 75, "leave": 72},
    "Scamacca": {"low": 70, "mid": 95, "high": 130, "leave": 110},
    "Dybala": {"low": 40, "mid": 60, "high": 90, "leave": 75},
    "Leao": {"low": 80, "mid": 110, "high": 150, "leave": 130},
    "Yildiz": {"low": 60, "mid": 85, "high": 120, "leave": 115},
    "Douvikas": {"low": 55, "mid": 75, "high": 100, "leave": 95},
    "Carnesecchi": {"low": 35, "mid": 48, "high": 65, "leave": 62},
    "Maignan": {"low": 30, "mid": 45, "high": 65, "leave": 60},
    "Barella": {"low": 50, "mid": 70, "high": 95, "leave": 90},
    "Zaccagni": {"low": 45, "mid": 65, "high": 90, "leave": 85},
    "Da Cunha": {"low": 40, "mid": 55, "high": 75, "leave": 72},
}

# Scenario planner templates per role (A/B/C).
SCENARIO_PLANS: dict[str, dict] = {
    "P": {
        "A": "1 cemento big (Svilar) + 2 titolari low-cost",
        "B": "2 medi (Vicario/Carnesecchi/Maignan) + 1 backup 1–5",
        "C": "3 titolari provincia se i top > leave",
        "pivot": "Se Svilar > leave → Vicario+Mandas/Butez",
    },
    "D": {
        "A": "1 bonus fascia (Dimarco/Wesley) + 4–5 cemento mod",
        "B": "0 elite fascia + 2 value esterni + 5–6 voti mod",
        "C": "solo cementi low-mid se Dimarco > leave",
        "pivot": "Se Dimarco > ~220 → Molina/Wesley value + centrali",
    },
    "C": {
        "A": "1 tra Paz/Calha/McT + 1 rigorista mid + volume",
        "B": "0 super-top + 2 bonus (Orso/Pulisic/Zacca) + lowcost",
        "C": "solo volume+rigoristi secondari se top gonfiano",
        "pivot": "Se Paz esce caro → Calha/McT; se entrambi cari → Orso+Da Cunha",
    },
    "A": {
        "A": "Malen + 1 semi + depth",
        "B": "Anti-Malen 2+2 (Lautaro/Thuram/Kean/Douvikas)",
        "C": "3 mid + upside se i top scappano",
        "pivot": "Se Malen > leave → piano B 2+2; evita Vetro a prezzo pieno",
    },
}

EXPERT_NOTES: dict[str, str] = {
    "Malen": "Guide: top absolute post-exploit; SOS/Goal avvisano overpay oltre 420–450 a 6.",
    "Martinez L.": "FCO: affidabilità gol+assist; piano B naturale se Malen scappa.",
    "Dimarco": "Consensus: unico D da produzione C/A; a 6 spesso no-buy se costa >220.",
    "Paz N.": "Hype young C; minutaggio Como da monitorare ma upside bonus altissimo.",
    "Calhanoglu": "Rigorista+tiro; età 32: preferire se forma ok, altrimenti McTominay.",
    "McTominay": "Box-to-box bonus; meno rigorista di Calha ma più cementato sui minuti.",
    "Svilar": "Unica certezza P big col mod; non lasciarlo sotto 80–90 in lega a 6.",
    "Thuram": "Gol+assist senza rigori Inter; value se Malen/Lautaro gonfiano.",
    "Hojlund": "Napoli: upside ma concorrenza; non pagare da top1 senza certezze titolari.",
    "Kean": "Titolare Como + bonus; semi-top concreto nelle guide mid-tier.",
    "Leao": "Alti e bassi: solo a sconto, mai da top budget.",
    "Dybala": "Magia a giorni alterni + infortuni: tetto basso, mai inseguire.",
    "Scamacca": "Rigorista Atalanta ma vetro: fitness chiave, sconto obbligatorio.",
    "De Bruyne": "Qualità top, età e carico: pochi gettoni a prezzo pieno.",
    "Barella": "Motore Inter; meno gol di McT/Calha ma voti solidi.",
    "Orsolini": "Specialista rigori Bologna: target C bonus nelle guide.",
    "Pulisic": "Milano: bonus offensivi, gerarchia rigori aperta.",
    "Bremer": "Mod+bonus se sano; storico muscolare → non overpay.",
    "Bastoni": "Pilastro mod Inter; meno bonus di Dimarco, più continuità.",
    "Wesley": "Esterno bonus emergente: molti mock lo mettono subito dopo Dimarco.",
    "Molina N.": "Terzino bonus; cotazione guida alta ma sotto Dimarco.",
    "Yildiz": "Upside Juve + possibili rigori; volatilità da giovane.",
    "Douvikas": "Punta Como da minutaggio; value anti-Malen.",
    "Ramos G.": "Milan: contendente offensivo/rigori; attenzione rotazioni.",
    "Kolo Muani": "Juve: rigorista designato ma non cemento titolare.",
    "Zaccagni": "Lazio: 1° rigore fluido + bonus; target C mid.",
    "Lookman": "Bonus machine se sano e titolare.",
    "Chiesa": "Talent + vetro: solo a forte sconto.",
    "Vlahovic": "Alti/bassi + muscolari: tetto rigoroso.",
}


def fitness_label(score: int | None) -> str:
    if score is None:
        return "n/d"
    if score >= 80:
        return "ottima"
    if score >= 65:
        return "buona"
    if score >= 50:
        return "discreta"
    if score >= 35:
        return "fragilità"
    return "alto rischio"


def score_fitness(name: str, age: int | None, starter_prob: int | None) -> tuple[int | None, str]:
    if starter_prob is None and age is None and name not in FRAGILE and name not in INJURY_FINE:
        return None, "n/d"
    base = 72
    if starter_prob is not None:
        base = int(0.45 * starter_prob + 0.55 * 70)
    base -= FRAGILE.get(name, 1) * 8
    fine = INJURY_FINE.get(name)
    if fine:
        base -= min(25, (fine.get("daysOut") or 0) // 8)
        if fine.get("muscular"):
            base -= 6
        base -= int(fine.get("multiComp") or 0) * 3
    if age is not None:
        if age >= 34:
            base -= 18
        elif age >= 32:
            base -= 10
        elif age >= 30:
            base -= 5
        elif age <= 22:
            base -= 2
    score = max(5, min(98, base))
    return score, fitness_label(score)


def minutes_model(
    role: str,
    pg: int | None,
    playeds_expected: int | None,
    starter: int | None,
) -> dict:
    """Proxy minutes / start / bench when true minutes feed is unavailable.

    Fantacalcio `playedsExpected` is a 0–100 titolarità score, not apps.
    Previous-season `pg` is appearances (0–38).
    """
    pe = playeds_expected if playeds_expected is not None else None
    p = pg if pg is not None else None
    if pe is None and p is None and starter is None:
        return {
            "minutesEst": None,
            "appsEst": None,
            "mpg": None,
            "startRate": None,
            "benchRate": None,
            "minutesNote": "n/d",
        }

    start_rate = starter
    if start_rate is None and pe is not None:
        start_rate = int(min(100, max(0, pe)))
    if start_rate is None and p is not None:
        start_rate = int(round(100 * min(38, p) / 38))

    # Apps: prefer last-season PG; else infer from start rate.
    if p is not None:
        apps = float(min(38, max(0, p)))
    elif start_rate is not None:
        apps = round(38 * start_rate / 100, 1)
    else:
        apps = 0.0

    if start_rate is None:
        mpg = 72
    elif start_rate >= 85:
        mpg = 87 if role in ("P", "D") else 84
    elif start_rate >= 70:
        mpg = 80
    elif start_rate >= 50:
        mpg = 68
    else:
        mpg = 45
    minutes = int(round(apps * mpg)) if apps else None
    if minutes is not None:
        minutes = min(3420, minutes)  # hard cap 38×90
    bench = None
    if start_rate is not None:
        bench = max(0, min(70, int(round((100 - start_rate) * 0.65))))
    note = "proxy PG×mpg + Tit% (no feed minuti ufficiali)"
    return {
        "minutesEst": minutes,
        "appsEst": int(round(apps)) if apps else None,
        "mpg": mpg,
        "startRate": start_rate,
        "benchRate": bench,
        "minutesNote": note,
    }


def est_minutes(pg: int | None, playeds_expected: int | None) -> int | None:
    return minutes_model("?", pg, playeds_expected, None)["minutesEst"]


def production_metrics(
    role: str,
    pg: int | None,
    fm: float | None,
    mv: float | None,
    goals: int | None,
    assists: int | None,
    pens: int | None,
    gs: int | None,
    minutes: int | None,
) -> dict:
    out: dict = {
        "goals": goals,
        "assists": assists,
        "pens": pens,
        "gs": gs,
        "minutes": minutes,
        "per90Goals": None,
        "per90Assists": None,
        "per90Prod": None,
        "per90ProdNoPen": None,
        "bonusProxy": None,
        "votePure": mv,
        "bonusPure": None,
        "gsPerApp": None,
        "csProxy": None,
    }
    if mv is not None and fm is not None:
        out["bonusPure"] = round(fm - mv, 2)
    if gs is not None and pg:
        out["gsPerApp"] = round(gs / max(pg, 1), 2)
        # Higher CS proxy when few goals conceded per app (P/D).
        if role in ("P", "D"):
            out["csProxy"] = round(max(0.0, 1.4 - (gs / max(pg, 1))), 2)

    if minutes and minutes >= 200:
        g90 = round(((goals or 0) * 90) / minutes, 3)
        a90 = round(((assists or 0) * 90) / minutes, 3)
        pens90 = round(((pens or 0) * 90) / minutes, 3)
        out["per90Goals"] = g90
        out["per90Assists"] = a90
        out["per90Prod"] = round(g90 + a90, 3)
        out["per90ProdNoPen"] = round(max(0.0, g90 - pens90) + a90, 3)
        bonus = (goals or 0) * 3 + (assists or 0) * 1 + (pens or 0) * 0.5
        if role in ("P", "D") and out["csProxy"] is not None:
            bonus += out["csProxy"] * 6
        out["bonusProxy"] = round(bonus, 1)
    elif fm is not None:
        out["bonusProxy"] = round(max(0.0, (fm - (mv or 6.0)) * 12), 1)
    return out


def fair_price(
    fvm: int,
    role: str,
    starter: int | None,
    fitness: int | None,
    prod: dict,
    name: str | None = None,
) -> dict:
    base = max(1, fvm)
    mult = 1.0
    if starter is not None:
        if starter >= 80:
            mult += 0.08
        elif starter < 45:
            mult -= 0.18
        elif starter < 60:
            mult -= 0.08
    if fitness is not None:
        if fitness >= 75:
            mult += 0.05
        elif fitness < 45:
            mult -= 0.2
        elif fitness < 55:
            mult -= 0.1
    p90 = prod.get("per90Prod")
    if p90 is not None:
        if role == "A" and p90 >= 0.55:
            mult += 0.1
        elif role == "C" and p90 >= 0.35:
            mult += 0.08
        elif role == "D" and p90 >= 0.2:
            mult += 0.12
        elif p90 < 0.08 and role in ("A", "C"):
            mult -= 0.08
    fair = int(round(base * mult))
    low = max(1, int(round(fair * 0.82)))
    high = int(round(fair * 1.12))
    mock = MOCK_RANGES.get(name or "")
    leave = None
    mock_mid = None
    if mock:
        leave = mock["leave"]
        mock_mid = mock["mid"]
        # Blend fair toward mock mid for top names.
        fair = int(round(0.55 * fair + 0.45 * mock["mid"]))
        low = min(low, mock["low"])
        high = max(high, mock["high"])
    return {
        "fair": fair,
        "low": low,
        "high": high,
        "leave": leave,
        "mockMid": mock_mid,
        "mockLow": mock["low"] if mock else None,
        "mockHigh": mock["high"] if mock else None,
    }


def traffic_light(fvm: int, band: dict) -> str:
    leave = band.get("leave")
    high = band.get("high") or fvm
    low = band.get("low") or fvm
    fair = band.get("fair") or fvm
    if leave and fvm >= leave:
        return "overpay"
    if fvm > high:
        return "overpay"
    if fvm < low:
        return "value"
    if abs(fvm - fair) <= max(5, fair * 0.08):
        return "fair"
    if fvm > fair:
        return "rich"
    return "value"


def scenario_plans(role: str) -> dict:
    return dict(SCENARIO_PLANS.get(role, {}))


def injury_profile(name: str) -> dict | None:
    fine = INJURY_FINE.get(name)
    frag = FRAGILE.get(name)
    if not fine and not frag:
        return None
    out = {
        "fragile": frag or 0,
        "label": None,
        "daysOut": None,
        "muscular": None,
        "multiComp": None,
        "note": None,
    }
    if fine:
        out.update(
            {
                "label": fine.get("note") or "fragilità",
                "daysOut": fine.get("daysOut"),
                "muscular": fine.get("muscular"),
                "multiComp": fine.get("multiComp"),
                "note": fine.get("note"),
            }
        )
    elif frag and frag >= 3:
        out["label"] = "storico fragilità"
    elif frag:
        out["label"] = "monitorare"
    return out


def team_context(team: str) -> dict:
    return dict(
        TEAM_CONTEXT.get(
            team,
            {
                "att": 3,
                "def": 3,
                "style": "n/d",
                "cs": "n/d",
                "sched": 3,
                "module": "n/d",
                "note": "",
            },
        )
    )


def squad_fit_hint(role: str, tier: str, fvm: int) -> str:
    if role == "P":
        return "Fit P: 1 titolare + 1 backup; priorità CS/voto se budget ok."
    if role == "D":
        if tier in ("super_top", "top", "top_bonus", "S") or fvm >= 80:
            return "Fit D: profilo bonus/fascia — 1 slot elite, resto cemento mod."
        return "Fit D: cemento modificatore / depth a basso costo."
    if role == "C":
        if tier in ("super_top", "top", "S", "A") or fvm >= 100:
            return "Fit C: motore bonus (rigori/inserimenti) — max 2 elite."
        return "Fit C: volume voti + upside lowcost."
    if tier in ("super_top", "S") or fvm >= 200:
        return "Fit A: slot top — definisce budget stagione."
    if fvm >= 80:
        return "Fit A: semi-top / value secondario."
    return "Fit A: depth/panchina a residuale."


def build_scientific_note(
    *,
    name: str,
    role: str,
    team: str,
    fvm: int,
    tier: str,
    age: int | None,
    starter: int | None,
    fitness: int | None,
    fitness_lbl: str,
    fm: float | None,
    mv: float | None,
    pg: int | None,
    playeds_expected: int | None,
    goals: int | None,
    assists: int | None,
    pens: int | None,
    gs: int | None,
    penalty_label: str,
    flags: list[str],
) -> str:
    mins = minutes_model(role, pg, playeds_expected, starter)
    minutes = mins["minutesEst"]
    prod = production_metrics(role, pg, fm, mv, goals, assists, pens, gs, minutes)
    band = fair_price(fvm, role, starter, fitness, prod, name)
    light = traffic_light(fvm, band)
    ctx = TEAM_CONTEXT.get(
        team,
        {"att": 3, "def": 3, "style": "n/d", "cs": "n/d", "sched": 3, "module": "n/d", "note": ""},
    )
    parts: list[str] = []

    leave_txt = f", leave>{band['leave']}" if band.get("leave") else ""
    mock_txt = ""
    if band.get("mockMid") is not None:
        mock_txt = f" Mock6 ~{band['mockLow']}–{band['mockHigh']} (mid {band['mockMid']})."
    parts.append(
        f"Mercato: FVM {fvm}, fair ~{band['fair']} (banda {band['low']}–{band['high']}{leave_txt}) [{light}].{mock_txt}"
    )
    if light == "overpay":
        parts.append("Listone in zona overpay → non inseguire.")
    elif light == "value":
        parts.append("Listone sotto fair/mock → possibile value.")

    if mins["minutesEst"] is not None:
        parts.append(
            f"Minuti proxy ~{mins['minutesEst']}' ({mins['appsEst']} app × {mins['mpg']}'"
            f", start~{mins['startRate']}%, panch~{mins['benchRate']}%)."
        )
    if prod["per90Prod"] is not None:
        nop = prod.get("per90ProdNoPen")
        extra = f", no-rig {nop}" if nop is not None else ""
        parts.append(
            f"Prod/90: {prod['per90Prod']} (G{prod['per90Goals']}/A{prod['per90Assists']}{extra})."
        )
    if prod.get("bonusPure") is not None and prod.get("votePure") is not None:
        parts.append(f"Voto puro MV {prod['votePure']} · bonus puro Δ {prod['bonusPure']:+}.")
    if prod.get("csProxy") is not None:
        parts.append(f"CS proxy {prod['csProxy']} (GS/app {prod.get('gsPerApp')}).")
    if goals is not None or assists is not None:
        g = goals or 0
        a = assists or 0
        p = pens or 0
        extra = f", rig {p}" if p else ""
        parts.append(f"Bonus raw 25/26: {g}G+{a}A{extra}.")

    sched_lbl = {1: "calendario duro", 2: "medio-duro", 3: "medio", 4: "morbido", 5: "molto morbido"}.get(
        ctx.get("sched", 3), "medio"
    )
    parts.append(
        f"Contesto {team}: att{ctx['att']}/def{ctx['def']}, {ctx['style']}, CS {ctx['cs']}, "
        f"modulo {ctx.get('module','?')}, avvio {sched_lbl}."
    )
    if ctx.get("note"):
        parts.append(ctx["note"] + ".")
    if role in ("P", "D"):
        parts.append("Mod: preferisci CS alto + voti stabili.")

    fine = INJURY_FINE.get(name)
    frag = FRAGILE.get(name)
    if fitness is not None:
        tip = ""
        if fitness < 45:
            tip = " Evita overpay / preferisci sconto."
        elif fitness < 55:
            tip = " Tetto stretto."
        parts.append(f"Durabilità: {fitness_lbl} ({fitness}/100).{tip}")
    if fine:
        mus = "sì" if fine.get("muscular") else "no"
        parts.append(
            f"Infortuni fini: ~{fine.get('daysOut', '?')}g out, muscolare {mus}, "
            f"carico×comp {fine.get('multiComp', 0)} ({fine.get('note','')})."
        )
    elif frag and frag >= 3:
        parts.append("Storico fragilità: sconto obbligatorio.")

    if age is not None:
        parts.append(f"Età {age}.")
    if starter is not None:
        parts.append(f"Tit~{starter}%.")
    if playeds_expected is not None:
        parts.append(f"Playeds attesi {playeds_expected}.")

    parts.append(squad_fit_hint(role, tier, fvm))
    plan = SCENARIO_PLANS.get(role, {})
    if plan:
        parts.append(f"Scenario A: {plan.get('A','')}.")
        parts.append(f"Pivot: {plan.get('pivot','')}.")
    if role == "A" and tier in ("super_top", "S"):
        parts.append("Se rivali sparano >leave/fair+15% → piano B 2+2.")
    elif role == "D" and (tier in ("super_top", "S") or name == "Dimarco"):
        parts.append("Se Dimarco >~220 a 6 → no-buy, 2 fasce mid.")
    elif role == "C" and tier in ("super_top", "top", "S", "A"):
        parts.append("Alterna rigorista vs box-to-box in base a chi esce prima.")
    elif role == "P" and tier in ("super_top", "top", "S", "A"):
        parts.append("1 elite P o 2 medi — non entrambi costosi.")

    if penalty_label and penalty_label != "—":
        parts.append(f"Flag: {penalty_label}.")
    if flags:
        parts.append("Tag: " + ", ".join(flags[:4]) + ".")

    expert = EXPERT_NOTES.get(name)
    if expert:
        parts.append(expert)

    return " ".join(parts)
