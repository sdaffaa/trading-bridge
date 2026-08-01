# -*- coding: utf-8 -*-
# ريل «ليش الأوردر بلوك يطق ستوبك؟» — 20.5s، هندسة سكب ريت تحت 30%
# جارت واحد حقيقي (الذهب M15، نافذة شيت النماذج 1) بريبلاي حي ووسوم تتراكم.
import json, os, math
from reel_build import (CREAM, INK, TEAL, TEAL_D, TEAL_L, BULL, BEAR, RED, MUTE,
                        FONT_CSS, htext, hend, GEM)

HERE = os.path.dirname(os.path.abspath(__file__))
ROW = next(r for r in json.load(open(os.path.join(HERE, "sheet_real.json"))) if r["cls"] == "sweep")
W_ = ROW["w"]; N = len(W_)                     # 31 real gold M15 candles
iH, BK, IOB, IR = ROW["iH"], ROW["bk"], ROW["iob"], ROW["ir"]
I1, I2, IPDL = ROW["i1"], ROW["i2"], ROW["ipdl"]
EQ = W_[I1]["h"]; PDL = W_[IPDL]["l"]
ZTOP = W_[IOB]["o"]; ZBOT = W_[IOB]["l"]; LV = W_[iH]["h"]
PIPS = int(round((max(c["h"] for c in W_[IR+1:]) - W_[IR]["l"]) / 0.1))  # gold: 0.1$ per point

# ---------- chart geometry (1000x820) ----------
CW, CH = 1000, 820
ymin = min(c["l"] for c in W_); ymax = max(c["h"] for c in W_)
pad = (ymax - ymin) * 0.08; ymin -= pad * 1.7; ymax += pad
pl, pr, pt, pb = 16, 20, 26, 20
pw = CW - pl - pr; ph = CH - pt - pb; slot = pw / N; bw = slot * 0.6
def x(i): return pl + slot * i + slot / 2
def y(p): return pt + (ymax - p) / (ymax - ymin) * ph

def L(x1, y1, x2, y2, col, w=2.0, dash=None, id=""):
    ln = math.hypot(x2 - x1, y2 - y1)
    d = f' stroke-dasharray="{dash}"' if dash else ''
    i = f' id="{id}"' if id else ''
    return (f'<line{i} data-len="{ln:.0f}" x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{col}" stroke-width="{w}"{d}/>'), ln

svg = [f'<svg viewBox="0 0 {CW} {CH}" width="{CW}" height="{CH}" xmlns="http://www.w3.org/2000/svg">']
for k in range(5):
    gy = pt + ph * k / 4
    svg.append(f'<line x1="{pl}" y1="{gy:.0f}" x2="{CW-pr}" y2="{gy:.0f}" stroke="rgba(15,46,60,0.06)" stroke-width="1.5"/>')
# zone (draws at ~4.9s)
zx0 = x(IOB) - slot*0.5; zx1 = x(min(IR+3, N-1)) + slot*0.5
svg.append(f'<g id="zone" opacity="0"><rect x="{zx0:.1f}" y="{y(ZTOP):.1f}" width="{zx1-zx0:.1f}" height="{y(ZBOT)-y(ZTOP):.1f}" fill="{TEAL}" style="opacity:0.16"/>'
           f'<rect x="{zx0:.1f}" y="{y(ZTOP):.1f}" width="{zx1-zx0:.1f}" height="{y(ZBOT)-y(ZTOP):.1f}" fill="none" stroke="{TEAL_D}" stroke-width="1.6"/>'
           + htext((zx0+zx1)/2, y(ZBOT)+30, "زون الطلب", TEAL_D, 24) + '</g>')
# candles, one group each
for i, c in enumerate(W_):
    cx = x(i); up = c["c"] >= c["o"]; col = BULL if up else BEAR
    yh, yl, yo, yc = y(c["h"]), y(c["l"]), y(c["o"]), y(c["c"])
    top, bot = min(yo, yc), max(yo, yc); bh = max(bot - top, 2.6)
    svg.append(f'<g class="cnd" id="c{i}"><line x1="{cx:.1f}" y1="{yh:.1f}" x2="{cx:.1f}" y2="{yl:.1f}" stroke="{col}" stroke-width="2.6"/>'
               f'<rect x="{cx-bw/2:.1f}" y="{top:.1f}" width="{bw:.1f}" height="{bh:.1f}" fill="{col}" rx="1"/></g>')
