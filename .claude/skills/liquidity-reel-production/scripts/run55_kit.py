# -*- coding: utf-8 -*-
"""تشغيلة ٥٥ — عُدّة الرسم واللوحة لدفعة الكاروسيلات متعدّدة المدارس.

🔒 لوحة الألوان والخطوط هنا **من أمر فهد 2026-08-12 نصّاً** (الغلاف
`#020F1A`، المحتوى `#F9F6F1`، العناوين `#0B2635`، التعليمي `#257A93`…)،
وهي تختلف عن كريم §1 المعتاد. الأمر الأحدث والأصرح يفوز، ولذلك تعيش هذه
اللوحة في ملفٍ مستقل بدل أن تُقحَم على `car_common` وتكسر ما بُني عليه.

الخطوط: IBM Plex Sans Arabic للعربية وInter للأرقام اللاتينية — منزّلة
محلياً ومضمَّنة base64، لأن التحميل الخارجي وقت الرندر يعطي صفحةً بلا خط.

كل ما هنا رسمٌ لا محتوى: الشموع تُرسم من OHLC كما هي بلا تجميل، والحجم من
الحجم، والبروفايل من `run55_facts.vprofile`، والـVWAP من حسابه الكامل.
"""
import base64, math, os

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(HERE, "fonts")

# ═════════════════════ اللوحة (أمر فهد 2026-08-12) ═════════════════════
DK_BG = "#020F1A"        # خلفية الغلاف
DK_2 = "#061824"         # الكحلي المساند
DK_TX = "#F7FAFB"        # نص الغلاف
FOCUS = "#20939E"        # لون التركيز على الغلاف

BG = "#F9F6F1"           # خلفية صفحات المحتوى
INK = "#0B2635"          # العناوين
EDU = "#257A93"          # اللون التعليمي
SUB = "#6A7B84"          # النص الثانوي
CARD = "#D9E3E3"         # البطاقات
LINE = "#B4C8CC"         # الحدود
RED = "#DF7573"          # التحذير والرفض والإبطال — لا غير
GRN = "#9FCC9E"          # التأكيد الإيجابي — لا غير

BULL = EDU               # الشمعة الصاعدة: تركواز
BEAR = INK               # الشمعة الهابطة: كحلي داكن
GRID = "rgba(11,38,53,0.07)"


def _ff(name, file, weight, style="normal"):
    p = os.path.join(FONTS, file)
    b = base64.b64encode(open(p, "rb").read()).decode()
    return (f"@font-face{{font-family:'{name}';font-style:{style};"
            f"font-weight:{weight};src:url(data:font/ttf;base64,{b}) "
            f"format('truetype')}}")


FONT_CSS = "\n".join([
    _ff("PlexAr", "IBMPlexSansArabic-Regular.ttf", 400),
    _ff("PlexAr", "IBMPlexSansArabic-Medium.ttf", 500),
    _ff("PlexAr", "IBMPlexSansArabic-SemiBold.ttf", 600),
    _ff("PlexAr", "IBMPlexSansArabic-Bold.ttf", 700),
    _ff("Inter", "Inter-var.ttf", "100 900"),
])


# ═════════════════════ نصّ داخل SVG ═════════════════════
def t(x, y, s, col=INK, fs=20, w=600, anchor="middle", rtl=True,
      halo=None, op=1.0, fam=None):
    """نصّ بهالةٍ بلون الخلفية بدل الإطار — القاعدة §3 المعتمدة.

    الهالة تُرسم بـ`paint-order:stroke` فيبقى الحرف نظيفاً فوق الشموع بلا
    صندوقٍ يحجبها."""
    h = BG if halo is None else halo
    d = ' direction="rtl"' if rtl else ' direction="ltr"'
    f = fam or ("PlexAr,sans-serif" if rtl else "Inter,PlexAr,sans-serif")
    return (f'<text x="{x:.1f}" y="{y:.1f}" fill="{col}" font-size="{fs}" '
            f'font-weight="{w}" font-family="{f}" text-anchor="{anchor}"'
            f'{d} opacity="{op}" style="paint-order:stroke;stroke:{h};'
            f'stroke-width:6px;stroke-linejoin:round">{s}</text>')


def num(v, dp=2):
    """رقم لاتيني معزول باتجاهه كي لا ينقلب داخل جملة عربية."""
    return f"⁦{v:,.{dp}f}⁩"


def dnum(s):
    return f"⁦{s}⁩"


