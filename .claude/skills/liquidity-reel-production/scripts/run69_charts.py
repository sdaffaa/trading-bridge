# -*- coding: utf-8 -*-
"""جارتات تشغيلة ٦٩ — وحدتان على سوقٍ حقيقي وثلاثٌ تخطيطية.

    ترند   ← النافذة ٧٠ · الكاردانو/دولار · ساعة · 2025-10-03 · فئة `chan`
    حصة    ← النافذة ٧١ · الإيثيريوم/دولار · ١٥د · 2026-07-31 · فئة `sweep`

وهما آخرُ نافذتين حرّتين في المخزون، وقد جُلبتا في تشغيلة ٦٨ بالمسح
الموسَّع. والثلاث الباقية بقاعدة §11 البديلة: شارة «مثال تخطيطي» على كل
لوحة · كلُّ ادّعاءٍ مقيسٌ بـ`assert` · أعدادٌ ونِسبٌ لا أسعار.

    python3 run69_charts.py
"""
import statistics as st

from reel_build import INK, TEAL, TEAL_D, RED, gen
from run15_charts import hl, badge, frame
import run31_charts as RC
from run58_charts import ar, rt, sm, band, mark
from run59_charts import spanx, vspan, xr


def _real(W, n):
    """حارسُ §4: تشتّتُ المدى وعددُ الهابطة ونسبةُ الجسم وسقفُ أطولِ شمعة."""
    R = [c["h"] - c["l"] for c in W]
    B = [abs(c["c"] - c["o"]) for c in W]
    dn = sum(1 for c in W if c["c"] < c["o"])
    med, bod = st.median(R), st.median(B)
    assert st.pstdev(R) / st.mean(R) >= 0.45, st.pstdev(R) / st.mean(R)
    assert dn >= n * 0.30, f"الهابطة {dn} من {n} — سلّمٌ لا سوق"
    assert 1.9 <= med / bod <= 3.1, f"وسيط المدى {med/bod:.2f} وسيطَ الجسم"
    assert max(R) / med <= 3.6, f"أطول شمعة {max(R)/med:.2f}× — تسحق اللوحة"


def dl(x1, y1, x2, y2, col=INK, w=1.8, dash=None):
    """خطٌّ مائل — `hl` أفقيٌّ وحده، وخطُّ الاتجاه لا يكون أفقياً."""
    d = f' stroke-dasharray="{dash}"' if dash else ''
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{col}" stroke-width="{w}" stroke-linecap="round"{d}/>')


def dot(x, y, col=INK, r=5.0):
    return (f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="#F2EEE7" '
            f'stroke="{col}" stroke-width="2"/>')


# ═════════════════════════════════════════════════════════════════
# ١ · «ترند» — من الفتائل أم الأجسام؟ (فنية · ريل · سوقٌ حقيقي)
#     الكاردانو/دولار · ساعة · 2025-10-03 · ٤٢ شمعة
# ═════════════════════════════════════════════════════════════════
D_WIN = 70
RD = RC.win(D_WIN)
WD = RD["w"]
D_N = len(WD)
D_A, D_B = RD["chi"]                       # طرفا حدّ القناة العلوي
D_LA, D_LB = RD["clo"]                     # طرفا الحدّ السفلي
D_BK, D_IR = RD["bk"], RD["ir"]
D_MED = st.median(c["h"] - c["l"] for c in WD)
D_T2, D_T3 = 0.20 * D_MED, 0.30 * D_MED


def _ln(i1, i2, f):
    y1, y2 = f(WD[i1]), f(WD[i2])
    m = (y2 - y1) / (i2 - i1)
    return lambda i: y1 + m * (i - i1)


_HI = lambda c: c["h"]                                       # noqa: E731
_BD = lambda c: max(c["o"], c["c"])                          # noqa: E731
D_WICK = _ln(D_A, D_B, _HI)
D_BODY = _ln(D_A, D_B, _BD)
D_LOW = _ln(D_LA, D_LB, lambda c: c["l"])


def _tch(ln, f, tol):
    return [i for i in range(D_A, D_B + 1) if abs(f(WD[i]) - ln(i)) <= tol]


def _vio(ln, f, tol):
    return [i for i in range(D_A, D_B + 1) if f(WD[i]) - ln(i) > tol]


D_TW = _tch(D_WICK, _HI, D_T2)             # لمساتُ خطّ الفتائل
D_VW = _vio(D_WICK, _HI, D_T2)             # تجاوزاتُه
D_TB = _tch(D_BODY, _BD, D_T2)             # لمساتُ خطّ الأجسام
D_VB = _vio(D_BODY, _BD, D_T2)             # تجاوزاتُه
D_TB3 = _tch(D_BODY, _BD, D_T3)            # لمساتُه بعد تليين السماح
D_VB3 = _vio(D_BODY, _BD, D_T3)

assert len(D_TW) == 9, len(D_TW)
assert not D_VW, D_VW
assert not _vio(D_WICK, _HI, D_T3), "الفتائل تجاوزت عند السماح الأوسع"
assert len(D_TB) == 6, len(D_TB)
assert len(D_VB) == 1, D_VB
assert len(D_TB3) == 8 and not D_VB3, (D_TB3, D_VB3)
# امتدادُ الخطّ بعد طرفه: أولُ إغلاقٍ فوقه هو شمعةُ الدخول نفسها — وهذا هو
# الفرقُ العملي بين الخطّين، لا مجرّد عدّ لمسات.
D_BRK = next(i for i in range(D_B + 1, D_N) if WD[i]["c"] - D_WICK(i) > D_T2)
D_DIFF = (D_WICK(D_A) - D_BODY(D_A)) / D_MED
assert D_BRK == D_IR, (D_BRK, D_IR)
assert D_DIFF <= 0.30, D_DIFF


