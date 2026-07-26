#!/usr/bin/env bash
# deploy.sh — one-shot bootstrap for a fresh Ubuntu VPS (DigitalOcean, etc.).
# Installs Docker if needed, fetches the repo, prompts for secrets, writes .env
# (dry-run ON), opens the firewall, and starts the bridge with docker compose.
#
# Usage on the server (as root):
#   curl -fsSL https://raw.githubusercontent.com/sdaffaa/trading-bridge/claude/skillz-agents-browse-select-wopyc0/deploy.sh -o deploy.sh
#   bash deploy.sh
set -euo pipefail

REPO="https://github.com/sdaffaa/trading-bridge.git"
BRANCH="${BRIDGE_BRANCH:-claude/skillz-agents-browse-select-wopyc0}"
DIR="/opt/trading-bridge"
PORT="${PORT:-5000}"

say() { printf "\n\033[1;36m==> %s\033[0m\n" "$*"; }
ask() { local p="$1" v=""; read -r -p "$p" v < /dev/tty; printf '%s' "$v"; }
ask_secret() { local p="$1" v=""; read -r -s -p "$p" v < /dev/tty; echo >/dev/tty; printf '%s' "$v"; }

[ "$(id -u)" -eq 0 ] || { echo "Run as root (sudo bash deploy.sh)"; exit 1; }

# --- 1. Docker (with compose plugin) + git ---
apt-get update -y || true
apt-get install -y curl git ca-certificates || true
if ! command -v docker >/dev/null 2>&1; then
  say "Installing Docker via the official script (includes compose plugin)"
  curl -fsSL https://get.docker.com | sh
  systemctl enable --now docker
fi
# Ensure the compose plugin is present (Ubuntu's package is docker-compose-v2)
if ! docker compose version >/dev/null 2>&1; then
  apt-get install -y docker-compose-v2 || apt-get install -y docker-compose-plugin || true
fi
docker --version
docker compose version

# --- 2. Fetch the project ---
say "Fetching the project into $DIR"
if [ -d "$DIR/.git" ]; then
  git -C "$DIR" fetch origin "$BRANCH" && git -C "$DIR" checkout "$BRANCH" && git -C "$DIR" pull --ff-only origin "$BRANCH"
else
  git clone --branch "$BRANCH" "$REPO" "$DIR"
fi
cd "$DIR"

# --- 3. Secrets -> .env (only if not already present) ---
if [ -f .env ]; then
  say ".env already exists — keeping it (edit it manually to change secrets)"
else
  say "Enter your keys (input is hidden for secrets; paste and press Enter)"
  ANTHROPIC_API_KEY="$(ask_secret 'ANTHROPIC_API_KEY (sk-ant-...): ')"
  TELEGRAM_TOKEN="$(ask_secret 'TELEGRAM_TOKEN: ')"
  TELEGRAM_CHAT_ID="$(ask 'TELEGRAM_CHAT_ID: ')"
  WEBHOOK_SECRET="$(ask 'WEBHOOK_SECRET (leave empty to auto-generate): ')"
  [ -n "$WEBHOOK_SECRET" ] || WEBHOOK_SECRET="$(head -c18 /dev/urandom | base64 | tr -d '/+=' | head -c24)"

  cp .env.example .env
  # fill values safely with python (handles special chars, no sed escaping issues)
  ANTHROPIC_API_KEY="$ANTHROPIC_API_KEY" TELEGRAM_TOKEN="$TELEGRAM_TOKEN" \
  TELEGRAM_CHAT_ID="$TELEGRAM_CHAT_ID" WEBHOOK_SECRET="$WEBHOOK_SECRET" \
  python3 - <<'PY'
import os, re
keys = ["ANTHROPIC_API_KEY","TELEGRAM_TOKEN","TELEGRAM_CHAT_ID","WEBHOOK_SECRET"]
txt = open(".env").read().splitlines()
have = {k: os.environ[k] for k in keys}
out = []
seen = set()
for line in txt:
    m = re.match(r'^(\w+)=', line)
    if m and m.group(1) in have:
        out.append(f"{m.group(1)}={have[m.group(1)]}"); seen.add(m.group(1))
    else:
        out.append(line)
for k in keys:
    if k not in seen:
        out.append(f"{k}={have[k]}")
open(".env","w").write("\n".join(out) + "\n")
print("wrote .env (AGENT_DRY_RUN stays 1 — safe)")
PY
  chmod 600 .env
fi

# --- 4. Firewall ---
if command -v ufw >/dev/null 2>&1; then
  say "Opening firewall ports 22 and $PORT"
  ufw allow 22/tcp || true
  ufw allow "${PORT}/tcp" || true
  yes | ufw enable || true
fi

# --- 5. Launch ---
say "Building and starting the bridge"
PORT="$PORT" docker compose up -d --build

sleep 5
say "Health check"
curl -fsS "http://localhost:${PORT}/health" && echo || echo "(health not ready yet; check: docker compose logs -f)"

IP="$(curl -fsS https://api.ipify.org 2>/dev/null || echo YOUR_SERVER_IP)"
cat <<DONE

============================================================
 trading-bridge is running (DRY-RUN — nothing is sent yet).
 Webhook URL:  http://${IP}:${PORT}/webhook
 Health:       http://${IP}:${PORT}/health
 Status:       http://${IP}:${PORT}/status

 Test it:
   curl -XPOST http://localhost:${PORT}/webhook \\
     -H "X-Webhook-Secret: <your WEBHOOK_SECRET>" \\
     -H "Content-Type: application/json" \\
     -d '{"symbol":"OANDA:XAUUSD","action":"buy","price":2350.5,"timeframe":"240"}'

 Watch logs:   cd $DIR && docker compose logs -f
 Go live later: edit $DIR/.env -> AGENT_DRY_RUN=0 -> docker compose up -d
============================================================
DONE
