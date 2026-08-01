#!/usr/bin/env python3
"""Generate the Liquidity State dark cover poster (1080x1920) as self-contained HTML.
The logo is a geometrically-computed icosahedron (12 golden-ratio verts, 20 faces,
metallic silver shading by face normal). No simplified logo — per brand rule."""
import math

PHI = (1 + 5 ** 0.5) / 2

# 12 icosahedron vertices
V = [
    (-1,  PHI, 0), ( 1,  PHI, 0), (-1, -PHI, 0), ( 1, -PHI, 0),
    (0, -1,  PHI), (0,  1,  PHI), (0, -1, -PHI), (0,  1, -PHI),
    ( PHI, 0, -1), ( PHI, 0,  1), (-PHI, 0, -1), (-PHI, 0,  1),
]
# 20 triangular faces
F = [
    (0,11,5),(0,5,1),(0,1,7),(0,7,10),(0,10,11),
    (1,5,9),(5,11,4),(11,10,2),(10,7,6),(7,1,8),
    (3,9,4),(3,4,2),(3,2,6),(3,6,8),(3,8,9),
    (4,9,5),(2,4,11),(6,2,10),(8,6,7),(9,8,1),
]

def rot_x(p, a):
    x, y, z = p; c, s = math.cos(a), math.sin(a)
    return (x, y * c - z * s, y * s + z * c)
def rot_y(p, a):
    x, y, z = p; c, s = math.cos(a), math.sin(a)
    return (x * c + z * s, y, -x * s + z * c)
def sub(a, b): return (a[0]-b[0], a[1]-b[1], a[2]-b[2])
def cross(a, b): return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])
def norm(a):
    m = math.sqrt(sum(c*c for c in a)) or 1.0
    return (a[0]/m, a[1]/m, a[2]/m)

# Orientation: point-up gem, brand rx=54deg
RY, RX = math.radians(31.7), math.radians(54)
P = [rot_x(rot_y(v, RY), RX) for v in V]

SCALE, CX, CY = 190, 0, 0  # projected into a 520x520 viewBox, centered at 260,260
VB = 520; C = VB / 2
def proj(p): return (C + p[0]*SCALE, C - p[1]*SCALE)  # y-up

LIGHT = norm((-0.35, 0.72, 0.6))  # upper-left key light

faces = []
for tri in F:
    a, b, c = (P[i] for i in tri)
    n = norm(cross(sub(b, a), sub(c, a)))
    if n[2] <= 0.02:      # back-face cull
        continue
    shade = max(0.0, n[0]*LIGHT[0] + n[1]*LIGHT[1] + n[2]*LIGHT[2])
    depth = (a[2] + b[2] + c[2]) / 3
    faces.append((depth, tri, shade))
faces.sort(key=lambda f: f[0])  # painter's: far first

def silver(t):
    # t in [0,1] -> metallic silver ramp (dark steel -> bright silver -> white highlight)
    stops = [(0.0,(58,74,90)),(0.45,(129,151,166)),(0.8,(196,212,219)),(1.0,(244,249,252))]
    for i in range(len(stops)-1):
        t0,c0 = stops[i]; t1,c1 = stops[i+1]
        if t <= t1:
            f = (t-t0)/(t1-t0) if t1>t0 else 0
            return tuple(round(c0[k]+(c1[k]-c0[k])*f) for k in range(3))
    return stops[-1][1]

paths = []
for depth, tri, shade in faces:
    pts = [proj(P[i]) for i in tri]
    d = "M " + " L ".join(f"{x:.2f},{y:.2f}" for x, y in pts) + " Z"
    r, g, b = silver(0.12 + 0.88 * shade)
    paths.append(f'<path d="{d}" fill="rgb({r},{g},{b})" stroke="#54687a" '
                 f'stroke-width="1.1" stroke-linejoin="round"/>')

logo_svg = (f'<svg viewBox="0 0 {VB} {VB}" width="360" height="360" '
            f'xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Liquidity State icosahedron">'
            + "".join(paths) + "</svg>")

