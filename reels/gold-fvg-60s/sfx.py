# effects-only sound bed, synthesised (no music, no voice): candle ticks, punch thumps, tool rise, TP chime
import json, numpy as np, wave
J = json.load(open('timeline.json')); T, S = J['T'], J['S']; SR = 48000; FPS = 60
n = int(T['total'] / FPS * SR) + SR; out = np.zeros(n)
t = lambda d: np.arange(int(d * SR)) / SR
def add(sig, f, g=1.0):
    i = int(f / FPS * SR); j = min(n, i + len(sig)); out[i:j] += g * sig[:j - i]
def tick():
    x = t(0.035); return np.sin(2*np.pi*2400*x) * np.exp(-x*160)
def thump():
    x = t(0.5); f = 90*np.exp(-x*6)+38; ph = 2*np.pi*np.cumsum(f)/SR
    return np.sin(ph)*np.exp(-x*7) + 0.15*np.random.default_rng(1).normal(size=len(x))*np.exp(-x*40)
def rise(d=0.7):
    x = t(d); f = 220 + 500*(x/d)**2; ph = 2*np.pi*np.cumsum(f)/SR
    return 0.5*np.sin(ph)*np.sin(np.pi*x/d)**2
def chime():
    x = t(1.6); return sum(a*np.sin(2*np.pi*fr*x) for fr, a in [(880,1),(1320,.5),(1760,.25)]) * np.exp(-x*3)
def air(d=0.45):
    r = np.random.default_rng(2).normal(size=int(d*SR)); k = np.ones(60)/60; r = np.convolve(r, k, 'same')
    x = t(d)[:len(r)]; return r*np.sin(np.pi*x/d)**2*6
for s, d in S: add(tick(), s + d, 0.10)
for k in ('sweep', 'bos', 'tp'): add(thump(), T[k], 0.9)
add(rise(), T['pos'] + 22, 0.35); add(chime(), T['tp'], 0.25)
add(thump(), T['result'] + 12, 1.0); add(air(), T['fvg'], 0.25); add(air(), T['liq'], 0.2)
add(air(0.6), T['outro'] - 10, 0.2)
out = out / max(1e-9, np.abs(out).max()) * 0.6
w = wave.open('sfx.wav', 'wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
w.writeframes((out[:int(T['total']/FPS*SR)] * 32767).astype(np.int16).tobytes()); w.close(); print('sfx ok')
