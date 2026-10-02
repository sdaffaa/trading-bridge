# -*- coding: utf-8 -*-
"""تشغيلة ٥٧ — ريل «VWAP»: الامتداد عن القيمة وجفاف حجم الاستمرار.

طبقتان فقط (VWAP رئيسي + الحجم مؤكِّد) كما تفرض وحدة المناهج، ولا دخول
ولا وقف ولا هدف: هذا **درس قراءة** لا صفقة، فلا يُكتب R لا يُقاس.

المقاسات من البريف: الشارت 952 عرضاً، خط الـVWAP ٦ بكسل، الباندات ٣٫٥،
الشموع ~٧٢٪ من ارتفاع اللوحة والحجم ~٢٦٪.

    python3 run57_vwap.py        # يكتب out57/reel57.html
"""
import os

from run55_kit import FONT_CSS, Panel, num, dnum, svg, t
import run55_page as RP
import run57_facts as F

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out57")
os.makedirs(OUT, exist_ok=True)

NAVY, NAVY2 = "#020F1A", "#061824"
OFFW, CARD, EDGE = "#F4F1EA", "#0B1B24", "#1B3540"
TXD, TXL, MUT = "#0B2635", "#EAF2F5", "#8FA6AF"
CYAN, AMBER, RED, GRN = "#35C6D8", "#D9A441", "#DF7573", "#7FBF7E"
BULL, BEAR = "#20939E", "#61808E"

CW, CH = 952, 900          # نسبة اللوحة تتبع البطاقة الرأسية
VOL_H = 234                # ≈٢٦٪ من ارتفاع اللوحة (البريف: ٢٢–٢٨٪)
DUR = 23.2


