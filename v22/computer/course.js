/* Eighty Columns: a course of ten sheets in punched cards, each in a window of its own.
   A sheet is built the first time it opens, so a closed sheet costs nothing. Every answer is
   checked with the engine: the holes are read by Fortran.decodeCard, and decks are run by
   Fortran.run and their printer output compared with the target's. Progress lasts while the
   page is open; nothing is stored. Needs Desk, Workspace and Cards. */

(function () {
  'use strict';
  var doc = document, $ = Desk.$, $$ = Desk.$$, el = Desk.el, plural = Desk.plural, C = Cards;
  var rtrim = C.rtrim, pick = C.pick, rowsText = C.rowsText, readColumn = C.readColumn, showCh = C.showCh;

  /* ---------------- progress ---------------- */
  var TITLES = {}, solved = {};
  for (var t = 1; t <= 10; t++) TITLES[t] = $('win-sheet-' + t).querySelector('.sheet-t').textContent;
  function two(n) { return (n < 10 ? '0' : '') + n; }
  function updateProgress() {
    var count = 0;
    for (var n = 1; n <= 10; n++) {
      var on = !!solved[n];
      if (on) count++;
      $('progress-index').children[n - 1].classList.toggle('done', on);
      var row = doc.querySelector('#sheet-list [data-sheet="' + n + '"]');
      row.classList.toggle('done', on);
      row.querySelector('.sl-s').textContent = on ? 'solved' : '';
      var stamp = doc.querySelector('#win-sheet-' + n + ' .stamp');
      if (stamp) stamp.hidden = !on;
    }
    $('progress-text').textContent = count === 0 ? 'None of the ten sheets is solved yet.' :
      count === 10 ? 'All ten sheets are solved.' : plural(count, 'sheet') + ' of ten ' + (count === 1 ? 'is' : 'are') + ' solved.';
  }
  function solve(n) { solved[n] = true; updateProgress(); }
  // a solved sheet offers the next one, which replaces it on the desk
  function next(n) {
    if (n >= 10) return null;
    var b = el('button', 'btn default', 'Open sheet ' + two(n + 1) + ', ' + TITLES[n + 1]);
    b.type = 'button'; b.setAttribute('data-act', 'doc:sheet-' + (n + 1));
    var p = el('p', 'fb-next'); p.appendChild(b);
    return { node: p };
  }

  /* ---------------- hints, checks, resets ---------------- */
  var hintSets = {}, hintShown = {}, checks = {}, resets = {}, decks = {};
  function setHints(id, list) { hintSets[id] = list; hintShown[id] = 0; var ol = $(id + '-hints'); ol.innerHTML = ''; ol.hidden = true; hintButton(id); }
  function hintButton(id) {
    var b = doc.querySelector('[data-hint="' + id + '"]'), total = hintSets[id].length, k = hintShown[id];
    b.disabled = k >= total;
    b.textContent = k >= total ? 'No more hints' : 'Show a hint (' + (k + 1) + ' of ' + total + ')';
  }
  doc.addEventListener('click', function (e) {
    var b = e.target.closest && e.target.closest('[data-hint], [data-check], [data-reset], [data-bench]');
    if (!b || b.disabled) return;
    var id;
    if ((id = b.getAttribute('data-check'))) checks[id]();
    else if ((id = b.getAttribute('data-reset'))) resets[id]();
    else if ((id = b.getAttribute('data-bench'))) {
      var n = +id.slice(1);
      Workspace.openText('Deck from sheet ' + two(n), decks[id]().join('\n'), 'FORTRAN source', 'Opened the deck from sheet ' + two(n) + '. Changes here do not affect the sheet.');
    } else if ((id = b.getAttribute('data-hint'))) {
      var list = hintSets[id], k = hintShown[id];
      if (!list || k >= list.length) return;
      var h = typeof list[k] === 'function' ? list[k]() : list[k], li = el('li');
      if (typeof h === 'string') li.textContent = h;
      else { li.appendChild(doc.createTextNode(h.text)); li.appendChild(el('pre', 'hint-pre', h.pre)); }
      var ol = $(id + '-hints'); ol.appendChild(li); ol.hidden = false;
      hintShown[id] = k + 1;
      hintButton(id);
    }
  });
  function answerHint(text, cards) { return { text: text, pre: C.rulerText(40) + '\n' + cards.join('\n') }; }
  function runAndCompare(cards, target) { var r = Fortran.run(cards); return { r: r, same: r.ok && C.samePrinter(target, r.printer) }; }
  function badCols(text) {
    var m = Fortran.encodeCard(text.padEnd(80)), out = [];
    for (var c = 0; c < 80; c++) if (!readColumn(m[c]).valid) out.push(c + 1);
    return out;
  }
  // notes on a statement card: where its label, continuation and statement sit
  function fieldNotes(text, n, want) {
    var t = text.padEnd(80), notes = [], lab = t.slice(0, 5), c6 = t.charAt(5), body = t.slice(6, 72);
    if (t.charAt(0) === 'C' || t.charAt(0) === '*') { notes.push('Card ' + n + ' has ' + showCh(t.charAt(0)) + ' in column 1, so the whole card is a comment and the reader skips it.'); return notes; }
    if (want.label !== undefined) {
      var l = lab.replace(/ /g, '');
      if (l === '') notes.push('Card ' + n + ' has no label in columns 1 to 5. It needs the label ' + want.label + '.');
      else if (!/^\d+$/.test(l)) notes.push('Columns 1 to 5 of card ' + n + ' hold ' + showCh(lab.trim()) + ', which is not a number. Only the label goes there; the statement starts in column 7.');
      else if (+l !== want.label) notes.push('Card ' + n + ' has the label ' + l + ', but this statement needs the label ' + want.label + '.');
    }
    if (want.cont) {
      if (c6 === ' ' || c6 === '0') notes.push('Column 6 of card ' + n + ' is ' + (c6 === ' ' ? 'blank' : 'a zero') + ', so the reader takes the card as a new statement instead of a continuation.');
      if (lab.trim() !== '') notes.push('Columns 1 to 5 of a continuation card should be blank. Card ' + n + ' has ' + showCh(lab.trim()) + ' there.');
    } else if (c6 !== ' ' && c6 !== '0') {
      notes.push('Column 6 of card ' + n + ' holds ' + showCh(c6) + ', so the reader takes the card as a continuation of the card before it. Leave column 6 blank and start the statement in column 7.');
    }
    if (t.slice(72).trim() !== '') notes.push('Card ' + n + ' has something in columns 73 to 80, which the compiler ignores. Your statement may run past column 72.');
    if (!body.trim() && !want.cont) notes.push('Columns 7 to 72 of card ' + n + ' are blank, so it holds no statement.');
    var bad = badCols(text);
    if (bad.length) notes.push('Column ' + bad.join(', ') + ' of card ' + n + ' has holes that do not make a character.');
    return notes;
  }
  // the usual failure report for a deck sheet
  function notYet(fb, notes, res, target) {
    if (res.r.ok && !res.same && target) notes = notes.concat([C.printerDiff(target, res.r.printer)]);
    fb.show('no', 'Not yet', notes.concat([{ diag: C.diagList(res.r.log) }, res.r.ok ? { printer: res.r.printer } : null]));
  }
  function fixedDeck(fix, blank) { return fix.map(function (t) { return t === null ? { text: blank || '', fixed: false } : { text: t, fixed: true }; }); }
  function target(id, cards) { var t = Fortran.run(cards).printer; Workspace.renderPrinter($(id + '-target'), t); return t; }

  /* ================================================================ the sheets */
  var BUILD = {};

  /* ---------------- 01: read a card ---------------- */
  BUILD[1] = function () {
    var POOL = ['      GO TO 20', '   10 X = A + B', '      PRINT 5, N', '      STOP 7', '   40 FORMAT (I5)',
      '      DO 50 I = 1, 9', '      Y = SQRT(X)', '      READ (5,10) K', '      IF (N) 10, 20, 30', '      WRITE (6,30) Z'];
    var fb = new C.Feedback($('l1-fb'));
    var grid = new C.Grid($('l1-card'), { readOnly: true, printed: false, label: 'Card to read, without printing' });
    var src = '';
    function fresh() {
      src = pick(POOL, src);
      grid.setMasks(Fortran.encodeCard(src));
      $('l1-answer').value = '';
      fb.clear();
      setHints('l1', [
        'Look at the zone rows first. A hole in row 12 with a digit hole is a letter from A to I, a hole in row 11 is J to R, and a hole in row 0 is S to Z. A single hole is a digit. The Punch Codes chart lists every code.',
        function () {
          var m = grid.masks, c = 0;
          while (c < 80 && !m[c].size) c++;
          var info = readColumn(m[c]);
          return 'The first punched column is column ' + (c + 1) + '. It has ' + C.holes(info.rows) + ', which is ' + showCh(info.ch) + '.';
        },
        'Columns 1 to 5 hold a statement label, if there is one, and the statement starts in column 7.'
      ]);
    }
    $('l1-new').addEventListener('click', fresh);
    $('l1-answer').addEventListener('keydown', function (e) { if (e.key === 'Enter') { e.preventDefault(); checks.l1(); } });
    checks.l1 = function () {
      var truth = Fortran.decodeCard(grid.masks);           // the engine reads the holes
      var want = truth.replace(/ /g, ''), got = $('l1-answer').value.toUpperCase().replace(/\s/g, '');
      if (!got) { fb.show('no', 'Not yet', ['Type what the card says into the field above the buttons first.']); return; }
      if (got === want) { solve(1); fb.show('ok', 'Correct', ['The card reads ' + truth.trim().replace(/ +/g, ' ') + '. Every column you decoded matches the holes.', 'Choose Another card to read one more.', next(1)]); return; }
      // line the typed characters up with the punched columns
      var cols = [];
      for (var c = 0; c < 80; c++) if (truth.charAt(c) !== ' ') cols.push(c);
      var k = 0;
      while (k < want.length && k < got.length && want.charAt(k) === got.charAt(k)) k++;
      var msg;
      if (k >= want.length) msg = 'You typed more characters than the card holds. The last punched column is column ' + (cols[cols.length - 1] + 1) + '.';
      else {
        var col = cols[k], info = readColumn(grid.masks[col]);
        msg = 'Column ' + (col + 1) + ' has ' + C.holes(info.rows) + ', which is ' + showCh(info.ch) + (k < got.length ? ', but you typed ' + showCh(got.charAt(k)) + ' there.' : '. Your answer stops before it.');
      }
      fb.show('no', 'Not yet', [msg, k ? 'Everything before that is right.' : '']);
    };
    fresh();
  };

  /* ---------------- 02: punch a character ---------------- */
  BUILD[2] = function () {
    var CLASSES = [
      { set: '0123456789', what: 'the digit', rule: 'A digit is one hole in the row with its own number.' },
      { set: 'ABCDEFGHI', what: 'the letter', rule: 'A to I take the zone hole in row 12, plus a digit hole that counts the place in the group: A is 1, B is 2, and so on to I, which is 9.' },
      { set: 'JKLMNOPQR', what: 'the letter', rule: 'J to R take the zone hole in row 11, plus a digit hole from 1 for J to 9 for R.' },
      { set: 'STUVWXYZ', what: 'the letter', rule: 'S to Z take the zone hole in row 0, plus a digit hole from 2 for S to 9 for Z.' },
      { set: "=+-*/(),.$'", what: 'the sign', rule: 'Most signs combine a hole in row 8 with a digit hole from 2 to 7, and some add a zone hole. The minus sign is a lone 11 hole, and the slash is 0-1. The second table of the Punch Codes chart lists them all.' }
    ];
    var fb = new C.Feedback($('l2-fb'));
    var grid = new C.Grid($('l2-card'), { cols: 5, typing: false, label: 'Five-column card' });
    var targets = [], round = 0;
    function fresh() { targets = CLASSES.map(function (k) { return pick(k.set.split('')); }); round = 0; grid.setText(''); grid.moveTo(0, 0, false); grid.status.textContent = ''; fb.clear(); show(); }
    function show() {
      var t = $('l2-target');
      t.innerHTML = '';
      if (round >= 5) { t.appendChild(el('span', 'tg-l', 'All five characters are punched.')); setHints('l2', ['Nothing is left to punch on this card. Choose Start again for five new characters.']); return; }
      var k = CLASSES[round], cur = targets[round];
      t.appendChild(el('span', 'tg-l', 'Column ' + (round + 1) + ' of 5: punch ' + k.what));
      t.appendChild(el('span', 'tg-big', cur));
      setHints('l2', [k.rule, function () { return showCh(cur) + ' is punched ' + rowsText(Fortran.punches(cur)) + '.'; }]);
    }
    $('l2-new').addEventListener('click', fresh);
    checks.l2 = function () {
      if (round >= 5) { fb.show('ok', 'Correct', ['All five characters are already punched. Choose Start again for new ones.']); return; }
      var ch = targets[round], want = Fortran.punches(ch), c = round, info = readColumn(grid.masks[c]), got = info.rows;
      if (rowsText(got) === rowsText(want)) {
        round++;
        show();
        if (round >= 5) { solve(2); fb.show('ok', 'Correct', [showCh(ch) + ' is ' + rowsText(want) + '. All five columns are right: the card reads ' + grid.getText() + '.', next(2)]); }
        else fb.show('ok', 'Correct', [showCh(ch) + ' is ' + rowsText(want) + '. Now punch column ' + (round + 1) + '.']);
        grid.moveTo(0, round, false);
        return;
      }
      var missing = want.filter(function (r) { return got.indexOf(r) === -1; }), extra = got.filter(function (r) { return want.indexOf(r) === -1; });
      var parts = [!got.length ? 'Column ' + (c + 1) + ' has no holes yet.' : 'Column ' + (c + 1) + ' has ' + C.holes(got) + ', which ' + (info.valid ? 'reads ' + showCh(info.ch) : 'is not a character on the 029') + '.'];
      var fix = [];
      if (missing.length) fix.push('punch row' + (missing.length > 1 ? 's ' : ' ') + C.orderRows(missing).join(' and '));
      if (extra.length) fix.push('clear row' + (extra.length > 1 ? 's ' : ' ') + C.orderRows(extra).join(' and '));
      parts.push(showCh(ch) + ' needs ' + plural(want.length, 'hole') + '. To get there, ' + fix.join(', and ') + '.');
      var others = [];
      for (var k = round + 1; k < 5; k++) if (grid.masks[k].size) others.push(k + 1);
      if (others.length) parts.push('Only column ' + (c + 1) + ' is checked now; the holes in column ' + others.join(' and ') + ' are ignored until its turn.');
      fb.show('no', 'Not yet', parts);
    };
    fresh();
  };

  /* ---------------- 03: punch a word ---------------- */
  BUILD[3] = function () {
    var POOL = ['A(I,J)', 'X=Y+1.5', 'N=N-1', 'GO TO 9', 'K=2*L', 'Z=X/Y', "'HELLO'", 'B$=C,D'];
    var fb = new C.Feedback($('l3-fb'));
    var grid = new C.Grid($('l3-card'), { cols: 10, typing: false, label: 'Ten-column card' });
    var word = '';
    function fresh() {
      word = pick(POOL, word);
      var t = $('l3-target');
      t.innerHTML = '';
      t.appendChild(el('span', 'tg-l', 'Punch, from column 1'));
      t.appendChild(el('span', 'tg-big', word));
      grid.setText(''); grid.moveTo(0, 0, false); grid.status.textContent = ''; fb.clear();
      setHints('l3', [
        'Work one column at a time. Punch a column, check the printing above it, and move to the next. The blank in an expression is a column with no holes.',
        function () {
          var c = 0, txt = rtrim(grid.getText());
          while (c < word.length && txt.charAt(c) === word.charAt(c)) c++;
          if (c >= word.length) return 'Every column already matches. Press Check.';
          return 'Column ' + (c + 1) + ' should be ' + showCh(word.charAt(c)) + ', which is punched ' + rowsText(Fortran.punches(word.charAt(c))) + '.';
        }
      ]);
    }
    $('l3-new').addEventListener('click', fresh);
    $('l3-clear').addEventListener('click', function () { grid.setText(''); grid.moveTo(0, 0, false); grid.status.textContent = 'The card is clear.'; });
    checks.l3 = function () {
      var got = rtrim(grid.getText()), bad = grid.badColumns();
      if (got === word && !bad.length) {
        solve(3);
        fb.show('ok', 'Correct', ['The card reads ' + word + ', one character in each of the first ' + word.length + ' columns.', 'From the next sheet on, the keypunch is switched on: typing on a card punches the codes for you.', next(3)]);
        return;
      }
      var wrong = [];
      for (var c = 0; c < 10; c++) {
        var w = word.charAt(c) || ' ', info = readColumn(grid.masks[c]);
        if (info.valid && info.ch === w) continue;
        var have = !info.rows.length ? 'is blank' : 'has ' + rowsText(info.rows) + (info.valid ? ', which is ' + showCh(info.ch) : ', which is not a character');
        wrong.push('Column ' + (c + 1) + ' ' + have + '. It should ' + (w === ' ' ? 'be blank.' : 'be ' + showCh(w) + ', punched ' + rowsText(Fortran.punches(w)) + '.'));
      }
      var parts = wrong.slice(0, 3);
      if (wrong.length > 3) parts.push('Another ' + plural(wrong.length - 3, 'column') + ' also differ' + (wrong.length - 3 === 1 ? 's' : '') + '.');
      fb.show('no', 'Not yet', parts);
    };
    fresh();
  };

  /* ---------------- 04: the card's fields ---------------- */
  BUILD[4] = function () {
    var FIX = ['      I = 7', '      GO TO 30', '      I = 0', null, '   40 FORMAT (1X,I3)', '      STOP', '      END'];
    var REF = ['C     PRINT THE VALUE OF I', '   30 WRITE (6,40) I'];
    function items() { return [{ text: '', fixed: false }].concat(fixedDeck(FIX)); }
    var tgt = target('l4', [REF[0]].concat(FIX.map(function (t) { return t === null ? REF[1] : t; })));
    var fb = new C.Feedback($('l4-fb'));
    var deck = new C.Deck($('l4-deck'), { name: 'Program deck', items: items() });
    resets.l4 = function () { deck.setItems(items()); fb.clear(); };
    decks.l4 = function () { return deck.cards(); };
    setHints('l4', [
      'Card 1 needs a C in column 1. After that, anything at all can follow, because the reader skips a comment card.',
      'On card 5, put the label 30 in columns 1 to 5, leave column 6 blank, and start WRITE in column 7. Right-justifying the label in column 5 was the custom, but anywhere in columns 1 to 5 works.',
      answerHint('A correct pair of cards, with a column ruler:', REF)
    ]);
    checks.l4 = function () {
      var cards = deck.cards(), c1 = cards[0].padEnd(80), notes = [], res = runAndCompare(cards, tgt);
      var isComment = c1.charAt(0) === 'C' || c1.charAt(0) === '*';
      if (!isComment) notes.push(cards[0].trim() === '' ? 'Card 1 is still blank. Punch a C in column 1 and a few words after it.' : 'Card 1 has ' + showCh(c1.charAt(0)) + ' in column 1, so the reader takes it as a statement, not a comment. Put a C in column 1.');
      else if (c1.slice(1).trim() === '') notes.push('Card 1 is a comment, but it says nothing. Add a few words that describe the program.');
      if (res.same && !notes.length) {
        solve(4);
        fb.show('ok', 'Correct', ['The program ran and printed ' + rtrim(res.r.printer[0]).trim() + '. Card 1 is a comment, and card 5 carries label 30 in the label field with its statement from column 7.', next(4)]);
        return;
      }
      notYet(fb, notes.concat(fieldNotes(cards[4], 5, { label: 30 })), res, tgt);
    };
  };

  /* ---------------- 05: continuation ---------------- */
  BUILD[5] = function () {
    var FIX = ['C     ONE LONG LINE OF PRINT', '      WRITE (6,10)', "   10 FORMAT (1X,'THE CARD READER TAKES ONE CARD AT A TIME,',", null, '      STOP', '      END'];
    var REF = "     1' AND THE PRINTER ONE LINE AT A TIME.')";
    var tgt = target('l5', FIX.map(function (t) { return t === null ? REF : t; }));
    var fb = new C.Feedback($('l5-fb'));
    var deck = new C.Deck($('l5-deck'), { name: 'Program deck', items: fixedDeck(FIX) });
    resets.l5 = function () { deck.setItems(fixedDeck(FIX)); fb.clear(); };
    decks.l5 = function () { return deck.cards(); };
    setHints('l5', [
      'Compare the target with the text on card 3. The rest of the line, from the blank after the comma onwards, still has to be printed, inside its own pair of quotes.',
      'Punch a 1 (or any character but a blank or 0) in column 6, and start the text in column 7. The statement still needs its closing parenthesis.',
      answerHint('A correct card 4, with a column ruler:', [REF])
    ]);
    checks.l5 = function () {
      var cards = deck.cards(), res = runAndCompare(cards, tgt);
      if (res.same) { solve(5); fb.show('ok', 'Correct', ['Card 4 continues statement 10, and the printer prints the whole line of ' + rtrim(tgt[0]).length + ' characters.', next(5)]); return; }
      notYet(fb, fieldNotes(cards[3], 4, { cont: true }), res, tgt);
    };
  };

  /* ---------------- 06: the dropped deck ---------------- */
  BUILD[6] = function () {
    var SRC = ['C     A TABLE OF SQUARES', 'C     EACH LINE GIVES N AND N SQUARED', '      WRITE (6,10)', '   10 FORMAT (1H1,5X,1HN,6X,6HSQUARE)',
      '      DO 20 I = 1, 5', '      ISQ = I*I', '      WRITE (6,30) I, ISQ', '   20 CONTINUE', '   30 FORMAT (1X,I6,I12)', '      STOP', '      END'];
    var ORDERED = SRC.map(function (t, i) { return t.padEnd(72) + 'SQRS' + String((i + 1) * 10).padStart(4, '0'); });
    var tgt = Fortran.run(ORDERED).printer;
    var fb = new C.Feedback($('l6-fb'));
    var order = [], sel = 0;
    var list = C.listWrap($('l6-deck'), 'Dropped deck', 'movable');
    var grid = new C.Grid($('l6-deck'), { readOnly: true, label: 'Selected card' });
    var colSel = $('l6-col');
    for (var c = 73; c <= 80; c++) { var o = el('option', '', String(c)); o.value = String(c); colSel.appendChild(o); }
    colSel.value = '80';
    function seqOf(t) { return t.slice(72, 80); }
    function render(focusIdx, what) {
      list.innerHTML = '';
      var frag = doc.createDocumentFragment();
      order.forEach(function (t, i) {
        var li = el('li', 'mv' + (i === sel ? ' sel' : '')), b = el('button', 'slot-b');
        b.type = 'button';
        b.appendChild(el('span', 'num', String(i + 1))); b.appendChild(el('code', 'line', t));
        b.setAttribute('aria-label', 'Position ' + (i + 1) + ': sequence ' + seqOf(t) + ', ' + t.slice(0, 72).replace(/ +/g, ' ').trim());
        b.setAttribute('aria-pressed', String(i === sel));
        b.addEventListener('click', function () { sel = i; render(i, 'card'); });
        li.appendChild(b);
        var up = el('button', 'btn mv-b', 'Up'), dn = el('button', 'btn mv-b', 'Down');
        up.type = dn.type = 'button';
        up.setAttribute('aria-label', 'Move ' + seqOf(t) + ' up'); dn.setAttribute('aria-label', 'Move ' + seqOf(t) + ' down');
        up.disabled = i === 0; dn.disabled = i === order.length - 1;
        up.addEventListener('click', function () { swap(i, i - 1, 'up'); });
        dn.addEventListener('click', function () { swap(i, i + 1, 'down'); });
        li.appendChild(up); li.appendChild(dn);
        frag.appendChild(li);
      });
      list.appendChild(frag);
      grid.setMasks(Fortran.encodeCard(order[sel]));
      grid.setLabel('Card at position ' + (sel + 1) + ', sequence ' + seqOf(order[sel]));
      if (focusIdx !== undefined) {
        var li2 = list.children[focusIdx], bs = li2.querySelectorAll('.mv-b');
        var f = what === 'up' ? bs[0] : what === 'down' ? bs[1] : li2.querySelector('.slot-b');
        if (f.disabled) f = li2.querySelector('.slot-b');
        f.focus();
      }
    }
    function swap(i, j, what) { var t = order[i]; order[i] = order[j]; order[j] = t; sel = j; render(j, what); }
    function shuffle() {
      do {
        order = ORDERED.slice();
        for (var i = order.length - 1; i > 0; i--) { var j = Math.floor(Math.random() * (i + 1)); var t = order[i]; order[i] = order[j]; order[j] = t; }
      } while (order.join() === ORDERED.join());
      sel = 0;
      $('l6-pockets').innerHTML = '';
      $('l6-sort-st').textContent = 'The deck is shuffled.';
      fb.clear();
      render();
    }
    // one pass of the sorter: pockets by the single digit hole in the column, read from the punches
    var POCKETS = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'R'];
    function sortPass(col) {
      var pockets = {};
      POCKETS.forEach(function (p) { pockets[p] = []; });
      order.forEach(function (t) {
        var rows = C.orderRows(Array.from(Fortran.encodeCard(t)[col - 1]));
        pockets[rows.length === 1 && rows[0] >= 0 && rows[0] <= 9 ? String(rows[0]) : 'R'].push(t);
      });
      order = [];
      POCKETS.forEach(function (p) { order = order.concat(pockets[p]); });
      return pockets;
    }
    $('l6-sort').addEventListener('click', function () {
      var col = +colSel.value, pockets = sortPass(col), box = $('l6-pockets'), max = 0, used = [];
      box.innerHTML = '';
      POCKETS.forEach(function (p) { max = Math.max(max, pockets[p].length); if (pockets[p].length) used.push((p === 'R' ? 'reject' : p) + ': ' + pockets[p].length); });
      // each pocket's stack is drawn card by card, 16px a card (8 on a narrow screen), the
      // cards' edges ruled every 16px (style.css)
      POCKETS.forEach(function (p) {
        var k = el('div', 'pk'), well = el('span', 'pk-well'), bar = el('span', 'pk-bar');
        bar.style.height = (Desk.narrowMQ.matches ? 8 : 16) * pockets[p].length + 'px';
        well.appendChild(bar); k.appendChild(well);
        k.appendChild(el('span', 'pk-n', String(pockets[p].length))); k.appendChild(el('span', 'pk-l', p));
        box.appendChild(k);
      });
      $('l6-sort-st').textContent = 'Sorted on column ' + col + '. Pockets ' + used.join(', ') + '. The pockets were stacked back from 0 to 9.';
      sel = 0;
      render();
    });
    $('l6-shuffle').addEventListener('click', shuffle);
    decks.l6 = function () { return order.slice(); };
    setHints('l6', [
      'The sequence numbers run SQRS0010, SQRS0020 and so on, in steps of ten. Column 80 is a 0 on every card, so sorting on it changes nothing.',
      'Sort on the rightmost column that differs first, then work leftwards: that is column 79, then column 78. The sorter keeps the cards in each pocket in the order they arrived, so each pass keeps the order the earlier passes made.',
      'If you prefer, use the Up and Down buttons to move each card until the sequence numbers run in order.'
    ]);
    checks.l6 = function () {
      var res = runAndCompare(order, tgt), inOrder = order.join('\n') === ORDERED.join('\n'), out = [];
      for (var i = 1; i < order.length; i++) if (seqOf(order[i]) < seqOf(order[i - 1])) out.push(i + 1);
      if (res.same && inOrder) {
        solve(6);
        fb.show('ok', 'Correct', ['The deck is back in sequence, from SQRS0010 to SQRS0110, and the program prints its table of squares.', { diag: C.diagList(res.r.log, { seqOk: true }) }, next(6)]);
        return;
      }
      var notes = [];
      if (out.length) notes.push(plural(out.length, 'card is', 'cards are') + ' out of sequence. The first is at position ' + out[0] + ': ' + seqOf(order[out[0] - 1]) + ' comes after ' + seqOf(order[out[0] - 2]) + '.');
      if (res.same) notes.push('The program happens to print the right output already, but a deck out of sequence is not finished: the next person to sort it would be misled.');
      else if (res.r.ok) notes.push(C.printerDiff(tgt, res.r.printer));
      else notes.push('With the cards in this order, the program does not run.');
      fb.show('no', 'Not yet', notes.concat([{ diag: C.diagList(res.r.log, { seqOk: true }) }]));
    };
    shuffle();
  };

  /* ---------------- 07: data cards ---------------- */
  BUILD[7] = function () {
    var ADDER = ['C     ADD UP A LIST OF NUMBERS', '      READ (5,10) N', '   10 FORMAT (I5)', '      ISUM = 0', '      DO 20 I = 1, N',
      '      READ (5,10) K', '      ISUM = ISUM + K', '   20 CONTINUE', '      WRITE (6,30) N, ISUM', '   30 FORMAT (1X,I3,13H NUMBERS SUM ,I6)', '      STOP', '      END'];
    var REF = ['    4', '   10', '   20', '   30', '   40'];
    function items() { return fixedDeck(ADDER).concat([{ text: '', fixed: false }]); }
    var tgt = target('l7', ADDER.concat(REF));
    var fb = new C.Feedback($('l7-fb'));
    var deck = new C.Deck($('l7-deck'), { name: 'Program and data deck', items: items(), add: true, addLabel: 'Add a data card after this one', max: 40 });
    resets.l7 = function () { deck.setItems(items()); fb.clear(); };
    decks.l7 = function () { return deck.cards(); };
    setHints('l7', [
      'The target says the program read 4 numbers, so the first data card holds the count 4, and four more cards follow it.',
      'Each number must fit in columns 1 to 5. Anything punched in column 6 or later is never read. Right-justify each number so its last digit is in column 5, as the I5 field was designed for.',
      answerHint('One correct set of data cards:', REF)
    ]);
    checks.l7 = function () {
      var cards = deck.cards(), res = runAndCompare(cards, tgt);
      if (res.same) { solve(7); fb.show('ok', 'Correct', ['The program read ' + deck.slots().map(function (s) { return s.text.trim(); }).join(', ') + ' and printed the target line.', next(7)]); return; }
      var notes = [];
      deck.slots().forEach(function (s) {
        var t = s.text.padEnd(80);
        if (t.slice(5).trim() !== '') notes.push('Card ' + (s.index + 1) + ' has something after column 5: ' + showCh(t.slice(5).trim()) + '. The I5 field never reads it.');
        if (s.text.trim() === '') notes.push('Card ' + (s.index + 1) + ' is blank, and a blank field reads as 0.');
      });
      if (res.r.log.some(function (l) { return /END OF FILE/.test(l); })) notes.push('The program asked for more data cards than the deck has. The first data card tells it how many numbers to read.');
      notYet(fb, notes, res, tgt);
    };
  };

  /* ---------------- 08: FORMAT and the line printer ---------------- */
  BUILD[8] = function () {
    var FIX = ['C     ONE REPORT LINE AT THE TOP OF A PAGE', '      N = 42', '      X = 3.5', '      WRITE (6,10) N, X', null, '      STOP', '      END'];
    var REF = '   10 FORMAT (1H1,3HN =,I5,6H   X =,F6.2)';
    var tgt = target('l8', FIX.map(function (t) { return t === null ? REF : t; }));
    var tbox = $('l8-target'), tr = el('pre', 'out-ruler', C.rulerText(32));
    tr.setAttribute('aria-hidden', 'true');
    tbox.insertBefore(tr, tbox.querySelector('pre'));
    var fb = new C.Feedback($('l8-fb'));
    var deck = new C.Deck($('l8-deck'), { name: 'Program deck', items: fixedDeck(FIX) });
    resets.l8 = function () { deck.setItems(fixedDeck(FIX)); fb.clear(); };
    decks.l8 = function () { return deck.cards(); };
    setHints('l8', [
      'Count the print positions in the target with the ruler above it. N is 42 and ends in position 8, so after "N =" it is printed in a field 5 wide: I5. X is 3.50, with two decimals, in a field 6 wide.',
      'The record must begin with the carriage control character 1 for a new page. 1H1 is a Hollerith constant of one character, the 1.',
      answerHint('A correct card 5, with a column ruler:', [REF])
    ]);
    checks.l8 = function () {
      var cards = deck.cards(), res = runAndCompare(cards, tgt);
      if (res.same) { solve(8); fb.show('ok', 'Correct', ['The printer starts a new page and prints the line exactly as the target shows it.', next(8)]); return; }
      var notes = fieldNotes(cards[4], 5, { label: 10 });
      if (cards[4].slice(6, 72).replace(/ /g, '').indexOf('FORMAT') !== 0 && cards[4].trim() !== '') notes.push('The statement on card 5 should begin with the word FORMAT.');
      notYet(fb, notes, res, tgt);
    };
  };

  /* ---------------- 09: punch, then feed back ---------------- */
  BUILD[9] = function () {
    var PROG_A = ['C     PUNCH N, THEN THE SQUARES OF 1 TO N', '      READ (5,10) N', '   10 FORMAT (I5)', '      PUNCH 10, N', '      DO 20 I = 1, N',
      '      ISQ = I*I', '      PUNCH 10, ISQ', '   20 CONTINUE', '      STOP', '      END'];
    var PROG_B = ['C     ADD UP THE CARDS THAT FOLLOW A COUNT', '      READ (5,10) N', '   10 FORMAT (I5)', '      ISUM = 0', '      DO 20 I = 1, N',
      '      READ (5,10) K', '      ISUM = ISUM + K', '   20 CONTINUE', '      WRITE (6,30) ISUM', '   30 FORMAT (1X,13HTHE TOTAL IS ,I6)', '      STOP', '      END'];
    var nTarget = 3 + Math.floor(Math.random() * 6);   // 3 to 8
    var tgt = target('l9', PROG_B.concat(Fortran.run(PROG_A.concat([String(nTarget).padStart(5)])).punched));
    var fb = new C.Feedback($('l9-fb')), lastPunched = null;
    function itemsA() { return fixedDeck(PROG_A).concat([{ text: '', fixed: false }]); }
    function itemsB(data) { return PROG_B.concat(data || []).map(function (t) { return { text: t, fixed: true }; }); }
    var deckA = new C.Deck($('l9-deck-a'), { name: 'Program A deck', items: itemsA(), onEdit: function () { if (lastPunched) $('l9-stack-st').textContent = 'The data card has changed since program A last ran. Run it again to punch new cards.'; } });
    var deckB = new C.Deck($('l9-deck-b'), { name: 'Program B deck', items: itemsB(), edit: false });
    var stack = C.listWrap($('l9-stack'), 'Output stacker');
    function renderStack(cards) {
      stack.innerHTML = '';
      (cards || []).forEach(function (t, i) {
        var li = el('li', 'fixed');
        li.appendChild(el('span', 'num', String(i + 1))); li.appendChild(el('code', 'line', t));
        li.setAttribute('aria-label', 'Punched card ' + (i + 1) + ': ' + (t.trim() || 'blank'));
        stack.appendChild(li);
      });
    }
    function reset() {
      deckA.setItems(itemsA()); deckB.setItems(itemsB());
      lastPunched = null; renderStack([]);
      $('l9-feed').disabled = true;
      $('l9-stack-st').textContent = 'Program A has not been run yet.';
      fb.clear();
    }
    resets.l9 = reset;
    $('l9-run-a').addEventListener('click', function () {
      var r = Fortran.run(deckA.cards()), d = C.diagList(r.log);
      lastPunched = r.punched;
      renderStack(r.punched);
      $('l9-feed').disabled = !r.punched.length;
      $('l9-stack-st').textContent = 'Program A ' + (r.ok ? 'ran' : 'stopped with errors') + ' and punched ' + plural(r.punched.length, 'card') + '.' + (d.length ? ' ' + d.join(' ') : '');
    });
    $('l9-feed').addEventListener('click', function () {
      if (!lastPunched) return;
      deckB.setItems(itemsB(lastPunched.map(rtrim)));
      $('l9-stack-st').textContent = 'The ' + plural(lastPunched.length, 'punched card') + ' now follow' + (lastPunched.length === 1 ? 's' : '') + ' the END card of program B.';
    });
    setHints('l9', [
      'Program B prints 1 + 4 + 9 + ... up to N squared. Add squares until you reach the target total; the last number you squared is N.',
      'Punch N right-justified in columns 1 to 5 of program A’s data card, then press Run program A, then Feed the stacker to program B.',
      function () { return 'The target needs N = ' + nTarget + '.'; }
    ]);
    checks.l9 = function () {
      var data = deckB.cards().slice(PROG_B.length);
      if (!data.length) { fb.show('no', 'Not yet', ['Program B has no data cards yet. Run program A, then feed its stacker to program B.']); return; }
      var fresh = Fortran.run(deckA.cards()).punched.map(rtrim), res = runAndCompare(deckB.cards(), tgt), fromA = data.join('\n') === fresh.join('\n');
      if (res.same && fromA) {
        solve(9);
        fb.show('ok', 'Correct', ['Program A punched ' + plural(data.length, 'card') + ' for N = ' + data[0].trim() + ', and program B read them back and printed the target total.', next(9)]);
        return;
      }
      var notes = [];
      if (!fromA) notes.push('The cards behind program B are not the ones program A punches from its current data card. Run program A again and feed its stacker to program B.');
      if (res.r.ok && !res.same) {
        var n = parseInt(data[0], 10);
        notes.push('Program B printed ' + rtrim(res.r.printer[0] || '').trim() + ', the total for N = ' + (isNaN(n) ? '?' : n) + '. ' + (n < nTarget ? 'That is too small.' : n > nTarget ? 'That is too large.' : ''));
      }
      fb.show('no', 'Not yet', notes.concat([{ diag: C.diagList(res.r.log) }, res.r.ok ? { printer: res.r.printer } : null]));
    };
    reset();
  };

  /* ---------------- 10: a deck of your own ---------------- */
  BUILD[10] = function () {
    var REF = ['C     COUNT DOWN FROM 5', '      DO 10 I = 1, 5', '      J = 6 - I', '      WRITE (6,20) J', '   10 CONTINUE', '      WRITE (6,30)',
      '   20 FORMAT (1X,I4)', "   30 FORMAT (8H LIFTOFF)", '      STOP', '      END'];
    var tgt = target('l10', REF);
    var fb = new C.Feedback($('l10-fb'));
    function items() { return [{ text: '', fixed: false }]; }
    var deck = new C.Deck($('l10-deck'), { name: 'Your deck', items: items(), add: true, move: true, max: 40 });
    resets.l10 = function () { deck.setItems(items()); fb.clear(); };
    decks.l10 = function () { return deck.cards(); };
    setHints('l10', [
      'Each number is printed right-justified, ending in print position 4, so after the carriage control blank the field is I4. The program needs an END card at the end, and usually a STOP before it.',
      'A loop can count I from 1 to 5 and print 6 - I. A FORMAT with 8H LIFTOFF prints the word: the first of the 8 characters is the blank for carriage control.',
      answerHint('One correct deck:', REF)
    ]);
    checks.l10 = function () {
      var cards = deck.cards();
      while (cards.length && !cards[cards.length - 1].trim()) cards.pop();
      var res = runAndCompare(cards, tgt);
      if (res.same) { solve(10); fb.show('ok', 'Correct', ['Your ' + plural(cards.length, 'card') + ' ran and printed the countdown exactly. That is the whole course.']); return; }
      var notes = [];
      if (!cards.length) notes.push('The deck is empty. Punch the first card, then add more.');
      deck.slots().forEach(function (s) {
        var t = s.text.padEnd(80);
        if (t.trim() && t.charAt(0) !== 'C' && t.charAt(0) !== '*' && t.charAt(5) !== ' ' && t.charAt(5) !== '0' && s.index === 0) notes.push('Card 1 has ' + showCh(t.charAt(5)) + ' in column 6, which makes it a continuation of nothing. Statements start in column 7.');
        if (t.slice(72).trim()) notes.push('Card ' + (s.index + 1) + ' runs past column 72.');
      });
      notYet(fb, notes, res, tgt);
    };
  };

  // each sheet is built the first time its window opens
  Object.keys(BUILD).forEach(function (n) {
    var built = false;
    Desk.onOpen('win-sheet-' + n, function () { if (built) return; built = true; BUILD[n](); updateProgress(); });
  });

  /* ---------------- the punch codes: two charts, built from the engine's table ---------------- */
  Desk.onOpen('win-codes', function (w) {
    if (w._built) return;
    w._built = true;
    function cellFor(rows) { var info = readColumn(new Set(rows)); return info.valid && info.ch !== ' ' ? info.ch : ''; }
    function build(table, extra) {
      var digits = extra.length ? [2, 3, 4, 5, 6, 7] : [0, 1, 2, 3, 4, 5, 6, 7, 8, 9];
      var thead = el('thead'), tr = el('tr');
      tr.appendChild(el('th', '', 'Zone'));
      digits.forEach(function (d) { tr.appendChild(el('th', '', extra.concat([d]).join('-'))); });
      thead.appendChild(tr); table.appendChild(thead);
      var tb = el('tbody');
      [null, 12, 11, 0].forEach(function (z) {
        var r = el('tr'), th = el('th', '', z === null ? 'none' : String(z));
        th.scope = 'row'; r.appendChild(th);
        digits.forEach(function (d) {
          if (z === d) { r.appendChild(el('td', 'na', '')); return; }
          var rows = (z === null ? [] : [z]).concat(extra, [d]), ch = cellFor(rows), td = el('td', ch ? '' : 'na', ch);
          td.setAttribute('aria-label', ch ? rowsText(rows) + ' is ' + ch : rowsText(rows) + ' is not a character');
          r.appendChild(td);
        });
        tb.appendChild(r);
      });
      table.appendChild(tb);
    }
    build($('chart-a'), []);
    build($('chart-b'), [8]);
    $('chart-alone').textContent = 'Alone, 12 is ' + cellFor([12]) + ', 11 is ' + cellFor([11]) + ', and 0 is the digit 0. A column with no holes is a blank.';
  });

  // Escape while typing or punching leaves the field for the sheet's heading; a second
  // Escape closes the sheet, as the Editor does with its text
  $$('.win.sheet .sheet-t').forEach(function (h) { h.tabIndex = -1; });
  Desk.onEscape(function (e) {
    var w = e.target.closest && e.target.closest('.win.sheet');
    if (!w || !e.target.matches('input, select, .cell')) return false;
    w.querySelector('.sheet-t').focus();
    return true;
  });

  updateProgress();
})();
