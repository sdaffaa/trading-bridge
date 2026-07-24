"""Tests for risk sizing and the vision multi-agent pipeline (mocked client)."""
import json

from agent import config, risk, vision


# --- risk ------------------------------------------------------------------
def test_risk_long_rr_and_size(monkeypatch):
    monkeypatch.setattr(config, "ACCOUNT_BALANCE", 10000.0)
    monkeypatch.setattr(config, "RISK_PERCENT", 1.0)
    monkeypatch.setattr(config, "MIN_RR", 2.0)
    p = risk.compute("long", entry=2000, sl=1990, tp=2030)
    assert p["risk_reward"] == 3.0            # (2030-2000)/(2000-1990)
    assert p["meets_min_rr"] is True
    assert p["risk_amount"] == 100.0          # 1% of 10000
    assert p["stop_distance"] == 10


def test_risk_no_trade_returns_empty():
    p = risk.compute("no_trade", 0, 0, 0)
    assert p["risk_reward"] is None


def test_risk_short():
    p = risk.compute("short", entry=100, sl=105, tp=90)
    assert p["risk_reward"] == 2.0            # (100-90)/(105-100)


# --- vision pipeline (client stubbed) -------------------------------------
class _Block:
    type = "text"
    def __init__(self, t): self.text = t


class _Resp:
    def __init__(self, t): self.content = [_Block(t)]


class _Msgs:
    def __init__(self, plan): self._plan = plan
    def create(self, **kw):
        # coordinator call uses output_config with a json_schema
        if "output_config" in kw:
            return _Resp(json.dumps(self._plan))
        return _Resp("markup: bias up, key level 1990")


class _Beta:  # unused here but mirrors client shape
    pass


class _Client:
    def __init__(self, plan): self.messages = _Msgs(plan)


def test_vision_analyze_builds_decision(monkeypatch):
    monkeypatch.setattr(config, "VISION_SCHOOLS", {"ict", "smc"})
    monkeypatch.setattr(config, "ACCOUNT_BALANCE", 5000.0)
    plan = {"action": "long", "grade": "A", "confidence": 0.8,
            "entry": 2000, "stop_loss": 1990, "take_profit": 2040, "reason": "confluence up"}
    monkeypatch.setattr(vision, "_client", _Client(plan))
    out = vision.analyze(b"\x89PNG_fake", "OANDA:XAUUSD", "240")
    d = out["decision"]
    assert d["action"] == "long" and d["grade"] == "A"
    assert d["risk_reward"] == 4.0            # (2040-2000)/(2000-1990)
    assert d["risk_amount"] == 50.0           # 1% of 5000
    assert len(out["markups"]) == 2           # one per school


def test_vision_handles_bad_coordinator(monkeypatch):
    monkeypatch.setattr(config, "VISION_SCHOOLS", {"ict"})

    class BadMsgs:
        def create(self, **kw):
            if "output_config" in kw:
                return _Resp("not json")
            return _Resp("markup")
    monkeypatch.setattr(vision, "_client", type("C", (), {"messages": BadMsgs()})())
    out = vision.analyze(b"x", "OANDA:XAUUSD", "240")
    assert out["decision"]["action"] == "alert_human"
