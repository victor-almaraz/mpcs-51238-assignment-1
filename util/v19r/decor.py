# v22's room: the things that can be swapped, each drawn again in other kinds, in the same
# boxes as v21's so any of them takes the same place: floor plants for either end (a snake
# plant and a kentia palm for the left, a Boston fern and a rubber plant for the right), desk
# plants (a jade and a bowl of cacti), prints (the Philips Pavilion and a Polytope for the
# wide frame, an Arp collage and a Taeuber-Arp composition for the narrow one), and mugs.
import math, random, sys
from mcm import *
from mcm2 import *
from render import render, REPO
from plants2 import leaf_fill, G1, G2, G3
OUT = REPO + '/v22/assets'
S = 6

def fin(name, o, W, H, D, seed, extra='', scale=S, grain=0.02, thr=0.1):
    defs = D.out() + extra + print_filter('pr', 1.4, thr, seed) + grain_filter('gr', 1.1, grain, seed + 1)
    return render(name, g(g(o, filter='url(#gr)'), filter='url(#pr)'), W, H, scale, OUT, defs=defs)

def floor_shadow(D, o, cx, y, rx):
    o.append(ellipse(cx, y, rx, 1.4, '#000', opacity=0.35, filter=D.blur(0.9)))

# ================================================================ floor plants, left: 110 x 210
def snake():
    # Sansevieria trifasciata 'Laurentii': broad flat sword leaves rising stiffly from the
    # soil in clumps, each turning a little as it rises (so it narrows where it shows its
    # edge), banded across in zigzags of grey-green on deep green, with thick golden margins
    # and a hard point; in a tall slate cylinder on a teak plinth
    W, H = 110, 210
    D = Defs(); o = []; rnd = random.Random(12)
    floor_shadow(D, o, 55, 209.2, 30)
    o.append(path(rrect(30, 198, 50, 11.4, 1.2), D.lin([(0, '#c99a6b'), (0.4, '#9a6a43'), (1, '#6a4428')], 0, 0, 1, 0)))
    o.append(rect(30, 198, 50, 0.6, '#ffffff', opacity=0.3))
    top = 127
    # (base x, height, lean, width, twist): back leaves first
    leaves = [(-14, 70, -14, 9, 0.6), (13, 76, 13, 9, 0.5), (-4, 104, -5, 11, 0.4), (6, 96, 6, 10.5, 0.7), (-10, 88, -9, 10, 0.9),
              (11, 112, 4, 11.5, 0.3), (-1, 120, 1, 12.5, 0.5), (16, 60, 18, 8, 0.8), (-17, 56, -18, 8, 0.6), (3, 84, 9, 11, 1.0), (-7, 74, -2, 10, 0.2)]
    def leaf(i, x0, h, lean, wd, tw):
        depth = 1 - i / (len(leaves) - 1)
        N = 40
        cx = lambda t: x0 + lean * t * t
        cy = lambda t: top + 2 - h * t
        L, R = [], []
        for k in range(N + 1):
            t = k / N
            prof = (1 - t ** 2.4) * (0.55 + 0.45 * abs(math.cos(math.pi * t * tw * 1.4)))
            w = wd / 2 * max(prof, 0.02) * (1 if t < 0.97 else 0.3)
            dx = 2 * lean * t; dy = -h
            n = math.hypot(dx, dy); nx, ny = -dy / n, dx / n
            L.append((cx(t) - nx * w, cy(t) - ny * w)); R.append((cx(t) + nx * w, cy(t) + ny * w))
        tip = (cx(1), cy(1) - 2.2)
        outline = 'M' + ' L'.join('%s,%s' % (f(x), f(y)) for x, y in L) + ' L%s,%s ' % (f(tip[0]), f(tip[1])) + ' L'.join('%s,%s' % (f(x), f(y)) for x, y in reversed(R)) + ' Z'
        inner_pts_l = [(x + (cx(k / N) - x) * 0.3, y) for k, (x, y) in enumerate(L)]
        inner_pts_r = [(x + (cx(k / N) - x) * 0.3, y) for k, (x, y) in enumerate(R)]
        inner = 'M' + ' L'.join('%s,%s' % (f(x), f(y)) for x, y in inner_pts_l) + ' ' + ' L'.join('%s,%s' % (f(x), f(y)) for x, y in reversed(inner_pts_r)) + ' Z'
        out = []
        gold = mix('#d6c45a', '#7d7a40', depth * 0.55)
        out.append(path(outline, D.lin([(0, light(gold, 0.15)), (1, dark(gold, 0.15))], 0, 0, 1, 0)))
        base = mix('#2f4a32', '#1c2a20', depth * 0.5)
        cp = D.clip(path(inner, '#000'))
        g_ = [rect(x0 - 30, top - h - 5, 60, h + 10, D.lin([(0, light(base, 0.12)), (0.5, base), (1, dark(base, 0.25))], 0, 0, 1, 0))]
        band = mix('#a7b58f', '#56664f', depth * 0.6)
        y = top
        while y > top - h:
            amp = rnd.uniform(1.0, 2.2); step = rnd.uniform(2.6, 4.2)
            zz = 'M%s,%s' % (f(x0 - 14), f(y))
            for j in range(10):
                zz += ' l%s,%s' % (f(2.8), f(-amp if j % 2 else amp))
            g_.append(path(zz, 'none', stroke=band, stroke_width=rnd.uniform(0.6, 1.3), opacity=rnd.uniform(0.45, 0.75),
                           transform='translate(%s 0)' % f(lean * ((top - y) / h) ** 2)))
            y -= step
        # the turn of the blade: light down one side where it faces the window
        g_.append(path(' '.join('%s%s,%s' % ('M' if k == 0 else 'L', f(x), f(y)) for k, (x, y) in enumerate(inner_pts_l)), 'none', stroke='#ffffff', stroke_width=1.0, opacity=0.12))
        out.append(g(g_, clip_path=cp))
        out.append(path(outline, 'none', stroke=dark(gold, 0.4), stroke_width=0.2, opacity=0.6))
        return out
    # the leaves rise from the soil inside the pot's mouth: clipped to the air above its rim
    # and to the pot's own width below it
    mouth = D.clip(rect(0, 0, W, 123, '#000') + rect(36, 0, 38, H, '#000'))
    o.append(g(sum((leaf(i, 55 + lf[0] * 1.05, lf[1], lf[2], lf[3] * 1.45, lf[4]) for i, lf in enumerate(leaves)), []), clip_path=mouth))
    # the pot: a tall cylinder glazed slate, its lip catching the light
    pot = rrect(35, 124, 40, 75, (1.5, 1.5, 3, 3))
    o.append(path(pot, D.lin([(0, '#7b8a91'), (0.3, '#556267'), (0.75, '#3a4448'), (1, '#262d30')], 0, 0, 1, 0)))
    o.append(rect(39, 128, 2.6, 66, '#ffffff', opacity=0.18, filter=D.blur(0.7)))
    o.append(path(rrect(33.6, 121.6, 42.8, 4.4, 1.2), D.lin([(0, '#8b9aa1'), (0.4, '#5c6a70'), (1, '#2e373b')], 0, 0, 1, 0)))
    o.append(ellipse(55, 122.6, 19.6, 1.0, '#2a1e16'))
    o.append(rect(35, 186, 40, 0.5, '#ffffff', opacity=0.2))
    return fin('plant-snake', o, W, H, D, 201)

