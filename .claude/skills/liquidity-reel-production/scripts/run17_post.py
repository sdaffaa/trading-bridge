# -*- coding: utf-8 -*-
"""مكساج الريل التعليمي الأكاديمي (22ث) — صوت هادئ يخدم الفهم لا الإثارة.
لا ضربات قوية ولا رايزر درامي: نقرات واجهة خفيفة عند كل خطوة، وضربة ناعمة
واحدة عند الخروج، وسرير موسيقي منخفض ثابت.
"""
import os, subprocess, imageio_ffmpeg
from sfx_mux import mux

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
H = os.path.join(ROOT, "assets", "sfx_packs", "h_institutional")
MUSIC = os.path.join(ROOT, "assets", "music")
FF = imageio_ffmpeg.get_ffmpeg_exe()

DUR, T_EXIT, T_CTA = 22.0, 10.75, 20.0

def bed(src, out, dur, ti, tc):
    af = (f"aloop=loop=2:size=48000*40,atrim=0:{dur},"
          f"volume='1-0.34*exp(-pow(t-{ti},2)/0.12)':eval=frame,"
          f"volume='1-0.40/(1+exp(-6*(t-{tc})))':eval=frame,"
          f"volume=0.50,afade=t=in:d=1.0,afade=t=out:st={dur-1.4}:d=1.4")
    subprocess.run([FF, "-y", "-v", "error", "-i", os.path.join(MUSIC, src + ".wav"),
                    "-af", af, out], check=True)
    return out[:-4]

if __name__ == "__main__":
    raw = os.path.join(HERE, "reel_academic_raw.mp4")
    b = bed("bed_institutional", os.path.join(HERE, "bed17_ac.wav"), DUR, T_EXIT, T_CTA)
    EV = [
        ("ui_scan",       0.10, -12),   # م1: العنوان
        ("ui_tick",       2.85, -12),   # م2: لافتة «ملاحظة» + خط الدخول
        ("ui_click",      3.35, -9),
        ("ui_click",      7.15, -7),    # م3: قفل الوقف على الدخول
        ("ui_tick",      10.35, -11),   # م4: لافتة «تفسير»
        ("impact_soft",  10.75, -6),    # لحظة الخروج — الضربة الوحيدة
        ("granular_air", 11.40, -14),   # الاستمرار
        ("ui_tick",      14.62, -11),   # م5: لافتة «قاعدة»
        ("ui_confirm",   16.30, -8),    # علامة الصح
        ("perc_filtered", 18.20, -11),  # م6: الخلاصة
        ("ui_confirm",   20.05, -7),    # م7: CTA
        ("logo_sting",   20.90, -5),
        (b, 0.0, -8),
    ]
    tmp = os.path.join(HERE, "_ac_mux.mp4")
    out = os.path.join(HERE, "reel_academic_final.mp4")
    mux(raw, EV, tmp, dur=DUR, lufs=-14, sfx_dir=H)
    import json as _j, re as _re
    m = subprocess.run([FF, "-hide_banner", "-i", tmp, "-af",
                        "loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True)
    d = _j.loads(_re.search(r"\{[^{}]*input_i[^{}]*\}", m.stderr, _re.S).group(0))
    af = (f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={d['input_i']}:"
          f"measured_TP={d['input_tp']}:measured_LRA={d['input_lra']}:"
          f"measured_thresh={d['input_thresh']}:offset={d['target_offset']}:linear=false,"
          f"aresample=48000")
    subprocess.run([FF, "-y", "-v", "error", "-i", tmp, "-c:v", "copy", "-af", af,
                    "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", "-t", str(DUR),
                    "-movflags", "+faststart", out], check=True)
    os.remove(tmp)
    for _ in range(2):
        mm = subprocess.run([FF, "-hide_banner", "-i", out, "-af",
                             "loudnorm=print_format=json", "-f", "null", "-"],
                            capture_output=True, text=True)
        dd = _j.loads(_re.search(r"\{[^{}]*input_i[^{}]*\}", mm.stderr, _re.S).group(0))
        li, tp = float(dd["input_i"]), float(dd["input_tp"])
        delta = -14.0 - li
        if abs(delta) < 0.4 or tp + delta > -1.2:
            break
        fix = os.path.join(HERE, "_ac_fix.mp4")
        subprocess.run([FF, "-y", "-v", "error", "-i", out, "-c:v", "copy",
                        "-af", f"volume={delta:.2f}dB", "-c:a", "aac", "-b:a", "192k",
                        "-ar", "48000", "-ac", "2", "-movflags", "+faststart", fix], check=True)
        os.replace(fix, out)
    print("academic FINAL OK ->", out, f"| {li:.1f} LUFS")
