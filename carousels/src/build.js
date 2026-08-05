const fs = require('fs');
const path = require('path');
const {chromium} = require('playwright');
const carousels = require('./content');
const {CH} = require('./charts');

const ROOT = path.join(__dirname, '..');
const OUT = path.join(ROOT, 'out');
const FONTS = path.join(ROOT, '..', 'reel-vp-lvn', 'public', 'fonts');
const b64 = (f) => fs.readFileSync(path.join(FONTS, f)).toString('base64');
const FONT_CSS = `
@font-face{font-family:'Tajawal';font-weight:700;src:url(data:font/woff;base64,${b64('Tajawal-Bold.woff')}) format('woff');font-display:block}
@font-face{font-family:'Tajawal';font-weight:500;src:url(data:font/woff;base64,${b64('Tajawal-Medium.woff')}) format('woff');font-display:block}
@font-face{font-family:'Tajawal';font-weight:400;src:url(data:font/woff;base64,${b64('Tajawal-Regular.woff')}) format('woff');font-display:block}`;

const GEM = `<svg class="gem" viewBox="0 0 100 100"><polygon points="50,6 82,32 68,50 32,50 18,32" fill="currentColor" opacity=".92"/><polygon points="32,50 68,50 50,94" fill="currentColor" opacity=".72"/><polygon points="18,32 32,50 50,94" fill="currentColor" opacity=".55"/><polygon points="82,32 68,50 50,94" fill="currentColor" opacity=".45"/></svg>`;

