# -*- coding: utf-8 -*-
"""جارتات تشغيلة ٦٥ — خمس سلاسل تخطيطية.

مخزون النوافذ الحقيقية ما زال صفراً حرّاً على الفريمين (يومٌ ثانٍ)، فوحدات
اليوم كلُّها بقاعدة §11 البديلة بشروطها الثلاثة: شارة «مثال تخطيطي» على
كل لوحة · كلُّ ادّعاءٍ مقيسٌ على السلسلة بـ`assert` · أعدادٌ ونِسبٌ لا
أسعار.

شفافيةُ الصناديق ٠٫١٦ لا ٠٫١٣: §3-4 تحدّد المدى **١٤–١٨٪**، ودونه يُقرأ
الصندوقُ رمادياً على الكريمي — وهو ما وقع فعلاً في لوحات ٦٤ (رُصد
بالفحص البصري 2026-09-10).

    python3 run65_charts.py
"""
import statistics as st

from reel_build import INK, TEAL, TEAL_D, RED, GREY, htext, gen
from run15_charts import hl, badge, frame
import run31_charts as RC
from run58_charts import ar, rt, why, sm, band, mark
from run59_charts import spanx, vspan, xr
from run64_charts import _free_col, _lab


# ═════════ ١ · عدّ الرفض عند حدٍّ واحد (فنية · مثال تخطيطي) ═════════
A_SEED = 50697
A_ANCH = [(0, 119.2), (6, 120.9), (10, 119.9), (14, 120.7), (18, 119.8),
          (22, 120.7), (26, 119.9), (33, 122.0)]
A_N = 34

WA = gen(A_ANCH, A_N, A_SEED, wick=0.75, bn=0.5)
RA = {"sym": "SCHEMATIC-R", "slug": "مثال تخطيطي — رفض", "w": WA}
_A_R = [c["h"] - c["l"] for c in WA]
A_MED = st.median(_A_R)
A_LVL = max(c["h"] for c in WA[:8])          # الحدّ: أعلى فتيلٍ في الثمان الأولى
# «لمسة» = فتيلٌ يبلغ الحدّ ضمن ٠٫٤٠ من وسيط الشمعة، بشرط أن يبتعد السعر
# بينها وبين سابقتها — وإلا عُدّت الشمعةُ الملاصقة لمسةً ثانية وكُذّب العدّ.
A_TOL = A_MED * 0.40
_raw = [i for i in range(8, 28) if A_LVL - A_TOL <= WA[i]["h"] <= A_LVL + A_TOL]
A_TCH = []
for _i in _raw:
    if A_TCH and (_i - A_TCH[-1] < 3
                  or max(WA[j]["h"] for j in range(A_TCH[-1] + 1, _i))
                  > A_LVL - A_MED * 0.70):
        continue
    A_TCH.append(_i)
A_BK = next(i for i in range(28, 31)
            if WA[i]["c"] > A_LVL and WA[i]["c"] > WA[i]["o"])
# الامتداد يُقاس على ما **بعد** شمعة الكسر لا عليها: البذرة السابقة جعلت
# الكسر آخرَ شمعة، فصار «قطع بعده» يصف الشمعة نفسها لا ما تلاها.
A_RUN = (max(c["h"] for c in WA[A_BK + 1:]) - A_LVL) / A_MED
# عمقُ الارتداد بين كل لمستين: أدنى قاعٍ بينهما منسوباً إلى الحدّ. البذرة
# الأولى (11045) أعطت خمس لمسات لكن بارتدادٍ ضحل، فبدت السلسلة مسطّحةً
# والخطُّ يمرّ في وسط الشموع كلّها — الدرسُ يُقرأ ولا يُرى (رُصد بالفحص
# البصري 2026-09-10). فالعمق شرطٌ في البذرة لا في النصّ.
A_DEPTH = min((A_LVL - min(WA[j]["l"] for j in range(A_TCH[k] + 1, A_TCH[k + 1])))
              / A_MED for k in range(len(A_TCH) - 1))

assert 3 <= len(A_TCH) <= 5, len(A_TCH)
assert not any(WA[i]["c"] > A_LVL for i in range(8, 28)), "إغلاقٌ فوق الحدّ قبل الكسر"
assert A_BK <= 30 and A_N - A_BK >= 3, (A_BK, A_N)
assert A_RUN >= 1.5, f"المسافة بعد الكسر {A_RUN:.2f} وسيط"
assert A_DEPTH >= 1.2, f"الارتداد بين اللمسات {A_DEPTH:.2f} وسيط — السلسلة مسطّحة"
assert all(WA[i]["h"] <= A_LVL + A_TOL for i in A_TCH)


def _ga(Wd, H):
    return frame(WA, Wd, H, pad=0.10, pb=66)


