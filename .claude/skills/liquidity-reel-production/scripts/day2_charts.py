# -*- coding: utf-8 -*-
"""جارتات يوم 2026-08-04 — ثلاث وحدات: السيولة الداخلية/الخارجية · التأكيد · البريكر بلوك.
كل دالة تُرجع SVG جاهزاً؛ البذور تُسجَّل مرة واحدة من البانى الرئيسي (day2_build.py).
"""
from reel_build import INK, TEAL, TEAL_D, RED, GREY, MUTE, htext, gen, chart
import chart_registry

CHARTS = []

def fresh(seed, anch, label):
    chart_registry.assert_fresh_synthetic(seed, anch, label=label)
    CHARTS.append((seed, anch, label))

def zbox(x0, y0, x1, y1, label="", col=TEAL, stroke=TEAL_D, fs=17, lx=None, dash=None, op=0.11):
    d = f' stroke-dasharray="{dash}"' if dash else ''
    s = (f'<rect x="{x0:.1f}" y="{min(y0,y1):.1f}" width="{x1-x0:.1f}" height="{abs(y1-y0):.1f}" fill="{col}" opacity="{op}"/>'
         f'<rect x="{x0:.1f}" y="{min(y0,y1):.1f}" width="{x1-x0:.1f}" height="{abs(y1-y0):.1f}" fill="none" '
         f'stroke="{stroke}" stroke-width="1.2"{d}/>')
    if label:
        s += htext(lx if lx else (x0 + x1) / 2, (y0 + y1) / 2 + 6, label, stroke, fs)
    return s

def xm(cx, cy, r=11, col=RED):
    return (f'<g stroke="{col}" stroke-width="3" stroke-linecap="round">'
            f'<line x1="{cx-r:.1f}" y1="{cy-r:.1f}" x2="{cx+r:.1f}" y2="{cy+r:.1f}"/>'
            f'<line x1="{cx-r:.1f}" y1="{cy+r:.1f}" x2="{cx+r:.1f}" y2="{cy-r:.1f}"/></g>')

def tick(cx, cy, col=TEAL_D):
    return (f'<polyline points="{cx-10:.1f},{cy:.1f} {cx-3:.1f},{cy+8:.1f} {cx+12:.1f},{cy-10:.1f}" fill="none" '
            f'stroke="{col}" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round"/>')

def frame(W, Wd, H, extra_pad=0.08, pr=16, pl=12, H_=None):
    ymin = min(c["l"] for c in W); ymax = max(c["h"] for c in W)
    rng = ymax - ymin
    return chart(W, Wd, H, ymin - rng * extra_pad, ymax + rng * extra_pad,
                 grid=4, pl=pl, pr=pr, pt=20, pb=14, body=0.6)

# ═══════════════ 1) السيولة الداخلية والخارجية ═══════════════
def _internal_data(seed, anch, N, ieq, iext, isweep, label):
    """قمم داخلية متساوية داخل النطاق + قمة خارجية أعلى؛ السعر يأخذ الداخلية ثم يتجه للخارجية."""
    fresh(seed, anch, label)
    W = gen(anch, N, seed, wick=0.8)
    rng = max(c["h"] for c in W) - min(c["l"] for c in W)
    EXT = max(W[i]["h"] for i in (iext,)) + rng * 0.02
    W[iext]["h"] = EXT
    INT = max(W[i]["h"] for i in ieq)
    for i in ieq:                        # تساوي القمم الداخلية
        W[i]["h"] = INT
        W[i]["c"] = min(W[i]["c"], INT - rng * 0.03)
    for j in range(iext + 1, isweep):    # لا شيء يتجاوز الداخلية قبل السحب
        if j not in ieq:
            cap = INT - rng * 0.02
            W[j]["h"] = min(W[j]["h"], cap)
            W[j]["o"] = min(W[j]["o"], cap); W[j]["c"] = min(W[j]["c"], cap)
    o = W[isweep - 1]["c"]               # شمعة تأخذ السيولة الداخلية
    W[isweep].update(o=o, h=INT + rng * 0.04, c=INT + rng * 0.015, l=o - rng * 0.02)
    prev = W[isweep]["c"]                # ثم اندفاع نحو الخارجية
    for i, j in enumerate(range(isweep + 1, N)):
        step = rng * (0.10 if i < 4 else 0.03)
        W[j].update(o=prev, c=min(prev + step, EXT + rng * 0.05),
                    h=min(prev + step, EXT + rng * 0.05) + rng * 0.02, l=prev - rng * 0.015)
        prev = W[j]["c"]
    return W, INT, EXT, rng

