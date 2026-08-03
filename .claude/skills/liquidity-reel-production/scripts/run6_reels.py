# -*- coding: utf-8 -*-
# تشغيلة 6 — تحويل وحدات اليوم الثلاث (فومو/باكتست/لوت) إلى ريلز (طلب فهد الصريح 2026-08-03)
import os
from reel_build import INK, TEAL, TEAL_D, RED, htext, hend, gen
from reel_sfx_kit import build_reel, geom, line_el, xmark, checkmark
import chart_registry

HERE = os.path.dirname(os.path.abspath(__file__))
GREY = "#5C6C73"

def chip(x0, y0, w, txt, col, id_, fs=21, fill="#F2EEE7"):
    w2 = max(w, len(txt) * (fs * 0.58))
    x0 -= (w2 - w) / 2
    return (f'<g id="{id_}" opacity="0"><rect x="{x0:.1f}" y="{y0:.1f}" width="{w2:.1f}" height="40" '
            f'fill="{fill}" stroke="{col}" stroke-width="1.3"/>' + htext(x0 + w2/2, y0 + 28, txt, col, fs) + '</g>')

# ================= ريل «فومو» — الملاحقة vs الرجعة =================
SEED = 4501
ANCH = [(0, 10.0), (6, 9.5), (13, 16.8), (16, 14.9), (19, 12.6), (23, 10.7), (27, 10.05), (31, 14.2), (37, 18.9)]
chart_registry.assert_fresh_synthetic(SEED, ANCH, label="run6-fomo")
W_ = gen(ANCH, 38, SEED, wick=0.85)
x, y, slot = geom(W_)
XC = max(range(11, 15), key=lambda j: W_[j]["h"])            # شمعة الملاحقة (القمة)
IZ0, IZ1 = 5, 7                                              # زون الانطلاق
ZT = max(max(c["o"], c["c"]) for c in W_[IZ0:IZ1+1]); ZB = min(c["l"] for c in W_[IZ0:IZ1+1])
ISTP = 17                                                    # طق ستوب اللاحق
IE = 27                                                      # الدخلة الصح
RB = 37

ex = []
ex.append(xmark(x(XC), y(W_[XC]["h"]), id="xc"))
ex.append(f'<g id="xclbl" opacity="0">{htext(x(XC)-slot*2.2, y(W_[XC]["h"])-22, "هني أغروك تلحق", RED, 24)}</g>')
sl_ch = W_[ISTP]["l"]
ex.append(line_el(x(XC)-slot*0.6, y(sl_ch), x(ISTP)+slot*0.8, y(sl_ch), RED, 1.9, dash="7 5", id="chstop"))
ex.append(f'<g id="chstoplbl" opacity="0">{htext(x(ISTP)+slot*0.5, y(sl_ch)+30, "طق ستوب اللاحقين", RED, 22)}</g>')
zx0 = x(IZ0)-slot*0.5; zx1 = x(min(IE+3, 37))+slot*0.5
ex.append(f'<g id="zone" opacity="0"><rect x="{zx0:.1f}" y="{y(ZT):.1f}" width="{zx1-zx0:.1f}" height="{y(ZB)-y(ZT):.1f}" fill="{TEAL}" style="opacity:0.16"/>'
          f'<rect x="{zx0:.1f}" y="{y(ZT):.1f}" width="{zx1-zx0:.1f}" height="{y(ZB)-y(ZT):.1f}" fill="none" stroke="{TEAL_D}" stroke-width="1.6"/>'
          + htext((zx0+zx1)/2, (y(ZT)+y(ZB))/2+8, "زون الانطلاق", TEAL_D, 23) + '</g>')
ex.append(f'<g id="circ" opacity="0"><circle cx="{x(IE):.1f}" cy="{y(W_[IE]["l"]):.1f}" r="16" fill="none" stroke="{TEAL_D}" stroke-width="3.2"/>'
          + htext(x(IE), y(W_[IE]["l"])+38, "الدخلة الصح", TEAL_D, 24) + '</g>')
