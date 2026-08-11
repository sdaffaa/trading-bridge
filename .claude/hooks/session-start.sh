#!/bin/bash
# SessionStart hook — Claude Code on the web.
#
# The remote container is rebuilt for every session, so nothing installed by
# hand survives. This script is the durable form of "installed": it lives in
# the repo and re-creates the toolchain each time a session starts.
#
# Skip the optional Agent Reach step with:  AGENT_REACH=0
set -euo pipefail

# Local machines already have their own setup — only rebuild in the cloud.
[ "${CLAUDE_CODE_REMOTE:-}" = "true" ] || exit 0

PROJECT="${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "$0")/../.." && pwd)}"
cd "$PROJECT"

# Some distro-managed packages (blinker, for one) were installed by apt without
# a RECORD file, so pip cannot uninstall them to satisfy an upgrade and aborts.
# Falling back to --ignore-installed shadows them in site-packages instead of
# failing the whole session over a transitive dependency.
PIP_ARGS=(--quiet --disable-pip-version-check --root-user-action=ignore)
pipq() {
  # First attempt silenced: its failure is expected and handled. If the retry
  # also fails, that error is real and surfaces.
  python3 -m pip install "${PIP_ARGS[@]}" "$@" 2>/dev/null \
    || python3 -m pip install "${PIP_ARGS[@]}" --ignore-installed "$@"
}

echo "[session-start] project dependencies"
pipq -r requirements.txt

# Toolchain the brand/chart pipeline in assets/brand needs. Without these,
# every session re-installs them before it can render or check anything.
#   Pillow, numpy      — frame analysis and the chart accuracy checks
#   cairosvg           — SVG → PNG for the logo lockups
#   imageio-ffmpeg     — a full ffmpeg; the bundled Playwright build has no
#                        H.264/HEVC decoder and cannot read phone recordings
#   websocket-client   — CDP driver used by assets/brand/capture-motion.py
echo "[session-start] chart + video toolchain"
pipq Pillow numpy cairosvg imageio-ffmpeg websocket-client

# Optional: Agent Reach. Non-fatal — a failure here must never block a session.
# Installed into its own venv so it cannot disturb the project's dependencies.
if [ "${AGENT_REACH:-1}" = "1" ] && [ ! -x "$HOME/.agent-reach-venv/bin/agent-reach" ]; then
  echo "[session-start] Agent Reach (optional)"
  if ! {
    python3 -m venv "$HOME/.agent-reach-venv"
    tmp="$(mktemp -d)"
    # The published archive URL is blocked by the egress proxy; git reads work.
    GIT_LFS_SKIP_SMUDGE=1 git clone --depth 1 --quiet \
      https://github.com/panniantong/agent-reach "$tmp/agent-reach"
    "$HOME/.agent-reach-venv/bin/pip" install --quiet "$tmp/agent-reach"
    rm -rf "$tmp"
  } >/dev/null 2>&1; then
    echo "[session-start]   skipped — upstream or network unavailable"
  fi
fi

# Put agent-reach on PATH for the session when it is present.
if [ -x "$HOME/.agent-reach-venv/bin/agent-reach" ] && [ -n "${CLAUDE_ENV_FILE:-}" ]; then
  echo 'export PATH="$HOME/.agent-reach-venv/bin:$PATH"' >> "$CLAUDE_ENV_FILE"
fi

echo "[session-start] ready"
