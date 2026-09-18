# -*- coding: utf-8 -*-
"""ريل «بركة السيولة المزدوجة» — نافذة حقيقية، مؤثرات فقط (§12).

النافذة: الدولار/ين · ساعة · 2026-01-09 (فهرس ٢٧ في `sheet_candidates`).
القصّة كلها مشتقّة من الشموع نفسها لا مفروضة عليها:
  · بركة تحت: قاعان متساويان عند الشمعتين ٢ و٦ (فرق 0.008).
  · بركة فوق: قمتان متساويتان عند الشمعتين ١٧ و٢٧ (فرق 0.012).
  · بعد تكوّن الاثنتين أخذ السعر **العليا** عند الشمعة ٢٨ ولم يلمس السفلى.
الأرقام تُقرأ من الشموع عند البناء، فإن تغيّرت النافذة تغيّرت معها أو سقط
البناء — ولا يُكتب رقمٌ باليد.

    python3 run44_reel.py            # يكتب reel44_barkatain.html
"""
import json, math, os

from reel_build import (CREAM, INK, TEAL, TEAL_D, BULL, BEAR, RED, FONT_CSS, htext, GEM)
import run31_charts as RC

HERE = os.path.dirname(os.path.abspath(__file__))
IDX, SLUG, DUR = 27, "barkatain", 22.2
R = RC.win(IDX); W = R["w"]; N = len(W)
NAME = {"USDJPY=X": "الدولار/ين", "GBPUSD=X": "الجنيه/الدولار"}.get(R["sym"], R["sym"])
TF = {"1h": "ساعة", "30m": "٣٠ دقيقة", "15m": "١٥ دقيقة"}.get(R["tf"], R["tf"])

# ── البركتان تُستخرجان بالقياس لا بالكتابة ──
TOL = (max(c["h"] for c in W) - min(c["l"] for c in W)) * 0.05


def _pair(idxs, key, want_close):
    best = None
    for a in range(len(idxs)):
        for b in range(a + 1, len(idxs)):
            i, j = idxs[a], idxs[b]
            if abs(j - i) < 3:
                continue
            d = abs(W[i][key] - W[j][key])
            if d <= TOL and (best is None or d < best[2]):
                best = (i, j, d)
    return best


HI = sorted(range(N), key=lambda i: -W[i]["h"])[:6]
LO = sorted(range(N), key=lambda i: W[i]["l"])[:6]
PH, PL = _pair(HI, "h", True), _pair(LO, "l", True)
assert PH and PL, "النافذة لا تحمل بركتين — لا يُبنى الريل عليها"
H1, H2 = sorted(PH[:2]); L1, L2 = sorted(PL[:2])
LVH = min(W[H1]["h"], W[H2]["h"])          # مستوى البركة العليا
LVL = max(W[L1]["l"], W[L2]["l"])          # مستوى البركة السفلى
TAKEN = next((j for j in range(H2 + 1, N) if W[j]["h"] > max(W[H1]["h"], W[H2]["h"])), None)
BROKEN = next((j for j in range(H2 + 1, N) if W[j]["l"] < min(W[L1]["l"], W[L2]["l"])), None)
assert TAKEN is not None and BROKEN is None, "البركة المأخوذة ليست العليا — تُعاد كتابة القصّة"
TOP = max(W[j]["h"] for j in range(TAKEN, N))
PIP = 0.01 if "JPY" in R["sym"] else 0.0001
GAIN = int(round((TOP - LVH) / PIP))

# ── هندسة الجارت ──
CW, CH = 1000, 860
ymin = min(c["l"] for c in W); ymax = max(c["h"] for c in W)
pad = (ymax - ymin) * 0.10; ymin -= pad; ymax += pad
pl, pr, pt, pb = 16, 20, 26, 20
pw, ph = CW - pl - pr, CH - pt - pb
slot = pw / N; bw = slot * 0.58
def x(i): return pl + slot * i + slot / 2
def y(p): return pt + (ymax - p) / (ymax - ymin) * ph


def line(x1, y1, x2, y2, col, w=2.4, dash=None, eid=""):
    ln = math.hypot(x2 - x1, y2 - y1)
    d = f' stroke-dasharray="{dash}"' if dash else ''
    i = f' id="{eid}"' if eid else ''
    return f'<line{i} data-len="{ln:.0f}" x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{col}" stroke-width="{w}"{d}/>'


svg = [f'<svg viewBox="0 0 {CW} {CH}" width="{CW}" height="{CH}" xmlns="http://www.w3.org/2000/svg">']
for k in range(5):
    gy = pt + ph * k / 4
    svg.append(f'<line x1="{pl}" y1="{gy:.0f}" x2="{CW-pr}" y2="{gy:.0f}" stroke="rgba(15,46,60,0.06)" stroke-width="1.5"/>')