const CSS = `
${FONT_CSS}
*{margin:0;padding:0;box-sizing:border-box}
body{background:#888}
.slide{width:1080px;height:1350px;position:relative;overflow:hidden;font-family:'Tajawal',sans-serif;direction:rtl}
.gem{width:100%;height:100%}

/* ---------- COVER (dark) ---------- */
.slide.dark{background:linear-gradient(157deg,#0B1A20 0%,#0E1E24 46%,#12262E 100%);color:#F2F5F7;
  display:flex;flex-direction:column;justify-content:center;padding:96px 92px 132px}
.hud{position:absolute;inset:0;opacity:.5}
.hud i{position:absolute;background:#8FD6E0;opacity:.055}
.glow{position:absolute;width:820px;height:820px;border-radius:50%;left:-260px;bottom:-320px;
  background:radial-gradient(circle,rgba(46,204,154,.20) 0%,rgba(23,128,143,.10) 42%,transparent 68%)}
.arcs{position:absolute;right:-180px;top:-160px;width:700px;height:700px;border-radius:50%;
  border:1px solid rgba(159,180,188,.15)}
.arcs::after{content:'';position:absolute;inset:78px;border-radius:50%;border:1px solid rgba(46,204,154,.12)}
.cover-kicker{position:relative;font-size:26px;font-weight:500;letter-spacing:5px;color:#7FA6B0;margin-bottom:34px}
.cover-kicker span{display:inline-block;width:54px;height:2px;background:#2ECC9A;vertical-align:middle;margin-left:16px;opacity:.8}
.hook{position:relative;font-size:88px;font-weight:700;line-height:1.32;letter-spacing:-1px}
.hook .hl{color:#48E3B0;text-shadow:0 0 44px rgba(46,204,154,.35)}
.cover-sub{position:relative;margin-top:40px;font-size:31px;font-weight:500;color:#9FB4BC;line-height:1.7;
  padding-right:24px;border-right:3px solid rgba(46,204,154,.55)}
.cover-foot{position:absolute;left:92px;right:92px;bottom:74px;display:flex;align-items:center;justify-content:space-between}
.brandline{display:flex;align-items:center;gap:14px;color:#C9D5DA}
.brandline .gemwrap{width:30px;height:30px;color:#D7DEE3}
.brandline b{font-size:25px;font-weight:500;letter-spacing:.3px}
.swipe{display:flex;align-items:center;gap:12px;font-size:26px;font-weight:700;color:#48E3B0}

/* ---------- LIGHT SLIDES ---------- */
.slide.light{background:#F4F6F5;color:#0E1E24;padding:84px 90px 118px;display:flex;flex-direction:column}
.slide.light::before{content:'';position:absolute;inset:0;
  background:radial-gradient(1100px 520px at 88% -8%,rgba(46,204,154,.09),transparent 62%)}
.top{position:relative;display:flex;align-items:center;justify-content:space-between;margin-bottom:44px}
.kicker{font-size:24px;font-weight:700;color:#1E9E78;letter-spacing:2.5px}
.count{font-size:23px;font-weight:700;color:#7A8F97;font-feature-settings:"tnum"}
.numbadge{position:relative;width:74px;height:74px;border-radius:22px;background:#0E1E24;color:#fff;
  display:flex;align-items:center;justify-content:center;font-size:38px;font-weight:700;margin-bottom:26px;
  box-shadow:0 12px 30px rgba(14,30,36,.18)}
.h1{position:relative;font-size:64px;font-weight:700;line-height:1.28;letter-spacing:-.5px;margin-bottom:24px}
.p{position:relative;font-size:33px;font-weight:500;line-height:1.78;color:#3B5058;max-width:900px}
.p b{color:#0E1E24;font-weight:700}
.card{position:relative;margin-top:36px;flex:1;min-height:0;display:flex;align-items:stretch;
  background:#fff;border:1px solid rgba(14,30,36,.09);
  border-radius:28px;padding:18px;box-shadow:0 22px 50px rgba(14,30,36,.09)}
.card > svg{width:100%;height:100%;display:block}
.dual{display:flex;gap:14px;width:100%;height:100%}
.dual svg{flex:1;min-width:0;height:100%;border-radius:14px;background:#FBFCFC}
.foot{position:absolute;left:90px;right:90px;bottom:52px;display:flex;align-items:center;justify-content:space-between}
.dots{display:flex;gap:9px}
.dots i{width:9px;height:9px;border-radius:50%;background:rgba(14,30,36,.16)}
.dots i.on{background:#1E9E78;width:26px;border-radius:5px}
.handle{display:flex;align-items:center;gap:11px;color:#7A8F97;font-size:23px;font-weight:500}
.handle .gemwrap{width:24px;height:24px;color:#9FB4BC}

/* quote slide */
.slide.quote{justify-content:center;text-align:center;align-items:center}
.slide.quote .top,.slide.cta .top{width:100%}
.slide.quote .mark{font-size:120px;font-weight:700;color:#2ECC9A;opacity:.30;line-height:.7;margin-bottom:30px}
.slide.quote .q{position:relative;font-size:82px;font-weight:700;line-height:1.4;letter-spacing:-1px;max-width:880px}
.slide.quote .rule{position:relative;width:110px;height:4px;background:#1E9E78;border-radius:2px;margin:44px 0 34px;opacity:.85}
.slide.quote .note{position:relative;font-size:31px;font-weight:500;color:#5C7078;max-width:760px;line-height:1.7}

/* cta slide */
.slide.cta{justify-content:center;align-items:center;text-align:center}
.slide.cta .h1{font-size:70px;margin-bottom:30px}
.slide.cta .p{font-size:36px;text-align:center}
.kw{color:#0E1E24;background:rgba(46,204,154,.24);padding:2px 14px;border-radius:10px;font-weight:700}
.savepill{margin-top:52px;display:inline-flex;align-items:center;gap:14px;background:#0E1E24;color:#fff;
  padding:24px 46px;border-radius:20px;font-size:33px;font-weight:700;box-shadow:0 18px 40px rgba(14,30,36,.22)}
.edu{position:absolute;bottom:120px;left:0;right:0;text-align:center;font-size:22px;color:#8FA2A9;font-weight:500}
`;

const dots = (i, total) => `<div class="dots">${Array.from({length: total}, (_, k) => `<i class="${k === i ? 'on' : ''}"></i>`).join('')}</div>`;
const handle = `<div class="handle"><span class="gemwrap">${GEM}</span><span dir="ltr">@liquidity.state</span></div>`;
const AR = ['٠','١','٢','٣','٤','٥','٦','٧','٨','٩'];
const arNum = (n) => String(n).split('').map(d => AR[+d]).join('');

