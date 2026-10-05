/* The pocket game on the bookcase: a handheld console drawn in pixels (200 x 300 of them, each
   a whole number of CSS pixels), its screen 160 x 144 in four shades of green, and on it
   Stack, a game of falling blocks. Seven shapes of four squares fall one at a time into a
   well ten wide and eighteen deep; they are moved, turned and dropped, and a row filled
   from wall to wall is cleared. Every ten rows the level goes up and the blocks fall faster.
   The next shape shows beside the well; the score is the handheld's own (40, 100, 300 or 1200
   points for one to four rows at once, times the level and one, a point a row for a soft
   drop and two for a hard one), and the best of the session is kept until the page closes.

   Keys: the arrows move (Down drops faster, Up turns), X turns clockwise, Z back, Space drops
   at once, Enter is Start (begin, pause), M is Select (the music off and on). The console's
   own buttons can be pressed with the pointer. The music is Rimsky-Korsakov's Flight of the
   Bumblebee on square waves over a triangle bass; it and the effects sound only while Room
   sounds is on. Leaving the console pauses the game. Needs Desk (desk.js). */

(function () {
  'use strict';
  var doc = document, station = doc.querySelector('.st-console');
  if (!station) return;
  var canvas = doc.getElementById('gb-canvas'), g = canvas.getContext('2d'), gb = station.querySelector('.gb');
  var statusEl = doc.getElementById('gb-status');
  var W = 200, H = 300, SX = 20, SY = 22;                    // the console, and its screen's corner
  var S = ['#9bbc0f', '#8bac0f', '#306230', '#0f380f'];        // the screen's four shades, light to dark

  /* ---------------- drawing in pixels ---------------- */
  function rect(c, x, y, w, h, col) { c.fillStyle = col; c.fillRect(x, y, w, h); }
  function disc(c, cx, cy, r, col) {
    c.fillStyle = col;
    for (var y = -r; y <= r; y++) { var hw = Math.floor(Math.sqrt(r * r - y * y) + 0.3); c.fillRect(cx - hw, cy + y, hw * 2 + 1, 1); }
  }
  // a 5 x 7 face for the screen and the case, a row of five bits to each line
  var FONT = {
    A: '0e11111f111111', B: '1e11111e11111e', C: '0e11101010110e', D: '1e11111111111e', E: '1f10101e10101f', F: '1f10101e101010',
    G: '0e11101711110f', H: '1111111f111111', I: '0e04040404040e', J: '07020202021206', K: '11121418141211', L: '1010101010101f',
    M: '111b1515111111', N: '11111915131111', O: '0e11111111110e', P: '1e11111e101010', Q: '0e11111115120d', R: '1e11111e141211',
    S: '0f10100e01011e', T: '1f040404040404', U: '1111111111110e', V: '11111111110a04', W: '11111115151515', X: '11110a040a1111',
    Y: '11110a04040404', Z: '1f01020408101f', 0: '0e11131519110e', 1: '040c040404040e', 2: '0e11010204081f', 3: '1f02040201110e',
    4: '02060a121f0202', 5: '1f101e0101110e', 6: '0608101e11110e', 7: '1f010204080808', 8: '0e11110e11110e', 9: '0e11110f01020c',
    '-': '0000001f000000', '.': '0000000000000c', ' ': '00000000000000'
  };
  function text(c, s, x, y, col, k) {
    k = k || 1; c.fillStyle = col;
    String(s).toUpperCase().split('').forEach(function (ch, i) {
      var f = FONT[ch] || FONT[' '];
      for (var r = 0; r < 7; r++) {
        var bits = parseInt(f.substr(r * 2, 2), 16);
        for (var b = 0; b < 5; b++) if (bits & (16 >> b)) c.fillRect(x + (i * 6 + b) * k, y + r * k, k, k);
      }
    });
  }
  function textW(s, k) { return (String(s).length * 6 - 1) * (k || 1); }

  /* ---------------- the console ---------------- */
  var CASE = '#c9c7bf', CASE_L = '#e4e2da', CASE_D = '#98968f', BEZEL = '#55566b', NAVY = '#2c3270', INK = '#26262c', BERRY = '#9c2456';
  var DPAD = { cx: 44, cy: 236 }, A = { cx: 172, cy: 230 }, B = { cx: 142, cy: 246 }, SEL = { x: 66, y: 272 }, STA = { x: 108, y: 272 };
  var body = doc.createElement('canvas'); body.width = W; body.height = H;
  (function drawBody() {
    var c = body.getContext('2d');
    // the case, its foot's right-hand corner rounded, as the handhelds' were
    for (var y = 0; y < H; y++) {
      var cut = y > H - 34 ? Math.ceil(34 - Math.sqrt(Math.max(0, 34 * 34 - Math.pow(y - (H - 34), 2)))) : 0;
      rect(c, 0, y, W - cut, 1, CASE);
      rect(c, W - cut - 1, y, 1, 1, CASE_D);
    }
    rect(c, 0, 0, W, 1, CASE_L); rect(c, 0, 0, 1, H, CASE_L); rect(c, 0, H - 1, W - 34, 1, CASE_D);
    rect(c, 0, 9, W, 1, CASE_D); rect(c, 0, 10, W, 1, CASE_L);
    text(c, 'OFF', 14, 1, CASE_D); text(c, 'ON', 38, 1, CASE_D);
    // the bezel, a corner of it rounded too, the screen in it, the battery lamp at its left
    for (var j = 0; j < 163; j++) {
      var cu = j > 163 - 14 ? Math.ceil(14 - Math.sqrt(Math.max(0, 196 - Math.pow(j - 149, 2)))) : 0;
      rect(c, 8, 15 + j, 184 - cu, 1, BEZEL);
    }
    rect(c, SX - 1, SY - 1, 162, 146, '#3a3b4a');
    disc(c, 13, 70, 2, '#e04848'); rect(c, 12, 69, 1, 1, '#ff9a9a');
    text(c, 'STACK', 100 - textW('STACK') / 2, 169, '#9a9bb0');
    // the maker's name on the case
    text(c, 'POCKET', 14, 186, NAVY, 2); rect(c, 88, 197, 28, 2, NAVY);
    // the speaker's grille: six slots on the slant
    for (var k = 0; k < 6; k++) for (var t = 0; t < 26; t++) rect(c, 150 + k * 7 + Math.floor(t / 2), 290 - t, 2, 1, CASE_D);
    text(c, 'B', B.cx - 2, B.cy + 15, NAVY); text(c, 'A', A.cx - 2, A.cy + 15, NAVY);
    text(c, 'SELECT', SEL.x + 12 - textW('SELECT') / 2, SEL.y + 10, NAVY); text(c, 'START', STA.x + 12 - textW('START') / 2, STA.y + 10, NAVY);
  })();
  // the buttons, drawn up or pressed in
  var pressed = {};
  function buttons(c) {
    var dp = pressed.left || pressed.right || pressed.up || pressed.down;
    rect(c, DPAD.cx - 18, DPAD.cy - 6, 37, 13, '#18181c'); rect(c, DPAD.cx - 6, DPAD.cy - 18, 13, 37, '#18181c');
    rect(c, DPAD.cx - 17, DPAD.cy - 5, 35, 11, INK); rect(c, DPAD.cx - 5, DPAD.cy - 17, 11, 35, INK);
    var hi = '#4a4a54';
    if (!pressed.left) rect(c, DPAD.cx - 16, DPAD.cy - 4, 8, 1, hi);
    if (!pressed.up) rect(c, DPAD.cx - 4, DPAD.cy - 16, 1, 8, hi);
    if (!pressed.right) rect(c, DPAD.cx + 9, DPAD.cy - 4, 8, 1, hi);
    if (!pressed.down) rect(c, DPAD.cx - 4, DPAD.cy + 9, 1, 8, hi);
    disc(c, DPAD.cx, DPAD.cy, 3, dp ? '#101012' : '#202026');
    [[B, pressed.b], [A, pressed.a]].forEach(function (p) {
      var o = p[0], down = p[1];
      disc(c, o.cx + 1, o.cy + 2, 11, '#6a1a3c');
      disc(c, o.cx + (down ? 1 : 0), o.cy + (down ? 1 : 0), 11, down ? '#841d4a' : BERRY);
      if (!down) { rect(c, o.cx - 6, o.cy - 7, 4, 1, '#c95a88'); rect(c, o.cx - 7, o.cy - 6, 1, 3, '#c95a88'); }
    });
    [[SEL, pressed.select], [STA, pressed.start]].forEach(function (p) {
      var o = p[0];
      rect(c, o.x + 1, o.y, 22, 6, '#7a7a80'); rect(c, o.x, o.y + 1, 24, 4, '#7a7a80');
      rect(c, o.x + 2, o.y + 1, 20, 4, p[1] ? '#56565c' : '#8e8e96');
    });
  }

  /* ---------------- the game ---------------- */
  var COLS = 10, ROWS = 20, HIDDEN = 2;                     // two rows above the well, where shapes appear
  var SHAPES = [
    [[0, 0, 0, 0], [1, 1, 1, 1], [0, 0, 0, 0], [0, 0, 0, 0]],   // I
    [[1, 1], [1, 1]],                                           // O
    [[0, 1, 0], [1, 1, 1], [0, 0, 0]],                          // T
    [[0, 1, 1], [1, 1, 0], [0, 0, 0]],                          // S
    [[1, 1, 0], [0, 1, 1], [0, 0, 0]],                          // Z
    [[1, 0, 0], [1, 1, 1], [0, 0, 0]],                          // J
    [[0, 0, 1], [1, 1, 1], [0, 0, 0]]                           // L
  ];
  // frames a row at each level, at the handheld's 59.7 frames a second
  var FALL = [53, 49, 45, 41, 37, 33, 28, 22, 17, 11, 10, 9, 8, 7, 6, 6, 5, 5, 4, 4, 3];
  var POINTS = [0, 40, 100, 300, 1200];
  var well, piece, next, bag, score, lines, level, best = 0, mode = 'title', fallAt = 0, clearing = null, overRows = 0, overAt = 0;

  function rot(m) { var n = m.length, o = []; for (var y = 0; y < n; y++) { o.push([]); for (var x = 0; x < n; x++) o[y].push(m[n - 1 - x][y]); } return o; }
  function draw7() { if (!bag || !bag.length) { bag = [0, 1, 2, 3, 4, 5, 6]; for (var i = 6; i > 0; i--) { var j = Math.floor(Math.random() * (i + 1)), t = bag[i]; bag[i] = bag[j]; bag[j] = t; } } return bag.pop(); }
  function spawn() {
    var k = next === undefined ? draw7() : next; next = draw7();
    var m = SHAPES[k];
    piece = { k: k, m: m, x: Math.floor((COLS - m.length) / 2), y: k === 0 ? HIDDEN - 1 : HIDDEN };
    if (hits(piece.m, piece.x, piece.y)) gameOver();
  }
  function hits(m, px, py) {
    for (var y = 0; y < m.length; y++) for (var x = 0; x < m.length; x++) {
      if (!m[y][x]) continue;
      var X = px + x, Y = py + y;
      if (X < 0 || X >= COLS || Y >= ROWS || (Y >= 0 && well[Y][X] >= 0)) return true;
    }
    return false;
  }
  function move(dx, dy) {
    if (hits(piece.m, piece.x + dx, piece.y + dy)) return false;
    piece.x += dx; piece.y += dy; return true;
  }
  function turn(dir) {
    if (piece.k === 1) return;
    var m = piece.m; m = dir > 0 ? rot(m) : rot(rot(rot(m)));
    // off a wall or the stack: along a column or two, or up one
    var kicks = [[0, 0], [-1, 0], [1, 0], [-2, 0], [2, 0], [0, -1]];
    for (var i = 0; i < kicks.length; i++) {
      if (!hits(m, piece.x + kicks[i][0], piece.y + kicks[i][1])) { piece.m = m; piece.x += kicks[i][0]; piece.y += kicks[i][1]; sfx('turn'); return; }
    }
  }
  function lock() {
    var m = piece.m;
    for (var y = 0; y < m.length; y++) for (var x = 0; x < m.length; x++) if (m[y][x] && piece.y + y >= 0) well[piece.y + y][piece.x + x] = piece.k;
    var full = [];
    for (var r = 0; r < ROWS; r++) if (well[r].every(function (v) { return v >= 0; })) full.push(r);
    piece = null;
    if (full.length) { clearing = { rows: full, t: now() }; sfx(full.length === 4 ? 'four' : 'clear'); }
    else { sfx('lock'); spawn(); }
  }
  function clearRows() {
    var n = clearing.rows.length;
    clearing.rows.forEach(function (r) { well.splice(r, 1); well.unshift(row()); });
    clearing = null;
    var was = level;
    lines += n; score += POINTS[n] * (level + 1);
    level = Math.max(level, Math.floor(lines / 10));
    if (level > was) { sfx('level'); say('Level ' + level + '.'); }
    spawn();
  }
  function row() { var r = []; for (var x = 0; x < COLS; x++) r.push(-1); return r; }
  function begin() {
    well = []; for (var r = 0; r < ROWS; r++) well.push(row());
    score = 0; lines = 0; level = 0; bag = null; next = undefined; clearing = null;
    mode = 'play'; spawn(); fallAt = now(); music(true);
    say('A new game. Level 0.');
  }
  function gameOver() {
    mode = 'over'; overRows = 0; overAt = now(); piece = null; music(false); sfx('over');
    if (score > best) best = score;
    say('Game over: ' + score + ' points, ' + lines + ' rows. The best this session is ' + best + '. Press Start to play again.');
  }
  function pause(on) {
    if (mode !== 'play' && mode !== 'pause') return;
    mode = on ? 'pause' : 'play'; music(!on); fallAt = now();
    sfx('pause'); say(on ? 'Paused.' : 'Playing.');
  }
  function drop() { var n = 0; while (move(0, 1)) n++; score += n * 2; lock(); }
  function speed() { return FALL[Math.min(level, FALL.length - 1)] * 1000 / 59.7; }

  /* ---------------- the controls ---------------- */
  var held = {}, REPEAT = 50, DELAY = 170, SOFT = 33;
  function press(k) {
    if (pressed[k]) return;
    pressed[k] = true; held[k] = now();
    if (k === 'start') { if (mode === 'title' || mode === 'over') { if (mode !== 'over' || overRows >= ROWS - HIDDEN) begin(); } else pause(mode === 'play'); return; }
    if (k === 'select') { musicOn = !musicOn; music(mode === 'play'); say(musicOn ? 'Music on.' : 'Music off.'); return; }
    if (mode !== 'play' || !piece || clearing) return;
    if (k === 'left' || k === 'right') { if (move(k === 'left' ? -1 : 1, 0)) sfx('move'); held[k + 'At'] = now() + DELAY; }
    else if (k === 'down') { if (move(0, 1)) { score++; fallAt = now(); } else lock(); held.downAt = now() + SOFT; }
    else if (k === 'up' || k === 'a') turn(1);
    else if (k === 'b') turn(-1);
    else if (k === 'drop') drop();
  }
  function release(k) { pressed[k] = false; delete held[k]; }
  function repeat(t) {
    if (mode !== 'play' || !piece || clearing) return;
    ['left', 'right'].forEach(function (k) {
      if (pressed[k] && t >= held[k + 'At']) { if (move(k === 'left' ? -1 : 1, 0)) sfx('move'); held[k + 'At'] = t + REPEAT; }
    });
    if (pressed.down && t >= held.downAt) { if (move(0, 1)) { score++; fallAt = t; } else lock(); held.downAt = t + SOFT; }
  }
  var KEYS = { ArrowLeft: 'left', ArrowRight: 'right', ArrowDown: 'down', ArrowUp: 'up', x: 'a', X: 'a', z: 'b', Z: 'b', ' ': 'drop', Enter: 'start', m: 'select', M: 'select' };
  // the keys are the game's while the console is in front, unless the focus is on a link, a
  // button or a field of the page's own (the menu, Put it back)
  function mine(e) {
    var a = doc.activeElement;
    if (Desk.current() !== 'console' || e.altKey || e.ctrlKey || e.metaKey) return false;
    if (a && a !== doc.body && !station.contains(a)) return false;
    return !(a && a.matches('a, button, input, select, textarea'));
  }
  gb.addEventListener('pointerdown', function () { gb.focus({ preventScroll: true }); });
  doc.addEventListener('keydown', function (e) {
    var k = KEYS[e.key];
    if (!k || !mine(e)) return;
    e.preventDefault();
    if (!e.repeat) press(k);
  });
  doc.addEventListener('keyup', function (e) { var k = KEYS[e.key]; if (k) release(k); });
  Array.prototype.forEach.call(station.querySelectorAll('.gb-key'), function (b) {
    var k = b.getAttribute('data-key');
    b.addEventListener('pointerdown', function (e) { e.preventDefault(); gb.focus({ preventScroll: true }); try { b.setPointerCapture(e.pointerId); } catch (err) { /* synthetic */ } press(k); });
    ['pointerup', 'pointercancel', 'lostpointercapture'].forEach(function (n) { b.addEventListener(n, function () { release(k); }); });
  });

  /* ---------------- the screen ---------------- */
  var TILE = [];
  // each shape's square in its own pattern of the four shades, as the handheld drew them
  [function (c) { rect(c, 0, 0, 8, 8, S[3]); rect(c, 1, 1, 6, 6, S[1]); rect(c, 1, 1, 2, 1, S[0]); },
   function (c) { rect(c, 0, 0, 8, 8, S[3]); rect(c, 1, 1, 6, 6, S[0]); rect(c, 2, 2, 4, 4, S[2]); },
   function (c) { rect(c, 0, 0, 8, 8, S[3]); rect(c, 1, 1, 6, 6, S[2]); rect(c, 1, 1, 5, 1, S[1]); rect(c, 1, 1, 1, 5, S[1]); },
   function (c) { rect(c, 0, 0, 8, 8, S[3]); rect(c, 1, 1, 6, 6, S[1]); for (var i = 0; i < 6; i++) for (var j = 0; j < 6; j++) if ((i + j) % 2) rect(c, 1 + i, 1 + j, 1, 1, S[2]); },
   function (c) { rect(c, 0, 0, 8, 8, S[3]); rect(c, 2, 2, 4, 4, S[1]); },
   function (c) { rect(c, 0, 0, 8, 8, S[3]); rect(c, 1, 1, 6, 6, S[2]); rect(c, 3, 3, 2, 2, S[0]); },
   function (c) { rect(c, 0, 0, 8, 8, S[3]); rect(c, 1, 1, 6, 6, S[0]); rect(c, 3, 3, 2, 2, S[3]); }
  ].forEach(function (fn) { var t = doc.createElement('canvas'); t.width = t.height = 8; fn(t.getContext('2d')); TILE.push(t); });
  var WALL = doc.createElement('canvas'); WALL.width = 8; WALL.height = 8;
  (function () { var c = WALL.getContext('2d'); rect(c, 0, 0, 8, 8, S[2]); rect(c, 0, 3, 8, 1, S[3]); rect(c, 0, 7, 8, 1, S[3]); rect(c, 3, 0, 1, 3, S[3]); rect(c, 7, 4, 1, 3, S[3]); })();

  function cell(c, k, x, y) { c.drawImage(TILE[k], SX + x, SY + y); }
  function box(c, x, y, w, h) { rect(c, SX + x, SY + y, w, h, S[3]); rect(c, SX + x + 1, SY + y + 1, w - 2, h - 2, S[0]); }
  function label(c, s, x, y) { text(c, s, SX + x, SY + y, S[3]); }
  function screen(c, t) {
    rect(c, SX, SY, 160, 144, S[0]);
    if (mode === 'title') {
      for (var y = 0; y < 144; y += 8) { c.drawImage(WALL, SX, SY + y); c.drawImage(WALL, SX + 152, SY + y); }
      text(c, 'STACK', SX + 80 - textW('STACK', 3) / 2, SY + 18, S[3], 3);
      label(c, 'FALLING BLOCKS', 80 - textW('FALLING BLOCKS') / 2, 46);
      [[2, 26, 64], [0, 50, 72], [5, 92, 64], [1, 114, 64]].forEach(function (p) {
        var m = SHAPES[p[0]];
        for (var yy = 0; yy < m.length; yy++) for (var xx = 0; xx < m.length; xx++) if (m[yy][xx]) cell(c, p[0], p[1] + xx * 8, p[2] + yy * 8);
      });
      if (Math.floor(t / 530) % 2 === 0) label(c, 'PRESS START', 80 - textW('PRESS START') / 2, 104);
      label(c, 'HI ' + pad(best), 80 - textW('HI 000000') / 2, 122);
      return;
    }
    for (var r = 0; r < 18; r++) { c.drawImage(WALL, SX + 8, SY + r * 8); c.drawImage(WALL, SX + 96, SY + r * 8); }
    rect(c, SX, SY, 8, 144, S[1]);
    // the well: hidden while paused, as the handheld hid it
    if (mode === 'pause') label(c, 'PAUSE', 56 - textW('PAUSE') / 2, 68);
    else {
      var flash = clearing && Math.floor((t - clearing.t) / 90) % 2 === 0;
      for (var y2 = HIDDEN; y2 < ROWS; y2++) for (var x2 = 0; x2 < COLS; x2++) {
        var v = well[y2][x2];
        if (v < 0) continue;
        if (clearing && clearing.rows.indexOf(y2) >= 0) { if (flash) rect(c, SX + 16 + x2 * 8, SY + (y2 - HIDDEN) * 8, 8, 8, S[2]); else cell(c, v, 16 + x2 * 8, (y2 - HIDDEN) * 8); }
        else cell(c, v, 16 + x2 * 8, (y2 - HIDDEN) * 8);
      }
      if (piece) {
        var m = piece.m;
        for (var py = 0; py < m.length; py++) for (var px = 0; px < m.length; px++)
          if (m[py][px] && piece.y + py >= HIDDEN) cell(c, piece.k, 16 + (piece.x + px) * 8, (piece.y + py - HIDDEN) * 8);
      }
      if (mode === 'over') {
        for (var k = 0; k < overRows; k++) for (var x3 = 0; x3 < COLS; x3++) c.drawImage(WALL, SX + 16 + x3 * 8, SY + 136 - k * 8);
        if (overRows >= ROWS - HIDDEN) {
          box(c, 22, 44, 68, 40); label(c, 'GAME', 56 - textW('GAME') / 2, 51); label(c, 'OVER', 56 - textW('OVER') / 2, 61);
          if (Math.floor(t / 530) % 2 === 0) { box(c, 18, 96, 76, 14); label(c, 'PRESS START', 56 - textW('PRESS START') / 2, 99); }
        }
      }
    }
    // the panel: score, level, rows, and the shape to come
    box(c, 104, 4, 54, 30); label(c, 'SCORE', 109, 8); label(c, pad(score), 155 - textW('000000'), 22);
    box(c, 104, 40, 54, 24); label(c, 'LEVEL', 109, 43); label(c, level, 155 - textW(String(level)), 53);
    box(c, 104, 70, 54, 24); label(c, 'LINES', 109, 73); label(c, lines, 155 - textW(String(lines)), 83);
    box(c, 110, 100, 42, 40);
    if (next !== undefined && mode !== 'pause') {
      var n = SHAPES[next], w = n[0].length, ox = 131 - w * 4, oy = next === 0 ? 112 : 112 + 4;
      for (var ny = 0; ny < n.length; ny++) for (var nx = 0; nx < n.length; nx++) if (n[ny][nx]) cell(c, next, ox + nx * 8, oy + ny * 8 - (next === 0 ? 4 : 0));
    }
  }
  function pad(n) { n = String(Math.min(999999, n)); while (n.length < 6) n = '0' + n; return n; }

  /* ---------------- the loop ---------------- */
  function now() { return performance.now(); }
  var frame = null;
  function tick(t) {
    frame = null;
    if (Desk.current() !== 'console') return;
    if (mode === 'play') {
      if (clearing) { if (t - clearing.t > 540) clearRows(); }
      else if (piece) {
        repeat(t);
        if (piece && !pressed.down && t - fallAt >= speed()) { fallAt = t; if (!move(0, 1)) lock(); }
      }
    } else if (mode === 'over' && overRows < ROWS - HIDDEN && t - overAt > 40) { overRows++; overAt = t; }
    g.drawImage(body, 0, 0);
    screen(g, t);
    buttons(g);
    frame = requestAnimationFrame(tick);
  }
  function run() { if (!frame) frame = requestAnimationFrame(tick); }

  /* ---------------- the console's size: whole CSS pixels to its pixel, as large as fits ---------------- */
  function fit() {
    var box = gb.parentNode.getBoundingClientRect(), avail = station.clientHeight - 90;
    // an even number of CSS pixels to its pixel, so they are whole multiples of the page's type
    var s = Math.max(2, Math.floor(Math.min(box.width / W, avail / H) / 2) * 2);
    gb.style.setProperty('--gs', s + 'px');
  }
  if (window.ResizeObserver) new ResizeObserver(fit).observe(station);

  Desk.onShow('console', function () { fit(); run(); });
  // put down, the game pauses and the music stops
  new MutationObserver(function () {
    if (Desk.current() === 'console') return;
    if (mode === 'play') pause(true);
    music(false);
    Object.keys(pressed).forEach(release);
  }).observe(doc.getElementById('desk'), { attributes: true, attributeFilter: ['data-at'] });

  function say(m) { statusEl.textContent = ''; setTimeout(function () { statusEl.textContent = m; }, 30); }

  /* ---------------- the sound: square waves, as the handheld's chip made ---------------- */
  var ac = null, out = null, musicOn = true, song = null;
  function soundOn() { var b = doc.getElementById('sound-btn'); return !b || b.getAttribute('aria-pressed') !== 'false'; }
  function ctx() {
    if (!soundOn()) return null;
    if (!ac) {
      var AC = window.AudioContext || window.webkitAudioContext;
      if (!AC) return null;
      ac = new AC(); out = ac.createGain(); out.gain.value = 0.12; out.connect(ac.destination);
    }
    if (ac.state === 'suspended') ac.resume();
    return ac;
  }
  function note(t, hz, dur, vol, type, to) {
    var o = ac.createOscillator(), v = ac.createGain();
    o.type = type || 'square'; o.frequency.setValueAtTime(hz, t);
    if (to) o.frequency.exponentialRampToValueAtTime(to, t + dur);
    v.gain.setValueAtTime(vol, t); v.gain.setValueAtTime(vol, t + dur * 0.7); v.gain.exponentialRampToValueAtTime(0.0001, t + dur);
    o.connect(v); v.connect(out); o.start(t); o.stop(t + dur + 0.02);
  }
  function sfx(name) {
    if (!ctx()) return;
    var t = ac.currentTime + 0.005;
    ({ move: function () { note(t, 1800, 0.02, 0.25); },
       turn: function () { note(t, 900, 0.03, 0.3); note(t + 0.03, 1400, 0.03, 0.3); },
       lock: function () { note(t, 160, 0.06, 0.5, 'square', 90); },
       clear: function () { [523, 659, 784, 1047].forEach(function (f, i) { note(t + i * 0.06, f, 0.07, 0.35); }); },
       four: function () { [523, 659, 784, 1047, 784, 1047, 1319].forEach(function (f, i) { note(t + i * 0.06, f, 0.08, 0.4); }); },
       level: function () { [784, 988, 1175, 1568].forEach(function (f, i) { note(t + i * 0.08, f, 0.1, 0.35); }); },
       pause: function () { note(t, 1047, 0.05, 0.3); note(t + 0.07, 1568, 0.08, 0.3); },
       over: function () { [392, 370, 349, 330, 311, 294].forEach(function (f, i) { note(t + i * 0.14, f, 0.16, 0.4, 'triangle'); }); }
    })[name]();
  }
  // the music: Rimsky-Korsakov's Flight of the Bumblebee (from The Tale of Tsar Saltan,
  // 1899-1900), its chromatic theme in sixteenths, each half-bar a group of eight (semitones
  // from A4, an octave up, as a chip's lead plays it); under it a bass of quarters on each
  // half-bar's root, low and an octave up
  var THEME = [
    [7, 6, 5, 4, 5, 4, 3, 2], [3, 2, 1, 0, -1, -2, -3, -4], [-5, -6, -7, -8, -9, -4, -5, -6], [-5, -6, -7, -8, -9, -8, -7, -6],
    [-5, -6, -7, -8, -7, -8, -9, -10], [-9, -8, -7, -6, -5, -4, -5, -6], [-5, -6, -7, -8, -9, -4, -5, -6], [-5, -6, -7, -8, -9, -8, -7, -6],
    [-5, -4, -5, -6, -5, -4, -5, -6], [-5, -4, -3, -2, -1, 0, 1, 2], [3, 2, 1, 0, -1, 0, 1, 2], [3, 4, 5, 6, 7, 6, 5, 4]];
  var ROOTS = [-24, -24, -29, -29, -24, -19, -29, -29, -24, -24, -29, -29];
  var TUNE = [], BASS = [];
  THEME.forEach(function (g) { g.forEach(function (n) { TUNE.push(n + 12); }); });
  ROOTS.forEach(function (r) { BASS.push(r, r + 12); });
  function hz(n) { return 440 * Math.pow(2, n / 12); }
  function music(on) {
    if (song) { clearInterval(song.timer); song = null; }
    if (!on || !musicOn || !ctx()) return;
    var step = 0.09 * Math.pow(0.97, Math.min(level || 0, 10));      // a sixteenth, quicker with the level
    song = { at: ac.currentTime + 0.05, i: 0, b: 0, bt: ac.currentTime + 0.05 };
    function plan() {
      if (!soundOn()) return;
      while (song.at < ac.currentTime + 0.4) {
        note(song.at, hz(TUNE[song.i % TUNE.length]), step * 0.85, 0.2);
        song.at += step; song.i++;
      }
      while (song.bt < ac.currentTime + 0.4) {
        note(song.bt, hz(BASS[song.b % BASS.length]), step * 3, 0.28, 'triangle');
        song.bt += step * 4; song.b++;
      }
    }
    plan(); song.timer = setInterval(plan, 120);
  }
})();
