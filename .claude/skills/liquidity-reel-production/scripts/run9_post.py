# -*- coding: utf-8 -*-
# run9 — رندر الريلز الأربعة + موسيقى مبطنة (داكنق عند الإمباكت والـCTA) + مكس حزمة G بترتيب V2
import os, subprocess, imageio_ffmpeg
from reel_render_any import render
from sfx_mux import mux

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
G = os.path.join(ROOT, "assets", "sfx_packs", "g_real")
MUSIC = os.path.join(ROOT, "assets", "music")
FF = imageio_ffmpeg.get_ffmpeg_exe()

def bed(src, out, dur, ti, tc):
    """بيد موسيقي: انخفاض غاوسي عند الإمباكت + خفض سيني بعد الـCTA (أمر المكس V2)."""
    af = (f"atrim=0:{dur},"
          f"volume='1-0.55*exp(-pow(t-{ti},2)/0.16)':eval=frame,"
          f"volume='1-0.6/(1+exp(-6*(t-{tc})))':eval=frame,"
          f"volume=0.6,afade=t=in:d=0.5,afade=t=out:st={dur-0.9}:d=0.9")
    subprocess.run([FF, "-y", "-v", "error", "-i", os.path.join(MUSIC, src + ".wav"),
                    "-af", af, out], check=True)
    return out[:-4]  # بلا الامتداد — sfx_mux يضيف .wav

JOBS = [
 ("fomo", "hype", 25.1, 14.9, 20.1,
  [("impact", 0.12, -3), ("whoosh", 2.5, 0),
   ("tick", 3.9, 0), ("pop", 4.35, -2), ("tick", 6.1, -2), ("pop", 6.6, -2),
   ("whoosh", 8.9, -5), ("pop", 12.9, 0), ("riser", 13.35, -2), ("impact", 14.9, 0),
   ("success", 16.7, 0), ("pop", 20.1, -3)]),
 ("backtest", "calm", 25.4, 16.5, 20.4,
  [("impact", 0.12, -3), ("whoosh", 2.5, 0),
   ("pop", 4.3, 0), ("tick", 6.9, 0), ("pop", 7.3, -2), ("whoosh", 10.3, -5),
   ("pop", 13.9, 0), ("riser", 15.0, -2), ("impact", 16.5, 0),
   ("success", 17.4, 0), ("pop", 20.4, -3)]),
 ("lot", "calm", 25.0, 12.95, 20.0,
  [("impact", 0.12, -3), ("whoosh", 2.5, 0),
   ("pop", 4.3, 0), ("pop", 5.7, -2), ("pop", 8.9, 0), ("pop", 10.3, -2),
   ("riser", 11.45, -2), ("impact", 12.95, 0),
   ("success", 17.3, 0), ("pop", 20.0, -3)]),
 ("alf", "hype", 26.4, 14.65, 21.4,
  [("impact", 0.12, -3), ("whoosh", 2.5, 0),
   ("tick", 4.0, 0), ("pop", 4.6, -2), ("whoosh", 6.3, -5),
   ("tick", 8.6, 0), ("pop", 10.0, -3), ("pop", 10.9, -2), ("pop", 13.3, 0),
   ("riser", 13.1, -2), ("impact", 14.65, 0), ("pop", 15.1, -2),
   ("tick", 17.4, -2), ("pop", 17.9, -3), ("success", 18.65, 0), ("pop", 21.4, -3)]),
]

for key, mus, dur, ti, tc, events in JOBS:
    raw = os.path.join(HERE, f"reel9_{key}_raw.mp4")
    render(os.path.join(HERE, f"reel9_{key}.html"), raw)
    bpath = bed(mus, os.path.join(HERE, f"bed9_{key}.wav"), dur, ti, tc)
    mux(raw, events + [(bpath, 0.0, -7)], os.path.join(HERE, f"reel9_{key}_final.mp4"),
        dur=dur, lufs=-14, sfx_dir=G)
    print(key, "FINAL OK")
print("ALL DONE")
