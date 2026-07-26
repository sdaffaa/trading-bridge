"""
Synthesize the SFX / sound-design bed from the shot script's SFX cues.
No spoken VO here (no TTS provider in this env) — instead the bed carries
sub-drops, ticks, risers, an impact and an air bed, with the VO windows left
open (ducked) so the Kuwaiti voiceover from vo_manifest.json drops straight in.
Master normalised toward -14 LUFS (BS.1770 K-weighting).
Output: audio.wav  (stereo, 48 kHz, 22.0 s)
"""
import numpy as np, wave, struct, os
from scipy import signal

SR=48000; DUR=22.0; N=int(SR*DUR)
rng=np.random.default_rng(74026)
buf=np.zeros(N, dtype=np.float64)

def idx(t): return int(t*SR)
def db(x): return 10**(x/20.0)
def add(sig, t0, gain):
    s=idx(t0); e=min(N, s+len(sig))
    buf[s:e]+=sig[:e-s]*gain

def env_exp(n, tau):
    t=np.arange(n)/SR
    return np.exp(-t/tau)

def sub_drop(level_db, f0=40.0, dur=0.75, pitch_drop=8.0):
    n=int(dur*SR); t=np.arange(n)/SR
    f=f0 - pitch_drop*(t/dur)               # slight downward glide
    ph=2*np.pi*np.cumsum(f)/SR
    s=np.sin(ph)*env_exp(n,dur*0.35)
    # add a soft click transient
    s[:200]+=np.hanning(400)[:200]*0.6
    return s*db(level_db)

def tick(level_db, f=1500.0, dur=0.035):
    n=int(dur*SR); t=np.arange(n)/SR
    s=np.sin(2*np.pi*f*t)*np.exp(-t/0.006)
    s+=rng.standard_normal(n)*np.exp(-t/0.003)*0.4
    return s*db(level_db)

def riser(dur, level_db, f0=200, f1=1600):
    n=int(dur*SR); t=np.arange(n)/SR
    noise=rng.standard_normal(n)
    # rising bandpass sweep
    out=np.zeros(n)
    # cheap: amplitude ramp + rising tonal sweep
    f=f0*(f1/f0)**(t/dur)
    ph=2*np.pi*np.cumsum(f)/SR
    tone=np.sin(ph)*0.5
    ramp=(t/dur)**1.8
    out=(tone+0.5*noise*ramp)*ramp
    return out*db(level_db)

def impact(level_db, f=60.0, dur=0.4):
    n=int(dur*SR); t=np.arange(n)/SR
    s=np.sin(2*np.pi*f*t)*env_exp(n,0.12)
    s[:120]+=np.hanning(240)[:120]*0.7
    return s*db(level_db)

def rev_reverb_swell(dur, level_db):
    n=int(dur*SR); t=np.arange(n)/SR
    noise=rng.standard_normal(n)
    b,a=signal.butter(4, 3000/(SR/2), 'low')
    noise=signal.lfilter(b,a,noise)
    ramp=(t/dur)**2                        # swell up into the hit
    return noise*ramp*db(level_db)

# ---- air bed (continuous, pink-ish, very low) ----
def pink(n):
    white=rng.standard_normal(n)
    b,a=signal.butter(2, 900/(SR/2),'low')
    p=signal.lfilter(b,a,white)
    return p/ (np.max(np.abs(p))+1e-9)
air=pink(N)
# gentle level automation: a touch louder in the quiet proof section
autom=np.interp(np.arange(N)/SR,
                [0,6,11,14.3,17.5,22],
                [db(-32),db(-32),db(-31),db(-30),db(-28),db(-30)])
buf+=air*autom

# ---- cue placements (from each beat's SFX line) ----
add(sub_drop(-6), 0.0, 1.0)                       # B1 hook impact
for tt in (0.35,0.95,1.55):                       # B1 printing ticks
    add(tick(-18), tt, 1.0)
