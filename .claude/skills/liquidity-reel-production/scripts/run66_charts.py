# -*- coding: utf-8 -*-
"""جارتات تشغيلة ٦٦ — ثلاثُ سلاسل تخطيطية سُلّمت، ووحدتان سوقيّتان رُحّلتا.

المخزون بدا حرّاً وهو ليس كذلك: قياسُ الفراغ بمقارنة `su`/`eu` بالسجل أعطى
**خمس** نوافذ، فبُنيت عليها وحدتان فنيتان كاملتان. ثم سقطتا عند
`RC.claim_fresh` لأن `_span` يبني مفتاحَ نوافذِ الدقائق من `date + d` لا من
`su`/`eu` — والحرُّ بمقياس المحرّك **صفر**. فالقاعدة: **لا يُقاس الفراغ إلا
بالدالّة التي تحرسه**، وكلُّ فحصٍ موازٍ يكذب.

فالوحدات المسلَّمة ثلاثٌ بقاعدة §11 البديلة بشروطها الثلاثة: شارة «مثال
تخطيطي» على كل لوحة · كلُّ ادّعاءٍ مقيسٌ بـ`assert` · أعدادٌ ونِسبٌ لا أسعار.
ووحدتا `habs` و`hissa` تبقيان هنا كاملتَي القياس — نافذتاهما مقيَّدتان
سابقاً فلا تُبنيان، ونصّاهما في `content/deferred/`.

    python3 run66_charts.py
"""
import statistics as st

from reel_build import INK, TEAL, TEAL_D, RED, GREY, htext, gen
from run15_charts import hl, badge, frame
import run31_charts as RC
from run58_charts import ar, rt, why, sm, band, mark
from run59_charts import spanx, vspan, xr


# ═════════════════════════════════════════════════════════════════
# ١ · «حبس» — المدى الذي حبس ثلاث عشرة شمعة (فنية · ريل · سوقٌ حقيقي)
#     الذهب · ٣٠ دقيقة · 2026-06-26 · ٤٩ شمعة
#
# وهذه الوحدة بديلةُ «قفزة» (الموضوع ١٢٣): درسُ القفزة يُقاس على إغلاقِ
# شمعةٍ وفتحِ التي تليها، والنافذتان اليوميّتان الوحيدتان الحرّتان
# (الأسترالي/الدولار والأسترالي/الين) موسومتان `bad` بسببٍ يصيب الدرسَ في
# مقتله: «وسيط الجسم/المدى 0.02 — شموع دوجي متتالية، إغلاق يومي غير
# موثوق». أي أنّ الافتتاحات نفسها مركّبةٌ لا مرصودة — فقياسُ القفزات
# عليها يقيس صناعةَ المزوّد لا فعلَ السوق. رُحّلت الوحدة، ولم تُخفَّض
# عتبة.
# ═════════════════════════════════════════════════════════════════
B_WIN = 23
RB_ = RC.win(B_WIN)
WB = RB_["w"]
B_N = len(WB)
B_BK = RB_["bk"]                                  # شمعة الكسر كما قاسها المسح
B_PRE = WB[:B_BK]
B_HI = max(c["h"] for c in B_PRE)
B_LO = min(c["l"] for c in B_PRE)
B_R = B_HI - B_LO
B_MED = st.median(c["h"] - c["l"] for c in WB)
B_BODY = abs(WB[B_BK]["c"] - WB[B_BK]["o"])
B_TI = max(range(B_BK + 1, B_N), key=lambda j: WB[j]["h"])
B_EXT = (WB[B_TI]["h"] - B_HI) / B_R
B_BACK = next(j for j in range(B_BK + 1, B_N) if WB[j]["l"] <= B_HI)
B_LONGEST = max(c["h"] - c["l"] for c in B_PRE) / B_MED

assert len(B_PRE) >= 12, len(B_PRE)
assert all(c["h"] <= B_HI and c["l"] >= B_LO for c in B_PRE), "شمعةٌ خرجت من المدى قبل الكسر"
assert WB[B_BK]["c"] > B_HI, "شمعة الكسر لم تُغلق فوق الحدّ"
assert B_BODY / B_MED >= 1.8, B_BODY / B_MED
assert B_EXT >= 1.0, B_EXT
assert B_LONGEST <= 1.6, B_LONGEST


def _gb(Wd, H):
    return RC._geo(WB, Wd, H)


def _rangebox(x, y, slot, col=TEAL, op=0.16):
    return RC.zbox(x(0) - slot * .5, y(B_HI), x(B_BK - 1) + slot * .5, y(B_LO),
                   col=col, op=op)


def b_range(r=None, Wd=880, H=250):
    """١ · المدى عرضٌ يُقاس قبل الكسر لا بعده."""
    svg, x, y, slot = _gb(Wd, H)
    svg += _rangebox(x, y, slot)
    svg += hl(x(0) - slot * .5, x(B_N - 1) + slot * .5, y(B_HI), INK, 1.8)
    svg += hl(x(0) - slot * .5, x(B_N - 1) + slot * .5, y(B_LO), INK, 1.8)
    svg += vspan(x(B_BK) + slot * 2.4, y(B_HI), y(B_LO),
                 rt(f'{xr(B_R / B_MED)} وسيطِ الشمعة'), INK, 16, H)
    svg += RC._title(Wd, rt("عرضُ المدى — رقمٌ قبل الكسر"))
    svg += RC._why(Wd, H, f'الحدّان {B_LO:,.2f} و{B_HI:,.2f} — بينهما '
                          f'{RC.pips(RB_, B_HI, B_LO)} نقطة', INK)
    svg += RC._sum(Wd, H, "وهذا العرضُ هو المسطرةُ التي تقيس بها ما بعده")
    return svg + badge(Wd, "المدى", True) + "</svg>"


