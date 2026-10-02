# -*- coding: utf-8 -*-
# الحزمة G — «واقعية جادة» (أمر فهد 2026-08-03: «يشبه الكرتون — غيّره»)
# هندسة صوت حقيقية بدل نغمات sine: ترانزينتات نويز، سب منزلق النغمة بتشبع، ريفيرب شرودر، وتر Karplus-Strong
import os
import numpy as np
import wave

SR = 48000
HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.normpath(os.path.join(HERE, "..", "..", "..", "..", "assets", "sfx_packs", "g_real"))
os.makedirs(D, exist_ok=True)
rng = np.random.default_rng(7)

def save(name, sig, gain=0.9):
    sig = sig / (np.max(np.abs(sig)) + 1e-9) * gain
    pcm = (sig * 32767).astype(np.int16)
    with wave.open(os.path.join(D, name + ".wav"), "w") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    print(name, round(len(sig)/SR, 2), "s")

def t_axis(dur): return np.arange(int(SR*dur)) / SR

def env_exp(n, tau): return np.exp(-np.arange(n)/(SR*tau))

def lowpass(sig, fc):
    """one-pole LP متتالي (طبقتين) — دافئ وطبيعي"""
    a = np.exp(-2*np.pi*fc/SR); out = np.copy(sig)
    for _ in range(2):
        y = np.zeros_like(out); acc = 0.0
        for i in range(len(out)):
            acc = (1-a)*out[i] + a*acc; y[i] = acc
        out = y
    return out

def highpass(sig, fc): return sig - lowpass(sig, fc)

def band_sweep(noise, f0, f1, bw=0.5):
    """بان باس متحرك عبر إطارات FFT — كنسة هوائية حقيقية"""
    n = len(noise); frame = 2048; hop = frame//2
    win = np.hanning(frame); out = np.zeros(n+frame)
    freqs = np.fft.rfftfreq(frame, 1/SR)
    steps = max(1, (n-frame)//hop)
    for k in range(steps+1):
        i = k*hop
        if i+frame > n: break
        prog = i/max(n-frame, 1)
        fc = f0*(f1/f0)**prog
        seg = noise[i:i+frame]*win
        S = np.fft.rfft(seg)
        mask = np.exp(-0.5*((np.log2(freqs+1e-6)-np.log2(fc))/bw)**2)
        out[i:i+frame] += np.fft.irfft(S*mask, frame)*win
    return out[:n]

def schroeder(sig, wet=0.25, decay=0.75, tail=0.5):
    out = np.concatenate([sig, np.zeros(int(SR*tail))])
    rev = np.zeros_like(out)
    for d_ms, fb in ((29.7, decay), (37.1, decay-0.03), (41.1, decay-0.06), (43.7, decay-0.09)):
        d = int(SR*d_ms/1000); buf = np.zeros_like(out)
        for i in range(d, len(out)):
            buf[i] = out[i-d] + fb*buf[i-d]
        rev += buf
    rev /= 4
    for d_ms in (5.0, 1.7):
        d = int(SR*d_ms/1000); g = 0.7; y = np.zeros_like(rev)
        for i in range(len(rev)):
            y[i] = -g*rev[i] + (rev[i-d] if i >= d else 0) + (g*y[i-d] if i >= d else 0)
        rev = y
    return out + wet*rev

def sat(sig, drive=1.6): return np.tanh(sig*drive)

# ===== إمباكت: سب منزلق النغمة 85→36Hz + لكمة نويز + ريفيرب قصير =====
dur = 1.1; t = t_axis(dur); n = len(t)
f = 85*(36/85)**np.clip(t/0.5, 0, 1)
phase = 2*np.pi*np.cumsum(f)/SR
sub = np.sin(phase) * env_exp(n, 0.30)
punch = lowpass(rng.standard_normal(int(SR*0.05)), 220) * env_exp(int(SR*0.05), 0.012) * 2.2
body = lowpass(rng.standard_normal(int(SR*0.16)), 700) * env_exp(int(SR*0.16), 0.05) * 0.8
sig = sub.copy(); sig[:len(punch)] += punch; sig[:len(body)] += body*0.6
save("impact", schroeder(sat(sig, 1.9), wet=0.18, tail=0.35))

# ===== ووش: كنسة نويز بفلتر متحرك 260→2000→600 =====
dur = 0.85; n = int(SR*dur)
no = rng.standard_normal(n)
w1 = band_sweep(no, 260, 2000, bw=0.55)
w2 = band_sweep(no, 2000, 600, bw=0.6)
mixw = np.linspace(0, 1, n)**1.4
sig = w1*(1-mixw) + w2*mixw
envl = np.minimum(np.arange(n)/(0.18*SR), 1) * np.exp(-np.maximum(np.arange(n)/SR-0.38, 0)/0.16)
save("whoosh", sat(sig*envl, 1.2), gain=0.62)

# ===== بوب (رسم وسم): طقّة نويز + طرقة خشب مخمدة =====
n1 = int(SR*0.008)
click = highpass(rng.standard_normal(n1), 900) * env_exp(n1, 0.0016)
n2 = int(SR*0.07)
knock = np.sin(2*np.pi*165*t_axis(0.07)) * env_exp(n2, 0.014)
knock = lowpass(sat(knock + 0.3*lowpass(rng.standard_normal(n2), 400), 1.5), 900)
sig = np.zeros(n2); sig[:n1] += click*1.4; sig += knock*0.9
save("pop", sig, gain=0.7)

# ===== تيك: طقّة نويز مجهرية (مو نغمة) =====
n1 = int(SR*0.005)
sig = band_sweep(rng.standard_normal(int(SR*0.03)), 2600, 2600, bw=0.35)
sig[:n1] += highpass(rng.standard_normal(n1), 1500) * env_exp(n1, 0.001) * 0.8
sig *= env_exp(len(sig), 0.006)
save("tick", sig, gain=0.5)

# ===== رايزر: نويز بكنسة صاعدة + سب يكبر — توتر بلا صفير =====
dur = 1.6; n = int(SR*dur); t = t_axis(dur)
noise_r = band_sweep(rng.standard_normal(n), 180, 1500, bw=0.7) * (t/dur)**2
subr = np.sin(2*np.pi*(52 + 14*t/dur)*t) * (t/dur)**2.4 * 0.8
sig = noise_r + subr
fade = np.ones(n); fo = int(0.14*SR); fade[-fo:] = np.linspace(1, 0, fo)
save("riser", sat(sig*fade, 1.3), gain=0.7)

# ===== سكسس: وتر Karplus-Strong دافئ (عضوي مو إلكتروني) =====
def pluck(freq, dur, damp=0.996):
    n = int(SR*dur); d = int(SR/freq)
    buf = lowpass(rng.standard_normal(d), 3000)
    out = np.zeros(n)
    for i in range(n):
        out[i] = buf[i % d]
        buf[i % d] = damp * 0.5 * (buf[i % d] + buf[(i+1) % d])
    return out
p1 = pluck(196, 1.1); p2 = 0.45*pluck(294, 0.9)
sig = p1; sig[:len(p2)] += p2
sig = lowpass(sig, 2200) * env_exp(len(sig), 0.4)
save("success", schroeder(sig, wet=0.15, tail=0.3), gain=0.62)

print("pack G ->", sorted(os.listdir(D)))
