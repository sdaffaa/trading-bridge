# -*- coding: utf-8 -*-
"""جارتات تشغيلة ٦٤ — سلاسل تخطيطية بالكامل.

مخزون النوافذ الحقيقية نفد على الفريمين معاً: `sheet_candidates.json`
صفرٌ حرّ من سبعٍ وستّين، ومسحُ الفريم اليومي في الصندوق أعطى ٣٣ مرشّحاً
كلَّها ساقطة (١٩ منشورة سابقاً · ١٠ لم تبلغ ٢R · ٤ أطول من اثنتين
وخمسين شمعة). فبُنيت وحدات اليوم بقاعدة §11 البديلة بشروطها الثلاثة:
شارة «مثال تخطيطي» على كل لوحة · كلُّ ادّعاءٍ مقيسٌ على السلسلة
بـ`assert` · أعدادٌ ونِسبٌ لا أسعار.

    python3 run64_charts.py
"""
import statistics as st

from reel_build import INK, TEAL, TEAL_D, RED, GREY, htext, gen
from run15_charts import hl, badge, frame
import run31_charts as RC
from run58_charts import ar, rt, why, sm, band, mark
from run59_charts import spanx, vspan, xr


def _lab(x, y, txt, col, fs=19):
    import run15_charts as R15
    if R15.MINIMAL:
        return ""
    return htext(x, y, txt, col, round(fs * RC._SC[0]))


def _free_col(W, lo, hi, prefer, half=2):
    """عمودٌ خالٍ يتّسع لوسمِ القياس الرأسي — مقيسٌ لا مقدَّر.

    الوسم الرأسي في ٦٣ وُضع بإزاحةٍ ثابتة عن شمعته، فوقع على الشموع
    هنا (رُصد بالفحص البصري 2026-09-09). فالموضع يُختار الآن بالبحث:
    عمودٌ لا تعبر أيُّ شمعةٍ فيه ولا في جيرانه المدى [lo, hi]، وأقربُه
    إلى الموضع المفضَّل. ويُبدأ بأوسعِ حرمٍ (`half`) ثم يُضيَّق شيئاً
    فشيئاً — لأن المدى الواسع (مدى شمعةٍ كاملة) لا يترك خمسةَ أعمدةٍ
    خالية أبداً، ويكفيه عمودٌ وجاراه. وإن لم يوجد رُفعت `AssertionError`
    فسقطت اللوحة في `unit_charts` بدل أن تُسلَّم مشوّهة."""
    for h in range(half, 0, -1):
        for j in sorted(range(len(W)), key=lambda k: abs(k - prefer)):
            a, b = max(0, j - h), min(len(W) - 1, j + h)
            if all(W[k]["h"] < lo or W[k]["l"] > hi for k in range(a, b + 1)):
                return j
    return None


# ═════════ ١ · اتفاق الفريمين (فنية · مثال تخطيطي) ═════════
# سلسلةُ دقائق واحدة، وشمعةُ الساعة تُجمَّع منها أربعاً أربعاً — فالفريمان
# بياناتٌ واحدة لا سلسلتان، وهذا شرطُ صدق الدرس: لو وُلّدت الساعة على
# حدة لأمكن أن تقول ما لا تقوله الدقائق.
A_SEED = 12051
A_ANCH = [(0, 100.0), (7, 99.4), (13, 99.8), (19, 100.6), (24, 99.9), (31, 99.6)]
A_N, A_K = 32, 4

WA = gen(A_ANCH, A_N, A_SEED, wick=0.65, bn=0.55)
RA = {"sym": "SCHEMATIC-A", "slug": "مثال تخطيطي — فريمان", "w": WA}


