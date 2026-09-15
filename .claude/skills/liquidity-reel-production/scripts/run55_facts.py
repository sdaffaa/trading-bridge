# -*- coding: utf-8 -*-
"""تشغيلة ٥٥ — قياس حقائق الكاروسيلات الخمسة من شموع حقيقية.

المصدر: Alpha Vantage `TIME_SERIES_DAILY` (OHLC **مع حجم حقيقي**) لخمسة
صناديق متداولة، محفوظ في `content/run55_data/*.csv`. الحجم هو ما فتح الباب
لمواضيع البروفايل والـVWAP: خطّ النوافذ القديم (`raw_windows` و
`sheet_candidates`) بلا حقل حجم، ولذلك بقيت هذه المواضيع مصفوفة منذ
2026-08-08.

**ما يزال متعذّراً هنا: الفوت برنت.** يحتاج عرضاً وطلباً داخل الشمعة، ولا
مصدر لهما. فيُرسم رسماً توضيحياً موسوماً «رسم توضيحي — وليس شارتاً
حقيقياً» و«أرقام تعليمية»، ولا يُقدَّم رقمٌ منه على أنه سوق.

كل رقم في الصفحات الثلاثين يخرج من هنا. وكل ادّعاء يمرّ على `assert`:
ما لا تثبته الشموع يسقط، ولا يُجمَّل.

    python3 run55_facts.py          # يطبع القياسات
    python3 run55_facts.py --json   # يكتب content/run55_facts.json
"""
import csv, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.normpath(os.path.join(HERE, "..", "..", "..", "..",
                                     "content", "run55_data"))
OUT = os.path.normpath(os.path.join(HERE, "..", "..", "..", "..",
                                    "content", "run55_facts.json"))


# ═════════════════════════ التحميل ═════════════════════════
def load(sym):
    """يعيد الشموع من الأقدم إلى الأحدث. الملف من المصدر بترتيب معكوس."""
    p = os.path.join(DATA, f"{sym}.csv")
    rows = list(csv.DictReader(open(p, encoding="utf-8")))
    bars = [dict(d=r["timestamp"], o=float(r["open"]), h=float(r["high"]),
                 l=float(r["low"]), c=float(r["close"]), v=int(r["volume"]))
            for r in rows][::-1]
    for b in bars:
        assert b["l"] <= min(b["o"], b["c"]) and b["h"] >= max(b["o"], b["c"]), \
            f"{sym} {b['d']}: تسلسل OHLC غير منطقي"
        assert b["h"] > b["l"], f"{sym} {b['d']}: مدى صفري"
        assert b["v"] > 0, f"{sym} {b['d']}: حجم صفري"
    ds = [b["d"] for b in bars]
    assert ds == sorted(ds), f"{sym}: التواريخ غير مرتّبة"
    assert len(ds) == len(set(ds)), f"{sym}: تاريخ مكرّر"
    return bars


def idx(bars, day):
    for i, b in enumerate(bars):
        if b["d"] == day:
            return i
    raise AssertionError(f"لا شمعة بتاريخ {day}")


# ═════════════════════════ أدوات القياس ═════════════════════════
def vprofile(bars, bins=48):
    """بروفايل حجم من شموع يومية: حجم كل يوم يُوزَّع بالتساوي على مداه.

    **هذا تقريب معلَن لا بيانات تِك.** الطريقة قياسية في أدوات البروفايل
    المبنية على OHLCV، ولا تدّعي معرفة أين تداول الحجم داخل اليوم — لذلك
    تُكتب على الصفحة نفسها. ما تعطيه صحيحًا: أين تراكم الحجم على محور
    السعر بمرور الأيام، وهو كل ما يقوم عليه درس العقد.
    """
    lo = min(b["l"] for b in bars)
    hi = max(b["h"] for b in bars)
    step = (hi - lo) / bins
    cells = [0.0] * bins
    for b in bars:
        a = max(0, min(bins - 1, int((b["l"] - lo) / step)))
        z = max(0, min(bins - 1, int((b["h"] - lo) / step)))
        n = z - a + 1
        share = b["v"] / n
        for k in range(a, z + 1):
            cells[k] += share
    poc = max(range(bins), key=lambda k: cells[k])

    # منطقة القيمة: ٧٠٪ من الحجم تُجمَع من العقدة الأعلى إلى الجانبين
    total = sum(cells)
    taken = {poc}
    acc = cells[poc]
    lo_k = hi_k = poc
    while acc < total * 0.70:
        dn = cells[lo_k - 1] if lo_k - 1 >= 0 else -1
        up = cells[hi_k + 1] if hi_k + 1 < bins else -1
        if up >= dn:
            hi_k += 1; taken.add(hi_k); acc += cells[hi_k]
        else:
            lo_k -= 1; taken.add(lo_k); acc += cells[lo_k]
    price = lambda k: lo + (k + 0.5) * step
    return dict(lo=lo, hi=hi, step=step, cells=cells, poc=poc,
                poc_price=price(poc), val=price(lo_k), vah=price(hi_k),
                price=price, total=total)


