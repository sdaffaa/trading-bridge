# -*- coding: utf-8 -*-
"""جارتات وحدة «فريم القرار وفريم التنفيذ» — خمس حالات.
فيها محرّك تكبير فريم: يولّد شموع الفريم الأصغر بحيث يكون مجموعها مطابقاً تماماً
للشمعة الأم (فتح = فتحها، إغلاق = إغلاقها، أقصى ارتفاع وانخفاض = ارتفاعها وانخفاضها)،
فالتكبير عرضٌ للشمعة نفسها لا اختراع حركة جديدة.
"""
import random
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

def zbox(x0, y0, x1, y1, col=TEAL, stroke=TEAL_D, op=0.11, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ''
    return (f'<rect x="{x0:.1f}" y="{min(y0,y1):.1f}" width="{x1-x0:.1f}" height="{abs(y1-y0):.1f}" '
            f'fill="{col}" opacity="{op}"/>'
            f'<rect x="{x0:.1f}" y="{min(y0,y1):.1f}" width="{x1-x0:.1f}" height="{abs(y1-y0):.1f}" '
            f'fill="none" stroke="{stroke}" stroke-width="1.3"{d}/>')

def hl(x0, x1, yy, col=INK, w=1.9, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<line x1="{x0:.1f}" y1="{yy:.1f}" x2="{x1:.1f}" y2="{yy:.1f}" stroke="{col}" stroke-width="{w}"{d}/>'

def xm(cx, cy, r=11, col=RED):
    return (f'<g stroke="{col}" stroke-width="3" stroke-linecap="round">'
            f'<line x1="{cx-r:.1f}" y1="{cy-r:.1f}" x2="{cx+r:.1f}" y2="{cy+r:.1f}"/>'
            f'<line x1="{cx-r:.1f}" y1="{cy+r:.1f}" x2="{cx+r:.1f}" y2="{cy-r:.1f}"/></g>')

def tick(cx, cy, col=TEAL_D):
    return (f'<polyline points="{cx-10:.1f},{cy:.1f} {cx-3:.1f},{cy+8:.1f} {cx+12:.1f},{cy-10:.1f}" '
            f'fill="none" stroke="{col}" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round"/>')

# ── محرّك تكبير الفريم ──────────────────────────────────────────────
def ltf_expand(par, k, seed, hi_i=None, lo_i=None):
    """k شمعة فرعية مجموعها = الشمعة الأم par تماماً."""
    r = random.Random(seed)
    o, h, l, c = par["o"], par["h"], par["l"], par["c"]
    hi_i = k - 2 if hi_i is None else hi_i
    lo_i = 1 if lo_i is None else lo_i
    # مسار إغلاقات من o إلى c بتذبذب داخل [l,h]
    closes = []
    for i in range(k):
        t = (i + 1) / k
        base = o + (c - o) * t
        jit = (r.random() - 0.5) * (h - l) * 0.34 * (1 - abs(2 * t - 1) * 0.5)
        closes.append(min(max(base + jit, l + (h - l) * 0.04), h - (h - l) * 0.04))
    closes[-1] = c
    W, prev = [], o
    for i in range(k):
        cc = closes[i]
        hi = max(prev, cc) + (h - l) * r.uniform(0.02, 0.07)
        lo = min(prev, cc) - (h - l) * r.uniform(0.02, 0.07)
        W.append(dict(o=prev, c=cc, h=min(hi, h), l=max(lo, l)))
        prev = cc
    W[hi_i]["h"] = h                      # القمة الأم على شمعة واحدة
    W[lo_i]["l"] = l                      # القاع الأم على شمعة واحدة
    for i, cd in enumerate(W):            # لا شيء يتجاوز حدود الأم
        cd["h"] = min(cd["h"], h); cd["l"] = max(cd["l"], l)
        cd["h"] = max(cd["h"], cd["o"], cd["c"]); cd["l"] = min(cd["l"], cd["o"], cd["c"])
    return W

# ══════ 1) القرار: منطقة على الفريم الأعلى ══════
def htf_zone(Wd=880, H=250, seed=8301):
    N = 30
    anch = [(0, 11.4), (5, 14.6), (9, 13.2), (13, 16.2), (18, 14.0), (23, 17.4), (29, 19.0)]
    fresh(seed, anch, f"فريم قرار {seed}")
    W = gen(anch, N, seed, wick=0.8)
    rng = max(c["h"] for c in W) - min(c["l"] for c in W)
    seg = W[7:10]
    ZT = max(max(c["o"], c["c"]) for c in seg); ZB = ZT - rng * 0.165
    for j in range(10, 17):
        if W[j]["l"] < ZT + rng * 0.02:
            d = ZT + rng * 0.02 - W[j]["l"]
            for kk in ("o", "c", "h", "l"): W[j][kk] += d
    for j in (17, 18):                     # العودة تدخل المنطقة إلى منتصفها ثم ترتد
        mid = (ZT + ZB) / 2
        W[j]["l"] = mid - rng * 0.01
        W[j]["o"] = ZT - rng * 0.005; W[j]["c"] = ZT + rng * 0.02
        W[j]["h"] = W[j]["c"] + rng * 0.02
    svg, x, y, slot = frame(W, Wd, H)
    svg += zbox(x(7) - slot * .6, y(ZT), x(N - 1) + slot * .5, y(ZB))
    svg += hl(x(4) - slot * .5, x(N - 1) + slot * .5, y(W[5]["h"]), MUTE, 1.5, dash="6 5")
    svg += head(Wd, "الفريم الأعلى: هيكل صاعد ومنطقة واحدة")
    svg += note(x(9), "هنا يُتخذ القرار", TEAL_D, H, 17)
    svg += note(x(24), "لا دخول من هذا الفريم", GREY, H, 17)
    return svg + badge(Wd, "قرار لا تنفيذ", True) + "</svg>"

# ══════ 2) التنفيذ: تكبير الشمعة اللامسة ══════
def ltf_entry(Wd=880, H=250, seed=8302):
    N = 30
    anch = [(0, 11.5), (5, 14.7), (9, 13.3), (13, 16.3), (18, 14.1), (23, 17.5), (29, 19.1)]
    fresh(seed, anch, f"فريم تنفيذ {seed}")
    P = gen(anch, N, seed, wick=0.8)
    rng = max(c["h"] for c in P) - min(c["l"] for c in P)
    par = dict(o=P[17]["o"], c=P[17]["o"] + rng * 0.10,
               h=P[17]["o"] + rng * 0.13, l=P[17]["o"] - rng * 0.06)
    W = ltf_expand(par, 22, seed + 7, hi_i=19, lo_i=5)
    ZT = par["o"] + (par["h"] - par["l"]) * 0.20
    ZB = par["l"] + (par["h"] - par["l"]) * 0.02
    LH = max(c["h"] for c in W[6:11])              # آخر قمة هابطة داخل التكبير
    for j in range(11, 14):
        W[j]["h"] = min(W[j]["h"], LH - (par["h"] - par["l"]) * 0.02)
        W[j]["o"] = min(W[j]["o"], W[j]["h"]); W[j]["c"] = min(W[j]["c"], W[j]["h"])
    for j in range(14, 17):
        W[j]["l"] = max(W[j]["l"], LH)
        W[j]["o"] = max(W[j]["o"], LH); W[j]["c"] = max(W[j]["c"], LH)
        W[j]["h"] = max(W[j]["h"], W[j]["c"])
    svg, x, y, slot = frame(W, Wd, H)
    svg += zbox(x(0) - slot * .4, y(ZT), x(len(W) - 1) + slot * .5, y(ZB))
    svg += hl(x(6) - slot * .5, x(len(W) - 1) + slot * .5, y(LH), INK, 2.0)
    svg += tick(x(15), y(W[15]["h"]) - 18)
    svg += head(Wd, "الشمعة نفسها مكبَّرة على فريم التنفيذ")
    svg += note(x(5), "المنطقة كما هي", TEAL_D, H, 17)
    svg += note(x(17), "إغلاق فوق آخر قمة = إذن الدخول", TEAL_D, H, 17)
    return svg + badge(Wd, "تنفيذ داخل المنطقة", True) + "</svg>"

# ══════ 3) الخطأ: القرار من الفريم الصغير ══════
def ltf_only(Wd=880, H=250, seed=8303):
    N = 34
    anch = [(0, 13.0), (4, 14.2), (8, 12.8), (12, 14.4), (16, 12.9), (20, 14.6),
            (24, 13.0), (28, 14.3), (33, 13.1)]
    fresh(seed, anch, f"فريم صغير وحده {seed}")
    W = gen(anch, N, seed, wick=0.9)
    svg, x, y, slot = frame(W, Wd, H)
    for j in (6, 11, 15, 21, 26, 30):
        svg += xm(x(j), y(W[j]["c"]), r=8)
    svg += head(Wd, "فريم التنفيذ وحده: إشارات متناقضة")
    svg += note(x(7), "ست إشارات في جلسة", RED, H, 17)
    svg += note(x(26), "بلا جهة يحكمها فريم أعلى", RED, H, 17)
    return svg + badge(Wd, "قرار من المكان الخطأ", False) + "</svg>"

# ══════ 4) الخطأ: التنفيذ من الفريم الكبير ══════
def htf_exec(Wd=880, H=250, seed=8304):
    N = 28
    anch = [(0, 11.8), (5, 14.8), (9, 13.4), (14, 16.6), (19, 14.4), (23, 17.0), (27, 18.2)]
    fresh(seed, anch, f"تنفيذ من الكبير {seed}")
    W = gen(anch, N, seed, wick=0.85)
    rng = max(c["h"] for c in W) - min(c["l"] for c in W)
    for j in range(18, 21):                      # شمعة اندفاع كبيرة على الفريم الأعلى
        W[j]["l"] = min(W[j]["l"], W[j]["o"] - rng * 0.10)
        W[j]["h"] = max(W[j]["h"], W[j]["c"] + rng * 0.03)
    ENT = W[20]["c"]; STP = min(c["l"] for c in W[17:21]) - rng * 0.035
    TGT = ENT + (ENT - STP) * 0.55            # الهدف أقصر من المخاطرة بوضوح
    svg, x, y, slot = frame(W, Wd, H)
    svg += hl(x(20) - slot * .6, x(N - 1) + slot * .5, y(ENT), INK, 2.0)
    svg += hl(x(20) - slot * .6, x(N - 1) + slot * .5, y(STP), RED, 1.7, dash="7 5")
    svg += hl(x(20) - slot * .6, x(N - 1) + slot * .5, y(TGT), TEAL_D, 1.7)
    bx = x(N - 1) + slot * 0.9
    svg += (f'<line x1="{bx:.1f}" y1="{y(ENT):.1f}" x2="{bx:.1f}" y2="{y(STP):.1f}" stroke="{RED}" stroke-width="2.4"/>'
            f'<line x1="{bx-10:.1f}" y1="{y(ENT):.1f}" x2="{bx+10:.1f}" y2="{y(ENT):.1f}" stroke="{RED}" stroke-width="2.4"/>'
            f'<line x1="{bx-10:.1f}" y1="{y(STP):.1f}" x2="{bx+10:.1f}" y2="{y(STP):.1f}" stroke="{RED}" stroke-width="2.4"/>')
    svg += head(Wd, "دخول من شمعة الفريم الأعلى نفسها")
    svg += note(x(7), "الوقف خلف الشمعة كلها", RED, H, 17)
    svg += note(x(23), "الهدف أقصر من المخاطرة", RED, H, 17)
    return svg + badge(Wd, "وقف يبتلع العائد", False) + "</svg>"

# ══════ 5) التطابق: الفريمان في جهة واحدة ══════
def frames_align(Wd=880, H=250, seed=8305):
    N = 30
    anch = [(0, 12.0), (6, 15.4), (10, 14.0), (15, 17.2), (19, 15.6), (24, 18.6), (29, 20.4)]
    fresh(seed, anch, f"تطابق الفريمين {seed}")
    W = gen(anch, N, seed, wick=0.8)
    rng = max(c["h"] for c in W) - min(c["l"] for c in W)
    seg = W[8:11]
    ZT = max(max(c["o"], c["c"]) for c in seg); ZB = ZT - rng * 0.145
    for j in (19, 20):
        mid = (ZT + ZB) / 2
        W[j]["l"] = mid - rng * 0.008
        W[j]["o"] = ZT - rng * 0.004; W[j]["c"] = ZT + rng * 0.018
        W[j]["h"] = W[j]["c"] + rng * 0.018
    svg, x, y, slot = frame(W, Wd, H)
    svg += zbox(x(8) - slot * .6, y(ZT), x(N - 1) + slot * .5, y(ZB))
    svg += tick(x(22), y(W[22]["h"]) - 18)
    svg += head(Wd, "الأعلى صاعد · التنفيذ يؤكد داخل المنطقة")
    svg += note(x(8), "قرار: شراء من المنطقة", TEAL_D, H, 17)
    svg += note(x(24), "تنفيذ: تأكيد ثم هدف", TEAL_D, H, 17)
    return svg + badge(Wd, "الإعداد الأقوى", True) + "</svg>"

CAR_CHARTS = [htf_zone, ltf_entry, ltf_only, htf_exec, frames_align]
HERO = htf_zone
