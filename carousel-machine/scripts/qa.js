/* ============================================================================
 * qa.js — automated slice of the QA gate (master prompt §9).
 *
 * Reads the single source page (src/carousel.html) and the PDF guide.
 * Automatable checks only. The VISUAL checks (Arabic shaping connected,
 * numbers not reversed, nothing clipped) still require a human/agent to open
 * each PNG — this script prints that reminder and never claims the visual
 * gate passed.
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

// on-screen content-word caps per slide (master prompt §6)
const WORD_CAP = { 1: 12, 2: 25, 3: 25, 4: 35, 5: 20, 6: 14, 7: 18 };

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
  return { w: b.readUInt32BE(16), h: b.readUInt32BE(20) };
}

/* ---- PDF page count (Chromium writes an uncompressed page tree) --------- */
function pdfPageCount(file) {
  const raw = fs.readFileSync(file).toString('latin1');
  const m = raw.match(/\/Type\s*\/Page(?![s])/g);
  return m ? m.length : null;
}

/* ---- Split the source page into its <section class="slide"> blocks ------ */
function splitSlides(html) {
  const out = [];
  const open = /<section[^>]*class="[^"]*\bslide\b[^"]*"[^>]*>/gi;
  let m;
  while ((m = open.exec(html))) {
    const end = html.indexOf('</section>', m.index);
    const body = html.slice(m.index, end === -1 ? html.length : end);
    const role = /data-role="([^"]+)"/.exec(m[0]);
    out.push({ role: role ? role[1] : 'slide', html: body });
  }
  return out;
}

/* ---- Remove whole elements whose class matches, nesting included ----------
 * A non-greedy regex stops at the first inner </tag> and leaks the parent's
 * remaining text, so walk tag depth to find the real closing tag instead. */
function stripExcluded(html, classRe) {
  const open = /<([a-z][\w-]*)\b([^>]*)>/gi;
  for (let guard = 0; guard < 500; guard++) {
    open.lastIndex = 0;
    let m, hit = null;
    while ((m = open.exec(html))) {
      const cls = /class\s*=\s*"([^"]*)"/i.exec(m[2]);
      if (cls && classRe.test(cls[1]) && !/\/$/.test(m[2])) {
        hit = { tag: m[1], start: m.index, after: open.lastIndex };
        break;
      }
    }
    if (!hit) return html;

    const scan = new RegExp(`<(/?)${hit.tag}\\b[^>]*>`, 'gi');
    scan.lastIndex = hit.after;
    let depth = 1, end = html.length, t;
    while ((t = scan.exec(html))) {
      depth += t[1] ? -1 : 1;
      if (depth === 0) { end = scan.lastIndex; break; }
    }
    html = html.slice(0, hit.start) + ' ' + html.slice(end);
  }
  return html;
}

/* ---- Visible content-word count -----------------------------------------
 * Counts reading load only (headline + body + rows + quote + CTA). Excludes
 * brand chrome, category chips, meta labels, the legal disclaimer, chart
 * annotations, and pure numeric tokens — those are data, not reading load. */
