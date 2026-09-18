# -*- coding: utf-8 -*-
# run12 — «كتاب الألفَين»: 1000 فكرة تحليل فني + 1000 فكرة نفسية (V2: غلاف داكن + أوف وايت، فصحى)
# يدمج مخرجات ايجنتات الكتابة الثمانية، ينقّي التكرار، يرقّم 1..1000 لكل جزء، ويبني HTML للرندر PDF
import json, os, re
from car_common import CSS, FONT_CSS, GEM, CW, brandbar, INK, GREY, TEAL, TEAL_D, MUTE, CARDBD

HERE = os.path.dirname(os.path.abspath(__file__))
CONT = os.path.join(HERE, "..", "content")

TECH_SECTIONS = [("ideas_tech_1", "الشموع والأنماط"),
                 ("ideas_tech_2", "السيولة والهيكل (SMC/ICT)"),
                 ("ideas_tech_3", "المستويات والمؤشرات والفريمات"),
                 ("ideas_tech_4", "التنفيذ وإدارة الصفقة")]
PSY_SECTIONS = [("ideas_psy_1", "الخوف والطمع والفومو"),
                ("ideas_psy_2", "الانضباط والعادات"),
                ("ideas_psy_3", "الانحيازات والتعامل مع الخسارة"),
                ("ideas_psy_4", "إدارة الذات وبيئة التداول")]
PER_SECTION = 250
TIPS_PER_PAGE = 18

