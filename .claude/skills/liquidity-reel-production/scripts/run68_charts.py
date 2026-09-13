# -*- coding: utf-8 -*-
"""جارتات تشغيلة ٦٨ — وحدتان على سوقٍ حقيقي وثلاثٌ تخطيطية.

المسحُ أمس عاد بصفر نافذةٍ حرّة، وتعليقُ `sheet_scan` نفسه يصف العلاج:
«قائمةٌ تُوسَّع ولا تُخفَّض عتبة». فوُسّعت القائمة من ٤٣ زوجاً إلى ١٠٣
(٥٥ أداة، وعلى رأسها العملاتُ الرقمية لأنها تتداول في العطلة) — فعاد
المسح بـ٤٩ نافذة، ٣١ منها حرّة بقياس الدالّة التي تحرس الفراغ
(`run31_charts._span` ثم `assert_fresh_real`). ولم تُمسّ عتبةٌ واحدة.

ووحدتان فنيتان أخذتا نافذتين حقيقيتين:
  · «عائق» (١٣٦) ← ٦٨ · لايتكوين/دولار · ساعة · 2026-06-14 · فئة `chan`
  · «حبس» (١٣٣) ← ٦٩ · دوجكوين/دولار · ساعة · 2026-08-30 · فئة `consol`
و«حبس» كان مؤجَّلاً ثلاث مرّات لأن النوافذ السابقة تسقط عتباتِه؛ وهذه
تجتازها الثلاث: جسمُ الكسر 2.56× (المطلوب 1.8 فأكثر)، والامتداد 1.15×
(المطلوب 1.0 فأكثر)، وأطولُ شمعةٍ داخل المدى 1.55× (المطلوب 1.6 فأقل).

والثلاث الباقية بقاعدة §11 البديلة بشروطها: شارة «مثال تخطيطي» على كل
لوحة · كلُّ ادّعاءٍ مقيسٌ بـ`assert` · أعدادٌ ونِسبٌ لا أسعار.

    python3 run68_charts.py
"""
import statistics as st

from reel_build import INK, TEAL, TEAL_D, RED, gen
from run15_charts import hl, badge, frame
import run31_charts as RC
from run58_charts import ar, rt, sm, band, mark
from run59_charts import spanx, vspan, xr


def _real(W, n):
    """تشتّتُ المدى وعددُ الهابطة ونسبةُ الجسم — حارسُ §4 على أي سلسلة مولّدة.

    وحدُّ الجسم أُضيف في ٦٨ بعد فحصٍ بصري: `gen(wick=0.9)` يعطي وسيطَ
    مدىً خمسةَ أضعاف وسيطِ الجسم، فتُقرأ اللوحة حقلَ صلبانٍ لا شموعاً.
    والنوافذُ الحقيقية في هذه التشغيلة بين 2.3 و2.4 — فهذا هو المعيار،
    ومعه سقفٌ لأطول شمعة كي لا تسحق واحدةٌ شاذّةٌ بقيّةَ اللوحة."""
    R = [c["h"] - c["l"] for c in W]
    B = [abs(c["c"] - c["o"]) for c in W]
    dn = sum(1 for c in W if c["c"] < c["o"])
    med, bod = st.median(R), st.median(B)
    assert st.pstdev(R) / st.mean(R) >= 0.45, st.pstdev(R) / st.mean(R)
    assert dn >= n * 0.30, f"الهابطة {dn} من {n} — سلّمٌ لا سوق"
    assert 1.9 <= med / bod <= 3.1, f"وسيط المدى {med/bod:.2f} وسيطَ الجسم"
    assert max(R) / med <= 3.6, f"أطول شمعة {max(R)/med:.2f}× — تسحق اللوحة"


# ═════════════════════════════════════════════════════════════════
# ١ · «عائق» — القمم بين الدخول والهدف (فنية · ريل · سوقٌ حقيقي)
#     لايتكوين/دولار · ساعة · 2026-06-14 · ٣٨ شمعة
# ═════════════════════════════════════════════════════════════════
O_WIN = 68
RO = RC.win(O_WIN)
WO = RO["w"]
O_N = len(WO)
O_IR = RO["ir"]
O_IOB = RO["iob"]
O_ENT = WO[O_IR]["c"]
_orng = (max(c["h"] for c in WO[:O_IR + 1]) - min(c["l"] for c in WO[:O_IR + 1]))
O_STP = WO[O_IOB]["l"] - _orng * 0.006
O_R = O_ENT - O_STP
O_TGT = O_ENT + 2 * O_R
O_MED = st.median(c["h"] - c["l"] for c in WO)

_piv = []
for _k in range(2, O_IR - 1):
    _h = WO[_k]["h"]
    if all(_h >= WO[_j]["h"] for _j in range(_k - 2, _k + 3) if _j != _k) \
            and O_ENT < _h < O_TGT:
        _piv.append((_k, _h))
_piv.sort(key=lambda p: p[1])
O_OBS = []
for _k, _h in _piv:
    if O_OBS and _h - O_OBS[-1][1] < 0.35 * O_MED:
        continue
    O_OBS.append((_k, _h))
O_RS = [(h - O_ENT) / O_R for _, h in O_OBS]
O_HIT = next(k for k in range(O_IR + 1, O_N) if WO[k]["h"] >= O_TGT)
O_LOW = min(range(O_IR + 1, O_HIT + 1), key=lambda k: WO[k]["l"])
O_MAE = (O_ENT - WO[O_LOW]["l"]) / O_R
O_FIRST = O_OBS[0]
O_STALL = [k for k in range(O_IR + 1, O_HIT + 1)
           if O_FIRST[1] - 0.25 * O_MED <= WO[k]["h"] <= O_FIRST[1] + 0.6 * O_MED]

