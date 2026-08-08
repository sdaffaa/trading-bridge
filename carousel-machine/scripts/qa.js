/* ============================================================================
 * qa.js — automated slice of the QA gate (master prompt §9).
 *
 * Automatable checks only. The VISUAL checks (Arabic shaping connected, numbers
 * not reversed, nothing clipped) still require a human/agent to open each PNG —
 * this script prints that reminder and never claims the visual gate passed.
 *
 *   node scripts/qa.js
 * ==========================================================================*/
'use strict';

const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const SRC = path.join(ROOT, 'src');
const OUT = path.join(ROOT, 'out');

const CANVAS_W = 1080;
const CANVAS_H = 1350;

// on-screen word caps per slide role (master prompt §6)
const WORD_CAP = { '01': 12, '02': 25, '03': 25, '04': 35, '05': 20, '06': 14, '07': 18 };

const report = [];
let failures = 0;
function check(ok, label, detail) {
  const mark = ok ? '✅' : '❌';
  if (!ok) failures++;
  report.push(`- [${ok ? 'x' : ' '}] ${mark} ${label}${detail ? ` — ${detail}` : ''}`);
  console.log(`${mark} ${label}${detail ? ` — ${detail}` : ''}`);
}

/* ---- PNG dimensions from the IHDR chunk (no image libs needed) ---------- */
function pngSize(file) {
  const b = fs.readFileSync(file);
  // PNG signature is 8 bytes; IHDR width/height are big-endian uint32 at 16/20.
  return { w: b.readUInt32BE(16), h: b.readUInt32BE(20) };
}

/* ---- Visible-text word count per slide -----------------------------------
 * Counts CONTENT words only (headline + body + steps + quote + CTA), per the
 * §6 caps. Excludes: brand chrome, category kicker, meta labels, the mandatory
 * legal disclaimer, the "توضيحي" tag, and chart annotation callouts. Also
 * excludes pure numeric / currency / R tokens — they are data, not reading load. */
function words(html) {
  const EXCLUDE = 'band|kicker|kchip|idx|wordmark|label|disclaimer|schematic-tag|callout|counter|handle|ghost';
  let s = html
    .replace(/<!--[\s\S]*?-->/g, ' ')
    .replace(/<svg[\s\S]*?<\/svg>/gi, ' ') // charts/logos are not words
    .replace(/<span class="dot"[^>]*><\/span>/gi, ' ') // strip decorative dot so kchip removes cleanly
    .replace(new RegExp(`<[^>]*class="[^"]*\\b(?:${EXCLUDE})\\b[^"]*"[^>]*>[\\s\\S]*?<\\/[^>]+>`, 'gi'), ' ')
    .replace(/<style[\s\S]*?<\/style>/gi, ' ')
    .replace(/<[^>]+>/g, ' ')
    .replace(/&[a-z]+;/gi, ' ')
    .replace(/[«»…📌←·]/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
  const tokens = s.length ? s.split(' ').filter(Boolean) : [];
  // keep only tokens that contain an Arabic letter (drops ١٪, $, ٣٤٠٠, ٢R, etc.)
  return tokens.filter((t) => /[؀-ۿ]/.test(t));
}

/* ---- WCAG relative-luminance contrast ----------------------------------- */
function lum(hex) {
  const n = hex.replace('#', '');
  const c = [0, 2, 4].map((i) => parseInt(n.slice(i, i + 2), 16) / 255)
    .map((v) => (v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4));
  return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2];
}
function contrast(a, b) {
  const [l1, l2] = [lum(a), lum(b)].sort((x, y) => y - x);
  return (l1 + 0.05) / (l2 + 0.05);
}

/* ========================================================================= */
console.log('== Liquidity State · Carousel QA ==\n');

// 1) all seven slides present
const slides = fs.readdirSync(SRC).filter((f) => /^slide-\d+\.html$/.test(f)).sort();
check(slides.length === 7, 'سبع سلايدات موجودة', `${slides.length}/7`);

// 2) word caps
for (const f of slides) {
  const num = f.match(/slide-(\d+)/)[1];
  const cap = WORD_CAP[num];
  const w = words(fs.readFileSync(path.join(SRC, f), 'utf8')).length;
  check(w <= cap, `سقف الكلمات ${f}`, `${w} ≤ ${cap}`);
}

// 3) disclaimer present on the trade/proof slide
const proof = fs.existsSync(path.join(SRC, 'slide-05.html'))
  ? fs.readFileSync(path.join(SRC, 'slide-05.html'), 'utf8') : '';
check(/لغرض تعليمي/.test(proof), 'سطر المخاطر على سلايد الصفقة', 'slide-05');

// 4) light palette only — no dark hero backgrounds in brand.css slide bg
const css = fs.readFileSync(path.join(SRC, 'brand.css'), 'utf8');
const lightBg = /--bg-top:\s*#F6F9F9/i.test(css) && /--bg-bottom:\s*#E9F1F0/i.test(css);
check(lightBg, 'لوحة فاتحة فقط (لا خلفيات داكنة للسلايد)', 'tokens verified');

// 5) contrast on the key text/background pairs (target ≥ 4.5:1)
const pairs = [
  ['ink on bg-top', '#0E1E24', '#F6F9F9'],
  ['ink on surface', '#0E1E24', '#FFFFFF'],
  ['ink-2 body on bg', '#37525A', '#F6F9F9'],
  ['ink-3 label on bg', '#5C7278', '#F6F9F9'],
  ['handle on brand band', '#EAF2F1', '#0E1E24'],
];
for (const [name, fg, bg] of pairs) {
  const r = contrast(fg, bg);
  check(r >= 4.5, `تباين: ${name}`, `${r.toFixed(2)}:1`);
}

// 6) rendered PNGs (only if render already ran)
const pngs = fs.existsSync(OUT) ? fs.readdirSync(OUT).filter((f) => f.endsWith('.png')).sort() : [];
if (pngs.length) {
  check(pngs.length === 7, 'سبع صور مصدّرة', `${pngs.length}/7`);
  for (const p of pngs) {
    const { w, h } = pngSize(path.join(OUT, p));
    check(w === CANVAS_W && h === CANVAS_H, `مقاس ${p}`, `${w}×${h}`);
  }
} else {
  report.push('- [ ] ⚠️ لم يتم الرندر بعد — شغّل `node scripts/render.js` ثم أعد QA للتحقق من الأبعاد.');
  console.log('⚠️ no PNGs yet — run render.js then re-run qa.js to verify dimensions.');
}

// ---- manual visual gate reminder (cannot be automated) ------------------
report.push('');
report.push('### فحص بصري يدوي إلزامي (لا يُؤتمت)');
report.push('- [ ] الحروف العربية متصلة في كل صورة');
report.push('- [ ] الأرقام غير معكوسة');
report.push('- [ ] لا نص مقصوص · الهوامش مطبّقة · آخر ١٢٠px فاضية');
report.push('- [ ] الغلاف مقروء بحجم ١٥٠px (thumbnail)');
report.push('- [ ] سلايد الاقتباس (٦) يشتغل وحده كسكرين شوت');

// ---- write report --------------------------------------------------------
fs.mkdirSync(OUT, { recursive: true });
const head = `# QA Report — Liquidity State Carousel\n\nAutomated checks: **${failures === 0 ? 'PASS' : failures + ' FAIL'}**\n\n`;
fs.writeFileSync(path.join(OUT, 'qa-report.md'), head + report.join('\n') + '\n');
console.log(`\nreport -> out/qa-report.md  (automated failures: ${failures})`);
process.exit(failures === 0 ? 0 : 1);
