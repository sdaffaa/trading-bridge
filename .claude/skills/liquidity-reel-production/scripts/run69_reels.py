# -*- coding: utf-8 -*-
"""ريلا تشغيلة ٦٩ — نافذتان حقيقيتان، ≤22.4 ثانية، مؤثرات فقط (§12).

    trend → النافذة ٧٠ · الكاردانو/دولار ساعة — الخطُّ على الفتائل لا الأجسام
    hissa → النافذة ٧١ · الإيثيريوم/دولار ١٥د — شمعةٌ صنعت ثلثَي الحركة

    python3 run69_reels.py [slug ...]
"""
import json, os, sys

from reel_build import INK, TEAL, TEAL_D, RED, htext
from reel_sfx_kit import (build_reel, line_el, zone_el, checkmark,
                          set_canvas, set_pad)
import tv_chart
import run69_charts as X
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
DEC = {"ADA-USD": 4, "ETH-USD": 2}
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


# ═════════ «ترند» — الخطُّ يُرسم على الفتائل ═════════
def markup_trend(r):
    W = r["w"]; x, y, slot = geo(W)
    a, b, brk = X.D_A, X.D_B, X.D_BRK
    ex = [
        sline(x(a) - slot * .5, y(X.D_WICK(a - .5)),
              x(b) + slot * .5, y(X.D_WICK(b + .5)), TEAL_D, 3.0, None, "chan"),
        '<g id="dots" opacity="0">' + "".join(
            f'<circle cx="{x(i):.1f}" cy="{y(W[i]["h"]):.1f}" r="8" '
            f'fill="#F2EEE7" stroke="{TEAL_D}" stroke-width="3"/>'
            for i in X.D_TW)
        + htext(x((a + b) / 2), y(max(c["h"] for c in W[a:b + 1])) - 22,
                f'{ar(len(X.D_TW))} لمسات · ولا تجاوز', TEAL_D, 27) + '</g>',
        '<g id="body" opacity="0">'
        f'<line x1="{x(a) - slot * .5:.1f}" y1="{y(X.D_BODY(a - .5)):.1f}" '
        f'x2="{x(b) + slot * .5:.1f}" y2="{y(X.D_BODY(b + .5)):.1f}" '
        f'stroke="{INK}" stroke-width="2.4" stroke-dasharray="9 7"/>'
        f'<rect x="{x(X.D_VB[0]) - slot * .5:.1f}" y="{y(W[X.D_VB[0]]["h"]):.1f}" '
        f'width="{slot:.1f}" '
        f'height="{y(W[X.D_VB[0]]["l"]) - y(W[X.D_VB[0]]["h"]):.1f}" '
        f'fill="{RED}" opacity="0.18"/>'
        + htext(x(X.D_VB[0]) + slot * 5.0, y(W[X.D_VB[0]]["h"]) - 16,
                f'الأجسام {ar(len(X.D_TB))} ومعها تجاوز', RED, 25) + '</g>',
        sline(x(b) + slot * .5, y(X.D_WICK(b + .5)),
              x(brk) + slot * .5, y(X.D_WICK(brk + .5)), TEAL_D, 2.2, "8 6", "ext"),
        '<g id="brk" opacity="0">'
        f'<rect x="{x(brk) - slot * .5:.1f}" y="{y(W[brk]["h"]):.1f}" '
        f'width="{slot:.1f}" height="{y(W[brk]["l"]) - y(W[brk]["h"]):.1f}" '
        f'fill="{TEAL}" opacity="0.20"/>'
        + htext(x(brk) - slot * 5.2, y(W[brk]["l"]) + 40,
                "أول إغلاقٍ فوقه", TEAL_D, 26) + '</g>',
        checkmark(x(X.D_N - 2), y(max(c["h"] for c in W[brk:])) - 48, id="ck"),
    ]
    marks = [("chan", 4.4, 5.4, "draw"), ("dots", 6.4, 7.0, "pop"),
             ("body", 9.4, 10.0, "pop"), ("ext", 12.4, 13.2, "draw"),
             ("brk", 15.4, 16.0, "pop"), ("ck", 18.4, 18.8, "pop")]
    full = ["dots", "body", "brk", "ck"]
    sfx = [("whoosh", 0.35, -3), ("whoosh", 4.45, -4), ("pop", 6.45, -4),
           ("tick", 8.2, -7), ("pop", 9.45, -3), ("whoosh", 12.45, -4),
           ("impact", 15.45, -1), ("tick", 17.2, -7), ("success", 18.45, -2)]
    return ("".join(ex), marks, full, ["chan", "ext"], (15.4, 15.9), sfx, 28)


