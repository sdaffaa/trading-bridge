# -*- coding: utf-8 -*-
# رندر ومكس الريل الفيروسي «وقفك يرسل عنوانك للسوق» — نظام الصوت H
import os, subprocess, imageio_ffmpeg
from reel_render_any import render
from sfx_mux import mux

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
H = os.path.join(ROOT, "assets", "sfx_packs", "h_institutional")
MUSIC = os.path.join(ROOT, "assets", "music")
FF = imageio_ffmpeg.get_ffmpeg_exe()

DUR, T_SWEEP, T_CTA = 34.1, 14.2, 29.1

def bed(src, out, dur, ti, tc):
    af = (f"aloop=loop=2:size=48000*40,atrim=0:{dur},"
          f"volume='1-0.62*exp(-pow(t-{ti},2)/0.10)':eval=frame,"      # pre-duck حول الذروة
          f"volume='1-0.30*exp(-pow(t-16.1,2)/0.05)':eval=frame,"      # صمت قصير عند الانهيار
          f"volume='1-0.55/(1+exp(-6*(t-{tc})))':eval=frame,"
          f"volume=0.60,afade=t=in:d=1.2,afade=t=out:st={dur-1.2}:d=1.2")
    subprocess.run([FF, "-y", "-v", "error", "-i", os.path.join(MUSIC, src + ".wav"),
                    "-af", af, out], check=True)
    return out[:-4]

raw = os.path.join(HERE, "reel14_stops_raw.mp4")
render(os.path.join(HERE, "reel14_stops.html"), raw)
b = bed("bed_institutional_tense", os.path.join(HERE, "bed14_stops.wav"), DUR, T_SWEEP, T_CTA)

EV = [
  ("reverse_atmos", 0.00, -4), ("impact_deep", 0.12, 0),               # الغلاف الداكن
  ("ui_scan", 2.45, -3), ("impact_clean", 3.00, -5),                   # المسحة الضوئية
  ("ui_click", 3.95, -4), ("ui_click", 4.75, -6), ("ui_click", 4.95, -7), ("ui_click", 5.15, -8),
  ("ui_tick", 6.15, -10), ("ui_tick", 6.45, -9), ("ui_tick", 6.70, -8), ("ui_tick", 6.90, -7),
  ("mech_click_bed", 6.10, -12),                                        # تراكم الأوامر
  ("ui_confirm", 7.35, -8),
  ("sub_drop", 10.20, -10),                                             # انقلاب المنظور
  ("ui_click", 10.70, -6), ("pulse_min", 11.50, -8),
  ("riser_soft", 11.05, -4),                                            # البناء نحو السحب
  ("impact_deep", 14.20, 0), ("granular_metal", 14.35, -9),             # سحب السيولة
  ("impact_clean", 16.10, -2),                                          # الانهيار
  ("ui_alert", 16.40, -6),
  ("impact_soft", 20.10, -5),                                           # التبرئة
  ("ui_confirm", 21.20, -5), ("ui_confirm", 23.30, -6),                 # بطاقات الحل
  ("perc_low", 25.10, -8), ("pulse_sub", 26.60, -7),
  ("ui_confirm", 26.70, -3), ("impact_soft", 27.10, -6),                # الخلاصة
  ("impact_soft", 29.10, -4), ("logo_sting", 29.85, -2),                # CTA
  (b, 0.0, -8),
]
mux(raw, EV, os.path.join(HERE, "reel14_stops_final.mp4"), dur=DUR, lufs=-14, sfx_dir=H)
print("stops FINAL OK")
