/* The room: its stations, one in front at a time, and what every object shares.

   Desk.go(name, focusEl)          brings a station to the front (focus to its heading)
   Desk.onShow(name, fn)           fn(section) each time the station is shown
   Desk.pager(box, items, status, label, buttons)   pages that turn, in a book or a magazine
   Desk.deck(id) / Desk.decks      every deck in the tray, by id
   Any button with data-go="station" moves there (data-chapter="i" opens the manual at
   that chapter, data-focus="id" focuses that element); any with data-deck="id" puts that
   deck on the coding form (form.js registers Desk.putOnForm). */

var Desk = (function () {
  'use strict';
  var doc = document;
  function $(id) { return doc.getElementById(id); }
  function $$(sel, el) { return Array.prototype.slice.call((el || doc).querySelectorAll(sel)); }
  function plural(n, one, many) { return n + ' ' + (n === 1 ? one : (many || one + 's')); }

  /* ---------------- the decks: the engine's samples, the music decks, the magazine's ---------------- */
  function slug(n) { return n.toLowerCase().replace(/\(.*?\)/g, '').replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, ''); }
  var decks = Fortran.samples.map(function (s) { return { id: slug(s.name), name: s.name, cards: s.cards, section: 'programs' }; })
    .concat(DECKS.music.map(function (d) { return { id: d.id, name: d.name, cards: d.cards, section: 'music' }; }))
    .concat(DECKS.magazine.map(function (d) { return { id: d.id, name: d.name, cards: d.cards, section: 'magazine' }; }));
  var byId = {};
  decks.forEach(function (d) { byId[d.id] = d; });

  /* ---------------- stations ---------------- */
  var stations = {}, shown = {}, current = 'desk';
  $$('[data-station]').forEach(function (s) { stations[s.getAttribute('data-station')] = s; });
  function heading(name) { return stations[name].querySelector('[tabindex="-1"]'); }

  // Each thing in the room grows into its station and shrinks back into its place: the
  // thing and the station's main object share one view-transition name for the change.
  // MORPH[station] is [the open object, the thing in the room].
  var MORPH = {
    manual: ['.spread', '.spine.v1'], magazine: ['#mag', '.o-mag .mini-mag'], portfolio: ['.folio-inside', '.o-folio .folders'],
    form: ['.pad-sheet', '.o-form .clipboard'], out: ['.fanfold', '.o-out .outtray'], recorder: ['.recorder', '.o-tape .player']
  };
  var REDUCED = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var LIST = window.matchMedia('(max-width: 879px), (max-height: 560px)');   // the room drawn as a list: nothing to grow from
  var openedFrom = {};                 // the thing in the room each station was last opened from
  function smallOf(name) {
    var b = openedFrom[name];
    if (b) return b.matches('.spine') ? b : b.querySelector('span');
    return MORPH[name] ? doc.querySelector(MORPH[name][1]) : null;
  }
  function bigOf(name) {
    var b = openedFrom[name];
    if (b && b.matches('.o-box')) return stations[name].querySelector('.tray');
    return MORPH[name] ? stations[name].querySelector(MORPH[name][0]) : null;
  }
  function seen(e) { return !!e && e.getClientRects().length > 0; }

  // go(name, focusEl, after, src): after() runs once the station is in front; src is the
  // button that asked, so a thing in the room is remembered as the station's way in
  function go(name, focusEl, after, src) {
    if (!stations[name]) return;
    var from = current;
    if (src && src.closest('.scene') && name !== 'desk') openedFrom[name] = src;
    // back in the room, the focus returns to the thing the station was opened from
    if (name === 'desk' && !focusEl) focusEl = openedFrom[from] || doc.querySelector('.overview [data-go="' + from + '"]');
    function apply() { show(name, focusEl); if (after) after(); }
    if (!doc.startViewTransition || REDUCED || from === name || LIST.matches) { apply(); return; }
    var opening = name !== 'desk', st = opening ? name : from;
    var a = opening ? smallOf(st) : bigOf(st), b = null;
    if (!MORPH[st] || !seen(a)) { apply(); return; }
    a.style.viewTransitionName = 'thing';
    var t = doc.startViewTransition(function () {
      a.style.viewTransitionName = '';
      apply();
      b = opening ? bigOf(st) : smallOf(st);
      if (seen(b)) b.style.viewTransitionName = 'thing';
    });
    // a transition the browser skips (a hidden tab, a second one begun) still makes the change
    t.ready.catch(function () {});
    if (t.updateCallbackDone) t.updateCallbackDone.catch(function () {});
    t.finished.then(function () { a.style.viewTransitionName = ''; if (b) b.style.viewTransitionName = ''; }, function () {});
  }
  function show(name, focusEl) {
    Object.keys(stations).forEach(function (k) { stations[k].hidden = k !== name; });
    $$('.labels [data-go]').forEach(function (b) {
      if (b.getAttribute('data-go') === name) b.setAttribute('aria-current', 'true');
      else b.removeAttribute('aria-current');
    });
    menu(false);
    doc.querySelector('.to-room').hidden = name === 'desk';
    current = name;
    $('desk').setAttribute('data-at', name);    // the room straight on, or the desk from above
    stations[name].scrollTop = 0;
    (shown[name] || []).forEach(function (fn) { fn(stations[name]); });
    (focusEl || heading(name)).focus({ preventScroll: true });
  }
  function onShow(name, fn) { (shown[name] = shown[name] || []).push(fn); if (current === name) fn(stations[name]); }

  doc.addEventListener('click', function (e) {
    var b = e.target.closest && e.target.closest('[data-go], [data-deck]');
    if (!b || b.disabled) return;
    if (b.hasAttribute('data-go')) {
      var at = b.getAttribute('data-focus'), ch = b.getAttribute('data-chapter');
      go(b.getAttribute('data-go'), at && $(at), ch === null ? null : function () { manualPages.show(+ch, true); }, b);
    }
    else if (api.putOnForm) api.putOnForm(b.getAttribute('data-deck'));
  });
  /* ---------------- the menu in the corner ---------------- */
  var menuBtn = $('menu-btn'), places = $('places');
  function menu(open) {
    if (places.hidden === !open) return;
    places.hidden = !open;
    menuBtn.setAttribute('aria-expanded', String(open));
  }
  menuBtn.addEventListener('click', function () {
    menu(places.hidden);
    if (!places.hidden) places.querySelector('[aria-current="true"]').focus();
  });
  // a click elsewhere closes it; so does Escape, which hands the focus back to the button
  doc.addEventListener('pointerdown', function (e) { if (!places.hidden && !e.target.closest('.drawer')) menu(false); });
  places.addEventListener('keydown', function (e) {
    var items = $$('.label, .back a', places), i = items.indexOf(doc.activeElement);
    if (e.key === 'Escape') { e.preventDefault(); menu(false); menuBtn.focus(); }
    else if (e.key === 'ArrowDown' || e.key === 'ArrowUp') { e.preventDefault(); items[(i + (e.key === 'ArrowDown' ? 1 : -1) + items.length) % items.length].focus(); }
  });
  places.addEventListener('focusout', function (e) { if (!e.relatedTarget || !e.relatedTarget.closest('.drawer')) menu(false); });

  // Escape puts the object down and returns to the room, except while typing
  doc.addEventListener('keydown', function (e) {
    if (e.key !== 'Escape' || current === 'desk' || e.defaultPrevented) return;
    if (e.target.matches('input[type="text"], textarea, select')) return;
    e.preventDefault();
    go('desk');
  });

  /* ---------------- pages that turn ---------------- */
  // items are pages (each with an h3 for focus); box holds the data-turn buttons; buttons,
  // if given, are an index, one per page. onTurn(i) runs after each turn.
  function pager(box, items, statusEl, label, buttons, onTurn) {
    var at = 0;
    buttons = buttons || [];
    function show(i, focus) {
      at = Math.max(0, Math.min(items.length - 1, i));
      items.forEach(function (it, k) { it.hidden = k !== at; });
      buttons.forEach(function (b, k) { if (k === at) b.setAttribute('aria-current', 'page'); else b.removeAttribute('aria-current'); });
      box.querySelector('[data-turn="-1"]').disabled = at === 0;
      box.querySelector('[data-turn="1"]').disabled = at === items.length - 1;
      statusEl.textContent = label + ' ' + (at + 1) + ' of ' + items.length;
      var scroller = items[at].parentNode;
      if (scroller) scroller.scrollTop = 0;
      if (onTurn) onTurn(at, items[at]);
      if (focus) items[at].querySelector('h3').focus({ preventScroll: true });
    }
    buttons.forEach(function (b, k) { b.addEventListener('click', function () { show(k, true); }); });
    $$('[data-turn]', box).forEach(function (b) {
      b.addEventListener('click', function () {
        show(at + Number(b.getAttribute('data-turn')), false);
        // the far button takes the focus when this one runs out of pages
        if (b.disabled) box.querySelector('[data-turn="' + (-Number(b.getAttribute('data-turn'))) + '"]').focus();
      });
    });
    box.addEventListener('keydown', function (e) {
      if (e.key !== 'ArrowLeft' && e.key !== 'ArrowRight') return;
      var t = e.target;
      if (t.matches('input, select, textarea, summary') || t.closest('pre, .art')) return;
      e.preventDefault();
      show(at + (e.key === 'ArrowLeft' ? -1 : 1), false);
    });
    show(0, false);
    return { show: show };
  }

  /* ---------------- the manual and the portfolio ---------------- */
  // the manual's three volumes share one contents, grouped by volume
  var VOLUMES = { 1: 'FORTRAN', 2: 'Sieves', 3: 'Music and tape' };
  var manualPages = (function manual() {
    var box = $('manual'), chapters = $$('.chapter', box), list = $('contents'), group = null, vol = null;
    var buttons = chapters.map(function (ch) {
      var v = ch.getAttribute('data-volume');
      if (v !== vol) {
        vol = v;
        var gl = doc.createElement('li'), h = doc.createElement('span');
        gl.className = 'vol'; gl.setAttribute('data-volume', v);
        h.className = 'vol-h'; h.textContent = 'Volume ' + v + ': ' + VOLUMES[v];
        group = doc.createElement('ol');
        gl.appendChild(h); gl.appendChild(group); list.appendChild(gl);
      }
      var li = doc.createElement('li'), b = doc.createElement('button');
      b.type = 'button'; b.textContent = ch.querySelector('h3').textContent;
      li.appendChild(b); group.appendChild(li);
      return b;
    });
    return pager(box, chapters, $('manual-page'), 'Page', buttons);
  })();
  (function portfolio() {
    var box = $('folio'), sheets = $$('.sheet', box);
    // a sheet's drawings are set in the first time it is shown, from drawings.js
    function fill(i, sheet) {
      $$('.drawing-slot[data-drawing]', sheet).forEach(function (slot) {
        slot.outerHTML = DRAWINGS[slot.getAttribute('data-drawing')];
      });
    }
    pager(box, sheets, $('folio-page'), 'Sheet', $$('button', $('folio-index')), fill);
  })();

  var api = {
    go: go, onShow: onShow, pager: pager, current: function () { return current; },
    decks: decks, deck: function (id) { return byId[id]; },
    $: $, $$: $$, plural: plural,
    putOnForm: null
  };
  return api;
})();
