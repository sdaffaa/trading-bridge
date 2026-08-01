#!/usr/bin/env python3
"""Reel frame (1080x1920, cream) with JAPANESE CANDLESTICKS for @liquidity.state.
Bodies come from REAL XAUUSD daily closes (open_t = close_{t-1}, close_t = close_t — both real).
Wicks are illustrative (disclosed in footer). Markup snapped exactly to real prices.
Embeds a render(progress) animation: candles build up (back-ease scaleY), then markup reveals,
then target hit (white flash + zoom). Static screenshot uses p=1 (default)."""
import json, os, math

F="/root/.claude/projects/-home-user-trading-bridge/0050bb5d-88b4-51aa-b27b-0d57c8da6c5e/tool-results/mcp-e5dcb266-4d83-4c1d-bb70-4bd740d597ce-GOLD_SILVER_HISTORY-1785560770698.txt"
rows=[r.split(",") for r in json.load(open(F))["result"].strip().splitlines()[1:] if "," in r]
alld=[(d,round(float(p),2)) for d,p in rows][:70][::-1]
W=alld[27:47]
dates=[d for d,_ in W]; cl=[p for _,p in W]; N=len(cl)

PRIOR_LOW=4009.99; SWEEP=4008.93; ENTRY=4042.63; BOS=4089.29; SL=4005.00; TP=4176.39
i_sweep=dates.index("2026-07-01"); i_entry=dates.index("2026-07-02")
i_bos=dates.index("2026-07-03"); i_tp=dates.index("2026-07-06")

# candle OHLC: open=prior close (real), close=today close (real); illustrative wicks
op=[cl[0]]+cl[:-1]
def wick(i):
    body=abs(cl[i]-op[i]); return max(3.0, body*0.28)   # illustrative
hi=[max(op[i],cl[i])+wick(i) for i in range(N)]
lo=[min(op[i],cl[i])-wick(i) for i in range(N)]

# transforms (portrait reel)
X0,X1=110,970; Y0,Y1=760,1500; PMAX,PMIN=4205.0,3975.0
def X(i): return X0+(i+0.5)/N*(X1-X0)
def Y(p): return Y0+(PMAX-p)/(PMAX-PMIN)*(Y1-Y0)
CW=(X1-X0)/N*0.56

svg=[]
# grid + right axis
for pr in range(3980,4201,40):
    y=Y(pr); svg.append(f'<line x1="{X0}" y1="{y:.1f}" x2="{X1}" y2="{y:.1f}" stroke="#0F2E3C" stroke-opacity="0.06" stroke-width="1"/>')
    svg.append(f'<text x="{X1+12}" y="{y+8:.1f}" fill="#93A2A8" font-size="22" font-family="Tajawal">{pr}</text>')
for i in range(0,N,4):
    svg.append(f'<text x="{X(i):.0f}" y="{Y1+40:.0f}" fill="#93A2A8" font-size="20" font-family="Tajawal" text-anchor="middle">{dates[i][5:]}</text>')

def el(inner,t0,cls="mk"):
    return f'<g class="{cls}" data-t0="{t0:.3f}">{inner}</g>'

# candles (each appears in build-up window 0..0.5)
for i in range(N):
    up = cl[i]>=op[i]; col="#2E8CA6" if up else "#122F3E"
    x=X(i); bt=Y(max(op[i],cl[i])); bb=Y(min(op[i],cl[i])); h=max(3,bb-bt)
    base=bb  # scaleY origin at candle bottom
    inner=(f'<line x1="{x:.1f}" y1="{Y(hi[i]):.1f}" x2="{x:.1f}" y2="{Y(lo[i]):.1f}" stroke="{col}" stroke-width="2.4"/>'
           f'<rect x="{x-CW:.1f}" y="{bt:.1f}" width="{2*CW:.1f}" height="{h:.1f}" fill="{col}"/>')
    t0=0.03+0.47*(i/(N-1))
    svg.append(f'<g class="cndl" data-t0="{t0:.3f}" style="transform-box:fill-box;transform-origin:{x:.1f}px {base:.1f}px;">{inner}</g>')

