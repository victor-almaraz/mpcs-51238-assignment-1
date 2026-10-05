/* The magazines on the shelf: choosing one, and turning its pages. After the cover, each
   leaf is an article whose text flows in columns; a spread shows two pages (one, when the
   window is narrow), each of one column or, in a newspaper (data-cols="2"), two, and turning
   the page moves the columns on by a spread. So an article takes as many spreads as its text
   needs at the window's size, and the folio counts pages as they fall. The index buttons open
   a leaf at its first spread; the arrow keys turn the pages; tabbing to something on another
   spread turns to it. The rack above the magazines shows one at a time, and the one last
   opened stands in front of the others on the shelf. Deck buttons
   (data-deck) belong to the desk. Without the script, every leaf stands in one scroll. */
(function () {
  'use strict';
  var doc = document, mags = Array.prototype.slice.call(doc.querySelectorAll('.st-mag .mag'));
  if (!mags.length) return;

  function setup(mag) {
    var leaves = Array.prototype.slice.call(mag.querySelectorAll('.mag-leaf'));
    var dots = Array.prototype.slice.call(mag.querySelectorAll('.mag-index [data-goto]'));
    var prev = mag.querySelector('[data-turn="-1"]'), next = mag.querySelector('[data-turn="1"]');
    var folio = mag.querySelector('.mag-folio');
    var cpp = Number(mag.getAttribute('data-cols')) || 1;     // columns to a page
    var at = 0, spread = 0;
    mag.classList.add('mag-js');

    function flowOf(leaf) { return leaf.querySelector('.mag-flow'); }
    function headingOf(i) { return leaves[i].querySelector('.mag-h'); }

    // lay a leaf's columns out at its present width, and count its spreads
    function layout(leaf) {
      var flow = flowOf(leaf);
      if (!flow) { leaf.spreads = 1; leaf.pages = 1; return; }
      var wasHidden = leaf.hidden;
      if (wasHidden) { leaf.style.visibility = 'hidden'; leaf.hidden = false; }
      var w = leaf.clientWidth, pad = parseFloat(getComputedStyle(flow).paddingLeft) || 0;
      if (w >= 100) {                                           // (zero while the station is out of sight)
        var pages = w >= 760 ? 2 : 1, per = pages * cpp, pitch = w / per;   // a column and its gap
        leaf.classList.toggle('one', pages === 1);
        flow.style.setProperty('--colw', (pitch - 2 * pad - 1) + 'px');    // a hair under, so the columns are never one too few
        flow.style.transform = 'none';
        // the last thing in the flow says how many columns it runs to
        var last = flow.lastElementChild, cols = 1;
        if (last) cols = Math.floor((last.getBoundingClientRect().right - flow.getBoundingClientRect().left - 1 - pad) / pitch) + 1;
        leaf.pages = pages; leaf.step = w;
        leaf.spreads = Math.max(1, Math.ceil(cols / per));
      }
      leaf.spreads = leaf.spreads || 1; leaf.pages = leaf.pages || 1;
      if (wasHidden) { leaf.hidden = true; leaf.style.visibility = ''; }
    }
    function layoutAll() { leaves.forEach(layout); }

    // the pages before a leaf: the cover is one, every spread two (one when narrow)
    function pagesBefore(i) { var n = 0; for (var k = 0; k < i; k++) n += k === 0 ? 1 : leaves[k].spreads * leaves[k].pages; return n; }
    function total() { return pagesBefore(leaves.length); }

    function show(i, s, focus) {
      i = Math.max(0, Math.min(leaves.length - 1, i));
      var leaf = leaves[i];
      s = Math.max(0, Math.min((leaf.spreads || 1) - 1, s));
      var had = doc.activeElement, lost = had && leaves[at].contains(had) && i !== at;
      at = i; spread = s;
      leaves.forEach(function (l, k) { l.hidden = k !== at; });
      var flow = flowOf(leaf);
      if (flow) flow.style.transform = 'translateX(' + (-spread * leaf.step) + 'px)';
      dots.forEach(function (b, k) { if (k === at) b.setAttribute('aria-current', 'page'); else b.removeAttribute('aria-current'); });
      prev.disabled = at === 0 && spread === 0;
      next.disabled = at === leaves.length - 1 && spread === leaf.spreads - 1;
      var first = pagesBefore(at) + 1 + spread * leaf.pages, last = at === 0 ? first : first + leaf.pages - 1;
      folio.textContent = (last > first ? 'Pages ' + first + '–' + last : 'Page ' + first) + ' of ' + total();
      mag.setAttribute('data-at', String(at));
      if (focus || lost) headingOf(at).focus({ preventScroll: true });
    }
    function turn(d) {
      var leaf = leaves[at];
      if (d > 0) { if (spread < leaf.spreads - 1) show(at, spread + 1); else if (at < leaves.length - 1) show(at + 1, 0, true); }
      else { if (spread > 0) show(at, spread - 1); else if (at > 0) show(at - 1, leaves[at - 1].spreads - 1, true); }
    }

    Array.prototype.forEach.call(mag.querySelectorAll('[data-goto]'), function (b) {
      b.addEventListener('click', function () { show(Number(b.getAttribute('data-goto')), 0, true); });
    });
    [prev, next].forEach(function (b) {
      b.addEventListener('click', function () {
        turn(Number(b.getAttribute('data-turn')));
        // at either end the pressed button is disabled; keep focus on the other one
        if (b.disabled) (b === prev ? next : prev).focus();
      });
    });
    mag.addEventListener('keydown', function (e) {
      if (e.key !== 'ArrowLeft' && e.key !== 'ArrowRight') return;
      if (e.altKey || e.ctrlKey || e.metaKey || e.shiftKey) return;
      if (e.target.matches('input, select, textarea, [contenteditable]')) return;
      e.preventDefault();
      turn(e.key === 'ArrowLeft' ? -1 : 1);
    });
    // something reached by Tab on another spread brings its spread round
    mag.addEventListener('focusin', function (e) {
      var leaf = leaves[at], flow = flowOf(leaf);
      if (!flow || !flow.contains(e.target) || e.target === headingOf(at)) return;
      var s = Math.floor((e.target.getBoundingClientRect().left - flow.getBoundingClientRect().left) / leaf.step);
      if (s !== spread) show(at, s);
      leaf.scrollLeft = 0;     // the browser may have scrolled the spread to bring it into view
    });

    var pending = null;
    function relayout() {
      clearTimeout(pending);
      pending = setTimeout(function () { if (!mag.hidden) { layoutAll(); show(at, spread); } }, 60);
    }
    if (window.ResizeObserver) new ResizeObserver(relayout).observe(mag);
    if (doc.fonts && doc.fonts.ready) doc.fonts.ready.then(relayout);
    layoutAll();
    show(0, 0, false);
    return {
      el: mag,
      shown: function () { layoutAll(); show(at, spread); },
      focus: function () { headingOf(at).focus({ preventScroll: true }); },
      at: function () { return at; }
    };
  }
  var issues = mags.map(setup);

  /* ---------------- the rack: which magazine is open ---------------- */
  var rack = Array.prototype.slice.call(doc.querySelectorAll('.mag-rack [data-issue]')), open = issues[0];
  function choose(key, focus) {
    issues.forEach(function (m) { m.el.hidden = m.el.getAttribute('data-issue') !== key; if (!m.el.hidden) open = m; });
    rack.forEach(function (b) { b.setAttribute('aria-pressed', String(b.getAttribute('data-issue') === key)); });
    open.shown();
    if (focus) open.focus();
    // on the shelf, the issue last opened stands in front of the others
    var img = doc.querySelector('.o-mag .mini-mag img'), n = key === 'moire' ? 'px-cover' : 'px-cover-' + key;
    if (img) { img.setAttribute('data-px', n); img.src = img.src.replace(/px-cover[\w-]*\.png/, n + '.png'); }
  }
  rack.forEach(function (b) { b.addEventListener('click', function () { choose(b.getAttribute('data-issue'), true); }); });

  if (window.Desk && Desk.onShow) {
    Desk.onShow('magazine', function () {
      open.shown();
      // the desk focuses the first title in the station; the open magazine's own heading instead
      setTimeout(function () { if (!open.el.contains(doc.activeElement)) open.focus(); }, 0);
    });
  }
})();