assert len(O_OBS) == 3, len(O_OBS)
assert O_RS[0] <= 0.45, O_RS[0]
assert O_HIT - O_IR == 8, O_HIT - O_IR
assert len(O_STALL) == 5, len(O_STALL)
assert O_MAE <= 0.75, O_MAE
assert O_FIRST[0] == RO["iH"], (O_FIRST[0], RO["iH"])   # أولُ عائقٍ هو القمّةُ المكسورة


def _go(Wd, H):
    return frame(WO, Wd, H, pad=0.08, pb=64)


def _olevels(svg, x, slot, y):
    e = x(O_N - 1) + slot * .5
    s = x(0) - slot * .5
    svg += hl(s, e, y(O_ENT), INK, 1.8)
    svg += hl(s, e, y(O_STP), RED, 1.6, "5 5")
    svg += hl(s, e, y(O_TGT), TEAL_D, 1.6, "5 5")
    return svg


def o_trade(r=None, Wd=880, H=250):
    """١ · ثلاثةُ مستويات: دخولٌ ووقفٌ وهدف."""
    svg, x, y, slot = _go(Wd, H)
    svg = _olevels(svg, x, slot, y)
    svg += mark(x(O_IR), slot, y(WO[O_IR]["h"]), y(WO[O_IR]["l"]), TEAL, 0.22)
    svg += vspan(x(O_IR) + slot * 2.1, y(O_ENT), y(O_STP), rt("مخاطرة"), RED, 16, H)
    svg += RC._title(Wd, rt("الصفقة ثلاثة أرقام تعرفها قبل الضغط"))
    svg += RC._why(Wd, H, f'الدخول عند {O_ENT:.4f} والوقف {O_STP:.4f} '
                          f'والهدف {O_TGT:.4f} — ضعفا المخاطرة', INK)
    svg += sm(Wd, H, "وإلى هنا كل شي واضح — والغلط يبدأ بعد هذي اللوحة")
    return svg + "</svg>"


def o_levels(r=None, Wd=880, H=250):
    """٢ · ما بين الدخول والهدف ثلاثُ قممٍ لا فراغ."""
    svg, x, y, slot = _go(Wd, H)
    svg = _olevels(svg, x, slot, y)
    for (k, h), rr in zip(O_OBS, O_RS):
        svg += hl(x(k) - slot * .5, x(O_N - 1) + slot * .5, y(h), TEAL_D, 1.4, "3 4")
        svg += mark(x(k), slot, y(WO[k]["h"]), y(WO[k]["l"]), TEAL_D, 0.18)
    svg += RC._title(Wd, rt("والطريق للهدف مو فاضي"))
    svg += RC._why(Wd, H, f'{ar(len(O_OBS))} قمم وسيطة بين الدخول والهدف — '
                          f'عند {xr(O_RS[0])} و{xr(O_RS[1])} و{xr(O_RS[2])} من المخاطرة', TEAL_D)
    svg += sm(Wd, H, "وكل وحدة منهن أوامرُ بيعٍ نايمة، مو خطٌّ على الشاشة")
    return svg + "</svg>"


def o_near(r=None, Wd=880, H=250):
    """٣ · أقربُ عائقٍ هو القمّةُ التي كسرتها أصلاً."""
    svg, x, y, slot = _go(Wd, H)
    svg = _olevels(svg, x, slot, y)
    svg += hl(x(0) - slot * .5, x(O_N - 1) + slot * .5, y(O_FIRST[1]), TEAL_D, 1.8)
    svg += mark(x(O_FIRST[0]), slot, y(WO[O_FIRST[0]]["h"]), y(WO[O_FIRST[0]]["l"]),
                TEAL_D, 0.24)
    svg += vspan(x(O_IR) + slot * 2.1, y(O_FIRST[1]), y(O_ENT),
                 rt(f'{xr(O_RS[0])} فقط'), TEAL_D, 16, H)
    svg += RC._title(Wd, rt("وأقربهن هي القمّة اللي كسرتها"))
    svg += RC._why(Wd, H, f'العائق الأول على بُعد {xr(O_RS[0])} من المخاطرة — '
                          f'وهو نفس المستوى الذي فتح لك الصفقة', TEAL_D)
    svg += sm(Wd, H, "كسرتها فصارت أرضًا — ثم رجعت فوقها فصارت سقفًا")
    return svg + "</svg>"


def o_stall(r=None, Wd=880, H=250):
    """٤ · خمسُ شمعاتٍ من ثمانٍ عند العائق الأول."""
    svg, x, y, slot = _go(Wd, H)
    svg = _olevels(svg, x, slot, y)
    svg += hl(x(0) - slot * .5, x(O_N - 1) + slot * .5, y(O_FIRST[1]), TEAL_D, 1.6)
    for k in O_STALL:
        svg += mark(x(k), slot, y(WO[k]["h"]), y(WO[k]["l"]), TEAL_D, 0.20)
    svg += spanx(x(O_IR) + slot * .5, x(O_HIT) + slot * .5,
                 y(max(c["h"] for c in WO[O_IR:O_HIT + 1])),
                 rt(f'{ar(O_HIT - O_IR)} شمعات للهدف'), INK)
    svg += RC._title(Wd, rt("وخمس من ثمان راحن على أول عائق"))
    svg += RC._why(Wd, H, f'{ar(len(O_STALL))} شمعات من {ar(O_HIT - O_IR)} تعاملن '
                          f'مع العائق الأول وحده قبل ما يعدّيه السعر', TEAL_D)
    svg += sm(Wd, H, "والوقت اللي تصبر فيه محسوب من هنا، مو من الهدف")
    return svg + "</svg>"


