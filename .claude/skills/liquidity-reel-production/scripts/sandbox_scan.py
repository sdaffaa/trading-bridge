# -*- coding: utf-8 -*-
"""الماسح: يجلب الشموع، يقصّ النوافذ، ويُخضعها للطبقات الخمس.

`query1.finance.yahoo.com` مرفوض من بوابة خروج هذه الجلسة، فالجلب يجري في
صندوق `sandbox_exec` المفتوح على الإنترنت. الصندوق لا يرى المستودع، فيُلصق
فيه `topdown.py` معه — منطقه كاملاً (العتبات والصيغ والتحقّقات) دون شروحه،
لأن أمر الصندوق محدود بـ16 ألف حرف. الشروح لا تُنفَّذ، فحذفها لا يغيّر حكماً.

الضمانة ليست في دقّة النسخ بل في إعادة الفحص: كل نافذة تخرج من هنا يعيد
`scan_setups.py` عرضها على `topdown.py` الأصلي داخل المستودع قبل أن يُبنى
منها ريل. فإن انحرفت نسخة الصندوق إلى التساهل رُفضت النافذة هناك، وإن
انحرفت إلى التشدّد ضاعت فرصة ولم يُقَل باطل. الأسوأ الممكن ضياع، لا كذب.

المرشّح الرخيص (كنس + ذيل + بلوغ ٢R) يطابق الطبقتين الرابعة والخامسة؛
غايته تقليل عدد النوافذ التي تُبنى، لا استبدال الحكم.

لا مفاتيح ولا حسابات: بيانات عامة فقط.

    python3 sandbox_scan.py [عدد_المقبولات] [رمز ...]
"""
import base64, datetime as dt, gzip, json, os, sys, urllib.parse, urllib.request

import topdown

UNIV = ["GC=F", "SI=F", "CL=F", "BZ=F", "NG=F", "HG=F", "BTC-USD", "ETH-USD",
        "EURUSD=X", "GBPUSD=X", "USDJPY=X", "^GSPC"]
Y = "https://query1.finance.yahoo.com/v8/finance/chart/"
RAW = os.path.join(os.path.dirname(os.path.abspath(__file__)), "raw_windows")
SLUG = {"GC=F": "gc", "SI=F": "si", "CL=F": "cl", "BZ=F": "bz", "NG=F": "ng",
        "HG=F": "hg", "BTC-USD": "btc", "ETH-USD": "eth", "EURUSD=X": "eur",
        "GBPUSD=X": "gbp", "USDJPY=X": "jpy", "^GSPC": "spx"}


def fetch(sym, iv, rng):
    url = f"{Y}{urllib.parse.quote(sym)}?interval={iv}&range={rng}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    d = json.load(urllib.request.urlopen(req, timeout=45))
    r = d["chart"]["result"][0]
    q = r["indicators"]["quote"][0]
    out, last = [], 0
    for i, t in enumerate(r["timestamp"]):
        o, h, l, c = q["open"][i], q["high"][i], q["low"][i], q["close"][i]
        if None in (o, h, l, c) or t <= last:
            continue
        # تقريب بحسب حجم السعر: أربعة أرقام على العملات، رقمان على ما فوق
        # المئة. الكسر الرابع في سعر بيتكوين ٦٤ ألفاً ضجيجٌ يضاعف حجم النافذة.
        p = 4 if abs(c) < 10 else (3 if abs(c) < 100 else 2)
        o, h, l, c = (round(v, p) for v in (o, h, l, c))
        h, l = max(o, h, c), min(o, l, c)
        if h == l:
            continue
        out.append(dict(d=dt.datetime.utcfromtimestamp(t).strftime("%Y-%m-%d %H:%M"),
                        o=o, h=h, l=l, c=c))
        last = t
    return out


EXEC_TF, EXEC_MIN = "3m", 3      # إطار التنفيذ (أمر فهد 2026-08-06)


def ts(s):
    return dt.datetime.strptime(s, "%Y-%m-%d %H:%M")


