# -*- coding: utf-8 -*-
"""طراز العرض «المسطّح» — مستخرَج من مرجع فهد 2026-08-08.

🔒 أمر فهد: «يجب أن تكون التصاميم مطابقة لشروطي وبنفس طريقة العرض بهذا
الفيديو، فقط بألواني وشعاري وشروطي». والمرجع ملفٌ وسمه صاحبه
`ENGINE_TEST … synthetic … do_not_publish` — فهو **مرجع طراز لا مصدر
بيانات**: لا يُقتبس منه رقمٌ ولا شمعة، إنما المفردات البصرية وحدها.

ما استُخرج منه بالقياس على الإطارات، لا بالانطباع:

  · **بلا هيكل منصّة**: لا شريط أدوات ولا شريط علوي ولا سفلي. الجارت
    يملأ الإطار، ومعه محور سعر يميناً ومحور وقت أسفل فقط.
  · **الوسم بطاقة لا نصّ عائم**: مستطيل بحدٍّ ٢٫٥ بكسل بلون العنصر
    وخلفية فاتحة معتمة، ونصّه إنجليزي عريض ٣٤ بكسل. البطاقة تجلس **على**
    الخطّ لا فوقه، وتلتصق بأحد طرفيه.
  · **الخطوط تعبر العرض كلّه** إلى حافة محور السعر.
  · **بطاقة سعر على المحور** لكل مستوى: مستطيل مصمت بلون العنصر ورقمٌ
    أبيض داخله — وهي الموضع الوحيد الذي يُكتب فيه رقم سعر.
  · **منطقتان شفافتان** بين الدخول والوقف (حمراء) وبين الدخول والهدف
    (خضراء في المرجع ← تركوازية عندنا)، تمتدّان إلى الحافة اليمنى.
  · **علامة مائية وسط اللوحة**: الرمز بحجم كبير باهت وتحته الفريم.

والألوان تُبدَّل إلى هوية الحساب: الخلفية كريمية، والشمعة الصاعدة
تركوازية والهابطة كحلية، والأخضر يصير تركوازياً — لأن الهوية لا تعرف
الأخضر.
"""
from reel_build import CREAM, INK, TEAL, TEAL_D, RED, MUTE, GREY

# ═══ لوحة الألوان في هذا الطراز ═══
BG = CREAM                       # #F2EEE7
GRID = "rgba(15,46,60,0.055)"
AXTX = "#8B9AA1"
AXBD = "rgba(15,46,60,0.14)"
WMK = "rgba(15,46,60,0.055)"
BULL, BEAR = "#2E8CA6", "#122F3E"
TAGBG = "#FBF9F5"
ZONE_LOSS = "rgba(210,75,75,0.13)"
ZONE_WIN = "rgba(46,125,150,0.16)"


