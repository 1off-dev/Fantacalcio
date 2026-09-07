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
    "INT": {"att": 5, "def": 5, "style": "attacco da big + modificatore", "cs": "alto", "sched": 2, "module": "3-5-2", "note": "carico europeo alto, ma ottima base per la porta inviolata"},
    "NAP": {"att": 5, "def": 4, "style": "attacco alto", "cs": "medio-alto", "sched": 3, "module": "4-3-3", "note": "tanti cross e volume offensivo"},
    "MIL": {"att": 4, "def": 4, "style": "bilanciato da big", "cs": "medio-alto", "sched": 3, "module": "4-2-3-1", "note": "rotazioni possibili per l’Europa"},
    "JUV": {"att": 4, "def": 5, "style": "controllo e modificatore", "cs": "alto", "sched": 3, "module": "3-4-2-1", "note": "difesa forte da modificatore"},
    "ATA": {"att": 4, "def": 3, "style": "volume offensivo", "cs": "medio", "sched": 3, "module": "3-4-2-1", "note": "buon contesto per bonus di centrocampisti e attaccanti"},
    "ROM": {"att": 4, "def": 4, "style": "transizioni e modificatore", "cs": "medio-alto", "sched": 3, "module": "3-4-2-1", "note": "attacco concentrato su pochi riferimenti (Malen e dintorni)"},
    "FIO": {"att": 3, "def": 3, "style": "possesso medio", "cs": "medio", "sched": 3, "module": "4-2-3-1", "note": "crea gioco, ma senza tetto da big"},
    "BOL": {"att": 3, "def": 4, "style": "solidità", "cs": "medio-alto", "sched": 4, "module": "4-2-3-1", "note": "buona base per value da porta inviolata"},
    "LAZ": {"att": 3, "def": 3, "style": "gioco sulle fasce e rigori", "cs": "medio", "sched": 3, "module": "4-3-3", "note": "gli esterni e i rigoristi possono fare la differenza"},
    "TOR": {"att": 2, "def": 3, "style": "blocco basso", "cs": "medio", "sched": 4, "module": "3-5-2", "note": "tetto di produzione basso"},
    "GEN": {"att": 2, "def": 3, "style": "difensivo", "cs": "medio", "sched": 4, "module": "3-5-2", "note": "utile soprattutto per low-cost da modificatore"},
    "UDI": {"att": 3, "def": 2, "style": "transizioni", "cs": "basso", "sched": 4, "module": "3-5-2", "note": "partite aperte, più bonus ma anche più reti subite"},
    "COM": {"att": 3, "def": 3, "style": "possesso e creazione", "cs": "medio", "sched": 3, "module": "4-2-3-1", "note": "contesto interessante per Paz e Kean"},
    "SAS": {"att": 3, "def": 2, "style": "partite aperte", "cs": "basso", "sched": 4, "module": "4-3-3", "note": "rigori e bonus possibili, poca solidità"},
    "CRE": {"att": 2, "def": 2, "style": "neopromossa", "cs": "basso", "sched": 3, "module": "3-5-2", "note": "andamento volatile"},
    "PAR": {"att": 2, "def": 2, "style": "neopromossa", "cs": "basso", "sched": 3, "module": "4-2-3-1", "note": "soprattutto profondità di rosa"},
    "PIS": {"att": 2, "def": 2, "style": "neopromossa", "cs": "basso", "sched": 3, "module": "3-5-2", "note": "pavimento basso"},
    "VER": {"att": 2, "def": 2, "style": "lotta salvezza", "cs": "basso", "sched": 4, "module": "3-4-2-1", "note": "evita overpay"},
    "CAG": {"att": 2, "def": 2, "style": "lotta salvezza", "cs": "basso", "sched": 4, "module": "4-3-3", "note": "target tardivi a basso costo"},
    "LEC": {"att": 2, "def": 2, "style": "lotta salvezza", "cs": "basso", "sched": 4, "module": "4-3-3", "note": "target tardivi a basso costo"},
    "MON": {"att": 2, "def": 2, "style": "lotta salvezza", "cs": "basso", "sched": 4, "module": "3-4-2-1", "note": "tetto basso"},
    "VEN": {"att": 2, "def": 2, "style": "lotta salvezza", "cs": "basso", "sched": 4, "module": "3-4-2-1", "note": "andamento volatile"},
    "FRO": {"att": 2, "def": 2, "style": "neopromossa", "cs": "basso", "sched": 3, "module": "3-5-2", "note": "soprattutto profondità"},
}

