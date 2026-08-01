#!/usr/bin/env python3
"""Educational trade chart (1080x1350, cream content template) for @liquidity.state.
REAL XAUUSD daily spot closes (Alpha Vantage GOLD_SILVER_HISTORY). Markup is snapped
EXACTLY to real close values via a single price->y / index->x transform. No invented data.
Line chart (closes only) — labelled 'لغرض تعليمي' with the data source, per brand honesty rule."""
import json, os, math

# ---- real data window (chronological), bars 27..46 of the last-70 slice ----
F="/root/.claude/projects/-home-user-trading-bridge/0050bb5d-88b4-51aa-b27b-0d57c8da6c5e/tool-results/mcp-e5dcb266-4d83-4c1d-bb70-4bd740d597ce-GOLD_SILVER_HISTORY-1785560770698.txt"
rows=[r.split(",") for r in json.load(open(F))["result"].strip().splitlines()[1:] if "," in r]
alld=[(d,round(float(p),2)) for d,p in rows][:70][::-1]          # chronological
W=alld[27:47]                                                     # 20 real points
dates=[d for d,_ in W]; px=[p for _,p in W]; N=len(px)

# ---- real trade levels (exact real closes) ----
PRIOR_LOW=4009.99   # 2026-06-25  liquidity
SWEEP=4008.93       # 2026-07-01  swept the prior low
ENTRY=4042.63       # 2026-07-02  reversal-confirmation close
BOS=4089.29         # 2026-06-28 swing high -> broken 07-03 (close 4130.37)
SL=4005.00          # below the sweep
TP=4176.39          # 2026-07-06  target (reached)
i_sweep=dates.index("2026-07-01"); i_entry=dates.index("2026-07-02")
i_bos=dates.index("2026-07-03");   i_tp=dates.index("2026-07-06")
risk=ENTRY-SL; reward=TP-ENTRY; RR=reward/risk

# ---- transforms ----
X0,X1=120,960; Y0,Y1=560,1060; PMAX,PMIN=4200.0,3980.0
def X(i): return X0+(i/(N-1))*(X1-X0)
def Y(p): return Y0+(PMAX-p)/(PMAX-PMIN)*(Y1-Y0)

# ---- svg geometry ----
g=[]
# grid + right axis
for pr in range(3980,4201,40):
    y=Y(pr); g.append(f'<line x1="{X0}" y1="{y:.1f}" x2="{X1}" y2="{y:.1f}" stroke="#0F2E3C" stroke-opacity="0.06" stroke-width="1"/>')
    g.append(f'<text x="{X1+14}" y="{y+9:.1f}" fill="#93A2A8" font-size="24" font-family="Tajawal">{pr}</text>')
# date ticks
for i in range(0,N,4):
    x=X(i); g.append(f'<text x="{x:.0f}" y="{Y1+42:.0f}" fill="#93A2A8" font-size="22" font-family="Tajawal" text-anchor="middle">{dates[i][5:]}</text>')
# long-position tool: reward (turquoise) & risk (red) zones, entry bar -> right
lx=X(i_entry)
g.append(f'<rect x="{lx:.1f}" y="{Y(TP):.1f}" width="{X1-lx:.1f}" height="{Y(ENTRY)-Y(TP):.1f}" fill="#2E7D96" fill-opacity="0.13"/>')
g.append(f'<rect x="{lx:.1f}" y="{Y(ENTRY):.1f}" width="{X1-lx:.1f}" height="{Y(SL)-Y(ENTRY):.1f}" fill="#D24B4B" fill-opacity="0.11"/>')
# return/order block zone (sweep..entry)
bx0=X(i_sweep)-10; bx1=X(i_entry)+10
g.append(f'<rect x="{bx0:.1f}" y="{Y(ENTRY+6):.1f}" width="{bx1-bx0:.1f}" height="{Y(SWEEP-4)-Y(ENTRY+6):.1f}" fill="#2E7D96" fill-opacity="0.16" stroke="#1E627A" stroke-width="1"/>')
# horizontal levels (thin, handle dots)
def hline(p,color,x0=X0,x1=X1,dash="6 7"):
    y=Y(p)
    g.append(f'<line x1="{x0}" y1="{y:.1f}" x2="{x1}" y2="{y:.1f}" stroke="{color}" stroke-width="1.7" stroke-dasharray="{dash}" stroke-linecap="round"/>')
    g.append(f'<circle cx="{x0}" cy="{y:.1f}" r="4.5" fill="{color}"/><circle cx="{x1}" cy="{y:.1f}" r="4.5" fill="{color}"/>')
