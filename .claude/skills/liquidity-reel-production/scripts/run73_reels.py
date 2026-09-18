# -*- coding: utf-8 -*-
"""ريلُ تشغيلة ٧٣ — نافذةٌ حقيقيةٌ واحدة، ≤22.4 ثانية، مؤثرات فقط (§12).

    nasib → النافذة ٧٨ · فول الصويا فريم ساعة — سبعُ شمعاتٍ حملن ثلثَ المدى

وريلٌ واحدٌ لا ريلان: بوابةُ `run32_desk.preflight` لم تُثبت نمطاً على
النافذة ٧٥، فبقيت «كثافة» كاروسيلاً ورُحّل ريلُها — والمزيجُ يُنقَص ولا
يُفبرَك ريلٌ ثانٍ من نافذةٍ لا تحمله (§8c).

والبيتات تأتي من ملفّ الوحدة بحقل `phase` لا `t` (قرار §11)، فالأزمانُ
هنا في `PHASE_T`.

ولا تذكرةَ أمرٍ فيه: الوحدةُ درسُ قياسٍ لا درسُ دخول، و§8d تمنع كتابة
دخولٍ ووقفٍ وR حين لا يقتضيه النموذج — ولا سعرَ مطبوعاً أصلاً، فالوحدةُ
وسيطُ المدى.

    python3 run73_reels.py [slug ...]
"""
import json, os, sys

from reel_build import INK, TEAL, TEAL_D, RED, CREAM, htext
from reel_sfx_kit import (build_reel, line_el, zone_el, checkmark,
                          set_canvas, set_pad)
import tv_chart
import run73_charts as X
from run58_charts import ar
from run59_charts import xr

HERE = os.path.dirname(os.path.abspath(__file__))
CONT = os.path.normpath(os.path.join(HERE, "..", "content"))
CVW, CVH = 1080, 1400
set_canvas(CVW, CVH)
set_pad(18, 122, 92, 66)
PL, PR, PT, PB = 18, 122, 92, 66
PW, PH = CVW - PL - PR, CVH - PT - PB
DUR = 22.4
DEC = {"ZS=F": 2}
#: الطورُ ووقتُه — ستّةُ بيتاتٍ تنتهي قبل نداء الفعل بثانيتين ونصف.
PHASE_T = {"result": 0.2, "structure": 3.4, "setup": 6.6,
           "wait": 10.0, "press": 13.6, "outcome": 17.0}
tv_chart.set_theme("light")


def geo(W):
    lo = min(c["l"] for c in W); hi = max(c["h"] for c in W)
    pad = (hi - lo) * 0.08
    ymin, ymax = lo - pad * 1.7, hi + pad
    slot = PW / len(W)
    return (lambda i: PL + slot * i + slot / 2,
            lambda p: PT + (ymax - p) / (ymax - ymin) * PH, slot)


def box(x0, y0, x1, y1, col, w=3.4):
    return (f'<rect x="{min(x0,x1):.1f}" y="{min(y0,y1):.1f}" '
            f'width="{abs(x1-x0):.1f}" height="{abs(y1-y0):.1f}" fill="none" '
            f'stroke="{col}" stroke-width="{w}"/>')


