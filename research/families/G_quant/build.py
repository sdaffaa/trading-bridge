"""Rebuild any candidate position (full history, NOT masked) by name, for combos and final HOLDOUT."""
import numpy as np, pandas as pd
import common as G, signals as S

_cache = {}


def _hmm3r():
    if "hmm3r" not in _cache:
        _cache["hmm3r"] = S.hmm_expanding(3, ("r",))
    return _cache["hmm3r"]


def _garch():
    if "garch" not in _cache:
        _cache["garch"] = S.garch_vol()[0]
    return _cache["garch"]


def twap_z():
    C = G.C; day = G.TDAY
    cum = C.groupby(day.values).cumsum(); cnt = C.groupby(day.values).cumcount() + 1
    return ((C - cum / cnt) / (C * S.sigma_1h() * np.sqrt(cnt.clip(lower=1)))).where(cnt >= 3)


def raw(name):
    """unscaled forecast (before vol targeting)."""
    if name == "tsmom_ra_10d_LF": return S.mode(S.tsmom_ra(230), "LF")
    if name == "tsmom_ra_10d_LS": return S.tsmom_ra(230)
    if name == "ewmac_128_512_LF": return S.mode(S.ewmac(128), "LF")
    if name == "ewmac_128_512_LS": return S.ewmac(128)
    if name == "ewmacblend_mid_LF": return S.mode(S.blend([S.ewmac(f) for f in (32, 64, 128, 256)]), "LF")
    if name == "kf_slope_ql1.0_qs1e-05_LF": return S.mode(S.kalman(1.0, 1e-5, 1.0, "slope"), "LF")
    if name == "hmm3_r_tsmomra10d_fliphigh_LF":
        ph = S.daily_to_bars(_hmm3r()["p2"]).fillna(0)
        return S.mode(S.tsmom_ra(230), "LF") * (1 - 2 * ph)
    if name == "garchfilt_scaled_tsmomra10d_LF":
        gv = _garch(); med = gv.rolling(260, min_periods=120).median()
        return S.mode(S.tsmom_ra(230), "LF") * S.daily_to_bars((med / gv).clip(0, 2))
    if name == "ou_L240_z2.5_0.0_hurst120_LF":
        vr, hu, adf, hl = S.rolling_tests(120, 23, 48)
        return S.mode(S.band(S.zscore_dev(240), 2.5, 0.0, hu < 0.5), "LF")
    if name == "twapmom_z1.5_LS":
        return -S.band(twap_z(), 1.5, 0.0).where(~G.NY_HOUR.isin([16]), 0.0)
    if name == "bh":
        return pd.Series(1.0, index=G.C.index)
    raise KeyError(name)


def pos(name, hours=None):
    if name == "bh_vt10":
        return G.vt(raw("bh"))
    return S.to_pos(raw(name), hours=hours)


def _hmm(K, feats):
    k = f"hmm{K}{feats}"
    if k not in _cache:
        _cache[k] = S.hmm_expanding(K, feats)
    return _cache[k]


def raw2(name):
    if name == "hmm2_r_ewmac128_fliphigh_LF":
        ph = S.daily_to_bars(_hmm(2, ("r",))["p1"]).fillna(0)
        return S.mode(S.ewmac(128), "LF") * (1 - 2 * ph)
    if name == "hmm2_rv_ewmac128_cuthigh_LF":
        ph = S.daily_to_bars(_hmm(2, ("r", "lrv"))["p1"]).fillna(0)
        return S.mode(S.ewmac(128), "LF") * (1 - ph)
    if name == "kf_tstat_ql1.0_qs1e-05_LF": return S.mode(S.kalman(1.0, 1e-5, 1.0, "tstat"), "LF")
    if name == "ewmac_256_1024_LF": return S.mode(S.ewmac(256), "LF")
    raise KeyError(name)


def full_pos(name, reg_params=None):
    """position for any top-10 name; combos use the IS-fitted weights stored in the registry."""
    import json
    if name.startswith("combo_"):
        w = json.loads(reg_params)["weights"]
        return sum(v * pos(k) for k, v in w.items())
    if name.endswith("_daily16"):
        return pos(name[:-8], hours=[16])
    try:
        return pos(name)
    except KeyError:
        return S.to_pos(raw2(name))
