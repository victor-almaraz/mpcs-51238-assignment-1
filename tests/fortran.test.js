/* Tests for scripts/fortran.js: the language, FORMAT, cards and errors. */

var FF = '\f';   // page break marker in result.printer

// "10 FORMAT (I5)" -> labelled card; anything else starts in column 7.
function card(line) {
  var m = /^(\d+) (.*)$/.exec(line);
  return m ? ('     ' + m[1]).slice(-5) + ' ' + m[2] : '      ' + line;
}

// Run a main program (an END card is added) followed by data cards.
function go(lines, data, opts) {
  return Fortran.run(lines.map(card).concat(['      END'], data || []), opts);
}

// Evaluate one expression by printing it with the given FORMAT edit descriptor.
function show(decls, expr, edit) {
  return go(decls.concat(['WRITE (6,10) ' + expr, '10 FORMAT (1X,' + edit + ')', 'STOP'])).printer;
}

function logHas(result, text) {
  return result.log.some(function (l) { return l.indexOf(text) !== -1; });
}

/* ---- the sample decks -------------------------------------------------- */

test('sample 1 prints the expected table on a new page', function () {
  var r = Fortran.run(Fortran.samples[0].cards);
  ok(r.ok, r.log.join('\n'));
  equal(r.printer, [FF,
    '     N      SQUARE     ROOT',
    '     1           1   1.0000',
    '     2           4   1.4142',
    '     3           9   1.7321',
    '     4          16   2.0000',
    '     5          25   2.2361']);
  equal(r.punched, []);
});

test("sample 2 (Heron's formula) is preceded by one blank line", function () {
  var r = Fortran.run(Fortran.samples[1].cards);
  ok(r.ok, r.log.join('\n'));
  equal(r.printer, ['', 'A =    3  B =    4  C =    5  AREA =      6.00']);
});

test('sample 3 finds the largest value', function () {
  var r = Fortran.run(Fortran.samples[2].cards);
  ok(r.ok, r.log.join('\n'));
  equal(r.printer, ['LARGEST OF   5 VALUES:     17.25']);
});

test('sample 4 punches seven cards and prints nothing', function () {
  var r = Fortran.run(Fortran.samples[3].cards);
  ok(r.ok, r.log.join('\n'));
  equal(r.printer, []);
  equal(r.punched.length, 7);
  r.punched.forEach(function (c) { equal(c.length, 80); });
  equal(r.punched.map(function (c) { return c.trim(); }), ['0', '3', '6', '9', '12', '15', '18']);
  equal(r.punched[0], '    0' + new Array(76).join(' '));
});

test('punched cards read back as data cards', function () {
  var punched = Fortran.run(Fortran.samples[3].cards).punched;
  var r = go(['READ (5,10) N', '10 FORMAT (I5)', 'WRITE (6,20) N', '20 FORMAT (1X,I5)', 'READ (5,10) N',
    'WRITE (6,20) N', 'READ (5,10) N', 'WRITE (6,20) N'], punched);
  ok(r.ok, r.log.join('\n'));
  equal(r.printer, ['    0', '    3', '    6']);
});

test('the listing numbers the source cards', function () {
  var r = Fortran.run(Fortran.samples[0].cards);
  equal(r.listing.length, 12);
  equal(r.listing[0], '   1  C     SQUARES AND SQUARE ROOTS');
  equal(r.listing[11], '  12        END');
});

/* ---- acceptance criteria ---------------------------------------------- */

test('DO 10 I = 1.10 is an assignment to DO10I, not a loop', function () {
  var r = go(['DO 10 I = 1.10', 'WRITE (6,20) DO10I', '20 FORMAT (1X,F6.2)', 'STOP']);
  ok(r.ok, r.log.join('\n'));
  equal(r.printer, ['  1.10']);
});

test('blanks are insignificant: G O T O 20', function () {
  var r = go(['G O T O 20', 'WRITE (6,10)', '10 FORMAT (1HX)', '20 STOP']);
  ok(r.ok, r.log.join('\n'));
  equal(r.printer, []);
});

