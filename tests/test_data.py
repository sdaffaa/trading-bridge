import numpy as np
import pandas as pd
import pytest

from tbot.data.dukascopy import decode_bi5, encode_bi5, ticks_to_bars
from tbot.data.quality import quality_report
from tbot.data.synthetic import random_walk_bars


def test_bi5_roundtrip_and_bars():
    h = pd.Timestamp("2024-03-05 14:00", tz="UTC")
    ticks = pd.DataFrame({"ask": [2100.155, 2100.255, 2099.905], "bid": [2099.905, 2100.005, 2099.655],
                          "ask_vol": [1.0, 2.0, 1.5], "bid_vol": [1.0, 1.0, 1.0]},
                         index=[h + pd.Timedelta(seconds=s) for s in (1, 30, 75)])
    dec = decode_bi5(encode_bi5(ticks, h, 1000.0), h, 1000.0)
    assert np.allclose(dec["ask"], ticks["ask"]) and np.allclose(dec["bid"], ticks["bid"])
    assert list(dec.index) == list(ticks.index)
    bars = ticks_to_bars(dec)
    assert len(bars) == 2
    assert bars.iloc[0].bid_h == pytest.approx(2100.005) and bars.iloc[0].ask_c == pytest.approx(2100.255)
    assert bars.iloc[0].ticks == 2
    assert bars.iloc[1].max_spread == pytest.approx(0.25)


def test_quality_report_on_clean_and_corrupted():
    b = random_walk_bars(days=21, seed=2)
    rep = quality_report(b)
    assert rep["structural_errors"] == [] and rep["duplicates"] == 0
    assert rep["coverage"] > 0.99 and rep["bars_outside_expected_session"] == 0
    assert rep["share_bars_in_17h_NY_winter"] == 0.0
    bad = b.drop(b.index[5000:5100])
    bad = pd.concat([bad, bad.iloc[[10]]]).sort_index()
    rep2 = quality_report(bad)
    assert rep2["duplicates"] == 1 and rep2["gaps_gt5m_in_session"] >= 1 and rep2["verdict"] == "FAIL"
