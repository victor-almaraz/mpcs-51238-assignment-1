# The magazine's plates as SVG, printed as v18's press printed them: every colour area a
# halftone screen of round dots at its ink's angle (cyan 15, magenta 75, yellow 0, black
# 45, orange 60 degrees), each dot sized to the tone under it with about 12% dot gain, the
# dots swelling past 78% until they close up; each ink a fraction of a unit out of
# register, overlapping inks multiplying. Where the tone changes, every dot is placed and
# sized; dots of one size share a path, each a zero-length stroke with a round cap. Where
# the tone is flat, the screen is a pattern of that tone. Numerals and the cover's title
# are outlines of Playfair Display Italic; the op-art swatches are drawn as geometry and
# printed in flat screens.
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
GS, CMAP, UPM, HMTX = FONT.getGlyphSet(), FONT.getBestCmap(), FONT['head'].unitsPerEm, FONT['hmtx']

def f(v): return ('%.2f' % v).rstrip('0').rstrip('.') if abs(v) >= 0.005 else '0'
def f1(v): return ('%.1f' % v).rstrip('0').rstrip('.') if abs(v) >= 0.05 else '0'
def clamp(t): return 0.0 if t < 0 else 1.0 if t > 1 else t
def smooth(a, b, t): t = clamp((t - a) / (b - a)); return t * t * (3 - 2 * t)

def outline(text, size, x, y, track=0.0):
    pen = SVGPathPen(GS); s = size / UPM
    for ch in text:
        gn = CMAP[ord(ch)]
        GS[gn].draw(TransformPen(pen, (s, 0, 0, -s, x, y)))
        x += HMTX[gn][0] * s + track * size
    return pen.getCommands()

def gain(t):
    """the printed tone of a dot meant for tone t: about 12% gain in the middle tones"""
    return clamp(t + 0.48 * t * (1 - t) * 0.25)

def radius(t, cell):
    t = gain(t)
    if t <= 0.785: return cell * math.sqrt(t / math.pi)
    # swelling toward each other, but stopping just short of the diagonal, so pinholes of
    # paper always remain between four dots
    return cell * (0.5 + (t - 0.785) / 0.215 * 0.18)

# ---- a graded screen: every dot of one ink at its angle, sized by cov(x, y) -------------
def screen(ink, cell, cov, box, shift=(0, 0), clip=None, steps=40):
    x0, y0, x1, y1 = box
    a = math.radians(ANGLE[ink]); ca, sa = math.cos(a), math.sin(a)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    R = math.hypot(x1 - x0, y1 - y0) / 2 + cell
    n = int(R / cell) + 1
    levels = {}
    for i in range(-n, n + 1):
        for j in range(-n, n + 1):
            u, v = i * cell, j * cell
            x, y = cx + u * ca - v * sa, cy + u * sa + v * ca
            if x < x0 - cell or x > x1 + cell or y < y0 - cell or y > y1 + cell: continue
            t = cov(x, y)
            if t is None or t <= 0.03: continue
            r = radius(min(t, 1.0), cell)
            q = max(1, round(r / cell * steps))
            levels.setdefault(q, []).append('M%s %sh.01' % (f1(x), f1(y)))
    paths = ''.join('<path stroke-width="%s" d="%s"/>' % (f(2 * q * cell / steps), ''.join(d)) for q, d in sorted(levels.items()))
    return ('<g class="ov" fill="none" stroke="%s" stroke-linecap="round" transform="translate(%s %s)"%s>%s</g>'
            % (INK[ink], f(shift[0]), f(shift[1]), (' clip-path="url(#%s)"' % clip) if clip else '', paths))

