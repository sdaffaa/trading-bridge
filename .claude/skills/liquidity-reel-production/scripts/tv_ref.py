# -*- coding: utf-8 -*-
"""طراز فيديو الجارت المعتمد — أمر فهد 2026-08-08 (بعد إلغاء ما قبله).

«اريد طريقة تصميم اي فيديو جارت مستقبلاً مطابق لنموذج الفيديوات التي
سأرسلها كماركب وتحديد وعمل السِت أب والكتابة على الخطوط فقط، مع اضافة
شعاري والوان جارتي الفاتحة، والباقي مطابق للفيديو».

فهذا الملف هو الطراز الواحد لكل فيديو جارت بعد اليوم. وما فيه مقيسٌ من
المراجع الثلاثة إطاراً بإطار، لا مقدَّرٌ بالنظر.

━━ ما يُؤخذ من المرجع (اصطلاح سوق وطريقة عرض) ━━

  · **لا محور سعر ولا محور وقت ولا شبكة.** اللوحة نظيفة: شموع وماركب
    فقط، ومعها خطٌّ أفقيٌّ منقّط واحد لسعر اللحظة. وهذا أكبر فرقٍ عن
    كل ما بنيناه سابقاً — كنّا نرسم محورين وشبكة كاملة.
  · **كتلة عنوان أعلى اللوحة**: `RMZ - TF` بخطٍّ أسودَ عريضٍ مضغوط،
    وتحته سطرٌ مائل بخطٍّ منحنٍ.
  · **الكتابة على الخطوط وحدها**: كل وسمٍ صغيرٌ عاديُّ الوزن، يجلس
    داخل مستطيله أو على خطّه. لا بطاقات محاطة بحدّ، ولا أرقام أسعار،
    ولا جُمل، ولا كابشن.
  · **المفردات**: شريط منطقة عريض (`OB + BSL` · `Demand Zone`) · صندوق
    بلا حشو (`FVG` · `Fibo Zone`) · أرقام فيبو على اليسار · وسم هيكل
    بشرطتين (`CHoCH`) · خطّ اتّجاه مائل واسمه **مائلٌ عليه** · خطّ
    أفقي يقطعه اسمه · مسار متوقَّع متعرّج برأس سهم · سهم عريض للاتجاه.
  · **التحديد**: مقابض زرقاء تلازم العنصر من تمام سحبه حتى بعد تسميته.
  · **المؤشّر صليبي** `+` لا سهم — هكذا في المرجعين الثاني والثالث.

━━ ما لا يُؤخذ منه ━━

المرجعان الثاني والثالث منشورا حسابٍ آخر. المأخوذ اصطلاحُ الرسم وطريقةُ
العرض — وهي مفردات يرسمها آلاف المتداولين وتبنيها أدوات المنصّة نفسها.
**ولا يُؤخذ**: علامته المائية ولا مسخته ولا اسمه ولا تحليله ولا أرقامه.
مكانها شعار فهد واسمه، بأمره: «مع اضافة شعاري والوان جارتي الفاتحة».
"""
from reel_build import CREAM, INK, TEAL, TEAL_D

# ═══ الألوان: هوية فهد الفاتحة، بأمره الصريح ═══
BG = CREAM                          # #F2EEE7 — خلفية الجارت الفاتحة
LN = "#1B3B49"                      # خطّ الماركب وحدود المستطيلات
TX = "#16323F"                      # نصّ الوسوم
TITLE = "#122F3E"                   # العنوان
BULL, BEAR = TEAL, INK              # الشمعة الصاعدة والهابطة
ZFILL = "rgba(46,125,150,0.10)"     # حشو شريط المنطقة الخفيف
ACC = TEAL_D                        # المسار المتوقَّع والسهم
WMK = "rgba(15,46,60,0.055)"        # العلامة المائية
DOT = "rgba(15,46,60,0.22)"         # خطّ سعر اللحظة المنقّط
SEL = "#2C6BD6"                     # أزرق مقابض التحديد

