# -*- coding: utf-8 -*-
"""جارتات تشغيلة ٦٧ — وحدةٌ على سوقٍ حقيقي وأربعٌ تخطيطية.

مسحُ `sheet_scan` أعاد ٣٥ نافذة، وقياسُ الفراغ بالدالّة التي تحرسه
(`run31_charts._span` ثم `assert_fresh_real`) أعطى **واحدة** حرّة:
الأسترالي/الدولار · ساعة · 2026-09-09 · فئة `consol`. وكلُّ ما عداها
مقيَّدٌ في `used_charts.json`.

وموضوع «حبس» (١٣٣) بقي مؤجَّلاً للمرّة الثالثة لأنّ هذه النافذة تسقط
ثلاثاً من عتباته: جسم الكسر 0.18× الوسيط (المطلوب ≥1.8)، والامتداد 0.77×
(المطلوب ≥1.0)، وأطول شمعة داخل المدى 2.00× (المطلوب ≤1.6). فاختير لها
الموضوع الذي **تسنده فعلاً**: «مسافة» (١٣٤) — والنافذة `consol` ودرسُها
عن البُعد عن حدّ المدى، فالنمط والموضوع متطابقان كما يشترط §11.5.

والأربع الباقية بقاعدة §11 البديلة بشروطها الثلاثة: شارة «مثال تخطيطي»
على كل لوحة · كلُّ ادّعاءٍ مقيسٌ بـ`assert` · أعدادٌ ونِسبٌ لا أسعار.

    python3 run67_charts.py
"""
import statistics as st

from reel_build import INK, TEAL, TEAL_D, RED, GREY, gen
from run15_charts import hl, badge, frame
import run31_charts as RC
from run58_charts import ar, rt, why, sm, band, mark
from run59_charts import spanx, vspan, xr


def _real(W, n):
    """تشتّتُ المدى وعددُ الهابطة — حارسُ §4 على أي سلسلة مولّدة."""
    R = [c["h"] - c["l"] for c in W]
    dn = sum(1 for c in W if c["c"] < c["o"])
    assert st.pstdev(R) / st.mean(R) >= 0.45, st.pstdev(R) / st.mean(R)
    assert dn >= n * 0.30, f"الهابطة {dn} من {n} — سلّمٌ لا سوق"


# ═════════════════════════════════════════════════════════════════
# ١ · «مسافة» — البُعد عن الحدّ (فنية · ريل · سوقٌ حقيقي)
#     الأسترالي/الدولار · ساعة · 2026-09-09 · ٤٧ شمعة
# ═════════════════════════════════════════════════════════════════
M_WIN = 67
RM = RC.win(M_WIN)
WM = RM["w"]
M_N = len(WM)
M_BK = RM["bk"]
M_PRE = WM[:M_BK]
M_HI = max(c["h"] for c in M_PRE)
M_MED = st.median(c["h"] - c["l"] for c in WM)
M_D = [(M_HI - c["c"]) / M_MED for c in WM]          # المسافة بوسيط المدى
M_FAR = [i for i in range(M_BK) if M_D[i] >= 1.8]
_runs, _cur = [], [M_FAR[0]]
for _i in M_FAR[1:]:
    if _i == _cur[-1] + 1:
        _cur.append(_i)
    else:
        _runs.append(_cur); _cur = [_i]
_runs.append(_cur)
M_RUN = max(_runs, key=len)                          # أطول تتابعٍ بعيد
M_LAST = M_RUN[-1]
M_NEXT = M_LAST + 1
M_CLOSED = (M_D[M_LAST] - M_D[M_NEXT]) / M_D[M_LAST]
M_PEAK = max(range(M_BK), key=lambda i: M_D[i])

assert len(M_PRE) >= 15, len(M_PRE)
assert len(M_RUN) >= 5, len(M_RUN)
assert M_D[M_LAST] >= 1.8, M_D[M_LAST]
assert M_D[M_NEXT] <= 0.35, M_D[M_NEXT]
assert M_CLOSED >= 0.85, M_CLOSED
assert M_NEXT < M_BK, (M_NEXT, M_BK)
assert WM[M_BK]["c"] > M_HI, "الشمعة التالية لم تُغلق فوق الحدّ"


def _gm(Wd, H):
    return frame(WM, Wd, H, pad=0.08, pb=64)


def m_level(r=None, Wd=880, H=250):
    """١ · الحدّ: أعلى قمّةٍ في الشمعات قبل الكسر."""
    svg, x, y, slot = _gm(Wd, H)
    svg += hl(x(0) - slot * .5, x(M_N - 1) + slot * .5, y(M_HI), INK, 1.8)
    _p = max(range(M_BK), key=lambda i: WM[i]["h"])
    svg += mark(x(_p), slot, y(WM[_p]["h"]), y(WM[_p]["l"]), TEAL, 0.22)
    svg += RC._title(Wd, rt("الحدّ رقمٌ واحدٌ تعرفه قبل كل شي"))
    svg += RC._why(Wd, H, f'أعلى قمّةٍ في {ar(M_BK)} شمعة — والمسافةُ كلها تُقاس منه', INK)
    svg += sm(Wd, H, "ووسيطُ مدى الشمعة هو المسطرة: كل رقمٍ جاي بوحداته")
    return svg + "</svg>"


