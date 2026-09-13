# -*- coding: utf-8 -*-
"""ريلا تشغيلة ٦٨ — نافذتان حقيقيتان، ≤22.4 ثانية، مؤثرات فقط (§12).

    aaiq → النافذة ٦٨ · لايتكوين/دولار ساعة — ثلاثُ قممٍ بين الدخول والهدف
    habs → النافذة ٦٩ · دوجكوين/دولار ساعة — عرضُ المدى هو المسطرة

ودرسا اليوم كلاهما **عن مستويات الصفقة نفسها** (دخولٌ ووقفٌ وهدف)، فطبعُ
المستويات عليهما هو الدرسُ لا وعدٌ زائدٌ عليه — بخلاف ريل ٦٧ الذي كان
قياسَ بُعدٍ فمُنع من تذكرة الأمر.

    python3 run68_reels.py [slug ...]
"""
import json, os, sys

from reel_build import INK, TEAL, TEAL_D, RED, htext
from reel_sfx_kit import (build_reel, line_el, zone_el, checkmark,
                          set_canvas, set_pad)
import tv_chart
import run68_charts as X68
from run58_charts import ar
from run59_charts import xr

HERE = os.path.dirname(os.path.abspath(__file__))
CONT = os.path.normpath(os.path.join(HERE, "..", "content"))
CVW, CVH = 1080, 1400
set_canvas(CVW, CVH)
set_pad(18, 122, 92, 66)
PL, PR, PT, PB = 18, 122, 92, 66
PW, PH = CVW - PL - PR, CVH - PT - PB
DUR = 22.4                                   # سقف skip-rate (§12)
DEC = {"LTC-USD": 2, "DOGE-USD": 5}
tv_chart.set_theme("light")


def geo(W):
    lo = min(c["l"] for c in W); hi = max(c["h"] for c in W)
    pad = (hi - lo) * 0.08
    ymin, ymax = lo - pad * 1.7, hi + pad
    slot = PW / len(W)
    return (lambda i: PL + slot * i + slot / 2,
            lambda p: PT + (ymax - p) / (ymax - ymin) * PH, slot)


# ═════════ «عائق» — ثلاثُ قممٍ بين الدخول والهدف ═════════
def markup_aaiq(r):
    W = r["w"]; x, y, slot = geo(W)
    R = CVW - PR
    dp = DEC[r["sym"]]
    ent, tgt = X68.O_ENT, X68.O_TGT
    k1, h1 = X68.O_FIRST
    ex = [
        line_el(x(0) - slot * .5, y(ent), R, y(ent), INK, 2.4, id="ent"),
        line_el(x(0) - slot * .5, y(tgt), R, y(tgt), TEAL_D, 2.4, id="tgt"),
        f'<g id="tgtlbl" opacity="0">'
        + htext(x(6), y(tgt) - 16, f'الهدف {tgt:,.{dp}f}', TEAL_D, 26) + '</g>',
        # القمم الثلاث: خطوطٌ رفيعة ووسمٌ بوحدات المخاطرة
        '<g id="obs" opacity="0">' + "".join(
            f'<line x1="{x(k) - slot * .5:.1f}" y1="{y(h):.1f}" x2="{R:.1f}" '
            f'y2="{y(h):.1f}" stroke="{TEAL_D}" stroke-width="2" '
            f'stroke-dasharray="7 7"/>'
            + htext(x(k) + slot * 3.4, y(h) - 12, f'{xr(rr)} من المخاطرة', TEAL_D, 24)
            for (k, h), rr in zip(X68.O_OBS, X68.O_RS)) + '</g>',
        # أقربُ عائقٍ هو القمّةُ التي كُسرت أصلاً
        f'<g id="near" opacity="0">'
        f'<line x1="{x(0) - slot * .5:.1f}" y1="{y(h1):.1f}" x2="{R:.1f}" '
        f'y2="{y(h1):.1f}" stroke="{RED}" stroke-width="3.4"/>'
        f'<rect x="{x(k1) - slot * .5:.1f}" y="{y(W[k1]["h"]):.1f}" '
        f'width="{slot:.1f}" height="{y(W[k1]["l"]) - y(W[k1]["h"]):.1f}" '
        f'fill="{RED}" opacity="0.16"/>'
        + htext(x(k1) + slot * 4.6, y(h1) + 40, "هذي القمّة اللي كسرتها", RED, 26)
        + '</g>',
        zone_el("stall", x(X68.O_STALL[0]) - slot * .5,
                y(max(c["h"] for c in W[X68.O_STALL[0]:X68.O_STALL[-1] + 1])),
                x(X68.O_STALL[-1]) + slot * .5,
                y(min(c["l"] for c in W[X68.O_STALL[0]:X68.O_STALL[-1] + 1])),
                htext(x((X68.O_STALL[0] + X68.O_STALL[-1]) / 2),
                      y(min(c["l"] for c in W[X68.O_STALL[0]:X68.O_STALL[-1] + 1])) + 38,
                      f'{ar(len(X68.O_STALL))} شمعات على أول عائق', RED, 26),
                fill=RED, stroke=RED),
        checkmark(x(X68.O_HIT), y(W[X68.O_HIT]["h"]) - 48, id="ck"),
    ]
    # كلُّ وسمٍ يلي بيتَه بلحظة: بيتات الملفّ عند 0.0/3.2/6.2/9.2/12.2/15.2/18.2
    marks = [("ent", 1.6, 2.4, "draw"), ("tgt", 2.8, 3.6, "draw"),
             ("tgtlbl", 3.6, 4.0, "pop"), ("obs", 6.6, 7.8, "pop"),
             ("near", 9.6, 10.2, "pop"), ("stall", 15.6, 16.8, "zone"),
             ("ck", 18.6, 19.0, "pop")]
    full = ["tgtlbl", "obs", "near", "stall", "ck"]
    sfx = [("whoosh", 0.35, -3), ("tick", 1.65, -6), ("whoosh", 2.85, -4),
           ("pop", 3.65, -4), ("riser", 5.9, -3), ("pop", 6.7, -3),
           ("impact", 9.65, -1), ("whoosh", 15.65, -4), ("tick", 17.4, -7),
           ("success", 18.65, -2)]
    return ("".join(ex), marks, full, ["ent", "tgt"], (9.6, 10.1), sfx, 14)


