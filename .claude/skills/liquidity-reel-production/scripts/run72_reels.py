# -*- coding: utf-8 -*-
"""ريلا تشغيلة ٧٢ — نافذتان حقيقيتان، ≤22.4 ثانية، مؤثرات فقط (§12).

    tasalsul → النافذة ٧٦ · السولانا/دولار ساعة — عُدَّ الأزواجَ قبل أن تسمّي
    jihatayn → النافذة ٧٧ · النحاس ٣٠ دقيقة — كلُّ مستوىً بلغه السعرُ لُمس من جهتيه

والبيتات تأتي من ملفّ الوحدة بحقل `phase` لا `t` (قرار §11)، فالأزمانُ
هنا في `PHASE_T` — جدولٌ واحدٌ للريلين كي لا يختلف إيقاعُهما بلا سبب.

ولا تذكرةَ أمرٍ في أيّهما: الوحدتان درسُ قراءةٍ لا درسُ دخول، و§8d تمنع
كتابة دخولٍ ووقفٍ وR حين لا يقتضيه النموذج.

    python3 run72_reels.py [slug ...]
"""
import json, os, sys

from reel_build import INK, TEAL, TEAL_D, RED, htext
from reel_sfx_kit import (build_reel, line_el, zone_el, checkmark,
                          set_canvas, set_pad)
import tv_chart
import run72_charts as X
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
DEC = {"SOL-USD": 2, "HG=F": 4}
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


def varr(x, y0, y1, col, w=3.2):
    """سهمٌ رأسيٌّ رأسُه عند `y1` — يقيس ابتعاداً، فلا يتجاوز ما يقيسه."""
    d = 1 if y1 > y0 else -1
    hd = 13
    return (f'<line x1="{x:.1f}" y1="{y0:.1f}" x2="{x:.1f}" '
            f'y2="{y1 - d * hd:.1f}" stroke="{col}" stroke-width="{w}"/>'
            f'<polygon points="{x:.1f},{y1:.1f} {x - hd * .6:.1f},'
            f'{y1 - d * hd:.1f} {x + hd * .6:.1f},{y1 - d * hd:.1f}" '
            f'fill="{col}"/>')


# ═════════ «تسلسل» — عُدَّ الأزواجَ قبل أن تسمّي ═════════
def markup_tasalsul(r):
    W = r["w"]; x, y, slot = geo(W)
    n = len(W)
    E = X.S_END
    seg = X.S_PAIR

    def pt(k):
        return x(E[k][0]), y(E[k][1])

    zig = "".join(
        line_el(*pt(k), *pt(k + 1), INK, 3.0, None, f"p{k}")
        for k in range(len(seg)))
    ends = "".join(
        f'<circle cx="{pt(k)[0]:.1f}" cy="{pt(k)[1]:.1f}" r="9" fill="none" '
        f'stroke="{INK}" stroke-width="3"/>' for k in range(len(E)))
    # التصنيفُ يُعاد رسمُه بلونه فوق الزقزاق: الصاعدُ تركوازٌ والهابطُ أحمر.
    cls = "".join(
        line_el(*pt(k), *pt(k + 1), TEAL_D if seg[k] == "↑" else RED, 5.0)
        for k in range(len(seg)))
    flip = "".join(
        f'<circle cx="{pt(k + 1)[0]:.1f}" cy="{pt(k + 1)[1]:.1f}" r="13" '
        f'fill="none" stroke="{RED}" stroke-width="3.4"/>' for k in X.S_FLIP)
    ra, rb = X.S_RA, X.S_RB
    lo = min(c["l"] for c in W[ra:rb + 1])
    hi = max(c["h"] for c in W[ra:rb + 1])

    ex = [
        zig,
        f'<g id="endc" opacity="0">{ends}</g>',
        '<g id="endt" opacity="0">'
        + htext(x(6), y(max(p for _, p, _ in E)) - 42,
                f'{ar(len(E))} أطراف', INK, 30) + '</g>',
        f'<g id="clsl" opacity="0">{cls}</g>',
        '<g id="clst" opacity="0">'
        + htext(x(n - 11), y(min(p for _, p, _ in E)) + 66,
                f'{ar(X.S_UP)} صاعدة و{ar(X.S_DN)} هابطة', INK, 30) + '</g>',
        f'<g id="flpc" opacity="0">{flip}</g>',
        # وسمُ الانقلابات في يمين اللوحة: في يسارها يقع فوق وسم الأطراف
        # بالحرف (رُئي في إطار 18.0).
        '<g id="flpt" opacity="0">'
        + htext(x(n - 11), y(max(p for _, p, _ in E)) - 42,
                f'{ar(len(X.S_FLIP))} انقلابات', RED, 31) + '</g>',
        '<g id="runb" opacity="0">'
        + box(x(ra) - slot * .5, y(hi) - 8, x(rb) + slot * .5, y(lo) + 8,
              TEAL_D, 3.6) + '</g>',
        '<g id="runt" opacity="0">'
        + htext((x(ra) + x(rb)) / 2, y(hi) - 34,
                f'{ar(X.S_SPAN)} شمعة — ربعُ النافذة', TEAL_D, 29) + '</g>',
        checkmark(x(n - 3), y(hi) - 96, id="ck"),
    ]
    # الأشكالُ تتراكم والوسومُ تتناوب: بلا زمن اختفاءٍ للوسم يجتمع أربعةُ
    # نصوصٍ على لوحةٍ واحدة (قاعدة `mark[4]` في `reel_sfx_kit`).
    marks = ([(f"p{k}", 6.8 + k * 0.20, 7.4 + k * 0.20, "draw")
              for k in range(len(seg))]
             + [("endc", 8.9, 9.4, "pop"), ("endt", 8.9, 9.4, "pop", 9.8, 0.4),
                ("clsl", 10.4, 11.0, "pop"),
                ("clst", 10.4, 11.0, "pop", 13.4, 0.4),
                ("flpc", 13.9, 14.5, "pop"),
                ("flpt", 13.9, 14.5, "pop", 16.8, 0.4),
                ("runb", 17.3, 17.9, "pop"), ("runt", 17.3, 17.9, "pop"),
                ("ck", 20.3, 20.7, "pop")])
    # و`fullset` هو ما يُحرَّك أصلاً لا ما يبقى فقط: حلقةُ المحرّك تمرّ
    # على `FULLSET` وحدها، فالوسمُ خارجَها يبقى شفافاً أبداً (رُئي: سهمُ
    # الابتعاد لم يظهر). فالكلُّ داخلَها، والاختفاءُ بـ`mark[4]`.
    full = ["endc", "endt", "clsl", "clst", "flpc", "flpt",
            "runb", "runt", "ck"]
    draw = [f"p{k}" for k in range(len(seg))]
    sfx = [("whoosh", 0.35, -3), ("tick", 2.60, -7), ("pop", 3.55, -5),
           ("whoosh", 6.70, -4), ("pop", 8.95, -4), ("pop", 10.45, -4),
           ("riser", 12.9, -6), ("impact", 13.95, -1), ("pop", 17.35, -4),
           ("success", 20.35, -2)]
    return ("".join(ex), marks, full, draw, (17.3, 17.8), sfx, 26)


