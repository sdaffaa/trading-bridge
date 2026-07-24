import json, pathlib

rows = json.loads(pathlib.Path("data/gc_daily.json").read_text())
rows = list(reversed(rows))  # chronological (oldest -> newest)
n = len(rows)

def feats(c):
    o,h,l,cl = c["open"],c["high"],c["low"],c["close"]
    rng = h-l or 1e-9
    body = abs(cl-o)
    up = h-max(o,cl)      # upper wick
    dn = min(o,cl)-l      # lower wick
    return rng,body,up,dn

LOOK=8      # bars forward to judge outcome
SWING=3     # bars each side to qualify a swing extreme

def is_swing_high(i):
    h=rows[i]["high"]
    for j in range(max(0,i-SWING),min(n,i+SWING+1)):
        if j!=i and rows[j]["high"]>h: return False
    return True
def is_swing_low(i):
    l=rows[i]["low"]
    for j in range(max(0,i-SWING),min(n,i+SWING+1)):
        if j!=i and rows[j]["low"]<l: return False
    return True

bear=[]  # bearish pin (upper wick) at high that FAILED (price continued up)
bull=[]  # bullish pin (lower wick) at low that FAILED (price continued down)

for i in range(SWING, n-LOOK):
    c=rows[i]; rng,body,up,dn=feats(c)
    if rng< c["close"]*0.008: continue          # ignore tiny-range days
    # bearish pin: long upper wick, small body, small lower wick
    if up>=1.8*body and up>=0.5*rng and dn<=0.3*rng and is_swing_high(i):
        H=c["high"]
        fwd=rows[i+1:i+1+LOOK]
        dip=min(x["low"] for x in fwd[:2])<c["close"]   # seller briefly in profit
        broke=max(x["high"] for x in fwd)>H              # swept above the pin high
        cont =fwd[-1]["close"]>c["close"]                # net continuation up
        if broke and cont:
            gain=max(x["high"] for x in fwd)-H
            bear.append((i,c["date"],round(up/body,1),round(gain,1),dip))
    # bullish pin: long lower wick, small body, small upper wick
    if dn>=2*body and dn>=0.55*rng and up<=0.25*rng and is_swing_low(i):
        L=c["low"]
        fwd=rows[i+1:i+1+LOOK]
        broke=min(x["low"] for x in fwd)<L
        cont =fwd[-1]["close"]<c["close"]
        if broke and cont:
            drop=L-min(x["low"] for x in fwd)
            bull.append((i,c["date"],round(dn/body,1),round(drop,1)))

bear.sort(key=lambda x:-x[3])
print("FAILED BEARISH PINS (false top -> price continued UP):")
for i,d,r,g,dip in bear: print(f"  idx {i}  {d}  wick/body={r}x  ran +{g} after  dip_first={dip}")
print("\nFAILED BULLISH PINS (false bottom -> price continued DOWN):")
for i,d,r,g in bull: print(f"  idx {i}  {d}  wick/body={r}x  fell -{g} after")

def window(i,pre=4,post=6):
    s=max(0,i-pre); e=min(n,i+post+1)
    print(f"\n--- window around idx {i} ({rows[i]['date']}), pin at position {i-s} ---")
    for k in range(s,e):
        c=rows[k]; mark=" <== PIN" if k==i else ""
        print(f'  {{o:{c["open"]},h:{c["high"]},l:{c["low"]},c:{c["close"]}}}, // {c["date"]}{mark}')

# show detail for the strongest of each (max wick ratio)
if bear:
    b=bear[0]; window(b[0]); print("BEAR PICK:",b)
if bull:
    b=max(bull,key=lambda x:x[2]); window(b[0]); print("BULL PICK:",b)
