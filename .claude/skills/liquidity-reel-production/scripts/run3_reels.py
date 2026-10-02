# -*- coding: utf-8 -*-
# تشغيلة المصنع 3 — الريلان: «استدراج» (الذهب 15د 2026-05-29) · «نص» (الداو ساعة 2025-10-29)
# النصوص من content/run3_copy.json (ايجنت صانع المحتوى)
import json, os
from reel_build import INK, TEAL, TEAL_D, RED, htext, hend
from reel_sfx_kit import build_reel, geom, line_el, xmark, checkmark

HERE = os.path.dirname(os.path.abspath(__file__))
C = json.load(open(os.path.join(HERE, "sheet_candidates.json")))
CP = json.load(open(os.path.join(HERE, "..", "content", "run3_copy.json")))

def txt7(key, fss=(60, 56, 54, 52, 52, 52, 54)):
    T = [(0.35, 1.9), (2.30, 4.1), (4.30, 6.5), (6.70, 8.8), (9.00, 11.9), (12.10, 13.9), (14.10, 15.6)]
    return [(f"t{i+1}", a, b, CP[key]["reel"]["txt"][i], fss[i], INK) for i, (a, b) in enumerate(T)]

# ================= ريل «استدراج» =================
row = C[13]; W_ = row["w"]; N = len(W_)                    # GC=F 15m — n=32
I1, IS0, IS1, IOB, IR, RB = 13, 16, 18, 9, 24, 30
EQ = W_[I1]["h"]; ZT, ZB = W_[IOB]["o"], W_[IOB]["l"]
x, y, slot = geom(W_)
XP = max(range(IS0, IS1+1), key=lambda j: W_[j]["h"])       # أعلى شمعة بالسحب

ex = []
ex.append(line_el(x(I1)-slot*0.5, y(EQ), x(IS1)+slot*0.55, y(EQ), RED, 2.4, id="baitline"))
ex.append(f'<g id="baitlbl" opacity="0">{htext(x((I1+IS0)/2), y(max(EQ, W_[XP]["h"]))-22, "هني أغروك تدخل", RED, 25)}</g>')
ex.append(xmark(x(XP), y(W_[XP]["h"]), id="xp"))
zx0 = x(IOB)-slot*0.5; zx1 = x(min(IR+3, N-1))+slot*0.5
ex.append(f'<g id="zone" opacity="0"><rect x="{zx0:.1f}" y="{y(ZT):.1f}" width="{zx1-zx0:.1f}" height="{y(ZB)-y(ZT):.1f}" fill="{TEAL}" style="opacity:0.16"/>'
          f'<rect x="{zx0:.1f}" y="{y(ZT):.1f}" width="{zx1-zx0:.1f}" height="{y(ZB)-y(ZT):.1f}" fill="none" stroke="{TEAL_D}" stroke-width="1.6"/>'
          + htext((zx0+zx1)/2, y(ZB)+30, "المنطقة الحقيقية", TEAL_D, 24) + '</g>')
ex.append(f'<g id="circ" opacity="0"><circle cx="{x(IR):.1f}" cy="{y(W_[IR]["l"]):.1f}" r="16" fill="none" stroke="{TEAL_D}" stroke-width="3.2"/>'
          + htext(x(IR)-slot*0.5, y(W_[IR]["l"])+40, "الدخلة الصح — من هني", TEAL_D, 24) + '</g>')
ex.append(checkmark(x(RB)+slot*1.05, y(W_[RB]["c"]), id="ck"))
ex.append(f'<g id="reallbl" opacity="0">{htext(x(RB)-slot*0.6, y(max(c["h"] for c in W_[RB:]))-16, "الحركة الحقيقية", TEAL_D, 25)}</g>')

story = [(13,2.45),(14,2.9),(15,3.3),(16,4.35),(17,4.7),(18,5.05),
         (19,6.9),(20,7.25),(21,7.6),(22,7.95),(23,8.3),(24,9.1),
         (25,10.2),(26,10.55),(27,10.9),(28,11.25),(29,11.6),(30,12.4),(31,13.6)]
cfg = dict(w=W_, base=12, openmax=30, open_t=[[31,0.35]], story=story,
  extra_svg="".join(ex),
  marks=[["baitline",4.35,4.85,"draw"],["baitlbl",4.85,5.15,"pop"],
         ["xp",6.35,6.65,"pop"],
         ["zone",8.95,9.45,"fade"],["circ",9.45,9.75,"pop"],
         ["ck",12.95,13.25,"pop"],["reallbl",13.25,13.55,"pop"]],
  fullset=["baitlbl","xp","zone","circ","ck","reallbl"], drawset=["baitline"],
  txt=txt7("istidraj"), chip="الذهب · 15 دقيقة", res=CP["istidraj"]["reel"]["res"],
  cta_k="اكتب «استدراج»", cta_s=CP["istidraj"]["reel"]["cta_s"],
  dur=19.8, res_t=15.9, cta_t=17.1, flash=(12.45,13.1), punch=(12.4,13.7,0.055),
  punch_origin="82% 30%", rflash=6.4)
fx = lambda i: x(i) / 1000; fy = lambda p: y(p) / 820
cfg["cam"] = [
  [0.0, 1.03, .5, .5], [2.3, 1.05, .5, .5],
  [3.5, 1.75, fx(15), fy(EQ)],                       # زوم قوي على بناء القمم
  [6.3, 2.00, fx(XP), fy(W_[XP]["h"])],              # لصق على X الفخ
  [7.9, 1.75, fx(21), fy((W_[21]["l"]+W_[21]["h"])/2)],   # بان مع النزول
  [9.4, 1.95, fx(IR), fy((ZT+ZB)/2)],                # لصق على الدخلة بالزون
  [11.7, 1.75, fx(27), fy(W_[27]["c"])],
  [12.9, 1.65, fx(RB), fy(W_[RB]["c"])],             # الذروة (فوقها البانش)
  [15.3, 1.15, .5, .52], [16.6, 1.02, .5, .5], [19.8, 1.03, .5, .5]]