# ═════════ «جهتين» — لُمس من جهتيه ثم عُبر ═════════
def markup_jihatayn(r):
    W = r["w"]; x, y, slot = geo(W)
    n = len(W)
    LV, NONE, BOTH = X.J_LV, X.J_NONE, X.J_BOTH
    top = max(BOTH, key=lambda e: e["up"] + e["dn"])

    def lv(e, col, w, upto=None, id=""):
        end = n - 1 if upto is None else upto
        return line_el(x(e["i"]) - slot * .5, y(e["p"]),
                       x(end) + slot * .5, y(e["p"]), col, w, None, id)

    def crossj(e):
        s0 = W[e["t2"]]["c"] > e["p"]
        return next(j for j in range(e["t2"] + 1, n)
                    if (W[j]["c"] > e["p"]) != s0)

    lines = "".join(lv(e, INK, 2.2, id=f"v{k}") for k, e in enumerate(LV))
    ntx = "".join(lv(e, RED, 3.2) for e in NONE)
    btx = "".join(lv(e, TEAL_D, 3.2) for e in BOTH)
    hits = "".join(
        f'<circle cx="{x(j):.1f}" cy="{y(e["p"]):.1f}" r="9" fill="none" '
        f'stroke="{TEAL_D}" stroke-width="3"/>'
        for e in BOTH for j in e["hits"])
    thits = "".join(
        f'<circle cx="{x(j):.1f}" cy="{y(top["p"]):.1f}" r="12" fill="none" '
        f'stroke="{TEAL_D if W[j]["c"] > top["p"] else RED}" '
        f'stroke-width="3.4"/>' for j in top["hits"])
    # سهمُ الابتعاد يُرسم على المستوى **الوسيط** لا على الأكثر لمساً:
    # الأكثرُ لمساً ابتعادُه ٠.٢١× والوسمُ يقول ١.١١×، فيكذّب الرسمُ وسمَه
    # (رُئي في إطار 14.4). فالمرسومُ هو الحالةُ الوسيطة نفسُها.
    rep = min(BOTH, key=lambda e: abs(e["away"] - X.J_AWAY))
    j2 = rep["t2"]
    jend = min(n - 1, j2 + X.J_HOR)
    far = max(range(j2, jend + 1), key=lambda j: abs(W[j]["c"] - rep["p"]))
    crs = "".join(
        f'<circle cx="{x(crossj(e)):.1f}" cy="{y(W[crossj(e)]["c"]):.1f}" '
        f'r="11" fill="none" stroke="{RED}" stroke-width="3.4"/>'
        for e in BOTH)

    ex = [
        lines,
        f'<g id="nonl" opacity="0">{ntx}</g>',
        '<g id="nont" opacity="0">'
        + htext(x(11), y(max(e["p"] for e in NONE)) - 40,
                f'{ar(len(NONE))} ما بلغها السعر', RED, 29) + '</g>',
        f'<g id="botl" opacity="0">{btx}{hits}</g>',
        '<g id="bott" opacity="0">'
        + htext(x(n - 11), y(min(e["p"] for e in BOTH)) + 64,
                f'{ar(len(BOTH))} من {ar(len(BOTH))} من الجهتين',
                TEAL_D, 30) + '</g>',
        f'<g id="mosc" opacity="0">{thits}</g>',
        '<g id="most" opacity="0">'
        + htext(x(top["i"]) + slot * 7.0, y(top["p"]) - 36,
                f'{ar(top["up"] + top["dn"])} لمسة: {ar(top["up"])} فوق '
                f'و{ar(top["dn"])} تحت', INK, 29) + '</g>',
        '<g id="awyl" opacity="0">'
        + varr(x(far), y(rep["p"]), y(W[far]["c"]), TEAL_D) + '</g>',
        '<g id="awyt" opacity="0">'
        # والوسمُ في فراغ اللوحة الأعلى لا بجانب سهمه: بجانبه يعبر عنقودَ
        # المستويات التسعة كلَّه (رُئي في إطار 14.4).
        + htext(x(11), PT + PH * 0.13,
                f'{xr(X.J_AWAY)} وسيطَ المدى بخمس شمعات', TEAL_D, 27)
        + '</g>',
        f'<g id="crsc" opacity="0">{crs}</g>',
        '<g id="crst" opacity="0">'
        + htext(x(9), y(min(e["p"] for e in BOTH)) + 100,
                f'{ar(len(BOTH))} من {ar(len(BOTH))} عُبرت بإغلاق',
                RED, 30) + '</g>',
        checkmark(x(n - 3), y(max(e["p"] for e in LV)) - 92, id="ck"),
    ]
    # النافذةُ ضيّقةٌ وخطوطُها تسعة، فلو بقي كلُّ وسمٍ إلى آخر الريل
    # تراكبت أربعةُ نصوصٍ فوق بعضها (رُئي في إطار 18.2). فالوسمُ يظهر
    # وحدَه في طوره ثم يختفي، والأشكالُ وحدَها تتراكم.
    marks = ([(f"v{k}", 6.7 + k * 0.16, 7.2 + k * 0.16, "draw")
              for k in range(len(LV))]
             + [("nonl", 8.2, 8.7, "pop"), ("nont", 8.2, 8.7, "pop", 8.9, 0.3),
                ("botl", 9.2, 9.8, "pop"),
                ("bott", 9.2, 9.8, "pop", 10.2, 0.3),
                ("mosc", 10.6, 11.2, "pop"),
                ("most", 10.6, 11.2, "pop", 13.5, 0.4),
                ("awyl", 13.9, 14.5, "pop"),
                ("awyt", 13.9, 14.5, "pop", 17.1, 0.4),
                ("crsc", 17.3, 17.9, "pop"), ("crst", 17.3, 17.9, "pop"),
                ("ck", 20.3, 20.7, "pop")])
    full = ["nonl", "nont", "botl", "bott", "mosc", "most",
            "awyl", "awyt", "crsc", "crst", "ck"]
    draw = [f"v{k}" for k in range(len(LV))]
    sfx = [("whoosh", 0.35, -3), ("tick", 2.60, -7), ("pop", 3.55, -5),
           ("whoosh", 6.65, -4), ("pop", 8.25, -4), ("pop", 9.25, -4),
           ("pop", 10.65, -4), ("riser", 12.8, -6), ("impact", 13.95, -1),
           ("pop", 17.35, -4), ("success", 20.35, -2)]
    return ("".join(ex), marks, full, draw, (17.3, 17.8), sfx, 22)


MARKUP = {"tasalsul": markup_tasalsul, "jihatayn": markup_jihatayn}


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
    with open(os.path.join(CONT, f"run72_{slug}.json"), encoding="utf-8") as f:
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
    out = os.path.join(HERE, f"reel72_{slug}.html")
    n = build_reel(cfg, out)
    print(f'{slug:<8} ريل {DUR}s · بيتات {len(beats)} · ماركب {len(marks)} · '
          f'نافذة {r["slug"]} · {n} bytes')
    return out, sfx


if __name__ == "__main__":
    for s in (sys.argv[1:] or list(MARKUP)):
        out, sfx = build(s)
        json.dump(sfx, open(os.path.join(HERE, f"reel72_{s}_sfx.json"), "w"),
                  ensure_ascii=False)