def o_all(r=None, Wd=880, H=250):
    """٥ · القصّة كاملة: ثلاثُ قممٍ وتراجعٌ ثم الهدف."""
    svg, x, y, slot = _go(Wd, H)
    svg = _olevels(svg, x, slot, y)
    for k, h in O_OBS:
        svg += hl(x(k) - slot * .5, x(O_N - 1) + slot * .5, y(h), TEAL_D, 1.3, "3 4")
    svg += band(x(O_IR) - slot * .5, x(O_LOW) + slot * .5,
                y(O_ENT), y(WO[O_LOW]["l"]), RED, 0.14)
    svg += mark(x(O_HIT), slot, y(WO[O_HIT]["h"]), y(WO[O_HIT]["l"]), TEAL, 0.22)
    svg += RC._title(Wd, rt("عدّ العوائق قبل لا تحسب الهدف"))
    svg += RC._why(Wd, H, f'{ar(len(O_OBS))} قمم وأسوأ تراجعٍ {xr(O_MAE)} من المخاطرة '
                          f'— ثم بلغ الهدف بالشمعة {ar(O_HIT - O_IR)}', INK)
    svg += sm(Wd, H, "الهدف وصل، بس الطريق له كان مزحومًا ومحسوبًا")
    return svg + "</svg>"


# ═════════════════════════════════════════════════════════════════
# ٢ · «حبس» — عرضُ المدى مسطرة (فنية · ريل · سوقٌ حقيقي)
#     دوجكوين/دولار · ساعة · 2026-08-30 · ٤٥ شمعة
# ═════════════════════════════════════════════════════════════════
B_WIN = 69
RB = RC.win(B_WIN)
WB = RB["w"]
B_N = len(WB)
B_CA, B_CB, B_IR = RB["ca"], RB["cb"], RB["ir"]
B_SEG = WB[B_CA:B_CB + 1]
B_RT = max(c["h"] for c in B_SEG)
B_RB = min(c["l"] for c in B_SEG)
B_W = B_RT - B_RB
B_HELD = len(B_SEG)
B_BODY = [abs(c["c"] - c["o"]) for c in B_SEG]
B_RNG = [c["h"] - c["l"] for c in B_SEG]
B_LNG = max(B_RNG) / st.median(B_RNG)
B_TALL = B_CA + max(range(B_HELD), key=lambda i: B_RNG[i])
B_KB = next(k for k in range(B_CB + 1, B_IR + 1) if WB[k]["c"] < B_RB)
B_BK = abs(WB[B_KB]["c"] - WB[B_KB]["o"]) / st.median(B_BODY)
B_LO = min(c["l"] for c in WB[B_KB:B_IR + 2])
B_ILO = min(range(B_KB, min(B_IR + 2, B_N)), key=lambda k: WB[k]["l"])
B_EXT = (B_RB - B_LO) / B_W
B_ENT = WB[B_IR]["c"]
_brng = (max(c["h"] for c in WB[:B_IR + 1]) - min(c["l"] for c in WB[:B_IR + 1]))
B_STP = WB[RB["iob"]]["l"] - _brng * 0.006
B_RR = B_ENT - B_STP
B_TGT = B_ENT + 2 * B_RR
B_HIT = next(k for k in range(B_IR + 1, B_N) if WB[k]["h"] >= B_TGT)
B_RW = B_RR / B_W
B_TW = (B_TGT - B_ENT) / B_W

assert B_HELD == 7, B_HELD
assert B_LNG <= 1.6, B_LNG
assert B_BK >= 1.8, B_BK
assert B_EXT >= 1.0, B_EXT
assert B_KB == B_CB + 1, (B_KB, B_CB)


def _gb(Wd, H):
    return frame(WB, Wd, H, pad=0.08, pb=64)


def _gbox(svg, x, y, slot, op=0.16):
    return svg + band(x(B_CA) - slot * .5, x(B_CB) + slot * .5,
                      y(B_RT), y(B_RB), TEAL_D, op)


def b_box(r=None, Wd=880, H=250):
    """١ · مدىً حبس سبع شمعات."""
    svg, x, y, slot = _gb(Wd, H)
    svg = _gbox(svg, x, y, slot)
    svg += hl(x(B_CA) - slot * .5, x(B_N - 1) + slot * .5, y(B_RT), INK, 1.6)
    svg += hl(x(B_CA) - slot * .5, x(B_N - 1) + slot * .5, y(B_RB), INK, 1.6)
    svg += spanx(x(B_CA) - slot * .5, x(B_CB) + slot * .5, y(B_RT),
                 rt(f'{ar(B_HELD)} شمعات'), INK)
    svg += RC._title(Wd, rt("مدىً حبس السعر سبع شمعات"))
    svg += RC._why(Wd, H, f'من {WB[B_CA]["d"]} إلى {WB[B_CB]["d"]} — '
                          f'عرضُ المدى {B_W:.6f}', INK)
    svg += sm(Wd, H, "وهذا العرض هو كل المسطرة اللي بتحتاجها بعد شوي")
    return svg + "</svg>"


