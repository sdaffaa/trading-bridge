import json, sys, urllib.request, datetime as dt

PIP = 1e-4
def r5(v): return round(v, 5)

def fetch(iv):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/EURUSD=X?interval={iv}&range=60d"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    d = json.load(urllib.request.urlopen(req, timeout=45))
    r = d["chart"]["result"][0]
    ts = r["timestamp"]; q = r["indicators"]["quote"][0]
    out = []; last = 0
    for i, t in enumerate(ts):
        o, h, l, c = q["open"][i], q["high"][i], q["low"][i], q["close"][i]
        if None in (o, h, l, c) or t <= last: continue
        o, h, l, c = r5(o), r5(h), r5(l), r5(c)
        h = max(o, h, l, c); l = min(o, h, l, c)
        if h == l: continue
        out.append(dict(ts=t, o=o, h=h, l=l, c=c)); last = t
    return out

def profile(cands, nbins=22):
    hi = max(c["h"] for c in cands); lo = min(c["l"] for c in cands)
    bh = (hi - lo) / nbins; vols = [0.0] * nbins
    for c in cands:
        rng = max(c["h"] - c["l"], 1e-9)
        b0 = max(0, int((c["l"] - lo) / bh)); b1 = min(nbins - 1, int((c["h"] - lo) / bh))
        for b in range(b0, b1 + 1):
            slo = lo + b * bh; shi = slo + bh
            ov = min(c["h"], shi) - max(c["l"], slo)
            if ov > 0: vols[b] += ov / rng
    poc = max(range(nbins), key=lambda b: vols[b])
    order = sorted(range(nbins), key=lambda b: -vols[b]); acc = 0; inc = set()
    for b in order:
        inc.add(b); acc += vols[b]
        if acc >= 0.70 * sum(vols): break
    return dict(pocp=lo + (poc + 0.5) * bh, vah=lo + (max(inc) + 1) * bh, val=lo + min(inc) * bh)

def hit_before_stop(w, jr, tgt, stop, long):
    for k in range(jr + 1, 30):
        if long:
            if w[k]["l"] <= stop: return None
            if w[k]["h"] >= tgt: return k
        else:
            if w[k]["h"] >= stop: return None
            if w[k]["l"] <= tgt: return k
    return None

def detect(w, rngN, pr, pmin):
    vah, val, poc = pr["vah"], pr["val"], pr["pocp"]
    wd = vah - val; out = []
    # A / F: first close above VAH
    for bk in range(rngN, 25):
        if w[bk]["c"] > vah + 0.05 * wd and all(w[k]["c"] <= vah for k in range(rngN, bk)):
            for jr in range(bk + 1, min(bk + 7, 27)):
                if w[jr]["l"] <= vah + 0.02 * wd and w[jr]["c"] >= vah:  # retest holds -> A
                    entry, tgt, stop = r5(vah), r5(vah + wd), r5(poc)
                    k = hit_before_stop(w, jr, tgt, stop, True)
                    p = int(round((tgt - entry) / PIP))
                    if k and p >= pmin:
                        out.append(dict(t="A", bk=bk, jr=jr, entry=entry, stop=stop, tgt=tgt, pips=p))
                    break
                if w[jr]["c"] < vah:  # failure back inside -> F
                    entry, tgt = r5(vah), r5(val)
                    stop = r5(max(w[m]["h"] for m in range(bk, jr + 1)) + 0.12 * wd)
                    k = hit_before_stop(w, jr, tgt, stop, False)
                    p = int(round((entry - tgt) / PIP))
                    if k and p >= pmin:
                        out.append(dict(t="F", bk=bk, jr=jr, entry=entry, stop=stop, tgt=tgt, pips=p))
                    break
            break
    # B: first close below VAL, retest holds
    for bk in range(rngN, 25):
        if w[bk]["c"] < val - 0.05 * wd and all(w[k]["c"] >= val for k in range(rngN, bk)):
            for jr in range(bk + 1, min(bk + 7, 27)):
                if w[jr]["h"] >= val - 0.02 * wd and w[jr]["c"] <= val:
                    entry, tgt, stop = r5(val), r5(val - wd), r5(poc)
                    k = hit_before_stop(w, jr, tgt, stop, False)
                    p = int(round((entry - tgt) / PIP))
                    if k and p >= pmin:
                        out.append(dict(t="B", bk=bk, jr=jr, entry=entry, stop=stop, tgt=tgt, pips=p))
                    break
            break
    # C: touch VAL from inside, bounce to POC
    for jr in range(rngN, 27):
        if w[jr]["c"] < val: break
        if w[jr]["l"] <= val + 0.02 * wd:
            entry, tgt, stop = r5(val), r5(poc), r5(val - 0.35 * wd)
            k = hit_before_stop(w, jr, tgt, stop, True)
            p = int(round((tgt - entry) / PIP))
            if k and p >= pmin:
                out.append(dict(t="C", jr=jr, entry=entry, stop=stop, tgt=tgt, pips=p))
            break
    # D: touch VAH from inside, reject to POC
    for jr in range(rngN, 27):
        if w[jr]["c"] > vah: break
        if w[jr]["h"] >= vah - 0.02 * wd:
            entry, tgt, stop = r5(vah), r5(poc), r5(vah + 0.35 * wd)
            k = hit_before_stop(w, jr, tgt, stop, False)
            p = int(round((entry - tgt) / PIP))
            if k and p >= pmin:
                out.append(dict(t="D", jr=jr, entry=entry, stop=stop, tgt=tgt, pips=p))
            break
    # E: exit below value then re-enter -> cross to VAH (80% rule)
    ex = [k for k in range(rngN, 26) if w[k]["c"] < val - 0.05 * wd]
    if ex:
        e0 = ex[0]
        for jr in range(e0 + 1, min(e0 + 8, 27)):
            if w[jr]["c"] > val:
                entry, tgt = r5(val), r5(vah)
                stop = r5(min(w[m]["l"] for m in range(e0, jr + 1)) - 0.12 * wd)
                k = hit_before_stop(w, jr, tgt, stop, True)
                p = int(round((tgt - entry) / PIP))
                if k and p >= pmin:
                    out.append(dict(t="E", jr=jr, entry=entry, stop=stop, tgt=tgt, pips=p))
                break
    # sanity: R:R between 0.5 and 4.5
    keep = []
    for c in out:
        risk = abs(c["entry"] - c["stop"]); rew = abs(c["tgt"] - c["entry"])
        if risk > 0 and 0.5 <= rew / risk <= 4.5: keep.append(c)
    return keep

