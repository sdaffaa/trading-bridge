# -*- coding: utf-8 -*-
"""وحدتا تشغيلة المصنع المتبقيتان (ريل + دليل لكل منهما) + سداد دين دليل «1000».
- تعادل (مالية): البريك إيفن — التأمين المبكر يخرجك، والهيكل الجديد هو الشرط.
- ثبات (نفسية): الثبات قبل المضاعفة — الحساب الصغير مختبر.
"""
import json, os, sys
from reel_build import INK, TEAL, TEAL_D, RED, GREY, MUTE, htext, gen, chart
from reel_sfx_kit import build_reel, geom, line_el, xmark, checkmark, zone_el, ring
from run9_reels import shift_cfg
from guide_build import build_guide
from car_common import dkmap
import chart_registry

HERE = os.path.dirname(os.path.abspath(__file__))
CONT = os.path.join(HERE, "..", "content")
CHARTS = []

def fresh(seed, anch, label):
    chart_registry.assert_fresh_synthetic(seed, anch, label=label)
    CHARTS.append((seed, anch, label))

def frame(W, Wd, H, pad=0.08):
    ymin = min(c["l"] for c in W); ymax = max(c["h"] for c in W); rng = ymax - ymin
    return chart(W, Wd, H, ymin - rng * pad, ymax + rng * pad, grid=4, pl=12, pr=16, pt=20, pb=14, body=0.6)

def tickmark(cx, cy, col=TEAL_D):
    return (f'<polyline points="{cx-10:.1f},{cy:.1f} {cx-3:.1f},{cy+8:.1f} {cx+12:.1f},{cy-10:.1f}" fill="none" '
            f'stroke="{col}" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round"/>')

def xmk(cx, cy, r=11, col=RED):
    return (f'<g stroke="{col}" stroke-width="3" stroke-linecap="round">'
            f'<line x1="{cx-r:.1f}" y1="{cy-r:.1f}" x2="{cx+r:.1f}" y2="{cy+r:.1f}"/>'
            f'<line x1="{cx-r:.1f}" y1="{cy+r:.1f}" x2="{cx+r:.1f}" y2="{cy-r:.1f}"/></g>')

# ═══════════ بيانات قصة البريك إيفن ═══════════
def _be_data(seed, anch, N, ient, idip, ok, label, wick=0.8):
    """دخول شراء، ارتفاع بسيط، ثم تنفّس يعود إلى نقطة الدخول، ثم انطلاق للهدف.
    ok=False: الوقف كان عند الدخول فخرج · ok=True: الوقف خلف قاع أعلى فنجا."""
    fresh(seed, anch, label)
    W = gen(anch, N, seed, wick=wick)
    rng = max(c["h"] for c in W) - min(c["l"] for c in W)
    ENT = W[ient]["c"]
    for j in range(ient + 1, idip):                    # ارتفاع أولي فوق الدخول
        W[j]["l"] = max(W[j]["l"], ENT + rng * 0.015)
        W[j]["o"] = max(W[j]["o"], W[j]["l"]); W[j]["c"] = max(W[j]["c"], W[j]["l"])
        W[j]["h"] = max(W[j]["h"], max(W[j]["o"], W[j]["c"]) + rng * 0.01)
    LOW2 = ENT + rng * 0.055                            # قاع أعلى (الهيكل الجديد)
    W[idip - 1]["l"] = LOW2
    W[idip - 1]["c"] = max(W[idip - 1]["c"], LOW2 + rng * 0.01)
    W[idip].update(o=W[idip - 1]["c"], c=ENT - rng * 0.012,
                   h=W[idip - 1]["c"] + rng * 0.01, l=ENT - rng * 0.03)   # التنفّس يلمس الدخول
    prev = W[idip]["c"]
    for i, j in enumerate(range(idip + 1, N)):          # ثم الانطلاق
        step = rng * (0.085 if i < 5 else 0.03)
        W[j].update(o=prev, c=prev + step, h=prev + step + rng * 0.02, l=prev - rng * 0.012)
        prev = W[j]["c"]
    return W, ENT, LOW2, rng