def b_clean(r=None, Wd=880, H=250):
    """٢ · مدىً نظيف: لا شمعةَ واحدة تسيطر عليه."""
    svg, x, y, slot = _gb(Wd, H)
    svg = _gbox(svg, x, y, slot, 0.12)
    svg += mark(x(B_TALL), slot, y(WB[B_TALL]["h"]), y(WB[B_TALL]["l"]), TEAL, 0.24)
    svg += vspan(x(B_TALL) + slot * 2.0, y(WB[B_TALL]["h"]), y(WB[B_TALL]["l"]),
                 rt(f'{xr(B_LNG)} الوسيط'), TEAL_D, 16, H)
    svg += RC._title(Wd, rt("وقبل تقيس، تأكد إنه مدىً نظيف"))
    svg += RC._why(Wd, H, f'أطولُ شمعةٍ داخله {xr(B_LNG)} وسيطَ شمعاته — '
                          f'ما تتجاوز {xr(1.6)}، فما في شمعةٌ صنعته وحدها', TEAL_D)
    svg += sm(Wd, H, "مدىً صنعته شمعةٌ وحدة عرضُه كذبة — لا تقيس عليه")
    return svg + "</svg>"


def b_break(r=None, Wd=880, H=250):
    """٣ · شمعةُ الكسر: جسمها ٢.٥٦× وسيطَ أجسام المدى."""
    svg, x, y, slot = _gb(Wd, H)
    svg = _gbox(svg, x, y, slot, 0.10)
    svg += hl(x(B_CA) - slot * .5, x(B_N - 1) + slot * .5, y(B_RB), INK, 1.6)
    svg += mark(x(B_KB), slot, y(max(WB[B_KB]["o"], WB[B_KB]["c"])),
                y(min(WB[B_KB]["o"], WB[B_KB]["c"])), RED, 0.26)
    svg += vspan(x(B_KB) + slot * 2.0, y(max(WB[B_KB]["o"], WB[B_KB]["c"])),
                 y(min(WB[B_KB]["o"], WB[B_KB]["c"])),
                 rt(f'{xr(B_BK)} الوسيط'), RED, 16, H)
    svg += RC._title(Wd, rt("والخروج منه ما كان متردد"))
    svg += RC._why(Wd, H, f'جسمُ شمعة الكسر {xr(B_BK)} وسيطَ أجسام المدى — '
                          f'إغلاقٌ تحت الحدّ لا لمسة', RED)
    svg += sm(Wd, H, "جسمٌ صغير عند الحدّ يعني ما صار شي — انتظر")
    return svg + "</svg>"


def b_ext(r=None, Wd=880, H=250):
    """٤ · الامتداد بعد الكسر يساوي عرضَ المدى."""
    svg, x, y, slot = _gb(Wd, H)
    svg = _gbox(svg, x, y, slot, 0.10)
    svg += hl(x(B_CA) - slot * .5, x(B_N - 1) + slot * .5, y(B_RB), INK, 1.6)
    svg += band(x(B_KB) - slot * .5, x(B_ILO) + slot * .5, y(B_RB), y(B_LO), RED, 0.14)
    svg += vspan(x(B_ILO) + slot * 2.0, y(B_RB), y(B_LO),
                 rt(f'{xr(B_EXT)} العرض'), RED, 16, H)
    svg += RC._title(Wd, rt("ونزل بقدّ عرضه بالضبط"))
    svg += RC._why(Wd, H, f'الامتدادُ بعد الكسر {xr(B_EXT)} عرضَ المدى — '
                          f'المسافة اللي حُبست هي المسافة اللي انطلقت', RED)
    svg += sm(Wd, H, "فعرضُ الحبس مو زينة، هو وحدةُ القياس اللي بعده")
    return svg + "</svg>"


def b_all(r=None, Wd=880, H=250):
    """٥ · الوقفُ والهدفُ بوحدة عرض المدى."""
    svg, x, y, slot = _gb(Wd, H)
    svg = _gbox(svg, x, y, slot, 0.10)
    svg += hl(x(0) - slot * .5, x(B_N - 1) + slot * .5, y(B_ENT), INK, 1.8)
    svg += hl(x(0) - slot * .5, x(B_N - 1) + slot * .5, y(B_STP), RED, 1.6, "5 5")
    svg += hl(x(0) - slot * .5, x(B_N - 1) + slot * .5, y(B_TGT), TEAL_D, 1.6, "5 5")
    svg += mark(x(B_HIT), slot, y(WB[B_HIT]["h"]), y(WB[B_HIT]["l"]), TEAL, 0.22)
    svg += RC._title(Wd, rt("عرضُ المدى يعطيك الوقف والهدف"))
    svg += RC._why(Wd, H, f'المخاطرة {xr(B_RW)} عرضَ المدى والهدف {xr(B_TW)} عرضه '
                          f'— أرقامٌ من الشارت لا من المزاج', INK)
    svg += sm(Wd, H, "قِس العرض أول، وبعدها كل شي ينحسب منه")
    return svg + "</svg>"


# ═════════════════════════════════════════════════════════════════
# ٣ · «تجريبي» — الرجعة التي تُقفل باليد (نفسية · كاروسيل · تخطيطي)
# ═════════════════════════════════════════════════════════════════
T_SEED = 19715
T_ANCH = [(0, 100.0), (6, 99.0), (12, 99.4), (18, 98.6), (24, 100.6), (33, 102.4)]
T_N = 34
WT = gen(T_ANCH, T_N, T_SEED, wick=0.42, bn=0.5)
RT_ = {"sym": "SCHEMATIC-T", "slug": "مثال تخطيطي — تجريبي", "w": WT}
T_E = 18
T_ENT = WT[T_E]["c"]
T_STP = min(c["l"] for c in WT[T_E - 4:T_E + 1]) - 0.05
T_S = T_ENT - T_STP
T_TGT = T_ENT + 2 * T_S
T_HIT = next(k for k in range(T_E + 1, T_N) if WT[k]["h"] >= T_TGT)
T_DEEP = min(range(T_E + 1, T_HIT + 1), key=lambda k: WT[k]["l"])
T_MAE = (T_ENT - WT[T_DEEP]["l"]) / T_S
T_RED = [k for k in range(T_E + 1, T_HIT + 1) if WT[k]["c"] < T_ENT]
T_MED = st.median(c["h"] - c["l"] for c in WT)
T_SU = T_S / T_MED