def m_far(r=None, Wd=880, H=250):
    """٢ · بعيدٌ فعلاً: أقصى مسافةٍ في النافذة."""
    svg, x, y, slot = _gm(Wd, H)
    svg += hl(x(0) - slot * .5, x(M_N - 1) + slot * .5, y(M_HI), INK, 1.8)
    svg += mark(x(M_PEAK), slot, y(WM[M_PEAK]["h"]), y(WM[M_PEAK]["l"]), TEAL, 0.22)
    svg += vspan(x(M_PEAK) + slot * 1.9, y(WM[M_PEAK]["c"]), y(M_HI),
                 rt(f'{xr(M_D[M_PEAK])}× الوسيط'), TEAL_D, 16, H)
    svg += RC._title(Wd, rt("وأبعدُ نقطةٍ كانت قريبة"))
    svg += RC._why(Wd, H, f'أقصى بُعدٍ في النافذة {xr(M_D[M_PEAK])}× وسيط مدى الشمعة '
                          f'— شمعتان ونصف لا أكثر', TEAL_D)
    svg += sm(Wd, H, "وهذا هو الرقم الذي يغرّك بأن تروح تنام")
    return svg + "</svg>"


def m_six(r=None, Wd=880, H=250):
    """٣ · ستُّ شمعاتٍ متتالية والمسافة ≥1.8×."""
    svg, x, y, slot = _gm(Wd, H)
    svg += hl(x(0) - slot * .5, x(M_N - 1) + slot * .5, y(M_HI), INK, 1.8)
    svg += band(x(M_RUN[0]) - slot * .5, x(M_LAST) + slot * .5,
                y(max(c["h"] for c in WM[M_RUN[0]:M_LAST + 1])),
                y(min(c["l"] for c in WM[M_RUN[0]:M_LAST + 1])), TEAL_D, 0.16)
    svg += spanx(x(M_RUN[0]) - slot * .5, x(M_LAST) + slot * .5,
                 y(max(c["h"] for c in WM[M_RUN[0]:M_LAST + 1])),
                 rt(f'{ar(len(M_RUN))} شمعة'), INK)
    svg += RC._title(Wd, rt("والبُعد ثبت ستّ شمعات"))
    svg += RC._why(Wd, H, f'{ar(len(M_RUN))} شمعة متتالية والمسافة ما نزلت تحت '
                          f'{xr(1.8)}× — ولا وحدة منهن قرّبت السعر', INK)
    svg += sm(Wd, H, "ستُّ ساعاتٍ تقول لك: ما في شي، روح")
    return svg + "</svg>"


def m_one(r=None, Wd=880, H=250):
    """٤ · شمعةٌ واحدة أغلقت تسعين بالمئة من المسافة."""
    svg, x, y, slot = _gm(Wd, H)
    svg += hl(x(0) - slot * .5, x(M_N - 1) + slot * .5, y(M_HI), INK, 1.8)
    svg += mark(x(M_NEXT), slot, y(WM[M_NEXT]["h"]), y(WM[M_NEXT]["l"]), RED, 0.24)
    svg += band(x(M_NEXT) - slot * .5, x(M_NEXT) + slot * .5,
                y(WM[M_NEXT]["c"]), y(WM[M_LAST]["c"]), RED, 0.16)
    svg += vspan(x(M_NEXT) + slot * 2.0, y(WM[M_NEXT]["c"]), y(WM[M_LAST]["c"]),
                 rt(f'{ar(round(M_CLOSED * 100))}٪ بشمعة'), RED, 16, H)
    svg += RC._title(Wd, rt("وشمعةٌ وحدة شالت البُعد كله"))
    svg += RC._why(Wd, H, f'من {xr(M_D[M_LAST])}× إلى {xr(M_D[M_NEXT])}× '
                          f'— {ar(round(M_CLOSED * 100))}٪ من المسافة بشمعةٍ واحدة', RED)
    svg += sm(Wd, H, "ولو كنت نايمًا، صحيت والسعر على الحدّ")
    return svg + "</svg>"


def m_all(r=None, Wd=880, H=250):
    """٥ · القصّة كاملة: بعيد ← بعيد ← قريب ← فوق."""
    svg, x, y, slot = _gm(Wd, H)
    svg += hl(x(0) - slot * .5, x(M_N - 1) + slot * .5, y(M_HI), INK, 1.8)
    svg += band(x(M_RUN[0]) - slot * .5, x(M_LAST) + slot * .5,
                y(max(c["h"] for c in WM[M_RUN[0]:M_LAST + 1])),
                y(min(c["l"] for c in WM[M_RUN[0]:M_LAST + 1])), TEAL_D, 0.14)
    svg += mark(x(M_NEXT), slot, y(WM[M_NEXT]["h"]), y(WM[M_NEXT]["l"]), RED, 0.22)
    svg += mark(x(M_BK), slot, y(WM[M_BK]["h"]), y(WM[M_BK]["l"]), TEAL, 0.22)
    svg += RC._title(Wd, rt("المسافة هي المنبّه، مو الكسر"))
    svg += RC._why(Wd, H, f'{ar(len(M_RUN))} شمعة بعيدة ← شمعةٌ قرّبت '
                          f'{ar(round(M_CLOSED * 100))}٪ ← الشمعة التالية فوق الحدّ', INK)
    svg += sm(Wd, H, "والمنبّه انضرب قبل الكسر بشمعة — لو كنت تقيس")
    return svg + "</svg>"