def b_inside(r=None, Wd=880, H=250):
    """٢ · ثلاث عشرة شمعة — ولا واحدةَ خرجت."""
    svg, x, y, slot = _gb(Wd, H)
    svg += _rangebox(x, y, slot)
    svg += spanx(x(0) - slot * .5, x(B_BK - 1) + slot * .5, y(B_HI),
                 rt(f'{ar(len(B_PRE))} شمعة'), INK)
    svg += RC._title(Wd, rt("ثلاثَ عشرةَ شمعةً داخله"))
    svg += RC._why(Wd, H, f'ولا قمّةَ فوق الحدّ ولا قاعَ تحته — وأطولُهنّ '
                          f'{xr(B_LONGEST)} وسيطِ الشمعة فقط', INK)
    svg += RC._sum(Wd, H, "وهذا ليس سوقاً ميتاً — هذا تراكمٌ يُقاس عرضُه ويُنتظر")
    return svg + badge(Wd, "داخل المدى", True) + "</svg>"


def b_break(r=None, Wd=880, H=250):
    """٣ · شمعةٌ واحدة أخرجته — بجسمٍ ضِعفَي الوسيط."""
    svg, x, y, slot = _gb(Wd, H)
    svg += _rangebox(x, y, slot, GREY, 0.14)
    svg += hl(x(0) - slot * .5, x(B_N - 1) + slot * .5, y(B_HI), INK, 1.8)
    svg += mark(x(B_BK), slot, y(WB[B_BK]["h"]), y(WB[B_BK]["l"]), TEAL, 0.24)
    svg += RC._title(Wd, rt("الكسر — جسمٌ لا لمسة"))
    svg += RC._why(Wd, H, f'جسمُ شمعة الكسر {RC.pips(RB_, WB[B_BK]["c"], WB[B_BK]["o"])} '
                          f'نقطة = {xr(B_BODY / B_MED)} وسيطِ الشمعة', TEAL_D)
    svg += RC._sum(Wd, H, "أكبرُ ممّا صنعته ثلاثَ عشرةَ شمعةً مجتمعةً داخل المدى")
    return svg + badge(Wd, "شمعة الكسر", True) + "</svg>"


def b_ext(r=None, Wd=880, H=250):
    """٤ · والامتداد بعده — بعرضِ المدى ونصفٍ تقريباً."""
    svg, x, y, slot = _gb(Wd, H)
    svg += hl(x(0) - slot * .5, x(B_N - 1) + slot * .5, y(B_HI), INK, 1.8)
    svg += band(x(B_BK) - slot * .5, x(B_TI) + slot * .5,
                y(WB[B_TI]["h"]), y(B_HI), TEAL, 0.18)
    svg += vspan(x(B_TI) + slot * 2.0, y(WB[B_TI]["h"]), y(B_HI),
                 rt(f'{xr(B_EXT)} عرضِ المدى'), TEAL_D, 16, H)
    svg += RC.tick(x(B_TI), y(WB[B_TI]["h"]) - 18)
    svg += RC._title(Wd, rt("ما بعد الحدّ — بمقياسِ ما قبله"))
    svg += RC._why(Wd, H, f'بلغ {WB[B_TI]["h"]:,.2f} بعد {ar(B_TI - B_BK)} شمعاتٍ من '
                          f'الكسر — أي {xr(B_EXT)} عرضِ المدى فوق حدّه', TEAL_D)
    svg += RC._sum(Wd, H, f'وعاد فلمس الحدّ بعد {ar(B_BACK - B_BK)} شمعتين — ثم مضى')
    return svg + badge(Wd, "الامتداد", True) + "</svg>"


def b_all(r=None, Wd=880, H=250):
    """٥ · النافذة كاملةً — مرجعُ كلِّ رقمٍ في الوحدة."""
    svg, x, y, slot = _gb(Wd, H)
    svg += _rangebox(x, y, slot, GREY, 0.14)
    svg += hl(x(0) - slot * .5, x(B_N - 1) + slot * .5, y(B_HI), INK, 1.8)
    svg += hl(x(0) - slot * .5, x(B_N - 1) + slot * .5, y(B_LO), INK, 1.4, "6 6")
    svg += mark(x(B_BK), slot, y(WB[B_BK]["h"]), y(WB[B_BK]["l"]), TEAL, 0.22)
    svg += RC.tick(x(B_TI), y(WB[B_TI]["h"]) - 18)
    svg += RC._title(Wd, rt("النافذة كاملةً"))
    svg += RC._why(Wd, H, f'المدى {xr(B_R / B_MED)} الوسيط · {ar(len(B_PRE))} شمعة داخله · '
                          f'الكسر {xr(B_BODY / B_MED)} · الامتداد {xr(B_EXT)} عرضِه', INK)
    svg += RC._sum(Wd, H, "قِس قبل أن يتحرّك — فبعد الحركة لا يبقى ما تقيس عليه")
    return svg + badge(Wd, "الحصيلة", True) + "</svg>"


# ═════════════════════════════════════════════════════════════════
# ٢ · «حصة» — حصّةُ شمعةٍ واحدة من الحركة (فنية · ريل · سوقٌ حقيقي)
#     البلاتين · ساعة · 2026-07-28 → 2026-07-30 · ٤٥ شمعة
# ═════════════════════════════════════════════════════════════════
H_WIN = 59
RH = RC.win(H_WIN)
WH = RH["w"]
H_N = len(WH)
H_LO = min(range(H_N), key=lambda i: WH[i]["l"])
H_HI = max(range(H_LO, H_N), key=lambda i: WH[i]["h"])
H_SEG = WH[H_LO:H_HI + 1]
H_NET = WH[H_HI]["c"] - WH[H_LO]["o"]
H_MED = st.median(c["h"] - c["l"] for c in H_SEG)
# «المساهمة» جسمُ الشمعة لا مداها: مدىً يذهب ويعود لا يحرّك الساق شيئاً،
# وأكبرُ شمعةٍ مدىً في نافذةِ الأسترالي/الدولار أغلقت على فتحها تماماً.
_H_C = sorted(((c["c"] - c["o"], i) for i, c in enumerate(H_SEG)),
              key=lambda t: abs(t[0]), reverse=True)