def internal_chart(Wd=880, H=300, seed=5101, hero=False):
    N = 34
    anch = [(0, 11.0), (3, 13.8), (6, 12.4), (9, 13.6), (12, 12.2), (15, 13.6),
            (18, 12.6), (21, 13.9), (24, 14.6), (28, 15.4), (33, 16.2)]
    W, INT, EXT, rng = _internal_data(seed, anch, N, (9, 15), 3, 22, f"سيولة داخلية {seed}")
    svg, x, y, slot = frame(W, Wd, H)
    svg += (f'<line x1="{x(8)-slot*0.6:.1f}" y1="{y(INT):.1f}" x2="{x(23)+slot*0.6:.1f}" y2="{y(INT):.1f}" '
            f'stroke="{RED}" stroke-width="1.8" stroke-dasharray="6 5"/>')
    svg += htext(x(12), y(INT) - 12, "سيولة داخلية", RED, 17)
    svg += (f'<line x1="{x(2)-slot*0.6:.1f}" y1="{y(EXT):.1f}" x2="{x(N-1)+slot*0.5:.1f}" y2="{y(EXT):.1f}" '
            f'stroke="{INK}" stroke-width="1.9"/>')
    svg += htext(x(7), y(EXT) - 12, "سيولة خارجية — الهدف", INK, 17)
    svg += xm(x(22), y(INT) - 22)
    if not hero:
        svg += htext(x(24), y(INT) + 96, "بعد الداخلية… الاتجاه للخارجية", TEAL_D, 17)
    return svg + "</svg>"

def internal_wrong(Wd=620, H=300, seed=5102):
    """الخطأ: استهداف السيولة الداخلية كهدف نهائي والخروج المبكر."""
    N = 26
    anch = [(0, 11.2), (4, 13.4), (7, 12.3), (10, 13.5), (13, 12.4), (16, 13.6), (20, 15.0), (25, 16.0)]
    W, INT, EXT, rng = _internal_data(seed, anch, N, (10, 16), 4, 18, f"خطأ داخلية {seed}")
    svg, x, y, slot = frame(W, Wd, H)
    svg += (f'<line x1="{x(9)-slot*0.6:.1f}" y1="{y(INT):.1f}" x2="{x(N-1):.1f}" y2="{y(INT):.1f}" '
            f'stroke="{RED}" stroke-width="1.7" stroke-dasharray="6 5"/>')
    svg += htext(x(13), y(INT) - 11, "خرج هنا ✗", RED, 16)
    svg += (f'<line x1="{x(3)-slot*0.6:.1f}" y1="{y(EXT):.1f}" x2="{x(N-1):.1f}" y2="{y(EXT):.1f}" '
            f'stroke="{INK}" stroke-width="1.8"/>')
    svg += htext(x(8), y(EXT) - 11, "الهدف الحقيقي", INK, 16)
    svg += xm(x(18), y(INT) - 20)
    return svg + "</svg>"

