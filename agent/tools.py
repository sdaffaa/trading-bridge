"""Agent tools — the only way the agent touches the world, so the safety boundary.

READ tools (safe, reversible) run automatically. ACT tools (side effects,
outward-facing) are gated: kill switch -> idempotency -> dry-run, and only then
perform the effect. Per-run context (ids, decision) is threaded via a
thread-local so each tool function stays simple while policy is enforced.
"""
import os
import sys
import json
import threading

from anthropic import beta_tool

from . import config, idempotency, marketdata, broker
from .logging_setup import jlog
from .notify import telegram_post

# Per-run context. Each alert runs in its own thread, so one context per thread.
ctx = threading.local()


def new_context(run_id: str, event_id: str, alert: dict) -> None:
    ctx.run_id = run_id
    ctx.event_id = event_id
    ctx.alert = alert
    ctx.decision = None


def kill_switch_engaged() -> bool:
    return os.path.exists(config.KILL_SWITCH_FILE)


# --------------------------------------------------------------------------
# READ TOOLS
# --------------------------------------------------------------------------
@beta_tool
def read_chart(symbol: str, timeframe: str) -> str:
    """Open the chart in TradingView and read exact OHLC + the bar's date.

    Call this when you need precise, current price data before judging a setup.
    Disabled unless AGENT_ENABLE_CHART_READS=1 (needs a browser + TradingView
    login). When disabled, judge from the alert fields instead.
    Args:
        symbol: e.g. "OANDA:XAUUSD".
        timeframe: e.g. "240" (4H), "1D".
    """
    if not config.ENABLE_CHART_READS:
        jlog("tool_call", tool="read_chart", run=ctx.run_id, id=ctx.event_id,
             ok=False, reason="disabled")
        return json.dumps({"error": "chart reads disabled; decide from the alert"})
    try:
        # Drives the tradingview-browse-select skill's tv_agent.py.
        skill_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            ".claude", "skills", "tradingview-browse-select", "scripts")
        if skill_dir not in sys.path:
            sys.path.insert(0, skill_dir)
        from tv_agent import TVAgent  # type: ignore
        with TVAgent(headless=True) as tv:
            tv.open_chart(symbol)
            tv.set_interval(timeframe)
            data = tv.read_ohlc()
        jlog("tool_call", tool="read_chart", run=ctx.run_id, id=ctx.event_id, ok=True)
        return json.dumps(data)
    except Exception as e:  # a tool failure must not crash the run
        jlog("tool_call", tool="read_chart", run=ctx.run_id, id=ctx.event_id,
             ok=False, error=str(e))
        return json.dumps({"error": f"chart read failed: {e}"})


@beta_tool
def read_price(symbol: str) -> str:
    """Fetch the current market price (and day range) for a symbol via a data feed.

    Prefer this for a fast, reliable quote. Returns an error field if no data
    provider is configured — in that case judge from the alert or escalate.
    Args:
        symbol: e.g. "OANDA:XAUUSD".
    """
    data = marketdata.get_quote(symbol)
    jlog("tool_call", tool="read_price", run=ctx.run_id, id=ctx.event_id,
         ok="error" not in data, source=data.get("source"))
    return json.dumps(data)


# --------------------------------------------------------------------------
# DECISION (terminal read tool)
# --------------------------------------------------------------------------
@beta_tool
def submit_decision(action: str, confidence: float, reason: str) -> str:
    """Record the final decision. Call this exactly once before notifying.

    Args:
        action: one of "long", "short", "no_trade", "alert_human".
        confidence: 0.0-1.0.
        reason: one or two sentences of justification.
    """
    ctx.decision = {"action": action, "confidence": confidence, "reason": reason}
    jlog("decision", run=ctx.run_id, id=ctx.event_id, **ctx.decision)
    return "decision recorded"


# --------------------------------------------------------------------------
# ACT TOOLS (gated)
# --------------------------------------------------------------------------
@beta_tool
def send_telegram(message: str) -> str:
    """Notify the operator via Telegram. ACT tool — gated. Include no secrets.

    Call this once, after submit_decision, with a short human-readable summary.
    """
    # gate order: kill switch -> idempotency -> dry-run -> effect
    if kill_switch_engaged():
        jlog("act_blocked", tool="send_telegram", run=ctx.run_id, id=ctx.event_id,
             reason="kill_switch")
        return "blocked: kill switch engaged"

    act_key = f"telegram:{ctx.event_id}"
    if idempotency.seen(act_key):
        jlog("act_skipped", tool="send_telegram", run=ctx.run_id, id=ctx.event_id,
             reason="idempotent_replay")
        return "skipped: already notified for this event"

    if config.DRY_RUN:
        jlog("act_dryrun", tool="send_telegram", run=ctx.run_id, id=ctx.event_id,
             would_send=message[:300])
        return "dry-run: message not actually sent"

    ok = telegram_post(message)
    if ok:
        idempotency.mark(act_key)
    jlog("act", tool="send_telegram", run=ctx.run_id, id=ctx.event_id, ok=ok)
    return "sent" if ok else "send failed (see logs)"


@beta_tool
def place_order(side: str) -> str:
    """Place a trade for the current alert's symbol. ACT tool — heavily gated.

    Only call this if execution is enabled and your confidence clears the
    minimum; otherwise notifying via send_telegram is the terminal action.
    Args:
        side: "long" or "short".
    """
    conf = (ctx.decision or {}).get("confidence", 0.0)
    symbol = (ctx.alert or {}).get("symbol", "")
    result = broker.place_order(symbol, side, conf, ctx.event_id)
    jlog("act", tool="place_order", run=ctx.run_id, id=ctx.event_id, **result)
    return json.dumps(result)


def build_toolset() -> list:
    """Assemble the agent's tools based on config.

    read_price and read_chart are always exposed (they self-describe when
    unavailable); place_order is added only when execution is enabled.
    """
    tools = [read_price, read_chart, submit_decision, send_telegram]
    if config.ENABLE_EXECUTION:
        tools.append(place_order)
    return tools