def chart(p):
    B, W = p["B"], p["W"]
    i0, i1, s0 = p["i0"], p["i1"], p["s0"]
    pn = Panel(B, i0, i1, CW, CH, pad=dict(l=18, r=112, t=26, b=46),
               vol_h=VOL_H)
    band = [(k, W[k][0], W[k][1]) for k in p["idx"] if k <= i1]
    pn.ext(lo=min(v - 2 * s for _, v, s in band),
           hi=max(v + 2 * s for _, v, s in band)).fin(0.05)

    L = {}
    s = []
    for k in range(6):
        v = pn.LO + (pn.HI - pn.LO) * k / 5
        Y = pn.y(v)
        s.append(f'<line x1="{pn.px0:.1f}" y1="{Y:.1f}" x2="{pn.px1:.1f}" '
                 f'y2="{Y:.1f}" stroke="rgba(255,255,255,0.055)" stroke-width="1"/>')
        s.append(t(pn.px1 + 12, Y + 8, num(v, 1), MUT, 22, 500, "start",
                   rtl=False, halo=CARD))
    L["grid"] = "".join(s)

    # الشموع: كل واحدة مجموعة تُكشف كاملةً — لا حركة داخل الشمعة تُخترع
    s = []
    bw = max(4.0, pn.slot * 0.66)
    for i in range(i0, i1 + 1):
        c = B[i]
        col = BULL if c["c"] >= c["o"] else BEAR
        X = pn.x(i)
        s.append(f'<g class="cd" data-i="{i}" opacity="0">'
                 f'<line x1="{X:.1f}" y1="{pn.y(c["h"]):.1f}" x2="{X:.1f}" '
                 f'y2="{pn.y(c["l"]):.1f}" stroke="{col}" stroke-width="2"/>'
                 f'<rect x="{X - bw / 2:.1f}" y="{min(pn.y(c["o"]), pn.y(c["c"])):.1f}" '
                 f'width="{bw:.1f}" '
                 f'height="{max(2.0, abs(pn.y(c["c"]) - pn.y(c["o"]))):.1f}" '
                 f'fill="{col}"/></g>')
    L["cds"] = "".join(s)

    # أعمدة الحجم: كل عمود بزمن شمعته، وقممها لا تُقصّ
    y0 = pn.py1 + 18
    y1 = y0 + VOL_H - 30
    mx = max(B[k]["v"] for k in range(i0, i1 + 1))
    s = [f'<line x1="{pn.px0:.1f}" y1="{y0 - 8:.1f}" x2="{pn.px1:.1f}" '
         f'y2="{y0 - 8:.1f}" stroke="{EDGE}" stroke-width="1.4"/>']
    for i in range(i0, i1 + 1):
        c = B[i]
        h = c["v"] / mx * (y1 - y0)
        col = BULL if c["c"] >= c["o"] else BEAR
        s.append(f'<g class="vb" data-i="{i}" opacity="0">'
                 f'<rect x="{pn.x(i) - bw / 2:.1f}" y="{y1 - h:.1f}" '
                 f'width="{bw:.1f}" height="{h:.1f}" fill="{col}" '
                 f'opacity="0.5"/></g>')
    s.append(t(pn.px1 + 12, y0 + 16, "الحجم", MUT, 21, 600, "start", halo=CARD))
    # خطّ متوسط حجم الجلسة — المرجع الذي يُقاس عليه «الجفاف»
    ym = y1 - p["mv"] / mx * (y1 - y0)
    L["volavg"] = (f'<line x1="{pn.x(p["s0"]):.1f}" y1="{ym:.1f}" '
                   f'x2="{pn.px1:.1f}" y2="{ym:.1f}" stroke="{AMBER}" '
                   f'stroke-width="2" stroke-dasharray="7 5"/>'
                   + t(pn.px1 - 14, ym - 10, f'متوسط حجم الجلسة {p["mv"]:,.0f}',
                       AMBER, 21, 700, "start", halo=CARD))
    L["vol"] = "".join(s)

    # ضوء على عمودَي الدفع والاستمرار — لا سهم طويل
    sp = []
    for i in [p["i"], p["j"]] + [k for k in p["idx"] if p["j"] < k <= p["j"] + 3]:
        c = B[i]
        h = c["v"] / mx * (y1 - y0)
        sp.append(f'<rect x="{pn.x(i) - bw / 2:.1f}" y="{y1 - h:.1f}" '
                  f'width="{bw:.1f}" height="{h:.1f}" fill="{CYAN}"/>')
    L["volspot"] = "".join(sp)

    # الـVWAP وباندات ±١σ و±٢σ — تبدأ من أول شمعة في الجلسة
    def poly(f_, w, col, op=1.0, dash=None):
        pts = " ".join(f"{pn.x(k):.1f},{pn.y(f_(v, s)):.1f}" for k, v, s in band)
        d = f' stroke-dasharray="{dash}"' if dash else ""
        return (f'<polyline points="{pts}" fill="none" stroke="{col}" '
                f'stroke-width="{w}" stroke-linejoin="round" opacity="{op}"{d}/>')

    L["vwap"] = (poly(lambda v, s: v, 6.0, CYAN)
                 + t(pn.px1 - 14, pn.y(band[-1][1]) - 16,
                     "VWAP الجلسة", CYAN, 24, 700, "start", halo=CARD))
    L["b1"] = (poly(lambda v, s: v + s, 3.5, CYAN, 0.42)
               + poly(lambda v, s: v - s, 3.5, CYAN, 0.42))
    L["b2"] = (poly(lambda v, s: v + 2 * s, 3.5, CYAN, 0.26, "10 8")
               + poly(lambda v, s: v - 2 * s, 3.5, CYAN, 0.26, "10 8")
               + t(pn.px1 - 14, pn.y(band[-1][1] + 2 * band[-1][2]) - 12,
                   "‎+2σ", CYAN, 22, 700, "start", rtl=False, halo=CARD))

    # حدّ الجلسة: خطّ رأسي عند إعادة الضبط
    xs = pn.x(s0) - pn.slot * 0.5
    L["sess"] = (f'<line x1="{xs:.1f}" y1="{pn.py0:.1f}" x2="{xs:.1f}" '
                 f'y2="{pn.py1:.1f}" stroke="{MUT}" stroke-width="2" '
                 f'stroke-dasharray="6 6"/>'
                 + t(xs + 12, pn.py0 + 26, "بداية الجلسة ⁦23:00⁩ غرينتش", MUT,
                     21, 600, "end", halo=CARD))

    L["ext"] = (f'<circle cx="{pn.x(p["i"]):.1f}" cy="{pn.y(B[p["i"]]["c"]):.1f}" '
                f'r="10" fill="none" stroke="{RED}" stroke-width="3"/>'
                + t(pn.x(p["i"]) - 18, pn.y(B[p["i"]]["c"]) + 8,
                    f'⁦{p["z"]:.2f}⁩σ', RED, 24, 700, "start", halo=CARD))
    L["peak"] = (f'<circle cx="{pn.x(p["j"]):.1f}" cy="{pn.y(p["peak"]):.1f}" '
                 f'r="10" fill="none" stroke="{RED}" stroke-width="3"/>'
                 f'<line x1="{pn.x(p["j"]):.1f}" y1="{pn.y(p["peak"]):.1f}" '
                 f'x2="{pn.x(p["j"]):.1f}" y2="{pn.y(p["vwap_j"]):.1f}" '
                 f'stroke="{RED}" stroke-width="2" stroke-dasharray="5 5"/>'
                 + t(pn.x(p["j"]) - 20, pn.y(p["peak"]) + 10,
                     f'⁦{p["ext_pts"]:.1f}⁩ نقطة فوق القيمة', RED, 23, 700,
                     "start", halo=CARD))
    L["back"] = (f'<circle cx="{pn.x(p["rec"]):.1f}" '
                 f'cy="{pn.y(p["close_rec"]):.1f}" r="10" fill="none" '
                 f'stroke="{GRN}" stroke-width="3"/>'
                 + t(pn.x(p["rec"]) - 14, pn.y(p["close_rec"]) + 34,
                     f'رجع للقيمة {num(p["close_rec"], 1)}', "#4E8E4C", 23,
                     700, "end", halo=CARD))

    tm = []
    every = max(1, (i1 - i0) // 7)
    for i in range(i0, i1 + 1):
        if (i - i0) % every:
            continue
        X = pn.x(i)
        if pn.px0 + 16 < X < pn.px1 - 16:
            lab = B[i]["d"][11:]            # HH:MM
            if B[i]["d"][11:] == "23:00" or i == i0:
                lab = B[i]["d"][5:10]       # حدّ اليوم يحمل تاريخه
            tm.append(f'<g class="tm" data-i="{i}" opacity="0">'
                      + t(X, pn.py1 + VOL_H + 4, dnum(lab), MUT, 21, 500,
                          "middle", rtl=False, halo=CARD) + '</g>')
    L["tm"] = "".join(tm)

    body = (L["grid"] + L["cds"] + L["vol"] + L["tm"]
            + f'<g id="gsess" opacity="0">{L["sess"]}</g>'
            + f'<g id="gvw" opacity="0">{L["vwap"]}</g>'
            + f'<g id="gb1" opacity="0">{L["b1"]}</g>'
            + f'<g id="gb2" opacity="0">{L["b2"]}</g>'
            + f'<g id="gext" opacity="0">{L["ext"]}</g>'
            + f'<g id="gpk" opacity="0">{L["peak"]}</g>'
            + f'<g id="gva" opacity="0">{L["volavg"]}</g>'
            + f'<g id="gvs" opacity="0">{L["volspot"]}</g>'
            + f'<g id="gbk" opacity="0">{L["back"]}</g>')
    return svg(CW, CH, body), pn


def hook_chart(p, W=560, H=430):
    """لقطة الهوك: شمعة الذروة وخطّ الـVWAP تحتها — المسافة هي الفكرة."""
    B = p["B"]
    a, z = p["j"] - 3, p["j"] + 1
    seg = B[a:z + 1]
    lo = min(min(c["l"] for c in seg), p["vwap_j"])
    hi = max(c["h"] for c in seg)
    pad = (hi - lo) * 0.16
    LO, HI = lo - pad, hi + pad
    y = lambda v: H - 66 - (v - LO) / (HI - LO) * (H - 140)
    n = len(seg)
    xs = lambda k: 170 + (k + 0.5) * (W - 300) / n
    bw = (W - 300) / n * 0.46
    s = []
    for k, c in enumerate(seg):
        col = BULL if c["c"] >= c["o"] else BEAR
        X = xs(k)
        s.append(f'<line x1="{X:.1f}" y1="{y(c["h"]):.1f}" x2="{X:.1f}" '
                 f'y2="{y(c["l"]):.1f}" stroke="{col}" stroke-width="3.5"/>'
                 f'<rect x="{X - bw / 2:.1f}" y="{min(y(c["o"]), y(c["c"])):.1f}" '
                 f'width="{bw:.1f}" '
                 f'height="{max(3.0, abs(y(c["c"]) - y(c["o"]))):.1f}" fill="{col}"/>')
    s.append(f'<line x1="40" y1="{y(p["vwap_j"]):.1f}" x2="{W - 40}" '
             f'y2="{y(p["vwap_j"]):.1f}" stroke="{CYAN}" stroke-width="6"/>')
    s.append(t(W - 44, y(p["vwap_j"]) + 34, "VWAP", CYAN, 26, 700, "end",
               rtl=False, halo=NAVY))
    s.append(f'<line x1="{xs(3):.1f}" y1="{y(p["peak"]):.1f}" '
             f'x2="{xs(3):.1f}" y2="{y(p["vwap_j"]):.1f}" stroke="{RED}" '
             f'stroke-width="2.5" stroke-dasharray="6 5"/>')
    s.append(t(xs(3) - 16, (y(p["peak"]) + y(p["vwap_j"])) / 2,
               f'⁦{p["ext_pts"]:.1f}⁩ نقطة', RED, 26, 700, "start", halo=NAVY))
    return svg(W, H, "".join(s))


def build(p):
    sv, pn = chart(p)
    hv = hook_chart(p)
    B = p["B"]
    rel = lambda i, v: (pn.x(i) / CW, pn.y(v) / CH)
    cx1, cy1 = rel(p["s0"] + 8, p["vwap_i"])
    cx2, cy2 = rel(p["j"], p["peak"])
    cx3, cy3 = rel(p["rec"], p["close_rec"])

    js = f"""
const S=(t,a,b)=>Math.max(0,Math.min(1,(t-a)/(b-a)));
const E=x=>x<.5?4*x*x*x:1-Math.pow(-2*x+2,3)/2;
const $=id=>document.getElementById(id);
const CDS=[...document.querySelectorAll('.cd')];
const VBS=[...document.querySelectorAll('.vb')];
const TMS=[...document.querySelectorAll('.tm')];
const I0={p['i0']}, S0={p['s0']}, IEX={p['i']}, IPK={p['j']}, IRC={p['rec']}, I1={p['i1']};
function revealTo(t){{
  if(t<3.70) return S0-1;
  if(t<5.60) return S0+6;
  if(t<7.40) return S0+6+Math.round(S(t,5.60,7.30)*6);
  if(t<9.60) return S0+12+Math.round(S(t,7.40,9.40)*(IEX-S0-12));
  if(t<11.80) return IEX+Math.round(S(t,9.60,11.10)*(IPK-IEX));
  if(t<14.60) return IPK+Math.round(S(t,11.80,13.60)*3);
  if(t<17.80) return IPK+3+Math.round(S(t,14.60,17.20)*(IRC-IPK-3));
  return I1;
}}
// ثلاث حركات كاميرا، والمركز مقيَّد فلا تخرج حافة من الإطار
const CAM=[[0.00,1.06,{cx1:.4f},{cy1:.4f}],[7.40,1.06,{cx1:.4f},{cy1:.4f}],
 [9.60,1.14,{cx2:.4f},{cy2:.4f}],[14.60,1.14,{cx2:.4f},{cy2:.4f}],
 [15.90,1.10,{cx3:.4f},{cy3:.4f}],[17.80,1.10,{cx3:.4f},{cy3:.4f}],
 [19.00,1.00,0.50,0.50],[23.20,1.00,0.50,0.50]];
function cam(t){{
  let a=CAM[0],b=CAM[CAM.length-1];
  for(let i=0;i<CAM.length-1;i++){{if(t>=CAM[i][0]&&t<=CAM[i+1][0]){{a=CAM[i];b=CAM[i+1];break;}}}}
  const u=b[0]===a[0]?0:E(S(t,a[0],b[0]));
  let s=a[1]+(b[1]-a[1])*u, cx=a[2]+(b[2]-a[2])*u, cy=a[3]+(b[3]-a[3])*u;
  const h=0.5/s;
  cx=Math.max(h,Math.min(1-h,cx)); cy=Math.max(h,Math.min(1-h,cy));
  return [s,cx,cy];
}}
const TX=[['t1',0.00,0.80],['t2',0.80,2.10],['t3',2.35,3.70],['t4',3.70,5.60],
 ['t5',5.60,7.40],['t6',7.40,9.60],['t7',9.60,11.80],['t8',11.80,14.60],
 ['t9',14.60,17.80],['t10',17.80,19.60],['t11',19.60,23.20]];
window.__DUR={DUR};
window.__setFrame=function(t){{
  const sw=E(S(t,2.00,2.30));
  $('navy').style.opacity=(1-sw); $('light').style.opacity=sw;
  $('card').style.opacity=E(S(t,2.15,2.60))*(1-E(S(t,19.60,20.00)));
  $('hook').style.opacity=(1-E(S(t,1.80,2.10)));

  const n=revealTo(t);
  for(const g of CDS) g.setAttribute('opacity', (+g.dataset.i)<=n?1:0);
  for(const g of VBS) g.setAttribute('opacity', (+g.dataset.i)<=n?1:0);
  for(const g of TMS) g.setAttribute('opacity', (+g.dataset.i)<=n?1:0);

  const [s,cx,cy]=cam(t);
  $('cam').style.transform=`scale(${{s.toFixed(4)}})`;
  $('cam').style.transformOrigin=`${{(cx*100).toFixed(2)}}% ${{(cy*100).toFixed(2)}}%`;

  $('gsess').setAttribute('opacity', E(S(t,3.85,4.20)));
  $('gvw').setAttribute('opacity',  E(S(t,4.55,4.95)));
  $('gb1').setAttribute('opacity',  E(S(t,5.75,6.15)));
  $('gb2').setAttribute('opacity',  E(S(t,6.55,6.95)));
  $('gext').setAttribute('opacity', E(S(t,8.95,9.30)));
  $('gpk').setAttribute('opacity',  E(S(t,11.05,11.40)));
  $('gva').setAttribute('opacity',  E(S(t,12.10,12.50)));
  $('gvs').setAttribute('opacity',  E(S(t,13.10,13.50)));
  $('gbk').setAttribute('opacity',  E(S(t,17.15,17.50)));

  for(const [id,a,b] of TX){{
    const o=E(S(t,a,a+0.18))*(1-E(S(t,b-0.16,b)));
    const el=$(id); el.style.opacity=o;
    el.style.transform=`translateY(${{((1-E(S(t,a,a+0.30)))*14).toFixed(2)}}px)`;
  }}
}};
window.__setFrame(0);
"""

    def TX(i, main, sub="", cls=""):
        s = f'<div class="sub">{sub}</div>' if sub else ""
        return f'<div class="tx {cls}" id="t{i}"><div class="mn">{main}</div>{s}</div>'

    src = (f'{p["meta"]["src"]} · ⁦15m⁩ · إعادة ضبط الجلسة ⁦23:00⁩ غرينتش · '
           f'VWAP محسوب من الشموع')
    texts = (
        TX(1, "السعر ابتعد عن قيمته.", "", "hook")
        + TX(2, "يرجع ولا يكمل؟", "", "hook")
        + TX(3, "القيمة مو سعر —<br>متوسط مرجَّح بالحجم.")
        + TX(4, "كل جلسة تبدأ من صفر", src)
        + TX(5, "الباندات = انحراف الجلسة", "‎±1σ و ‎±2σ حول الـVWAP")
        + TX(6, "الإغلاق فوق ‎+2σ",
             f'⁦{p["z"]:.2f}⁩σ فوق القيمة — وحجم الدفع نفسه '
             f'⁦{p["rel_i"]:.2f}⁩× المتوسط')
        + TX(7, "الذروة: ⁦25⁩ نقطة فوق القيمة", "أبعد ما وصله السعر في الجلسة")
        + TX(8, "حجم الاستمرار جفّ",
             f'ثلاث شمعات بعد الذروة = ⁦{p["dry"]:.2f}⁩× متوسط حجم الجلسة')
        + TX(9, "رجع للقيمة", f'⁦{p["back"]:.1f}⁩ نقطة في ⁦{p["bars"]}⁩ شمعة')
        + TX(10, "الـVWAP يقول وين القيمة،<br>والحجم يقول منو يدفع.")
        + TX(11, 'اكتب «VWAP» وخذ قائمة الفحص',
             "احفظ الريل وراجعه قبل تحليلك الجاي<br>"
             "وأرسله لمتداول يعتمد على أداة واحدة", "cta")
    )

    html = f"""<!DOCTYPE html><html lang="ar" dir="rtl"><head><meta charset="UTF-8">
<style>{FONT_CSS}
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{background:#000}}
#stage{{position:relative;width:1080px;height:1920px;overflow:hidden;
  font-family:'PlexAr',sans-serif;direction:rtl}}
#navy{{position:absolute;inset:0;background:
  radial-gradient(120% 80% at 50% 12%, {NAVY2} 0%, {NAVY} 62%, #01080F 100%)}}
#light{{position:absolute;inset:0;background:{OFFW};opacity:0}}
#brand{{position:absolute;top:104px;left:0;right:0;display:flex;
  flex-direction:column;align-items:center;gap:10px;z-index:9}}
#brand .g{{width:60px;height:60px}}
#brand .w{{font-family:'Inter',sans-serif;font-size:22px;letter-spacing:7px;
  color:{CYAN};font-weight:500}}
#hook{{position:absolute;top:1090px;left:0;right:0;display:flex;
  justify-content:center;z-index:7}}
#hook svg{{width:560px;height:430px;display:block}}
#card{{position:absolute;top:566px;left:44px;right:44px;height:938px;
  background:{CARD};border:1.5px solid {EDGE};overflow:hidden;opacity:0;z-index:3}}
#cam{{width:100%;height:100%;will-change:transform}}
#cam svg{{width:100%;height:100%;display:block}}
.tx{{position:absolute;top:262px;left:70px;right:70px;text-align:center;
  opacity:0;z-index:8}}
.tx .mn{{font-size:70px;font-weight:700;line-height:1.24;color:{TXD};
  letter-spacing:-1px}}
.tx .sub{{margin-top:18px;font-size:30px;font-weight:400;color:#5C6C73;
  line-height:1.5}}
.tx.hook{{top:436px}}
.tx.hook .mn{{font-size:96px;color:#F7FAFB;line-height:1.22}}
.tx.cta{{top:0;bottom:0;display:flex;flex-direction:column;
  align-items:center;justify-content:center}}
.tx.cta .mn{{font-size:86px;color:{TXD}}}
.tx.cta .sub{{font-size:35px;color:#5C6C73;margin-top:34px;line-height:1.6}}
</style></head><body>
<div id="stage">
  <div id="navy"></div><div id="light"></div>
  <div id="brand"><div class="g">{RP.GEM}</div><div class="w">LIQUIDITY STATE</div></div>
  <div id="hook">{hv}</div>
  <div id="card"><div id="cam">{sv}</div></div>
  {texts}
</div>
<script>{js}</script></body></html>"""
    path = os.path.join(OUT, "reel57.html")
    open(path, "w", encoding="utf-8").write(html)
    return path


if __name__ == "__main__":
    p = F.facts()
    print("→", build(p))
