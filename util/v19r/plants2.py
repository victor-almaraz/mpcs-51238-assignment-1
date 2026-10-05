# v21's plants drawn again, lusher: leaves layered in depth (those behind darker and cooler),
# each blade lit across from the upper left with its veins, pots with their glaze or clay
# and a rim of soil, and the stands' wood and brass. The fiddle-leaf fig and the monstera
# stand on the floor; the golden pothos trails over the desk.
import math, random
from mcm import *
from mcm2 import *
from render import render, REPO
OUT = REPO + '/v21/assets'
S = 6
G1, G2, G3 = '#4f6b42', '#5f7a4f', '#7c9862'

def fin(name, o, W, H, D, seed):
    defs = D.out() + print_filter('pr', 1.4, 0.1, seed) + grain_filter('gr', 1.1, 0.02, seed + 1)
    return render(name, g(g(o, filter='url(#gr)'), filter='url(#pr)'), W, H, S, OUT, defs=defs)

def leaf_fill(D, c, depth):
    """a blade's colour, cooler and darker the further back it is (depth 0 front .. 1 back)"""
    base = mix(c, '#2e4034', depth * 0.45)
    return D.lin([(0, light(base, 0.22)), (0.5, base), (1, dark(base, 0.28))], 0, 0, 1, 1)

def fig_leaf(D, x, y, s, ang, c, depth):
    d = ('M0,0 C%s,%s %s,%s %s,%s C%s,%s %s,%s 0,%s C%s,%s %s,%s %s,%s C%s,%s %s,%s 0,0 Z' % (
        f(s * 0.38), f(-s * 0.05), f(s * 0.52), f(s * 0.38), f(s * 0.38), f(s * 0.56), f(s * 0.66), f(s * 0.82), f(s * 0.32), f(s * 1.18), f(s * 1.22),
        f(-s * 0.32), f(s * 1.18), f(-s * 0.66), f(s * 0.82), f(-s * 0.38), f(s * 0.56), f(-s * 0.52), f(s * 0.38), f(-s * 0.38), f(-s * 0.05)))
    out = [path(d, leaf_fill(D, c, depth))]
    vc = light(c, 0.35) if depth < 0.5 else dark(c, 0.1)
    out.append(path('M0,%s C%s,%s %s,%s 0,%s' % (f(s * 0.06), f(s * 0.03), f(s * 0.5), f(-s * 0.02), f(s * 0.9), f(s * 1.14)), 'none', stroke=vc, stroke_width=0.32, opacity=0.8))
    for k in range(5):
        t = 0.2 + k * 0.17
        for sd in (-1, 1):
            out.append(path('M0,%s Q%s,%s %s,%s' % (f(s * t), f(sd * s * 0.2), f(s * (t + 0.02)), f(sd * s * 0.38), f(s * (t - 0.08))), 'none', stroke=vc, stroke_width=0.16, opacity=0.6))
    out.append(path(d, 'none', stroke=dark(c, 0.4), stroke_width=0.15, opacity=0.6))
    return g(out, transform='translate(%s %s) rotate(%s)' % (f(x), f(y), f(ang)))

