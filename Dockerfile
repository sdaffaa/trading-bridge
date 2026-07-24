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

COPY . .

# Persist idempotency state across restarts (mount a volume at /data).
VOLUME ["/data"]
EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD python -c "import urllib.request,os;urllib.request.urlopen(f'http://127.0.0.1:{os.environ.get(\"PORT\",\"5000\")}/health').read()" || exit 1

# 1 worker, 8 threads: the loop is I/O-bound (model + Telegram), and background
# dispatch keeps requests non-blocking.
CMD ["sh", "-c", "gunicorn -w 1 --threads 8 -b 0.0.0.0:${PORT} --timeout 120 tv_claude_bridge:app"]
