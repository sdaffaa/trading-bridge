const { chromium } = require('playwright');
const path = require('path');

const NAMES = ['01-cover','02-stakes','03-what','04-trap','05-stat','06-examples','07-cta'];

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ deviceScaleFactor: 2 });
  await page.goto('file://' + path.resolve(__dirname, 'carousel.html'), { waitUntil: 'networkidle' });
  await page.waitForTimeout(400); // let inline JS charts/fonts settle
  for (let i = 0; i < 7; i++) {
    const el = await page.$('#s' + (i + 1));
    await el.screenshot({ path: path.resolve(__dirname, 'out', NAMES[i] + '.png') });
    console.log('rendered', NAMES[i]);
  }
  await browser.close();
})();
