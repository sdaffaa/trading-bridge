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
# الشموع تشغل ٦٢٪ من العرض والباقي فراغٌ نظيف يمتدّ إليه الماركب —
# هذا ما يجعل أسماء المرجع تُقرأ: تجلس في الخالي لا على الشموع.
RP_OFF = max(14, int(len(W) * 0.62))
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
# 🔒 «الماركب سيء». والقياس بيّن أن منطقة الأوردر بلوك كانت **٤٫١٦ نقطة**
# على مدى ٥٤٥ — تسعة بكسلات — بينما جسم الشمعة الوسيط في النافذة ٢٧٫٧
# نقطة. السبب أنّي رسمتها **جسماً** فوقعت على شمعة دوجي. واصطلاح السوق
# أن الأوردر بلوك مدى الشمعة كاملاً (القمّة إلى القاع): هناك تقع الأوامر،
# والذيل جزءٌ من المنطقة لا خارجها. فصارت المنطقة تصف ما تصفه فعلاً،
# وكبرت من ٩ بكسلات إلى ما يناسب شمعتها.
OB_HI, OB_LO = W[IOB]["h"], W[IOB]["l"]

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
# فجوةٌ أصغر من جسم الشمعة الوسيط ليست اختلالاً يُتداول عليه، إنما ضجيج.
# ورسمُها يعطي شريحةً بعشرين بكسلاً باسمٍ معلَّق فوقها — وهو من أسباب
# «الماركب سيء». فالعتبة من البيانات نفسها لا من رقمٍ مختار.
_MEDB = sorted(abs(c["c"] - c["o"]) for c in W)[len(W) // 2]
if FVG and (FVG[2] - FVG[1]) < _MEDB:
    FVG = None

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

# 🔒 «الرسم عشوائي» — أمر فهد 2026-08-08. وكان محقّاً: ستّة من تسعة
# عناصر لم تكن ناتجةً عن الصفقة، إنما عن **حدود النافذة**:
#   · `BSL` كان أعلى قمّةٍ في النافذة — وقعت شمعة ٤٧، أي **بعد** الدخول
#     والهدف. سيولةٌ هدفاً لصفقةٍ انتهت قبل أن تتكوّن.
#   · `Demand Zone` كان أدنى قاعٍ في النافذة — شمعة ٣، قبل الصفقة بسبعٍ
#     وثلاثين شمعة.
#   · `Trendline` من شمعة الدخول إلى آخر النافذة، بلا لمساتٍ تسنده.
#   · السوينقات ٥١ و٥٣ و٥٦ — كلّها بعد انتهاء الصفقة.
# الدقّة في الإحداثيات لا تنفع إن كان الاختيار عشوائياً. فكل عنصرٍ الآن
# **يُشتقّ من سلسلة الصفقة**: سيولة ← كنس ← انقلاب ← أوردر بلوك ← فجوة
# ← ارتداد ← هدف. وما لا يوجد منها لا يُرسم.

# منطقة الطلب/العرض: القاعدة التي ارتدّ منها السعر عند الكنس — لا طرف
# النافذة. قاعُها أدنى قيعان شمعات الكنس، وسقفُها جسم شمعة الارتداد.
_dl = range(max(0, SW - 1), min(len(W), SW + 2))
_dr = range(SW, min(len(W), SW + 3))
if SELL:
    DM_A = max(c["h"] for c in (W[j] for j in _dl))
    DM_B_P = min(min(W[j]["o"], W[j]["c"]) for j in _dr)
else:
    DM_A = max(max(W[j]["o"], W[j]["c"]) for j in _dr)
    DM_B_P = min(c["l"] for c in (W[j] for j in _dl))
DM_T, DM_B = Y(DM_A), Y(DM_B_P)
DM_X0 = X(min(_dl)) - SLOT * 0.6

# الأوردر بلوك غالباً **هو** قاعدة الطلب نفسها في نافذةٍ قصيرة: الشمعة
# المعاكسة التي ارتدّ منها السعر. فرسمُ منطقتين متطابقتين وتسميتهما
# باسمين ليس دقّةً بل حشو. فإن احتوت إحداهما الأخرى بأكثر من نصفها
# يبقى `OB` — وهو الأخصّ — وتُسقَط الأخرى.
def _ov(a0, a1, b0, b1):
    lo, hi = max(min(a0, a1), min(b0, b1)), min(max(a0, a1), max(b0, b1))
    inter = max(0.0, hi - lo)
    return inter / max(min(abs(a1 - a0), abs(b1 - b0)), 1e-9)


SHOW_DM = _ov(OB_T, OB_B, DM_T, DM_B) < 0.5


ENT, TGT = PLAN["ENT"], PLAN["TGT"]


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


def _target_liq():
    """السيولة التي تقصدها الصفقة: قمّةٌ محورية **قبل الدخول** يقع
    طرفها بين الدخول والهدف — وهي ما يسعى إليه السعر فعلاً.

    وإن لم تُوجد فلا يُرسم الوسم أصلاً؛ لا يُستبدل بأعلى قمّةٍ في
    النافذة كما كان. عنصرٌ لا سند له في الصفقة هو الرسم العشوائي."""
    lo, hi = min(ENT, TGT), max(ENT, TGT)
    want = "h" if not SELL else "l"
    cands = [(i, W[i][want]) for i, k in _pivots()
             if i < FILL and k == want and lo <= W[i][want] <= hi]
    if not cands:
        return None
    i, _ = min(cands, key=lambda t: abs(t[1] - TGT))
    if SELL:
        return i, Y(min(W[i]["o"], W[i]["c"])), Y(W[i]["l"]), X(i) - SLOT * 0.6
    return i, Y(W[i]["h"]), Y(max(W[i]["o"], W[i]["c"])), X(i) - SLOT * 0.6


_TL = _target_liq()
SUP_I, SUP_T, SUP_B, SUP_X0 = _TL if _TL else (None, 0.0, 0.0, 0.0)

FV_X0 = FV_T = FV_B = 0.0
if FVG:
    _i, _flo, _fhi = FVG
    FV_X0 = X(_i) - SLOT * 0.6
    FV_T, FV_B = Y(_fhi), Y(_flo)

FB_T, FB_B = Y(FIB618), Y(FIB5)
FB_X0 = X(_LEG_LO if SELL else _LEG_HI) - SLOT * 0.6


# ═══════════ موضع الاسم: حيث لا شمعة ═══════════
# 🔒 «الماركب سيء» — أمر فهد. والمقارنة جنباً إلى جنب مع المرجع كشفت
# السبب الذي لم تكشفه ثلاث جولاتٍ من الاشتقاق: **وسوم المرجع تقع في
# فراغٍ نظيف، ووسومي تقع فوق الشموع فتُمحى.** عنده الماركب يمتدّ يميناً
# إلى مساحةٍ خالية فيُقرأ اسمه من أول نظرة؛ وعندي كان الاسم عند نسبةٍ
# ثابتة من عرض الشكل، فيقع على أجسام الشموع مهما كانت النسبة.
#
# فالموضع يُحسب الآن ولا يُفترض: يُمسح مدى الشكل أفقياً، ويُختار الموضع
# الذي لا تقطعه شمعةٌ تشترك مع الشكل في مداه الرأسي.
_PLACED = []            # [(x0, x1, ytop, ybot)] لكل اسمٍ وُضع


def _clear_x(x0, x1, ytop, ybot, txt, fs=26):
    """أنظف موضعٍ لاسمٍ داخل [x0,x1]: لا تقطعه شمعةٌ في نطاقه الرأسي،
    ولا يلامس اسماً وُضع قبله.

    يُمنع التصادم **بالبناء** لا بالفحص بعده، ويُفضَّل اليمين عند
    التساوي — هناك يمتدّ الشكل إلى الفراغ، وهو موضع أسماء المرجع."""
    w = len(txt) * fs * 0.56 + 24
    yt, yb = min(ytop, ybot), max(ytop, ybot)
    busy = [(X(i) - SLOT * 0.7, X(i) + SLOT * 0.7) for i, c in enumerate(W)
            if not (Y(c["h"]) > yb or Y(c["l"]) < yt)]
    busy += [(px0, px1) for px0, px1, pt, pb in _PLACED
             if not (pt > yb + 34 or pb < yt - 34)]
    lo, hi = x0 + w / 2 + 8, x1 - w / 2 - 8
    if hi <= lo:
        lo = hi = (x0 + x1) / 2
    best, bestsc = None, -1e9
    for k in range(81):
        cx = lo + (hi - lo) * (k / 80.0 if hi > lo else 0)
        a, b = cx - w / 2, cx + w / 2
        gap = min((-1.0 if (p < b and q > a) else min(abs(a - q), abs(b - p)))
                  for p, q in busy) if busy else 1e9
        sc = min(gap, 60) + (cx - lo) / max(hi - lo, 1) * 8
        if gap >= 0 and sc > bestsc:
            best, bestsc = cx, sc
    # لم يبقَ موضعٌ نظيف داخل الشكل: يُرفع الاسم فوق حافته العليا —
    # وهو ما تفعله المنصّة نفسها حين يضيق الشكل. أن يجلس اسمان متلاصقان
    # على شمعةٍ واحدة أسوأ من أن يعلو أحدهما شكله.
    if best is None:
        cx, dy = (x0 + x1) / 2, -(yb - yt) / 2 - 22
        _PLACED.append((cx - w / 2, cx + w / 2, yt + dy - 16, yt + dy + 16))
        return cx, dy
    _PLACED.append((best - w / 2, best + w / 2, yt, yb))
    return best, 0.0


_LBL = {}                                   # يُملأ بعد اشتقاق كل العناصر
_lx = lambda k, _x0=None: _LBL[k][0]
_ldy = lambda k: _LBL[k][1]


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


# السوينقات ترقّم **قصّة الصفقة** لا آخر ثلاث نقاطٍ في النافذة:
#   (1) الطرف الذي كُسر لاحقاً   (2) شمعة الكنس   (3) شمعة الانقلاب
_REF_I = (min(range(max(0, SW - 8), SW + 1), key=lambda j: W[j]["l"]) if SELL
          else max(range(max(0, SW - 8), SW + 1), key=lambda j: W[j]["h"]))
_STORY = [(_REF_I, "h" if not SELL else "l"), (SW, "l" if not SELL else "h")]
if ICH is not None:
    _STORY.append((ICH, "h" if not SELL else "l"))
SWINGS = [(n, X(i), (Y(W[i]["h"]) - 18) if k == "h" else (Y(W[i]["l"]) + 34))
          for n, (i, k) in enumerate(_STORY, start=1)]


def _trend():
    """خطّ اتّجاه لا يُرسم إلا إذا سنده **ثلاث لمسات** محورية.

    كان يُرسم من شمعة الدخول إلى آخر النافذة بلا سند — خطٌّ يقول إن
    ثمّة اتّجاهاً ولا شيء يثبته. فإن لم تجتمع ثلاث نقاطٍ على استقامةٍ
    واحدة فلا خطّ."""
    want = "l" if not SELL else "h"
    pv = [(i, W[i][want]) for i, k in _pivots() if k == want]
    if len(pv) < 3:
        return None
    best = None
    for a in range(len(pv) - 2):
        for b in range(len(pv) - 1, a + 1, -1):
            (i0, p0), (i1, p1) = pv[a], pv[b]
            if i1 - i0 < 8:
                continue
            m = (p1 - p0) / (i1 - i0)
            tol = (_HI - _LO) * 0.012
            hits = [j for j, pj in pv
                    if i0 <= j <= i1 and abs(pj - (p0 + m * (j - i0))) <= tol]
            if len(hits) >= 3 and (best is None or len(hits) > best[0]):
                best = (len(hits), i0, p0, i1, p1)
    if best is None:
        return None
    _, i0, p0, i1, p1 = best
    return X(i0), Y(p0), X(i1), Y(p1), best[0]


_TR = _trend()

TR_X0, TR_Y0, TR_X1, TR_Y1 = (_TR[:4] if _TR else (0.0, 0.0, 0.0, 0.0))
_LBL["ob"] = _clear_x(OB_X0, XR, OB_T, OB_B, "OB")
_LBL["dem"] = _clear_x(DM_X0, XR, DM_T, DM_B,
                       "Supply Zone" if SELL else "Demand Zone")
if SUP_I is not None:
    _LBL["sup"] = _clear_x(SUP_X0, XR, SUP_T, SUP_B, "SSL" if SELL else "BSL")
if FVG:
    _LBL["fvg"] = _clear_x(FV_X0, XR, FV_T, FV_B, "FVG")
_LBL["fib"] = _clear_x(FB_X0, XR, FB_T, FB_B, "Fibo Zone")
LQ_Y = Y(LVL)

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
    if SUP_I is not None:
        ex.append(R.zone_bar(SUP_X0, XR, SUP_T, SUP_B, gid="sup"))
        ex.append(R.shape_label(SUP_X0, SUP_T, XR, SUP_B,
                                "SSL" if SELL else "BSL",
                                gid="sup_l", at=_lx("sup"), dy=_ldy("sup")))
    ex.append(R.zone_bar(OB_X0, XR, OB_T, OB_B, gid="ob"))
    ex.append(R.shape_label(OB_X0, OB_T, XR, OB_B, "OB",
                            gid="ob_l", at=_lx("ob"), dy=_ldy("ob")))
    if ICH is not None:
        ex.append(R.struct_label(X(ICH), Y(W[ICH]["c"]), "CHoCH", gid="ch"))
    if FVG:
        ex.append(R.box(FV_X0, FV_T, XR, FV_B, gid="fvg"))
        ex.append(R.shape_label(FV_X0, FV_T, XR, FV_B, "FVG",
                                gid="fvg_l", at=_lx("fvg"), dy=_ldy("fvg")))
    ex.append(R.box(FB_X0, FB_T, XR, FB_B, gid="fib"))
    ex.append(R.shape_label(FB_X0, FB_T, XR, FB_B, "Fibo Zone",
                            gid="fib_l", at=_lx("fib"), dy=_ldy("fib")))
    ex.append(R.fib_mark(FB_X0, FB_T, "0.618", gid="f618"))
    ex.append(R.fib_mark(FB_X0, FB_B, "0.5", gid="f5"))
    if SHOW_DM:
        ex.append(R.zone_bar(DM_X0, XR, DM_T, DM_B, gid="dem"))
        ex.append(R.shape_label(DM_X0, DM_T, XR, DM_B,
                                "Supply Zone" if SELL else "Demand Zone",
                                gid="dem_l", at=_lx("dem"), dy=_ldy("dem")))
    if _TR:
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
    if SUP_I is not None:
        o.append(R.handles("box", SUP_X0, SUP_T, XR, SUP_B, gid="h_sup"))
    o.append(R.handles("box", OB_X0, OB_T, XR, OB_B, gid="h_ob"))
    if FVG:
        o.append(R.handles("box", FV_X0, FV_T, XR, FV_B, gid="h_fvg"))
    o.append(R.handles("box", FB_X0, FB_T, XR, FB_B, gid="h_fib"))
    if SHOW_DM:
        o.append(R.handles("box", DM_X0, DM_T, XR, DM_B, gid="h_dem"))
    if _TR:
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
    (_el("sup", T_SUP, _D1) if SUP_I is not None else [])
    + _el("ob", T_OB, _DR)
    + ([("ch", T_CHOCH, T_CHOCH + CUT, "cut")] if ICH is not None else [])
    + (_el("fvg", T_FVG, _DR) if FVG else [])
    + _el("fib", T_FIB, _DR)
    + [("f618", T_FIB + _DR + _HOLD + 0.20, T_FIB + _DR + _HOLD + 0.20 + CUT, "cut"),
       ("f5", T_FIB + _DR + _HOLD + 0.40, T_FIB + _DR + _HOLD + 0.40 + CUT, "cut")]
    + (_el("dem", T_DEM, _DR) if SHOW_DM else [])
    + (_el("trd", T_TRD, _DR, mode="draw", lbl=False) if _TR else [])
    + _el("liq", T_LIQ, _DR, mode="draw", lbl=False)
    + [("swp", T_LIQ + _DR + _HOLD, T_LIQ + _DR + _HOLD + CUT, "cut")]
    + [(f"sw{n}", T_SWG + 0.24 * (n - 1), T_SWG + 0.24 * (n - 1) + CUT, "cut")
       for n, _, _ in SWINGS]
    + [("prj", T_PROJ, T_PROJ + 2.60, "draw"),
       ("arw", T_ARROW, T_ARROW + 0.45, "pop")]
)
FULLSET = ["ob", "ob_l", "fib", "fib_l", "arw", "f618", "f5", "swp",
           "h_ob", "h_fib", "h_liq"]
