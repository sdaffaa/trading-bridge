"""Regression tests for the independent review findings (reports/REVIEW_1.md), one per defect."""
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from tbot.data.synthetic import make_bars, random_walk_bars
from tbot.engine.backtest import TradingCore, run_backtest
from tbot.engine.sim import ExecConfig
from tbot.instrument import load_instrument
from tbot.metrics.performance import summarize
from tbot.research.walkforward import ABSTAIN, Fold, in_days, make_folds, walk_forward
from tbot.risk.engine import RiskConfig
from tbot.strategies.base import empty_signals
from tbot.strategies.hypotheses import (H1_NYOpeningRange, H2_LondonAsianBreakout, H3_IntradayMomentum,
                                        H5_TimeOfDayDrift)

SPEC = load_instrument(Path(__file__).parents[1] / "configs/instrument_test.json")
RC = RiskConfig(risk_per_trade_frac=0.005, daily_loss_limit_frac=0.05, max_drawdown_frac=0.9)
BARS = random_walk_bars(days=60, seed=5, start="2024-02-01")
P = ["bid_o", "bid_h", "bid_l", "bid_c", "ask_o", "ask_h", "ask_l", "ask_c"]


def _ny(ts):
    return pd.DatetimeIndex(ts).tz_convert("America/New_York")


@pytest.mark.parametrize("strat", [H1_NYOpeningRange(range_min=10, stop_mode="opposite", rr=0),
                                   H2_LondonAsianBreakout(buffer=0.0, stop_mode="opposite", rr=0),
                                   H3_IntradayMomentum(decision=600, k=0.0, stop_atr=1.0)])
def test_d1_intraday_hypotheses_flat_by_1631_same_day(strat):
    r = run_backtest(BARS, strat.signals(BARS), SPEC, RC, ExecConfig(), 10000)
    t = r.trades
    assert len(t) > 5
    ex = _ny(t["exit_time"])
    assert ((ex.hour * 60 + ex.minute) <= 16 * 60 + 31).all()
    from tbot.data.bars import trading_day
    assert (pd.to_datetime(trading_day(pd.DatetimeIndex(t["exit_time"]))) == t["entry_day"].values).all()
    assert (t["swap"] == 0).all()
    assert ((t["exit_time"] - t["entry_time"]) < pd.Timedelta(hours=15)).all()   # London open -> 16:30 NY is ~14h


def test_d2_h5_robust_to_missing_minute_bars():
    s = H5_TimeOfDayDrift(window=(8, 12), side=1)
    ny = _ny(BARS.index)
    holes = BARS[~(((ny.hour == 11) & (ny.minute == 59)) | ((ny.hour == 8) & (ny.minute == 4)))]
    r = run_backtest(holes, s.signals(holes), SPEC, RC, ExecConfig(), 10000)
    assert len(r.trades) > 10
    assert ((r.trades["exit_time"] - r.trades["entry_time"]) < pd.Timedelta(hours=5)).all()


def test_d3_rejected_closes_are_retried():
    s = H5_TimeOfDayDrift(window=(8, 12), side=1)
    r = run_backtest(BARS, s.signals(BARS), SPEC, RC, ExecConfig(reject_prob=0.5, seed=1), 10000)
    assert r.decisions["broker_rejected"] > 0
    assert ((r.trades["exit_time"] - r.trades["entry_time"]) < pd.Timedelta(hours=5)).all()


def _core(**kw):
    return TradingCore(SPEC, RiskConfig(risk_per_trade_frac=0.01, fixed_volume=0.1, max_drawdown_frac=0.9,
                                        daily_loss_limit_frac=0.5), ExecConfig(**kw), 10000.0)


def test_d4_kill_cancels_pending_entry_and_flattens_late_fill():
    b = make_bars([100] * 10)
    c = _core(latency_bars=1)
    day = pd.Timestamp("2024-01-02").date()
    for i, (t, row) in enumerate(b.iterrows()):
        c.step(t, row[P].to_numpy(float), day, entry=1 if i == 0 else 0, stop=95.0, kill_switch=i >= 1)
    assert not c.broker.positions and not c.broker.pending
    assert c.decisions["entry_cancelled_halt"] == 1


def test_d5_reconcile_style_kill_flattens_open_position():
    b = make_bars([100] * 10)
    c = _core()
    day = pd.Timestamp("2024-01-02").date()
    for i, (t, row) in enumerate(b.iterrows()):
        if i == 3:
            assert c.broker.positions
            c.risk.trigger_kill_switch(t)          # what LiveRunner.reconcile does on mismatch
        c.step(t, row[P].to_numpy(float), day, entry=1 if i == 0 else 0, stop=95.0)
    assert not c.broker.positions
    assert c.broker.trades[-1].exit_reason == "kill_switch"


