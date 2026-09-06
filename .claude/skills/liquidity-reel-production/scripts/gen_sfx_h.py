# -*- coding: utf-8 -*-
"""الحزمة H — «Institutional» : نظام صوت سينمائي فاخر لعلامة مالية.
كل شيء مُصنَّع بالـDSP (numpy) — لا عيّنات جاهزة ولا موسيقى مكتبات.
المصادر الصوتية المسموحة فقط: سنثات أنالوج عميقة، سب باس، غرانيولار، درونات،
إمباكتات نظيفة، رايزرات ناعمة، أجواء معكوسة، أصوات واجهة رقمية، نبضات دنيا،
إيقاع مفلتر، وقوام ميكانيكي.  الصمت عنصر أصيل في النظام.
"""
import os
import numpy as np
import wave

SR = 48000
HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.normpath(os.path.join(HERE, "..", "..", "..", "..", "assets", "sfx_packs", "h_institutional"))
M = os.path.normpath(os.path.join(HERE, "..", "..", "..", "..", "assets", "music"))
os.makedirs(D, exist_ok=True)
os.makedirs(M, exist_ok=True)
rng = np.random.default_rng(2026)

# ───────────────────────── أدوات أساسية ─────────────────────────
def t_ax(d): return np.arange(int(SR * d)) / SR
def env_exp(n, tau): return np.exp(-np.arange(n) / (SR * tau))

def fade(sig, ms_in=4, ms_out=12):
    n_i, n_o = int(SR * ms_in / 1000), int(SR * ms_out / 1000)
    s = sig.copy()
    if n_i and len(s) > n_i: s[:n_i] *= np.linspace(0, 1, n_i)
    if n_o and len(s) > n_o: s[-n_o:] *= np.linspace(1, 0, n_o)
    return s

def fft_lp(sig, fc, order=4):
    n = len(sig); S = np.fft.rfft(sig); f = np.fft.rfftfreq(n, 1 / SR)
    return np.fft.irfft(S / np.sqrt(1 + (f / fc) ** (2 * order)), n)

def fft_hp(sig, fc, order=4):
    n = len(sig); S = np.fft.rfft(sig); f = np.fft.rfftfreq(n, 1 / SR)
    H = (f / max(fc, 1e-6)) ** order / np.sqrt(1 + (f / max(fc, 1e-6)) ** (2 * order))
    H[0] = 0
    return np.fft.irfft(S * H, n)

def fft_bp(sig, fc, bw_oct=0.6):
    n = len(sig); S = np.fft.rfft(sig); f = np.fft.rfftfreq(n, 1 / SR)
    H = np.exp(-0.5 * ((np.log2(f + 1e-6) - np.log2(fc)) / bw_oct) ** 2)
    return np.fft.irfft(S * H, n)

def morph_lp(sig, fc_curve, res=0.0):
    """فلتر متحرك عبر إطارات FFT — حركة فلتر أنالوج بلا حلقات بايثون بطيئة."""
    n = len(sig); frame = 2048; hop = frame // 2
    win = np.hanning(frame); out = np.zeros(n + frame)
    f = np.fft.rfftfreq(frame, 1 / SR)
    for i in range(0, max(n - frame, 1), hop):
        fc = float(fc_curve[min(i, len(fc_curve) - 1)])
        H = 1 / np.sqrt(1 + (f / fc) ** 8)
        if res > 0:                                  # رنين حول التردد المقطعي
            H = H + res * np.exp(-0.5 * ((np.log2(f + 1e-6) - np.log2(fc)) / 0.12) ** 2)
        out[i:i + frame] += np.fft.irfft(np.fft.rfft(sig[i:i + frame] * win) * H, frame) * win
    return out[:n]

def make_ir(dur=2.4, damp=3800, pre_ms=18, shape=3.2):
    n = int(SR * dur)
    ir = rng.standard_normal(n) * np.exp(-shape * np.arange(n) / n)
    ir = fft_lp(ir, damp)
    ir[:int(SR * pre_ms / 1000)] = 0
    return ir / (np.max(np.abs(ir)) + 1e-9)

IR_ROOM = make_ir(1.1, 5200, 8, 5.0)      # غرفة تقنية ضيقة
IR_HALL = make_ir(3.4, 2600, 26, 2.6)     # فضاء مؤسسي واسع ومكتوم

