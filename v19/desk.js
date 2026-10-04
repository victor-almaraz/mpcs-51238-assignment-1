/* The desk: its stations, one in front at a time, and what every object shares.

   Desk.go(name, focusEl)          brings a station to the front (focus to its heading)
   Desk.onShow(name, fn)           fn(section) each time the station is shown
   Desk.pager(box, items, status, label, buttons)   pages that turn, in a book or a magazine
   Desk.deck(id) / Desk.decks      every deck in the tray, by id
   Any button with data-go="station" moves there; any with data-deck="id" puts that deck
   on the coding form (form.js registers Desk.putOnForm). */

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
  function go(name, focusEl) {
    if (!stations[name]) return;
    Object.keys(stations).forEach(function (k) { stations[k].hidden = k !== name; });
    $$('.labels [data-go]').forEach(function (b) {
      if (b.getAttribute('data-go') === name) {
        b.setAttribute('aria-current', 'true');
        b.scrollIntoView({ block: 'nearest', inline: 'nearest' });   // keeps it in view in the narrow strip
      } else b.removeAttribute('aria-current');
    });
    current = name;
    $('desk').setAttribute('data-at', name);    // shows the props left round this station
    stations[name].scrollTop = 0;
    (shown[name] || []).forEach(function (fn) { fn(stations[name]); });
    (focusEl || heading(name)).focus({ preventScroll: true });
  }
  function onShow(name, fn) { (shown[name] = shown[name] || []).push(fn); if (current === name) fn(stations[name]); }

  doc.addEventListener('click', function (e) {
    var b = e.target.closest && e.target.closest('[data-go], [data-deck]');
    if (!b || b.disabled) return;
    if (b.hasAttribute('data-go')) go(b.getAttribute('data-go'));
    else if (api.putOnForm) api.putOnForm(b.getAttribute('data-deck'));
  });
  // Escape puts the object down and returns to the desk, except while typing
  doc.addEventListener('keydown', function (e) {
    if (e.key !== 'Escape' || current === 'desk' || e.defaultPrevented) return;
    if (e.target.matches('input[type="text"], textarea, select')) return;
    var from = current;
    e.preventDefault();
    go('desk', doc.querySelector('.overview [data-go="' + from + '"]'));
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
  (function manual() {
    var box = $('manual'), chapters = $$('.chapter', box), list = $('contents');
    var buttons = chapters.map(function (ch) {
      var li = doc.createElement('li'), b = doc.createElement('button');
      b.type = 'button'; b.textContent = ch.querySelector('h3').textContent;
      li.appendChild(b); list.appendChild(li);
      return b;
    });
    pager(box, chapters, $('manual-page'), 'Page', buttons);
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
