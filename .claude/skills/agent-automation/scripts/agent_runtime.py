#!/usr/bin/env python3
"""
agent_runtime.py — a small, production-shaped runtime for autonomous Claude agents.

Encodes the skill's four parts: a validated trigger, a Tool Runner agent loop,
read/act tools with gating, and a reliability envelope (idempotency, retries,
timeout, structured JSON logs, kill switch, dry-run).

Anchored to the trading-bridge flow: a TradingView alert comes in, the agent
reads data (read tools), reasons, and finishes by calling submit_decision; a
gated act tool (Telegram) fires only when allowed. Ship with AGENT_DRY_RUN=1.

Requires: pip install anthropic   (auth via ANTHROPIC_API_KEY or `ant auth login`).

CLI:
    AGENT_DRY_RUN=1 python agent_runtime.py '{"symbol":"OANDA:XAUUSD","action":"buy","price":2350.5,"id":"a1"}'
"""

import os
import sys
import json
import time
import hashlib
import logging
import threading

try:
    from anthropic import Anthropic, beta_tool
except ImportError:
    sys.stderr.write("Missing dependency. Run: pip install anthropic\n")
    raise

# ----- config -------------------------------------------------------------
MODEL = os.environ.get("AGENT_MODEL", "claude-opus-4-8")
DRY_RUN = os.environ.get("AGENT_DRY_RUN", "1") == "1"        # default safe
KILL_SWITCH_FILE = os.environ.get("AGENT_KILL_FILE", "/tmp/agent.kill")
ALLOWED_SYMBOLS = set(
    os.environ.get("AGENT_ALLOWED_SYMBOLS", "OANDA:XAUUSD,BINANCE:BTCUSDT").split(","))
ALLOWED_ACTIONS = {"buy", "sell", "info"}
MAX_ITERATIONS = int(os.environ.get("AGENT_MAX_ITERS", "8"))
RUN_TIMEOUT_S = float(os.environ.get("AGENT_TIMEOUT_S", "90"))

_PROCESSED = set()          # idempotency store (swap for Redis/DB in production)
_LOCK = threading.Lock()

# ----- structured logging -------------------------------------------------
logger = logging.getLogger("agent")
if not logger.handlers:
    h = logging.StreamHandler()
    h.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(h)
    logger.setLevel(logging.INFO)


def jlog(event, **fields):
    """One structured line per step, always carrying event/run/idempotency ids."""
    logger.info(json.dumps({"event": event, **fields}, default=str))


def kill_switch_engaged():
    return os.path.exists(KILL_SWITCH_FILE)


class Reject(Exception):
    """Trigger failed validation — reject at the door, never reaches the agent."""


# ----- trigger validation (first, cheapest guardrail) ---------------------
def validate_alert(data: dict) -> dict:
    sym = data.get("symbol")
    if sym not in ALLOWED_SYMBOLS:
        raise Reject(f"symbol not allowed: {sym!r}")
    action = data.get("action")
    if action not in ALLOWED_ACTIONS:
        raise Reject(f"bad action: {action!r}")
    try:
        price = float(data["price"])
    except (KeyError, TypeError, ValueError):
        raise Reject("missing/invalid price")
    event_id = data.get("id") or hashlib.sha256(
        json.dumps(data, sort_keys=True).encode()).hexdigest()[:16]
    return {"symbol": sym, "action": action, "price": price, "id": event_id}


# ----- tools --------------------------------------------------------------
# Read tools run automatically. Act tools are gated. Context (run_id, event_id,
# dry_run, decision) is threaded via a thread-local so the @beta_tool functions
# stay simple while still enforcing policy.
_ctx = threading.local()


@beta_tool
def read_ohlc(symbol: str, timeframe: str) -> str:
    """Read the latest OHLC candle for a symbol at a timeframe.

    Call this to get current price data before judging a setup.
    Args:
        symbol: e.g. "OANDA:XAUUSD".
        timeframe: e.g. "240" for 4H, "1D" for daily.
    """
    # Stub: replace with a real feed, or drive the tradingview-browse-select
    # skill's tv_agent.py for exact reads from the chart.
    data = {"symbol": symbol, "timeframe": timeframe,
            "open": None, "high": None, "low": None, "close": None,
            "note": "stub — wire a real data source or read_chart() here"}
    jlog("tool_call", tool="read_ohlc", run=_ctx.run_id, id=_ctx.event_id,
         args={"symbol": symbol, "timeframe": timeframe}, ok=True)
    return json.dumps(data)


@beta_tool
def submit_decision(action: str, confidence: float, reason: str) -> str:
    """Record the agent's final decision. Call this exactly once to finish.

    Args:
        action: one of "long", "short", "no_trade", "alert_human".
        confidence: 0.0-1.0.
        reason: one or two sentences of justification.
    """
    _ctx.decision = {"action": action, "confidence": confidence, "reason": reason}
    jlog("decision", run=_ctx.run_id, id=_ctx.event_id, **_ctx.decision)
    return "decision recorded"