def _gd(Wd, H):
    return frame(WD, Wd, H, pad=0.08, pb=64)


def _chan(svg, x, y, slot, top=True, bot=True, col=INK, w=1.8):
    if top:
        svg += dl(x(D_A) - slot * .5, y(D_WICK(D_A - .5)),
                  x(D_B) + slot * .5, y(D_WICK(D_B + .5)), col, w)
    if bot:
        svg += dl(x(D_LA) - slot * .5, y(D_LOW(D_LA - .5)),
                  x(D_LB) + slot * .5, y(D_LOW(D_LB + .5)), INK, 1.5, "6 6")
    return svg


def d_chan(r=None, Wd=880, H=250):
    """١ · القناة الهابطة: حدّان بين الشمعة ١٧ والشمعة ٣١."""
    svg, x, y, slot = _gd(Wd, H)
    svg = _chan(svg, x, y, slot)
    svg += spanx(x(D_A) - slot * .5, x(D_B) + slot * .5,
                 y(max(c["h"] for c in WD[D_A:D_B + 1])),
                 rt(f'{ar(D_B - D_A + 1)} شمعة'), INK)
    svg += RC._title(Wd, rt("قناةٌ هابطة — والسؤال وين يُرسم حدّها"))
    svg += RC._why(Wd, H, f'{ar(D_B - D_A + 1)} شمعة بين طرفَي الحدّ، '
                          f'ووسيطُ مدى الشمعة {D_MED:.4f}', INK)
    svg += sm(Wd, H, "من فوق خطٌّ واحد — بس على شنو نمرّه؟")
    return svg + "</svg>"


def d_wick(r=None, Wd=880, H=250):
    """٢ · خطُّ الفتائل: تسعُ لمساتٍ وصفرُ تجاوز."""
    svg, x, y, slot = _gd(Wd, H)
    svg = _chan(svg, x, y, slot, bot=False, col=TEAL_D, w=2.2)
    for i in D_TW:
        svg += dot(x(i), y(WD[i]["h"]), TEAL_D)
    svg += RC._title(Wd, rt("خطُّ الفتائل: تسع لمسات وولا تجاوز"))
    svg += RC._why(Wd, H, f'{ar(len(D_TW))} لمسات وصفرُ إغلاقٍ فوقه — '
                          f'وثابتٌ على سماحَين مختلفين', TEAL_D)
    svg += sm(Wd, H, "اللمسة تُعدّ بالسماح، ما تُشاف بالنظر")
    return svg + "</svg>"


def d_body(r=None, Wd=880, H=250):
    """٣ · خطُّ الأجسام: ستُّ لمساتٍ وتجاوزٌ واحد."""
    svg, x, y, slot = _gd(Wd, H)
    svg += dl(x(D_A) - slot * .5, y(D_BODY(D_A - .5)),
              x(D_B) + slot * .5, y(D_BODY(D_B + .5)), INK, 2.2)
    for i in D_TB:
        svg += dot(x(i), y(_BD(WD[i])), INK)
    for i in D_VB:
        svg += mark(x(i), slot, y(WD[i]["h"]), y(WD[i]["l"]), RED, 0.24)
    svg += RC._title(Wd, rt("وخطُّ الأجسام يطلع عليه واحد"))
    svg += RC._why(Wd, H, f'{ar(len(D_TB))} لمسات ومعها تجاوزٌ واحد — '
                          f'الشمعة {ar(D_VB[0])} خرجت فوقه', RED)
    svg += sm(Wd, H, "ولا يستوي بلا تجاوز إلا لو وسّعت السماح")
    return svg + "</svg>"


def d_cmp(r=None, Wd=880, H=250):
    """٤ · الخطّان معاً: الفرق بينهما مسافةُ فتيل."""
    svg, x, y, slot = _gd(Wd, H)
    svg = _chan(svg, x, y, slot, bot=False, col=TEAL_D, w=2.2)
    svg += dl(x(D_A) - slot * .5, y(D_BODY(D_A - .5)),
              x(D_B) + slot * .5, y(D_BODY(D_B + .5)), INK, 1.8, "7 6")
    svg += vspan(x(D_B) + slot * 2.2, y(D_WICK(D_B)), y(D_BODY(D_B)),
                 rt(f'{xr(D_DIFF)} الوسيط'), INK, 16, H)
    svg += RC._title(Wd, rt("والفرق بينهما خُمسُ شمعة"))
    svg += RC._why(Wd, H, f'المسافة بين الخطّين {xr(D_DIFF)} وسيطَ المدى — '
                          f'وتقلب العدّ من {ar(len(D_TW))} بلا تجاوز إلى '
                          f'{ar(len(D_TB))} ومعها واحد', INK)
    svg += sm(Wd, H, "على الأجسام تدخل بدري، وعلى الفتائل تنتظر")
    return svg + "</svg>"


