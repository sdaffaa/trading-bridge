"""Self-monitoring — who watches the watcher.

Tracks run success/failure, alerts the operator after N consecutive failures,
and (optionally) runs a watchdog that alerts if no successful run happens within
a silence window. Operator alerts are system-health notices, so they send
regardless of AGENT_DRY_RUN (dry-run governs trading actions, not ops alerts).
"""
import time
import threading
from datetime import datetime, timezone

from . import config, store
from .logging_setup import jlog
from .notify import telegram_post

_lock = threading.Lock()
_consecutive_failures = 0
_watchdog_started = False


def record_run(ok: bool, detail: str = "") -> None:
    """Record a run's success/failure; alert after a run of failures."""
    global _consecutive_failures
    store.record_metric("run", ok, detail)
    with _lock:
        if ok:
            _consecutive_failures = 0
            return
        _consecutive_failures += 1
        n = _consecutive_failures
    jlog("run_failure_recorded", consecutive=n, detail=detail)
    if config.ALERT_ON_FAILURE and n == config.ALERT_FAILS_THRESHOLD:
        alert_operator(f"⚠️ trading-bridge: {n} consecutive run failures. Last: {detail}")


def alert_operator(message: str) -> bool:
    """Send an operational alert to the operator (ignores dry-run)."""
    if not (config.TELEGRAM_TOKEN and config.TELEGRAM_CHAT_ID):
        jlog("operator_alert_undeliverable", message=message[:200])
        return False
    ok = telegram_post(message)
    jlog("operator_alert", ok=ok, message=message[:200])
    return ok


def health() -> dict:
    last = store.last_success_ts("run")
    with _lock:
        fails = _consecutive_failures
    age = (time.time() - last) if last else None
    return {
        "status": "ok",
        "last_success_ts": last,
        "last_success_age_s": round(age, 1) if age is not None else None,
        "consecutive_failures": fails,
    }


def start_watchdog_if_enabled() -> bool:
    global _watchdog_started
    if config.HEARTBEAT_MAX_SILENCE_S <= 0:
        return False
    with _lock:
        if _watchdog_started:
            return True
        _watchdog_started = True
    threading.Thread(target=_watchdog_loop, daemon=True, name="watchdog").start()
    jlog("watchdog_started", max_silence_s=config.HEARTBEAT_MAX_SILENCE_S)
    return True


def _watchdog_loop() -> None:
    limit = config.HEARTBEAT_MAX_SILENCE_S
    alerted = False
    while True:
        time.sleep(max(30, limit // 3))
        last = store.last_success_ts("run")
        silent = (time.time() - last) if last else None
        if silent is not None and silent > limit:
            if not alerted:
                alert_operator(
                    f"🚨 trading-bridge: no successful run in {int(silent)}s "
                    f"(limit {limit}s). Is the market open / the feed up?")
                alerted = True
        else:
            alerted = False