def palm():
    # a kentia palm (Howea forsteriana): a few long fronds arching up and out from a cluster
    # of stems, each a curved rachis with its leaflets set evenly along it, long in the middle
    # and short at either end, drooping from it; in a woven rattan basket
    W, H = 110, 210
    D = Defs(); o = []; rnd = random.Random(9)
    floor_shadow(D, o, 55, 209.2, 30)
    bx, by = 55, 150
    # (angle out from upright, length, how far it arches over): back fronds first
    fronds = [(-62, 92, 0.55), (58, 90, 0.55), (-28, 108, 0.3), (24, 104, 0.32), (-80, 70, 0.7), (82, 68, 0.7), (-8, 118, 0.15), (40, 96, 0.45), (-44, 98, 0.45), (8, 112, 0.2)]
    for i, (ang, L, arch) in enumerate(fronds):
        depth = 1 - i / (len(fronds) - 1)
        a = math.radians(ang)
        # the rachis: up and out, then over
        p0 = (bx + math.sin(a) * 3, by)
        L *= 1.18
        p1 = (bx + math.sin(a) * L * 0.16, by - L * 0.8)
        p2 = (bx + math.sin(a) * L * (0.42 + arch * 0.12), by - L * (0.86 - arch * 0.6))
        def at(t):
            return ((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0], (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1])
        def tangent(t):
            return (2 * (1 - t) * (p1[0] - p0[0]) + 2 * t * (p2[0] - p1[0]), 2 * (1 - t) * (p1[1] - p0[1]) + 2 * t * (p2[1] - p1[1]))
        stem = mix('#6b8452', '#2e4034', depth * 0.5)
        o.append(path('M%s,%s Q%s,%s %s,%s' % (f(p0[0]), f(p0[1]), f(p1[0]), f(p1[1]), f(p2[0]), f(p2[1])), 'none', stroke=stem, stroke_width=0.9))
        n = 30
        for k in range(4, n):
            t = k / n
            px, py = at(t); tx, ty = tangent(t); th = math.atan2(ty, tx)
            ln = 4 + 11 * math.sin(math.pi * (t - 0.1) / 0.92) if t > 0.1 else 4
            for sd in (-1, 1):
                la = th + sd * 0.75 + 0.45 * (1 if math.cos(th) >= 0 else -1) * 0.6   # leaflets droop under their weight
                mx_, my_ = px + math.cos(la) * ln * 0.55, py + math.sin(la) * ln * 0.55 + ln * 0.12
                qx, qy = px + math.cos(la) * ln, py + math.sin(la) * ln + ln * 0.38
                c = mix(rnd.choice(['#5f7a4f', '#6b8a56', '#57724a']), '#2b3d31', depth * 0.5)
                nx_, ny_ = -math.sin(la) * 0.65, math.cos(la) * 0.65
                o.append(path('M%s,%s Q%s,%s %s,%s Q%s,%s %s,%s Z' % (f(px), f(py), f(mx_ + nx_), f(my_ + ny_), f(qx), f(qy), f(mx_ - nx_), f(my_ - ny_), f(px), f(py)), c))
                if depth < 0.5 and k % 3 == 0:
                    o.append(line(px, py, mx_, my_, '#ffffff', 0.12, opacity=0.25))
    # the stems, sheathed, rising from the soil
    for k in range(5):
        x = bx - 6 + k * 3
        o.append(path('M%s,150 Q%s,138 %s,128' % (f(x), f(x + (k - 2) * 0.8), f(x + (k - 2) * 2.4)), 'none', stroke='#5a6b45', stroke_width=1.6))
    # the basket: rattan woven in rows, a rolled rim
    bk = 'M30,148 L80,148 L75,206 L35,206 Z'
    cp = D.clip(path(bk, '#000'))
    weave = [path(bk, D.lin([(0, '#d9b98a'), (0.5, '#b8925e'), (1, '#7f5f36')], 0, 0, 1, 0))]
    for r in range(15):
        y = 150 + r * 3.9
        for c in range(14):
            x = 28 + c * 4 + (2 if r % 2 else 0)
            weave.append(path(rrect(x, y, 3.4, 2.8, 1.2), '#ffffff', opacity=0.12))
            weave.append(path(rrect(x, y + 2.2, 3.4, 0.6, 0.3), '#5a3f22', opacity=0.35))
    o.append(g(weave, clip_path=cp))
    o.append(path(rrect(28, 144.6, 54, 5, 2.5), D.lin([(0, '#e5c899'), (0.5, '#b8925e'), (1, '#7f5f36')])))
    o.append(path(bk, 'none', stroke='#6a4e2c', stroke_width=0.3))
    return fin('plant-palm', o, W, H, D, 211)

# ================================================================ floor plants, right: 140 x 160
def stand(D, o, cx, H, top=128):
    brassg = D.lin([(0, '#f3dfa0'), (0.4, '#c9a14e'), (1, '#7d5c22')], 0, 0, 1, 0)
    for x in (cx - 20, cx + 20):
        for a, b in ((x - 4, x - 7), (x + 4, x - 3)):
            o.append(line(a, top, b, H - 1, '#7d5c22', 1.0))
            o.append(line(a - 0.2, top, b - 0.2, H - 1, '#f3dfa0', 0.3, opacity=0.8))

def fern():
    # a Boston fern (Nephrolepis exaltata) spilling from an ochre-glazed pot on hairpin legs:
    # long fronds arching out and down, their pinnae in pairs
    W, H = 140, 160
    cx = 70
    D = Defs(); o = []; rnd = random.Random(13)
    floor_shadow(D, o, cx, 159.4, 30)
    stand(D, o, cx, H)
    pot = 'M%s,98 L%s,98 L%s,126 C%s,129 %s,130 %s,130 L%s,130 C%s,130 %s,129 %s,126 Z' % (
        f(cx - 22), f(cx + 22), f(cx + 19), f(cx + 19), f(cx + 17), f(cx + 15), f(cx - 15), f(cx - 17), f(cx - 19), f(cx - 19))
    fronds = []
    for k in range(30):
        ang = rnd.uniform(-150, 150)
        fronds.append((ang, rnd.uniform(38, 62) * (0.75 if abs(ang) < 40 else 1)))
    fronds.sort(key=lambda fr: -abs(fr[0]))   # the drooping ones behind
    def frond(ang, L, depth):
        a = math.radians(ang)
        x0, y0 = cx + math.sin(a) * 6, 98
        # out, up a little, then over and down under its own weight
        ex = x0 + math.sin(a) * L
        ey = y0 - math.cos(a) * L * 0.6 + (abs(math.sin(a)) * L * 0.75)
        c1x, c1y = x0 + math.sin(a) * L * 0.35, y0 - L * (0.55 if abs(ang) < 90 else 0.25)
        out = []
        col = mix(rnd.choice([G2, G3, '#8aa66a']), '#2e4034', depth * 0.45)
        out.append(path('M%s,%s Q%s,%s %s,%s' % (f(x0), f(y0), f(c1x), f(c1y), f(ex), f(ey)), 'none', stroke=col, stroke_width=0.45))
        n = 24
        for k in range(1, n):
            t = k / n
            px = (1 - t) ** 2 * x0 + 2 * (1 - t) * t * c1x + t * t * ex
            py = (1 - t) ** 2 * y0 + 2 * (1 - t) * t * c1y + t * t * ey
            tx = 2 * (1 - t) * (c1x - x0) + 2 * t * (ex - c1x); ty = 2 * (1 - t) * (c1y - y0) + 2 * t * (ey - c1y)
            th = math.atan2(ty, tx); ln = 4.4 * (1 - t * 0.7)
            for sd in (-1, 1):
                la = th + sd * 1.1
                out.append(path('M%s,%s L%s,%s' % (f(px), f(py), f(px + math.cos(la) * ln), f(py + math.sin(la) * ln)), 'none', stroke=col, stroke_width=1.1, stroke_linecap='round'))
        return out
    back = [fr for fr in fronds if abs(fr[0]) > 60]
    front = [fr for fr in fronds if abs(fr[0]) <= 60]
    for i, (ang, L) in enumerate(front): o += frond(ang, L, 0.7 - 0.5 * i / max(1, len(front)))
    o.append(path(pot, D.lin([(0, '#e9c160'), (0.45, '#c99a2e'), (1, '#7d5c16')], 0, 0, 1, 0)))
    o.append(path(pot, D.lin([(0, '#ffffff', 0.4), (0.15, '#ffffff', 0), (1, '#ffffff', 0)], 0, 0, 0, 1)))
    o.append(rect(cx - 15, 102, 2.2, 24, '#ffffff', opacity=0.28, filter=D.blur(0.6)))
    o.append(ellipse(cx, 98.2, 21.6, 1.2, '#3a2a1e'))
    o.append(path(pot, 'none', stroke='#6e5114', stroke_width=0.3))
    for i, (ang, L) in enumerate(back): o += frond(ang, L, 0.3 * i / max(1, len(back)))
    return fin('plant-fern', o, W, H, D, 221)

