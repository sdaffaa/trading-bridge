"""Code-correctness tests on hand-computed synthetic cases (NOT profitability evidence)."""
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from tbot.data.bars import trading_day, validate_bars
from tbot.data.synthetic import make_bars
from tbot.engine.backtest import run_backtest
from tbot.engine.sim import ExecConfig, Order, SimBroker
from tbot.instrument import load_instrument
from tbot.risk.engine import RiskConfig, RiskEngine
from tbot.strategies.base import empty_signals

SPEC = load_instrument(Path(__file__).parents[1] / "configs/instrument_test.json")
RC = RiskConfig(risk_per_trade_frac=0.01, fixed_volume=0.1, daily_loss_limit_frac=0.5, max_drawdown_frac=0.9)


def sig_for(bars, at=0, side=1, stop=95.0, target=102.0, exits=()):
    s = empty_signals(bars.index)
    s.iloc[at, s.columns.get_loc("entry")] = side
    s.iloc[at, s.columns.get_loc("stop")] = stop
    s.iloc[at, s.columns.get_loc("target")] = target
    for e in exits:
        s.iloc[e, s.columns.get_loc("exit")] = 1
    return s


def run(bars, sig, rc=RC, ec=None, bal=10000.0):
    return run_backtest(bars, sig, SPEC, rc, ec or ExecConfig(), bal, keep_log=True)


def test_volume_floor():
    assert SPEC.floor_volume(0.0967) == 0.09
    assert SPEC.floor_volume(0.009) == 0.0
    assert SPEC.floor_volume(0.03) == 0.03   # float-safe
    assert SPEC.floor_volume(1e9) == 100


def test_long_target_exact_pnl():
    b = make_bars([100, 100, (100, 102.5, 99.9, 102), 102])
    r = run(b, sig_for(b))
    t = r.trades.iloc[0]
    assert t.entry == pytest.approx(100.1) and t.exit == pytest.approx(102.0)
    assert t.exit_reason == "target"
    assert t.gross == pytest.approx(19.0) and t.commission == pytest.approx(0.7)
    assert t.net == pytest.approx(18.3)
    assert r.equity.iloc[-1] == pytest.approx(10018.3)


def test_stop_gap_fills_at_open_not_stop():
    b = make_bars([100, 100, (94, 94.5, 93, 94), 94])
    t = run(b, sig_for(b)).trades.iloc[0]
    assert t.exit == pytest.approx(93.9) and t.exit_reason == "stop"
    assert t.net == pytest.approx(-62.7)


def test_intrabar_ambiguity_worst_and_best():
    b = make_bars([100, 100, (100, 103, 94, 100), 100])
    worst = run(b, sig_for(b)).trades.iloc[0]
    best = run(b, sig_for(b), ec=ExecConfig(intrabar="best")).trades.iloc[0]
    assert worst.exit_reason == "stop" and worst.gross == pytest.approx(-51.0) and worst.ambiguous
    assert best.exit_reason == "target" and best.gross == pytest.approx(19.0)


def test_short_uses_ask_for_stops():
    # short at bid 99.9; ask high reaches 101.1 >= stop 101 -> stopped at 101
    b = make_bars([100, 100, (100, 101.0, 99.5, 100), 100])
    t = run(b, sig_for(b, side=-1, stop=101.0, target=90.0)).trades.iloc[0]
    assert t.entry == pytest.approx(99.9) and t.exit == pytest.approx(101.0)
    assert t.gross == pytest.approx(-11.0)


def test_round_trip_costs_spread_and_commission():
    b = make_bars([100] * 5)
    t = run(b, sig_for(b, target=np.nan, exits=(1,))).trades.iloc[0]
    assert t.net == pytest.approx(-(0.2 * 10 + 0.7))
    assert t.spread_cost == pytest.approx(2.0)


def test_swap_triple_wednesday_rollover():
    # 2024-01-03 is a Wednesday; 17:00 NY = 22:00 UTC in January
    b = make_bars([100] * 10, start="2024-01-03 21:55")
    t = run(b, sig_for(b, target=np.nan, exits=(8,))).trades.iloc[0]
    assert t.swap == pytest.approx(-10 * 0.1 * 3)
    assert t.net == pytest.approx(-2.7 - 3.0)


def test_latency_and_slippage():
    b = make_bars([100, 100, 101, 101, 101, 101])
    t = run(b, sig_for(b, target=np.nan, exits=(3,)),
            ec=ExecConfig(latency_bars=1, slippage_fixed=0.05)).trades.iloc[0]
    assert t.entry == pytest.approx(101.1 + 0.05)   # decided bar0 -> +1 bar latency -> bar2 open + slip
    assert t.exit == pytest.approx(100.9 - 0.05)    # exit decided bar3 -> bar5 open - slip
    assert t.exit_time == b.index[5]


