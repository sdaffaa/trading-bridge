# -*- coding: utf-8 -*-
import os, subprocess, imageio_ffmpeg
from reel_render_any import render
from sfx_mux import mux
HERE=os.path.dirname(os.path.abspath(__file__))
ROOT=os.path.normpath(os.path.join(HERE,"..","..","..",".."))
H=os.path.join(ROOT,"assets","sfx_packs","h_institutional"); MUSIC=os.path.join(ROOT,"assets","music")
FF=imageio_ffmpeg.get_ffmpeg_exe()
DUR, CTA = 24.4, 19.6
af=(f"aloop=loop=2:size=48000*40,atrim=0:{DUR},"
    f"volume='1-0.35*exp(-pow(t-18.5,2)/0.12)':eval=frame,"
    f"volume='1-0.55/(1+exp(-6*(t-{CTA})))':eval=frame,"
    f"volume=0.58,afade=t=in:d=1.2,afade=t=out:st={DUR-1.2}:d=1.2")
raw=os.path.join(HERE,"reel_grid_raw.mp4")
render(os.path.join(HERE,"reel_grid.html"), raw)
bed=os.path.join(HERE,"bed_grid.wav")
subprocess.run([FF,"-y","-v","error","-i",os.path.join(MUSIC,"bed_institutional.wav"),"-af",af,bed],check=True)

EV=[("reverse_atmos",0.00,-4),("impact_deep",0.12,0),
    ("ui_scan",2.45,-3),("impact_clean",3.00,-5)]
for i in range(6):                      # ظهور الإطارات الست
    EV.append(("ui_tick", 2.78+i*0.22, -9))
for i in range(6):                      # رسم محتوى كل خانة
    EV.append(("ui_click", 5.25+i*0.95, -7))
    EV.append(("perc_filtered", 5.55+i*0.95, -13))
for i in range(6):                      # صدور الحكم على كل خانة
    EV.append(("ui_confirm", 11.62+i*1.15, -6))
    EV.append(("pulse_min", 11.70+i*1.15, -11))
EV += [("riser_short",17.0,-7),("impact_deep",18.42,-2),("granular_air",18.6,-16),
       ("impact_soft",CTA,-4),("logo_sting",CTA+0.75,-2),(bed[:-4],0.0,-8)]
mux(raw, EV, os.path.join(HERE,"reel_grid_final.mp4"), dur=DUR, lufs=-14, sfx_dir=H)
print("GRID FINAL OK")
