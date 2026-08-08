# -*- coding: utf-8 -*-
"""أثاث شاشة المنصة: محور سعر يميناً · محور وقت أسفل · شبكة · وسم الرمز والفريم.

ليس استنساخاً لمنصة بعينها ولا يحمل شعارها: هذه اصطلاحات عرض الجارت المشتركة
بين المنصات (السعر يمين · الوقت أسفل · لصيقة السعر الحي)، بألوان الحساب وتوقيعه.

يُرسم كله في طبقة pre_svg تحت الشموع، فلا يغطي شمعة ولا ماركب.
"""
# القياسات تُقرأ عند النداء لا عند الاستيراد: set_canvas/set_pad تُنفَّذان بعد الاستيراد،
# واستيراد القيم يجمّد لوحة المحرك الافتراضية فيُرسم الأثاث لمقاس آخر.
import reel_sfx_kit as _K
from reel_sfx_kit import plot_box, price_scale

# لوحتان: الفاتحة هي لوحة جسم الشرح في الهوية، والداكنة للغلاف والافتتاحية
LIGHT = dict(BG="#FBF9F5", GRID="rgba(15,46,60,0.075)", AXBD="rgba(15,46,60,0.17)",
             AXTX="#6B7C84", LEGT="#0F2E3C", WMK="rgba(15,46,60,0.055)",
             LVL="#0F2E3C", PILL="#1E627A", PILLTX="#FBF9F5")
DARK = dict(BG="#0B1520", GRID="rgba(255,255,255,0.045)", AXBD="rgba(255,255,255,0.10)",
            AXTX="#7F97A1", LEGT="#D8E5EB", WMK="rgba(216,229,235,0.055)",
            LVL="#D8E5EB", PILL="#43D4DC", PILLTX="#08131C")
T = LIGHT

def set_theme(name="light"):
    """يبدّل لوحة الأثاث. الافتراضي فاتح: جسم الشرح في الهوية أوف-وايت."""
    global T, BG, GRID, AXBD, AXTX, LEGT, WMK
    T = LIGHT if name == "light" else DARK
    BG, GRID, AXBD, AXTX, LEGT, WMK = (T["BG"], T["GRID"], T["AXBD"],
                                       T["AXTX"], T["LEGT"], T["WMK"])

BG = T["BG"]; GRID = T["GRID"]; AXBD = T["AXBD"]
AXTX = T["AXTX"]; LEGT = T["LEGT"]; WMK = T["WMK"]


def _step(span, target=6):
    """خطوة سعرية «مستديرة» — المحاور تقرأ كمنصة لا كأرقام عشوائية."""
    raw = span / max(target, 1)
    import math
    mag = 10 ** math.floor(math.log10(raw)) if raw > 0 else 1
    for m in (1, 2, 2.5, 5, 10):
        if raw <= mag * m:
            return mag * m
    return mag * 10


