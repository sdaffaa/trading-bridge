# -*- coding: utf-8 -*-
"""صوت الريل الشامل: ذروة عند التنفيذ ونقرة لكل طبقة، فوق سرير نابض."""
import os, sys
from sfx_mux import mux
from run25_post import master, H
from run26_post import bed, sub

HERE = os.path.dirname(os.path.abspath(__file__))
DUR = 30.5
LAYERS = [6.05, 9.25, 12.35, 15.60, 19.00]
EV = ([("impact_deep", 0.10, -12), ("reverse_swell", 2.35, -16), ("sub_drop", 2.90, -12)]
      + [("ui_click", t, -24) for t in LAYERS]
      + [("ui_scan", 3.00, -19), ("reverse_swell", 16.20, -17),
         ("impact_clean", 17.80, -13), ("reverse_swell", 20.50, -18),
         ("sub_drop", 22.05, -11), ("impact_clean", 22.10, -13),
         ("riser_short", 25.70, -19), ("ui_confirm", 26.80, -15)])

if __name__ == "__main__":
    for tag in sys.argv[1:]:
        raw = os.path.join(HERE, f"reel28_{tag}_light_raw.mp4")
        if not os.path.isfile(raw):
            print("تخطٍّ:", tag); continue
        b1 = bed(os.path.join(HERE, f"bed28_{tag}.wav"), DUR)
        b2 = sub(os.path.join(HERE, f"sub28_{tag}.wav"), DUR)
        tmp = os.path.join(HERE, f"_q28_{tag}.mp4")
        out = os.path.join(HERE, f"reel28_{tag}_final.mp4")
        mux(raw, EV + [(b1, 0.0, -7), (b2, 0.0, -9)], tmp, dur=DUR, lufs=-16, sfx_dir=H)
        li, tp = master(tmp, out, DUR)
        for f in (tmp, b1 + ".wav", b2 + ".wav"):
            os.remove(f)
        print(f"{tag:<20} {li:.1f} LUFS · TP {tp:.1f}")
