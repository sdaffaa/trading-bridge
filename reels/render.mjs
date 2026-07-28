// Deterministic frame renderer: drives template.html via window.__setT(t)
// Usage: node render.mjs [template.html] [out_frames_dir]
import { chromium } from 'playwright-core';
import { fileURLToPath, pathToFileURL } from 'url';
import path from 'path';
import fs from 'fs';

const CHROME = '/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell';
const tpl = process.argv[2] || 'template.html';
const framesDir = process.argv[3] || 'out/frames';
fs.rmSync(framesDir, { recursive: true, force: true });
fs.mkdirSync(framesDir, { recursive: true });

const url = pathToFileURL(path.resolve(tpl)).href;

const browser = await chromium.launch({
  executablePath: CHROME,
  args: ['--no-sandbox', '--force-color-profile=srgb', '--disable-lcd-text', '--hide-scrollbars']
});
const page = await browser.newPage({
  viewport: { width: 1080, height: 1920 },
  deviceScaleFactor: 1
});
await page.goto(url, { waitUntil: 'networkidle' });
await page.evaluate(() => document.fonts.ready);
await page.waitForTimeout(300);

const meta = await page.evaluate(() => window.__meta());
const { fps, duration } = meta;
const total = Math.round(fps * duration);
console.log(`Rendering ${total} frames @ ${fps}fps (${duration}s)`);

const stage = await page.$('#stage');
for (let f = 0; f < total; f++) {
  const t = f / fps;
  await page.evaluate((t) => window.__setT(t), t);
  await page.evaluate(() => new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r))));
  await stage.screenshot({ path: path.join(framesDir, `f${String(f).padStart(4, '0')}.png`) });
  if (f % 30 === 0) process.stdout.write(`  ${f}/${total}\r`);
}
console.log(`\nDone: ${total} frames -> ${framesDir}`);
await browser.close();
