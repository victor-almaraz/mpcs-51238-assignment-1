/* The computer on the desk. Its desktop is a page of its own (computer/), in the style it
   was made in, shown in a frame on the computer's screen; the frame is loaded the first
   time the computer is used, and kept, with its windows and files, until the page is
   reloaded. The room and the computer talk by postMessage (computer/link.js):
     to the computer   { type: 'open-text', name, text, kind, note }
     from it           { type: 'ready' }, { type: 'punch', name, text }, { type: 'room' }
   Needs Desk (desk.js), Form (form.js) and Out (out.js). */

var Computer = (function () {
  'use strict';
  var $ = Desk.$, plural = Desk.plural;
  var frame = $('screen'), ready = false, queue = [];

  // index.html by name, so the frame also loads when the page is opened from disk
  function boot() { if (!frame.getAttribute('src')) frame.src = 'computer/index.html'; }

  // The desktop draws in whole screen pixels of two CSS pixels each. Its frame is placed on
  // whole device pixels and sized to whole screen pixels, centred on the glass (which may
  // fall on fractions), so the browser never resamples it.
  var glass = frame.parentNode;
  function snap() {
    var r = glass.getBoundingClientRect(), dpr = window.devicePixelRatio || 1;
    if (!r.width) return;
    var w = Math.floor(r.width / 2) * 2, h = Math.floor(r.height / 2) * 2;
    var x = (Math.round((r.left + (r.width - w) / 2) * dpr) / dpr) - r.left;
    var y = (Math.round((r.top + (r.height - h) / 2) * dpr) / dpr) - r.top;
    frame.style.width = w + 'px'; frame.style.height = h + 'px';
    frame.style.left = x + 'px'; frame.style.top = y + 'px';
  }
  if (window.ResizeObserver) new ResizeObserver(snap).observe(glass);
  window.addEventListener('resize', snap);
  function send(msg) {
    if (ready) frame.contentWindow.postMessage(msg, '*');
    else { queue.push(msg); boot(); }
  }
  // the screen takes the keys once it is lit, so the desktop can be used straight away
  function focusScreen() { if (ready && Desk.current() === 'computer') frame.focus(); }
  Desk.onShow('computer', function () { boot(); snap(); setTimeout(focusScreen, 0); });

  window.addEventListener('message', function (e) {
    var d = e.data;
    if (e.source !== frame.contentWindow || !d) return;
    if (d.type === 'ready') {
      ready = true;
      $('screen-off').hidden = true;
      queue.splice(0).forEach(send);
      focusScreen();
    } else if (d.type === 'room') {
      Desk.go('desk');
    } else if (d.type === 'punch') {
      // one card to a line; a line longer than a card is cut at column 80, as a keypunch would
      var lines = String(d.text).replace(/\s+$/, '').split('\n'), long = 0;
      var cards = lines.map(function (l) { if (l.length > 80) long++; return l.slice(0, 80); });
      Desk.go('form', null, function () {
        Form.set(cards, String(d.name || 'From the computer'));
        Form.status('Punched ' + plural(cards.length, 'card') + ' from the computer’s Editor.' +
          (long ? ' ' + plural(long, 'line') + ' ran past column 80 and ' + (long === 1 ? 'was' : 'were') + ' cut there.' : ''));
      });
    }
  });

  // the deck on the form, typed in as a text; the stacker's cards, read in
  function deckText(cards) { return cards.map(function (c) { return c.replace(/ +$/, ''); }).join('\n'); }
  $('form-to-computer').addEventListener('click', function () {
    var name = Form.name() || 'Deck from the card punch';
    send({ type: 'open-text', name: name, text: deckText(Form.deck()), kind: 'FORTRAN source',
           note: 'Typed in from the coding form, one line to a card.' });
    Desk.go('computer');
  });
  $('stack-computer').addEventListener('click', function () {
    var cards = Out.stack();
    send({ type: 'open-text', name: 'Punched cards', text: deckText(cards), kind: 'Text',
           note: 'Read in from the stacker: ' + plural(cards.length, 'card') + ', one line to a card.' });
    Desk.go('computer');
  });

  return { send: send };
})();