TFS = [("15min", "M15", 900, 0.0012, 0.0060, 12, 4),
       ("30min", "M30", 1800, 0.0018, 0.0080, 18, 3),
       ("5min",  "M5",  300,  0.0008, 0.0045, 8,  3)]

KW = dt.timezone(dt.timedelta(hours=3))
all_cands = {}
for iv, tf, sec, wmin, wmax, pmin, need in TFS:
    cs = fetch(iv)
    cands = []
    for s in range(0, len(cs) - 30):
        w = cs[s:s + 30]
        if max(w[i + 1]["ts"] - w[i]["ts"] for i in range(29)) > 8 * sec: continue
        for rngN in (14, 16, 18, 20):
            pr = profile(w[:rngN])
            wd = pr["vah"] - pr["val"]
            if not (wmin <= wd <= wmax): continue
            f3 = sum(c["c"] for c in w[:3]) / 3; l3 = sum(c["c"] for c in w[rngN - 3:rngN]) / 3
            if abs(l3 - f3) > 0.9 * wd: continue
            for c in detect(w, rngN, pr, pmin):
                c.update(s=s, rngN=rngN, tf=tf)
                cands.append(c)
    all_cands[tf] = (cs, cands)
    n = {}
    for c in cands: n[c["t"]] = n.get(c["t"], 0) + 1
    print(f"{tf}: {len(cs)} candles, cands per type: {sorted(n.items())}", file=sys.stderr)

used_types = {}
chosen = []
for iv, tf, sec, wmin, wmax, pmin, need in TFS:
    cs, cands = all_cands[tf]
    cands.sort(key=lambda c: -c["pips"])
    picked = []
    def ok(c):
        return all(abs(c["s"] - p["s"]) >= 30 for p in picked)
    for want_new in (True, False):
        for c in cands:
            if len(picked) >= need: break
            if not ok(c): continue
            if want_new and used_types.get(c["t"], 0) > 0: continue
            if used_types.get(c["t"], 0) >= 2: continue
            picked.append(c); used_types[c["t"]] = used_types.get(c["t"], 0) + 1
    for c in picked:
        w = cs[c["s"]:c["s"] + 30]
        wj = []
        for cd in w:
            k = dt.datetime.fromtimestamp(cd["ts"], KW)
            wj.append(dict(d=f"{k.hour:02d}:{k.minute:02d}", o=cd["o"], h=cd["h"], l=cd["l"], c=cd["c"]))
        jrk = dt.datetime.fromtimestamp(w[c["jr"]]["ts"], KW)
        tr = dict(t=c["t"], tf=tf, date=jrk.strftime("%Y-%m-%d"), w=wj,
                  jr=c["jr"], entry=c["entry"], stop=c["stop"], tgt=c["tgt"],
                  pips=c["pips"], rngN=c["rngN"],
                  su=dt.datetime.fromtimestamp(w[0]["ts"], dt.timezone.utc).isoformat(),
                  eu=dt.datetime.fromtimestamp(w[-1]["ts"], dt.timezone.utc).isoformat())
        if "bk" in c: tr["bk"] = c["bk"]
        chosen.append(tr)

print(f"chosen: {[(t['tf'], t['t'], t['pips']) for t in chosen]}", file=sys.stderr)
print(json.dumps(chosen, ensure_ascii=False))
