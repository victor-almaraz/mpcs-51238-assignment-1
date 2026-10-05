# The magazine's plates as SVG files, in place of v18's canvas press (halftone.js): flat
# process inks that overprint (multiply), Ben-Day screens of fixed dots stepped in bands
# instead of per-dot tone, each ink a hair out of register, numerals and the cover title
# as outlines of Playfair Display Italic, and the op-art swatches as true geometry.
import os as _os; UTIL = _os.path.normpath(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..')); REPO = _os.path.dirname(UTIL)
import math, os
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

REPO = REPO
OUT = REPO + '/v21/assets/mag'
os.makedirs(OUT, exist_ok=True)
INK = dict(c='#00a6c8', m='#dc0078', y='#ffd400', k='#0d0d0d', o='#ff5a1f')
PAPER = '#fffaf0'
ANGLE = dict(c=15, m=75, y=0, k=45, o=60)
FONT = TTFont(REPO + '/fonts/playfair-display/playfair-display-latin-400-italic.woff2')
GS, CMAP, UPM = FONT.getGlyphSet(), FONT.getBestCmap(), FONT['head'].unitsPerEm
HMTX = FONT['hmtx']

def f(v): return ('%.2f' % v).rstrip('0').rstrip('.')

def outline(text, size, x, y, track=0.0):
    """the text as one path, baseline at y, in Playfair Display Italic"""
    pen = SVGPathPen(GS)
    s = size / UPM
    for ch in text:
        gn = CMAP[ord(ch)]
        GS[gn].draw(TransformPen(pen, (s, 0, 0, -s, x, y)))
        x += HMTX[gn][0] * s + track * size
    return pen.getCommands(), x

def width(text, size, track=0.0):
    return sum(HMTX[CMAP[ord(c)]][0] for c in text) * size / UPM + track * size * len(text)

def benday(id_, ink, cell, r):
    """a screen of fixed dots: cell apart, radius r, at the ink's angle"""
    return ('<pattern id="%s" width="%s" height="%s" patternUnits="userSpaceOnUse" patternTransform="rotate(%d)">'
            '<circle cx="%s" cy="%s" r="%s" fill="%s"/></pattern>') % (id_, f(cell), f(cell), ANGLE[ink], f(cell / 2), f(cell / 2), f(r), INK[ink])

def steps(ink, cell, n=5, lo=0.18, hi=0.48):
    """n screens of one ink, from light to heavy dots: a tone scale in steps"""
    return ''.join(benday('%s%d' % (ink, i), ink, cell, cell * (lo + (hi - lo) * i / (n - 1))) for i in range(n))

def svg(w, h, defs, body, title):
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" preserveAspectRatio="xMidYMid slice">'
            '<title>%s</title><defs>%s</defs><style>.ov{mix-blend-mode:multiply}</style>%s</svg>') % (w, h, title, defs, body)

