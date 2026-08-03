# -*- coding: utf-8 -*-
# دمج طبقة المؤثرات الصوتية مع ريل (§12 — مؤثرات فقط، بدون كلام)
# الاستخدام:
#   from sfx_mux import mux
#   mux("reel.mp4", [("whoosh", 0.4), ("tick", 1.2), ("riser", 12.0), ("impact", 13.3),
#                    ("success", 17.9), ("pop", 20.2)], "reel_final.mp4", dur=22.2)
# كل حدث: (اسم المؤثر من assets/sfx بدون الامتداد، زمن البداية بالثواني، [اختياري] gain dB)
import os, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
SFX = os.path.normpath(os.path.join(HERE, "..", "..", "..", "..", "assets", "sfx"))

def _ff():
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()

def mux(video_in, events, video_out, dur=None, lufs=-16):
    """يبني طبقة صوت من المؤثرات على أزمانها، يعمل ماستر loudnorm، ويدمجها مع الفيديو (نسخ الفيديو)."""
    ff = _ff()
    ins, fparts, labels = [], [], []
    for i, ev in enumerate(events):
        name, t = ev[0], ev[1]
        gain = ev[2] if len(ev) > 2 else 0.0
        path = os.path.join(SFX, name + ".wav")
        if not os.path.isfile(path):
            raise FileNotFoundError(path)
        ins += ["-i", path]
        d = int(round(t * 1000))
        fparts.append(f"[{i+1}:a]adelay={d}|{d},volume={10**(gain/20):.4f}[s{i}]")
        labels.append(f"[s{i}]")
    n = len(events)
    trim = f",atrim=0:{dur}" if dur else ""
    fc = (";".join(fparts) + ";" + "".join(labels) +
          f"amix=inputs={n}:normalize=0,apad{trim},"
          f"loudnorm=I={lufs}:TP=-1.5:LRA=11[aout]")
    cmd = [ff, "-y", "-v", "error", "-i", video_in] + ins + [
        "-filter_complex", fc, "-map", "0:v", "-map", "[aout]",
        "-c:v", "copy", "-c:a", "aac", "-b:a", "128k", "-shortest", video_out]
    subprocess.run(cmd, check=True)
    return video_out

if __name__ == "__main__":
    print("SFX dir:", SFX, "->", sorted(os.listdir(SFX)))
