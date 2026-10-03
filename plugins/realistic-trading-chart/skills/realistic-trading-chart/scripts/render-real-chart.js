#!/usr/bin/env node
'use strict';
/* render-real-chart.js — fetch REAL market OHLC, auto-detect the liquidity sweep,
 * and render a brand-styled TradingView-look chart card to PNG.
 *
 *   node render-real-chart.js --symbol XAUUSD --interval 15m --window 70 \
 *        --out xau-example.png [--title "XAU/USD"] [--scale 2]
 *
 * Falls back across data providers (Yahoo → Binance → Stooq). Requires open
 * network egress to those hosts; in a locked sandbox it errors clearly.
 * Requires: playwright-core + Chromium (see render-chart.js for path resolution).
 */
const fs = require('fs');
const path = require('path');
const { chartSVG } = require('./chart-engine');
const { fetchOHLC } = require('./fetch-ohlc');

const arg = (n, d) => { const i = process.argv.indexOf('--' + n); if (i < 0) return d; const v = process.argv[i+1]; return (v===undefined||String(v).startsWith('--')) ? true : v; };

function fontFace(w, file){ const p=path.join(__dirname,'..','fonts',file); if(!fs.existsSync(p)) return ''; const b64=fs.readFileSync(p).toString('base64'); return `@font-face{font-family:'Tajawal';font-weight:${w};font-display:block;src:url(data:font/woff2;base64,${b64}) format('woff2');}`; }
function findChromium(){ const ok=p=>p&&fs.existsSync(p)?p:null; if(ok(process.env.CHROMIUM_PATH))return process.env.CHROMIUM_PATH; try{for(const d of fs.readdirSync('/opt/pw-browsers')){if(/^chromium-\d+$/.test(d)){for(const r of ['chrome-linux/chrome','chrome-linux64/chrome']){const c=ok(path.join('/opt/pw-browsers',d,r));if(c)return c;}}}}catch(_){}try{const p=require('playwright-core').chromium.executablePath();if(ok(p))return p;}catch(_){}return undefined; }

(async () => {
  const symbol = arg('symbol','XAUUSD');
  const interval = arg('interval','15m');
  const window = +arg('window',70);
  const width = +arg('width',1040), height = +arg('height',520), scale = +arg('scale',2);
  const out = arg('out','real-chart.png');
  const title = arg('title', symbol.replace(/USD$/,'/USD'));
  const bg = arg('bg','#12262E');

  console.error(`fetching ${symbol} ${interval} …`);
  const data = await fetchOHLC({ symbol, interval, limit: Math.max(window, 90) });
  const candles = data.candles.slice(-window);
  console.error(`source=${data.source} using ${candles.length} candles`);

  const { svg, meta } = chartSVG({ width, height, candles, annotate:true, bg:'transparent' });
  const chg = ((candles.at(-1).close - candles[0].open) / candles[0].open * 100);
  const chgStr = (chg>=0?'▲ ':'▼ ') + Math.abs(chg).toFixed(2) + '%';
  const chgCol = chg>=0 ? '#2ECC9A' : '#E15A5A';

  const css = ['400','700','800','900'].map(w=>fontFace(w,`tajawal-arabic-${w}-normal.woff2`)).join('\n');
  const cardW = width + 44, cardH = height + 78;
  const html = `<!doctype html><html dir="rtl" lang="ar"><head><meta charset="utf-8"><style>${css}
   *{margin:0;padding:0;box-sizing:border-box}html,body{background:#0E1E24}
   .card{width:${cardW}px;background:linear-gradient(180deg,#12272F,#0E2027);border:1px solid #2ECC9A22;border-radius:24px;padding:20px 22px 16px;font-family:'Tajawal',sans-serif}
   .bar{display:flex;align-items:center;gap:14px;margin-bottom:10px;padding:0 4px}
   .tk{font-weight:800;font-size:27px;color:#fff;letter-spacing:.5px}
   .tf{font-weight:700;font-size:19px;color:#9FB4BC;background:#1B3A45;border-radius:8px;padding:4px 12px}
   .chg{font-weight:800;font-size:22px;color:${chgCol}}
   .edu{margin-inline-start:auto;font-weight:600;font-size:20px;color:#6f8891}
   .box{width:${width}px;height:${height}px}
  </style></head><body><div class="card">
    <div class="bar"><span class="tk">${title}</span><span class="tf">${String(interval).toUpperCase()}</span><span class="chg">${chgStr}</span><span class="edu">لغرض تعليمي · داتا حقيقية</span></div>
    <div class="box">${svg}</div>
  </div></body></html>`;

  const { chromium } = require('playwright-core');
  const browser = await chromium.launch({ executablePath: findChromium(), args: ['--no-sandbox','--force-color-profile=srgb'] });
  const page = await browser.newPage({ viewport:{ width:cardW+40, height:cardH+40 }, deviceScaleFactor: scale });
  await page.setContent(html, { waitUntil:'load' });
  await page.evaluate(()=>document.fonts.ready); await page.waitForTimeout(250);
  await page.locator('.card').screenshot({ path: out });
  await browser.close();
  console.error(`rendered ${out} — sweep@${meta.sweepIndex}, pool ${meta.pool.toFixed(2)}, last ${meta.last.toFixed(2)}`);
})().catch(e => { console.error('ERROR:', e.message); process.exit(1); });
