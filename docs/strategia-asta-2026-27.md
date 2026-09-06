# Dossier asta Fantacalcio 2026/27

**Aggiornato:** 6 settembre 2026 (post 2ª giornata, mercato chiuso)  
**Lega:** 6 squadre · Classic · rosa **3-8-8-6** · **1000 crediti** · asta aperta · **modificatore difesa**  
**Fonti:** [Quotazioni ufficiali Fantacalcio.it](https://www.fantacalcio.it/quotazioni-fantacalcio/2026-27), guide SOS Fanta / Goal / Fantacalcio-Online / Sportnews BetFlag (ago–set 2026)

Il listone del tool (`data/asta-board-2026-27.json`) è allineato alla pagina quotazioni Classic (QI / QA / FVM base 1000).

---

## 1. Contesto stagione

- Serie A 2026/27 già partita; molte aste arrivano **dopo** le prime due giornate.
- **Malen (Roma)** ha distorto i prezzi: exploit iniziale → FVM ufficiale **450**/1000.
- In lega a **6** con **1000** crediti l’inflazione sui top è massima.
- Con **modificatore difesa** i voti puri di P+D valgono punti di classifica; **Dimarco** resta un outlier (produzione da attaccante in slot difesa).

---

## 2. Budget consigliato (1000 crediti)

| Strategia | P | D | C | A | Quando |
|---|---:|---:|---:|---:|---|
| **Modificatore first** (consigliata) | 100 | 250 | 270 | 380 | Priorità P top + difesa da voto/bonus, senza inseguire Malen a ogni costo |
| Equilibrata + mod | 90 | 210 | 300 | 400 | 1 top C + attacco solido |
| Anti-Malen (2+2) | 85 | 200 | 315 | 400 | Malen > ~420–450: due punte + due semi |

**Regole:** piano A/B/C per reparto; non scendere sotto ~25–30 crediti prima degli ultimi slot; in asta aperta a 6 rispetta i **cap** del tool.

---

## 3. Fasce (nomi = listone ufficiale)

### Portieri

| Fascia | Nomi |
|---|---|
| Super top | **Svilar** |
| Top | Vicario, Martinez Jo., Carnesecchi, Maignan, Butez |
| Affidabili | Meret, Mandas, Skorupski, De Gea, Okoye, Perri, Falcone, Caprile |

Piani: Svilar (~90–100) + P2 provincia; oppure due medio-alti (es. Carnesecchi + Okoye/Falcone). Su Inter/Como/Napoli valuta pacchetto titolare+vice (`Sanchez Ro.` per Como).

### Difensori

| Fascia | Nomi |
|---|---|
| Super top | **Dimarco** (FVM 240) |
| Top bonus | Wesley, Molina N., Bremer, Pavlovic, Mancini, Solet |
| Modificatore | Akanji, Bastoni, Rrahmani, Kalulu, N'Dicka, Di Lorenzo |
| Value | Ostigard, Spence |

Meglio spesso **no-Dimarco** a 6: Wesley/Molina N. + centrali da voto. Dimarco solo se dopo l’acquisto restano ≥180 crediti difesa.

### Centrocampisti

| Fascia | Nomi |
|---|---|
| Super top | Paz N., Calhanoglu, McTominay |
| Top | Orsolini, Pulisic, Rabiot, De Bruyne, Baturina, Mora |
| Bonus | Da Cunha, Zaccagni, Barella, Zaniolo, Atta, Frattesi |

**1 super-top oppure 2 top**, non entrambi i pacchetti.

### Attaccanti

| Fascia | Nomi | Cap mentale |
|---|---|---|
| Super top | Malen, Martinez L. | Malen **max ~420–450**; Martinez L. **~360–400** |
| Top | Hojlund, Thuram, Ramos G., Douvikas, Kean, Kolo Muani, Woltemade | ~180–300 |
| Semi | Scamacca, Davis K., Berardi, Esposito F.P., Yildiz, Dybala | ~90–140 |

Strategie: star+depth **oppure** anti-Malen 2+2 (due top + due semi).

---

## 4. Tattica asta aperta a 6

1. Non aprire tu i super-top se puoi evitarlo.  
2. Àncora al **FVM**, non alla QA (Malen QA 38 vs FVM 450).  
3. Se a metà asta hai già speso >45% in A+C e la Difesa è vuota, sei fuori piano.  
4. Preferisci rigoristi anche in 3ª fascia.  
5. Chiudi con titolari da 1–5 crediti.

---

## 5. Checklist giorno asta

- [ ] Avvia il tool (`npm start`)
- [ ] Seleziona budget **Modificatore first** (o Anti-Malen)
- [ ] Segna i giocatori presi dagli altri
- [ ] Rispetta i cap; ricalcola residuo per slot
- [ ] Piano B se Malen > 450 o Dimarco > 250
- [ ] Esporta la rosa JSON e caricala su Leghe Fantacalcio

---

## 6. API e formazioni

Vedi [api-e-integrazioni.md](./api-e-integrazioni.md): **nessuna API ufficiale** per voti/formazioni write; il repo aggiorna il listone via scrape della pagina quotazioni; le formazioni restano sull’app ufficiale.
