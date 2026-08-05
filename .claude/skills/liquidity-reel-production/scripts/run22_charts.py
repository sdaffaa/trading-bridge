# -*- coding: utf-8 -*-
"""جارتات تشغيلة 22 — ثلاث وحدات: خريطة (AMD) · دروداون · ملل.
كل دالة تُرجع SVG جاهزاً، والبذور تُسجَّل مرة واحدة من run22_build.py.
أرقام وحدة الدروداون كلها محسوبة لا مُقدَّرة (انظر _SEQ ودوال الحساب أسفله).
"""
from reel_build import INK, TEAL, TEAL_D, RED, GREY, MUTE, htext, gen
from run15_charts import zbox, xm, tick, hl, badge, frame, head, note, cap, floorc, CARD
import chart_registry

CHARTS = []
_AR = str.maketrans("0123456789", "٠١٢٣٤٥٦٧٨٩")

def fresh(seed, anch, label):
    chart_registry.assert_fresh_synthetic(seed, anch, label=label)
    CHARTS.append((seed, anch, label))

def _box(seed, anch, N, iAcc, label, wick=0.72, squeeze=0.55, shrink=0.85):
    """يضغط أول iAcc شمعة داخل صندوق ضيق = مرحلة التجميع/النطاق.
    shrink يتحكم بحجم شموع الصندوق: القيمة المنخفضة تجعله شريطاً غير مقروء،
    لذلك تُبقى قريبة من الواحد ويُضبط ارتفاع الصندوق من المراسي نفسها."""
    fresh(seed, anch, label)
    W = gen(anch, N, seed, wick=wick)
    rng = max(c["h"] for c in W) - min(c["l"] for c in W)
    mid = sum(c["c"] for c in W[:iAcc]) / iAcc
    half = rng * squeeze * 0.30
    for j in range(iAcc):
        for k in ("o", "c", "h", "l"):
            W[j][k] = mid + (W[j][k] - mid) * shrink
        W[j]["h"] = min(W[j]["h"], mid + half); W[j]["l"] = max(W[j]["l"], mid - half)
        W[j]["o"] = min(max(W[j]["o"], W[j]["l"]), W[j]["h"])
        W[j]["c"] = min(max(W[j]["c"], W[j]["l"]), W[j]["h"])
    AH = max(c["h"] for c in W[:iAcc]); AL = min(c["l"] for c in W[:iAcc])
    return W, AH, AL, rng

def vsep(xx, y0, y1, col=MUTE):
    return (f'<line x1="{xx:.1f}" y1="{y0}" x2="{xx:.1f}" y2="{y1}" stroke="{col}" '
            f'stroke-width="1.2" stroke-dasharray="5 5" opacity="0.75"/>')


# ══════════════ 1) خريطة — تجميع · تلاعب · توزيع (AMD) ══════════════
def amd_map(Wd=880, H=250, seed=8401):
    """المراحل الثلاث في يوم واحد: نطاق ضيق ← سحب كاذب ← اتجاه."""
    N = 34
    anch = [(0, 13.7), (3, 14.3), (6, 13.7), (9, 14.25), (12, 13.95), (15, 14.5),
            (20, 15.5), (26, 16.4), (33, 17.0)]
    W, AH, AL, rng = _box(seed, anch, N, 12, f"خريطة اليوم {seed}")
    W[13].update(l=AL - rng * 0.075, o=AL + rng * 0.005, c=AL + rng * 0.03, h=AL + rng * 0.045)
    for j in range(14, N):
        floorc(W, j, AL + rng * 0.012)
    svg, x, y, slot = frame(W, Wd, H)
    svg += zbox(x(0) - slot * .4, y(AH), x(11) + slot * .5, y(AL))
    svg += hl(x(0) - slot * .4, x(N - 1) + slot * .5, y(AL), INK, 1.6, dash="6 5")
    svg += vsep(x(12) + slot * .5, 58, H - 46)
    svg += vsep(x(18) + slot * .5, 58, H - 46)
    svg += tick(x(16), y(W[16]["h"]) - 18)
    svg += head(Wd, "ثلاث مراحل في جلسة واحدة")
    svg += note(x(5), "تجميع", TEAL_D, H, 18)
    svg += note(x(14), "تلاعب", RED, H, 18)
    svg += note(x(27), "توزيع", TEAL_D, H, 18)
    return svg + badge(Wd, "خريطة اليوم", True) + "</svg>"

