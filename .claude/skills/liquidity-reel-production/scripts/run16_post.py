# -*- coding: utf-8 -*-
"""مكساج ريل «التعادل — النسخة السريعة» (12.4ث) — نظام الصوت H.
الموسيقى تبدأ من الفريم صفر، وتنخفض قبل ضربة الوقف وعند الـCTA.
لا يتكرر أي مؤثر أكثر من مرتين (شرط البريف §9).
"""
import os, subprocess, imageio_ffmpeg
from sfx_mux import mux

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
H = os.path.join(ROOT, "assets", "sfx_packs", "h_institutional")
MUSIC = os.path.join(ROOT, "assets", "music")
FF = imageio_ffmpeg.get_ffmpeg_exe()

DUR, T_HIT, T_CTA = 12.4, 6.60, 10.0

def bed(src, out, dur, ti, tc):
    af = (f"atrim=0:{dur},"
          f"volume='1-0.55*exp(-pow(t-{ti},2)/0.09)':eval=frame,"    # انخفاض حول الضربة
          f"volume='1-0.45/(1+exp(-7*(t-{tc})))':eval=frame,"        # هبوط عند الـCTA
          f"volume=0.62,afade=t=in:d=0.35,afade=t=out:st={dur-0.9}:d=0.9")
    subprocess.run([FF, "-y", "-v", "error", "-i", os.path.join(MUSIC, src + ".wav"),
                    "-af", af, out], check=True)
    return out[:-4]

if __name__ == "__main__":
    raw = os.path.join(HERE, "reel_be_fast_raw.mp4")
    b = bed("bed_institutional_tense", os.path.join(HERE, "bed16_be.wav"), DUR, T_HIT, T_CTA)
    EV = [
        ("granular_air",  0.00, -12),   # م1: نَفَس الاقتراب
        ("impact_soft",   0.30, -4),    # لمس خط التعادل + ظهور X
        ("ui_scan",       0.56, -9),    # سناب باتجاه الانطلاق
        ("reverse_swell", 1.26, -5),    # م2: الرجوع البصري
        ("ui_tick",       2.16, -10),   # م3: خط الدخول
        ("ui_click",      3.48, -4),    # م4: قفل الوقف على التعادل
        ("riser_short",   5.70, -6),    # م5: بناء التوتر داخل التصحيح
        ("impact_clean",  6.60,  0),    # م6: ضرب الوقف — أقوى لحظة
        ("granular_metal", 6.68, -11),
        ("impact_deep",   7.32, -5),    # الانطلاق
        ("ui_confirm",    7.90, -7),    # علامة الصح
        ("perc_filtered", 8.30, -9),    # م7: الخلاصة
        ("ui_click",     10.05, -5),    # م8: CTA
        ("logo_sting",   10.85, -3),
        (b, 0.0, -9),
    ]
    tmp = os.path.join(HERE, "_be_mux.mp4")
    out = os.path.join(HERE, "reel_be_fast_final.mp4")
    mux(raw, EV, tmp, dur=DUR, lufs=-14, sfx_dir=H)
    # ماستر نهائي: loudnorm بمرحلتين (الأحادية المرحلة تخطئ بـ2–3 LU) + ليميتر
    # ثم فرض 48kHz ستيريو — شرط البريف §12
    import json as _j, re as _re
    m = subprocess.run([FF, "-hide_banner", "-i", tmp, "-af",
                        "loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json",
                        "-f", "null", "-"], capture_output=True, text=True)
    d = _j.loads(_re.search(r"\{[^{}]*input_i[^{}]*\}", m.stderr, _re.S).group(0))
    af = (f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={d['input_i']}:"
          f"measured_TP={d['input_tp']}:measured_LRA={d['input_lra']}:"
          f"measured_thresh={d['input_thresh']}:offset={d['target_offset']}:linear=false,"
          f"aresample=48000")   # بلا ليميتر إضافي: كان يخنق الذروات ويهبط بالجهارة 2 LU
    subprocess.run([FF, "-y", "-v", "error", "-i", tmp, "-c:v", "copy",
                    "-af", af, "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", "-t", str(DUR),
                    "-movflags", "+faststart", out], check=True)
    os.remove(tmp)
    # تصحيح ختامي: loudnorm داخل filter_complex يقصّر عن هدفه بنحو 2 LU،
    # فتُقاس النتيجة فعلياً ويُضاف الفارق كسبًا صريحاً ما دامت الذروة تحتمله
    for _ in range(2):
        mm = subprocess.run([FF, "-hide_banner", "-i", out, "-af",
                             "loudnorm=print_format=json", "-f", "null", "-"],
                            capture_output=True, text=True)
        dd = _j.loads(_re.search(r"\{[^{}]*input_i[^{}]*\}", mm.stderr, _re.S).group(0))
        li, tp = float(dd["input_i"]), float(dd["input_tp"])
        delta = -14.0 - li
        if abs(delta) < 0.4 or tp + delta > -1.2:
            break
        fix = os.path.join(HERE, "_be_fix.mp4")
        subprocess.run([FF, "-y", "-v", "error", "-i", out, "-c:v", "copy",
                        "-af", f"volume={delta:.2f}dB", "-c:a", "aac", "-b:a", "192k",
                        "-ar", "48000", "-ac", "2", "-movflags", "+faststart", fix], check=True)
        os.replace(fix, out)
    print("be-fast FINAL OK ->", out, f"| {li:.1f} LUFS -> target -14")
