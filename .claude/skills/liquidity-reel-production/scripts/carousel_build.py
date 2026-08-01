# -*- coding: utf-8 -*-
import base64, os, math

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(HERE, "fonts")

# ---------- Brand (LIGHT theme, matching real template) ----------
CREAM="#F2EEE7"; CREAM2="#ECE6DB"
INK="#0F2E3C"           # deep navy-teal (titles)
TEAL="#2E7D96"          # primary teal accent
TEAL_D="#1E627A"        # darker teal
TEAL_L="#5AA6BC"
BULL="#2E8CA6"          # teal bullish candle
BEAR="#122F3E"          # navy bearish candle
RED="#D24B4B"
GREY="#5C6C73"          # body grey
MUTE="#93A2A8"
LINE="#7C8C93"
CARDBD="#DED8CC"

# ---------- Fonts ----------
def font_face(name, fname, weight):
    with open(os.path.join(FONTS, fname), "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    return (f"@font-face{{font-family:'{name}';font-style:normal;font-weight:{weight};"
            f"font-display:block;src:url(data:font/ttf;base64,{b64}) format('truetype');}}")
FONT_CSS = "\n".join([
    font_face("Tajawal","Tajawal-Regular.ttf",400),
    font_face("Tajawal","Tajawal-Medium.ttf",500),
    font_face("Tajawal","Tajawal-Bold.ttf",700),
    font_face("Tajawal","Tajawal-ExtraBold.ttf",800),
    font_face("Tajawal","Tajawal-Black.ttf",900),
])

# ---------- Real EUR/USD daily (chronological) ----------
RAW = """
06-15 1.15720 1.16220 1.15660 1.15900
06-16 1.15900 1.16190 1.15730 1.16070
06-17 1.16070 1.16160 1.14770 1.14990
06-18 1.14990 1.15280 1.14500 1.14560
06-19 1.14570 1.14800 1.14160 1.14680
06-22 1.14650 1.14730 1.14180 1.14270
06-23 1.14270 1.14380 1.13740 1.13810
06-24 1.13820 1.13840 1.13240 1.13570
06-25 1.13600 1.13880 1.13330 1.13690
06-26 1.13680 1.14340 1.13530 1.13830
06-29 1.13850 1.14300 1.13770 1.14200
06-30 1.14210 1.14360 1.13810 1.14210
07-01 1.14210 1.14230 1.13610 1.13760
07-02 1.13760 1.14720 1.13730 1.14300
07-03 1.14350 1.14620 1.14190 1.14350
07-06 1.14350 1.14440 1.14080 1.14400
07-07 1.14410 1.14470 1.14070 1.14110
07-08 1.14110 1.14310 1.13900 1.14140
07-09 1.14220 1.14490 1.14120 1.14280
07-10 1.14280 1.14600 1.14100 1.14130
07-13 1.14100 1.14450 1.13770 1.13810
07-14 1.13850 1.14620 1.13760 1.14190
07-15 1.14190 1.14820 1.14050 1.14630
07-16 1.14640 1.14760 1.14300 1.14410
07-17 1.14410 1.14520 1.14240 1.14390
07-20 1.14320 1.14490 1.14020 1.14140
07-21 1.14130 1.14280 1.13960 1.13970
07-22 1.13970 1.14210 1.13960 1.14100
07-23 1.14070 1.14350 1.13630 1.13760
07-24 1.13710 1.14000 1.13640 1.13670
07-27 1.13690 1.14180 1.13650 1.13670
07-28 1.13690 1.14050 1.13530 1.13850
07-29 1.13870 1.14700 1.13740 1.14650
07-30 1.14650 1.15360 1.14320 1.15270
07-31 1.15270 1.15460 1.14530 1.15270
"""
CANDLES=[]
for ln in RAW.strip().splitlines():
    p=ln.split(); CANDLES.append(dict(d=p[0],o=float(p[1]),h=float(p[2]),l=float(p[3]),c=float(p[4])))

# ---------- Clean candlestick chart (light) ----------
def candle_chart(candles, W, H, ymin, ymax, *, price_axis=True, dates=True, grid_step=0.005,
                 markup=None, body_ratio=0.56, pad_top=64, pad_bottom=38, pad_left=10,
                 pad_right=70, font=13):
    markup=markup or {}
    plotL=pad_left; plotR=W-pad_right; plotT=pad_top; plotB=H-pad_bottom
    plotW=plotR-plotL; plotH=plotB-plotT; n=len(candles); slot=plotW/n; bw=slot*body_ratio
    def x(i): return plotL+slot*i+slot/2
    def y(pr): return plotT+(ymax-pr)/(ymax-ymin)*plotH
    s=[]
    # grid
    g=math.ceil(ymin/grid_step)*grid_step
    while g<=ymax+1e-9:
        gy=y(g)
        s.append(f'<line x1="{plotL}" y1="{gy:.1f}" x2="{plotR}" y2="{gy:.1f}" stroke="rgba(15,46,60,0.07)" stroke-width="1"/>')
        if price_axis:
            s.append(f'<text x="{plotR+10}" y="{gy+4:.1f}" fill="{MUTE}" font-size="{font}" font-family="Tajawal" font-weight="500">{g:.4f}</text>')
        g+=grid_step
    # candles
    for i,c in enumerate(candles):
        cx=x(i); up=c["c"]>=c["o"]; col=BULL if up else BEAR
        yh=y(c["h"]); yl=y(c["l"]); yo=y(c["o"]); yc=y(c["c"])
        top=min(yo,yc); bot=max(yo,yc); bh=max(bot-top,2.0)
        s.append(f'<line x1="{cx:.1f}" y1="{yh:.1f}" x2="{cx:.1f}" y2="{yl:.1f}" stroke="{col}" stroke-width="1.7"/>')
        s.append(f'<rect x="{cx-bw/2:.1f}" y="{top:.1f}" width="{bw:.1f}" height="{bh:.1f}" fill="{col}" rx="1"/>')
    if dates:
        step=max(1,n//7)
        for i in range(0,n,step):
            s.append(f'<text x="{x(i):.1f}" y="{plotB+24:.1f}" fill="{MUTE}" font-size="{font-1}" font-family="Tajawal" text-anchor="middle">{candles[i]["d"]}</text>')
    # zones
    for z in markup.get("zones",[]):
        zx=x(z["i0"])-slot/2; zw=(z["i1"]-z["i0"]+1)*slot; zy=y(z["p_hi"]); zh=y(z["p_lo"])-zy
        s.append(f'<rect x="{zx:.1f}" y="{zy:.1f}" width="{zw:.1f}" height="{zh:.1f}" fill="{z.get("fill",BULL)}" opacity="{z.get("op",0.10)}" rx="4"/>')
    # zigzag structure line
    for zz in markup.get("zigzags",[]):
        pts=" ".join(f"{x(i):.1f},{y(pr):.1f}" for i,pr in zz["pts"])
        s.append(f'<polyline points="{pts}" fill="none" stroke="{zz.get("color",LINE)}" '
                 f'stroke-width="{zz.get("w",2.4)}" stroke-dasharray="{zz.get("dash","1 7")}" '
                 f'stroke-linecap="round" stroke-linejoin="round" opacity="{zz.get("op",0.9)}"/>')
    # horizontal levels
    for lv in markup.get("levels",[]):
        ly=y(lv["price"]); x0=x(lv["from"]); x1=lv.get("to_x",plotR)
        s.append(f'<line x1="{x0:.1f}" y1="{ly:.1f}" x2="{x1:.1f}" y2="{ly:.1f}" stroke="{lv.get("color",INK)}" '
                 f'stroke-width="1.8" stroke-dasharray="7 6" opacity="0.7"/>')
        if lv.get("label"):
            s.append(f'<text x="{x0-8:.1f}" y="{ly-8:.1f}" fill="{lv.get("color",INK)}" font-size="14" '
                     f'font-family="Tajawal" font-weight="700" text-anchor="start">{lv["label"]}</text>')
    # callouts: pill + connector + marker  {i,price,text,color,px,py,marker}
    for co in markup.get("callouts",[]):
        mx=x(co["i"]); my=y(co["price"]); col=co["color"]
        px=co.get("px", mx); py=co.get("py", my-52)
        tw=co.get("w",70); th=30
        pl=px-tw/2
        pl=max(plotL+2,min(pl,plotR-tw-2))
        # connector
        s.append(f'<line x1="{mx:.1f}" y1="{my:.1f}" x2="{px:.1f}" y2="{py+(th/2 if py<my else -th/2):.1f}" '
                 f'stroke="{col}" stroke-width="1.3" opacity="0.6"/>')
        # marker
        mk=co.get("marker","dot")
        if mk=="x":
            r=8
            s.append(f'<line x1="{mx-r:.1f}" y1="{my-r:.1f}" x2="{mx+r:.1f}" y2="{my+r:.1f}" stroke="{RED}" stroke-width="3" stroke-linecap="round"/>')
            s.append(f'<line x1="{mx-r:.1f}" y1="{my+r:.1f}" x2="{mx+r:.1f}" y2="{my-r:.1f}" stroke="{RED}" stroke-width="3" stroke-linecap="round"/>')
        elif mk=="check":
            s.append(f'<circle cx="{mx:.1f}" cy="{my:.1f}" r="9" fill="none" stroke="{col}" stroke-width="2.4"/>')
            s.append(f'<polyline points="{mx-4:.1f},{my:.1f} {mx-1:.1f},{my+3.5:.1f} {mx+5:.1f},{my-4:.1f}" fill="none" stroke="{col}" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/>')
        elif mk=="hollow":
            s.append(f'<circle cx="{mx:.1f}" cy="{my:.1f}" r="7" fill="{CREAM}" stroke="{INK}" stroke-width="2.2"/>')
        else:
            s.append(f'<circle cx="{mx:.1f}" cy="{my:.1f}" r="5" fill="{col}" stroke="{CREAM}" stroke-width="1.6"/>')
        # pill
        s.append(f'<rect x="{pl:.1f}" y="{py-th/2:.1f}" width="{tw}" height="{th}" rx="15" fill="#FFFFFF" stroke="{col}" stroke-width="1.5"/>')
        s.append(f'<text x="{pl+tw/2:.1f}" y="{py+5:.1f}" fill="{col}" font-size="{co.get("fs",15)}" '
                 f'font-family="Tajawal" font-weight="800" text-anchor="middle">{co["text"]}</text>')
    # simple labels (schematics)  {i,price,text,color,above,w}
    for m in markup.get("labels",[]):
        px=x(m["i"]); py=y(m["price"]); above=m.get("above",True); col=m["color"]
        s.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="4.5" fill="{col}" stroke="{CREAM}" stroke-width="1.5"/>')
        ty=py-16 if above else py+26; tw=m.get("w",56); th=26
        tx=max(plotL+2,min(px-tw/2,plotR-tw-2))
        s.append(f'<rect x="{tx:.1f}" y="{ty-18:.1f}" width="{tw}" height="{th}" rx="13" fill="#FFFFFF" stroke="{col}" stroke-width="1.4"/>')
        s.append(f'<text x="{tx+tw/2:.1f}" y="{ty:.1f}" fill="{col}" font-size="{m.get("fs",15)}" '
                 f'font-family="Tajawal" font-weight="800" text-anchor="middle">{m["text"]}</text>')
    for a in markup.get("notes",[]):
        s.append(f'<text x="{a["x"]:.1f}" y="{a["y"]:.1f}" fill="{a.get("color",INK)}" font-size="{a.get("fs",15)}" '
                 f'font-family="Tajawal" font-weight="{a.get("weight",700)}" text-anchor="{a.get("anchor","middle")}">{a["text"]}</text>')
    for ar in markup.get("arrows",[]):
        x1,y1,x2,y2=ar["x1"],ar["y1"],ar["x2"],ar["y2"]; col=ar.get("color",TEAL)
        ang=math.atan2(y2-y1,x2-x1);L=11
        a1=(x2-L*math.cos(ang-0.4),y2-L*math.sin(ang-0.4));a2=(x2-L*math.cos(ang+0.4),y2-L*math.sin(ang+0.4))
        s.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{col}" stroke-width="2.6"/>')
        s.append(f'<polygon points="{x2:.1f},{y2:.1f} {a1[0]:.1f},{a1[1]:.1f} {a2[0]:.1f},{a2[1]:.1f}" fill="{col}"/>')
    return (f'<svg viewBox="0 0 {W} {H}" width="{W}" height="{H}" xmlns="http://www.w3.org/2000/svg">'
            +"".join(s)+'</svg>'), x, y, slot

# ---------- Synthetic schematics ----------
def synth(seq):
    out=[]
    for o,c,he,le in seq:
        out.append(dict(d="",o=o,h=max(o,c)+he,l=min(o,c)-le,c=c))
    return out
def idx_xy(cands,W,H,pt=44,pb=22,pl=16,pr=16):
    ymin=min(c["l"] for c in cands)-1.6; ymax=max(c["h"] for c in cands)+2.6
    plotL=pl;plotR=W-pr;plotT=pt;plotB=H-pb;plotW=plotR-plotL;plotH=plotB-plotT;n=len(cands);slot=plotW/n
    return (lambda i: plotL+slot*i+slot/2),(lambda pr_: plotT+(ymax-pr_)/(ymax-ymin)*plotH)
def sc_chart(cands,W,H,markup):
    ymin=min(c["l"] for c in cands)-1.6; ymax=max(c["h"] for c in cands)+2.6
    return candle_chart(cands,W,H,ymin,ymax,price_axis=False,dates=False,grid_step=(ymax-ymin)/4,
                        markup=markup,pad_top=44,pad_bottom=22,pad_left=16,pad_right=16)

up_c=synth([(10,13,1,1.5),(13,12,1.5,1),(12,17,1.2,1),(17,16,1,2),(16,15.5,.8,1.2),
            (15.5,21,1.2,1),(21,20,1,2.2),(20,19.5,.8,1),(19.5,25,1.4,1),(25,24,1,1.2)])
up_markup=dict(
  zigzags=[{"pts":[(0,up_c[0]["l"]),(2,up_c[2]["h"]),(4,up_c[4]["l"]),(5,up_c[5]["h"]),(7,up_c[7]["l"]),(8,up_c[8]["h"])],"color":TEAL,"dash":"1 8","w":3,"op":.8}],
  labels=[{"i":2,"price":up_c[2]["h"],"text":"HH","color":TEAL_D,"above":True},
          {"i":5,"price":up_c[5]["h"],"text":"HH","color":TEAL_D,"above":True},
          {"i":8,"price":up_c[8]["h"],"text":"HH","color":TEAL_D,"above":True},
          {"i":4,"price":up_c[4]["l"],"text":"HL","color":INK,"above":False},
          {"i":7,"price":up_c[7]["l"],"text":"HL","color":INK,"above":False}])
up_svg,_,_,_=sc_chart(up_c,820,430,up_markup)

dn_c=synth([(25,22,1.5,1),(22,23,1,1.5),(23,18,1,1.2),(18,19,2,1),(19,19.5,1.2,.8),
            (19.5,14,1,1.2),(14,15,2.2,1),(15,15.5,1,.8),(15.5,10,1,1.4),(10,11,1.2,1)])
dn_markup=dict(
  zigzags=[{"pts":[(0,dn_c[0]["h"]),(2,dn_c[2]["l"]),(4,dn_c[4]["h"]),(5,dn_c[5]["l"]),(7,dn_c[7]["h"]),(8,dn_c[8]["l"])],"color":RED,"dash":"1 8","w":3,"op":.75}],
  labels=[{"i":2,"price":dn_c[2]["l"],"text":"LL","color":RED,"above":False},
          {"i":5,"price":dn_c[5]["l"],"text":"LL","color":RED,"above":False},
          {"i":8,"price":dn_c[8]["l"],"text":"LL","color":RED,"above":False},
          {"i":4,"price":dn_c[4]["h"],"text":"LH","color":INK,"above":True},
          {"i":7,"price":dn_c[7]["h"],"text":"LH","color":INK,"above":True}])
dn_svg,_,_,_=sc_chart(dn_c,820,430,dn_markup)

ch_c=synth([(10,13,1,1.5),(13,12,1.5,1),(12,17,1.2,1),(17,16.5,1,1.5),(16.5,16,.8,1),
            (16,20,1.2,1),(20,18,1,1.5),(18,19,1.2,1),(19,15.5,.8,1),(15.5,13.5,.8,1.4)])
chx,chy=idx_xy(ch_c,820,430)
last_HL=ch_c[6]["l"]; ch_midx=(chx(8)+chx(9))/2
ch_markup=dict(
  zigzags=[{"pts":[(0,ch_c[0]["l"]),(2,ch_c[2]["h"]),(4,ch_c[4]["l"]),(5,ch_c[5]["h"]),(6,ch_c[6]["l"])],"color":TEAL,"dash":"1 8","w":2.6,"op":.6}],
  levels=[{"price":last_HL,"from":6,"to_x":820-16,"color":RED}],
  labels=[{"i":2,"price":ch_c[2]["h"],"text":"HH","color":TEAL_D,"above":True},
          {"i":5,"price":ch_c[5]["h"],"text":"HH","color":TEAL_D,"above":True},
          {"i":6,"price":ch_c[6]["l"],"text":"HL","color":INK,"above":False},
          {"i":9,"price":ch_c[9]["l"],"text":"LL","color":RED,"above":False}],
  notes=[{"x":ch_midx,"y":chy(ch_c[5]["h"])+2,"text":"CHoCH","color":RED,"fs":21,"weight":900}],
  arrows=[{"x1":ch_midx,"y1":chy(ch_c[5]["h"])+12,"x2":ch_midx,"y2":chy(last_HL)+2,"color":RED}])
ch_svg,_,_,_=sc_chart(ch_c,820,430,ch_markup)

cover_hero,_,_,_=sc_chart(up_c,900,360,dict(
  zigzags=[{"pts":[(0,up_c[0]["l"]),(2,up_c[2]["h"]),(4,up_c[4]["l"]),(5,up_c[5]["h"]),(7,up_c[7]["l"]),(8,up_c[8]["h"])],"color":TEAL,"dash":"1 8","w":3,"op":.8}],
  labels=[{"i":2,"price":up_c[2]["h"],"text":"HH","color":TEAL_D,"above":True},
          {"i":7,"price":up_c[7]["l"],"text":"HL","color":INK,"above":False}]))
def_chart,_,_,_=sc_chart(up_c,820,360,dict(
  zigzags=[{"pts":[(0,up_c[0]["l"]),(2,up_c[2]["h"]),(4,up_c[4]["l"]),(5,up_c[5]["h"]),(7,up_c[7]["l"]),(8,up_c[8]["h"])],"color":TEAL,"dash":"1 8","w":3,"op":.8}],
  labels=[{"i":2,"price":up_c[2]["h"],"text":"قمة","color":TEAL_D,"above":True,"w":58},
          {"i":4,"price":up_c[4]["l"],"text":"قاع","color":INK,"above":False,"w":58}]))

# ---------- REAL chart ----------
Wr,Hr=960,610; ymin_r=1.1285; ymax_r=1.1660
i_LL=7;i_SH=22;i_HL=31;i_HH=34;BOS_LVL=1.14820
def build_real():
    tmp,X,Y,slot=candle_chart(CANDLES,Wr,Hr,ymin_r,ymax_r,markup={}, pad_top=70)
    mk=dict(
      zigzags=[{"pts":[(0,CANDLES[0]["h"]),(i_LL,CANDLES[i_LL]["l"]),(i_SH,CANDLES[i_SH]["h"]),
                       (i_HL,CANDLES[i_HL]["l"]),(i_HH,CANDLES[i_HH]["h"])],"color":LINE,"dash":"1 7","w":2.2,"op":.85}],
      levels=[{"price":BOS_LVL,"from":i_SH,"to_x":Wr-70,"color":TEAL_D}],
      zones=[{"i0":i_HL-1,"i1":i_HL+1,"p_lo":1.1332,"p_hi":1.1372,"fill":BULL,"op":.14}],
      callouts=[
        {"i":i_LL,"price":CANDLES[i_LL]["l"],"text":"LL","color":RED,"px":X(i_LL),"py":Y(CANDLES[i_LL]["l"])+54,"w":54,"marker":"dot"},
        {"i":i_SH,"price":CANDLES[i_SH]["h"],"text":"قمة الهيكل","color":INK,"px":X(i_SH),"py":Y(CANDLES[i_SH]["h"])-50,"w":108,"marker":"hollow","fs":14},
        {"i":i_HL,"price":CANDLES[i_HL]["l"],"text":"HL","color":TEAL_D,"px":X(i_HL),"py":Y(CANDLES[i_HL]["l"])+54,"w":54,"marker":"check"},
        {"i":i_HH,"price":CANDLES[i_HH]["h"],"text":"HH","color":TEAL_D,"px":X(i_HH)-6,"py":Y(CANDLES[i_HH]["h"])-46,"w":54,"marker":"dot"}])
    svg,X,Y,slot=candle_chart(CANDLES,Wr,Hr,ymin_r,ymax_r,markup=mk, pad_top=70)
    bos_y=Y(BOS_LVL); brk_x=X(33)
    def arrow(x1,y1,x2,y2,col):
        ang=math.atan2(y2-y1,x2-x1);L=12
        a1=(x2-L*math.cos(ang-0.4),y2-L*math.sin(ang-0.4));a2=(x2-L*math.cos(ang+0.4),y2-L*math.sin(ang+0.4))
        return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{col}" stroke-width="2.6"/>'
                f'<polygon points="{x2:.1f},{y2:.1f} {a1[0]:.1f},{a1[1]:.1f} {a2[0]:.1f},{a2[1]:.1f}" fill="{col}"/>')
    ex=[]
    bpx=X(26)
    ex.append(f'<rect x="{bpx-34:.1f}" y="{bos_y-16:.1f}" width="68" height="31" rx="15" fill="#FFFFFF" stroke="{TEAL_D}" stroke-width="1.6"/>')
    ex.append(f'<text x="{bpx:.1f}" y="{bos_y+5:.1f}" fill="{TEAL_D}" font-size="16" font-family="Tajawal" font-weight="900" text-anchor="middle">BOS</text>')
    ex.append(arrow(brk_x,Y(1.1450),brk_x,bos_y-2,TEAL))
    ex.append(f'<text x="{X(29):.1f}" y="{Y(1.1452):.1f}" fill="{TEAL_D}" font-size="15" font-family="Tajawal" font-weight="800" text-anchor="middle">كسر الهيكل ↑</text>')
    ex.append(f'<text x="{X(4):.1f}" y="{Y(1.1628):.1f}" fill="{RED}" font-size="16" font-family="Tajawal" font-weight="800" text-anchor="middle">اتجاه هابط ↓</text>')
    ex.append(f'<text x="{X(19):.1f}" y="{Y(1.1300):.1f}" fill="{TEAL_D}" font-size="16" font-family="Tajawal" font-weight="800" text-anchor="middle">اتجاه صاعد ↑</text>')
    return svg.replace("</svg>","".join(ex)+"</svg>")
rsvg=build_real()

# ---------- Logo + wordmark ----------
GEM='''<svg viewBox="0 0 48 48" width="100%" height="100%" xmlns="http://www.w3.org/2000/svg">
<defs><linearGradient id="gm" x1="0" y1="0" x2="1" y2="1">
<stop offset="0" stop-color="#EDF2F4"/><stop offset="1" stop-color="#9CB0BA"/></linearGradient></defs>
<polygon points="24,3 39,15 33,44 15,44 9,15" fill="url(#gm)"/>
<polygon points="24,3 33,44 24,29" fill="#ffffff" opacity="0.7"/>
<polygon points="24,3 15,44 24,29" fill="#C2D0D8" opacity="0.7"/>
<polygon points="9,15 24,29 15,44" fill="#8ea6b1" opacity="0.6"/>
<polygon points="39,15 24,29 33,44" fill="#dbe6ec" opacity="0.7"/>
<polyline points="9,15 24,21 39,15" fill="none" stroke="#5b7480" stroke-width="0.7" opacity="0.5"/>
<polyline points="24,3 24,29" stroke="#5b7480" stroke-width="0.5" opacity="0.35"/>
</svg>'''
AR=str.maketrans("0123456789","٠١٢٣٤٥٦٧٨٩")
def ar(n): return str(n).translate(AR)

def brandbar(compact=False):
    sz=54 if not compact else 44
    ws=26 if not compact else 22
    return f'''<div class="brand">
      <div class="gem" style="width:{sz}px;height:{sz}px">{GEM}</div>
      <div class="wm"><span class="ln"></span><span class="wmt" style="font-size:{ws}px">LIQUIDITY STATE</span><span class="ln"></span></div>
    </div>'''
def counter(i,total=8):
    return f'<div class="counter"><b>{ar(i)}</b><i>/</i><b>{ar(total)}</b></div>'
def swipe():
    return '<div class="swipe"><span>اسحب&nbsp;&nbsp;→</span></div>'
def dots(active,total=8):
    return '<div class="dots">'+''.join(f'<span class="dot {"on" if i==active else ""}"></span>' for i in range(1,total+1))+'</div>'
def eyebrow(t):
    return f'<div class="eyebrow"><span class="dash"></span>{t}<span class="dash"></span></div>'

SL=[]
CW='data-canvas-width="1080" data-canvas-height="1350"'

# 1 Cover
SL.append(f'''<div class="slide" {CW}>
  {counter(1)}
  {brandbar()}
  <div class="cover">
    {eyebrow("درس — قراءة السوق")}
    <h1 class="big">الماركت ستركجر</h1>
    <p class="tag2">اقرأ هيكل السوق واعرف اتجاهه <b>قبل</b> لا يتحرّك</p>
    <div class="chartwrap">{cover_hero}</div>
  </div>
  {swipe()}{dots(1)}
</div>''')

# 2 What
SL.append(f'''<div class="slide" {CW}>
  {counter(2)}
  {brandbar(True)}
  <div class="cont">
    {eyebrow("التعريف")}
    <h2 class="ttl">شنو الماركت ستركجر؟</h2>
    <p class="lead">هو <b>تسلسل القمم والقيعان</b> اللي يرسمها السعر. منه تعرف السوق: <b class="tt">صاعد؟ هابط؟</b> ولا على وشك ينقلب؟</p>
    <div class="chartwrap">{def_chart}</div>
    <div class="note">بدون قراءة الهيكل، تدخل ضد الاتجاه وتسمّيه «ارتداد».</div>
  </div>
  {swipe()}{dots(2)}
</div>''')

# 3 Uptrend
SL.append(f'''<div class="slide" {CW}>
  {counter(3)}
  {brandbar(True)}
  <div class="cont">
    <div class="numrow"><span class="num">{ar(1)}</span><h2 class="ttl">الاتجاه الصاعد</h2></div>
    <div class="rule bull">قمم أعلى <b>(HH)</b> + قيعان أعلى <b>(HL)</b></div>
    <div class="chartwrap">{up_svg}</div>
    <p class="lead">كل قمة أعلى من اللي قبلها وكل قاع أعلى من اللي قبله → <b class="tt">المشترين مسيطرين</b>.</p>
  </div>
  {swipe()}{dots(3)}
</div>''')

# 4 Downtrend
SL.append(f'''<div class="slide" {CW}>
  {counter(4)}
  {brandbar(True)}
  <div class="cont">
    <div class="numrow"><span class="num">{ar(2)}</span><h2 class="ttl">الاتجاه الهابط</h2></div>
    <div class="rule bear">قمم أدنى <b>(LH)</b> + قيعان أدنى <b>(LL)</b></div>
    <div class="chartwrap">{dn_svg}</div>
    <p class="lead">كل قمة أدنى وكل قاع أدنى → <b class="tr">البائعين مسيطرين</b>. لا تشتري بحجة إنه «رخيص».</p>
  </div>
  {swipe()}{dots(4)}
</div>''')

# 5 CHoCH
SL.append(f'''<div class="slide" {CW}>
  {counter(5)}
  {brandbar(True)}
  <div class="cont">
    <div class="numrow"><span class="num">{ar(3)}</span><h2 class="ttl">لحظة الانقلاب</h2></div>
    <div class="rule neutral">أول كسر لآخر قاع/قمة مؤثرة = تغيّر طابع <b>(CHoCH)</b></div>
    <div class="chartwrap">{ch_svg}</div>
    <div class="twocol">
      <div class="term"><span class="tb">BOS</span><p>كسر يؤكد <b>استمرار</b> الاتجاه</p></div>
      <div class="term"><span class="trr">CHoCH</span><p>كسر يعلن <b>بداية انعكاسه</b></p></div>
    </div>
  </div>
  {swipe()}{dots(5)}
</div>''')

# 6 Real
SL.append(f'''<div class="slide" {CW}>
  {counter(6)}
  {brandbar(True)}
  <div class="cont">
    <div class="realhead">{eyebrow("تطبيق حقيقي")}<span class="ticker">EUR / USD · يومي</span></div>
    <div class="chartwrap big">{rsvg}</div>
    <div class="flow"><span class="fx bear">LL</span><span class="arw">←</span><span class="fx bull">HL</span><span class="arw">←</span><span class="fx lvl">BOS</span><span class="arw">←</span><span class="fx bull">HH</span></div>
    <p class="lead center">قاع أدنى ثم قاع أعلى، وبعده <b class="tt">كسر الهيكل (BOS)</b> وقمة أعلى — انقلب السوق من هابط إلى صاعد أمامك.</p>
  </div>
  <div class="botmeta">لغرض تعليمي · بيانات حقيقية</div>{dots(6)}
</div>''')

# 7 Quote
SL.append(f'''<div class="slide" {CW}>
  {counter(7)}
  {brandbar(True)}
  <div class="quote">
    <div class="qm">”</div>
    <h1 class="big2">لا تتوقّع السوق…<br><span class="tt">اقرأ هيكله.</span></h1>
    <p class="tag2 center">الاتجاه مو رأي — هو تسلسل قمم وقيعان تشوفه بعينك.</p>
  </div>
  {swipe()}{dots(7)}
</div>''')

# 8 CTA
SL.append(f'''<div class="slide" {CW}>
  {counter(8)}
  {brandbar()}
  <div class="cta">
    <h1 class="big2">خذ الدرس معك</h1>
    <div class="checkbox">
      <div class="ci"><span class="ck">✓</span><p>احفظ المنشور يرجع لك وقت التحليل</p></div>
      <div class="ci"><span class="ck">✓</span><p>شاركه مع متداول يحتاجه</p></div>
      <div class="ci"><span class="ck">✓</span><p>علّق كلمة <b class="tt">«ستركجر»</b> ويوصلك ملف PDF</p></div>
    </div>
    <p class="tag2 center">أرسلك الشرح الكامل خطوة بخطوة 📩</p>
  </div>
  <div class="botmeta">لغرض تعليمي</div>{dots(8)}
</div>''')

CSS=f'''
*{{margin:0;padding:0;box-sizing:border-box}}
body{{background:#cfcabf;font-family:'Tajawal',sans-serif}}
.slide{{position:relative;width:1080px;height:1350px;overflow:hidden;direction:rtl;
  background:radial-gradient(120% 90% at 50% 0%, #F7F3EC 0%, {CREAM} 45%, {CREAM2} 100%);color:{INK}}}
.counter{{position:absolute;top:56px;left:80px;z-index:6;direction:ltr;display:inline-flex;align-items:center;
  gap:8px;color:{TEAL_D};font-weight:800;font-size:30px;padding:6px 22px;border-radius:30px;
  border:1.5px solid {TEAL_L};background:rgba(255,255,255,0.5)}}
.counter i{{font-style:normal;opacity:.5;font-weight:600}}
.brand{{position:absolute;top:56px;left:0;right:0;display:flex;flex-direction:column;align-items:center;gap:8px;z-index:5}}
.gem{{filter:drop-shadow(0 6px 12px rgba(15,46,60,0.18))}}
.wm{{display:flex;align-items:center;gap:14px}}
.wm .ln{{width:38px;height:2px;background:{TEAL_L};display:inline-block;border-radius:2px}}
.wmt{{color:{TEAL_D};font-weight:500;letter-spacing:6px}}

.eyebrow{{display:flex;align-items:center;justify-content:center;gap:16px;color:{TEAL};
  font-weight:800;font-size:27px;letter-spacing:.5px}}
.eyebrow .dash{{width:46px;height:3px;background:{TEAL_L};border-radius:2px;display:inline-block}}

.cover{{position:absolute;top:250px;left:90px;right:90px;display:flex;flex-direction:column;align-items:center;text-align:center}}
.big{{font-size:96px;font-weight:900;color:{INK};line-height:1.08;letter-spacing:-1px;margin-top:22px}}
.big2{{font-size:82px;font-weight:900;color:{INK};line-height:1.14;letter-spacing:-1px;text-align:center}}
.tag2{{font-size:36px;color:{GREY};font-weight:500;margin-top:22px;line-height:1.5}}
.tag2 b{{color:{TEAL_D};font-weight:800}} .tag2.center{{text-align:center}}
.tt{{color:{TEAL_D}!important}} .tr{{color:{RED}!important}}
.chartwrap{{margin-top:40px;width:100%;background:#FBF9F5;border:1px solid {CARDBD};border-radius:26px;
  padding:22px;box-shadow:0 18px 44px rgba(15,46,60,0.10)}}
.chartwrap svg{{width:100%;height:auto;display:block}}
.chartwrap.big{{padding:16px}}

.cont{{position:absolute;top:190px;left:90px;right:90px;bottom:150px;display:flex;flex-direction:column;gap:26px}}
.ttl{{font-size:62px;font-weight:900;color:{INK};line-height:1.1;letter-spacing:-.5px}}
.lead{{font-size:34px;line-height:1.55;color:{GREY};font-weight:500}}
.lead b{{color:{INK};font-weight:800}} .lead.center{{text-align:center}}
.note{{font-size:30px;font-weight:700;color:{INK};background:rgba(46,125,150,0.09);
  border-right:6px solid {TEAL};border-radius:14px;padding:20px 24px}}
.numrow{{display:flex;align-items:center;gap:20px}}
.num{{width:78px;height:78px;flex:none;display:flex;align-items:center;justify-content:center;font-size:44px;
  font-weight:900;color:#fff;background:linear-gradient(135deg,{TEAL},{TEAL_D});border-radius:22px;
  box-shadow:0 10px 22px rgba(46,125,150,0.30)}}
.rule{{font-size:35px;font-weight:700;padding:18px 26px;border-radius:16px;color:{INK};
  background:#FBF9F5;border:1px solid {CARDBD}}}
.rule b{{font-weight:900}}
.rule.bull{{border-right:6px solid {TEAL}}} .rule.bull b{{color:{TEAL_D}}}
.rule.bear{{border-right:6px solid {RED}}} .rule.bear b{{color:{RED}}}
.rule.neutral{{border-right:6px solid {INK}}} .rule.neutral b{{color:{INK}}}
.twocol{{display:flex;gap:20px}}
.term{{flex:1;background:#FBF9F5;border:1px solid {CARDBD};border-radius:18px;padding:22px;text-align:center}}
.term p{{font-size:27px;color:{GREY};margin-top:10px;font-weight:600}} .term b{{color:{INK}}}
.tb{{font-size:42px;font-weight:900;color:{TEAL_D}}} .trr{{font-size:42px;font-weight:900;color:{RED}}}

.realhead{{display:flex;align-items:center;justify-content:space-between}}
.ticker{{color:{TEAL_D};font-weight:800;font-size:30px;background:rgba(46,125,150,0.10);
  padding:6px 18px;border-radius:12px;border:1px solid {TEAL_L}}}
.flow{{display:flex;align-items:center;justify-content:center;gap:12px}}
.fx{{font-weight:900;font-size:28px;padding:8px 22px;border-radius:12px}}
.fx.bull{{color:#fff;background:{BULL}}} .fx.bear{{color:#fff;background:{BEAR}}}
.fx.lvl{{color:{INK};background:#fff;border:1.5px solid {TEAL_D}}}
.arw{{color:{MUTE};font-size:26px;font-weight:900}}

.quote{{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:0 110px;text-align:center}}
.qm{{font-size:170px;color:{TEAL_L};line-height:.5;font-weight:900;opacity:.6;margin-bottom:24px}}
.quote .big2{{font-size:92px}} .quote .tag2{{margin-top:34px}}

.cta{{position:absolute;top:210px;left:90px;right:90px;bottom:150px;display:flex;flex-direction:column;
  align-items:center;justify-content:center;gap:40px}}
.checkbox{{width:100%;background:#FBF9F5;border:1px solid {CARDBD};border-radius:24px;padding:14px 26px;
  box-shadow:0 16px 40px rgba(15,46,60,0.10)}}
.ci{{display:flex;align-items:center;gap:18px;padding:22px 4px;border-bottom:1px solid #EDE7DB}}
.ci:last-child{{border-bottom:none}}
.ci p{{font-size:32px;font-weight:700;color:{INK}}} .ci p b{{font-weight:900}}
.ck{{width:48px;height:48px;flex:none;display:flex;align-items:center;justify-content:center;border-radius:50%;
  border:2.5px solid {TEAL};color:{TEAL_D};font-size:26px;font-weight:900}}

.swipe{{position:absolute;bottom:96px;left:0;right:0;display:flex;justify-content:center;z-index:6}}
.swipe span{{color:{TEAL_D};font-weight:800;font-size:28px;padding:10px 34px;
  border:1.5px solid {TEAL_L};border-radius:30px;background:rgba(255,255,255,0.5)}}
.botmeta{{position:absolute;bottom:100px;left:0;right:0;text-align:center;color:{MUTE};font-size:24px;font-weight:600}}
.dots{{position:absolute;bottom:54px;left:0;right:0;display:flex;gap:10px;justify-content:center;z-index:6}}
.dot{{width:10px;height:10px;border-radius:50%;background:rgba(15,46,60,0.18)}}
.dot.on{{background:{TEAL};width:30px;border-radius:6px}}
'''

HTML=f'''<!DOCTYPE html><html lang="ar" dir="rtl"><head><meta charset="UTF-8">
<title>الماركت ستركجر — Liquidity State</title>
<meta name="hz:slide-selector" content=".slide">
<meta name="hz:canvas-width" content="1080"><meta name="hz:canvas-height" content="1350">
<style>{FONT_CSS}\n{CSS}</style></head><body>
{''.join(SL)}
</body></html>'''
with open(os.path.join(HERE,"carousel.html"),"w",encoding="utf-8") as f:
    f.write(HTML)
print("wrote carousel.html", len(HTML), "bytes", len(SL), "slides")
