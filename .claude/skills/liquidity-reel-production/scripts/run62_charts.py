# -*- coding: utf-8 -*-
"""جارتات تشغيلة ٦٢ — **تخطيطية** لثلاث وحدات، وحقيقية للفنيّتين.

مخزون `sheet_candidates.json` نفد إلا نافذتين حرّتين، وقد أخذتهما
الوحدتان الفنيّتان (ريلٌ وكاروسيل). فالثلاث الباقية تُبنى بجارتات
تخطيطية على قاعدة §11 (2026-08-06) بشروطها الثلاثة:

1. **الشارة تقول ما هو**: «مثال تخطيطي» على كل رسم.
2. **ما لا تُثبته الشموع لا يُرسم**: كل ادّعاء يُقاس بـ`assert` على
   السلسلة المولّدة قبل أن يُرسم.
3. **القياس بالنِّسب والأعداد لا بالنقاط**: السلسلة بلا أداة فلا وحدة
   لها — فالأرقام هنا **عددُ شمعات** أو **مضاعفُ مخاطرة** أو **نسبةٌ إلى
   وسيط الشمعة**، ولا يُطبع سعرٌ واحد.

    python3 run62_charts.py
"""
import statistics as st

from reel_build import INK, TEAL, TEAL_D, RED, GREY, htext, gen
from run15_charts import zbox, xm, tick, hl, badge, frame
import run31_charts as RC
from run58_charts import ar, rt, why, sm, band, mark, span, ranges
from run59_charts import tag, spanx, vspan, xr, _pt


def _clean(cs, keep=()):
    """شموع ممكنة فقط: لا قاعٌ فوق جسمه ولا فتيلٌ شوكة."""
    for j, c in enumerate(cs):
        top, bot = max(c["o"], c["c"]), min(c["o"], c["c"])
        c["h"] = max(min(c["h"], top + 0.9), top)
        if j not in keep:
            c["l"] = min(max(c["l"], bot - 0.9), bot)
    return cs


def _med(W):
    return st.median([c["h"] - c["l"] for c in W])


def _lab(x, y, txt, col, fs=19):
    import run15_charts as R15
    if R15.MINIMAL:
        return ""
    return htext(x, y, txt, col, round(fs * RC._SC[0]))


def _ring(x, y, col, r=12, sw=3):
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="none" stroke="{col}" stroke-width="{sw}"/>'


# ═════════ ١ · رجوع — الأسبوع الذي غبتَ فيه (نفسية) ═════════
A_SEED = 6207
A_ANCH = [(0, 20.0), (6, 21.4), (12, 20.6), (18, 22.2), (24, 21.2), (33, 23.6)]
A_N = 34
A_LVL = 20.55                 # المستوى الذي تركتَه على الشاشة
A_OUT = (8, 19)               # مدى الغياب — اثنتا عشرة شمعة
A_TOUCH = (11, 16)            # لمستان داخل الغياب
A_BACK = 20                   # شمعة العودة
A_FIRST = 27                  # أول لمسة بعد العودة


def _series_a():
    cs = gen(A_ANCH, A_N, A_SEED, wick=0.5, bn=0.6)
    for j in A_TOUCH + (A_FIRST,):
        cs[j]["l"] = A_LVL
        cs[j]["c"] = max(cs[j]["c"], A_LVL + 0.35)
        cs[j]["h"] = max(cs[j]["h"], cs[j]["c"] + 0.12)
    for j, c in enumerate(cs):
        if j not in A_TOUCH + (A_FIRST,):
            c["l"] = max(c["l"], A_LVL + 0.10)
            c["o"] = max(c["o"], c["l"]); c["c"] = max(c["c"], c["l"])
            c["h"] = max(c["h"], c["o"], c["c"])
    return _clean(cs, keep=A_TOUCH + (A_FIRST,))


