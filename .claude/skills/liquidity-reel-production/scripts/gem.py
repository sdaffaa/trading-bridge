# -*- coding: utf-8 -*-
import math
phi=(1+5**0.5)/2
V=[(0,1,phi),(0,1,-phi),(0,-1,phi),(0,-1,-phi),
   (1,phi,0),(1,-phi,0),(-1,phi,0),(-1,-phi,0),
   (phi,0,1),(phi,0,-1),(-phi,0,1),(-phi,0,-1)]
def d2(a,b): return sum((a[i]-b[i])**2 for i in range(3))
mind=min(d2(V[i],V[j]) for i in range(12) for j in range(i+1,12))
FACES=[]
for i in range(12):
    for j in range(i+1,12):
        for k in range(j+1,12):
            if abs(d2(V[i],V[j])-mind)<1e-6 and abs(d2(V[j],V[k])-mind)<1e-6 and abs(d2(V[i],V[k])-mind)<1e-6:
                FACES.append((i,j,k))

def matmul(m,v): return (sum(m[0][i]*v[i] for i in range(3)),sum(m[1][i]*v[i] for i in range(3)),sum(m[2][i]*v[i] for i in range(3)))
def rot(rx,ry,rz):
    cx,sx=math.cos(rx),math.sin(rx); cy,sy=math.cos(ry),math.sin(ry); cz,sz=math.cos(rz),math.sin(rz)
    Rx=[[1,0,0],[0,cx,-sx],[0,sx,cx]]; Ry=[[cy,0,sy],[0,1,0],[-sy,0,cy]]; Rz=[[cz,-sz,0],[sz,cz,0],[0,0,1]]
    def mm(A,B): return [[sum(A[r][t]*B[t][c] for t in range(3)) for c in range(3)] for r in range(3)]
    return mm(mm(Rz,Ry),Rx)

def norm(v):
    m=math.sqrt(sum(c*c for c in v)) or 1; return (v[0]/m,v[1]/m,v[2]/m)
def sub(a,b): return (a[0]-b[0],a[1]-b[1],a[2]-b[2])
def cross(a,b): return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
def dot(a,b): return sum(a[i]*b[i] for i in range(3))

def build_gem(rx,ry,rz,size=48,pad=3,light=(-0.35,0.72,0.6),edge="#5b7480",edgew=0.35,gid="gm"):
    R=rot(rx,ry,rz)
    RV=[matmul(R,v) for v in V]
    L=norm(light)
    tris=[]
    for (i,j,k) in FACES:
        a,b,c=RV[i],RV[j],RV[k]
        n=norm(cross(sub(b,a),sub(c,a)))
        # ensure normal points outward (away from origin ~ centroid direction)
        cen=((a[0]+b[0]+c[0])/3,(a[1]+b[1]+c[1])/3,(a[2]+b[2]+c[2])/3)
        if dot(n,cen)<0: n=(-n[0],-n[1],-n[2])
        if n[2]<=0.02: continue  # cull back faces (viewer +z)
        inten=0.28+0.72*max(0.0,dot(n,L))
        cz=(a[2]+b[2]+c[2])/3
        tris.append((cz,inten,(a,b,c)))
    tris.sort(key=lambda t:t[0])  # back to front
    xs=[p[0] for _,_,tri in tris for p in tri]; ys=[p[1] for _,_,tri in tris for p in tri]
    minx,maxx,miny,maxy=min(xs),max(xs),min(ys),max(ys)
    sc=(size-2*pad)/max(maxx-minx,maxy-miny)
    cx=(size)/2-(minx+maxx)/2*sc; cy=(size)/2+(miny+maxy)/2*sc
    def P(p): return (cx+p[0]*sc, cy-p[1]*sc)
    def shade(t):
        c0=(84,104,115); c1=(240,246,249)
        return "#%02x%02x%02x"%tuple(int(c0i+(c1i-c0i)*t) for c0i,c1i in zip(c0,c1))
    out=[f'<svg viewBox="0 0 {size} {size}" width="100%" height="100%" xmlns="http://www.w3.org/2000/svg">']
    for _,inten,tri in tris:
        pts=" ".join(f"{P(p)[0]:.2f},{P(p)[1]:.2f}" for p in tri)
        out.append(f'<polygon points="{pts}" fill="{shade(inten)}" stroke="{edge}" stroke-width="{edgew}" stroke-linejoin="round"/>')
    out.append('</svg>')
    return "".join(out)

if __name__=="__main__":
    import os
    HERE=os.path.dirname(os.path.abspath(__file__))
    # try several orientations
    presets={
      "facefwd":(math.radians(37),math.radians(0),0),         # ~3-fold face forward
      "vertexup":(math.radians(31.7),math.radians(0),0),      # vertex up (5-fold-ish)
      "edgefwd":(math.radians(0),math.radians(0),0),
      "brandish":(math.radians(20),math.radians(18),math.radians(0)),
      "tiltA":(math.radians(52),math.radians(0),0),
      "tiltB":(math.radians(-58),math.radians(0),0),
    }
    cells=""
    for name,(a,b,c) in presets.items():
        g=build_gem(a,b,c)
        cells+=f'<div style="text-align:center"><div style="width:220px;height:220px;margin:auto">{g}</div><div style="color:#9fb4bc;font:20px sans-serif">{name}</div></div>'
    html=f'<!DOCTYPE html><html><head><meta charset="utf-8"></head><body style="margin:0;background:#0A1620;display:flex;flex-wrap:wrap;gap:20px;padding:30px;justify-content:center">{cells}</body></html>'
    open(os.path.join(HERE,"gem_test.html"),"w").write(html)
    print("wrote gem_test.html with",len(presets),"orientations; faces:",len(FACES))
