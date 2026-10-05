/* The card reader and the line printer, under the desk. A deck that is run goes through them
   before its printout reaches the out tray: the reader takes the cards one by one from its
   hopper (the deck there going down, each card's punching shown at the read station as it
   passes), then the printer prints the job's output a line at a time on its fan-fold paper.
   It is quick (the whole deck in at most three seconds, the printout in at most four) but
   it is seen; Skip ends it at once, and with reduced motion it is over as it starts. Then the
   printout is carried to the out tray. Each card and each line is told to the room's sounds
   (room:card, room:line). Reader.run(deck, result, done). Needs Desk (desk.js). */

var Reader = (function () {
  'use strict';
  var doc = document, $ = Desk.$, plural = Desk.plural;
  var REDUCED = window.matchMedia('(prefers-reduced-motion: reduce)');
  var scene = doc.querySelector('.overview');
  var hopper = $('reader-hopper'), lamp = $('reader-lamp'), card = $('read-card'), count = $('read-count');
  var paper = $('reader-print'), status = $('reader-status'), skip = $('reader-skip'), take = $('reader-out');
  var job = null, toTray = null;      // the job going through, and where its printout goes

  function tell(what) { if (scene) scene.dispatchEvent(new CustomEvent('room:' + what)); }
  function show(fraction) { hopper.style.setProperty('--left', String(fraction)); }

  // the printout as the printer leaves it: pages of lines, a rule at each form feed
  function printTo(lines, n) {
    paper.textContent = '';
    var pre = null;
    for (var i = 0; i < n; i++) {
      var line = lines[i];
      if (line === '\f') {
        pre = null;
        if (i === 0) continue;
        var div = doc.createElement('div'); div.className = 'pagebreak'; div.textContent = 'new page';
        paper.appendChild(div);
        continue;
      }
      if (!pre) { pre = doc.createElement('pre'); paper.appendChild(pre); }
      pre.textContent += (pre.textContent ? '\n' : '') + line;
    }
    paper.scrollTop = paper.scrollHeight;
  }

  function finish() {
    if (!job) return;
    clearTimeout(job.timer);
    var j = job; job = null;
    show(0);
    lamp.classList.remove('on');
    var last = j.deck[j.deck.length - 1] || '';
    card.querySelector('code').textContent = last.padEnd(80).slice(0, 80);
    count.textContent = 'Read ' + plural(j.deck.length, 'card') + '.';
    if (j.lines.length) printTo(j.lines, j.lines.length);
    else paper.innerHTML = '<p class="placeholder">The program printed nothing.</p>';
    status.textContent = 'The job ' + (j.result.ok ? 'ran without errors' : 'stopped with errors') + '. The printout is ready for the out tray.';
    skip.disabled = true; take.disabled = false;
    take.focus({ preventScroll: true });
  }

  function run(deck, result, done) {
    if (job) { clearTimeout(job.timer); job = null; }
    job = { deck: deck, result: result, lines: result.printer || [], timer: null };
    toTray = done;
    take.disabled = true; skip.disabled = false;
    paper.textContent = '';
    status.textContent = 'Reading ' + plural(deck.length, 'card') + '.';
    Desk.go('reader', status);
    if (REDUCED.matches || !deck.length) { finish(); return; }
    lamp.classList.add('on');
    var per = Math.min(60, 3200 / deck.length), i = 0, j = job;
    function readNext() {
      if (job !== j) return;
      if (i < deck.length) {
        card.querySelector('code').textContent = deck[i].padEnd(80).slice(0, 80);
        count.textContent = 'Card ' + (i + 1) + ' of ' + deck.length + '.';
        show(1 - (i + 1) / deck.length);
        tell('card');
        i++;
        j.timer = setTimeout(readNext, per);
        return;
      }
      lamp.classList.remove('on');
      status.textContent = 'Printing.';
      var lines = j.lines, n = 0, step = Math.min(50, 4000 / Math.max(1, lines.length));
      (function printNext() {
        if (job !== j) return;
        if (n >= lines.length) { finish(); return; }
        n++;
        printTo(lines, n);
        if (lines[n - 1] !== '\f') tell('line');
        j.timer = setTimeout(printNext, step);
      })();
    }
    readNext();
  }

  skip.addEventListener('click', finish);
  take.addEventListener('click', function () { if (toTray) toTray(); });
  show(0);
  return { run: run };
})();
