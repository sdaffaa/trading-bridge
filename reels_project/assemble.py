#!/usr/bin/env python3
# xfade-concat the 10 segments, add music, export final reels mp4.
import subprocess, os

FPS = 30
T = 0.5  # crossfade duration
DUR = {1:5.0, 2:4.4, 3:4.4, 4:4.4, 5:4.4, 6:4.4, 7:4.4, 8:4.4, 9:4.4, 10:5.2}
durs = [DUR[p] for p in range(1, 11)]

inputs = []
for p in range(1, 11):
    inputs += ["-i", f"segments/seg{p:02d}.mp4"]

# build xfade chain
parts = []
prev = "0:v"
run_len = durs[0]
for k in range(1, 10):
    offset = run_len - T
    out = f"x{k}"
    trans = "fade"
    parts.append(f"[{prev}][{k}:v]xfade=transition={trans}:duration={T}:offset={offset:.3f}[{out}]")
    prev = out
    run_len = run_len + durs[k] - T

final_len = run_len
vfilter = ";".join(parts)
# add subtle global fade in/out on video
vfilter += f";[{prev}]fade=t=in:st=0:d=0.6,fade=t=out:st={final_len-0.7:.3f}:d=0.7[vout]"

fc = vfilter
cmd = ["ffmpeg", "-y"] + inputs + [
    "-i", "music/bed.wav",
    "-filter_complex", fc,
    "-map", "[vout]", "-map", "10:a",
    "-c:v", "libx264", "-preset", "medium", "-crf", "19",
    "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
    "-movflags", "+faststart", "-shortest",
    "output/reels_final.mp4",
]
print(f"final length ~{final_len:.2f}s")
print("running ffmpeg assemble...")
r = subprocess.run(cmd, capture_output=True, text=True)
if r.returncode != 0:
    print(r.stderr[-2000:]); raise SystemExit(1)
print("output/reels_final.mp4 built")
# write length for music step
with open("music/_len.txt", "w") as f:
    f.write(f"{final_len:.3f}")
