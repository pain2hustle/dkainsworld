// Browser QA for DKAINSWORLD candidate or live site.
// Usage: node qa_browser.mjs <baseUrl> <outDir>
import { createRequire } from 'node:module';
import fs from 'node:fs';
const require = createRequire('C:/Users/Servi/code/amh-hive/package.json');
const { chromium } = require('playwright');

const base = process.argv[2] || 'http://127.0.0.1:8766/';
const out = process.argv[3] || 'D:/AMH/DKAINSWORLD-PhotoUpdate/private/qa';
fs.mkdirSync(out, { recursive: true });
const MAPS = 'https://maps.app.goo.gl/Nu84KZXRDFjCbwpp7?g_st=ac';
const STORE = 'https://www.facebook.com/marketplace/profile/100005788064086/?ref=permalink&mibextid=dXMIcH';
const report = { base, widths: {}, failures: [] };
const fail = (w, msg) => report.failures.push(`${w}: ${msg}`);

const browser = await chromium.launch({ executablePath: process.env.QA_CHROME || undefined });
for (const [w, h] of [[320, 700], [390, 844], [1366, 900]]) {
  const ctx = await browser.newContext({ viewport: { width: w, height: h }, deviceScaleFactor: 1 });
  const page = await ctx.newPage();
  const consoleErrors = [];
  const bad = [];
  page.on('console', m => m.type() === 'error' && consoleErrors.push(m.text()));
  page.on('response', r => r.status() >= 400 && bad.push(`${r.status()} ${r.url()}`));
  await page.goto(base, { waitUntil: 'networkidle' });
  await page.mouse.wheel(0, 1); await page.waitForTimeout(150); await page.evaluate(() => scrollTo(0, 0));
  await page.waitForTimeout(9500);
  await page.screenshot({ path: `${out}/hero-${w}.png` });
  const r = {};
  r.overflow = await page.evaluate(() => document.documentElement.scrollWidth - innerWidth);
  if (r.overflow > 0) fail(w, `horizontal overflow ${r.overflow}px`);
  // hero controls clickable (not covered by fixed nav or scene)
  r.heroControls = await page.evaluate(() => [...document.querySelectorAll('.hero-actions a,.hero-actions button')].map(el => {
    const b = el.getBoundingClientRect(); const hit = document.elementFromPoint(b.left + b.width / 2, b.top + b.height / 2);
    return { text: el.textContent.trim(), visible: b.bottom <= innerHeight && b.top >= 0, clickable: !!hit && (hit === el || el.contains(hit)) };
  }));
  r.heroControls.forEach(c => (!c.clickable || !c.visible) && fail(w, `hero control not clickable/visible: ${c.text}`));
  // emblem + header logo not clipped
  r.emblem = await page.evaluate(() => {
    const hero = document.querySelector('.hero').getBoundingClientRect();
    const e = document.querySelector('.hero-scene-emblem').getBoundingClientRect();
    const logo = document.querySelector('.brand-art img'); const lb = logo.getBoundingClientRect(); const pb = logo.parentElement.getBoundingClientRect();
    const fx = document.querySelector('.hero-orbit-fx');
    return { inside: e.left >= hero.left - 1 && e.right <= hero.right + 1 && e.top >= hero.top - 1 && e.bottom <= hero.bottom + 1,
      emblemRect: [e.left, e.top, e.width, e.height].map(Math.round), logoInside: lb.left >= pb.left - 1 && lb.right <= pb.right + 1 && lb.top >= pb.top - 1 && lb.bottom <= pb.bottom + 1,
      logoSrc: logo.getAttribute('src'), videoTime: fx ? fx.currentTime : -1, videoPaused: fx ? fx.paused : null,
      blend: fx ? getComputedStyle(fx).mixBlendMode : null };
  });
  if (!r.emblem.inside) fail(w, 'emblem clipped by hero');
  if (!r.emblem.logoInside) fail(w, 'header logo clipped');
  if (r.emblem.videoTime !== -1) fail(w, 'effects video should be gone');
  // emblem must not cover copy
  r.copyOverlap = await page.evaluate(() => {
    const e = document.querySelector('.hero-scene-emblem').getBoundingClientRect();
    return [...document.querySelectorAll('.hero h1,.hero-description,.hero-actions')].some(n => {
      const b = n.getBoundingClientRect(); return !(b.right <= e.left || b.left >= e.right || b.bottom <= e.top || b.top >= e.bottom);
    });
  });
  if (r.copyOverlap) fail(w, 'emblem overlaps hero copy/buttons');
  // exact links
  r.links = await page.evaluate(([MAPS, STORE]) => ({
    tel: [...new Set([...document.querySelectorAll('a[href^="tel:"]')].map(a => a.getAttribute('href')))],
    maps: [...new Set([...document.querySelectorAll('a[href*="maps.app.goo.gl"]')].map(a => a.href))].every(x => x === MAPS),
    store: [...document.querySelectorAll('.fb-store-link')].map(a => a.href === STORE).length,
    storeExact: [...document.querySelectorAll('.fb-store-link')].every(a => a.href === STORE),
    pay: [...document.querySelectorAll('.payment-link')].map(a => a.dataset.copy || a.href),
    bottomNav: [...document.querySelectorAll('.bottom-nav span')].map(s => s.textContent.trim())
  }), [MAPS, STORE]);
  if (r.links.tel.join() !== 'tel:+15104350747' || !r.links.maps || !r.links.storeExact || r.links.store < 4) fail(w, 'link mismatch ' + JSON.stringify(r.links));
  // menu: open, Escape, focus restore
  await page.click('#menu-open');
  r.menuOpen = await page.evaluate(() => document.querySelector('#site-menu').open);
  await page.keyboard.press('Escape');
  r.menuClosedFocus = await page.evaluate(() => !document.querySelector('#site-menu').open && document.activeElement.id === 'menu-open');
  if (!r.menuOpen || !r.menuClosedFocus) fail(w, 'menu open/escape/focus');
  // QR from hero
  const qrBtn = page.locator('.hero-actions [data-qr]');
  await qrBtn.click();
  r.qrOpen = await page.evaluate(() => document.querySelector('#qr-dialog').open);
  await page.keyboard.press('Escape');
  r.qrFocus = await page.evaluate(() => !document.querySelector('#qr-dialog').open && document.activeElement.matches('.hero-actions [data-qr]'));
  if (!r.qrOpen || !r.qrFocus) fail(w, 'QR open/escape/focus');
  // filters + search
  await page.click('[data-filter="backpacks"]');
  r.backpacks = await page.locator('.item-card:not([hidden])').count();
  await page.click('[data-filter="all"]');
  await page.fill('#search', 'pipe');
  await page.waitForTimeout(200);
  r.searchPipe = await page.locator('.item-card:not([hidden])').count();
  await page.fill('#search', '');
  await page.waitForTimeout(200);
  r.all = await page.locator('.item-card:not([hidden])').count();
  if (r.backpacks !== 2 || r.searchPipe < 1 || r.all !== 20) fail(w, `filters ${r.backpacks}/${r.searchPipe}/${r.all}`);
  // every card has a photo; 3 Facebook listings link out; price list covers every item
  r.cards = await page.evaluate(() => ({
    total: document.querySelectorAll('.item-card').length,
    withPhoto: document.querySelectorAll('.item-card .item-photo img').length,
    examples: document.querySelectorAll('.item-card .photo-example').length, credits: document.querySelectorAll('.photo-credits li').length,
    fb: [...document.querySelectorAll('.card-fb-link')].map(a => a.href),
    priceRows: document.querySelectorAll('#price-list .pl-panel > ul > li').length,
    priceTargets: [...document.querySelectorAll('#price-list .pl-panel > ul > li > a')].every(a => document.querySelector(a.getAttribute('href')))
  }));
  const FB = ['1103700079241670', '2106563970226121', '28444710648484140'];
  if (r.cards.total !== 20 || r.cards.withPhoto !== 20 || r.cards.examples !== 0 || r.cards.priceRows !== 20 || !r.cards.priceTargets
    || r.cards.fb.length !== 3 || !FB.every(id => r.cards.fb.includes(`https://www.facebook.com/marketplace/item/${id}/`))) fail(w, 'cards ' + JSON.stringify(r.cards));
  // galleries for the four new-photo listings
  r.galleries = {};
  for (const [id, n] of [['pipe-wrenches', 3], ['pick-your-tools', 3], ['dbz-orange-yellow', 3], ['kid-goku', 2]]) {
    const btn = page.locator(`.item-photo[data-gallery="${id}"]`);
    await btn.scrollIntoViewIfNeeded();
    const thumbOk = await btn.locator('img').evaluate(i => i.complete && i.naturalWidth > 0);
    await btn.click();
    await page.waitForTimeout(250);
    const first = await page.textContent('#photo-count');
    await page.click('#photo-next');
    await page.waitForTimeout(150);
    const second = await page.textContent('#photo-count');
    const imgOk = await page.evaluate(() => { const i = document.querySelector('#gallery-image'); return i.complete && i.naturalWidth > 0; });
    if (id === 'pipe-wrenches') await page.screenshot({ path: `${out}/gallery-${w}.png` });
    await page.keyboard.press('Escape');
    const focusBack = await btn.evaluate(b => document.activeElement === b);
    r.galleries[id] = { thumbOk, first, second, imgOk, focusBack };
    if (!thumbOk || first.trim() !== `1 of ${n}` || second.trim() !== `2 of ${n}` || !imgOk || !focusBack) fail(w, `gallery ${id} ${JSON.stringify(r.galleries[id])}`);
  }
  // all images load after full scroll
  await page.evaluate(async () => { for (let y = 0; y < document.body.scrollHeight; y += 500) { scrollTo(0, y); await new Promise(r => setTimeout(r, 60)); } });
  await page.evaluate(async () => { for (const i of document.images) { if (i.complete && i.naturalWidth) continue; i.scrollIntoView({ block: 'center' }); for (let k = 0; k < 40 && !(i.complete && i.naturalWidth); k++) await new Promise(r => setTimeout(r, 100)); } });
  r.brokenImages = await page.evaluate(() => [...document.images].filter(i => !(i.complete && i.naturalWidth > 0)).map(i => i.getAttribute('src')));
  if (r.brokenImages.length) fail(w, 'broken images ' + r.brokenImages);
  // fixed nav must not hide footer end
  await page.evaluate(() => { document.documentElement.style.scrollBehavior = 'auto'; scrollTo(0, document.body.scrollHeight); });
  await page.waitForTimeout(600);
  r.footerClear = await page.evaluate(() => { const nav = document.querySelector('.bottom-nav'); const last = document.querySelector('.site-footer').lastElementChild.getBoundingClientRect(); const n = nav ? nav.getBoundingClientRect() : { top: innerHeight }; return getComputedStyle(nav).display === 'none' || last.bottom <= n.top + 1; });
  if (!r.footerClear) fail(w, 'fixed bottom nav covers footer end');
  await page.screenshot({ path: `${out}/full-${w}.png`, fullPage: true });
  r.consoleErrors = consoleErrors; r.http4xx = bad;
  if (consoleErrors.length) fail(w, 'console errors ' + consoleErrors.join(' | '));
  if (bad.length) fail(w, 'HTTP errors ' + bad.join(' | '));
  report.widths[w] = r;
  await ctx.close();
}
// reduced motion
const rm = await browser.newContext({ viewport: { width: 390, height: 844 }, reducedMotion: 'reduce' });
const p2 = await rm.newPage();
await p2.goto(base, { waitUntil: 'networkidle' });
report.reducedMotion = await p2.evaluate(() => ({
  video: document.querySelector('.hero-orbit-fx') ? 'present' : 'none',
  emblemAnim: getComputedStyle(document.querySelector('.hero-scene-emblem')).animationName,
  star: getComputedStyle(document.querySelector('.tiny-star')).animationName }));
if (report.reducedMotion.video !== 'none' || report.reducedMotion.emblemAnim !== 'none' || report.reducedMotion.star !== 'none') report.failures.push('reduced motion not honored');
await rm.close();
await browser.close();
report.passed = report.failures.length === 0;
fs.writeFileSync(`${out}/report.json`, JSON.stringify(report, null, 2));
console.log(JSON.stringify({ passed: report.passed, failures: report.failures }, null, 1));
