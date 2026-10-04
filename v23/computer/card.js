/* Cards for the course: the punch codes, an interactive card, a deck of cards with a
   keypunch, and feedback that compares printer output. Every code comes from the engine
   (Fortran.punches, decodeCard, encodeCard), so a card means exactly what the reader reads.
   Needs Desk (wm.js) and Workspace (workspace.js, for the printer). */

var Cards = (function () {
  'use strict';
  var doc = document, el = Desk.el, plural = Desk.plural;
  var ROWS = [12, 11, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9];

  function rtrim(s) { return String(s).replace(/ +$/, ''); }
  function pick(list, not) { var c; do { c = list[Math.floor(Math.random() * list.length)]; } while (list.length > 1 && c === not); return c; }

  /* ---------------- punch codes ---------------- */
  function orderRows(rows) { return ROWS.filter(function (r) { return rows.indexOf(r) !== -1; }); }
  // written in the 029's notation: zone first, then 8, then the digit (0-8-3)
  function rank(r) { return r === 12 ? 0 : r === 11 ? 1 : r === 0 ? 2 : r === 8 ? 3 : 4 + r; }
  function rowsText(rows) {
    rows = orderRows(rows).sort(function (a, b) { return rank(a) - rank(b); });
    return rows.length ? rows.join('-') : 'no holes';
  }
  function holes(rows) { return rows.length === 1 ? 'a hole in row ' + rows[0] : 'holes in rows ' + rowsText(rows); }
  // one column: { rows, ch, valid }; a pattern that is not in the 029's table is not valid
  function readColumn(mask) {
    var rows = orderRows(Array.from(mask));
    if (!rows.length) return { rows: rows, ch: ' ', valid: true };
    var ch = Fortran.decodeCard([new Set(rows)]).charAt(0);
    var ok = rowsText(Fortran.punches(ch)) === rowsText(rows);
    return { rows: rows, ch: ok ? ch : null, valid: ok };
  }
  function punchable(ch) { return ch === ' ' || Fortran.punches(ch).length > 0; }
  function sanitize(value) {
    var out = '', up = String(value).toUpperCase();
    for (var i = 0; i < up.length && out.length < 80; i++) if (punchable(up.charAt(i))) out += up.charAt(i);
    return out;
  }
  function showCh(ch) { return ch === undefined || ch === null ? 'nothing' : ch === ' ' ? 'a blank' : '“' + ch + '”'; }
  function rulerText(cols) {
    var tens = '', ones = '';
    for (var c = 1; c <= cols; c++) { tens += c % 10 === 0 ? String(c / 10 % 10) : ' '; ones += String(c % 10); }
    return tens + '\n' + ones;
  }

  /* ---------------- the interactive card ---------------- */
  // A role="grid" of 12 rows by N columns with a roving tabindex. Each cell is a punch
  // position; the column headers carry the printing along the top edge. One column is
  // 10px wide, the advance of the monospaced face, so the printing sits over its column.
  var count = 0;
  function Grid(host, o) {
    o = o || {};
    var self = this, cols = this.cols = o.cols || 80;
    this.readOnly = !!o.readOnly; this.typing = !!o.typing; this.printed = o.printed !== false;
    this.onChange = o.onChange || function () {};
    this.masks = []; for (var c = 0; c < cols; c++) this.masks.push(new Set());
    this.r = 0; this.c = 0; this.colEls = []; this.cells = [];
    var id = 'cg' + (++count);

    var box = el('div', 'cardbox' + (cols <= 12 ? ' big' : ''));
    var card = el('div', 'card');
    card.style.setProperty('--cols', cols);
    var grid = this.grid = el('div', 'cardgrid');
    grid.setAttribute('role', 'grid');
    grid.setAttribute('aria-label', o.label || 'Card');
    grid.setAttribute('aria-rowcount', '13');
    grid.setAttribute('aria-colcount', String(cols + 1));
    grid.setAttribute('aria-describedby', id + '-help');
    if (this.readOnly) grid.setAttribute('aria-readonly', 'true');
    var frag = doc.createDocumentFragment();

    var head = el('div', 'crow head'), corner = el('div', 'corner');
    head.setAttribute('role', 'row'); corner.setAttribute('role', 'columnheader');
    corner.appendChild(el('span', 'sr', 'Row'));
    head.appendChild(corner);
    for (c = 0; c < cols; c++) { var h = el('div', 'ch'); h.setAttribute('role', 'columnheader'); head.appendChild(h); this.colEls.push([h]); }
    frag.appendChild(head);
    ROWS.forEach(function (row, ri) {
      var re = el('div', 'crow'), rh = el('div', 'rh', String(row)), line = [];
      re.setAttribute('role', 'row'); rh.setAttribute('role', 'rowheader');
      re.appendChild(rh);
      for (var cc = 0; cc < cols; cc++) {
        var cell = el('div', 'cell');
        cell.setAttribute('role', 'gridcell'); cell.tabIndex = -1;
        cell.dataset.r = ri; cell.dataset.c = cc;
        if (row >= 0 && row <= 9) cell.dataset.d = String(row);   // only the digit rows are printed
        re.appendChild(cell); line.push(cell); self.colEls[cc].push(cell);
      }
      self.cells.push(line);
      frag.appendChild(re);
    });
    grid.appendChild(frag);
    card.appendChild(grid);

    // column numbers and the field band, drawn under the card, never behind its text
    var ruler = el('div', 'cruler');
    ruler.setAttribute('aria-hidden', 'true');
    ruler.appendChild(el('span', 'corner'));
    for (c = 0; c < cols; c++) { var n = c + 1; ruler.appendChild(el('span', '', (cols <= 12 || n === 1 || n % 10 === 0) ? String(n) : '')); }
    card.appendChild(ruler);
    if (cols === 80) {
      var band = el('div', 'fieldband');
      band.setAttribute('aria-hidden', 'true');
      band.innerHTML = '<span class="corner"></span><i class="fb-l">label</i><i class="fb-c"></i><i class="fb-s">statement</i><i class="fb-q">sequence</i>';
      card.appendChild(band);
    }
    box.appendChild(card);
    host.appendChild(box);
    var help = el('p', 'sr', this.readOnly ? 'Use the arrow keys to read the card.' :
      this.typing ? 'Arrow keys move. Space or Enter punches or clears a hole. Typing a character punches its code and moves to the next column.' :
        'Arrow keys move. Space or Enter punches or clears a hole.');
    help.id = id + '-help';
    host.appendChild(help);
    this.status = el('p', 'cardstatus'); this.status.setAttribute('role', 'status');
    host.appendChild(this.status);

    grid.addEventListener('click', function (e) {
      var cell = e.target.closest('.cell');
      if (!cell) return;
      self.moveTo(+cell.dataset.r, +cell.dataset.c, true);
      if (!self.readOnly) self.toggle(self.r, self.c);
    });
    grid.addEventListener('keydown', function (e) { self.key(e); });
    this.refreshAll();
    this.moveTo(0, 0, false);
  }
  Grid.prototype.refreshCol = function (c) {
    var info = readColumn(this.masks[c]), els = this.colEls[c], h = els[0], m = this.masks[c];
    h.classList.toggle('bad', !info.valid);
    if (!this.printed) { h.textContent = ''; h.setAttribute('aria-label', 'Column ' + (c + 1)); }
    else if (!info.valid) { h.textContent = ''; h.setAttribute('aria-label', 'Column ' + (c + 1) + ': not a character'); }
    else { h.textContent = info.ch === ' ' ? '' : info.ch; h.setAttribute('aria-label', 'Column ' + (c + 1) + ': ' + (info.ch === ' ' ? 'blank' : info.ch)); }
    for (var ri = 0; ri < 12; ri++) {
      var on = m.has(ROWS[ri]), cell = els[ri + 1];
      if (cell._on === on) continue;      // only cells that changed are touched
      cell._on = on;
      cell.classList.toggle('p', on);
      cell.setAttribute('aria-label', 'Row ' + ROWS[ri] + ', column ' + (c + 1) + ', ' + (on ? 'punched' : 'not punched'));
    }
  };
  Grid.prototype.refreshAll = function () { for (var c = 0; c < this.cols; c++) this.refreshCol(c); };
  Grid.prototype.moveTo = function (r, c, focus) {
    r = Math.max(0, Math.min(11, r)); c = Math.max(0, Math.min(this.cols - 1, c));
    this.cells[this.r][this.c].tabIndex = -1;
    this.colEls[this.c].forEach(function (e) { e.classList.remove('cur'); });
    this.r = r; this.c = c;
    var cell = this.cells[r][c];
    cell.tabIndex = 0;
    this.colEls[c].forEach(function (e) { e.classList.add('cur'); });
    if (focus) { cell.focus({ preventScroll: true }); cell.scrollIntoView({ block: 'nearest', inline: 'nearest' }); }
  };
  Grid.prototype.announce = function (c, extra) {
    var info = readColumn(this.masks[c]);
    this.status.textContent = (extra ? extra + ' ' : '') + 'Column ' + (c + 1) + ': ' + rowsText(info.rows) + ', ' + (!info.valid ? 'no character' : info.ch === ' ' ? 'blank' : info.ch) + '.';
  };
  Grid.prototype.changed = function (c) { this.refreshCol(c); this.announce(c); this.onChange(this); };
  Grid.prototype.toggle = function (ri, c) { var row = ROWS[ri], m = this.masks[c]; if (m.has(row)) m.delete(row); else m.add(row); this.changed(c); };
  Grid.prototype.setColumn = function (c, rows) { this.masks[c] = new Set(rows); this.changed(c); };
  Grid.prototype.key = function (e) {
    var k = e.key, r = this.r, c = this.c;
    if (e.altKey || e.metaKey) return;
    var moves = { ArrowLeft: [r, c - 1], ArrowRight: [r, c + 1], ArrowUp: [r - 1, c], ArrowDown: [r + 1, c],
      Home: e.ctrlKey ? [0, 0] : [r, 0], End: e.ctrlKey ? [11, this.cols - 1] : [r, this.cols - 1], PageUp: [0, c], PageDown: [11, c] };
    if (moves[k]) { e.preventDefault(); this.moveTo(moves[k][0], moves[k][1], true); return; }
    if (e.ctrlKey) return;
    if (k === ' ' || k === 'Enter') { e.preventDefault(); if (this.readOnly) this.announce(c, 'This card is read only.'); else this.toggle(r, c); return; }
    if (this.readOnly) return;
    if (k === 'Delete' && this.typing) { e.preventDefault(); this.setColumn(c, []); return; }
    if (k === 'Backspace' && this.typing) { e.preventDefault(); if (c > 0) { this.moveTo(r, c - 1, true); this.setColumn(c - 1, []); } return; }
    if (k.length === 1) {
      e.preventDefault();
      if (!this.typing) { this.status.textContent = 'The keypunch is off on this sheet. Put the holes in with Space or Enter.'; return; }
      var ch = k.toUpperCase();
      if (!punchable(ch)) { this.status.textContent = showCh(ch) + ' is not on the 029 keypunch.'; return; }
      this.setColumn(c, Fortran.punches(ch));
      if (c < this.cols - 1) this.moveTo(r, c + 1, true);
    }
  };
  Grid.prototype.getText = function () { var m = this.masks.slice(); while (m.length < 80) m.push(new Set()); return Fortran.decodeCard(m).slice(0, this.cols); };
  Grid.prototype.setText = function (t) { this.setMasks(Fortran.encodeCard(String(t || '').padEnd(80).slice(0, 80))); };
  Grid.prototype.setMasks = function (masks) {
    this.masks = masks.slice(0, this.cols).map(function (s) { return new Set(s); });
    while (this.masks.length < this.cols) this.masks.push(new Set());
    this.refreshAll();
  };
  Grid.prototype.badColumns = function () { var out = []; for (var c = 0; c < this.cols; c++) if (!readColumn(this.masks[c]).valid) out.push(c + 1); return out; };
  Grid.prototype.setLabel = function (t) { this.grid.setAttribute('aria-label', t); };

  /* ---------------- decks: a list of cards, some of them yours to punch ---------------- */
  // items: [{ text, fixed }]. Selecting one of your cards puts it under the keypunch, where
  // it can be typed as a line or punched hole by hole on the card below.
  function listWrap(host, name, cls) {
    var wrap = el('div', 'decklist-wrap'), rul = el('pre', 'deckruler', rulerText(80)), list = el('ol', 'decklist' + (cls ? ' ' + cls : ''));
    rul.setAttribute('aria-hidden', 'true');
    list.setAttribute('aria-label', name);
    wrap.appendChild(rul); wrap.appendChild(list); host.appendChild(wrap);
    return list;
  }
  function Deck(host, o) {
    var self = this;
    this.o = o = o || {};
    this.items = (o.items || []).map(function (it) { return { text: rtrim(it.text), fixed: !!it.fixed }; });
    this.sel = -1;
    this.list = listWrap(host, o.name || 'Deck');
    if (o.edit !== false) {
      this.tools = el('div', 'deck-tools');
      host.appendChild(this.tools);
      if (o.add) {
        this.addBtn = this.button(o.addLabel || 'Add a card after this one', function () { self.add(); });
        this.delBtn = this.button('Remove this card', function () { self.remove(); });
      }
      if (o.move) {
        this.upBtn = this.button('Move up', function () { self.move(-1); });
        this.downBtn = this.button('Move down', function () { self.move(1); });
      }
      var box = el('div', 'keypunch'), lab = el('label', '', 'Keypunch'), kid = 'kp' + (++count);
      var kwrap = el('div', 'kp-wrap'), kr = el('pre', 'kp-ruler', rulerText(80));
      lab.htmlFor = kid; kr.setAttribute('aria-hidden', 'true');
      var input = this.input = el('input', 'kp-in');
      input.id = kid; input.type = 'text'; input.maxLength = 80; input.spellcheck = false; input.autocomplete = 'off';
      input.setAttribute('autocapitalize', 'characters');
      kwrap.appendChild(kr); kwrap.appendChild(input);
      box.appendChild(lab); box.appendChild(kwrap);
      host.appendChild(box);
      input.addEventListener('input', function () {
        if (self.sel < 0) return;
        var pos = sanitize(input.value.slice(0, input.selectionStart)).length, clean = sanitize(input.value);
        if (clean !== input.value) { input.value = clean; input.setSelectionRange(pos, pos); }
        self.items[self.sel].text = rtrim(clean);
        self.grid.setText(clean);
        self.renderLine(self.sel);
        if (o.onEdit) o.onEdit();
      });
      this.grid = new Grid(host, { typing: true, label: 'Card under the keypunch', onChange: function (g) {
        if (self.sel < 0) return;
        var t = rtrim(g.getText());
        self.items[self.sel].text = t; input.value = t;
        self.renderLine(self.sel);
        if (o.onEdit) o.onEdit();
      } });
    }
    this.render();
    this.select(this.items.findIndex(function (it) { return !it.fixed; }));
  }
  Deck.prototype.button = function (label, fn) { var b = el('button', 'btn', label); b.type = 'button'; b.addEventListener('click', fn); this.tools.appendChild(b); return b; };
  Deck.prototype.render = function () {
    var self = this, frag = doc.createDocumentFragment();
    this.list.innerHTML = '';
    this.items.forEach(function (it, i) {
      var li = el('li', it.fixed ? 'fixed' : 'slot');
      if (it.fixed) { li.appendChild(el('span', 'num', String(i + 1))); li.appendChild(el('code', 'line')); }
      else {
        var b = el('button', 'slot-b'); b.type = 'button';
        b.appendChild(el('span', 'num', String(i + 1))); b.appendChild(el('code', 'line')); b.appendChild(el('span', 'tag', 'your card'));
        b.addEventListener('click', function () { self.select(i, true); });
        li.appendChild(b);
      }
      frag.appendChild(li);
    });
    this.list.appendChild(frag);
    this.items.forEach(function (it, i) { self.renderLine(i); });
    this.mark();
  };
  Deck.prototype.renderLine = function (i) {
    var li = this.list.children[i];
    if (!li) return;
    var t = this.items[i].text;
    li.querySelector('.line').textContent = t.padEnd(80);
    var desc = 'Card ' + (i + 1) + (this.items[i].fixed ? '' : ', your card') + ': ' + (t.trim() === '' ? 'blank' : t.replace(/ +/g, ' ').trim());
    (this.items[i].fixed ? li : li.querySelector('button')).setAttribute('aria-label', desc);
  };
  Deck.prototype.mark = function () {
    var sel = this.sel;
    Array.prototype.forEach.call(this.list.children, function (li, k) {
      li.classList.toggle('sel', k === sel);
      var b = li.querySelector('button'); if (b) b.setAttribute('aria-pressed', String(k === sel));
    });
    var it = this.items[sel], mine = !!it && !it.fixed;
    if (this.delBtn) this.delBtn.disabled = !mine || this.slotCount() <= 1;
    if (this.upBtn) this.upBtn.disabled = !mine || sel <= 0;
    if (this.downBtn) this.downBtn.disabled = !mine || sel >= this.items.length - 1;
    if (this.addBtn) this.addBtn.disabled = this.items.length >= (this.o.max || 40);
  };
  Deck.prototype.select = function (i, focus) {
    this.sel = i;
    if (this.grid) {
      var on = i >= 0 && !this.items[i].fixed, t = on ? this.items[i].text : '';
      this.input.disabled = !on;
      this.grid.setText(t); this.input.value = t;
      this.grid.setLabel(on ? 'Card ' + (i + 1) + ' under the keypunch' : 'Card under the keypunch');
      if (focus && on) this.input.focus();
    }
    this.mark();
  };
  Deck.prototype.slotCount = function () { return this.items.filter(function (it) { return !it.fixed; }).length; };
  Deck.prototype.add = function () {
    var at = this.sel >= 0 ? this.sel + 1 : this.items.length;
    this.items.splice(at, 0, { text: '', fixed: false });
    this.render(); this.select(at, true);
    if (this.o.onEdit) this.o.onEdit();
  };
  Deck.prototype.remove = function () {
    if (this.sel < 0 || this.items[this.sel].fixed || this.slotCount() <= 1) return;
    this.items.splice(this.sel, 1);
    var next = Math.min(this.sel, this.items.length - 1);
    while (next >= 0 && this.items[next].fixed) next--;
    if (next < 0) next = this.items.findIndex(function (it) { return !it.fixed; });
    this.render(); this.select(next, true);
    if (this.o.onEdit) this.o.onEdit();
  };
  Deck.prototype.move = function (d) {
    var i = this.sel, j = i + d;
    if (i < 0 || j < 0 || j >= this.items.length) return;
    var t = this.items[i]; this.items[i] = this.items[j]; this.items[j] = t;
    this.render(); this.select(j);
    if (this.o.onEdit) this.o.onEdit();
    var b = this.list.children[j].querySelector('button'); if (b) b.focus();
  };
  Deck.prototype.setItems = function (items) {
    this.items = items.map(function (it) { return { text: rtrim(it.text), fixed: !!it.fixed }; });
    this.render();
    this.select(this.items.findIndex(function (it) { return !it.fixed; }));
  };
  Deck.prototype.cards = function () { return this.items.map(function (it) { return it.text; }); };
  Deck.prototype.slots = function () { var out = []; this.items.forEach(function (it, i) { if (!it.fixed) out.push({ index: i, text: it.text }); }); return out; };

  /* ---------------- printer output, compared ---------------- */
  function samePrinter(a, b) {
    if (a.length !== b.length) return false;
    for (var i = 0; i < a.length; i++) if (rtrim(a[i]) !== rtrim(b[i])) return false;
    return true;
  }
  function printerDiff(target, yours) {
    var t = target.map(rtrim), y = yours.map(rtrim);
    if (!y.length) return 'The printer printed nothing at all.';
    if (t[0] === '\f' && y[0] !== '\f') return 'The target starts on a new page, but your output does not. A 1 as the first character of a record sends the printer to a new page.';
    if (y[0] === '\f' && t[0] !== '\f') return 'Your output starts with a new page that the target does not have. The first character of the record was a 1, which the printer takes as carriage control.';
    for (var i = 0; i < Math.max(t.length, y.length); i++) {
      if (t[i] === y[i]) continue;
      if (y[i] === undefined) return 'Your output stops after line ' + i + ', but the target has ' + plural(t.length, 'line') + '.';
      if (t[i] === undefined) return 'Your output has ' + plural(y.length, 'line') + ', more than the ' + t.length + ' of the target.';
      var a = t[i], b = y[i], k = 0;
      while (k < a.length && k < b.length && a.charAt(k) === b.charAt(k)) k++;
      var tail = '';
      if (b.length && a.slice(1) === b) tail = ' Your line is the target with its first character missing: that character was taken as carriage control.';
      else if (a === b.slice(1) || a === b.replace(/^ /, '')) tail = ' Your line has an extra character at the front.';
      return 'Line ' + (i + 1) + ' differs from print position ' + (k + 1) + ' on: the target has ' + showCh(a.charAt(k) || undefined) + ' there, and yours has ' + showCh(b.charAt(k) || undefined) + '.' + tail;
    }
    return '';
  }
  // the engine's diagnostics, worded for the course; sequence-number warnings are folded together
  function diagList(log, opts) {
    opts = opts || {};
    var seqWarn = 0, out = [];
    log.forEach(function (l) {
      if (/warning: columns 73-80 are ignored/.test(l)) { seqWarn++; return; }
      out.push(l.replace(/^card (\d+): /, 'Card $1: '));
    });
    if (seqWarn && !opts.hideSeq) out.push('The reader warned on ' + plural(seqWarn, 'card') + ' that columns 73 to 80 are ignored.' + (opts.seqOk ? ' That is expected: they hold the sequence numbers.' : ''));
    return out;
  }
  // A verdict, with notes, the interpreter's messages and the printer output as evidence.
  function Feedback(box) { this.box = box; }
  Feedback.prototype.clear = function () { this.box.innerHTML = ''; this.box.className = 'feedback'; };
  Feedback.prototype.show = function (kind, head, parts) {
    var box = this.box;
    box.innerHTML = '';
    box.className = 'feedback ' + kind;
    var h = el('p', 'fb-head', head);
    box.appendChild(h);
    (parts || []).forEach(function (p) {
      if (!p) return;
      if (typeof p === 'string') { box.appendChild(el('p', '', p)); return; }
      if (p.node) { box.appendChild(p.node); return; }
      if (p.diag && p.diag.length) {
        box.appendChild(el('p', 'fb-sub', 'The interpreter reported'));
        var ul = el('ul', 'diag');
        p.diag.forEach(function (d) { ul.appendChild(el('li', '', d)); });
        box.appendChild(ul);
      }
      if (p.printer) {
        box.appendChild(el('p', 'fb-sub', p.label || 'Your printer output'));
        var pr = el('div', 'printer small');
        Workspace.renderPrinter(pr, p.printer);
        box.appendChild(pr);
      }
    });
  };

  return {
    ROWS: ROWS, rtrim: rtrim, pick: pick, orderRows: orderRows, rowsText: rowsText, holes: holes, readColumn: readColumn,
    sanitize: sanitize, showCh: showCh, rulerText: rulerText, listWrap: listWrap,
    Grid: Grid, Deck: Deck, Feedback: Feedback, samePrinter: samePrinter, printerDiff: printerDiff, diagList: diagList
  };
})();