ex.append(checkmark(x(RB)-slot*0.2, y(W_[RB]["c"])-30, id="ck"))
ex.append(f'<g id="reslbl" opacity="0">{htext(x(33), y(max(c["h"] for c in W_[33:]))-20, "+150 نقطة", TEAL_D, 28)}</g>')

story = [(i, round(2.4 + (i-14)*0.5, 2)) for i in range(14, 19)]
story += [(i, round(7.3 + (i-19)*0.3, 2)) for i in range(19, 27)]
story += [(27, 11.5)] + [(i, round(13.5 + (i-28)*0.28, 2)) for i in range(28, 38)]

cfg = dict(
  w=W_, base=14, openmax=36, open_t=[[37, 0.35]], story=story,
  extra_svg="".join(ex),
  marks=[["xc", 2.6, 2.95, "pop"], ["xclbl", 2.95, 3.2, "pop"],
         ["chstop", 4.8, 5.3, "draw"], ["chstoplbl", 5.3, 5.55, "pop"],
         ["zone", 7.6, 8.1, "fade"],
         ["circ", 11.6, 11.95, "pop"],
         ["ck", 15.4, 15.7, "pop"], ["reslbl", 15.7, 16.0, "pop"]],
  fullset=["xc", "xclbl", "chstoplbl", "zone", "circ", "ck", "reslbl"], drawset=["chstop"],
  txt=[("t1", 0.35, 2.2, "فاتتك شمعة الاندفاع؟<br>وقف… لا تلحقها", 54, INK),
       ("t2", 2.45, 4.5, "هني أغروك تدخل بآخرها…<br>أغلى سعر بالحركة", 50, INK),
       ("t3", 4.75, 7.2, "أول تنفس طبيعي…<br>طق ستوب اللاحقين", 50, INK),
       ("t4", 7.5, 9.6, "الصح: علّم زون الانطلاق<br>وحط تنبيه", 50, INK),
       ("t5", 9.9, 13.2, "الدخلة عند الرجعة…<br>لأن السعر يختبر منطقته قبل يكمل", 46, INK),
       ("t6", 13.5, 15.3, "وإذا ما رجع؟<br>خلها تروح… السوق يفتح باجر", 46, INK)],
  chip="درس الفومو · لغرض تعليمي", res="+150 نقطة للي صبر… وستوب للي لحق",
  cta_k="اكتب «فومو»", cta_s="ويوصلك دليل قاعدة الرجعة — 16 صفحة — على الخاص",
  edu="لغرض تعليمي — مثال تخطيطي",
  dur=21.6, res_t=16.3, cta_t=18.4, flash=(13.6, 14.25), punch=(13.55, 14.85, 0.05),
  punch_origin="62% 55%", rflash=6.2)
fxn = lambda i: x(i)/1000; fyn = lambda p: y(p)/820
cfg["cam"] = [
  [0.0, 1.03, .5, .5], [2.3, 1.05, .5, .5],
  [2.8, 1.85, fxn(XC), fyn(W_[XC]["h"])],
  [5.0, 1.9, fxn(ISTP), fyn(sl_ch)],
  [7.7, 1.75, fxn((IZ0+IE)/2), fyn((ZT+ZB)/2)],
  [11.5, 1.95, fxn(IE), fyn(W_[IE]["l"])],
  [13.9, 1.6, fxn(31), fyn(W_[31]["c"])],
  [16.1, 1.15, .5, .48], [18.1, 1.02, .5, .5], [21.6, 1.03, .5, .5]]
print("fomo html:", build_reel(cfg, "reel_fomo.html"), "| XC", XC)
REG = [(SEED, ANCH, "ريل فومو run6")]

