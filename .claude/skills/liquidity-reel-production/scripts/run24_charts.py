# -*- coding: utf-8 -*-
"""جارتات تشغيلة 24 — ثلاث وحدات نفسية: احتمالات · مبكر · تردد.
كل الأرقام الإحصائية محسوبة بمحاكاة ذات بذرة ثابتة (انظر _sim) لا مقدّرة.
البذور السعرية تُسجَّل مرة واحدة من run24_build.py.
"""
import random
from reel_build import INK, TEAL, TEAL_D, RED, GREY, MUTE, htext, gen
from run15_charts import zbox, xm, tick, hl, badge, frame, head, note, cap, floorc
from run22_charts import _grid, _curves, _pairbars, _signed
import chart_registry

CHARTS = []
_AR = str.maketrans("0123456789", "٠١٢٣٤٥٦٧٨٩")
def ar(v, d=0):
    return (f"%.{d}f" % v).replace(".", "٫").translate(_AR)

def fresh(seed, anch, label):
    chart_registry.assert_fresh_synthetic(seed, anch, label=label)
    CHARTS.append((seed, anch, label))

# ───────── نموذج واحد لكل الوحدة: عائد/مخاطرة ٢ ونسبة فوز ٤٠٪ (توقع +٠٫٢R) ─────────
RR, WR = 2.0, 0.40

def _paths(n, k, seed):
    rng = random.Random(seed)
    out = []
    for _ in range(k):
        v, cur = 0.0, [0.0]
        for _ in range(n):
            v += RR if rng.random() < WR else -1.0
            cur.append(v)
        out.append(cur)
    return out

def _finals(n, k, seed):
    rng = random.Random(seed)
    return sorted(sum(RR if rng.random() < WR else -1.0 for _ in range(n)) for _ in range(k))


# ══════════════ 1) احتمالات — الصفقة الواحدة ليست حكماً ══════════════
def pb_paths(Wd=880, H=250, seed=8501):
    """ست عيّنات من عشرين صفقة بالنموذج ذاته: بعضها يصعد وبعضها يهبط."""
    ps = _paths(20, 6, 4603)   # بذرة تُظهر عيّنتين خاسرتين من ست
    ser = [(p, RED if p[-1] < 0 else TEAL_D, 2.2) for p in ps]
    svg, x, y = _curves(Wd, H, ser, base=0.0)
    svg += head(Wd, "ست عيّنات · عشرون صفقة لكل عيّنة · النموذج نفسه")
    svg += htext(Wd / 2, H - 14, "المنحنى الأحمر ليس نموذجاً فاشلاً — بل العيّنة نفسها بحظّ مختلف", INK, 18)
    return svg + badge(Wd, "عشرون صفقة لا تحكم", False) + "</svg>"

def pb_spread(Wd=880, H=250, seed=8502):
    """التشتت يضيق مع طول العيّنة: ٢٠ ثم ١٠٠ ثم ٥٠٠ صفقة."""
    rows = []
    for n in (20, 100, 500):
        xs = _finals(n, 4000, 4601)
        p5, p50, p95 = xs[200], xs[2000], xs[3800]
        neg = sum(1 for v in xs if v < 0) / len(xs) * 100
        rows.append((n, p5 / n, p50 / n, p95 / n, neg))
    s, pl, pr, pt, pb = _grid(Wd, H, 58, 104)
    lo, hi = -0.65, 0.75
    ypx = lambda v: pt + (hi - v) / (hi - lo) * (H - pt - pb)
    s.append(f'<line x1="{pl}" y1="{ypx(0):.1f}" x2="{Wd-pr}" y2="{ypx(0):.1f}" '
             f'stroke="{MUTE}" stroke-width="1.4" stroke-dasharray="6 5"/>')
    gw = (Wd - pl - pr) / 3
    for i, (n, a, m, b, neg) in enumerate(rows):
        cx = pl + gw * (i + 0.5)
        s.append(f'<rect x="{cx-46:.1f}" y="{ypx(b):.1f}" width="92" height="{ypx(a)-ypx(b):.1f}" '
                 f'fill="{TEAL}" opacity="0.20"/>')
        s.append(f'<line x1="{cx-52:.1f}" y1="{ypx(m):.1f}" x2="{cx+52:.1f}" y2="{ypx(m):.1f}" '
                 f'stroke="{INK}" stroke-width="2.6"/>')
        s.append(htext(cx, ypx(b) - 12, f"+{ar(b,2)}R", TEAL_D, 17))
        s.append(htext(cx, ypx(a) + 26, f"{ar(a,2)}R", RED, 17))
        s.append(htext(cx, H - pb + 42, f"{ar(n)} صفقة", INK, 20))
        s.append(htext(cx, H - pb + 70, f"خاسرة {ar(neg,1)}٪", GREY, 17))
    svg = "".join(s)
    svg += head(Wd, "متوسط الربح لكل صفقة · النطاق ٥٪–٩٥٪")
    return svg + badge(Wd, "التشتت يضيق بالعدد", True) + "</svg>"

