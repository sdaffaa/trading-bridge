# -*- coding: utf-8 -*-
"""رندر ريل «جلسة متداول» ودمج طبقة المؤثرات (§12 — بلا كلام منطوق).

الحزمة `g_real` لا الحزمة الأساسية: نقراتها مبنية من ترانزينتات نويز
حقيقية فتناسب واجهةً تُنقَر، وهي افتراضي §209 أصلاً.
"""
import os, subprocess, sys

from sfx_mux import mux
import run32_desk as D

HERE = os.path.dirname(os.path.abspath(__file__))
PACK = os.path.normpath(os.path.join(HERE, "..", "..", "..", "..",
                                     "assets", "sfx_packs", "g_real"))

if __name__ == "__main__":
    for slug in sys.argv[1:]:
        raw = os.path.join(HERE, f"reel32_{slug}_raw.mp4")
        subprocess.run([sys.executable, os.path.join(HERE, "reel_render_any.py"),
                        os.path.join(HERE, f"reel32_{slug}.html"), raw], check=True)
        out = os.path.join(HERE, f"reel32_{slug}_final.mp4")
        mux(raw, D.SFX, out, dur=D.DUR, lufs=-16, sfx_dir=PACK)
        print(f"{slug:<10} → {os.path.basename(out)} {os.path.getsize(out)//1024} KB")