def be_chart(Wd=880, H=300, seed=6101, hero=False):
    N = 32
    anch = [(0, 13.6), (4, 12.4), (8, 11.8), (11, 12.2), (15, 13.4), (18, 12.9),
            (21, 13.6), (25, 15.0), (31, 16.4)]
    W, ENT, LOW2, rng = _be_data(seed, anch, N, 11, 19, False, f"تعادل {seed}")
    svg, x, y, slot = frame(W, Wd, H)
    svg += (f'<line x1="{x(11)-slot*0.6:.1f}" y1="{y(ENT):.1f}" x2="{x(N-1)+slot*0.5:.1f}" y2="{y(ENT):.1f}" '
            f'stroke="{INK}" stroke-width="1.9"/>')
    svg += htext(x(12), y(ENT) + 36, "الدخول = الوقف بعد التأمين", INK, 16)
    svg += xmk(x(19), y(ENT) + 4)
    svg += htext(x(23), y(ENT) + 66, "التنفّس أخرجك ✗", RED, 16)
    if not hero:
        svg += (f'<line x1="{x(16)-slot*0.6:.1f}" y1="{y(LOW2):.1f}" x2="{x(N-1)+slot*0.5:.1f}" y2="{y(LOW2):.1f}" '
                f'stroke="{TEAL_D}" stroke-width="1.7" stroke-dasharray="5 5"/>')
        svg += htext(x(26), y(LOW2) - 12, "قاع أعلى — الوقف خلفه ✓", TEAL_D, 16)
        svg += tickmark(x(29), y(W[29]["c"]) - 24)
    return svg + "</svg>"

def be_right(Wd=620, H=300, seed=6102):
    N = 28
    anch = [(0, 13.4), (4, 12.2), (8, 11.6), (11, 12.0), (15, 13.2), (18, 12.7), (21, 13.4), (27, 15.6)]
    W, ENT, LOW2, rng = _be_data(seed, anch, N, 11, 18, True, f"تعادل صحيح {seed}")
    svg, x, y, slot = frame(W, Wd, H)
    svg += (f'<line x1="{x(11)-slot*0.6:.1f}" y1="{y(ENT):.1f}" x2="{x(N-1):.1f}" y2="{y(ENT):.1f}" '
            f'stroke="{INK}" stroke-width="1.6" opacity="0.5"/>')
    svg += (f'<line x1="{x(15)-slot*0.6:.1f}" y1="{y(LOW2):.1f}" x2="{x(N-1):.1f}" y2="{y(LOW2):.1f}" '
            f'stroke="{TEAL_D}" stroke-width="1.8" stroke-dasharray="5 5"/>')
    svg += htext(x(21), y(LOW2) - 11, "الوقف خلف القاع الأعلى ✓", TEAL_D, 16)
    svg += tickmark(x(25), y(W[25]["c"]) - 22)
    return svg + "</svg>"

def be_partial(Wd=620, H=300, seed=6103):
    """جني جزئي بدل النقل المبكر."""
    N = 28
    anch = [(0, 13.2), (4, 12.0), (8, 11.5), (11, 11.9), (15, 13.0), (18, 12.6), (21, 13.3), (27, 15.2)]
    W, ENT, LOW2, rng = _be_data(seed, anch, N, 11, 18, True, f"جني جزئي {seed}")
    svg, x, y, slot = frame(W, Wd, H)
    P1 = ENT + rng * 0.16
    svg += (f'<line x1="{x(11)-slot*0.6:.1f}" y1="{y(P1):.1f}" x2="{x(N-1):.1f}" y2="{y(P1):.1f}" '
            f'stroke="{TEAL}" stroke-width="1.7" stroke-dasharray="4 6"/>')
    svg += htext(x(17), y(P1) - 11, "جني جزئي ✓", TEAL_D, 16)
    svg += (f'<line x1="{x(11)-slot*0.6:.1f}" y1="{y(ENT):.1f}" x2="{x(N-1):.1f}" y2="{y(ENT):.1f}" '
            f'stroke="{INK}" stroke-width="1.5" opacity="0.45"/>')
    svg += tickmark(x(25), y(W[25]["c"]) - 22)
    return svg + "</svg>"