def _agg(W, K):
    out = []
    for s in range(0, len(W), K):
        g = W[s:s + K]
        out.append(dict(d=str(s // K), o=g[0]["o"], c=g[-1]["c"],
                        h=max(x["h"] for x in g), l=min(x["l"] for x in g)))
    return out


HA = _agg(WA, A_K)
A_LVL = max(c["h"] for c in WA[12:19])           # قمّة الدقائق المكسورة
A_BK = next(i for i in range(19, 25)
            if WA[i]["c"] > A_LVL and WA[i]["c"] > WA[i]["o"])
A_KI = A_BK // A_K                                # شمعة الساعة التي تحويه
A_HLVL = max(h["h"] for h in HA[:A_KI])           # قمّة الساعة قبلها
A_RUN = max(c["h"] for c in WA[A_BK:min(A_BK + A_K, A_N)])
A_BACK = next(j for j in range(A_BK + 1, A_N) if WA[j]["c"] < A_LVL)
_A_R = [c["h"] - c["l"] for c in WA]
A_MED = st.median(_A_R)
A_GAP = (A_HLVL - A_LVL) / A_MED

assert len(HA) == A_N // A_K == 8, len(HA)
assert WA[A_BK]["c"] > A_LVL, "شمعة الكسر لا تغلق فوق قمّة الدقائق"
assert A_RUN < A_HLVL, "الدقائق بلغت قمّة الساعة — فلا تعارض بين الفريمين"
assert 3 <= A_BACK - A_BK <= 6, A_BACK - A_BK
assert A_GAP >= 1.15, f"الفجوة بين القمّتين {A_GAP:.2f} وسيط"
assert HA[A_KI]["c"] < HA[A_KI]["h"], "شمعة الساعة أغلقت على قمّتها"


def _ga(Wd, H):
    return frame(WA, Wd, H, pad=0.10, pb=66)


def _gh(Wd, H):
    return frame(HA, Wd, H, pad=0.12, pb=66)


def a_low(r=None, Wd=880, H=250):
    """الدقائق وحدها: إغلاقٌ فوق قمّةٍ محلّية — إشارةُ كسرٍ مكتملة."""
    svg, x, y, slot = _ga(Wd, H)
    svg += hl(x(12) - slot * .5, x(A_BK) + slot * .8, y(A_LVL), INK, 1.7)
    svg += mark(x(A_BK), slot, y(WA[A_BK]["h"]), y(WA[A_BK]["l"]), TEAL_D, 0.22)
    svg += RC._title(Wd, rt("على الدقائق: كسرٌ مكتمل"))
    svg += why(Wd, H, f'الشمعة {ar(A_BK + 1)} أغلقت فوق قمّةِ {ar(7)} شمعات قبلها', TEAL_D)
    svg += sm(Wd, H, "ولو وقفتَ عند هذي اللوحة وحدها لدخلت — والإشارة تامّة")
    return svg + badge(Wd, "مثال تخطيطي", True) + "</svg>"


def a_high(r=None, Wd=880, H=250):
    """والساعة من البيانات نفسها: القمّة أعلى بكثير ولم تُلمس."""
    svg, x, y, slot = _gh(Wd, H)
    svg += hl(x(0) - slot * .5, x(len(HA) - 1) + slot * .5, y(A_HLVL), RED, 1.7)
    svg += mark(x(A_KI), slot, y(HA[A_KI]["h"]), y(HA[A_KI]["l"]), RED, 0.18)
    svg += RC._title(Wd, rt("وعلى الساعة: لا شيء"))
    svg += why(Wd, H, 'شمعةُ الساعة التي تحوي الكسر أغلقت دون قمّتها ودون قمّة السابقات', RED)
    svg += sm(Wd, H, f'كلُّ {ar(A_K)} شمعات دقائق = شمعةُ ساعةٍ واحدة — البيانات نفسها')
    return svg + badge(Wd, "مثال تخطيطي", True) + "</svg>"


def a_gap(r=None, Wd=880, H=250):
    """المسافة بين القمّتين مقيسةٌ بوسيط الشمعة لا بالسعر."""
    svg, x, y, slot = _ga(Wd, H)
    svg += band(x(12) - slot * .5, x(A_N - 1) + slot * .5, y(A_HLVL), y(A_LVL), TEAL, 0.13)
    svg += hl(x(12) - slot * .5, x(A_N - 1) + slot * .5, y(A_LVL), INK, 1.6, "5 6")
    svg += hl(x(12) - slot * .5, x(A_N - 1) + slot * .5, y(A_HLVL), RED, 1.7)
    j = _free_col(WA, A_LVL, A_HLVL, A_N - 4)
    assert j is not None, "لا عمود يخلو من الشموع لوسم المسافة"
    # لا قوسَ هنا: حدّا الشريط نفسُهما يريان المسافة، والقوسُ فوقهما يمرّ
    # في وسط حروف الوسم مهما أُزيح. فالوسم وحده داخل العمود الخالي.
    svg += _lab(x(j), y(A_HLVL) + 30, rt(f'{xr(A_GAP)} الشمعة'), INK, 17)
    svg += RC._title(Wd, rt("المسافة بين القمّتين"))
    svg += why(Wd, H, f'قمّةُ الساعة تعلو قمّةَ الدقائق بـ{xr(A_GAP)} وسيطِ الشمعة', INK)
    svg += sm(Wd, H, "وهذي المسافة هي ثمنُ الدخول على إشارةٍ لم يوقّعها الفريم الأكبر")
    return svg + badge(Wd, "مثال تخطيطي", True) + "</svg>"


def a_back(r=None, Wd=880, H=250):
    """ثم يعود الإغلاق تحت القمّة نفسها بعد شمعاتٍ معدودة."""
    n = A_BACK - A_BK
    svg, x, y, slot = _ga(Wd, H)
    svg += hl(x(12) - slot * .5, x(A_N - 1) + slot * .5, y(A_LVL), INK, 1.6, "5 6")
    svg += mark(x(A_BACK), slot, y(WA[A_BACK]["h"]), y(WA[A_BACK]["l"]), RED, 0.22)
    svg += RC._title(Wd, rt("والعودة تحتها"))
    svg += why(Wd, H, f'{ar(n)} شمعات ورجع الإغلاق تحت القمّة المكسورة', RED)
    svg += sm(Wd, H, "فالكسرُ الذي رأيته صحيحٌ على فريمه، وغيرُ مؤثّرٍ على ما فوقه")
    return svg + badge(Wd, "مثال تخطيطي", True) + "</svg>"


def a_all(r=None, Wd=880, H=250):
    """السلسلة كاملة — مرجعُ كلِّ رقمٍ في الوحدة."""
    assert len(WA) == A_N, len(WA)
    svg, x, y, slot = _ga(Wd, H)
    svg += hl(x(0) - slot * .5, x(A_N - 1) + slot * .5, y(A_LVL), GREY, 1.4, "5 6")
    svg += hl(x(0) - slot * .5, x(A_N - 1) + slot * .5, y(A_HLVL), GREY, 1.4, "5 6")
    svg += RC._title(Wd, rt("السلسلة كاملة"))
    svg += why(Wd, H, f'{ar(A_N)} شمعة دقائق = {ar(len(HA))} شمعات ساعة', INK)
    svg += sm(Wd, H, "ولا سعرَ مكتوبٌ هنا، فالرسم تخطيطي لا طبعةُ سوق")
    return svg + badge(Wd, "مثال تخطيطي", True) + "</svg>"


# ═════════ ٢ · أوّل ساعة بعد الافتتاح (أساسية · مثال تخطيطي) ═════════
B_SEED = 20424
B_ANCH = [(0, 50.0), (6, 49.8), (11, 50.0), (14, 50.7), (17, 50.1),
          (23, 49.7), (29, 49.9)]
B_N, B_OPEN, B_HOUR = 30, 12, 6           # عشرُ دقائق للشمعة ⇒ الساعة ستّ

WB = gen(B_ANCH, B_N, B_SEED, wick=0.7, bn=0.55)
RB = {"sym": "SCHEMATIC-B", "slug": "مثال تخطيطي — افتتاح", "w": WB}
B_PH = max(c["h"] for c in WB[:B_OPEN])
B_PL = min(c["l"] for c in WB[:B_OPEN])
B_END = B_OPEN + B_HOUR                   # أوّل شمعةٍ بعد الساعة الأولى
B_HI = max(c["h"] for c in WB[B_OPEN:B_END])
B_IB = max(range(B_OPEN, B_END), key=lambda i: WB[i]["h"])
_B_R = [c["h"] - c["l"] for c in WB]
B_MED = st.median(_B_R[:B_OPEN])
B_BIG = [i for i in range(B_OPEN, B_END) if _B_R[i] > B_MED]
B_OVER = (B_HI - B_PH) / B_MED
B_BACK = next(j for j in range(B_IB + 1, B_END) if WB[j]["c"] < B_PH)

assert B_HI > B_PH, "الساعة الأولى لم تتجاوز قمّة ما قبلها"
assert WB[B_END - 1]["c"] < B_PH, "الإغلاق لم يعد داخل المدى قبل انتهاء الساعة"
assert all(WB[j]["c"] < B_PH for j in range(B_END, B_N)), "القمّة كُسرت بعد الساعة"
assert min(c["l"] for c in WB[B_END:]) >= B_PL, "القاع كُسر بعد الساعة"
assert len(B_BIG) >= 4, len(B_BIG)
assert B_OVER >= 0.55, f"التجاوز {B_OVER:.2f} وسيط — لا يُرى"


def _gb(Wd, H):
    return frame(WB, Wd, H, pad=0.10, pb=66)


def _rng(svg, x, y, slot, a, b, col=INK, dash="5 6"):
    return (svg + hl(x(a) - slot * .5, x(b) + slot * .5, y(B_PH), col, 1.6, dash)
            + hl(x(a) - slot * .5, x(b) + slot * .5, y(B_PL), col, 1.6, dash))


def o_prev(r=None, Wd=880, H=250):
    """قبل الافتتاح: مدىً محفوظٌ بحدّين واضحين."""
    svg, x, y, slot = _gb(Wd, H)
    svg += band(x(0) - slot * .5, x(B_OPEN - 1) + slot * .5, y(B_PH), y(B_PL), TEAL, 0.13)
    svg += spanx(x(0) - slot * .5, x(B_OPEN - 1) + slot * .5, y(B_PH),
                 f'{ar(B_OPEN)} شمعة', GREY)
    svg += RC._title(Wd, rt("المدى الذي يسبق الجرس"))
    svg += why(Wd, H, f'{ar(B_OPEN)} شمعة بحدّين لم يُخترقا — وهذي هي المستويات', TEAL_D)
    svg += sm(Wd, H, "الحدّان مرسومان على أعلى فتيلٍ وأدنى فتيل، لا على الإغلاقات")
    return svg + badge(Wd, "مثال تخطيطي", True) + "</svg>"


def o_break(r=None, Wd=880, H=250):
    """وفي أوّل ساعة: تجاوزٌ فوق الحدّ العلوي."""
    svg, x, y, slot = _gb(Wd, H)
    svg = _rng(svg, x, y, slot, 0, B_N - 1)
    svg += mark(x(B_IB), slot, y(WB[B_IB]["h"]), y(WB[B_IB]["l"]), RED, 0.22)
    j = _free_col(WB, B_PH, B_HI, B_IB + 3)
    assert j is not None, "لا عمود يخلو من الشموع لوسم التجاوز"
    # الفجوة بين الحدّ والفتيل أضيقُ من أن تسع سطراً، وتحت القوس شموع —
    # فالوسم فوق طرفه الأعلى حيث لا شيء إلا هامشُ اللوحة.
    # وخيطٌ منقّطٌ يربط رأسَ القوس بفتيل الشمعة نفسها، وإلا قرأ الناظر
    # القياسَ على الشمعة التي تحته لا على التي وُضع من أجلها.
    svg += hl(x(B_IB), x(j), y(B_HI), RED, 1.2, "3 5")
    svg += vspan(x(j), y(B_HI), y(B_PH), "", RED, H=H)
    svg += _lab(x(j), y(B_HI) - 12, rt(f'{xr(B_OVER)} الشمعة'), RED, 17)
    svg += RC._title(Wd, rt("والساعة الأولى تتجاوزه"))
    svg += why(Wd, H, f'الفتيل يعلو الحدّ بـ{xr(B_OVER)} وسيطِ الشمعة قبل الافتتاح', RED)
    svg += sm(Wd, H, "ومن اشترى هنا اشترى تجاوزاً لم يُغلق فوقه أحد")
    return svg + badge(Wd, "مثال تخطيطي", True) + "</svg>"


def o_wide(r=None, Wd=880, H=250):
    """شمعاتُ الساعة الأولى أوسع من شمعات ما قبلها."""
    svg, x, y, slot = _gb(Wd, H)
    for i in B_BIG:
        # ٠٫١٤ يقرأ رمادياً على الكريمي — و§3-4 تمنع الرمادي. رُفع حتى
        # يُقرأ تركوازاً (فُحص بصرياً 2026-09-09).
        svg += mark(x(i), slot, y(WB[i]["h"]), y(WB[i]["l"]), TEAL_D, 0.22)
    svg += spanx(x(B_OPEN) - slot * .5, x(B_END - 1) + slot * .5,
                 y(max(c["h"] for c in WB[B_OPEN:B_END])), rt("أوّل ساعة"), INK)
    svg += RC._title(Wd, rt("لماذا تُكسر هنا بالذات"))
    svg += why(Wd, H, f'{ar(len(B_BIG))} من {ar(B_HOUR)} شمعات مداها فوق وسيطِ ما قبل الجرس', TEAL_D)
    svg += sm(Wd, H, "المدى يتّسع فيمرّ فوق الحدّ بلا نيّة — واتّساعُ المدى ليس قراراً")
    return svg + badge(Wd, "مثال تخطيطي", True) + "</svg>"


def o_back(r=None, Wd=880, H=250):
    """ثم يعود الإغلاق داخل المدى قبل أن تنتهي الساعة."""
    n = B_BACK - B_IB
    svg, x, y, slot = _gb(Wd, H)
    svg = _rng(svg, x, y, slot, 0, B_N - 1)
    svg += mark(x(B_BACK), slot, y(WB[B_BACK]["h"]), y(WB[B_BACK]["l"]), TEAL_D, 0.22)
    svg += RC._title(Wd, rt("والعودة داخل المدى"))
    svg += why(Wd, H, f'{ar(n)} شمعة ورجع الإغلاق تحت الحدّ — والساعة لم تنتهِ بعد', TEAL_D)
    svg += sm(Wd, H, f'وبقيّةُ الجلسة — {ar(B_N - B_END)} شمعة — أغلقت كلُّها داخل الحدّين')
    return svg + badge(Wd, "مثال تخطيطي", True) + "</svg>"


def o_all(r=None, Wd=880, H=250):
    """السلسلة كاملة — مرجعُ كلِّ رقمٍ في الوحدة."""
    assert len(WB) == B_N, len(WB)
    svg, x, y, slot = _gb(Wd, H)
    svg = _rng(svg, x, y, slot, 0, B_N - 1, GREY)
    svg += RC._title(Wd, rt("السلسلة كاملة"))
    svg += why(Wd, H, f'{ar(B_N)} شمعة · {ar(B_OPEN)} قبل الجرس و{ar(B_HOUR)} في أوّل ساعة', INK)
    svg += sm(Wd, H, "ولا سعرَ مكتوبٌ هنا، فالرسم تخطيطي لا طبعةُ سوق")
    return svg + badge(Wd, "مثال تخطيطي", True) + "</svg>"


# ═════════ ٣ · تضخيم الخسارة بالذاكرة (نفسية · مثال تخطيطي) ═════════
C_SEED = 18415
C_ANCH = [(0, 20.0), (9, 20.5), (17, 21.0), (24, 21.7), (27, 21.9),
          (28, 21.0), (33, 21.2)]
C_N, C_R = 34, 28                          # C_R = الشمعة المعاكسة الكبيرة

WC = gen(C_ANCH, C_N, C_SEED, wick=0.6, bn=0.5)
RC_ = {"sym": "SCHEMATIC-C", "slug": "مثال تخطيطي — ذاكرة", "w": WC}
_C_R = [c["h"] - c["l"] for c in WC]
C_MED = st.median(_C_R)
C_K = _C_R[C_R] / C_MED
C_UP = [i for i in range(C_R) if WC[i]["c"] > WC[i]["o"]]
C_DROP = WC[C_R]["o"] - WC[C_R]["c"]
# كم شمعةً صاعدةً سابقة يلزم جمعُ صافيها حتى يبلغ هبوطَ الشمعة المعاكسة.
_s, C_ERASE = 0.0, None
for _k in range(1, C_R + 1):
    _s += max(0.0, WC[C_R - _k]["c"] - WC[C_R - _k]["o"])
    if _s >= C_DROP:
        C_ERASE = _k
        break
C_NET = WC[-1]["c"] - WC[0]["o"]
C_SHARE = C_DROP / (max(c["h"] for c in WC) - min(c["l"] for c in WC))

assert _C_R[C_R] == max(_C_R), "الشمعة المعاكسة ليست الأكبر في السلسلة"
assert _C_R[C_R] / sorted(_C_R)[-2] >= 1.25, "لا تتميّز عن ثانيتها"
assert 2.6 <= C_K <= 6.0, f"مداها {C_K:.2f} وسيط"
assert WC[C_R]["c"] < WC[C_R]["o"], "الشمعة المعاكسة ليست هابطة"
assert len(C_UP) >= 18, len(C_UP)
assert C_ERASE is not None and 4 <= C_ERASE <= 12, C_ERASE
assert C_NET > 0, "النافذة انتهت خاسرة — فلا مبالغةَ في الذاكرة تُشرح"


def _gc(Wd, H):
    return frame(WC, Wd, H, pad=0.10, pb=66)


def c_run(r=None, Wd=880, H=250):
    """قبلها: أغلبُ الشمعات مشت مع الفكرة."""
    svg, x, y, slot = _gc(Wd, H)
    for i in C_UP:
        # TEAL_D عند شفافيةٍ منخفضة يُقرأ رمادياً على الكريمي، و§3-4 تمنع
        # الرمادي — فالتظليل بـTEAL الأفتح (فُحص بصرياً 2026-09-09).
        svg += mark(x(i), slot, y(WC[i]["h"]), y(WC[i]["l"]), TEAL, 0.22)
    # لا تُسمّى «حمراء»: الشمعة الهابطة في هويتنا كحليّة لا حمراء (§1)،
    # فالوصف اللوني يناقض ما يراه الناظر.
    svg += RC._title(Wd, rt("ما قبل الشمعة المعاكسة"))
    svg += why(Wd, H, f'{ar(len(C_UP))} من {ar(C_R)} شمعة أغلقت فوق فتحها', TEAL_D)
    svg += sm(Wd, H, "وهذا كلُّه لن تتذكّره — لأنه لم يوجعك ولا مرّة")
    return svg + badge(Wd, "مثال تخطيطي", True) + "</svg>"


def c_one(r=None, Wd=880, H=250):
    """والشمعة الواحدة: مدىً أضعافُ المعتاد."""
    svg, x, y, slot = _gc(Wd, H)
    svg += mark(x(C_R), slot, y(WC[C_R]["h"]), y(WC[C_R]["l"]), RED, 0.22)
    # مدى الشمعة الكبيرة يغطّي اللوحة كلَّها تقريباً، فلا عمودَ يخلو منه
    # ولو واحد — والقوس هنا يُقصد به المقارنة نفسها. فيُختار أقصرُ جارٍ
    # قبلها: أقلُّ حبرٍ يعبره القوس، وطرفاه يبرزان فوقه وتحته فتُقرأ
    # المقارنة من الشكل لا من السطر وحده.
    j = min(range(C_R - 4, C_R), key=lambda k: _C_R[k])
    assert _C_R[j] <= 0.6 * _C_R[C_R], "الجار المختار ليس أقصر بوضوح"
    svg += vspan(x(j), y(WC[C_R]["h"]), y(WC[C_R]["l"]), f'{xr(C_K)} الشمعة', RED, H=H)
    svg += RC._title(Wd, rt("الشمعة التي ستتذكّرها"))
    svg += why(Wd, H, f'مداها {xr(C_K)} وسيط السلسلة — وهي الأكبر فيها كلّها', RED)
    svg += sm(Wd, H, f'وحصّتها من مدى النافذة كلّه {ar(round(C_SHARE * 100))}٪ لا أكثر')
    return svg + badge(Wd, "مثال تخطيطي", True) + "</svg>"


def c_erase(r=None, Wd=880, H=250):
    """وما محته فعلاً: صافي شمعاتٍ معدودة لا الشهر كلّه."""
    a = C_R - C_ERASE
    svg, x, y, slot = _gc(Wd, H)
    svg += band(x(a) - slot * .5, x(C_R - 1) + slot * .5,
                y(max(c["h"] for c in WC[a:C_R])),
                y(min(c["l"] for c in WC[a:C_R])), TEAL, 0.13)
    svg += spanx(x(a) - slot * .5, x(C_R - 1) + slot * .5,
                 y(max(c["h"] for c in WC[a:C_R])), f'{ar(C_ERASE)} شمعة', INK)
    svg += mark(x(C_R), slot, y(WC[C_R]["h"]), y(WC[C_R]["l"]), RED, 0.20)
    svg += RC._title(Wd, rt("كم شمعةً محت فعلاً"))
    svg += why(Wd, H, f'هبوطُها يساوي صافيَ {ar(C_ERASE)} شمعةً صاعدة قبلها', INK)
    svg += sm(Wd, H, f'لا {ar(len(C_UP))} — والفرقُ بين الرقمين هو التضخيم نفسه')
    return svg + badge(Wd, "مثال تخطيطي", True) + "</svg>"


def c_net(r=None, Wd=880, H=250):
    """وبعدها: النافذة ما زالت فوق نقطة بدايتها."""
    svg, x, y, slot = _gc(Wd, H)
    svg += hl(x(0) - slot * .5, x(C_N - 1) + slot * .5, y(WC[0]["o"]), INK, 1.7)
    svg += mark(x(C_N - 1), slot, y(WC[-1]["h"]), y(WC[-1]["l"]), TEAL_D, 0.22)
    svg += RC._title(Wd, rt("وأين انتهت النافذة"))
    svg += why(Wd, H, "الإغلاق الأخير فوق فتح الشمعة الأولى — النافذة رابحة", TEAL_D)
    svg += sm(Wd, H, "والذاكرة تقول عكس ذلك، لأنها تحسب الوجع لا الصافي")
    return svg + badge(Wd, "مثال تخطيطي", True) + "</svg>"


def c_all(r=None, Wd=880, H=250):
    """السلسلة كاملة — مرجعُ كلِّ رقمٍ في الوحدة."""
    assert len(WC) == C_N, len(WC)
    svg, x, y, slot = _gc(Wd, H)
    svg += hl(x(0) - slot * .5, x(C_N - 1) + slot * .5, y(WC[0]["o"]), GREY, 1.4, "5 6")
    svg += RC._title(Wd, rt("السلسلة كاملة"))
    svg += why(Wd, H, f'{ar(C_N)} شمعة تخطيطية — والأرقام أعدادٌ ونِسب', INK)
    svg += sm(Wd, H, "ولا سعرَ مكتوبٌ هنا، فالرسم تخطيطي لا طبعةُ سوق")
    return svg + badge(Wd, "مثال تخطيطي", True) + "</svg>"


SETS = {"fremain": [a_low, a_high, a_gap, a_back, a_all],
        "iftitah": [o_prev, o_break, o_wide, o_back, o_all],
        "thakira": [c_run, c_one, c_erase, c_net, c_all]}
WINS = {"fremain": RA, "iftitah": RB, "thakira": RC_}
REAL = {}
SYN = {"fremain": (A_SEED, A_ANCH), "iftitah": (B_SEED, B_ANCH),
       "thakira": (C_SEED, C_ANCH)}


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