def d_all(r=None, Wd=880, H=250):
    """٥ · الخلاصة: الخطُّ الذي يُحترم هو الذي يُقاس."""
    svg, x, y, slot = _gd(Wd, H)
    svg = _chan(svg, x, y, slot, bot=False, col=TEAL_D, w=2.2)
    for i in D_TW:
        svg += dot(x(i), y(WD[i]["h"]), TEAL_D, 4.4)
    svg += dl(x(D_B) + slot * .5, y(D_WICK(D_B + .5)),
              x(D_BRK) + slot * .5, y(D_WICK(D_BRK + .5)), TEAL_D, 1.6, "6 5")
    svg += mark(x(D_BRK), slot, y(WD[D_BRK]["h"]), y(WD[D_BRK]["l"]), TEAL, 0.24)
    svg += RC._title(Wd, rt("وأول إغلاقٍ فوقه كان شمعة الدخول"))
    svg += RC._why(Wd, H, f'{ar(len(D_TW))} لمسات وصفرُ تجاوز، وأولُ إغلاقٍ '
                          f'فوق امتداده الشمعة {ar(D_BRK)} — شمعةُ الدخول نفسها', INK)
    svg += sm(Wd, H, "الخطُّ اللي ما ينكسر قبل وقته يقول لك وقته")
    return svg + "</svg>"


# ═════════════════════════════════════════════════════════════════
# ٢ · «حصة» — حركةٌ صنعتها شمعة (فنية · ريل · سوقٌ حقيقي)
#     الإيثيريوم/دولار · ١٥ دقيقة · 2026-07-31 · ٣٤ شمعة
# ═════════════════════════════════════════════════════════════════
S_WIN = 71
RS = RC.win(S_WIN)
WS = RS["w"]
S_N = len(WS)
S_IR, S_IOB = RS["ir"], RS["iob"]
S_LO = min(range(S_IOB, S_IR + 1), key=lambda k: WS[k]["l"])
S_TOP = max(range(S_IR, S_N), key=lambda k: WS[k]["h"])
S_MOVE = WS[S_TOP]["h"] - WS[S_LO]["l"]
S_RNG = [(i, WS[i]["h"] - WS[i]["l"]) for i in range(S_LO, S_TOP + 1)]
S_BIG = max(S_RNG, key=lambda p: p[1])
S_SHARE = S_BIG[1] / S_MOVE
S_GROSS = sum(v for _, v in S_RNG)
S_MED = st.median(c["h"] - c["l"] for c in WS)
S_BARS = S_TOP - S_LO + 1
S_ENT = WS[S_IR]["c"]
_srng = (max(x["h"] for x in WS[:S_IR + 1]) - min(x["l"] for x in WS[:S_IR + 1]))
S_STP = WS[S_IOB]["l"] - _srng * 0.006
S_TGT = S_ENT + 2 * (S_ENT - S_STP)
S_HIT = next(k for k in range(S_IR + 1, S_N) if WS[k]["h"] >= S_TGT)

assert 0.60 <= S_SHARE <= 0.72, S_SHARE
assert S_BARS == 16, S_BARS
assert S_GROSS / S_MOVE >= 3.5, S_GROSS / S_MOVE
assert S_BIG[1] / S_MED >= 2.4, S_BIG[1] / S_MED


def _gs(Wd, H):
    return frame(WS, Wd, H, pad=0.08, pb=64)


def s_move(r=None, Wd=880, H=250):
    """١ · الحركة كاملة: من القاع إلى القمّة."""
    svg, x, y, slot = _gs(Wd, H)
    svg += hl(x(S_LO) - slot * .5, x(S_N - 1) + slot * .5, y(WS[S_LO]["l"]), INK, 1.6)
    svg += hl(x(S_LO) - slot * .5, x(S_N - 1) + slot * .5, y(WS[S_TOP]["h"]), INK, 1.6)
    # الوسمُ يسار الطرف: `S_TOP` قريبٌ من حافّة اللوحة فيُقصّ يمينها
    svg += vspan(x(S_TOP) - slot * 2.6, y(WS[S_TOP]["h"]), y(WS[S_LO]["l"]),
                 rt(f'المدى {S_MOVE:.2f}'), INK, 16, H)
    svg += RC._title(Wd, rt("حركةٌ كاملة على ستّ عشرة شمعة"))
    svg += RC._why(Wd, H, f'من القاع {WS[S_LO]["l"]:.2f} إلى القمّة '
                          f'{WS[S_TOP]["h"]:.2f} — المدى {S_MOVE:.2f}', INK)
    svg += sm(Wd, H, "ستّ عشرة شمعة تعبت — بس مو كلهن اشتغلن")
    return svg + "</svg>"


def s_big(r=None, Wd=880, H=250):
    """٢ · شمعةٌ واحدة صنعت ثلثَي الحركة."""
    svg, x, y, slot = _gs(Wd, H)
    svg += hl(x(S_LO) - slot * .5, x(S_N - 1) + slot * .5, y(WS[S_TOP]["h"]), INK, 1.4)
    svg += mark(x(S_BIG[0]), slot, y(WS[S_BIG[0]]["h"]), y(WS[S_BIG[0]]["l"]), TEAL, 0.26)
    svg += vspan(x(S_BIG[0]) - slot * 3.0, y(WS[S_BIG[0]]["h"]), y(WS[S_BIG[0]]["l"]),
                 rt(f'{ar(round(S_SHARE * 100))}٪ من الحركة'), TEAL_D, 16, H)
    svg += RC._title(Wd, rt("وشمعةٌ وحدة شالت ثلثينها"))
    svg += RC._why(Wd, H, f'مداها {S_BIG[1]:.2f} من {S_MOVE:.2f} — '
                          f'{ar(round(S_SHARE * 100))}٪، و{xr(S_BIG[1]/S_MED)} وسيطَ المدى', TEAL_D)
    svg += sm(Wd, H, "لو فاتتك هذي، فاتك ثلثا الحركة كلها")
    return svg + "</svg>"