def rubber():
    # a rubber plant (Ficus elastica 'Burgundy'): three stems with large glossy oval leaves,
    # dark green going to wine, a red sheath at each new leaf, in a white pot on a teak foot
    W, H = 140, 160
    cx = 70
    D = Defs(); o = []; rnd = random.Random(17)
    floor_shadow(D, o, cx, 159.4, 26)
    o.append(path(rrect(cx - 22, 150, 44, 9.4, 1.2), D.lin([(0, '#c99a6b'), (0.4, '#9a6a43'), (1, '#6a4428')], 0, 0, 1, 0)))
    stems = [(cx - 6, -10, 18), (cx + 2, 4, 8), (cx + 8, 12, 30)]
    for sx, lean, top in stems:
        o.append(path('M%s,108 C%s,70 %s,50 %s,%s' % (f(sx), f(sx + lean * 0.3), f(sx + lean * 0.8), f(sx + lean), f(top)), 'none', stroke='#5a4a36', stroke_width=1.4))
    leaves = []
    for sx, lean, top in stems:
        for k in range(6):
            t = k / 6
            px = sx + lean * (t ** 1.4); py = 100 - (100 - top) * t
            sd = 1 if k % 2 else -1
            leaves.append((px, py, rnd.uniform(15, 20) * (1 - t * 0.25), sd * rnd.uniform(55, 95) + (180 if False else 0), t))
        leaves.append((sx + lean, top, 9, rnd.uniform(-10, 10), 1.0))
    rnd.shuffle(leaves)
    for i, (x, y, s, ang, t) in enumerate(leaves):
        depth = 1 - i / (len(leaves) - 1)
        c = mix('#2f5a3c', '#6e2b36', 0.0 if t < 0.55 else (t - 0.55) * 1.6)
        d = 'M0,0 C%s,%s %s,%s 0,%s C%s,%s %s,%s 0,0 Z' % (f(s * 0.42), f(-s * 0.1), f(s * 0.46), f(s * 0.8), f(s * 1.15), f(-s * 0.46), f(s * 0.8), f(-s * 0.42), f(-s * 0.1))
        base = mix(c, '#1d2620', depth * 0.3)
        lv = [path(d, D.lin([(0, light(base, 0.38)), (0.4, base), (1, dark(base, 0.3))], 0, 0, 1, 1)),
              path('M0,%s Q%s,%s 0,%s' % (f(s * 0.1), f(s * 0.25), f(s * 0.55), f(s), ), 'none', stroke='#ffffff', stroke_width=0.5, opacity=0.22),
              path('M0,%s L0,%s' % (f(s * 0.05), f(s * 1.08)), 'none', stroke='#e6b9a6' if t > 0.5 else '#c9cfa8', stroke_width=0.4, opacity=0.75),
              ellipse(-s * 0.15, s * 0.4, s * 0.1, s * 0.3, '#ffffff', opacity=0.18, filter=D.blur(s * 0.04))]
        if t >= 1.0: lv.append(path('M0,0 L0,%s' % f(-s * 0.6), 'none', stroke='#c0453a', stroke_width=1.1, stroke_linecap='round'))
        o.append(g(lv, transform='translate(%s %s) rotate(%s)' % (f(x), f(y), f(ang + 180))))
    pot = rrect(cx - 19, 106, 38, 44, (1, 1, 2, 2))
    o.append(path(pot, D.lin([(0, '#fbf8f0'), (0.55, '#ece6d8'), (1, '#bdb4a2')], 0, 0, 1, 0)))
    o.append(rect(cx - 15, 110, 2.4, 36, '#ffffff', opacity=0.6, filter=D.blur(0.6)))
    o.append(ellipse(cx, 106.6, 18.4, 1.1, '#3a2a1e'))
    o.append(path(pot, 'none', stroke='#8f8673', stroke_width=0.3))
    return fin('plant-rubber', o, W, H, D, 231)

# ================================================================ desk plants: 100 x 116, the desk at 82
def jade():
    # a jade plant (Crassula ovata): a thick branching trunk, fat paddle leaves edged red, in
    # a low celadon bowl
    W, H = 100, 116
    DESK, cx = 82, 50
    D = Defs(); o = []; rnd = random.Random(23)
    o.append(ellipse(cx, DESK - 0.6, 15, 0.9, '#000', opacity=0.35, filter=D.blur(0.6)))
    trunk = '#6b5a3e'
    branches = [((cx, DESK - 12), (cx - 3, DESK - 26)), ((cx - 3, DESK - 26), (cx - 16, DESK - 40)), ((cx - 3, DESK - 26), (cx + 8, DESK - 44)),
                ((cx + 8, DESK - 44), (cx + 22, DESK - 52)), ((cx + 8, DESK - 44), (cx + 2, DESK - 60)), ((cx - 16, DESK - 40), (cx - 26, DESK - 46)),
                ((cx - 16, DESK - 40), (cx - 12, DESK - 56)), ((cx, DESK - 14), (cx + 14, DESK - 26)), ((cx + 14, DESK - 26), (cx + 26, DESK - 32))]
    for (x0, y0), (x1, y1) in branches:
        o.append(line(x0, y0, x1, y1, trunk, 2.6 if y0 > DESK - 30 else 1.6, stroke_linecap='round'))
        o.append(line(x0 - 0.4, y0, x1 - 0.4, y1, '#a59272', 0.4, opacity=0.6))
    tips = [b[1] for b in branches] + [(cx - 8, DESK - 33), (cx + 4, DESK - 36), (cx + 20, DESK - 40)]
    lv = []
    for x, y in tips:
        for k in range(rnd.randint(4, 6)):
            a = rnd.uniform(0, 360); s = rnd.uniform(4.5, 6.5)
            lv.append((x, y, s, a))
    rnd.shuffle(lv)
    for i, (x, y, s, a) in enumerate(lv):
        depth = 1 - i / (len(lv) - 1)
        c = mix('#6f8f4f', '#33452c', depth * 0.5)
        d = 'M0,0 C%s,%s %s,%s 0,%s C%s,%s %s,%s 0,0 Z' % (f(s * 0.55), f(s * 0.1), f(s * 0.6), f(s * 0.95), f(s * 1.2), f(-s * 0.6), f(s * 0.95), f(-s * 0.55), f(s * 0.1))
        o.append(g([path(d, D.lin([(0, light(c, 0.3)), (0.5, c), (1, dark(c, 0.3))], 0, 0, 1, 1)),
                    path(d, 'none', stroke='#b0503a', stroke_width=0.35, opacity=0.7),
                    ellipse(-s * 0.1, s * 0.5, s * 0.12, s * 0.28, '#ffffff', opacity=0.25)],
                   transform='translate(%s %s) rotate(%s)' % (f(x), f(y), f(a))))
    bowl = 'M%s,%s L%s,%s C%s,%s %s,%s %s,%s L%s,%s C%s,%s %s,%s %s,%s Z' % (
        f(cx - 18), f(DESK - 13), f(cx + 18), f(DESK - 13), f(cx + 17), f(DESK - 5), f(cx + 12), f(DESK - 1.5), f(cx + 8), f(DESK - 1.2),
        f(cx - 8), f(DESK - 1.2), f(cx - 12), f(DESK - 1.5), f(cx - 17), f(DESK - 5), f(cx - 18), f(DESK - 13))
    o.append(path(bowl, D.lin([(0, '#cfd9c3'), (0.5, '#a7b79c'), (1, '#6f7f68')], 0, 0, 1, 0)))
    o.append(path('M%s,%s C%s,%s %s,%s %s,%s' % (f(cx - 16), f(DESK - 10), f(cx - 6), f(DESK - 8), f(cx + 6), f(DESK - 8), f(cx + 16), f(DESK - 10)), 'none', stroke='#ffffff', stroke_width=0.4, opacity=0.45))
    o.append(ellipse(cx, DESK - 13, 17.8, 1.4, '#3a2a1e'))
    o.append(path(bowl, 'none', stroke='#5e6b58', stroke_width=0.22))
    return fin('desk-jade', o, W, H, D, 241)