FS_LBL = 26                         # وسم الماركب — مقيس من المرجع
FS_FIB = 24                         # رقم فيبو
SANS = "system-ui,Segoe UI,sans-serif"
SERIF = "Georgia,Times New Roman,serif"


def _e(t):
    return str(t).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _t(x, y, txt, fs=FS_LBL, col=TX, anchor="middle", weight="500",
       family=SANS, extra=""):
    return (f'<text x="{x:.1f}" y="{y:.1f}" fill="{col}" font-size="{fs}" '
            f'font-weight="{weight}" text-anchor="{anchor}" font-family="{family}" '
            f'direction="ltr"{extra}>{_e(txt)}</text>')


def _wrap(o, gid):
    return f'<g id="{gid}" opacity="0">{o}</g>' if gid else o


# ═══════════════════ الأثاث ═══════════════════

def furniture(CW, CH, sym, tf, sub, gem="", handle="@LIQUIDITY.STATE",
              price_y=None):
    """خلفية اللوحة كما في المرجع: بلا محاور وبلا شبكة.

    كنّا نرسم محور سعرٍ يميناً بأرقامه ومحور وقتٍ أسفل بوسومه وشبكةً
    كاملة. والمرجع لا يرسم منها شيئاً — واللوحة عنده شموعٌ وماركب على
    فراغ، وخطٌّ أفقيٌّ منقّط واحد لسعر اللحظة. النظافة هذه جزءٌ من
    الطراز لا إهمالٌ فيه: كل بكسلٍ باقٍ يخدم الماركب."""
    g = [f'<rect x="0" y="0" width="{CW}" height="{CH}" fill="{BG}"/>']

    # العلامة المائية: شعار فهد كبيراً باهتاً وسط اللوحة، مكان مسخة المرجع
    cx, cy = CW / 2, CH * 0.44
    if gem:
        _g = gem.replace('width="100%" height="100%"', 'width="420" height="420"')
        g.append(f'<g transform="translate({cx-210:.0f},{cy-210:.0f})" '
                 f'opacity=".07">{_g}</g>')

    # كتلة العنوان — سطرٌ عريضٌ مضغوط وتحته سطرٌ مائل
    g.append(_t(cx, 168, f"{sym} - {tf}", fs=78, col=TITLE, weight="900",
                extra=' letter-spacing="-1"'))
    if sub:
        g.append(_t(cx, 232, sub, fs=44, col=TITLE, family=SERIF,
                    weight="400", extra=' font-style="italic" opacity="0.88"'))

    # خطّ سعر اللحظة المنقّط — العنصر الوحيد الباقي من أثاث المنصّة
    if price_y is not None:
        g.append(f'<line x1="0" y1="{price_y:.1f}" x2="{CW}" y2="{price_y:.1f}" '
                 f'stroke="{DOT}" stroke-width="2" stroke-dasharray="2 9"/>')

    # التوقيع أسفل اللوحة — موضع المرجع، والاسم اسمُ فهد
    g.append(_t(cx, CH - 54, handle, fs=42, col=INK, family=SERIF,
                anchor="middle", weight="400",
                extra=' font-style="italic" opacity="0.30" letter-spacing="1.5"'))
    return "".join(g)


# ═══════════════════ مفردات الماركب ═══════════════════

def _drag_rect(gid, x0, y0, x1, y1, fill):
    """مستطيلٌ يُسحب أفقياً من حافته اليسرى — بنية نمط `zonedrag`.

    المحرّك يبحث عن `.zw` (المجموعة التي تُقاس) و`.zf` (الحشو)، ويقرأ
    شفافية الحشو من `data-fo` كي لا يفرض شفافيته هو. والاسم **ليس**
    هنا: يُبنى عنصراً مستقلاً كي يظهر بقصّةٍ صلبة بعد استقرار الشكل،
    كما في المرجع (يستقرّ المربّع ثم يُكتب فيه)."""
    xa, xb = min(x0, x1), max(x0, x1)
    ya, yb = min(y0, y1), max(y0, y1)
    w, h = xb - xa, yb - ya
    fo = "0" if fill == "none" else "1"
    return (f'<g id="{gid}" opacity="0">'
            f'<g class="zw" style="transform-box:view-box;'
            f'transform-origin:{xa:.1f}px {ya:.1f}px">'
            f'<rect class="zf" data-fo="{fo}" x="{xa:.1f}" y="{ya:.1f}" '
            f'width="{w:.1f}" height="{h:.1f}" fill="{fill}" opacity="0"/>'
            f'<rect x="{xa:.1f}" y="{ya:.1f}" width="{w:.1f}" height="{h:.1f}" '
            f'fill="none" stroke="{LN}" stroke-width="1.6"/></g>'
            f'<g class="zl" opacity="0"></g></g>')


