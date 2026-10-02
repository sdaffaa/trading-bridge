# -*- coding: utf-8 -*-
"""ريلا تشغيلة ٧٠ — نافذتان حقيقيتان، ≤22.4 ثانية، مؤثرات فقط (§12).

    muhla → النافذة ٧٠ · الكاردانو/دولار ساعة — كم شمعةً بين السحب والكسر؟

وهو الريلُ الوحيد: الوحدةُ الفنيةُ الثانية «تصفية» سلسلةٌ مولّدة، والقاعدة
المقفلة تمنع الريل عليها (`furniture` يطبع أرقامَ المحور و§11 البديلة تمنع
طبع سعرٍ على مثالٍ تخطيطي) — فتحوّلت كاروسيلاً وبيتاتُها في `reel_deferred`.

    python3 run70_reels.py [slug ...]
"""
import json, os, sys

from reel_build import INK, TEAL, TEAL_D, RED, htext
from reel_sfx_kit import (build_reel, line_el, zone_el, checkmark,
                          set_canvas, set_pad)
import tv_chart
import run70_charts as X
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
DEC = {"ADA-USD": 4}
tv_chart.set_theme("light")


def geo(W):
    lo = min(c["l"] for c in W); hi = max(c["h"] for c in W)
    pad = (hi - lo) * 0.08
    ymin, ymax = lo - pad * 1.7, hi + pad
    slot = PW / len(W)
    return (lambda i: PL + slot * i + slot / 2,
            lambda p: PT + (ymax - p) / (ymax - ymin) * PH, slot)


def sline(x1, y1, x2, y2, col, w=2.4, dash=None, id=""):
    """خطٌّ مائلٌ قابلٌ للرسم التدريجي — `line_el` يحمل `data-len`."""
    return line_el(x1, y1, x2, y2, col, w, dash, id)


# ═════════ «مهلة» — السحبُ يفتح البابَ والكسرُ هو الدخول ═════════
def markup_muhla(r):
    W = r["w"]; x, y, slot = geo(W)
    e = X.H_SLOW                              # أطولُ مهلة: ٨ شمعات
    f = X.H_FAST                              # أقصرُها: شمعةٌ واحدة
    dp = DEC[r["sym"]]
    lo = min(range(e["sw"], e["brk"] + 1), key=lambda k: W[k]["l"])
    ex = [
        line_el(x(0) - slot * .5, y(e["lvl"]), x(len(W) - 1) + slot * .5,
                y(e["lvl"]), INK, 3.0, None, "lvl"),
        '<g id="lvt" opacity="0">'
        + htext(x(11), y(e["lvl"]) + 64, f'قاعٌ سابق {e["lvl"]:,.{dp}f}', INK, 25)
        + '</g>',
        '<g id="sw" opacity="0">'
        f'<rect x="{x(e["sw"]) - slot * .48:.1f}" y="{y(W[e["sw"]]["h"]) - 3:.1f}" '
        f'width="{slot * .96:.1f}" '
        f'height="{y(W[e["sw"]]["l"]) - y(W[e["sw"]]["h"]) + 6:.1f}" '
        f'fill="none" stroke="{RED}" stroke-width="3.4"/>'
        + htext(x(e["sw"]) + slot * 6.2, y(e["lvl"]) + 142,
                'سحبٌ ثم إغلاقٌ فوق', RED, 27) + '</g>',
        line_el(x(e["ti"]) - slot * .5, y(e["top"]), x(len(W) - 1) + slot * .5,
                y(e["top"]), INK, 2.6, "9 7", "top"),
        '<g id="topt" opacity="0">'
        + htext(x(len(W) - 9), y(e["top"]) - 16,
                f'قمّةُ الهيكل {e["top"]:,.{dp}f}', INK, 25) + '</g>',
        zone_el("wait", x(e["sw"]) - slot * .5, y(W[e["sw"]]["c"]),
                x(e["brk"]) + slot * .5, y(W[lo]["l"]),
                htext(x((e["sw"] + e["brk"]) / 2), y(W[lo]["l"]) + 46,
                      f'{ar(e["gap"])} شمعات · ضدَّك {xr(e["adv"])} وسيطَ المدى',
                      RED, 26)),
        '<g id="brk" opacity="0">'
        f'<rect x="{x(e["brk"]) - slot * .48:.1f}" y="{y(W[e["brk"]]["h"]) - 3:.1f}" '
        f'width="{slot * .96:.1f}" '
        f'height="{y(W[e["brk"]]["l"]) - y(W[e["brk"]]["h"]) + 6:.1f}" '
        f'fill="none" stroke="{TEAL_D}" stroke-width="3.4"/>'
        + htext(x(e["brk"]) - slot * 3.2, y(W[e["brk"]]["h"]) - 26,
                'هني الكسر', TEAL_D, 27) + '</g>',
        '<g id="fast" opacity="0">'
        f'<rect x="{x(f["sw"]) - slot * .48:.1f}" y="{y(W[f["sw"]]["h"]) - 3:.1f}" '
        f'width="{slot * 1.96:.1f}" '
        f'height="{y(W[f["sw"]]["l"]) - y(W[f["sw"]]["h"]) + 6:.1f}" '
        f'fill="none" stroke="{TEAL}" stroke-width="3.0" stroke-dasharray="7 5"/>'
        + htext(x(f["sw"]) + slot * 4.0, y(W[f["sw"]]["h"]) - 30,
                f'{ar(len(X.H_ONE))} من {ar(len(X.H_DONE))} بشمعةٍ وحدة',
                TEAL_D, 26) + '</g>',
        checkmark(x(e["brk"]), y(W[e["brk"]]["h"]) - 52, id="ck"),
    ]
    marks = [("lvl", 2.6, 3.4, "draw"), ("lvt", 3.5, 4.0, "pop"),
             ("sw", 6.0, 6.6, "pop"), ("top", 8.4, 9.2, "draw"),
             ("topt", 9.3, 9.8, "pop"), ("wait", 12.0, 13.0, "zone"),
             ("fast", 15.2, 15.8, "pop"), ("brk", 17.6, 18.2, "pop"),
             ("ck", 18.9, 19.3, "pop")]
    full = ["lvt", "sw", "topt", "wait", "fast", "brk", "ck"]
    sfx = [("whoosh", 0.35, -3), ("tick", 2.65, -7), ("pop", 3.55, -4),
           ("impact", 6.05, -1), ("whoosh", 8.45, -4), ("pop", 9.35, -4),
           ("riser", 11.4, -6), ("tick", 12.05, -7), ("pop", 15.25, -4),
           ("impact", 17.65, 0), ("success", 18.95, -2)]
    return ("".join(ex), marks, full, ["lvl", "top"], (17.6, 18.1), sfx, 26)


