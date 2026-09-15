# -*- coding: utf-8 -*-
"""جارتات تشغيلة ٣٥ — نافذة **حقيقية** من `raw_windows` لا رسمٌ مولّد.

المخزون عاد ممتلئاً بعد مسح 2026-08-07، فلا حاجة إلى التخطيطي هنا:
النافذة `bz_sc_2026-08-07_1051` (برنت · تنفيذ ٣ دقائق) حرّة لم تُنشر،
وتحمل في ملفها الفريمَين معاً — أربعين شمعة ساعة (سياق أربعين ساعة)
وستّين شمعة ثلاث دقائق (ثلاث ساعات) — وهذا ما يجعل موضوع «كم ساعة يطلبك
فريمك» مقيساً على الشموع لا موصوفاً بالكلام.

القاعدة كما هي: **ما لا تُثبته الشموع لا يُرسم**. كل حالة تتحقّق من
ادّعائها بـ`assert` قبل أن تُخرج SVG.
"""
import topdown
from reel_build import INK, TEAL, TEAL_D, RED, GREY, htext
from run15_charts import zbox, xm, tick, hl, badge, frame
import run31_charts as RC

SET = "bz_sc_2026-08-07_1051.json"
D, LAY, PLAN = topdown.build(SET)
EXEC = D["exec_tf"]
EXEC_MIN = int(EXEC.rstrip("m"))
W = D[EXEC]["w"]
H1 = D["1h"]["w"]
DP = PLAN["dp"]
L4, L5 = LAY[3], LAY[4]
LVL, EQ, SW = L4["lvl"], L4["eq"], L4["sw"]
FILL, HIT = PLAN["fill"], PLAN["hit"]
BARS = HIT - FILL

# ═══ التحقّق يسبق الرسم ═══
assert len(EQ) >= 2, "أقلّ من قاعين عند المستوى"
assert W[SW]["l"] < LVL < W[SW]["c"], "شمعة السحب لا تنزل تحت المستوى وتغلق فوقه"
assert all(W[j]["l"] > PLAN["STP"] for j in range(SW + 1, HIT + 1)), "الوقف ضُرب قبل الهدف"
assert W[HIT]["h"] >= PLAN["TGT"], "الهدف لم يُبلغ"
MINUTES = BARS * EXEC_MIN                    # زمن الصفقة من الدخول إلى الهدف
SPAN_MIN = (len(W) - 1) * EXEC_MIN           # مدى النافذة المعروضة
H1_HOURS = len(H1) - 1                       # سياق الساعة بالساعات

_AR = str.maketrans("0123456789", "٠١٢٣٤٥٦٧٨٩")


def ar(n):
    return str(int(n)).translate(_AR)


def _lab(x, y, txt, col, fs=19):
    import run15_charts as R15
    if R15.MINIMAL:
        return ""
    return htext(x, y, txt, col, round(fs * RC._SC[0]))


def _mark(x, y, col, r=12, sw=3):
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="none" stroke="{col}" stroke-width="{sw}"/>'


def _geo(w, Wd, H):
    return frame(w, Wd, H)


# ═══════════ الحالات ═══════════
def c_pool(Wd=880, H=250):
    """١ · تجمّع السيولة: قيعان متساوية على فريم التنفيذ."""
    svg, x, y, slot = _geo(W, Wd, H)
    svg += hl(x(min(EQ)) - slot * .8, x(min(HIT + 2, len(W) - 1)), y(LVL), INK, 2.0)
    for j in EQ:
        svg += _mark(x(j), y(W[j]["l"]), GREY, 9, 2.2)
    # فوق الخط لا تحته: الشريط السفلي محجوز لسطرَي «لماذا» و«الخلاصة»،
    # وأي وسم ينزل إليه يقع فوقهما.
    svg += _lab((x(min(EQ)) + x(max(EQ))) / 2, y(LVL) - round(16 * RC._SC[0]),
                f'{ar(len(EQ))} قيعان عند {LVL:,.{DP}f}', INK)
    svg += RC._title(Wd, f'ثلاث ساعات من فريم {EXEC_MIN} دقائق ترسم مستوى واحداً')
    svg += RC._why(Wd, H, "هني تنام أوامر الوقف — تحت الخط", INK)
    svg += RC._sum(Wd, H, f'النافذة كلها {ar(SPAN_MIN)} دقيقة أمام الشاشة')
    return svg + badge(Wd, f'برنت · {ar(EXEC_MIN)} دقائق', True) + "</svg>"


def c_sweep(Wd=880, H=250):
    """٢ · الفتيل تحت المستوى والإغلاق فوقه — لحظة القرار كلها شمعة واحدة."""
    c = W[SW]
    rg = c["h"] - c["l"]
    wick = (min(c["o"], c["c"]) - c["l"]) / rg
    assert wick >= 0.30, "الذيل السفلي ضعيف"
    svg, x, y, slot = _geo(W, Wd, H)
    svg += hl(x(min(EQ)) - slot * .8, x(min(HIT + 2, len(W) - 1)), y(LVL), INK, 2.0)
    svg += f'<line x1="{x(SW):.1f}" y1="{y(min(c["o"], c["c"])):.1f}" x2="{x(SW):.1f}" ' \
           f'y2="{y(c["l"]):.1f}" stroke="{RED}" stroke-width="9" stroke-linecap="round" opacity=".55"/>'
    svg += xm(x(SW), y(c["l"]))
    svg += _mark(x(SW), y(c["c"]), TEAL_D)
    svg += _lab(x(SW) - slot * 5.6, y(c["l"]) - round(10 * RC._SC[0]),
                f'ذيل رفض {ar(round(wick * 100))}٪', RED, 18)
    svg += RC._title(Wd, "الشمعة التي تقرّر تمرّ في ثلاث دقائق", TEAL_D)
    svg += RC._why(Wd, H, "هني القرار كله — لأن الإغلاق رجع فوق الخط", TEAL_D)
    svg += RC._sum(Wd, H, f'من فتح الشمعة إلى إغلاقها: {ar(EXEC_MIN)} دقائق')
    return svg + badge(Wd, "لحظة القرار", True) + "</svg>"


