"""Autonomous scheduled trigger — the system starts analyzing on its own.

When AGENT_SCHEDULE_SECONDS > 0, a background thread fires a periodic analysis
run for each configured symbol, with no webhook and no manual command. This is
the "cron" trigger from the agent-automation skill, made real: every tick emits
an `info` alert per symbol and dispatches it through the same validated,
deduped, gated pipeline the webhook uses.
"""
import time
import threading

from . import config, market_hours
from .logging_setup import jlog

_started = False
_lock = threading.Lock()


def start_if_enabled() -> bool:
    """Start the scheduler once, if configured. Safe to call multiple times."""
    global _started
    if config.SCHEDULE_SECONDS <= 0:
        return False
    with _lock:
        if _started:
            return True
        _started = True
    threading.Thread(target=_loop, daemon=True, name="scheduler").start()
    jlog("scheduler_started", every_s=config.SCHEDULE_SECONDS,
         symbols=sorted(config.schedule_symbols()), timeframe=config.SCHEDULE_TIMEFRAME)
    return True


def _loop() -> None:
    from . import runtime  # late import to avoid an import cycle
    while True:
        tick = int(time.time())
        for symbol in sorted(config.schedule_symbols()):
            if config.RESPECT_MARKET_HOURS and not market_hours.is_open(symbol):
                jlog("scheduler_skip_closed", symbol=symbol)
                continue
            alert = {
                "symbol": symbol,
                "action": "info",
                "timeframe": config.SCHEDULE_TIMEFRAME,
                "note": "scheduled periodic analysis",
                # unique per tick so idempotency doesn't suppress scheduled runs
                "id": f"sched:{symbol}:{tick}",
            }
            try:
                runtime.dispatch(alert)
            except runtime.Reject as e:
                jlog("scheduler_reject", symbol=symbol, reason=str(e))
            except Exception as e:  # a bad tick must not kill the loop
                jlog("scheduler_error", symbol=symbol, error=str(e))
        time.sleep(config.SCHEDULE_SECONDS)
