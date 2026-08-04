# -*- coding: utf-8 -*-
"""ريل «ورقة الغش» — شبكة 2×3 تُبنى تباعاً (فكرة مطلوبة من فهد 2026-08-04).
الموضوع: ست مناطق على الجارت وماذا تفعل عند كل واحدة.
عقد التشغيل نفسه: #stage / window.__DUR / window.__setFrame(t) — يعمل مع reel_render_any.py
"""
import json, os
from reel_build import INK, TEAL, TEAL_D, TEAL_L, BULL, BEAR, RED, GREY, MUTE, CARDBD, FONT_CSS, htext, GEM

HERE = os.path.dirname(os.path.abspath(__file__))

# ───────── هندسة الشبكة ─────────
SW, SH = 1080, 1920
COLS, ROWS = 2, 3
MX, TOP = 52, 428          # هامش جانبي وبداية الشبكة
GAP_X, GAP_Y = 34, 100
CW_ = (SW - MX * 2 - GAP_X) // COLS       # عرض الخانة
CH_ = 300                                  # ارتفاع الخانة

def cell_xy(i):
    r, c = divmod(i, COLS)
    return MX + c * (CW_ + GAP_X), TOP + r * (CH_ + GAP_Y)

# ───────── محرك الجارت المصغّر داخل الخانة ─────────
from reel_build import gen as _gen

def _proj(X, Y, W, pl=44, pr=44, pt=64, pb=42):
    """يسقط الشموع داخل صندوق الخانة ويرجع دوال الإحداثيات."""
    x0, x1 = X + pl, X + CW_ - pr
    y0, y1 = Y + pt, Y + CH_ - pb
    lo = min(c["l"] for c in W); hi = max(c["h"] for c in W); rng = hi - lo
    lo -= rng * 0.07; hi += rng * 0.07
    n = len(W); slot = (x1 - x0) / n
    fx = lambda i: x0 + slot * i + slot / 2
    fy = lambda p: y0 + (hi - p) / (hi - lo) * (y1 - y0)
    return fx, fy, slot, (x0, x1, y0, y1)

def _candles(W, fx, fy, slot):
    bw = slot * 0.58
    out = []
    for i, c in enumerate(W):
        up = c["c"] >= c["o"]; col = BULL if up else BEAR
        cx = fx(i); yh, yl = fy(c["h"]), fy(c["l"]); yo, yc = fy(c["o"]), fy(c["c"])
        top, bot = min(yo, yc), max(yo, yc)
        out.append(f'<line x1="{cx:.1f}" y1="{yh:.1f}" x2="{cx:.1f}" y2="{yl:.1f}" stroke="{col}" stroke-width="1.9"/>')
        out.append(f'<rect x="{cx-bw/2:.1f}" y="{top:.1f}" width="{bw:.1f}" height="{max(bot-top,2.6):.1f}" fill="{col}" rx="0.8"/>')
    return "".join(out)

