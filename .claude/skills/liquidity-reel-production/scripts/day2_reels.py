# -*- coding: utf-8 -*-
"""ريلات يوم 2026-08-04 الثلاثة (V2 + صوت Pack H).
كل ريل: افتتاحية داكنة → Light Sweep → قصة على جارت حي → خلاصة → CTA.
النصوص من content/day2_*.json (مفتاح reel).
"""
import json, os, sys
from reel_build import INK, TEAL, TEAL_D, RED, GREY, htext, gen
from reel_sfx_kit import build_reel, geom, line_el, xmark, checkmark, zone_el, ring
from run9_reels import shift_cfg
import chart_registry

HERE = os.path.dirname(os.path.abspath(__file__))
CONT = os.path.join(HERE, "..", "content")
REG = []

def load(key):
    with open(os.path.join(CONT, f"day2_{key}.json"), encoding="utf-8") as f:
        return json.load(f)["reel"]

def txt_beats(lines, spans):
    """يوزّع أسطر الايجنت على نوافذ زمنية محددة مسبقاً."""
    out = []
    for i, (a, b, fs) in enumerate(spans):
        if i >= len(lines):
            break
        out.append((f"t{i+2}", a, b, lines[i], fs, INK))
    return out

# ═════════ 1) السيولة الداخلية والخارجية ═════════
def build_internal():
    R = load("internal")
    N, SEED = 36, 5401
    ANCH = [(0, 11.0), (3, 13.9), (7, 12.5), (11, 13.7), (15, 12.4), (19, 13.7),
            (22, 12.9), (25, 14.2), (28, 15.2), (32, 16.0), (35, 16.6)]
    chart_registry.assert_fresh_synthetic(SEED, ANCH, label="ريل السيولة الداخلية")
    W = gen(ANCH, N, SEED, wick=0.8)
    RNG = max(c["h"] for c in W) - min(c["l"] for c in W)
    IEQ, IEXT, ISW = (11, 19), 3, 24
    EXT = W[IEXT]["h"] + RNG * 0.02
    W[IEXT]["h"] = EXT
    INT = max(W[i]["h"] for i in IEQ)
    for i in IEQ:
        W[i]["h"] = INT; W[i]["c"] = min(W[i]["c"], INT - RNG * 0.03)
    for j in range(IEXT + 1, ISW):
        if j not in IEQ:
            cap = INT - RNG * 0.022
            W[j]["h"] = min(W[j]["h"], cap)
            W[j]["o"] = min(W[j]["o"], cap); W[j]["c"] = min(W[j]["c"], cap)
    o = W[ISW - 1]["c"]
    W[ISW].update(o=o, h=INT + RNG * 0.045, c=INT + RNG * 0.02, l=o - RNG * 0.02)
    prev = W[ISW]["c"]
    for i, j in enumerate(range(ISW + 1, N)):
        step = RNG * (0.11 if i < 5 else 0.02)
        c = min(prev + step, EXT + RNG * 0.03)
        W[j].update(o=prev, c=c, h=c + RNG * 0.02, l=prev - RNG * 0.015); prev = c
    x, y, slot = geom(W)
    ex = []
    ex.append(line_el(x(IEQ[0]) - slot * 1.4, y(INT), x(ISW) + slot * 1.4, y(INT), RED, 2.0, dash="7 5", id="intl"))
    ex.append(f'<g id="intlbl" opacity="0">{htext(x(17), y(INT) - 18, "سيولة داخلية", RED, 23)}</g>')
    for k, i in enumerate(IEQ):
        ex.append(ring(f"e{k}", x(i), y(INT), 13, RED))
    ex.append(line_el(x(IEXT) - slot * 1.0, y(EXT), x(N - 1) + slot * 0.5, y(EXT), INK, 2.2, id="extl"))
    ex.append(f'<g id="extlbl" opacity="0">{htext(x(20), y(EXT) - 18, "سيولة خارجية — الهدف", INK, 23)}</g>')
    ex.append(xmark(x(ISW), y(INT) - 26, id="sw", r=15))
    ex.append(f'<g id="swlbl" opacity="0">{htext(x(ISW) - slot * 3.6, y(INT) - 60, "أخذها أولاً", RED, 23)}</g>')
    ex.append(checkmark(x(33), y(EXT) + 34, id="ck"))
    ex.append(f'<g id="reslbl" opacity="0">{htext(x(30), y(EXT) + 78, "ثم اتجه للخارجية", TEAL_D, 25)}</g>')
    story = [(ISW, 9.6)] + [(j, round(10.8 + (j - ISW - 1) * 0.26, 2)) for j in range(ISW + 1, N)]
    cfg = dict(
        w=W, base=23, openmax=34, open_t=[[35, 0.35]], story=story,
        extra_svg="".join(ex),
        marks=[["intl", 2.6, 3.2, "draw"], ["intlbl", 3.2, 3.45, "pop"],
               ["e0", 3.5, 3.75, "ring"], ["e1", 3.7, 3.95, "ring"],
               ["extl", 5.6, 6.2, "draw"], ["extlbl", 6.2, 6.45, "pop"],
               ["sw", 9.9, 10.25, "drawx"], ["swlbl", 10.25, 10.5, "pop", 14.2, 0.5],
               ["ck", 13.2, 13.5, "pop"], ["reslbl", 13.5, 13.8, "pop"]],
        fullset=["intlbl", "e0", "e1", "extlbl", "sw", "swlbl", "ck", "reslbl"],
        drawset=["intl", "extl"],
        txt=txt_beats(R["lines"], [(2.45, 4.5, 50), (4.75, 6.9, 50), (7.15, 9.4, 48),
                                   (9.65, 11.9, 48), (12.15, 14.4, 48), (14.65, 16.6, 48)]),
        chip="السيولة الداخلية والخارجية · لغرض تعليمي",
        res=R["res"], cta_k="اكتب «داخلية»", cta_s=R["cta_s"],
        edu="لغرض تعليمي — مثال تخطيطي",
        dur=22.0, res_t=17.0, cta_t=18.4, flash=(9.9, 10.55), punch=(9.85, 11.15, 0.05),
        punch_origin="55% 40%", rflash=10.0,
        intro=dict(eyeb="درس تطبيقي — مفاهيم السيولة", hook=R["hook"], sub=R["sub"], t=2.5))
    fx = lambda i: x(i) / 1000; fy = lambda p: y(p) / 820
    cfg["cam"] = [[0.0, 1.03, .5, .5], [2.3, 1.06, .5, .5, "creep"],
                  [3.0, 1.7, fx(15), fy(INT), "anticip"],
                  [5.8, 1.45, fx(12), fy((INT + EXT) / 2), "creep"],
                  [9.6, 1.9, fx(ISW), fy(INT), "anticip"],
                  [11.2, 1.4, fx(29), fy((INT + EXT) / 2), "whip", -1.1],
                  [13.4, 1.5, fx(32), fy(EXT), "creep", 0],
                  [17.2, 1.12, .5, .48, "creep"], [18.6, 1.02, .5, .5, "creep"], [22.0, 1.03, .5, .5, "creep"]]
    shift_cfg(cfg)
    print("internal reel:", build_reel(cfg, "reel_day2_internal.html"), "| dur", cfg["dur"], "| flash", cfg["flash"], "| cta", cfg["cta_t"])
    REG.append((SEED, ANCH, "ريل السيولة الداخلية"))
    return cfg["dur"], cfg["flash"][0], cfg["cta_t"]