# ═════════════════════════════════════════════════════════════════
# ٢ · «فتائل» — الذيول تحت (فنية · ريل · مثال تخطيطي)
# ═════════════════════════════════════════════════════════════════
F_SEED = 16437
F_ANCH = [(0, 100.0), (8, 99.2), (16, 99.0), (23, 99.6), (28, 100.8), (33, 102.2)]
F_N = 34
WF = gen(F_ANCH, F_N, F_SEED, wick=0.95, bn=0.5)
RF = {"sym": "SCHEMATIC-F", "slug": "مثال تخطيطي — فتائل", "w": WF}
F_LW = [min(c["o"], c["c"]) - c["l"] for c in WF]
F_UW = [c["h"] - max(c["o"], c["c"]) for c in WF]
F_R = [c["h"] - c["l"] for c in WF]
F_MED = st.median(F_R)
F_IDX = [i for i in range(F_N) if F_LW[i] > F_UW[i]]
F_CNT = len(F_IDX)
F_RATIO = st.median(F_LW) / st.median(F_UW)
F_LOW = min(range(F_N), key=lambda i: WF[i]["l"])
F_RUN = (max(c["h"] for c in WF[26:]) - min(c["l"] for c in WF[:26])) / F_MED
F_DEEP = max(range(F_N), key=lambda i: F_LW[i])

_real(WF, F_N)
assert F_CNT == 21, F_CNT
assert F_RATIO >= 1.7, F_RATIO
assert F_RUN >= 3.0, F_RUN
assert F_LOW < 26, F_LOW


def _gf(Wd, H):
    return frame(WF, Wd, H, pad=0.10, pb=66)


def f_count(r=None, Wd=880, H=250):
    """١ · العدّ: كم شمعةً ذيلُها السفلي أطول."""
    svg, x, y, slot = _gf(Wd, H)
    for i in F_IDX:
        svg += mark(x(i), slot, y(min(WF[i]["o"], WF[i]["c"])), y(WF[i]["l"]), TEAL, 0.20)
    svg += RC._title(Wd, rt("عدّهن قبل لا تفسّرهن"))
    svg += RC._why(Wd, H, f'{ar(F_CNT)} من {ar(F_N)} شمعة ذيلُها السفلي أطول من العلوي', TEAL_D)
    svg += sm(Wd, H, "الملوّن هو الذيل السفلي وحده — لا الشمعة كلها")
    return svg + badge(Wd, "مثال تخطيطي", True) + "</svg>"


def f_ratio(r=None, Wd=880, H=250):
    """٢ · النسبة: وسيط السفلي مقابل وسيط العلوي."""
    svg, x, y, slot = _gf(Wd, H)
    svg += mark(x(F_DEEP), slot, y(min(WF[F_DEEP]["o"], WF[F_DEEP]["c"])),
                y(WF[F_DEEP]["l"]), TEAL, 0.24)
    svg += vspan(x(F_DEEP) + slot * 1.9, y(min(WF[F_DEEP]["o"], WF[F_DEEP]["c"])),
                 y(WF[F_DEEP]["l"]), rt("أطولُ ذيل"), TEAL_D, 16, H)
    svg += RC._title(Wd, rt("وقيسهن، لا تقارنهن بالنظر"))
    svg += RC._why(Wd, H, f'وسيطُ الذيل السفلي {xr(F_RATIO)}× وسيطَ العلوي '
                          f'— مو إحساس، رقم', TEAL_D)
    svg += sm(Wd, H, "والوسيط يحمي العدّ من شمعةٍ شاذّةٍ وحدة")
    return svg + badge(Wd, "مثال تخطيطي", True) + "</svg>"


def f_low(r=None, Wd=880, H=250):
    """٣ · القاع: أين وقع داخل السلسلة."""
    svg, x, y, slot = _gf(Wd, H)
    svg += hl(x(0) - slot * .5, x(F_N - 1) + slot * .5, y(WF[F_LOW]["l"]), INK, 1.6, "5 6")
    svg += mark(x(F_LOW), slot, y(WF[F_LOW]["h"]), y(WF[F_LOW]["l"]), RED, 0.22)
    svg += RC._title(Wd, rt("والقاع طلع قبل الحركة"))
    svg += RC._why(Wd, H, f'أدنى قاع عند الشمعة {ar(F_LOW + 1)} من {ar(F_N)} '
                          f'— قبل الامتداد بوقت طويل', INK)
    svg += sm(Wd, H, "الذيول ما تنبّئ، بس تقول وين تعب البائع")
    return svg + badge(Wd, "مثال تخطيطي", True) + "</svg>"


def f_run(r=None, Wd=880, H=250):
    """٤ · ما بعدها: الامتداد بوحدات الوسيط."""
    svg, x, y, slot = _gf(Wd, H)
    svg += band(x(26) - slot * .5, x(F_N - 1) + slot * .5,
                y(max(c["h"] for c in WF[26:])), y(WF[F_LOW]["l"]), TEAL_D, 0.14)
    svg += spanx(x(26) - slot * .5, x(F_N - 1) + slot * .5,
                 y(max(c["h"] for c in WF[26:])), rt(f'{xr(F_RUN)}× الوسيط'), INK)
    svg += RC._title(Wd, rt("والامتداد بعدهن مقيس"))
    svg += RC._why(Wd, H, f'من القاع إلى أعلى نقطة {xr(F_RUN)}× وسيط مدى الشمعة', TEAL_D)
    svg += sm(Wd, H, "رقمٌ تقدر تقارنه بأي نافذةٍ ثانية")
    return svg + badge(Wd, "مثال تخطيطي", True) + "</svg>"


