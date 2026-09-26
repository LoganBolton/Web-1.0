// End-to-end checks of the interactive parts of the Weave, through the proxy.
// usage: python -m othernet.serve &  then  node tools/smoke_test.js
const { chromium } = require(process.env.PW_PATH || 'playwright');
const results = [];
function check(name, ok, detail = '') { results.push([name, ok, detail]); console.log(`${ok ? 'PASS' : 'FAIL'}  ${name} ${detail}`); }

(async () => {
  const browser = await chromium.launch({ proxy: { server: process.env.WEAVE_PROXY || 'http://127.0.0.1:8080' } });
  const ctx = await browser.newContext();
  const page = await ctx.newPage();
  const errors = [];
  page.on('pageerror', e => errors.push(`${page.url()}: ${e.message}`));

  // Courier paywall: 3 free articles, then the wall, then the library pass unlocks.
  await page.goto('http://ostmerecourier.wir/section/politics/');
  const arts = await page.$$eval('.story h3 a', as => as.map(a => a.href));
  for (const a of arts.slice(0, 3)) await page.goto(a);
  await page.goto(arts[4]);
  check('courier paywall appears on 4th article', await page.isVisible('#pw-wall'));
  await page.fill('#pw-u', 'courier_share'); await page.fill('#pw-p', 'kittiwake7'); await page.click('#pw-form button');
  check('shared login is refused', (await page.textContent('#pw-msg')).includes('suspended'));
  await page.fill('#pw-u', 'athenaeum'); await page.fill('#pw-p', 'NINEFORDS-412'); await page.click('#pw-form button');
  check('library pass unlocks article', !(await page.isVisible('#pw-wall')) && (await page.textContent('#pw-msg')).includes('Welcome'));

  // Tallow Boards back room
  await page.goto('http://tallowboards.fol/forum/backroom/');
  await page.fill('#pw-u', 'member'); await page.fill('#pw-p', 'wicket'); await page.click('#pw-form button');
  check('back room opens with wicket', (await page.textContent('#pw-rest')).includes('Lockwright'));

  // Crier poll results only after voting
  await page.goto('http://thecrier.wir/poll.html'); await page.waitForSelector('button.vote');
  await page.click('button.vote');
  check('crier poll shows 38%', (await page.textContent('#app')).includes('38%'));

  // Emberline journey planner
  await page.goto('http://emberline.ves/?from=Lanternport&to=Ostmere'); await page.waitForSelector('#results table');
  check('emberline fare in lumes', (await page.textContent('#results')).includes('lm'));

  // Bazaar cart
  await page.goto('http://bazaar.ves/search/?q=kettlebright+k-40'); await page.waitForSelector('#res .tile');
  await page.click('#res .tile a'); await page.click('text=Add to basket');
  await page.goto('http://bazaar.ves/cart/'); await page.waitForSelector('#total b');
  check('bazaar basket total', (await page.textContent('#total')).includes('Total'));

  // Lanthorn search
  await page.goto('http://lanthorn.ves/search/?q=deepshaft+rescue'); await page.waitForSelector('.r a.t');
  check('lanthorn returns results', (await page.$$('.r a.t')).length >= 3);
  await page.goto('http://lanthorn.ves/search/?q=slatebrook+haulage'); await page.waitForTimeout(800);
  check('lanthorn cannot see the Moot rulings', !(await page.content()).includes('rulings.khr'));

  // Copper Kettle gift card
  await page.goto('http://copperkettle.ves/gift-cards/'); await page.fill('#gc', 'CK-3500-1400'); await page.click('#go');
  check('gift card balance 3.00', (await page.textContent('#bal')).includes('3.00'));

  // Recipe scaler
  await page.goto('http://hearthandhob.fol/recipe/gorse-hollow-apple-cake/'); await page.fill('#sv', '16'); await page.dispatchEvent('#sv', 'input');
  check('recipe scaler doubles flour', (await page.textContent('#ing')).includes('3 measures flour'));

  // Snip chain lands on Stillframe
  await page.goto('http://snip.ves/go'); await page.waitForURL(/stillframe/, { timeout: 8000 }).catch(() => {});
  check('snip chain reaches stillframe', page.url().includes('stillframe.hal'), page.url());

  // Unknown domain
  const r = await page.goto('http://nowhere.ves/');
  check('unknown domain is 404', r.status() === 404);

  check('no page script errors', errors.length === 0, errors.slice(0, 3).join(' | '));
  await browser.close();
  process.exit(results.every(r => r[1]) ? 0 : 1);
})();
