/* The file system: a model of the disk, held in memory for the session and gone when the
   page is closed. Every folder, document, program and application is a node in one tree,
   and everything that shows the tree is drawn from it: the desk's icons, each folder's
   window, the Workspace HD list, the Trash and the folders in the Window menu. A change to
   the tree redraws them all.

   A node: { id, name, kind, icon, parent, children (folders only), locked, win (the window
   it opens), group (a heading in its folder), note (a folder's infobar), from (in the
   Trash: where it was), kindText (the kind shown in a list), seq (the order it was made
   in), order (a folder's: 'hand', 'name' or 'kind') }. Kinds:
     disk       the root, Workspace HD; its contents are the desk's icons
     folder     opens its own window, made here
     trash      the Trash, a list with Put Back
     document   opens a window of the page; application, the same
     program, text   opened by workspace.js (Files.opener); a text is the Editor's, saved
   The workspace's own items are locked, as the Finder could lock a file: they can be moved
   into other folders but not renamed or thrown away. Folders made and texts saved during
   the session can be renamed, moved and thrown away.

   A folder shows its icons in one of three orders (the View menu): by hand, the order of its
   children, which dragging an icon between two others or Move Icon Earlier and Later
   change; by name; or by kind. A manual move in a sorted folder keeps the sorted order as
   it stands and goes on by hand. Restore Original Order puts the children back in the
   order they were made. In a folder with groups (the Programs) each group keeps its own.

   Files.add(folder, spec)      a new node in a folder (returns it)
   Files.opener(kind, fn)       fn(node) opens a node of that kind
   Files.byWin(id), Files.alive(node), Files.path(node), Files.front()
   Files.save(o, done)          asks for a name and a folder, then done(name, folder)
   Files.trashText(name, text, info)   an edited text from the Editor goes to the Trash
   Files.onChange(fn)           after every change */

