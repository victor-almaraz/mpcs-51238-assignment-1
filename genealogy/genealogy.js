/* The genealogy's tree, drawn from scripts/versions.js on graph paper and read from left to
   right: each room a small print (assets/rooms/vNN-s.png, two CSS pixels to its pixel) in the
   column of its generation (one after the latest of the rooms it builds on), the prints in a
   column ordered beside their parents so the lines cross as little as they can, the work's
   chapters (CHAPTERS) named over their columns. Lines run at right angles from each room to the
   rooms made from it: full where one builds on it, dashed where one took a part from it, each
   room's lines along a lane of its own in the gap. Pointing at a print lights its whole line,
   every room it came from and every room that came from it, and shows its label. The tree is a
   picture of the lineage written out under it, so it is hidden from screen readers; the
   lineage's entries light it too, as they take the pointer or the focus. */
(function () {
  'use strict';
  var tree = document.getElementById('tree');
  if (!tree || !window.VERSIONS) return;
  var NW = 104, NH = 68, GAP = 44, VGAP = 12, TOP = 92, SIDE = 8, BOTTOM = 16;
  var byId = {};
  VERSIONS.forEach(function (v) { byId[v.id] = v; });
  function even(n) { return Math.round(n / 2) * 2; }
  function no(id) { return 'No. ' + id.slice(1); }

  // generations: one after the latest parent
  function gen(v) { if (v.gen === undefined) v.gen = v.parents.length ? 1 + Math.max.apply(null, v.parents.map(function (p) { return gen(byId[p]); })) : 0; return v.gen; }
  VERSIONS.forEach(gen);
  var cols = [];
  VERSIONS.forEach(function (v) { (cols[v.gen] = cols[v.gen] || []).push(v); });
  var tallest = Math.max.apply(null, cols.map(function (c) { return c.length; }));
  var height = TOP + tallest * NH + (tallest - 1) * VGAP + BOTTOM, width = SIDE * 2 + cols.length * NW + (cols.length - 1) * GAP;
  tree.style.width = width + 'px'; tree.style.height = height + 'px';

  // each column ordered by where its rooms' parents stand (their mean), then centred
  cols.forEach(function (col, g) {
    if (g > 0) {
      col.forEach(function (v, i) { var ps = v.parents.map(function (p) { return byId[p].cy; }); v.key = ps.reduce(function (a, b) { return a + b; }, 0) / ps.length + i * 0.01; });
      col.sort(function (a, b) { return a.key - b.key; });
    }
    var span = col.length * NH + (col.length - 1) * VGAP, y0 = TOP + (height - TOP - BOTTOM - span) / 2;
    col.forEach(function (v, i) { v.x = even(SIDE + g * (NW + GAP)); v.y = even(y0 + i * (NH + VGAP)); v.cy = v.y + NH / 2; });
  });

  // the chapters: a band behind each one's columns, its numeral and name over them
  (window.CHAPTERS || []).forEach(function (c, k) {
    var gs = VERSIONS.filter(function (v) { return v.id >= c.first && v.id <= c.last; }).map(function (v) { return v.gen; });
    var g0 = Math.min.apply(null, gs), g1 = Math.max.apply(null, gs);
    var x0 = even(g0 * (NW + GAP) + SIDE - (g0 ? GAP / 2 : SIDE)), x1 = even(g1 * (NW + GAP) + SIDE + NW + (g1 < cols.length - 1 ? GAP / 2 : SIDE));
    var band = document.createElement('div');
    band.className = 'band' + (k % 2 ? ' alt' : ''); band.style.left = x0 + 'px'; band.style.width = (x1 - x0) + 'px';
    band.innerHTML = '<span class="cn"></span><span class="ct"></span>';
    band.firstChild.textContent = c.numeral; band.lastChild.textContent = c.title;
    tree.appendChild(band);
  });

  // the lines: out of the parent's right side along its lane in the gap, along the lane to the
  // child's height, and into the child's left side; a part taken from a room in the same column
  // runs out to the lane and back into the child's right side
  var NS = 'http://www.w3.org/2000/svg', svg = document.createElementNS(NS, 'svg');
  svg.setAttribute('width', width); svg.setAttribute('height', height);
  var lanes = {};
  cols.forEach(function (col) {
    var givers = col.filter(function (p) { return VERSIONS.some(function (v) { return v.parents.concat(v.borrows).indexOf(p.id) >= 0; }); });
    var step = givers.length > 1 ? (GAP - 16) / (givers.length - 1) : 0;
    givers.forEach(function (p, i) { lanes[p.id] = even(p.x + NW + 8 + i * step); });
  });
  var lines = [];
  VERSIONS.forEach(function (v) {
    var links = v.parents.map(function (p) { return [p, false]; }).concat(v.borrows.map(function (b) { return [b, true]; }));
    links.forEach(function (link, k) {
      var p = byId[link[0]], dashed = link[1], lx = lanes[p.id], py = even(p.cy + (dashed ? 8 : 0));
      var cy = even(v.cy + (k - (links.length - 1) / 2) * 8), pts;
      if (p.gen === v.gen) pts = [p.x + NW, py, lx, py, lx, cy, v.x + NW, cy];
      else pts = [p.x + NW, py, lx, py, lx, cy, v.x, cy];
      var l = document.createElementNS(NS, 'polyline');
      l.setAttribute('points', pts.join(' '));
      l.setAttribute('fill', 'none'); l.setAttribute('stroke', dashed ? '#b5462b' : '#1e1d1b'); l.setAttribute('stroke-width', '2');
      if (dashed) l.setAttribute('stroke-dasharray', '6 4');
      l.dataset.from = v.id; l.dataset.to = p.id;
      svg.appendChild(l); lines.push(l);
    });
  });
  tree.appendChild(svg);

  // the prints, each a way into its room, its number on a tag at its corner
  VERSIONS.forEach(function (v) {
    var a = document.createElement('a');
    a.className = 'node'; a.href = '../' + v.id + '/'; a.tabIndex = -1; a.dataset.id = v.id; a.dataset.status = v.status;
    a.style.left = v.x + 'px'; a.style.top = v.y + 'px';
    a.innerHTML = '<img width="48" height="30" alt=""><b></b>';
    a.firstChild.src = '../assets/rooms/' + v.id + '-s.png';
    a.lastChild.textContent = v.id.slice(1);
    tree.appendChild(a); v.el = a;
  });

  // the label, beside the print pointed at: its number, its name, what it is and where it came from
  var tag = document.createElement('div');
  tag.className = 'tag'; tag.hidden = true;
  tag.innerHTML = '<b></b><span class="tt"></span><span class="tn"></span><span class="tf"></span>';
  tree.appendChild(tag);
  function from(v) {
    var s = v.parents.length ? 'From ' + v.parents.map(no).join(' and ') : '';
    if (v.borrows.length) s += (s ? ', with a part of ' : 'With a part of ') + v.borrows.map(no).join(' and ');
    return s ? s + '.' : 'The first room.';
  }
  function label(v) {
    if (!v) { tag.hidden = true; return; }
    var parts = tag.children;
    parts[0].textContent = no(v.id); parts[1].textContent = v.title; parts[2].textContent = v.note; parts[3].textContent = from(v);
    tag.hidden = false;
    var right = v.x + NW + 14, w = tag.offsetWidth;
    tag.style.left = (right + w > width ? v.x - 14 - w : right) + 'px';
    tag.style.top = Math.max(TOP, Math.min(height - tag.offsetHeight - 4, v.y - 6)) + 'px';
  }

  // a room's line: everything it came from and everything that came from it
  function up(id, out) { if (out[id]) return out; out[id] = 1; var v = byId[id]; v.parents.concat(v.borrows).forEach(function (p) { up(p, out); }); return out; }
  function down(id, out) { out[id] = 1; VERSIONS.forEach(function (v) { if (!out[v.id] && v.parents.concat(v.borrows).indexOf(id) >= 0) down(v.id, out); }); return out; }
  function light(id) {
    label(id && byId[id]);
    if (!id) { tree.classList.remove('lit'); VERSIONS.forEach(function (v) { v.el.classList.remove('on', 'here'); }); lines.forEach(function (l) { l.classList.remove('on'); }); return; }
    var a = up(id, {}), d = down(id, {}), on = {};
    Object.keys(a).concat(Object.keys(d)).forEach(function (k) { on[k] = 1; });
    tree.classList.add('lit');
    VERSIONS.forEach(function (v) { v.el.classList.toggle('on', !!on[v.id]); v.el.classList.toggle('here', v.id === id); });
    lines.forEach(function (l) { l.classList.toggle('on', !!((a[l.dataset.from] && a[l.dataset.to]) || (d[l.dataset.from] && d[l.dataset.to]))); });
  }
  tree.addEventListener('pointerover', function (e) { var n = e.target.closest('.node'); light(n && n.dataset.id); });
  tree.addEventListener('pointerleave', function () { light(null); });
  Array.prototype.forEach.call(document.querySelectorAll('.lineage li'), function (li) {
    var id = li.id.replace('l-', '');
    li.addEventListener('pointerenter', function () { light(id); });
    li.addEventListener('pointerleave', function () { light(null); });
    li.addEventListener('focusin', function () { light(id); });
    li.addEventListener('focusout', function () { light(null); });
  });
  // come here from a room's print in the gallery, its line already lit
  var at = /^#l-(v\d\d)$/.exec(location.hash);
  if (at && byId[at[1]]) {
    light(at[1]); document.getElementById('l-' + at[1]).classList.add('here');
    addEventListener('load', function () { tree.parentNode.scrollIntoView({ block: 'start' }); });
  }
})();
