"""
XAUUSD 15m candle series for the "which high takes your stop" reel.

Real anchor: gold spot ~$4,066/oz on 2026-07-26 (public sources; live intraday
feeds were unavailable in this locked environment, so the *series* is a
deterministic teaching construction anchored to that real level and labelled
لغرض تعليمي in the reel, per the pipeline's education-purpose rule).

Structure encoded (left -> right):
  Low_L  : reference low for the LEFT high
  H_L    : LEFT high (slightly lower)  -> its drop SWEEPS below Low_L  => STRONG
  Low_R  : higher reference low for the RIGHT high
  H_R    : RIGHT high (HIGHER, the one the eye calls 'strong') -> its drop
           does NOT reach Low_R => WEAK => the high that takes your stop
  Then resolution: H_R is run (stop-hunt spike) and price collapses to target.
"""
import json, math, os, random

random.seed(74026)  # deterministic; no Date/random-at-runtime dependence

# --- key swing skeleton (price, index) ---
# 61 bars, 15m each.
N = 61
# anchor levels near real spot 4066
LOW_L   = 4048.0
H_L     = 4082.0     # left high  (strong)
SWEEP   = 4043.0     # wick low below LOW_L on the drop from H_L
LOW_R   = 4064.0     # higher low (reference for right high)
H_R     = 4088.0     # right high (higher, weak)
WEAKLOW = 4070.5     # shallow drop from H_R, stays ABOVE LOW_R (not swept)
RUN     = 4091.5     # stop-run spike above H_R
TARGET  = 4052.0     # collapse target after the run

# control points (index -> target close)
pts = [
    (0, 4055.0), (4, LOW_L+0.5), (6, LOW_L+1.5), (9, 4066.0),
    (14, H_L-1.0),                      # rally to left high
    (15, H_L-3.0),
    (19, SWEEP+2.0),                    # drop sweeps low (wick lower)
    (22, 4060.0),
    (27, LOW_R+1.0), (30, LOW_R+2.0),   # higher low
    (38, H_R-1.5),                      # rally to right high (higher)
    (43, WEAKLOW+1.0),                  # shallow drop, not swept
    (47, WEAKLOW+2.5),
    (52, H_R-2.0),                      # re-approach right high (frame-0 endpoint)
    (55, RUN-1.0),                      # stop-run spike
    (57, 4074.0),                       # collapse begins
    (60, TARGET),                       # target
]

def interp_close(i):
    for k in range(len(pts)-1):
        i0,c0 = pts[k]; i1,c1 = pts[k+1]
        if i0 <= i <= i1:
            t = (i-i0)/(i1-i0) if i1>i0 else 0
            t = t*t*(3-2*t)  # smoothstep
            return c0 + (c1-c0)*t
    return pts[-1][1]

candles = []
prev_close = pts[0][1]
for i in range(N):
    base = interp_close(i)
    # organic wobble
    wob = (random.random()-0.5)*3.2
    close = base + wob
    open_ = prev_close + (random.random()-0.5)*1.4
    # body + wicks with 15m-like ranges
    hi = max(open_, close) + random.random()*3.0 + 0.8
    lo = min(open_, close) - (random.random()*3.0 + 0.8)
    # force the exact structural extremes on the key bars
    if i == 14: hi = H_L + 0.6; close = H_L-2.0; open_= H_L-5
    if i == 18: lo = SWEEP+1.2                       # approaching sweep
    if i == 19: lo = SWEEP; close = SWEEP+6; open_=SWEEP+7   # sweep wick + reject
    if i == 38: hi = H_R + 0.5; close = H_R-2.5; open_=H_R-6 # right high (higher)
    if i == 43: lo = WEAKLOW; close = WEAKLOW+3               # shallow, not swept
    if i == 55: hi = RUN; close = RUN-3; open_=H_R            # stop-run spike above H_R
    if i == 60: lo = TARGET-0.5; close = TARGET+0.5
    o,h,l,c = round(open_,2),round(hi,2),round(lo,2),round(close,2)
    h = max(h,o,c); l = min(l,o,c)
    candles.append({"i":i,"o":o,"h":round(h,2),"l":round(l,2),"c":c,
                    "up": c>=o})
    prev_close = c

meta = {
    "symbol":"XAUUSD","tf":"15m","anchor_spot":4066.38,"n":N,
    "reveal_frame0": 53,          # bars shown in HOOK/LOOP (price approaching H_R)
    "reveal_full": N,             # full resolution shown in PROOF
    "levels":{
        "LOW_L":LOW_L,"H_L":H_L,"SWEEP":SWEEP,"LOW_R":LOW_R,"H_R":H_R,
        "WEAKLOW":WEAKLOW,"RUN":RUN,"TARGET":TARGET},
    "idx":{"H_L":14,"SWEEP":19,"LOW_L":5,"LOW_R":29,"H_R":38,"WEAKLOW":43,
           "RUN":55,"TARGET":60},
    "price_top":4095.5,"price_bot":4039.5,
}

if __name__ == "__main__":
    out = {"meta":meta,"candles":candles}
    os.makedirs(os.path.dirname(os.path.abspath(__file__)), exist_ok=True)
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"candles.json"),"w") as f:
        json.dump(out,f,indent=1)
    hh=max(c["h"] for c in candles); ll=min(c["l"] for c in candles)
    print(f"wrote {N} candles  range {ll} .. {hh}")
    print("H_L", candles[14]["h"], "SWEEP low", candles[19]["l"], "(LOW_L", LOW_L, ")",
          "=> swept:", candles[19]["l"] < LOW_L)
    print("H_R", candles[38]["h"], "WEAK low", candles[43]["l"], "(LOW_R", LOW_R, ")",
          "=> swept:", candles[43]["l"] < LOW_R)
