# -*- coding: utf-8 -*-
# run9 — إعادة تصميم ريلز اليوم الأربعة وفق MASTER PROMPT V2:
#   فصحى كاملة + افتتاحية داكنة (م1) + Light Sweep للأوف وايت (م2) + مدة معيارية ≥25ث
# نفس الجارتات المسجلة لوحدات اليوم (استبدال لا تكرار) — بلا تسجيل جديد
import os
from reel_build import INK, TEAL, TEAL_D, RED, htext, hend, gen
from reel_sfx_kit import build_reel, geom, line_el, xmark, checkmark, zone_el, ring, pos_box

HERE = os.path.dirname(os.path.abspath(__file__))
SH = 1.3          # إزاحة المحتوى بعد الافتتاحية الداكنة (تنتهي 2.5 + مسحة 0.55)

def shift_cfg(cfg, sh=SH, cta_extra=0.4, tail=5.0):
    """يدفع كل التوقيتات بعد الافتتاحية ويطيل الذيل ليحقق مدة V2 المعيارية."""
    cfg["story"] = [(i, round(t + sh, 2)) for i, t in cfg["story"]]
    cfg["marks"] = [[m[0], round(m[1] + sh, 2), round(m[2] + sh, 2), m[3]] for m in cfg["marks"]]
    cfg["txt"] = [(i, round(a + sh, 2), round(b + sh, 2), t, fs, c) for i, a, b, t, fs, c in cfg["txt"]]
    cfg["flash"] = (round(cfg["flash"][0] + sh, 2), round(cfg["flash"][1] + sh, 2))
    cfg["punch"] = (round(cfg["punch"][0] + sh, 2), round(cfg["punch"][1] + sh, 2), cfg["punch"][2])
    if cfg.get("rflash"):
        cfg["rflash"] = round(cfg["rflash"] + sh, 2)
    cfg["res_t"] = round(cfg["res_t"] + sh + 0.2, 2)
    cfg["cta_t"] = round(cfg["cta_t"] + sh + cta_extra, 2)
    cfg["dur"] = round(cfg["cta_t"] + tail, 2)
    cam = []
    for kf in cfg["cam"]:
        kf = list(kf)
        if kf[0] > 2.31:
            kf[0] = round(kf[0] + sh, 2)
        cam.append(kf)
    cam[-1][0] = cfg["dur"]
    cfg["cam"] = cam
    return cfg

# ================= ريل «فومو» (فصحى) =================
SEED = 4501
ANCH = [(0, 10.0), (6, 9.5), (13, 16.8), (16, 14.9), (19, 12.6), (23, 10.7), (27, 10.05), (31, 14.2), (37, 18.9)]
W_ = gen(ANCH, 38, SEED, wick=0.85)
x, y, slot = geom(W_)
XC = max(range(11, 15), key=lambda j: W_[j]["h"])
IZ0, IZ1 = 5, 7
ZT = max(max(c["o"], c["c"]) for c in W_[IZ0:IZ1+1]); ZB = min(c["l"] for c in W_[IZ0:IZ1+1])
ISTP = 17
IE = 27
RB = 37

ex = []
ex.append(xmark(x(XC), y(W_[XC]["h"]), id="xc"))
ex.append(f'<g id="xclbl" opacity="0">{htext(x(XC)-slot*2.2, y(W_[XC]["h"])-22, "الملاحقة هنا", RED, 24)}</g>')
sl_ch = W_[ISTP]["l"]
ex.append(line_el(x(XC)-slot*0.6, y(sl_ch), x(ISTP)+slot*0.8, y(sl_ch), RED, 1.9, dash="7 5", id="chstop"))
ex.append(f'<g id="chstoplbl" opacity="0">{htext(x(ISTP)+slot*0.5, y(sl_ch)+30, "أصاب وقف الملاحقين", RED, 22)}</g>')
zx0 = x(IZ0)-slot*0.5; zx1 = x(min(IE+3, 37))+slot*0.5
ex.append(zone_el("zone", zx0, y(ZT), zx1, y(ZB), htext((zx0+zx1)/2, (y(ZT)+y(ZB))/2+8, "منطقة الانطلاق", TEAL_D, 23)))
ex.append(ring("circ", x(IE), y(W_[IE]["l"]), 16, TEAL_D, htext(x(IE), y(W_[IE]["l"])+38, "الدخول الصحيح", TEAL_D, 24)))
ex.append(checkmark(x(RB)-slot*0.2, y(W_[RB]["c"])-30, id="ck"))
ex.append(f'<g id="reslbl" opacity="0">{htext(x(33), y(max(c["h"] for c in W_[33:]))-20, "+150 نقطة", TEAL_D, 28)}</g>')

