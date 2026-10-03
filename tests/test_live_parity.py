"""Research-vs-execution parity: replaying bars through LiveRunner (rolling buffer,
one bar at a time, with a restart in the middle) must reproduce run_backtest exactly."""
import numpy as np
import pandas as pd
import pytest

from tbot.data.synthetic import random_walk_bars
from tbot.engine.backtest import run_backtest
from tbot.engine.sim import ExecConfig
from tbot.instrument import load_instrument
from tbot.live.runner import LiveRunner, LiveTradingNotApproved
from tbot.risk.engine import RiskConfig
from tbot.strategies.hypotheses import H1_NYOpeningRange, H4_AsiaMeanReversion
from pathlib import Path

SPEC = load_instrument(Path(__file__).parents[1] / "configs/instrument_test.json")
RC = RiskConfig(risk_per_trade_frac=0.005, daily_loss_limit_frac=0.03, max_drawdown_frac=0.5)
EC = ExecConfig(slippage_fixed=0.02, slippage_random=0.05, seed=3)


def _trades_key(df):
    d = df[["entry_time", "side", "volume", "entry", "exit_time", "exit", "exit_reason"]].copy()
    for c in ("volume", "entry", "exit"):
        d[c] = d[c].round(8)
    return d.astype(str).values.tolist()


@pytest.mark.parametrize("strat,buf,days", [(H1_NYOpeningRange(range_min=30, stop_mode="opposite", rr=2.0), 1500, 4),
                                            (H4_AsiaMeanReversion(lookback=30, z=2.0, stop_sd=3.0), 200, 3)])
def test_replay_matches_backtest_with_restart(tmp_path, strat, buf, days):
    bars = random_walk_bars(days=days, seed=11, start="2024-03-04")
    bt = run_backtest(bars, strat.signals(bars), SPEC, RC, EC, 10000.0)
    assert len(bt.trades) > 0
    r = LiveRunner(strat, SPEC, RC, EC, 10000.0, tmp_path, buffer_bars=buf)
    half = len(bars) // 2
    for t, row in bars.iloc[:half].iterrows():
        r.on_bar(t, row)
    r = LiveRunner.resume(strat, tmp_path)           # simulated process restart
    for t, row in bars.iloc[half:].iterrows():
        r.on_bar(t, row)
    r.core.finish(bars.index[-1], bars.iloc[-1][["bid_o", "bid_h", "bid_l", "bid_c",
                                                 "ask_o", "ask_h", "ask_l", "ask_c"]].to_numpy(float))
    live = pd.DataFrame([x.__dict__ for x in r.core.broker.trades])
    assert _trades_key(live) == _trades_key(bt.trades)
    assert r.core.broker.balance == pytest.approx(bt.equity.iloc[-1])


def test_kill_switch_flattens_and_blocks(tmp_path):
    strat = H4_AsiaMeanReversion(lookback=30, z=2.0, stop_sd=3.0)
    bars = random_walk_bars(days=3, seed=11, start="2024-03-04")
    r = LiveRunner(strat, SPEC, RC, EC, 10000.0, tmp_path, buffer_bars=200)
    opened = False
    for t, row in bars.iterrows():
        r.on_bar(t, row)
        if r.core.broker.positions and not opened:
            opened = True
            (tmp_path / "KILL").write_text("stop")
    assert opened and not r.core.broker.positions
    assert r.core.risk.state.kill_switch
    assert r.core.broker.trades[-1].exit_reason in ("kill_switch", "stop", "target")
    assert r.core.decisions["kill_switch"] > 0


def test_duplicate_bar_ignored_and_reconcile(tmp_path):
    strat = H4_AsiaMeanReversion(lookback=30, z=2.0, stop_sd=3.0)
    bars = random_walk_bars(days=1, seed=1, start="2024-03-04")
    r = LiveRunner(strat, SPEC, RC, EC, 10000.0, tmp_path, buffer_bars=200)
    t, row = bars.index[0], bars.iloc[0]
    r.on_bar(t, row)
    r.on_bar(t, row)
    assert len(r.buffer) == 1
    assert r.reconcile([]) is True
    assert r.reconcile([{"side": 1, "volume": 0.1}]) is False and r.core.risk.state.kill_switch


def test_live_mode_refused_without_approval(tmp_path):
    with pytest.raises(LiveTradingNotApproved):
        LiveRunner(H4_AsiaMeanReversion(lookback=30, z=2.0, stop_sd=3.0), SPEC, RC, EC, 1.0, tmp_path, 10,
                   mode="live")
