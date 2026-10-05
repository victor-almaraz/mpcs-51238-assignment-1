/* The Dada miscellanea: five documents of chance and nonsense, 1913 to 1924, each with a
   little machine in it. Duchamp's threads and Arp's squares are pictures drawn once in
   the room's palette and kept as PNGs, eight falls of each, one chosen afresh when the window
   opens or the button is pressed; Man Ray's bars are elements, built from the text they
   black out. Sound goes through Tape, and the cut-up poem goes to the Editor through
   Workspace.openText. Needs Desk (wm.js), Fortran, Tape and Workspace (workspace.js). */

(function () {
  'use strict';
  var doc = document, $ = Desk.$, $$ = Desk.$$, plural = Desk.plural;
  // A fresh one of n pictures, never the one already showing
  function another(n, now) { var k; do k = Math.floor(Math.random() * n); while (n > 1 && k === now); return k; }

  /* ---------------- Duchamp: three threads of one metre, let fall ---------------- */
  // The falls are pictures drawn once, in the palette, and kept as PNGs (like the
  // other pictures of the documents): each thread a metre (240 screen pixels) walked out in
  // gentle random bends on its blue strip, with the span between its ends marked under it.
  // FALLS holds those spans, in metres, for each of the eight falls.
  var FALLS = [[0.93, 0.97, 0.97], [0.96, 0.95, 1.0], [0.98, 0.94, 0.98], [0.98, 0.99, 0.93], [0.99, 0.95, 0.95], [0.95, 0.97, 0.97], [0.95, 0.97, 0.97], [0.98, 0.95, 0.96]], fall = 0;
  function dropThreads() {
    fall = another(FALLS.length, fall);
    var spans = FALLS[fall], img = $('dd-stop-c');
    img.src = '../assets/pics/dada-stoppages-' + (fall + 1) + '.png';
    $('dd-stop-read').textContent = 'The ruler is one metre. The threads span ' + spans.map(function (v) { return v.toFixed(2) + ' m'; }).join(', ') + ' between their ends, marked under each strip.';
    img.alt = 'Three threads, each one metre long, lying where they fell on three blue strips; between their ends they span ' + spans.map(function (v) { return v.toFixed(2); }).join(', ') + ' metres';
  }
  Desk.onOpen('win-dd-stoppages', dropThreads);
  $('dd-stop-drop').addEventListener('click', dropThreads);

  /* ---------------- Arp: squares dropped on a sheet ---------------- */
  // eight drops, drawn once and kept as PNGs: torn squares of ink, grey, blue and paper
  // on a yellow sheet
  var DROPS = 8, drop = 0;
  function dropSquares() { drop = another(DROPS, drop); $('dd-arp-c').src = '../assets/pics/dada-arp-' + (drop + 1) + '.png'; }
  Desk.onOpen('win-dd-arp', dropSquares);
  $('dd-arp-drop').addEventListener('click', dropSquares);

  /* ---------------- Ball: the vowels of Karawane, sounded ---------------- */
  // u, o, a, e, i from low to high, as their first formants run; one syllable to a pulse,
  // a pulse between words and two between lines
  var VOWEL = { u: 55, 'ü': 55, o: 59, 'ô': 59, a: 62, e: 66, 'é': 66, i: 69 };
  var kwLines = $$('#win-dd-karawane .kw p'), kwEvents = [], kwStarts = [], BPM = 150;
  (function () {
    var t = 0;
    kwLines.forEach(function (p) {
      kwStarts.push(t);
      p.textContent.toLowerCase().split(/\s+/).forEach(function (word) {
        (word.match(/[aeiouüôé]+/g) || []).forEach(function (v) { kwEvents.push({ time: t, note: VOWEL[v.charAt(0)], len: 1, loud: 6 }); t++; });
        t++;
      });
      t += 2;
    });
  })();
  var kwPlayer = null, kwOn = false;
  function kwTick(st) {
    var pulse = st.position / (60 / (BPM * 4)), at = -1;
    kwStarts.forEach(function (s, i) { if (pulse >= s) at = i; });
    kwLines.forEach(function (p, i) { p.classList.toggle('now', st.playing && i === at); });
    if (!st.playing && kwOn && st.position >= st.duration) kwStop();
  }
  function kwStop() { kwOn = false; if (kwPlayer) kwPlayer.stop(); $('dd-kw-play').textContent = 'Sound the vowels'; kwLines.forEach(function (p) { p.classList.remove('now'); }); }
  $('dd-kw-play').addEventListener('click', function () {
    if (kwOn) { kwStop(); return; }
    if (!kwPlayer) { kwPlayer = Tape.createPlayer({ bpm: BPM, hiss: 0.05, onTick: kwTick }); kwPlayer.load(kwEvents); }
    kwPlayer.stop(); kwOn = true; this.textContent = 'Stop'; kwPlayer.play();
  });
  Desk.onClose('win-dd-karawane', kwStop);

  /* ---------------- Tzara: the bag ---------------- */
  var poem = null;
  function shuffle(a) { for (var i = a.length - 1; i > 0; i--) { var j = Math.floor(Math.random() * (i + 1)), t = a[i]; a[i] = a[j]; a[j] = t; } return a; }
  // copied out in the order they leave the bag, two to five words to a line
  function cut() {
    var words = shuffle($('dd-article').value.split(/\s+/).filter(Boolean)), lines = [];
    if (!words.length) { $('dd-poem').textContent = 'The bag is empty. Put an article in it first.'; return; }
    while (words.length && lines.length < 12) {
      var n = 2 + Math.floor(Math.random() * 4), line = words.splice(0, n).join(' ');
      while (line.length > 48) { var k = line.lastIndexOf(' ', 48); if (k < 1) k = 48; lines.push(line.slice(0, k)); line = line.slice(k).trim(); }
      if (line) lines.push(line);
    }
    poem = lines.slice(0, 12);
    $('dd-poem').textContent = poem.join('\n') + (words.length ? '\n…' : '');
    $('dd-poem-note').textContent = (words.length ? plural(words.length, 'word') + ' stayed in the bag, as a poem here runs to twelve lines. ' : '') + 'In the Editor, the poem is a FORTRAN program that prints it, one line of the poem to a printed line, on a new page.';
    $('dd-poem-ed').disabled = false; $('dd-lg-poem').disabled = false;
  }
  // The poem as a program: one FORMAT of quoted lines, a slash between them, carried on
  // continuation cards numbered 1 to 9 and then A, B, C in column 6. Only characters the
  // keypunch has are kept, and apostrophes, which would close the quotes, are dropped.
  function program(lines) {
    var cards = ['C     A DADAIST POEM, AFTER TRISTAN TZARA (1920): THE WORDS OF AN',
      'C     ARTICLE CUT APART, SHAKEN IN A BAG AND COPIED OUT AS DRAWN.',
      '      WRITE (6,10)', '   10 FORMAT (1H1,'];
    var clean = lines.map(function (l) {
      return l.toUpperCase().split('').filter(function (ch) { return ch === ' ' || (ch !== "'" && Fortran.punches(ch).length > 0); }).join('').replace(/ +/g, ' ').trim();
    }).filter(Boolean);
    clean.forEach(function (l, i) {
      cards.push('     ' + '123456789ABC'.charAt(i) + ' ' + (i ? "1X,'" : "'") + l + "'" + (i < clean.length - 1 ? '/' : ')'));
    });
    return cards.concat(['      STOP', '      END']).join('\n');
  }
  $('dd-cut').addEventListener('click', cut);
  $('dd-poem-ed').addEventListener('click', function () {
    if (!poem) return;
    Workspace.openText('Dadaist poem', program(poem), 'FORTRAN source', 'A poem from Tzara’s bag, as a program that prints it. Run it to read the poem on the Printout.');
  });

  /* ---------------- Man Ray: the words blacked out ---------------- */
  // a bar for every word, built of elements, as it changes with the text: each character is
  // 5 screen pixels (10 CSS pixels), the monospaced face's advance, so the bars keep the
  // columns of a program
  function blackOut(lines, what) {
    lines = lines.slice(0, 40).map(function (l) { return l.slice(0, 80).replace(/\s+$/, ''); });
    while (lines.length > 1 && !lines[lines.length - 1]) lines.pop();
    var cols = Math.max(20, lines.reduce(function (m, l) { return Math.max(m, l.length); }, 0));
    var box = $('dd-lg-c'), frag = doc.createDocumentFragment(), bars = 0;
    box.style.width = 2 * (12 + 5 * cols) + 'px'; box.style.height = 2 * (12 + 12 * lines.length) + 'px';
    lines.forEach(function (l, r) {
      var re = /\S+/g, m;
      while ((m = re.exec(l))) {
        bars++;
        var bar = doc.createElement('span');
        bar.className = 'lg-bar';
        bar.style.left = 12 + 10 * m.index + 'px'; bar.style.top = 18 + 24 * r + 'px'; bar.style.width = 10 * m[0].length - 2 + 'px';
        frag.appendChild(bar);
      }
    });
    box.textContent = ''; box.appendChild(frag);
    $('dd-lg-info').textContent = plural(lines.length, 'line') + ', ' + plural(bars, 'bar');
    box.setAttribute('aria-label', plural(lines.length, 'line') + ' of black bars, ' + plural(bars, 'bar') + ' in all, blacking out ' + what);
  }
  function fromEditor() { blackOut($('src').value.split('\n'), 'the text in the Editor, “' + $('ed-name').textContent + '”'); }
  Desk.onOpen('win-dd-lautgedicht', fromEditor);
  $('dd-lg-ed').addEventListener('click', fromEditor);
  $('dd-lg-poem').addEventListener('click', function () { if (poem) blackOut(poem, 'the cut-up poem'); });
})();
