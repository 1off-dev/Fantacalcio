# Dossier asta Fantacalcio 2026/27 — metodo a ruoli

**Aggiornato:** 7 settembre 2026  
**Lega:** 6 squadre · Classic · rosa **3-8-8-6** · **500 crediti** · **modificatore difesa**  
**Formato asta:** chiamata **per ruolo** (P → D → C → A). Si resta su un ruolo finché tutte le rose hanno chiuso quegli slot.

Il tool (`public/`) calcola live **Pri** (con fit rosa), **Tit%**, **Forma**, **Età**, FM 25/26, **fair/mock/leave**, semaforo overpay, prod/90, **scenari A/B/C** e note scientifiche per ogni giocatore. I prezzi (FVM asta / fair / leave) sono **riscalati ×0.5** rispetto al listone Fantacalcio pensato su scala ~1000.

**Freschezza dati:** il board parte dal listone ufficiale Fantacalcio.it, che a volte resta indietro sul calciomercato. Override curati in `OUT_OF_SERIE_A` / `TEAM_OVERRIDES` (es. Di Gregorio→Bournemouth escluso). Aggiorna con `npm run fetch`.

### Tracking 6 squadre (live)
1. Rinomina le 6 squadre nella barra (la tua + 5 rivali).
2. **Compra** = assegna a te + prezzo; **Preso** = assegna a un rivale + prezzo.
3. Residui/slot per squadra aggiornano **Pri**, gli **scenari A/B/C** e la **strategia live**:
   - rivali “affamati” (budget alto + slot aperti) → alza aggressività sui titolari certi;
   - top già usciti → sposta Pri su semi/value;
   - leave/semaforo overpay → non inseguire;
   - inflazione ruolo / warchest residuo → protegge i ruoli successivi.

---

## 1. Perché l’asta a ruoli cambia tutto

In asta aperta “mista” puoi bilanciare P/D mentre gli altri bruciano crediti in A.  
In asta **a ruoli**:

1. Il mercato di un ruolo si **svuota prima** (es. 18 portieri in 6×3).
2. I top del ruolo corrente gonfiano subito; i value spariscono se resti passivo.
3. Il budget residuo degli altri ruoli è **bloccato**: non puoi “recuperare dopo” comprando un P low-cost mentre gli altri prendono Malen.

**Regola madre:** ogni ruolo ha un budget piano e uno **spend-safe** = residuo ruolo − 1 credito × slot ancora vuoti.

---

## 2. Budget consigliato (invariato, ma vincolato al ruolo)

| Strategia | P | D | C | A | Uso |
|---|---:|---:|---:|---:|---|
| **Modificatore first** | 50 | 125 | 135 | 190 | Default scientifici + mod |
| Equilibrata + mod | 45 | 105 | 150 | 200 | Più peso C |
| Anti-Malen 2+2 | 40 | 100 | 160 | 200 | Se Malen > 210–230 |
| **Malen first** | 40 | 90 | 110 | 260 | Warchest A per prendere Malen |

### Piano Malen first (dettaglio)
Obiettivo: chiudere **Malen** nella fascia mock **~215**, con tetto soft **leave 230** e **hard stop 245** (sotto cap 252).

1. **P (≤40):** niente big gonfi; 1 titolare mid + 2 filler.
2. **D (≤90):** solo cementi da modificatore; **niente Dimarco/Wesley elite**.
3. **C (≤110):** niente Paz/Calha/McT; al massimo 1 bonus mid (Orsolini/Zaccagni) + volume.
4. **A (260):** apri aggressivo su Malen. Se lo prendi ≤230 restano ~30 per 1 mid-low + filler a 1. Se supera 245 → abort e **2+2** col residuo (come Anti-Malen).

Durante la fase P spendi solo il budget P (salvo aggiustamenti manuali). Il motore Pri penalizza chi sforerebbe lo spend-safe.

---

## 3. Playbook per fase

### Portieri
- Target: 1 **cemento** (Tit% alto + Forma Solido/Normale) + 1/2 titolari provincia.
- Non overpayare il secondo big se il primo è già uscito caro.
- Evita gerarchie incerte (flag “verificare_gerarchia”).

### Difensori
- Prima i **voti mod** (centrali affidabili), poi 1 esterno bonus se resta spend-safe.
- Dimarco solo se dopo restano ≥90 sul budget D.
- Forma Fragile/Vetro sui centrali = sconto obbligatorio.

### Centrocampisti
- Max **uno** tra Paz N. / Calhanoglu / McTominay.
- Poi rigoristi/bonus con Forma ≥55.
- Se i top scappano, non inseguire: ruota su Orsolini / Zaccagni / Da Cunha value.

### Attaccanti
- Piano **Malen first**: warchest A 260, target 215 / leave 230 / hard stop 245.
- Se Malen > cap sul piano standard, attiva **2+2** (Anti-Malen).
- Ranking scientifico: FM × Tit% × Forma / prezzo, non il nome.
- Scamacca/Dybala/Chiesa: solo a forte sconto (Vetro).

---

## 4. Metriche del tool (asta scientifica)

| Metrica | Formula / fonte | Uso |
|---|---|---|
| **Tit%** | 70% playeds listone + 30% PG/38 del 25/26 | Continuità schieramento |
| **Forma** | Disponibilità PG − fragilità curata − età | Chi si rompe gioca poco |
| **Età** | Profili Fantacalcio (+ hint) | Declino / upside young |
| **FM 25/26** | Statistiche Fantacalcio | Produzione reale |
| **Pri** | Mix Tit%+Forma+FM+fascia+rigori+fabbisogno slot/budget | Ordine d’acquisto live |
| **Note** | Guide SOS/Goal/FCO + regole repo | Contesto asta |

La **Pri si aggiorna** a ogni Compra/Preso: top usciti, slot rimasti, budget ruolo, scarcity di mercato.

---

## 5. Checklist giorno asta

- [ ] Apri il tool, piano **Modificatore first**
- [ ] Lascia attivo **Solo ruolo di fase**
- [ ] Segna **Preso** su ogni assegnazione altrui
- [ ] Segui la colonna **Pri** / pannello Priorità
- [ ] Quando i tuoi slot del ruolo sono pieni → **Ruolo fatto → avanza**
- [ ] Esporta JSON a fine asta

---

## 6. API / dati

Vedi [api-e-integrazioni.md](./api-e-integrazioni.md). Aggiorna listone/età/stats con `npm run fetch`.
