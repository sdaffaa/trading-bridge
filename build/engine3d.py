"""
Cinematic perspective 3D renderer for the reel.
Real 3D: extruded candlesticks (6-face boxes, lit + shaded), a perspective floor
grid, contact shadows, depth fog, and a pinhole camera you dolly/truck/pedestal.
Pure Python/Pillow + numpy — deterministic, no GPU.
"""
import math, numpy as np
from PIL import Image, ImageDraw, ImageFilter
from engine import (W,H, NEARWHITE,SILVER,GOLD,TEAL,RED,BLACK, font,FA,FL,FL_BLACK,
                    CANDLES,META,LV,IDX, clamp,lerp)

N=META["n"]; PTOP=META["price_top"]; PBOT=META["price_bot"]
PMID=(PTOP+PBOT)/2
DX=0.52                      # world spacing between candles (X)
PYS=13.0/(PTOP-PBOT)         # price -> world Y scale (range -> ~13 units tall)
BW=DX*0.62                   # body width (X)
BD=DX*0.62                   # body depth (Z)
WW=DX*0.16                   # wick width/depth
FLOOR_Y=-(PMID-PBOT)*PYS-1.4 # floor a bit under the lowest price
LIGHT=np.array([-0.45,0.92,0.55]); LIGHT/=np.linalg.norm(LIGHT)
BG_TOP=(9,12,17); BG_BOT=(6,8,11); FOG=(9,12,17)

def X(i):  return (i-(N-1)/2)*DX
def Yp(p): return (p-PMID)*PYS

class Cam:
    def __init__(self, eye, target, fov_deg=34.0, up=(0,1,0)):
        self.eye=np.array(eye,float); self.t=np.array(target,float)
        f=self.t-self.eye; f/=np.linalg.norm(f)
        r=np.cross(f,np.array(up,float)); r/=np.linalg.norm(r)
        u=np.cross(r,f)
        self.f,self.r,self.u=f,r,u
        self.foc=(0.5*H)/math.tan(math.radians(fov_deg)/2)
    def project(self, P):
        P=np.atleast_2d(P).astype(float); rel=P-self.eye
        cz=rel@self.f; cx=rel@self.r; cy=rel@self.u
        cz=np.where(np.abs(cz)<1e-3,1e-3,cz)
        sx=W/2+self.foc*cx/cz; sy=H/2-self.foc*cy/cz
        return np.stack([sx,sy],1), cz
    def dist(self, P): return np.linalg.norm(np.array(P,float)-self.eye)

def _shade(base, normal, fogf):
    d=0.34+0.72*max(0.0,float(normal@LIGHT))
    col=[clamp(base[k]*d,0,255) for k in range(3)]
    col=[lerp(col[k],FOG[k],fogf) for k in range(3)]
    return tuple(int(c) for c in col)

def _box(cam, x0,x1,y0,y1,z0,z1, base, draw, fogf, edge=None):
    V=np.array([[x0,y0,z0],[x1,y0,z0],[x1,y1,z0],[x0,y1,z0],
                [x0,y0,z1],[x1,y0,z1],[x1,y1,z1],[x0,y1,z1]],float)
    scr,cz=cam.project(V)
    faces=[(0,1,2,3,(0,0,-1)),(4,5,6,7,(0,0,1)),(0,1,5,4,(0,-1,0)),
           (3,2,6,7,(0,1,0)),(1,2,6,5,(1,0,0)),(0,3,7,4,(-1,0,0))]
    items=[]
    cen=V.mean(0)
    for a,b,c,d,nrm in faces:
        nrm=np.array(nrm,float)
        fcen=V[[a,b,c,d]].mean(0)
        if (cam.eye-fcen)@nrm<=0: continue        # back-face cull
        depth=(cz[a]+cz[b]+cz[c]+cz[d])/4
        items.append((depth,[a,b,c,d],nrm))
    items.sort(key=lambda t:-t[0])
    for depth,idx,nrm in items:
        poly=[tuple(scr[k]) for k in idx]
        draw.polygon(poly, fill=_shade(base,nrm,fogf))
        if edge: draw.line(poly+[poly[0]],fill=edge,width=1)

def _bg():
    img=Image.new("RGB",(W,H),BG_TOP)
    top=np.array(BG_TOP); bot=np.array(BG_BOT)
    col=(top[None,:]*(1-np.linspace(0,1,H))[:,None]+bot[None,:]*np.linspace(0,1,H)[:,None]).astype(np.uint8)
    return Image.fromarray(np.repeat(col[:,None,:],W,1))

def _floor(cam, draw):
    z0,z1=-6.0,6.0
    xs=[X(i) for i in range(-2,N+2,4)]
    for x in xs:
        p,_=cam.project(np.array([[x,FLOOR_Y,z0],[x,FLOOR_Y,z1]]))
        draw.line([tuple(p[0]),tuple(p[1])],fill=(22,27,35),width=1)
    for z in np.linspace(z0,z1,7):
        p,_=cam.project(np.array([[X(-2),FLOOR_Y,z],[X(N+1),FLOOR_Y,z]]))
        draw.line([tuple(p[0]),tuple(p[1])],fill=(20,25,33),width=1)

def _shadow(cam, i, draw):
    x=X(i); s=BW*1.15
    quad=np.array([[x-s,FLOOR_Y+0.02,-s],[x+s,FLOOR_Y+0.02,-s],
                   [x+s,FLOOR_Y+0.02,s],[x-s,FLOOR_Y+0.02,s]])
    scr,_=cam.project(quad)
    draw.polygon([tuple(p) for p in scr],fill=(4,6,9))