def r_level(r=None, Wd=880, H=250):
    """الحدّ يُرسم من أعلى فتيلٍ سابق — لا من تقدير."""
    svg, x, y, slot = _ga(Wd, H)
    svg += hl(x(0) - slot * .5, x(A_N - 1) + slot * .5, y(A_LVL), INK, 1.8)
    _p = max(range(8), key=lambda i: WA[i]["h"])
    svg += mark(x(_p), slot, y(WA[_p]["h"]), y(WA[_p]["l"]), TEAL, 0.22)
    svg += RC._title(Wd, rt("الحدّ من فتيلٍ لا من تقدير"))
    svg += why(Wd, H, f'أعلى فتيلٍ في الشمعات {ar(8)} الأولى — نقطةٌ واحدة تُرسم عليها', INK)
    svg += sm(Wd, H, "ولو رسمته بالنظر لتحرّك معك كلّما تحرّك السعر")
    return svg + badge(Wd, "مثال تخطيطي", True) + "</svg>"


def r_touch(r=None, Wd=880, H=250):
    """اللمسات: خمسُ زياراتٍ للحدّ بلا إغلاقٍ فوقه."""
    svg, x, y, slot = _ga(Wd, H)
    svg += hl(x(0) - slot * .5, x(A_N - 1) + slot * .5, y(A_LVL), INK, 1.8)
    for i in A_TCH:
        svg += mark(x(i), slot, y(WA[i]["h"]), y(WA[i]["l"]), RED, 0.22)
    svg += RC._title(Wd, rt("عدّ الزيارات لا انطباعها"))
    svg += why(Wd, H, f'{ar(len(A_TCH))} لمسات للحدّ — ولا إغلاقَ فوقه في أيٍّ منها', RED)
    svg += sm(Wd, H, "واللمسةُ فتيلٌ يبلغ الحدّ ثم يعود، لا شمعةٌ تجلس عليه")
    return svg + badge(Wd, "مثال تخطيطي", True) + "</svg>"


def r_gap(r=None, Wd=880, H=250):
    """وبين كل لمستين ابتعادٌ — وإلا فهي لمسةٌ واحدة طويلة."""
    svg, x, y, slot = _ga(Wd, H)
    svg += hl(x(A_TCH[0]) - slot * 1.5, x(A_TCH[-1]) + slot * 1.5, y(A_LVL), INK, 1.8)
    lo = min(WA[j]["l"] for j in range(A_TCH[0], A_TCH[-1] + 1))
    svg += band(x(A_TCH[0]) - slot * .5, x(A_TCH[-1]) + slot * .5,
                y(A_LVL), y(lo), TEAL, 0.16)
    svg += spanx(x(A_TCH[0]) - slot * .5, x(A_TCH[-1]) + slot * .5, y(A_LVL),
                 f'{ar(A_TCH[-1] - A_TCH[0] + 1)} شمعة', GREY)
    svg += RC._title(Wd, rt("ما بين اللمستين"))
    svg += why(Wd, H, f'أدنى ارتدادٍ بين لمستين = {xr(A_DEPTH)} وسيطِ الشمعة — ابتعادٌ حقيقي', INK)
    svg += sm(Wd, H, "وهذا شرطُ العدّ نفسه: الملاصقةُ لا تُعدّ مرّتين")
    return svg + badge(Wd, "مثال تخطيطي", True) + "</svg>"


def r_break(r=None, Wd=880, H=250):
    """ثم إغلاقٌ فوق الحدّ، والمسافة بعده مقيسة."""
    svg, x, y, slot = _ga(Wd, H)
    svg += hl(x(0) - slot * .5, x(A_N - 1) + slot * .5, y(A_LVL), INK, 1.8)
    svg += mark(x(A_BK), slot, y(WA[A_BK]["h"]), y(WA[A_BK]["l"]), TEAL, 0.24)
    hi = max(c["h"] for c in WA[A_BK + 1:])
    j = _free_col(WA, A_LVL, hi, A_BK - 4)
    assert j is not None, "لا عمود يخلو من الشموع لوسم المسافة"
    svg += vspan(x(j), y(hi), y(A_LVL), "", TEAL_D, H=H)
    svg += _lab(x(j), y(hi) + 26, rt(f'{xr(A_RUN)} الشمعة'), TEAL_D, 17)
    svg += RC._title(Wd, rt("والإغلاق الذي يفرق"))
    svg += why(Wd, H, f'الشمعة {ar(A_BK + 1)} أغلقت فوقه، وقطع السعر بعدها {xr(A_RUN)} وسيطِ الشمعة', TEAL_D)
    svg += sm(Wd, H, "الفتيلُ زيارة، والإغلاقُ قرار — والفرقُ بينهما مسافةُ الحركة")
    return svg + badge(Wd, "مثال تخطيطي", True) + "</svg>"


def r_all(r=None, Wd=880, H=250):
    """السلسلة كاملة — مرجعُ كلِّ رقمٍ في الوحدة."""
    assert len(WA) == A_N, len(WA)
    svg, x, y, slot = _ga(Wd, H)
    svg += hl(x(0) - slot * .5, x(A_N - 1) + slot * .5, y(A_LVL), GREY, 1.4, "5 6")
    svg += RC._title(Wd, rt("السلسلة كاملة"))
    svg += why(Wd, H, f'{ar(A_N)} شمعة · {ar(len(A_TCH))} لمسات · إغلاقٌ واحد فوق الحدّ', INK)
    svg += sm(Wd, H, "ولا سعرَ مكتوبٌ هنا، فالرسم تخطيطي لا طبعةُ سوق")
    return svg + badge(Wd, "مثال تخطيطي", True) + "</svg>"


