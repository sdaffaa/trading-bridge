# -*- coding: utf-8 -*-
"""جارتات تشغيلة ٣٤ — **تخطيطية** لا سوق حقيقي.

مخزون النوافذ الحقيقية في `sheet_candidates.json` نفد: ثماني نوافذ صالحة
كلّها مسجّلة في `used_charts.json`، وستّ موسومة بالفساد. و§180 يحكم هذه
الحالة بالضبط: تُبنى الوحدة **بجارتات تخطيطية** ويُذكر أن سلايد السوق
الحقيقي مؤجَّل حتى تُعبَّأ النوافذ.

ولأن التخطيطي ليس رخصةً للكذب، تحكم الملفَ قاعدتان:

1. **الشارة تقول ما هو**: كل جارت يحمل «مثال تخطيطي» صراحةً، فلا يُقرأ
   كطبعة سوق.
2. **ما لا تُثبته الشموع لا يُرسم** — نفس قاعدة `run31_charts`: كل ادّعاء
   يُقاس على السلسلة المولّدة بـ`assert` قبل أن يُرسم. والقياسات تُذكر
   **بالنِّسب** لا بالنقاط، لأن السلسلة بلا أداة فلا وحدة لها.
"""
from reel_build import INK, TEAL, TEAL_D, RED, GREY, htext, gen
from run15_charts import zbox, xm, tick, hl, badge, frame
import run31_charts as RC

SEED = 3417
ANCH = [(0, 10.2), (6, 14.6), (10, 12.95), (13, 13.0), (17, 14.4),
        (21, 12.9), (23, 13.4), (29, 17.2)]
N = 30

# القاعان المتساويان وشمعة السحب تُثبَّت بتحرير الفتائل وحدها — كما يفعل
# `gen` مع `swings` — فتبقى سلسلة الفتح/الإغلاق متّصلة كما ولّدها المحرّك.
P1, P2, SWP = 10, 13, 22
LVL = 12.30
DEEP = 11.80


def _series():
    cs = gen(ANCH, N, SEED, wick=0.55, bn=0.6)
    for j in (P1, P2):
        cs[j]["l"] = LVL
        cs[j]["h"] = max(cs[j]["h"], max(cs[j]["o"], cs[j]["c"]) + 0.15)
    cs[SWP]["l"] = DEEP
    # لا فتيل آخر ينزل تحت المستوى بين القاعين وقمة الحركة — ولا يُرفع قاع
    # فوق جسم شمعته أبداً، وإلا خرجت شمعة مستحيلة تفضح التخطيطي.
    for j in range(P1 + 1, N):
        if j in (P2, SWP):
            continue
        cs[j]["l"] = min(max(cs[j]["l"], LVL + 0.04), min(cs[j]["o"], cs[j]["c"]))
    for j, c in enumerate(cs):               # فتائل معقولة: لا شوكات طويلة
        top, bot = max(c["o"], c["c"]), min(c["o"], c["c"])
        c["h"] = min(c["h"], top + 0.9)
        if j not in (P1, P2, SWP):           # الثلاثة فتائلها هي القصّة
            c["l"] = max(c["l"], bot - 0.9)
    return cs


W = _series()
R = {"sym": "SCHEMATIC", "w": W}

# التحقّق يسبق الرسم: لو انزاحت السلسلة بتعديل مرتقب، ينكسر البناء بصوتٍ
# عالٍ بدل أن يخرج جارت يقول ما لا تقوله شموعه.
assert abs(W[P1]["l"] - W[P2]["l"]) < 1e-9, "القاعان غير متساويين"
assert W[SWP]["l"] < LVL, "شمعة السحب لم تنزل تحت القاعين"
assert W[SWP]["c"] > LVL, "شمعة السحب لم تغلق فوق القاعين"
assert min(W[j]["l"] for j in range(P1 + 1, SWP)) >= LVL, "قاع آخر يسبق السحب"
TOP = max(range(SWP, N), key=lambda j: W[j]["h"])
assert W[TOP]["h"] > W[SWP]["c"], "لا حركة صاعدة بعد الإغلاق"

SW_DEPTH = LVL - W[SWP]["l"]                       # عمق الفتيل تحت المستوى
RUN_UP = W[TOP]["h"] - W[SWP]["c"]                 # الحركة بعد الإغلاق
# النسبة تُقاس بالمخاطرة لا بعمق الفتيل: الوقف تحت فتيل السحب هو المكان
# الوحيد الذي ينقض الفكرة إن ضُرب، فهو مقام النسبة الصادق.
RISK = W[SWP]["c"] - W[SWP]["l"]
RR = RUN_UP / RISK


def _ar(v, d=1):
    return (f"%.{d}f" % v).replace(".", "٫").translate(str.maketrans("0123456789", "٠١٢٣٤٥٦٧٨٩"))


def _t(Wd, txt, col=INK):
    return RC._title(Wd, txt, col)


def _w(Wd, H, txt, col=INK):
    return RC._why(Wd, H, txt, col)


def _s(Wd, H, txt):
    return RC._sum(Wd, H, txt)


def _geo(Wd, H):
    return frame(W, Wd, H)


def _lab(x, y, txt, col, fs=19):
    """وسم على الجارت — يختفي في وضع الغلاف كبقية النصوص.

    الغلاف يعرض الجارت بعرض ٧٠٠ تحت عنوان ضخم، فالوسوم عليه تصير حَشواً
    غير مقروء؛ و`htext` المباشر لا يعرف بوضع الغلاف فيرسمها رغم ذلك."""
    import run15_charts as R15
    if R15.MINIMAL:
        return ""
    return htext(x, y, txt, col, round(fs * RC._SC[0]))


