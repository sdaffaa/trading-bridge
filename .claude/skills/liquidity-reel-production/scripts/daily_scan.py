# -*- coding: utf-8 -*-
"""مسح نوافذ يومية حقيقية — أخو `sheet_scan` لكن على الفريم اليومي.

سببه: مخزون `sheet_candidates.json` كله منشور، والمصدر لا يعطي أكثر من
سنة على الساعة وشهرين على الدقائق — فكل مسحٍ جديد يعيد التواريخ نفسها
فتسقط كلها في `assert_fresh_real`. أما الفريم اليومي فيمتدّ عشر سنوات
لكل زوج، وعلى أزواجٍ لم يمسسها السجل بعد — فالنوافذ الحرّة فيه بالمئات،
ولا مفتاح API يُمرَّر للصندوق.

الشروط الثلاثة كما هي بلا تخفيف: ≥٤ شمعات بعد الدخول · بلوغ ٢R داخل
النافذة · مخاطرة ≥٦ نقاط أساس. ويُضاف شرطٌ رابع هنا: النافذة لا تتقاطع
مع أي مدىً في `used.json` (السجل يُشحن مع الحمولة) — فلا يضيع نصيب
القبول على نوافذ منشورة كما ضاع في تشغيلة سابقة.
"""
import json, sys, os, urllib.request, urllib.parse, datetime as dt

# ── مفردات الكشف: منقولة حرفياً من `sheet_scan` فالنمط واحد والفريم متغيّر ──
def swings(cs, idxs, key, cmpmax):
    out = []
    for k in range(1, len(idxs) - 1):
        a, b, c = idxs[k-1], idxs[k], idxs[k+1]
        v = cs[b][key]
        if cmpmax and v >= cs[a][key] and v >= cs[c][key]: out.append(b)
        if not cmpmax and v <= cs[a][key] and v <= cs[c][key]: out.append(b)
    return out


def classify(cs, bk, r, ztop, relax):
    pb = list(range(bk, r + 1))
    dep = cs[bk]["h"] - ztop
    if dep <= 0: return []
    out = []
    sh = swings(cs, pb, "h", True); sl = swings(cs, pb, "l", False)
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


# ────────────────────────── جلب يومي بلا مفتاح ──────────────────────────
DAY = 86400

