# -*- coding: utf-8 -*-
# تشغيلة المصنع 2 — الريلان الفنيان (مؤثرات فقط):
#   1) «كسر» — الكسر الحقيقي vs الوهمي (الذهب 30 دقيقة 2026-07-02)
#   2) «سيولة» — أنواع تجمعات السيولة (الناسداك 30 دقيقة 2026-06-18)
import json, os
from reel_build import INK, TEAL, TEAL_D, RED, htext, hend
from reel_sfx_kit import build_reel, geom, line_el, xmark, checkmark

HERE = os.path.dirname(os.path.abspath(__file__))
C = json.load(open(os.path.join(HERE, "sheet_candidates.json")))

# ================= ريل «كسر» =================
row = C[10]; W_ = row["w"]; N = len(W_)                    # GC=F 30m — n=27
I1, POKE, IOB, IR, RB = 10, 15, 8, 20, 23
EQ = W_[I1]["h"]; ZT, ZB = W_[IOB]["o"], W_[IOB]["l"]
x, y, slot = geom(W_)
PIPS = int(round((max(c["h"] for c in W_[RB:]) - EQ) / 0.1))

ex = []
ex.append(line_el(x(I1), y(EQ), x(RB)+slot*0.55, y(EQ), INK, 2.4, id="lvlline"))
ex.append(f'<g id="lvllbl" opacity="0">{hend(x(RB)+slot*0.55, y(EQ), INK)}{htext(x(I1)+slot*1.8, y(EQ)-14, "المستوى", INK, 24)}</g>')
ex.append(xmark(x(POKE), y(W_[POKE]["h"]), id="xpoke"))
ex.append(f'<g id="fklbl" opacity="0">{htext(x(POKE)-slot*0.4, y(W_[POKE]["h"])-38, "وهمي — فتيل", RED, 26)}</g>')
zx0 = x(IOB)-slot*0.5; zx1 = x(RB)+slot*0.5
ex.append(f'<g id="zone" opacity="0"><rect x="{zx0:.1f}" y="{y(ZT):.1f}" width="{zx1-zx0:.1f}" height="{y(ZB)-y(ZT):.1f}" fill="{TEAL}" style="opacity:0.16"/>'
          f'<rect x="{zx0:.1f}" y="{y(ZT):.1f}" width="{zx1-zx0:.1f}" height="{y(ZB)-y(ZT):.1f}" fill="none" stroke="{TEAL_D}" stroke-width="1.6"/>'
          + htext((zx0+zx1)/2, y(ZB)+30, "زون الطلب", TEAL_D, 24) + '</g>')
ex.append(f'<g id="circ" opacity="0"><circle cx="{x(IR):.1f}" cy="{y(W_[IR]["l"]):.1f}" r="16" fill="none" stroke="{RED}" stroke-width="3.2"/></g>')
ex.append(checkmark(x(RB)+slot*1.05, y(W_[RB]["c"]), id="ck"))
ex.append(f'<g id="reallbl" opacity="0">{htext(x(RB)-slot*0.2, y(max(c["h"] for c in W_[RB:]))-16, "حقيقي — جسم", TEAL_D, 26)}</g>')

story = [(11,2.45),(12,2.8),(13,3.15),(14,3.5),(15,4.35),(16,6.7),(17,7.05),(18,7.4),(19,7.75),
         (20,8.5),(21,9.6),(22,10.0),(23,11.9),(24,13.6),(25,13.95),(26,14.3)]
TXT = [
 ("t1", 0.35, 1.9,  "شلون تفرق الكسر<br>الصدق من الكذب؟", 60, INK),
 ("t2", 2.30, 4.2,  "نفس المستوى… كسرين", 58, INK),
 ("t3", 4.40, 6.4,  "الأول: فتيل اخترق ورجع", 56, INK),
 ("t4", 6.60, 8.3,  "اللي دخل معاه… انطق ستوبه", 52, INK),
 ("t5", 8.50, 11.3, "السعر نزل ياخذ سيولة تحت", 52, INK),
 ("t6", 11.50, 13.4, "الثاني: جسم سكّر فوق المستوى", 52, INK),
 ("t7", 13.70, 15.6, "الفتيل يكذب… الجسم يصدق", 56, INK),
]
cfg = dict(w=W_, base=I1, openmax=RB, open_t=[[24,0.15],[25,0.45],[26,0.75]], story=story,
  extra_svg="".join(ex),
  marks=[["lvlline",2.5,3.0,"draw"],["lvllbl",2.95,3.2,"pop"],
         ["xpoke",4.85,5.15,"pop"],["fklbl",5.15,5.45,"pop"],
         ["zone",8.4,8.9,"fade"],["circ",8.9,9.2,"pop"],
         ["ck",12.45,12.75,"pop"],["reallbl",12.75,13.05,"pop"]],
  fullset=["lvllbl","xpoke","fklbl","zone","circ","ck","reallbl"], drawset=["lvlline"],
  txt=TXT, chip="الذهب · 30 دقيقة", res=f"‎+{PIPS} نقطة بعد الكسر الحقيقي",
  cta_k="اكتب «كسر»", cta_s="يوصلك دليل الكسر الحقيقي كامل",
  dur=19.8, res_t=15.9, cta_t=17.1, flash=(11.95,12.6), punch=(11.9,13.2,0.055),
  punch_origin="80% 42%", rflash=4.95)
