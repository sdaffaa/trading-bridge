# -*- coding: utf-8 -*-
"""Permanent chart registry — no chart may EVER be reused across videos.

Every synthetic teaching chart is fingerprinted by (seed, anchors); every
real-data chart by (symbol, timeframe, date range). Builders MUST call
`assert_fresh()` for each chart before rendering, then `register()` after the
video ships. The ledger lives in used_charts.json next to this file and is
committed to the repo, so the ban survives across sessions and machines.
"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
LEDGER = os.path.join(HERE, "used_charts.json")

def _load():
    if os.path.exists(LEDGER):
        with open(LEDGER, encoding="utf-8") as f:
            return json.load(f)
    return {"synthetic": [], "real": []}

def _save(d):
    with open(LEDGER, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=1)

def _syn_key(seed, anchors):
    return {"seed": seed, "anchors": [list(a) for a in anchors]}

def assert_fresh_synthetic(seed, anchors, label=""):
    d = _load()
    for e in d["synthetic"]:
        if e["seed"] == seed:
            raise ValueError(f"chart seed {seed} already used in '{e['video']}' — pick a new seed ({label})")
        if e["anchors"] == [list(a) for a in anchors]:
            raise ValueError(f"chart anchors already used in '{e['video']}' — reshape the scenario ({label})")

def assert_fresh_real(symbol, timeframe, start, end, label=""):
    d = _load()
    for e in d["real"]:
        if e["symbol"] == symbol and e["timeframe"] == timeframe and not (end < e["start"] or start > e["end"]):
            raise ValueError(f"real window {symbol} {timeframe} {start}..{end} overlaps '{e['video']}' — fetch a different period/instrument ({label})")

def register_synthetic(video, charts):
    """charts: list of (seed, anchors, label)"""
    d = _load()
    for seed, anchors, label in charts:
        d["synthetic"].append({**_syn_key(seed, anchors), "label": label, "video": video})
    _save(d)

def register_real(video, symbol, timeframe, start, end, label=""):
    d = _load()
    d["real"].append({"symbol": symbol, "timeframe": timeframe, "start": start, "end": end,
                      "label": label, "video": video})
    _save(d)

if __name__ == "__main__":
    d = _load()
    print(f"ledger: {len(d['synthetic'])} synthetic, {len(d['real'])} real windows")
    for e in d["synthetic"]:
        print(f"  seed {e['seed']:>4}  {e['video']} :: {e['label']}")
    for e in d["real"]:
        print(f"  {e['symbol']} {e['timeframe']} {e['start']}..{e['end']}  {e['video']}")
