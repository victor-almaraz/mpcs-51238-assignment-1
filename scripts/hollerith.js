/* Hollerith card codes (IBM 029) and card encode/decode.
   Classic script: defines the global `Hollerith`. No DOM. */
var Hollerith = (function () {
  'use strict';

  // Card rows, top to bottom.
  var ROWS = [12, 11, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9];

  var toChar = {};   // "12-8-3" -> "."
  var toRows = {};   // "." -> [12, 8, 3]

  // Rows are stored in the table's notation (12-8-3), which punches() returns;
  // the decode key lists them top to bottom so it does not depend on that order.
  function key(rows) {
    return ROWS.filter(function (r) { return rows.indexOf(r) !== -1; }).join('-');
  }

  function define(ch, rows) {
    toRows[ch] = rows;
    toChar[key(rows)] = ch;
  }

  define(' ', []);
  var d;
  for (d = 0; d <= 9; d++) define(String(d), [d]);
  for (d = 1; d <= 9; d++) {
    define(String.fromCharCode(64 + d), [12, d]);        // A-I
    define(String.fromCharCode(73 + d), [11, d]);        // J-R
  }
  for (d = 2; d <= 9; d++) define(String.fromCharCode(81 + d), [0, d]);  // S-Z

  var symbols = {
    '&': [12], '-': [11], '/': [0, 1],
    '.': [12, 8, 3], '$': [11, 8, 3], ',': [0, 8, 3],
    '(': [12, 8, 5], '*': [11, 8, 4], '%': [0, 8, 4],
    '+': [12, 8, 6], ')': [11, 8, 5], '_': [0, 8, 5],
    '<': [12, 8, 4], ';': [11, 8, 6], '>': [0, 8, 6],
    ':': [8, 2], '=': [8, 6], '?': [0, 8, 7],
    '#': [8, 3], "'": [8, 5], '"': [8, 7],
    '@': [8, 4], '¢': [12, 8, 2], '!': [11, 8, 2],
    '|': [12, 8, 7], '¬': [11, 8, 7]
  };
  for (var ch in symbols) define(ch, symbols[ch]);

  function upper(ch) {
    var u = ch.toUpperCase();
    return u.length === 1 ? u : ch;
  }

  // "A" -> [12, 1]; " " -> []; unknown -> []
  function punches(ch) {
    ch = upper(String(ch).charAt(0));
    return toRows.hasOwnProperty(ch) ? toRows[ch].slice() : [];
  }

  // string -> array of 80 column masks (each a Set of punched rows)
  function encodeCard(text) {
    text = String(text == null ? '' : text);
    var masks = [];
    for (var c = 0; c < 80; c++) {
      masks.push(new Set(c < text.length ? punches(text.charAt(c)) : []));
    }
    return masks;
  }

  // array of 80 masks (Sets or arrays) -> 80-character string.
  // A pattern with no character in the table decodes as "?".
  function decodeCard(masks) {
    var out = '';
    for (var c = 0; c < 80; c++) {
      var mask = masks && masks[c] ? Array.from(masks[c]) : [];
      var k = key(mask);
      out += toChar.hasOwnProperty(k) ? toChar[k] : '?';
    }
    return out;
  }

  return {
    punches: punches,
    encodeCard: encodeCard,
    decodeCard: decodeCard
  };
})();
