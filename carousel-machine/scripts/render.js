/* ============================================================================
 * render.js — one source page -> one PNG per slide, at exactly 1080x1350.
 *
 * Source: src/carousel.html, a single page holding every <section class="slide">
 * (shared gem symbol, shared chrome — the logo can't drift between slides).
 * Each slide is screenshotted at deviceScaleFactor 2 then downscaled to
 * 1080x1350 for a sharper result. Fonts are base64-embedded in fonts.css so
 * the headless browser never waits on a network font.
 *
 * Usage:
 *   node scripts/render.js               # every slide in src/carousel.html
 *   node scripts/render.js 5             # only slide 5
 *   node scripts/render.js 2 5 7         # a subset
 *   node scripts/render.js --page other.html
 * ==========================================================================*/
'use strict';

const path = require('path');
const fs = require('fs');

const { chromium } = requirePlaywright();
function requirePlaywright() {
  try {
    return require('playwright');
  } catch (_) {
    const { createRequire } = require('module');
    for (const base of ['/opt/node22/lib/node_modules/', process.env.NODE_PATH || '']) {
      try {
        return createRequire(base + 'x.js')('playwright');
      } catch (_) {}
    }
    throw new Error('playwright not found — see carousel-machine/README.md (المتطلبات).');
  }
}

const ROOT = path.resolve(__dirname, '..');
const OUT = path.join(ROOT, 'out');

const CANVAS_W = 1080;
const CANVAS_H = 1350;
const SCALE = 2;

function parseArgs(argv) {
  const only = [];
  let page = path.join(ROOT, 'src', 'carousel.html');
  for (let i = 0; i < argv.length; i++) {
    if (argv[i] === '--page') page = path.resolve(argv[++i]);
    else if (/^\d+$/.test(argv[i])) only.push(Number(argv[i]));
  }
  return { page, only };
}

(async () => {
  const { page: pagePath, only } = parseArgs(process.argv.slice(2));
  if (!fs.existsSync(pagePath)) {
    console.error(`source page not found: ${path.relative(ROOT, pagePath)}`);
    process.exit(1);
  }
  fs.mkdirSync(OUT, { recursive: true });

  const browser = await chromium.launch({
    args: ['--force-color-profile=srgb', '--font-render-hinting=none'],
  });
  const context = await browser.newContext({
    viewport: { width: CANVAS_W, height: CANVAS_H },
    deviceScaleFactor: SCALE,
  });
  const page = await context.newPage();

  await page.goto('file://' + pagePath, { waitUntil: 'networkidle' });
  await page.evaluate(() => document.fonts.ready);

  const slides = await page.$$('.slide');
  if (!slides.length) {
    console.error('no .slide sections found in the source page');
    process.exit(1);
  }

  const written = [];
  for (let i = 0; i < slides.length; i++) {
    const n = i + 1;
    if (only.length && !only.includes(n)) continue;
    const role = (await slides[i].getAttribute('data-role')) || 'slide';
    const name = `${String(n).padStart(2, '0')}-${role}.png`;
    const dest = path.join(OUT, name);
    await slides[i].screenshot({ path: dest }); // clips to the slide box, 2x
    written.push(dest);
    console.log(`  ✓ slide ${n} (${role}) -> out/${name}`);
  }

  await browser.close();

  // Downscale the 2x captures to exactly 1080x1350 using Chromium itself.
  await downscale(written);
  console.log(`done — ${written.length} slide(s).`);
})().catch((e) => {
  console.error(e);
  process.exit(1);
});

async function downscale(files) {
  if (!files.length) return;
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setViewportSize({ width: CANVAS_W, height: CANVAS_H });
  for (const p of files) {
    const b64 = fs.readFileSync(p).toString('base64');
    await page.setContent(
      `<style>*{margin:0}html,body{width:${CANVAS_W}px;height:${CANVAS_H}px}` +
        `img{width:${CANVAS_W}px;height:${CANVAS_H}px;display:block}</style>` +
        `<img src="data:image/png;base64,${b64}">`,
      { waitUntil: 'load' }
    );
    await page.screenshot({ path: p, clip: { x: 0, y: 0, width: CANVAS_W, height: CANVAS_H } });
  }
  await browser.close();
}
