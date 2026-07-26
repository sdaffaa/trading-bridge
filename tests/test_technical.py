"""Tests for the technical-analysis engine and the confluence methodology."""
from agent import technical, methodology, config


def _c(o, h, l, cl, v=0):
    return {"o": o, "h": h, "l": l, "c": cl, "v": v}


def test_sma_ema_rsi_atr():
    closes = [float(i) for i in range(1, 21)]        # 1..20 rising
    assert technical.sma(closes, 5) == sum(closes[-5:]) / 5
    assert technical.ema(closes, 5) is not None
    assert technical.rsi(closes, 14) == 100.0        # only gains -> RSI 100
    candles = [_c(i, i + 1, i - 1, i) for i in range(1, 21)]
    assert technical.atr(candles, 14) is not None


def test_swings_and_structure_bullish():
    # ascending zig-zag -> higher highs / higher lows
    seq = [10, 12, 9, 14, 11, 16, 13, 18, 15, 20, 17, 22]
    candles = [_c(p, p + 0.5, p - 0.5, p) for p in seq]
    sh, sl = technical.swings(candles, span=1)
    struct = technical.structure(sh, sl)
    assert "bullish" in struct or struct == "mixed / transition"


def test_fair_value_gap_detected():
    # create a bullish 3-candle gap: candle[i-1].high < candle[i+1].low
    candles = [_c(10, 10.2, 9.8, 10), _c(10, 12, 10, 11.5), _c(12, 12.5, 11, 12)]
    # pad to satisfy lookback window
    candles = [_c(9, 9.2, 8.8, 9)] * 5 + candles
    fvgs = technical.fair_value_gaps(candles, price=12)
    assert any(f["type"] == "bullish" for f in fvgs)


def test_volume_profile_poc_in_range():
    candles = [_c(p, p + 1, p - 1, p, v=100) for p in [10, 11, 12, 11, 10, 11, 12, 11, 10]]
    vp = technical.volume_profile(candles, bins=6)
    assert vp is not None
    assert vp["val"] <= vp["poc"] <= vp["vah"]


def test_analyze_needs_provider():
    # provider is "none" in tests -> error, not a crash
    assert "error" in technical.analyze("OANDA:XAUUSD", "240")


def test_analyze_with_stubbed_candles(monkeypatch):
    candles = [_c(p, p + 1, p - 1, p, v=100 + i)
               for i, p in enumerate([10 + (i % 5) for i in range(60)])]
    monkeypatch.setattr(technical, "get_candles", lambda s, t, limit=200: {"candles": candles})
    out = technical.analyze("OANDA:XAUUSD", "240")
    assert out["source"] == "fmp"
    assert out["trend"] in {"uptrend", "downtrend", "ranging", "unknown"}
    assert "volume_profile" in out and "market_structure" in out


def test_methodology_confluence_default():
    instr = methodology.instructions()
    assert "confluence" in instr.lower() or "four schools" in instr.lower()
    for token in ("SMC", "ICT", "Volume Profile", "order-flow"):
        assert token in instr


def test_methodology_single_school(monkeypatch):
    monkeypatch.setattr(config, "METHODOLOGY", {"ict"})
    assert "ICT lens" in methodology.instructions()


def test_methodology_subset(monkeypatch):
    monkeypatch.setattr(config, "METHODOLOGY", {"smc", "volume_profile"})
    instr = methodology.instructions()
    assert "SMC lens" in instr and "Volume Profile lens" in instr