# ---- a flat screen: one tone of one ink, as a pattern ---------------------------------
def flat(id_, ink, cell, t):
    """dots up to 78%; past that the ink closes round holes of paper"""
    t2 = min(gain(t), 0.97)
    if t2 <= 0.785:
        r = cell * math.sqrt(t2 / math.pi)
        inner = '<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (f(cell / 2), f(cell / 2), f(r), INK[ink])
    else:
        hole = cell * math.sqrt((1 - t2) / math.pi) * 0.9
        inner = ('<rect width="%s" height="%s" fill="%s"/>' % (f(cell), f(cell), INK[ink]) +
                 ('<circle cx="0" cy="0" r="%s" fill="%s"/>' % (f(hole), PAPER) if hole > 0.05 else ''))
    return ('<pattern id="%s" width="%s" height="%s" patternUnits="userSpaceOnUse" patternTransform="rotate(%d)">%s</pattern>'
            % (id_, f(cell), f(cell), ANGLE[ink], inner))

# ---- screens for the page's blocks of colour: seamless tiles. Each angle is taken as a
# whole-number slope (q, p) so the rotated lattice repeats on a square of side cell times
# the root of p² + q²: 15° ≈ (4, 1), 75° ≈ (1, 4), 0°, 45° (1, 1), 60° ≈ (4, 7).
SLOPE = dict(c=(4, 1), m=(1, 4), y=(1, 0), k=(1, 1), o=(4, 7))
def tile(ink, tone, cell=4.4):
    q, p = SLOPE[ink]
    n2 = p * p + q * q
    s_ = cell / math.sqrt(n2)
    T = s_ * n2
    v1 = (q * s_, p * s_); v2 = (-p * s_, q * s_)
    t2 = gain(tone)
    closed = t2 > 0.785
    r = cell * math.sqrt(t2 / math.pi) if not closed else cell * math.sqrt((1 - t2) / math.pi) * 0.9
    off = 0.5 if closed else 0.0
    pts = []
    N = int(math.sqrt(n2)) + 3
    for i in range(-N * 3, N * 3):
        for j in range(-N * 3, N * 3):
            x = (i + off) * v1[0] + (j + off) * v2[0]; y = (i + off) * v1[1] + (j + off) * v2[1]
            if -r <= x <= T + r and -r <= y <= T + r: pts.append((x, y))
    dots = ''.join('<circle cx="%s" cy="%s" r="%s"/>' % (f(x), f(y), f(r)) for x, y in pts)
    if closed:
        body = '<rect width="%s" height="%s" fill="%s"/><g fill="%s">%s</g>' % (f(T), f(T), INK[ink], PAPER, dots)
    else:
        body = '<g fill="%s">%s</g>' % (INK[ink], dots)
    name = 'screen-%s%d' % (ink, round(tone * 100))
    open(os.path.join(OUT, name + '.svg'), 'w').write('<svg xmlns="http://www.w3.org/2000/svg" width="%s" height="%s" viewBox="0 0 %s %s">%s</svg>' % (f(T), f(T), f(T), f(T), body))
    print(name, f(T))

def svg(w, h, defs, body, title):
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" preserveAspectRatio="xMidYMid slice">'
            '<title>%s</title><defs>%s</defs><style>.ov{mix-blend-mode:multiply}</style>'
            '<rect width="%d" height="%d" fill="%s"/>%s</svg>') % (w, h, title, defs, w, h, PAPER, body)