# markup (reveal after candles)
def hline(p,color,dash="6 7",t0=0.55):
    y=Y(p); s=(f'<line x1="{X0}" y1="{y:.1f}" x2="{X1}" y2="{y:.1f}" stroke="{color}" stroke-width="1.7" stroke-dasharray="{dash}" stroke-linecap="round"/>'
              f'<circle cx="{X0}" cy="{y:.1f}" r="4" fill="{color}"/><circle cx="{X1}" cy="{y:.1f}" r="4" fill="{color}"/>')
    return el(s,t0)
svg.append(hline(PRIOR_LOW,"#122F3E",t0=0.55))
svg.append(hline(BOS,"#2E7D96",t0=0.70))
# sweep marker
svg.append(el(f'<circle cx="{X(i_sweep):.1f}" cy="{Y(SWEEP):.1f}" r="10" fill="#D24B4B"/>',0.60))
# BOS break arrow (touches BOS line)
ax=X(i_bos); ay1=Y(BOS)
svg.append(el(f'<line x1="{ax:.1f}" y1="{Y(cl[i_bos])+30:.1f}" x2="{ax:.1f}" y2="{ay1:.1f}" stroke="#2E7D96" stroke-width="3"/>'
              f'<path d="M{ax-9:.1f},{ay1+13:.1f} L{ax:.1f},{ay1:.1f} L{ax+9:.1f},{ay1+13:.1f}" fill="none" stroke="#2E7D96" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>',0.74))
# OB / return zone
bx0=X(i_sweep)-CW-6; bx1=X(i_entry)+CW+6
svg.append(el(f'<rect x="{bx0:.1f}" y="{Y(ENTRY+6):.1f}" width="{bx1-bx0:.1f}" height="{Y(SWEEP-4)-Y(ENTRY+6):.1f}" fill="#2E7D96" fill-opacity="0.16" stroke="#1E627A" stroke-width="1"/>',0.78))
# long-position tool zones
lx=X(i_entry)-CW
svg.append(el(f'<rect x="{lx:.1f}" y="{Y(TP):.1f}" width="{X1-lx:.1f}" height="{Y(ENTRY)-Y(TP):.1f}" fill="#2E7D96" fill-opacity="0.13"/>'
              f'<rect x="{lx:.1f}" y="{Y(ENTRY):.1f}" width="{X1-lx:.1f}" height="{Y(SL)-Y(ENTRY):.1f}" fill="#D24B4B" fill-opacity="0.11"/>',0.82))
for p,c in [(ENTRY,"#1E627A"),(TP,"#2E8CA6"),(SL,"#D24B4B")]:
    y=Y(p); svg.append(el(f'<line x1="{lx:.1f}" y1="{y:.1f}" x2="{X1}" y2="{y:.1f}" stroke="{c}" stroke-width="2"/><circle cx="{X1}" cy="{y:.1f}" r="4" fill="{c}"/>',0.84))
# target hit check
svg.append(el(f'<circle cx="{X(i_tp):.1f}" cy="{Y(TP):.1f}" r="11" fill="#2E8CA6"/>'
              f'<path d="M{X(i_tp)-8:.1f},{Y(TP):.1f} l6,7 l12,-15" fill="none" stroke="#fff" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>',0.90))
SVG="".join(svg)

# HTML labels with appear times
def lbl(x,y,text,color,size,anchor,t0,w=700):
    tx="translateX(-100%)" if anchor=="end" else ("translateX(-50%)" if anchor=="mid" else "")
    return (f'<div class="lbl mk" data-t0="{t0:.3f}" style="left:{x:.0f}px;top:{y:.0f}px;color:{color};'
            f'font-size:{size}px;font-weight:{w};transform:{tx};">{text}</div>')
