// Renders grape-animation.html to a PNG frame sequence with headless Chromium.
// Usage: node render.mjs [outDir] [size] [fps] [bg]
import { chromium } from "playwright";
import { mkdirSync, rmSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const here = dirname(fileURLToPath(import.meta.url));
const outDir = process.argv[2] || join(here, "frames");
const size = Number(process.argv[3] || 800);
const fps = Number(process.argv[4] || 30);
const bg = process.argv[5] || "white";

rmSync(outDir, { recursive: true, force: true });
mkdirSync(outDir, { recursive: true });

const browser = await chromium.launch({ args: ["--force-color-profile=srgb", "--disable-lcd-text"] });
const page = await browser.newPage({ viewport: { width: size, height: size }, deviceScaleFactor: 1 });
await page.goto(`file://${join(here, "grape-animation.html")}?frame=0&bg=${bg}`);
await page.waitForFunction(() => !!window.grapeAnim);

const duration = await page.evaluate(() => window.grapeAnim.duration);
const total = Math.round(duration * fps);
for (let i = 0; i < total; i++) {
  await page.evaluate((t) => window.grapeAnim.setTime(t), i / fps);
  await page.screenshot({ path: join(outDir, `f_${String(i).padStart(4, "0")}.png`), omitBackground: bg === "none" });
}
await browser.close();
console.log(`rendered ${total} frames at ${fps}fps into ${outDir}`);
