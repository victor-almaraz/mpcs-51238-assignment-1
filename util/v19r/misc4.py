# The miscellanea's drawings as old scientific plates (a fourth pass for v21). After the
# engraved figures of 19th-century textbooks (Ganot's physics, crystallography): tone
# translated into parallel lines, cross-hatching and stipple; points lettered in italic;
# a plate frame of double rules, its plate number at the head and its caption, "Fig. 1.",
# in Caslon small capitals and italics at the foot; foxed, yellowed paper; black or sepia
# ink with an occasional pale hand-tinted wash. Two take a particular source: the cube in
# the flat red, yellow and blue of Byrne's Euclid (1847), and the UPIC page as a tracing of
# Marey's graphic method, white lines scratched into smoked paper. The data are those
# checked against the sources (see version-designs.md).
import math, random, os
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
import misc2
from misc2 import f, P, line, path, circle, rect, OUT
from misc3 import Sheet as Base3, taper, seg

INK, SEPIA, CARMINE, PRUSSIAN, GAMBOGE = '#231c14', '#5b4127', '#a8362b', '#2f4a6b', '#c9a13c'
PAPER = '#f2e8d2'
BYRNE = dict(red='#c8352a', yellow='#e8b923', blue='#2b5f9e')

ITAL = {}
def font_i(fam, wt):
    k = (fam, wt)
    if k not in ITAL:
        slug = fam.lower().replace(' ', '-')
        t = TTFont('%s/fonts/%s/%s-latin-%d-italic.woff2' % (misc2.REPO, slug, slug, wt))
        ITAL[k] = (t.getGlyphSet(), t.getBestCmap(), t['head'].unitsPerEm, t['hmtx'])
    return ITAL[k]

class Plate(Base3):
    def __init__(self, w, h, title, seed, pl, fig, cap):
        super().__init__(w, h, title, seed)
        self.pl, self.fig, self.cap = pl, fig, cap
        self.rnd = random.Random(seed * 7 + 3)
    # serif lettering: Libre Caslon, roman or italic, as outlines
    def serif(self, x, y, s, size, fill=INK, italic=False, wt=400, anchor='start', rot=0, track=0.0, caps=False):
        if caps: s = s.upper()
        if not italic:
            return self.text(x, y, s, size / (1.35 if size < 12 else 1.1), fill, fam='Libre Caslon Text', wt=wt, anchor=anchor, rot=rot, track=track)
        gs, cmap, upm, hmtx = font_i('Libre Caslon Text', 400)   # the italic comes in one weight
        sc = size / upm; ls = track * upm
        adv = [hmtx[cmap.get(ord(c), cmap[ord('?')])][0] + ls for c in s]
        width = (sum(adv) - (ls if s else 0)) * sc
        dx = {'start': 0, 'middle': -width / 2, 'end': -width}[anchor]
        tr = 'translate(%s %s)' % (f(x), f(y)) + (' rotate(%s)' % f(rot) if rot else '') + ' translate(%s 0) scale(%s %s)' % (f(dx), ('%.5f' % sc).rstrip('0'), ('%.5f' % -sc).rstrip('0'))
        uses, u = [], 0
        for c, a in zip(s, adv):
            if c != ' ':
                gn = cmap.get(ord(c), cmap[ord('?')])
                k = ('LCi', wt, gn)
                if k not in self.glyphs:
                    pen = SVGPathPen(gs, ntos=lambda v: str(int(round(v))))
                    gs[gn].draw(pen)
                    self.glyphs[k] = ('t%d' % len(self.glyphs), pen.getCommands())
                uses.append('<use href="#%s"%s/>' % (self.glyphs[k][0], (' x="%d"' % round(u)) if u else ''))
            u += a
        self.add('<g transform="%s" fill="%s">%s</g>' % (tr, fill, ''.join(uses)))
    def aged(self):
        """old paper: yellowed toward the edges, a few foxing spots"""
        self.add(rect(0, 0, self.w, self.h, PAPER))
        self.add(rect(0, 0, self.w, self.h, self.rad([(0, '#fff8e8', 0.5), (0.6, '#fff8e8', 0), (1, '#8a6a30', 0.28)], 0.5, 0.45, 0.8)))
        for k in range(int(self.w * self.h / 9000)):
            x, y = self.rnd.uniform(0, self.w), self.rnd.uniform(0, self.h)
            r = self.rnd.uniform(0.8, 3.5)
            self.add(circle(x, y, r, '#8a5a2a', opacity=f(self.rnd.uniform(0.05, 0.14)), filter=self.blur(r * 0.6)))
    def frame(self, top=26, bottom=34):
        """the plate's double rule, its number at the head and its caption at the foot"""
        m = 10
        self.add(rect(m, top - 6, self.w - 2 * m, self.h - top - bottom + 12, 'none', stroke=INK, stroke_width='1.2'))
        self.add(rect(m + 3, top - 3, self.w - 2 * m - 6, self.h - top - bottom + 6, 'none', stroke=INK, stroke_width='0.4'))
        self.serif(self.w - m - 2, top - 10, 'Pl. %s' % self.pl, 9, INK, italic=True, anchor='end')
        self.serif(self.w / 2, self.h - 12, 'Fig. %s. ' % self.fig, 10, INK, wt=700, anchor='end', caps=False)
        self.serif(self.w / 2, self.h - 12, self.cap, 10, INK, italic=True)
        return (m + 3, top - 3, self.w - m - 3, self.h - bottom + 3)
    def hatch(self, shape_d, angle, gap, w=0.35, color=INK, box=None, opacity=1, cross=None):
        """engraver's tone: parallel lines across a shape (and crossed, if cross is an angle)"""
        cid = self.id('h')
        self.defs.append('<clipPath id="%s"><path d="%s"/></clipPath>' % (cid, shape_d))
        x0, y0, x1, y1 = box or (0, 0, self.w, self.h)
        out = ''
        for ang in ([angle] + ([cross] if cross is not None else [])):
            a = math.radians(ang); dx, dy = math.cos(a), math.sin(a)
            cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
            R = math.hypot(x1 - x0, y1 - y0) / 2 + gap
            k = -R
            while k <= R:
                px, py = cx - dy * k, cy + dx * k
                out += 'M%s %sL%s %s' % (f(px - dx * R), f(py - dy * R), f(px + dx * R), f(py + dy * R))
                k += gap
        self.add('<path d="%s" stroke="%s" stroke-width="%s" fill="none" clip-path="url(#%s)"%s/>' % (out, color, f(w), cid, (' opacity="%s"' % f(opacity)) if opacity < 1 else ''))
    def stipple(self, shape_d, n, box, r=0.45, color=INK, opacity=1):
        cid = self.id('s')
        self.defs.append('<clipPath id="%s"><path d="%s"/></clipPath>' % (cid, shape_d))
        x0, y0, x1, y1 = box
        d = ''.join('M%s %sh.01' % (f(self.rnd.uniform(x0, x1)), f(self.rnd.uniform(y0, y1))) for _ in range(n))
        self.add('<path d="%s" stroke="%s" stroke-width="%s" stroke-linecap="round" clip-path="url(#%s)"%s/>' % (d, color, f(2 * r), cid, (' opacity="%s"' % f(opacity)) if opacity < 1 else ''))
    def tint(self, d, color, op=0.16):
        """a hand-tinted wash: pale, a little outside the line, as a colourist laid it"""
        self.add('<path d="%s" fill="%s" opacity="%s" transform="translate(%s %s)" style="mix-blend-mode:multiply"/>' % (d, color, f(op), f(self.rnd.uniform(-1.5, 1.5)), f(self.rnd.uniform(-1.2, 1.2))))
    def letter(self, x, y, s, size=10):
        self.serif(x, y, s, size, INK, italic=True, anchor='middle')

