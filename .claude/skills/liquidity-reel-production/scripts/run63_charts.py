# -*- coding: utf-8 -*-
"""جارتات تشغيلة ٦٣ — نافذةٌ حقيقية واحدة وأربعُ سلاسل تخطيطية.

مخزون `sheet_candidates.json` كان صفراً حرّاً، فمُسح الفريم اليومي
بـ`daily_scan` فأعطى نافذةً واحدة (النحاس · يومي · ٣٤ شمعة) — أخذتها
الوحدة الفنية الأولى، والأربع الباقية تخطيطية بقاعدة §11 البديلة
بشروطها الثلاثة (شارة «مثال تخطيطي» · كل ادّعاءٍ مقيسٌ بـ`assert` ·
أعدادٌ ونِسبٌ لا أسعار).

    python3 run63_charts.py
"""
import statistics as st

from reel_build import INK, TEAL, TEAL_D, RED, GREY, htext, gen
from run15_charts import zbox, xm, tick, hl, badge, frame
import run31_charts as RC
from run58_charts import ar, rt, why, sm, band, mark, span, ranges
from run59_charts import tag, spanx, vspan, xr, _pt

import datetime as dt


def _lab(x, y, txt, col, fs=19):
    import run15_charts as R15
    if R15.MINIMAL:
        return ""
    return htext(x, y, txt, col, round(fs * RC._SC[0]))


def _ring(x, y, col, r=12, sw=3):
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="none" stroke="{col}" stroke-width="{sw}"/>'


# ═════════ ١ · أسبوعي — حدود الأسبوع الماضي (فنية · نافذة حقيقية) ═════════
WIN_A = 66
_R = RC.win(WIN_A)
WA = _R["w"]
A_YEAR = 2026


def _weeks(W):
    """تقسيم النافذة إلى أسابيع تقويمية — الحدود من التاريخ لا من العدّ.

    عدُّ خمسٍ خمساً يكذب على أسبوعٍ فيه عطلة: أسبوعُ الافتتاح هنا أربعة
    أيام وأسبوعُ الختام يومٌ واحد."""
    out = {}
    for i, c in enumerate(W):
        m, d = map(int, c["d"].split("-"))
        out.setdefault(dt.date(A_YEAR, m, d).isocalendar()[:2], []).append(i)
    return [out[k] for k in sorted(out)]


A_WK = _weeks(WA)
A_HL = [(max(WA[i]["h"] for i in g), min(WA[i]["l"] for i in g)) for g in A_WK]
assert len(A_WK) == 8, len(A_WK)


def _brk(n):
    """أوّل يومٍ في الأسبوع n تجاوز حدَّ الأسبوع السابق — أعلى أو أدنى."""
    ph, pl = A_HL[n - 1]
    up = next((i for i in A_WK[n] if WA[i]["h"] > ph), None)
    dn = next((i for i in A_WK[n] if WA[i]["l"] < pl), None)
    return up, dn


A_BRK = {n: _brk(n) for n in range(1, len(A_WK))}
# الأسابيع الكاملة وحدها تُحسب: الأخير يومٌ واحد فلا يُسأل عن سلوك أسبوع.
A_FULL = [n for n in range(1, len(A_WK) - 1)]
A_OUT = [n for n in A_FULL if A_BRK[n][0] or A_BRK[n][1]]
A_IN = [n for n in A_FULL if not (A_BRK[n][0] or A_BRK[n][1])]
assert len(A_FULL) == 6 and len(A_OUT) == 4 and len(A_IN) == 2, (A_FULL, A_OUT, A_IN)
# اليومُ الذي وقع فيه الكسر داخل أسبوعه — الترتيب لا الفهرس المطلق.
A_DAY = {n: (A_WK[n].index(A_BRK[n][0] or A_BRK[n][1]) + 1) for n in A_OUT}
A_EARLY = [n for n in A_OUT if A_DAY[n] <= 2]
assert len(A_EARLY) == 4, A_DAY
_A_MED = st.median([c["h"] - c["l"] for c in WA])
A_RNG = [(h - l) / _A_MED for h, l in A_HL[:-1]]
assert 1.5 <= min(A_RNG) and max(A_RNG) <= 5.0, A_RNG


