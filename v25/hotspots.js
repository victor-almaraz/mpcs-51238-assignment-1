/* The room as a point-and-click scene. Everything that can be taken up is a hotspot: under
   the pointer (or with the keyboard's focus) it is outlined in white, one art pixel wide,
   and a caption beside the cursor says what pressing it does ("Use the computer"). The
   arrow keys move from hotspot to hotspot, to the nearest in that direction, and Enter
   takes it up; H outlines every hotspot for a moment, to show what the room holds. A hotspot's
   data-say, if it has one, is its caption.
   Needs Desk (desk.js). */

(function () {
  'use strict';
  var doc = document, scene = doc.querySelector('.overview');
  if (!scene) return;
  var LIST = window.matchMedia('(max-width: 1011px), (max-height: 505px)');
  var SAY = { v1: 'Read volume 1: FORTRAN', v2: 'Read volume 2: Sieves', v3: 'Read volume 3: Music and tape',
    'o-mag': 'Read the magazines', 'o-folio': 'Look through the miscellanea', 'o-box': 'Open the deck box',
    'o-form': 'Pick up the coding form', 'o-out': 'Look in the out tray', 'o-computer': 'Use the computer', 'o-tape': 'Use the tape player',
    'o-reader': 'Look at the card reader and printer', 'o-upic': 'Draw on the UPIC', 'o-console': 'Play the pocket game', 'o-timer': 'Set the tomato timer', 'o-album': 'Look through the photo album',
    'print-wide': 'Change the print', 'print-narrow': 'Change the print', 'print-shelf': 'Change the print', 'floor-l': 'Change the plant',
    'floor-r': 'Change the plant', 'desk-plant': 'Change the plant', lamp: 'Change the lamp', mug: 'Change the mug', 'print-tank': 'Change the print', chair: 'Change the chair' };
  var spots = Array.prototype.slice.call(scene.querySelectorAll('.obj, .swap'));
  function sayOf(b) { if (b.hasAttribute('data-say')) return b.getAttribute('data-say'); if (b.classList.contains('lamp-switch')) return Decor.lampOn() ? 'Turn the lamp off' : 'Turn the lamp on'; var sw = b.getAttribute('data-swap'); if (sw) return SAY[sw]; for (var k in SAY) if (b.classList.contains(k)) return SAY[k]; return b.getAttribute('aria-label') || b.textContent.trim(); }
  var hint = doc.createElement('div');
  hint.className = 'hint'; hint.setAttribute('aria-hidden', 'true'); hint.hidden = true;
  doc.body.appendChild(hint);
  function show(b, x, y) {
    hint.textContent = typeof b === 'string' ? b : sayOf(b); hint.hidden = false;
    var w = hint.offsetWidth, h = hint.offsetHeight;
    hint.style.left = Math.max(4, Math.min(innerWidth - w - 4, x)) + 'px';
    hint.style.top = Math.max(4, Math.min(innerHeight - h - 4, y)) + 'px';
  }
  function hide() { hint.hidden = true; }
  spots.forEach(function (b) {
    b.addEventListener('pointermove', function (e) { if (!LIST.matches) show(b, e.clientX + 18, e.clientY + 22); });
    b.addEventListener('pointerleave', hide);
    b.addEventListener('focus', function () {
      if (LIST.matches || !b.matches(':focus-visible')) return;
      var r = b.getBoundingClientRect();
      show(b, r.left + r.width / 2 - 60, r.top - 34);
    });
    b.addEventListener('blur', hide);
    b.addEventListener('click', function () { if (b.classList.contains('lamp-switch') && !hint.hidden) hint.textContent = sayOf(b); else hide(); });
  });
  // the bare wall: its caption, and the hand, say it can be changed
  scene.addEventListener('pointermove', function (e) {
    if (LIST.matches || spots.some(function (b) { return b.contains(e.target); })) return;
    var on = window.Decor && Decor.wallAt(e);
    scene.classList.toggle('on-wall', !!on);
    if (on) show('Change the wallpaper', e.clientX + 18, e.clientY + 22);
    else hide();
  });
  scene.addEventListener('pointerleave', function () { scene.classList.remove('on-wall'); hide(); });
  scene.addEventListener('click', function (e) { if (scene.classList.contains('on-wall')) hide(); });

  // the arrow keys: from the focused hotspot (or none) to the nearest in that direction on the
  // wall in front, weighing distance across the direction twice as much as distance along it
  function centre(b) { var r = b.getBoundingClientRect(); return [r.left + r.width / 2, r.top + r.height / 2]; }
  var DIRS = { ArrowLeft: [-1, 0], ArrowRight: [1, 0], ArrowUp: [0, -1], ArrowDown: [0, 1] };
  doc.addEventListener('keydown', function (e) {
    if (LIST.matches || Desk.current() !== 'desk' || e.altKey || e.ctrlKey || e.metaKey) return;
    var t = doc.activeElement;
    if (t && /^(INPUT|TEXTAREA|SELECT)$/.test(t.tagName)) return;
    if (e.key === 'h' || e.key === 'H') {
      scene.classList.add('reveal');
      setTimeout(function () { scene.classList.remove('reveal'); }, 1600);
      return;
    }
    var d = DIRS[e.key];
    if (!d) return;
    e.preventDefault();
    var station = scene.closest('.station').getBoundingClientRect();
    var near = spots.filter(function (b) { var c = centre(b); return c[0] >= station.left && c[0] <= station.right; });
    var from = spots.indexOf(t) >= 0 ? t : null, best = null, bs = Infinity;
    if (!from) { (near[0] || spots[0]).focus(); return; }
    var c = centre(from);
    near.forEach(function (b) {
      if (b === from) return;
      var p = centre(b), along = (p[0] - c[0]) * d[0] + (p[1] - c[1]) * d[1];
      if (along <= 2) return;
      var across = Math.abs((p[0] - c[0]) * d[1] - (p[1] - c[1]) * d[0]), s = along + 2 * across;
      if (across > along * 1.8) return;            // only what lies roughly that way
      if (s < bs) { bs = s; best = b; }
    });
    if (best) best.focus();
  });
})();
