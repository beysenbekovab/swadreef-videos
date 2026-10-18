// node render.mjs ../qamar-mushaf.mp4 [30]     весь ролик (нужен mix.wav — python3 sfx.py)
// node render.mjs --stills 3,9.5,15,19,23,27   кадры для проверки → stills/
import { createRequire } from 'node:module';
import { spawn } from 'node:child_process';
import { createServer } from 'node:http';
import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { extname, join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const require = createRequire(import.meta.url);
let chromium;
try { ({ chromium } = require('playwright')); }
catch { ({ chromium } = require(join(process.execPath, '../../lib/node_modules/playwright'))); }

const here = dirname(fileURLToPath(import.meta.url));
const args = process.argv.slice(2);
const STILLS = args[0] === '--stills' ? args[1].split(',').map(Number) : null;
const OUT = STILLS ? null : (args[0] || join(here, '../qamar-mushaf.mp4')), FPS = Number((!STILLS && args[1]) || 30);
const TYPES = { '.html': 'text/html', '.json': 'application/json', '.png': 'image/png', '.jpg': 'image/jpeg',
  '.woff2': 'font/woff2', '.ttf': 'font/ttf', '.js': 'text/javascript', '.css': 'text/css' };
const server = createServer(async (req, res) => {
  try {
    const p = join(here, 'web', decodeURIComponent(new URL(req.url, 'http://x').pathname));
    res.writeHead(200, { 'content-type': TYPES[extname(p)] || 'application/octet-stream' }); res.end(await readFile(p));
  } catch { res.writeHead(404); res.end(); }
}).listen(8790);

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
await page.goto('http://127.0.0.1:8790/index.html');
await page.waitForFunction(() => window.READY === true, null, { timeout: 30000 });
const cdp = await page.context().newCDPSession(page);
const shot = async (t, q) => {
  await page.evaluate(t => window.render(t), t);
  const { data } = await cdp.send('Page.captureScreenshot', { format: 'jpeg', quality: q });
  return Buffer.from(data, 'base64');
};

if (STILLS) {
  await mkdir(join(here, 'stills'), { recursive: true });
  for (const t of STILLS) await writeFile(join(here, `stills/t_${t}.jpg`), await shot(t, 85));
} else {
  const dur = await page.evaluate(() => window.TLDUR), n = Math.round(dur * FPS);
  const ff = spawn('ffmpeg', ['-v', 'error', '-y', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-',
    '-i', join(here, 'mix.wav'), '-map', '0:v', '-map', '1:a',
    '-vf', 'scale=out_color_matrix=bt709:out_range=tv,format=yuv420p',
    '-c:v', 'libx264', '-preset', 'slow', '-crf', '16', '-profile:v', 'high',
    '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-color_range', 'tv',
    '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-t', String(dur), '-movflags', '+faststart', OUT],
    { stdio: ['pipe', 'inherit', 'inherit'] });
  for (let f = 0; f < n; f++) {
    if (!ff.stdin.write(await shot(f / FPS, 95))) await new Promise(r => ff.stdin.once('drain', r));
    if (f % 150 === 0) console.log(`frame ${f}/${n}`);
  }
  ff.stdin.end(); await new Promise(r => ff.on('close', r));
  console.log('→', OUT);
}
await browser.close(); server.close();