def amd_buy(Wd=880, H=250, seed=8402):
    """سحب أسفل النطاق ثم إغلاق داخله = تلاعب هابط ← يوم شراء."""
    N = 32
    anch = [(0, 13.5), (3, 14.0), (6, 13.5), (9, 14.0), (11, 13.7), (14, 13.2),
            (17, 14.3), (22, 15.4), (31, 16.6)]
    W, AH, AL, rng = _box(seed, anch, N, 11, f"خريطة شراء {seed}")
    W[13].update(l=AL - rng * 0.075, o=AL + rng * 0.005, c=AL + rng * 0.035, h=AL + rng * 0.05)
    for j in range(14, N):
        floorc(W, j, AL + rng * 0.012)
    svg, x, y, slot = frame(W, Wd, H)
    svg += zbox(x(0) - slot * .4, y(AH), x(10) + slot * .5, y(AL))
    svg += hl(x(0) - slot * .4, x(N - 1) + slot * .5, y(AL), INK, 1.7)
    svg += hl(x(13) - slot * .5, x(N - 1) + slot * .5, y(AH + rng * 0.26), TEAL_D, 1.7)
    svg += tick(x(15), y(W[15]["h"]) - 18)
    svg += head(Wd, "المتصل السفلي: قاع النطاق · العلوي: الهدف")
    svg += note(x(5), "نطاق التجميع", TEAL_D, H, 17)
    svg += note(x(24), "الدخول بعد العودة داخل النطاق", TEAL_D, H, 17)
    return svg + badge(Wd, "اتجاه اليوم: شراء", True) + "</svg>"

def amd_sell(Wd=880, H=250, seed=8403):
    """المرآة: سحب أعلى النطاق ثم إغلاق داخله = تلاعب صاعد ← يوم بيع."""
    N = 32
    anch = [(0, 14.5), (3, 14.0), (6, 14.5), (9, 14.0), (11, 14.3), (14, 14.9),
            (17, 13.7), (22, 12.6), (31, 11.4)]
    W, AH, AL, rng = _box(seed, anch, N, 11, f"خريطة بيع {seed}")
    W[13].update(h=AH + rng * 0.075, o=AH - rng * 0.005, c=AH - rng * 0.035, l=AH - rng * 0.05)
    for j in range(14, N):
        cap(W, j, AH - rng * 0.012)
    svg, x, y, slot = frame(W, Wd, H)
    svg += zbox(x(0) - slot * .4, y(AH), x(10) + slot * .5, y(AL))
    svg += hl(x(0) - slot * .4, x(N - 1) + slot * .5, y(AH), INK, 1.7)
    svg += hl(x(13) - slot * .5, x(N - 1) + slot * .5, y(AL - rng * 0.26), TEAL_D, 1.7)
    svg += tick(x(15), y(W[15]["l"]) + 24)
    svg += head(Wd, "المتصل العلوي: قمة النطاق · السفلي: الهدف")
    svg += note(x(5), "نطاق التجميع", TEAL_D, H, 17)
    svg += note(x(24), "السحب الكاذب حدّد الاتجاه", TEAL_D, H, 17)
    return svg + badge(Wd, "اتجاه اليوم: بيع", True) + "</svg>"

def amd_none(Wd=880, H=250, seed=8404):
    """لا مرحلة تلاعب: السعر يغادر النطاق ولا يعود — انتظار السحب يكلّف وقفاً."""
    N = 30
    anch = [(0, 13.6), (3, 14.1), (6, 13.6), (9, 14.0), (12, 14.9), (16, 15.8),
            (22, 16.9), (29, 17.8)]
    W, AH, AL, rng = _box(seed, anch, N, 10, f"خريطة بلا تلاعب {seed}")
    for j in range(11, N):
        floorc(W, j, AH + rng * 0.02)
    ENT = AH + rng * 0.09
    STP = ENT + rng * 0.11
    svg, x, y, slot = frame(W, Wd, H)
    svg += zbox(x(0) - slot * .4, y(AH), x(9) + slot * .5, y(AL), op=0.09,
                col=MUTE, stroke=GREY, dash="6 5")
    svg += hl(x(12) - slot * .5, x(N - 1) + slot * .5, y(ENT), INK, 1.9)
    svg += hl(x(12) - slot * .5, x(N - 1) + slot * .5, y(STP), RED, 1.6, dash="7 5")
    svg += xm(x(14), y(STP) - 6)
    svg += head(Wd, "المتصل: بيع انتظاراً لسحب · المتقطع: الوقف")
    svg += note(x(5), "النطاق غادره السعر", GREY, H, 17)
    svg += note(x(23), "لم تقع مرحلة تلاعب أصلاً", RED, H, 17)
    return svg + badge(Wd, "النموذج لا ينطبق", False) + "</svg>"

