# -*- coding: utf-8 -*-
"""نسختان صوتيتان أهدأ لكل ريل: «هادئة» و«صامتة».
سبب الإزعاج في النسخ السابقة ثلاثة أشياء عولجت هنا:
  1) كثرة المؤثرات (12–14 حدثاً) → خُفّضت إلى ثلاثة أحداث ناعمة فقط.
  2) عناصر معدنية حادة (impact_clean · granular_metal · riser · logo_sting)
     → استُبدلت بأنعم ما في الحزمة، وقُصّت الترددات العالية بمرشّح.
  3) سرير متوتر بمستوى مرتفع → سرير مؤسسي هادئ بثلث المستوى وبلا داكنق حاد.
الماستر عند ‎-16 LUFS‎ لا ‎-14‎: إنستقرام يرفع المنخفض ولا يخفض المرتفع.
"""
import os, subprocess, json, re, imageio_ffmpeg
from sfx_mux import mux

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
H = os.path.join(ROOT, "assets", "sfx_packs", "h_institutional")
MUSIC = os.path.join(ROOT, "assets", "music")
FF = imageio_ffmpeg.get_ffmpeg_exe()

# (اسم الملف الخام، المدة، أحداث ناعمة [(عنصر، زمن، كسب)])
JOBS = {
    "academic": dict(
        raw="reel_academic_raw.mp4", dur=22.0, out="reel_academic",
        ev=[("ui_tick", 3.35, -20), ("impact_soft", 10.75, -15), ("ui_tick", 20.05, -19)]),
    "fast": dict(
        raw="reel_be_fast_raw.mp4", dur=12.4, out="reel_be_fast",
        ev=[("impact_soft", 0.30, -14), ("impact_soft", 6.60, -11), ("ui_tick", 10.05, -19)]),
}

def soft_bed(out, dur):
    """سرير هادئ: مستوى منخفض + قصّ الحواد العالية + دخول وخروج طويلان."""
    af = (f"atrim=0:{dur},"
          "lowpass=f=4200,"            # يزيل الحدّة المعدنية
          "highpass=f=45,"             # يزيل الهدير تحت السمع
          "volume=0.26,"
          f"afade=t=in:d=1.6,afade=t=out:st={dur-2.0}:d=2.0")
    subprocess.run([FF, "-y", "-v", "error", "-i",
                    os.path.join(MUSIC, "bed_institutional.wav"), "-af", af, out], check=True)
    return out[:-4]

def master(src, dst, dur, lufs=-16.0):
    m = subprocess.run([FF, "-hide_banner", "-i", src, "-af",
                        f"loudnorm=I={lufs}:TP=-2:LRA=11:print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True)
    d = json.loads(re.search(r"\{[^{}]*input_i[^{}]*\}", m.stderr, re.S).group(0))
    af = (f"loudnorm=I={lufs}:TP=-2:LRA=11:measured_I={d['input_i']}:measured_TP={d['input_tp']}:"
          f"measured_LRA={d['input_lra']}:measured_thresh={d['input_thresh']}:"
          f"offset={d['target_offset']}:linear=false,lowpass=f=15000,aresample=48000")
    subprocess.run([FF, "-y", "-v", "error", "-i", src, "-c:v", "copy", "-af", af,
                    "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", "-t", str(dur),
                    "-movflags", "+faststart", dst], check=True)
    # تصحيح مقيس (loudnorm داخل filter_complex يقصّر عن هدفه)
    for _ in range(2):
        mm = subprocess.run([FF, "-hide_banner", "-i", dst, "-af",
                             "loudnorm=print_format=json", "-f", "null", "-"],
                            capture_output=True, text=True)
        dd = json.loads(re.search(r"\{[^{}]*input_i[^{}]*\}", mm.stderr, re.S).group(0))
        li, tp = float(dd["input_i"]), float(dd["input_tp"])
        delta = lufs - li
        if abs(delta) < 0.4 or tp + delta > -1.5:
            return li, tp
        fix = dst + ".fix.mp4"
        subprocess.run([FF, "-y", "-v", "error", "-i", dst, "-c:v", "copy",
                        "-af", f"volume={delta:.2f}dB", "-c:a", "aac", "-b:a", "192k",
                        "-ar", "48000", "-ac", "2", "-movflags", "+faststart", fix], check=True)
        os.replace(fix, dst)
    return li, tp

if __name__ == "__main__":
    for key, j in JOBS.items():
        raw = os.path.join(HERE, j["raw"])
        if not os.path.isfile(raw):
            print("skip (لا يوجد خام):", j["raw"]); continue
        # ── نسخة هادئة ──
        b = soft_bed(os.path.join(HERE, f"bed18_{key}.wav"), j["dur"])
        tmp = os.path.join(HERE, f"_q_{key}.mp4")
        quiet = os.path.join(HERE, j["out"] + "_quiet.mp4")
        mux(raw, list(j["ev"]) + [(b, 0.0, -6)], tmp, dur=j["dur"], lufs=-16, sfx_dir=H)
        li, tp = master(tmp, quiet, j["dur"])
        os.remove(tmp)
        print(f'{key} هادئة: {os.path.basename(quiet)} | {li:.1f} LUFS · TP {tp:.1f}')
        # ── نسخة صامتة ──
        silent = os.path.join(HERE, j["out"] + "_silent.mp4")
        subprocess.run([FF, "-y", "-v", "error", "-i", raw, "-c:v", "copy", "-an",
                        "-movflags", "+faststart", silent], check=True)
        print(f'{key} صامتة: {os.path.basename(silent)}')
