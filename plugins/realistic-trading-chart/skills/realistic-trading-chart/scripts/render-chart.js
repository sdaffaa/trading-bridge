#!/usr/bin/env node
/* render-chart.js — render a realistic TradingView-style candlestick chart to PNG.
 *
 * Usage:
 *   node render-chart.js --out chart.png [--seed 7] [--width 1040] [--height 520]
 *                        [--annotate] [--scale 2] [--base 2348] [--n 64]
 *                        [--bg "#12262E"] [--ticker "XAU/USD"] [--tf M15]
 *
 * Produces a standalone chart PNG. To embed inside a carousel slide, import
 * chart-engine.js directly (see SKILL.md) and drop the returned SVG into your
 * slide HTML instead of rendering here.
 *
 * Requires: playwright-core (npm i playwright-core) and a Chromium build.
 * Chromium path resolution order: $CHROMIUM_PATH, playwright's default,
 * then common /opt/pw-browsers location.
 */
'use strict';
const fs = require('fs');
const path = require('path');
const { chartSVG } = require('./chart-engine');

function arg(name, def) {
  const i = process.argv.indexOf('--' + name);
  if (i === -1) return def;
  const v = process.argv[i + 1];
  return (v === undefined || v.startsWith('--')) ? true : v;
}

function fontFace(weight, file) {
  const p = path.join(__dirname, '..', 'fonts', file);
  if (!fs.existsSync(p)) return '';
  const b64 = fs.readFileSync(p).toString('base64');
  return `@font-face{font-family:'Tajawal';font-weight:${weight};font-display:block;` +
         `src:url(data:font/woff2;base64,${b64}) format('woff2');}`;
}

function findChromium() {
  const ok = p => p && fs.existsSync(p) ? p : null;
  if (ok(process.env.CHROMIUM_PATH)) return process.env.CHROMIUM_PATH;
  // scan common Playwright browser dirs for an existing chrome binary
  const glob = '/opt/pw-browsers';
  try {
    for (const d of fs.readdirSync(glob)) {
      if (/^chromium-\d+$/.test(d)) {
        for (const rel of ['chrome-linux/chrome', 'chrome-linux64/chrome']) {
          const c = ok(path.join(glob, d, rel));
          if (c) return c;
        }
      }
    }
  } catch (_) {}
  // fall back to playwright's default only if it actually exists
  try {
    const p = require('playwright-core').chromium.executablePath();
    if (ok(p)) return p;
  } catch (_) {}
  return undefined;
}

(async () => {
  const width = +arg('width', 1040);
  const height = +arg('height', 520);
  const scale = +arg('scale', 2);
  const out = arg('out', 'chart.png');
  const bg = arg('bg', '#12262E');

  const { svg, meta } = chartSVG({
    width, height,
    seed: +arg('seed', 7),
    base: +arg('base', 2348),
    n: +arg('n', 64),
    annotate: arg('annotate', false) === true || arg('annotate', false) === 'true',
    bg: 'transparent',
  });

  const css = [
    fontFace(400, 'tajawal-arabic-400-normal.woff2'),
    fontFace(700, 'tajawal-arabic-700-normal.woff2'),
    fontFace(800, 'tajawal-arabic-800-normal.woff2'),
    fontFace(900, 'tajawal-arabic-900-normal.woff2'),
  ].join('\n');

  const html = `<!doctype html><html dir="rtl" lang="ar"><head><meta charset="utf-8"><style>${css}
    *{margin:0;padding:0}html,body{background:${bg}}
    .box{width:${width}px;height:${height}px;background:${bg};font-family:'Tajawal',sans-serif}
  </style></head><body><div class="box">${svg}</div></body></html>`;

  const { chromium } = require('playwright-core');
  const executablePath = findChromium();
  const browser = await chromium.launch({ executablePath, args: ['--no-sandbox', '--force-color-profile=srgb'] });
  const page = await browser.newPage({ viewport: { width, height }, deviceScaleFactor: scale });
  await page.setContent(html, { waitUntil: 'load' });
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(250);
  await page.locator('.box').screenshot({ path: out });
  await browser.close();
  console.log(`rendered ${out} (${width * scale}x${height * scale}) — last ${meta.last}, pool ${meta.pool.toFixed(2)}`);
})().catch(e => { console.error(e); process.exit(1); });
