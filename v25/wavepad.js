/* A wave pad: one cycle of a wave, drawn on a small canvas in pixels and changed by drawing
   on it, or chosen from the buttons beside it (each button's data-wave names a shape). The
   UPIC sounds its voices in one, and the tape player and the computer's Player their notes.
   A pad given no shape at the start shows the "tape" shape, which stands for the player's own
   sound (a triangle with a soft octave over it) and gives no samples, so the player keeps it.

   WavePad(canvas, buttons, onChange, first, colours) -> { samples() (null for the tape's own), name() }
   first is the shape to begin with (the tape's own if none); colours ({ paper, rule, ink }) are
   the pad's, if it is drawn in another palette (the computer's).
   onChange(name, samples) is called whenever the wave changes; name is the shape's, or
   "drawn" for a wave drawn by hand. */

var WavePad = function (canvas, buttons, onChange, first, colours) {
  'use strict';
  var N = 96, wave = new Float32Array(N), name = null;
  colours = colours || {};
  var PAPER = colours.paper || '#f1e7d5', RULE = colours.rule || '#cbb991', INK = colours.ink || '#1e1d1b';
  var SHAPES = {
    sine: function (t) { return Math.sin(2 * Math.PI * t); },
    triangle: function (t) { return 1 - 4 * Math.abs(Math.round(t - 0.25) - (t - 0.25)); },
    reed: function (t) { return t < 0.2 ? 1 : t < 0.5 ? -0.25 : t < 0.6 ? 0.6 : -0.4; },
    tooth: function (t) { return 1 - 2 * t; },
    // the tape's own: a triangle and, a quarter as loud, the sine an octave over it
    tape: function (t) { return (SHAPES.triangle(t) + 0.25 * Math.sin(4 * Math.PI * t)) / 1.15; }
  };
  var g = canvas.getContext('2d');

  function draw() {
    var w = canvas.width, h = canvas.height, prev = null;
    g.fillStyle = PAPER; g.fillRect(0, 0, w, h);
    g.fillStyle = RULE; g.fillRect(0, Math.floor(h / 2), w, 1);
    g.fillStyle = INK;
    for (var i = 0; i < N; i++) {
      var y = Math.round((1 - wave[i]) / 2 * (h - 1));
      if (prev === null) g.fillRect(i, y, 1, 1);
      else for (var yy = Math.min(prev, y); yy <= Math.max(prev, y); yy++) g.fillRect(i, yy, 1, 1);
      prev = y;
    }
  }
  function mark() { buttons.forEach(function (b) { b.setAttribute('aria-pressed', String(b.getAttribute('data-wave') === name)); }); }
  function changed() { mark(); if (onChange) onChange(name, samples()); }
  function shape(n) { name = n; for (var i = 0; i < N; i++) wave[i] = SHAPES[n](i / N); draw(); }
  function samples() { return name === 'tape' ? null : Array.prototype.slice.call(wave); }

  // drawing on the pad: each column under the pointer takes its height, the columns between
  // two moves filled in along the line
  var last = null;
  function at(e) {
    var r = canvas.getBoundingClientRect();
    return [Math.max(0, Math.min(N - 1, Math.floor((e.clientX - r.left) / r.width * N))), Math.max(-1, Math.min(1, 1 - 2 * (e.clientY - r.top) / r.height))];
  }
  canvas.addEventListener('pointerdown', function (e) {
    e.preventDefault();
    try { canvas.setPointerCapture(e.pointerId); } catch (err) { /* synthetic */ }
    last = at(e); wave[last[0]] = last[1]; name = 'drawn'; draw();
  });
  canvas.addEventListener('pointermove', function (e) {
    if (!last) return;
    var p = at(e), a = Math.min(p[0], last[0]), b = Math.max(p[0], last[0]);
    for (var i = a; i <= b; i++) wave[i] = b === a ? p[1] : last[1] + (p[1] - last[1]) * (i - last[0]) / (p[0] - last[0]);
    last = p; draw();
  });
  function up() { if (last) { last = null; changed(); } }
  canvas.addEventListener('pointerup', up);
  canvas.addEventListener('pointercancel', up);
  buttons.forEach(function (b) {
    b.addEventListener('click', function () { shape(b.getAttribute('data-wave')); changed(); });
  });

  shape(first || 'tape');
  mark();
  return { samples: samples, name: function () { return name; } };
};