_real(WT, T_N)
assert 0.60 <= T_MAE <= 0.85, T_MAE
assert len(T_RED) == 5, len(T_RED)
assert T_HIT - T_E == 14, T_HIT - T_E


def _gt(Wd, H):
    return frame(WT, Wd, H, pad=0.10, pb=66)


def _tlv(svg, x, y, slot):
    s, e = x(0) - slot * .5, x(T_N - 1) + slot * .5
    svg += hl(s, e, y(T_ENT), INK, 1.8)
    svg += hl(s, e, y(T_STP), RED, 1.6, "5 5")
    svg += hl(s, e, y(T_TGT), TEAL_D, 1.6, "5 5")
    return svg


def t_setup(r=None, Wd=880, H=250):
    """١ · صفقةٌ واحدة على النظام نفسه."""
    svg, x, y, slot = _gt(Wd, H)
    svg = _tlv(svg, x, y, slot)
    svg += mark(x(T_E), slot, y(WT[T_E]["h"]), y(WT[T_E]["l"]), TEAL, 0.22)
    svg += vspan(x(T_E) + slot * 2.1, y(T_ENT), y(T_STP), rt(f'{xr(T_SU)} الوسيط'), RED, 16, H)
    svg += RC._title(Wd, rt("نفس النظام، نفس الدخلة، نفس الوقف"))
    svg += RC._why(Wd, H, f'الوقفُ {xr(T_SU)} وسيطَ مدى الشمعة والهدف ضعفاه — '
                          f'قواعدُ وحدة على الحسابين', INK)
    svg += sm(Wd, H, "فإذا النظام واحد، ليش النتيجة تختلف؟")
    return svg + badge(Wd, "مثال تخطيطي", True) + "</svg>"


def t_deep(r=None, Wd=880, H=250):
    """٢ · أعمقُ رجعةٍ أكلت ثلاثة أرباع الوقف."""
    svg, x, y, slot = _gt(Wd, H)
    svg = _tlv(svg, x, y, slot)
    svg += band(x(T_E) - slot * .5, x(T_DEEP) + slot * .5,
                y(T_ENT), y(WT[T_DEEP]["l"]), RED, 0.16)
    svg += mark(x(T_DEEP), slot, y(WT[T_DEEP]["h"]), y(WT[T_DEEP]["l"]), RED, 0.24)
    svg += vspan(x(T_DEEP) + slot * 2.1, y(T_ENT), y(WT[T_DEEP]["l"]),
                 rt(f'{xr(T_MAE)} الوقف'), RED, 16, H)
    svg += RC._title(Wd, rt("والرجعة وصلت ثلاثة أرباع الوقف"))
    svg += RC._why(Wd, H, f'أعمقُ نقطةٍ ضد الصفقة {xr(T_MAE)} من مسافة الوقف — '
                          f'قرّبت ولا ضربته', RED)
    svg += sm(Wd, H, "على الشاشة هذي اللحظة تبين معاك كأنها خسارة مؤكدة")
    return svg + badge(Wd, "مثال تخطيطي", True) + "</svg>"


def t_five(r=None, Wd=880, H=250):
    """٣ · خمسُ شمعاتٍ أغلقن تحت الدخول."""
    svg, x, y, slot = _gt(Wd, H)
    svg = _tlv(svg, x, y, slot)
    for k in T_RED:
        svg += mark(x(k), slot, y(WT[k]["h"]), y(WT[k]["l"]), RED, 0.20)
    svg += spanx(x(T_RED[0]) - slot * .5, x(T_RED[-1]) + slot * .5,
                 y(max(WT[k]["h"] for k in T_RED)),
                 rt(f'{ar(len(T_RED))} شمعات'), RED)
    svg += RC._title(Wd, rt("خمس شمعات تحت سعر دخولك"))
    svg += RC._why(Wd, H, f'{ar(len(T_RED))} شمعات متتالية أغلقن تحت الدخول — '
                          f'وهنا بالضبط تنضغط اليد على الزر', RED)
    svg += sm(Wd, H, "على التجريبي تتركهن يمشون، وعلى الحقيقي تقفل")
    return svg + badge(Wd, "مثال تخطيطي", True) + "</svg>"


def t_run(r=None, Wd=880, H=250):
    """٤ · بعدها انطلق للهدف."""
    svg, x, y, slot = _gt(Wd, H)
    svg = _tlv(svg, x, y, slot)
    svg += band(x(T_RED[-1]) - slot * .5, x(T_HIT) + slot * .5,
                y(T_TGT), y(T_ENT), TEAL_D, 0.14)
    svg += mark(x(T_HIT), slot, y(WT[T_HIT]["h"]), y(WT[T_HIT]["l"]), TEAL, 0.22)
    # بلا قوسٍ زمنيّ هنا: `spanx` يُقصَر إلى أسفل شريط العنوان، وخطُّ
    # الهدف يسكن هناك — فالقوسُ يركب عليه. العددُ في السطر تحت اللوحة.
    svg += RC._title(Wd, rt("والهدف جا بعدهن مباشرة"))
    svg += RC._why(Wd, H, f'الهدفُ تحقّق بعد {ar(T_HIT - T_E)} شمعة من الدخول — '
                          f'والخمسُ الحمر كنّ في طريقه لا ضدّه', TEAL_D)
    svg += sm(Wd, H, "اللي قفل عند الشمعة الخامسة سجّل خسارة على صفقةٍ رابحة")
    return svg + badge(Wd, "مثال تخطيطي", True) + "</svg>"


