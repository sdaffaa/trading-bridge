# -*- coding: utf-8 -*-
import base64, os, math, json
HERE=os.path.dirname(os.path.abspath(__file__)); FONTS=os.path.join(HERE,"fonts")

CREAM="#F2EEE7"; CREAM2="#ECE6DB"; INK="#0F2E3C"; TEAL="#2E7D96"; TEAL_D="#1E627A"
TEAL_L="#5AA6BC"; BULL="#2E8CA6"; BEAR="#122F3E"; RED="#D24B4B"; GREY="#5C6C73"
MUTE="#93A2A8"; LINE="#7C8C93"; CARDBD="#DED8CC"
CYAN="#43D4DC"; CYANG="rgba(67,212,220,0.55)"  # brand poster cyan glow

def ff(name,fn,w):
    with open(os.path.join(FONTS,fn),"rb") as f: b=base64.b64encode(f.read()).decode()
    return f"@font-face{{font-family:'{name}';font-weight:{w};font-display:block;src:url(data:font/ttf;base64,{b}) format('truetype')}}"
FONT_CSS="\n".join([ff("Tajawal","Tajawal-Regular.ttf",400),ff("Tajawal","Tajawal-Medium.ttf",500),
    ff("Tajawal","Tajawal-Bold.ttf",700),ff("Tajawal","Tajawal-ExtraBold.ttf",800),ff("Tajawal","Tajawal-Black.ttf",900)])

RAW="""06-15 1.15720 1.16220 1.15660 1.15900
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
07-31 1.15270 1.15460 1.14530 1.15270"""
C=[dict(d=p[0],o=float(p[1]),h=float(p[2]),l=float(p[3]),c=float(p[4])) for p in (l.split() for l in RAW.strip().splitlines())]