# ═══════════ جارت الثبات (منحنى حساب لا سعر) ═══════════
def equity_chart(Wd=880, H=300, seed=6201, hero=False):
    """منحنيان: التزام ثابت مقابل مضاعفة مبكرة — رسم خطي لا شموع (بيانات تخطيطية)."""
    label = f"منحنى ثبات {seed}"
    anch = [(0, 10.0), (10, 10.0)]
    fresh(seed, anch, label)
    import random
    rnd = random.Random(seed)
    n = 40
    a = [100.0]; b = [100.0]
    for i in range(1, n):
        r = rnd.uniform(-1.0, 1.35)
        a.append(a[-1] + r * 1.0)                      # حجم ثابت منضبط
        mult = 3.2 if i > 14 else 1.0                  # مضاعفة مبكرة بعد 14 صفقة
        b.append(b[-1] + r * mult - (2.4 if i in (17, 23, 29, 33) else 0))
    lo = min(min(a), min(b)) - 4; hi = max(max(a), max(b)) + 4
    pl, pr, pt, pb = 46, 16, 22, 26
    pw = Wd - pl - pr; ph = H - pt - pb
    X = lambda i: pl + pw * i / (n - 1)
    Y = lambda v: pt + (hi - v) / (hi - lo) * ph
    s = [f'<svg class="chartsvg" viewBox="0 0 {Wd} {H}" width="{Wd}" height="{H}" xmlns="http://www.w3.org/2000/svg">']
    for k in range(5):
        gy = pt + ph * k / 4
        s.append(f'<line x1="{pl}" y1="{gy:.1f}" x2="{Wd-pr}" y2="{gy:.1f}" stroke="rgba(15,46,60,0.06)" stroke-width="1"/>')
    s.append(f'<line x1="{pl}" y1="{Y(100):.1f}" x2="{Wd-pr}" y2="{Y(100):.1f}" stroke="{MUTE}" stroke-width="1.2" stroke-dasharray="4 5"/>')
    pa = " ".join(f"{X(i):.1f},{Y(v):.1f}" for i, v in enumerate(a))
    pb_ = " ".join(f"{X(i):.1f},{Y(v):.1f}" for i, v in enumerate(b))
    s.append(f'<polyline points="{pb_}" fill="none" stroke="{RED}" stroke-width="2.4" opacity="0.85"/>')
    s.append(f'<polyline points="{pa}" fill="none" stroke="{TEAL_D}" stroke-width="2.8"/>')
    s.append(f'<line x1="{X(14):.1f}" y1="{pt}" x2="{X(14):.1f}" y2="{pt+ph}" stroke="{INK}" stroke-width="1.4" stroke-dasharray="6 5"/>')
    s.append(htext(X(14) + 74, pt + 18, "لحظة المضاعفة", INK, 16))
    s.append(htext(X(33), Y(a[33]) - 18, "حجم ثابت ✓", TEAL_D, 16))
    s.append(htext(X(30), Y(b[30]) + 26, "مضاعفة مبكرة ✗", RED, 16))
    if not hero:
        s.append(htext(X(6), Y(100) - 14, "خط البداية", MUTE, 15))
    return "".join(s) + "</svg>"

