# -*- coding: utf-8 -*-
"""طبقة صوت الريل: سرير هادئ + مؤثرات على أزمانها — بلا كلام.

§12 يفرض «مؤثرات فقط»؛ وبريف فهد يطلب سريراً Minimal Ambient بلا كلمات
فوقها. `bed_institutional` مسجّل ٤٠ث بلا غناء، فيُقصّ إلى مدّة الريل عند
مستوى منخفض حتى تبقى النقرات مقروءة، ثم يُعمل ماستر loudnorm على −14 LUFS
وذروة −1 dBTP كما يطلب البريف.
"""
import os, subprocess, sys
import imageio_ffmpeg

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", "..", "..", ".."))
SFX = os.path.join(ROOT, "assets", "sfx")
MUS = os.path.join(ROOT, "assets", "music")
DUR = 23.5

# (المؤثر، الزمن، الكسب dB) — نقرة عند كل مستوى، وِش عند كل حركة كاميرا،
# تِك عند تحقّق كل هدف، وإمباكت واحد عند الهوك.
EV = [("impact", 0.04, -3), ("whoosh", 1.70, -8),
      ("pop", 4.84, -6), ("pop", 5.44, -6), ("pop", 6.04, -6),
      ("whoosh", 6.42, -9), ("pop", 7.58, -8),
      ("whoosh", 9.28, -9), ("pop", 9.44, -8),
      ("pop", 12.12, -6), ("pop", 13.98, -5),
      ("whoosh", 15.72, -9), ("tick", 16.98, -1), ("tick", 18.08, -1),
      ("whoosh", 19.28, -10), ("pop", 20.05, -7)]


def build(frames_glob, video_out):
    """يُرمَّز من إطارات PNG مباشرةً — مرّة واحدة، بلا جيل ثانٍ من الضياع."""
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    ins = ["-framerate", "30", "-i", frames_glob,
           "-i", os.path.join(MUS, "bed_institutional.wav")]
    parts = [f"[1:a]atrim=0:{DUR},asetpts=N/SR/TB,volume=-19dB,"
             f"afade=t=in:st=0:d=0.8,afade=t=out:st={DUR-1.2}:d=1.2[bed]"]
    labels = ["[bed]"]
    for i, (n, t, g) in enumerate(EV):
        p = os.path.join(SFX, n + ".wav")
        assert os.path.isfile(p), p
        ins += ["-i", p]
        d = int(round(t * 1000))
        parts.append(f"[{i+2}:a]aresample=48000,adelay={d}|{d},"
                     f"volume={g}dB[s{i}]")
        labels.append(f"[s{i}]")
    fc = (";".join(parts) + ";" + "".join(labels) +
          f"amix=inputs={len(labels)}:normalize=0,"
          f"apad=whole_dur={DUR},atrim=0:{DUR},"
          f"loudnorm=I=-14:TP=-1.2:LRA=9[aout]")
    cmd = [ff, "-y", "-v", "error"] + ins + [
        "-filter_complex", fc, "-map", "0:v", "-map", "[aout]",
        "-c:v", "libx264", "-profile:v", "high", "-level", "4.2",
        "-pix_fmt", "yuv420p", "-crf", "11", "-maxrate", "20M",
        "-bufsize", "40M", "-preset", "slow",
        "-x264-params", "qpmin=0:aq-mode=3",
        "-color_primaries", "bt709", "-color_trc", "bt709",
        "-colorspace", "bt709", "-r", "30",
        "-c:a", "aac", "-ar", "48000", "-b:a", "256k",
        "-movflags", "+faststart", video_out]
    subprocess.run(cmd, check=True)
    return video_out


if __name__ == "__main__":
    print(build(sys.argv[1], sys.argv[2]))
