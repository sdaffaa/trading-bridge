# -*- coding: utf-8 -*-
"""ريلا تشغيلة ٧١ — نافذتان حقيقيتان، ≤22.4 ثانية، مؤثرات فقط (§12).

    damj  → النافذة ٧٣ · الأفالانش/دولار ساعة — عشرةُ خطوطٍ وأربعةُ أماكن
    lamsa → النافذة ٧٤ · الريبل/دولار ساعة — چم شمعة قبل أول لمسة؟

والبيتات تأتي من ملفّ الوحدة بحقل `phase` لا `t` (قرار §11)، فالأزمانُ
هنا في `PHASE_T` — جدولٌ واحدٌ للريلين كي لا يختلف إيقاعُهما بلا سبب.

ولا تذكرةَ أمرٍ في أيّهما: الوحدتان درسُ قراءةٍ لا درسُ دخول، و§8d تمنع
كتابة دخولٍ ووقفٍ وR حين لا يقتضيه النموذج.

    python3 run71_reels.py [slug ...]
"""
import json, os, sys

from reel_build import INK, TEAL, TEAL_D, RED, htext
from reel_sfx_kit import (build_reel, line_el, zone_el, checkmark,
                          set_canvas, set_pad)
import tv_chart
import run71_charts as X
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
DEC = {"AVAX-USD": 3, "XRP-USD": 4}
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


# ═════════ «دمج» — عشرةُ خطوطٍ يقرؤها السوقُ أربعةَ أماكن ═════════
def markup_damj(r):
    W = r["w"]; x, y, slot = geo(W)
    n = len(W)
    x0, x1 = x(0) - slot * .5, x(n - 1) + slot * .5
    bot, top, born = X.D_BOT, X.D_TOP, X.D_BORN
    best = X.D_EACH.index(max(X.D_EACH))
    bline = X.D_BIG[best][1]

    lines = "".join(
        line_el(x0, y(p), x1, y(p), INK, 2.4, None, f"l{k}")
        for k, (_, p) in enumerate(X.D_LV))
    zones = "".join(
        zone_el(f"z{k}",
                x0, y(min(pp for _, pp in g)) + 4,
                x1, y(max(pp for _, pp in g)) - 4, "")
        for k, g in enumerate(X.D_GRP))
    dots = "".join(
        f'<circle cx="{x(j):.1f}" cy="{y(max(bot, min(top, W[j]["c"]))):.1f}" '
        f'r="9" fill="none" stroke="{TEAL_D}" stroke-width="3"/>'
        for j in range(born + 1, n)
        if W[j]["l"] <= top and W[j]["h"] >= bot)

    ex = [
        lines,
        '<g id="lvt" opacity="0">'
        + htext(x(9), y(X.D_LV[-1][1]) - 40,
                f'{ar(len(X.D_LV))} مستويات', INK, 30) + '</g>',
        zones,
        '<g id="bigt" opacity="0">'
        + box(x(born) + slot * .5, y(top), x1, y(bot), TEAL_D, 3.2)
        + htext(x(born) - slot * 3.0, y(top) - 30,
                f'{ar(len(X.D_BIG))} خطوطٍ · {xr(X.D_WIDE)} وسيط المدى',
                TEAL_D, 27) + '</g>',
        f'<g id="tch" opacity="0">{dots}'
        + htext(x(n - 8), y(bot) + 70,
                f'{ar(X.D_ZT)} لمسات للمنطقة', TEAL_D, 29) + '</g>',
        '<g id="one" opacity="0">'
        + line_el(x(born) + slot * .5, y(bline), x1, y(bline), RED, 3.4, None, "")
        # ووسمُ أقوى خطٍّ في الطرف الأيسر: عند الطرف الأيمن يلتقي بوسم
        # اللمسات لأن الخطَّ من المنطقة نفسها (رُئي في إطار 20.8).
        + htext(x(7), y(bline) - 34,
                f'أقوى خطٍّ {ar(max(X.D_EACH))}', RED, 27) + '</g>',
        checkmark(x(n - 3), y(top) - 96, id="ck"),
    ]
    marks = ([(f"l{k}", 3.5 + k * 0.18, 4.0 + k * 0.18, "draw")
              for k in range(len(X.D_LV))]
             + [("lvt", 5.6, 6.1, "pop")]
             + [(f"z{k}", 10.8 + k * 0.22, 11.6 + k * 0.22, "zone")
                for k in range(len(X.D_GRP))]
             + [("bigt", 12.6, 13.2, "pop"), ("tch", 17.4, 18.1, "pop"),
                ("one", 19.0, 19.5, "pop"), ("ck", 20.2, 20.6, "pop")])
    # المناطقُ تبقى ظاهرةً بعد رسمها: بدونها في `fullset` تختفي عند
    # انتهاء نافذتها فيصل بيتُ «أربعُ مناطق» ولا منطقةَ على الشاشة.
    full = [f"z{k}" for k in range(len(X.D_GRP))] + \
           ["lvt", "bigt", "tch", "one", "ck"]
    draw = [f"l{k}" for k in range(len(X.D_LV))]
    sfx = [("whoosh", 0.35, -3), ("tick", 2.60, -7), ("pop", 3.55, -5),
           ("pop", 5.65, -4), ("whoosh", 6.70, -4), ("riser", 9.60, -6),
           ("tick", 10.85, -7), ("pop", 12.65, -4), ("impact", 17.45, -1),
           ("pop", 19.05, -4), ("success", 20.25, -2)]
    return ("".join(ex), marks, full, draw, (17.4, 17.9), sfx, 26)