# ================= ريل «باكتست» — عينة الخمسين =================
SEED2 = 4502
ANCH2 = [(0, 14.0), (6, 15.2), (10, 13.9), (15, 15.8), (20, 14.3), (24, 13.6), (29, 15.4), (34, 16.8), (43, 18.4)]
chart_registry.assert_fresh_synthetic(SEED2, ANCH2, label="run6-backtest")
W2 = gen(ANCH2, 44, SEED2, wick=0.8)
x2, y2, slot2 = geom(W2)
T_IDX = [7, 13, 21, 31]     # مواقع الصفقات الأربع على الجارت
ex2 = []
ex2.append(f'<g id="m1" opacity="0"><circle cx="{x2(7):.1f}" cy="{y2(W2[7]["l"]):.1f}" r="13" fill="none" stroke="{TEAL_D}" stroke-width="2.8"/>{htext(x2(7), y2(W2[7]["l"])+34, "+2R", TEAL_D, 24)}</g>')
ex2.append(f'<g id="m2" opacity="0">{xmark(x2(13), y2(W2[13]["h"]))}{htext(x2(13), y2(W2[13]["h"])-22, "−1R", RED, 24)}</g>'.replace('class="mk"', ''))
ex2.append(f'<g id="m3" opacity="0">{htext(x2(22), y2(max(c["h"] for c in W2[20:25]))-24, "3 خسارات ورا بعض −3R", RED, 23)}'
           f'<rect x="{x2(20)-slot2*0.6:.1f}" y="{y2(max(c["h"] for c in W2[20:25])):.1f}" width="{slot2*4.5:.1f}" height="{y2(min(c["l"] for c in W2[20:25]))-y2(max(c["h"] for c in W2[20:25])):.1f}" fill="{RED}" opacity="0.08"/></g>')
ex2.append(f'<g id="m4" opacity="0"><circle cx="{x2(31):.1f}" cy="{y2(W2[31]["l"]):.1f}" r="13" fill="none" stroke="{TEAL_D}" stroke-width="2.8"/>{htext(x2(31), y2(W2[31]["l"])+34, "+4R", TEAL_D, 24)}</g>')
tb_x, tb_y = x2(28), y2(max(c["h"] for c in W2))
ex2.append(chip(x2(30)-slot2*8, tb_y-6, slot2*17, "إصابة 45% · RR 1:2 · أطول سلسلة 5", TEAL_D, "tbl", fs=20))
ex2.append(f'<g id="reslbl2" opacity="0">{htext(x2(37), y2(W2[43]["h"])-26, "+35R لكل 100 صفقة", TEAL_D, 26)}</g>')

story2 = [(i, round(2.4 + (i-9)*0.5, 2)) for i in range(9, 12)]
story2 += [(i, round(4.9 + (i-12)*0.45, 2)) for i in range(12, 17)]
story2 += [(i, round(7.6 + (i-17)*0.35, 2)) for i in range(17, 27)]
story2 += [(i, round(11.5 + (i-27)*0.4, 2)) for i in range(27, 34)]
story2 += [(i, round(14.6 + (i-34)*0.28, 2)) for i in range(34, 44)]

cfg2 = dict(
  w=W2, base=9, openmax=42, open_t=[[43, 0.35]], story=story2,
  extra_svg="".join(ex2),
  marks=[["m1", 3.0, 3.35, "pop"], ["m2", 5.6, 5.95, "pop"],
         ["m3", 9.0, 9.4, "fade"], ["m4", 12.6, 12.95, "pop"],
         ["tbl", 15.2, 15.55, "pop"], ["reslbl2", 16.1, 16.4, "pop"]],
  fullset=["m1", "m2", "m3", "m4", "tbl", "reslbl2"], drawset=[],
  txt=[("t1", 0.35, 2.2, "نظامك ربحان ولا خسران…<br>عندك دليل؟", 52, INK),
       ("t2", 2.45, 4.6, "أول صفقة ربحت…<br>لا تحكم — سجّلها وكمّل", 48, INK),
       ("t3", 4.9, 7.3, "ثاني وحدة خسرت…<br>لا تعدل القواعد بنص الاختبار", 46, INK),
       ("t4", 7.6, 11.2, "ثلاث خسارات ورا بعض؟<br>كل نظام له سلاسل… سجّل طولها", 46, INK),
       ("t5", 11.5, 14.3, "رابحة كبيرة +4R…<br>رقم بالجدول مو حفلة", 48, INK),
       ("t6", 14.6, 16.6, "بعد 50 صفقة…<br>الأرقام تتكلم مو الذاكرة", 48, INK)],
  chip="درس الباك تست · لغرض تعليمي", res="45% إصابة × RR 1:2 = نظام ربحان",
  cta_k="اكتب «باكتست»", cta_s="وتوصلك خطة الاختبار كاملة PDF على الخاص",
  edu="لغرض تعليمي — مثال تخطيطي",
  dur=21.8, res_t=16.9, cta_t=18.7, flash=(15.2, 15.8), punch=(15.15, 16.3, 0.045),
  punch_origin="60% 30%", rflash=None)
