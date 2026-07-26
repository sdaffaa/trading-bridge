"""Arabic trade formatting + open-trade follow-up (the feedback loop)."""
from agent import config, store, idempotency
import agent.runtime as runtime


# --- Arabic caption --------------------------------------------------------
def test_format_plan_arabic_trade():
    alert = {"symbol": "OANDA:XAUUSD", "timeframe": "15"}
    d = {"action": "long", "grade": "B", "confidence": 0.72, "timeframe": "240→15",
         "entry": 2000, "stop_loss": 1990, "take_profit": 2030,
         "risk_reward": 3.0, "reason": "توافق ICT و SMC صعوداً"}
    out = runtime._format_plan(alert, d)
    assert "شراء" in out
    assert "الدخول: 2000" in out
    assert "240→15" in out                     # multi-timeframe label shown
    assert "التحليل: توافق" in out


def test_format_plan_arabic_no_trade():
    alert = {"symbol": "FX:EURUSD", "timeframe": "15"}
    d = {"action": "no_trade", "grade": "none", "reason": "تعارض بين المدارس"}
    out = runtime._format_plan(alert, d)
    assert "لا توجد صفقة" in out
    assert "تعارض" in out


# --- follow-up: TP/SL detection records outcomes + notifies ----------------
class _FakeVision:
    def __init__(self, reviews): self._reviews = reviews
    def evaluate_open_trades(self, png, symbol, timeframe, trades):
        return self._reviews


def _seed_open_trade(symbol="OANDA:XAUUSD"):
    decision = {"action": "long", "confidence": 0.8, "grade": "B",
                "entry": 2000, "stop_loss": 1990, "take_profit": 2030,
                "reason": "setup"}
    store.record_decision("evt-1", "run-1", symbol, decision, dry_run=True)


def test_followup_tp_hit_records_win(monkeypatch):
    monkeypatch.setattr(config, "DRY_RUN", True)     # no real telegram
    _seed_open_trade()
    assert len(store.open_trades("OANDA:XAUUSD")) == 1

    vision = _FakeVision({"evt-1": {"status": "tp_hit", "note": "ضرب الهدف"}})
    runtime._followup_open_trades({"symbol": "OANDA:XAUUSD", "timeframe": "15"},
                                  b"png", vision, "15")

    # outcome recorded → the trade is no longer open, and it's a win
    assert store.open_trades("OANDA:XAUUSD") == []
    assert store.stats()["wins"] == 1


def test_followup_sl_hit_records_loss(monkeypatch):
    monkeypatch.setattr(config, "DRY_RUN", True)
    _seed_open_trade()
    vision = _FakeVision({"evt-1": {"status": "sl_hit", "note": "ضرب الوقف"}})
    runtime._followup_open_trades({"symbol": "OANDA:XAUUSD", "timeframe": "15"},
                                  b"png", vision, "15")
    assert store.open_trades("OANDA:XAUUSD") == []
    s = store.stats()
    assert s["graded"] == 1 and s["wins"] == 0


def test_followup_running_keeps_trade_open(monkeypatch):
    monkeypatch.setattr(config, "DRY_RUN", True)
    _seed_open_trade()
    vision = _FakeVision({"evt-1": {"status": "running", "manage": "hold",
                                    "note": "ما زالت جارية"}})
    runtime._followup_open_trades({"symbol": "OANDA:XAUUSD", "timeframe": "15"},
                                  b"png", vision, "15")
    assert len(store.open_trades("OANDA:XAUUSD")) == 1   # still open


def test_followup_running_management_recommendation(monkeypatch):
    monkeypatch.setattr(config, "DRY_RUN", True)
    _seed_open_trade()
    vision = _FakeVision({"evt-1": {"status": "running", "manage": "move_sl_be",
                                    "note": "الصفقة في ربح جيد"}})
    runtime._followup_open_trades({"symbol": "OANDA:XAUUSD", "timeframe": "3"},
                                  b"png", vision, "3")
    assert len(store.open_trades("OANDA:XAUUSD")) == 1        # still open, managed
    assert idempotency.seen("manage:evt-1:move_sl_be")       # rec sent (deduped)


def test_suppress_new_trade_when_position_open():
    _seed_open_trade("OANDA:XAUUSD")
    d = {"action": "long", "confidence": 0.8, "grade": "A", "timeframe": "240→15→3",
         "entry": 4100, "stop_loss": 4080, "take_profit": 4140}
    out, suppressed = runtime._suppress_if_duplicate("OANDA:XAUUSD", d)
    assert suppressed is True
    assert out["action"] == "no_trade"                # downgraded, not a new trade


def test_no_suppression_when_flat():
    d = {"action": "long", "confidence": 0.8, "grade": "A",
         "entry": 4100, "stop_loss": 4080, "take_profit": 4140}
    out, suppressed = runtime._suppress_if_duplicate("OANDA:XAUUSD", d)
    assert suppressed is False and out["action"] == "long"


def test_no_suppression_for_no_trade():
    _seed_open_trade("OANDA:XAUUSD")
    d = {"action": "no_trade", "grade": "none", "reason": "flat"}
    out, suppressed = runtime._suppress_if_duplicate("OANDA:XAUUSD", d)
    assert suppressed is False                         # nothing to suppress


def test_followup_running_hold_is_silent(monkeypatch):
    monkeypatch.setattr(config, "DRY_RUN", True)
    _seed_open_trade()
    vision = _FakeVision({"evt-1": {"status": "running", "manage": "hold",
                                    "note": "سليمة"}})
    runtime._followup_open_trades({"symbol": "OANDA:XAUUSD", "timeframe": "3"},
                                  b"png", vision, "3")
    assert not idempotency.seen("manage:evt-1:hold")         # no message for 'hold'
