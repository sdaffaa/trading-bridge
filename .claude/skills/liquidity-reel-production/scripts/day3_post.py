# -*- coding: utf-8 -*-
import json, os, subprocess, sys, imageio_ffmpeg
from reel_render_any import render
from sfx_mux import mux
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
H = os.path.join(ROOT, "assets", "sfx_packs", "h_institutional")
MUSIC = os.path.join(ROOT, "assets", "music")
FF = imageio_ffmpeg.get_ffmpeg_exe()
META = json.load(open(os.path.join(HERE, "day3_reels_meta.json"), encoding="utf-8"))
BEDS = {"tadul": "bed_institutional", "thabat": "bed_institutional_tense"}

def bed(src, out, dur, ti, tc):
    af = (f"aloop=loop=2:size=48000*40,atrim=0:{dur},"
          f"volume='1-0.60*exp(-pow(t-{ti},2)/0.10)':eval=frame,"
          f"volume='1-0.55/(1+exp(-6*(t-{tc})))':eval=frame,"
          f"volume=0.60,afade=t=in:d=1.2,afade=t=out:st={dur-1.2}:d=1.2")
    subprocess.run([FF, "-y", "-v", "error", "-i", os.path.join(MUSIC, src + ".wav"), "-af", af, out], check=True)
    return out[:-4]

def events(ti, tc, b):
    return [("reverse_atmos", 0.00, -4), ("impact_deep", 0.12, 0),
            ("ui_scan", 2.45, -3), ("impact_clean", 3.00, -5),
            ("ui_click", 3.95, -4), ("ui_click", 5.85, -6), ("ui_tick", 6.40, -8),
            ("mech_click_bed", 7.20, -13), ("pulse_min", 8.10, -9),
            ("riser_soft", ti - 3.1, -4), ("impact_deep", ti, 0), ("granular_metal", ti + 0.15, -9),
            ("ui_confirm", ti + 2.6, -4), ("impact_soft", ti + 3.0, -6),
            ("pulse_sub", tc - 2.6, -8), ("ui_confirm", tc - 1.4, -5),
            ("impact_soft", tc, -4), ("logo_sting", tc + 0.75, -2), (b, 0.0, -8)]

for key in (sys.argv[1:] or list(META)):
    dur, ti, tc = META[key]
    raw = os.path.join(HERE, f"reel_day3_{key}_raw.mp4")
    render(os.path.join(HERE, f"reel_day3_{key}.html"), raw)
    b = bed(BEDS[key], os.path.join(HERE, f"bed_day3_{key}.wav"), dur, ti, tc)
    mux(raw, events(ti, tc, b), os.path.join(HERE, f"reel_day3_{key}_final.mp4"), dur=dur, lufs=-14, sfx_dir=H)
    print(key, "FINAL OK")
print("ALL DONE")
