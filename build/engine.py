"""
Core render engine for the Liquidity State reel:
chart geometry, camera, grade, and the Arabic-safe text engine.
1080x1920, deterministic.
"""
import json, math, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1080, 1920
FPS = 30

# ---- palette (from the shot script) ----
NEARWHITE = (242,245,247)   # F2F5F7
SILVER    = (201,209,214)   # C9D1D6
GOLD      = (214,169,74)    # D6A94A
TEAL      = (46,158,143)    # 2E9E8F  (strong)
RED       = (239,83,80)     # EF5350  (weak)
BLACK     = (10,12,16)      # 0A0C10
PANEL     = (13,16,22)
GRID      = (26,31,40)
UPCOL     = (54,170,150)
DNCOL     = (224,84,80)

# ---- fonts ----
FA = os.path.join(HERE,"assets/fonts/Tajawal-Bold-ar.ttf")
FA_BLACK = os.path.join(HERE,"assets/fonts/Tajawal-Black-ar.ttf")
FL = os.path.join(HERE,"assets/fonts/Tajawal-Bold-latin.ttf")
FL_BLACK = os.path.join(HERE,"assets/fonts/Tajawal-Black-latin.ttf")
_fc={}
def font(path,size):
    k=(path,size)
    if k not in _fc: _fc[k]=ImageFont.truetype(path,size)
    return _fc[k]

# ---- data ----
with open(os.path.join(HERE,"candles.json")) as f:
    DATA=json.load(f)
CANDLES=DATA["candles"]; META=DATA["meta"]
PTOP=META["price_top"]; PBOT=META["price_bot"]; NBARS=META["n"]
LV=META["levels"]; IDX=META["idx"]

# chart pixel band (leave reel safe zones top/bottom)
CX0, CX1 = 46, 902          # candle x span
CYTOP, CYBOT = 250, 1600     # price band y span
AXIS_X = 912

def px(i):
    return CX0 + (i+0.5)*(CX1-CX0)/NBARS
def py(price):
    return CYTOP + (PTOP-price)/(PTOP-PBOT)*(CYBOT-CYTOP)
BARW = (CX1-CX0)/NBARS

# ---------- easing ----------
def clamp(x,a=0.0,b=1.0): return a if x<a else b if x>b else x
def ease_out(t): t=clamp(t); return 1-(1-t)**3
def ease_in(t): t=clamp(t); return t*t*t
def ease_io(t): t=clamp(t); return t*t*(3-2*t)
def lerp(a,b,t): return a+(b-a)*t

# ---------- Arabic-safe text ----------
def _is_ar(ch):
    o=ord(ch); return 0x0600<=o<=0x06FF or 0xFB50<=o<=0xFEFF
def draw_ar(d, xy, text, fnt, fill, anchor="mm", direction="rtl"):
    d.text(xy, text, font=fnt, fill=fill, anchor=anchor, direction=direction)
def ar_w(d, text, fnt, direction="rtl"):
    b=d.textbbox((0,0),text,font=fnt,anchor="la",direction=direction)
    return b[2]-b[0]

# vector glyphs the fonts lack (draw crisp, on-brand)
def sym_neq(d, cx, cy, s, col, wpx=7):
    d.line([(cx-s,cy-s*0.34),(cx+s,cy-s*0.34)],fill=col,width=wpx)
    d.line([(cx-s,cy+s*0.34),(cx+s,cy+s*0.34)],fill=col,width=wpx)
    d.line([(cx+s*0.55,cy-s*0.9),(cx-s*0.55,cy+s*0.9)],fill=col,width=wpx)
def sym_check(d, cx, cy, s, col, wpx=9):
    d.line([(cx-s*0.7,cy+s*0.05),(cx-s*0.15,cy+s*0.6)],fill=col,width=wpx)
    d.line([(cx-s*0.15,cy+s*0.6),(cx+s*0.8,cy-s*0.65)],fill=col,width=wpx)
def sym_cross(d, cx, cy, s, col, wpx=9):
    d.line([(cx-s*0.7,cy-s*0.7),(cx+s*0.7,cy+s*0.7)],fill=col,width=wpx)
    d.line([(cx-s*0.7,cy+s*0.7),(cx+s*0.7,cy-s*0.7)],fill=col,width=wpx)
def sym_dot(d, cx, cy, r, col):
    d.ellipse([cx-r,cy-r,cx+r,cy+r],fill=col)

def measure_runs(d, runs, direction="rtl"):
    """runs: list of (text, font). Returns total width (LTR layout of visual order)."""
    tot=0
    for t,fnt in runs:
        tot+=ar_w(d,t,fnt,direction="ltr" if not any(_is_ar(c) for c in t) else "rtl")
    return tot

