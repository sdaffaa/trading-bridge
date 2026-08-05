# -*- coding: utf-8 -*-
# قالب ريل المؤثرات (§12 — بدون كلام): جارت حقيقي واحد بريبلاي حي + بيتات نصية + ذروة فلاش/زوم
# مشتق من reel_sheet_build.py وصار بارامتري: build_reel(cfg) يكتب HTML جاهز للرندر.
import json, math, os
from reel_build import INK, TEAL, TEAL_D, RED, BULL, BEAR, FONT_CSS, htext, hend, GEM

HERE = os.path.dirname(os.path.abspath(__file__))
CW, CH = 1000, 820

def set_canvas(w, h):
    """يغيّر مساحة رسم الجارت (viewBox) قبل geom/build_reel — لتوزيع شاشة مختلف.
    ليس تشويهاً للشموع: الشموع تُرسم أصلاً داخل المساحة الجديدة من نفس OHLC."""
    global CW, CH
    CW, CH = w, h

PAD = (16, 20, 26, 20)          # يسار · يمين · أعلى · أسفل

def set_pad(pl, pr, pt, pb):
    """يفرّغ حزاماً حول منطقة الشموع — محور السعر يميناً ومحور الوقت أسفل كما في المنصات."""
    global PAD
    PAD = (pl, pr, pt, pb)

def plot_box():
    pl, pr, pt, pb = PAD
    return pl, pr, pt, pb, CW - pl - pr, CH - pt - pb

def price_scale(W_):
    """المدى السعري نفسه الذي تستعمله geom — ليتطابق محور السعر مع الشموع."""
    ymin = min(c["l"] for c in W_); ymax = max(c["h"] for c in W_)
    pad = (ymax - ymin) * 0.08
    return ymin - pad * 1.7, ymax + pad

def geom(W_):
    N = len(W_)
    ymin, ymax = price_scale(W_)
    pl, pr, pt, pb = PAD
    pw = CW - pl - pr; ph = CH - pt - pb; slot = pw / N
    return (lambda i: pl + slot * i + slot / 2), (lambda p: pt + (ymax - p) / (ymax - ymin) * ph), slot

def line_el(x1, y1, x2, y2, col, w=2.4, dash=None, id=""):
    ln = math.hypot(x2 - x1, y2 - y1)
    d = f' stroke-dasharray="{dash}"' if dash else ''
    i = f' id="{id}"' if id else ''
    return (f'<line{i} data-len="{ln:.0f}" x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{col}" stroke-width="{w}"{d}/>')

def xmark(cx, cy, col=RED, r=16, id="x1"):
    ln = math.hypot(2*r, 2*r)
    return (f'<g id="{id}" opacity="0">'
            f'<line data-len="{ln:.0f}" x1="{cx-r}" y1="{cy-r}" x2="{cx+r}" y2="{cy+r}" stroke="{col}" stroke-width="5" stroke-linecap="round"/>'
            f'<line data-len="{ln:.0f}" x1="{cx-r}" y1="{cy+r}" x2="{cx+r}" y2="{cy-r}" stroke="{col}" stroke-width="5" stroke-linecap="round"/></g>')

def zone_el(id, x0, y0, x1, y1, label_html="", fill=TEAL, stroke=TEAL_D):
    """زون احترافي: الإطار يترسم حول المحيط ثم التعبئة والوسم يتنفسان — mode «zone»."""
    w = abs(x1 - x0); h = abs(y1 - y0); per = 2 * (w + h)
    return (f'<g id="{id}" opacity="0">'
            f'<rect class="zf" x="{min(x0,x1):.1f}" y="{min(y0,y1):.1f}" width="{w:.1f}" height="{h:.1f}" fill="{fill}" opacity="0"/>'
            f'<path class="zb" data-len="{per:.0f}" d="M {x0:.1f} {y0:.1f} H {x1:.1f} V {y1:.1f} H {x0:.1f} Z" '
            f'fill="none" stroke="{stroke}" stroke-width="1.7"/>'
            f'<g class="zl" opacity="0">{label_html}</g></g>')

def ring(id, cx, cy, r=15, col=TEAL_D, label_html=""):
    """دائرة دخول نابضة: تظهر بسلايد ثم حلقة نبض تتوسع — mode «ring»."""
    return (f'<g id="{id}" opacity="0">'
            f'<circle class="r0" cx="{cx:.1f}" cy="{cy:.1f}" r="{r}" fill="none" stroke="{col}" stroke-width="3.2"/>'
            f'<circle class="rp" data-cx="{cx:.1f}" data-cy="{cy:.1f}" data-r="{r}" cx="{cx:.1f}" cy="{cy:.1f}" r="{r}" '
            f'fill="none" stroke="{col}" stroke-width="2" opacity="0"/>'
            f'{label_html}</g>')