def amd_late(Wd=880, H=250, seed=8405):
    """دخول في آخر مرحلة التوزيع: المسافة إلى الهدف أقصر من الوقف."""
    N = 32
    anch = [(0, 13.4), (3, 13.9), (6, 13.4), (9, 13.9), (11, 13.2), (14, 14.4),
            (18, 15.5), (23, 16.3), (27, 16.6), (31, 15.6)]
    W, AH, AL, rng = _box(seed, anch, N, 10, f"خريطة متأخر {seed}")
    W[11].update(l=AL - rng * 0.07, o=AL, c=AL + rng * 0.03, h=AL + rng * 0.045)
    for j in range(12, N):
        floorc(W, j, AL + rng * 0.01)
    ENT = W[24]["c"]
    STP = ENT - rng * 0.16
    for j in range(27, 30):
        cap(W, j, ENT - rng * 0.04)
    W[28]["l"] = min(W[28]["l"], STP - rng * 0.03)
    svg, x, y, slot = frame(W, Wd, H)
    svg += zbox(x(0) - slot * .4, y(AH), x(9) + slot * .5, y(AL), op=0.09,
                col=MUTE, stroke=GREY, dash="6 5")
    svg += hl(x(23) - slot * .5, x(N - 1) + slot * .5, y(ENT), INK, 1.9)
    svg += hl(x(23) - slot * .5, x(N - 1) + slot * .5, y(STP), RED, 1.6, dash="7 5")
    svg += xm(x(28), y(STP) + 8)
    svg += head(Wd, "المتصل: الدخول · المتقطع: الوقف")
    svg += note(x(6), "التجميع ثم التلاعب", GREY, H, 17)
    svg += note(x(25), "دخول بعد معظم المسافة", RED, H, 17)
    return svg + badge(Wd, "متأخر على الحركة", False) + "</svg>"


# ══════════════ 2) دروداون — رياضيات التراجع ══════════════
# متتالية واحدة تُستعمل في كل رسوم الوحدة: 24 صفقة، 10 رابحة، عائد/مخاطرة 1.5
_SEQ = [1, 1, -1, 1, -1, 1, -1, -1, -1, -1, -1, -1, -1, 1, -1, 1, 1, -1, -1, 1, 1, -1, -1, 1]
_RR = 1.5

def _equity_of(risk):
    """منحنى رأس المال وأقصى تراجع عند حجم مخاطرة معيّن — حساب لا تقدير."""
    v, cur, peak, mdd = 100.0, [100.0], 100.0, 0.0
    for s in _SEQ:
        v *= (1 + _RR * risk) if s > 0 else (1 - risk)
        cur.append(v); peak = max(peak, v); mdd = max(mdd, (peak - v) / peak * 100)
    return cur, mdd

def _grid(Wd, H, pt=58, pb=80, pl=52, pr=44):
    s = [f'<svg class="chartsvg" viewBox="0 0 {Wd} {H}" width="{Wd}" height="{H}" '
         f'xmlns="http://www.w3.org/2000/svg"><rect width="{Wd}" height="{H}" fill="{CARD}"/>']
    for k in range(5):
        gy = pt + (H - pt - pb) * k / 4
        s.append(f'<line x1="{pl}" y1="{gy:.1f}" x2="{Wd-pr}" y2="{gy:.1f}" '
                 f'stroke="rgba(15,46,60,0.06)" stroke-width="1"/>')
    return s, pl, pr, pt, pb

