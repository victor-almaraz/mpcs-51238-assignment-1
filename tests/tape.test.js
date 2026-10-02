/* Tests for the pure parts of scripts/tape.js (card parsing and timing). */

function tapeCard(fields) { return fields.map(function (n) { return n == null ? '     ' : ('     ' + n).slice(-5); }).join(''); }

test('tape: an event card reads TIME, NOTE, LEN and LOUD from 5-column fields', function () {
  var r = Tape.parseCards([tapeCard([4, 60, 2, 9])]);
  equal(r.events, [{ time: 4, note: 60, len: 2, loud: 9 }]);
  equal(r.skipped, 0);
  equal(r.length, 6);
});

test('tape: blank or zero LEN and LOUD take their defaults', function () {
  equal(Tape.parseCards([tapeCard([0, 62])]).events, [{ time: 0, note: 62, len: 1, loud: 7 }]);
  equal(Tape.parseCards([tapeCard([0, 62, 0, 0])]).events, [{ time: 0, note: 62, len: 1, loud: 7 }]);
  equal(Tape.parseCards([tapeCard([0, 62, 1, 12])]).events[0].loud, 9);
});

test('tape: bare numbers are onsets by default', function () {
  var r = Tape.parseCards(['    2', '    3', '    7'], { note: 64 });
  equal(r.events.map(function (e) { return [e.time, e.note]; }), [[2, 64], [3, 64], [7, 64]]);
});

test('tape: parseCards counts the bare cards, and the mode does not touch event cards', function () {
  var cards = ['    2', tapeCard([4, 60, 2, 9]), '    7'];
  equal(Tape.parseCards(cards).bare, 2);
  var events = [tapeCard([0, 62]), tapeCard([3, 67, 2])];
  equal(Tape.parseCards(events).bare, 0);
  equal(Tape.parseCards(events, { bare: 'pitch' }).events, Tape.parseCards(events).events);
});

test('tape: in pitch mode bare numbers are notes above the base, one per pulse', function () {
  var r = Tape.parseCards(['    2', '    3', '    7'], { bare: 'pitch', base: 48 });
  equal(r.events.map(function (e) { return [e.time, e.note]; }), [[0, 50], [1, 51], [2, 55]]);
});

test('tape: the stacker of the sieve deck plays as a rhythm', function () {
  var run = Fortran.run(Fortran.samples[4].cards);
  var r = Tape.parseCards(run.punched);
  equal(r.events.map(function (e) { return e.time; }), [2, 3, 7, 8, 12, 13, 17, 18]);
  equal(r.skipped, 0);
});

test('tape: cards with text, extra columns, or no TIME are skipped', function () {
  var r = Tape.parseCards([
    ' FORTY',                                   // a word punched by a deck
    '0129405536344444571517039767496010557647', // a row of digits
    tapeCard([null, 60]),                           // NOTE without TIME
    '',                                         // a blank card
    tapeCard([1, 200])                              // NOTE out of range
  ]);
  equal(r.events, []);
  equal(r.skipped, 5);
});

test('tape: events are sorted by time and keep card order at equal times', function () {
  var r = Tape.parseCards([tapeCard([5, 60]), tapeCard([1, 64]), tapeCard([5, 67])]);
  equal(r.events.map(function (e) { return e.note; }), [64, 60, 67]);
});

test('tape: midiToHz puts A above middle C at 440', function () {
  equal(Tape.midiToHz(69), 440);
  equal(Math.round(Tape.midiToHz(60) * 100) / 100, 261.63);
});

test('tape: a pulse is a quarter beat, and double speed halves time and doubles pitch', function () {
  equal(Tape.pulseSeconds({ bpm: 120 }), 0.125);
  var ev = Tape.parseCards([tapeCard([8, 57, 4])]).events;
  equal(Tape.schedule(ev, { bpm: 120 }), [{ t: 1, dur: 0.5, hz: 220, gain: 7 / 9 }]);
  equal(Tape.schedule(ev, { bpm: 120, speed: 2 }), [{ t: 0.5, dur: 0.25, hz: 440, gain: 7 / 9 }]);
});