def pos_box(id, x0, x1, ye, ys, yt, lbl_e="الدخول", lbl_s="الستوب", lbl_t="الهدف",
            col_t=TEAL_D, col_s=RED, col_e="#ECF3F6", anchor_e="end"):
    """بوكس هدف/ستوب بستايل TradingView: خط دخول يترسم ← الستوب يتمدد لتحت ← الهدف يتمدد لفوق."""
    w = x1 - x0
    ln = w
    return (f'<g id="{id}" opacity="0">'
            f'<rect class="pt" x="{x0:.1f}" y="{yt:.1f}" width="{w:.1f}" height="{ye-yt:.1f}" '
            f'fill="{col_t}" fill-opacity="0.13" stroke="{col_t}" stroke-width="1.4" stroke-opacity="0.85"/>'
            f'<rect class="ps" x="{x0:.1f}" y="{ye:.1f}" width="{w:.1f}" height="{ys-ye:.1f}" '
            f'fill="{col_s}" fill-opacity="0.12" stroke="{col_s}" stroke-width="1.4" stroke-opacity="0.8"/>'
            f'<line class="pe" data-len="{ln:.0f}" x1="{x0:.1f}" y1="{ye:.1f}" x2="{x1:.1f}" y2="{ye:.1f}" '
            f'stroke="{col_e}" stroke-width="2.2"/>'
            f'<g class="pl" opacity="0">'
            + htext((x0+x1)/2, yt + 30, lbl_t, col_t, 22)
            + htext((x0+x1)/2, ys - 22, lbl_s, col_s, 22)
            + htext(x1 - 12, ye - 12, lbl_e, col_e, 21, anchor=anchor_e)
            + '</g></g>')

def checkmark(cx, cy, col=TEAL_D, id="ck1"):
    return (f'<g id="{id}" opacity="0"><circle cx="{cx}" cy="{cy}" r="19" fill="none" stroke="{col}" stroke-width="4"/>'
            f'<polyline points="{cx-9},{cy} {cx-2},{cy+8} {cx+11},{cy-8}" fill="none" stroke="{col}" stroke-width="4.5" '
            f'stroke-linecap="round" stroke-linejoin="round"/></g>')

def candles_svg(W_, x, y, slot):
    bw = slot * 0.6
    out = []
    for i, c in enumerate(W_):
        cx = x(i); up = c["c"] >= c["o"]; col = BULL if up else BEAR
        yh, yl, yo, yc = y(c["h"]), y(c["l"]), y(c["o"]), y(c["c"])
        top, bot = min(yo, yc), max(yo, yc); bh = max(bot - top, 2.6)
        # فتيل .cw يرسم من المنتصف + جسم .cb ينمو باتجاه الإغلاق (صاعد: من تحت، هابط: من فوق)
        out.append(f'<g class="cnd" id="c{i}">'
                   f'<line class="cw" x1="{cx:.1f}" y1="{yh:.1f}" x2="{cx:.1f}" y2="{yl:.1f}" stroke="{col}" stroke-width="2.6"/>'
                   f'<rect class="cb {"up" if up else "dn"}" x="{cx-bw/2:.1f}" y="{top:.1f}" width="{bw:.1f}" height="{bh:.1f}" fill="{col}" rx="1"/></g>')
    return "".join(out)