test('column 6: 0 is not a continuation, 1 and * are', function () {
  var r1 = Fortran.run(['      I = 1 +', '     12', '      WRITE (6,10) I', '   10 FORMAT (1X,I3)', '      END']);
  ok(r1.ok, r1.log.join('\n'));
  equal(r1.printer, ['  3']);
  var r2 = Fortran.run(['      I = 1 +', '     *2', '      WRITE (6,10) I', '   10 FORMAT (1X,I3)', '      END']);
  ok(r2.ok, r2.log.join('\n'));
  equal(r2.printer, ['  3']);
});

test('a card with 0 in column 6 is a separate statement', function () {
  var r = Fortran.run(['      I = 1', '     0J = 2', '      WRITE (6,10) I, J', '   10 FORMAT (1X,2I3)', '      END']);
  ok(r.ok, r.log.join('\n'));
  equal(r.printer, ['  1  2']);
});

test('columns 73-80 are ignored and warned about', function () {
  var text = '      I = 5'.padEnd(72) + 'SEQ00010';
  var r = Fortran.run([text, '      WRITE (6,10) I', '   10 FORMAT (1X,I3)', '      END']);
  ok(r.ok, r.log.join('\n'));
  equal(r.printer, ['  5']);
  ok(logHas(r, 'card 1: warning'), r.log.join('\n'));
});

test('FORMAT I5 prints 123 on a normal line', function () {
  var r = go(['WRITE (6,10) 123', '10 FORMAT (I5)', 'STOP']);
  equal(r.printer, [' 123']);   // I5 gives "  123": the first blank is carriage control
});

test('I3 for 123: the leading 1 is carriage control (page break, prints 23)', function () {
  var r = go(['WRITE (6,10) 123', '10 FORMAT (I3)', 'STOP']);
  equal(r.printer, [FF, '23']);
});

test('I5 with a wider field keeps the number', function () {
  equal(show([], '123', 'I5'), ['  123']);
});

test('integer arithmetic: 3/2*2 is 2', function () {
  equal(show([], '3/2*2', 'I3'), ['  2']);
});

test('DO 5 I = 3, 1 runs its body once', function () {
  var r = go(['N = 0', 'DO 5 I = 3, 1', 'N = N + 1', '5 CONTINUE', 'WRITE (6,10) N', '10 FORMAT (1X,I3)', 'STOP']);
  equal(r.printer, ['  1']);
});

test('PUNCH with I5 starts in column 1 and pads to 80', function () {
  var r = go(['N = 3', 'PUNCH 20, N', '20 FORMAT (I5)', 'STOP']);
  equal(r.punched, ['    3' + new Array(76).join(' ')]);
  equal(r.punched[0].length, 80);
});

test('PUNCH with 1X,I5 leaves column 1 blank', function () {
  var r = go(['N = 3', 'PUNCH 20, N', '20 FORMAT (1X,I5)', 'STOP']);
  equal(r.punched[0].slice(0, 6), '     3');
  equal(r.punched[0].length, 80);
});

test('WRITE (7,f) also punches', function () {
  var r = go(['WRITE (7,20) 42', '20 FORMAT (I3)', 'STOP']);
  equal(r.punched[0].slice(0, 3), ' 42');
  equal(r.printer, []);
});

test('a PUNCH record over 80 characters is truncated with a warning', function () {
  var r = go(['PUNCH 20', "20 FORMAT (1H1,78X,'ABCDE')", 'STOP']);
  equal(r.punched[0].length, 80);
  equal(r.punched[0].slice(0, 2), '1 ');   // no carriage-control removal: the 1 stays in column 1
  equal(r.punched[0].slice(79), 'A');
  ok(logHas(r, 'warning'), r.log.join('\n'));
  ok(logHas(r, 'card 1'), r.log.join('\n'));
});

test('an undefined label returns ok: false with a card-numbered log entry', function () {
  var r = go(['GO TO 40', 'STOP']);
  equal(r.ok, false);
  equal(r.log, ['card 1: undefined label 40']);
  equal(r.printer, []);
});