def sample_chart(Wd=620, H=300, seed=6202):
    """جدول العيّنة: عدد الصفقات مقابل ثبات النتيجة (أعمدة تخطيطية)."""
    fresh(seed, [(0, 1.0), (5, 1.0)], f"أعمدة العيّنة {seed}")
    import random
    rnd = random.Random(seed)
    vals = [rnd.uniform(-2.0, 2.6) for _ in range(24)]
    pl, pr, pt, pb = 30, 16, 24, 28
    pw = Wd - pl - pr; ph = H - pt - pb
    mid = pt + ph / 2
    bw = pw / 24 * 0.62
    s = [f'<svg class="chartsvg" viewBox="0 0 {Wd} {H}" width="{Wd}" height="{H}" xmlns="http://www.w3.org/2000/svg">']
    s.append(f'<line x1="{pl}" y1="{mid:.1f}" x2="{Wd-pr}" y2="{mid:.1f}" stroke="{MUTE}" stroke-width="1.2"/>')
    for i, v in enumerate(vals):
        cx = pl + pw * (i + 0.5) / 24
        h = abs(v) / 2.6 * (ph / 2 - 8)
        col = TEAL_D if v >= 0 else RED
        yy = mid - h if v >= 0 else mid
        s.append(f'<rect x="{cx-bw/2:.1f}" y="{yy:.1f}" width="{bw:.1f}" height="{h:.1f}" fill="{col}" opacity="0.85"/>')
    s.append(htext(pl + pw * 0.5, pt + 4, "عيّنة واحدة لا تكفي للحكم", GREY, 16))
    return "".join(s) + "</svg>"

# ═══════════ الريلات ═══════════
def build_reel_be():
    R = json.load(open(os.path.join(CONT, "day3_tadul.json"), encoding="utf-8"))["reel"]
    N, SEED = 34, 6301
    ANCH = [(0, 13.4), (4, 12.2), (8, 11.6), (11, 12.0), (15, 13.4), (18, 12.9),
            (21, 13.7), (25, 15.0), (33, 16.6)]
    W, ENT, LOW2, RNG = _be_data(SEED, ANCH, N, 11, 20, False, "ريل التعادل")
    x, y, slot = geom(W)
    ex = []
    ex.append(line_el(x(11) - slot * 0.6, y(ENT), x(N - 1) + slot * 0.5, y(ENT), INK, 2.2, id="ent"))
    ex.append(f'<g id="entlbl" opacity="0">{htext(x(15), y(ENT) - 18, "نقطة الدخول", INK, 23)}</g>')
    ex.append(f'<g id="be" opacity="0">'
              f'<rect x="{x(11)-slot*0.6:.1f}" y="{y(ENT)-3:.1f}" width="{x(N-1)-x(11)+slot:.1f}" height="6" fill="{RED}" opacity="0.30"/>'
              + htext(x(24), y(ENT) - 42, "نقلت الوقف إلى التعادل", RED, 23) + '</g>')
    ex.append(xmark(x(20), y(ENT) + 6, id="hit", r=15))
    ex.append(f'<g id="hitlbl" opacity="0">{htext(x(20) - slot * 3.6, y(ENT) + 56, "تنفّس عادي… أخرجك", RED, 23)}</g>')
    ex.append(line_el(x(15) - slot * 0.6, y(LOW2), x(N - 1) + slot * 0.5, y(LOW2), TEAL_D, 2.0, dash="5 5", id="hh"))
    ex.append(f'<g id="hhlbl" opacity="0">{htext(x(27), y(LOW2) - 16, "قاع أعلى — انقله خلفه", TEAL_D, 23)}</g>')
    ex.append(checkmark(x(31), y(W[31]["c"]) - 32, id="ck"))
    ex.append(f'<g id="reslbl" opacity="0">{htext(x(28), y(W[32]["h"]) - 26, "الهيكل قبل التعادل", TEAL_D, 25)}</g>')
    story = [(20, 9.6)] + [(j, round(11.0 + (j - 21) * 0.26, 2)) for j in range(21, N)]
    cfg = dict(
        w=W, base=19, openmax=32, open_t=[[33, 0.35]], story=story,
        extra_svg="".join(ex),
        marks=[["ent", 2.6, 3.1, "draw"], ["entlbl", 3.1, 3.35, "pop"],
               ["be", 5.2, 5.55, "pop", 13.4, 0.4],
               ["hit", 9.9, 10.25, "drawx"], ["hitlbl", 10.25, 10.5, "pop", 13.4, 0.4],
               ["hh", 13.6, 14.1, "draw"], ["hhlbl", 14.1, 14.35, "pop"],
               ["ck", 15.9, 16.2, "pop"], ["reslbl", 16.2, 16.5, "pop"]],
        fullset=["entlbl", "be", "hit", "hitlbl", "hhlbl", "ck", "reslbl"],
        drawset=["ent", "hh"],
        txt=[(f"t{i+2}", a, b, t, fs, INK) for i, (a, b, fs, t) in enumerate(
            [(2.45, 4.6, 50, R["lines"][0]), (4.85, 7.2, 48, R["lines"][1]),
             (7.45, 9.6, 48, R["lines"][2]), (9.85, 12.4, 48, R["lines"][3]),
             (12.65, 15.4, 46, R["lines"][4]), (15.65, 17.6, 48, R["lines"][5])])],
        chip="البريك إيفن · لغرض تعليمي",
        res=R["res"], cta_k="اكتب «تعادل»", cta_s=R["cta_s"],
        edu="لغرض تعليمي — مثال تخطيطي",
        dur=22.0, res_t=17.9, cta_t=19.3, flash=(9.9, 10.55), punch=(9.85, 11.15, 0.05),
        punch_origin="55% 50%", rflash=10.0,
        intro=dict(eyeb="درس تطبيقي — إدارة الصفقة", hook=R["hook"], sub=R["sub"], t=2.5))
    fx = lambda i: x(i) / 1000; fy = lambda p: y(p) / 820
    cfg["cam"] = [[0.0, 1.03, .5, .5], [2.3, 1.06, .5, .5, "creep"],
                  [3.0, 1.7, fx(14), fy(ENT), "anticip"],
                  [5.4, 1.55, fx(18), fy(ENT), "creep"],
                  [9.7, 1.95, fx(20), fy(ENT), "anticip"],
                  [11.4, 1.5, fx(24), fy((ENT + W[26]["c"]) / 2), "whip", -1.1],
                  [13.8, 1.7, fx(22), fy(LOW2), "creep", 0],
                  [16.1, 1.35, fx(30), fy(W[30]["c"]), "creep"],
                  [18.1, 1.12, .5, .48, "creep"], [19.5, 1.02, .5, .5, "creep"], [22.0, 1.03, .5, .5, "creep"]]
    shift_cfg(cfg)
    print("be reel:", build_reel(cfg, "reel_day3_tadul.html"), "| dur", cfg["dur"], "| flash", cfg["flash"], "| cta", cfg["cta_t"])
    return cfg["dur"], cfg["flash"][0], cfg["cta_t"]