def test_rejection_and_partial_fill():
    b = make_bars([100] * 5)
    r = run(b, sig_for(b, target=np.nan), ec=ExecConfig(reject_prob=1.0))
    assert len(r.trades) == 0 and r.decisions["broker_rejected"] == 1
    r2 = run(b, sig_for(b, target=np.nan, exits=(2,)), ec=ExecConfig(max_fill_volume=0.04))
    assert r2.trades.iloc[0].volume == pytest.approx(0.04)


def test_stale_order_expires_over_gap():
    idx = list(pd.date_range("2024-01-02 14:00", periods=2, freq="1min", tz="UTC")) + \
        [pd.Timestamp("2024-01-02 16:00", tz="UTC")]
    b = make_bars([100, 100, 100]).set_axis(pd.DatetimeIndex(idx))
    s = sig_for(b, at=1, target=np.nan)
    r = run(b, s)
    assert len(r.trades) == 0
    assert any(e["ev"] == "expired" for e in r.broker_log)


def test_risk_sizing_rounds_down_and_rejects_below_min():
    re_ = RiskEngine(SPEC, RiskConfig(risk_per_trade_frac=0.005))
    re_.on_new_day(None, 10000)
    d = re_.size_order(side=1, ref_price=100.1, stop=95.0, spread=0.2, equity=10000, open_positions=[], open_risk=0)
    assert d.reason == "ok" and d.volume == pytest.approx(0.09)
    assert d.planned_risk <= 50.0 + 1e-9
    d2 = re_.size_order(side=1, ref_price=100.1, stop=-900, spread=0.2, equity=10000, open_positions=[], open_risk=0)
    assert d2.reason in ("below_min_volume", "volume_exceeds_risk_budget")
    d3 = re_.size_order(side=1, ref_price=100.1, stop=101, spread=0.2, equity=10000, open_positions=[], open_risk=0)
    assert d3.reason == "stop_wrong_side"
    re2 = RiskEngine(SPEC, RiskConfig(max_spread=0.1))
    re2.on_new_day(None, 10000)
    assert re2.size_order(side=1, ref_price=100.1, stop=95, spread=0.2, equity=10000, open_positions=[],
                          open_risk=0).reason == "spread_too_wide"


def test_daily_loss_limit_flattens_and_blocks():
    # 0.4 lot, price falls 3 -> loss ~ 128 > 1% of 10000 -> flatten next open; later signal blocked
    rc = RiskConfig(risk_per_trade_frac=0.05, max_total_risk_frac=0.05, fixed_volume=0.4, daily_loss_limit_frac=0.01,
                    max_drawdown_frac=0.5, max_margin_usage=1.0)
    b = make_bars([100, 100, (100, 100, 97, 97), 97, 97, 97])
    s = sig_for(b, stop=90, target=np.nan)
    s.iloc[4, s.columns.get_loc("entry")] = 1
    s.iloc[4, s.columns.get_loc("stop")] = 90
    r = run(b, s, rc=rc)
    assert r.trades.iloc[0].exit_reason == "risk_halt"
    assert r.decisions["daily_halted"] == 1
    assert any(e[1] == "daily_halt" for e in r.risk_events)


def test_duplicate_order_rejected():
    br = SimBroker(SPEC, ExecConfig(), 1000)
    t = pd.Timestamp("2024-01-02", tz="UTC")
    assert br.submit(Order("x", "entry", 1, 0.01, t))
    assert not br.submit(Order("x", "entry", 1, 0.01, t))


def test_trading_day_dst():
    idx = pd.DatetimeIndex(["2024-07-10 20:59", "2024-07-10 21:00", "2024-01-10 21:30", "2024-01-10 22:00"],
                           tz="UTC")
    d = trading_day(idx)
    assert str(d[0]) == "2024-07-10" and str(d[1]) == "2024-07-11"   # EDT: 17:00 NY = 21:00 UTC
    assert str(d[2]) == "2024-01-10" and str(d[3]) == "2024-01-11"   # EST: 17:00 NY = 22:00 UTC


def test_validate_bars_catches_bad_data():
    b = make_bars([100, 100])
    assert validate_bars(b) == []
    bad = b.copy()
    bad.iloc[0, bad.columns.get_loc("bid_h")] = 50
    assert any("inconsistent" in e for e in validate_bars(bad))