def cacti():
    # three cacti in a terracotta pot: a column with arms, a round barrel ribbed and spined,
    # and a small one in flower
    W, H = 100, 116
    DESK, cx = 82, 50
    D = Defs(); o = []; rnd = random.Random(29)
    o.append(ellipse(cx, DESK - 0.6, 15, 0.9, '#000', opacity=0.35, filter=D.blur(0.6)))
    def body(d, c):
        return path(d, D.lin([(0, light(c, 0.25)), (0.45, c), (1, dark(c, 0.35))], 0, 0, 1, 0))
    def ribs(x, y0, y1, w, n, c):
        return g([line(x - w / 2 + w * (k + 0.5) / n, y0, x - w / 2 + w * (k + 0.5) / n, y1, dark(c, 0.3), 0.3, opacity=0.6) for k in range(n)])
    def spines(x, y0, y1, w):
        pts = []
        for k in range(int((y1 - y0) / 2.2)):
            for j in range(3):
                pts.append(circle(x - w / 2 + w * (j + 0.5) / 3 + rnd.uniform(-0.3, 0.3), y0 + k * 2.2 + rnd.uniform(0, 0.8), 0.25, '#f2ead0'))
        return g(pts, opacity=0.85)
    col = '#5b7a4e'
    # the column, with two arms
    o.append(body(rrect(cx - 4, DESK - 66, 9, 56, 4.5), col))
    o.append(body('M%s,%s C%s,%s %s,%s %s,%s L%s,%s C%s,%s %s,%s %s,%s Z' % (f(cx - 4), f(DESK - 34), f(cx - 12), f(DESK - 34), f(cx - 12), f(DESK - 38), f(cx - 12), f(DESK - 50),
                                                                       f(cx - 7), f(DESK - 50), f(cx - 7), f(DESK - 40), f(cx - 6), f(DESK - 39), f(cx - 4), f(DESK - 39)), col))
    o.append(body('M%s,%s C%s,%s %s,%s %s,%s L%s,%s C%s,%s %s,%s %s,%s Z' % (f(cx + 5), f(DESK - 28), f(cx + 13), f(DESK - 28), f(cx + 13), f(DESK - 32), f(cx + 13), f(DESK - 44),
                                                                       f(cx + 8), f(DESK - 44), f(cx + 8), f(DESK - 34), f(cx + 7), f(DESK - 33), f(cx + 5), f(DESK - 33)), col))
    o.append(ribs(cx + 0.5, DESK - 64, DESK - 12, 9, 4, col))
    o.append(spines(cx + 0.5, DESK - 64, DESK - 12, 9))
    # the barrel
    bc = '#6d8a55'
    o.append(body('M%s,%s C%s,%s %s,%s %s,%s C%s,%s %s,%s %s,%s Z' % (f(cx - 20), f(DESK - 12), f(cx - 22), f(DESK - 30), f(cx - 4), f(DESK - 30), f(cx - 6), f(DESK - 12),
                                                                f(cx - 9), f(DESK - 11), f(cx - 17), f(DESK - 11), f(cx - 20), f(DESK - 12)), bc))
    for k in range(5):
        x = cx - 19 + k * 3.2
        o.append(path('M%s,%s Q%s,%s %s,%s' % (f(cx - 13), f(DESK - 27), f(x - 1), f(DESK - 22), f(x), f(DESK - 11.5)), 'none', stroke=dark(bc, 0.35), stroke_width=0.35))
    o.append(g([circle(cx - 19 + k * 3.2 + rnd.uniform(-0.4, 0.4), DESK - 14 - j * 3.2, 0.3, '#f6edd2') for k in range(5) for j in range(4)], opacity=0.9))
    # the small one, in flower
    sc = '#7d9a5e'
    o.append(body('M%s,%s C%s,%s %s,%s %s,%s Z' % (f(cx + 10), f(DESK - 12), f(cx + 10), f(DESK - 24), f(cx + 22), f(DESK - 24), f(cx + 22), f(DESK - 12)), sc))
    for k in range(5):
        a = -math.pi / 2 + (k - 2) * 0.5
        o.append(path('M%s,%s Q%s,%s %s,%s Q%s,%s %s,%s' % (f(cx + 16), f(DESK - 21), f(cx + 16 + math.cos(a - 0.3) * 4), f(DESK - 21 + math.sin(a - 0.3) * 4), f(cx + 16 + math.cos(a) * 5), f(DESK - 21 + math.sin(a) * 5),
                                                      f(cx + 16 + math.cos(a + 0.3) * 4), f(DESK - 21 + math.sin(a + 0.3) * 4), f(cx + 16), f(DESK - 21)), '#e0705a'))
    o.append(circle(cx + 16, DESK - 21.4, 1.1, '#f3c34e'))
    # the pot: terracotta, a rolled rim
    pot = 'M%s,%s L%s,%s L%s,%s L%s,%s Z' % (f(cx - 23), f(DESK - 12), f(cx + 23), f(DESK - 12), f(cx + 19), f(DESK - 1.2), f(cx - 19), f(DESK - 1.2))
    o.append(path(pot, D.lin([(0, '#d8875d'), (0.45, '#b86a45'), (1, '#7d4024')], 0, 0, 1, 0)))
    o.append(path(rrect(cx - 24.5, DESK - 15, 49, 4, 1), D.lin([(0, '#e19a70'), (0.5, '#c0724c'), (1, '#8a4a2b')], 0, 0, 1, 0)))
    o.append(rect(cx - 24, DESK - 14.8, 48, 0.5, '#ffffff', opacity=0.3))
    o.append(ellipse(cx, DESK - 14.6, 22, 0.8, '#3a2a1e'))
    return fin('desk-cacti', o, W, H, D, 251)

