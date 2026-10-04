/* Icons: the desktop's pictures that are drawn in the page, as vector art in the room's
   manner, flat colour with a soft light across it, in the room's palette.

   Every icon is a symbol in one hidden sprite, made once when the page loads, on a 48-unit
   square; an icon on screen is an <svg data-icon="name"> holding a <use> of its symbol, so
   each shape is in the page once however many icons show it. Documents share one page, a
   sheet with its corner turned down, with a picture of what they hold on it; applications
   share one tile, a rounded square in a colour of their own; every folder is the same
   folder. The menu bar's glyph is the sieve 5@2 | 5@3 as a row of points.

   Icons.fill(scope)          gives every svg[data-icon] in scope its symbol
   Icons.make(name)           a new icon, an <svg class="ico"> */

var Icons = (function () {
  'use strict';
  var doc = document, NS = 'http://www.w3.org/2000/svg';
  var C = {
    ink: '#1e1d1b', soft: '#6b665e', line: '#b4ab9b', paper: '#fbf9f3', blue: '#2b4560', sky: '#a9c1d3',
    accent: '#b5462b', ochre: '#c99a2e', sage: '#7d8a78', slate: '#49555a', teak: '#9a6136', cream: '#efe6d2'
  };

  // the shared gradients: paper, its turned corner, the folder, and each application's tile
  function lin(id, stops, x2, y2) {
    return '<linearGradient id="' + id + '" x1="0" y1="0" x2="' + (x2 || 0) + '" y2="' + (y2 === undefined ? 1 : y2) + '">' +
      stops.map(function (s) { return '<stop offset="' + s[0] + '" stop-color="' + s[1] + '"/>'; }).join('') + '</linearGradient>';
  }
  var DEFS = [
    lin('ig-page', [[0, '#fffdf8'], [1, '#ebe4d5']]),
    lin('ig-fold', [[0, '#d6ccb9'], [1, '#f4efe4']], 1, 1),
    lin('ig-fback', [[0, '#bf8a2a'], [1, '#a77623']]),
    lin('ig-ffront', [[0, '#e9bb57'], [1, '#d09d36']]),
    lin('ig-disk', [[0, '#f1efea'], [0.55, '#cfccc4'], [1, '#a9a59c']]),
    lin('ig-steel', [[0, '#c9c6bf'], [0.5, '#f0eee9'], [1, '#a8a49b']], 1, 0),
    lin('ig-t-blue', [[0, '#41658a'], [1, '#22384f']]),
    lin('ig-t-teak', [[0, '#b77847'], [1, '#7c4826']]),
    lin('ig-t-sage', [[0, '#93a08d'], [1, '#5f6c5b']]),
    lin('ig-t-slate', [[0, '#5d6a70'], [1, '#2e373b']]),
    lin('ig-t-ivory', [[0, '#fbf6ea'], [1, '#e0d6c2']]),
    lin('ig-warn', [[0, '#e3b54b'], [1, '#c48f23']])
  ].join('');

  // a sheet of paper with its top right corner turned down, a hairline round it
  var PAGE = '<path d="M12 3.5h17.5l9 9V42a2.5 2.5 0 0 1-2.5 2.5H12A2.5 2.5 0 0 1 9.5 42V6A2.5 2.5 0 0 1 12 3.5z" fill="url(#ig-page)" stroke="#a79e8e" stroke-width=".8"/>' +
    '<path d="M29.5 3.5V10a2.5 2.5 0 0 0 2.5 2.5h6.5z" fill="url(#ig-fold)" stroke="#a79e8e" stroke-width=".8" stroke-linejoin="round"/>';
  // an application's tile: a rounded square, lit along its top edge
  function tile(g) {
    return '<rect x="4.5" y="4.5" width="39" height="39" rx="10" fill="url(#ig-t-' + g + ')"/>' +
      '<rect x="5" y="5" width="38" height="38" rx="9.5" fill="none" stroke="#fff" stroke-opacity=".28" stroke-width="1"/>' +
      '<path d="M8 14.5a9.5 9.5 0 0 1 9.5-9.5h13A9.5 9.5 0 0 1 40 14.5" fill="none" stroke="#fff" stroke-opacity=".22" stroke-width="1.2"/>';
  }
  // lines of text: [x, y, length] each, as rounded strokes
  function lines(list, col, w) {
    return '<path d="' + list.map(function (l) { return 'M' + l[0] + ' ' + l[1] + 'h' + l[2]; }).join('') +
      '" stroke="' + (col || C.line) + '" stroke-width="' + (w || 1.6) + '" stroke-linecap="round" fill="none"/>';
  }
  // a punched card: cream, its top left corner cut, and its text punched in it as the
  // keypunch punches it (Fortran.punches): one column every 2 units, the 12 rows from 12, 11
  // and 0 down to 9, each hole a short slot; a blue tick over each column for its printing
  var ROWS = [12, 11, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9];
  function card(x, y, w, h, text) {
    var s = '<path d="M' + (x + 3) + ' ' + y + 'H' + (x + w) + 'V' + (y + h) + 'H' + x + 'V' + (y + 3) + 'z" fill="' + C.cream + '" stroke="#9b8f78" stroke-width=".7" stroke-linejoin="round"/>';
    if (!text) return s;
    var rh = (h - 4.4) / 12, d = '', p = '';
    text.split('').forEach(function (ch, k) {
      var cx = x + 3 + k * 2;
      if (ch !== ' ') p += 'M' + cx + ' ' + (y + 1.6) + 'h.9';
      Fortran.punches(ch).forEach(function (r) { var yy = y + 3.4 + ROWS.indexOf(r) * rh; d += 'M' + cx + ' ' + yy.toFixed(2) + 'v' + Math.max(0.8, rh * 0.8).toFixed(2); });
    });
    return s + '<path d="' + p + '" stroke="#7f97b0" stroke-width=".8" fill="none"/><path d="' + d + '" stroke="' + C.ink + '" stroke-width=".9" fill="none"/>';
  }

  var ICONS = {
    // the hard disk: a flat aluminium box seen a little from above, a slot and a lamp
    disk: '<path d="M8 17l4-6h24l4 6z" fill="#e8e5de" stroke="#8e8a81" stroke-width=".8" stroke-linejoin="round"/>' +
      '<rect x="6" y="17" width="36" height="16" rx="3" fill="url(#ig-disk)" stroke="#8e8a81" stroke-width=".8"/>' +
      '<rect x="10" y="23.5" width="16" height="2.6" rx="1.3" fill="#3a3935"/><rect x="10.6" y="23.9" width="14.8" height=".6" rx=".3" fill="#fff" fill-opacity=".25"/>' +
      '<circle cx="35.5" cy="25" r="2.6" fill="' + C.ochre + '" fill-opacity=".25"/><circle cx="35.5" cy="25" r="1.6" fill="' + C.ochre + '"/>' +
      '<path d="M8 21h5M8 28.5h22" stroke="#8e8a81" stroke-width=".5" stroke-opacity=".6"/>' +
      '<path d="M7 31.5h34" stroke="#fff" stroke-opacity=".5" stroke-width=".8"/>',
    readme: PAGE + '<circle cx="23.5" cy="21" r="7.5" fill="' + C.blue + '"/><circle cx="23.5" cy="17.4" r="1.3" fill="#fff"/>' +
      '<path d="M23.5 20.5v5" stroke="#fff" stroke-width="2.2" stroke-linecap="round"/>' + lines([[14, 33, 19], [14, 37, 14]]),
    document: PAGE + lines([[14, 15, 12], [14, 19, 19], [14, 23, 17], [14, 27, 19], [14, 31, 10], [14, 35, 18], [14, 39, 13]]),
    // a table of numbers in columns
    textdoc: PAGE + lines([[14, 15, 19]], C.soft, 1.4) + lines([[14, 20, 3], [21, 20, 4], [29, 20, 4], [14, 24, 3], [21, 24, 4], [29, 24, 4], [14, 28, 3], [21, 28, 4], [29, 28, 4], [14, 32, 3], [21, 32, 4], [29, 32, 4], [14, 36, 3], [21, 36, 4], [29, 36, 4]]),
    folder: '<path d="M5 12a2.5 2.5 0 0 1 2.5-2.5h10l3.5 4h19.5A2.5 2.5 0 0 1 43 16v22a2.5 2.5 0 0 1-2.5 2.5h-33A2.5 2.5 0 0 1 5 38z" fill="url(#ig-fback)"/>' +
      '<path d="M9 13.5h28a1.5 1.5 0 0 1 1.5 1.5v6H7.5v-6A1.5 1.5 0 0 1 9 13.5z" fill="#fbf8ef" stroke="#c9bfa9" stroke-width=".5"/>' +
      '<path d="M5 18.5a2.5 2.5 0 0 1 2.5-2.5h33a2.5 2.5 0 0 1 2.5 2.5V38a2.5 2.5 0 0 1-2.5 2.5h-33A2.5 2.5 0 0 1 5 38z" fill="url(#ig-ffront)"/>' +
      '<path d="M6 17.5h36" stroke="#fff" stroke-opacity=".45" stroke-width="1"/>',
    // the Editor: a sheet of ruled text on the blue tile, a pencil across it
    editor: tile('blue') + '<rect x="12" y="11" width="20" height="26" rx="1.5" fill="' + C.paper + '"/>' + lines([[15, 16, 12], [15, 20, 14], [15, 24, 9], [15, 28, 12]], '#9fb2c4', 1.4) +
      '<g transform="rotate(45 30 26)"><rect x="27.5" y="10" width="5" height="22" fill="' + C.ochre + '"/><rect x="27.5" y="10" width="1.6" height="22" fill="#fff" fill-opacity=".3"/>' +
      '<rect x="27.5" y="7" width="5" height="3.4" rx="1" fill="' + C.accent + '"/><path d="M27.5 32h5l-2.5 6z" fill="#ead9b8"/><path d="M29.2 36l1.6 0-.8 2z" fill="' + C.ink + '"/></g>',
    // the Player: a reel-to-reel machine's two reels on the teak tile, the tape between
    player: tile('teak') + [16, 32].map(function (x) {
      return '<circle cx="' + x + '" cy="20" r="7.5" fill="' + C.cream + '"/><circle cx="' + x + '" cy="20" r="4.6" fill="#3b2a1d"/><circle cx="' + x + '" cy="20" r="1.4" fill="' + C.cream + '"/>';
    }).join('') + '<path d="M9.5 23.5L13 35h22l3.5-11.5" fill="none" stroke="#3b2a1d" stroke-width="1.2"/>' +
      '<rect x="12" y="33" width="24" height="5" rx="1.5" fill="#d8cdb4"/><circle cx="24" cy="35.5" r="1.2" fill="' + C.accent + '"/>',
    // Eighty Columns: a punched card on the sage tile, FORTRAN printed along it
    course: tile('sage') + card(9, 13, 30, 22, 'FORTRAN 80'),
    // the Calculator: a lit display and keys on the slate tile
    calc: tile('slate') + '<rect x="11" y="10" width="26" height="8" rx="1.5" fill="#e9dcae"/><path d="M27 14h7" stroke="#5a4c22" stroke-width="2" stroke-linecap="round"/>' +
      [0, 1, 2, 3].map(function (c) { return [0, 1, 2].map(function (r) { var last = c === 3 && r === 2; return '<circle cx="' + (14 + c * 6.7) + '" cy="' + (23.5 + r * 6) + '" r="2.3" fill="' + (last ? C.accent : c === 3 ? C.ochre : C.cream) + '"/>'; }).join(''); }).join(''),
    // Crible: 24 numbers as points, the members of the sieve 3@0 | 4@1 in terracotta
    crible: tile('ivory') + (function () {
      var s = '';
      for (var r = 0; r < 4; r++) for (var c = 0; c < 6; c++) {
        var n = r * 6 + c, on = n % 3 === 0 || n % 4 === 1;
        s += '<circle cx="' + (11.5 + c * 5) + '" cy="' + (16 + r * 5.4) + '" r="' + (on ? 2 : 1) + '" fill="' + (on ? C.accent : C.soft) + '"/>';
      }
      return s;
    })(),
    // Tzara's recipe: a top hat on the page, words cut apart below it
    hat: PAGE + '<path d="M17 10.5h12l-.8 12h-10.4z" fill="' + C.ink + '"/><rect x="17.3" y="18.5" width="11.4" height="2.4" fill="' + C.accent + '"/>' +
      '<path d="M12.5 23.5c3-1.6 18-1.6 21 0" fill="none" stroke="' + C.ink + '" stroke-width="2.2" stroke-linecap="round"/>' +
      '<g fill="#fff" stroke="#a79e8e" stroke-width=".6"><rect x="13" y="29" width="7" height="3.4"/><rect x="22" y="28" width="9" height="3.4" transform="rotate(-6 26 30)"/><rect x="15" y="35" width="10" height="3.4" transform="rotate(4 20 37)"/><rect x="27" y="35" width="6" height="3.4"/></g>',
    // a FORTRAN program: a little card at its head, then statements indented to column 7
    source: PAGE + card(12.5, 6.5, 15, 8) + lines([[14, 18, 2], [18, 18, 14], [18, 22, 10], [18, 26, 15], [14, 30, 2], [18, 30, 8], [18, 34, 12], [18, 38, 6]], '#8e9aa6'),
    // a music program: a staff with one terracotta note on it
    music: PAGE + lines([[13.5, 13, 21], [13.5, 16, 21], [13.5, 19, 21], [13.5, 22, 21], [13.5, 25, 21]], '#a99f8e', 0.9) +
      '<ellipse cx="22" cy="23.5" rx="3" ry="2.2" transform="rotate(-20 22 23.5)" fill="' + C.accent + '"/><path d="M24.6 22.8V12.5l4 2.4" fill="none" stroke="' + C.ink + '" stroke-width="1.2"/>' + lines([[14, 33, 18], [14, 37, 12]]),
    // a picture: a framed landscape, the sun in ochre
    picture: PAGE + '<rect x="13.5" y="14" width="21" height="17" fill="' + C.sky + '"/><circle cx="29" cy="19" r="2.6" fill="' + C.ochre + '"/>' +
      '<path d="M13.5 31v-5l5-4.5 4.5 3.5 4-3 7.5 5.5V31z" fill="' + C.sage + '"/><rect x="13.5" y="14" width="21" height="17" fill="none" stroke="#857b6a" stroke-width=".8"/>' + lines([[14, 36, 16]]),
    // the printout: two panels of fan-fold paper, sprocket holes down each side, green bars
    printout: [[5, 5], [9, 23]].map(function (o) {
      var x = o[0], y = o[1];
      return '<rect x="' + x + '" y="' + y + '" width="34" height="18" fill="#fffdf8" stroke="#a79e8e" stroke-width=".8"/>' +
        '<rect x="' + (x + 5) + '" y="' + (y + 3) + '" width="24" height="4" fill="#dbe7d2"/><rect x="' + (x + 5) + '" y="' + (y + 11) + '" width="24" height="4" fill="#dbe7d2"/>' +
        [0, 1, 2, 3].map(function (k) { return '<circle cx="' + (x + 2.4) + '" cy="' + (y + 3 + k * 4) + '" r=".9" fill="#a79e8e"/><circle cx="' + (x + 31.6) + '" cy="' + (y + 3 + k * 4) + '" r=".9" fill="#a79e8e"/>'; }).join('') +
        lines([[x + 7, y + 9, 14], [x + 7, y + 5, 9]], C.soft, 1.1);
    }).join(''),
    // the job log: prompts and lines, one terracotta mark
    log: PAGE + '<path d="M14 14l2.5 2-2.5 2M14 22l2.5 2-2.5 2M14 30l2.5 2-2.5 2" fill="none" stroke="' + C.soft + '" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/>' +
      lines([[20, 16, 12], [20, 24, 8], [20, 32, 10]]) + '<circle cx="31" cy="38" r="3.6" fill="' + C.accent + '"/><path d="M31 36v2.2" stroke="#fff" stroke-width="1.3" stroke-linecap="round"/><circle cx="31" cy="40" r=".7" fill="#fff"/>',
    // the listing: numbered lines
    listing: PAGE + lines([[13.5, 14, 2], [13.5, 18, 2], [13.5, 22, 2], [13.5, 26, 2], [13.5, 30, 2], [13.5, 34, 2], [13.5, 38, 2]], C.soft, 1.4) +
      lines([[18.5, 14, 14], [18.5, 18, 9], [21, 22, 12], [21, 26, 7], [18.5, 30, 11], [18.5, 34, 15], [18.5, 38, 8]]),
    // the program's output: a short stack of records
    punchfile: card(4, 8, 30, 18) + card(9, 14, 30, 18) + card(14, 20, 30, 18, '  7  12  19'),
    // the Trash: a wire basket, tapered; full, papers crumpled over its rim
    trash: basket(false), 'trash-full': basket(true),
    // the alert: an ochre triangle, rounded, with a mark
    note: '<path d="M24 6.5c1.1 0 2.1.6 2.6 1.6l15.5 28.4c1 1.9-.3 4.2-2.6 4.2H8.5c-2.3 0-3.6-2.3-2.6-4.2L21.4 8.1c.5-1 1.5-1.6 2.6-1.6z" fill="url(#ig-warn)"/>' +
      '<path d="M24 17v11" stroke="' + C.ink + '" stroke-width="3.2" stroke-linecap="round"/><circle cx="24" cy="34" r="2" fill="' + C.ink + '"/>'
  };
  function basket(full) {
    var s = '';
    if (full) s += '<g fill="#fbf9f3" stroke="#a79e8e" stroke-width=".7"><path d="M14 13c1-4 6-5 8-2 3-2 6 0 5 3 2 2 0 5-3 4-2 2-6 1-7-1-3 0-4-2-3-4z"/><path d="M25 11c2-3 7-2 8 1 3 1 2 5-1 5-2 2-6 1-6-1-2-1-2-4-1-5z"/></g>';
    s += '<path d="M10 15.5h28l-3 27H13z" fill="url(#ig-steel)" stroke="#7f7b72" stroke-width=".8" stroke-linejoin="round"/>';
    s += '<path d="M15.5 16l1.6 26M21 16l.8 26M27 16l-.8 26M32.5 16l-1.6 26" stroke="#8a867d" stroke-width=".8"/>';
    s += '<path d="M11.2 26h25.6M12.2 35h23.6" stroke="#8a867d" stroke-width=".7"/>';
    return s + '<rect x="9" y="13.5" width="30" height="3" rx="1.5" fill="#d9d6cf" stroke="#7f7b72" stroke-width=".8"/>';
  }
  // the menu glyph, on a 20 by 14 square: the sieve 5@2 | 5@3, fifteen points in three rows
  var GLYPH = (function () {
    var s = '';
    for (var r = 0; r < 3; r++) for (var c = 0; c < 5; c++) {
      var n = r * 5 + c, on = n % 5 === 2 || n % 5 === 3;
      s += '<circle cx="' + (2.5 + c * 3.75) + '" cy="' + (2.6 + r * 4.4) + '" r="' + (on ? 1.6 : 0.8) + '" fill="' + (on ? C.accent : 'currentColor') + '"/>';
    }
    return s;
  })();

  var sprite = doc.createElementNS(NS, 'svg');
  sprite.setAttribute('aria-hidden', 'true');
  sprite.setAttribute('style', 'position:absolute;width:0;height:0;overflow:hidden');
  sprite.innerHTML = '<defs>' + DEFS + '</defs>' + Object.keys(ICONS).map(function (k) {
    return '<symbol id="ic-' + k + '" viewBox="0 0 48 48">' + ICONS[k] + '</symbol>';
  }).join('') + '<symbol id="ic-glyph" viewBox="0 0 20 14">' + GLYPH + '</symbol>';
  doc.body.insertBefore(sprite, doc.body.firstChild);

  function set(svg, name) {
    if (!ICONS[name] && name !== 'glyph') name = 'document';
    svg.setAttribute('data-icon', name);
    svg.setAttribute('viewBox', name === 'glyph' ? '0 0 20 14' : '0 0 48 48');
    svg.setAttribute('focusable', 'false');
    svg.innerHTML = '<use href="#ic-' + name + '"/>';
  }
  function make(name) {
    var s = doc.createElementNS(NS, 'svg');
    s.setAttribute('class', 'ico'); s.setAttribute('aria-hidden', 'true');
    set(s, name);
    return s;
  }
  function fill(scope) { Array.prototype.forEach.call((scope || doc).querySelectorAll('svg[data-icon]'), function (s) { set(s, s.getAttribute('data-icon')); }); }
  fill();
  return { make: make, set: set, fill: fill };
})();
