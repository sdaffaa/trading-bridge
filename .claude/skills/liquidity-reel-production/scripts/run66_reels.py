# -*- coding: utf-8 -*-
"""ريلا تشغيلة ٦٦ — نافذتان حقيقيتان، ≤22.4 ثانية، مؤثرات فقط (§12).

وهذان ريلا **قياس** لا ريلا صفقة، فلا يمرّان على `run32_desk`: محرّك
«جلسة متداول» يفتح تذكرةَ أمرٍ ويطبع دخولاً ووقفاً وهدفاً، وموضوعا اليوم
درسان في قراءة الشمعات لا خطّتا دخول — فطبعُ تذكرةٍ عليهما يَعِد بما لا
يدرّسه. فيُبنيان على نمط `run31_reel`: جارتٌ واحد بريبلاي حي، وسوم تتراكم،
وطبقةُ مؤثرات مثبّتة على لحظات الأحداث.

    habs  → النافذة ٢٣ · الذهب ٣٠ دقيقة — مدىً حبس ثلاث عشرة شمعة
    hissa → النافذة ٥٩ · البلاتين ساعة — شمعةٌ واحدة ونصفُ الحركة

والنمطان مختلفان وإن كانت فئةُ النافذتين واحدة (`consol`): الأولى تقيس
**عرضاً** يمتدّ أفقياً ويسقط على ما بعده، والثانية تقيس **حصّةً** من صافي
ساقٍ رأسية. §11 يمنع أن يتشابه ريلان، والتشابهُ في الدرس والماركب لا في
الوسم الذي صنّف به المسحُ النافذة.

⚠️ **مؤجَّلٌ لا مهجور**: نافذتا الوحدتين تبيّن أنهما مقيَّدتان سابقاً
(بمقياس `RC.claim_fresh` لا `su`/`eu`)، فلم يُسلَّم ريلٌ في ٦٦ ونصّا
الوحدتين في `content/deferred/`. الماركب والإيقاع والمؤثرات هنا مقيسةٌ
وجاهزة: أوّلُ نافذةٍ حرّة تُعيد قياسَ الأرقام وتُشغّل الملفّ كما هو.

    python3 run66_reels.py [slug ...]
"""
import json, os, sys

from reel_build import INK, TEAL, TEAL_D, RED, GREY, htext
from reel_sfx_kit import (build_reel, line_el, zone_el, xmark, checkmark, ring,
                          set_canvas, set_pad)
import tv_chart
import run31_charts as RC
import run66_charts as X66
from run58_charts import ar

HERE = os.path.dirname(os.path.abspath(__file__))
CONT = os.path.normpath(os.path.join(HERE, "..", "content"))
CVW, CVH = 1080, 1400
set_canvas(CVW, CVH)
set_pad(18, 122, 92, 66)
PL, PR, PT, PB = 18, 122, 92, 66
PW, PH = CVW - PL - PR, CVH - PT - PB
DUR = 22.4                                   # سقف skip-rate (§12)
DEC = {"GC=F": 1, "PL=F": 1, "NQ=F": 0, "YM=F": 0, "USDJPY=X": 3,
       "AUDUSD=X": 5, "GBPUSD=X": 5, "EURUSD=X": 5, "BTC-USD": 0}
tv_chart.set_theme("light")


def geo(W):
    lo = min(c["l"] for c in W); hi = max(c["h"] for c in W)
    pad = (hi - lo) * 0.08
    ymin, ymax = lo - pad * 1.7, hi + pad
    slot = PW / len(W)
    return (lambda i: PL + slot * i + slot / 2,
            lambda p: PT + (ymax - p) / (ymax - ymin) * PH, slot)


