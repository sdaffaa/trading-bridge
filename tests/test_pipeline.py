"""End-to-end tests for the agent pipeline — no network, no API key."""
import os
import json

import pytest

from agent import config, validation, idempotency, tools, scheduler, store
import agent.runtime as runtime
import tv_claude_bridge as bridge


# --- validation -----------------------------------------------------------
def test_validate_accepts_and_normalizes():
    a = validation.validate_alert(
        {"symbol": "OANDA:XAUUSD", "action": "BUY", "price": "2350.5", "timeframe": "240"})
    assert a["symbol"] == "OANDA:XAUUSD"
    assert a["action"] == "buy"        # lowercased
    assert a["price"] == 2350.5        # coerced to float
    assert len(a["id"]) == 16          # derived stable id


def test_validate_derives_stable_id():
    payload = {"symbol": "OANDA:XAUUSD", "action": "buy", "price": 1}
    assert validation.validate_alert(payload)["id"] == validation.validate_alert(payload)["id"]


@pytest.mark.parametrize("bad", [
    {"symbol": "BAD:X", "action": "buy", "price": 1},
    {"symbol": "OANDA:XAUUSD", "action": "hodl", "price": 1},
    {"symbol": "OANDA:XAUUSD", "action": "buy", "price": "abc"},
    "not-a-dict",
])
def test_validate_rejects(bad):
    with pytest.raises(validation.Reject):
        validation.validate_alert(bad)


# --- idempotency ----------------------------------------------------------
def test_idempotency_persists_and_dedupes():
    assert not idempotency.seen("run:X")
    idempotency.mark("run:X")
    assert idempotency.seen("run:X")
    # reconnecting to the SQLite file (restart) still sees the key
    store.reset_for_tests()
    assert idempotency.seen("run:X")


# --- act-tool gating ------------------------------------------------------
def test_send_telegram_dry_run_does_not_send():
    tools.new_context("r", "e", {})
    assert "dry-run" in tools.send_telegram("hi")


def test_send_telegram_blocked_by_kill_switch():
    tools.new_context("r", "e", {})
    open(config.KILL_SWITCH_FILE, "w").close()
    try:
        assert "kill switch" in tools.send_telegram("hi")
    finally:
        os.remove(config.KILL_SWITCH_FILE)


def test_send_telegram_idempotent(monkeypatch):
    # even outside dry-run, a repeat for the same event is skipped
    monkeypatch.setattr(config, "DRY_RUN", False)
    sent = []
    monkeypatch.setattr(tools, "telegram_post", lambda m: (sent.append(m), True)[1])
    tools.new_context("r", "evt-idem", {})
    assert tools.send_telegram("first") == "sent"
    assert "skipped" in tools.send_telegram("second")
    assert sent == ["first"]           # only sent once


def test_read_chart_disabled_returns_hint():
    tools.new_context("r", "e", {})
    assert "disabled" in json.loads(tools.read_chart("OANDA:XAUUSD", "240"))["error"]


def test_toolset_default_tools(monkeypatch):
    # read_price, read_chart, submit_decision, send_telegram (no place_order)
    monkeypatch.setattr(config, "ENABLE_EXECUTION", False)
    assert len(tools.build_toolset()) == 4


# --- runtime loop + dedupe (Claude stubbed) -------------------------------
def test_run_alert_runs_and_dedupes(stub_claude):
    a = {"symbol": "OANDA:XAUUSD", "action": "buy", "price": 2350, "id": "R1"}
    assert runtime.run_alert(a)["status"] == "ok"
    assert len(stub_claude) == 1                     # agent loop invoked once
    assert runtime.run_alert(a)["status"] == "duplicate"
    assert len(stub_claude) == 1                     # not invoked again


def test_run_alert_survives_agent_error(monkeypatch):
    class Boom:
        class beta:
            class messages:
                @staticmethod
                def tool_runner(**kw):
                    raise RuntimeError("api down")
    monkeypatch.setattr(runtime, "_client", Boom())
    out = runtime.run_alert({"symbol": "OANDA:XAUUSD", "action": "buy", "price": 1, "id": "E"})
    assert out["status"] == "error"                  # caught, not raised


# --- scheduler ------------------------------------------------------------
def test_scheduler_off_by_default(monkeypatch):
    monkeypatch.setattr(config, "SCHEDULE_SECONDS", 0)
    monkeypatch.setattr(scheduler, "_started", False)
    assert scheduler.start_if_enabled() is False


def test_scheduler_symbols_fallback(monkeypatch):
    monkeypatch.setattr(config, "SCHEDULE_SYMBOLS", set())
    monkeypatch.setattr(config, "ALLOWED_SYMBOLS", {"OANDA:XAUUSD", "FX:EURUSD"})
    # empty schedule set -> first allowed symbol (sorted)
    assert config.schedule_symbols() == {"FX:EURUSD"}


def test_scheduler_starts_when_enabled(monkeypatch):
    monkeypatch.setattr(config, "SCHEDULE_SECONDS", 3600)  # long, won't tick in-test
    monkeypatch.setattr(scheduler, "_started", False)
    assert scheduler.start_if_enabled() is True
    assert scheduler.start_if_enabled() is True             # idempotent


# --- webhook endpoints ----------------------------------------------------
@pytest.fixture
def client():
    return bridge.app.test_client()


def test_health_and_status(client):
    assert client.get("/health").status_code == 200
    body = json.loads(client.get("/status").data)
    assert body["dry_run"] is True
    assert "telegram_configured" in body


def test_webhook_accepts_good_alert(client, stub_claude):
    r = client.post("/webhook", json={"symbol": "OANDA:XAUUSD", "action": "buy",
                                      "price": 2350, "id": "W1"})
    assert r.status_code == 202
    assert json.loads(r.data)["id"] == "W1"


def test_webhook_rejects_bad_symbol(client):
    r = client.post("/webhook", json={"symbol": "BAD:X", "action": "buy", "price": 1})
    assert r.status_code == 400
    assert json.loads(r.data)["status"] == "rejected"


def test_webhook_rejects_invalid_json(client):
    r = client.post("/webhook", data="not json", content_type="text/plain")
    assert r.status_code == 400


def test_webhook_secret_enforced(client, monkeypatch):
    monkeypatch.setattr(config, "WEBHOOK_SECRET", "s3cret")
    good = {"symbol": "OANDA:XAUUSD", "action": "buy", "price": 1}
    assert client.post("/webhook", json=good).status_code == 401
    r = client.post("/webhook", json=good, headers={"X-Webhook-Secret": "s3cret"})
    assert r.status_code == 202