story = [(i, round(2.4 + (i-14)*0.5, 2)) for i in range(14, 19)]
story += [(i, round(7.3 + (i-19)*0.3, 2)) for i in range(19, 27)]
story += [(27, 11.5)] + [(i, round(13.5 + (i-28)*0.28, 2)) for i in range(28, 38)]

cfg = dict(
  w=W_, base=14, openmax=36, open_t=[[37, 0.35]], story=story,
  extra_svg="".join(ex),
  marks=[["xc", 2.6, 3.05, "drawx"], ["xclbl", 3.05, 3.3, "pop"],
         ["chstop", 4.8, 5.3, "draw"], ["chstoplbl", 5.3, 5.55, "pop"],
         ["zone", 7.6, 8.5, "zone"],
         ["circ", 11.6, 12.0, "ring"],
         ["ck", 15.4, 15.7, "pop"], ["reslbl", 15.7, 16.0, "pop"]],
  fullset=["xc", "xclbl", "chstoplbl", "zone", "circ", "ck", "reslbl"], drawset=["chstop"],
  txt=[("t2", 2.45, 4.5, "الإغراء: الدخول في آخرها…<br>أغلى سعر في الحركة", 50, INK),
       ("t3", 4.75, 7.2, "أول تنفّس طبيعي…<br>أصاب وقف الملاحقين", 50, INK),
       ("t4", 7.5, 9.6, "الصواب: حدد منطقة الانطلاق<br>وضع تنبيهاً", 50, INK),
       ("t5", 9.9, 13.2, "الدخول عند الرجعة…<br>لأن السعر يختبر منطقته قبل أن يواصل", 46, INK),
       ("t6", 13.5, 15.3, "وإن لم يعد؟<br>دعها… السوق يفتح غداً", 46, INK)],
  chip="درس الفومو · لغرض تعليمي", res="+150 نقطة لمن صبر… ووقف لمن لاحق",
  cta_k="اكتب «فومو»", cta_s="ليصلك دليل قاعدة الرجعة — 16 صفحة — على الخاص",
  edu="لغرض تعليمي — مثال تخطيطي",
  dur=21.6, res_t=16.3, cta_t=18.4, flash=(13.6, 14.25), punch=(13.55, 14.85, 0.05),
  punch_origin="62% 55%", rflash=6.2,
  intro=dict(eyeb="درس تطبيقي — نفسية التداول",
             hook="فاتتك شمعة الاندفاع؟<br>توقف… لا تلاحقها",
             sub="متى تنتظر الرجعة… ومتى تنساها؟", t=2.5))
fxn = lambda i: x(i)/1000; fyn = lambda p: y(p)/820
cfg["cam"] = [
  [0.0, 1.03, .5, .5], [2.3, 1.05, .5, .5, "creep"],
  [2.8, 1.85, fxn(XC), fyn(W_[XC]["h"]), "anticip"],
  [5.0, 1.9, fxn(ISTP), fyn(sl_ch), "ramp"],
  [7.7, 1.75, fxn((IZ0+IE)/2), fyn((ZT+ZB)/2), "creep"],
  [11.5, 1.95, fxn(IE), fyn(W_[IE]["l"]), "anticip"],
  [13.9, 1.6, fxn(31), fyn(W_[31]["c"]), "whip", -1.2],
  [16.1, 1.15, .5, .48, "creep", 0], [18.1, 1.02, .5, .5, "creep"], [21.6, 1.03, .5, .5, "creep"]]
shift_cfg(cfg)
print("fomo html:", build_reel(cfg, "reel9_fomo.html"), "| dur", cfg["dur"], "| flash", cfg["flash"], "| cta", cfg["cta_t"])