def avwap(bars, i0, upto=None):
    """VWAP مرسى: Σ(السعر النموذجي × الحجم) ÷ Σالحجم منذ شمعة المرساة.

    هذا حسابٌ كامل لا تقريب — السعر النموذجي (h+l+c)/3 هو التعريف القياسي
    على الشموع، والحجم حقيقي. فالخط الناتج هو الخط نفسه الذي ترسمه المنصّة
    على الفريم اليومي.
    """
    upto = len(bars) - 1 if upto is None else upto
    pv = vv = 0.0
    out = {}
    for i in range(i0, upto + 1):
        b = bars[i]
        tp = (b["h"] + b["l"] + b["c"]) / 3
        pv += tp * b["v"]; vv += b["v"]
        out[i] = pv / vv
    return out


def swing_lows(bars, k=3):
    return [i for i in range(k, len(bars) - k)
            if all(bars[i]["l"] <= bars[j]["l"] for j in range(i - k, i + k + 1))]


def swing_highs(bars, k=3):
    return [i for i in range(k, len(bars) - k)
            if all(bars[i]["h"] >= bars[j]["h"] for j in range(i - k, i + k + 1))]


def sma_vol(bars, i, n=20):
    a = max(0, i - n)
    return sum(b["v"] for b in bars[a:i]) / max(1, i - a)


def pct(x):
    return f"{x:.1f}٪"


# ═════════════════════════ ١ · العقدة (SPY · بروفايل + حجم) ═════════════════════════
def c1_node():
    B = load("SPY")
    # نطاق البروفايل معلَن وثابت: من قاع ٢٧ مارس إلى ٢ يونيو. اختير بمسحٍ
    # على كل النطاقات الممكنة في الأدوات الخمس بشرطين: أن تكون العقدتان
    # مُلامَستين بعد النطاق (وإلا فلا مقارنة)، وأن يكون الفرق بينهما حاداً.
    a, z = idx(B, "2026-03-27"), idx(B, "2026-06-02")
    rng = B[a:z + 1]
    P = vprofile(rng)

    # العقدة الرقيقة: أقل خلية **داخل** المدى المتداول بين طرفي منطقة القيمة،
    # لا عند حافة البروفايل (حواف البروفايل رقيقة دائماً — وذلك ليس درساً).
    ks = [k for k in range(len(P["cells"]))
          if P["val"] < P["price"](k) < P["vah"]]
    lvn = min(ks, key=lambda k: P["cells"][k])
    hvn = P["poc"]
    lvn_p, hvn_p = P["price"](lvn), P["price"](hvn)
    assert P["cells"][lvn] < P["cells"][hvn] * 0.62, \
        "الفرق بين العقدتين ضعيف — لا يصلح درساً"

    # ما بعد النطاق: كم شمعة أغلقت داخل شريط كل عقدة؟
    half = P["step"] * 0.5
    after = B[z + 1:]
    n_lvn = sum(1 for b in after if abs(b["c"] - lvn_p) <= half)
    n_hvn = sum(1 for b in after if abs(b["c"] - hvn_p) <= half)
    # وكم شمعة **لمست** كلاً منهما (عبرت الشريط بمداها)؟
    t_lvn = sum(1 for b in after if b["l"] <= lvn_p + half and b["h"] >= lvn_p - half)
    t_hvn = sum(1 for b in after if b["l"] <= hvn_p + half and b["h"] >= hvn_p - half)
    assert t_lvn >= 2 and t_hvn >= 2, "إحدى العقدتين لم تُلمَس مرّتين بعد النطاق — لا مقارنة"
    assert n_hvn > n_lvn, "السميكة لم تحتجز السعر أكثر — الادّعاء لا يثبت"

    return dict(sym="SPY", name="صندوق إس آند بي ٥٠٠", tf="يومي",
                a=B[a]["d"], z=B[z]["d"], bars=B, i0=a, i1=z,
                prof=P, lvn=lvn, hvn=hvn, lvn_p=lvn_p, hvn_p=hvn_p,
                lvn_vol=P["cells"][lvn], hvn_vol=P["cells"][hvn],
                ratio=P["cells"][lvn] / P["cells"][hvn],
                n_lvn=n_lvn, n_hvn=n_hvn, t_lvn=t_lvn, t_hvn=t_hvn,
                after_n=len(after), poc=P["poc_price"], vah=P["vah"], val=P["val"])


