"""
Compact (~31 bar) XAUUSD 15m series for the 3D version — same CORRECTED SMC
structure as data.py, but fewer/bigger candles so the perspective 3D frame reads
cleanly. Strong high = drop BODY-CLOSES below prior low (BOS); weak high = drop
stays above the low.
"""
import json, random
random.seed(74026)
N=31
L0=4060.0; H_L=4085.0; BOSLOW=4051.0; L1=4064.0; H_R=4087.0
WEAKLOW=4071.0; RUN=4091.5; TARGET=4050.0

pts=[(0,4058.0),(3,L0+0.5),(5,4070.0),
     (8,H_L-2.0),                 # LEFT high
     (9,4079.0),
     (11,BOSLOW+2.0),             # displacement: body-close below L0 (BOS)
     (12,4055.0),
     (14,L1+0.5),(16,4074.0),
     (19,H_R-2.0),                # RIGHT high (near-equal)
     (22,WEAKLOW+1.0),            # shallow drop, stays above L1
     (24,WEAKLOW+3.0),
     (26,H_R-2.0),               # re-approach (frame-0 end)
     (28,RUN-1.5),               # stop-run spike
     (29,4072.0),
     (30,TARGET)]                # collapse

def interp(i):
    for k in range(len(pts)-1):
        i0,c0=pts[k]; i1,c1=pts[k+1]
        if i0<=i<=i1:
            t=(i-i0)/(i1-i0) if i1>i0 else 0; t=t*t*(3-2*t)
            return c0+(c1-c0)*t
    return pts[-1][1]

candles=[]; prev=pts[0][1]
for i in range(N):
    base=interp(i)
    close=base+(random.random()-0.5)*2.6
    open_=prev+(random.random()-0.5)*1.3
    hi=max(open_,close)+random.random()*2.3+0.8
    lo=min(open_,close)-(random.random()*2.3+0.8)
    if i==8:  hi=H_L+0.5; open_=H_L-6; close=H_L-2.5      # LEFT high
    if i==10: open_=4072; close=4062; lo=4061
    if i==11: open_=4062; close=BOSLOW+2; lo=BOSLOW       # BOS: body closes below L0
    if i==12: open_=BOSLOW+2; close=4054; lo=4052
    if i==19: hi=H_R+0.5; open_=H_R-6; close=H_R-2.5      # RIGHT high
    if i==22: lo=WEAKLOW; close=WEAKLOW+3                 # shallow, stays above L1
    if i==28: hi=RUN; open_=H_R-1; close=RUN-3            # stop-run spike
    if i==30: lo=TARGET-0.5; close=TARGET+0.5
    o,h,l,c=round(open_,2),round(hi,2),round(lo,2),round(close,2)
    h=max(h,o,c); l=min(l,o,c)
    candles.append({"i":i,"o":o,"h":round(h,2),"l":round(l,2),"c":c,"up":c>=o})
    prev=c

meta={"symbol":"XAUUSD","tf":"15m","anchor_spot":4066.38,"n":N,
 "reveal_frame0":26,"reveal_full":N,
 "levels":{"LOW_L":L0,"H_L":H_L,"SWEEP":BOSLOW,"LOW_R":L1,"H_R":H_R,
           "WEAKLOW":WEAKLOW,"RUN":RUN,"TARGET":TARGET},
 "idx":{"H_L":8,"SWEEP":12,"LOW_L":3,"LOW_R":14,"H_R":19,"WEAKLOW":22,"RUN":28,"TARGET":30},
 "price_top":4094.0,"price_bot":4046.0}

if __name__=="__main__":
    json.dump({"meta":meta,"candles":candles},open(__file__.replace("data3d.py","candles3d.json"),"w"),indent=1)
    print(f"wrote {N} candles  range {min(c['l'] for c in candles)}..{max(c['h'] for c in candles)}")
    print("BOS:",candles[11]['c']<L0 and candles[12]['c']<L0," weak-noBreak:",candles[22]['l']>L1)