def f_all(r=None, Wd=880, H=250):
    """٥ · الصورة كاملة."""
    svg, x, y, slot = _gf(Wd, H)
    for i in F_IDX:
        svg += mark(x(i), slot, y(min(WF[i]["o"], WF[i]["c"])), y(WF[i]["l"]), TEAL, 0.16)
    svg += hl(x(0) - slot * .5, x(F_N - 1) + slot * .5, y(WF[F_LOW]["l"]), INK, 1.6, "5 6")
    svg += RC._title(Wd, rt("ثلاثة أرقام تكفي"))
    svg += RC._why(Wd, H, f'{ar(F_CNT)} من {ar(F_N)} · وسيطُهن {xr(F_RATIO)}× · '
                          f'والامتداد {xr(F_RUN)}×', INK)
    svg += sm(Wd, H, "واللي ما تقدر تعدّه، لا تبني عليه قرار")
    return svg + badge(Wd, "مثال تخطيطي", True) + "</svg>"


# ═════════════════════════════════════════════════════════════════
# ٣ · «تقليد» — الدخول بلا سبب يخصّك (نفسية · كاروسيل · مثال تخطيطي)
# ═════════════════════════════════════════════════════════════════
Q_SEED = 30060
Q_ANCH = [(0, 100.0), (7, 99.4), (12, 99.6), (16, 101.8),
          (20, 101.0), (26, 102.6), (31, 103.4)]
Q_N = 32
WQ = gen(Q_ANCH, Q_N, Q_SEED, wick=0.85, bn=0.5)
RQ = {"sym": "SCHEMATIC-Q", "slug": "مثال تخطيطي — تقليد", "w": WQ}
Q_R = [c["h"] - c["l"] for c in WQ]
Q_MED = st.median(Q_R)
Q_IMP = max(range(12, 18), key=lambda i: WQ[i]["c"] - WQ[i]["o"])
Q_LVL = max(c["h"] for c in WQ[:Q_IMP])
Q_BACK = next(i for i in range(Q_IMP + 1, Q_N) if WQ[i]["l"] <= Q_LVL < WQ[i]["c"])
Q_BODY = (WQ[Q_IMP]["c"] - WQ[Q_IMP]["o"]) / Q_MED
Q_MAE_C = (WQ[Q_IMP]["c"] - min(c["l"] for c in WQ[Q_IMP + 1:Q_BACK + 1])) / Q_MED
Q_MAE_R = (WQ[Q_BACK]["c"] - min(c["l"] for c in WQ[Q_BACK + 1:])) / Q_MED
Q_PEAK = (max(c["h"] for c in WQ[Q_BACK:]) - WQ[Q_BACK]["c"]) / Q_MED
Q_GAP = Q_MAE_C / Q_MAE_R

_real(WQ, Q_N)
assert Q_BODY >= 2.0, Q_BODY
assert WQ[Q_IMP]["c"] > Q_LVL, "الاندفاعة لم تُغلق فوق الحدّ"
assert Q_BACK - Q_IMP <= 4, (Q_IMP, Q_BACK)
assert Q_MAE_C >= 2.0, Q_MAE_C
assert Q_MAE_R <= 0.9, Q_MAE_R
assert Q_GAP >= 3.0, Q_GAP


def _gq(Wd, H):
    return frame(WQ, Wd, H, pad=0.10, pb=66)


def q_imp(r=None, Wd=880, H=250):
    """١ · الاندفاعة التي يراها الكل."""
    svg, x, y, slot = _gq(Wd, H)
    svg += hl(x(0) - slot * .5, x(Q_N - 1) + slot * .5, y(Q_LVL), INK, 1.8)
    svg += mark(x(Q_IMP), slot, y(WQ[Q_IMP]["h"]), y(WQ[Q_IMP]["l"]), TEAL, 0.24)
    svg += RC._title(Wd, rt("الشمعة اللي يشوفها الكل"))
    svg += RC._why(Wd, H, f'جسمُها {xr(Q_BODY)}× وسيط مدى الشمعة وأغلقت فوق الحدّ', TEAL_D)
    svg += sm(Wd, H, "وهني تجيك الرسالة: «دخلوا، دخلت؟»")
    return svg + badge(Wd, "مثال تخطيطي", True) + "</svg>"


def q_copy(r=None, Wd=880, H=250):
    """٢ · دخولُ التقليد: عند إغلاقها."""
    svg, x, y, slot = _gq(Wd, H)
    svg += hl(x(0) - slot * .5, x(Q_N - 1) + slot * .5, y(Q_LVL), INK, 1.6, "5 6")
    svg += hl(x(Q_IMP) - slot * .5, x(Q_N - 1) + slot * .5, y(WQ[Q_IMP]["c"]), RED, 1.8)
    _lo = min(c["l"] for c in WQ[Q_IMP + 1:Q_BACK + 1])
    svg += band(x(Q_IMP) + slot * .5, x(Q_BACK) + slot * .5,
                y(WQ[Q_IMP]["c"]), y(_lo), RED, 0.16)
    svg += vspan(x(Q_BACK) + slot * 1.9, y(WQ[Q_IMP]["c"]), y(_lo),
                 rt(f'{xr(Q_MAE_C)}× ضدّك'), RED, 16, H)
    svg += RC._title(Wd, rt("ودخلتَ عند إغلاقها"))
    svg += RC._why(Wd, H, f'رجع السعر ضدّك {xr(Q_MAE_C)}× الوسيط قبل ما يتحرك', RED)
    svg += sm(Wd, H, "نفس الصفقة، بس دخلتها بأغلى نقطة فيها")
    return svg + badge(Wd, "مثال تخطيطي", True) + "</svg>"