def furniture(W, dec=2, sym="GC=F", tf="15m", tlabels=None, ticks=6, split=False):
    """أثاث اللوحة تحت الشموع.

    `split=True` يُرجع (ثابت، متحرّك) بدل نصٍّ واحد: محور السعر والشبكة
    الأفقية والعلامة المائية لا تتحرّك، أمّا خطوط الوقت الرأسية ووسومها
    فتنزلق مع الشموع. يلزم هذا في وضع الريبلاي (تمرير الجارت أفقياً)،
    وإلا بقيت الساعات ثابتة تحت شموعٍ تمشي — وهو ما لا يقع في منصّة."""
    pl, pr, pt, pb, pw, ph = plot_box()
    CW, CH = _K.CW, _K.CH
    ymin, ymax = price_scale(W)
    x0, x1 = pl, CW - pr
    ytop, ybot = pt, CH - pb
    py = lambda v: pt + (ymax - v) / (ymax - ymin) * ph

    g = [f'<rect x="0" y="0" width="{CW}" height="{CH}" fill="{BG}"/>']
    tg = []                                   # الطبقة المنزلقة (محور الوقت)

    # ── الشبكة وأرقام السعر ──
    st = _step(ymax - ymin, ticks)
    v = (int(ymin / st) + 1) * st
    while v < ymax:
        yy = py(v)
        g.append(f'<line x1="{x0}" y1="{yy:.1f}" x2="{x1}" y2="{yy:.1f}" stroke="{GRID}" stroke-width="1.4"/>')
        g.append(f'<text x="{x1 + 9}" y="{yy + 6:.1f}" fill="{AXTX}" font-size="19" font-weight="600" '
                 f'font-family="system-ui,sans-serif" direction="ltr">{v:,.{dec}f}</text>')
        v += st

    # ── الوقت أسفل ──
    if tlabels:
        every = max(1, len(tlabels) // 6)
        slot = pw / _K.vis_n(len(W))
        for i in range(0, len(tlabels), every):
            xx = x0 + slot * i + slot / 2
            if xx < x0 + 34:          # أول وسم يفيض عن الحافة اليسرى
                continue
            if xx > x1 - 30:
                break
            (tg if split else g).append(
                f'<line x1="{xx:.1f}" y1="{ytop}" x2="{xx:.1f}" y2="{ybot}" stroke="{GRID}" stroke-width="1.4"/>'
                f'<text x="{xx:.1f}" y="{ybot + 30:.1f}" fill="{AXTX}" font-size="19" font-weight="600" '
                f'text-anchor="middle" font-family="system-ui,sans-serif" direction="ltr">{tlabels[i]}</text>')

    # ── حدّا المحورين ──
    g.append(f'<line x1="{x1}" y1="{ytop}" x2="{x1}" y2="{ybot}" stroke="{AXBD}" stroke-width="1.6"/>')
    g.append(f'<line x1="{x0}" y1="{ybot}" x2="{x1}" y2="{ybot}" stroke="{AXBD}" stroke-width="1.6"/>')

    # ── وسم الرمز الباهت وسط الشاشة، كما تفعل المنصات ──
    g.append(f'<text x="{(x0 + x1) / 2:.0f}" y="{pt + ph * 0.46:.0f}" fill="{WMK}" font-size="104" font-weight="900" '
             f'text-anchor="middle" font-family="system-ui,sans-serif" direction="ltr">{sym}</text>')
    g.append(f'<text x="{(x0 + x1) / 2:.0f}" y="{pt + ph * 0.46 + 62:.0f}" fill="{WMK}" font-size="46" font-weight="800" '
             f'text-anchor="middle" letter-spacing="6" font-family="system-ui,sans-serif" direction="ltr">@LIQUIDITY.STATE</text>')
    return ("".join(g), "".join(tg)) if split else "".join(g)


def legend(W, sym="GC=F", tf="15m", dec=2, up=None, dn=None):
    """شريط الرمز والفريم وقيم آخر شمعة — أعلى يسار الشاشة كما في المنصات."""
    pl, pr, pt, pb, pw, ph = plot_box()
    CW, CH = _K.CW, _K.CH
    c = W[-1]
    d = c["c"] - c["o"]
    col = (up or ("#2E8CA6" if T is LIGHT else "#43D4DC")) if d >= 0 else (dn or ("#D24B4B" if T is LIGHT else "#E05656"))
    o = []
    o.append(f'<text x="{pl + 4}" y="{pt - 34}" fill="{LEGT}" font-size="25" font-weight="800" '
             f'font-family="system-ui,sans-serif" direction="ltr">{sym}  ·  {tf}</text>')
    parts = [("O", c["o"]), ("H", c["h"]), ("L", c["l"]), ("C", c["c"])]
    xx = pl + 4
    for k, v in parts:
        o.append(f'<text x="{xx}" y="{pt - 6}" fill="{AXTX}" font-size="19" font-weight="700" '
                 f'font-family="system-ui,sans-serif" direction="ltr">{k}</text>')
        o.append(f'<text x="{xx + 19}" y="{pt - 6}" fill="{col}" font-size="19" font-weight="800" '
                 f'font-family="system-ui,sans-serif" direction="ltr">{v:,.{dec}f}</text>')
        xx += 35 + 11.2 * len(f"{v:,.{dec}f}")   # تباعد يفصل الحرف عن رقمه والمجموعة عن تاليتها
    return "".join(o)
