# The gallery (../../index.html) and the genealogy's written lineage (../../genealogy/index.html),
# set from scripts/versions.js (read through JavaScriptCore), so both pages show every room
# without a script; the genealogy's tree is drawn in the page by genealogy/genealogy.js.
import os, json, html, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, '..', '..'))
JSC = '/System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Helpers/jsc'
V = json.loads(subprocess.check_output([JSC, os.path.join(REPO, 'scripts/versions.js'), '-e', 'print(JSON.stringify(VERSIONS))']))
E = html.escape
def no(i): return 'No. ' + i[1:]
def frm(v):
    s = 'From ' + ' and '.join(no(p) for p in v['parents']) if v['parents'] else ''
    if v['borrows']: s += (', with a part of ' if s else 'With a part of ') + ' and '.join(no(b) for b in v['borrows'])
    return s + '.' if s else 'The first room.'
HEAD = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%s</title>
<link rel="stylesheet" href="%sfonts/fonts.css">
<link rel="stylesheet" href="%scss/rooms.css">
</head>
<body>
'''
def gallery():
    cards = '\n'.join('      <li class="room-card" data-status="%s"><span class="pin" aria-hidden="true"></span><a href="%s/"><img src="assets/rooms/%s.png" width="192" height="120" alt=""><span class="no">%s</span><span class="t">%s</span><span class="n">%s</span><span class="from">%s</span></a></li>'
                      % (v['status'], v['id'], v['id'], no(v['id']), E(v['title']), E(v['note']), frm(v)) for v in V)
    return HEAD % ('The rooms: a FORTRAN punched-card interpreter in twenty-five rooms', '', '') + '''<!-- The gallery: every room of the site pinned up on a board on the last room's wall, each a
     print of the room in that room's palette (assets/rooms/, made by util/gallery/thumbs.py).
     Set from scripts/versions.js by util/gallery/build_pages.py. -->
<main class="board">
  <span class="pin l" aria-hidden="true"></span><span class="pin r" aria-hidden="true"></span>
  <div class="board-in">
    <header class="head">
      <div>
        <p class="kicker">A folio from the bookshelf</p>
        <h1>The rooms</h1>
        <p class="lede">A FORTRAN punched-card interpreter, and a deck that computes Iannis Xenakis’s sieves, made twenty-five times over: first plainly, then in a run of styles, then as a desk, a desktop, a puzzle, a magazine and at last a room to wander in. Each print is pinned up where it was taken; press one to go in.</p>
      </div>
      <ul class="ways">
        <li><a href="genealogy/">The genealogy</a></li>
        <li><a href="v25/">The last room</a></li>
      </ul>
    </header>
    <ol class="rooms">
%s
    </ol>
  </div>
</main>
</body>
</html>
''' % cards
def genealogy():
    items = '\n'.join('      <li id="l-%s"><span class="no">%s</span><b><a href="../%s/">%s</a></b>%s<span class="from">%s</span> %s</li>'
                      % (v['id'], no(v['id']), v['id'], E(v['title']), ' <i>(in progress)</i>' if v['status'] != 'complete' else '', frm(v), E(v['note'])) for v in V)
    return HEAD % ('The genealogy of the rooms', '../', '../') + '''<!-- The genealogy: the rooms as a family tree on graph paper (genealogy.js draws it from
     scripts/versions.js), each room under the ones it was made from, and the lineage written out.
     The lineage is set from scripts/versions.js by util/gallery/build_pages.py. -->
<main class="board">
  <span class="pin l" aria-hidden="true"></span><span class="pin r" aria-hidden="true"></span>
  <div class="board-in">
    <header class="head">
      <div>
        <p class="kicker">A folio from the bookshelf</p>
        <h1>The genealogy of the rooms</h1>
        <p class="lede">How each room was made from the ones before it: a plain page, three ways of laying it out, eleven styles on the one with tabs, then the styles crossed with each other into desks, desktops, a game, a magazine and the room. A full line runs from a room to one it builds on; a dashed line to one it took a single part from. Point at a room to see its line.</p>
      </div>
      <ul class="ways">
        <li><a href="../">The rooms</a></li>
        <li><a href="../v25/">The last room</a></li>
      </ul>
    </header>
    <div class="tree-wrap"><div class="tree" id="tree" aria-hidden="true"></div></div>
    <ul class="legend" aria-hidden="true"><li><i></i>builds on</li><li><i class="b"></i>takes a part from</li>%s</ul>
    <h2>The lineage</h2>
    <ol class="lineage">
%s
    </ol>
  </div>
</main>
<script src="../scripts/versions.js"></script>
<script src="genealogy.js"></script>
</body>
</html>
''' % (('<li>a dashed card: still in progress</li>' if any(v['status'] != 'complete' for v in V) else ''), items)
if __name__ == '__main__':
    open(os.path.join(REPO, 'index.html'), 'w').write(gallery())
    open(os.path.join(REPO, 'genealogy', 'index.html'), 'w').write(genealogy())
    print(len(V), 'rooms')