def q_cond(r=None, Wd=880, H=250):
    """٣ · دخولُ الشرط: عند العودة فوق الحدّ."""
    svg, x, y, slot = _gq(Wd, H)
    svg += hl(x(0) - slot * .5, x(Q_N - 1) + slot * .5, y(Q_LVL), INK, 1.8)
    svg += mark(x(Q_BACK), slot, y(WQ[Q_BACK]["h"]), y(WQ[Q_BACK]["l"]), TEAL, 0.24)
    _lo = min(c["l"] for c in WQ[Q_BACK + 1:])
    svg += band(x(Q_BACK) + slot * .5, x(Q_N - 1) + slot * .5,
                y(WQ[Q_BACK]["c"]), y(_lo), TEAL_D, 0.16)
    svg += vspan(x(Q_BACK) + slot * 2.0, y(WQ[Q_BACK]["c"]), y(_lo),
                 rt(f'{xr(Q_MAE_R)}× ضدّك'), TEAL_D, 16, H)
    svg += RC._title(Wd, rt("والشرط دخّلك بعدها بشمعتين"))
    svg += RC._why(Wd, H, f'أول إغلاقٍ يرجع فوق الحدّ — والارتداد ضدّك '
                          f'{xr(Q_MAE_R)}× الوسيط بس', TEAL_D)
    svg += sm(Wd, H, "شرطٌ مكتوبٌ قبل، مو قرارٌ وقت الحماس")
    return svg + badge(Wd, "مثال تخطيطي", True) + "</svg>"


def q_gap(r=None, Wd=880, H=250):
    """٤ · الفرق بين الألمين."""
    svg, x, y, slot = _gq(Wd, H)
    svg += hl(x(0) - slot * .5, x(Q_N - 1) + slot * .5, y(Q_LVL), INK, 1.6, "5 6")
    svg += mark(x(Q_IMP), slot, y(WQ[Q_IMP]["h"]), y(WQ[Q_IMP]["l"]), RED, 0.18)
    svg += mark(x(Q_BACK), slot, y(WQ[Q_BACK]["h"]), y(WQ[Q_BACK]["l"]), TEAL, 0.22)
    svg += RC._title(Wd, rt("نفس النتيجة… وألمان مختلفان"))
    svg += RC._why(Wd, H, f'{xr(Q_MAE_C)}× مقابل {xr(Q_MAE_R)}× — '
                          f'أي {xr(Q_GAP)}× فرقٍ بالألم على نفس الاتجاه', INK)
    svg += sm(Wd, H, "والاتجاه كان صح بالحالتين — المكان هو اللي اختلف")
    return svg + badge(Wd, "مثال تخطيطي", True) + "</svg>"


def q_all(r=None, Wd=880, H=250):
    """٥ · الصورة كاملة."""
    svg, x, y, slot = _gq(Wd, H)
    svg += hl(x(0) - slot * .5, x(Q_N - 1) + slot * .5, y(Q_LVL), INK, 1.8)
    svg += mark(x(Q_IMP), slot, y(WQ[Q_IMP]["h"]), y(WQ[Q_IMP]["l"]), RED, 0.16)
    svg += mark(x(Q_BACK), slot, y(WQ[Q_BACK]["h"]), y(WQ[Q_BACK]["l"]), TEAL, 0.20)
    svg += band(x(Q_BACK) + slot * .5, x(Q_N - 1) + slot * .5,
                y(max(c["h"] for c in WQ[Q_BACK:])), y(WQ[Q_BACK]["c"]), TEAL_D, 0.12)
    svg += RC._title(Wd, rt("السبب اللي يخصّك اهو المكان"))
    svg += RC._why(Wd, H, f'الاندفاعة ← ارتدادٌ {xr(Q_MAE_C)}× · '
                          f'العودة فوق الحدّ ← ارتدادٌ {xr(Q_MAE_R)}× · '
                          f'والامتداد بعدها {xr(Q_PEAK)}×', INK)
    svg += sm(Wd, H, "ولو ما عندك شرطٌ مكتوب، انت داخلٌ بسبب غيرك")
    return svg + badge(Wd, "مثال تخطيطي", True) + "</svg>"


# ═════════════════════════════════════════════════════════════════
# ٤ · «تدوير» — فجوةُ تدوير العقد (أساسية · كاروسيل · مثال تخطيطي)
#     الإزاحة مُعلَنة: العقد الجديد يبدأ أعلى بمقدارٍ لم يتداوله أحد.
# ═════════════════════════════════════════════════════════════════
W_SEED = 4
W_ANCH = [(0, 100.0), (7, 99.4), (13, 100.2), (18, 99.8),
          (24, 100.6), (30, 100.2), (35, 100.9)]