H_TOP, H_TI = _H_C[0]
H_SEC = _H_C[1][0]
H_ONE = WH[H_LO + H_TI]
H_SHARE = H_TOP / H_NET
H_REST = H_NET - H_TOP
H_UPS = sum(1 for c in H_SEG if c["c"] > c["o"])

assert H_NET > 0 and len(H_SEG) >= 20, (H_NET, len(H_SEG))
assert 0.50 <= H_SHARE <= 0.70, H_SHARE
assert abs(H_SEC) / abs(H_TOP) <= 0.85, abs(H_SEC) / abs(H_TOP)
assert (H_ONE["h"] - H_ONE["l"]) / H_MED >= 2.4, (H_ONE["h"] - H_ONE["l"]) / H_MED


def _gh(Wd, H):
    return RC._geo(WH, Wd, H)


def h_leg(r=None, Wd=880, H=250):
    """١ · الساق: من قاعِ النافذة إلى قمّتها، ستٌّ وعشرون شمعة."""
    svg, x, y, slot = _gh(Wd, H)
    svg += hl(x(H_LO) - slot * .5, x(H_N - 1) + slot * .5, y(WH[H_LO]["o"]), GREY, 1.4, "5 6")
    svg += hl(x(H_LO) - slot * .5, x(H_N - 1) + slot * .5, y(WH[H_HI]["c"]), GREY, 1.4, "5 6")
    svg += spanx(x(H_LO) - slot * .5, x(H_HI) + slot * .5, y(WH[H_HI]["c"]),
                 rt(f'{ar(len(H_SEG))} شمعة'), INK)
    svg += RC._title(Wd, rt("الساقُ كما يراها من يعدّ الساعات"))
    svg += RC._why(Wd, H, f'{ar(len(H_SEG))} ساعة بين القاع والقمّة — '
                          f'صافيها {RC.pips(RH, WH[H_HI]["c"], WH[H_LO]["o"])} نقطة', INK)
    svg += RC._sum(Wd, H, "والسؤال ليس كم تحرّك، بل مَن حرّكه من هذه الشمعات")
    return svg + badge(Wd, "الساق", True) + "</svg>"


def h_one(r=None, Wd=880, H=250):
    """٢ · شمعةٌ واحدة حملت أكثرَ من نصف الصافي."""
    svg, x, y, slot = _gh(Wd, H)
    svg += mark(x(H_LO + H_TI), slot, y(H_ONE["h"]), y(H_ONE["l"]), TEAL, 0.24)
    svg += band(x(H_LO + H_TI) - slot * .5, x(H_LO + H_TI) + slot * .5,
                y(H_ONE["c"]), y(H_ONE["o"]), TEAL_D, 0.28)
    svg += vspan(x(H_LO + H_TI) + slot * 1.9, y(H_ONE["c"]), y(H_ONE["o"]),
                 rt(f'{ar(round(H_SHARE * 100, 1))}٪ من الصافي'), TEAL_D, 16, H)
    svg += RC._title(Wd, rt("شمعةٌ واحدة — ونصفُ الحركة"))
    svg += RC._why(Wd, H, f'جسمُها {RC.pips(RH, H_ONE["c"], H_ONE["o"])} نقطة من أصل '
                          f'{RC.pips(RH, WH[H_HI]["c"], WH[H_LO]["o"])} نقطة للساق كلّها', TEAL_D)
    svg += RC._sum(Wd, H, "والجسمُ لا المدى: مدىً يذهب ويعود لا ينقل السعر من مكانه")
    return svg + badge(Wd, "الشمعة الواحدة", True) + "</svg>"


def h_rest(r=None, Wd=880, H=250):
    """٣ · الخمسُ والعشرون الباقية اقتسمن أقلَّ من النصف."""
    svg, x, y, slot = _gh(Wd, H)
    svg += band(x(H_LO) - slot * .5, x(H_HI) + slot * .5,
                y(WH[H_HI]["c"]), y(WH[H_LO]["o"]), GREY, 0.14)
    svg += mark(x(H_LO + H_TI), slot, y(H_ONE["h"]), y(H_ONE["l"]), TEAL, 0.24)
    svg += RC._title(Wd, rt("والباقي؟ خمسٌ وعشرون شمعة"))
    svg += RC._why(Wd, H, f'مجموعُ أجسادِهنّ {RC.pips(RH, H_REST, 0)} نقطة = '
                          f'{ar(round(100 * H_REST / H_NET, 1))}٪ فقط', INK)
    svg += RC._sum(Wd, H, f'و{ar(H_UPS)} منهنّ فقط صاعدة — أي أن نصف الوقت تذبذبٌ لا حركة')
    return svg + badge(Wd, "الباقي", False) + "</svg>"


