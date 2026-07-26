"""
Render 660 frames (22.0s @ 30fps) and encode to 1080x1920 H.264/AAC MP4.
Frames are streamed straight into ffmpeg (imageio-ffmpeg's libx264 build);
audio.wav is muxed as AAC. Verifies the loop seam on the exported file.
"""
import subprocess, sys, os, time
import numpy as np
import imageio_ffmpeg
import scenes
from engine import W,H,FPS

HERE=os.path.dirname(os.path.abspath(__file__))
OUT=os.path.join(HERE,"..","out","liquidity_high_stop.mp4")
os.makedirs(os.path.dirname(OUT),exist_ok=True)
AUDIO=os.path.join(HERE,"audio.wav")
FFMPEG=imageio_ffmpeg.get_ffmpeg_exe()
DUR=22.0; NFR=int(round(DUR*FPS))

cmd=[FFMPEG,"-y",
     "-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-",
     "-i",AUDIO,
     "-c:v","libx264","-preset","medium","-crf","18","-pix_fmt","yuv420p",
     "-profile:v","high","-level","4.0",
     "-c:a","aac","-b:a","192k","-ar","48000",
     "-movflags","+faststart","-shortest",OUT]

print(f"rendering {NFR} frames -> {OUT}")
t0=time.time()
proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,
                      stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
first=last=None
try:
    for n in range(NFR):
        t=n/FPS
        im=scenes.frame(t).convert("RGB")
        if im.size!=(W,H): im=im.resize((W,H))
        arr=np.asarray(im,dtype=np.uint8)
        if n==0: first=arr.copy()
        if n==NFR-1: last=arr.copy()
        proc.stdin.write(arr.tobytes())
        if n% 60==0:
            print(f"  frame {n:3d}/{NFR}  t={t:5.2f}s  ({time.time()-t0:5.1f}s)")
    proc.stdin.close()
except BrokenPipeError:
    print("FFMPEG ERR:\n",proc.stderr.read().decode()[-2000:]); sys.exit(1)
rc=proc.wait()
err=proc.stderr.read().decode()
if rc!=0:
    print("FFMPEG failed:\n",err[-2500:]); sys.exit(1)
print(f"encoded in {time.time()-t0:.1f}s")

# loop-seam check: background continuity (exclude caption band) between frame0 & lastframe
if first is not None and last is not None:
    band=slice(0,1050)   # above the caption zone -> chart/background only
    d=np.abs(first[band].astype(int)-last[band].astype(int)).mean()
    print(f"loop-seam background delta (chart region): {d:.2f} / 255  "
          f"({'seam OK' if d<14 else 'seam JUMP - review'})")
print("done:",OUT, f"{os.path.getsize(OUT)/1e6:.2f} MB")
