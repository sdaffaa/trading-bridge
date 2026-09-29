"""Calendar / session lookup tables learned on IS: hour x dow, hour, dow, month, session
open-to-now, position vs day/week/month open, previous day/week/month direction, first-hour
direction, US-data window 12:30-13:30. All keys causal (use only bars < i, or bar i's open time)."""
from common import *
import pickle

LABP = "/tmp/claude-0/-home-user-trading-bridge/b109c4cd-e10b-5fab-96f6-d6f544632108/scratchpad/labels_B.pkl"


def build_keys():
    t = IDX
    hour = t.hour.values.astype(np.int64); dow = t.dayofweek.values.astype(np.int64)
    month = t.month.values.astype(np.int64) - 1
    minute = t.minute.values.astype(np.int64)
    prevc = np.r_[O[0], C[:-1]]
    s = pd.Series(O, index=t)
    def popen(freq):
        g = t.to_period(freq) if freq != "D" else t.normalize()
        return s.groupby(g).transform("first").values
    dopen = popen("D"); wopen = popen("W"); mopen = popen("M")
    sgn = lambda x: (x > 0).astype(np.int64)
    # session: 0 Asia 23-7, 1 London 7-13, 2 NY 13-21, 3 late 21-23
    sess = np.select([(hour >= 7) & (hour < 13), (hour >= 13) & (hour < 21), (hour >= 21) & (hour < 23)], [1, 2, 3], 0)
    sid = np.cumsum(np.r_[1, (sess[1:] != sess[:-1]) | (np.diff(t.values).astype("timedelta64[m]").astype(np.int64) > 120)])
    sopen = pd.Series(O).groupby(sid).transform("first").values
    D = bars("1D")
    prevday = np.nan_to_num(htf_to_m1(np.sign(D.close - D.open), "1D"), nan=0)
    wk = M1.resample("W-SUN", label="left", closed="left").agg({"open": "first", "close": "last"}).dropna()
    wser = pd.Series(np.sign(wk.close - wk.open).values, index=wk.index + pd.Timedelta("7D"))
    prevweek = np.nan_to_num(wser.reindex(t, method="ffill").values, nan=0)
    mo = M1.resample("MS").agg({"open": "first", "close": "last"}).dropna()
    mser = pd.Series(np.sign(mo.close - mo.open).values, index=mo.index + pd.offsets.MonthBegin(1))
    prevmonth = np.nan_to_num(mser.reindex(t, method="ffill").values, nan=0)
    pd_ = (prevday > 0).astype(np.int64); pw = (prevweek > 0).astype(np.int64); pm = (prevmonth > 0).astype(np.int64)
    # first hour of UTC day direction (known from 01:00)
    day = t.normalize()
    h0 = pd.Series(np.where(hour == 0, C, np.nan), index=t).groupby(day).transform("last").values
    fh = np.where(hour >= 1, np.where(np.isnan(h0), -1, sgn(h0 - dopen)), -1)
    # London first hour 07:00-08:00
    l0 = pd.Series(np.where(hour == 7, C, np.nan), index=t).groupby(day).transform("last").values
    lo7 = pd.Series(np.where(hour == 7, O, np.nan), index=t).groupby(day).transform("first").values
    lfh = np.where(hour >= 8, np.where(np.isnan(l0) | np.isnan(lo7), -1, sgn(l0 - lo7)), -1)
    # US data window
    tod = hour * 60 + minute
    usw = (tod >= 750) & (tod < 810)
    uo = pd.Series(np.where(tod == 750, O, np.nan), index=t).groupby(day).transform("first").values
    us_key = np.where(usw & ~np.isnan(uo), 24 + 2 * sgn(prevc - np.nan_to_num(uo)) + (tod >= 780), hour)
    ad = atr(bars("1D")); ad = htf_to_m1(ad, "1D")
    dpos3 = np.where(np.isnan(ad), 1, np.where(prevc - dopen > 0.25 * ad, 2, np.where(prevc - dopen < -0.25 * ad, 0, 1)))
    K = {
        "hour": (hour, 24), "dow": (dow, 7), "month": (month, 12), "hourXdow": (hour * 7 + dow, 168),
        "min15": (hour * 4 + minute // 15, 96), "min15Xdow": ((hour * 4 + minute // 15) * 7 + dow, 672),
        "sess_sign": (sess * 2 + sgn(prevc - sopen), 8),
        "hourXsess_sign": (hour * 2 + sgn(prevc - sopen), 48),
        "vs_dopen": (sgn(prevc - dopen), 2), "vs_wopen": (sgn(prevc - wopen), 2), "vs_mopen": (sgn(prevc - mopen), 2),
        "vs_dwm": (sgn(prevc - dopen) * 4 + sgn(prevc - wopen) * 2 + sgn(prevc - mopen), 8),
        "hourXvs_dwm": (hour * 8 + sgn(prevc - dopen) * 4 + sgn(prevc - wopen) * 2 + sgn(prevc - mopen), 192),
        "hourXdpos3": (hour * 3 + dpos3, 72),
        "prevday": (pd_, 2), "prevweek": (pw, 2), "prevmonth": (pm, 2), "prevDWM": (pd_ * 4 + pw * 2 + pm, 8),
        "hourXprevday": (hour * 2 + pd_, 48), "hourXprevDWM": (hour * 8 + pd_ * 4 + pw * 2 + pm, 192),
        "dowXprevday": (dow * 2 + pd_, 14), "monthXprevmonth": (month * 2 + pm, 24),
        "firsthour": (np.where(fh >= 0, fh, -1), 2), "hourXfirsthour": (np.where(fh >= 0, hour * 2 + fh, -1), 48),
        "hourXlondonFH": (np.where(lfh >= 0, hour * 2 + lfh, -1), 48),
        "us_window": (us_key.astype(np.int64), 28),
        "hourXdowXvs_dopen": ((hour * 7 + dow) * 2 + sgn(prevc - dopen), 336),
    }
    return K


if __name__ == "__main__":
    SC = stop_configs()
    LAB = pickle.load(open(LABP, "rb"))
    K = build_keys()
    pickle.dump(K, open("/tmp/claude-0/-home-user-trading-bridge/b109c4cd-e10b-5fab-96f6-d6f544632108/scratchpad/calkeys_B.pkl", "wb"))
    log = Log("res_s3_calendar.csv")
    for kn, (keys, nk) in K.items():
        for sn, dist in SC.items():
            idx, lo, so = LAB[sn]
            dflt = default_dir(lo, so)
            for minc in (200, 1000):
                tab, lwr, swr, cnt = learn_table(keys[idx], lo, so, nk, minc=minc)
                if (tab != 0).sum() == 0:
                    continue
                d = apply_table(keys, tab, dflt)
                log.add("calendar", f"{kn}_min{minc}", sn, quick(d, dist))
        print(kn, flush=True)
    log.save()
    df = pd.DataFrame(log.rows)
    print(len(df), "variants")
    print(df[df.is_n >= 300].sort_values("is_wr", ascending=False).head(25).to_string())