# ================================================================ prints, the wide frame: 214 x 168 at 5
def oak_frame(o, W, H):
    fr = 7
    fw, fh = W - 3, H - 4
    o.append(rect(3, 4, W - 3, H - 3, '#28180c', opacity=0.2, filter='url(#soft)'))
    o.append(rect(0, 0, fw, fh, P['oak']))
    for pts, c in ((((0, 0), (fw, 0), (fw - fr, fr), (fr, fr)), light(P['oak'], 0.18)), (((0, 0), (fr, fr), (fr, fh - fr), (0, fh)), light(P['oak'], 0.08)),
                   (((fw, 0), (fw, fh), (fw - fr, fh - fr), (fw - fr, fr)), dark(P['oak'], 0.12)), (((0, fh), (fr, fh - fr), (fw - fr, fh - fr), (fw, fh)), dark(P['oak'], 0.2))):
        o.append(poly(pts, c))
    o.append(rect(0, 0, fw, 1.4, P['oakl'])); o.append(rect(0, 0, 1.4, fh, P['oakl']))
    o.append(rect(fw - 1.4, 0, 1.4, fh, P['oakd'])); o.append(rect(0, fh - 1.4, fw, 1.4, P['oakd']))
    mx, my, mw, mh = fr, fr, fw - 2 * fr, fh - 2 * fr
    o.append(rect(mx, my, mw, mh, P['paper']))
    o.append(rect(mx, my, mw, 1.2, '#000', opacity=0.08)); o.append(rect(mx, my, 1.2, mh, '#000', opacity=0.06))
    return mx, my, mw, mh

def wide_print(name, art_fn, left, right, seed):
    W, H = 214, 168
    o = []
    mx, my, mw, mh = oak_frame(o, W, H)
    ix, iy, iw, ih = mx + 18, my + 16, mw - 36, mh - 40
    art = art_fn(ix, iy, iw, ih)
    o.append(g(art, filter='url(#pr)'))
    o.append(rect(mx + 15.4, my + 13.4, mw - 30.8, mh - 34.8, 'none', stroke='#ffffff', stroke_width=1.0, opacity=0.8))
    o.append(rect(mx + 16, my + 14, mw - 32, mh - 36, 'none', stroke='#000', stroke_width=0.4, opacity=0.18))
    o.append(poly([(mx + mw * 0.55, my), (mx + mw * 0.72, my), (mx + mw * 0.36, my + mh), (mx + mw * 0.19, my + mh)], '#ffffff', opacity=0.07))
    o.append(text(ix, iy + ih + 9, left, 3.2, P['soft'], 'Work Sans', 400, 0.06))
    o.append(text(ix + iw, iy + ih + 9, right, 3.0, P['soft'], 'Work Sans', 400, 0.06, 'end'))
    return render(name, g(o, filter='url(#gr)'), W, H, 5, OUT, defs=print_filter('pr', 1.3, 0.22, seed) + grain_filter('gr', 1.1, 0.025, seed + 1) + blur_filter('soft', 1.0))

def ruled_shell(a, b, c, d, n, col, w=0.22):
    # a hyperbolic paraboloid between two skew edges a-b and c-d (b-c the other pair):
    # straight lines joining points at equal steps along opposite edges, both families
    out = []
    for k in range(n + 1):
        t = k / n
        p = (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t); q = (d[0] + (c[0] - d[0]) * t, d[1] + (c[1] - d[1]) * t)
        out.append(line(p[0], p[1], q[0], q[1], col, w))
        p = (a[0] + (d[0] - a[0]) * t, a[1] + (d[1] - a[1]) * t); q = (b[0] + (c[0] - b[0]) * t, b[1] + (c[1] - b[1]) * t)
        out.append(line(p[0], p[1], q[0], q[1], col, w, opacity=0.7))
    return out

def pavilion():
    # the Philips Pavilion (Brussels, 1958): its tent of hyperbolic-paraboloid shells rising to
    # three peaks, each shell ruled in both families in a flat ink, overprinting, on a pale sky
    # with an ochre sun, visitors for scale at its foot
    def art(ix, iy, iw, ih):
        a = [rect(ix, iy, iw, ih, '#efe6d2'), rect(ix, iy, iw, ih * 0.82, D_sky)]
        a.append(circle(ix + iw * 0.84, iy + ih * 0.22, ih * 0.11, P['ochre'], opacity=0.9))
        gy = iy + ih * 0.84
        a.append(rect(ix, gy, iw, ih - (gy - iy), '#d9cdb2'))
        L, M1, M2, R = ix + iw * 0.06, ix + iw * 0.36, ix + iw * 0.6, ix + iw * 0.92
        p1, p2, p3 = (ix + iw * 0.3, iy + ih * 0.06), (ix + iw * 0.55, iy + ih * 0.3), (ix + iw * 0.8, iy + ih * 0.48)
        a += ruled_shell((L, gy), p1, (M1 + 6, gy - 10), (M1 - 18, gy), 26, P['slate'], 0.2)
        a += ruled_shell(p1, p2, (M2, gy), (M1 + 6, gy - 10), 24, P['accent'], 0.2)
        a += ruled_shell(p2, p3, (R, gy), (M2, gy), 20, '#2b4560', 0.2)
        a += ruled_shell((M1 - 18, gy), (M1 + 6, gy - 10), p2, (M2 - 10, gy), 14, P['ochre'], 0.18)
        a.append(line(ix, gy, ix + iw, gy, P['ink'], 0.4))
        for k, x in enumerate((ix + iw * 0.12, ix + iw * 0.15, ix + iw * 0.66, ix + iw * 0.7, ix + iw * 0.72)):
            a.append(circle(x, gy - 4.2, 0.7, P['ink'])); a.append(rect(x - 0.5, gy - 3.5, 1.0, 3.5, P['ink']))
        return a
    D_sky = '#dfe5e3'
    return wide_print('print-pavilion', art, 'Pavillon Philips', 'Bruxelles 1958', 301)

def polytope():
    # a Polytope: nets of steel cables hung in catenaries across a dark hall, with the flashes
    # of light along them, after the Polytope de Montréal (1967)
    def art(ix, iy, iw, ih):
        rnd = random.Random(67)
        a = [rect(ix, iy, iw, ih, '#24323f')]
        for net, (col, n) in enumerate(((P['paper'], 18), ('#d5b465', 14), ('#e58e6c', 12))):
            for k in range(n):
                y0 = iy + ih * (0.08 + 0.05 * net) + k * 1.2
                x0, x1 = ix + 4 + net * 10, ix + iw - 4 - net * 8
                sag = ih * (0.25 + 0.04 * k + 0.08 * net)
                a.append(path('M%s,%s Q%s,%s %s,%s' % (f(x0), f(y0 + k * 2.8), f((x0 + x1) / 2), f(y0 + sag), f(x1), f(y0 + k * 1.6)), 'none', stroke=col, stroke_width=0.22, opacity=0.75))
        for k in range(70):
            x, y = ix + rnd.uniform(6, iw - 6), iy + rnd.uniform(ih * 0.15, ih * 0.85)
            a.append(circle(x, y, rnd.uniform(0.5, 1.3), '#fff6dc', opacity=rnd.uniform(0.5, 1)))
        return a
    return wide_print('print-polytope', polytope_art := art, 'Polytope', 'Montréal 1967', 311)

# ================================================================ prints, the narrow frame: 120 x 150 at 6
def black_frame(D, o, W, H):
    o.append(rect(2.4, 3.2, W - 2, H - 2, '#000', opacity=0.3, filter=D.blur(1.4)))
    o.append(rect(0, 0, W - 2, H - 2, D.lin([(0, '#3a3836'), (0.5, '#1b1a18'), (1, '#0d0c0b')], 0, 0, 1, 1)))
    o.append(rect(0.4, 0.4, W - 2.8, 0.5, '#ffffff', opacity=0.25))
    return 3, 3, W - 8, H - 8