if SHOW_DM:
    FULLSET += ["dem", "dem_l", "h_dem"]
if SUP_I is not None:
    FULLSET += ["sup", "sup_l", "h_sup"]
if _TR:
    FULLSET.append("h_trd")
FULLSET += [f"sw{n}" for n, _, _ in SWINGS]
if ICH is not None:
    FULLSET.append("ch")
if FVG:
    FULLSET += ["fvg", "fvg_l", "h_fvg"]
DRAWSET = ["liq", "prj"] + (["trd"] if _TR else [])

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
    lb = [("OB", _lx("ob"), (OB_T + OB_B) / 2 + _ldy("ob")),
          ("Fibo Zone", _lx("fib"), (FB_T + FB_B) / 2 + _ldy("fib")),
          ("Sweep", X(SW), LQ_Y - 32),
          ("SSL", XR - 120 - (3 * 26 * 0.56 + 22) / 2, LQ_Y)]
    if FVG:
        lb.append(("FVG", _lx("fvg"), (FV_T + FV_B) / 2 + _ldy("fvg")))
    if ICH is not None:
        lb.append(("CHoCH", X(ICH), Y(W[ICH]["c"])))
    if SUP_I is not None:
        lb.append(("BSL", _lx("sup"), (SUP_T + SUP_B) / 2 + _ldy("sup")))
    if SHOW_DM:
        lb.append(("Demand Zone", _lx("dem"), (DM_T + DM_B) / 2 + _ldy("dem")))
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
             *((("المنطقة علوي", DM_T, DM_A),
                ("المنطقة سفلي", DM_B, DM_B_P)) if SHOW_DM else ()),
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
