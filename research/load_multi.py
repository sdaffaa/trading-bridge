"""Load HistData M1 (EST, UTC-5 fixed) 2014-2025 + Tickstory M1 for 2026 into one UTC frame."""
import glob, os
import pandas as pd
D = "/tmp/claude-0/-home-user-trading-bridge/b109c4cd-e10b-5fab-96f6-d6f544632108/scratchpad/moredata"
CACHE = D + "/xau_m1_2014_2026.parquet"

def load_multi():
    if os.path.exists(CACHE):
        return pd.read_parquet(CACHE)
    parts = []
    for y in range(2014, 2026):
        df = pd.read_csv(f"{D}/DAT_MT_XAUUSD_M1_{y}.csv", header=None,
                         names=["d", "t", "open", "high", "low", "close", "v"])
        df.index = pd.to_datetime(df.d + " " + df.t, format="%Y.%m.%d %H:%M") + pd.Timedelta(hours=5)
        parts.append(df[["open", "high", "low", "close"]])
    ts = pd.read_csv(glob.glob(f"{D}/XAUUSD_M1_tickstory*.csv")[0])
    ts.index = pd.to_datetime(ts.Date.astype(str) + " " + ts.Timestamp, format="%Y%m%d %H:%M:%S")
    ts.columns = [c.lower() for c in ts.columns]
    parts.append(ts.loc["2026-01-01":, ["open", "high", "low", "close"]])
    m1 = pd.concat(parts)
    m1 = m1[~m1.index.duplicated()].sort_index().astype(float)
    m1.to_parquet(CACHE)
    return m1

if __name__ == "__main__":
    m1 = load_multi()
    print(len(m1), m1.index[0], m1.index[-1])
    print(m1.close.resample("YE").last().round(0).to_dict())