print("istidraj html:", build_reel(cfg, "reel_istidraj.html"), "| XP", XP)

# ================= ريل «نص» =================
row = C[4]; W_ = row["w"]; N = len(W_)                     # YM=F 1h — n=42
ILO, IHI, IOB, IR = 2, 26, 18, 39
LO = W_[ILO]["l"]; HI = W_[IHI]["h"]; MID = (LO+HI)/2
ZT, ZB = W_[IOB]["o"], W_[IOB]["l"]
x, y, slot = geom(W_)

ex = []
ex.append(f'<g id="shade" opacity="0">'
          f'<rect x="{x(ILO):.1f}" y="{y(HI):.1f}" width="{x(N-1)-x(ILO):.1f}" height="{y(MID)-y(HI):.1f}" fill="{RED}" opacity="0.06"/>'
          f'<rect x="{x(ILO):.1f}" y="{y(MID):.1f}" width="{x(N-1)-x(ILO):.1f}" height="{y(LO)-y(MID):.1f}" fill="{TEAL}" opacity="0.08"/>'
          + htext(x(8), y((HI+MID)/2), "غالي", RED, 26) + htext(x(8), y((MID+LO)/2), "رخيص", TEAL_D, 26) + '</g>')
ex.append(line_el(x(ILO), y(MID), x(N-1)+slot*0.4, y(MID), INK, 2.2, dash="9 7", id="midline"))
ex.append(f'<g id="midlbl" opacity="0">{hend(x(N-1)+slot*0.4, y(MID), INK)}{htext(x(6), y(MID)-14, "نص المدى", INK, 24)}</g>')
ex.append(line_el(x(IHI)-slot*0.4, y(HI), x(IHI)+slot*2.2, y(HI), INK, 1.8, id="hiline"))
ex.append(line_el(x(ILO)-slot*0.4, y(LO), x(ILO)+slot*2.2, y(LO), INK, 1.8, id="loline"))
zx0 = x(IOB)-slot*0.5; zx1 = x(min(IR+2, N-1))+slot*0.5
ex.append(f'<g id="zone" opacity="0"><rect x="{zx0:.1f}" y="{y(ZT):.1f}" width="{zx1-zx0:.1f}" height="{y(ZB)-y(ZT):.1f}" fill="{TEAL}" style="opacity:0.16"/>'
          f'<rect x="{zx0:.1f}" y="{y(ZT):.1f}" width="{zx1-zx0:.1f}" height="{y(ZB)-y(ZT):.1f}" fill="none" stroke="{TEAL_D}" stroke-width="1.6"/>'
          + htext((zx0+zx1)/2, y(ZB)+30, "زون الطلب", TEAL_D, 24) + '</g>')
ex.append(f'<g id="circ" opacity="0"><circle cx="{x(IR):.1f}" cy="{y(W_[IR]["l"]):.1f}" r="16" fill="none" stroke="{TEAL_D}" stroke-width="3.2"/>'
          + htext(x(IR)-slot*2.0, y(W_[IR]["l"])+42, "الدخول الصح — هني بالرخيص", TEAL_D, 23) + '</g>')
ex.append(checkmark(x(41)+slot*0.9, y(W_[41]["c"]), id="ck"))

story = [(i, round(5.9 + (i-27)*0.3, 2)) for i in range(27, 39)]      # النزول 27..38
story += [(39, 10.1), (40, 12.4), (41, 12.75)]
cfg = dict(w=W_, base=26, openmax=39, open_t=[[40,0.2],[41,0.5]], story=story,
  extra_svg="".join(ex),
  marks=[["hiline",2.5,2.95,"draw"],["loline",2.5,2.95,"draw"],
         ["midline",3.2,3.75,"draw"],["midlbl",3.75,4.0,"pop"],
         ["shade",4.6,5.1,"fade"],
         ["zone",9.7,10.1,"fade"],["circ",10.25,10.55,"pop"],
         ["ck",13.0,13.3,"pop"]],
  fullset=["midlbl","shade","zone","circ","ck"], drawset=["midline","hiline","loline"],
  txt=txt7("nus"), chip="الداو جونز · فريم الساعة", res=CP["nus"]["reel"]["res"],
  cta_k="اكتب «نص»", cta_s=CP["nus"]["reel"]["cta_s"],
  dur=19.8, res_t=15.9, cta_t=17.1, flash=(12.45,13.1), punch=(12.4,13.7,0.055),
  punch_origin="85% 55%", rflash=None)
cfg.pop("rflash")
fx = lambda i: x(i) / 1000; fy = lambda p: y(p) / 820
cfg["cam"] = [
  [0.0, 1.03, .5, .5], [2.3, 1.05, .5, .5],
  [3.6, 1.55, .45, fy(MID)],                          # زوم على خط النص
  [5.4, 1.25, .5, .5],                                # نوسّع مع التظليل
  [7.4, 1.75, fx(31), fy(W_[31]["c"])],               # بان قريب مع نزول الرجعة
  [9.7, 1.95, fx(37), fy((ZT+ZB)/2)],                 # لصق على الزون بالرخيص
  [10.9, 1.95, fx(IR), fy((ZT+ZB)/2)],                # الدخلة
  [12.9, 1.65, fx(40), fy(W_[40]["h"])],              # الارتداد (الذروة)
  [15.3, 1.15, .5, .5], [16.6, 1.02, .5, .5], [19.8, 1.03, .5, .5]]
print("nus html:", build_reel(cfg, "reel_nus.html"))