W_N = 36
W_K = 18                                           # أول شمعةٍ في العقد الجديد
_W0 = gen(W_ANCH, W_N, W_SEED, wick=0.85, bn=0.5)
W_R0 = [c["h"] - c["l"] for c in _W0]
W_MED = st.median(W_R0)
W_OFF = W_MED * 2.2                                # إزاحةُ التدوير المُعلَنة
WW = [dict(c) for c in _W0]
for _c in WW[W_K:]:
    for _k in ("o", "h", "l", "c"):
        _c[_k] = round(_c[_k] + W_OFF, 6)
RW = {"sym": "SCHEMATIC-W", "slug": "مثال تخطيطي — تدوير", "w": WW}
W_GAP = WW[W_K]["o"] - WW[W_K - 1]["c"]
W_SEP = WW[W_K]["l"] - WW[W_K - 1]["h"]
W_SHORT = sum(1 for r in W_R0 if r < W_GAP)
W_BEF = W_R0[W_K - 1] / W_MED
W_AFT = W_R0[W_K] / W_MED

_real(_W0, W_N)
assert W_SEP > 0, "الشمعتان تتلامسان — لا فجوة"
assert W_SEP / W_MED >= 0.5, W_SEP / W_MED
assert 2.0 <= W_GAP / W_MED <= 2.6, W_GAP / W_MED
assert W_SHORT >= W_N * 0.85, W_SHORT


def _gw(Wd, H):
    return frame(WW, Wd, H, pad=0.08, pb=66)


def w_gap(r=None, Wd=880, H=250):
    """١ · الفجوة نفسها."""
    svg, x, y, slot = _gw(Wd, H)
    svg += band(x(W_K - 1) - slot * .5, x(W_K) + slot * .5,
                y(WW[W_K]["o"]), y(WW[W_K - 1]["c"]), RED, 0.18)
    svg += vspan(x(W_K) + slot * 2.0, y(WW[W_K]["o"]), y(WW[W_K - 1]["c"]),
                 rt(f'{xr(W_GAP / W_MED)}× الوسيط'), RED, 16, H)
    svg += RC._title(Wd, rt("الجارت قفز… والسوق ما قفز"))
    svg += RC._why(Wd, H, f'الفجوة {xr(W_GAP / W_MED)}× وسيط مدى الشمعة '
                          f'بين إغلاقٍ وفتحٍ متجاورين', RED)
    svg += sm(Wd, H, "إزاحة عقد جديد، مو حركة سعر")
    return svg + badge(Wd, "مثال تخطيطي", True) + "</svg>"


def w_none(r=None, Wd=880, H=250):
    """٢ · ولا تداولَ داخلها."""
    svg, x, y, slot = _gw(Wd, H)
    svg += band(x(W_K - 1) - slot * .5, x(W_K) + slot * .5,
                y(WW[W_K]["l"]), y(WW[W_K - 1]["h"]), RED, 0.20)
    svg += mark(x(W_K - 1), slot, y(WW[W_K - 1]["h"]), y(WW[W_K - 1]["l"]), INK, 0.18)
    svg += mark(x(W_K), slot, y(WW[W_K]["h"]), y(WW[W_K]["l"]), INK, 0.18)
    svg += RC._title(Wd, rt("وما مرّ فيها ولا سعر"))
    svg += RC._why(Wd, H, f'فتيلا الشمعتين ما تلامسا — فراغٌ تامٌّ '
                          f'{xr(W_SEP / W_MED)}× الوسيط', RED)
    svg += sm(Wd, H, "لا أحد اشترى ولا باع بهالمسافة")
    return svg + badge(Wd, "مثال تخطيطي", True) + "</svg>"


def w_size(r=None, Wd=880, H=250):
    """٣ · حجمها مقارنةً بالشمعات."""
    svg, x, y, slot = _gw(Wd, H)
    svg += mark(x(W_K - 1), slot, y(WW[W_K - 1]["h"]), y(WW[W_K - 1]["l"]), TEAL, 0.22)
    svg += mark(x(W_K), slot, y(WW[W_K]["h"]), y(WW[W_K]["l"]), TEAL, 0.22)
    svg += RC._title(Wd, rt("وأكبر من كل شمعةٍ حواليها"))
    svg += RC._why(Wd, H, f'{ar(W_SHORT)} من {ar(W_N)} شمعة مداها أقصر من الفجوة '
                          f'— وجارتاها {xr(W_BEF)}× و{xr(W_AFT)}×', TEAL_D)
    svg += sm(Wd, H, "فلو حسبتها حركةً، صارت أكبر حركةٍ بالنافذة وهي وهم")
    return svg + badge(Wd, "مثال تخطيطي", True) + "</svg>"


def w_fix(r=None, Wd=880, H=250):
    """٤ · ما يبقى صحيحاً رغمها."""
    svg, x, y, slot = _gw(Wd, H)
    svg += hl(x(W_K) - slot * .5, x(W_N - 1) + slot * .5,
              y(max(c["h"] for c in WW[W_K:])), INK, 1.6, "5 6")
    svg += band(x(W_K) - slot * .5, x(W_N - 1) + slot * .5,
                y(max(c["h"] for c in WW[W_K:])),
                y(min(c["l"] for c in WW[W_K:])), TEAL_D, 0.12)
    svg += RC._title(Wd, rt("واشتغل داخل العقد الواحد"))
    svg += RC._why(Wd, H, f'{ar(W_N - W_K)} شمعة بعد التدوير — مستوياتُها '
                          f'كلها من عقدها هي', INK)
    svg += sm(Wd, H, "المستوى المرسوم قبل التدوير يخصّ عقدًا انتهى")
    return svg + badge(Wd, "مثال تخطيطي", True) + "</svg>"


