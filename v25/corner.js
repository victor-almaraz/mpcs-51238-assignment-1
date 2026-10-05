/* The reading corner's things (index.html, #corner). A book is taken down from the shelf and
   the narrator says what it is, offering a deck it calls to mind (look.js); the metronome is
   set going, and runs down after a while; the fish are fed, and come up to the flakes; the
   clock's hands keep the visitor's time, drawn in pixels on its face. What happens is told as
   events on the scene, for the sounds (sounds.js). Needs Look (look.js) and Decor (decor.js). */

(function () {
  'use strict';
  var doc = document, scene = doc.querySelector('.overview'), corner = doc.getElementById('corner');
  if (!scene || !corner) return;
  var status = doc.getElementById('swap-status');
  function say(msg) { status.textContent = ''; setTimeout(function () { status.textContent = msg; }, 30); }
  function tell(what, detail) { scene.dispatchEvent(new CustomEvent('room:' + what, { detail: detail })); }

  /* ---------------- the books: taken down, they are read about ---------------- */
  Array.prototype.forEach.call(corner.querySelectorAll('.book'), function (b) {
    b.addEventListener('click', function () {
      Look.look(b);
      b.classList.add('taken');
      tell('book');
    });
  });

  /* ---------------- the metronome ---------------- */
  var met = corner.querySelector('.metronome'), beat = null, runs = null;
  function going(on) {
    clearInterval(beat); clearTimeout(runs);
    met.setAttribute('aria-pressed', String(on));
    met.setAttribute('data-say', on ? 'Stop the metronome' : 'Start the metronome');
    met.setAttribute('aria-label', 'A metronome: ' + (on ? 'ticking' : 'still'));
    if (!on) return;
    // a tick at each end of the swing, two to the second, as the rod's frames show (style.css)
    tell('tick'); beat = setInterval(function () { tell('tick'); }, 500);
    runs = setTimeout(function () { going(false); say('The metronome runs down.'); }, 40000);
  }
  met.addEventListener('click', function () {
    var on = met.getAttribute('aria-pressed') !== 'true';
    going(on);
    say(on ? 'The metronome ticks, two beats to the second.' : 'The metronome is still.');
  });

  /* ---------------- the fish ---------------- */
  var tank = corner.querySelector('.tank'), fed = null;
  tank.addEventListener('click', function () {
    // the flakes start again from the surface at every pinch
    scene.classList.remove('feeding'); void scene.offsetWidth; scene.classList.add('feeding');
    clearTimeout(fed); fed = setTimeout(function () { scene.classList.remove('feeding'); }, 5600);
    tell('feed');
    say('A pinch of flakes on the water. The tetras and the angelfish come up for them; the corydoras waits on the gravel for what sinks.');
  });

  /* ---------------- the clock ---------------- */
  // its hands in the ink of its marks, for each time of day (the palette's, as the face is drawn)
  var INK = { morning: '#342b4a', evening: '#342b4a', night: '#271e3f' };
  var clock = corner.querySelector('.clock'), hands = clock.querySelector('canvas'), g = hands.getContext('2d');
  function line(x0, y0, x1, y1) {
    var dx = Math.abs(x1 - x0), dy = Math.abs(y1 - y0), sx = x0 < x1 ? 1 : -1, sy = y0 < y1 ? 1 : -1, e = dx - dy;
    for (;;) {
      g.fillRect(x0, y0, 1, 1);
      if (x0 === x1 && y0 === y1) return;
      var e2 = 2 * e;
      if (e2 > -dy) { e -= dy; x0 += sx; }
      if (e2 < dx) { e += dx; y0 += sy; }
    }
  }
  function draw() {
    var d = new Date(), m = d.getMinutes(), h = d.getHours() % 12 + m / 60;
    g.clearRect(0, 0, 29, 29);
    g.fillStyle = INK[Decor.time()] || INK.evening;
    var a = m / 60 * 2 * Math.PI, b = h / 12 * 2 * Math.PI;
    line(14, 14, Math.round(14 + Math.sin(a) * 9), Math.round(14 - Math.cos(a) * 9));
    line(14, 14, Math.round(14 + Math.sin(b) * 6), Math.round(14 - Math.cos(b) * 6));
  }
  function told() {
    var d = new Date(), h = d.getHours(), m = d.getMinutes();
    return 'It says ' + (h % 12 || 12) + ':' + (m < 10 ? '0' : '') + m + '.';
  }
  clock.addEventListener('click', function () { Look.look(clock); });
  draw();
  setInterval(draw, 20000);
  new MutationObserver(draw).observe(doc.getElementById('desk'), { attributes: true, attributeFilter: ['data-time'] });
  window.Corner = { time: told };
})();
