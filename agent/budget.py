"""Cost & rate controls — keep an autonomous loop from running away.

A daily token budget (approx, in-memory, resets on restart or UTC day change)
and a minimum interval between runs (throttle). Both off by default (0).
"""
import time
import threading
from datetime import datetime, timezone

from . import config

_lock = threading.Lock()
_day = None
_tokens_used = 0
_last_run_ts = 0.0


def _today() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def allow_run() -> tuple:
    """(ok, reason). Enforces the min-interval throttle and daily token budget."""
    global _day, _tokens_used, _last_run_ts
    with _lock:
        now = time.time()
        if _day != _today():                       # roll the daily counter
            _day, _tokens_used = _today(), 0
        if config.MIN_RUN_INTERVAL_S > 0 and (now - _last_run_ts) < config.MIN_RUN_INTERVAL_S:
            return False, "throttled (min run interval)"
        if config.DAILY_TOKEN_BUDGET > 0 and _tokens_used >= config.DAILY_TOKEN_BUDGET:
            return False, "daily token budget exhausted"
        _last_run_ts = now
        return True, "ok"


def add_usage(tokens: int) -> None:
    global _tokens_used
    with _lock:
        _tokens_used += max(0, int(tokens or 0))


def remaining() -> dict:
    with _lock:
        used = _tokens_used if _day == _today() else 0
    budget = config.DAILY_TOKEN_BUDGET
    return {"daily_token_budget": budget, "tokens_used_today": used,
            "tokens_remaining": (budget - used) if budget > 0 else None}
