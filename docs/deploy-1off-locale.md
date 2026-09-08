# Deploy 1off.it — Fantacalcio realtime

## Perché non dal Cloud Agent
Da Cursor Cloud la **porta 22 verso 217.154.125.55 è chiusa** (timeout).
Dal tuo PC SSH funziona: usa un **agente locale** (Cursor Desktop) o il terminale.

## Cosa c’è già nel repo
- `server/` — Node + SQLite (`better-sqlite3`) + WebSocket
- `scripts/deploy-1off.sh` — rsync + systemd + snippet nginx
- Target: **https://www.1off.it/fantacalcio/**

## Cosa deve fare l’agente locale
1. Apri il repo `Fantacalcio` in Cursor Desktop (branch `cursor/login-sola-lettura-2c1f` o quello aggiornato).
2. Completa il collegamento frontend → API/WS del server (sostituire sync GitHub/PeerJS con `./api` + `./ws` quando `/api/health` risponde).
3. Lancia il deploy:

```bash
export SSH_PASSWORD='…'   # password root del server (non committarla)
./scripts/deploy-1off.sh
```

4. Se nginx non ha ancora `location /fantacalcio/`, sul server:

```bash
# nel server block di www.1off.it
include snippets/fantacalcio.conf;
nginx -t && systemctl reload nginx
```

5. Verifica:
   - https://www.1off.it/fantacalcio/api/health
   - https://www.1off.it/fantacalcio/
   - Login admin / admin → modifica → altro browser in sola lettura vede subito

## Credenziali
- **SSH server:** root @ www.1off.it (password solo in env `SSH_PASSWORD`, mai in git)
- **App write:** `admin` / `admin` (o `root` se impostato `ASTA_ROOT_PASSWORD` sul servizio)
- **Sola lettura:** pulsante dedicato (niente scrittura sul DB)

## Prompt da dare all’agente locale
> Continua il deploy Fantacalcio su www.1off.it/fantacalcio.
> SSH dal mio PC funziona (root). Completa il wiring frontend al server SQLite+WebSocket in `server/`, poi esegui `SSH_PASSWORD=… ./scripts/deploy-1off.sh`, sistema nginx se serve, e verifica sync realtime tra due sessioni.
