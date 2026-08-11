#!/usr/bin/env bash
# Master the six MSA voiceover segments, place each at its beat, and mux the
# result into reel-entry-gate.mp4.
#
#   ./mux-vo.sh  [dir-with-s1..s6.mp3]  [video.mp4]  [out.mp4]
#
# The segments are generated per beat rather than as one take on purpose: the
# video's chart holds and caption changes are on a fixed clock, and a single
# continuous read drifts away from them within a few seconds. Each segment is
# placed at the exact second its beat starts, so the voice cannot slide out of
# sync with the words on screen no matter how the read is paced.
set -euo pipefail

SRC="${1:-$(dirname "$0")}"
VID="${2:-$(dirname "$0")/../reel-entry-gate.mp4}"
OUT="${3:-$(dirname "$0")/../reel-entry-gate-vo.mp4}"

FF="${FFMPEG:-$(command -v ffmpeg || true)}"
[ -x "$FF" ] || FF=/usr/local/lib/python3.11/dist-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2
[ -x "$FF" ] || { echo "ffmpeg not found — set FFMPEG=/path/to/ffmpeg"; exit 1; }

# Beat start times, in seconds, from the caption track in reel-entry-gate.html.
# Index i holds the start of segment i+1.
OFFSETS=(0.10 5.70 9.50 14.55 23.00 27.90)
# What each segment has room for before the next one begins. The last is the
# gap to the loop seam at 32.8s.
SLOTS=(5.60 3.80 5.05 8.45 4.90 4.90)

for i in 1 2 3 4 5 6; do
  [ -f "$SRC/s$i.mp3" ] || { echo "missing $SRC/s$i.mp3"; exit 1; }
done

dur() { "$FF" -v error -i "$1" -f null - 2>&1 >/dev/null;
        "$FF" -hide_banner -i "$1" 2>&1 | sed -n 's/.*Duration: \([0-9:.]*\).*/\1/p' \
        | awk -F: '{printf "%.2f", $1*3600+$2*60+$3}'; }

echo "── segment fit ─────────────────────────────────────────────"
over=0
for i in 0 1 2 3 4 5; do
  n=$((i+1)); d=$(dur "$SRC/s$n.mp3"); slot=${SLOTS[$i]}
  fit=$(awk -v d="$d" -v s="$slot" 'BEGIN{print (d<=s)?"ok":"OVER"}')
  printf "  s%s  %5.2fs  slot %5.2fs  %s\n" "$n" "$d" "$slot" "$fit"
  [ "$fit" = "OVER" ] && over=1
done
if [ "$over" = 1 ]; then
  echo
  echo "  One or more segments run past their slot and will overlap the next."
  echo "  Shorten that line's text and regenerate it, rather than speeding the"
  echo "  read up — a rushed hook is worse than a late one."
fi
echo

# Per segment: trim leading/trailing silence, even out the dynamics, then delay
# it to its beat. Loudness is set once on the finished mix, not per segment, so
# the segments keep their relative weight.
FILTER=""
for i in 0 1 2 3 4 5; do
  n=$((i+1)); ms=$(awk -v o="${OFFSETS[$i]}" 'BEGIN{printf "%d", o*1000}')
  FILTER+="[$i:a]silenceremove=start_periods=1:start_threshold=-45dB,"
  FILTER+="areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse,"
  FILTER+="acompressor=threshold=-18dB:ratio=3:attack=8:release=120,"
  FILTER+="adelay=${ms}|${ms}[v$n];"
done
FILTER+="[v1][v2][v3][v4][v5][v6]amix=inputs=6:duration=longest:normalize=0,"
FILTER+="loudnorm=I=-14:TP=-1.2:LRA=9[vo]"

"$FF" -y -loglevel error \
  -i "$SRC/s1.mp3" -i "$SRC/s2.mp3" -i "$SRC/s3.mp3" \
  -i "$SRC/s4.mp3" -i "$SRC/s5.mp3" -i "$SRC/s6.mp3" \
  -filter_complex "$FILTER" -map "[vo]" -ar 48000 -ac 2 "$SRC/vo-master.wav"
echo "wrote $SRC/vo-master.wav"

# -shortest so the audio cannot extend the video past its loop seam.
"$FF" -y -loglevel error -i "$VID" -i "$SRC/vo-master.wav" \
  -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -shortest "$OUT"
echo "wrote $OUT"
"$FF" -hide_banner -i "$OUT" 2>&1 | sed -n 's/^  \(Duration\|  Stream\).*/&/p'
