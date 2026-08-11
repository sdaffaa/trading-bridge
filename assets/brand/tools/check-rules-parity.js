#!/usr/bin/env node
/*
 * The drawing rules live in two places: markup.js applies them while drawing,
 * verify_drawing.py checks them standalone. Two implementations drift, so this
 * runs both over the same spec and fails loudly on the first disagreement.
 *
 *   node tools/check-rules-parity.js [spec.json]
 *
 * Defaults to the skill's bundled example.
 */
const { execFileSync } = require('child_process');
const fs = require('fs');
const path = require('path');

global.window = {};
require(path.join(__dirname, '..', 'markup.js'));
const { LSChart } = global.window;

const specPath = process.argv[2] || path.join(
  __dirname, '..', '..', '..', '.claude', 'skills',
  'chart-drawing-accuracy', 'examples', 'demo-spec.json');

const spec = JSON.parse(fs.readFileSync(specPath, 'utf8'));
const pyScript = path.join(
  __dirname, '..', '..', '..', '.claude', 'skills',
  'chart-drawing-accuracy', 'scripts', 'verify_drawing.py');

// verify_drawing.py exits 1 whenever it finds a violation, which is the normal
// case here — read its stdout either way and only treat a crash as an error.
let pyOut;
try {
  pyOut = execFileSync('python3', [pyScript, specPath, '--json'], { encoding: 'utf8' });
} catch (e) {
  if (e.stdout && e.status === 1) pyOut = e.stdout;
  else throw e;
}
const py = JSON.parse(pyOut).findings;
const js = LSChart.audit(spec.candles, spec.drawings);

let bad = 0;
console.log(`comparing ${js.length} drawings from ${path.basename(specPath)}\n`);
for (let i = 0; i < py.length; i++) {
  const p = py[i], j = js[i];
  const same = p.status === j.status && p.should_end_at === j.should_end_at;
  if (!same) {
    bad++;
    console.log(`  MISMATCH  ${p.id}`);
    console.log(`     python: ${p.status} → ${p.should_end_at}`);
    console.log(`     js:     ${j.status} → ${j.should_end_at}`);
  } else {
    console.log(`  ok  ${p.id.padEnd(14)} ${p.status}` +
                (p.should_end_at === null ? '' : ` → ${p.should_end_at}`));
  }
}

if (bad) {
  console.error(`\n${bad} disagreement(s) — the two rule implementations have drifted.`);
  process.exit(1);
}
console.log('\nboth implementations agree.');
