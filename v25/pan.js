/* Turning round the corner. The room is two walls side by side, the desk's and the reading
   corner's (style.css, "round the corner"); one is in front at a time, and the room turns
   from one to the other as a point-and-click game pans: by the tab at each wall's edge, or
   when the keyboard's focus goes to something on the other wall. The turn eases in and out,
   a whole art pixel at a time (--pan, in art pixels); with reduced motion it is a cut.
   Pan.to(view) turns to a wall (0 the desk's, 1 the corner's); Pan.view() says which. */

var Pan = (function () {
  'use strict';
  var doc = document, scene = doc.querySelector('.overview'), corner = doc.getElementById('corner');
  if (!scene || !corner) return { to: function () {}, view: function () { return 0; } };
  var station = scene.closest('.station');
  var REDUCED = window.matchMedia('(prefers-reduced-motion: reduce)');
  var LIST = window.matchMedia('(max-width: 1011px), (max-height: 505px)');
  var WIDTH = 640, TIME = 700;
  var view = 0, at = 0, frame = null, done = null;

  function set(x) { at = x; scene.style.setProperty('--pan', String(x)); }
  function to(v, focusEl) {
    v = v ? 1 : 0;
    if (v === view) { if (focusEl) focusEl.focus({ preventScroll: true }); return; }
    view = v;
    scene.setAttribute('data-view', String(v));
    if (focusEl) focusEl.focus({ preventScroll: true });
    scene.dispatchEvent(new CustomEvent('room:turn', { detail: { view: v } }));
    cancelAnimationFrame(frame);
    var from = at, goal = v * WIDTH, t0 = null;
    if (REDUCED.matches || LIST.matches) { set(goal); return; }
    function step(t) {
      if (t0 === null) t0 = t;
      var k = Math.min(1, (t - t0) / TIME), e = k < 0.5 ? 2 * k * k : 1 - Math.pow(-2 * k + 2, 2) / 2;
      set(Math.round(from + (goal - from) * e));
      if (k < 1) frame = requestAnimationFrame(step);
    }
    frame = requestAnimationFrame(step);
    // where frames are held back (a page out of sight), the turn still ends where it should
    clearTimeout(done); done = setTimeout(function () { if (at !== goal) { cancelAnimationFrame(frame); set(goal); } }, TIME + 150);
  }

  // the tabs at the walls' edges; the focus goes with the room, to the tab on the far side
  Array.prototype.forEach.call(scene.querySelectorAll('[data-turn-to]'), function (b) {
    b.addEventListener('click', function () {
      var v = Number(b.getAttribute('data-turn-to'));
      to(v, b.matches(':focus-visible') ? scene.querySelector('[data-turn-to="' + (1 - v) + '"]') : null);
    });
  });
  // the keyboard's focus on the other wall turns the room to it
  scene.addEventListener('focusin', function (e) {
    if (e.target.closest('.narration') || e.target.matches('[data-turn-to]')) return;
    if (e.target.closest('.scene .swap, .scene .obj')) to(corner.contains(e.target) ? 1 : 0);
    station.scrollLeft = 0;
  });
  return { to: to, view: function () { return view; } };
})();