# ================= ريل «باكتست» (فصحى) =================
SEED2 = 4502
ANCH2 = [(0, 14.0), (6, 15.2), (10, 13.9), (15, 15.8), (20, 14.3), (24, 13.6), (29, 15.4), (34, 16.8), (43, 18.4)]
W2 = gen(ANCH2, 44, SEED2, wick=0.8)
x2, y2, slot2 = geom(W2)

def chip_el(x0, y0, w, txt, col, id_, fs=21, fill="#F2EEE7"):
    w2 = max(w, len(txt) * (fs * 0.58))
    x0 -= (w2 - w) / 2
    return (f'<g id="{id_}" opacity="0"><rect x="{x0:.1f}" y="{y0:.1f}" width="{w2:.1f}" height="40" '
            f'fill="{fill}" stroke="{col}" stroke-width="1.3"/>' + htext(x0 + w2/2, y0 + 28, txt, col, fs) + '</g>')

ex2 = []
ex2.append(ring("m1", x2(7), y2(W2[7]["l"]), 13, TEAL_D, htext(x2(7), y2(W2[7]["l"])+34, "+2R", TEAL_D, 24)))
ex2.append(xmark(x2(13), y2(W2[13]["h"]), id="m2"))
ex2.append(f'<g id="m2l" opacity="0">{htext(x2(13), y2(W2[13]["h"])-26, "−1R", RED, 24)}</g>')
ex2.append(f'<g id="m3" opacity="0">{htext(x2(22), y2(max(c["h"] for c in W2[20:25]))-24, "3 خسائر متتالية −3R", RED, 23)}'
           f'<rect x="{x2(20)-slot2*0.6:.1f}" y="{y2(max(c["h"] for c in W2[20:25])):.1f}" width="{slot2*4.5:.1f}" height="{y2(min(c["l"] for c in W2[20:25]))-y2(max(c["h"] for c in W2[20:25])):.1f}" fill="{RED}" opacity="0.08"/></g>')
ex2.append(ring("m4", x2(31), y2(W2[31]["l"]), 13, TEAL_D, htext(x2(31), y2(W2[31]["l"])+34, "+4R", TEAL_D, 24)))
tb_y = y2(max(c["h"] for c in W2))
ex2.append(chip_el(x2(30)-slot2*8, tb_y-6, slot2*17, "إصابة 45% · RR 1:2 · أطول سلسلة 5", TEAL_D, "tbl", fs=20))
ex2.append(f'<g id="reslbl2" opacity="0">{htext(x2(37), y2(W2[43]["h"])-26, "+35R لكل 100 صفقة", TEAL_D, 26)}</g>')

story2 = [(i, round(2.4 + (i-9)*0.5, 2)) for i in range(9, 12)]
story2 += [(i, round(4.9 + (i-12)*0.45, 2)) for i in range(12, 17)]
story2 += [(i, round(7.6 + (i-17)*0.35, 2)) for i in range(17, 27)]
story2 += [(i, round(11.5 + (i-27)*0.4, 2)) for i in range(27, 34)]
story2 += [(i, round(14.6 + (i-34)*0.28, 2)) for i in range(34, 44)]

cfg2 = dict(
  w=W2, base=9, openmax=42, open_t=[[43, 0.35]], story=story2,
  extra_svg="".join(ex2),
  marks=[["m1", 3.0, 3.4, "ring"], ["m2", 5.6, 6.0, "drawx"], ["m2l", 6.0, 6.25, "pop"],
         ["m3", 9.0, 9.4, "fade"], ["m4", 12.6, 13.0, "ring"],
         ["tbl", 15.2, 15.55, "pop"], ["reslbl2", 16.1, 16.4, "pop"]],
  fullset=["m1", "m2", "m2l", "m3", "m4", "tbl", "reslbl2"], drawset=[],
  txt=[("t2", 2.45, 4.6, "أول صفقة ربحت…<br>لا تحكم — سجّلها وواصل", 48, INK),
       ("t3", 4.9, 7.3, "الثانية خسرت…<br>لا تعدّل القواعد في منتصف الاختبار", 46, INK),
       ("t4", 7.6, 11.2, "ثلاث خسائر متتالية؟<br>لكل نظام سلاسله… سجّل طولها", 46, INK),
       ("t5", 11.5, 14.3, "رابحة كبيرة +4R…<br>رقم في الجدول لا احتفال", 48, INK),
       ("t6", 14.6, 16.6, "بعد 50 صفقة…<br>الأرقام تتكلم لا الذاكرة", 48, INK)],
  chip="درس الباك تست · لغرض تعليمي", res="إصابة 45% × RR ‏1:2 = نظام رابح",
  cta_k="اكتب «باكتست»", cta_s="لتصلك خطة الاختبار كاملة PDF على الخاص",
  edu="لغرض تعليمي — مثال تخطيطي",
  dur=21.8, res_t=16.9, cta_t=18.7, flash=(15.2, 15.8), punch=(15.15, 16.3, 0.045),
  punch_origin="60% 30%",
  intro=dict(eyeb="درس تطبيقي — أساسيات التداول",
             hook="نظامك رابح أم خاسر…<br>أين الدليل؟",
             sub="عيّنة من 50 صفقة تتكلم بالأرقام", t=2.5))
