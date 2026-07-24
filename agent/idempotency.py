"""File-backed idempotency store — same event produces the same effect once.

Webhooks and retries deliver duplicates; without deduping we double-send or
double-trade. Keys are persisted to disk so a restart does not re-fire past
events. Swap this module's two functions for Redis/DB in a multi-process deploy.
"""
import os
import threading

from . import config
from .logging_setup import jlog

_LOCK = threading.Lock()
_SEEN = set()
_LOADED = False


def _path() -> str:
    return os.path.join(config.STATE_DIR, "processed_keys.txt")


def _ensure_loaded() -> None:
    global _LOADED
    if _LOADED:
        return
    try:
        os.makedirs(config.STATE_DIR, exist_ok=True)
        if os.path.exists(_path()):
            with open(_path(), "r", encoding="utf-8") as f:
                for line in f:
                    k = line.strip()
                    if k:
                        _SEEN.add(k)
    except OSError as e:
        jlog("idempotency_load_error", error=str(e))
    _LOADED = True


def seen(key: str) -> bool:
    with _LOCK:
        _ensure_loaded()
        return key in _SEEN


def mark(key: str) -> None:
    """Record a key as processed (idempotent; persists best-effort)."""
    with _LOCK:
        _ensure_loaded()
        if key in _SEEN:
            return
        _SEEN.add(key)
        try:
            os.makedirs(config.STATE_DIR, exist_ok=True)
            with open(_path(), "a", encoding="utf-8") as f:
                f.write(key + "\n")
        except OSError as e:
            jlog("idempotency_persist_error", key=key, error=str(e))
