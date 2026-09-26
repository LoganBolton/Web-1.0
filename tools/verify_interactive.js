// Replay the browser steps of interactive eval questions and check the answer appears.
// usage: python -m othernet.serve &   then   node tools/verify_interactive.js [evals/questions.jsonl]
const fs = require('fs');
const { chromium } = require(process.env.PW_PATH || 'playwright');

const norm = s => String(s).toLowerCase().replace(/,/g, '').replace(/\s+/g, ' ').trim();

(async () => {
  const file = process.argv[2] || 'evals/questions.jsonl';
  const qs = fs.readFileSync(file, 'utf8').trim().split('\n').map(JSON.parse).filter(q => q.steps && q.steps.length);
  const browser = await chromium.launch({ proxy: { server: process.env.WEAVE_PROXY || 'http://127.0.0.1:8080' } });
  let failed = 0;
  for (const q of qs) {
    const page = await (await browser.newContext()).newPage();
    let text = '';
    try {
      for (const [op, a, b] of q.steps) {
        if (op === 'goto') { await page.goto(a); await page.waitForLoadState('load'); }
        else if (op === 'fill') { await page.fill(a, b); await page.dispatchEvent(a, 'input'); }
        else if (op === 'select') { await page.selectOption(a, b); await page.dispatchEvent(a, 'change'); await page.dispatchEvent(a, 'input'); }
        else if (op === 'check') { await page.check(a); await page.dispatchEvent(a, 'input'); }
        else if (op === 'click') { await page.waitForSelector(a); await page.click(a); }
        else if (op === 'read') { await page.waitForTimeout(400); text = await page.textContent(a); }
      }
    } catch (e) { text = 'ERROR ' + e.message; }
    const wants = q.expect ? [q.expect] : [q.answer, ...(q.accept || [])];
    const ok = wants.some(w => norm(text).includes(norm(w)));
    if (!ok) failed++;
    console.log(`${ok ? 'PASS' : 'FAIL'} ${q.id} ${q.question.slice(0, 70)}${ok ? '' : '\n      wanted ' + JSON.stringify(wants) + ' got ' + JSON.stringify(text.slice(0, 200))}`);
    await page.context().close();
  }
  console.log(`${qs.length - failed}/${qs.length} interactive questions verified`);
  await browser.close();
  process.exit(failed ? 1 : 0);
})();