test('Fortran.run never throws', function () {
  var junk = [undefined, null, 5, 'text', {}, [], [null], [1, 2, 3], ['      END'], ['', '', ''],
    ['      IF ('], ['      DO 10 I ='], ['      FORMAT ('], ['      WRITE ('], ['      X = ((('], ['\u0000￿'],
    ['      I = 1/0', '      END'], ['      READ (5,10) I', '   10 FORMAT (I5)', '      END'],
    ['      A(1) = 1', '      END'], ['      WRITE (6,10) 1', '   10 FORMAT (', '      END']];
  junk.forEach(function (j) {
    var r;
    try { r = Fortran.run(j); } catch (e) { throw new Error('threw on ' + JSON.stringify(j) + ': ' + e.message); }
    ok(typeof r.ok === 'boolean' && Array.isArray(r.printer) && Array.isArray(r.punched) &&
      Array.isArray(r.log) && Array.isArray(r.listing), 'bad result for ' + JSON.stringify(j));
  });
});

/* ---- arithmetic and types --------------------------------------------- */

test('integer division truncates toward zero', function () {
  equal(show([], '(-7)/2', 'I3'), [' -3']);
  equal(show([], '7/(-2)', 'I3'), [' -3']);
});

test('mixed integer/real arithmetic promotes to REAL', function () {
  equal(show([], '7/2.0', 'F5.2'), [' 3.50']);
  equal(show([], '2**3', 'I3'), ['  8']);
  equal(show([], '2.0**3', 'F5.1'), ['  8.0']);
  equal(show([], '2**3**2', 'I4'), [' 512']);   // right associative
  equal(show([], '-2**2', 'I3'), [' -4']);
});

test('implicit typing: I-N are integer, others real; declarations override', function () {
  equal(show(['I = 7.9'], 'I', 'I3'), ['  7']);
  equal(show(['X = 7'], 'X', 'F5.1'), ['  7.0']);
  equal(show(['REAL K', 'K = 2.5'], 'K', 'F5.1'), ['  2.5']);
  equal(show(['INTEGER A', 'A = 2.9'], 'A', 'I3'), ['  2']);
});

test('reals are single precision', function () {
  equal(show(['X = 0.1'], 'X*3.0', 'F12.9'), [' 0.300000012']);
  equal(show(['X = 16777216.0'], 'X + 1.0', 'F12.1'), ['  16777216.0']);
});

test('integers are 32-bit', function () {
  equal(show(['I = 2147483647'], 'I + 1', 'I12'), [' -2147483648']);
});

test('uninitialized variables are zero', function () {
  equal(show([], 'K', 'I3'), ['  0']);
});

test('intrinsic functions', function () {
  equal(show([], 'SQRT(16.0)', 'F5.1'), ['  4.0']);
  equal(show([], 'ABS(-2.5)', 'F5.1'), ['  2.5']);
  equal(show([], 'IABS(-4)', 'I3'), ['  4']);
  equal(show([], 'FLOAT(3)/2.0', 'F5.2'), [' 1.50']);
  equal(show([], 'INT(-3.7)', 'I3'), [' -3']);
  equal(show([], 'IFIX(3.7)', 'I3'), ['  3']);
  equal(show([], 'MOD(-7,3)', 'I3'), [' -1']);
  equal(show([], 'AMOD(7.5,2.0)', 'F5.2'), [' 1.50']);
  equal(show([], 'MAX0(3,9,4)', 'I3'), ['  9']);
  equal(show([], 'MIN0(3,9,4)', 'I3'), ['  3']);
  equal(show([], 'AMAX1(1.5,2.5)', 'F5.2'), [' 2.50']);
  equal(show([], 'AMIN1(1.5,2.5)', 'F5.2'), [' 1.50']);
  equal(show([], 'SIGN(3.0,-1.0)', 'F5.1'), [' -3.0']);
  equal(show([], 'ALOG(EXP(2.0))', 'F5.2'), [' 2.00']);
  equal(show([], 'ALOG10(1000.0)', 'F5.2'), [' 3.00']);
  equal(show([], 'SIN(0.0)+COS(0.0)', 'F5.2'), [' 1.00']);
  equal(show([], 'ATAN(1.0)*4.0', 'F6.4'), ['3.1416']);
});

test('logical IF with relational and logical operators', function () {
  var r = go(['K = 0',
    'IF (3 .LT. 4 .AND. .NOT. 1 .GT. 2) K = K + 1',
    'IF (3 .GE. 4 .OR. 2 .NE. 2) K = K + 10',
    'IF (.TRUE.) K = K + 100',
    'IF (.FALSE.) K = K + 1000',
    'IF (1.5 .EQ. 1.5) K = K + 10000',
    'IF (2 .LE. 2.0) K = K + 100000',
    'WRITE (6,10) K', '10 FORMAT (1X,I7)', 'STOP']);
  ok(r.ok, r.log.join('\n'));
  equal(r.printer, [' 110101']);
});

