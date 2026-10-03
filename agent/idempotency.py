"""Idempotency — same event produces the same effect once.

Thin wrapper over the durable SQLite store (agent/store.py), which persists keys
across restarts. Kept as a named module so call sites read clearly.
"""
from . import store


def seen(key: str) -> bool:
    return store.seen(key)


def mark(key: str) -> None:
    store.mark(key)
