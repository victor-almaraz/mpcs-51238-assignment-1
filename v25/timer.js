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

  /* ---------------- the tomato, drawn in pixels ---------------- */
  var R = '#ce3a2e', R_L = '#ee765f', R_D = '#a02822', R_DD = '#761c1a', CREAM = '#f6ecdc', CREAM_D = '#d8c8b0', INK = '#3a2622';
  var GR = '#5a8c3c', GR_D = '#46703a', GR_L = '#8cb85a';
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
  var CX = 80, CY = 74, RX = 66, RY = 48, BAND = 60;
  function body(x, y) { var u = (x - CX) / RX, v = (y - CY) / RY; return u * u + v * v <= 1; }
  function draw() {
    g.clearRect(0, 0, W, H);
    // its shadow on the desk, then the body: lit from the left, the top above the seam
    for (var y = 0; y < H; y++) for (var x = 0; x < W; x++) {
      var sx = x - 6, sy = y - 6;
      if (!body(x, y)) { if (body(sx, sy) && y > CY) rect(x, y, 1, 1, 'rgba(40,24,18,0.3)'); continue; }
      var u = (x - CX) / RX, v = (y - CY) / RY, lite = -u * 0.7 - v * 0.7;
      var c = lite > 0.75 ? R_L : lite > -0.35 ? R : lite > -0.85 ? R_D : R_DD;
      if (lite > -0.35 && lite <= 0.75 && (x + y) % 2 && lite > 0.6) c = R_L;
      if (lite > -0.85 && lite <= -0.35 && (x + y) % 2 && lite > -0.5) c = R;
      rect(x, y, 1, 1, c);
    }
    // the turning top's band: the minutes run past the pointer as the time does
    var min = remaining() / 60000;
    for (var bx = CX - RX; bx <= CX + RX; bx++) {
      for (var by = BAND - 4; by <= BAND + 4; by++) if (body(bx, by)) rect(bx, by, 1, 1, by === BAND + 4 ? CREAM_D : CREAM);
    }
    var hw = Math.sqrt(1 - Math.pow((BAND - CY) / RY, 2)) * RX - 3;
    for (var m = 0; m <= 60; m++) {
      var th = (m - min) * 6 * Math.PI / 180;
      if (Math.abs(th) > 1.35) continue;
      var tx = Math.round(CX + Math.sin(th) * hw), major = m % 5 === 0;
      rect(tx, BAND - 4, 1, major ? 3 : 2, INK);
      if (major && Math.abs(th) < 0.9) { var s = String(m); digits(s, tx - (s.length * 6 - 1) / 2 | 0, BAND - 0, INK); }
    }
    for (var sx2 = CX - RX; sx2 <= CX + RX; sx2++) if (body(sx2, BAND + 5)) rect(sx2, BAND + 5, 1, 1, R_DD);
    // the pointer, fixed on the body under the band
    rect(CX - 2, BAND + 6, 5, 1, CREAM); rect(CX - 1, BAND + 7, 3, 1, CREAM); rect(CX, BAND + 8, 1, 1, CREAM);
    // the calyx and its stem
    [[-1, 0.5], [1, 0.5], [-0.35, 1], [0.35, 1], [0, -1]].forEach(function (l) {
      for (var k = 0; k < 14; k++) {
        var lx = CX + l[0] * k * 1.6, ly = 30 + k * 0.45 * l[1] - (l[1] < 0 ? k * 0.6 : 0), wdt = Math.max(1, 4 - Math.abs(k - 5) * 0.5);
        rect(Math.round(lx - wdt / 2), Math.round(ly), Math.round(wdt), 2, k < 3 ? GR_D : GR);
        if (k === 6) rect(Math.round(lx), Math.round(ly), 1, 1, GR_L);
      }
    });
    rect(CX - 2, 16, 4, 14, GR_D); rect(CX - 2, 16, 1, 14, GR); rect(CX + 2, 15, 3, 2, GR_D);
  }
  // two CSS pixels to its pixel, as the page's type has, or four where there is room
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