WA = _series_a()
RA = {"sym": "SCHEMATIC-A", "slug": "مثال تخطيطي أ", "w": WA}
assert all(abs(WA[j]["l"] - A_LVL) < 1e-9 for j in A_TOUCH), "اللمستان لا تقعان على المستوى"
assert min(WA[j]["l"] for j in range(A_OUT[0], A_OUT[1] + 1)) == A_LVL, "قاعٌ أدنى داخل الغياب"
assert A_TOUCH[0] >= A_OUT[0] and A_TOUCH[1] <= A_OUT[1], "اللمستان خارج مدى الغياب"
assert min(WA[j]["l"] for j in range(A_BACK, A_FIRST)) > A_LVL, "لمسةٌ قبل أول فرصة"
_A_FAR = (WA[A_BACK]["c"] - A_LVL) / _med(WA)
# الحدّ يحرس المعنى لا رقماً بعينه: العودة يجب أن تكون فوق المستوى
# بأكثر من شمعة كاملة (وإلا فلا «بُعد» يُروى)، ودون خمس (وإلا خرج
# المستوى من اللوحة). والرقم المكتوب هو المقيس لا المطلوب.
assert 1.2 <= _A_FAR <= 4.5, f"بُعد العودة {_A_FAR:.2f}"


def _ga(Wd, H):
    # المستوى عند أدنى السلسلة، فيُرفَع القاع بحشوةٍ أوسع
    # وإلا داس خطُّه وحلقاتُه سطرَ «لماذا» أسفل اللوحة.
    return frame(WA, Wd, H, pad=0.10, pb=66)


def g_away(r=None, Wd=880, H=250):
    """اثنتا عشرة شمعة مرّت وأنت غير موجود."""
    a, b = A_OUT
    assert b - a + 1 == 12, b - a + 1
    svg, x, y, slot = _ga(Wd, H)
    # الشريط تركوازي لا رمادي: قاعدةُ الهوية §3-4 تمنع الصناديق الرمادية،
    # ومعنى «الغياب» يحمله القوسُ ووسمُه لا لونُ التعبئة.
    svg += band(x(a) - slot * .5, x(b) + slot * .5, y(max(c["h"] for c in WA[a:b+1])),
                y(min(c["l"] for c in WA[a:b+1])), TEAL, 0.13)
    top = min(y(WA[k]["h"]) for k in range(a, b + 1))
    svg += spanx(x(a) - slot * .5, x(b) + slot * .5, top, f'{ar(b-a+1)} شمعة', GREY)
    svg += RC._title(Wd, rt("الشمعات التي مرّت بغيابك"))
    svg += why(Wd, H, f'{ar(b-a+1)} شمعة تشكّلت والشاشة مقفلة', GREY)
    svg += sm(Wd, H, "والسوق ما انتظرك ولا مشى ضدّك — مشى وبس", TEAL_D)
    return svg + badge(Wd, "مثال تخطيطي", True) + "</svg>"


def g_missed(r=None, Wd=880, H=250):
    """وفيها لمستان للمستوى نفسه — فرصتان لم تكن على الشاشة."""
    svg, x, y, slot = _ga(Wd, H)
    svg += hl(x(0) - slot * .5, x(A_N - 1) + slot * .5, y(A_LVL), INK, 1.8)
    for j in A_TOUCH:
        svg += _ring(x(j), y(WA[j]["l"]), TEAL_D, 11, 2.6)
    svg += RC._title(Wd, rt("لمستان فاتتاك"))
    svg += why(Wd, H, 'لمستان للمستوى نفسه وقعتا داخل غيابك', TEAL_D)
    svg += sm(Wd, H, "ومن رجع يدوّر تعويضهن دخل على غير شرطه")
    return svg + badge(Wd, "مثال تخطيطي", True) + "</svg>"