add(impact(-3, f=60), 3.75, 1.0)                  # B2 "هدف"
add(riser(0.8,-14), 4.0, 1.0)                     # B3 riser starts
add(riser(0.5,-12)*0.0+1e-9*np.ones(int(0.5*SR)), 5.5, 0.0)  # placeholder
# B4 riser resolve (short downward-settling swell)
add(sub_drop(-16,f0=90,dur=0.5,pitch_drop=40), 5.5, 1.0)
add(tick(-20), 6.65, 1.0)                         # B5+6 badge tick
add(riser(1.2,-13), 8.6, 1.0)                     # B7a riser into base
add(tick(-18), 11.2, 1.0)                         # B7b badge 1
add(tick(-18), 11.5, 1.0)                         # B7b badge 2
add(rev_reverb_swell(0.6,-10), 13.0, 1.0)         # pre-verdict reverse swell
add(sub_drop(-4), 13.6, 1.0)                      # B8 verdict hit (peak)
add(tick(-18), 18.7, 1.0)                         # B10 SL settle tick
add(sub_drop(-8), 19.2, 1.0)                      # B11 loop echo

# ---- VO ducking windows: gentle dip so a future VO sits on top cleanly ----
# (bed already low; apply mild -3 dB dips across spoken spans for headroom)
duck=np.ones(N)
vo_spans=[(0.0,2.4),(2.6,4.0),(6.0,8.5),(8.6,11.0),(11.0,13.5),(14.3,17.3),(17.5,19.1),(19.2,21.9)]
for a,b in vo_spans:
    s,e=idx(a),idx(b); w=np.ones(e-s)*db(-3)
    ramp=int(0.08*SR)
    w[:ramp]=np.linspace(1,db(-3),ramp); w[-ramp:]=np.linspace(db(-3),1,ramp)
    duck[s:e]*=w
buf*=duck

# ---- BS.1770 K-weighting integrated loudness ----
def k_weight(x):
    # stage 1: high-shelf
    b1=np.array([1.53512485958697,-2.69169618940638,1.19839281085285])
    a1=np.array([1.0,-1.69065929318241,0.73248077421585])
    # stage 2: high-pass
    b2=np.array([1.0,-2.0,1.0])
    a2=np.array([1.0,-1.99004745483398,0.99007225036621])
    y=signal.lfilter(b1,a1,x); y=signal.lfilter(b2,a2,y)
    return y
def lufs(x):
    y=k_weight(x); ms=np.mean(y**2)
    return -0.691+10*np.log10(ms+1e-12)

# The bed is sparse (transient sub-drops dominate true-peak but not integrated
# loudness). Global peak-normalising would crush it, so we soft-clip transients
# with tanh and target the BED at -16 LUFS. The -14 LUFS *master* is reached when
# the Fahed VO layers on top (vo_manifest loudnorm I=-14).
BED_TARGET=-16.0
THR=db(-3.0)                       # tanh knee ~ -3 dBFS
for _ in range(4):
    cur=lufs(buf)
    buf*=db(BED_TARGET-cur)
    buf=THR*np.tanh(buf/THR)       # gentle transient limiting, preserves low level
peak=np.max(np.abs(buf))
if peak>db(-1.0):
    buf*=db(-1.0)/peak
print(f"bed LUFS {lufs(buf):.1f}  peak {20*np.log10(np.max(np.abs(buf))+1e-9):.1f} dBFS "
      f"(master -14 LUFS reached with VO layered)")

# ---- write stereo wav 48k ----
st=np.stack([buf,buf],axis=1)
st=np.clip(st,-1,1)
pcm=(st*32767).astype('<i2')
out=os.path.join(os.path.dirname(os.path.abspath(__file__)),"audio.wav")
with wave.open(out,'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes(pcm.tobytes())
print("wrote",out, f"{len(buf)/SR:.2f}s")
