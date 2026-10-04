/* Two small applications on the desk: the Calculator, a desk accessory, and Crible, a game
   of sieves. The engine is used read-only (Fortran.punches, for the Calculator's card) and
   sound through Tape. Needs Desk (wm.js), Fortran and Tape. */

/* ================================================================ the Calculator */
// Immediate execution, as the desk accessory worked: each operator applies the one before
// it. The arithmetic is single precision (Math.fround), as a FORTRAN REAL on the 704 was
// about seven digits; a result too big for a REAL, or a division by zero, fills the display
// with asterisks, as FORMAT fills a field that a number does not fit. The display is
// punched, column by column, on a short card under it, with the 029's codes.
var Calculator = (function () {
  'use strict';
  var doc = document, $ = Desk.$, $$ = Desk.$$;
  var COLS = 27, REAL_MAX = 3.4028235e38, MAX_ENTRY = 12;
  var acc = null, op = null, entry = null, again = null, err = null, eMode = false;
  var w = $('win-calc'), out = $('calc-out');

  var f32 = Math.fround;
  function apply(a, o, b) {
    if (o === '+') return f32(a + b);
    if (o === '-') return f32(a - b);
    if (o === '*') return f32(a * b);
    if (o === '/') return b === 0 ? NaN : f32(a / b);
    return f32(Math.pow(a, b));
  }
  // seven significant digits, as a REAL holds; E notation as FORTRAN's E14.7 prints it
  function fmtE(x) {
    if (x === 0) return '0.0000000E+00';
    var e = Math.floor(Math.log10(Math.abs(x))) + 1, m = Math.abs(x) / Math.pow(10, e);
    var d = Math.round(m * 1e7);
    if (d >= 1e7) { d = Math.round(d / 10); e++; }
    if (d < 1e6) { d *= 10; e--; }
    return (x < 0 ? '-' : '') + '0.' + String(d) + 'E' + (e < 0 ? '-' : '+') + (Math.abs(e) < 10 ? '0' : '') + Math.abs(e);
  }
  function fmtF(x) {
    var a = Math.abs(x);
    if (a !== 0 && (a >= 1e10 || a < 1e-6)) return fmtE(x);
    var s = x.toPrecision(7);
    if (s.indexOf('e') >= 0) return fmtE(x);
    if (s.indexOf('.') >= 0) s = s.replace(/0+$/, '').replace(/\.$/, '.');
    return s;
  }
  function shown() {
    if (err) return '*************';
    if (entry !== null) return entry;
    var v = acc === null ? 0 : acc;
    return eMode ? fmtE(v) : fmtF(v);
  }
  function opText(o) { return { '+': '+', '-': '-', '*': '*', '/': '/', '**': '**' }[o]; }

  function render() {
    var s = shown();
    out.textContent = s;
    $('calc-st').textContent = op && acc !== null ? (eMode ? fmtE(acc) : fmtF(acc)) + ' ' + opText(op) : ' ';
    punch(s);
  }
  function note(msg) { $('calc-note').textContent = msg; }

  function key(k) {
    if (err && k !== 'C') { if (/^[0-9.]$/.test(k) || k === 'E') clear(); else return; }
    if (/^[0-9]$/.test(k) || k === '.') {
      if (entry === null) { entry = k === '.' ? '0.' : k; if (!op) acc = null; }
      else if (k === '.' && entry.indexOf('.') >= 0) return;
      else if (entry.replace(/[-.]/g, '').length >= MAX_ENTRY - 2) { note('An entry holds at most ten digits.'); return; }
      else entry = entry === '0' && k !== '.' ? k : entry + k;
    } else if (k === 'BS') {
      if (entry === null) return;
      entry = entry.slice(0, -1);
      if (entry === '' || entry === '-') entry = null;
    } else if (k === 'C') clear();
    else if (k === 'E') { if (entry !== null) entry = null; else if (!op) clear(); }
    else if (k === '=') {
      if (op) {
        var b = entry !== null ? +entry : acc;
        again = { op: op, b: b };
        result(apply(acc, op, b));
        op = null;
      } else if (again && entry === null && acc !== null) result(apply(acc, again.op, again.b));
      else if (entry !== null) result(f32(+entry));
    } else {   // an operator
      if (entry !== null) {
        if (op) { result(apply(acc, op, +entry)); if (err) { render(); return; } }
        else acc = f32(+entry);
        entry = null;
      } else if (acc === null) acc = 0;
      op = k;
    }
    render();
  }
  function result(v) {
    entry = null;
    if (!isFinite(v) || Math.abs(v) > REAL_MAX) {
      err = v !== v ? 'That has no value as a REAL: a division by zero, or a power of a negative number. C clears it.' : 'The result is too large for a REAL, whose limit is about 3.4E+38. C clears it.';
      note(err); acc = null; op = null;
      return;
    }
    acc = v;
    note(eMode ? 'Results in E notation, as FORMAT (E14.7) prints them.' : 'Single precision, as a FORTRAN REAL.');
  }
  function clear() { acc = null; op = null; entry = null; again = null; err = null; note(eMode ? 'Cleared. Results in E notation.' : 'Cleared.'); }

  // the display, punched from column 1 on a short card drawn as SVG: a slot for each hole,
  // rows 6 units apart, and a point where a digit row is not punched, as the card prints them
  var ROWS = [12, 11, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9], CW = 7.5, RH = 6;
  function punch(s) {
    var c = $('calc-holes'), W = 4 + CW * COLS + 6, H = 4 + 12 * RH + 2;
    c.setAttribute('viewBox', '0 0 ' + W + ' ' + H); c.setAttribute('width', W); c.setAttribute('height', H);
    var slots = '', dots = '';
    for (var col = 0; col < COLS; col++) {
      var rows = col < s.length ? Fortran.punches(s.charAt(col)) : [];
      ROWS.forEach(function (r, j) {
        var x = 4 + CW * col + CW / 2, y = 4 + RH * j;
        if (rows.indexOf(r) >= 0) slots += 'M' + x + ' ' + (y + 1) + 'v3.4';
        else if (j >= 2) dots += 'M' + x + ' ' + (y + 2.7) + 'h0';
      });
    }
    // the card, its top right corner cut at 45 degrees
    c.innerHTML = '<path class="cc-card" d="M.5 .5H' + (W - 6) + 'L' + (W - .5) + ' 6V' + (H - .5) + 'H.5z"/>' +
      '<path class="cc-dots" d="' + dots + '"/><path class="cc-slots" d="' + slots + '"/>';
    $('calc-print').textContent = s.slice(0, COLS);
  }

  // a key typed is shown pressed on the keypad for a moment
  function flash(k) {
    var b = w.querySelector('[data-key="' + (k === 'BS' ? 'E' : k) + '"]');
    if (!b) return;
    b.classList.add('hit');
    setTimeout(function () { b.classList.remove('hit'); }, 120);
  }
  w.addEventListener('click', function (e) { var b = e.target.closest('[data-key]'); if (b) key(b.getAttribute('data-key')); });
  w.addEventListener('keydown', function (e) {
    if (e.metaKey || e.ctrlKey || e.altKey || (e.key === 'Enter' && e.target.id === 'calc-e')) return;
    var k = e.key;
    if (k === ',') k = '.';
    if (k === '^') k = '**';
    if (k === 'Enter') k = '=';
    if (k === 'Backspace') k = 'BS';
    if (k === 'Delete') k = 'E';
    if (k === 'c' || k === 'C') k = 'C';
    // Space still presses the key in focus
    if (!/^([0-9.+\-*\/=CE]|\*\*|BS)$/.test(k) || (k === 'E' && e.key !== 'Delete')) return;
    e.preventDefault();
    flash(k); key(k);
  });
  $('calc-e').addEventListener('click', function () {
    eMode = !eMode;
    this.setAttribute('aria-pressed', String(eMode));
    if (entry === null && !err) note(eMode ? 'Results in E notation, as FORMAT (E14.7) prints them.' : 'Results in plain figures, as FORMAT (F) prints them, up to seven digits.');
    render();
  });
  // Escape clears first, and closes the window only when there is nothing to clear
  Desk.onEscape(function (e) {
    if (!w.contains(e.target) || (acc === null && entry === null && !op && !err)) return false;
    clear(); render();
    return true;
  });
  render();
  return { key: key, value: shown };
})();