def s_rest(r=None, Wd=880, H=250):
    """٣ · الخمس عشرة الباقية: الثلث الباقي موزَّعاً."""
    svg, x, y, slot = _gs(Wd, H)
    for i, _ in S_RNG:
        if i != S_BIG[0]:
            svg += mark(x(i), slot, y(WS[i]["h"]), y(WS[i]["l"]), INK, 0.12)
    svg += RC._title(Wd, rt("وخمس عشرة شمعة تقاسمن الباقي"))
    svg += RC._why(Wd, H, f'{ar(S_BARS - 1)} شمعة على '
                          f'{S_MOVE - S_BIG[1]:.2f} — نصيبُ الواحدة أقلُّ من '
                          f'ثلث وسيط المدى', INK)
    svg += sm(Wd, H, "وكلهن على الشاشة كانن يبينن شغل")
    return svg + "</svg>"


def s_net(r=None, Wd=880, H=250):
    """٤ · المجموع مقابل الصافي: الحركة تأكل نفسها."""
    svg, x, y, slot = _gs(Wd, H)
    svg += band(x(S_LO) - slot * .5, x(S_TOP) + slot * .5,
                y(WS[S_TOP]["h"]), y(WS[S_LO]["l"]), TEAL_D, 0.12)
    svg += mark(x(S_BIG[0]), slot, y(WS[S_BIG[0]]["h"]), y(WS[S_BIG[0]]["l"]), TEAL, 0.22)
    svg += RC._title(Wd, rt("مجموعُ المديات أربعةُ أضعاف الصافي"))
    svg += RC._why(Wd, H, f'مجموعُ مديات الستّ عشرة {S_GROSS:.2f} وصافي '
                          f'الحركة {S_MOVE:.2f} — الباقي أكل بعضه', INK)
    svg += sm(Wd, H, "الحركة مو مجموع تعب الشمعات، هي الفرق بين طرفين")
    return svg + "</svg>"


def s_all(r=None, Wd=880, H=250):
    """٥ · الخلاصة: ابحث عن الشمعة لا عن الساعة."""
    svg, x, y, slot = _gs(Wd, H)
    svg += hl(x(0) - slot * .5, x(S_N - 1) + slot * .5, y(S_ENT), INK, 1.8)
    svg += hl(x(0) - slot * .5, x(S_N - 1) + slot * .5, y(S_TGT), TEAL_D, 1.6, "5 5")
    svg += mark(x(S_BIG[0]), slot, y(WS[S_BIG[0]]["h"]), y(WS[S_BIG[0]]["l"]), TEAL, 0.24)
    svg += RC._title(Wd, rt("والشمعة نفسها هي اللي بلّغت الهدف"))
    svg += RC._why(Wd, H, f'الدخول {S_ENT:.2f} والهدف {S_TGT:.2f} — '
                          f'بلغه السعر بالشمعة {ar(S_HIT - S_IR)} بعد الدخول', INK)
    svg += sm(Wd, H, "فاللي يطلع من الصفقة قبلها يطلع قبل شغلها")
    return svg + "</svg>"


# ═════════════════════════════════════════════════════════════════
# ٣ · «تشابه» — ثمانٍ تشبه واثنتان تستوفي (نفسية · كاروسيل · تخطيطي)
# ═════════════════════════════════════════════════════════════════
P_SEED = 1810
P_ANCH = [(0, 100.0), (8, 101.4), (15, 100.2), (23, 99.3), (31, 100.6), (43, 102.2)]
P_N = 44
WP = gen(P_ANCH, P_N, P_SEED, wick=0.5, bn=0.5)
RP = {"sym": "SCHEMATIC-P", "slug": "مثال تخطيطي — تشابه", "w": WP}
P_MED = st.median(c["h"] - c["l"] for c in WP)
P_MB = st.median(abs(c["c"] - c["o"]) for c in WP)
P_LOOK = [k for k in range(10, P_N - 6)
          if WP[k]["c"] > max(c["c"] for c in WP[k - 8:k])]
P_SET = []
for _k in P_LOOK:
    _lvl = max(c["h"] for c in WP[_k - 12:_k - 1])
    if not (WP[_k]["c"] > _lvl and WP[_k - 1]["c"] <= _lvl):
        continue
    if abs(WP[_k]["c"] - WP[_k]["o"]) < 1.3 * P_MB:
        continue
    _pb = [j for j in range(_k + 1, min(_k + 9, P_N)) if WP[j]["l"] <= _lvl]
    if not _pb or WP[_pb[0]]["l"] < _lvl - 1.3 * P_MED:
        continue
    if P_SET and _k - P_SET[-1][0] < 6:
        continue
    P_SET.append((_k, _lvl, _pb[0], abs(WP[_k]["c"] - WP[_k]["o"]) / P_MB))
P_GHOST = len(P_LOOK) - len(P_SET)

_real(WP, P_N)
assert len(P_LOOK) == 8, len(P_LOOK)
assert len(P_SET) == 2, len(P_SET)
assert P_GHOST == 6, P_GHOST


def _gp(Wd, H):
    return frame(WP, Wd, H, pad=0.10, pb=66)