test('arithmetic IF and computed GO TO', function () {
  var r = go(['DO 50 I = -1, 1', 'IF (I) 10, 20, 30', '10 PUNCH 90, 1', 'GO TO 50', '20 PUNCH 90, 2', 'GO TO 50',
    '30 PUNCH 90, 3', '50 CONTINUE', '90 FORMAT (I1)', 'STOP']);
  ok(r.ok, r.log.join('\n'));
  equal(r.punched.map(function (c) { return c.charAt(0); }), ['1', '2', '3']);

  var g = go(['DO 50 I = 0, 4', 'GO TO (10, 20, 30), I', 'PUNCH 90, 9', 'GO TO 50', '10 PUNCH 90, 1', 'GO TO 50',
    '20 PUNCH 90, 2', 'GO TO 50', '30 PUNCH 90, 3', '50 CONTINUE', '90 FORMAT (I1)', 'STOP']);
  ok(g.ok, g.log.join('\n'));
  equal(g.punched.map(function (c) { return c.charAt(0); }), ['9', '1', '2', '3', '9']);
});

test('DO loops: step, negative step, nesting, shared terminator', function () {
  var r = go(['DO 5 I = 1, 10, 3', 'PUNCH 90, I', '5 CONTINUE', '90 FORMAT (I2)', 'STOP']);
  equal(r.punched.map(function (c) { return c.trim(); }), ['1', '4', '7', '10']);
  var d = go(['DO 5 I = 5, 1, -2', 'PUNCH 90, I', '5 CONTINUE', '90 FORMAT (I2)', 'STOP']);
  equal(d.punched.map(function (c) { return c.trim(); }), ['5', '3', '1']);
  var n = go(['DO 5 I = 1, 2', 'DO 5 J = 1, 2', 'PUNCH 90, I*10+J', '5 CONTINUE', '90 FORMAT (I2)', 'STOP']);
  equal(n.punched.map(function (c) { return c.trim(); }), ['11', '12', '21', '22']);
});

test('arrays: one and two dimensions, column-major order', function () {
  var r = go(['DIMENSION IV(3), IW(2,3)', 'DO 10 I = 1, 3', 'IV(I) = I*I', '10 CONTINUE',
    'DO 20 I = 1, 2', 'DO 20 J = 1, 3', 'IW(I,J) = 10*I + J', '20 CONTINUE',
    'WRITE (6,30) IV(3), IW(2,3), IW(1,2)', '30 FORMAT (1X,3I4)', 'STOP']);
  ok(r.ok, r.log.join('\n'));
  equal(r.printer, ['   9  23  12']);
});

test('type declarations may carry dimensions', function () {
  var r = go(['INTEGER T(3)', 'REAL U(2)', 'T(2) = 7', 'U(1) = 1.5', 'WRITE (6,10) T(2), U(1)', '10 FORMAT (1X,I2,F4.1)', 'STOP']);
  ok(r.ok, r.log.join('\n'));
  equal(r.printer, [' 7 1.5']);
});

test('PAUSE logs and continues; STOP n is logged', function () {
  var r = go(['PAUSE 3', 'WRITE (6,10)', '10 FORMAT (1HX)', 'STOP 7']);
  ok(r.ok, r.log.join('\n'));
  equal(r.log, ['PAUSE 3', 'STOP 7']);
  equal(r.printer, ['']);   // the lone X is a carriage control character: an unknown code is a single space
});

/* ---- FORMAT ------------------------------------------------------------ */

test('F output: rounding, negatives, overflow', function () {
  equal(show([], '3.14159', 'F8.3'), ['   3.142']);
  equal(show([], '-2.5', 'F6.1'), ['  -2.5']);
  equal(show([], '0.5', 'F3.2'), ['.50']);          // leading zero dropped to fit
  equal(show([], '12345.0', 'F4.1'), ['****']);
  equal(show([], '6.0', 'F5.0'), ['   6.']);
  equal(show(['X = -0.001'], 'X', 'F6.2'), ['  0.00']);
});

