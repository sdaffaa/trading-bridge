# -*- coding: utf-8 -*-
"""أسباب الدخول — تُحسب من الشموع الظاهرة حتى شمعة التنفيذ، بلا نظر للمستقبل.

كل سبب دالة تفحص شرطاً وتعيد رقماً حقيقياً أو None. ما لا يتحقق لا يُعرض.
هذه هي «الأسباب الواقعية»: لو لم يتحقق الشرط في السوق، لا يظهر السطر.
"""
import statistics as st


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
    return ("مع الاتجاه القريب", f"الإغلاق فوق متوسط {n} شمعة ({ma:,.2f})", w[i]["c"] - ma)


def respected(w, a, b, lvl, above=True):
    """كم شمعة احترمت المستوى قبل الحدث؟ المستوى المُختبَر أقوى من المرسوم."""
    n = sum(1 for c in w[a:b] if (c["l"] > lvl if above else c["h"] < lvl))
    return ("مستوى مُختبَر", f"{n} شمعة احترمته قبل الحدث", n) if n >= 4 else None


def rr(ENT, STP, TGT):
    U = ENT - STP
    return ("عائد مقابل مخاطرة", f"{U:,.2f} مقابل {TGT - ENT:,.2f} — نسبة ١:٢", 2.0)


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