def p_look(r=None, Wd=880, H=250):
    """١ · ثمانيةُ مواضعَ تشبه النموذج بالنظر."""
    svg, x, y, slot = _gp(Wd, H)
    for i in P_LOOK:
        svg += mark(x(i), slot, y(WP[i]["h"]), y(WP[i]["l"]), TEAL_D, 0.18)
    svg += RC._title(Wd, rt("ثمانية مواضع تشبهه بالنظر"))
    svg += RC._why(Wd, H, f'{ar(len(P_LOOK))} إغلاقات فوق أعلى إغلاقات '
                          f'آخر {ar(8)} شمعات — كلها تبين معاك كسراً', TEAL_D)
    svg += sm(Wd, H, "وهذي بالضبط اللحظة اللي تقول فيها «شفته مرّة ثانية»")
    return svg + badge(Wd, "مثال تخطيطي", True) + "</svg>"


def p_cond(r=None, Wd=880, H=250):
    """٢ · الشروط الثلاثة مكتوبةً على الحالة الأولى."""
    svg, x, y, slot = _gp(Wd, H)
    k, lvl, j, b = P_SET[0]
    svg += hl(x(max(0, k - 13)) - slot * .5, x(min(P_N - 1, j + 3)) + slot * .5,
              y(lvl), INK, 1.6)
    svg += mark(x(k), slot, y(WP[k]["h"]), y(WP[k]["l"]), TEAL, 0.24)
    svg += mark(x(j), slot, y(WP[j]["h"]), y(WP[j]["l"]), TEAL_D, 0.20)
    svg += vspan(x(j) + slot * 2.2, y(lvl), y(lvl - 1.3 * P_MED),
                 rt("أعمقُ مسموح"), RED, 16, H)
    svg += RC._title(Wd, rt("والشروط الثلاثة تنكتب قبل العدّ"))
    svg += RC._why(Wd, H, f'إغلاقٌ فوق أعلى قمّةٍ في {ar(12)} شمعة، وجسمٌ '
                          f'{xr(1.3)} وسيطَ الأجسام أو أكثر، ورجعةٌ تثبت', TEAL_D)
    svg += sm(Wd, H, "ثلاثة أرقام — مو ثلاثة انطباعات")
    return svg + badge(Wd, "مثال تخطيطي", True) + "</svg>"


def p_strict(r=None, Wd=880, H=250):
    """٣ · اثنتان فقط تجتازان."""
    svg, x, y, slot = _gp(Wd, H)
    for k, lvl, j, b in P_SET:
        svg += hl(x(max(0, k - 13)) - slot * .5, x(min(P_N - 1, j + 3)) + slot * .5,
                  y(lvl), INK, 1.5)
        svg += mark(x(k), slot, y(WP[k]["h"]), y(WP[k]["l"]), TEAL, 0.24)
    svg += RC._title(Wd, rt("واثنتان فقط تجتاز الثلاثة"))
    svg += RC._why(Wd, H, f'جسماهما {xr(P_SET[0][3])} و{xr(P_SET[1][3])} '
                          f'وسيطَ الأجسام — والبقيّة تسقط على شرطٍ منها', TEAL_D)
    svg += sm(Wd, H, "العتبة ما تعرف حماسك، تعرف رقمك")
    return svg + badge(Wd, "مثال تخطيطي", True) + "</svg>"


def p_gap(r=None, Wd=880, H=250):
    """٤ · ستُّ فرصٍ موهومة."""
    svg, x, y, slot = _gp(Wd, H)
    _ghost = [i for i in P_LOOK if i not in [s[0] for s in P_SET]]
    for i in _ghost:
        svg += mark(x(i), slot, y(WP[i]["h"]), y(WP[i]["l"]), RED, 0.20)
    svg += RC._title(Wd, rt("والفرق ستُّ فرصٍ موهومة"))
    svg += RC._why(Wd, H, f'{ar(P_GHOST)} مواضع أقنعتك أنها النموذج وما هي '
                          f'هو — وكلُّ وحدةٍ منهن كانت ممكن تصير صفقة', RED)
    svg += sm(Wd, H, "ست دخلات بشهر، كلها لأنك «شفت» النموذج")
    return svg + badge(Wd, "مثال تخطيطي", True) + "</svg>"


def p_all(r=None, Wd=880, H=250):
    """٥ · الخلاصة: عدّ بالعتبة لا بالعين."""
    svg, x, y, slot = _gp(Wd, H)
    for i in P_LOOK:
        col = TEAL if i in [s[0] for s in P_SET] else RED
        svg += mark(x(i), slot, y(WP[i]["h"]), y(WP[i]["l"]), col, 0.20)
    svg += RC._title(Wd, rt("ثمانٍ تشبه — واثنتان تستوفي"))
    svg += RC._why(Wd, H, f'{ar(len(P_LOOK))} بالنظر و{ar(len(P_SET))} '
                          f'بالعتبة في {ar(P_N)} شمعة', INK)
    svg += sm(Wd, H, "اكتب شروطك على ورقة، وعُدّ عليها لا على شعورك")
    return svg + badge(Wd, "مثال تخطيطي", True) + "</svg>"


# ═════════════════════════════════════════════════════════════════
# ٤ · «تشكّل» — الشمعة الجارية أربعةُ أرقام (أساسية · كاروسيل · تخطيطي)
# ═════════════════════════════════════════════════════════════════
F_SEED = 528
F_ANCH = [(0, 100.0), (9, 101.2), (18, 100.0), (27, 101.6), (35, 100.8)]
F_N = 36
WF = gen(F_ANCH, F_N, F_SEED, wick=0.6, bn=0.5)
RF = {"sym": "SCHEMATIC-F", "slug": "مثال تخطيطي — تشكّل", "w": WF}
F_K, F_DONE = 12, 8                      # شمعةُ الفريم الأعلى، والمُغلَق منها
F_S = F_N - F_K                          # بداية الشمعة الجارية
F_SEG = WF[F_S:F_S + F_DONE]
F_HI = max(c["h"] for c in F_SEG)
F_LO = min(c["l"] for c in F_SEG)
F_PX = F_SEG[-1]["c"]
F_POS = (F_PX - F_LO) / (F_HI - F_LO)
F_LEFT = F_K - F_DONE
F_MED = st.median(c["h"] - c["l"] for c in WF)
F_SIZE = (F_HI - F_LO) / F_MED
F_FULL = [(i, i + F_K) for i in range(0, F_S, F_K)]

