/* FORTRAN IV punched-card interpreter.
   Classic script: defines the global `Fortran`. Load hollerith.js first. No DOM.

   Fortran.encodeCard(text)   string -> 80 column masks
   Fortran.decodeCard(masks)  80 masks -> string
   Fortran.punches(ch)        character -> punched rows
   Fortran.run(cards, opts)   run a deck, never throws
   Fortran.samples            [{ name, cards }]                                  */
var Fortran = (function () {
  'use strict';

  var INT_MAX = 2147483647;
  var DEFAULT_STMT_LIMIT = 1000000;
  var PAGE_BREAK = '\f';   // printer entry that marks a new page

  // A compile-time or run-time problem. Always reported through result.log.
  function FError(message) { this.message = message; }

  function spaces(n) { return ' '.repeat(Math.max(0, n)); }
  function stars(n) { return '*'.repeat(n); }
  function padLeft(s, w) { return spaces(w - s.length) + s; }
  function isDigit(c) { return c >= '0' && c <= '9'; }
  function isFormat(t) { return t.slice(0, 7) === 'FORMAT('; }

  function normalizeCard(c) {
    var s = c == null ? '' : String(c);
    s = s.replace(/[\r\n]+/g, ' ').replace(/\t/g, ' ').toUpperCase();
    return s.length < 80 ? s + spaces(80 - s.length) : s.slice(0, 80);
  }

  /* ------------------------------------------------------------------ */
  /* Text helpers                                                        */
  /* ------------------------------------------------------------------ */

  // Index of the ")" matching the "(" at s[open], or -1.
  function matchParen(s, open) {
    var depth = 0;
    for (var i = open; i < s.length; i++) {
      if (s.charAt(i) === '(') depth++;
      else if (s.charAt(i) === ')') { depth--; if (depth === 0) return i; }
    }
    return -1;
  }

  function checkBalanced(s) {
    var depth = 0;
    for (var i = 0; i < s.length && depth >= 0; i++) {
      if (s.charAt(i) === '(') depth++;
      else if (s.charAt(i) === ')') depth--;
    }
    if (depth !== 0) throw new FError('unbalanced parentheses');
  }

  function hasTopComma(s) {
    var depth = 0;
    for (var i = 0; i < s.length; i++) {
      var c = s.charAt(i);
      if (c === '(') depth++;
      else if (c === ')') depth--;
      else if (c === ',' && depth === 0) return true;
    }
    return false;
  }

  // Split on commas at parenthesis depth 0. "" gives [].
  function splitTop(s) {
    if (s === '') return [];
    var parts = [], depth = 0, cur = '';
    for (var i = 0; i < s.length; i++) {
      var c = s.charAt(i);
      if (c === '(') depth++;
      else if (c === ')') depth--;
      if (c === ',' && depth === 0) { parts.push(cur); cur = ''; }
      else cur += c;
    }
    parts.push(cur);
    return parts;
  }

  // Remove blanks from a statement, except inside nH and '...' literals
  // (Hollerith literals are only recognised in FORMAT statements).
  function stripStatement(text) {
    var fmt = isFormat(text.replace(/ /g, ''));
    var out = '', i = 0, n = text.length;
    var last = text.replace(/ +$/, '').length - 1;   // a Hollerith literal must end before this (the closing ")")
    while (i < n) {
      var c = text.charAt(i);
      if (c === ' ') { i++; continue; }
      if (c === "'") {
        var j = i + 1, lit = "'";
        for (;;) {
          if (j >= n) throw new FError('unterminated apostrophe literal');
          if (text.charAt(j) === "'") {
            if (text.charAt(j + 1) === "'") { lit += "''"; j += 2; continue; }
            lit += "'"; j++; break;
          }
          lit += text.charAt(j++);
        }
        out += lit; i = j; continue;
      }
      if (fmt && isDigit(c)) {
        var prev = out.charAt(out.length - 1);
        if (prev === '(' || prev === ',' || prev === '/') {
          var k = i, digits = '';
          while (k < n && (text.charAt(k) === ' ' || isDigit(text.charAt(k)))) {
            if (text.charAt(k) !== ' ') digits += text.charAt(k);
            k++;
          }
          if (text.charAt(k) === 'H') {
            var count = parseInt(digits, 10);
            if (!(count >= 1) || k + 1 + count > last) throw new FError('bad Hollerith count');
            out += digits + 'H' + text.substr(k + 1, count);
            i = k + 1 + count;
            continue;
          }
        }
      }
      out += c; i++;
    }
    return out;
  }

  /* ------------------------------------------------------------------ */
  /* FORMAT                                                              */
  /* ------------------------------------------------------------------ */

  // Parse a stripped "FORMAT(...)" statement into a flat list of operations.
  // Returns { ops, rev } where rev is where reversion restarts.
  function parseFormat(s) {
    var pos = 6;
    function err(m) { throw new FError('bad FORMAT: ' + m); }
    function readInt() {
      var v = '';
      while (isDigit(s.charAt(pos))) v += s.charAt(pos++);
      return v === '' ? null : parseInt(v, 10);
    }
    function need(what) {
      var v = readInt();
      if (v === null) err('expected ' + what);
      return v;
    }
    function parseList() {
      var items = [];
      for (;;) {
        var c = s.charAt(pos);
        if (c === '') err('missing ")"');
        if (c === ')') { pos++; return items; }
        if (c === ',') { pos++; continue; }
        if (c === '/') { pos++; items.push({ k: '/' }); continue; }
        if (c === "'") {
          var text = '';
          pos++;
          for (;;) {
            if (pos >= s.length) err('unterminated literal');
            if (s.charAt(pos) === "'") {
              if (s.charAt(pos + 1) === "'") { text += "'"; pos += 2; continue; }
              pos++; break;
            }
            text += s.charAt(pos++);
          }
          items.push({ k: 'lit', text: text });
          continue;
        }
        var rep = readInt();
        var hasRep = rep !== null;
        if (!hasRep) rep = 1;
        else if (rep < 1) err('repeat count must be at least 1');
        c = s.charAt(pos);
        if (c === 'H' && hasRep) {
          var h = s.substr(pos + 1, rep);
          if (h.length !== rep) err('bad Hollerith count');
          pos += 1 + rep;
          items.push({ k: 'lit', text: h });
        } else if (c === 'X') {
          pos++;
          items.push({ k: 'X', n: rep });
        } else if (c === '/' && hasRep) {
          pos++;
          for (var q = 0; q < rep; q++) items.push({ k: '/' });
        } else if (c === '(') {
          pos++;
          items.push({ k: 'group', rep: rep, items: parseList() });
        } else if (c === 'I' || c === 'F' || c === 'E') {
          pos++;
          var w = need('field width after ' + c);
          var d = 0;
          if (c !== 'I') {
            if (s.charAt(pos) !== '.') err('expected "." in ' + c + 'w.d');
            pos++;
            d = need('digits after "."');
          }
          if (w < 1) err('field width must be at least 1');
          if (d > 100) err('too many digits after "."');
          if (c === 'E' && d < 1) err('E needs at least 1 digit after "."');
          items.push({ k: c, w: w, d: d, rep: rep });
        } else {
          err('unsupported or misplaced "' + (c || 'end of statement') + '"');
        }
      }
    }
    if (s.charAt(pos) !== '(') err('expected "("');
    pos++;
    var items = parseList();
    if (pos !== s.length) err('unexpected text after closing ")"');

    var ops = [], rev = 0;
    function expand(list, top) {
      list.forEach(function (it) {
        if (it.k === 'group') {
          if (top) rev = ops.length;
          for (var r = 0; r < it.rep; r++) expand(it.items, false);
        } else if (it.k === 'I' || it.k === 'F' || it.k === 'E') {
          for (var r2 = 0; r2 < it.rep; r2++) ops.push({ k: it.k, w: it.w, d: it.d });
        } else {
          ops.push(it);
        }
        if (ops.length > 100000) err('FORMAT is too large');
      });
    }
    expand(items, true);
    return { ops: ops, rev: rev };
  }

  // Drive a FORMAT over a list. cb: more(), data(op), lit(text), x(n), slash().
  function walkFormat(fmt, cb) {
    var ops = fmt.ops, i = 0, progress = false;
    for (;;) {
      if (i >= ops.length) {
        if (!cb.more()) return;
        if (!progress) throw new FError('FORMAT has no data descriptor but the list has items left');
        cb.slash();                 // reversion: new record
        progress = false;
        i = fmt.rev;
        continue;
      }
      var op = ops[i++];
      if (op.k === 'I' || op.k === 'F' || op.k === 'E') {
        if (!cb.more()) return;
        cb.data(op);
        progress = true;
      } else if (op.k === 'X') cb.x(op.n);
      else if (op.k === 'lit') cb.lit(op.text);
      else cb.slash();
    }
  }

  function fmtI(v, w) {
    var s = String(v);
    return s.length > w ? stars(w) : padLeft(s, w);
  }

  function fmtF(v, w, d) {
    if (!isFinite(v)) return stars(w);
    var s = Math.abs(v).toFixed(d);
    if (s.indexOf('e') !== -1) return stars(w);
    if (d === 0) s += '.';
    var neg = v < 0 && /[1-9]/.test(s);
    if (s.length + (neg ? 1 : 0) > w && s.indexOf('0.') === 0) s = s.slice(1);
    s = (neg ? '-' : '') + s;
    return s.length > w ? stars(w) : padLeft(s, w);
  }

  function fmtE(v, w, d) {
    if (!isFinite(v)) return stars(w);
    var digits, exp;
    if (v === 0) { digits = new Array(d + 1).join('0'); exp = 0; }
    else {
      var m = /^(\d)\.?(\d*)e([+-]\d+)$/.exec(Math.abs(v).toExponential(d - 1));
      digits = m[1] + m[2];
      exp = parseInt(m[3], 10) + 1;
    }
    var ex = Math.abs(exp);
    var tail = 'E' + (exp < 0 ? '-' : '+') + (ex < 10 ? '0' : '') + ex;
    var body = '0.' + digits + tail;
    var sign = v < 0 ? '-' : '';
    if (sign.length + body.length > w) body = body.slice(1);
    var s = sign + body;
    return s.length > w ? stars(w) : padLeft(s, w);
  }

  function editOut(op, x) {
    if (op.k === 'I') {
      if (x.t !== 'I') throw new FError('FORMAT mismatch: I' + op.w + ' needs an INTEGER value');
      return fmtI(x.v, op.w);
    }
    if (x.t !== 'R') {
      throw new FError('FORMAT mismatch: ' + op.k + op.w + '.' + op.d + ' needs a REAL value');
    }
    return op.k === 'F' ? fmtF(x.v, op.w, op.d) : fmtE(x.v, op.w, op.d);
  }

  // Run a FORMAT for output. vals: [{t, v}]. Returns the records.
  function formatOutput(fmt, vals) {
    var recs = [], cur = '', vi = 0;
    walkFormat(fmt, {
      more: function () { return vi < vals.length; },
      data: function (op) { cur += editOut(op, vals[vi++]); },
      lit: function (t) { cur += t; },
      x: function (n) { cur += spaces(n); },
      slash: function () { recs.push(cur); cur = ''; }
    });
    recs.push(cur);
    return recs;
  }

  // Leading and trailing blanks are ignored; embedded blanks read as zeros, as on the 029-era machines.
  function fieldText(field) { return field.trim().replace(/ /g, '0'); }

  function parseIntField(field, where) {
    var t = fieldText(field);
    if (t === '') return 0;
    if (!/^[+-]?\d+$/.test(t)) throw new FError('invalid input data "' + field.trim() + '" ' + where);
    return parseInt(t, 10) | 0;
  }

  function parseRealField(field, d, where) {
    var t = fieldText(field);
    if (t === '') return 0;
    var m = /^([+-]?)(\d*)(\.?)(\d*)(?:E([+-]?\d+))?$/.exec(t);
    if (!m || (m[2] === '' && m[4] === '')) {
      throw new FError('invalid input data "' + field.trim() + '" ' + where);
    }
    var v;
    if (m[3] === '.') v = parseFloat((m[2] || '0') + '.' + (m[4] || '0'));
    else v = parseInt(m[2] + m[4], 10) / Math.pow(10, d);   // implied decimal point
    if (m[5]) v *= Math.pow(10, parseInt(m[5], 10));
    if (m[1] === '-') v = -v;
    return Math.fround(v);
  }

  // Run a FORMAT for input. dests: [{t, set(E, v)}].
  function formatInput(fmt, dests, E) {
    var line = E.nextCard(), pos = 0, di = 0;
    walkFormat(fmt, {
      more: function () { return di < dests.length; },
      data: function (op) {
        var dest = dests[di++];
        var field = line.text.substr(pos, op.w);
        pos += op.w;
        var where = 'on data card ' + line.n;
        if (op.k === 'I') {
          if (dest.t !== 'I') throw new FError('FORMAT mismatch: I' + op.w + ' needs an INTEGER variable');
          dest.set(E, parseIntField(field, where));
        } else {
          if (dest.t !== 'R') {
            throw new FError('FORMAT mismatch: ' + op.k + op.w + '.' + op.d + ' needs a REAL variable');
          }
          dest.set(E, parseRealField(field, op.d, where));
        }
      },
      lit: function (t) { pos += t.length; },
      x: function (n) { pos += n; },
      slash: function () { line = E.nextCard(); pos = 0; }
    });
  }

  /* ------------------------------------------------------------------ */
  /* Expressions                                                         */
  /* ------------------------------------------------------------------ */

  function trunc32(x) { return Math.trunc(x) | 0; }

  function toR(n) {
    if (n.t === 'L') throw new FError('logical value where a number is needed');
    if (n.t === 'R') return n;
    return { t: 'R', f: function (E) { return Math.fround(n.f(E)); } };
  }

  function toI(n) {
    if (n.t === 'L') throw new FError('logical value where a number is needed');
    if (n.t === 'I') return n;
    return { t: 'I', f: function (E) { return trunc32(n.f(E)); } };
  }

  function ipow(x, y) {
    if (y < 0) {
      if (x === 1) return 1;
      if (x === -1) return (y % 2 === 0) ? 1 : -1;
      if (x === 0) throw new FError('zero raised to a negative power');
      return 0;
    }
    var r = 1;
    while (y > 0) {
      if (y & 1) r = Math.imul(r, x);
      x = Math.imul(x, x);
      y >>= 1;
    }
    return r;
  }

  var RELOPS = {
    LT: function (a, b) { return a < b; }, LE: function (a, b) { return a <= b; },
    EQ: function (a, b) { return a === b; }, NE: function (a, b) { return a !== b; },
    GT: function (a, b) { return a > b; }, GE: function (a, b) { return a >= b; }
  };

  function arith(op, a, b) {
    if (a.t === 'L' || b.t === 'L') throw new FError('logical value where a number is needed');
    var f;
    if (a.t === 'I' && b.t === 'I') {
      var af = a.f, bf = b.f;
      if (op === '+') f = function (E) { return (af(E) + bf(E)) | 0; };
      else if (op === '-') f = function (E) { return (af(E) - bf(E)) | 0; };
      else if (op === '*') f = function (E) { return Math.imul(af(E), bf(E)); };
      else if (op === '/') {
        f = function (E) {
          var x = af(E), y = bf(E);
          if (y === 0) throw new FError('integer division by zero');
          return (x / y) | 0;
        };
      } else f = function (E) { return ipow(af(E), bf(E)); };
      return { t: 'I', f: f };
    }
    var ra = toR(a).f, rb = toR(b).f;
    if (op === '+') f = function (E) { return Math.fround(ra(E) + rb(E)); };
    else if (op === '-') f = function (E) { return Math.fround(ra(E) - rb(E)); };
    else if (op === '*') f = function (E) { return Math.fround(ra(E) * rb(E)); };
    else if (op === '/') {
      f = function (E) {
        var x = ra(E), y = rb(E);
        if (y === 0) throw new FError('division by zero');
        return Math.fround(x / y);
      };
    } else {
      f = function (E) {
        var r = Math.pow(ra(E), rb(E));
        if (r !== r) throw new FError('invalid exponentiation');
        return Math.fround(r);
      };
    }
    return { t: 'R', f: f };
  }

  // name(args) for the intrinsic functions.
  function intrinsic(name, args) {
    function arity(min, max) {
      if (args.length < min || args.length > max) {
        throw new FError('wrong number of arguments for ' + name);
      }
    }
    function real(fn, domain) {
      arity(1, 1);
      var a = toR(args[0]).f;
      return {
        t: 'R', f: function (E) {
          var x = a(E);
          if (domain && !domain(x)) throw new FError('argument out of range for ' + name);
          return Math.fround(fn(x));
        }
      };
    }
    function fold(type, pick) {
      arity(2, 99);
      var conv = args.map(type === 'I' ? toI : toR).map(function (n) { return n.f; });
      return {
        t: type, f: function (E) {
          var r = conv[0](E);
          for (var i = 1; i < conv.length; i++) r = pick(r, conv[i](E));
          return r;
        }
      };
    }
    switch (name) {
      case 'SQRT': return real(Math.sqrt, function (x) { return x >= 0; });
      case 'SIN': return real(Math.sin);
      case 'COS': return real(Math.cos);
      case 'ATAN': return real(Math.atan);
      case 'EXP': return real(Math.exp);
      case 'ALOG': return real(Math.log, function (x) { return x > 0; });
      case 'ALOG10': return real(Math.log10, function (x) { return x > 0; });
      case 'ABS': {
        arity(1, 1);
        var an = args[0];
        if (an.t === 'L') throw new FError('logical value where a number is needed');
        var af = an.f;
        return an.t === 'I'
          ? { t: 'I', f: function (E) { return Math.abs(af(E)) | 0; } }
          : { t: 'R', f: function (E) { return Math.abs(af(E)); } };
      }
      case 'IABS': {
        arity(1, 1);
        var ia = toI(args[0]).f;
        return { t: 'I', f: function (E) { return Math.abs(ia(E)) | 0; } };
      }
      case 'FLOAT': arity(1, 1); return toR(args[0]);
      case 'INT': case 'IFIX': arity(1, 1); return toI(args[0]);
      case 'MOD': {
        arity(2, 2);
        var m1 = toI(args[0]).f, m2 = toI(args[1]).f;
        return {
          t: 'I', f: function (E) {
            var y = m2(E);
            if (y === 0) throw new FError('integer division by zero in MOD');
            return m1(E) % y | 0;
          }
        };
      }
      case 'AMOD': {
        arity(2, 2);
        var r1 = toR(args[0]).f, r2 = toR(args[1]).f;
        return {
          t: 'R', f: function (E) {
            var y = r2(E);
            if (y === 0) throw new FError('division by zero in AMOD');
            return Math.fround(r1(E) % y);
          }
        };
      }
      case 'MAX0': return fold('I', Math.max);
      case 'MIN0': return fold('I', Math.min);
      case 'AMAX1': return fold('R', Math.max);
      case 'AMIN1': return fold('R', Math.min);
      case 'SIGN': {
        arity(2, 2);
        var t = (args[0].t === 'I' && args[1].t === 'I') ? 'I' : 'R';
        var s1 = (t === 'I' ? toI : toR)(args[0]).f, s2 = (t === 'I' ? toI : toR)(args[1]).f;
        return {
          t: t, f: function (E) {
            var a = Math.abs(s1(E));
            return s2(E) < 0 ? -a : a;
          }
        };
      }
    }
    throw new FError('undefined array or function ' + name);
  }

  function checkName(name) {
    if (name.length > 6) throw new FError('name "' + name + '" is longer than 6 characters');
  }

  // Subscript -> zero-based offset function.
  function subscriptOffset(name, dims, subs) {
    if (subs.length !== dims.length) {
      throw new FError(name + ' needs ' + dims.length + ' subscript' + (dims.length > 1 ? 's' : ''));
    }
    var fs = subs.map(function (s) { return toI(s).f; });
    return function (E) {
      var idx = fs.map(function (f) { return f(E); });
      for (var k = 0; k < idx.length; k++) {
        if (idx[k] < 1 || idx[k] > dims[k]) {
          throw new FError('subscript out of range: ' + name + '(' + idx.join(',') + ')');
        }
      }
      return idx.length === 1 ? idx[0] - 1 : (idx[0] - 1) + (idx[1] - 1) * dims[0];
    };
  }

  // S = { typeOf(name), dims: { name: [..] } }
  function compileExpr(src, S) {
    var pos = 0;
    function fail(m) { throw new FError(m); }

    function peekOp() {
      if (src.charAt(pos) !== '.') return null;
      var m = /^\.(LT|LE|EQ|NE|GT|GE|AND|OR|NOT|TRUE|FALSE)\./.exec(src.substr(pos, 7));
      return m ? m[1] : null;
    }
    function eatOp(op) { pos += op.length + 2; }
    function needLogical(n) {
      if (n.t !== 'L') fail('numeric value where a logical value is needed');
      return n.f;
    }

    function pOr() {
      var left = pAnd();
      while (peekOp() === 'OR') {
        eatOp('OR');
        left = (function (a, b) {
          var af = needLogical(a), bf = needLogical(b);
          return { t: 'L', f: function (E) { return af(E) || bf(E); } };
        })(left, pAnd());
      }
      return left;
    }
    function pAnd() {
      var left = pNot();
      while (peekOp() === 'AND') {
        eatOp('AND');
        left = (function (a, b) {
          var af = needLogical(a), bf = needLogical(b);
          return { t: 'L', f: function (E) { return af(E) && bf(E); } };
        })(left, pNot());
      }
      return left;
    }
    function pNot() {
      if (peekOp() === 'NOT') {
        eatOp('NOT');
        var f = needLogical(pNot());
        return { t: 'L', f: function (E) { return !f(E); } };
      }
      return pRel();
    }
    function pRel() {
      var left = pArith(), op = peekOp();
      if (op && RELOPS[op]) {
        eatOp(op);
        var right = pArith();
        if (left.t === 'L' || right.t === 'L') fail('logical value in a comparison');
        if (left.t !== right.t) { left = toR(left); right = toR(right); }
        var cmp = RELOPS[op], lf = left.f, rf = right.f;
        return { t: 'L', f: function (E) { return cmp(lf(E), rf(E)); } };
      }
      return left;
    }
    function pArith() {
      var neg = false, c = src.charAt(pos);
      if (c === '+' || c === '-') { neg = c === '-'; pos++; }
      var left = pTerm();
      if (neg) left = negate(left);
      for (;;) {
        c = src.charAt(pos);
        if (c !== '+' && c !== '-') return left;
        pos++;
        left = arith(c, left, pTerm());
      }
    }
    function negate(n) {
      if (n.t === 'L') fail('logical value where a number is needed');
      var f = n.f;
      return n.t === 'I'
        ? { t: 'I', f: function (E) { return (-f(E)) | 0; } }
        : { t: 'R', f: function (E) { return -f(E); } };
    }
    function pTerm() {
      var left = pFactor();
      for (;;) {
        var c = src.charAt(pos);
        if (c === '*' && src.charAt(pos + 1) !== '*') { pos++; left = arith('*', left, pFactor()); }
        else if (c === '/') { pos++; left = arith('/', left, pFactor()); }
        else return left;
      }
    }
    function pFactor() {
      var base = pPrimary();
      if (src.substr(pos, 2) === '**') {
        pos += 2;
        var neg = false;
        if (src.charAt(pos) === '-') { neg = true; pos++; } else if (src.charAt(pos) === '+') pos++;
        var exp = pFactor();
        if (neg) exp = negate(exp);
        return arith('**', base, exp);
      }
      return base;
    }
    function pArgs() {
      var args = [];
      pos++;   // "("
      for (;;) {
        args.push(pOr());
        var c = src.charAt(pos++);
        if (c === ')') return args;
        if (c !== ',') fail('expected "," or ")"');
      }
    }
    function pNumber() {
      var start = pos, isReal = false;
      while (isDigit(src.charAt(pos))) pos++;
      if (src.charAt(pos) === '.' && !peekOp()) {
        isReal = true; pos++;
        while (isDigit(src.charAt(pos))) pos++;
      }
      var m = /^E[+-]?\d+/.exec(src.substr(pos));
      if (m) { isReal = true; pos += m[0].length; }
      var text = src.slice(start, pos), v;
      if (isReal) {
        v = Math.fround(parseFloat(text));
        return { t: 'R', f: function () { return v; } };
      }
      v = parseInt(text, 10);
      if (v > INT_MAX) fail('integer constant too large');
      return { t: 'I', f: function () { return v; } };
    }
    function pPrimary() {
      var c = src.charAt(pos);
      if (c === '(') {
        pos++;
        var e = pOr();
        if (src.charAt(pos++) !== ')') fail('unbalanced parentheses');
        return e;
      }
      if (isDigit(c) || (c === '.' && isDigit(src.charAt(pos + 1)))) return pNumber();
      if (c === '.') {
        var op = peekOp();
        if (op === 'TRUE' || op === 'FALSE') {
          eatOp(op);
          var tv = op === 'TRUE';
          return { t: 'L', f: function () { return tv; } };
        }
        fail('unexpected "."');
      }
      var m = /^[A-Z][A-Z0-9]*/.exec(src.substr(pos));
      if (!m) fail(c === '' ? 'expression ends early' : 'unexpected "' + c + '"');
      var name = m[0];
      pos += name.length;
      if (src.charAt(pos) === '(') {
        var args = pArgs();
        if (S.dims[name]) {
          checkName(name);
          var off = subscriptOffset(name, S.dims[name], args);
          return { t: S.typeOf(name), f: function (E) { return E.a[name][off(E)]; } };
        }
        return intrinsic(name, args);
      }
      checkName(name);
      if (S.dims[name]) fail('array ' + name + ' used without subscripts');
      return { t: S.typeOf(name), f: function (E) { var v = E.v[name]; return v === undefined ? 0 : v; } };
    }

    if (src === '') fail('missing expression');
    var node = pOr();
    if (pos < src.length) fail('unexpected "' + src.charAt(pos) + '"');
    return node;
  }

  // NAME or NAME(subscripts) -> { t, set(E, v) }
  function compileLvalue(src, S) {
    var m = /^([A-Z][A-Z0-9]*)(\((.*)\))?$/.exec(src);
    if (!m || (m[2] && matchParen(src, m[1].length) !== src.length - 1)) {
      throw new FError('"' + src + '" cannot be assigned to');
    }
    var name = m[1];
    checkName(name);
    var t = S.typeOf(name);
    if (m[2]) {
      if (!S.dims[name]) throw new FError(name + ' is not a DIMENSIONed array');
      var subs = splitTop(m[3]).map(function (p) { return compileExpr(p, S); });
      var off = subscriptOffset(name, S.dims[name], subs);
      return { t: t, set: function (E, v) { E.a[name][off(E)] = v; } };
    }
    if (S.dims[name]) throw new FError('array ' + name + ' used without subscripts');
    return { t: t, set: function (E, v) { E.v[name] = v; } };
  }

  /* ------------------------------------------------------------------ */
  /* Statements                                                          */
  /* ------------------------------------------------------------------ */

  // ctx: { card, index, labels, formats }
  function labelIndex(ctx, label) {
    var idx = ctx.labels[label];
    if (idx === undefined) throw new FError('undefined label ' + label);
    return idx;
  }

  function matchAssignment(t) {
    var m = /^[A-Z][A-Z0-9]*/.exec(t);
    if (!m) return null;
    var p = m[0].length;
    if (t.charAt(p) === '(') {
      var close = matchParen(t, p);
      if (close < 0) return null;
      p = close + 1;
    }
    if (t.charAt(p) !== '=') return null;
    var rhs = t.slice(p + 1);
    if (hasTopComma(rhs)) return null;
    return { lhs: t.slice(0, p), rhs: rhs };
  }

  // READ / WRITE / PRINT / PUNCH
  function compileIO(t, keyword, S, ctx) {
    var rest = t.slice(keyword.length), unit, label, list;
    if (rest.charAt(0) === '(') {
      var close = matchParen(rest, 0);
      var control = rest.slice(1, close).split(',');
      if (control.length !== 2 || !/^\d+$/.test(control[0]) || !/^\d+$/.test(control[1])) {
        throw new FError('unsupported I/O control list "' + rest.slice(0, close + 1) + '"');
      }
      unit = parseInt(control[0], 10);
      label = parseInt(control[1], 10);
      list = rest.slice(close + 1);
    } else {
      var m = /^(\d+)(?:,(.*))?$/.exec(rest);
      if (!m) throw new FError('bad ' + keyword + ' statement');
      unit = keyword === 'READ' ? 5 : keyword === 'PUNCH' ? 7 : 6;
      label = parseInt(m[1], 10);
      list = m[2] || '';
    }
    var input = keyword === 'READ';
    if (input ? unit !== 5 : (unit !== 6 && unit !== 7)) {
      throw new FError('unit ' + unit + ' is not available (reader is 5, printer 6, punch 7)');
    }
    var fidx = labelIndex(ctx, label);
    var fmt = ctx.formats[fidx];
    if (!fmt) throw new FError('missing FORMAT: label ' + label + ' is not a FORMAT statement');
    var parts = splitTop(list);
    parts.forEach(function (p) {
      if (/^\(.*,[A-Z][A-Z0-9]*=.*\)$/.test(p)) throw new FError('implied DO in an I/O list is not supported');
    });
    if (input) {
      var dests = parts.map(function (p) { return compileLvalue(p, S); });
      return { exec: function (E) { formatInput(fmt, dests, E); } };
    }
    var items = parts.map(function (p) {
      var n = compileExpr(p, S);
      if (n.t === 'L') throw new FError('a logical value cannot be written');
      return n;
    });
    return {
      exec: function (E) {
        var vals = items.map(function (n) { return { t: n.t, v: n.f(E) }; });
        var recs = formatOutput(fmt, vals);
        for (var i = 0; i < recs.length; i++) {
          if (unit === 6) E.print(recs[i]); else E.punch(recs[i]);
        }
      }
    };
  }

  function compileStatement(t, S, ctx, nested) {
    var m;
    if (isFormat(t)) {   // parsed earlier, with the declarations
      if (nested) throw new FError('FORMAT is not allowed in a logical IF');
      return { exec: null };
    }
    checkBalanced(t);

    var asg = matchAssignment(t);
    if (asg) {
      var lv = compileLvalue(asg.lhs, S);
      var rhs = (lv.t === 'I' ? toI : toR)(compileExpr(asg.rhs, S));
      return { exec: function (E) { lv.set(E, rhs.f(E)); } };
    }

    if (/^(INTEGER|REAL|DIMENSION)/.test(t)) {
      if (nested) throw new FError('declarations are not allowed in a logical IF');
      return { exec: null };
    }

    if (t === 'CONTINUE') return { exec: function () {} };

    if (t === 'END') {
      if (nested) throw new FError('END is not allowed in a logical IF');
      return { exec: function (E) { E.done = true; } };
    }

    if ((m = /^STOP(\d*)$/.exec(t))) {
      var code = m[1] === '' ? '' : String(parseInt(m[1], 10));
      return {
        exec: function (E) {
          if (code !== '') E.log.push('STOP ' + code);
          E.done = true;
        }
      };
    }

    if ((m = /^PAUSE(\d*)$/.exec(t))) {
      var pcode = m[1] === '' ? 'PAUSE' : 'PAUSE ' + parseInt(m[1], 10);
      return { exec: function (E) { E.log.push(pcode); } };
    }

    if ((m = /^GOTO(\d+)$/.exec(t))) {
      var target = labelIndex(ctx, parseInt(m[1], 10));
      return { exec: function () { return target; } };
    }

    if (/^GOTO\(/.test(t)) {
      var close = matchParen(t, 4);
      var targets = splitTop(t.slice(5, close)).map(function (p) {
        if (!/^\d+$/.test(p)) throw new FError('bad label list in computed GO TO');
        return labelIndex(ctx, parseInt(p, 10));
      });
      var sel = toI(compileExpr(t.slice(close + 1).replace(/^,/, ''), S)).f;
      return {
        exec: function (E) {
          var i = sel(E);
          if (i >= 1 && i <= targets.length) return targets[i - 1];
        }
      };
    }

    if (/^IF\(/.test(t)) {
      if (nested) throw new FError('IF is not allowed in a logical IF');
      var c = matchParen(t, 2);
      var cond = compileExpr(t.slice(3, c), S);
      var after = t.slice(c + 1);
      if ((m = /^(\d+),(\d+),(\d+)$/.exec(after))) {
        if (cond.t === 'L') throw new FError('arithmetic IF needs a numeric expression');
        var f = cond.f;
        var neg = labelIndex(ctx, parseInt(m[1], 10));
        var zero = labelIndex(ctx, parseInt(m[2], 10));
        var pos = labelIndex(ctx, parseInt(m[3], 10));
        return {
          exec: function (E) {
            var x = f(E);
            return x < 0 ? neg : x === 0 ? zero : pos;
          }
        };
      }
      if (isDigit(after.charAt(0))) throw new FError('arithmetic IF needs three labels');
      if (cond.t !== 'L') throw new FError('logical IF needs a logical expression');
      if (after === '') throw new FError('logical IF has no statement');
      var inner = compileStatement(after, S, ctx, true);
      if (!inner.exec) throw new FError('bad statement in logical IF');
      var lf = cond.f, ex = inner.exec;
      return { exec: function (E) { if (lf(E)) return ex(E); } };
    }

    if ((m = /^DO(\d+),?([A-Z][A-Z0-9]*)=(.+)$/.exec(t))) {
      if (nested) throw new FError('DO is not allowed in a logical IF');
      var term = ctx.labels[parseInt(m[1], 10)];
      if (term === undefined || term <= ctx.index) {
        throw new FError('DO terminator not found: label ' + parseInt(m[1], 10));
      }
      var name = m[2];
      checkName(name);
      if (S.dims[name]) throw new FError('array ' + name + ' used without subscripts');
      if (S.typeOf(name) !== 'I') throw new FError('DO variable ' + name + ' must be INTEGER');
      var params = splitTop(m[3]);
      if (params.length < 2 || params.length > 3) throw new FError('bad DO parameters');
      var pf = params.map(function (p) { return toI(compileExpr(p, S)).f; });
      var doIndex = ctx.index;
      return {
        exec: function (E) {
          var start = pf[0](E), limit = pf[1](E), step = pf.length === 3 ? pf[2](E) : 1;
          if (step === 0) throw new FError('DO step is zero');
          var trips = Math.max(1, Math.trunc((limit - start + step) / step));   // one-trip
          while (E.stack.length && E.stack[E.stack.length - 1].doIndex === doIndex) E.stack.pop();
          E.v[name] = start;
          E.stack.push({ doIndex: doIndex, term: term, start: doIndex + 1, name: name, cur: start, step: step, left: trips });
        }
      };
    }

    if (/^READ/.test(t)) return compileIO(t, 'READ', S, ctx);
    if (/^WRITE\(/.test(t)) return compileIO(t, 'WRITE', S, ctx);
    if (/^PRINT/.test(t)) return compileIO(t, 'PRINT', S, ctx);
    if (/^PUNCH/.test(t)) return compileIO(t, 'PUNCH', S, ctx);

    throw new FError('unknown statement "' + t.slice(0, 20) + '"');
  }

  /* ------------------------------------------------------------------ */
  /* Running a deck                                                      */
  /* ------------------------------------------------------------------ */

  function isCommentCard(line) {
    var c = line.charAt(0);
    return c === 'C' || c === '*';
  }

  function isContinuation(line) {
    var c = line.charAt(5);
    return c !== ' ' && c !== '0';
  }

  function runDeck(rawCards, opts, result) {
    var log = result.log;
    var failed = false;
    function error(card, msg) { failed = true; log.push((card ? 'card ' + card + ': ' : '') + msg); }
    function warn(card, msg) { log.push('card ' + card + ': warning: ' + msg); }

    var cards = (Array.isArray(rawCards) ? rawCards : []).map(normalizeCard);
    var limit = opts && typeof opts.stmtLimit === 'number' && opts.stmtLimit > 0
      ? opts.stmtLimit : DEFAULT_STMT_LIMIT;

    // Source ends at the first END card.
    var endAt = -1, i;
    for (i = 0; i < cards.length; i++) {
      var ln = cards[i];
      if (isCommentCard(ln) || isContinuation(ln)) continue;
      if (ln.slice(6, 72).replace(/ /g, '') === 'END') { endAt = i; break; }
    }
    var srcCount = endAt === -1 ? cards.length : endAt + 1;
    if (endAt === -1) error(0, 'no END card in the deck');

    // Listing, then statements (first card + continuations).
    var stmts = [], prev = null;
    for (i = 0; i < srcCount; i++) {
      var line = cards[i], n = i + 1;
      result.listing.push(padLeft(String(n), 4) + '  ' + line.replace(/ +$/, ''));
      if (line.slice(72).trim() !== '') warn(n, 'columns 73-80 are ignored');
      if (isCommentCard(line) || line.slice(0, 72).trim() === '') continue;
      var labelField = line.slice(0, 5).replace(/ /g, ''), body = line.slice(6, 72);
      if (isContinuation(line)) {
        if (!prev) error(n, 'continuation card has no statement to continue');
        else {
          if (labelField !== '') warn(n, 'label on a continuation card is ignored');
          prev.text += body;
        }
        continue;
      }
      if (labelField !== '' && !/^\d+$/.test(labelField)) {
        error(n, 'invalid statement label "' + labelField + '"');
        prev = null;
        continue;
      }
      prev = { card: n, label: labelField === '' ? null : parseInt(labelField, 10), text: body };
      stmts.push(prev);
    }

    // Strip blanks; collect labels.
    var labels = {};
    stmts.forEach(function (st, k) {
      st.index = k;
      try { st.t = stripStatement(st.text); }
      catch (e) { if (!(e instanceof FError)) throw e; error(st.card, e.message); st.t = null; }
      if (st.label !== null) {
        if (labels[st.label] !== undefined) error(st.card, 'duplicate label ' + st.label);
        else labels[st.label] = k;
      }
    });

    // Declarations and FORMATs (they can appear anywhere).
    var declared = {}, dims = {}, formats = {};
    var S = {
      dims: dims,
      typeOf: function (name) {
        return declared[name] || (/^[I-N]/.test(name) ? 'I' : 'R');
      }
    };
    stmts.forEach(function (st) {
      var t = st.t;
      if (t === null) return;
      try {
        if (t === '') throw new FError('empty statement');
        if (isFormat(t)) { formats[st.index] = parseFormat(t); return; }
        var m = /^(INTEGER|REAL|DIMENSION)(.*)$/.exec(t);
        if (!m || matchAssignment(t)) return;
        checkBalanced(t);
        var kind = m[1];
        splitTop(m[2]).forEach(function (item) {
          var d = /^([A-Z][A-Z0-9]*)(?:\((\d+)(?:,(\d+))?\))?$/.exec(item);
          if (!d) throw new FError('bad declaration "' + item + '"');
          checkName(d[1]);
          if (kind !== 'DIMENSION') declared[d[1]] = kind === 'INTEGER' ? 'I' : 'R';
          if (d[2] !== undefined) {
            var size = [parseInt(d[2], 10)];
            if (d[3] !== undefined) size.push(parseInt(d[3], 10));
            if (size.indexOf(0) !== -1 || size.reduce(function (a, b) { return a * b; }, 1) > 1000000) {
              throw new FError('bad array size for ' + d[1]);
            }
            if (dims[d[1]]) throw new FError(d[1] + ' is dimensioned twice');
            dims[d[1]] = size;
          } else if (kind === 'DIMENSION') {
            throw new FError('DIMENSION needs a size for ' + d[1]);
          }
        });
      } catch (e) {
        if (!(e instanceof FError)) throw e;
        error(st.card, e.message);
      }
    });

    // Compile.
    stmts.forEach(function (st) {
      st.exec = null;
      if (st.t === null || st.t === '') return;
      try {
        var out = compileStatement(st.t, S, { card: st.card, index: st.index, labels: labels, formats: formats }, false);
        st.exec = out.exec;
      } catch (e) {
        if (!(e instanceof FError)) throw e;
        error(st.card, e.message);
      }
    });

    if (failed) { result.ok = false; return; }

    // Run.
    var data = [];
    for (i = srcCount; i < cards.length; i++) data.push({ n: i + 1, text: cards[i] });
    var dp = 0;
    var E = {
      v: Object.create(null),
      a: Object.create(null),
      stack: [],
      done: false,
      log: log,
      cur: null,
      nextCard: function () {
        if (dp >= data.length) throw new FError('END OF FILE ON UNIT 5');
        return data[dp++];
      },
      print: function (rec) {
        var cc = rec.charAt(0), text = rec.slice(1), p = result.printer;
        if (text.length > 132) {
          text = text.slice(0, 132);
          warn(E.cur.card, 'printer line truncated to 132 characters');
        }
        if (cc === '+' && p.length && p[p.length - 1] !== PAGE_BREAK) {
          var old = p[p.length - 1], merged = '';
          for (var k = 0; k < Math.max(old.length, text.length); k++) {
            var nc = text.charAt(k);
            merged += nc !== '' && nc !== ' ' ? nc : (old.charAt(k) || ' ');
          }
          p[p.length - 1] = merged;
          return;
        }
        if (cc === '0') p.push('');
        else if (cc === '-') p.push('', '');
        else if (cc === '1') p.push(PAGE_BREAK);
        p.push(text);
      },
      punch: function (rec) {
        if (rec.length > 80) {
          rec = rec.slice(0, 80);
          warn(E.cur.card, 'punched record truncated to 80 columns');
        }
        result.punched.push(rec + spaces(80 - rec.length));
      }
    };
    Object.keys(dims).forEach(function (name) {
      var size = dims[name].reduce(function (a, b) { return a * b; }, 1);
      E.a[name] = new Array(size).fill(0);
    });

    var pc = 0, count = 0;
    try {
      while (!E.done && pc < stmts.length) {
        var st = stmts[pc];
        if (!st.exec) { pc++; continue; }
        if (count >= limit) { E.cur = st; throw new FError('TIME LIMIT EXCEEDED'); }
        count++;
        E.cur = st;
        var here = pc, next = st.exec(E);
        if (next === undefined) {
          pc = here + 1;
          while (E.stack.length) {                         // end of a DO loop?
            var fr = E.stack[E.stack.length - 1];
            if (fr.term !== here) break;
            if (--fr.left > 0) {
              fr.cur = (fr.cur + fr.step) | 0;
              E.v[fr.name] = fr.cur;
              pc = fr.start;
              break;
            }
            E.stack.pop();
          }
        } else {
          pc = next;
          while (E.stack.length) {                         // jumped out of a loop?
            var top = E.stack[E.stack.length - 1];
            if (pc >= top.start && pc <= top.term) break;
            E.stack.pop();
          }
        }
      }
    } catch (e) {
      if (!(e instanceof FError)) throw e;
      error(E.cur ? E.cur.card : 0, e.message);
    }
    result.ok = !failed;
  }

  function run(cards, opts) {
    var result = { ok: true, printer: [], punched: [], log: [], listing: [] };
    try {
      runDeck(cards, opts, result);
    } catch (e) {
      result.ok = false;
      result.log.push('internal error: ' + (e && e.message ? e.message : e));
    }
    return result;
  }

  /* ------------------------------------------------------------------ */
  /* Sample decks                                                        */
  /* ------------------------------------------------------------------ */

  var samples = [
    {
      name: 'Squares and roots',
      cards: [
        'C     SQUARES AND SQUARE ROOTS',
        '      WRITE (6,10)',
        '   10 FORMAT (1H1,5X,1HN,6X,6HSQUARE,5X,4HROOT)',
        '      DO 20 I = 1, 5',
        '      X = FLOAT(I)',
        '      Y = SQRT(X)',
        '      ISQ = I*I',
        '      WRITE (6,30) I, ISQ, Y',
        '   20 CONTINUE',
        '   30 FORMAT (1X,I6,I12,F9.4)',
        '      STOP',
        '      END'
      ]
    },
    {
      name: "Heron's formula",
      cards: [
        'C     AREA OF A TRIANGLE BY HERONS FORMULA',
        '      READ (5,10) IA, IB, IC',
        '   10 FORMAT (3I5)',
        '      S = FLOAT(IA+IB+IC)/2.0',
        '      AREA = SQRT(S*(S-FLOAT(IA))*(S-FLOAT(IB))*(S-FLOAT(IC)))',
        '      WRITE (6,20) IA, IB, IC, AREA',
        '   20 FORMAT (1H0,3HA =,I5,5H  B =,I5,5H  C =,I5,8H  AREA =,F10.2)',
        '      STOP',
        '      END',
        '    3    4    5'
      ]
    },
    {
      name: 'Largest of N values',
      cards: [
        'C     LARGEST VALUE IN A SET OF NUMBERS',
        '      DIMENSION A(100)',
        '      READ (5,100) N',
        '  100 FORMAT (I5)',
        '      DO 5 I = 1, N',
        '      READ (5,101) A(I)',
        '    5 CONTINUE',
        '  101 FORMAT (F10.2)',
        '      BIGA = A(1)',
        '      DO 20 I = 2, N',
        '      IF (BIGA - A(I)) 10, 20, 20',
        '   10 BIGA = A(I)',
        '   20 CONTINUE',
        '      WRITE (6,102) N, BIGA',
        "  102 FORMAT (1H ,10HLARGEST OF,I4,8H VALUES:,F10.2)",
        '      STOP',
        '      END',
        '    5',
        '3.5',
        '-2.0',
        '17.25',
        '9.0',
        '17.0'
      ]
    },
    {
      name: 'Punch the multiples of 3 below 20',
      cards: [
        'C     PUNCH THE MULTIPLES OF 3 BELOW 20, ONE PER CARD',
        '      DO 10 N = 0, 19',
        '      IF (MOD(N,3)) 10, 5, 10',
        '    5 PUNCH 20, N',
        '   10 CONTINUE',
        '   20 FORMAT (I5)',
        '      STOP',
        '      END'
      ]
    },
    {
      name: 'Sieve generator (after Xenakis)',
      cards: [
        'C     SIEVE GENERATOR, AFTER XENAKIS',
        'C     A RESIDUAL CLASS M(S) IS EVERY INTEGER X WITH X-S DIVISIBLE BY M.',
        'C     DATA CARD 1 (3I5): MODE, N, LIMIT',
        'C        MODE 1 = UNION OF THE N CLASSES',
        'C        MODE 2 = INTERSECTION OF THE N CLASSES',
        'C        MODE 3 = COMPLEMENT OF THE UNION',
        'C        N IS 1 TO 10. THE SIEVE IS TESTED ON 0 TO LIMIT-1.',
        'C     DATA CARDS 2 TO N+1 (2I5): M, S',
        'C     EACH MEMBER IS PRINTED WITH ITS INTERVAL FROM THE LAST ONE,',
        'C     AND PUNCHED, ONE PER CARD, FOR USE AS DATA ELSEWHERE.',
        '      DIMENSION IM(10), IS(10)',
        '      READ (5,10) MODE, N, LIMIT',
        '   10 FORMAT (3I5)',
        '      DO 20 K = 1, N',
        '      READ (5,11) IM(K), IS(K)',
        '   20 CONTINUE',
        '   11 FORMAT (2I5)',
        '      WRITE (6,30) MODE, N, LIMIT',
        "   30 FORMAT (1H1,'SIEVE  MODE =',I2,'  N =',I3,'  LIMIT =',I6)",
        '      WRITE (6,31)',
        "   31 FORMAT (1H0,5X,'K',3X,'MEMBER',3X,'INTERVAL')",
        '      NM = 0',
        '      LAST = 0',
        '      DO 60 J = 1, LIMIT',
        '      NV = J - 1',
        '      NH = 0',
        '      DO 40 K = 1, N',
        '      IF (MOD(MOD(NV-IS(K),IM(K))+IM(K),IM(K))) 40, 35, 40',
        '   35 NH = NH + 1',
        '   40 CONTINUE',
        '      MEMB = 0',
        '      IF (MODE .EQ. 1 .AND. NH .GT. 0) MEMB = 1',
        '      IF (MODE .EQ. 2 .AND. NH .EQ. N) MEMB = 1',
        '      IF (MODE .EQ. 3 .AND. NH .EQ. 0) MEMB = 1',
        '      IF (MEMB .EQ. 0) GO TO 60',
        '      NM = NM + 1',
        '      ITV = NV - LAST',
        '      LAST = NV',
        '      PUNCH 34, NV',
        '      IF (NM .EQ. 1) GO TO 50',
        '      WRITE (6,32) NM, NV, ITV',
        '      GO TO 60',
        '   50 WRITE (6,33) NM, NV',
        '   60 CONTINUE',
        '      WRITE (6,36) NM',
        '      STOP',
        '   32 FORMAT (1X,I6,I9,I11)',
        '   33 FORMAT (1X,I6,I9)',
        '   34 FORMAT (I5)',
        "   36 FORMAT (1H0,I5,' MEMBERS')",
        '      END',
        '    1    2   20',
        '    5    2',
        '    5    3'
      ]
    }
  ];

  return {
    encodeCard: Hollerith.encodeCard,
    decodeCard: Hollerith.decodeCard,
    punches: Hollerith.punches,
    run: run,
    samples: samples
  };
})();