def conv(sig, ir, wet=0.25, tail=True):
    n = len(sig) + len(ir) - 1
    N = 1 << int(np.ceil(np.log2(n)))
    y = np.fft.irfft(np.fft.rfft(sig, N) * np.fft.rfft(ir, N), N)[:n]
    y /= (np.max(np.abs(y)) + 1e-9)
    dry = np.concatenate([sig, np.zeros(len(ir) - 1)]) if tail else sig
    y = y[:len(dry)] * np.max(np.abs(sig))
    return dry * (1 - wet) + y * wet

def sat(sig, drive=1.5): return np.tanh(sig * drive)

def limit(sig, ceil=0.92):
    return np.tanh(sig / max(np.max(np.abs(sig)), 1e-9) * 1.05) * ceil

def analog_saw(f0, dur, cents=0.0, harm=26, drift=0.0009, seed_ph=None):
    """ساو أنالوج جمعي مع انجراف نغمي طفيف — دفء بلا حدّة رقمية."""
    t = t_ax(dur); n = len(t)
    f = f0 * 2 ** (cents / 1200)
    f = f * (1 + drift * np.sin(2 * np.pi * rng.uniform(0.03, 0.09) * t + rng.uniform(0, 6)))
    ph = 2 * np.pi * np.cumsum(f) / SR + (seed_ph if seed_ph is not None else rng.uniform(0, 6))
    out = np.zeros(n)
    for k in range(1, harm + 1):
        if f0 * k > 15000: break
        out += np.sin(k * ph) / k
    return out / np.max(np.abs(out) + 1e-9)

def sub(f0, dur, glide_to=None, glide_t=0.4, tau=0.5):
    t = t_ax(dur); n = len(t)
    if glide_to:
        f = f0 * (glide_to / f0) ** np.clip(t / glide_t, 0, 1)
    else:
        f = np.full(n, float(f0))
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env_exp(n, tau)

def granular(src, dur, grain_ms=110, density=16, spread=0.12, jitter=1.0):
    out = np.zeros(int(SR * dur))
    g = int(SR * grain_ms / 1000)
    for _ in range(int(dur * density)):
        pos = int(rng.integers(0, max(1, len(src) - g - 1)))
        rate = float(1 + rng.normal(0, spread))
        idx = np.clip((pos + np.arange(g) * rate).astype(int), 0, len(src) - 1)
        st = int(rng.integers(0, max(1, len(out) - g - 1)))
        out[st:st + g] += src[idx] * np.hanning(g) * float(rng.uniform(0.25, 1.0)) * jitter
    return out / (np.max(np.abs(out)) + 1e-9)

def save(name, sig, gain=0.86, folder=None, fade_out=40):
    sig = fade(np.asarray(sig, dtype=float), 3, fade_out)
    sig = sig / (np.max(np.abs(sig)) + 1e-9) * gain
    pcm = (sig * 32767).astype(np.int16)
    path = os.path.join(folder or D, name + ".wav")
    with wave.open(path, "w") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    print(f"  {name:22s} {len(sig)/SR:6.2f}s")
    return sig

print("── الحزمة H: العناصر ──")

# ═════════ 1. إمباكتات نظيفة ═════════
# impact_deep — الحدث الرئيسي: سب منزلق + ترانزينت مفلتر + ذيل قاعة مكتوم
n = int(SR * 1.5)
s = sub(68, 1.5, glide_to=29, glide_t=0.42, tau=0.42)
tr = fft_hp(rng.standard_normal(int(SR * 0.004)), 1800) * env_exp(int(SR * 0.004), 0.0012) * 1.6
body = fft_lp(rng.standard_normal(int(SR * 0.11)), 520) * env_exp(int(SR * 0.11), 0.035) * 0.55
x = s.copy(); x[:len(tr)] += tr; x[:len(body)] += body
IMPACT_DEEP = save("impact_deep", conv(sat(x, 1.7), IR_HALL, 0.14))

# impact_clean — قطع تقني جاف بلا ذيل (للانتقالات الحادة)
n = int(SR * 0.3)
x = sub(92, 0.3, glide_to=46, glide_t=0.12, tau=0.075)
k = fft_bp(rng.standard_normal(int(SR * 0.006)), 2400, 0.9) * env_exp(int(SR * 0.006), 0.0016) * 1.2
x[:len(k)] += k
save("impact_clean", sat(x, 1.3), gain=0.8)

# impact_soft — تأكيد خفيف تحت النص (لا يقاطع القراءة)
x = sub(58, 0.55, glide_to=38, glide_t=0.2, tau=0.18)
save("impact_soft", conv(fft_lp(x, 260), IR_ROOM, 0.1), gain=0.62)