test('E output uses the normalized 0.ddddE+xx form', function () {
  equal(show([], '12345.0', 'E12.4'), ['  0.1235E+05']);
  equal(show([], '-0.00123', 'E12.3'), ['  -0.123E-02']);
  equal(show([], '0.0', 'E10.3'), [' 0.000E+00']);
  equal(show([], '12345.0', 'E5.2'), ['*****']);
});

test('I output: negatives and overflow', function () {
  equal(show([], '-42', 'I5'), ['  -42']);
  equal(show([], '123456', 'I3'), ['***']);
});

test('repeat counts and groups', function () {
  var r = go(['WRITE (6,10) 1, 2, 3, 4, 5.5, 6, 7.5', '10 FORMAT (1X,3I2,2(I2,F4.1))', 'STOP']);
  ok(r.ok, r.log.join('\n'));
  equal(r.printer, [' 1 2 3 4 5.5 6 7.5']);
});

test('nX, / and apostrophe literals', function () {
  var r = go(['WRITE (6,10) 5', "10 FORMAT (1X,'A',2X,'B''C',/,1X,I2)", 'STOP']);
  ok(r.ok, r.log.join('\n'));
  equal(r.printer, ['A  B\'C', ' 5']);
});

test('output stops at the first data descriptor with no data left', function () {
  var r = go(['WRITE (6,10) 5', "10 FORMAT (1X,'N=',I2,' M=',I2,' END')", 'STOP']);
  equal(r.printer, ['N= 5 M=']);
});

test('reversion: a short FORMAT is reused with new records', function () {
  var r = go(['WRITE (6,10) 1, 2, 3', '10 FORMAT (1X,I2)', 'STOP']);
  equal(r.printer, [' 1', ' 2', ' 3']);
});

test('reversion restarts at the last top-level group', function () {
  var r = go(['WRITE (6,10) 1, 2, 3, 4, 5', "10 FORMAT (1X,'A',I2,2(I2,'/'))", 'STOP']);
  ok(r.ok, r.log.join('\n'));
  equal(r.printer, ['A 1 2/ 3/', '4/ 5/']);   // the second record starts at the group, so its first blank is carriage control
});

test('carriage control: blank, 0, -, 1, +', function () {
  var r = go(['WRITE (6,10)', '10 FORMAT (1H ,1HA)',
    'WRITE (6,20)', '20 FORMAT (1H0,1HB)',
    'WRITE (6,30)', '30 FORMAT (1H-,1HC)',
    'WRITE (6,40)', '40 FORMAT (1H1,1HD)',
    'WRITE (6,50)', '50 FORMAT (1H ,1HE)',
    'WRITE (6,60)', '60 FORMAT (1H+,1H-)',
    'STOP']);
  ok(r.ok, r.log.join('\n'));
  equal(r.printer, ['A', '', 'B', '', '', 'C', FF, 'D', '-']);
});

test('an overprint line merges with the previous line', function () {
  var r = go(['WRITE (6,10)', '10 FORMAT (1H ,3HABC)', 'WRITE (6,20)', '20 FORMAT (1H+,1X,1HX)', 'STOP']);
  equal(r.printer, ['AXC']);
});

test('printer lines are truncated to 132 characters with a warning', function () {
  var r = go(['WRITE (6,10)', "10 FORMAT (1X,140X,'Z')", 'STOP']);
  equal(r.printer[0].length, 132);
  ok(logHas(r, 'warning'));
});

test('Hollerith constants keep their blanks', function () {
  var r = go(['WRITE (6,10)', '10 FORMAT (1H ,5HA B C)', 'STOP']);
  equal(r.printer, ['A B C']);
});

test('FORMAT statements may follow their use', function () {
  var r = go(['WRITE (6,10) 4', 'STOP', '10 FORMAT (1X,I2)']);
  equal(r.printer, [' 4']);
});

/* ---- input ------------------------------------------------------------- */

test('READ: integers, blanks, implied decimal point, explicit point', function () {
  var r = go(['READ (5,10) I, J, X, Y, Z', '10 FORMAT (2I3,3F6.2)', 'WRITE (6,20) I, J, X, Y, Z',
    '20 FORMAT (1X,2I3,3F7.2)', 'STOP'], ['  7-12  12341.5      9. ']);
  ok(r.ok, r.log.join('\n'));
  equal(r.printer, ['  7-12  12.34   1.50   9.00']);
});

