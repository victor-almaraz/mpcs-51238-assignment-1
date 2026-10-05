/* The UPIC, after the Unité Polyagogique Informatique du CEMAMu that Xenakis built in Paris
   and first played in 1977: music drawn rather than written. On the page time runs to the
   right and pitch rises up it (four octaves, C2 to C6, a rule at every C); each line drawn
   is a voice, sounding its pitch as the page plays under the playhead, so a slanting line is
   a glissando, a branching one an arborescence, a scatter of dashes a cloud. Every voice
   sounds in the wave drawn on the small pad: one cycle of it, drawn freehand or chosen.
   A line is drawn with the pointer or with the keyboard (the arrows move the pen, Space puts
   it down and lifts it); it only runs forward in time, as the UPIC's did. A page can be
   punched as tape cards (one event card a pulse, at 120 beats a minute) into the out tray's
   stacker, and played on the tape player. Needs Desk (desk.js), Out (out.js), Tape
   (scripts/tape.js) and WavePad (wavepad.js). */

var Upic = (function () {
  'use strict';
  var doc = document, $ = Desk.$, plural = Desk.plural;
  var W = 360, H = 200, LOW = 36, OCT = 4;               // the page in pixels; C2 (MIDI 36) and four octaves up
  var PAPER = '#f1e7d5', GRID = '#e2d6bd', RULE = '#cbb991', INK = '#1e1d1b', LIVE = '#b5462b', PEN = '#2b4560';
  var page = $('upic-page'), g = page.getContext('2d');
  var status = $('upic-status'), lengthIn = $('upic-length'), lengthOut = $('upic-length-out');
  var playBtn = $('upic-play'), head = $('upic-playhead'), penMark = $('upic-pen'), threadBtn = $('upic-thread');
  var strokes = [], drawing = null, playing = null, length = Number(lengthIn.value);

  function say(msg) { status.textContent = ''; setTimeout(function () { status.textContent = msg; }, 30); }
  function tell(what) { var s = doc.querySelector('.overview'); if (s) s.dispatchEvent(new CustomEvent('room:' + what)); }
  function midiAt(y) { return LOW + OCT * 12 * (1 - y / (H - 1)); }
  function hz(y) { return 440 * Math.pow(2, (midiAt(y) - 69) / 12); }
  var NAMES = ['C', 'C sharp', 'D', 'E flat', 'E', 'F', 'F sharp', 'G', 'A flat', 'A', 'B flat', 'B'];
  function noteName(y) { var m = Math.round(midiAt(y)); return NAMES[m % 12] + (Math.floor(m / 12) - 1); }
  function secs(x) { return Math.round(x / W * length * 10) / 10; }

  /* ---------------- the page ---------------- */
  // lines are set pixel by pixel, without smoothing, as everything in the room is
  function plot(x0, y0, x1, y1, col) {
    g.fillStyle = col;
    x0 = Math.round(x0); y0 = Math.round(y0); x1 = Math.round(x1); y1 = Math.round(y1);
    var dx = Math.abs(x1 - x0), dy = -Math.abs(y1 - y0), sx = x0 < x1 ? 1 : -1, sy = y0 < y1 ? 1 : -1, e = dx + dy;
    for (;;) {
      g.fillRect(x0, y0, 1, 1);
      if (x0 === x1 && y0 === y1) return;
      var e2 = 2 * e;
      if (e2 >= dy) { e += dy; x0 += sx; }
      if (e2 <= dx) { e += dx; y0 += sy; }
    }
  }
  function draw(at) {
    g.fillStyle = PAPER; g.fillRect(0, 0, W, H);
    g.fillStyle = GRID;
    for (var s = 1; s < length; s++) g.fillRect(Math.round(s / length * W), 0, 1, H);
    for (var k = 1; k < OCT * 4; k++) if (k % 4) g.fillRect(0, Math.round(H - 1 - k * (H - 1) / (OCT * 4)), W, 1);
    g.fillStyle = RULE;
    for (k = 1; k < OCT; k++) g.fillRect(0, Math.round(H - 1 - k * (H - 1) / OCT), W, 1);
    strokes.forEach(function (st) {
      var live = at !== undefined && st[0][0] <= at && at <= st[st.length - 1][0];
      for (var i = 1; i < st.length; i++) plot(st[i - 1][0], st[i - 1][1], st[i][0], st[i][1], live ? LIVE : INK);
      if (st.length === 1) plot(st[0][0], st[0][1], st[0][0], st[0][1], live ? LIVE : INK);
    });
    page.setAttribute('aria-label', strokes.length ? 'The page: ' + plural(strokes.length, 'line') + ' over ' + length + ' seconds.' : 'The page, blank.');
  }
  function at(e) {
    var r = page.getBoundingClientRect();
    return [Math.max(0, Math.min(W - 1, (e.clientX - r.left) / r.width * W)), Math.max(0, Math.min(H - 1, (e.clientY - r.top) / r.height * H))];
  }
  // a line runs only forward in time: a point to its left is passed over
  function extend(st, p) {
    var last = st[st.length - 1];
    if (p[0] > last[0] + 0.5 || (Math.abs(p[0] - last[0]) <= 0.5 && Math.abs(p[1] - last[1]) >= 1)) st.push([Math.max(p[0], last[0]), p[1]]);
  }
  function close(st) {
    if (st.length === 1) st.push([Math.min(W - 1, st[0][0] + 3), st[0][1]]);   // a dot is a short note
    draw();
  }
  page.addEventListener('pointerdown', function (e) {
    if (e.button !== 0) return;
    e.preventDefault();
    page.focus({ preventScroll: true });
    try { page.setPointerCapture(e.pointerId); } catch (err) { /* synthetic */ }
    drawing = [at(e)]; strokes.push(drawing); draw();
  });
  page.addEventListener('pointermove', function (e) { if (drawing) { extend(drawing, at(e)); draw(); } });
  function up() { if (drawing) { close(drawing); drawing = null; say(plural(strokes.length, 'line') + ' on the page.'); } }
  page.addEventListener('pointerup', up);
  page.addEventListener('pointercancel', up);

  // the keyboard's pen: the arrows move it (with Shift, ten times as far), Space puts it down
  // and lifts it; while it is down, moving it draws
  var pen = { x: 0, y: H / 2, down: null };
  function showPen() {
    penMark.style.left = (pen.x / W * 100) + '%'; penMark.style.top = (pen.y / H * 100) + '%';
    penMark.classList.toggle('down', !!pen.down);
  }
  page.addEventListener('focus', function () { penMark.hidden = false; showPen(); });
  page.addEventListener('blur', function () { penMark.hidden = true; if (pen.down) { close(pen.down); pen.down = null; } });
  page.addEventListener('keydown', function (e) {
    var step = e.shiftKey ? 10 : 2, moved = true;
    if (e.key === 'ArrowRight') pen.x = Math.min(W - 1, pen.x + step);
    else if (e.key === 'ArrowLeft') { if (pen.down) { say('A line runs only forward in time. Lift the pen with Space to move back.'); e.preventDefault(); return; } pen.x = Math.max(0, pen.x - step); }
    else if (e.key === 'ArrowUp') pen.y = Math.max(0, pen.y - step);
    else if (e.key === 'ArrowDown') pen.y = Math.min(H - 1, pen.y + step);
    else if (e.key === ' ' || e.key === 'Enter') {
      if (pen.down) { close(pen.down); pen.down = null; say('Pen up. ' + plural(strokes.length, 'line') + ' on the page.'); }
      else { pen.down = [[pen.x, pen.y]]; strokes.push(pen.down); draw(); say('Pen down at ' + secs(pen.x) + ' seconds, ' + noteName(pen.y) + '.'); }
      moved = false;
    }
    else return;
    e.preventDefault();
    if (moved && pen.down) { extend(pen.down, [pen.x, pen.y]); draw(); }
    showPen();
    if (moved) say(secs(pen.x) + ' seconds, ' + noteName(pen.y) + (pen.down ? ', drawing' : '') + '.');
  });

  /* ---------------- the wave (wavepad.js) ---------------- */
  var pad = WavePad($('upic-wave'), Array.prototype.slice.call(doc.querySelectorAll('.st-upic [data-wave]')), function (n) {
    say(n === 'drawn' ? 'The wave is redrawn.' : 'The wave is a ' + doc.querySelector('.st-upic [data-wave="' + n + '"]').textContent.toLowerCase() + '.');
  }, 'sine');

  /* ---------------- playing ---------------- */
  var ac = null;
  function periodic() { var h = Tape.harmonics(pad.samples(), 32); return ac.createPeriodicWave(h.real, h.imag); }
  function stop(quiet) {
    if (!playing) return;
    var p = playing; playing = null;
    cancelAnimationFrame(p.raf);
    p.voices.forEach(function (o) { try { o.stop(); } catch (e) { /* already stopped */ } });
    p.out.disconnect();
    head.hidden = true; playBtn.textContent = 'Play the page'; playBtn.setAttribute('aria-pressed', 'false');
    draw();
    if (!quiet) say('Stopped.');
  }
  function play() {
    if (playing) { stop(); return; }
    var lines = strokes.filter(function (st) { return st.length > 1; });
    if (!lines.length) { say('The page is blank: draw a line on it first.'); return; }
    var AC = window.AudioContext || window.webkitAudioContext;
    if (!AC) { say('This browser cannot play sound.'); return; }
    ac = ac || new AC();
    if (ac.state === 'suspended') ac.resume();
    var out = ac.createGain(), comp = ac.createDynamicsCompressor();
    out.gain.value = 0.7; out.connect(comp); comp.connect(ac.destination);
    var t0 = ac.currentTime + 0.08, w = periodic(), voices = [];
    function time(x) { return t0 + x / W * length; }
    lines.forEach(function (st) {
      var o = ac.createOscillator(), v = ac.createGain(), ts = time(st[0][0]), te = time(st[st.length - 1][0]);
      o.setPeriodicWave(w);
      o.frequency.setValueAtTime(hz(st[0][1]), ts);
      for (var i = 1; i < st.length; i++) {
        var t = time(st[i][0]);
        if (t - time(st[i - 1][0]) < 0.002) o.frequency.setValueAtTime(hz(st[i][1]), t);
        else o.frequency.exponentialRampToValueAtTime(hz(st[i][1]), t);
      }
      v.gain.setValueAtTime(0, ts); v.gain.linearRampToValueAtTime(0.16, ts + 0.02);
      v.gain.setValueAtTime(0.16, Math.max(ts + 0.02, te)); v.gain.linearRampToValueAtTime(0, te + 0.05);
      o.connect(v); v.connect(out);
      o.start(ts); o.stop(te + 0.08);
      voices.push(o);
    });
    playing = { voices: voices, out: out, raf: 0 };
    head.hidden = false; playBtn.textContent = 'Stop'; playBtn.setAttribute('aria-pressed', 'true');
    say('Playing ' + plural(lines.length, 'voice') + ' over ' + length + ' seconds.');
    tell('upic');
    (function frame() {
      if (!playing) return;
      var x = (ac.currentTime - t0) / length * W;
      if (x > W) { stop(true); say('The page has played.'); return; }
      head.style.left = (Math.max(0, x) / W * 100) + '%';
      draw(x);
      playing.raf = requestAnimationFrame(frame);
    })();
  }
  playBtn.addEventListener('click', play);

  /* ---------------- the pages to begin from ---------------- */
  function rnd(seed) { return function () { seed = (seed * 16807) % 2147483647; return seed / 2147483647; }; }
  var PAGES = {
    // a line that branches as it rises and falls, each branch branching again
    arborescence: function () {
      var r = rnd(1978), out = [];
      (function branch(x, y, slope, depth) {
        var st = [[x, y]], len = 52 + r() * 30;
        for (var k = 1; k <= 10 && x < W - 4; k++) {
          // a branch bends back as it nears the page's edge
          if ((y < 16 && slope < 0) || (y > H - 16 && slope > 0)) slope = -slope * 0.6;
          x = Math.min(W - 2, x + len / 10); y += slope * len / 10 + Math.sin(k * 1.3 + depth) * 0.6;
          st.push([x, y]);
        }
        out.push(st);
        if (depth < 4 && x < W - 40) {
          branch(x, y, Math.max(-0.9, slope - 0.25 - r() * 0.3), depth + 1);
          branch(x, y, Math.min(0.9, slope + 0.25 + r() * 0.3), depth + 1);
        }
      })(8, 110, -0.1, 0);
      return out;
    },
    // twelve strings, each sliding from its own pitch to another, crossing in the middle
    glissandi: function () {
      var out = [];
      for (var k = 0; k < 12; k++) {
        var y0 = 20 + k * 14, y1 = H - 20 - k * 14, st = [];
        for (var i = 0; i <= 10; i++) st.push([20 + i * 32, y0 + (y1 - y0) * i / 10]);
        out.push(st);
      }
      return out;
    },
    // short dashes scattered thickest at the middle, a cloud of points
    cloud: function () {
      var r = rnd(1956), out = [];
      for (var k = 0; k < 90; k++) {
        var x = W / 2 + (r() + r() + r() - 1.5) * W * 0.55, y = H / 2 + (r() + r() + r() - 1.5) * H * 0.6;
        x = Math.max(2, Math.min(W - 8, x)); y = Math.max(2, Math.min(H - 3, y));
        out.push([[x, y], [x + 2 + r() * 4, y]]);
      }
      return out;
    }
  };
  Array.prototype.forEach.call(doc.querySelectorAll('[data-page]'), function (b) {
    b.addEventListener('click', function () { stop(true); strokes = PAGES[b.getAttribute('data-page')](); draw(); say('The page now holds ' + b.textContent + ': ' + plural(strokes.length, 'line') + '.'); });
  });
  $('upic-undo').addEventListener('click', function () { if (strokes.length) { strokes.pop(); draw(); say('The last line is taken off. ' + plural(strokes.length, 'line') + ' on the page.'); } });
  $('upic-clear').addEventListener('click', function () { stop(true); strokes = []; draw(); say('The page is blank.'); });
  lengthIn.addEventListener('input', function () { length = Number(lengthIn.value); lengthOut.textContent = length + ' seconds'; draw(); });

  /* ---------------- punching the page as tape cards ---------------- */
  // each line read at every pulse (a sixteenth at 120 beats a minute) as the nearest note;
  // a note held over several pulses is one card with its length
  function cards() {
    var pulse = 60 / (120 * 4), events = [];
    strokes.forEach(function (st) {
      if (st.length < 2) return;
      var p0 = Math.ceil(st[0][0] / W * length / pulse), p1 = Math.floor(st[st.length - 1][0] / W * length / pulse), i = 1, run = null;
      for (var p = p0; p <= p1; p++) {
        var x = p * pulse / length * W;
        while (i < st.length - 1 && st[i][0] < x) i++;
        var a = st[i - 1], b = st[i], f = b[0] > a[0] ? (x - a[0]) / (b[0] - a[0]) : 1;
        var note = Math.round(midiAt(a[1] + (b[1] - a[1]) * Math.max(0, Math.min(1, f))));
        if (run && run.note === note && run.time + run.len === p) run.len++;
        else { run = { time: p, note: note, len: 1 }; events.push(run); }
      }
    });
    events.sort(function (a, b) { return a.time - b.time || a.note - b.note; });
    function i5(n) { return String(n).padStart(5); }
    return events.slice(0, 999).map(function (e) { return i5(e.time) + i5(e.note) + i5(e.len) + i5(6); });
  }
  $('upic-punch').addEventListener('click', function () {
    var c = cards();
    if (!c.length) { say('The page is blank: there is nothing to punch.'); return; }
    Out.receive(c, 'The UPIC');
    threadBtn.disabled = false;
    say('The page is punched as ' + plural(c.length, 'tape card') + ' into the out tray’s stacker. They can be threaded on the tape player.');
  });
  threadBtn.addEventListener('click', function () { $('stack-tape').click(); });
  Out.onNewStack(function () { threadBtn.disabled = true; });

  Desk.onShow('desk', function () { stop(true); });
  strokes = PAGES.arborescence();
  draw();
  return { stop: stop };
})();
