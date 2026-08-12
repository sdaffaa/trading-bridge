#!/usr/bin/env bash
# Encode a frame sequence to the Liquidity State reel spec: 1080x1920, 30fps CFR, H.264 High,
# yuv420p, Rec.709, faststart, silent. Produces a spec-master (~16 Mbps CBR) and a small web copy (CRF 14).
# Usage: encode.sh <frames_dir> <out_basename_without_ext> [fps]
# ffmpeg: uses `ffmpeg` on PATH, else the imageio-ffmpeg static build (pip install imageio-ffmpeg).
set -euo pipefail
FRAMES="${1:?frames dir}"; OUT="${2:?out basename}"; FPS="${3:-30}"
if command -v ffmpeg >/dev/null 2>&1; then FF=ffmpeg
else FF=$(python3 -c "import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())"); fi
common=(-hide_banner -loglevel error -framerate "$FPS" -i "$FRAMES/%04d.png"
  -c:v libx264 -profile:v high -level 4.2 -pix_fmt yuv420p -r "$FPS"
  -color_primaries bt709 -color_trc bt709 -colorspace bt709 -movflags +faststart)
# spec master (CBR ~16 Mbps to satisfy 15-20 Mbps requirement even for flat vector content)
"$FF" -y "${common[@]}" -b:v 16M -maxrate 16M -minrate 16M -bufsize 8M \
  -x264-params "nal-hrd=cbr:keyint=$((FPS*2)):min-keyint=$FPS:force-cfr=1" "${OUT}.mp4"
# web copy (visually identical, small enough for chat upload)
"$FF" -y "${common[@]}" -crf 14 -maxrate 20M -bufsize 20M \
  -x264-params "keyint=$((FPS*2)):min-keyint=$FPS" "${OUT}_web.mp4"
echo "wrote ${OUT}.mp4 (master) and ${OUT}_web.mp4 (web)"
