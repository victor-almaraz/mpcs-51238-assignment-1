# What makes v21's workroom lived in: a framed screen print of a sieve where the title
# was, a molded-plywood chair at the desk, a flat-woven rug on the floor, a trailing
# pothos in a glazed pot and a mug on the desk. Units are tenths of an em; SCALE px a unit.
import math, random
from mcm import *
from render import render, REPO
OUT = REPO + '/v21/assets'
SCALE = 5
PLY = '#c49a6c'
PLYD = '#8f6a45'
LEAF = '#5f7a4f'
LEAFD = '#465d3b'
LEAFL = '#86a06a'

def common(seed):
    return print_filter('pr', 1.3, 0.22, seed) + grain_filter('gr', 1.1, 0.05, seed + 1) + blur_filter('soft', 1.0)

# ---- the print: a sieve after Xenakis, as rows of dots across the integers 0 to 23, one
# residue class to a row, each in its own colour, and their union in ink at the foot;
# framed in oak over a wide mat
def sieve_print():
    W, H = 214, 168
    o = []
    o.append(rect(3, 4, W - 3, H - 3, '#28180c', opacity=0.2, filter='url(#soft)'))
    fr = 7
    o.append(rect(0, 0, W - 3, H - 4, P['oak']))
    fw, fh = W - 3, H - 4
    for pts, c in ((((0, 0), (fw, 0), (fw - fr, fr), (fr, fr)), light(P['oak'], 0.18)), (((0, 0), (fr, fr), (fr, fh - fr), (0, fh)), light(P['oak'], 0.08)),
                   (((fw, 0), (fw, fh), (fw - fr, fh - fr), (fw - fr, fr)), dark(P['oak'], 0.12)), (((0, fh), (fr, fh - fr), (fw - fr, fh - fr), (fw, fh)), dark(P['oak'], 0.2))):
        o.append(poly(pts, c))
    for k in range(10):
        o.append(line(fr * 0.2 + k * 0.6, fr * 0.2 + k * 0.6, fw - fr * 0.2 - k * 0.6, fr * 0.2 + k * 0.6, P['oakd'], 0.1, opacity=0.3))
    o.append(rect(0, 0, W - 3, 1.4, P['oakl'])); o.append(rect(0, 0, 1.4, H - 4, P['oakl']))
    o.append(rect(W - 4.4, 0, 1.4, H - 4, P['oakd'])); o.append(rect(0, H - 5.4, W - 3, 1.4, P['oakd']))
    mx, my, mw, mh = fr, fr, W - 3 - 2 * fr, H - 4 - 2 * fr
    o.append(rect(mx, my, mw, mh, P['paper']))
    o.append(rect(mx, my, mw, 1.2, '#000', opacity=0.08)); o.append(rect(mx, my, 1.2, mh, '#000', opacity=0.06))
    # the image, on a cream sheet in the mat's window
    ix, iy, iw, ih = mx + 18, my + 16, mw - 36, mh - 40
    art = [rect(ix, iy, iw, ih, '#efe6d2')]
    rows = [(2, 0, P['ochre']), (3, 1, P['accent']), (4, 2, P['slate']), (5, 0, P['sage']), (7, 3, P['teak'])]
    n = 24
    cw = iw / (n + 1)
    rh = ih / (len(rows) + 2)
    for r, (m, res, col) in enumerate(rows):
        y = iy + rh * (r + 1)
        art.append(line(ix + cw * 0.5, y, ix + iw - cw * 0.5, y, P['ink'], 0.12, opacity=0.35))
        for k in range(n):
            x = ix + cw * (k + 1)
            if k % m == res: art.append(circle(x, y, cw * 0.36, col))
            else: art.append(circle(x, y, 0.45, P['ink'], opacity=0.5))
    # the union, the sieve itself, in ink on a rule of its own
    y = iy + rh * (len(rows) + 1)
    art.append(rect(ix + cw * 0.5, y - 0.15, iw - cw, 0.3, P['ink']))
    for k in range(n):
        x = ix + cw * (k + 1)
        if any(k % m == res for m, res, _ in rows): art.append(rect(x - cw * 0.3, y - cw * 0.3, cw * 0.6, cw * 0.6, P['ink']))
    # a large disc printed over the left, in overprinting terracotta, out of register
    art.append(circle(ix + iw * 0.2, iy + ih * 0.42, ih * 0.36, P['accent'], opacity=0.16))
    o.append(g(art, filter='url(#pr)'))
    # the glass over it all: a faint diagonal sheen; the mat's bevel catching the light
    o.append(rect(mx + 15.4, my + 13.4, mw - 30.8, mh - 34.8, 'none', stroke='#ffffff', stroke_width=1.0, opacity=0.8))
    o.append(rect(mx + 16, my + 14, mw - 32, mh - 36, 'none', stroke='#000', stroke_width=0.4, opacity=0.18))
    o.append(poly([(mx + mw * 0.55, my), (mx + mw * 0.72, my), (mx + mw * 0.36, my + mh), (mx + mw * 0.19, my + mh)], '#ffffff', opacity=0.07))
    o.append(poly([(mx + mw * 0.75, my), (mx + mw * 0.78, my), (mx + mw * 0.42, my + mh), (mx + mw * 0.39, my + mh)], '#ffffff', opacity=0.08))
    o.append(text(ix, iy + ih + 9, 'Crible', 3.2, P['soft'], 'Work Sans', 400, 0.06))
    o.append(text(ix + iw, iy + ih + 9, '7/30', 3.0, P['soft'], 'Work Sans', 400, 0.06, 'end'))
    return render('print-sieve', g(o, filter='url(#gr)'), W, H, SCALE, OUT, defs=print_filter('pr', 1.3, 0.22, 101) + grain_filter('gr', 1.1, 0.025, 102) + blur_filter('soft', 1.0))

