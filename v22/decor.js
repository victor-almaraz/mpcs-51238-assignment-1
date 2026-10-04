/* The room's things that can be swapped: the three prints on the wall (one pinned up behind
   the shelf), the lamp, the plant at each end
   of the floor, the plant on the desk and the mug. Each is a button; pressing it puts the
   next of its kind in its place, the picture fading out and the next fading in once it has
   loaded. Every kind is drawn in the same box as the first, so each takes the same place.
   The wallpaper changes too, from the menu or by clicking the bare wall.
   Each time the page opens, every place and the wall take a kind chosen by chance; nothing
   is kept from one opening to the next. */

(function () {
  'use strict';
  var doc = document, V21 = '../v21/assets/', OWN = 'assets/';
  var KINDS = {
    'print-wide': { what: 'the print by the window', items: [
      [V21 + 'print-sieve.webp', 'a screen print of a sieve, its residue classes as rows of coloured dots'],
      [OWN + 'print-pavilion.webp', 'a screen print of the Philips Pavilion, its shells as ruled surfaces'],
      [OWN + 'print-polytope.webp', 'a print of a Polytope, cables hung across a dark hall with points of light']] },
    'print-shelf': { what: 'the print behind the shelf', items: [
      [OWN + 'shelf-print-paraboloids.webp', 'an ochre screen print of ruled surfaces under a terracotta sun'],
      [OWN + 'shelf-print-glissandi.webp', 'a print of the string glissandi of Metastaseis'],
      [OWN + 'shelf-print-psappha.webp', 'a print of the rhythm of Psappha, 27 of its first 40 pulses struck']] },
    'print-narrow': { what: 'the narrow print', items: [
      [V21 + 'print-dada.webp', 'a Dada poster of Hugo Ball’s sound poem, in black and red'],
      [OWN + 'print-arp.webp', 'a collage of torn squares after Hans Arp'],
      [OWN + 'print-taeuber.webp', 'a grid of coloured rectangles and circles after Sophie Taeuber-Arp']] },
    'floor-l': { what: 'the plant at the left', items: [
      [V21 + 'plant-fig.webp', 'a fiddle-leaf fig on a teak tripod'],
      [OWN + 'plant-snake.webp', 'a snake plant in a tall slate pot'],
      [OWN + 'plant-palm.webp', 'a kentia palm in a rattan basket']] },
    'floor-r': { what: 'the plant at the right', items: [
      [V21 + 'plant-monstera.webp', 'a monstera in a white pot on brass legs'],
      [OWN + 'plant-fern.webp', 'a Boston fern in an ochre pot on brass legs'],
      [OWN + 'plant-rubber.webp', 'a rubber plant in a white pot']] },
    'desk-plant': { what: 'the plant on the desk', items: [
      [V21 + 'pothos.webp', 'a pothos trailing over the desk'],
      [OWN + 'desk-jade.webp', 'a jade plant in a celadon bowl'],
      [OWN + 'desk-cacti.webp', 'three cacti in a terracotta pot']] },
    'lamp': { what: 'the lamp', items: [
      [V21 + 'lamp.webp', 'a black task lamp on a curved arm, its shade turned to the desk'],
      [OWN + 'lamp-dome.webp', 'a white dome lamp on a flared stem'],
      [OWN + 'lamp-angle.webp', 'a terracotta balanced-arm lamp on springs'],
      [OWN + 'lamp-ceramic.webp', 'an ochre ceramic lamp with a linen drum shade']] },
    'mug': { what: 'the mug', items: [
      [V21 + 'mug.webp', 'a cream mug dipped in terracotta'],
      [OWN + 'mug-sage.webp', 'a sage mug'],
      [OWN + 'mug-striped.webp', 'a cream mug banded in ochre and slate'],
      [OWN + 'mug-enamel.webp', 'a speckled enamel mug rimmed in blue'],
      [OWN + 'mug-sieve.webp', 'a cream mug printed with a sieve in terracotta points'],
      [OWN + 'mug-black.webp', 'a black stoneware mug with a white ring'],
      [OWN + 'mug-cup.webp', 'a white cup on its saucer']] }
  };
  var status = doc.getElementById('swap-status');
  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)');

  function label(b, k) {
    var kind = KINDS[b.getAttribute('data-swap')], item = kind.items[k];
    b.setAttribute('aria-label', 'Change ' + kind.what + ': now ' + item[1] + ', ' + (k + 1) + ' of ' + kind.items.length);
  }
  Array.prototype.forEach.call(doc.querySelectorAll('[data-swap]'), function (b) {
    // each opening of the page sets the room afresh: a kind chosen by chance for every place
    var kind = KINDS[b.getAttribute('data-swap')], img = b.querySelector('img'), busy = false;
    var at = Math.floor(Math.random() * kind.items.length);
    if (at) img.src = kind.items[at][0];
    b.setAttribute('data-v', at);
    label(b, at);
    b.addEventListener('click', function () {
      if (busy) return;
      busy = true;
      at = (at + 1) % kind.items.length;
      var next = new Image(), item = kind.items[at];
      next.src = item[0];
      var fade = reduced.matches ? Promise.resolve() : new Promise(function (r) { b.classList.add('fading'); setTimeout(r, 180); });
      var ready = next.decode ? next.decode().catch(function () {}) : Promise.resolve();
      Promise.all([fade, ready]).then(function () {
        img.src = item[0];
        b.setAttribute('data-v', at);
        b.classList.remove('fading');
        label(b, at);
        status.textContent = '';
        setTimeout(function () { status.textContent = kind.what.charAt(0).toUpperCase() + kind.what.slice(1) + ' is now ' + item[1] + '.'; }, 30);
        busy = false;
      });
    });
  });

  /* ---------------- the wallpaper ---------------- */
  // each paper is a tile and a ground in style.css, hung by data-paper on the room
  var PAPERS = [
    ['', 'a deep blue paper under an ogee trellis with cream seed pods'],
    ['atomic', 'a sage paper with cream starbursts and ochre boomerangs'],
    ['trellis', 'a burnt umber paper with a diamond trellis and cream buds'],
    ['grass', 'an ivory grasscloth in fine vertical stripes']];
  var room = doc.getElementById('desk'), paper = Math.floor(Math.random() * PAPERS.length), wall = doc.querySelector('.overview .wall');
  function put() { var p = PAPERS[paper]; if (p[0]) room.setAttribute('data-paper', p[0]); else room.removeAttribute('data-paper'); return p; }
  put();
  function hang() {
    paper = (paper + 1) % PAPERS.length;
    var p = put();
    status.textContent = '';
    setTimeout(function () { status.textContent = 'The wall is now hung with ' + p[1] + '.'; }, 30);
  }
  doc.getElementById('paper-btn').addEventListener('click', hang);
  if (wall) wall.addEventListener('click', hang);
})();