# ═════════════════════ لوحة الشارت ═════════════════════
class Panel:
    """محوّل إحداثيات لنافذة شموع: زمنٌ بالفهرس وسعرٌ بالقيمة.

    الرسم بالفهرس لا بالزمن — وهذا يفرض أن تكون الشموع متتالية بلا فجوات
    (قاعدة فهد)، وبيانات اليوم الواحد للصناديق كذلك بحكم الجلسة.
    """

    def __init__(self, bars, i0, i1, W, H, pad=None, vol_h=0, prof_w=0):
        self.b, self.i0, self.i1 = bars, i0, i1
        self.W, self.H = W, H
        p = dict(l=16, r=96, t=30, b=44)
        if pad:
            p.update(pad)
        self.p = p
        self.vol_h = vol_h
        self.prof_w = prof_w
        seg = bars[i0:i1 + 1]
        self.lo = min(c["l"] for c in seg)
        self.hi = max(c["h"] for c in seg)
        self.n = len(seg)

    def ext(self, lo=None, hi=None):
        """يوسّع مدى السعر ليشمل مستوى خارج الشموع (وقف/هدف/خط)."""
        if lo is not None:
            self.lo = min(self.lo, lo)
        if hi is not None:
            self.hi = max(self.hi, hi)
        return self

    def fin(self, m=0.06):
        span = self.hi - self.lo
        self.LO = self.lo - span * m
        self.HI = self.hi + span * m
        self.px0 = self.p["l"] + self.prof_w
        self.px1 = self.W - self.p["r"]
        self.py0 = self.p["t"]
        self.py1 = self.H - self.p["b"] - self.vol_h
        self.slot = (self.px1 - self.px0) / self.n
        return self

    def x(self, i):
        return self.px0 + (i - self.i0 + 0.5) * self.slot

    def y(self, v):
        return self.py1 - (v - self.LO) / (self.HI - self.LO) * (self.py1 - self.py0)

    # ── الشموع ──
    def candles(self, wick=1.7):
        s = []
        bw = max(3.0, self.slot * 0.62)
        for i in range(self.i0, self.i1 + 1):
            c = self.b[i]
            up = c["c"] >= c["o"]
            col = BULL if up else BEAR
            X = self.x(i)
            s.append(f'<line x1="{X:.1f}" y1="{self.y(c["h"]):.1f}" x2="{X:.1f}" '
                     f'y2="{self.y(c["l"]):.1f}" stroke="{col}" '
                     f'stroke-width="{wick}"/>')
            yo, yc = self.y(c["o"]), self.y(c["c"])
            top, hgt = min(yo, yc), max(1.6, abs(yc - yo))
            s.append(f'<rect x="{X - bw / 2:.1f}" y="{top:.1f}" width="{bw:.1f}" '
                     f'height="{hgt:.1f}" fill="{col}"/>')
        return "".join(s)

    # ── شبكة ومحاور ──
    def grid(self, rows=5):
        s = []
        for k in range(rows + 1):
            v = self.LO + (self.HI - self.LO) * k / rows
            Y = self.y(v)
            s.append(f'<line x1="{self.px0:.1f}" y1="{Y:.1f}" x2="{self.px1:.1f}" '
                     f'y2="{Y:.1f}" stroke="{GRID}" stroke-width="1"/>')
            s.append(t(self.px1 + 10, Y + 6, num(v, self.dp()), SUB, 17, 500,
                       "start", rtl=False, halo=BG))
        return "".join(s)

    def dp(self):
        return 2 if self.hi < 1000 else 0

    def times(self, every=None, fs=16):
        """وسوم زمن مختصرة MM-DD، معزولة باتجاهها كي لا تنقلب."""
        every = every or max(1, self.n // 7)
        s = []
        for i in range(self.i0, self.i1 + 1):
            if (i - self.i0) % every:
                continue
            X = self.x(i)
            if X < self.px0 + 12 or X > self.px1 - 12:
                continue
            s.append(t(X, self.py1 + (self.vol_h + 30 if self.vol_h else 26),
                       dnum(self.b[i]["d"][5:]), SUB, fs, 500, "middle",
                       rtl=False, halo=BG))
        return "".join(s)

    # ── الحجم ──
    def volume(self, hi_i=()):
        """أعمدة الحجم أسفل الشموع — مصدرها حجم المصدر نفسه، لا تقدير."""
        if not self.vol_h:
            return ""
        seg = self.b[self.i0:self.i1 + 1]
        mx = max(c["v"] for c in seg)
        y0 = self.py1 + 16
        y1 = y0 + self.vol_h - 22
        s = [f'<line x1="{self.px0:.1f}" y1="{y0 - 6:.1f}" x2="{self.px1:.1f}" '
             f'y2="{y0 - 6:.1f}" stroke="{LINE}" stroke-width="1"/>']
        bw = max(3.0, self.slot * 0.62)
        for i in range(self.i0, self.i1 + 1):
            c = self.b[i]
            h = (c["v"] / mx) * (y1 - y0)
            col = EDU if i in hi_i else (BULL if c["c"] >= c["o"] else BEAR)
            op = 1.0 if i in hi_i else 0.42
            s.append(f'<rect x="{self.x(i) - bw / 2:.1f}" y="{y1 - h:.1f}" '
                     f'width="{bw:.1f}" height="{h:.1f}" fill="{col}" '
                     f'opacity="{op}"/>')
        s.append(t(self.px1 + 10, y0 + 12, "الحجم", SUB, 16, 600, "start"))
        return "".join(s)

    # ── البروفايل ──
    def profile(self, P, poc=True, marks=()):
        """بروفايل أفقي بجانب محور السعر — أعمدة من الحافة اليسرى.

        `marks` = [(سعر, لون, وسم)] لتمييز عقدةٍ بعينها."""
        if not self.prof_w:
            return ""
        mx = max(P["cells"])
        s = []
        for k, v in enumerate(P["cells"]):
            pr = P["price"](k)
            if not (self.LO <= pr <= self.HI):
                continue
            hgt = max(1.5, (P["step"] / (self.HI - self.LO)) *
                      (self.py1 - self.py0) * 0.86)
            w = (v / mx) * (self.prof_w - 10)
            col = EDU
            op = 0.22
            for mp, mc, _ in marks:
                if abs(pr - mp) < P["step"] * 0.5:
                    col, op = mc, 0.85
            s.append(f'<rect x="{self.p["l"]:.1f}" y="{self.y(pr) - hgt / 2:.1f}" '
                     f'width="{w:.1f}" height="{hgt:.1f}" fill="{col}" '
                     f'opacity="{op}"/>')
        if poc:
            Y = self.y(P["poc_price"])
            s.append(f'<line x1="{self.p["l"]:.1f}" y1="{Y:.1f}" '
                     f'x2="{self.px1:.1f}" y2="{Y:.1f}" stroke="{EDU}" '
                     f'stroke-width="1.6" stroke-dasharray="7 5"/>')
        return "".join(s)

    # ── خطوط ومناطق ──
    def hline(self, v, col=INK, w=1.8, dash=None, x0=None, x1=None, ends=True):
        a = self.px0 if x0 is None else x0
        z = self.px1 if x1 is None else x1
        Y = self.y(v)
        d = f' stroke-dasharray="{dash}"' if dash else ""
        s = (f'<line x1="{a:.1f}" y1="{Y:.1f}" x2="{z:.1f}" y2="{Y:.1f}" '
             f'stroke="{col}" stroke-width="{w}"{d}/>')
        if ends:
            for X in (a, z):
                s += (f'<circle cx="{X:.1f}" cy="{Y:.1f}" r="4.6" fill="{BG}" '
                      f'stroke="{col}" stroke-width="1.6"/>')
        return s

    def label(self, v, txt, col=INK, up=True, x=None, fs=19, side="right"):
        """وسم مستوى داخل اللوحة، على الجانب الذي لا شموع فيه.

        في العربية «البداية» أقصى اليمين: فوسمُ اليمين يُثبَّت بـ`start`
        عند الحافة اليمنى فيمتدّ يساراً، ووسمُ اليسار بـ`end` عند الحافة
        اليسرى فيمتدّ يميناً. و`end` على اليمين كان يدفع النصّ فوق محور
        السعر فيُقصّ — وهو ما أكل «عقدة سميكة» في أول رندر."""
        if x is None:
            x = self.px1 - 10 if side == "right" else self.px0 + 10
        a = "start" if side == "right" else "end"
        return t(x, self.y(v) + (-9 if up else 21), txt, col, fs, 700, a)

    def band(self, lo, hi, col=EDU, op=0.14, x0=None, x1=None, edge=True):
        a = self.px0 if x0 is None else x0
        z = self.px1 if x1 is None else x1
        y0, y1 = self.y(hi), self.y(lo)
        s = (f'<rect x="{a:.1f}" y="{y0:.1f}" width="{z - a:.1f}" '
             f'height="{max(2.0, y1 - y0):.1f}" fill="{col}" opacity="{op}"/>')
        if edge:
            s += (f'<rect x="{a:.1f}" y="{y0:.1f}" width="{z - a:.1f}" '
                  f'height="{max(2.0, y1 - y0):.1f}" fill="none" stroke="{col}" '
                  f'stroke-width="1"/>')
        return s

    def line(self, pts, col=EDU, w=2.4, dash=None):
        p = " ".join(f"{self.x(i):.1f},{self.y(v):.1f}" for i, v in pts)
        d = f' stroke-dasharray="{dash}"' if dash else ""
        return (f'<polyline points="{p}" fill="none" stroke="{col}" '
                f'stroke-width="{w}" stroke-linejoin="round"{d}/>')

    def mark(self, i, v, col=EDU, r=11):
        return (f'<circle cx="{self.x(i):.1f}" cy="{self.y(v):.1f}" r="{r}" '
                f'fill="none" stroke="{col}" stroke-width="2.8"/>')

    def arrow(self, i, v, up=True, col=EDU, size=15):
        """سهم بجانب الشمعة لا فوقها — لا يلامس جسمها."""
        X, Y = self.x(i), self.y(v)
        d = -1 if up else 1
        y0 = Y + d * 34
        s = (f'<line x1="{X:.1f}" y1="{y0:.1f}" x2="{X:.1f}" '
             f'y2="{Y + d * 9:.1f}" stroke="{col}" stroke-width="2.8"/>')
        s += (f'<polygon points="{X:.1f},{Y + d * 3:.1f} '
              f'{X - 6:.1f},{Y + d * 15:.1f} {X + 6:.1f},{Y + d * 15:.1f}" '
              f'fill="{col}"/>')
        return s


def svg(W, H, body, bg="none"):
    return (f'<svg viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
            f'xmlns="http://www.w3.org/2000/svg" style="background:{bg}">'
            f'{body}</svg>')


# ═════════════════════ الفوت برنت — رسم توضيحي ═════════════════════
def footprint(rows, W=880, H=430, title="", note="أرقام تعليمية"):
    """خليّة فوت برنت توضيحية: عرض × طلب لكل مستوى سعر داخل شمعة واحدة.

    🔒 **لا مصدر لبيانات العرض والطلب داخل الشمعة في هذا الخطّ.** فهذه
    أرقامٌ تعليمية معلَنة على الرسم نفسه، لا سوق. الشكل يشرح كيف يُقرأ
    الاختلال القطري والامتصاص — وهو ما يُدرَّس — دون أن يدّعي أنها صفقة.

    rows = [(سعر, بِد, آسك)] من الأعلى إلى الأسفل.
    """
    rw = 430
    x0, y0 = (W - rw) / 2 - 46, 78
    rh = (H - y0 - 62) / len(rows)
    s = [t(W / 2, 36, title, INK, 25, 700)] if title else []
    mx = max(max(b, a) for _, b, a in rows)
    for k, (pr, bid, ask) in enumerate(rows):
        Y = y0 + k * rh
        s.append(f'<rect x="{x0:.1f}" y="{Y:.1f}" width="{rw}" '
                 f'height="{rh - 4:.1f}" fill="none" stroke="{LINE}" '
                 f'stroke-width="1"/>')
        s.append(f'<line x1="{x0 + rw / 2:.1f}" y1="{Y:.1f}" '
                 f'x2="{x0 + rw / 2:.1f}" y2="{Y + rh - 4:.1f}" '
                 f'stroke="{LINE}" stroke-width="1"/>')
        for j, (v, col) in enumerate(((bid, RED), (ask, EDU))):
            cx = x0 + rw * (0.25 + 0.5 * j)
            w = (v / mx) * (rw / 2 - 16)
            s.append(f'<rect x="{cx - w / 2:.1f}" y="{Y + 4:.1f}" '
                     f'width="{w:.1f}" height="{rh - 12:.1f}" fill="{col}" '
                     f'opacity="0.18"/>')
            s.append(t(cx, Y + rh / 2 + 4, dnum(f"{v:,}"), INK, 19, 600,
                       "middle", rtl=False))
        s.append(t(x0 + rw + 16, Y + rh / 2 + 4, num(pr, 2), SUB, 18, 600,
                   "start", rtl=False))
    s.append(t(x0 + rw * 0.25, y0 - 14, "بِـد (بيع)", SUB, 17, 600))
    s.append(t(x0 + rw * 0.75, y0 - 14, "آسك (شراء)", SUB, 17, 600))
    s.append(t(W - 20, H - 14, note, RED, 19, 700, "start"))
    return svg(W, H, "".join(s))
