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

def _tf(t):
    """توحيد صيغة الفريم: `M15` و`15m` و`15` فريم واحد.

    بلا هذا التوحيد تمرّ نافذة منشورة كأنها حرّة لمجرّد أن السجل كتبها
    بصيغة أخرى — وهذا ما كاد يعيد نشر ذهب ١٥ دقيقة 2026-06-26."""
    t = str(t).strip().lower()
    unit = {"m": "m", "h": "h", "d": "d", "w": "w"}
    if t and t[0] in unit and t[1:].isdigit():        # M15 · H1 · D1
        return t[1:] + unit[t[0]]
    if t.isdigit():                                    # 15
        return t + "m"
    return t


def _ov(a0, a1, b0, b1):
    """تقاطع مدَيين زمنيين بمقارنة نصّية بعد قصّ اللاحقة الزمنية.

    السجل يخلط `2026-06-26T06:00` مع `2026-06-26 06:00+00:00`؛ المقارنة
    النصّية الخام تجعلهما لا يتقاطعان.

    والطرفان يُرتَّبان قبل المقارنة: نوافذ تعبر منتصف الليل تصل مقلوبة
    (`20:00..07:00`)، والمقارنة الخام كانت تمرّرها كأنها حرّة — فمرّت
    نافذة منشورة في run36 مرّة أخرى."""
    n = lambda s: str(s).replace("T", " ")[:16]
    a0, a1 = sorted((n(a0), n(a1)))
    b0, b1 = sorted((n(b0), n(b1)))
    return not (a1 < b0 or a0 > b1)


def assert_fresh_real(symbol, timeframe, start, end, label=""):
    d = _load()
    for e in d["real"]:
        if e["symbol"].split("=")[0] == symbol.split("=")[0] \
                and _tf(e["timeframe"]) == _tf(timeframe) \
                and _ov(start, end, e["start"], e["end"]):
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