def narrow_print(name, art_fn, seed, ground=('#f4ead2', '#e6d6b2')):
    W, H = 120, 150
    D = Defs(); o = []
    fx, fy, fw, fh = black_frame(D, o, W, H)
    o.append(rect(fx, fy, fw, fh, D.lin([(0, ground[0]), (1, ground[1])], 0, 0, 1, 1)))
    o.append(g(art_fn(D, fx, fy, fw, fh), clip_path=D.clip(rect(fx, fy, fw, fh, '#000'))))
    o.append(rect(fx, fy, fw, fh, D.lin([(0, '#ffffff', 0), (0.5, '#ffffff', 0), (1, '#6b5a3a', 0.12)], 0, 0, 1, 1)))
    o.append(rect(fx, fy, fw, fh, 'none', stroke='#000', stroke_width=0.5, opacity=0.35))
    o.append(poly([(fx + fw * 0.58, fy), (fx + fw * 0.72, fy), (fx + fw * 0.34, fy + fh), (fx + fw * 0.2, fy + fh)], '#ffffff', opacity=0.07))
    defs = D.out() + print_filter('pr', 1.6, 0.18, seed) + grain_filter('gr', 1.1, 0.05, seed + 1)
    return render(name, g(g(o, filter='url(#gr)'), filter='url(#pr)'), W, H, 6, OUT, defs=defs)

def torn(rnd, x, y, w, h, jit=0.6):
    pts = []
    cs = [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]
    for i in range(4):
        (x0, y0), (x1, y1) = cs[i], cs[(i + 1) % 4]
        n = max(3, int(math.hypot(x1 - x0, y1 - y0) / 2.2))
        for k in range(n):
            t = k / n
            pts.append((x0 + (x1 - x0) * t + rnd.uniform(-jit, jit), y0 + (y1 - y0) * t + rnd.uniform(-jit, jit)))
    return pts

def arp():
    # squares arranged according to the laws of chance, after Arp's collages of 1916-17:
    # torn papers, black, grey and blue, near square to a grey-blue sheet laid on the mount
    def art(D, fx, fy, fw, fh):
        rnd = random.Random(1917)
        a = [rect(fx + 10, fy + 12, fw - 20, fh - 26, '#c9cdc4')]
        for k in range(13):
            s = rnd.uniform(9, 20); w = s * (1.4 if rnd.random() < 0.3 else 1)
            x = fx + 12 + rnd.uniform(0, fw - 24 - w); y = fy + 14 + rnd.uniform(0, fh - 30 - s)
            c = rnd.choice(['#1b1a18', '#1b1a18', '#2b4560', '#7f8178', '#efe9d6', '#1b1a18'])
            a.append(poly(torn(rnd, x, y, w, s), c, transform='rotate(%s %s %s)' % (f(rnd.uniform(-4, 4)), f(x + w / 2), f(y + s / 2))))
        a.append(text(fx + fw / 2, fy + fh - 5, 'H. ARP 1917', 3.0, '#5d5851', 'Work Sans', 600, 0.3, 'middle'))
        return a
    return narrow_print('print-arp', art, 321)

def taeuber():
    # a vertical-horizontal composition after Sophie Taeuber-Arp: a grid of rectangles in
    # flat colour, a few circles over it, on a cream sheet
    def art(D, fx, fy, fw, fh):
        rnd = random.Random(1918)
        a = []
        x0, y0, w, h = fx + 9, fy + 10, fw - 18, fh - 26
        cols, rows = 5, 7
        cw, rh = w / cols, h / rows
        pal = ['#c23a26', '#2b4560', '#c99a2e', '#1b1a18', '#efe6d2', '#efe6d2', '#7d8a78', '#efe6d2']
        for r in range(rows):
            for c in range(cols):
                a.append(rect(x0 + c * cw + 0.6, y0 + r * rh + 0.6, cw - 1.2, rh - 1.2, rnd.choice(pal)))
        for k in range(4):
            c = rnd.randrange(cols); r = rnd.randrange(rows)
            a.append(circle(x0 + (c + 0.5) * cw, y0 + (r + 0.5) * rh, min(cw, rh) * 0.36, rnd.choice(['#efe6d2', '#1b1a18', '#c23a26'])))
        a.append(rect(x0, y0, w, h, 'none', stroke='#1b1a18', stroke_width=0.6))
        a.append(text(fx + fw / 2, fy + fh - 5, 'S. TAEUBER 1918', 3.0, '#5d5851', 'Work Sans', 600, 0.3, 'middle'))
        return a
    return narrow_print('print-taeuber', art, 331)

# ================================================================ mugs: 32 x 30
def mug_shape(D, o, body_fill, rim='#3a2416', handle=True):
    o.append(ellipse(14, 29.6, 10, 0.8, '#000', opacity=0.3, filter=D.blur(0.5)))
    body = 'M4,4 L22,4 L21.4,28 C21.4,29 20,30 18,30 L8,30 C6,30 4.6,29 4.6,28 Z'
    hd = 'M21.6,9 C29.5,8 29.5,22.5 21.2,21.4 L21.3,18.6 C26.4,19.2 26.4,11 21.6,11.8 Z'
    if handle:
        o.append(path(hd, body_fill)); o.append(path(hd, 'none', stroke='#00000033', stroke_width=0.25))
    o.append(path(body, body_fill))
    return body

def mug_sage():
    # a Heath-style cylinder in a sage glaze, the clay showing brown at the rim
    W, H = 32, 30
    D = Defs(); o = []
    sage = D.lin([(0, '#a5b29d'), (0.45, '#7d8a78'), (1, '#4f5a4b')], 0, 0, 1, 0)
    body = mug_shape(D, o, sage)
    o.append(rect(4, 4, 18, 1.1, '#7a5a3d'))
    o.append(path('M6.4,7 C6.6,15 7,23 7.6,28', 'none', stroke='#ffffff', stroke_width=0.7, opacity=0.3, stroke_linecap='round'))
    o.append(ellipse(13, 4.1, 9, 0.9, '#2a1a10'))
    o.append(path(body, 'none', stroke='#3d4639', stroke_width=0.22, opacity=0.8))
    return fin('mug-sage', o, W, H, D, 341)

def mug_striped():
    # a cream mug banded in ochre and slate, after the Arabia stripes of the fifties
    W, H = 32, 30
    D = Defs(); o = []
    cream = D.lin([(0, '#f9f4e8'), (0.5, '#ece4d2'), (1, '#c9bfa9')], 0, 0, 1, 0)
    body = mug_shape(D, o, cream)
    cp = D.clip(path(body, '#000'))
    o.append(g([rect(0, 12, 26, 2.4, '#c99a2e'), rect(0, 15.4, 26, 1.0, '#49555a'), rect(0, 17.4, 26, 2.4, '#c99a2e'), rect(0, 24, 26, 0.8, '#49555a'),
                rect(0, 0, 26, 30, D.lin([(0, '#ffffff', 0.25), (0.35, '#ffffff', 0), (1, '#000000', 0.25)], 0, 0, 1, 0))], clip_path=cp))
    o.append(ellipse(13, 4.1, 9, 0.9, '#3a2416'))
    o.append(ellipse(13, 4.1, 9, 0.9, 'none', stroke='#ffffff', stroke_width=0.35, opacity=0.8))
    o.append(path(body, 'none', stroke='#8f8673', stroke_width=0.22, opacity=0.8))
    return fin('mug-striped', o, W, H, D, 351)