# Mock/auction paid ranges at 6 teams × 500 (sintesi guide/mock, riscalati da 1000).
MOCK_RANGES: dict[str, dict] = {
    "Malen": {"low": 190, "mid": 215, "high": 240, "leave": 230},
    "Martinez L.": {"low": 140, "mid": 165, "high": 190, "leave": 185},
    "Thuram": {"low": 80, "mid": 100, "high": 120, "leave": 118},
    "Hojlund": {"low": 70, "mid": 90, "high": 115, "leave": 110},
    "Kean": {"low": 45, "mid": 60, "high": 75, "leave": 72},
    "Dimarco": {"low": 80, "mid": 100, "high": 120, "leave": 112},
    "Paz N.": {"low": 90, "mid": 115, "high": 145, "leave": 140},
    "Calhanoglu": {"low": 70, "mid": 90, "high": 110, "leave": 108},
    "McTominay": {"low": 65, "mid": 85, "high": 105, "leave": 102},
    "Svilar": {"low": 35, "mid": 48, "high": 60, "leave": 58},
    "Vicario": {"low": 22, "mid": 30, "high": 40, "leave": 39},
    "Orsolini": {"low": 35, "mid": 48, "high": 60, "leave": 59},
    "Pulisic": {"low": 40, "mid": 52, "high": 68, "leave": 65},
    "Wesley": {"low": 35, "mid": 48, "high": 62, "leave": 60},
    "Bremer": {"low": 28, "mid": 38, "high": 50, "leave": 48},
    "Bastoni": {"low": 20, "mid": 28, "high": 38, "leave": 36},
    "Scamacca": {"low": 35, "mid": 48, "high": 65, "leave": 55},
    "Dybala": {"low": 20, "mid": 30, "high": 45, "leave": 38},
    "Leao": {"low": 40, "mid": 55, "high": 75, "leave": 65},
    "Yildiz": {"low": 30, "mid": 42, "high": 60, "leave": 58},
    "Douvikas": {"low": 28, "mid": 38, "high": 50, "leave": 48},
    "Carnesecchi": {"low": 18, "mid": 24, "high": 32, "leave": 31},
    "Maignan": {"low": 15, "mid": 22, "high": 32, "leave": 30},
    "Barella": {"low": 25, "mid": 35, "high": 48, "leave": 45},
    "Zaccagni": {"low": 22, "mid": 32, "high": 45, "leave": 42},
    "Da Cunha": {"low": 20, "mid": 28, "high": 38, "leave": 36},
}

# Crediti asta (lega 6×500). FVM Fantacalcio è tipicamente su scala ~1000.
BUDGET_TOTAL = 500
FVM_SCALE = 0.5


def to_auction_credits(fvm: int | float | None) -> int:
    if fvm is None:
        return 1
    return max(1, int(round(float(fvm) * FVM_SCALE)))

