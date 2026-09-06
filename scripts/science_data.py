"""Dati scientifici asta: fragilità, età note, pareri guida."""

from __future__ import annotations

# Penalità forma (punti 0–100 tolti al fitness) per storici infortuni / carico.
FRAGILE: dict[str, int] = {
    "Scamacca": 28,
    "Scalvini": 30,
    "Zaniolo": 22,
    "Leao": 14,
    "Dybala": 18,
    "Calhanoglu": 12,
    "Bremer": 16,
    "Bastoni": 8,
    "Thuram": 10,
    "Kolo Muani": 14,
    "Hojlund": 10,
    "Churchill": 0,
    "Gosens": 16,
    "Smolcic": 20,
    "Bellanova": 12,
    "Fruk": 10,
    "Retegui": 12,
    "Lookman": 10,
    "Koopmeiners": 10,
    "Tonali": 8,
    "Bove": 24,
    "Eriksen": 14,
    "Abraham": 20,
    "Immobile": 10,
    "Politano": 8,
    "Pasalic": 12,
    "Ruggeri": 14,
    "Buongiorno": 18,
    "Acerbi": 10,
    "Skriniar": 16,
    "Gatti": 14,
    "Danilo": 10,
    "Fagioli": 12,
    "Locatelli": 8,
    "Rabiot": 8,
    "Vlahovic": 14,
    "Chiesa": 26,
    "Kean": 8,
    "Laurientè": 10,
    "Berardi": 12,
    "Toloi": 18,
    "Djimsiti": 10,
    "De Roon": 6,
    "Zaccagni": 8,
    "Luis Alberto": 10,
    "Milinkovic-Savic S.": 8,
    "Raspadori": 10,
    "Osimhen": 16,
    "Kvaratskhelia": 12,
    "Ngonge": 14,
    "Colpani": 12,
    "Pulisic": 10,
    "Theo Hernandez": 12,
    "Tomori": 10,
    "Giroud": 8,
    "Jovic": 14,
    "Beltran": 10,
    "Nico Gonzalez": 12,
    "Mandragora": 10,
    "Biraghi": 8,
    "Martinez L.": 6,
    "Dimarco": 8,
    "Barella": 6,
    "Mkhitaryan": 10,
    "Darmian": 8,
    "Malen": 6,
    "Dybala": 18,
    "Cristante": 8,
    "Mancini": 8,
    "Ndicka": 6,
    "Svilar": 4,
    "Pellegrini Lo.": 12,
    "El Shaarawy": 10,
    "Dovbyk": 10,
    "Wesley": 8,
    "De Bruyne": 12,
    "McTominay": 6,
    "Paz N.": 6,
    "Orsolini": 6,
    "Ferguson": 22,
    "Zaniolo": 22,
}

# Età note (fallback se scrape fallisce) — età al 2026.
AGE_HINTS: dict[str, int] = {
    "Malen": 27,
    "Martinez L.": 28,
    "Dimarco": 28,
    "Paz N.": 21,
    "Calhanoglu": 32,
    "McTominay": 29,
    "Svilar": 26,
    "Thuram": 28,
    "Hojlund": 23,
    "Kean": 26,
    "Leao": 27,
    "Dybala": 32,
    "Scamacca": 27,
    "De Bruyne": 35,
    "Barella": 29,
    "Orsolini": 29,
    "Pulisic": 28,
    "Rabiot": 31,
    "Bremer": 29,
    "Bastoni": 27,
    "Maignan": 31,
    "Vicario": 29,
    "Carnesecchi": 25,
    "Butez": 29,
    "Yildiz": 21,
    "Douvikas": 27,
    "Ramos G.": 25,
    "Kolo Muani": 27,
    "Woltemade": 24,
    "Zaccagni": 31,
    "Frattesi": 26,
    "Samardzic": 24,
    "Baturina": 23,
    "Mora": 22,
    "Da Cunha": 23,
    "Wesley": 22,
    "Molina N.": 28,
    "Pavlovic": 24,
    "Solet": 25,
    "Akanji": 31,
    "Rrahmani": 32,
    "Kalulu": 26,
    "N'Dicka": 26,
    "Di Lorenzo": 32,
    "Berardi": 32,
    "Davis K.": 28,
    "Esposito F.P.": 21,
    "Laurientè": 29,
    "Simeone": 31,
    "Raspadori": 26,
    "Castro S.": 22,
    "Colombo": 24,
    "Zaniolo": 27,
    "Atta": 23,
    "Vlasic": 28,
    "McKennie": 27,
    "Conceicao": 23,
    "Kessie": 29,
    "Scalvini": 22,
    "Ostigard": 26,
    "Spence": 25,
    "Bisseck": 25,
    "Chalobah T.": 27,
    "Gila": 26,
}