def fetch_daily(sym):
    """كل التاريخ اليومي المتاح من ياهو — بلا مفتاح.

    (ستوك يردّ صفحة تحقّق جافاسكربت للعميل غير المتصفّح، فلا CSV منه.)"""
    url = (f"https://query1.finance.yahoo.com/v8/finance/chart/"
           f"{urllib.parse.quote(sym)}?interval=1d&range=10y")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Accept": "*/*"})
    d = json.load(urllib.request.urlopen(req, timeout=60))
    r = d["chart"]["result"][0]
    ts = r["timestamp"]; q = r["indicators"]["quote"][0]
    out = []; last = 0
    for i, t in enumerate(ts):
        o, h, l, c = q["open"][i], q["high"][i], q["low"][i], q["close"][i]
        if None in (o, h, l, c) or t <= last: continue
        o, h, l, c = (round(v, 6) for v in (o, h, l, c))
        h = max(o, h, l, c); l = min(o, h, l, c)
        if h == l: continue
        # يُطبَّع الطابع إلى منتصف اليوم UTC فتُقاس الفجوات بالأيام لا بساعات الجلسة
        t = (t // DAY) * DAY
        if t <= last: continue
        out.append(dict(ts=t, o=o, h=h, l=l, c=c)); last = t
    return out


# ─────────────────────── بوابة السجل: لا نافذة منشورة ───────────────────────
def _n(s):
    return str(s).replace("T", " ")[:16]


def overlaps(sym, a0, a1, used):
    """تقاطعٌ مع مدىً منشور — بنفس منطق `chart_registry._ov` والرمز بلا لاحقة."""
    base = sym.split("=")[0].upper()
    a0, a1 = sorted((_n(a0), _n(a1)))
    for e in used:
        if e["symbol"].split("=")[0].upper() != base: continue
        b0, b1 = sorted((_n(e["start"]), _n(e["end"])))
        if not (a1 < b0 or a0 > b1): return True
    return False


MAXW = 52
MIN_AFTER = 4
MIN_RISK_BP = 0.0006
PER_CLS = 12
# أدنى وسيطٍ لنسبة الجسم إلى المدى في النافذة. سببه مقيس: أزواج الفوركس
# الفورية عند هذا المصدر تكتب الإغلاق اليومي مساوياً للافتتاح تقريباً،
# فوسيط النسبة 0.02 — تسعٌ وعشرون شمعة دوجي متتالية. ورسمُها يكذب مرّتين:
# الشكل يقول إن السوق لم يقرّر شيئاً طوال شهر، والتحليل يبني «إغلاقاً فوق
# الحدّ» على إغلاقٍ لا يفرقه عن افتتاحه شيء. والعقود الآجلة والعملات
# المشفّرة تعطي 0.34–0.52 فتمرّ.
MIN_BODY = 0.15

# أدواتٌ لم يمسّها السجل على الفريم اليومي، وأخرى مسّها في مدىً بعيد
# فبقيّة عقودها حرّة — والبوابة `overlaps` هي التي تفصل لا هذه القائمة.
PAIRS = ["GC=F", "SI=F", "HG=F", "PL=F", "PA=F",
         "CL=F", "NG=F", "RB=F", "HO=F", "BZ=F",
         "ZC=F", "ZW=F", "ZS=F", "KC=F", "CT=F", "SB=F", "CC=F",
         "NQ=F", "ES=F", "YM=F", "RTY=F", "ZN=F", "ZB=F",
         "6E=F", "6B=F", "6A=F", "6J=F", "6C=F", "6S=F",
         "BTC-USD", "ETH-USD", "SOL-USD", "LTC-USD", "XRP-USD",
         "SPY", "QQQ", "IWM", "GLD", "SLV", "TLT", "USO"]

used = []
if os.path.exists("used.json"):
    used = json.load(open("used.json"))["real"]

allc = {}; series = {}
for sym in PAIRS:
    try:
        cs = fetch_daily(sym)
    except Exception as ex:
        print(f"{sym}: fetch failed {ex}", file=sys.stderr); continue
    if len(cs) < 300:
        print(f"{sym}: only {len(cs)} candles", file=sys.stderr); continue
    key = (sym.upper(), "1d")
    series[key] = cs
    for relax in (False, True):
        cands = scan(cs, sym.upper(), "1d", DAY, relax)
        for c in cands: c["relax"] = relax
        allc.setdefault(key, []).extend(cands)
    kinds = {}
    for c in allc[key]: kinds[c["cls"]] = kinds.get(c["cls"], 0) + 1
    print(f"{sym}: {len(cs)} candles {cs[0]['ts']}..{cs[-1]['ts']}, {sorted(kinds.items())}", file=sys.stderr)

chosen = []
for cls in ("chan", "consol", "sweep"):
    pool = [c for v in allc.values() for c in v if c["cls"] == cls]
    pool.sort(key=lambda c: (c["relax"], -c["s"]))
    kept = []
    for c in pool:
        if any(k["sym"] == c["sym"] and abs(k["bk"] - c["bk"]) < 40 for k in kept): continue
        kept.append(c)
        if len(kept) >= PER_CLS: break
    if not kept: print(f"NO CANDIDATE for {cls}", file=sys.stderr)
    chosen.extend(kept)

rows = []; rejected = []
for c in chosen:
    cs = series[(c["sym"], "1d")]
    ws = max(0, c["iH"] - 5)
    ee = c["ir"] + 1
    while ee < len(cs) - 1 and cs[ee]["h"] < cs[c["bk"]]["h"] and ee - c["ir"] < 9: ee += 1
    we = min(len(cs) - 1, max(ee + 3, c["ir"] + MIN_AFTER))
    lbl = f'{c["cls"]} {c["sym"]} 1d'
    if we - ws + 1 > MAXW:
        rejected.append(f'{lbl}: النافذة {we-ws+1} شمعة > {MAXW}'); continue
    if we - c["ir"] < MIN_AFTER:
        rejected.append(f'{lbl}: {we-c["ir"]} شمعات بعد الدخول'); continue
    ent = cs[c["ir"]]["c"]; stp = cs[c["iob"]]["l"]
    rng = max(x["h"] for x in cs[ws:c["ir"]+1]) - min(x["l"] for x in cs[ws:c["ir"]+1])
    stp -= rng * 0.006
    if ent <= stp or (ent - stp) / ent < MIN_RISK_BP:
        rejected.append(f'{lbl}: المخاطرة {(ent-stp)/ent*1e4:.1f} نقطة أساس'); continue
    tgt = ent + (ent - stp) * 2.0
    if not any(cs[k]["h"] >= tgt for k in range(c["ir"] + 1, we + 1)):
        rejected.append(f'{lbl}: لم يبلغ ٢R داخل النافذة'); continue
    ds = lambda i: dt.datetime.fromtimestamp(cs[i]["ts"], dt.timezone.utc).strftime("%Y-%m-%d")
    if overlaps(c["sym"], ds(ws), ds(we), used):
        rejected.append(f'{lbl} {ds(ws)}: منشورة سابقاً'); continue
    bod = sorted(abs(x["c"] - x["o"]) / (x["h"] - x["l"]) for x in cs[ws:we + 1])
    med = bod[len(bod) // 2]
    if med < MIN_BODY:
        rejected.append(f'{lbl} {ds(ws)}: وسيط الجسم/المدى {med:.2f} < {MIN_BODY}'); continue
    w = []
    for cd in cs[ws:we+1]:
        k = dt.datetime.fromtimestamp(cd["ts"], dt.timezone.utc)
        w.append(dict(d=k.strftime("%m-%d"), o=cd["o"], h=cd["h"], l=cd["l"], c=cd["c"]))
    row = dict(cls=c["cls"], sym=c["sym"], tf="1d", w=w,
               date=ds(c["ir"]), su=ds(ws), eu=ds(we), relax=c["relax"])
    for key in ("iH", "bk", "iob", "ir", "i1", "i2", "ipdl", "ca", "cb", "rt", "rb"):
        if key in c: row[key] = c[key] - ws
    for key in ("chi", "clo"):
        if key in c: row[key] = [v - ws for v in c[key]]
    rows.append(row)

for m in rejected: print("rejected " + m, file=sys.stderr)
print(f"chosen: {[(r['cls'], r['sym'], r['su'], r['eu'], len(r['w'])) for r in rows]}", file=sys.stderr)
print(json.dumps(rows, ensure_ascii=False))