def build_reel_thabat():
    R = json.load(open(os.path.join(CONT, "day3_thabat.json"), encoding="utf-8"))["reel"]
    N, SEED = 34, 6302
    ANCH = [(0, 12.0), (5, 13.2), (9, 12.4), (13, 13.6), (17, 12.6), (21, 13.9),
            (24, 12.8), (28, 14.4), (33, 15.4)]
    fresh(SEED, ANCH, "ريل الثبات")
    W = gen(ANCH, N, SEED, wick=0.8)
    RNG = max(c["h"] for c in W) - min(c["l"] for c in W)
    IBIG = 22                                   # لحظة مضاعفة الحجم
    for j in range(IBIG, N):                    # تقلب أعنف بعد المضاعفة (نفس المسار، أثر أكبر)
        mid = (W[j]["o"] + W[j]["c"]) / 2
        for k in ("o", "c", "h", "l"):
            W[j][k] = mid + (W[j][k] - mid) * 2.1
    x, y, slot = geom(W)
    ex = []
    ex.append(line_el(x(IBIG) - slot * 0.5, 30, x(IBIG) - slot * 0.5, 792, INK, 2.0, dash="7 6", id="big"))
    ex.append(f'<g id="biglbl" opacity="0">{htext(x(IBIG) - slot * 3.2, 58, "ضاعفتَ الحجم هنا", INK, 24)}</g>')
    ex.append(f'<g id="samp" opacity="0">'
              f'<rect x="{x(6)-slot*0.6:.1f}" y="{y(max(c["h"] for c in W[4:12]))-58:.1f}" width="{slot*9:.1f}" height="42" '
              f'fill="#F2EEE7" stroke="{TEAL_D}" stroke-width="1.3"/>'
              + htext(x(10), y(max(c["h"] for c in W[4:12])) - 28, "عيّنة صغيرة… لا حكم", TEAL_D, 22) + '</g>')
    lo_i = min(range(IBIG, N), key=lambda j: W[j]["l"])
    ex.append(f'<g id="dd" opacity="0">'
              f'<rect x="{x(IBIG)-slot*0.5:.1f}" y="{y(max(c["h"] for c in W[IBIG:])):.1f}" '
              f'width="{x(N-1)-x(IBIG)+slot:.1f}" height="{y(W[lo_i]["l"])-y(max(c["h"] for c in W[IBIG:])):.1f}" '
              f'fill="{RED}" opacity="0.07"/>'
              + htext(x(28), y(W[lo_i]["l"]) + 34, "التقلب تضاعف… لا الخبرة", RED, 23) + '</g>')
    ex.append(f'<g id="reslbl" opacity="0">{htext(x(24), y(max(c["h"] for c in W[26:])) - 26, "ثبّت النتيجة قبل الحجم", TEAL_D, 25)}</g>')
    story = [(j, round(2.4 + (j - 12) * 0.42, 2)) for j in range(12, 22)]
    story += [(j, round(9.6 + (j - 22) * 0.34, 2)) for j in range(22, N)]
    cfg = dict(
        w=W, base=11, openmax=32, open_t=[[33, 0.35]], story=story,
        extra_svg="".join(ex),
        marks=[["samp", 4.2, 4.55, "pop", 9.2, 0.4],
               ["big", 9.3, 9.8, "draw"], ["biglbl", 9.8, 10.05, "pop"],
               ["dd", 13.0, 13.4, "fade"],
               ["reslbl", 15.6, 15.9, "pop"]],
        fullset=["samp", "biglbl", "dd", "reslbl"],
        drawset=["big"],
        txt=[(f"t{i+2}", a, b, t, fs, INK) for i, (a, b, fs, t) in enumerate(
            [(2.45, 4.4, 50, R["lines"][0]), (4.65, 6.9, 48, R["lines"][1]),
             (7.15, 9.2, 48, R["lines"][2]), (9.45, 12.2, 48, R["lines"][3]),
             (12.45, 15.0, 46, R["lines"][4]), (15.25, 17.4, 48, R["lines"][5])])],
        chip="الثبات قبل المضاعفة · لغرض تعليمي",
        res=R["res"], cta_k="اكتب «ثبات»", cta_s=R["cta_s"],
        edu="لغرض تعليمي — مثال تخطيطي",
        dur=22.0, res_t=17.7, cta_t=19.1, flash=(9.4, 10.05), punch=(9.35, 10.65, 0.05),
        punch_origin="50% 40%", rflash=13.1,
        intro=dict(eyeb="درس تطبيقي — نفسية التداول", hook=R["hook"], sub=R["sub"], t=2.5))
    fx = lambda i: x(i) / 1000; fy = lambda p: y(p) / 820
    cfg["cam"] = [[0.0, 1.03, .5, .5], [2.3, 1.06, .5, .5, "creep"],
                  [3.0, 1.6, fx(9), fy(W[9]["c"]), "anticip"],
                  [6.0, 1.45, fx(16), fy(W[16]["c"]), "creep"],
                  [9.3, 1.85, fx(IBIG), fy(W[IBIG]["c"]), "anticip"],
                  [11.2, 1.35, fx(27), fy(W[27]["c"]), "whip", -1.1],
                  [13.4, 1.4, fx(29), fy(W[29]["c"]), "creep", 0],
                  [17.9, 1.12, .5, .48, "creep"], [19.3, 1.02, .5, .5, "creep"], [22.0, 1.03, .5, .5, "creep"]]
    shift_cfg(cfg)
    print("thabat reel:", build_reel(cfg, "reel_day3_thabat.html"), "| dur", cfg["dur"], "| flash", cfg["flash"], "| cta", cfg["cta_t"])
    return cfg["dur"], cfg["flash"][0], cfg["cta_t"]