# ═════════ «حصة» — شمعةٌ صنعت ثلثَي الحركة ═════════
def markup_hissa(r):
    W = r["w"]; x, y, slot = geo(W)
    R = CVW - PR
    dp = DEC[r["sym"]]
    big, lo, top = X.S_BIG[0], X.S_LO, X.S_TOP
    ex = [
        line_el(x(lo) - slot * .5, y(W[lo]["l"]), R, y(W[lo]["l"]), INK, 2.4, id="lo"),
        '<g id="lv" opacity="0">'
        f'<line x1="{x(0) - slot * .5:.1f}" y1="{y(X.S_ENT):.1f}" x2="{R:.1f}" '
        f'y2="{y(X.S_ENT):.1f}" stroke="{INK}" stroke-width="2.6"/>'
        f'<line x1="{x(0) - slot * .5:.1f}" y1="{y(X.S_TGT):.1f}" x2="{R:.1f}" '
        f'y2="{y(X.S_TGT):.1f}" stroke="{TEAL_D}" stroke-width="2.4" '
        f'stroke-dasharray="9 7"/>'
        + htext(x(5), y(X.S_TGT) - 14, f'الهدف {X.S_TGT:,.{dp}f}', TEAL_D, 25)
        + htext(x(5), y(X.S_ENT) + 36, f'الدخول {X.S_ENT:,.{dp}f}', INK, 25) + '</g>',
        '<g id="ent" opacity="0">'
        f'<rect x="{x(X.S_IR) - slot * .5:.1f}" y="{y(W[X.S_IR]["h"]):.1f}" '
        f'width="{slot:.1f}" '
        f'height="{y(W[X.S_IR]["l"]) - y(W[X.S_IR]["h"]):.1f}" '
        f'fill="{TEAL}" opacity="0.18"/></g>',
        '<g id="big" opacity="0">'
        f'<rect x="{x(big) - slot * .48:.1f}" y="{y(W[big]["h"]) - 3:.1f}" '
        f'width="{slot * .96:.1f}" '
        f'height="{y(W[big]["l"]) - y(W[big]["h"]) + 6:.1f}" '
        f'fill="none" stroke="{TEAL_D}" stroke-width="3.4"/>'
        + htext(x(big) - slot * 5.0, y(W[big]["l"]) + 42,
                f'{ar(round(X.S_SHARE * 100))}٪ من الحركة', TEAL_D, 27) + '</g>',
        zone_el("move", x(lo) - slot * .5, y(W[top]["h"]),
                x(top) + slot * .5, y(W[lo]["l"]),
                htext(x((lo + top) / 2), y(W[top]["h"]) - 18,
                      f'{ar(X.S_BARS)} شمعة · المدى {X.S_MOVE:.2f}', INK, 26)),
        checkmark(x(X.S_HIT), y(W[X.S_HIT]["h"]) - 48, id="ck"),
    ]
    marks = [("lo", 3.4, 4.2, "draw"), ("lv", 6.4, 7.2, "pop"),
             ("ent", 10.0, 10.6, "pop"), ("big", 12.4, 13.0, "pop"),
             ("move", 15.4, 16.4, "zone"), ("ck", 18.4, 18.8, "pop")]
    full = ["lv", "ent", "big", "move", "ck"]
    sfx = [("whoosh", 0.35, -3), ("tick", 3.45, -7), ("pop", 6.45, -4),
           ("tick", 9.0, -7), ("pop", 10.05, -3), ("impact", 12.45, 0),
           ("whoosh", 15.45, -4), ("tick", 17.4, -7), ("success", 18.45, -2)]
    return ("".join(ex), marks, full, ["lo"], (12.4, 12.9), sfx, 22)


MARKUP = {"trend": markup_trend, "hissa": markup_hissa}

BASE_CSS = """
.hl{top:118px;left:56px;right:56px;line-height:1.16}
.hl b{display:block;font-size:50px;font-weight:900;line-height:1.14;letter-spacing:-.6px}
.hl .why{display:block;margin-top:10px;font-size:29px;font-weight:600;color:#6B7C84}
#chartclip{top:360px;left:0}
#chip{display:none} #endlogo{display:none} #res{display:none}
#cta{top:1712px} #cta .k{font-size:44px;padding:9px 30px} #cta .s{margin-top:8px;font-size:26px}
#edu{bottom:22px;font-size:19px;opacity:.5}
"""


def load(slug):
    with open(os.path.join(CONT, f"run69_{slug}.json"), encoding="utf-8") as f:
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
    out = os.path.join(HERE, f"reel69_{slug}.html")
    n = build_reel(cfg, out)
    print(f'{slug:<8} ريل {DUR}s · بيتات {len(beats)} · ماركب {len(marks)} · '
          f'نافذة {r["slug"]} · {n} bytes')
    return out, sfx


if __name__ == "__main__":
    for s in (sys.argv[1:] or list(MARKUP)):
        out, sfx = build(s)
        json.dump(sfx, open(os.path.join(HERE, f"reel69_{s}_sfx.json"), "w"),
                  ensure_ascii=False)
