/* The room's things that can be swapped, after v22: the three prints on the wall (one pinned
   up behind the shelf), the lamp, the plant at each end of the floor, the plant on the desk
   and the mug. Each is a button; pressing it puts the next of its kind in its place at once.
   Every kind is drawn in pixels in the same box as the first, lit where it stands, so each
   takes the same place in the same light. The wallpaper changes too, from the menu or by
   pressing the bare wall: each paper is a picture of the room of its own (style.css). The
   switch on the wall turns the lamp off and on, and the room is drawn in the light there is:
   each lamp's own light, or, with it off, only the screen's and the dusk's.
   Each time the page opens, every place and the wall take a kind chosen by chance; nothing
   is kept from one opening to the next. Decor.wallAt tells hotspots.js where the bare wall is. */

(function () {
  'use strict';
  var doc = document, A = 'assets/';
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

  // the light: the lamp on the desk, or 'off'. What the lamp's light reaches is drawn for each
  // (assets/lit/<light>/); everything else once (assets/)
  var LIT = ['desk-cacti', 'desk-jade', 'desk-pothos', 'lamp-angle', 'lamp-ceramic', 'lamp-dome', 'lamp-task', 'mug-black', 'mug-cup',
    'mug-dipped', 'mug-enamel', 'mug-sage', 'mug-sieve', 'mug-striped', 'plant-fig', 'plant-palm', 'plant-snake', 'print-arp',
    'print-dada', 'print-pavilion', 'print-polytope', 'print-sieve', 'print-taeuber', 'px-coding-form', 'px-computer',
    'px-out-tray', 'px-vol-1', 'switch-on', 'switch-off'];
  var room = doc.getElementById('desk'), scene = doc.querySelector('.overview');
  var lampOn = true, flicker = false, swaps = [], SWAYS = { 'floor-l': 1, 'floor-r': 1, 'desk-plant': 1 };
  var REDUCED = window.matchMedia('(prefers-reduced-motion: reduce)');
  function light() { return lampOn && !flicker ? lampKind() : 'off'; }
  function src(name, at) { return A + (LIT.indexOf(name) >= 0 ? 'lit/' + (at || light()) + '/' : '') + name + '.png'; }
  function lampKind() { var b = scene.querySelector('[data-swap="lamp"]'); return b.swapItem().split('-')[1]; }

  Array.prototype.forEach.call(doc.querySelectorAll('[data-swap]'), function (b) {
    var kind = KINDS[b.getAttribute('data-swap')], img = b.querySelector('img');
    var at = Math.floor(Math.random() * kind.items.length);
    b.swapItem = function () { return kind.items[at][0]; };
    b.show = function () {
      var item = kind.items[at];
      img.src = src(item[0]);
      if (SWAYS[b.getAttribute('data-swap')]) {
        b.classList.add('sways');
        b.style.setProperty('--sway', 'url(' + src(item[0]).replace(A, A + 'anim/').replace('.png', '-sway.png') + ')');
      }
      b.setAttribute('aria-label', 'Change ' + kind.what + ': now ' + item[1] + (b.getAttribute('data-swap') === 'lamp' && !lampOn ? ', switched off' : '') + ', ' + (at + 1) + ' of ' + kind.items.length);
      return item;
    };
    b.addEventListener('click', function () {
      at = (at + 1) % kind.items.length;
      var item = kind.items[at];
      if (b.getAttribute('data-swap') === 'lamp') relight(); else b.show();
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
    say('The wall is now hung with ' + PAPERS[paper][1] + '.');
  }
  doc.getElementById('paper-btn').addEventListener('click', next);

  /* ---------------- the lamp's switch ---------------- */
  var sw = scene.querySelector('.lamp-switch');
  sw.addEventListener('click', function () {
    lampOn = !lampOn;
    relight();
    // switched on, the lamp catches, drops out and holds, as an old one does
    if (lampOn && !REDUCED.matches) {
      [[60, true], [130, false], [210, true], [260, false]].forEach(function (f) {
        setTimeout(function () { if (lampOn) { flicker = f[1]; relight(); } }, f[0]);
      });
    }
    say(lampOn ? 'The lamp is on.' : 'The lamp is off; the room is lit by the screen and the dusk.');
  });

  // everything drawn for the light, in the light there is now
  function relight() {
    var p = PAPERS[paper][0];
    if (p === 'ogee') room.removeAttribute('data-paper'); else room.setAttribute('data-paper', p);
    room.setAttribute('data-light', light());
    room.style.setProperty('--back-l', 'url(' + A + 'lit/' + light() + '/room-' + p + '.png)');
    room.style.setProperty('--steam', 'url(' + A + 'anim/lit/' + light() + '/steam.png)');
    swaps.forEach(function (b) { b.show(); });
    Array.prototype.forEach.call(scene.querySelectorAll('img[data-lit]'), function (img) { img.src = src(img.getAttribute('data-lit').replace('.png', '')); });
    sw.querySelector('img').src = src(lampOn ? 'switch-on' : 'switch-off');
    sw.setAttribute('aria-pressed', String(lampOn));
    sw.setAttribute('aria-label', 'The lamp’s switch: ' + (lampOn ? 'on' : 'off'));
  }
  relight();

  // once the room is up, the pictures for every other choice are fetched, so a change shows at once
  window.addEventListener('load', function () {
    var lights = ['task', 'dome', 'angle', 'ceramic', 'off'], seen = {};
    function get(u) { if (!seen[u]) { seen[u] = 1; new Image().src = u; } }
    swaps.forEach(function (b) {
      KINDS[b.getAttribute('data-swap')].items.forEach(function (it) {
        // a lamp is drawn only in its own light and switched off
        if (b.getAttribute('data-swap') === 'lamp') { get(src(it[0], it[0].split('-')[1])); get(src(it[0], 'off')); }
        else get(src(it[0]));
      });
    });
    lights.forEach(function (l) { get(A + 'anim/lit/' + l + '/steam.png'); });
    PAPERS.forEach(function (p) { get(A + 'room-' + p[0] + '-r.png'); get(A + 'tile-' + p[0] + '.png'); get(A + 'lit/' + light() + '/room-' + p[0] + '.png'); });
    lights.forEach(function (l) {
      get(A + 'lit/' + l + '/room-' + PAPERS[paper][0] + '.png');
      Array.prototype.forEach.call(scene.querySelectorAll('img[data-lit]'), function (img) { get(src(img.getAttribute('data-lit').replace('.png', ''), l)); });
    });
    get(src('switch-off', 'off'));
  });

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
  window.Decor = { wallAt: function (e) { return bare(e.target) && wallAt(e.clientX, e.clientY); }, lampOn: function () { return lampOn; } };
})();