var Files = (function () {
  'use strict';
  var doc = document, $ = Desk.$, $$ = Desk.$$, el = Desk.el, plural = Desk.plural;
  var nodes = {}, byWin = {}, openers = {}, changed = [], seq = 0;

  /* ---------------- the tree ---------------- */
  function make(spec, parent) {
    var n = { id: 'n' + (++seq), seq: seq, name: spec.name, kind: spec.kind || 'document', icon: spec.icon, parent: null, locked: spec.locked !== false };
    ['win', 'group', 'groups', 'note', 'place', 'href', 'kindText', 'program', 'text', 'scrap'].forEach(function (k) { if (spec[k] !== undefined) n[k] = spec[k]; });
    if (isFolder(n)) { n.children = []; n.order = 'hand'; if (!n.icon) n.icon = 'folder'; }   // every folder looks the same
    nodes[n.id] = n;
    if (n.win) byWin[n.win] = n;
    if (parent) { n.parent = parent; parent.children.push(n); }
    (spec.items || []).forEach(function (s) { make(s, n); });
    return n;
  }
  function isFolder(n) { return n.kind === 'folder' || n.kind === 'disk' || n.kind === 'trash'; }
  function within(n, f) { for (var p = n; p; p = p.parent) if (p === f) return true; return false; }
  function alive(n) { return !!n && !!nodes[n.id] && within(n, root); }
  function inTrash(n) { return within(n, trash); }
  function path(n) { return n === root ? root.name : path(n.parent) + ': ' + n.name; }
  function walk(f, fn) { f.children.forEach(function (c) { fn(c); if (c.children) walk(c, fn); }); }
  function hasLocked(n) { if (n.locked) return true; var any = false; if (n.children) walk(n, function (c) { if (c.locked) any = true; }); return any; }
  function taken(f, name, except) { name = name.toLowerCase(); return f.children.some(function (c) { return c !== except && c.name.toLowerCase() === name; }); }
  function unique(f, base) { var name = base, k = 2; while (taken(f, name)) name = base + ' ' + k++; return name; }
  function folders() { var out = [root]; walk(root, function (c) { if (c.kind === 'folder') out.push(c); }); return out; }

  var D = 'document', P = 'picture';
  var root = make({ kind: 'disk', name: 'Workspace HD', win: 'win-disk', icon: 'disk' });
  [
    { name: 'Read Me', win: 'win-welcome', icon: 'readme' },
    { kind: 'folder', name: 'About', win: 'win-about', place: '80 60 560', note: 'read in any order', items: [
      { name: 'A short history of FORTRAN', win: 'win-ch-fortran', icon: D },
      { name: 'The job', win: 'win-ch-job', icon: D },
      { name: 'Using the workspace', win: 'win-ch-using', icon: D },
      { name: 'The language', win: 'win-ch-language', icon: D },
      { name: 'The line printer', win: 'win-ch-printer', icon: D },
      { name: 'Iannis Xenakis and the sieve', win: 'win-ch-xenakis', icon: D },
      { name: 'The sieve generator', win: 'win-ch-sieve', icon: D },
      { name: 'The music programs', win: 'win-ch-music', icon: D },
      { name: 'The Player', win: 'win-ch-player', icon: D }] },
    // its programs are added by workspace.js, from programs.js
    { kind: 'folder', name: 'Programs', win: 'win-programs', place: '100 80 620', note: 'opening one replaces the Editor’s text', groups: ['Samples', 'Music'] },
    { kind: 'folder', name: 'Xenakis miscellanea', win: 'win-portfolio', place: '140 100 600', note: 'pictures and a printout', items: [
      { name: 'Metastaseis, bars 309–314', win: 'win-pf-a', icon: P, kindText: 'picture' },
      { name: 'Three sieves on a line', win: 'win-pf-e', icon: P, kindText: 'picture' },
      { name: 'Achorripsis, the matrix', win: 'win-pf-i', icon: P, kindText: 'picture' },
      { name: 'Analogique A and B: screens', win: 'win-pf-j', icon: P, kindText: 'picture' },
      { name: 'Nomos Alpha and the cube', win: 'win-pf-d', icon: P, kindText: 'picture' },
      { name: 'ST printout', win: 'win-pf-h', icon: 'textdoc' },
      { name: 'Arborescences', win: 'win-pf-c', icon: P, kindText: 'picture' },
      { name: 'A UPIC page', win: 'win-pf-f', icon: P, kindText: 'picture' }] },
    { kind: 'folder', name: 'Dada miscellanea', win: 'win-dada', place: '160 120 600', note: 'chance, by hand', items: [
      { name: '3 Standard Stoppages', win: 'win-dd-stoppages', icon: P, kindText: 'picture, dropped afresh' },
      { name: 'Karawane', win: 'win-dd-karawane', icon: D, kindText: 'sound poem' },
      { name: 'Squares by chance', win: 'win-dd-arp', icon: P, kindText: 'picture, dropped afresh' },
      { name: 'To make a Dadaist poem', win: 'win-dd-tzara', icon: 'hat', kindText: 'recipe, with a hat' },
      { name: 'Lautgedicht', win: 'win-dd-lautgedicht', icon: 'textdoc', kindText: 'sound poem, blacked out' }] },
    { kind: 'folder', name: 'Results', win: 'win-results', place: '200 140 520', note: 'written afresh at each run', items: [
      { name: 'Printout', win: 'win-printer', icon: 'printout' },
      { name: 'Job Log', win: 'win-log', icon: 'log' },
      { name: 'Listing', win: 'win-listing', icon: 'listing' },
      { name: 'Output', win: 'win-records', icon: 'punchfile' }] },
    { kind: 'application', name: 'Editor', win: 'win-editor', icon: 'editor' },
    { kind: 'application', name: 'Player', win: 'win-player', icon: 'player' },
    { kind: 'application', name: 'Eighty Columns', win: 'win-course', icon: 'course', kindText: 'application, 10 sheets' },
    { kind: 'application', name: 'Calculator', win: 'win-calc', icon: 'calc', kindText: 'desk accessory' },
    { kind: 'application', name: 'Crible', win: 'win-crible', icon: 'crible', kindText: 'application, a game of sieves' }
  ].forEach(function (s) { make(s, root); });
  var trash = make({ kind: 'trash', name: 'Trash', win: 'win-trash', icon: 'trash' });
  trash.parent = null;

  function describe(n) {
    if (n.kindText) return n.kindText;
    if (n.kind === 'folder') return 'folder, ' + plural(n.children.length, 'item');
    if (n.kind === 'program') return 'FORTRAN program';
    if (n.kind === 'text') return 'text, saved in this session';
    if (n.kind === 'trash') return n.children.length ? 'special, ' + plural(n.children.length, 'item') : 'special, empty';
    return n.kind;
  }

  /* ---------------- the order of a folder's icons ---------------- */
  var KINDS = ['folder', 'application', 'document', 'picture', 'program', 'text'];
  function kindRank(n) { var k = KINDS.indexOf(n.icon === 'picture' ? 'picture' : n.kind); return k < 0 ? KINDS.length : k; }
  function byName(a, b) { return a.name.localeCompare(b.name, 'en', { numeric: true, sensitivity: 'base' }) || a.seq - b.seq; }
  var SORTS = {
    name: byName,
    kind: function (a, b) { return kindRank(a) - kindRank(b) || byName(a, b); }
  };
  // a folder's children as its icons stand
  function shown(f) { return SORTS[f.order] ? f.children.slice().sort(SORTS[f.order]) : f.children.slice(); }
  // the neighbours that an icon can trade places with: its group, in its folder
  function peers(n) { var g = n.group || 'Other'; return shown(n.parent).filter(function (c) { return !n.parent.groups || (c.group || 'Other') === g; }); }
  // A move by hand: the order as it stands becomes the folder's own, then n goes before
  // `before` (null: after the last of its peers).
  function reorder(n, before) {
    var f = n.parent;
    if (before === n) return;
    f.children = shown(f); f.order = 'hand';
    var p = peers(n);
    if (!before) before = p[p.length - 1] === n ? null : nextOf(f, p[p.length - 1]);
    detachFrom(f, n);
    var k = before ? f.children.indexOf(before) : f.children.length;
    f.children.splice(k < 0 ? f.children.length : k, 0, n);
    render();
    say('“' + n.name + '” is now ' + (peers(n).indexOf(n) + 1) + ' of ' + peers(n).length + (f.groups ? ' in ' + (n.group || 'Other') : '') + ' in ' + where(f) + '.');
  }
  function nextOf(f, c) { return f.children[f.children.indexOf(c) + 1] || null; }
  function detachFrom(f, n) { f.children.splice(f.children.indexOf(n), 1); }
  function step(n, d) {
    if (!n.parent || n.parent === trash) return;
    var p = peers(n), i = p.indexOf(n), j = i + d;
    if (j < 0 || j >= p.length) { say('“' + n.name + '” is already the ' + (d < 0 ? 'first' : 'last') + (n.parent.groups ? ' in ' + (n.group || 'Other') : '') + ' in ' + where(n.parent) + '.'); return; }
    reorder(n, d < 0 ? p[j] : p[j + 1] || null);
  }
  function setOrder(f, order) {
    if (order === 'original') { f.children.sort(function (a, b) { return a.seq - b.seq; }); f.order = 'hand'; }
    else f.order = order;
    render();
    say(where(f) === 'the desk' ? 'The desk is ' + ORDER_TEXT[f.order] + '.' : '“' + f.name + '” is ' + ORDER_TEXT[f.order] + '.');
  }
  var ORDER_TEXT = { hand: 'in its own order, by hand', name: 'ordered by name', kind: 'ordered by kind' };
  // a polite note for screen readers, after each change of order
  function say(msg) { var s = $('fs-status'); s.textContent = ''; setTimeout(function () { s.textContent = msg; }, 30); }

  /* ---------------- drawing the tree ---------------- */
  function iconEl(n) {
    var li = el('li'), b = el('button', 'icon'), c = el('canvas', 'ico');
    b.type = 'button'; b.setAttribute('aria-describedby', 'icon-hint');
    b.setAttribute('data-node', n.id);
    if (n.win) b.setAttribute('data-win', n.win);
    if (n === trash) b.id = 'icon-trash';
    c.setAttribute('data-icon', n === trash && n.children.length ? 'trash-full' : n.icon);
    c.setAttribute('aria-hidden', 'true');
    b.appendChild(c); b.appendChild(el('span', 'ico-label', n.name));
    li.appendChild(b);
    Px.drawIcon(c);
    return li;
  }
  function list(label, items) {
    var ul = el('ul', 'folder'); ul.setAttribute('aria-label', label);
    items.forEach(function (n) { ul.appendChild(iconEl(n)); });
    return ul;
  }
  var cascade = 0;
  // a folder's window: its title, the count and its note, and its icons, in groups if it has them
  function folderWin(f) {
    var w = f.win && $(f.win);
    if (!w) {
      if (!f.win) f.win = 'win-f-' + f.id;
      byWin[f.win] = f;
      var k = cascade++ % 6;
      w = el('section', 'win folder-win'); w.id = f.win;
      w.setAttribute('data-place', f.place || (160 + 40 * k) + ' ' + (100 + 30 * k) + ' 520');
      w.appendChild(el('h2', 'title', f.name));
      var info = el('p', 'infobar'); info.setAttribute('aria-hidden', 'true');
      info.appendChild(el('span')); info.appendChild(el('span'));
      w.appendChild(info);
      w.appendChild(el('div', 'pane'));
      Desk.addWindow(w);
    }
    if (w.querySelector('.title').textContent !== f.name) { w.querySelector('.title').textContent = f.name; Desk.refresh(w); }
    var spans = w.querySelectorAll('.infobar span');
    spans[0].textContent = plural(f.children.length, 'item');
    spans[1].textContent = f.locked ? f.note : 'made in this session';
    var pane = w.querySelector('.pane');
    pane.innerHTML = '';
    if (!f.children.length) pane.appendChild(el('p', 'placeholder', 'This folder is empty. Drag an icon onto it, or select one and choose Move To… from the File menu.'));
    else if (f.groups) {
      pane.setAttribute('data-iconnav', '');
      var all = shown(f);
      f.groups.concat(['Other']).forEach(function (g) {
        var items = all.filter(function (c) { return (c.group || 'Other') === g; });
        if (!items.length) return;
        pane.appendChild(el('h3', 'group', g));
        pane.appendChild(list(g + ' in ' + f.name, items));
      });
    } else pane.appendChild(list('Contents of ' + f.name, shown(f)));
    if (Desk.isOpen(w)) Desk.snapLabels(w);
  }
  // the desk: the disk, then the disk's contents, then the Trash in its corner
  function renderDesk() {
    var ul = doc.querySelector('.icons'), frag = doc.createDocumentFragment();
    frag.appendChild(iconEl(root));
    shown(root).forEach(function (n) { frag.appendChild(iconEl(n)); });
    var t = iconEl(trash); t.className = 'trash-slot'; frag.appendChild(t);
    ul.innerHTML = ''; ul.appendChild(frag);
    Desk.snapLabels(ul);
  }
  // Workspace HD: the same contents as a list, with their kinds
  function renderDisk() {
    var body = $('disk-list'), frag = doc.createDocumentFragment();
    shown(root).concat([trash]).forEach(function (n) {
      var tr = el('tr'), td = el('td'), b;
      b = el('button', 'lv', n.name); b.type = 'button'; b.setAttribute('data-act', 'node:' + n.id);
      td.appendChild(b); tr.appendChild(td); tr.appendChild(el('td', '', describe(n)));
      frag.appendChild(tr);
    });
    body.innerHTML = ''; body.appendChild(frag);
    $('disk-count').textContent = plural(root.children.length + 1, 'item');
  }
  function renderTrash() {
    var ul = $('trash-list'), n = trash.children.length;
    ul.innerHTML = '';
    trash.children.forEach(function (t) {
      var li = el('li'), b = el('button', 'btn', 'Put Back');
      b.type = 'button'; b.setAttribute('data-act', 'put-back:' + t.id); b.setAttribute('aria-label', 'Put back ' + t.name);
      var where = t.scrap ? 'edited text from the Editor' : describe(t) + ', from ' + (t.from === root ? 'the desk' : t.from.name);
      li.appendChild(el('span', '', t.name + ', ' + where)); li.appendChild(b);
      ul.appendChild(li);
    });
    $('trash-note').textContent = n
      ? 'The Trash holds ' + plural(n, 'item') + '. Put Back returns one to where it was; Empty Trash in the Special menu throws them away for good.'
      : 'The Trash is empty. Drag a folder or a saved text here, or choose Move to Trash from the File menu. When you open another program, an edited text is moved here too, and you can put it back until the Trash is emptied.';
  }
  // the folders, in the Window menu, after Workspace HD
  function renderWindowMenu() {
    $$('#menu-window li[data-fs]').forEach(function (li) { li.remove(); });
    var after = doc.querySelector('#menu-window [data-act="open:win-disk"]').parentNode;
    folders().slice(1).forEach(function (f) {
      var li = el('li'), b = el('button', '', f.name);
      li.setAttribute('role', 'none'); li.setAttribute('data-fs', '');
      b.type = 'button'; b.setAttribute('role', 'menuitemcheckbox'); b.setAttribute('aria-checked', String(Desk.isOpen($(f.win))));
      b.setAttribute('data-act', 'open:' + f.win);
      li.appendChild(b);
      after.parentNode.insertBefore(li, after.nextSibling);
      after = li;
    });
  }
  // Everything is redrawn from the tree; the focus and the selection follow their node.
  function render() {
    var a = doc.activeElement, focusId = a && a.getAttribute && a.getAttribute('data-node');
    var focusIn = focusId && (a.closest('.win') ? a.closest('.win').id : 'desk');
    var sel = Desk.selected(), selId = sel && sel.getAttribute('data-node');
    folders().slice(1).forEach(folderWin);
    // windows hosted by a folder: a document's window follows its node
    Object.keys(byWin).forEach(function (id) {
      var n = byWin[id], w = $(id);
      if (!w || n === root || n === trash) return;
      var host = n.parent && n.parent !== root ? n.parent.win : null;
      if (host) w.setAttribute('data-host', host); else w.removeAttribute('data-host');
    });
    renderDesk(); renderDisk(); renderTrash(); renderWindowMenu();
    if (focusId) { var f = iconIn(focusIn, focusId); if (f) f.focus({ preventScroll: true }); }
    if (selId) Desk.selectIcon(iconIn(focusIn || 'desk', selId) || null);
    changed.forEach(function (fn) { fn(); });
  }
  function iconIn(where, id) {
    var scope = where === 'desk' ? doc.querySelector('.icons') : $(where);
    return (scope && scope.querySelector('[data-node="' + id + '"]')) || $$('[data-node="' + id + '"]').filter(Desk.visible)[0] || null;
  }

  /* ---------------- changing the tree ---------------- */
  function detach(n) { var p = n.parent; if (p) p.children.splice(p.children.indexOf(n), 1); n.parent = null; }
  function closeAll(n) { if (n.win) Desk.close(n.win); if (n.children) walk(n, function (c) { if (c.win) Desk.close(c.win); }); }
  function where(f) { return f === root ? 'the desk' : f.name; }
  function move(n, f) {
    if (f === trash) return throwAway(n);
    if (n.parent === f) return false;
    if (n.kind === 'folder' && within(f, n)) { Desk.alert('“' + n.name + '” cannot go inside itself.'); return false; }
    if (taken(f, n.name)) { Desk.alert('There is already an item named “' + n.name + '” in ' + where(f) + '. Rename one of them first.'); return false; }
    var was = inTrash(n);
    detach(n); n.parent = f; f.children.push(n);
    if (was) delete n.from;
    render();
    return true;
  }
  function throwAway(n) {
    if (n === root || n === trash || n.parent === trash) return false;
    if (hasLocked(n)) {
      Desk.alert(n.locked
        ? '“' + n.name + '” belongs to the workspace and is locked, so it cannot be thrown away. It can still be moved into another folder.'
        : '“' + n.name + '” holds items that belong to the workspace, so it cannot be thrown away. Move them out of it first.');
      return false;
    }
    closeAll(n);
    n.from = n.parent; detach(n); n.parent = trash; trash.children.push(n);
    render();
    return true;
  }
  function putBack(n) {
    if (!n || n.parent !== trash) return;
    if (n.scrap) { detach(n); delete nodes[n.id]; render(); if (openers.scrap) openers.scrap(n); return; }
    var to = alive(n.from) ? n.from : root;
    if (taken(to, n.name)) n.name = unique(to, n.name);
    detach(n); delete n.from; n.parent = to; to.children.push(n);
    render();
    var b = iconIn(to === root ? 'desk' : to.win, n.id);
    if (b) b.focus({ preventScroll: true }); else Desk.open('win-trash');
  }
  function empty() {
    if (!trash.children.length) { Desk.alert('The Trash is already empty.'); return; }
    trash.children.slice().forEach(function (n) {
      [n].concat(n.children ? (function () { var a = []; walk(n, function (c) { a.push(c); }); return a; })() : []).forEach(function (c) {
        if (c.kind === 'folder' && c.win) { Desk.removeWindow(c.win); delete byWin[c.win]; }
        delete nodes[c.id];
      });
    });
    trash.children = [];
    render();
  }
  function add(f, spec) { var n = make(Object.assign({ locked: false }, spec), f); render(); return n; }

  /* ---------------- renaming, in place under the icon ---------------- */
  function rename(n) {
    var b = $$('[data-node="' + n.id + '"]').filter(Desk.visible)[0];
    if (!b) return;
    var li = b.parentNode, input = el('input', 'ico-edit'), done = false;
    input.type = 'text'; input.value = n.name; input.maxLength = 31;
    input.spellcheck = false; input.autocomplete = 'off';
    input.setAttribute('aria-label', 'New name for ' + n.name + '. Enter keeps it, Escape cancels.');
    li.classList.add('renaming'); li.appendChild(input);
    // the field grows with the name, centred under the icon, on whole screen pixels
    function fit() { var w = Math.max(124, Desk.ev(input.value.length * 10 + 24)); input.style.width = w + 'px'; input.style.left = Desk.ev((124 - w) / 2) + 'px'; }
    input.addEventListener('input', fit); fit();
    input.focus(); input.select();
    function finish(keep) {
      if (done) return;
      var v = input.value.trim().replace(/:/g, '-');
      if (keep && v && v !== n.name && taken(n.parent, v, n)) {
        if (keep === 'enter') { Desk.alert('The name “' + v + '” is already used in ' + where(n.parent) + '. Please choose a different name.'); return; }
        keep = false;
      }
      done = true;
      li.classList.remove('renaming'); input.remove();
      if (keep && v && v !== n.name) { n.name = v; render(); }
      var again = iconIn(n.parent === root ? 'desk' : n.parent.win, n.id);
      if (again && keep !== 'blur') again.focus({ preventScroll: true });
    }
    input.addEventListener('keydown', function (e) {
      if (e.key === 'Enter') { e.preventDefault(); finish('enter'); }
      else if (e.key === 'Escape') { e.preventDefault(); e.stopPropagation(); finish(false); }
      e.stopPropagation();   // the arrow keys move in the name, not between icons
    });
    input.addEventListener('blur', function () { setTimeout(function () { if (doc.activeElement !== input && !doc.querySelector('.alert-veil.open')) finish('blur'); }, 0); });
  }

  /* ---------------- the Finder's actions ---------------- */
  function selectedNode(verb) {
    var b = Desk.selected(), n = b && Desk.visible(b) && nodes[b.getAttribute('data-node')];
    if (!n) Desk.alert('Select an icon on the desk or in a folder first, then choose ' + verb + '.');
    return n || null;
  }
  // the folder in front, if a folder's window is the front window; else the desk
  function front() { var t = Desk.topWin(), n = t && byWin[t.id]; return n && n.kind === 'folder' ? n : root; }
  function places(except) {
    return folders().filter(function (f) { return !(except && except.kind === 'folder' && within(f, except)); })
      .map(function (f) { return { value: f.id, label: f === root ? root.name + ' (the desk)' : path(f) }; });
  }
  Desk.action('node', function (id) { var n = nodes[id]; if (n) openNode(n); });
  Desk.action('new-folder', function () {
    var f = front(), n = make({ kind: 'folder', name: unique(f, 'untitled folder'), locked: false }, f);
    render();
    if (f !== root) Desk.open(f.win, { focus: false });
    var b = iconIn(f === root ? 'desk' : f.win, n.id);
    if (b && Desk.visible(b)) { Desk.selectIcon(b); rename(n); }
    else Desk.alert('A new folder, “' + n.name + '”, is on the desk.');
  });
  Desk.action('rename', function () {
    var n = selectedNode('Rename');
    if (!n) return;
    if (n.locked || n === root || n === trash) { Desk.alert('“' + n.name + '” belongs to the workspace and is locked, so it keeps its name. Folders you make and texts you save can be renamed.'); return; }
    rename(n);
  });
  Desk.action('move-to', function () {
    var n = selectedNode('Move To…');
    if (!n) return;
    if (n === root || n === trash) { Desk.alert('“' + n.name + '” stays where it is.'); return; }
    Desk.ask({ msg: 'Move “' + n.name + '” to:', ok: 'Move', places: places(n), place: n.parent.id }, function (name, id) {
      var f = nodes[id];
      if (f === n.parent) return;
      if (taken(f, n.name)) return 'There is already an item named “' + n.name + '” in ' + where(f) + '.';
      setTimeout(function () { if (move(n, f)) { var b = iconIn(f === root ? 'desk' : f.win, n.id); if (b && Desk.visible(b)) b.focus(); } }, 0);
    });
  });
  Desk.action('trash-selected', function () { var n = selectedNode('Move to Trash'); if (n) throwAway(n); });
  // the View menu: the order of the front folder's icons, or the desk's
  Desk.action('order', function (o) { setOrder(front(), o); });
  Desk.action('icon-step', function (d) {
    var n = selectedNode(d < 0 ? 'Move Icon Earlier' : 'Move Icon Later');
    if (!n) return;
    if (n === root || n === trash) { Desk.alert('“' + n.name + '” keeps its place on the desk.'); return; }
    stepAndFocus(n, +d);
  });
  function stepAndFocus(n, d) {
    step(n, d);
    var b = iconIn(n.parent === root ? 'desk' : n.parent.win, n.id);
    if (b && Desk.visible(b)) { Desk.selectIcon(b); b.focus({ preventScroll: true }); }
  }
  Desk.onMenu(function (m) {
    if (m.id !== 'menu-view') return;
    var f = front();
    $$('[role="menuitemradio"]', m).forEach(function (it) {
      var on = it.getAttribute('data-act') === 'order:' + f.order;
      it.classList.toggle('checked', on); it.setAttribute('aria-checked', String(on));
    });
    $('view-of').textContent = f === root ? 'the desk' : f.name;
  });
  Desk.action('put-back', function (id) { putBack(nodes[id]); });
  Desk.action('empty-trash', empty);
  function openNode(n) {
    if (n.win) { Desk.open(n.win); return; }
    if (openers[n.kind]) openers[n.kind](n);
  }
  Desk.onIcon(function (b) { var n = nodes[b.getAttribute('data-node')]; if (n) openNode(n); });
  // Command (or Control) and Delete throws the selected icon away, as in the Finder; Option
  // (Alt) and an arrow moves it earlier or later among its neighbours. On the desk, whose
  // columns fill from the right, right is earlier.
  doc.addEventListener('keydown', function (e) {
    if (!(e.target.matches && e.target.matches('.icon[data-node]'))) return;
    var n = nodes[e.target.getAttribute('data-node')];
    if (!n) return;
    if ((e.key === 'Backspace' || e.key === 'Delete') && (e.metaKey || e.ctrlKey)) { e.preventDefault(); throwAway(n); return; }
    if (!e.altKey || e.metaKey || e.ctrlKey || n === root || n === trash) return;
    var desk = n.parent === root && !Desk.narrowMQ.matches;
    var d = { ArrowUp: -1, ArrowDown: 1, ArrowLeft: desk ? 1 : -1, ArrowRight: desk ? -1 : 1 }[e.key];
    if (!d) return;
    e.preventDefault();
    stepAndFocus(n, d);
  });

  /* ---------------- dragging icons with a mouse ---------------- */
  // An icon dragged by more than a few pixels leaves an outline under the pointer. Dropped
  // on a folder's picture, an open folder's window, the desk or the Trash, it moves there.
  // Dropped among its own neighbours (between two icons, on a label, or on an icon that is
  // not a folder) it takes that place, before the icon after the pointer; a blue bar marks
  // the place.
  var drag = null, eatClick = false;
  doc.addEventListener('dragstart', function (e) { if (e.target.closest && e.target.closest('.icon')) e.preventDefault(); });
  doc.addEventListener('pointerdown', function (e) {
    if (e.button !== 0 || e.pointerType !== 'mouse' || Desk.narrowMQ.matches) return;
    var b = e.target.closest && e.target.closest('.icon[data-node]'), n = b && nodes[b.getAttribute('data-node')];
    if (!n || n === root || n === trash || b.closest('.renaming')) return;
    drag = { b: b, n: n, x: e.clientX, y: e.clientY, ghost: null, to: null, mark: null };
  });
  // a place among n's own neighbours under the pointer, or null; { same: true } when the
  // place is where n already is
  function slotAt(x, y, t, n) {
    var f = n.parent;
    if (!f || f === trash || t.closest('.trash-slot')) return null;
    var desk = f === root, scope = desk ? doc.querySelector('.icons') : $(f.win);
    if (!scope || !Desk.visible(scope) || !scope.contains(t) || (!desk && !t.closest('.pane'))) return null;
    var mine = scope.querySelector('[data-node="' + n.id + '"]'), ul = mine && mine.closest('ul');
    if (!ul) return null;
    // with groups, only inside the icon's own group
    if (!desk && f.groups) {
      var r = ul.getBoundingClientRect();
      if (x < r.left - 8 || x > r.right + 8 || y < r.top - 8 || y > r.bottom + 8) return null;
    }
    var lis = $$(':scope > li', ul).filter(function (li) { var b = li.querySelector('[data-node]'); return b && nodes[b.getAttribute('data-node')].parent === f; });
    // the desk fills columns from the right, top to bottom; a folder fills rows, left to right
    var cols = desk && !Desk.narrowMQ.matches, k = lis.length;
    for (var i = 0; i < lis.length; i++) {
      var q = lis[i].getBoundingClientRect();
      var after = cols ? q.right < x || (q.left <= x + 8 && q.top + q.height / 2 > y)
        : q.top > y || (q.bottom >= y && q.left + q.width / 2 > x);
      if (after) { k = i; break; }
    }
    var p = peers(n), at = p.indexOf(n), before = k < lis.length ? nodes[lis[k].querySelector('[data-node]').getAttribute('data-node')] : null;
    if (before === n || (before ? p.indexOf(before) === at + 1 : at === p.length - 1)) return { same: true };
    return { n: f, before: before, reorder: true, mark: k < lis.length ? lis[k] : lis[lis.length - 1], cls: k < lis.length ? 'ins-before' : 'ins-after', cols: cols };
  }
  function targetAt(x, y, d) {
    var t = doc.elementFromPoint(x, y);
    if (!t) return null;
    var b = t.closest('.icon[data-node]'), n = b && nodes[b.getAttribute('data-node')];
    var slot = slotAt(x, y, t, d);
    // a folder's picture takes the icon in; its label, among neighbours, is a place
    if (n && n !== d && isFolder(n) && (t.closest('.ico') || !slot)) return { n: n, mark: b, cls: 'drop' };
    if (slot) return slot.same ? null : slot;
    var w = t.closest('.win');
    if (w) { var f = byWin[w.id]; return f && isFolder(f) ? { n: f, mark: w, cls: 'drop' } : null; }
    if (t.closest('.desktop')) return { n: root, mark: null };
    return null;
  }
  function allowed(n, f) { return f !== n && !(n.kind === 'folder' && within(f, n)) && f !== n.parent; }
  doc.addEventListener('pointermove', function (e) {
    if (!drag) return;
    if (!drag.ghost) {
      if (Math.abs(e.clientX - drag.x) + Math.abs(e.clientY - drag.y) < 8) return;
      var r = drag.b.querySelector('canvas').getBoundingClientRect();
      drag.dx = drag.x - r.left; drag.dy = drag.y - r.top;
      drag.ghost = el('div', 'icon-ghost'); drag.ghost.setAttribute('aria-hidden', 'true');
      var c = el('canvas', 'ico'); c.setAttribute('data-icon', drag.b.querySelector('canvas').getAttribute('data-icon')); Px.drawIcon(c);
      drag.ghost.appendChild(c); doc.body.appendChild(drag.ghost);
    }
    drag.ghost.style.transform = 'translate(' + Desk.ev(e.clientX - drag.dx) + 'px,' + Desk.ev(e.clientY - drag.dy) + 'px)';
    var t = targetAt(e.clientX, e.clientY, drag.n), ok = t && (t.reorder || allowed(drag.n, t.n));
    var mark = ok ? t.mark : null, cls = ok ? t.cls + (t.cols ? ' cols' : '') : '';
    if (drag.mark !== mark || drag.cls !== cls) { unmark(drag); if (mark) DOMTokenList.prototype.add.apply(mark.classList, cls.split(' ')); drag.mark = mark; drag.cls = cls; }
    drag.to = ok ? t : null;
  });
  function unmark(d) { if (d.mark) d.mark.classList.remove('drop', 'ins-before', 'ins-after', 'cols'); }
  function endDrag(drop) {
    var d = drag;
    drag = null;
    if (!d || !d.ghost) return;
    d.ghost.remove();
    unmark(d);
    eatClick = true; setTimeout(function () { eatClick = false; }, 0);
    if (drop && d.to) { if (d.to.reorder) reorder(d.n, d.to.before); else move(d.n, d.to.n); }
  }
  doc.addEventListener('pointerup', function () { endDrag(true); });
  doc.addEventListener('pointercancel', function () { endDrag(false); });
  doc.addEventListener('click', function (e) { if (eatClick) { eatClick = false; e.stopPropagation(); e.preventDefault(); } }, true);

  /* ---------------- for the applications ---------------- */
  // Save As: a name and a folder; the name must be new in that folder
  function save(o, done) {
    var f = alive(o.folder) && !inTrash(o.folder) ? o.folder : front();
    Desk.ask({ msg: o.msg, ok: 'Save', name: unique(f, o.name), places: places(null), place: f.id }, function (name, id) {
      var to = nodes[id];
      name = name.replace(/:/g, '-').slice(0, 31);
      if (!name) return 'Please give the text a name.';
      if (taken(to, name)) return 'There is already an item named “' + name + '” in ' + where(to) + '.';
      done(name, to);
    });
  }
  function trashText(name, text, info) {
    make({ kind: 'text', name: name, icon: 'source', text: text, scrap: info, locked: false }, trash);
    render();
  }

  render();
  return {
    add: add, alive: alive, path: path, front: front, save: save, trashText: trashText, where: where,
    byWin: function (id) { return byWin[id]; },
    opener: function (kind, fn) { openers[kind] = fn; },
    onChange: function (fn) { changed.push(fn); }
  };
})();