def fig():
    W, H = 110, 210
    D = Defs(); o = []
    rnd = random.Random(21)
    o.append(ellipse(56, 209.2, 30, 1.4, '#000', opacity=0.35, filter=D.blur(0.9)))
    teak = D.lin([(0, '#c99a6b'), (0.4, '#9a6a43'), (1, '#6a4428')], 0, 0, 1, 0)
    for x0, x1, back in ((55, 56, True), (42, 30, False), (68, 82, False)):
        o.append(poly([(x0 - 1.5, 168), (x0 + 1.5, 168), (x1 + 1.3, H - 0.6), (x1 - 1.3, H - 0.6)], dark('#9a6a43', 0.25) if back else teak))
    o.append(path(rrect(35, 165.6, 40, 3.8, 1.2), D.lin([(0, '#d8ad7c'), (0.5, '#9a6a43'), (1, '#5f3d24')])))
    pot = 'M38,137 L72,137 L68.4,166 L41.6,166 Z'
    o.append(path(pot, D.lin([(0, '#d8875d'), (0.45, '#b86a45'), (1, '#7d4024')], 0, 0, 1, 0)))
    o.append(path(rrect(35.6, 131.6, 38.8, 6.4, 1.4), D.lin([(0, '#e19a70'), (0.5, '#c0724c'), (1, '#8a4a2b')], 0, 0, 1, 0)))
    o.append(rect(36, 132, 38, 0.6, '#ffffff', opacity=0.3))
    o.append(ellipse(55, 132.4, 17.4, 1.3, '#3a2a1e'))
    o.append(rect(38, 138, 34, 2.0, '#000', opacity=0.15))
    # trunk and branches
    trunk = D.lin([(0, '#8a6a4e'), (1, '#4a3324')], 0, 0, 1, 0)
    o.append(path('M53.6,133 C53,110 56,90 53,60 C52,45 55,30 54,18 L56,18 C57,30 54,45 55,60 C58,90 55,110 56.4,133 Z', trunk))
    o.append(path('M54.2,88 C48,80 40,74 31,72', 'none', stroke='#5a3f2c', stroke_width=0.9))
    o.append(path('M55.4,70 C62,62 70,58 79,55', 'none', stroke='#5a3f2c', stroke_width=0.9))
    spots = [(55, 18, 13, 180), (49, 28, 14, 140), (62, 32, 14, 215), (46, 44, 15, 118), (64, 48, 15, 242), (51, 60, 15, 152), (61, 72, 14, 205),
             (31, 72, 14, 98), (39, 76, 13, 160), (79, 55, 14, 258), (71, 59, 13, 200), (48, 96, 14, 132), (62, 103, 13, 228), (52, 115, 12, 168),
             (58, 24, 11, 200), (44, 64, 12, 110), (67, 84, 12, 236), (36, 86, 11, 140)]
    order = sorted(spots, key=lambda s_: rnd.random())
    for i, (x, y, s, a) in enumerate(order):
        depth = 1 - i / (len(order) - 1)
        o.append(fig_leaf(D, x, y, s * 1.05, a + rnd.uniform(-10, 10), rnd.choice([G1, G2, G3, G2]), depth * 0.9))
    return fin('plant-fig', o, W, H, D, 151)