def test_d6_pending_entries_count_against_limits():
    b = make_bars([100] * 10)
    s = empty_signals(b.index)
    for i in (0, 1):
        s.iloc[i, s.columns.get_loc("entry")] = 1
        s.iloc[i, s.columns.get_loc("stop")] = 95.0
    rc = RiskConfig(risk_per_trade_frac=0.01, max_open_positions=1, max_trades_per_day=1, max_drawdown_frac=0.9)
    r = run_backtest(b, s, SPEC, rc, ExecConfig(latency_bars=1), 10000)
    assert r.decisions["filled"] == 1
    assert r.decisions["max_trades_per_day"] + r.decisions["max_open_positions"] == 1


def test_d7_walk_forward_abstains_when_nothing_qualifies():
    days = pd.date_range("2020-01-01", "2020-12-31", freq="B")
    d = pd.DataFrame({"ret": 0.001, "pnl": 10.0, "active": True}, index=days)
    grid = [({"p": 0}, d, pd.DataFrame(), {}), ({"p": 1}, d, pd.DataFrame(), {})]
    tab, oos = walk_forward(grid, [Fold("2020-01-01", "2020-06-30", "2020-07-01", "2020-12-31")], min_trades=30)
    assert tab.iloc[0]["chosen"] == ABSTAIN
    assert (oos["ret"] == 0).all() and (oos["pnl"] == 0).all()


def test_d8_embargo_and_trading_day_assignment():
    f = make_folds("2016-01-01", "2019-01-01", "2019-07-01", 6, 36, embargo_days=1)[0]
    assert pd.Timestamp(f.train_end) == pd.Timestamp("2018-12-30")   # 2018-12-31 left unused
    # trade entered Sunday 22:05 UTC belongs to Monday's trading day
    t = pd.DataFrame({"entry_day": [pd.Timestamp("2019-07-01")], "net": [1.0], "planned_risk": [1.0]})
    assert len(in_days(t, "2019-07-01", "2020-01-01")) == 1 and len(in_days(t, "2019-01-01", "2019-07-01")) == 0
    r = run_backtest(make_bars([100] * 5, start="2019-06-30 22:05"),
                     empty_signals(make_bars([100] * 5, start="2019-06-30 22:05").index).assign(
                         entry=[1, 0, 0, 0, 0], stop=[95, np.nan, np.nan, np.nan, np.nan]),
                     SPEC, RC, ExecConfig(), 10000)
    assert r.trades.iloc[0]["entry_day"] == pd.Timestamp("2019-07-01")


def test_d9_sortino_uses_downside_deviation():
    class R:  # minimal BacktestResult stand-in
        pass
    d = pd.DataFrame({"equity_end": [101.0, 100.0, 102.0, 101.5]},
                     index=pd.date_range("2024-01-01", periods=4, freq="D"))
    d["active"], d["pnl"] = True, d["equity_end"].diff().fillna(1.0)
    r = R()
    r.trades, r.daily, r.equity = pd.DataFrame(), d, d["equity_end"]
    r.exposure_bars, r.n_bars, r.max_margin_used, r.n_ambiguous, r.decisions, r.risk_events = 0, 1, 0, 0, {}, []
    m = summarize(r, 100.0)
    x = d["equity_end"] / d["equity_end"].shift(1).fillna(100.0) - 1
    dd = np.sqrt(np.mean(np.minimum(x, 0) ** 2))
    assert m["sortino_ann"] == pytest.approx(x.mean() / dd * np.sqrt(260))


def test_d10_research_slice_by_trading_day(tmp_path):
    import sys
    sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))
    from run_research import load_parquets
    b = make_bars([100] * 180, start="2024-06-30 20:00", freq="1min")
    b.to_parquet(tmp_path / "x.parquet")
    out = load_parquets(tmp_path, "2024-01-01", "2024-07-01")
    assert len(out) == 60                                                  # 20:00-20:59 UTC only
    assert out.index.max() < pd.Timestamp("2024-06-30 21:00", tz="UTC")   # 17:00 EDT cutoff


def test_d11_peak_equity_tracked_on_close_not_bar_low():
    c = _core()
    b = make_bars([100, 100, (100, 100, 90, 100), 100])
    day = pd.Timestamp("2024-01-02").date()
    for i, (t, row) in enumerate(b.iterrows()):
        c.step(t, row[P].to_numpy(float), day, entry=1 if i == 0 else 0, stop=50.0)
    assert c.risk.state.peak_equity == pytest.approx(10000.0)