def g_far(r=None, Wd=880, H=250):
    """ويوم رجعت، السعر بعيدٌ عن مستواك بثلاث شمعات."""
    svg, x, y, slot = _ga(Wd, H)
    svg += hl(x(0) - slot * .5, x(A_N - 1) + slot * .5, y(A_LVL), INK, 1.8)
    svg += mark(x(A_BACK), slot, y(WA[A_BACK]["h"]), y(WA[A_BACK]["l"]), TEAL_D, 0.22)
    # وسمُ القوس يُرفع فوق قمم الجوار بيدنا: `vspan` يضعه تحت الطرف الأدنى،
    # والطرف الأدنى هنا هو المستوى نفسه عند قاع اللوحة فلا فراغ تحته،
    # فيسقط إلى بديله فوق الطرف الأعلى — وهناك شمعاتٌ يمرّ عليها.
    svg += vspan(x(A_BACK), y(WA[A_BACK]["c"]), y(A_LVL), "", INK, H=H)
    ly = (min(y(WA[j]["h"]) for j in range(max(0, A_BACK - 2), min(A_N, A_BACK + 3)))
          - round(16 * RC._SC[0]))
    assert ly > round(76 * RC._SC[0]), "لا فراغ فوق قمم الجوار لوسم القوس"
    svg += _lab(x(A_BACK), ly, rt(f'{xr(_A_FAR)} الشمعة'), INK, 16)
    svg += RC._title(Wd, rt("بعيدٌ عن مستواك"))
    svg += why(Wd, H, f'يوم رجعت، المسافة إلى المستوى {xr(_A_FAR)} وسيط الشمعة', GREY)
    svg += sm(Wd, H, "فالسعر اللي بذاكرتك مو السعر اللي على الشاشة", TEAL_D)
    return svg + badge(Wd, "مثال تخطيطي", True) + "</svg>"


def g_wait(r=None, Wd=880, H=250):
    """وأول فرصة صادقة جاءت بعد سبع شمعات من عودتك."""
    n = A_FIRST - A_BACK
    assert n == 7, n
    svg, x, y, slot = _ga(Wd, H)
    svg += hl(x(0) - slot * .5, x(A_N - 1) + slot * .5, y(A_LVL), INK, 1.8)
    svg += mark(x(A_BACK), slot, y(WA[A_BACK]["h"]), y(WA[A_BACK]["l"]), GREY, 0.20)
    svg += _ring(x(A_FIRST), y(WA[A_FIRST]["l"]), TEAL_D, 11, 2.6)
    top = min(y(WA[k]["h"]) for k in range(A_BACK, A_FIRST + 1))
    svg += spanx(x(A_BACK) - slot * .5, x(A_FIRST) + slot * .5, top, f'{ar(n)} شمعات', TEAL_D)
    svg += RC._title(Wd, rt("أول فرصة بعد العودة"))
    svg += why(Wd, H, f'{ar(n)} شمعات بين عودتك وأول لمسة للمستوى', TEAL_D)
    svg += sm(Wd, H, "والسبع هذي شغلها انتظار — مو تعويض")
    return svg + badge(Wd, "مثال تخطيطي", True) + "</svg>"


def g_all(r=None, Wd=880, H=250):
    """السلسلة كاملة — مرجع كل عددٍ في الوحدة."""
    assert len(WA) == A_N, len(WA)
    svg, x, y, slot = _ga(Wd, H)
    svg += hl(x(0) - slot * .5, x(A_N - 1) + slot * .5, y(A_LVL), GREY, 1.4, "5 6")
    svg += RC._title(Wd, rt("السلسلة كاملة"))
    svg += why(Wd, H, f'{ar(A_N)} شمعة تخطيطية — والأرقام كلها أعدادُ شمعات ونِسب', INK)
    svg += sm(Wd, H, "ولا سعرَ مكتوبٌ هنا، لأن الرسم تخطيطي لا طبعةُ سوق")
    return svg + badge(Wd, "مثال تخطيطي", True) + "</svg>"


# ═════════ ٢ · سحوبات — الربح بمضاعف المخاطرة (مالية) ═════════
B_SEED = 4407
B_ANCH = [(0, 30.0), (5, 29.0), (10, 29.4), (16, 32.6), (22, 31.8), (29, 34.4)]
B_N = 30
B_ENT = 12                    # شمعة الدخول
B_STOP_PAD = 0.35


def _series_b():
    cs = gen(B_ANCH, B_N, B_SEED, wick=0.55, bn=0.6)
    c = cs[B_ENT]
    lo = min(cs[j]["l"] for j in range(B_ENT - 3, B_ENT + 1))
    c["l"] = lo - B_STOP_PAD              # ذيل رفض واضح
    c["c"] = max(c["c"], c["o"]) + 0.10
    c["h"] = max(c["h"], c["c"] + 0.15)
    return _clean(cs, keep=(B_ENT,))