cfg2.pop("rflash")
fxn2 = lambda i: x2(i)/1000; fyn2 = lambda p: y2(p)/820
cfg2["cam"] = [
  [0.0, 1.03, .5, .5], [2.3, 1.05, .5, .5],
  [2.8, 1.8, fxn2(7), fyn2(W2[7]["l"])],
  [5.3, 1.85, fxn2(13), fyn2(W2[13]["h"])],
  [8.6, 1.7, fxn2(22), fyn2(W2[22]["c"])],
  [12.3, 1.85, fxn2(31), fyn2(W2[31]["l"])],
  [15.1, 1.45, fxn2(33), fyn2(W2[33]["h"])],
  [16.9, 1.12, .5, .48], [18.5, 1.02, .5, .5], [21.8, 1.03, .5, .5]]
print("backtest html:", build_reel(cfg2, "reel_backtest.html"))
REG.append((SEED2, ANCH2, "ريل باكتست run6"))

# ================= ريل «لوت» — الحجم يمشي ورا الستوب =================
SEED3 = 4503
ANCH3 = [(0, 10.0), (5, 9.6), (10, 13.4), (14, 11.2), (15, 10.9), (20, 14.8), (25, 12.2), (26, 11.9), (31, 16.0), (39, 18.6)]
chart_registry.assert_fresh_synthetic(SEED3, ANCH3, label="run6-lot")
W3 = gen(ANCH3, 40, SEED3, wick=0.8)
x3, y3, slot3 = geom(W3)
IA, IBB = 15, 26                                 # دخلتان: ستوب قريب / ستوب بعيد
rng3 = max(c["h"] for c in W3) - min(c["l"] for c in W3)
SLA = W3[IA]["l"] - rng3*0.035                   # ستوب 20 نقطة
SLB = W3[IBB]["l"] - rng3*0.13                   # ستوب 100 نقطة
ex3 = []
for id_, I, SLv, lbl in (("ea", IA, SLA, "ستوب 20 نقطة"), ("eb", IBB, SLB, "ستوب 100 نقطة")):
    bxx = x3(I) + slot3*1.7
    ex3.append(f'<g id="{id_}" opacity="0"><circle cx="{x3(I):.1f}" cy="{y3(W3[I]["l"]):.1f}" r="14" fill="none" stroke="{TEAL_D}" stroke-width="3"/>'
               f'<line x1="{x3(I)-slot3*1.4:.1f}" y1="{y3(SLv):.1f}" x2="{bxx+6:.1f}" y2="{y3(SLv):.1f}" stroke="{RED}" stroke-width="1.7" stroke-dasharray="6 5"/>'
               f'<line x1="{bxx:.1f}" y1="{y3(W3[I]["l"]):.1f}" x2="{bxx:.1f}" y2="{y3(SLv):.1f}" stroke="{INK}" stroke-width="1.8"/>'
               + htext(bxx+12, (y3(W3[I]["l"])+y3(SLv))/2+7, lbl, INK, 21, anchor="start") + '</g>')
