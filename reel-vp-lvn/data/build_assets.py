#!/usr/bin/env python3
"""Build educational XAUUSD 15m candles + data-derived volume profile + timed SFX bed.
Educational template (لغرض تعليمي) — user overlays a real TradingView replay for publishing.
No ffmpeg needed: SFX written directly as WAV via the stdlib wave module.
"""
import json, math, wave, struct
import numpy as np

rng = np.random.default_rng(7)

# ---------- 1) Candle narrative (15m XAUUSD, ~90 bars) ----------
# Levels the story is engineered around:
NPOC   = 3320.0   # prior-session naked POC (untouched magnet = target)
LVN_LO, LVN_HI = 3321.0, 3332.0   # الفراغ (thin, fast traversal)
WALL_LO, WALL_HI = 3345.0, 3350.0 # HVN wall / VAH area (sell location)
ENTRY  = 3347.0
SL     = 3353.0
TP     = 3320.0

bars = []
price = 3356.0
def push(o,h,l,c,v):
    bars.append([round(o,2),round(h,2),round(l,2),round(c,2),float(v)])

# Phase A: downtrend into value (0-13)
for i in range(14):
    o=price; c=o-rng.uniform(0.3,1.1); h=max(o,c)+rng.uniform(0.2,0.6); l=min(o,c)-rng.uniform(0.2,0.6)
    push(o,h,l,c, rng.uniform(80,140)); price=c
# Phase B: acceptance / balance building HVN + POC ~3340 (14-59), high volume
price=3345.0
for i in range(46):
    drift=(3340.5-price)*0.18
    o=price; c=o+drift+rng.uniform(-1.6,1.6)
    c=min(max(c,3335.0),3349.5)
    h=max(o,c)+rng.uniform(0.3,1.0); l=min(o,c)-rng.uniform(0.3,1.0)
    # heavier volume near the wall (3345-3349) and near POC (3340)
    v=rng.uniform(150,230)
    if 3345<=(h+l)/2<=3350: v+=rng.uniform(80,160)
    push(o,h,l,c,v); price=c
# Phase C: rotate up toward the wall / entry (60-69)
for i in range(10):
    o=price; c=o+rng.uniform(0.4,1.3); c=min(c,3347.5)
    h=max(o,c)+rng.uniform(0.2,0.7); l=min(o,c)-rng.uniform(0.2,0.6)
    push(o,h,l,c, rng.uniform(120,190)); price=c
# Phase D: entry bar — rejection wick at the wall (70)
o=price; h=3348.6; c=3345.2; l=3344.6
push(o,h,l,c, 260); price=c
# Phase E: fast slide through the LVN to tap the nPOC (71-80) — big red bars, LOW volume in the gap
slide_targets=[3341,3335,3330,3326,3322,3320,3321,3322]
for t in slide_targets:
    o=price; c=float(t); h=max(o,c)+rng.uniform(0.2,0.5); l=min(o,c)-rng.uniform(0.3,0.9)
    if c<=NPOC+0.6: l=min(l,3319.4)   # tap the magnet
    v=rng.uniform(70,120)             # thin — traversal
    push(o,h,l,c,v); price=c
# Phase F: target reached, small base (81-89)
for i in range(9):
    o=price; c=o+rng.uniform(-0.8,0.9); c=min(max(c,3320.5),3325.0)
    h=max(o,c)+rng.uniform(0.2,0.6); l=min(o,c)-rng.uniform(0.2,0.6)
    push(o,h,l,c, rng.uniform(90,150)); price=c

candles=[{"o":b[0],"h":b[1],"l":b[2],"c":b[3],"v":b[4]} for b in bars]

# ---------- 2) Volume profile from the series ($1 rows) ----------
lo=min(b[2] for b in bars); hi=max(b[1] for b in bars)
row=1.0
edges=np.arange(math.floor(lo), math.ceil(hi)+row, row)
centers=(edges[:-1]+edges[1:])/2
vol=np.zeros(len(centers))
for o,h,l,c,v in bars:
    lohi=np.where((centers>=l)&(centers<=h))[0]
    if len(lohi)==0:
        idx=int(np.clip(np.searchsorted(centers,(h+l)/2)-1,0,len(centers)-1)); vol[idx]+=v; continue
    vol[lohi]+=v/len(lohi)