# BOS: swing high -> break candle only
bos, bosln = L(x(iH), y(LV), x(BK)+slot*0.55, y(LV), INK, 2.4, id="bosline")
svg.append(bos)
svg.append(f'<g id="boslbl" opacity="0">{hend(x(BK)+slot*0.55, y(LV), INK)}{htext(x(iH)+slot*1.6, y(LV)-14, "BOS", INK, 24)}</g>')
# naive early entry (above the zone, at candle 16 close) + its stop
NE = 16; nep = W_[NE]["c"]
svg.append(f'<g id="nentry" opacity="0">'
           f'<circle cx="{x(NE):.1f}" cy="{y(nep):.1f}" r="13" fill="none" stroke="{TEAL_D}" stroke-width="3"/>'
           f'<line x1="{x(NE)-14:.1f}" y1="{y(nep):.1f}" x2="{x(11.6)+8:.1f}" y2="{y(nep)-16:.1f}" stroke="{TEAL_D}" stroke-width="1.6"/>'
           + htext(x(11.5), y(nep)-24, "دخول مستعجل", TEAL_D, 24, "end") + '</g>')
px22 = 22 * (ymax - ymin) / ph                 # ~22px in price units, keeps the stop clear of PDL
nsp = W_[IPDL]["l"] - px22
XI = next(i for i in range(I2 + 1, IR + 1) if W_[i]["l"] <= nsp)   # the real stop-hit candle
nst, _ = L(x(NE-2), y(nsp), x(XI)+slot*0.6, y(nsp), RED, 2.0, dash="8 7", id="nstop")
svg.append(nst)
svg.append(f'<g id="nstoplbl" opacity="0">{htext(x(19), y(nsp)+28, "ستوب", RED, 22)}</g>')
# stop-hit X on the actual crossing candle
svg.append(f'<g id="xhit" opacity="0">'
           f'<line x1="{x(XI)-16:.1f}" y1="{y(nsp)-16:.1f}" x2="{x(XI)+16:.1f}" y2="{y(nsp)+16:.1f}" stroke="{RED}" stroke-width="5" stroke-linecap="round"/>'
           f'<line x1="{x(XI)-16:.1f}" y1="{y(nsp)+16:.1f}" x2="{x(XI)+16:.1f}" y2="{y(nsp)-16:.1f}" stroke="{RED}" stroke-width="5" stroke-linecap="round"/></g>')
# liquidity sweep line + PDL
swp, swpln = L(x(I1)-slot*0.6, y(EQ), x(I2)+slot*0.55, y(EQ), RED, 2.4, id="sweepline")
svg.append(swp)
svg.append(f'<g id="sweeplbl" opacity="0">{htext(x((I1+I2)/2), y(max(EQ, W_[I2]["h"]))-20, "سيولة القمم", RED, 26)}</g>')
pdl, _ = L(x(IPDL)-slot*1.6, y(PDL), x(IPDL)+slot*1.6, y(PDL), INK, 2.0, dash="7 6", id="pdlline")
svg.append(pdl)
svg.append(f'<g id="pdllbl" opacity="0">{htext(x(IPDL)+slot*1.1, y(PDL)-12, "PDL", INK, 22)}</g>')
# real retest entry
svg.append(f'<g id="circ" opacity="0"><circle cx="{x(IR):.1f}" cy="{y(W_[IR]["l"]):.1f}" r="17" fill="none" stroke="{RED}" stroke-width="3.4"/></g>')
svg.append(f'<g id="entlbl" opacity="0">{htext(x(IR), y(ZBOT)+30, "الدخلة الصح", TEAL_D, 26)}</g>')
svg.append('</svg>')
CHART = "".join(svg)

