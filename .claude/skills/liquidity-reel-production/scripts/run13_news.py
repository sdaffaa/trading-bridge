# -*- coding: utf-8 -*-
# run13 — ريل «الخبر يسرّع الوصول إلى الهدف» وفق V2 + نظام الصوت H
# الفكرة: الخبر لا يصنع الاتجاه — يضغط زمن الحركة القائمة. ومعه يتسع السبريد ويحدث الانزلاق.
import os
from reel_build import INK, TEAL, TEAL_D, RED, GREY, htext, gen
from reel_sfx_kit import build_reel, geom, line_el, checkmark, zone_el, ring
from run9_reels import shift_cfg
import chart_registry

HERE = os.path.dirname(os.path.abspath(__file__))
VIDEO = "run13-news-accel"

N = 40
SEED = 4801
ANCH = [(0, 12.4), (4, 11.6), (8, 12.2), (11, 11.4), (14, 12.0), (18, 12.6),
        (22, 12.9), (26, 13.2), (28, 13.4), (31, 16.4), (34, 17.6), (39, 18.2)]
chart_registry.assert_fresh_synthetic(SEED, ANCH, label="ريل تسريع الخبر")
W_ = gen(ANCH, N, SEED, wick=0.8)

IZ0, IZ1 = 10, 12          # منطقة الدخول
IE = 13                    # شمعة الدخول
INEWS = 28                 # لحظة صدور الخبر
RNG = max(c["h"] for c in W_) - min(c["l"] for c in W_)

# تذبذب بطيء بين الدخول والخبر: تقليص الأجسام والفتائل (ساعات من الزحف)
mid = sum(W_[j]["c"] for j in range(IE, INEWS)) / (INEWS - IE)
for j in range(IE + 1, INEWS):
    for k in ("o", "c", "h", "l"):
        W_[j][k] = mid + (W_[j][k] - mid) * 0.42

# اندفاع ما بعد الخبر: أربع شمعات تقطع المسافة المتبقية
prev = W_[INEWS - 1]["c"]
for i, j in enumerate(range(INEWS, INEWS + 4)):
    step = RNG * (0.20 if i == 0 else 0.16)
    W_[j].update(o=prev, c=prev + step, h=prev + step + RNG * 0.035, l=prev - RNG * 0.018)
    prev = W_[j]["c"]
TGT = W_[INEWS + 3]["c"] + RNG * 0.01
for j in range(INEWS + 4, N):     # ما بعد الهدف: استقرار فوقه
    lo = TGT + RNG * 0.005
    W_[j]["l"] = max(W_[j]["l"], lo)
    W_[j]["o"] = max(W_[j]["o"], lo); W_[j]["c"] = max(W_[j]["c"], lo)
    W_[j]["h"] = max(W_[j]["h"], max(W_[j]["o"], W_[j]["c"]) + RNG * 0.01)

ZT = max(max(c["o"], c["c"]) for c in W_[IZ0:IZ1 + 1])
ZB = min(c["l"] for c in W_[IZ0:IZ1 + 1])
SL = ZB - RNG * 0.05
assert all(c["l"] > SL for c in W_[IE:]), "شمعة لامست الوقف!"

x, y, slot = geom(W_)
ex = []
zx0 = x(IZ0) - slot * 0.5; zx1 = x(IE + 2) + slot * 0.5
ex.append(zone_el("zone", zx0, y(ZT), zx1, y(ZB),
                  htext((zx0 + zx1) / 2, y(ZT) - 16, "منطقة الدخول", TEAL_D, 22)))
ex.append(ring("circ", x(IE), y(W_[IE]["l"]), 15, TEAL_D,
               htext(x(IE) + slot * 3.4, y(W_[IE]["l"]) + 44, "الدخول بشرطك", TEAL_D, 23)))
ex.append(line_el(x(IE) - slot * 0.5, y(TGT), x(N - 1) + slot * 0.5, y(TGT), TEAL_D, 1.8, dash="3 6", id="tgt"))
ex.append(f'<g id="tgtlbl" opacity="0">{htext(x(IE + 5), y(TGT) - 14, "الهدف", TEAL_D, 23)}</g>')
# شريحة الزحف البطيء
gx = x((IE + INEWS) / 2)
gy = y(max(c["h"] for c in W_[IE + 1:INEWS])) - 96
ex.append(f'<g id="grind" opacity="0"><rect x="{gx-slot*4.2:.1f}" y="{gy:.1f}" width="{slot*8.4:.1f}" height="40" '
          f'fill="#F2EEE7" stroke="{GREY}" stroke-width="1.2"/>'
          + htext(gx, gy + 28, "ساعات من الزحف", GREY, 21) + '</g>')
# خط لحظة الخبر (رأسي)
nx = x(INEWS) - slot * 0.55
ex.append(line_el(nx, 30, nx, 792, INK, 2.0, dash="7 6", id="nws"))
ex.append(f'<g id="nwslbl" opacity="0">{htext(nx - slot * 2.6, 58, "صدور الخبر", INK, 24)}</g>')
# تحذير التكلفة
wx = x(32)
ex.append(f'<g id="warn" opacity="0"><rect x="{wx-slot*5.2:.1f}" y="{y(TGT)+108:.1f}" width="{slot*10.4:.1f}" height="42" '
          f'fill="#F8ECEC" stroke="{RED}" stroke-width="1.3"/>'
          + htext(wx, y(TGT) + 137, "يتسع السبريد… ويحدث الانزلاق", RED, 22) + '</g>')
