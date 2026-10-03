'use strict';
/* carousel-kit.js — Liquidity State carousel design system.
 * Cairo (display) + Tajawal (body) typography, brand theme, glass cards,
 * 3D-background layering, and ready slide components. Compose a carousel as
 * data, get self-contained HTML per slide, render to 1080×1350 PNG.
 *
 *   const K = require('./carousel-kit');
 *   const html = K.slide({ num:'١', total:'٥', bg:'/abs/path/bg-02-vortex.png',
 *     kt:'سيكولوجيا', ke:'PSYCHOLOGY',
 *     main: K.H('تبيع <span style="color:'+K.RED+'">بخوف</span>.',96) + K.P('...') });
 *   await K.renderSlides([html], 'out', { scale:2 });   // needs playwright-core + chromium
 *
 * 3D backgrounds: use the PNGs shipped in the `liquidity-3d-backgrounds` skill
 * (assets/bg-01…bg-10). Pass an absolute path (or a path relative to the HTML)
 * as `bg`.
 */
const fs = require('fs');
const path = require('path');

// ---- fonts (base64-inlined @font-face) ----
function fontCss(){
  const dir = path.join(__dirname, '..', 'fonts');
  const face = (fam,w,file)=>{ const p=path.join(dir,file); if(!fs.existsSync(p)) return '';
    return `@font-face{font-family:'${fam}';font-style:normal;font-weight:${w};font-display:block;src:url(data:font/woff2;base64,${fs.readFileSync(p).toString('base64')}) format('woff2');}`; };
  return [
    face('Tajawal',400,'tajawal-arabic-400-normal.woff2'),
    face('Tajawal',700,'tajawal-arabic-700-normal.woff2'),
    face('Tajawal',800,'tajawal-arabic-800-normal.woff2'),
    face('Cairo',400,'cairo-arabic-400-normal.woff2'),
    face('Cairo',700,'cairo-arabic-700-normal.woff2'),
    face('Cairo',900,'cairo-arabic-900-normal.woff2'),
  ].join('\n');
}

// brand palette
const GREEN='#2ECC9A', MINT='#7BEBC8', RED='#E15A5A', AMBER='#E8B24A', GREY='#8496a0';

const GRAIN = "url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='260' height='260'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.8' numOctaves='2' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E\")";

const gem = `<svg viewBox="0 0 100 100" width="100%" height="100%" xmlns="http://www.w3.org/2000/svg"><g stroke="#0E1E24" stroke-width="1.4" stroke-linejoin="round"><polygon points="50,6 82,30 50,44" fill="#DCE8EB"/><polygon points="50,6 18,30 50,44" fill="#B9CBD1"/><polygon points="82,30 92,66 50,44" fill="#C9D9DD"/><polygon points="18,30 8,66 50,44" fill="#A7BCC3"/><polygon points="92,66 50,94 50,44" fill="#9FB4BC"/><polygon points="8,66 50,94 50,44" fill="#8CA3AB"/></g></svg>`;