function words(html) {
  const EXCLUDE = 'band|kicker|kchip|chip|idx|wordmark|pagebox|foot|dots|label|disclaimer|'
                + 'schematic-tag|callout|clab|axis-note|counter|handle|ghost';
  const s = stripExcluded(
      html.replace(/<!--[\s\S]*?-->/g, ' ').replace(/<svg[\s\S]*?<\/svg>/gi, ' '),
      new RegExp(`\\b(?:${EXCLUDE})\\b`))
    .replace(/<style[\s\S]*?<\/style>/gi, ' ')
    .replace(/<[^>]+>/g, ' ')
    .replace(/&[a-z]+;/gi, ' ')
    .replace(/[«»…📌←·]/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
  const tokens = s.length ? s.split(' ').filter(Boolean) : [];
  return tokens.filter((t) => /[؀-ۿ]/.test(t)); // Arabic-bearing tokens only
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

// 1) single source page with seven slides
const pagePath = path.join(SRC, 'carousel.html');
const pageHtml = fs.existsSync(pagePath) ? fs.readFileSync(pagePath, 'utf8') : '';
const slides = splitSlides(pageHtml);
check(slides.length === 7, 'سبع سلايدات في صفحة المصدر الواحدة', `${slides.length}/7 · src/carousel.html`);

// 2) the gem is defined once and reused (no per-slide drift)
const gemDefs = (pageHtml.match(/<symbol id="gem"/g) || []).length;
const gemUses = (pageHtml.match(/<use href="#gem"/g) || []).length;
check(gemDefs === 1, 'شعار الجوهرة معرّف مرة واحدة', `${gemDefs} تعريف · ${gemUses} استخدام`);

// 3) word caps
slides.forEach((s, i) => {
  const n = i + 1;
  const cap = WORD_CAP[n];
  const w = words(s.html).length;
  check(w <= cap, `سقف الكلمات · سلايد ${n} (${s.role})`, `${w} ≤ ${cap}`);
});

// 4) disclaimer on the trade/proof slide
const proof = slides.find((s) => s.role === 'proof');
check(!!proof && /لغرض تعليمي/.test(proof.html), 'سطر المخاطر على سلايد الصفقة', 'data-role="proof"');

// 5) light palette — computed from the tokens themselves, so a palette change
//    can never silently pass this gate.
const css = fs.readFileSync(path.join(SRC, 'brand.css'), 'utf8');
function token(name) {
  const m = css.match(new RegExp(`--${name}:\\s*(#[0-9A-Fa-f]{6})`));
  return m ? m[1] : null;
}
const grounds = ['bg-top', 'bg-bottom'].map((n) => token(n));
check(grounds.every((c) => c && lum(c) > 0.6), 'لوحة فاتحة فقط (لا خلفيات داكنة)', grounds.join(' → '));

// 6) contrast, read from the real tokens
const CREAM = token('bg-top');
const pairs = [
  ['ink on cream', token('ink'), CREAM],
  ['ink on surface', token('ink'), token('surface')],
  ['ink-2 body on cream', token('ink-2'), CREAM],
  ['ink-3 label on cream', token('ink-3'), CREAM],
  ['accent on cream', token('accent'), CREAM],
  ['accent on tint box', token('accent'), token('surface-alt')],
  ['bear text on cream', token('bear'), CREAM],
];
for (const [name, fg, bg] of pairs) {
  const r = contrast(fg, bg);
  check(r >= 4.5, `تباين: ${name}`, `${r.toFixed(2)}:1`);
}

// 7) exported PNGs
const pngs = fs.existsSync(OUT)
  ? fs.readdirSync(OUT).filter((f) => /^\d\d-.*\.png$/.test(f)).sort() : [];
if (pngs.length) {
  check(pngs.length === 7, 'سبع صور مصدّرة', `${pngs.length}/7`);
  for (const p of pngs) {
    const { w, h } = pngSize(path.join(OUT, p));
    check(w === CANVAS_W && h === CANVAS_H, `مقاس ${p}`, `${w}×${h}`);
  }
} else {
  report.push('- [ ] ⚠️ لم يتم الرندر بعد — شغّل `node scripts/render.js`.');
  console.log('⚠️ no PNGs yet — run render.js then re-run qa.js.');
}

// 8) the PDF lead magnet
const guideSrc = path.join(SRC, 'guide.html');
const guidePdf = path.join(OUT, 'liquidity-state-guide.pdf');
check(fs.existsSync(guideSrc), 'مصدر الدليل موجود', 'src/guide.html');
if (fs.existsSync(guidePdf)) {
  const n = pdfPageCount(guidePdf);
  const kb = (fs.statSync(guidePdf).size / 1024).toFixed(0);
  check(n !== null && n >= 4, 'ملف الدليل PDF مبني', `${n} صفحات · ${kb} KB`);
  const g = fs.readFileSync(guideSrc, 'utf8');
  check(/لغرض تعليمي فقط/.test(g), 'سطر المخاطر داخل الدليل', 'guide.html');
  // the guide states its own page count on the cover — keep it honest
  const claim = /class="meta">[^<]*?<span class="num">(\d+)<\/span>\s*صفحات/.exec(g);
  if (claim) {
    check(Number(claim[1]) === n, 'عدد الصفحات المعلن يطابق الملف', `مكتوب ${claim[1]} · فعلي ${n}`);
  }
} else {
  report.push('- [ ] ⚠️ الدليل غير مبني — شغّل `node scripts/pdf.js`.');
  console.log('⚠️ guide PDF not built — run pdf.js.');
}

// ---- manual visual gate reminder (cannot be automated) ------------------
report.push('');
report.push('### فحص بصري يدوي إلزامي (لا يُؤتمت)');
report.push('- [ ] الحروف العربية متصلة في كل صورة وفي كل صفحة من الدليل');
report.push('- [ ] الأرقام والمعادلات غير معكوسة');
report.push('- [ ] لا نص مقصوص · الهوامش مطبّقة · آخر ١٢٠px فاضية من النص');
report.push('- [ ] الغلاف مقروء بحجم ١٥٠px (thumbnail)');
report.push('- [ ] سلايد الاقتباس (٦) يشتغل وحده كسكرين شوت');

fs.mkdirSync(OUT, { recursive: true });
const head = `# QA Report — Liquidity State Carousel\n\nAutomated checks: **${failures === 0 ? 'PASS' : failures + ' FAIL'}**\n\n`;
fs.writeFileSync(path.join(OUT, 'qa-report.md'), head + report.join('\n') + '\n');
console.log(`\nreport -> out/qa-report.md  (automated failures: ${failures})`);
process.exit(failures === 0 ? 0 : 1);
