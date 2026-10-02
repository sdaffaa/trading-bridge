# -*- coding: utf-8 -*-
"""جارتات تشغيلة 23 — وحدة «أمر معلّق أم تنفيذ فوري؟».
خمس حالات تنفيذ على منطقة واحدة المفهوم: تنفيذ عند السعر، مطاردة، أمر لم يُنفَّذ،
دخول بعد تأكيد، وانزلاق عبر فجوة. البذور تُسجَّل مرة واحدة من run23_build.py.
"""
from reel_build import INK, TEAL, TEAL_D, RED, GREY, MUTE, htext, gen
from run15_charts import zbox, xm, tick, hl, badge, frame, head, note, cap, floorc
import chart_registry

CHARTS = []

def fresh(seed, anch, label):
    chart_registry.assert_fresh_synthetic(seed, anch, label=label)
    CHARTS.append((seed, anch, label))

def _zone(seed, anch, N, i0, i1, label, wick=0.8, thick=0.095):
    """منطقة نشأة من الشموع i0..i1 بارتفاع thick من مدى الجارت.
    اشتقاق الارتفاع من فرق شموع النشأة وحدها يجعله شريطاً غير مقروء حين تتقارب."""
    fresh(seed, anch, label)
    W = gen(anch, N, seed, wick=wick)
    rng = max(c["h"] for c in W) - min(c["l"] for c in W)
    seg = W[i0:i1 + 1]
    ZT = max(max(c["o"], c["c"]) for c in seg)
    ZB = ZT - rng * thick
    for j in range(i0, i1 + 1):                  # قيعان النشأة عند حدّ المنطقة
        W[j]["l"] = min(W[j]["l"], ZB + rng * 0.006)
    return W, ZT, ZB, rng

def _hold_above(W, ZT, rng, a, b):
    """بين النشأة والعودة يبقى السعر فوق المنطقة بوضوح."""
    for j in range(a, b):
        floorc(W, j, ZT + rng * 0.05)

def bracket(x0, y0, y1, col=RED, w=2.2, r=9):
    """قوس رأسي يقيس مسافة بين مستويين."""
    return (f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{x0:.1f}" y2="{y1:.1f}" stroke="{col}" stroke-width="{w}"/>'
            f'<line x1="{x0-r:.1f}" y1="{y0:.1f}" x2="{x0+r:.1f}" y2="{y0:.1f}" stroke="{col}" stroke-width="{w}"/>'
            f'<line x1="{x0-r:.1f}" y1="{y1:.1f}" x2="{x0+r:.1f}" y2="{y1:.1f}" stroke="{col}" stroke-width="{w}"/>')

# مراسٍ ذات قاع واضح: ارتفاع من المنطقة، ثم عودة عميقة إليها، ثم استكمال.
# ٢٦ شمعة لا ٣٠ حتى تتسع أجسام الشموع وتُقرأ العودة من نظرة واحدة.
ANCH = [(0, 16.6), (2, 14.8), (4, 14.6), (9, 18.2), (12, 17.0), (16, 14.8),
        (19, 16.6), (22, 18.0), (25, 19.4)]


# ═══════════ 1) أمر معلّق نُفِّذ عند سعره ═══════════
def ex_limit_hit(Wd=880, H=250, seed=8431):
    N = 26
    W, ZT, ZB, rng = _zone(seed, ANCH, N, 2, 4, f"تنفيذ معلّق {seed}")
    _hold_above(W, ZT, rng, 5, 15)
    LIM = ZB + (ZT - ZB) * 0.50
    for j in (15, 16, 17):                       # العودة تدخل المنطقة
        W[j]["l"] = min(W[j]["l"], LIM - rng * 0.008)
        floorc(W, j, ZB + rng * 0.004)
        W[j]["h"] = max(W[j]["h"], max(W[j]["o"], W[j]["c"]) + rng * 0.014)
    for j in range(18, N):
        floorc(W, j, ZT)
    STP = ZB - rng * 0.045
    svg, x, y, slot = frame(W, Wd, H)
    svg += zbox(x(1) - slot * .5, y(ZT), x(N - 1) + slot * .5, y(ZB))
    svg += hl(x(11) - slot * .5, x(N - 1) + slot * .5, y(LIM), INK, 1.9, dash="9 5")
    svg += hl(x(9) - slot * .5, x(N - 1) + slot * .5, y(STP), RED, 1.6, dash="7 5")
    svg += tick(x(18), y(W[18]["h"]) - 18)
    svg += head(Wd, "المتقطع الداكن: أمر معلّق · الأحمر: الوقف")
    svg += note(x(5), "منطقة النشأة", TEAL_D, H, 17)
    svg += note(x(20), "نُفِّذ عند سعرك تماماً", TEAL_D, H, 17)
    return svg + badge(Wd, "تنفيذ عند السعر المطلوب", True) + "</svg>"