# ═════════ «نصيب» — سبعُ شمعاتٍ حملن ثلثَ المدى ═════════
def markup_nasib(r):
    W = r["w"]; x, y, slot = geo(W)
    n = len(W)
    rng = [c["h"] - c["l"] for c in W]
    hi = max(c["h"] for c in W); lo = min(c["l"] for c in W)
    # شمعةُ الوحدة: أقربُ مدىً إلى الوسيط والأقدمُ عند التعادل — تُبرَز
    # لتُرى الوحدةُ لا لتُقاس، فلا عتبةَ جديدةً هنا ولا رقمَ جديد.
    unit = min(range(n), key=lambda i: (abs(rng[i] - X.N_MED), i))
    imax, imin = X.N_SRT[0][1], X.N_SRT[-1][1]
    cx = PL + PW * 0.5
    ytop, ybot = y(hi) - 44, y(lo) + 68

    def cbox(i, col, w=3.4, pad=7):
        return box(x(i) - slot * .42, y(W[i]["h"]) - pad,
                   x(i) + slot * .42, y(W[i]["l"]) + pad, col, w)

    # الإطفاءُ بطبقةٍ كريميةٍ فوق ما ليس مقيساً — فالعينُ تقع على السبع.
    dimb = "".join(
        f'<rect x="{x(j) - slot * .48:.1f}" y="{y(W[j]["h"]):.1f}" '
        f'width="{slot * .96:.1f}" '
        f'height="{max(2.0, y(W[j]["l"]) - y(W[j]["h"])):.1f}" '
        f'fill="{CREAM}" opacity="0.66"/>'
        for j in range(n) if j not in X.N_BIG)

    ex = [
        # ١ · الوحدة
        f'<g id="unib" opacity="0">{cbox(unit, INK, 3.4)}</g>',
        '<g id="unit" opacity="0">'
        + htext(cx, ytop, 'شمعةٌ بطولِ الوسيط — وحدةُ القياس', INK, 30)
        + '</g>',
        # ٢ · أكبرُ ثلاث
        '<g id="topc" opacity="0">'
        + "".join(cbox(i, TEAL_D, 3.4) for i in X.N_TOP3) + '</g>',
        '<g id="topt" opacity="0">'
        + htext(cx, ybot, f'أكبرُ ثلاثٍ — {ar(round(X.N_S3 * 100))}٪ '
                          f'من مجموع المدى', TEAL_D, 30) + '</g>',
        # ٣ · الطرفان
        '<g id="mxc" opacity="0">'
        + cbox(imax, TEAL_D, 3.6) + cbox(imin, RED, 3.6) + '</g>',
        '<g id="mxt" opacity="0">'
        + htext(cx, ytop, f'الكبرى {xr(X.N_MAX)} الوسيط والصغرى '
                          f'{xr(X.N_MIN)}', INK, 29) + '</g>',
        # ٤ · السبعُ فوق الضِعف — وما عداها يُطفأ
        f'<g id="dimb" opacity="0">{dimb}</g>',
        '<g id="bigc" opacity="0">'
        + "".join(cbox(i, TEAL_D, 3.4) for i in X.N_BIG) + '</g>',
        '<g id="bigt" opacity="0">'
        + htext(cx, ybot, f'{ar(len(X.N_BIG))} فوق ضِعف الوسيط — '
                          f'{ar(round(X.N_SBIG * 100))}٪ من المدى',
                TEAL_D, 29) + '</g>',
        # ٥ · الممشيّةُ والمقطوعة: الخطّان هما عرضُ النافذة نفسُه
        line_el(PL, y(hi), PL + PW, y(hi), INK, 2.6, None, "spn0"),
        line_el(PL, y(lo), PL + PW, y(lo), INK, 2.6, None, "spn1"),
        '<g id="spnt" opacity="0">'
        + htext(cx, ytop, f'مشى {xr(X.N_WALK)} وانتقل {xr(X.N_SPAN)}',
                TEAL_D, 31) + '</g>',
        checkmark(x(n - 3), y(lo) + 74, id="ck"),
    ]
    # و`fullset` هو ما يُحرَّك أصلاً لا ما يبقى فقط: حلقةُ المحرّك تمرّ
    # على `FULLSET` وحدها، فالوسمُ خارجَها يبقى شفافاً أبداً (درس ٧٢).
    # وهنا **الأشكالُ تتناوب كالوسوم** خلافاً لريلات ٧٢: تلك تروي قصةً
    # واحدةً تتراكم، وهذه خمسةُ قياساتٍ مستقلّة على نافذةٍ واحدة — فبقاءُ
    # إطارِ الوحدة وإطارِ الأصغر تحت طبقة الإطفاء يزحم لوحةَ «السبع»
    # ويكذّبها (رُئي في إطار 14.6). فكلُّ قياسٍ يظهر وحدَه ثم يخلي اللوحة.
    marks = [("unib", 6.8, 7.4, "pop", 8.5, 0.4),
             ("unit", 6.8, 7.4, "pop", 8.5, 0.4),
             ("topc", 8.9, 9.5, "pop", 10.1, 0.4),
             ("topt", 8.9, 9.5, "pop", 10.1, 0.4),
             ("mxc", 10.4, 11.0, "pop", 13.4, 0.4),
             ("mxt", 10.4, 11.0, "pop", 13.4, 0.4),
             ("dimb", 13.9, 14.5, "pop", 16.8, 0.4),
             ("bigc", 13.9, 14.5, "pop", 16.8, 0.4),
             ("bigt", 13.9, 14.5, "pop", 16.8, 0.4),
             ("spn0", 17.3, 17.9, "draw"),
             ("spn1", 17.3, 17.9, "draw"),
             ("spnt", 17.9, 18.4, "pop"),
             ("ck", 20.3, 20.7, "pop")]
    full = ["unib", "unit", "topc", "topt", "mxc", "mxt",
            "dimb", "bigc", "bigt", "spnt", "ck"]
    draw = ["spn0", "spn1"]
    sfx = [("whoosh", 0.35, -3), ("tick", 2.60, -7), ("pop", 3.55, -5),
           ("whoosh", 6.70, -4), ("pop", 8.95, -4), ("pop", 10.45, -4),
           ("riser", 12.9, -6), ("impact", 13.95, -1), ("pop", 17.35, -4),
           ("success", 20.35, -2)]
    # والنافذةُ تكتمل قبل أوّلِ قياس: درسٌ يعدّ أربعاً وأربعين شمعةً لا
    # يصحّ أن يضع إطارَه على شمعةٍ لم تُكشف بعد — فالكشفُ في ٦.٢ ثانية.
    return ("".join(ex), marks, full, draw, (17.3, 17.8), sfx, 22, 6.2)


