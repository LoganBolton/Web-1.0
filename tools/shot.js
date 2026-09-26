// Screenshot Weave pages through the proxy.
// usage: node tools/shot.js out_dir url1 [url2 ...]   (server must be on :8080)
const { chromium } = require(process.env.PW_PATH || 'playwright');
(async () => {
  const [out, ...urls] = process.argv.slice(2);
  const browser = await chromium.launch({ proxy: { server: 'http://127.0.0.1:8080' } });
  const page = await browser.newPage({ viewport: { width: 1200, height: 900 } });
  const errors = [];
  page.on('pageerror', e => errors.push(e.message));
  let i = 0;
  for (const u of urls) {
    await page.goto(u, { waitUntil: 'load' });
    await page.waitForTimeout(300);
    const name = `${out}/${String(i++).padStart(2, '0')}-${u.replace(/[^a-z0-9]+/gi, '_').slice(7, 70)}.png`;
    await page.screenshot({ path: name, fullPage: false });
    console.log(name);
  }
  if (errors.length) console.log('JS errors:', errors);
  await browser.close();
})();
