/* Tests for the sieve generator deck (Fortran.samples[4]). */

var SIEVE = Fortran.samples[4];
var SOURCE_CARDS = SIEVE.cards.slice(0, SIEVE.cards.length - 3);   // the three data cards come last

function pad5(n) { return ('     ' + n).slice(-5); }

// Run the deck on a sieve: mode 1 union, 2 intersection, 3 complement of the union.
function sieveRun(mode, limit, classes) {
  var data = [pad5(mode) + pad5(classes.length) + pad5(limit)];
  classes.forEach(function (c) { data.push(pad5(c[0]) + pad5(c[1])); });
  return Fortran.run(SOURCE_CARDS.concat(data));
}

// Independent reference in plain JavaScript.
function sieveMembers(mode, limit, classes) {
  var out = [];
  for (var n = 0; n < limit; n++) {
    var hits = classes.filter(function (c) { return (((n - c[1]) % c[0]) + c[0]) % c[0] === 0; }).length;
    if ((mode === 1 && hits > 0) || (mode === 2 && hits === classes.length) || (mode === 3 && hits === 0)) out.push(n);
  }
  return out;
}

// The printed table: [{ k, member, interval|null }]
function printedRows(r) {
  var rows = [];
  r.printer.forEach(function (line) {
    var m = /^\s+(\d+)\s+(\d+)(?:\s+(\d+))?$/.exec(line);
    if (m) rows.push({ k: +m[1], member: +m[2], interval: m[3] === undefined ? null : +m[3] });
  });
  return rows;
}

function checkSieve(mode, limit, classes) {
  var r = sieveRun(mode, limit, classes);
  ok(r.ok, r.log.join('\n'));
  var want = sieveMembers(mode, limit, classes);
  var rows = printedRows(r);
  equal(rows.map(function (x) { return x.member; }), want, 'members');
  equal(rows.map(function (x) { return x.k; }), want.map(function (_, i) { return i + 1; }), 'numbering');
  equal(rows.map(function (x) { return x.interval; }).slice(1),
    want.slice(1).map(function (v, i) { return v - want[i]; }), 'intervals');
  equal(r.punched.map(function (c) { return +c.trim(); }), want, 'punched members');
  equal(r.printer[r.printer.length - 1], pad5(want.length) + ' MEMBERS');
  return r;
}

test('the sieve sample is the fifth sample and carries its own data', function () {
  equal(Fortran.samples.length, 5);
  ok(/sieve/i.test(SIEVE.name));
});

test('sample 5: 5@2 | 5@3 over 0..19 gives 2 3 7 8 12 13 17 18', function () {
  var r = Fortran.run(SIEVE.cards);
  ok(r.ok, r.log.join('\n'));
  equal(r.printer.slice(0, 5), [FF,
    'SIEVE  MODE = 1  N =  2  LIMIT =    20',
    '',
    '     K   MEMBER   INTERVAL',
    '     1        2']);
  equal(printedRows(r).map(function (x) { return x.member; }), [2, 3, 7, 8, 12, 13, 17, 18]);
  equal(printedRows(r).map(function (x) { return x.interval; }), [null, 1, 4, 1, 4, 1, 4, 1]);
  equal(r.printer[r.printer.length - 1], '    8 MEMBERS');
  equal(r.punched.map(function (c) { return c.trim(); }), ['2', '3', '7', '8', '12', '13', '17', '18']);
});

test('sieve: union of 3@0 and 4@0', function () { checkSieve(1, 12, [[3, 0], [4, 0]]); });
test('sieve: intersection 3@0 & 4@0 over 24 is 0 and 12', function () {
  var r = checkSieve(2, 24, [[3, 0], [4, 0]]);
  equal(r.punched.map(function (c) { return +c.trim(); }), [0, 12]);
});
test('sieve: complement !3@0 over 7 is 1 2 4 5', function () {
  var r = checkSieve(3, 7, [[3, 0]]);
  equal(r.punched.map(function (c) { return +c.trim(); }), [1, 2, 4, 5]);
});
test('sieve: a negative shift, 3@-1, is the same as 3@2', function () {
  var r = checkSieve(1, 10, [[3, -1]]);
  equal(r.punched.map(function (c) { return +c.trim(); }), [2, 5, 8]);
});
test('sieve: a shift larger than the modulus and larger than the range', function () {
  checkSieve(1, 30, [[7, 100], [4, 9]]);
});
test('sieve: an empty sieve (the intersection of 3@0 and 3@1)', function () {
  var r = checkSieve(2, 50, [[3, 0], [3, 1]]);
  equal(r.punched, []);
  equal(r.printer[r.printer.length - 1], '    0 MEMBERS');
});
test('sieve: a modulus of 1 contains every integer', function () { checkSieve(1, 8, [[1, 0]]); });
test('sieve: ten classes, the largest allowed', function () {
  checkSieve(1, 200, [[2, 1], [3, 0], [5, 4], [7, 2], [11, 3], [13, 5], [17, 0], [19, 7], [23, 1], [29, 11]]);
  checkSieve(2, 200, [[2, 0], [3, 0], [5, 0], [1, 0]]);
});
test('sieve: a Xenakis-style combination, (3@0 | 4@1) with period 12', function () {
  var r = checkSieve(1, 36, [[3, 0], [4, 1]]);
  var want = sieveMembers(1, 12, [[3, 0], [4, 1]]);
  var again = r.punched.map(function (c) { return +c.trim(); }).filter(function (n) { return n >= 12 && n < 24; })
    .map(function (n) { return n - 12; });
  equal(again, want, 'periodic with period 12');
});
test('sieve: more than ten classes is reported as an error', function () {
  var classes = [];
  for (var i = 0; i < 11; i++) classes.push([i + 2, 0]);
  var r = sieveRun(1, 10, classes);
  equal(r.ok, false);
  ok(logHas(r, 'subscript out of range'));
});
test('sieve: the punched members can be fed back in as data', function () {
  var punched = sieveRun(1, 20, [[5, 2], [5, 3]]).punched;
  var r = go(['DO 5 I = 1, 8', 'READ (5,10) N', 'WRITE (6,20) N', '5 CONTINUE', '10 FORMAT (I5)', '20 FORMAT (1X,I3)', 'STOP'],
    punched);
  ok(r.ok, r.log.join('\n'));
  equal(r.printer.map(Number), [2, 3, 7, 8, 12, 13, 17, 18]);
});
