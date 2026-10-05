# v21's wallpaper, darker and more elaborate: a deep blue ground under a half-drop ogee
# trellis in a pale blue hairline; in each cell a cream seed pod with a dotted spine, a
# pair of leaves and a crown of three ochre dots; at each crossing a small four-petal
# flower; seeds scattered between. A 60 × 90 tile, hung at 6em × 9em.
import os as _os; UTIL = _os.path.normpath(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..')); REPO = _os.path.dirname(UTIL)
from mcm import f
W, H = 60, 90
GROUND, LATTICE, CREAM, OCHRE, PALE = '#2b4560', '#4a6886', '#e6dcc4', '#c9a45a', '#6f8ca8'

def ogee():
    d = ''
    for ox in (0, 60):
        for oy in (-90, 0, 90):
            # from each node down to the next half-drop node, in two S-curves
            for sx in (1, -1):
                x0, y0 = ox, oy
                d += 'M%s,%s C%s,%s %s,%s %s,%s C%s,%s %s,%s %s,%s' % (
                    f(x0), f(y0), f(x0), f(y0 + 20), f(x0 + sx * 30), f(y0 + 25), f(x0 + sx * 30), f(y0 + 45),
                    f(x0 + sx * 30), f(y0 + 65), f(x0 + sx * 60), f(y0 + 70), f(x0 + sx * 60), f(y0 + 90))
    return '<path d="%s" fill="none" stroke="%s" stroke-width="0.7"/>' % (d, LATTICE)

def pod(x, y):
    o = []
    o.append('<path d="M%s,%s Q%s,%s %s,%s Q%s,%s %s,%s Z" fill="%s" fill-opacity="0.12" stroke="%s" stroke-width="0.75"/>' % (
        f(x), f(y - 11), f(x + 6.5), f(y), f(x), f(y + 11), f(x - 6.5), f(y), f(x), f(y - 11), CREAM, CREAM))
    o.append('<path d="M%s,%s L%s,%s" stroke="%s" stroke-width="0.7" stroke-dasharray="0.01 1.6" stroke-linecap="round"/>' % (f(x), f(y - 8), f(x), f(y + 8), CREAM))
    # a stem below the pod, and two leaves rising from it
    o.append('<path d="M%s,%s L%s,%s" stroke="%s" stroke-width="0.6"/>' % (f(x), f(y + 11), f(x), f(y + 21), CREAM))
    for sd in (-1, 1):
        bx, by = x, y + 18
        tx, ty = x + sd * 8.5, y + 9.5
        o.append('<path d="M%s,%s C%s,%s %s,%s %s,%s C%s,%s %s,%s %s,%s Z" fill="%s" opacity="0.85"/>' % (
            f(bx), f(by), f(bx + sd * 1.5), f(by - 5), f(tx - sd * 3), f(ty - 0.5), f(tx), f(ty),
            f(tx - sd * 0.5), f(ty + 3.5), f(bx + sd * 4), f(by + 0.5), f(bx), f(by), PALE))
        o.append('<path d="M%s,%s Q%s,%s %s,%s" fill="none" stroke="%s" stroke-width="0.4"/>' % (f(bx), f(by - 0.4), f(bx + sd * 4), f(by - 3.6), f(tx - sd * 0.8), f(ty + 0.8), GROUND))
    for dx, dy in ((0, -15), (-2.6, -13.4), (2.6, -13.4)):
        o.append('<circle cx="%s" cy="%s" r="0.95" fill="%s"/>' % (f(x + dx), f(y + dy), OCHRE))
    return ''.join(o)

def flower(x, y):
    o = ''.join('<circle cx="%s" cy="%s" r="1.5" fill="%s" opacity="0.9"/>' % (f(x + dx), f(y + dy), CREAM) for dx, dy in ((0, -1.9), (1.9, 0), (0, 1.9), (-1.9, 0)))
    return o + '<circle cx="%s" cy="%s" r="0.9" fill="%s"/>' % (f(x), f(y), OCHRE)

def seeds(x, y):
    return ''.join('<circle cx="%s" cy="%s" r="0.55" fill="%s" opacity="0.8"/>' % (f(x + dx), f(y + dy), PALE) for dx, dy in ((0, 0), (1.6, 1.2), (-1.4, 1.5)))

body = ['<rect width="%d" height="%d" fill="%s"/>' % (W, H, GROUND), ogee()]
for x, y in ((30, 0), (30, 90), (0, 45), (60, 45), (30, -90 + 0)):
    body.append(pod(x, y - 2))
for x, y in ((0, 0), (60, 0), (0, 90), (60, 90), (30, 45)):
    body.append(flower(x, y))
for x, y in ((15, 22), (45, 22), (15, 68), (45, 68)):
    body.append(seeds(x, y))
s = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">%s</svg>' % (W, H, W * 4, H * 4, ''.join(body))
open(REPO + '/v21/assets/wallpaper.svg', 'w').write(s)
print(len(s))