def _mark(x, y, col, r=12, sw=3):
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="none" stroke="{col}" stroke-width="{sw}"/>'


# ═══════════ الحالات ═══════════
def s_equal(Wd=880, H=250):
    """١ · قاعان متساويان: سيولة معلّقة يراها الجميع بالطريقة نفسها."""
    svg, x, y, slot = _geo(Wd, H)
    svg += hl(x(P1) - slot * .8, x(min(SWP + 4, N - 1)), y(LVL), INK, 2.0)
    for j in (P1, P2):
        svg += _mark(x(j), y(W[j]["l"]), GREY, 9, 2.2)
    svg += _lab((x(P1) + x(P2)) / 2, y(LVL) + round(28 * RC._SC[0]),
                "قاعان متساويان", INK)
    svg += _t(Wd, "قاعان متساويان = أوامر متجمّعة تحتهما")
    svg += _w(Wd, H, "هني تحت الخط تنام أوامر الوقف", INK)
    svg += _s(Wd, H, "قبل أن يتحرّك السعر، الجميع يرى الصورة نفسها")
    return svg + badge(Wd, "مثال تخطيطي", True) + "</svg>"


def s_break(Wd=880, H=250):
    """٢ · الكسر الذي يوافق الرأي الهابط: فتيل تحت القاعين."""
    svg, x, y, slot = _geo(Wd, H)
    svg += hl(x(P1) - slot * .8, x(min(SWP + 4, N - 1)), y(LVL), INK, 2.0)
    for j in (P1, P2):
        svg += _mark(x(j), y(W[j]["l"]), GREY, 9, 2.2)
    svg += xm(x(SWP), y(W[SWP]["l"]))
    svg += hl(x(SWP) - slot * 1.4, x(SWP) + slot * 1.4, y(W[SWP]["l"]), RED, 1.6, "6 5")
    svg += _t(Wd, "النزول تحت المستوى يعطي الرأي تأكيده", RED)
    svg += _w(Wd, H, "هني أغروك تبيع — لأن اللي شفته وافق رأيك", RED)
    svg += _s(Wd, H, "لكن الفتيل تحت المستوى محاولة… والإغلاق هو الحكم")
    return svg + badge(Wd, "مثال تخطيطي", False) + "</svg>"


def s_close(Wd=880, H=250):
    """٣ · الإغلاق فوق القاعين — الإشارة المعاكسة، والحركة بعدها. (البطل)"""
    svg, x, y, slot = _geo(Wd, H)
    svg += hl(x(P1) - slot * .8, x(TOP) + slot * .5, y(LVL), INK, 2.0)
    for j in (P1, P2):
        svg += _mark(x(j), y(W[j]["l"]), GREY, 9, 2.2)
    svg += _lab((x(P1) + x(P2)) / 2, y(LVL) + round(28 * RC._SC[0]),
                "قاعان متساويان", INK)
    svg += xm(x(SWP), y(W[SWP]["l"]))
    svg += _mark(x(SWP), y(W[SWP]["c"]), TEAL_D)
    # بلا وسم عائم عند شمعة السحب: فوقها ويمينها تمرّ الحركة الصاعدة،
    # وتحتها علامة السحب نفسها — فأي نص هناك يدوس أحدهما. الصورة تكفي:
    # علامة عند قاع الفتيل، وحلقة عند الإغلاق، والفتيل يصل بينهما.
    svg += tick(x(TOP), y(W[TOP]["h"]) - 18)
    svg += _t(Wd, "الإغلاق فوق القاع يُلغي الكسر الذي تحته", TEAL_D)
    svg += _w(Wd, H, "هني الإشارة اللي تعاكسك — ولذلك رفضتها", TEAL_D)
    svg += _s(Wd, H, f"من الإغلاق إلى القمة ≈ {_ar(RR)} ضعف المخاطرة "
                     f"(الوقف تحت فتيل السحب)")
    return svg + badge(Wd, "مثال تخطيطي", True) + "</svg>"


def s_late(Wd=880, H=250):
    """٤ · التأكيد الزائد: تأجيل القبول حتى يمضي نصف الحركة."""
    late = SWP + max(2, (TOP - SWP) // 2)
    assert late < TOP, "لا مسافة بين الدخول المتأخر والقمة"
    lost = W[late]["c"] - W[SWP]["c"]
    assert lost > 0, "الدخول المتأخر ليس أعلى من الإغلاق"
    svg, x, y, slot = _geo(Wd, H)
    svg += hl(x(P1) - slot * .8, x(TOP) + slot * .5, y(LVL), INK, 2.0)
    svg += _mark(x(SWP), y(W[SWP]["c"]), TEAL_D, 11, 2.4)
    svg += _mark(x(late), y(W[late]["c"]), RED)
    svg += hl(x(SWP) - slot * .6, x(TOP) + slot * .5, y(W[TOP]["h"]), INK, 1.6, "7 6")
    svg += _t(Wd, "كل تأكيد إضافي يُشترى بجزء من الحركة", RED)
    svg += _w(Wd, H, "هني دخلت متأخر — لأنك طلبت تأكيداً بعد التأكيد", RED)
    svg += _s(Wd, H, f"ضاع نحو {_ar(lost / RUN_UP * 100, 0)}٪ من الحركة قبل أن تقتنع")
    return svg + badge(Wd, "مثال تخطيطي", False) + "</svg>"


CASES = [s_close, s_equal, s_break, s_late]      # البطل أولاً: غلافٌ وصفحةُ بطل

if __name__ == "__main__":
    print(f"عمق الفتيل {SW_DEPTH:.2f} · الحركة {RUN_UP:.2f} · العائد/المخاطرة {RR:.2f} · قمة {TOP}")
    for f in CASES:
        f(880, 250); print("✓", f.__name__)
