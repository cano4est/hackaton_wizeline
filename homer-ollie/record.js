// Renderiza la animación cuadro por cuadro y la manda a ffmpeg.
//   node record.js [fps]  ->  build/video.mp4 (sin audio) + build/timeline.json
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');
const http = require('http');

// Servidor estático mínimo: con file:// el canvas queda "tainted" y no se puede exportar.
function serve(dir) {
  const types = { '.html': 'text/html', '.png': 'image/png', '.ttf': 'font/ttf', '.m4a': 'audio/mp4' };
  const server = http.createServer((req, res) => {
    const file = path.join(dir, decodeURIComponent(new URL(req.url, 'http://x').pathname));
    if (!file.startsWith(dir) || !fs.existsSync(file) || fs.statSync(file).isDirectory()) { res.writeHead(404); return res.end(); }
    res.writeHead(200, { 'Content-Type': types[path.extname(file)] || 'application/octet-stream' });
    fs.createReadStream(file).pipe(res);
  });
  return new Promise(r => server.listen(0, '127.0.0.1', () => r(server)));
}

(async () => {
  const fps = Number(process.argv[2] || 60);
  const out = path.join(__dirname, 'build');
  fs.mkdirSync(out, { recursive: true });

  const server = await serve(__dirname);
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto(`http://127.0.0.1:${server.address().port}/index.html?capture`);
  await page.waitForFunction(() => window.ready);
  const timeline = await page.evaluate(() => window.timeline);
  fs.writeFileSync(path.join(out, 'timeline.json'), JSON.stringify(timeline, null, 2));

  const ffmpeg = spawn('ffmpeg', ['-loglevel', 'error', '-y', '-f', 'image2pipe', '-framerate', String(fps),
    '-i', '-', '-c:v', 'libx264', '-preset', 'slow', '-crf', '16', '-pix_fmt', 'yuv420p',
    path.join(out, 'video.mp4')], { stdio: ['pipe', 'inherit', 'inherit'] });

  const n = Math.round(timeline.loop * fps);
  for (let i = 0; i < n; i++) {
    const data = await page.evaluate(t => { window.renderAt(t); return document.querySelector('canvas').toDataURL('image/png'); }, i / fps);
    const buf = Buffer.from(data.split(',')[1], 'base64');
    if (!ffmpeg.stdin.write(buf)) await new Promise(r => ffmpeg.stdin.once('drain', r));
  }
  ffmpeg.stdin.end();
  await new Promise(r => ffmpeg.on('close', r));
  await browser.close();
  server.close();
  console.log(`${n} cuadros a ${fps} fps -> build/video.mp4`);
})();