def draw_runs_centered(d, cx, cy, runs, gap=10):
    """runs listed in VISUAL left->right order: (text, font, fill).
    Arabic runs get direction rtl; others ltr. Centered horizontally at cx."""
    widths=[]
    for t,fnt,_ in runs:
        dirn="rtl" if any(_is_ar(c) for c in t) else "ltr"
        widths.append(ar_w(d,t,fnt,direction=dirn))
    total=sum(widths)+gap*(len(runs)-1)
    x=cx-total/2
    for (t,fnt,fill),wv in zip(runs,widths):
        dirn="rtl" if any(_is_ar(c) for c in t) else "ltr"
        d.text((x,cy),t,font=fnt,fill=fill,anchor="lm",direction=dirn)
        x+=wv+gap
    return total

# ---------- text animation layer ----------
def text_layer(draw_fn, size=(W,H)):
    lay=Image.new("RGBA",size,(0,0,0,0))
    dd=ImageDraw.Draw(lay)
    draw_fn(dd)
    return lay

def paste_maskwipe(base, lay, progress, direction="RL"):
    """reveal lay onto base via a hard wipe. RL = right-to-left."""
    p=clamp(progress)
    mask=Image.new("L",lay.size,0)
    md=ImageDraw.Draw(mask)
    w,h=lay.size
    if direction=="RL":
        x0=int(w*(1-p)); md.rectangle([x0,0,w,h],fill=255)
    else:
        x1=int(w*p); md.rectangle([0,0,x1,h],fill=255)
    a=lay.split()[3]
    from PIL import ImageChops
    mask=ImageChops.multiply(mask,a)
    base.paste(lay,(0,0),mask)

def paste_alpha(base, lay, alpha=1.0, dx=0, dy=0):
    if alpha<=0: return
    a=lay.split()[3].point(lambda v:int(v*clamp(alpha)))
    base.paste(lay,(int(dx),int(dy)),a)

def scaled_layer(lay, scale, center):
    """scale an RGBA layer about center point, return same-size layer."""
    if abs(scale-1.0)<1e-3: return lay
    w,h=lay.size
    nw,nh=max(1,int(w*scale)),max(1,int(h*scale))
    sm=lay.resize((nw,nh),Image.LANCZOS)
    out=Image.new("RGBA",(w,h),(0,0,0,0))
    cx,cy=center
    out.alpha_composite(sm,(int(cx-nw*(cx/w)),int(cy-nh*(cy/h))))
    return out

# ---------- grade / vignette (precomputed) ----------
def make_vignette(strength=0.16):
    v=Image.new("L",(W,H),0)
    d=ImageDraw.Draw(v)
    import math as m
    # radial darkening toward edges
    max_r=m.hypot(W/2,H/2)
    step=Image.radial_gradient("L").resize((W,H))
    return step  # 0 center? radial_gradient is 0 center ->255 edge
_VIG=None
def apply_grade(img, vig=0.16, teal=0.05):
    """teal-silver push + vignette. img RGB in place-ish (returns new)."""
    global _VIG
    if _VIG is None:
        _VIG=Image.radial_gradient("L").resize((W,H))
    r,g,b=img.split()
    # subtle teal-silver: lift blue/green shadows slightly, cool highlights
    b=b.point(lambda v:min(255,int(v+ (255-v)*0.06 + 4)))
    g=g.point(lambda v:min(255,int(v+ (255-v)*0.03)))
    img=Image.merge("RGB",(r,g,b))
    # vignette
    dark=Image.new("RGB",(W,H),(0,0,0))
    vmask=_VIG.point(lambda v:int(v*vig))
    img=Image.composite(dark,img,vmask)
    return img