# ═════════ ٢ · الهضم بعد الاندفاع (فنية · مثال تخطيطي) ═════════
B_SEED = 2821
B_ANCH = [(0, 55.0), (9, 55.1), (11, 56.4), (20, 56.5), (26, 57.6), (31, 57.4)]
B_N, B_IMP = 32, 10

WB = gen(B_ANCH, B_N, B_SEED, wick=0.6, bn=0.55)
RB = {"sym": "SCHEMATIC-D", "slug": "مثال تخطيطي — هضم", "w": WB}
_B_R = [c["h"] - c["l"] for c in WB]
B_MED = st.median(_B_R)
B_K = _B_R[B_IMP] / B_MED
B_HI, B_LO = WB[B_IMP]["h"], WB[B_IMP]["l"]
B_DIG = list(range(B_IMP + 1, 21))
B_DMED = st.median([_B_R[i] for i in B_DIG]) / B_MED
B_BK = next(i for i in range(21, B_N)
            if WB[i]["c"] > B_HI and WB[i]["c"] > WB[i]["o"])
B_RUN = (max(c["h"] for c in WB[B_BK:]) - B_HI) / B_MED

# هي أكبرُ شمعةٍ في السلسلة فعلاً، لكن ثانيتَها ٨٨٪ منها — فالتفوّق لا
# يُرى على اللوحة. ودرسُ ٦٣ يقول: لا يُكتب ادّعاءٌ لا يراه الناظر. فبقي
# الشرطُ في البيانات وحُذف وصفُ «الأكبر» من النصّ، لأن الدرس هنا عن
# **مدى الشمعة كحدّين** لا عن تفرّدها في الحجم.
assert _B_R[B_IMP] == max(_B_R), "شمعة الاندفاع ليست الأكبر في السلسلة"
assert 2.6 <= B_K <= 6.0, f"مدى الاندفاع {B_K:.2f}"
assert WB[B_IMP]["c"] > WB[B_IMP]["o"], "شمعة الاندفاع ليست صاعدة"
assert all(B_LO <= WB[i]["l"] and WB[i]["h"] <= B_HI for i in B_DIG), \
    "شمعةُ هضمٍ خرجت من مدى الاندفاع"
assert B_DMED <= 0.85, f"وسيط الهضم {B_DMED:.2f}"
assert B_RUN >= 1.5, f"الاستكمال {B_RUN:.2f} وسيط"


def _gb(Wd, H):
    return frame(WB, Wd, H, pad=0.10, pb=66)


def d_imp(r=None, Wd=880, H=250):
    """الاندفاع: شمعةٌ أضعافُ المعتاد."""
    svg, x, y, slot = _gb(Wd, H)
    svg += mark(x(B_IMP), slot, y(B_HI), y(B_LO), TEAL, 0.24)
    j = _free_col(WB, B_LO, B_HI, B_IMP + 6)
    if j is not None:
        svg += vspan(x(j), y(B_HI), y(B_LO), "", TEAL_D, H=H)
        svg += _lab(x(j), y(B_HI) + 26, rt(f'{xr(B_K)} الشمعة'), TEAL_D, 17)
    svg += RC._title(Wd, rt("الاندفاع أوّلاً"))
    svg += why(Wd, H, f'مدى الشمعة {ar(B_IMP + 1)} = {xr(B_K)} وسيط السلسلة', TEAL_D)
    svg += sm(Wd, H, "وهذي الشمعة هي المسطرة: كلُّ ما بعدها يُقاس عليها لا على الوسيط")
    return svg + badge(Wd, "مثال تخطيطي", True) + "</svg>"


def d_range(r=None, Wd=880, H=250):
    """والهضم داخل مداها لا خارجه."""
    svg, x, y, slot = _gb(Wd, H)
    svg += band(x(B_IMP) - slot * .5, x(B_DIG[-1]) + slot * .5,
                y(B_HI), y(B_LO), TEAL, 0.16)
    svg += hl(x(B_IMP) - slot * .5, x(B_N - 1) + slot * .5, y(B_HI), INK, 1.6, "5 6")
    svg += hl(x(B_IMP) - slot * .5, x(B_N - 1) + slot * .5, y(B_LO), INK, 1.6, "5 6")
    svg += spanx(x(B_DIG[0]) - slot * .5, x(B_DIG[-1]) + slot * .5, y(B_HI),
                 f'{ar(len(B_DIG))} شمعة', INK)
    svg += RC._title(Wd, rt("عشرُ شمعاتٍ داخل شمعةٍ واحدة"))
    svg += why(Wd, H, f'{ar(len(B_DIG))} شمعة تالية لم تخرج من مدى الاندفاع — لا فوقه ولا تحته', INK)
    svg += sm(Wd, H, "والخروجُ من المدى هو الحدث، لا مرور الوقت داخله")
    return svg + badge(Wd, "مثال تخطيطي", True) + "</svg>"


