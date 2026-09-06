# -*- coding: utf-8 -*-
"""أسباب الدخول — تُحسب من الشموع الظاهرة حتى شمعة التنفيذ، بلا نظر للمستقبل.

كل سبب دالة تفحص شرطاً وتعيد رقماً حقيقياً أو None. ما لا يتحقق لا يُعرض.
هذه هي «الأسباب الواقعية»: لو لم يتحقق الشرط في السوق، لا يظهر السطر.
"""
import statistics as st


def _n(v):
    """تنسيق فرقٍ سعري بلا ضجيج عشري: 0.1001 تُقرأ 0.10 لا كما خزّنها الحاسوب."""
    a = abs(v)
    if a >= 100: return f"{v:,.0f}"
    if a >= 1: return f"{v:,.2f}"
    if a >= 0.01: return f"{v:.3f}"
    return f"{v:.5f}"


def _p(v):
    """تنسيق **مستوىً سعري** — غير `_n` الذي يُنسّق فرقاً.

    `above_ma` كانت تطبع المتوسط بـ`,.2f`، فمتوسط الأسترالي/الدولار
    0.70153 يصير «0.70» — مستوىً لا يدلّ على شيء. المستوى يحتاج خانات
    أداته لا خانات الفرق."""
    a = abs(v)
    if a >= 1000: return f"{v:,.0f}"
    if a >= 100: return f"{v:,.2f}"
    if a >= 1: return f"{v:,.3f}"
    return f"{v:.5f}"


def _rng(w):
    return max(c["h"] for c in w) - min(c["l"] for c in w)


def equal_lows(w, fill, lvl, R):
    """كم شمعة قاعها ملاصق للمستوى؟ تراكم القيعان = تراكم أوامر إيقاف تحتها."""
    n = sum(1 for c in w[:fill] if abs(c["l"] - lvl) <= R * 0.055)
    return ("قيعان متلاصقة", f"{n} قيعان عند المستوى نفسه — سيولة متراكمة تحته", n) if n >= 3 else None


def rejection(w, i, name="الشمعة"):
    """نسبة الذيل السفلي من مدى الشمعة: رفضٌ مقيس لا انطباع."""
    c = w[i]; rg = c["h"] - c["l"]
    if rg <= 0: return None
    wick = min(c["o"], c["c"]) - c["l"]
    p = wick / rg
    return ("ذيل رفض", f"الذيل السفلي {p*100:.0f}٪ من مدى {name} — البائع فقد السيطرة", p) if p >= 0.35 else None


def displacement(w, i, look=10):
    """مدى شمعة الحدث مقابل وسيط ما قبلها: الاندفاع يُقاس ولا يُوصف."""
    prev = [c["h"] - c["l"] for c in w[max(0, i - look):i]]
    if len(prev) < 5: return None
    m = st.median(prev)
    if m <= 0: return None
    k = (w[i]["h"] - w[i]["l"]) / m
    return ("إزاحة", f"مدى الشمعة {k:.1f}× وسيط العشر السابقة — دخول سيولة فعلي", k) if k >= 1.4 else None


def above_ma(w, i):
    """الإغلاق فوق متوسط الفترة المتاحة: الاتجاه القريب مع الصفقة لا ضدها."""
    n = min(20, i)
    if n < 8: return None
    ma = sum(c["c"] for c in w[i - n:i]) / n
    if w[i]["c"] <= ma: return None
    return ("مع الاتجاه القريب", f"الإغلاق فوق متوسط {n} شمعة ({_p(ma)})", w[i]["c"] - ma)


def respected(w, a, b, lvl, above=True):
    """كم شمعة احترمت المستوى قبل الحدث؟ المستوى المُختبَر أقوى من المرسوم."""
    n = sum(1 for c in w[a:b] if (c["l"] > lvl if above else c["h"] < lvl))
    return ("مستوى مُختبَر", f"{n} شمعة احترمته قبل الحدث", n) if n >= 4 else None