# ═════════════════════════ ٢ · المرساة (GLD · ICT + AVWAP) ═════════════════════════
def c2_anchor():
    """غارة سيولة البيع (ICT) والـVWAP المرسى فاصلاً بين الخصم والعلاوة.

    البحث الأول جرّب نموذج ICT الكامل — كنس ثم إزاحة ثم فجوة قيمة ثم رجعة
    إليها — فلم يثبت **ولا مرّة** على الأدوات الخمس: من ١٤ كنساً صالحاً لم
    تُتبَع ١٢ بشمعة إزاحة (جسم ≥ متوسط المدى الحقيقي)، والاثنتان الباقيتان
    بلا فجوة. الشموع اليومية للصناديق لا تفجّر فجوات كفجوات الفريم الصغير.
    فلم يُخفَّض تعريف الفجوة ولا الإزاحة — نُقل الدرس إلى نموذج ICT آخر
    **موجود فعلاً** في هذه البيانات: الغارة على السيولة والإغلاق فوق
    المستوى، والهدف سيولة الشراء فوق النطاق.

    والـVWAP هنا ليس زينة: الدخول تحت الخط (خصم) والهدف فوقه (علاوة) —
    وهذا هو التقسيم نفسه الذي يعمل به ICT، محسوباً على حجم حقيقي.
    """
    B = load("GLD")
    SL, SH = swing_lows(B, 2), swing_highs(B, 2)

    best = None
    for p in SL:
        lvl = B[p]["l"]
        for s in range(p + 2, min(p + 15, len(B))):
            if not (B[s]["l"] < lvl and B[s]["c"] > lvl):
                continue
            if min(B[k]["l"] for k in range(p + 1, s)) <= lvl:
                break                      # كُنس المستوى قبله — البركة استُهلكت
            hs = [k for k in SH if p <= k < s]
            if not hs:
                continue
            tgt = max(B[k]["h"] for k in hs)      # سيولة الشراء فوق النطاق
            ent, stop = B[s]["c"], B[s]["l"]
            if tgt <= ent:
                continue
            rr = (tgt - ent) / (ent - stop)
            hit = next((k for k in range(s + 1, len(B)) if B[k]["h"] >= tgt), None)
            if hit is None:
                continue
            low_after = min(b["l"] for b in B[s + 1:hit + 1])
            if low_after <= stop:
                continue
            av = avwap(B, p)                       # المرساة = القاع المكنوس
            if B[s]["c"] >= av[s]:
                continue                            # لا خصم — لا درس
            if tgt <= av[s]:
                continue                            # الهدف ليس في العلاوة
            cand = dict(p=p, s=s, lvl=lvl, ent=ent, stop=stop, tgt=tgt, rr=rr,
                        hit=hit, av=av, anchor=p, low_after=low_after,
                        bars_to_target=hit - s,
                        disc=(av[s] - ent) / av[s] * 100,
                        prem=(tgt - av[s]) / av[s] * 100,
                        rel=B[s]["v"] / sma_vol(B, s),
                        tgt_i=max(hs, key=lambda k: B[k]["h"]))
            if best is None or cand["rr"] > best["rr"]:
                best = cand
    assert best is not None, "لا غارة سيولة بخصم وعلاوة تثبت على هذه النافذة"
    assert best["rr"] >= 2.0, "المكافأة أقل من ضعف المخاطرة — لا تُدرَّس خطوةَ دخول"

    B0 = max(0, best["p"] - 5)
    B1 = min(len(B) - 1, best["hit"] + 4)
    return dict(sym="GLD", name="صندوق الذهب", tf="يومي", bars=B,
                i0=B0, i1=B1, **best)


