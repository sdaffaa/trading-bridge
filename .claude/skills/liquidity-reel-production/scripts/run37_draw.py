# -*- coding: utf-8 -*-
"""تشغيلة ٣٧ — ريل «الصفقة تنرسم جدامك»: صامت، خمسة توكنز، ٢٢ ثانية.

🔒 بريف فهد 2026-08-08. ما يميّزه عن كل ريلاتنا السابقة ثلاثة:
  · **بلا نصّ منطوق وبلا موسيقى** — مؤثرات فقط، وصمتٌ حقيقي بينها.
  · **بلا لغة على الشاشة** إلا خمسة توكنز إنجليزية: `$$$` · `ORDER BLOCK`
    · `SELL/BUY` · `STOP LOSS` · `TAKE PROFIT`. سببُ المنع في البريف:
    خلوّ الفيديو من اللغة أكبر مضاعف وصول، وأي جملة تقفل أسواقاً.
  · **لوب**: الإطار الأخير يطابق الصفر زاويةً وتكبيراً — ولذلك `cam=[]`
    (قرار فهد: «اللوب أهم — بلا بوش»).

والخط الزمني ليس اقتراحاً: كل سطر في `BEATS` يقابل سطراً في جدول البريف،
ويفحصه `_gate()` قبل البناء — مدّة ≤٢٢، وتغيّر بصري كل ≤١٫٥ ثانية، ودفعة
الوصول في آخر ١٥٪، وCTA واحد بعد الثانية ١٦.

الشموع تُقرأ من تصدير المتداول عبر `xau_load` ولا تُولَّد أبداً. وأسعار
الصفقة الأربعة تُمرَّر ولا تُستنتج: هذا ريلُ صفقةٍ يحدّدها فهد لا نافذةٍ
يقبلها ماسح.

    LS_DATA=xau.csv LS_TF=15m LS_SYM="XAUUSD" LS_DIR=SELL \\
    LS_ENT=… LS_STP=… LS_TGT=… LS_LIQ=… LS_KW=صفقة python3 run37_draw.py
"""
import os
import sys

from reel_build import INK, TEAL, TEAL_D, RED, htext
from reel_sfx_kit import (build_reel, line_el, set_canvas, set_pad,
                          set_price_pad, set_vis)
import tv_chart
import xau_load

HERE = os.path.dirname(os.path.abspath(__file__))
tv_chart.set_theme("light")

# ═══════════ اللوحة ═══════════
CVW, CVH = 1080, 1560
set_canvas(CVW, CVH)
set_pad(20, 128, 96, 84)
PL, PR, PT, PB = 20, 128, 96, 84
PW, PH = CVW - PL - PR, CVH - PT - PB
CX, CY = 0, 200                       # ركن الجارت داخل إطار 1080×1920
DUR = 22.0                            # سقف البريف المطلق ٢٣ — نلتزم ٢٢ بالضبط
FPS = 60                              # بريف التسليم

# ═══════════ المدخلات ═══════════
def _env(k, cast=str, req=True, default=None):
    v = os.environ.get(k)
    if v is None or v == "":
        if req:
            sys.exit(f"✗ ينقص المتغيّر {k} — البريف يوجب التوقّف لا التخمين")
        return default
    return cast(v)


DATA = _env("LS_DATA")
TF = _env("LS_TF", default="15m", req=False)
SYM = _env("LS_SYM", default="XAUUSD", req=False)
DIRN = _env("LS_DIR").upper()
assert DIRN in ("SELL", "BUY"), "LS_DIR = SELL أو BUY"
ENT = _env("LS_ENT", float)
STP = _env("LS_STP", float)
TGT = _env("LS_TGT", float)
LIQ = _env("LS_LIQ", float)
KW = _env("LS_KW", req=False, default="")     # كلمة الـCTA العربية

W, REP = xau_load.load(os.path.join(HERE, DATA) if not os.path.isabs(DATA) else DATA, TF)
xau_load.assert_levels(W, entry=ENT, stop=STP, target=TGT, liquidity=LIQ)