def t_all(r=None, Wd=880, H=250):
    """٥ · الفرق بين الحسابين خمسُ شمعات."""
    svg, x, y, slot = _gt(Wd, H)
    svg = _tlv(svg, x, y, slot)
    svg += band(x(T_E) - slot * .5, x(T_DEEP) + slot * .5,
                y(T_ENT), y(WT[T_DEEP]["l"]), RED, 0.12)
    svg += mark(x(T_HIT), slot, y(WT[T_HIT]["h"]), y(WT[T_HIT]["l"]), TEAL, 0.20)
    svg += RC._title(Wd, rt("الفرق مو بالنظام، الفرق بالخمس"))
    svg += RC._why(Wd, H, f'{xr(T_MAE)} من الوقف و{ar(len(T_RED))} شمعات حمر — '
                          f'ثم الهدف بالشمعة {ar(T_HIT - T_E)}', INK)
    svg += sm(Wd, H, "قِس رجعتك قبل، عشان تعرف شنو تحتمل قبل لا تدخل")
    return svg + badge(Wd, "مثال تخطيطي", True) + "</svg>"


# ═════════════════════════════════════════════════════════════════
# ٤ · «تكرار» — حالتان بخمسين شمعة (أساسية · كاروسيل · تخطيطي)
# ═════════════════════════════════════════════════════════════════
K_SEED = 58
K_ANCH = [(0, 100.0), (7, 101.6), (13, 100.4), (20, 99.2), (27, 100.2),
          (34, 99.0), (41, 101.0), (49, 102.6)]
K_N = 50
WK = gen(K_ANCH, K_N, K_SEED, wick=0.55, bn=0.5)
RK = {"sym": "SCHEMATIC-K", "slug": "مثال تخطيطي — تكرار", "w": WK}
K_MED = st.median(c["h"] - c["l"] for c in WK)
K_MB = st.median(abs(c["c"] - c["o"]) for c in WK)
K_SET = []
for _k in range(13, K_N - 9):
    _lvl = max(c["h"] for c in WK[_k - 12:_k - 1])
    if not (WK[_k]["c"] > _lvl and WK[_k - 1]["c"] <= _lvl):
        continue
    if abs(WK[_k]["c"] - WK[_k]["o"]) < 1.3 * K_MB:
        continue
    _pb = [j for j in range(_k + 1, min(_k + 9, K_N)) if WK[j]["l"] <= _lvl]
    if not _pb or WK[_pb[0]]["l"] < _lvl - 1.3 * K_MED:
        continue
    if K_SET and _k - K_SET[-1][0] < 6:
        continue
    K_SET.append((_k, _lvl, _pb[0], abs(WK[_k]["c"] - WK[_k]["o"]) / K_MB))
K_GAP = K_SET[1][0] - K_SET[0][0]

_real(WK, K_N)
assert len(K_SET) == 2, len(K_SET)
assert K_GAP == 13, K_GAP
assert K_SET[0][3] >= 1.3 and K_SET[1][3] >= 1.3, [s[3] for s in K_SET]


def _gk(Wd, H):
    return frame(WK, Wd, H, pad=0.10, pb=66)


def _kcase(svg, x, y, slot, i, col, op=0.24):
    k, lvl, j, b = K_SET[i]
    svg += hl(x(max(0, k - 13)) - slot * .5, x(min(K_N - 1, j + 3)) + slot * .5,
              y(lvl), INK, 1.6)
    svg += mark(x(k), slot, y(WK[k]["h"]), y(WK[k]["l"]), col, op)
    return svg


def k_first(r=None, Wd=880, H=250):
    """١ · الحالة الأولى: كسرٌ بجسمٍ ثلاثة أضعاف."""
    svg, x, y, slot = _gk(Wd, H)
    svg = _kcase(svg, x, y, slot, 0, TEAL)
    k, lvl, j, b = K_SET[0]
    svg += vspan(x(k) + slot * 2.2, y(max(WK[k]["o"], WK[k]["c"])),
                 y(min(WK[k]["o"], WK[k]["c"])), rt(f'{xr(b)} الوسيط'), TEAL_D, 16, H)
    svg += RC._title(Wd, rt("الحالة الأولى: كسرٌ يجتاز الشرطين"))
    svg += RC._why(Wd, H, f'إغلاقٌ فوق أعلى قمّةٍ في {ar(12)} شمعة، وجسمُ الكسر '
                          f'{xr(b)} وسيطَ الأجسام', TEAL_D)
    svg += sm(Wd, H, "شرطان تحققا — ويبقى ثالث")
    return svg + badge(Wd, "مثال تخطيطي", True) + "</svg>"


def k_cond(r=None, Wd=880, H=250):
    """٢ · الشرط الثالث: رجعةٌ تثبت فوق المستوى."""
    svg, x, y, slot = _gk(Wd, H)
    svg = _kcase(svg, x, y, slot, 0, TEAL, 0.16)
    k, lvl, j, b = K_SET[0]
    svg += mark(x(j), slot, y(WK[j]["h"]), y(WK[j]["l"]), TEAL_D, 0.24)
    svg += vspan(x(j) + slot * 2.2, y(lvl), y(lvl - 1.3 * K_MED),
                 rt("أعمقُ مسموح"), RED, 16, H)
    svg += RC._title(Wd, rt("والرجعة جت بشمعة وحدة"))
    svg += RC._why(Wd, H, f'رجعت بعد شمعةٍ واحدة ووقفت فوق الحدّ — ما نزلت '
                          f'أعمق من {xr(1.3)} وسيطَ المدى تحته', TEAL_D)
    svg += sm(Wd, H, "رجعةٌ أعمق من كذا تلغي الحالة، ما تأجّلها")
    return svg + badge(Wd, "مثال تخطيطي", True) + "</svg>"


