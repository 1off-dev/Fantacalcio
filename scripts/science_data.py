"""Heuristic scientific signals for Fantacalcio Classic auction board."""

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
    "Solet": 1, "Gila": 1, "Spence": 1, "Chalobah T.": 1, "Lookman": 2,
    "Chiesa": 4, "Vlahovic": 3, "Koopmeiners": 1, "Retegui": 1,
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
}

TEAM_CONTEXT: dict[str, dict] = {
    "INT": {"att": 5, "def": 5, "style": "top-attacco+mod", "cs": "alto"},
    "NAP": {"att": 5, "def": 4, "style": "attacco alto", "cs": "medio-alto"},
    "MIL": {"att": 4, "def": 4, "style": "bilanciato big", "cs": "medio-alto"},
    "JUV": {"att": 4, "def": 5, "style": "controllo+mod", "cs": "alto"},
    "ATA": {"att": 4, "def": 3, "style": "volume offensivo", "cs": "medio"},
    "ROM": {"att": 4, "def": 4, "style": "transizioni+mod", "cs": "medio-alto"},
    "FIO": {"att": 3, "def": 3, "style": "possesso medio", "cs": "medio"},
    "BOL": {"att": 3, "def": 4, "style": "solidità", "cs": "medio-alto"},
    "LAZ": {"att": 3, "def": 3, "style": "fasce+rigori", "cs": "medio"},
    "TOR": {"att": 2, "def": 3, "style": "blocco basso", "cs": "medio"},
    "GEN": {"att": 2, "def": 3, "style": "difensivo", "cs": "medio"},
    "UDI": {"att": 3, "def": 2, "style": "transizioni", "cs": "basso"},
    "COM": {"att": 3, "def": 3, "style": "possesso/creazione", "cs": "medio"},
    "SAS": {"att": 3, "def": 2, "style": "open games", "cs": "basso"},
    "CRE": {"att": 2, "def": 2, "style": "neopromossa", "cs": "basso"},
    "PAR": {"att": 2, "def": 2, "style": "neopromossa", "cs": "basso"},
    "PIS": {"att": 2, "def": 2, "style": "neopromossa", "cs": "basso"},
    "VER": {"att": 2, "def": 2, "style": "sopravvivenza", "cs": "basso"},
    "CAG": {"att": 2, "def": 2, "style": "sopravvivenza", "cs": "basso"},
    "LEC": {"att": 2, "def": 2, "style": "sopravvivenza", "cs": "basso"},
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
    if starter_prob is None and age is None and name not in FRAGILE:
        return None, "n/d"
    base = 72
    if starter_prob is not None:
        base = int(0.45 * starter_prob + 0.55 * 70)
    base -= FRAGILE.get(name, 1) * 8
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


def est_minutes(pg: int | None, playeds_expected: int | None) -> int | None:
    if playeds_expected is None and pg is None:
        return None
    pe = playeds_expected if playeds_expected is not None else 0
    p = pg if pg is not None else 0
    apps = 0.55 * pe + 0.45 * min(38, p)
    return int(round(apps * 78))


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
        "bonusProxy": None,
    }
    if minutes and minutes >= 200:
        g90 = round(((goals or 0) * 90) / minutes, 3)
        a90 = round(((assists or 0) * 90) / minutes, 3)
        out["per90Goals"] = g90
        out["per90Assists"] = a90
        out["per90Prod"] = round(g90 + a90, 3)
        bonus = (goals or 0) * 3 + (assists or 0) * 1 + (pens or 0) * 0.5
        if role in ("P", "D") and gs is not None and pg:
            bonus += max(0, 8 - (gs / max(pg, 1)))
        out["bonusProxy"] = round(bonus, 1)
    elif fm is not None:
        out["bonusProxy"] = round(max(0.0, (fm - (mv or 6.0)) * 12), 1)
    return out


def fair_price(fvm: int, role: str, starter: int | None, fitness: int | None, prod: dict) -> dict:
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
    return {"fair": fair, "low": max(1, int(round(fair * 0.82))), "high": int(round(fair * 1.12))}


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
    minutes = est_minutes(pg, playeds_expected)
    prod = production_metrics(role, pg, fm, mv, goals, assists, pens, gs, minutes)
    band = fair_price(fvm, role, starter, fitness, prod)
    ctx = TEAM_CONTEXT.get(team, {"att": 3, "def": 3, "style": "n/d", "cs": "n/d"})
    parts: list[str] = []

    parts.append(f"Mercato: FVM {fvm}, fair ~{band['fair']} (banda {band['low']}–{band['high']}).")
    if fvm > band["high"]:
        parts.append("Listone sopra fair → rischio overpay.")
    elif fvm < band["low"]:
        parts.append("Listone sotto fair → possibile value.")

    if prod["per90Prod"] is not None:
        parts.append(
            f"Prod/90: {prod['per90Prod']} (G{prod['per90Goals']}/A{prod['per90Assists']}) su ~{minutes}'."
        )
    elif fm is not None:
        bits = [f"FM {fm}"]
        if mv is not None:
            bits.append(f"MV {mv}")
        if pg is not None:
            bits.append(f"PG {pg}")
        parts.append("Prev: " + ", ".join(bits) + ".")
    if goals is not None or assists is not None:
        g = goals or 0
        a = assists or 0
        p = pens or 0
        extra = f", rig {p}" if p else ""
        parts.append(f"Bonus raw 25/26: {g}G+{a}A{extra}.")

    parts.append(f"Contesto {team}: att{ctx['att']}/def{ctx['def']}, {ctx['style']}, CS {ctx['cs']}.")
    if role in ("P", "D"):
        parts.append("Mod: preferisci CS alto + voti stabili.")

    frag = FRAGILE.get(name)
    if fitness is not None:
        tip = ""
        if fitness < 45:
            tip = " Evita overpay / preferisci sconto."
        elif fitness < 55:
            tip = " Tetto stretto."
        parts.append(f"Durabilità: {fitness_lbl} ({fitness}/100).{tip}")
    elif frag and frag >= 3:
        parts.append("Storico fragilità: sconto obbligatorio.")

    if age is not None:
        parts.append(f"Età {age}.")
    if starter is not None:
        parts.append(f"Tit~{starter}%.")
    if playeds_expected is not None:
        parts.append(f"Playeds attesi {playeds_expected}.")

    parts.append(squad_fit_hint(role, tier, fvm))
    if role == "A" and tier in ("super_top", "S"):
        parts.append("Scenario: se rivali sparano >fair+15% → passa al piano B.")
    elif role == "D" and (tier in ("super_top", "S") or name == "Dimarco"):
        parts.append("Scenario: se >~220 a 6 → no-buy, prendi 2 fasce mid.")
    elif role == "C" and tier in ("super_top", "top", "S", "A"):
        parts.append("Scenario: alterna rigorista vs box-to-box in base a chi esce prima.")
    elif role == "P" and tier in ("super_top", "top", "S", "A"):
        parts.append("Scenario: 1 elite P o 2 medi — non entrambi costosi.")

    if penalty_label and penalty_label != "—":
        parts.append(f"Flag: {penalty_label}.")
    if flags:
        parts.append("Tag: " + ", ".join(flags[:4]) + ".")

    expert = EXPERT_NOTES.get(name)
    if expert:
        parts.append(expert)

    return " ".join(parts)