_real(WF, F_N)
assert 0.04 <= F_POS <= 0.14, F_POS
assert F_LEFT == 4, F_LEFT
assert F_SIZE >= 3.0, F_SIZE
assert len(F_FULL) == 2, F_FULL


def _gf(Wd, H):
    return frame(WF, Wd, H, pad=0.10, pb=66)


def _hbox(svg, x, y, slot, a, b, col=INK, op=0.10):
    seg = WF[a:b]
    return svg + band(x(a) - slot * .34, x(b - 1) + slot * .34,
                      y(max(c["h"] for c in seg)), y(min(c["l"] for c in seg)), col, op)


def f_htf(r=None, Wd=880, H=250):
    """١ · شمعةُ الفريم الأعلى اثنتا عشرة شمعةً صغيرة."""
    svg, x, y, slot = _gf(Wd, H)
    for a, b in F_FULL:
        svg = _hbox(svg, x, y, slot, a, b, INK, 0.10)
    svg += spanx(x(F_FULL[0][0]) - slot * .5, x(F_FULL[0][1] - 1) + slot * .5,
                 y(max(c["h"] for c in WF[F_FULL[0][0]:F_FULL[0][1]])),
                 rt(f'{ar(F_K)} شمعة'), INK)
    svg += RC._title(Wd, rt("شمعة الساعة اثنتا عشرة شمعة صغيرة"))
    svg += RC._why(Wd, H, f'كلُّ صندوقٍ شمعةُ فريمٍ أعلى مكتملة — '
                          f'{ar(F_K)} شمعةٍ صغيرة تصنع واحدة', INK)
    svg += sm(Wd, H, "وما دام الصندوق ما سكّر، الشمعة ما خلصت")
    return svg + badge(Wd, "مثال تخطيطي", True) + "</svg>"


def f_pos(r=None, Wd=880, H=250):
    """٢ · السعر عند أحد عشر بالمئة من قاع الجارية."""
    svg, x, y, slot = _gf(Wd, H)
    svg = _hbox(svg, x, y, slot, F_S, F_S + F_DONE, TEAL_D, 0.14)
    svg += hl(x(F_S) - slot * .5, x(F_N - 1) + slot * .5, y(F_HI), INK, 1.6)
    svg += hl(x(F_S) - slot * .5, x(F_N - 1) + slot * .5, y(F_LO), INK, 1.6)
    svg += vspan(x(F_S + F_DONE - 1) + slot * 1.8, y(F_PX), y(F_LO),
                 rt(f'{ar(round(F_POS * 100))}٪'), TEAL_D, 16, H)
    svg += RC._title(Wd, rt("والسعر الآن قريبٌ من قاعها"))
    svg += RC._why(Wd, H, f'موضعُ السعر {ar(round(F_POS * 100))}٪ من قاع مدى '
                          f'الشمعة الجارية — أي إغلاقٌ ضعيفٌ لو سكّرت الحين', TEAL_D)
    svg += sm(Wd, H, "الموضع رقم، مو إحساس بأن «الشمعة حمرا»")
    return svg + badge(Wd, "مثال تخطيطي", True) + "</svg>"


def f_left(r=None, Wd=880, H=250):
    """٣ · أربعُ شمعاتٍ باقية قبل الإغلاق."""
    svg, x, y, slot = _gf(Wd, H)
    svg = _hbox(svg, x, y, slot, F_S, F_S + F_DONE, TEAL_D, 0.10)
    for i in range(F_S + F_DONE, F_N):
        svg += mark(x(i), slot, y(WF[i]["h"]), y(WF[i]["l"]), RED, 0.18)
    svg += spanx(x(F_S + F_DONE) - slot * .5, x(F_N - 1) + slot * .5,
                 y(max(c["h"] for c in WF[F_S + F_DONE:])),
                 rt(f'{ar(F_LEFT)} باقية'), RED)
    svg += RC._title(Wd, rt("وباقي أربع شمعات على إغلاقها"))
    svg += RC._why(Wd, H, f'{ar(F_DONE)} من {ar(F_K)} أُغلقت و{ar(F_LEFT)} '
                          f'باقية — وثلثُ الشمعة يقدر يقلب شكلها', RED)
    svg += sm(Wd, H, "اللي يقرأ الشمعة قبل ما تسكّر يقرأ نصف جملة")
    return svg + badge(Wd, "مثال تخطيطي", True) + "</svg>"


def f_size(r=None, Wd=880, H=250):
    """٤ · مدى الجارية أربعةُ أضعاف الصغيرة تقريباً."""
    svg, x, y, slot = _gf(Wd, H)
    svg = _hbox(svg, x, y, slot, F_S, F_S + F_DONE, TEAL_D, 0.12)
    svg += vspan(x(F_S) - slot * 1.6, y(F_HI), y(F_LO),
                 rt(f'{xr(F_SIZE)} الصغيرة'), INK, 16, H)
    svg += RC._title(Wd, rt("ومداها يساوي أربع شمعاتٍ صغيرة"))
    svg += RC._why(Wd, H, f'مدى الشمعة الجارية {xr(F_SIZE)} وسيطَ مدى الشمعة '
                          f'الصغيرة — ووقفُك يُقاس بالكبيرة لا بالصغيرة', INK)
    svg += sm(Wd, H, "تدخل على الصغيرة وتحتمل على الكبيرة — وهنا الغلط")
    return svg + badge(Wd, "مثال تخطيطي", True) + "</svg>"


