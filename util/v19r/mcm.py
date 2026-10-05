# A small vocabulary for mid-century vector illustration: flat fields of a few colours,
# a screen-printer's speckle, halftone shading in place of gradients, a hairline ink line
# printed slightly out of register with the colour under it, and ruled-line surfaces.
import math, random

P = dict(wall='#ece8df', paper='#f7f4ec', ivory='#f4f0e7', stone='#d8d1c3', ink='#1e1d1b', soft='#5d5851',
         oak='#c8a97e', oakd='#a98b68', oakl='#dcc6a7', walnut='#4e3727', walnutd='#3d2b20', walnutl='#7a5a45',
         teak='#9a6a43', teakd='#7d5334', teakl='#b98a5e',
         accent='#b5462b', ochre='#c99a2e', sage='#7d8a78', slate='#49555a', linen='#c7bba5', brass='#b0975f',
         steel='#d2d0cb', steeld='#8f8c86', alu='#dddbd5', tape='#5b3a22', cream='#efe9da')

def hexrgb(c): c = c.lstrip('#'); return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))
def mix(a, b, t):
    A, B = hexrgb(a), hexrgb(b)
    return '#%02x%02x%02x' % tuple(int(round(A[i] + (B[i] - A[i]) * t)) for i in range(3))
def light(c, t): return mix(c, '#ffffff', t)
def dark(c, t): return mix(c, '#000000', t)
def f(v): return ('%.2f' % v).rstrip('0').rstrip('.')

def attrs(**kw):
    return ''.join(' %s="%s"' % (k.rstrip('_').replace('_', '-'), v) for k, v in kw.items() if v is not None)
def rect(x, y, w, h, fill, **kw): return '<rect x="%s" y="%s" width="%s" height="%s" fill="%s"%s/>' % (f(x), f(y), f(w), f(h), fill, attrs(**kw))
def circle(cx, cy, r, fill, **kw): return '<circle cx="%s" cy="%s" r="%s" fill="%s"%s/>' % (f(cx), f(cy), f(r), fill, attrs(**kw))
def line(x1, y1, x2, y2, stroke, w=0.25, **kw): return '<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="%s"%s/>' % (f(x1), f(y1), f(x2), f(y2), stroke, f(w), attrs(**kw))
def path(d, fill, **kw): return '<path d="%s" fill="%s"%s/>' % (d, fill, attrs(**kw))
def poly(pts, fill, **kw): return '<polygon points="%s" fill="%s"%s/>' % (' '.join('%s,%s' % (f(x), f(y)) for x, y in pts), fill, attrs(**kw))
def text(x, y, s, size, fill, family='Jost', weight=600, track=0, anchor='start', **kw):
    return ('<text x="%s" y="%s" font-family="%s" font-weight="%d" font-size="%s" letter-spacing="%s" text-anchor="%s" fill="%s"%s>%s</text>'
            % (f(x), f(y), family, weight, f(size), f(track * size), anchor, fill, attrs(**kw), s))
def g(inner, **kw): return '<g%s>%s</g>' % (attrs(**kw), ''.join(inner) if isinstance(inner, list) else inner)

def rrect(x, y, w, h, r):
    """a rect with corner radii r = (tl, tr, br, bl)"""
    tl, tr, br, bl = r if isinstance(r, (list, tuple)) else (r,) * 4
    return ('M%s,%s H%s A%s,%s 0 0 1 %s,%s V%s A%s,%s 0 0 1 %s,%s H%s A%s,%s 0 0 1 %s,%s V%s A%s,%s 0 0 1 %s,%s Z'
            % (f(x + tl), f(y), f(x + w - tr), f(tr), f(tr), f(x + w), f(y + tr), f(y + h - br), f(br), f(br), f(x + w - br), f(y + h),
               f(x + bl), f(bl), f(bl), f(x), f(y + h - bl), f(y + tl), f(tl), f(tl), f(x + tl), f(y)))

# ---- filters -----------------------------------------------------------------------
def print_filter(id_, freq=1.4, thr=0.3, seed=3, soft=0.06):
    """screen-printed ink: the colour starved here and there in a fine speckle, where the
       noise falls below thr"""
    k = 1 / soft
    return ('<filter id="%s" x="-5%%" y="-5%%" width="110%%" height="110%%" color-interpolation-filters="sRGB">'
            '<feTurbulence type="fractalNoise" baseFrequency="%s" numOctaves="2" seed="%d" result="n"/>'
            '<feColorMatrix in="n" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  %s 0 0 0 %s" result="a"/>'
            '<feComposite in="SourceGraphic" in2="a" operator="in"/></filter>') % (id_, freq, seed, f(k), f(-k * (thr - soft)))