ex3.append(chip(x3(IA)-slot3*3.8, y3(SLA)+52, slot3*7.6, "اللوت: 0.05 — مخاطرة 1%", TEAL_D, "ca", fs=20))
ex3.append(chip(x3(IBB)-slot3*3.8, y3(SLB)+104, slot3*7.6, "اللوت: 0.01 — مخاطرة 1% ثابتة", TEAL_D, "cb", fs=20))
ex3.append(chip(x3(20)-slot3*5.5, y3(max(c["h"] for c in W3))-4, slot3*11, "0.05 ثابتة × ستوب 100 = −5% ✗", RED, "warn", fs=22, fill="#F8ECEC"))
ex3.append(f'<g id="reslbl3" opacity="0">{htext(x3(34), y3(max(c["h"] for c in W3[34:]))-22, "المخاطرة ثابتة… واللوت يتحرك", TEAL_D, 24)}</g>')

story3 = [(i, round(2.4 + (i-11)*0.4, 2)) for i in range(11, 16)]
story3 += [(i, round(6.0 + (i-16)*0.13, 2)) for i in range(16, 27)]
story3 += [(i, round(13.4 + (i-27)*0.3, 2)) for i in range(27, 40)]

cfg3 = dict(
  w=W3, base=11, openmax=38, open_t=[[39, 0.35]], story=story3,
  extra_svg="".join(ex3),
  marks=[["ea", 3.0, 3.35, "pop"], ["ca", 4.4, 4.75, "pop"],
         ["eb", 7.6, 7.95, "pop"], ["cb", 9.0, 9.35, "pop"],
         ["warn", 11.6, 11.95, "pop"],
         ["reslbl3", 16.0, 16.3, "pop"]],
  fullset=["ea", "ca", "eb", "cb", "warn", "reslbl3"], drawset=[],
  txt=[("t1", 0.35, 2.2, "الستوب يتغير…<br>واللوت عندك ثابت؟", 54, INK),
       ("t2", 2.45, 5.9, "ستوب قريب 20 نقطة →<br>10$ ÷ (20×10$) = 0.05 لوت", 46, INK),
       ("t3", 6.2, 10.9, "ستوب بعيد 100 نقطة →<br>10$ ÷ (100×10$) = 0.01 لوت", 46, INK),
       ("t4", 11.2, 13.1, "نفس اللوت على الكل؟<br>−5% بضربة وحدة", 48, INK),
       ("t5", 13.4, 15.8, "المعادلة قبل الزر…<br>وقرّب النتيجة لتحت دايم", 46, INK)],
  chip="درس حجم العقد · لغرض تعليمي", res="اللوت قرار محسوب… يمشي ورا الستوب",
  cta_k="اكتب «لوت»", cta_s="وياك دليل الحجم صفحة صفحة على الخاص",
  edu="لغرض تعليمي — مثال تخطيطي",
  dur=21.2, res_t=16.5, cta_t=18.3, flash=(11.65, 12.25), punch=(11.6, 12.75, 0.045),
  punch_origin="50% 25%", rflash=None)
cfg3.pop("rflash")
fxn3 = lambda i: x3(i)/1000; fyn3 = lambda p: y3(p)/820
cfg3["cam"] = [
  [0.0, 1.03, .5, .5], [2.3, 1.05, .5, .5],
  [2.8, 1.9, fxn3(IA), fyn3(SLA)],
  [6.4, 1.9, fxn3(IBB), fyn3(SLB)],
  [11.3, 1.55, fxn3(20), fyn3(W3[20]["h"])],
  [13.6, 1.7, fxn3(30), fyn3(W3[30]["c"])],
  [16.5, 1.12, .5, .48], [18.2, 1.02, .5, .5], [21.2, 1.03, .5, .5]]
print("lot html:", build_reel(cfg3, "reel_lot.html"))
REG.append((SEED3, ANCH3, "ريل لوت run6"))

chart_registry.register_synthetic("run6-2026-08-03", REG)
print("registered", len(REG))
