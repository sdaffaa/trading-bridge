# -*- coding: utf-8 -*-
"""تشغيلة ٤١ — فيديو الجارت بالطراز المعتمد. أمر فهد 2026-08-08.

«اريد طريقة تصميم اي فيديو جارت مستقبلاً مطابق لنموذج الفيديوات … كماركب
وتحديد وعمل السِت أب والكتابة على الخطوط فقط، مع اضافة شعاري والوان
جارتي الفاتحة، والباقي مطابق للفيديو».

فهذه هي التشغيلة الواحدة لكل فيديو جارت بعد اليوم، وما قبلها ملغى.

━━ ترتيب بناء السِت أب — مقيسٌ من المرجع الثالث ━━

المرجع يبني من الأعلى إلى الأسفل ثم يتقدّم في الزمن، لا عشوائياً:

    ٣٫٠ث   شريط `OB + BSL` أعلى اللوحة
    ٦٫٠ث   وسم `CHoCH` عند نقطة انقلاب الهيكل
    ٩٫٠ث   صندوق `FVG`
   ١٢٫٠ث   صندوق `Fibo Zone` وأرقامه على يساره
   ١٥٫٠ث   شريط `Demand Zone` أسفل اللوحة
   ١٨٫٠ث   خطّ `Trendline` المائل واسمه مائلٌ عليه
   ٢١٫٠ث   خطّ `Liquidity` الأفقي
   ٢٤٫٠ث   المسار المتوقَّع المتعرّج على الفراغ
   ٢٨٫٠ث   السهم العريض

وكلٌّ منها: سحبةٌ مُيسَّرة `u²(3−2u)` ← مقابض تحديد ← اسمٌ بقصّة صلبة
في إطارٍ واحد ← رفع المقابض. وهي الحركة المقيسة في الجولة السابقة.

━━ الصدق ━━

الشموع والأسعار من نافذةٍ حقيقية اجتازت الطبقات الخمس (`topdown.build`).
والمسار المتوقَّع يُرسم على **الفراغ أمام آخر شمعة** ولا يدّعي شمعةً
لم تُطبع — فهو توقّعٌ ظاهرٌ أنه توقّع، لا صفقةٌ مفبركة.

    LS_SET=<ملف النافذة> python3 run41_ref.py
"""
import os

from reel_sfx_kit import (build_reel, set_canvas, set_pad, set_price_pad,
                          set_vis)
import topdown
import tv_ref as R
from car_common import GEM

HERE = os.path.dirname(os.path.abspath(__file__))

# ═══════════ اللوحة ═══════════
# بلا محاور: الهوامش للعنوان أعلى وللتوقيع أسفل فقط، والشموع تعبر العرض.
CVW, CVH = 1080, 1920
set_canvas(CVW, CVH)
PL, PR, PT, PB = 0, 0, 300, 150
set_pad(PL, PR, PT, PB)
PW, PH = CVW - PL - PR, CVH - PT - PB
DUR = 28.5
FPS = 60

SET = os.environ.get("LS_SET", "btc_sc_2026-08-07_1233.json")
TAG = SET.replace(".json", "")
D, LAY, PLAN = topdown.build(SET)
DP = PLAN["dp"]
FILL, HIT = PLAN["fill"], PLAN["hit"]
EXEC = D.get("exec_tf", "5m")
W = D[EXEC]["w"]
SYM = D["sym"]
TF_EN = {"3m": "M3", "5m": "M5", "15m": "M15", "1h": "H1", "4H": "H4",
         "1D": "D1"}.get(EXEC, EXEC.upper())
assert HIT < len(W), "الهدف خارج النافذة المرسومة"

SELL = PLAN["STP"] > PLAN["ENT"]
L3, L4 = LAY[2], LAY[3]
LVL, SW = L4["lvl"], L4["sw"]          # مستوى السيولة وشمعة كنسه

