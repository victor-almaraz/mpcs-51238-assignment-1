/* The room's things that can be swapped, after v22: the three prints on the wall (one pinned
   up behind the shelf), the lamp, the plant at each end of the floor, the plant on the desk
   and the mug. Each is a button; pressing it puts the next of its kind in its place at once.
   Every kind is drawn in pixels in the same box as the first, lit where it stands, so each
   takes the same place in the same light. The wallpaper changes too, from the menu or by
   pressing the bare wall: each paper is a picture of the room of its own (style.css). The
   switch on the wall turns the lamp off and on, and the room is drawn in the light there is:
   each lamp's own light, or, with it off, only the screen's and the dusk's.
   The room is lit for the time of day by the visitor's clock (morning, evening or night, each
   drawn in assets/<time>/), or as the menu's Light chooses.
   Each time the page opens, every place and the wall take a kind chosen by chance, unless the
   address says otherwise: the room is written in it as #room= and a code, one figure for each
   place, then the paper and the lamp's switch, kept up to date as things change, so a room
   can be sent to someone as a link; nothing is stored. Decor.wallAt tells hotspots.js where
   the bare wall is. */

(function () {
  'use strict';
  var doc = document;
  var KINDS = {
    'print-wide': { what: 'the print by the window', items: [
      ['print-sieve', 'a screen print of a sieve, its residue classes as rows of coloured dots'],
      ['print-pavilion', 'a screen print of the Philips Pavilion, its shells as ruled surfaces'],
      ['print-polytope', 'a print of a Polytope, cables hung across a dark hall with points of light']] },
    'print-shelf': { what: 'the print behind the shelf', items: [
      ['shelf-print-paraboloids', 'an ochre screen print of ruled surfaces under a terracotta sun'],
      ['shelf-print-glissandi', 'a print of the string glissandi of Metastaseis'],
      ['shelf-print-psappha', 'a print of the rhythm of Psappha, its pulses struck in ink']] },
    'print-narrow': { what: 'the narrow print', items: [
      ['print-dada', 'a Dada poster of Hugo Ball’s sound poem, in black and red'],
      ['print-arp', 'a collage of torn squares after Hans Arp'],
      ['print-taeuber', 'a grid of coloured rectangles and circles after Sophie Taeuber-Arp']] },
    'floor-l': { what: 'the plant at the left', items: [
      ['plant-fig', 'a fiddle-leaf fig on a teak tripod'],
      ['plant-snake', 'a snake plant in a tall slate pot'],
      ['plant-palm', 'a kentia palm in a rattan basket']] },
    'floor-r': { what: 'the plant at the right', items: [
      ['plant-monstera', 'a monstera in a white pot on brass legs'],
      ['plant-fern', 'a Boston fern in an ochre pot on brass legs'],
      ['plant-rubber', 'a rubber plant in a white pot']] },
    'desk-plant': { what: 'the plant on the desk', items: [
      ['desk-pothos', 'a pothos trailing over the desk'],
      ['desk-jade', 'a jade plant in a celadon bowl'],
      ['desk-cacti', 'three cacti in a terracotta pot']] },
    'lamp': { what: 'the lamp', items: [
      ['lamp-task', 'a black task lamp on a curved arm, its shade turned to the desk'],
      ['lamp-dome', 'a white dome lamp on a flared stem'],
      ['lamp-angle', 'a terracotta balanced-arm lamp on springs'],
      ['lamp-ceramic', 'an ochre ceramic lamp with a linen drum shade']] },
    'mug': { what: 'the mug', items: [
      ['mug-dipped', 'a cream mug dipped in terracotta'],
      ['mug-sage', 'a sage mug'],
      ['mug-striped', 'a cream mug banded in ochre and slate'],
      ['mug-enamel', 'a speckled enamel mug rimmed in blue'],
      ['mug-sieve', 'a cream mug printed with a sieve in terracotta points'],
      ['mug-black', 'a black stoneware mug with a white ring'],
      ['mug-cup', 'a white cup on its saucer']] }
  };
  var status = doc.getElementById('swap-status');
  function say(msg) { status.textContent = ''; setTimeout(function () { status.textContent = msg; }, 30); }
  function cap(s) { return s.charAt(0).toUpperCase() + s.slice(1); }
  // what happens in the room is told as events on the scene, for the sounds (sounds.js)
  function tell(what, detail) { scene.dispatchEvent(new CustomEvent('room:' + what, { detail: detail })); }

  /* ---------------- the time of day ---------------- */
  var TIMES = { morning: 'morning light through the window', evening: 'the dusk through the window', night: 'moonlight through the window' };
  var LIGHTS = ['clock', 'morning', 'evening', 'night'], chosen = 'clock';
  function clockTime() { var h = new Date().getHours(); return h >= 5 && h < 12 ? 'morning' : h >= 12 && h < 21 ? 'evening' : 'night'; }
  function time() { return chosen === 'clock' ? clockTime() : chosen; }
  function base() { return 'assets/' + time() + '/'; }
  // the ground under each paper's tile, at each time (the colour behind the room)
  var GROUND = { evening: { ogee: '#283463', atomic: '#344758', trellis: '#443048', grass: '#88808a' },
    morning: { ogee: '#293a5b', atomic: '#47625e', trellis: '#673c44', grass: '#a39e94' },
    night: { ogee: '#222a5e', atomic: '#293a5b', trellis: '#3e2a44', grass: '#575884' } };

  // the light: the lamp on the desk, or 'off'. What the lamp's light reaches is drawn for each
  // (assets/<time>/lit/<light>/); everything else once a time (assets/<time>/)
  var LIT = ['desk-cacti', 'desk-jade', 'desk-pothos', 'lamp-angle', 'lamp-ceramic', 'lamp-dome', 'lamp-task', 'mug-black', 'mug-cup',
    'mug-dipped', 'mug-enamel', 'mug-sage', 'mug-sieve', 'mug-striped', 'plant-fig', 'plant-palm', 'plant-snake', 'print-arp',
    'print-dada', 'print-pavilion', 'print-polytope', 'print-sieve', 'print-taeuber', 'px-coding-form', 'px-computer',
    'px-out-tray', 'px-vol-1', 'px-reader', 'switch-on', 'switch-off'];
  var room = doc.getElementById('desk'), scene = doc.querySelector('.overview');
  var lampOn = true, flicker = false, swaps = [], SWAYS = { 'floor-l': 1, 'floor-r': 1, 'desk-plant': 1 };
  var REDUCED = window.matchMedia('(prefers-reduced-motion: reduce)');
  function light() { return lampOn && !flicker ? lampKind() : 'off'; }
  function src(name, at, t) {
    var b = t ? 'assets/' + t + '/' : base();
    return b + (LIT.indexOf(name) >= 0 ? 'lit/' + (at || light()) + '/' : '') + name + '.png';
  }
  function lampKind() { var b = scene.querySelector('[data-swap="lamp"]'); return b.swapItem().split('-')[1]; }

  Array.prototype.forEach.call(doc.querySelectorAll('[data-swap]'), function (b) {
    var kind = KINDS[b.getAttribute('data-swap')], img = b.querySelector('img');
    var at = Math.floor(Math.random() * kind.items.length);
    b.swapItem = function () { return kind.items[at][0]; };
    b.swapAt = function (i) { if (i !== undefined) at = i; return at; };
    b.swapCount = kind.items.length;
    b.show = function () {
      var item = kind.items[at];
      img.src = src(item[0]);
      if (SWAYS[b.getAttribute('data-swap')]) {
        b.classList.add('sways');
        b.style.setProperty('--sway', 'url(' + src(item[0]).replace(base(), base() + 'anim/').replace('.png', '-sway.png') + ')');
      }
      b.setAttribute('aria-label', 'Change ' + kind.what + ': now ' + item[1] + (b.getAttribute('data-swap') === 'lamp' && !lampOn ? ', switched off' : '') + ', ' + (at + 1) + ' of ' + kind.items.length);
      return item;
    };
    b.addEventListener('click', function () {
      at = (at + 1) % kind.items.length;
      var item = kind.items[at];
      if (b.getAttribute('data-swap') === 'lamp') relight(); else { b.show(); write(); }
      tell('swap', { place: b.getAttribute('data-swap'), item: item[0] });
      say(cap(kind.what) + ' is now ' + item[1] + '.');
    });
    swaps.push(b);
  });

  /* ---------------- the wallpaper ---------------- */
  var PAPERS = [
    ['ogee', 'a deep blue paper under an ogee trellis with cream seed pods'],
    ['atomic', 'a sage paper with cream starbursts and ochre boomerangs'],
    ['trellis', 'a burnt umber paper with a diamond trellis and cream buds'],
    ['grass', 'an ivory grasscloth in fine vertical stripes']];
  var paper = Math.floor(Math.random() * PAPERS.length);
  function next() {
    paper = (paper + 1) % PAPERS.length;
    relight();
    tell('paper', { paper: PAPERS[paper][0] });
    say('The wall is now hung with ' + PAPERS[paper][1] + '.');
  }
  doc.getElementById('paper-btn').addEventListener('click', next);

  /* ---------------- the lamp's switch ---------------- */
  var sw = scene.querySelector('.lamp-switch');
  sw.addEventListener('click', function () {
    lampOn = !lampOn;
    relight();
    tell('switch', { on: lampOn });
    // switched on, the lamp catches, drops out and holds, as an old one does
    if (lampOn && !REDUCED.matches) {
      [[60, true], [130, false], [210, true], [260, false]].forEach(function (f) {
        setTimeout(function () { if (lampOn) { flicker = f[1]; relight(); tell('flicker', { lit: !f[1] }); } }, f[0]);
      });
    }
    say(lampOn ? 'The lamp is on.' : 'The lamp is off; the room is lit by the screen and ' + TIMES[time()].replace(' through the window', '') + '.');
  });

  /* ---------------- the room's code, in the address ---------------- */
  // one figure for each place (in the order of the buttons), one for the paper, one for the switch
  function code() { return swaps.map(function (b) { return b.swapAt(); }).join('') + paper + (lampOn ? 1 : 0); }
  function read(h) {
    var m = /(?:^#|&)room=(\d+)/.exec(h || '');
    if (!m || m[1].length !== swaps.length + 2) return false;
    var d = m[1].split('').map(Number);
    if (swaps.some(function (b, i) { return d[i] >= b.swapCount; }) || d[swaps.length] >= PAPERS.length || d[swaps.length + 1] > 1) return false;
    swaps.forEach(function (b, i) { b.swapAt(d[i]); });
    paper = d[swaps.length]; lampOn = d[swaps.length + 1] === 1;
    return true;
  }
  function write() {
    if (!history.replaceState) return;
    try { history.replaceState(null, '', location.pathname + location.search + '#room=' + code()); } catch (e) { /* a file: page */ }
  }
  read(location.hash);
  window.addEventListener('hashchange', function () { if (read(location.hash)) { relight(); say('The room is set as the link describes.'); } });
  var copyBtn = doc.getElementById('copy-room');
  copyBtn.addEventListener('click', function () {
    write();
    var url = location.href;
    var done = function () { say('A link to this room is copied. Whoever opens it finds the room as it is now, in the light of their own clock.'); };
    if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(url).then(done, function () { say('The link to this room is in the address bar: ' + url); });
    else say('The link to this room is in the address bar: ' + url);
  });

  /* ---------------- the menu's Light ---------------- */
  var lightBtn = doc.getElementById('light-btn');
  function labelLight() { lightBtn.textContent = 'Light: ' + (chosen === 'clock' ? 'by the clock (' + time() + ')' : time()); }
  // a new time's room is shown once its pictures are in, so it never stands bare between them
  function turnTo(fn) {
    var b = base(), p = PAPERS[paper][0];
    var urls = [b + 'lit/' + light() + '/room-' + p + '.png', b + 'room-' + p + '-r.png', b + 'tile-' + p + '.png', b + 'floor-tile.png']
      .concat(swaps.map(function (sb) { return src(sb.swapItem()); }));
    Promise.all(urls.map(function (u) { return new Promise(function (r) { var i = new Image(); i.onload = i.onerror = r; i.src = u; if (i.complete) r(); setTimeout(r, 1500); }); }))
      .then(function () { relight(); prefetch(); if (fn) fn(); });
  }
  lightBtn.addEventListener('click', function () {
    chosen = LIGHTS[(LIGHTS.indexOf(chosen) + 1) % LIGHTS.length];
    labelLight();
    turnTo(function () { say('The room is lit by ' + TIMES[time()] + (chosen === 'clock' ? ', as the clock says.' : '.')); });
  });
  // by the clock, the light turns when the hour does
  var was = time();
  setInterval(function () { if (time() !== was) { was = time(); turnTo(); } }, 60000);

  // everything drawn for the light, in the light there is now
  function relight() {
    var p = PAPERS[paper][0], t = time(), b = base();
    if (p === 'ogee') room.removeAttribute('data-paper'); else room.setAttribute('data-paper', p);
    room.setAttribute('data-light', light());
    room.setAttribute('data-time', t);
    var css = { '--back-l': b + 'lit/' + light() + '/room-' + p + '.png', '--back-r': b + 'room-' + p + '-r.png', '--tile': b + 'tile-' + p + '.png',
      '--floor-tile': b + 'floor-tile.png', '--steam': b + 'anim/lit/' + light() + '/steam.png', '--reel-l': b + 'anim/reel-l.png',
      '--reel-r': b + 'anim/reel-r.png', '--screen': b + 'anim/screen.png' };
    for (var k in css) room.style.setProperty(k, 'url(' + css[k] + ')');
    room.style.setProperty('--paper-blue', GROUND[t][p]);
    swaps.forEach(function (b) { b.show(); });
    Array.prototype.forEach.call(scene.querySelectorAll('img[data-px]'), function (img) { img.src = src(img.getAttribute('data-px')); });
    sw.querySelector('img').src = src(lampOn ? 'switch-on' : 'switch-off');
    sw.setAttribute('aria-pressed', String(lampOn));
    sw.setAttribute('aria-label', 'The lamp’s switch: ' + (lampOn ? 'on' : 'off'));
    labelLight();
    write();
  }
  relight();

  // once the room is up, the pictures for every other choice are fetched, so a change shows at once
  var seen = {};
  function get(u) { if (!seen[u]) { seen[u] = 1; new Image().src = u; } }
  function prefetch() {
    var lights = ['task', 'dome', 'angle', 'ceramic', 'off'], b = base();
    swaps.forEach(function (sb) {
      KINDS[sb.getAttribute('data-swap')].items.forEach(function (it) {
        // a lamp is drawn only in its own light and switched off
        if (sb.getAttribute('data-swap') === 'lamp') { get(src(it[0], it[0].split('-')[1])); get(src(it[0], 'off')); }
        else get(src(it[0]));
      });
    });
    lights.forEach(function (l) { get(b + 'anim/lit/' + l + '/steam.png'); });
    PAPERS.forEach(function (p) { get(b + 'room-' + p[0] + '-r.png'); get(b + 'tile-' + p[0] + '.png'); get(b + 'lit/' + light() + '/room-' + p[0] + '.png'); });
    lights.forEach(function (l) {
      get(b + 'lit/' + l + '/room-' + PAPERS[paper][0] + '.png');
      Array.prototype.forEach.call(scene.querySelectorAll('img[data-px]'), function (img) { get(src(img.getAttribute('data-px'), l)); });
    });
    get(src('switch-off', 'off'));
  }
  window.addEventListener('load', prefetch);

  // the bare wall, in the room's pixels (640 x 320): all of it above the floor but the desk's
  // top, its trestles, the shelf's board and the stool; past the picture the paper runs on
  var wall = scene.querySelector('.wall');
  function wallAt(x, y) {
    if (getComputedStyle(wall).display === 'none') return false;
    var r = scene.getBoundingClientRect(), ap = parseFloat(getComputedStyle(scene).fontSize) * 92 / 640;
    var ax = (x - r.left) / ap, ay = (y - r.top) / ap;
    if (ay >= 309) return false;
    if (ax >= 70 && ax < 570 && ay >= 208 && ay < 225) return false;
    if (ax >= 327 && ax < 605 && ay >= 82 && ay < 89) return false;
    if (ax >= 368 && ax < 428 && ay >= 248) return false;
    return true;
  }
  var bare = function (t) { return !t.closest('button, a, input, .drawer'); };
  scene.addEventListener('click', function (e) {
    if (bare(e.target) && wallAt(e.clientX, e.clientY)) next();
  });
  window.Decor = { wallAt: function (e) { return bare(e.target) && wallAt(e.clientX, e.clientY); }, lampOn: function () { return lampOn; },
    item: function (place) { var b = scene.querySelector('[data-swap="' + place + '"]'); return b && b.swapItem(); },
    paper: function () { return PAPERS[paper][0]; }, time: time };
})();
