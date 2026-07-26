"""Tests for the completeness build: data, market hours, budget, monitoring,
execution, decision tracking, and the new endpoints."""
import json
from datetime import datetime, timezone

import pytest

from agent import (config, store, budget, monitoring, market_hours,
                   marketdata, broker, tools)
import agent.runtime as runtime
import tv_claude_bridge as bridge


# --- market hours ---------------------------------------------------------
def test_crypto_always_open():
    assert market_hours.is_open("BINANCE:BTCUSDT") is True


def test_forex_closed_saturday():
    sat = datetime(2026, 7, 25, 12, 0, tzinfo=timezone.utc)   # Saturday
    assert market_hours.is_open("OANDA:XAUUSD", now=sat) is False


def test_forex_open_wednesday():
    wed = datetime(2026, 7, 22, 12, 0, tzinfo=timezone.utc)   # Wednesday
    assert market_hours.is_open("OANDA:XAUUSD", now=wed) is True


def test_forex_sunday_opens_at_21():
    assert market_hours.is_open("FX:EURUSD",
                                now=datetime(2026, 7, 26, 20, tzinfo=timezone.utc)) is False
    assert market_hours.is_open("FX:EURUSD",
                                now=datetime(2026, 7, 26, 22, tzinfo=timezone.utc)) is True


# --- market data ----------------------------------------------------------
def test_marketdata_none_provider():
    assert "error" in marketdata.get_quote("OANDA:XAUUSD")


def test_marketdata_generic(monkeypatch):
    monkeypatch.setattr(config, "DATA_PROVIDER", "generic")
    monkeypatch.setattr(config, "DATA_URL_TEMPLATE", "https://x/{symbol}")
    monkeypatch.setattr(config, "DATA_PRICE_PATH", "data.0.p")

    class R:
        def raise_for_status(self): pass
        def json(self): return {"data": [{"p": 2351.2}]}
    monkeypatch.setattr(marketdata.requests, "get", lambda *a, **k: R())
    q = marketdata.get_quote("OANDA:XAUUSD")
    assert q["price"] == 2351.2 and q["source"] == "generic"


def test_read_price_tool(monkeypatch):
    tools.new_context("r", "e", {"symbol": "OANDA:XAUUSD"})
    monkeypatch.setattr(marketdata, "get_quote",
                        lambda s: {"symbol": s, "price": 2350, "source": "test"})
    assert json.loads(tools.read_price("OANDA:XAUUSD"))["price"] == 2350


# --- budget ---------------------------------------------------------------
def test_budget_daily_cap(monkeypatch):
    monkeypatch.setattr(config, "DAILY_TOKEN_BUDGET", 100)
    assert budget.allow_run()[0] is True
    budget.add_usage(150)
    ok, why = budget.allow_run()
    assert ok is False and "budget" in why


def test_budget_throttle(monkeypatch):
    monkeypatch.setattr(config, "MIN_RUN_INTERVAL_S", 999)
    assert budget.allow_run()[0] is True
    assert budget.allow_run()[0] is False        # too soon


# --- monitoring -----------------------------------------------------------
def test_monitoring_alerts_after_threshold(monkeypatch):
    monkeypatch.setattr(config, "ALERT_FAILS_THRESHOLD", 2)
    monkeypatch.setattr(config, "ALERT_ON_FAILURE", True)
    alerts = []
    monkeypatch.setattr(monitoring, "alert_operator", lambda m: alerts.append(m))
    monitoring.record_run(False, "boom")
    assert not alerts                            # 1st failure: no alert yet
    monitoring.record_run(False, "boom")
    assert len(alerts) == 1                      # threshold reached
    monitoring.record_run(True)                  # success resets the counter
    assert monitoring.health()["consecutive_failures"] == 0


# --- execution layer ------------------------------------------------------
def test_execution_disabled_by_default():
    r = broker.place_order("OANDA:XAUUSD", "long", 0.9, "x")
    assert r["status"] == "disabled"


def test_execution_enforces_confidence(monkeypatch):
    monkeypatch.setattr(config, "ENABLE_EXECUTION", True)
    monkeypatch.setattr(config, "MIN_CONFIDENCE_TO_TRADE", 0.7)
    assert broker.place_order("OANDA:XAUUSD", "long", 0.5, "x")["status"] == "rejected"


def test_execution_dry_run(monkeypatch):
    monkeypatch.setattr(config, "ENABLE_EXECUTION", True)
    monkeypatch.setattr(config, "DRY_RUN", True)
    r = broker.place_order("OANDA:XAUUSD", "long", 0.9, "evt")
    assert r["status"] == "dry_run"


def test_execution_idempotent(monkeypatch):
    monkeypatch.setattr(config, "ENABLE_EXECUTION", True)
    monkeypatch.setattr(config, "DRY_RUN", False)
    monkeypatch.setattr(config, "MIN_CONFIDENCE_TO_TRADE", 0.5)
    first = broker.place_order("OANDA:XAUUSD", "long", 0.9, "evt-x")
    assert first["status"] == "paper_filled"
    assert broker.place_order("OANDA:XAUUSD", "long", 0.9, "evt-x")["status"] == "skipped"


def test_toolset_includes_place_order_when_enabled(monkeypatch):
    monkeypatch.setattr(config, "ENABLE_EXECUTION", True)
    names = [t.name if hasattr(t, "name") else str(t) for t in tools.build_toolset()]
    assert any("place_order" in n for n in names)


# --- decision tracking + endpoints ----------------------------------------
def test_decision_recorded_and_stats(stub_claude, monkeypatch):
    # drive a decision via the runtime, then check it persisted
    def fake_runner(**kw):
        tools.submit_decision("long", 0.8, "test setup")
        return iter([])
    monkeypatch.setattr(runtime._client.beta.messages, "tool_runner", fake_runner)
    runtime.run_alert({"symbol": "OANDA:XAUUSD", "action": "buy", "price": 1, "id": "D9"})
    s = store.stats()
    assert s["total_decisions"] == 1
    assert s["by_action"].get("long") == 1


def test_outcome_endpoint_updates_accuracy(stub_claude, monkeypatch):
    def fake_runner(**kw):
        tools.submit_decision("long", 0.8, "x")
        return iter([])
    monkeypatch.setattr(runtime._client.beta.messages, "tool_runner", fake_runner)
    runtime.run_alert({"symbol": "OANDA:XAUUSD", "action": "buy", "price": 1, "id": "D10"})

    c = bridge.app.test_client()
    r = c.post("/outcome", json={"id": "D10", "outcome": "win", "pnl": 12.5})
    assert r.status_code == 200
    stats = json.loads(c.get("/stats").data)
    assert stats["wins"] == 1 and stats["accuracy"] == 1.0 and stats["total_pnl"] == 12.5


def test_outcome_unknown_id_404():
    c = bridge.app.test_client()
    assert c.post("/outcome", json={"id": "nope", "outcome": "win"}).status_code == 404


def test_health_deep():
    c = bridge.app.test_client()
    body = json.loads(c.get("/health").data)
    assert "consecutive_failures" in body and "budget" in body


def test_run_throttled_returns_status(monkeypatch, stub_claude):
    monkeypatch.setattr(config, "MIN_RUN_INTERVAL_S", 999)
    budget.allow_run()                            # consume the slot
    out = runtime.run_alert({"symbol": "OANDA:XAUUSD", "action": "buy", "price": 1, "id": "T"})
    assert out["status"] == "throttled"
