#!/usr/bin/env python3
"""Liquidity State REEL cover (1080x1920), matched to the account's dark template.
- Geometrically-computed icosahedron (12 golden-ratio verts, 20 faces), oriented down a
  3-fold axis for a clean hexagonal point-up silhouette, metallic silver shading. No simplified logo.
- Tajawal embedded base64 (tajawal_embed.css). Faint candles + guilloche texture background.
"""
import math, os, base64

PHI = (1 + 5 ** 0.5) / 2
V = [(-1,PHI,0),(1,PHI,0),(-1,-PHI,0),(1,-PHI,0),(0,-1,PHI),(0,1,PHI),
     (0,-1,-PHI),(0,1,-PHI),(PHI,0,-1),(PHI,0,1),(-PHI,0,-1),(-PHI,0,1)]
F = [(0,11,5),(0,5,1),(0,1,7),(0,7,10),(0,10,11),(1,5,9),(5,11,4),(11,10,2),
     (10,7,6),(7,1,8),(3,9,4),(3,4,2),(3,2,6),(3,6,8),(3,8,9),(4,9,5),
     (2,4,11),(6,2,10),(8,6,7),(9,8,1)]

def nrm(a):
    m=math.sqrt(sum(c*c for c in a)) or 1.0; return (a[0]/m,a[1]/m,a[2]/m)
def sub(a,b): return (a[0]-b[0],a[1]-b[1],a[2]-b[2])
def add(a,b): return (a[0]+b[0],a[1]+b[1],a[2]+b[2])
def cross(a,b): return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
def dot(a,b): return a[0]*b[0]+a[1]*b[1]+a[2]*b[2]
def matvec(M,v): return tuple(dot(M[i],v) for i in range(3))
def matmul(A,B):
    Bt=list(zip(*B)); return tuple(tuple(dot(A[i],Bt[j]) for j in range(3)) for i in range(3))
def rot(axis,ang):
    x,y,z=nrm(axis); c=math.cos(ang); s=math.sin(ang); t=1-c
    return ((t*x*x+c,t*x*y-s*z,t*x*z+s*y),
            (t*x*y+s*z,t*y*y+c,t*y*z-s*x),
            (t*x*z-s*y,t*y*z+s*x,t*z*z+c))
def align(a,b):  # rotation mapping unit a -> unit b
    a=nrm(a); b=nrm(b); v=cross(a,b); c=dot(a,b)
    if c<-0.9999: return rot((1,0,0),math.pi)
    if c> 0.9999: return ((1,0,0),(0,1,0),(0,0,1))
    return rot(v,math.acos(max(-1,min(1,c))))

# 1) align a 3-fold axis (face-0 centroid) to +z  -> hexagonal silhouette
axis3=nrm(add(add(V[0],V[11]),V[5]))
R=align(axis3,(0,0,1))
P=[matvec(R,v) for v in V]
# 2) spin about z so a silhouette vertex points up
outer=max(P,key=lambda p:p[0]*p[0]+p[1]*p[1])
spin=math.pi/2-math.atan2(outer[1],outer[0])
R=matmul(rot((0,0,1),spin),R)
# 3) slight tilt for crystalline depth
R=matmul(rot((1,0,0),math.radians(-13)),R)
P=[matvec(R,v) for v in V]

VB=560; C=VB/2; S=205
def proj(p): return (C+p[0]*S, C-p[1]*S)
LIGHT=nrm((-0.32,0.75,0.58))
def silver(t):
    st=[(0.0,(52,68,84)),(0.4,(120,143,159)),(0.72,(190,206,214)),(1.0,(246,250,253))]
    for i in range(len(st)-1):
        t0,c0=st[i]; t1,c1=st[i+1]
        if t<=t1:
            f=(t-t0)/(t1-t0) if t1>t0 else 0
            return tuple(round(c0[k]+(c1[k]-c0[k])*f) for k in range(3))
    return st[-1][1]
