# Scan real market data for bullish OB-retest patterns (3 classes) for pattern sheets.
# Runs inside sandbox_exec (open internet). Output: JSON rows for sheet_build.py.
import json, sys, os, urllib.request, urllib.parse, datetime as dt

def fetch(sym, iv):
    rng = "1y" if iv == "1h" else "60d"
    fp = "/home/user/y_" + sym.replace("=", "_").replace("^", "_") + "_" + iv + ".json"
    if os.path.exists(fp):
        d = json.load(open(fp))
    else:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{urllib.parse.quote(sym)}?interval={iv}&range={rng}"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Accept": "*/*"})
        d = json.load(urllib.request.urlopen(req, timeout=45))
    r = d["chart"]["result"][0]
    ts = r["timestamp"]; q = r["indicators"]["quote"][0]
    out = []; last = 0
    for i, t in enumerate(ts):
        o, h, l, c = q["open"][i], q["high"][i], q["low"][i], q["close"][i]
        if None in (o, h, l, c) or t <= last: continue
        o, h, l, c = (round(v, 6) for v in (o, h, l, c))
        h = max(o, h, l, c); l = min(o, h, l, c)
        if h == l: continue
        out.append(dict(ts=t, o=o, h=h, l=l, c=c)); last = t
    return out

def swings(cs, idxs, key, cmpmax):
    out = []
    for k in range(1, len(idxs) - 1):
        a, b, c = idxs[k-1], idxs[k], idxs[k+1]
        v = cs[b][key]
        if cmpmax and v >= cs[a][key] and v >= cs[c][key]: out.append(b)
        if not cmpmax and v <= cs[a][key] and v <= cs[c][key]: out.append(b)
    return out

def classify(cs, bk, r, ztop, relax):
    """return ALL pattern classes this pullback matches"""
    pb = list(range(bk, r + 1))
    dep = cs[bk]["h"] - ztop
    if dep <= 0: return []
    out = []
    sh = swings(cs, pb, "h", True); sl = swings(cs, pb, "l", False)
    # sweep: top1 then equal-or-higher top2, then decline
    tol = (0.32 if relax else 0.22) * dep
    tops = sorted(pb, key=lambda i: -cs[i]["h"])[:4]
    for i1 in sorted(tops):
        done = False
        for i2 in sorted(tops):
            if i2 < i1 + 3: continue
            h1, h2 = cs[i1]["h"], cs[i2]["h"]
            if h1 - tol <= h2 <= h1 + tol and max(cs[k]["h"] for k in pb) <= max(h1, h2):
                if r - i2 >= 2 and i1 - bk <= len(pb) * 0.6:
                    ipdl = min(range(i1, i2 + 1), key=lambda k: cs[k]["l"])
                    out.append(dict(cls="sweep", i1=i1, i2=i2, ipdl=ipdl)); done = True; break
        if done: break
    # consolidation: flat sub-range then drop
    need = 5 if relax else 6
    best = None
    for a in range(1, len(pb) - need):
        for b in range(len(pb) - 2, a + need - 2, -1):
            seg = pb[a:b+1]
            rt = max(cs[k]["h"] for k in seg); rb = min(cs[k]["l"] for k in seg)
            if (rt - rb) < (0.55 if relax else 0.45) * dep and rb > ztop + 0.15 * dep:
                if best is None or len(seg) > best[1] - best[0] + 1: best = (seg[0], seg[-1])
                break
    if best:
        out.append(dict(cls="consol", ca=best[0], cb=best[1],
                        rt=max(range(best[0], best[1]+1), key=lambda k: cs[k]["h"]),
                        rb=min(range(best[0], best[1]+1), key=lambda k: cs[k]["l"])))
    # channel: swing highs & lows stepping down, small violations tolerated
    if len(sh) >= 2 and len(sl) >= 2 and len(pb) >= (6 if relax else 8):
        ok_h = (cs[sh[-1]]["h"] < cs[sh[0]]["h"] - 0.15 * dep and
                all(cs[sh[k+1]]["h"] <= cs[sh[k]]["h"] + 0.08 * dep for k in range(len(sh)-1)))
        ok_l = (cs[sl[-1]]["l"] < cs[sl[0]]["l"] - 0.10 * dep and
                all(cs[sl[k+1]]["l"] <= cs[sl[k]]["l"] + 0.08 * dep for k in range(len(sl)-1)))
        if ok_h and ok_l:
            out.append(dict(cls="chan", chi=[sh[0], sh[-1]], clo=[sl[0], sl[-1]]))
    return out

