# -*- coding: utf-8 -*-
# الحزمة F — «رسمية جادة» (أمر فهد 2026-08-03): طابع مؤسسي رزين — مكتوم، جاف، منخفض التردد، بلا زخرفة
import os, subprocess, imageio_ffmpeg

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
D = os.path.join(ROOT, "assets", "sfx_packs", "f_formal")
os.makedirs(D, exist_ok=True)
FF = imageio_ffmpeg.get_ffmpeg_exe()

def run(args, out):
    subprocess.run([FF, "-y", "-v", "error"] + args + [os.path.join(D, out)], check=True)

# ووش — هواء غامق قصير جاف (بلا صدى ولا لمعان)
run(["-f","lavfi","-i","anoisesrc=d=0.55:c=brown:a=0.9",
     "-af","lowpass=f=700,volume='min(t*7,1)*max(1-(t-0.18)*3.2,0)':eval=frame,volume=2.2"], "whoosh.wav")

# بوب — نقرة خشبية مكتومة بجسم منخفض
run(["-f","lavfi","-i","sine=frequency=180:duration=0.12",
     "-f","lavfi","-i","sine=frequency=880:duration=0.03",
     "-filter_complex",
     "[0]volume='max(1-t*10,0)':eval=frame[a];[1]volume='max(1-t*40,0)':eval=frame,volume=0.25[b];"
     "[a][b]amix=inputs=2:normalize=0,volume=2.2"], "pop.wav")

# تيك — نقرة قلم هادئة
run(["-f","lavfi","-i","sine=frequency=1150:duration=0.035",
     "-af","volume='max(1-t*32,0)':eval=frame,volume=0.85"], "tick.wav")

# إمباكت — ثود عميق جاف رزين: سب 42+84 بذيل قصير، بلا رشة نويز عالية
run(["-f","lavfi","-i","sine=frequency=42:duration=0.85",
     "-f","lavfi","-i","sine=frequency=84:duration=0.55",
     "-f","lavfi","-i","anoisesrc=d=0.07:c=brown:a=0.8",
     "-filter_complex",
     "[0]volume='max(1-t*1.6,0)':eval=frame[s0];[1]volume='max(1-t*2.6,0)':eval=frame,volume=0.6[s1];"
     "[2]lowpass=f=260,volume='max(1-t*15,0)':eval=frame,volume=0.7[n];"
     "[s0][s1][n]amix=inputs=3:normalize=0,volume=3.4,alimiter=limit=0.95:level=false"], "impact.wav")

# رايزر — درون توتر منخفض يتصاعد بهدوء (بلا تريمولو ولا صفير)
run(["-f","lavfi","-i","aevalsrc=exprs='sin(2*PI*t*(58+46*t))*min(t*1.2\\,1)*0.65':d=1.6",
     "-f","lavfi","-i","anoisesrc=d=1.6:c=brown:a=0.5",
     "-filter_complex",
     "[1]lowpass=f=900,volume='min(t*0.55,0.8)':eval=frame[n];"
     "[0][n]amix=inputs=2:normalize=0,afade=t=out:st=1.42:d=0.18,volume=2.0"], "riser.wav")

# سكسس — نغمة تأكيد رزينة: طبقة منخفضة + خامسة هادئة، هبوط سريع بلا احتفال
run(["-f","lavfi","-i","sine=frequency=196:duration=0.9",
     "-f","lavfi","-i","sine=frequency=294:duration=0.7",
     "-filter_complex",
     "[1]volume=0.4[b];[0][b]amix=inputs=2:normalize=0,"
     "volume='min(t*12,1)*max(1-t*1.5,0)':eval=frame,volume=1.8"], "success.wav")

print("pack F ->", sorted(os.listdir(D)))