def draw_chart3d(reveal, cam, highlights=None, brightness=1.0, print_glow=0):
    img=_bg(); d=ImageDraw.Draw(img,"RGB")
    _floor(cam,d)
    # shadow layer (soft)
    sh=Image.new("RGB",(W,H),(0,0,0)); shm=Image.new("L",(W,H),0); shd=ImageDraw.Draw(shm)
    for c in CANDLES[:reveal]:
        x=X(c["i"]); s=BW*1.2
        quad=np.array([[x-s,FLOOR_Y+0.02,-s],[x+s,FLOOR_Y+0.02,-s],
                       [x+s,FLOOR_Y+0.02,s],[x-s,FLOOR_Y+0.02,s]])
        scr,_=cam.project(quad); shd.polygon([tuple(p) for p in scr],fill=120)
    shm=shm.filter(ImageFilter.GaussianBlur(9))
    img=Image.composite(sh,img,shm); d=ImageDraw.Draw(img,"RGB")
    # candles far->near
    order=sorted(range(reveal),key=lambda i:-cam.dist([X(i),0,0]))
    dmax=max(cam.dist([X(i),0,0]) for i in range(reveal)) if reveal else 1
    dmin=min(cam.dist([X(i),0,0]) for i in range(reveal)) if reveal else 0
    for i in order:
        c=CANDLES[i]; x=X(i)
        up=c["up"]; base=[int(v*brightness) for v in (TEAL if up else RED)]
        fogf=clamp((cam.dist([x,0,0])-dmin)/max(1e-3,(dmax-dmin))*0.5)
        yb,yt=Yp(min(c["o"],c["c"])),Yp(max(c["o"],c["c"]))
        if yt-yb<0.05: yt=yb+0.05
        # wick
        _box(cam,x-WW/2,x+WW/2,Yp(c["l"]),Yp(c["h"]),-WW/2,WW/2,
             [int(v*0.7) for v in base],d,fogf)
        # body
        _box(cam,x-BW/2,x+BW/2,yb,yt,-BD/2,BD/2,base,d,fogf,
             edge=tuple(min(255,int(v*1.25)) for v in base))
    # highlights (glow at projected high, level lines)
    if highlights:
        gl=Image.new("RGBA",(W,H),(0,0,0,0)); gd=ImageDraw.Draw(gl)
        for tag in highlights.get("highs",[]):
            idx=IDX["H_"+tag]; P=np.array([[X(idx),Yp(LV["H_"+tag]),BD/2]])
            scr,_=cam.project(P); sx,sy=scr[0]
            col=highlights.get("high_col",GOLD)
            gd.ellipse([sx-60,sy-60,sx+60,sy+60],fill=(col[0],col[1],col[2],150))
        gl=gl.filter(ImageFilter.GaussianBlur(26))
        img=Image.alpha_composite(img.convert("RGBA"),gl).convert("RGB"); d=ImageDraw.Draw(img,"RGB")
        for ln in highlights.get("lines",[]):
            price,col,style=ln; y=Yp(price)
            p,_=cam.project(np.array([[X(0),y,BD/2],[X(reveal-1),y,BD/2]]))
            if style=="dash":
                a=np.array(p[0]); b=np.array(p[1]); L=np.linalg.norm(b-a); u=(b-a)/L; t=0
                while t<L:
                    s0=a+u*t; s1=a+u*min(t+16,L); d.line([tuple(s0),tuple(s1)],fill=col,width=2); t+=30
            else:
                d.line([tuple(p[0]),tuple(p[1])],fill=col,width=2)
    # price axis (billboarded right)
    fl=font(FL,26)
    for gp in range(int(PBOT)+(10-int(PBOT)%10),int(PTOP),10):
        P=np.array([[X(N+1),Yp(gp),0]]); scr,cz=cam.project(P)
        sx,sy=scr[0]
        if cz[0]>0: d.text((min(W-8,sx+6),sy),f"{gp:.0f}",font=fl,fill=(120,132,140),anchor="lm")
    # ticker
    d.text((46,150),"XAUUSD",font=font(FL_BLACK,30),fill=SILVER,anchor="lm")
    d.text((214,150),"15m",font=font(FL,28),fill=(120,132,140),anchor="lm")
    if print_glow>0 and reveal>0:
        c=CANDLES[reveal-1]; P=np.array([[X(c["i"]),Yp(c["c"]),BD/2]]); scr,_=cam.project(P); sx,sy=scr[0]
        gl=Image.new("RGBA",(W,H),(0,0,0,0)); gd=ImageDraw.Draw(gl)
        r=int(60*print_glow); gd.ellipse([sx-r,sy-r,sx+r,sy+r],
              fill=(GOLD[0],GOLD[1],GOLD[2],int(70*print_glow)))
        gl=gl.filter(ImageFilter.GaussianBlur(24))
        img=Image.alpha_composite(img.convert("RGBA"),gl).convert("RGB")
    return img

# a default cinematic camera focused on a candle index
def cam_for(focus_i=None, eye=None, target=None, fov=34.0):
    if target is None:
        fx=X(focus_i if focus_i is not None else N*0.6); target=(fx,1.2,0)
    if eye is None:
        eye=(target[0]*0.4+2.4, 3.2, 15.5)
    return Cam(eye,target,fov)

if __name__=="__main__":
    cam=cam_for(focus_i=IDX["H_R"])
    im=draw_chart3d(META["reveal_full"],cam,
        highlights={"highs":["L","R"],"high_col":GOLD,
          "lines":[(LV["LOW_L"],(150,160,170),"dash"),(LV["LOW_R"],(150,160,170),"dash")]})
    im.save("frames/_3dtest.png"); print("3d test saved")