faces=[]
for tri in F:
    a,b,c=(P[i] for i in tri)
    n=nrm(cross(sub(b,a),sub(c,a)))
    if n[2]<=0.03: continue
    sh=max(0.0,dot(n,LIGHT)); dep=(a[2]+b[2]+c[2])/3
    faces.append((dep,tri,sh))
faces.sort(key=lambda f:f[0])
paths=[]
for dep,tri,sh in faces:
    pts=[proj(P[i]) for i in tri]
    d="M "+" L ".join(f"{x:.2f},{y:.2f}" for x,y in pts)+" Z"
    r,g,b=silver(0.10+0.90*sh)
    paths.append(f'<path d="{d}" fill="rgb({r},{g},{b})" stroke="#54687a" stroke-width="1" stroke-linejoin="round"/>')
LOGO=(f'<svg viewBox="0 0 {VB} {VB}" width="300" height="300" xmlns="http://www.w3.org/2000/svg" '
      f'aria-label="Liquidity State icosahedron">'+"".join(paths)+'</svg>')

# --- faint candlesticks (deterministic pseudo-random walk) ---
def candles():
    seed=1234567; px=1180.0; out=[]; x=690
    for i in range(16):
        seed=(1103515245*seed+12345)%2147483648; r=(seed/2147483648)-0.5
        o=px; px=px+r*14; cl=px
        seed=(1103515245*seed+12345)%2147483648; wick=abs((seed/2147483648))*10+3
        hi=max(o,cl)+wick; lo=min(o,cl)-wick
        up=cl>=o; col="#2E8CA6" if up else "#16333f"
        def Y(v): return 1180-(v-1120)*7.0
        yo,yc,yh,yl=Y(o),Y(cl),Y(hi),Y(lo)
        top=min(yo,yc); h=max(4,abs(yc-yo))
        out.append(f'<line x1="{x+9}" y1="{yh:.1f}" x2="{x+9}" y2="{yl:.1f}" stroke="{col}" stroke-width="2"/>')
        out.append(f'<rect x="{x}" y="{top:.1f}" width="18" height="{h:.1f}" fill="{col}"/>')
        x+=26
    return "".join(out)
CANDLES=candles()

TAJ=open(os.path.join(os.path.dirname(__file__),"tajawal_embed.css"),encoding="utf-8").read()

def icon(kind):
    if kind=="liq":  # liquidity sweep — droplet
        return ('<path d="M32 8 C32 8 50 30 50 42 a18 18 0 0 1 -36 0 C14 30 32 8 32 8 Z" '
                'fill="none" stroke="#5AA6BC" stroke-width="3"/>'
                '<path d="M24 40 a8 8 0 0 0 8 8" fill="none" stroke="#5AA6BC" stroke-width="3" stroke-linecap="round"/>')
    if kind=="choch":  # change of pattern — zigzag + up arrow
        return ('<polyline points="8,48 20,34 30,44 44,20 56,30" fill="none" stroke="#5AA6BC" '
                'stroke-width="3" stroke-linejoin="round" stroke-linecap="round"/>'
                '<path d="M44 20 l12 0 l0 12" fill="none" stroke="#5AA6BC" stroke-width="3" stroke-linecap="round"/>')
    # block — box
    return ('<rect x="14" y="18" width="36" height="28" fill="none" stroke="#5AA6BC" stroke-width="3"/>'
            '<line x1="14" y1="30" x2="50" y2="30" stroke="#5AA6BC" stroke-width="2"/>')

def icon_svg(kind):
    return (f'<svg viewBox="0 0 64 64" width="64" height="64" xmlns="http://www.w3.org/2000/svg">{icon(kind)}</svg>')

BOTTOM = ""
items=[("liq","سحب السيولة"),("choch","تغيّر النمط"),("block","البلوك")]
cells=[]
for k,lbl in items:
    cells.append(f'<div class="bcell"><div class="bic">{icon_svg(k)}</div><div class="blbl">{lbl}</div></div>')
