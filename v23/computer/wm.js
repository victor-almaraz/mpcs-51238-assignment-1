/* The desktop: windows, icons, the menu bar, the alert and the keyboard model. It knows
   nothing of FORTRAN; the applications (workspace.js, course.js) add their own actions,
   Escape handlers and open hooks through Desk.

   Markup it expects:
     <section class="win" id="win-x" data-place="left top width [height]" [data-host="win-folder"]>
       <h2 class="title">Name</h2> ...                    the title bar is built around the h2
     <button class="icon" data-win="win-x">            opens a window (double-click with a mouse)
     <button data-act="name:arg">                       runs an action (see Desk.act)
   Windows made later (the folders, fs.js) join with Desk.addWindow.
   One screen pixel is 2 CSS pixels: every position and size is kept even. */

var Desk = (function () {
  'use strict';
  var doc = document;
  var narrowMQ = window.matchMedia('(max-width: 700px)');
  var reducedMQ = window.matchMedia('(prefers-reduced-motion: reduce)');
  function $(id) { return doc.getElementById(id); }
  function $$(sel, el) { return Array.prototype.slice.call((el || doc).querySelectorAll(sel)); }
  function el(tag, cls, text) { var e = doc.createElement(tag); if (cls) e.className = cls; if (text !== undefined) e.textContent = text; return e; }
  function clamp(v, a, b) { return v < a ? a : v > b ? b : v; }
  function ev(n) { return 2 * Math.round(n / 2); }
  function plural(n, one, many) { return n + ' ' + (n === 1 ? one : (many || one + 's')); }
  function visible(e) { return !!e && doc.contains(e) && e.getClientRects().length > 0; }

  function download(text, name) {
    var url = URL.createObjectURL(new Blob([text], { type: 'text/plain' }));
    var a = el('a'); a.href = url; a.download = name;
    doc.body.appendChild(a); a.click(); doc.body.removeChild(a);
    setTimeout(function () { URL.revokeObjectURL(url); }, 1000);
  }
  // resolves true when the text is on the clipboard
  function copyText(text) {
    function fallback() {
      var ta = el('textarea'); ta.value = text; doc.body.appendChild(ta); ta.select();
      var done = false; try { done = doc.execCommand('copy'); } catch (e) { done = false; }
      doc.body.removeChild(ta);
      return done;
    }
    if (navigator.clipboard && navigator.clipboard.writeText) return navigator.clipboard.writeText(text).then(function () { return true; }, fallback);
    return Promise.resolve(fallback());
  }

  var desktop = $('desktop');
  var wins = [];
  var z = 10, opener = {}, beforeMenu = null;
  var hooks = { open: {}, close: {}, resize: [], escape: [], icon: [], menu: [] };
  var lastPointer = 'mouse';
  doc.addEventListener('pointerdown', function (e) { lastPointer = e.pointerType || 'mouse'; }, true);

  /* ---------------- title bars ---------------- */
  function titlebar(w) {
    var h = w.querySelector('h2.title');
    if (!h.id) h.id = w.id + '-t';
    w.setAttribute('role', 'dialog'); w.setAttribute('aria-modal', 'false');
    w.setAttribute('aria-labelledby', h.id); w.tabIndex = -1;
    var bar = el('div', 'titlebar');
    var close = el('button', 'box close'), zoom = el('button', 'box zoom');
    close.type = zoom.type = 'button';
    // each box is named by its own word and the title, so the name follows a changing title
    [[close, 'Close'], [zoom, 'Zoom']].forEach(function (b) {
      var word = el('span', 'sr', b[1]); word.id = w.id + '-' + b[1].toLowerCase();
      b[0].appendChild(word); b[0].setAttribute('aria-labelledby', word.id + ' ' + h.id);
    });
    zoom.setAttribute('aria-pressed', 'false');
    w.insertBefore(bar, h);
    bar.appendChild(close); bar.appendChild(h); bar.appendChild(zoom);
    var grow = el('div', 'grow'); grow.setAttribute('aria-hidden', 'true'); w.appendChild(grow);
  }

  /* ---------------- windows ---------------- */
  function isOpen(w) { return w.classList.contains('open'); }
  function topWin() {
    var best = null;
    wins.forEach(function (w) { if (isOpen(w) && (!best || +w.style.zIndex > +best.style.zIndex)) best = w; });
    return best;
  }
  function activate(w) {
    if (+w.style.zIndex !== z || !w.classList.contains('active')) w.style.zIndex = ++z;
    wins.forEach(function (o) { o.classList.toggle('active', o === w); });
  }
  // a window's icon is in its folder when that is open, else the folder's own icon, and so
  // on out to the desk
  function iconFor(id) {
    var w = $(id), host = w && w.getAttribute('data-host'), hw = host && $(host);
    if (hw) return (isOpen(hw) && hw.querySelector('.icon[data-win="' + id + '"], [data-act="open:' + id + '"]')) || iconFor(host);
    return $$('.icon[data-win="' + id + '"]').filter(visible)[0] || null;
  }
  function iconsWidth() { var ic = doc.querySelector('.icons'); return narrowMQ.matches ? 0 : ev(ic.offsetWidth + 18); }
  function place(w) {
    var p = (w.getAttribute('data-place') || '40 40 600').split(/\s+/).map(Number);
    var dw = desktop.clientWidth, dh = desktop.clientHeight;
    // never smaller than a window's least size, even on a desk not yet laid out
    var width = ev(Math.max(240, Math.min(p[2], dw - 16))), right = dw - iconsWidth() - 8;
    w.style.width = width + 'px';
    w.style.height = p[3] ? ev(Math.max(140, (dh - 16) * p[3])) + 'px' : '';
    // clear of the icons if the window fits beside them, else as far left as it needs
    var left = p[0] + width > right ? Math.max(8, right - width) : p[0];
    w.style.left = ev(Math.max(8, Math.min(left, dw - width - 8))) + 'px';
    w.style.top = ev(p[1]) + 'px';
  }
  function fit(w) {
    if (narrowMQ.matches) return;
    var dw = desktop.clientWidth, dh = desktop.clientHeight;
    if (w.offsetHeight > dh - 8) w.style.height = ev(dh - 9) + 'px';
    w.style.left = ev(clamp(w.offsetLeft, 0, Math.max(0, dw - w.offsetWidth))) + 'px';
    w.style.top = ev(clamp(w.offsetTop, 0, Math.max(0, dh - w.offsetHeight - 4))) + 'px';
  }
  // A title is centred on the grid, not by the browser, which would split an odd margin.
  function snapTitle(w) {
    var t = w.querySelector('.title'), bar = w.querySelector('.titlebar');
    if (!t || !bar.offsetWidth) return;
    t.style.left = ev((bar.clientWidth - t.offsetWidth) / 2) + 'px';
  }
  // An icon's label is nudged by one CSS pixel when centring would put it between two
  // screen pixels; text inside it is set flush left, so every line starts on the grid.
  function snapLabels(scope) {
    $$('.ico-label', scope).forEach(function (l) {
      l.style.left = '0px';
      var x = l.getBoundingClientRect().left - l.closest('.icon').getBoundingClientRect().left;
      if (Math.round(x) % 2) l.style.left = '1px';
    });
  }
  // Auto table layout can share out an odd pixel; each column is fixed at an even width.
  function snapTables(scope) {
    $$('table', scope).forEach(function (t) {
      if (!t.offsetWidth || !t.rows.length) return;
      t.classList.remove('snapped'); t.style.width = '';
      var cells = Array.prototype.slice.call(t.rows[0].cells);
      cells.forEach(function (c) { c.style.width = ''; });
      var ws = cells.map(function (c) { return 2 * Math.ceil(c.getBoundingClientRect().width / 2); });
      cells.forEach(function (c, i) { c.style.width = ws[i] + 'px'; });
      if (t.classList.contains('fill')) cells[cells.length - 1].style.width = '';   // the last column takes the rest
      else t.style.width = ws.reduce(function (a, b) { return a + b; }, 2) + 'px';
      t.classList.add('snapped');
    });
  }
  function refresh(w) {
    snapLabels(w); snapTables(w); snapTitle(w);
    if (doc.fonts && doc.fonts.status !== 'loaded') doc.fonts.ready.then(function () { snapTables(w); snapTitle(w); });
  }

  function open(id, opts) {
    opts = opts || {};
    var w = $(id);
    if (!w) return;
    if (!isOpen(w)) {
      var from = doc.activeElement;
      if (from && from.closest && from.closest('.menubar')) from = beforeMenu;
      opener[id] = from && from !== doc.body ? from : null;
      if (hooks.open[id]) hooks.open[id](w);     // before it shows, so it opens built
      w.classList.add('open');
      if (!w._placed) { place(w); w._placed = true; }
      settle(w);
      fit(w);
      refresh(w);
    }
    activate(w);
    snapTitle(w);
    if (opts.focus !== false) (opts.focusEl || w).focus({ preventScroll: true });
    syncWindowMenu();
  }
  // whole pixels only, so the size box and the patterns never land on a half pixel
  function settle(w) { if (!narrowMQ.matches && !w.style.height) w.style.height = 2 * Math.ceil(w.getBoundingClientRect().height / 2) + 'px'; }
  // a window with no height of its own, never sized by hand, fits its content afresh next time
  function ownHeight(w) { return !!(w.getAttribute('data-place') || '').split(/\s+/)[3]; }
  function close(id) {
    var w = $(id);
    if (!w || !isOpen(w)) return;
    var hadFocus = w.contains(doc.activeElement);
    if (hooks.close[id]) hooks.close[id](w);
    w.classList.remove('open', 'active');
    if (w.classList.contains('zoomed')) unzoom(w);
    if (!ownHeight(w) && !w._sized) w.style.height = '';
    var nx = topWin();
    if (nx) activate(nx);
    if (hadFocus || doc.activeElement === doc.body) {
      var t = opener[id], ic = iconFor(id);
      // a window that was merely focused is a poorer place to return to than the icon or
      // button that opens this one (Safari does not focus buttons on click)
      if (!visible(t) || (t.classList.contains('win') && visible(ic))) t = visible(ic) ? ic : nx;
      if (t) t.focus({ preventScroll: true });
    }
    syncWindowMenu();
  }
  function unzoom(w) {
    w.style.cssText = w._unzoomed + ';z-index:' + w.style.zIndex;
    w.classList.remove('zoomed'); w.querySelector('.zoom').setAttribute('aria-pressed', 'false');
  }
  function zoom(w) {
    if (w.classList.contains('zoomed')) { unzoom(w); activate(w); }
    else {
      w._unzoomed = w.style.cssText;
      w.style.left = '6px'; w.style.top = '6px';
      w.style.width = ev(desktop.clientWidth - 12 - iconsWidth()) + 'px'; w.style.height = ev(desktop.clientHeight - 12) + 'px';
      w.classList.add('zoomed'); w.querySelector('.zoom').setAttribute('aria-pressed', 'true');
    }
    refresh(w);
  }

  // Drag by the title bar, or size by the size box: a dotted outline follows the pointer,
  // and the window takes the new place or size on release.
  function track(handle, w, start, move) {
    handle.addEventListener('pointerdown', function (e) {
      if (narrowMQ.matches || e.button !== 0 || e.target.closest('.box')) return;
      e.preventDefault();
      activate(w);
      var ghost = el('div', 'ghost'); ghost.setAttribute('aria-hidden', 'true');
      ghost.style.cssText = 'left:' + w.offsetLeft + 'px;top:' + w.offsetTop + 'px;width:' + w.offsetWidth + 'px;height:' + w.offsetHeight + 'px';
      desktop.appendChild(ghost);
      var s = start(), sx = e.clientX, sy = e.clientY;
      try { handle.setPointerCapture(e.pointerId); } catch (err) { /* synthetic pointers cannot be captured */ }
      function mv(e2) { move(s, e2.clientX - sx, e2.clientY - sy, ghost.style); }
      function up() {
        handle.removeEventListener('pointermove', mv); handle.removeEventListener('pointerup', up); handle.removeEventListener('pointercancel', up);
        ghost.remove();
        ['left', 'top', 'width', 'height'].forEach(function (k) { if (s[k] !== undefined) w.style[k] = s[k] + 'px'; });
        if (s.ow !== undefined) w._sized = true;      // sized by hand: kept
      }
      handle.addEventListener('pointermove', mv); handle.addEventListener('pointerup', up); handle.addEventListener('pointercancel', up);
    });
  }
  function wire(w) {
    w.addEventListener('pointerdown', function () { if (!w.classList.contains('active')) activate(w); });
    w.addEventListener('focusin', function () { if (!w.classList.contains('active')) activate(w); });
    w.querySelector('.close').addEventListener('click', function () { close(w.id); });
    w.querySelector('.zoom').addEventListener('click', function () { zoom(w); });
    track(w.querySelector('.titlebar'), w, function () { return { ox: w.offsetLeft, oy: w.offsetTop, left: w.offsetLeft, top: w.offsetTop }; },
      function (s, dx, dy, g) {
        s.left = ev(clamp(s.ox + dx, 40 - w.offsetWidth, desktop.clientWidth - 40));
        s.top = ev(clamp(s.oy + dy, 0, desktop.clientHeight - 24));
        g.left = s.left + 'px'; g.top = s.top + 'px';
      });
    track(w.querySelector('.grow'), w, function () { return { ow: w.offsetWidth, oh: w.offsetHeight, width: w.offsetWidth, height: w.offsetHeight }; },
      function (s, dx, dy, g) {
        s.width = ev(clamp(s.ow + dx, 240, desktop.clientWidth - w.offsetLeft));
        s.height = ev(clamp(s.oh + dy, 140, desktop.clientHeight - w.offsetTop));
        g.width = s.width + 'px'; g.height = s.height + 'px';
      });
  }
  // titles and the applications follow a window that changes size
  var ro = 'ResizeObserver' in window ? new ResizeObserver(function (entries) {
    entries.forEach(function (en) { if (!isOpen(en.target)) return; snapTitle(en.target); hooks.resize.forEach(function (f) { f(en.target); }); });
  }) : null;
  function adopt(w) { titlebar(w); wire(w); if (ro) ro.observe(w); wins.push(w); }
  $$('.win').forEach(adopt);
  function addWindow(w) { desktop.appendChild(w); adopt(w); return w; }
  function removeWindow(id) {
    var w = $(id);
    if (!w) return;
    close(id);
    if (ro) ro.unobserve(w);
    wins.splice(wins.indexOf(w), 1);
    w.remove();
    delete opener[id];
  }

  /* ---------------- icons on the desktop and in folders ---------------- */
  var selIcon = null;
  function selectIcon(b) {
    if (selIcon) selIcon.classList.remove('sel');
    selIcon = b;
    if (b) b.classList.add('sel');
  }
  function activateIcon(b) {
    if (b.hasAttribute('data-win')) open(b.getAttribute('data-win'));
    else hooks.icon.forEach(function (f) { f(b); });
  }
  // icons are found by delegation, so icons added later (the Programs) need no wiring
  doc.addEventListener('focusin', function (e) { var b = e.target.closest && e.target.closest('.icon'); if (b) selectIcon(b); });
  // Keyboard activation (detail 0), touch and narrow screens open an icon at once; a mouse
  // needs a double-click: the browser's dblclick, or two clicks on one icon within 500ms.
  // Whichever comes first opens it; the other is then ignored.
  var lastClick = { b: null, t: 0 }, opened = { b: null, t: 0 };
  function openOnce(b) {
    var now = Date.now();
    if (opened.b === b && now - opened.t < 600) return;
    opened = { b: b, t: now };
    activateIcon(b);
  }
  doc.addEventListener('click', function (e) {
    var b = e.target.closest && e.target.closest('.icon');
    if (!b) return;
    selectIcon(b);
    var now = Date.now(), twice = lastClick.b === b && now - lastClick.t < 500;
    lastClick = twice ? { b: null, t: 0 } : { b: b, t: now };
    if (e.detail === 0 || e.detail > 1 || twice || lastPointer !== 'mouse' || narrowMQ.matches) openOnce(b);
  });
  doc.addEventListener('dblclick', function (e) { var b = e.target.closest && e.target.closest('.icon'); if (b && b.tagName !== 'A') openOnce(b); });
  desktop.addEventListener('pointerdown', function (e) { if (e.target === desktop || e.target.classList.contains('icons')) selectIcon(null); });
  // arrow keys move between the icons of one group (with Option or Alt they move the icon, fs.js)
  doc.addEventListener('keydown', function (e) {
    var list = e.target.closest && e.target.closest('.icons, .folder');
    if (!list || !e.target.classList.contains('icon') || e.altKey) return;
    var k = { ArrowDown: 1, ArrowRight: 1, ArrowUp: -1, ArrowLeft: -1 }[e.key];
    if (!k && e.key !== 'Home' && e.key !== 'End') return;
    var all = $$('.icon', list.closest('[data-iconnav]') || list), i = all.indexOf(e.target);
    if (i < 0) return;
    e.preventDefault();
    all[e.key === 'Home' ? 0 : e.key === 'End' ? all.length - 1 : (i + k + all.length) % all.length].focus();
  });

  /* ---------------- the alert and the dialog ---------------- */
  // One at a time, in front of everything: the desk and the menu bar go inert behind it,
  // Tab stays inside it, Escape cancels it, and the focus goes back where it came from.
  var modal = null;
  function showModal(veil, box, focusEl, onCancel) {
    var back = doc.activeElement;
    if (!visible(back) || back.closest('.menu')) back = visible(beforeMenu) ? beforeMenu : (topWin() || doc.querySelector('.icons .icon'));
    if (modal) hideModal(false);
    modal = { veil: veil, back: back, cancel: onCancel };
    veil.classList.add('open');
    box.style.left = ev((veil.clientWidth - box.offsetWidth) / 2) + 'px';
    box.style.top = ev(Math.max(12, (veil.clientHeight - box.offsetHeight) / 2)) + 'px';
    desktop.inert = true; doc.querySelector('.menubar').inert = true;
    focusEl.focus();
  }
  function hideModal(refocus) {
    if (!modal) return;
    var m = modal;
    modal = null;
    m.veil.classList.remove('open');
    desktop.inert = false; doc.querySelector('.menubar').inert = false;
    if (refocus !== false && visible(m.back)) m.back.focus({ preventScroll: true });
  }
  $$('.alert-veil').forEach(function (veil) {
    veil.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') { e.preventDefault(); e.stopPropagation(); var c = modal && modal.cancel; hideModal(); if (c) c(); }
      else if (e.key === 'Tab') {
        var f = $$('button, input, select', veil).filter(function (x) { return !x.disabled && visible(x); }), i = f.indexOf(doc.activeElement);
        e.preventDefault();
        f[(i + (e.shiftKey ? -1 : 1) + f.length) % f.length].focus();
      }
    });
  });
  function alertBox(msg, icon) {
    var ic = $('alert-ico'); ic.setAttribute('data-icon', icon || 'note'); Px.drawIcon(ic);
    $('alert-msg').textContent = msg;
    showModal($('alert-veil'), $('alert'), $('alert-ok'));
  }
  $('alert-ok').addEventListener('click', function () { hideModal(); });
  // The dialog asks for a name, a place, or both. o = { msg, ok, name, places: [{ value,
  // label }], place }; done(name, place) returns a message to keep it open, or nothing.
  var askDone = null;
  function ask(o, done) {
    $('ask-msg').textContent = o.msg;
    $('ask-err').textContent = '';
    $('ask-ok').textContent = o.ok || 'OK';
    var nameRow = $('ask-name').parentNode, where = $('ask-where');
    nameRow.hidden = o.name == null;
    $('ask-name').value = o.name == null ? '' : o.name;
    where.innerHTML = '';
    o.places.forEach(function (p) { var op = el('option', '', p.label); op.value = p.value; where.appendChild(op); });
    where.value = o.place;
    askDone = done;
    showModal($('ask-veil'), $('ask'), o.name == null ? where : $('ask-name'));
    if (o.name != null) $('ask-name').select();
  }
  $('ask').addEventListener('submit', function (e) {
    e.preventDefault();
    var name = $('ask-name').value.trim(), err = askDone && askDone(name, $('ask-where').value);
    if (err) { $('ask-err').textContent = err; ($('ask-name').parentNode.hidden ? $('ask-where') : $('ask-name')).focus(); return; }
    hideModal();
  });
  $('ask-cancel').addEventListener('click', function () { hideModal(); });

  /* ---------------- actions shared by menus and buttons ---------------- */
  // "name" or "name:arg". The desktop's own are here; the applications add theirs.
  var actions = {
    open: function (id) { open(id); },
    // a document's own Previous and Next replace it with its neighbour
    doc: function (id, src) {
      var cur = src && src.closest('.win');
      open('win-' + id);
      if (cur && cur.hasAttribute('data-host') && cur.id !== 'win-' + id) close(cur.id);
    },
    click: function (id) { var b = $(id); if (b && !b.disabled) b.click(); },
    'open-selected': function () {
      if (selIcon && visible(selIcon)) { if (selIcon.tagName === 'A') selIcon.click(); else activateIcon(selIcon); }
      else alertBox('Select an icon on the desktop or in a folder first, then choose Open Selected Icon.');
    },
    'close-front': function () { var t = topWin(); if (t) close(t.id); },
    'close-all': function () { wins.filter(isOpen).forEach(function (w) { close(w.id); }); },
    'clean-up': function () {
      wins.forEach(function (w) { if (w.classList.contains('zoomed')) unzoom(w); w._placed = false; });
      wins.filter(isOpen).forEach(function (w) { w._sized = false; place(w); w._placed = true; settle(w); fit(w); refresh(w); });
    }
  };
  function act(a, src) {
    var i = a.indexOf(':'), k = i < 0 ? a : a.slice(0, i), arg = i < 0 ? '' : a.slice(i + 1);
    if (actions[k]) actions[k](arg, src);
  }
  doc.addEventListener('click', function (e) {
    var b = e.target.closest && e.target.closest('[data-act]');
    if (!b || b.closest('.menu') || b.disabled) return;
    act(b.getAttribute('data-act'), b);
  });

  /* ---------------- menu bar ---------------- */
  var tops = $$('.m-top'), openTop = null;
  tops.forEach(function (t, i) { t.tabIndex = i ? -1 : 0; });
  function menuOf(t) { return $(t.getAttribute('aria-controls')); }
  function enabledItems(m) { return $$('[role^="menuitem"]', m).filter(function (it) { return it.getAttribute('aria-disabled') !== 'true'; }); }
  function syncWindowMenu() {
    $$('#menu-window [data-act]').forEach(function (it) { var w = $(it.getAttribute('data-act').slice(5)), on = !!w && isOpen(w); it.classList.toggle('checked', on); it.setAttribute('aria-checked', String(on)); });
  }
  function rove(t) { tops.forEach(function (o) { o.tabIndex = o === t ? 0 : -1; }); }
  function openMenu(t, which) {
    if (openTop && openTop !== t) closeMenu(false);
    if (!openTop) { var a = doc.activeElement; if (!(a && a.closest && a.closest('.menubar'))) beforeMenu = a; }
    openTop = t; rove(t);
    t.setAttribute('aria-expanded', 'true');
    var m = menuOf(t);
    // an item mirrors a button elsewhere: it is dimmed when that button is
    $$('[data-mirror]', m).forEach(function (it) { it.setAttribute('aria-disabled', String(!!$(it.getAttribute('data-mirror')).disabled)); });
    syncWindowMenu();
    hooks.menu.forEach(function (f) { f(m); });   // an application marks its own items
    m.classList.add('open');
    m.style.left = '';
    var r = m.getBoundingClientRect(), vw = doc.documentElement.clientWidth;
    if (r.right > vw - 2) m.style.left = (m.offsetLeft - (r.right - vw + 2)) + 'px';
    if (which) { var its = enabledItems(m); (which === 'last' ? its[its.length - 1] : its[0]).focus(); }
  }
  function closeMenu(refocus) {
    if (!openTop) return;
    var t = openTop;
    openTop = null;
    t.setAttribute('aria-expanded', 'false');
    menuOf(t).classList.remove('open');
    if (refocus) t.focus();
  }
  function step(i, d) { return tops[(i + d + tops.length) % tops.length]; }
  tops.forEach(function (t, i) {
    t.addEventListener('click', function () { if (openTop === t) closeMenu(false); else openMenu(t, lastPointer === 'mouse' ? null : 'first'); });
    t.addEventListener('pointerenter', function () {
      if (!openTop || openTop === t) return;
      var hadFocus = menuOf(openTop).contains(doc.activeElement);
      openMenu(t, null);
      if (hadFocus) t.focus();
    });
    t.addEventListener('keydown', function (e) {
      var k = e.key;
      if (k === 'ArrowRight' || k === 'ArrowLeft') {
        e.preventDefault();
        var n = step(i, k === 'ArrowRight' ? 1 : -1), was = !!openTop;
        closeMenu(false); n.focus(); rove(n);
        if (was) openMenu(n, 'first');
      } else if (k === 'ArrowDown' || k === 'Enter' || k === ' ') { e.preventDefault(); openMenu(t, 'first'); }
      else if (k === 'ArrowUp') { e.preventDefault(); openMenu(t, 'last'); }
      else if (k === 'Home' || k === 'End') { e.preventDefault(); var h = tops[k === 'Home' ? 0 : tops.length - 1]; h.focus(); rove(h); }
      else if (k === 'Escape' && openTop) { e.preventDefault(); e.stopPropagation(); closeMenu(true); }
    });
    var m = menuOf(t);
    m.addEventListener('keydown', function (e) {
      var its = enabledItems(m), j = its.indexOf(doc.activeElement), k = e.key;
      if (k === 'ArrowDown' || k === 'ArrowUp') { e.preventDefault(); its[(j + (k === 'ArrowDown' ? 1 : -1) + its.length) % its.length].focus(); }
      else if (k === 'Home' || k === 'End') { e.preventDefault(); its[k === 'Home' ? 0 : its.length - 1].focus(); }
      else if (k === 'ArrowRight' || k === 'ArrowLeft') { e.preventDefault(); openMenu(step(i, k === 'ArrowRight' ? 1 : -1), 'first'); }
      else if (k === 'Escape') { e.preventDefault(); e.stopPropagation(); closeMenu(true); }
      else if (k === 'Tab') closeMenu(false);
    });
    // by delegation, so items added later (the folders in the Window menu) need no wiring
    function itemOf(e) { var it = e.target.closest('[role^="menuitem"]'); return it && m.contains(it) ? it : null; }
    m.addEventListener('pointerover', function (e) { var it = itemOf(e); if (it && it !== doc.activeElement && it.getAttribute('aria-disabled') !== 'true') it.focus({ preventScroll: true }); });
    m.addEventListener('click', function (e) {
      var it = itemOf(e);
      if (!it) return;
      if (it.tagName === 'A') { closeMenu(false); return; }
      if (it.getAttribute('aria-disabled') === 'true') return;
      var back = beforeMenu;
      closeMenu(false);
      var before = doc.activeElement;
      act(it.getAttribute('data-act'), it);
      // if the action did not move focus, put it back where it was before the menu opened
      if (doc.activeElement === before || doc.activeElement === doc.body) { if (modal) return; if (visible(back)) back.focus({ preventScroll: true }); else t.focus(); }
    });
  });
  doc.addEventListener('pointerdown', function (e) { if (openTop && !e.target.closest('.menubar')) closeMenu(false); });

  /* ---------------- Escape: an application may claim it first, then it closes the front window ---------------- */
  doc.addEventListener('keydown', function (e) {
    if (e.key !== 'Escape' || e.defaultPrevented || modal) return;
    if (openTop) { closeMenu(true); return; }
    for (var i = 0; i < hooks.escape.length; i++) if (hooks.escape[i](e)) { e.preventDefault(); return; }
    var t = topWin();
    if (t) { e.preventDefault(); close(t.id); }
  });

  /* ---------------- the grid ---------------- */
  // Scrolling moves content by whole screen pixels only.
  doc.addEventListener('scroll', function (e) {
    var t = e.target;
    if (!t || t === doc) return;
    if (Math.round(t.scrollTop) % 2) t.scrollTop = Math.round(t.scrollTop) - 1;
    if (Math.round(t.scrollLeft) % 2) t.scrollLeft = Math.round(t.scrollLeft) - 1;
  }, true);
  // the bitmap faces change every text width once they arrive, so everything is re-snapped then
  function snapAll() { snapLabels(doc); wins.filter(isOpen).forEach(function (w) { snapTitle(w); snapTables(w); }); }
  if (doc.fonts && doc.fonts.ready) doc.fonts.ready.then(snapAll);
  narrowMQ.addEventListener('change', function () { wins.filter(isOpen).forEach(function (w) { if (!narrowMQ.matches) fit(w); w._placed = false; }); snapAll(); });
  // the desk picture, on whole screen pixels: the beams meet right of centre, in the space
  // between the first windows and the icons
  var desk = $('desktop');
  function placeDesk() {
    var x = desk.clientWidth * 0.65 - 800, y = (desk.clientHeight - 1140) * 0.5;
    desk.style.backgroundPosition = 2 * Math.round(x / 2) + 'px ' + 2 * Math.round(y / 2) + 'px';
  }
  placeDesk();
  window.addEventListener('resize', function () { placeDesk(); if (!narrowMQ.matches) wins.filter(isOpen).forEach(fit); });

  /* ---------------- clock ---------------- */
  function tick() {
    var d = new Date(), h = d.getHours() % 12 || 12, m = d.getMinutes();
    $('clock').textContent = h + ':' + (m < 10 ? '0' : '') + m + (d.getHours() < 12 ? ' AM' : ' PM');
  }
  tick(); setInterval(tick, 20000);
  $$('canvas[data-icon]').forEach(Px.drawIcon);

  return {
    $: $, $$: $$, el: el, clamp: clamp, ev: ev, plural: plural, visible: visible, download: download, copyText: copyText,
    narrowMQ: narrowMQ, reducedMQ: reducedMQ,
    open: open, close: close, isOpen: isOpen, topWin: topWin, alert: alertBox, ask: ask, act: act,
    addWindow: addWindow, removeWindow: removeWindow, refresh: refresh,
    selected: function () { return selIcon; }, selectIcon: selectIcon, snapLabels: snapLabels,
    // the applications' ways in
    action: function (name, fn) { actions[name] = fn; },
    onOpen: function (id, fn) { hooks.open[id] = fn; },
    onClose: function (id, fn) { hooks.close[id] = fn; },
    onResize: function (fn) { hooks.resize.push(fn); },
    onEscape: function (fn) { hooks.escape.push(fn); },
    onIcon: function (fn) { hooks.icon.push(fn); },
    onMenu: function (fn) { hooks.menu.push(fn); }
  };
})();
