"""Structured JSON logging — one line per step, keyed by run/event ids.

You cannot operate what you cannot see. Every tool call, decision, and act emits
a single JSON line so a run is reconstructable and alert-able.
"""
import json
import logging
import sys

_logger = logging.getLogger("agent")


def setup(level: str = "INFO") -> logging.Logger:
    if not _logger.handlers:
        h = logging.StreamHandler(sys.stdout)
        h.setFormatter(logging.Formatter("%(message)s"))
        _logger.addHandler(h)
    _logger.setLevel(level)
    _logger.propagate = False
    return _logger


def jlog(event: str, **fields) -> None:
    """Emit one structured line. Never raise from logging."""
    try:
        _logger.info(json.dumps({"event": event, **fields}, default=str, ensure_ascii=False))
    except Exception:  # logging must never break the pipeline
        _logger.info(json.dumps({"event": event, "log_error": True}))


setup()
