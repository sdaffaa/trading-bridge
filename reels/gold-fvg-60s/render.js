const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs'), { spawn } = require('child_process'), path = require('path');
(async () => {
  const mode = process.argv[2] || 'stills';
  const browser = await chromium.launch({ args: ['--allow-file-access-from-files'], executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
  const page = await browser.newPage({ viewport: { width: 540, height: 960 } });
  page.on('console', m => console.log('page:', m.text())); page.on('pageerror', e => console.log('ERR', e.message));
  await page.goto('file://' + path.resolve('chart.html'));
  const T = await page.evaluate(d => window.setup(d), JSON.parse(fs.readFileSync('trade.json')));
  console.log(JSON.stringify(T));
  fs.writeFileSync('timeline.json', JSON.stringify({ T, S: await page.evaluate(() => window.sched()) }));
  const dec = s => Buffer.from(s.split(',')[1], 'base64');
  if (mode === 'stills') {
    fs.mkdirSync('stills', { recursive: true });
    for (const a of process.argv.slice(3)) {
      const f = isNaN(+a) ? Math.round(eval(a.replace(/[a-zA-Z]+/g, k => 'T.' + k))) : +a;
      fs.writeFileSync(`stills/${a.replace(/[^\w+-]/g, '_')}.png`, dec(await page.evaluate(f => window.frame(f), f)));
    }
  } else if (mode === 'probe') {
    const out = [];
    for (let f = 0; f < T.total; f += 15) out.push({ f, ...(await page.evaluate(f => window.probe(f), f)) });
    fs.writeFileSync('probe.json', JSON.stringify(out));
  } else {
    const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', '60', '-c:v', 'mjpeg', '-i', '-',
      '-c:v', 'libx264', '-preset', 'slow', '-crf', '18', '-pix_fmt', 'yuv420p', '-r', '60', '-movflags', '+faststart', 'video_silent.mp4'], { stdio: ['pipe', 'inherit', 'inherit'] });
    for (let f = 0; f < T.total; f++) {
      const buf = dec(await page.evaluate(f => window.frame(f, 'image/jpeg'), f));
      if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
      if (f % 600 === 0) console.log('frame', f, '/', T.total);
    }
    ff.stdin.end(); await new Promise(r => ff.on('close', r));
  }
  await browser.close();
})();