def _ga(Wd, H):
    return frame(WA, Wd, H, pad=0.08, pb=62)


def a_bounds(r=None, Wd=880, H=250):
    """حدّان اثنان لا خطٌّ واحد: قمّة الأسبوع الماضي وقاعُه."""
    svg, x, y, slot = _ga(Wd, H)
    n = A_FULL[-1]
    ph, pl = A_HL[n - 1]
    g = A_WK[n]
    # الحدّ يبدأ حيث وُلد: من إغلاق الأسبوع السابق لا من أوّله — قبل ذلك
    # لم يكن حدّاً بعد. والوسمان في الطرف الأيسر من اللوحة حيث الشمعات
    # الأولى أوطأ من الحدّين بكثير، فلا يجلس نصٌّ على شمعة.
    L, Rt = x(A_WK[n - 1][-1]) + slot * .5, x(g[-1]) + slot * .5
    svg += hl(L, Rt, y(ph), INK, 2.0) + hl(L, Rt, y(pl), INK, 2.0)
    svg += band(x(g[0]) - slot * .5, Rt, y(ph), y(pl), TEAL, 0.10)
    # بلا وسمين على اللوحة: النافذة أربعٌ وثلاثون شمعة يومية فلا فراغ
    # يتّسع لسطرين عربيّين لا يجلسان على شمعة — قيست ثلاثة مواضع
    # (يسار اللوحة · داخل الشريط · يمين الخطّين) فكلُّها مشغولة. والخطّان
    # الكحليّان والشريط بينهما يقولان ما يقوله الوسم، والعنوان وسطرا
    # «لماذا» يسمّيانهما بالكلمات.
    svg += RC._title(Wd, rt("حدّان تبدأ منهما"))
    svg += why(Wd, H, "الأسبوع الجديد يفتح وفوقه سقفٌ وتحته أرضٌ مرسومان سلفاً", INK)
    svg += sm(Wd, H, "وهما ما يُقاس عليه، لا خطٌّ ترسمه صباح الاثنين", TEAL_D)
    return svg + badge(Wd, "النحاس · يومي", True) + "</svg>"


def a_break(r=None, Wd=880, H=250):
    """وأربعةٌ من ستّة خرجت من الحدّين — والخروج مبكّر."""
    svg, x, y, slot = _ga(Wd, H)
    for n in A_OUT:
        up, dn = A_BRK[n]
        j = up or dn
        col = TEAL_D if up else RED
        ph, pl = A_HL[n - 1]
        svg += hl(x(A_WK[n - 1][0]) - slot * .4, x(j) + slot * .6,
                  y(ph if up else pl), col, 1.8, "6 5")
        svg += mark(x(j), slot, y(WA[j]["h"]), y(WA[j]["l"]), col, 0.20)
    svg += RC._title(Wd, rt("أربعةٌ من ستّة خرجت"))
    svg += why(Wd, H, f'{ar(len(A_OUT))} أسابيع كسرت حدَّ سابقها و{ar(len(A_IN))} بقيت داخله', TEAL_D)
    svg += sm(Wd, H, "فالحدّ ليس جداراً — هو أوّلُ سؤالٍ يُسأل")
    return svg + badge(Wd, "النحاس · يومي", True) + "</svg>"


