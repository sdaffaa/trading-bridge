"""
3D scene compositor. frame(t) -> RGB for time t.
Base = perspective 3D chart (engine3d) with animated camera; overlays (Arabic
captions with depth-shadow, badges, subtitles, and the RULE authority frame)
are reused from the 2D scenes module.
"""
import math, numpy as np
from PIL import Image, ImageDraw, ImageFilter
import engine3d as E3
from engine3d import (W,H, NEARWHITE,SILVER,GOLD,TEAL,RED, font,FA,FL,
                      draw_chart3d, Cam, X, Yp, IDX, LV, META, clamp,lerp)
from engine import FA_BLACK, ease_out, ease_in, ease_io
import scenes as S2   # reuse 2D overlays: captions, subtitle, rule frame, badges

R0=META["reveal_frame0"]; RF=META["reveal_full"]
B=S2.B; which=S2.which

# ---- camera keyframe states: (eye, target, fov) ----
S_wide    = ((1.4,3.5,39.0),(-0.4,0.5,0),40.0)
S_widein  = ((1.7,3.6,34.5),(-0.2,0.6,0),39.0)
S_hr      = ((2.4,3.7,29.0),(X(IDX["H_R"])*0.5,1.3,0),36.0)
S_hrin    = ((2.7,3.6,25.0),(X(IDX["H_R"])*0.5,1.4,0),34.0)
S_low     = ((1.9,1.5,28.0),(X(IDX["H_R"])*0.5,-2.4,0),39.0)
S_full    = ((1.3,3.4,36.0),(-0.3,0.5,0),40.0)
S_fullout = ((1.1,3.3,41.0),(-0.3,0.4,0),41.0)
S_up      = ((1.7,4.6,31.0),(X(IDX["H_L"])*0.4,1.8,0),36.0)

def _mk(s):
    (e,t,f)=s; return e,t,f
def cam_lerp(a,b,p):
    (ea,ta,fa)=a; (eb,tb,fb)=b
    e=tuple(lerp(ea[i],eb[i],p) for i in range(3))
    t=tuple(lerp(ta[i],tb[i],p) for i in range(3))
    return Cam(e,t,lerp(fa,fb,p))

def beat_cam(k,p,lt):
    if k==1:   return cam_lerp(S_wide,S_widein,ease_out(p))
    if k==2:   return cam_lerp(S_widein,S_widein,p)
    if k==3:   return cam_lerp(S_widein,S_widein,p)
    if k==4:   return cam_lerp(S_widein,S_fullout,ease_io(p))
    if k==56:  return cam_lerp(S_fullout,S_hr,ease_out(p))
    if k=="7a":return cam_lerp(S_hr,S_low,ease_io(p))
    if k==8:
        c=cam_lerp(S_hrin,S_hrin,p)
        if lt<0.4:  # micro-shake
            sh=1.6*math.sin(lt*3*2*math.pi)
            c=Cam((S_hrin[0][0]+sh*0.02,S_hrin[0][1],S_hrin[0][2]),S_hrin[1],S_hrin[2])
        return c
    if k==9:   return cam_lerp(S_hrin,S_fullout,ease_io(p))
    if k==10:  return cam_lerp(S_full,S_up,ease_io(p))
    return cam_lerp(S_wide,S_widein,ease_out(p))   # 11

def frame(t):
    k,lt,dl=which(t); p=lt/dl
    # RULE authority frame stays the flat 2D screenshot frame
    if k=="7b":
        img=S2.rule_frame(lt,dl)
        return S2.draw_subtitle(img,t)
    # printing reveal for hook/loop
    if k in (1,11):
        reveal=min(R0,24+int(ease_io(clamp((lt-0.1)/1.8))*2+0.999))
        pg=(0.4+0.6*abs(math.sin(lt*7)))*0.6
    else:
        reveal=R0 if k in (2,3,4,56,"7a") else RF
        pg=0
    bright=0.45 if k==3 else 1.0
    # highlights
    hl=None
    if k in (1,2,11): hl={"highs":["L","R"],"high_col":GOLD}
    elif k==3:        hl={"highs":["L","R"],"high_col":GOLD}
    elif k==4:        hl={"highs":["L","R"],"high_col":GOLD,
                          "lines":[(LV["LOW_L"],(150,160,170),"dash"),(LV["LOW_R"],(150,160,170),"dash")]}
    elif k==56:       hl={"highs":["R"],"high_col":(150,160,168)}
    elif k=="7a":     hl={"highs":["R"],"high_col":(150,160,168)}
    elif k==8:        hl={"highs":["R"],"high_col":RED}
    elif k==9:        hl={"highs":["L","R"],"high_col":GOLD,
                          "lines":[(LV["H_L"],TEAL,"solid"),(LV["H_R"],RED,"dash")]}
    elif k==10:       hl={"highs":["L","R"],"high_col":(150,160,168)}
    cam=beat_cam(k,p,lt)
    img=draw_chart3d(reveal,cam,highlights=hl,brightness=bright,print_glow=pg)

    # ---- overlays (reuse 2D caption engine; depth-shadow built into _txt_layer) ----
    if k==1:
        img=S2.caption_wipe(img,"أي هاي بياخذ ستوبك؟",font(FA_BLACK,86),NEARWHITE,1250,lt,0.3,0.6)
    elif k==2:
        img=S2.caption_seq(img,[("t","والثاني هدف",FA,70,SILVER),("t","…",FL,66,SILVER),
                            ("t","واحد حماية",FA,70,SILVER)],1250,lt,0.0,0.4,mode="rise",scrim_w=880)
    elif k==3:
        img=S2.caption_stamp(img,"شلون؟",font(FA_BLACK,118),GOLD,960,lt,0.05)
    elif k==56:
        d=ImageDraw.Draw(img); x=X(IDX["H_R"]); P=np.array([[x,Yp(LV["H_R"]),E3.BD/2]])
        scr,_=cam.project(P); sx,sy=scr[0]
        if lt>0.6: S2.marker_badge(d,sx,sy-150,"الأعلى",(150,160,168))
        img=S2.caption_seq(img,[("t","الأقوى",FA,88,SILVER),("neq",24,SILVER),
                            ("t","الأعلى",FA,88,SILVER)],1250,lt,0.2,0.5,mode="fade",scrim_w=760,gap=26)
    elif k=="7a":
        img=S2.caption_wipe(img,"القوة من اللي تحته",font(FA,88),TEAL,1250,lt,0.1,0.6)
    elif k==8:
        img=S2.caption_stamp(img,"اهو اللي بياخذ ستوبك",font(FA_BLACK,96),NEARWHITE,1250,lt,0.02)
    elif k==9:
        img=S2.caption_seq(img,[("t","ما كسر",FA,66,RED),("cross",22,RED),
                            ("check",22,TEAL),("t","كسر",FA,66,TEAL)],1250,lt,0.1,0.6,mode="rise",scrim_w=640,gap=26)
    elif k==10:
        img=S2.caption_seq(img,[("t","اهو سيولة مستهدفة",FA,72,TEAL),("t","…",FL,66,TEAL),
                            ("t","اهو مو حماية",FA,72,TEAL)],1290,lt,0.1,0.6,mode="wipe",scrim_w=1000,maxw=1000)
    elif k==11:
        img=S2.caption_seq(img,[("t","بالتعليقات",FA_BLACK,78,GOLD),
                            ("pill","قوي",FA_BLACK,70,(10,12,16),GOLD),
                            ("t","اكتب",FA_BLACK,78,GOLD)],1250,lt,0.0,0.5,mode="rise",scrim_w=900)
    img=S2.draw_subtitle(img,t)
    return img