fxn2 = lambda i: x2(i)/1000; fyn2 = lambda p: y2(p)/820
cfg2["cam"] = [
  [0.0, 1.03, .5, .5], [2.3, 1.05, .5, .5, "creep"],
  [2.8, 1.8, fxn2(7), fyn2(W2[7]["l"]), "anticip"],
  [5.3, 1.85, fxn2(13), fyn2(W2[13]["h"]), "ramp"],
  [8.6, 1.7, fxn2(22), fyn2(W2[22]["c"]), "creep"],
  [12.3, 1.85, fxn2(31), fyn2(W2[31]["l"]), "anticip"],
  [15.1, 1.45, fxn2(33), fyn2(W2[33]["h"]), "whip", 1.1],
  [16.9, 1.12, .5, .48, "creep", 0], [18.5, 1.02, .5, .5, "creep"], [21.8, 1.03, .5, .5, "creep"]]
shift_cfg(cfg2)
print("backtest html:", build_reel(cfg2, "reel9_backtest.html"), "| dur", cfg2["dur"], "| flash", cfg2["flash"], "| cta", cfg2["cta_t"])

# ================= ريل «لوت» (فصحى) =================
SEED3 = 4503
ANCH3 = [(0, 10.0), (5, 9.6), (10, 13.4), (14, 11.2), (15, 10.9), (20, 14.8), (25, 12.2), (26, 11.9), (31, 16.0), (39, 18.6)]
W3 = gen(ANCH3, 40, SEED3, wick=0.8)
x3, y3, slot3 = geom(W3)
IA, IBB = 15, 26
rng3 = max(c["h"] for c in W3) - min(c["l"] for c in W3)
SLA = W3[IA]["l"] - rng3*0.035
SLB = W3[IBB]["l"] - rng3*0.13
ex3 = []
for id_, I, SLv, lbl in (("ea", IA, SLA, "وقف 20 نقطة"), ("eb", IBB, SLB, "وقف 100 نقطة")):
    bxx = x3(I) + slot3*1.7
    ex3.append(f'<g id="{id_}" opacity="0">'
               f'<circle class="r0" cx="{x3(I):.1f}" cy="{y3(W3[I]["l"]):.1f}" r="14" fill="none" stroke="{TEAL_D}" stroke-width="3"/>'
               f'<circle class="rp" data-r="14" cx="{x3(I):.1f}" cy="{y3(W3[I]["l"]):.1f}" r="14" fill="none" stroke="{TEAL_D}" stroke-width="2" opacity="0"/>'
               f'<line x1="{x3(I)-slot3*1.4:.1f}" y1="{y3(SLv):.1f}" x2="{bxx+6:.1f}" y2="{y3(SLv):.1f}" stroke="{RED}" stroke-width="1.7" stroke-dasharray="6 5"/>'
               f'<line x1="{bxx:.1f}" y1="{y3(W3[I]["l"]):.1f}" x2="{bxx:.1f}" y2="{y3(SLv):.1f}" stroke="{INK}" stroke-width="1.8"/>'
               + htext(bxx+12, (y3(W3[I]["l"])+y3(SLv))/2+7, lbl, INK, 21, anchor="start") + '</g>')
