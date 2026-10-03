#!/usr/bin/env bash
# start.sh — bring the bridge up on a plain host (no Docker).
# Creates a venv, installs deps, runs preflight checks, then starts the server.
set -euo pipefail
cd "$(dirname "$0")"

PYTHON="${PYTHON:-python3}"
VENV=".venv"

# --- venv + deps ---
if [ ! -d "$VENV" ]; then
  echo "==> creating virtualenv"
  "$PYTHON" -m venv "$VENV"
fi
# shellcheck disable=SC1091
source "$VENV/bin/activate"
echo "==> installing dependencies"
pip install -q -r requirements.txt gunicorn

# --- env / preflight ---
if [ -f .env ]; then
  set -a; # shellcheck disable=SC1091
  . ./.env; set +a
fi

if [ -z "${ANTHROPIC_API_KEY:-}" ]; then
  echo "!! ANTHROPIC_API_KEY is not set — the agent's model call will fail."
  echo "   Set it in .env (or run 'ant auth login')."
fi
if [ "${AGENT_DRY_RUN:-1}" = "1" ]; then
  echo "-- DRY-RUN is ON: decisions are logged, Telegram is NOT sent."
  echo "   Set AGENT_DRY_RUN=0 in .env to go live (after watching some runs)."
fi
if [ "${AGENT_SCHEDULE_SECONDS:-0}" -gt 0 ] 2>/dev/null; then
  echo "-- SCHEDULER ON: the system will analyze every ${AGENT_SCHEDULE_SECONDS}s on its own."
fi

PORT="${PORT:-5000}"
echo "==> starting on 0.0.0.0:${PORT}  (POST /webhook, GET /health, GET /status)"
exec gunicorn -w 1 --threads 8 -b "0.0.0.0:${PORT}" --timeout 120 tv_claude_bridge:app