# ═════════ «حبس» — عرضُ المدى هو المسطرة ═════════
def markup_habs(r):
    W = r["w"]; x, y, slot = geo(W)
    R = CVW - PR
    dp = DEC[r["sym"]]
    ca, cb, kb = X68.B_CA, X68.B_CB, X68.B_KB
    ex = [
        zone_el("box", x(ca) - slot * .5, y(X68.B_RT), x(cb) + slot * .5,
                y(X68.B_RB),
                htext(x((ca + cb) / 2), y(X68.B_RT) - 18,
                      f'{ar(X68.B_HELD)} شمعات محبوسة', TEAL_D, 27)),
        line_el(x(ca) - slot * .5, y(X68.B_RB), R, y(X68.B_RB), INK, 2.4, id="lo"),
        f'<g id="boxlbl" opacity="0">'
        + htext(x(cb) + slot * 5.2, y(X68.B_RT) + 34,
                f'العرض {X68.B_W:.{dp}f}', INK, 25) + '</g>',
        # شمعةُ الكسر: إطارٌ حول الجسم ووسمُ المضاعف
        f'<g id="brk" opacity="0">'
        f'<rect x="{x(kb) - slot * .45:.1f}" '
        f'y="{min(y(W[kb]["c"]), y(W[kb]["o"])) - 4:.1f}" width="{slot * .9:.1f}" '
        f'height="{abs(y(W[kb]["o"]) - y(W[kb]["c"])) + 8:.1f}" '
        f'fill="none" stroke="{RED}" stroke-width="3.4"/>'
        + htext(x(kb) + slot * 4.4, y(W[kb]["l"]) + 42,
                f'جسمٌ {xr(X68.B_BK)} الوسيط', RED, 26) + '</g>',
        zone_el("ext", x(kb) - slot * .5, y(X68.B_RB), x(X68.B_ILO) + slot * .5,
                y(X68.B_LO),
                htext(x((kb + X68.B_ILO) / 2), y(X68.B_LO) + 40,
                      f'نزلَ {xr(X68.B_EXT)} عرضَ المدى', RED, 26),
                fill=RED, stroke=RED),
        f'<g id="lv" opacity="0">'
        f'<line x1="{x(0) - slot * .5:.1f}" y1="{y(X68.B_ENT):.1f}" x2="{R:.1f}" '
        f'y2="{y(X68.B_ENT):.1f}" stroke="{INK}" stroke-width="2.6"/>'
        f'<line x1="{x(0) - slot * .5:.1f}" y1="{y(X68.B_TGT):.1f}" x2="{R:.1f}" '
        f'y2="{y(X68.B_TGT):.1f}" stroke="{TEAL_D}" stroke-width="2.4" '
        f'stroke-dasharray="9 7"/>'
        + htext(x(4), y(X68.B_TGT) - 14,
                f'الهدف {xr(X68.B_TW)} العرض', TEAL_D, 25)
        + htext(x(4), y(X68.B_ENT) + 36,
                f'الوقف {xr(X68.B_RW)} العرض', RED, 25) + '</g>',
        f'<g id="tall" opacity="0">'
        f'<rect x="{x(X68.B_TALL) - slot * .5:.1f}" y="{y(W[X68.B_TALL]["h"]):.1f}" '
        f'width="{slot:.1f}" '
        f'height="{y(W[X68.B_TALL]["l"]) - y(W[X68.B_TALL]["h"]):.1f}" '
        f'fill="{TEAL}" opacity="0.20"/>'
        + htext(x(X68.B_TALL) + slot * 4.6, y(W[X68.B_TALL]["h"]) - 16,
                f'أطولها {xr(X68.B_LNG)} الوسيط', TEAL_D, 25) + '</g>',
        checkmark(x(X68.B_HIT), y(W[X68.B_HIT]["h"]) - 48, id="ck"),
    ]
    # كلُّ وسمٍ يلي بيتَه بلحظة، و`base=26` يجعل المدى مكتملاً عند 2.2 ثانية
    # فلا يتحدّث النصُّ عن عرضٍ لم يُرسم بعد.
    marks = [("lo", 1.4, 2.2, "draw"), ("box", 2.3, 3.4, "zone"),
             ("boxlbl", 3.4, 3.9, "pop"), ("tall", 6.4, 6.9, "pop"),
             ("brk", 9.4, 9.9, "pop"), ("ext", 12.4, 13.4, "zone"),
             ("lv", 15.4, 16.1, "pop"), ("ck", 18.5, 18.9, "pop")]
    full = ["box", "boxlbl", "tall", "brk", "ext", "lv", "ck"]
    sfx = [("whoosh", 0.35, -3), ("tick", 1.45, -7), ("whoosh", 2.35, -4),
           ("pop", 3.45, -4), ("pop", 6.45, -4), ("riser", 8.3, -3),
           ("impact", 9.45, 0), ("whoosh", 12.45, -4), ("pop", 15.45, -3),
           ("success", 18.55, -2)]
    return ("".join(ex), marks, full, ["lo"], (9.4, 9.9), sfx, 26)


