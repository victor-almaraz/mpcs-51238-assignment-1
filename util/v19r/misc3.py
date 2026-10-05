# The miscellanea's drawings, a third pass for v21: depth (ink layered and fading with
# distance, cast shadows, shaded forms, washes of colour behind the figures), flow (strokes
# that taper like a pen at both ends and swell through the middle, curves where the subject
# moves), and grain (the paper's tooth and fibres, and a faint wobble of ink on paper), all
# in the SVG files themselves: the texture comes from small SVG filters.
import math, random
from misc2 import Sheet as Base, f, P, line, path, circle, rect, arrow, GRAPH, BLUE, RED, SEPIA, GREEN, PAPER, VELLUM, MANU

class Sheet(Base):
    def __init__(self, w, h, title, seed=1):
        super().__init__(w, h, title)
        self.seed = seed
        # paper: a fine tooth, and long fibres; ink: a faint wobble, as of a pen on paper
        self.defs.append(('<filter id="tooth" x="0" y="0" width="100%%" height="100%%"><feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves="3" seed="%d"/>'
                          '<feColorMatrix values="0 0 0 0 0.33  0 0 0 0 0.27  0 0 0 0 0.18  0 0 0 -1.1 0.62"/></filter>') % seed)
        self.defs.append(('<filter id="fibre" x="0" y="0" width="100%%" height="100%%"><feTurbulence type="fractalNoise" baseFrequency="0.012 0.35" numOctaves="2" seed="%d"/>'
                          '<feColorMatrix values="0 0 0 0 0.45  0 0 0 0 0.38  0 0 0 0 0.26  0 0 0 -1.6 0.95"/></filter>') % (seed + 1))
        self.defs.append(('<filter id="ink" x="-2%%" y="-2%%" width="104%%" height="104%%"><feTurbulence type="fractalNoise" baseFrequency="0.06" numOctaves="2" seed="%d" result="t"/>'
                          '<feDisplacementMap in="SourceGraphic" in2="t" scale="1.3" xChannelSelector="R" yChannelSelector="G"/></filter>') % (seed + 2))
        self.blurs = {}
    def blur(self, sd):
        if sd not in self.blurs:
            i = self.id('b'); self.blurs[sd] = i
            self.defs.append('<filter id="%s" x="-30%%" y="-30%%" width="160%%" height="160%%"><feGaussianBlur stdDeviation="%s"/></filter>' % (i, f(sd)))
        return 'url(#%s)' % self.blurs[sd]
    def rad(self, stops, cx=0.5, cy=0.5, r=0.5):
        i = self.id('r')
        self.defs.append('<radialGradient id="%s" cx="%s" cy="%s" r="%s">%s</radialGradient>' % (i, f(cx), f(cy), f(r), ''.join('<stop offset="%s" stop-color="%s" stop-opacity="%s"/>' % (f(o), c, f(a)) for o, c, a in stops)))
        return 'url(#%s)' % i
    def grain(self, amount=1.0):
        """the paper's tooth and fibres over everything, multiplied in"""
        self.add('<rect width="%s" height="%s" filter="url(#tooth)" opacity="%s" style="mix-blend-mode:multiply"/>' % (f(self.w), f(self.h), f(0.5 * amount)))
        self.add('<rect width="%s" height="%s" filter="url(#fibre)" opacity="%s" style="mix-blend-mode:multiply"/>' % (f(self.w), f(self.h), f(0.16 * amount)))
        # the sheet's edges darkened a little, as old paper is
        self.add('<rect width="%s" height="%s" fill="%s"/>' % (f(self.w), f(self.h), self.rad([(0, '#000', 0), (0.7, '#000', 0), (1, '#5a4320', 0.18)], 0.5, 0.5, 0.75)))
    def ink(self, *items, opacity=1):
        self.add('<g filter="url(#ink)"%s>%s</g>' % ((' opacity="%s"' % f(opacity)) if opacity < 1 else '', ''.join(items)))

def taper(pts, wmax, w0=0.15, w1=0.15, swell=0.6):
    """a pen stroke along pts: thin at both ends, swelling to wmax through the middle"""
    L, R = [], []
    n = len(pts)
    for i, (x, y) in enumerate(pts):
        t = i / (n - 1)
        w = w0 + (w1 - w0) * t + (wmax - (w0 + (w1 - w0) * t)) * (math.sin(math.pi * t) ** swell)
        xa, ya = pts[max(0, i - 1)]; xb, yb = pts[min(n - 1, i + 1)]
        nx, ny = -(yb - ya), xb - xa
        nl = math.hypot(nx, ny) or 1
        L.append((x + nx / nl * w / 2, y + ny / nl * w / 2)); R.append((x - nx / nl * w / 2, y - ny / nl * w / 2))
    return P(L + R[::-1]) + 'Z'

def seg(x0, y0, x1, y1, n=8, bow=0.0):
    """points along a line, bowed a little to one side"""
    out = []
    for k in range(n + 1):
        t = k / n
        b = bow * math.sin(math.pi * t)
        nx, ny = -(y1 - y0), x1 - x0; nl = math.hypot(nx, ny) or 1
        out.append((x0 + (x1 - x0) * t + nx / nl * b, y0 + (y1 - y0) * t + ny / nl * b))
    return out

def wash(S, d, color, op=0.12, sd=6):
    S.add(path(d, fill=color, opacity=f(op), filter=S.blur(sd)))

