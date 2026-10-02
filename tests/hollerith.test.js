/* Tests for scripts/hollerith.js */

var ALL_CHARS = ' 0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ&-/.$,(*%+)_<;>:=?#\'"@¢!|¬';

test('punches: letters, digits, space', function () {
  equal(Fortran.punches('A'), [12, 1]);
  equal(Fortran.punches('I'), [12, 9]);
  equal(Fortran.punches('J'), [11, 1]);
  equal(Fortran.punches('R'), [11, 9]);
  equal(Fortran.punches('S'), [0, 2]);
  equal(Fortran.punches('Z'), [0, 9]);
  equal(Fortran.punches('0'), [0]);
  equal(Fortran.punches('7'), [7]);
  equal(Fortran.punches(' '), []);
});

test('punches: symbols', function () {
  equal(Fortran.punches('&'), [12]);
  equal(Fortran.punches('-'), [11]);
  equal(Fortran.punches('/'), [0, 1]);
  equal(Fortran.punches('.'), [12, 8, 3]);
  equal(Fortran.punches('$'), [11, 8, 3]);
  equal(Fortran.punches(','), [0, 8, 3]);
  equal(Fortran.punches('('), [12, 8, 5]);
  equal(Fortran.punches(')'), [11, 8, 5]);
  equal(Fortran.punches('+'), [12, 8, 6]);
  equal(Fortran.punches('*'), [11, 8, 4]);
  equal(Fortran.punches('='), [8, 6]);
  equal(Fortran.punches("'"), [8, 5]);
  equal(Fortran.punches(':'), [8, 2]);
});

test('punches: lowercase maps to uppercase, unknown gives nothing', function () {
  equal(Fortran.punches('a'), [12, 1]);
  equal(Fortran.punches('~'), []);
  equal(Fortran.punches('é'), []);
  equal(Fortran.punches(''), []);
});

test('every character has a distinct punch pattern', function () {
  var seen = {};
  ALL_CHARS.split('').forEach(function (ch) {
    var key = Fortran.punches(ch).join('-');
    ok(!seen.hasOwnProperty(key), '"' + ch + '" shares its punches with "' + seen[key] + '"');
    seen[key] = ch;
  });
});

test('encodeCard gives 80 columns, padded and truncated', function () {
  var masks = Fortran.encodeCard('AB');
  equal(masks.length, 80);
  equal(Array.from(masks[0]), [12, 1]);
  equal(Array.from(masks[1]), [12, 2]);
  equal(masks[2].size, 0);
  equal(Fortran.encodeCard(new Array(100).join('A')).length, 80);
  equal(Fortran.encodeCard('').length, 80);
});

test('encodeCard: lowercase becomes uppercase, unknown characters become blank columns', function () {
  var masks = Fortran.encodeCard('a~');
  equal(Array.from(masks[0]), [12, 1]);
  equal(masks[1].size, 0);
});

test('decodeCard(encodeCard(x)) round-trips the whole character set', function () {
  var text = ALL_CHARS + ALL_CHARS;
  equal(Fortran.decodeCard(Fortran.encodeCard(text)), (text + new Array(81).join(' ')).slice(0, 80));
  equal(Fortran.decodeCard(Fortran.encodeCard(ALL_CHARS)).trimEnd(), ALL_CHARS.trimEnd());
});

test('decodeCard: an unknown pattern decodes as "?", short input counts as blanks', function () {
  var masks = Fortran.encodeCard('A');
  masks[1] = new Set([1, 2]);
  var s = Fortran.decodeCard(masks);
  equal(s.length, 80);
  equal(s.slice(0, 3), 'A? ');
  equal(Fortran.decodeCard([]), new Array(81).join(' '));
});

test('decodeCard accepts arrays of rows as well as Sets', function () {
  var masks = Fortran.encodeCard('HI').map(function (m) { return Array.from(m); });
  equal(Fortran.decodeCard(masks).slice(0, 2), 'HI');
});
