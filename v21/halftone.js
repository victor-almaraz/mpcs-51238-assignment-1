/* Halftone: a plate renderer for canvases, after Version 18's press.
   Every colour area is a screen of round dots at its ink's angle (cyan 15, magenta 75,
   yellow 0, black 45, spot orange 60 degrees). Dot area follows tone, with about 12%
   dot gain; past 85% the dots swell until they close up. Each plate is a fraction of
   a pixel out of register, overlapping inks multiply, and the paper carries specks.
   Canvases render at device resolution.

   Nothing here looks up page elements by itself: every function takes a canvas (or a
   context) and its size, plus the element to measure where text is involved. Painters
   that cost anything are keyed (Halftone.fresh), so a canvas is printed again only
   when its size, its inputs or the device pixel ratio change. */
var Halftone = (function () {
  'use strict';

  var INKS = {
    c: { color: '#00a6c8', angle: 15 },
    m: { color: '#dc0078', angle: 75 },
    y: { color: '#ffd400', angle: 0 },
    k: { color: '#0d0d0d', angle: 45 },
    o: { color: '#ff5a1f', angle: 60 }
  };
  var PAPER = '#fffaf0';
  var DISPLAY = 'italic 400 {s}px "Playfair Display", Didot, "Bodoni 72", serif';
  var H = { INKS: INKS, PAPER: PAPER, ready: false };

  function clamp(t) { return t < 0 ? 0 : t > 1 ? 1 : t; }
  function smooth(a, b, t) { t = clamp((t - a) / (b - a)); return t * t * (3 - 2 * t); }
  function hash(i) { var s = Math.sin(i * 12.9898 + 78.233) * 43758.5453; return s - Math.floor(s); }
  function lum(hex) {
    var v = [1, 3, 5].map(function (i) { var c = parseInt(hex.substr(i, 2), 16) / 255; return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4); });
    return 0.2126 * v[0] + 0.7152 * v[1] + 0.0722 * v[2];
  }
  // contrast of a screen of coverage t against bare paper, averaging ink and paper by area
  function screenContrast(ink, t, ground) {
    var a = t * lum(INKS[ink].color) + (1 - t) * lum(ground || PAPER), b = lum(ground || PAPER);
    return (Math.max(a, b) + 0.05) / (Math.min(a, b) + 0.05);
  }
  function dpr() { return Math.min(3, window.devicePixelRatio || 1); }

  // True (and remembered) when the canvas has not yet been printed for this key.
  function fresh(canvas, key) {
    key = key + '@' + dpr() + (H.ready ? 'F' : 'f');
    if (canvas._htKey === key) return false;
    canvas._htKey = key;
    return true;
  }

  // A canvas at device resolution. bg: a colour to print on, or null for a clear canvas.
  function setup(canvas, w, h, bg) {
    var r = dpr();
    canvas.width = Math.round(w * r); canvas.height = Math.round(h * r);
    canvas.style.width = w + 'px'; canvas.style.height = h + 'px';
    var ctx = canvas.getContext('2d');
    ctx.setTransform(r, 0, 0, r, 0, 0);
    ctx.globalCompositeOperation = 'source-over';
    ctx.clearRect(0, 0, w, h);
    if (bg !== null) { ctx.fillStyle = bg || PAPER; ctx.fillRect(0, 0, w, h); }
    return ctx;
  }

  // One plate: a rotated lattice of round dots whose area follows tone(x, y).
  // Dots are gathered into four paths by lattice parity. Two dots of one class are at
  // least two cells apart and never touch, so filling each class at once multiplies
  // every overlap exactly as dot-by-dot filling would, at a fraction of the cost.
  // clip: an optional {x0, y0, x1, y1} outside which the tone is known to be zero.
  function plate(ctx, w, h, ink, cell, tone, shift, clip) {
    var a = INKS[ink].angle * Math.PI / 180, ca = Math.cos(a), sa = Math.sin(a);
    var n = Math.ceil(Math.sqrt(w * w + h * h) / cell / 2) + 2;
    var ox = w / 2 + (shift ? shift[0] : 0.4), oy = h / 2 + (shift ? shift[1] : -0.3);
    var x0 = -cell, y0 = -cell, x1 = w + cell, y1 = h + cell, salt = ink.charCodeAt(0);
    if (clip) { x0 = Math.max(x0, clip.x0 - cell); y0 = Math.max(y0, clip.y0 - cell); x1 = Math.min(x1, clip.x1 + cell); y1 = Math.min(y1, clip.y1 + cell); }
    var paths = [new Path2D(), new Path2D(), new Path2D(), new Path2D()], any = false;
    for (var i = -n; i <= n; i++) {
      for (var j = -n; j <= n; j++) {
        var x = ox + (i * ca - j * sa) * cell, y = oy + (i * sa + j * ca) * cell;
        if (x < x0 || y < y0 || x > x1 || y > y1) continue;
        var t = tone(x, y);
        if (t <= 0.03) continue;
        // area-true radius with dot gain; past 85% the dots swell smoothly until they close up
        var r = cell * Math.sqrt(clamp(t) / Math.PI) * (1.12 + 0.07 * (hash(i * 131 + j * 7 + salt) - 0.5));
        if (t > 0.85) r += (cell * 0.74 - r) * smooth(0.85, 1, t);
        var p = paths[(i & 1) * 2 + (j & 1)];
        p.moveTo(x + r, y);
        p.arc(x, y, r, 0, Math.PI * 2);
        any = true;
      }
    }
    if (!any) return;
    ctx.globalCompositeOperation = 'multiply';
    ctx.fillStyle = INKS[ink].color;
    for (var k = 0; k < 4; k++) ctx.fill(paths[k]);
    ctx.globalCompositeOperation = 'source-over';
  }

  // Paper grain: a fixed scatter of tiny fibres and specks.
  function grain(ctx, w, h, seed) {
    var count = Math.round(w * h / 140);
    ctx.globalCompositeOperation = 'multiply';
    for (var i = 0; i < count; i++) {
      var x = hash(seed + i * 2.17) * w, y = hash(seed + i * 3.91 + 7) * h, v = hash(seed + i * 5.3);
      ctx.fillStyle = 'rgba(80, 64, 40, ' + (0.05 + 0.08 * v).toFixed(3) + ')';
      ctx.fillRect(x, y, v > 0.85 ? 2.2 : 0.9, 0.9);
    }
    ctx.globalCompositeOperation = 'source-over';
  }

  /* ---------------- type: the real text's words, set again on a canvas ---------------- */
  // Each word is measured where the browser laid it out, so the canvas copy sits exactly
  // over the (transparent) real text: same face, size, letter-spacing and line breaks.
  var measure = document.createElement('canvas').getContext('2d');
  function runsOf(el, origin) {
    var out = [], tw = document.createTreeWalker(el, NodeFilter.SHOW_TEXT), n;
    while ((n = tw.nextNode())) {
      var cs = getComputedStyle(n.parentElement);
      var font = cs.fontStyle + ' ' + cs.fontWeight + ' ' + cs.fontSize + ' ' + cs.fontFamily;
      var ls = cs.letterSpacing === 'normal' ? '0px' : cs.letterSpacing;
      measure.font = font; measure.letterSpacing = ls;
      var re = /\S+/g, m;
      while ((m = re.exec(n.textContent))) {
        var r = document.createRange(); r.setStart(n, m.index); r.setEnd(n, m.index + m[0].length);
        var q = r.getClientRects()[0];
        if (!q) continue;
        var asc = measure.measureText(m[0]).fontBoundingBoxAscent;
        out.push({ t: m[0], font: font, ls: ls, x: q.left - origin.left, y: q.top - origin.top + asc,
          top: q.top - origin.top, bottom: q.bottom - origin.top, right: q.right - origin.left });
      }
    }
    return out;
  }
  // A single run set from scratch: text in the display face at size s, its ink's left
  // edge at x and its cap top at top (for canvases with no DOM text behind them).
  function displayRun(text, s, x, top, ls) {
    var font = DISPLAY.replace('{s}', s.toFixed(2));
    measure.font = font; measure.letterSpacing = (ls || 0) + 'px';
    var m = measure.measureText(text);
    var left = x + m.actualBoundingBoxLeft, base = top + m.actualBoundingBoxAscent;
    return { t: text, font: font, ls: (ls || 0) + 'px', x: left, y: base, top: top,
      bottom: base + m.actualBoundingBoxDescent, right: left + m.width };
  }
  // the size at which text in the display face is wide wide and/or tall tall
  function fitDisplay(text, wide, tall, ls) {
    measure.font = DISPLAY.replace('{s}', '100'); measure.letterSpacing = (ls || 0) * 100 + 'px';
    var m = measure.measureText(text);
    var mw = m.actualBoundingBoxLeft + m.actualBoundingBoxRight, mh = m.actualBoundingBoxAscent + m.actualBoundingBoxDescent;
    return Math.min(wide ? wide / mw * 100 : 1e9, tall ? tall / mh * 100 : 1e9);
  }
  function bbox(runs) {
    var b = { x0: 1e9, y0: 1e9, x1: -1e9, y1: -1e9 };
    runs.forEach(function (r) { b.x0 = Math.min(b.x0, r.x); b.x1 = Math.max(b.x1, r.right); b.y0 = Math.min(b.y0, r.top); b.y1 = Math.max(b.y1, r.bottom); });
    return b;
  }
  function drawRuns(ctx, runs, color, dx, dy) {
    ctx.fillStyle = color; ctx.textBaseline = 'alphabetic';
    runs.forEach(function (r) { ctx.font = r.font; ctx.letterSpacing = r.ls; ctx.fillText(r.t, r.x + (dx || 0), r.y + (dy || 0)); });
    ctx.letterSpacing = '0px';
  }
  // A plate cut to the letterforms: the dots are drawn, then trimmed to the exact glyph
  // outlines, so edges stay crisp and hairlines survive at any screen ruling.
  function screenedType(ctx, w, h, runs, ink, cell, tone, shift, dx, dy) {
    var L = document.createElement('canvas'); L.width = ctx.canvas.width; L.height = ctx.canvas.height;
    var lc = L.getContext('2d'), s = L.width / w, b = bbox(runs), pad = cell * 2;
    lc.setTransform(s, 0, 0, s, 0, 0);
    plate(lc, w, h, ink, cell, tone, shift, { x0: b.x0 + (dx || 0) - pad, y0: b.y0 + (dy || 0) - pad, x1: b.x1 + (dx || 0) + pad, y1: b.y1 + (dy || 0) + pad });
    // all the words go on one mask first: trimming word by word would cut each away
    var M = document.createElement('canvas'); M.width = L.width; M.height = L.height;
    var mc = M.getContext('2d'); mc.setTransform(s, 0, 0, s, 0, 0);
    drawRuns(mc, runs, '#000', dx, dy);
    lc.setTransform(1, 0, 0, 1, 0, 0);
    lc.globalCompositeOperation = 'destination-in';
    lc.drawImage(M, 0, 0);
    ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalCompositeOperation = 'multiply'; ctx.drawImage(L, 0, 0); ctx.restore();
  }
  function knockout(ctx, runs, dx, dy) { ctx.globalCompositeOperation = 'source-over'; drawRuns(ctx, runs, PAPER, dx, dy); }

  /* ---------------- op-art swatches ---------------- */
  // Each takes unit-square coordinates and returns [block ink, black] coverage, or null
  // outside its shape: rings, stripes, quadrants, bars, crossed rings, warped checker,
  // rays, nested squares, spiral.
  var OP = [
    function (u, v) { var d = Math.hypot(u - 0.5, v - 0.5); if (d > 0.5) return null; var k = Math.floor(d * 10); return k % 2 ? [0.95, 0] : [0, 0.95]; },
    function (u, v) { var s = ((u + v) * 7) % 1; return s < 0.5 ? [0, 0.05] : [0.6, 0.95]; },
    function (u, v) { var d = Math.hypot(u - 0.5, v - 0.5); if (d > 0.5) return null; var q = Math.floor((Math.atan2(v - 0.5, u - 0.5) / Math.PI + 1) * 2); return q % 2 ? [0, 0] : [0.15, 0.95]; },
    function (u, v) { if (v < 0.5 && Math.hypot(u - 0.5, v - 0.5) > 0.5) return null; return Math.floor(v * 12) % 2 ? [0, 0] : [0.9, 0.95]; },
    function (u, v) { var a = Math.hypot(u - 0.38, v - 0.45), b = Math.hypot(u - 0.62, v - 0.55); return [0.2 + 0.6 * u, ((a * 14) % 1 < 0.5 ? 0.6 : 0) + ((b * 14) % 1 < 0.5 ? 0.4 : 0)]; },
    function (u, v) { var x = u + 0.08 * Math.sin(v * 9), c = (Math.floor(x * 6) + Math.floor(v * 6)) % 2; return c ? [0, 0] : [0.9, 0.95]; },
    function (u, v) { var d = Math.hypot(u - 0.5, v - 0.5); if (d > 0.5) return null; var ray = Math.floor((Math.atan2(v - 0.5, u - 0.5) / Math.PI + 1) * 8) % 2; return ray ? [0, 0] : [0.9, 0.95 - d]; },
    function (u, v) { var m = Math.max(Math.abs(u - 0.5), Math.abs(v - 0.5)); return Math.floor(m * 14) % 2 ? [0, 0] : [0.9, 0.95]; },
    function (u, v) { var d = Math.hypot(u - 0.5, v - 0.5); if (d > 0.5) return null; var s = (Math.atan2(v - 0.5, u - 0.5) / (2 * Math.PI) + Math.log(d + 0.02) * 0.9) * 3; return ((s % 1) + 1) % 1 < 0.5 ? [0, 0] : [0.9, 0.9]; }
  ];

  /* ---------------- compositions ---------------- */

  // The title plate and colour field, stacked as a cover: a black plate across the top
  // (0 to o.split) with o.runs knocked out of it to bare paper, a magenta shadow printed
  // out of register inside the letters and a yellow ramp across the word; then an orange
  // field below with a black disc cropped by the right edge and a magenta target of rings.
  // Without o.runs (or before the faces load) the black plate is flat ink, so real text
  // laid over it still reads.
  function cover(canvas, w, h, o) {
    o = o || {};
    var ctx = setup(canvas, w, h), split = o.split || h * 0.45;
    var cell = Math.max(2, Math.min(6.5, w / 95)), seed = o.seed || 5;
    var fh = h - split, foot = Math.min(42, split * 0.14);
    var disc = { x: w * 0.9, y: split + fh * 0.3, r: Math.min(w * 0.42, fh * 0.42) };
    var tgt = { x: w * 0.25, y: split + fh * 0.32, r: Math.min(w * 0.18, fh * 0.22) };
    var ring = Math.max(3, tgt.r / 6), fine = Math.max(1.2, Math.min(3, w / 200));
    // the field first, so the black plate's broken foot overprints it
    plate(ctx, w, h, 'o', cell * 1.1, function (x, y) {
      if (y < split - foot) return 0;
      if (Math.hypot(x - tgt.x, y - tgt.y) < tgt.r) return 0;
      return 1 - 0.5 * smooth(0.25, 1.15, (x / w) * 0.3 + ((y - split) / fh) * 0.9);
    }, [0.6, 0.4], { x0: 0, y0: split - foot, x1: w, y1: h });
    // the target's rings on a finer screen than the field, so their edges stay round
    plate(ctx, w, h, 'm', fine, function (x, y) {
      var d = Math.hypot(x - tgt.x, y - tgt.y);
      if (d >= tgt.r) return 0;
      return (d % ring) > ring / 2 ? 1 : 0;
    }, [-0.7, 0.3], { x0: tgt.x - tgt.r, y0: tgt.y - tgt.r, x1: tgt.x + tgt.r, y1: tgt.y + tgt.r });
    plate(ctx, w, h, 'k', cell, function (x, y) {
      var d = Math.hypot(x - disc.x, y - disc.y);
      return 1 - smooth(disc.r - cell * 4, disc.r, d);
    }, [0.2, -0.6], { x0: disc.x - disc.r, y0: disc.y - disc.r, x1: w, y1: disc.y + disc.r });
    var runs = H.ready && o.runs && o.runs.length ? o.runs : null;
    function ground(x, y) { return y > split ? 0 : 0.96 - 0.55 * smooth(split - foot, split, y) - 0.3 * smooth(w * 0.7, w, x) * smooth(split * 0.6, split, y); }
    if (!runs) {
      ctx.fillStyle = INKS.k.color; ctx.fillRect(0, 0, w, split);
      grain(ctx, w, h, seed);
      return { contrast: 0, letters: 'flat' };
    }
    plate(ctx, w, h, 'k', cell, ground, [0.3, -0.4], { x0: 0, y0: 0, x1: w, y1: split });
    grain(ctx, w, h, seed);
    var b = bbox(runs), fs = o.fontSize || (b.y1 - b.y0);
    var dx = fs * 0.035, dy = fs * 0.025, tc = Math.max(1.6, cell * 0.8);
    knockout(ctx, runs, dx, dy);
    screenedType(ctx, w, h, runs, 'm', tc, function () { return 0.96; }, [-0.5, 0.4], dx, dy);
    knockout(ctx, runs, 0, 0);
    screenedType(ctx, w, h, runs, 'y', tc * 0.88, function (x) { return 0.32 * smooth(b.x0, b.x1, x); }, [0.2, 0.2], 0, 0);
    // effective contrast: paper letters against the thinnest part of the ground behind them
    var tmin = 1;
    for (var x = b.x0; x <= b.x1; x += 8) for (var y = b.y0; y <= b.y1; y += 8) tmin = Math.min(tmin, ground(x, y));
    return { contrast: screenContrast('k', tmin), letters: 'knockout' };
  }

  // A small cover with its own title set on the canvas (for a thumbnail with no DOM text).
  function coverThumb(canvas, w, h, title) {
    title = title || 'FORTRAN';
    var split = h * 0.42, s = fitDisplay(title, w * 0.9, 0, -0.035);
    var run = displayRun(title, s, w * 0.04, split * 0.42, -0.035 * s);
    return cover(canvas, w, h, { split: split, runs: [run], fontSize: s, seed: 9 });
  }

  // A block of one ink with a big numeral knocked out of it to bare paper (cropped by the
  // block's edges, with a screened black drop shadow) and an op-art swatch overprinted on
  // it in black. Tall blocks put the numeral at the top and the swatch at the foot; wide
  // strips put them side by side. o: { ink, op (index into OP), numeral (or none), seed }.
  function shot(canvas, w, h, o) {
    var ctx = setup(canvas, w, h), ink = o.ink || 'm', f = OP[(o.op || 0) % OP.length];
    var strip = w > h * 1.35, text = o.numeral || '';
    var op = strip
      ? { s: h * 0.8, x: w - h * 0.8 - h * 0.1, y: h * 0.1 }
      : { s: Math.min(w * 0.62, h * 0.52), x: 0, y: 0 };
    if (!strip) { op.x = w - op.s - w * 0.08; op.y = h - op.s - Math.min(h * 0.07, w * 0.08); }
    if (!text && !strip) { op.s = Math.min(w, h) * 0.7; op.x = (w - op.s) / 2; op.y = (h - op.s) / 2; }
    function inOp(x, y) { var u = (x - op.x) / op.s, v = (y - op.y) / op.s; return u >= 0 && u <= 1 && v >= 0 && v <= 1 ? f(u, v) : null; }
    var box = { x0: op.x, y0: op.y, x1: op.x + op.s, y1: op.y + op.s };
    // the block on a 5px screen, its light falling off away from the numeral; the swatch on
    // a much finer one, so spirals and rings keep smooth edges
    var fine = Math.max(1.6, Math.min(2.2, op.s / 80));
    plate(ctx, w, h, ink, 5, function (x, y) {
      if (inOp(x, y)) return 0;
      return strip ? 0.96 - 0.45 * smooth(0.35, 1, x / w) : 0.96 - 0.4 * smooth(0.25, 0.95, y / h);
    }, [0.5, -0.3]);
    plate(ctx, w, h, ink, fine, function (x, y) { var q = inOp(x, y); return q ? q[0] : 0; }, [0.3, -0.2], box);
    plate(ctx, w, h, 'k', fine, function (x, y) { var q = inOp(x, y); return q ? q[1] : 0; }, [-0.3, 0.4], box);
    if (text) {
      // set big enough to be cropped: it bleeds off the block's top and left edges
      var size = strip ? fitDisplay(text, (op.x - h * 0.1) * 1.02, h * 1.12) : fitDisplay(text, w * 1.02, h * 0.62);
      var run = displayRun(text, size, -size * 0.05, -size * 0.07);
      var sx = size * 0.035, sy = size * 0.025;
      knockout(ctx, [run], sx, sy);
      screenedType(ctx, w, h, [run], 'k', 4, function () { return 0.6; }, [0.1, 0.2], sx, sy);
      knockout(ctx, [run], 0, 0);
    }
    grain(ctx, w, h, o.seed || 40);
  }

  // Two inks overprinting across a strip (yellow and cyan meet in green), with a black rule
  // along the foot whose top edge breaks into dots.
  function wash(canvas, w, h, o) {
    o = o || {};
    var ctx = setup(canvas, w, h), a = o.a || 'y', b = o.b || 'c', rule = o.rule == null ? Math.min(18, h * 0.12) : o.rule;
    plate(ctx, w, h, a, 7, function (x, y) { return y > h - rule ? 0 : 0.95 * (1 - smooth(0.15, 0.75, x / w)); }, [0.5, 0.2]);
    plate(ctx, w, h, b, 7, function (x, y) { return y > h - rule ? 0 : 0.95 * smooth(0.3, 0.95, x / w) * (0.75 + 0.25 * (y / h)); }, [-0.4, 0.5]);
    if (rule) plate(ctx, w, h, 'k', 5, function (x, y) { return smooth(h - rule - 8, h - rule + 6, y); }, [0.2, -0.3], { x0: 0, y0: h - rule - 10, x1: w, y1: h });
    grain(ctx, w, h, o.seed || 17);
  }

  // Display type of 40px and up, screened over its own transparent real text: a black
  // screen ramping lighter across the word (never below 88% coverage) over the ink's
  // plate printed out of register, and a screened rule of the ink under the last line.
  // The canvas is a child of el (which must be positioned). maxRight: the x in viewport
  // coordinates past which the overhang room must not reach. Returns false (and shows
  // the real text) when the type is too small, hidden, or the faces have not loaded.
  var KMIN = 0.88;
  function heading(el, ink, o) {
    o = o || {};
    var cs = getComputedStyle(el), fs = parseFloat(cs.fontSize);
    var old = el.querySelector(':scope > canvas.ht-type');
    if (!H.ready || fs < 40 || !el.getClientRects().length) {
      el.classList.remove('ht-on'); if (old) { old.remove(); }
      return false;
    }
    var r = el.getBoundingClientRect(), pad = Math.ceil(fs * 0.45);
    var w = Math.ceil(r.width + 2 * pad), h = Math.ceil(r.height + 2 * pad);
    if (o.maxRight) w = Math.max(1, Math.min(w, Math.floor(o.maxRight - (r.left - pad))));
    var c = old;
    if (!c) {
      c = document.createElement('canvas');
      c.className = 'ht-type';
      c.setAttribute('aria-hidden', 'true');
      el.appendChild(c);
    }
    if (!fresh(c, [w, h, fs, ink, el.textContent].join('|')) && el.classList.contains('ht-on')) return true;
    c.style.position = 'absolute'; c.style.left = -pad + 'px'; c.style.top = -pad + 'px';
    var runs = runsOf(el, { left: r.left - pad, top: r.top - pad }), b = bbox(runs);
    var ctx = setup(c, w, h, null), cell = Math.max(2.6, fs / 30);
    var dx = fs * 0.04, dy = fs * 0.03;
    screenedType(ctx, w, h, runs, ink, cell * 1.15, function () { return 0.95; }, [0.6, -0.4], dx, dy);
    screenedType(ctx, w, h, runs, 'k', cell, function (x) { return 1 - (1 - KMIN) * smooth(b.x0, b.x1, x); }, [-0.3, 0.2], 0, 0);
    if (o.rule !== false) {
      var last = runs.reduce(function (m, q) { return q.bottom > m ? q.bottom : m; }, 0), lastLeft = 1e9, lastRight = 0;
      runs.forEach(function (q) { if (q.bottom === last) { lastLeft = Math.min(lastLeft, q.x); lastRight = Math.max(lastRight, q.right); } });
      var y0 = last + fs * 0.04, y1 = y0 + fs * 0.16;
      plate(ctx, w, h, ink, cell * 1.3, function (x, y) { return y >= y0 && y <= y1 && x >= lastLeft && x <= lastRight ? 0.95 - 0.55 * smooth(lastLeft, lastRight, x) : 0; }, [0.2, 0.3], { x0: lastLeft, y0: y0, x1: lastRight, y1: y1 });
    }
    c.dataset.contrast = screenContrast('k', KMIN).toFixed(2);
    el.classList.add('ht-on');
    return true;
  }

  // Calls fn once the given faces (CSS font shorthands) have loaded, setting H.ready.
  function whenFonts(fonts, fn) {
    function go() { H.ready = true; fn(); }
    if (!document.fonts || !document.fonts.load) { go(); return; }
    Promise.all(fonts.map(function (f) { return document.fonts.load(f); }).concat(document.fonts.ready)).then(go, go);
  }

  H.clamp = clamp; H.smooth = smooth; H.hash = hash; H.screenContrast = screenContrast;
  H.fresh = fresh; H.setup = setup; H.plate = plate; H.grain = grain;
  H.runsOf = runsOf; H.bbox = bbox; H.displayRun = displayRun; H.fitDisplay = fitDisplay;
  H.screenedType = screenedType; H.knockout = knockout; H.OP = OP;
  H.cover = cover; H.coverThumb = coverThumb; H.shot = shot; H.wash = wash; H.heading = heading;
  H.whenFonts = whenFonts;
  return H;
})();
