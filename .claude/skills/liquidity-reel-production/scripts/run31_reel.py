# -*- coding: utf-8 -*-
"""ريلات تشغيلة ٣١ — نافذة حقيقية، ≤22.4 ثانية، مؤثرات فقط (§12).

لا كلام منطوق ولا ريل صامت: طبقة `assets/sfx` مثبّتة على لحظات الأحداث
عبر `sfx_mux.mux`. الشموع تتكشّف من الإطار صفر (لا لقطة ساكنة في البداية)،
والوسوم تتراكم على جارت واحد كما في §7.

الكاميرا هنا هادئة عمداً: أمر فهد الأخير (2026-08-06) كان «بدون زومات
عالجارت» على ريل الباك تست، و§13 يوجب كيفريمات كاميرا — فالتوفيق أن تبقى
الكيفريمات موجودة بمدى ضيّق (≤1.18) بلا لصق على الشموع.

    python3 run31_reel.py <slug>
"""
import json, os, sys

from reel_build import INK, TEAL, TEAL_D, RED, GREY, htext
from reel_sfx_kit import (build_reel, line_el, zone_el, xmark, checkmark, ring,
                          set_canvas, set_pad)
import tv_chart
import run31_charts as RC
from car_common import dkmap

HERE = os.path.dirname(os.path.abspath(__file__))
CONT = os.path.normpath(os.path.join(HERE, "..", "content"))
CVW, CVH = 1080, 1400
set_canvas(CVW, CVH)
set_pad(18, 122, 92, 66)
PL, PR, PT, PB = 18, 122, 92, 66
PW, PH = CVW - PL - PR, CVH - PT - PB
DUR = 22.4                                   # سقف skip-rate (§12)
tv_chart.set_theme("light")


def geo(W):
    lo = min(c["l"] for c in W); hi = max(c["h"] for c in W)
    pad = (hi - lo) * 0.08
    ymin, ymax = lo - pad * 1.7, hi + pad
    slot = PW / len(W)
    return (lambda i: PL + slot * i + slot / 2,
            lambda p: PT + (ymax - p) / (ymax - ymin) * PH, slot)


def markup(r):
    """وسوم القصة على إحداثيات لوحة الريل — كلها على أسعار OHLC فعلية."""
    W = r["w"]; x, y, slot = geo(W)
    iH, bk, iob, ir = r["iH"], r["bk"], r["iob"], r["ir"]
    lv = W[iH]["h"]; zt, zb = W[iob]["o"], W[iob]["l"]
    top_i = max(range(ir, len(W)), key=lambda j: W[j]["h"])
    ne = max(iob + 1, min(ir - 3, len(W) - 2))
    low_i = min(range(ne + 1, ir + 1), key=lambda j: W[j]["l"])
    R = CVW - PR
    ex = [
        # كسر الهيكل: من القمة إلى شمعة الكسر فقط (§7)
        line_el(x(iH) - slot * .6, y(lv), x(bk) + slot * .55, y(lv), INK, 2.4, id="bos"),
        f'<g id="boslbl" opacity="0">{htext(x(iH) + slot * 1.8, y(lv) - 16, "كسر الهيكل", INK, 26)}</g>',
        zone_el("zn", x(iob) - slot * .6, y(zt), x(min(ir + 3, len(W) - 1)) + slot * .5,
                y(zb), htext((x(iob) + x(ir)) / 2, y(zb) + 34, "منطقة الطلب", TEAL_D, 25)),
        # الدخول المستعجل فوق المنطقة ثم هبوط السعر تحته
        f'<g id="trap" opacity="0">'
        f'<circle cx="{x(ne):.1f}" cy="{y(W[ne]["c"]):.1f}" r="13" fill="none" '
        f'stroke="{RED}" stroke-width="3.2"/>'
        + htext(x(ne) - slot * 3.4, y(W[ne]["c"]) - 22, "هني أغروك", RED, 25) + '</g>',
        xmark(x(low_i), y(W[low_i]["l"]) + 26, id="xh", r=17),
        # الدخول الصحيح عند العودة
        ring("ent", x(ir), y(W[ir]["l"]), 15, TEAL_D,
             htext(x(ir) - slot * 3.8, y(W[ir]["l"]) + 46, "الدخلة الصح", TEAL_D, 26)),
        line_el(x(ir) - slot * .6, y(W[top_i]["h"]), R, y(W[top_i]["h"]), TEAL_D, 2.2,
                dash="8 7", id="tgt"),
        f'<g id="tgtlbl" opacity="0">'
        + htext(x(ir) + slot * 2.0, y(W[top_i]["h"]) - 16,
                f'الهدف · {RC.pips(r, W[top_i]["h"], W[ir]["l"])} نقطة', TEAL_D, 26) + '</g>',
        checkmark(x(top_i), y(W[top_i]["h"]) - 46, id="ck"),
    ]
    return "".join(ex), dict(x=x, y=y, slot=slot, iH=iH, bk=bk, iob=iob, ir=ir,
                             top=top_i, ne=ne, low=low_i, lv=lv, zt=zt, zb=zb)