def _curves(Wd, H, series, lo=None, hi=None, base=None, pt=58, pb=80):
    """منحنيات متعددة على محور واحد. series = [(vals, color, width)]"""
    s, pl, pr, pt, pb = _grid(Wd, H, pt, pb)
    allv = [v for vals, _, _ in series for v in vals]
    lo = min(allv) if lo is None else lo
    hi = max(allv) if hi is None else hi
    pad = max(hi - lo, 1e-6) * 0.16
    lo -= pad; hi += pad
    n = max(len(vals) for vals, _, _ in series)
    x = lambda i: pl + (Wd - pl - pr) * (i / max(n - 1, 1))
    y = lambda v: pt + (hi - v) / (hi - lo) * (H - pt - pb)
    if base is not None:
        s.append(f'<line x1="{pl}" y1="{y(base):.1f}" x2="{Wd-pr}" y2="{y(base):.1f}" '
                 f'stroke="{MUTE}" stroke-width="1.4" stroke-dasharray="6 5"/>')
    for vals, col, w in series:
        p = " ".join(f"{x(i):.1f},{y(v):.1f}" for i, v in enumerate(vals))
        s.append(f'<polyline points="{p}" fill="none" stroke="{col}" stroke-width="{w}" '
                 f'stroke-linejoin="round" stroke-linecap="round"/>')
    return "".join(s), x, y

def _pairbars(Wd, H, items, pt=58, pb=86, pl=44, pr=44):
    """أعمدة مزدوجة: الأحمر = الخسارة، السماوي = المطلوب للتعافي."""
    s, pl, pr, pt, pb = _grid(Wd, H, pt, pb, pl, pr)
    mx = max(max(a, b) for _, a, b, _sa, _sb in items)
    n = len(items); gw = (Wd - pl - pr) / n; bw = gw * 0.27
    y0 = H - pb; hmax = H - pb - pt - 22
    for i, (lab, a, b, sa, sb) in enumerate(items):
        cx = pl + gw * (i + 0.5)
        for j, (v, col, txt) in enumerate(((a, RED, sa), (b, TEAL_D, sb))):
            bh = v / mx * hmax
            bx = cx + 5 if j == 0 else cx - bw - 5
            s.append(f'<rect x="{bx:.1f}" y="{y0-bh:.1f}" width="{bw:.1f}" height="{bh:.1f}" '
                     f'fill="{col}" opacity="{0.55 if j==0 else 0.85}"/>')
            s.append(htext(bx + bw / 2, y0 - bh - 9, txt, col, 16))
        s.append(htext(cx, y0 + 26, lab, INK, 18))
    return "".join(s), y0

def _signed(Wd, H, items, pt=58, pb=104, pl=44, pr=44):
    """أعمدة موجبة/سالبة حول خط الصفر.
    الهوامش مضبوطة كي لا تتقاطع قيمة العمود السالب مع اسم المجموعة تحته."""
    s, pl, pr, pt, pb = _grid(Wd, H, pt, pb, pl, pr)
    mx = max(abs(v) for _, v, _ in items) or 1
    n = len(items); gw = (Wd - pl - pr) / n; bw = gw * 0.42
    zy = pt + (H - pt - pb) * 0.55
    hmax = (H - pt - pb) * 0.42
    s.append(f'<line x1="{pl}" y1="{zy:.1f}" x2="{Wd-pr}" y2="{zy:.1f}" stroke="{GREY}" stroke-width="1.6"/>')
    for i, (lab, v, txt) in enumerate(items):
        cx = pl + gw * (i + 0.5)
        bh = abs(v) / mx * hmax
        col = TEAL_D if v >= 0 else RED
        ty = zy - bh if v >= 0 else zy
        s.append(f'<rect x="{cx-bw/2:.1f}" y="{ty:.1f}" width="{bw:.1f}" height="{bh:.1f}" '
                 f'fill="{col}" opacity="0.75"/>')
        s.append(htext(cx, (zy - bh - 9) if v >= 0 else (zy + bh + 19), txt, col, 16))
        s.append(htext(cx, H - pb + 50, lab, INK, 18))
    return "".join(s), zy