def f_all(r=None, Wd=880, H=250):
    """٥ · الخلاصة: أربعةُ أرقامٍ تُقرأ الآن."""
    svg, x, y, slot = _gf(Wd, H)
    svg = _hbox(svg, x, y, slot, F_S, F_S + F_DONE, TEAL_D, 0.12)
    for i in range(F_S + F_DONE, F_N):
        svg += mark(x(i), slot, y(WF[i]["h"]), y(WF[i]["l"]), RED, 0.14)
    svg += RC._title(Wd, rt("الشمعة الجارية أربعة أرقام لا رأي"))
    svg += RC._why(Wd, H, f'مداها {xr(F_SIZE)} الصغيرة، والسعر '
                          f'{ar(round(F_POS * 100))}٪ من قاعها، وباقي '
                          f'{ar(F_LEFT)} من {ar(F_K)}', INK)
    svg += sm(Wd, H, "اقرأها بهالأربعة، وبعدها قرّر تدخل ولا تنتظر")
    return svg + badge(Wd, "مثال تخطيطي", True) + "</svg>"


# ═════════════════════════════════════════════════════════════════
# ٥ · «عائم» — الربح العائم وعدٌ لا رصيد (مالية · كاروسيل · تخطيطي)
# ═════════════════════════════════════════════════════════════════
M_SEED = 1484
M_ANCH = [(0, 100.0), (7, 99.2), (14, 99.6), (20, 101.9), (26, 100.4), (33, 100.9)]
M_N = 34
WM = gen(M_ANCH, M_N, M_SEED, wick=0.45, bn=0.5)
RM = {"sym": "SCHEMATIC-M", "slug": "مثال تخطيطي — عائم", "w": WM}
M_E = 14
M_ENT = WM[M_E]["c"]
M_STP = min(c["l"] for c in WM[M_E - 4:M_E + 1]) - 0.05
M_S = M_ENT - M_STP
M_TOP = max(range(M_E + 1, M_N), key=lambda k: WM[k]["h"])
M_MFE = (WM[M_TOP]["h"] - M_ENT) / M_S
M_EX = next(k for k in range(M_TOP + 1, M_N) if WM[k]["c"] <= M_ENT + 1.0 * M_S)
M_LOCK = (WM[M_EX]["c"] - M_ENT) / M_S
M_GAP = M_MFE - M_LOCK
M_MED = st.median(c["h"] - c["l"] for c in WM)
M_SU = M_S / M_MED

_real(WM, M_N)
assert 2.6 <= M_MFE <= 3.0, M_MFE
assert 0.8 <= M_LOCK <= 1.1, M_LOCK
assert M_EX - M_TOP == 1, M_EX - M_TOP
# مسافةُ الوقف تُرى على اللوحة: وقفٌ أقلُّ من وسيط المدى يجعل R شعرةً
# بين خطّين، فلا يُقرأ منه شيء. قِيس على النسخة السابقة: 0.94× لا تُرى.
assert M_SU >= 1.3, M_SU


def _gm(Wd, H):
    return frame(WM, Wd, H, pad=0.10, pb=66)


def _mlv(svg, x, y, slot, tgt=True):
    s, e = x(0) - slot * .5, x(M_N - 1) + slot * .5
    svg += hl(s, e, y(M_ENT), INK, 1.8)
    svg += hl(s, e, y(M_STP), RED, 1.6, "5 5")
    return svg


def m_trade(r=None, Wd=880, H=250):
    """١ · صفقةٌ ودخولٌ ووقف."""
    svg, x, y, slot = _gm(Wd, H)
    svg = _mlv(svg, x, y, slot)
    svg += mark(x(M_E), slot, y(WM[M_E]["h"]), y(WM[M_E]["l"]), TEAL, 0.22)
    svg += vspan(x(M_E) + slot * 2.0, y(M_ENT), y(M_STP),
                 rt(f'{xr(M_SU)} الوسيط'), RED, 16, H)
    svg += RC._title(Wd, rt("صفقة ودخول ووقف — وR وحدة القياس"))
    svg += RC._why(Wd, H, f'مسافةُ الوقف {xr(M_SU)} وسيطَ مدى الشمعة، '
                          f'وكلُّ ما بعدها يُقاس بها', INK)
    svg += sm(Wd, H, "R مو وحدة فلوس، هي وحدة مسافة")
    return svg + badge(Wd, "مثال تخطيطي", True) + "</svg>"


