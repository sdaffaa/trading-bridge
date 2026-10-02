# -*- coding: utf-8 -*-
# run14 — الريل الفيروسي «وقفك يرسل عنوانك للسوق» (مخطط content/reel_viral_stops.md)
# قمم متساوية ← تراكم أوامر الوقف ← سحب السيولة ← انهيار ← الحل الثلاثي · صوت Pack H
import os
from reel_build import INK, TEAL, TEAL_D, RED, GREY, MUTE, htext, gen
from reel_sfx_kit import build_reel, geom, line_el, xmark, checkmark, ring
from run9_reels import shift_cfg
import chart_registry

HERE = os.path.dirname(os.path.abspath(__file__))
VIDEO = "run14-stop-liquidity"

N = 40
SEED = 4901
ANCH = [(0, 12.0), (4, 13.4), (8, 12.6), (12, 14.6), (15, 13.2), (18, 14.6),
        (21, 13.4), (24, 14.6), (26, 14.0), (27, 15.2), (30, 12.4), (33, 11.0), (39, 10.2)]
chart_registry.assert_fresh_synthetic(SEED, ANCH, label="ريل سيولة الوقف")
W_ = gen(ANCH, N, SEED, wick=0.8)

HI = [12, 18, 24]            # القمم الثلاث المتساوية
ISW = 27                     # شمعة سحب السيولة
RNG = max(c["h"] for c in W_) - min(c["l"] for c in W_)
HL = max(W_[i]["h"] for i in HI)                       # مستوى القمم المتساوية

# فرض التساوي البصري + منع أي شمعة أخرى من تجاوز المستوى قبل السحب
for i in HI:
    W_[i]["h"] = HL
    W_[i]["c"] = min(W_[i]["c"], HL - RNG * 0.035)
    W_[i]["o"] = min(W_[i]["o"], HL - RNG * 0.02)
for j in range(0, ISW):
    if j not in HI:
        cap = HL - RNG * 0.022
        W_[j]["h"] = min(W_[j]["h"], cap)
        W_[j]["o"] = min(W_[j]["o"], W_[j]["h"]); W_[j]["c"] = min(W_[j]["c"], W_[j]["h"])

# شمعة السحب: تخترق المستوى بفتيل ثم تغلق تحته (سحب لا كسر)
o = W_[ISW - 1]["c"]
W_[ISW].update(o=o, h=HL + RNG * 0.055, c=HL - RNG * 0.055, l=HL - RNG * 0.075)
# الانهيار بعدها
prev = W_[ISW]["c"]
for i, j in enumerate(range(ISW + 1, ISW + 6)):
    step = RNG * (0.13 if i == 0 else 0.10)
    W_[j].update(o=prev, c=prev - step, h=prev + RNG * 0.018, l=prev - step - RNG * 0.03)
    prev = W_[j]["c"]
for j in range(ISW + 6, N):
    cap = W_[ISW + 5]["c"] + RNG * 0.03
    W_[j]["h"] = min(W_[j]["h"], cap)
    W_[j]["o"] = min(W_[j]["o"], cap); W_[j]["c"] = min(W_[j]["c"], cap)
    W_[j]["l"] = min(W_[j]["l"], W_[j]["c"] - RNG * 0.01)

x, y, slot = geom(W_)
IENT = ISW + 2               # الدخول بعد السحب (البيع)
SAFE = HL + RNG * 0.085      # الوقف الآمن خلف القمة الأبعد

ex = []
# مستوى القمم + الدوائر الثلاث
ex.append(line_el(x(HI[0]) - slot * 1.2, y(HL), x(ISW) + slot * 1.6, y(HL), INK, 2.0, id="eq"))
ex.append(f'<g id="eqlbl" opacity="0">{htext(x(HI[0]) - slot * 2.8, y(HL) + 32, "قمم متساوية", INK, 23)}</g>')
for k, i in enumerate(HI):
    ex.append(ring(f"r{k}", x(i), y(HL), 13, TEAL_D))

