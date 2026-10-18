// Рендер ролика: node render.mjs [out.mp4] [--stills]
// Покадрово вызывает renderFrame(t) в Chromium и склеивает кадры через ffmpeg.
import { createRequire } from 'node:module';
import { spawn } from 'node:child_process';
import { fileURLToPath, pathToFileURL } from 'node:url';
import path from 'node:path';
import fs from 'node:fs';

const require = createRequire(import.meta.url);
let chromium;
try { ({ chromium } = require('playwright')); }
catch { ({ chromium } = require(path.join(process.execPath, '../../lib/node_modules/playwright'))); }

const dir = path.dirname(fileURLToPath(import.meta.url));
const args = process.argv.slice(2);
const stills = args.includes('--stills');
const out = path.resolve(args.find(a => !a.startsWith('--')) || path.join(dir, 'out/qamar-mushaf-reel.mp4'));
fs.mkdirSync(path.dirname(out), { recursive: true });

const browser = await chromium.launch({ args: ['--allow-file-access-from-files'] });
const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
await page.goto(pathToFileURL(path.join(dir, 'index.html')).href);
await page.evaluate(() => window.ready);
const { fps, duration } = await page.evaluate(() => ({ fps: CONFIG.fps, duration: CONFIG.duration }));

if (stills) {
  // контрольные кадры для быстрой проверки
  const stillsDir = path.join(path.dirname(out), 'stills');
  fs.mkdirSync(stillsDir, { recursive: true });
  for (let t = 0.5; t < duration; t += 1) {
    await page.evaluate(t => renderFrame(t), t);
    await page.screenshot({ path: path.join(stillsDir, `t${t.toFixed(1).padStart(4, '0')}.png`) });
  }
  console.log('stills →', stillsDir);
} else {
  const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(fps), '-i', '-',
    '-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=stereo', '-shortest',
    '-c:v', 'libx264', '-preset', 'slow', '-crf', '16', '-pix_fmt', 'yuv420p', '-profile:v', 'high',
    '-c:a', 'aac', '-b:a', '128k', '-movflags', '+faststart', out], { stdio: ['pipe', 'inherit', 'inherit'] });
  const total = Math.round(fps * duration);
  for (let f = 0; f < total; f++) {
    await page.evaluate(t => renderFrame(t), f / fps);
    const buf = await page.screenshot({ type: 'png' });
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    if (f % fps === 0) process.stdout.write(`\r${f}/${total}`);
  }
  ff.stdin.end();
  await new Promise((res, rej) => ff.on('close', c => c ? rej(new Error('ffmpeg ' + c)) : res()));
  console.log('\n→', out);
}
await browser.close();
