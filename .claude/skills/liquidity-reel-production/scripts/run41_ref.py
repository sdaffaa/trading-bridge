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
DUR = 30.0
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


# ═══════════ إحداثيات العناصر — ملتصقة بشمعتها ═══════════
# 🔒 «يجب ان تكون دقة الماركب ١٠٠٪» — أمر فهد 2026-08-08.
#
# أول بناءٍ أزاح الشريطين إلى سقف النافذة وقاعها هرباً من تصادم الأسماء،
# وهذا يكسر الدقّة: `OB` في المراجع يجلس على **جسم شمعته بالضبط**، لا
# على سقفٍ اختير للراحة. فالقاعدة الآن:
#
#   · كل منطقة تأخذ سعرها الحقيقي من الشمعة التي اشتُقّت منها.
#   · وتمتدّ يميناً إلى حافة اللوحة — امتداد المنصّة نفسه: تغيّرٌ في
#     الزمن لا في السعر، فلا يمسّ الدقّة.
#   · والتصادم يُحلّ بموضع **الاسم** أفقياً لا بإزاحة الشكل. فتتقاطع
#     المناطق (وهو تقاطعٌ حقيقي يجب أن يظهر) ولا تتقاطع أسماؤها.
# **لا توسيع.** كل حدٍّ هو حدّ شمعته بالضبط؛ والاسم يخرج فوق الشكل حين
# يضيق عنه (`shape_label`). التوسيع يُصلح المظهر ويكسر ما يُرسم لأجله:
# حدّا الأوردر بلوك هما موضع التفاعل، وإزاحتُهما ثمانية بكسلات تجعل
# اللوحة تقول سعراً لم تلمسه الشمعة.
_HI = max(c["h"] for c in W); _LO = min(c["l"] for c in W)

OB_T, OB_B = Y(OB_HI), Y(OB_LO)            # جسم شمعة الأوردر بلوك بالضبط
OB_X0 = X(IOB) - SLOT * 0.6

_iHI = max(range(len(W)), key=lambda j: W[j]["h"])
_iLO = min(range(len(W)), key=lambda j: W[j]["l"])
SUP_T, SUP_B = Y(_HI), Y(max(W[_iHI]["o"], W[_iHI]["c"]))
DM_T, DM_B = Y(min(W[_iLO]["o"], W[_iLO]["c"])), Y(_LO)
SUP_X0, DM_X0 = X(_iHI) - SLOT * 0.6, X(_iLO) - SLOT * 0.6

FV_X0 = FV_T = FV_B = 0.0
if FVG:
    _i, _flo, _fhi = FVG
    FV_X0 = X(_i) - SLOT * 0.6
    FV_T, FV_B = Y(_fhi), Y(_flo)

FB_T, FB_B = Y(FIB618), Y(FIB5)
FB_X0 = X(_LEG_LO if SELL else _LEG_HI) - SLOT * 0.6

TR_X0, TR_Y0 = X(_T0), Y(W[_T0]["h"] if SELL else W[_T0]["l"])
TR_X1, TR_Y1 = X(_T1), Y(W[_T1]["h"] if SELL else W[_T1]["l"])
LQ_Y = Y(LVL)

# موضع اسم كل عنصر: نسبةٌ من عرضه. أداةُ فضّ التصادم في هذا الطراز.
LX = {"sup": 0.50, "ob": 0.74, "fvg": 0.58, "fib": 0.30, "dem": 0.50}
_lx = lambda k, x0: x0 + (XR - x0) * LX[k]