def d_narrow(r=None, Wd=880, H=250):
    """وشمعاتُ الهضم أضيق من الوسيط لا أوسع."""
    svg, x, y, slot = _gb(Wd, H)
    for i in B_DIG:
        svg += mark(x(i), slot, y(WB[i]["h"]), y(WB[i]["l"]), TEAL, 0.22)
    svg += RC._title(Wd, rt("ضيقُ المدى ليس ضعفاً"))
    svg += why(Wd, H, f'وسيط شمعات الهضم {xr(B_DMED)} وسيطِ السلسلة — أضيقُ لا أوسع', TEAL_D)
    svg += sm(Wd, H, "الضيقُ يقول إن أحداً لا يدفع، والدفعُ يبدأ عند الخروج")
    return svg + badge(Wd, "مثال تخطيطي", True) + "</svg>"


def d_cont(r=None, Wd=880, H=250):
    """ثم الخروج فوق حدّ الاندفاع، والمسافة بعده مقيسة."""
    svg, x, y, slot = _gb(Wd, H)
    svg += hl(x(B_IMP) - slot * .5, x(B_N - 1) + slot * .5, y(B_HI), INK, 1.8)
    svg += mark(x(B_BK), slot, y(WB[B_BK]["h"]), y(WB[B_BK]["l"]), TEAL, 0.24)
    hi = max(c["h"] for c in WB[B_BK:])
    j = _free_col(WB, B_HI, hi, B_BK - 5)
    if j is not None:
        svg += vspan(x(j), y(hi), y(B_HI), "", TEAL_D, H=H)
        svg += _lab(x(j), y(hi) + 26, rt(f'{xr(B_RUN)} الشمعة'), TEAL_D, 17)
    svg += RC._title(Wd, rt("والاستكمال حين يخرج"))
    svg += why(Wd, H, f'الشمعة {ar(B_BK + 1)} أغلقت فوق حدّ الاندفاع، وقطعت {xr(B_RUN)} وسيطِ الشمعة', TEAL_D)
    svg += sm(Wd, H, "ولو خرج من الحدّ الأسفل لكان الجوابُ عكسَه بنفس القاعدة")
    return svg + badge(Wd, "مثال تخطيطي", True) + "</svg>"


def d_all(r=None, Wd=880, H=250):
    """السلسلة كاملة — مرجعُ كلِّ رقمٍ في الوحدة."""
    assert len(WB) == B_N, len(WB)
    svg, x, y, slot = _gb(Wd, H)
    svg += hl(x(0) - slot * .5, x(B_N - 1) + slot * .5, y(B_HI), GREY, 1.4, "5 6")
    svg += hl(x(0) - slot * .5, x(B_N - 1) + slot * .5, y(B_LO), GREY, 1.4, "5 6")
    svg += RC._title(Wd, rt("السلسلة كاملة"))
    svg += why(Wd, H, f'{ar(B_N)} شمعة · اندفاعٌ ثم {ar(len(B_DIG))} شمعة هضم ثم خروج', INK)
    svg += sm(Wd, H, "ولا سعرَ مكتوبٌ هنا، فالرسم تخطيطي لا طبعةُ سوق")
    return svg + badge(Wd, "مثال تخطيطي", True) + "</svg>"


# ═════════ ٣ · سلسلة الخسائر المتتابعة (نفسية · مثال تخطيطي) ═════════
C_SEED = 1015
C_ANCH = [(0, 30.0), (10, 30.6), (18, 30.2), (25, 29.6), (31, 30.1), (39, 30.8)]
C_N = 40

WC = gen(C_ANCH, C_N, C_SEED, wick=0.6, bn=0.5)
RC_ = {"sym": "SCHEMATIC-S", "slug": "مثال تخطيطي — سلسلة", "w": WC}
_C_DN = [c["c"] < c["o"] for c in WC]


def _runs(flags):
    """تتابعاتُ الرايات المرفوعة: (البداية، الطول) لكلٍّ منها."""
    out, s, cur = [], 0, 0
    for i, v in enumerate(flags):
        if v:
            if cur == 0:
                s = i
            cur += 1
        else:
            if cur:
                out.append((s, cur))
            cur = 0
    if cur:
        out.append((s, cur))
    return out


C_RUNS = _runs(_C_DN)
C_BIG = [r for r in C_RUNS if r[1] >= 3]
C_MAX = max(r[1] for r in C_RUNS)
C_LONG = next(r for r in C_RUNS if r[1] == C_MAX)
C_DN = sum(_C_DN)
C_NET = WC[-1]["c"] - WC[0]["o"]

assert C_MAX == 5, C_MAX
assert len(C_BIG) == 3, len(C_BIG)
assert 16 <= C_DN <= 24, C_DN
assert C_NET > 0, "النافذة انتهت خاسرة — فلا درسَ في احتمال التتابع"


def _gc(Wd, H):
    return frame(WC, Wd, H, pad=0.10, pb=66)