# ---- a molded-plywood side chair: its back and seat two curved shells, its legs splayed;
# the plywood's laminations show as stripes along the edges
def chair():
    W, H = 64, 144
    o = []
    rnd = random.Random(3)
    def ply(d, c=PLY):
        return [path(d, c), path(d, 'none', stroke=PLYD, stroke_width=0.35, transform='translate(-0.3 0.25)', opacity=0.8)]
    # back legs, behind
    for x0, x1 in ((16, 12), (48, 52)):
        o += ply('M%s,78 L%s,%s L%s,%s L%s,78 Z' % (f(x0 - 1.6), f(x1 - 1.4), f(H), f(x1 + 1.4), f(H), f(x0 + 1.6)), dark(PLY, 0.18))
    # the spine that carries the back
    o += ply('M30,40 L34,40 L35,80 L29,80 Z', dark(PLY, 0.1))
    # the back: a wide shell, its top edge lit
    back = 'M6,12 C6,6 10,4 32,4 C54,4 58,6 58,12 L58,30 C58,36 54,38 32,38 C10,38 6,36 6,30 Z'
    o += ply(back)
    o.append(path('M9,8 C14,6 50,6 55,8', 'none', stroke=light(PLY, 0.35), stroke_width=1.0))
    o.append(path('M7,30 C10,35 54,35 57,30', 'none', stroke=PLYD, stroke_width=0.5, opacity=0.6))
    # the seat, seen at its front edge: a shallow dish
    seat = 'M2,76 C2,72 10,70 32,70 C54,70 62,72 62,76 L62,80 C62,84 54,85 32,85 C10,85 2,84 2,80 Z'
    o += ply(seat)
    for k in range(4):
        o.append(path('M4,%s C12,%s 52,%s 60,%s' % (f(79 + k * 1.1), f(83 + k * 1.1 - 2), f(83 + k * 1.1 - 2), f(79 + k * 1.1)), 'none', stroke=light(PLY, 0.25) if k % 2 else PLYD, stroke_width=0.3, opacity=0.6))
    # front legs, splayed
    for x0, x1 in ((20, 10), (44, 54)):
        o += ply('M%s,84 L%s,%s L%s,%s L%s,84 Z' % (f(x0 - 1.8), f(x1 - 1.6), f(H), f(x1 + 1.6), f(H), f(x0 + 1.8)))
        o.append(rect(x1 - 1.9, H - 1.4, 3.8, 1.4, P['ink']))
    # the stretcher between them
    o.append(path('M14,118 L50,118 L50,120 L14,120 Z', dark(PLY, 0.14)))
    # drawn narrow, then widened to the chair's proportions (it is about two thirds as wide as tall)
    return render('chair', g(g(g(o, transform='scale(1.5 1)'), filter='url(#gr)'), filter='url(#pr)'), W * 1.5, H, SCALE, OUT, defs=common(111))

