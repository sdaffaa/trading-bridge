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


def test_vision_analyze_returns_coordinator_levels(monkeypatch):
    monkeypatch.setattr(config, "VISION_SCHOOLS", {"ict"})
    plan = {"action": "long", "grade": "B", "confidence": 0.7,
            "entry": 2000, "stop_loss": 1990, "take_profit": 2030, "reason": "صعود",
            "entry_y": 0.5, "stop_y": 0.6, "target_y": 0.3}
    monkeypatch.setattr(vision, "_client", _Client(plan))
    out = vision.analyze(b"png", "OANDA:XAUUSD", "15")
    assert out["levels"] == {"entry_y": 0.5, "stop_y": 0.6, "target_y": 0.3}


def test_vision_analyze_levels_empty_when_partial(monkeypatch):
    monkeypatch.setattr(config, "VISION_SCHOOLS", {"ict"})
    plan = {"action": "long", "grade": "B", "confidence": 0.7,
            "entry": 2000, "stop_loss": 1990, "take_profit": 2030, "reason": "صعود",
            "entry_y": 0.5}                       # missing stop_y/target_y
    monkeypatch.setattr(vision, "_client", _Client(plan))
    out = vision.analyze(b"png", "OANDA:XAUUSD", "15")
    assert out["levels"] == {}                    # incomplete -> not used


def test_vision_analyze_mtf_uses_lower_tf_and_tags(monkeypatch):
    monkeypatch.setattr(config, "VISION_SCHOOLS", {"ict", "smc"})
    plan = {"action": "long", "grade": "B", "confidence": 0.7,
            "entry": 2000, "stop_loss": 1990, "take_profit": 2030, "reason": "توافق صعودي"}
    monkeypatch.setattr(vision, "_client", _Client(plan))
    out = vision.analyze_mtf(b"htf", b"ltf", "OANDA:XAUUSD", "240", "15")
    assert out["decision"]["action"] == "long"
    assert out["decision"]["timeframe"] == "15"          # entry from the lower TF
    tfs = {m["timeframe"] for m in out["markups"]}
    assert tfs == {"240", "15"}                            # both TFs represented
    assert len(out["markups"]) == 4                        # 2 schools x 2 timeframes


def test_evaluate_open_trades_maps_status(monkeypatch):
    reviews = {"reviews": [
        {"id": "t1", "status": "tp_hit", "note": "ضرب الهدف"},
        {"id": "t2", "status": "running", "note": "ما زالت جارية"},
    ]}

    class RevMsgs:
        def create(self, **kw):
            return _Resp(json.dumps(reviews))
    monkeypatch.setattr(vision, "_client", type("C", (), {"messages": RevMsgs()})())
    trades = [{"id": "t1", "action": "long", "entry": 2000, "sl": 1990, "tp": 2030},
              {"id": "t2", "action": "short", "entry": 100, "sl": 105, "tp": 90}]
    out = vision.evaluate_open_trades(b"png", "OANDA:XAUUSD", "15", trades)
    assert out["t1"]["status"] == "tp_hit"
    assert out["t2"]["status"] == "running"


def test_evaluate_open_trades_empty_shortcircuits():
    assert vision.evaluate_open_trades(b"png", "X", "15", []) == {}


def test_locate_levels_clamps_fractions(monkeypatch):
    ys = {"entry_y": 0.5, "stop_y": 1.4, "target_y": -0.2}   # out-of-range on purpose

    class LocMsgs:
        def create(self, **kw):
            return _Resp(json.dumps(ys))
    monkeypatch.setattr(vision, "_client", type("C", (), {"messages": LocMsgs()})())
    out = vision.locate_levels(b"png", "OANDA:XAUUSD", "15",
                               {"entry": 2000, "stop_loss": 1990, "take_profit": 2030})
    assert out["entry_y"] == 0.5
    assert out["stop_y"] == 1.0        # clamped to [0,1]
    assert out["target_y"] == 0.0


def test_locate_levels_needs_prices():
    assert vision.locate_levels(b"png", "X", "15", {"entry": None}) == {}


# --- on-chart markup rendering --------------------------------------------
def _blank_png(w=800, h=600):
    import io
    from PIL import Image
    buf = io.BytesIO()
    Image.new("RGB", (w, h), (20, 22, 28)).save(buf, format="PNG")
    return buf.getvalue()


def test_annotate_draws_on_trade():
    from agent import annotate
    png = _blank_png()
    d = {"action": "long", "grade": "B", "entry": 2000, "stop_loss": 1990,
         "take_profit": 2030, "risk_reward": 3.0}
    out = annotate.render(png, d, {"entry_y": 0.5, "stop_y": 0.62, "target_y": 0.3})
    assert out != png and len(out) > len(png)      # something was drawn


def test_annotate_noop_without_levels():
    from agent import annotate
    png = _blank_png()
    d = {"action": "long", "entry": 2000, "stop_loss": 1990, "take_profit": 2030}
    assert annotate.render(png, d, {}) == png       # no ys -> unchanged


def test_annotate_noop_on_no_trade():
    from agent import annotate
    png = _blank_png()
    assert annotate.render(png, {"action": "no_trade"}, {}) == png


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
