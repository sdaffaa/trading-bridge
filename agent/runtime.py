"""The agent runtime — validate -> dedupe -> Tool Runner loop -> gated act.

This is the reliability envelope around the agent loop: idempotency, a hard
timeout, an iteration cap, and structured logging. The webhook layer dispatches
run_alert in a background thread so the HTTP response returns fast.
"""
import time
import hashlib
import threading

from anthropic import Anthropic

from . import config, tools, budget, monitoring, store, methodology
from .validation import validate_alert, Reject  # re-exported for callers
from . import idempotency
from .logging_setup import jlog

__all__ = ["run_alert", "dispatch", "Reject"]

_client = None
_client_lock = threading.Lock()


def _system() -> str:
    lines = [
        "You are an automated TECHNICAL ANALYST agent inside a bridge that receives "
        "TradingView alerts. Base every decision on technical analysis of the chart, "
        "not on the bare alert. For each alert:",
        "1) DATA SOURCE: if the alert already includes a 'technicals' block, those "
        "were computed on TradingView (your chart) — use them as the source of truth. "
        "Otherwise call analyze_chart(symbol, timeframe) for the technical picture "
        "(trend, EMA/SMA, RSI, ATR, market structure, fair value gaps, volume profile, "
        "volume state). Prefer the TradingView-provided technicals when both exist.",
        "2) Analyze using this methodology:\n" + methodology.instructions(),
        "3) Call submit_decision exactly once with action in "
        "{long, short, no_trade, alert_human}, confidence 0-1 reflecting confluence "
        "strength, and a one-line reason that CITES the specific technical factors "
        "(e.g. 'uptrend, RSI 58, price above SMA20, 1.2 ATR to recent high').",
    ]
    if config.ENABLE_EXECUTION:
        lines.append(
            "4) If action is long/short and confidence is high, call place_order with "
            "that side (capped and gated). Then call send_telegram once with a short "
            "summary of the technical rationale.")
    else:
        lines.append(
            "4) Then call send_telegram exactly once with a short summary of your "
            "decision and the technical reasoning. You are NOT authorized to place orders.")
    lines.append("If analyze_chart returns an error (no data feed), use action "
                 "alert_human and say data is unavailable. Be concise and decisive.")
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
         dry_run=config.DRY_RUN, model=config.MODEL, vision=config.VISION_MODE)

    if config.VISION_MODE:
        return _run_vision(alert, run_id)

    prompt = (
        f"TradingView alert:\n"
        f"- symbol: {alert['symbol']}\n"
        f"- action: {alert['action']}\n"
        f"- price: {alert['price']}\n"
        f"- timeframe: {alert['timeframe']}\n"
        f"- note: {alert['note']}\n"
        f"- id: {alert['id']}\n"
    )
    if alert.get("ta"):
        import json as _json
        prompt += (
            "- technicals (computed on TradingView, treat as source of truth): "
            f"{_json.dumps(alert['ta'])}\n"
        )
    prompt += "\nAssess this signal and follow your instructions."

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