def h_ratio(r=None, Wd=880, H=250):
    """٤ · وليست مجرّد الأكبر — هي أكبرُ من الثانية بفارقٍ يُرى."""
    svg, x, y, slot = _gh(Wd, H)
    j2 = H_LO + _H_C[1][1]
    svg += mark(x(H_LO + H_TI), slot, y(H_ONE["h"]), y(H_ONE["l"]), TEAL, 0.24)
    svg += mark(x(j2), slot, y(WH[j2]["h"]), y(WH[j2]["l"]), GREY, 0.22)
    svg += RC._title(Wd, rt("الأولى والثانية — والفرقُ بينهما"))
    svg += RC._why(Wd, H, f'مدى الشمعة الأولى {xr((H_ONE["h"] - H_ONE["l"]) / H_MED)} '
                          f'وسيطِ الساق، وجسمُ الثانية '
                          f'{ar(round(100 * abs(H_SEC) / abs(H_TOP)))}٪ من جسمها', TEAL_D)
    svg += RC._sum(Wd, H, "ولو تقاربتا لما صحّ الدرس — فالتفوّقُ شرطٌ يُقاس لا وصفٌ يُكتب")
    return svg + badge(Wd, "النسبة", True) + "</svg>"


def h_all(r=None, Wd=880, H=250):
    """٥ · النافذة كاملةً — مرجعُ كلِّ رقمٍ في الوحدة."""
    svg, x, y, slot = _gh(Wd, H)
    svg += hl(x(0) - slot * .5, x(H_N - 1) + slot * .5, y(WH[H_LO]["o"]), GREY, 1.4, "5 6")
    svg += hl(x(0) - slot * .5, x(H_N - 1) + slot * .5, y(WH[H_HI]["c"]), GREY, 1.4, "5 6")
    svg += mark(x(H_LO + H_TI), slot, y(H_ONE["h"]), y(H_ONE["l"]), TEAL, 0.24)
    svg += RC._title(Wd, rt("النافذة كاملةً"))
    svg += RC._why(Wd, H, f'{ar(len(H_SEG))} ساعة · شمعةٌ واحدة '
                          f'{ar(round(H_SHARE * 100, 1))}٪ · والباقي '
                          f'{ar(round(100 * H_REST / H_NET, 1))}٪', INK)
    svg += RC._sum(Wd, H, "فالجلوسُ كلَّ ساعة لا يزيد حصّتك — يزيد عددَ الساعات التي تنتظرها")
    return svg + badge(Wd, "الحصيلة", True) + "</svg>"


# ═════════════════════════════════════════════════════════════════
# ٣ · «لوم» — إسنادُ السبب (نفسية · مثال تخطيطي)
# ═════════════════════════════════════════════════════════════════
L_SEED = 9365
L_ANCH = [(0, 96.0), (6, 95.2), (11, 95.4), (15, 94.0), (18, 95.6), (24, 97.6), (29, 98.4)]
L_N = 30
WL = gen(L_ANCH, L_N, L_SEED, wick=0.85, bn=0.5)
RL = {"sym": "SCHEMATIC-L", "slug": "مثال تخطيطي — لوم", "w": WL}
_L_R = [c["h"] - c["l"] for c in WL]
L_MED = st.median(_L_R)
L_LVL = min(c["l"] for c in WL[:11])          # المستوى: أدنى قاعٍ في ١١ الأولى
L_STP = L_LVL - L_MED * 0.15                  # وقفٌ ضيّقٌ تحته عمداً
L_SW = min(range(12, 19), key=lambda i: WL[i]["l"])
L_EXC = L_STP - WL[L_SW]["l"]                 # التجاوزُ تحت الوقف
L_SHORT = [r for r in _L_R if r < L_EXC]
L_BACK = next(i for i in range(L_SW + 1, L_N) if WL[i]["c"] > L_LVL)
L_RUN = (max(c["h"] for c in WL[L_BACK:]) - L_LVL) / L_MED

assert L_EXC > 0, "لا تجاوزَ تحت الوقف"
assert L_EXC / L_MED >= 1.4, L_EXC / L_MED
assert len(L_SHORT) >= 26, len(L_SHORT)
assert L_BACK - L_SW <= 3, (L_SW, L_BACK)
assert L_RUN >= 2.5, L_RUN


def _gl(Wd, H):
    return frame(WL, Wd, H, pad=0.10, pb=66)


def l_level(r=None, Wd=880, H=250):
    """١ · المستوى من شمعةٍ معلومة لا من النظر."""
    svg, x, y, slot = _gl(Wd, H)
    svg += hl(x(0) - slot * .5, x(L_N - 1) + slot * .5, y(L_LVL), INK, 1.8)
    _p = min(range(11), key=lambda i: WL[i]["l"])
    svg += mark(x(_p), slot, y(WL[_p]["h"]), y(WL[_p]["l"]), TEAL, 0.22)
    svg += RC._title(Wd, rt("المستوى نقطةٌ واحدة تُقرأ"))
    svg += why(Wd, H, f'أدنى قاعٍ في الشمعات {ar(11)} الأولى — رقمٌ واحدٌ تعرفه قبل الدخول', INK)
    svg += sm(Wd, H, "ولو رسمتَه بالنظر لتحرّك معك كلّما تحرّك السعر")
    return svg + badge(Wd, "مثال تخطيطي", True) + "</svg>"


def l_stop(r=None, Wd=880, H=250):
    """٢ · الوقف تحته بكسرٍ من شمعة — وهذا قرارُك أنت."""
    svg, x, y, slot = _gl(Wd, H)
    svg += hl(x(0) - slot * .5, x(L_N - 1) + slot * .5, y(L_LVL), INK, 1.8)
    svg += hl(x(0) - slot * .5, x(L_N - 1) + slot * .5, y(L_STP), RED, 1.8, "8 7")
    svg += vspan(x(3), y(L_LVL), y(L_STP), rt(f'{xr(0.15)} وسيطِ الشمعة'), RED, 16, H)
    svg += RC._title(Wd, rt("الوقف تحت المستوى — بكم؟"))
    svg += why(Wd, H, f'مسافةُ الوقف هنا {xr(0.15)} وسيطِ مدى الشمعة — ضيّقةٌ عمداً', RED)
    svg += sm(Wd, H, "وهذا أوّلُ رقمٍ تملك تغييره غداً، ولا يملكه أحدٌ غيرك")
    return svg + badge(Wd, "مثال تخطيطي", True) + "</svg>"