# ---------------------------------------------------------------- A: Metastaseis
def a1():
    S = Sheet(560, 360, 'Graph of straight string glissando lines whose bundles form curved envelopes, bars 309 to 314', 11)
    S.paper(PAPER)
    x0, x1, y0, y1 = 56, 538, 22, 292
    S.add(rect(x0, y0, x1 - x0, y1 - y0, S.grid(4, 20, '#d4e2ee', '#afc9df', 0.3, 0.6, x0, y0)))
    def py(m): return y1 - (m - 31) * (y1 - y0) / (96 - 31)
    def bx(b): return x0 + (b - 309) * (x1 - x0) / 5
    sections = [('vn I', 12, RED, (68, 92), (57, 84), 309.4, 313.6), ('vn II', 12, BLUE, (60, 84), (80, 58), 309.6, 313.8),
                ('va', 8, GRAPH, (54, 72), (70, 50), 309.8, 314.0), ('vc', 8, SEPIA, (40, 62), (60, 38), 310.0, 314.0), ('cb', 6, GREEN, (32, 46), (44, 33), 310.2, 314.0)]
    rnd = random.Random(3)
    # washes of each section's colour behind its surface, the deeper sections fainter
    for k, (name, n, c, (pa, pb), (qa, qb), t0, t1) in enumerate(sections):
        quad = P([(bx(t0), py(pa)), (bx(t0), py(pb)), (bx(t1), py(qb)), (bx(t1), py(qa))]) + 'Z'
        wash(S, quad, c, 0.07, 8)
    for m in range(36, 97, 12):
        S.add(line(x0 - 4, py(m), x0, py(m), GRAPH, 0.6))
        S.text(x0 - 7, py(m) + 3, 'C%d' % (m // 12 - 1), 9, GRAPH, anchor='end')
    for b in range(309, 315):
        S.add(line(bx(b), y1, bx(b), y1 + 5, GRAPH, 0.7))
        S.text(bx(b), y1 + 15, str(b), 9.5, GRAPH, anchor='middle')
    S.add(line(x0, y0, x0, y1, GRAPH, 0.9), line(x0, y1, x1, y1, GRAPH, 0.9))
    S.text(18, (y0 + y1) / 2, 'pitch', 10, GRAPH, rot=-90, anchor='middle')
    # the glissandi, in pen: each part a tapered straight stroke, its note heads at either end
    for depth, (name, n, c, (pa, pb), (qa, qb), t0, t1) in enumerate(reversed(sections)):
        d, heads = '', ''
        for k in range(n):
            u = k / (n - 1)
            p0, p1 = pa + (pb - pa) * u, qa + (qb - qa) * u
            a0, a1 = t0 + rnd.uniform(-0.05, 0.05), t1 - rnd.uniform(0, 0.08)
            d += taper(seg(bx(a0), py(p0), bx(a1), py(p1), 10), 1.15, 0.35, 0.35, 0.4)
            heads += 'M%s %sa1.6 1.25 -20 1 0 0.01 0M%s %sa1.6 1.25 -20 1 0 0.01 0' % (f(bx(a0) - 1.6), f(py(p0)), f(bx(a1) - 1.6), f(py(p1)))
        S.ink(path(d, fill=c, opacity='0.85'), path(heads, stroke=c, w=2.4, stroke_linecap='round'), opacity=0.75 + 0.05 * depth)
    for k, (name, n, c, *_) in enumerate(sections):
        lx = x0 + 110 + k * 80
        S.add(path(taper(seg(lx, 344, lx + 16, 344, 6), 1.6), fill=c))
        S.text(lx + 20, 347.5, '%s %d' % (name, n), 9, GRAPH)
    S.text(x0, 347.5, 'bars (time)', 9, GRAPH); S.add(arrow(x0 + 88, 344.5, 20))
    S.text(x0 + 8, y0 + 16, '46 strings, a part each: straight lines, curved surfaces', 13, GRAPH, fam='Caveat', opacity=0.85)
    S.grain()
    S.save('a1')

# ---------------------------------------------------------------- B: Philips Pavilion
def a2():
    S = Sheet(420, 280, 'Postcard drawing of a tent-like pavilion built from ruled, saddle-shaped concrete shells', 21)
    S.add(rect(0, 0, 420, 280, '#f4eee0'))
    ix, iy, iw, ih = 12, 12, 396, 210
    cp = S.id('c'); S.defs.append('<clipPath id="%s"><rect x="%s" y="%s" width="%s" height="%s"/></clipPath>' % (cp, ix, iy, iw, ih))
    sc = []
    sc.append(rect(ix, iy, iw, ih, S.lin([(0, '#a9c4d6'), (0.55, '#dfe8e6'), (1, '#f1e9d6')])))
    rnd = random.Random(58)
    for k in range(7):   # soft clouds
        cx, cy = ix + rnd.uniform(0, iw), iy + rnd.uniform(10, 70)
        sc.append('<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="#ffffff" opacity="0.5" filter="%s"/>' % (f(cx), f(cy), f(rnd.uniform(30, 60)), f(rnd.uniform(5, 10)), S.blur(5)))
    gy = iy + ih * 0.8
    # a line of trees in the distance, paler with the air between
    trees = 'M%s %s' % (f(ix), f(gy))
    x = ix
    while x < ix + iw:
        w = rnd.uniform(8, 18); hgt = rnd.uniform(10, 24)
        trees += 'Q%s %s %s %s' % (f(x + w / 2), f(gy - hgt * 1.6), f(x + w), f(gy)); x += w
    trees += 'L%s %sZ' % (f(ix + iw), f(gy))
    sc.append(path(trees, fill='#8fa58f', opacity='0.55'))
    sc.append(rect(ix, gy, iw, iy + ih - gy, S.lin([(0, '#cdbf9c'), (1, '#a8966f')])))
    # three hyperbolic paraboloid shells: shaded from the light on the left to shadow on the
    # right, their rulings in both families fading where the surface turns from us
    def shell(a, b, c, d, n, light, dark):
        g_ = S.lin([(0, light), (1, dark)], 1, 0.4)
        out = [path(P([a, b, c, d]) + 'Z', fill=g_)]
        L = lambda p, q, t: (p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t)
        d1_, d2_ = '', ''
        for i in range(n + 1):
            t = i / n
            p, q = L(a, b, t), L(d, c, t); d1_ += 'M%s %sL%s %s' % (f(p[0]), f(p[1]), f(q[0]), f(q[1]))
            p, q = L(a, d, t), L(b, c, t); d2_ += 'M%s %sL%s %s' % (f(p[0]), f(p[1]), f(q[0]), f(q[1]))
        out += [path(d1_, stroke='#4f4a40', w=0.4, opacity='0.55'), path(d2_, stroke='#4f4a40', w=0.35, opacity='0.35'),
                path(P([a, b, c, d]) + 'Z', stroke='#36322b', w=0.9, stroke_linejoin='round')]
        return out
    A, B, C, D = (ix + 70, gy), (ix + 150, iy + 70), (ix + 200, gy - 8), (ix + 160, gy)
    E, F = (ix + 268, iy + 18), (ix + 300, gy - 4)
    G, H = (ix + 352, gy), (ix + 320, gy)
    # their shadow, long, across the ground to the right
    sc.append(path(P([(ix + 70, gy), (ix + 352, gy), (ix + 404, gy + 20), (ix + 150, gy + 22)]) + 'Z', fill='#4a3b22', opacity='0.32', filter=S.blur(3)))
    sc += shell(A, B, C, D, 22, '#f4f1ea', '#c9c2b2')
    sc += shell(B, E, F, C, 26, '#fbf9f4', '#d5cebd')
    sc += shell(E, G, H, F, 18, '#d4ccbb', '#a79e8a')
    for px in (ix + 52, ix + 60, ix + 210, ix + 216, ix + 362):
        sc.append(path('M%s %sl-2 9h4z' % (f(px), f(gy + 0.5)), fill='#2f2c27'))
        sc.append(circle(px, gy - 1.2, 1.6, '#2f2c27'))
        sc.append('<ellipse cx="%s" cy="%s" rx="4" ry="0.8" fill="#2f2c27" opacity="0.3"/>' % (f(px + 3), f(gy + 9.5)))
    # the print's own grain and a little fading at its corners
    sc.append(rect(ix, iy, iw, ih, S.rad([(0, '#000', 0), (0.65, '#000', 0), (1, '#5a4320', 0.25)], 0.5, 0.5, 0.75)))
    S.add('<g clip-path="url(#%s)">%s</g>' % (cp, ''.join(sc)))
    S.add(rect(ix, iy, iw, ih, 'none', stroke='#ffffff', stroke_width='3'))
    S.text(ix + 4, 252, 'Bruxelles · Expo 58', 26, '#2c3e5a', fam='Caveat', wt=700)
    S.text(ix + 6, 270, 'LE PAVILLON PHILIPS · LE CORBUSIER, I. XENAKIS', 7, '#5d5851', fam='Work Sans', wt=600, track=0.12)
    sx, sy = 352, 230
    perf = ''.join('M%s %sa1.6 1.6 0 1 0 0.01 0' % (f(sx + k * 5), f(sy)) for k in range(10)) + ''.join('M%s %sa1.6 1.6 0 1 0 0.01 0' % (f(sx + k * 5), f(sy + 42)) for k in range(10))
    S.add(rect(sx - 1, sy + 1.5, 48, 42, '#000', opacity='0.18', filter=S.blur(1.2)))
    S.add(rect(sx - 2, sy, 48, 42, '#fbf5e6'), path(perf, fill='#f4eee0'))
    S.add(rect(sx + 3, sy + 4, 38, 30, S.lin([(0, '#c55536'), (1, '#9c3a22')])), path(P([(sx + 7, sy + 31), (sx + 18, sy + 11), (sx + 26, sy + 30), (sx + 33, sy + 16), (sx + 38, sy + 31)]), stroke='#fbf5e6', w=1.2))
    S.text(sx + 22, sy + 39.6, 'BELGIQUE 3F', 4.4, '#5d5851', fam='Work Sans', wt=600, anchor='middle', track=0.1)
    # a postmark's wavy lines over the stamp's corner
    S.ink(path(''.join('M%s %sq6 -3 12 0t12 0t12 0' % (f(sx - 22), f(sy + 12 + k * 4)) for k in range(4)), stroke='#2c3e5a', w=0.7, opacity='0.6'),
          '<circle cx="%s" cy="%s" r="11" fill="none" stroke="#2c3e5a" stroke-width="0.8" opacity="0.6"/>' % (f(sx - 4), f(sy + 22)))
    S.grain(1.2)
    S.save('a2')

# ---------------------------------------------------------------- C: Pithoprakta
def b1():
    S = Sheet(560, 340, 'A cloud of short sloping glissando strokes and pizzicato dots, denser in the middle', 31)
    S.paper(PAPER)
    x0, x1, y0, y1 = 40, 540, 20, 300
    S.add(rect(x0, y0, x1 - x0, y1 - y0, S.grid(5, 25, '#ece4cf', '#dccfae', 0.3, 0.55, x0, y0)))
    # the cloud's density, washed in behind it
    S.add('<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="%s" opacity="0.2" filter="%s"/>' % (f((x0 + x1) / 2), f((y0 + y1) / 2), f(180), f(90), BLUE, S.blur(30)))
    S.add(line(x0, y0, x0, y1, GRAPH, 0.9), line(x0, y1, x1, y1, GRAPH, 0.9))
    S.text(16, (y0 + y1) / 2, 'pitch', 10, GRAPH, rot=-90, anchor='middle')
    S.text(x1 - 30, y1 + 18.5, 'time', 10, GRAPH, anchor='end'); S.add(arrow(x1 - 24, y1 + 15, 22))
    rnd = random.Random(1956)
    # three planes of strokes: behind, thin and pale; in front, full and dark
    for plane, (n, wmax, op) in enumerate(((220, 0.8, 0.35), (200, 1.2, 0.6), (160, 1.7, 0.9))):
        ds = {BLUE: '', RED: '', GRAPH: ''}
        for k in range(n):
            tx = min(max(rnd.gauss(0.5, 0.2), 0.02), 0.96); ty = min(max(rnd.gauss(0.5, 0.22), 0.04), 0.96)
            v = math.sqrt(sum(rnd.gauss(0, 1) ** 2 for _ in range(3)))
            ang = math.atan(v * 0.55) * rnd.choice((-1, 1))
            L = rnd.uniform(9, 20) * (0.8 + 0.2 * plane)
            x, y = x0 + tx * (x1 - x0), y1 - ty * (y1 - y0)
            ds[rnd.choice((BLUE, BLUE, RED, GRAPH))] += taper(seg(x, y, x + L * math.cos(ang), y - L * math.sin(ang), 6, rnd.uniform(-1.2, 1.2)), wmax, 0.1, 0.4)
        S.ink(*[path(d, fill=c) for c, d in ds.items()], opacity=op)
    dots = ''
    for k in range(130):
        x = x0 + min(max(rnd.gauss(0.5, 0.28), 0.02), 0.98) * (x1 - x0); y = y1 - min(max(rnd.gauss(0.5, 0.3), 0.03), 0.97) * (y1 - y0)
        dots += 'M%s %sh.01' % (f(x), f(y))
    S.add(path(dots, stroke=GRAPH, w=4.4, stroke_linecap='round', opacity='0.18', filter=S.blur(1.2)))
    S.ink(path(dots, stroke=GRAPH, w=2.6, stroke_linecap='round'))
    ix, iy, iw, ih = x1 - 190, y0 + 12, 178, 80
    S.add(rect(ix + 2, iy + 3, iw, ih, '#000', opacity='0.15', filter=S.blur(2)))
    S.add(rect(ix, iy, iw, ih, PAPER), rect(ix, iy, iw, ih, 'none', stroke=GRAPH, stroke_width='0.6'))
    pts = []
    for k in range(61):
        v = k / 60 * 4
        p = math.sqrt(2 / math.pi) * v * v * math.exp(-v * v / 2)
        pts.append((ix + 10 + v / 4 * (iw - 20), iy + ih - 14 - p / 0.6 * (ih - 32)))
    S.add(path(P(pts + [(pts[-1][0], iy + ih - 14), (pts[0][0], iy + ih - 14)]) + 'Z', fill=RED, opacity='0.12'))
    S.ink(path(taper(pts, 1.6, 0.6, 0.6, 0.3), fill=RED), line(ix + 10, iy + ih - 14, ix + iw - 8, iy + ih - 14, GRAPH, 0.6))
    S.text(ix + 8, iy + 14, 'speeds: Maxwell–Boltzmann', 8, GRAPH)
    S.text(ix + iw - 8, iy + ih - 4, 'v', 8, GRAPH, anchor='end')
    S.text(x0 + 10, y1 - 10, 'pizz. ·   gliss. /', 13, GRAPH, fam='Caveat', opacity=0.85)
    S.grain()
    S.save('b1')

# ---------------------------------------------------------------- D: Arborescences
def c1():
    S = Sheet(560, 320, 'A single line branching like a tree from left to right, with a faint mirrored copy in red', 41)
    S.paper(VELLUM, 0.05)
    y_mid = 160
    for k in range(-12, 13):
        S.add(line(20, y_mid + k * 10, 540, y_mid + k * 10, '#b9a985', 0.5 if k % 6 == 0 else 0.25, opacity='0.55'))
    rnd = random.Random(1973)
    paths = []
    def grow(x, y, dy, depth, w):
        L = rnd.uniform(38, 60)
        nx, ny = x + L, y + dy * L + rnd.uniform(-5, 5)
        if ny < 84: ny, dy = 84 + (84 - ny) * 0.3, abs(dy) * 0.6
        elif ny > 236: ny, dy = 236 - (ny - 236) * 0.3, -abs(dy) * 0.6
        paths.append((x, y, nx, ny, w, depth))
        if nx > 520 or depth > 6: return
        k = rnd.choice((2, 3)) if depth < 2 else rnd.choice((1, 1, 1, 2))
        for i in range(k):
            ndy = dy * 0.55 + rnd.uniform(-0.3, 0.3) + (i - (k - 1) / 2) * 0.5
            grow(nx, ny, max(-0.6, min(0.6, ndy)), depth + 1, max(0.55, w * 0.8))
    paths.append((24, y_mid, 70, y_mid, 2.2, 0))
    grow(70, y_mid, 0.0, 0, 2.0)
    def pts(x, y, nx, ny, n=12):
        out = []
        for k in range(n + 1):
            t = k / n; s = t * t * (3 - 2 * t)
            out.append((x + (nx - x) * t, y + (ny - y) * s))
        return out
    # the inversion: a wash of red under it, its branches faint and soft, as if behind the sheet
    mirror = ''.join(taper(pts(x, 2 * y_mid - y, nx, 2 * y_mid - ny), w * 0.9, w * 0.85, w * 0.7, 0.2) for x, y, nx, ny, w, dep in paths)
    S.add(path(mirror, fill=RED, opacity='0.18', filter=S.blur(1.0)))
    S.add(path(mirror, fill=RED, opacity='0.22'))
    # the tree, in ink: each branch a stroke narrowing toward its tip; the shadow of the ink
    # a little offset, as it lies on the vellum's grain
    d = ''.join(taper(pts(x, y, nx, ny), w, w * 1.0, w * 0.75, 0.2) for x, y, nx, ny, w, dep in paths)
    S.add(path(d, fill='#5a4a30', opacity='0.18', filter=S.blur(1.4), transform='translate(1.2 1.6)'))
    S.ink(path(d, fill='#1f1d1a'))
    S.add(circle(24, y_mid, 2.6, '#1f1d1a'))
    S.text(30, 28, 'arborescence', 15, GRAPH, fam='Caveat', wt=700)
    S.text(30, 44, 'one line, branching, on the plane of pitch and time', 12, GRAPH, fam='Caveat', opacity=0.8)
    S.text(530, 300, 'mirror (inversion), in red', 12, RED, fam='Caveat', anchor='end', opacity=0.8)
    S.add(line(20, 300, 180, 300, GRAPH, 0.6)); S.text(184, 303, 'time', 9, GRAPH); S.add(arrow(226, 300, 22))
    S.grain(1.1)
    S.save('c1')

# ---------------------------------------------------------------- E: Nomos Alpha
def d1():
    S = Sheet(440, 330, 'A cube with vertices numbered 1 to 8 and three dashed rotation axes: through faces, through a diagonal, through edges', 51)
    S.paper(PAPER)
    S.add(rect(0, 0, 440, 330, S.grid(5, 25, '#ece4cf', '#dccfae')))
    cx, cy, a = 200, 186, 108
    ox, oy = 48, -40
    V = {1: (cx - a / 2, cy + a / 2), 2: (cx + a / 2, cy + a / 2), 3: (cx + a / 2, cy - a / 2), 4: (cx - a / 2, cy - a / 2)}
    for k in range(4): V[k + 5] = (V[k + 1][0] + ox, V[k + 1][1] + oy)
    # its shadow on the paper, thrown down and to the right
    S.add(path(P([(V[1][0] + 18, V[1][1] + 8), (V[2][0] + 30, V[2][1] + 8), (V[6][0] + 46, V[6][1] + 30), (V[5][0] + 30, V[5][1] + 34)]) + 'Z', fill='#4a3b22', opacity='0.22', filter=S.blur(6)))
    ext = lambda p, q, t: (p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t)
    fc = ((V[1][0] + V[3][0]) / 2 + ox / 2, (V[1][1] + V[3][1]) / 2 + oy / 2)
    m1 = ((V[1][0] + V[5][0]) / 2, (V[1][1] + V[5][1]) / 2); m2 = ((V[3][0] + V[7][0]) / 2, (V[3][1] + V[7][1]) / 2)
    axes = [((fc[0], cy - a / 2 - 52 + oy / 2), (fc[0], cy + a / 2 + 46 + oy / 2), BLUE), (ext(V[1], V[7], -0.35), ext(V[1], V[7], 1.35), RED), (ext(m1, m2, -0.4), ext(m1, m2, 1.4), GREEN)]
    # the axes behind the cube first, faint; then the cube's faces, shaded; then the axes again in front
    for p, q, c in axes: S.add(line(p[0], p[1], q[0], q[1], c, 1.0, stroke_dasharray='6 3', opacity='0.7'))
    S.add(path(P([V[1], V[2], V[3], V[4]]) + 'Z', fill=S.lin([(0, '#fbf6e8'), (1, '#e9dfc6')], 1, 1), opacity='0.85'))
    S.add(path(P([V[4], V[3], V[7], V[8]]) + 'Z', fill=S.lin([(0, '#fffaf0'), (1, '#efe5cd')], 1, 0), opacity='0.88'))
    S.add(path(P([V[2], V[6], V[7], V[3]]) + 'Z', fill=S.lin([(0, '#d9ccad'), (1, '#c3b38f')], 1, 0), opacity='0.9'))
    hidden = [(1, 5), (5, 6), (5, 8)]
    S.ink(path(''.join('M%s %sL%s %s' % (f(V[p][0]), f(V[p][1]), f(V[q][0]), f(V[q][1])) for p, q in hidden), stroke=GRAPH, w=0.8, stroke_dasharray='4 3', opacity='0.6'))
    edges = [(1, 2), (2, 3), (3, 4), (4, 1), (2, 6), (3, 7), (4, 8), (6, 7), (7, 8)]
    S.ink(path(''.join(taper(seg(V[p][0], V[p][1], V[q][0], V[q][1], 8), 2.1, 1.2, 1.2, 0.5) for p, q in edges), fill='#1f1d1a'))
    # where each axis comes out of the cube toward us, it is drawn again over the faces
    for p, q, c in axes:
        for t0, t1 in ((0.0, 0.2), (0.8, 1.0)):
            a_, b_ = ext(p, q, t0), ext(p, q, t1)
            S.add(line(a_[0], a_[1], b_[0], b_[1], c, 1.3, stroke_dasharray='6 3'))
    # the turns: arrows on ellipses round the face axis and the diagonal
    for (x, y), c in (((fc[0], cy - a / 2 - 40 + oy / 2), BLUE), (ext(V[1], V[7], 1.22), RED)):
        S.ink(path(taper([(x + 14 * math.cos(t), y + 5 * math.sin(t)) for t in [k / 20 * 1.7 * math.pi for k in range(21)]], 1.4, 0.4, 1.2), fill=c),
              path('M%s %sl-4.6 -3l0.6 5.4z' % (f(x + 14 * math.cos(1.7 * math.pi) + 1), f(y + 5 * math.sin(1.7 * math.pi))), fill=c))
    S.text(fc[0] + 6, 30, 'face axis: 90°, 180°, 270° (×3 = 9)', 11, BLUE, fam='Caveat', wt=700)
    S.text(430, 292, 'diagonal: 120°, 240° (×4 = 8)', 11, RED, fam='Caveat', wt=700, anchor='end')
    S.text(24, 300, 'edge axis: 180° (×6 = 6)', 11, GREEN, fam='Caveat', wt=700)
    for k, (x, y) in V.items():
        S.add(circle(x + 1, y + 1.6, 9, '#000', opacity='0.2', filter=S.blur(1.2)))
        S.add(circle(x, y, 8.6, S.rad([(0, '#ffffff', 1), (1, '#efe7d4', 1)], 0.4, 0.35, 0.7)), circle(x, y, 8.6, 'none', stroke='#1f1d1a', stroke_width='1.1'))
        S.text(x, y + 4, str(k), 11, '#1f1d1a', wt=700, anchor='middle')
    S.text(420, 318, 'identity 1 + 9 + 8 + 6 = 24 rotations', 9, GRAPH, anchor='end')
    S.grain()
    S.save('d1')

# ---------------------------------------------------------------- F: three sieves
def e1():
    S = Sheet(600, 300, "Three sieves drawn on lines: a seventeen-semitone scale, a forty-pulse rhythm, and the sample deck's sieve 2 3 7 8 12 13 17 18", 61)
    S.paper(MANU, 0.03)
    for y in range(18, 300, 10): S.add(line(14, y, 586, y, '#e3dccb', 0.3))
    S.text(20, 30, 'JONCHAIES · 17@{0,1,4,5,7,11,12,16} · semitones', 9.5, GRAPH, fam='Work Sans', wt=600, track=0.08)
    mem = {0, 1, 4, 5, 7, 11, 12, 16}
    x, w, y = 20, 16.4, 40
    S.add(rect(x - 2, y + 2, 34 * w + 2, 36, '#000', opacity='0.18', filter=S.blur(2.4)))
    white, black = S.lin([(0, '#fffefa'), (0.85, '#f1ead8'), (1, '#d8cfba')]), S.lin([(0, '#4a4642'), (0.15, '#1f1d1a'), (0.9, '#121110'), (1, '#3a3632')])
    for k in range(34):
        on = (k % 17) in mem
        S.add(path('M%s %sh%sv%sq0 2 -2 2h%sq-2 0 -2 -2z' % (f(x + k * w), f(y), f(w - 2), f(32), f(-(w - 6))), fill=black if on else white))
        S.add(path('M%s %sh%sv%sq0 2 -2 2h%sq-2 0 -2 -2z' % (f(x + k * w), f(y), f(w - 2), f(32), f(-(w - 6))), stroke='#6f6b62', w=0.5))
        if on: S.add(rect(x + k * w + 2, y + 2, 2.2, 28, '#ffffff', opacity='0.22'))
        if k % 17 == 0: S.ink(path(taper(seg(x + k * w - 1.2, y - 7, x + k * w - 1.2, y + 44, 6), 1.8), fill=RED))
    steps = [b - a for a, b in zip(sorted(mem), sorted(mem)[1:] + [17])]
    for per in (0, 17):
        for a_, st in zip(sorted(mem), steps):
            S.text(x + (per + a_) * w + st * w / 2 - 1, y + 50, str(st), 8.5, RED, anchor='middle')
    S.text(20, 128, 'PSAPPHA · RHYTHMIC SIEVE · PERIOD 40 PULSES · MODULI 8 AND 5', 9.5, GRAPH, fam='Work Sans', wt=600, track=0.08)
    rm = {0, 1, 3, 4, 6, 8, 10, 11, 12, 13, 14, 16, 17, 19, 20, 22, 23, 25, 27, 28, 29, 31, 33, 35, 36, 37, 38}
    y = 150
    S.ink(path(taper(seg(20, y, 580, y, 30), 0.9, 0.5, 0.5), fill='#55534c'))
    for k in range(40):
        px = 26 + k * 13.9
        if k in rm:
            S.add(circle(px + 0.8, y + 1.6, 4.8, '#000', opacity='0.18', filter=S.blur(1.0)))
            S.add(circle(px, y, 4.8, S.rad([(0, '#5e86c0', 1), (0.6, BLUE, 1), (1, '#173a6b', 1)], 0.35, 0.3, 0.8)))
        else: S.add(circle(px, y, 1.4, '#8a857a'))
        if k % 8 == 0:
            S.add(line(px, y + 9, px, y + 15, GRAPH, 0.7))
            S.text(px, y + 25, str(k), 8.5, GRAPH, anchor='middle')
    S.text(20, 212, '5@2 | 5@3 · THE SAMPLE DECK · 0 TO 19', 9.5, GRAPH, fam='Work Sans', wt=600, track=0.08)
    y = 224
    for k in range(20):
        on = k % 5 in (2, 3)
        bx_ = 20 + k * 22
        S.add(rect(bx_ + 0.8, y + 1.6, 18, 18, '#000', opacity='0.16' if on else '0.08', filter=S.blur(1.0)))
        S.add(rect(bx_, y, 18, 18, S.lin([(0, '#c44a33'), (1, '#8e2c1f')]) if on else S.lin([(0, '#fffefa'), (1, '#efe8d6')])), rect(bx_, y, 18, 18, 'none', stroke='#6f6b62', stroke_width='0.5'))
        S.text(bx_ + 9, y + 32, str(k), 8.5, GRAPH, anchor='middle')
    S.text(470, 238, '2 3 7 8 12 13 17 18', 13, RED, fam='Caveat', wt=700)
    S.grain(0.9)
    S.save('e1')

# ---------------------------------------------------------------- G: a UPIC page
def f1():
    S = Sheet(560, 320, 'A page of pen-drawn wavy arcs in bundles, pitch against time', 71)
    S.paper(PAPER, 0.03)
    x0, x1, y0, y1 = 24, 536, 18, 290
    for k in range(1, 12): S.add(line(x0 + k * (x1 - x0) / 12, y0, x0 + k * (x1 - x0) / 12, y1, '#d9d3c4', 0.4))
    S.add(rect(x0, y0, x1 - x0, y1 - y0, 'none', stroke='#8a857a', stroke_width='0.8'))
    rnd = random.Random(1978)
    bundles = [(40, 220, 260, 120, 9, 0.8, -0.9, BLUE), (180, 70, 380, 160, 7, 1.0, 1.2, '#1f1d1a'), (300, 230, 520, 200, 8, 0.6, 0.6, BLUE),
               (80, 110, 200, 60, 5, 1.2, -1.6, RED), (360, 60, 520, 90, 6, 0.9, 1.0, '#1f1d1a'), (230, 250, 330, 260, 4, 0.5, 2.0, SEPIA)]
    # a pencilled underdrawing first, the arcs' paths roughed in
    under = ''
    for xs, ys, xe, ye, n, amp, freq, c in bundles:
        pts = [(xs + (xe - xs) * t, ys + (ye - ys) * t + amp * 18 * math.sin(2 * math.pi * freq * t)) for t in [k / 30 for k in range(31)]]
        under += 'M' + 'L'.join('%s %s' % (f(x), f(y + rnd.uniform(-2, 2))) for x, y in pts)
    S.add(path(under, stroke='#9a958a', w=0.5, opacity='0.5'))
    for xs, ys, xe, ye, n, amp, freq, c in bundles:
        d = ''
        for k in range(n):
            off = (k - n / 2) * 3.2
            ph = rnd.uniform(0, 1)
            pts = []
            for s_ in range(48):
                t = s_ / 47
                pts.append((xs + (xe - xs) * t, ys + (ye - ys) * t + off + amp * 18 * math.sin(2 * math.pi * (freq * t + ph * 0.15)) * (0.6 + 0.4 * t)))
            d += taper(pts, rnd.uniform(1.0, 1.9), 0.2, 0.3, 0.7)
        S.add(path(d, fill=c, opacity='0.25', filter=S.blur(1.6)))
        S.ink(path(d, fill=c, opacity='0.9', style='mix-blend-mode:multiply'))
    S.text(x0, y1 + 18, 'UPIC · drawn arcs: pitch over time', 9, GRAPH)
    S.text(x1 - 28, y1 + 18, 'time', 9, GRAPH, anchor='end'); S.add(arrow(x1 - 24, y1 + 15, 22))
    S.grain()
    S.save('f1')

# ---------------------------------------------------------------- I: Achorripsis
def i1():
    S = Sheet(640, 330, 'A matrix of 28 columns of time by 7 rows of timbre; most of its 196 cells are empty, and the rest hold 1, 2, 3 or, once, 4 events', 81)
    S.paper(PAPER)
    S.add(rect(0, 0, 640, 330, S.grid(4, 20, '#efe7d4', '#e2d6bb')))
    x0, y0, cw, ch = 82, 46, 19.4, 26
    counts = [0] * 107 + [1] * 65 + [2] * 19 + [3] * 4 + [4] * 1
    rnd = random.Random(1957); rnd.shuffle(counts)
    shade = ['#fffdf6', '#efe2c4', '#dfc796', '#c79f5f', '#a36f35']
    S.add(rect(x0 + 2, y0 + 3, 28 * cw, 7 * ch, '#000', opacity='0.2', filter=S.blur(3)))
    S.text(x0, 24, 'TIME (28 COLUMNS)', 9, GRAPH, fam='Work Sans', wt=600, track=0.12)
    for c in range(28):
        if c % 2 == 0 or c == 27: S.text(x0 + c * cw + cw / 2, 40, str(c + 1), 8.5, GRAPH, anchor='middle')
    S.text(26, y0 + 3.5 * ch, 'TIMBRE', 9, GRAPH, fam='Work Sans', wt=600, rot=-90, anchor='middle', track=0.12)
    roman = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII']
    grads = [S.lin([(0, light), (1, dk)]) for light, dk in (('#fffefa', '#f6efdf'), ('#f5ead0', '#e6d6b2'), ('#e8d3a6', '#d4b67f'), ('#d4ae70', '#b78949'), ('#b3793d', '#8f5a28'))]
    for r in range(7):
        S.text(x0 - 10, y0 + r * ch + ch / 2 + 4, roman[r], 10, GRAPH, wt=700, anchor='end')
        for c in range(28):
            v = counts[r * 28 + c]
            S.add(rect(x0 + c * cw, y0 + r * ch, cw, ch, grads[v]))
            if v:
                S.add(rect(x0 + c * cw, y0 + r * ch, cw, 1.2, '#ffffff', opacity='0.35'))
                S.text(x0 + c * cw + cw / 2, y0 + r * ch + ch / 2 + 4, str(v), 11, '#2a2216' if v < 3 else '#fffaf0', wt=700, anchor='middle')
    grid = ''.join('M%s %sV%s' % (f(x0 + c * cw), f(y0), f(y0 + 7 * ch)) for c in range(29)) + ''.join('M%s %sH%s' % (f(x0), f(y0 + r * ch), f(x0 + 28 * cw)) for r in range(8))
    S.ink(path(grid, stroke='#8a7a5a', w=0.5))
    S.ink(rect(x0, y0, 28 * cw, 7 * ch, 'none', stroke='#2a2216', stroke_width='1.5'),
          path(''.join('M%s %sV%s' % (f(x0 + c * cw), f(y0), f(y0 + 7 * ch)) for c in range(4, 28, 4)), stroke='#2a2216', w=0.9))
    ly = y0 + 7 * ch + 26
    for k, (v, n) in enumerate(((0, 107), (1, 65), (2, 19), (3, 4), (4, 1))):
        lx = x0 + k * 108
        S.add(rect(lx, ly - 9, 12, 12, grads[v]), rect(lx, ly - 9, 12, 12, 'none', stroke='#8a7a5a', stroke_width='0.6'))
        S.text(lx + 18, ly + 1, '%d: %d' % (v, n), 9.5, GRAPH)
    S.text(x0, ly + 24, 'events per cell: number of cells · 196 cells · mean 0.6 · Poisson', 9.5, GRAPH, wt=700)
    S.text(x0 + 28 * cw, ly + 44, 'the counts are his; the places are chance', 12, SEPIA, fam='Caveat', anchor='end')
    S.grain()
    S.save('i1')

# ---------------------------------------------------------------- J: Analogique screens
# After Xenakis's scheme for Analogique A (as Di Scipio sets it out): the range of pitch in six
# regions, I to VI; dynamics pp, f, fff; density 1, 3 or 9 notes a half-bar. Each variable has
# two sets: f0 = regions I, II, V, VI and f1 = III, IV; g0 = pp, pp, f, fff and g1 = pp, f;
# d0 = 1, 1, 3, 9 and d1 = 1, 3, 3, 9. The eight screens are their combinations,
# A = f0 g0 d0 to H = f1 g1 d1. Each panel is a grid of regions (up) by dynamics (across);
# in each region its set sounds, a cell is drawn from its g set and filled with notes by its d set.
def j1():
    S = Sheet(640, 344, 'Eight small panels lettered A to H, each a cloud of short grains of sound placed by pitch and loudness, some dense and some sparse', 91)
    S.paper(PAPER, 0.03)
    S.text(24, 26, 'SCREENS · 6 PITCH REGIONS × 3 DYNAMICS · DENSITY IN NOTES A HALF-BAR', 9.5, GRAPH, fam='Work Sans', wt=600, track=0.1)
    rnd = random.Random(1958)
    F = {0: (0, 1, 4, 5), 1: (2, 3)}
    G = {0: (0, 0, 1, 2), 1: (0, 1)}
    Dn = {0: (1, 1, 3, 9), 1: (1, 3, 3, 9)}
    for k in range(8):
        fset, gset, dset = (k >> 2) & 1, (k >> 1) & 1, k & 1
        col, row = k % 4, k // 4
        x, y, w, h = 24 + col * 152, 42 + row * 150, 136, 112
        gx0, gw = x + 14, w - 18
        S.add(rect(x + 2.5, y + 3.5, w, h, '#000', opacity='0.16', filter=S.blur(2.6)))
        S.add(rect(x, y, w, h, S.lin([(0, '#fffefa'), (1, '#f4eedf')])), rect(x, y, w, h, 'none', stroke='#55534c', stroke_width='0.8'))
        rh, cw = h / 6, gw / 3
        for r in range(6):
            yy = y + h - (r + 1) * rh
            if r in F[fset]: S.add(rect(gx0, yy, gw, rh, BLUE, opacity='0.05'))
            S.add(line(x, yy, x + w, yy, '#e1dace', 0.5))
            S.text(x + 6, yy + rh / 2 + 2.5, 'I II III IV V VI'.split()[r], 5.2, '#8a857a', anchor='middle')
        for c in (1, 2): S.add(line(gx0 + c * cw, y, gx0 + c * cw, y + h, '#e1dace', 0.5, stroke_dasharray='2 2'))
        grains = {'#1f1d1a': '', BLUE: ''}
        for r in F[fset]:
            c = rnd.choice(G[gset])
            n = rnd.choice(Dn[dset])
            wgt = (1.0, 1.7, 2.5)[c]          # pp light, f heavier, fff heaviest
            for g_ in range(n):
                gx = gx0 + c * cw + 3 + rnd.random() * (cw - 10)
                gy = y + h - (r + 0.2 + rnd.random() * 0.6) * rh
                L = rnd.uniform(3, 7)
                grains[rnd.choice(('#1f1d1a', '#1f1d1a', BLUE))] += taper(seg(gx, gy, gx + L, gy + rnd.uniform(-0.5, 0.5), 4), wgt, 0.3, 0.3, 0.5)
        S.ink(*[path(d, fill=c) for c, d in grains.items() if d])
        S.text(x, y + h + 16, 'ABCDEFGH'[k], 12, GRAPH, fam='Work Sans', wt=600)
        S.text(x + w, y + h + 15, 'f%d  g%d  d%d' % (fset, gset, dset), 8.5, GRAPH, anchor='end')
    S.text(616, 22 + 300 + 14, 'pp  ·  f  ·  fff  across', 11, GRAPH, fam='Caveat', anchor='end')
    S.grain()
    S.save('j1')

# ---------------------------------------------------------------- L: Terretektorh
def l1():
    S = Sheet(520, 470, 'Plan of a round hall: 88 players, marked by section, are scattered through rings of audience seats', 101)
    S.paper(PAPER)
    cx, cy, R = 260, 222, 200
    S.add(circle(cx + 3, cy + 5, R + 8, '#000', opacity='0.18', filter=S.blur(6)))
    S.add(circle(cx, cy, R + 6, S.lin([(0, '#efe7d3'), (1, '#d9cdb2')], 1, 1)))
    S.ink(circle(cx, cy, R + 6, 'none', stroke='#1f1d1a', stroke_width='2.6'))
    # the floor lit from the centre, where the conductor stands
    S.add(circle(cx, cy, R, S.rad([(0, '#fffbf0', 1), (0.7, '#f5eedd', 1), (1, '#e8dcc2', 1)])))
    rnd = random.Random(1966)
    rings = list(range(30, int(R) - 6, 13))
    cand = []
    for r in rings:
        n = int(2 * math.pi * r / 10)
        for k in range(n):
            a = 2 * math.pi * k / n
            if any(abs(((a - ax + math.pi) % (2 * math.pi)) - math.pi) < 7 / r for ax in (0, math.pi / 2, math.pi, 3 * math.pi / 2)): continue
            cand.append((cx + r * math.cos(a), cy + r * math.sin(a), a))
    rnd.shuffle(cand)
    players, seats = cand[:88], cand[88:]
    # seats: small chairs turned to the centre, their shadows soft
    sd = ''.join('M%s %sh.01' % (f(x + 0.6), f(y + 0.9)) for x, y, a in seats)
    S.add(path(sd, stroke='#000', w=4.4, stroke_linecap='round', opacity='0.1', filter=S.blur(0.8)))
    S.add(path(''.join('M%s %sh.01' % (f(x), f(y)) for x, y, a in seats), stroke='#cdbf9e', w=3.8, stroke_linecap='round'))
    S.add(path(''.join('M%s %sh.01' % (f(x - 0.5), f(y - 0.6)) for x, y, a in seats), stroke='#e6dcc5', w=1.6, stroke_linecap='round'))
    kinds = ['s'] * 60 + ['w'] * 12 + ['b'] * 13 + ['p'] * 3
    rnd.shuffle(kinds)
    marks = {'s': '', 'w': '', 'b': '', 'p': ''}
    for (x, y, a), kd in zip(players, kinds):
        if kd == 's': marks[kd] += 'M%s %sa3.6 3.6 0 1 0 0.01 0' % (f(x - 3.6), f(y))
        elif kd == 'w': marks[kd] += 'M%s %sl4.2 7h-8.4z' % (f(x), f(y - 4.6))
        elif kd == 'b': marks[kd] += 'M%s %sh7.2v7.2h-7.2z' % (f(x - 3.6), f(y - 3.6))
        else: marks[kd] += 'M%s %sl5.2 5.2-5.2 5.2-5.2-5.2z' % (f(x), f(y - 5.2))
    style = {'s': '#1f1d1a', 'w': GREEN, 'b': RED, 'p': BLUE}
    for kd, d in marks.items():
        S.add(path(d, fill='#000', opacity='0.22', filter=S.blur(1.1), transform='translate(1 1.4)'))
        S.add(path(d, fill=style[kd]))
    # sound travelling round the hall: a faint spiral of arrows through the rings
    sp = [(cx + (40 + t * 140) * math.cos(t * 4.4), cy + (40 + t * 140) * math.sin(t * 4.4)) for t in [k / 60 for k in range(61)]]
    S.ink(path(taper(sp, 1.8, 0.3, 0.6, 0.5), fill=RED, opacity='0.45'))
    S.add(circle(cx + 1, cy + 1.6, 11, '#000', opacity='0.25', filter=S.blur(1.4)))
    S.add(circle(cx, cy, 10.5, S.rad([(0, '#ffffff', 1), (1, '#efe7d4', 1)], 0.4, 0.35, 0.7)), circle(cx, cy, 10.5, 'none', stroke='#1f1d1a', stroke_width='1.2'), circle(cx, cy, 3.2, '#1f1d1a'))
    for a in (math.pi / 4, 5 * math.pi / 4):
        S.add(circle(cx + (R + 3) * math.cos(a), cy + (R + 3) * math.sin(a), 7, PAPER))
    ly = 448
    for k, (kd, lab) in enumerate((('s', '60 strings'), ('w', '12 woodwinds'), ('b', '13 brass'), ('p', '3 percussion'))):
        lx = 40 + k * 118
        if kd == 's': S.add(circle(lx, ly - 3, 3.6, style[kd]))
        elif kd == 'w': S.add(path('M%s %sl4.2 7h-8.4z' % (f(lx), f(ly - 7)), fill=style[kd]))
        elif kd == 'b': S.add(rect(lx - 3.5, ly - 6.5, 7, 7, style[kd]))
        else: S.add(path('M%s %sl5 5-5 5-5-5z' % (f(lx), f(ly - 8)), fill=style[kd]))
        S.text(lx + 10, ly + 0.5, lab, 9.5, GRAPH)
    S.text(cx + 14, cy - 12, 'chef', 13, GRAPH, fam='Caveat', wt=700)
    S.grain()
    S.save('l1')

if __name__ == '__main__':
    import sys
    for k in (sys.argv[1:] or ['a1', 'a2', 'b1', 'c1', 'd1', 'e1', 'f1', 'i1', 'j1', 'l1']): globals()[k]()
