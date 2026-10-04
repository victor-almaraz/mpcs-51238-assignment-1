/* The Dada miscellanea: five documents of chance and nonsense, 1913 to 1924, each with a
   little machine in it. Duchamp's threads and Arp's squares are drawn as SVG afresh each
   time the window opens or the button is pressed, so no two falls are alike; Man Ray's bars
   are elements, built from the text they black out. Sound goes through Tape, and the cut-up
   poem goes to the Editor through Workspace.openText. Needs Desk (wm.js), Fortran, Tape and
   Workspace (workspace.js). */

(function () {
  'use strict';
  var doc = document, $ = Desk.$, $$ = Desk.$$, plural = Desk.plural;
  var rnd = Math.random, COL = 9;
  function f1(v) { return v.toFixed(1); }

  /* ---------------- Duchamp: three threads of one metre, let fall ---------------- */
  // Each thread is a metre (480 units) let fall on its strip of Prussian blue: its heading
  // wanders as the sum of three slow waves of chance phase and size, so it bends gently as a
  // thread does, and a thread that would leave its strip is let fall flatter. Under each
  // strip, a rule marks the span between the thread's two ends.
  var M = 480, STRIP_H = 76;
  function fallOne() {
    for (var tries = 0; tries < 12; tries++) {
      var waves = [0, 1, 2].map(function (k) { return { a: (0.45 - k * 0.12) * (rnd() * 2 - 1) * Math.pow(0.8, tries), f: 0.6 + k * 0.9 + rnd() * 0.8, p: rnd() * 6.283 }; });
      var x = 0, y = 0, pts = [[0, 0]], N = 160, ds = M / N, lo = 0, hi = 0;
      for (var i = 1; i <= N; i++) {
        var t = i / N, th = 0;
        waves.forEach(function (w) { th += w.a * Math.sin(6.283 * w.f * t + w.p); });
        x += ds * Math.cos(th); y += ds * Math.sin(th);
        pts.push([x, y]); lo = Math.min(lo, y); hi = Math.max(hi, y);
      }
      if (hi - lo < STRIP_H - 18) return { pts: pts, lo: lo, hi: hi, span: Math.hypot(x, y) / M };
    }
    return { pts: [[0, 0], [M, 0]], lo: 0, hi: 0, span: 1 };
  }
  function dropThreads() {
    var svg = $('dd-stop-c'), W = 600, H = 400, out = [], spans = [];
    out.push('<rect class="dd-sheet" width="' + W + '" height="' + H + '"/>');
    // the metre itself, as a ruler across the head of the sheet
    var rx = 60, ticks = '';
    for (var k = 0; k <= 10; k++) ticks += 'M' + (rx + k * M / 10) + ' 30v' + (k % 5 ? -5 : -9);
    out.push('<path class="dd-rule" d="M' + rx + ' 30h' + M + ticks + '"/><text class="dd-lbl" x="' + (rx + M + 8) + '" y="31">1 m</text>');
    for (var n = 0; n < 3; n++) {
      var top = 52 + n * 114, th = fallOne(), x0 = rx, y0 = top + STRIP_H / 2 - (th.lo + th.hi) / 2;
      spans.push(th.span);
      out.push('<rect class="dd-strip" x="30" y="' + top + '" width="540" height="' + STRIP_H + '" rx="2"/>');
      var d = th.pts.map(function (p, i) { return (i ? 'L' : 'M') + f1(x0 + p[0]) + ' ' + f1(y0 + p[1]); }).join('');
      out.push('<path class="dd-thread-sh" d="' + d + '" transform="translate(1.2 1.6)"/><path class="dd-thread" d="' + d + '"/>');
      var last = th.pts[th.pts.length - 1], ex = x0 + last[0], by = top + STRIP_H + 14;
      out.push('<path class="dd-rule" d="M' + x0 + ' ' + (by - 5) + 'v10M' + f1(ex) + ' ' + (by - 5) + 'v10M' + x0 + ' ' + by + 'H' + f1(ex) + '"/>' +
        '<text class="dd-lbl" x="' + f1(ex + 8) + '" y="' + (by + 4) + '">' + th.span.toFixed(2) + ' m</text>');
    }
    svg.innerHTML = out.join('');
    $('dd-stop-read').textContent = 'The ruler is one metre. The threads span ' + spans.map(function (v) { return v.toFixed(2) + ' m'; }).join(', ') + ' between their ends, marked under each strip.';
    svg.setAttribute('aria-label', 'Three threads, each one metre long, lying where they fell on three blue strips; between their ends they span ' + spans.map(function (v) { return v.toFixed(2); }).join(', ') + ' metres');
  }
  Desk.onOpen('win-dd-stoppages', dropThreads);
  $('dd-stop-drop').addEventListener('click', dropThreads);

  /* ---------------- Arp: squares dropped on a sheet ---------------- */
  // A dozen squares and oblongs of paper, torn along their edges, let fall on a sheet and
  // pasted where they lay: black, grey, slate blue and white, near square to the sheet, as
  // Arp's are, overlapping where they happen to.
  var PAPERS = ['#1e1d1b', '#1e1d1b', '#1e1d1b', '#8d8a84', '#49606f', '#fbf9f3', '#2b4560'];
  function torn(x, y, w, h) {
    var pts = [], corners = [[x, y], [x + w, y], [x + w, y + h], [x, y + h]];
    corners.forEach(function (c, i) {
      var d = corners[(i + 1) % 4], len = Math.hypot(d[0] - c[0], d[1] - c[1]), n = Math.max(3, Math.round(len / 6));
      var nx = -(d[1] - c[1]) / len, ny = (d[0] - c[0]) / len;
      for (var k = 0; k < n; k++) {
        var t = k / n, j = k ? (rnd() - 0.5) * 2.6 : 0;
        pts.push(f1(c[0] + (d[0] - c[0]) * t + nx * j) + ' ' + f1(c[1] + (d[1] - c[1]) * t + ny * j));
      }
    });
    return 'M' + pts.join('L') + 'z';
  }
  function dropSquares() {
    var svg = $('dd-arp-c'), W = 560, H = 400, out = ['<rect class="dd-ground" width="' + W + '" height="' + H + '"/>'];
    var n = 10 + Math.floor(rnd() * 5);
    for (var i = 0; i < n; i++) {
      var s = 34 + rnd() * 46, w = s * (rnd() < 0.3 ? 1.3 + rnd() * 0.5 : 1), h = s;
      var x = 30 + rnd() * (W - 60 - w), y = 30 + rnd() * (H - 60 - h), a = (rnd() - 0.5) * 7;
      var tr = ' transform="rotate(' + f1(a) + ' ' + f1(x + w / 2) + ' ' + f1(y + h / 2) + ')"', d = torn(x, y, w, h);
      out.push('<path class="dd-sq-sh" d="' + d + '"' + tr + '/><path d="' + d + '" fill="' + PAPERS[Math.floor(rnd() * PAPERS.length)] + '"' + tr + '/>');
    }
    svg.innerHTML = out.join('');
    svg.setAttribute('aria-label', plural(n, 'torn square') + ' and oblongs of paper, black, grey, blue and white, scattered on a sheet where they fell');
  }
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
  // 9 pixels, the monospaced face's advance at 15px, so the bars keep the columns of a program
  function blackOut(lines, what) {
    lines = lines.slice(0, 40).map(function (l) { return l.slice(0, 80).replace(/\s+$/, ''); });
    while (lines.length > 1 && !lines[lines.length - 1]) lines.pop();
    var cols = Math.max(20, lines.reduce(function (m, l) { return Math.max(m, l.length); }, 0));
    var box = $('dd-lg-c'), frag = doc.createDocumentFragment(), bars = 0;
    box.style.width = 24 + COL * cols + 'px'; box.style.height = 24 + 24 * lines.length + 'px';
    lines.forEach(function (l, r) {
      var re = /\S+/g, m;
      while ((m = re.exec(l))) {
        bars++;
        var bar = doc.createElement('span');
        bar.className = 'lg-bar';
        bar.style.left = 12 + COL * m.index + 'px'; bar.style.top = 18 + 24 * r + 'px'; bar.style.width = COL * m[0].length - 2 + 'px';
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