def c_plan(Wd=880, H=250):
    """٣ · الصفقة كاملة: دخول ووقف وهدف، والزمن الذي استغرقته. (البطل)

    مقصوصة على جوار الصفقة: النافذة الستّينية تهبط طويلاً قبل الدخول،
    فيصير الصندوق ختماً في الزاوية وأعلى اللوحة فارغاً. القصّ لا يغيّر
    رقماً — الشموع نفسها والادّعاءات نفسها، لكن ما يُشرَح يملأ الإطار."""
    j0 = max(0, FILL - 20)
    j1 = min(len(W), HIT + 7)
    w = W[j0:j1]
    fill, hit = FILL - j0, HIT - j0
    svg, x, y, slot = _geo(w, Wd, H)
    x0, x1 = x(fill) - slot * .6, x(min(hit + 2, len(w) - 1))
    svg += zbox(x0, y(PLAN["TGT"]), x1, y(PLAN["ENT"]), col=TEAL, stroke=TEAL_D, op=0.10)
    svg += zbox(x0, y(PLAN["ENT"]), x1, y(PLAN["STP"]), col=RED, stroke=RED, op=0.10)
    svg += hl(x0, x1, y(PLAN["ENT"]), INK, 2.0)
    svg += _lab(x0 + (x1 - x0) / 2, y(PLAN["TGT"]) + round(26 * RC._SC[0]),
                f'الهدف {PLAN["TGT"]:,.{DP}f}', TEAL_D, 18)
    svg += _lab(x0 + (x1 - x0) / 2, y(PLAN["STP"]) - round(10 * RC._SC[0]),
                f'الوقف {PLAN["STP"]:,.{DP}f}', RED, 18)
    svg += tick(x(hit), y(PLAN["TGT"]) - 26)
    svg += RC._title(Wd, f'من الدخول إلى الهدف: {ar(BARS)} شمعات = {ar(MINUTES)} دقيقة')
    svg += RC._why(Wd, H, "هني انتهت الصفقة — والشاشة صارت فاضية", TEAL_D)
    svg += RC._sum(Wd, H, f'دخول {PLAN["ENT"]:,.{DP}f} · وقف {PLAN["STP"]:,.{DP}f} '
                          f'· هدف {PLAN["TGT"]:,.{DP}f}')
    return svg + badge(Wd, f'{ar(MINUTES)} دقيقة', True) + "</svg>"


def c_context(Wd=880, H=250):
    """٤ · السياق على الساعة: أربعون شمعة = أربعون ساعة خلف قرارٍ من دقائق."""
    a = D["1h"]["anchor"]
    w = H1[max(0, a - 29):a + 1]
    L = LAY[2]
    off = max(0, a - 29)
    hi, lo = L["hi"] - off, L["lo"] - off
    assert 0 <= hi < len(w) and 0 <= lo < len(w), "فهارس الهيكل خارج المقطع"
    svg, x, y, slot = _geo(w, Wd, H)
    svg += hl(x(0), x(len(w) - 1), y(w[hi]["h"]), INK, 2.0)
    svg += _lab(x(4), y(w[hi]["h"]) - round(14 * RC._SC[0]),
                f'قمة {w[hi]["h"]:,.{DP}f}', INK, 18)
    svg += _mark(x(lo), y(w[lo]["l"]), TEAL_D, 11, 2.6)
    svg += _lab(x(lo) - slot * 3.4, y(w[lo]["l"]) + round(30 * RC._SC[0]),
                f'قاعٌ أعلى {w[lo]["l"]:,.{DP}f}', TEAL_D, 18)
    svg += RC._title(Wd, f'الساعة تُقرأ مرّة: {ar(len(w))} شمعة = {ar(len(w))} ساعة')
    svg += RC._why(Wd, H, "هني السياق — يُقرأ قبل الجلسة لا خلالها", INK)
    svg += RC._sum(Wd, H, "قراءةٌ واحدة على الساعة تكفي ليومٍ كامل")
    return svg + badge(Wd, "برنت · ساعة", True) + "</svg>"


CASES = [c_plan, c_pool, c_sweep, c_context]      # البطل أولاً

if __name__ == "__main__":
    print(f'{D["sym"]} · {EXEC} · {D["anchor_utc"]} · شموع {len(W)} · '
          f'صفقة {BARS} شمعات = {MINUTES} دقيقة · نافذة {SPAN_MIN} دقيقة · '
          f'ساعة {H1_HOURS} ساعة')
    for f in CASES:
        f(880, 250); print("✓", f.__name__)