def a_early(r=None, Wd=880, H=250):
    """والكسر يقع في اليوم الأول أو الثاني — أربعٌ من أربع."""
    svg, x, y, slot = _ga(Wd, H)
    for n in A_OUT:
        up, dn = A_BRK[n]
        j = up or dn
        svg += mark(x(j), slot, y(WA[j]["h"]), y(WA[j]["l"]),
                    TEAL_D if up else RED, 0.22)
        svg += _lab(x(j), y(min(WA[i]["l"] for i in A_WK[n])) + 30,
                    rt(f'اليوم {ar(A_DAY[n])}'), GREY, 17)
    svg += RC._title(Wd, rt("والخروج يقع باكراً"))
    svg += why(Wd, H, f'{ar(len(A_EARLY))} من {ar(len(A_OUT))} وقعت في اليوم الأوّل أو الثاني', TEAL_D)
    svg += sm(Wd, H, "فمن ينتظر منتصف الأسبوع يقرأ خبراً لا فرصة")
    return svg + badge(Wd, "النحاس · يومي", True) + "</svg>"


def a_inside(r=None, Wd=880, H=250):
    """واثنان بقيا داخل الحدّين — أسبوعٌ بلا قرار."""
    svg, x, y, slot = _ga(Wd, H)
    for n in A_IN:
        ph, pl = A_HL[n - 1]
        g = A_WK[n]
        svg += band(x(g[0]) - slot * .5, x(g[-1]) + slot * .5, y(ph), y(pl), GREY, 0.16)
        svg += hl(x(g[0]) - slot * .5, x(g[-1]) + slot * .5, y(ph), INK, 1.6, "5 5")
        svg += hl(x(g[0]) - slot * .5, x(g[-1]) + slot * .5, y(pl), INK, 1.6, "5 5")
    svg += RC._title(Wd, rt("واثنان لم يخرجا"))
    svg += why(Wd, H, f'{ar(len(A_IN))} أسبوعان مرّا كاملين داخل حدّي سابقهما', GREY)
    svg += sm(Wd, H, "وهذان أسبوعا انتظارٍ لا أسبوعا صبرٍ على صفقة", TEAL_D)
    return svg + badge(Wd, "النحاس · يومي", True) + "</svg>"


def a_all(r=None, Wd=880, H=250):
    """النافذة كاملة — حدود كل أسبوع على أسبوعه."""
    assert len(WA) == 34, len(WA)
    svg, x, y, slot = _ga(Wd, H)
    for n, g in enumerate(A_WK):
        h, l = A_HL[n]
        svg += hl(x(g[0]) - slot * .5, x(g[-1]) + slot * .5, y(h), INK, 1.5)
        svg += hl(x(g[0]) - slot * .5, x(g[-1]) + slot * .5, y(l), INK, 1.5)
    svg += RC._title(Wd, rt("النافذة كاملة"))
    svg += why(Wd, H, f'{ar(len(WA))} شمعة يومية · {ar(len(A_WK) - 1)} أسابيع بحدودها', INK)
    svg += sm(Wd, H, "ومدى الأسبوع بين ١٫٧ و٤٫٥ أضعاف اليوم الاعتيادي")
    return svg + badge(Wd, "النحاس · يومي", True) + "</svg>"




# ═════════ ٢ · أخبار — شمعة الخبر (أساسية · مثال تخطيطي) ═════════
B_SEED = 7349
B_ANCH = [(0, 40.0), (7, 40.4), (13, 40.1), (15, 41.6), (21, 40.9), (28, 41.4)]
B_N = 29
B_NEWS = 14                   # شمعة الخبر


def _series_b():
    return gen(B_ANCH, B_N, B_SEED, wick=0.6, bn=0.6)


