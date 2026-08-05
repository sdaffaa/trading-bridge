# -*- coding: utf-8 -*-
"""صوت الريل الشامل: نفس اللغة النابضة، مع ذروة عند التنفيذ ونقرة لكل طبقة."""
import os
from sfx_mux import mux
from run25_post import master, H
from run26_post import bed, sub

HERE = os.path.dirname(os.path.abspath(__file__))
DUR = 30.5
LAYERS = [6.05, 9.25, 12.35, 15.60, 19.00]     # بداية كل سبب
EV = ([("impact_deep", 0.10, -12)]                       # ضربة الهوك
      + [("reverse_swell", 2.35, -16), ("sub_drop", 2.90, -12)]   # الانسحاب الكاشف
      + [("ui_click", t, -24) for t in LAYERS]           # نقرة لكل طبقة
      + [("ui_scan", 3.00, -19),                         # رسم المستوى
         ("reverse_swell", 16.20, -17), ("impact_clean", 17.80, -13),   # الكنس
         ("reverse_swell", 20.50, -18),
         ("sub_drop", 22.05, -11), ("impact_clean", 22.10, -13),       # التنفيذ
         ("riser_short", 25.70, -19), ("ui_confirm", 26.80, -15)])     # الهدف

if __name__ == "__main__":
    raw = os.path.join(HERE, "reel28_light_raw.mp4")
    b1 = bed(os.path.join(HERE, "bed28.wav"), DUR)
    b2 = sub(os.path.join(HERE, "sub28.wav"), DUR)
    tmp = os.path.join(HERE, "_q28.mp4")
    out = os.path.join(HERE, "reel28_light_final.mp4")
    mux(raw, EV + [(b1, 0.0, -7), (b2, 0.0, -9)], tmp, dur=DUR, lufs=-16, sfx_dir=H)
    li, tp = master(tmp, out, DUR)
    for f in (tmp, b1 + ".wav", b2 + ".wav"):
        os.remove(f)
    print(f"{os.path.basename(out)} | {len(EV)+2} حدثاً | {li:.1f} LUFS · TP {tp:.1f}")
