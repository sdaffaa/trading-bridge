# -*- coding: utf-8 -*-
import os, glob, subprocess, time
from playwright.sync_api import sync_playwright
import imageio_ffmpeg
HERE=os.path.dirname(os.path.abspath(__file__))
CHROME="/opt/pw-browsers/chromium-1194/chrome-linux/chrome"
FR=os.path.join(HERE,"frames"); os.makedirs(FR,exist_ok=True)
for f in glob.glob(os.path.join(FR,"*.jpg")): os.remove(f)
FPS=30
t0=time.time()
with sync_playwright() as p:
    b=p.chromium.launch(executable_path=CHROME,args=["--no-sandbox","--force-color-profile=srgb","--disable-lcd-text"])
    pg=b.new_page(viewport={"width":1080,"height":1920},device_scale_factor=1)
    pg.goto("file://"+os.path.join(HERE,"reel_sheet.html")); pg.wait_for_timeout(500)
    DUR=pg.evaluate("()=>window.__DUR"); N=int(round(DUR*FPS)); print("DUR",DUR,"frames",N)
    st=pg.query_selector("#stage")
    for i in range(N):
        t=i/FPS
        pg.evaluate("(t)=>window.__setFrame(t)",t)
        st.screenshot(path=os.path.join(FR,f"f{i:05d}.jpg"),type="jpeg",quality=93)
        if i%60==0: print(f"frame {i}/{N}  {time.time()-t0:.0f}s")
    b.close()
print(f"captured {N} frames in {time.time()-t0:.0f}s")
exe=imageio_ffmpeg.get_ffmpeg_exe()
out=os.path.join(HERE,"reel_sheet.mp4")
cmd=[exe,"-y","-framerate",str(FPS),"-i",os.path.join(FR,"f%05d.jpg"),
     "-c:v","libx264","-pix_fmt","yuv420p","-crf","19","-preset","medium",
     "-movflags","+faststart",out]
r=subprocess.run(cmd,capture_output=True,text=True)
print("ffmpeg rc",r.returncode)
if r.returncode!=0: print(r.stderr[-1500:])
print("SIZE",os.path.getsize(out)//1024,"KB")
# cleanup frames to save disk
for f in glob.glob(os.path.join(FR,"*.jpg")): os.remove(f)
print("done", out)
