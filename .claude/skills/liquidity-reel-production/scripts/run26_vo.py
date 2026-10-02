# -*- coding: utf-8 -*-
"""تعليق صوتي بالفصحى فوق ريلات تشغيلة ٢٦، مع خفض طبقة المؤثرات تحته.

الأسطر وأزمانها تُقرأ من reel26_*_vo.json الذي يكتبه run26_reels — النص
المنطوق هو نص الكابشن حرفياً، فلا ينقسم انتباه المشاهد بين ما يقرأ وما يسمع.

⚠ الشبكة: هذا الملف يحتاج الوصول إلى api.elevenlabs.io. في جلسة كتابته كان
   المضيف مرفوضاً بسياسة البيئة (403 من بوابة الخروج)، فلم يُنفَّذ. يُشغَّل
   كما هو في بيئة يُسمح فيها بالمضيف. المفتاح يُقرأ من .env غير المتعقَّب
   ولا يُمرَّر إلى أي أداة خارجية.

الاستخدام:
    python3 run26_vo.py            # الثلاثة
    python3 run26_vo.py sweep      # واحد
"""
import json, os, re, subprocess, sys
import imageio_ffmpeg

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
FF = imageio_ffmpeg.get_ffmpeg_exe()
VOD = os.path.join(HERE, "vo")

# صوت عربي فصيح، ذكر، نبرة مؤسسية. يُضبط بعد سماع عيّنات.
VOICE_ID = os.environ.get("LS_VOICE_ID", "")
MODEL = "eleven_multilingual_v2"
SETTINGS = dict(stability=0.55, similarity_boost=0.75, style=0.15,
                use_speaker_boost=True)


def key_from_env():
    p = os.path.join(ROOT, ".env")
    for line in open(p, encoding="utf-8"):
        if line.startswith("ELEVENLABS_API_KEY="):
            return line.split("=", 1)[1].strip()
    raise SystemExit("لا مفتاح في .env")


def tts(text, out):
    """يولّد سطراً واحداً. يرفع خطأً واضحاً بدل تمرير ملف صامت."""
    import urllib.request, urllib.error
    if not VOICE_ID:
        raise SystemExit("عيّن LS_VOICE_ID لصوت عربي فصيح قبل التشغيل")
    body = json.dumps(dict(text=text, model_id=MODEL, voice_settings=SETTINGS)).encode()
    req = urllib.request.Request(
        f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}",
        data=body, headers={"xi-api-key": key_from_env(),
                            "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=120) as r, open(out, "wb") as f:
            f.write(r.read())
    except urllib.error.URLError as e:
        raise SystemExit(f"تعذّر الوصول إلى api.elevenlabs.io: {e}\n"
                         "إن كان الرفض من بوابة الخروج فالمضيف غير مسموح في هذه البيئة.")
    return out


def dur(path):
    r = subprocess.run([FF, "-hide_banner", "-i", path], capture_output=True, text=True).stderr
    h, m, s = re.search(r"Duration: (\d+):(\d+):([\d.]+)", r).groups()
    return int(h) * 3600 + int(m) * 60 + float(s)


def build_track(key, total):
    """مسار تعليق واحد: كل سطر عند زمنه، والباقي صمت."""
    v = json.load(open(os.path.join(HERE, f"reel26_{key}_vo.json"), encoding="utf-8"))
    os.makedirs(VOD, exist_ok=True)
    parts, ins, f = [], [], []
    for n, ln in enumerate(v["lines"]):
        p = os.path.join(VOD, f"{key}_{n:02d}.mp3")
        if not os.path.isfile(p):
            tts(ln["text"], p)
        d = dur(p)
        if d > ln["slot"] + 0.45:
            print(f'  ⚠ السطر {n} يطول عن نافذته: {d:.2f}s مقابل {ln["slot"]:.2f}s '
                  f'— «{ln["text"]}»')
        ins += ["-i", p]
        ms = int(round(ln["t"] * 1000))
        f.append(f"[{len(parts)+1}:a]adelay={ms}|{ms},volume=1.0[v{len(parts)}]")
        parts.append(f"[v{len(parts)}]")
    fc = (";".join(f) + ";" + "".join(parts) +
          f"amix=inputs={len(parts)}:normalize=0,apad=whole_dur={total},"
          f"atrim=0:{total},highpass=f=90,acompressor=threshold=-18dB:ratio=3:attack=8:release=180[vo]")
    out = os.path.join(VOD, f"{key}_vo.wav")
    subprocess.run([FF, "-y", "-v", "error", "-f", "lavfi", "-t", str(total),
                    "-i", "anullsrc=r=48000:cl=stereo"] + ins +
                   ["-filter_complex", fc, "-map", "[vo]", out], check=True)
    return out


def mix(key, suf="_light"):
    """يخفض طبقة المؤثرات تحت الكلام بالضغط الجانبي — لا يقطعها."""
    src = os.path.join(HERE, f"reel26_{key}{suf}_final.mp4")   # الصورة + المؤثرات
    if not os.path.isfile(src):
        print("لا يوجد:", os.path.basename(src)); return
    total = dur(src)
    vo = build_track(key, total)
    out = os.path.join(HERE, f"reel26_{key}{suf}_vo.mp4")
    fc = ("[0:a]highpass=f=35[sfx];"
          "[1:a]asplit=2[vo1][sc];"
          "[sfx][sc]sidechaincompress=threshold=0.035:ratio=8:attack=12:release=320[duck];"
          "[duck][vo1]amix=inputs=2:normalize=0,"
          "loudnorm=I=-16:TP=-2:LRA=11,aresample=48000[a]")
    subprocess.run([FF, "-y", "-v", "error", "-i", src, "-i", vo,
                    "-filter_complex", fc, "-map", "0:v", "-map", "[a]",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                    "-movflags", "+faststart", out], check=True)
    print(f"{key:<6} {os.path.basename(out)}")


if __name__ == "__main__":
    for k in (sys.argv[1:] or ["sweep", "fvg", "bos"]):
        mix(k)