def k_second(r=None, Wd=880, H=250):
    """٣ · الحالة الثانية بعد ثلاث عشرة شمعة."""
    svg, x, y, slot = _gk(Wd, H)
    svg = _kcase(svg, x, y, slot, 1, TEAL)
    k, lvl, j, b = K_SET[1]
    svg += vspan(x(k) + slot * 2.2, y(max(WK[k]["o"], WK[k]["c"])),
                 y(min(WK[k]["o"], WK[k]["c"])), rt(f'{xr(b)} الوسيط'), TEAL_D, 16, H)
    svg += RC._title(Wd, rt("والثانية جت بنفس الشروط"))
    svg += RC._why(Wd, H, f'جسمُ كسرها {xr(b)} وسيطَ الأجسام — أضعفُ من الأولى '
                          f'وما زالت تستوفي الشرط', TEAL_D)
    svg += sm(Wd, H, "الشرط عتبة تُجتاز، مو مسابقةٌ على الأقوى")
    return svg + badge(Wd, "مثال تخطيطي", True) + "</svg>"


def k_gap(r=None, Wd=880, H=250):
    """٤ · المسافة بين الحالتين ثلاث عشرة شمعة."""
    svg, x, y, slot = _gk(Wd, H)
    svg = _kcase(svg, x, y, slot, 0, TEAL, 0.18)
    svg = _kcase(svg, x, y, slot, 1, TEAL, 0.18)
    svg += spanx(x(K_SET[0][0]) - slot * .5, x(K_SET[1][0]) + slot * .5,
                 y(max(c["h"] for c in WK[K_SET[0][0]:K_SET[1][0] + 1])),
                 rt(f'{ar(K_GAP)} شمعة'), INK)
    svg += RC._title(Wd, rt("وبينهن ثلاث عشرة شمعة فاضية"))
    svg += RC._why(Wd, H, f'{ar(K_GAP)} شمعة بين الحالة والتي تليها — '
                          f'فراغٌ متوقَّع لا عطلٌ في السوق', INK)
    svg += sm(Wd, H, "ثلاث عشرة ساعة على فريم الساعة: نصفُ يومٍ ونصف")
    return svg + badge(Wd, "مثال تخطيطي", True) + "</svg>"


def k_all(r=None, Wd=880, H=250):
    """٥ · حالتان في خمسين شمعة."""
    svg, x, y, slot = _gk(Wd, H)
    for i in (0, 1):
        svg = _kcase(svg, x, y, slot, i, TEAL, 0.20)
    svg += RC._title(Wd, rt("حالتان بخمسين شمعة — وهذا معدّلك"))
    svg += RC._why(Wd, H, f'{ar(len(K_SET))} حالتان استوفتا الشروط الثلاثة في '
                          f'{ar(K_N)} شمعة — والباقي انتظار', INK)
    svg += sm(Wd, H, "لو دخلت أكثر من كذا، فأنت تدخل على نموذجٍ ثاني")
    return svg + badge(Wd, "مثال تخطيطي", True) + "</svg>"