# ---- a flat-woven rug, its near edge, in elevation a band on the floor with fringes
def rug():
    W, H = 560, 20
    o = []
    band = [poly([(10, 4), (W - 10, 4), (W - 4, H - 4), (4, H - 4)], P['accent'])]
    cols = [P['cream'], P['ochre'], P['slate'], P['cream']]
    # a row of lozenges between two stripes
    band.append(rect(0, 6.2, W, 1.2, P['cream'])); band.append(rect(0, H - 7.2, W, 1.2, P['cream']))
    k = 0
    for x in range(14, W - 14, 16):
        c = cols[k % len(cols)]; k += 1
        band.append(poly([(x, 10), (x + 6, 8.1), (x + 12, 10), (x + 6, 11.9)], c))
        band.append(rect(x + 13.2, 9.4, 1.6, 1.2, P['ink'], opacity=0.6))
    o.append(g(band, clip_path='url(#rugc)'))
    for x in (4, W - 4):
        for j in range(9):
            y = 5 + j * 1.3
            d = -1 if x < W / 2 else 1
            o.append(line(x + d * (6 - j * 0.6 if j < 4 else 1.8 + j * 0.2), y, x + d * (8.5 - j * 0.4), y + 0.6, P['cream'], 0.35))
    defs = common(121) + clip('rugc', poly([(10, 4), (W - 10, 4), (W - 4, H - 4), (4, H - 4)], '#000'))
    return render('rug', g(g(o, filter='url(#gr)'), filter='url(#pr)'), W, H, SCALE, OUT, defs=defs)