WB = _series_b()
RB = {"sym": "SCHEMATIC-B", "slug": "مثال تخطيطي ب", "w": WB}
B_E = WB[B_ENT]["c"]
B_S = WB[B_ENT]["l"] - 0.05
B_R = B_E - B_S
B_T = B_E + 2 * B_R
B_HIT = next((j for j in range(B_ENT + 1, B_N) if WB[j]["h"] >= B_T), None)
assert B_HIT is not None, "الهدف ٢R لم يتحقّق على السلسلة"
assert min(WB[j]["l"] for j in range(B_ENT + 1, B_HIT + 1)) > B_S, "الوقف ضُرب قبل الهدف"
_B_K = B_R / _med(WB)
assert 0.7 <= _B_K <= 2.2, f"{_B_K:.2f}"


def _gb(Wd, H):
    return frame(WB, Wd, H, pad=0.10, pb=66)


def _b_lines(x, y, slot, n):
    """أسعار الخطة تبدأ من شمعة الدخول لا من أوّل اللوحة.

    الأمر الدائم «الخطوط تتوقف عند شمعتها»: خطُّ دخولٍ ممدودٌ فوق شمعاتٍ
    سبقت القرار يوهم أن السعر كان مرصوداً قبل أن يُتّخذ."""
    L, Rt = x(B_ENT) - slot * .5, x(n - 1) + slot * .5
    s = hl(L, Rt, y(B_E), TEAL_D, 1.8) + hl(L, Rt, y(B_S), RED, 1.8, "6 6")
    return s + hl(L, Rt, y(B_T), TEAL_D, 1.6, "7 6")


def k_risk(r=None, Wd=880, H=250):
    """وحدةُ الحساب مخاطرةٌ واحدة — لا مبلغ."""
    svg, x, y, slot = _gb(Wd, H)
    svg += _b_lines(x, y, slot, B_N)
    svg += band(x(B_ENT) - slot * .5, x(B_N - 1) + slot * .5, y(B_E), y(B_S), TEAL, 0.10)
    svg += vspan(x(B_ENT) + slot * 3.2, y(B_E), y(B_S), "مخاطرةٌ واحدة", TEAL_D, H=H)
    svg += RC._title(Wd, rt("مخاطرةٌ واحدة = وحدة الحساب"))
    svg += why(Wd, H, "من الدخول إلى الوقف مسافةٌ واحدة، وهي وحدة القياس", INK)
    svg += sm(Wd, H, "وكل ربحٍ يُقال بعدها بمضاعفها لا بالدنانير", TEAL_D)
    return svg + badge(Wd, "مثال تخطيطي", True) + "</svg>"


def k_two(r=None, Wd=880, H=250):
    """والهدف مضاعفان — تحقّق على السلسلة لا على الورق."""
    svg, x, y, slot = _gb(Wd, H)
    svg += _b_lines(x, y, slot, B_N)
    svg += mark(x(B_HIT), slot, y(WB[B_HIT]["h"]), y(WB[B_HIT]["l"]), TEAL_D, 0.22)
    svg += tick(x(B_HIT), y(B_T) - 20)
    svg += RC._title(Wd, rt("الهدف مضاعفان"))
    svg += why(Wd, H, f'تحقّق بعد {ar(B_HIT-B_ENT)} شمعات من الدخول — ٢R', TEAL_D)
    svg += sm(Wd, H, "والرقم على الشاشة صار مضاعفين، مو مبلغاً بعد")
    return svg + badge(Wd, "مثال تخطيطي", True) + "</svg>"


def k_med(r=None, Wd=880, H=250):
    """والمخاطرة نفسها تُقاس بشمعة السلسلة."""
    svg, x, y, slot = _gb(Wd, H)
    svg += _b_lines(x, y, slot, B_N)
    j = max(range(4, B_N - 6), key=lambda k: min(WB[m]["l"] for m in range(k - 2, k + 3)) - B_E)
    assert min(WB[m]["l"] for m in range(j - 2, j + 3)) > B_E, "لا موضع خالٍ للقوس"
    svg += vspan(x(j), y(B_E), y(B_S), f'{xr(_B_K)} الشمعة', TEAL_D, H=H)
    svg += RC._title(Wd, rt("المخاطرة بمقياس الشمعة"))
    svg += why(Wd, H, f'مسافة الوقف {xr(_B_K)} وسيط شمعة السلسلة', INK)
    svg += sm(Wd, H, "وبها يُحسب الحجم قبل أي كلام عن سحب", TEAL_D)
    return svg + badge(Wd, "مثال تخطيطي", True) + "</svg>"


