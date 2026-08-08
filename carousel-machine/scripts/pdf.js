/* ============================================================================
 * pdf.js — build the explanatory PDF lead magnet (and, optionally, a PDF
 * export of the carousel itself).
 *
 *   node scripts/pdf.js                 # out/liquidity-state-guide.pdf (A4)
 *   node scripts/pdf.js --carousel      # + out/carousel.pdf (1080x1350 pages)
 *   node scripts/pdf.js --preview       # + PNG preview of each guide page
 *
 * The guide is the file ManyChat sends when someone comments the keyword.
 * It reuses brand.css tokens via guide.css, so it can never drift from the
 * carousel's visual identity.
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
const SRC = path.join(ROOT, 'src');
const OUT = path.join(ROOT, 'out');

const GUIDE_PDF = path.join(OUT, 'liquidity-state-guide.pdf');
const CAROUSEL_PDF = path.join(OUT, 'carousel.pdf');

/* Count pages without a PDF library: Chromium writes an uncompressed page tree,
 * so /Type /Page (not /Pages) is a reliable marker. Returns null if unreadable. */
function pdfPageCount(file) {
  const raw = fs.readFileSync(file).toString('latin1');
  const m = raw.match(/\/Type\s*\/Page(?![s])/g);
  return m ? m.length : null;
}

(async () => {
  const args = process.argv.slice(2);
  const wantCarousel = args.includes('--carousel');
  const wantPreview = args.includes('--preview');

  fs.mkdirSync(OUT, { recursive: true });
  const browser = await chromium.launch();

  /* ---- 1. The explanatory guide (A4) ------------------------------------ */
  const guideSrc = path.join(SRC, 'guide.html');
  if (!fs.existsSync(guideSrc)) {
    console.error('missing src/guide.html');
    process.exit(1);
  }
  const page = await browser.newPage();
  await page.goto('file://' + guideSrc, { waitUntil: 'networkidle' });
  await page.evaluate(() => document.fonts.ready);

  await page.pdf({
    path: GUIDE_PDF,
    format: 'A4',
    printBackground: true,
    preferCSSPageSize: true,
    margin: { top: '0', right: '0', bottom: '0', left: '0' },
  });
  const gPages = pdfPageCount(GUIDE_PDF);
  const gSize = (fs.statSync(GUIDE_PDF).size / 1024).toFixed(0);
  console.log(`  ✓ out/${path.basename(GUIDE_PDF)} — ${gPages ?? '?'} صفحات · ${gSize} KB`);

  // Optional PNG preview of each guide page, for the mandatory visual check.
  if (wantPreview) {
    const sections = await page.$$('.page');
    for (let i = 0; i < sections.length; i++) {
      const dest = path.join(OUT, `guide-p${String(i + 1).padStart(2, '0')}.png`);
      await sections[i].screenshot({ path: dest });
      console.log(`     · preview out/${path.basename(dest)}`);
    }
  }

  /* ---- 2. Optional: the carousel as a PDF -------------------------------- */
  if (wantCarousel) {
    const carSrc = path.join(SRC, 'carousel.html');
    const p2 = await browser.newPage();
    await p2.goto('file://' + carSrc, { waitUntil: 'networkidle' });
    await p2.evaluate(() => document.fonts.ready);
    // Neutralize the authoring view so each slide becomes exactly one page.
    await p2.addStyleTag({
      content:
        'body{display:block!important;gap:0!important;padding:0!important;background:none!important}' +
        '.slide{page-break-after:always;break-after:page;margin:0!important}' +
        '.slide:last-of-type{page-break-after:auto;break-after:auto}',
    });
    await p2.pdf({
      path: CAROUSEL_PDF,
      width: '1080px',
      height: '1350px',
      printBackground: true,
      margin: { top: '0', right: '0', bottom: '0', left: '0' },
    });
    const cPages = pdfPageCount(CAROUSEL_PDF);
    const cSize = (fs.statSync(CAROUSEL_PDF).size / 1024).toFixed(0);
    console.log(`  ✓ out/${path.basename(CAROUSEL_PDF)} — ${cPages ?? '?'} صفحات · ${cSize} KB`);
  }

  await browser.close();
  console.log('done.');
})().catch((e) => {
  console.error(e);
  process.exit(1);
});