def _choch():
    """نقطة انقلاب الهيكل: أول شمعةٍ بعد الكنس تغلق خلف الطرف السابق.

    تُشتقّ ولا تُوضع بالنظر، وإن لم تُوجد فلا يُرسم الوسم أصلاً — وسمٌ
    بلا حدثٍ يقابله هو بالضبط ما ينقض دقّة الماركب."""
    if SELL:
        ref = min(W[j]["l"] for j in range(max(0, SW - 8), SW + 1))
        return next((i for i in range(SW + 1, len(W)) if W[i]["c"] < ref), None)
    ref = max(W[j]["h"] for j in range(max(0, SW - 8), SW + 1))
    return next((i for i in range(SW + 1, len(W)) if W[i]["c"] > ref), None)


ICH = _choch()


def _pivots(k=3):
    """قممٌ وقيعانٌ محورية حقيقية: أدنى/أعلى نقطةٍ في نافذة ٧ شمعات."""
    out = []
    for i in range(k, len(W) - k):
        seg = W[i - k:i + k + 1]
        if W[i]["l"] == min(c["l"] for c in seg):
            out.append((i, "l"))
        elif W[i]["h"] == max(c["h"] for c in seg):
            out.append((i, "h"))
    return out


SWINGS = [(n, X(i), Y(W[i]["l"]) + 34 if k == "l" else Y(W[i]["h"]) - 18)
          for n, (i, k) in enumerate(_pivots()[-3:], start=1)]

# ═══════════ الخط الزمني — إيقاع المرجع ≈٣ث للعنصر ═══════════
_D1, _DR = 2.30, 1.20                  # سحبة أولى ثم ما بعدها
_HOLD, _DESEL, CUT = 0.35, 0.85, 0.02

T_SUP = 1.00
T_OB = 4.40
T_CHOCH = 7.30
T_FVG = 8.60
T_FIB = 11.80
T_DEM = 15.00
T_TRD = 18.20
T_LIQ = 21.00
T_SWG = 23.60
T_PROJ = 25.40
T_ARROW = 28.80
T_RUN = T_RUN_E = 0.0                   # لا ريبلاي — الجارت ساكن كالمرجع


