// Exporta la animación cuadro por cuadro: node record.js  ->  frames/ + ffmpeg
const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

(async () => {
  const fps = 30;
  const out = path.join(__dirname, 'frames');
  fs.rmSync(out, { recursive: true, force: true });
  fs.mkdirSync(out);
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1000, height: 700 } });
  await page.goto('file://' + path.join(__dirname, 'index.html') + '?capture');
  await page.waitForFunction(() => window.ready);
  const loop = await page.evaluate(() => window.LOOP);
  const canvas = await page.$('canvas');
  const n = Math.round(loop * fps);
  for (let i = 0; i < n; i++) {
    await page.evaluate(t => window.renderAt(t), i / fps);
    await canvas.screenshot({ path: path.join(out, String(i).padStart(4, '0') + '.png') });
  }
  await browser.close();
  console.log(`${n} cuadros en ${out}`);
})();
