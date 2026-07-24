"""Execution layer — OFF by default, deliberately.

Turning this on lets the agent place orders. It is heavily gated: disabled
unless AGENT_ENABLE_EXECUTION=1, honors the kill switch and dry-run, enforces
hard caps (size, max open positions, min confidence), and is idempotent per
decision id. The default broker is a PaperBroker that only records intended
orders — no real money. Implement a real broker by subclassing Broker and
selecting it via AGENT_BROKER.
"""
import os

from . import config, store
from .logging_setup import jlog


class Broker:
    name = "base"

    def submit(self, symbol, side, size, event_id) -> dict:
        raise NotImplementedError


class PaperBroker(Broker):
    """Records intended orders to the store; executes nothing real."""
    name = "paper"

    def submit(self, symbol, side, size, event_id) -> dict:
        jlog("paper_order", symbol=symbol, side=side, size=size, id=event_id)
        return {"status": "paper_filled", "symbol": symbol, "side": side, "size": size}


def _select() -> Broker:
    if config.BROKER == "paper":
        return PaperBroker()
    # add real brokers here (e.g. MT5/CCXT) and select by name
    jlog("broker_unknown", broker=config.BROKER)
    return PaperBroker()


def kill_switch_engaged() -> bool:
    return os.path.exists(config.KILL_SWITCH_FILE)


def place_order(symbol: str, side: str, confidence: float, event_id: str) -> dict:
    """Gated order placement. side in {long, short}. Returns a status dict."""
    if not config.ENABLE_EXECUTION:
        return {"status": "disabled", "reason": "execution disabled (AGENT_ENABLE_EXECUTION=0)"}
    if kill_switch_engaged():
        jlog("order_blocked", reason="kill_switch", id=event_id)
        return {"status": "blocked", "reason": "kill switch engaged"}
    if side not in ("long", "short"):
        return {"status": "rejected", "reason": f"non-directional action: {side}"}
    if confidence < config.MIN_CONFIDENCE_TO_TRADE:
        return {"status": "rejected",
                "reason": f"confidence {confidence} < min {config.MIN_CONFIDENCE_TO_TRADE}"}
    if store.open_positions_count() >= config.MAX_OPEN_POSITIONS:
        return {"status": "rejected", "reason": "max open positions reached"}

    order_key = f"order:{event_id}"
    if store.seen(order_key):
        return {"status": "skipped", "reason": "idempotent replay"}

    size = config.MAX_POSITION_SIZE
    if config.DRY_RUN:
        jlog("order_dryrun", symbol=symbol, side=side, size=size, id=event_id)
        return {"status": "dry_run", "symbol": symbol, "side": side, "size": size}

    result = _select().submit(symbol, side, size, event_id)
    store.mark(order_key)
    jlog("order_placed", id=event_id, **result)
    return result
