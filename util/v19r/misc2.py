# The Xenakis miscellanea's ten drawings, drawn again for v21 as SVG files: one set of papers
# (graph paper, vellum, manuscript paper, a postcard), each with a slight tone across it and
# its rules as patterns; inks of graphite, blue-black, red and sepia in varied weights; typed
# labels in Courier Prime, notes by hand in Caveat, titles in Work Sans, all as outlines (each
# glyph defined once in its file), so a file stands alone as an image. The data follow the
# captions (counts, sieves, sections); what is random is seeded.
import os as _os; UTIL = _os.path.normpath(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..')); REPO = _os.path.dirname(UTIL)
import math, random, os
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen

REPO = REPO
OUT = REPO + '/v21/assets/misc'
GRAPH, BLUE, RED, SEPIA, GREEN = '#33312d', '#24508f', '#a8362b', '#6b4a2a', '#2f6b4f'
PAPER, VELLUM, MANU = '#fbf9f2', '#f3ecdc', '#fcfaf3'

FONTS = {}
def font(fam, wt):
    k = (fam, wt)
    if k not in FONTS:
        slug = fam.lower().replace(' ', '-')
        t = TTFont('%s/fonts/%s/%s-latin-%d-normal.woff2' % (REPO, slug, slug, wt))
        FONTS[k] = (t.getGlyphSet(), t.getBestCmap(), t['head'].unitsPerEm, t['hmtx'])
    return FONTS[k]

def f(v):
    s = ('%.1f' % v).rstrip('0').rstrip('.')
    return '0' if s in ('-0', '') else s

class Sheet:
    def __init__(self, w, h, title):
        self.w, self.h, self.title = w, h, title
        self.defs, self.body, self.glyphs, self.n = [], [], {}, 0
    def id(self, p='i'): self.n += 1; return '%s%d' % (p, self.n)
    def add(self, *s): self.body.extend(s)
    def lin(self, stops, x2=0, y2=1):
        i = self.id('g')
        self.defs.append('<linearGradient id="%s" x1="0" y1="0" x2="%s" y2="%s">%s</linearGradient>' % (i, f(x2), f(y2), ''.join('<stop offset="%s" stop-color="%s"/>' % (f(o), c) for o, c in stops)))
        return 'url(#%s)' % i
    def grid(self, minor, major, cminor, cmajor, wminor=0.3, wmajor=0.55, ox=0, oy=0):
        i = self.id('p')
        self.defs.append(('<pattern id="%s" width="%s" height="%s" patternUnits="userSpaceOnUse" x="%s" y="%s">'
                          '<path d="%s" fill="none" stroke="%s" stroke-width="%s"/>'
                          '<path d="M0 0H%sM0 0V%s" fill="none" stroke="%s" stroke-width="%s"/></pattern>') % (
            i, f(major), f(major), f(ox), f(oy),
            ''.join('M0 %sH%sM%s 0V%s' % (f(k * minor), f(major), f(k * minor), f(major)) for k in range(1, int(major / minor))),
            cminor, f(wminor), f(major), f(major), cmajor, f(wmajor)))
        return 'url(#%s)' % i
    def paper(self, c, tone=0.04):
        self.add('<rect width="%s" height="%s" fill="%s"/>' % (f(self.w), f(self.h), c))
        self.add('<rect width="%s" height="%s" fill="%s" opacity="%s"/>' % (f(self.w), f(self.h), self.lin([(0, '#ffffff'), (1, '#8a7a5a')], 1, 1), f(tone * 4)))
    def text(self, x, y, s, size, fill=GRAPH, fam='Courier Prime', wt=400, anchor='start', rot=0, track=0.0, opacity=1):
        # the drawings are shown at about half their size, so small type is set larger
        size = size * (1.35 if size < 12 else 1.1)
        gs, cmap, upm, hmtx = font(fam, wt)
        sc = size / upm
        ls = track * upm
        adv = [hmtx[cmap.get(ord(c), cmap[ord('?')])][0] + ls for c in s]
        width = (sum(adv) - (ls if s else 0)) * sc
        dx = {'start': 0, 'middle': -width / 2, 'end': -width}[anchor]
        tr = 'translate(%s %s)' % (f(x), f(y)) + (' rotate(%s)' % f(rot) if rot else '') + ' translate(%s 0) scale(%s %s)' % (f(dx), ('%.5f' % sc).rstrip('0'), ('%.5f' % -sc).rstrip('0'))
        uses, u = [], 0
        for c, a in zip(s, adv):
            if c != ' ':
                gn = cmap.get(ord(c), cmap[ord('?')])
                k = (fam, wt, gn)
                if k not in self.glyphs:
                    pen = SVGPathPen(gs, ntos=lambda v: str(int(round(v))))
                    gs[gn].draw(pen)
                    self.glyphs[k] = ('t%d' % len(self.glyphs), pen.getCommands())
                uses.append('<use href="#%s"%s/>' % (self.glyphs[k][0], (' x="%d"' % round(u)) if u else ''))
            u += a
        self.add('<g transform="%s" fill="%s"%s>%s</g>' % (tr, fill, (' opacity="%s"' % f(opacity)) if opacity < 1 else '', ''.join(uses)))
    def save(self, key):
        defs = self.defs + ['<path id="%s" d="%s"/>' % (i, d) for i, d in self.glyphs.values()]
        s = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %s %s" width="%s" height="%s"><title>%s</title><defs>%s</defs>%s</svg>'
             % (f(self.w), f(self.h), f(self.w), f(self.h), self.title, ''.join(defs), ''.join(self.body)))
        open(os.path.join(OUT, key + '.svg'), 'w').write(s)
        print(key, len(s) // 1024, 'KB')

def arrow(x, y, L, c=GRAPH, w=0.8):
    return '<path d="M%s %sh%s" stroke="%s" stroke-width="%s"/><path d="M%s %sl-5 -2.6v5.2z" fill="%s"/>' % (f(x), f(y), f(L), c, f(w), f(x + L), f(y), c)

def P(pts): return 'M' + 'L'.join('%s %s' % (f(x), f(y)) for x, y in pts)
def line(x1, y1, x2, y2, c, w=0.6, **kw):
    extra = ''.join(' %s="%s"' % (k.replace('_', '-'), v) for k, v in kw.items())
    return '<path d="M%s %sL%s %s" stroke="%s" stroke-width="%s" fill="none"%s/>' % (f(x1), f(y1), f(x2), f(y2), c, f(w), extra)
def path(d, fill='none', stroke=None, w=None, **kw):
    extra = ''.join(' %s="%s"' % (k.replace('_', '-'), v) for k, v in kw.items())
    return '<path d="%s" fill="%s"%s%s%s/>' % (d, fill, (' stroke="%s"' % stroke) if stroke else '', (' stroke-width="%s"' % f(w)) if w is not None else '', extra)
def circle(cx, cy, r, fill, **kw):
    extra = ''.join(' %s="%s"' % (k.replace('_', '-'), v) for k, v in kw.items())
    return '<circle cx="%s" cy="%s" r="%s" fill="%s"%s/>' % (f(cx), f(cy), f(r), fill, extra)
def rect(x, y, w, h, fill, **kw):
    extra = ''.join(' %s="%s"' % (k.replace('_', '-'), v) for k, v in kw.items())
    return '<rect x="%s" y="%s" width="%s" height="%s" fill="%s"%s/>' % (f(x), f(y), f(w), f(h), fill, extra)

NOTE = ['C', 'C♯', 'D', 'E♭', 'E', 'F', 'F♯', 'G', 'A♭', 'A', 'B♭', 'B']

# ---------------------------------------------------------------- A: Metastaseis
def a1():
    S = Sheet(560, 360, 'Graph of straight string glissando lines whose bundles form curved envelopes, bars 309 to 314')
    S.paper(PAPER)
    x0, x1, y0, y1 = 56, 538, 22, 292
    S.add(rect(x0, y0, x1 - x0, y1 - y0, S.grid(4, 20, '#cfe0ee', '#a9c6df', 0.3, 0.6, x0, y0)))
    # pitch: G1 to C7 up the page, an octave every 48 units, the C's named in the margin
    def py(midi): return y1 - (midi - 31) * (y1 - y0) / (96 - 31)
    for m in range(36, 97, 12):
        S.add(line(x0 - 4, py(m), x0, py(m), GRAPH, 0.6))
        S.text(x0 - 7, py(m) + 3, 'C%d' % (m // 12 - 1), 9, GRAPH, anchor='end')
    # bars 309 to 314 across
    def bx(b): return x0 + (b - 309) * (x1 - x0) / 5
    for b in range(309, 315):
        S.add(line(bx(b), y1, bx(b), y1 + 5, GRAPH, 0.7))
        S.text(bx(b), y1 + 15, str(b), 9.5, GRAPH, anchor='middle')
    S.add(line(x0, y0, x0, y1, GRAPH, 0.9), line(x0, y1, x1, y1, GRAPH, 0.9))
    S.text(18, (y0 + y1) / 2, 'pitch', 10, GRAPH, rot=-90, anchor='middle')
    S.text(x0, 347.5, 'bars (time)', 9, GRAPH)
    S.add(arrow(x0 + 88, 344.5, 20))
    # 46 string parts, each a straight glissando between two pitches; each section a ruled
    # surface, its first pitches spread one way and its last the other, so the envelope curves
    sections = [('vn I', 12, RED, (68, 92), (52, 84), 309.4, 313.6), ('vn II', 12, BLUE, (60, 84), (80, 58), 309.6, 313.8),
                ('va', 8, GRAPH, (54, 72), (70, 50), 309.8, 314.0), ('vc', 8, SEPIA, (40, 62), (60, 38), 310.0, 314.0), ('cb', 6, GREEN, (32, 46), (44, 33), 310.2, 314.0)]
    rnd = random.Random(3)
    for name, n, c, (pa, pb), (qa, qb), t0, t1 in sections:
        ls = []
        for k in range(n):
            u = k / (n - 1)
            p0, p1 = pa + (pb - pa) * u, qa + (qb - qa) * u
            a0, a1 = t0 + rnd.uniform(-0.05, 0.05), t1 - rnd.uniform(0, 0.08)
            ls.append('M%s %sL%s %s' % (f(bx(a0)), f(py(p0)), f(bx(a1)), f(py(p1))))
            S.add(circle(bx(a0), py(p0), 1.3, c), circle(bx(a1), py(p1), 1.3, c))
        S.add(path(''.join(ls), stroke=c, w=0.75, opacity='0.9'))
    # the legend, in a row under the graph
    for k, (name, n, c, *_) in enumerate(sections):
        lx = x0 + 110 + k * 80
        S.add(line(lx, 344, lx + 16, 344, c, 1.4))
        S.text(lx + 20, 347.5, '%s %d' % (name, n), 9, GRAPH)
    S.text(x0 + 8, y0 + 16, '46 strings, a part each: straight lines, curved surfaces', 13, GRAPH, fam='Caveat', opacity=0.85)
    S.save('a1')

# ---------------------------------------------------------------- B: Philips Pavilion
def a2():
    S = Sheet(420, 280, 'Postcard drawing of a tent-like pavilion built from ruled, saddle-shaped concrete shells')
    S.add(rect(0, 0, 420, 280, '#f6f1e4'))
    ix, iy, iw, ih = 12, 12, 396, 210
    S.add(rect(ix, iy, iw, ih, S.lin([(0, '#c9dbe6'), (0.7, '#eef2ee'), (1, '#f4efe0')])))
    gy = iy + ih * 0.78
    S.add(rect(ix, gy, iw, iy + ih - gy, S.lin([(0, '#cbbd9c'), (1, '#b3a27c')])))
    # three hyperbolic paraboloid shells, each ruled by its two families of straight lines
    def shell(a, b, c, d, n, w=0.45, fill='#eae6dc'):
        S.add(path(P([a, b, c, d]) + 'Z', fill=fill, opacity='0.9'))
        L = lambda p, q, t: (p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t)
        dd = ''
        for i in range(n + 1):
            t = i / n
            p, q = L(a, b, t), L(d, c, t); dd += 'M%s %sL%s %s' % (f(p[0]), f(p[1]), f(q[0]), f(q[1]))
            p, q = L(a, d, t), L(b, c, t); dd += 'M%s %sL%s %s' % (f(p[0]), f(p[1]), f(q[0]), f(q[1]))
        S.add(path(dd, stroke='#5f5a50', w=w, opacity='0.8'))
        S.add(path(P([a, b, c, d]) + 'Z', stroke='#3b3832', w=0.8))
    shell((ix + 70, gy), (ix + 150, iy + 70), (ix + 200, gy - 8), (ix + 160, gy), 22, fill='#e3ddd0')
    shell((ix + 150, iy + 70), (ix + 268, iy + 18), (ix + 300, gy - 4), (ix + 200, gy - 8), 26)
    shell((ix + 268, iy + 18), (ix + 352, gy), (ix + 320, gy), (ix + 300, gy - 4), 18, fill='#d9d2c3')
    # the shells' shadow on the ground, and visitors for scale
    S.add(path(P([(ix + 70, gy), (ix + 352, gy), (ix + 390, gy + 14), (ix + 120, gy + 14)]) + 'Z', fill='#8f7f5e', opacity='0.35'))
    for k, px in enumerate((ix + 52, ix + 60, ix + 210, ix + 216, ix + 360)):
        S.add(circle(px, gy + 8 - 9.5, 1.5, '#3b3832'), path('M%s %sl-1.8 8h3.6z' % (f(px), f(gy + 8 - 8)), fill='#3b3832'))
    S.add(rect(ix, iy, iw, ih, 'none', stroke='#ffffff', stroke_width='3'))
    # the card's lower field: the place, handwritten, and a stamp
    S.text(ix + 4, 252, 'Bruxelles · Expo 58', 26, '#2c3e5a', fam='Caveat', wt=700)
    S.text(ix + 6, 270, 'LE PAVILLON PHILIPS · LE CORBUSIER, I. XENAKIS', 7, '#5d5851', fam='Work Sans', wt=600, track=0.12)
    sx, sy = 352, 230
    perf = ''.join('M%s %sa1.6 1.6 0 1 0 0.01 0' % (f(sx + k * 5), f(sy)) for k in range(0, 10)) + ''.join('M%s %sa1.6 1.6 0 1 0 0.01 0' % (f(sx + k * 5), f(sy + 42)) for k in range(0, 10))
    S.add(rect(sx - 2, sy, 48, 42, '#fbf5e6'), path(perf, fill='#f6f1e4'))
    S.add(rect(sx + 3, sy + 4, 38, 30, '#b5462b'), path(P([(sx + 7, sy + 31), (sx + 18, sy + 11), (sx + 26, sy + 30), (sx + 33, sy + 16), (sx + 38, sy + 31)]), stroke='#fbf5e6', w=1.2))
    S.text(sx + 22, sy + 39.6, 'BELGIQUE 3F', 4.4, '#5d5851', fam='Work Sans', wt=600, anchor='middle', track=0.1)
    S.save('a2')

# ---------------------------------------------------------------- C: Pithoprakta
def b1():
    S = Sheet(560, 340, 'A cloud of short sloping glissando strokes and pizzicato dots, denser in the middle')
    S.paper(PAPER)
    x0, x1, y0, y1 = 40, 540, 20, 300
    S.add(rect(x0, y0, x1 - x0, y1 - y0, S.grid(5, 25, '#ece4cf', '#dccfae', 0.3, 0.55, x0, y0)))
    S.add(line(x0, y0, x0, y1, GRAPH, 0.9), line(x0, y1, x1, y1, GRAPH, 0.9))
    S.text(16, (y0 + y1) / 2, 'pitch', 10, GRAPH, rot=-90, anchor='middle')
    S.text(x1 - 30, y1 + 18.5, 'time', 10, GRAPH, anchor='end')
    S.add(arrow(x1 - 24, y1 + 15, 22))
    rnd = random.Random(1956)
    # glissandi: speeds by Maxwell-Boltzmann (the length of a 3-D normal), up or down at random;
    # their places thickest in the middle of the field
    strokes = {BLUE: '', RED: '', GRAPH: ''}
    for k in range(520):
        tx = min(max(rnd.gauss(0.5, 0.2), 0.02), 0.96); ty = min(max(rnd.gauss(0.5, 0.22), 0.04), 0.96)
        v = math.sqrt(sum(rnd.gauss(0, 1) ** 2 for _ in range(3)))
        ang = math.atan(v * 0.55) * rnd.choice((-1, 1))
        L = rnd.uniform(9, 20)
        x, y = x0 + tx * (x1 - x0), y1 - ty * (y1 - y0)
        c = rnd.choice((BLUE, BLUE, RED, GRAPH))
        strokes[c] += 'M%s %sl%s %s' % (f(x), f(y), f(L * math.cos(ang)), f(-L * math.sin(ang)))
    for c, d in strokes.items(): S.add(path(d, stroke=c, w=0.8, stroke_linecap='round', opacity='0.85'))
    dots = ''
    for k in range(130):
        x = x0 + min(max(rnd.gauss(0.5, 0.28), 0.02), 0.98) * (x1 - x0); y = y1 - min(max(rnd.gauss(0.5, 0.3), 0.03), 0.97) * (y1 - y0)
        dots += 'M%s %sh.01' % (f(x), f(y))
    S.add(path(dots, stroke=GRAPH, w=2.4, stroke_linecap='round'))
    # an inset: the distribution of the speeds
    ix, iy, iw, ih = x1 - 190, y0 + 12, 178, 80
    S.add(rect(ix, iy, iw, ih, PAPER, opacity='0.94'), rect(ix, iy, iw, ih, 'none', stroke=GRAPH, stroke_width='0.6'))
    pts = []
    for k in range(61):
        v = k / 60 * 4
        p = math.sqrt(2 / math.pi) * v * v * math.exp(-v * v / 2)
        pts.append((ix + 10 + v / 4 * (iw - 20), iy + ih - 14 - p / 0.6 * (ih - 30)))
    S.add(path(P(pts), stroke=RED, w=1.1), line(ix + 10, iy + ih - 14, ix + iw - 8, iy + ih - 14, GRAPH, 0.6))
    S.text(ix + 8, iy + 14, 'speeds: Maxwell–Boltzmann', 8, GRAPH)
    S.text(ix + iw - 8, iy + ih - 4, 'v', 8, GRAPH, anchor='end')
    S.text(x0 + 10, y1 - 10, 'pizz. ·   gliss. /', 13, GRAPH, fam='Caveat', opacity=0.85)
    S.save('b1')

# ---------------------------------------------------------------- D: Arborescences
def c1():
    S = Sheet(560, 320, 'A single line branching like a tree from left to right, with a faint mirrored copy in red')
    S.paper(VELLUM, 0.05)
    y_mid = 160
    for k in range(-12, 13):
        S.add(line(20, y_mid + k * 10, 540, y_mid + k * 10, '#b9a985', 0.5 if k % 6 == 0 else 0.25, opacity='0.6'))
    rnd = random.Random(1973)
    paths = []
    def grow(x, y, dy, depth, w):
        L = rnd.uniform(38, 60)
        nx, ny = x + L, y + dy * L + rnd.uniform(-5, 5)
        # near the sheet's edges a branch turns back rather than running along them
        if ny < 84: ny, dy = 84 + (84 - ny) * 0.3, abs(dy) * 0.6
        elif ny > 236: ny, dy = 236 - (ny - 236) * 0.3, -abs(dy) * 0.6
        paths.append((x, y, nx, ny, w))
        if nx > 520 or depth > 6: return
        k = rnd.choice((2, 3)) if depth < 2 else rnd.choice((1, 1, 1, 2))
        for i in range(k):
            ndy = dy * 0.55 + rnd.uniform(-0.3, 0.3) + (i - (k - 1) / 2) * 0.5
            grow(nx, ny, max(-0.6, min(0.6, ndy)), depth + 1, max(0.55, w * 0.8))
    paths.append((24, y_mid, 70, y_mid, 1.8))
    grow(70, y_mid, 0.0, 0, 1.6)
    def curve(x, y, nx, ny):
        return 'M%s %sC%s %s %s %s %s %s' % (f(x), f(y), f(x + (nx - x) * 0.45), f(y), f(x + (nx - x) * 0.55), f(ny), f(nx), f(ny))
    # the mirror first, faint and in red: the tree inverted about the middle line
    S.add(path(''.join(curve(x, 2 * y_mid - y, nx, 2 * y_mid - ny) for x, y, nx, ny, w in paths), stroke=RED, w=0.7, opacity='0.3'))
    for w in sorted(set(round(p[4], 1) for p in paths)):
        S.add(path(''.join(curve(x, y, nx, ny) for x, y, nx, ny, ww in paths if round(ww, 1) == w), stroke='#1f1d1a', w=w, stroke_linecap='round'))
    S.add(circle(24, y_mid, 2.2, '#1f1d1a'))
    S.text(30, 28, 'arborescence', 15, GRAPH, fam='Caveat', wt=700)
    S.text(30, 44, 'one line, branching, on the plane of pitch and time', 12, GRAPH, fam='Caveat', opacity=0.8)
    S.text(530, 300, 'mirror (inversion), in red', 12, RED, fam='Caveat', anchor='end', opacity=0.8)
    S.add(line(20, 300, 180, 300, GRAPH, 0.6))
    S.text(184, 303, 'time', 9, GRAPH)
    S.add(arrow(226, 300, 22))
    S.save('c1')

# ---------------------------------------------------------------- E: Nomos Alpha
def d1():
    S = Sheet(440, 330, 'A cube with vertices numbered 1 to 8 and three dashed rotation axes: through faces, through a diagonal, through edges')
    S.paper(PAPER)
    S.add(rect(0, 0, 440, 330, S.grid(5, 25, '#ece4cf', '#dccfae')))
    # an oblique view of the cube
    cx, cy, a = 200, 186, 108
    ox, oy = 48, -40
    V = {1: (cx - a / 2, cy + a / 2), 2: (cx + a / 2, cy + a / 2), 3: (cx + a / 2, cy - a / 2), 4: (cx - a / 2, cy - a / 2)}
    for k in range(4): V[k + 5] = (V[k + 1][0] + ox, V[k + 1][1] + oy)
    hidden = [(1, 5), (5, 6), (5, 8)]
    edges = [(1, 2), (2, 3), (3, 4), (4, 1), (2, 6), (3, 7), (4, 8), (6, 7), (7, 8)]
    S.add(path(''.join('M%s %sL%s %s' % (f(V[p][0]), f(V[p][1]), f(V[q][0]), f(V[q][1])) for p, q in hidden), stroke=GRAPH, w=0.8, stroke_dasharray='4 3', opacity='0.7'))
    S.add(path(P([V[4], V[3], V[7], V[8]]) + 'Z', fill='#e8dfc8', opacity='0.7'), path(P([V[2], V[6], V[7], V[3]]) + 'Z', fill='#d8ccb0', opacity='0.7'))
    S.add(path(''.join('M%s %sL%s %s' % (f(V[p][0]), f(V[p][1]), f(V[q][0]), f(V[q][1])) for p, q in edges), stroke='#1f1d1a', w=1.6, stroke_linejoin='round'))
    # the three kinds of axis, each with an arrow of its turn
    fc = ((V[1][0] + V[3][0]) / 2 + ox / 2, (V[1][1] + V[3][1]) / 2 + oy / 2)
    def axis(p, q, c, label, lx, ly, anchor='start'):
        S.add(line(p[0], p[1], q[0], q[1], c, 1.1, stroke_dasharray='6 3'))
        S.text(lx, ly, label, 11, c, fam='Caveat', wt=700, anchor=anchor)
    axis((fc[0], cy - a / 2 - 52 + oy / 2), (fc[0], cy + a / 2 + 46 + oy / 2), BLUE, 'face axis: 90°, 180°, 270° (×3 = 9)', fc[0] + 6, 30)
    d0, d1_ = V[1], V[7]
    ext = lambda p, q, t: (p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t)
    axis(ext(d0, d1_, -0.35), ext(d0, d1_, 1.35), RED, 'diagonal: 120°, 240° (×4 = 8)', 430, 292, 'end')
    m1 = ((V[1][0] + V[5][0]) / 2, (V[1][1] + V[5][1]) / 2); m2 = ((V[3][0] + V[7][0]) / 2, (V[3][1] + V[7][1]) / 2)
    axis(ext(m1, m2, -0.4), ext(m1, m2, 1.4), GREEN, 'edge axis: 180° (×6 = 6)', 24, 300)
    for (x, y), c in ((( fc[0], cy - a / 2 - 40 + oy / 2), BLUE), (ext(d0, d1_, 1.22), RED)):
        S.add(path('M%s %sa14 5 0 1 1 -1 0.4' % (f(x + 14), f(y)), stroke=c, w=0.9), path('M%s %sl-4 -2.6l0.4 4.6z' % (f(x + 13), f(y + 0.4)), fill=c))
    for k, (x, y) in V.items():
        S.add(circle(x, y, 8.6, PAPER), circle(x, y, 8.6, 'none', stroke='#1f1d1a', stroke_width='1.1'))
        S.text(x, y + 4, str(k), 11, '#1f1d1a', wt=700, anchor='middle')
    S.text(420, 318, 'identity 1 + 9 + 8 + 6 = 24 rotations', 9, GRAPH, anchor='end')
    S.save('d1')

# ---------------------------------------------------------------- F: three sieves
def e1():
    S = Sheet(600, 300, "Three sieves drawn on lines: a seventeen-semitone scale, a forty-pulse rhythm, and the sample deck's sieve 2 3 7 8 12 13 17 18")
    S.paper(MANU, 0.03)
    for y in range(18, 300, 10): S.add(line(14, y, 586, y, '#e3dccb', 0.3))
    # the scale: two periods of 17 semitones as keys, the members inked
    S.text(20, 30, 'JONCHAIES · 17@{0,1,4,5,7,11,12,16} · semitones', 9.5, GRAPH, fam='Work Sans', wt=600, track=0.08)
    mem = {0, 1, 4, 5, 7, 11, 12, 16}
    x, w, y = 20, 16.4, 40
    for k in range(34):
        on = (k % 17) in mem
        S.add(rect(x + k * w, y, w - 2, 34, '#1f1d1a' if on else '#fffdf6'), rect(x + k * w, y, w - 2, 34, 'none', stroke='#55534c', stroke_width='0.6'))
        if on: S.add(rect(x + k * w + 2, y + 2, 2.2, 30, '#ffffff', opacity='0.22'))
        if k % 17 == 0: S.add(line(x + k * w - 1.2, y - 6, x + k * w - 1.2, y + 42, RED, 1.4))
    steps = [b - a for a, b in zip(sorted(mem), sorted(mem)[1:] + [17])]
    xx = x
    for k, sv in enumerate(sorted(mem)):
        pass
    for per in (0, 17):
        for a, st in zip(sorted(mem), steps):
            S.text(x + (per + a) * w + st * w / 2 - 1, y + 50, str(st), 8.5, RED, anchor='middle')
    # the rhythm: forty pulses, the sieve's members as heads, the rest as dots, beamed in 8s
    S.text(20, 128, 'PSAPPHA · RHYTHMIC SIEVE · PERIOD 40 PULSES · MODULI 8 AND 5', 9.5, GRAPH, fam='Work Sans', wt=600, track=0.08)
    rm = {0, 1, 3, 4, 6, 8, 10, 11, 12, 13, 14, 16, 17, 19, 20, 22, 23, 25, 27, 28, 29, 31, 33, 35, 36, 37, 38}
    y = 150
    S.add(line(20, y, 580, y, '#55534c', 0.5))
    for k in range(40):
        px = 26 + k * 13.9
        if k in rm: S.add(circle(px, y, 4.6, BLUE), circle(px - 1.3, y - 1.4, 1.3, '#ffffff', opacity='0.4'))
        else: S.add(circle(px, y, 1.4, '#8a857a'))
        if k % 8 == 0:
            S.add(line(px, y + 9, px, y + 15, GRAPH, 0.7))
            S.text(px, y + 25, str(k), 8.5, GRAPH, anchor='middle')
    # the sample deck's sieve on the integers 0 to 19
    S.text(20, 212, '5@2 | 5@3 · THE SAMPLE DECK · 0 TO 19', 9.5, GRAPH, fam='Work Sans', wt=600, track=0.08)
    y = 224
    for k in range(20):
        on = k % 5 in (2, 3)
        S.add(rect(20 + k * 22, y, 18, 18, RED if on else '#fffdf6'), rect(20 + k * 22, y, 18, 18, 'none', stroke='#55534c', stroke_width='0.6'))
        S.text(29 + k * 22, y + 32, str(k), 8.5, GRAPH, anchor='middle')
    S.text(470, 238, '2 3 7 8 12 13 17 18', 13, RED, fam='Caveat', wt=700)
    S.save('e1')

# ---------------------------------------------------------------- G: a UPIC page
def f1():
    S = Sheet(560, 320, 'A page of pen-drawn wavy arcs in bundles, pitch against time')
    S.paper(PAPER, 0.03)
    x0, x1, y0, y1 = 24, 536, 18, 290
    for k in range(1, 12): S.add(line(x0 + k * (x1 - x0) / 12, y0, x0 + k * (x1 - x0) / 12, y1, '#d9d3c4', 0.4))
    S.add(rect(x0, y0, x1 - x0, y1 - y0, 'none', stroke='#8a857a', stroke_width='0.8'))
    rnd = random.Random(1978)
    def stroke(pts, w0, w1, c):
        # a pen line whose pressure swells and fades: an outline of the left and right edges
        L, R = [], []
        for i, (x, y) in enumerate(pts):
            t = i / (len(pts) - 1)
            w = w0 + (w1 - w0) * math.sin(math.pi * t) ** 0.8
            (xa, ya) = pts[max(0, i - 1)]; (xb, yb) = pts[min(len(pts) - 1, i + 1)]
            nx, ny = -(yb - ya), xb - xa; nl = math.hypot(nx, ny) or 1
            L.append((x + nx / nl * w / 2, y + ny / nl * w / 2)); R.append((x - nx / nl * w / 2, y - ny / nl * w / 2))
        return P(L + R[::-1]) + 'Z'
    bundles = [(40, 220, 260, 120, 9, 0.8, -0.9, BLUE), (180, 70, 380, 160, 7, 1.0, 1.2, '#1f1d1a'), (300, 230, 520, 200, 8, 0.6, 0.6, BLUE),
               (80, 110, 200, 60, 5, 1.2, -1.6, RED), (360, 60, 520, 90, 6, 0.9, 1.0, '#1f1d1a'), (230, 250, 330, 260, 4, 0.5, 2.0, SEPIA)]
    for xs, ys, xe, ye, n, amp, freq, c in bundles:
        d = ''
        for k in range(n):
            off = (k - n / 2) * 3.2
            ph = rnd.uniform(0, 1)
            pts = []
            for s_ in range(40):
                t = s_ / 39
                x = xs + (xe - xs) * t
                y = ys + (ye - ys) * t + off + amp * 18 * math.sin(2 * math.pi * (freq * t + ph * 0.15)) * (0.6 + 0.4 * t)
                pts.append((x, y))
            d += stroke(pts, 0.4, rnd.uniform(1.0, 1.8), c)
        S.add(path(d, fill=c, opacity='0.88'))
    S.text(x0, y1 + 18, 'UPIC · drawn arcs: pitch over time', 9, GRAPH)
    S.text(x1 - 28, y1 + 18, 'time', 9, GRAPH, anchor='end')
    S.add(arrow(x1 - 24, y1 + 15, 22))
    S.save('f1')

# ---------------------------------------------------------------- I: Achorripsis
def i1():
    S = Sheet(640, 330, 'A matrix of 28 columns of time by 7 rows of timbre; most of its 196 cells are empty, and the rest hold 1, 2, 3 or, once, 4 events')
    S.paper(PAPER)
    S.add(rect(0, 0, 640, 330, S.grid(4, 20, '#efe7d4', '#e2d6bb')))
    x0, y0, cw, ch = 82, 46, 19.4, 26
    counts = [0] * 107 + [1] * 65 + [2] * 19 + [3] * 4 + [4] * 1
    rnd = random.Random(1957); rnd.shuffle(counts)
    shade = ['#fffdf6', '#efe2c4', '#dfc796', '#c79f5f', '#a36f35']
    S.text(x0, 24, 'TIME (28 COLUMNS)', 9, GRAPH, fam='Work Sans', wt=600, track=0.12)
    for c in range(28):
        if c % 2 == 0 or c == 27: S.text(x0 + c * cw + cw / 2, 40, str(c + 1), 8.5, GRAPH, anchor='middle')
    S.text(26, y0 + 3.5 * ch, 'TIMBRE', 9, GRAPH, fam='Work Sans', wt=600, rot=-90, anchor='middle', track=0.12)
    roman = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII']
    for r in range(7):
        S.text(x0 - 10, y0 + r * ch + ch / 2 + 4, roman[r], 10, GRAPH, wt=700, anchor='end')
        for c in range(28):
            v = counts[r * 28 + c]
            S.add(rect(x0 + c * cw, y0 + r * ch, cw, ch, shade[v]))
            if v: S.text(x0 + c * cw + cw / 2, y0 + r * ch + ch / 2 + 4, str(v), 11, '#2a2216' if v < 3 else '#fffaf0', wt=700, anchor='middle')
    grid = ''.join('M%s %sV%s' % (f(x0 + c * cw), f(y0), f(y0 + 7 * ch)) for c in range(29)) + ''.join('M%s %sH%s' % (f(x0), f(y0 + r * ch), f(x0 + 28 * cw)) for r in range(8))
    S.add(path(grid, stroke='#8a7a5a', w=0.5))
    S.add(rect(x0, y0, 28 * cw, 7 * ch, 'none', stroke='#2a2216', stroke_width='1.4'))
    for c in range(4, 28, 4): S.add(line(x0 + c * cw, y0, x0 + c * cw, y0 + 7 * ch, '#2a2216', 0.9))
    ly = y0 + 7 * ch + 26
    for k, (v, n) in enumerate(((0, 107), (1, 65), (2, 19), (3, 4), (4, 1))):
        lx = x0 + k * 108
        S.add(rect(lx, ly - 9, 12, 12, shade[v]), rect(lx, ly - 9, 12, 12, 'none', stroke='#8a7a5a', stroke_width='0.6'))
        S.text(lx + 18, ly + 1, '%d: %d' % (v, n), 9.5, GRAPH)
    S.text(x0, ly + 24, 'events per cell: number of cells · 196 cells · mean 0.6 · Poisson', 9.5, GRAPH, wt=700)
    S.text(x0 + 28 * cw, ly + 44, 'the counts are his; the places are chance', 12, SEPIA, fam='Caveat', anchor='end')
    S.save('i1')

# ---------------------------------------------------------------- J: Analogique screens
def j1():
    S = Sheet(640, 344, 'Eight small panels lettered A to H, each a cloud of short grains of sound placed by pitch and loudness, some dense and some sparse')
    S.paper(PAPER, 0.03)
    S.text(24, 26, 'SCREENS · PITCH (3 REGISTERS) BY LOUDNESS · HALF A BAR EACH', 9.5, GRAPH, fam='Work Sans', wt=600, track=0.1)
    rnd = random.Random(1958)
    dens = [0.9, 0.12, 0.7, 0.3, 1.0, 0.08, 0.55, 0.4]
    for k in range(8):
        col, row = k % 4, k // 4
        x, y, w, h = 24 + col * 152, 42 + row * 150, 136, 112
        S.add(rect(x + 1.5, y + 2, w, h, '#000', opacity='0.06'), rect(x, y, w, h, '#fffdf6'), rect(x, y, w, h, 'none', stroke='#55534c', stroke_width='0.8'))
        for k2 in (1, 2): S.add(line(x, y + k2 * h / 3, x + w, y + k2 * h / 3, '#d9d3c4', 0.6, stroke_dasharray='2 2'))
        for k2 in (1, 2, 3): S.add(line(x + k2 * w / 4, y, x + k2 * w / 4, y + h, '#ece6d6', 0.5))
        n = int(dens[k] * 140)
        reg = rnd.choice((0, 1, 2))
        lv = {c: '' for c in ('#1f1d1a', BLUE)}
        for g_ in range(n):
            band = reg if rnd.random() < 0.6 else rnd.choice((0, 1, 2))
            gx = x + 6 + rnd.random() * (w - 16)
            gy = y + h - (band + rnd.random()) * h / 3
            L = rnd.uniform(2, 7)
            lv[rnd.choice(('#1f1d1a', '#1f1d1a', BLUE))] += 'M%s %sh%s' % (f(gx), f(gy), f(L))
        for c, d in lv.items():
            if d: S.add(path(d, stroke=c, w=1.6, stroke_linecap='round'))
        S.text(x, y + h + 16, 'ABCDEFGH'[k], 12, GRAPH, fam='Work Sans', wt=600)
        S.text(x + w, y + h + 15, 'density %d' % n, 8.5, GRAPH, anchor='end')
    S.save('j1')

# ---------------------------------------------------------------- L: Terretektorh
def l1():
    S = Sheet(520, 470, 'Plan of a round hall: 88 players, marked by section, are scattered through rings of audience seats')
    S.paper(PAPER)
    cx, cy, R = 260, 222, 200
    S.add(circle(cx, cy, R + 6, '#e9e1cd'), circle(cx, cy, R + 6, 'none', stroke='#1f1d1a', stroke_width='2.4'))
    S.add(circle(cx, cy, R, '#f7f2e4'))
    rnd = random.Random(1966)
    # rings of seats, broken by four aisles
    seats = ''
    rings = list(range(30, int(R) - 6, 13))
    cand = []
    for r in rings:
        n = int(2 * math.pi * r / 10)
        for k in range(n):
            a = 2 * math.pi * k / n
            if any(abs(((a - ax + math.pi) % (2 * math.pi)) - math.pi) < 7 / r for ax in (0, math.pi / 2, math.pi, 3 * math.pi / 2)): continue
            x, y = cx + r * math.cos(a), cy + r * math.sin(a)
            cand.append((x, y, a))
    rnd.shuffle(cand)
    players, seats = cand[:88], cand[88:]
    S.add(path(''.join('M%s %sh.01' % (f(x), f(y)) for x, y, a in seats), stroke='#cdbf9e', w=3.6, stroke_linecap='square'))
    kinds = ['s'] * 60 + ['w'] * 12 + ['b'] * 13 + ['p'] * 3
    rnd.shuffle(kinds)
    marks = {'s': '', 'w': '', 'b': '', 'p': ''}
    for (x, y, a), kd in zip(players, kinds):
        if kd == 's': marks[kd] += 'M%s %sa3.4 3.4 0 1 0 0.01 0' % (f(x - 3.4), f(y))
        elif kd == 'w': marks[kd] += 'M%s %sl4 6.6h-8z' % (f(x), f(y - 4.4))
        elif kd == 'b': marks[kd] += 'M%s %sh7v7h-7z' % (f(x - 3.5), f(y - 3.5))
        else: marks[kd] += 'M%s %sl5 5-5 5-5-5z' % (f(x), f(y - 5))
    style = {'s': '#1f1d1a', 'w': GREEN, 'b': RED, 'p': BLUE}
    for kd, d in marks.items(): S.add(path(d, fill=style[kd]))
    # the conductor at the centre, and the doors
    S.add(circle(cx, cy, 10, '#fffdf6'), circle(cx, cy, 10, 'none', stroke='#1f1d1a', stroke_width='1.2'), circle(cx, cy, 3, '#1f1d1a'))
    for a in (math.pi / 4, 5 * math.pi / 4):
        x, y = cx + (R + 3) * math.cos(a), cy + (R + 3) * math.sin(a)
        S.add(circle(x, y, 7, PAPER))
    ly = 448
    for k, (kd, lab) in enumerate((('s', '60 strings'), ('w', '12 woodwinds'), ('b', '13 brass'), ('p', '3 percussion'))):
        lx = 40 + k * 118
        if kd == 's': S.add(circle(lx, ly - 3, 3.6, style[kd]))
        elif kd == 'w': S.add(path('M%s %sl4.2 7h-8.4z' % (f(lx), f(ly - 7)), fill=style[kd]))
        elif kd == 'b': S.add(rect(lx - 3.5, ly - 6.5, 7, 7, style[kd]))
        else: S.add(path('M%s %sl5 5-5 5-5-5z' % (f(lx), f(ly - 8)), fill=style[kd]))
        S.text(lx + 10, ly + 0.5, lab, 9.5, GRAPH)
    S.text(cx + 14, cy - 12, 'chef', 13, GRAPH, fam='Caveat', wt=700)
    S.save('l1')

if __name__ == '__main__':
    import sys
    for k in (sys.argv[1:] or ['a1', 'a2', 'b1', 'c1', 'd1', 'e1', 'f1', 'i1', 'j1', 'l1']): globals()[k]()