const BASE = `
${fontCss()}
*{margin:0;padding:0;box-sizing:border-box}
:root{--green:${GREEN};--mint:${MINT};--red:${RED};--amber:${AMBER};--sub:#9FB4BC;--card:#173039;--line:#2ECC9A2b;--acc:${GREEN}}
html,body{margin:0;padding:0;background:#0A171C}
.slide{position:relative;width:1080px;height:1350px;overflow:hidden;color:#fff;font-family:'Tajawal',sans-serif;background:#0A171C}
.bg3d{position:absolute;inset:0;z-index:0;background-position:center;background-size:cover;background-repeat:no-repeat}
.s-scrim{position:absolute;inset:0;z-index:1;pointer-events:none;background:linear-gradient(270deg, rgba(8,18,22,.72) 0%, rgba(8,18,22,.36) 44%, rgba(8,18,22,0) 74%), radial-gradient(60% 48% at 50% 44%, rgba(8,18,22,.28), transparent 66%)}
.bg-grain{position:absolute;inset:0;z-index:2;opacity:.13;mix-blend-mode:overlay;background-image:${GRAIN};background-size:260px 260px}
.bg-vign{position:absolute;inset:0;z-index:2;background:radial-gradient(130% 100% at 50% 36%, transparent 50%, rgba(0,0,0,.55) 100%)}
.wrap{position:absolute;inset:0;padding:88px 84px 92px;display:flex;flex-direction:column;z-index:3}
.head{display:flex;align-items:center;justify-content:space-between}
.brand{display:flex;align-items:center;gap:14px}.brand .g{width:44px;height:44px;filter:drop-shadow(0 4px 14px rgba(0,0,0,.5))}
.brand span{font-family:'Cairo';font-weight:700;font-size:25px;color:#CFE0E4}
.count{font-family:'Cairo';border:1.5px solid rgba(255,255,255,.16);color:#C6D4D8;font-weight:700;font-size:22px;padding:6px 18px;border-radius:999px;background:rgba(255,255,255,.05)}
.main{flex:1;display:flex;flex-direction:column;justify-content:center;padding:8px 0}
.kick{display:inline-flex;align-items:center;gap:16px;align-self:flex-start;padding:10px 20px;border-radius:999px;background:color-mix(in srgb, var(--acc) 12%, transparent);border:1px solid color-mix(in srgb, var(--acc) 34%, transparent)}
.kick .dot{width:10px;height:10px;border-radius:50%;background:var(--acc);box-shadow:0 0 16px 4px color-mix(in srgb, var(--acc) 75%, transparent)}
.kick .t{font-family:'Cairo';color:var(--acc);font-weight:700;font-size:25px}
.kick .en{font-family:'Cairo';color:#8397a0;font-weight:700;font-size:19px;letter-spacing:5px}
h1{font-family:'Cairo';font-weight:900;line-height:1.22;letter-spacing:-.5px;text-shadow:0 8px 44px rgba(0,0,0,.5)}
h1 span{text-shadow:0 0 40px color-mix(in srgb, currentColor 45%, transparent)}
.body{color:#C6D4D9;font-weight:500;line-height:1.65;font-family:'Tajawal'}.body b{color:#fff;font-weight:700}
.foot{display:flex;align-items:center;justify-content:space-between;margin-top:auto;padding-top:26px}
.foot .edu{color:#8196a0;font-weight:600;font-size:21px}
.swipe{display:flex;align-items:center;gap:12px;color:#fff;font-weight:800;font-size:27px;font-family:'Cairo'}.swipe .arw{color:var(--acc);font-size:30px}
.card{background:linear-gradient(180deg, rgba(255,255,255,.06), rgba(255,255,255,.022));backdrop-filter:blur(16px) saturate(1.2);border:1px solid rgba(46,204,154,.24);border-radius:24px;box-shadow:0 24px 60px rgba(0,0,0,.5), inset 0 1px 0 rgba(255,255,255,.10)}
`;

const bgLayers = file => `<div class="bg3d" style="background-image:url('${file}')"></div><div class="s-scrim"></div><div class="bg-grain"></div><div class="bg-vign"></div>`;

// ---- components (return inner HTML) ----
const AR=['١','٢','٣','٤','٥','٦','٧','٨'];
const H=(h,s=82)=>`<h1 style="font-size:${s}px;margin-top:28px">${h}</h1>`;
const P=(h,s=34)=>`<p class="body" style="font-size:${s}px;margin-top:34px;max-width:900px">${h}</p>`;
const CARD=(h,st='')=>`<div class="card" style="padding:38px 42px;margin-top:38px;${st}">${h}</div>`;
const STAT=(n,l)=>CARD(`<div style="display:flex;align-items:center;gap:40px"><div dir="ltr" style="font-family:Cairo;font-weight:900;font-size:118px;color:var(--green);line-height:1;letter-spacing:-3px">${n}</div><div style="font-weight:600;font-size:33px;color:#C6D4D9;line-height:1.5">${l}</div></div>`);
const STEP=(n,t)=>`<div style="display:flex;align-items:center;gap:24px;margin-top:20px"><div style="min-width:70px;height:70px;border-radius:16px;background:#13303A;border:1px solid var(--line);display:flex;align-items:center;justify-content:center;font-family:Cairo;font-weight:900;font-size:36px;color:var(--green)">${n}</div><div style="font-weight:600;font-size:33px;color:#DCE7EA;line-height:1.4">${t}</div></div>`;
const STEPS=(a,st=0)=>`<div style="margin-top:34px">${a.map((t,i)=>STEP(AR[i+st],t)).join('')}</div>`;
const TWO=(a,b)=>`<div style="display:flex;gap:24px;margin-top:40px">${[a,b].map(c=>`<div class="card" style="flex:1;padding:34px 30px"><div style="font-weight:800;font-size:29px;color:${c.c}">${c.h}</div><div style="font-weight:500;font-size:30px;color:#C4D3D8;margin-top:14px;line-height:1.5">${c.b}</div></div>`).join('')}</div>`;
const QUOTE=(h)=>`<div style="margin-top:26px"><div style="font-family:Georgia,serif;font-size:190px;color:var(--green);opacity:.22;line-height:.6;height:100px">”</div><div style="font-family:Cairo;font-weight:900;font-size:72px;line-height:1.3;letter-spacing:-1px">${h}</div></div>`;
const CTA=(title,kw)=>`<div class="card" style="padding:36px 42px;margin-top:40px"><div style="display:flex;align-items:center;gap:16px"><span style="font-size:38px">📌</span><span style="font-family:Cairo;font-weight:800;font-size:36px;color:#fff">${title}</span></div><div style="font-weight:600;font-size:31px;color:#C4D3D8;margin-top:16px;line-height:1.5">وعلّق كلمة <b style="color:var(--green);font-weight:800">«${kw}»</b> أرسلك الدليل PDF 📊</div></div>`;

