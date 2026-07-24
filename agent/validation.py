"""Trigger validation — the first, cheapest guardrail.

Reject malformed or out-of-policy alerts at the door, before the agent sees
anything. Derives a stable idempotency id when the sender doesn't supply one.
"""
import json
import hashlib

from . import config


class Reject(Exception):
    """Raised when a trigger payload fails validation. Never reaches the agent."""


def validate_alert(data) -> dict:
    if not isinstance(data, dict):
        raise Reject("payload is not a JSON object")

    symbol = data.get("symbol")
    if symbol not in config.ALLOWED_SYMBOLS:
        raise Reject(f"symbol not allowed: {symbol!r}")

    action = str(data.get("action", "")).lower()
    if action not in config.ALLOWED_ACTIONS:
        raise Reject(f"action not allowed: {action!r}")

    price = data.get("price")
    if price is not None:
        try:
            price = float(price)
        except (TypeError, ValueError):
            raise Reject(f"invalid price: {price!r}")

    timeframe = str(data.get("timeframe", "")) or None

    event_id = str(data.get("id") or "").strip()
    if not event_id:
        # Stable hash of the meaningful fields → deterministic idempotency key.
        basis = {"symbol": symbol, "action": action, "price": price, "timeframe": timeframe}
        event_id = hashlib.sha256(
            json.dumps(basis, sort_keys=True).encode()).hexdigest()[:16]

    return {
        "id": event_id,
        "symbol": symbol,
        "action": action,
        "price": price,
        "timeframe": timeframe,
        "note": str(data.get("note", "") or "")[:500],
    }