def cup():
    # a white cup on its saucer, a band of blue at the lip, after the period's hotel china
    W, H = 32, 30
    D = Defs(); o = []
    o.append(ellipse(15, 29.4, 13, 0.9, '#000', opacity=0.3, filter=D.blur(0.5)))
    white = D.lin([(0, '#fdfbf6'), (0.55, '#ebe6db'), (1, '#c7c0b1')], 0, 0, 1, 0)
    o.append(path('M2,26.4 C2,29.2 28,29.2 28,26.4 C28,25.4 2,25.4 2,26.4 Z', white))
    o.append(path('M2,26.4 C2,29.2 28,29.2 28,26.4', 'none', stroke='#9d9585', stroke_width=0.25))
    o.append(path('M22.6,14 C28.6,13.4 28.4,22.4 21.4,21.6 L21.6,19.6 C25.6,20 25.8,15.6 22.4,16 Z', white))
    body = 'M7,12 L24,12 C24,20 22,25.6 15.5,25.8 C9,25.6 7,20 7,12 Z'
    o.append(path(body, white))
    cp = D.clip(path(body, '#000'))
    o.append(g([rect(5, 12.8, 22, 1.5, '#2b4560'), rect(5, 15, 22, 0.4, '#2b4560')], clip_path=cp))
    o.append(ellipse(15.5, 12, 8.5, 1.0, '#4a2c18'))
    o.append(ellipse(15.5, 12, 8.5, 1.0, 'none', stroke='#ffffff', stroke_width=0.4, opacity=0.9))
    o.append(path(body, 'none', stroke='#9d9585', stroke_width=0.22))
    return fin('mug-cup', o, W, H, D, 361)

def mug_enamel():
    # an enamel camping mug: white speckled with grey, its rim and handle rolled in blue
    W, H = 32, 30
    D = Defs(); o = []
    rnd = random.Random(7)
    white = D.lin([(0, '#fbfaf6'), (0.5, '#ebe8e0'), (1, '#c4c0b6')], 0, 0, 1, 0)
    body = mug_shape(D, o, white, handle=False)
    o.append(path('M21.6,9 C29.5,8 29.5,22.5 21.2,21.4', 'none', stroke='#3f74ad', stroke_width=1.6, stroke_linecap='round'))
    cp = D.clip(path(body, '#000'))
    o.append(g([circle(rnd.uniform(4, 22), rnd.uniform(6, 29), rnd.uniform(0.15, 0.35), '#5d6670', opacity=rnd.uniform(0.3, 0.7)) for k in range(70)], clip_path=cp))
    o.append(g([rect(0, 26.6, 26, 4, '#3f74ad')], clip_path=cp))
    o.append(path('M4,4 L22,4', 'none', stroke='#3f74ad', stroke_width=1.6, stroke_linecap='round'))
    o.append(ellipse(13, 4.1, 8.4, 0.8, '#3a2416'))
    o.append(path(body, 'none', stroke='#8f8a80', stroke_width=0.22, opacity=0.8))
    return fin('mug-enamel', o, W, H, D, 371)

def mug_sieve():
    # a cream mug printed with a sieve: two rows of points round it, the members in terracotta
    W, H = 32, 30
    D = Defs(); o = []
    cream = D.lin([(0, '#f9f4e8'), (0.5, '#ece4d2'), (1, '#c9bfa9')], 0, 0, 1, 0)
    body = mug_shape(D, o, cream)
    cp = D.clip(path(body, '#000'))
    dots = []
    for r, (m, res) in enumerate(((3, 0), (4, 1))):
        for k in range(8):
            on = k % m == res
            dots.append(circle(5.6 + k * 2.2, 13 + r * 4, 0.75 if on else 0.3, '#b5462b' if on else '#5d5851'))
    dots.append(rect(4.6, 21.4, 17, 0.35, '#1e1d1b'))
    for k in range(8):
        if k % 3 == 0 or k % 4 == 1: dots.append(rect(5.1 + k * 2.2, 22.3, 1.0, 1.0, '#1e1d1b'))
    o.append(g(dots + [rect(0, 0, 26, 30, D.lin([(0, '#ffffff', 0.2), (0.35, '#ffffff', 0), (1, '#000000', 0.22)], 0, 0, 1, 0))], clip_path=cp))
    o.append(ellipse(13, 4.1, 9, 0.9, '#3a2416'))
    o.append(ellipse(13, 4.1, 9, 0.9, 'none', stroke='#ffffff', stroke_width=0.35, opacity=0.8))
    o.append(path(body, 'none', stroke='#8f8673', stroke_width=0.22, opacity=0.8))
    return fin('mug-sieve', o, W, H, D, 381)

def mug_black():
    # a matte black cylinder with one white ring, after the period's Scandinavian stoneware
    W, H = 32, 30
    D = Defs(); o = []
    blk = D.lin([(0, '#55524d'), (0.4, '#2a2826'), (1, '#121110')], 0, 0, 1, 0)
    body = mug_shape(D, o, blk)
    cp = D.clip(path(body, '#000'))
    o.append(g([rect(0, 9.5, 26, 1.1, '#efe9dc')], clip_path=cp))
    o.append(path('M6.4,12 C6.6,18 7,24 7.6,28', 'none', stroke='#ffffff', stroke_width=0.6, opacity=0.18, stroke_linecap='round'))
    o.append(ellipse(13, 4.1, 9, 0.9, '#1a120c'))
    o.append(ellipse(13, 4.1, 9, 0.9, 'none', stroke='#ffffff', stroke_width=0.3, opacity=0.5))
    return fin('mug-black', o, W, H, D, 391)

# ================================================================ lamps: 70 x 106, the desk at 106
def brassg(D): return D.lin([(0, '#f3dfa0'), (0.35, '#c9a14e'), (0.6, '#8d6a2a'), (1, '#d8b867')], 0, 0, 1, 1)

def lamp_dome():
    # a dome lamp after the flared lamps of the late sixties: a white trumpet rising to a
    # wide white dome, lit from within, its rim glowing where the light comes out
    W, H = 70, 106
    D = Defs(); o = []
    cx = 28
    o.append(ellipse(cx, 105.4, 15, 1.2, '#000', opacity=0.35, filter=D.blur(0.7)))
    white = D.lin([(0, '#fdfcf8'), (0.5, '#ebe7dd'), (1, '#b9b3a6')], 0, 0, 1, 0)
    o.append(path('M%s,48 C%s,70 %s,96 %s,105.6 L%s,105.6 C%s,96 %s,70 %s,48 Z' % (f(cx - 1.4), f(cx - 1.6), f(cx - 4), f(cx - 13), f(cx + 13), f(cx + 4), f(cx + 1.6), f(cx + 1.4)), white))
    o.append(path('M%s,52 C%s,72 %s,96 %s,104.6' % (f(cx - 0.8), f(cx - 1.2), f(cx - 3.4), f(cx - 10)), 'none', stroke='#ffffff', stroke_width=0.5, opacity=0.7))
    o.append(ellipse(cx, 105.4, 13, 0.6, '#9f998c'))
    # the light falling on the trumpet from the dome above
    o.append(path('M%s,48 L%s,48 L%s,62 L%s,62 Z' % (f(cx - 1.4), f(cx + 1.4), f(cx + 1.6), f(cx - 1.6)), '#fff1c8', opacity=0.6))
    dome = 'M%s,48 C%s,30 %s,22 %s,22 C%s,22 %s,30 %s,48 Z' % (f(cx - 24), f(cx - 22), f(cx - 10), f(cx), f(cx + 10), f(cx + 22), f(cx + 24))
    o.append(path(dome, D.lin([(0, '#ffffff'), (0.55, '#f1ede3'), (1, '#c8c1b2')], 0, 0, 1, 0)))
    o.append(path('M%s,44 C%s,30 %s,25 %s,24.4' % (f(cx - 20), f(cx - 18), f(cx - 10), f(cx - 2)), 'none', stroke='#ffffff', stroke_width=0.9, opacity=0.9))
    o.append(ellipse(cx, 48, 24, 2.4, D.rad([(0, '#fffbe8'), (0.6, '#ffe7a8'), (1, '#f4c86a')])))
    o.append(ellipse(cx, 48.6, 12, 1.0, '#ffffff', opacity=0.9))
    return fin('lamp-dome', o, W, H, D, 451)