# ═════════ «حبس» — المدى مسطرة ═════════
def markup_habs(r):
    W = r["w"]; x, y, slot = geo(W)
    bk, hi, lo, ti = X66.B_BK, X66.B_HI, X66.B_LO, X66.B_TI
    R = CVW - PR
    ex = [
        zone_el("rng", x(0) - slot * .5, y(hi), x(bk - 1) + slot * .5, y(lo),
                htext(x(bk / 2), y(lo) + 34, "مدىً واحد", TEAL_D, 26)),
        line_el(x(0) - slot * .5, y(hi), R, y(hi), INK, 2.4, id="top"),
        f'<g id="toplbl" opacity="0">'
        + htext(x(bk) + slot * 2.2, y(hi) - 16,
                f'الحدّ {hi:,.{DEC.get(r["sym"], 2)}f}', INK, 26) + '</g>',
        # شمعة الكسر: عمودٌ خفيفٌ خلفها وإطارٌ حول جسمها — لا تعبئةٌ تطمسها.
        # (رُصد بالفحص البصري: تعبئةٌ بشفافية ٠٫٢٤ فوق الشمعة تمحوها فيرى
        #  المشاهدُ شريطاً تركوازياً لا شمعةً مميَّزة.)
        f'<g id="bkc" opacity="0">'
        f'<rect x="{x(bk) - slot * .5:.1f}" y="{y(W[bk]["h"]):.1f}" '
        f'width="{slot:.1f}" height="{y(W[bk]["l"]) - y(W[bk]["h"]):.1f}" '
        f'fill="{TEAL}" opacity="0.14"/>'
        f'<rect x="{x(bk) - slot * .45:.1f}" y="{min(y(W[bk]["c"]), y(W[bk]["o"])) - 4:.1f}" '
        f'width="{slot * .9:.1f}" '
        f'height="{abs(y(W[bk]["o"]) - y(W[bk]["c"])) + 8:.1f}" '
        f'fill="none" stroke="{TEAL_D}" stroke-width="3.2"/>'
        + htext(x(bk) + slot * 3.6, y(W[bk]["l"]) + 40,
                f'جسمٌ {RC.pips(r, W[bk]["c"], W[bk]["o"])} نقطة', TEAL_D, 26) + '</g>',
        line_el(x(bk) - slot * .5, y(W[ti]["h"]), R, y(W[ti]["h"]), TEAL_D, 2.2,
                dash="8 7", id="ext"),
        f'<g id="extlbl" opacity="0">'
        + htext(x(bk) + slot * 3.2, y(W[ti]["h"]) - 16,
                f'{X66.B_EXT:.2f}× عرضِ المدى', TEAL_D, 26) + '</g>',
        checkmark(x(ti), y(W[ti]["h"]) - 48, id="ck"),
    ]
    marks = [("rng", 3.2, 4.6, "zone"), ("top", 5.0, 5.9, "draw"),
             ("toplbl", 5.9, 6.2, "pop"), ("bkc", 10.2, 10.7, "pop"),
             ("ext", 15.0, 15.9, "draw"), ("extlbl", 15.9, 16.3, "pop"),
             ("ck", 18.6, 19.0, "pop")]
    full = ["toplbl", "bkc", "extlbl", "ck"]
    sfx = [("whoosh", 0.35, -3), ("tick", 2.2, -6), ("whoosh", 3.25, -4),
           ("pop", 5.95, -4), ("tick", 8.0, -7), ("riser", 8.8, -2),
           ("impact", 10.25, 0), ("tick", 13.0, -7), ("whoosh", 15.05, -4),
           ("pop", 15.95, -4), ("success", 18.65, -2)]
    return "".join(ex), marks, full, ["top", "ext"], (10.2, 10.7), sfx, max(2, bk - 6)