WB = _series_b()
RB = {"sym": "SCHEMATIC-N", "slug": "مثال تخطيطي — خبر", "w": WB}
_B_R = [c["h"] - c["l"] for c in WB]
_B_MED = st.median(_B_R)
B_K = _B_R[B_NEWS] / _B_MED
_c = WB[B_NEWS]
B_UP = (_c["h"] - max(_c["o"], _c["c"])) / _B_R[B_NEWS]
B_DN = (min(_c["o"], _c["c"]) - _c["l"]) / _B_R[B_NEWS]
B_QUIET = [i for i in range(B_NEWS - 6, B_NEWS) if _B_R[i] < _B_MED * 0.9]
# مدى الهدوء قبل الخبر: أعلى قمّة وأدنى قاع في الشمعات الستّ السابقة.
B_PH = max(WB[i]["h"] for i in range(B_NEWS - 6, B_NEWS))
B_PL = min(WB[i]["l"] for i in range(B_NEWS - 6, B_NEWS))
# أوّل شمعة بعد الخبر عاد إغلاقها داخل مدى الهدوء.
B_BACK = next((j for j in range(B_NEWS + 1, B_N) if B_PL <= WB[j]["c"] <= B_PH), None)
# الحدّ يحرس المعنى لا رقماً بعينه: شمعة الخبر يجب أن تكون أضعاف الوسيط
# (وإلا فلا «خبر»)، ودون ستّة أضعاف كي تبقى بقيّة السلسلة مقروءة على
# اللوحة. والرقم المكتوب في النصّ هو المقيس لا المطلوب.
assert 2.6 <= B_K <= 6.0, f"مدى شمعة الخبر {B_K:.2f}"
assert B_UP >= 0.22 and B_DN >= 0.22, (B_UP, B_DN)
assert len(B_QUIET) >= 4, len(B_QUIET)
assert B_BACK is not None, "السعر لم يعد داخل مدى الهدوء"
# الأكبر في السلسلة كلّها لا فيما قبلها وحدها: البذرة الأولى (8868) كانت
# تجعل شمعة الخبر أكبر من سابقاتها فقط، فتظهر بعدها شمعاتٌ أطول منها
# ويقرأ الناظر عكسَ ما يقول السطر — رُصد بالفحص البصري 2026-09-08.
assert _B_R[B_NEWS] == max(_B_R), "شمعة الخبر ليست الأكبر في السلسلة"
assert _B_R[B_NEWS] / sorted(_B_R)[-2] >= 1.25, "شمعة الخبر لا تتميّز عن ثانيتها"


def _gb(Wd, H):
    return frame(WB, Wd, H, pad=0.09, pb=64)


def n_quiet(r=None, Wd=880, H=250):
    """قبل الخبر: مدىً ضيّق وشمعات أصغر من المعتاد."""
    a, b = B_NEWS - 6, B_NEWS - 1
    svg, x, y, slot = _gb(Wd, H)
    svg += band(x(a) - slot * .5, x(b) + slot * .5, y(B_PH), y(B_PL), TEAL, 0.13)
    svg += spanx(x(a) - slot * .5, x(b) + slot * .5, y(B_PH), f'{ar(6)} شمعات', GREY)
    svg += RC._title(Wd, rt("الهدوء الذي يسبقه"))
    svg += why(Wd, H, f'{ar(len(B_QUIET))} من ست شمعات مداها دون وسيط السلسلة', GREY)
    svg += sm(Wd, H, "والسوق هنا لا يقرّر — ينتظر رقماً لم يصدر بعد", TEAL_D)
    return svg + badge(Wd, "مثال تخطيطي", True) + "</svg>"


def n_bar(r=None, Wd=880, H=250):
    """وشمعة الخبر: مدىً أضعافُ المعتاد وذيلان في الجهتين."""
    svg, x, y, slot = _gb(Wd, H)
    svg += mark(x(B_NEWS), slot, y(WB[B_NEWS]["h"]), y(WB[B_NEWS]["l"]), RED, 0.20)
    svg += vspan(x(B_NEWS) - slot * 2.6, y(WB[B_NEWS]["h"]), y(WB[B_NEWS]["l"]),
                 f'{xr(B_K)} الشمعة', INK, H=H)
    svg += RC._title(Wd, rt("شمعةٌ واحدة تبتلع أسبوعاً"))
    svg += why(Wd, H, f'مداها {xr(B_K)} وسيط السلسلة — وهي الأكبر فيها كلّها', RED)
    svg += sm(Wd, H, "ولا وقفَ يسع هذا المدى إلا وقفٌ يلغي الصفقة أصلاً")
    return svg + badge(Wd, "مثال تخطيطي", True) + "</svg>"