# ═════════════════════════════════════════════════════════════════
# ٥ · «هامش» — كم شمعةً يحتمل حسابك (مالية · كاروسيل · تخطيطي)
# ═════════════════════════════════════════════════════════════════
G_SEED = 126
G_ANCH = [(0, 100.0), (7, 99.1), (14, 100.3), (21, 99.0), (31, 101.4)]
G_N = 32
WG = gen(G_ANCH, G_N, G_SEED, wick=0.65, bn=0.5)
RG = {"sym": "SCHEMATIC-G", "slug": "مثال تخطيطي — هامش", "w": WG}
G_R = [c["h"] - c["l"] for c in WG]
G_MED = st.median(G_R)
G_CUSH = 2.3                                     # وسادةُ المثال بوحدة الشمعة
G_MAX = max(range(G_N), key=lambda i: G_R[i])
G_MX = G_R[G_MAX] / G_MED
G_OVER = [i for i in range(G_N) if G_R[i] / G_MED > G_CUSH]
# شمعةُ الوسيط تُختار من وسط اللوحة لا من طرفها: وسمُها عند الحافّة
# يركب على جيرانها، وأيُّ شمعةٍ ضمن ٥٪ من الوسيط تؤدّي الغرض نفسه.
_gcands = [i for i in range(G_N) if abs(G_R[i] - G_MED) <= 0.05 * G_MED]
G_TYP = min(_gcands or range(G_N), key=lambda i: abs(i - G_N // 2))

_real(WG, G_N)
assert G_MX > G_CUSH, (G_MX, G_CUSH)
assert len(G_OVER) == 3, len(G_OVER)
assert 2.6 <= G_MX <= 3.2, G_MX


def _gg(Wd, H):
    return frame(WG, Wd, H, pad=0.12, pb=66)


def g_med(r=None, Wd=880, H=250):
    """١ · وحدةُ القياس: وسيطُ مدى الشمعة."""
    svg, x, y, slot = _gg(Wd, H)
    svg += mark(x(G_TYP), slot, y(WG[G_TYP]["h"]), y(WG[G_TYP]["l"]), TEAL, 0.24)
    svg += vspan(x(G_TYP) + slot * 2.0, y(WG[G_TYP]["h"]), y(WG[G_TYP]["l"]),
                 rt("وسيطُ المدى"), TEAL_D, 16, H)
    svg += RC._title(Wd, rt("أول شي: شنو حجم الشمعة عندك"))
    svg += RC._why(Wd, H, f'وسيطُ مدى الشمعة في {ar(G_N)} شمعة — '
                          f'وهذي وحدةُ القياس اللي بيتحسب عليها كل شي', TEAL_D)
    svg += sm(Wd, H, "مو أكبر شمعة ولا أصغر وحدة — الوسيط")
    return svg + badge(Wd, "مثال تخطيطي", True) + "</svg>"


def g_cush(r=None, Wd=880, H=250):
    """٢ · الوسادة: الهامشُ الحرّ بوحدة الشمعة."""
    svg, x, y, slot = _gg(Wd, H)
    _c = WG[G_TYP]["c"]
    svg += hl(x(0) - slot * .5, x(G_N - 1) + slot * .5, y(_c), INK, 1.6)
    svg += band(x(0) - slot * .5, x(G_N - 1) + slot * .5,
                y(_c), y(_c - G_CUSH * G_MED), RED, 0.14)
    svg += vspan(x(G_N - 4) + slot * 1.2, y(_c), y(_c - G_CUSH * G_MED),
                 rt(f'{xr(G_CUSH)} شمعة'), RED, 16, H)
    svg += RC._title(Wd, rt("والوسادة تنحسب مو تنحسّ"))
    svg += RC._why(Wd, H, f'الهامشُ الحرّ ÷ قيمة النقطة ÷ وسيط مدى الشمعة = '
                          f'{xr(G_CUSH)} شمعة معاكسة يحتملها الحساب', RED)
    svg += sm(Wd, H, "رقمٌ واحد يقول لك كم تبعد عن نداء الهامش")
    return svg + badge(Wd, "مثال تخطيطي", True) + "</svg>"


def g_big(r=None, Wd=880, H=250):
    """٣ · أكبرُ شمعةٍ في النافذة تتجاوز الوسادة وحدها."""
    svg, x, y, slot = _gg(Wd, H)
    svg += mark(x(G_MAX), slot, y(WG[G_MAX]["h"]), y(WG[G_MAX]["l"]), RED, 0.26)
    svg += vspan(x(G_MAX) + slot * 2.0, y(WG[G_MAX]["h"]), y(WG[G_MAX]["l"]),
                 rt(f'{xr(G_MX)} الوسيط'), RED, 16, H)
    svg += RC._title(Wd, rt("وشمعةٌ وحدة تاكلها كلها"))
    svg += RC._why(Wd, H, f'أكبرُ شمعةٍ في النافذة {xr(G_MX)} وسيطَ المدى — '
                          f'أوسعُ من وسادةٍ طولها {xr(G_CUSH)} شمعة', RED)
    svg += sm(Wd, H, "نداءُ الهامش ما يحتاج سلسلة خسائر، يحتاج شمعة")
    return svg + badge(Wd, "مثال تخطيطي", True) + "</svg>"


def g_three(r=None, Wd=880, H=250):
    """٤ · ثلاثُ شمعاتٍ من اثنتين وثلاثين تجاوزن الوسادة."""
    svg, x, y, slot = _gg(Wd, H)
    for i in G_OVER:
        svg += mark(x(i), slot, y(WG[i]["h"]), y(WG[i]["l"]), RED, 0.22)
    svg += RC._title(Wd, rt("ومو شمعة وحدة — ثلاث"))
    svg += RC._why(Wd, H, f'{ar(len(G_OVER))} شمعات من {ar(G_N)} تجاوزن الوسادة: '
                          f'{xr(G_R[G_OVER[0]]/G_MED)} و{xr(G_R[G_OVER[1]]/G_MED)} '
                          f'و{xr(G_R[G_OVER[2]]/G_MED)}', RED)
    svg += sm(Wd, H, "يعني الاحتمال مو نادر، هو شهريٌّ تقريبًا")
    return svg + badge(Wd, "مثال تخطيطي", True) + "</svg>"


def g_all(r=None, Wd=880, H=250):
    """٥ · الخلاصة: احسب وسادتك قبل لا تفتح."""
    svg, x, y, slot = _gg(Wd, H)
    _c = WG[G_TYP]["c"]
    svg += band(x(0) - slot * .5, x(G_N - 1) + slot * .5,
                y(_c), y(_c - G_CUSH * G_MED), RED, 0.10)
    svg += mark(x(G_MAX), slot, y(WG[G_MAX]["h"]), y(WG[G_MAX]["l"]), RED, 0.24)
    svg += RC._title(Wd, rt("وسادةٌ بشمعتين ونصف مو وسادة"))
    svg += RC._why(Wd, H, f'وسادةٌ {xr(G_CUSH)} شمعة وأكبرُ شمعةٍ {xr(G_MX)} — '
                          f'فالفرقُ يُسدّ بلوتٍ أصغر لا بأملٍ أكبر', INK)
    svg += sm(Wd, H, "صغّر اللوت حتى تصير وسادتك أوسع من أكبر شمعة")
    return svg + badge(Wd, "مثال تخطيطي", True) + "</svg>"


# ═════════════════════════════════════════════════════════════════
SETS = {"aaiq": [o_trade, o_levels, o_near, o_stall, o_all],
        "habs": [b_box, b_clean, b_break, b_ext, b_all],
        "tajribi": [t_setup, t_deep, t_five, t_run, t_all],
        "takrar": [k_first, k_cond, k_second, k_gap, k_all],
        "hamesh": [g_med, g_cush, g_big, g_three, g_all]}
WINS = {"aaiq": RO, "habs": RB, "tajribi": RT_, "takrar": RK, "hamesh": RG}
REAL = {"aaiq": O_WIN, "habs": B_WIN}
SYN = {"tajribi": (T_SEED, T_ANCH), "takrar": (K_SEED, K_ANCH),
       "hamesh": (G_SEED, G_ANCH)}


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