# ═══════════ الهندسة ═══════════
# مدرَجٌ فارغ يمين اللوحة يمشي إليه المسار المتوقَّع — وهو نفسه الفراغ
# الذي أمر فهد بتركه: «الشموع تمشي بمنتصف الجارت لا بآخر الطرف الأيمن».
RP_OFF = 14
VIS = len(W) + RP_OFF
ANCHOR = len(W) - 1                    # لا انزلاق
# **الشموع ساكنة.** المرجع الثالث لا يحرّك شمعةً واحدة: الجارت مكتملٌ
# من الإطار صفر، والحركةُ كلُّها في الماركب والمؤشّر. وكان طلبٌ سابق
# بتحريكها («اجعل الشموع تتحرك هكذا») — وقد ألغى فهد شروطه القديمة
# وأمر بمطابقة المرجع، والمرجع ساكن. فتُطبع كلُّها من البداية.
RP_BASE = len(W) - 1
set_vis(VIS)
set_price_pad(1.15, 0.10)


def geo():
    lo = min(c["l"] for c in W); hi = max(c["h"] for c in W)
    pad = (hi - lo) * 0.10
    ymin, ymax = lo - pad * 1.15, hi + pad
    slot = PW / VIS
    return (lambda i: PL + slot * i + slot / 2,
            lambda p: PT + (ymax - p) / (ymax - ymin) * PH, slot)


X, Y, SLOT = geo()
XL, XR = 24, CVW - 24                  # الماركب يعبر العرض كما في المرجع
XLAST = X(len(W) - 1)                  # آخر شمعة — الفراغ يبدأ بعدها

# الأوردر بلوك: آخر شمعة معاكسة قبل الاندفاع — تُشتقّ لا تُختار بالنظر
_OB = [i for i in range(max(0, FILL - 14), FILL)
       if (W[i]["c"] > W[i]["o"]) == SELL]
assert _OB, "لا شمعة معاكسة قبل الدخول — الأوردر بلوك لا يُشتقّ"
IOB = _OB[-1]
OB_HI, OB_LO = max(W[IOB]["o"], W[IOB]["c"]), min(W[IOB]["o"], W[IOB]["c"])

# فجوة القيمة: أوّل ثلاثيّةٍ لا يتلامس فيها ذيلا الطرفين بعد الدخول
def _fvg():
    for i in range(IOB, min(HIT, len(W) - 2)):
        a, c = W[i], W[i + 2]
        if not SELL and c["l"] > a["h"]:
            return i + 1, a["h"], c["l"]
        if SELL and c["h"] < a["l"]:
            return i + 1, c["h"], a["l"]
    return None


FVG = _fvg()

# منطقة فيبو ٠٫٥–٠٫٦١٨ على الساق التي سبقت الدخول
_LEG_LO = min(range(max(0, FILL - 12), FILL + 1), key=lambda j: W[j]["l"])
_LEG_HI = max(range(max(0, FILL - 12), FILL + 1), key=lambda j: W[j]["h"])
_a, _b = W[_LEG_LO]["l"], W[_LEG_HI]["h"]
FIB5, FIB618 = _a + (_b - _a) * 0.5, _a + (_b - _a) * 0.618

# خطّ الاتّجاه: من قاع الساق إلى قاع ما بعد الدخول (أو العكس في البيع)
_T0 = _LEG_LO
_T1 = max(range(FILL, len(W)), key=lambda j: W[j]["h"] if SELL else -W[j]["l"])
if _T1 <= _T0:
    _T1 = len(W) - 1


# ═══════════ إحداثيات العناصر — مصدرٌ واحد ═══════════
# تُحسب مرّةً ويقرؤها الماركبُ والمقابضُ والمؤشّر معاً.
#
# والترتيب الرأسي **يقوّس الحركة** كما في المرجع الثالث: شريطٌ عريض عند
# سقف النافذة وآخر عند قاعها، وبينهما الصناديق. أول بناءٍ اشتقّ الشريطين
# من جسم الأوردر بلوك وقاع الساق فوقعا في وسط اللوحة متلاصقين، وتراكبت
# أسماؤهما مع `CHoCH` و`Liquidity`. والتقويس يمنع التصادم بالبناء لا
# بالمعالجة بعده.
_HI = max(c["h"] for c in W); _LO = min(c["l"] for c in W)
_BAND = (Y(_LO) - Y(_HI)) * 0.045          # سُمك الشريط بنسبة ارتفاع اللوحة
OB_T, OB_B = Y(_HI) - _BAND * 1.6, Y(_HI) + _BAND * 0.4
DM_T, DM_B = Y(_LO) - _BAND * 0.4, Y(_LO) + _BAND * 1.6