def dd_asym(Wd=880, H=250, seed=8411):
    """كل خسارة تحتاج ربحاً أكبر منها — والفجوة تتسع كلما عمق التراجع."""
    items = [("٥٪", 5, 5.3, "٥", "٥٫٣"), ("١٠٪", 10, 11.1, "١٠", "١١٫١"),
             ("٢٠٪", 20, 25, "٢٠", "٢٥"), ("٣٠٪", 30, 42.9, "٣٠", "٤٢٫٩"),
             ("٥٠٪", 50, 100, "٥٠", "١٠٠")]
    svg, y0 = _pairbars(Wd, H, items)
    svg = svg.replace("</svg>", "")
    svg += head(Wd, "الأحمر: التراجع · السماوي: الربح اللازم للعودة")
    svg += htext(Wd / 2, H - 14, "عند ٥٠٪ تحتاج مضاعفة ما تبقّى لتعود إلى نقطة البداية", RED, 18)
    return svg + badge(Wd, "العلاقة غير متماثلة", False) + "</svg>"

def dd_paths(Wd=880, H=250, seed=8412):
    """نفس الصفقات الـ٢٤ بحجمين مختلفين: النهاية واحدة والحفرة ليست واحدة."""
    a, mda = _equity_of(0.01)
    b, mdb = _equity_of(0.05)
    svg, x, y = _curves(Wd, H, [(b, RED, 2.6), (a, INK, 2.6)], base=100.0)
    fmt = lambda v: ("%.1f" % v).replace(".", "٫").translate(_AR)
    svg += head(Wd, "الأحمر: مخاطرة ٥٪ · الداكن: مخاطرة ١٪")
    svg += htext(Wd / 2, H - 46, f"أقصى تراجع: {fmt(mdb)}٪ مقابل {fmt(mda)}٪", RED, 19)
    svg += htext(Wd / 2, H - 14, "المحصلة بعد ٢٤ صفقة متقاربة — والفارق كله في عمق الحفرة", INK, 18)
    return svg + badge(Wd, "الحجم لا يضاعف الحافة", False) + "</svg>"

def dd_maxdd(Wd=880, H=250, seed=8413):
    """أقصى تراجع يتناسب طردياً مع حجم المخاطرة — من المتتالية نفسها."""
    rows = []
    for r, lab in ((0.005, "٠٫٥٪"), (0.01, "١٪"), (0.02, "٢٪"), (0.03, "٣٪"), (0.05, "٥٪")):
        _, m = _equity_of(r)
        rows.append((lab, -m, f"−{('%.1f' % m).replace('.', '٫').translate(_AR)}٪"))
    svg, zy = _signed(Wd, H, rows)
    svg += head(Wd, "أقصى تراجع لكل حجم مخاطرة — الصفقات ذاتها")
    svg += htext(Wd / 2, H - 14, "ضاعف الحجم خمس مرات… يتضاعف التراجع خمس مرات", RED, 18)
    return svg + badge(Wd, "التناسب طردي", False) + "</svg>"

def dd_streak(Wd=880, H=250, seed=8414):
    """سلسلة الخسائر ليست سوء حظ — احتمالها محسوب ومرتفع."""
    a, _ = _equity_of(0.01)
    svg, x, y = _curves(Wd, H, [(a, INK, 2.8)], base=100.0)
    x0, x1 = x(6), x(13)                       # مواضع السلسلة داخل المتتالية
    svg += (f'<rect x="{x0:.1f}" y="58" width="{x1-x0:.1f}" height="{H-138:.1f}" '
            f'fill="{RED}" opacity="0.10"/>')
    svg += htext((x0 + x1) / 2, H - 74, "سبع خسائر متتالية", RED, 18)
    svg += head(Wd, "منحنى المخاطرة ١٪ عبر ٢٤ صفقة")
    svg += htext(Wd / 2, H - 14,
                 "عند فوز ٥٠٪ وخلال ١٠٠ صفقة: احتمال سلسلة ٦ خسائر ≈ ٥٥٪", INK, 18)
    return svg + badge(Wd, "متوقَّع لا استثنائي", True) + "</svg>"