def l_sweep(r=None, Wd=880, H=250):
    """٣ · التجاوز: أطولُ من ثمانٍ وعشرين شمعةٍ كاملة."""
    svg, x, y, slot = _gl(Wd, H)
    svg += hl(x(0) - slot * .5, x(L_N - 1) + slot * .5, y(L_STP), RED, 1.8, "8 7")
    svg += mark(x(L_SW), slot, y(WL[L_SW]["h"]), y(WL[L_SW]["l"]), RED, 0.24)
    svg += vspan(x(L_SW) + slot * 2.2, y(L_STP), y(WL[L_SW]["l"]),
                 rt(f'{xr(L_EXC / L_MED)} الوسيط'), RED, 16, H)
    svg += RC._title(Wd, rt("ما تحت الوقف — مقيساً"))
    svg += why(Wd, H, f'التجاوزُ تحت الوقف {xr(L_EXC / L_MED)} وسيطِ الشمعة، '
                      f'و{ar(len(L_SHORT))} من {ar(L_N)} شمعةٍ مداها أقصرُ منه', RED)
    svg += sm(Wd, H, "والسبريدُ كسرٌ من شمعةٍ واحدة — فلا يفسّر مسافةً تفوق ثمانياً وعشرين")
    return svg + badge(Wd, "مثال تخطيطي", True) + "</svg>"


def l_back(r=None, Wd=880, H=250):
    """٤ · وعاد فوق المستوى بعد شمعتين ثم مضى."""
    svg, x, y, slot = _gl(Wd, H)
    svg += hl(x(0) - slot * .5, x(L_N - 1) + slot * .5, y(L_LVL), INK, 1.8)
    svg += band(x(L_BACK) - slot * .5, x(L_N - 1) + slot * .5,
                y(max(c["h"] for c in WL[L_BACK:])), y(L_LVL), TEAL, 0.16)
    svg += RC._title(Wd, rt("عاد فوقه — ثم مضى"))
    svg += why(Wd, H, f'عاد السعرُ فوق المستوى بعد {ar(L_BACK - L_SW)} شمعتين من القاع، '
                      f'ثم امتدّ {xr(L_RUN)} وسيطِ الشمعة', TEAL_D)
    svg += sm(Wd, H, "فالاتجاهُ كان صحيحاً، والذي أخرجك مسافةُ وقفٍ اخترتَها أنت")
    return svg + badge(Wd, "مثال تخطيطي", True) + "</svg>"


def l_all(r=None, Wd=880, H=250):
    """٥ · السلسلة كاملة — مرجعُ كلِّ رقمٍ في الوحدة."""
    assert len(WL) == L_N, len(WL)
    svg, x, y, slot = _gl(Wd, H)
    svg += hl(x(0) - slot * .5, x(L_N - 1) + slot * .5, y(L_LVL), INK, 1.8)
    svg += hl(x(0) - slot * .5, x(L_N - 1) + slot * .5, y(L_STP), RED, 1.4, "8 7")
    svg += mark(x(L_SW), slot, y(WL[L_SW]["h"]), y(WL[L_SW]["l"]), RED, 0.22)
    svg += RC._title(Wd, rt("السلسلة كاملة"))
    # ولا يبدأ مقطعٌ برقمٍ بعد «·»: النقطةُ الوسطى تجلس بارتفاع الأرقام
    # الهندية فتلتصق بها، فقُرئ «٢٨ ·» رقماً واحداً «٢٨٠» في أول رندر
    # (رُصد بالفحص البصري). فيُقدَّم لفظٌ على كلِّ رقمٍ يلي فاصلاً.
    svg += why(Wd, H, f'{ar(L_N)} شمعة · التجاوز {xr(L_EXC / L_MED)} الوسيط · '
                      f'وأقصرُ منه {ar(len(L_SHORT))} شمعةً · والامتداد بعده {xr(L_RUN)}', INK)
    svg += sm(Wd, H, "ولا سعرَ مكتوبٌ هنا، فالرسم تخطيطي لا طبعةُ سوق")
    return svg + badge(Wd, "مثال تخطيطي", True) + "</svg>"


# ═════════════════════════════════════════════════════════════════
# ٤ · «صيفي» — زحفُ الجلسة ساعة (أساسية · مثال تخطيطي)
#     ٤٨ شمعة عشر دقائق ⇒ ثماني شمعات ساعة
# ═════════════════════════════════════════════════════════════════
S_SEED = 15285
S_ANCH = [(0, 2412), (5, 2406), (11, 2411), (14, 2420), (17, 2432), (22, 2424),
          (28, 2431), (34, 2421), (40, 2430), (47, 2423)]
S_N = 48
WS = gen(S_ANCH, S_N, S_SEED, wick=0.85, bn=0.6)
RS = {"sym": "SCHEMATIC-S", "slug": "مثال تخطيطي — صيفي", "w": WS}
S_HR = [dict(o=WS[6 * k]["o"], h=max(c["h"] for c in WS[6 * k:6 * k + 6]),
             l=min(c["l"] for c in WS[6 * k:6 * k + 6]), c=WS[6 * k + 5]["c"])
        for k in range(8)]
S_DAY = max(c["h"] for c in WS) - min(c["l"] for c in WS)
S_HMED = st.median(h["h"] - h["l"] for h in S_HR)
S_BIG = max(range(8), key=lambda k: S_HR[k]["h"] - S_HR[k]["l"])
S_RB = (S_HR[S_BIG]["h"] - S_HR[S_BIG]["l"]) / S_HMED


