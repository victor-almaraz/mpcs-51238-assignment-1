/* The magazine on the desk: turning its pages, and printing its plates through Halftone.
   Only the opening on view is printed, and only while the magazine station is shown;
   each canvas is printed again only when its size changes. The desk's thumbnail of the
   cover is printed when it first has a size. Deck buttons (data-deck) belong to the desk. */
(function () {
  'use strict';
  var H = window.Halftone;
  var mag = document.getElementById('mag');
  var thumb = document.getElementById('mag-thumb');
  if (!H) return;

  /* ---------------- the thumbnail on the desk ---------------- */
  function paintThumb() {
    if (!thumb) return;
    var box = thumb.parentNode, w = box.clientWidth, h = box.clientHeight;
    if (!w || !h) return;
    if (H.fresh(thumb, w + 'x' + h)) H.coverThumb(thumb, w, h);
  }
  if (thumb && window.ResizeObserver) new ResizeObserver(paintThumb).observe(thumb.parentNode);

  if (!mag) { H.whenFonts(['italic 400 100px "Playfair Display"'], paintThumb); return; }

  /* ---------------- pages ---------------- */
  var leaves = Array.prototype.slice.call(mag.querySelectorAll('.mag-leaf'));
  var dots = Array.prototype.slice.call(mag.querySelectorAll('.mag-index [data-goto]'));
  var prev = mag.querySelector('[data-turn="-1"]'), next = mag.querySelector('[data-turn="1"]');
  var folio = mag.querySelector('.mag-folio');
  var at = 0;
  mag.classList.add('mag-js');

  function headingOf(i) { return leaves[i].querySelector('.mag-h'); }
  function visible() { return mag.getClientRects().length > 0 && mag.clientWidth > 0; }

  function show(i, focus) {
    i = Math.max(0, Math.min(leaves.length - 1, i));
    var had = document.activeElement, lost = had && leaves[at].contains(had) && i !== at;
    at = i;
    leaves.forEach(function (leaf, k) { leaf.hidden = k !== at; });
    dots.forEach(function (b, k) { if (k === at) b.setAttribute('aria-current', 'page'); else b.removeAttribute('aria-current'); });
    prev.disabled = at === 0;
    next.disabled = at === leaves.length - 1;
    folio.textContent = 'Page ' + (at + 1) + ' of ' + leaves.length;
    mag.setAttribute('data-at', String(at));
    Array.prototype.forEach.call(leaves[at].querySelectorAll('.mag-page'), function (p) { p.scrollTop = 0; });
    leaves[at].scrollTop = 0;
    paint();
    // focus follows the page when asked, or when it would otherwise be lost with the old page
    if (focus || lost) headingOf(at).focus({ preventScroll: true });
  }

  Array.prototype.forEach.call(mag.querySelectorAll('[data-goto]'), function (b) {
    b.addEventListener('click', function () { show(Number(b.getAttribute('data-goto')), true); });
  });
  [prev, next].forEach(function (b) {
    b.addEventListener('click', function () {
      show(at + Number(b.getAttribute('data-turn')), false);
      // at either end the pressed button is disabled; keep focus on the other one
      if (b.disabled) (b === prev ? next : prev).focus();
    });
  });
  mag.addEventListener('keydown', function (e) {
    if (e.key !== 'ArrowLeft' && e.key !== 'ArrowRight') return;
    if (e.altKey || e.ctrlKey || e.metaKey || e.shiftKey) return;
    if (e.target.matches('input, select, textarea, [contenteditable]')) return;
    var to = at + (e.key === 'ArrowLeft' ? -1 : 1);
    if (to < 0 || to >= leaves.length) return;
    e.preventDefault();
    // from the bar's buttons focus stays put; from anywhere in the pages it moves to the heading
    show(to, !e.target.closest('.mag-turn'));
  });

  /* ---------------- printing ---------------- */
  function sizeOf(el) { return { w: Math.floor(el.clientWidth), h: Math.floor(el.clientHeight) }; }

  function paintCover(leaf, canvas) {
    var page = canvas.parentNode, s = sizeOf(page);
    if (!s.w || !s.h) return;
    var top = page.querySelector('.mag-cover-top'), big = page.querySelector('.mag-big');
    var fs = parseFloat(getComputedStyle(big).fontSize);
    if (!H.fresh(canvas, [s.w, s.h, top.offsetHeight, fs].join('|'))) return;
    var o = page.getBoundingClientRect();
    var runs = H.ready ? H.runsOf(big, { left: o.left + page.clientLeft, top: o.top + page.clientTop }) : null;
    var r = H.cover(canvas, s.w, s.h, { split: top.offsetHeight, runs: runs, fontSize: fs });
    canvas.dataset.contrast = r.contrast ? r.contrast.toFixed(2) : '';
    big.classList.toggle('ht-on', r.letters === 'knockout');
  }

  function paintLeaf() {
    var leaf = leaves[at], ink = leaf.getAttribute('data-ink') || 'm', t0 = performance.now();
    Array.prototype.forEach.call(leaf.querySelectorAll('canvas.mag-plate'), function (c) {
      var kind = c.getAttribute('data-plate');
      if (kind === 'cover') { paintCover(leaf, c); return; }
      var s = sizeOf(c.parentNode);
      if (!s.w || !s.h || !H.fresh(c, s.w + 'x' + s.h)) return;
      if (kind === 'shot') H.shot(c, s.w, s.h, { ink: ink, op: Number(c.getAttribute('data-op')), numeral: c.getAttribute('data-num'), seed: 40 + at });
      else if (kind === 'wash') H.wash(c, s.w, s.h, { a: 'y', b: 'c', seed: 17 + at });
    });
    Array.prototype.forEach.call(leaf.querySelectorAll('.mag-screen'), function (el) {
      var page = el.closest('.mag-page');
      H.heading(el, ink, { maxRight: page.getBoundingClientRect().right });
    });
    mag.dataset.htMs = Math.round(performance.now() - t0);
  }

  var queued = false;
  function paint() {
    if (!visible()) return;
    paintLeaf();
  }
  function paintSoon() {
    if (queued) return;
    queued = true;
    requestAnimationFrame(function () { queued = false; paint(); });
  }

  if (window.ResizeObserver) {
    var last = '';
    new ResizeObserver(function () {
      var s = mag.clientWidth + 'x' + mag.clientHeight;
      if (s === last || !mag.clientWidth) return;
      last = s;
      paintSoon();
    }).observe(mag);
  } else {
    window.addEventListener('resize', paintSoon);
  }

  if (window.Desk && Desk.onShow) {
    Desk.onShow('magazine', function () {
      paint();
      // the desk focuses the cover's title; opened at another page, focus that page's heading
      setTimeout(function () {
        if (at !== 0 && !mag.contains(document.activeElement)) headingOf(at).focus({ preventScroll: true });
      }, 0);
    });
  }

  show(0, false);
  H.whenFonts(['italic 400 100px "Playfair Display"', '400 17px "Jost"'], function () { paintThumb(); paint(); });
})();
