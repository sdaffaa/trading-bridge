"""
Beat-by-beat compositor. frame(t) -> RGB image for time t (seconds).
Implements the 11-beat cinematic shot script exactly on timing.
"""
import math
from PIL import Image, ImageDraw, ImageFilter, ImageChops
from engine import (W,H,FPS, NEARWHITE,SILVER,GOLD,TEAL,RED,BLACK,
    font,FA,FA_BLACK,FL,FL_BLACK, CANDLES,META,LV,IDX, px,py,BARW,
    CX0,CX1,CYTOP,CYBOT,AXIS_X,
    clamp,ease_out,ease_in,ease_io,lerp,
    draw_ar,ar_w,draw_runs_centered,sym_neq,sym_check,sym_cross,sym_dot,
    draw_chart,apply_grade,camera)

DUR=22.0
R0=META["reveal_frame0"]; RF=META["reveal_full"]

# ---- beat table (start,end) ----
B={
 1:(0.0,2.6),2:(2.6,4.0),3:(4.0,4.8),4:(4.8,6.0),56:(6.0,8.6),
 "7a":(8.6,11.0),"7b":(11.0,13.6),8:(13.6,14.3),9:(14.3,17.5),
 10:(17.5,19.2),11:(19.2,22.0)}

def which(t):
    for k,(a,b) in B.items():
        if a<=t<b: return k,(t-a),(b-a)
    return 11,(t-B[11][0]),(B[11][1]-B[11][0])

# ---------- caption helpers ----------
def scrim(img, cx, cy, w, h, alpha=120, blur=26):
    lay=Image.new("RGBA",(W,H),(0,0,0,0))
    d=ImageDraw.Draw(lay)
    x0,y0,x1,y1=int(cx-w/2),int(cy-h/2),int(cx+w/2),int(cy+h/2)
    d.rounded_rectangle([x0,y0,x1,y1],radius=int(h*0.4),fill=(6,8,11,alpha))
    lay=lay.filter(ImageFilter.GaussianBlur(blur))
    return Image.alpha_composite(img.convert("RGBA"),lay).convert("RGB")

def _txt_layer(text, fnt, fill, direction="rtl", shadow=True):
    tmp=Image.new("RGBA",(W,260),(0,0,0,0)); d=ImageDraw.Draw(tmp)
    w=ar_w(d,text,fnt,direction=direction)
    lay=Image.new("RGBA",(W,260),(0,0,0,0)); d=ImageDraw.Draw(lay)
    cx=W//2; cy=130
    if shadow:
        d.text((cx+2,cy+3),text,font=fnt,fill=(0,0,0,150),anchor="mm",direction=direction)
    d.text((cx,cy),text,font=fnt,fill=fill,anchor="mm",direction=direction)
    return lay,w