_norm_re = re.compile(r"[ً-ْـ]|[^\w\s]")
def norm(s):
    s = _norm_re.sub("", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s.replace("أ", "ا").replace("إ", "ا").replace("آ", "ا").replace("ة", "ه").replace("ى", "ي")

def jac(a, b):
    A, B = set(a.split()), set(b.split())
    return len(A & B) / max(len(A | B), 1)

def load_clean(sections):
    """يحمّل شرائح القسم، ينقّي التكرار داخلها وعبرها، ويقتطع 250 من كل شريحة."""
    seen_keys = set(); kept_norms = []
    out = []
    for fname, label in sections:
        with open(os.path.join(CONT, fname + ".json"), encoding="utf-8") as f:
            raw = json.load(f)
        keep = []
        for tip in raw:
            tip = re.sub(r"^\s*[\d٠-٩]+[\.\-\)\s]+", "", str(tip)).strip()
            if not (20 <= len(tip) <= 220):
                continue
            k = norm(tip)
            if k in seen_keys:
                continue
            if any(jac(k, p) >= 0.72 for p in kept_norms[-600:]):
                continue
            seen_keys.add(k); kept_norms.append(k); keep.append(tip)
            if len(keep) == PER_SECTION:
                break
        if len(keep) < PER_SECTION:
            raise SystemExit(f"{fname}: بقي {len(keep)} فقط بعد التنقية — نحتاج {PER_SECTION}")
        out.append((label, keep))
        print(fname, "->", len(keep), "أفكار نظيفة (من", len(raw), ")")
    return out

def tip_el(n, txt):
    return (f'<div class="tip"><span class="tn">{n}</span><p>{txt}</p></div>')

def tips_pages(sections, part_title, start_page, total_pages, part_cls):
    slides = []
    n = 0
    for label, tips in sections:
        sec_start = n + 1
        # صفحة عنوان القسم
        slides.append(f'''<div class="slide" {CW}>{brandbar(True)}
  <div class="secdiv"><div class="sd1">{part_title}</div>
  <h1 class="sd2">{label}</h1>
  <div class="sd3">الأفكار {sec_start} – {sec_start + len(tips) - 1}</div><div class="tbar"></div></div>
  <div class="gfoot">كتاب الألفَين · لغرض تعليمي</div></div>''')
        for i in range(0, len(tips), TIPS_PER_PAGE):
            chunk = tips[i:i+TIPS_PER_PAGE]
            body = "".join(tip_el(n + j + 1, t) for j, t in enumerate(chunk))
            slides.append(f'''<div class="slide" {CW}>{brandbar(True)}
  <div class="tipwrap"><div class="tiphead"><span class="th1 {part_cls}">{part_title}</span><span class="th2">{label}</span></div>
  <div class="tipcols">{body}</div></div>
  <div class="gfoot">كتاب الألفَين · لغرض تعليمي · @liquidity.state</div></div>''')
            n += len(chunk)
    return slides, n

def cover():
    return f'''<div class="slide dark" {CW}>
  <div class="dhd"><div class="hgem">{GEM}</div><div class="hwm"><span class="hln"></span>LIQUIDITY STATE<span class="hln" style="transform:scaleX(-1)"></span></div></div>
  <div class="dcover">
    <div class="deyeb"><span class="dsh"></span>المكتبة المكثفة — نسخة V2<span class="dsh"></span></div>
    <h1 class="dbig">كتاب الألفَين</h1>
    <div class="tbar"></div>
    <p class="dtag">1000 فكرة في <b>التحليل الفني</b><br>و1000 فكرة في <b>نفسية المتداول</b></p>
    <div class="dstats"><div><b>2000</b><span>فكرة مرقمة</span></div><div><b>8</b><span>أقسام</span></div><div><b>250</b><span>فكرة لكل قسم</span></div></div>
  </div>
  <div class="gfoot dk">ملف «الألفين» · <span dir="ltr">@liquidity.state</span></div>
</div>'''

def part_divider(num, title, rng, secs):
    lis = "".join(f'<div class="ci"><span class="ck">{i+1}</span><p>{lbl} <b>({PER_SECTION} فكرة)</b></p></div>'
                  for i, (_, lbl) in enumerate(secs))
    return f'''<div class="slide" {CW}>{brandbar(True)}
  <div class="cta">
    <p class="tag2 center">الجزء {num} — الأفكار {rng}</p>
    <h1 class="big2">{title}</h1>
    <div class="checkbox">{lis}</div>
  </div>
  <div class="botmeta">لغرض تعليمي</div></div>'''

def outro():
    return f'''<div class="slide" {CW}>{brandbar()}
  <div class="cta">
    <h1 class="big2">كيف تستعمل هذا الكتاب؟</h1>
    <div class="checkbox">
      <div class="ci"><span class="ck">✓</span><p>لا تقرأه دفعة واحدة — <b>عشر أفكار يومياً</b> تكفي لبناء عينٍ جديدة</p></div>
      <div class="ci"><span class="ck">✓</span><p>علّم على كل فكرة لمستك شخصياً… وارجع إليها بعد أسبوع من التطبيق</p></div>
      <div class="ci"><span class="ck">✓</span><p>اختر فكرة واحدة كل جلسة واجعلها <b>قاعدة اليوم</b> على الجارت</p></div>
    </div>
    <p class="tag2 center">تابع <span dir="ltr">@liquidity.state</span> — كل يوم درس جديد 📩</p>
  </div>
  <div class="botmeta">لغرض تعليمي</div></div>'''

BCSS = f'''
.tipwrap{{position:absolute;top:190px;bottom:120px;left:70px;right:70px;display:flex;flex-direction:column}}
.tiphead{{display:flex;align-items:center;gap:16px;margin-bottom:18px}}
.th1{{font-size:22px;font-weight:900;color:#fff;background:{TEAL_D};padding:6px 18px;border-radius:2px}}
.th1.psy{{background:{INK}}}
.th2{{font-size:23px;font-weight:800;color:{GREY}}}
.tipcols{{height:968px;column-count:2;column-gap:36px;column-fill:auto}}
.tip{{display:flex;gap:11px;align-items:flex-start;break-inside:avoid;margin-bottom:13px}}
.tip p{{font-size:21px;line-height:1.44;color:{INK};font-weight:600;text-align:right}}
.tn{{flex:none;min-width:46px;text-align:center;font-size:17px;font-weight:900;color:{TEAL_D};
  border:1.5px solid {CARDBD};background:#FBF9F5;padding:3px 6px;margin-top:2px;border-radius:2px}}
.secdiv{{position:absolute;top:0;bottom:0;left:0;right:0;display:flex;flex-direction:column;
  align-items:center;justify-content:center;gap:22px}}
.sd1{{font-size:26px;font-weight:800;color:{TEAL_D};letter-spacing:1px}}
.sd2{{font-size:72px;font-weight:900;color:{INK};text-align:center;line-height:1.2;padding:0 80px}}
.sd3{{font-size:28px;font-weight:700;color:{GREY}}}
.dstats{{display:flex;gap:26px;justify-content:center;margin-top:34px}}
.dstats div{{border:1px solid #173C47;background:rgba(67,212,220,0.05);padding:16px 30px;text-align:center}}
.dstats b{{display:block;font-size:44px;font-weight:900;color:#43D4DC}}
.dstats span{{font-size:20px;color:#B8C8CC;font-weight:600}}
.gfoot{{position:absolute;bottom:54px;left:0;right:0;text-align:center;color:{MUTE};font-size:21px;font-weight:600}}
.gfoot.dk{{color:#7F97A1}}
'''

if __name__ == "__main__":
    tech = load_clean(TECH_SECTIONS)
    psy = load_clean(PSY_SECTIONS)
    slides = [cover()]
    slides.append(part_divider("الأول", "التحليل الفني", "1 – 1000", TECH_SECTIONS))
    s_t, n_t = tips_pages(tech, "التحليل الفني", 0, 0, "tech")
    slides += s_t
    slides.append(part_divider("الثاني", "نفسية المتداول", "1 – 1000", PSY_SECTIONS))
    s_p, n_p = tips_pages(psy, "نفسية المتداول", 0, 0, "psy")
    slides += s_p
    slides.append(outro())
    assert n_t == 1000 and n_p == 1000, (n_t, n_p)
    html = f'''<!DOCTYPE html><html lang="ar" dir="rtl"><head><meta charset="UTF-8">
<title>كتاب الألفَين — Liquidity State</title>
<style>{FONT_CSS}\n{CSS}\n{BCSS}</style></head><body>
{''.join(slides)}
</body></html>'''
    out = os.path.join(HERE, "ideas_book.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)
    print("ideas_book.html:", len(slides), "صفحة |", n_t, "فنية +", n_p, "نفسية")