def internal_right(Wd=620, H=300, seed=5103):
    N = 26
    anch = [(0, 11.4), (4, 13.6), (7, 12.5), (10, 13.7), (13, 12.6), (16, 13.8), (20, 15.2), (25, 16.4)]
    W, INT, EXT, rng = _internal_data(seed, anch, N, (10, 16), 4, 18, f"صحيح داخلية {seed}")
    svg, x, y, slot = frame(W, Wd, H)
    svg += (f'<line x1="{x(9)-slot*0.6:.1f}" y1="{y(INT):.1f}" x2="{x(N-1):.1f}" y2="{y(INT):.1f}" '
            f'stroke="{RED}" stroke-width="1.6" stroke-dasharray="5 5" opacity="0.7"/>')
    svg += (f'<line x1="{x(3)-slot*0.6:.1f}" y1="{y(EXT):.1f}" x2="{x(N-1):.1f}" y2="{y(EXT):.1f}" '
            f'stroke="{TEAL_D}" stroke-width="1.9"/>')
    svg += htext(x(9), y(EXT) - 11, "الهدف: السيولة الخارجية ✓", TEAL_D, 16)
    svg += tick(x(23), y(W[23]["c"]) - 24)
    return svg + "</svg>"

# ═══════════════ 2) التأكيد ═══════════════
def _confirm_data(seed, anch, N, iz0, iz1, itouch, ok, label):
    """منطقة طلب، لمسة، ثم إما تأكيد وصعود أو اختراق وخسارة."""
    fresh(seed, anch, label)
    W = gen(anch, N, seed, wick=0.8)
    rng = max(c["h"] for c in W) - min(c["l"] for c in W)
    ZT = max(max(c["o"], c["c"]) for c in W[iz0:iz1 + 1])
    ZB = min(c["l"] for c in W[iz0:iz1 + 1])
    for j in range(iz1 + 1, itouch):          # لا يعود قبل موعده
        W[j]["l"] = max(W[j]["l"], ZT + rng * 0.02)
        W[j]["o"] = max(W[j]["o"], W[j]["l"]); W[j]["c"] = max(W[j]["c"], W[j]["l"])
        W[j]["h"] = max(W[j]["h"], max(W[j]["o"], W[j]["c"]))
    W[itouch]["l"] = ZB + (ZT - ZB) * 0.25    # اللمسة داخل المنطقة
    W[itouch]["o"] = max(W[itouch]["o"], ZT)
    W[itouch]["c"] = ZT + rng * (0.015 if ok else -0.02)
    W[itouch]["h"] = max(W[itouch]["o"], W[itouch]["c"]) + rng * 0.015
    prev = W[itouch]["c"]
    for i, j in enumerate(range(itouch + 1, N)):
        step = rng * (0.09 if ok else -0.08)
        W[j].update(o=prev, c=prev + step, h=prev + max(step, 0) + rng * 0.02,
                    l=prev + min(step, 0) - rng * 0.02)
        prev = W[j]["c"]
    return W, ZT, ZB, rng

def confirm_chart(Wd=880, H=300, seed=5201, hero=False):
    N = 30
    anch = [(0, 15.6), (4, 14.2), (7, 13.2), (10, 13.6), (14, 15.4), (18, 14.4),
            (21, 13.5), (24, 15.2), (29, 16.6)]
    W, ZT, ZB, rng = _confirm_data(seed, anch, N, 7, 9, 21, True, f"تأكيد {seed}")
    svg, x, y, slot = frame(W, Wd, H)
    svg += zbox(x(7) - slot * 0.5, y(ZT), x(N - 1) + slot * 0.5, y(ZB), "المنطقة", lx=x(12))
    svg += (f'<circle cx="{x(21):.1f}" cy="{y(W[21]["c"]):.1f}" r="14" fill="none" stroke="{TEAL_D}" stroke-width="2.6"/>')
    svg += htext(x(20), y(ZB) + 34, "إغلاق جسم داخل المنطقة ✓", TEAL_D, 16)
    if not hero:
        svg += tick(x(27), y(W[27]["c"]) - 26)
    return svg + "</svg>"

def confirm_wrong(Wd=620, H=300, seed=5202):
    N = 26
    anch = [(0, 15.8), (4, 14.4), (7, 13.4), (10, 13.8), (14, 15.2), (18, 14.0), (21, 13.4), (25, 11.8)]
    W, ZT, ZB, rng = _confirm_data(seed, anch, N, 7, 9, 20, False, f"بلا تأكيد {seed}")
    svg, x, y, slot = frame(W, Wd, H)
    svg += zbox(x(7) - slot * 0.5, y(ZT), x(N - 1) + slot * 0.5, y(ZB), "المنطقة", lx=x(11), fs=16)
    svg += xm(x(20), y(ZT) - 6)
    svg += htext(x(15), y(ZT) - 34, "دخول عند اللمسة ✗", RED, 16)
    return svg + "</svg>"

