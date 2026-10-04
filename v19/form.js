/* The coding form: the card tray beside it, the deck on it, and the card in hand under it.
   Form.deck() is the deck as the reader takes it; Form.set(cards, name) replaces it. */

var Form = (function () {
  'use strict';
  var doc = document, $ = Desk.$, $$ = Desk.$$, plural = Desk.plural;
  var ROWS = [12, 11, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9];
  var SVG_NS = 'http://www.w3.org/2000/svg';
  var CARD_INK = '#2b2118', CARD_HOLE = '#241a12', CARD_PRINT = '#8a7558';
  var cardsEl = $('cards'), selected = 0;

  /* ---------------- the ruler over the form ---------------- */
  (function () {
    var tens = '', ones = '';
    for (var c = 1; c <= 80; c++) { tens += c % 10 === 0 ? String(c / 10) : ' '; ones += String(c % 10); }
    $('ruler').textContent = 'LABEL+' + 'STATEMENT'.padEnd(66) + 'SEQUENCE\n' + tens + '\n' + ones;
  })();

  /* ---------------- the card in hand ---------------- */
  function svgEl(name, attrs, text) {
    var e = doc.createElementNS(SVG_NS, name);
    for (var k in attrs) e.setAttribute(k, attrs[k]);
    if (text !== undefined) e.textContent = text;
    return e;
  }
  // one card, 12 rows by 80 columns, with its printing, its holes and the faint row digits
  function drawCard(text) {
    var t80 = text.padEnd(80).slice(0, 80), masks = Fortran.encodeCard(t80);
    var left = 24, colW = 10, top = 22, rowH = 13, width = left + 80 * colW + 8, height = top + 12 * rowH + 6;
    var svg = svgEl('svg', { viewBox: '0 0 ' + width + ' ' + height, role: 'img', 'aria-label': 'Punched card: ' + (t80.trim() || 'blank') });
    var frag = doc.createDocumentFragment();
    frag.appendChild(svgEl('polygon', { points: '14.5,0.5 ' + (width - 0.5) + ',0.5 ' + (width - 0.5) + ',' + (height - 0.5) + ' 0.5,' + (height - 0.5) + ' 0.5,14.5', style: 'fill: var(--card, #f1e2bb); stroke: var(--card-edge, #8f7550)' }));
    ROWS.forEach(function (row, r) { frag.appendChild(svgEl('text', { x: left - 4, y: top + r * rowH + 9, 'text-anchor': 'end', 'font-size': 9, 'font-family': '"IBM Plex Mono", monospace', fill: CARD_INK }, String(row))); });
    for (var c = 0; c < 80; c++) {
      var x = left + c * colW, ch = t80.charAt(c);
      if (ch !== ' ') frag.appendChild(svgEl('text', { x: x + colW / 2, y: 15, 'text-anchor': 'middle', 'font-size': 11, 'font-family': '"IBM Plex Mono", monospace', fill: CARD_INK }, ch));
      for (var r = 0; r < 12; r++) {
        var y = top + r * rowH, row = ROWS[r];
        if (masks[c].has(row)) frag.appendChild(svgEl('rect', { x: x + 2, y: y + 1, width: 6, height: 10, fill: CARD_HOLE }));
        else if (row >= 0 && row <= 9) frag.appendChild(svgEl('text', { x: x + colW / 2, y: y + 9, 'text-anchor': 'middle', 'font-size': 8, 'font-family': '"IBM Plex Mono", monospace', fill: CARD_PRINT }, String(row)));
      }
    }
    svg.appendChild(frag);
    return svg;
  }
  // redrawn at most once a frame, and only while the card in hand is open
  var pending = false;
  function showCard() {
    if (pending) return;
    pending = true;
    requestAnimationFrame(function () {
      pending = false;
      var rows = cardsEl.children;
      if (!rows.length) return;
      if (selected >= rows.length) selected = rows.length - 1;
      $('card-caption').textContent = 'Card ' + (selected + 1) + ' of ' + rows.length + '.';
      $('prev-card').disabled = selected === 0;
      $('next-card').disabled = selected === rows.length - 1;
      if (!$('in-hand').open) return;
      var holder = $('card-svg');
      holder.textContent = '';
      holder.appendChild(drawCard(rows[selected].querySelector('input').value));
    });
  }
  // on a short screen the card in hand starts folded away, so the form keeps its rows
  if (window.innerHeight < 1000) $('in-hand').open = false;
  $('in-hand').addEventListener('toggle', showCard);
  $('prev-card').addEventListener('click', function () { if (selected > 0) select(selected - 1); });
  $('next-card').addEventListener('click', function () { if (selected < cardsEl.children.length - 1) select(selected + 1); });

  /* ---------------- the deck on the form, one card a line ---------------- */
  function sanitize(value) {
    var out = '', up = value.toUpperCase();
    for (var i = 0; i < up.length && out.length < 80; i++) { var ch = up.charAt(i); if (ch === ' ' || Fortran.punches(ch).length > 0) out += ch; }
    return out;
  }
  function rowsList() { return Array.prototype.slice.call(cardsEl.children); }
  function rowIndex(row) { return rowsList().indexOf(row); }
  function renumber() {
    rowsList().forEach(function (row, i) {
      row.firstChild.textContent = String(i + 1);
      row.lastChild.setAttribute('aria-label', 'Card ' + (i + 1));
      row.classList.toggle('selected', i === selected);
    });
  }
  function select(i) { selected = i; renumber(); showCard(); }
  function focusRow(i, caret) {
    var rows = rowsList();
    if (i < 0 || i >= rows.length) return;
    var input = rows[i].lastChild, pos = caret === undefined ? input.value.length : Math.min(caret, input.value.length);
    input.focus();
    input.setSelectionRange(pos, pos);
  }
  // one listener of each kind on the list, not on every card
  cardsEl.addEventListener('focusin', function (e) { var row = e.target.closest('.row'); if (row) select(rowIndex(row)); });
  cardsEl.addEventListener('input', function (e) {
    var input = e.target, row = input.closest('.row');
    var before = input.value.slice(0, input.selectionStart), clean = sanitize(input.value);
    if (clean !== input.value) { var pos = sanitize(before).length; input.value = clean; input.setSelectionRange(pos, pos); }
    if (rowIndex(row) === selected) showCard();
  });
  cardsEl.addEventListener('keydown', function (e) {
    var input = e.target, row = input.closest('.row'), i = rowIndex(row);
    if (e.key === 'Enter') { e.preventDefault(); insertRow(i + 1, ''); focusRow(i + 1, 0); }
    else if (e.key === 'Backspace' && input.value === '' && cardsEl.children.length > 1) { e.preventDefault(); removeRow(i); focusRow(Math.max(0, i - 1)); }
    else if (e.key === 'ArrowUp' && i > 0) { e.preventDefault(); focusRow(i - 1, input.selectionStart); }
    else if (e.key === 'ArrowDown' && i < cardsEl.children.length - 1) { e.preventDefault(); focusRow(i + 1, input.selectionStart); }
  });
  // pasting several lines makes a card of each
  cardsEl.addEventListener('paste', function (e) {
    var data = e.clipboardData && e.clipboardData.getData('text');
    if (!data || !/[\r\n]/.test(data)) return;
    e.preventDefault();
    var input = e.target, i = rowIndex(input.closest('.row'));
    var lines = data.replace(/\r\n?/g, '\n').replace(/\n$/, '').split('\n');
    var start = input.selectionStart, end = input.selectionEnd;
    input.value = sanitize(input.value.slice(0, start) + lines[0] + input.value.slice(end));
    for (var k = 1; k < lines.length; k++) insertRow(i + k, lines[k]);
    focusRow(i + lines.length - 1);
  });
  function makeRow(text) {
    var row = doc.createElement('div'), num = doc.createElement('span'), input = doc.createElement('input');
    row.className = 'row'; num.className = 'num';
    input.type = 'text'; input.className = 'card'; input.maxLength = 80;
    input.spellcheck = false; input.autocomplete = 'off'; input.setAttribute('autocapitalize', 'characters');
    input.value = sanitize(text);
    row.appendChild(num); row.appendChild(input);
    return row;
  }
  function insertRow(i, text) {
    var row = makeRow(text), rows = cardsEl.children;
    if (i >= rows.length) cardsEl.appendChild(row); else cardsEl.insertBefore(row, rows[i]);
    if (i <= selected && rows.length > 1) selected++;
    renumber(); showCard();
  }
  function removeRow(i) {
    cardsEl.removeChild(cardsEl.children[i]);
    if (selected > i || selected >= cardsEl.children.length) selected = Math.max(0, selected - 1);
    renumber(); showCard();
  }
  // the deck as the reader takes it: blank cards at the end are not sent
  function deck() {
    var d = rowsList().map(function (row) { return row.lastChild.value; });
    while (d.length && d[d.length - 1].trim() === '') d.pop();
    return d;
  }
  function set(cards, name) {
    var frag = doc.createDocumentFragment();
    (cards.length ? cards : ['']).forEach(function (t) { frag.appendChild(makeRow(t)); });
    cardsEl.textContent = '';
    cardsEl.appendChild(frag);
    selected = 0; renumber(); showCard();
    $('deck-name').textContent = name || ' ';
    markTray(null);
  }

  /* ---------------- the card tray: every deck, in three sections ---------------- */
  var trayButtons = {};
  Desk.decks.forEach(function (d) {
    var li = doc.createElement('li'), b = doc.createElement('button'), label = doc.createElement('span'), count = doc.createElement('span');
    b.type = 'button'; b.className = 'deck ' + d.section;
    label.className = 'deck-label'; label.textContent = d.name;
    count.className = 'deck-count'; count.textContent = plural(d.cards.length, 'card');
    b.appendChild(label); b.appendChild(doc.createTextNode(' ')); b.appendChild(count);
    b.addEventListener('click', function () { take(d.id); });
    li.appendChild(b);
    $('deck-tray-' + d.section).appendChild(li);
    trayButtons[d.id] = b;
  });
  function markTray(id) { Object.keys(trayButtons).forEach(function (k) { trayButtons[k].classList.toggle('out-of-tray', k === id); }); }
  function take(id) {
    var d = Desk.deck(id);
    set(d.cards, d.name);
    markTray(id);
    $('editor-status').textContent = 'The deck “' + d.name + '” is on the coding form.';
  }
  // from anywhere (the magazine): put the deck on the form and bring the form to the front
  Desk.putOnForm = function (id) { if (!Desk.deck(id)) return; take(id); Desk.go('form'); };

  $('add-card').addEventListener('click', function () { insertRow(selected + 1, ''); focusRow(selected + 1, 0); });
  $('delete-card').addEventListener('click', function () {
    if (cardsEl.children.length > 1) removeRow(selected);
    else { rowsList()[0].lastChild.value = ''; showCard(); }
  });
  $('clear-deck').addEventListener('click', function () { set([]); });

  take(Desk.decks[0].id);
  $('editor-status').textContent = '';
  return { deck: deck, set: set, name: function () { return $('deck-name').textContent.trim(); }, status: function (t) { $('editor-status').textContent = t; } };
})();