def pb_hist(Wd=880, H=250, seed=8503):
    """توزيع محصلة مئة صفقة: المنطقة السالبة موجودة رغم أفضلية موجبة."""
    xs = _finals(100, 4000, 4601)
    lo, hi, nb = -30, 70, 25
    w = (hi - lo) / nb
    bins = [0] * nb
    for v in xs:
        k = min(nb - 1, max(0, int((v - lo) / w)))
        bins[k] += 1
    neg = sum(1 for v in xs if v < 0) / len(xs) * 100
    s, pl, pr, pt, pb = _grid(Wd, H, 58, 96)
    mx = max(bins); bw = (Wd - pl - pr) / nb
    y0 = H - pb
    for i, c in enumerate(bins):
        h = c / mx * (H - pt - pb - 16)
        col = RED if lo + w * (i + 1) <= 0 else TEAL_D
        s.append(f'<rect x="{pl+i*bw+1.5:.1f}" y="{y0-h:.1f}" width="{bw-3:.1f}" height="{h:.1f}" '
                 f'fill="{col}" opacity="0.72"/>')
    zx = pl + (0 - lo) / (hi - lo) * (Wd - pl - pr)
    s.append(f'<line x1="{zx:.1f}" y1="{pt}" x2="{zx:.1f}" y2="{y0:.1f}" stroke="{INK}" stroke-width="2"/>')
    s.append(htext(zx, y0 + 28, "صفر", INK, 18))
    svg = "".join(s)
    svg += head(Wd, "محصلة أربعة آلاف عيّنة · مئة صفقة لكل عيّنة")
    svg += htext(Wd / 2, H - 14, f"‏{ar(neg,1)}٪ من العيّنات انتهت خاسرة رغم أن النموذج رابح", RED, 18)
    return svg + badge(Wd, "الخسارة واردة بلا خطأ", False) + "</svg>"

