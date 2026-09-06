# -*- coding: utf-8 -*-
# توليد حزم مؤثرات بديلة (أوفلاين، توليف ffmpeg) للمقارنة — كل حزمة نفس الأدوار الستة:
# whoosh, pop, tick, impact, riser, success
import os, subprocess, imageio_ffmpeg

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
FF = imageio_ffmpeg.get_ffmpeg_exe()

def run(args):
    subprocess.run([FF, "-y", "-v", "error"] + args, check=True)

def gen(pack, recipes):
    d = os.path.join(ROOT, "assets", "sfx_packs", pack)
    os.makedirs(d, exist_ok=True)
    for name, args in recipes.items():
        run(args + [os.path.join(d, name + ".wav")])
    print(pack, "->", sorted(os.listdir(d)))

# ===== الحزمة B — «ناعمة عميقة»: دفء وهدوء، بدون حدة =====
gen("b_soft", {
 "whoosh": ["-f","lavfi","-i","anoisesrc=d=0.8:c=brown:a=0.9",
            "-af","lowpass=f=1100,volume='min(t*4,1)*max(1-(t-0.4)*2.6,0)':eval=frame,afade=t=out:st=0.65:d=0.15"],
 "pop":    ["-f","lavfi","-i","sine=frequency=220:duration=0.14",
            "-af","volume='max(1-t*9,0)':eval=frame,volume=1.5"],
 "tick":   ["-f","lavfi","-i","sine=frequency=400:duration=0.05",
            "-af","volume='max(1-t*22,0)':eval=frame"],
 "impact": ["-f","lavfi","-i","sine=frequency=45:duration=0.65","-f","lavfi","-i","anoisesrc=d=0.12:c=brown:a=0.6",
            "-filter_complex","[0]volume='max(1-t*1.8,0)':eval=frame[a];[1]lowpass=f=380,volume='max(1-t*9,0)':eval=frame[b];[a][b]amix=inputs=2:duration=longest,volume=2.6"],
 "riser":  ["-f","lavfi","-i","aevalsrc=exprs='sin(2*PI*t*(120+280*t))*min(t*1.1\\,1)*0.7':d=1.4",
            "-af","lowpass=f=1500,afade=t=out:st=1.15:d=0.25"],
 "success":["-f","lavfi","-i","sine=frequency=330:duration=1.0","-f","lavfi","-i","sine=frequency=415:duration=1.0","-f","lavfi","-i","sine=frequency=494:duration=1.0",
            "-filter_complex","[0][1][2]amix=inputs=3:normalize=0,volume='min(t*7,1)*max(1-t*1.15,0)':eval=frame,volume=1.4"],
})

# ===== الحزمة C — «زجاجية نقية»: نقرات حادة نظيفة، إحساس تقني =====
gen("c_glassy", {
 "whoosh": ["-f","lavfi","-i","anoisesrc=d=0.5:c=white:a=0.7",
            "-af","highpass=f=1600,lowpass=f=9000,volume='min(t*8,1)*max(1-(t-0.2)*3.4,0)':eval=frame"],
 "pop":    ["-f","lavfi","-i","sine=frequency=1200:duration=0.08","-f","lavfi","-i","sine=frequency=2400:duration=0.05",
            "-filter_complex","[1]volume=0.3[b];[0][b]amix=inputs=2:normalize=0,volume='max(1-t*15,0)':eval=frame,volume=1.6"],
 "tick":   ["-f","lavfi","-i","sine=frequency=2600:duration=0.03",
            "-af","volume='max(1-t*35,0)':eval=frame,volume=0.9"],
 "impact": ["-f","lavfi","-i","sine=frequency=90:duration=0.4","-f","lavfi","-i","anoisesrc=d=0.08:c=white:a=0.5",
            "-filter_complex","[1]bandpass=f=3000:w=2000,volume='max(1-t*14,0)':eval=frame[b];[0]volume='max(1-t*3,0)':eval=frame[a];[a][b]amix=inputs=2:duration=longest,volume=2.4"],
 "riser":  ["-f","lavfi","-i","aevalsrc=exprs='sin(2*PI*t*(400+900*t))*min(t*1.6\\,1)*0.55':d=1.1",
            "-af","afade=t=out:st=0.9:d=0.2"],
 "success":["-f","lavfi","-i","sine=frequency=880:duration=1.1","-f","lavfi","-i","sine=frequency=1760:duration=0.7",
            "-filter_complex","[1]volume=0.35[b];[0][b]amix=inputs=2:normalize=0,volume='max(1-t*1.1,0)':eval=frame,volume=1.5"],
})

# ===== الحزمة D — «سينمائية»: هواء وصدى وضربة عميقة مركّبة =====
gen("d_cinema", {
 "whoosh": ["-f","lavfi","-i","anoisesrc=d=1.0:c=pink:a=0.9",
            "-af","lowpass=f=900,aecho=0.6:0.45:60:0.35,volume='min(t*3,1)*max(1-(t-0.5)*2.2,0)':eval=frame"],
 "pop":    ["-f","lavfi","-i","sine=frequency=150:duration=0.16",
            "-af","volume='max(1-t*8,0)':eval=frame,volume=1.8"],
 "tick":   ["-f","lavfi","-i","sine=frequency=500:duration=0.04",
            "-af","volume='max(1-t*28,0)':eval=frame"],
 "impact": ["-f","lavfi","-i","sine=frequency=55:duration=1.1","-f","lavfi","-i","sine=frequency=110:duration=0.9",
            "-f","lavfi","-i","sine=frequency=165:duration=0.7","-f","lavfi","-i","anoisesrc=d=0.15:c=brown:a=0.7",
            "-filter_complex","[3]lowpass=f=300,volume='max(1-t*7,0)':eval=frame[n];[0][1][2][n]amix=inputs=4:normalize=0,volume='max(1-t*1.1,0)':eval=frame,volume=2.8"],
 "riser":  ["-f","lavfi","-i","anoisesrc=d=1.6:c=pink:a=0.8","-f","lavfi","-i","aevalsrc=exprs='sin(2*PI*t*(90+220*t))*min(t*0.8\\,1)*0.5':d=1.6",
            "-filter_complex","[0]lowpass=f=2200,volume='min(t*0.75,1)':eval=frame[a];[a][1]amix=inputs=2:normalize=0,afade=t=out:st=1.35:d=0.25,volume=1.2"],
 "success":["-f","lavfi","-i","sine=frequency=262:duration=1.3","-f","lavfi","-i","sine=frequency=392:duration=1.3",
            "-filter_complex","[0][1]amix=inputs=2:normalize=0,volume='min(t*4,1)*max(1-(t-0.45)*1.4,0)':eval=frame,volume=1.6"],
})
print("all packs done")
