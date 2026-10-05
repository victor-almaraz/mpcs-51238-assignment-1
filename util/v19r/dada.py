# A Dada print for v21's wall: a typographic collage after the posters of 1916-22 (Zürich,
# Hanover, the Kleine Dada Soirée): Hugo Ball's sound poem Gadji beri bimba (1916) scattered
# in mixed faces at many sizes and angles, a big red DADA, a torn newsprint fragment, a
# halftone disc and heavy rules, printed in black and red on a yellowing sheet, in a narrow
# black frame. 120 × 150 units (12em × 15em).
import math, random
from mcm import *
from mcm2 import *
from render import render, REPO
OUT = REPO + '/v21/assets'
RED, INK = '#c23a26', '#1b1a18'

def T(x, y, s, size, fam, wt=400, fill=INK, rot=0, anchor='start', italic=False, track=0, blend=False):
    st = ';'.join(x_ for x_ in ('font-style:italic' if italic else '', 'mix-blend-mode:multiply' if blend else '') if x_) or None
    return text(x, y, s, size, fill, fam, wt, track, anchor, transform='rotate(%s %s %s)' % (f(rot), f(x), f(y)) if rot else None, style=st)

def print_():
    W, H = 120, 150
    D = Defs(); o = []
    o.append(rect(2.4, 3.2, W - 2, H - 2, '#000', opacity=0.3, filter=D.blur(1.4)))
    o.append(rect(0, 0, W - 2, H - 2, D.lin([(0, '#3a3836'), (0.5, '#1b1a18'), (1, '#0d0c0b')], 0, 0, 1, 1)))
    o.append(rect(0.4, 0.4, W - 2.8, 0.5, '#ffffff', opacity=0.25))
    fx, fy, fw, fh = 3, 3, W - 8, H - 8
    o.append(rect(fx, fy, fw, fh, D.lin([(0, '#f4ead2'), (1, '#e6d6b2')], 0, 0, 1, 1)))
    a = []
    clipr = D.clip(rect(fx, fy, fw, fh, '#000'))
    rnd = random.Random(16)
    # a torn fragment of newsprint, under everything
    torn = [(fx + 52, fy + 70), (fx + 104, fy + 64), (fx + 109, fy + 102), (fx + 58, fy + 108)]
    pts = []
    for i in range(4):
        (x0, y0), (x1, y1) = torn[i], torn[(i + 1) % 4]
        for k in range(10):
            t = k / 10
            pts.append((x0 + (x1 - x0) * t + rnd.uniform(-0.8, 0.8), y0 + (y1 - y0) * t + rnd.uniform(-0.8, 0.8)))
    a.append(poly(pts, '#d9d3c4', transform='rotate(-4 %s %s)' % (f(fx + 80), f(fy + 86))))
    for k in range(16):
        y = fy + 74 + k * 2.0
        a.append(g([rect(fx + 56 + c * 12.4, y, 11 - rnd.uniform(0, 4), 0.6, '#77736b', opacity=0.7) for c in range(4)], transform='rotate(-4 %s %s)' % (f(fx + 80), f(fy + 86))))
    # a halftone disc, a photograph's fragment
    a.append(halftone(fx + 8, fy + 92, fx + 40, fy + 124, lambda x, y: max(0, 0.9 - math.hypot(x - fx - 24, y - fy - 108) / 16) if math.hypot(x - fx - 24, y - fy - 108) < 16 else 0, 1.5, INK, angle=45))
    # the red block letters, aslant, overprinting
    a.append(T(fx + 4, fy + 46, 'DADA', 30, 'Archivo Black', fill=RED, rot=-9, track=-0.02, blend=True))
    # the poem, in pieces
    a.append(T(fx + 7, fy + 15, 'gadji beri bimba', 9.2, 'Bodoni Moda', 400, italic=True))
    a.append(T(fx + fw - 4, fy + 9.6, 'glandridi', 6.4, 'Big Shoulders Display', 800, anchor='end', track=0.08))
    a.append(T(fx + 74, fy + 26, 'laula', 11, 'Bodoni Moda', 700, rot=12))
    a.append(T(fx + 70, fy + 58, 'lonni cadori', 7.2, 'Courier Prime', 700, rot=-3))
    a.append(T(fx + 9, fy + 62, 'GADJAMA', 8.6, 'Oswald', 600, track=0.32))
    a.append(T(fx + 104, fy + 132, 'bim beri glassala', 5.0, 'Courier Prime', 400, rot=-90))
    a.append(T(fx + 44, fy + 120, 'glandride', 12, 'Bodoni Moda', 400, italic=True, fill=RED, rot=-6))
    a.append(T(fx + 8, fy + 136, 'ZÜRICH · CABARET VOLTAIRE · 1916', 3.2, 'Work Sans', 600, track=0.22))
    a.append(T(fx + 48, fy + 84, 'zimzim', 6.0, 'Archivo Black', rot=88))
    a.append(T(fx + 30, fy + 76, 'o', 22, 'Bodoni Moda', 700, fill=RED))
    # heavy rules and a pointing arrow
    a.append(rect(fx + 4, fy + 20, 62, 2.2, INK, transform='rotate(-9 %s %s)' % (f(fx + 4), f(fy + 20))))
    a.append(rect(fx + 60, fy + 34, 2.4, 40, INK))
    a.append(rect(fx + 8, fy + 66, 40, 1.0, RED))
    a.append(poly([(fx + 66, fy + 96), (fx + 84, fy + 96), (fx + 84, fy + 92), (fx + 92, fy + 98), (fx + 84, fy + 104), (fx + 84, fy + 100), (fx + 66, fy + 100)], INK, transform='rotate(-20 %s %s)' % (f(fx + 79), f(fy + 98))))
    a.append(circle(fx + 92, fy + 40, 9, 'none', stroke=RED, stroke_width=2.2))
    a.append(circle(fx + 92, fy + 40, 3.4, INK))
    o.append(g(a, clip_path=clipr))
    o.append(rect(fx, fy, fw, fh, D.lin([(0, '#ffffff', 0), (0.5, '#ffffff', 0), (1, '#6b5a3a', 0.12)], 0, 0, 1, 1)))
    o.append(rect(fx, fy, fw, fh, 'none', stroke='#000', stroke_width=0.5, opacity=0.35))
    o.append(poly([(fx + fw * 0.58, fy), (fx + fw * 0.72, fy), (fx + fw * 0.34, fy + fh), (fx + fw * 0.2, fy + fh)], '#ffffff', opacity=0.07))
    defs = D.out() + print_filter('pr', 1.6, 0.18, 171) + grain_filter('gr', 1.1, 0.05, 172)
    return render('print-dada', g(g(o, filter='url(#gr)'), filter='url(#pr)'), W, H, 6, OUT, defs=defs)

if __name__ == '__main__':
    print_()