# ═════════════════════════ ٣ · الامتصاص (QQQ · SMC + فوت برنت توضيحي) ═════════════════════════
def c3_absorb():
    """كسر هيكلٍ انقلب — والامتصاص الذي لا تراه الشمعة.

    الأداة اختارتها البيانات لا الرغبة: مُسحت الأدوات الخمس عن «كسر بإغلاق
    فوق قمّة سوينق ثم إغلاق تحت القاع الذي سبقها»، فأعطت ست حالات أعمقها
    الناسداك (٥٫٠١٪). الفضة — التي كانت مرشّحة أولاً — لم تعطِ ولا حالة.

    وشقّ الفوت برنت في هذا الكاروسيل **رسم توضيحي موسوم**: لا مصدر لعرضٍ
    وطلبٍ داخل الشمعة هنا، فأرقامه تعليمية معلَنة ولا تُقدَّم سوقاً.
    """
    B = load("QQQ")
    highs, lows = swing_highs(B, 2), swing_lows(B, 2)

    best = None
    for hi in highs:
        # كسر بإغلاق فوق القمّة
        br = next((k for k in range(hi + 1, min(hi + 8, len(B)))
                   if B[k]["c"] > B[hi]["h"]), None)
        if br is None:
            continue
        prev = [k for k in lows if k < hi]
        if not prev:
            continue
        base = prev[-1]                         # القاع الذي سبق القمّة
        # الاستدراج: يعود ويغلق تحت ذلك القاع خلال عشر شمعات من الكسر
        fail = next((k for k in range(br + 1, min(br + 13, len(B)))
                     if B[k]["c"] < B[base]["l"]), None)
        if fail is None:
            continue
        ent = B[br]["c"]
        drop = (ent - B[fail]["c"]) / ent * 100
        # شمعة الكسر بحجم مرتفع لكن السعر لم يتقدّم بعدها — أثر الامتصاص
        rel = B[br]["v"] / sma_vol(B, br)
        cand = dict(hi=hi, br=br, base=base, fail=fail, ent=ent, drop=drop,
                    rel=rel, span=fail - br)
        if best is None or cand["drop"] > best["drop"]:
            best = cand
    assert best is not None, "لا كسرَ هيكلٍ ينقلب على هذه النافذة"
    assert best["drop"] >= 4.0, "الانقلاب أضعف من أن يُدرَّس"

    # القمّة التالية بعد الكسر: أعلى ما وصله السعر قبل أن ينقلب
    top = max(range(best["br"], best["fail"] + 1), key=lambda k: B[k]["h"])
    B0 = max(0, best["base"] - 4)
    B1 = min(len(B) - 1, best["fail"] + 3)
    return dict(sym="QQQ", name="صندوق الناسداك", tf="يومي", bars=B,
                i0=B0, i1=B1, top=top, top_h=B[top]["h"], **best)


