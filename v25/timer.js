/* The tomato timer on the desk, for working in pomodoros: a spell of work (25 minutes), a short
   break (5); after every fourth spell, a long break (15). Taken up, the timer is drawn large
   in pixels, its top turning as the minutes run down past its pointer, the time and the spell
   under it, a tomato for each spell done in the set of four, and its controls: Start and
   Pause, Reset (the spell back to its start), Skip (on to the next), the lengths, and whether
   the next spell starts by itself. It runs wherever the visitor is in the room (the page's
   title counts down too), and rings its bell when a spell ends, if Room sounds is on; while
   it is in front, it ticks. Nothing is stored. Needs Desk (desk.js). */

(function () {
  'use strict';
  var doc = document, station = doc.querySelector('.st-timer');
  if (!station) return;
  var $ = function (id) { return doc.getElementById(id); };
  var canvas = $('pomo-canvas'), g = canvas.getContext('2d'), wrap = station.querySelector('.pomo-tomato');
  var roomBtn = doc.querySelector('.o-timer'), title = doc.title;
  var W = 160, H = 128;
  var NAMES = { work: 'Work', short: 'Short break', long: 'Long break' };
  var phase = 'work', running = false, endAt = 0, left = 0, done = 0;

  function minutes(k) { var v = Math.round(Number($('pomo-' + k).value)); return Math.max(1, Math.min(90, v || 1)); }
  function length(p) { return minutes(p) * 60000; }
  function every() { return Math.max(2, Math.min(8, Math.round(Number($('pomo-every').value)) || 4)); }
  function fmt(ms) { var s = Math.ceil(ms / 1000), m = Math.floor(s / 60); s %= 60; return (m < 10 ? '0' : '') + m + ':' + (s < 10 ? '0' : '') + s; }
  function say(m) { $('pomo-status').textContent = ''; setTimeout(function () { $('pomo-status').textContent = m; }, 30); }

  /* ---------------- the spells ---------------- */
  function load(p) { phase = p; left = length(p); running = false; show(); }
  function start() { if (running) return; running = true; endAt = Date.now() + left; show(); say(NAMES[phase] + ': ' + fmt(left) + ', running.'); }
  function pause() { if (!running) return; left = Math.max(0, endAt - Date.now()); running = false; show(); say('Paused at ' + fmt(left) + '.'); }
  // after work, a break (the long one when the set is done); after a break, work. A spell of
  // work counts as done only if it ran out, not if it was skipped
  function nextPhase(counts) {
    if (phase === 'work') { if (counts) done++; return counts && done % every() === 0 ? 'long' : 'short'; }
    return 'work';
  }
  function finish() {
    var was = phase, p = nextPhase(true);
    bell();
    load(p);
    var msg = (was === 'work' ? 'The spell of work is over: ' + done + ' done. ' : 'The break is over. ') + NAMES[p] + ' next, ' + minutes(p) + ' minutes.';
    if ($('pomo-auto').checked) { start(); msg += ' It has started.'; }
    say('The tomato timer rings. ' + msg);
  }

  $('pomo-go').addEventListener('click', function () { if (running) pause(); else start(); });
  $('pomo-reset').addEventListener('click', function () { load(phase); say(NAMES[phase] + ' set back to ' + fmt(left) + '.'); });
  $('pomo-skip').addEventListener('click', function () { var p = nextPhase(false); load(p); say('Skipped to ' + NAMES[p].toLowerCase() + ', ' + fmt(left) + '.'); });
  ['work', 'short', 'long'].forEach(function (k) {
    $('pomo-' + k).addEventListener('change', function () { if (!running && phase === k) { left = length(k); show(); } });
  });

  /* ---------------- what shows: the time, the spell, the tally, the room's caption ---------------- */
  function remaining() { return running ? Math.max(0, endAt - Date.now()) : left; }
  function show() {
    var ms = remaining(), t = fmt(ms);
    $('pomo-time').textContent = t;
    $('pomo-phase').textContent = NAMES[phase];
    $('pomo-go').textContent = running ? 'Pause' : (ms < length(phase) ? 'Go on' : 'Start');
    // the set's tomatoes: those done in it, or all of them in the long break that ends it
    var n = every(), have = phase === 'long' ? n : done % n, tally = $('pomo-tally');
    if (tally.children.length !== n) { tally.textContent = ''; for (var i = 0; i < n; i++) tally.appendChild(doc.createElement('i')); }
    Array.prototype.forEach.call(tally.children, function (el, i) { el.classList.toggle('done', i < have); });
    $('pomo-count').textContent = done === 1 ? '1 spell of work done' : done + ' spells of work done';
    doc.title = running ? t + ' ' + NAMES[phase] + ' · ' + title : title;
    if (roomBtn) roomBtn.setAttribute('data-say', running ? 'Tomato timer: ' + t + ' of ' + NAMES[phase].toLowerCase() + ' left' : 'Set the tomato timer');
    station.setAttribute('data-phase', phase);
  }

  /* ---------------- the tomato, drawn in pixels ----------------
     Its body an ellipsoid lit from the upper left, its shading dithered between neighbouring
     tones of one ramp, faint lobes running down from the calyx, a highlight; the turning top's
     band a slice of the same ellipsoid, curving down at the front as a ring seen from a little
     above does, its minutes foreshortened toward the sides; the calyx's five sepals and the
     stem, cut square, on top. The body and calyx are drawn once; the band each second. */
  var RED = ['#4a1312', '#6e1b18', '#922620', '#b53326', '#d0452f', '#e56a4e', '#f49a7e'], SHINE = '#ffe3d4';
  var CRM = ['#a8936f', '#c9b48e', '#e3d4b4', '#f6eddb', '#fffaf0'], INK = '#3a2422';
  var GRN = ['#22381c', '#33532a', '#487236', '#62923f', '#86b552', '#aed27a'];
  var BAYER = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]];
  var CX = 80, CY = 78, RX = 66, RY = 46, BAND = 58, LIGHT = norm([-0.55, -0.62, 0.56]);
  function norm(v) { var l = Math.hypot(v[0], v[1], v[2]); return [v[0] / l, v[1] / l, v[2] / l]; }
  function ramp(tones, v, x, y) {
    // v in 0..1 across the ramp; between two tones, an ordered dither fixed to the grid
    var f = Math.max(0, Math.min(tones.length - 1.001, v * (tones.length - 1))), i = Math.floor(f);
    return tones[(f - i) * 16 > BAYER[y & 3][x & 3] + 0.5 ? i + 1 : i];
  }
  function normal(x, y) {
    var nx = (x + 0.5 - CX) / RX, ny = (y + 0.5 - CY) / RY, q = 1 - nx * nx - ny * ny;
    return q <= 0 ? null : [nx, ny, Math.sqrt(q)];
  }
  function lit(n) { return Math.max(0, n[0] * LIGHT[0] + n[1] * LIGHT[1] + n[2] * LIGHT[2]); }
  var base = doc.createElement('canvas'); base.width = W; base.height = H;
  (function drawBase() {
    var c = base.getContext('2d');
    function put(x, y, col) { c.fillStyle = col; c.fillRect(x, y, 1, 1); }
    // its shadow on the desk, a soft ellipse in two steps of dither
    for (var y = CY + 20; y < H; y++) for (var x = 0; x < W; x++) {
      var u = (x - CX - 8) / (RX + 4), v = (y - CY - 30) / 16, d = u * u + v * v;
      if (d < 1 && (d < 0.55 || (x + y) % 2)) put(x, y, 'rgba(46,26,20,0.32)');
    }
    for (var y2 = 0; y2 < H; y2++) for (var x2 = 0; x2 < W; x2++) {
      var n = normal(x2, y2);
      if (!n) continue;
      var l = lit(n), lobe = Math.cos(Math.atan2(n[0], n[2]) * 7) * (1 - n[1]) * 0.05;
      var v2 = 0.12 + 0.88 * Math.pow(l, 0.85) - Math.max(0, lobe);
      var edge = n[2] < 0.16;
      var col = edge ? RED[0] : ramp(RED, v2, x2, y2);
      var h = norm([LIGHT[0], LIGHT[1], LIGHT[2] + 1]), sp = n[0] * h[0] + n[1] * h[1] + n[2] * h[2];
      if (sp > 0.985) col = SHINE; else if (sp > 0.97 && (x2 + y2) % 2) col = RED[6];
      put(x2, y2, col);
    }
    // the calyx: five sepals from the stem, seen a little from above, and the stem cut square
    var sx = CX, sy = 34;
    for (var k = 0; k < 5; k++) {
      var a = -Math.PI / 2 + k * 2 * Math.PI / 5 + 0.35;
      for (var t = 0; t < 1; t += 0.02) {
        var len = 26 * (0.8 + 0.2 * Math.sin(k * 2.1)), w = 5.5 * Math.sin(Math.PI * Math.min(1, t * 1.25)) * (1 - t * 0.6);
        var px = sx + Math.cos(a) * len * t, py = sy + Math.sin(a) * len * t * 0.42 + t * t * 6;
        for (var s2 = -w; s2 <= w; s2 += 0.5) {
          var qx = Math.round(px - Math.sin(a) * s2 * 0.9), qy = Math.round(py + Math.cos(a) * s2 * 0.42);
          var side = s2 < 0 ? 1 : 0, shade = 0.25 + 0.5 * side + 0.25 * (1 - t);
          put(qx, qy, Math.abs(s2) > w - 0.7 ? GRN[0] : ramp(GRN, shade, qx, qy));
        }
      }
    }
    for (var yy = 16; yy < 36; yy++) for (var xx = -3; xx <= 3; xx++) {
      var bend = Math.round((36 - yy) * 0.12);
      put(sx + xx + bend, yy, Math.abs(xx) === 3 ? GRN[0] : xx < 0 ? GRN[3] : xx === 0 ? GRN[2] : GRN[1]);
    }
    for (var e = -3; e <= 3; e++) put(sx + e + 2, 15, e === -3 || e === 3 ? GRN[0] : GRN[5]);
  })();
  function draw() {
    g.clearRect(0, 0, W, H);
    g.drawImage(base, 0, 0);
    // the band: the ellipsoid's slice from BAND - 5 to BAND + 4, its front sagging by up to 3
    var min = remaining() / 60000, hw = Math.sqrt(1 - Math.pow((BAND - CY) / RY, 2)) * RX;
    for (var x = Math.ceil(CX - hw); x < CX + hw; x++) {
      var sinT = (x + 0.5 - CX) / hw, cosT = Math.sqrt(Math.max(0, 1 - sinT * sinT)), sag = Math.round(3 * cosT);
      for (var dy = -5; dy <= 4; dy++) {
        var y = BAND + dy + sag, n = normal(x, y);
        if (!n) continue;
        var l = lit([sinT * 0.9, -0.1, cosT]);
        rect(x, y, 1, 1, dy === 4 ? CRM[0] : dy === -5 ? CRM[1] : ramp(CRM, 0.2 + 0.8 * l, x, y));
      }
      if (normal(x, BAND + 5 + sag)) rect(x, BAND + 5 + sag, 1, 1, RED[0]);         // the seam under the turning top
    }
    // the minutes, round the band: foreshortened toward its sides, numbered every five
    for (var m = 0; m <= 60; m++) {
      var th = (m - min) * 6 * Math.PI / 180;
      if (Math.cos(th) < 0.18) continue;
      var tx = Math.round(CX + Math.sin(th) * (hw - 2)), sg = Math.round(3 * Math.cos(th)), major = m % 5 === 0;
      rect(tx, BAND - 4 + sg, 1, major ? 3 : 2, INK);
      if (major && Math.cos(th) > 0.6) { var s = String(m); digits(s, tx - ((s.length * 6 - 1) / 2 | 0), BAND - 0 + sg, INK); }
    }
    // the pointer, a cream notch on the body under the band's middle
    rect(CX - 2, BAND + 8, 5, 1, CRM[3]); rect(CX - 1, BAND + 9, 3, 1, CRM[3]); rect(CX, BAND + 10, 1, 1, CRM[2]);
  }
  var DIG = { 0: '0e11131519110e', 1: '040c040404040e', 2: '0e11010204081f', 3: '1f02040201110e', 4: '02060a121f0202', 5: '1f101e0101110e',
    6: '0608101e11110e', 7: '1f010204080808', 8: '0e11110e11110e', 9: '0e11110f01020c' };
  function rect(x, y, w, h, c) { g.fillStyle = c; g.fillRect(x, y, w, h); }
  function digits(s, x, y, c) {
    g.fillStyle = c;
    String(s).split('').forEach(function (ch, i) {
      var f = DIG[ch];
      for (var r = 0; r < 7; r++) { var b = parseInt(f.substr(r * 2, 2), 16); for (var k = 0; k < 5; k++) if (b & (16 >> k)) g.fillRect(x + i * 6 + k, y + r, 1, 1); }
    });
  }
  function fit() { wrap.style.setProperty('--ts', (station.clientHeight > 900 && station.clientWidth > 1400 ? 4 : 2) + 'px'); }
  if (window.ResizeObserver) new ResizeObserver(fit).observe(station);

  /* ---------------- the clock that drives it ---------------- */
  var lastSec = -1;
  setInterval(function () {
    if (running && Date.now() >= endAt) { left = 0; running = false; finish(); return; }
    var sec = Math.ceil(remaining() / 1000);
    if (sec !== lastSec) { lastSec = sec; show(); if (running && Desk.current() === 'timer') tick(); }
    if (Desk.current() === 'timer') draw();
  }, 200);
  Desk.onShow('timer', function () { fit(); draw(); show(); });

  /* ---------------- its sounds: a tick while it is in front and running, the bell ---------------- */
  var ac = null, out = null;
  function ctx() {
    var b = $('sound-btn');
    if (b && b.getAttribute('aria-pressed') === 'false') return null;
    if (!ac) { var AC = window.AudioContext || window.webkitAudioContext; if (!AC) return null; ac = new AC(); out = ac.createGain(); out.gain.value = 0.3; out.connect(ac.destination); }
    if (ac.state === 'suspended') ac.resume();
    return ac;
  }
  function ping(t, hz, dur, vol) {
    var o = ac.createOscillator(), v = ac.createGain();
    o.frequency.value = hz; v.gain.setValueAtTime(vol, t); v.gain.exponentialRampToValueAtTime(0.0001, t + dur);
    o.connect(v); v.connect(out); o.start(t); o.stop(t + dur + 0.05);
  }
  function tick() { if (!ctx()) return; var t = ac.currentTime; ping(t, 3100, 0.012, 0.05); ping(t + 0.004, 1700, 0.01, 0.03); }
  // the bell: a clapper on a small steel bell, struck twenty times
  function bell() {
    if (!ctx()) return;
    var t = ac.currentTime + 0.02;
    for (var k = 0; k < 20; k++) { var at = t + k * 0.07; ping(at, 2350, 0.25, 0.18); ping(at, 3790, 0.15, 0.08); ping(at, 5600, 0.08, 0.04); }
  }

  load('work');
})();
