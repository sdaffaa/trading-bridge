# trading-bridge

An **autonomous agent pipeline**: a TradingView alert comes in over a webhook, a
Claude agent reasons over it with tools, decides, and notifies via Telegram —
without a human in the loop for each step, and safe to leave running.

```
TradingView alert ──POST /webhook──▶ validate ▶ dedupe ▶ [background] agent loop
                                                                 │
                             read tools (chart/OHLC) ◀───────────┤
                                                                 ▼
                                              submit_decision ▶ send_telegram (gated)
```

The webhook validates and dedupes the alert, then dispatches the agent run on a
background thread and returns `202` immediately — it never blocks or polls. The
agent (in `agent/`) runs a Tool Runner loop, calls `submit_decision`, and then a
**gated** `send_telegram` act tool. Every step emits a structured JSON log line
keyed by run and event id.

## Architecture

| Module | Responsibility |
|---|---|
| `tv_claude_bridge.py` | Flask entry: `/webhook`, `/health`, `/status`, and a `--once` CLI |
| `agent/config.py` | All settings from env; safe defaults (dry-run on) |
| `agent/validation.py` | Reject malformed/out-of-policy alerts at the door; derive idempotency id |
| `agent/idempotency.py` | File-backed dedupe so replays/restarts don't double-fire |
| `agent/tools.py` | Agent tools — **the safety boundary**: read (auto) vs act (gated) |
| `agent/runtime.py` | The agent loop + reliability envelope (timeout, iteration cap, logging) |
| `agent/notify.py` | Telegram side effect, isolated; secrets stay here |
| `agent/logging_setup.py` | Structured JSON logging |

Design guidance for extending it lives in the skills under
`.claude/skills/` (`agent-automation`, `tradingview-browse-select`).

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env        # fill in credentials; keep AGENT_DRY_RUN=1 at first
```

Auth: set `ANTHROPIC_API_KEY`, or run `ant auth login` and leave it blank.

## Run

```bash
# Test a single alert synchronously (dry-run: no real Telegram send)
AGENT_DRY_RUN=1 python tv_claude_bridge.py --once \
  '{"symbol":"OANDA:XAUUSD","action":"buy","price":2350.5,"timeframe":"240"}'

# Start the webhook server
python tv_claude_bridge.py
```

Point a TradingView alert at `http://<host>:5000/webhook` with a JSON body:

```json
{"symbol": "OANDA:XAUUSD", "action": "buy", "price": {{close}}, "timeframe": "240"}
```

## Safety model

The agent only touches the world through **tools**, so the tool surface is the
policy. Read tools run automatically; **act tools are gated** and check, in order:

1. **Kill switch** — `touch /tmp/agent.kill` halts all acting instantly, mid-run.
2. **Idempotency** — the same alert notifies at most once (persisted to disk).
3. **Dry-run** — `AGENT_DRY_RUN=1` (default) logs *would-have* acts without doing them.

Trigger validation (`AGENT_ALLOWED_SYMBOLS`, `AGENT_ALLOWED_ACTIONS`) rejects
out-of-policy alerts before the agent ever sees them, and secrets live only in
env / the notify module — never in the model's context.

**Go live deliberately:** watch several dry-run runs in the logs, confirm the
decisions and would-have sends look right, then set `AGENT_DRY_RUN=0`.

## Getting it running

One command, then it runs on its own:

```bash
cp .env.example .env         # fill ANTHROPIC_API_KEY + Telegram; keep AGENT_DRY_RUN=1 at first
docker compose up -d         # or: ./start.sh   (venv + gunicorn, no Docker)
```

**How analysis starts without you.** The agent begins on an *event*, not a
command. Two ways:

- **Webhook (reactive).** Point a TradingView alert at `https://<host>/webhook`
  with a JSON message like
  `{"symbol":"OANDA:XAUUSD","action":"buy","price":{{close}},"timeframe":"{{interval}}"}`.
  When the market condition fires, TradingView calls the webhook and the agent
  runs — hands-off.
- **Scheduler (autonomous).** Set `AGENT_SCHEDULE_SECONDS` > 0 and the system
  analyzes the configured symbols on that interval by itself — no webhook, no
  command:

  ```bash
  AGENT_SCHEDULE_SECONDS=3600 AGENT_SCHEDULE_SYMBOLS=OANDA:XAUUSD AGENT_SCHEDULE_TIMEFRAME=240
  ```

Both run through the same validated, deduped, gated pipeline. `GET /status`
reflects the live config (including the schedule).

## Tests

No network or API key needed — the Claude call is stubbed:

```bash
pip install -r requirements-dev.txt
pytest
```

CI runs the same suite on every push/PR (`.github/workflows/ci.yml`).

## Deployment

**Docker** (persists idempotency state in a volume):

```bash
docker build -t trading-bridge .
docker run -p 5000:5000 --env-file .env -v tb-data:/data trading-bridge
```

**systemd** (non-Docker): see `deploy/trading-bridge.service` — copy it to
`/etc/systemd/system/`, point `EnvironmentFile` at a root-only `.env`, and
`systemctl enable --now trading-bridge`.

Both run under gunicorn with one worker and several threads — the request handler
returns fast and the agent runs on a background thread, so a single worker fits.

## Notes

- This bridge **notifies**; it does not place orders. Auto-execution is out of
  scope by default and would need capped, idempotent order tools you enable
  deliberately (see the `agent-automation` skill).
- Not financial advice.