SELL = DIRN == "SELL"
# اتّساق الاتجاه: في البيع الوقف فوق الدخول والهدف تحته، وفي الشراء العكس.
# رقمٌ مقلوب هنا يعني صفقة مستحيلة تُرسم بثقة — فيُفحص لا يُفترض.
if SELL:
    assert STP > ENT > TGT, f"بيع: يجب STP({STP}) > ENT({ENT}) > TGT({TGT})"
else:
    assert STP < ENT < TGT, f"شراء: يجب STP({STP}) < ENT({ENT}) < TGT({TGT})"
DP = 2 if max(c["h"] for c in W) > 100 else 4

# ═══════════ الهندسة ═══════════
# الشموع تتحرّك آخر ثلاث ثوانٍ (18→21)، فالنافذة أطول من المعروض
# والإزاحة اليمنى عشرة سلوتات كما ضُبطت في ريل التحليل (أمر فهد).
BARS_LIVE = 8                          # شمعات تُطبع في نافذة الحركة
RP_OFF = 10                            # مدرَج فارغ يمين اللوحة (أمر فهد)
# **الجارت لا ينزلق في هذا الريل.** البريف يوجب أن يطابق الإطارُ الأخير
# الصفرَ زاويةً وتكبيراً، والانزلاق يغيّر التأطير فيكسر اللوب. والمخرج
# ليس إلغاء الحركة: المدرَج الفارغ يمين اللوحة يتّسع للشمعات الثماني،
# فتُطبع فيه بلا أن يتحرّك الإطار — وهو ما يفعله الريبلاي حين تكون
# الإزاحة اليمنى أوسع من عدد الشمعات القادمة.
VIS = len(W) + RP_OFF
ANCHOR = len(W) - 1                    # المرساة عند آخر شمعة ⇐ الإزاحة صفر دائماً
RP_BASE = len(W) - 1 - BARS_LIVE       # أول شمعة تُطبع حيّة
assert RP_BASE > 5, "النافذة أقصر من أن تُطبع منها ثماني شمعات"
set_vis(VIS)
set_price_pad(1.25, 0.08)


def geo():
    lo = min(c["l"] for c in W); hi = max(c["h"] for c in W)
    pad = (hi - lo) * 0.08
    ymin, ymax = lo - pad * 1.25, hi + pad
    slot = PW / VIS
    return (lambda i: PL + slot * i + slot / 2,
            lambda p: PT + (ymax - p) / (ymax - ymin) * PH, slot)


X, Y, SLOT = geo()
RSHIFT = SLOT * (len(W) - 1 - ANCHOR)
R = CVW - PR + RSHIFT                  # يبلغ حافة المحور بعد الانزلاق كذلك

# الأوردر بلوك: الشمعة المعاكسة الأخيرة قبل الاندفاع — تُشتقّ من الدخول
# لا تُختار بالنظر. حدّها الذي يلمسه السعر هو سعر الدخول نفسه.
FILL = min(range(len(W)), key=lambda i: abs(W[i]["c"] - ENT))
_OB = [i for i in range(max(0, FILL - 14), FILL)
       if (W[i]["c"] > W[i]["o"]) == SELL]        # بيع ← شمعة صاعدة
assert _OB, "لا شمعة معاكسة قبل الدخول — الأوردر بلوك لا يُشتقّ"
IOB = _OB[-1]
OB_HI, OB_LO = max(W[IOB]["o"], W[IOB]["c"]), min(W[IOB]["o"], W[IOB]["c"])
HIT = next((i for i in range(FILL + 1, len(W))
            if (W[i]["l"] <= TGT if SELL else W[i]["h"] >= TGT)), len(W) - 1)


# ═══════════ الخط الزمني — سطراً بسطر من جدول البريف ═══════════
T_LIQ, T_LIQ_E = 0.50, 3.00
T_DOL = 3.00
T_BOX, T_BOX_E = 4.50, 8.00
T_OBL = 8.00
T_SIDE = 9.50
T_STP, T_STP_E = 11.50, 14.50
T_TGT, T_TGT_E = 14.50, 18.00
T_RUN, T_RUN_E = 18.00, 21.00
T_ARR = 21.00
T_CTA = 19.00                          # البريف: لا CTA قبل ١٦


