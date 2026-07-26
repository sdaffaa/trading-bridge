"""
XAUUSD 15m candle series — CORRECTED SMC model for "which high takes your stop".

Real anchor: gold spot ~$4,066/oz on 2026-07-26 (public sources; live intraday
feeds unavailable in this env, so the series is a deterministic teaching
construction anchored to that level, labelled لغرض تعليمي in the reel).

CORRECT rule (per SMC methodology — body-close discipline):
  STRONG high (protected): the drop from the high BODY-CLOSES below the prior
    swing low  ->  Break of Structure (BOS) down. A wick alone does NOT count.
  WEAK high (liquidity): the drop from the high does NOT break the prior low
    (shallow internal pullback)  ->  unmitigated liquidity, expected to be taken
    ->  this is the high that takes your stop.

Structure (left -> right):
  L0   = prior low under the LEFT high
  H_L  = LEFT high   -> its drop BODY-CLOSES below L0 (BOS)      => STRONG
  L1   = higher low under the RIGHT high
  H_R  = RIGHT high (near-equal, the eye's 'obvious' high) -> its drop stays
         ABOVE L1 (no break)                                     => WEAK
  Then: price spikes ABOVE H_R (stop-run / buy-side liquidity) and collapses to
  target -> proof the weak high was the trap.
"""
import json, random

random.seed(74026)
N = 61
L0      = 4060.0    # prior low under the left high
H_L     = 4085.0    # LEFT high (strong)
BOSLOW  = 4051.0    # displacement low after H_L (body closes below L0)
L1      = 4064.0    # higher low under the right high
H_R     = 4087.0    # RIGHT high (near-equal / a hair higher) = weak
WEAKLOW = 4071.0    # shallow drop from H_R, stays ABOVE L1 (no break)
RUN     = 4091.5    # stop-run spike above H_R
TARGET  = 4050.0    # collapse target

pts = [
    (0,4057.0),(4,L0+0.5),(6,L0+0.8),(9,4072.0),
    (14,H_L-2.0),                         # rally to LEFT high
    (16,4074.0),
    (19,BOSLOW+1.5),                      # displacement DOWN, body-close < L0 (BOS)
    (21,4056.0),
    (24,L1+0.5),(30,4075.0),
    (38,H_R-2.0),                         # rally to RIGHT high (near-equal)
    (43,WEAKLOW+1.0),                     # shallow drop, stays above L1
    (47,WEAKLOW+3.0),
    (52,H_R-2.0),                         # re-approach right high (frame-0 endpoint)
    (55,RUN-1.5),                         # stop-run spike above H_R
    (57,4072.0),
    (60,TARGET),                          # collapse to target
]

def interp(i):
    for k in range(len(pts)-1):
        i0,c0=pts[k]; i1,c1=pts[k+1]
        if i0<=i<=i1:
            t=(i-i0)/(i1-i0) if i1>i0 else 0
            t=t*t*(3-2*t)
            return c0+(c1-c0)*t
    return pts[-1][1]

candles=[]; prev=pts[0][1]
for i in range(N):
    base=interp(i)
    close=base+(random.random()-0.5)*3.0
    open_=prev+(random.random()-0.5)*1.4
    hi=max(open_,close)+random.random()*2.6+0.8
    lo=min(open_,close)-(random.random()*2.6+0.8)
    # structural bars
    if i==14: hi=H_L+0.5; open_=H_L-6; close=H_L-2.5      # LEFT high
    if i==18: open_=4072; close=4062; lo=4061             # start of drop
    if i==19: open_=4062; close=BOSLOW+2; lo=BOSLOW       # displacement: BODY closes below L0 (BOS)
    if i==20: open_=BOSLOW+2; close=4054; lo=4052         # follow-through below L0
    if i==38: hi=H_R+0.5; open_=H_R-6; close=H_R-2.5      # RIGHT high (near-equal, hair higher)
    if i==43: lo=WEAKLOW; close=WEAKLOW+3                 # shallow drop, stays above L1
    if i==55: hi=RUN; open_=H_R-1; close=RUN-3            # stop-run spike above H_R
    if i==60: lo=TARGET-0.5; close=TARGET+0.5
    o,h,l,c=round(open_,2),round(hi,2),round(lo,2),round(close,2)
    h=max(h,o,c); l=min(l,o,c)
    candles.append({"i":i,"o":o,"h":round(h,2),"l":round(l,2),"c":c,"up":c>=o})
    prev=c

meta={
 "symbol":"XAUUSD","tf":"15m","anchor_spot":4066.38,"n":N,
 "reveal_frame0":53,"reveal_full":N,
 "levels":{"LOW_L":L0,"H_L":H_L,"SWEEP":BOSLOW,"LOW_R":L1,"H_R":H_R,
           "WEAKLOW":WEAKLOW,"RUN":RUN,"TARGET":TARGET},
 "idx":{"H_L":14,"SWEEP":20,"LOW_L":5,"LOW_R":24,"H_R":38,"WEAKLOW":43,
        "RUN":55,"TARGET":60},
 "price_top":4095.0,"price_bot":4045.5,
}

if __name__=="__main__":
    json.dump({"meta":meta,"candles":candles},open(__file__.replace("data.py","candles.json"),"w"),indent=1)
    hh=max(c["h"] for c in candles); ll=min(c["l"] for c in candles)
    print(f"wrote {N} candles  range {ll} .. {hh}")
    print(f"LEFT high {candles[14]['h']}  drop close bar19={candles[19]['c']} bar20={candles[20]['c']} "
          f"(L0={L0}) => BOS(body<low): {candles[19]['c']<L0 and candles[20]['c']<L0}")
    print(f"RIGHT high {candles[38]['h']}  drop low bar43={candles[43]['l']} (L1={L1}) "
          f"=> broke low: {candles[43]['l']<L1}  (weak = must be False)")