MARKUP = {"muhla": markup_muhla}

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
    with open(os.path.join(CONT, f"run70_{slug}.json"), encoding="utf-8") as f:
        return json.load(f)


def build(slug):
    C = load(slug)
    assert C["window"] == X.REAL[slug], \
        f'{slug}: نافذة الملف {C["window"]} لا تطابق {X.REAL[slug]}'
    assert C.get("media") == "reel", f'{slug}: ملفّه يعلن {C.get("media")} لا ريلاً'
    r = X.WINS[slug]
    W = r["w"]
    ex, marks, full, drawset, flash, sfx, base = MARKUP[slug](r)
    beats = C["reel"]["beats"]
    assert beats[-1]["t"] < DUR - 2.6, "آخر بيت يتجاوز موضع نداء الفعل"
    txt = []
    for i, b in enumerate(beats):
        end = beats[i + 1]["t"] - 0.05 if i + 1 < len(beats) else DUR - 0.6
        sub = f'<span class="why">{b["sub"]}</span>' if b.get("sub") else ""
        txt.append((f"t{i+1}", b["t"], round(end, 2), f'<b>{b["title"]}</b>{sub}', 50, INK))

    span = DUR - 3.2
    story = [(j, round(0.15 + (j - base) * span / max(1, len(W) - base), 2))
             for j in range(base, len(W))]
    cam = []                                  # أثاثُ اللوحة داخل الطبقة المتحرّكة
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
        cam=cam,
    )
    out = os.path.join(HERE, f"reel70_{slug}.html")
    n = build_reel(cfg, out)
    print(f'{slug:<8} ريل {DUR}s · بيتات {len(beats)} · ماركب {len(marks)} · '
          f'نافذة {r["slug"]} · {n} bytes')
    return out, sfx


if __name__ == "__main__":
    for s in (sys.argv[1:] or list(MARKUP)):
        out, sfx = build(s)
        json.dump(sfx, open(os.path.join(HERE, f"reel70_{s}_sfx.json"), "w"),
                  ensure_ascii=False)