# الصندوقان يقتسمان الفراغ بين الشريطين: الفجوة أعلى وفيبو أسفلها،
# وكلٌّ في نطاق x مستقلّ كي لا يلتقي اسماهما.
FV_X0 = FV_X1 = FV_T = FV_B = 0.0
if FVG:
    _i, _flo, _fhi = FVG
    FV_X0 = max(XL + 20, X(_i) - SLOT)
    FV_X1 = min(FV_X0 + 300, XR - 20)
    FV_T, FV_B = Y(_fhi), Y(_flo)
    if FV_B - FV_T < 54:                   # فجوةٌ رفيعة لا يتّسع لها اسم
        _m = (FV_T + FV_B) / 2
        FV_T, FV_B = _m - 27, _m + 27
FB_T, FB_B = Y(FIB618), Y(FIB5)
if FB_B - FB_T < 54:
    _m = (FB_T + FB_B) / 2
    FB_T, FB_B = _m - 27, _m + 27
# منطقة فيبو ٠٫٥–٠٫٦١٨ تقع كثيراً على فجوة القيمة نفسها — وهو تقاطعٌ
# حقيقي لا خطأ. فيبقى الصندوقان ويُفصلان **أفقياً**: الفجوة عند شمعاتها
# وفيبو بجوارها، فيُقرأ الاسمان. وإن ضاق اليمين انتقل الصندوق يساراً.
_FBW = 330
if FVG and abs((FB_T + FB_B) / 2 - (FV_T + FV_B) / 2) < 60:
    FB_X0 = FV_X1 + 44
    if FB_X0 + _FBW > XR - 20:
        FB_X0 = max(XL + 20, FV_X0 - 44 - _FBW)
else:
    FB_X0 = X(_LEG_LO) + SLOT * 2
FB_X0 = max(XL + 20, min(FB_X0, XR - 20 - _FBW))
FB_X1 = FB_X0 + _FBW
TR_X0, TR_Y0 = X(_T0), Y(W[_T0]["h"] if SELL else W[_T0]["l"])
TR_X1, TR_Y1 = X(_T1), Y(W[_T1]["h"] if SELL else W[_T1]["l"])
LQ_Y = Y(LVL)

# ═══════════ الخط الزمني — كيفريمات المرجع الثالث ═══════════
_D1, _DR = 2.30, 1.20                  # سحبة أولى ثم ما بعدها
_HOLD, _DESEL, CUT = 0.35, 0.85, 0.02

T_OB = 1.20
T_CHOCH = 5.20
T_FVG = 8.20
T_FIB = 11.60
T_DEM = 15.20
T_TRD = 18.20
T_LIQ = 21.20
T_PROJ = 24.20
T_ARROW = 27.40
T_RUN = T_RUN_E = 0.0                   # لا ريبلاي — الجارت ساكن كالمرجع


def markup():
    """الست أب كما يبنيه المرجع: أشرطة ثم صناديق ثم خطوط ثم توقّع."""
    ex = []
    ex.append(R.zone_bar(XL, XR, OB_T, OB_B, gid="ob"))
    ex.append(R.shape_label(XL, OB_T, XR, OB_B, "OB + BSL", gid="ob_l"))
    ex.append(R.struct_label(X(SW), Y(LVL), "CHoCH", gid="ch"))
    if FVG:
        ex.append(R.box(FV_X0, FV_T, FV_X1, FV_B, gid="fvg"))
        ex.append(R.shape_label(FV_X0, FV_T, FV_X1, FV_B, "FVG", gid="fvg_l"))
    ex.append(R.box(FB_X0, FB_T, FB_X1, FB_B, gid="fib"))
    ex.append(R.shape_label(FB_X0, FB_T, FB_X1, FB_B, "Fibo Zone", gid="fib_l"))
    ex.append(R.fib_mark(FB_X0, FB_T, "0.618", gid="f618"))
    ex.append(R.fib_mark(FB_X0, FB_B, "0.5", gid="f5"))
    ex.append(R.zone_bar(XL, XR, DM_T, DM_B, gid="dem"))
    ex.append(R.shape_label(XL, DM_T, XR, DM_B,
                            "Supply Zone" if SELL else "Demand Zone", gid="dem_l"))
    ex.append(R.trend_line(TR_X0, TR_Y0, TR_X1, TR_Y1, "Trendline", gid="trd"))
    ex.append(R.level_line(XL, XR, LQ_Y, "Liquidity", gid="liq"))
    return "".join(ex)