# ═════════ 2. سب باس ونبضات دنيا ═════════
x = sub(41, 0.75, tau=0.24)
save("pulse_sub", sat(fft_lp(x, 160), 1.2), gain=0.7)

x = sub(33, 2.6, tau=1.5)
save("sub_drop", sat(x, 1.15), gain=0.78)

# نبضة واجهة دنيا — علامة إيقاعية بلا طبل
x = sub(52, 0.22, tau=0.05) * 0.9
cl = fft_bp(rng.standard_normal(int(SR * 0.003)), 3200, 0.7) * env_exp(int(SR * 0.003), 0.001) * 0.35
x[:len(cl)] += cl
save("pulse_min", x, gain=0.6)

# ═════════ 3. درونات عميقة ═════════
def drone(f0, dur, second=1.5, cents=(0, 7, -6), fc_a=180, fc_b=520, tension=False):
    t = t_ax(dur); n = len(t)
    lay = np.zeros(n)
    for c in cents:
        lay += analog_saw(f0, dur, cents=c)
        lay += 0.55 * analog_saw(f0 * second, dur, cents=c + rng.uniform(-4, 4))
    if tension:                                  # ثانية صغرى → نبض تداخلي متوتر
        lay += 0.42 * analog_saw(f0 * 1.0595, dur, cents=3)
    lay /= np.max(np.abs(lay))
    fc = fc_a + (fc_b - fc_a) * (0.5 - 0.5 * np.cos(2 * np.pi * t / dur))
    lay = morph_lp(lay, fc, res=0.25)
    lay += 0.85 * np.sin(2 * np.pi * f0 / 2 * t) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.08 * t))
    return lay / np.max(np.abs(lay))

DR_CALM = drone(55, 8.0)
save("drone_low", fade(DR_CALM, 400, 700), gain=0.55)
DR_TENSE = drone(49, 8.0, tension=True, fc_a=140, fc_b=430)
save("drone_tension", fade(DR_TENSE, 400, 700), gain=0.55)

# ═════════ 4. قوام غرانيولار وأجواء معكوسة ═════════
AIR_SRC = fft_bp(rng.standard_normal(int(SR * 3)), 2600, 1.1)
GRAN_AIR = granular(AIR_SRC, 6.0, grain_ms=140, density=13, spread=0.2)
save("granular_air", fade(fft_hp(GRAN_AIR, 900) * 0.8, 500, 900), gain=0.45)

GRAN_METAL = granular(fft_bp(analog_saw(220, 2.0), 1400, 0.8), 4.0, grain_ms=70, density=22, spread=0.3)
save("granular_metal", fade(GRAN_METAL, 300, 600), gain=0.5)

# جو معكوس — يُبنى قبل القطع (يسبق الإمباكت دائماً)
rev_src = conv(sub(64, 1.2, glide_to=40, glide_t=0.5, tau=0.5) + 0.35 * GRAN_AIR[:int(SR * 1.2)], IR_HALL, 0.55)
save("reverse_atmos", fade(rev_src[::-1], 600, 30), gain=0.62)

rev2 = conv(analog_saw(110, 1.6) * env_exp(int(SR * 1.6), 0.5), IR_HALL, 0.6)
save("reverse_swell", fade(fft_lp(rev2, 2400)[::-1], 700, 25), gain=0.58)

# ═════════ 5. أصوات واجهة رقمية ═════════
def ui(fc, ms, bw=0.55, tau=None, noise=True):
    n = int(SR * ms / 1000)
    src = rng.standard_normal(n) if noise else np.sin(2 * np.pi * fc * t_ax(ms / 1000))
    x = fft_bp(src, fc, bw) * env_exp(n, tau or ms / 4000)
    return x

save("ui_click", ui(3400, 7, 0.5, 0.0018), gain=0.42)
save("ui_tick", ui(5200, 4, 0.4, 0.0009), gain=0.33)
x = np.zeros(int(SR * 0.24))
a = ui(1700, 40, 0.35, 0.008, noise=False); b = ui(2550, 55, 0.35, 0.011, noise=False)
x[:len(a)] += a * 0.9
x[int(SR * 0.07):int(SR * 0.07) + len(b)] += b * 0.75
x += np.pad(sub(46, 0.18, tau=0.05) * 0.5, (0, len(x) - int(SR * 0.18)))
save("ui_confirm", x, gain=0.5)
a1 = ui(620, 110, 0.3, 0.02, noise=False)
a2 = 0.5 * ui(430, 110, 0.3, 0.03, noise=False)
save("ui_alert", a1 + a2, gain=0.45)
save("ui_scan", fade(morph_lp(rng.standard_normal(int(SR * 0.6)) * 0.4,
                              np.linspace(700, 6000, int(SR * 0.6)), res=0.5), 20, 60), gain=0.36)