ex3.append(chip_el(x3(IA)-slot3*3.8, y3(SLA)+52, slot3*7.6, "اللوت: 0.05 — مخاطرة 1%", TEAL_D, "ca", fs=20))
ex3.append(chip_el(x3(IBB)-slot3*3.8, y3(SLB)+104, slot3*7.6, "اللوت: 0.01 — مخاطرة 1% ثابتة", TEAL_D, "cb", fs=20))
ex3.append(chip_el(x3(20)-slot3*5.5, y3(max(c["h"] for c in W3))-4, slot3*11, "0.05 ثابتة × وقف 100 = −5% ✗", RED, "warn", fs=22, fill="#F8ECEC"))
ex3.append(f'<g id="reslbl3" opacity="0">{htext(x3(34), y3(max(c["h"] for c in W3[34:]))-22, "المخاطرة ثابتة… والعقد يتحرك", TEAL_D, 24)}</g>')

story3 = [(i, round(2.4 + (i-11)*0.4, 2)) for i in range(11, 16)]
story3 += [(i, round(6.0 + (i-16)*0.13, 2)) for i in range(16, 27)]
story3 += [(i, round(13.4 + (i-27)*0.3, 2)) for i in range(27, 40)]

cfg3 = dict(
  w=W3, base=11, openmax=38, open_t=[[39, 0.35]], story=story3,
  extra_svg="".join(ex3),
  marks=[["ea", 3.0, 3.4, "ring"], ["ca", 4.4, 4.75, "pop"],
         ["eb", 7.6, 8.0, "ring"], ["cb", 9.0, 9.35, "pop"],
         ["warn", 11.6, 11.95, "pop"],
         ["reslbl3", 16.0, 16.3, "pop"]],
  fullset=["ea", "ca", "eb", "cb", "warn", "reslbl3"], drawset=[],
  txt=[("t2", 2.45, 5.9, "وقف قريب 20 نقطة ←<br>‏10$ ÷ (20×10$) = 0.05 لوت", 46, INK),
       ("t3", 6.2, 10.9, "وقف بعيد 100 نقطة ←<br>‏10$ ÷ (100×10$) = 0.01 لوت", 46, INK),
       ("t4", 11.2, 13.1, "العقد نفسه للجميع؟<br>‏−5% بضربة واحدة", 48, INK),
       ("t5", 13.4, 15.8, "المعادلة قبل الزر…<br>وقرّب النتيجة للأسفل دائماً", 46, INK)],
  chip="درس حجم العقد · لغرض تعليمي", res="العقد قرار محسوب… يتبع الوقف",
  cta_k="اكتب «لوت»", cta_s="ليصلك دليل الحجم صفحة صفحة على الخاص",
  edu="لغرض تعليمي — مثال تخطيطي",
  dur=21.2, res_t=16.5, cta_t=18.3, flash=(11.65, 12.25), punch=(11.6, 12.75, 0.045),
  punch_origin="50% 25%",
  intro=dict(eyeb="درس تطبيقي — إدارة المخاطر",
             hook="الوقف يتغير…<br>وعقدك ثابت؟",
             sub="معادلة الحجم (Lot) قبل زر التنفيذ", t=2.5))
fxn3 = lambda i: x3(i)/1000; fyn3 = lambda p: y3(p)/820
cfg3["cam"] = [
  [0.0, 1.03, .5, .5], [2.3, 1.05, .5, .5, "creep"],
  [2.8, 1.9, fxn3(IA), fyn3(SLA), "anticip"],
  [6.4, 1.9, fxn3(IBB), fyn3(SLB), "ramp"],
  [11.3, 1.55, fxn3(20), fyn3(W3[20]["h"]), "whip", -1.1],
  [13.6, 1.7, fxn3(30), fyn3(W3[30]["c"]), "anticip", 0],
  [16.5, 1.12, .5, .48, "creep"], [18.2, 1.02, .5, .5, "creep"], [21.2, 1.03, .5, .5, "creep"]]
shift_cfg(cfg3)
print("lot html:", build_reel(cfg3, "reel9_lot.html"), "| dur", cfg3["dur"], "| flash", cfg3["flash"], "| cta", cfg3["cta_t"])

# ================= ريل «خطة الألف نقطة» (فصحى) =================
N4 = 40
SEED4 = 4400
ANCH4 = [(0, 16.0), (4, 14.6), (8, 13.4), (12, 13.8), (16, 17.6), (21, 14.6),
         (22, 13.9), (26, 17.2), (30, 19.0), (34, 21.4), (39, 24.0)]