// optional chart component (uses the sibling realistic-trading-chart skill if present)
function CHART(markers){
  let chartSVG;
  try { chartSVG = require(path.join(__dirname,'..','..','realistic-trading-chart','scripts','chart-engine')).chartSVG; }
  catch(_) { return '<div style="margin-top:22px;height:400px;border:1px dashed #2E4A54;border-radius:24px;display:flex;align-items:center;justify-content:center;color:#6f8891">[chart: install realistic-trading-chart skill]</div>'; }
  const { svg } = chartSVG({ width:1040, height:470, seed:42, annotate:!markers, markers });
  return `<div style="margin-top:22px;background:linear-gradient(180deg,#12272F,#0E2027);border:1px solid var(--line);border-radius:24px;padding:18px 20px 14px"><div style="display:flex;align-items:center;gap:12px;margin-bottom:8px;padding:0 4px"><span style="font-family:Cairo;font-weight:800;font-size:25px;color:#fff">XAU/USD</span><span style="font-weight:700;font-size:18px;color:#9FB4BC;background:#1B3A45;border-radius:8px;padding:3px 11px">M15</span><span style="margin-inline-start:auto;font-weight:600;font-size:19px;color:#6f8891">لغرض تعليمي</span></div><div style="height:400px">${svg}</div></div>`;
}

// ---- slide wrapper ----
function slide(o){
  const acc = o.acc ? ` style="--acc:${o.acc}"` : '';
  return `<!doctype html><html dir="rtl" lang="ar"><head><meta charset="utf-8"><style>${BASE}${o.css||''}</style></head>
  <body><div class="slide"${acc}>${o.bg?bgLayers(o.bg):''}<div class="wrap">
    <div class="head"><div class="brand"><div class="g">${gem}</div><span>liquidity.state@</span></div><div class="count">${o.num} / ${o.total}</div></div>
    <div class="main"><div class="kick"><span class="dot"></span><span class="t">${o.kt}</span><span class="en">${o.ke}</span></div>${o.main}</div>
    <div class="foot"><span class="edu">${o.foot||'اسحب ←'}</span><div class="swipe">${o.last?'شارك 🔁':'اسحب <span class="arw">←</span>'}</div></div>
  </div></div></body></html>`;
}

// ---- render helper (needs playwright-core + Chromium) ----
function findChromium(){const ok=p=>p&&fs.existsSync(p)?p:null;if(ok(process.env.CHROMIUM_PATH))return process.env.CHROMIUM_PATH;
  try{for(const d of fs.readdirSync('/opt/pw-browsers')){if(/^chromium-\d+$/.test(d)){for(const r of ['chrome-linux/chrome','chrome-linux64/chrome']){const c=ok(path.join('/opt/pw-browsers',d,r));if(c)return c;}}}}catch(_){}
  try{const p=require('playwright-core').chromium.executablePath();if(ok(p))return p;}catch(_){}return undefined;}

async function renderSlides(htmlArray, outdir='out', { scale=2 } = {}){
  fs.mkdirSync(outdir,{recursive:true});
  const { chromium } = require('playwright-core');
  const b = await chromium.launch({ executablePath:findChromium(), args:['--no-sandbox','--force-color-profile=srgb'] });
  const out=[];
  for(let i=0;i<htmlArray.length;i++){
    const p = await b.newPage({ viewport:{width:1080,height:1350}, deviceScaleFactor:scale });
    await p.setContent(htmlArray[i],{waitUntil:'load'});
    await p.evaluate(()=>document.fonts.ready); await p.waitForTimeout(250);
    const f = path.join(outdir, String(i+1).padStart(2,'0')+'.png');
    await p.locator('.slide').screenshot({ path:f }); await p.close(); out.push(f);
  }
  await b.close(); return out;
}

module.exports = { BASE, bgLayers, gem, slide, renderSlides, fontCss,
  H, P, CARD, STAT, STEP, STEPS, TWO, QUOTE, CTA, CHART,
  GREEN, MINT, RED, AMBER, GREY };