# ═════════ 6. رايزرات ناعمة ═════════
dur = 3.2; n = int(SR * dur); t = t_ax(dur)
noise_r = morph_lp(rng.standard_normal(n), np.exp(np.linspace(np.log(240), np.log(2600), n)), res=0.4)
noise_r *= (t / dur) ** 2.2
sub_r = np.sin(2 * np.pi * (38 + 16 * t / dur) * t) * (t / dur) ** 2.6 * 0.9
x = noise_r * 0.55 + sub_r
x[-int(SR * 0.25):] *= np.linspace(1, 0.35, int(SR * 0.25))   # يخلي مكاناً للإمباكت
save("riser_soft", sat(x, 1.15), gain=0.62)

dur = 1.8; n = int(SR * dur); t = t_ax(dur)
x = fft_bp(rng.standard_normal(n), 900, 1.4) * (t / dur) ** 3 + np.sin(2 * np.pi * 44 * t) * (t / dur) ** 3 * 0.7
save("riser_short", sat(x, 1.1), gain=0.55)

# ═════════ 7. إيقاع مفلتر وقوام ميكانيكي ═════════
x = fft_bp(rng.standard_normal(int(SR * 0.09)), 190, 0.75) * env_exp(int(SR * 0.09), 0.018)
save("perc_low", sat(x, 1.3), gain=0.55)
x = fft_bp(rng.standard_normal(int(SR * 0.05)), 1250, 0.5) * env_exp(int(SR * 0.05), 0.008)
save("perc_filtered", x, gain=0.42)

# قوام ميكانيكي: نبضات مبوَّبة على رنينات لا-توافقية (غرفة خوادم)
dur = 4.0; n = int(SR * dur)
base = np.zeros(n)
for f in (137, 219, 361, 487):
    base += fft_bp(rng.standard_normal(n), f, 0.18) / 4
gate = (np.sin(2 * np.pi * 7.3 * t_ax(dur)) > 0.55).astype(float)
gate = fft_lp(gate, 60)
save("mech_texture", fade(base * gate * 1.4, 300, 500), gain=0.4)

x = granular(fft_bp(rng.standard_normal(int(SR * 1.5)), 800, 0.4), 2.5, grain_ms=28, density=40, spread=0.35)
save("mech_click_bed", fade(x, 200, 400), gain=0.35)

# ═════════ 8. ستينج الهوية ═════════
dur = 3.6; n = int(SR * dur)
pre = np.zeros(n)
rv = fade(rev_src[::-1], 500, 20)[:int(SR * 0.9)]
pre[:len(rv)] += rv * 0.55                                   # جو معكوس يبني للحظة
hit = np.zeros(n)
hi = IMPACT_DEEP[:min(len(IMPACT_DEEP), n - int(SR * 0.9))]
hit[int(SR * 0.9):int(SR * 0.9) + len(hi)] += hi
tone = np.zeros(n)
tt = t_ax(dur - 0.9)
bell = (np.sin(2 * np.pi * 110 * tt) + 0.4 * np.sin(2 * np.pi * 165 * tt) + 0.18 * np.sin(2 * np.pi * 330 * tt))
bell *= env_exp(len(tt), 0.85) * 0.5
tone[int(SR * 0.9):int(SR * 0.9) + len(bell)] += bell
sting = conv(pre + hit + tone, IR_HALL, 0.3)[:n]
save("logo_sting", sting, gain=0.8)

