# -*- coding: utf-8 -*-
"""حزمة «القلم» — لريل الرسم الصامت (بريف فهد 2026-08-08).

البريف يطلب ثلاثة أصوات لا ستّة: **قلم** قصير عند كل عنصر يُرسم، و**تك**
خفيف على كل شمعة تُطبع في آخر ثلاث ثوانٍ، و**ضربة** واحدة منخفضة (~40Hz)
عند بلوغ الهدف. وما عداها صمتٌ حقيقي لا يُملأ.

ولماذا حزمة جديدة: `pop` و`whoosh` في الحزم السابقة أصواتُ **ظهور**
(ترانزينت ثم ذيل) — تصلح لوسمٍ ينبثق، ولا تصلح لخطٍّ يُسحب بيد. صوت
القلم عريضُ الطيف قصيرُ الذيل بحبيبات احتكاك، ومدّته تتبع مدّة السحب لا
مدّةً ثابتة، فيُولَّد بثلاث مدد ويُختار الأقرب لكل عنصر.

    python3 gen_sfx_pen.py
"""
import os
import wave

import numpy as np

SR = 48000
HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.normpath(os.path.join(HERE, "..", "..", "..", "..",
                                  "assets", "sfx_packs", "p_pen"))
os.makedirs(D, exist_ok=True)
rng = np.random.default_rng(37)


def save(name, sig, gain=0.9):
    sig = np.asarray(sig, dtype=float)
    sig = sig / (np.max(np.abs(sig)) + 1e-9) * gain
    with wave.open(os.path.join(D, name + ".wav"), "w") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((sig * 32767).astype(np.int16).tobytes())
    print(f'{name:<10} {len(sig)/SR:.2f}s')


def lowpass(sig, fc, poles=2):
    a = np.exp(-2 * np.pi * fc / SR); out = np.copy(sig)
    for _ in range(poles):
        y = np.zeros_like(out); acc = 0.0
        for i in range(len(out)):
            acc = (1 - a) * out[i] + a * acc
            y[i] = acc
        out = y
    return out


def highpass(sig, fc):
    return sig - lowpass(sig, fc, 1)


def pen(dur):
    """سحبة قلم: احتكاكٌ متصل + حبيبات دقيقة + بداية ونهاية ناعمتان.

    الاحتكاك نويز مقصوص بين ١٫٨ و٦ كيلوهرتز — أعلى منه يصير «شش»، وأدنى
    منه يصير حفيفاً. والحبيبات نبضات عشوائية خفيفة تكسر رتابة النويز فلا
    يُسمع كضجيج مولّد. والغلاف يفتح في ١٢ مللي ويغلق في ٣٥ — يدٌ تبدأ
    وتنتهي، لا مفتاح يُفتح ويُقفل."""
    n = int(SR * dur)
    base = rng.normal(0, 1, n)
    base = highpass(lowpass(base, 6000), 1800)

    # حبيبات الاحتكاك: نبضة كل ٢–٥ مللي بسعة عشوائية
    grains = np.zeros(n)
    i = 0
    while i < n:
        i += int(SR * rng.uniform(0.002, 0.005))
        if i >= n:
            break
        w = int(SR * 0.0016)
        seg = rng.normal(0, 1, min(w, n - i)) * np.hanning(min(w, n - i))
        grains[i:i + len(seg)] += seg * rng.uniform(0.3, 1.0)
    grains = highpass(lowpass(grains, 9000), 2500)

    sig = base * 0.62 + grains * 0.38
    env = np.ones(n)
    a = int(SR * 0.012); r = int(SR * 0.035)
    env[:a] = np.linspace(0, 1, a) ** 0.7
    env[-r:] = np.linspace(1, 0, r) ** 1.6
    # تموّج خفيف: ضغط اليد لا يثبت على طول السحبة
    env *= 1 + 0.10 * np.sin(2 * np.pi * np.arange(n) / SR * rng.uniform(7, 11))
    return sig * env


def tick():
    """تك طباعة شمعة: نقرة جافة قصيرة جداً بلا رنين — لا تزاحم الصمت."""
    n = int(SR * 0.035)
    sig = rng.normal(0, 1, n)
    sig = highpass(lowpass(sig, 5200), 1400)
    sig *= np.exp(-np.arange(n) / (SR * 0.006))
    body = np.sin(2 * np.pi * 1150 * np.arange(n) / SR) * np.exp(-np.arange(n) / (SR * 0.004))
    return sig * 0.8 + body * 0.2


def thump():
    """ضربة الوصول: سب منزلق ٥٥←٣٦ هرتز بتشبع خفيف وذيل قصير.

    البريف يقول «~40Hz»؛ النغمة الثابتة عند ٤٠ تُسمع طنيناً، والانزلاق
    من فوقها إليها يُسمع ضربة. والتشبع يضيف توافقيات تجعلها مسموعة على
    سمّاعة الجوال التي لا تنقل ٤٠ هرتز أصلاً."""
    n = int(SR * 0.55)
    t = np.arange(n) / SR
    f = 55 * np.exp(-t / 0.10) + 36
    ph = 2 * np.pi * np.cumsum(f) / SR
    sub = np.sin(ph) * np.exp(-t / 0.16)
    sub = np.tanh(sub * 2.1) / np.tanh(2.1)          # تشبع → توافقيات مسموعة
    click = rng.normal(0, 1, n) * np.exp(-t / 0.004)
    click = lowpass(click, 2200) * 0.25
    return sub * 0.92 + click


if __name__ == "__main__":
    for k, dur in (("pen_s", 0.28), ("pen_m", 0.75), ("pen_l", 1.60)):
        save(k, pen(dur), 0.82)
    save("tick", tick(), 0.55)
    save("thump", thump(), 0.95)
    print("→", D)
