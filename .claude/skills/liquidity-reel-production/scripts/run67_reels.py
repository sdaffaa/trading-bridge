# -*- coding: utf-8 -*-
"""ريل تشغيلة ٦٧ — نافذةٌ حقيقية واحدة، ≤22.4 ثانية، مؤثرات فقط (§12).

وهذا ريلُ **قياس** لا ريلُ صفقة، فلا يمرّ على `run32_desk`: محرّك «جلسة
متداول» يفتح تذكرةَ أمرٍ ويطبع دخولاً ووقفاً وهدفاً، وموضوعُ اليوم درسٌ في
قياس البُعد عن حدٍّ لا خطّةُ دخول — فطبعُ تذكرةٍ عليه يَعِد بما لا يدرّسه.

    masafa → النافذة ٦٧ · الأسترالي/الدولار ساعة — ستُّ شمعاتٍ بعيدة ثمّ ٩٠٪
             بشمعةٍ واحدة

ووحدة «فتائل» كانت ريلاً ثانياً فصارت كاروسيلاً: المخزونُ أعطى نافذةً
حقيقيةً واحدة، و§11 يقول عند غيابها «الريل يتحول كاروسيل/شيت». ولا يُبنى
ريلٌ على سلسلةٍ مولّدة لأنّ `tv_chart.furniture` يطبع أرقامَ محورِ السعر،
و§11 البديلة تمنع طبعَ أيّ سعرٍ على مثالٍ تخطيطي.

    python3 run67_reels.py [slug ...]
"""
import json, os, sys

from reel_build import INK, TEAL, TEAL_D, RED, GREY, htext
from reel_sfx_kit import (build_reel, line_el, zone_el, xmark, checkmark, ring,
                          set_canvas, set_pad)
import tv_chart
import run31_charts as RC
import run67_charts as X67
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



# ═════════ «مسافة» — البُعد عن الحدّ منبّهٌ يتغيّر كل شمعة ═════════
def markup_masafa(r):
    W = r["w"]; x, y, slot = geo(W)
    hi = X67.M_HI
    a, b = X67.M_RUN[0], X67.M_LAST
    nx, bk = X67.M_NEXT, X67.M_BK
    R = CVW - PR
    dp = DEC.get(r["sym"], 2)
    ex = [
        line_el(x(0) - slot * .5, y(hi), R, y(hi), INK, 2.4, id="top"),
        f'<g id="toplbl" opacity="0">'
        + htext(x(bk) + slot * 2.4, y(hi) - 16,
                f'الحدّ {hi:,.{dp}f}', INK, 26) + '</g>',
        # الشريحة البعيدة: ستُّ شمعاتٍ ما نزلت المسافة فيهنّ
        zone_el("far", x(a) - slot * .5, y(max(c["h"] for c in W[a:b + 1])),
                x(b) + slot * .5, y(min(c["l"] for c in W[a:b + 1])),
                htext(x((a + b) / 2), y(min(c["l"] for c in W[a:b + 1])) + 36,
                      f'{ar(len(X67.M_RUN))} شمعة ما نزلت تحت 1.80×', TEAL_D, 26)),
        # الشمعة التي أغلقت تسعين بالمئة: عمودٌ خفيفٌ وإطارٌ حول الجسم
        f'<g id="one" opacity="0">'
        f'<rect x="{x(nx) - slot * .5:.1f}" y="{y(W[nx]["h"]):.1f}" '
        f'width="{slot:.1f}" height="{y(W[nx]["l"]) - y(W[nx]["h"]):.1f}" '
        f'fill="{RED}" opacity="0.14"/>'
        f'<rect x="{x(nx) - slot * .45:.1f}" '
        f'y="{min(y(W[nx]["c"]), y(W[nx]["o"])) - 4:.1f}" width="{slot * .9:.1f}" '
        f'height="{abs(y(W[nx]["o"]) - y(W[nx]["c"])) + 8:.1f}" '
        f'fill="none" stroke="{RED}" stroke-width="3.2"/>'
        + htext(x(nx) + slot * 3.8, y(W[nx]["l"]) + 42,
                f'{ar(round(X67.M_CLOSED * 100))}٪ بشمعة', RED, 27) + '</g>',
        checkmark(x(bk), y(W[bk]["h"]) - 48, id="ck"),
    ]
    # لا وسمَ عائمٌ لأقصى بُعد: رقمُه في عنوان البيت نفسه، ووسمُه على
    # اللوحة يبقى ظاهراً فيلتقي لاحقاً بشمعة «٩٠٪» فيُقرأ وسماً لها.
    marks = [("top", 3.0, 3.9, "draw"), ("toplbl", 3.9, 4.3, "pop"),
             ("far", 9.4, 10.6, "zone"),
             ("one", 12.4, 12.9, "pop"), ("ck", 18.6, 19.0, "pop")]
    # «far» في `fullset` وإن كان زوناً: محرّكُ المؤثرات لا يحرّك إلا ما في
    # `fullset` أو `drawset` — ووسمٌ في `marks` وحدها يبقى شفافاً للأبد
    # (قِيس: opacity=0 في كل لحظة). وهي علّةٌ موروثة من ٦٦ لم تُرصد لأن
    # ريلَيها لم يُرندَرا.
    full = ["toplbl", "far", "one", "ck"]
    sfx = [("whoosh", 0.35, -3), ("tick", 2.0, -6), ("whoosh", 3.05, -4),
           ("pop", 3.95, -4), ("tick", 5.6, -7), ("pop", 6.45, -4),
           ("whoosh", 9.45, -4), ("riser", 11.2, -2), ("impact", 12.45, 0),
           ("tick", 15.4, -7), ("success", 18.65, -2)]
    return ("".join(ex), marks, full, ["top"], (12.4, 12.9), sfx,
            max(2, a - 5))


MARKUP = {"masafa": markup_masafa}

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
    with open(os.path.join(CONT, f"run67_{slug}.json"), encoding="utf-8") as f:
        return json.load(f)


def build(slug):
    C = load(slug)
    assert C["window"] == X67.REAL[slug], \
        f'{slug}: نافذة الملف {C["window"]} لا تطابق {X67.REAL[slug]}'
    assert C.get("media") == "reel", f'{slug}: ملفّه يعلن {C.get("media")} لا ريلاً'
    r = X67.WINS[slug]
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
    # بلا زومات: أثاثُ اللوحة داخل الطبقة المتحرّكة، فأيُّ تكبيرٍ يدفع
    # محورَ السعر خارج الكانفاس — قِيس بالفحص: عند 1.10 قُصّت خمسةُ أرقامٍ
    # من المحور الأيمن. والصيغةُ المعتمدة في `run28_cinema` بلا كاميرا أصلاً.
    cam = []
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
    out = os.path.join(HERE, f"reel67_{slug}.html")
    n = build_reel(cfg, out)
    print(f'{slug:<8} ريل {DUR}s · بيتات {len(beats)} · ماركب {len(marks)} · '
          f'نافذة {r["slug"]} · {n} bytes')
    return out, sfx


SFX_OF = {}

if __name__ == "__main__":
    for s in (sys.argv[1:] or list(MARKUP)):
        out, sfx = build(s)
        SFX_OF[s] = sfx
        json.dump(sfx, open(os.path.join(HERE, f"reel67_{s}_sfx.json"), "w"),
                  ensure_ascii=False)
