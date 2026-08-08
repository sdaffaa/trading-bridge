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

/* ---- Remove whole elements whose class matches, nesting included ----------
 * A non-greedy regex stops at the first inner </tag> and leaks the parent's
 * remaining text, so walk tag depth to find the real closing tag instead. */
function stripExcluded(html, classRe) {
  const open = /<([a-z][\w-]*)\b([^>]*)>/gi;
  for (let guard = 0; guard < 500; guard++) {
    open.lastIndex = 0;
    let m, hit = null;
    while ((m = open.exec(html))) {
      const attrs = m[2];
      const cls = /class\s*=\s*"([^"]*)"/i.exec(attrs);
      if (cls && classRe.test(cls[1]) && !/\/$/.test(attrs)) {
        hit = { tag: m[1], start: m.index, after: open.lastIndex };
        break;
      }
    }
    if (!hit) return html;

    // walk forward, tracking depth of same-named tags, to the matching close
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

/* ---- Visible-text word count per slide -----------------------------------
 * Counts CONTENT words only (headline + body + steps + quote + CTA), per the
 * §6 caps. Excludes: brand chrome, category kicker, meta labels, the mandatory
 * legal disclaimer, the "توضيحي" tag, and chart annotation callouts. Also
 * excludes pure numeric / currency / R tokens — they are data, not reading load. */
function words(html) {
  const EXCLUDE = 'band|kicker|kchip|chip|idx|wordmark|pagebox|foot|dots|label|disclaimer|'
                + 'schematic-tag|callout|clab|axis-note|counter|handle|ghost';
  let s = stripExcluded(
      html.replace(/<!--[\s\S]*?-->/g, ' ')
          .replace(/<svg[\s\S]*?<\/svg>/gi, ' '), // charts/logos are not words
      new RegExp(`\\b(?:${EXCLUDE})\\b`))
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

// 4) light palette only — assert the slide ground tokens are genuinely light.
// Computed from the tokens themselves so a palette change can't silently pass.
const css = fs.readFileSync(path.join(SRC, 'brand.css'), 'utf8');
function token(name) {
  const m = css.match(new RegExp(`--${name}:\\s*(#[0-9A-Fa-f]{6})`));
  return m ? m[1] : null;
}
const grounds = ['bg-top', 'bg-bottom'].map((n) => token(n));
const lightBg = grounds.every((c) => c && lum(c) > 0.6); // clearly light, never a dark hero
check(lightBg, 'لوحة فاتحة فقط (لا خلفيات داكنة للسلايد)', grounds.join(' → '));

// 5) contrast on the key text/background pairs (target ≥ 4.5:1)
// Colors are read from brand.css tokens so the check tracks the real palette.
const CREAM = token('bg-top') || '#F4EFE8';
const pairs = [
  ['ink on cream', token('ink'), CREAM],
  ['ink on surface', token('ink'), token('surface')],
  ['ink-2 body on cream', token('ink-2'), CREAM],
  ['ink-3 label on cream', token('ink-3'), CREAM],
  ['accent (wordmark/keyword) on cream', token('accent'), CREAM],
  ['accent on tint box', token('accent'), token('surface-alt')],
  ['bear text on cream', token('bear'), CREAM],
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