# the real data: the plunge candle that hits the naive stop IS the retest candle (XI == IR).
# story order: BOS -> tops -> naive entry -> TURN (sweep revealed) -> drop -> one candle
# hits the stop AND taps the zone -> the correct entry -> rally.
open_t = [(27, 0.15), (28, 0.45), (29, 0.75), (30, 1.05)]
story = [(13, 2.45), (14, 3.1), (15, 3.5), (16, 3.9), (17, 5.4), (18, 5.8),
         (19, 6.4), (20, 6.7), (21, 7.0)]
tt = 9.8
for i in range(22, IR):
    story.append((i, round(tt, 2))); tt += 0.35
story += [(IR, 11.85), (27, 15.5), (28, 15.9), (29, 16.3), (30, 16.7)]
XHIT_T = 12.1

TXT = [
    ("t1", 0.35, 1.9,  "ليش الأوردر بلوك<br>يطق ستوبك؟", 64, INK),
    ("t2", 2.30, 3.9,  "نفس الزون… نتيجتين", 58, INK),
    ("t3", 4.00, 4.9,  "شلون؟ تعال اقولك", 58, INK),
    ("t4", 5.00, 7.2,  "يدخلون على طول", 58, INK),
    ("t5", 7.45, 9.4,  "السوق يسحب السيولة أول", 56, INK),
    ("t6", 9.60, 11.5, "بعدين يرد للزون", 58, INK),
    ("t7", 12.10, 13.3, "انطق الستوب", 58, RED),
    ("t7b", 13.60, 15.1, "ونفس الشمعة… الدخلة الصح", 52, INK),
    ("t8", 15.40, 17.8, "الدخلة المستعجلة<br>اهي اللي تطق ستوبك", 54, INK),
]
texts = "".join(
    f'<div class="hl" id="{i}" style="font-size:{fs}px;color:{col}">{t}</div>'
    for i, a, b, t, fs, col in TXT)

