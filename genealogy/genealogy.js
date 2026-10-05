/* The genealogy's tree, drawn from scripts/versions.js on graph paper: each room a card in the
   row of its generation (one below the deepest of the rooms it builds on), the rooms in a row
   ordered under their parents so the lines cross as little as they can, and lines from each
   room up to the ones it builds on (full) or took a part from (dashed), run at right angles
   on the paper's grid in whole two-pixel steps. Pointing at a card, or focusing one, lights its
   whole line: every room it came from and every room that came from it. The tree is a picture
   of the lineage written out under it, so it is hidden from screen readers. */
(function () {
  'use strict';
  var tree = document.getElementById('tree');
  if (!tree || !window.VERSIONS) return;
  var NW = 128, NH = 84, GAP = 12, ROW = 140, LINE = 112, TOP = 24, SIDE = 24, MAX = 6;
  var byId = {};
  VERSIONS.forEach(function (v) { byId[v.id] = v; });

  // generations: one below the deepest parent
  function gen(v) { if (v.gen === undefined) v.gen = v.parents.length ? 1 + Math.max.apply(null, v.parents.map(function (p) { return gen(byId[p]); })) : 0; return v.gen; }
  VERSIONS.forEach(gen);
  var rows = [];
  VERSIONS.forEach(function (v) { (rows[v.gen] = rows[v.gen] || []).push(v); });

  // order each row under its parents (the mean of their places), then space it evenly; a
  // generation of more than MAX rooms runs on to a second line under the first
  var widest = Math.min(MAX, Math.max.apply(null, rows.map(function (r) { return r.length; })));
  var width = SIDE * 2 + widest * NW + (widest - 1) * GAP;
  function even(n) { return Math.round(n / 2) * 2; }
  var y = TOP;
  rows.forEach(function (row, g) {
    if (g > 0) {
      row.forEach(function (v, i) { var ps = v.parents.map(function (p) { return byId[p].x; }); v.key = ps.reduce(function (a, b) { return a + b; }, 0) / ps.length + i * 0.01; });
      row.sort(function (a, b) { return a.key - b.key; });
    }
    var lines = Math.ceil(row.length / MAX), per = Math.ceil(row.length / lines);
    for (var k = 0; k < lines; k++) {
      var part = row.slice(k * per, (k + 1) * per), span = part.length * NW + (part.length - 1) * GAP, x0 = (width - span) / 2;
      part.forEach(function (v, i) { v.x = even(x0 + i * (NW + GAP)); v.y = even(y); });
      y += k < lines - 1 ? LINE : ROW;
    }
  });
  var height = y - ROW + NH + TOP;
  tree.style.width = width + 'px'; tree.style.height = height + 'px';

  // the lines, at right angles: up from the child, across just under the parent, up into it
  // (the cards are laid over the lines, so a line passing behind a card is hidden by it)
  var NS = 'http://www.w3.org/2000/svg', svg = document.createElementNS(NS, 'svg');
  svg.setAttribute('width', width); svg.setAttribute('height', height);
  var lines = [];
  VERSIONS.forEach(function (v) {
    [['parents', false], ['borrows', true]].forEach(function (kind) {
      v[kind[0]].forEach(function (pid, k) {
        var p = byId[pid], cx = v.x + NW / 2 + (k - (v[kind[0]].length - 1) / 2) * 16 + (kind[1] ? 8 : 0);
        var px = p.x + NW / 2 + (kind[1] ? 8 : 0), mid = even(p.y + NH + 12 + (kind[1] ? 8 : 0));      // across just under the parent
        var l = document.createElementNS(NS, 'polyline');
        l.setAttribute('points', [even(cx), v.y, even(cx), mid, even(px), mid, even(px), p.y + NH].join(' '));
        l.setAttribute('fill', 'none'); l.setAttribute('stroke', kind[1] ? '#b5462b' : '#1e1d1b'); l.setAttribute('stroke-width', '2');
        if (kind[1]) l.setAttribute('stroke-dasharray', '6 4');
        l.dataset.from = v.id; l.dataset.to = pid;
        svg.appendChild(l); lines.push(l);
      });
    });
  });
  tree.appendChild(svg);

  // the cards, each a way into its room
  VERSIONS.forEach(function (v) {
    var a = document.createElement('a');
    a.className = 'node'; a.href = '../' + v.id + '/'; a.tabIndex = -1; a.dataset.id = v.id; a.dataset.status = v.status;
    a.style.left = v.x + 'px'; a.style.top = v.y + 'px';
    a.innerHTML = '<b></b><span></span>';
    a.firstChild.textContent = 'No. ' + v.id.slice(1); a.lastChild.textContent = v.title;
    a.title = v.title + (v.status !== 'complete' ? ' (in progress)' : '');
    tree.appendChild(a); v.el = a;
  });

  // a room's line: everything it came from and everything that came from it
  function up(id, out) { if (out[id]) return out; out[id] = 1; var v = byId[id]; v.parents.concat(v.borrows).forEach(function (p) { up(p, out); }); return out; }
  function down(id, out) { out[id] = 1; VERSIONS.forEach(function (v) { if (!out[v.id] && v.parents.concat(v.borrows).indexOf(id) >= 0) down(v.id, out); }); return out; }
  function light(id) {
    if (!id) { tree.classList.remove('lit'); VERSIONS.forEach(function (v) { v.el.classList.remove('on'); }); lines.forEach(function (l) { l.classList.remove('on'); }); return; }
    var a = up(id, {}), d = down(id, {}), on = {};
    Object.keys(a).concat(Object.keys(d)).forEach(function (k) { on[k] = 1; });
    tree.classList.add('lit');
    VERSIONS.forEach(function (v) { v.el.classList.toggle('on', !!on[v.id]); });
    lines.forEach(function (l) { l.classList.toggle('on', (a[l.dataset.from] && a[l.dataset.to]) || (d[l.dataset.from] && d[l.dataset.to])); });
  }
  tree.addEventListener('pointerover', function (e) { var n = e.target.closest('.node'); light(n && n.dataset.id); });
  tree.addEventListener('pointerleave', function () { light(null); });
  // the lineage written out lights the tree too, as its entries take the focus or the pointer
  Array.prototype.forEach.call(document.querySelectorAll('.lineage li'), function (li) {
    var id = li.id.replace('l-', '');
    li.addEventListener('pointerenter', function () { light(id); });
    li.addEventListener('pointerleave', function () { light(null); });
    li.addEventListener('focusin', function () { light(id); });
    li.addEventListener('focusout', function () { light(null); });
  });
})();
