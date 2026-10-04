/* Pixels: everything on screen that is drawn rather than set in type.

   The screen has eight colours, those whose R, G and B are each 0 or 255, and one screen
   pixel is 2 CSS pixels. Every tone is a hatch: each channel of a colour is compared with
   the same 8x8 threshold matrix, and the matrix is built the way an engraver builds a tone,
   so as a tone darkens the ink goes down in this order:
     1 a 45-degree line every 8 pixels      4 then horizontals
     2 a second set between, every 4         5 then verticals
     3 the crossing 135-degree lines         6 and at last the gaps fill in, to solid
   A grey hatches in black; a colour hatches each channel apart, so lilac is blue lines
   on white. TONES gives the seven steps of that scale (paper to solid), which code the
   difficulty of the course's sheets.

   Px.drawIcon(canvas)        a 32x32 icon (or the 16x12 menu glyph) by its data-icon name
   --tone-0 to --tone-6       the seven steps of the scale, as CSS url() tiles
   The documents' pictures (the plates, the miscellanea's drawings and the large numerals)
   were drawn through the same matrix once and are kept as PNGs in assets/pics/, so every
   browser shows the same pixels; only the icons, the tiles and the pictures that change
   (the piano roll, the calculator's card) are drawn in the page. */

var Px = (function () {
  'use strict';
  var doc = document, root = doc.documentElement;
  function clamp(v, a, b) { return v < a ? a : v > b ? b : v; }

  /* ---------------- the hatch matrix ---------------- */
  // Bayer order spreads the pixels within one step, so a part-drawn line breaks evenly.
  var BAYER = [[0]];
  while (BAYER.length < 8) {
    var n0 = BAYER.length, next = [];
    for (var y0 = 0; y0 < 2 * n0; y0++) {
      next.push([]);
      for (var x0 = 0; x0 < 2 * n0; x0++) next[y0].push(4 * BAYER[y0 % n0][x0 % n0] + [0, 2, 3, 1][(y0 >= n0 ? 2 : 0) + (x0 >= n0 ? 1 : 0)]);
    }
    BAYER = next;
  }
  var STEPS = [
    function (x, y) { return (x + y) % 8 === 0; },          // 45 degrees, pitch 8
    function (x, y) { return (x + y) % 8 === 4; },          // 45 degrees, pitch 4
    function (x, y) { return (x - y + 8) % 4 === 0; },      // 135 degrees: cross-hatch
    function (x, y) { return y % 4 === 0; },                // horizontals
    function (x, y) { return x % 4 === 0; }                 // verticals
  ];
  function stepOf(x, y) { for (var s = 0; s < STEPS.length; s++) if (STEPS[s](x, y)) return s; return STEPS.length; }
  var order = [];
  for (var yy = 0; yy < 8; yy++) for (var xx = 0; xx < 8; xx++) order.push({ x: xx, y: yy, s: stepOf(xx, yy), b: BAYER[yy][xx] });
  order.sort(function (a, b) { return a.s - b.s || a.b - b.b; });
  // TH[y][x] is the darkness at which the pixel takes ink: the first pixel inked has the
  // highest threshold. A channel is on (lit) where its value exceeds the threshold.
  // the seven steps: paper, then each step of STEPS complete, then solid
  var counts = [0];
  STEPS.forEach(function (f, s) { counts.push(order.filter(function (p) { return p.s <= s; }).length); });
  counts.push(64);
  var TONES = counts.map(function (c) { return 1 - c / 64; });
  // An engraver never draws part of a line, so every pixel of a step shares one threshold,
  // halfway between the tones on either side of it: a tone always lands on a whole step.
  var TH = [[], [], [], [], [], [], [], []];
  order.forEach(function (p) { TH[p.y][p.x] = (TONES[p.s] + TONES[p.s + 1]) / 2; });

  function th(x, y) { return TH[y & 7][x & 7]; }
  function bit(v, x, y) { return v > th(x, y); }   // true is lit (white, for a grey)
  function rgbBits(c, x, y) { var t = th(x, y); return [c[0] > t ? 255 : 0, c[1] > t ? 255 : 0, c[2] > t ? 255 : 0]; }
  function mix3(a, b, f) { return [a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f, a[2] + (b[2] - a[2]) * f]; }
  function rgbOf(v) { return typeof v === 'number' ? [v, v, v] : v; }

  // the colour design: lilac scroll tracks, green bars
  var TRACK = [0.86, 0.86, 1], GREENBAR = [0.86, 1, 0.86];

  /* ---------------- tiles for CSS, drawn at screen resolution and shown at 2x ---------------- */
  function canvasURL(w, h, fn) {
    var c = doc.createElement('canvas'); c.width = w; c.height = h;
    var ctx = c.getContext('2d'), img = ctx.createImageData(w, h), d = img.data;
    for (var y = 0; y < h; y++) for (var x = 0; x < w; x++) {
      var o = (y * w + x) * 4, p = fn(x, y);
      if (!p) continue;
      d[o] = p[0]; d[o + 1] = p[1]; d[o + 2] = p[2]; d[o + 3] = 255;
    }
    ctx.putImageData(img, 0, 0);
    return 'url(' + c.toDataURL() + ')';
  }
  function tile(v) { var c = rgbOf(v); return canvasURL(8, 8, function (x, y) { return rgbBits(c, x, y); }); }
  function toneTile(k) { return tile(TONES[clamp(k, 0, 6)]); }
  // pixel art from strings: '#' black, 'o' white, anything else transparent
  function art(rows, ink) {
    return canvasURL(rows[0].length, rows.length, function (x, y) {
      var c = rows[y].charAt(x);
      return c === '#' ? (ink || [0, 0, 0]) : c === 'o' ? [255, 255, 255] : null;
    });
  }
  var HOLE = ['..........', '...####...', '..#oooo#..', '.#oooooo#.', '.#oooooo#.', '.#oooooo#.', '.#oooooo#.', '..#oooo#..', '...####...', '..........'];
  var RADIO = ['..####..', '.#oooo#.', '#oooooo#', '#oooooo#', '#oooooo#', '#oooooo#', '.#oooo#.', '..####..'];
  var ARROW = ['..#..', '.###.', '#####', '.###.', '.###.'];
  var CHECK = ['......#', '.....#.', '#...#..', '.#.#...', '..#....'];
  function rot(rows, dir) {
    var n = rows.length, out = [];
    for (var y = 0; y < n; y++) {
      var s = '';
      for (var x = 0; x < n; x++) {
        var u = dir === 'up' ? [x, y] : dir === 'down' ? [x, n - 1 - y] : dir === 'left' ? [y, x] : [n - 1 - y, x];
        s += rows[u[1]].charAt(u[0]);
      }
      out.push(s);
    }
    return out;
  }
  function frameAt(x, y, a, b) { return (x === a || x === b) && y >= a && y <= b || (y === a || y === b) && x >= a && x <= b; }
  var css = {
    '--pat-50': tile(0.5),
    '--pat-track': tile(TRACK),
    '--pat-stripes': canvasURL(1, 2, function (x, y) { return y ? [255, 255, 255] : [0, 0, 0]; }),
    '--pat-holes': canvasURL(10, 10, function (x, y) { var c = HOLE[y].charAt(x); return c === '#' ? [0, 0, 0] : c === 'o' ? [255, 255, 255] : rgbBits(GREENBAR, x, y); }),
    '--grow': canvasURL(8, 8, function (x, y) { return frameAt(x, y, 0, 7) || frameAt(x, y, 1, 4) || frameAt(x, y, 3, 6) ? [0, 0, 0] : [255, 255, 255]; }),
    '--check': art(CHECK), '--check-on': art(CHECK, [255, 255, 255]),
    '--radio': art(RADIO),
    '--radio-on': art(RADIO.map(function (r, y) { return y > 1 && y < 6 ? r.slice(0, 2) + (y === 2 || y === 5 ? 'o##o' : '####') + r.slice(6) : r; })),
    '--radio-off': canvasURL(8, 8, function (x, y) { var c = RADIO[y].charAt(x); return c === '#' ? ((x + y) % 2 ? [255, 255, 255] : [0, 0, 0]) : c === 'o' ? [255, 255, 255] : null; })
  };
  ['up', 'down', 'left', 'right'].forEach(function (d) { css['--arrow-' + d] = art(rot(ARROW, d)); });
  for (var k = 0; k <= 6; k++) css['--tone-' + k] = toneTile(k);
  Object.keys(css).forEach(function (n) { root.style.setProperty(n, css[n]); });

  // the sieve 5@2 | 5@3, drawn by the menu glyph
  function SIEVE(n) { return n % 5 === 2 || n % 5 === 3; }

  /* ---------------- icons: 32x32 bitmaps with masks ---------------- */
  // After the classic Finder's rules: a one-pixel black outline round every silhouette,
  // interiors mostly white (selection inverts an icon, so heavy black or a half tone would
  // read the same either way), straight lines at 45 degrees or in 2:1 steps, and one family
  // of shapes. Documents share one page and applications one tilted page, each with a badge
  // drawn on graph paper below; every folder is the same folder, whatever it holds, as the
  // Finder drew them. Colour is an accent, one to an icon.
  // A cell is 0 transparent, 1 white, 2 black, or a palette colour [r, g, b];
  // { d: v } fills with a grey hatch, { c: [r, g, b] } with a colour hatch.
  var YEL = [255, 255, 0], RED = [255, 0, 0], BLU = [0, 0, 255], GRN = [0, 255, 0];
  var PALE = { c: [0.88, 0.88, 1] };            // the lightest blue hatch: a folder's fill
  function grid(w, h) { var g = []; for (var y = 0; y < h; y++) g.push(new Array(w).fill(0)); g.w = w; g.h = h; return g; }
  function fillOf(v, i, j) {
    if (typeof v === 'number' || Array.isArray(v)) return v;
    if (v.d !== undefined) return bit(v.d, i, j) ? 1 : 2;
    var p = rgbBits(v.c, i, j);
    return p[0] && p[1] && p[2] ? 1 : !p[0] && !p[1] && !p[2] ? 2 : p;
  }
  function R(g, x, y, w, h, v) { for (var j = y; j < y + h; j++) for (var i = x; i < x + w; i++) if (g[j] && i >= 0 && i < g.w) g[j][i] = fillOf(v, i, j); }
  function O(g, x, y, w, h, fill) { R(g, x, y, w, h, 2); R(g, x + 1, y + 1, w - 2, h - 2, fill || 1); }
  function P(g, x, y, v) { if (g[y] && x >= 0 && x < g.w) g[y][x] = v === undefined ? 2 : v; }
  function line(g, x0, y0, x1, y1, v) {
    var dx = Math.abs(x1 - x0), dy = Math.abs(y1 - y0), sx = x0 < x1 ? 1 : -1, sy = y0 < y1 ? 1 : -1, e = dx - dy;
    for (;;) { P(g, x0, y0, v); if (x0 === x1 && y0 === y1) break; var e2 = 2 * e; if (e2 > -dy) { e -= dy; x0 += sx; } if (e2 < dx) { e += dx; y0 += sy; } }
  }
  // a glyph drawn as text: # black, o white, r red, b blue, y yellow, g green, : pale hatch
  var INK = { '#': 2, o: 1, r: RED, b: BLU, y: YEL, g: GRN, ':': PALE };
  function stamp(g, x, y, rows) {
    rows.forEach(function (r, j) { for (var i = 0; i < r.length; i++) { var ch = r.charAt(i); if (INK[ch] !== undefined) P(g, x + i, y + j, fillOf(INK[ch], x + i, y + j)); } });
  }
  // broken lines of text on a 3-pixel pitch: each row is a list of [start, length] runs
  function text(g, x, y, rows) { rows.forEach(function (runs, j) { runs.forEach(function (r) { line(g, x + r[0], y + 3 * j, x + r[0] + r[1] - 1, y + 3 * j); }); }); }

  // the document page: 23 by 30, its top right corner folded down by 5 pixels
  function page(g) {
    var x0 = 5, y0 = 1, x1 = 27, y1 = 30, f = 5;
    for (var y = y0; y <= y1; y++) for (var x = x0; x <= x1; x++) {
      if (x - (x1 - f) > y - y0) continue;
      g[y][x] = (x === x0 || x === x1 || y === y0 || y === y1 || x - (x1 - f) === y - y0) ? 2 : 1;
    }
    line(g, x1 - f, y0, x1 - f, y0 + f); line(g, x1 - f, y0 + f, x1, y0 + f);
  }
  // the folder: a tab at the top left, a pale hatched body, and the lip of its front
  function folder(g) {
    O(g, 2, 5, 11, 4, PALE); O(g, 2, 8, 28, 20, PALE); R(g, 3, 8, 9, 1, PALE);
    line(g, 3, 11, 28, 11);
  }
  // the application: a page tilted to stand on its corner, as System 7 drew applications
  function diamond(g) {
    for (var y = 2; y <= 30; y++) for (var x = 2; x <= 30; x++) {
      var d = Math.abs(x - 16) + Math.abs(y - 16);
      if (d <= 14) g[y][x] = d === 14 ? 2 : 1;
    }
  }
  var GLYPH_INFO = ['.#####.', '#ooooo#', '#oo#oo#', '#ooooo#', '#o##oo#', '#oo#oo#', '#oo#oo#', '#o###o#', '.#####.'];
  var GLYPH_CARD = ['..#######', '.#o#oo#o#', '#oo#o#oo#', '#o#oo#oo#', '#########'];

  var ICONS = {
    // the hard disk: a flat box seen a little from above, its top face white
    disk: function (g) {
      for (var j = 0; j < 4; j++) { line(g, 6 - j, 10 + j, 29 - j, 10 + j, j === 0 ? 2 : 1); P(g, 6 - j, 10 + j); P(g, 29 - j, 10 + j); }
      O(g, 2, 13, 27, 10); line(g, 29, 10, 29, 19); line(g, 28, 22, 29, 21); line(g, 29, 19, 29, 21);
      for (var k = 1; k < 4; k++) P(g, 29 - k + 1, 10 + k);
      R(g, 5, 17, 9, 1, 2); R(g, 5, 19, 9, 1, 2); R(g, 23, 17, 3, 2, GRN); P(g, 22, 17); P(g, 22, 18); P(g, 26, 17); P(g, 26, 18); line(g, 22, 16, 26, 16); line(g, 22, 19, 26, 19);
    },
    readme: function (g) { page(g); stamp(g, 9, 5, GLYPH_INFO); text(g, 9, 18, [[[0, 14]], [[0, 9], [10, 4]], [[0, 12]], [[0, 6]]]); },
    document: function (g) { page(g); text(g, 9, 9, [[[0, 9]], [[0, 14]], [[0, 5], [6, 8]], [[0, 13]], [[0, 8], [9, 5]], [[0, 14]], [[0, 7]]]); },
    // a table of numbers in columns
    textdoc: function (g) { page(g); line(g, 9, 8, 22, 8); for (var j = 0; j < 6; j++) { var y = 11 + 3 * j; line(g, 9, y, 10, y); line(g, 13, y, 16, y); line(g, 19, y, 22, y); } },
    folder: folder,
    // the Editor: a pencil at 45 degrees across the tilted page, graphite at its point
    editor: function (g) {
      diamond(g);
      text(g, 8, 13, [[[2, 4]], [[0, 10]], [[2, 7]]]);
      for (var y = 0; y < 32; y++) for (var x = 0; x < 32; x++) {
        var s = x + y - 32, v = x - y;            // across the pencil, and along it
        if (Math.abs(s) > 2 || v < -9 || v > 21) continue;
        var tip = v < -5, room = tip ? Math.floor((v + 9) / 2) : 2;
        if (Math.abs(s) > room) continue;
        g[y][x] = Math.abs(s) === room || v === 21 || v === -5 ? 2 : tip ? (v < -7 ? 2 : 1) : v > 17 ? RED : YEL;
      }
    },
    // the Player: a speaker on the tilted page, three waves leaving it
    player: function (g) {
      diamond(g);
      O(g, 7, 13, 5, 7);
      for (var x = 11; x <= 16; x++) { var h = x - 11 + 3; for (var y = 16 - h; y <= 16 + h; y++) g[y][x] = (y === 16 - h || y === 16 + h || x === 16) ? 2 : YEL; }
      [3, 6, 9].forEach(function (r) { for (var k = -r + 1; k <= r - 1; k++) P(g, 17 + r - Math.abs(k), 16 + k, BLU); });
    },
    // Eighty Columns: a punched card on the tilted page, FORTRAN 80 punched along it, a column
    // every 2 pixels, each with its printing above it in blue
    course: function (g) {
      diamond(g);
      for (var y = 8; y <= 24; y++) for (var x = 4; x <= 28; x++) {
        if (x - 4 + y - 8 < 4) continue;
        g[y][x] = (x === 4 || x === 28 || y === 8 || y === 24 || x - 4 + y - 8 === 4) ? 2 : 1;
      }
      // one column every 2 pixels, a hole 1 by 1 in each of the 12 rows from row 11 down
      var ROW = [12, 11, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9];
      'FORTRAN 80'.split('').forEach(function (ch, k) {
        if (ch === ' ') return;
        P(g, 8 + 2 * k, 10, BLU);
        Fortran.punches(ch).forEach(function (r) { P(g, 8 + 2 * k, 11 + ROW.indexOf(r)); });
      });
    },
    // the Calculator: a desk calculator stood on the tilted page, its display lit green
    calc: function (g) {
      diamond(g);
      O(g, 9, 5, 15, 23); O(g, 11, 7, 11, 5, GRN);
      [15, 17, 19].forEach(function (x) { line(g, x, 9, x, 10); });
      for (var r = 0; r < 4; r++) for (var c = 0; c < 3; c++) R(g, 12 + 4 * c, 14 + 3 * r, 2, 2, 2);
    },
    // Crible: a strip of 24 numbers on the tilted page, the members of the sieve 3@0 | 4@1 in red
    crible: function (g) {
      diamond(g);
      O(g, 6, 9, 21, 15);
      for (var r = 0; r < 4; r++) for (var c = 0; c < 6; c++) {
        var n = r * 6 + c, x = 8 + 3 * c, y = 11 + 3 * r;
        if (n % 3 === 0 || n % 4 === 1) R(g, x, y, 2, 2, RED); else P(g, x, y);
      }
    },
    // Tzara's recipe: a top hat on the page, and below it words cut apart
    hat: function (g) {
      page(g);
      O(g, 12, 6, 9, 11); R(g, 13, 13, 7, 2, RED); O(g, 9, 16, 15, 3);
      text(g, 9, 22, [[[0, 4], [6, 3], [11, 3]], [[0, 2], [4, 5], [11, 3]], [[1, 3], [7, 6]]]);
    },
    source: function (g) {
      page(g);
      stamp(g, 8, 4, GLYPH_CARD);
      text(g, 9, 13, [[[0, 1], [3, 10]], [[5, 9]], [[5, 6]], [[0, 3], [5, 8]], [[5, 7]], [[5, 4]]]);
    },
    // a music program: a staff with one red note head
    music: function (g) {
      page(g);
      for (var k = 0; k < 5; k++) line(g, 8, 8 + 2 * k, 24, 8 + 2 * k);
      line(g, 18, 6, 18, 14); line(g, 19, 6, 21, 8); line(g, 19, 7, 20, 8);
      stamp(g, 14, 13, ['.###.', '#rrr#', '.###.']);
      text(g, 9, 22, [[[0, 12]], [[0, 8]]]);
    },
    // a picture: a framed landscape, its sky left white
    picture: function (g) {
      page(g); O(g, 8, 9, 17, 15);
      stamp(g, 18, 11, ['.yy.', 'yyyy', 'yyyy', '.yy.']);
      for (var x = 9; x <= 23; x++) {
        var top = x <= 14 ? 22 - (x - 9) * 1.4 : x <= 18 ? 15 + (x - 14) : 19 - (x - 18) * 0.6;
        top = Math.round(top);
        for (var y = top; y <= 22; y++) g[y][x] = y === top ? 2 : fillOf({ c: [0.6, 1, 0.6] }, x, y);
      }
    },
    // the printout: two panels of fan-fold paper, sprocket holes down both sides, a green bar on each
    printout: function (g) {
      [[3, 2, 23, 13], [6, 15, 23, 14]].forEach(function (p, n) {
        O(g, p[0], p[1], p[2], p[3]);
        for (var y = p[1] + 2; y < p[1] + p[3] - 1; y += 3) { P(g, p[0] + 2, y); P(g, p[0] + p[2] - 3, y); }
        R(g, p[0] + 4, p[1] + 3, p[2] - 8, 3, { c: [0.6, 1, 0.6] });
        line(g, p[0] + 5, p[1] + 8, p[0] + 14, p[1] + 8); line(g, p[0] + 5, p[1] + 10, p[0] + 11, p[1] + 10);
      });
      for (var x = 7; x < 26; x += 2) P(g, x, 15, 1);
    },
    // the job log: prompts and lines, one red mark
    log: function (g) {
      page(g);
      [9, 14, 19].forEach(function (y) { P(g, 9, y - 1); P(g, 10, y); P(g, 9, y + 1); line(g, 13, y, 13 + (y === 14 ? 6 : 9), y); });
      R(g, 20, 21, 2, 5, RED); R(g, 20, 27, 2, 2, RED);
    },
    // the listing: numbered lines
    listing: function (g) { page(g); for (var j = 0; j < 7; j++) { var y = 8 + 3 * j; P(g, 9, y); P(g, 10, y); line(g, 13, y, 13 + [10, 6, 9, 4, 8, 10, 5][j], y); } },
    // the program's output: a short stack of records, each a page of numbers
    punchfile: function (g) {
      [[3, 3], [6, 6], [9, 9]].forEach(function (o) { O(g, o[0], o[1], 19, 21); });
      for (var j = 0; j < 5; j++) { var y = 13 + 3 * j; line(g, 12, y, 14, y); line(g, 18, y, 23, y); }
    },
    // the Trash: the can seen straight on; full, its lid lifted on the papers inside
    trash: function (g, full) {
      var lift = full ? 3 : 0;
      if (full) { O(g, 9, 5, 7, 5); O(g, 15, 6, 8, 4); line(g, 11, 7, 14, 7); line(g, 17, 8, 21, 8); }
      R(g, 6, 6 - lift, 20, 3, 2); R(g, 7, 7 - lift, 18, 1, 1); O(g, 13, 3 - lift, 6, 4); R(g, 14, 5 - lift, 4, 1, 1);
      for (var y = 9; y <= 29; y++) { var a = 8 + Math.floor((y - 9) / 10), b = 23 - Math.floor((y - 9) / 10); for (var x = a; x <= b; x++) g[y][x] = (x === a || x === b || y === 29) ? 2 : 1; }
      line(g, 8, 9, 23, 9);
      [12, 16, 20].forEach(function (x) { line(g, x, 11, x, 27); });
    },
    // the alert: a yellow triangle, its sides in clean 2:1 steps, and a black mark
    note: function (g) {
      for (var y = 4; y <= 28; y++) { var half = Math.floor((y - 4) / 2); for (var x = 16 - half; x <= 16 + half; x++) g[y][x] = (x === 16 - half || x === 16 + half || y === 28) ? 2 : YEL; }
      R(g, 15, 11, 3, 10, 2); R(g, 15, 23, 3, 3, 2);
    },
    // the menu glyph: the sieve 5@2 | 5@3 as a little grid of points
    glyph: function (g) {
      O(g, 0, 0, 16, 12);
      for (var r = 0; r < 3; r++) for (var c = 0; c < 5; c++) {
        var nn = r * 5 + c, x = 2 + c * 3 - (c > 2 ? 1 : 0), y = 2 + r * 3 + 1;
        if (SIEVE(nn)) R(g, x, y, 2, 2, RED); else P(g, x, y);
      }
    }
  };
  function drawIcon(c) {
    var name = c.getAttribute('data-icon'), small = name === 'glyph';
    var g = small ? grid(16, 12) : grid(32, 32);
    ICONS[name.replace(/-full$/, '')](g, /-full$/.test(name));
    c.width = g.w; c.height = g.h;
    var ctx = c.getContext('2d'), img = ctx.createImageData(g.w, g.h), d = img.data;
    for (var y = 0; y < g.h; y++) for (var x = 0; x < g.w; x++) {
      var o = (y * g.w + x) * 4, v = g[y][x], p = Array.isArray(v) ? v : v === 1 ? [255, 255, 255] : [0, 0, 0];
      d[o] = p[0]; d[o + 1] = p[1]; d[o + 2] = p[2]; d[o + 3] = v ? 255 : 0;
    }
    ctx.putImageData(img, 0, 0);
  }

  return { rgbBits: rgbBits, mix3: mix3, TONES: TONES, drawIcon: drawIcon };
})();