def scan(cs, sym, tf, sec, relax=False):
    res = []; n = len(cs)
    for bk in range(25, n - 14):
        seg = range(bk - 20, bk - 2)
        iH = max(seg, key=lambda i: cs[i]["h"]); lv = cs[iH]["h"]
        if cs[bk]["c"] <= lv or cs[bk-1]["c"] > lv: continue
        if max(cs[i+1]["ts"] - cs[i]["ts"] for i in range(bk-22, min(bk+22, n-1))) > 6 * sec: continue
        il = min(range(iH, bk), key=lambda i: cs[i]["l"])
        if il <= iH + 1: continue
        obs = [i for i in range(max(iH, il-2), min(il+3, bk)) if cs[i]["c"] < cs[i]["o"]]
        if not obs: continue
        iob = obs[-1]
        ztop = cs[iob]["o"]; zbot = cs[iob]["l"]; zh = ztop - zbot
        if zh <= 0 or cs[bk]["c"] - ztop < 1.2 * zh: continue
        r = None
        for k in range(bk + 4, min(bk + 30, n - 9)):
            if cs[k]["l"] <= ztop:
                if cs[k]["c"] > zbot and cs[k]["l"] > zbot - 0.5*zh: r = k
                break
        if not r: continue
        hi_after = max(cs[k]["h"] for k in range(r + 1, min(r + 10, n)))
        if hi_after < cs[bk]["h"]: continue
        if min(cs[k]["l"] for k in range(r, min(r + 10, n))) < zbot - 0.2*zh: continue
        infos = classify(cs, bk, r, ztop, relax)
        touch = (ztop - cs[r]["l"]) / zh
        if touch > 0.7: continue
        score = (hi_after - cs[bk]["h"]) / zh - touch + min(r - bk, 14) * 0.05
        for info in infos:
            info = dict(info)
            info.update(sym=sym, tf=tf, iH=iH, bk=bk, iob=iob, ir=r, s=round(score, 3))
            res.append(info)
    return res

KW = dt.timezone(dt.timedelta(hours=3))
SRC = [("GC=F", "30m", 1800), ("YM=F", "30m", 1800), ("NQ=F", "30m", 1800),
       ("GBPUSD=X", "15m", 900), ("USDJPY=X", "15m", 900), ("GC=F", "15m", 900),
       ("GC=F", "1h", 3600), ("YM=F", "1h", 3600), ("NQ=F", "1h", 3600),
       ("GBPUSD=X", "1h", 3600), ("USDJPY=X", "1h", 3600), ("AUDUSD=X", "1h", 3600)]
allc = {}; series = {}
for sym, iv, sec in SRC:
    cs = fetch(sym, iv)
    series[(sym, iv)] = cs
    for relax in (False, True):
        cands = scan(cs, sym, iv, sec, relax)
        for c in cands: c["relax"] = relax
        allc.setdefault((sym, iv), []).extend(cands)
    kinds = {}
    for c in allc[(sym, iv)]: kinds[c["cls"]] = kinds.get(c["cls"], 0) + 1
    print(f"{sym} {iv}: {len(cs)} candles, {sorted(kinds.items())}", file=sys.stderr)

chosen = []; used_syms = set()
for cls in ("chan", "consol", "sweep"):
    pool = [c for v in allc.values() for c in v if c["cls"] == cls]
    pool.sort(key=lambda c: (c["relax"], -c["s"]))
    pick = next((c for c in pool if c["sym"] not in used_syms), pool[0] if pool else None)
    if pick:
        used_syms.add(pick["sym"]); chosen.append(pick)
    else:
        print(f"NO CANDIDATE for {cls}", file=sys.stderr)

rows = []
for c in chosen:
    cs = series[(c["sym"], c["tf"])]
    ws = max(0, c["iH"] - 5)
    ee = c["ir"] + 1
    while ee < len(cs) - 1 and cs[ee]["h"] < cs[c["bk"]]["h"] and ee - c["ir"] < 9: ee += 1
    we = min(len(cs) - 1, ee + 3, ws + 41)
    w = []
    for cd in cs[ws:we+1]:
        k = dt.datetime.fromtimestamp(cd["ts"], KW)
        w.append(dict(d=f"{k.hour:02d}:{k.minute:02d}", o=cd["o"], h=cd["h"], l=cd["l"], c=cd["c"]))
    row = dict(cls=c["cls"], sym=c["sym"], tf=c["tf"], w=w,
               date=dt.datetime.fromtimestamp(cs[c["ir"]]["ts"], KW).strftime("%Y-%m-%d"),
               su=dt.datetime.fromtimestamp(cs[ws]["ts"], dt.timezone.utc).isoformat(),
               eu=dt.datetime.fromtimestamp(cs[we]["ts"], dt.timezone.utc).isoformat(),
               relax=c["relax"])
    for key in ("iH", "bk", "iob", "ir", "i1", "i2", "ipdl", "ca", "cb", "rt", "rb"):
        if key in c: row[key] = c[key] - ws
    for key in ("chi", "clo"):
        if key in c: row[key] = [v - ws for v in c[key]]
    rows.append(row)

print(f"chosen: {[(r['cls'], r['sym'], r['tf'], r['date'], len(r['w'])) for r in rows]}", file=sys.stderr)
print(json.dumps(rows, ensure_ascii=False))