def zone_bar(x0, x1, y0, y1, gid, fill=ZFILL):
    """شريط منطقة عريض — `OB + BSL` و`Demand Zone`. يعبر عرض اللوحة."""
    return _drag_rect(gid, x0, y0, x1, y1, fill)


def box(x0, y0, x1, y1, gid, fill="none"):
    """صندوق بلا حشو — `FVG` و`Fibo Zone` في المرجع."""
    return _drag_rect(gid, x0, y0, x1, y1, fill)


def shape_label(x0, y0, x1, y1, txt, gid=None, at=None, min_h=42):
    """اسم الشكل — عنصرٌ مستقلّ يظهر بقصّةٍ صلبة بعد استقرار الشكل.

    `at` يزيح الاسم أفقياً داخل الشكل بدل توسيطه: هذه أداةُ فضّ التصادم
    هنا. فحين تتقاطع منطقتان في السعر — وهو تقاطعٌ حقيقي يجب أن يظهر —
    يبقى الشكلان في مكانيهما الصحيحين ويُفرَّق بين اسميهما أفقياً.

    وحين يضيق الشكل عن اسمه **يخرج الاسم فوقه ولا يتمدّد الشكل**. أوّل
    بناءٍ وسّع الشريط ليتّسع للاسم، فانزاحت حدوده عن حدود شمعته: مركزه
    صحيح وحافّتاه خاطئتان — وحدّا الأوردر بلوك هما موضع التفاعل كلّه.
    الشكل يقول السعر، والاسم يجد مكانه حوله."""
    cx = at if at is not None else (x0 + x1) / 2
    top, h = min(y0, y1), abs(y1 - y0)
    cy = (top + h / 2 + FS_LBL * 0.35) if h >= min_h else (top - 10)
    return _wrap(_t(cx, cy, txt), gid)


def fib_mark(x, y, txt, tick=42, gid=None):
    """رقم مستوى فيبو على يسار الصندوق مع شرطةٍ قصيرة — كما في المرجع.

    وهو **الرقم الوحيد** المسموح على اللوحة: نسبةٌ لا سعر. المرجع لا
    يكتب سعراً واحداً في الإطار كلّه."""
    o = (f'<line x1="{x:.1f}" y1="{y:.1f}" x2="{x+tick:.1f}" y2="{y:.1f}" '
         f'stroke="{LN}" stroke-width="1.6"/>'
         + _t(x - 12, y + FS_FIB * 0.35, txt, fs=FS_FIB, anchor="end"))
    return _wrap(o, gid)


def struct_label(x, y, txt, arm=26, gid=None):
    """وسم هيكل بين شرطتين — `CHoCH` و`BOS` كما رُسما في المرجع."""
    w = len(txt) * FS_LBL * 0.56
    o = (f'<line x1="{x-w/2-arm:.1f}" y1="{y:.1f}" x2="{x-w/2-6:.1f}" y2="{y:.1f}" '
         f'stroke="{LN}" stroke-width="1.6"/>'
         f'<line x1="{x+w/2+6:.1f}" y1="{y:.1f}" x2="{x+w/2+arm:.1f}" y2="{y:.1f}" '
         f'stroke="{LN}" stroke-width="1.6"/>'
         + _t(x, y + FS_LBL * 0.35, txt))
    return _wrap(o, gid)