BASE_CSS = """
.hl{top:118px;left:56px;right:56px;line-height:1.16}
.hl b{display:block;font-size:50px;font-weight:900;line-height:1.14;letter-spacing:-.6px}
.hl .why{display:block;margin-top:10px;font-size:29px;font-weight:600;color:#6B7C84}
#chartclip{top:360px;left:0}
#chip{display:none} #endlogo{display:none} #res{display:none}
#cta{top:1792px} #cta .k{font-size:44px;padding:9px 30px} #cta .s{margin-top:8px;font-size:26px}
#edu{bottom:22px;font-size:19px;opacity:.5}
"""


def build(slug):
    C = json.load(open(os.path.join(CONT, f"run31_{slug}.json"), encoding="utf-8"))
    r = RC.win(C["window"])
    W = r["w"]
    ex, G = markup(r)
    beats = C["reel"]["beats"]
    assert beats[-1]["t"] < DUR, "آخر بيت يتجاوز مدة الريل"
    txt = []
    for i, b in enumerate(beats):
        end = beats[i + 1]["t"] - 0.05 if i + 1 < len(beats) else DUR - 0.6
        sub = f'<span class="why">{b["sub"]}</span>' if b.get("sub") else ""
        txt.append((f"t{i+1}", b["t"], round(end, 2), f'<b>{b["title"]}</b>{sub}', 50, INK))

    # الشموع تتكشّف من الإطار صفر: القاعدة «فريم-0 شموع تتحرك» (§12)
    base = max(4, G["iob"] - 2)
    span = DUR - 3.2
    story = [(j, round(0.15 + (j - base) * span / max(1, len(W) - base), 2))
             for j in range(base, len(W))]
    marks = [
        ("bos", 3.0, 3.8, "draw"), ("boslbl", 3.8, 4.1, "pop"),
        ("zn", 5.2, 6.4, "zone"),
        ("trap", 8.6, 9.0, "pop"), ("xh", 10.4, 10.9, "drawx"),
        ("ent", 13.4, 13.9, "ring"),
        ("tgt", 16.4, 17.2, "draw"), ("tgtlbl", 17.2, 17.6, "pop"),
        ("ck", 19.4, 19.8, "pop"),
    ]
    full = ["boslbl", "zn", "trap", "xh", "ent", "tgtlbl", "ck"]
    cam = [[0.0, 1.02, .5, .5], [6.0, 1.10, .55, .52, "creep"],
           [11.0, 1.16, .58, .56, "ramp"], [16.0, 1.12, .52, .48, "creep"],
           [DUR, 1.04, .5, .5, "creep"]]
    cfg = dict(
        w=W, dark=False, extra_css=BASE_CSS, extra_html="", grid=False,
        pre_svg=tv_chart.furniture(W, dec=C.get("dec", 2), sym=r["sym"], tf=r["tf"],
                                   tlabels=[c["d"] for c in W]),
        lp_pill=True, lp_dec=C.get("dec", 2), lp_col=tv_chart.T["PILL"],
        lp_txt=tv_chart.T["PILLTX"],
        base=base, openmax=len(W), open_t=[[base, 0.4]], story=story,
        extra_svg=ex, marks=marks, fullset=full, drawset=["bos", "tgt"], dom_marks=[],
        preview_a=0.0, preview_b=0.0, res_tease=False, sweep_op=0.0,
        txt=txt, chip="", res="",
        cta_k=f'اكتب «{C["car"]["cta"]["keyword"]}»', cta_s="ويصلك الدليل كاملاً",
        edu=f'{r["slug"]} — لغرض تعليمي',
        dur=DUR, res_t=999, cta_t=DUR - 2.6,
        flash=(10.4, 10.9), flash_op=0.20, punch=(10.4, 10.8, 0.05),
        cam=cam,
    )
    out = os.path.join(HERE, f"reel31_{slug}.html")
    n = build_reel(cfg, out)
    print(f'{slug:<10} ريل {DUR}s · بيتات {len(beats)} · ماركب {len(marks)} · '
          f'نافذة {r["slug"]} · {n} bytes')
    return out


# مؤثرات §12: مؤثر واحد لكل حدث بصري، والصمت بينها جزء من الإيقاع
SFX = [("whoosh", 0.35, -3), ("tick", 2.0, -6), ("whoosh", 3.0, -4),
       ("pop", 3.85, -4), ("whoosh", 5.25, -4), ("tick", 7.2, -7),
       ("pop", 8.65, -3), ("impact", 10.45, 0), ("tick", 12.0, -7),
       ("pop", 13.45, -3), ("riser", 15.1, -2), ("whoosh", 16.45, -4),
       ("pop", 17.25, -4), ("success", 19.45, -2)]

if __name__ == "__main__":
    for s in sys.argv[1:]:
        build(s)