@beta_tool
def send_telegram(message: str) -> str:
    """Send a message to the operator's Telegram. ACT tool — gated.

    Call this to notify the human of the decision. Do not include secrets.
    """
    # ---- gate: kill switch -> idempotency -> dry-run ----
    if kill_switch_engaged():
        jlog("act_blocked", tool="send_telegram", run=_ctx.run_id,
             id=_ctx.event_id, reason="kill_switch")
        return "blocked: kill switch engaged"

    act_key = f"telegram:{_ctx.event_id}"
    with _LOCK:
        if act_key in _PROCESSED:
            jlog("act_skipped", tool="send_telegram", run=_ctx.run_id,
                 id=_ctx.event_id, reason="idempotent_replay")
            return "skipped: already sent for this event"

    if DRY_RUN:
        jlog("act_dryrun", tool="send_telegram", run=_ctx.run_id, id=_ctx.event_id,
             would_send=message[:200])
        return "dry-run: message not actually sent"

    ok = _telegram_post(message)
    if ok:
        with _LOCK:
            _PROCESSED.add(act_key)
    jlog("act", tool="send_telegram", run=_ctx.run_id, id=_ctx.event_id, ok=ok)
    return "sent" if ok else "send failed"


def _telegram_post(message: str) -> bool:
    """Real side effect, isolated so the tool stays about policy. Secrets stay here."""
    import requests
    token = os.environ.get("TELEGRAM_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not (token and chat_id):
        jlog("act_error", tool="send_telegram", reason="missing_telegram_env")
        return False
    for attempt in range(4):                       # retry transient failures only
        try:
            r = requests.post(f"https://api.telegram.org/bot{token}/sendMessage",
                              json={"chat_id": chat_id, "text": message}, timeout=10)
            if r.status_code < 400:
                return True
            if r.status_code < 500 and r.status_code != 429:
                return False                       # 4xx (not 429): don't retry
        except requests.RequestException:
            pass
        time.sleep(2 ** attempt)                    # 1,2,4,8s backoff
    return False


TOOLS = [read_ohlc, submit_decision, send_telegram]

SYSTEM = (
    "You are an automated trading-signal analyst agent. For each alert: read the "
    "data you need with the read tools, judge the setup briefly, then call "
    "submit_decision exactly once with action in "
    "{long, short, no_trade, alert_human}. After deciding, call send_telegram once "
    "with a short human-readable summary of your decision and why. Be concise. "
    "You are not authorized to place orders."
)


# ----- the run (reliability envelope) -------------------------------------
def run_alert(raw: dict) -> dict:
    """Validate -> dedupe -> agent loop (Tool Runner) -> gated act. Returns result."""
    alert = validate_alert(raw)                     # raises Reject on bad input
    run_id = hashlib.sha256(f"{alert['id']}:{time.time_ns()}".encode()).hexdigest()[:12]

    with _LOCK:
        if alert["id"] in _PROCESSED:
            jlog("skip_duplicate", run=run_id, id=alert["id"])
            return {"status": "duplicate", "id": alert["id"]}

    _ctx.run_id = run_id
    _ctx.event_id = alert["id"]
    _ctx.decision = None
    jlog("run_start", run=run_id, id=alert["id"], alert=alert, dry_run=DRY_RUN)

    client = Anthropic()
    prompt = (f"Alert: symbol={alert['symbol']} action={alert['action']} "
              f"price={alert['price']} id={alert['id']}. Assess it.")

    runner = client.beta.messages.tool_runner(
        model=MODEL,
        max_tokens=8000,
        thinking={"type": "adaptive"},
        system=SYSTEM,
        tools=TOOLS,
        messages=[{"role": "user", "content": prompt}],
    )

    deadline = time.time() + RUN_TIMEOUT_S
    iterations = 0
    for _message in runner:                          # runner drives tool execution
        iterations += 1
        if iterations >= MAX_ITERATIONS:
            jlog("run_capped", run=run_id, id=alert["id"], iterations=iterations)
            break
        if time.time() > deadline:
            jlog("run_timeout", run=run_id, id=alert["id"])
            break

    with _LOCK:
        _PROCESSED.add(alert["id"])
    result = {"status": "ok", "id": alert["id"], "run": run_id,
              "decision": _ctx.decision, "dry_run": DRY_RUN}
    jlog("run_end", **result)
    return result


# ----- CLI ----------------------------------------------------------------
def _main():
    if len(sys.argv) < 2:
        sys.stderr.write('usage: agent_runtime.py \'{"symbol":..,"action":..,"price":..}\'\n')
        sys.exit(2)
    try:
        payload = json.loads(sys.argv[1])
    except json.JSONDecodeError as e:
        sys.stderr.write(f"bad JSON payload: {e}\n")
        sys.exit(2)
    try:
        out = run_alert(payload)
    except Reject as e:
        jlog("rejected", reason=str(e))
        print(json.dumps({"status": "rejected", "reason": str(e)}))
        sys.exit(1)
    print(json.dumps(out, default=str))


if __name__ == "__main__":
    _main()
