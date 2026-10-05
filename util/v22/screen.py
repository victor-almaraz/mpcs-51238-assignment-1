# v22's computer: the pictures of its documents as SVG files (v22/assets/screen/), drawn in
# the room's flat mid-century manner and palette: the desk picture (a night at Persepolis),
# the Read Me's glissandi, the nine About plates, Hugo Ball, and Tzara's hat.
# Type in them is outlined from the bundled faces, each glyph defined once in its file.
import os as _os; UTIL = _os.path.normpath(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..')); REPO = _os.path.dirname(UTIL)
import math, random, os
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen

REPO = REPO
OUT = REPO + '/v22/assets/screen'
os.makedirs(OUT, exist_ok=True)

P = dict(ink='#1e1d1b', soft='#5d5851', paper='#f7f4ec', cream='#efe6d2', sand='#e4d8c0', stone='#d8d1c3',
         blue='#2b4560', blue_l='#4f7194', sky='#a9c1d3', accent='#b5462b', ochre='#c99a2e', sage='#7d8a78',
         slate='#49555a', teak='#9a6136', walnut='#4e3727', green='#dbe7d2', mint='#b9cfae')

def f(v):
    s = ('%.1f' % v).rstrip('0').rstrip('.')
    return '0' if s in ('-0', '') else s

def rect(x, y, w, h, fill, rx=0, **kw):
    a = ''.join(' %s="%s"' % (k.replace('_', '-'), v) for k, v in kw.items())
    return '<rect x="%s" y="%s" width="%s" height="%s"%s fill="%s"%s/>' % (f(x), f(y), f(w), f(h), ' rx="%s"' % f(rx) if rx else '', fill, a)

def circle(cx, cy, r, fill, **kw):
    a = ''.join(' %s="%s"' % (k.replace('_', '-'), v) for k, v in kw.items())
    return '<circle cx="%s" cy="%s" r="%s" fill="%s"%s/>' % (f(cx), f(cy), f(r), fill, a)

def path(d, fill='none', **kw):
    a = ''.join(' %s="%s"' % (k.replace('_', '-'), v) for k, v in kw.items())
    return '<path d="%s" fill="%s"%s/>' % (d, fill, a)

def lin(id, stops, x2=0, y2=1, x1=0, y1=0):
    return '<linearGradient id="%s" x1="%s" y1="%s" x2="%s" y2="%s">%s</linearGradient>' % (
        id, x1, y1, x2, y2, ''.join('<stop offset="%s" stop-color="%s"%s/>' % (o, c, ' stop-opacity="%s"' % op if op != 1 else '') for o, c, op in [(s + (1,))[:3] for s in stops]))

def rad(id, stops, cx=0.5, cy=0.5, r=0.5):
    return '<radialGradient id="%s" cx="%s" cy="%s" r="%s">%s</radialGradient>' % (
        id, cx, cy, r, ''.join('<stop offset="%s" stop-color="%s"%s/>' % (o, c, ' stop-opacity="%s"' % op if op != 1 else '') for o, c, op in [(s + (1,))[:3] for s in stops]))

# ---------------------------------------------------------------- outlined type
FONTS = {}
def face(slug, weight, style='normal'):
    k = (slug, weight, style)
    if k not in FONTS:
        t = TTFont('%s/fonts/%s/%s-latin-%d-%s.woff2' % (REPO, slug, slug, weight, style))
        FONTS[k] = (t.getGlyphSet(), t.getBestCmap(), t['head'].unitsPerEm, t['hmtx'])
    return FONTS[k]

class Type:
    """text as outlines; each glyph is defined once per file and used again"""
    def __init__(self): self.glyphs = {}
    def text(self, x, y, s, size, fill, slug='work-sans', weight=400, anchor='start', ls=0, style='normal', opacity=None):
        gs, cmap, upm, hmtx = face(slug, weight, style)
        sc = size / upm
        lsu = ls / sc
        names = [cmap.get(ord(c), cmap[ord('?')]) for c in s]
        width = sum(hmtx[n][0] + lsu for n in names) - (lsu if s else 0)
        if anchor == 'middle': x -= width * sc / 2
        elif anchor == 'end': x -= width * sc
        out, u = [], 0
        for c, n in zip(s, names):
            if c != ' ':
                key = (slug, weight, style, n)
                if key not in self.glyphs:
                    pen = SVGPathPen(gs, ntos=lambda v: str(int(round(v))))
                    gs[n].draw(pen)
                    self.glyphs[key] = ('t%d' % len(self.glyphs), pen.getCommands())
                out.append('<use href="#%s"%s/>' % (self.glyphs[key][0], ' x="%d"' % round(u) if u else ''))
            u += hmtx[n][0] + lsu
        op = ' opacity="%s"' % opacity if opacity is not None else ''
        return '<g transform="translate(%s %s) scale(%s %s)" fill="%s"%s>%s</g>' % (f(x), f(y), ('%.5f' % sc).rstrip('0'), ('%.5f' % -sc).rstrip('0'), fill, op, ''.join(out))
    def defs(self):
        return ''.join('<path id="%s" d="%s"/>' % v for v in self.glyphs.values())

def save(name, w, h, body, defs='', T=None, title='', aspect=None):
    d = defs + (T.defs() if T else '')
    pa = ' preserveAspectRatio="%s"' % aspect if aspect else ''
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d"%s>%s%s%s</svg>'
           % (w, h, w, h, pa, '<title>%s</title>' % title if title else '', '<defs>%s</defs>' % d if d else '', body))
    open(os.path.join(OUT, name + '.svg'), 'w', encoding='utf-8').write(svg)
    print(name, len(svg) // 1024, 'KB')

# ---------------------------------------------------------------- the desk: Persepolis at night
def desktop():
    # The Polytope de Persépolis (1971): at night on the terrace of Persepolis, under the
    # mountain, children with torches climbing it in a winding line, searchlights over the
    # ruins. Flat layers, after the travel posters of the period; the icons' column is on the
    # right, so the mountain's peak and the beams' crossing are right of centre.
    random.seed(1971)
    W, H = 1600, 1000
    D = [lin('sky', [(0, '#0c1624'), (0.45, '#1b2e45'), (0.78, '#2d4562'), (1, '#4a5a6a')]),
         lin('beam', [(0, '#f4e8c8', 0), (0.55, '#f4e8c8', 0.10), (1, '#f4e8c8', 0.30)], 0, 1),
         lin('far', [(0, '#2a3e56'), (1, '#22344a')]),
         lin('mtn', [(0, '#1b2b3e'), (1, '#141f2e')]),
         lin('gnd', [(0, '#111a26'), (1, '#0a1019')]),
         rad('glow', [(0, '#f2a94a', 0.55), (0.4, '#e08a3a', 0.18), (1, '#e08a3a', 0)]),
         rad('torch', [(0, '#ffe2a0', 1), (0.35, '#f3b24c', 0.9), (1, '#f3b24c', 0)]),
         rad('moon', [(0, '#f6efdc', 0.35), (1, '#f6efdc', 0)])]
    o = [rect(0, 0, W, H, 'url(#sky)')]
    # stars, thinning toward the horizon
    st = []
    for k in range(170):
        x, y = random.uniform(0, W), random.uniform(0, 560) ** 1.0
        if random.random() < (y / 560) ** 1.5: continue
        st.append('M%s %sh0' % (f(x), f(y)))
    o.append(path(''.join(st), stroke='#f2ead8', stroke_width='1.6', stroke_linecap='round', opacity='.55'))
    big = ''.join('M%s %sh0' % (f(random.uniform(0, W)), f(random.uniform(20, 360))) for k in range(26))
    o.append(path(big, stroke='#fff6e0', stroke_width='2.6', stroke_linecap='round', opacity='.8'))
    # a low moon, a disc with its halo
    o.append(circle(250, 190, 120, 'url(#moon)'))
    o.append(circle(250, 190, 26, '#efe6cf', opacity='.92'))
    # the searchlights, from the terrace, crossing above the mountain
    for (bx, by, tx, spread) in [(1010, 772, 760, -1), (1150, 776, 1560, 1), (1080, 770, 1200, 0.2)]:
        a = math.atan2(-by, tx - bx); L = 1300
        ex, ey = bx + L * math.cos(a), by + L * math.sin(a)
        nx, ny = -math.sin(a), math.cos(a)
        w0, w1 = 4, 70
        d = 'M%s %sL%s %sL%s %sL%s %sz' % (f(bx + nx * w0), f(by + ny * w0), f(ex + nx * w1), f(ey + ny * w1), f(ex - nx * w1), f(ey - ny * w1), f(bx - nx * w0), f(by - ny * w0))
        D.append('<linearGradient id="b%d" gradientUnits="userSpaceOnUse" x1="%s" y1="%s" x2="%s" y2="%s"><stop offset="0" stop-color="#f4e8c8" stop-opacity=".34"/><stop offset=".7" stop-color="#f4e8c8" stop-opacity=".07"/><stop offset="1" stop-color="#f4e8c8" stop-opacity="0"/></linearGradient>'
                 % (bx, f(bx), f(by), f(ex), f(ey)))
        o.append(path(d, 'url(#b%d)' % bx))
    # the far range, then the mountain behind the terrace
    def ridge(pts):
        return 'M' + 'L'.join('%s %s' % (f(x), f(y)) for x, y in pts)
    far = [(0, 640)]
    for k in range(1, 33):
        x = k * 50
        far.append((x, 620 - 60 * math.sin(k * 0.5) - 25 * math.sin(k * 1.7 + 1) + random.uniform(-8, 8)))
    o.append(path(ridge(far) + 'L1600 1000L0 1000z', 'url(#far)'))
    mt = [(0, 780), (160, 742), (320, 700), (470, 640), (600, 585), (720, 528), (820, 486), (905, 452), (960, 440), (1010, 448),
          (1090, 478), (1190, 520), (1300, 566), (1420, 610), (1520, 650), (1600, 672)]
    pts = []
    for i in range(len(mt) - 1):
        (x0, y0), (x1, y1) = mt[i], mt[i + 1]
        for t in (0, 0.33, 0.66):
            pts.append((x0 + (x1 - x0) * t, y0 + (y1 - y0) * t + (random.uniform(-7, 7) if t else 0)))
    pts.append(mt[-1])
    o.append(path(ridge(pts) + 'L1600 1000L0 1000z', 'url(#mtn)'))
    # the torch-bearers' path: switchbacks up the mountain, a dotted line of fire
    sw = [(560, 770), (900, 742), (700, 712), (980, 682), (790, 650), (1040, 620), (860, 590), (1060, 560), (920, 530), (1010, 500), (955, 470)]
    tor, glow = [], []
    for i in range(len(sw) - 1):
        (x0, y0), (x1, y1) = sw[i], sw[i + 1]
        n = int(math.hypot(x1 - x0, y1 - y0) / 13)
        for k in range(n):
            t = k / n
            x, y = x0 + (x1 - x0) * t + random.uniform(-1.5, 1.5), y0 + (y1 - y0) * t + random.uniform(-1.5, 1.5)
            s = 1 - 0.55 * (770 - y) / 300
            tor.append(circle(x, y, 5.5 * s, 'url(#torch)'))
            glow.append('M%s %sh0' % (f(x), f(y)))
    o.append(''.join(tor))
    o.append(path(''.join(glow), stroke='#fff0c8', stroke_width='2', stroke_linecap='round'))
    # the glow of the bonfires on the terrace
    o.append('<ellipse cx="820" cy="790" rx="520" ry="120" fill="url(#glow)"/>')
    # the terrace and its ruins: the stair's long wall, the Gate's piers, the Apadana's columns
    o.append(path('M0 792L1600 800V1000H0z', 'url(#gnd)'))
    o.append(rect(150, 770, 1100, 30, '#0f1824'))
    o.append(rect(150, 770, 1100, 2.5, '#6b4f33', opacity='.7'))
    for k in range(40):
        o.append(rect(170 + k * 27, 778, 14, 3, '#0a1119'))
    ruins = []
    # the Gate of All Nations: two massive piers with the doorway between
    for x in (330, 420):
        ruins.append(rect(x, 600, 46, 170, '#0b131d'))
        ruins.append(rect(x, 600, 46, 3, '#7a5a3a', opacity='.5'))
        ruins.append(rect(x + 40, 604, 6, 166, '#5a4430', opacity='.35'))
    # columns, standing and broken, their capitals of addorsed beasts as a little T
    cols = [(560, 560), (610, 548), (660, 590), (710, 556), (770, 680), (820, 562), (870, 600), (930, 572), (990, 700), (1040, 590), (1100, 640), (1150, 600)]
    for x, top in cols:
        whole = top < 650
        ruins.append(rect(x, top, 13, 770 - top, '#0b131d'))
        ruins.append(rect(x + 10, top + 4, 3, 766 - top, '#7a5a3a', opacity='.45'))
        if whole:
            ruins.append(path('M%s %sh31v7h-6v6h-19v-6h-6z' % (f(x - 9), f(top - 13)), '#0b131d'))
            ruins.append(rect(x - 9, top - 13, 31, 2, '#7a5a3a', opacity='.45'))
    o.append(''.join(ruins))
    # fires along the terrace, and their light on the stones
    for x in (250, 520, 760, 1000, 1210):
        o.append(circle(x, 768, 26, 'url(#torch)', opacity='.75'))
        o.append(path('M%s 772q4-14 0-22q-4 8-5 12q6-3 5 10z' % f(x), '#ffd27a'))
    # the foreground: a dark edge with a few stones
    o.append(path('M0 900Q400 880 800 905T1600 895V1000H0z', '#070c13'))
    save('desktop', W, H, ''.join(o), ''.join(D), aspect='xMidYMid slice')

# ---------------------------------------------------------------- Read Me: two fans of glissandi
def hero():
    # after Metastaseis: two fans of straight glissandi, one opening from a point as the other
    # closes to one, their envelope a curve though every line is straight
    W, H = 640, 200
    o = [rect(0, 0, W, H, P['paper'])]
    grid = ''.join('M%d 0v%d' % (x, H) for x in range(40, W, 40)) + ''.join('M0 %dh%d' % (y, W) for y in range(20, H, 20))
    o.append(path(grid, stroke='#c9bfa9', stroke_width='.5', opacity='.7'))
    a, b = [], []
    for k in range(26):
        t = k / 25
        a.append('M20 %sL620 %s' % (f(100 + (t - 0.5) * 12), f(12 + t * 176)))
        b.append('M20 %sL620 %s' % (f(14 + t * 172), f(100 + (0.5 - t) * 10)))
    o.append(path(''.join(b), stroke=P['blue'], stroke_width='1.1', opacity='.85'))
    o.append(path(''.join(a), stroke=P['accent'], stroke_width='1.1', opacity='.85'))
    save('hero', W, H, ''.join(o), title='Two fans of glissandi')

# ---------------------------------------------------------------- the About plates, 720 x 120
def plate(name, body, defs='', ground=None):
    W, H = 720, 120
    save(name, W, H, rect(0, 0, W, H, ground or P['cream']) + body, defs)

def bars(rows, x0, y0, step, col, h=5, r=2.5, unit=7):
    return ''.join(rect(x0 + a * unit, y0 + i * step, w * unit, h, col, r) for i, row in enumerate(rows) for a, w in row)

def plates():
    random.seed(57)
    U = 7   # one column
    # 0 history: a coding sheet: the label field, the statements, the margin at column 72
    rows = [[(0, 1), (6, 12)], [(6, 9), (17, 6)], [(1, 2), (6, 20)], [(6, 7), (14, 10)], [(6, 15)], [(1, 2), (6, 11), (18, 4)], [(6, 13)], [(6, 4)]]
    o = rect(24, 0, 5 * U, 120, '#e3d3b3') + path(''.join('M%s 0v120' % f(24 + k * U * 10) for k in range(10)), stroke='#d2c4a8', stroke_width='.6')
    o += bars([[(a, w) for a, w in r] for r in rows], 24, 12, 13, P['slate'], unit=U)
    o += rect(24 + 72 * U - 1, 0, 2, 120, P['accent'])
    o += rect(24 + 72 * U + 1, 0, 8 * U, 120, '#e8dcc6')
    plate('plate-0', o)
    # 1 the job: the program, its END, and the data after it
    o = bars([[(6, 14)], [(6, 9), (16, 5)], [(1, 2), (6, 17)], [(6, 3)]], 24, 12, 13, P['slate'], unit=U)
    o += rect(24 + 6 * U, 12 + 4 * 13, 3 * U, 5, P['accent'], 2.5)
    o += bars([[(0, 5), (5, 5), (10, 5)], [(0, 5), (5, 5)], [(0, 5), (5, 5), (10, 5), (15, 5)]], 24, 12 + 5 * 13 + 4, 13, P['blue_l'], unit=U)
    o += path('M%s 6v108' % f(24 + 40 * U), stroke='#cdbf9f', stroke_width='1', stroke_dasharray='3 4')
    plate('plate-1', o)
    # 2 using the workspace: windows over the desk, each with its two buttons
    o = rect(0, 0, 720, 120, P['blue'])
    for x, y, w, h in [(40, 22, 230, 120), (210, 46, 260, 120), (420, 14, 250, 120)]:
        o += rect(x + 3, y + 5, w, h, '#000', 8, opacity='.25')
        o += rect(x, y, w, h, P['paper'], 8) + rect(x, y, w, 18, '#e6dfd0', 8) + rect(x, y + 10, w, 8, '#e6dfd0')
        o += circle(x + 11, y + 9, 3.6, P['accent']) + circle(x + 23, y + 9, 3.6, P['ochre'])
        o += bars([[(0, 18)], [(0, 12), (13, 6)], [(0, 15)], [(0, 9)]], x + 14, y + 30, 12, '#b9b0a0', h=4, r=2, unit=w / 26)
    plate('plate-2', o)
    # 3 the language: loops within loops, as DO ranges nest
    o = ''
    for k, (c, w) in enumerate([(P['ochre'], 640), (P['sage'], 480), (P['blue_l'], 320), (P['accent'], 160)]):
        x, y, h = 360 - w / 2, 14 + k * 12, 92 - k * 24
        o += rect(x, y, w, h, 'none', h / 2, stroke=c, stroke_width='5')
        o += path('M%s %sh12l-6 9z' % (f(x + w - 6), f(y + h / 2 - 4)), c)
    plate('plate-3', o)
    # 4 the line printer: fan-fold paper, green bars and sprocket holes, folded
    o = ''
    for k in range(3):
        x = 30 + k * 230
        sk = 'translate(%d 0) skewY(%d)' % (x, -6 if k % 2 else 6)
        g = rect(0, 8, 210, 100, '#fffdf8', stroke='#cfc5b2') + ''.join(rect(16, 14 + j * 22, 178, 11, P['green']) for j in range(5))
        g += ''.join(circle(7, 14 + j * 9, 2.4, P['cream'], stroke='#b7ad99') + circle(203, 14 + j * 9, 2.4, P['cream'], stroke='#b7ad99') for j in range(11))
        g += bars([[(0, 9), (11, 6)], [(0, 13)], [(2, 7), (11, 9)], [(0, 11)], [(0, 6), (8, 8)], [(0, 12)], [(2, 9)]], 22, 17, 12.3, '#6f6a62', h=3, r=1.5, unit=8)
        o += '<g transform="%s">%s</g>' % (sk, g)
    plate('plate-4', o)
    # 5 Xenakis: a ruled surface, two families of straight lines
    a, b = [], []
    for k in range(31):
        t = k / 30
        a.append('M%s %sL%s %s' % (f(40 + t * 640), f(14), f(360 + (t - 0.5) * 120), f(106)))
        b.append('M%s 106L%s %s' % (f(40 + t * 640), f(360 + (0.5 - t) * 520), f(14)))
    o = path(''.join(b), stroke=P['blue_l'], stroke_width='1', opacity='.8') + path(''.join(a), stroke=P['accent'], stroke_width='1')
    plate('plate-5', o)
    # 6 the sieve: 48 points on a line, the members of 3@0 | 4@1 | 6@5 raised
    o = path('M24 92h672', stroke=P['soft'], stroke_width='1')
    for n in range(48):
        x = 30 + n * 14
        on = n % 3 == 0 or n % 4 == 1 or n % 6 == 5
        o += rect(x - 4, 92 - 64, 8, 64, P['ochre'], 2) if on else ''
        o += circle(x, 92, 3 if on else 1.6, P['ink'] if on else P['soft'])
        if n % 12 == 0: o += path('M%s 96v8' % f(x), stroke=P['soft'], stroke_width='1')
    plate('plate-6', o)
    # 7 the music programs: notes on a roll, coloured by loudness
    o = ''.join(path('M0 %sh720' % f(y), stroke='#d6c9ad', stroke_width='.8', stroke_dasharray='2 3') for y in (24, 60, 96))
    q, l = (143, 176, 200), (181, 70, 43)
    t = 0
    while t < 680:
        n = random.randint(0, 20); ln = random.choice((14, 14, 28, 42)); v = random.random()
        c = '#%02x%02x%02x' % tuple(int(q[i] + (l[i] - q[i]) * v) for i in range(3))
        o += rect(20 + t, 104 - n * 4.4, ln - 3, 7, c, 3)
        t += random.choice((7, 14, 14, 21))
    plate('plate-7', o)
    # 8 the Player: two reels and the sound leaving them
    o = ''
    for cx in (80, 210):
        o += circle(cx, 60, 46, P['teak']) + circle(cx, 60, 40, '#3b2a1d') + circle(cx, 60, 16, P['cream'])
        o += ''.join(circle(cx + 27 * math.cos(a), 60 + 27 * math.sin(a), 8, P['teak']) for a in (0.5, 2.6, 4.7))
        o += circle(cx, 60, 4, P['ink'])
    o += path('M80 106H210', stroke='#3b2a1d', stroke_width='3')
    d = 'M270 60' + ''.join('L%s %s' % (f(270 + k * 2), f(60 + 40 * math.sin(k * 0.21) * math.exp(-((k - 110) / 70) ** 2) * (0.6 + 0.4 * math.sin(k * 0.047)))) for k in range(1, 216))
    o += path(d, stroke=P['accent'], stroke_width='2.4', stroke_linejoin='round')
    o += path('M270 60H700', stroke='#c9bc9f', stroke_width='1')
    plate('plate-8', o)

# ---------------------------------------------------------------- Hugo Ball, 1916
def ball():
    # Ball reciting at the Cabaret Voltaire, after the photograph: the tall hat striped blue and
    # white, the high white collar, the cape with stiff wings, gold outside and scarlet within,
    # cardboard claws, legs in tubes, and the music stand with his poems on it
    W, H = 480, 400
    T = Type()
    D = lin('gold', [(0, '#e2b64e'), (1, '#c6962c')]) + lin('tube', [(0, '#3d5c80'), (0.5, '#6f8fb0'), (1, '#2b4560')], 1, 0)
    o = [rect(0, 0, W, H, P['paper']), rect(0, 352, W, 48, '#e6dccb'), path('M0 352h480', stroke='#bfb39d', stroke_width='1.5')]
    # the stand
    o.append(path('M86 350l22-34 22 34M108 316V176', stroke=P['ink'], stroke_width='3', stroke_linecap='round'))
    o.append(path('M70 152l76 8-6 42-74-8z', P['cream'], stroke=P['ink'], stroke_width='2', stroke_linejoin='round'))
    o.append(path(''.join('M%s %sl%s %s' % (f(78), f(164 + k * 7 + 0.0), 56, 6) for k in range(5)), stroke='#8f8574', stroke_width='1.4'))
    # the legs, in tubes banded at the knee
    for x in (238, 272):
        o.append(rect(x, 262, 26, 86, 'url(#tube)', 3))
        o.append(path('M%s 290h26M%s 318h26' % (x, x), stroke=P['paper'], stroke_width='2.5'))
        o.append(rect(x - 4, 344, 34, 9, P['ink'], 3))
    # the cape: two stiff wings, scarlet within, gold without, with claws at the ends
    o.append(path('M255 150L150 214L190 286L255 230z', P['accent']))
    o.append(path('M255 150L360 214L320 286L255 230z', P['accent']))
    o.append(path('M255 140L176 196L130 270L196 300L255 238L314 300L380 270L334 196z', 'url(#gold)', stroke='#8f6a1f', stroke_width='1.5', stroke_linejoin='round'))
    o.append(path('M255 152V238M200 200L176 280M310 200L334 280', stroke='#9d7623', stroke_width='1.4'))
    for sx in (-1, 1):
        cx = 255 + sx * 118
        o.append(path('M%s 268l%s 26M%s 270l%s 30M%s 266l%s 22' % (f(cx), f(sx * 6), f(cx - sx * 8), f(sx * 2), f(cx + sx * 8), f(sx * 12)), stroke=P['ink'], stroke_width='3', stroke_linecap='round'))
    # the high collar, the face
    o.append(path('M220 150Q255 118 290 150L282 108Q255 96 228 108z', P['paper'], stroke=P['ink'], stroke_width='2', stroke_linejoin='round'))
    o.append('<ellipse cx="255" cy="94" rx="15" ry="18" fill="#e9cfb4" stroke="%s" stroke-width="1.6"/>' % P['ink'])
    o.append(path('M249 92h3M259 92h3M251 103q4 2 8 0', stroke=P['ink'], stroke_width='1.6', stroke_linecap='round'))
    # the hat, a tall cylinder striped blue and white
    o.append(rect(236, 18, 38, 62, P['paper'], 2, stroke=P['ink'], stroke_width='2'))
    o.append(''.join(rect(238, 22 + k * 12, 34, 6, P['blue']) for k in range(5)))
    o.append(rect(230, 76, 50, 6, P['ink'], 2))
    o.append(T.text(456, 36, 'Zürich, 1916', 15, P['soft'], 'jost', 400, 'end', ls=0.6))
    save('ball', W, H, ''.join(o), D, T, title='Hugo Ball in his cardboard costume at the Cabaret Voltaire')

# ---------------------------------------------------------------- Tzara's hat
def hat():
    # the newspaper with a corner cut away, the scissors, and the hat with the words rising
    W, H = 480, 320
    T = Type()
    random.seed(1920)
    o = [rect(0, 0, W, H, P['paper']), rect(0, 268, W, 52, '#e6dccb'), path('M0 268h480', stroke='#bfb39d', stroke_width='1.5')]
    # the paper, its corner cut
    o.append(path('M22 196h86l18 18v54H22z', '#fbf8f0', stroke='#a59b88', stroke_width='1.4', stroke_linejoin='round'))
    o.append(path('M108 196v18h18', stroke='#a59b88', stroke_width='1.2'))
    o.append(''.join(rect(30, 204 + k * 8, [62, 70, 84, 80, 52, 88, 76, 44][k], 3, '#8f8574') for k in range(8)))
    # the hat, upturned: the brim, the crown below it, the band
    o.append('<ellipse cx="236" cy="200" rx="78" ry="14" fill="%s"/>' % P['ink'])
    o.append(path('M182 200L194 266h84l12-66z', P['ink']))
    o.append(path('M188 232h96', stroke=P['accent'], stroke_width='8'))
    o.append('<ellipse cx="236" cy="199" rx="56" ry="8" fill="#3a3733"/>')
    # the scissors, open
    o.append(path('M380 248L440 196M392 254L452 214', stroke='#8b8a86', stroke_width='5', stroke_linecap='round'))
    o.append(circle(372, 254, 10, 'none', stroke=P['accent'], stroke_width='4') + circle(388, 262, 10, 'none', stroke=P['accent'], stroke_width='4'))
    # the words, cut from the article, rising out of the hat
    words = ['brain', 'chance', 'music', 'electronic', 'applauded', 'hour', 'machine', 'audience']
    spots = [(236, 176, -3), (292, 150, 5), (198, 140, -6), (150, 112, 4), (300, 106, -4), (220, 86, 7), (160, 58, -5), (290, 42, 3)]
    for w, (x, y, a) in zip(words, spots):
        width = len(w) * 8.6 + 14
        o.append('<g transform="rotate(%d %s %s)">%s%s</g>' % (a, f(x), f(y), rect(x - width / 2, y - 12, width, 20, '#fffdf8', stroke='#a59b88', stroke_width='1'),
                                                          T.text(x, y + 3, w, 14, P['ink'], 'ibm-plex-mono', 400, 'middle')))
    save('hat', W, H, ''.join(o), '', T, title='An upturned hat with words rising out of it, a newspaper and scissors')

if __name__ == '__main__':
    desktop(); hero(); plates(); ball(); hat()