def _swin(a, b):
    """نسبةُ ما تلتقطه نافذةٌ من ساعات اليوم إلى مدى اليوم كلّه."""
    seg = S_HR[a:b]
    return (max(h["h"] for h in seg) - min(h["l"] for h in seg)) / S_DAY


S_A = _swin(2, 5)                # نافذتك بتوقيتها الأصلي — الساعات ٢·٣·٤
S_B = _swin(3, 6)                # وبعد أن تزحف ساعة — الساعات ٣·٤·٥

assert S_BIG == 2, S_BIG
assert S_A >= 0.80 and S_B <= 0.42, (S_A, S_B)
assert S_RB >= 2.4, S_RB


def _gs(Wd, H):
    return frame(WS, Wd, H, pad=0.10, pb=66)


def _hourlines(x, y, slot, H):
    s = ""
    for k in range(1, 8):
        xx = x(6 * k) - slot * .5
        s += (f'<line x1="{xx:.1f}" y1="58" x2="{xx:.1f}" y2="{H - 50:.0f}" '
              f'stroke="{GREY}" stroke-width="1" stroke-dasharray="3 5" opacity=".55"/>')
    return s


def s_hours(r=None, Wd=880, H=250):
    """١ · اليومُ ثماني ساعات، كلُّ ساعةٍ ستُّ شمعات."""
    svg, x, y, slot = _gs(Wd, H)
    svg += _hourlines(x, y, slot, H)
    svg += RC._title(Wd, rt("اليوم — ثماني ساعات"))
    svg += why(Wd, H, f'{ar(S_N)} شمعةَ عشرِ دقائق تُجمَّع ستّاً ستّاً ⇒ {ar(8)} شمعاتِ ساعة', INK)
    svg += sm(Wd, H, "والخطوطُ المنقّطة حدودُ الساعات — لا مستوياتِ سعر")
    return svg + badge(Wd, "مثال تخطيطي", True) + "</svg>"


def s_big(r=None, Wd=880, H=250):
    """٢ · ساعةٌ واحدة تحمل الحركة."""
    svg, x, y, slot = _gs(Wd, H)
    svg += _hourlines(x, y, slot, H)
    svg += band(x(6 * S_BIG) - slot * .5, x(6 * S_BIG + 5) + slot * .5,
                y(S_HR[S_BIG]["h"]), y(S_HR[S_BIG]["l"]), TEAL, 0.20)
    svg += RC._title(Wd, rt("ساعةُ الحركة — مقيسةً"))
    svg += why(Wd, H, f'الساعةُ الثالثة مداها {xr(S_RB)} وسيطِ مدى الساعة في هذا اليوم', TEAL_D)
    svg += sm(Wd, H, "وهذه الساعةُ وحدها هي التي تدفع نتيجتَك — والباقي جلوس")
    return svg + badge(Wd, "مثال تخطيطي", True) + "</svg>"


def s_winA(r=None, Wd=880, H=250):
    """٣ · نافذتك بتوقيتها الأصلي."""
    svg, x, y, slot = _gs(Wd, H)
    svg += _hourlines(x, y, slot, H)
    seg = S_HR[2:5]
    svg += band(x(12) - slot * .5, x(29) + slot * .5,
                y(max(h["h"] for h in seg)), y(min(h["l"] for h in seg)), TEAL, 0.18)
    svg += RC._title(Wd, rt("ثلاثُ ساعاتٍ — بتوقيتها الأصلي"))
    svg += why(Wd, H, f'تلتقط {ar(round(S_A * 100, 1))}٪ من مدى اليوم كلّه', TEAL_D)
    svg += sm(Wd, H, "لأن ساعةَ الحركة داخلها — لا لأن النافذة طويلة")
    return svg + badge(Wd, "مثال تخطيطي", True) + "</svg>"


def s_winB(r=None, Wd=880, H=250):
    """٤ · وبعد أن تزحف ساعةً واحدة."""
    svg, x, y, slot = _gs(Wd, H)
    svg += _hourlines(x, y, slot, H)
    seg = S_HR[3:6]
    svg += band(x(18) - slot * .5, x(35) + slot * .5,
                y(max(h["h"] for h in seg)), y(min(h["l"] for h in seg)), RED, 0.18)
    svg += band(x(6 * S_BIG) - slot * .5, x(6 * S_BIG + 5) + slot * .5,
                y(S_HR[S_BIG]["h"]), y(S_HR[S_BIG]["l"]), GREY, 0.16)
    svg += RC._title(Wd, rt("نفسُ الثلاث — بعد زحفِ ساعة"))
    svg += why(Wd, H, f'تلتقط {ar(round(S_B * 100, 1))}٪ فقط — وساعةُ الحركة صارت خارجها', RED)
    svg += sm(Wd, H, "ساعةٌ واحدةٌ من الفرق أسقطت أكثرَ من نصف مدى اليوم من نافذتك")
    return svg + badge(Wd, "مثال تخطيطي", True) + "</svg>"


def s_all(r=None, Wd=880, H=250):
    """٥ · السلسلة كاملة — مرجعُ كلِّ رقمٍ في الوحدة."""
    assert len(WS) == S_N, len(WS)
    svg, x, y, slot = _gs(Wd, H)
    svg += _hourlines(x, y, slot, H)
    svg += RC._title(Wd, rt("السلسلة كاملة"))
    svg += why(Wd, H, f'{ar(8)} ساعات · ساعةُ الحركة {xr(S_RB)} الوسيط · '
                      f'النافذة {ar(round(S_A * 100, 1))}٪ ثم {ar(round(S_B * 100, 1))}٪', INK)
    svg += sm(Wd, H, "ولا سعرَ مكتوبٌ هنا، فالرسم تخطيطي لا طبعةُ سوق")
    return svg + badge(Wd, "مثال تخطيطي", True) + "</svg>"