def rr(ENT, STP, TGT):
    """عائد مقابل مخاطرة — بخاناتٍ تكفي الأداة.

    كان التنسيق `,.2f` ثابتاً، وهو يكفي المؤشرات والذهب ويبتلع الفوركس:
    مخاطرة الأسترالي/الدولار 0.00056 تُطبع «0.00 مقابل 0.00» فتظهر على
    لوحة أسباب الريل صفراً (رُصد 2026-09-04 على النافذتين ٤٨ و٥٠).
    والتنسيق الآن `_n` نفسه الذي تستعمله بقيّة الأسباب — ولا عتبة تغيّرت."""
    return ("عائد مقابل مخاطرة",
            f"{_n(ENT - STP)} مقابل {_n(TGT - ENT)} — نسبة ١:٢", 2.0)


# ═══════════ أسباب ريل «جلسة متداول» — أربعة أنماط دخول ═══════════
# كلها تتبع القاعدة نفسها: قيمة مقيسة أو `None`. الفرق أن هذه تُقاس على
# فهارس `sheet_candidates.json` (`i1/i2/ipdl` · `ca/cb/rt/rb` · `chi/clo`)
# التي لم تُستعمل قبل اليوم، فيختلف سبب الدخول باختلاف النافذة لا نصّها.

def equal_highs(w, i1, i2, R):
    """قمّتان متساويتان: الفرق بينهما نسبةً إلى المدى — تحت ٤٪ يُعدّ تساوياً."""
    d = abs(w[i1]["h"] - w[i2]["h"])
    if R <= 0 or d > R * 0.04:
        return None
    return ("قمّتان متساويتان", f"الفرق بينهما {_n(d)} فقط = {d/R*100:.1f}٪ من المدى "
                                f"— سيولة أوامر فوقهما", d)


def swept(w, i2, fill, R):
    """كنسٌ فعلي: السعر تجاوز القمّة الثانية ثم أغلق تحتها قبل التنفيذ."""
    hi = w[i2]["h"]
    j = next((k for k in range(i2 + 1, fill + 1)
              if w[k]["h"] > hi and w[k]["c"] < hi), None)
    if j is None:
        return None
    over = (w[j]["h"] - hi)
    return ("كنس ثم إغلاق تحت", f"تجاوزها بـ{_n(over)} ثم أغلق تحتها — "
                                f"اصطياد سيولة لا اختراق", over)


def compression(w, a, b, R):
    """انضغاط النطاق: عرضه نسبةً إلى مدى الشاشة — الضيق يسبق الحركة."""
    if b <= a or R <= 0:
        return None
    rt = max(c["h"] for c in w[a:b + 1]); rb = min(c["l"] for c in w[a:b + 1])
    p = (rt - rb) / R
    if p > 0.42:
        return None
    return ("نطاق منضغط", f"{b-a+1} شمعة داخل {p*100:.0f}٪ من مدى الشاشة — "
                          f"تجميع قبل الحركة", p)


def breakout_close(w, i, lvl, R):
    """كسر بإغلاق لا بفتيل: مقدار تجاوز الجسم للحدّ."""
    d = w[i]["c"] - lvl
    if d <= 0 or R <= 0 or d < R * 0.004:
        return None
    return ("كسر بإغلاق", f"الجسم أغلق فوق الحدّ بـ{_n(d)} = {d/R*100:.1f}٪ "
                          f"من المدى — لا فتيل عابر", d)


def steps_down(w, hi_a, hi_b, lo_a, lo_b, R):
    """قناة هابطة: تدرّج القمم والقيعان معاً — أحدهما وحده ليس قناة."""
    dh = w[hi_a]["h"] - w[hi_b]["h"]
    dl = w[lo_a]["l"] - w[lo_b]["l"]
    if R <= 0 or dh <= 0 or dl <= 0:
        return None
    return ("قمم وقيعان متدرّجة", f"القمم نزلت {_n(dh)} والقيعان {_n(dl)} — "
                                  f"قناة هابطة لا هبوط عشوائي", min(dh, dl) / R)