test('READ: blank numeric fields are zero; F input applies the implied d', function () {
  var r = go(['READ (5,10) I, X', '10 FORMAT (I5,F10.2)', 'WRITE (6,20) I, X', '20 FORMAT (1X,I3,F8.3)', 'STOP'],
    ['         314']);
  ok(r.ok, r.log.join('\n'));
  equal(r.printer, ['  0   3.140']);
});

test('READ: embedded blanks read as zeros, leading and trailing blanks are ignored', function () {
  var r = go(['READ (5,10) I, J', '10 FORMAT (2I5)', 'WRITE (6,20) I, J', '20 FORMAT (1X,2I6)', 'STOP'], [' 1 2  7   ']);
  ok(r.ok, r.log.join('\n'));
  equal(r.printer, ['   102     7']);
});

test('ABS of an integer stays a 32-bit integer', function () {
  equal(show(['I = -2147483647 - 1'], 'ABS(I)', 'I12'), [' -2147483648']);
});

test('READ: E notation and a sign', function () {
  var r = go(['READ (5,10) X', '10 FORMAT (E10.2)', 'WRITE (6,20) X', '20 FORMAT (1X,F8.1)', 'STOP'], ['-1.5E+2']);
  ok(r.ok, r.log.join('\n'));
  equal(r.printer, ['  -150.0']);
});

test('READ: / skips to the next card, reversion reads more cards', function () {
  var r = go(['READ (5,10) I, J', '10 FORMAT (I2,/,I2)', 'READ (5,20) K, L', '20 FORMAT (I2)',
    'WRITE (6,30) I, J, K, L', '30 FORMAT (1X,4I3)', 'STOP'], [' 1', ' 2', ' 3', ' 4']);
  ok(r.ok, r.log.join('\n'));
  equal(r.printer, ['  1  2  3  4']);
});

test('READ f, list and a data card past the end', function () {
  var r = go(['READ 10, N', '10 FORMAT (I5)', 'READ 10, M', 'STOP'], ['    4']);
  equal(r.ok, false);
  ok(logHas(r, 'END OF FILE ON UNIT 5'), r.log.join('\n'));
  ok(logHas(r, 'card 3'), r.log.join('\n'));
});

test('READ: invalid data is reported', function () {
  var r = go(['READ (5,10) N', '10 FORMAT (I5)', 'STOP'], ['  1A2']);
  equal(r.ok, false);
  ok(logHas(r, 'invalid input data'), r.log.join('\n'));
});

test('cards after the first END card are data, not source', function () {
  var r = Fortran.run(['      READ (5,10) N', '   10 FORMAT (I5)', '      WRITE (6,20) N', '   20 FORMAT (1X,I5)',
    '      STOP', '      END', '    7', '      X = (']);
  ok(r.ok, r.log.join('\n'));
  equal(r.printer, ['    7']);
  equal(r.listing.length, 6);
});

/* ---- errors and limits -------------------------------------------------- */

function expectError(lines, text, data) {
  var r = go(lines, data);
  equal(r.ok, false, 'ok for: ' + lines.join(' | '));
  ok(logHas(r, text), 'expected "' + text + '" in log: ' + JSON.stringify(r.log));
  ok(/^card \d+: /.test(r.log[0]), 'log entry has a card number: ' + r.log[0]);
  return r;
}