def markup():
    """كل عنصر في مجموعته، ويُرسم بالترتيب الذي يفرضه الجدول."""
    ex = []
    # ١) خط السيولة — يُرسم من اليسار إلى اليمين بسرعة ثابتة
    ex.append(line_el(PL, Y(LIQ), R, Y(LIQ), INK, 3.0, id="liq"))
    # ٢) `$$$` تحت الخط (بيع: السيولة فوق فالرمز تحتها مباشرة)
    ex.append(f'<g id="dol" opacity="0">'
              + htext(X(max(0, FILL - 16)), Y(LIQ) + (34 if SELL else -18),
                      "$$$", INK, 44) + '</g>')
    # ٣) بوكس الأوردر بلوك — أربعة أضلاع تُرسم واحداً واحداً
    bx0, bx1 = X(IOB) - SLOT * .6, X(min(HIT + 2, len(W) - 1))
    yt, yb = Y(OB_HI), Y(OB_LO)
    for n, (a, b, c, d) in enumerate((
            (bx0, yt, bx1, yt), (bx1, yt, bx1, yb),
            (bx1, yb, bx0, yb), (bx0, yb, bx0, yt))):
        ex.append(line_el(a, b, c, d, TEAL_D, 3.0, id=f"ob{n}"))
    ex.append(f'<g id="obfill" opacity="0"><rect x="{bx0:.1f}" y="{yt:.1f}" '
              f'width="{bx1-bx0:.1f}" height="{yb-yt:.1f}" fill="{TEAL}" '
              f'fill-opacity=".12"/></g>')
    # ٤) ليبل ORDER BLOCK
    ex.append(f'<g id="obl" opacity="0">'
              + htext((bx0 + bx1) / 2, yb + 40, "ORDER BLOCK", TEAL_D, 30) + '</g>')
    # ٥) توكن الاتجاه عند حافة البوكس التي يلمسها السعر
    ey = Y(ENT)
    ex.append(f'<g id="side" opacity="0">'
              f'<rect x="{bx0-172:.1f}" y="{ey-27:.1f}" width="150" height="54" '
              f'fill="{RED if SELL else TEAL_D}" rx="2"/>'
              + htext(bx0 - 97, ey + 11, DIRN, "#FFFFFF", 32) + '</g>')
    # ٦) الوقف — خط متقطّع فوق البوكس (بيع)
    ex.append(line_el(bx0, Y(STP), R, Y(STP), RED, 2.6, dash="10 8", id="stp"))
    ex.append(f'<g id="stpl" opacity="0">'
              + htext(bx0 + 176, Y(STP) - 16, "STOP LOSS", RED, 28) + '</g>')
    # ٧) الهدف — خط متقطّع تحته
    ex.append(line_el(bx0, Y(TGT), R, Y(TGT), TEAL_D, 2.6, dash="10 8", id="tgt"))
    ex.append(f'<g id="tgtl" opacity="0">'
              + htext(bx0 + 196, Y(TGT) + 36, "TAKE PROFIT", TEAL_D, 28) + '</g>')
    return "".join(ex)


MARKS = [
    ("liq", T_LIQ, T_LIQ_E, "draw"),
    ("dol", T_DOL, T_DOL + 0.55, "pop"),
    ("ob0", T_BOX, T_BOX + 0.90, "draw"), ("ob1", T_BOX + 0.85, T_BOX + 1.75, "draw"),
    ("ob2", T_BOX + 1.70, T_BOX + 2.60, "draw"), ("ob3", T_BOX + 2.55, T_BOX_E, "draw"),
    ("obfill", T_BOX_E - 0.30, T_BOX_E + 0.20, "fade"),
    ("obl", T_OBL, T_OBL + 0.60, "pop"),
    ("side", T_SIDE, T_SIDE + 0.60, "pop"),
    ("stp", T_STP, T_STP + 1.60, "draw"), ("stpl", T_STP + 1.55, T_STP + 2.15, "pop"),
    ("tgt", T_TGT, T_TGT + 2.00, "draw"), ("tgtl", T_TGT + 1.95, T_TGT + 2.60, "pop"),
]
FULLSET = ["dol", "obfill", "obl", "side", "stpl", "tgtl"]
DRAWSET = ["liq", "ob0", "ob1", "ob2", "ob3", "stp", "tgt"]

