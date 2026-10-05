/* Looking, the point-and-click game's other verb. Pressing a thing uses it (takes it up, or
   changes it); looking at it (the right button, or L with the thing under the pointer or
   focused) has the narrator say what it is, in a line along the foot of the room. Every print
   leads to a deck, and so does every book that can be taken down: the narrator offers to put the deck it calls to mind on the coding form.
   The narration is read out as well (a live region), and goes on a press elsewhere, on
   Escape, or after a while. Needs Desk (desk.js) and Decor (decor.js). */

(function () {
  'use strict';
  var doc = document, scene = doc.querySelector('.overview');
  if (!scene) return;
  var LIST = window.matchMedia('(max-width: 1011px), (max-height: 505px)');

  // what the narrator says of each thing: [line, deck to offer, the offer]
  var LOOK = {
    'print-sieve': ['A screen print of a sieve: five residue classes in five colours, every member a bright dot, and their union struck in ink along the foot. Xenakis built scales and rhythms this way.', 'sieve-scale', 'Sieve scale'],
    'print-pavilion': ['The Philips Pavilion, Brussels, 1958: Xenakis drew its shells, in Le Corbusier’s office, from the ruled surfaces of the glissandi in Metastaseis.', 'string-glissandi', 'String glissandi'],
    'print-polytope': ['The Polytope de Montréal, 1967: steel cables hung through the French Pavilion, and hundreds of lights flashing along them, by chance and by plan.', 'stochastic-cloud', 'Stochastic cloud'],
    'print-dada': ['A Dada poster: DADA in red over Hugo Ball’s sound poem, Gadji beri bimba, first read at the Cabaret Voltaire in 1916. “Glandridi” is one of its words.', 'tzara-s-hat', 'Tzara’s hat'],
    'print-arp': ['Torn squares after Hans Arp, who is said to have let his squares fall on the sheet and pasted them where they lay: arranged according to the laws of chance.', 'erratum-musical', 'Erratum musical'],
    'print-taeuber': ['A grid of rectangles and circles after Sophie Taeuber-Arp: each cell one flat colour, the sheet a grid of cells, as a cellular automaton’s is.', 'life', 'Life'],
    'shelf-print-paraboloids': ['An ochre screen print of ruled surfaces, straight strings that bend into saddles: the geometry of the Pavilion and of Metastaseis.', 'string-glissandi', 'String glissandi'],
    'shelf-print-glissandi': ['The string glissandi of Metastaseis, 1954: each string player sliding on a line of its own, terracotta crossing slate.', 'string-glissandi', 'String glissandi'],
    'shelf-print-psappha': ['Psappha, 1975, for one percussionist: its pulses laid out on a grid, some struck, most not. Rhythms like these can be cut from sieves.', 'two-rhythm-sieves', 'Two rhythm sieves'],
    'plant-fig': ['A fiddle-leaf fig on a teak tripod. It has not been moved in years, which is why it is still alive.'],
    'plant-snake': ['A snake plant in a tall slate pot. It asks for nothing and gets it.'],
    'plant-palm': ['A kentia palm in a rattan basket, its fronds arching over the floor.'],
    'plant-monstera': ['A monstera in a white pot on brass legs, its leaves split as if by a hole punch.'],
    'plant-fern': ['A Boston fern spilling out of an ochre pot. It wants more water than it gets.'],
    'plant-rubber': ['A rubber plant in a white pot, a red sheath at the tip of its newest leaf.'],
    'desk-pothos': ['A pothos, trailing over the desk toward the coding form.'],
    'desk-jade': ['A jade plant in a celadon bowl, its leaves thick and red at the rims.'],
    'desk-cacti': ['Three cacti in one terracotta pot. The small one is in flower.'],
    'lamp-task': ['A black task lamp on a curved arm, its shade turned down to the desk.'],
    'lamp-dome': ['A white dome lamp on a flared stem. It lights the desk under it and little else.'],
    'lamp-angle': ['A terracotta balanced-arm lamp, held where it is put by its springs.'],
    'lamp-ceramic': ['An ochre ceramic lamp under a linen drum, throwing light up the wall and down onto the desk.'],
    'mug-dipped': ['A cream mug dipped in terracotta. The coffee is cold.'],
    'mug-sage': ['A sage mug. Still warm.'],
    'mug-striped': ['A cream mug banded in ochre and slate.'],
    'mug-enamel': ['A speckled enamel mug rimmed in blue, chipped at the handle.'],
    'mug-sieve': ['A mug printed with a sieve in terracotta points. Someone had it made.'],
    'mug-black': ['A black stoneware mug with a white ring.'],
    'mug-cup': ['A white cup on its saucer, a blue band round it.'],
    v1: ['The reference manual, volume 1: FORTRAN, card by card.'],
    v2: ['The reference manual, volume 2: sieves, and how to compute them.'],
    v3: ['The reference manual, volume 3: music, and the tape player.'],
    'o-mag': ['Five magazines in their ledge: Moiré, of art and computing; Event, a Fluxus newspaper; Gesso, of painting by rule and chance; Cons, of Lisp; and Silver, of black-and-white photography. Their articles print decks you can run.'],
    'o-folio': ['A file box of Xenakis miscellanea: drawings, photographs, notes.'],
    'o-box': ['The deck box: every sample deck, each behind its tab.'],
    'o-form': ['A coding form on a clipboard, eighty columns to a line, ready for cards.'],
    'o-out': ['The out tray, where the printouts and the punched cards come back.'],
    'o-computer': ['The computer. Its screen is on; the Editor is open.'],
    'o-tape': ['A reel-to-reel tape player. It plays the cards a program punches.'],
    'o-reader': ['A card reader and a line printer in one steel cabinet. Every deck that is run passes through the reader, and the printer prints what it says.'],
    'o-upic': ['The UPIC’s tablet. Xenakis had it built in Paris in the 1970s, so that music could be drawn: time across the page, pitch up it, every line a voice.'],
    'print-kelly': ['After Ellsworth Kelly’s Spectrum Colors Arranged by Chance, 1951: a grid of squares, each one’s colour drawn by chance from numbered slips.', 'spectrum-colors-by-chance', 'Spectrum colors arranged by chance'],
    'print-fluxus': ['A poster for a Fluxus concert, 1962: the evening’s events listed in boxes of type, black on newsprint, one box in yellow.', 'event-cards', 'Event cards'],
    'print-molnar': ['After Vera Molnár’s (Des)Ordres, 1974: squares inside squares, drawn by a plotter, their corners moved by chance, a little more in each.', 'order-and-disorder', 'Order and disorder'],
    'book-xenakis': ['Iannis Xenakis, Formalized Music, 1971: the English edition of Musiques formelles, with the sieves, Achorripsis, and the stochastic program written in FORTRAN for an IBM 7090.', 'sieve-generator', 'Sieve generator'],
    'book-hiller': ['Lejaren Hiller and Leonard Isaacson, Experimental Music, 1959: how they programmed the ILLIAC I at Illinois to compose the Illiac Suite for string quartet. Its fourth movement is made with Markov chains.', 'markov-melody', 'Markov melody'],
    'book-cage': ['John Cage, Silence, 1961. In it he tells of entering the anechoic chamber at Harvard and hearing two sounds, one high and one low: his nervous system and his blood.', 'an-echo-in-an-empty-room', 'An echo in an empty room'],
    'book-mccracken': ['Daniel D. McCracken, A Guide to FORTRAN Programming, 1961: one of the first books to teach the language, statement by statement.', 'squares-and-roots', 'Squares and roots'],
    'book-knuth': ['Donald Knuth, The Art of Computer Programming, volume 2: Seminumerical Algorithms, 1969. Its first chapter is on random numbers: how a machine that only follows rules makes numbers that pass for chance, and how to test them.', 'stochastic-cloud', 'Stochastic cloud'],
    'book-reichardt': ['Cybernetic Serendipity: the computer and the arts, 1968, edited by Jasia Reichardt: Studio International’s special issue for her show at the ICA in London, Knowlton and Harmon’s pictures among its pages.', 'studies-in-perception', 'Studies in perception'],
    camera: [null],
    'o-album': ['A photo album in black cloth: black-and-white prints and a few Polaroids, of places and of people, each held by its corners and captioned in white pencil.'],
    'o-timer': ['A tomato kitchen timer, for working in pomodoros: twenty-five minutes of work, then a short break, and after every fourth a long one. Francesco Cirillo named the method after a timer like it, in the late 1980s.'],
    'o-console': ['A pocket game console, grey, its screen grey-green, its batteries still good. In it is a game of falling blocks.'],
    metronome: ['A wooden metronome. György Ligeti’s Poème symphonique, 1962, is for a hundred of them, wound, set going at once and left to run down.', 'poeme-symphonique', 'Poème symphonique'],
    tank: ['A planted tank: a school of neon tetras, an angelfish, and a corydoras that keeps to the gravel, among vallisneria, a sword plant and a piece of driftwood. Press it to feed them.'],
    'chair-lounge': ['A teak lounge chair, slate cushions buttoned twice, a terracotta throw over its arm and a book left open face down on the seat.'],
    'chair-butterfly': ['A butterfly chair: one sling of tan leather hung by its corners from two loops of black iron rod.'],
    'chair-wire': ['A diamond chair of welded steel wire, a lattice you can see the wall through, a terracotta pad on its seat.'],
    'chair-tub': ['A low tub chair in mustard bouclé, its back and arms one rounded wall. Easy to get into, hard to get out of.'],
    clock: [null],
    'lamp-switch': [null],
    wall: [null]
  };
  var PAPER = { ogee: 'A deep blue paper under an ogee trellis, cream seed pods in its cells.', atomic: 'A sage paper of cream starbursts and ochre boomerangs.',
    trellis: 'A burnt umber paper, a diamond trellis with cream buds at its crossings.', grass: 'An ivory grasscloth, its fibres in fine vertical stripes.' };

  function keyOf(el) {
    if (el === 'wall') return 'wall';
    if (el.classList.contains('lamp-switch')) return 'lamp-switch';
    var sw = el.getAttribute('data-swap');
    if (sw) return Decor.item(sw);
    for (var k in LOOK) if (el.classList.contains(k)) return k;
    return null;
  }
  function lineOf(k) {
    if (k === 'wall') return [PAPER[Decor.paper()] + ' Press the bare wall to hang another.'];
    if (k === 'camera') return ['A 35 mm single-lens reflex, its film the full frame of 24 by 36 millimetres that Barnack’s Leica set in 1925, loaded with black-and-white film, ' + Corner.frames() + ' of its 36 frames taken.'];
    if (k === 'clock') return ['A black cat clock, its eyes and tail swinging to the seconds, keeping the visitor’s own time. ' + Corner.time()];
    if (k === 'lamp-switch') return [Decor.lampOn() ? 'A toggle switch, up. The lamp is on.' : 'A toggle switch, down. The lamp is off, and the room is lit by the screen and ' + { morning: 'the morning', evening: 'the dusk', night: 'the moon' }[Decor.time()] + '.'];
    return LOOK[k];
  }

  /* the narrator's line: ink, paper type, along the foot of the room */
  var box = doc.createElement('div'), text = doc.createElement('p'), offer = doc.createElement('button');
  box.className = 'narration'; box.hidden = true; box.setAttribute('role', 'status');
  text.className = 'narration-text';
  offer.type = 'button'; offer.className = 'narration-deck';
  box.appendChild(text); box.appendChild(offer);
  scene.appendChild(box);
  var timer = null;
  function look(el) {
    var k = keyOf(el), line = k && lineOf(k);
    if (!line) return;
    text.textContent = line[0];
    offer.hidden = !line[1];
    if (line[1]) { offer.setAttribute('data-deck', line[1]); offer.textContent = 'Put ' + line[2] + ' on the coding form'; }
    else offer.removeAttribute('data-deck');
    box.hidden = false;
    scene.dispatchEvent(new CustomEvent('room:look', { detail: { what: k } }));
    clearTimeout(timer);
    timer = setTimeout(close, line[1] ? 14000 : 9000);
  }
  function close() {
    box.hidden = true; clearTimeout(timer);
    // a book taken down to be read about goes back on its shelf
    Array.prototype.forEach.call(scene.querySelectorAll('.book.taken'), function (b) { b.classList.remove('taken'); });
  }
  offer.addEventListener('click', close);

  function spotOf(t) { return t.closest && t.closest('.overview .obj, .overview .swap'); }
  // what is under the pointer, for L
  var hovered = null;
  scene.addEventListener('pointermove', function (e) { hovered = spotOf(e.target) || (Decor.wallAt(e) ? 'wall' : null); });
  scene.addEventListener('pointerleave', function () { hovered = null; });
  // the right button looks
  scene.addEventListener('contextmenu', function (e) {
    if (LIST.matches || e.target.closest('.narration')) return;
    var s = spotOf(e.target) || (Decor.wallAt(e) ? 'wall' : null);
    if (!s) return;
    e.preventDefault();
    look(s);
  });
  // a press anywhere but the narration puts it away (and does whatever the press does)
  scene.addEventListener('pointerdown', function (e) { if (e.button === 0 && !e.target.closest('.narration')) close(); });
  doc.addEventListener('keydown', function (e) {
    if (LIST.matches || Desk.current() !== 'desk' || e.altKey || e.ctrlKey || e.metaKey) return;
    var t = doc.activeElement;
    if (t && /^(INPUT|TEXTAREA|SELECT)$/.test(t.tagName)) return;
    if (e.key === 'Escape' && !box.hidden) { close(); e.stopPropagation(); return; }
    if (e.key !== 'l' && e.key !== 'L') return;
    var s = spotOf(t) || hovered;
    if (s) { e.preventDefault(); look(s); }
  }, true);
  // taking a thing up puts the narration away
  ['manual', 'magazine', 'portfolio', 'form', 'out', 'computer', 'recorder', 'reader', 'upic', 'console', 'timer', 'album'].forEach(function (n) { Desk.onShow(n, close); });
  scene.addEventListener('room:turn', close);
  window.Look = { look: look };
})();