print("kasr html bytes:", build_reel(cfg, "reel_kasr.html"), "| PIPS", PIPS, "| poke", POKE, "realbrk", RB)

# ================= ريل «سيولة» =================
row = C[11]; W_ = row["w"]; N = len(W_)                    # NQ=F 30m — n=31
I1, I2, IPDL, IOB, IR, RB = 19, 22, 20, 14, 26, 28
EQ = W_[I1]["h"]; PDL = W_[IPDL]["l"]; ZT, ZB = W_[IOB]["o"], W_[IOB]["l"]
x, y, slot = geom(W_)
SWP = next(j for j in range(I2+1, N) if W_[j]["l"] < PDL)   # شمعة سحب سيولة القاع
PTS = int(round(max(c["h"] for c in W_[RB:]) - W_[IR]["l"]))

ex = []
ex.append(line_el(x(I1)-slot*0.6, y(EQ), x(RB)+slot*0.55, y(EQ), RED, 2.4, id="eqline"))
ex.append(f'<g id="eqlbl" opacity="0">{htext(x((I1+I2)/2), y(max(EQ, W_[I2]["h"]))-20, "سيولة القمم", RED, 26)}</g>')
ex.append(line_el(x(IPDL)-slot*1.2, y(PDL), x(SWP)+slot*0.6, y(PDL), INK, 2.0, dash="7 6", id="pdlline"))
ex.append(f'<g id="pdllbl" opacity="0">{htext(x(IPDL)+slot*0.4, y(PDL)+30, "سيولة القاع (PDL)", INK, 23)}</g>')
zx0 = x(IOB)-slot*0.5; zx1 = x(min(IR+3, N-1))+slot*0.5
ex.append(f'<g id="zone" opacity="0"><rect x="{zx0:.1f}" y="{y(ZT):.1f}" width="{zx1-zx0:.1f}" height="{y(ZB)-y(ZT):.1f}" fill="{TEAL}" style="opacity:0.16"/>'
          f'<rect x="{zx0:.1f}" y="{y(ZT):.1f}" width="{zx1-zx0:.1f}" height="{y(ZB)-y(ZT):.1f}" fill="none" stroke="{TEAL_D}" stroke-width="1.6"/>'
          + htext((zx0+zx1)/2, y(ZB)+30, "زون الطلب", TEAL_D, 24) + '</g>')
ex.append(f'<g id="circ" opacity="0"><circle cx="{x(IR):.1f}" cy="{y(W_[IR]["l"]):.1f}" r="16" fill="none" stroke="{RED}" stroke-width="3.2"/></g>')
ex.append(checkmark(x(RB)+slot*1.05, y(W_[RB]["c"]), id="ck"))
ex.append(f'<g id="cklbl" opacity="0">{htext(x(RB)-slot*0.3, y(max(c["h"] for c in W_[RB:]))-16, "خذ اللي فوق", TEAL_D, 26)}</g>')

story = [(19,2.45),(20,3.3),(21,3.65),(22,4.1),(23,6.6),(24,6.95),(25,7.3),
         (26,8.3),(27,10.4),(28,11.9),(29,13.7),(30,14.05)]
TXT = [
 ("t1", 0.35, 1.9,  "تعرف وين السوق<br>ياخذ الستوبات؟", 60, INK),
 ("t2", 2.30, 4.3,  "الستوبات تتجمع… والسوق يشوفها", 52, INK),
 ("t3", 4.50, 6.3,  "قمم متساوية = سيولة فوق", 54, INK),
 ("t4", 6.50, 8.1,  "وقاع قريب = سيولة تحت", 54, INK),
 ("t5", 8.30, 11.3, "نزل… خذ اللي تحت وارتد", 52, INK),
 ("t6", 11.50, 13.4, "وطلع ياخذ اللي فوق", 56, INK),
 ("t7", 13.70, 15.6, "السعر يمشي من سيولة… لسيولة", 50, INK),
]
cfg = dict(w=W_, base=18, openmax=27, open_t=[[28,0.15],[29,0.45],[30,0.75]], story=story,
  extra_svg="".join(ex),
  marks=[["eqline",4.6,5.2,"draw"],["eqlbl",5.2,5.5,"pop"],
         ["pdlline",5.7,6.1,"draw"],["pdllbl",6.1,6.35,"pop"],
         ["zone",8.2,8.7,"fade"],["circ",8.8,9.1,"pop"],
         ["ck",12.45,12.75,"pop"],["cklbl",12.75,13.05,"pop"]],
  fullset=["eqlbl","pdllbl","zone","circ","ck","cklbl"], drawset=["eqline","pdlline"],
  txt=TXT, chip="الناسداك · 30 دقيقة", res=f"‎+{PTS} نقطة من الزون",
  cta_k="اكتب «سيولة»", cta_s="يوصلك دليل تجمعات السيولة كامل",
  dur=19.8, res_t=15.9, cta_t=17.1, flash=(11.95,12.6), punch=(11.9,13.2,0.055),
  punch_origin="80% 30%", rflash=7.6)
print("suyula html bytes:", build_reel(cfg, "reel_suyula.html"), "| PTS", PTS, "| pdl sweep", SWP)
