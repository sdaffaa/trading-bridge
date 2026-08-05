# -*- coding: utf-8 -*-
"""طبقة صوت هادئة لريلات تشغيلة ٢٦ (§12 — مؤثرات بلا كلام).

يعيد استعمال سرير وماستر تشغيلة ٢٥ نفسيهما، والمؤثرات مثبّتة على أحداث
كل ريل: رسم المستوى · ظهور أداة الصفقة · بلوغ الهدف.
"""
import os
from sfx_mux import mux
from run25_post import soft_bed, master, H

HERE = os.path.dirname(os.path.abspath(__file__))
DUR = 19.4
# (رسم المستوى، ظهور أداة الصفقة = الخطوة ٣، بلوغ الهدف = داخل الخطوة ٥)
BEATS = {"sweep": (4.10, 9.00, 14.88),
         "fvg":   (5.57, 9.26, 15.01),
         "bos":   (3.69, 10.41, 15.58)}

if __name__ == "__main__":
    import sys
    SUF = os.environ.get("LS_SUF", "_light")
    for key in (sys.argv[1:] or list(BEATS)):
        raw = os.path.join(HERE, f"reel26_{key}{SUF}_raw.mp4")
        if not os.path.isfile(raw):
            print("تخطٍّ (لا يوجد خام):", os.path.basename(raw)); continue
        t_lvl, t_box, t_ck = BEATS[key]
        bed = soft_bed(os.path.join(HERE, f"bed26_{key}{SUF}.wav"), DUR)
        ev = [("ui_tick", t_lvl, -20), ("impact_soft", t_box, -15),
              ("ui_confirm", t_ck, -18), (bed, 0.0, -6)]
        tmp = os.path.join(HERE, f"_q26_{key}{SUF}.mp4")
        out = os.path.join(HERE, f"reel26_{key}{SUF}_final.mp4")
        mux(raw, ev, tmp, dur=DUR, lufs=-16, sfx_dir=H)
        li, tp = master(tmp, out, DUR)
        os.remove(tmp); os.remove(bed + ".wav")
        print(f"{key:<6} {os.path.basename(out)} | {li:.1f} LUFS · TP {tp:.1f}")