# ═════════ «لمسة» — چم شمعة قبل أول لمسة؟ ═════════
def markup_lamsa(r):
    W = r["w"]; x, y, slot = geo(W)
    n = len(W)
    x0, x1 = x(0) - slot * .5, x(n - 1) + slot * .5
    q, lt, nv = X.L_QUICK, X.L_LATE, X.L_NEV[0]

    def lv(e, col, w, upto=None):
        end = n - 1 if upto is None else upto
        return line_el(x(e["i"]) - slot * .5, y(e["p"]),
                       x(end) + slot * .5, y(e["p"]), col, w, None, "")

    lines = "".join(
        line_el(x(e["i"]) - slot * .5, y(e["p"]),
                x(n - 1) + slot * .5, y(e["p"]), INK, 2.2, None, f"v{k}")
        for k, e in enumerate(X.L_LV))
    hits = "".join(
        f'<circle cx="{x(e["t"]):.1f}" cy="{y(e["p"]):.1f}" r="10" '
        f'fill="none" stroke="{TEAL_D}" stroke-width="3.2"/>'
        for e in X.L_TST)

    ex = [
        lines,
        '<g id="cnt" opacity="0">'
        + htext(x(9), y(X.L_LV[0]["p"]) - 44,
                f'{ar(len(X.L_LV))} مستويات', INK, 30) + '</g>',
        '<g id="fast" opacity="0">'
        + lv(q, TEAL_D, 3.4, q["t"])
        + box(x(q["t"]) - slot * .5, y(W[q["t"]]["h"]) - 6,
              x(q["t"]) + slot * .5, y(W[q["t"]]["l"]) + 6, TEAL_D, 3.0)
        + htext(x(q["t"]) + slot * 4.4, y(q["p"]) - 34,
                f'{ar(q["age"])} شمعات', TEAL_D, 28) + '</g>',
        '<g id="slow" opacity="0">'
        + lv(lt, INK, 3.0, lt["t"])
        + box(x(lt["t"]) - slot * .5, y(W[lt["t"]]["h"]) - 6,
              x(lt["t"]) + slot * .5, y(W[lt["t"]]["l"]) + 6, INK, 3.0)
        + htext(x(lt["i"]) + slot * 5.0, y(lt["p"]) + 52,
                f'{ar(lt["age"])} شمعة', INK, 28) + '</g>',
        f'<g id="hits" opacity="0">{hits}'
        + htext(x(n - 9), y(X.L_LV[-1]["p"]) - 40,
                f'{ar(len(X.L_TST))} من {ar(len(X.L_LV))}', TEAL_D, 30) + '</g>',
        '<g id="nev" opacity="0">'
        + lv(nv, RED, 3.4)
        + htext(x(nv["i"]) + slot * 6.6, y(nv["p"]) + 48,
                'ما جاه السعر أبداً', RED, 27) + '</g>',
        checkmark(x(n - 3), y(X.L_LV[-1]["p"]) - 92, id="ck"),
    ]
    marks = ([(f"v{k}", 3.5 + k * 0.22, 4.1 + k * 0.22, "draw")
              for k in range(len(X.L_LV))]
             + [("cnt", 6.8, 7.3, "pop"), ("fast", 10.6, 11.2, "pop"),
                ("slow", 12.4, 13.0, "pop"), ("hits", 16.6, 17.2, "pop"),
                ("nev", 18.8, 19.4, "pop"), ("ck", 20.2, 20.6, "pop")])
    full = ["cnt", "fast", "slow", "hits", "nev", "ck"]
    draw = [f"v{k}" for k in range(len(X.L_LV))]
    sfx = [("whoosh", 0.35, -3), ("tick", 2.60, -7), ("pop", 3.55, -5),
           ("pop", 6.85, -4), ("whoosh", 9.80, -4), ("pop", 10.65, -4),
           ("pop", 12.45, -4), ("riser", 15.4, -6), ("impact", 16.65, -1),
           ("pop", 18.85, -4), ("success", 20.25, -2)]
    return ("".join(ex), marks, full, draw, (16.6, 17.1), sfx, 24)