def _proj_pts():
    """المسار المتوقَّع: ثلاث نقاطٍ على الفراغ وحده بعد آخر شمعة.

    ارتفاعها من مدى النافذة نفسها لا من رقمٍ مخترع، واتجاهها اتجاه
    الصفقة. ولا تلمس أيّ شمعة — الفراغ يبدأ عند `XLAST`."""
    x0 = XLAST + SLOT * 1.5
    step = (XR - 40 - x0) / 3.0
    y0 = Y(W[len(W) - 1]["c"])
    amp = abs(Y(PLAN["TGT"]) - Y(PLAN["ENT"])) * 0.85
    s = 1 if SELL else -1
    # النِّسب الأربع من المرجع: هبوطٌ ثم ارتدادٌ ثم ذروة.
    off = [0.0, 0.75, 0.20, 1.55]
    # **يُصغَّر المدى ولا تُقصّ النقاط.** أول بناءٍ قصّ كل نقطةٍ على حافة
    # مربّع الرسم، فوقعت الذروة والارتداد كلاهما على السقف وصار المتعرّج
    # خطّاً مستقيماً — عيبٌ رآه الفحص البصري على الملف المرندَر. فالحلّ
    # أن يُضرب المدى كلُّه في معاملٍ واحد يُدخل أبعد نقطةٍ داخل اللوحة،
    # فيبقى شكل المسار ويصغر حجمه.
    lo, hi = PT + 40, CVH - PB - 40
    far = max(off)
    room = (y0 - lo) if s < 0 else (hi - y0)
    k = min(1.0, room / max(amp * far, 1e-6))
    return [(x0 + step * dx, y0 + s * amp * o * k)
            for dx, o in zip((0.0, 0.9, 1.7, 3.0), off)]


def overlay():
    p = _proj_pts()
    o = [R.projection(p, gid="prj")]
    # السهم العريض داخل مربّع الرسم دائماً: يبدأ من ركن الفراغ السفلي
    # (العلوي في البيع) وينتهي عند ذروة المسار. أول بناءٍ اشتقّه من نقاط
    # المسار بإزاحةٍ ثابتة فخرج من اللوحة إلى فوق العنوان.
    _s = 1 if SELL else -1
    ax0, ay0 = p[0][0] + 40, min(max(p[0][1] - _s * 190, PT + 60), CVH - PB - 60)
    ax1, ay1 = p[-1][0] - 30, min(max(p[-1][1] + _s * 30, PT + 60), CVH - PB - 60)
    o.append(R.big_arrow(ax0, ay0, ax1, ay1, gid="arw"))
    o.append(R.handles("box", XL, OB_T, XR, OB_B, gid="h_ob"))
    if FVG:
        o.append(R.handles("box", FV_X0, FV_T, FV_X1, FV_B, gid="h_fvg"))
    o.append(R.handles("box", FB_X0, FB_T, FB_X1, FB_B, gid="h_fib"))
    o.append(R.handles("box", XL, DM_T, XR, DM_B, gid="h_dem"))
    o.append(R.handles("line", TR_X0, TR_Y0, TR_X1, TR_Y1, gid="h_trd"))
    o.append(R.handles("line", XL, LQ_Y, XR, LQ_Y, gid="h_liq"))
    return "".join(o)


def _el(draw_id, t0, dur, mode="zonedrag", lbl=True):
    """دورة عنصرٍ واحد كما في المرجع، أربع خطوات:

        سحبةٌ مُيسَّرة ← مقابضُ التحديد ← الاسمُ بقصّةٍ صلبة ← رفع المقابض

    والاسم عنصرٌ مستقلّ (`<id>_l`) لا جزءٌ من الشكل: في المرجع يستقرّ
    المربّع أولاً ثم يُكتب فيه، والمقابض قائمة بينهما."""
    t1 = t0 + dur
    m = [(draw_id, t0, t1, mode),
         (f"h_{draw_id}", t1, t1 + CUT, "cut", t1 + _HOLD + _DESEL, CUT)]
    if lbl:
        m.append((f"{draw_id}_l", t1 + _HOLD, t1 + _HOLD + CUT, "cut"))
    return m


