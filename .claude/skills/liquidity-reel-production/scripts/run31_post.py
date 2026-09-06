# -*- coding: utf-8 -*-
"""رندر ريلات تشغيلة ٣١ ودمج طبقة المؤثرات (§12 — بلا كلام منطوق).

المؤثرات مثبّتة على لحظات الأحداث في `run31_reel.SFX`، والماستر عند
−16 LUFS لأن طبقة بلا كلام تُخلط أخفض من طبقة فيها صوت (§12).
"""
import os, subprocess, sys

from sfx_mux import mux
import run31_reel as R

HERE = os.path.dirname(os.path.abspath(__file__))

if __name__ == "__main__":
    for slug in sys.argv[1:]:
        raw = os.path.join(HERE, f"reel31_{slug}_raw.mp4")
        subprocess.run([sys.executable, os.path.join(HERE, "reel_render_any.py"),
                        os.path.join(HERE, f"reel31_{slug}.html"), raw], check=True)
        out = os.path.join(HERE, f"reel31_{slug}_final.mp4")
        mux(raw, R.SFX, out, dur=R.DUR, lufs=-16)
        print(f"{slug:<10} → {os.path.basename(out)} "
              f"{os.path.getsize(out)//1024} KB")