# ═════════════════════════════════════════════════════════════════
# ٥ · «تركيب» — القاعدةُ التي تُحسب عليها النسبة (مالية · مثال تخطيطي)
#     سلسلتان: نسبةٌ واحدة (٦٪) وثمانُ موجات — والفرقُ في القاعدة وحدها
# ═════════════════════════════════════════════════════════════════
# البذرةُ الأولى (28092) أعطت سلّماً لا سوقاً: أربعُ شمعاتٍ للموجة وضجيجٌ
# ٠٫٣٤ فصارت الشموع كلُّها صاعدةً متقاربةَ الأجسام بلا فتائل — وهو ما يمنعه
# §4 صراحةً، والأسوأ أنّ «الموجات تكبر» لا تُرى في سلّمٍ منتظم (رُصد
# بالفحص البصري). فخمسُ شمعاتٍ للموجة وارتدادٌ ٤٥٪ وضجيجٌ ٠٫٥٥ وفتيلٌ
# ٠٫٩٥، والبذرةُ تُختار بشرطَي الواقعية: ستَّ عشرةَ شمعةً هابطة من إحدى
# وأربعين، وتشتّتُ المدى ٠٫٧٦ من وسطه.
T_SEED = 52098
T_LEGS, T_STEP, T_BASE, T_PER = 8, 0.06, 100.0, 5


def _tanch(compound):
    a, p = [(0, T_BASE)], T_BASE
    for k in range(T_LEGS):
        top = p + (p if compound else T_BASE) * T_STEP
        a.append((T_PER * k + 3, top))
        a.append((T_PER * k + 5, top - (top - p) * 0.45))   # ارتدادٌ بين الموجتين
        p = top
    return a


T_ANCH_A, T_ANCH_B = _tanch(True), _tanch(False)
T_N = T_LEGS * T_PER + 1
WTA = gen(T_ANCH_A, T_N, T_SEED, wick=0.95, bn=0.55)
WTB = gen(T_ANCH_B, T_N, T_SEED, wick=0.95, bn=0.55)
RT_ = {"sym": "SCHEMATIC-T", "slug": "مثال تخطيطي — تركيب", "w": WTA}
# بصمةُ الوحدة تجمع مرسَيَي السلسلتين: الوحدة سلسلتان لا واحدة، فبصمةٌ
# لإحداهما تترك الأخرى حرّةً في السجل فتعود في تشغيلةٍ قادمة كأنها جديدة.
T_ANCH = T_ANCH_A + T_ANCH_B


def _tamps(W):
    """سَعةُ كلِّ موجة مقيسةً على الشموع — لا على المرساة."""
    return [max(c["h"] for c in W[T_PER * k + 1:T_PER * k + 4])
            - min(c["l"] for c in W[max(0, T_PER * k - 1):T_PER * k + 2])
            for k in range(T_LEGS)]


T_AMP_A, T_AMP_B = _tamps(WTA), _tamps(WTB)
T_GROW = T_AMP_A[-1] / T_AMP_A[0]
T_FLAT = T_AMP_B[-1] / T_AMP_B[0]
T_END_A = max(a[1] for a in T_ANCH_A)
T_END_B = max(a[1] for a in T_ANCH_B)
T_GAIN = (T_END_A - T_BASE) / (T_END_B - T_BASE) - 1

import statistics as _st
_T_DN = sum(1 for c in WTA if c["c"] < c["o"])
_T_RG = [c["h"] - c["l"] for c in WTA]
_T_VAR = _st.pstdev(_T_RG) / _st.mean(_T_RG)

assert T_GROW >= 1.30, T_GROW
assert 0.90 <= T_FLAT <= 1.10, T_FLAT
assert T_GAIN >= 0.20, T_GAIN
# واقعيةُ السلسلة شرطٌ يُقاس لا ذوق (§4): سلّمٌ صاعدٌ منتظم ليس سوقاً
assert _T_DN >= T_N * 0.28, f"الهابطة {_T_DN} من {T_N} — سلّمٌ لا سوق"
assert _T_VAR >= 0.45, f"تشتّتُ المدى {_T_VAR:.2f} — أجسامٌ متقاربة" 


def _gta(Wd, H):
    return frame(WTA, Wd, H, pad=0.10, pb=66)


def _gtb(Wd, H):
    return frame(WTB, Wd, H, pad=0.10, pb=66)


def _leglines(x, H, col=GREY):
    s = ""
    for k in range(1, T_LEGS):
        xx = x(T_PER * k)
        s += (f'<line x1="{xx:.1f}" y1="58" x2="{xx:.1f}" y2="{H - 50:.0f}" '
              f'stroke="{col}" stroke-width="1" stroke-dasharray="3 5" opacity=".5"/>')
    return s


def t_legs(r=None, Wd=880, H=250):
    """١ · ثمانُ موجات ونسبةٌ واحدة."""
    svg, x, y, slot = _gta(Wd, H)
    svg += _leglines(x, H)
    svg += RC._title(Wd, rt("ثمانُ موجات — ونسبةٌ واحدة"))
    svg += why(Wd, H, f'{ar(T_LEGS)} موجات، كلُّ موجةٍ {ar(6)}٪ — لا تتغيّر النسبةُ ولا العدد', INK)
    svg += sm(Wd, H, "والخطوطُ المنقّطة حدودُ الموجات — لا مستوياتِ سعر")
    return svg + badge(Wd, "مثال تخطيطي", True) + "</svg>"