def n_wick(r=None, Wd=880, H=250):
    """وذيلاها يقولان إن الجهتين ضُربتا في شمعةٍ واحدة."""
    svg, x, y, slot = _gb(Wd, H)
    c = WB[B_NEWS]
    top, bot = max(c["o"], c["c"]), min(c["o"], c["c"])
    svg += mark(x(B_NEWS), slot, y(c["h"]), y(top), RED, 0.22)
    svg += mark(x(B_NEWS), slot, y(bot), y(c["l"]), RED, 0.22)
    svg += _lab(x(B_NEWS) - slot * 3.0, y(c["h"]) + 14, rt(f'{ar(round(B_UP*100))}٪ فوق'), RED, 18)
    svg += _lab(x(B_NEWS) - slot * 3.0, y(c["l"]) - 8, rt(f'{ar(round(B_DN*100))}٪ تحت'), RED, 18)
    svg += RC._title(Wd, rt("ذيلان لا ذيلٌ واحد"))
    svg += why(Wd, H, "الشمعة ضربت الجهتين قبل أن تغلق — فمن دخل قبلها خرج بأيّهما", RED)
    svg += sm(Wd, H, "والاتجاه الذي تراه بعدها ليس الاتجاه الذي عاشته", TEAL_D)
    return svg + badge(Wd, "مثال تخطيطي", True) + "</svg>"


def n_after(r=None, Wd=880, H=250):
    """ثم يعود السعر داخل مدى الهدوء بعد شمعاتٍ معدودة."""
    n = B_BACK - B_NEWS
    svg, x, y, slot = _gb(Wd, H)
    svg += hl(x(B_NEWS - 6) - slot * .5, x(B_N - 1) + slot * .5, y(B_PH), INK, 1.6, "5 6")
    svg += hl(x(B_NEWS - 6) - slot * .5, x(B_N - 1) + slot * .5, y(B_PL), INK, 1.6, "5 6")
    svg += mark(x(B_BACK), slot, y(WB[B_BACK]["h"]), y(WB[B_BACK]["l"]), TEAL_D, 0.22)
    svg += RC._title(Wd, rt("والعودة إلى ما قبله"))
    svg += why(Wd, H, f'{ar(n)} شمعات ورجع الإغلاق داخل مدى الهدوء نفسه', TEAL_D)
    svg += sm(Wd, H, "فالخبر حرّك السعر ولم يحرّك الحدّين — وهذا ما تتداوله")
    return svg + badge(Wd, "مثال تخطيطي", True) + "</svg>"


def n_all(r=None, Wd=880, H=250):
    """السلسلة كاملة — مرجع كل رقمٍ في الوحدة."""
    assert len(WB) == B_N, len(WB)
    svg, x, y, slot = _gb(Wd, H)
    svg += hl(x(0) - slot * .5, x(B_N - 1) + slot * .5, y(B_PH), GREY, 1.4, "5 6")
    svg += hl(x(0) - slot * .5, x(B_N - 1) + slot * .5, y(B_PL), GREY, 1.4, "5 6")
    svg += RC._title(Wd, rt("السلسلة كاملة"))
    svg += why(Wd, H, f'{ar(B_N)} شمعة تخطيطية — والأرقام أعدادٌ ونِسب', INK)
    svg += sm(Wd, H, "ولا سعرَ مكتوبٌ هنا، فالرسم تخطيطي لا طبعةُ سوق")
    return svg + badge(Wd, "مثال تخطيطي", True) + "</svg>"


SETS = {"usbou3i": [a_bounds, a_break, a_early, a_inside, a_all],
        "akhbar": [n_quiet, n_bar, n_wick, n_after, n_all]}
WINS = {"usbou3i": _R, "akhbar": RB}
REAL = {"usbou3i": WIN_A}
SYN = {"akhbar": (B_SEED, B_ANCH)}


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