# ═══════════ 2) تنفيذ فوري بعد أن تحرك السعر ═══════════
def ex_market_chase(Wd=880, H=250, seed=8432):
    N = 26
    W, ZT, ZB, rng = _zone(seed, ANCH, N, 2, 4, f"تنفيذ مطاردة {seed}")
    _hold_above(W, ZT, rng, 5, 15)
    LIM = ZB + (ZT - ZB) * 0.50
    for j in (15, 16):
        W[j]["l"] = min(W[j]["l"], LIM - rng * 0.006)
        floorc(W, j, ZB + rng * 0.004)
    for j in range(17, N):
        floorc(W, j, ZT)
    ENT = W[20]["c"]                              # الدخول بالسوق بعد الارتداد
    STP = ZB - rng * 0.045
    svg, x, y, slot = frame(W, Wd, H, pr=52)
    svg += zbox(x(1) - slot * .5, y(ZT), x(N - 1) + slot * .5, y(ZB))
    svg += hl(x(11) - slot * .5, x(N - 1) + slot * .5, y(LIM), MUTE, 1.6, dash="6 5")
    svg += hl(x(19) - slot * .5, x(N - 1) + slot * .5, y(ENT), INK, 2.0)
    svg += hl(x(9) - slot * .5, x(N - 1) + slot * .5, y(STP), RED, 1.6, dash="7 5")
    svg += bracket(x(N - 1) + slot * 1.0, y(ENT), y(LIM))
    svg += head(Wd, "الرمادي: سعر المنطقة · المتصل: سعر التنفيذ")
    svg += note(x(5), "المنطقة", GREY, H, 17)
    svg += note(x(20), "المسافة الزائدة تُقتطع من العائد", RED, H, 17)
    return svg + badge(Wd, "الوقف نفسه… والهدف أبعد", False) + "</svg>"


# ═══════════ 3) أمر معلّق لم يُنفَّذ ═══════════
def ex_limit_miss(Wd=880, H=250, seed=8433):
    N = 26
    W, ZT, ZB, rng = _zone(seed, ANCH, N, 2, 4, f"معلّق لم يُنفَّذ {seed}", thick=0.15)
    _hold_above(W, ZT, rng, 5, 15)
    LIM = ZB + (ZT - ZB) * 0.15                  # الأمر في عمق المنطقة
    for j in (15, 16):                           # السعر يلمس الحافة العليا فقط
        W[j]["l"] = min(W[j]["l"], ZT - (ZT - ZB) * 0.18)
        floorc(W, j, ZB + (ZT - ZB) * 0.42)
    for j in range(17, N):
        floorc(W, j, ZT)
    svg, x, y, slot = frame(W, Wd, H)
    svg += zbox(x(1) - slot * .5, y(ZT), x(N - 1) + slot * .5, y(ZB))
    svg += hl(x(11) - slot * .5, x(N - 1) + slot * .5, y(LIM), INK, 1.9, dash="9 5")
    svg += xm(x(16) + slot * 1.6, y(LIM), r=10)
    svg += head(Wd, "المتقطع: أمر معلّق في عمق المنطقة")
    svg += note(x(5), "المنطقة", TEAL_D, H, 17)
    svg += note(x(20), "انعكس قبل أن يبلغ أمرك", RED, H, 17)
    return svg + badge(Wd, "لم يُنفَّذ — فرصة فائتة", False) + "</svg>"