L=[
 lbl(X1-6,Y(PRIOR_LOW)-50,"سيولة سابقة","#122F3E",26,"end",0.57),
 lbl(X(i_sweep)-14,Y(SWEEP)+28,"سحب سيولة","#D24B4B",28,"end",0.62),
 lbl(X0+8,Y(BOS)-44,"تغيّر نمط","#2E7D96",28,"start",0.72),
 lbl(X(i_bos)+14,Y(cl[i_bos])+6,"كسر","#2E7D96",24,"start",0.76),
 lbl(X(i_entry)-8,Y(ENTRY+6)+2,"منطقة الدخول","#1E627A",24,"end",0.80),
 lbl(X1-6,Y(TP)-42,"هدف  4176.39","#1E627A",28,"end",0.86),
 lbl(X1-6,Y(SL)+8,"ستوب  4005","#D24B4B",26,"end",0.86),
]
LABELS="".join(L)
TAJ=open(os.path.join(os.path.dirname(__file__),"tajawal_embed.css"),encoding="utf-8").read()

# small logo (reuse)
import importlib.util
PHI=(1+5**0.5)/2
Vv=[(-1,PHI,0),(1,PHI,0),(-1,-PHI,0),(1,-PHI,0),(0,-1,PHI),(0,1,PHI),(0,-1,-PHI),(0,1,-PHI),(PHI,0,-1),(PHI,0,1),(-PHI,0,-1),(-PHI,0,1)]
FA=[(0,11,5),(0,5,1),(0,1,7),(0,7,10),(0,10,11),(1,5,9),(5,11,4),(11,10,2),(10,7,6),(7,1,8),(3,9,4),(3,4,2),(3,2,6),(3,6,8),(3,8,9),(4,9,5),(2,4,11),(6,2,10),(8,6,7),(9,8,1)]
def nrm(a):
    m=math.sqrt(sum(c*c for c in a))or 1;return(a[0]/m,a[1]/m,a[2]/m)
