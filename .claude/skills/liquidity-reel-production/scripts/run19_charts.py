# -*- coding: utf-8 -*-
"""جارتات وحدة «الترند لاين» — خمس حالات على خط اتجاه واحد.
نفس انضباط تخطيط run15: شريط علوي (شارة الحكم + عنوان) وشريط سفلي (ملاحظتان)
خارج مساحة الشموع، فلا يقع أي وسم على شمعة.
"""
from reel_build import INK, TEAL, TEAL_D, RED, GREY, MUTE, htext, gen, chart
import chart_registry

CHARTS = []

def fresh(seed, anch, label):
    chart_registry.assert_fresh_synthetic(seed, anch, label=label)
    CHARTS.append((seed, anch, label))

def badge(Wd, txt, ok):
    col = TEAL_D if ok else RED
    bw = min(Wd - 40, 36 + int(len(txt) * 11.5))
    return (f'<rect x="14" y="14" width="{bw}" height="38" '
            f'fill="{"#EAF3F5" if ok else "#F8ECEC"}" stroke="{col}" stroke-width="1.4"/>'
            + htext(14 + bw / 2, 40, txt, col, 19))

def head(Wd, txt, col=INK, fs=19):
    return htext(Wd - 20, 37, txt, col, fs, anchor="start")

def note(cx, txt, col=INK, H=250, fs=18):
    return htext(cx, H - 16, txt, col, fs)

def frame(W, Wd, H, pad=0.06, pl=14, pr=18, pt=58, pb=50):
    ymin = min(c["l"] for c in W); ymax = max(c["h"] for c in W); rng = ymax - ymin
    return chart(W, Wd, H, ymin - rng * pad, ymax + rng * pad,
                 grid=4, pl=pl, pr=pr, pt=pt, pb=pb, body=0.6)

def xm(cx, cy, r=11, col=RED):
    return (f'<g stroke="{col}" stroke-width="3" stroke-linecap="round">'
            f'<line x1="{cx-r:.1f}" y1="{cy-r:.1f}" x2="{cx+r:.1f}" y2="{cy+r:.1f}"/>'
            f'<line x1="{cx-r:.1f}" y1="{cy+r:.1f}" x2="{cx+r:.1f}" y2="{cy-r:.1f}"/></g>')

def tick(cx, cy, col=TEAL_D):
    return (f'<polyline points="{cx-10:.1f},{cy:.1f} {cx-3:.1f},{cy+8:.1f} {cx+12:.1f},{cy-10:.1f}" '
            f'fill="none" stroke="{col}" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round"/>')

def ring(cx, cy, r=13, col=TEAL_D):
    return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r}" fill="none" stroke="{col}" stroke-width="2.8"/>'

# ── خط الاتجاه: يمرّ بمرتكزين ويُرسم ممتداً إلى آخر الشارت ──
def _lineP(i0, p0, i1, p1):
    return lambda i: p0 + (p1 - p0) * (i - i0) / (i1 - i0)

