#!/usr/bin/env python3
# Generate a cinematic ambient bed (offline, ffmpeg synthesis) sized to video length.
import subprocess, sys

LENGTH = float(sys.argv[1]) if len(sys.argv) > 1 else 39.0

# Layered pad: root+fifth+octave drones (Am feel: A2 110, C3 130.8, E3 164.8),
# slow tremolo, a soft heartbeat sub pulse, gentle high shimmer, big reverb.
fc = (
    # --- warm drone chord (A minor-ish) ---
    f"sine=frequency=110:sample_rate=44100,volume=0.16[a1];"
    f"sine=frequency=164.81:sample_rate=44100,volume=0.11[a2];"
    f"sine=frequency=220:sample_rate=44100,volume=0.08[a3];"
    f"sine=frequency=130.81:sample_rate=44100,volume=0.06[a4];"
    f"[a1][a2][a3][a4]amix=inputs=4:normalize=0[chord];"
    f"[chord]tremolo=f=0.12:d=0.5,lowpass=f=900[pad];"
    # --- soft heartbeat sub pulse every ~2.4s ---
    f"sine=frequency=55:sample_rate=44100[sub0];"
    f"[sub0]tremolo=f=0.42:d=0.9,lowpass=f=120,volume=0.22[sub];"
    # --- airy shimmer high ---
    f"sine=frequency=1318.5:sample_rate=44100,volume=0.014[s1];"
    f"sine=frequency=1760:sample_rate=44100,volume=0.010[s2];"
    f"[s1][s2]amix=inputs=2:normalize=0,tremolo=f=0.19:d=0.7,highpass=f=800[shim];"
    # --- combine ---
    f"[pad][sub][shim]amix=inputs=3:normalize=0[mix];"
    f"[mix]aecho=0.8:0.9:600|900:0.35|0.25,"
    f"aecho=0.7:0.8:1400:0.2,"
    f"highpass=f=45,lowpass=f=6500,"
    f"loudnorm=I=-18:TP=-2:LRA=8,"
    f"afade=t=in:st=0:d=2.5,afade=t=out:st={LENGTH-3.0}:d=3.0[out]"
)
cmd = [
    "ffmpeg", "-y",
    "-f", "lavfi", "-t", f"{LENGTH}", "-i", "anullsrc=r=44100:cl=stereo",
    "-filter_complex", fc, "-map", "[out]",
    "-t", f"{LENGTH}", "-c:a", "pcm_s16le", "music/bed.wav",
]
# anullsrc unused input just to have a base; filters are all sources -> drop map of 0
cmd = [
    "ffmpeg", "-y",
    "-filter_complex", fc, "-map", "[out]",
    "-t", f"{LENGTH}", "-c:a", "pcm_s16le", "music/bed.wav",
]
r = subprocess.run(cmd, capture_output=True, text=True)
if r.returncode != 0:
    print(r.stderr[-1800:]); raise SystemExit(1)
print(f"music/bed.wav built ({LENGTH:.2f}s)")