def dd_cap(Wd=880, H=250, seed=8415):
    """سقف خسارة يومي يقطع المتتالية قبل أن تتحول إلى حفرة."""
    a, _ = _equity_of(0.01)
    capped = a[:9] + [a[8]] * (len(a) - 9)     # التوقف عند بلوغ السقف
    svg, x, y = _curves(Wd, H, [(a, RED, 2.4), (capped, TEAL_D, 2.8)], base=100.0)
    svg += (f'<line x1="{x(8):.1f}" y1="58" x2="{x(8):.1f}" y2="{H-84:.1f}" '
            f'stroke="{TEAL_D}" stroke-width="1.6" stroke-dasharray="6 5"/>')
    svg += htext(x(8), H - 74, "سقف اليوم", TEAL_D, 17)
    svg += head(Wd, "السماوي: توقّف عند السقف · الأحمر: واصل")
    svg += htext(Wd / 2, H - 14, "السقف لا يمنع الخسارة — يمنع تحوّلها إلى تراجع يصعب رده", INK, 18)
    return svg + badge(Wd, "قرار واحد يوقف النزيف", True) + "</svg>"


# ══════════════ 3) ملل — يوم بلا فرصة ══════════════
def bore_quiet(Wd=880, H=250, seed=8421):
    """جلسة كاملة داخل نطاق ضيق: لا هيكل ولا منطقة ولا سبب للدخول."""
    N = 34
    anch = [(0, 13.8), (11, 13.9), (18, 13.7), (26, 13.9), (33, 13.8)]
    W, AH, AL, rng = _box(seed, anch, N, 13, f"ملل هادئ {seed}", squeeze=0.78)
    for j in range(13, N):
        cap(W, j, AH - rng * 0.004); floorc(W, j, AL + rng * 0.004)
    svg, x, y, slot = frame(W, Wd, H)
    svg += zbox(x(0) - slot * .4, y(AH), x(N - 1) + slot * .5, y(AL), op=0.09,
                col=MUTE, stroke=GREY, dash="6 5")
    svg += head(Wd, "السعر لم يغادر النطاق طوال الجلسة")
    svg += note(x(6), "لا كسر… لا منطقة", GREY, H, 17)
    svg += note(x(25), "القرار الصحيح: لا صفقة", TEAL_D, H, 17)
    return svg + badge(Wd, "يوم بلا فرصة", True) + "</svg>"

def bore_forced(Wd=880, H=250, seed=8422):
    """دخول من منتصف النطاق لمجرد الحضور — الوقف يُضرب داخل الضجيج."""
    N = 32
    anch = [(0, 13.4), (10, 13.5), (17, 13.3), (25, 13.5), (31, 13.4)]
    W, AH, AL, rng = _box(seed, anch, N, 12, f"ملل قسري {seed}", squeeze=0.80)
    for j in range(12, N):
        cap(W, j, AH - rng * 0.004); floorc(W, j, AL + rng * 0.004)
    ENT = (AH + AL) / 2
    STP = ENT - (AH - AL) * 0.34
    W[22]["l"] = min(W[22]["l"], STP - (AH - AL) * 0.06)
    svg, x, y, slot = frame(W, Wd, H)
    svg += zbox(x(0) - slot * .4, y(AH), x(N - 1) + slot * .5, y(AL), op=0.08,
                col=MUTE, stroke=GREY, dash="6 5")
    svg += hl(x(16) - slot * .5, x(N - 1) + slot * .5, y(ENT), INK, 1.9)
    svg += hl(x(16) - slot * .5, x(N - 1) + slot * .5, y(STP), RED, 1.6, dash="7 5")
    svg += xm(x(22), y(STP) + 8)
    svg += head(Wd, "المتصل: الدخول · المتقطع: الوقف")
    svg += note(x(6), "دخول من منتصف النطاق", INK, H, 17)
    svg += note(x(24), "الضجيج وحده كفى لضرب الوقف", RED, H, 17)
    return svg + badge(Wd, "صفقة ملل", False) + "</svg>"

