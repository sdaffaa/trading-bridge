const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs'), { spawn } = require('child_process'), path = require('path');
(async () => {
  const mode = process.argv[2] || 'stills';
  const browser = await chromium.launch({ args: ['--allow-file-access-from-files'], executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
  const page = await browser.newPage({ viewport: { width: 540, height: 960 } });
  page.on('console', m => console.log('page:', m.text())); page.on('pageerror', e => console.log('ERR', e.message));
  await page.goto('file://' + path.resolve(process.env.PAGE||'chart.html'));
  const T = await page.evaluate(d => window.setup(d), JSON.parse(fs.readFileSync('trade.json')));
  console.log(JSON.stringify(T));
  const dec = s => Buffer.from(s.split(',')[1], 'base64');
  if (mode === 'stills') {
    const fr = process.argv.slice(3).map(Number);
    fs.mkdirSync('stills', { recursive: true });
    for (const f of fr) fs.writeFileSync(`stills/${process.env.PFX||'f'}${f}.png`, dec(await page.evaluate(f => window.frame(f), f)));
  } else {
    const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', '30', '-i', '-',
      '-vf', 'scale=1080:1920:flags=lanczos', '-c:v', 'libx264', '-preset', 'slow', '-crf', '18', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', process.env.OUT||'out.mp4'], { stdio: ['pipe', 'inherit', 'inherit'] });
    for (let f = 0; f < T.total; f++) {
      const buf = dec(await page.evaluate(f => window.frame(f), f));
      if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    }
    ff.stdin.end(); await new Promise(r => ff.on('close', r));
  }
  await browser.close();
})();
