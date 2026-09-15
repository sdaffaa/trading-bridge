# -*- coding: utf-8 -*-
# الحزمة E — «قوية» (طلب فهد 2026-08-03): مؤثرات أضخم وأعمق، ترانزينتات حادة وسب-بيس مركب
import os, subprocess, imageio_ffmpeg

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
D = os.path.join(ROOT, "assets", "sfx_packs", "e_strong")
os.makedirs(D, exist_ok=True)
FF = imageio_ffmpeg.get_ffmpeg_exe()

def run(args, out):
    subprocess.run([FF, "-y", "-v", "error"] + args + [os.path.join(D, out)], check=True)

# ووش — كنسة هوائية عريضة بهجوم سريع وذيل صدى
run(["-f","lavfi","-i","anoisesrc=d=0.9:c=pink:a=1.0",
     "-f","lavfi","-i","anoisesrc=d=0.9:c=white:a=0.55",
     "-filter_complex",
     "[0]lowpass=f=1400,volume='min(t*9,1)*max(1-(t-0.28)*2.6,0)':eval=frame[a];"
     "[1]highpass=f=900,lowpass=f=6500,volume='min(t*12,1)*max(1-(t-0.2)*3.2,0)':eval=frame[b];"
     "[a][b]amix=inputs=2:normalize=0,aecho=0.5:0.4:55:0.3,volume=3.2"], "whoosh.wav")

# بوب — نقرة مزدوجة بجسم
run(["-f","lavfi","-i","sine=frequency=520:duration=0.16",
     "-f","lavfi","-i","sine=frequency=1040:duration=0.09",
     "-f","lavfi","-i","anoisesrc=d=0.045:c=white:a=0.5",
     "-filter_complex",
     "[0]volume='max(1-t*8,0)':eval=frame[a];[1]volume='max(1-t*14,0)':eval=frame,volume=0.5[b];"
     "[2]bandpass=f=2400:w=1800,volume='max(1-t*24,0)':eval=frame[c];"
     "[a][b][c]amix=inputs=3:normalize=0,volume=3.0"], "pop.wav")

# تيك — نقرة حادة نظيفة
run(["-f","lavfi","-i","sine=frequency=2100:duration=0.05",
     "-f","lavfi","-i","anoisesrc=d=0.02:c=white:a=0.4",
     "-filter_complex",
     "[1]highpass=f=3000[b];[0][b]amix=inputs=2:normalize=0,volume='max(1-t*26,0)':eval=frame,volume=1.6"], "tick.wav")

# إمباكت — ضربة سينمائية مركبة: سب 36+72+145 + نويز برست + كليب خفيف
run(["-f","lavfi","-i","sine=frequency=36:duration=1.3",
     "-f","lavfi","-i","sine=frequency=72:duration=1.0",
     "-f","lavfi","-i","sine=frequency=145:duration=0.7",
     "-f","lavfi","-i","anoisesrc=d=0.2:c=brown:a=1.0",
     "-f","lavfi","-i","anoisesrc=d=0.09:c=white:a=0.7",
     "-filter_complex",
     "[0]volume='max(1-t*0.95,0)':eval=frame[s0];[1]volume='max(1-t*1.6,0)':eval=frame,volume=0.8[s1];"
     "[2]volume='max(1-t*3.2,0)':eval=frame,volume=0.55[s2];"
     "[3]lowpass=f=420,volume='max(1-t*6,0)':eval=frame,volume=0.9[n0];"
     "[4]bandpass=f=2800:w=2400,volume='max(1-t*16,0)':eval=frame,volume=0.5[n1];"
     "[s0][s1][s2][n0][n1]amix=inputs=5:normalize=0,volume=4.4,alimiter=limit=0.97:level=false"], "impact.wav")

# رايزر — 1.8ث: نويز متصاعد + صفير صاعد + تريمولو يتسارع
run(["-f","lavfi","-i","anoisesrc=d=1.8:c=pink:a=0.9",
     "-f","lavfi","-i","aevalsrc=exprs='sin(2*PI*t*(85+260*t*t))*min(t*0.9\\,1)*0.7':d=1.8",
     "-filter_complex",
     "[0]lowpass=f=2600,volume='min(t*0.7,1)*min(t*0.7,1)':eval=frame[a];"
     "[a][1]amix=inputs=2:normalize=0,tremolo=f=9:d=0.35,afade=t=out:st=1.62:d=0.18,volume=2.6"], "riser.wav")

# سكسس — وتد صاعد لامع بجسم
run(["-f","lavfi","-i","sine=frequency=294:duration=1.2",
     "-f","lavfi","-i","sine=frequency=440:duration=1.2",
     "-f","lavfi","-i","sine=frequency=587:duration=1.0",
     "-f","lavfi","-i","sine=frequency=1174:duration=0.6",
     "-filter_complex",
     "[3]volume=0.28[d];[0][1][2][d]amix=inputs=4:normalize=0,"
     "volume='min(t*9,1)*max(1-(t-0.35)*1.15,0)':eval=frame,volume=2.6"], "success.wav")

print("pack E ->", sorted(os.listdir(D)))
