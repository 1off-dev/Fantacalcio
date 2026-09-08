#!/usr/bin/env bash
# Deploy Fantacalcio realtime su www.1off.it/fantacalcio
set -euo pipefail

HOST="${DEPLOY_HOST:-217.154.125.55}"
USER="${DEPLOY_USER:-root}"
REMOTE_DIR="${REMOTE_DIR:-/var/www/fantacalcio}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

if [[ -z "${SSH_PASSWORD:-}" ]]; then
  echo "Imposta SSH_PASSWORD (password root del server)" >&2
  exit 1
fi

if ! command -v sshpass >/dev/null; then
  echo "Serve sshpass" >&2
  exit 1
fi

SSH=(sshpass -e ssh -o StrictHostKeyChecking=accept-new -o PreferredAuthentications=password -o PubkeyAuthentication=no)
SCP=(sshpass -e scp -o StrictHostKeyChecking=accept-new -o PreferredAuthentications=password -o PubkeyAuthentication=no)
export SSHPASS="$SSH_PASSWORD"

echo "==> Test SSH $USER@$HOST"
"${SSH[@]}" "$USER@$HOST" 'echo OK; uname -a; node -v || true'

echo "==> Prepara pacchetto"
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT
mkdir -p "$TMP/app"
rsync -a --delete \
  --exclude node_modules \
  --exclude .git \
  --exclude server/data \
  "$ROOT/public" "$ROOT/server" "$ROOT/package.json" "$TMP/app/"
# root package for convenience
cp "$ROOT/server/package.json" "$TMP/app/server/package.json"

# env file on server (password admin app = admin; root login server separate)
cat > "$TMP/app/server/.env.example" <<'EOF'
PORT=3847
BASE_PATH=/fantacalcio
ASTA_DB_PATH=/var/www/fantacalcio/server/data/asta.sqlite
ASTA_SEED_JSON=/var/www/fantacalcio/public/asta-live.json
ASTA_ADMIN_PASSWORD=admin
ASTA_ROOT_PASSWORD=admin
EOF

cat > "$TMP/app/server/fantacalcio.service" <<EOF
[Unit]
Description=Fantacalcio Asta realtime
After=network.target

[Service]
Type=simple
WorkingDirectory=$REMOTE_DIR/server
Environment=PORT=3847
Environment=BASE_PATH=/fantacalcio
Environment=ASTA_DB_PATH=$REMOTE_DIR/server/data/asta.sqlite
Environment=ASTA_SEED_JSON=$REMOTE_DIR/public/asta-live.json
Environment=ASTA_ADMIN_PASSWORD=admin
Environment=ASTA_ROOT_PASSWORD=admin
Environment=NODE_ENV=production
ExecStart=/usr/bin/node src/index.js
Restart=always
RestartSec=2
User=www-data
Group=www-data

[Install]
WantedBy=multi-user.target
EOF

cat > "$TMP/nginx-fantacalcio.conf" <<'EOF'
location /fantacalcio/ {
    proxy_pass http://127.0.0.1:3847/fantacalcio/;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_read_timeout 3600s;
    proxy_send_timeout 3600s;
    proxy_buffering off;
}
EOF

echo "==> Upload"
"${SSH[@]}" "$USER@$HOST" "mkdir -p '$REMOTE_DIR' /tmp/fantacalcio-upload"
"${SCP[@]}" -r "$TMP/app/." "$USER@$HOST:/tmp/fantacalcio-upload/"
"${SCP[@]}" "$TMP/nginx-fantacalcio.conf" "$USER@$HOST:/tmp/nginx-fantacalcio.conf"

echo "==> Install remoto"
"${SSH[@]}" "$USER@$HOST" bash -s <<REMOTE
set -euo pipefail
REMOTE_DIR='$REMOTE_DIR'
# Node.js se manca
if ! command -v node >/dev/null; then
  curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
  apt-get install -y nodejs build-essential python3
fi
apt-get install -y build-essential python3 >/dev/null 2>&1 || true
rsync -a --delete /tmp/fantacalcio-upload/ "\$REMOTE_DIR/"
mkdir -p "\$REMOTE_DIR/server/data"
cd "\$REMOTE_DIR/server"
npm install --omit=dev
# systemd
cp "\$REMOTE_DIR/server/fantacalcio.service" /etc/systemd/system/fantacalcio.service
# nginx snippet
if [[ -d /etc/nginx/sites-enabled ]]; then
  SITE=\$(ls /etc/nginx/sites-enabled | head -1)
  CONF="/etc/nginx/sites-available/\${SITE:-default}"
  [[ -f \$CONF ]] || CONF="/etc/nginx/nginx.conf"
  if ! grep -q 'location /fantacalcio/' /etc/nginx/sites-enabled/* 2>/dev/null; then
    # insert into first server block if possible via conf.d
    cp /tmp/nginx-fantacalcio.conf /etc/nginx/conf.d/fantacalcio-proxy.conf.bak 2>/dev/null || true
    mkdir -p /etc/nginx/snippets
    cp /tmp/nginx-fantacalcio.conf /etc/nginx/snippets/fantacalcio.conf
    echo "Aggiungi: include snippets/fantacalcio.conf; nel server block di www.1off.it"
  fi
fi
id www-data >/dev/null 2>&1 || useradd -r -s /usr/sbin/nologin www-data
chown -R www-data:www-data "\$REMOTE_DIR"
systemctl daemon-reload
systemctl enable fantacalcio
systemctl restart fantacalcio
systemctl --no-pager --full status fantacalcio | head -30
curl -sS http://127.0.0.1:3847/fantacalcio/api/health || true
REMOTE

echo "==> Fatto. Apri https://www.1off.it/fantacalcio/"
echo "    Se 404: includi snippets/fantacalcio.conf nel server nginx di www.1off.it e reload."