# ═════════ 2) التأكيد ═════════
def build_confirm():
    R = load("confirm")
    N, SEED = 34, 5402
    ANCH = [(0, 16.0), (4, 14.6), (8, 13.4), (11, 13.8), (15, 15.6), (19, 14.6),
            (23, 13.7), (26, 15.0), (30, 16.2), (33, 17.0)]
    chart_registry.assert_fresh_synthetic(SEED, ANCH, label="ريل التأكيد")
    W = gen(ANCH, N, SEED, wick=0.8)
    RNG = max(c["h"] for c in W) - min(c["l"] for c in W)
    IZ0, IZ1, ITOUCH = 8, 10, 23
    ZT = max(max(c["o"], c["c"]) for c in W[IZ0:IZ1 + 1])
    ZB = min(c["l"] for c in W[IZ0:IZ1 + 1])
    for j in range(IZ1 + 1, ITOUCH):
        W[j]["l"] = max(W[j]["l"], ZT + RNG * 0.02)
        W[j]["o"] = max(W[j]["o"], W[j]["l"]); W[j]["c"] = max(W[j]["c"], W[j]["l"])
        W[j]["h"] = max(W[j]["h"], max(W[j]["o"], W[j]["c"]))
    W[ITOUCH].update(o=ZT + RNG * 0.02, l=ZB + (ZT - ZB) * 0.2, c=ZB + (ZT - ZB) * 0.55)
    W[ITOUCH]["h"] = W[ITOUCH]["o"] + RNG * 0.01
    W[ITOUCH + 1].update(o=W[ITOUCH]["c"], c=ZT + RNG * 0.012,
                         h=ZT + RNG * 0.03, l=W[ITOUCH]["c"] - RNG * 0.012)
    prev = W[ITOUCH + 1]["c"]
    for i, j in enumerate(range(ITOUCH + 2, N)):
        step = RNG * (0.10 if i < 5 else 0.035)
        W[j].update(o=prev, c=prev + step, h=prev + step + RNG * 0.02, l=prev - RNG * 0.015); prev = W[j]["c"]
    SL = ZB - RNG * 0.05
    assert all(c["l"] > SL for c in W[ITOUCH:]), "شمعة لامست الوقف!"
    x, y, slot = geom(W)
    ex = []
    zx0 = x(IZ0) - slot * 0.5; zx1 = x(N - 1) + slot * 0.5
    ex.append(zone_el("zone", zx0, y(ZT), zx1, y(ZB),
                      htext(x(14), (y(ZT) + y(ZB)) / 2 + 8, "المنطقة", TEAL_D, 22)))
    ex.append(f'<g id="touch" opacity="0"><circle cx="{x(ITOUCH):.1f}" cy="{y(W[ITOUCH]["l"]):.1f}" r="14" '
              f'fill="none" stroke="{RED}" stroke-width="2.8"/>'
              + htext(x(ITOUCH) - slot * 3.4, y(W[ITOUCH]["l"]) + 42, "اللمسة ليست دخولاً", RED, 22) + '</g>')
    ex.append(ring("conf", x(ITOUCH + 1), y(W[ITOUCH + 1]["c"]), 15, TEAL_D,
                   htext(x(ITOUCH + 1) + slot * 4.2, y(W[ITOUCH + 1]["c"]) - 6, "إغلاق جسم داخل المنطقة", TEAL_D, 21)))
    ex.append(line_el(zx0, y(SL), x(N - 1) + slot * 0.5, y(SL), RED, 1.7, dash="6 5", id="sl"))
    ex.append(f'<g id="sllbl" opacity="0">{htext(x(17), y(SL) + 30, "الوقف خلف المنطقة", RED, 21)}</g>')
    ex.append(checkmark(x(31), y(W[31]["c"]) - 30, id="ck"))
    ex.append(f'<g id="reslbl" opacity="0">{htext(x(28), y(W[32]["h"]) - 24, "التأكيد قبل التنفيذ", TEAL_D, 25)}</g>')
    story = [(ITOUCH, 9.4), (ITOUCH + 1, 11.2)]
    story += [(j, round(12.6 + (j - ITOUCH - 2) * 0.24, 2)) for j in range(ITOUCH + 2, N)]
    cfg = dict(
        w=W, base=22, openmax=32, open_t=[[33, 0.35]], story=story,
        extra_svg="".join(ex),
        marks=[["zone", 2.6, 3.5, "zone"],
               ["sl", 5.4, 5.9, "draw"], ["sllbl", 5.9, 6.15, "pop"],
               ["touch", 9.7, 10.05, "pop", 13.6, 0.5],
               ["conf", 11.5, 11.9, "ring"],
               ["ck", 14.6, 14.9, "pop"], ["reslbl", 14.9, 15.2, "pop"]],
        fullset=["zone", "touch", "conf", "sllbl", "ck", "reslbl"],
        drawset=["sl"],
        txt=txt_beats(R["lines"], [(2.45, 4.6, 50), (4.85, 7.0, 48), (7.25, 9.3, 48),
                                   (9.55, 11.3, 48), (11.55, 13.9, 46), (14.15, 16.4, 48)]),
        chip="التأكيد قبل التنفيذ · لغرض تعليمي",
        res=R["res"], cta_k="اكتب «تأكيد»", cta_s=R["cta_s"],
        edu="لغرض تعليمي — مثال تخطيطي",
        dur=22.0, res_t=16.8, cta_t=18.2, flash=(11.5, 12.15), punch=(11.45, 12.75, 0.05),
        punch_origin="58% 55%", rflash=9.8,
        intro=dict(eyeb="درس تطبيقي — نموذج التنفيذ", hook=R["hook"], sub=R["sub"], t=2.5))
    fx = lambda i: x(i) / 1000; fy = lambda p: y(p) / 820
    cfg["cam"] = [[0.0, 1.03, .5, .5], [2.3, 1.06, .5, .5, "creep"],
                  [3.0, 1.65, fx(13), fy((ZT + ZB) / 2), "anticip"],
                  [5.6, 1.5, fx(15), fy(SL), "creep"],
                  [9.5, 1.95, fx(ITOUCH), fy(W[ITOUCH]["l"]), "anticip"],
                  [11.4, 1.95, fx(ITOUCH + 1), fy(W[ITOUCH + 1]["c"]), "ramp"],
                  [13.9, 1.45, fx(29), fy(W[29]["c"]), "whip", -1.0],
                  [16.9, 1.12, .5, .48, "creep", 0], [18.4, 1.02, .5, .5, "creep"], [22.0, 1.03, .5, .5, "creep"]]
    shift_cfg(cfg)
    print("confirm reel:", build_reel(cfg, "reel_day2_confirm.html"), "| dur", cfg["dur"], "| flash", cfg["flash"], "| cta", cfg["cta_t"])
    REG.append((SEED, ANCH, "ريل التأكيد"))
    return cfg["dur"], cfg["flash"][0], cfg["cta_t"]