# Scenario planner templates per role (A/B/C) — linguaggio naturale · asta 6×500.
SCENARIO_PLANS: dict[str, dict] = {
    "P": {
        "A": "un portiere big affidabile (tipo Svilar) più due titolari low-cost",
        "B": "due portieri medi (Vicario/Carnesecchi/Maignan) più un backup da pochi crediti",
        "C": "tre titolari di provincia se i top costano troppo",
        "pivot": "se Svilar sfora il tetto (~58), prendi Vicario più un titolare economico",
    },
    "D": {
        "A": "un esterno da bonus (Dimarco/Wesley) più quattro-cinque cementi da modificatore",
        "B": "niente elite di fascia, due esterni value e tanti voti da modificatore",
        "C": "solo cementi a basso-medio prezzo se Dimarco è fuori budget",
        "pivot": "se Dimarco passa i ~110, punta su Molina/Wesley value e centrali solidi",
    },
    "C": {
        "A": "uno tra Paz/Calhanoglu/McTominay più un rigorista medio e volume di voti",
        "B": "niente super-top, due pezzi da bonus (Orsolini/Pulisic/Zaccagni) e low-cost",
        "C": "solo volume e rigoristi secondari se i top gonfiano",
        "pivot": "se Paz esce caro vai su Calhanoglu/McTominay; se anche loro sono cari, Orsolini + Da Cunha",
    },
    "A": {
        "A": "Malen first: warchest A (~260), Malen ≤230–245 + profondità a 1",
        "B": "piano anti-Malen con due+due (Lautaro/Thuram/Kean/Douvikas)",
        "C": "tre medi più upside se i top scappano di prezzo",
        "pivot": "con piano Malen first tieni hard stop ~245; se sfora, passa al B 2+2. Con gli altri piani, leave ~230 attiva già il B",
    },
}

