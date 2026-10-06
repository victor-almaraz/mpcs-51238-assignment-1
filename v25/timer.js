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
     The body, its calyx and its stem are a picture (assets/st/pomo-body.png), made by
     util/v25/seeds25.py from a solid: a squat sphere whose radius swells in five lobes round its
     shoulders, dips into a well at the top and flattens where it stands, seen from a little
     above. Over it, each second, the turning top's band of minutes is drawn round the same solid
     (TOM matches seeds25.py's), so it rides the lobes and sags at the front as a ring seen from
     above does; its minutes and numbers are placed by longitude, so they foreshorten toward the
     sides and turn away round them. */
  var RED0 = '#3e1022', CRM = ['#a8936f', '#c9b48e', '#e3d4b4', '#f6eddb', '#fffaf0'], INK = '#3a2422';
  var TOM = { cx: 80, cy: 76, rx: 66, ry: 46, tilt: 0.36, lobes: 0.055, well: 0.2 }, BAND = -0.2, BH = 0.13;
  function radius(ph, la) {
    var up = Math.max(0, Math.min(1, (0.75 - Math.sin(ph)) / 1.5));
    return 1 + TOM.lobes * Math.cos(5 * la + 0.4) * up - TOM.well * Math.exp(-Math.pow((ph + Math.PI / 2) / 0.42, 2));
  }
  function point(ph, la) {
    var r = radius(ph, la), X = r * Math.cos(ph) * Math.sin(la) * TOM.rx, Y = r * Math.sin(ph) * TOM.ry, Z = r * Math.cos(ph) * Math.cos(la) * TOM.rx;
    if (Y > 0.8 * TOM.ry) Y = 0.8 * TOM.ry + (Y - 0.8 * TOM.ry) * 0.35;
    var c = Math.cos(TOM.tilt), s = Math.sin(TOM.tilt);
    return [TOM.cx + X, TOM.cy + Y * c + Z * s, Z * c - Y * s];
  }
  // how squarely a point of the surface faces the viewer, and how much light it takes
  function facing(ph, la) {
    var p = point(ph, la), a = point(ph + 1e-3, la), b = point(ph, la + 1e-3);
    var u = [a[0] - p[0], a[1] - p[1], a[2] - p[2]], v = [b[0] - p[0], b[1] - p[1], b[2] - p[2]];
    var n = [v[1] * u[2] - v[2] * u[1], v[2] * u[0] - v[0] * u[2], v[0] * u[1] - v[1] * u[0]], l = Math.hypot(n[0], n[1], n[2]) || 1;
    if (n[0] * (p[0] - TOM.cx) + n[1] * (p[1] - TOM.cy) + n[2] * p[2] < 0) l = -l;   // outward
    return [n[0] / l, n[1] / l, n[2] / l];
  }
  var base = doc.createElement('canvas'); base.width = W; base.height = H;
  (function drawBase() {
    var c = base.getContext('2d');
    // its shadow on the desk, a soft ellipse in two steps
    c.fillStyle = 'rgba(46,26,20,0.32)';
    for (var y = 100; y < H; y++) for (var x = 0; x < W; x++) {
      var u = (x - TOM.cx - 8) / (TOM.rx + 6), v = (y - 113) / 13, d = u * u + v * v;
      if (d < 1 && (d < 0.55 || (x + y) % 2)) c.fillRect(x, y, 1, 1);
    }
    var body = new Image();
    body.onload = function () { c.drawImage(body, 0, 0); if (Desk.current() === 'timer') draw(); };
    body.src = 'assets/st/pomo-body.png';
  })();
  // the band's pixels, worked out once: for each, its longitude, how far down the band it lies
  // (0 its top, 1 its foot) and its shade
  var BANDPX = (function () {
    var seen = {}, out = [];
    for (var i = 0; i <= 1600; i++) {
      var la = -Math.PI + i * 2 * Math.PI / 1600;
      for (var k = 0; k <= 40; k++) {
        var ph = BAND - BH + k * 2 * BH / 40, n = facing(ph, la);
        if (n[2] < 0.2) continue;
        var p = point(ph, la), x = Math.floor(p[0]), y = Math.floor(p[1]), key = y * W + x;
        if (seen[key] !== undefined && out[seen[key]].z > p[2]) continue;
        var l = -0.55 * n[0] - 0.68 * n[1] + 0.48 * n[2];
        var o = { x: x, y: y, z: p[2], la: la, t: k / 40, edge: n[2] < 0.32, l: l };
        if (seen[key] === undefined) { seen[key] = out.length; out.push(o); } else out[seen[key]] = o;
      }
    }
    return out;
  })();
  var SEAM = (function () {
    var out = [];
    for (var i = 0; i <= 1600; i++) {
      var la = -Math.PI + i * 2 * Math.PI / 1600;
      if (facing(BAND + BH + 0.02, la)[2] < 0.2) continue;
      var p = point(BAND + BH + 0.02, la); out.push([Math.floor(p[0]), Math.floor(p[1])]);
    }
    return out;
  })();
  function draw() {
    g.clearRect(0, 0, W, H);
    g.drawImage(base, 0, 0);
    SEAM.forEach(function (p) { rect(p[0], p[1], 1, 1, RED0); });              // the seam under the turning top
    BANDPX.forEach(function (o) {
      // lit from the upper left, in bands; its top edge catching the light, its foot in shade,
      // its ends, where it turns away, dark
      var v = o.l + (o.t < 0.2 ? 0.14 : o.t > 0.8 ? -0.16 : 0);
      rect(o.x, o.y, 1, 1, o.edge || o.t > 0.95 ? CRM[0] : CRM[Math.max(1, Math.min(4, Math.floor(0.4 + v * 4.4)))]);
    });
    // the minutes, round the band, numbered every five
    var min = remaining() / 60000;
    for (var m = 0; m <= 60; m++) {
      var la = (m - min) * 6 * Math.PI / 180, major = m % 5 === 0;
      if (facing(BAND, la)[2] < 0.4) continue;
      var a = point(BAND - BH * 0.85, la), b2 = point(BAND - BH * (major ? 0.45 : 0.62), la);
      for (var y = Math.floor(a[1]); y <= Math.floor(b2[1]); y++) rect(Math.floor(a[0] + (b2[0] - a[0]) * (y - a[1]) / Math.max(1, b2[1] - a[1])), y, 1, 1, INK);
      if (major && Math.cos(la) > 0.55) {
        var c = point(BAND - BH * 0.3, la), s = String(m);
        digits(s, Math.round(c[0]) - ((s.length * 6 - 1) / 2 | 0), Math.round(c[1]), INK);
      }
    }
    // the pointer, a cream notch on the body under the band's middle
    var q = point(BAND + BH + 0.09, 0), qx = Math.round(q[0]), qy = Math.round(q[1]);
    rect(qx - 2, qy, 5, 1, CRM[3]); rect(qx - 1, qy + 1, 3, 1, CRM[3]); rect(qx, qy + 2, 1, 1, CRM[2]);
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