def _esc(t):
    return (str(t).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def tag(x, y, txt, col, anchor="start", fs=34, pad=16, gid=None, op=None):
    """بطاقة وسم: مستطيل بحدٍّ ملوّن ونصّ إنجليزي عريض، مركزها على الخطّ.

    `anchor="start"` يضع يسار البطاقة عند x (لوسوم الطرف الأيسر)، و`"end"`
    يضع يمينها عنده (لوسوم الطرف الأيمن). والعرض يُقدَّر من عدد الحروف —
    الخطّ أحادي الوزن هنا فالتقدير يكفي، ويُترك هامش ١٦ على الجانبين."""
    w = len(txt) * fs * 0.62 + pad * 2
    h = fs + 20
    x0 = x if anchor == "start" else x - w
    o = (f'<rect x="{x0:.1f}" y="{y-h/2:.1f}" width="{w:.1f}" height="{h:.1f}" '
         f'fill="{TAGBG}" fill-opacity=".94" stroke="{col}" stroke-width="2.5"/>'
         f'<text x="{x0+w/2:.1f}" y="{y+fs*0.36:.1f}" fill="{col}" font-size="{fs}" '
         f'font-weight="800" text-anchor="middle" letter-spacing="1.5" '
         f'font-family="system-ui,Segoe UI,sans-serif" direction="ltr">{_esc(txt)}</text>')
    if gid:
        o = f'<g id="{gid}" opacity="{0 if op is None else op}">{o}</g>'
    return o


def axis_chip(xr, y, txt, col, fs=24, gid=None):
    """بطاقة السعر على المحور — الموضع الوحيد الذي يُكتب فيه رقم سعر."""
    w = len(txt) * fs * 0.60 + 20
    o = (f'<rect x="{xr+6:.1f}" y="{y-fs*0.86:.1f}" width="{w:.1f}" '
         f'height="{fs*1.72:.1f}" fill="{col}"/>'
         f'<text x="{xr+6+w/2:.1f}" y="{y+fs*0.35:.1f}" fill="#FFFFFF" font-size="{fs}" '
         f'font-weight="800" text-anchor="middle" '
         f'font-family="system-ui,Segoe UI,sans-serif" direction="ltr">{_esc(txt)}</text>')
    return f'<g id="{gid}" opacity="0">{o}</g>' if gid else o


def zone(x0, y0, x1, y1, fill, gid=None):
    return (f'<g id="{gid}" opacity="0">' if gid else "") + \
           (f'<rect x="{x0:.1f}" y="{min(y0,y1):.1f}" width="{x1-x0:.1f}" '
            f'height="{abs(y1-y0):.1f}" fill="{fill}"/>') + \
           ("</g>" if gid else "")


def comment_chip(cx, y, txt, fs=34, gid=None):
    """شريحة التعليق السفلية: مستطيل مصمت داكن ونصّ أبيض — كما في المرجع."""
    w = len(txt) * fs * 0.60 + 56
    h = fs + 30
    o = (f'<rect x="{cx-w/2:.1f}" y="{y-h/2:.1f}" width="{w:.1f}" height="{h:.1f}" '
         f'rx="10" fill="{INK}"/>'
         f'<text x="{cx:.1f}" y="{y+fs*0.36:.1f}" fill="#FFFFFF" font-size="{fs}" '
         f'font-weight="800" text-anchor="middle" letter-spacing="1" '
         f'font-family="system-ui,Segoe UI,sans-serif" direction="ltr">{_esc(txt)}</text>')
    return f'<g id="{gid}" opacity="0">{o}</g>' if gid else o


def _step(rng, n=6):
    import math
    raw = rng / max(1, n)
    p = 10 ** math.floor(math.log10(raw)) if raw > 0 else 1
    for m in (1, 2, 2.5, 5, 10):
        if raw <= p * m:
            return p * m
    return p * 10


def furniture(W, CW, CH, pl, pr, pt, pb, ymin, ymax, slot, dec, sym, tf, gem=""):
    """أثاث اللوحة في هذا الطراز: (ثابت، منزلق).

    الثابت: الخلفية والشبكة الأفقية وأرقام المحور والعلامة المائية
    والشعار. والمنزلق: خطوط الوقت الرأسية ووسومها — تمشي مع الشموع.
    (الفصل نفسه الذي يحتاجه وضع الريبلاي في `reel_sfx_kit`.)"""
    x1 = CW - pr
    py = lambda v: pt + (ymax - v) / (ymax - ymin) * (CH - pt - pb)
    g = [f'<rect x="0" y="0" width="{CW}" height="{CH}" fill="{BG}"/>']

    st = _step(ymax - ymin, 6)
    v = (int(ymin / st) + 1) * st
    while v < ymax:
        yy = py(v)
        g.append(f'<line x1="0" y1="{yy:.1f}" x2="{x1}" y2="{yy:.1f}" '
                 f'stroke="{GRID}" stroke-width="1.5"/>'
                 f'<text x="{x1+14}" y="{yy+9:.1f}" fill="{AXTX}" font-size="26" '
                 f'font-weight="600" font-family="system-ui,sans-serif" '
                 f'direction="ltr">{v:,.{dec}f}</text>')
        v += st

    # العلامة المائية: الرمز كبيراً باهتاً وتحته الفريم — ووسطها الشعار
    cx, cy = x1 / 2, pt + (CH - pt - pb) * 0.46
    if gem:
        _g = gem.replace('width="100%" height="100%"', 'width="92" height="92"')
        g.append(f'<g transform="translate({cx-46:.0f},{cy-206:.0f})" '
                 f'opacity=".16">{_g}</g>')
    g.append(f'<text x="{cx:.0f}" y="{cy:.0f}" fill="{WMK}" font-size="104" '
             f'font-weight="900" text-anchor="middle" letter-spacing="6" '
             f'font-family="system-ui,sans-serif" direction="ltr">{_esc(sym)}</text>'
             f'<text x="{cx:.0f}" y="{cy+72:.0f}" fill="{WMK}" font-size="52" '
             f'font-weight="700" text-anchor="middle" '
             f'font-family="system-ui,sans-serif" direction="ltr">{_esc(tf)}</text>'
             f'<text x="{cx:.0f}" y="{cy+128:.0f}" fill="{WMK}" font-size="24" '
             f'font-weight="800" text-anchor="middle" letter-spacing="8" '
             f'font-family="system-ui,sans-serif" direction="ltr">LIQUIDITY STATE</text>')
    g.append(f'<line x1="{x1}" y1="0" x2="{x1}" y2="{CH-pb}" stroke="{AXBD}" stroke-width="1.6"/>'
             f'<line x1="0" y1="{CH-pb}" x2="{x1}" y2="{CH-pb}" stroke="{AXBD}" stroke-width="1.6"/>')

    tg = []
    every = max(1, len(W) // 8)
    for i in range(0, len(W), every):
        xx = pl + slot * i + slot / 2
        if xx > x1 - 30:
            break
        tg.append(f'<line x1="{xx:.1f}" y1="0" x2="{xx:.1f}" y2="{CH-pb}" '
                  f'stroke="{GRID}" stroke-width="1.5"/>'
                  f'<text x="{xx:.1f}" y="{CH-pb+40:.1f}" fill="{AXTX}" font-size="26" '
                  f'font-weight="600" text-anchor="middle" '
                  f'font-family="system-ui,sans-serif" direction="ltr">{W[i]["d"]}</text>')
    return "".join(g), "".join(tg)