def pb_streak(Wd=880, H=250, seed=8504):
    """مئة نتيجة متتابعة: الخسائر تتجمّع طبيعياً لا لسبب."""
    rng = random.Random(915)
    res = [rng.random() < WR for _ in range(100)]
    best = run = bi = 0
    cur = 0
    for i, w in enumerate(res):
        if w:
            run = 0; cur = i + 1
        else:
            run += 1
            if run > best: best, bi = run, cur
    import run15_charts as _R15
    sc = _R15.SCALE
    cols, rows = 20, 5
    top = round(120 * sc); bot = H - round(96 * sc)
    ch = (bot - top) / rows - 8
    cw, x0, y0 = (Wd - 80) / cols, 40, top
    s = [f'<svg class="chartsvg" viewBox="0 0 {Wd} {H}" width="{Wd}" height="{H}" '
         f'xmlns="http://www.w3.org/2000/svg">']
    for i, w in enumerate(res):
        cx = x0 + (i % cols) * cw; cy = y0 + (i // cols) * (ch + 8)
        inrun = bi <= i < bi + best
        s.append(f'<rect x="{cx+2:.1f}" y="{cy:.1f}" width="{cw-4:.1f}" height="{ch:.1f}" '
                 f'fill="{TEAL_D if w else RED}" opacity="{0.9 if inrun else (0.8 if w else 0.4)}"/>')
    svg = "".join(s)
    svg += head(Wd, "مئة صفقة بالترتيب · السماوي رابح والأحمر خاسر")
    svg += htext(Wd / 2, H - 14,
                 f"أطول سلسلة خسائر هنا {ar(best)} — والوسيط المتوقع سبع خسائر في كل مئة", INK, 18)
    return svg + badge(Wd, "التجمّع طبيعي", True) + "</svg>"

def pb_matrix(Wd=880, H=250, seed=8505):
    """القرار والنتيجة أمران منفصلان: أربع حالات لا اثنتان."""
    cells = [("قرار صحيح · نتيجة رابحة", TEAL_D, "استحقاق"),
             ("قرار صحيح · نتيجة خاسرة", TEAL, "ثمن عادل"),
             ("قرار خاطئ · نتيجة رابحة", RED, "مكافأة خادعة"),
             ("قرار خاطئ · نتيجة خاسرة", RED, "درس مستحَق")]
    s = [f'<svg class="chartsvg" viewBox="0 0 {Wd} {H}" width="{Wd}" height="{H}" '
         f'xmlns="http://www.w3.org/2000/svg">']
    import run15_charts as _R15
    sc = _R15.SCALE
    top = round(120 * sc); bot = H - round(96 * sc)
    cw, chh = (Wd - 100) / 2, (bot - top) / 2 - 16
    for i, (lab, col, verdict) in enumerate(cells):
        cx = 50 + (i % 2) * cw; cy = top + (i // 2) * (chh + 24)
        s.append(f'<rect x="{cx:.1f}" y="{cy}" width="{cw-14:.1f}" height="{chh:.1f}" '
                 f'fill="{col}" opacity="0.10"/>')
        s.append(f'<rect x="{cx:.1f}" y="{cy}" width="{cw-14:.1f}" height="{chh:.1f}" fill="none" '
                 f'stroke="{col}" stroke-width="1.3"/>')
        s.append(htext(cx + (cw - 14) / 2, cy + chh * 0.42, lab, INK, round(19 * sc)))
        s.append(htext(cx + (cw - 14) / 2, cy + chh * 0.72, verdict, col, round(18 * sc)))
    svg = "".join(s)
    svg += head(Wd, "النتيجة لا تُقيّم القرار")
    svg += htext(Wd / 2, H - 14, "الخانة الحمراء العلوية أخطرها: ربح كافأ قراراً خاطئاً", RED, 18)
    return svg + badge(Wd, "قيّم القرار لا النتيجة", True) + "</svg>"


# ══════════════ 2) مبكر — الخروج قبل الهدف ══════════════
_TRADE = None
def _trade():
    """بيانات صفقة واحدة تُستعمل في رسمين: الهدف الكامل والخروج المبكر."""
    global _TRADE
    if _TRADE is None:
        anch = [(0, 14.8), (3, 13.6), (6, 13.2), (10, 14.4), (14, 15.6),
                (18, 16.8), (22, 17.6), (27, 18.4)]
        fresh(8511, anch, "صفقة الهدف الكامل 8511")
        W = gen(anch, 28, 8511, wick=0.78)
        rng = max(c["h"] for c in W) - min(c["l"] for c in W)
        ENT = W[8]["c"]; STP = ENT - rng * 0.12
        for j in range(9, 28):
            floorc(W, j, STP + rng * 0.02)
        _TRADE = (W, ENT, STP, rng)
    return _TRADE

def em_full(Wd=880, H=250, seed=8511):
    W, ENT, STP, rng = _trade()
    R = ENT - STP; TGT = ENT + 2 * R
    svg, x, y, slot = frame(W, Wd, H)
    svg += hl(x(7) - slot * .5, x(27) + slot * .5, y(ENT), INK, 2.0)
    svg += hl(x(7) - slot * .5, x(27) + slot * .5, y(STP), RED, 1.6, dash="7 5")
    svg += hl(x(7) - slot * .5, x(27) + slot * .5, y(TGT), TEAL_D, 1.9)
    svg += tick(x(24), y(TGT) - 20)
    svg += head(Wd, "المتصل: الدخول · المتقطع: الوقف · العلوي: الهدف")
    svg += note(x(5), "الدخول", INK, H, 17)
    svg += note(x(21), "بلغ الهدف ٢R كاملاً", TEAL_D, H, 17)
    return svg + badge(Wd, "خطة نُفِّذت كما كُتبت", True) + "</svg>"

def em_cut(Wd=880, H=250, seed=8512):
    """الحركة ذاتها: الخروج عند نصف R والسعر يواصل إلى الهدف."""
    W, ENT, STP, rng = _trade()
    R = ENT - STP; TGT = ENT + 2 * R; CUT = ENT + 0.5 * R
    svg, x, y, slot = frame(W, Wd, H)
    svg += hl(x(7) - slot * .5, x(27) + slot * .5, y(ENT), INK, 2.0)
    svg += hl(x(7) - slot * .5, x(27) + slot * .5, y(STP), RED, 1.6, dash="7 5")
    svg += hl(x(7) - slot * .5, x(27) + slot * .5, y(TGT), MUTE, 1.5, dash="6 5")
    svg += hl(x(11) - slot * .5, x(27) + slot * .5, y(CUT), RED, 2.0)
    svg += xm(x(12), y(CUT) - 4, r=10)
    svg += head(Wd, "الأحمر المتصل: خروج مبكر · الرمادي: الهدف المتروك")
    svg += note(x(5), "الدخول نفسه", INK, H, 17)
    svg += note(x(21), "خرج بـ٠٫٥R ثم واصل إلى ٢R", RED, H, 17)
    return svg + badge(Wd, "ربع الحركة فقط", False) + "</svg>"

def em_math(Wd=880, H=250, seed=8513):
    """حتى مع نسبة فوز أعلى للهدف الأقرب، يبقى التوقع أقل."""
    rows = []
    for tp, wr, lab in ((2.0, 0.40, "٢R"), (1.0, 0.55, "١R"), (0.5, 0.70, "٠٫٥R")):
        e = wr * tp - (1 - wr)
        rows.append((f"هدف {lab}", e, f"{'+' if e>=0 else ''}{ar(e,2)}R"))
    svg, zy = _signed(Wd, H, rows)
    svg += head(Wd, "التوقع لكل صفقة · نسبة الفوز تُمنح للهدف الأقرب")
    svg += htext(Wd / 2, H - 14,
                 "٢R بفوز ٤٠٪ · ١R بفوز ٥٥٪ · ٠٫٥R بفوز ٧٠٪ — والأعلى ما زال الأبعد", INK, 18)
    return svg + badge(Wd, "الهدف الأقرب لا يعوّض", False) + "</svg>"

def em_asym(Wd=880, H=250, seed=8514):
    """قطف الرابحة وترك الخاسرة كاملة يقلب التوقع إلى سالب."""
    rng = random.Random(2211)
    seq = [rng.random() < WR for _ in range(60)]
    disc = [0.0]; plan = [0.0]
    for w in seq:
        disc.append(disc[-1] + (RR if w else -1.0))
        plan.append(plan[-1] + (0.5 if w else -1.0))
    svg, x, y = _curves(Wd, H, [(disc, TEAL_D, 2.6), (plan, RED, 2.6)], base=0.0)
    svg += head(Wd, "السماوي: الخطة · الأحمر: قطف الربح وترك الخسارة")
    svg += htext(Wd / 2, H - 46, f"الفارق بعد ستين صفقة: {ar(disc[-1]-plan[-1],0)}R", RED, 19)
    svg += htext(Wd / 2, H - 14, "الإشارات واحدة — والفارق كله في لحظة الخروج", INK, 18)
    return svg + badge(Wd, "سلوك غير متماثل", False) + "</svg>"

def em_partial(Wd=880, H=250, seed=8515):
    """الخروج الجزئي ليس مجانياً: يمحو الأفضلية ما لم ينقذ وقفُ التعادل ثلث الخسائر.
    نصف عند 1R ونصف عند 2R => الرابحة 1.5R. التوقع = 0.4*1.5 - 0.6*(1-x)
    ويساوي الخطة الكاملة (+0.20R) عند x = ثلث الخسائر بالضبط."""
    rng = random.Random(3307)
    seq = [rng.random() < WR for _ in range(60)]
    save = random.Random(4408)
    full, bare, withbe = [0.0], [0.0], [0.0]
    for w in seq:
        full.append(full[-1] + (RR if w else -1.0))
        bare.append(bare[-1] + (1.5 if w else -1.0))
        if w:
            withbe.append(withbe[-1] + 1.5)
        else:                                   # وقف التعادل ينقذ ٤٠٪ من الخسائر
            withbe.append(withbe[-1] + (0.0 if save.random() < 0.40 else -1.0))
    svg, x, y = _curves(Wd, H, [(full, TEAL_D, 2.6), (withbe, INK, 2.4), (bare, RED, 2.4)],
                        base=0.0)
    svg += head(Wd, "السماوي: هدف كامل · الداكن: جزئي مع وقف تعادل · الأحمر: جزئي بلا وقف")
    svg += htext(Wd / 2, H - 46, "الجزئي بلا وقف تعادل: التوقع صفر بالضبط", RED, 19)
    svg += htext(Wd / 2, H - 14,
                 "لا يعادل الخطة إلا إذا أنقذ وقفُ التعادل ثلث خسائرك على الأقل", INK, 18)
    return svg + badge(Wd, "الجزئي ليس مجانياً", False) + "</svg>"


# ══════════════ 3) تردد — الشلل عند الإشارة ══════════════
_H_ANCH = [(0, 15.6), (4, 14.2), (7, 13.7), (11, 14.9), (15, 16.2), (20, 17.4), (26, 18.2)]

def hz_missed(Wd=880, H=250, seed=8521):
    """الإعداد اكتمل بشروطه ولم يُنفَّذ — والسعر ذهب إلى الهدف."""
    fresh(seed, _H_ANCH, f"تردد إشارة فائتة {seed}")
    W = gen(_H_ANCH, 27, seed, wick=0.78)
    rng = max(c["h"] for c in W) - min(c["l"] for c in W)
    ENT = W[9]["c"]; STP = ENT - rng * 0.11; TGT = ENT + (ENT - STP) * 2
    for j in range(10, 27):
        floorc(W, j, STP + rng * 0.02)
    svg, x, y, slot = frame(W, Wd, H)
    svg += hl(x(8) - slot * .5, x(26) + slot * .5, y(ENT), MUTE, 1.8, dash="8 5")
    svg += hl(x(8) - slot * .5, x(26) + slot * .5, y(STP), MUTE, 1.4, dash="5 5")
    svg += hl(x(8) - slot * .5, x(26) + slot * .5, y(TGT), TEAL_D, 1.8)
    svg += xm(x(10), y(ENT) - 4, r=10)
    svg += head(Wd, "المتقطع الرمادي: إشارة مكتملة لم تُنفَّذ")
    svg += note(x(5), "الشرط تحقّق", GREY, H, 17)
    svg += note(x(21), "الحركة تمّت بلا صاحبها", RED, H, 17)
    return svg + badge(Wd, "إشارة صحيحة… بلا تنفيذ", False) + "</svg>"

def hz_chase(Wd=880, H=250, seed=8522):
    """بعد أن ذهبت المسافة يأتي الدخول بوقف واسع ونسبة مقلوبة."""
    anch = [(0, 15.4), (4, 14.0), (8, 13.6), (12, 15.2), (16, 16.8), (21, 17.6), (26, 17.0)]
    fresh(seed, anch, f"تردد مطاردة {seed}")
    W = gen(anch, 27, seed, wick=0.78)
    rng = max(c["h"] for c in W) - min(c["l"] for c in W)
    ENT = W[20]["c"]; STP = ENT - rng * 0.19
    for j in range(23, 27):
        cap(W, j, ENT - rng * 0.02)
    W[25]["l"] = min(W[25]["l"], STP - rng * 0.02)
    svg, x, y, slot = frame(W, Wd, H)
    svg += hl(x(19) - slot * .5, x(26) + slot * .5, y(ENT), INK, 2.0)
    svg += hl(x(19) - slot * .5, x(26) + slot * .5, y(STP), RED, 1.6, dash="7 5")
    svg += xm(x(25), y(STP) + 8)
    svg += head(Wd, "المتصل: دخول متأخر · المتقطع: وقف اتّسع")
    svg += note(x(6), "الإشارة كانت هنا", GREY, H, 17)
    svg += note(x(21), "الدخول بعد أن ذهبت المسافة", RED, H, 17)
    return svg + badge(Wd, "التردد ثم المطاردة", False) + "</svg>"

def hz_cost(Wd=880, H=250, seed=8523):
    """عشر إشارات: أربع نُفِّذت — والمحصلة تتبع الانتقاء لا النموذج."""
    rng = random.Random(5150)
    seq = [rng.random() < WR for _ in range(10)]
    allr = [0.0]; picked = [0.0]
    take = {0, 1, 4, 7}                       # المنفَّذة فعلاً
    for i, w in enumerate(seq):
        r = RR if w else -1.0
        allr.append(allr[-1] + r)
        picked.append(picked[-1] + (r if i in take else 0.0))
    svg, x, y = _curves(Wd, H, [(allr, TEAL_D, 2.6), (picked, RED, 2.6)], base=0.0)
    svg += head(Wd, "السماوي: تنفيذ كل إشارة · الأحمر: أربع من عشر")
    svg += htext(Wd / 2, H - 14,
                 "الانتقاء بالمزاج يحذف الرابحات والخاسرات معاً — بلا قاعدة تفرّق", INK, 18)
    return svg + badge(Wd, "انتقاء بلا قاعدة", False) + "</svg>"

def hz_trigger(Wd=880, H=250, seed=8524):
    """أمر معلّق مكتوب قبل الجلسة يزيل قرار اللحظة."""
    anch = [(0, 15.8), (4, 14.4), (8, 13.8), (12, 14.2), (16, 15.6), (21, 17.0), (26, 18.0)]
    fresh(seed, anch, f"تردد زناد {seed}")
    W = gen(anch, 27, seed, wick=0.78)
    rng = max(c["h"] for c in W) - min(c["l"] for c in W)
    LIM = W[8]["l"] + rng * 0.02
    for j in (11, 12):
        W[j]["l"] = min(W[j]["l"], LIM - rng * 0.006)
        floorc(W, j, LIM - rng * 0.02)
    for j in range(13, 27):
        floorc(W, j, LIM + rng * 0.02)
    svg, x, y, slot = frame(W, Wd, H)
    svg += hl(x(6) - slot * .5, x(26) + slot * .5, y(LIM), INK, 1.9, dash="9 5")
    svg += tick(x(14), y(W[14]["h"]) - 18)
    svg += head(Wd, "المتقطع: أمر موضوع قبل الجلسة لا عندها")
    svg += note(x(5), "الشرط مكتوب مسبقاً", TEAL_D, H, 17)
    svg += note(x(21), "نُفِّذ بلا قرار لحظي", TEAL_D, H, 17)
    return svg + badge(Wd, "الزناد يُسحب مسبقاً", True) + "</svg>"

def hz_afterloss(Wd=880, H=250, seed=8525):
    """التردد يشتد بعد الخسائر فتفوت الصفقة التي كانت ستعوّض."""
    seq = [False, False, False, False, True, True, False, True, True, True, False, True]
    cur = [0.0]
    for w in seq:
        cur.append(cur[-1] + (RR if w else -1.0))
    miss = 4                                   # أول رابحة بعد السلسلة لم تُنفَّذ
    skipped = cur[:miss + 1] + [cur[miss]] * (len(cur) - miss - 1)
    svg, x, y = _curves(Wd, H, [(cur, TEAL_D, 2.6), (skipped, RED, 2.4)], base=0.0)
    svg += xm(x(miss + 1), y(cur[miss + 1]), r=11)
    svg += head(Wd, "السماوي: التزام كامل · الأحمر: توقّف بعد السلسلة")
    svg += htext(Wd / 2, H - 14,
                 "الصفقة التي تلي السلسلة هي أكثر ما يُترك — وهي التي تعيد المنحنى", RED, 18)
    return svg + badge(Wd, "التوقف بعد الخسائر", False) + "</svg>"


CAR_CHARTS = {
    "prob":  [pb_paths, pb_spread, pb_hist, pb_streak, pb_matrix],
    "early": [em_full, em_cut, em_math, em_asym, em_partial],
    "hesit": [hz_missed, hz_chase, hz_cost, hz_trigger, hz_afterloss],
}
HERO = {"prob": pb_paths, "early": em_cut, "hesit": hz_missed}
