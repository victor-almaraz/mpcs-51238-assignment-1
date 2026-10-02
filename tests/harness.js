/* Minimal test harness: no dependencies, runs in a browser (tests/index.html)
   or in any JavaScript runtime that can evaluate the scripts in order.
   Defines globals: test(name, fn), equal(actual, expected, msg), ok(value, msg),
   Tests.runAll(). */
var Tests = (function () {
  'use strict';
  var list = [];

  function equal(actual, expected, msg) {
    var a = JSON.stringify(actual), e = JSON.stringify(expected);
    if (a !== e) throw new Error((msg ? msg + ': ' : '') + 'expected ' + e + ' but got ' + a);
  }

  function ok(value, msg) {
    if (!value) throw new Error(msg || 'assertion failed');
  }

  function test(name, fn) { list.push({ name: name, fn: fn }); }

  // -> [{ name, passed, error }]
  function runAll() {
    return list.map(function (t) {
      try { t.fn(); return { name: t.name, passed: true, error: '' }; }
      catch (e) { return { name: t.name, passed: false, error: e && e.message ? e.message : String(e) }; }
    });
  }

  return { equal: equal, ok: ok, test: test, runAll: runAll };
})();

var test = Tests.test, equal = Tests.equal, ok = Tests.ok;