def chart(cands,W,H,ymin,ymax,*,price_axis=False,dates=False,grid=4,pl=14,pr=64,pt=40,pb=34,brk=None,body=0.56,pstep=None):
    plotL=pl;plotR=W-pr;plotT=pt;plotB=H-pb;pw=plotR-plotL;ph=plotB-plotT;n=len(cands);slot=pw/n;bw=slot*body
    def x(i):return plotL+slot*i+slot/2
    def y(p):return plotT+(ymax-p)/(ymax-ymin)*ph
    s=[]
    gs=(ymax-ymin)/grid
    for k in range(grid+1):
        gy=y(ymin+gs*k); s.append(f'<line x1="{plotL}" y1="{gy:.1f}" x2="{plotR}" y2="{gy:.1f}" stroke="rgba(15,46,60,0.06)" stroke-width="1"/>')
    if price_axis:
        if pstep is None: pstep=0.005
        elif pstep=="auto":
            pstep=next(st for st in (0.0005,0.001,0.002,0.0025,0.005,0.01,0.02,0.05) if (ymax-ymin)/st<=6.5)
        dec=5 if pstep<0.001 else 4
        gg=math.ceil(ymin/pstep)*pstep
        while gg<=ymax+1e-9:
            gy=y(gg); s.append(f'<text x="{plotR+14}" y="{gy+4:.1f}" fill="{MUTE}" font-size="12" font-family="Tajawal" font-weight="500">{gg:.{dec}f}</text>'); gg+=pstep
    if dates:
        st=max(1,n//7)
        for i in range(0,n,st): s.append(f'<text x="{x(i):.1f}" y="{plotB+22:.1f}" fill="{MUTE}" font-size="11" font-family="Tajawal" text-anchor="middle">{cands[i]["d"]}</text>')
    for i,c in enumerate(cands):
        cx=x(i);up=c["c"]>=c["o"];col=BULL if up else BEAR
        yh=y(c["h"]);yl=y(c["l"]);yo=y(c["o"]);yc=y(c["c"]);top=min(yo,yc);bot=max(yo,yc);bh=max(bot-top,2.0)
        cls="cndl"+(" brk" if brk and i in brk else "")
        s.append(f'<g class="{cls}"><line x1="{cx:.1f}" y1="{yh:.1f}" x2="{cx:.1f}" y2="{yl:.1f}" stroke="{col}" stroke-width="1.7"/>'
                 f'<rect x="{cx-bw/2:.1f}" y="{top:.1f}" width="{bw:.1f}" height="{bh:.1f}" fill="{col}" rx="1"/></g>')
    svg=f'<svg class="chartsvg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" xmlns="http://www.w3.org/2000/svg">'+"".join(s)
    return svg,x,y,slot

import random as _rnd
def gen(anchors,n,seed,wick=0.9,bn=0.5,swings=None):
    _rnd.seed(seed); xs=[a[0] for a in anchors]; ys=[a[1] for a in anchors]
    def line(i):
        if i<=xs[0]: return ys[0]
        for k in range(len(xs)-1):
            if xs[k]<=i<=xs[k+1]:
                t=(i-xs[k])/(xs[k+1]-xs[k]); return ys[k]+(ys[k+1]-ys[k])*t
        return ys[-1]
    cs=[]; prev=line(0); vol=1.0
    for i in range(n):
        lv=line(i); o=prev
        # volatility clustering: quiet stretches vs active stretches
        vol=max(0.4,min(2.0,vol*_rnd.uniform(0.78,1.28)))
        dev=_rnd.uniform(-bn,bn)*vol
        r=_rnd.random()
        if r<0.16:      # doji / tiny body
            c=o+max(-0.13,min(0.13,(lv+dev)-o))
        elif r>0.90:    # impulse candle
            c=lv+dev+(1 if lv>=o else -1)*_rnd.uniform(0.7,1.2)*bn*vol
        else:           # regular body
            c=lv+dev
        # wicks: squared randomness -> mostly short, occasionally long pin bars
        hi=max(o,c)+0.05+wick*vol*(_rnd.random()**2.2)*1.7
        lo=min(o,c)-0.05-wick*vol*(_rnd.random()**2.2)*1.7
        cs.append(dict(o=o,h=hi,l=lo,c=c)); prev=c
    for idx,typ in (swings or []):
        w=range(max(0,idx-2),min(n,idx+3))
        if typ=='H': cs[idx]["h"]=max(cs[j]["h"] for j in w)+0.5
        else: cs[idx]["l"]=min(cs[j]["l"] for j in w)-0.5
    return cs
# dense teaching charts (~30 candles) with known swing indices
UP =gen([(0,10),(6,16.5),(11,13),(17,20.5),(22,17.5),(28,25.5)],30,7,swings=[(6,'H'),(11,'L'),(17,'H'),(22,'L'),(28,'H')])
UPz=[(0,'l'),(6,'h'),(11,'l'),(17,'h'),(22,'l'),(28,'h')]; UPh=[6,17,28]; UPl=[11,22]
DN =gen([(0,26),(6,19),(11,22),(17,15),(22,18),(28,10.5)],30,8,swings=[(6,'L'),(11,'H'),(17,'L'),(22,'H'),(28,'L')])
DNz=[(0,'h'),(6,'l'),(11,'h'),(17,'l'),(22,'h'),(28,'l')]; DNl=[6,17,28]; DNh=[11,22]
CH =gen([(0,11),(5,15.5),(9,13),(14,20),(19,15.5),(23,18.5),(29,11.5)],30,9,swings=[(5,'H'),(9,'L'),(14,'H'),(19,'L'),(23,'H'),(29,'L')])
CHz=[(0,'l'),(5,'h'),(9,'l'),(14,'h'),(19,'l'),(23,'h'),(29,'l')]
SW =gen([(0,12),(5,14),(9,17),(13,13),(17,10),(21,13)],22,5,swings=[(9,'H'),(17,'L')])
MUP=gen([(0,10),(4,14),(7,12),(11,16.5)],12,11,wick=0.7,bn=0.4,swings=[(4,'H'),(7,'L')])
MCH=gen([(0,10),(4,14),(7,12),(9,15),(11,10.5)],12,14,wick=0.7,bn=0.4,swings=[(4,'H'),(7,'L'),(9,'H')])
MDN=gen([(0,16),(4,12),(7,13.5),(11,9)],12,12,wick=0.7,bn=0.4,swings=[(4,'L'),(7,'H')])
RNG=gen([(0,13),(3,14),(6,12.5),(9,14),(11,12.8)],12,13,wick=0.7,bn=0.4)

def htext(x,y,txt,col,fs,anchor="middle",italic=False,weight=900):
    it=' font-style="italic"' if italic else ''
    return (f'<text x="{x:.1f}" y="{y:.1f}" fill="{col}" font-size="{fs}" font-family="Tajawal" font-weight="{weight}"{it} '
            f'text-anchor="{anchor}" paint-order="stroke" stroke="{CREAM}" stroke-width="6.5" stroke-linejoin="round">{txt}</text>')
def lbl(x,y,txt,col,above=True,w=54,fs=15,cls="mk"):
    ty=y-15 if above else y+26
    return (f'<g class="{cls}"><circle cx="{x:.1f}" cy="{y:.1f}" r="4.5" fill="{col}" stroke="{CREAM}" stroke-width="1.5"/>'
            f'{htext(x,ty,txt,col,fs+3)}</g>')

def zzline(x,y,pts,col,w=3,op=0.8,dash=None,cls="draw"):
    p=" ".join(f"{x(i):.1f},{y(v):.1f}" for i,v in pts)
    d=f'stroke-dasharray="{dash}" ' if dash else ''
    return f'<polyline class="{cls}" points="{p}" fill="none" stroke="{col}" stroke-width="{w}" {d}stroke-linecap="round" stroke-linejoin="round" opacity="{op}"/>'

# ---- schematics ----
def _zpts(cs,z): return [(i,cs[i]["h"] if t=='h' else cs[i]["l"]) for i,t in z]
# distinct dataset for the definition scene (no chart repeats across scenes)
UPD=gen([(0,13),(4,16.8),(9,14.5),(15,19.5),(20,17),(28,22.5)],30,55,swings=[(4,'H'),(9,'L'),(15,'H'),(20,'L'),(28,'H')])
UPDz=[(0,'l'),(4,'h'),(9,'l'),(15,'h'),(20,'l'),(28,'h')]
def sc_def_up():
    cs=UPD; W,H=980,460; ymin=min(c["l"] for c in cs)-1.5;ymax=max(c["h"] for c in cs)+2.8
    svg,x,y,_=chart(cs,W,H,ymin,ymax,grid=4,pt=48,pb=22,pl=16,pr=16,body=0.5)
    svg+=zzline(x,y,_zpts(cs,UPDz),TEAL_D,w=2.2,op=.5)
    svg+=lbl(x(15),y(cs[15]["h"]),"قمة",TEAL_D,True)
    svg+=lbl(x(20),y(cs[20]["l"]),"قاع",INK,False)
    return svg+"</svg>"
def sc_up():
    cs=UP; W,H=980,460; ymin=min(c["l"] for c in cs)-1.5;ymax=max(c["h"] for c in cs)+2.8
    svg,x,y,_=chart(cs,W,H,ymin,ymax,grid=4,pt=48,pb=22,pl=16,pr=16,body=0.5)
    svg+=zzline(x,y,_zpts(cs,UPz),TEAL_D,w=2.2,op=.5)
    for i in UPh: svg+=lbl(x(i),y(cs[i]["h"]),"HH",TEAL_D,True)
    for i in UPl: svg+=lbl(x(i),y(cs[i]["l"]),"HL",INK,False)
    return svg+"</svg>"
def sc_dn():
    cs=DN; W,H=980,460; ymin=min(c["l"] for c in cs)-2.6;ymax=max(c["h"] for c in cs)+1.6
    svg,x,y,_=chart(cs,W,H,ymin,ymax,grid=4,pt=48,pb=22,pl=16,pr=16,body=0.5)
    svg+=zzline(x,y,_zpts(cs,DNz),RED,w=2.2,op=.45)
    for i in DNl: svg+=lbl(x(i),y(cs[i]["l"]),"LL",RED,False)
    for i in DNh: svg+=lbl(x(i),y(cs[i]["h"]),"LH",INK,True)
    return svg+"</svg>"
def sc_ch():
    cs=CH; W,H=980,460; ymin=min(c["l"] for c in cs)-2.0;ymax=max(c["h"] for c in cs)+2.6
    svg,x,y,_=chart(cs,W,H,ymin,ymax,grid=4,pt=48,pb=22,pl=16,pr=16,body=0.5)
    hl=cs[19]["l"]; bi=26
    svg+=zzline(x,y,_zpts(cs,CHz),TEAL_D,w=2.0,op=.45)
    svg+=f'<line class="draw" x1="{x(19):.1f}" y1="{y(hl):.1f}" x2="{W-16:.1f}" y2="{y(hl):.1f}" stroke="{RED}" stroke-width="2.2" stroke-dasharray="7 6" opacity="0.85"/>'
    svg+=lbl(x(5),y(cs[5]["h"]),"HH",TEAL_D,True)+lbl(x(14),y(cs[14]["h"]),"HH",TEAL_D,True)
    svg+=lbl(x(9),y(cs[9]["l"]),"HL",INK,False)+lbl(x(19),y(cs[19]["l"]),"HL",INK,False)
    svg+=lbl(x(29),y(cs[29]["l"]),"LL",RED,False)
    svg+=(f'<g class="pop2">{htext(x(bi)-8,y(hl)-54,"CHoCH",RED,22)}'
          f'<line x1="{x(bi):.1f}" y1="{y(hl)-42:.1f}" x2="{x(bi):.1f}" y2="{y(hl)+4:.1f}" stroke="{RED}" stroke-width="2.6"/>'
          f'<polygon points="{x(bi):.1f},{y(hl)+4:.1f} {x(bi)-6:.1f},{y(hl)-8:.1f} {x(bi)+6:.1f},{y(hl)-8:.1f}" fill="{RED}"/></g>')
    return svg+"</svg>"
def sc_swing():
    cs=SW; W,H=980,460; ymin=min(c["l"] for c in cs)-2.4;ymax=max(c["h"] for c in cs)+2.8
    svg,x,y,_=chart(cs,W,H,ymin,ymax,grid=4,pt=48,pb=22,pl=16,pr=16,body=0.5)
    svg+=f'<g class="pop"><circle cx="{x(9):.1f}" cy="{y(cs[9]["h"]):.1f}" r="7" fill="{CREAM}" stroke="{TEAL_D}" stroke-width="2.4"/></g>'
    svg+=f'<g class="pop"><circle cx="{x(17):.1f}" cy="{y(cs[17]["l"]):.1f}" r="7" fill="{CREAM}" stroke="{RED}" stroke-width="2.4"/></g>'
    svg+=f'<g class="pop">{htext(x(9),y(cs[9]["h"])-18,"قمة مؤثرة",TEAL_D,19)}</g>'
    svg+=f'<g class="pop">{htext(x(17),y(cs[17]["l"])+28,"قاع مؤثر",RED,19)}</g>'
    return svg+"</svg>"
def mini(cands,W,H):
    svg,x,y,_=chart(cands,W,H,min(c["l"] for c in cands)-1.4,max(c["h"] for c in cands)+2.0,grid=3,pt=28,pb=14,pl=12,pr=12,body=0.5)
    return svg,x,y
def mini_bos():
    W,H=440,300; svg,x,y=mini(MUP,W,H); lv=MUP[4]["h"]; bx=x(10)
    svg+=f'<line class="draw" x1="{x(4):.1f}" y1="{y(lv):.1f}" x2="{W-12:.1f}" y2="{y(lv):.1f}" stroke="{TEAL_D}" stroke-width="1.8" stroke-dasharray="5 5" opacity="0.85"/>'
    svg+=f'<g class="brkfx2"><line x1="{bx:.1f}" y1="{y(MUP[7]["l"]):.1f}" x2="{bx:.1f}" y2="{y(lv)-2:.1f}" stroke="{TEAL}" stroke-width="2.4"/><polygon points="{bx:.1f},{y(lv)-2:.1f} {bx-5:.1f},{y(lv)+9:.1f} {bx+5:.1f},{y(lv)+9:.1f}" fill="{TEAL}"/></g>'
    return svg+"</svg>"
def mini_choch():
    W,H=440,300; svg,x,y=mini(MCH,W,H); lv=MCH[7]["l"]; bx=x(11)
    svg+=f'<line class="draw" x1="{x(7):.1f}" y1="{y(lv):.1f}" x2="{W-12:.1f}" y2="{y(lv):.1f}" stroke="{RED}" stroke-width="1.8" stroke-dasharray="5 5" opacity="0.85"/>'
    svg+=f'<g class="brkfx2"><line x1="{bx:.1f}" y1="{y(MCH[9]["h"]):.1f}" x2="{bx:.1f}" y2="{y(lv)+15:.1f}" stroke="{RED}" stroke-width="2.4"/><polygon points="{bx:.1f},{y(lv)+15:.1f} {bx-5:.1f},{y(lv)+4:.1f} {bx+5:.1f},{y(lv)+4:.1f}" fill="{RED}"/></g>'
    return svg+"</svg>"
def mini_state(cands,col_line):
    W,H=320,200; svg,x,y=mini(cands,W,H)
    return svg+"</svg>"

def hend(cx,cy,col):  # circle endpoint handle (TradingView style)
    return f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="5.5" fill="{CREAM}" stroke="{col}" stroke-width="2"/>'
def sc_real():
    W,H=980,660; ymin=1.1268;ymax=1.1665
    iLL,iSH,iHL,iHH=7,22,31,34
    BOSv=C[iSH]["h"]; HLv=C[iHL]["l"]; LLv=C[iLL]["l"]; HHv=C[iHH]["h"]  # exact wick prices
    svg,x,y,slot=chart(C,W,H,ymin,ymax,price_axis=True,dates=True,grid=5,pt=54,pb=40,pl=12,pr=70,brk={33,34})
    # range/accumulation box: exactly BOS-high (top) to HL-low (bottom), idx22..32 — teal wash
    bx0,bx1=iSH,32
    rx0=x(bx0)-slot/2; rw=(bx1-bx0+1)*slot; ry0=y(BOSv); rh=y(HLv)-y(BOSv)
    svg+=f'<rect class="boxpop" x="{rx0:.2f}" y="{ry0:.2f}" width="{rw:.2f}" height="{rh:.2f}" fill="{TEAL}" stroke="{TEAL_D}" stroke-width="1"/>'
    # structure zigzag on exact wick tips
    svg+=zzline(x,y,[(0,C[0]["h"]),(iLL,LLv),(iSH,BOSv),(iHL,HLv),(iHH,HHv)],TEAL_D,w=2.0,op=.55,dash="1 7",cls="draw zz")
    # BOS ray (navy) — sits exactly on the swing-high wick, left end = box top-left
    lx0=rx0; lx1=W-70; ly=y(BOSv)
    svg+=f'<line class="draw hray" x1="{lx0:.2f}" y1="{ly:.2f}" x2="{lx1:.2f}" y2="{ly:.2f}" stroke="{INK}" stroke-width="1.8"/>'
    svg+=f'<g class="pop">{hend(lx0,ly,INK)}{hend(lx1,ly,INK)}{htext(lx0+12,ly-12,"BOS",INK,22,"start",weight=800)}</g>'
    # SSL ray (navy) exactly on the major-low wick
    sy=y(LLv); sx0=x(iLL); sx1=x(iLL+9)
    svg+=f'<line class="draw hray" x1="{sx0:.2f}" y1="{sy:.2f}" x2="{sx1:.2f}" y2="{sy:.2f}" stroke="{INK}" stroke-width="1.6" stroke-dasharray="6 5"/>'
    svg+=f'<g class="pop">{hend(sx0,sy,INK)}{hend(sx1,sy,INK)}{htext(sx1+18,sy+6,"SSL",INK,18,"start",weight=800)}</g>'
    # structure markers snapped to exact wick tips (frameless)
    def marker(i,txt,col,low,cls="pop",tdx=0):
        mx=x(i); my=y(C[i]["l"] if low else C[i]["h"]); ty=my+26 if low else my-15
        return (f'<g class="{cls}"><circle cx="{mx:.2f}" cy="{my:.2f}" r="4.5" fill="{col}" stroke="{CREAM}" stroke-width="1.5"/>'
                f'{htext(mx+tdx,ty,txt,col,20)}</g>')
    svg+=marker(iLL,"LL",INK,True)+marker(iHL,"HL",TEAL_D,True)
    # breakout arrow (teal) — starts inside range, tip lands exactly on the BOS line at the breakout candle
    brkx=x(33)
    svg+=(f'<g class="brkfx"><line x1="{brkx:.2f}" y1="{y(1.14350):.2f}" x2="{brkx:.2f}" y2="{ly:.2f}" stroke="{TEAL_D}" stroke-width="2.4"/>'
          f'<polygon points="{brkx:.2f},{ly:.2f} {brkx-6:.2f},{ly+11:.2f} {brkx+6:.2f},{ly+11:.2f}" fill="{TEAL_D}"/>'
          f'{htext(x(29),y(1.14150),"Breakout",TEAL_D,19,italic=True,weight=800)}</g>')
    svg+=marker(iHH,"HH",TEAL_D,False,cls="hhpop",tdx=-22)
    svg+=f'<g class="pop">{htext(x(4),y(1.1632),"هابط ↓",INK,17,weight=800)}</g>'
    svg+=f'<g class="hhpop">{htext(x(19),y(1.1300),"صاعد ↑",TEAL_D,17,weight=800)}</g>'
    svg+=f'<rect class="flash" x="0" y="0" width="{W}" height="{H}" fill="#ffffff" opacity="0"/>'
    return svg+"</svg>"

# ---- precise icosahedron gem (20 faces, computed) ----
_PHI=(1+5**0.5)/2
_V=[(0,1,_PHI),(0,1,-_PHI),(0,-1,_PHI),(0,-1,-_PHI),(1,_PHI,0),(1,-_PHI,0),(-1,_PHI,0),(-1,-_PHI,0),(_PHI,0,1),(_PHI,0,-1),(-_PHI,0,1),(-_PHI,0,-1)]
def _d2(a,b): return sum((a[i]-b[i])**2 for i in range(3))
_mind=min(_d2(_V[i],_V[j]) for i in range(12) for j in range(i+1,12))
_FACES=[(i,j,k) for i in range(12) for j in range(i+1,12) for k in range(j+1,12)
        if abs(_d2(_V[i],_V[j])-_mind)<1e-6 and abs(_d2(_V[j],_V[k])-_mind)<1e-6 and abs(_d2(_V[i],_V[k])-_mind)<1e-6]
def _gem(rx,ry=0.0,rz=0.0,size=48,pad=2.5,light=(-0.32,0.74,0.6),edge="#54687a",edgew=0.32):
    cx_,sx_=math.cos(rx),math.sin(rx); cy_,sy_=math.cos(ry),math.sin(ry); cz_,sz_=math.cos(rz),math.sin(rz)
    def mm(A,B): return [[sum(A[r][t]*B[t][c] for t in range(3)) for c in range(3)] for r in range(3)]
    Rx=[[1,0,0],[0,cx_,-sx_],[0,sx_,cx_]]; Ry=[[cy_,0,sy_],[0,1,0],[-sy_,0,cy_]]; Rz=[[cz_,-sz_,0],[sz_,cz_,0],[0,0,1]]
    R=mm(mm(Rz,Ry),Rx)
    def mv(v): return (sum(R[0][i]*v[i] for i in range(3)),sum(R[1][i]*v[i] for i in range(3)),sum(R[2][i]*v[i] for i in range(3)))
    RV=[mv(v) for v in _V]
    lm=math.sqrt(sum(c*c for c in light)); L=tuple(c/lm for c in light)
    tris=[]
    for (i,j,k) in _FACES:
        a,b,c=RV[i],RV[j],RV[k]
        ux=(b[0]-a[0],b[1]-a[1],b[2]-a[2]); vx=(c[0]-a[0],c[1]-a[1],c[2]-a[2])
        n=(ux[1]*vx[2]-ux[2]*vx[1],ux[2]*vx[0]-ux[0]*vx[2],ux[0]*vx[1]-ux[1]*vx[0])
        nm=math.sqrt(sum(t*t for t in n)) or 1; n=tuple(t/nm for t in n)
        cen=((a[0]+b[0]+c[0])/3,(a[1]+b[1]+c[1])/3,(a[2]+b[2]+c[2])/3)
        if sum(n[i]*cen[i] for i in range(3))<0: n=(-n[0],-n[1],-n[2])
        if n[2]<=0.02: continue
        inten=0.30+0.70*max(0.0,sum(n[i]*L[i] for i in range(3)))
        tris.append(((a[2]+b[2]+c[2])/3,inten,(a,b,c)))
    tris.sort(key=lambda t:t[0])
    xs=[p[0] for _,_,tri in tris for p in tri]; ys=[p[1] for _,_,tri in tris for p in tri]
    sc=(size-2*pad)/max(max(xs)-min(xs),max(ys)-min(ys))
    ox=size/2-(min(xs)+max(xs))/2*sc; oy=size/2+(min(ys)+max(ys))/2*sc
    def sh(t):
        c0=(80,101,113); c1=(242,247,250); return "#%02x%02x%02x"%tuple(int(a+(b-a)*t) for a,b in zip(c0,c1))
    out=[f'<svg viewBox="0 0 {size} {size}" width="100%" height="100%" xmlns="http://www.w3.org/2000/svg">']
    for _,inten,tri in tris:
        pts=" ".join(f"{ox+p[0]*sc:.2f},{oy-p[1]*sc:.2f}" for p in tri)
        out.append(f'<polygon points="{pts}" fill="{sh(inten)}" stroke="{edge}" stroke-width="{edgew}" stroke-linejoin="round"/>')
    return "".join(out)+"</svg>"
GEM=_gem(math.radians(54.0))
def logo(top=110):
    return f'<div class="logo" style="top:{top}px"><div class="g">{GEM}</div><div class="wm"><span class="ln"></span><span class="wmt">LIQUIDITY STATE</span><span class="ln"></span></div></div>'
# cyan line icons for the poster
IUP=f'<svg viewBox="0 0 40 40" xmlns="http://www.w3.org/2000/svg"><circle cx="20" cy="20" r="17" fill="none" stroke="{CYAN}" stroke-width="2"/><path d="M20 28 V13 M13.5 19.5 L20 13 L26.5 19.5" fill="none" stroke="{CYAN}" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/></svg>'
IDN=f'<svg viewBox="0 0 40 40" xmlns="http://www.w3.org/2000/svg"><circle cx="20" cy="20" r="17" fill="none" stroke="{CYAN}" stroke-width="2"/><path d="M20 12 V27 M13.5 20.5 L20 27 L26.5 20.5" fill="none" stroke="{CYAN}" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/></svg>'
ISW=f'<svg viewBox="0 0 40 40" xmlns="http://www.w3.org/2000/svg"><circle cx="20" cy="20" r="17" fill="none" stroke="{CYAN}" stroke-width="2"/><path d="M14 16 H26 L22 12 M26 24 H14 L18 28" fill="none" stroke="{CYAN}" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/></svg>'
A=str.maketrans("0123456789","٠١٢٣٤٥٦٧٨٩")
def ar(n): return str(n).translate(A)

# ============ SCENES ============
scenes=[]
def scene(id,dur,html): scenes.append({"id":id,"dur":dur,"html":html,"tw":[]})
def T(sel,ls,d,sp,stag=0): scenes[-1]["tw"].append([sel,round(ls,3),d,sp,stag])

# 1 POSTER (dark brand cover)
scene("s1",4.8,f'''<div class="poster">
  <div class="ptag">درس الماركت ستركجر</div>
  <div class="pgem">{GEM}</div>
  <div class="pwm"><span class="pln l"></span><span class="pwmt">LIQUIDITY STATE</span><span class="pln r"></span></div>
  <div class="pdivg pd1"><span></span><i></i><span></span></div>
  <h1 class="ptitle">الماركت<br>ستركجر</h1>
  <div class="pdivg pd2"><span></span><i></i><span></span></div>
  <div class="peyeb">اقرأ السوق قبل لا يتحرّك</div>
  <div class="psub2">هيكل السوق يكشف لك الاتجاه — تعلّم تقرأه صح</div>
  <div class="ppill">٣ مفاهيم أساسية</div>
  <div class="prow">
    <div class="pi p_a"><div class="pic">{IUP}</div><span>صاعد؟</span></div>
    <div class="pv"></div>
    <div class="pi p_b"><div class="pic">{IDN}</div><span>هابط؟</span></div>
    <div class="pv"></div>
    <div class="pi p_c"><div class="pic">{ISW}</div><span>انقلاب؟</span></div>
  </div></div>''')
T(".pgem",0.1,0.6,{"op":[0,1],"s":[.7,1],"ease":"ob"})
T(".pwm",0.55,0.5,{"op":[0,1],"ty":[14,0],"ease":"oc"})
T(".pd1",0.8,0.45,{"op":[0,1],"s":[.4,1],"ease":"oc"})
T(".ptitle",0.95,0.6,{"op":[0,1],"s":[.86,1],"ease":"ob"})
T(".pd2",1.6,0.4,{"op":[0,1],"s":[.4,1],"ease":"oc"})
T(".peyeb",1.75,0.45,{"op":[0,1],"ty":[16,0],"ease":"oc"})
T(".psub2",2.0,0.45,{"op":[0,1],"ty":[16,0],"ease":"oc"})
T(".ppill",2.35,0.45,{"op":[0,1],"s":[.7,1],"ease":"ob"})
T(".p_a",2.7,0.4,{"op":[0,1],"ty":[18,0],"ease":"oc"})
T(".p_b",2.85,0.4,{"op":[0,1],"ty":[18,0],"ease":"oc"})
T(".p_c",3.0,0.4,{"op":[0,1],"ty":[18,0],"ease":"oc"})

# 2 PROBLEM
scene("s2",4.8,f'''{logo(160)}<div class="mid">
  <div class="a eyeb">المشكلة</div>
  <div class="b titan2">تحلّل بالإحساس؟</div>
  <div class="c hooksub">السوق يتكلم بلغة وحدة فقط:<br><b>القمم والقيعان</b></div>
  <div class="d pillrow"><span class="pl">شراء عشوائي</span><span class="pl">ستوب سريع</span><span class="pl">حيرة</span></div></div>''')
T(".a",0.15,0.4,{"op":[0,1],"ty":[20,0],"ease":"oc"})
T(".b",0.45,0.55,{"op":[0,1],"s":[.75,1],"ease":"ob"})
T(".c",1.1,0.5,{"op":[0,1],"ty":[20,0],"ease":"oc"})
T(".d .pl",1.9,0.4,{"op":[0,1],"s":[.6,1],"ease":"ob"},0.22)

# 3 WHAT
scene("s3",5.4,f'''{logo(150)}<div class="mid">
  <div class="a eyeb">الحل</div>
  <div class="b titan">الماركت<br>ستركجر</div>
  <div class="c hooksub">تسلسل القمم والقيعان اللي يكشف الاتجاه</div>
  <div class="d chartbox">{sc_def_up()}</div></div>''')
T(".a",0.2,0.4,{"op":[0,1],"ty":[20,0],"ease":"oc"})
T(".b",0.5,0.6,{"op":[0,1],"s":[.75,1],"ease":"ob"})
T(".c",1.2,0.5,{"op":[0,1],"ty":[20,0],"ease":"oc"})
T(".d",1.6,0.4,{"op":[0,1],"ty":[40,0],"ease":"oc"})
T(".d .cndl",1.8,0.32,{"op":[0,1],"sy":[.2,1],"ease":"ob"},0.11)
T(".d .draw",3.3,0.7,{"draw":True,"ease":"oc"})
T(".d .mk",3.6,0.32,{"op":[0,1],"s":[0,1],"ease":"ob"},0.18)

# 4 THREE STATES
scene("s4",3.8,f'''{logo(150)}<div class="mid">
  <div class="a eyeb2">السوق ما عنده إلا ٣ حالات</div>
  <div class="grid3">
    <div class="st b1"><div class="mc">{mini_state(MUP,TEAL)}</div><div class="stt tt">صاعد</div></div>
    <div class="st b2"><div class="mc">{mini_state(MDN,RED)}</div><div class="stt tr">هابط</div></div>
    <div class="st b3"><div class="mc">{mini_state(RNG,INK)}</div><div class="stt">عرضي</div></div>
  </div>
  <div class="c hooksub">وظيفتك: تعرف وين إحنا الحين</div></div>''')
T(".a",0.15,0.45,{"op":[0,1],"ty":[20,0],"ease":"oc"})
T(".b1",0.6,0.45,{"op":[0,1],"s":[.7,1],"ease":"ob"})
T(".b2",0.85,0.45,{"op":[0,1],"s":[.7,1],"ease":"ob"})
T(".b3",1.1,0.45,{"op":[0,1],"s":[.7,1],"ease":"ob"})
T(".c",1.9,0.5,{"op":[0,1],"ty":[20,0],"ease":"oc"})

# 5 UPTREND
scene("s5",5.8,f'''{logo(120)}<div class="top">
  <div class="numrow"><span class="num">1</span><h2 class="ttl">الاتجاه الصاعد</h2></div>
  <div class="rule bull">قمم أعلى (HH) + قيعان أعلى (HL)</div></div>
  <div class="chartbox mid2">{sc_up()}</div>
  <div class="capt">طالما ما كُسر آخر قاع أعلى → <b class="tt">المشترين مسيطرين</b></div>''')
T(".numrow",0.15,0.45,{"op":[0,1],"tx":[40,0],"ease":"oc"})
T(".rule",0.45,0.45,{"op":[0,1],"ty":[20,0],"ease":"oc"})
T(".chartbox",0.6,0.4,{"op":[0,1],"ty":[30,0],"ease":"oc"})
T(".cndl",0.75,0.32,{"op":[0,1],"sy":[.2,1],"ease":"ob"},0.14)
T(".draw",2.5,0.7,{"draw":True,"ease":"oc"})
T(".mk",2.8,0.34,{"op":[0,1],"s":[0,1],"ease":"ob"},0.18)
T(".capt",3.2,0.5,{"op":[0,1],"ty":[20,0],"ease":"oc"})

# 6 DOWNTREND
scene("s6",5.4,f'''{logo(120)}<div class="top">
  <div class="numrow"><span class="num">2</span><h2 class="ttl">الاتجاه الهابط</h2></div>
  <div class="rule bear">قمم أدنى (LH) + قيعان أدنى (LL)</div></div>
  <div class="chartbox mid2">{sc_dn()}</div>
  <div class="capt">كل قمة وقاع أدنى → <b class="tr">البائعين مسيطرين</b></div>''')
T(".numrow",0.15,0.4,{"op":[0,1],"tx":[40,0],"ease":"oc"})
T(".rule",0.4,0.4,{"op":[0,1],"ty":[20,0],"ease":"oc"})
T(".chartbox",0.55,0.4,{"op":[0,1],"ty":[30,0],"ease":"oc"})
T(".cndl",0.7,0.3,{"op":[0,1],"sy":[.2,1],"ease":"ob"},0.12)
T(".draw",2.3,0.6,{"draw":True,"ease":"oc"})
T(".mk",2.55,0.3,{"op":[0,1],"s":[0,1],"ease":"ob"},0.15)
T(".capt",2.9,0.45,{"op":[0,1],"ty":[20,0],"ease":"oc"})

# 7 SWINGS
scene("s7",4.8,f'''{logo(120)}<div class="top">
  <h2 class="ttl">كيف تحدد القمة والقاع؟</h2>
  <div class="rule neutral">القمة المؤثرة = أعلى من الشمعتين حولها</div></div>
  <div class="chartbox mid2">{sc_swing()}</div>
  <div class="capt">حدد القمم والقيعان الصح → <b>يبين معاك الهيكل</b></div>''')
T(".ttl",0.15,0.45,{"op":[0,1],"tx":[40,0],"ease":"oc"})
T(".rule",0.45,0.45,{"op":[0,1],"ty":[20,0],"ease":"oc"})
T(".chartbox",0.6,0.4,{"op":[0,1],"ty":[30,0],"ease":"oc"})
T(".cndl",0.75,0.3,{"op":[0,1],"sy":[.2,1],"ease":"ob"},0.16)
T(".pop",2.6,0.4,{"op":[0,1],"s":[.2,1],"ease":"ob"},0.2)
T(".capt",3.2,0.45,{"op":[0,1],"ty":[20,0],"ease":"oc"})

# 8 CHoCH
scene("s8",5.8,f'''{logo(120)}<div class="top">
  <div class="numrow"><span class="num">3</span><h2 class="ttl">لحظة الانقلاب</h2></div>
  <div class="rule redr">أول كسر لآخر قاع مؤثر = تغيّر نمط</div></div>
  <div class="chartbox mid2">{sc_ch()}</div>
  <div class="capt">هنا الاتجاه <b class="tr">انقلب</b> — لا تكابر معه</div>''')
T(".numrow",0.15,0.4,{"op":[0,1],"tx":[40,0],"ease":"oc"})
T(".rule",0.4,0.4,{"op":[0,1],"ty":[20,0],"ease":"oc"})
T(".chartbox",0.55,0.4,{"op":[0,1],"ty":[30,0],"ease":"oc"})
T(".cndl",0.7,0.3,{"op":[0,1],"sy":[.2,1],"ease":"ob"},0.11)
T(".draw",2.2,0.6,{"draw":True,"ease":"oc"})
T(".mk",2.45,0.3,{"op":[0,1],"s":[0,1],"ease":"ob"},0.14)
T(".pop2",3.1,0.45,{"op":[0,1],"s":[.3,1],"ease":"ob"})
T(".capt",3.4,0.45,{"op":[0,1],"ty":[20,0],"ease":"oc"})

# 9 BOS vs CHoCH
scene("s9",4.6,f'''{logo(120)}<div class="top"><h2 class="ttl">BOS ولا CHoCH؟</h2></div>
  <div class="cmp">
    <div class="cc c1"><div class="cmc">{mini_bos()}</div><div class="cl tt">BOS</div><div class="cd">كسر يؤكد <b>استمرار</b> الاتجاه</div></div>
    <div class="cc c2"><div class="cmc">{mini_choch()}</div><div class="cl tr">CHoCH</div><div class="cd">كسر يعلن <b>انعكاس</b> الاتجاه</div></div>
  </div>
  <div class="capt short">الفرق بينهم = الفرق بين ربح وخسارة</div>''')
T(".ttl",0.15,0.45,{"op":[0,1],"ty":[20,0],"ease":"oc"})
T(".c1",0.5,0.5,{"op":[0,1],"tx":[50,0],"ease":"oc"})
T(".c2",0.75,0.5,{"op":[0,1],"tx":[-50,0],"ease":"oc"})
T(".c1 .draw",1.5,0.5,{"draw":True,"ease":"oc"})
T(".c2 .draw",1.7,0.5,{"draw":True,"ease":"oc"})
T(".c1 .brkfx2",1.9,0.4,{"op":[0,1],"ty":[16,0],"ease":"oc"})
T(".c2 .brkfx2",2.1,0.4,{"op":[0,1],"ty":[-16,0],"ease":"oc"})
T(".capt",2.7,0.5,{"op":[0,1],"ty":[20,0],"ease":"oc"})

# 10 REAL
scene("s10",9.4,f'''{logo(110)}<div class="top"><div class="realh"><span class="eyeb">على السوق الحقيقي</span><span class="tick">EUR/USD يومي</span></div></div>
  <div class="chartbox big mid2">{sc_real()}</div>
  <div class="flowbox"><span class="fx bear">LL</span><span class="aw">←</span><span class="fx bull">HL</span><span class="aw">←</span><span class="fx lvl">BOS</span><span class="aw">←</span><span class="fx bull">HH</span></div>
  <div class="capt s6cap">انقلب من <b class="tr">هابط ↓</b> إلى <b class="tt">صاعد ↑</b></div>''')
T(".realh",0.15,0.4,{"op":[0,1],"ty":[20,0],"ease":"oc"})
T(".chartbox",0.25,0.4,{"op":[0,1],"ty":[30,0],"ease":"oc"})
T(".cndl:not(.brk)",0.4,0.16,{"op":[0,1],"sy":[.25,1],"ease":"ob"},0.098)  # 33 candles ~3.6s
T(".boxpop",4.0,0.55,{"op":[0,0.18],"ease":"oc"})
T(".zz",4.3,0.9,{"draw":True,"ease":"oc"})
T(".hray",4.4,0.75,{"draw":True,"ease":"oc"})
T(".pop",4.8,0.35,{"op":[0,1],"s":[0,1],"ease":"ob"},0.16)
T(".brk",6.3,0.24,{"op":[0,1],"sy":[.15,1],"ease":"ob"},0.18)
T(".brkfx",6.6,0.4,{"op":[0,1],"ty":[26,0],"ease":"oc"})
T(".hhpop",7.0,0.45,{"op":[0,1],"s":[.2,1],"ease":"ob"})
T(".flowbox",7.3,0.5,{"op":[0,1],"ty":[20,0],"ease":"oc"})
T(".s6cap",7.6,0.5,{"op":[0,1],"ty":[20,0],"ease":"oc"})

# 11 QUOTE
scene("s11",3.2,f'''{logo(150)}<div class="mid">
  <div class="qm">”</div>
  <div class="a titan2">لا تتوقّع السوق…<br><span class="tt">اقرأ هيكله.</span></div>
  <div class="c hooksub">الاتجاه مو رأي — هو تسلسل تشوفه بعينك</div></div>''')
T(".qm",0.1,0.4,{"op":[0,1],"s":[.4,1],"ease":"ob"})
T(".a",0.4,0.6,{"op":[0,1],"s":[.82,1],"ease":"ob"})
T(".c",1.1,0.5,{"op":[0,1],"ty":[20,0],"ease":"oc"})

# 12 CTA
scene("s12",3.6,f'''{logo(150)}<div class="mid">
  <div class="a titan2">خلّ الدرس معاك</div>
  <div class="b cbox">احفظ الريل 📌 وشاركه مع متداول</div>
  <div class="c cbox key">علّق «<b class="tt">ستركجر</b>» ويوصلك ملف الشرح PDF</div>
  <div class="d hand">{GEM}<span>@liquidity.state</span></div></div>''')
T(".a",0.15,0.5,{"op":[0,1],"s":[.8,1],"ease":"ob"})
T(".b",0.55,0.45,{"op":[0,1],"ty":[24,0],"ease":"oc"})
T(".c",0.9,0.45,{"op":[0,1],"ty":[24,0],"ease":"oc"})
T(".d",1.3,0.45,{"op":[0,1],"ty":[20,0],"ease":"oc"})

# ---- compute absolute timeline ----
SCN=[]; TW=[]; t=0.0
for s in scenes:
    st=round(t,3); en=round(t+s["dur"],3); SCN.append([s["id"],st,en])
    for sel,ls,d,sp,stag in s["tw"]:
        TW.append({"sel":f'#{s["id"]} {sel}',"start":round(st+ls,3),"dur":d,"stag":stag,"sp":sp})
    t=en
DUR=round(t,3)
# real scene start for flash/zoom
REAL=[x for x in SCN if x[0]=="s10"][0][1]
BRK=round(REAL+6.3,3)  # breakout moment

STAGE="".join(f'<div class="scene" id="{s["id"]}">{s["html"]}</div>' for s in scenes)

CSS=f'''*{{margin:0;padding:0;box-sizing:border-box}} html,body{{background:#000}}
#stage{{position:relative;width:1080px;height:1920px;overflow:hidden;direction:rtl;font-family:'Tajawal',sans-serif;
  background:radial-gradient(120% 80% at 50% 12%, #F7F3EC 0%, {CREAM} 46%, {CREAM2} 100%)}}
.scene{{position:absolute;inset:0;opacity:0;will-change:opacity,transform}}
/* ---- dark brand poster (scene 1) ---- */
#s1{{background:radial-gradient(135% 95% at 50% 24%, #0C2029 0%, #08131C 46%, #04090F 100%)}}
.poster{{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:0 90px}}
.ptag{{position:absolute;top:74px;right:80px;color:{CYAN};border:1.5px solid rgba(67,212,220,.5);border-radius:3px;padding:9px 26px;font-size:28px;font-weight:800;letter-spacing:.5px}}
.pgem{{width:156px;height:156px;filter:drop-shadow(0 0 36px {CYANG})}}
.pwm{{display:flex;align-items:center;gap:16px;margin-top:14px}}
.pln{{width:64px;height:2px}} .pln.l{{background:linear-gradient(90deg,transparent,{CYAN})}} .pln.r{{background:linear-gradient(90deg,{CYAN},transparent)}}
.pwmt{{font-size:42px;font-weight:600;letter-spacing:11px;background:linear-gradient(180deg,#ffffff,#8fa6b0);-webkit-background-clip:text;background-clip:text;color:transparent}}
.pdivg{{display:flex;align-items:center;gap:14px;width:56%;margin:30px 0}}
.pdivg span{{flex:1;height:2px;background:linear-gradient(90deg,transparent,{CYAN},transparent);box-shadow:0 0 14px {CYANG}}}
.pdivg i{{width:11px;height:11px;background:{CYAN};transform:rotate(45deg);box-shadow:0 0 14px {CYAN};flex:none}}
.ptitle{{font-size:158px;font-weight:900;line-height:.96;letter-spacing:-4px;background:linear-gradient(180deg,#ffffff 0%,#C4D4DB 55%,#7F97A1 100%);-webkit-background-clip:text;background-clip:text;color:transparent;filter:drop-shadow(0 3px 22px rgba(67,212,220,.18))}}
.peyeb{{color:{CYAN};font-size:36px;font-weight:800;letter-spacing:.5px}}
.psub2{{color:#C7D6DC;font-size:37px;font-weight:600;margin-top:14px;line-height:1.4}}
.ppill{{margin-top:36px;color:#EAF2F5;border:1.5px solid rgba(67,212,220,.5);border-radius:3px;padding:15px 40px;font-size:35px;font-weight:800;letter-spacing:.5px}}
.prow{{display:flex;align-items:flex-start;gap:30px;margin-top:64px}}
.pi{{display:flex;flex-direction:column;align-items:center;gap:14px;width:180px}}
.pic{{width:66px;height:66px;filter:drop-shadow(0 0 12px rgba(67,212,220,.4))}} .pic svg{{width:100%;height:100%;display:block}}
.pi span{{color:{CYAN};font-size:34px;font-weight:800}}
.pv{{width:1.5px;height:96px;background:linear-gradient(180deg,transparent,rgba(67,212,220,.45),transparent);margin-top:10px}}
.logo{{position:absolute;left:0;right:0;display:flex;flex-direction:column;align-items:center;gap:10px}}
.logo .g{{width:60px;height:60px;filter:drop-shadow(0 6px 12px rgba(15,46,60,.18))}}
.wm{{display:flex;align-items:center;gap:14px}} .wm .ln{{width:40px;height:2px;background:{TEAL_L};border-radius:2px}}
.wmt{{color:{TEAL_D};font-weight:500;letter-spacing:7px;font-size:28px}}
.mid{{position:absolute;top:0;left:90px;right:90px;bottom:0;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;gap:20px}}
.eyeb{{color:{TEAL};font-weight:800;font-size:34px;letter-spacing:.5px}}
.eyeb2{{color:{TEAL};font-weight:900;font-size:48px;text-align:center}}
.hookbig{{color:{INK};font-weight:900;font-size:120px;line-height:1.02;letter-spacing:-2px}} .tt2{{color:{RED}}}
.hooksub{{color:{GREY};font-weight:600;font-size:44px;margin-top:8px;line-height:1.4}} .hooksub b{{color:{INK};font-weight:900}}
.titan{{color:{INK};font-weight:900;font-size:150px;line-height:.98;letter-spacing:-3px}}
.titan2{{color:{INK};font-weight:900;font-size:100px;letter-spacing:-2px;line-height:1.05}}
.tt{{color:{TEAL_D}!important}} .tr{{color:{RED}!important}}
.pillrow{{display:flex;gap:16px;margin-top:14px}}
.pl{{font-size:34px;font-weight:800;color:{RED};background:transparent;border:1.5px solid rgba(210,75,75,.5);padding:12px 26px;border-radius:2px}}
.chartbox{{width:100%;background:transparent;border:none;box-shadow:none;padding:6px;margin-top:10px}}
.chartbox svg{{width:100%;height:auto;display:block}} .big{{padding:2px}}
.top{{position:absolute;top:250px;left:80px;right:80px;display:flex;flex-direction:column;gap:22px}}
.numrow{{display:flex;align-items:center;gap:22px}}
.num{{width:90px;height:90px;flex:none;display:flex;align-items:center;justify-content:center;font-size:58px;font-weight:900;font-style:italic;color:#fff;background:linear-gradient(135deg,{TEAL},{TEAL_D});border-radius:0;box-shadow:0 6px 16px rgba(46,125,150,.22)}}
.ttl{{font-size:78px;font-weight:900;color:{INK};letter-spacing:-1px}}
.rule{{font-size:46px;font-weight:800;padding:2px 0;color:{GREY}}}
.rule b{{font-weight:900;color:{INK}}}
.rule.bull b{{color:{TEAL_D}}} .rule.bear b{{color:{RED}}} .rule.neutral b{{color:{INK}}} .rule.redr b{{color:{RED}}}
.mid2{{position:absolute;top:520px;left:70px;right:70px}}
.capt{{position:absolute;bottom:250px;left:90px;right:90px;text-align:center;color:{GREY};font-weight:600;font-size:46px;line-height:1.5}}
.capt b{{color:{INK};font-weight:900}} .capt.short{{font-size:42px}}
.realh{{display:flex;align-items:center;justify-content:space-between}}
.tick{{color:{TEAL_D};font-weight:800;font-size:36px;background:transparent;padding:8px 20px;border-radius:2px;border:1.5px solid {TEAL_L}}}
.flowbox{{position:absolute;bottom:370px;left:80px;right:80px;display:flex;align-items:center;justify-content:center;gap:14px}}
.s6cap{{bottom:260px;font-size:44px}}
.fx{{font-weight:900;font-size:46px}}
.fx.bull{{color:{TEAL_D}}} .fx.bear{{color:{INK}}} .fx.lvl{{color:{TEAL_D}}}
.aw{{color:{MUTE};font-size:36px;font-weight:900}}
.grid3{{display:flex;gap:24px;width:100%;margin-top:20px}}
.st{{flex:1;background:transparent;border:none;box-shadow:none;padding:6px}}
.st .mc svg{{width:100%;height:auto}} .stt{{font-size:42px;font-weight:900;color:{INK};margin-top:6px}}
.cmp{{display:flex;gap:30px;position:absolute;top:440px;left:60px;right:60px}}
.cc{{flex:1;background:transparent;border:none;box-shadow:none;padding:10px;text-align:center}}
.cmc svg{{width:100%;height:auto}} .cl{{font-size:56px;font-weight:900;margin-top:10px}} .cd{{font-size:34px;color:{GREY};font-weight:600;margin-top:6px}} .cd b{{color:{INK};font-weight:900}}
.cbox{{width:100%;font-size:48px;font-weight:800;padding:32px;border-radius:3px;line-height:1.4;color:{INK};background:transparent;border:1.5px solid {CARDBD}}}
.cbox.key{{background:rgba(46,125,150,.10);border:2px solid {TEAL}}}
.hand{{display:flex;align-items:center;gap:16px;margin-top:6px}} .hand svg{{width:60px;height:60px}} .hand span{{font-size:44px;font-weight:800;color:{TEAL_D};direction:ltr}}
.qm{{font-size:150px;color:{TEAL_L};line-height:.5;font-weight:900;opacity:.6;margin-bottom:10px}}
.cndl,.mk,.pop,.pop2,.hhpop,.bospill,.brkfx,.brkfx2{{transform-box:fill-box}}
.cndl{{transform-origin:center bottom}} .mk,.pop,.pop2{{transform-origin:center center}}
'''

JS=f'''
const FPS=30,DUR={DUR},BRK={BRK};
const SCN={json.dumps(SCN)};
const TW={json.dumps(TW)};
function clamp(v,a,b){{return v<a?a:v>b?b:v}}
function E(u,t){{u=clamp(u,0,1);
 if(t=='oc')return 1-Math.pow(1-u,3);
 if(t=='ob'){{const c=1.70158,d=c+1;return 1+d*Math.pow(u-1,3)+c*Math.pow(u-1,2);}}
 return u;}}
function L(a,b,u){{return a+(b-a)*u}}
function apply(el,sp,u){{let tr='';
 if('s'in sp)tr+=`scale(${{L(sp.s[0],sp.s[1],u)}}) `;
 if('sy'in sp)tr+=`scaleY(${{L(sp.sy[0],sp.sy[1],u)}}) `;
 if('tx'in sp)tr+=`translateX(${{L(sp.tx[0],sp.tx[1],u)}}px) `;
 if('ty'in sp)tr+=`translateY(${{L(sp.ty[0],sp.ty[1],u)}}px) `;
 if(tr)el.style.transform=tr;
 if('op'in sp)el.style.opacity=L(sp.op[0],sp.op[1],u);
 if('draw'in sp){{if(el.__len===undefined){{el.__len=(typeof el.getTotalLength==='function')?el.getTotalLength():0;}}
   if(el.__len>0){{el.style.strokeDasharray=el.__len;el.style.strokeDashoffset=el.__len*(1-u);}}else{{el.style.opacity=u;}}}}
}}
function bind(){{for(const w of TW){{w.els=[...document.querySelectorAll(w.sel)];}}}}
function setFrame(t){{
 for(const [id,st,en] of SCN){{
   const el=document.getElementById(id);const FIN=0.45,FOUT=0.4;let op=0;
   if(t>=st-FIN&&t<=en){{if(t<st)op=E((t-(st-FIN))/FIN,'oc');else if(t>en-FOUT)op=1-E((t-(en-FOUT))/FOUT,'oc');else op=1;}}
   el.style.opacity=op;
   const p=clamp((t-st)/(en-st),0,1);el.style.transform=`scale(${{1.008+0.02*p}})`;
 }}
 for(const w of TW){{if(!w.els)continue;w.els.forEach((el,i)=>{{const s=w.start+i*w.stag;apply(el,w.sp,E((t-s)/w.dur,w.sp.ease||'lin'));}});}}
 const fl=document.querySelector('#s10 .flash');
 if(fl){{let ft=t-BRK;let o=0;if(ft>0&&ft<0.45){{o=ft<0.12?(ft/0.12)*0.5:0.5*(1-(ft-0.12)/0.33);}}fl.style.opacity=Math.max(0,o);}}
 const cs=document.querySelector('#s10 .chartsvg');
 if(cs){{let zt=t-BRK;let z=0;if(zt>0&&zt<1.1){{z=Math.sin((zt/1.1)*Math.PI)*0.06;}}cs.style.transformOrigin='72% 60%';cs.style.transform=`scale(${{1+z}})`;}}
}}
window.__setFrame=setFrame;window.__DUR=DUR;
bind();setFrame(0);
'''

HTML=f'''<!DOCTYPE html><html lang="ar" dir="rtl"><head><meta charset="UTF-8"><style>{FONT_CSS}\n{CSS}</style></head>
<body><div id="stage">{STAGE}</div><script>{JS}</script></body></html>'''
open(os.path.join(HERE,"reel.html"),"w",encoding="utf-8").write(HTML)
print(f"wrote reel.html {len(HTML)} bytes | DUR={DUR}s | scenes={len(scenes)} | frames={int(DUR*30)}")
print("scene starts:", [(s[0],s[1]) for s in SCN])
