import { chromium } from 'playwright';
import { pathToFileURL } from 'url';
const b = await chromium.launch();
const pg = await b.newPage({ viewport: { width:1080, height:1920 }, deviceScaleFactor:1 });
await pg.goto(pathToFileURL('cover.html').href);
await pg.waitForTimeout(1200);
await (await pg.$('.poster')).screenshot({ path:'cover.png' });
await b.close();
console.log('OK');
