/* Running a deck, and the out tray: the printout, the job ticket, the listing, and the
   punch's stacker. Out.stack() is the cards in the stacker; Out.onNewStack(fn) runs fn after
   each job, when the stacker has been emptied and refilled. */

var Out = (function () {
  'use strict';
  var doc = document, $ = Desk.$, plural = Desk.plural;
  var ROWS = [12, 11, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9];
  var SHOWN = 300, stack = [], listeners = [];

  function renderPrinter(lines) {
    var box = $('printer'), pre = null, text = [];
    box.textContent = '';
    if (!lines.length) { var p = doc.createElement('p'); p.className = 'placeholder'; p.textContent = 'The program did not print anything.'; box.appendChild(p); return; }
    function flush() { if (pre) pre.textContent = text.join('\n'); pre = null; text = []; }
    lines.forEach(function (line, i) {
      if (line === '\f') {
        flush();
        if (i === 0) return;      // the first page's own form feed draws no rule
        var div = doc.createElement('div'); div.className = 'pagebreak'; div.textContent = 'new page';
        box.appendChild(div);
        return;
      }
      if (!pre) { pre = doc.createElement('pre'); box.appendChild(pre); }
      text.push(line);
    });
    flush();
  }
  function renderLog(result) {
    var pre = doc.createElement('pre');
    pre.textContent = result.log.concat([result.ok ? 'Job ended normally.' : 'Job ended with errors.']).join('\n');
    $('log').textContent = '';
    $('log').appendChild(pre);
  }

  /* ---------------- the stacker ---------------- */
  // Each punched card is one small canvas: its stock, clipped corner and holes, drawn at the
  // screen's pixel density. The text it holds is its accessible name.
  var W = 168, H = 76;
  function cardCanvas(text, n) {
    var c = doc.createElement('canvas'), dpr = Math.min(2, window.devicePixelRatio || 1);
    c.width = W * dpr; c.height = H * dpr;
    c.setAttribute('role', 'img');
    c.setAttribute('aria-label', 'Card ' + n + ': ' + (text.trim() || 'blank'));
    var g = c.getContext('2d'), masks = Fortran.encodeCard(text.padEnd(80).slice(0, 80));
    g.scale(dpr, dpr);
    g.fillStyle = '#f1e2bb'; g.strokeStyle = '#8f7550'; g.lineWidth = 1;
    g.beginPath(); g.moveTo(6.5, 0.5); g.lineTo(W - 0.5, 0.5); g.lineTo(W - 0.5, H - 0.5); g.lineTo(0.5, H - 0.5); g.lineTo(0.5, 6.5); g.closePath();
    g.fill(); g.stroke();
    g.fillStyle = '#241a12';
    for (var col = 0; col < 80; col++) for (var r = 0; r < 12; r++) if (masks[col].has(ROWS[r])) g.fillRect(4 + col * 2, 9 + r * 5.5, 1.2, 3.6);
    return c;
  }
  function renderStacker(punched) {
    stack = punched;
    var box = $('stacker'), frag = doc.createDocumentFragment();
    box.textContent = '';
    ['stack-tape', 'stack-replace', 'stack-append', 'stack-copy', 'stack-download', 'stack-computer'].forEach(function (id) { $(id).disabled = !punched.length; });
    $('stack-status').textContent = '';
    $('stack-count').textContent = punched.length
      ? 'The program punched ' + plural(punched.length, 'card') + '.' + (punched.length > SHOWN ? ' The first ' + SHOWN + ' are shown.' : '')
      : 'The program did not punch any cards.';
    punched.slice(0, SHOWN).forEach(function (t, i) { frag.appendChild(cardCanvas(t, i + 1)); });
    box.appendChild(frag);
    listeners.forEach(function (fn) { fn(stack); });
  }

  /* ---------------- running ---------------- */
  $('run-deck').addEventListener('click', function () {
    var deck = Form.deck(), result = Fortran.run(deck);
    renderPrinter(result.printer);
    renderLog(result);
    $('listing').textContent = result.listing.join('\n');
    renderStacker(result.punched);
    $('run-status').textContent = 'The reader took ' + plural(deck.length, 'card') +
      (result.ok ? ', and the job ran without errors.' : ', and the job stopped with errors. See the job log for details.');
    Form.status('');
    // the out tray comes to the front, the fresh printout feeding in
    var out = $('out');
    out.classList.remove('fresh');
    Desk.go('out', $('run-status'));
    void out.offsetWidth;
    out.classList.add('fresh');
  });

  /* ---------------- what can be done with the punched cards ---------------- */
  function cards() { return stack.map(function (c) { return c.replace(/ +$/, ''); }); }
  function text() { return cards().join('\n') + '\n'; }
  $('stack-replace').addEventListener('click', function () {
    Form.set(cards(), 'Cards from the stacker');
    Form.status('The punched cards replaced the deck.');
    Desk.go('form');
  });
  $('stack-append').addEventListener('click', function () {
    var name = Form.name();
    Form.set(Form.deck().concat(cards()), name ? name + ', with punched cards' : 'Cards from the stacker');
    Form.status('The punched cards were added to the end of the deck, as data.');
    Desk.go('form');
  });
  $('stack-copy').addEventListener('click', function () {
    var status = $('stack-status');
    function fallback() {
      var ta = doc.createElement('textarea'); ta.value = text(); doc.body.appendChild(ta); ta.select();
      var done = false; try { done = doc.execCommand('copy'); } catch (e) { done = false; }
      doc.body.removeChild(ta);
      status.textContent = done ? 'The cards were copied to the clipboard.' : 'Copying failed, so please use Download instead.';
    }
    if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(text()).then(function () { status.textContent = 'The cards were copied to the clipboard.'; }, fallback);
    else fallback();
  });
  $('stack-download').addEventListener('click', function () {
    var url = URL.createObjectURL(new Blob([text()], { type: 'text/plain' })), a = doc.createElement('a');
    a.href = url; a.download = 'punched-cards.txt';
    doc.body.appendChild(a); a.click(); doc.body.removeChild(a);
    setTimeout(function () { URL.revokeObjectURL(url); }, 1000);
    $('stack-status').textContent = 'The cards were downloaded as a text file.';
  });

  return { stack: function () { return stack; }, onNewStack: function (fn) { listeners.push(fn); } };
})();