MARKUP = {"nasib": markup_nasib}


BASE_CSS = """
.hl{top:118px;left:56px;right:56px;line-height:1.16}
.hl b{display:block;font-size:50px;font-weight:900;line-height:1.14;letter-spacing:-.6px}
.hl .why{display:block;margin-top:10px;font-size:25px;font-weight:600;color:#6B7C84;white-space:normal;line-height:1.35}
#chartclip{top:360px;left:0}
#chip{display:none} #endlogo{display:none} #res{display:none}
#cta{top:1712px} #cta .k{font-size:44px;padding:9px 30px} #cta .s{margin-top:8px;font-size:26px}
#edu{bottom:22px;font-size:19px;opacity:.5}
"""


def load(slug):
    with open(os.path.join(CONT, f"run73_{slug}.json"), encoding="utf-8") as f:
        return json.load(f)


def build(slug):
    C = load(slug)
    assert C["window"] == X.REAL[slug], \
        f'{slug}: نافذة الملف {C["window"]} لا تطابق {X.REAL[slug]}'
    assert C.get("media") == "reel", f'{slug}: ملفّه يعلن {C.get("media")} لا ريلاً'
    r = X.WINS[slug]
    W = r["w"]
    ex, marks, full, drawset, flash, sfx, base, rev = MARKUP[slug](r)
    beats = sorted(C["reel"]["beats"], key=lambda b: PHASE_T[b["phase"]])
    assert len(beats) == len(PHASE_T), f'{slug}: {len(beats)} بيتاً لا {len(PHASE_T)}'
    assert PHASE_T[beats[-1]["phase"]] < DUR - 2.6, "آخر بيت يتجاوز موضع نداء الفعل"
    assert rev < min(m[1] for m in marks), "القياسُ يسبق اكتمالَ النافذة"
    txt = []
    for i, b in enumerate(beats):
        t0 = PHASE_T[b["phase"]]
        end = (PHASE_T[beats[i + 1]["phase"]] - 0.05
               if i + 1 < len(beats) else DUR - 0.6)
        sub = f'<span class="why">{b["sub"]}</span>' if b.get("sub") else ""
        txt.append((f"t{i+1}", t0, round(end, 2),
                    f'<b>{b["title"]}</b>{sub}', 50, INK))

    story = [(j, round(0.15 + (j - base) * rev / max(1, len(W) - base), 2))
             for j in range(base, len(W))]
    cfg = dict(
        w=W, dark=False, extra_css=BASE_CSS, extra_html="", grid=False,
        pre_svg=tv_chart.furniture(W, dec=DEC[r["sym"]], sym=r["sym"],
                                   tf=r["tf"], tlabels=[c["d"] for c in W]),
        lp_pill=True, lp_dec=DEC[r["sym"]], lp_col=tv_chart.T["PILL"],
        lp_txt=tv_chart.T["PILLTX"],
        base=base, openmax=len(W), open_t=[[base, 0.4]], story=story,
        extra_svg=ex, marks=marks, fullset=full, drawset=drawset, dom_marks=[],
        preview_a=0.0, preview_b=0.0, res_tease=False, sweep_op=0.0,
        txt=txt, chip="", res="",
        cta_k=f'اكتب «{C["car"]["cta"]["keyword"]}»', cta_s="ويصلك الدليل كاملاً",
        edu=f'{r["slug"]} — لغرض تعليمي',
        dur=DUR, res_t=999, cta_t=DUR - 2.6,
        flash=flash, flash_op=0.18, punch=(flash[0], flash[1], 0.05),
        cam=[],
    )
    out = os.path.join(HERE, f"reel73_{slug}.html")
    n = build_reel(cfg, out)
    print(f'{slug:<8} ريل {DUR}s · بيتات {len(beats)} · ماركب {len(marks)} · '
          f'نافذة {r["slug"]} · {n} bytes')
    return out, sfx


if __name__ == "__main__":
    for s in (sys.argv[1:] or list(MARKUP)):
        out, sfx = build(s)
        json.dump(sfx, open(os.path.join(HERE, f"reel73_{s}_sfx.json"), "w"),
                  ensure_ascii=False)
