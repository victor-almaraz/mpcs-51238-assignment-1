/* The room's things that can be swapped, after v22: the three prints on the wall (one pinned
   up behind the shelf), the lamp, the plant at each end of the floor, the plant on the desk
   and the mug. Each is a button; pressing it puts the next of its kind in its place at once.
   Every kind is drawn in pixels in the same box as the first, lit where it stands, so each
   takes the same place in the same light. The wallpaper changes too, from the menu or by
   pressing the bare wall: each paper is a picture of the room of its own (style.css).
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

  Array.prototype.forEach.call(doc.querySelectorAll('[data-swap]'), function (b) {
    var kind = KINDS[b.getAttribute('data-swap')], img = b.querySelector('img');
    var at = Math.floor(Math.random() * kind.items.length);
    function put() {
      var item = kind.items[at];
      img.src = A + item[0] + '.png';
      b.setAttribute('aria-label', 'Change ' + kind.what + ': now ' + item[1] + ', ' + (at + 1) + ' of ' + kind.items.length);
      return item;
    }
    put();
    b.addEventListener('click', function () {
      at = (at + 1) % kind.items.length;
      say(cap(kind.what) + ' is now ' + put()[1] + '.');
    });
    // the others are fetched once the room is up, so a swap shows at once
    window.addEventListener('load', function () {
      kind.items.forEach(function (it) { new Image().src = A + it[0] + '.png'; });
    });
  });

  /* ---------------- the wallpaper ---------------- */
  var PAPERS = [
    ['', 'a deep blue paper under an ogee trellis with cream seed pods'],
    ['atomic', 'a sage paper with cream starbursts and ochre boomerangs'],
    ['trellis', 'a burnt umber paper with a diamond trellis and cream buds'],
    ['grass', 'an ivory grasscloth in fine vertical stripes']];
  var room = doc.getElementById('desk'), scene = doc.querySelector('.overview');
  var paper = Math.floor(Math.random() * PAPERS.length);
  function hangPaper() { var p = PAPERS[paper]; if (p[0]) room.setAttribute('data-paper', p[0]); else room.removeAttribute('data-paper'); return p; }
  hangPaper();
  function next() {
    paper = (paper + 1) % PAPERS.length;
    say('The wall is now hung with ' + hangPaper()[1] + '.');
  }
  window.addEventListener('load', function () {
    PAPERS.forEach(function (p) { var n = p[0] || 'ogee'; new Image().src = A + 'room-' + n + '.png'; new Image().src = A + 'tile-' + n + '.png'; });
  });
  doc.getElementById('paper-btn').addEventListener('click', next);

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
  window.Decor = { wallAt: function (e) { return bare(e.target) && wallAt(e.clientX, e.clientY); } };
})();