def k_hold(r=None, Wd=880, H=250):
    """وزمنُ الصفقة يُعدّ بالشمعات لا بالساعات."""
    n = B_HIT - B_ENT
    svg, x, y, slot = _gb(Wd, H)
    svg += mark(x(B_ENT), slot, y(WB[B_ENT]["h"]), y(WB[B_ENT]["l"]), TEAL_D, 0.22)
    svg += mark(x(B_HIT), slot, y(WB[B_HIT]["h"]), y(WB[B_HIT]["l"]), TEAL_D, 0.22)
    top = min(y(WB[k]["h"]) for k in range(B_ENT, B_HIT + 1))
    svg += spanx(x(B_ENT) - slot * .5, x(B_HIT) + slot * .5, top, f'{ar(n)} شمعات', TEAL_D)
    svg += RC._title(Wd, rt("زمن الصفقة بالشمعات"))
    svg += why(Wd, H, f'{ar(n)} شمعات بين الضغطة وبلوغ المضاعفين', TEAL_D)
    svg += sm(Wd, H, "وجدول السحب يُكتب بعد أن يُغلق الأمر، لا قبله")
    return svg + badge(Wd, "مثال تخطيطي", True) + "</svg>"


def k_all(r=None, Wd=880, H=250):
    """السلسلة كاملة — مرجع كل نسبةٍ في الوحدة."""
    assert len(WB) == B_N, len(WB)
    svg, x, y, slot = _gb(Wd, H)
    svg += hl(x(0) - slot * .5, x(B_N - 1) + slot * .5, y(WB[0]["c"]), GREY, 1.4, "5 6")
    svg += RC._title(Wd, rt("السلسلة كاملة"))
    svg += why(Wd, H, f'{ar(B_N)} شمعة تخطيطية — والأرقام مضاعفاتٌ ونِسب', INK)
    svg += sm(Wd, H, "ولا مبلغَ هنا: المبلغ يجي من رصيدك أنت")
    return svg + badge(Wd, "مثال تخطيطي", True) + "</svg>"


# ═════════ ٣ · ترتيب — خطوات القرار الأربع (أساسية) ═════════
C_SEED = 8200
C_ANCH = [(0, 50.0), (5, 48.6), (9, 49.2), (14, 52.8), (20, 51.4), (27, 54.6)]
C_N = 28
C_LVL_I = 8                   # الشمعة التي رُسم منها المستوى
C_BK = 14                     # شمعة الكسر
C_BACK = 20                   # شمعة العودة إلى المستوى
C_ENT = 21                    # شمعة الدخول


def _series_c():
    cs = gen(C_ANCH, C_N, C_SEED, wick=0.5, bn=0.6)
    lvl = max(cs[C_LVL_I]["o"], cs[C_LVL_I]["c"])
    for j in range(C_LVL_I + 1, C_BK):
        cs[j]["h"] = min(cs[j]["h"], lvl - 0.05)
        cs[j]["o"] = min(cs[j]["o"], cs[j]["h"]); cs[j]["c"] = min(cs[j]["c"], cs[j]["h"])
        cs[j]["l"] = min(cs[j]["l"], cs[j]["o"], cs[j]["c"])
    # شمعة الكسر تفتح تحت المستوى وتغلق فوقه: بغير ذلك تخرج من `gen`
    # شمعةً هابطةً (كحلية) أغلقت فوق الحدّ — واللون يناقض العنوان.
    cs[C_BK]["o"] = min(cs[C_BK]["o"], lvl - 0.20)
    cs[C_BK]["c"] = lvl + 0.55
    cs[C_BK]["h"] = max(cs[C_BK]["h"], cs[C_BK]["c"] + 0.15)
    cs[C_BK]["l"] = min(cs[C_BK]["l"], cs[C_BK]["o"] - 0.05)
    cs[C_BACK]["l"] = lvl - 0.10
    cs[C_BACK]["c"] = max(cs[C_BACK]["c"], lvl + 0.08)
    cs[C_ENT]["l"] = lvl
    cs[C_ENT]["c"] = max(cs[C_ENT]["c"], lvl + 0.45)
    cs[C_ENT]["h"] = max(cs[C_ENT]["h"], cs[C_ENT]["c"] + 0.12)
    return _clean(cs, keep=(C_BACK, C_ENT)), lvl


