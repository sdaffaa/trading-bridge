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
DUR = 23.2

# (المؤثر، الزمن، الكسب dB) — نقرة عند كل مستوى، وِش عند كل حركة كاميرا،
# تِك عند تحقّق كل هدف، وإمباكت واحد عند الهوك.
EV = [("impact", 0.04, -3), ("whoosh", 1.95, -8),
      ("pop", 3.88, -7), ("pop", 4.58, -6),          # حدّ الجلسة ثم خطّ الـVWAP
      ("pop", 5.78, -7), ("pop", 6.58, -7),          # الباند الأول ثم الثاني
      ("pop", 8.98, -6), ("whoosh", 9.55, -9),       # الامتداد ثم دخول الكاميرا
      ("tick", 11.08, -2),                            # الذروة
      ("pop", 12.12, -7), ("pop", 13.12, -5),         # متوسط الحجم ثم الضوء
      ("whoosh", 15.85, -9), ("tick", 17.18, -1),     # الرجوع للقيمة
      ("whoosh", 18.95, -10), ("pop", 19.65, -7)]


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
        "-shortest", "-movflags", "+faststart", video_out]
    subprocess.run(cmd, check=True)
    return video_out


if __name__ == "__main__":
    print(build(sys.argv[1], sys.argv[2]))