# ═════════ «حصة» — شمعةٌ واحدة ونصفُ الحركة ═════════
def markup_hissa(r):
    W = r["w"]; x, y, slot = geo(W)
    lo_i, hi_i, one = X66.H_LO, X66.H_HI, X66.H_LO + X66.H_TI
    R = CVW - PR
    dp = DEC.get(r["sym"], 2)
    ex = [
        line_el(x(lo_i) - slot * .5, y(W[lo_i]["o"]), R, y(W[lo_i]["o"]), GREY, 2.0,
                dash="6 6", id="lg0"),
        line_el(x(lo_i) - slot * .5, y(W[hi_i]["c"]), R, y(W[hi_i]["c"]), GREY, 2.0,
                dash="6 6", id="lg1"),
        f'<g id="lglbl" opacity="0">'
        + htext(x(lo_i) + slot * 5.0, y(W[hi_i]["c"]) - 16,
                f'الساق {RC.pips(r, W[hi_i]["c"], W[lo_i]["o"])} نقطة', INK, 26) + '</g>',
        # الشمعة الواحدة: عمودٌ خفيفٌ خلفها وإطارٌ حول جسمها — والتعبئةُ
        # الثقيلة تمحو الشمعةَ نفسها فيبقى شريطٌ لا درس (رُصد بالفحص البصري).
        f'<g id="one" opacity="0">'
        f'<rect x="{x(one) - slot * .5:.1f}" y="{y(W[one]["h"]):.1f}" '
        f'width="{slot:.1f}" height="{y(W[one]["l"]) - y(W[one]["h"]):.1f}" '
        f'fill="{TEAL}" opacity="0.14"/>'
        f'<rect x="{x(one) - slot * .45:.1f}" y="{y(W[one]["c"]) - 4:.1f}" '
        f'width="{slot * .9:.1f}" height="{y(W[one]["o"]) - y(W[one]["c"]) + 8:.1f}" '
        f'fill="none" stroke="{TEAL_D}" stroke-width="3.2"/>'
        + htext(x(one) + slot * 4.4, y(W[one]["c"]) - 18,
                f'{X66.H_SHARE * 100:.1f}٪ من الصافي', TEAL_D, 27) + '</g>',
        f'<g id="restlbl" opacity="0">'
        + htext(x(hi_i) - slot * 3.0, y(W[lo_i]["o"]) + 44,
                f'والباقي {ar(len(X66.H_SEG) - 1)} شمعة — '
                f'{100 - X66.H_SHARE * 100:.1f}٪', RED, 26) + '</g>',
        checkmark(x(hi_i), y(W[hi_i]["h"]) - 48, id="ck"),
    ]
    marks = [("lg0", 3.0, 3.8, "draw"), ("lg1", 4.0, 4.8, "draw"),
             ("lglbl", 4.8, 5.2, "pop"), ("one", 10.0, 10.6, "pop"),
             ("restlbl", 14.6, 15.1, "pop"), ("ck", 18.6, 19.0, "pop")]
    full = ["lglbl", "one", "restlbl", "ck"]
    sfx = [("whoosh", 0.35, -3), ("tick", 2.0, -6), ("whoosh", 3.05, -4),
           ("whoosh", 4.05, -5), ("pop", 5.25, -4), ("tick", 7.6, -7),
           ("riser", 8.6, -2), ("impact", 10.05, 0), ("tick", 12.6, -7),
           ("pop", 14.65, -3), ("success", 18.65, -2)]
    return "".join(ex), marks, full, ["lg0", "lg1"], (10.0, 10.6), sfx, max(2, lo_i - 4)


MARKUP = {"habs": markup_habs, "hissa": markup_hissa}

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
    with open(os.path.join(CONT, f"run66_{slug}.json"), encoding="utf-8") as f:
        return json.load(f)


def build(slug):
    C = load(slug)
    assert C["window"] == X66.REAL[slug], \
        f'{slug}: نافذة الملف {C["window"]} لا تطابق {X66.REAL[slug]}'
    r = X66.WINS[slug]
    W = r["w"]
    ex, marks, full, drawset, flash, sfx, base = MARKUP[slug](r)
    beats = C["reel"]["beats"]
    assert beats[-1]["t"] < DUR - 2.6, "آخر بيت يتجاوز موضع نداء الفعل"
    txt = []
    for i, b in enumerate(beats):
        end = beats[i + 1]["t"] - 0.05 if i + 1 < len(beats) else DUR - 0.6
        sub = f'<span class="why">{b["sub"]}</span>' if b.get("sub") else ""
        txt.append((f"t{i+1}", b["t"], round(end, 2), f'<b>{b["title"]}</b>{sub}', 50, INK))

    # الشموع تتكشّف من الإطار صفر: القاعدة «فريم-0 شموع تتحرك» (§12)
    span = DUR - 3.2
    story = [(j, round(0.15 + (j - base) * span / max(1, len(W) - base), 2))
             for j in range(base, len(W))]
    cam = [[0.0, 1.02, .5, .5], [6.0, 1.09, .55, .52, "creep"],
           [11.0, 1.15, .56, .54, "ramp"], [16.0, 1.10, .52, .48, "creep"],
           [DUR, 1.03, .5, .5, "creep"]]
    cfg = dict(
        w=W, dark=False, extra_css=BASE_CSS, extra_html="", grid=False,
        pre_svg=tv_chart.furniture(W, dec=DEC.get(r["sym"], 2), sym=r["sym"],
                                   tf=r["tf"], tlabels=[c["d"] for c in W]),
        lp_pill=True, lp_dec=DEC.get(r["sym"], 2), lp_col=tv_chart.T["PILL"],
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
    out = os.path.join(HERE, f"reel66_{slug}.html")
    n = build_reel(cfg, out)
    print(f'{slug:<8} ريل {DUR}s · بيتات {len(beats)} · ماركب {len(marks)} · '
          f'نافذة {r["slug"]} · {n} bytes')
    return out, sfx


SFX_OF = {}

if __name__ == "__main__":
    for s in (sys.argv[1:] or list(MARKUP)):
        out, sfx = build(s)
        SFX_OF[s] = sfx
        json.dump(sfx, open(os.path.join(HERE, f"reel66_{s}_sfx.json"), "w"),
                  ensure_ascii=False)
