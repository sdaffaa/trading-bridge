# -*- coding: utf-8 -*-
# ريل «خطة الألف نقطة» — سكربت فهد الشخصي (2026-08-03)، 8 خطوات على جارت واحد حي
import os
from reel_build import INK, TEAL, TEAL_D, RED, htext, hend, gen
from reel_sfx_kit import build_reel, geom, line_el, xmark, checkmark, zone_el, ring
import chart_registry

HERE = os.path.dirname(os.path.abspath(__file__))

N = 40
SEED = 4400
ANCH = [(0, 16.0), (4, 14.6), (8, 13.4), (12, 13.8), (16, 17.6), (21, 14.6),
        (22, 13.9), (26, 17.2), (30, 19.0), (34, 21.4), (39, 24.0)]
chart_registry.assert_fresh_synthetic(SEED, ANCH, label="run5-alf-noqta")
W_ = gen(ANCH, N, SEED, wick=0.85)
x, y, slot = geom(W_)

# مراسي القصة على الشموع المولدة
IPV = max(range(0, 4), key=lambda j: W_[j]["h"])          # قمة البداية (مستوى الستركجر)
BOSv = W_[IPV]["h"]
IB = next(i for i in range(8, 20) if W_[i]["c"] > BOSv)    # شمعة كسر الستركجر
IZ0, IZ1 = 11, 13                                          # قاعدة الانطلاق (الزون)
ZT = max(max(c["o"], c["c"]) for c in W_[IZ0:IZ1+1])
ZB = min(c["l"] for c in W_[IZ0:IZ1+1])
IE = 22                                                    # شمعة الدخلة (رجعة للزون)
SL = ZB - (max(c["h"] for c in W_) - min(c["l"] for c in W_)) * 0.035   # الستوب تحت الزون
ISEC = 26                                                  # التأمين بعد أول دفعة
T1 = W_[IB]["h"] + (BOSv - ZB) * 0.9                       # هدف 1
RB = 39                                                    # نهاية الحركة (الأهداف الكبيرة)
T2 = W_[36]["h"]

ex = []
# مستوى الستركجر + الكسر
ex.append(line_el(x(IPV)-slot*0.4, y(BOSv), x(IB)+slot*0.75, y(BOSv), INK, 2.0, id="bos"))
ex.append(f'<g id="boslbl" opacity="0">{htext(x((IPV+IB)/2), y(BOSv)-18, "الستركجر انقلب صاعد", INK, 24)}</g>')
# منطقة الاهتمام
zx0 = x(IZ0)-slot*0.5; zx1 = x(min(IE+3, N-1))+slot*0.5
ex.append(zone_el("zone", zx0, y(ZT), zx1, y(ZB), htext((zx0+zx1)/2, (y(ZT)+y(ZB))/2+8, "منطقة الاهتمام", TEAL_D, 23)))
# الستوب والأهداف
ex.append(line_el(x(IE)-slot*2.2, y(SL), x(IE)+slot*2.2, y(SL), RED, 2.0, dash="8 6", id="stop"))
ex.append(f'<g id="stoplbl" opacity="0">{htext(x(IE)-slot*4.6, y(SL)+30, "الستوب", RED, 22)}</g>')
ex.append(line_el(x(IE)-slot*0.5, y(T1), x(31)+slot*0.5, y(T1), TEAL_D, 1.8, dash="2 6", id="t1"))
ex.append(f'<g id="t1lbl" opacity="0">{htext(x(29), y(T1)-12, "هدف 1", TEAL_D, 22)}</g>')
ex.append(line_el(x(IE)-slot*0.5, y(T2), x(38)+slot*0.6, y(T2), TEAL_D, 1.8, dash="2 6", id="t2"))
ex.append(f'<g id="t2lbl" opacity="0">{htext(x(32), y(T2)+30, "هدف 2 — الفريم الكبير", TEAL_D, 22)}</g>')
# شريحة الفوت برنت عند الدخلة
fx0 = x(IE)-slot*2.6; fy0 = y(SL)+44
ex.append(f'<g id="fp" opacity="0"><rect x="{fx0:.1f}" y="{fy0:.1f}" width="{slot*5.2:.1f}" height="40" fill="#F2EEE7" stroke="{TEAL_D}" stroke-width="1.3"/>'
          + htext(fx0+slot*2.6, fy0+28, "الفوت برنت: امتصاص بيع ✓", TEAL_D, 21) + '</g>')
# الدخلة + التأمين + النهاية
ex.append(ring("circ", x(IE), y(W_[IE]["l"]), 16, TEAL_D, htext(x(IE)+slot*3.2, y(W_[IE]["l"])+34, "الدخلة", TEAL_D, 24)))
ex.append(f'<g id="sec" opacity="0">{line_el(x(ISEC)-slot*1.6, y(W_[IE]["l"]), x(ISEC)+slot*1.6, y(W_[IE]["l"]), INK, 2.0)}'
          + htext(x(ISEC), y(W_[IE]["l"])+30, "أمّن — الستوب صار هني", INK, 22) + '</g>')