def lamp_angle():
    # a balanced-arm lamp in terracotta enamel: a stepped round base, two arms held by
    # springs, and a conical shade tipped down toward the desk
    W, H = 70, 106
    D = Defs(); o = []
    TC = '#b5462b'
    enamel = D.lin([(0, light(TC, 0.3)), (0.4, TC), (1, dark(TC, 0.4))], 0, 0, 1, 0)
    o.append(ellipse(16, 105.4, 13, 1.2, '#000', opacity=0.35, filter=D.blur(0.7)))
    o.append(path('M4,106 C4.4,103 8,102 16,102 C24,102 27.6,103 28,106 Z', enamel))
    o.append(path('M8,102.4 C8.4,100.4 11,99.6 16,99.6 C21,99.6 23.6,100.4 24,102.4 Z', D.lin([(0, light(TC, 0.25)), (1, dark(TC, 0.3))], 0, 0, 1, 0)))
    o.append(path(rrect(14.4, 96.8, 3.2, 3.2, 0.6), '#2a2826'))
    # the lower arm: two parallel rods rising from the base to the elbow, springs beside them
    lo = [(16, 98), (26, 56)]; hi = [(26, 56), (50, 30)]
    for (x0, y0), (x1, y1) in (lo, hi):
        for d in (-0.9, 0.9):
            o.append(line(x0 + d, y0, x1 + d, y1, '#1e1d1b', 0.6))
        o.append(line(x0 + 0.5, y0, x1 + 0.5, y1, '#ffffff', 0.15, opacity=0.4))
    # the springs: tight coils alongside each arm, from near its foot to its middle
    for (x0, y0), (x1, y1) in (lo, hi):
        ax, ay = x1 - x0, y1 - y0; L = math.hypot(ax, ay); ux, uy = ax / L, ay / L; nx, ny = -uy, ux
        sx0, sy0 = x0 + ux * L * 0.12 + nx * 2.2, y0 + uy * L * 0.12 + ny * 2.2
        n = 22; ln = L * 0.45
        pts = ' '.join('%s%s,%s' % ('M' if k == 0 else 'L', f(sx0 + ux * ln * k / n + nx * (0.7 if k % 2 else -0.7)), f(sy0 + uy * ln * k / n + ny * (0.7 if k % 2 else -0.7))) for k in range(n + 1))
        o.append(path(pts, 'none', stroke='#9a968d', stroke_width=0.3))
        o.append(line(x0 + nx * 1.2, y0 + ny * 1.2, sx0, sy0, '#5f5c56', 0.25))
    for kx, ky in ((26, 56), (16, 98), (50, 30)):
        o.append(circle(kx, ky, 1.6, '#2a2826')); o.append(circle(kx, ky, 0.6, '#8e8a82'))
    # the shade: a cone tipped toward the desk, terracotta outside, its throat lit
    sh = [path('M-3,-5 L3,-5 L11,6 L-11,6 Z', enamel), path(rrect(-3.4, -7.4, 6.8, 3, 1.2), D.lin([(0, light(TC, 0.2)), (1, dark(TC, 0.3))], 0, 0, 1, 0)),
          ellipse(0, 6, 11, 2.2, D.lin([(0, '#fff6dc'), (1, '#f0d9a0')])), ellipse(0, 6.4, 5, 1.0, '#ffffff', opacity=0.9),
          path('M-2,-4.4 L-9,5', 'none', stroke='#ffffff', stroke_width=0.5, opacity=0.4)]
    o.append(g(sh, transform='translate(53 34) rotate(-28)'))
    return fin('lamp-angle', o, W, H, D, 461)

def lamp_ceramic():
    # a table lamp of the fifties: a bellied ochre-glazed base on a teak foot, a brass
    # stem, and a drum shade of linen lit from within
    W, H = 70, 106
    D = Defs(); o = []
    cx = 26
    o.append(ellipse(cx, 105.4, 15, 1.2, '#000', opacity=0.35, filter=D.blur(0.7)))
    o.append(path(rrect(cx - 11, 102.4, 22, 3.6, 1.0), D.lin([(0, '#c99a6b'), (0.4, '#9a6a43'), (1, '#6a4428')], 0, 0, 1, 0)))
    body = 'M%s,102.4 C%s,96 %s,86 %s,78 C%s,72 %s,68 %s,66 L%s,66 C%s,68 %s,72 %s,78 C%s,86 %s,96 %s,102.4 Z' % (
        f(cx - 7), f(cx - 13), f(cx - 13), f(cx - 9), f(cx - 6), f(cx - 3), f(cx - 2.6), f(cx + 2.6), f(cx + 3), f(cx + 6), f(cx + 9), f(cx + 13), f(cx + 13), f(cx + 7))
    o.append(path(body, D.lin([(0, '#e3b85c'), (0.35, '#c99a2e'), (1, '#7d5c16')], 0, 0, 1, 0)))
    o.append(path('M%s,98 C%s,92 %s,84 %s,78' % (f(cx - 8), f(cx - 10.6), f(cx - 10.4), f(cx - 7)), 'none', stroke='#ffffff', stroke_width=0.9, opacity=0.45, stroke_linecap='round'))
    for k in range(3):
        y = 84 + k * 4
        o.append(path('M%s,%s Q%s,%s %s,%s' % (f(cx - 11.6 + k), f(y), f(cx), f(y + 1.6), f(cx + 11.6 - k), f(y)), 'none', stroke='#7d5c16', stroke_width=0.35, opacity=0.6))
    o.append(path(rrect(cx - 0.9, 46, 1.8, 20, 0.6), brassg(D)))
    # the drum shade: linen, its weave in faint lines, glowing; its lit rims
    shade = rrect(cx - 19, 22, 38, 25, 0.8)
    o.append(path(shade, D.lin([(0, '#f1e4c4'), (0.5, '#fbf1d6'), (1, '#dcc9a0')], 0, 0, 1, 0)))
    cp = D.clip(path(shade, '#000'))
    weave = [rect(cx - 19, 22 + k * 0.9, 38, 0.18, '#b9a57c', opacity=0.25) for k in range(28)]
    weave.append(ellipse(cx, 36, 10, 9, '#fff6dc', opacity=0.55, filter=D.blur(3)))
    o.append(g(weave, clip_path=cp))
    o.append(rect(cx - 19, 46, 38, 1.0, '#fff1c8'))
    o.append(rect(cx - 19, 22, 38, 0.8, '#d9c497'))
    return fin('lamp-ceramic', o, W, H, D, 471)

if __name__ == '__main__':
    for w in (sys.argv[1:] or ['snake', 'palm', 'fern', 'rubber', 'jade', 'cacti', 'pavilion', 'polytope', 'arp', 'taeuber', 'mug_sage', 'mug_striped', 'cup']):
        globals()[w]()