# ═══════════ 4) تنفيذ فوري بعد تأكيد ═══════════
def ex_market_confirm(Wd=880, H=250, seed=8434):
    N = 26
    W, ZT, ZB, rng = _zone(seed, ANCH, N, 2, 4, f"تنفيذ بتأكيد {seed}")
    _hold_above(W, ZT, rng, 5, 15)
    for j in (15, 16):
        W[j]["l"] = min(W[j]["l"], ZB + (ZT - ZB) * 0.30)
        floorc(W, j, ZB + rng * 0.004)
    W[17].update(o=ZT - (ZT - ZB) * 0.4, c=ZT + rng * 0.055,   # شمعة العودة فوق المنطقة
                 l=ZB + (ZT - ZB) * 0.2, h=ZT + rng * 0.075)
    for j in range(18, N):
        floorc(W, j, ZT + rng * 0.02)
    ENT = W[17]["c"]
    STP = ZB - rng * 0.045
    svg, x, y, slot = frame(W, Wd, H)
    svg += zbox(x(1) - slot * .5, y(ZT), x(N - 1) + slot * .5, y(ZB))
    svg += hl(x(16) - slot * .5, x(N - 1) + slot * .5, y(ENT), INK, 2.0)
    svg += hl(x(9) - slot * .5, x(N - 1) + slot * .5, y(STP), RED, 1.6, dash="7 5")
    svg += tick(x(19), y(W[19]["h"]) - 18)
    svg += head(Wd, "الدخول عند إغلاق شمعة عادت فوق المنطقة")
    svg += note(x(5), "المنطقة", TEAL_D, H, 17)
    svg += note(x(20), "سعر أسوأ مقابل شرط متحقق", TEAL_D, H, 17)
    return svg + badge(Wd, "مقايضة معلنة", True) + "</svg>"


# ═══════════ 5) انزلاق عبر فجوة ═══════════
def ex_slip(Wd=880, H=250, seed=8435):
    N = 26
    W, ZT, ZB, rng = _zone(seed, ANCH, N, 2, 4, f"انزلاق فجوة {seed}")
    _hold_above(W, ZT, rng, 5, 14)
    LIM = ZB + (ZT - ZB) * 0.50
    W[14]["l"] = min(W[14]["l"], ZT + rng * 0.02)
    FILL = ZB - rng * 0.085                       # سعر التنفيذ الفعلي بعد الفجوة
    W[15].update(o=FILL, c=FILL - rng * 0.02, h=FILL + rng * 0.012,
                 l=FILL - rng * 0.05)             # فجوة هابطة تعبر سعر الأمر
    for j in range(16, N):
        floorc(W, j, FILL - rng * 0.06)
    svg, x, y, slot = frame(W, Wd, H, pr=52)
    svg += zbox(x(1) - slot * .5, y(ZT), x(N - 1) + slot * .5, y(ZB))
    svg += hl(x(11) - slot * .5, x(N - 1) + slot * .5, y(LIM), INK, 1.9, dash="9 5")
    svg += hl(x(13) - slot * .5, x(N - 1) + slot * .5, y(FILL), RED, 2.0)
    svg += bracket(x(N - 1) + slot * 1.0, y(LIM), y(FILL))
    svg += head(Wd, "المتقطع: سعر أمرك · الأحمر: سعر التنفيذ")
    svg += note(x(5), "المنطقة", GREY, H, 17)
    svg += note(x(20), "الفجوة نفّذت الأمر أدنى بكثير", RED, H, 17)
    return svg + badge(Wd, "الانزلاق يوسّع مخاطرتك", False) + "</svg>"


CAR_CHARTS = {"limit": [ex_limit_hit, ex_market_chase, ex_limit_miss,
                        ex_market_confirm, ex_slip]}
HERO = {"limit": ex_limit_hit}