def tline(x, y, f, i0, i1, N, slot, col=INK, w=2.4, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ''
    return (f'<line x1="{x(i0)-slot*0.5:.1f}" y1="{y(f(i0)):.1f}" '
            f'x2="{x(N-1)+slot*0.5:.1f}" y2="{y(f(N-1)):.1f}" '
            f'stroke="{col}" stroke-width="{w}" stroke-linecap="round"{d}/>')

def _base(seed, anch, N, label, wick=0.85):
    fresh(seed, anch, label)
    W = gen(anch, N, seed, wick=wick)
    return W, max(c["h"] for c in W) - min(c["l"] for c in W)

def _sit_low(W, j, p, rng, wickdrop=0.0):
    """يُجلس قاع الشمعة j على المستوى p (مع فتيل اختياري تحته)."""
    W[j]["l"] = p - rng * wickdrop
    W[j]["o"] = max(W[j]["o"], p); W[j]["c"] = max(W[j]["c"], p)
    W[j]["h"] = max(W[j]["h"], max(W[j]["o"], W[j]["c"]) + rng * 0.012)

def _keep_above(W, j, p, rng, m=0.015):
    if W[j]["l"] < p + rng * m:
        d = p + rng * m - W[j]["l"]
        for k in ("o", "c", "h", "l"): W[j][k] += d

# ══════ 1) خط من الفتائل: كل فتيل يخترقه فتخرج مبكراً ══════
def tl_wicks(Wd=880, H=250, seed=8201):
    N = 30
    anch = [(0, 11.0), (5, 12.6), (9, 12.0), (14, 14.2), (18, 13.4), (23, 15.8), (29, 17.2)]
    W, rng = _base(seed, anch, N, f"ترند فتائل {seed}")
    P = [(2, 10.6), (10, 12.0), (19, 13.5)]
    f = _lineP(P[0][0], P[0][1], P[2][0], P[2][1])
    for j in range(N):
        if j >= P[0][0]:
            _keep_above(W, j, f(j), rng, 0.02)
    for j, _ in P:
        _sit_low(W, j, f(j), rng)
    for j in (7, 16, 25):                      # فتائل تعبر الخط ثم تُغلق فوقه
        W[j]["l"] = f(j) - rng * 0.045
    svg, x, y, slot = frame(W, Wd, H)
    svg += tline(x, y, f, P[0][0], P[2][0], N, slot, INK, 2.4)
    for j in (7, 16, 25):
        svg += xm(x(j), y(f(j)) + 16, r=9)
    svg += head(Wd, "خط مرسوم على أدنى الفتائل")
    svg += note(x(8), "ثلاث اختراقات وهمية", RED, H, 17)
    svg += note(x(24), "خرجت ثلاث مرات… والاتجاه قائم", RED, H, 17)
    return svg + badge(Wd, "إشارات كاذبة", False) + "</svg>"

# ══════ 2) خط من الإغلاقات: يصمد ويعطي إشارة واحدة ══════
def tl_bodies(Wd=880, H=250, seed=8202):
    N = 30
    anch = [(0, 11.2), (5, 12.8), (10, 12.2), (15, 14.4), (20, 13.8), (25, 16.0), (29, 15.4)]
    W, rng = _base(seed, anch, N, f"ترند أجسام {seed}")
    P = [(3, 11.4), (11, 12.5), (21, 13.9)]
    f = _lineP(P[0][0], P[0][1], P[2][0], P[2][1])
    for j in range(P[0][0], N):
        _keep_above(W, j, f(j), rng, 0.01)
    for j, _ in P:                              # الإغلاق على الخط والفتيل تحته
        W[j]["c"] = f(j) + rng * 0.005
        W[j]["o"] = max(W[j]["o"], W[j]["c"])
        W[j]["l"] = f(j) - rng * 0.05
        W[j]["h"] = max(W[j]["h"], W[j]["o"] + rng * 0.012)
    for j in range(26, N):                      # الكسر الحقيقي: إغلاق تحت الخط
        W[j]["c"] = min(W[j]["c"], f(j) - rng * 0.05)
        W[j]["o"] = min(W[j]["o"], f(j) + rng * 0.01)
        W[j]["l"] = min(W[j]["l"], W[j]["c"] - rng * 0.02)
        W[j]["h"] = max(W[j]["o"], W[j]["c"]) + rng * 0.012
    svg, x, y, slot = frame(W, Wd, H)
    svg += tline(x, y, f, P[0][0], P[2][0], N, slot, INK, 2.4)
    for j, _ in P:
        svg += ring(x(j), y(f(j)) + 4, r=11)
    svg += xm(x(27), y(f(27)) + 14, r=10)
    svg += head(Wd, "الخط نفسه مرسوماً على الإغلاقات")
    svg += note(x(9), "الفتائل تعبر… والإغلاق يحترم", TEAL_D, H, 17)
    svg += note(x(25), "إشارة واحدة: إغلاق تحت الخط", RED, H, 17)
    return svg + badge(Wd, "إشارة واحدة نظيفة", True) + "</svg>"

# ══════ 3) لمستان لا تصنعان خطاً — الثالثة تُثبته ══════
def tl_third(Wd=880, H=250, seed=8203):
    N = 32
    anch = [(0, 11.4), (6, 13.2), (11, 12.4), (17, 14.8), (22, 14.0), (27, 16.4), (31, 17.4)]
    W, rng = _base(seed, anch, N, f"ترند لمسة ثالثة {seed}")
    P = [(2, 11.0), (12, 12.4), (23, 13.9)]
    f = _lineP(P[0][0], P[0][1], P[2][0], P[2][1])
    for j in range(P[0][0], N):
        _keep_above(W, j, f(j), rng, 0.018)
    for j, _ in P:
        _sit_low(W, j, f(j), rng, 0.012)
    svg, x, y, slot = frame(W, Wd, H)
    svg += tline(x, y, f, P[0][0], P[1][0], N, slot, MUTE, 2.0, dash="7 6")
    svg += tline(x, y, f, P[2][0], N - 1, N, slot, TEAL_D, 2.6)
    for k, (j, _) in enumerate(P):
        svg += (ring(x(j), y(f(j)) + 4, r=11, col=(GREY if k < 2 else TEAL_D)))
    svg += tick(x(26), y(W[26]["h"]) - 20)
    svg += head(Wd, "المتقطع: فرضية · المتصل: خط مؤكَّد")
    svg += note(x(8), "لمستان = فرضية فقط", GREY, H, 17)
    svg += note(x(25), "الثالثة تُثبت الخط وتفتح الصفقة", TEAL_D, H, 17)
    return svg + badge(Wd, "ادخل بعد الثالثة", True) + "</svg>"

# ══════ 4) ميل حاد: خط شديد الانحدار يُكسر بلا انعكاس ══════
def tl_steep(Wd=880, H=250, seed=8204):
    N = 30
    anch = [(0, 10.8), (4, 12.8), (8, 14.6), (12, 16.4), (16, 17.6), (21, 16.2), (25, 16.8), (29, 18.4)]
    W, rng = _base(seed, anch, N, f"ترند ميل حاد {seed}")
    P = [(1, 10.9), (9, 14.4)]                  # ميل حاد جداً
    f = _lineP(P[0][0], P[0][1], P[1][0], P[1][1])
    for j in range(P[0][0], 18):
        _keep_above(W, j, f(j), rng, 0.01)
    for j, _ in P:
        _sit_low(W, j, f(j), rng)
    # خط ثانٍ أهدأ يبقى صامداً بعد كسر الحاد
    Q = [(1, 10.7), (21, 15.4)]
    g = _lineP(Q[0][0], Q[0][1], Q[1][0], Q[1][1])
    for j in range(18, N):
        _keep_above(W, j, g(j), rng, 0.015)
    svg, x, y, slot = frame(W, Wd, H)
    svg += tline(x, y, f, P[0][0], P[1][0], 20, slot, RED, 2.4)
    svg += tline(x, y, g, Q[0][0], Q[1][0], N, slot, TEAL_D, 2.4, dash="7 6")
    svg += xm(x(19), y(f(19)) + 10, r=10)
    svg += head(Wd, "الأحمر: ميل حاد · المتقطع: ميل واقعي")
    svg += note(x(9), "كُسر الحاد سريعاً", RED, H, 17)
    svg += note(x(25), "والاتجاه لم ينعكس", TEAL_D, H, 17)
    return svg + badge(Wd, "كسر بلا انعكاس", False) + "</svg>"

# ══════ 5) إعادة الرسم بعد الكسر ══════
def tl_redraw(Wd=880, H=250, seed=8205):
    N = 30
    anch = [(0, 11.6), (5, 13.2), (10, 12.6), (15, 14.6), (19, 13.2), (24, 12.0), (29, 10.4)]
    W, rng = _base(seed, anch, N, f"ترند إعادة رسم {seed}")
    P = [(2, 11.2), (11, 12.6)]
    f = _lineP(P[0][0], P[0][1], P[1][0], P[1][1])
    for j in range(P[0][0], 18):
        _keep_above(W, j, f(j), rng, 0.012)
    for j, _ in P:
        _sit_low(W, j, f(j), rng)
    for j in range(18, N):                      # كسر حقيقي واستمرار هبوطي
        W[j]["h"] = min(W[j]["h"], f(j) - rng * 0.02)
        W[j]["o"] = min(W[j]["o"], W[j]["h"]); W[j]["c"] = min(W[j]["c"], W[j]["h"])
        W[j]["l"] = min(W[j]["l"], W[j]["c"] - rng * 0.015)
    R = [(2, 11.2), (20, 11.6)]                 # الخط الموسَّع بعد الكسر
    r = _lineP(R[0][0], R[0][1], R[1][0], R[1][1])
    svg, x, y, slot = frame(W, Wd, H)
    svg += tline(x, y, f, P[0][0], P[1][0], N, slot, INK, 2.2)
    svg += tline(x, y, r, R[0][0], R[1][0], N, slot, RED, 2.2, dash="6 5")
    svg += xm(x(19), y(f(19)) + 12, r=10)
    svg += head(Wd, "المتصل: الخط الأصلي · المتقطع: بعد التوسيع")
    svg += note(x(8), "كُسر بإغلاق واضح", INK, H, 17)
    svg += note(x(24), "التوسيع أخّر الاعتراف فقط", RED, H, 17)
    return svg + badge(Wd, "الخط لا يُعاد رسمه", False) + "</svg>"

CAR_CHARTS = [tl_wicks, tl_bodies, tl_third, tl_steep, tl_redraw]
HERO = tl_bodies
