"""Look-ahead (truncation) test for every strategy + metric correctness on known series."""
import numpy as np
import pandas as pd
import pytest

from tbot.data.synthetic import random_walk_bars
from tbot.metrics.performance import max_drawdown, longest_streak
from tbot.metrics.robustness import benjamini_hochberg, bootstrap_stats, deflated_sharpe, holm
from tbot.strategies.hypotheses import ALL

BARS = random_walk_bars(days=45, seed=7)
COLS = ["entry", "stop", "target", "exit"]


def _same(a: pd.DataFrame, b: pd.DataFrame) -> bool:
    for c in COLS:
        x, y = a[c].to_numpy(dtype=float), b[c].to_numpy(dtype=float)
        if not np.allclose(x, y, equal_nan=True):
            return False
    return True


def leak_free(strat, bars=BARS, n_signal_cuts=8, n_random=4, seed=1) -> bool:
    """Signals up to bar k must be identical whether or not future bars exist.
    Cuts are placed right AFTER rows where the full run fires (so a 1-bar look-ahead
    on the firing row is exposed) plus random cuts (to expose non-firing -> firing)."""
    rng = np.random.default_rng(seed)
    full = strat.signals(bars)
    fire = np.nonzero((full["entry"].to_numpy() != 0) | (full["exit"].to_numpy() != 0))[0]
    fire = fire[(fire > len(bars) // 4) & (fire < len(bars) - 2)]
    cuts = list(rng.choice(fire, size=min(n_signal_cuts, len(fire)), replace=False) + 1) if len(fire) else []
    cuts += list(rng.integers(len(bars) // 4, len(bars) - 2, size=n_random))
    for k in cuts:
        if not _same(full.iloc[:k], strat.signals(bars.iloc[:k])):
            return False
    return True


@pytest.mark.parametrize("cls", ALL)
def test_no_lookahead_truncation(cls):
    for params in cls.grid():
        strat = cls(**params)
        assert leak_free(strat), f"look-ahead in {strat.label()}"


@pytest.mark.parametrize("cls", ALL)
def test_signals_well_formed(cls):
    for params in cls.grid():
        s = cls(**params).signals(BARS)
        e = s["entry"].to_numpy()
        assert set(np.unique(e)) <= {-1, 0, 1}
        st = s["stop"].to_numpy()[e != 0]
        assert np.isfinite(st).all(), "every entry needs a stop"
        c = ((BARS["bid_c"] + BARS["ask_c"]) / 2).to_numpy()[e != 0]
        assert ((c - st) * e[e != 0] > 0).all(), "stop must be on the losing side"


def test_max_drawdown_known():
    eq = pd.Series([100, 120, 90, 95, 130, 110], index=pd.date_range("2024", periods=6, freq="D"))
    dd, pk, tr, rec = max_drawdown(eq)
    assert dd == pytest.approx(0.25) and pk == eq.index[1] and tr == eq.index[2] and rec == eq.index[4]


def test_streak():
    assert longest_streak(np.array([1, 1, 0, 1, 1, 1, 0])) == 3


def test_multiple_testing_corrections():
    p = [0.01, 0.04, 0.03, 0.2]
    assert holm(p) == pytest.approx([0.04, 0.09, 0.09, 0.2])
    assert benjamini_hochberg(p) == pytest.approx([0.04, 0.04 * 4 / 3, 0.04 * 4 / 3, 0.2])


def test_bootstrap_and_dsr_sanity():
    rng = np.random.default_rng(0)
    noise = rng.normal(0, 0.01, 1000)
    b = bootstrap_stats(noise, n_boot=300)
    assert b["mean_ci95"][0] < 0 < b["mean_ci95"][1]
    strong = rng.normal(0.003, 0.01, 1000)
    assert deflated_sharpe(strong, 1)["dsr"] > 0.99
    # with many trials the same noise series must not look significant
    assert deflated_sharpe(noise, 100)["dsr"] < 0.5


class _LeakyStrategy:
    """Negative control: uses the NEXT bar's close. The truncation test must catch it."""
    def signals(self, bars):
        from tbot.strategies.base import empty_signals
        c = ((bars["bid_c"] + bars["ask_c"]) / 2)
        nxt = c.shift(-1)
        s = empty_signals(bars.index)
        up = (nxt > c).to_numpy()
        s["entry"] = np.where(up, 1, 0)
        s["stop"] = np.where(up, c - 1, np.nan)
        return s


def test_truncation_test_detects_leak():
    assert not leak_free(_LeakyStrategy())


@pytest.mark.parametrize("cls", ALL)
def test_strategies_actually_trade_on_synthetic(cls):
    n = sum(int((cls(**p).signals(BARS)["entry"] != 0).sum()) for p in cls.grid())
    assert n > 0, "test would be vacuous if no signals are produced"