def s_all_dn(r=None, Wd=880, H=250):
    """الهابطات موزّعةٌ على النافذة لا مجتمعة."""
    svg, x, y, slot = _gc(Wd, H)
    for i, v in enumerate(_C_DN):
        if v:
            svg += mark(x(i), slot, y(WC[i]["h"]), y(WC[i]["l"]), RED, 0.16)
    svg += RC._title(Wd, rt("كم واحدة أصلاً"))
    svg += why(Wd, H, f'{ar(C_DN)} شمعة من {ar(C_N)} أغلقت تحت فتحها', RED)
    svg += sm(Wd, H, "الرقم وحده لا يوجع — الذي يوجع ترتيبُها")
    return svg + badge(Wd, "مثال تخطيطي", True) + "</svg>"


def s_long(r=None, Wd=880, H=250):
    """أطولُ تتابع: خمسٌ ورا بعض."""
    a, n = C_LONG
    svg, x, y, slot = _gc(Wd, H)
    lo = min(WC[j]["l"] for j in range(a, a + n))
    hi = max(WC[j]["h"] for j in range(a, a + n))
    svg += band(x(a) - slot * .5, x(a + n - 1) + slot * .5, y(hi), y(lo), TEAL, 0.16)
    svg += spanx(x(a) - slot * .5, x(a + n - 1) + slot * .5, y(hi),
                 f'{ar(n)} متتابعة', RED)
    svg += RC._title(Wd, rt("أطولُ تتابع في النافذة"))
    svg += why(Wd, H, f'{ar(n)} شمعات هابطة ورا بعض — وهذا أطولُ ما في السلسلة', RED)
    svg += sm(Wd, H, "وهو الموضع الذي يقول لك فيه رأسك إن شيئاً انكسر")
    return svg + badge(Wd, "مثال تخطيطي", True) + "</svg>"


def s_count(r=None, Wd=880, H=250):
    """والتتابعُ الطويل ليس واحداً: ثلاثةٌ في نافذةٍ واحدة."""
    svg, x, y, slot = _gc(Wd, H)
    for a, n in C_BIG:
        lo = min(WC[j]["l"] for j in range(a, a + n))
        hi = max(WC[j]["h"] for j in range(a, a + n))
        svg += band(x(a) - slot * .5, x(a + n - 1) + slot * .5, y(hi), y(lo), TEAL, 0.16)
        svg += _lab((x(a) + x(a + n - 1)) / 2, y(hi) - 10, ar(n), RED, 18)
    svg += RC._title(Wd, rt("ولا مرّةً واحدة"))
    svg += why(Wd, H, f'{ar(len(C_BIG))} تتابعاتٍ طولُها ثلاثٌ فأكثر في النافذة نفسها', INK)
    svg += sm(Wd, H, f'وأطولُها {ar(C_MAX)} — فالخمسُ ليست حدثاً نادراً، هي شكلُ التوزيع')
    return svg + badge(Wd, "مثال تخطيطي", True) + "</svg>"


def s_net(r=None, Wd=880, H=250):
    """ومع ذلك انتهت النافذة فوق نقطة البداية."""
    svg, x, y, slot = _gc(Wd, H)
    svg += hl(x(0) - slot * .5, x(C_N - 1) + slot * .5, y(WC[0]["o"]), INK, 1.8)
    a, n = C_LONG
    svg += band(x(a) - slot * .5, x(a + n - 1) + slot * .5,
                y(max(WC[j]["h"] for j in range(a, a + n))),
                y(min(WC[j]["l"] for j in range(a, a + n))), TEAL, 0.16)
    svg += mark(x(C_N - 1), slot, y(WC[-1]["h"]), y(WC[-1]["l"]), TEAL, 0.24)
    svg += RC._title(Wd, rt("وأين انتهت النافذة"))
    svg += why(Wd, H, "الإغلاق الأخير فوق فتح الشمعة الأولى — رغم التتابع كلّه", TEAL_D)
    svg += sm(Wd, H, "فالسؤالُ الصحيح ليس «كم خسرت ورا بعض» بل «هل تغيّر الشرط»")
    return svg + badge(Wd, "مثال تخطيطي", True) + "</svg>"


def s_all(r=None, Wd=880, H=250):
    """السلسلة كاملة — مرجعُ كلِّ رقمٍ في الوحدة."""
    assert len(WC) == C_N, len(WC)
    svg, x, y, slot = _gc(Wd, H)
    svg += hl(x(0) - slot * .5, x(C_N - 1) + slot * .5, y(WC[0]["o"]), GREY, 1.4, "5 6")
    svg += RC._title(Wd, rt("السلسلة كاملة"))
    svg += why(Wd, H, f'{ar(C_N)} شمعة · {ar(C_DN)} هابطة · أطولُ تتابع {ar(C_MAX)}', INK)
    svg += sm(Wd, H, "ولا سعرَ مكتوبٌ هنا، فالرسم تخطيطي لا طبعةُ سوق")
    return svg + badge(Wd, "مثال تخطيطي", True) + "</svg>"


# ═════════ ٤ · أين يبدأ اليوم على الجارت (أساسية · مثال تخطيطي) ═════════
# سلسلةُ دقائق واحدة، تُجمَّع ستّاً ستّاً في «يوم» — مرّةً من الشمعة صفر
# ومرّةً من الشمعة الثالثة. البيانات نفسُها والحدُّ وحدَه تغيّر.
D_SEED = 2115
D_ANCH = [(0, 80.0), (12, 80.5), (22, 80.1), (33, 80.9), (41, 80.4), (47, 80.8)]
D_N, D_K, D_OFF = 48, 6, 3