def t_grow(r=None, Wd=880, H=250):
    """٢ · حين تبقى النسبةُ على قاعدةٍ تكبر — تكبر الموجة."""
    svg, x, y, slot = _gta(Wd, H)
    svg += _leglines(x, H)
    svg += band(x(0) - slot * .5, x(T_PER) + slot * .5,
                y(max(c["h"] for c in WTA[1:T_PER])),
                y(min(c["l"] for c in WTA[:2])), GREY, 0.16)
    svg += band(x(T_PER * (T_LEGS - 1)) - slot * .5, x(T_N - 1) + slot * .5,
                y(max(c["h"] for c in WTA[T_PER * (T_LEGS - 1) + 1:])),
                y(min(c["l"] for c in WTA[T_PER * (T_LEGS - 1) - 1:T_PER * (T_LEGS - 1) + 2])),
                TEAL, 0.20)
    svg += RC._title(Wd, rt("الموجةُ الثامنة أطولُ من الأولى"))
    svg += why(Wd, H, f'سَعةُ الثامنة {xr(T_GROW)} سَعةَ الأولى — مقيسةً على الشموع لا حساباً', TEAL_D)
    svg += sm(Wd, H, "نفسُ النسبة، لكن القاعدةَ كبرت — فكبر ما تعطيه النسبة")
    return svg + badge(Wd, "مثال تخطيطي", True) + "</svg>"


def t_flat(r=None, Wd=880, H=250):
    """٣ · وحين تُسحب فتعود القاعدة — تتساوى الموجات."""
    svg, x, y, slot = _gtb(Wd, H)
    svg += _leglines(x, H)
    svg += band(x(0) - slot * .5, x(T_PER) + slot * .5,
                y(max(c["h"] for c in WTB[1:T_PER])),
                y(min(c["l"] for c in WTB[:2])), GREY, 0.16)
    svg += band(x(T_PER * (T_LEGS - 1)) - slot * .5, x(T_N - 1) + slot * .5,
                y(max(c["h"] for c in WTB[T_PER * (T_LEGS - 1) + 1:])),
                y(min(c["l"] for c in WTB[T_PER * (T_LEGS - 1) - 1:T_PER * (T_LEGS - 1) + 2])),
                GREY, 0.18)
    svg += RC._title(Wd, rt("وهنا الثامنةُ كالأولى تماماً"))
    svg += why(Wd, H, f'سَعةُ الثامنة {xr(T_FLAT)} سَعةَ الأولى — الموجاتُ متساويةٌ لأن '
                      f'القاعدةَ تعود كما كانت', RED)
    svg += sm(Wd, H, "نفسُ النسبة ونفسُ العدد — ولا شيءَ يكبر")
    return svg + badge(Wd, "مثال تخطيطي", True) + "</svg>"


def t_gap(r=None, Wd=880, H=250):
    """٤ · الفرقُ بعد ثمانِ موجاتٍ فقط."""
    svg, x, y, slot = _gta(Wd, H)
    svg += _leglines(x, H)
    svg += band(x(T_PER * (T_LEGS - 1)) - slot * .5, x(T_N - 1) + slot * .5,
                y(max(c["h"] for c in WTA[T_PER * (T_LEGS - 1) + 1:])),
                y(min(c["l"] for c in WTA[T_PER * (T_LEGS - 1) - 1:])), TEAL, 0.20)
    svg += RC._title(Wd, rt("بعد ثمانِ موجاتٍ فقط"))
    svg += why(Wd, H, f'{ar(f"{T_END_A - T_BASE:.2f}")} وحدةً ربحاً مقابل '
                      f'{ar(f"{T_END_B - T_BASE:.2f}")} — أي '
                      f'{ar(round(T_GAIN * 100, 1))}٪ إضافيةً بنفسِ النسبة', TEAL_D)
    svg += sm(Wd, H, "والحسابُ على افتراضٍ معلَن: ثمانُ موجاتٍ رابحةٍ متّصلة، وهذا لا يقع في سوق")
    return svg + badge(Wd, "مثال تخطيطي", True) + "</svg>"


def t_all(r=None, Wd=880, H=250):
    """٥ · السلسلة كاملة — مرجعُ كلِّ رقمٍ في الوحدة."""
    assert len(WTA) == T_N and len(WTB) == T_N, (len(WTA), len(WTB))
    svg, x, y, slot = _gta(Wd, H)
    svg += _leglines(x, H)
    svg += RC._title(Wd, rt("السلسلة كاملة"))
    svg += why(Wd, H, f'{ar(T_LEGS)} موجات × {ar(6)}٪ · الثامنة {xr(T_GROW)} الأولى · '
                      f'والفرقُ {ar(round(T_GAIN * 100, 1))}٪', INK)
    svg += sm(Wd, H, "والقاعدةُ وحدةُ حسابٍ معلنة تبدأ من مئة — لا سعرَ سوقٍ ولا عملة")
    return svg + badge(Wd, "مثال تخطيطي", True) + "</svg>"


# ═════════════════════════════════════════════════════════════════
SETS = {"habs": [b_range, b_inside, b_break, b_ext, b_all],
        "hissa": [h_leg, h_one, h_rest, h_ratio, h_all],
        "loum": [l_level, l_stop, l_sweep, l_back, l_all],
        "sayfi": [s_hours, s_big, s_winA, s_winB, s_all],
        "tarkib": [t_legs, t_grow, t_flat, t_gap, t_all]}
WINS = {"habs": RB_, "hissa": RH, "loum": RL, "sayfi": RS, "tarkib": RT_}
REAL = {"habs": B_WIN, "hissa": H_WIN}
SYN = {"loum": (L_SEED, L_ANCH), "sayfi": (S_SEED, S_ANCH),
       "tarkib": (T_SEED, T_ANCH)}


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