html = f'''<!DOCTYPE html><html lang="ar" dir="rtl"><head><meta charset="utf-8"><style>
{FONT_CSS}
*{{margin:0;padding:0;box-sizing:border-box}}
#stage{{width:1080px;height:1920px;position:relative;overflow:hidden;font-family:Tajawal;
  background:radial-gradient(120% 90% at 50% 0%, #F7F3EC 0%, #F2EEE7 55%, #ECE6DB 100%)}}
.hl{{position:absolute;top:150px;left:40px;right:40px;text-align:center;font-weight:900;
  line-height:1.22;color:{INK};opacity:0}}
#chartwrap{{position:absolute;top:430px;left:40px;width:1000px;height:820px}}
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
<div id="chip">الذهب · 15 دقيقة</div>
<div id="chartwrap">{CHART}</div>
<div id="res">‎+{PIPS} نقطة من الزون</div>
<div id="cta"><span class="k">اكتب «ريتيست»</span><div class="s">يوصلك شيت أشكال الرجعة الثلاثة</div></div>
<div id="edu">لغرض تعليمي — بيانات حقيقية</div>
<div id="flash"></div><div id="rflash"></div>
</div>
<script>
window.__DUR = 20.5;
const $ = id => document.getElementById(id);
const clamp = (v,a,b) => Math.max(a, Math.min(b, v));
const oc = t => 1 - Math.pow(1-t, 3);                     // ease-out cubic
const ob = t => {{ const c1=1.70158, c3=c1+1; return 1 + c3*Math.pow(t-1,3) + c1*Math.pow(t-1,2); }}; // back
function seg(t,a,b){{ return clamp((t-a)/(b-a), 0, 1); }}
const CANDS = {json.dumps({str(i): 0 for i in range(N)})};
const OPEN = {json.dumps(open_t)};
const STORY = {json.dumps(story)};
const TXTS = {json.dumps([[i, a, b] for i, a, b, _, __, ___ in TXT])};
const MARKS = [
  ["bosline", 2.55, 3.05, "draw"], ["boslbl", 2.95, 3.25, "pop"],
  ["zone", 4.55, 5.05, "fade"],
  ["nentry", 5.60, 5.95, "pop"], ["nstop", 6.00, 6.35, "draw"], ["nstoplbl", 6.30, 6.55, "pop"],
  ["sweepline", 7.60, 8.30, "draw"], ["sweeplbl", 8.30, 8.60, "pop"],
  ["pdlline", 8.80, 9.20, "draw"], ["pdllbl", 9.15, 9.40, "pop"],
  ["xhit", {XHIT_T}, {XHIT_T} + 0.3, "pop"],
  ["circ", 13.70, 14.00, "pop"], ["entlbl", 14.00, 14.30, "pop"],
];
// elements hidden during the story replay, visible in the opening + ending
const FULLSET = ["zone","boslbl","nentry","nstoplbl","xhit","sweeplbl","pdllbl","circ","entlbl"];
const DRAWSET = ["bosline","nstop","sweepline","pdlline"];
function setLine(el, k){{                    // k: 0..1 drawn fraction
  const len = +el.dataset.len || 300;
  el.style.strokeDasharray = el.getAttribute("stroke-dasharray") && k>=1 ? el.getAttribute("stroke-dasharray") : len;
  el.style.strokeDashoffset = len * (1 - k);
  el.style.opacity = k > 0 ? 1 : 0;
}}
window.__setFrame = function(t) {{
  const P0 = t < 2.05;                       // opening (full chart, rally printing)
  const TR = seg(t, 1.9, 2.35);              // transition fade of story elements
  // candles
  for (let i = 0; i < {N}; i++) {{
    const el = $("c"+i); let k = 0;
    if (i <= 12) k = 1;
    else if (P0 || t < 2.35) {{
      const o = OPEN.find(p => p[0] === i);
      if (i <= 26) k = 1;
      else if (o) k = seg(t, o[1], o[1]+0.5);
      if (!P0) k = k * (1 - TR);             // fade out during transition
      el.style.opacity = (i <= 12) ? 1 : (1 - TR);
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
  // markup: opening shows everything; story reveals per MARKS
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
  // headline texts: clip-wipe in, fade out
  for (const [id, a, b] of TXTS) {{
    const el = $(id);
    const ki = oc(seg(t, a, a+0.45)), ko = seg(t, b, b+0.3);
    el.style.opacity = ki * (1 - ko);
    el.style.clipPath = `inset(0 ${{(1-ki)*100}}% 0 0)`;
    el.style.transform = `translateY(${{(1-ki)*24}}px)`;
  }}
  // chips / result / CTA
  $("chip").style.opacity = Math.min(oc(seg(t, 0.8, 1.2)), 1);
  const r1 = oc(seg(t, 1.25, 1.6)) * (1 - seg(t, 1.9, 2.2));
  const r2 = oc(seg(t, 17.4, 17.8));
  $("res").style.opacity = Math.max(r1, r2);
  const ck = oc(seg(t, 18.0, 18.45));
  $("cta").style.opacity = ck;
  $("cta").style.transform = `translateY(${{(1-ck)*30}}px)`;
  // flashes + zoom punch
  const f1 = seg(t, 15.5, 15.72), f2 = seg(t, 15.72, 16.35);
  $("flash").style.opacity = f1 > 0 && f2 < 1 ? 0.45 * (f1 < 1 ? f1 : (1-f2)) : 0;
  const rf = seg(t, {XHIT_T-0.05}, {XHIT_T+0.1}), rf2 = seg(t, {XHIT_T+0.1}, {XHIT_T+0.6});
  $("rflash").style.opacity = rf > 0 && rf2 < 1 ? 0.16 * (rf < 1 ? rf : (1-rf2)) : 0;
  const punch = Math.sin(Math.PI * seg(t, 15.5, 16.7)) * 0.055;
  const kb = 1.008 + 0.02 * (t / 20.5);
  const wrap = $("chartwrap");
  wrap.style.transform = `scale(${{kb + punch}})`;
  wrap.style.transformOrigin = punch > 0 ? "72% 40%" : "50% 46%";
}};
window.__setFrame(0);
</script></body></html>'''

open(os.path.join(HERE, "reel_sheet.html"), "w").write(html)
print("wrote reel_sheet.html", len(html), "bytes | DUR=20.5s | candles", N, "| PIPS", PIPS)