def m_peak(r=None, Wd=880, H=250):
    """٢ · الذروة: ٢.٨٢R على الشاشة."""
    svg, x, y, slot = _gm(Wd, H)
    svg = _mlv(svg, x, y, slot)
    svg += band(x(M_E) - slot * .5, x(M_TOP) + slot * .5,
                y(WM[M_TOP]["h"]), y(M_ENT), TEAL_D, 0.14)
    svg += mark(x(M_TOP), slot, y(WM[M_TOP]["h"]), y(WM[M_TOP]["l"]), TEAL, 0.24)
    svg += vspan(x(M_TOP) + slot * 2.0, y(WM[M_TOP]["h"]), y(M_ENT),
                 rt(f'{xr(M_MFE)}R عائم'), TEAL_D, 16, H)
    svg += RC._title(Wd, rt("والشاشة قالت ٢.٨٢R"))
    svg += RC._why(Wd, H, f'أقصى ربحٍ عائم {xr(M_MFE)}R بلغه أعلى فتيلٍ بعد '
                          f'الدخول بـ{ar(M_TOP - M_E)} شمعات', TEAL_D)
    svg += sm(Wd, H, "وهذا الرقم اللي تصوّره وترسله لصاحبك")
    return svg + badge(Wd, "مثال تخطيطي", True) + "</svg>"


def m_fall(r=None, Wd=880, H=250):
    """٣ · شمعةٌ واحدة أكلت الفرق."""
    svg, x, y, slot = _gm(Wd, H)
    svg = _mlv(svg, x, y, slot)
    svg += band(x(M_TOP) - slot * .5, x(M_EX) + slot * .5,
                y(WM[M_TOP]["h"]), y(WM[M_EX]["c"]), RED, 0.16)
    for i in range(M_TOP + 1, M_EX + 1):
        svg += mark(x(i), slot, y(WM[i]["h"]), y(WM[i]["l"]), RED, 0.20)
    svg += vspan(x(M_EX) + slot * 2.0, y(WM[M_TOP]["h"]), y(WM[M_EX]["c"]),
                 rt(f'{xr(M_GAP)}R'), RED, 16, H)
    svg += RC._title(Wd, rt("وشمعةٌ وحدة شالت الفرق كله"))
    svg += RC._why(Wd, H, f'من الذروة إلى الخروج شمعةٌ واحدة — '
                          f'ونزل {xr(M_GAP)}R', RED)
    svg += sm(Wd, H, "ما صار شي غلط بالتحليل — صار الوقت مرّ")
    return svg + badge(Wd, "مثال تخطيطي", True) + "</svg>"


def m_locked(r=None, Wd=880, H=250):
    """٤ · المقيَّد: ٠.٨٦R."""
    svg, x, y, slot = _gm(Wd, H)
    svg = _mlv(svg, x, y, slot)
    svg += band(x(M_E) - slot * .5, x(M_EX) + slot * .5,
                y(WM[M_EX]["c"]), y(M_ENT), TEAL_D, 0.14)
    svg += mark(x(M_EX), slot, y(WM[M_EX]["h"]), y(WM[M_EX]["l"]), TEAL_D, 0.24)
    svg += vspan(x(M_EX) + slot * 2.0, y(WM[M_EX]["c"]), y(M_ENT),
                 rt(f'{xr(M_LOCK)}R مقيَّد'), TEAL_D, 16, H)
    svg += RC._title(Wd, rt("واللي دخل الحساب ٠.٨٦R"))
    svg += RC._why(Wd, H, f'الربحُ المقيَّد {xr(M_LOCK)}R عند الشمعة '
                          f'{ar(M_EX - M_E)} — وهو وحده اللي يُحسب', TEAL_D)
    svg += sm(Wd, H, "ما يُقيَّد إلا عند إغلاقٍ فعلي، والباقي شاشة")
    return svg + badge(Wd, "مثال تخطيطي", True) + "</svg>"


def m_all(r=None, Wd=880, H=250):
    """٥ · الخلاصة: وعدٌ ورصيد."""
    svg, x, y, slot = _gm(Wd, H)
    svg = _mlv(svg, x, y, slot)
    svg += band(x(M_E) - slot * .5, x(M_TOP) + slot * .5,
                y(WM[M_TOP]["h"]), y(M_ENT), TEAL_D, 0.08)
    svg += mark(x(M_TOP), slot, y(WM[M_TOP]["h"]), y(WM[M_TOP]["l"]), TEAL, 0.20)
    svg += mark(x(M_EX), slot, y(WM[M_EX]["h"]), y(WM[M_EX]["l"]), RED, 0.20)
    svg += RC._title(Wd, rt("عائمٌ ٢.٨٢ ومقيَّدٌ ٠.٨٦"))
    svg += RC._why(Wd, H, f'الفرق {xr(M_GAP)}R ضاع في شمعةٍ واحدة — '
                          f'فاكتب متى تُقيّد قبل ما تدخل', INK)
    svg += sm(Wd, H, "الرقم الأخضر وعد، والإغلاق هو الرصيد")
    return svg + badge(Wd, "مثال تخطيطي", True) + "</svg>"


# ═════════════════════════════════════════════════════════════════
SETS = {"trend": [d_chan, d_wick, d_body, d_cmp, d_all],
        "hissa": [s_move, s_big, s_rest, s_net, s_all],
        "tashabuh": [p_look, p_cond, p_strict, p_gap, p_all],
        "tashakkul": [f_htf, f_pos, f_left, f_size, f_all],
        "aaim": [m_trade, m_peak, m_fall, m_locked, m_all]}
WINS = {"trend": RD, "hissa": RS, "tashabuh": RP, "tashakkul": RF, "aaim": RM}
REAL = {"trend": D_WIN, "hissa": S_WIN}
SYN = {"tashabuh": (P_SEED, P_ANCH), "tashakkul": (F_SEED, F_ANCH),
       "aaim": (M_SEED, M_ANCH)}


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
        print(f'{slug:<10} ثبت {len(ok)}/{len(SETS[slug])} · {r["slug"]}'
              + ("" if not dropped else " · سقط "
                 + " · ".join(f"{a}: {b}" for a, b in dropped)))