hline(PRIOR_LOW,"#122F3E")           # prior liquidity (navy)
hline(BOS,"#2E7D96")                  # BOS (turquoise)
# entry/SL/TP solid-ish from entry bar
for p,c in [(ENTRY,"#1E627A"),(TP,"#2E8CA6"),(SL,"#D24B4B")]:
    y=Y(p); g.append(f'<line x1="{lx:.1f}" y1="{y:.1f}" x2="{X1}" y2="{y:.1f}" stroke="{c}" stroke-width="2"/>')
    g.append(f'<circle cx="{X1}" cy="{y:.1f}" r="4.5" fill="{c}"/>')
# price close line (navy) + nodes
pts=" ".join(f"{X(i):.1f},{Y(px[i]):.1f}" for i in range(N))
g.append(f'<polyline points="{pts}" fill="none" stroke="#0F2E3C" stroke-width="3" stroke-linejoin="round" stroke-linecap="round"/>')
for i in range(N):
    g.append(f'<circle cx="{X(i):.1f}" cy="{Y(px[i]):.1f}" r="3.2" fill="#0F2E3C"/>')
# highlight markers
g.append(f'<circle cx="{X(i_sweep):.1f}" cy="{Y(SWEEP):.1f}" r="9" fill="#D24B4B"/>')            # sweep (red)
g.append(f'<circle cx="{X(i_entry):.1f}" cy="{Y(ENTRY):.1f}" r="9" fill="#1E627A"/>')             # entry
g.append(f'<circle cx="{X(i_tp):.1f}" cy="{Y(TP):.1f}" r="10" fill="#2E8CA6"/>')                  # target
# BOS break arrow (touches the BOS line exactly)
ax=X(i_bos); ay0=Y(px[i_bos]); ay1=Y(BOS)
g.append(f'<line x1="{ax:.1f}" y1="{ay0+40:.1f}" x2="{ax:.1f}" y2="{ay1:.1f}" stroke="#2E7D96" stroke-width="3"/>')
g.append(f'<path d="M{ax-9:.1f},{ay1+13:.1f} L{ax:.1f},{ay1:.1f} L{ax+9:.1f},{ay1+13:.1f}" fill="none" stroke="#2E7D96" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>')
# target check
g.append(f'<path d="M{X(i_tp)-8:.1f},{Y(TP):.1f} l6,7 l12,-15" fill="none" stroke="#fff" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>')
SVG="".join(g)

# ---- HTML labels (cream halo, no boxes) at exact coords ----
def lbl(x,y,text,color,size=30,anchor="start",w=700):
    tx = "translateX(-100%)" if anchor=="end" else ("translateX(-50%)" if anchor=="mid" else "")
    return (f'<div class="lbl" style="left:{x:.0f}px; top:{y:.0f}px; color:{color}; '
            f'font-size:{size}px; font-weight:{w}; transform:{tx};">{text}</div>')
L=[]
L.append(lbl(X1-6, Y(PRIOR_LOW)-52, "سيولة سابقة", "#122F3E", 28, "end"))
L.append(lbl(X(i_sweep)-14, Y(SWEEP)+30, "سحب سيولة", "#D24B4B", 30, "end"))
L.append(lbl(X0+8, Y(BOS)-44, "تغيّر نمط", "#2E7D96", 30, "start"))
L.append(lbl(X(i_entry)-8, Y(ENTRY+6)+2, "منطقة الدخول", "#1E627A", 26, "end"))
L.append(lbl(X1-6, Y(TP)-44, "هدف  4176.39", "#1E627A", 30, "end"))
L.append(lbl(X1-6, Y(SL)+10, "ستوب  4005", "#D24B4B", 28, "end"))
L.append(lbl(X(i_bos)+14, Y(px[i_bos])+8, "كسر", "#2E7D96", 26, "start"))
LABELS="".join(L)

TAJ=open(os.path.join(os.path.dirname(__file__),"tajawal_embed.css"),encoding="utf-8").read()

