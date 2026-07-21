#!/usr/bin/env python3
# Build per-slide motion segments: Ken Burns zoom on slide + STATIC caption overlay.
import subprocess, os

FPS = 30
# durations per page (seconds). hook a bit longer.
DUR = {1:5.0, 2:4.4, 3:4.4, 4:4.4, 5:4.4, 6:4.4, 7:4.4, 8:4.4, 9:4.4, 10:5.2}

os.makedirs("segments", exist_ok=True)

for p in range(1, 11):
    dur = DUR[p]
    frames = int(round(dur * FPS))
    # alternate zoom direction for rhythm; add gentle vertical drift
    if p % 2 == 1:      # push in
        z = f"1.0+0.060*on/{frames}"
    else:               # pull out
        z = f"1.060-0.060*on/{frames}"
    # slight vertical drift (parallax feel)
    ydrift = f"ih/2-(ih/zoom/2)+{'-' if p%3==0 else ''}{18}*sin(on/{frames}*3.14159)"
    vf = (
        f"[0:v]scale=1350:2400,setsar=1,"
        f"zoompan=z='{z}':d={frames}:x='iw/2-(iw/zoom/2)':y='{ydrift}':"
        f"s=1080x1920:fps={FPS}[bg];"
        f"[bg][1:v]overlay=0:0:format=auto,format=yuv420p[v]"
    )
    out = f"segments/seg{p:02d}.mp4"
    cmd = [
        "ffmpeg", "-y",
        "-i", f"final/p{p:02d}.png",
        "-i", f"captions/cap{p:02d}.png",
        "-filter_complex", vf, "-map", "[v]",
        "-frames:v", str(frames),
        "-r", str(FPS), "-c:v", "libx264", "-preset", "veryfast",
        "-crf", "20", "-pix_fmt", "yuv420p", out,
    ]
    print(f"-> {out}  dur={dur}s frames={frames} {'push' if p%2 else 'pull'}")
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("FFMPEG ERROR:\n", r.stderr[-1500:]); raise SystemExit(1)

print("all segments built")