def grain_filter(id_, freq=0.9, amt=0.10, seed=7, tint=(0.25, 0.18, 0.1)):
    """paper or cloth tooth laid over a surface: dark specks and light specks"""
    return ('<filter id="%s" x="0" y="0" width="100%%" height="100%%" color-interpolation-filters="sRGB">'
            '<feTurbulence type="fractalNoise" baseFrequency="%s" numOctaves="3" seed="%d" result="n"/>'
            '<feColorMatrix in="n" type="matrix" values="0 0 0 0 %s  0 0 0 0 %s  0 0 0 0 %s  %s 0 0 0 %s" result="d"/>'
            '<feComposite in="d" in2="SourceGraphic" operator="in" result="dd"/>'
            '<feMerge><feMergeNode in="SourceGraphic"/><feMergeNode in="dd"/></feMerge></filter>'
            ) % (id_, freq, seed, tint[0], tint[1], tint[2], f(amt * 6), f(-amt * 2.6))

def shadow_filter(id_, dx=5.5, dy=3.5, sd=2.75, op=0.24, color='#28180c'):
    return ('<filter id="%s" x="-30%%" y="-30%%" width="170%%" height="170%%"><feDropShadow dx="%s" dy="%s" stdDeviation="%s" flood-color="%s" flood-opacity="%s"/></filter>'
            % (id_, f(dx), f(dy), f(sd), color, f(op)))

def blur_filter(id_, sd):
    return '<filter id="%s" x="-50%%" y="-50%%" width="200%%" height="200%%"><feGaussianBlur stdDeviation="%s"/></filter>' % (id_, f(sd))

# ---- halftone ----------------------------------------------------------------------
def halftone(x0, y0, x1, y1, cov, cell, fill, angle=45, rmax=0.62, **kw):
    """dots on a screen at `angle`, each sized to the coverage cov(x, y) in 0..1"""
    out = []
    a = math.radians(angle); ca, sa = math.cos(a), math.sin(a)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    R = math.hypot(x1 - x0, y1 - y0) / 2 + cell
    n = int(R / cell) + 1
    for i in range(-n, n + 1):
        for j in range(-n, n + 1):
            u, v = i * cell, j * cell
            x, y = cx + u * ca - v * sa, cy + u * sa + v * ca
            if x < x0 - cell or x > x1 + cell or y < y0 - cell or y > y1 + cell: continue
            c = max(0.0, min(1.0, cov(x, y)))
            if c <= 0.02: continue
            r = cell * rmax * math.sqrt(c)
            out.append('<circle cx="%s" cy="%s" r="%s"/>' % (f(x), f(y), f(r)))
    return '<g fill="%s"%s>%s</g>' % (fill, attrs(**kw), ''.join(out))

def hatch(x0, y0, x1, y1, gap, stroke, w=0.2, angle=45, **kw):
    """parallel rules across a box, at `angle` degrees; clip them to the shape wanted"""
    out = []
    a = math.radians(angle); dx, dy = math.cos(a), math.sin(a)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    R = math.hypot(x1 - x0, y1 - y0) / 2 + gap
    k = -R
    while k <= R:
        px, py = cx - dy * k, cy + dx * k
        out.append('<line x1="%s" y1="%s" x2="%s" y2="%s"/>' % (f(px - dx * R), f(py - dy * R), f(px + dx * R), f(py + dy * R)))
        k += gap
    return '<g stroke="%s" stroke-width="%s"%s>%s</g>' % (stroke, f(w), attrs(**kw), ''.join(out))

def ruled(a, b, c, d, n, stroke, w=0.2, both=True, **kw):
    """the two families of straight rulings of a twisted quadrilateral a b c d: a
       hyperbolic paraboloid seen in elevation"""
    L = lambda p, q, t: (p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t)
    out = []
    for i in range(n + 1):
        t = i / n
        p, q = L(a, b, t), L(d, c, t)
        out.append('<line x1="%s" y1="%s" x2="%s" y2="%s"/>' % (f(p[0]), f(p[1]), f(q[0]), f(q[1])))
        if both:
            p, q = L(a, d, t), L(b, c, t)
            out.append('<line x1="%s" y1="%s" x2="%s" y2="%s"/>' % (f(p[0]), f(p[1]), f(q[0]), f(q[1])))
    return '<g stroke="%s" stroke-width="%s" stroke-linecap="round"%s>%s</g>' % (stroke, f(w), attrs(**kw), ''.join(out))

def clip(id_, shape): return '<clipPath id="%s">%s</clipPath>' % (id_, shape)