# ---------- chart ----------
def draw_chart(reveal, brightness=1.0, dim_price=None, highlights=None,
               show_axis=True, current_tag=True, print_glow=0):
    """
    highlights: dict controlling glows/labels, e.g.
      {'highs':['L','R'], 'lows':['L','R'], 'liq':[...], 'stop':None}
    print_glow: 0..1 glow on the last (printing) candle.
    Returns RGB image (full frame) with candles.
    """
    img=Image.new("RGB",(W,H),BLACK)
    d=ImageDraw.Draw(img)
    # panel bg subtle gradient
    d.rectangle([0,0,W,H],fill=PANEL)
    # faint horizontal grid + price ticks
    for gp in range(int(PBOT)+ (5-int(PBOT)%5), int(PTOP), 10):
        y=py(gp)
        d.line([(CX0-6,y),(AXIS_X-4,y)],fill=GRID,width=1)
    bright=lambda col: tuple(int(c*brightness) for c in col)
    # candles
    for c in CANDLES[:reveal]:
        i=c["i"]; x=px(i)
        col = UPCOL if c["up"] else DNCOL
        b=brightness
        if dim_price and not dim_price(c): b=b*0.5
        col=tuple(int(v*b) for v in col)
        yo,yc,yh,yl=py(c["o"]),py(c["c"]),py(c["h"]),py(c["l"])
        # wick
        d.line([(x,yh),(x,yl)],fill=col,width=2)
        # body
        bw=BARW*0.62
        top=min(yo,yc); bot=max(yo,yc)
        if bot-top<2: bot=top+2
        d.rectangle([x-bw/2,top,x+bw/2,bot],fill=col)
    # printing glow on last candle
    if print_glow>0 and reveal>0:
        gl=Image.new("RGBA",(W,H),(0,0,0,0))
        gd=ImageDraw.Draw(gl)
        c=CANDLES[reveal-1]; x=px(c["i"]); yc=py(c["c"])
        r=int(70*print_glow)
        gd.ellipse([x-r,yc-r,x+r,yc+r],fill=(GOLD[0],GOLD[1],GOLD[2],int(70*print_glow)))
        gl=gl.filter(ImageFilter.GaussianBlur(30))
        img=Image.alpha_composite(img.convert("RGBA"),gl).convert("RGB")
        d=ImageDraw.Draw(img)
    # highlights (glows + level lines)
    if highlights:
        gl=Image.new("RGBA",(W,H),(0,0,0,0)); gd=ImageDraw.Draw(gl)
        def glow(x,y,col,rad=54,a=150):
            gd.ellipse([x-rad,y-rad,x+rad,y+rad],fill=(col[0],col[1],col[2],a))
        for tag in highlights.get("highs",[]):
            idx=IDX["H_"+tag]; glow(px(idx),py(CANDLES[idx]["h"]),
                                    highlights.get("high_col",GOLD))
        for tag in highlights.get("lows",[]):
            key="LOW_"+tag
            price=LV[key]; # approximate x under corresponding high
            xh=px(IDX["H_"+tag]); glow(xh,py(price),TEAL,rad=46,a=120)
        gl=gl.filter(ImageFilter.GaussianBlur(26))
        img=Image.alpha_composite(img.convert("RGBA"),gl).convert("RGB")
        d=ImageDraw.Draw(img)
        # level lines
        for ln in highlights.get("lines",[]):
            price,col,style=ln
            y=py(price)
            if style=="dash":
                xx=CX0
                while xx<AXIS_X:
                    d.line([(xx,y),(min(xx+14,AXIS_X),y)],fill=col,width=2); xx+=26
            else:
                d.line([(CX0,y),(AXIS_X,y)],fill=col,width=2)
    # price axis
    if show_axis:
        d.line([(AXIS_X,CYTOP-30),(AXIS_X,CYBOT+30)],fill=GRID,width=2)
        fl=font(FL,26)
        for gp in range(int(PBOT)+(10-int(PBOT)%10), int(PTOP), 10):
            y=py(gp)
            d.text((AXIS_X+10,y),f"{gp:.0f}",font=fl,fill=(120,132,140),anchor="lm")
    # current price tag
    if current_tag and reveal>0:
        c=CANDLES[reveal-1]; y=py(c["c"])
        col=UPCOL if c["up"] else DNCOL
        fl=font(FL,26)
        tw=170
        d.rectangle([AXIS_X-2,y-20,AXIS_X-2+tw,y+20],fill=col)
        d.text((AXIS_X+8,y),f"{c['c']:.2f}",font=fl,fill=(6,10,12),anchor="lm")
    # header ticker
    fl=font(FL_BLACK,30); fa=font(FA,28)
    d.text((CX0,150),"XAUUSD",font=fl,fill=SILVER,anchor="lm")
    d.text((CX0+168,150),"15m",font=font(FL,28),fill=(120,132,140),anchor="lm")
    return img

# camera: crop-zoom about focus (fx,fy in px), zoom z>=1
def camera(img, z, fx, fy):
    if z<=1.001: return img
    cw,ch=int(W/z),int(H/z)
    left=int(clamp(fx-cw/2,0,W-cw)); top=int(clamp(fy-ch/2,0,H-ch))
    crop=img.crop((left,top,left+cw,top+ch))
    return crop.resize((W,H),Image.LANCZOS)

if __name__=="__main__":
    im=draw_chart(META["reveal_full"],
                  highlights={"highs":["L","R"],"lows":["L","R"],
                     "lines":[(LV["LOW_L"],(90,110,120),"dash"),
                              (LV["LOW_R"],(90,110,120),"dash")]})
    im=apply_grade(im)
    im.save(os.path.join(HERE,"frames/_charttest.png"))
    print("chart test saved")