HTML = f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8" />
<title>Liquidity State — Reel Cover</title>
<meta name="hz:slide-selector" content=".poster" />
<meta name="hz:canvas-width" content="1080" />
<meta name="hz:canvas-height" content="1920" />
<style>
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700;800;900&display=swap');
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ display:flex; justify-content:center; align-items:center; min-height:100vh; background:#05090d; }}
.poster {{
  position:relative; width:1080px; height:1920px; overflow:hidden;
  font-family:'Tajawal',sans-serif; color:#fff;
  background:radial-gradient(120% 80% at 50% 34%, #0C2029 0%, #08131C 55%, #04090F 100%);
}}
.glow {{ position:absolute; left:50%; top:30%; width:820px; height:820px; transform:translate(-50%,-50%);
  background:radial-gradient(circle, rgba(67,212,220,0.28) 0%, rgba(67,212,220,0.10) 38%, rgba(67,212,220,0) 68%);
  filter:blur(2px); }}
.logo {{ position:absolute; left:50%; top:30%; transform:translate(-50%,-50%);
  filter:drop-shadow(0 0 26px rgba(67,212,220,0.55)) drop-shadow(0 10px 30px rgba(0,0,0,0.55)); }}
.rhombus {{ position:absolute; left:50%; transform:translate(-50%,0) rotate(45deg);
  width:16px; height:16px; background:#43D4DC; box-shadow:0 0 18px 4px rgba(67,212,220,0.75); }}
.rhombus.a {{ top:absolute; }}
.divider {{ position:absolute; left:50%; transform:translateX(-50%); width:520px; height:1.5px;
  background:linear-gradient(90deg, rgba(67,212,220,0) 0%, rgba(67,212,220,0.9) 50%, rgba(67,212,220,0) 100%); }}
.title {{ position:absolute; left:0; right:0; text-align:center; font-weight:900; line-height:1.12;
  font-size:120px; letter-spacing:1px;
  background:linear-gradient(180deg,#ffffff 0%, #C4D4DB 55%, #7F97A1 100%);
  -webkit-background-clip:text; background-clip:text; -webkit-text-fill-color:transparent;
  filter:drop-shadow(0 2px 10px rgba(0,0,0,0.5)); }}
.result {{ position:absolute; left:50%; transform:translateX(-50%); width:780px;
  display:flex; flex-direction:column; align-items:center; gap:14px; padding:34px 40px;
  border:1.5px solid rgba(67,212,220,0.55); border-radius:2px;
  background:rgba(46,140,166,0.14); }}
.result .line1 {{ display:flex; align-items:center; justify-content:center; gap:18px; white-space:nowrap; }}
.result .tick {{ font-size:48px; color:#43D4DC; font-weight:900; }}
.result .txt {{ font-size:54px; font-weight:800; color:#EAF6F8; }}
.result .num {{ font-size:44px; font-weight:800; color:#9fd8e0; font-style:italic; direction:ltr; }}
.edu {{ position:absolute; left:50%; transform:translateX(-50%); font-size:32px; font-weight:500;
  color:#7F97A1; letter-spacing:0.5px; white-space:nowrap; }}
.wordmark {{ position:absolute; left:0; right:0; bottom:96px; text-align:center; font-weight:700;
  font-size:44px; letter-spacing:16px; color:#C4D4DB;
  text-shadow:0 0 14px rgba(196,212,219,0.25); }}
.wordmark span {{ display:inline-block; }}
</style>
</head>
<body>
<div class="poster" data-canvas-width="1080" data-canvas-height="1920">
  <div class="glow"></div>
  <div class="logo">{logo_svg}</div>

  <div class="rhombus" style="top:648px;"></div>
  <div class="divider" style="top:700px;"></div>

  <div class="title" style="top:770px;">البلوك اللي<br/>يرجّع السعر</div>

  <div class="result" style="top:1110px;">
    <div class="line1">
      <span class="tick">✓</span>
      <span class="txt">الصفقة وصلت الهدف</span>
    </div>
    <span class="num">+___ نقطة</span>
  </div>
  <div class="edu" style="top:1340px;">صفقة موثقة — لغرض تعليمي</div>

  <div class="divider" style="top:1440px;"></div>
  <div class="rhombus" style="top:1432px;"></div>

  <div class="wordmark"><span>LIQUIDITY&nbsp;&nbsp;STATE</span></div>
</div>
</body>
</html>"""

import os
out = os.path.join(os.path.dirname(__file__), "cover.html")
with open(out, "w", encoding="utf-8") as f:
    f.write(HTML)
print("wrote", out, "| visible faces:", len(faces))