# ═══════════ الأدلة ═══════════
GUIDES = {
 "tadul":  dict(file="day3_tadul.json", kw="تعادل", eyebrow="دليل — إدارة الصفقة",
                title="البريك إيفن<br>ومتى تنقل وقفك",
                hero=lambda: be_chart(700, 330, seed=6111, hero=True),
                charts=[lambda: be_chart(880, 260, seed=6112), lambda: be_right(880, 260, seed=6113),
                        lambda: be_partial(880, 260, seed=6114), lambda: be_chart(880, 260, seed=6115),
                        lambda: be_right(880, 260, seed=6116)]),
 "thabat": dict(file="day3_thabat.json", kw="ثبات", eyebrow="دليل — نفسية التداول",
                title="الثبات<br>قبل المضاعفة",
                hero=lambda: equity_chart(700, 330, seed=6211, hero=True),
                charts=[lambda: equity_chart(880, 260, seed=6212), lambda: sample_chart(880, 260, seed=6213),
                        lambda: equity_chart(880, 260, seed=6214), lambda: sample_chart(880, 260, seed=6215),
                        lambda: equity_chart(880, 260, seed=6216)]),
 "alf":    dict(file="day3_alf.json", kw="1000", eyebrow="دليل — الخطة الأسبوعية",
                title="الخطوات الثماني<br>خطة الألف نقطة",
                hero=lambda: be_chart(700, 330, seed=6311, hero=True),
                charts=[lambda: be_chart(880, 260, seed=6312), lambda: be_right(880, 260, seed=6313),
                        lambda: be_partial(880, 260, seed=6314), lambda: be_chart(880, 260, seed=6315),
                        lambda: be_right(880, 260, seed=6316)]),
}