# ═════════════════════════ ٤ · الجهد (USO · حجم + AVWAP) ═════════════════════════
def c4_effort():
    """جهد بلا نتيجة: حجم مضاعف ومدى واسع وجسم ضئيل — ثم ماذا؟

    الشرط ليس «حجم مرتفع» وحده — ذلك ليس إشارة. الشرط ثلاثي: حجم ≥ ١٫٦×
    متوسط عشرين يوماً، وجسمٌ ≤ ٣٥٪ من مدى اليوم (الجهد لم يُنتج إزاحة)،
    ثم تُقاس **النتيجة** بعد ثلاث شمعات بلا انتقاء.
    """
    B = load("USO")
    anc = idx(B, "2026-07-02")     # مرساة معلَنة: قاع السوينق الذي بدأ الموجة
    av = avwap(B, anc)

    days = []
    for i in range(anc + 1, len(B) - 6):
        rel = B[i]["v"] / sma_vol(B, i)
        if rel < 1.6:
            continue
        rng = B[i]["h"] - B[i]["l"]
        body = abs(B[i]["c"] - B[i]["o"])
        if body > rng * 0.35:          # جهد بلا نتيجة: مدى واسع وجسم ضئيل
            continue
        days.append(dict(i=i, d=B[i]["d"], rel=rel, rng=rng, body=body,
                         ratio=body / rng, close=B[i]["c"], av=av[i],
                         dist=(B[i]["c"] - av[i]) / av[i] * 100,
                         a3=(B[i + 3]["c"] - B[i]["c"]) / B[i]["c"] * 100,
                         a5=(B[i + 5]["c"] - B[i]["c"]) / B[i]["c"] * 100,
                         vol=B[i]["v"], vol_avg=sma_vol(B, i)))
    assert len(days) >= 3, "أقل من ثلاثة أيام جهدٍ بلا نتيجة — لا مقارنة"

    # الحكم الذي تسنده هذه النافذة: البُعد عن المرساة يفرّق بين النتيجتين.
    near = min(days, key=lambda x: abs(x["dist"]))
    far = max(days, key=lambda x: abs(x["dist"]))
    assert near["a3"] > 0 > far["a3"], \
        "القريب من المرساة والبعيد عنها لم يفترقا في النتيجة — لا درس"
    assert far["dist"] > near["dist"] * 3, "الفارق في البُعد ضعيف"

    B0, B1 = max(0, anc - 3), min(len(B) - 1, far["i"] + 6)
    return dict(sym="USO", name="صندوق النفط", tf="يومي", bars=B,
                i0=B0, i1=B1, anchor=anc, av=av, days=days,
                near=near, far=far, n=len(days))


# ═════════════════════════ ٥ · التحريك (SLV · نفس + مخاطرة) ═════════════════════════
def c5_move():
    """نقلُ الوقف يحوّل خسارةً محسوبة إلى خسارةٍ مفتوحة — بالأرقام.

    لا وعظ: الوقف البنائي تحت قاع السوينق بهامش ٠٫٣٪، والدخول إغلاقٌ فوق
    قمّة ذلك القاع. ثم يُقاس ما جرى فعلاً بعد ضربه — أدنى قاع خلال خمس
    شمعات — لأن مَن ينقل الوقف لا يخرج عند مستواه القديم بل يبقى.
    """
    B = load("SLV")
    best = None
    for lo in swing_lows(B, 3):
        # الوقف البنائي: تحت القاع بهامش ٠٫٣٪
        stop = B[lo]["l"] * 0.997
        ent = None
        for k in range(lo + 1, min(lo + 6, len(B))):
            if B[k]["c"] > B[lo]["h"]:
                ent = k; break
        if ent is None:
            continue
        hit = next((k for k in range(ent + 1, len(B)) if B[k]["l"] <= stop), None)
        if hit is None or hit - ent > 14:
            continue
        # ماذا لو نُقل الوقف بدل تقبّله؟ أدنى قاع خلال خمس شمعات بعد ضربه
        after = B[hit:min(hit + 6, len(B))]
        deep = min(b["l"] for b in after)
        l1 = (B[ent]["c"] - stop) / B[ent]["c"] * 100
        l2 = (B[ent]["c"] - deep) / B[ent]["c"] * 100
        cand = dict(lo=lo, ent=ent, stop=stop, hit=hit, deep=deep,
                    l1=l1, l2=l2, mult=l2 / l1,
                    deep_i=min(range(hit, min(hit + 6, len(B))),
                               key=lambda k: B[k]["l"]))
        if cand["mult"] < 1.8:
            continue
        if best is None or cand["mult"] > best["mult"]:
            best = cand
    assert best is not None, "لا حالة يتضاعف فيها الضرر بعد ضرب الوقف"

    B0 = max(0, best["lo"] - 5)
    B1 = min(len(B) - 1, best["deep_i"] + 3)
    return dict(sym="SLV", name="صندوق الفضة", tf="يومي", bars=B,
                i0=B0, i1=B1, **best)


# ═════════════════════════ التشغيل ═════════════════════════
def all_facts():
    return dict(c1=c1_node(), c2=c2_anchor(), c3=c3_absorb(),
                c4=c4_effort(), c5=c5_move())


