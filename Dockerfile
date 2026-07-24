# trading-bridge — production image
FROM python:3.11-slim

# gunicorn serves Flask; the app dispatches agent runs on background threads,
# so a single worker with several threads fits the webhook-returns-fast design.
ENV PYTHONUNBUFFERED=1 \
    PORT=5000 \
    AGENT_DRY_RUN=1 \
    AGENT_STATE_DIR=/data/agent-state

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# DejaVu fonts so the on-chart markup labels (Entry/SL/TP + numbers) render crisply.
RUN apt-get update && apt-get install -y --no-install-recommends fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

# Vision mode opens the chart in a headless browser. Install Chromium + system
# deps. Set INSTALL_CHROMIUM=0 to skip (smaller image, no vision). Needs a 2GB+
# host to run Chromium.
ARG INSTALL_CHROMIUM=1
RUN if [ "$INSTALL_CHROMIUM" = "1" ]; then playwright install --with-deps chromium; fi
ENV PLAYWRIGHT_BROWSERS_PATH=/root/.cache/ms-playwright

COPY . .

# Persist idempotency state across restarts (mount a volume at /data).
VOLUME ["/data"]
EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD python -c "import urllib.request;urllib.request.urlopen('http://127.0.0.1:5000/health').read()" || exit 1

# Gunicorn always binds 5000 INSIDE the container; the host port is chosen by
# docker-compose (PORT in .env, e.g. 80 for TradingView). 1 worker, 8 threads:
# I/O-bound loop, background dispatch keeps requests non-blocking.
CMD ["sh", "-c", "gunicorn -w 1 --threads 8 -b 0.0.0.0:5000 --timeout 120 tv_claude_bridge:app"]