# تراكم أوامر الوقف: أربعة صفوف من الشرطات الحمراء فوق المستوى
ROWX = [x(HI[0]) - slot * 0.8 + slot * 0.62 * k for k in range(26)]
for row in range(4):
    yy = y(HL) - 9 - row * 9
    dashes = "".join(
        f'<line x1="{xx:.1f}" y1="{yy:.1f}" x2="{xx+slot*0.40:.1f}" y2="{yy:.1f}" '
        f'stroke="{RED}" stroke-width="3" stroke-linecap="round" opacity="{0.85-row*0.12:.2f}"/>'
        for xx in ROWX[::1 if row % 2 == 0 else 1])
    ex.append(f'<g id="stk{row}" opacity="0">{dashes}</g>')
ex.append(f'<g id="stklbl" opacity="0">{htext(x(HI[1]), y(HL) - 62, "أوامر وقف متراكمة", RED, 23)}</g>')

# سهم المشترين من الأسفل نحو الكتلة
ax_ = x(ISW) - slot * 0.2
ex.append(line_el(ax_, y(W_[ISW]["l"]) + 120, ax_, y(HL) + 22, TEAL_D, 2.2, dash="6 5", id="arr"))
ex.append(f'<g id="arrlbl" opacity="0">'
          f'<polygon points="{ax_:.1f},{y(HL)+14:.1f} {ax_-8:.1f},{y(HL)+32:.1f} {ax_+8:.1f},{y(HL)+32:.1f}" fill="{TEAL_D}"/>'
          + htext(ax_ - slot * 3.4, y(W_[ISW]["l"]) + 118, "من يبيع يحتاج مشترين", TEAL_D, 22) + '</g>')

# السحب ثم الانهيار
ex.append(f'<g id="swplbl" opacity="0">{htext(x(ISW) - slot * 3.2, y(HL) - 34, "سحب السيولة", RED, 24)}</g>')
ex.append(xmark(x(ISW + 3), y(W_[ISW + 3]["c"]) + 18, id="xd", r=14))
ex.append(f'<g id="xdlbl" opacity="0">{htext(x(ISW + 3) - slot * 3.2, y(W_[ISW + 3]["c"]) + 62, "بلا عودة", RED, 23)}</g>')

# الحل: الوقف الآمن + الدخول بعد السحب
ex.append(line_el(x(HI[0]) - slot * 1.0, y(SAFE), x(N - 1) + slot * 0.5, y(SAFE), TEAL_D, 1.9, dash="4 6", id="safe"))
ex.append(f'<g id="safelbl" opacity="0">{htext(x(HI[1] + 3), y(SAFE) - 14, "الوقف خلف القمة الأبعد ✓", TEAL_D, 23)}</g>')
ex.append(ring("ent", x(IENT), y(W_[IENT]["o"]), 15, TEAL_D,
               htext(x(IENT) + slot * 4.6, y(W_[IENT]["o"]) + 8, "الدخول بعد السحب", TEAL_D, 22)))
ex.append(checkmark(x(35), y(W_[35]["c"]) - 34, id="ck"))
ex.append(f'<g id="reslbl" opacity="0">{htext(x(31), y(W_[36]["c"]) + 58, "خلف السيولة… لا أمامها", TEAL_D, 26)}</g>')

story = [(ISW, 12.2)]
story += [(j, round(13.35 + (j - ISW - 1) * 0.24, 2)) for j in range(ISW + 1, ISW + 6)]
story += [(j, round(14.75 + (j - ISW - 6) * 0.20, 2)) for j in range(ISW + 6, N)]