if __name__ == "__main__":
    F = all_facts()
    f = F["c1"]
    print(f'\n■ ١ العقدة — {f["name"]} {f["a"]}→{f["z"]}')
    print(f'   POC {f["poc"]:.2f} · VAH {f["vah"]:.2f} · VAL {f["val"]:.2f}')
    print(f'   عقدة رقيقة {f["lvn_p"]:.2f} · سميكة {f["hvn_p"]:.2f} · '
          f'النسبة {f["ratio"]*100:.0f}٪')
    print(f'   بعد النطاق ({f["after_n"]} شمعة): لمست الرقيقة {f["t_lvn"]} '
          f'وأغلقت داخلها {f["n_lvn"]} · لمست السميكة {f["t_hvn"]} '
          f'وأغلقت داخلها {f["n_hvn"]}')

    f = F["c2"]
    B = f["bars"]
    print(f'\n■ ٢ المرساة — {f["name"]}')
    print(f'   القاع المكنوس {B[f["p"]]["d"]} عند {f["lvl"]:.2f} · الغارة '
          f'{B[f["s"]]["d"]} قاع {f["stop"]:.2f} وإغلاق {f["ent"]:.2f} فوقه')
    print(f'   المرساة {f["av"][f["s"]]:.2f} — الدخول تحتها {f["disc"]:.2f}٪ '
          f'(خصم) والهدف {f["tgt"]:.2f} فوقها {f["prem"]:.2f}٪ (علاوة)')
    print(f'   {f["rr"]:.2f}R · بلغ الهدف {B[f["hit"]]["d"]} بعد '
          f'{f["bars_to_target"]} شمعة · أدنى قاع بينهما {f["low_after"]:.2f} '
          f'فوق الوقف · حجم الغارة {f["rel"]:.2f}× المتوسط')

    f = F["c3"]
    B = f["bars"]
    print(f'\n■ ٣ الامتصاص — {f["name"]}')
    print(f'   القمّة {B[f["hi"]]["d"]} {B[f["hi"]]["h"]:.2f} · الكسر '
          f'{B[f["br"]]["d"]} إغلاق {f["ent"]:.2f} بحجم '
          f'{f["rel"]:.2f}× المتوسط')
    print(f'   أعلى ما وصله {f["top_h"]:.2f} ثم أغلق تحت قاع '
          f'{B[f["base"]]["d"]} ({B[f["base"]]["l"]:.2f}) في '
          f'{B[f["fail"]]["d"]} — هبوط {f["drop"]:.1f}٪ خلال {f["span"]} شمعة')

    f = F["c4"]
    B = f["bars"]
    print(f'\n■ ٤ الجهد — {f["name"]} · المرساة {B[f["anchor"]]["d"]}')
    for x in f["days"]:
        print(f'   {x["d"]}: حجم {x["rel"]:.2f}× · جسم {x["ratio"]*100:.0f}٪ من المدى · '
              f'بُعد عن المرساة {x["dist"]:+.2f}٪ · بعد ٣ شمعات {x["a3"]:+.2f}٪ '
              f'وبعد ٥ {x["a5"]:+.2f}٪')
    print(f'   الأقرب {f["near"]["d"]} ({f["near"]["dist"]:+.2f}٪) صعد · '
          f'الأبعد {f["far"]["d"]} ({f["far"]["dist"]:+.2f}٪) هبط')

    f = F["c5"]
    B = f["bars"]
    print(f'\n■ ٥ التحريك — {f["name"]}')
    print(f'   دخول {B[f["ent"]]["d"]} {B[f["ent"]]["c"]:.2f} · وقف بنائي '
          f'{f["stop"]:.2f} ({f["l1"]:.2f}٪) ضُرب {B[f["hit"]]["d"]}')
    print(f'   ولو نُقل: القاع {f["deep"]:.2f} في {B[f["deep_i"]]["d"]} = '
          f'{f["l2"]:.2f}٪ — أي {f["mult"]:.1f}× الخسارة المخطّطة')

    if "--json" in sys.argv:
        thin = {k: {kk: vv for kk, vv in v.items()
                    if kk not in ("bars", "prof", "av")}
                for k, v in F.items()}
        json.dump(thin, open(OUT, "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1, default=str)
        print("\n→", OUT)