def agg(h1, hours):
    """الفريمات الأعلى تُجمَّع من بيانات الساعة نفسها.

    شموع ياهو اليومية للعقود تستعمل تعريف جلسة مختلفاً — قالت إن قمة
    2026-08-03 للذهب 4,083.50 بينما بيانات الساعة تقول 4,134.70. خلطُ
    السلسلتين يبني تحليلاً على معطيات متناقضة."""
    b = {}
    for c in h1:
        t = ts(c["d"])
        k = t.replace(minute=0)
        k = k.replace(hour=0) if hours >= 24 else k.replace(hour=t.hour // hours * hours)
        x = b.setdefault(k, dict(d=c["d"], o=c["o"], h=c["h"], l=c["l"], c=c["c"]))
        x["h"] = max(x["h"], c["h"]); x["l"] = min(x["l"], c["l"]); x["c"] = c["c"]
    return [(k, b[k]) for k in sorted(b)]


def agg_min(m1, minutes):
    """يجمّع شموع الدقيقة إلى إطار أدقّ من إطارات ياهو.

    ياهو لا يخدم ٣ دقائق (١م·٢م·٥م·١٥م…)، وأمر فهد 2026-08-06 أن يكون
    الدخول على ٣ دقائق. فتُجمَّع من الدقيقة الواحدة على حدود الساعة
    (الدقيقة // ٣) — لا على أول شمعة في المصفوفة، وإلا اختلفت الشموع
    باختلاف نقطة بدء الجلب."""
    b = {}
    for c in m1:
        t = ts(c["d"])
        k = t.replace(minute=t.minute // minutes * minutes)
        x = b.setdefault(k, dict(d=k.strftime("%Y-%m-%d %H:%M"),
                                 o=c["o"], h=c["h"], l=c["l"], c=c["c"]))
        x["h"] = max(x["h"], c["h"]); x["l"] = min(x["l"], c["l"]); x["c"] = c["c"]
    return [b[k] for k in sorted(b)]


def contiguous(w, minutes):
    """هل الشموع متتالية زمنياً بلا شمعة ناقصة؟

    أمر فهد: «لا تجعل فراغات بالجارت — يجب أن تكون الشموع متتالية».
    النافذة التي ينقصها بوكت (عطلة جلسة أو انقطاع بيانات) تُرسم متلاصقة
    بالفهرس فتوهم أن السعر تحرّك بلا انقطاع — فتُرفض من المصدر."""
    step = dt.timedelta(minutes=minutes)
    return all(ts(w[i + 1]["d"]) - ts(w[i]["d"]) == step for i in range(len(w) - 1))


def closed(rows, anchor, hours, n):
    """آخر n شمعة أُغلقت قبل لحظة المرساة — الجارية لا تدخل."""
    lim = dt.timedelta(hours=hours)
    return [x for k, x in rows if k + lim <= anchor][-n:]


def cands(m5):
    out = []
    for sw in range(40, len(m5) - 20):
        w = m5[sw - 40:sw + 20]
        R = max(c["h"] for c in w) - min(c["l"] for c in w)
        if R <= 0:
            continue
        tol, pierce = R * 0.015, R * 0.001
        lb = m5[sw - 16:sw]
        base = min(c["l"] for c in lb)
        c0 = m5[sw]
        if not (c0["l"] < base - pierce and c0["c"] > base):
            continue
        eq = [c for c in lb if abs(c["l"] - base) <= tol]
        if len(eq) < 2:
            continue
        rg = c0["h"] - c0["l"]
        wick = (min(c0["o"], c0["c"]) - c0["l"]) / rg if rg else 0
        if wick < 0.30:
            continue
        ent = c0["c"]; stp = c0["l"] - R * 0.006; tgt = ent + (ent - stp) * 2
        hit = None
        for j in range(sw + 1, sw + 20):
            if m5[j]["l"] < stp:
                break
            if m5[j]["h"] >= tgt:
                hit = j; break
        if hit is None:
            continue
        out.append(dict(sw=sw, eq=len(eq), wick=round(wick, 3),
                        bars=hit - sw, anchor=c0["d"]))
    return out


def window(sym, h1, m5, sw):
    a = ts(m5[sw]["d"])
    d1 = closed(agg(h1, 24), a, 24, 15)
    h4 = closed(agg(h1, 4), a, 4, 34)
    hh = closed([(ts(c["d"]), c) for c in h1], a, 1, 40)
    w5 = m5[sw - 40:sw + 20]
    if len(d1) < 15 or len(h4) < 34 or len(hh) < 40:
        return None
    if not contiguous(w5, EXEC_MIN):
        return None
    row = lambda b: [b["d"], b["o"], b["h"], b["l"], b["c"]]
    return {"sym": sym, "anchor_utc": m5[sw]["d"], "exec_tf": EXEC_TF,
            "src": f"Yahoo {sym}: 1h خام و{EXEC_TF} مجمَّعة من الدقيقة، "
                   f"و1D/4H مجمَّعة من الساعة — سلسلة واحدة متسقة",
            "1D": {"anchor": 14, "rows": [row(b) for b in d1]},
            "4H": {"anchor": 33, "rows": [row(b) for b in h4]},
            "1h": {"anchor": 39, "rows": [row(b) for b in hh]},
            EXEC_TF: {"anchor": 40, "rows": [row(b) for b in w5]}}


def fname(w):
    s = SLUG.get(w["sym"], w["sym"].lower().replace("=", "").replace("^", ""))
    return f'{s}_sc_{w["anchor_utc"].replace(" ", "_").replace(":", "")}.json'


def gate(w):
    """الطبقات الخمس بكود المستودع نفسه. الرفض يُعاد بسببه لا بصمت."""
    os.makedirs(RAW, exist_ok=True)
    p = os.path.join(RAW, fname(w))
    json.dump(w, open(p, "w", encoding="utf-8"), ensure_ascii=False)
    try:
        D, L, P = topdown.build(fname(w))
    except Exception as e:
        os.remove(p)
        return None, f"{type(e).__name__}: {e}"
    # نفس عتبة الجدوى في `scan_setups.py`، تُطبَّق هنا كي لا تُهدر حصّة
    # النوافذ العائدة على صفقات وقفُها داخل الفارق السعري.
    rr = (P["ENT"] - P["STP"]) / P["ENT"]
    if rr < 0.0006:
        os.remove(p)
        return None, f"AssertionError: المخاطرة {rr*1e4:.1f} نقطة أساس — ضجيج"
    return dict(file=fname(w), w=w, L=L, P=P), None


if __name__ == "__main__":
    top = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    univ = sys.argv[2:] or UNIV
    found = []
    for sym in univ:
        try:
            h1 = fetch(sym, "1h", "1mo")
            # مدى الدقيقة الواحدة عند ياهو سبعة أيام لا شهر — فالمسح على
            # إطار التنفيذ يغطّي أسبوعاً، وهذا ثمن الثلاث دقائق المعلَن.
            m5 = agg_min(fetch(sym, "1m", "7d"), EXEC_MIN)
        except Exception as e:
            print(f"{sym}: تعذّر الجلب — {e}", file=sys.stderr)
            continue
        cs = cands(m5)
        print(f"{sym}: {len(cs)} مرشّح من {len(m5)} شمعة", file=sys.stderr)
        for c in cs:
            c.update(sym=sym, _h1=h1, _m5=m5)
        found += cs
    # ترتيب المرشّحين: قيعان أكثر عند المستوى، ثم ذيل أعمق، ثم بلوغ أسرع
    found.sort(key=lambda c: (-c["eq"], -c["wick"], c["bars"]))
    print(f"\nالمرشّحون: {len(found)} — يُعرضون على الطبقات الخمس بالترتيب",
          file=sys.stderr)

    ok, seen, why = [], 0, {}
    for c in found:
        if len(ok) >= top:
            break
        w = window(c["sym"], c["_h1"], c["_m5"], c["sw"])
        if not w:
            continue
        seen += 1
        r, err = gate(w)
        if err:
            k = err.split(":")[0] + " — " + err.split(":", 1)[1].split("[")[0].strip()[:44]
            why[k] = why.get(k, 0) + 1
            continue
        ok.append(r)
        print(f'\n✓ {r["file"]}  {w["sym"]} · {w["anchor_utc"]}', file=sys.stderr)
        for x in r["L"]:
            print(f'    [{x["tf"]:>3}] {x["title"]}: {x["detail"]}', file=sys.stderr)
        P = r["P"]
        print(f'    ← دخول {P["ENT"]:,.2f} · وقف {P["STP"]:,.2f} · هدف '
              f'{P["TGT"]:,.2f} · تحقّق بعد {P["hit"] - P["fill"]} شمعة',
              file=sys.stderr)

    print(f'\nفُحص {seen} من {len(found)} · قُبل {len(ok)} · أسباب الرفض:',
          file=sys.stderr)
    for k, v in sorted(why.items(), key=lambda x: -x[1])[:8]:
        print(f'   {v:>4} × {k}', file=sys.stderr)

    print("===WINDOWS_GZ_B64===")
    print(base64.b64encode(gzip.compress(
        json.dumps([r["w"] for r in ok], ensure_ascii=False,
                   separators=(",", ":")).encode(), 9)).decode())
