# -*- coding: utf-8 -*-
# رندر ومكس ريل الأخبار بنظام الصوت H (Institutional)
import os, subprocess, imageio_ffmpeg
from reel_render_any import render
from sfx_mux import mux

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
H = os.path.join(ROOT, "assets", "sfx_packs", "h_institutional")
MUSIC = os.path.join(ROOT, "assets", "music")
FF = imageio_ffmpeg.get_ffmpeg_exe()

DUR, T_NEWS, T_CTA = 27.1, 11.8, 22.1

def bed(src, out, dur, ti, tc):
    """بيد مؤسسي: pre-duck قبل الإمباكت + خفض عند الـCTA (معمار المكساج H)."""
    af = (f"aloop=loop=1:size=48000*40,atrim=0:{dur},"
          f"volume='1-0.62*exp(-pow(t-{ti},2)/0.10)':eval=frame,"
          f"volume='1-0.55/(1+exp(-6*(t-{tc})))':eval=frame,"
          f"volume=0.62,afade=t=in:d=1.0,afade=t=out:st={dur-1.0}:d=1.0")
    subprocess.run([FF, "-y", "-v", "error", "-i", os.path.join(MUSIC, src + ".wav"),
                    "-af", af, out], check=True)
    return out[:-4]

raw = os.path.join(HERE, "reel13_news_raw.mp4")
render(os.path.join(HERE, "reel13_news.html"), raw)
b = bed("bed_institutional", os.path.join(HERE, "bed13_news.wav"), DUR, T_NEWS, T_CTA)

EV = [
  ("reverse_atmos", 0.00, -4), ("impact_deep", 0.12, 0),        # الغلاف الداكن
  ("ui_scan", 2.45, -3), ("impact_clean", 3.00, -4),            # المسحة الضوئية
  ("ui_click", 3.95, -2), ("perc_low", 4.35, -6),               # منطقة الدخول
  ("ui_confirm", 4.95, -6),                                     # الدخول بشرطك
  ("ui_click", 5.95, -4), ("ui_tick", 6.45, -6),                # خط الهدف
  ("mech_click_bed", 7.60, -10), ("ui_tick", 8.75, -8),         # الزحف البطيء
  ("reverse_swell", 9.60, -5), ("riser_soft", 8.90, -4),        # البناء نحو الخبر
  ("impact_deep", 11.80, 0), ("granular_metal", 12.05, -9),     # لحظة صدور الخبر
  ("pulse_min", 12.60, -6), ("pulse_min", 12.95, -7),
  ("ui_confirm", 14.75, -3), ("impact_soft", 15.05, -5),        # الهدف تحقق
  ("ui_alert", 16.55, -4),                                      # تحذير السبريد
  ("sub_drop", 19.30, -8),                                      # الخلاصة
  ("impact_soft", 22.10, -4), ("logo_sting", 22.85, -2),        # CTA وستينج الهوية
  (b, 0.0, -8),
]
mux(raw, EV, os.path.join(HERE, "reel13_news_final.mp4"), dur=DUR, lufs=-14, sfx_dir=H)
print("news FINAL OK")
