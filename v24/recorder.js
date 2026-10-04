/* The reel-to-reel recorder, on the shared Tape module. Its tape is threaded from the
   output stacker; a new job empties the stacker, so the old tape comes off the reels. */

(function () {
  'use strict';
  var $ = Desk.$, plural = Desk.plural;
  var REDUCED = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var HUB = 26, FULL = 90;          // radii of the empty hub and a full reel, in SVG units
  var recorder = $('recorder'), keys = ['tape-stop', 'tape-play', 'tape-pause'];
  var threaded = false, lastPos = 0, angleL = 0, angleR = 0;
  var el = {};
  ['pack-l', 'pack-r', 'tape-l', 'tape-r', 'tape-mid', 'spokes-l', 'spokes-r', 'cw0', 'cw1', 'cw2', 'cw3', 'counter-of', 'tape-counter-text', 'tape-play', 'tape-pause']
    .forEach(function (id) { el[id] = $(id); });

  function clock(s) { s = Math.max(0, Math.floor(s + 1e-6)); return Math.floor(s / 60) + ':' + String(s % 60).padStart(2, '0'); }
  function spoken(s) { return s < 60 ? (Math.round(s * 10) / 10) + ' second' + (s === 1 ? '' : 's') : clock(s); }

  function draw(st) {
    var frac = threaded && st.duration ? Math.max(0, Math.min(1, st.position / st.duration)) : 0;
    // the supply reel empties as the take-up reel fills; the tape's area is conserved
    var area = FULL * FULL - HUB * HUB;
    var rL = threaded ? Math.sqrt(HUB * HUB + area * (1 - frac)) : HUB, rR = threaded ? Math.sqrt(HUB * HUB + area * frac) : HUB;
    el['pack-l'].setAttribute('r', rL.toFixed(1));
    el['pack-r'].setAttribute('r', rR.toFixed(1));
    el['tape-l'].setAttribute('y1', (112 + rL).toFixed(1));
    el['tape-r'].setAttribute('y2', (112 + rR).toFixed(1));
    ['tape-l', 'tape-r', 'tape-mid'].forEach(function (id) { el[id].style.display = threaded ? '' : 'none'; });
    // a constant tape speed turns the smaller pack faster; nothing turns off screen
    var pos = Math.max(0, st.position), d = pos - lastPos;
    lastPos = pos;
    if (!REDUCED && d > 0 && d < 1 && Desk.current() === 'recorder') {
      var v = 150 * st.speed;
      angleL += d * v / rL * 180 / Math.PI;
      angleR += d * v / rR * 180 / Math.PI;
      el['spokes-l'].setAttribute('transform', 'rotate(' + (angleL % 360).toFixed(2) + ')');
      el['spokes-r'].setAttribute('transform', 'rotate(' + (angleR % 360).toFixed(2) + ')');
    }
    var secs = Math.floor(pos + 1e-6), mm = String(Math.min(99, Math.floor(secs / 60))).padStart(2, '0'), ss = String(secs % 60).padStart(2, '0');
    el.cw0.textContent = mm.charAt(0); el.cw1.textContent = mm.charAt(1); el.cw2.textContent = ss.charAt(0); el.cw3.textContent = ss.charAt(1);
    el['counter-of'].textContent = 'of ' + clock(st.duration);
    el['tape-counter-text'].textContent = clock(pos) + ' of ' + clock(st.duration);
    el['tape-play'].setAttribute('aria-pressed', String(st.playing));
    el['tape-pause'].setAttribute('aria-pressed', String(threaded && !st.playing && pos > 0 && pos < st.duration));
    recorder.setAttribute('data-state', !threaded ? 'empty' : st.playing ? 'playing' : 'stopped');
  }
  var player = Tape.createPlayer({ bpm: 120, speed: 1, onTick: draw });

  function bareMode() { return document.querySelector('input[name="bare"]:checked').value; }
  function setKeys(on) { keys.forEach(function (id) { $(id).disabled = !on; }); }
  function thread() {
    var stack = Out.stack(), parsed = Tape.parseCards(stack, { bare: bareMode() }), n = parsed.events.length;
    threaded = n > 0;
    lastPos = 0;
    player.load(parsed.events);
    setKeys(threaded);
    // the Rhythm/Scale switch only reads bare numbers; tapes of full tape cards ignore it
    $('bare-switch').disabled = threaded && parsed.bare === 0;
    var skipped = plural(parsed.skipped, 'card') + (parsed.skipped === 1 ? ' was' : ' were') + ' skipped';
    $('tape-status').textContent = threaded
      ? 'Threaded ' + plural(n, 'note') + ' from the stacker, and ' + skipped + '. The tape runs ' + spoken(player.state().duration) + '.' +
        (parsed.bare === 0 ? ' These cards set their own times and notes, so the Rhythm and Scale switch does not apply.' : '')
      : 'Nothing could be threaded: none of the ' + plural(stack.length, 'card') + ' in the stacker is a tape card, so ' + skipped + '.';
  }
  Out.onNewStack(function (stack) {
    threaded = false;
    player.load([]);
    setKeys(false);
    $('bare-switch').disabled = false;
    $('tape-thread').disabled = !stack.length;
    $('tape-status').textContent = stack.length
      ? 'The stacker holds ' + plural(stack.length, 'new card') + '. Thread the tape to play them.'
      : 'The program punched no cards, so there is nothing to thread.';
  });

  $('tape-thread').addEventListener('click', thread);
  // from the stacker: carry the cards to the recorder and thread them
  $('stack-tape').addEventListener('click', function () { Desk.go('recorder'); thread(); });
  Array.prototype.forEach.call(document.querySelectorAll('input[name="bare"]'), function (r) { r.addEventListener('change', function () { if (threaded) thread(); }); });
  $('tape-play').addEventListener('click', function () { if (threaded) player.play(); });
  $('tape-pause').addEventListener('click', function () { player.pause(); });
  $('tape-stop').addEventListener('click', function () { player.stop(); lastPos = 0; });
  $('tape-tempo').addEventListener('input', function () {
    var bpm = Number(this.value);
    $('tempo-out').textContent = bpm + ' beats a minute';
    player.setTempo(bpm);
  });
  Array.prototype.forEach.call(document.querySelectorAll('input[name="speed"]'), function (r) { r.addEventListener('change', function () { player.setSpeed(Number(this.value)); }); });
  draw(player.state());
})();