WD = gen(D_ANCH, D_N, D_SEED, wick=0.6, bn=0.5)
RD = {"sym": "SCHEMATIC-B", "slug": "مثال تخطيطي — بداية اليوم", "w": WD}


def _agg(W, K, off):
    out = []
    for s in range(off, len(W) - K + 1, K):
        g = W[s:s + K]
        out.append(dict(d=str(s), o=g[0]["o"], c=g[-1]["c"],
                        h=max(v["h"] for v in g), l=min(v["l"] for v in g)))
    return out


DA = _agg(WD, D_K, 0)
DB = _agg(WD, D_K, D_OFF)
D_UPA = sum(1 for c in DA if c["c"] > c["o"])
D_UPB = sum(1 for c in DB if c["c"] > c["o"])
D_FLIP = sum(1 for i in range(len(DB))
             if (DA[i]["c"] > DA[i]["o"]) != (DB[i]["c"] > DB[i]["o"]))

assert len(DA) == 8 and len(DB) == 7, (len(DA), len(DB))
assert D_FLIP >= 3, D_FLIP
assert abs(D_UPA - D_UPB) >= 2, (D_UPA, D_UPB)


def _gd(Wd, H):
    return frame(WD, Wd, H, pad=0.10, pb=66)


def _gda(Wd, H):
    return frame(DA, Wd, H, pad=0.12, pb=66)


def _gdb(Wd, H):
    return frame(DB, Wd, H, pad=0.12, pb=66)


def b_min(r=None, Wd=880, H=250):
    """الدقائق: بياناتٌ واحدة لا خلاف عليها."""
    svg, x, y, slot = _gd(Wd, H)
    for s in range(0, D_N, D_K):
        svg += hl(x(s) - slot * .5, x(s) - slot * .5, y(max(c["h"] for c in WD)),
                  GREY, 1.2, "4 5")
    svg += RC._title(Wd, rt("البيانات لا خلاف عليها"))
    svg += why(Wd, H, f'{ar(D_N)} شمعة دقائق — هذي كلُّ ما حدث، ولا أحد يجادل فيها', INK)
    svg += sm(Wd, H, "الخلافُ يبدأ عند سؤالٍ واحد: من أين نبدأ عدّ اليوم؟")
    return svg + badge(Wd, "مثال تخطيطي", True) + "</svg>"


def b_day_a(r=None, Wd=880, H=250):
    """الحدّ الأوّل: يومٌ يبدأ من الشمعة صفر."""
    svg, x, y, slot = _gda(Wd, H)
    svg += RC._title(Wd, rt("حدٌّ أوّل"))
    svg += why(Wd, H, f'كلُّ {ar(D_K)} شمعات = يومٌ واحد ⇒ {ar(len(DA))} أيام · {ar(D_UPA)} منها صاعدة', TEAL_D)
    svg += sm(Wd, H, "والناظرُ إلى هذي اللوحة يقول: اتجاهٌ صاعد بلا شكّ")
    return svg + badge(Wd, "مثال تخطيطي", True) + "</svg>"


def b_day_b(r=None, Wd=880, H=250):
    """والحدّ الثاني: نفسُ الدقائق تبدأ متأخّرةً ثلاث شمعات."""
    svg, x, y, slot = _gdb(Wd, H)
    svg += RC._title(Wd, rt("حدٌّ ثانٍ · نفس الدقائق"))
    svg += why(Wd, H, f'الحدُّ متأخّرٌ {ar(D_OFF)} شمعات ⇒ {ar(D_UPB)} صاعدة من {ar(len(DB))}', RED)
    svg += sm(Wd, H, "ولا شمعةَ دقيقةٍ واحدة تغيّرت — تغيّر موضعُ الخطّ فقط")
    return svg + badge(Wd, "مثال تخطيطي", True) + "</svg>"


def b_flip(r=None, Wd=880, H=250):
    """وعددُ الأيام التي انقلب لونُها مقيسٌ لا مقدَّر."""
    svg, x, y, slot = _gda(Wd, H)
    for i in range(len(DB)):
        if (DA[i]["c"] > DA[i]["o"]) != (DB[i]["c"] > DB[i]["o"]):
            svg += mark(x(i), slot, y(DA[i]["h"]), y(DA[i]["l"]), RED, 0.20)
    svg += RC._title(Wd, rt("كم يوماً انقلب لونُه"))
    svg += why(Wd, H, f'{ar(D_FLIP)} أيام من {ar(len(DB))} صارت بلونٍ معاكس بتغيير الحدّ وحده', RED)
    svg += sm(Wd, H, "فإذا بنيتَ قاعدةً على «إغلاق اليوم» فاكتب أوّلاً: إغلاقُ أيّ ساعة")
    return svg + badge(Wd, "مثال تخطيطي", True) + "</svg>"


