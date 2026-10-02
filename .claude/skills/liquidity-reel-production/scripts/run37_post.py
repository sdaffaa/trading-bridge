# -*- coding: utf-8 -*-
"""رندر ريل ٣٧ ودمج طبقته الصوتية.

بريف فهد: **بدون فويس أوفر وبدون موسيقى خلفية**. مؤثرات فقط — سبع سحبات
قلم، وتِك لكل شمعة تُطبع في آخر ثلاث ثوانٍ، وضربة واحدة عند بلوغ الهدف.
والماستر عند −16 LUFS، والصمت بين المؤثرات يبقى صمتاً حقيقياً لا يُملأ.

والرندر بستين إطاراً (`LS_FPS=60`) كما يوجب بند التسليم.

    python3 run37_post.py            # يرندر ثم يدمج
    python3 run37_post.py --mux      # يدمج فقط (الفيديو الخام موجود)
"""
import os
import subprocess
import sys

from sfx_mux import mux

HERE = os.path.dirname(os.path.abspath(__file__))
PEN = os.path.normpath(os.path.join(HERE, "..", "..", "..", "..",
                                    "assets", "sfx_packs", "p_pen"))
RAW = os.path.join(HERE, "reel37_draw_raw.mp4")
OUT = os.path.join(HERE, "reel37_draw_final.mp4")

if __name__ == "__main__":
    import run37_draw as R
    if "--mux" not in sys.argv:
        env = dict(os.environ, LS_FPS="60")
        subprocess.run([sys.executable, os.path.join(HERE, "reel_render_any.py"),
                        os.path.join(HERE, "reel37_draw.html"), RAW],
                       check=True, env=env)
    mux(RAW, R.SFX, OUT, dur=R.DUR, lufs=-16, sfx_dir=PEN)
    mb = os.path.getsize(OUT) / 1048576
    print(f"→ {os.path.basename(OUT)}  {mb:.1f} MB  ·  {R.DUR}s · 60fps · "
          f"{len(R.SFX)} مؤثراً (٧ قلم + {R.BARS_LIVE} تِك + ضربة)")
    if mb > 30:
        print("⚠ يتجاوز سقف ٣٠ ميغابايت في بند التسليم")