def markup():
    """الست أب كما يبنيه المرجع: أشرطة ثم صناديق ثم خطوط ثم توقّع."""
    ex = []
    ex.append(R.zone_bar(SUP_X0, XR, SUP_T, SUP_B, gid="sup"))
    ex.append(R.shape_label(SUP_X0, SUP_T, XR, SUP_B, "BSL",
                            gid="sup_l", at=_lx("sup", SUP_X0)))
    ex.append(R.zone_bar(OB_X0, XR, OB_T, OB_B, gid="ob"))
    ex.append(R.shape_label(OB_X0, OB_T, XR, OB_B, "OB",
                            gid="ob_l", at=_lx("ob", OB_X0)))
    if ICH is not None:
        ex.append(R.struct_label(X(ICH), Y(W[ICH]["c"]), "CHoCH", gid="ch"))
    if FVG:
        ex.append(R.box(FV_X0, FV_T, XR, FV_B, gid="fvg"))
        ex.append(R.shape_label(FV_X0, FV_T, XR, FV_B, "FVG",
                                gid="fvg_l", at=_lx("fvg", FV_X0)))
    ex.append(R.box(FB_X0, FB_T, XR, FB_B, gid="fib"))
    ex.append(R.shape_label(FB_X0, FB_T, XR, FB_B, "Fibo Zone",
                            gid="fib_l", at=_lx("fib", FB_X0)))
    ex.append(R.fib_mark(FB_X0, FB_T, "0.618", gid="f618"))
    ex.append(R.fib_mark(FB_X0, FB_B, "0.5", gid="f5"))
    ex.append(R.zone_bar(DM_X0, XR, DM_T, DM_B, gid="dem"))
    ex.append(R.shape_label(DM_X0, DM_T, XR, DM_B,
                            "Supply Zone" if SELL else "Demand Zone",
                            gid="dem_l", at=_lx("dem", DM_X0)))
    ex.append(R.trend_line(TR_X0, TR_Y0, TR_X1, TR_Y1, "Trendline", gid="trd"))
    # جهة السيولة تتبع الاتجاه: الشراء يكنس سيولة البيع (SSL) والعكس.
    # تسميةٌ مقلوبة تجعل اللوحة تقول غير ما تصفه الشموع.
    ex.append(R.level_line(XL, XR, LQ_Y, "BSL" if SELL else "SSL", gid="liq"))
    ex.append(R.struct_label(X(SW), LQ_Y - 32, "Sweep", gid="swp"))
    for _n, _sx, _sy in SWINGS:
        ex.append(R.swing(_sx, _sy, _n, gid=f"sw{_n}"))
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
    o.append(R.handles("box", SUP_X0, SUP_T, XR, SUP_B, gid="h_sup"))
    o.append(R.handles("box", OB_X0, OB_T, XR, OB_B, gid="h_ob"))
    if FVG:
        o.append(R.handles("box", FV_X0, FV_T, XR, FV_B, gid="h_fvg"))
    o.append(R.handles("box", FB_X0, FB_T, XR, FB_B, gid="h_fib"))
    o.append(R.handles("box", DM_X0, DM_T, XR, DM_B, gid="h_dem"))
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
    _el("sup", T_SUP, _D1)
    + _el("ob", T_OB, _DR)
    + ([("ch", T_CHOCH, T_CHOCH + CUT, "cut")] if ICH is not None else [])
    + (_el("fvg", T_FVG, _DR) if FVG else [])
    + _el("fib", T_FIB, _DR)
    + [("f618", T_FIB + _DR + _HOLD + 0.20, T_FIB + _DR + _HOLD + 0.20 + CUT, "cut"),
       ("f5", T_FIB + _DR + _HOLD + 0.40, T_FIB + _DR + _HOLD + 0.40 + CUT, "cut")]
    + _el("dem", T_DEM, _DR)
    + _el("trd", T_TRD, _DR, mode="draw", lbl=False)
    + _el("liq", T_LIQ, _DR, mode="draw", lbl=False)
    + [("swp", T_LIQ + _DR + _HOLD, T_LIQ + _DR + _HOLD + CUT, "cut")]
    + [(f"sw{n}", T_SWG + 0.24 * (n - 1), T_SWG + 0.24 * (n - 1) + CUT, "cut")
       for n, _, _ in SWINGS]
    + [("prj", T_PROJ, T_PROJ + 2.60, "draw"),
       ("arw", T_ARROW, T_ARROW + 0.45, "pop")]
)
FULLSET = ["sup", "sup_l", "ob", "ob_l", "fib", "fib_l", "dem", "dem_l",
           "arw", "f618", "f5", "swp",
           "h_sup", "h_ob", "h_fib", "h_dem", "h_trd", "h_liq"]