W4 = gen(ANCH4, N4, SEED4, wick=0.85)
x4, y4, slot4 = geom(W4)
IPV = max(range(0, 4), key=lambda j: W4[j]["h"])
BOSv = W4[IPV]["h"]
IB = next(i for i in range(8, 20) if W4[i]["c"] > BOSv)
IZ0b, IZ1b = 11, 13
ZTb = max(max(c["o"], c["c"]) for c in W4[IZ0b:IZ1b+1])
ZBb = min(c["l"] for c in W4[IZ0b:IZ1b+1])
IE4 = 22
RNG4 = max(c["h"] for c in W4) - min(c["l"] for c in W4)
SL4 = min(c["l"] for c in W4[19:31]) - RNG4 * 0.03
assert all(c["l"] > SL4 for c in W4[19:31]), "شمعة لامست الوقف!"
ISEC = 26
T1 = W4[IB]["h"] + (BOSv - ZBb) * 0.9
RB4 = 39
T2 = W4[36]["h"]

ex4 = []
ex4.append(line_el(x4(IPV)-slot4*0.4, y4(BOSv), x4(IB)+slot4*0.75, y4(BOSv), INK, 2.0, id="bos"))
ex4.append(f'<g id="boslbl" opacity="0">{htext(x4((IPV+IB)/2), y4(BOSv)-18, "الهيكل انقلب صاعداً", INK, 24)}</g>')
zx0b = x4(IZ0b)-slot4*0.5; zx1b = x4(min(IE4+3, N4-1))+slot4*0.5
ex4.append(zone_el("zone", zx0b, y4(ZTb), zx1b, y4(ZBb), htext((zx0b+zx1b)/2, (y4(ZTb)+y4(ZBb))/2+8, "منطقة الاهتمام", TEAL_D, 23)))
ex4.append(pos_box("pbox", x4(IE4)-slot4*0.9, x4(30)+slot4*0.5, y4(W4[IE4]["l"]), y4(SL4), y4(T1),
                   lbl_e="الدخول", lbl_s="الوقف", lbl_t="الهدف 1"))
ex4.append(line_el(x4(IE4)-slot4*0.5, y4(T2), x4(38)+slot4*0.6, y4(T2), TEAL_D, 1.8, dash="2 6", id="t2"))
ex4.append(f'<g id="t2lbl" opacity="0">{htext(x4(32), y4(T2)+30, "الهدف 2 — الفريم الكبير", TEAL_D, 22)}</g>')
fx0 = x4(IE4)-slot4*2.6; fy0 = y4(SL4)+44
ex4.append(f'<g id="fp" opacity="0"><rect x="{fx0:.1f}" y="{fy0:.1f}" width="{slot4*5.2:.1f}" height="40" fill="#F2EEE7" stroke="{TEAL_D}" stroke-width="1.3"/>'
           + htext(fx0+slot4*2.6, fy0+28, "الفوت برنت: امتصاص بيع ✓", TEAL_D, 21) + '</g>')
ex4.append(ring("circ", x4(IE4), y4(W4[IE4]["l"]), 16, TEAL_D, htext(x4(IE4)+slot4*3.2, y4(W4[IE4]["l"])+34, "الدخول", TEAL_D, 24)))
ex4.append(f'<g id="sec" opacity="0">{line_el(x4(ISEC)-slot4*1.6, y4(W4[IE4]["l"]), x4(ISEC)+slot4*1.6, y4(W4[IE4]["l"]), INK, 2.0)}'
           + htext(x4(ISEC), y4(W4[IE4]["l"])+30, "انقل الوقف هنا — صفر مخاطرة", INK, 22) + '</g>')
ex4.append(checkmark(x4(RB4)-slot4*0.2, y4(W4[RB4]["c"])-34, id="ck"))
ex4.append(f'<g id="reslbl" opacity="0">{htext(x4(35), y4(max(c["h"] for c in W4[36:]))-20, "+1000 نقطة", TEAL_D, 30)}</g>')

story4 = [(i, round(2.5 + (i-13)*0.45, 2)) for i in range(13, 17)]
story4 += [(i, round(5.0 + (i-17)*0.35, 2)) for i in range(17, 22)]
story4 += [(22, 11.9)]
story4 += [(i, round(13.6 + (i-23)*0.45, 2)) for i in range(23, 28)]
story4 += [(i, round(16.0 + (i-28)*0.16, 2)) for i in range(28, 40)]

