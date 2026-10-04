/* The workspace: the programs, the Editor and its saved texts, a job and its Results, the
   program's Output and the Player. The engine is used through Fortran.run only, and sound
   through Tape. Needs Desk (wm.js), Files (fs.js), Px (pixels.js) and PROGRAMS (programs.js).

   Workspace.openText(name, text, kind)   puts a text in the Editor (the old one to the Trash)
   Workspace.renderPrinter(box, lines, empty)   printer lines, with a rule at each new page */

var Workspace = (function () {
  'use strict';
  var doc = document, $ = Desk.$, $$ = Desk.$$, el = Desk.el, plural = Desk.plural, clamp = Desk.clamp;
  var LIST = PROGRAMS.list, N_ENGINE = PROGRAMS.engine;

  /* ---------------- the programs, into the Programs folder ---------------- */
  var progFolder = Files.byWin('win-programs');
  LIST.forEach(function (s, i) {
    Files.add(progFolder, { kind: 'program', name: s.name, icon: i < N_ENGINE ? 'source' : 'music', group: i < N_ENGINE ? 'Samples' : 'Music', program: i, locked: true });
  });
  Files.opener('program', function (n) { openProgram(n.program, n); });
  Files.opener('text', function (n) { openText(n.name, n.text, n.kindText || 'FORTRAN source', 'Opened ' + n.name + ' from ' + Files.where(n.parent) + '.', n); });

  /* ================================================================ the Editor */
  var src = $('src'), gutterEl = $('gutter'), rulerEl = $('ruler'), marginsEl = $('margins');
  var current = { name: LIST[0].name, original: LIST[0].lines.join('\n'), kind: 'FORTRAN source', node: null };
  src.value = current.original;

  // ruler ticks: one cell per column, a longer tick every fifth, numbers where they help
  (function buildTicks() {
    var t = $('ticks'), shown = { 1: 1, 7: 1, 10: 1, 20: 1, 30: 1, 40: 1, 50: 1, 60: 1, 72: 1, 80: 1 }, frag = doc.createDocumentFragment();
    for (var c = 1; c <= 80; c++) {
      var s = el('span', 'tk' + (c % 5 === 0 ? ' t5' : '') + (c === 6 || c === 7 || c === 72 || c === 73 ? ' tf' : ''));
      if (shown[c]) s.appendChild(el('b', '', String(c)));
      frag.appendChild(s);
    }
    t.appendChild(frag);
  })();

  function isComment(l) { var c = l.charAt(0); return c === 'C' || c === 'c' || c === '*'; }
  function isEndLine(l) {
    var u = l.toUpperCase(), c6 = u.charAt(5);
    return !isComment(u) && (c6 === ' ' || c6 === '0' || c6 === '') && u.slice(6, 72).replace(/ /g, '') === 'END';
  }
  function endIndex(ls) { for (var i = 0; i < ls.length; i++) if (isEndLine(ls[i])) return i; return -1; }
  function lastCol(l) { return l.replace(/\s+$/, '').length; }
  function trimmed(ls) { ls = ls.slice(); while (ls.length && ls[ls.length - 1].trim() === '') ls.pop(); return ls; }
  function slug(s) { return s.toLowerCase().replace(/\(.*?\)/g, '').replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '') || 'untitled'; }

  var lastCount = -1;
  function renderGutter(ls) {
    if (ls.length === lastCount) return;
    lastCount = ls.length;
    var out = '';
    for (var i = 1; i <= ls.length; i++) out += '<span>' + i + '</span>';
    gutterEl.innerHTML = out;
  }
  function syncScroll() {
    gutterEl.style.transform = 'translateY(' + (-src.scrollTop) + 'px)';
    rulerEl.style.transform = marginsEl.style.transform = 'translateX(' + (-src.scrollLeft) + 'px)';
  }
  src.addEventListener('scroll', syncScroll);
  function caret() {
    var p = src.selectionStart, before = src.value.slice(0, p);
    return { line: before.split('\n').length, col: p - before.lastIndexOf('\n'), pos: p };
  }
  function fieldName(l, col, data) {
    if (data) return col > 80 ? 'past column 80' : 'data';
    if (isComment(l)) return 'comment';
    if (col <= 5) return 'label field';
    if (col === 6) return 'continuation column';
    if (col <= 72) return 'statement field';
    if (col <= 80) return 'ignored columns';
    return 'past column 80';
  }
  var shownText = '', note = '', curLine = null;
  // One pass over the lines on each change; the cursor's line is looked up, not rescanned.
  function updateStatus() {
    var ls = src.value.split('\n'), c = caret(), l = ls[c.line - 1] || '', end = endIndex(ls);
    var data = end >= 0 && c.line - 1 > end;
    renderGutter(ls);
    if (curLine) curLine.classList.remove('cur');
    curLine = gutterEl.children[c.line - 1] || null;
    if (curLine) curLine.classList.add('cur');
    $('ed-pos').textContent = 'Line ' + c.line + ', Col ' + c.col;
    $('ed-field').textContent = fieldName(l, c.col, data);
    $('caretcol').style.transform = 'translateX(' + (Math.min(c.col, 81) - 1) * 10 + 'px)';
    $('caretcol').hidden = c.col > 80;
    // warnings: the cursor's line first, then any other line that runs too far
    var warn = '', over = [];
    ls.forEach(function (x, i) {
      var n = lastCol(x), isData = end >= 0 && i > end;
      if (n > 80 || (!isData && !isComment(x) && n > 72)) over.push(i);
    });
    var n = lastCol(l);
    if (n > 80) warn = 'Line ' + c.line + ' is ' + n + ' columns long; only the first 80 are read.';
    else if (!data && !isComment(l) && n > 72) warn = 'Line ' + c.line + ' runs past column 72; columns 73–80 are ignored.';
    else if (over.length) warn = plural(over.length, 'line') + ' run' + (over.length === 1 ? 's' : '') + ' too far, first line ' + (over[0] + 1) + '.';
    // a warning about the columns comes first; otherwise the last note stands
    var line = warn || note;
    if (line !== shownText) { $('ed-warn').textContent = line; shownText = line; }
    $('ed-warn').classList.toggle('on', !!warn);
    $('ed-lines').textContent = plural(ls.length, 'line') + (end >= 0 ? ', ' + plural(Math.max(0, trimmed(ls).length - end - 1), 'data line') : ', no END line');
    var edited = src.value !== current.original;
    $('ed-revert').disabled = !edited;
    $('ed-kind').textContent = current.kind + (edited ? ', edited' : '');
  }
  src.addEventListener('input', function () { note = ''; });
  ['input', 'keyup', 'click', 'focus'].forEach(function (e) { src.addEventListener(e, updateStatus); });
  doc.addEventListener('selectionchange', function () { if (doc.activeElement === src) updateStatus(); });

  function insert(text) {
    // execCommand keeps the browser's undo history; setRangeText is the fallback
    if (!(doc.execCommand && doc.execCommand('insertText', false, text))) {
      src.setRangeText(text, src.selectionStart, src.selectionEnd, 'end');
      src.dispatchEvent(new Event('input'));
    }
  }
  // Tab: on to column 7, then to column 73; Shift+Tab: back to the start of the field
  src.addEventListener('keydown', function (e) {
    if (e.key === 'Tab' && !e.altKey && !e.ctrlKey && !e.metaKey) {
      e.preventDefault();
      var c = caret(), l = src.value.split('\n')[c.line - 1], col = c.col, lineStart = c.pos - (col - 1);
      if (e.shiftKey) {
        var back = col > 73 ? 73 : col > 7 ? 7 : 1, to = lineStart + Math.min(back - 1, l.length);
        src.setSelectionRange(to, to); updateStatus();
        return;
      }
      var stop = col < 7 ? 7 : col < 73 ? 73 : 0;
      if (!stop) return;
      if (col - 1 < l.length && src.selectionStart === src.selectionEnd) {
        // inside existing text, move the cursor rather than push the text along
        if (stop - 1 <= l.length) { var target = lineStart + stop - 1; src.setSelectionRange(target, target); updateStatus(); return; }
        src.setSelectionRange(lineStart + l.length, lineStart + l.length);
        col = l.length + 1;
      }
      insert(' '.repeat(stop - col));
    } else if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
      e.preventDefault(); runJob();
    } else if ((e.key === 's' || e.key === 'S') && (e.ctrlKey || e.metaKey)) {
      e.preventDefault(); Desk.act(e.shiftKey ? 'save-as' : 'save');
    }
  });

  /* ---------------- documents in the Editor: opened, saved, and thrown away ---------------- */
  function setDoc(d) {
    if (src.value !== current.original && src.value.trim() !== '') toTrash();
    current = d;
    src.value = d.text != null ? d.text : d.original;
    $('ed-name').textContent = d.name;
    lastCount = -1;
    src.setSelectionRange(0, 0); src.scrollTop = 0; src.scrollLeft = 0; syncScroll();
    updateStatus();
  }
  // an edited text that would be lost goes to the Trash, from which Put Back reopens it
  var trashed = false;
  function toTrash() { Files.trashText(current.name, src.value, current); trashed = true; }
  Files.opener('scrap', function (t) {
    var d = t.scrap;
    setDoc({ name: d.name, original: d.original, kind: d.kind, node: d.node, text: t.text });
    Desk.open('win-editor', { focusEl: src });
    say('The edited text of ' + t.name + ' was put back.');
  });
  function say(msg) { note = msg; updateStatus(); }

  function openText(name, text, kind, note, node) {
    trashed = false;
    setDoc({ name: name, original: text, kind: kind || 'FORTRAN source', node: node || null });
    Desk.open('win-editor', { focusEl: src });
    say((note || 'Opened ' + name + '.') + (trashed ? ' The edited text before it is in the Trash.' : ''));
  }
  function openProgram(i, node) { var s = LIST[i]; openText(s.name, s.lines.join('\n'), i < N_ENGINE ? 'FORTRAN source' : 'FORTRAN music program', null, node); }

  // Save writes a saved text back where it is; anything else is saved as a new text in a
  // folder. A program of the workspace is locked, so its edits are saved as a copy.
  function saveAs() {
    var n = current.node;
    Files.save({
      msg: 'Save the Editor’s text as a document. It is kept in the folder you choose until the page is closed; Download keeps a copy on your computer.',
      name: n && n.kind === 'text' ? current.name + ' copy' : current.name, folder: n && n.parent
    }, function (name, folder) {
      var node = Files.add(folder, { kind: 'text', name: name, icon: current.kind === 'output records' ? 'punchfile' : 'source', text: src.value, kindText: current.kind === 'FORTRAN source' ? null : current.kind });
      setTimeout(function () {
        current = { name: name, original: src.value, kind: current.kind, node: node };
        $('ed-name').textContent = name;
        say('Saved as ' + name + ' in ' + Files.where(folder) + '.');
      }, 0);
    });
  }
  function save() {
    var n = current.node;
    if (!(n && n.kind === 'text' && Files.alive(n))) { saveAs(); return; }
    n.text = src.value; current.original = src.value;
    say('Saved ' + n.name + ' in ' + Files.where(n.parent) + '.');
  }
  // a saved text renamed in its folder is renamed in the Editor too
  Files.onChange(function () {
    var n = current.node;
    if (n && n.name !== current.name && n.kind === 'text') { current.name = n.name; $('ed-name').textContent = n.name; }
  });
  $('ed-revert').addEventListener('click', function () {
    src.value = current.original; lastCount = -1; updateStatus();
    say('The text is back to the way it was opened.');
  });
  $('ed-download').addEventListener('click', function () {
    var name = slug(current.name) + '.f';
    Desk.download(src.value.replace(/\n?$/, '\n'), name);
    say('Downloaded the text as ' + name + '.');
  });

  /* ================================================================ running a job */
  var punched = [], jobName = '';
  function runJob() {
    var lines = trimmed(src.value.split('\n'));
    var result = Fortran.run(lines);
    renderPrinter($('printer'), result.printer, 'The program did not print anything.');
    $('pr-count').textContent = plural(result.printer.filter(function (l) { return l !== '\f'; }).length, 'line') + ', ' +
      plural(Math.max(1, result.printer.filter(function (l, i) { return l === '\f' && i > 0; }).length + 1), 'page');
    renderLog(result);
    $('listing').textContent = result.listing.length ? result.listing.join('\n') : 'The job produced no listing.';
    renderOutput(result.punched);
    $('run-status').textContent = 'The computer read ' + plural(lines.length, 'line') +
      (result.ok ? ', and the job ran without errors.' : ', and the job stopped with errors. See the Job Log for details.');
    jobName = current.name;
    $('pr-job').textContent = jobName;
    say(result.ok ? 'The job ran without errors.' : 'The job stopped with errors.');
    Desk.open('win-printer', { focus: result.ok });
    if (!result.ok) {
      Desk.open('win-log');
      Desk.alert('The job stopped with errors. The Job Log has the details.', 'note');
    }
  }
  $('ed-run').addEventListener('click', runJob);

  // Printer lines, one <pre> per page, with a perforated rule between pages. The first
  // page's own form feed draws no rule. Shared with the course.
  function renderPrinter(box, lines, empty) {
    box.innerHTML = '';
    if (!lines.length) { box.appendChild(el('p', 'placeholder', empty || 'Nothing was printed.')); return; }
    var pre = null, text = [];
    function flush() { if (pre) pre.textContent = text.join('\n'); pre = null; text = []; }
    lines.forEach(function (ln, i) {
      if (ln === '\f') {
        flush();
        if (i === 0) return;
        var div = el('div', 'pagebreak'); div.appendChild(el('span', '', 'new page')); box.appendChild(div);
        return;
      }
      if (!pre) { pre = el('pre'); box.appendChild(pre); }
      text.push(ln);
    });
    flush();
  }
  // The engine's messages are worded for cards; the workspace shows them in its own terms.
  var LOG_WORDS = [
    [/^card (\d+): /, 'line $1: '],
    [/on data card (\d+)/g, 'on data line $1'],
    [/no END card in the deck/g, 'no END line in the program'],
    [/continuation card has no statement to continue/g, 'continuation line has no statement to continue'],
    [/label on a continuation card is ignored/g, 'label on a continuation line is ignored'],
    [/punched record truncated to 80 columns/g, 'output record truncated to 80 columns'],
    [/\(reader is 5, printer 6, punch 7\)/g, '(use 5 for input, 6 for the printer, 7 for the output)'],
    [/bad Hollerith count/g, 'bad count in an nH literal'],
    [/\b[Cc]ards\b/g, 'lines'], [/\b[Cc]ard\b/g, 'line'], [/\b[Dd]eck\b/g, 'program'],
    [/\b[Pp]unch(ed)?\b/g, 'output'], [/\b[Rr]eader\b/g, 'input']
  ];
  function digital(msg) { return LOG_WORDS.reduce(function (m, r) { return m.replace(r[0], r[1]); }, String(msg)); }
  function renderLog(result) {
    var box = $('log'), pre = el('pre');
    box.innerHTML = '';
    pre.textContent = result.log.map(digital).concat([result.ok ? 'Job ended normally.' : 'Job ended with errors.']).join('\n');
    pre.tabIndex = 0; pre.setAttribute('aria-label', 'Job log');
    box.appendChild(pre);
  }

  /* ---------------- the program's output ---------------- */
  var OUT_BUTTONS = ['out-play', 'out-replace', 'out-append', 'out-copy', 'out-download'], SHOWN = 1000;
  function outLines() { return punched.map(function (r) { return r.replace(/ +$/, ''); }); }
  function renderOutput(list, initial) {
    punched = list.slice();
    var ol = $('records'), frag = doc.createDocumentFragment();
    ol.innerHTML = '';
    outLines().slice(0, SHOWN).forEach(function (r) { frag.appendChild(el('li', '', r || ' ')); });
    ol.appendChild(frag);
    OUT_BUTTONS.forEach(function (id) { $(id).disabled = !punched.length; });
    $('pl-load').disabled = !punched.length;
    $('out-count').textContent = plural(punched.length, 'record');
    if (initial) return;
    $('out-status').textContent = punched.length
      ? 'The program wrote ' + plural(punched.length, 'record') + ' to its output.' + (punched.length > SHOWN ? ' Only the first ' + SHOWN + ' are shown.' : '')
      : 'The program wrote nothing to its output.';
  }
  $('out-replace').addEventListener('click', function () {
    setDoc({ name: 'Output', original: outLines().join('\n'), kind: 'output records', node: null });
    Desk.open('win-editor', { focusEl: src });
    say('The output replaced the text.');
  });
  $('out-append').addEventListener('click', function () {
    src.value = trimmed(src.value.split('\n')).concat(outLines()).join('\n');
    lastCount = -1;
    Desk.open('win-editor', { focusEl: src });
    src.setSelectionRange(src.value.length, src.value.length);
    updateStatus();
    say('The output was added after the text, as ' + plural(punched.length, 'data line') + '.');
  });
  $('out-copy').addEventListener('click', function () {
    Desk.copyText(outLines().join('\n') + '\n').then(function (ok) {
      $('out-status').textContent = ok ? 'The records were copied to the clipboard.' : 'Copying failed, so please use Download instead.';
    });
  });
  $('out-download').addEventListener('click', function () {
    Desk.download(outLines().join('\n') + '\n', 'output.txt');
    $('out-status').textContent = 'The records were downloaded as output.txt.';
  });
  $('out-play').addEventListener('click', function () {
    loadTape();
    player.play();
    Desk.open('win-player', { focusEl: player.state().playing ? $('pl-pause') : $('pl-play').disabled ? rollWrap : $('pl-play') });
  });

  /* ================================================================ the Player */
  var tape = null, tapeEvents = [], tapeInfo = null, bareMode = 'rhythm';
  var roll = $('roll'), rollWrap = $('roll-wrap'), playhead = $('playhead');
  var player = Tape.createPlayer({ bpm: 120, speed: 1, onTick: onTick });
  function fmt(t) { var m = Math.floor(t / 60), s = t - m * 60; return m + ':' + (s < 10 ? '0' : '') + s.toFixed(1); }
  function loadTape() { tape = punched.slice(); $('pl-name').textContent = 'Output of ' + (jobName || 'the last job'); parseTape(); }
  function parseTape() {
    tapeInfo = Tape.parseCards(tape, { bare: bareMode });
    tapeEvents = tapeInfo.events;
    player.load(tapeEvents);
    var bare = tapeInfo.bare;
    if (bare === 0 && $('pl-bare').contains(doc.activeElement)) rollWrap.focus();
    $('pl-bare').disabled = bare === 0;
    $('pl-bare-note').textContent = bare === 0
      ? 'Off for this file: every line in it is a note record, which sets its own time and note.'
      : plural(bare, 'bare number') + ' in this file. Rhythm plays each as a time on middle C; Scale plays them one per pulse, as semitones above the C below.';
    var st = player.state();
    $('pl-status').textContent = plural(tapeEvents.length, 'note') + ' loaded, ' + plural(tapeInfo.skipped, 'line') + ' skipped. The music lasts ' + fmt(st.duration) + '.';
    $('pl-len').textContent = plural(tapeInfo.length, 'pulse');
    drawRoll();
    onTick(st);
  }
  $('pl-load').addEventListener('click', loadTape);
  $('pl-play').addEventListener('click', function () { player.play(); });
  $('pl-pause').addEventListener('click', function () { player.pause(); });
  $('pl-stop').addEventListener('click', function () { player.stop(); $('pl-status').textContent = 'Stopped and rewound to the start.'; });
  $('pl-tempo').addEventListener('input', function () { var v = +this.value; player.setTempo(v); $('pl-tempo-out').textContent = v + ' beats a minute'; });
  $$('input[name="pl-speed"]').forEach(function (r) { r.addEventListener('change', function () { player.setSpeed(+r.value); }); });
  $$('input[name="pl-bare"]').forEach(function (r) { r.addEventListener('change', function () { bareMode = r.value; if (tape) parseTape(); }); });

  // the roll: notes as outlined bars, hatched by loudness from pale blue to red, at
  // screen resolution and shown at 2x. Notes not yet played (with reduced motion) are white.
  var rollGeom = null;
  function drawRoll(progress) {
    var w = Math.max(50, Math.floor(rollWrap.clientWidth / 2)), h = Desk.narrowMQ.matches ? 75 : 95;
    roll.width = w; roll.height = h; roll.style.width = 2 * w + 'px'; roll.style.height = 2 * h + 'px';
    var ctx = roll.getContext('2d'), img = ctx.createImageData(w, h), d = img.data;
    var px = new Uint8Array(w * h).fill(7);   // colour index r<<2 | g<<1 | b; 7 is white
    var evs = tapeEvents, len = tapeInfo ? Math.max(1, tapeInfo.length) : 1, lo = 127, hi = 0;
    evs.forEach(function (e) { lo = Math.min(lo, e.note); hi = Math.max(hi, e.note); });
    if (!evs.length) { lo = 48; hi = 72; }
    lo -= 1; hi += 1;
    var rowH = (h - 6) / (hi - lo + 1), sx = (w - 4) / len;
    rollGeom = { sx: sx, len: len };
    function setPx(x, y, v) { if (x >= 0 && x < w && y >= 0 && y < h) px[y * w + x] = v; }
    for (var n = lo; n <= hi; n++) if (n % 12 === 0) {
      var yy = Math.round(h - 5 - (n - lo + 0.5) * rowH);
      for (var x = 0; x < w; x += 2) setPx(x, yy, 1);   // a blue dotted line at every C
    }
    for (var b = 0; b <= len; b += 4) for (var k = 0; k < (b % 16 ? 2 : 4); k++) setPx(2 + Math.round(b * sx), h - 1 - k, 0);
    var played = progress == null ? Infinity : progress * len;
    evs.forEach(function (e) {
      var x0 = 2 + Math.round(e.time * sx), x1 = Math.max(x0 + 1, 2 + Math.round((e.time + e.len) * sx) - 1);
      var y1 = Math.round(h - 5 - (e.note - lo) * rowH), y0 = Math.min(y1 - 1, Math.round(h - 5 - (e.note - lo + 1) * rowH) + 1);
      var solid = e.time < played, col = Px.mix3([0.6, 0.8, 1], [1, 0, 0], (e.loud - 1) / 8);
      for (var y = y0; y <= y1; y++) for (var xx = x0; xx <= x1; xx++) {
        var edge = y === y0 || y === y1 || xx === x0 || xx === x1, q = Px.rgbBits(col, xx, y);
        setPx(xx, y, edge ? 0 : solid ? (q[0] ? 4 : 0) | (q[1] ? 2 : 0) | (q[2] ? 1 : 0) : 7);
      }
    });
    for (var i = 0; i < w * h; i++) { var o = i * 4, v = px[i]; d[o] = v & 4 ? 255 : 0; d[o + 1] = v & 2 ? 255 : 0; d[o + 2] = v & 1 ? 255 : 0; d[o + 3] = 255; }
    ctx.putImageData(img, 0, 0);
  }
  var lastRollDraw = 0, wasPlaying;
  function onTick(st) {
    var playing = st.playing, dur = st.duration, pos = st.position;
    $('pl-time').textContent = fmt(pos);
    $('pl-dur').textContent = fmt(dur);
    var had = doc.activeElement;
    $('pl-play').disabled = !tapeEvents.length || playing;
    $('pl-pause').disabled = !playing;
    $('pl-stop').disabled = !tapeEvents.length || (!playing && pos === 0);
    // a transport key that just went dim hands the focus to the one that makes sense next
    if (had && had.disabled && had.closest('.transport')) (playing ? $('pl-pause') : $('pl-play').disabled ? rollWrap : $('pl-play')).focus();
    var frac = dur ? pos / dur : 0;
    if (rollGeom) {
      if (Desk.reducedMQ.matches) {
        // no moving line: notes already played fill in, a few times a second at most
        playhead.hidden = true;
        var now = Date.now();
        if (!playing || now - lastRollDraw > 300) { lastRollDraw = now; drawRoll(pos === 0 && !playing ? 0 : frac); }
      } else {
        playhead.hidden = false;
        playhead.style.transform = 'translateX(' + 2 * Math.round(2 + frac * rollGeom.len * rollGeom.sx) + 'px)';
      }
    }
    rollWrap.setAttribute('aria-valuemax', String(Math.round(dur * 10) / 10));
    rollWrap.setAttribute('aria-valuenow', String(Math.round(pos * 10) / 10));
    rollWrap.setAttribute('aria-valuetext', tapeEvents.length ? fmt(pos) + ' of ' + fmt(dur) + (playing ? ', playing' : '') : 'No notes loaded');
    if (playing !== wasPlaying) {
      if (wasPlaying !== undefined && tapeEvents.length) {
        if (playing) $('pl-status').textContent = 'Playing ' + plural(tapeEvents.length, 'note') + ' at ' + st.bpm + ' beats a minute' + (st.speed === 2 ? ', double speed.' : '.');
        else if (pos >= dur && dur > 0) $('pl-status').textContent = 'The music has ended. Press Play to hear it again.';
        else if (pos > 0) $('pl-status').textContent = 'Paused at ' + fmt(pos) + '.';
      }
      wasPlaying = playing;
    }
  }
  // the tape's own seek starts again from the top if asked to play from the very end
  function seekTo(t) { var st = player.state(); if (t >= st.duration - 0.01) { player.pause(); player.seek(st.duration); } else player.seek(t); }
  rollWrap.addEventListener('pointerdown', function (e) {
    if (!rollGeom || !tapeEvents.length) return;
    var r = roll.getBoundingClientRect(), st = player.state();
    if (st.duration) seekTo(clamp(((e.clientX - r.left) / 2 - 2) / (rollGeom.len * rollGeom.sx), 0, 1) * st.duration);
  });
  rollWrap.addEventListener('keydown', function (e) {
    var st = player.state(), t = st.position;
    if (!st.duration) return;
    var to = { ArrowRight: t + 1, ArrowUp: t + 1, ArrowLeft: t - 1, ArrowDown: t - 1, PageUp: t + 5, PageDown: t - 5, Home: 0, End: st.duration }[e.key];
    if (to === undefined) return;
    e.preventDefault();
    seekTo(clamp(to, 0, st.duration));
  });
  function frac() { var st = player.state(); return st.duration ? st.position / st.duration : 0; }
  Desk.onResize(function (w) { if (w.id === 'win-player') drawRoll(Desk.reducedMQ.matches ? frac() : null); });
  Desk.onClose('win-player', function () { player.pause(); });
  Desk.onOpen('win-player', function () { requestAnimationFrame(function () { drawRoll(); onTick(player.state()); }); });

  /* ---------------- the workspace's actions ---------------- */
  Desk.action('new', function () { openText('Untitled', '', 'FORTRAN source', 'A new, empty text.'); });
  Desk.action('open-programs', function () { Desk.open('win-programs', { focus: false }); doc.querySelector('#win-programs .icon').focus(); });
  Desk.action('select-all', function () { Desk.open('win-editor', { focusEl: src }); src.select(); });
  Desk.action('save', save);
  Desk.action('save-as', saveAs);
  Desk.action('about-box', function () { Desk.alert('A FORTRAN workspace on an eight-colour screen: an Editor and a Player, sample programs, a sieve generator and seven music programs after Iannis Xenakis, Eighty Columns, a course of ten sheets in punched cards, a Calculator, Crible, a game of sieves, and two folders of miscellanea, one of Xenakis and one of Dada.'); });
  // Escape in the text leaves it, rather than closing the Editor
  Desk.onEscape(function (e) {
    if (e.target !== src) return false;
    $('ed-run').focus();
    say('Left the text. Tab moves between the controls; Escape again closes the Editor.');
    return true;
  });

  updateStatus();
  renderOutput([], true);
  return { openText: openText, renderPrinter: renderPrinter };
})();