def _run_vision(alert: dict, run_id: str) -> dict:
    """Vision path: open the chart, run the four school markups + coordinator,
    then send the chart image + trade plan (gated)."""
    import os
    from . import chartshot, vision, notify, annotate

    # top-down multi-timeframe chain (e.g. 240 -> 15 -> 3: bias, structure, entry)
    # when configured; otherwise the alert's own single timeframe. Entry = lowest.
    tfs = list(config.VISION_TIMEFRAMES)
    chain = tfs if len(tfs) >= 2 else None
    entry_tf = tfs[-1] if tfs else alert["timeframe"]
    tf_label = "→".join(tfs) if chain else entry_tf

    png, markups, levels, key_levels = None, [], {}, []
    shots, capture_ok = [], True
    if chain:
        for tf in chain:                               # highest -> lowest
            p = chartshot.capture(alert["symbol"], tf)
            if not p:
                capture_ok = False
                break
            shots.append((tf, p))
        png = shots[-1][1] if (shots and capture_ok) else None   # entry chart = image sent
    else:
        png = chartshot.capture(alert["symbol"], entry_tf)
        capture_ok = bool(png)

    if not capture_ok or not png:
        decision = {"action": "alert_human", "confidence": 0.0, "grade": "none",
                    "reason": "chart screenshot failed (browser/network on the host)"}
        monitoring.record_run(False, "chartshot failed")
    else:
        try:
            _followup_open_trades(alert, png, vision, entry_tf)  # track prior signals first
        except Exception as e:
            jlog("followup_error", run=run_id, id=alert["id"], error=str(e)[:200])
        try:
            if chain:
                out = vision.analyze_chain(shots, alert["symbol"])
            else:
                out = vision.analyze(png, alert["symbol"], entry_tf)
            decision, markups = out["decision"], out["markups"]
            levels = out.get("levels") or {}
            key_levels = out.get("key_levels") or []
            monitoring.record_run(True)
        except Exception as e:
            jlog("vision_error", run=run_id, id=alert["id"], error=str(e))
            monitoring.record_run(False, str(e)[:200])
            decision = {"action": "alert_human", "confidence": 0.0, "grade": "none",
                        "reason": f"vision analysis failed: {e}"}
            png = None
    decision["timeframe"] = tf_label

    # one live signal per symbol: if a prior trade on this pair is still open
    # (the follow-up above already closed any that hit TP/SL), don't fire a new
    # one at a different price — the management messages handle the open position.
    decision, suppressed = _suppress_if_duplicate(alert["symbol"], decision)
    if suppressed:
        jlog("trade_suppressed", run=run_id, id=alert["id"], symbol=alert["symbol"],
             reason="position_already_open")
        levels, key_levels = {}, []

    tools.ctx.decision = decision
    idempotency.mark(f"run:{alert['id']}")
    store.record_decision(alert["id"], run_id, alert["symbol"], decision, config.DRY_RUN)

    # draw the trade markup (entry / SL / TP zones) onto the image that gets sent.
    # Prefer the coordinator's own coordinates; fall back to a dedicated locate call.
    if png and decision.get("action") in ("long", "short"):
        try:
            ys = levels or vision.locate_levels(png, alert["symbol"], entry_tf, decision)
            if ys:
                png = annotate.render(png, decision, ys, key_levels)
            else:
                jlog("annotate_skipped", run=run_id, id=alert["id"], reason="no_levels")
        except Exception as e:
            jlog("annotate_error", run=run_id, id=alert["id"], error=str(e)[:200])

    caption = _format_plan(alert, decision, markups)
    _send_plan(alert["id"], png, caption)

    result = {"status": "ok", "id": alert["id"], "run": run_id,
              "decision": decision, "dry_run": config.DRY_RUN}
    jlog("run_end", **result)
    return result


def _suppress_if_duplicate(symbol: str, decision: dict):
    """Enforce one live signal per symbol. If a prior long/short on this pair is
    still open, downgrade a fresh long/short to no_trade so trades don't stack on
    the same pair at different prices. Returns (decision, suppressed?)."""
    if decision.get("action") not in ("long", "short"):
        return decision, False
    if not store.open_trades(symbol):
        return decision, False
    return ({"action": "no_trade",
             "confidence": decision.get("confidence", 0),
             "grade": decision.get("grade", "none"),
             "reason": "توجد صفقة مفتوحة على هذا الزوج — تتم إدارة المركز الحالي",
             "timeframe": decision.get("timeframe")}, True)


def _followup_open_trades(alert: dict, png, vision, timeframe=None) -> None:
    """Review still-open signals for this symbol against the fresh chart, report
    TP/SL hits in Arabic, and record their outcomes (the feedback loop)."""
    trades = store.open_trades(alert["symbol"])
    if not trades:
        return
    reviews = vision.evaluate_open_trades(png, alert["symbol"],
                                          timeframe or alert["timeframe"], trades)
    for t in trades:
        r = reviews.get(str(t["id"])) or reviews.get(t["id"])
        if not r:
            continue
        status = r.get("status")
        note = r.get("note", "")
        side = _AR_ACTION.get(t["action"], t["action"])
        if status == "tp_hit":
            store.record_outcome(t["id"], "win")
            _send_followup(t["id"],
                           f"✅ ضرب الهدف\n📊 {t['symbol']} — {side}\n"
                           f"الدخول: {t.get('entry')} ← الهدف: {t.get('tp')}\n{note}")
        elif status == "sl_hit":
            store.record_outcome(t["id"], "loss")
            _send_followup(t["id"],
                           f"❌ ضرب الوقف\n📊 {t['symbol']} — {side}\n"
                           f"الدخول: {t.get('entry')} ← الوقف: {t.get('sl')}\n{note}")
        elif status == "running":
            # active trade management: send an actionable recommendation once per
            # distinct action (deduped by manage key), stay silent on plain 'hold'.
            manage = r.get("manage", "hold")
            if manage in _AR_MANAGE:
                _send_followup(
                    t["id"],
                    f"🛠️ إدارة الصفقة\n📊 {t['symbol']} — {side}\n"
                    f"الدخول: {t.get('entry')} | الوقف: {t.get('sl')} | "
                    f"الهدف: {t.get('tp')}\nالتوصية: {_AR_MANAGE[manage]}\n{note}",
                    key=f"manage:{t['id']}:{manage}")
        # 'unclear' stays open — re-checked next run