ex.append(checkmark(x(INEWS + 3) + slot * 1.4, y(TGT) - 30, id="ck"))
ex.append(f'<g id="reslbl" opacity="0">{htext(x(35), y(max(c["h"] for c in W_[34:])) - 22, "تحقق في دقائق", TEAL_D, 27)}</g>')

story = [(i, round(2.3 + (i - 14) * 0.42, 2)) for i in range(14, 18)]          # ما بعد الدخول
story += [(i, round(6.0 + (i - 18) * 0.30, 2)) for i in range(18, 28)]         # الزحف البطيء
story += [(i, round(10.7 + (i - 28) * 0.30, 2)) for i in range(28, 32)]        # اندفاع الخبر
story += [(i, round(12.3 + (i - 32) * 0.22, 2)) for i in range(32, 40)]        # الاستقرار فوق الهدف

cfg = dict(
    w=W_, base=13, openmax=38, open_t=[[39, 0.35]], story=story,
    extra_svg="".join(ex),
    marks=[["zone", 2.6, 3.4, "zone"], ["circ", 3.6, 4.0, "ring"],
           ["tgt", 4.6, 5.1, "draw"], ["tgtlbl", 5.1, 5.35, "pop"],
           ["grind", 7.4, 7.75, "pop"],
           ["nws", 9.9, 10.3, "draw"], ["nwslbl", 10.3, 10.55, "pop"],
           ["ck", 13.4, 13.7, "pop"], ["reslbl", 13.7, 14.0, "pop"],
           ["warn", 15.2, 15.55, "pop"]],
    fullset=["zone", "circ", "tgtlbl", "grind", "nwslbl", "ck", "reslbl", "warn"],
    drawset=["tgt", "nws"],
    txt=[("t2", 2.45, 4.4, "الخبر لا يصنع الاتجاه…<br>بل يضغط زمنه", 50, INK),
         ("t3", 4.65, 6.6, "صفقتك كانت صحيحة<br>قبل صدوره", 52, INK),
         ("t4", 6.85, 9.6, "الهدف كان يحتاج ساعات<br>من الزحف", 50, INK),
         ("t5", 9.85, 13.2, "ثم صدر الخبر…<br>فقُطعت المسافة في دقائق", 48, INK),
         ("t6", 13.45, 15.9, "لكن التسارع سلاح ذو حدين", 50, INK),
         ("t7", 16.15, 18.4, "صغّر الحجم قبل الخبر…<br>لا تدخل بسببه", 48, INK)],
    chip="الأخبار والتسارع · لغرض تعليمي",
    res="الخبر يسرّع هدفك… ولا يصنعه",
    cta_k="اكتب «خبر»", cta_s="ليصلك دليل التعامل مع الأخبار على الخاص",
    edu="لغرض تعليمي — مثال تخطيطي",
    dur=21.0, res_t=18.9, cta_t=20.4, flash=(10.5, 11.15), punch=(10.45, 11.75, 0.05),
    punch_origin="60% 45%", rflash=None,
    intro=dict(eyeb="درس تطبيقي — الأخبار وإدارة الصفقة",
               hook="هدفك يحتاج ساعات…<br>والخبر دقائق",
               sub="كيف يضغط الخبر زمن الحركة — وكيف ينقلب عليك", t=2.5))

fxn = lambda i: x(i) / 1000
fyn = lambda p: y(p) / 820
cfg["cam"] = [
    [0.0, 1.03, .5, .5], [2.3, 1.05, .5, .5, "creep"],
    [2.9, 1.85, fxn((IZ0 + IE) / 2), fyn((ZT + ZB) / 2), "anticip"],
    [4.9, 1.55, fxn(IE + 6), fyn(TGT), "creep"],
    [7.2, 1.75, fxn((IE + INEWS) / 2), fyn(mid), "creep"],
    [10.0, 1.9, fxn(INEWS), fyn(W_[INEWS]["o"]), "anticip"],
    [11.0, 1.35, fxn(INEWS + 2), fyn((W_[INEWS]["o"] + TGT) / 2), "whip", -1.1],
    [13.3, 1.6, fxn(INEWS + 4), fyn(TGT), "creep", 0],
    [15.4, 1.32, fxn(INEWS), fyn(TGT), "creep"],
    [18.6, 1.12, .5, .48, "creep"], [20.2, 1.02, .5, .5, "creep"], [21.0, 1.03, .5, .5, "creep"]]

shift_cfg(cfg)
print("news html:", build_reel(cfg, "reel13_news.html"),
      "| dur", cfg["dur"], "| flash", cfg["flash"], "| cta", cfg["cta_t"])
chart_registry.register_synthetic(VIDEO, [(SEED, ANCH, "ريل تسريع الخبر")])
print("registered")
