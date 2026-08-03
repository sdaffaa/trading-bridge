# -*- coding: utf-8 -*-
# قالب ريل المؤثرات (§12 — بدون كلام): جارت حقيقي واحد بريبلاي حي + بيتات نصية + ذروة فلاش/زوم
# مشتق من reel_sheet_build.py وصار بارامتري: build_reel(cfg) يكتب HTML جاهز للرندر.
import json, math, os
from reel_build import INK, TEAL, TEAL_D, RED, BULL, BEAR, FONT_CSS, htext, hend

HERE = os.path.dirname(os.path.abspath(__file__))
CW, CH = 1000, 820

def geom(W_):
    N = len(W_)
    ymin = min(c["l"] for c in W_); ymax = max(c["h"] for c in W_)
    pad = (ymax - ymin) * 0.08; ymin -= pad * 1.7; ymax += pad
    pl, pr, pt, pb = 16, 20, 26, 20
    pw = CW - pl - pr; ph = CH - pt - pb; slot = pw / N
    return (lambda i: pl + slot * i + slot / 2), (lambda p: pt + (ymax - p) / (ymax - ymin) * ph), slot

def line_el(x1, y1, x2, y2, col, w=2.4, dash=None, id=""):
    ln = math.hypot(x2 - x1, y2 - y1)
    d = f' stroke-dasharray="{dash}"' if dash else ''
    i = f' id="{id}"' if id else ''
    return (f'<line{i} data-len="{ln:.0f}" x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{col}" stroke-width="{w}"{d}/>')