def level_line(x0, x1, y, txt, gid=None, dash=None, col=None):
    """خطّ أفقي يقطعه اسمه في موضعٍ منه — `Liquidity` في المرجع.

    الاسم لا يعلو الخطّ ولا يتدلّى عنه: الخطّ يمشي ثم ينقطع عند الاسم
    ثم يستأنف. ويُنفَّذ بمستطيلٍ بلون الخلفية يمحو ما تحته."""
    w = len(txt) * FS_LBL * 0.56 + 22
    cx = x1 - w / 2 - 120
    d = f' stroke-dasharray="{dash}"' if dash else ""
    o = (f'<line x1="{x0:.1f}" y1="{y:.1f}" x2="{x1:.1f}" y2="{y:.1f}" '
         f'stroke="{col or LN}" stroke-width="1.8"{d}/>'
         f'<rect x="{cx-w/2:.1f}" y="{y-FS_LBL*0.8:.1f}" width="{w:.1f}" '
         f'height="{FS_LBL*1.6:.1f}" fill="{BG}"/>'
         + _t(cx, y + FS_LBL * 0.35, txt))
    return _wrap(o, gid)


def trend_line(x0, y0, x1, y1, txt, gid=None, at=0.42):
    """خطّ اتّجاه مائل واسمه **مائلٌ عليه بزاويته** — `Trendline`.

    في المرجع لا يجلس الاسم أفقياً فوق الخطّ المائل: يميل بميله ويركب
    عليه. وهذا يحتاج `rotate` بالزاوية المحسوبة، ولذلك لم يكن ممكناً
    بمفرداتنا السابقة التي تعرف الأفقي وحده."""
    import math
    ang = math.degrees(math.atan2(y1 - y0, x1 - x0))
    lx, ly = x0 + (x1 - x0) * at, y0 + (y1 - y0) * at
    o = (f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{x1:.1f}" y2="{y1:.1f}" '
         f'stroke="{LN}" stroke-width="1.8"/>'
         f'<g transform="translate({lx:.1f},{ly:.1f}) rotate({ang:.2f})">'
         + _t(0, -10, txt) + '</g>')
    return _wrap(o, gid)


def projection(pts, gid=None, col=None, head=True):
    """المسار المتوقَّع: خطٌّ متعرّج رفيع برأس سهمٍ صغير في نهايته.

    يُرسم على **الفراغ أمام آخر شمعة** — لا على الشموع. وهو آخر ما
    يُرسم في المرجع قبل السهم العريض، لأنه توقّعٌ لا وصف."""
    c = col or ACC
    d = " ".join(f"{'M' if i == 0 else 'L'} {x:.1f} {y:.1f}"
                 for i, (x, y) in enumerate(pts))
    o = [f'<path d="{d}" fill="none" stroke="{c}" stroke-width="2.6" '
         f'stroke-linejoin="round" stroke-linecap="round"/>']
    if head and len(pts) >= 2:
        import math
        (px, py), (qx, qy) = pts[-2], pts[-1]
        a = math.atan2(qy - py, qx - px)
        for s in (-0.42, 0.42):
            o.append(f'<line x1="{qx:.1f}" y1="{qy:.1f}" '
                     f'x2="{qx-26*math.cos(a-s):.1f}" y2="{qy-26*math.sin(a-s):.1f}" '
                     f'stroke="{c}" stroke-width="2.6" stroke-linecap="round"/>')
    return _wrap("".join(o), gid)


def big_arrow(x0, y0, x1, y1, gid=None, w=34, col=None):
    """السهم العريض الذي يختم المرجع — عريضٌ شبهُ شفّاف بلون التمييز."""
    import math
    a = math.atan2(y1 - y0, x1 - x0)
    hl, hw = 96, w * 2.5
    bx, by = x1 - hl * math.cos(a), y1 - hl * math.sin(a)
    nx, ny = -math.sin(a), math.cos(a)
    p = [(x0 + nx * w / 2, y0 + ny * w / 2), (bx + nx * w / 2, by + ny * w / 2),
         (bx + nx * hw / 2, by + ny * hw / 2), (x1, y1),
         (bx - nx * hw / 2, by - ny * hw / 2), (bx - nx * w / 2, by - ny * w / 2),
         (x0 - nx * w / 2, y0 - ny * w / 2)]
    d = " ".join(f"{'M' if i == 0 else 'L'} {a_:.1f} {b_:.1f}"
                 for i, (a_, b_) in enumerate(p)) + " Z"
    return _wrap(f'<path d="{d}" fill="{col or ACC}" opacity="0.82"/>', gid)