def confirm_choch(Wd=620, H=300, seed=5203):
    """تغير الطابع داخل المنطقة: قاع أعلى بعد اللمسة."""
    N = 26
    anch = [(0, 15.4), (4, 14.0), (7, 13.0), (10, 13.4), (14, 15.0), (18, 13.9), (20, 13.6), (25, 16.2)]
    W, ZT, ZB, rng = _confirm_data(seed, anch, N, 7, 9, 19, True, f"تغير طابع {seed}")
    svg, x, y, slot = frame(W, Wd, H)
    svg += zbox(x(7) - slot * 0.5, y(ZT), x(N - 1) + slot * 0.5, y(ZB), "", fs=16)
    svg += (f'<line x1="{x(19)-slot*0.8:.1f}" y1="{y(W[20]["h"]):.1f}" x2="{x(23)+slot*0.5:.1f}" y2="{y(W[20]["h"]):.1f}" '
            f'stroke="{INK}" stroke-width="1.7"/>')
    svg += htext(x(21), y(W[20]["h"]) - 11, "تغير الطابع (CHoCH) ✓", INK, 16)
    svg += tick(x(24), y(W[24]["c"]) - 24)
    return svg + "</svg>"

# ═══════════════ 3) البريكر بلوك ═══════════════
def _breaker_data(seed, anch, N, iob, ibrk, iret, label):
    """أوردر بلوك صاعد يفشل ويُخترق، ثم يُختبر من الأسفل فينقلب مقاومة."""
    fresh(seed, anch, label)
    W = gen(anch, N, seed, wick=0.8)
    rng = max(c["h"] for c in W) - min(c["l"] for c in W)
    o = W[iob - 1]["c"]                       # شمعة البلوك (بائعة قبل صعود فاشل)
    body = rng * 0.10
    W[iob].update(o=o, c=o - body, h=o + body * 0.25, l=o - body * 1.3)
    ZT, ZB = W[iob]["o"], W[iob]["c"]
    prev = W[iob]["c"]                        # صعود قصير ثم فشل
    for i, j in enumerate(range(iob + 1, ibrk)):
        step = rng * 0.05
        W[j].update(o=prev, c=prev + step, h=prev + step + rng * 0.02, l=prev - rng * 0.015)
        prev = W[j]["c"]
    for i, j in enumerate(range(ibrk, iret - 2)):   # اختراق هابط عبر البلوك
        step = rng * 0.09
        W[j].update(o=prev, c=prev - step, h=prev + rng * 0.015, l=prev - step - rng * 0.025)
        prev = W[j]["c"]
    for i, j in enumerate(range(iret - 2, iret + 1)):   # عودة لاختبار البلوك من الأسفل
        tgt = ZB + (ZT - ZB) * (0.35 + 0.25 * i)
        W[j].update(o=prev, c=tgt, h=tgt + rng * 0.02, l=prev - rng * 0.015)
        prev = tgt
    for i, j in enumerate(range(iret + 1, N)):        # الرفض والهبوط
        step = rng * (0.11 if i < 3 else 0.05)
        W[j].update(o=prev, c=prev - step, h=prev + rng * 0.012, l=prev - step - rng * 0.02)
        prev = W[j]["c"]
    return W, ZT, ZB, rng