# الشموع: ساكنة حتى ١٨ ثم تُطبع ثمانٍ حتى ٢١، ثم تثبت للوب
RP_KF = [[0.0, RP_BASE], [T_RUN, RP_BASE], [T_RUN_E, len(W) - 1], [DUR, len(W) - 1]]

# ═══════════ المؤثرات — سبع سحبات قلم بالضبط + تِك لكل شمعة + ضربة ═══════════
# سبع سحبات بالضبط، واحدة لكل عنصر يُرسم: السيولة · $$$ · البوكس ·
# ORDER BLOCK · توكن الاتجاه · الوقف · الهدف. والصمت بينها يبقى صمتاً.
SFX = [("pen_l", T_LIQ, -2), ("pen_s", T_DOL, -5), ("pen_l", T_BOX, -3),
       ("pen_s", T_OBL, -5), ("pen_s", T_SIDE, -5),
       ("pen_m", T_STP, -3), ("pen_m", T_TGT, -3)]
assert len(SFX) == 7, "البريف: سبعة مؤثرات قلم بالضبط"
_STEP = (T_RUN_E - T_RUN) / BARS_LIVE
SFX += [("tick", round(T_RUN + _STEP * (i + 1), 2), -9) for i in range(BARS_LIVE)]
SFX += [("thump", T_ARR, 0)]


# ═══════════ المؤشر ═══════════
# «ما فيه إطار واحد ساكن — الكيرسر أو الشموع لازم تكون بحركة ١٠٠٪ من
# الوقت» (البريف). والشموع ساكنة حتى ١٨، فالمؤشر هو الحركة قبلها: يسحب
# كل عنصر بيده ثم ينتقل إلى التالي. `ss` تيسيرٌ بشري، و`lin` على شقّ
# السحب وحده لأن الرسم خطّي في الزمن.
FX = lambda i: CX + X(i)
FY = lambda p: CY + Y(p)
_bx0, _bx1 = FX(IOB) - SLOT * .6, FX(min(HIT + 2, len(W) - 1))
_yt, _yb = FY(OB_HI), FY(OB_LO)
CURSOR = [
    [0.00, CX + PL - 40, FY(LIQ) - 26, "ss"],
    [T_LIQ, CX + PL, FY(LIQ), "ss"],
    [T_LIQ_E, CX + R - RSHIFT, FY(LIQ), "lin"],           # سحب خط السيولة
    [T_DOL, FX(max(0, FILL - 16)), FY(LIQ) + (34 if SELL else -18), "ss", "down"],
    [T_BOX, _bx0, _yt, "ss"],
    [T_BOX + 0.90, _bx1, _yt, "lin"],                     # الضلع العلوي
    [T_BOX + 1.75, _bx1, _yb, "lin"],                     # الأيمن
    [T_BOX + 2.60, _bx0, _yb, "lin"],                     # السفلي
    [T_BOX_E, _bx0, _yt, "lin"],                          # الأيسر
    [T_OBL, (_bx0 + _bx1) / 2, _yb + 40, "ss", "down"],
    [T_SIDE, _bx0 - 97, FY(ENT), "ss", "down"],
    [T_STP, _bx0, FY(STP), "ss"],
    [T_STP + 1.60, CX + R - RSHIFT, FY(STP), "lin"],      # سحب خط الوقف
    [T_TGT, _bx0, FY(TGT), "ss"],
    [T_TGT + 2.00, CX + R - RSHIFT, FY(TGT), "lin"],      # سحب خط الهدف
    [T_RUN, CX + PL + 60, FY(LIQ) - 60, "creep"],         # يبتعد فتبقى الشموع وحدها
    [DUR, CX + PL - 40, FY(LIQ) - 26, "creep"],           # ويعود لموضع الإطار صفر — لوب
]


