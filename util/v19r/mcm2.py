# A richer vocabulary on top of mcm.py, for v21's second drawing of the room: one light from
# the upper left, gradients for the turn of a form, materials (wood with its figure, brushed
# aluminium, enamel and glaze with their gloss, gilt), contact shadows and rim lights, and
# small hardware (screws, knurled knobs). Gradients and clips are collected in a Defs.
import math, random
from mcm import *

class Defs:
    def __init__(self): self.items = []; self.n = 0
    def add(self, s): self.items.append(s)
    def id(self, p='d'): self.n += 1; return '%s%d' % (p, self.n)
    def lin(self, stops, x1=0, y1=0, x2=0, y2=1, units='objectBoundingBox'):
        i = self.id('lg')
        st = ''.join('<stop offset="%s" stop-color="%s"%s/>' % (f(o), c, (' stop-opacity="%s"' % f(a)) if a < 1 else '') for o, c, a in [(s + (1,))[:3] if len(s) == 2 else s for s in stops])
        self.add('<linearGradient id="%s" gradientUnits="%s" x1="%s" y1="%s" x2="%s" y2="%s">%s</linearGradient>' % (i, units, f(x1), f(y1), f(x2), f(y2), st))
        return 'url(#%s)' % i
    def rad(self, stops, cx=0.5, cy=0.5, r=0.5, fx=None, fy=None, units='objectBoundingBox'):
        i = self.id('rg')
        st = ''.join('<stop offset="%s" stop-color="%s"%s/>' % (f(o), c, (' stop-opacity="%s"' % f(a)) if a < 1 else '') for o, c, a in [(s + (1,))[:3] if len(s) == 2 else s for s in stops])
        self.add('<radialGradient id="%s" gradientUnits="%s" cx="%s" cy="%s" r="%s" fx="%s" fy="%s">%s</radialGradient>' % (i, units, f(cx), f(cy), f(r), f(cx if fx is None else fx), f(cy if fy is None else fy), st))
        return 'url(#%s)' % i
    def clip(self, shape):
        i = self.id('cp'); self.add('<clipPath id="%s">%s</clipPath>' % (i, shape)); return 'url(#%s)' % i
    def blur(self, sd):
        i = self.id('bl'); self.add('<filter id="%s" x="-50%%" y="-50%%" width="200%%" height="200%%"><feGaussianBlur stdDeviation="%s"/></filter>' % (i, f(sd))); return 'url(#%s)' % i
    def out(self): return ''.join(self.items)

def soft_shadow(D, shape_d, dx=0, dy=0, sd=1.5, op=0.3, color='#1c140c'):
    return path(shape_d, color, opacity=op, filter=D.blur(sd), transform='translate(%s %s)' % (f(dx), f(dy)))

def ellipse(cx, cy, rx, ry, fill, **kw):
    return '<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="%s"%s/>' % (f(cx), f(cy), f(rx), f(ry), fill, attrs(**kw))

# ---- wood: tone streaks along the grain, the grain's lines wandering with a few cathedral
# arches, and pores as broken dashes ----------------------------------------------------
def wood(D, x, y, w, h, base, seed=1, vertical=False, lines=None, contrast=1.0, arches=1):
    rnd = random.Random(seed)
    L, T = (h, w) if vertical else (w, h)     # along and across the grain
    out = [rect(x, y, w, h, base)]
    # streaks: wide soft bands of lighter and darker wood
    stops = []
    for k in range(9):
        o = k / 8
        c = light(base, 0.08 * contrast) if rnd.random() < 0.5 else dark(base, 0.1 * contrast)
        stops.append((o, c, 0.55))
    g_ = D.lin(stops, 0, 0, 1, 0) if vertical else D.lin(stops, 0, 0, 0, 1)
    out.append(rect(x, y, w, h, g_))
    n = lines or max(6, int(T / 1.1))
    gl = []
    for i in range(n):
        off = (i + rnd.uniform(-0.3, 0.3)) / n * T
        amp = rnd.uniform(0.2, 0.9) * (T / n)
        ph = rnd.uniform(0, 6.28); k = rnd.uniform(0.6, 1.6) * 2 * math.pi / L
        pts = []
        for s in range(0, 41):
            u = s / 40 * L
            v = off + amp * math.sin(k * u + ph) + amp * 0.4 * math.sin(2.7 * k * u + ph * 1.3)
            pts.append((x + v, y + u) if vertical else (x + u, y + v))
        d = 'M' + ' L'.join('%s,%s' % (f(a), f(b)) for a, b in pts)
        c = dark(base, rnd.uniform(0.12, 0.3) * contrast)
        gl.append(path(d, 'none', stroke=c, stroke_width=f(rnd.uniform(0.12, 0.3)), opacity=f(rnd.uniform(0.35, 0.8))))
    # cathedral arches: nested parabolas pointing along the grain
    for a in range(arches):
        cu, cv = rnd.uniform(0.2, 0.8) * L, rnd.uniform(0.25, 0.75) * T
        for j in range(5):
            span = (j + 1) * T / 9; reach = (j + 1) * L / 7
            p0, p1, p2 = (cu - reach, cv - span), (cu + reach * 0.2, cv), (cu - reach, cv + span)
            if vertical: p0, p1, p2 = (x + p0[1], y + p0[0]), (x + p1[1], y + p1[0]), (x + p2[1], y + p2[0])
            else: p0, p1, p2 = (x + p0[0], y + p0[1]), (x + p1[0], y + p1[1]), (x + p2[0], y + p2[1])
            gl.append(path('M%s,%s Q%s,%s %s,%s' % (f(p0[0]), f(p0[1]), f(p1[0]) if not vertical else f(p1[0]), f(p1[1]), f(p2[0]), f(p2[1])), 'none', stroke=dark(base, 0.22 * contrast), stroke_width=0.18, opacity=0.6))
    # pores
    for i in range(int(n * 1.5)):
        off = rnd.uniform(0, T)
        d = ('M%s,%s L%s,%s' % (f(x + off), f(y), f(x + off), f(y + h))) if vertical else ('M%s,%s L%s,%s' % (f(x), f(y + off), f(x + w), f(y + off)))
        gl.append(path(d, 'none', stroke=dark(base, 0.35 * contrast), stroke_width=0.12, stroke_dasharray='%s %s' % (f(rnd.uniform(0.3, 1.2)), f(rnd.uniform(2, 7))), stroke_dashoffset=f(rnd.uniform(0, 8)), opacity=0.45))
    out.append(g(gl, clip_path=D.clip(rect(x, y, w, h, '#000'))))
    return g(out)