MARKS = (
    _el("ob", T_OB, _D1)
    + [("ch", T_CHOCH, T_CHOCH + CUT, "cut")]
    + (_el("fvg", T_FVG, _DR) if FVG else [])
    + _el("fib", T_FIB, _DR)
    + [("f618", T_FIB + _DR + _HOLD + 0.20, T_FIB + _DR + _HOLD + 0.20 + CUT, "cut"),
       ("f5", T_FIB + _DR + _HOLD + 0.40, T_FIB + _DR + _HOLD + 0.40 + CUT, "cut")]
    + _el("dem", T_DEM, _DR)
    + _el("trd", T_TRD, _DR, mode="draw", lbl=False)
    + _el("liq", T_LIQ, _DR, mode="draw", lbl=False)
    + [("prj", T_PROJ, T_PROJ + 2.60, "draw"),
       ("arw", T_ARROW, T_ARROW + 0.45, "pop")]
)
FULLSET = ["ob", "ob_l", "ch", "fib", "fib_l", "dem", "dem_l", "arw",
           "f618", "f5", "h_ob", "h_fib", "h_dem", "h_trd", "h_liq"]
if FVG:
    FULLSET += ["fvg", "fvg_l", "h_fvg"]
DRAWSET = ["trd", "liq", "prj"]

RP_KF = [[0.0, RP_BASE], [T_RUN, RP_BASE], [T_RUN_E, len(W) - 1], [DUR, len(W) - 1]]

# ═══════════ المؤشّر الصليبي ═══════════
# حاضرٌ طوال الوقت، ينتقل بين العناصر ويسحب كلاً بيده. تيسير `ss` على
# كل ساق كي يبقى تحت رأس ما يُرسم — الخطوط تُرسم بالتيسير نفسه.
_P = _proj_pts()
CURSOR = [
    # يدخل المؤشّر من خارج اللوحة إلى نقطة الإمساك: بلا هذه الساق تبقى
    # الثانية الأولى إطاراً ساكناً، والمرجع لا يترك إطاراً ساكناً واحداً.
    [0.00, XL - 150, OB_T - 120, "ss"],
    [T_OB, XL, OB_T, "ss"],
    [T_OB + _D1, XR, OB_B, "ss"],
    [T_CHOCH, X(SW), LQ_Y, "ss", "down"],
    [T_FVG, FV_X0 if FVG else XL, FV_T if FVG else OB_B, "ss"],
    [T_FVG + _DR, FV_X1 if FVG else XL + 300, FV_B if FVG else FB_T, "ss"],
    [T_FIB, FB_X0, FB_T, "ss"],
    [T_FIB + _DR, FB_X1, FB_B, "ss"],
    [T_DEM, XL, DM_T, "ss"],
    [T_DEM + _DR, XR, DM_B, "ss"],
    [T_TRD, TR_X0, TR_Y0, "ss"],
    [T_TRD + _DR, TR_X1, TR_Y1, "ss"],
    [T_LIQ, XL, LQ_Y, "ss"],
    [T_LIQ + _DR, XR, LQ_Y, "ss"],
    [T_PROJ, _P[0][0], _P[0][1], "ss"],
    [T_PROJ + 2.60, _P[-1][0], _P[-1][1], "ss"],
    [DUR, XL - 150, OB_T - 120, "creep"],       # يعود لموضع الإطار صفر
]