def w_all(r=None, Wd=880, H=250):
    """٥ · الصورة كاملة."""
    svg, x, y, slot = _gw(Wd, H)
    svg += band(x(W_K - 1) - slot * .5, x(W_K) + slot * .5,
                y(WW[W_K]["l"]), y(WW[W_K - 1]["h"]), RED, 0.16)
    svg += hl(x(W_K) - slot * .5, x(W_N - 1) + slot * .5,
              y(max(c["h"] for c in WW[W_K:])), INK, 1.5, "5 6")
    svg += RC._title(Wd, rt("اقرأ القفزة قبل لا تفسّرها"))
    svg += RC._why(Wd, H, f'فجوة {xr(W_GAP / W_MED)}× · فراغٌ تام '
                          f'{xr(W_SEP / W_MED)}× · {ar(W_SHORT)} من {ar(W_N)} '
                          f'شمعة أقصر منها', INK)
    svg += sm(Wd, H, "وسؤالك الأول: هل هذا يومُ تدوير؟")
    return svg + badge(Wd, "مثال تخطيطي", True) + "</svg>"


# ═════════════════════════════════════════════════════════════════
# ٥ · «أدنى» — أصغر عقدٍ أكبر من مخاطرتك (مالية · كاروسيل · مثال تخطيطي)
# ═════════════════════════════════════════════════════════════════
A_SEED = 771
A_ANCH = [(0, 100.0), (6, 99.3), (11, 99.6), (15, 99.0),
          (19, 99.9), (25, 100.9), (30, 101.4)]
A_N = 31
A_MULT = 3.4                     # افتراضٌ مُعلَن: أصغر عقدٍ = ٣٫٤× الحدّ المسموح
WA = gen(A_ANCH, A_N, A_SEED, wick=0.85, bn=0.5)
RA = {"sym": "SCHEMATIC-A", "slug": "مثال تخطيطي — أدنى", "w": WA}
A_R = [c["h"] - c["l"] for c in WA]
A_MED = st.median(A_R)
A_SW = min(range(12, 20), key=lambda i: WA[i]["l"])
A_ENT = next(i for i in range(A_SW + 1, A_N)
             if i > A_SW + 1 and WA[i]["c"] > max(c["h"] for c in WA[A_SW:i]))
A_DIST = (WA[A_ENT]["c"] - WA[A_SW]["l"]) / A_MED
A_NEED = A_DIST / A_MULT                            # المسافة التي يفرضها الحدّ
A_HIT = sum(1 for r in A_R if r > A_NEED * A_MED)   # شمعاتٌ تبتلع تلك المسافة
A_RUN = (max(c["h"] for c in WA[A_ENT:]) - WA[A_ENT]["c"]) / A_MED

_real(WA, A_N)
_A_SPAN = (max(c["h"] for c in WA) - min(c["l"] for c in WA)) / A_MED
assert _A_SPAN <= 5.7, _A_SPAN          # لوحةٌ أوسع تُرقّق الشمعات (§4)
assert 2.4 <= A_DIST <= 2.8, A_DIST
assert A_NEED < 1.0, A_NEED
assert A_HIT >= A_N * 0.55, A_HIT
assert A_RUN >= 2.0, A_RUN


def _ga(Wd, H):
    return frame(WA, Wd, H, pad=0.10, pb=66)


def a_setup(r=None, Wd=880, H=250):
    """١ · الصفقة كما تُقرأ."""
    svg, x, y, slot = _ga(Wd, H)
    svg += hl(x(0) - slot * .5, x(A_N - 1) + slot * .5, y(WA[A_SW]["l"]), INK, 1.8)
    svg += mark(x(A_SW), slot, y(WA[A_SW]["h"]), y(WA[A_SW]["l"]), TEAL, 0.22)
    svg += mark(x(A_ENT), slot, y(WA[A_ENT]["h"]), y(WA[A_ENT]["l"]), TEAL_D, 0.22)
    svg += RC._title(Wd, rt("الصفقة سليمة… والمشكلة مو فيها"))
    svg += RC._why(Wd, H, f'القاع عند الشمعة {ar(A_SW + 1)} والدخول عند '
                          f'{ar(A_ENT + 1)} — شرطٌ مقروء', TEAL_D)
    svg += sm(Wd, H, "وامتدّت بعدها " + rt(f'{xr(A_RUN)}×') + " وسيطَ مدى الشمعة")
    return svg + badge(Wd, "مثال تخطيطي", True) + "</svg>"


def a_stop(r=None, Wd=880, H=250):
    """٢ · مسافةُ الوقف التي يفرضها الهيكل."""
    svg, x, y, slot = _ga(Wd, H)
    svg += band(x(A_SW) - slot * .5, x(A_N - 1) + slot * .5,
                y(WA[A_ENT]["c"]), y(WA[A_SW]["l"]), RED, 0.14)
    svg += vspan(x(A_ENT) + slot * 2.0, y(WA[A_ENT]["c"]), y(WA[A_SW]["l"]),
                 rt(f'{xr(A_DIST)}× الوسيط'), RED, 16, H)
    svg += RC._title(Wd, rt("ووقفك يقرّره الهيكل لا مزاجك"))
    svg += RC._why(Wd, H, f'من الدخول إلى تحت القاع {xr(A_DIST)}× وسيط مدى الشمعة', RED)
    svg += sm(Wd, H, "وهذي المسافة مو قابلة للتفاوض — هي اللي تبطّل الفكرة")
    return svg + badge(Wd, "مثال تخطيطي", True) + "</svg>"


