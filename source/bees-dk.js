// Bee facts box (copied from Austin's poem page): rotates every 8 s, pauses while held/hovered or list open,
// tap the fact or "All facts" to open the full list. Menu mini-box mirrors the current fact and jumps to the box.
(function () {
  var bf = document.getElementById('bfact'), bl = document.getElementById('blist'), ba = document.getElementById('ball'), mini = document.getElementById('bmini');
  if (!bf || !bl) return;
  var fs = [].slice.call(bl.querySelectorAll('li')), cur = 0, held = false;
  function show(i) { cur = i; var li = fs[i]; bf.classList.add('fade'); setTimeout(function () { bf.innerHTML = li.innerHTML; bf.querySelectorAll('a').forEach(function (a) { a.remove() }); var num = document.createElement('small'); num.className = 'bnum'; num.textContent = 'Fact ' + (i + 1) + ' of ' + fs.length; bf.prepend(num); bf.classList.remove('fade'); if (mini) { var t = li.querySelector('b'), sp = li.querySelector('span'); var box = mini.querySelector('.bmini-fact'); box.innerHTML = ''; var bb = document.createElement('b'); bb.textContent = t ? t.textContent.trim() : 'Fact ' + (i + 1); var ss = document.createElement('span'); ss.textContent = sp ? sp.textContent.trim() : li.textContent.trim(); box.append(bb, ss); } }, 350) }
  function pick() { if (fs.length < 2) return 0; var i; do { i = Math.floor(Math.random() * fs.length) } while (i === cur); return i }
  if (fs.length) { var first = pick(); show(first); }
  var reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  setInterval(function () { if (!bl.hidden || document.hidden || reduce || held) return; show(pick()) }, 8000);
  ['pointerenter', 'pointerdown', 'focusin'].forEach(function (e) { bf.addEventListener(e, function () { held = true }) });
  ['pointerleave', 'focusout'].forEach(function (e) { bf.addEventListener(e, function () { held = false }) });
  function toggle() { var o = bl.hidden; bl.hidden = !o; ba.setAttribute('aria-expanded', String(o)); bf.setAttribute('aria-expanded', String(o)); ba.textContent = o ? 'Hide list' : 'All facts'; if (o) { var li = fs[cur]; li && bl.scrollTo && bl.scrollTo({ top: li.offsetTop - bl.offsetTop, behavior: 'smooth' }) } }
  bf.addEventListener('click', toggle); ba.addEventListener('click', toggle);
  var hist = [cur], hi = 0;
  var _show = show; show = function (i) { if (hist[hi] !== i) { hist = hist.slice(0, hi + 1); hist.push(i); hi = hist.length - 1; } _show(i); };
  var nx = document.getElementById('bnext'), pv = document.getElementById('bprev');
  if (nx) nx.addEventListener('click', function () { if (hi < hist.length - 1) { hi++; _show(hist[hi]); } else show(pick()); });
  if (pv) pv.addEventListener('click', function () { if (hi > 0) { hi--; _show(hist[hi]); } });
  if (mini) mini.addEventListener('click', function () { var m = document.getElementById('site-menu'); if (m && m.open) m.close(); document.getElementById('bees').scrollIntoView({ behavior: 'smooth', block: 'center' }) });
})();