WC, C_LVL = _series_c()
RC_ = {"sym": "SCHEMATIC-C", "slug": "مثال تخطيطي ج", "w": WC}
assert max(WC[j]["h"] for j in range(C_LVL_I + 1, C_BK)) < C_LVL, "المستوى مُخترق قبل الكسر"
assert WC[C_BK]["c"] > C_LVL, "شمعة الكسر لم تغلق فوق المستوى"
assert WC[C_BK]["o"] < C_LVL < WC[C_BK]["c"], "جسم شمعة الكسر لا يعبر المستوى"
assert WC[C_BACK]["l"] < C_LVL < WC[C_BACK]["c"], "العودة لم تلمس المستوى"
_C_WICK = (min(WC[C_ENT]["o"], WC[C_ENT]["c"]) - WC[C_ENT]["l"]) / (WC[C_ENT]["h"] - WC[C_ENT]["l"])
assert _C_WICK >= 0.35, f"ذيل الدخول {_C_WICK:.2f}"


def _gc(Wd, H):
    return frame(WC, Wd, H, pad=0.10, pb=66)


def p_level(r=None, Wd=880, H=250):
    """الخطوة الأولى: المستوى يُرسم من شمعةٍ بعينها."""
    svg, x, y, slot = _gc(Wd, H)
    svg += hl(x(C_LVL_I) - slot * .5, x(C_N - 1) + slot * .5, y(C_LVL), INK, 1.8)
    svg += mark(x(C_LVL_I), slot, y(WC[C_LVL_I]["h"]), y(WC[C_LVL_I]["l"]), INK, 0.20)
    svg += RC._title(Wd, rt("١ · من أي شمعة رُسم"))
    svg += why(Wd, H, "المستوى حدُّ شمعةٍ واحدة — لا خطٌّ مرسومٌ بالنظر", INK)
    svg += sm(Wd, H, "ولو ما تقدر تشاورها بإصبعك، فما رسمت شيئاً")
    return svg + badge(Wd, "مثال تخطيطي", True) + "</svg>"


def p_break(r=None, Wd=880, H=250):
    """الخطوة الثانية: الإغلاق فوقه — لا الفتيل."""
    n = C_BK - C_LVL_I
    svg, x, y, slot = _gc(Wd, H)
    svg += hl(x(C_LVL_I) - slot * .5, x(C_N - 1) + slot * .5, y(C_LVL), INK, 1.8)
    svg += mark(x(C_BK), slot, y(WC[C_BK]["h"]), y(WC[C_BK]["l"]), TEAL_D, 0.22)
    top = min(y(WC[k]["h"]) for k in range(C_LVL_I, C_BK + 1))
    svg += spanx(x(C_LVL_I) - slot * .5, x(C_BK) + slot * .5, top, f'{ar(n)} شمعات', GREY)
    svg += RC._title(Wd, rt("٢ · الإغلاق فوقه"))
    svg += why(Wd, H, f'{ar(n)} شمعات قبل أن يُغلق فوق المستوى', TEAL_D)
    svg += sm(Wd, H, "والفتيل اللي دخل ورجع ما يكسر شي")
    return svg + badge(Wd, "مثال تخطيطي", True) + "</svg>"