# ---- a pothos in a glazed stoneware pot, its vines trailing over the desk's edge. The pot
# stands at y = 80 (the desk top); the vines hang below it, over the desk's front
def pothos():
    W, H = 100, 116
    DESK = 82
    o = []
    rnd = random.Random(8)
    def leaf(x, y, s, ang, c):
        d = 'M0,0 C%s,%s %s,%s 0,%s C%s,%s %s,%s 0,0 Z' % (f(s * 0.7), f(-s * 0.2), f(s * 0.6), f(s * 0.9), f(s * 1.2), f(-s * 0.6), f(s * 0.9), f(-s * 0.7), f(-s * 0.2))
        return g([path(d, c), path('M0,%s L0,%s' % (f(s * 0.1), f(s * 1.05)), 'none', stroke=dark(c, 0.2), stroke_width=0.25)],
                 transform='translate(%s %s) rotate(%s)' % (f(x), f(y), f(ang)))
    cx = 50
    # vines: from the pot's rim, some up and out, two down over the edge
    vines = [((cx - 6, DESK - 22), [(-14, -20), (-20, -38), (-16, -52)]), ((cx + 4, DESK - 22), [(10, -22), (20, -36), (24, -46)]),
             ((cx + 10, DESK - 21), [(22, -6), (32, 10), (36, 28)]), ((cx - 10, DESK - 21), [(-18, -2), (-22, 16), (-20, 30)]),
             ((cx, DESK - 23), [(0, -24), (-4, -44)])]
    leaves = []
    for (x0, y0), pts in vines:
        d = 'M%s,%s' % (f(x0), f(y0))
        px, py = x0, y0
        for dx, dy in pts:
            nx, ny = x0 + dx, y0 + dy
            d += ' Q%s,%s %s,%s' % (f((px + nx) / 2 + rnd.uniform(-3, 3)), f((py + ny) / 2), f(nx), f(ny))
            px, py = nx, ny
            ang = math.degrees(math.atan2(dx, -dy)) + rnd.uniform(-40, 40)
            leaves.append(leaf(nx, ny, rnd.uniform(5.5, 8), ang + 180 if dy > 0 else ang + rnd.choice([-60, 60]), rnd.choice([LEAF, LEAFD, LEAFL])))
            leaves.append(leaf((px + nx) / 2 + rnd.uniform(-3, 3), (py + ny) / 2, rnd.uniform(4, 6), rnd.uniform(0, 360), rnd.choice([LEAF, LEAFD])))
        o.append(path(d, 'none', stroke=LEAFD, stroke_width=0.45))
    # a crown of leaves at the rim
    for k in range(9):
        a = -150 + k * 26 + rnd.uniform(-8, 8)
        leaves.append(leaf(cx + rnd.uniform(-9, 9), DESK - 22 + rnd.uniform(-3, 2), rnd.uniform(6, 9), a, rnd.choice([LEAF, LEAFD, LEAFL])))
    # the pot: stoneware, a matt cream glaze dipped in slate, a little foot
    pot = 'M%s,%s L%s,%s C%s,%s %s,%s %s,%s L%s,%s C%s,%s %s,%s %s,%s Z' % (
        f(cx - 13), f(DESK - 22), f(cx + 13), f(DESK - 22), f(cx + 13), f(DESK - 10), f(cx + 11), f(DESK - 3), f(cx + 9), f(DESK - 1.4),
        f(cx - 9), f(DESK - 1.4), f(cx - 11), f(DESK - 3), f(cx - 13), f(DESK - 10), f(cx - 13), f(DESK - 22))
    hang = [l for l in leaves]
    o = [g(o)]
    o.append(g([path(pot, P['cream']),
                g([path('M%s,%s L%s,%s L%s,%s C%s,%s %s,%s %s,%s Z' % (f(cx - 14), f(DESK - 10), f(cx + 14), f(DESK - 13), f(cx + 14), f(DESK), f(cx + 4), f(DESK + 1), f(cx - 4), f(DESK + 1), f(cx - 14), f(DESK)), P['slate']),
                   halftone(cx + 2, DESK - 23, cx + 14, DESK, lambda x, y: (x - cx - 2) / 12 * 0.8, 0.8, P['stone'])], clip_path='url(#pot)'),
                rect(cx - 13.6, DESK - 23.2, 27.2, 1.6, light(P['cream'], 0.3)),
                rect(cx - 7, DESK - 1.4, 14, 1.4, dark(P['slate'], 0.2))]))
    o.append(g(hang))
    defs = common(131) + clip('pot', path(pot, '#000'))
    return render('pothos', g(g(o, filter='url(#gr)'), filter='url(#pr)'), W, H, SCALE, OUT, defs=defs)

# ---- a mug: cream stoneware dipped in terracotta, a loop handle
def mug():
    W, H = 30, 30
    o = [path('M4,4 L22,4 L21.4,28 C21.4,29 20,30 18,30 L8,30 C6,30 4.6,29 4.6,28 Z', P['cream']),
         path('M21.6,9 C29,8 29,22 21.2,21 L21.3,18.4 C26,19 26,11 21.6,11.8 Z', P['cream']),
         path('M4.3,17 L21.7,15 L21.4,28 C21.4,29 20,30 18,30 L8,30 C6,30 4.6,29 4.6,28 Z', P['accent']),
         rect(4, 4, 18, 1.4, light(P['cream'], 0.3)), rect(5, 5.4, 16, 1.2, P['walnutd'], opacity=0.75),
         halftone(14, 4, 22, 30, lambda x, y: (x - 14) / 8 * 0.7, 0.7, '#000', opacity=0.18),
         path('M4,4 L22,4 L21.4,28 C21.4,29 20,30 18,30 L8,30 C6,30 4.6,29 4.6,28 Z', 'none', stroke=P['soft'], stroke_width=0.4, transform='translate(-0.3 0.2)'),
         path('M21.6,9 C29,8 29,22 21.2,21 L21.3,18.4 C26,19 26,11 21.6,11.8 Z', 'none', stroke=P['soft'], stroke_width=0.4, transform='translate(-0.3 0.2)')]
    return render('mug', g(g(o, filter='url(#gr)'), filter='url(#pr)'), W, H, SCALE, OUT, defs=common(141))

if __name__ == '__main__':
    import sys
    for w in (sys.argv[1:] or ['sieve_print', 'chair', 'rug', 'pothos', 'mug']): globals()[w]()