# ═════════ 9. أسِرَّة موسيقية (40 ثانية، قابلة للتكرار والخفض) ═════════
def bed(name, dur=40.0, tense=False):
    n = int(SR * dur); t = t_ax(dur)
    out = np.zeros(n)
    # طبقة الدرون الأساسية
    d = drone(49 if tense else 55, dur, tension=tense,
              fc_a=130 if tense else 170, fc_b=380 if tense else 480)
    out += d * 0.85
    # هواء غرانيولار خافت
    air = granular(AIR_SRC, dur, grain_ms=170, density=8, spread=0.22)
    out += fft_hp(air, 1200) * 0.16
    # نبض دنيا منتظم — إحساس الدقة المؤسسية
    step = 1.0 if tense else 2.0
    p = sub(52 if tense else 44, 0.5, tau=0.14)
    for k in np.arange(2.0, dur - 1.0, step):
        i = int(SR * k)
        seg = p[:min(len(p), n - i)]
        out[i:i + len(seg)] += seg * (0.5 if tense else 0.34)
    # نقرات واجهة متفرقة (توقيع تقني)
    tick = ui(5200, 4, 0.4, 0.0009)
    for k in np.arange(4.0, dur - 2.0, 3.7 if tense else 5.3):
        i = int(SR * (k + rng.uniform(-0.15, 0.15)))
        seg = tick[:min(len(tick), n - i)]
        out[i:i + len(seg)] += seg * 0.22
    if tense:
        out += np.pad(fft_lp(GRAN_METAL, 900)[:min(len(GRAN_METAL), n)], (0, max(0, n - len(GRAN_METAL)))) * 0.10
    # فراغات مقصودة: الصمت جزء من التصميم
    for gap in ((dur * 0.45, 0.45), (dur * 0.78, 0.35)):
        i0 = int(SR * gap[0]); i1 = i0 + int(SR * gap[1])
        ramp = np.ones(n)
        ramp[i0:i1] = np.linspace(1, 0.12, i1 - i0)
        ramp[i1:i1 + int(SR * 0.5)] = np.linspace(0.12, 1, min(int(SR * 0.5), n - i1))
        out *= ramp
    out = limit(sat(out, 1.05), 0.75)
    return save(name, fade(out, 900, 1400), gain=0.72, folder=M)

print("── الأسِرَّة الموسيقية ──")
bed("bed_institutional", 40.0, tense=False)
bed("bed_institutional_tense", 40.0, tense=True)

# ═════════ 10. مونتاج عرض (يسمعه العميل مرة واحدة) ═════════
print("── مونتاج العرض ──")
DUR = 46.0
n = int(SR * DUR)
mix = np.zeros(n)

def place(sig, at, g=1.0):
    i = int(SR * at)
    seg = np.asarray(sig)[:max(0, min(len(sig), n - i))]
    if len(seg): mix[i:i + len(seg)] += seg * g

def wav(name):
    with wave.open(os.path.join(D, name + ".wav")) as w:
        return np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(float) / 32767

# صمت مقصود 0.0–0.8 ثم جو معكوس يبني إلى الإمباكت الأول
place(wav("reverse_atmos"), 0.8, 0.85)
place(wav("impact_deep"), 2.3, 1.0)
place(np.tile(wav("drone_low"), 3)[:int(SR * 20)], 2.35, 0.42)      # الدرون يدخل تحت الإمباكت
place(wav("ui_scan"), 4.2, 0.55)
for k, at in enumerate((5.4, 5.9, 6.4, 6.9)): place(wav("ui_tick"), at, 0.5 - k * 0.05)
place(wav("ui_click"), 7.6, 0.7)
place(wav("pulse_min"), 8.4, 0.75)
place(wav("pulse_sub"), 9.4, 0.7)
place(wav("perc_low"), 10.4, 0.6)
place(wav("perc_filtered"), 11.0, 0.5)
place(wav("mech_texture"), 11.6, 0.5)
place(wav("granular_air"), 13.0, 0.5)
place(wav("ui_confirm"), 16.2, 0.6)
# فراغ مقصود 17.2–18.0 (لا شيء إطلاقاً)
place(wav("drone_tension"), 18.0, 0.5)
place(wav("granular_metal"), 19.4, 0.4)
place(wav("riser_soft"), 20.8, 0.75)
place(wav("impact_clean"), 24.0, 0.95)
place(wav("mech_click_bed"), 24.2, 0.45)
place(wav("ui_alert"), 26.4, 0.5)
place(wav("riser_short"), 27.4, 0.6)
place(wav("impact_deep"), 29.2, 0.9)
place(wav("sub_drop"), 29.25, 0.5)
place(wav("impact_soft"), 31.6, 0.7)
place(wav("reverse_swell"), 32.4, 0.6)
# مقطع البيد المؤسسي كاملاً تحت النهاية
bed_wav = wav("bed_institutional") if os.path.exists(os.path.join(D, "bed_institutional.wav")) else None
with wave.open(os.path.join(M, "bed_institutional.wav")) as w:
    bd = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(float) / 32767
place(bd[:int(SR * 10)], 34.0, 0.55)
# صمت 41.6–42.2 ثم ستينج الهوية
place(wav("logo_sting"), 42.2, 1.0)
mix = limit(mix, 0.9)
save("_demo_montage", fade(mix, 200, 1200), gain=0.9)

print("\nالحزمة H ->", len(sorted(os.listdir(D))), "ملفاً في", D)
