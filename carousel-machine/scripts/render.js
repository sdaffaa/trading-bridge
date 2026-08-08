/* ============================================================================
 * render.js — HTML slides -> PNG at exactly 1080x1350.
 *
 * Renders at deviceScaleFactor 2 (2160x2700) then downscales to 1080x1350 for
 * a sharper result (master prompt §8.4). Fonts are base64-embedded in
 * fonts.css so the headless browser never waits on a network font.
 *
 * Usage:
 *   node scripts/render.js                 # render every src/slide-*.html
 *   node scripts/render.js src/slide-01.html src/slide-05.html
 * ==========================================================================*/
'use strict';

const path = require('path');
const fs = require('fs');

// Resolve Playwright locally if installed, else fall back to the environment's
// pre-installed global install (Chromium is provided at PLAYWRIGHT_BROWSERS_PATH).
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
    throw new Error('playwright not found — see carousel-machine/README.md (Setup).');
  }
}

const ROOT = path.resolve(__dirname, '..');
const SRC = path.join(ROOT, 'src');
const OUT = path.join(ROOT, 'out');

const CANVAS_W = 1080;
const CANVAS_H = 1350;
const SCALE = 2;

// slide-01.html -> 01-cover.png  (role names for nicer filenames)
const ROLE = {
  '01': 'cover', '02': 'stakes', '03': 'turn', '04': 'rule',
  '05': 'proof', '06': 'reframe', '07': 'cta',
};

function slideFiles(argv) {
  if (argv.length) return argv.map((a) => path.resolve(a));
  return fs
    .readdirSync(SRC)
    .filter((f) => /^slide-\d+\.html$/.test(f))
    .sort()
    .map((f) => path.join(SRC, f));
}

function outName(file) {
  const m = path.basename(file).match(/slide-(\d+)\.html$/);
  const num = m ? m[1] : '00';
  const role = ROLE[num] ? `-${ROLE[num]}` : '';
  return `${num}${role}.png`;
}

(async () => {
  fs.mkdirSync(OUT, { recursive: true });
  const files = slideFiles(process.argv.slice(2));
  if (!files.length) {
    console.error('no slides found in src/');
    process.exit(1);
  }

  const browser = await chromium.launch({
    args: ['--force-color-profile=srgb', '--font-render-hinting=none'],
  });
  const context = await browser.newContext({
    viewport: { width: CANVAS_W, height: CANVAS_H },
    deviceScaleFactor: SCALE,
  });
  const page = await context.newPage();

  for (const file of files) {
    await page.goto('file://' + file, { waitUntil: 'networkidle' });
    // Ensure the embedded font is fully parsed before shooting.
    await page.evaluate(() => document.fonts.ready);
    const el = await page.$('.slide');
    if (!el) {
      console.error(`  ! no .slide element in ${path.basename(file)} — skipped`);
      continue;
    }
    const dest = path.join(OUT, outName(file));
    await el.screenshot({ path: dest }); // clips to the .slide box at 2160x2700
    console.log(`  ✓ ${path.basename(file)} -> out/${path.basename(dest)}`);
  }

  await browser.close();

  // Downscale 2x captures to exactly 1080x1350 using Chromium itself (no extra deps).
  await downscaleAll(files);
  console.log('done.');
})().catch((e) => {
  console.error(e);
  process.exit(1);
});

async function downscaleAll(files) {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  for (const file of files) {
    const p = path.join(OUT, outName(file));
    if (!fs.existsSync(p)) continue;
    const b64 = fs.readFileSync(p).toString('base64');
    await page.setViewportSize({ width: CANVAS_W, height: CANVAS_H });
    await page.setContent(
      `<style>*{margin:0}html,body{width:${CANVAS_W}px;height:${CANVAS_H}px}` +
        `img{width:${CANVAS_W}px;height:${CANVAS_H}px;display:block;image-rendering:auto}</style>` +
        `<img src="data:image/png;base64,${b64}">`,
      { waitUntil: 'load' }
    );
    await page.screenshot({ path: p, clip: { x: 0, y: 0, width: CANVAS_W, height: CANVAS_H } });
  }
  await browser.close();
}