MARKUP = {"aaiq": markup_aaiq, "habs": markup_habs}

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
    with open(os.path.join(CONT, f"run68_{slug}.json"), encoding="utf-8") as f:
        return json.load(f)


def build(slug):
    C = load(slug)
    assert C["window"] == X68.REAL[slug], \
        f'{slug}: نافذة الملف {C["window"]} لا تطابق {X68.REAL[slug]}'
    assert C.get("media") == "reel", f'{slug}: ملفّه يعلن {C.get("media")} لا ريلاً'
    r = X68.WINS[slug]
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
    # بلا زومات: أثاثُ اللوحة داخل الطبقة المتحرّكة فأيُّ تكبيرٍ يقصّ محورَ
    # السعر — قِيس في ٦٧ (خمسةُ أرقامٍ مقصوصة عند 1.10).
    cam = []
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
    out = os.path.join(HERE, f"reel68_{slug}.html")
    n = build_reel(cfg, out)
    print(f'{slug:<8} ريل {DUR}s · بيتات {len(beats)} · ماركب {len(marks)} · '
          f'نافذة {r["slug"]} · {n} bytes')
    return out, sfx


if __name__ == "__main__":
    for s in (sys.argv[1:] or list(MARKUP)):
        out, sfx = build(s)
        json.dump(sfx, open(os.path.join(HERE, f"reel68_{s}_sfx.json"), "w"),
                  ensure_ascii=False)