ex.append(checkmark(x(RB)-slot*0.2, y(W_[RB]["c"])-34, id="ck"))
ex.append(f'<g id="reslbl" opacity="0">{htext(x(35), y(max(c["h"] for c in W_[36:]))-20, "+1000 نقطة", TEAL_D, 30)}</g>')

# تكشّف الشموع مع الخطوات
story = [(i, round(2.5 + (i-13)*0.45, 2)) for i in range(13, 17)]           # الستركجر
story += [(i, round(5.0 + (i-17)*0.35, 2)) for i in range(17, 22)]          # الرجعة للزون
story += [(22, 11.9)]                                                        # شمعة الدخلة
story += [(i, round(13.6 + (i-23)*0.45, 2)) for i in range(23, 28)]         # الدفعة الأولى
story += [(i, round(16.0 + (i-28)*0.16, 2)) for i in range(28, 40)]         # امتداد الفريم الكبير

TXT = [
 ("t1", 0.35, 2.2, "خلني أعلمك أربح<br>أكثر من 1000 نقطة أسبوعيًا", 56, INK),
 ("t2", 2.45, 4.6, "1 — افتح الجارت…<br>وحدد الماركت ستركجر", 52, INK),
 ("t3", 4.85, 6.9, "2 — حدد مناطق الاهتمام", 52, INK),
 ("t4", 7.15, 9.2, "3 — حدد الستوب والأهداف<br>قبل أي شي", 50, INK),
 ("t5", 9.45, 11.6, "4 — تابع الفوت برنت<br>بنماذجك الخاصة", 50, INK),
 ("t6", 11.85, 13.3, "5 — ادخل الصفقة", 54, INK),
 ("t7", 13.55, 15.7, "6 — أمّن بعد ربح معين…<br>خلاص ما تخسر", 48, INK),
 ("t8", 15.95, 17.9, "7 — خلها تروح حق أهدافك<br>بالفريمات الكبيرة", 48, INK),
]

fxn = lambda i: x(i) / 1000
fyn = lambda p: y(p) / 820

cfg = dict(
  w=W_, base=12, openmax=38, open_t=[[39, 0.35]], story=story,
  extra_svg="".join(ex),
  marks=[["bos", 2.7, 3.3, "draw"], ["boslbl", 3.3, 3.6, "pop"],
         ["zone", 5.0, 5.9, "zone"],
         ["stop", 7.3, 7.8, "draw"], ["stoplbl", 7.8, 8.05, "pop"],
         ["t1", 8.0, 8.5, "draw"], ["t1lbl", 8.5, 8.75, "pop"],
         ["t2", 16.1, 16.6, "draw"], ["t2lbl", 16.6, 16.85, "pop"],
         ["fp", 9.6, 9.95, "pop"],
         ["circ", 12.0, 12.4, "ring"],
         ["sec", 13.8, 14.15, "pop"],
         ["ck", 17.35, 17.65, "pop"], ["reslbl", 17.65, 17.95, "pop"]],
  fullset=["boslbl", "zone", "stoplbl", "t1lbl", "t2lbl", "fp", "circ", "sec", "ck", "reslbl"],
  drawset=["bos", "stop", "t1", "t2"],
  txt=TXT, chip="خطتي الأسبوعية · لغرض تعليمي",
  res="مبروك عليك… 1000 نقطة بالأسبوع",
  cta_k="اكتب «1000»", cta_s="ويوصلك دليل الخطوات الثمان كامل على الخاص",
  edu="لغرض تعليمي — مثال تخطيطي",
  dur=22.2, res_t=18.25, cta_t=19.7, flash=(13.35, 14.0), punch=(13.3, 14.6, 0.05),
  punch_origin="55% 45%", rflash=6.0)

cfg["cam"] = [
  [0.0, 1.03, .5, .5], [2.3, 1.05, .5, .5],
  [2.9, 1.7, fxn(IB), fyn(BOSv)],                       # زوم على الكسر/الستركجر
  [5.2, 1.85, fxn((IZ0+IE)/2), fyn((ZT+ZB)/2)],         # منطقة الاهتمام
  [7.5, 1.5, fxn(IE), fyn(SL)],                        # الستوب والأهداف
  [9.7, 1.9, fxn(IE), fyn(ZB)],                         # لصق على الفوت برنت
  [11.9, 1.95, fxn(IE), fyn(W_[IE]["l"])],              # الدخلة
  [13.8, 1.65, fxn(ISEC), fyn(W_[IE]["l"])],            # التأمين (فوقه البانش)
  [16.2, 1.3, fxn(32), fyn(W_[32]["c"])],               # بان مع الامتداد
  [17.9, 1.12, .5, .48], [19.4, 1.02, .5, .5], [22.2, 1.03, .5, .5]]

print("alf html:", build_reel(cfg, "reel_alf.html"), "| IB", IB, "BOSv", round(BOSv, 2))
chart_registry.register_synthetic("run5-alf-noqta", [(SEED, ANCH, "ريل خطة الألف نقطة")])
print("registered")
