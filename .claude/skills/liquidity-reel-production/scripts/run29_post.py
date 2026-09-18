# -*- coding: utf-8 -*-
"""صوت ريل الباك تست: النبرة أهدأ لأن الصورة لم تعد تتحرّك.

في تشغيلة ٢٨ كانت الكاميرا تصنع نصف التوتّر، فكان الصوت يرافقها. هنا
الجارت ثابت، فلو بقيت الضربات بالحدّة نفسها لبدت مُقحمة على صورة ساكنة.
خُفِّضت الذُّرى وأُبقيت النقرات: النقرة تُعلِّم انتقال الطبقة، والضربة
تُحجز للتنفيذ ولحظة بلوغ الهدف وحدهما.
"""
import os, sys

from sfx_mux import mux
from run25_post import master, H
from run26_post import bed, sub

HERE = os.path.dirname(os.path.abspath(__file__))
DUR = 30.0
LAYERS = [6.05, 9.25, 12.35, 15.60, 19.00]
EV = ([("impact_deep", 0.10, -13), ("reverse_swell", 2.35, -17),
       ("sub_drop", 2.90, -13), ("ui_scan", 3.00, -20)]
      + [("ui_click", t, -24) for t in LAYERS]
      + [("reverse_swell", 16.30, -18), ("impact_clean", 17.80, -14),
         ("reverse_swell", 20.60, -19),
         ("sub_drop", 22.05, -12), ("impact_clean", 22.10, -14),
         ("riser_short", 24.60, -20), ("ui_confirm", 25.62, -15),
         ("ui_scan", 25.45, -21)])

if __name__ == "__main__":
    for tag in sys.argv[1:]:
        raw = os.path.join(HERE, f"reel29_{tag}_light_raw.mp4")
        if not os.path.isfile(raw):
            print("تخطٍّ:", tag); continue
        b1 = bed(os.path.join(HERE, f"bed29_{tag}.wav"), DUR)
        b2 = sub(os.path.join(HERE, f"sub29_{tag}.wav"), DUR)
        tmp = os.path.join(HERE, f"_q29_{tag}.mp4")
        out = os.path.join(HERE, f"reel29_{tag}_final.mp4")
        mux(raw, EV + [(b1, 0.0, -8), (b2, 0.0, -10)], tmp, dur=DUR,
            lufs=-16, sfx_dir=H)
        li, tp = master(tmp, out, DUR)
        for f in (tmp, b1 + ".wav", b2 + ".wav"):
            os.remove(f)
        print(f"{tag:<24} {li:.1f} LUFS · TP {tp:.1f}")