for i, c in enumerate(W):
    cx = x(i); up = c["c"] >= c["o"]; col = BULL if up else BEAR
    yh, yl, yo, yc = y(c["h"]), y(c["l"]), y(c["o"]), y(c["c"])
    top, bot = min(yo, yc), max(yo, yc); bh = max(bot - top, 2.6)
    svg.append(f'<g class="cnd" id="c{i}"><line x1="{cx:.1f}" y1="{yh:.1f}" x2="{cx:.1f}" y2="{yl:.1f}" stroke="{col}" stroke-width="2.6"/>'
               f'<rect x="{cx-bw/2:.1f}" y="{top:.1f}" width="{bw:.1f}" height="{bh:.1f}" fill="{col}" rx="1"/></g>')
# البركة السفلى
svg.append(line(x(L1) - slot * .7, y(LVL), x(N - 1), y(LVL), TEAL_D, 2.6, eid="lowline"))
# الوسم يمين الخطّ حيث الفراغ: عند القاعين نفسهما تقع الشموع فيشطبها النصّ.
svg.append(f'<g id="lowlbl" opacity="0">{htext(x(N - 1) - slot * 2.2, y(LVL) + 36, "بركة تحت", TEAL_D, 26)}</g>')
for n_, j in enumerate((L1, L2)):
    svg.append(f'<g id="lo{n_}" opacity="0"><circle cx="{x(j):.1f}" cy="{y(W[j]["l"]):.1f}" r="12" fill="none" stroke="{TEAL_D}" stroke-width="3.2"/></g>')
# البركة العليا
svg.append(line(x(H1) - slot * .7, y(LVH), x(N - 1), y(LVH), RED, 2.6, eid="hiline"))
svg.append(f'<g id="hilbl" opacity="0">{htext(x(H1) + slot * 2.4, y(LVH) - 20, "بركة فوق", RED, 26)}</g>')
for n_, j in enumerate((H1, H2)):
    svg.append(f'<g id="hi{n_}" opacity="0"><circle cx="{x(j):.1f}" cy="{y(W[j]["h"]):.1f}" r="12" fill="none" stroke="{RED}" stroke-width="3.2"/></g>')
# الشمعة التي أخذت العليا
svg.append(f'<g id="take" opacity="0"><circle cx="{x(TAKEN):.1f}" cy="{y(W[TAKEN]["h"]):.1f}" r="18" fill="none" stroke="{RED}" stroke-width="4"/>'
           + htext(x(TAKEN) - slot * 2.2, y(W[TAKEN]["h"]) - 26, "أُخذت", RED, 26) + '</g>')
svg.append(f'<g id="safe" opacity="0">{htext(x(N - 1) - slot * 2.2, y(LVL) + 78, "ما انلمست", TEAL_D, 26)}</g>')
svg.append('</svg>')
CHART = "".join(svg)

OPEN = [(i, round(0.10 + 0.030 * i, 2)) for i in range(N)]     # فريم-٠ والشموع تتحرك (§12)
TXT = [
    ("t1", 0.30, 2.30, "بركتين سيولة<br>بنفس النافذة", 62, INK),
    ("t2", 2.60, 5.20, "قاعان متساويان تحت", 54, TEAL_D),
    ("t3", 5.60, 8.20, "وقمّتان متساويتان فوق", 54, RED),
    ("t4", 8.60, 11.6, "السوق ما ياخذ الثنتين", 56, INK),
    ("t5", 12.0, 15.0, "أخذ العليا…", 58, RED),
    ("t6", 15.3, 18.2, "والسفلى ما انلمست", 54, TEAL_D),
]
MARKS = [
    ("lowline", 2.70, 3.35, "draw"), ("lo0", 3.30, 3.55, "pop"), ("lo1", 3.55, 3.80, "pop"),
    ("lowlbl", 3.85, 4.15, "pop"),
    ("hiline", 5.70, 6.35, "draw"), ("hi0", 6.30, 6.55, "pop"), ("hi1", 6.55, 6.80, "pop"),
    ("hilbl", 6.85, 7.15, "pop"),
    ("take", 12.10, 12.55, "pop"),
    ("safe", 15.45, 15.80, "pop"),
]
DRAWSET = ["lowline", "hiline"]
FULLSET = ["lo0", "lo1", "lowlbl", "hi0", "hi1", "hilbl", "take", "safe"]

texts = "".join(f'<div class="hl" id="{i}" style="font-size:{fs}px;color:{col}">{t}</div>'
                for i, a, b, t, fs, col in TXT)