def a_squeeze(r=None, Wd=880, H=250):
    """٣ · المسافة التي يفرضها أصغر عقد."""
    svg, x, y, slot = _ga(Wd, H)
    _need = WA[A_ENT]["c"] - A_NEED * A_MED
    svg += hl(x(0) - slot * .5, x(A_N - 1) + slot * .5, y(WA[A_ENT]["c"]), INK, 1.6)
    svg += band(x(A_SW) - slot * .5, x(A_N - 1) + slot * .5,
                y(WA[A_ENT]["c"]), y(_need), RED, 0.26)
    svg += vspan(x(A_SW) - slot * 2.2, y(WA[A_ENT]["c"]), y(_need),
                 rt(f'{xr(A_NEED)}× بس'), RED, 16, H)
    svg += RC._title(Wd, rt("وأصغر عقدٍ يعطيك هالشبر"))
    svg += RC._why(Wd, H, f'لو خاطرت بالحدّ المسموح وأصغر عقد، وقفك '
                          f'{xr(A_NEED)}× الوسيط لا أكثر', RED)
    svg += sm(Wd, H, "أي أقصر من شمعةٍ عادية وحدة")
    return svg + badge(Wd, "مثال تخطيطي", True) + "</svg>"


def a_noise(r=None, Wd=880, H=250):
    """٤ · كم شمعةً تبتلع تلك المسافة."""
    svg, x, y, slot = _ga(Wd, H)
    _big = [i for i in range(A_N) if A_R[i] > A_NEED * A_MED]
    for i in _big:
        svg += mark(x(i), slot, y(WA[i]["h"]), y(WA[i]["l"]), RED, 0.16)
    svg += RC._title(Wd, rt("وهالشبر تبلعه الشمعة العادية"))
    svg += RC._why(Wd, H, f'{ar(A_HIT)} من {ar(A_N)} شمعة مداها أكبر من '
                          f'{xr(A_NEED)}× — أي وحدة منهن تطقّه', RED)
    svg += sm(Wd, H, "فالوقف ما ينضرب بالتحليل، ينضرب بالضجيج")
    return svg + badge(Wd, "مثال تخطيطي", True) + "</svg>"


def a_all(r=None, Wd=880, H=250):
    """٥ · الخلاصة: الصفقة مو لك اليوم."""
    svg, x, y, slot = _ga(Wd, H)
    svg += hl(x(0) - slot * .5, x(A_N - 1) + slot * .5, y(WA[A_SW]["l"]), INK, 1.6, "5 6")
    svg += band(x(A_SW) - slot * .5, x(A_N - 1) + slot * .5,
                y(WA[A_ENT]["c"]), y(WA[A_SW]["l"]), RED, 0.12)
    svg += mark(x(A_ENT), slot, y(WA[A_ENT]["h"]), y(WA[A_ENT]["l"]), TEAL_D, 0.20)
    svg += RC._title(Wd, rt("صفقةٌ صحيحة وحسابٌ ما يشيلها"))
    svg += RC._why(Wd, H, f'الهيكل يطلب {xr(A_DIST)}× وأصغر عقدٍ يسمح '
                          f'{xr(A_NEED)}× — والفرق {xr(A_MULT)}×', INK)
    svg += sm(Wd, H, "أداة أصغر أو فريم أدنى أو تتركها — لا تصغّر وقفك")
    return svg + badge(Wd, "مثال تخطيطي", True) + "</svg>"


# ═════════════════════════════════════════════════════════════════
SETS = {"masafa": [m_level, m_far, m_six, m_one, m_all],
        "fataayil": [f_count, f_ratio, f_low, f_run, f_all],
        "taqleed": [q_imp, q_copy, q_cond, q_gap, q_all],
        "tadweer": [w_gap, w_none, w_size, w_fix, w_all],
        "adna": [a_setup, a_stop, a_squeeze, a_noise, a_all]}
WINS = {"masafa": RM, "fataayil": RF, "taqleed": RQ, "tadweer": RW, "adna": RA}
REAL = {"masafa": M_WIN}
SYN = {"fataayil": (F_SEED, F_ANCH), "taqleed": (Q_SEED, Q_ANCH),
       "tadweer": (W_SEED, W_ANCH), "adna": (A_SEED, A_ANCH)}


def unit_charts(slug):
    r = WINS[slug]
    ok, dropped = [], []
    for f in SETS[slug]:
        try:
            f(r if slug in REAL else None, 880, 250)
            ok.append(f)
        except AssertionError as e:
            dropped.append((f.__name__, str(e)))
    return r, ok, dropped


if __name__ == "__main__":
    for slug in SETS:
        r, ok, dropped = unit_charts(slug)
        print(f'{slug:<9} ثبت {len(ok)}/{len(SETS[slug])} · {r["slug"]}'
              + ("" if not dropped else " · سقط "
                 + " · ".join(f"{a}: {b}" for a, b in dropped)))
