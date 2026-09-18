# -*- coding: utf-8 -*-
"""صوتُ ريلات تشغيلة ٧٣ — مؤثراتٌ فقط بلا كلام (§12).

أزمانُ المؤثرات تخرج من `run73_reels` نفسه (`reel73_<slug>_sfx.json`) فهي
مثبّتةٌ على لحظات الحدث البصري لا مقدَّرةً بالأذن: الفيديو هو المرجع
والمؤثّرُ يتبعه. والماستر `loudnorm I=-16` لأن طبقةً بلا كلامٍ تُسمع أعلى
من طبقةٍ فيها صوتٌ عند المستوى نفسه.

    python3 run73_post.py [slug ...]
"""
import json, os, subprocess, sys

import imageio_ffmpeg
from sfx_mux import mux

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
PACK = os.path.join(ROOT, "assets", "sfx_packs", "g_real")
DUR = 22.4


def post(slug):
    raw = os.path.join(HERE, f"reel73_{slug}_raw.mp4")
    ev = json.load(open(os.path.join(HERE, f"reel73_{slug}_sfx.json"),
                        encoding="utf-8"))
    out = os.path.join(HERE, f"reel73_{slug}_final.mp4")
    assert os.path.isfile(raw), f"لا فيديو خام لـ{slug}"
    assert ev, f"{slug}: لا مؤثرات — و§12 تمنع ريلاً صامتاً"
    tmp = os.path.join(HERE, f"_mix73_{slug}.mp4")
    mux(raw, [tuple(e) for e in ev], tmp, dur=DUR, lufs=-16, sfx_dir=PACK)

    # 🔒 `sfx_mux` يمرّر `-shortest`، وطبقةُ المؤثرات تنتهي بآخر مؤثرٍ
    # (هنا success عند 18.95 + 1.40 = 20.35ث) فيُقصّ الفيديو عندها ويضيع
    # ذيلُ نداء الفعل. فيُعاد الدمج: صورةٌ من الخام كاملةً وصوتٌ من
    # الماستر، بلا `-shortest` — فالطول طولُ الأطول لا الأقصر.
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    subprocess.run([ff, "-y", "-v", "error", "-i", raw, "-i", tmp,
                    "-map", "0:v", "-map", "1:a", "-c", "copy", out], check=True)
    os.remove(tmp)

    r = subprocess.run([ff, "-i", out], capture_output=True, text=True)
    dur = next(l for l in r.stderr.splitlines() if "Duration" in l)
    dur = dur.strip().split(",")[0].split()[1]
    hh, mm, ss = dur.split(":")
    secs = int(hh) * 3600 + int(mm) * 60 + float(ss)
    assert abs(secs - DUR) < 0.15, f"{slug}: الطول {secs} لا {DUR}"
    assert "Audio:" in r.stderr, f"{slug}: بلا طبقة صوت — و§12 تمنع ريلاً صامتاً"
    kb = os.path.getsize(out) // 1024
    print(f'{slug:<8} {len(ev)} مؤثراً · {secs}ث · {kb} ك.ب')
    return out


if __name__ == "__main__":
    for s in (sys.argv[1:] or ["nasib"]):
        post(s)