MARKUP = {"damj": markup_damj, "lamsa": markup_lamsa}

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
    with open(os.path.join(CONT, f"run71_{slug}.json"), encoding="utf-8") as f:
        return json.load(f)


def build(slug):
    C = load(slug)
    assert C["window"] == X.REAL[slug], \
        f'{slug}: نافذة الملف {C["window"]} لا تطابق {X.REAL[slug]}'
    assert C.get("media") == "reel", f'{slug}: ملفّه يعلن {C.get("media")} لا ريلاً'
    r = X.WINS[slug]
    W = r["w"]
    ex, marks, full, drawset, flash, sfx, base = MARKUP[slug](r)
    beats = sorted(C["reel"]["beats"], key=lambda b: PHASE_T[b["phase"]])
    assert len(beats) == len(PHASE_T), f'{slug}: {len(beats)} بيتاً لا {len(PHASE_T)}'
    assert PHASE_T[beats[-1]["phase"]] < DUR - 2.6, "آخر بيت يتجاوز موضع نداء الفعل"
    txt = []
    for i, b in enumerate(beats):
        t0 = PHASE_T[b["phase"]]
        end = (PHASE_T[beats[i + 1]["phase"]] - 0.05
               if i + 1 < len(beats) else DUR - 0.6)
        sub = f'<span class="why">{b["sub"]}</span>' if b.get("sub") else ""
        txt.append((f"t{i+1}", t0, round(end, 2),
                    f'<b>{b["title"]}</b>{sub}', 50, INK))

    span = DUR - 3.2
    story = [(j, round(0.15 + (j - base) * span / max(1, len(W) - base), 2))
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
    out = os.path.join(HERE, f"reel71_{slug}.html")
    n = build_reel(cfg, out)
    print(f'{slug:<8} ريل {DUR}s · بيتات {len(beats)} · ماركب {len(marks)} · '
          f'نافذة {r["slug"]} · {n} bytes')
    return out, sfx


if __name__ == "__main__":
    for s in (sys.argv[1:] or list(MARKUP)):
        out, sfx = build(s)
        json.dump(sfx, open(os.path.join(HERE, f"reel71_{s}_sfx.json"), "w"),
                  ensure_ascii=False)