# ---- brushed aluminium: a cool gradient, hairlines along the brushing, a soft highlight
def brushed(D, x, y, w, h, base='#d9d8d3', seed=2, vertical_light=True):
    rnd = random.Random(seed)
    out = [rect(x, y, w, h, D.lin([(0, light(base, 0.35)), (0.45, base), (1, dark(base, 0.12))]))]
    hl = []
    for i in range(int(h / 0.35)):
        yy = y + i * 0.35 + rnd.uniform(0, 0.3)
        c = '#ffffff' if rnd.random() < 0.5 else dark(base, 0.25)
        hl.append(line(x, yy, x + w, yy, c, 0.08, opacity=f(rnd.uniform(0.15, 0.45))))
    out.append(g(hl))
    out.append(rect(x, y, w, h, D.lin([(0, '#ffffff', 0), (0.3, '#ffffff', 0.32), (0.42, '#ffffff', 0.05), (0.7, '#ffffff', 0), (1, '#ffffff', 0)], 0, 0, 1, 0.3)))
    return g(out, clip_path=D.clip(rect(x, y, w, h, '#000')))

def screw(D, x, y, r=0.9, phillips=True, ang=20):
    out = [circle(x, y, r, D.rad([(0, '#f2f1ec'), (0.6, '#bdbab2'), (1, '#86837c')], 0.35, 0.3, 0.75)),
           circle(x, y, r, 'none', stroke='#6e6b64', stroke_width=r * 0.15)]
    a = math.radians(ang)
    for t in ((0,) if not phillips else (0, 90)):
        b = a + math.radians(t)
        out.append(line(x - r * 0.65 * math.cos(b), y - r * 0.65 * math.sin(b), x + r * 0.65 * math.cos(b), y + r * 0.65 * math.sin(b), '#4f4c46', r * 0.22))
    return g(out)

def knob(D, x, y, r, cap='#e8e6e0', body='#1e1d1b', ind=-40, knurl=True):
    out = [circle(x + r * 0.08, y + r * 0.14, r * 1.02, '#000', opacity=0.25, filter=D.blur(r * 0.12)),
           circle(x, y, r, D.rad([(0, light(body, 0.35)), (0.75, body), (1, dark(body, 0.4))], 0.35, 0.3, 0.8))]
    if knurl:
        for k in range(36):
            a = 2 * math.pi * k / 36
            out.append(line(x + r * 0.84 * math.cos(a), y + r * 0.84 * math.sin(a), x + r * 0.98 * math.cos(a), y + r * 0.98 * math.sin(a), light(body, 0.25), r * 0.035, opacity=0.8))
    out.append(circle(x, y, r * 0.68, D.rad([(0, '#ffffff'), (0.5, cap), (1, dark(cap, 0.25))], 0.35, 0.3, 0.8)))
    out.append(circle(x, y, r * 0.68, 'none', stroke=dark(cap, 0.35), stroke_width=r * 0.04))
    a = math.radians(ind - 90)
    out.append(line(x + r * 0.2 * math.cos(a), y + r * 0.2 * math.sin(a), x + r * 0.62 * math.cos(a), y + r * 0.62 * math.sin(a), '#b5462b', r * 0.09, stroke_linecap='round'))
    return g(out)

def gilt(D):
    return D.lin([(0, '#f1dc96'), (0.35, '#c9a24e'), (0.55, '#fbeebc'), (0.8, '#a9822f'), (1, '#d8b867')], 0, 0, 1, 1)

def glass_glare(D, x, y, w, h, op=0.35):
    """a diagonal sheen across a pane of glass"""
    gid = D.lin([(0, '#ffffff', 0), (0.42, '#ffffff', 0), (0.5, '#ffffff', op), (0.58, '#ffffff', op * 0.4), (0.66, '#ffffff', 0), (1, '#ffffff', 0)], 0, 0, 1, 1)
    return rect(x, y, w, h, gid)