FULLSET += [f"sw{n}" for n, _, _ in SWINGS]
if ICH is not None:
    FULLSET.append("ch")
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
    [0.00, SUP_X0 - 150, SUP_T - 120, "ss"],
    [T_SUP, SUP_X0, SUP_T, "ss"],
    [T_SUP + _D1, XR, SUP_B, "ss"],
    [T_OB, OB_X0, OB_T, "ss"],
    [T_OB + _DR, XR, OB_B, "ss"],
    [T_CHOCH, X(ICH) if ICH is not None else OB_X0,
     Y(W[ICH]["c"]) if ICH is not None else OB_B, "ss", "down"],
    [T_FVG, FV_X0 if FVG else FB_X0, FV_T if FVG else FB_T, "ss"],
    [T_FVG + _DR, XR, FV_B if FVG else FB_B, "ss"],
    [T_FIB, FB_X0, FB_T, "ss"],
    [T_FIB + _DR, XR, FB_B, "ss"],
    [T_DEM, DM_X0, DM_T, "ss"],
    [T_DEM + _DR, XR, DM_B, "ss"],
    [T_TRD, TR_X0, TR_Y0, "ss"],
    [T_TRD + _DR, TR_X1, TR_Y1, "ss"],
    [T_LIQ, XL, LQ_Y, "ss"],
    [T_LIQ + _DR, XR, LQ_Y, "ss"],
    [T_SWG, SWINGS[0][1], SWINGS[0][2], "ss", "down"],
    [T_SWG + 0.7, SWINGS[-1][1], SWINGS[-1][2], "ss", "down"],
    [T_PROJ, _P[0][0], _P[0][1], "ss"],
    [T_PROJ + 2.60, _P[-1][0], _P[-1][1], "ss"],
    [DUR, SUP_X0 - 150, SUP_T - 120, "creep"],   # يعود لموضع الإطار صفر
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
    lb = [("BSL", _lx("sup", SUP_X0), (SUP_T + SUP_B) / 2),
          ("OB", _lx("ob", OB_X0), (OB_T + OB_B) / 2),
          ("Fibo Zone", _lx("fib", FB_X0), (FB_T + FB_B) / 2),
          ("Demand Zone", _lx("dem", DM_X0), (DM_T + DM_B) / 2),
          ("Sweep", X(SW), LQ_Y - 32),
          ("SSL", XR - 120 - (3 * 26 * 0.56 + 22) / 2, LQ_Y)]
    if FVG:
        lb.append(("FVG", _lx("fvg", FV_X0), (FV_T + FV_B) / 2))
    if ICH is not None:
        lb.append(("CHoCH", X(ICH), Y(W[ICH]["c"])))
    for i in range(len(lb)):
        for j in range(i + 1, len(lb)):
            (na, xa, ya), (nb, xb, yb) = lb[i], lb[j]
            wa = len(na) * 26 * 0.56 + 20
            wb = len(nb) * 26 * 0.56 + 20
            if abs(ya - yb) < 32 and abs(xa - xb) < (wa + wb) / 2:
                raise AssertionError(
                    f"وسمان متراكبان: «{na}» و«{nb}» "
                    f"(Δy={abs(ya-yb):.0f} Δx={abs(xa-xb):.0f})")

    # 🔒 دقّة الماركب ١٠٠٪: مركز كل منطقةٍ على السعر المشتقّ منها بالضبط.
    # هذا هو الشرط الذي يمنع تكرار خطأ البناء الأول — إزاحةُ شكلٍ إلى
    # موضعٍ مريحٍ بصرياً تمرّ بلا أن يلحظها أحد ما لم تُقس.
    # يُقاس **كل حدٍّ على حدة** لا المركز: مركزٌ صحيح وحافّتان مزاحتان
    # يمرّ من فحص المركز، وهو بالضبط الخطأ الذي وقع في البناء الأول.
    edges = [("OB علوي", OB_T, OB_HI), ("OB سفلي", OB_B, OB_LO),
             ("BSL علوي", SUP_T, _HI),
             ("BSL سفلي", SUP_B, max(W[_iHI]["o"], W[_iHI]["c"])),
             ("القاع علوي", DM_T, min(W[_iLO]["o"], W[_iLO]["c"])),
             ("القاع سفلي", DM_B, _LO),
             ("فيبو ٠٫٦١٨", FB_T, FIB618), ("فيبو ٠٫٥", FB_B, FIB5),
             ("السيولة", LQ_Y, LVL)]
    if FVG:
        _i, _flo, _fhi = FVG
        edges += [("الفجوة علوي", FV_T, _fhi), ("الفجوة سفلي", FV_B, _flo)]
    for nm, got, price in edges:
        d = abs(got - Y(price))
        assert d < 0.01, f"«{nm}» يبعد {d:.2f} بكسل عن سعره الحقيقي"
    # الوسوم الهيكلية على شمعاتها لا قربها
    assert ICH is None or 0 <= ICH < len(W), "CHoCH خارج النافذة"
    assert 0 <= SW < len(W), "شمعة الكنس خارج النافذة"
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