/* ================================================================ Crible */
// A target sieve over the numbers 0 to 47, twelve to a row, is made of one to three
// residue classes; the player rebuilds it by adding classes. Each target is checked to
// need every class it was made of (no smaller union of classes up to modulus 9 gives it),
// so the count it was made with is the par. Play sounds a sieve as a rhythm, one pulse to
// a number, through Tape.
var Crible = (function () {
  'use strict';
  var doc = document, $ = Desk.$, $$ = Desk.$$, el = Desk.el, plural = Desk.plural;
  var N = 48, ROW = 12, MODS = [2, 3, 4, 5, 6, 7, 8, 9];
  var level = 0, target = [], targetSet = null, mine = [], mod = 3, hints = 0, solved = false, cur = 0;

  function cls(m, s) { var a = []; for (var n = s; n < N; n += m) a.push(n); return a; }
  function setOf(classes) { var on = new Uint8Array(N); classes.forEach(function (c) { cls(c[0], c[1]).forEach(function (n) { on[n] = 1; }); }); return on; }
  function same(a, b) { for (var i = 0; i < N; i++) if (a[i] !== b[i]) return false; return true; }
  function count(a) { var k = 0; for (var i = 0; i < N; i++) k += a[i]; return k; }
  function name(c) { return c[0] + '@' + c[1]; }
  function formula(classes) { return classes.length ? classes.slice().sort(function (a, b) { return a[0] - b[0] || a[1] - b[1]; }).map(name).join(' | ') : '(empty)'; }

  // the fewest classes whose union is exactly the set, up to three
  function fewest(on) {
    var inside = [];
    MODS.forEach(function (m) { for (var s = 0; s < m; s++) if (cls(m, s).every(function (n) { return on[n]; })) inside.push([m, s]); });
    for (var i = 0; i < inside.length; i++) {
      if (same(setOf([inside[i]]), on)) return 1;
    }
    for (i = 0; i < inside.length; i++) for (var j = i + 1; j < inside.length; j++) if (same(setOf([inside[i], inside[j]]), on)) return 2;
    return 3;
  }
  function makeTarget() {
    var k = level < 1 ? 1 : level < 3 ? 2 : 3, top = level < 2 ? 6 : 9;
    for (var tries = 0; tries < 400; tries++) {
      var t = [];
      for (var i = 0; i < k; i++) { var m = 2 + Math.floor(Math.random() * (top - 1)); t.push([m, Math.floor(Math.random() * m)]); }
      var on = setOf(t), n = count(on);
      if (n < 6 || n > 40) continue;
      if (fewest(on) < k) continue;
      return t;
    }
    return [[3, 1]];
  }

  /* ---------------- the boards ---------------- */
  function build(box, buttons) {
    var ruler = el('div', 'cr-row cr-ruler'); ruler.setAttribute('aria-hidden', 'true');
    ruler.appendChild(el('span', 'cr-rl'));
    for (var c = 0; c < ROW; c++) ruler.appendChild(el('span', 'cr-n', String(c)));
    box.appendChild(ruler);
    for (var r = 0; r < N / ROW; r++) {
      var row = el('div', 'cr-row');
      var lab = el('span', 'cr-rl', String(r * ROW)); lab.setAttribute('aria-hidden', 'true');
      row.appendChild(lab);
      for (c = 0; c < ROW; c++) {
        var n = r * ROW + c, cell = el(buttons ? 'button' : 'span', 'cr-cell');
        cell.setAttribute('data-n', n);
        if (buttons) { cell.type = 'button'; cell.tabIndex = n === 0 ? 0 : -1; }
        row.appendChild(cell);
      }
      box.appendChild(row);
    }
  }
  var tBox = $('cr-target'), mBox = $('cr-mine');
  build(tBox, false); build(mBox, true);
  var tCells = $$('.cr-cell', tBox), mCells = $$('.cr-cell', mBox);

  // the moduli, as radio buttons drawn like the Player's
  MODS.forEach(function (m) {
    var lab = el('label'), r = el('input');
    r.type = 'radio'; r.name = 'cr-mod'; r.value = m; r.checked = m === mod;
    r.addEventListener('change', function () { setMod(m, false); });
    lab.appendChild(r); lab.appendChild(doc.createTextNode(' ' + m));
    $('cr-mods').appendChild(lab);
  });
  function setMod(m, fromKey) {
    mod = m;
    $$('input[name="cr-mod"]').forEach(function (r) { r.checked = +r.value === m; });
    preview(cur);
    if (fromKey) say('Modulus ' + m + '. The class through ' + cur + ' is ' + m + '@' + (cur % m) + '.');
  }

  function draw() {
    var on = setOf(mine);
    tCells.forEach(function (c, n) { c.classList.toggle('on', !!targetSet[n]); });
    mCells.forEach(function (c, n) {
      var t = !!targetSet[n], m = !!on[n];
      c.className = 'cr-cell' + (t && m ? ' hit' : t ? ' miss' : m ? ' extra' : '') + (c.classList.contains('pv') ? ' pv' : '');
      c.setAttribute('aria-label', n + (m ? ', in your sieve' : ', not in your sieve') + (t ? ', in the target' : ', not in the target'));
    });
    $('cr-formula').textContent = formula(mine);
    $('cr-level').textContent = 'sieve ' + (level + 1);
    $('cr-par').textContent = 'made of ' + plural(target.length, 'class', 'classes');
    var members = []; for (var n = 0; n < N; n++) if (targetSet[n]) members.push(n);
    $('cr-t-list').textContent = plural(members.length, 'number') + ': ' + members.join(', ') + '.';
    $('cr-hint-b').disabled = solved;
    $('cr-clear').disabled = solved || !mine.length;
  }
  // the cells of the class that pressing would add or take away
  function preview(n) {
    var s = n % mod;
    mCells.forEach(function (c, i) { c.classList.toggle('pv', i % mod === s); });
  }
  function clearPreview() { mCells.forEach(function (c) { c.classList.remove('pv'); }); }

  function toggle(n) {
    if (solved) { say('This sieve is solved. Next sieve brings another.'); return; }
    var c = [mod, n % mod], i = -1;
    mine.forEach(function (x, k) { if (x[0] === c[0] && x[1] === c[1]) i = k; });
    if (i >= 0) mine.splice(i, 1); else mine.push(c);
    draw();
    var on = setOf(mine);
    if (same(on, targetSet)) win();
    else {
      var miss = 0, extra = 0;
      for (var k = 0; k < N; k++) { if (targetSet[k] && !on[k]) miss++; if (on[k] && !targetSet[k]) extra++; }
      say((i >= 0 ? name(c) + ' left your sieve. ' : name(c) + ' joined your sieve. ') +
        (extra ? plural(extra, 'number') + ' not in the target' + (miss ? ', and ' : '.') : '') + (miss ? plural(miss, 'number') + ' still missing.' : ''));
    }
  }
  function win() {
    solved = true;
    var k = mine.length, par = target.length;
    say('Solved with ' + plural(k, 'class', 'classes') + ': ' + formula(mine) + (k < par ? ', fewer than it was made with.' : k === par ? ', as few as it was made with.' : '. It was made with ' + par + '; can you see how?') + (hints ? ' ' + plural(hints, 'hint') + ' used.' : '') + ' Next sieve brings another.');
    draw();
    $('cr-next').focus();
  }
  function fresh(next) {
    if (next) level++;
    target = makeTarget(); targetSet = setOf(target);
    mine = []; hints = 0; solved = false;
    stopPlay();
    draw();
    say('Sieve ' + (level + 1) + ': ' + plural(count(targetSet), 'number') + ', made of ' + plural(target.length, 'class', 'classes') + ', no modulus above ' + (level < 2 ? 6 : 9) + '.');
  }

  /* ---------------- the keyboard and the mouse ---------------- */
  function focusCell(n) {
    mCells[cur].tabIndex = -1; cur = n; mCells[n].tabIndex = 0; mCells[n].focus(); preview(n);
  }
  mBox.addEventListener('click', function (e) { var c = e.target.closest('.cr-cell'); if (c) { var n = +c.getAttribute('data-n'); if (n !== cur) { mCells[cur].tabIndex = -1; cur = n; c.tabIndex = 0; } toggle(n); preview(n); } });
  mBox.addEventListener('pointerover', function (e) { var c = e.target.closest('.cr-cell'); if (c) preview(+c.getAttribute('data-n')); });
  mBox.addEventListener('pointerleave', function () { if (!mBox.contains(doc.activeElement)) clearPreview(); else preview(cur); });
  mBox.addEventListener('focusin', function (e) { var c = e.target.closest('.cr-cell'); if (c) preview(+c.getAttribute('data-n')); });
  mBox.addEventListener('focusout', function (e) { if (!mBox.contains(e.relatedTarget)) clearPreview(); });
  mBox.addEventListener('keydown', function (e) {
    if (e.metaKey || e.ctrlKey || e.altKey) return;
    var n = cur, k = e.key;
    var to = { ArrowLeft: n - 1, ArrowRight: n + 1, ArrowUp: n - ROW, ArrowDown: n + ROW, Home: n - n % ROW, End: n - n % ROW + ROW - 1 }[k];
    if (to !== undefined) { e.preventDefault(); if (to >= 0 && to < N) focusCell(to); return; }
    if (/^[2-9]$/.test(k)) { e.preventDefault(); setMod(+k, true); }
  });

  /* ---------------- sound ---------------- */
  var BPM = 132, player = Tape.createPlayer({ bpm: BPM, hiss: 0.05, onTick: tick }), playing = null;
  function tick(st) {
    var pulse = st.playing ? Math.floor(st.position / (60 / (BPM * 4))) : -1;
    [tCells, mCells].forEach(function (cells, k) { cells.forEach(function (c, n) { c.classList.toggle('now', playing === k && n === pulse); }); });
    if (!st.playing && playing !== null && st.position >= st.duration) { playing = null; label(); }
  }
  function label() {
    $('cr-play-t').textContent = playing === 0 ? 'Stop' : 'Play the target';
    $('cr-play-m').textContent = playing === 1 ? 'Stop' : 'Play your sieve';
  }
  function stopPlay() { if (playing !== null) { player.stop(); playing = null; label(); tick(player.state()); } }
  function play(k) {
    if (playing === k) { stopPlay(); return; }
    var on = k === 0 ? targetSet : setOf(mine), evs = [];
    for (var n = 0; n < N; n++) if (on[n]) evs.push({ time: n, note: n % ROW === 0 ? 48 : k === 0 ? 67 : 60, len: 1, loud: n % ROW === 0 ? 9 : 6 });
    if (!evs.length) { say('Your sieve is empty, so there is nothing to play.'); return; }
    player.stop();
    player.load(evs);
    playing = k; label();
    player.play();
  }
  $('cr-play-t').addEventListener('click', function () { play(0); });
  $('cr-play-m').addEventListener('click', function () { play(1); });
  $('cr-clear').addEventListener('click', function () { mine = []; draw(); say('Your sieve is empty again.'); mCells[cur].focus(); });
  // a solved sieve leads to a harder one; an unsolved one is swapped for another like it
  $('cr-next').addEventListener('click', function () { fresh(solved); });
  $('cr-hint-b').addEventListener('click', function () {
    var have = mine.map(name), left = target.filter(function (c) { return have.indexOf(name(c)) < 0; });
    hints++;
    say(left.length ? 'One class of the target is ' + name(left[Math.floor(Math.random() * left.length)]) + '.' : 'Every class the target was made of is in your sieve; take away the ones that are not.');
  });
  Desk.onClose('win-crible', stopPlay);
  function say(msg) { $('cr-status').textContent = msg; }

  level = 0;
  target = makeTarget(); targetSet = setOf(target);
  draw();
  say('Choose a modulus, then press a number in your sieve to add the class through it.');
  return {};
})();
