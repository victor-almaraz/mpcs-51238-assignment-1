# The tape player's deck parts for v21, drawn in the room's new manner: the reel flange
# (shaded only in rings round its centre, as it turns), the plate's guides and tension arms,
# and the vented head cover with the capstan and pinch roller. SVG units of the deck (520 × 250).
import math
from mcm import *
from mcm2 import *
from render import render, REPO
OUT = REPO + '/v21/assets'

def flange(D, cx, cy, R):
    d = ['M%s,%s a%s,%s 0 1 0 %s,0 a%s,%s 0 1 0 %s,0 Z' % (f(cx - R), f(cy), f(R), f(R), f(2 * R), f(R), f(R), f(-2 * R))]
    r0, r1 = R * 0.34, R * 0.86
    for i in range(3):
        a0 = math.radians(-90 + i * 120 + 18); a1 = math.radians(-90 + i * 120 + 102)
        d.append('M%s,%s A%s,%s 0 0 1 %s,%s L%s,%s A%s,%s 0 0 0 %s,%s Z' % (
            f(cx + r1 * math.cos(a0)), f(cy + r1 * math.sin(a0)), f(r1), f(r1), f(cx + r1 * math.cos(a1)), f(cy + r1 * math.sin(a1)),
            f(cx + r0 * math.cos(a1)), f(cy + r0 * math.sin(a1)), f(r0), f(r0), f(cx + r0 * math.cos(a0)), f(cy + r0 * math.sin(a0))))
    shape = ' '.join(d)
    rings = D.rad([(0, '#d9d7d1'), (0.3, '#f2f1ed'), (0.34, '#bebbb4'), (0.62, '#dedcd6'), (0.86, '#c9c6bf'), (0.9, '#f5f4f0'), (0.96, '#d4d1ca'), (1, '#8e8b84')], 0.5, 0.5, 0.5)
    o = [path(shape, rings, fill_rule='evenodd'),
         path(shape, 'none', stroke='#6f6b63', stroke_width=1.0, stroke_linejoin='round', fill_rule='evenodd'),
         circle(cx, cy, R * 0.25, D.rad([(0, '#ffffff'), (0.6, '#dcd8cf'), (1, '#9a968d')], 0.5, 0.5, 0.5)),
         circle(cx, cy, R * 0.25, 'none', stroke='#77736b', stroke_width=0.8),
         circle(cx, cy, R * 0.1, D.rad([(0, '#5a5853'), (1, '#1f1e1c')], 0.5, 0.5, 0.5))]
    for i in range(3):
        a = math.radians(-30 + i * 120)
        o.append(line(cx + R * 0.11 * math.cos(a), cy + R * 0.11 * math.sin(a), cx + R * 0.21 * math.cos(a), cy + R * 0.21 * math.sin(a), '#3a3833', R * 0.045, stroke_linecap='round'))
    return o

def parts():
    D = Defs()
    render('reel', g(flange(D, 102, 102, 100)), 204, 204, 3, OUT, defs=D.out())
    D = Defs(); o = []
    for cx in (120, 400):
        o.append(circle(cx + 5, 117, 102, '#000', opacity=0.22, filter=D.blur(4)))
        o.append(circle(cx, 112, 100, D.rad([(0, '#7c7a74'), (0.9, '#5d5b56'), (1, '#45433f')], 0.5, 0.5, 0.5)))
    for gx in (200, 320):
        ax = gx + (-46 if gx < 260 else 46)
        o.append(line(gx, 232, ax, 196, '#5d5b56', 5.2, stroke_linecap='round'))
        o.append(line(gx, 232, ax, 196, '#cfcdc7', 3.4, stroke_linecap='round'))
        o.append(circle(ax, 196, 5, D.rad([(0, '#ffffff'), (0.6, '#c9c6bf'), (1, '#77736b')], 0.35, 0.3, 0.8)))
        o.append(circle(gx, 232, 9, D.rad([(0, '#ffffff'), (0.6, '#c9c6bf'), (1, '#77736b')], 0.35, 0.3, 0.8)))
        o.append(circle(gx, 232, 9, 'none', stroke='#55524c', stroke_width=0.8))
        o.append(circle(gx, 232, 2.8, '#2a2826'))
    o.append(text(120, 240, 'SUPPLY', 7, '#5d5851', 'Jost', 400, 0.32, 'middle'))
    o.append(text(400, 240, 'TAKE-UP', 7, '#5d5851', 'Jost', 400, 0.32, 'middle'))
    render('deck', g(o), 520, 250, 3, OUT, defs=D.out())
    D = Defs()
    hs = rrect(226, 212, 68, 34, (9, 9, 2, 2))
    h = [path(hs, '#000', opacity=0.35, filter=D.blur(2), transform='translate(2 3)'),
         path(hs, D.lin([(0, '#4e4c48'), (0.18, '#34322f'), (1, '#1a1918')]))]
    for k in range(9):
        h.append(path(rrect(236 + k * 5.6, 219, 2.8, 12, 1.4), '#0d0c0b'))
        h.append(rect(236 + k * 5.6, 230.4, 2.8, 0.8, '#6a6863'))
    h.append(rect(226, 212.6, 68, 1.2, '#ffffff', opacity=0.2))
    h.append(text(232, 242, 'REC · PB', 5, '#a8a59d', 'Jost', 600, 0.25))
    h.append(circle(284, 238, 2.6, D.rad([(0, '#ffc2a8'), (0.5, '#c4482b'), (1, '#6e1f10')], 0.4, 0.35, 0.7)))
    render('head', g(h), 520, 250, 3, OUT, defs=D.out())

if __name__ == '__main__':
    parts()