def _gate():
    """بوابة ما قبل الإنتاج — بنودها من البريف حرفياً."""
    assert DUR <= 22.0, f"المدّة {DUR} > ٢٢"
    # التغيّر البصري **مدّة لا لحظة**: خطٌّ يُسحب في ثانيتين تغيّرٌ طوالهما،
    # فالفحص على فجوات ما بين فترات النشاط لا ما بين بداياتها. (أول صياغة
    # قاست البدايات فرسبت على خط الهدف — وهو يُرسم بلا انقطاع.)
    act = [(m[1], m[2]) for m in MARKS] + [(T_RUN, T_RUN_E), (T_CTA, T_CTA + 0.45)]
    act.sort()
    merged = [list(act[0])]
    for a, b in act[1:]:
        if a <= merged[-1][1] + 1e-9:
            merged[-1][1] = max(merged[-1][1], b)
        else:
            merged.append([a, b])
    holes = [(merged[i][1], merged[i + 1][0]) for i in range(len(merged) - 1)]
    holes.append((0.0, merged[0][0]))
    worst = max(((b - a), a, b) for a, b in holes)
    assert worst[0] <= 1.5 + 1e-9, \
        f"نافذة {worst[0]:.2f}s بلا عنصر جديد ({worst[1]:.2f}→{worst[2]:.2f}) — الحدّ ١٫٥"
    assert merged[-1][1] <= DUR + 1e-9, "عنصر يتجاوز نهاية الريل"
    assert T_ARR >= DUR * 0.85, "دفعة الوصول ليست في آخر ١٥٪ من المدّة"
    assert T_CTA >= 16.0, "CTA قبل الثانية ١٦"
    assert RP_KF[0][1] == RP_KF[1][1] and RP_KF[-1][1] == len(W) - 1


_gate()

CSS = """
#chartclip{top:%dpx;left:%dpx}
#chip{display:none} #res{display:none} #endlogo{display:none} #edu{display:none}
/* تحت وسوم الوقت لا فوقها: البريف يوجب ألّا يغطّي الـCTA الشموع، ووسوم
   الساعة جزء من الجارت. */
#cta{top:1806px;left:80px;right:80px}
#cta .k{font-size:38px;padding:12px 34px;border-width:2px}
#cta .s{display:none}
""" % (CY, CX)

cfg = dict(
    w=W, dark=False, extra_css=CSS, grid=False,
    extra_html="",                          # لا عنوان ولا كارد — بريف فهد
    pre_svg=None, scroll_svg=None,          # يُملآن أدناه
    lp_pill=True, lp_dec=DP, lp_col=tv_chart.T["PILL"], lp_txt=tv_chart.T["PILLTX"],
    base=RP_BASE - 1, openmax=RP_BASE - 1, open_t=[[RP_BASE - 1, 0.3]], story=[],
    extra_svg=markup(), overlay_svg="",
    replay={"kf": RP_KF, "vis": ANCHOR},
    marks=MARKS, fullset=FULLSET, drawset=DRAWSET, dom_marks=[],
    cursor=CURSOR, crosshair=False, chart_at=(CX, CY),
    tlabels=[c["d"] for c in W],
    preview_a=0.0, preview_b=0.0, res_tease=False, sweep_op=0.0,
    txt=[], chip="", res="",
    cta_k=(f'اكتب «{KW}»' if KW else ""), cta_s="",
    edu="", dur=DUR, res_t=999, cta_t=T_CTA,
    flash=(0.0, 0.0), flash_op=0.0, punch=(0.0, 0.0, 0.0),
    cam=[],                                  # قرار فهد: اللوب أهم — بلا بوش
)
_F = tv_chart.furniture(W, dec=DP, sym=SYM, tf=TF,
                        tlabels=[c["d"] for c in W], split=True)
cfg["pre_svg"], cfg["scroll_svg"] = _F

if __name__ == "__main__":
    out = os.path.join(HERE, "reel37_draw.html")
    n = build_reel(cfg, out)
    print(f'✅ {SYM} · {TF} · {DIRN} — {REP["n"]} شمعة حقيقية '
          f'({REP["start"]} → {REP["end"]})\n'
          f'   دخول {ENT:,.{DP}f} · وقف {STP:,.{DP}f} · هدف {TGT:,.{DP}f} '
          f'· سيولة {LIQ:,.{DP}f}\n'
          f'   أوردر بلوك: الشمعة {IOB} [{OB_LO:,.{DP}f} … {OB_HI:,.{DP}f}] '
          f'· الوصول عند الشمعة {HIT}\n'
          f'   {DUR}s · {FPS}fps · مؤثرات {len(SFX)} '
          f'(٧ قلم + {BARS_LIVE} تِك + ضربة) · {n} bytes')
