"""The agent runtime — validate -> dedupe -> Tool Runner loop -> gated act.

This is the reliability envelope around the agent loop: idempotency, a hard
timeout, an iteration cap, and structured logging. The webhook layer dispatches
run_alert in a background thread so the HTTP response returns fast.
"""
import time
import hashlib
import threading

from anthropic import Anthropic

from . import config, tools, budget, monitoring, store
from .validation import validate_alert, Reject  # re-exported for callers
from . import idempotency
from .logging_setup import jlog

__all__ = ["run_alert", "dispatch", "Reject"]

_client = None
_client_lock = threading.Lock()


def _system() -> str:
    lines = [
        "You are an automated trading-signal analyst agent inside a bridge that "
        "receives TradingView alerts. For each alert:",
        "1) Call read_price for a current quote (and read_chart if enabled) before "
        "judging; if data is unavailable, judge conservatively or escalate.",
        "2) Call submit_decision exactly once with action in "
        "{long, short, no_trade, alert_human}, a confidence 0-1, and a one-line reason.",
    ]
    if config.ENABLE_EXECUTION:
        lines.append(
            "3) If action is long/short and confidence is high, call place_order with "
            "that side (it is capped and gated). Then call send_telegram once with a "
            "short summary.")
    else:
        lines.append(
            "3) Then call send_telegram exactly once with a short human-readable "
            "summary of your decision and why. You are NOT authorized to place orders.")
    lines.append("Use action alert_human when a human should look; be concise and decisive.")
    return "\n".join(lines)


def _client_singleton() -> Anthropic:
    global _client
    with _client_lock:
        if _client is None:
            _client = Anthropic()      # auth from ANTHROPIC_API_KEY / ant profile
        return _client


def run_alert(raw: dict) -> dict:
    """Run one alert end-to-end. Raises Reject on invalid input."""
    alert = validate_alert(raw)                       # door guard
    run_id = hashlib.sha256(
        f"{alert['id']}:{time.time_ns()}".encode()).hexdigest()[:12]

    if idempotency.seen(f"run:{alert['id']}"):
        jlog("skip_duplicate", run=run_id, id=alert["id"])
        return {"status": "duplicate", "id": alert["id"], "run": run_id}

    allowed, why = budget.allow_run()                 # cost / rate control
    if not allowed:
        jlog("run_throttled", run=run_id, id=alert["id"], reason=why)
        return {"status": "throttled", "id": alert["id"], "run": run_id, "reason": why}

    tools.new_context(run_id, alert["id"], alert)
    jlog("run_start", run=run_id, id=alert["id"], alert=alert,
         dry_run=config.DRY_RUN, model=config.MODEL)

    prompt = (
        f"TradingView alert:\n"
        f"- symbol: {alert['symbol']}\n"
        f"- action: {alert['action']}\n"
        f"- price: {alert['price']}\n"
        f"- timeframe: {alert['timeframe']}\n"
        f"- note: {alert['note']}\n"
        f"- id: {alert['id']}\n\n"
        f"Assess this signal and follow your instructions."
    )

    try:
        runner = _client_singleton().beta.messages.tool_runner(
            model=config.MODEL,
            max_tokens=config.MAX_TOKENS,
            thinking={"type": "adaptive"},
            system=_system(),
            tools=tools.build_toolset(),
            messages=[{"role": "user", "content": prompt}],
        )
        deadline = time.time() + config.RUN_TIMEOUT_S
        iterations = 0
        for message in runner:
            iterations += 1
            _account_tokens(message)                   # daily budget accounting
            if iterations >= config.MAX_ITERATIONS:
                jlog("run_capped", run=run_id, id=alert["id"], iterations=iterations)
                break
            if time.time() > deadline:
                jlog("run_timeout", run=run_id, id=alert["id"])
                break
    except Exception as e:                             # never crash the worker
        jlog("run_error", run=run_id, id=alert["id"], error=str(e))
        monitoring.record_run(False, detail=str(e)[:200])
        return {"status": "error", "id": alert["id"], "run": run_id, "error": str(e)}

    idempotency.mark(f"run:{alert['id']}")
    decision = tools.ctx.decision
    store.record_decision(alert["id"], run_id, alert["symbol"], decision, config.DRY_RUN)
    monitoring.record_run(True)
    if decision and decision.get("action") == "alert_human":
        monitoring.alert_operator(
            f"🚨 escalation [{alert['symbol']}]: {decision.get('reason', '')}")
    result = {"status": "ok", "id": alert["id"], "run": run_id,
              "decision": decision, "dry_run": config.DRY_RUN}
    jlog("run_end", **result)
    return result


def _account_tokens(message) -> None:
    """Best-effort daily token accounting from the message usage."""
    try:
        u = getattr(message, "usage", None)
        if u is not None:
            budget.add_usage((getattr(u, "input_tokens", 0) or 0) +
                             (getattr(u, "output_tokens", 0) or 0))
    except Exception:
        pass


def dispatch(raw: dict) -> str:
    """Validate synchronously (so the webhook can reject fast), then run the
    agent in a background thread. Returns the event id it will process under.
    Raises Reject if the payload is invalid."""
    alert = validate_alert(raw)                        # fail fast for a 4xx
    t = threading.Thread(target=_safe_run, args=(raw,), daemon=True,
                         name=f"agent-{alert['id']}")
    t.start()
    return alert["id"]


def _safe_run(raw: dict) -> None:
    try:
        run_alert(raw)
    except Reject as e:                                # already validated; defensive
        jlog("rejected_in_worker", reason=str(e))
    except Exception as e:
        jlog("worker_crash", error=str(e))
