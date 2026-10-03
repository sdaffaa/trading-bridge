"""trading-bridge agent package.

An autonomous Claude agent pipeline: a validated trigger -> a Tool Runner agent
loop -> gated tools -> a reliability envelope (idempotency, retries, timeout,
structured logs, kill switch, dry-run).

Public entry points:
    from agent.runtime import run_alert, dispatch, Reject
"""
from .runtime import run_alert, dispatch, Reject  # noqa: F401

__all__ = ["run_alert", "dispatch", "Reject"]