def box_d(x0, y0, x1, y1): return 'M%s %sH%sV%sH%sZ' % (f(x0), f(y0), f(x1), f(y1), f(x0))

# ---------------------------------------------------------------- A, fig. 1: Metastaseis
def a1():
    S = Plate(560, 360, 'Graph of straight string glissando lines whose bundles form curved envelopes, bars 309 to 314', 11, 'A', 1, 'Metastaseis: glissandi of the strings, bars 309–314')
    S.aged()
    fx0, fy0, fx1, fy1 = S.frame()
    x0, x1, y0, y1 = 60, 528, 34, 286
    # the engraved grid: fine rules, a heavier rule every fifth
    d1_, d2_ = '', ''
    for k in range(0, 41):
        x = x0 + k * (x1 - x0) / 40
        (d1_ if k % 8 else d2_).__add__('')
        if k % 8: d1_ += 'M%s %sV%s' % (f(x), f(y0), f(y1))
        else: d2_ += 'M%s %sV%s' % (f(x), f(y0), f(y1))
    for k in range(0, 26):
        y = y0 + k * (y1 - y0) / 25
        if k % 5: d1_ += 'M%s %sH%s' % (f(x0), f(y), f(x1))
        else: d2_ += 'M%s %sH%s' % (f(x0), f(y), f(x1))
    S.add(path(d1_, stroke=SEPIA, w=0.2, opacity='0.45'), path(d2_, stroke=SEPIA, w=0.45, opacity='0.6'))
    def py(m): return y1 - (m - 31) * (y1 - y0) / (96 - 31)
    def bx(b): return x0 + (b - 309) * (x1 - x0) / 5
    for m in range(36, 97, 12): S.serif(x0 - 6, py(m) + 3, 'C%d' % (m // 12 - 1), 8.5, INK, anchor='end')
    for b in range(309, 315): S.serif(bx(b), y1 + 12, str(b), 8.5, INK, anchor='middle')
    S.serif(26, (y0 + y1) / 2, 'Pitch', 9, INK, italic=True, rot=-90, anchor='middle')
    S.serif((x0 + x1) / 2, y1 + 24, 'Bars (time)', 9, INK, italic=True, anchor='middle')
    S.add(rect(x0, y0, x1 - x0, y1 - y0, 'none', stroke=INK, stroke_width='0.9'))
    # the parts, each section in its own line, as an engraved chart keys them
    sections = [('Violins I', 12, (68, 92), (57, 84), 309.4, 313.6, None, CARMINE), ('Violins II', 12, (60, 84), (80, 58), 309.6, 313.8, '6 2.5', PRUSSIAN),
                ('Violas', 8, (54, 72), (70, 50), 309.8, 314.0, '1 1.8', None), ('Violoncellos', 8, (40, 62), (60, 38), 310.0, 314.0, '7 2 1.2 2', None), ('Basses', 6, (32, 46), (44, 33), 310.2, 314.0, '3 1.5', None)]
    rnd = random.Random(3)
    for name, n, (pa, pb), (qa, qb), t0, t1, dash, tint in sections:
        if tint: S.tint(P([(bx(t0), py(pa)), (bx(t0), py(pb)), (bx(t1), py(qb)), (bx(t1), py(qa))]) + 'Z', tint, 0.1)
        d = ''
        for k in range(n):
            u = k / (n - 1)
            p0, p1 = pa + (pb - pa) * u, qa + (qb - qa) * u
            a0, a1_ = t0 + rnd.uniform(-0.05, 0.05), t1 - rnd.uniform(0, 0.08)
            d += 'M%s %sL%s %s' % (f(bx(a0)), f(py(p0)), f(bx(a1_)), f(py(p1)))
            S.add(circle(bx(a0), py(p0), 1.2, INK), circle(bx(a1_), py(p1), 1.2, INK))
        S.ink(path(d, stroke=INK, w=0.6, **({'stroke_dasharray': dash} if dash else {})))
    # the key, boxed
    kx, ky = x1 - 120, y0 + 8
    S.add(rect(kx, ky, 112, 68, PAPER), rect(kx, ky, 112, 68, 'none', stroke=INK, stroke_width='0.6'))
    S.serif(kx + 56, ky + 11, 'Key', 9, INK, italic=True, anchor='middle')
    for k, (name, n, *rest) in enumerate(sections):
        dash = rest[4]
        S.add(line(kx + 8, ky + 21 + k * 10, kx + 30, ky + 21 + k * 10, INK, 0.8, **({'stroke_dasharray': dash} if dash else {})))
        S.serif(kx + 36, ky + 24 + k * 10, '%s, %d' % (name, n), 8, INK)
    S.grain(0.8)
    S.save('a1')

# ---------------------------------------------------------------- A, fig. 2: the Pavilion
def a2():
    S = Plate(420, 280, 'An engraved view of a tent-like pavilion built from ruled, saddle-shaped concrete shells', 21, 'A', 2, 'Pavillon Philips, Bruxelles, 1958')
    S.aged()
    fx0, fy0, fx1, fy1 = S.frame(26, 34)
    ix, iy, iw, ih = fx0 + 4, fy0 + 4, fx1 - fx0 - 8, fy1 - fy0 - 8
    gy = iy + ih * 0.8
    # the sky: horizontal engraved lines, closer and darker toward the top
    d = ''
    y = iy + 2; gap = 1.6
    while y < gy - 20:
        d += 'M%s %sH%s' % (f(ix), f(y), f(ix + iw)); y += gap; gap *= 1.07
    S.add(path(d, stroke=INK, w=0.25, opacity='0.55'))
    # the ground: lines closing toward the horizon
    d = ''
    for k in range(18):
        y = gy + (iy + ih - gy) * (k / 17) ** 1.6
        d += 'M%s %sH%s' % (f(ix), f(y), f(ix + iw))
    S.add(path(d, stroke=INK, w=0.35, opacity='0.7'))
    def L(p, q, t): return (p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t)
    def shell(a, b, c, dd, n, shade):
        quad = P([a, b, c, dd]) + 'Z'
        S.add(path(quad, fill=PAPER))
        r1, r2 = '', ''
        for i in range(n + 1):
            t = i / n
            p, q = L(a, b, t), L(dd, c, t); r1 += 'M%s %sL%s %s' % (f(p[0]), f(p[1]), f(q[0]), f(q[1]))
            p, q = L(a, dd, t), L(b, c, t); r2 += 'M%s %sL%s %s' % (f(p[0]), f(p[1]), f(q[0]), f(q[1]))
        S.add(path(r1, stroke=INK, w=0.35, opacity='0.85'), path(r2, stroke=INK, w=0.3, opacity='0.5'))
        if shade: S.hatch(quad, 72, shade, 0.3, INK, box=(ix, iy, ix + iw, iy + ih), opacity=0.7)
        S.add(path(quad, stroke=INK, w=0.9, stroke_linejoin='round'))
    A, B, C, D = (ix + 64, gy), (ix + 140, iy + 62), (ix + 190, gy - 7), (ix + 152, gy)
    E, F = (ix + 254, iy + 14), (ix + 286, gy - 4)
    G, H = (ix + 336, gy), (ix + 306, gy)
    # the cast shadow, cross-hatched across the ground
    S.hatch(P([(ix + 64, gy), (ix + 336, gy), (ix + iw, gy + 18), (ix + 140, gy + 20)]) + 'Z', 0, 1.2, 0.35, INK, box=(ix, gy, ix + iw, iy + ih), cross=35)
    shell(A, B, C, D, 22, None)
    shell(B, E, F, C, 26, None)
    shell(E, G, H, F, 18, 2.0)
    for px in (ix + 46, ix + 54, ix + 200, ix + 206, ix + 350):
        S.add(path('M%s %sl-1.8 8.5h3.6z' % (f(px), f(gy + 0.6)), fill=INK), circle(px, gy - 1, 1.5, INK))
    # lettered: the peaks
    S.letter(B[0] - 7, B[1] - 3, 'a'); S.letter(E[0] + 6, E[1] - 2, 'b'); S.letter(C[0] + 3, C[1] - 6, 'c')
    S.grain(0.9)
    S.save('a2')

# ---------------------------------------------------------------- B: Pithoprakta
def b1():
    S = Plate(560, 340, 'A cloud of short sloping glissando strokes and pizzicato dots, denser in the middle', 31, 'B', 3, 'Pithoprakta: a cloud of glissandi, after the graphs')
    S.aged()
    fx0, fy0, fx1, fy1 = S.frame()
    x0, x1, y0, y1 = 52, 530, 36, 276
    S.add(line(x0, y0, x0, y1, INK, 0.9), line(x0, y1, x1, y1, INK, 0.9))
    for k in range(0, 11): S.add(line(x0 + k * (x1 - x0) / 10, y1, x0 + k * (x1 - x0) / 10, y1 + 4, INK, 0.6))
    S.serif(34, (y0 + y1) / 2, 'Pitch', 9, INK, italic=True, rot=-90, anchor='middle')
    S.serif(x1, y1 + 16, 'Time', 9, INK, italic=True, anchor='end')
    S.letter(x0 - 8, y1 + 10, 'O')
    rnd = random.Random(1956)
    # three planes: the strokes behind are finer, as an engraver lightens a distance
    for plane, (n, w) in enumerate(((220, 0.35), (200, 0.6), (160, 0.95))):
        d = ''
        for k in range(n):
            tx = min(max(rnd.gauss(0.5, 0.2), 0.02), 0.96); ty = min(max(rnd.gauss(0.5, 0.22), 0.04), 0.96)
            v = math.sqrt(sum(rnd.gauss(0, 1) ** 2 for _ in range(3)))
            ang = math.atan(v * 0.55) * rnd.choice((-1, 1))
            Lg = rnd.uniform(9, 19)
            x, y = x0 + tx * (x1 - x0), y1 - ty * (y1 - y0)
            d += 'M%s %sl%s %s' % (f(x), f(y), f(Lg * math.cos(ang)), f(-Lg * math.sin(ang)))
        S.ink(path(d, stroke=INK, w=w, stroke_linecap='round', opacity=f(0.55 + 0.2 * plane)))
    dots = ''.join('M%s %sh.01' % (f(x0 + min(max(rnd.gauss(0.5, 0.28), 0.02), 0.98) * (x1 - x0)), f(y1 - min(max(rnd.gauss(0.5, 0.3), 0.03), 0.97) * (y1 - y0))) for _ in range(130))
    S.ink(path(dots, stroke=INK, w=2.4, stroke_linecap='round'))
    # fig. 3a: the law of the speeds, its area cross-hatched
    ix, iy, iw, ih = x1 - 176, y0 + 12, 168, 82
    S.add(rect(ix, iy, iw, ih, PAPER), rect(ix, iy, iw, ih, 'none', stroke=INK, stroke_width='0.6'))
    pts = []
    for k in range(61):
        v = k / 60 * 4
        p = math.sqrt(2 / math.pi) * v * v * math.exp(-v * v / 2)
        pts.append((ix + 16 + v / 4 * (iw - 26), iy + ih - 18 - p / 0.6 * (ih - 36)))
    area = P(pts + [(pts[-1][0], iy + ih - 18), (pts[0][0], iy + ih - 18)]) + 'Z'
    S.hatch(area, 45, 1.6, 0.3, INK, box=(ix, iy, ix + iw, iy + ih))
    S.add(path(P(pts), stroke=INK, w=0.9), line(ix + 16, iy + ih - 18, ix + iw - 8, iy + ih - 18, INK, 0.6), line(ix + 16, iy + ih - 18, ix + 16, iy + 14, INK, 0.6))
    S.serif(ix + iw - 8, iy + ih - 8, 'v', 9, INK, italic=True, anchor='end')
    S.serif(ix + 20, iy + 18, 'f(v)', 9, INK, italic=True)
    S.serif(ix + iw, iy - 4, 'Fig. 3a. Law of speeds (Maxwell)', 7.5, INK, italic=True, anchor='end')
    S.serif(x0 + 10, y0 + 12, 'Strokes: glissandi.  Points: pizzicati.', 8.5, INK, italic=True)
    S.grain(0.8)
    S.save('b1')

# ---------------------------------------------------------------- C: Arborescences
def c1():
    S = Plate(560, 320, 'A single line branching like a tree from left to right, with its inversion dotted beneath', 41, 'C', 4, 'An arborescence, and its inversion')
    S.aged()
    S.frame()
    y_mid = 152
    rnd = random.Random(1973)
    paths = []
    def grow(x, y, dy, depth, w):
        Lg = rnd.uniform(38, 60)
        nx, ny = x + Lg, y + dy * Lg + rnd.uniform(-5, 5)
        if ny < 70: ny, dy = 70 + (70 - ny) * 0.3, abs(dy) * 0.6
        elif ny > 236: ny, dy = 236 - (ny - 236) * 0.3, -abs(dy) * 0.6
        paths.append((x, y, nx, ny, w, depth))
        if nx > 520 or depth > 6: return
        k = rnd.choice((2, 3)) if depth < 2 else rnd.choice((1, 1, 1, 2))
        for i in range(k):
            ndy = dy * 0.55 + rnd.uniform(-0.3, 0.3) + (i - (k - 1) / 2) * 0.5
            grow(nx, ny, max(-0.6, min(0.6, ndy)), depth + 1, max(0.55, w * 0.8))
    paths.append((34, y_mid, 74, y_mid, 2.0, 0))
    grow(74, y_mid, 0.0, 0, 1.8)
    def curve(x, y, nx, ny): return 'M%s %sC%s %s %s %s %s %s' % (f(x), f(y), f(x + (nx - x) * 0.45), f(y), f(x + (nx - x) * 0.55), f(ny), f(nx), f(ny))
    S.add(line(30, y_mid, 534, y_mid, INK, 0.4, stroke_dasharray='1 2.5', opacity='0.6'))
    S.serif(532, y_mid - 4, 'axis of inversion', 7.5, INK, italic=True, anchor='end')
    # the inversion, dotted, as a construction is drawn
    S.add(path(''.join(curve(x, 2 * y_mid - y, nx, 2 * y_mid - ny) for x, y, nx, ny, w, dep in paths if dep < 4), stroke=INK, w=0.5, stroke_dasharray='0.8 1.6', opacity='0.55'))
    for w in sorted(set(round(p[4], 1) for p in paths)):
        S.ink(path(''.join(curve(x, y, nx, ny) for x, y, nx, ny, ww, dep in paths if round(ww, 1) == w), stroke=INK, w=w * 0.8, stroke_linecap='round'))
    # the branch points of the first orders, lettered
    marks = sorted([(x, y) for x, y, nx, ny, w, dep in paths if dep in (1, 2)])[:6]
    for k, (x, y) in enumerate(marks):
        S.add(circle(x, y, 2.2, PAPER), circle(x, y, 2.2, 'none', stroke=INK, stroke_width='0.7'))
        S.letter(x + 1, y - 5, 'abcdef'[k], 9)
    S.add(circle(34, y_mid, 2.4, INK)); S.letter(30, y_mid - 6, 'O', 9)
    S.add(line(34, 268, 200, 268, INK, 0.6), path('M200 268l-5 -2.4v4.8z', fill=INK))
    S.serif(206, 271, 't', 9, INK, italic=True)
    S.grain(0.8)
    S.save('c1')

# ---------------------------------------------------------------- D: Nomos Alpha (after Byrne)
def d1():
    S = Plate(440, 330, 'A cube with vertices numbered 1 to 8 and three dashed rotation axes: through faces, through a diagonal, through edges', 51, 'D', 5, 'The cube and its axes of rotation')
    S.aged()
    S.frame(26, 32)
    cx, cy, a = 196, 178, 104
    ox, oy = 46, -38
    V = {1: (cx - a / 2, cy + a / 2), 2: (cx + a / 2, cy + a / 2), 3: (cx + a / 2, cy - a / 2), 4: (cx - a / 2, cy - a / 2)}
    for k in range(4): V[k + 5] = (V[k + 1][0] + ox, V[k + 1][1] + oy)
    ext = lambda p, q, t: (p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t)
    fc = ((V[1][0] + V[7][0]) / 2, (V[1][1] + V[7][1]) / 2)
    m1 = ((V[1][0] + V[5][0]) / 2, (V[1][1] + V[5][1]) / 2); m2 = ((V[3][0] + V[7][0]) / 2, (V[3][1] + V[7][1]) / 2)
    axes = [((fc[0], fc[1] - 108), (fc[0], fc[1] + 104), 'A', "A’"), (ext(V[1], V[7], -0.32), ext(V[1], V[7], 1.32), 'B', "B’"), (ext(m1, m2, -0.42), ext(m1, m2, 1.42), 'C', "C’")]
    for p, q, l1, l2 in axes: S.add(line(p[0], p[1], q[0], q[1], INK, 0.6, stroke_dasharray='7 2 1.5 2', opacity='0.5'))
    # Byrne's flat colours: the front face red, the top yellow, the side blue
    faces = [(P([V[1], V[2], V[3], V[4]]) + 'Z', BYRNE['red']), (P([V[4], V[3], V[7], V[8]]) + 'Z', BYRNE['yellow']), (P([V[2], V[6], V[7], V[3]]) + 'Z', BYRNE['blue'])]
    for d, c in faces: S.add(path(d, fill=c, opacity='0.92'))
    S.ink(path(''.join('M%s %sL%s %s' % (f(V[p][0]), f(V[p][1]), f(V[q][0]), f(V[q][1])) for p, q in ((1, 5), (5, 6), (5, 8))), stroke=INK, w=0.9, stroke_dasharray='3 2.5'))
    S.ink(path(''.join('M%s %sL%s %s' % (f(V[p][0]), f(V[p][1]), f(V[q][0]), f(V[q][1])) for p, q in ((1, 2), (2, 3), (3, 4), (4, 1), (2, 6), (3, 7), (4, 8), (6, 7), (7, 8))), stroke=INK, w=2.6, stroke_linejoin='round'))
    for p, q, l1, l2 in axes:
        for t0, t1 in ((0.0, 0.22), (0.78, 1.0)):
            A_, B_ = ext(p, q, t0), ext(p, q, t1)
            S.add(line(A_[0], A_[1], B_[0], B_[1], INK, 1.0, stroke_dasharray='7 2 1.5 2'))
        S.letter(p[0] - 6, p[1] + 4, l1, 11); S.letter(q[0] + 7, q[1] + 3, l2, 11)
    # the turns about A and B, small arcs with arrow heads
    for (x, y) in ((fc[0], fc[1] - 92), ext(V[1], V[7], 1.2)):
        S.add(path('M%s %sa13 4.5 0 1 1 -2 0.6' % (f(x + 13), f(y)), stroke=INK, w=0.8), path('M%s %sl-4.4 -2.8l0.6 5z' % (f(x + 11.4), f(y + 0.8)), fill=INK))
    for k, (x, y) in V.items():
        S.add(circle(x, y, 7.6, PAPER), circle(x, y, 7.6, 'none', stroke=INK, stroke_width='0.9'))
        S.serif(x, y + 3.6, str(k), 10, INK, italic=True, anchor='middle')
    for k, t in enumerate(('AA’, through faces: 90°, 180°, 270°', 'BB’, through corners: 120°, 240°', 'CC’, through edges: 180°')):
        S.serif(296, 232 + k * 12, t, 8, INK, italic=True)
    S.serif(296, 274, 'Rotations: 1 + 3·3 + 4·2 + 6·1 = 24', 8, INK)
    S.grain(0.7)
    S.save('d1')

# ---------------------------------------------------------------- E: three sieves
def e1():
    S = Plate(600, 300, "Three sieves drawn on lines: a seventeen-semitone scale, a forty-pulse rhythm, and the sample deck's sieve 2 3 7 8 12 13 17 18", 61, 'E', 6, 'Three sieves: of pitch, of rhythm, of the integers')
    S.aged()
    S.frame(24, 32)
    def brace(x0, x1, y, label):
        m = (x0 + x1) / 2
        S.add(path('M%s %sq0 4 4 4H%sq4 0 4 4q0 -4 4 -4H%sq4 0 4 -4' % (f(x0), f(y), f(m - 4), f(m + 4) if False else f(x1 - 4)), stroke=INK, w=0.6) if False else '')
        S.add(path('M%s %sQ%s %s %s %s T%s %s M%s %sQ%s %s %s %s T%s %s' % (f(x0), f(y), f(x0), f(y + 4), f((x0 + m) / 2), f(y + 4), f(m), f(y + 8),
                                                                          f(x1), f(y), f(x1), f(y + 4), f((x1 + m) / 2), f(y + 4), f(m), f(y + 8)), stroke=INK, w=0.6))
        S.serif(m, y + 18, label, 8, INK, italic=True, anchor='middle')
    S.serif(30, 42, 'a.', 9, INK, wt=700); S.serif(44, 42, 'Jonchaies: the scale 17@{0, 1, 4, 5, 7, 11, 12, 16}, in semitones', 9, INK, italic=True)
    mem = {0, 1, 4, 5, 7, 11, 12, 16}
    x, w, y = 30, 15.8, 50
    for k in range(34):
        on = (k % 17) in mem
        d = box_d(x + k * w, y, x + k * w + w - 1.6, y + 30)
        if on: S.add(path(d, fill=INK))
        else: S.add(path(d, fill=PAPER)); S.hatch(d, 90, 1.5, 0.25, INK, box=(x + k * w, y, x + k * w + w, y + 30), opacity=0.35)
        S.add(path(d, stroke=INK, w=0.5))
    brace(x, x + 17 * w - 1.6, y + 34, 'one period: 17 semitones (an octave and a fourth)')
    brace(x + 17 * w, x + 34 * w - 1.6, y + 34, 'the period repeated')
    S.serif(30, 146, 'b.', 9, INK, wt=700); S.serif(44, 146, 'Psappha: the sieve of the first 40 pulses (after Flint), moduli 8 and 5', 9, INK, italic=True)
    rm = {0, 1, 3, 4, 6, 8, 10, 11, 12, 13, 14, 16, 17, 19, 20, 22, 23, 25, 27, 28, 29, 31, 33, 35, 36, 37, 38}
    y = 166
    S.add(line(30, y, 580, y, INK, 0.5))
    for k in range(40):
        px = 36 + k * 13.6
        S.add(line(px, y - 3, px, y + 3, INK, 0.4))
        if k in rm: S.add(circle(px, y, 4.2, INK), circle(px - 1.3, y - 1.4, 1.0, PAPER, opacity='0.6'))
        if k % 8 == 0: S.serif(px, y + 16, str(k), 8, INK, anchor='middle')
    S.serif(30, 214, 'c.', 9, INK, wt=700); S.serif(44, 214, 'The sample deck: 5@2 | 5@3, on the integers 0 to 19', 9, INK, italic=True)
    y = 224
    for k in range(20):
        on = k % 5 in (2, 3)
        d = box_d(30 + k * 22, y, 48 + k * 22, y + 18)
        S.add(path(d, fill=PAPER))
        if on: S.hatch(d, 45, 1.3, 0.45, INK, box=(30 + k * 22, y, 48 + k * 22, y + 18), cross=-45)
        S.add(path(d, stroke=INK, w=0.6))
        S.serif(39 + k * 22, y + 30, str(k), 8, INK, anchor='middle')
    S.serif(482, 238, '= 2, 3, 7, 8, 12, 13, 17, 18', 9, INK, italic=True)
    S.grain(0.8)
    S.save('e1')

# ---------------------------------------------------------------- F: a UPIC page, as a Marey tracing
def f1():
    S = Plate(560, 320, 'A page of drawn wavy arcs in bundles, pitch against time, as white tracings on smoked paper', 71, 'F', 7, 'Tracings of a UPIC page, after the graphic method')
    S.aged()
    fx0, fy0, fx1, fy1 = S.frame()
    x0, y0, x1, y1 = fx0 + 6, fy0 + 6, fx1 - 6, fy1 - 22
    # smoked paper: soot, unevenly laid, varnished to a brown
    S.add(rect(x0, y0, x1 - x0, y1 - y0, '#1d1814'))
    S.add(rect(x0, y0, x1 - x0, y1 - y0, S.rad([(0, '#4a3a2a', 0.5), (1, '#000', 0)], 0.4, 0.4, 0.8)))
    S.add('<rect x="%s" y="%s" width="%s" height="%s" filter="url(#tooth)" opacity="0.5" style="mix-blend-mode:screen"/>' % (f(x0), f(y0), f(x1 - x0), f(y1 - y0)))
    # the time marks, scratched along the top by a chronograph, a tooth every second
    d = 'M%s %sH%s' % (f(x0 + 6), f(y0 + 10), f(x1 - 6))
    for k in range(0, 61):
        xx = x0 + 6 + k * (x1 - x0 - 12) / 60
        d += 'M%s %sV%s' % (f(xx), f(y0 + 10), f(y0 + (6 if k % 5 == 0 else 8)))
    S.add(path(d, stroke='#efe3c8', w=0.5, opacity='0.85'))
    rnd = random.Random(1978)
    bundles = [(40, 220, 260, 120, 9, 0.8, -0.9), (180, 70, 380, 160, 7, 1.0, 1.2), (300, 230, 520, 200, 8, 0.6, 0.6),
               (80, 110, 200, 60, 5, 1.2, -1.6), (360, 60, 520, 90, 6, 0.9, 1.0), (230, 250, 330, 262, 4, 0.5, 2.0)]
    for xs, ys, xe, ye, n, amp, freq in bundles:
        d = ''
        for k in range(n):
            off = (k - n / 2) * 3.0
            ph = rnd.uniform(0, 1)
            pts = [(xs + (xe - xs) * t, ys + (ye - ys) * t + off + amp * 18 * math.sin(2 * math.pi * (freq * t + ph * 0.15)) * (0.6 + 0.4 * t)) for t in [s_ / 47 for s_ in range(48)]]
            d += taper(pts, rnd.uniform(0.7, 1.3), 0.25, 0.25, 0.6)
        S.ink(path(d, fill='#f4ead2', opacity='0.92'))
    S.serif(x0 + 4, y1 + 14, 'Time, in seconds, above; pitch rising upward.', 8.5, INK, italic=True)
    S.grain(0.6)
    S.save('f1')

# ---------------------------------------------------------------- I: Achorripsis
def i1():
    S = Plate(640, 330, 'A matrix of 28 columns of time by 7 rows of timbre; most of its 196 cells are empty, and the rest hold 1, 2, 3 or, once, 4 events', 81, 'I', 8, 'Achorripsis: events in each cell of the matrix')
    S.aged()
    S.frame(24, 32)
    x0, y0, cw, ch = 82, 50, 19.4, 25
    counts = [0] * 107 + [1] * 65 + [2] * 19 + [3] * 4 + [4] * 1
    rnd = random.Random(1957); rnd.shuffle(counts)
    S.serif(x0 + 14 * cw, 32, 'Time (columns 1 to 28)', 9, INK, italic=True, anchor='middle')
    for c in range(28):
        if c % 2 == 0 or c == 27: S.serif(x0 + c * cw + cw / 2, 44, str(c + 1), 7.5, INK, anchor='middle')
    S.serif(34, y0 + 3.5 * ch, 'Timbre', 9, INK, italic=True, rot=-90, anchor='middle')
    roman = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII']
    def tone(d, v, bx):
        if v == 1: S.hatch(d, 45, 2.4, 0.3, INK, box=bx)
        elif v == 2: S.hatch(d, 45, 1.8, 0.35, INK, box=bx, cross=-45)
        elif v == 3: S.hatch(d, 45, 1.1, 0.45, INK, box=bx, cross=-45)
        elif v == 4: S.add(path(d, fill=INK))
    for r in range(7):
        S.serif(x0 - 8, y0 + r * ch + ch / 2 + 3.5, roman[r], 9, INK, anchor='end')
        for c in range(28):
            v = counts[r * 28 + c]
            bx = (x0 + c * cw, y0 + r * ch, x0 + (c + 1) * cw, y0 + (r + 1) * ch)
            if v:
                tone(box_d(*bx), v, bx)
                lab = (bx[0] + cw / 2, bx[1] + ch / 2)
                S.add(circle(lab[0], lab[1], 4.6, PAPER if v < 4 else INK))
                S.serif(lab[0], lab[1] + 3.4, str(v), 9, INK if v < 4 else PAPER, wt=700, anchor='middle')
    grid = ''.join('M%s %sV%s' % (f(x0 + c * cw), f(y0), f(y0 + 7 * ch)) for c in range(29)) + ''.join('M%s %sH%s' % (f(x0), f(y0 + r * ch), f(x0 + 28 * cw)) for r in range(8))
    S.add(path(grid, stroke=INK, w=0.45))
    S.add(rect(x0 - 2.5, y0 - 2.5, 28 * cw + 5, 7 * ch + 5, 'none', stroke=INK, stroke_width='1.4'), rect(x0, y0, 28 * cw, 7 * ch, 'none', stroke=INK, stroke_width='0.6'))
    ly = y0 + 7 * ch + 24
    S.serif(x0, ly, 'Events in a cell:', 8.5, INK, italic=True)
    for k, (v, n) in enumerate(((0, 107), (1, 65), (2, 19), (3, 4), (4, 1))):
        lx = x0 + 92 + k * 92
        bx = (lx, ly - 9, lx + 12, ly + 3)
        S.add(path(box_d(*bx), fill=PAPER)); tone(box_d(*bx), v, bx); S.add(path(box_d(*bx), stroke=INK, w=0.6))
        S.serif(lx + 17, ly + 1, '%d, in %d cells' % (v, n), 8.5, INK)
    S.serif(x0, ly + 20, 'Poisson’s law, with a mean of 0·6 events to a cell, over 196 cells.', 8.5, INK, italic=True)
    S.grain(0.8)
    S.save('i1')

# ---------------------------------------------------------------- J: the Analogique screens
def j1():
    S = Plate(640, 344, 'Eight small figures lettered A to H, each a grid of six pitch regions by three dynamics holding a few short notes', 91, 'J', 9, 'The eight screens of Analogique A')
    S.aged()
    S.frame(24, 30)
    rnd = random.Random(1958)
    F = {0: (0, 1, 4, 5), 1: (2, 3)}
    G = {0: (0, 0, 1, 2), 1: (0, 1)}
    Dn = {0: (1, 1, 3, 9), 1: (1, 3, 3, 9)}
    for k in range(8):
        fset, gset, dset = (k >> 2) & 1, (k >> 1) & 1, k & 1
        col, row = k % 4, k // 4
        x, y, w, h = 44 + col * 146, 40 + row * 146, 118, 102
        rh, cw = h / 6, w / 3
        for r in range(6):
            yy = y + h - (r + 1) * rh
            if r in F[fset]:
                d = box_d(x, yy, x + w, yy + rh)
                S.hatch(d, 0, 1.4, 0.2, INK, box=(x, yy, x + w, yy + rh), opacity=0.45)
            S.serif(x - 4, yy + rh / 2 + 2.6, 'I II III IV V VI'.split()[r], 6, INK, anchor='end')
        S.add(path(''.join('M%s %sH%s' % (f(x), f(y + r * rh), f(x + w)) for r in range(1, 6)) + ''.join('M%s %sV%s' % (f(x + c * cw), f(y), f(y + h)) for c in (1, 2)), stroke=INK, w=0.35))
        S.add(rect(x, y, w, h, 'none', stroke=INK, stroke_width='0.9'))
        d = ''
        for r in F[fset]:
            c = rnd.choice(G[gset]); n = rnd.choice(Dn[dset])
            wgt = (0.9, 1.6, 2.4)[c]
            for g_ in range(n):
                gx = x + c * cw + 3 + rnd.random() * (cw - 11); gy = y + h - (r + 0.25 + rnd.random() * 0.5) * rh
                S.add(line(gx, gy, gx + rnd.uniform(4, 7), gy, INK, wgt, stroke_linecap='round'))
        for c, dyn in enumerate(('pp', 'f', 'fff')): S.serif(x + c * cw + cw / 2, y + h + 10, dyn, 8.5, INK, italic=True, wt=700, anchor='middle')
        S.serif(x, y - 5, '%s.' % 'ABCDEFGH'[k], 9, INK, wt=700)
        S.serif(x + w, y - 5, 'f%d g%d d%d' % (fset, gset, dset), 8, INK, italic=True, anchor='end')
    S.grain(0.8)
    S.save('j1')

# ---------------------------------------------------------------- L: Terretektorh
def l1():
    S = Plate(520, 470, 'Plan of a round hall: 88 players, marked by section, are scattered through rings of audience seats', 101, 'L', 10, 'Terretektorh: plan of the hall')
    S.aged()
    S.frame(26, 32)
    cx, cy, R = 260, 212, 172
    # the wall: a thick ring, cross-hatched, as walls are in an engraved plan
    ring = 'M%s %sa%s %s 0 1 0 %s 0a%s %s 0 1 0 %s 0ZM%s %sa%s %s 0 1 1 %s 0a%s %s 0 1 1 %s 0Z' % (
        f(cx - R - 7), f(cy), f(R + 7), f(R + 7), f(2 * R + 14), f(R + 7), f(R + 7), f(-2 * R - 14), f(cx - R), f(cy), f(R), f(R), f(2 * R), f(R), f(R), f(-2 * R))
    S.add(path(ring, fill=PAPER, fill_rule='evenodd'))
    S.hatch(ring, 45, 1.3, 0.4, INK, box=(cx - R - 8, cy - R - 8, cx + R + 8, cy + R + 8), cross=-45)
    S.add(circle(cx, cy, R + 7, 'none', stroke=INK, stroke_width='1.2'), circle(cx, cy, R, 'none', stroke=INK, stroke_width='0.8'))
    rnd = random.Random(1966)
    cand = []
    for r in range(28, int(R) - 6, 13):
        n = int(2 * math.pi * r / 10)
        for k in range(n):
            a = 2 * math.pi * k / n
            if any(abs(((a - ax + math.pi) % (2 * math.pi)) - math.pi) < 7 / r for ax in (0, math.pi / 2, math.pi, 3 * math.pi / 2)): continue
            cand.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    rnd.shuffle(cand)
    players, seats = cand[:88], cand[88:]
    S.add(path(''.join('M%s %sh2.4v2.4h-2.4z' % (f(x - 1.2), f(y - 1.2)) for x, y in seats), fill='none', stroke=INK, stroke_width='0.35', opacity='0.7'))
    kinds = ['s'] * 60 + ['w'] * 12 + ['b'] * 13 + ['p'] * 3
    rnd.shuffle(kinds)
    marks = {'s': '', 'w': '', 'b': '', 'p': ''}
    for (x, y), kd in zip(players, kinds):
        if kd == 's': marks[kd] += 'M%s %sa3.3 3.3 0 1 0 0.01 0' % (f(x - 3.3), f(y))
        elif kd == 'w': marks[kd] += 'M%s %sl4 6.6h-8z' % (f(x), f(y - 4.4))
        elif kd == 'b': marks[kd] += 'M%s %sh6.6v6.6h-6.6z' % (f(x - 3.3), f(y - 3.3))
        else: marks[kd] += 'M%s %sl5 5-5 5-5-5z' % (f(x), f(y - 5))
    S.add(path(marks['s'], fill=INK), path(marks['w'], fill=PAPER, stroke=INK, stroke_width='1'), path(marks['b'], fill=INK), path(marks['p'], fill=PAPER, stroke=INK, stroke_width='1.1'))
    # the conductor at the centre, with a compass rose of the four aisles
    for a in range(4):
        ang = a * math.pi / 2
        S.add(path('M%s %sL%s %sL%s %sZ' % (f(cx + 16 * math.cos(ang)), f(cy + 16 * math.sin(ang)), f(cx + 3 * math.cos(ang + 0.8)), f(cy + 3 * math.sin(ang + 0.8)), f(cx + 3 * math.cos(ang - 0.8)), f(cy + 3 * math.sin(ang - 0.8))), fill=INK))
    S.add(circle(cx, cy, 2.4, PAPER, stroke=INK, stroke_width='0.8'))
    S.letter(cx + 22, cy - 8, 'Conductor', 8.5)
    # a scale of the plan, and the explanation of the signs
    ly = 418
    S.serif(42, ly - 12, 'Explanation of the signs', 9, INK, italic=True)
    for k, (kd, lab) in enumerate((('s', 'Strings, 60'), ('w', 'Woodwinds, 12'), ('b', 'Brass, 13'), ('p', 'Percussion, 3'))):
        lx = 50 + k * 112
        if kd == 's': S.add(circle(lx, ly - 3, 3.4, INK))
        elif kd == 'w': S.add(path('M%s %sl4 6.6h-8z' % (f(lx), f(ly - 7)), fill=PAPER, stroke=INK, stroke_width='1'))
        elif kd == 'b': S.add(rect(lx - 3.3, ly - 6.3, 6.6, 6.6, INK))
        else: S.add(path('M%s %sl5 5-5 5-5-5z' % (f(lx), f(ly - 8)), fill=PAPER, stroke=INK, stroke_width='1.1'))
        S.serif(lx + 9, ly, lab, 8.5, INK)
    S.add(path('M%s %sh%s' % (f(42), f(ly + 12), f(14)), stroke=INK, w=0.4), path('M42 %sh60' % f(ly + 14), stroke=INK, w=1.6, stroke_dasharray='10 10'))
    S.serif(108, ly + 17, 'seats of the audience, open squares', 8, INK, italic=True)
    S.grain(0.8)
    S.save('l1')

if __name__ == '__main__':
    import sys
    for k in (sys.argv[1:] or ['a1', 'a2', 'b1', 'c1', 'd1', 'e1', 'f1', 'i1', 'j1', 'l1']): globals()[k]()