def build_guide_unit(key):
    u = GUIDES[key]
    gd = json.load(open(os.path.join(CONT, u["file"]), encoding="utf-8"))["guide"]
    pages, tk = [], 0
    for pg in gd["pages"]:
        p = dict(title=pg["title"], paras=pg.get("paras", []))
        if pg.get("rules"):
            p["rules"] = [dict(t=r["t"], bad=bool(r.get("bad"))) for r in pg["rules"]]
        if pg.get("note"):
            p["note"] = pg["note"]
        if pg["title"].strip().startswith("الصفقة") and tk < len(u["charts"]):
            p["svg"] = u["charts"][tk](); tk += 1
        pages.append(p)
    cfg = dict(eyebrow=u["eyebrow"], title=u["title"], keyword=u["kw"], subtitle=gd["subtitle"],
               hero=dkmap(u["hero"]()), pages=pages,
               outro_title=gd["outro_title"], outro_items=gd["outro_items"])
    n = build_guide(cfg, os.path.join(HERE, f"guide_day3_{key}.html"))
    print(f"guide_day3_{key}.html: {n} pages | charts: {tk}")

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "all"
    meta = {}
    if mode in ("all", "reels"):
        meta["tadul"] = build_reel_be()
        meta["thabat"] = build_reel_thabat()
        with open(os.path.join(HERE, "day3_reels_meta.json"), "w", encoding="utf-8") as f:
            json.dump(meta, f, ensure_ascii=False)
    if mode in ("all", "guides"):
        for k in ("tadul", "thabat", "alf"):
            if os.path.exists(os.path.join(CONT, GUIDES[k]["file"])):
                build_guide_unit(k)
    chart_registry.register_synthetic("day3-factory-2026-08-04", CHARTS)
    print("registered charts:", len(CHARTS))