def build_reel(cfg, out_html):
    """cfg keys:
    w: candles · base: آخر شمعة ثابتة · open_t: [(i,t)] رالي الافتتاح · story: [(i,t)] الريبلاي
    extra_svg: عناصر الماركب (نصوص svg جاهزة بمعرفات) · marks: [[id,a,b,mode]] mode: draw|pop|fade
    fullset/drawset: معرفات العناصر · txt: [(id,a,b,html,fs,color)] · chip/res/cta_k/cta_s
    dur · flash:(a,b) · punch:(a,b,strength) · rflash:(t,) اختياري · kb_end:نسبة كن بيرنز
    """
    W_ = cfg["w"]; N = len(W_)
    x, y, slot = geom(W_)
    _ymin, _ymax = price_scale(W_)
    _pl, _pr, _pt, _pb, _pw, _ph = plot_box()
    dark = bool(cfg.get("dark"))
    svg = [f'<svg viewBox="0 0 {CW} {CH}" width="{CW}" height="{CH}" xmlns="http://www.w3.org/2000/svg">']
    if cfg.get("grid", True):
        for k in range(5):
            gy = 26 + (CH - 46) * k / 4
            svg.append(f'<line x1="16" y1="{gy:.0f}" x2="{CW-20}" y2="{gy:.0f}" stroke="rgba(15,46,60,0.06)" stroke-width="1.5"/>')
    svg.append(cfg.get("pre_svg", ""))       # أثاث المنصة يسبق الشموع فلا يغطيها
    svg.append(candles_svg(W_, x, y, slot))
    # خط السعر الحي (ستايل TradingView) — يتبع إغلاق آخر شمعة مكشوفة
    svg.append(f'<g id="lp" opacity="0"><line id="lpl" x1="16" y1="0" x2="{CW-20}" y2="0" '
               f'stroke="{INK}" stroke-width="1.5" stroke-dasharray="5 5" opacity="0.4"/>'
               f'<circle id="lpd" cx="{CW-20}" cy="0" r="4.5" fill="{INK}"/>'
               + (f'<rect id="lpp" x="{CW-_pr+3}" y="0" width="{_pr-7}" height="30" rx="3" fill="{cfg.get("lp_col", INK)}"/>'
                  f'<text id="lpv" x="{CW-_pr+9}" y="0" fill="{cfg.get("lp_txt", "#08131C")}" '
                  f'font-size="19" font-weight="800" font-family="system-ui,sans-serif">0</text>'
                  if cfg.get("lp_pill") else '') + '</g>')
    svg.append(cfg["extra_svg"])
    svg.append('</svg>')
    CHART = "".join(svg)
    if dark:   # خريطة الثيم الغامق (المرجع §3–4): إعادة تلوين كل عناصر الجارت
        for a, b in [("#F2EEE7", "#08131C"), ("#0F2E3C", "#D8E5EB"), ("#1E627A", "#3AAFC0"),
                     ("#2E7D96", "#43D4DC"), ("#D24B4B", "#E05656"), ("#2E8CA6", "#43D4DC"),
                     ("#122F3E", "#5E7A88"), ("rgba(15,46,60,0.06)", "rgba(255,255,255,0.055)")]:
            CHART = CHART.replace(a, b)
    TXTC = "#ECF3F6" if dark else INK
    SUBC = "#8FA6AF" if dark else "#5C6C73"
    ACC = "#3AAFC0" if dark else TEAL_D
    RESC = "#43D4DC" if dark else TEAL_D
    EDUC = "#7F97A1" if dark else "#93A2A8"
    BGCSS = ("radial-gradient(120% 90% at 50% 0%, #0C2029 0%, #08131C 55%, #04090F 100%)" if dark
             else "radial-gradient(120% 90% at 50% 0%, #F7F3EC 0%, #F2EEE7 55%, #ECE6DB 100%)")
    GRAIN = ('<div id="grain"></div>' if dark else '')
    texts = "".join(f'<div class="hl" id="{i}" style="font-size:{fs}px;color:{(TXTC if (dark and col == INK) else col)}">{t}</div>'
                    for i, a, b, t, fs, col in cfg["txt"])
    fl_a, fl_b = cfg["flash"]; pu_a, pu_b, pu_s = cfg["punch"]
    rf = cfg.get("rflash")
    rflash_js = ""
    if rf:
        rflash_js = (f'const rf=seg(t,{rf-0.05},{rf+0.1}), rf2=seg(t,{rf+0.1},{rf+0.6});'
                     f'$("rflash").style.opacity = rf>0&&rf2<1 ? 0.16*(rf<1?rf:(1-rf2)) : 0;')
    # افتتاحية داكنة V2 (نظام الهويتين): غلاف داكن 0→t ثم Light Sweep يكشف المحتوى الأوف وايت
    intro = cfg.get("intro")
    INTRO_CSS = INTRO_HTML = INTRO_JS = ""
    if intro:
        ti = intro.get("t", 2.5)
        INTRO_CSS = (
            '#intro{position:absolute;inset:0;z-index:5;display:flex;flex-direction:column;'
            'align-items:center;justify-content:center;gap:24px;'
            'background:radial-gradient(120% 90% at 50% 0%, #0C2029 0%, #08131C 55%, #04090F 100%)}'
            '#intro .ig{width:118px} #intro .ig svg{width:118px;height:auto}'
            '#intro .iwm{font-size:25px;font-weight:800;letter-spacing:10px;color:#B8C8CC}'
            '#intro .ieyeb{margin-top:26px;font-size:30px;font-weight:700;color:#43D4DC}'
            '#intro .ihook{font-size:74px;font-weight:900;color:#EDF4F5;text-align:center;'
            'line-height:1.28;padding:0 56px;opacity:0}'
            '#intro .ibar{width:320px;height:3px;'
            'background:linear-gradient(90deg,transparent,#43D4DC,transparent)}'
            '#intro .isub{font-size:33px;font-weight:700;color:#B8C8CC;opacity:0;padding:0 60px;text-align:center}'
            '#isweep{position:absolute;top:0;bottom:0;left:0;width:340px;z-index:6;opacity:0;'
            'pointer-events:none;background:linear-gradient(100deg,transparent 0%,'
            'rgba(255,255,255,0.85) 45%,rgba(67,212,220,0.3) 55%,transparent 100%);'
            'transform:skewX(-12deg)}')
        INTRO_HTML = ('<div id="intro"><div class="ig">' + GEM + '</div>'
                      '<div class="iwm">LIQUIDITY STATE</div>'
                      '<div class="ieyeb">' + intro.get("eyeb", "") + '</div>'
                      '<div class="ihook" id="ihook">' + intro["hook"] + '</div>'
                      '<div class="ibar"></div>'
                      '<div class="isub" id="isub">' + intro.get("sub", "") + '</div></div>'
                      '<div id="isweep"></div>')
        INTRO_JS = (
            'const IT=%.2f;'
            'const iw = seg(t, IT, IT+0.55);'
            'const introEl = $("intro");'
            'if (iw >= 1) introEl.style.display="none";'
            'else { introEl.style.display=""; introEl.style.clipPath = `inset(0 0 0 ${(iw*100).toFixed(2)}%%)`; }'
            'const ihk = oc(seg(t, 0.2, 0.75));'
            '$("ihook").style.opacity = ihk;'
            '$("ihook").style.transform = `translateY(${((1-ihk)*28).toFixed(1)}px)`;'
            '$("isub").style.opacity = oc(seg(t, 0.65, 1.1));'
            'const iswk = seg(t, IT-0.05, IT+0.62);'
            'const isw = $("isweep");'
            'if (iswk>0 && iswk<1) { isw.style.opacity = 0.7*Math.sin(Math.PI*iswk);'
            'isw.style.transform = `translateX(${(-360+1560*iswk).toFixed(0)}px) skewX(-12deg)`; }'
            'else isw.style.opacity=0;') % ti
    html = f'''<!DOCTYPE html><html lang="ar" dir="rtl"><head><meta charset="utf-8"><style>
{FONT_CSS}
*{{margin:0;padding:0;box-sizing:border-box}}
#stage{{width:1080px;height:1920px;position:relative;overflow:hidden;font-family:Tajawal;
  background:{BGCSS}}}
#grain{{position:absolute;inset:0;pointer-events:none;opacity:0.05;mix-blend-mode:overlay;
  background-image:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='220' height='220'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='2'/></filter><rect width='100%25' height='100%25' filter='url(%23n)'/></svg>")}}
.hl{{position:absolute;top:150px;left:40px;right:40px;text-align:center;font-weight:900;
  line-height:1.22;color:{TXTC};opacity:0}}
#chartwrap{{position:absolute;top:430px;left:40px;width:{CW}px;height:{CH}px;transform-origin:0 0}}
.cnd .cw{{transform-box:fill-box;transform-origin:50% 50%}}
.cnd .cb{{transform-box:fill-box}}
.cnd .cb.up{{transform-origin:50% 100%}}
.cnd .cb.dn{{transform-origin:50% 0%}}
.pt{{transform-box:fill-box;transform-origin:50% 100%}}
.ps{{transform-box:fill-box;transform-origin:50% 0%}}
#chip{{position:absolute;top:372px;right:40px;border:2px solid {ACC};color:{ACC};
  font-weight:800;font-size:26px;padding:8px 18px;opacity:0;border-radius:0}}
#res{{position:absolute;top:1290px;left:0;right:0;text-align:center;font-weight:900;
  font-size:52px;color:{RESC};opacity:0}}
#cta{{position:absolute;top:1430px;left:70px;right:70px;text-align:center;opacity:0}}
#cta .k{{display:inline-block;border:2.5px solid {TXTC};color:{TXTC};font-weight:900;font-size:56px;
  padding:14px 44px;border-radius:0}}
#cta .s{{margin-top:16px;font-weight:700;font-size:34px;color:{SUBC}}}
#edu{{position:absolute;bottom:46px;left:0;right:0;text-align:center;font-size:22px;color:{EDUC};font-weight:600}}
#endlogo{{position:absolute;bottom:96px;left:0;right:0;text-align:center;opacity:0}}
#endlogo .eg{{width:74px;margin:0 auto}} #endlogo .eg svg{{width:74px;height:auto}}
#endlogo .ew{{margin-top:8px;font-size:23px;font-weight:800;letter-spacing:9px;color:{SUBC}}}
#flash{{position:absolute;inset:0;background:#fff;opacity:0;pointer-events:none}}
#rflash{{position:absolute;inset:0;background:{RED};opacity:0;pointer-events:none}}
#camrot{{width:100%;height:100%;transform-origin:500px 410px}}
#vig{{position:absolute;top:400px;left:20px;width:1040px;height:880px;pointer-events:none;opacity:0;
  background:radial-gradient(78% 68% at 50% 48%, transparent 52%, rgba(8,19,28,0.34) 100%)}}
#sweep{{position:absolute;top:380px;left:0;width:260px;height:920px;pointer-events:none;opacity:0;
  background:linear-gradient(100deg, transparent 0%, rgba(255,255,255,0.75) 45%, rgba(67,212,220,0.25) 55%, transparent 100%);
  transform:skewX(-14deg)}}
{INTRO_CSS}
{cfg.get('extra_css','')}
</style></head><body><div id="stage">
{cfg.get('extra_html','')}
{texts}
<div id="chip">{cfg["chip"]}</div>
<div id="chartwrap"><div id="camrot">{CHART}</div></div>
<div id="vig"></div>
<div id="sweep"></div>
<div id="res">{cfg["res"]}</div>
<div id="cta"><span class="k">{cfg["cta_k"]}</span><div class="s">{cfg["cta_s"]}</div></div>
<div id="edu">{cfg.get("edu", "لغرض تعليمي — بيانات حقيقية")}</div>
<div id="endlogo"><div class="eg">{GEM}</div><div class="ew">LIQUIDITY STATE</div></div>
<div id="flash"></div><div id="rflash"></div>
{INTRO_HTML}
{GRAIN}
</div>
<script>
window.__DUR = {cfg["dur"]};
const $ = id => document.getElementById(id);
const clamp = (v,a,b) => Math.max(a, Math.min(b, v));
const oc = t => 1 - Math.pow(1-t, 3);
const ob = t => {{ const c1=1.70158, c3=c1+1; return 1 + c3*Math.pow(t-1,3) + c1*Math.pow(t-1,2); }};
function seg(t,a,b){{ return clamp((t-a)/(b-a), 0, 1); }}
const BASE = {cfg["base"]};
const OPEN = {json.dumps(cfg["open_t"])};
const STORY = {json.dumps(cfg["story"])};
const TXTS = {json.dumps([[i, a, b] for i, a, b, _, __, ___ in cfg["txt"]])};
const MARKS = {json.dumps(cfg["marks"])};
const FULLSET = {json.dumps(cfg["fullset"])};
const DRAWSET = {json.dumps(cfg["drawset"])};
const DOM_MARKS = {json.dumps(cfg.get("dom_marks", []))};
const LPP = {json.dumps(bool(cfg.get("lp_pill")))};
const LPD = {cfg.get("lp_dec", 2)};
const YMIN = {_ymin}, YMAX = {_ymax}, PT = {_pt}, PH = {_ph};
const OPENMAX = {cfg.get("openmax", "BASE")};
const YO = {json.dumps([round(y(c["o"]), 1) for c in W_])};
const CDUR = {json.dumps([round(0.4 + 0.18*((i*37)%10)/10, 3) for i in range(N)])};
const YC = {json.dumps([round(y(c["c"]), 1) for c in W_])};
function setLine(el, k){{
  const len = +el.dataset.len || 300;
  el.style.strokeDasharray = el.getAttribute("stroke-dasharray") && k>=1 ? el.getAttribute("stroke-dasharray") : len;
  el.style.strokeDashoffset = len * (1 - k);
  el.style.opacity = k > 0 ? 1 : 0;
}}
const CND = [];
for (let i = 0; i < {N}; i++) {{
  const g = $("c"+i);
  CND.push({{g, w: g.querySelector(".cw"), b: g.querySelector(".cb")}});
}}
// تكشّف احترافي: الفتيل يرسم من المنتصف ← الجسم ينمو باتجاه إغلاقه ← لمعة وصول
function candleK(i, k, fade) {{
  const c = CND[i];
  if (k <= 0) {{ c.g.style.opacity = 0; return; }}
  c.g.style.opacity = fade !== undefined ? fade : 1;
  const kw = Math.min(k / 0.45, 1), kb = clamp((k - 0.25) / 0.75, 0, 1);
  c.w.style.transform = `scaleY(${{(0.1 + 0.9*oc(kw)).toFixed(4)}})`;
  c.b.style.transform = `scaleY(${{(kb >= 1 ? 1 : 0.1 + 0.9*oc(kb)).toFixed(4)}})`;
  c.g.style.filter = k < 1 ? `brightness(${{(1 + 0.42*(1-k)).toFixed(3)}})` : "";
}}
window.__setFrame = function(t) {{
  const P0 = t < {cfg.get("preview_a", 2.05)};
  const TR = seg(t, {cfg.get("preview_a", 2.05) - 0.15}, {cfg.get("preview_b", 2.35)});
  let li = BASE, lk = 1;                       // آخر شمعة مكشوفة (لخط السعر الحي)
  for (let i = 0; i < {N}; i++) {{
    let k = 0;
    if (i <= BASE) k = 1;
    else if (P0 || t < {cfg.get("preview_b", 2.35)}) {{
      const o = OPEN.find(p => p[0] === i);
      if (i <= OPENMAX) k = 1;
      else if (o) k = seg(t, o[1], o[1]+CDUR[i]);
      candleK(i, clamp(k, 0, 1), (i <= BASE) ? 1 : (k > 0 ? 1 - TR : 0));
      if (k > 0 && i > li) {{ li = i; lk = k; }}
      continue;
    }} else {{
      const s = STORY.find(p => p[0] === i);
      if (s) k = seg(t, s[1], s[1]+CDUR[i]);
      if (k > 0 && i > li) {{ li = i; lk = k; }}
    }}
    candleK(i, k);
  }}
  // خط السعر الحي: يمشي من الافتتاح للإغلاق مع تكشف الشمعة
  const ly = YO[li] + (YC[li] - YO[li]) * Math.min(lk * 1.6, 1);
  $("lp").style.opacity = (P0 ? 0.9 : (t < 2.35 ? (1 - TR) * 0.9 : 0.9));
  $("lpl").setAttribute("y1", ly); $("lpl").setAttribute("y2", ly);
  $("lpd").setAttribute("cy", ly);
  if (LPP) {{
    const pv = YMAX - (ly - PT) / PH * (YMAX - YMIN);
    $("lpp").setAttribute("y", ly - 15);
    $("lpv").setAttribute("y", ly + 6);
    $("lpv").textContent = pv.toFixed(LPD);
  }}
  for (const id of FULLSET) {{
    const el = $(id);
    const m = MARKS.find(m => m[0] === id);
    if (P0 || t < {cfg.get("preview_b", 2.35)}) {{
      el.style.opacity = 1 - TR;
      if (m && m[3] === "zone") {{
        setLine(el.querySelector(".zb"), 1);
        el.querySelector(".zf").style.opacity = 0.16;
        const zl = el.querySelector(".zl"); if (zl) zl.style.opacity = 1;
      }}
      if (m && m[3] === "drawx") el.querySelectorAll("line").forEach(l => setLine(l, 1));
      if (m && m[3] === "posbox") {{
        setLine(el.querySelector(".pe"), 1);
        el.querySelector(".ps").style.transform = "scaleY(1)";
        el.querySelector(".pt").style.transform = "scaleY(1)";
        el.querySelector(".pl").style.opacity = 1;
      }}
      if (m && m[3] === "ring") {{ const rp = el.querySelector(".rp"); if (rp) rp.style.opacity = 0; }}
      continue;
    }}
    if (!m) {{ el.style.opacity = 0; continue; }}
    const k = seg(t, m[1], m[2]);
    if (m[3] === "pop") {{
      el.style.opacity = oc(k);
      el.style.transformBox = "fill-box"; el.style.transformOrigin = "50% 50%";
      el.style.transform = `translateY(${{((1-ob(k))*14).toFixed(2)}}px) scale(${{(0.6 + 0.4*ob(k)).toFixed(4)}})`;
    }} else if (m[3] === "zone") {{
      el.style.opacity = k > 0 ? 1 : 0;
      setLine(el.querySelector(".zb"), Math.min(k / 0.6, 1));
      el.querySelector(".zf").style.opacity = clamp((k - 0.5) / 0.5, 0, 1) * 0.16;
      const zl = el.querySelector(".zl"); if (zl) zl.style.opacity = clamp((k - 0.6) / 0.4, 0, 1);
    }} else if (m[3] === "ring") {{
      el.style.opacity = oc(k);
      el.style.transformBox = "fill-box"; el.style.transformOrigin = "50% 50%";
      el.style.transform = `scale(${{(0.5 + 0.5*ob(k)).toFixed(4)}})`;
      const rp = el.querySelector(".rp");
      if (rp) {{
        if (k >= 1) {{
          const ph = ((t - m[2]) % 1.5) / 1.5;
          rp.setAttribute("r", (+rp.dataset.r) * (1 + 0.55 * ph));
          rp.style.opacity = (1 - ph) * 0.55;
        }} else rp.style.opacity = 0;
      }}
    }} else if (m[3] === "posbox") {{
      el.style.opacity = k > 0 ? 1 : 0;
      setLine(el.querySelector(".pe"), Math.min(k / 0.3, 1));
      el.querySelector(".ps").style.transform = `scaleY(${{oc(clamp((k - 0.26) / 0.38, 0, 1)).toFixed(4)}})`;
      el.querySelector(".pt").style.transform = `scaleY(${{oc(clamp((k - 0.48) / 0.52, 0, 1)).toFixed(4)}})`;
      el.querySelector(".pl").style.opacity = clamp((k - 0.78) / 0.22, 0, 1);
    }} else if (m[3] === "drawx") {{
      el.style.opacity = k > 0 ? 1 : 0;
      const ls = el.querySelectorAll("line");
      setLine(ls[0], Math.min(k * 2, 1)); setLine(ls[1], clamp(k * 2 - 1, 0, 1));
    }} else {{
      el.style.opacity = oc(k);
    }}
    // إزالة المنتهي (قاعدة V2): mark[4] = زمن بدء الاختفاء، mark[5] = مدته
    if (m.length > 4 && m[4]) {{
      const ko = seg(t, m[4], m[4] + (m[5] || 0.4));
      if (ko > 0) el.style.opacity = (parseFloat(el.style.opacity) || 0) * (1 - ko);
    }}
  }}
  for (const id of DRAWSET) {{
    const el = $(id);
    if (P0 || t < {cfg.get("preview_b", 2.35)}) {{ setLine(el, 1); el.style.opacity = 1 - TR; continue; }}
    const m = MARKS.find(m => m[0] === id);
    setLine(el, m ? seg(t, m[1], m[2]) : 0);
  }}
  for (const [id, a, b] of TXTS) {{
    const el = $(id);
    const ki = oc(seg(t, a, a+0.45)), ko = seg(t, b, b+0.3);
    el.style.opacity = ki * (1 - ko);
    el.style.clipPath = `inset(0 ${{(1-ki)*100}}% 0 0)`;
    el.style.transform = `translateY(${{(1-ki)*24}}px)`;
  }}
  $("chip").style.opacity = Math.min(oc(seg(t, 0.8, 1.2)), 1);
  // عناصر واجهة خارج الشارت (لافتات المراحل مثلاً): [id, ظهور، اكتمال، اختفاء، مدته]
  for (const m of DOM_MARKS) {{
    const el = $(m[0]); if (!el) continue;
    const ki = oc(seg(t, m[1], m[2]));
    const ko = (m.length > 3 && m[3]) ? seg(t, m[3], m[3] + (m[4] || 0.3)) : 0;
    el.style.opacity = (ki * (1 - ko)).toFixed(3);
    el.style.transform = `translateY(${{((1 - ki) * 10).toFixed(1)}}px)`;
  }}
  const r1 = {"oc(seg(t, 1.25, 1.6)) * (1 - seg(t, 1.9, 2.2))" if cfg.get("res_tease", True) else "0"};
  const r2 = oc(seg(t, {cfg["res_t"]}, {cfg["res_t"]}+0.4));
  $("res").style.opacity = Math.max(r1, r2);
  const ck = oc(seg(t, {cfg["cta_t"]}, {cfg["cta_t"]}+0.45));
  $("cta").style.opacity = ck;
  $("endlogo").style.opacity = oc(seg(t, {cfg["cta_t"]}+0.7, {cfg["cta_t"]}+1.3));
  $("cta").style.transform = `translateY(${{(1-ck)*30}}px)`;
  const f1 = seg(t, {fl_a}, {fl_a}+0.22), f2 = seg(t, {fl_a}+0.22, {fl_b});
  $("flash").style.opacity = f1 > 0 && f2 < 1 ? {cfg.get("flash_op", 0.45)} * (f1 < 1 ? f1 : (1-f2)) : 0;
  {rflash_js}
  const punch = Math.sin(Math.PI * seg(t, {pu_a}, {pu_b})) * {pu_s};
  const shp = seg(t, {fl_a}, {fl_a} + 0.42);
  const shake = shp > 0 && shp < 1 ? Math.sin(shp * 42) * (1 - shp) * 5.5 : 0;
  // كاميرا سينمائية: [t, scale, fx, fy, ease?, rot?] — ease: ss|whip|ramp|anticip|creep
  const CAM = {json.dumps(cfg.get("cam", [[0, 1.03, 0.5, 0.5]]))};
  const EASE = {{
    ss: u => u * u * (3 - 2 * u),
    creep: u => -(Math.cos(Math.PI * u) - 1) / 2,
    whip: u => u >= 1 ? 1 : 1 - Math.pow(2, -10 * u),
    ramp: u => u < 0.5 ? 16 * Math.pow(u, 5) : 1 - Math.pow(-2 * u + 2, 5) / 2,
    anticip: u => {{ const c = 1.70158 * 1.1, c2 = c * 1.525;
      return u < 0.5 ? (Math.pow(2*u, 2) * ((c2 + 1) * 2 * u - c2)) / 2
                     : (Math.pow(2*u - 2, 2) * ((c2 + 1) * (u * 2 - 2) + c2) + 2) / 2; }}
  }};
  function camPose(tt) {{
    let s0 = CAM[0], s1 = CAM[CAM.length - 1];
    for (let i = 0; i < CAM.length - 1; i++)
      if (tt >= CAM[i][0] && tt <= CAM[i + 1][0]) {{ s0 = CAM[i]; s1 = CAM[i + 1]; break; }}
    if (tt <= CAM[0][0]) s1 = s0 = CAM[0];
    if (tt >= CAM[CAM.length - 1][0]) s0 = s1 = CAM[CAM.length - 1];
    const ez = EASE[s1[4] || "ss"] || EASE.ss;
    const u = s1[0] > s0[0] ? ez(seg(tt, s0[0], s1[0])) : 0;
    return {{ cs: s0[1] + (s1[1] - s0[1]) * u,
             fx: s0[2] + (s1[2] - s0[2]) * u,
             fy: s0[3] + (s1[3] - s0[3]) * u,
             rz: (s0[5] || 0) + ((s1[5] || 0) - (s0[5] || 0)) * u }};
  }}
  const pNow = camPose(t), pPrev = camPose(Math.max(0, t - 0.033));
  // اهتزاز هاند-هيلد ميكروسكوبي مستمر (حياة سينمائية بالثبات)
  let cs = pNow.cs * (1 + 0.0028 * Math.sin(t * 0.62)) + punch;
  let fx = pNow.fx + 0.0021 * Math.sin(t * 0.9 + 1.3) + 0.0011 * Math.sin(t * 2.3);
  let fy = pNow.fy + 0.0017 * Math.cos(t * 0.8) + 0.0009 * Math.sin(t * 1.7 + 0.5);
  const lim = cs > 1 ? (cs - 1) / (2 * cs) : 0;    // ما نطلع برا حدود الجارت
  fx = Math.max(0.5 - lim, Math.min(0.5 + lim, fx));
  fy = Math.max(0.5 - lim, Math.min(0.5 + lim, fy));
  const CWp = {CW}, CHp = {CH};
  const tx = CWp / 2 - cs * fx * CWp + shake;
  const ty = CHp / 2 - cs * fy * CHp + shake * 0.6;
  const wrap = $("chartwrap");
  wrap.style.transform = `translate(${{tx.toFixed(1)}}px, ${{ty.toFixed(1)}}px) scale(${{cs.toFixed(4)}})`;
  // دوران دَتش + موشن بلير يتبع سرعة الكاميرا
  const camSpeed = Math.abs(pNow.cs - pPrev.cs) * 130 + (Math.abs(pNow.fx - pPrev.fx) + Math.abs(pNow.fy - pPrev.fy)) * 380;
  const mblur = clamp(camSpeed - 0.22, 0, 3.0);
  const rot = $("camrot");
  rot.style.transform = pNow.rz ? `rotate(${{pNow.rz.toFixed(3)}}deg)` : "";
  rot.style.filter = mblur > 0.25 ? `blur(${{mblur.toFixed(2)}}px)` : "";
  // فينيت يتنفس مع الزوم + ضربة ضوء تكنس الشاشة بالذروة
  $("vig").style.opacity = clamp(0.10 + (cs - 1) * 0.17 + (shp > 0 && shp < 1 ? 0.08 : 0), 0, 0.36);
  const swk = seg(t, {fl_a} - 0.08, {fl_a} + 0.5);
  const sw = $("sweep");
  if (swk > 0 && swk < 1) {{
    sw.style.opacity = {cfg.get("sweep_op", 0.55)} * Math.sin(Math.PI * swk);
    sw.style.transform = `translateX(${{(-320 + 1500 * swk).toFixed(0)}}px) skewX(-14deg)`;
  }} else sw.style.opacity = 0;
  if (t > {cfg["cta_t"]} + 0.6) {{
    const pulse = 1 + 0.028 * Math.sin(2 * Math.PI * (t - {cfg["cta_t"]}) * 0.8);
    $("cta").style.transform = `translateY(0px) scale(${{pulse.toFixed(4)}})`;
  }}
  {INTRO_JS}
}};
window.__setFrame(0);
</script></body></html>'''
    with open(os.path.join(HERE, out_html), "w", encoding="utf-8") as f:
        f.write(html)
    return len(html)
