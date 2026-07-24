"""Arabic trade formatting + open-trade follow-up (the feedback loop)."""
from agent import config, store
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
    vision = _FakeVision({"evt-1": {"status": "running", "note": "ما زالت جارية"}})
    runtime._followup_open_trades({"symbol": "OANDA:XAUUSD", "timeframe": "15"},
                                  b"png", vision, "15")
    assert len(store.open_trades("OANDA:XAUUSD")) == 1   # still open