def save(name, s):
    open(os.path.join(OUT, name + '.svg'), 'w').write(s)
    print(name, len(s) // 1024, 'KB')

# ---- op-art swatches, as geometry: shapes printed in black (a closed-up screen) on the
# swatch's ground, the leaf's ink at 90% ---------------------------------------------
def op_shapes(kind, x, y, s):
    cx, cy, R = x + s / 2, y + s / 2, s / 2
    if kind == 1:
        d = ''
        w = s / 7 / math.sqrt(2) * 0.5
        for k in range(15):
            ax, bx = x + k * s / 7 - s, x + k * s / 7
            d += 'M%s %sL%s %sL%s %sL%s %sZ' % (f(ax - w), f(y + s), f(bx - w), f(y), f(bx + w), f(y), f(ax + w), f(y + s))
        return d, 'sq'
    if kind == 4:
        d = ''
        for (ox, oy) in ((-0.12, -0.05), (0.12, 0.05)):
            for k in range(1, 18):
                r1, r2 = k * s / 28, k * s / 28 + s / 64
                px, py = cx + ox * s, cy + oy * s
                d += ('M%s %sa%s %s 0 1 0 %s 0a%s %s 0 1 0 %s 0Z' % (f(px - r2), f(py), f(r2), f(r2), f(2 * r2), f(r2), f(r2), f(-2 * r2)) +
                      'M%s %sa%s %s 0 1 1 %s 0a%s %s 0 1 1 %s 0Z' % (f(px - r1), f(py), f(r1), f(r1), f(2 * r1), f(r1), f(r1), f(-2 * r1)))
        return d, 'sq'
    if kind == 5:
        n = 6; cells = []
        def P(u, v): return (x + (u + 0.08 * math.sin(v * 9)) * s, y + v * s)
        for i in range(-1, n + 1):
            for j in range(n):
                if (i + j) % 2: continue
                pts = [P(i / n, (j + k / 8) / n) for k in range(9)] + [P((i + 1) / n, (j + 1 - k / 8) / n) for k in range(9)]
                cells.append('M' + 'L'.join('%s %s' % (f(a), f(b)) for a, b in pts) + 'Z')
        return ''.join(cells), 'sq'
    if kind == 6:
        d = ''
        for k in range(0, 16, 2):
            a0, a1 = k * math.pi / 8, (k + 1) * math.pi / 8
            d += 'M%s %sL%s %sA%s %s 0 0 1 %s %sZ' % (f(cx), f(cy), f(cx + R * math.cos(a0)), f(cy + R * math.sin(a0)), f(R), f(R), f(cx + R * math.cos(a1)), f(cy + R * math.sin(a1)))
        return d, 'disc'
    if kind == 7:
        d = ''
        for k in range(7, 0, -2):
            o, i_ = s * k / 14, s * (k - 1) / 14
            d += 'M%s %sh%sv%sh%sZ' % (f(cx - o), f(cy - o), f(2 * o), f(2 * o), f(-2 * o))
            if i_ > 0: d += 'M%s %sv%sh%sv%sZ' % (f(cx - i_), f(cy - i_), f(2 * i_), f(2 * i_), f(-2 * i_))
        return d, 'sq'
    if kind == 8:
        d = ''
        turns, gap = 4.2, R / 4.2
        w = gap * 0.12     # each arm a quarter of the gap, so ink and ground share it
        for arm in (0, math.pi):
            outer, inner = [], []
            for k in range(0, 300):
                t = k / 299 * turns * 2 * math.pi
                r = gap * t / (2 * math.pi) * 1.05
                ang = t + arm
                outer.append('%s %s' % (f(cx + (r + w) * math.cos(ang)), f(cy + (r + w) * math.sin(ang))))
                inner.append('%s %s' % (f(cx + max(0, r - w) * math.cos(ang)), f(cy + max(0, r - w) * math.sin(ang))))
            d += 'M' + 'L'.join(outer) + 'L' + 'L'.join(reversed(inner)) + 'Z'
        return d, 'disc'

def swatch(kind, ink, x, y, s, n):
    d, ground = op_shapes(kind, x, y, s)
    cid = 'sw%d' % n
    cl = ('<circle cx="%s" cy="%s" r="%s"/>' % (f(x + s / 2), f(y + s / 2), f(s / 2))) if ground == 'disc' else ('<rect x="%s" y="%s" width="%s" height="%s"/>' % (f(x), f(y), f(s), f(s)))
    defs = '<clipPath id="%s">%s</clipPath>' % (cid, cl) + flat('g%d' % n, ink, 2.6, 0.72) + flat('k%d' % n, 'k', 2.2, 0.95)
    body = ('<g clip-path="url(#%s)">' % cid +
            '<g class="ov" transform="translate(0.5 -0.3)">%s</g>' % cl.replace('/>', ' fill="url(#g%d)"/>' % n) +
            '<path class="ov" fill="url(#k%d)" fill-rule="evenodd" transform="translate(-0.4 0.5)" d="%s"/></g>' % (n, d))
    return defs, body

# ---- a block: the leaf's ink, its tone falling off away from the numeral; the numeral
# knocked out to paper over its screened black shadow; the swatch printed beside it
def shot(name, ink, kind, numeral, W, H, strip=False):
    cell = 7
    if strip:
        s = H * 0.8; ox, oy = W - s - H * 0.1, H * 0.1
        tone = lambda x, y: 0.96 - 0.45 * smooth(0.35, 1, x / W)
    else:
        s = min(W * 0.5, H * 0.55); ox, oy = W - s - W * 0.08, H - s - min(H * 0.07, W * 0.08)
        tone = lambda x, y: 0.96 - 0.4 * smooth(0.25, 0.95, y / H)
    if not numeral and strip: ox = W - s - H * 0.12
    # the block's screen stops at the swatch's own outline: a square, or a disc
    round_ = op_shapes(kind, ox, oy, s)[1] == 'disc'
    if round_: inop = lambda x, y: math.hypot(x - ox - s / 2, y - oy - s / 2) <= s / 2 + 1
    else: inop = lambda x, y: ox - 1 <= x <= ox + s + 1 and oy - 1 <= y <= oy + s + 1
    defs = flat('ks', 'k', 4, 0.6)
    body = [screen(ink, cell, lambda x, y: None if inop(x, y) else tone(x, y), (0, 0, W, H), (0.5, -0.3))]
    sd, sb = swatch(kind, ink, ox, oy, s, 1)
    defs += sd; body.append(sb)
    if numeral:
        size = H * 1.15 if strip else H * 0.86
        d = outline(numeral, size, -size * 0.04, size * 0.78, -0.02)
        sx, sy = size * 0.035, size * 0.025
        body.append('<path class="ov" d="%s" fill="url(#ks)" transform="translate(%s %s)"/>' % (d, f(sx), f(sy)))
        body.append('<path d="%s" fill="%s"/>' % (d, PAPER))
    save(name, svg(W, H, defs, ''.join(body), name))

# ---- the wash: yellow and cyan screens across a strip, meeting in green, over a black
# rule whose top edge breaks into dots
def wash():
    W, H, rule = 600, 170, 18
    body = [screen('y', 7, lambda x, y: None if y > H - rule else 0.95 * (1 - smooth(0.15, 0.75, x / W)), (0, 0, W, H - rule), (0.5, 0.2)),
            screen('c', 7, lambda x, y: None if y > H - rule else 0.95 * smooth(0.3, 0.95, x / W) * (0.75 + 0.25 * (y / H)), (0, 0, W, H - rule), (-0.4, 0.5)),
            '<rect y="%d" width="%d" height="%d" fill="url(#kr)"/>' % (H - rule + 4, W, rule - 4),
            screen('k', 5, lambda x, y: smooth(H - rule - 8, H - rule + 6, y), (0, H - rule - 10, W, H - rule + 6), (0.2, -0.3))]
    save('wash', svg(W, H, flat('kr', 'k', 5, 0.96), ''.join(body), 'wash'))

# ---- the cover: the field (orange falling off toward the foot, a black disc cropped by
# the right edge with a screened edge, a magenta target of rings on a finer screen); with
# band=True also the black title band, its foot breaking into dots, and the title
def cover(name, W, H, band=0, title=False):
    cell = 6.5
    top = band; fh = H - top; foot = min(42, band * 0.14) if band else 0
    disc = (W * 0.9, top + fh * 0.3, min(W * 0.42, fh * 0.42))
    tgt = (W * 0.25, top + fh * 0.32, min(W * 0.18, fh * 0.22))
    ring = max(3, tgt[2] / 6)
    def orange(x, y):
        if y < top - foot: return None
        if math.hypot(x - tgt[0], y - tgt[1]) < tgt[2]: return None
        return 1 - 0.5 * smooth(0.25, 1.15, (x / W) * 0.3 + ((y - top) / fh) * 0.9)
    body = [screen('o', cell * 1.1, orange, (0, top - foot, W, H), (0.6, 0.4))]
    # the target: rings of magenta, solid, on a fine screen of their own
    tx, ty, tr = tgt
    d = ''
    for k in range(6):
        r1, r2 = k * ring + ring / 2, k * ring + ring
        if r1 >= tr: break
        r2 = min(r2, tr)
        d += ('M%s %sa%s %s 0 1 0 %s 0a%s %s 0 1 0 %s 0Z' % (f(tx - r2), f(ty), f(r2), f(r2), f(2 * r2), f(r2), f(r2), f(-2 * r2)) +
              'M%s %sa%s %s 0 1 1 %s 0a%s %s 0 1 1 %s 0Z' % (f(tx - r1), f(ty), f(r1), f(r1), f(2 * r1), f(r1), f(r1), f(-2 * r1)))
    defs = flat('mt', 'm', 2.4, 0.97) + flat('kd', 'k', cell, 1.0)
    body.append('<path class="ov" fill="url(#mt)" fill-rule="evenodd" transform="translate(-0.7 0.3)" d="%s"/>' % d)
    # the disc: closed-up black inside, and its edge printed dot by dot
    dx, dy, dr = disc
    body.append('<circle class="ov" cx="%s" cy="%s" r="%s" fill="url(#kd)" transform="translate(0.2 -0.6)"/>' % (f(dx), f(dy), f(dr - cell * 4)))
    body.append(screen('k', cell, lambda x, y: (lambda dd: None if dd < dr - cell * 4 - 1 else 1 - smooth(dr - cell * 4, dr, dd))(math.hypot(x - dx, y - dy)),
                       (dx - dr, dy - dr, W, dy + dr), (0.2, -0.6)))
    if band:
        def ground(x, y): return 0.96 - 0.55 * smooth(band - foot, band, y) - 0.3 * smooth(W * 0.7, W, x) * smooth(band * 0.6, band, y)
        body.append('<rect width="%d" height="%s" fill="url(#kd)" class="ov"/>' % (W, f(band * 0.6)))
        body.append(screen('k', cell, lambda x, y: None if y < band * 0.6 - cell else ground(x, y), (0, band * 0.6 - cell, W, band), (0.3, -0.4)))
    if title:
        size = W * 0.205
        d = outline('MOIRÉ', size * 1.12, W * 0.035, band * 0.6, -0.02)
        defs += flat('tm', 'm', 3, 0.96) + flat('yb', 'y', 4, 0.96)
        body.append('<path d="%s" fill="%s" transform="translate(%s %s)"/>' % (d, PAPER, f(size * 0.035), f(size * 0.025)))
        body.append('<path class="ov" d="%s" fill="url(#tm)" transform="translate(%s %s)"/>' % (d, f(size * 0.035), f(size * 0.025)))
        body.append('<path d="%s" fill="%s"/>' % (d, PAPER))
        body.append('<rect class="ov" x="%s" y="%s" width="%s" height="%s" fill="url(#yb)"/>' % (f(W * 0.3), f(band * 0.72), f(W * 0.5), f(band * 0.1)))
        body.append('<rect x="%s" y="%s" width="%s" height="%s" fill="%s"/>' % (f(W * 0.48), f(H * 0.62), f(W * 0.46), f(H * 0.12), PAPER))
        body.append('<rect class="ov" x="%s" y="%s" width="%s" height="%s" fill="url(#yb)"/>' % (f(W * 0.58), f(H * 0.75), f(W * 0.36), f(H * 0.035)))
        body.append('<rect x="%s" y="%s" width="%s" height="%s" fill="%s"/>' % (f(W * 0.08), f(H * 0.83), f(W * 0.86), f(H * 0.09), PAPER))
    save(name, svg(W, H, defs, ''.join(body), name))

if __name__ == '__main__':
    shot('contents', 'm', 6, '', 600, 150, strip=True)
    shot('a1', 'c', 5, '01', 600, 460)
    shot('a2', 'o', 4, '02', 600, 430)
    shot('a3', 'y', 7, '03', 600, 430)
    shot('a4', 'm', 8, '04', 600, 460)
    shot('catalogue', 'c', 1, '13', 600, 150, strip=True)
    wash()
    cover('cover-field', 600, 450)
    cover('cover-thumb', 600, 800, band=340, title=True)
    for ink in 'cmyko': tile(ink, 0.96)
