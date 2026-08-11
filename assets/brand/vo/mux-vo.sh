#!/usr/bin/env bash
# Master the six MSA voiceover segments, place each at its beat, and mux the
# result into reel-entry-gate.mp4.
#
#   ./mux-vo.sh  [dir-with-s1..s6.mp3]  [video.mp4]  [out.mp4]
#
# The segments are generated per beat rather than as one take on purpose: the
# video's chart holds and caption changes are on a fixed clock, and a single
# continuous read drifts away from them within a few seconds.
#
# Placement is sequential with a floor, not fixed: segment N starts at its beat
# time, or right after segment N-1 finishes if that is later. A read that runs
# half a second long therefore pushes the next line instead of talking over it,
# and the schedule re-converges at the next beat with slack in it.
set -euo pipefail

SRC="${1:-$(dirname "$0")}"
VID="${2:-$(dirname "$0")/../reel-entry-gate.mp4}"
OUT="${3:-$(dirname "$0")/../reel-entry-gate-vo.mp4}"

FF="${FFMPEG:-$(command -v ffmpeg || true)}"
[ -x "$FF" ] || FF=/usr/local/lib/python3.11/dist-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2
[ -x "$FF" ] || { echo "ffmpeg not found — set FFMPEG=/path/to/ffmpeg"; exit 1; }

# Beat start times from the caption track in reel-entry-gate.html.
BEATS=(0.10 5.70 9.50 14.55 23.00 27.90)
GAP=0.12            # breath between two segments that had to be pushed together
SEAM=32.80          # the loop seam: nothing should still be speaking past it

for i in 1 2 3 4 5 6; do
  [ -f "$SRC/s$i.mp3" ] || { echo "missing $SRC/s$i.mp3"; exit 1; }
done

dur() {
  "$FF" -hide_banner -i "$1" 2>&1 | sed -n 's/.*Duration: \([0-9:.]*\).*/\1/p' \
  | awk -F: '{printf "%.2f", $1*3600+$2*60+$3}'
}

echo "── placement ───────────────────────────────────────────────"
OFFS=(); prev_end=0
for i in 0 1 2 3 4 5; do
  n=$((i+1)); d=$(dur "$SRC/s$n.mp3"); beat=${BEATS[$i]}
  start=$(awk -v b="$beat" -v p="$prev_end" -v g="$GAP" \
          'BEGIN{s=(p+g>b)?p+g:b; printf "%.2f", s}')
  end=$(awk -v s="$start" -v d="$d" 'BEGIN{printf "%.2f", s+d}')
  push=$(awk -v s="$start" -v b="$beat" 'BEGIN{printf "%.2f", s-b}')
  note=$(awk -v p="$push" 'BEGIN{print (p>0.01)?"pushed +"p"s":"on its beat"}')
  printf "  s%s  %5.2fs   %6.2f → %6.2f   (beat %5.2f, %s)\n" "$n" "$d" "$start" "$end" "$beat" "$note"
  OFFS+=("$start"); prev_end=$end
done

late=$(awk -v e="$prev_end" -v s="$SEAM" 'BEGIN{print (e>s)?"yes":"no"}')
echo
if [ "$late" = "yes" ]; then
  echo "  Speech runs past the loop seam at ${SEAM}s (ends at ${prev_end}s)."
  echo "  Shorten a line's TEXT and regenerate it — do not speed the read up."
  echo "  A rushed hook costs more than a late one."
else
  echo "  Speech ends at ${prev_end}s, inside the ${SEAM}s seam."
fi
echo

# Per segment: trim the silence at both ends, even out the dynamics, delay to
# its slot. Loudness is set once on the finished mix so the segments keep their
# relative weight instead of each being pushed to the same level.
FILTER=""
for i in 0 1 2 3 4 5; do
  n=$((i+1)); ms=$(awk -v o="${OFFS[$i]}" 'BEGIN{printf "%d", o*1000}')
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
echo "wrote $SRC/vo-master.wav  (-14 LUFS)"

# -shortest so the audio can never extend the video past its loop seam.
"$FF" -y -loglevel error -i "$VID" -i "$SRC/vo-master.wav" \
  -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -shortest "$OUT"
echo "wrote $OUT"
"$FF" -hide_banner -i "$OUT" 2>&1 | sed -n 's/.*\(Duration: [0-9:.]*\).*/  \1/p;s/.*\(Stream #0:[01].*\)/  \1/p'