def b_all(r=None, Wd=880, H=250):
    """السلسلة كاملة — مرجعُ كلِّ رقمٍ في الوحدة."""
    assert len(WD) == D_N, len(WD)
    svg, x, y, slot = _gd(Wd, H)
    svg += RC._title(Wd, rt("السلسلة كاملة"))
    svg += why(Wd, H, f'{ar(D_N)} شمعة دقائق = {ar(len(DA))} أيام بحدٍّ و{ar(len(DB))} بحدٍّ آخر', INK)
    svg += sm(Wd, H, "ولا سعرَ مكتوبٌ هنا، فالرسم تخطيطي لا طبعةُ سوق")
    return svg + badge(Wd, "مثال تخطيطي", True) + "</svg>"


# ═════════ ٥ · فاتورة الأدوات بمقياس المخاطرة (مالية · مثال تخطيطي) ═════════
E_SEED = 21269
E_ANCH = [(0, 44.0), (7, 43.6), (12, 43.9), (18, 44.6), (24, 44.2), (29, 44.9)]
E_N, E_ENT = 30, 18

WE = gen(E_ANCH, E_N, E_SEED, wick=0.65, bn=0.5)
RE = {"sym": "SCHEMATIC-F", "slug": "مثال تخطيطي — فاتورة", "w": WE}
_E_R = [c["h"] - c["l"] for c in WE]
E_MED = st.median(_E_R)
E_SW = min(range(6, 14), key=lambda i: WE[i]["l"])   # قاعُ البنية
E_RISK = WE[E_ENT]["c"] - WE[E_SW]["l"]
E_K = E_RISK / E_MED
E_SHORT = [i for i in range(E_N) if _E_R[i] < E_RISK]
E_BIG = max(range(E_N), key=lambda i: _E_R[i])
E_BK = _E_R[E_BIG] / E_MED

assert E_RISK > 0, "الدخول تحت قاع البنية — لا مسافةَ مخاطرة"
assert 1.35 <= E_K <= 1.85, f"المخاطرة {E_K:.2f} وسيط"
assert 20 <= len(E_SHORT) <= 26, len(E_SHORT)
assert E_BK >= 2.2, f"أكبر شمعة {E_BK:.2f} وسيط"


def _ge(Wd, H):
    return frame(WE, Wd, H, pad=0.10, pb=66)


def f_risk(r=None, Wd=880, H=250):
    """مسافةُ المخاطرة: من قاع البنية إلى إغلاق الدخول."""
    svg, x, y, slot = _ge(Wd, H)
    svg += band(x(E_SW) - slot * .5, x(E_ENT) + slot * .5,
                y(WE[E_ENT]["c"]), y(WE[E_SW]["l"]), TEAL, 0.16)
    svg += hl(x(E_SW) - slot * .5, x(E_N - 1) + slot * .5, y(WE[E_SW]["l"]), INK, 1.6, "5 6")
    svg += hl(x(E_SW) - slot * .5, x(E_N - 1) + slot * .5, y(WE[E_ENT]["c"]), INK, 1.6, "5 6")
    j = _free_col(WE, WE[E_SW]["l"], WE[E_ENT]["c"], E_N - 4)
    if j is not None:
        svg += _lab(x(j), y(WE[E_ENT]["c"]) + 30, rt(f'{xr(E_K)} الشمعة'), INK, 17)
    svg += RC._title(Wd, rt("وحدةُ القياس: مسافةُ المخاطرة"))
    svg += why(Wd, H, f'من قاع البنية إلى إغلاق الدخول = {xr(E_K)} وسيطِ الشمعة', INK)
    svg += sm(Wd, H, "وكلُّ فاتورةٍ تُقاس على هذي المسافة لا على حجم حسابك")
    return svg + badge(Wd, "مثال تخطيطي", True) + "</svg>"


def f_short(r=None, Wd=880, H=250):
    """وأغلبُ الشمعات أقصرُ من هذي المسافة."""
    svg, x, y, slot = _ge(Wd, H)
    for i in E_SHORT:
        svg += mark(x(i), slot, y(WE[i]["h"]), y(WE[i]["l"]), TEAL, 0.20)
    svg += RC._title(Wd, rt("أقصرُ من مخاطرتك"))
    svg += why(Wd, H, f'{ar(len(E_SHORT))} شمعة من {ar(E_N)} مداها الكامل أقلُّ من مسافة المخاطرة', TEAL_D)
    svg += sm(Wd, H, "فالمسافةُ التي تراهن عليها أكبرُ من حركة يومٍ عاديّ — احسبها كذلك")
    return svg + badge(Wd, "مثال تخطيطي", True) + "</svg>"


