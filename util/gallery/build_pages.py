# The gallery (../../index.html) and the genealogy's written lineage (../../genealogy/index.html),
# set from scripts/versions.js (read through JavaScriptCore), so both pages show every room
# without a script; the genealogy's tree is drawn in the page by genealogy/genealogy.js. Both
# are in the four chapters of CHAPTERS.
import os, json, html, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, '..', '..'))
JSC = '/System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Helpers/jsc'
DATA = json.loads(subprocess.check_output([JSC, os.path.join(REPO, 'scripts/versions.js'), '-e', 'print(JSON.stringify({v: VERSIONS, c: CHAPTERS}))']))
V, CH = DATA['v'], DATA['c']
LAST = V[-1]['id']
E = html.escape
def no(i): return 'No. ' + i[1:]
def n(i): return str(int(i[1:]))
def frm(v):
    s = 'From ' + ' and '.join(no(p) for p in v['parents']) if v['parents'] else ''
    if v['borrows']: s += (', with a part of ' if s else 'With a part of ') + ' and '.join(no(b) for b in v['borrows'])
    return s + '.' if s else 'The first room.'
def rooms_of(c):
    ids = [v['id'] for v in V]
    return V[ids.index(c['first']):ids.index(c['last']) + 1]
def span(c): return 'Nos. %s to %s' % (n(c['first']), n(c['last']))

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
def chapter_index(prefix):
    return '''    <nav class="chapters" aria-label="Chapters">
      <ol>
%s
      </ol>
    </nav>''' % '\n'.join('        <li><a href="%s#ch-%s"><span class="cn">%s</span> <span class="ct">%s</span> <span class="cr">%s</span></a></li>'
                         % (prefix, c['id'], c['numeral'], E(c['title']), span(c)) for c in CH)

# fastenings for the prints, in turn: a pin of one colour or another, or two strips of tape
FASTEN = ['pin', 'tape', 'pin blue', 'pin ochre', 'tape', 'pin']
def card(v, k):
    last = v['id'] == LAST
    img = ('<img src="assets/rooms/%s-l.png" width="384" height="240" alt="">' % v['id']) if last else ('<img src="assets/rooms/%s.png" width="192" height="120" alt="">' % v['id'])
    return ('      <li class="room-card%s" data-status="%s"><span class="fasten %s" aria-hidden="true"></span>'
            '<a class="go" href="%s/"><span class="print">%s</span><span class="label"><span class="no">%s</span><span class="t">%s</span><span class="n">%s</span><span class="from">%s</span></span></a>'
            '<a class="line" href="genealogy/#l-%s">Its line in the genealogy</a></li>'
            % (' last' if last else '', v['status'], FASTEN[k % len(FASTEN)], v['id'], img, no(v['id']), E(v['title']), E(v['note']), frm(v), v['id']))

def gallery():
    k = 0; secs = []
    for c in CH:
        cards = []
        for v in rooms_of(c): cards.append(card(v, k)); k += 1
        secs.append('''    <section class="chapter" id="ch-%s" aria-labelledby="ch-%s-h">
      <header class="ch-head"><span class="cn" aria-hidden="true">%s</span><div><h2 id="ch-%s-h">%s</h2><p>%s</p></div><p class="cr">%s</p></header>
      <ol class="rooms" start="%s">
%s
      </ol>
    </section>''' % (c['id'], c['id'], c['numeral'], c['id'], E(c['title']), E(c['note']), span(c), n(c['first']), '\n'.join(cards)))
    return HEAD % ('The rooms: a FORTRAN punched-card interpreter in twenty-five rooms', '', '') + '''<!-- The gallery: every room of the site pinned up on a board on the last room's wall, in the
     work's four chapters, each a print of the room in that room's palette (assets/rooms/, made
     by util/gallery/thumbs.py). Set from scripts/versions.js by util/gallery/build_pages.py. -->
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
        <li><a href="%s/">The last room</a></li>
      </ul>
    </header>
%s
%s
  </div>
</main>
</body>
</html>
''' % (LAST, chapter_index(''), '\n'.join(secs))

def lineage_item(v):
    return ('        <li id="l-%s" tabindex="-1"><img src="../assets/rooms/%s-s.png" width="48" height="30" alt=""><div><span class="no">%s</span> <b><a href="../%s/">%s</a></b>%s'
            '<span class="from">%s</span> %s</div></li>'
            % (v['id'], v['id'], no(v['id']), v['id'], E(v['title']), ' <i>(in progress)</i>' if v['status'] != 'complete' else '', frm(v), E(v['note'])))

def genealogy():
    secs = '\n'.join('''    <section class="ln-ch" id="ch-%s" aria-labelledby="ln-%s-h">
      <h3 id="ln-%s-h"><span class="cn">%s</span> %s <span class="cr">%s</span></h3>
      <ol class="lineage" start="%s">
%s
      </ol>
    </section>''' % (c['id'], c['id'], c['id'], c['numeral'], E(c['title']), span(c), n(c['first']), '\n'.join(lineage_item(v) for v in rooms_of(c))) for c in CH)
    dashed = '<li><i class="d"></i>a dashed print: still in progress</li>' if any(v['status'] != 'complete' for v in V) else ''
    return HEAD % ('The genealogy of the rooms', '../', '../') + '''<!-- The genealogy: the rooms as a family tree on graph paper, read from left to right (genealogy.js
     draws it from scripts/versions.js), each room beside the ones it was made from, and the
     lineage written out in the work's four chapters. The lineage is set from scripts/versions.js
     by util/gallery/build_pages.py. -->
<main class="board wide">
  <span class="pin l" aria-hidden="true"></span><span class="pin r" aria-hidden="true"></span>
  <div class="board-in">
    <header class="head">
      <div>
        <p class="kicker">A folio from the bookshelf</p>
        <h1>The genealogy of the rooms</h1>
        <p class="lede">How each room was made from the ones before it, read from left to right: a plain page and two ways of laying it out, eleven styles on the one with tabs, the styles crossed with one another, and the workspace they became. A full line runs to a room from one it builds on; a dashed line from one it took a single part from. Point at a print to read its label and light its line.</p>
      </div>
      <ul class="ways">
        <li><a href="../">The rooms</a></li>
        <li><a href="../%s/">The last room</a></li>
      </ul>
    </header>
    <div class="tree-wrap"><div class="tree" id="tree" aria-hidden="true"></div></div>
    <ul class="legend" aria-hidden="true"><li><i></i>builds on</li><li><i class="b"></i>takes a part from</li>%s</ul>
    <h2>The lineage</h2>
%s
  </div>
</main>
<script src="../scripts/versions.js"></script>
<script src="genealogy.js"></script>
</body>
</html>
''' % (LAST, dashed, secs)

if __name__ == '__main__':
    open(os.path.join(REPO, 'index.html'), 'w').write(gallery())
    open(os.path.join(REPO, 'genealogy', 'index.html'), 'w').write(genealogy())
    print(len(V), 'rooms in', len(CH), 'chapters')
