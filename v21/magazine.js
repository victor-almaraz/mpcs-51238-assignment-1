/* The magazine on the shelf: turning its pages. Its plates are SVG files (assets/mag/),
   flat process inks overprinting, Ben-Day screens and outlined numerals, so nothing is
   printed here. Deck buttons (data-deck) belong to the desk. */
(function () {
  'use strict';
  var mag = document.getElementById('mag');
  if (!mag) return;

  /* ---------------- pages ---------------- */
  var leaves = Array.prototype.slice.call(mag.querySelectorAll('.mag-leaf'));
  var dots = Array.prototype.slice.call(mag.querySelectorAll('.mag-index [data-goto]'));
  var prev = mag.querySelector('[data-turn="-1"]'), next = mag.querySelector('[data-turn="1"]');
  var folio = mag.querySelector('.mag-folio');
  var at = 0;
  mag.classList.add('mag-js');   // pages that turn; without the script they scroll

  function headingOf(i) { return leaves[i].querySelector('.mag-h'); }

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

  if (window.Desk && Desk.onShow) {
    Desk.onShow('magazine', function () {
      // the desk focuses the cover's title; opened at another page, focus that page's heading
      setTimeout(function () {
        if (at !== 0 && !mag.contains(document.activeElement)) headingOf(at).focus({ preventScroll: true });
      }, 0);
    });
  }

  show(0, false);
})();