def p_back(r=None, Wd=880, H=250):
    """الخطوة الثالثة: العودة إليه — الحدّ المكسور يصير مرجعاً."""
    n = C_BACK - C_BK
    svg, x, y, slot = _gc(Wd, H)
    svg += hl(x(C_LVL_I) - slot * .5, x(C_N - 1) + slot * .5, y(C_LVL), INK, 1.8)
    svg += mark(x(C_BACK), slot, y(WC[C_BACK]["h"]), y(WC[C_BACK]["l"]), TEAL_D, 0.22)
    svg += _ring(x(C_BACK), y(C_LVL), TEAL_D, 11, 2.6)
    top = min(y(WC[k]["h"]) for k in range(C_BK, C_BACK + 1))
    svg += spanx(x(C_BK) - slot * .5, x(C_BACK) + slot * .5, top, f'{ar(n)} شمعات', GREY)
    svg += RC._title(Wd, rt("٣ · العودة إليه"))
    svg += why(Wd, H, f'{ar(n)} شمعات بين الكسر والعودة إلى الحدّ نفسه', TEAL_D)
    svg += sm(Wd, H, "وهني يصير الحدُّ مرجعاً، لا سعرَ تنفيذٍ بعد")
    return svg + badge(Wd, "مثال تخطيطي", True) + "</svg>"


def p_entry(r=None, Wd=880, H=250):
    """الخطوة الرابعة: شمعةٌ ترفض النزول — وذيلها يُقاس."""
    svg, x, y, slot = _gc(Wd, H)
    svg += hl(x(C_LVL_I) - slot * .5, x(C_N - 1) + slot * .5, y(C_LVL), INK, 1.8)
    svg += mark(x(C_ENT), slot, y(WC[C_ENT]["h"]), y(WC[C_ENT]["l"]), TEAL_D, 0.24)
    svg += tag(x(C_ENT), y(WC[C_ENT]["h"]), y(WC[C_ENT]["l"]),
               f'{ar(round(_C_WICK*100))}٪', TEAL_D)
    svg += RC._title(Wd, rt("٤ · شمعةٌ ترفض"))
    svg += why(Wd, H, f'ذيلها السفلي {ar(round(_C_WICK*100))}٪ من مداها', TEAL_D)
    svg += sm(Wd, H, "والأربع خطوات بترتيبها — واحدةٌ ناقصة تُلغي الباقي")
    return svg + badge(Wd, "مثال تخطيطي", True) + "</svg>"


def p_all(r=None, Wd=880, H=250):
    """السلسلة كاملة — والخطوات الأربع عليها بالترتيب."""
    assert len(WC) == C_N, len(WC)
    svg, x, y, slot = _gc(Wd, H)
    svg += hl(x(C_LVL_I) - slot * .5, x(C_N - 1) + slot * .5, y(C_LVL), GREY, 1.4, "5 6")
    for j, col in ((C_LVL_I, INK), (C_BK, TEAL_D), (C_BACK, GREY), (C_ENT, TEAL_D)):
        svg += mark(x(j), slot, y(WC[j]["h"]), y(WC[j]["l"]), col, 0.16)
    svg += RC._title(Wd, rt("السلسلة كاملة"))
    svg += why(Wd, H, f'{ar(C_N)} شمعة تخطيطية · أربع علاماتٍ بترتيب الخطوات', INK)
    svg += sm(Wd, H, "ولا سعرَ مكتوبٌ هنا — الترتيب هو الدرس لا الأرقام")
    return svg + badge(Wd, "مثال تخطيطي", True) + "</svg>"


SETS = {"rujoo": [g_away, g_missed, g_far, g_wait, g_all],
        "suhoob": [k_risk, k_two, k_med, k_hold, k_all],
        "tarteeb": [p_level, p_break, p_back, p_entry, p_all]}
WINS = {"rujoo": RA, "suhoob": RB, "tarteeb": RC_}
SYN = {"rujoo": (A_SEED, A_ANCH), "suhoob": (B_SEED, B_ANCH), "tarteeb": (C_SEED, C_ANCH)}


def unit_charts(slug):
    r = WINS[slug]
    ok, dropped = [], []
    for f in SETS[slug]:
        try:
            f(None, 880, 250); ok.append(f)
        except AssertionError as e:
            dropped.append((f.__name__, str(e)))
    return r, ok, dropped


if __name__ == "__main__":
    for slug in SETS:
        r, ok, dropped = unit_charts(slug)
        print(f'{slug:<8} ثبت {len(ok)}/{len(SETS[slug])}'
              + ("" if not dropped else " · سقط " + " · ".join(f"{a}: {b}" for a, b in dropped)))
