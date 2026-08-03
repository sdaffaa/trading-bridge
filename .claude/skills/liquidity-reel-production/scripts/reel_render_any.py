# -*- coding: utf-8 -*-
# رندر أي ريل مبني على عقد #stage/__DUR/__setFrame: python3 reel_render_any.py in.html out.mp4
import os, sys, glob, subprocess, time
from playwright.sync_api import sync_playwright
import imageio_ffmpeg

HERE = os.path.dirname(os.path.abspath(__file__))
CHROME = glob.glob("/opt/pw-browsers/chromium-*/chrome-linux/chrome")[0]
FPS = 30

def render(html_in, mp4_out):
    fr = os.path.join(HERE, "frames_any")
    os.makedirs(fr, exist_ok=True)
    for f in glob.glob(os.path.join(fr, "*.jpg")): os.remove(f)
    t0 = time.time()
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROME, args=["--no-sandbox", "--force-color-profile=srgb", "--disable-lcd-text"])
        pg = b.new_page(viewport={"width": 1080, "height": 1920}, device_scale_factor=1)
        pg.goto("file://" + os.path.abspath(html_in)); pg.wait_for_timeout(500)
        DUR = pg.evaluate("()=>window.__DUR"); N = int(round(DUR * FPS))
        print("DUR", DUR, "frames", N)
        st = pg.query_selector("#stage")
        for i in range(N):
            pg.evaluate("(t)=>window.__setFrame(t)", i / FPS)
            st.screenshot(path=os.path.join(fr, f"f{i:05d}.jpg"), type="jpeg", quality=93)
        b.close()
    print(f"captured {N} frames in {time.time()-t0:.0f}s")
    exe = imageio_ffmpeg.get_ffmpeg_exe()
    r = subprocess.run([exe, "-y", "-v", "error", "-framerate", str(FPS), "-i", os.path.join(fr, "f%05d.jpg"),
                        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "19", "-preset", "medium",
                        "-movflags", "+faststart", mp4_out], capture_output=True, text=True)
    print("ffmpeg rc", r.returncode, r.stderr[-300:] if r.returncode else "")
    return mp4_out

if __name__ == "__main__":
    render(sys.argv[1], sys.argv[2])
