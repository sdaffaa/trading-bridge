"""trading-bridge — TradingView → autonomous Claude agent → Telegram.

The webhook validates the alert, dedupes it, and dispatches the agent run in a
background thread so it returns fast (never blocks, never sleep-polls). The agent
(agent/) reasons with tools, decides, and notifies via gated act tools.

Run:
    python tv_claude_bridge.py            # Flask server on $PORT (default 5000)
    python tv_claude_bridge.py --once '{"symbol":"OANDA:XAUUSD","action":"buy","price":2350.5}'

Endpoints:
    POST /webhook   TradingView alert intake (JSON)
    GET  /health    liveness
    GET  /status    non-secret config summary
"""
import sys
import json
import hmac

from flask import Flask, request, jsonify

from agent import config, scheduler, monitoring, store, budget
from agent.runtime import dispatch, run_alert, Reject
from agent.logging_setup import jlog

app = Flask(__name__)

# Start background workers at import time so they run under gunicorn too
# (no __main__). Each is a no-op unless configured; all idempotent.
scheduler.start_if_enabled()
monitoring.start_watchdog_if_enabled()


def _authorized(req) -> bool:
    """Optional shared-secret check. If WEBHOOK_SECRET is unset, allow (dev only)."""
    if not config.WEBHOOK_SECRET:
        return True
    supplied = req.headers.get("X-Webhook-Secret", "") or req.args.get("secret", "")
    return hmac.compare_digest(supplied, config.WEBHOOK_SECRET)


@app.route("/webhook", methods=["POST"])
def webhook():
    if not _authorized(request):
        jlog("webhook_unauthorized")
        return jsonify({"status": "unauthorized"}), 401

    # TradingView can send JSON or a raw text body; accept both.
    data = request.get_json(silent=True)
    if data is None:
        try:
            data = json.loads(request.get_data(as_text=True) or "{}")
        except json.JSONDecodeError:
            return jsonify({"status": "bad_request", "reason": "invalid JSON"}), 400

    try:
        event_id = dispatch(data)                 # validates, then runs in background
    except Reject as e:
        jlog("webhook_rejected", reason=str(e))
        return jsonify({"status": "rejected", "reason": str(e)}), 400

    # Return fast — the agent runs asynchronously.
    return jsonify({"status": "accepted", "id": event_id}), 202


@app.route("/health", methods=["GET"])
def health():
    h = monitoring.health()
    h["budget"] = budget.remaining()
    return jsonify(h), 200


@app.route("/status", methods=["GET"])
def status():
    return jsonify(config.summary()), 200


@app.route("/stats", methods=["GET"])
def stats():
    """Decision counts, accuracy, and P&L (the feedback loop)."""
    out = store.stats()
    out["recent"] = store.recent_decisions(limit=10)
    return jsonify(out), 200


@app.route("/outcome", methods=["POST"])
def outcome():
    """Record the outcome of a past decision: {id, outcome, pnl?}.

    outcome is "win" | "loss" | "flat" (or any label); pnl is optional numeric.
    """
    if not _authorized(request):
        return jsonify({"status": "unauthorized"}), 401
    data = request.get_json(silent=True) or {}
    event_id = data.get("id")
    result = str(data.get("outcome", "")).strip()
    if not event_id or not result:
        return jsonify({"status": "bad_request", "reason": "need id and outcome"}), 400
    pnl = data.get("pnl")
    try:
        pnl = float(pnl) if pnl is not None else None
    except (TypeError, ValueError):
        return jsonify({"status": "bad_request", "reason": "pnl must be numeric"}), 400
    ok = store.record_outcome(event_id, result, pnl)
    if not ok:
        return jsonify({"status": "not_found", "id": event_id}), 404
    jlog("outcome_recorded", id=event_id, outcome=result, pnl=pnl)
    return jsonify({"status": "ok", "id": event_id}), 200


def _run_once(payload_str: str) -> int:
    try:
        payload = json.loads(payload_str)
    except json.JSONDecodeError as e:
        sys.stderr.write(f"bad JSON: {e}\n")
        return 2
    try:
        out = run_alert(payload)                   # synchronous, for testing
    except Reject as e:
        print(json.dumps({"status": "rejected", "reason": str(e)}))
        return 1
    print(json.dumps(out, default=str, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "--once":
        if len(sys.argv) < 3:
            sys.stderr.write('usage: --once \'{"symbol":..,"action":..,"price":..}\'\n')
            sys.exit(2)
        sys.exit(_run_once(sys.argv[2]))

    jlog("startup", **config.summary())
    app.run(host=config.HOST, port=config.PORT)