def breaker_chart(Wd=880, H=300, seed=5301, hero=False):
    N = 32
    anch = [(0, 16.6), (4, 15.6), (8, 15.0), (12, 15.6), (16, 14.0), (22, 15.2), (26, 13.0), (31, 11.6)]
    W, ZT, ZB, rng = _breaker_data(seed, anch, N, 9, 13, 21, f"بريكر {seed}")
    svg, x, y, slot = frame(W, Wd, H)
    svg += zbox(x(9) - slot * 0.5, y(ZT), x(N - 1) + slot * 0.5, y(ZB), "بريكر بلوك", stroke=RED, col=RED, lx=x(27), fs=17)
    svg += htext(x(9) + slot * 2.4, y(ZT) - 16, "بلوك فشل ✗", RED, 17)
    svg += (f'<line x1="{x(12)-slot*0.6:.1f}" y1="{y(W[9]["l"]):.1f}" x2="{x(17)+slot*0.6:.1f}" y2="{y(W[9]["l"]):.1f}" '
            f'stroke="{INK}" stroke-width="1.7"/>')
    svg += htext(x(14), y(W[9]["l"]) + 44, "كسر الهيكل (BOS)", INK, 16)
    if not hero:
        svg += (f'<circle cx="{x(21):.1f}" cy="{y(W[21]["c"]):.1f}" r="13" fill="none" stroke="{TEAL_D}" stroke-width="2.6"/>')
        svg += htext(x(21) + slot * 3.4, y(W[21]["c"]) - 30, "بيع من البريكر", TEAL_D, 17)
        svg += tick(x(29), y(W[29]["c"]) + 26)
    return svg + "</svg>"

def breaker_ob(Wd=620, H=300, seed=5302):
    """أوردر بلوك عادي ناجح — للمقارنة."""
    N = 24
    anch = [(0, 13.0), (4, 12.0), (7, 11.4), (9, 11.8), (13, 14.0), (17, 13.0), (19, 13.4), (23, 15.4)]
    fresh(seed, anch, f"مقارنة بلوك {seed}")
    W = gen(anch, N, seed, wick=0.8)
    rng = max(c["h"] for c in W) - min(c["l"] for c in W)
    o = W[8]["c"]; body = rng * 0.11
    W[9].update(o=o, c=o - body, h=o + body * 0.2, l=o - body * 1.2)
    ZT, ZB = W[9]["o"], W[9]["c"]
    prev = W[9]["c"]
    for i, j in enumerate(range(10, 14)):
        step = rng * 0.11
        W[j].update(o=prev, c=prev + step, h=prev + step + rng * 0.02, l=prev - rng * 0.015); prev = W[j]["c"]
    for j in range(14, 18):
        W[j]["l"] = max(W[j]["l"], ZT + rng * 0.01)
        W[j]["o"] = max(W[j]["o"], W[j]["l"]); W[j]["c"] = max(W[j]["c"], W[j]["l"])
        W[j]["h"] = max(W[j]["h"], max(W[j]["o"], W[j]["c"]))
    W[18]["l"] = ZB + (ZT - ZB) * 0.4
    svg, x, y, slot = frame(W, Wd, H)
    svg += zbox(x(9) - slot * 0.5, y(ZT), x(N - 1) + slot * 0.5, y(ZB), "أوردر بلوك ✓", lx=x(20), fs=16)
    svg += tick(x(22), y(W[22]["c"]) - 24)
    return svg + "</svg>"

def breaker_wrong(Wd=620, H=300, seed=5303):
    """الخطأ: اعتبار كل بلوك مكسور بريكراً بلا كسر هيكل."""
    N = 24
    anch = [(0, 14.0), (4, 14.6), (8, 13.8), (12, 14.4), (16, 13.6), (20, 14.2), (23, 13.8)]
    fresh(seed, anch, f"خطأ بريكر {seed}")
    W = gen(anch, N, seed, wick=0.75)
    rng = max(c["h"] for c in W) - min(c["l"] for c in W)
    ZT = W[10]["h"]; ZB = W[10]["l"]
    svg, x, y, slot = frame(W, Wd, H)
    svg += zbox(x(10) - slot * 0.6, y(ZT), x(N - 1) + slot * 0.5, y(ZB), "«بريكر» بلا كسر هيكل ✗",
                stroke=RED, col=RED, lx=x(18), fs=15, dash="6 5")
    svg += xm(x(19), y((ZT + ZB) / 2))
    svg += htext(x(6), y(max(c["h"] for c in W)) + 4, "تذبذب فقط", MUTE, 16)
    return svg + "</svg>"
