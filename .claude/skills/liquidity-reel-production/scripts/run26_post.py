# -*- coding: utf-8 -*-
"""تصميم صوت تشغيلة ٢٦ — تغيير جذري عن الطبقة الهادئة السابقة.

ما تغيّر ولماذا:
  • السرير: من وسادة مؤسسية ساكنة (bed_institutional) إلى **نبض إيقاعي**
    (pulse_min) مقصوص الحواد. الوسادة الساكنة لا تعطي إحساس تقدّم، والريل
    التعليمي يحتاج نبضاً يمشي معه.
  • أساس منخفض مستمر (drone_low) بمستوى شبه معدوم يملأ الطيف تحت ٢٠٠Hz
    فلا يبدو الصوت رفيعاً على سمّاعة الهاتف.
  • كل خطوة تُعلَن بنقرة (ui_click) خفيفة: الأذن تتعلّم أن النقرة تعني
    «معلومة جديدة»، فتشدّ الانتباه بلا إزعاج.
  • لحظة التنفيذ صارت الذروة الصوتية: انتفاخ عكسي قبلها + هبوط جهير معها.
    قبلها كانت مجرد نقرة كباقي الأحداث، فضاعت أهم لحظة في الريل.
  • بلوغ الهدف: صعود قصير ثم تأكيد.

الأزمان تُقرأ من reel26_*_cues.json الذي يكتبه run26_reels — لا تُكتب هنا
فتنحرف عن الصورة عند أي تعديل في التوقيت.
"""
import json, os, re, subprocess, imageio_ffmpeg
from sfx_mux import mux
from run25_post import master, H

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
FF = imageio_ffmpeg.get_ffmpeg_exe()


def bed(out, dur, src="pulse_min.wav", vol=0.30, lp=5200, fi=1.2, fo=2.2):
    """سرير نابض: قصّ الحواد العالية يمنع الحدّة، والفيد يمنع القطع المفاجئ."""
    af = (f"aloop=loop=-1:size=2e9,atrim=0:{dur},lowpass=f={lp},highpass=f=38,"
          f"volume={vol},afade=t=in:d={fi},afade=t=out:st={dur - fo:.2f}:d={fo}")
    subprocess.run([FF, "-y", "-v", "error", "-i", os.path.join(H, src),
                    "-af", af, out], check=True)
    return out[:-4]


def sub(out, dur, vol=0.16):
    """أساس منخفض يملأ ما تحت ٢٠٠Hz — بلا هذا يبدو الصوت رفيعاً على الهاتف."""
    af = (f"aloop=loop=-1:size=2e9,atrim=0:{dur},lowpass=f=200,volume={vol},"
          f"afade=t=in:d=2.0,afade=t=out:st={dur - 2.5:.2f}:d=2.5")
    subprocess.run([FF, "-y", "-v", "error", "-i", os.path.join(H, "drone_low.wav"),
                    "-af", af, out], check=True)
    return out[:-4]


def events(c, b1, b2):
    """خريطة الأحداث: كل مؤثر مربوط بحدث بصري، بلا مؤثر يتيم."""
    ev = [(b1, 0.0, -7), (b2, 0.0, -9),
          ("impact_deep", c["hook"], -13)]                       # ضربة الهوك
    for k, t in enumerate(c["steps"]):                            # نقرة لكل خطوة
        ev.append(("ui_click", t, -25 if k else -23))
    ev += [("ui_scan", c["t_lvl"], -19),                          # رسم المستوى
           ("reverse_swell", max(0.0, c["t_box"] - 1.6), -16),    # ترقّب قبل التنفيذ
           ("sub_drop", c["t_box"], -11),                         # لحظة التنفيذ
           ("impact_clean", c["t_box"] + 0.05, -13),
           ("riser_short", max(0.0, c["t_ck"] - 1.0), -20),       # صعود نحو الهدف
           ("ui_confirm", c["t_ck"], -15)]                        # بلوغ الهدف
    return ev


if __name__ == "__main__":
    import sys
    SUF = os.environ.get("LS_SUF", "_light")
    for key in (sys.argv[1:] or ["sweep", "fvg", "bos"]):
        raw = os.path.join(HERE, f"reel26_{key}{SUF}_raw.mp4")
        cue = os.path.join(HERE, f"reel26_{key}_cues.json")
        if not (os.path.isfile(raw) and os.path.isfile(cue)):
            print("تخطٍّ:", os.path.basename(raw)); continue
        c = json.load(open(cue)); dur = c["dur"]
        b1 = bed(os.path.join(HERE, f"bed26_{key}.wav"), dur)
        b2 = sub(os.path.join(HERE, f"sub26_{key}.wav"), dur)
        tmp = os.path.join(HERE, f"_q26_{key}.mp4")
        out = os.path.join(HERE, f"reel26_{key}{SUF}_final.mp4")
        ev = events(c, b1, b2)
        mux(raw, ev, tmp, dur=dur, lufs=-16, sfx_dir=H)
        li, tp = master(tmp, out, dur)
        for f in (tmp, b1 + ".wav", b2 + ".wav"):
            os.remove(f)
        print(f"{key:<6} {os.path.basename(out)} | {len(ev)} حدثاً | {li:.1f} LUFS · TP {tp:.1f}")