cfg4 = dict(
  w=W4, base=12, openmax=38, open_t=[[39, 0.35]], story=story4,
  extra_svg="".join(ex4),
  marks=[["bos", 2.7, 3.3, "draw"], ["boslbl", 3.3, 3.6, "pop"],
         ["zone", 5.0, 5.9, "zone"],
         ["pbox", 7.3, 8.75, "posbox"],
         ["t2", 16.1, 16.6, "draw"], ["t2lbl", 16.6, 16.85, "pop"],
         ["fp", 9.6, 9.95, "pop"],
         ["circ", 12.0, 12.4, "ring"],
         ["sec", 13.8, 14.15, "pop"],
         ["ck", 17.35, 17.65, "pop"], ["reslbl", 17.65, 17.95, "pop"]],
  fullset=["boslbl", "zone", "pbox", "t2lbl", "fp", "circ", "sec", "ck", "reslbl"],
  drawset=["bos", "t2"],
  txt=[("t2", 2.45, 4.6, "1 — افتح الجارت…<br>وحدد هيكل السوق", 52, INK),
       ("t3", 4.85, 6.9, "2 — حدد مناطق الاهتمام", 52, INK),
       ("t4", 7.15, 9.2, "3 — حدد الوقف والأهداف<br>قبل أي شيء", 50, INK),
       ("t5", 9.45, 11.6, "4 — تابع الفوت برنت<br>بنماذجك الخاصة", 50, INK),
       ("t6", 11.85, 13.3, "5 — ادخل الصفقة", 54, INK),
       ("t7", 13.55, 15.7, "6 — انقل الوقف إلى دخولك…<br>فلا خسارة بعدها", 48, INK),
       ("t8", 15.95, 17.9, "7 — دعها تمضي نحو أهدافك<br>على الفريمات الكبيرة", 48, INK)],
  chip="خطتي الأسبوعية · لغرض تعليمي",
  res="مبارك… 1000 نقطة في الأسبوع",
  cta_k="اكتب «1000»", cta_s="ليصلك دليل الخطوات الثماني كاملاً على الخاص",
  edu="لغرض تعليمي — مثال تخطيطي",
  dur=22.2, res_t=18.25, cta_t=19.7, flash=(13.35, 14.0), punch=(13.3, 14.6, 0.05),
  punch_origin="55% 45%", rflash=6.0,
  intro=dict(eyeb="الخطة الأسبوعية — ثماني خطوات",
             hook="دعني أعلّمك أن تربح<br>أكثر من 1000 نقطة أسبوعياً",
             sub="خطة واحدة… على جارت واحد حي", t=2.5))
fxn4 = lambda i: x4(i) / 1000
fyn4 = lambda p: y4(p) / 820
cfg4["cam"] = [
  [0.0, 1.03, .5, .5], [2.3, 1.05, .5, .5, "creep"],
  [2.9, 1.7, fxn4(IB), fyn4(BOSv), "anticip"],
  [5.2, 1.85, fxn4((IZ0b+IE4)/2), fyn4((ZTb+ZBb)/2), "ramp"],
  [7.5, 1.5, fxn4(IE4), fyn4(SL4), "creep"],
  [9.7, 1.9, fxn4(IE4), fyn4(ZBb), "anticip"],
  [11.9, 1.95, fxn4(IE4), fyn4(W4[IE4]["l"]), "ramp"],
  [13.7, 1.95, fxn4(IE4), fyn4(W4[IE4]["l"])],
  [14.3, 1.65, fxn4(ISEC), fyn4(W4[IE4]["l"]), "whip", -1.2],
  [16.2, 1.3, fxn4(32), fyn4(W4[32]["c"]), "creep", 0],
  [17.9, 1.12, .5, .48, "creep"], [19.4, 1.02, .5, .5, "creep"], [22.2, 1.03, .5, .5, "creep"]]
shift_cfg(cfg4)
print("alf html:", build_reel(cfg4, "reel9_alf.html"), "| dur", cfg4["dur"], "| flash", cfg4["flash"], "| cta", cfg4["cta_t"])