def monstera():
    W, H = 140, 160
    cx = 70
    D = Defs(); o = []
    rnd = random.Random(31)
    o.append(ellipse(cx, 159.4, 30, 1.2, '#000', opacity=0.35, filter=D.blur(0.8)))
    brassg = D.lin([(0, '#f3dfa0'), (0.4, '#c9a14e'), (1, '#7d5c22')], 0, 0, 1, 0)
    for x in (cx - 20, cx + 20):
        for a, b in ((x - 4, x - 7), (x + 4, x - 3)):
            o.append(line(a, 128, b, H - 1, '#7d5c22', 1.0))
            o.append(line(a - 0.2, 128, b - 0.2, H - 1, '#f3dfa0', 0.3, opacity=0.8))
        o.append(path('M%s,%s C%s,%s %s,%s %s,%s' % (f(x - 7), f(H - 1), f(x - 7), f(H + 0.7), f(x - 3), f(H + 0.7), f(x - 3), f(H - 1)), 'none', stroke='#b28d42', stroke_width=1.0))
    leaves = [(-58, 40, 22, 0.9), (60, 40, 22, 0.9), (-38, 30, 20, 0.7), (36, 28, 20, 0.7), (-26, 52, 28, 0.4), (24, 54, 28, 0.35), (0, 50, 30, 0.1), (-50, 46, 24, 0.2), (50, 44, 24, 0.15)]
    masks = []
    for n, (ang, length, size, depth) in enumerate(leaves):
        a = math.radians(ang)
        tx, ty = cx + math.sin(a) * length * 0.9, 104 - math.cos(a) * length * 1.5
        o.append(path('M%s,104 Q%s,%s %s,%s' % (f(cx), f(cx + math.sin(a) * length * 0.25), f(104 - length * 0.8), f(tx), f(ty)), 'none', stroke=mix('#4a6340', '#2e4034', depth * 0.4), stroke_width=0.9))
        c = rnd.choice([G1, G2, G2, G3])
        R = size / 2
        shape = 'M0,0 C%s,%s %s,%s 0,%s C%s,%s %s,%s 0,0 Z' % (f(R * 1.3), f(-R * 0.5), f(R * 1.2), f(R * 1.6), f(R * 2.0), f(-R * 1.2), f(R * 1.6), f(-R * 1.3), f(-R * 0.5))
        slits = ' '.join('M%s,%s L%s,%s' % (f(sd * R * 1.5), f(R * (0.3 + k * 0.34)), f(sd * R * 0.26), f(R * (0.42 + k * 0.34))) for k in range(5) for sd in (-1, 1))
        holes = ''.join('<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="#000"/>' % (f(sd * R * 0.5), f(R * (0.6 + k * 0.5)), f(R * 0.09), f(R * 0.05)) for k in range(2) for sd in (-1, 1))
        mid = 'mk%d' % n
        masks.append('<mask id="%s" maskUnits="userSpaceOnUse" x="-50" y="-50" width="100" height="100"><path d="%s" fill="#fff"/><path d="%s" stroke="#000" stroke-width="%s" stroke-linecap="round"/>%s</mask>' % (mid, shape, slits, f(R * 0.11), holes))
        rot = ang + 180 + rnd.uniform(-8, 8)
        vc = light(c, 0.3)
        veins = ' '.join('M0,%s L%s,%s' % (f(R * (0.25 + k * 0.34)), f(sd * R * 1.0), f(R * (0.38 + k * 0.34))) for k in range(5) for sd in (-1, 1))
        o.append(g([path(shape, leaf_fill(D, c, depth), mask='url(#%s)' % mid),
                    path(veins, 'none', stroke=vc, stroke_width=0.18, opacity=0.5, mask='url(#%s)' % mid),
                    path('M0,%s L0,%s' % (f(R * 0.1), f(R * 1.9)), 'none', stroke=vc, stroke_width=0.4, opacity=0.8)],
                   transform='translate(%s %s) rotate(%s)' % (f(tx), f(ty), f(rot))))
    pot = 'M%s,104 L%s,104 L%s,126 C%s,129 %s,130 %s,130 L%s,130 C%s,130 %s,129 %s,126 Z' % (
        f(cx - 24), f(cx + 24), f(cx + 24), f(cx + 24), f(cx + 21), f(cx + 18), f(cx - 18), f(cx - 21), f(cx - 24), f(cx - 24))
    o.append(path(pot, D.lin([(0, '#fbf8f0'), (0.55, '#ece6d8'), (1, '#bdb4a2')], 0, 0, 1, 0)))
    o.append(path(pot, D.lin([(0, '#ffffff', 0.5), (0.18, '#ffffff', 0), (1, '#ffffff', 0)], 0, 0, 0, 1)))
    o.append(ellipse(cx, 104.2, 23.6, 1.2, '#3a2a1e'))
    o.append(rect(cx - 24, 103.4, 48, 0.9, '#ffffff', opacity=0.7))
    o.append(path(pot, 'none', stroke='#8f8673', stroke_width=0.3))
    return fin('plant-monstera', o, W, H, D, 161, ) if False else render('plant-monstera', g(g(o, filter='url(#gr)'), filter='url(#pr)'), W, H, S, OUT,
        defs=D.out() + ''.join(masks) + print_filter('pr', 1.4, 0.1, 161) + grain_filter('gr', 1.1, 0.02, 162))

def heart(D, x, y, s, ang, c, depth, variegate, rnd):
    d = 'M0,0 C%s,%s %s,%s 0,%s C%s,%s %s,%s 0,0 Z' % (f(s * 0.75), f(-s * 0.25), f(s * 0.65), f(s * 0.95), f(s * 1.25), f(-s * 0.65), f(s * 0.95), f(-s * 0.75), f(-s * 0.25))
    out = [path(d, leaf_fill(D, c, depth))]
    if variegate:
        # golden pothos: soft streaks of cream marbling the blade from the rib outward
        for k in range(2):
            t = rnd.uniform(0.3, 0.85); sd = rnd.choice((-1, 1))
            out.append(ellipse(sd * s * rnd.uniform(0.12, 0.3), s * t, s * rnd.uniform(0.08, 0.16), s * rnd.uniform(0.18, 0.3), '#e6dfa6',
                               opacity=0.45, filter=D.blur(s * 0.05), transform='rotate(%s %s %s)' % (f(sd * 35), f(sd * s * 0.2), f(s * t))))
    out.append(path('M0,%s L0,%s' % (f(s * 0.08), f(s * 1.15)), 'none', stroke=light(c, 0.35), stroke_width=0.22, opacity=0.8))
    out.append(path(d, 'none', stroke=dark(c, 0.4), stroke_width=0.12, opacity=0.5))
    return g(out, transform='translate(%s %s) rotate(%s)' % (f(x), f(y), f(ang)))