def place(img, lay, y, alpha=1.0, dy=0, scale=1.0):
    L=lay
    if abs(scale-1.0)>1e-3:
        nw,nh=int(W*scale),int(260*scale)
        s=lay.resize((nw,nh),Image.LANCZOS)
        L=Image.new("RGBA",(W,260),(0,0,0,0))
        L.alpha_composite(s,((W-nw)//2,(260-nh)//2))
    a=L.split()[3].point(lambda v:int(v*clamp(alpha)))
    img.paste(L,(0,int(y-130+dy)),a)

def caption_wipe(img, text, fnt, fill, y, lt, t_in, dur_in, with_scrim=True):
    lay,w=_txt_layer(text,fnt,fill)
    if with_scrim: img=scrim(img,W//2,y,w+90,150)
    p=ease_out((lt-t_in)/dur_in) if lt>=t_in else 0.0
    # right-to-left wipe of the text layer
    mask=Image.new("L",(W,260),0); md=ImageDraw.Draw(mask)
    x0=int(W*(1-clamp(p)))
    md.rectangle([x0,0,W,260],fill=255)
    a=ImageChops.multiply(lay.split()[3],mask)
    img.paste(lay,(0,int(y-130)),a)
    return img

def caption_rise(img, text, fnt, fill, y, lt, t_in, dur_in, rise=18, with_scrim=True):
    lay,w=_txt_layer(text,fnt,fill)
    if with_scrim: img=scrim(img,W//2,y,w+90,150)
    p=ease_out((lt-t_in)/dur_in) if lt>=t_in else 0.0
    place(img,lay,y,alpha=p,dy=(1-p)*rise)
    return img

def caption_stamp(img, text, fnt, fill, y, lt, t_in, with_scrim=True):
    lay,w=_txt_layer(text,fnt,fill)
    if with_scrim: img=scrim(img,W//2,y,w+90,150)
    e=lt-t_in
    if e<0: return img
    p=ease_out(e/0.12)
    scale=lerp(1.16,1.0,p); alpha=clamp(e/0.06)
    place(img,lay,y,alpha=alpha,scale=scale)
    return img

def caption_scalein(img, text, fnt, fill, y, lt, t_in, dur_in, with_scrim=True):
    lay,w=_txt_layer(text,fnt,fill)
    if with_scrim: img=scrim(img,W//2,y,w+90,150)
    p=ease_out((lt-t_in)/dur_in) if lt>=t_in else 0.0
    place(img,lay,y,alpha=p,scale=lerp(0.96,1.0,p))
    return img

# ---------- mixed-run caption engine (Arabic + Latin punct + vector symbols + pills) ----------
def _is_ar_s(s): return any(0x0600<=ord(c)<=0x06FF for c in s)
def _seq_widths(d, seq, sc):
    ws=[]
    for it in seq:
        k=it[0]
        if k=="t":
            _,tx,path,size,fill=it
            f=font(path,int(size*sc)); dirn="rtl" if _is_ar_s(tx) else "ltr"
            ws.append(ar_w(d,tx,f,direction=dirn))
        elif k=="neq": ws.append(int(it[1]*2*sc))
        elif k in ("check","cross"): ws.append(int(it[1]*2.0*sc))
        elif k=="pill":
            _,tx,path,size,fill,bg=it
            f=font(path,int(size*sc)); ws.append(ar_w(d,tx,f,direction="rtl")+int(44*sc))
    return ws
def draw_seq(d, cx, cy, seq, gap=16, maxw=980, base_sc=1.0):
    sc=base_sc
    ws=_seq_widths(d,seq,sc); total=sum(ws)+gap*sc*(len(seq)-1)
    if total>maxw:
        sc=base_sc*maxw/total
        ws=_seq_widths(d,seq,sc); total=sum(ws)+gap*sc*(len(seq)-1)
    x=cx-total/2
    for it,wv in zip(seq,ws):
        k=it[0]
        if k=="t":
            _,tx,path,size,fill=it
            f=font(path,int(size*sc)); dirn="rtl" if _is_ar_s(tx) else "ltr"
            d.text((x,cy),tx,font=f,fill=fill,anchor="lm",direction=dirn)
        elif k=="neq":
            sym_neq(d,x+wv/2,cy,int(it[1]*sc),it[2],max(4,int(7*sc)))
        elif k=="check":
            sym_check(d,x+wv/2,cy,int(it[1]*sc),it[2],max(5,int(9*sc)))
        elif k=="cross":
            sym_cross(d,x+wv/2,cy,int(it[1]*sc),it[2],max(5,int(9*sc)))
        elif k=="pill":
            _,tx,path,size,fill,bg=it
            f=font(path,int(size*sc))
            d.rounded_rectangle([x,cy-int(38*sc),x+wv,cy+int(38*sc)],radius=int(20*sc),fill=bg)
            d.text((x+wv/2,cy),tx,font=f,fill=fill,anchor="mm",direction="rtl")
        x+=wv+gap*sc
    return total

def caption_seq(img, seq, y, lt, t_in, dur_in, mode="wipe", scrim_w=900, maxw=980, gap=16):
    lay=Image.new("RGBA",(W,260),(0,0,0,0)); d=ImageDraw.Draw(lay)
    draw_seq(d,W//2,130,seq,gap=gap,maxw=maxw)
    img=scrim(img,W//2,y,scrim_w,150)
    p=ease_out((lt-t_in)/dur_in) if lt>=t_in else 0.0
    if mode=="wipe":
        mask=Image.new("L",(W,260),0); md=ImageDraw.Draw(mask)
        md.rectangle([int(W*(1-clamp(p))),0,W,260],fill=255)
        a=ImageChops.multiply(lay.split()[3],mask)
        img.paste(lay,(0,int(y-130)),a)
    elif mode=="rise":
        a=lay.split()[3].point(lambda v:int(v*clamp(p)))
        img.paste(lay,(0,int(y-130+(1-p)*18)),a)
    else:
        a=lay.split()[3].point(lambda v:int(v*clamp(p)))
        img.paste(lay,(0,int(y-130)),a)
    return img

# runs caption (mixed arabic + symbol) drawn directly with animation alpha
def caption_runs(img, runs_fn, y, lt, t_in, dur_in, scrim_w=760, mode="wipe"):
    lay=Image.new("RGBA",(W,260),(0,0,0,0)); d=ImageDraw.Draw(lay)
    runs_fn(d,130)
    img=scrim(img,W//2,y,scrim_w,150)
    p=ease_out((lt-t_in)/dur_in) if lt>=t_in else 0.0
    if mode=="wipe":
        mask=Image.new("L",(W,260),0); md=ImageDraw.Draw(mask)
        md.rectangle([int(W*(1-clamp(p))),0,W,260],fill=255)
        a=ImageChops.multiply(lay.split()[3],mask)
        img.paste(lay,(0,int(y-130)),a)
    else:
        a=lay.split()[3].point(lambda v:int(v*clamp(p)))
        img.paste(lay,(0,int(y-130)),a)
    return img

# ---------- chart-with-camera base ----------
def base(reveal, brightness=1.0, highlights=None, print_glow=0):
    im=draw_chart(reveal,brightness=brightness,highlights=highlights,print_glow=print_glow)
    return im

def marker_badge(d, cx, cy, text, col, fnt=None):
    fnt=fnt or font(FA,40)
    w=ar_w(d,text,fnt); pad=22
    x0,y0,x1,y1=cx-w/2-pad,cy-34,cx+w/2+pad,cy+34
    d.rounded_rectangle([x0,y0,x1,y1],radius=16,fill=col)
    d.text((cx,cy),text,font=fnt,fill=(8,12,14),anchor="mm",direction="rtl")

def liq_arrow(d, x, y, col, up=False):
    # small liquidity arrow into a low
    L=46
    if up:
        d.line([(x,y+L),(x,y)],fill=col,width=6)
        d.polygon([(x-11,y+13),(x+11,y+13),(x,y)],fill=col)
    else:
        d.line([(x,y-L),(x,y)],fill=col,width=6)
        d.polygon([(x-11,y-13),(x+11,y-13),(x,y)],fill=col)

# ============ BEATS ============
def frame(t):
    k,lt,dl=which(t)
    # ---- B1 HOOK ----
    if k==1:
        p=lt/dl
        # last 3 candles printing 50->53
        reveal=min(R0, 50+int(ease_io(clamp((lt-0.1)/2.0))*3+0.999))
        pg=0.4+0.6*abs(math.sin(lt*7))
        hi={"highs":["L","R"],"high_col":GOLD}
        im=base(reveal,highlights=hi,print_glow=pg*0.6)
        im=apply_grade(im)
        fx,fy=px(IDX["H_R"]),py(LV["H_R"]); z=1.0+0.04*ease_out(p)
        im=camera(im,z,fx,fy)
        im=caption_wipe(im,"أي هاي بياخذ ستوبك؟",font(FA_BLACK,86),NEARWHITE,1250,lt,0.3,0.6)
        return im
    # ---- B2 PARADOX ----
    if k==2:
        ph=0.5+0.5*math.sin(lt*7)
        # alternate pulse: left bright when ph>0.5 else right
        colL=GOLD if (int(lt/0.4)%2==0) else (120,100,60)
        colR=GOLD if (int(lt/0.4)%2==1) else (120,100,60)
        im=draw_chart(R0,highlights={"highs":["L"],"high_col":colL})
        im2=draw_chart(R0,highlights={"highs":["R"],"high_col":colR})
        # merge glows: just draw both highlights
        im=draw_chart(R0,highlights={"highs":["L","R"],"high_col":GOLD})
        # emphasize alternately via extra glow
        gl=Image.new("RGBA",(W,H),(0,0,0,0)); gd=ImageDraw.Draw(gl)
        tag="L" if int(lt/0.4)%2==0 else "R"
        idx=IDX["H_"+tag]; x=px(idx); y=py(LV["H_"+tag])
        gd.ellipse([x-70,y-70,x+70,y+70],fill=(GOLD[0],GOLD[1],GOLD[2],120))
        gl=gl.filter(ImageFilter.GaussianBlur(30))
        im=Image.alpha_composite(im.convert("RGBA"),gl).convert("RGB")
        im=apply_grade(im)
        im=camera(im,1.04,px(IDX["H_R"]),py(LV["H_R"]))
        im=caption_seq(im,[("t","والثاني هدف",FA,70,SILVER),("t","…",FL,66,SILVER),
                           ("t","واحد حماية",FA,70,SILVER)],1250,lt,0.0,0.4,mode="rise",scrim_w=880)
        return im
    # ---- B3 PIVOT ----
    if k==3:
        im=draw_chart(R0,brightness=0.45,highlights={"highs":["L","R"],"high_col":GOLD})
        im=apply_grade(im)
        im=camera(im,1.04,px(IDX["H_R"]),py(LV["H_R"]))
        im=caption_stamp(im,"شلون؟",font(FA_BLACK,118),GOLD,960,lt,0.05)
        return im
    # ---- B4 INVITE (partial give) ----
    if k==4:
        p=lt/dl
        hi={"highs":["L","R"],"high_col":GOLD,
            "lines":[(LV["LOW_L"],(120,140,150),"dash"),(LV["LOW_R"],(120,140,150),"dash")]}
        im=draw_chart(R0,brightness=1.0,highlights=hi)
        # light the lows appearing
        gl=Image.new("RGBA",(W,H),(0,0,0,0)); gd=ImageDraw.Draw(gl)
        a=int(150*ease_out((lt-0.2)/0.8))
        for price,xidx in [(LV["LOW_L"],19),(LV["LOW_R"],43)]:
            x=px(xidx); y=py(price)
            gd.ellipse([x-40,y-40,x+40,y+40],fill=(TEAL[0],TEAL[1],TEAL[2],max(0,a)))
        gl=gl.filter(ImageFilter.GaussianBlur(22))
        im=Image.alpha_composite(im.convert("RGBA"),gl).convert("RGB")
        im=apply_grade(im)
        z=lerp(1.06,1.0,ease_io(p))   # pull-back
        im=camera(im,z,px(IDX["H_R"]),py((LV["H_R"]+LV["LOW_R"])/2))
        return im
    # ---- B5+6 BELIEF+WHY ----
    if k==56:
        p=lt/dl
        im=draw_chart(R0,highlights={"highs":["R"],"high_col":(150,160,168)})
        d=ImageDraw.Draw(im)
        # gray arrow pointing to higher (right) high + badge "الأعلى"
        x=px(IDX["H_R"]); y=py(LV["H_R"])
        ap=ease_out(clamp(lt/0.8))
        d.line([(x,y-150),(x,y-40*ap-30)],fill=(150,160,168),width=6)
        d.polygon([(x-12,y-52),(x+12,y-52),(x,y-34)],fill=(150,160,168))
        if lt>0.6: marker_badge(d,x,y-200,"الأعلى",(150,160,168))
        im=apply_grade(im)
        im=camera(im,1.0+0.05*ease_out(p),x,y)
        im=caption_seq(im,[("t","الأقوى",FA,88,SILVER),("neq",24,SILVER),
                           ("t","الأعلى",FA,88,SILVER)],1250,lt,0.2,0.5,mode="fade",scrim_w=760,gap=26)
        return im
    # ---- B7a TURN ----
    if k=="7a":
        p=lt/dl
        # high loses brightness, low zone lights teal; track down
        bR=lerp(1.0,0.6,ease_io(p))
        im=draw_chart(R0,brightness=1.0)
        d=ImageDraw.Draw(im)
        # teal wash on the low under right high
        gl=Image.new("RGBA",(W,H),(0,0,0,0)); gd=ImageDraw.Draw(gl)
        x=px(IDX["WEAKLOW"]); y=py(LV["WEAKLOW"])
        gd.ellipse([x-90,y-70,x+90,y+70],fill=(TEAL[0],TEAL[1],TEAL[2],int(150*ease_out(p))))
        # dim the high
        xh=px(IDX["H_R"]); yh=py(LV["H_R"])
        gd.ellipse([xh-70,yh-70,xh+70,yh+70],fill=(0,0,0,int(120*ease_out(p))))
        gl=gl.filter(ImageFilter.GaussianBlur(26))
        im=Image.alpha_composite(im.convert("RGBA"),gl).convert("RGB")
        im=apply_grade(im)
        fy=lerp(yh,y,ease_io(p))
        im=camera(im,1.05,xh,fy)
        im=caption_wipe(im,"القوة من اللي تحته",font(FA,88),TEAL,1250,lt,0.1,0.6)
        return im
    # ---- B7b RULE (split screen, screenshot frame) ----
    if k=="7b":
        return rule_frame(lt,dl)
    # ---- B8 VERDICT ----
    if k==8:
        p=lt/dl
        im=draw_chart(RF,highlights={"highs":["R"],"high_col":RED})
        d=ImageDraw.Draw(im)
        # weak high split by sweep candle: emphasize run+tail
        xr=px(IDX["RUN"]);
        im=apply_grade(im)
        # micro-shake on surrounding frame
        import random
        sh=1.5*math.sin(lt*3*2*math.pi) if lt<0.4 else 0
        im=camera(im,1.03,px(IDX["H_R"])+sh,py(LV["H_R"]))
        im=caption_stamp(im,"اهو اللي بياخذ ستوبك",font(FA_BLACK,96),NEARWHITE,1250,lt,0.02)
        return im
    # ---- B9 PROOF ----
    if k==9:
        p=lt/dl
        hi={"highs":["L","R"],"high_col":GOLD,
            "lines":[(LV["H_L"],(TEAL[0],TEAL[1],TEAL[2]),"solid"),
                     (LV["H_R"],(RED[0],RED[1],RED[2]),"dash")]}
        im=draw_chart(RF,highlights=hi)
        d=ImageDraw.Draw(im)
        # held (strong) check near H_L ; fell (weak) cross near H_R
        sym_check(d,px(IDX["H_L"])-40,py(LV["H_L"])-150,26,TEAL,9)
        sym_cross(d,px(IDX["H_R"])+40,py(LV["H_R"])-150,24,RED,9)
        im=apply_grade(im)
        z=lerp(1.05,1.0,ease_io(p))
        im=camera(im,z,(px(IDX["H_L"])+px(IDX["TARGET"]))/2, (CYTOP+CYBOT)/2)
        im=caption_seq(im,[("t","طاح",FA,74,RED),("cross",22,RED),
                           ("check",22,TEAL),("t","صمد",FA,74,TEAL)],
                          1250,lt,0.1,0.6,mode="rise",scrim_w=560,gap=30)
        return im
    # ---- B10 CARE ----
    if k==10:
        p=lt/dl
        im=draw_chart(RF,highlights={"highs":["L","R"],"high_col":(150,160,168)})
        d=ImageDraw.Draw(im)
        # stop line moves from above weak high to above strong high
        y_weak=py(LV["H_R"])-70; y_strong=py(LV["H_L"])-70
        y=lerp(y_weak,y_strong,ease_io(p))
        xx=CX0
        while xx<AXIS_X:
            d.line([(xx,y),(min(xx+16,AXIS_X),y)],fill=RED if p<0.5 else TEAL,width=3); xx+=28
        d.text((AXIS_X-6,y-2),"SL",font=font(FL,26),fill=(RED if p<0.5 else TEAL),anchor="rm")
        im=apply_grade(im)
        im=camera(im,1.03,px(IDX["H_L"]),lerp(y_weak,y_strong,ease_io(p)))
        im=caption_seq(im,[("t","اهو سيولة مستهدفة",FA,72,TEAL),("t","…",FL,66,TEAL),
                           ("t","اهو مو حماية",FA,72,TEAL)],1290,lt,0.1,0.6,mode="wipe",
                          scrim_w=1000,maxw=1000)
        return im
    # ---- B11 LOOP ----
    p=lt/dl
    reveal=min(R0,50+int(ease_io(clamp(lt/2.0))*3+0.999))
    pg=0.4+0.6*abs(math.sin(lt*7))
    im=base(reveal,highlights={"highs":["L","R"],"high_col":GOLD},print_glow=pg*0.6)
    im=apply_grade(im)
    im=camera(im,1.0+0.03*ease_out(p),px(IDX["H_R"]),py(LV["H_R"]))
    im=caption_seq(im,[("t","بالتعليقات",FA_BLACK,78,GOLD),
                       ("pill","قوي",FA_BLACK,70,(10,12,16),GOLD),
                       ("t","اكتب",FA_BLACK,78,GOLD)],1250,lt,0.0,0.5,mode="rise",scrim_w=900)
    return im

def proof_runs(d,cy):
    # صمد ✓   ✕ طاح   (visual left->right)
    fnt=font(FA,76)
    parts=[("صمد",fnt,TEAL),("طاح",fnt,RED)]
    # measure
    w1=ar_w(d,"صمد",fnt); w2=ar_w(d,"طاح",fnt)
    gap=70
    total=w1+gap+40+gap+w2
    x=W/2-total/2
    d.text((x+w1/2,cy),"صمد",font=fnt,fill=TEAL,anchor="mm",direction="rtl"); x+=w1+gap
    sym_check(d,x,cy,22,TEAL,8); x+=40+gap
    d.text((x+w2/2,cy),"طاح",font=fnt,fill=RED,anchor="mm",direction="rtl")

def rule_runs(d,cy):
    # سحب اللو = قوي · ما سحب = ضعيف  (visual left->right, RTL sentence)
    fA=font(FA,74); fL=font(FL,64)
    # We lay RTL: rightmost is first word. Build visual left->right sequence:
    seq=[("ضعيف",fA,RED),("=",fL,SILVER),("سحب",fA,NEARWHITE),("ما",fA,NEARWHITE),
         ("·",fL,GOLD),("قوي",fA,TEAL),("=",fL,SILVER),("اللو",fA,NEARWHITE),("سحب",fA,NEARWHITE)]
    widths=[]
    for tx,fn,_ in seq:
        dirn="rtl" if any(0x600<=ord(c)<=0x6FF for c in tx) else "ltr"
        widths.append(ar_w(d,tx,fn,direction=dirn))
    gap=18; total=sum(widths)+gap*(len(seq)-1)
    x=W/2-total/2
    for (tx,fn,col),wv in zip(seq,widths):
        dirn="rtl" if any(0x600<=ord(c)<=0x6FF for c in tx) else "ltr"
        d.text((x,cy),tx,font=fn,fill=col,anchor="lm",direction=dirn); x+=wv+gap

def _mini_panel(strong):
    """Schematic mini formation. strong=True: last drop candle's wick pierces the
    'last low' line (liquidity swept). False: drop stops clearly above it (not swept)."""
    PW,PH=W//2-8, int(H*0.46)
    im=Image.new("RGB",(PW,PH),(11,14,19))
    d=ImageDraw.Draw(im)
    top,bot=54,PH-54
    pmax,pmin=(4092.0,4046.0)
    def yy(p): return top+(pmax-p)/(pmax-pmin)*(bot-top)
    lastlow=4058.0
    # 4 green rise candles -> high -> 3 red drop candles (last = the test)
    if strong:
        seq=[(4060,4066,True),(4066,4072,True),(4072,4080,True),(4080,4086,True),
             (4086,4078,False),(4078,4070,False),(4070,4066,False)]  # last wick pierces below
        wick_lo=4049.0; col_low=TEAL; badge="قوي"; label="سحب اللو"
    else:
        seq=[(4062,4068,True),(4068,4076,True),(4076,4084,True),(4084,4090,True),
             (4090,4082,False),(4082,4074,False),(4074,4067,False)]  # last low stays above line
        wick_lo=4066.0; col_low=RED; badge="ضعيف"; label="ما وصله"
    n=len(seq); cw=(PW-72)/n
    lastx=None
    for i,(o,c,up) in enumerate(seq):
        x=42+i*cw+cw/2
        col=(54,170,150) if up else (224,84,80)
        hh=max(o,c)+3; ll=min(o,c)-3
        if i==n-1: ll=wick_lo; lastx=x       # the decisive test candle
        d.line([(x,yy(hh)),(x,yy(ll))],fill=col,width=3)
        t=min(yy(o),yy(c)); b=max(yy(o),yy(c)); b=max(b,t+3)
        d.rectangle([x-cw*0.32,t,x+cw*0.32,b],fill=col)
    # last-low dashed line + label
    yl=yy(lastlow); xx=24
    while xx<PW-24:
        d.line([(xx,yl),(min(xx+16,PW-24),yl)],fill=(170,180,190),width=2); xx+=28
    d.text((PW-30,yl-24),"آخر لو",font=font(FA,28),fill=(180,190,200),anchor="rm",direction="rtl")
    # highlight the decisive wick vs the gap
    if strong:
        d.line([(lastx,yl),(lastx,yy(wick_lo))],fill=col_low,width=5)   # pierce
        liq_arrow(d,lastx,yy(wick_lo)+8,col_low,up=True)
    else:
        # show the gap between drop low and the line
        d.line([(lastx,yy(wick_lo)),(lastx,yl)],fill=(120,130,140),width=2)
        liq_arrow(d,lastx+2,yy(wick_lo)-8,col_low,up=False)
    return im,badge,col_low,label,PW,PH

def rule_frame(lt,dl):
    im=Image.new("RGB",(W,H),BLACK)
    d0=ImageDraw.Draw(im)
    # section title
    d0.text((W//2,220),"قوة الهاي من اللي تحته",font=font(FA_BLACK,56),fill=NEARWHITE,
            anchor="mm",direction="rtl")
    left,bL,cL,lblL,PW,PH=_mini_panel(True)
    right,bR,cR,lblR,_,_=_mini_panel(False)
    py0=int(H*0.32)
    im.paste(left,(4,py0)); im.paste(right,(W//2+4,py0))
    d=ImageDraw.Draw(im)
    d.line([(W//2,py0-6),(W//2,py0+PH+6)],fill=(40,46,56),width=3)
    # panel frames tinted by verdict
    d.rectangle([4,py0,4+PW,py0+PH],outline=(cL[0],cL[1],cL[2]),width=3)
    d.rectangle([W//2+4,py0,W//2+4+PW,py0+PH],outline=(cR[0],cR[1],cR[2]),width=3)
    # verdict labels above panels (staggered reveal)
    if lt>0.2:
        d.text((4+PW//2,py0-34),lblL,font=font(FA,40),fill=cL,anchor="mm",direction="rtl")
    if lt>0.5:
        d.text((W//2+4+PW//2,py0-34),lblR,font=font(FA,40),fill=cR,anchor="mm",direction="rtl")
    # badges below panels
    if lt>0.2: marker_badge(d,4+PW//2,py0+PH+48,bL,cL)
    if lt>0.5: marker_badge(d,W//2+4+PW//2,py0+PH+48,bR,cR)
    # rule caption (auto-fit, no clipping)
    seq=[("t","ضعيف",FA,66,RED),("t","=",FL,58,SILVER),("t","سحب",FA,66,NEARWHITE),
         ("t","ما",FA,66,NEARWHITE),("t","·",FL,58,GOLD),("t","قوي",FA,66,TEAL),
         ("t","=",FL,58,SILVER),("t","اللو",FA,66,NEARWHITE),("t","سحب",FA,66,NEARWHITE)]
    im=caption_seq(im,seq,py0+PH+130,lt,0.1,0.6,mode="wipe",scrim_w=1010,maxw=1010,gap=14)
    return im