test('error: unknown statement', function () { expectError(['FROBNICATE 5'], 'unknown statement'); });
test('error: unbalanced parentheses', function () { expectError(['X = (1 + 2'], 'unbalanced parentheses'); });
test('error: missing FORMAT', function () {
  expectError(['WRITE (6,99) 1'], 'undefined label 99');
  expectError(['WRITE (6,10) 1', '10 CONTINUE'], 'missing FORMAT');
});
test('error: bad Hollerith count', function () {
  expectError(['WRITE (6,10)', '10 FORMAT (90HSHORT)'], 'Hollerith');
});
test('error: a Hollerith count that swallows the closing parenthesis', function () {
  expectError(['WRITE (6,10)', '10 FORMAT (10HHELLO)'], 'bad Hollerith count');
});
test('error: too many decimal digits is a FORMAT error, not a crash', function () {
  expectError(['WRITE (6,10) 1.0', '10 FORMAT (F120.110)'], 'bad FORMAT');
});
test('error: arithmetic IF with two labels', function () {
  expectError(['IF (1) 10, 20', '10 CONTINUE', '20 STOP'], 'three labels');
});
test('error: DO terminator not found', function () { expectError(['DO 10 I = 1, 3'], 'DO terminator not found'); });
test('error: DO terminator before the DO', function () {
  expectError(['5 CONTINUE', 'DO 5 I = 1, 3'], 'DO terminator not found');
});
test('error: subscript out of range', function () {
  expectError(['DIMENSION A(3)', 'A(4) = 1.0'], 'subscript out of range');
  expectError(['DIMENSION A(3)', 'I = 0', 'X = A(I)'], 'subscript out of range');
});
test('error: integer division by zero', function () {
  expectError(['I = 0', 'J = 5/I'], 'integer division by zero');
  expectError(['J = MOD(5,0)'], 'division by zero');
});
test('error: duplicate label', function () { expectError(['5 CONTINUE', '5 CONTINUE'], 'duplicate label'); });
test('error: names longer than 6 characters', function () { expectError(['TOOLONG = 1'], 'longer than 6'); });
test('error: continuation card with nothing to continue', function () {
  var r = Fortran.run(['     1X = 1', '      END']);
  equal(r.ok, false);
  ok(logHas(r, 'card 1'));
});
test('error: no END card', function () {
  var r = Fortran.run(['      X = 1']);
  equal(r.ok, false);
  ok(logHas(r, 'no END card'));
});
test('error: invalid label', function () {
  var r = Fortran.run(['  1A2 CONTINUE', '      END']);
  equal(r.ok, false);
  ok(logHas(r, 'invalid statement label'));
});
test('error: FORMAT type mismatch', function () {
  expectError(['WRITE (6,10) 1.5', '10 FORMAT (I5)'], 'FORMAT mismatch');
  expectError(['WRITE (6,10) 2', '10 FORMAT (F5.1)'], 'FORMAT mismatch');
});
test('error: FORMAT with no data descriptor but a list', function () {
  expectError(['WRITE (6,10) 2', "10 FORMAT (1X,'HI')"], 'no data descriptor');
});
test('error: SQRT of a negative number', function () { expectError(['X = SQRT(-1.0)'], 'argument out of range'); });
test('error: undefined function', function () { expectError(['X = FOO(1.0)'], 'undefined array or function'); });
test('error: unsupported units', function () {
  expectError(['WRITE (3,10) 1', '10 FORMAT (I1)'], 'unit 3');
});

test('compile errors are all reported and nothing runs', function () {
  var r = go(['WRITE (6,10)', '10 FORMAT (1HX)', 'GO TO 77', 'FROBNICATE']);
  equal(r.ok, false);
  equal(r.log.length, 2);
  equal(r.printer, []);
});

test('time limit', function () {
  var r = go(['10 GO TO 10'], null, { stmtLimit: 500 });
  equal(r.ok, false);
  ok(logHas(r, 'TIME LIMIT EXCEEDED'));
  var r2 = go(['10 GO TO 10']);
  equal(r2.ok, false);
  ok(logHas(r2, 'TIME LIMIT EXCEEDED'));
});

test('a program that stays under the limit is not stopped', function () {
  var r = go(['DO 5 I = 1, 100', '5 CONTINUE', 'STOP'], null, { stmtLimit: 1000 });
  ok(r.ok, r.log.join('\n'));
});

test('lowercase cards are punched as uppercase and run', function () {
  var r = Fortran.run(['      write (6,10) 5', '   10 format (1x,i2)', '      end']);
  ok(r.ok, r.log.join('\n'));
  equal(r.printer, [' 5']);
});

test('comment cards (C or *) and blank cards are skipped', function () {
  var r = Fortran.run(['C     COMMENT', '* ANOTHER', '', '      WRITE (6,10) 5', '   10 FORMAT (1X,I2)', '      END']);
  ok(r.ok, r.log.join('\n'));
  equal(r.printer, [' 5']);
});

test('the run result is fresh each time', function () {
  var a = Fortran.run(Fortran.samples[3].cards), b = Fortran.run(Fortran.samples[3].cards);
  equal(a.punched.length, 7);
  equal(b.punched.length, 7);
});
