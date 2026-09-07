# Dossier asta Fantacalcio 2026/27 — metodo a ruoli

**Aggiornato:** 7 settembre 2026  
**Lega:** 6 squadre · Classic · rosa **3-8-8-6** · **1000 crediti** · **modificatore difesa**  
**Formato asta:** chiamata **per ruolo** (P → D → C → A). Si resta su un ruolo finché tutte le rose hanno chiuso quegli slot.

Il tool (`public/`) calcola live **Pri** (con fit rosa), **Tit%**, **Forma**, **Età**, FM 25/26, **fair/mock/leave**, semaforo overpay, prod/90, **scenari A/B/C** e note scientifiche per ogni giocatore.

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
| **Modificatore first** | 100 | 250 | 270 | 380 | Default scientifici + mod |
| Equilibrata + mod | 90 | 210 | 300 | 400 | Più peso C |
| Anti-Malen 2+2 | 85 | 200 | 315 | 400 | Se Malen > 420–450 |

Durante la fase P spendi solo il budget P (salvo aggiustamenti manuali). Il motore Pri penalizza chi sforerebbe lo spend-safe.

---

## 3. Playbook per fase

### Portieri
- Target: 1 **cemento** (Tit% alto + Forma Solido/Normale) + 1/2 titolari provincia.
- Non overpayare il secondo big se il primo è già uscito caro.
- Evita gerarchie incerte (flag “verificare_gerarchia”).

### Difensori
- Prima i **voti mod** (centrali affidabili), poi 1 esterno bonus se resta spend-safe.
- Dimarco solo se dopo restano ≥180 sul budget D.
- Forma Fragile/Vetro sui centrali = sconto obbligatorio.

### Centrocampisti
- Max **uno** tra Paz N. / Calhanoglu / McTominay.
- Poi rigoristi/bonus con Forma ≥55.
- Se i top scappano, non inseguire: ruota su Orsolini / Zaccagni / Da Cunha value.

### Attaccanti
- Se Malen > cap, attiva **2+2**.
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