# Pareri sintesi guide/articoli (SOS Fanta, Goal, FCO, Fantacalcio) — stagione 26/27.
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
    "Frattesi": "Inserimenti: upside se titolare; altrimenti lascia.",
    "Samardzic": "Creativo Atalanta: upside alto, rischio panchina.",
    "Baturina": "Talento C: guide lo spingono come breakout.",
    "Mora": "Young C da minuti; low-mid invest.",
    "Da Cunha": "Como: rigorista + tiri, profilo bonus.",
    "Scalvini": "Altissimo potenziale ma storico infortuni grave: evita o sconto max.",
    "Zaniolo": "Caos+infortuni: solo a prezzo di riserva.",
    "Berardi": "Sassuolo: rigorista classico, volume tiri.",
    "Davis K.": "Udinese: 1° rigore e punta centrale.",
    "Esposito F.P.": "Giovane Inter/prestito: upside, non certezza.",
    "Laurientè": "Sassuolo: contendente rigori/bonus.",
    "Castro S.": "Roma depth + 3° rigore: late target.",
    "Colombo": "Genoa: eredita rigori, profilo value A.",
    "Vicario": "P top dopo Svilar in molte mock a 6.",
    "Carnesecchi": "Atalanta: affidabile col mod, prezzo medio.",
    "Maignan": "Nome big ma concorrenza/vice: verifica gerarchia.",
    "Butez": "P titolare medio-alto: piano biporta.",
    "Akanji": "Mod Inter: voto puro, pochi bonus.",
    "Rrahmani": "Napoli mod: continuità > bonus.",
    "Kalulu": "Juve: value mod se titolare.",
    "N'Dicka": "Roma: titolare mod, profilo cemento.",
    "Di Lorenzo": "Terzino/mod ibrido Napoli.",
    "Pavlovic": "Milan: centrale top per voto+duelli.",
    "Solet": "Udinese: bonus da fisico + possibili rigori.",
    "Gila": "Value D emergente nelle guide lowcost.",
    "Spence": "Esterno value se conferma minuti.",
    "Bisseck": "Inter depth: upside se rotazioni.",
    "Atta": "Fiorentina: upside tiri/rigori secondari.",
    "Vlasic": "Torino: 1° rigore + tiri da fuori.",
    "McKennie": "Box-to-box Juve: voti, meno bonus puri.",
    "Conceicao": "Milan: upside panchina/titolare a tratti.",
    "Kessie": "Esperienza + inserimenti: mid C.",
    "Retegui": "Se presente listone: volume finalizzazioni.",
    "Lookman": "Bonus machine se sano e titolare.",
    "Koopmeiners": "Regia/rigori a tratti: dipende squadra.",
    "Chiesa": "Talent + vetro: solo a forte sconto.",
    "Vlahovic": "Alti/bassi + muscolari: tetto rigoroso.",
}


def fitness_label(score: int | None) -> str:
    if score is None:
        return "n/d"
    if score >= 80:
        return "Solido"
    if score >= 55:
        return "Normale"
    if score >= 35:
        return "Fragile"
    return "Vetro"


def compute_fitness(
    *,
    name: str,
    age: int | None,
    pg_prev: int | None,
    playeds_expected: int | None,
    prev_matches: int = 38,
) -> tuple[int, str]:
    """Fitness 0–100: disponibilità storica − fragilità − età."""
    if pg_prev is not None:
        score = min(100, round(100 * pg_prev / max(prev_matches - 4, 1)))
    elif playeds_expected is not None:
        score = int(playeds_expected)
    else:
        score = 58

    score -= FRAGILE.get(name, 0)

    if age is not None:
        if age >= 35:
            score -= 16
        elif age >= 33:
            score -= 10
        elif age >= 31:
            score -= 5
        elif age <= 18:
            score -= 6
        elif age <= 20:
            score -= 3

    score = max(0, min(100, int(score)))
    return score, fitness_label(score)