def save(name, s):
    open(os.path.join(OUT, name + '.svg'), 'w').write(s)
    print(name, len(s) // 1024, 'KB')

# ---- op-art swatches, drawn in black inside a square (x, y, s) ------------------------
def op(kind, x, y, s):
    cx, cy, R = x + s / 2, y + s / 2, s / 2
    K = INK['k']
    out = []
    if kind == 1:      # diagonal stripes, in the square
        out.append('<clipPath id="op1"><rect x="%s" y="%s" width="%s" height="%s"/></clipPath>' % (f(x), f(y), f(s), f(s)))
        period = s / 7 / math.sqrt(2)      # across the stripes
        lines = ''.join('<line x1="%s" y1="%s" x2="%s" y2="%s"/>' % (f(x + k * s / 7 - s), f(y + s), f(x + k * s / 7), f(y)) for k in range(0, 15))
        out.append('<rect x="%s" y="%s" width="%s" height="%s" fill="%s"/>' % (f(x), f(y), f(s), f(s), PAPER))
        out.append('<g clip-path="url(#op1)" stroke="%s" stroke-width="%s">%s</g>' % (K, f(period * 0.5), lines))
    elif kind == 4:    # two sets of rings crossing in a moire
        for (ox, oy) in ((-0.12, -0.05), (0.12, 0.05)):
            rings = ''.join('<circle cx="%s" cy="%s" r="%s"/>' % (f(cx + ox * s), f(cy + oy * s), f(k * s / 28)) for k in range(1, 18))
            out.append('<g fill="none" stroke="%s" stroke-width="%s" clip-path="url(#op4)">%s</g>' % (K, f(s / 60), rings))
        out.insert(0, '<clipPath id="op4"><rect x="%s" y="%s" width="%s" height="%s"/></clipPath>' % (f(x), f(y), f(s), f(s)))
    elif kind == 5:    # a checker warped by a sine, cell by cell
        n = 6; cells = []
        def P(u, v): return (x + (u + 0.08 * math.sin(v * 9)) * s, y + v * s)
        for i in range(-1, n + 1):
            for j in range(n):
                if (i + j) % 2: continue
                pts = []
                for k in range(9): pts.append(P((i + 0) / n, (j + k / 8) / n))
                for k in range(9): pts.append(P((i + 1) / n, (j + 1 - k / 8) / n))
                cells.append('M' + ' L'.join('%s,%s' % (f(a), f(b)) for a, b in pts) + 'Z')
        out.append('<clipPath id="op5"><rect x="%s" y="%s" width="%s" height="%s"/></clipPath>' % (f(x), f(y), f(s), f(s)))
        out.append('<rect x="%s" y="%s" width="%s" height="%s" fill="%s"/>' % (f(x), f(y), f(s), f(s), PAPER))
        out.append('<path clip-path="url(#op5)" fill="%s" d="%s"/>' % (K, ' '.join(cells)))
    elif kind == 6:    # rays from the centre, in a disc
        wedges = []
        for k in range(16):
            if k % 2: continue
            a0, a1 = k * math.pi / 8, (k + 1) * math.pi / 8
            wedges.append('M%s,%s L%s,%s A%s,%s 0 0 1 %s,%s Z' % (f(cx), f(cy), f(cx + R * math.cos(a0)), f(cy + R * math.sin(a0)), f(R), f(R), f(cx + R * math.cos(a1)), f(cy + R * math.sin(a1))))
        out.append('<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (f(cx), f(cy), f(R), PAPER))
        out.append('<path fill="%s" d="%s"/>' % (K, ' '.join(wedges)))
    elif kind == 7:    # nested squares
        for k in range(7, 0, -1):
            d = s * k / 14
            out.append('<rect x="%s" y="%s" width="%s" height="%s" fill="%s"/>' % (f(cx - d), f(cy - d), f(2 * d), f(2 * d), K if k % 2 else PAPER))
    elif kind == 8:    # an Archimedean spiral of two arms, as thick strokes, in a disc
        out.append('<clipPath id="op8"><circle cx="%s" cy="%s" r="%s"/></clipPath>' % (f(cx), f(cy), f(R)))
        out.append('<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (f(cx), f(cy), f(R), PAPER))
        turns, gap = 4.2, R / 4.2          # one arm's turns; the two arms share the gap
        for arm in (0, math.pi):
            pts = []
            for k in range(0, 400):
                t = k / 399 * turns * 2 * math.pi
                r = gap * t / (2 * math.pi) * 1.05
                pts.append('%s,%s' % (f(cx + r * math.cos(t + arm)), f(cy + r * math.sin(t + arm))))
            out.append('<path clip-path="url(#op8)" fill="none" stroke="%s" stroke-width="%s" d="M%s"/>' % (K, f(gap * 0.26), ' L'.join(pts)))
        out.append('<circle cx="%s" cy="%s" r="%s" fill="none" stroke="%s" stroke-width="%s"/>' % (f(cx), f(cy), f(R), K, f(s / 70)))
    return ''.join(out)

# ---- a block: the leaf's ink, its tone stepped down the block in Ben-Day bands, a numeral
# knocked out to paper (bleeding off the top and left) over its screened black shadow, and
# an op-art swatch overprinted in black
def shot(name, ink, kind, numeral, W, H, strip=False):
    defs = steps(ink, 7) + benday('ks', 'k', 5, 1.55)
    b = ['<rect width="%d" height="%d" fill="%s"/>' % (W, H, PAPER)]
    # the solid, then four bands of lighter screens toward the far edge
    bands = 5
    if strip:
        x0 = W * 0.42
        b.append('<rect width="%s" height="%d" fill="%s"/>' % (f(x0), H, INK[ink]))
        for i in range(bands):
            bx = x0 + (W - x0) * i / bands
            b.append('<rect x="%s" width="%s" height="%d" fill="url(#%s%d)"/>' % (f(bx), f((W - x0) / bands + 0.5), H, ink, bands - 1 - i))
    else:
        y0 = H * 0.5
        b.append('<rect width="%d" height="%s" fill="%s"/>' % (W, f(y0), INK[ink]))
        for i in range(bands):
            by = y0 + (H - y0) * i / bands
            b.append('<rect y="%s" width="%d" height="%s" fill="url(#%s%d)"/>' % (f(by), W, f((H - y0) / bands + 0.5), ink, bands - 1 - i))
    # the swatch
    s = H * 0.78 if strip else min(W * 0.5, H * 0.56)
    ox, oy = (W - s - H * 0.11, (H - s) / 2) if strip else (W - s - W * 0.07, H - s - H * 0.07)
    if not numeral and strip:
        ox = W - s - H * 0.11
    b.append('<g class="ov" transform="translate(-1.2 0.8)">%s</g>' % op(kind, ox, oy, s))
    if numeral:
        size = (H * 1.18) if strip else H * 0.86
        nx, ny = -size * 0.04, size * 0.78
        d, _ = outline(numeral, size, nx, ny, -0.02)
        # the shadow, a black screen out of register, then the numeral knocked out to paper
        b.append('<path class="ov" d="%s" fill="url(#ks)" transform="translate(%s %s)"/>' % (d, f(size * 0.035), f(size * 0.025)))
        b.append('<path d="%s" fill="%s"/>' % (d, PAPER))
        b.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.2" transform="translate(%s %s)" opacity="0.5"/>' % (d, INK[ink], f(-0.8), f(0.6)))
    save(name, svg(W, H, defs, ''.join(b), name))

# ---- the wash: yellow and cyan overprinting across a strip, meeting in green, over a
# black rule whose top edge breaks into dots
def wash():
    W, H = 600, 170
    rule = 18
    defs = (steps('y', 8) + steps('c', 8) + benday('kr', 'k', 6, 2.2))
    b = ['<rect width="%d" height="%d" fill="%s"/>' % (W, H, PAPER)]
    # each ink is one row of abutting bands (no overlaps, which would multiply into seams)
    n, bw = 8, W / 8
    ys = [INK['y'], INK['y'], 'url(#y4)', 'url(#y3)', 'url(#y2)', 'url(#y1)', 'url(#y0)', None]
    cs = [None, None, 'url(#c0)', 'url(#c1)', 'url(#c2)', 'url(#c3)', INK['c'], INK['c']]
    for ink, row, sh in (('y', ys, '0.8 0.4'), ('c', cs, '-0.6 0.6')):
        parts = []
        i = 0
        while i < n:
            if row[i] is None: i += 1; continue
            j = i
            while j + 1 < n and row[j + 1] == row[i]: j += 1
            parts.append('<rect x="%s" width="%s" height="%d" fill="%s"/>' % (f(i * bw), f((j - i + 1) * bw), H - rule, row[i]))
            i = j + 1
        b.append('<g class="ov" transform="translate(%s)">%s</g>' % (sh, ''.join(parts)))
    b.append('<rect y="%d" width="%d" height="%d" fill="%s"/>' % (H - rule, W, rule, INK['k']))
    b.append('<rect y="%d" width="%d" height="8" fill="url(#kr)"/>' % (H - rule - 8, W))
    save('wash', svg(W, H, defs, ''.join(b), 'wash'))

# ---- the cover's field: orange stepping lighter toward the foot, a black disc cropped by
# the right edge, a magenta target of rings at the left; the title band is the page's own
# black, above it
def cover_field(W=600, H=450, name='cover-field', with_band=False, band=0):
    defs = steps('o', 8) + steps('k', 6, 4)
    b = ['<rect width="%d" height="%d" fill="%s"/>' % (W, H, PAPER)]
    top = band
    fh = H - top
    bands = 6
    b.append('<rect y="%s" width="%d" height="%s" fill="%s"/>' % (f(top), W, f(fh * 0.4), INK['o']))
    for i in range(bands - 1):
        y = top + fh * 0.4 + fh * 0.6 * i / (bands - 1)
        b.append('<rect y="%s" width="%d" height="%s" fill="url(#o%d)"/>' % (f(y), W, f(fh * 0.6 / (bands - 1) + 0.5), 4 - i))
    tx, ty, tr = W * 0.25, top + fh * 0.33, min(W * 0.18, fh * 0.22)
    b.append('<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (f(tx), f(ty), f(tr + 2), PAPER))
    rings = ''.join('<circle cx="%s" cy="%s" r="%s"/>' % (f(tx), f(ty), f(tr * (k + 0.5) / 6)) for k in range(6))
    b.append('<g class="ov" fill="none" stroke="%s" stroke-width="%s" transform="translate(-1 0.6)">%s</g>' % (INK['m'], f(tr / 12), rings))
    dx, dy, dr = W * 0.92, top + fh * 0.3, min(W * 0.42, fh * 0.42)
    b.append('<circle class="ov" cx="%s" cy="%s" r="%s" fill="%s" transform="translate(0.5 -0.8)"/>' % (f(dx), f(dy), f(dr), INK['k']))
    # the disc's edge breaks into the screen: a ring of heavy black dots round it
    b.append('<circle class="ov" cx="%s" cy="%s" r="%s" fill="none" stroke="url(#k3)" stroke-width="10"/>' % (f(dx), f(dy), f(dr + 5)))
    if with_band:
        b.append('<rect width="%d" height="%s" fill="%s"/>' % (W, f(band), INK['k']))
        d, _ = outline('FORTRAN', W * 0.205, W * 0.035, band * 0.62, -0.035)
        b.append('<path d="%s" fill="%s" transform="translate(%s %s)"/>' % (d, INK['m'], f(W * 0.007), f(W * 0.005)))
        b.append('<path d="%s" fill="%s"/>' % (d, PAPER))
        b.append('<rect x="%s" y="%s" width="%s" height="%s" fill="%s"/>' % (f(W * 0.3), f(band * 0.76), f(W * 0.5), f(band * 0.1), INK['y']))
        # cover lines, as blocks of paper and yellow
        b.append('<rect x="%s" y="%s" width="%s" height="%s" fill="%s"/>' % (f(W * 0.48), f(H * 0.62), f(W * 0.46), f(H * 0.12), PAPER))
        b.append('<rect x="%s" y="%s" width="%s" height="%s" fill="%s"/>' % (f(W * 0.58), f(H * 0.75), f(W * 0.36), f(H * 0.035), INK['y']))
        b.append('<rect x="%s" y="%s" width="%s" height="%s" fill="%s"/>' % (f(W * 0.08), f(H * 0.83), f(W * 0.86), f(H * 0.09), PAPER))
    save(name, svg(W, H, defs, ''.join(b), name))

if __name__ == '__main__':
    shot('contents', 'm', 6, '', 600, 150, strip=True)
    shot('a1', 'c', 5, '01', 600, 460)
    shot('a2', 'o', 4, '02', 600, 430)
    shot('a3', 'y', 7, '03', 600, 430)
    shot('a4', 'm', 8, '04', 600, 460)
    shot('catalogue', 'c', 1, '13', 600, 150, strip=True)
    wash()
    cover_field()
    cover_field(600, 800, 'cover-thumb', True, 340)