def retest_of(w, brk, lvl, fill):
    """العودة لاختبار الحدّ المكسور: كم شمعة بين الكسر والاختبار."""
    if fill <= brk:
        return None
    lo = min(c["l"] for c in w[brk + 1:fill + 1])
    if lo > lvl:
        return None
    return ("إعادة اختبار الحدّ", f"عاد للحدّ بعد {fill-brk} شمعات من كسره — "
                                  f"المقاومة صارت دعماً", fill - brk)


def _pack(rows, S):
    """يُرجع (الأسباب المتحقّقة، سطر العائد) — الشرط ثلاثة فأكثر عدا العائد."""
    ok = [dict(t=t, d=d) for t, d, _ in (r for r in rows if r)]
    return ok, dict(zip(("t", "d"), rr(S["ENT"], S["STP"], S["TGT"])[:2]))


def build_desk(S):
    """أسباب الدخول بحسب فئة النافذة (`cls`) — لكل فئة فهارسها ومقاييسها.

    ترجع `(reasons, rr_row)`؛ والبنّاء يرفض ما دون ثلاثة أسباب متحقّقة."""
    w, fill, cls = S["w"], S["fill"], S["cls"]
    R = _rng(w[:fill + 1])
    if cls == "sweep":
        rows = [equal_highs(w, S["i1"], S["i2"], R),
                swept(w, S["i2"], fill, R),
                equal_lows(w, fill, w[S["ipdl"]]["l"], R),
                rejection(w, fill, "شمعة العودة"),
                displacement(w, S["bk"]),
                above_ma(w, fill)]
    elif cls == "consol":
        rt = max(w[k]["h"] for k in range(S["ca"], S["cb"] + 1))
        rows = [compression(w, S["ca"], S["cb"], R),
                breakout_close(w, S["bk"], rt, R),
                retest_of(w, S["bk"], S["ZT"], fill),
                rejection(w, fill, "شمعة العودة"),
                above_ma(w, fill)]
    elif cls == "chan":
        hi, lo = S["chi"], S["clo"]
        rows = [steps_down(w, hi[0], hi[1], lo[0], lo[1], R),
                breakout_close(w, S["bk"], w[hi[1]]["h"], R),
                respected(w, hi[0], S["bk"], w[hi[0]]["h"], above=False),
                rejection(w, fill, "شمعة العودة"),
                above_ma(w, fill)]
    else:                                   # zone — كسر هيكل ثم منطقة أصل
        rows = [breakout_close(w, S["bk"], S["LH"], R),
                displacement(w, S["bk"]),
                respected(w, S["iob"] + 1, S["bk"], S["ZT"], above=True),
                rejection(w, fill, "شمعة العودة"),
                above_ma(w, fill)]
    return _pack(rows, S)


def build(S):
    w, fill = S["w"], S["fill"]
    R = _rng(w[:fill + 1])          # المدى المرئي وقت التنفيذ لا المدى الكامل
    out = []
    if S["key"] == "sweep":
        out = [equal_lows(w, fill, S["LOW"], R),
               rejection(w, fill, "شمعة الكنس"),
               displacement(w, fill),
               above_ma(w, fill)]
    elif S["key"] == "fvg":
        gap = S["GH"] - S["GL"]
        out = [("فجوة مقيسة", f'{gap:,.2f} دولاراً = {gap / R * 100:.0f}٪ من مدى الشاشة', gap),
               respected(w, S["k"] + 2, fill, S["GH"], above=True),
               rejection(w, fill, "شمعة العودة"),
               above_ma(w, fill)]
    else:
        out = [respected(w, S["p"] + 1, S["brk"], S["LH"], above=False),
               ("كسر بإغلاق", f'الإغلاق فوق القمة بـ{w[S["brk"]]["c"] - S["LH"]:,.2f} دولاراً', 1),
               rejection(w, fill, "شمعة العودة"),
               above_ma(w, fill)]
    out = [o for o in out if o]
    out.append(rr(S["ENT"], S["STP"], S["TGT"]))
    return [dict(t=t, d=d) for t, d, _ in out[:4]]
