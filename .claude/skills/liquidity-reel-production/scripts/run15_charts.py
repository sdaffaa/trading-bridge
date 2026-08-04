# -*- coding: utf-8 -*-
"""جارتات تشغيلة 15 — خمس وحدات: تشوك · محروق · آسيا · سبريد · غرور.
كل دالة تُرجع SVG جاهزاً. البذور تُسجَّل مرة واحدة من run15_build.py.
اصطلاح: كل وحدة تبني بياناتها مرة، ثم خمسة سيناريوهات متمايزة (صفقة لكل صفحة).
"""
from reel_build import INK, TEAL, TEAL_D, RED, GREY, MUTE, htext, gen, chart
import chart_registry

CHARTS = []
CARD = "#FBF9F5"
BD = "#D8D2C8"

def fresh(seed, anch, label):
    chart_registry.assert_fresh_synthetic(seed, anch, label=label)
    CHARTS.append((seed, anch, label))

# ─────────────────────────── أوليات مشتركة ───────────────────────────
def zbox(x0, y0, x1, y1, label="", col=TEAL, stroke=TEAL_D, fs=17, lx=None, ly=None,
         dash=None, op=0.11):
    d = f' stroke-dasharray="{dash}"' if dash else ''
    s = (f'<rect x="{x0:.1f}" y="{min(y0,y1):.1f}" width="{x1-x0:.1f}" height="{abs(y1-y0):.1f}" '
         f'fill="{col}" opacity="{op}"/>'
         f'<rect x="{x0:.1f}" y="{min(y0,y1):.1f}" width="{x1-x0:.1f}" height="{abs(y1-y0):.1f}" '
         f'fill="none" stroke="{stroke}" stroke-width="1.2"{d}/>')
    if label:
        s += htext(lx if lx is not None else (x0 + x1) / 2,
                   ly if ly is not None else (y0 + y1) / 2 + 6, label, stroke, fs)
    return s

def xm(cx, cy, r=11, col=RED):
    return (f'<g stroke="{col}" stroke-width="3" stroke-linecap="round">'
            f'<line x1="{cx-r:.1f}" y1="{cy-r:.1f}" x2="{cx+r:.1f}" y2="{cy+r:.1f}"/>'
            f'<line x1="{cx-r:.1f}" y1="{cy+r:.1f}" x2="{cx+r:.1f}" y2="{cy-r:.1f}"/></g>')

def tick(cx, cy, col=TEAL_D):
    return (f'<polyline points="{cx-10:.1f},{cy:.1f} {cx-3:.1f},{cy+8:.1f} {cx+12:.1f},{cy-10:.1f}" '
            f'fill="none" stroke="{col}" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round"/>')