poc_i=int(np.argmax(vol)); POC=float(centers[poc_i])
# value area 70%
total=vol.sum(); target=0.70*total
lo_i=hi_i=poc_i; acc=vol[poc_i]
while acc<target and (lo_i>0 or hi_i<len(vol)-1):
    left=vol[lo_i-1] if lo_i>0 else -1
    right=vol[hi_i+1] if hi_i<len(vol)-1 else -1
    if right>=left: hi_i+=1; acc+=vol[hi_i]
    else: lo_i-=1; acc+=vol[lo_i]
VAL=float(centers[lo_i]); VAH=float(centers[hi_i])
profile=[{"price":float(centers[i]),"vol":float(vol[i])} for i in range(len(centers))]

levels={"POC":round(POC,1),"VAH":round(VAH,1),"VAL":round(VAL,1),
        "nPOC":NPOC,"lvnLo":LVN_LO,"lvnHi":LVN_HI,"wallLo":WALL_LO,"wallHi":WALL_HI,
        "entry":ENTRY,"sl":SL,"tp":TP,"priceLo":round(lo,1),"priceHi":round(hi,1),
        "maxVol":float(vol.max())}

json.dump({"candles":candles,"profile":profile,"levels":levels},
          open("data/chart.json","w"), ensure_ascii=False, indent=0)
print("bars",len(candles),"POC",levels["POC"],"VAH",levels["VAH"],"VAL",levels["VAL"],
      "range",levels["priceLo"],"-",levels["priceHi"],"maxVol",round(levels["maxVol"]))

# ---------- 3) SFX bed (22.0s mono 48k WAV) ----------
SR=48000; DUR=22.0; N=int(SR*DUR); t=np.arange(N)/SR
mix=np.zeros(N)
def add(sig, at, gain):
    s=int(at*SR); e=min(N,s+len(sig)); mix[s:e]+=sig[:e-s]*gain
def sub(freq,dur,f_end=None):
    n=int(dur*SR); tt=np.arange(n)/SR
    f=freq if f_end is None else np.linspace(freq,f_end,n)
    ph=2*np.pi*np.cumsum(f)/SR
    env=np.exp(-tt*3.0)
    return np.sin(ph)*env
def tick(dur=0.03,freq=2200):
    n=int(dur*SR); tt=np.arange(n)/SR
    return np.sin(2*np.pi*freq*tt)*np.exp(-tt*90)
def riser(dur):
    n=int(dur*SR); tt=np.arange(n)/SR
    noise=rng.standard_normal(n)
    # rising lowpass-ish: multiply by rising envelope + rising tone
    tone=np.sin(2*np.pi*np.linspace(120,600,n)*tt)
    env=(tt/dur)**2
    return (noise*0.3+tone*0.7)*env
def impact(freq=60,dur=0.5):
    n=int(dur*SR); tt=np.arange(n)/SR
    return np.sin(2*np.pi*freq*tt)*np.exp(-tt*6.0)

# ambient bed (very low)
bed=(rng.standard_normal(N)*0.006)
# smooth the bed a touch
kernel=np.ones(64)/64; bed=np.convolve(bed,kernel,mode='same')
mix+=bed

add(sub(40,0.6), 0.0, 0.5)            # frame-0 sub-drop
for k in range(6):                    # subtle ticks first 8s (state changes)
    add(tick(), 0.5+1.2*k, 0.10)
add(riser(3.2), 10.0, 0.16)           # into the TURN
add(impact(60,0.5), 13.0, 0.5)        # on «منزلق»
add(sub(40,0.7), 13.2, 0.55)          # verdict sub-drop
add(tick(0.05,1600), 17.0, 0.22); add(impact(55,0.5),17.0,0.35)  # nPOC tap
add(sub(40,0.8,30), 19.8, 0.4)        # loop echo

# normalize peak to -3 dBFS
peak=np.max(np.abs(mix)) or 1.0
mix=mix/peak*(10**(-3/20))
pcm=(mix*32767).astype(np.int16)
with wave.open("public/audio/sfx.wav","w") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes(pcm.tobytes())
print("sfx.wav written", round(DUR,1),"s")
