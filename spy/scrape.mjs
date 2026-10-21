import { createRequire } from 'module';
const require = createRequire(import.meta.url);
const { chromium } = require('playwright');
import fs from 'fs';
const [,, kw, max, out] = process.argv;
const url = 'https://www.facebook.com/ads/library/?active_status=active&ad_type=all&country=FR&is_targeted_country=false&media_type=all&q=' + encodeURIComponent(kw) + '&search_type=keyword_unordered&sort_data[direction]=desc&sort_data[mode]=total_impressions';
const browser = await chromium.launch({ headless: true });
const ctx = await browser.newContext({ locale: 'fr-FR', userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36', viewport: { width: 1280, height: 900 } });
const page = await ctx.newPage();
const ads = new Map();
function harvest(obj) {
  if (!obj || typeof obj !== 'object') return;
  if (obj.ad_archive_id && obj.snapshot) { ads.set(obj.ad_archive_id, obj); return; }
  for (const v of Object.values(obj)) harvest(v);
}
page.on('response', async r => {
  const u = r.url();
  if (!u.includes('/api/graphql') && !u.includes('/ads/library')) return;
  try {
    const t = await r.text();
    for (const line of t.split('\n')) { const s = line.trim(); if (s.startsWith('{')) { try { harvest(JSON.parse(s)); } catch {} } }
    // inline JSON in HTML
    if (u.includes('/ads/library')) for (const m of t.matchAll(/<script type="application\/json"[^>]*>(.*?)<\/script>/gs)) { try { harvest(JSON.parse(m[1])); } catch {} }
  } catch {}
});
await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 });
await page.waitForTimeout(6000);
let last = -1, stale = 0;
while (ads.size < +max && stale < 6) {
  await page.mouse.wheel(0, 6000);
  await page.waitForTimeout(1800);
  if (ads.size === last) stale++; else { stale = 0; last = ads.size; }
}
fs.writeFileSync(out, JSON.stringify([...ads.values()]));
console.log(kw, ads.size);
await browser.close();
