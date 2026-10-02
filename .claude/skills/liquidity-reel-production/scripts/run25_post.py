# -*- coding: utf-8 -*-
"""طبقة صوت هادئة لريلات تشغيلة ٢٥ (§12 — مؤثرات بلا كلام).

المسار نفسه المعتمد في run18_quiet: ثلاثة مؤثرات ناعمة فقط + سرير مؤسسي
مقصوص الحواد العالية بثلث المستوى، والماستر عند ‎-16 LUFS‎ لا ‎-14‎
لأن إنستقرام يرفع المنخفض ولا يخفض المرتفع.

المؤثرات مثبّتة على أحداث الريل نفسها لا على إيقاع عشوائي:
  الشرط (رسم المستوى) · الدخول (رسم خط الدخول) · تحقق الهدف (علامة الصحّ)
"""
import os, re, json, subprocess, imageio_ffmpeg
from sfx_mux import mux

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
H = os.path.join(ROOT, "assets", "sfx_packs", "h_institutional")
MUSIC = os.path.join(ROOT, "assets", "music")
FF = imageio_ffmpeg.get_ffmpeg_exe()
DUR = 19.4

# (زمن رسم المستوى، زمن خط الدخول، زمن علامة الصحّ) لكل نموذج
BEATS = {"sweep": (2.90, 9.90, 15.90),
         "fvg":   (2.90, 10.40, 15.90),
         "bos":   (2.90, 10.40, 16.00)}

def soft_bed(out, dur):
    af = (f"atrim=0:{dur},lowpass=f=4200,highpass=f=45,volume=0.26,"
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
    for _ in range(2):        # loudnorm داخل filter_complex يقصّر عن هدفه فيُقاس ويُصحّح
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
    import sys
    for key in (sys.argv[1:] or list(BEATS)):
        raw = os.path.join(HERE, f"reel25_{key}_raw.mp4")
        if not os.path.isfile(raw):
            print("تخطٍّ (لا يوجد خام):", os.path.basename(raw)); continue
        t_lvl, t_ent, t_ck = BEATS[key]
        bed = soft_bed(os.path.join(HERE, f"bed25_{key}.wav"), DUR)
        ev = [("ui_tick", t_lvl, -20), ("impact_soft", t_ent, -15),
              ("ui_confirm", t_ck, -18), (bed, 0.0, -6)]
        tmp = os.path.join(HERE, f"_q25_{key}.mp4")
        out = os.path.join(HERE, f"reel25_{key}_final.mp4")
        mux(raw, ev, tmp, dur=DUR, lufs=-16, sfx_dir=H)
        li, tp = master(tmp, out, DUR)
        os.remove(tmp); os.remove(bed + ".wav")
        print(f"{key:<6} {os.path.basename(out)} | {li:.1f} LUFS · TP {tp:.1f}")
