# Fantacalcio Asta 2026/27

Assistente per l'asta **Classic** (rosa 3-8-8-6, **1000 crediti**, **6 squadre**, **modificatore difesa**) + dossier strategia aggiornato.

## Cosa include

- [`docs/strategia-asta-2026-27.md`](docs/strategia-asta-2026-27.md) — dossier budget, fasce e tattica
- [`docs/api-e-integrazioni.md`](docs/api-e-integrazioni.md) — API stats / Leghe Fantacalcio (limiti reali)
- [`public/`](public/) — tool web per il giorno dell'asta (listone, cap, rosa, export JSON)
- [`scripts/fetch_listone.py`](scripts/fetch_listone.py) — aggiorna listone ufficiale da Fantacalcio.it

## Avvio rapido

```bash
npm run fetch   # aggiorna listone + board
npm start       # http://127.0.0.1:4173
```

Nel browser: scegli il piano budget, cerca i giocatori, segna **Compra** / **Preso**, esporta la rosa a fine asta.

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