def bore_wait(Wd=880, H=250, seed=8423):
    """الفرصة جاءت في آخر الجلسة: سحب أسفل النطاق ثم عودة — من انتظر أخذها."""
    N = 34
    anch = [(0, 13.2), (12, 13.3), (20, 13.1), (24, 12.4), (28, 14.0), (33, 15.4)]
    W, AH, AL, rng = _box(seed, anch, N, 21, f"ملل انتظار {seed}", squeeze=0.72)
    W[24].update(l=AL - rng * 0.06, o=AL + rng * 0.005, c=AL + rng * 0.03, h=AL + rng * 0.045)
    for j in range(25, N):
        floorc(W, j, AL + rng * 0.012)
    svg, x, y, slot = frame(W, Wd, H)
    svg += zbox(x(0) - slot * .4, y(AH), x(21) + slot * .5, y(AL))
    svg += hl(x(0) - slot * .4, x(N - 1) + slot * .5, y(AL), INK, 1.7)
    svg += tick(x(27), y(W[27]["h"]) - 18)
    svg += head(Wd, "٢١ شمعة بلا إشارة… ثم إشارة واحدة")
    svg += note(x(8), "انتظار بلا تنفيذ", GREY, H, 17)
    svg += note(x(28), "السحب ثم العودة ← الدخول", TEAL_D, H, 17)
    return svg + badge(Wd, "الانتظار جزء من العمل", True) + "</svg>"

def bore_budget(Wd=880, H=250, seed=8424):
    """صفقة الملل استهلكت مخاطرة اليوم، فجاءت الفرصة الحقيقية بلا ميزانية."""
    N = 34
    anch = [(0, 13.0), (11, 13.1), (18, 12.9), (23, 12.3), (27, 13.8), (33, 15.2)]
    W, AH, AL, rng = _box(seed, anch, N, 19, f"ملل ميزانية {seed}", squeeze=0.74)
    W[23].update(l=AL - rng * 0.06, o=AL + rng * 0.005, c=AL + rng * 0.03, h=AL + rng * 0.045)
    for j in range(24, N):
        floorc(W, j, AL + rng * 0.012)
    E1 = (AH + AL) / 2
    S1 = E1 - (AH - AL) * 0.32
    W[15]["l"] = min(W[15]["l"], S1 - (AH - AL) * 0.05)
    svg, x, y, slot = frame(W, Wd, H)
    svg += zbox(x(0) - slot * .4, y(AH), x(19) + slot * .5, y(AL), op=0.08,
                col=MUTE, stroke=GREY, dash="6 5")
    svg += hl(x(10) - slot * .5, x(18) + slot * .5, y(E1), INK, 1.8)
    svg += hl(x(10) - slot * .5, x(18) + slot * .5, y(S1), RED, 1.5, dash="7 5")
    svg += xm(x(15), y(S1) + 8)
    svg += tick(x(26), y(W[26]["h"]) - 18)
    svg += head(Wd, "الأولى: صفقة ملل · الثانية: الإشارة الحقيقية")
    svg += note(x(7), "استهلكت مخاطرة اليوم", RED, H, 17)
    svg += note(x(27), "الفرصة جاءت… ولا ميزانية لها", RED, H, 17)
    return svg + badge(Wd, "الثمن الحقيقي للملل", False) + "</svg>"

def bore_count(Wd=880, H=250, seed=8425):
    """أثر عدد الصفقات اليومي على المحصلة — رسم تخطيطي للفكرة لا إحصاء لحساب."""
    items = [("١", 2.0, "مركّزة"), ("٢", 2.6, "مركّزة"), ("٣", 1.4, "مقبولة"),
             ("٤", -0.6, "تتشتّت"), ("٦", -2.2, "ملل"), ("٨", -3.4, "ملل")]
    svg, zy = _signed(Wd, H, items)
    svg += head(Wd, "المحور الأفقي: عدد الصفقات في اليوم")
    svg += htext(Wd / 2, H - 14,
                 "بعد الفرص الحقيقية تبدأ الصفقات التي تُفتح لملء الوقت", INK, 18)
    return svg + badge(Wd, "رسم توضيحي للفكرة", False) + "</svg>"


# ─────────────────────────── الخرائط ───────────────────────────
CAR_CHARTS = {
    "amd":  [amd_map, amd_buy, amd_sell, amd_none, amd_late],
    "dd":   [dd_asym, dd_paths, dd_maxdd, dd_streak, dd_cap],
    "bore": [bore_quiet, bore_forced, bore_wait, bore_budget, bore_count],
}
# غلاف «دروداون»: المنحنيان أوضح من الأعمدة في مساحة الغلاف الصغيرة
HERO = {"amd": amd_map, "dd": dd_paths, "bore": bore_forced}