# ═════════ 3) البريكر بلوك ═════════
def build_breaker():
    R = load("breaker")
    N, SEED = 36, 5403
    ANCH = [(0, 17.0), (4, 16.0), (8, 15.4), (12, 16.0), (16, 14.2), (22, 15.4), (27, 13.0), (35, 11.4)]
    chart_registry.assert_fresh_synthetic(SEED, ANCH, label="ريل البريكر")
    W = gen(ANCH, N, SEED, wick=0.8)
    RNG = max(c["h"] for c in W) - min(c["l"] for c in W)
    IOB, IBRK, IRET = 10, 14, 23
    o = W[IOB - 1]["c"]; body = RNG * 0.10
    W[IOB].update(o=o, c=o - body, h=o + body * 0.25, l=o - body * 1.3)
    ZT, ZB = W[IOB]["o"], W[IOB]["c"]
    prev = W[IOB]["c"]
    for j in range(IOB + 1, IBRK):
        step = RNG * 0.05
        W[j].update(o=prev, c=prev + step, h=prev + step + RNG * 0.02, l=prev - RNG * 0.015); prev = W[j]["c"]
    for j in range(IBRK, IRET - 2):
        step = RNG * 0.085
        W[j].update(o=prev, c=prev - step, h=prev + RNG * 0.015, l=prev - step - RNG * 0.025); prev = W[j]["c"]
    for i, j in enumerate(range(IRET - 2, IRET + 1)):
        tgt = ZB + (ZT - ZB) * (0.35 + 0.25 * i)
        W[j].update(o=prev, c=tgt, h=tgt + RNG * 0.018, l=prev - RNG * 0.012); prev = tgt
    for i, j in enumerate(range(IRET + 1, N)):
        step = RNG * (0.10 if i < 4 else 0.045)
        W[j].update(o=prev, c=prev - step, h=prev + RNG * 0.012, l=prev - step - RNG * 0.02); prev = W[j]["c"]
    SLB = ZT + RNG * 0.05
    assert all(c["h"] < SLB for c in W[IRET:]), "شمعة تجاوزت الوقف!"
    x, y, slot = geom(W)
    ex = []
    zx0 = x(IOB) - slot * 0.5; zx1 = x(N - 1) + slot * 0.5
    ex.append(zone_el("blk", zx0, y(ZT), zx1, y(ZB),
                      htext(x(IOB) + slot * 3.0, (y(ZT) + y(ZB)) / 2 - 26, "أوردر بلوك", TEAL_D, 22)))
    ex.append(xmark(x(IBRK + 1), (y(ZT) + y(ZB)) / 2, id="fail", r=14))
    ex.append(f'<g id="faillbl" opacity="0">{htext(x(IBRK + 1) - slot * 3.4, y(ZB) + 44, "فشل واخترقه السعر", RED, 22)}</g>')
    ex.append(line_el(x(IBRK) - slot * 0.6, y(W[IOB]["l"]), x(IRET - 3) + slot * 0.6, y(W[IOB]["l"]), INK, 2.0, id="bos"))
    ex.append(f'<g id="boslbl" opacity="0">{htext(x(IBRK + 2), y(W[IOB]["l"]) + 30, "كسر الهيكل (BOS)", INK, 22)}</g>')
    ex.append(ring("brk", x(IRET), y(W[IRET]["c"]), 15, TEAL_D,
                   htext(x(IRET) - slot * 4.4, y(W[IRET]["c"]) + 8, "بيع من البريكر", TEAL_D, 22)))
    ex.append(line_el(zx0, y(SLB), x(N - 1) + slot * 0.5, y(SLB), RED, 1.7, dash="6 5", id="sl"))
    ex.append(f'<g id="sllbl" opacity="0">{htext(x(19), y(SLB) - 14, "الوقف فوق البريكر", RED, 21)}</g>')
    ex.append(checkmark(x(33), y(W[33]["c"]) + 34, id="ck"))
    ex.append(f'<g id="reslbl" opacity="0">{htext(x(30), y(W[34]["c"]) + 74, "انقلب دوره", TEAL_D, 25)}</g>')
    story = [(j, round(9.4 + (j - IRET + 2) * 0.30, 2)) for j in range(IRET - 2, IRET + 1)]
    story += [(j, round(12.4 + (j - IRET - 1) * 0.24, 2)) for j in range(IRET + 1, N)]
    cfg = dict(
        w=W, base=20, openmax=34, open_t=[[35, 0.35]], story=story,
        extra_svg="".join(ex),
        marks=[["blk", 2.6, 3.5, "zone"],
               ["fail", 4.8, 5.15, "drawx", 10.4, 0.4], ["faillbl", 5.15, 5.4, "pop", 10.4, 0.4],
               ["bos", 6.6, 7.1, "draw"], ["boslbl", 7.1, 7.35, "pop", 11.0, 0.4],
               ["sl", 9.0, 9.5, "draw"], ["sllbl", 9.5, 9.75, "pop"],
               ["brk", 11.9, 12.3, "ring"],
               ["ck", 14.6, 14.9, "pop"], ["reslbl", 14.9, 15.2, "pop"]],
        fullset=["blk", "fail", "faillbl", "boslbl", "sllbl", "brk", "ck", "reslbl"],
        drawset=["bos", "sl"],
        txt=txt_beats(R["lines"], [(2.45, 4.6, 50), (4.85, 6.5, 48), (6.75, 8.8, 48),
                                   (9.05, 11.6, 46), (11.85, 14.4, 48), (14.65, 16.6, 48)]),
        chip="البريكر بلوك · لغرض تعليمي",
        res=R["res"], cta_k="اكتب «بريكر»", cta_s=R["cta_s"],
        edu="لغرض تعليمي — مثال تخطيطي",
        dur=22.0, res_t=16.9, cta_t=18.3, flash=(11.9, 12.55), punch=(11.85, 13.15, 0.05),
        punch_origin="55% 45%", rflash=5.0,
        intro=dict(eyeb="درس تطبيقي — مفاهيم SMC", hook=R["hook"], sub=R["sub"], t=2.5))
    fx = lambda i: x(i) / 1000; fy = lambda p: y(p) / 820
    cfg["cam"] = [[0.0, 1.03, .5, .5], [2.3, 1.06, .5, .5, "creep"],
                  [3.0, 1.75, fx(IOB + 2), fy((ZT + ZB) / 2), "anticip"],
                  [6.4, 1.55, fx(IBRK + 2), fy(W[IOB]["l"]), "creep"],
                  [9.0, 1.5, fx(18), fy(SLB), "creep"],
                  [11.8, 1.9, fx(IRET), fy(W[IRET]["c"]), "anticip"],
                  [13.6, 1.4, fx(29), fy(W[29]["c"]), "whip", 1.1],
                  [15.4, 1.45, fx(32), fy(W[32]["c"]), "creep", 0],
                  [17.0, 1.12, .5, .48, "creep"], [18.5, 1.02, .5, .5, "creep"], [22.0, 1.03, .5, .5, "creep"]]
    shift_cfg(cfg)
    print("breaker reel:", build_reel(cfg, "reel_day2_breaker.html"), "| dur", cfg["dur"], "| flash", cfg["flash"], "| cta", cfg["cta_t"])
    REG.append((SEED, ANCH, "ريل البريكر"))
    return cfg["dur"], cfg["flash"][0], cfg["cta_t"]

BUILDERS = {"internal": build_internal, "confirm": build_confirm, "breaker": build_breaker}

if __name__ == "__main__":
    keys = sys.argv[1:] or list(BUILDERS)
    meta = {}
    for k in keys:
        meta[k] = BUILDERS[k]()
    with open(os.path.join(HERE, "day2_reels_meta.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False)
    chart_registry.register_synthetic("day2-reels-2026-08-04", REG)
    print("registered reels charts:", len(REG))
