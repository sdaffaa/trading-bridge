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
    # Match tolerantly: TradingView sends the bare ticker ("XAUUSD") while the
    # allowlist may carry an exchange prefix ("OANDA:XAUUSD"). Compare by the
    # part after ":" so both forms work.
    def _bare(s):
        return str(s).split(":")[-1].strip().upper()
    allowed_bare = {_bare(x) for x in config.ALLOWED_SYMBOLS}
    if symbol not in config.ALLOWED_SYMBOLS and _bare(symbol) not in allowed_bare:
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

    result = {
        "id": event_id,
        "symbol": symbol,
        "action": action,
        "price": price,
        "timeframe": timeframe,
        "note": str(data.get("note", "") or "")[:500],
    }
    # TradingView-computed technicals (from the Pine feed) — pass through so the
    # agent analyzes TradingView's own numbers, no external data platform needed.
    ta = data.get("ta")
    if isinstance(ta, dict):
        result["ta"] = {str(k)[:32]: v for k, v in list(ta.items())[:32]}
    return result
