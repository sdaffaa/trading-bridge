# -*- coding: utf-8 -*-
"""نقرة واجهة للحزمة G — الصوت الناقص في ريل «جلسة متداول».

كانت نقرات الأدوات تُنفَّذ بـ`pop`، وهي نغمة حدث لا نقرة زرّ: طويلة
(~180ms) ومنغّمة، فتُسمع كإشعار لا كضغطة فأرة. النقرة الحقيقية ترانزينت
نويز قصير جداً (~22ms) بلا نغمة، ونقرة الزرّ الفيزيائية نقرتان: هبوط
الزرّ ثم ارتداده بعد ~14ms وبطاقة أقل.

    python3 gen_sfx_click.py
"""
import os, wave
import numpy as np

SR = 48000
HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.normpath(os.path.join(HERE, "..", "..", "..", "..",
                                  "assets", "sfx_packs", "g_real"))
rng = np.random.default_rng(21)


def lowpass(sig, fc):
    a = np.exp(-2 * np.pi * fc / SR)
    y = np.zeros_like(sig); acc = 0.0
    for i, v in enumerate(sig):
        acc = (1 - a) * v + a * acc; y[i] = acc
    return y


def transient(dur, tau, fc_lo, fc_hi, amp):
    n = int(SR * dur)
    noise = rng.standard_normal(n)
    band = lowpass(noise, fc_hi) - lowpass(noise, fc_lo)
    return band * np.exp(-np.arange(n) / (SR * tau)) * amp


def main():
    down = transient(0.022, 0.0030, 900, 6500, 1.00)      # هبوط الزرّ
    up = transient(0.016, 0.0022, 1400, 8000, 0.42)       # الارتداد
    n = int(SR * 0.045)
    sig = np.zeros(n)
    sig[:len(down)] += down
    off = int(SR * 0.014)
    sig[off:off + len(up)] += up
    sig = sig / (np.max(np.abs(sig)) + 1e-9) * 0.72       # أهدأ من الأحداث
    with wave.open(os.path.join(D, "click.wav"), "w") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((sig * 32767).astype(np.int16).tobytes())
    print(f'click.wav {len(sig)/SR:.3f}s → {D}')


if __name__ == "__main__":
    main()