def swing(x, y, n, gid=None, fs=22):
    """ترقيم السوينقات `(1)…(5)` بالأزرق عند القمّة أو القاع.

    في المراجع الأربعة كلّها: أرقامٌ صغيرة زرقاء على النقاط المحورية،
    يقرأ بها المشاهد ترتيب الحركة بلا جملة واحدة."""
    return _wrap(_t(x, y, f"({n})", fs=fs, col=SEL, weight="700"), gid)


def chip_label(cx, y, txt, gid=None, fs=22):
    """وسمٌ مميَّز بخلفيةٍ زرقاء مصمتة — `Strong Bearish Wave` في المرجع.

    يُستعمل لعنصرٍ واحدٍ في اللوحة يريد الكاتب تمييزه عن بقيّة الوسوم،
    ولا يُكثَر منه: في المرجع لا يظهر إلا مرّةً واحدة."""
    w = len(txt) * fs * 0.58 + 22
    o = (f'<rect x="{cx-w/2:.1f}" y="{y-fs*0.9:.1f}" width="{w:.1f}" '
         f'height="{fs*1.8:.1f}" fill="{SEL}"/>'
         + _t(cx, y + fs * 0.34, txt, fs=fs, col="#FFFFFF", weight="700"))
    return _wrap(o, gid)


def channel(x0, y0, x1, y1, dy, gid=None, fill="rgba(15,46,60,0.07)"):
    """قناة سعرية: خطّان متوازيان بينهما ظِلٌّ خفيف — قناة المرجع الرابع."""
    o = (f'<path d="M {x0:.1f} {y0:.1f} L {x1:.1f} {y1:.1f} '
         f'L {x1:.1f} {y1+dy:.1f} L {x0:.1f} {y0+dy:.1f} Z" fill="{fill}"/>'
         f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{x1:.1f}" y2="{y1:.1f}" '
         f'stroke="{LN}" stroke-width="1.6"/>'
         f'<line x1="{x0:.1f}" y1="{y0+dy:.1f}" x2="{x1:.1f}" y2="{y1+dy:.1f}" '
         f'stroke="{LN}" stroke-width="1.6"/>')
    return _wrap(o, gid)


def handles(kind, x0, y0, x1, y1, gid=None, r=9):
    """مقابض التحديد — أربع دوائر في الأركان ومربّعان في منتصف الضلعين.

    مقيسة من المرجع الثاني: تظهر لحظة تمام السحبة، وتبقى وقت كتابة
    الاسم، ثم ترتفع. وهي التي تجعل الرسم يبدو يداً تمسك أداة."""
    c = (lambda x, y: f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="#FBF9F5" '
                      f'stroke="{SEL}" stroke-width="2.6"/>')
    s = (lambda x, y: f'<rect x="{x-r:.1f}" y="{y-r:.1f}" width="{2*r}" '
                      f'height="{2*r}" fill="#FBF9F5" stroke="{SEL}" '
                      f'stroke-width="2.6"/>')
    if kind == "line":
        o = c(x0, y0) + c(x1, y1)
    else:
        yt, yb = min(y0, y1), max(y0, y1)
        o = (f'<rect x="{min(x0,x1):.1f}" y="{yt:.1f}" width="{abs(x1-x0):.1f}" '
             f'height="{yb-yt:.1f}" fill="rgba(44,107,214,0.08)" stroke="{SEL}" '
             f'stroke-width="2.4"/>'
             + c(x0, yt) + c(x1, yt) + c(x0, yb) + c(x1, yb)
             + s((x0 + x1) / 2, yt) + s((x0 + x1) / 2, yb))
    return _wrap(o, gid)