cfg = dict(
    w=W_, base=26, openmax=38, open_t=[[39, 0.35]], story=story,
    extra_svg="".join(ex),
    marks=[["eq", 2.6, 3.15, "draw"], ["eqlbl", 3.15, 3.4, "pop"],
           ["r0", 3.4, 3.65, "ring"], ["r1", 3.6, 3.85, "ring"], ["r2", 3.8, 4.05, "ring"],
           ["stk0", 4.8, 5.05, "pop", 12.55, 0.30], ["stk1", 5.05, 5.3, "pop", 12.75, 0.30],
           ["stk2", 5.3, 5.55, "pop", 12.95, 0.30], ["stk3", 5.55, 5.8, "pop", 13.15, 0.30],
           ["stklbl", 6.0, 6.3, "pop", 12.6, 0.35],
           ["arr", 9.3, 9.9, "draw", 13.0, 0.4], ["arrlbl", 9.9, 10.2, "pop", 13.0, 0.4],
           ["swplbl", 12.65, 12.95, "pop", 16.4, 0.5],
           ["xd", 14.5, 14.85, "pop"], ["xdlbl", 14.85, 15.15, "pop", 18.4, 0.5],
           ["safe", 19.2, 19.8, "draw"], ["safelbl", 19.8, 20.1, "pop"],
           ["ent", 21.9, 22.3, "ring"],
           ["ck", 25.2, 25.5, "pop"], ["reslbl", 25.5, 25.8, "pop"]],
    fullset=["eqlbl", "r0", "r1", "r2", "stk0", "stk1", "stk2", "stk3", "stklbl",
             "arrlbl", "swplbl", "xd", "xdlbl", "safelbl", "ent", "ck", "reslbl"],
    drawset=["eq", "arr", "safe"],
    txt=[("t2", 2.45, 4.4, "ثلاث قمم متساوية", 54, INK),
         ("t3", 4.65, 6.5, "كل بائع وضع وقفه فوقها", 50, INK),
         ("t4", 6.75, 8.6, "آلاف الأوامر<br>في نقطة واحدة", 50, INK),
         ("t5", 8.85, 11.0, "الآن انظر من الجهة الأخرى", 50, INK),
         ("t6", 11.25, 13.9, "من يريد البيع يحتاج مشترين…<br>وأكبرهم فوق القمم", 44, INK),
         ("t7", 14.15, 16.2, "لذلك صعد السعر ليأخذها", 50, INK),
         ("t8", 16.45, 18.5, "ثم انهار بلا عودة", 52, INK),
         ("t9", 18.75, 21.0, "لم يصطدك السوق شخصياً…<br>وقفك كان في الطابور", 46, INK),
         ("t10", 21.25, 23.6, "والحل ليس وقفاً أوسع", 50, INK),
         ("t11", 23.85, 25.9, "ضعه خلف القمة الأبعد…<br>أو ادخل بعد السحب", 46, INK)],
    chip="سيولة الوقف · لغرض تعليمي",
    res="خلف السيولة… لا أمامها",
    cta_k="اكتب «سيولة»", cta_s="ليصلك نموذج وضع الوقف خلف السيولة على الخاص",
    edu="لغرض تعليمي — مثال تخطيطي",
    dur=28.0, res_t=26.2, cta_t=27.4, flash=(12.9, 13.55), punch=(12.85, 14.15, 0.055),
    punch_origin="55% 40%", rflash=14.6,
    intro=dict(eyeb="درس تطبيقي — السيولة وإدارة المخاطر",
               hook="وقفك يرسل عنوانك<br>للسوق",
               sub="ليس مجازاً… انظر إلى القمم الثلاث", t=2.5))

fxn = lambda i: x(i) / 1000
fyn = lambda p: y(p) / 820
cfg["cam"] = [
    [0.0, 1.03, .5, .5], [2.3, 1.06, .5, .5, "creep"],
    [3.0, 1.6, fxn(HI[1]), fyn(HL), "anticip"],
    [4.9, 1.95, fxn(HI[1]), fyn(HL) - 0.03, "creep"],
    [8.9, 1.15, .5, .5, "ramp"],
    [9.5, 1.55, fxn(ISW - 2), fyn((HL + W_[ISW]["l"]) / 2), "creep"],
    [12.3, 1.95, fxn(ISW), fyn(HL), "anticip"],
    [13.7, 1.35, fxn(ISW + 3), fyn((HL + W_[ISW + 5]["c"]) / 2), "whip", -1.2],
    [16.3, 1.5, fxn(ISW + 4), fyn(W_[ISW + 4]["c"]), "creep", 0],
    [18.7, 1.08, .5, .5, "creep"],
    [19.4, 1.45, fxn(HI[1] + 4), fyn(SAFE), "creep"],
    [22.0, 1.6, fxn(IENT), fyn(W_[IENT]["o"]), "anticip"],
    [25.4, 1.25, fxn(33), fyn(W_[33]["c"]), "creep"],
    [26.6, 1.1, .5, .48, "creep"], [27.4, 1.02, .5, .5, "creep"], [28.0, 1.03, .5, .5, "creep"]]

shift_cfg(cfg)
print("stops html:", build_reel(cfg, "reel14_stops.html"),
      "| dur", cfg["dur"], "| flash", cfg["flash"], "| cta", cfg["cta_t"])
chart_registry.register_synthetic(VIDEO, [(SEED, ANCH, "ريل سيولة الوقف")])
print("registered")