def sub(a,b):return(a[0]-b[0],a[1]-b[1],a[2]-b[2])
def ad(a,b):return(a[0]+b[0],a[1]+b[1],a[2]+b[2])
def cr(a,b):return(a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
def dt(a,b):return a[0]*b[0]+a[1]*b[1]+a[2]*b[2]
def mv(M,v):return tuple(dt(M[i],v)for i in range(3))
def mm(A,B):
    Bt=list(zip(*B));return tuple(tuple(dt(A[i],Bt[j])for j in range(3))for i in range(3))
def rtt(ax,an):
    x,y,z=nrm(ax);c=math.cos(an);s=math.sin(an);t=1-c
    return((t*x*x+c,t*x*y-s*z,t*x*z+s*y),(t*x*y+s*z,t*y*y+c,t*y*z-s*x),(t*x*z-s*y,t*y*z+s*x,t*z*z+c))
def al(a,b):
    a=nrm(a);b=nrm(b);v=cr(a,b);c=dt(a,b)
    if c>0.9999:return((1,0,0),(0,1,0),(0,0,1))
    if c<-0.9999:return rtt((1,0,0),math.pi)
    return rtt(v,math.acos(max(-1,min(1,c))))
R=al(nrm(ad(ad(Vv[0],Vv[11]),Vv[5])),(0,0,1));P=[mv(R,v)for v in Vv]
o=max(P,key=lambda p:p[0]**2+p[1]**2);R=mm(rtt((0,0,1),math.pi/2-math.atan2(o[1],o[0])),R)
R=mm(rtt((1,0,0),math.radians(-13)),R);P=[mv(R,v)for v in Vv]
def prj(p):return(120+p[0]*100,120-p[1]*100)
LIv=nrm((-0.32,0.75,0.58))
def sil(t):
    st=[(0,(52,68,84)),(0.4,(120,143,159)),(0.72,(190,206,214)),(1,(246,250,253))]
    for i in range(3):
        t0,c0=st[i];t1,c1=st[i+1]
        if t<=t1:
            f=(t-t0)/(t1-t0)if t1>t0 else 0;return tuple(round(c0[k]+(c1[k]-c0[k])*f)for k in range(3))
    return st[-1][1]
ff=[]
for tri in FA:
    a,b,c=(P[i]for i in tri);nn=nrm(cr(sub(b,a),sub(c,a)))
    if nn[2]<=0.03:continue
    ff.append(((a[2]+b[2]+c[2])/3,tri,max(0,dt(nn,LIv))))
ff.sort(key=lambda x:x[0]);pth=[]
for _,tri,sh in ff:
    d="M "+" L ".join(f"{prj(P[i])[0]:.1f},{prj(P[i])[1]:.1f}" for i in tri)+" Z"
    r,g_,b=sil(0.1+0.9*sh);pth.append(f'<path d="{d}" fill="rgb({r},{g_},{b})" stroke="#54687a" stroke-width="0.9" stroke-linejoin="round"/>')
LOGO=f'<svg viewBox="0 0 240 240" width="104" height="104" xmlns="http://www.w3.org/2000/svg">{"".join(pth)}</svg>'

HTML=f"""<!DOCTYPE html>
<html lang="ar" dir="rtl"><head><meta charset="UTF-8"/>
<title>Liquidity State — Candlestick Reel</title>
<meta name="hz:slide-selector" content=".slide"/><meta name="hz:canvas-width" content="1080"/><meta name="hz:canvas-height" content="1920"/>
<style>
{TAJ}
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{display:flex;justify-content:center;align-items:center;min-height:100vh;background:#ccc;}}
.slide{{position:relative;width:1080px;height:1920px;overflow:hidden;font-family:'Tajawal',sans-serif;color:#0F2E3C;
  background:radial-gradient(120% 80% at 50% 32%, #F7F3EC 0%, #F2EEE7 55%, #ECE6DB 100%);}}
.stage{{position:absolute;inset:0;transform-origin:50% 62%;}}
.chip{{position:absolute;top:44px;right:56px;padding:10px 22px;border:1.5px solid rgba(46,125,150,0.5);border-radius:4px;
  font-size:26px;font-weight:700;letter-spacing:1px;color:#1E627A;direction:ltr;}}
.logo{{position:absolute;left:56px;top:66px;filter:drop-shadow(0 6px 12px rgba(15,46,60,0.16));}}
.wm{{position:absolute;left:180px;top:96px;font-weight:700;font-size:30px;letter-spacing:8px;color:#3d5560;direction:ltr;}}
.hook{{position:absolute;left:0;right:0;top:250px;text-align:center;font-size:78px;font-weight:900;color:#0F2E3C;line-height:1.08;}}
.sub{{position:absolute;left:0;right:0;top:430px;text-align:center;font-size:34px;font-weight:500;color:#5C6C73;}}
.plot{{position:absolute;left:0;top:0;}}
.lbl{{position:absolute;white-space:nowrap;font-family:'Tajawal',sans-serif;opacity:0;
  text-shadow:0 0 6px #F4EFE6,0 0 6px #F4EFE6,2px 2px 5px #F4EFE6,-2px -2px 5px #F4EFE6,2px -2px 5px #F4EFE6,-2px 2px 5px #F4EFE6;}}
.mk{{opacity:0;}}
.cndl{{opacity:0;}}
.flash{{position:absolute;inset:0;background:#fff;opacity:0;pointer-events:none;}}
.result{{position:absolute;left:50%;top:1580px;transform:translateX(-50%);display:flex;align-items:center;gap:24px;
  padding:20px 40px;border:1.5px solid rgba(46,125,150,0.45);border-radius:3px;background:rgba(46,140,166,0.10);white-space:nowrap;opacity:0;}}
.result .tick{{font-size:38px;color:#2E8CA6;font-weight:900;}}
.result .t{{font-size:38px;font-weight:800;color:#0F2E3C;}}
.result .v{{font-size:36px;font-weight:800;color:#1E627A;direction:ltr;font-style:italic;}}
.cta{{position:absolute;left:50%;top:1678px;transform:translateX(-50%);display:flex;gap:14px;align-items:center;
  padding:16px 40px;border-radius:3px;background:#0F2E3C;color:#EAF6F8;font-size:30px;font-weight:700;white-space:nowrap;opacity:0;}}
.cta b{{color:#5AA6BC;}}
.foot{{position:absolute;left:0;right:0;bottom:30px;text-align:center;font-size:22px;font-weight:500;color:#7C8A90;}}
</style></head>
<body>
<div class="slide" data-canvas-width="1080" data-canvas-height="1920">
  <div class="flash" id="flash"></div>
  <div class="stage" id="stage">
    <div class="logo">{LOGO}</div><div class="wm">LIQUIDITY STATE</div>
    <div class="chip">XAUUSD · يومي</div>
    <div class="hook">البلوك اللي<br/>يرجّع السعر</div>
    <div class="sub">سحب السيولة ← تغيّر النمط ← الدخول ← الهدف</div>
    <svg class="plot" width="1080" height="1920" viewBox="0 0 1080 1920" xmlns="http://www.w3.org/2000/svg">{SVG}</svg>
    {LABELS}
    <div class="result" id="res"><span class="tick">✓</span><span class="t">وصل الهدف</span><span class="v">+$133.76 · RR 1:3.5</span></div>
    <div class="cta" id="cta">للملف كامل اكتب <b>بلوك</b> بالتعليقات</div>
  </div>
  <div class="foot">لغرض تعليمي — أجسام الشموع من إغلاقات XAUUSD اليومية الحقيقية (Alpha Vantage) · الفتائل توضيحية</div>
</div>
<script>
function ease(x){{return 1-Math.pow(1-x,3);}}
function back(x){{const c=1.70158;return 1+ (c+1)*Math.pow(x-1,3)+c*Math.pow(x-1,2);}}
function render(p){{
  document.querySelectorAll('.cndl').forEach(g=>{{
    const t0=+g.dataset.t0, d=0.06; let a=(p-t0)/d; a=Math.max(0,Math.min(1,a));
    g.style.opacity=a>0?1:0; const s=a>=1?1:back(a); g.style.transform='scaleY('+s.toFixed(3)+')';
  }});
  document.querySelectorAll('.mk,.lbl').forEach(g=>{{
    const t0=+g.dataset.t0, d=0.05; let a=(p-t0)/d; a=Math.max(0,Math.min(1,a)); g.style.opacity=ease(a);
  }});
  // target flash + zoom around 0.90
  const fp=Math.max(0,1-Math.abs(p-0.91)/0.05); document.getElementById('flash').style.opacity=(fp*0.5).toFixed(3);
  const zt=Math.max(0,Math.min(1,(p-0.86)/0.12)); document.getElementById('stage').style.transform='scale('+(1+0.05*ease(zt)).toFixed(4)+')';
  const rp=Math.max(0,Math.min(1,(p-0.93)/0.05)); document.getElementById('res').style.opacity=rp;
  const cp=Math.max(0,Math.min(1,(p-0.95)/0.05)); document.getElementById('cta').style.opacity=cp;
}}
function fromHash(){{const m=/p=([0-9.]+)/.exec(location.hash); render(m?parseFloat(m[1]):1);}}
window.addEventListener('hashchange',fromHash); fromHash();
</script>
</body></html>"""
out=os.path.join(os.path.dirname(__file__),"reel_frame.html")
open(out,"w",encoding="utf-8").write(HTML)
print("wrote",out,"N",N)