def hl(x0, x1, yy, col=INK, w=1.8, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<line x1="{x0:.1f}" y1="{yy:.1f}" x2="{x1:.1f}" y2="{yy:.1f}" stroke="{col}" stroke-width="{w}"{d}/>'

def badge(Wd, txt, ok):
    """شارة الحكم أعلى يمين الإطار — عرضها يتبع طول النص."""
    col = TEAL_D if ok else RED
    bw = min(Wd - 40, 36 + int(len(txt) * 11.5))
    return (f'<rect x="14" y="14" width="{bw}" height="38" '
            f'fill="{"#EAF3F5" if ok else "#F8ECEC"}" stroke="{col}" stroke-width="1.4"/>'
            + htext(14 + bw / 2, 40, txt, col, 19))

def frame(W, Wd, H, pad=0.06, pl=14, pr=18, pt=58, pb=50):
    """شريط علوي (عنوان + شارة) وشريط سفلي (ملاحظات) خارج مساحة الشموع دائماً."""
    ymin = min(c["l"] for c in W); ymax = max(c["h"] for c in W); rng = ymax - ymin
    return chart(W, Wd, H, ymin - rng * pad, ymax + rng * pad,
                 grid=4, pl=pl, pr=pr, pt=pt, pb=pb, body=0.6)

def head(Wd, txt, col=INK, fs=19):
    """عنوان الجارت في الطرف المقابل للشارة (الشارة يسار، العنوان يمين)."""
    # في RTL يكون "start" هو الطرف الأيمن — anchor="end" يدفع النص خارج اللوحة
    return htext(Wd - 20, 37, txt, col, fs, anchor="start")

def note(cx, txt, col=INK, H=250, fs=18):
    """ملاحظة في الشريط السفلي — لا تصطدم بأي شمعة."""
    return htext(cx, H - 16, txt, col, fs)

def cap(W, j, top):
    """يقصّ الشمعة j بحيث لا تتجاوز المستوى top."""
    W[j]["h"] = min(W[j]["h"], top)
    W[j]["o"] = min(W[j]["o"], top); W[j]["c"] = min(W[j]["c"], top)
    W[j]["l"] = min(W[j]["l"], W[j]["h"])

def floorc(W, j, bot):
    W[j]["l"] = max(W[j]["l"], bot)
    W[j]["o"] = max(W[j]["o"], bot); W[j]["c"] = max(W[j]["c"], bot)
    W[j]["h"] = max(W[j]["h"], W[j]["l"])


# ══════════════════ 1) تشوك — تغيّر الطابع (CHoCH) ══════════════════
# هبوط بقمم وقيعان هابطة، ثم إغلاق فوق آخر قمة هابطة = تغيّر الطابع.
def _choch(seed, anch, N, iLH, iBRK, label, wick=0.8):
    fresh(seed, anch, label)
    W = gen(anch, N, seed, wick=wick)
    rng = max(c["h"] for c in W) - min(c["l"] for c in W)
    LH = W[iLH]["h"]                                  # آخر قمة هابطة
    for j in range(iLH + 1, iBRK):                    # لا شيء يتجاوزها قبل الكسر
        cap(W, j, LH - rng * 0.02)
    return W, LH, rng

def choch_full(Wd=880, H=250, seed=8101):
    """التسلسل الكامل: تغيّر طابع بإغلاق ← عودة إلى منطقة النشأة ← دخول ← هدف."""
    N = 30
    anch = [(0, 17.4), (4, 15.6), (7, 16.4), (11, 13.8), (14, 14.7), (17, 12.9),
            (20, 16.9), (24, 15.2), (29, 19.6)]
    W, LH, rng = _choch(seed, anch, N, 14, 20, f"تشوك كامل {seed}")
    for j in range(20, 23):                           # الاندفاع يغلق فوق القمة
        floorc(W, j, LH + rng * 0.03)
    ZT, ZB = LH, LH - rng * 0.075                     # منطقة النشأة = القمة المكسورة
    for j in range(23, 26):                           # العودة تلمس المنطقة ثم ترتد
        W[j]["l"] = min(W[j]["l"], ZB + rng * 0.012)
        floorc(W, j, ZB)
    svg, x, y, slot = frame(W, Wd, H)
    svg += hl(x(14) - slot * .6, x(N - 1) + slot * .5, y(LH), INK, 1.9)
    svg += zbox(x(23) - slot * .6, y(ZT), x(N - 1) + slot * .5, y(ZB))
    svg += tick(x(21), y(W[21]["h"]) - 18)
    svg += head(Wd, "إغلاق فوق آخر قمة هابطة = تغيّر الطابع")
    svg += note(x(9), "القمة المكسورة", INK, H, 17)
    svg += note(x(25), "العودة إليها ← الدخول ← الهدف", TEAL_D, H, 17)
    return svg + badge(Wd, "دخول من العودة", True) + "</svg>"

def choch_wick(Wd=880, H=250, seed=8102):
    """فتيل يتجاوز القمة والإغلاق تحتها — ليس تغيّر طابع، والهبوط يستأنف."""
    N = 30
    anch = [(0, 17.8), (4, 16.0), (8, 16.8), (12, 14.2), (15, 15.1), (18, 13.2),
            (21, 15.4), (25, 13.0), (29, 11.4)]
    W, LH, rng = _choch(seed, anch, N, 15, 21, f"تشوك فتيل {seed}")
    W[21].update(h=LH + rng * 0.055, o=LH - rng * 0.03, c=LH - rng * 0.05,
                 l=LH - rng * 0.075)                  # الفتيل يعبر والإغلاق تحت
    for j in range(22, N):
        cap(W, j, LH - rng * 0.03)
    svg, x, y, slot = frame(W, Wd, H)
    svg += hl(x(15) - slot * .6, x(N - 1) + slot * .5, y(LH), INK, 1.9)
    svg += xm(x(21), y(W[21]["h"]) - 6)
    svg += head(Wd, "الفتيل عبر القمة… والإغلاق تحتها")
    svg += note(x(9), "القمة الهابطة", INK, H, 17)
    svg += note(x(25), "الهبوط يستأنف بلا تغيّر", RED, H, 17)
    return svg + badge(Wd, "لا يوجد تغيّر طابع", False) + "</svg>"

def choch_inner(Wd=880, H=250, seed=8103):
    """كسر قمة داخلية لا القمة التي صنعت القاع — إشارة ضعيفة تُستنزف."""
    N = 30
    anch = [(0, 18.2), (3, 16.4), (6, 17.2), (10, 14.6), (13, 15.4), (16, 15.0),
            (19, 15.9), (23, 14.4), (29, 12.2)]
    fresh(seed, anch, f"تشوك داخلي {seed}")
    W = gen(anch, N, seed, wick=0.8)
    rng = max(c["h"] for c in W) - min(c["l"] for c in W)
    MAIN = W[6]["h"]                                   # القمة التي صنعت القاع
    INNER = W[13]["h"]                                 # قمة داخلية أدنى منها
    for j in range(7, N):
        cap(W, j, MAIN - rng * 0.03)
    for j in range(19, 21):
        floorc(W, j, INNER + rng * 0.02)
    svg, x, y, slot = frame(W, Wd, H)
    svg += hl(x(6) - slot * .6, x(N - 1) + slot * .5, y(MAIN), INK, 2.0)
    svg += hl(x(13) - slot * .6, x(24) + slot * .5, y(INNER), MUTE, 1.6, dash="6 5")
    svg += xm(x(20), y(W[20]["h"]) - 8)
    svg += head(Wd, "الخط المتصل: القمة الحاكمة · المتقطع: قمة داخلية")
    svg += note(x(8), "لم تُكسر الحاكمة", INK, H, 17)
    svg += note(x(24), "كسر الداخلية لا يعني شيئاً", RED, H, 17)
    return svg + badge(Wd, "إشارة ضعيفة", False) + "</svg>"

def choch_align(Wd=880, H=250, seed=8104):
    """تغيّر طابع صاعد داخل هيكل أعلى صاعد — الإعداد الأقوى."""
    N = 30
    anch = [(0, 12.4), (5, 16.8), (9, 14.6), (12, 15.5), (15, 13.9), (18, 17.6),
            (22, 16.2), (29, 21.4)]
    W, LH, rng = _choch(seed, anch, N, 12, 18, f"تشوك موافق {seed}")
    for j in range(18, 21):
        floorc(W, j, LH + rng * 0.03)
    ZT, ZB = LH, LH - rng * 0.07
    for j in range(21, 24):
        W[j]["l"] = min(W[j]["l"], ZB + rng * 0.01); floorc(W, j, ZB)
    svg, x, y, slot = frame(W, Wd, H)
    svg += hl(x(12) - slot * .6, x(N - 1) + slot * .5, y(LH), INK, 1.8)
    svg += zbox(x(21) - slot * .6, y(ZT), x(N - 1) + slot * .5, y(ZB))
    svg += tick(x(19), y(W[19]["h"]) - 18)
    svg += head(Wd, "تغيّر طابع صاعد داخل هيكل أعلى صاعد")
    svg += note(x(7), "الاتجاه الأكبر صاعد", TEAL_D, H, 17)
    svg += note(x(24), "العودة ← استكمال الاتجاه", TEAL_D, H, 17)
    return svg + badge(Wd, "الإعداد الأقوى", True) + "</svg>"

def choch_chase(Wd=880, H=250, seed=8105):
    """تغيّر طابع صحيح، لكن الدخول مطاردةً بلا عودة — التنفّس يضرب الوقف."""
    N = 30
    anch = [(0, 17.0), (4, 15.2), (8, 16.1), (12, 13.6), (15, 14.5), (18, 12.8),
            (21, 16.6), (25, 14.1), (29, 18.8)]
    W, LH, rng = _choch(seed, anch, N, 15, 21, f"تشوك مطاردة {seed}")
    for j in range(21, 24):
        floorc(W, j, LH + rng * 0.03)
    ENT = W[22]["c"]
    STP = LH - rng * 0.015
    for j in range(24, 27):                            # التنفّس ينزل تحت الوقف
        cap(W, j, ENT - rng * 0.02)
    W[26]["l"] = min(W[26]["l"], STP - rng * 0.025)
    svg, x, y, slot = frame(W, Wd, H)
    svg += hl(x(15) - slot * .6, x(N - 1) + slot * .5, y(LH), MUTE, 1.6, dash="6 5")
    svg += hl(x(22) - slot * .6, x(N - 1) + slot * .5, y(ENT), INK, 1.9)
    svg += hl(x(22) - slot * .6, x(N - 1) + slot * .5, y(STP), RED, 1.6, dash="7 5")
    svg += xm(x(26), y(W[26]["l"]) + 8)
    svg += head(Wd, "الخط المتصل: الدخول · الأحمر: الوقف")
    svg += note(x(9), "دخول مطاردةً بلا عودة", INK, H, 17)
    svg += note(x(25), "التنفّس أخرجك ثم واصل", RED, H, 17)
    return svg + badge(Wd, "دخول بلا عودة", False) + "</svg>"


# ══════════════════ 2) محروق — المنطقة التي استُهلكت ══════════════════
def _zone_series(seed, anch, N, ZI, touches, label, wick=0.8, thick=0.075, last=None):
    """منطقة رفيعة عند ZI: السعر يبقى فوقها بوضوح، ولا ينزل إليها إلا في اللمسات.
    touches: [(j, depth)] حيث depth ‏0=يلمس السقف و‏1=يصل القاع. last=مؤشر بداية العبور النهائي."""
    fresh(seed, anch, label)
    W = gen(anch, N, seed, wick=wick)
    rng = max(c["h"] for c in W) - min(c["l"] for c in W)
    seg = W[max(0, ZI - 1):ZI + 2]
    ZT = max(max(c["o"], c["c"]) for c in seg)
    ZB = ZT - rng * thick
    tj = {j for j, _ in touches}
    end = last if last is not None else N
    for j in range(ZI + 2, end):                       # بين اللمسات: السعر فوق المنطقة
        if j not in tj:
            floorc(W, j, ZT + rng * 0.025)
    for j, depth in touches:                           # اللمسة تنزل داخل المنطقة فقط
        lo = ZT - (ZT - ZB) * depth
        W[j]["l"] = lo
        W[j]["o"] = max(min(W[j]["o"], ZT + rng * 0.01), lo)
        W[j]["c"] = max(min(W[j]["c"], ZT + rng * 0.02), lo)
        W[j]["h"] = max(W[j]["o"], W[j]["c"]) + rng * 0.015
    return W, ZT, ZB, rng

def burn_first(Wd=880, H=250, seed=8111):
    """اللمسة الأولى: رد فعل حاد من حافة المنطقة وهدف كامل."""
    N = 30
    anch = [(0, 11.0), (4, 10.4), (8, 15.8), (12, 14.2), (16, 11.6), (20, 12.4),
            (24, 16.4), (29, 19.2)]
    W, ZT, ZB, rng = _zone_series(seed, anch, N, 5, [(16, 0.8)], f"محروق أولى {seed}")
    svg, x, y, slot = frame(W, Wd, H)
    svg += zbox(x(4) - slot * .6, y(ZT), x(N - 1) + slot * .5, y(ZB))
    svg += tick(x(17), y(W[17]["h"]) - 18)
    svg += head(Wd, "المنطقة تُختبر للمرة الأولى")
    svg += note(x(8), "حدود المنطقة", TEAL_D, H, 17)
    svg += note(x(24), "رد فعل حاد ← الهدف كاملاً", TEAL_D, H, 17)
    return svg + badge(Wd, "اللمسة الأولى هي الأثمن", True) + "</svg>"

def burn_second(Wd=880, H=250, seed=8112):
    """اللمسة الثانية: توقف أضعف ومسافة أقصر — جزء من الهدف فقط."""
    N = 32
    anch = [(0, 11.2), (4, 10.6), (9, 16.2), (13, 14.0), (17, 11.8), (21, 14.6),
            (25, 12.2), (28, 14.0), (31, 13.4)]
    W, ZT, ZB, rng = _zone_series(seed, anch, N, 5, [(17, 0.55), (25, 0.9)], f"محروق ثانية {seed}")
    svg, x, y, slot = frame(W, Wd, H)
    svg += zbox(x(4) - slot * .6, y(ZT), x(N - 1) + slot * .5, y(ZB))
    svg += tick(x(18), y(W[18]["h"]) - 18)
    svg += head(Wd, "اللمسة الثانية على المنطقة نفسها")
    svg += note(x(9), "الأولى: دفعة كاملة", TEAL_D, H, 17)
    svg += note(x(26), "الثانية: مسافة أقصر", RED, H, 17)
    return svg + badge(Wd, "نصف الهدف", True) + "</svg>"

def burn_third(Wd=880, H=250, seed=8113):
    """اللمسة الثالثة: السعر يعبر بلا توقف — المنطقة استُهلكت."""
    N = 32
    anch = [(0, 11.4), (4, 10.8), (9, 16.0), (13, 13.8), (17, 12.0), (21, 14.2),
            (24, 12.3), (27, 13.6), (31, 9.2)]
    W, ZT, ZB, rng = _zone_series(seed, anch, N, 5, [(17, 0.5), (24, 0.85)],
                                 f"محروق ثالثة {seed}", last=28)
    for j in range(28, N):                              # العبور النهائي
        cap(W, j, ZB - rng * 0.02)
    svg, x, y, slot = frame(W, Wd, H)
    svg += zbox(x(4) - slot * .6, y(ZT), x(N - 1) + slot * .5, y(ZB),
                col=MUTE, stroke=GREY, dash="6 5", op=0.10)
    svg += xm(x(29), y(ZB) + 8)
    svg += head(Wd, "ثلاث لمسات على المنطقة ذاتها")
    svg += note(x(9), "لمستان أُضعفتا المنطقة", GREY, H, 17)
    svg += note(x(26), "الثالثة عبرت بلا توقف", RED, H, 17)
    return svg + badge(Wd, "منطقة مستهلكة", False) + "</svg>"

def burn_flip(Wd=880, H=250, seed=8114):
    """بعد العبور تنقلب المنطقة: تُباع من الأعلى بدل أن تُشترى من الأسفل."""
    N = 32
    anch = [(0, 12.0), (4, 11.4), (8, 16.6), (12, 14.6), (16, 12.6), (20, 10.2),
            (24, 12.3), (28, 10.8), (31, 8.4)]
    W, ZT, ZB, rng = _zone_series(seed, anch, N, 5, [(16, 0.75)],
                                 f"محروق انقلاب {seed}", last=20)
    for j in range(20, 24):
        cap(W, j, ZB - rng * 0.03)
    for j in range(24, 26):                             # العودة تختبرها من الأسفل
        W[j]["h"] = max(W[j]["h"], ZB + (ZT - ZB) * 0.45)
        cap(W, j, ZT - rng * 0.01)
    svg, x, y, slot = frame(W, Wd, H)
    svg += zbox(x(4) - slot * .6, y(ZT), x(N - 1) + slot * .5, y(ZB), op=0.10,
                col=RED, stroke=RED)
    svg += tick(x(27), y(W[27]["l"]) + 24)
    svg += head(Wd, "المنطقة نفسها بعد أن عبرها السعر")
    svg += note(x(9), "كانت تُشترى", GREY, H, 17)
    svg += note(x(26), "صارت تُباع ← الهدف للأسفل", RED, H, 17)
    return svg + badge(Wd, "انقلبت بعد العبور", True) + "</svg>"

def burn_redraw(Wd=880, H=250, seed=8115):
    """توسيع حدود المنطقة بعد اللمسة الثانية — وقف بلا مبرر ثم خسارة أكبر."""
    N = 30
    anch = [(0, 11.6), (4, 11.0), (8, 15.8), (12, 14.0), (16, 12.2), (20, 13.8),
            (24, 11.9), (29, 9.0)]
    W, ZT, ZB, rng = _zone_series(seed, anch, N, 5, [(16, 0.55), (24, 0.95)],
                                 f"محروق توسيع {seed}", last=26)
    for j in range(26, N):
        cap(W, j, ZB - rng * 0.03)
    WIDE = ZB - rng * 0.10
    svg, x, y, slot = frame(W, Wd, H)
    svg += zbox(x(4) - slot * .6, y(ZT), x(N - 1) + slot * .5, y(ZB))
    svg += zbox(x(20) - slot * .6, y(ZB), x(N - 1) + slot * .5, y(WIDE), op=0.09,
                col=RED, stroke=RED, dash="6 5")
    svg += xm(x(27), y(W[27]["l"]) + 6)
    svg += head(Wd, "المتصل: الحدود الأصلية · المتقطع: التوسيع")
    svg += note(x(9), "الحدود التي رسمتها أولاً", TEAL_D, H, 17)
    svg += note(x(25), "التوسيع وسّع الخسارة", RED, H, 17)
    return svg + badge(Wd, "وقف بلا مبرر", False) + "</svg>"


# ══════════════════ 3) آسيا — نطاق الجلسة الآسيوية ══════════════════
def _asia(seed, anch, N, iEnd, label, wick=0.7, squeeze=0.55):
    """يضغط أول iEnd شمعة داخل صندوق ضيق = نطاق الجلسة الآسيوية."""
    fresh(seed, anch, label)
    W = gen(anch, N, seed, wick=wick)
    rng = max(c["h"] for c in W) - min(c["l"] for c in W)
    mid = sum(c["c"] for c in W[:iEnd]) / iEnd
    half = rng * squeeze * 0.30
    for j in range(iEnd):                               # ضغط الشموع داخل الصندوق
        for k in ("o", "c", "h", "l"):
            W[j][k] = mid + (W[j][k] - mid) * 0.42
        W[j]["h"] = min(W[j]["h"], mid + half); W[j]["l"] = max(W[j]["l"], mid - half)
        W[j]["o"] = min(max(W[j]["o"], W[j]["l"]), W[j]["h"])
        W[j]["c"] = min(max(W[j]["c"], W[j]["l"]), W[j]["h"])
    AH = max(c["h"] for c in W[:iEnd]); AL = min(c["l"] for c in W[:iEnd])
    return W, AH, AL, rng

def asia_sweep(Wd=880, H=250, seed=8121):
    """لندن تسحب أدنى النطاق بفتيل ثم تُغلق فوقه وتتجه للأعلى."""
    N = 32
    anch = [(0, 14.0), (10, 14.0), (14, 13.4), (17, 14.6), (22, 15.9), (31, 16.8)]
    W, AH, AL, rng = _asia(seed, anch, N, 14, f"آسيا سحب {seed}")
    W[15].update(l=AL - rng * 0.055, o=AL + rng * 0.01,
                 c=AL + rng * 0.03, h=AL + rng * 0.045)
    for j in range(16, N):
        floorc(W, j, AL + rng * 0.01)
    svg, x, y, slot = frame(W, Wd, H)
    svg += zbox(x(0) - slot * .4, y(AH), x(13) + slot * .5, y(AL))
    svg += hl(x(0) - slot * .4, x(N - 1) + slot * .5, y(AL), INK, 1.6, dash="6 5")
    svg += tick(x(17), y(W[17]["h"]) - 18)
    svg += head(Wd, "لندن تسحب أدنى النطاق ثم تُغلق فوقه")
    svg += note(x(6), "نطاق آسيا", TEAL_D, H, 17)
    svg += note(x(24), "الهدف: أعلى النطاق وما فوقه", TEAL_D, H, 17)
    return svg + badge(Wd, "دخول بعد الإغلاق", True) + "</svg>"

def asia_break(Wd=880, H=250, seed=8122):
    """اختراق حقيقي بإغلاق كامل خارج النطاق ثم إعادة اختبار من الأعلى."""
    N = 32
    anch = [(0, 13.4), (11, 13.4), (15, 14.6), (19, 14.2), (23, 15.6), (31, 16.6)]
    W, AH, AL, rng = _asia(seed, anch, N, 12, f"آسيا اختراق {seed}")
    for j in range(13, 16):
        floorc(W, j, AH + rng * 0.055)
    for j in range(18, 21):                              # إعادة اختبار من الأعلى
        W[j]["l"] = min(W[j]["l"], AH + rng * 0.008); floorc(W, j, AH)
    svg, x, y, slot = frame(W, Wd, H)
    svg += zbox(x(0) - slot * .4, y(AH), x(11) + slot * .5, y(AL))
    svg += hl(x(0) - slot * .4, x(N - 1) + slot * .5, y(AH), INK, 1.8)
    svg += tick(x(19), y(W[19]["l"]) + 24)
    svg += head(Wd, "إغلاق كامل خارج الحدّ ثم إعادة اختبار")
    svg += note(x(6), "نطاق آسيا", TEAL_D, H, 17)
    svg += note(x(24), "إعادة الاختبار ← الاستمرار", TEAL_D, H, 17)
    return svg + badge(Wd, "دخول من إعادة الاختبار", True) + "</svg>"

def asia_inside(Wd=880, H=250, seed=8123):
    """التداول داخل النطاق نفسه: ذهاب وإياب يأكل الحساب بلا اتجاه."""
    N = 30
    anch = [(0, 13.8), (10, 13.8), (16, 13.9), (23, 13.7), (29, 13.8)]
    W, AH, AL, rng = _asia(seed, anch, N, 12, f"آسيا داخل {seed}", squeeze=0.8)
    for j in range(12, N):                               # يبقى داخل الصندوق
        cap(W, j, AH - rng * 0.004); floorc(W, j, AL + rng * 0.004)
    svg, x, y, slot = frame(W, Wd, H)
    svg += zbox(x(0) - slot * .4, y(AH), x(N - 1) + slot * .5, y(AL), op=0.09,
                col=MUTE, stroke=GREY, dash="6 5")
    for j in (14, 19, 24):
        svg += xm(x(j), y(W[j]["c"]), r=9)
    svg += head(Wd, "السعر لم يغادر النطاق طوال الجلسة")
    svg += note(x(6), "حدود النطاق", GREY, H, 17)
    svg += note(x(23), "ثلاث محاولات… ثلاث خسائر", RED, H, 17)
    return svg + badge(Wd, "لا اتجاه… لا صفقة", False) + "</svg>"

def asia_wide(Wd=880, H=250, seed=8124):
    """نطاق واسع بلا هامش: الوقف خلف الحدّ يجعل العائد أصغر من المخاطرة."""
    N = 30
    anch = [(0, 12.6), (4, 15.4), (8, 12.2), (12, 15.2), (16, 13.0), (22, 15.6), (29, 14.6)]
    W, AH, AL, rng = _asia(seed, anch, N, 16, f"آسيا واسع {seed}", squeeze=1.15)
    for j in range(16, N):                              # لا شيء يغادر النطاق
        cap(W, j, AH - rng * 0.004); floorc(W, j, AL + rng * 0.004)
    svg, x, y, slot = frame(W, Wd, H, pr=64)
    svg += zbox(x(0) - slot * .4, y(AH), x(N - 1) + slot * .5, y(AL), op=0.10,
                col=MUTE, stroke=GREY)
    bx = x(N - 1) + slot * 0.9
    svg += (f'<line x1="{bx:.1f}" y1="{y(AH):.1f}" x2="{bx:.1f}" y2="{y(AL):.1f}" stroke="{RED}" stroke-width="2.4"/>'
            f'<line x1="{bx-10:.1f}" y1="{y(AH):.1f}" x2="{bx+10:.1f}" y2="{y(AH):.1f}" stroke="{RED}" stroke-width="2.4"/>'
            f'<line x1="{bx-10:.1f}" y1="{y(AL):.1f}" x2="{bx+10:.1f}" y2="{y(AL):.1f}" stroke="{RED}" stroke-width="2.4"/>')
    svg += head(Wd, "نطاق آسيا اتسع حتى صار الوقف أكبر من الهدف")
    svg += note(x(7), "حدود النطاق", GREY, H, 17)
    svg += note(x(23), "الوقف خلف الحدّ = مخاطرة كبيرة", RED, H, 17)
    return svg + badge(Wd, "يوم بلا صفقة", False) + "</svg>"

def asia_double(Wd=880, H=250, seed=8125):
    """سحب الجهتين: الأدنى ثم الأعلى — الدخول بعد الثانية لا الأولى."""
    N = 34
    anch = [(0, 14.2), (11, 14.2), (15, 13.6), (19, 15.2), (23, 14.4), (28, 12.9), (33, 12.1)]
    W, AH, AL, rng = _asia(seed, anch, N, 13, f"آسيا مزدوج {seed}")
    W[15].update(l=AL - rng * 0.05, o=AL, c=AL + rng * 0.025, h=AL + rng * 0.04)
    W[20].update(h=AH + rng * 0.05, o=AH - rng * 0.01, c=AH - rng * 0.03, l=AH - rng * 0.05)
    for j in range(21, N):
        cap(W, j, AH - rng * 0.02)
    svg, x, y, slot = frame(W, Wd, H)
    svg += zbox(x(0) - slot * .4, y(AH), x(12) + slot * .5, y(AL))
    svg += hl(x(0) - slot * .4, x(N - 1) + slot * .5, y(AL), MUTE, 1.5, dash="6 5")
    svg += hl(x(0) - slot * .4, x(N - 1) + slot * .5, y(AH), INK, 1.7)
    svg += xm(x(15), y(W[15]["l"]) + 8, r=9)
    svg += tick(x(21), y(W[21]["l"]) + 24)
    svg += head(Wd, "سحب للأدنى ثم سحب للأعلى في الجلسة ذاتها")
    svg += note(x(7), "السحب الأول: فخّ", GREY, H, 17)
    svg += note(x(26), "بعد الثاني يبدأ الاتجاه", TEAL_D, H, 17)
    return svg + badge(Wd, "ادخل بعد الثانية", True) + "</svg>"


# ══════════════════ 4) سبريد — التكلفة الخفية ══════════════════
def _spread_series(seed, anch, N, iEnt, label, wick=0.75):
    fresh(seed, anch, label)
    W = gen(anch, N, seed, wick=wick)
    rng = max(c["h"] for c in W) - min(c["l"] for c in W)
    return W, W[iEnt]["c"], rng

def _cost_bar(x0, Wd, ytop, ybot, frac, txt):
    """شريط أفقي يقارن التكلفة بالهدف: الجزء الأحمر = ما يأخذه السبريد."""
    w = Wd - x0 - 30
    h = 26
    yy = ybot
    return (f'<rect x="{x0}" y="{yy-h}" width="{w}" height="{h}" fill="#EAF3F5" stroke="{TEAL_D}" stroke-width="1.2"/>'
            f'<rect x="{x0}" y="{yy-h}" width="{w*frac:.1f}" height="{h}" fill="{RED}" opacity="0.55"/>'
            + htext(x0 + w / 2, yy - h + 19, txt, INK, 17))

def spread_thin(Wd=880, H=250, seed=8131):
    """هدف عشر نقاط وتكلفة ثلاث: ثلث الحركة يذهب قبل أن تبدأ."""
    N = 26
    anch = [(0, 12.0), (6, 11.6), (10, 12.1), (14, 12.6), (19, 13.0), (25, 12.8)]
    W, ENT, rng = _spread_series(seed, anch, N, 10, f"سبريد ضيق الهدف {seed}")
    TGT = ENT + rng * 0.30
    ASK = ENT + rng * 0.09
    svg, x, y, slot = frame(W, Wd, H, pb=76)
    svg += zbox(x(9) - slot * .5, y(ASK), x(N - 1) + slot * .5, y(ENT), op=0.16,
                col=RED, stroke=RED)
    svg += hl(x(9) - slot * .5, x(N - 1) + slot * .5, y(TGT), TEAL_D, 1.7)
    svg += head(Wd, "الشريط الأحمر: السبريد ٣ · الخط: الهدف ١٠")
    svg += _cost_bar(40, Wd, 0, H - 16, 0.30, "التكلفة تأكل ٣٠٪ من الحركة")
    return svg + badge(Wd, "هامش لا يكفي", False) + "</svg>"

def spread_wide(Wd=880, H=250, seed=8132):
    """النموذج نفسه بهدف أربعين نقطة: التكلفة تنكمش إلى جزء صغير."""
    N = 30
    anch = [(0, 11.4), (6, 10.9), (10, 11.5), (16, 14.2), (23, 16.4), (29, 17.6)]
    W, ENT, rng = _spread_series(seed, anch, N, 10, f"سبريد هدف واسع {seed}")
    TGT = ENT + rng * 0.62
    ASK = ENT + rng * 0.045
    svg, x, y, slot = frame(W, Wd, H, pb=76)
    svg += zbox(x(9) - slot * .5, y(ASK), x(N - 1) + slot * .5, y(ENT), op=0.16,
                col=RED, stroke=RED)
    svg += hl(x(9) - slot * .5, x(N - 1) + slot * .5, y(TGT), TEAL_D, 1.7)
    svg += tick(x(28), y(W[28]["h"]) - 18)
    svg += head(Wd, "السبريد نفسه · الهدف ٤٠ نقطة")
    svg += _cost_bar(40, Wd, 0, H - 16, 0.075, "التكلفة ٧٪ فقط — النموذج نفسه")
    return svg + badge(Wd, "المسافة تحتمل التكلفة", True) + "</svg>"

def spread_open(Wd=880, H=250, seed=8133):
    """عند فتح الجلسة يتسع السبريد فيُنفَّذ أمرك بعيداً عن السعر الذي رأيته."""
    N = 28
    anch = [(0, 12.4), (8, 12.2), (11, 12.4), (15, 13.4), (20, 13.0), (27, 13.6)]
    W, ENT, rng = _spread_series(seed, anch, N, 11, f"سبريد الافتتاح {seed}")
    NARROW = ENT + rng * 0.045
    WIDEV = ENT + rng * 0.17
    svg, x, y, slot = frame(W, Wd, H)
    svg += zbox(x(0) - slot * .4, y(NARROW), x(10) + slot * .4, y(ENT), op=0.14,
                col=GREY, stroke=GREY)
    svg += zbox(x(10) + slot * .4, y(WIDEV), x(15) + slot * .5, y(ENT - rng * 0.03),
                op=0.18, col=RED, stroke=RED)
    svg += xm(x(12), y(W[12]["c"]), r=10)
    svg += head(Wd, "عرض السبريد قبل الافتتاح وبعده")
    svg += note(x(5), "هادئ وضيق", GREY, H, 17)
    svg += note(x(20), "اتسع لحظة الافتتاح", RED, H, 17)
    return svg + badge(Wd, "توقيت تنفيذ خاطئ", False) + "</svg>"

def spread_limit(Wd=880, H=250, seed=8134):
    """أمر معلق داخل المنطقة: السعر يأتي إليك فتدفع تكلفة واحدة لا اثنتين."""
    N = 30
    anch = [(0, 11.0), (5, 14.6), (9, 13.4), (14, 11.4), (18, 12.6), (24, 15.2), (29, 17.0)]
    fresh(seed, anch, f"سبريد أمر معلق {seed}")
    W = gen(anch, N, seed, wick=0.78)
    rng = max(c["h"] for c in W) - min(c["l"] for c in W)
    seg = W[3:6]
    ZT = max(max(c["o"], c["c"]) for c in seg); ZB = min(c["l"] for c in seg)
    ZT = ZB + (ZT - ZB) * 0.55
    for j in range(13, 16):
        W[j]["l"] = min(W[j]["l"], ZB + rng * 0.012); floorc(W, j, ZB)
    svg, x, y, slot = frame(W, Wd, H)
    svg += zbox(x(3) - slot * .5, y(ZT), x(N - 1) + slot * .5, y(ZB))
    svg += (f'<line x1="{x(9)-slot*.5:.1f}" y1="{y((ZT+ZB)/2):.1f}" x2="{x(N-1)+slot*.5:.1f}" '
            f'y2="{y((ZT+ZB)/2):.1f}" stroke="{INK}" stroke-width="1.9" stroke-dasharray="9 5"/>')
    svg += tick(x(16), y(W[16]["h"]) - 18)
    svg += head(Wd, "المتقطع: أمر معلق موضوع قبل وصول السعر")
    svg += note(x(7), "المنطقة", TEAL_D, H, 17)
    svg += note(x(24), "تنفيذ واحد ← تكلفة واحدة", TEAL_D, H, 17)
    return svg + badge(Wd, "السعر يأتي إليك", True) + "</svg>"

def spread_count(Wd=880, H=250, seed=8135):
    """عشر صفقات صغيرة مقابل صفقتين: التكلفة تتراكم بعدد التنفيذات لا بحجمها."""
    N = 30
    anch = [(0, 12.0), (7, 12.6), (13, 12.2), (19, 12.9), (25, 12.4), (29, 12.8)]
    fresh(seed, anch, f"سبريد تراكم {seed}")
    W = gen(anch, N, seed, wick=0.7)
    svg, x, y, slot = frame(W, Wd, H, pb=76)
    for j in (3, 6, 9, 12, 15, 18, 21, 24, 27):
        svg += (f'<line x1="{x(j):.1f}" y1="{y(W[j]["l"])+14:.1f}" x2="{x(j):.1f}" '
                f'y2="{y(W[j]["h"])-14:.1f}" stroke="{RED}" stroke-width="1.4" stroke-dasharray="4 4" opacity="0.85"/>')
    svg += head(Wd, "كل خط أحمر = تنفيذ واحد بتكلفته")
    svg += _cost_bar(40, Wd, 0, H - 16, 0.62, "تسع تنفيذات: المحصلة سالبة قبل أول خطأ")
    return svg + badge(Wd, "العدد لا الحجم", False) + "</svg>"


# ══════════════════ 5) غرور — الثقة الزائدة بعد سلسلة ══════════════════
def _equity(Wd, H, vals, sizes, hi_idx=None, pad=0.16):
    """منحنى حساب + أعمدة حجم أسفل كل نقطة. vals نسب مئوية من رأس المال."""
    lo, hi = min(vals), max(vals); rng = max(hi - lo, 1e-6)
    lo -= rng * pad; hi += rng * pad
    pl, pr, pt, pb = 46, 44, 58, 96
    x = lambda i: pl + (Wd - pl - pr) * (i / max(len(vals) - 1, 1))
    y = lambda v: pt + (hi - v) / (hi - lo) * (H - pt - pb)
    s = [f'<svg class="chartsvg" viewBox="0 0 {Wd} {H}" width="{Wd}" height="{H}" '
         f'xmlns="http://www.w3.org/2000/svg"><rect width="{Wd}" height="{H}" fill="{CARD}"/>']
    for k in range(5):
        gy = pt + (H - pt - pb) * k / 4
        s.append(f'<line x1="{pl}" y1="{gy:.1f}" x2="{Wd-pr}" y2="{gy:.1f}" stroke="rgba(15,46,60,0.06)" stroke-width="1"/>')
    base = H - pb + 4
    mx = max(sizes) or 1
    for i, sz in enumerate(sizes):                      # أعمدة الحجم
        bh = 30 * sz / mx
        col = RED if (hi_idx is not None and i in hi_idx) else TEAL_D
        s.append(f'<rect x="{x(i)-9:.1f}" y="{base:.1f}" width="18" height="{bh:.1f}" fill="{col}" opacity="0.5"/>')
    pts = " ".join(f"{x(i):.1f},{y(v):.1f}" for i, v in enumerate(vals))
    s.append(f'<polyline points="{pts}" fill="none" stroke="{INK}" stroke-width="2.6" '
             f'stroke-linejoin="round" stroke-linecap="round"/>')
    for i, v in enumerate(vals):
        s.append(f'<circle cx="{x(i):.1f}" cy="{y(v):.1f}" r="4.6" fill="{CARD}" stroke="{INK}" stroke-width="2.2"/>')
    s.append(htext(Wd - 20, base + 48, "حجم المخاطرة لكل صفقة", GREY, 15, anchor="start"))
    return "".join(s), x, y, base

def ego_steady(Wd=880, H=250, seed=8141):
    """أربع صفقات رابحة بحجم ثابت: المنحنى يصعد بخطوات متساوية."""
    vals = [100, 101.6, 103.1, 104.9, 106.4]
    svg, x, y, base = _equity(Wd, H, vals, [1, 1, 1, 1, 1])
    svg += head(Wd, "أربع صفقات رابحة بحجم مخاطرة واحد")
    svg += tick(x(4) - 26, y(106.4) - 16)
    return svg + badge(Wd, "خطوات متساوية", True) + "</svg>"

def ego_double(Wd=880, H=250, seed=8142):
    """مضاعفة الحجم بعد الثالثة: خسارة واحدة تمحو السلسلة كاملة."""
    vals = [100, 101.7, 103.4, 105.2, 98.1]
    svg, x, y, base = _equity(Wd, H, vals, [1, 1, 1, 1, 4], hi_idx={4})
    svg += head(Wd, "العمود الأخير: أربعة أضعاف الحجم")
    svg += xm(x(4) - 26, y(98.1) + 8)
    svg += htext(Wd / 2, H - 14, "خسارة واحدة محت الصفقات الأربع", RED, 18)
    return svg + badge(Wd, "الحجم لا الإشارة", False) + "</svg>"

def ego_noplan(Wd=880, H=250, seed=8143):
    """دخول بلا شرط لأن «اليوم يومك» — صفقة خارج النموذج تنتهي بوقف نظيف."""
    N = 28
    anch = [(0, 12.2), (5, 14.8), (9, 13.6), (13, 15.4), (17, 14.2), (21, 11.8), (27, 10.4)]
    fresh(seed, anch, f"غرور بلا شرط {seed}")
    W = gen(anch, N, seed, wick=0.8)
    rng = max(c["h"] for c in W) - min(c["l"] for c in W)
    ENT = W[16]["c"]
    STP = ENT - rng * 0.10
    svg, x, y, slot = frame(W, Wd, H)
    svg += hl(x(15) - slot * .6, x(N - 1) + slot * .5, y(ENT), INK, 1.9)
    svg += hl(x(15) - slot * .6, x(N - 1) + slot * .5, y(STP), RED, 1.6, dash="7 5")
    svg += xm(x(21), y(STP) + 8)
    svg += head(Wd, "المتصل: الدخول · المتقطع: الوقف")
    svg += note(x(8), "لا منطقة ولا هيكل", INK, H, 17)
    svg += note(x(22), "وقف نظيف بلا مبرر للدخول", RED, H, 17)
    return svg + badge(Wd, "خارج النموذج", False) + "</svg>"

def ego_reset(Wd=880, H=250, seed=8144):
    """العودة إلى الحجم الثابت بعد الخسارة: التعافي بطيء لكنه يحدث."""
    vals = [98.1, 98.9, 99.7, 100.6, 101.5, 102.3]
    svg, x, y, base = _equity(Wd, H, vals, [1, 1, 1, 1, 1, 1])
    svg += head(Wd, "العودة إلى الحجم الثابت بعد الخسارة")
    svg += tick(x(5) - 26, y(102.3) - 16)
    svg += htext(Wd / 2, H - 14, "تعافٍ بطيء بلا محاولة تعويض", TEAL_D, 18)
    return svg + badge(Wd, "تعافٍ منضبط", True) + "</svg>"

def ego_curve(Wd=880, H=250, seed=8145):
    """منحنى شهر كامل: القمة قبل الغرور والحفرة بعده."""
    vals = [100, 101.2, 102.6, 104.3, 106.0, 107.4, 99.8, 96.4, 97.3, 98.6]
    sizes = [1, 1, 1, 1, 1, 1, 3.5, 3, 1, 1]
    svg, x, y, base = _equity(Wd, H, vals, sizes, hi_idx={6, 7})
    svg += head(Wd, "عشرة أسابيع: الأعمدة الحمراء حجم مضاعف")
    svg += xm(x(7), y(96.4) - 6)
    svg += htext(Wd / 2, H - 14, "ستة أسابيع انضباط… محاها أسبوعان", RED, 18)
    return svg + badge(Wd, "الحفرة بعد القمة", False) + "</svg>"


# ─────────────────────────── الخرائط ───────────────────────────
CAR_CHARTS = {
    "choch":  [choch_full, choch_wick, choch_inner, choch_align, choch_chase],
    "burn":   [burn_first, burn_second, burn_third, burn_flip, burn_redraw],
    "asia":   [asia_sweep, asia_break, asia_inside, asia_wide, asia_double],
    "spread": [spread_thin, spread_wide, spread_open, spread_limit, spread_count],
    "ego":    [ego_steady, ego_double, ego_noplan, ego_reset, ego_curve],
}
HERO = {"choch": choch_full, "burn": burn_first, "asia": asia_sweep,
        "spread": spread_wide, "ego": ego_curve}