function coverHTML(c, total) {
  const hud = Array.from({length: 9}, (_, i) => `<i style="left:${(i + 1) * 10}%;top:0;width:1px;height:100%"></i>`).join('')
    + Array.from({length: 13}, (_, i) => `<i style="top:${(i + 1) * 7.2}%;left:0;height:1px;width:100%"></i>`).join('');
  return `<section class="slide dark">
    <div class="hud">${hud}</div><div class="glow"></div><div class="arcs"></div>
    <div class="cover-kicker">${c.kicker}<span></span></div>
    <h1 class="hook">${c.cover.hook}</h1>
    <p class="cover-sub">${c.cover.sub}</p>
    <div class="cover-foot">
      <div class="brandline"><span class="gemwrap">${GEM}</span><b dir="ltr">@liquidity.state</b></div>
      <div class="swipe">اسحب <span>←</span></div>
    </div>
  </section>`;
}

function slideHTML(s, idx, total, kicker) {
  const counter = `<div class="count">${arNum(idx + 1)} / ${arNum(total)}</div>`;
  const top = `<div class="top"><div class="kicker">${kicker}</div>${counter}</div>`;
  const foot = `<div class="foot">${dots(idx, total)}${handle}</div>`;

  if (s.type === 'quote') {
    return `<section class="slide light quote">${top}
      <div class="mark">”</div>
      <h2 class="q">${s.quote}</h2><div class="rule"></div><p class="note">${s.note}</p>${foot}</section>`;
  }
  if (s.type === 'cta') {
    return `<section class="slide light cta">${top}
      <h2 class="h1">${s.title}</h2><p class="p">${s.body}</p>
      ${s.pill ? `<div class="savepill">${s.pill}</div>` : ''}
      <div class="edu">المحتوى لغرض تعليمي — مو توصية</div>${foot}</section>`;
  }
  const chart = s.chart && CH[s.chart] ? `<div class="card">${CH[s.chart]()}</div>` : '';
  const badge = s.n ? `<div class="numbadge">${s.n}</div>` : '';
  return `<section class="slide light">${top}${badge}
    <h2 class="h1">${s.title}</h2><p class="p">${s.body}</p>${chart}${foot}</section>`;
}

function buildHTML(c) {
  const total = c.slides.length + 1;
  const body = [coverHTML(c, total), ...c.slides.map((s, i) => slideHTML(s, i + 1, total, c.kicker))].join('\n');
  return `<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8"><style>${CSS}
    @page{size:1080px 1350px;margin:0}
    @media print{.slide{break-after:page;page-break-after:always}}
  </style></head><body>${body}</body></html>`;
}

(async () => {
  fs.mkdirSync(OUT, {recursive: true});
  const browser = await chromium.launch({executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'});
  const page = await browser.newPage({viewport: {width: 1080, height: 1350}, deviceScaleFactor: 1});

  for (const c of carousels) {
    const html = buildHTML(c);
    const htmlPath = path.join(OUT, `${c.id}.html`);
    fs.writeFileSync(htmlPath, html);
    await page.goto('file://' + htmlPath, {waitUntil: 'load'});
    await page.evaluate(() => document.fonts.ready);
    await page.waitForTimeout(250);

    const dir = path.join(OUT, c.id);
    fs.mkdirSync(dir, {recursive: true});
    const els = await page.$$('.slide');
    const names = ['01-cover', ...c.slides.map((s, i) => {
      const kind = s.type === 'quote' ? 'quote' : s.type === 'cta' ? 'cta' : s.type === 'stakes' ? 'stakes' : 'value';
      return String(i + 2).padStart(2, '0') + '-' + kind;
    })];
    for (let i = 0; i < els.length; i++) {
      await els[i].screenshot({path: path.join(dir, `${names[i]}.png`)});
    }
    await page.pdf({path: path.join(OUT, `${c.id}.pdf`), width: '1080px', height: '1350px',
      printBackground: true, pageRanges: `1-${els.length}`});
    console.log(`✓ ${c.id}: ${els.length} slides + pdf`);
  }
  await browser.close();
})();