def _gate():
    """بوابة ما قبل الإنتاج.

    السكون هنا يُقاس على **المؤشّر مع الماركب معاً** لا على الماركب
    وحده. فالمرجع يترك بين عناصره نحو ثلاث ثوانٍ لا يُرسم فيها شيء —
    وليست سكوناً: المؤشّر يقطع اللوحة إلى العنصر التالي طوالها. وقاعدةُ
    «تغيّرٌ كل ١٫٥ث» كانت من شروط نسبة التخطّي، وقد ألغاها فهد وأمر
    بمطابقة المرجع. فالمقيس الباقي أن **لا إطار ساكن**: في كل لحظةٍ
    إمّا عنصرٌ يُرسم وإمّا مؤشّرٌ ينتقل."""
    act = sorted((m[1], m[2]) for m in MARKS)

    # ساق مؤشّر متحرّكة = نشاط بصري
    for (ta, xa, ya, *_), (tb, xb, yb, *_) in zip(CURSOR, CURSOR[1:]):
        if (abs(xa - xb) > 2 or abs(ya - yb) > 2) and tb > ta:
            act.append((ta, tb))
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
    assert worst[0] <= 0.7 + 1e-9, \
        f"إطار ساكن {worst[0]:.2f}s — لا ماركب ولا مؤشّر ({worst[1]:.2f}→{worst[2]:.2f})"
    assert merged[-1][1] <= DUR + 1e-9, "عنصر يتجاوز نهاية الفيديو"
    assert all(px > XLAST for px, _ in _proj_pts()), \
        "المسار المتوقَّع يلمس الشموع — يجب أن يُرسم على الفراغ وحده"
    assert all(PT <= py <= CVH - PB for _, py in _proj_pts()), \
        "المسار المتوقَّع يخرج من مربّع الرسم"

    # لا يتراكب وسمان. البناء الأول أوقع `FVG` على `Fibo Zone` و`CHoCH`
    # على `Demand Zone`، ولم يكن في البوابة ما يمسكه — فالفحص البصري
    # وحده كشفه. وهذا الشرط يمسكه قبل الرندر.
    lb = [("OB + BSL", (XL + XR) / 2, (OB_T + OB_B) / 2),
          ("Demand", (XL + XR) / 2, (DM_T + DM_B) / 2),
          ("Fibo Zone", (FB_X0 + FB_X1) / 2, (FB_T + FB_B) / 2),
          ("CHoCH", X(SW), LQ_Y),
          ("Liquidity", XR - 120 - (len("Liquidity") * 26 * 0.56 + 22) / 2, LQ_Y)]
    if FVG:
        lb.append(("FVG", (FV_X0 + FV_X1) / 2, (FV_T + FV_B) / 2))
    for i in range(len(lb)):
        for j in range(i + 1, len(lb)):
            (na, xa, ya), (nb, xb, yb) = lb[i], lb[j]
            wa = len(na) * 26 * 0.56 + 20
            wb = len(nb) * 26 * 0.56 + 20
            if abs(ya - yb) < 34 and abs(xa - xb) < (wa + wb) / 2:
                raise AssertionError(
                    f"وسمان متراكبان: «{na}» و«{nb}» "
                    f"(Δy={abs(ya-yb):.0f} Δx={abs(xa-xb):.0f})")
    assert RP_KF[0][1] == RP_KF[1][1] and RP_KF[-1][1] == len(W) - 1


_gate()

CSS = """
#chartclip{top:0;left:0}
#chip{display:none} #res{display:none} #endlogo{display:none} #edu{display:none}
#cta{display:none}
"""

_lo = min(c["l"] for c in W); _hi = max(c["h"] for c in W)
_pad = (_hi - _lo) * 0.10
cfg = dict(
    w=W, dark=False, extra_css=CSS, grid=False, extra_html="",
    pre_svg=R.furniture(CVW, CVH, SYM, TF_EN, "Analysis per Week", gem=GEM,
                        price_y=Y(W[len(W) - 1]["c"])),
    scroll_svg="",                       # لا محور وقت — طراز المرجع
    lp_pill=False,
    base=RP_BASE - 1, openmax=RP_BASE - 1, open_t=[[RP_BASE - 1, 0.3]], story=[],
    extra_svg=markup(), overlay_svg=overlay(),
    replay={"kf": RP_KF, "vis": ANCHOR},
    marks=MARKS, fullset=FULLSET, drawset=DRAWSET, dom_marks=[],
    cursor=CURSOR, cursor_style="cross", crosshair=False, chart_at=(0, 0),
    draw_ease="ss",
    tlabels=[c["d"] for c in W],
    preview_a=0.0, preview_b=0.0, res_tease=False, sweep_op=0.0,
    txt=[], chip="", res="", cta_k="", cta_s="", edu="",
    dur=DUR, res_t=999, cta_t=999,
    flash=(0.0, 0.0), flash_op=0.0, punch=(0.0, 0.0, 0.0), cam=[],
)

if __name__ == "__main__":
    out = os.path.join(HERE, f"reel41_{TAG}.html")
    n = build_reel(cfg, out)
    print(f"✅ {SYM} · {TF_EN} · {'بيع' if SELL else 'شراء'} — {len(W)} شمعة حقيقية\n"
          f"   عناصر: OB+BSL · CHoCH · {'FVG · ' if FVG else ''}Fibo Zone · "
          f"{'Supply' if SELL else 'Demand'} Zone · Trendline · Liquidity · "
          f"مسار متوقَّع · سهم\n"
          f"   {DUR}s · {FPS}fps · {n} bytes → {os.path.basename(out)}")
