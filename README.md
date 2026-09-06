# Fantacalcio Asta 2026/27

Assistente per l'asta **Classic** (rosa 3-8-8-6, **1000 crediti**, **6 squadre**, **modificatore difesa**) + dossier strategia aggiornato.

## Cosa include

- [`docs/strategia-asta-2026-27.md`](docs/strategia-asta-2026-27.md) — dossier budget, fasce e tattica
- [`docs/api-e-integrazioni.md`](docs/api-e-integrazioni.md) — API stats / Leghe Fantacalcio (limiti reali)
- [`public/`](public/) — tool web per il giorno dell'asta (listone, cap, rosa, export JSON)
- [`scripts/fetch_listone.py`](scripts/fetch_listone.py) — aggiorna listone ufficiale da Fantacalcio.it

## Avvio rapido (PC)

```bash
npm run fetch   # aggiorna listone + board
npm start       # http://127.0.0.1:4173
```

Nel browser: l’asta è **a ruoli** (P→D→C→A). Segui la fase, usa la colonna **Pri** (si aggiorna a ogni Compra/Preso), controlla **Forma** ed **Età**, segna acquisti e giocatori presi, poi esporta la rosa.

## iPhone / GitHub Pages

URL: **https://1off-dev.github.io/Fantacalcio/**

Il sito è già sul branch `gh-pages`, ma GitHub richiede **un click tuo** per attivarlo (il token dell’agent non può creare il sito Pages):

1. Apri: https://github.com/1off-dev/Fantacalcio/settings/pages  
2. **Build and deployment → Source**: scegli **Deploy from a branch**  
3. Branch: **`gh-pages`** / folder: **`/` (root)** → **Save**  
4. Aspetta 1–2 minuti, poi apri il link su Safari iPhone  
5. Opzionale: Condividi → **Aggiungi a Schermata Home**

Se vedi ancora 404, attendi la pubblicazione (Settings → Pages mostra lo stato) e fai hard refresh.

## Configurazione lega

| Voce | Valore |
|------|--------|
| Modalità | Classic |
| Squadre | 6 |
| Budget | 1000 |
| Rosa | 3P / 8D / 8C / 6A |
| Modificatore | Difesa |
| Asta | Aperta |

## Note API

Non esiste un'API pubblica ufficiale Fantacalcio.it per voti o per **scrivere** le formazioni settimanali. Dettagli in `docs/api-e-integrazioni.md`.