def band(x0, y0, x1, y1, col=TEAL, stroke=TEAL_D, op=0.16, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ''
    return (f'<rect x="{x0:.1f}" y="{min(y0,y1):.1f}" width="{x1-x0:.1f}" height="{abs(y1-y0):.1f}" fill="{col}" opacity="{op}"/>'
            f'<rect x="{x0:.1f}" y="{min(y0,y1):.1f}" width="{x1-x0:.1f}" height="{abs(y1-y0):.1f}" fill="none" '
            f'stroke="{stroke}" stroke-width="1.5"{d}/>')

def hline(x0, x1, y, col=INK, w=1.8, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<line x1="{x0:.1f}" y1="{y:.1f}" x2="{x1:.1f}" y2="{y:.1f}" stroke="{col}" stroke-width="{w}"{d}/>'

def arrow(x0, y0, x1, y1, col, w=3.2):
    import math
    ang = math.atan2(y1 - y0, x1 - x0)
    a1 = (x1 - 14 * math.cos(ang - 0.42), y1 - 14 * math.sin(ang - 0.42))
    a2 = (x1 - 14 * math.cos(ang + 0.42), y1 - 14 * math.sin(ang + 0.42))
    return (f'<line x1="{x0:.0f}" y1="{y0:.0f}" x2="{x1:.0f}" y2="{y1:.0f}" stroke="{col}" '
            f'stroke-width="{w}" stroke-linecap="round"/>'
            f'<polygon points="{x1:.0f},{y1:.0f} {a1[0]:.0f},{a1[1]:.0f} {a2[0]:.0f},{a2[1]:.0f}" fill="{col}"/>')

SEEDS = []

def _mk(seed, anch, N, label, wick=0.75):
    SEEDS.append((seed, anch, label))
    return _gen(anch, N, seed, wick=wick)

# ── 1) الفجوة السعرية: شمعة اندفاع تترك فراغاً بين ذيل ما قبلها وذيل ما بعدها
def art_fvg(X, Y):
    N, K = 15, 7
    W = _mk(7101, [(0, 11.6), (4, 11.0), (7, 13.6), (10, 13.2), (14, 14.6)], N, "خانة الفجوة")
    rng = max(c["h"] for c in W) - min(c["l"] for c in W)
    o = W[K-1]["c"]; step = rng * 0.34
    W[K].update(o=o, c=o + step, h=o + step + rng * 0.03, l=o - rng * 0.02)
    lo = o + step * 0.30; hi = o + step * 0.66
    p, nx = W[K-1], W[K+1]
    for k in ("h", "o", "c"): p[k] = min(p[k], lo)
    p["l"] = min(p["l"], p["c"] - rng * 0.03)
    for k in ("l", "o", "c"): nx[k] = max(nx[k], hi)
    nx["h"] = max(nx["h"], nx["c"] + rng * 0.03)
    for j in range(K+2, N):                       # يعود إلى الفجوة ثم يواصل
        W[j]["l"] = max(W[j]["l"], lo + (hi-lo)*0.2 if j in (10, 11) else hi + rng*0.01)
        W[j]["o"] = max(W[j]["o"], W[j]["l"]); W[j]["c"] = max(W[j]["c"], W[j]["l"])
        W[j]["h"] = max(W[j]["h"], max(W[j]["o"], W[j]["c"]) + rng*0.01)
    fx, fy, slot, (x0, x1, y0, y1) = _proj(X, Y, W)
    s = _candles(W, fx, fy, slot)
    s += band(fx(K)-slot*2.2, fy(hi), x1, fy(lo))
    s += htext(fx(K)-slot*2.9, fy((hi+lo)/2)+6, "FVG", TEAL_D, 18)
    return s

# ── 2) أوردر بلوك: آخر شمعة معاكسة قبل الاندفاع
def art_ob(X, Y):
    N, K = 15, 6
    W = _mk(7102, [(0, 13.2), (3, 12.2), (6, 11.6), (9, 13.8), (12, 13.0), (14, 14.6)], N, "خانة الأوردر بلوك")
    rng = max(c["h"] for c in W) - min(c["l"] for c in W)
    o = W[K-1]["c"]; body = rng * 0.13
    W[K].update(o=o, c=o - body, h=o + body*0.2, l=o - body*1.35)
    ZT, ZB = W[K]["o"], W[K]["c"]
    prev = W[K]["c"]
    for j in range(K+1, K+4):
        st = rng * 0.15
        W[j].update(o=prev, c=prev+st, h=prev+st+rng*0.025, l=prev-rng*0.015); prev = W[j]["c"]
    for j in range(K+4, N):
        floor = ZB + (ZT-ZB)*0.25 if j in (11, 12) else ZT + rng*0.01
        W[j]["l"] = max(W[j]["l"], floor)
        W[j]["o"] = max(W[j]["o"], W[j]["l"]); W[j]["c"] = max(W[j]["c"], W[j]["l"])
        W[j]["h"] = max(W[j]["h"], max(W[j]["o"], W[j]["c"]) + rng*0.015)
    fx, fy, slot, (x0, x1, y0, y1) = _proj(X, Y, W)
    s = _candles(W, fx, fy, slot)
    s += band(fx(K)-slot*0.7, fy(ZT), x1, fy(ZB))
    s += htext(fx(K)-slot*1.9, fy((ZT+ZB)/2)+6, "OB", TEAL_D, 18)
    return s

# ── 3) بريكر بلوك: بلوك فشل واخترقه السعر ثم انقلب مقاومة
def art_breaker(X, Y):
    N, K = 16, 5
    W = _mk(7103, [(0, 14.6), (3, 13.8), (5, 13.4), (8, 14.0), (11, 12.2), (16, 11.0)], N, "خانة البريكر")
    rng = max(c["h"] for c in W) - min(c["l"] for c in W)
    o = W[K-1]["c"]; body = rng * 0.12
    W[K].update(o=o, c=o - body, h=o + body*0.22, l=o - body*1.3)
    ZT, ZB = W[K]["o"], W[K]["c"]
    prev = W[K]["c"]
    for j in range(K+1, K+3):                       # صعود فاشل
        st = rng * 0.07
        W[j].update(o=prev, c=prev+st, h=prev+st+rng*0.02, l=prev-rng*0.015); prev = W[j]["c"]
    for j in range(K+3, K+6):                       # اختراق هابط
        st = rng * 0.13
        W[j].update(o=prev, c=prev-st, h=prev+rng*0.015, l=prev-st-rng*0.025); prev = W[j]["c"]
    for i, j in enumerate(range(K+6, K+9)):         # عودة تختبر البلوك من الأسفل
        tgt = ZB + (ZT-ZB)*(0.3+0.3*i)
        W[j].update(o=prev, c=tgt, h=tgt+rng*0.02, l=prev-rng*0.012); prev = tgt
    for i, j in enumerate(range(K+9, N)):           # رفض وهبوط
        st = rng * 0.11
        W[j].update(o=prev, c=prev-st, h=prev+rng*0.012, l=prev-st-rng*0.02); prev = W[j]["c"]
    fx, fy, slot, (x0, x1, y0, y1) = _proj(X, Y, W)
    s = _candles(W, fx, fy, slot)
    s += band(fx(K)-slot*0.7, fy(ZT), x1, fy(ZB), col=RED, stroke=RED, op=0.13)
    s += htext(x1-52, fy((ZT+ZB)/2)+6, "انقلبت", RED, 17)
    return s

# ── 4) قمم متساوية: مستوى واحد تلمسه ثلاث قمم وأوامر الوقف فوقه
def art_eqh(X, Y):
    N = 15
    W = _mk(7104, [(0, 11.6), (3, 13.4), (6, 12.2), (9, 13.4), (12, 12.4), (14, 13.4)], N, "خانة القمم المتساوية")
    rng = max(c["h"] for c in W) - min(c["l"] for c in W)
    HI = [3, 8, 13]
    HL = max(W[i]["h"] for i in HI)
    for i in HI:
        W[i]["h"] = HL; W[i]["c"] = min(W[i]["c"], HL - rng*0.05)
    for j in range(N):
        if j not in HI:
            cap = HL - rng*0.04
            W[j]["h"] = min(W[j]["h"], cap)
            W[j]["o"] = min(W[j]["o"], cap); W[j]["c"] = min(W[j]["c"], cap)
    fx, fy, slot, (x0, x1, y0, y1) = _proj(X, Y, W)
    s = _candles(W, fx, fy, slot)
    s += hline(x0, x1, fy(HL), INK, 2.0)
    for k in range(3):
        yy = fy(HL) - 8 - k*8
        s += f'<line x1="{x0+8:.1f}" y1="{yy:.1f}" x2="{x1-8:.1f}" y2="{yy:.1f}" stroke="{RED}" stroke-width="2.6" stroke-dasharray="9 7" opacity="{0.9-k*0.2:.2f}"/>'
    s += htext((x0+x1)/2, y1+2, "أوامر الوقف فوق المستوى", RED, 17)
    return s

# ── 5) منتصف المدى: نطاق واضح وخط 50% والسعر يشتري من الرخيص
def art_eq(X, Y):
    N = 16
    W = _mk(7105, [(0, 11.2), (4, 14.4), (8, 12.0), (11, 12.6), (13, 11.9), (15, 14.2)], N, "خانة منتصف المدى")
    rng = max(c["h"] for c in W) - min(c["l"] for c in W)
    HIv = max(c["h"] for c in W[:6]); LOv = min(c["l"] for c in W[:3])
    MIDv = (HIv + LOv) / 2
    for j in range(6, 14):                          # الرجعة تبقى تحت النصف
        cap = MIDv - rng*0.02
        W[j]["h"] = min(W[j]["h"], cap)
        W[j]["o"] = min(W[j]["o"], cap); W[j]["c"] = min(W[j]["c"], cap)
    fx, fy, slot, (x0, x1, y0, y1) = _proj(X, Y, W)
    s = band(x0, fy(MIDv), x1, fy(LOv), op=0.12)
    s += _candles(W, fx, fy, slot)
    s += hline(x0, x1, fy(HIv), INK, 1.9)
    s += hline(x0, x1, fy(LOv), INK, 1.9)
    s += hline(x0, x1, fy(MIDv), TEAL_D, 2.2, dash="7 6")
    s += htext(x0+34, fy(MIDv)-12, "50%", TEAL_D, 18)
    s += htext(x0+46, fy((MIDv+LOv)/2)+6, "الرخيص", TEAL_D, 17)
    return s

# ── 6) سحب السيولة: فتيل يخترق القاع ثم إغلاق فوقه وانطلاق
def art_sweep(X, Y):
    N, K = 15, 8
    W = _mk(7106, [(0, 13.6), (3, 12.4), (6, 12.8), (8, 12.2), (11, 13.6), (14, 14.8)], N, "خانة سحب السيولة")
    rng = max(c["h"] for c in W) - min(c["l"] for c in W)
    LOW = min(W[j]["l"] for j in range(2, 6))
    for j in range(6, K):
        W[j]["l"] = max(W[j]["l"], LOW + rng*0.03)
        W[j]["o"] = max(W[j]["o"], W[j]["l"]); W[j]["c"] = max(W[j]["c"], W[j]["l"])
    W[K].update(o=W[K-1]["c"], l=LOW - rng*0.06, c=LOW + rng*0.06,
                h=max(W[K-1]["c"], LOW + rng*0.06) + rng*0.02)
    prev = W[K]["c"]
    for i, j in enumerate(range(K+1, N)):
        st = rng * (0.13 if i < 4 else 0.05)
        W[j].update(o=prev, c=prev+st, h=prev+st+rng*0.02, l=prev-rng*0.015); prev = W[j]["c"]
    fx, fy, slot, (x0, x1, y0, y1) = _proj(X, Y, W)
    s = _candles(W, fx, fy, slot)
    s += hline(x0, x1, fy(LOW), INK, 1.9, dash="6 5")
    s += htext(x0+70, fy(LOW)+30, "سحب تحت القاع", RED, 17)
    return s

CELLS = [
    ("fvg",     "الفجوة السعرية (FVG)", art_fvg,     "انتظر العودة", TEAL_D,
     lambda X, Y: arrow(X + 230, Y + 214, X + 150, Y + 158, TEAL_D)),
    ("ob",      "أوردر بلوك",           art_ob,      "شراء من المنطقة", TEAL_D,
     lambda X, Y: arrow(X + 80, Y + 200, X + 236, Y + 74, TEAL_D)),
    ("breaker", "بريكر بلوك",           art_breaker, "بيع من المنطقة", RED,
     lambda X, Y: arrow(X + 84, Y + 96, X + 238, Y + 226, RED)),
    ("eqh",     "قمم متساوية",          art_eqh,     "سيولة… لا هدف", RED,
     lambda X, Y: arrow(X + 246, Y + 74, X + 176, Y + 118, RED)),
    ("eq",      "منتصف المدى",          art_eq,      "اشترِ تحت النصف", TEAL_D,
     lambda X, Y: arrow(X + 244, Y + 108, X + 176, Y + 196, TEAL_D)),
    ("sweep",   "سحب السيولة",          art_sweep,   "ادخل بعد السحب", TEAL_D,
     lambda X, Y: arrow(X + 84, Y + 214, X + 232, Y + 104, TEAL_D)),
]

def build(out_html="reel_grid.html"):
    frames, arts, verds, labels = [], [], [], []
    for i, (key, title, art, verdict, vcol, varrow) in enumerate(CELLS):
        X, Y = cell_xy(i)
        frames.append(f'<g id="fr{i}" opacity="0">'
                      f'<rect x="{X}" y="{Y}" width="{CW_}" height="{CH_}" fill="#FBF9F5" '
                      f'stroke="{CARDBD}" stroke-width="2"/></g>')
        labels.append(f'<g id="lb{i}" opacity="0">{htext(X + CW_/2, Y + CH_ + 42, title, INK, 27)}</g>')
        arts.append(f'<g id="ar{i}" opacity="0">{art(X, Y)}</g>')
        verds.append(f'<g id="vd{i}" opacity="0">{varrow(X, Y)}'
                     f'<rect x="{X+14}" y="{Y+14}" width="{len(verdict)*15+30}" height="42" '
                     f'fill="{"#EAF3F5" if vcol == TEAL_D else "#F8ECEC"}" stroke="{vcol}" stroke-width="1.6"/>'
                     + htext(X + 14 + (len(verdict)*15+30)/2, Y + 44, verdict, vcol, 24) + '</g>')

    # جداول التوقيت: [id, بداية, نهاية, نمط]
    marks = []
    for i in range(6):
        a = 2.75 + i * 0.22
        marks += [[f"fr{i}", a, a + 0.28, "pop"], [f"lb{i}", a + 0.12, a + 0.4, "fade"]]
    for i in range(6):
        a = 5.2 + i * 0.95
        marks.append([f"ar{i}", a, a + 0.55, "grow"])
    for i in range(6):
        a = 11.6 + i * 1.15
        marks.append([f"vd{i}", a, a + 0.42, "pop"])

    CTA_T, DUR = 19.6, 24.4
    SVG = ("".join(frames) + "".join(labels) + "".join(arts) + "".join(verds))

    html = f'''<!DOCTYPE html><html lang="ar" dir="rtl"><head><meta charset="utf-8"><style>
{FONT_CSS}
*{{margin:0;padding:0;box-sizing:border-box}}
#stage{{width:{SW}px;height:{SH}px;position:relative;overflow:hidden;font-family:Tajawal;
  background:radial-gradient(120% 90% at 50% 0%, #F7F3EC 0%, #F2EEE7 55%, #ECE6DB 100%)}}
#hd{{position:absolute;top:140px;left:40px;right:40px;text-align:center;opacity:0}}
#hd h1{{font-size:62px;font-weight:900;color:{INK};line-height:1.16;letter-spacing:-1px}}
#hd p{{margin-top:14px;font-size:31px;font-weight:600;color:{GREY}}}
#grid{{position:absolute;inset:0;transform-origin:540px 960px}}
#res{{position:absolute;top:1612px;left:40px;right:40px;text-align:center;font-size:46px;
  font-weight:900;color:{TEAL_D};opacity:0}}
#cta{{position:absolute;top:1694px;left:70px;right:70px;text-align:center;opacity:0}}
#cta .k{{display:inline-block;border:2.5px solid {INK};color:{INK};font-weight:900;font-size:52px;padding:12px 40px}}
#cta .s{{margin-top:14px;font-size:31px;font-weight:700;color:{GREY}}}
#edu{{position:absolute;bottom:44px;left:0;right:0;text-align:center;font-size:22px;color:#93A2A8;font-weight:600}}
#flash{{position:absolute;inset:0;background:#fff;opacity:0;pointer-events:none}}
#intro{{position:absolute;inset:0;z-index:5;display:flex;flex-direction:column;align-items:center;
  justify-content:center;gap:22px;background:radial-gradient(120% 90% at 50% 0%, #0C2029 0%, #08131C 55%, #04090F 100%)}}
#intro .ig{{width:112px}} #intro .ig svg{{width:112px;height:auto}}
#intro .iwm{{font-size:24px;font-weight:800;letter-spacing:10px;color:#B8C8CC}}
#intro .ieyeb{{margin-top:22px;font-size:29px;font-weight:700;color:#43D4DC}}
#intro .ihook{{font-size:72px;font-weight:900;color:#EDF4F5;text-align:center;line-height:1.26;padding:0 60px;opacity:0}}
#intro .ibar{{width:320px;height:3px;background:linear-gradient(90deg,transparent,#43D4DC,transparent)}}
#intro .isub{{font-size:32px;font-weight:700;color:#B8C8CC;opacity:0;padding:0 60px;text-align:center}}
#isweep{{position:absolute;top:0;bottom:0;left:0;width:340px;z-index:6;opacity:0;pointer-events:none;
  background:linear-gradient(100deg,transparent 0%,rgba(255,255,255,0.85) 45%,rgba(67,212,220,0.3) 55%,transparent 100%);
  transform:skewX(-12deg)}}
</style></head><body><div id="stage">
<div id="hd"><h1>ست مناطق على الجارت</h1><p>وماذا تفعل عند كل واحدة</p></div>
<svg id="grid" viewBox="0 0 {SW} {SH}" width="{SW}" height="{SH}" xmlns="http://www.w3.org/2000/svg">{SVG}</svg>
<div id="res">احفظها… ستحتاجها في كل جلسة</div>
<div id="cta"><span class="k">اكتب «مناطق»</span><div class="s">ليصلك الدليل الكامل — ست مناطق بشروطها</div></div>
<div id="edu">لغرض تعليمي — أمثلة تخطيطية</div>
<div id="flash"></div>
<div id="intro"><div class="ig">{GEM}</div><div class="iwm">LIQUIDITY STATE</div>
  <div class="ieyeb">ورقة الجارت السريعة</div>
  <div class="ihook" id="ihook">ست مناطق…<br>وقرار واحد لكلٍّ منها</div>
  <div class="ibar"></div>
  <div class="isub" id="isub">احفظها قبل جلسة الغد</div></div>
<div id="isweep"></div>
</div>
<script>
window.__DUR = {DUR};
const $ = id => document.getElementById(id);
const clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
const seg=(t,a,b)=>clamp((t-a)/(b-a),0,1);
const oc=t=>1-Math.pow(1-t,3);
const ob=t=>{{const c1=1.70158,c3=c1+1;return 1+c3*Math.pow(t-1,3)+c1*Math.pow(t-1,2);}};
const MARKS = {json.dumps(marks)};
const CTA_T = {CTA_T};
window.__setFrame = function(t) {{
  // الافتتاحية الداكنة ثم المسحة الضوئية
  const iw = seg(t, 2.5, 3.05), intro = $("intro");
  if (iw >= 1) intro.style.display = "none";
  else {{ intro.style.display=""; intro.style.clipPath = `inset(0 0 0 ${{(iw*100).toFixed(2)}}%)`; }}
  const ihk = oc(seg(t, 0.2, 0.75));
  $("ihook").style.opacity = ihk;
  $("ihook").style.transform = `translateY(${{((1-ihk)*26).toFixed(1)}}px)`;
  $("isub").style.opacity = oc(seg(t, 0.65, 1.1));
  const iswk = seg(t, 2.45, 3.12), isw = $("isweep");
  if (iswk>0 && iswk<1) {{ isw.style.opacity = 0.7*Math.sin(Math.PI*iswk);
    isw.style.transform = `translateX(${{(-360+1560*iswk).toFixed(0)}}px) skewX(-12deg)`; }}
  else isw.style.opacity = 0;
  // العنوان
  const hk = oc(seg(t, 2.6, 3.1));
  $("hd").style.opacity = hk * (1 - seg(t, CTA_T-0.6, CTA_T));
  $("hd").style.transform = `translateY(${{((1-hk)*18).toFixed(1)}}px)`;
  // عناصر الشبكة
  for (const [id,a,b,mode] of MARKS) {{
    const el = $(id); const k = seg(t,a,b);
    if (mode === "pop") {{
      el.style.opacity = oc(k);
      el.style.transformBox="fill-box"; el.style.transformOrigin="50% 50%";
      el.style.transform = `scale(${{(0.72+0.28*ob(k)).toFixed(4)}})`;
    }} else if (mode === "grow") {{
      el.style.opacity = Math.min(oc(k*1.6),1);
      el.style.transformBox="fill-box"; el.style.transformOrigin="50% 100%";
      el.style.transform = `scaleY(${{(0.25+0.75*oc(k)).toFixed(4)}})`;
    }} else {{ el.style.opacity = oc(k); }}
  }}
  // نبضة إضاءة على الخانة لحظة صدور حكمها
  for (let i=0;i<6;i++) {{
    const a = 11.6 + i*1.15;
    const p = seg(t, a, a+0.5);
    const fr = $("fr"+i).querySelector("rect");
    if (p>0 && p<1) {{ fr.setAttribute("stroke", "{TEAL}"); fr.setAttribute("stroke-width", (2+2.4*Math.sin(Math.PI*p)).toFixed(2)); }}
    else if (p>=1) {{ fr.setAttribute("stroke", "{CARDBD}"); fr.setAttribute("stroke-width", 2); }}
  }}
  // تنفّس مجهري للشبكة + انكماش خفيف عند الخلاصة
  const br = 1 + 0.0035*Math.sin(t*0.7);
  const shrink = 1 - 0.045*seg(t, CTA_T-1.0, CTA_T+0.4);
  $("grid").style.transform = `scale(${{(br*shrink).toFixed(4)}})`;
  // الخلاصة والدعوة
  $("res").style.opacity = oc(seg(t, 18.4, 18.9)) * (1 - seg(t, CTA_T-0.2, CTA_T+0.2));
  const ck = oc(seg(t, CTA_T, CTA_T+0.45));
  $("cta").style.opacity = ck;
  $("cta").style.transform = `translateY(${{((1-ck)*26).toFixed(1)}}px) scale(${{(1+0.02*Math.sin(2*Math.PI*(t-CTA_T)*0.75)).toFixed(4)}})`;
  const f1 = seg(t, 18.4, 18.55), f2 = seg(t, 18.55, 18.95);
  $("flash").style.opacity = f1>0 && f2<1 ? 0.32*(f1<1?f1:(1-f2)) : 0;
}};
window.__setFrame(0);
</script></body></html>'''
    p = os.path.join(HERE, out_html)
    open(p, "w", encoding="utf-8").write(html)
    print("grid reel:", len(html), "| DUR", DUR, "| CTA", CTA_T)
    return DUR, CTA_T

if __name__ == "__main__":
    build()