EXPERT_NOTES: dict[str, str] = {
    "Malen": "Top assoluto post-exploit: col piano Malen first punta 215 e non superare 245; oltre leave (~230) sugli altri piani spesso conviene il 2+2.",
    "Martinez L.": "Affidabile su gol e assist: è il piano B naturale se Malen scappa di prezzo.",
    "Dimarco": "È l’unico difensore che produce come un centrocampista/attaccante; a 6×500 spesso non vale se passa i 110.",
    "Paz N.": "Giovane di hype a Como: minutaggio da seguire, ma il potenziale bonus è altissimo.",
    "Calhanoglu": "Rigorista e tiro da lontano; a 32 anni prendilo solo se la forma regge, altrimenti preferisci McTominay.",
    "McTominay": "Box-to-box da bonus: meno rigorista di Calhanoglu, ma di solito più continuo sui minuti.",
    "Svilar": "La certezza più chiara tra i portieri big col modificatore: sotto 40–48 in lega a 6×500 è difficile lasciarlo.",
    "Thuram": "Gol e assist senza dipendere dai rigori Inter: value se Malen e Lautaro gonfiano.",
    "Hojlund": "A Napoli ha upside ma anche concorrenza: non pagarlo da top 1 senza certezza di titolare.",
    "Kean": "Titolare a Como con bonus: semi-top concreto nelle guide di fascia media.",
    "Leao": "Alti e bassi: ha senso solo a sconto, mai da budget da top.",
    "Dybala": "Qualità a giorni alterni e infortuni: tetto basso, non inseguire.",
    "Scamacca": "Rigorista Atalanta ma fragile: la forma è tutto, chiedi sconto.",
    "De Bruyne": "Qualità top, età e carico alti: pochi gettoni a prezzo pieno.",
    "Barella": "Motore Inter: meno gol di McTominay/Calhanoglu, voti più solidi.",
    "Orsolini": "Specialista rigori a Bologna: target da bonus tra i centrocampisti.",
    "Pulisic": "A Milano porta bonus offensivi; la gerarchia rigoristi non è chiusa.",
    "Bremer": "Modificatore e bonus se resta sano; storico muscolare → non overpay.",
    "Bastoni": "Pilastro Inter da modificatore: meno bonus di Dimarco, più continuità.",
    "Wesley": "Esterno emergente da bonus: nei mock spesso subito dopo Dimarco.",
    "Molina N.": "Terzino da bonus; cotazione alta ma sotto Dimarco.",
    "Yildiz": "Upside Juve e possibili rigori: volatilità da giovane.",
    "Douvikas": "Punta Como con minutaggio: value nel piano anti-Malen.",
    "Ramos G.": "A Milan contendente offensivo/rigori: attenzione alle rotazioni.",
    "Kolo Muani": "A Juve è rigorista designato, ma non un cemento di titolarità.",
    "Zaccagni": "Alla Lazio è primo rigorista fluido e porta bonus: target mid tra i C.",
    "Lookman": "Macchina da bonus se resta sano e titolare.",
    "Chiesa": "Talento fragile: solo a forte sconto.",
    "Vlahovic": "Alti e bassi più muscolari: tieni un tetto rigoroso.",
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
    """fvm is already in auction credits (6×500)."""
    if role == "P":
        return "In rosa ti serve un portiere titolare affidabile e un secondo a basso costo: non spendere due volte da top."
    if role == "D":
        if tier in ("super_top", "top", "top_bonus", "S") or fvm >= 40:
            return "Profilo da esterno/bonus: tienine al massimo uno costoso e riempi il resto con difensori da modificatore."
        return "Profilo da cemento per il modificatore: utile a basso/medio prezzo per chiudere la difesa."
    if role == "C":
        if tier in ("super_top", "top", "S", "A") or fvm >= 50:
            return "Centrocampista da bonus (rigori o inserimenti): al massimo due pezzi elite, poi volume di voti."
        return "Centrocampista da volume: buono per riempire la rosa senza bruciare il budget."
    if tier in ("super_top", "S") or fvm >= 100:
        return "Attaccante da slot top: decide buona parte del budget di stagione."
    if fvm >= 40:
        return "Attaccante semi-top o value: utile come secondo/terzo pezzo dietro al big."
    return "Attaccante da profondità: prendilo a residuo, non a prezzo pieno."


def _sched_phrase(sched: int) -> str:
    return {
        1: "un avvio di calendario piuttosto duro",
        2: "un avvio di calendario medio-duro",
        3: "un avvio di calendario nella media",
        4: "un avvio di calendario favorevole",
        5: "un avvio di calendario molto favorevole",
    }.get(sched, "un avvio di calendario nella media")


def _traffic_phrase(light: str) -> str:
    return {
        "overpay": "Sul listone risulta caro rispetto al fair e ai mock: meglio non inseguirlo.",
        "value": "Sul listone sembra sotto il prezzo giusto: possibile affare se la titolarità regge.",
        "rich": "Sul listone è un po’ sopra il fair: paga solo se ti serve davvero nello schema.",
        "fair": "Sul listone è in linea con il prezzo stimato.",
    }.get(light, "")


def build_scientific_note(
    *,
    name: str,
    role: str,
    team: str,
    fvm: int,
    fvm_listone: int | None = None,
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

    # Prezzo (crediti asta 6×500)
    listone = fvm_listone if fvm_listone is not None else int(round(fvm / FVM_SCALE))
    price_bits = [
        f"Listone Fantacalcio {listone} → ≈{fvm} in asta 6×{BUDGET_TOTAL}",
        f"prezzo stimato intorno a {band['fair']} (fascia ragionevole {band['low']}–{band['high']})",
    ]
    if band.get("leave") is not None:
        price_bits.append(f"meglio lasciarlo andare sopra {band['leave']}")
    parts.append("Prezzo: " + "; ".join(price_bits) + ".")
    if band.get("mockMid") is not None:
        parts.append(
            f"Nelle aste a 6×{BUDGET_TOTAL} di solito esce tra {band['mockLow']} e {band['mockHigh']} "
            f"(valore medio circa {band['mockMid']})."
        )
    traffic = _traffic_phrase(light)
    if traffic:
        parts.append(traffic)

    # Minuti / titolarità
    if mins["minutesEst"] is not None and mins.get("appsEst") is not None:
        bench = mins.get("benchRate") or 0
        start = mins.get("startRate")
        if start is not None and start >= 85:
            min_txt = (
                f"Dovrebbe giocare molto: circa {mins['minutesEst']} minuti stimati "
                f"({mins['appsEst']} partite × ~{mins['mpg']}'), con titolarità intorno al {start}%."
            )
        elif start is not None and start >= 55:
            min_txt = (
                f"Minutaggio da monitorare: circa {mins['minutesEst']} minuti stimati "
                f"({mins['appsEst']} partite × ~{mins['mpg']}'), titolarità ~{start}% "
                f"e rischio rotazioni/panchina intorno al {bench}%."
            )
        else:
            min_txt = (
                f"Non è un cemento di minuti: stima ~{mins['minutesEst']} minuti "
                f"({mins['appsEst']} partite × ~{mins['mpg']}'), spesso a disposizione "
                f"(panchina/subentri ~{bench}%)."
            )
        parts.append(min_txt + " Stima da presenze, non da feed minuti ufficiali.")
    elif starter is not None:
        parts.append(f"Probabilità di partire titolare intorno al {starter}%.")

    # Produzione
    if goals is not None or assists is not None:
        g = goals or 0
        a = assists or 0
        p = pens or 0
        season = "Nella scorsa stagione"
        if p:
            parts.append(f"{season} ha fatto {g} gol e {a} assist (di cui {p} rigoristi).")
        else:
            parts.append(f"{season} ha fatto {g} gol e {a} assist.")
    if prod["per90Prod"] is not None:
        g90 = prod.get("per90Goals")
        a90 = prod.get("per90Assists")
        nop = prod.get("per90ProdNoPen")
        line = (
            f"Produzione stimata ogni 90 minuti: {prod['per90Prod']} tra gol e assist"
        )
        if g90 is not None and a90 is not None:
            line += f" (gol {g90}, assist {a90}"
            if nop is not None:
                line += f"; senza rigori ~{nop}"
            line += ")"
        parts.append(line + ".")
    if prod.get("bonusPure") is not None and prod.get("votePure") is not None:
        delta = prod["bonusPure"]
        if delta >= 0.4:
            parts.append(
                f"Il voto medio è {prod['votePure']}, ma i bonus alzano molto il rendimento "
                f"(+{delta} rispetto al voto puro)."
            )
        elif delta <= -0.3:
            parts.append(
                f"Il voto medio è {prod['votePure']}: i bonus aiutano poco "
                f"({delta:+} rispetto al voto puro), quindi conta soprattutto la continuità."
            )
        else:
            parts.append(
                f"Rendimento equilibrato tra voto ({prod['votePure']}) e bonus ({delta:+})."
            )
    if prod.get("csProxy") is not None and role in ("P", "D"):
        gs_app = prod.get("gsPerApp")
        cs = prod["csProxy"]
        if cs >= 1.0:
            parts.append(
                f"Buona lettura da porta inviolata: pochi gol subiti a partita"
                + (f" (~{gs_app})" if gs_app is not None else "")
                + ", utile col modificatore."
            )
        else:
            parts.append(
                f"Contributo alla porta inviolata solo medio"
                + (f" (gol subiti/partita ~{gs_app})" if gs_app is not None else "")
                + ": meglio se entra a prezzo contenuto."
            )

    # Contesto club
    att = ctx.get("att", 3)
    deff = ctx.get("def", 3)
    style = ctx.get("style", "n/d")
    cs = ctx.get("cs", "n/d")
    module = ctx.get("module", "?")
    parts.append(
        f"Gioca nel {team} ({module}): attacco {att}/5, difesa {deff}/5, stile «{style}», "
        f"propensione alla porta inviolata {cs}, {_sched_phrase(int(ctx.get('sched', 3)))}."
    )
    if ctx.get("note"):
        note = ctx["note"].rstrip(".")
        parts.append(f"Contesto club: {note}.")
    if role in ("P", "D"):
        parts.append("Col modificatore difesa conta avere voti stabili e poche reti subite.")

    # Forma / infortuni / età
    if fitness is not None:
        if fitness < 45:
            tip = " Conviene prenderlo solo a forte sconto."
        elif fitness < 55:
            tip = " Tieni un tetto basso e non inseguire."
        else:
            tip = ""
        parts.append(f"Affidabilità fisica: {fitness_lbl} ({fitness}/100).{tip}")
    fine = INJURY_FINE.get(name)
    frag = FRAGILE.get(name)
    if fine:
        days = fine.get("daysOut", "?")
        mus = "con storicità muscolare" if fine.get("muscular") else "senza particolare ricorrenza muscolare"
        load = fine.get("multiComp", 0)
        load_txt = {
            0: "carico di partite gestibile",
            1: "un po’ di carico extra (coppe/nazionali)",
            2: "carico alto per più competizioni",
        }.get(load, "carico da monitorare")
        detail = fine.get("note") or ""
        parts.append(
            f"Storico disponibilità: circa {days} giorni persi di recente, {mus}, {load_txt}"
            + (f" — {detail}" if detail else "")
            + "."
        )
    elif frag and frag >= 3:
        parts.append("Ha uno storico di fragilità: non pagarlo come se fosse sempre disponibile.")

    identity = []
    if age is not None:
        identity.append(f"{age} anni")
    if starter is not None:
        identity.append(f"titolare stimato al {starter}%")
    if playeds_expected is not None and starter is None:
        identity.append(f"titolarità listone {playeds_expected}%")
    if identity:
        parts.append("Profilo: " + ", ".join(identity) + ".")

    # Fit + scenari
    parts.append(squad_fit_hint(role, tier, fvm))
    plan = SCENARIO_PLANS.get(role, {})
    if plan:
        parts.append(f"Piano A sul ruolo: {plan.get('A', '').rstrip('.')}.")
        if plan.get("pivot"):
            parts.append(f"Se i top scappano: {plan.get('pivot', '').rstrip('.')}.")

    if role == "A" and tier in ("super_top", "S"):
        leave = band.get("leave") or band.get("high")
        if leave:
            parts.append(
                f"Se i rivali lo spingono oltre {leave} (o oltre il fair +15%), passa al piano B con due attaccanti medi."
            )
        else:
            parts.append("Se esce troppo caro, passa al piano B con due attaccanti medi.")
    elif role == "D" and (tier in ("super_top", "S") or name == "Dimarco"):
        parts.append("Se Dimarco supera circa 110 in lega a 6×500, meglio lasciarlo e prendere due esterni mid.")
    elif role == "C" and tier in ("super_top", "top", "S", "A"):
        parts.append("Scegli tra rigorista e box-to-box in base a chi esce prima e a che prezzo.")
    elif role == "P" and tier in ("super_top", "top", "S", "A"):
        parts.append("Prendi un portiere elite oppure due medi: non entrambi costosi.")

    if penalty_label and penalty_label != "—":
        parts.append(f"Sui rigoristi: {penalty_label}.")

    # Soften flags into words (skip raw snake tags)
    flag_tips = []
    if "hype_post_gol" in flags:
        flag_tips.append("c’è molto hype dopo i gol: attenzione all’overpay")
    if "lasciare_se_overpay" in flags:
        flag_tips.append("lascialo se il prezzo sfora")
    if "mod_e_bonus" in flags:
        flag_tips.append("unisce modificatore e bonus")
    if "costa_come_centrocampista" in flags:
        flag_tips.append("può costare come un centrocampista")
    if "unica_certezza_big" in flags:
        flag_tips.append("è tra le poche certezze tra i big")
    if "sposta_asta_centrocampo" in flags:
        flag_tips.append("può spostare tutta l’asta di centrocampo")
    if "verificare_gerarchia" in flags:
        flag_tips.append("verifica la gerarchia in porta/reparto")
    if "rischio_fisico" in flags:
        flag_tips.append("rischio fisico da considerare")
    if "listone_overpay" in flags:
        flag_tips.append("listone già alto")
    if "listone_value" in flags:
        flag_tips.append("listone interessante")
    if flag_tips:
        parts.append("Da ricordare: " + "; ".join(flag_tips[:4]) + ".")

    expert = EXPERT_NOTES.get(name)
    if expert:
        parts.append(expert if expert.endswith(".") else expert + ".")

    return " ".join(p.strip() for p in parts if p and p.strip())


def parse_mantra(raw: str | None) -> list[str]:
    """Codici Mantra Fantacalcio (por, dc, e, t, …) da data-filter-role-mantra."""
    if not raw:
        return []
    return [c.strip().lower() for c in raw.split("|") if c.strip()]


def advanced_profile(role: str, mantra: list[str]) -> dict | None:
    """Segnala D/C che in Mantra giocano più avanti del ruolo Classic."""
    codes = set(mantra or [])
    if role == "D":
        if codes & {"e", "w"}:
            if "w" in codes:
                return {
                    "playAdvanced": True,
                    "advancedKind": "esterno_ala",
                    "advancedLabel": "Esterno/ala",
                    "advancedHint": "Mantra esterno/ala: profilo offensivo da bonus",
                }
            return {
                "playAdvanced": True,
                "advancedKind": "terzino_esterno",
                "advancedLabel": "Terzino/esterno",
                "advancedHint": "Mantra terzino o esterno: sale e porta bonus",
            }
        if "b" in codes and codes & {"e", "dd", "ds"}:
            return {
                "playAdvanced": True,
                "advancedKind": "braccetto",
                "advancedLabel": "Braccetto",
                "advancedHint": "Braccetto di difesa a 3: può salire sulla fascia",
            }
        return None
    if role == "C":
        if codes & {"t", "a"}:
            kind = "trequartista" if "t" in codes else "centrocampista_offensivo"
            label = "Trequartista" if "t" in codes else "Offensivo"
            return {
                "playAdvanced": True,
                "advancedKind": kind,
                "advancedLabel": label,
                "advancedHint": "Mantra trequartista/attacco: gioca più avanti del classico C",
            }
        if "w" in codes:
            return {
                "playAdvanced": True,
                "advancedKind": "ala_centrocampo",
                "advancedLabel": "Ala/esterno",
                "advancedHint": "Mantra ala/wing: profilo offensivo da fascia",
            }
        if "e" in codes and "m" not in codes:
            return {
                "playAdvanced": True,
                "advancedKind": "esterno_centrocampo",
                "advancedLabel": "Esterno",
                "advancedHint": "Mantra esterno di centrocampo",
            }
        return None
    return None


def assign_gk_depth(players: list[dict]) -> None:
    """Assegna P1/P2/P3 per squadra (mutates list in place)."""
    by_team: dict[str, list[dict]] = {}
    for p in players:
        if p.get("role") != "P":
            continue
        by_team.setdefault(p.get("team") or "?", []).append(p)

    def sort_key(p: dict) -> tuple:
        return (
            -(p.get("starterProb") if p.get("starterProb") is not None else -1),
            -(p.get("playedsExpected") if p.get("playedsExpected") is not None else -1),
            -(p.get("fvm") or 0),
            -(p.get("pgPrev") if p.get("pgPrev") is not None else -1),
            p.get("name") or "",
        )

    for team, keepers in by_team.items():
        ranked = sorted(keepers, key=sort_key)
        uncertain = any("verificare_gerarchia" in (p.get("flags") or []) for p in ranked[:2])
        if len(ranked) >= 2:
            top = ranked[0].get("starterProb") or 0
            second = ranked[1].get("starterProb") or 0
            if top - second < 20 and top < 95:
                uncertain = True
        labels = {1: "Titolare", 2: "Secondo", 3: "Terzo"}
        for i, p in enumerate(ranked):
            slot = i + 1 if i < 3 else None
            p["gkSlot"] = slot
            p["gkSlotLabel"] = labels.get(slot)
            p["gkUncertain"] = bool(uncertain and slot in (1, 2))
            if slot and slot <= 3:
                flags = list(p.get("flags") or [])
                tag = f"porta_{slot}"
                if tag not in flags:
                    flags.append(tag)
                if uncertain and slot in (1, 2) and "verificare_gerarchia" not in flags:
                    flags.append("verificare_gerarchia")
                p["flags"] = flags