def pothos():
    W, H = 100, 116
    DESK, cx = 82, 50
    D = Defs(); o = []
    rnd = random.Random(8)
    vines = [((cx - 6, DESK - 22), [(-14, -20), (-20, -38), (-16, -52)]), ((cx + 4, DESK - 22), [(10, -22), (20, -36), (24, -46)]),
             ((cx + 10, DESK - 21), [(20, -6), (28, 10), (31, 30)]), ((cx - 10, DESK - 21), [(-18, -2), (-24, 14), (-22, 32)]),
             ((cx, DESK - 23), [(0, -24), (-4, -44)]), ((cx + 12, DESK - 20), [(20, -12), (30, -8), (34, 0)])]
    leaves = []
    for (x0, y0), pts in vines:
        d = 'M%s,%s' % (f(x0), f(y0)); px, py = x0, y0
        for dx, dy in pts:
            nx, ny = x0 + dx, y0 + dy
            d += ' Q%s,%s %s,%s' % (f((px + nx) / 2 + rnd.uniform(-3, 3)), f((py + ny) / 2), f(nx), f(ny))
            ang = math.degrees(math.atan2(dx, -dy))
            leaves.append((nx, ny, rnd.uniform(6, 8.5), ang + 180 if dy > 0 else ang + rnd.choice([-60, 60])))
            leaves.append(((px + nx) / 2 + rnd.uniform(-3, 3), (py + ny) / 2, rnd.uniform(4.5, 6.5), rnd.uniform(0, 360)))
            px, py = nx, ny
        o.append(path(d, 'none', stroke='#4f6b42', stroke_width=0.5))
    for k in range(11):
        leaves.append((cx + rnd.uniform(-10, 10), DESK - 22 + rnd.uniform(-4, 2), rnd.uniform(6.5, 9.5), -150 + k * 27 + rnd.uniform(-8, 8)))
    rnd.shuffle(leaves)
    lv = [heart(D, x, y, s, a, rnd.choice([G1, G2, G3, G2]), 0.8 * (1 - i / len(leaves)), rnd.random() < 0.7, rnd) for i, (x, y, s, a) in enumerate(leaves)]
    pot = 'M%s,%s L%s,%s C%s,%s %s,%s %s,%s L%s,%s C%s,%s %s,%s %s,%s Z' % (
        f(cx - 13), f(DESK - 22), f(cx + 13), f(DESK - 22), f(cx + 13), f(DESK - 10), f(cx + 11), f(DESK - 3), f(cx + 9), f(DESK - 1.4),
        f(cx - 9), f(DESK - 1.4), f(cx - 11), f(DESK - 3), f(cx - 13), f(DESK - 10), f(cx - 13), f(DESK - 22))
    cp = D.clip(path(pot, '#000'))
    o.append(ellipse(cx, DESK - 0.6, 11, 0.9, '#000', opacity=0.35, filter=D.blur(0.6)))
    o.append(g([path(pot, D.lin([(0, '#fbf8ef'), (0.55, '#ebe3d1'), (1, '#b9ae98')], 0, 0, 1, 0)),
                path('M%s,%s L%s,%s L%s,%s C%s,%s %s,%s %s,%s Z' % (f(cx - 14), f(DESK - 10), f(cx + 14), f(DESK - 13), f(cx + 14), f(DESK), f(cx + 4), f(DESK + 1), f(cx - 4), f(DESK + 1), f(cx - 14), f(DESK)),
                     D.lin([(0, '#6b7c84'), (0.5, '#49555a'), (1, '#2b3337')], 0, 0, 1, 0)),
                path('M%s,%s C%s,%s %s,%s %s,%s' % (f(cx - 13), f(DESK - 9.6), f(cx - 4), f(DESK - 11), f(cx + 4), f(DESK - 11.6), f(cx + 13), f(DESK - 12.6)), 'none', stroke='#ffffff', stroke_width=0.35, opacity=0.4),
                rect(cx - 10, DESK - 21, 2.4, 18, '#ffffff', opacity=0.35, filter=D.blur(0.6))], clip_path=cp))
    o.append(ellipse(cx, DESK - 22, 12.8, 1.2, '#3a2a1e'))
    o.append(path(pot, 'none', stroke='#8f8673', stroke_width=0.22))
    o += lv
    return fin('pothos', o, W, H, D, 131)

if __name__ == '__main__':
    import sys
    for w in (sys.argv[1:] or ['fig', 'monstera', 'pothos']): globals()[w]()
