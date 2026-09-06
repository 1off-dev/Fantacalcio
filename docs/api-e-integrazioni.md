# API, dati e formazioni settimanali

Stato al **6 settembre 2026**. Focus: cosa si può automatizzare senza violare termini / senza API ufficiali inesistenti.

---

## 1. Statistiche e voti — cosa esiste davvero

| Fonte | Tipo accesso | Utile per | Limiti |
|---|---|---|---|
| **Fantacalcio.it quotazioni** | Pagina web + export Excel (login per Excel) | QI/QA/FVM Classic & Mantra | Nessuna API pubblica documentata; lo scraper del repo legge l’HTML della tabella |
| **Fantacalcio.it voti/statistiche** | Sito / app | Pagelle giornata, bonus | No API pubblica; scraping fragile |
| **PyFanta** ([baldogiovine/PyFanta](https://github.com/baldogiovine/PyFanta)) | FastAPI wrapper di scrape | Match stats, summary outfield/GK | Non ufficiale, può rompersi |
| **Fantacalcio-Online** | Sito (prezzi asta, stats) | Prezzi reali aste, rigoristi, titolarità | Dati aggregati loro; non è un’API aperta per terzi |
| **Sofascore / FBref / Understat** | Web / API non ufficiali o rate-limit | xG, minuti, rating | Non mappati 1:1 ai bonus Fantacalcio |
| **API-Football / Sportmonks** | API commerciali | Eventi partita, lineup ufficiali | A pagamento; andrebbero mappati ai bonus FC |

### Cosa fa questo repo

- `scripts/fetch_listone.py` → aggiorna `data/listone-2026-27.json` e ricalcola `data/asta-board-2026-27.json` dalla pagina ufficiale quotazioni.
- Il tool asta usa FVM + fasce curate + cap per lega 6×1000.

**Raccomandazione pratica:** per l’asta usa listone ufficiale + guide aggiornate; per la stagione, Sofascore/FBref come supporto “minuti/xG”, e i voti dalla piattaforma della tua lega.

---

## 2. Connessione a Fantacalcio / Leghe per le formazioni

### Risposta breve

**Non esiste un’API pubblica ufficiale** di Fantacalcio.it / Leghe Fantacalcio per preparare e **attivare** (scrivere) le formazioni settimana per settimana.

### Cosa esiste in community (solo lettura / non ufficiale)

| Progetto | Capacità | Rischio |
|---|---|---|
| [dmarro89/fantacalcio-mcp](https://github.com/dmarro89/fantacalcio-mcp) | MCP read-only su `apileague.fantacalcio.it` (profilo, rosa, settings) | Endpoint interni, ToS, breaking change; **niente write formazioni** in v0.0.1 |
| pacchetto npm `leghe-fantacalcio` | Client verso API mobile legacy | Non ufficiale, manutenzione incerta |
| Export Excel calendario/rose dalla lega | Analisi offline | Manuale |

### Formazioni settimanali: percorso supportato

1. Preparare la formazione sull’**App Leghe Fantacalcio** / sito ufficiale.
2. Usare **probabili formazioni** Fantacalcio.it + ultime dai campi.
3. (Opzionale) Tool personale di *decisione* (chi schierare) basato su rosa exportata — **senza** auto-submit.

Automatizzare il submit della formazione via reverse engineering **non è consigliato**: viola tipicamente i termini, è instabile e può far sospendere l’account.

---

## 3. Integrazione futura (fuori scope asta)

Se dopo l’asta vorrai un assistente formazioni *locale*:

1. Export rosa post-asta (già previsto dal tool).
2. Lettura manuale / CSV dei convocati.
3. Suggerimento XI + panchina in CLI/web.
4. Copia-incolla sull’app ufficiale.

Nessuna dipendenza da API write non ufficiali.