BOTTOM='<div class="bdivider"></div>'.join(cells)

HTML=f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8" />
<title>Liquidity State — Reel Cover</title>
<meta name="hz:slide-selector" content=".poster" />
<meta name="hz:canvas-width" content="1080" />
<meta name="hz:canvas-height" content="1920" />
<style>
{TAJ}
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ display:flex; justify-content:center; align-items:center; min-height:100vh; background:#05090d; }}
.poster {{ position:relative; width:1080px; height:1920px; overflow:hidden; font-family:'Tajawal',sans-serif;
  color:#fff; background:radial-gradient(125% 78% at 50% 30%, #102833 0%, #0A1721 46%, #050C13 78%, #03080d 100%); }}
.tex {{ position:absolute; inset:0; opacity:0.5; }}
.cand {{ position:absolute; right:-10px; top:120px; opacity:0.20; }}
.vig {{ position:absolute; inset:0; background:radial-gradient(120% 70% at 50% 32%, rgba(0,0,0,0) 40%, rgba(2,7,12,0.55) 100%); }}
.chip-tr {{ position:absolute; top:70px; right:70px; padding:12px 26px; border:1.5px solid rgba(90,166,188,0.55);
  border-radius:4px; font-size:34px; font-weight:700; letter-spacing:2px; color:#9fd2de; direction:ltr;
  background:rgba(46,140,166,0.10); }}
.logo {{ position:absolute; left:50%; top:300px; transform:translate(-50%,-50%);
  filter:drop-shadow(0 0 30px rgba(67,212,220,0.5)) drop-shadow(0 12px 30px rgba(0,0,0,0.55)); }}
.gdot {{ position:absolute; left:50%; top:430px; transform:translate(-50%,-50%); width:16px; height:16px;
  background:#43D4DC; border-radius:50%; box-shadow:0 0 26px 8px rgba(67,212,220,0.8); }}
.wordmark {{ position:absolute; left:0; right:0; top:492px; text-align:center; font-weight:700;
  font-size:52px; letter-spacing:18px; color:#C4D4DB; direction:ltr; text-shadow:0 0 16px rgba(196,212,219,0.28); }}
.uline {{ position:absolute; left:50%; top:582px; transform:translateX(-50%); width:430px; height:1.5px;
  background:linear-gradient(90deg, rgba(67,212,220,0) 0%, rgba(67,212,220,0.85) 50%, rgba(67,212,220,0) 100%); }}
.rh {{ position:absolute; left:50%; transform:translate(-50%,-50%) rotate(45deg); width:14px; height:14px;
  background:#43D4DC; box-shadow:0 0 16px 3px rgba(67,212,220,0.8); }}
.plabel {{ position:absolute; left:50%; top:660px; transform:translateX(-50%); display:flex; align-items:center;
  gap:22px; color:#5AA6BC; font-size:36px; font-weight:700; white-space:nowrap; }}
.plabel .ar {{ width:70px; height:2px; background:linear-gradient(90deg,rgba(90,166,188,0),rgba(90,166,188,0.9)); position:relative; }}
.plabel .ar::after {{ content:''; position:absolute; width:9px; height:9px; border-top:2px solid #5AA6BC; border-right:2px solid #5AA6BC; }}
.plabel .arL {{ top:-4px; right:0; transform:rotate(45deg); }}
.plabel .arR {{ top:-4px; left:0; transform:rotate(-135deg); }}
.title {{ position:absolute; left:0; right:0; top:760px; text-align:center; font-weight:900; line-height:1.12;
  font-size:126px; letter-spacing:0.5px;
  background:linear-gradient(180deg,#ffffff 0%, #C4D4DB 52%, #7F97A1 100%);
  -webkit-background-clip:text; background-clip:text; -webkit-text-fill-color:transparent;
  filter:drop-shadow(0 3px 12px rgba(0,0,0,0.5)); }}
.subt {{ position:absolute; left:0; right:0; top:1055px; text-align:center; font-size:46px; font-weight:500; color:#8fb3bf; }}
.result {{ position:absolute; left:50%; top:1180px; transform:translateX(-50%); width:800px;
  display:flex; flex-direction:column; align-items:center; gap:14px; padding:32px 40px;
  border:1.5px solid rgba(67,212,220,0.5); border-radius:3px; background:rgba(46,140,166,0.13); }}
.result .l1 {{ display:flex; align-items:center; justify-content:center; gap:18px; white-space:nowrap; }}
.result .tick {{ font-size:46px; color:#43D4DC; font-weight:900; }}
.result .txt {{ font-size:52px; font-weight:800; color:#EAF6F8; }}
.result .num {{ font-size:42px; font-weight:800; color:#9fd8e0; font-style:italic; direction:ltr; }}
.edu {{ position:absolute; left:50%; top:1420px; transform:translateX(-50%); font-size:32px; font-weight:500;
  color:#7F97A1; white-space:nowrap; }}
.bottom {{ position:absolute; left:50%; bottom:120px; transform:translateX(-50%); display:flex; align-items:center; gap:0; }}
.bcell {{ display:flex; flex-direction:column; align-items:center; gap:16px; width:290px; }}
.bic {{ opacity:0.95; }}
.blbl {{ font-size:38px; font-weight:700; color:#cfe4ea; }}
.bdivider {{ width:1.5px; height:150px; background:linear-gradient(180deg,rgba(90,166,188,0),rgba(90,166,188,0.5),rgba(90,166,188,0)); }}
.wm2 {{ position:absolute; left:0; right:0; bottom:66px; text-align:center; font-size:26px; letter-spacing:8px;
  color:#5f7681; direction:ltr; }}
</style>
</head>
<body>
<div class="poster" data-canvas-width="1080" data-canvas-height="1920">
  <svg class="tex" viewBox="0 0 1080 1920" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="none">
    <g stroke="#2E7D96" stroke-width="1" fill="none" opacity="0.10">
      <ellipse cx="150" cy="560" rx="230" ry="230"/><ellipse cx="150" cy="560" rx="185" ry="205"/>
      <ellipse cx="150" cy="560" rx="140" ry="180"/><ellipse cx="150" cy="560" rx="95" ry="150"/>
      <ellipse cx="960" cy="1500" rx="230" ry="230"/><ellipse cx="960" cy="1500" rx="185" ry="205"/>
      <ellipse cx="960" cy="1500" rx="140" ry="180"/>
    </g>
  </svg>
  <svg class="cand" width="470" height="360" viewBox="0 0 470 360" xmlns="http://www.w3.org/2000/svg">{CANDLES}</svg>
  <div class="vig"></div>

  <div class="chip-tr">XAUUSD</div>
  <div class="logo">{LOGO}</div>
  <div class="gdot"></div>
  <div class="wordmark">LIQUIDITY&nbsp;&nbsp;STATE</div>
  <div class="uline"></div>
  <div class="rh" style="left:50%; top:582px;"></div>

  <div class="plabel"><span class="ar"><i class="arL"></i></span>طريقة الدخول<span class="ar"><i class="arR"></i></span></div>

  <div class="title">البلوك اللي<br/>يرجّع السعر</div>
  <div class="subt">دخول SMC خطوة خطوة على شارت واحد</div>

  <div class="result">
    <div class="l1"><span class="tick">✓</span><span class="txt">الصفقة وصلت الهدف</span></div>
    <span class="num">+___ نقطة</span>
  </div>
  <div class="edu">صفقة موثقة — لغرض تعليمي</div>

  <div class="bottom">{BOTTOM}</div>
</div>
</body>
</html>"""

out=os.path.join(os.path.dirname(__file__),"cover.html")
open(out,"w",encoding="utf-8").write(HTML)
print("wrote",out,"| faces",len(faces))