def xmark(cx, cy, col=RED, r=16, id="x1"):
    return (f'<g id="{id}" opacity="0">'
            f'<line x1="{cx-r}" y1="{cy-r}" x2="{cx+r}" y2="{cy+r}" stroke="{col}" stroke-width="5" stroke-linecap="round"/>'
            f'<line x1="{cx-r}" y1="{cy+r}" x2="{cx+r}" y2="{cy-r}" stroke="{col}" stroke-width="5" stroke-linecap="round"/></g>')

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
        out.append(f'<g class="cnd" id="c{i}"><line x1="{cx:.1f}" y1="{yh:.1f}" x2="{cx:.1f}" y2="{yl:.1f}" stroke="{col}" stroke-width="2.6"/>'
                   f'<rect x="{cx-bw/2:.1f}" y="{top:.1f}" width="{bw:.1f}" height="{bh:.1f}" fill="{col}" rx="1"/></g>')
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
    svg = [f'<svg viewBox="0 0 {CW} {CH}" width="{CW}" height="{CH}" xmlns="http://www.w3.org/2000/svg">']
    for k in range(5):
        gy = 26 + (CH - 46) * k / 4
        svg.append(f'<line x1="16" y1="{gy:.0f}" x2="{CW-20}" y2="{gy:.0f}" stroke="rgba(15,46,60,0.06)" stroke-width="1.5"/>')
    svg.append(candles_svg(W_, x, y, slot))
    svg.append(cfg["extra_svg"])
    svg.append('</svg>')
    CHART = "".join(svg)
    texts = "".join(f'<div class="hl" id="{i}" style="font-size:{fs}px;color:{col}">{t}</div>'
                    for i, a, b, t, fs, col in cfg["txt"])
    fl_a, fl_b = cfg["flash"]; pu_a, pu_b, pu_s = cfg["punch"]
    rf = cfg.get("rflash")
    rflash_js = ""
    if rf:
        rflash_js = (f'const rf=seg(t,{rf-0.05},{rf+0.1}), rf2=seg(t,{rf+0.1},{rf+0.6});'
                     f'$("rflash").style.opacity = rf>0&&rf2<1 ? 0.16*(rf<1?rf:(1-rf2)) : 0;')
    html = f'''<!DOCTYPE html><html lang="ar" dir="rtl"><head><meta charset="utf-8"><style>
{FONT_CSS}
*{{margin:0;padding:0;box-sizing:border-box}}
#stage{{width:1080px;height:1920px;position:relative;overflow:hidden;font-family:Tajawal;
  background:radial-gradient(120% 90% at 50% 0%, #F7F3EC 0%, #F2EEE7 55%, #ECE6DB 100%)}}
.hl{{position:absolute;top:150px;left:40px;right:40px;text-align:center;font-weight:900;
  line-height:1.22;color:{INK};opacity:0}}
#chartwrap{{position:absolute;top:430px;left:40px;width:1000px;height:820px;transform-origin:0 0}}
.cnd{{transform-box:fill-box;transform-origin:50% 100%}}
#chip{{position:absolute;top:372px;right:40px;border:2px solid {TEAL_D};color:{TEAL_D};
  font-weight:800;font-size:26px;padding:8px 18px;opacity:0;border-radius:0}}
#res{{position:absolute;top:1290px;left:0;right:0;text-align:center;font-weight:900;
  font-size:52px;color:{TEAL_D};opacity:0}}
#cta{{position:absolute;top:1430px;left:70px;right:70px;text-align:center;opacity:0}}
#cta .k{{display:inline-block;border:2.5px solid {INK};color:{INK};font-weight:900;font-size:56px;
  padding:14px 44px;border-radius:0}}
#cta .s{{margin-top:16px;font-weight:700;font-size:34px;color:#5C6C73}}
#edu{{position:absolute;bottom:46px;left:0;right:0;text-align:center;font-size:22px;color:#93A2A8;font-weight:600}}
#flash{{position:absolute;inset:0;background:#fff;opacity:0;pointer-events:none}}
#rflash{{position:absolute;inset:0;background:{RED};opacity:0;pointer-events:none}}
</style></head><body><div id="stage">
{texts}
<div id="chip">{cfg["chip"]}</div>
<div id="chartwrap">{CHART}</div>
<div id="res">{cfg["res"]}</div>
<div id="cta"><span class="k">{cfg["cta_k"]}</span><div class="s">{cfg["cta_s"]}</div></div>
<div id="edu">{cfg.get("edu", "لغرض تعليمي — بيانات حقيقية")}</div>
<div id="flash"></div><div id="rflash"></div>
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
const OPENMAX = {cfg.get("openmax", "BASE")};
function setLine(el, k){{
  const len = +el.dataset.len || 300;
  el.style.strokeDasharray = el.getAttribute("stroke-dasharray") && k>=1 ? el.getAttribute("stroke-dasharray") : len;
  el.style.strokeDashoffset = len * (1 - k);
  el.style.opacity = k > 0 ? 1 : 0;
}}
window.__setFrame = function(t) {{
  const P0 = t < 2.05;
  const TR = seg(t, 1.9, 2.35);
  for (let i = 0; i < {N}; i++) {{
    const el = $("c"+i); let k = 0;
    if (i <= BASE) k = 1;
    else if (P0 || t < 2.35) {{
      const o = OPEN.find(p => p[0] === i);
      if (i <= OPENMAX) k = 1;
      else if (o) k = seg(t, o[1], o[1]+0.5);
      if (!P0) k = k * (1 - TR);
      el.style.opacity = (i <= BASE) ? 1 : (1 - TR);
      el.style.transform = `scaleY(${{0.25 + 0.75*ob(clamp(k,0,1)) || 0.25}})`;
      if (k <= 0) el.style.opacity = 0;
      continue;
    }} else {{
      const s = STORY.find(p => p[0] === i);
      if (s) k = seg(t, s[1], s[1]+0.5);
    }}
    el.style.opacity = k > 0 ? 1 : 0;
    el.style.transform = `scaleY(${{k >= 1 ? 1 : 0.25 + 0.75*ob(k)}})`;
  }}
  for (const id of FULLSET) {{
    const el = $(id);
    if (P0 || t < 2.35) {{ el.style.opacity = 1 - TR; continue; }}
    const m = MARKS.find(m => m[0] === id);
    el.style.opacity = m ? oc(seg(t, m[1], m[2])) : 0;
    if (m && m[3] === "pop") {{
      const k = seg(t, m[1], m[2]);
      el.style.transform = `scale(${{0.4 + 0.6*ob(k)}})`;
      el.style.transformBox = "fill-box"; el.style.transformOrigin = "50% 50%";
    }}
  }}
  for (const id of DRAWSET) {{
    const el = $(id);
    if (P0 || t < 2.35) {{ setLine(el, 1); el.style.opacity = 1 - TR; continue; }}
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
  const r1 = oc(seg(t, 1.25, 1.6)) * (1 - seg(t, 1.9, 2.2));
  const r2 = oc(seg(t, {cfg["res_t"]}, {cfg["res_t"]}+0.4));
  $("res").style.opacity = Math.max(r1, r2);
  const ck = oc(seg(t, {cfg["cta_t"]}, {cfg["cta_t"]}+0.45));
  $("cta").style.opacity = ck;
  $("cta").style.transform = `translateY(${{(1-ck)*30}}px)`;
  const f1 = seg(t, {fl_a}, {fl_a}+0.22), f2 = seg(t, {fl_a}+0.22, {fl_b});
  $("flash").style.opacity = f1 > 0 && f2 < 1 ? 0.45 * (f1 < 1 ? f1 : (1-f2)) : 0;
  {rflash_js}
  const punch = Math.sin(Math.PI * seg(t, {pu_a}, {pu_b})) * {pu_s};
  const shp = seg(t, {fl_a}, {fl_a} + 0.42);
  const shake = shp > 0 && shp < 1 ? Math.sin(shp * 42) * (1 - shp) * 5.5 : 0;
  // كاميرا كيفريمات: [t, scale, fx, fy] — fx/fy نقطة التركيز بنسب الجارت
  const CAM = {json.dumps(cfg.get("cam", [[0, 1.03, 0.5, 0.5]]))};
  const ss = u => u * u * (3 - 2 * u);          // smoothstep
  let s0 = CAM[0], s1 = CAM[CAM.length - 1];
  for (let i = 0; i < CAM.length - 1; i++)
    if (t >= CAM[i][0] && t <= CAM[i + 1][0]) {{ s0 = CAM[i]; s1 = CAM[i + 1]; break; }}
  if (t <= CAM[0][0]) s1 = s0 = CAM[0];
  if (t >= CAM[CAM.length - 1][0]) s0 = s1 = CAM[CAM.length - 1];
  const u = s1[0] > s0[0] ? ss(seg(t, s0[0], s1[0])) : 0;
  const cs = (s0[1] + (s1[1] - s0[1]) * u) + punch;
  let fx = s0[2] + (s1[2] - s0[2]) * u;
  let fy = s0[3] + (s1[3] - s0[3]) * u;
  const lim = cs > 1 ? (cs - 1) / (2 * cs) : 0;    // ما نطلع برا حدود الجارت
  fx = clamp(fx, 0.5 - lim, 0.5 + lim) * 0 + Math.max(0.5 - lim, Math.min(0.5 + lim, fx));
  fy = Math.max(0.5 - lim, Math.min(0.5 + lim, fy));
  const CWp = 1000, CHp = 820;
  const tx = CWp / 2 - cs * fx * CWp + shake;
  const ty = CHp / 2 - cs * fy * CHp + shake * 0.6;
  const wrap = $("chartwrap");
  wrap.style.transform = `translate(${{tx.toFixed(1)}}px, ${{ty.toFixed(1)}}px) scale(${{cs.toFixed(4)}})`;
  if (t > {cfg["cta_t"]} + 0.6) {{
    const pulse = 1 + 0.028 * Math.sin(2 * Math.PI * (t - {cfg["cta_t"]}) * 0.8);
    $("cta").style.transform = `translateY(0px) scale(${{pulse.toFixed(4)}})`;
  }}
}};
window.__setFrame(0);
</script></body></html>'''
    with open(os.path.join(HERE, out_html), "w", encoding="utf-8") as f:
        f.write(html)
    return len(html)