html = f'''<!DOCTYPE html><html lang="ar" dir="rtl"><head><meta charset="utf-8"><style>
{FONT_CSS}
*{{margin:0;padding:0;box-sizing:border-box}}
#stage{{width:1080px;height:1920px;position:relative;overflow:hidden;font-family:Tajawal;
  background:radial-gradient(120% 90% at 50% 0%, #F7F3EC 0%, #F2EEE7 55%, #ECE6DB 100%)}}
.hl{{position:absolute;top:150px;left:40px;right:40px;text-align:center;font-weight:900;
  line-height:1.22;opacity:0}}
#chartwrap{{position:absolute;top:430px;left:40px;width:1000px;height:860px}}
.cnd{{transform-box:fill-box;transform-origin:50% 100%}}
#chip{{position:absolute;top:372px;right:40px;border:2px solid {TEAL_D};color:{TEAL_D};
  font-weight:800;font-size:26px;padding:8px 18px;opacity:0}}
#res{{position:absolute;top:1330px;left:0;right:0;text-align:center;font-weight:900;
  font-size:50px;color:{TEAL_D};opacity:0}}
#cta{{position:absolute;top:1470px;left:70px;right:70px;text-align:center;opacity:0}}
#cta .k{{display:inline-block;border:2.5px solid {INK};color:{INK};font-weight:900;font-size:54px;padding:14px 44px}}
#cta .s{{margin-top:16px;font-weight:700;font-size:32px;color:#5C6C73}}
#edu{{position:absolute;bottom:46px;left:0;right:0;text-align:center;font-size:22px;color:#93A2A8;font-weight:600}}
</style></head><body><div id="stage">
{texts}
<div id="chip">{NAME} · {TF}</div>
<div id="chartwrap">{CHART}</div>
<div id="res">‎+{GAIN} نقطة من البركة العليا</div>
<div id="cta"><span class="k">اكتب «بركتين»</span><div class="s">ويوصلك الدليل كامل</div></div>
<div id="edu">لغرض تعليمي — بيانات حقيقية · {R["date"]}</div>
</div>
<script>
window.__DUR = {DUR};
const $ = id => document.getElementById(id);
const clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
const oc=t=>1-Math.pow(1-t,3);
const ob=t=>{{const c1=1.70158,c3=c1+1;return 1+c3*Math.pow(t-1,3)+c1*Math.pow(t-1,2);}};
const seg=(t,a,b)=>clamp((t-a)/(b-a),0,1);
const OPEN={json.dumps(OPEN)};
const TXTS={json.dumps([[i, a, b] for i, a, b, _, __, ___ in TXT])};
const MARKS={json.dumps(MARKS)};
const DRAWSET={json.dumps(DRAWSET)};
const FULLSET={json.dumps(FULLSET)};
function setLine(el,k){{
  const len=+el.dataset.len||300;
  el.style.strokeDasharray=len; el.style.strokeDashoffset=len*(1-k);
  el.style.opacity=k>0?1:0;
}}
window.__setFrame=function(t){{
  for(let i=0;i<{N};i++){{
    const el=$("c"+i); const o=OPEN[i];
    const k=seg(t,o[1],o[1]+0.42);
    el.style.opacity=k>0?1:0;
    el.style.transform=`scaleY(${{k>=1?1:0.25+0.75*ob(k)}})`;
  }}
  $("chip").style.opacity=oc(seg(t,0.20,0.70));
  for(const id of DRAWSET){{
    const m=MARKS.find(m=>m[0]===id);
    setLine($(id), m?seg(t,m[1],m[2]):0);
  }}
  for(const id of FULLSET){{
    const el=$(id), m=MARKS.find(m=>m[0]===id);
    const k=m?seg(t,m[1],m[2]):0;
    el.style.opacity=oc(k);
    if(m&&m[3]==="pop"){{
      el.style.transformBox="fill-box"; el.style.transformOrigin="50% 50%";
      el.style.transform=`scale(${{0.4+0.6*ob(k)}})`;
    }}
  }}
  for(const [id,a,b] of TXTS){{
    const el=$(id); const kin=seg(t,a,a+0.32), kout=seg(t,b,b+0.28);
    el.style.opacity=oc(kin)*(1-kout);
    el.style.transform=`translateY(${{(1-oc(kin))*26}}px)`;
  }}
  $("res").style.opacity=oc(seg(t,15.9,16.5))*(1-seg(t,21.4,22.0));
  const kc=seg(t,18.5,19.1);
  $("cta").style.opacity=oc(kc);
  $("cta").style.transform=`scale(${{0.86+0.14*ob(kc)}})`;
}};
window.__setFrame(0);
</script></body></html>'''

if __name__ == "__main__":
    out = os.path.join(HERE, f"reel44_{SLUG}.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)
    print(f'{SLUG} | {NAME} {TF} {R["date"]} | {DUR}s | شموع {N} | '
          f'بركة تحت {L1},{L2} @ {LVL:.3f} · بركة فوق {H1},{H2} @ {LVH:.3f} · '
          f'أُخذت العليا عند {TAKEN} · +{GAIN} نقطة | {len(html)} bytes')