def _send_followup(trade_id, message: str, key: str = None) -> None:
    """Send a follow-up message once (gated like any outbound notice). The dedupe
    key defaults to one-per-trade; pass an action-specific key to allow a distinct
    management message each time the recommendation changes."""
    import os
    from . import notify
    if os.path.exists(config.KILL_SWITCH_FILE):
        jlog("act_blocked", tool="telegram", id=trade_id, reason="kill_switch")
        return
    key = key or f"followup:{trade_id}"
    if idempotency.seen(key):
        return
    if config.DRY_RUN:
        jlog("act_dryrun", tool="telegram", id=trade_id, would_send=message[:200])
        idempotency.mark(key)
        return
    if notify.telegram_post(message):
        idempotency.mark(key)
    jlog("act", tool="telegram_followup", id=trade_id)


_AR_ACTION = {"long": "شراء 🟢", "short": "بيع 🔴",
              "no_trade": "لا توجد صفقة", "alert_human": "تدخل بشري ⚠️"}

# active trade-management recommendations (Arabic). 'hold' is intentionally absent
# so an on-track trade produces no message.
_AR_MANAGE = {
    "move_sl_be": "انقل وقف الخسارة إلى نقطة الدخول (تعادل) 🛡️",
    "partial_tp": "جني أرباح جزئي وتأمين الباقي 💰",
    "trail_sl": "حرّك الوقف خلف الهيكل (تتبّع الربح) 📈",
    "tighten_sl": "قرّب وقف الخسارة — الزخم يضعف ⚠️",
    "exit": "أغلق الصفقة الآن — السياق انقلب 🚪",
}


def _format_plan(alert: dict, d: dict, markups=None) -> str:
    head = f"📊 {alert['symbol']} — فريم {d.get('timeframe') or alert['timeframe']}"
    action = d.get("action")
    if action in ("no_trade", "alert_human", None):
        label = _AR_ACTION.get(action, "لا توجد صفقة")
        return (f"{head}\nالقرار: {label}  |  التصنيف: {d.get('grade','-')}\n"
                f"السبب: {d.get('reason','')}")
    lines = [
        head,
        f"القرار: {_AR_ACTION.get(action, action)}  |  التصنيف: {d.get('grade','-')}  "
        f"|  الثقة: {round(float(d.get('confidence',0) or 0)*100)}%",
        f"الدخول: {d.get('entry')}",
        f"وقف الخسارة: {d.get('stop_loss')}",
        f"جني الأرباح: {d.get('take_profit')}",
    ]
    if d.get("risk_reward"):
        lines.append(f"العائد/المخاطرة: {d['risk_reward']}")
    if d.get("risk_amount"):
        lines.append(f"المخاطرة: {d.get('risk_percent')}% ≈ {d['risk_amount']} "
                     f"(~{d.get('suggested_units')} وحدة)")
    lines.append(f"التحليل: {d.get('reason','')}")
    return "\n".join(str(x) for x in lines)


def _send_plan(event_id: str, png, caption: str) -> None:
    """Gate the outbound notification: mute -> kill switch -> idempotency -> dry-run."""
    import os
    from . import notify
    action = (tools.ctx.decision or {}).get("action")
    if action == "no_trade" and not config.NOTIFY_ON_NO_TRADE:
        jlog("act_skipped", tool="telegram", id=event_id, reason="no_trade_muted")
        return
    if os.path.exists(config.KILL_SWITCH_FILE):
        jlog("act_blocked", tool="telegram", id=event_id, reason="kill_switch")
        return
    key = f"telegram:{event_id}"
    if idempotency.seen(key):
        jlog("act_skipped", tool="telegram", id=event_id, reason="idempotent")
        return
    if config.DRY_RUN:
        jlog("act_dryrun", tool="telegram", id=event_id, would_send=caption[:200])
        return
    ok = notify.telegram_photo(png, caption) if png else notify.telegram_post(caption)
    if ok:
        idempotency.mark(key)
    jlog("act", tool="telegram", id=event_id, ok=ok, has_image=bool(png))


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
