// DKAINSWORLD easter egg (owner's clip): 3 s after load a card pops up and plays the punch, then shows
// "Made in the happiest city in the United States · Fremont, CA" and fades away. Never blocks taps.
// Only when the header logo is tapped: plays, holds the last frame, text slides up, waits for the next touch/scroll. Reduced motion skips.
(function () {
  const calm = matchMedia('(prefers-reduced-motion: reduce)');
  function punch() {
    if (calm.matches || document.querySelector('.punch-egg')) return;
    const box = document.createElement('div'); box.className = 'punch-egg'; box.setAttribute('aria-hidden', 'true');
    box.innerHTML = '<div class="punch-card"><video muted playsinline preload="auto" disablepictureinpicture><source src="/assets/punch.mp4?v=5296c9c1" type="video/mp4"></video>' +
      '<div class="punch-made"><p>Made in the happiest city in the United States</p><strong>Fremont, CA</strong></div></div>';
    document.body.append(box);
    const v = box.querySelector('video');
    // hold on the last frame, short pause, then the text slides up; stays until the visitor touches/scrolls
    const done = () => { if (box.classList.contains('made')) return; v.pause(); setTimeout(() => box.classList.add('made'), 450); };
    v.addEventListener('ended', done, { once: true });
    v.addEventListener('error', () => box.remove(), { once: true });
    requestAnimationFrame(() => box.classList.add('in'));
    v.play().catch(() => box.remove());
    setTimeout(done, 9000);
    const born = performance.now(), evs = ['pointerdown', 'touchstart', 'touchmove', 'wheel', 'scroll', 'keydown'];
    const end = () => { if (performance.now() - born < 350) return; evs.forEach(e => removeEventListener(e, end, true)); box.classList.add('out'); setTimeout(() => box.remove(), 350); };
    evs.forEach(e => addEventListener(e, end, { capture: true, passive: true }));
  }
  window.dkainsPunch = punch;
  const logo = document.querySelector('.site-header .brand');
  if (logo) logo.addEventListener('click', (e) => { e.preventDefault(); setTimeout(punch, 0); });
})();