def f_big(r=None, Wd=880, H=250):
    """والحركةُ التي تدفع الفاتورة نادرة."""
    svg, x, y, slot = _ge(Wd, H)
    svg += mark(x(E_BIG), slot, y(WE[E_BIG]["h"]), y(WE[E_BIG]["l"]), TEAL, 0.24)
    # مدى أكبرِ شمعةٍ يغطّي اللوحة، فلا عمودَ يخلو منه — يُختار أقصرُ جارٍ
    # قبلها (أقلُّ حبرٍ يعبره القوس)، ويُكتب الوسمُ **تحت** طرفه الأدنى حيث
    # الفراغ، لا فوقه حيث فتيلُ الجار (رُصد بالفحص البصري 2026-09-10).
    # العمودُ يُختار على **النصف الأعلى** من مدى الشمعة (من إغلاقها إلى
    # قمّتها) لا على المدى كلّه: المدى الكامل يغطّي اللوحة فلا عمودَ يخلو
    # منه، أمّا النصفُ الأعلى فيتّسع لوسمٍ فوق طرف القوس. وتحت الطرف
    # الأدنى يسكن سطرُ «لماذا» — فالوسمُ هناك يقع عليه (رُصد 2026-09-10).
    _top = max(WE[E_BIG]["o"], WE[E_BIG]["c"])
    j = _free_col(WE, _top, WE[E_BIG]["h"], E_BIG - 4)
    if j is None:
        j = min(range(max(0, E_BIG - 4), E_BIG), key=lambda k: _E_R[k])
    # خيطٌ منقّطٌ يربط رأسَ القوس بفتيل الشمعة، وإلا قُرئ القياسُ على
    # الشمعة التي تحته لا على التي وُضع من أجلها.
    svg += hl(min(x(j), x(E_BIG)), max(x(j), x(E_BIG)), y(WE[E_BIG]["h"]),
              TEAL_D, 1.2, "3 5")
    svg += vspan(x(j), y(WE[E_BIG]["h"]), y(WE[E_BIG]["l"]), "", TEAL_D, H=H)
    svg += _lab(x(j), y(WE[E_BIG]["h"]) - 12, rt(f'{xr(E_BK)} الشمعة'), TEAL_D, 17)
    svg += RC._title(Wd, rt("والحركةُ التي تدفع"))
    svg += why(Wd, H, f'أكبرُ شمعةٍ في النافذة {xr(E_BK)} وسيطِ الشمعة — واحدةٌ من {ar(E_N)}', TEAL_D)
    svg += sm(Wd, H, "فالفاتورةُ شهرية والحركةُ الكبيرة ليست شهرية — وهنا يقع الحساب")
    return svg + badge(Wd, "مثال تخطيطي", True) + "</svg>"


def f_ratio(r=None, Wd=880, H=250):
    """والفاتورةُ تُترجَم إلى عددِ صفقاتٍ لا إلى مبلغ."""
    svg, x, y, slot = _ge(Wd, H)
    svg += band(x(E_SW) - slot * .5, x(E_ENT) + slot * .5,
                y(WE[E_ENT]["c"]), y(WE[E_SW]["l"]), TEAL, 0.16)
    svg += spanx(x(E_SW) - slot * .5, x(E_ENT) + slot * .5, y(WE[E_ENT]["c"]),
                 rt("وحدةٌ واحدة"), INK)
    svg += RC._title(Wd, rt("الفاتورة بعددِ الصفقات"))
    svg += why(Wd, H, "اقسم فاتورتك الشهرية على مبلغِ مخاطرتك في الصفقة الواحدة", INK)
    svg += sm(Wd, H, "يطلع لك عددٌ — وهو كم صفقةً ناجحة تشتغل لأدواتك قبل نفسك")
    return svg + badge(Wd, "مثال تخطيطي", True) + "</svg>"


def f_all(r=None, Wd=880, H=250):
    """السلسلة كاملة — مرجعُ كلِّ رقمٍ في الوحدة."""
    assert len(WE) == E_N, len(WE)
    svg, x, y, slot = _ge(Wd, H)
    svg += hl(x(0) - slot * .5, x(E_N - 1) + slot * .5, y(WE[E_SW]["l"]), GREY, 1.4, "5 6")
    svg += hl(x(0) - slot * .5, x(E_N - 1) + slot * .5, y(WE[E_ENT]["c"]), GREY, 1.4, "5 6")
    svg += RC._title(Wd, rt("السلسلة كاملة"))
    svg += why(Wd, H, f'{ar(E_N)} شمعة · المخاطرة {xr(E_K)} الوسيط · {ar(len(E_SHORT))} شمعة أقصرُ منها', INK)
    svg += sm(Wd, H, "ولا سعرَ مكتوبٌ هنا، فالرسم تخطيطي لا طبعةُ سوق")
    return svg + badge(Wd, "مثال تخطيطي", True) + "</svg>"


SETS = {"rafd": [r_level, r_touch, r_gap, r_break, r_all],
        "hadm": [d_imp, d_range, d_narrow, d_cont, d_all],
        "silsila": [s_all_dn, s_long, s_count, s_net, s_all],
        "bidaya": [b_min, b_day_a, b_day_b, b_flip, b_all],
        "fatoura": [f_risk, f_short, f_big, f_ratio, f_all]}
WINS = {"rafd": RA, "hadm": RB, "silsila": RC_, "bidaya": RD, "fatoura": RE}
REAL = {}
SYN = {"rafd": (A_SEED, A_ANCH), "hadm": (B_SEED, B_ANCH),
       "silsila": (C_SEED, C_ANCH), "bidaya": (D_SEED, D_ANCH),
       "fatoura": (E_SEED, E_ANCH)}


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
        print(f'{slug:<9} ثبت {len(ok)}/{len(SETS[slug])}'
              + ("" if not dropped else " · سقط " + " · ".join(f"{a}: {b}" for a, b in dropped)))