# small silver icosahedron (reuse orientation from cover)
PHI=(1+5**0.5)/2
V=[(-1,PHI,0),(1,PHI,0),(-1,-PHI,0),(1,-PHI,0),(0,-1,PHI),(0,1,PHI),(0,-1,-PHI),(0,1,-PHI),(PHI,0,-1),(PHI,0,1),(-PHI,0,-1),(-PHI,0,1)]
FA=[(0,11,5),(0,5,1),(0,1,7),(0,7,10),(0,10,11),(1,5,9),(5,11,4),(11,10,2),(10,7,6),(7,1,8),(3,9,4),(3,4,2),(3,2,6),(3,6,8),(3,8,9),(4,9,5),(2,4,11),(6,2,10),(8,6,7),(9,8,1)]
def nrm(a):
    m=math.sqrt(sum(c*c for c in a))or 1;return(a[0]/m,a[1]/m,a[2]/m)
def sub(a,b):return(a[0]-b[0],a[1]-b[1],a[2]-b[2])
def add(a,b):return(a[0]+b[0],a[1]+b[1],a[2]+b[2])
def cr(a,b):return(a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
def dt(a,b):return a[0]*b[0]+a[1]*b[1]+a[2]*b[2]
def mv(M,v):return tuple(dt(M[i],v)for i in range(3))
def mm(A,B):
    Bt=list(zip(*B));return tuple(tuple(dt(A[i],Bt[j])for j in range(3))for i in range(3))
def rt(ax,an):
    x,y,z=nrm(ax);c=math.cos(an);s=math.sin(an);t=1-c
    return((t*x*x+c,t*x*y-s*z,t*x*z+s*y),(t*x*y+s*z,t*y*y+c,t*y*z-s*x),(t*x*z-s*y,t*y*z+s*x,t*z*z+c))
def al(a,b):
    a=nrm(a);b=nrm(b);v=cr(a,b);c=dt(a,b)
    if c>0.9999:return((1,0,0),(0,1,0),(0,0,1))
    if c<-0.9999:return rt((1,0,0),math.pi)
    return rt(v,math.acos(max(-1,min(1,c))))
R=al(nrm(add(add(V[0],V[11]),V[5])),(0,0,1));P=[mv(R,v)for v in V]
o=max(P,key=lambda p:p[0]**2+p[1]**2);R=mm(rt((0,0,1),math.pi/2-math.atan2(o[1],o[0])),R)
R=mm(rt((1,0,0),math.radians(-13)),R);P=[mv(R,v)for v in V]
def prj(p):return(140+p[0]*118,140-p[1]*118)
LI=nrm((-0.32,0.75,0.58))
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
    ff.append(((a[2]+b[2]+c[2])/3,tri,max(0,dt(nn,LI))))
ff.sort(key=lambda x:x[0]);pth=[]
for _,tri,sh in ff:
    d="M "+" L ".join(f"{prj(P[i])[0]:.1f},{prj(P[i])[1]:.1f}" for i in tri)+" Z"
    r,g_,b=sil(0.1+0.9*sh);pth.append(f'<path d="{d}" fill="rgb({r},{g_},{b})" stroke="#54687a" stroke-width="0.9" stroke-linejoin="round"/>')
LOGO=f'<svg viewBox="0 0 280 280" width="120" height="120" xmlns="http://www.w3.org/2000/svg">{"".join(pth)}</svg>'

HTML=f"""<!DOCTYPE html>
<html lang="ar" dir="rtl"><head><meta charset="UTF-8"/>
<title>Liquidity State — Educational Trade</title>
<meta name="hz:slide-selector" content=".slide"/><meta name="hz:canvas-width" content="1080"/><meta name="hz:canvas-height" content="1350"/>
<style>
{TAJ}
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{display:flex;justify-content:center;align-items:center;min-height:100vh;background:#ddd;}}
.slide{{position:relative;width:1080px;height:1350px;overflow:hidden;font-family:'Tajawal',sans-serif;
  color:#0F2E3C;background:radial-gradient(120% 90% at 50% 30%, #F7F3EC 0%, #F2EEE7 55%, #ECE6DB 100%);}}
.chip-tr{{position:absolute;top:44px;right:56px;padding:10px 24px;border:1.5px solid rgba(46,125,150,0.5);
  border-radius:4px;font-size:28px;font-weight:700;letter-spacing:1px;color:#1E627A;direction:ltr;}}
.logo{{position:absolute;left:50%;top:118px;transform:translate(-50%,-50%);filter:drop-shadow(0 6px 14px rgba(15,46,60,0.18));}}
.wm{{position:absolute;left:0;right:0;top:196px;text-align:center;font-weight:700;font-size:34px;letter-spacing:11px;color:#3d5560;direction:ltr;}}
.uline{{position:absolute;left:50%;top:244px;transform:translateX(-50%);width:300px;height:1.5px;background:linear-gradient(90deg,rgba(46,125,150,0),rgba(46,125,150,0.8),rgba(46,125,150,0));}}
.sec{{position:absolute;left:50%;top:286px;transform:translateX(-50%);display:flex;align-items:center;gap:18px;color:#2E7D96;font-size:30px;font-weight:700;white-space:nowrap;}}
.sec i{{width:54px;height:2px;background:linear-gradient(90deg,rgba(46,125,150,0),rgba(46,125,150,0.9));}}
.title{{position:absolute;left:0;right:0;top:330px;text-align:center;font-size:82px;font-weight:900;color:#0F2E3C;line-height:1.1;}}
.subt{{position:absolute;left:0;right:0;top:452px;text-align:center;font-size:34px;font-weight:500;color:#5C6C73;}}
.plot{{position:absolute;left:0;top:0;}}
.lbl{{position:absolute;white-space:nowrap;font-family:'Tajawal',sans-serif;
  text-shadow:0 0 6px #F4EFE6,0 0 6px #F4EFE6,2px 2px 5px #F4EFE6,-2px -2px 5px #F4EFE6,2px -2px 5px #F4EFE6,-2px 2px 5px #F4EFE6;}}
.result{{position:absolute;left:50%;top:1108px;transform:translateX(-50%);display:flex;align-items:center;gap:26px;
  padding:20px 40px;border:1.5px solid rgba(46,125,150,0.45);border-radius:3px;background:rgba(46,140,166,0.10);white-space:nowrap;}}
.result .tick{{font-size:40px;color:#2E8CA6;font-weight:900;}}
.result .t{{font-size:40px;font-weight:800;color:#0F2E3C;}}
.result .v{{font-size:38px;font-weight:800;color:#1E627A;direction:ltr;font-style:italic;}}
.cta{{position:absolute;left:50%;top:1206px;transform:translateX(-50%);display:flex;align-items:center;gap:16px;
  padding:16px 40px;border-radius:3px;background:#0F2E3C;color:#EAF6F8;font-size:32px;font-weight:700;white-space:nowrap;}}
.cta b{{color:#5AA6BC;}}
.foot{{position:absolute;left:0;right:0;bottom:34px;text-align:center;font-size:24px;font-weight:500;color:#7C8A90;}}
</style></head>
<body>
<div class="slide" data-canvas-width="1080" data-canvas-height="1350">
  <div class="chip-tr">XAUUSD · يومي</div>
  <div class="logo">{LOGO}</div>
  <div class="wm">LIQUIDITY&nbsp;&nbsp;STATE</div>
  <div class="uline"></div>
  <div class="sec"><i></i>صفقة موثقة<i style="transform:scaleX(-1)"></i></div>
  <div class="title">الدخول من سحب السيولة</div>
  <div class="subt">سحب السيولة ← تغيّر النمط ← الدخول من البلوك ← الهدف</div>
  <svg class="plot" width="1080" height="1350" viewBox="0 0 1080 1350" xmlns="http://www.w3.org/2000/svg">{SVG}</svg>
  {LABELS}
  <div class="result"><span class="tick">✓</span><span class="t">وصل الهدف</span><span class="v">+$133.76&nbsp;&nbsp;·&nbsp;&nbsp;RR 1:3.5</span></div>
  <div class="cta">للملف كامل خطوة خطوة اكتب <b>بلوك</b> بالتعليقات</div>
  <div class="foot">لغرض تعليمي — إغلاقات XAUUSD يومية حقيقية · المصدر: Alpha Vantage · يونيو–يوليو 2026</div>
</div>
</body></html>"""

out=os.path.join(os.path.dirname(__file__),"trade.html")
open(out,"w",encoding="utf-8").write(HTML)
print("wrote",out,f"| N={N} entry={ENTRY} SL={SL} TP={TP} RR={RR:.2f} reward=${reward:.2f}")
