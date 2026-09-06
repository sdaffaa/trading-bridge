# -*- coding: utf-8 -*-
"""غلاف ريل التعادل — إطار حقيقي من الريل نفسه + هوك الغلاف."""
import os, glob, base64
from playwright.sync_api import sync_playwright
from car_common import FONT_CSS, GEM

HERE = os.path.dirname(os.path.abspath(__file__))
CHROME = glob.glob("/opt/pw-browsers/chromium-*/chrome-linux/chrome")[0]
FRAME_T = 1.05   # لحظة اكتمال الضربة والانطلاق معاً في كادر واحد          # بعد ضرب الوقف مباشرة: الضربة والانطلاق في كادر واحد

def run():
    shot = os.path.join(HERE, "_cover_frame.png")
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROME, args=["--no-sandbox", "--force-color-profile=srgb"])
        pg = b.new_page(viewport={"width": 1080, "height": 1920}, device_scale_factor=1)
        pg.goto("file://" + os.path.join(HERE, "reel_be_fast.html")); pg.wait_for_timeout(400)
        pg.evaluate("(t)=>window.__setFrame(t)", FRAME_T)
        # إخفاء كل طبقات الريل النصية والضوئية: الغلاف يحمل نصه وحده
        pg.evaluate("""()=>{['chip','res','cta','edu','endlogo','sweep','flash','rflash','vig','run0','brand']
            .forEach(i=>{const e=document.getElementById(i); if(e) e.style.opacity='0';});
            document.querySelectorAll('[id^="t"]').forEach(e=>{
              if(/^t\d+$/.test(e.id)) e.style.opacity='0';});}""")
        pg.wait_for_timeout(120)
        pg.query_selector("#stage").screenshot(path=shot)
        b64 = base64.b64encode(open(shot, "rb").read()).decode()
        html = f'''<!DOCTYPE html><html lang="ar" dir="rtl"><head><meta charset="utf-8"><style>{FONT_CSS}
*{{margin:0;padding:0;box-sizing:border-box}}
#c{{position:relative;width:1080px;height:1920px;overflow:hidden;background:#04090F;font-family:Tajawal}}
#bg{{position:absolute;inset:0;background:url(data:image/png;base64,{b64}) center/cover;
  filter:saturate(.95) contrast(1.04)}}
/* حجاب خفيف أعلى الشاشة فقط ليقرأ الهوك — الجارت يبقى حاداً وواضحاً */
#sc{{position:absolute;inset:0;background:linear-gradient(180deg,rgba(4,9,15,.90) 0%,rgba(4,9,15,.74) 20%,
  rgba(4,9,15,.16) 38%,rgba(4,9,15,0) 58%,rgba(4,9,15,0) 84%,rgba(4,9,15,.55) 100%)}}
/* الشعار مصغَّر ~45% وليس أول ما تقع عليه العين */
#lg{{position:absolute;top:50px;left:0;right:0;display:flex;flex-direction:column;align-items:center;gap:6px;opacity:.80}}
#lg .g{{width:35px;height:35px}} #lg .g svg{{width:35px;height:auto}}
#lg .w{{font-size:15px;letter-spacing:6px;color:#7F97A1;font-weight:800}}
/* الهوك في الثلث العلوي، وبحجم أصغر 15% ليأخذ الجارت مساحة أكبر */
#hk{{position:absolute;top:168px;left:70px;right:70px;text-align:center}}
#hk h1{{font-size:88px;line-height:1.16;font-weight:900;color:#EDF4F5;letter-spacing:-2px;
  text-shadow:0 10px 40px rgba(0,0,0,.75)}}
#hk h1 b{{color:#43D4DC}}
#ft{{position:absolute;bottom:52px;left:0;right:0;text-align:center;font-size:21px;
  color:#7F97A1;font-weight:600;letter-spacing:1px;opacity:.7}}
</style></head><body><div id="c">
<div id="bg"></div><div id="sc"></div>
<div id="lg"><div class="g">{GEM}</div><div class="w">LIQUIDITY STATE</div></div>
<div id="hk"><h1>تأمينك للصفقة<br><b>أخرجك</b> بدري.</h1></div>
<div id="ft">لغرض تعليمي</div>
</div></body></html>'''
        hp = os.path.join(HERE, "cover_be.html")
        open(hp, "w", encoding="utf-8").write(html)
        pg2 = b.new_page(viewport={"width": 1080, "height": 1920}, device_scale_factor=1)
        pg2.goto("file://" + hp); pg2.wait_for_timeout(500)
        pg2.query_selector("#c").screenshot(path=os.path.join(HERE, "cover_be.png"))
        b.close()
    os.remove(shot)
    print("cover_be.png OK")

if __name__ == "__main__":
    run()
