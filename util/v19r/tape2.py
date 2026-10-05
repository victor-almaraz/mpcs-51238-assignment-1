# v21's tape machine on the desk, drawn again in more detail: a teak case with mitred
# corners, a brushed aluminium deck with an anodised name strip, seven-inch reels with
# their packs of tape catching the light, tension arms, guides, capstan and pinch roller,
# a vented head cover, two VU meters under glass, shaded transport keys, a knurled knob
# and a tape counter. Units are tenths of an em (150 × 106).
import math, random
from mcm import *
from mcm2 import *
from render import render, REPO
OUT = REPO + '/v21/assets'

def reel(D, cx, cy, R, pack, rot):
    o = []
    o.append(circle(cx + 1.4, cy + 1.6, R + 0.4, '#000', opacity=0.28, filter=D.blur(1.2)))
    # the tape pack: brown oxide, fine rings, a sheen across it
    o.append(circle(cx, cy, pack, D.rad([(0, '#6d4428'), (0.7, '#5b3a22'), (1, '#43291a')], 0.5, 0.5, 0.5)))
    for k in range(1, 14):
        o.append(circle(cx, cy, pack * (0.32 + 0.68 * k / 14), 'none', stroke='#3a2416' if k % 2 else '#7a4f30', stroke_width=0.12, opacity=0.5))
    o.append(circle(cx, cy, pack, D.lin([(0, '#ffffff', 0), (0.38, '#ffffff', 0.0), (0.48, '#f3d9b8', 0.32), (0.56, '#ffffff', 0.0), (1, '#ffffff', 0)], 0, 0, 1, 1)))
    # the flange: aluminium, a raised rim, three windows
    d = ['M%s,%s a%s,%s 0 1 0 %s,0 a%s,%s 0 1 0 %s,0 Z' % (f(cx - R), f(cy), f(R), f(R), f(2 * R), f(R), f(R), f(-2 * R))]
    r0, r1 = R * 0.34, R * 0.86
    for i in range(3):
        a0 = math.radians(rot + i * 120 + 18); a1 = math.radians(rot + i * 120 + 102)
        d.append('M%s,%s A%s,%s 0 0 1 %s,%s L%s,%s A%s,%s 0 0 0 %s,%s Z' % (
            f(cx + r1 * math.cos(a0)), f(cy + r1 * math.sin(a0)), f(r1), f(r1), f(cx + r1 * math.cos(a1)), f(cy + r1 * math.sin(a1)),
            f(cx + r0 * math.cos(a1)), f(cy + r0 * math.sin(a1)), f(r0), f(r0), f(cx + r0 * math.cos(a0)), f(cy + r0 * math.sin(a0))))
    shape = ' '.join(d)
    o.append(path(shape, D.rad([(0, '#f4f3ef'), (0.55, '#cfcdc6'), (0.85, '#b3b0a8'), (1, '#e2e0da')], 0.38, 0.32, 0.72), fill_rule='evenodd'))
    o.append(path(shape, D.lin([(0, '#ffffff', 0), (0.45, '#ffffff', 0.45), (0.55, '#ffffff', 0), (1, '#ffffff', 0)], 0, 0, 1, 1), fill_rule='evenodd'))
    o.append(circle(cx, cy, R - 0.35, 'none', stroke='#ffffff', stroke_width=0.35, opacity=0.7))
    o.append(circle(cx, cy, R, 'none', stroke='#6f6b63', stroke_width=0.3))
    o.append(path(shape, 'none', stroke='#7e7a72', stroke_width=0.25, stroke_linejoin='round', fill_rule='evenodd'))
    # the hub and spindle
    o.append(circle(cx, cy, R * 0.25, D.rad([(0, '#fafaf7'), (0.7, '#cfcbc2'), (1, '#9a968d')], 0.35, 0.3, 0.75)))
    o.append(circle(cx, cy, R * 0.25, 'none', stroke='#77736b', stroke_width=0.22))
    o.append(circle(cx, cy, R * 0.1, D.rad([(0, '#6a6862'), (1, '#1f1e1c')], 0.4, 0.35, 0.7)))
    for i in range(3):
        a = math.radians(rot + 60 + i * 120)
        o.append(line(cx + R * 0.11 * math.cos(a), cy + R * 0.11 * math.sin(a), cx + R * 0.2 * math.cos(a), cy + R * 0.2 * math.sin(a), '#3a3833', R * 0.045, stroke_linecap='round'))
    o.append(circle(cx - R * 0.03, cy - R * 0.04, R * 0.035, '#ffffff', opacity=0.8))
    return o

def vu(D, x, y, w, h, needle):
    o = [path(rrect(x - 0.9, y - 0.9, w + 1.8, h + 1.8, 1.4), D.lin([(0, '#f0efea'), (1, '#8d8a83')])),
         path(rrect(x, y, w, h, 0.8), D.lin([(0, '#f7efd8'), (1, '#e8dcb9')]))]
    cx, cy, R = x + w / 2, y + h + 3.2, h * 0.95
    marks = []
    for t in range(15):
        a = math.radians(-46 + t * 92 / 14)
        red = t >= 11
        L = 1.5 if t % 2 == 0 else 0.8
        marks.append(line(cx + R * math.sin(a), cy - R * math.cos(a), cx + (R - L) * math.sin(a), cy - (R - L) * math.cos(a), '#b5462b' if red else '#1e1d1b', 0.2))
    a0, a1, a2 = math.radians(-46), math.radians(-46 + 11 * 92 / 14), math.radians(46)
    marks.append(path('M%s,%s A%s,%s 0 0 1 %s,%s' % (f(cx + R * math.sin(a0)), f(cy - R * math.cos(a0)), f(R), f(R), f(cx + R * math.sin(a1)), f(cy - R * math.cos(a1))), 'none', stroke='#1e1d1b', stroke_width=0.18))
    marks.append(path('M%s,%s A%s,%s 0 0 1 %s,%s' % (f(cx + R * math.sin(a1)), f(cy - R * math.cos(a1)), f(R), f(R), f(cx + R * math.sin(a2)), f(cy - R * math.cos(a2))), 'none', stroke='#b5462b', stroke_width=0.55))
    o.append(g(marks, clip_path=D.clip(path(rrect(x, y, w, h, 0.8), '#000'))))
    o.append(text(x + 1.2, y + h - 1.0, 'VU', 1.5, '#1e1d1b', 'Work Sans', 600, 0.05))
    a = math.radians(needle)
    o.append(g([line(cx, cy, cx + (R + 0.3) * math.sin(a), cy - (R + 0.3) * math.cos(a), '#111', 0.22)], clip_path=D.clip(path(rrect(x, y, w, h, 0.8), '#000'))))
    o.append(rect(x, y, w, 1.6, '#000', opacity=0.12))
    o.append(glass_glare(D, x, y, w, h, 0.45))
    return o

def room():
    W, H = 150, 106
    D = Defs()
    o = []
    ch = H - 3
    # feet
    for fx in (14, W - 22):
        o.append(path(rrect(fx, H - 4, 8, 4, (0, 0, 1.2, 1.2)), D.lin([(0, '#3a3836'), (1, '#121110')])))
    # the case: teak, mitred at the corners, its top edge rounded and lit
    o.append(soft_shadow(D, rrect(0, 0, W, ch, 3.2), 1.2, 2.0, 1.6, 0.35))
    case = rrect(0, 0, W, ch, 3.2)
    cc = D.clip(path(case, '#000'))
    t = 5.4
    o.append(g([wood(D, 0, 0, W, ch, P['teak'], seed=4, lines=26, arches=2),
                # the side rails' grain runs up; the mitres
                g(wood(D, 0, 0, t, ch, P['teak'], seed=5, vertical=True, lines=5, arches=0), clip_path=D.clip(poly([(0, 0), (t, t), (t, ch - t), (0, ch)], '#000'))),
                g(wood(D, W - t, 0, t, ch, P['teak'], seed=6, vertical=True, lines=5, arches=0), clip_path=D.clip(poly([(W, 0), (W - t, t), (W - t, ch - t), (W, ch)], '#000'))),
                line(0, 0, t, t, P['teakd'], 0.25), line(W, 0, W - t, t, P['teakd'], 0.25), line(0, ch, t, ch - t, P['teakd'], 0.25), line(W, ch, W - t, ch - t, P['teakd'], 0.25),
                rect(0, 0, W, ch, D.lin([(0, '#ffffff', 0.18), (0.08, '#ffffff', 0), (0.9, '#000000', 0), (1, '#000000', 0.22)])),
                rect(0, 0, W, ch, D.lin([(0, '#ffffff', 0.12), (0.05, '#ffffff', 0), (0.95, '#000000', 0), (1, '#000000', 0.18)], 0, 0, 1, 0)),
                rect(0, 0.4, W, 0.6, '#ffffff', opacity=0.25)], clip_path=cc))
    # the deck plate, set into the case, its shadow on the plate's top
    px, py, pw, ph = t, t, W - 2 * t, ch - 2 * t
    o.append(rect(px - 0.4, py - 0.4, pw + 0.8, ph + 0.8, '#2a1a10', opacity=0.6))
    o.append(brushed(D, px, py, pw, ph))
    o.append(rect(px, py, pw, 1.6, D.lin([(0, '#000000', 0.25), (1, '#000000', 0)])))
    strip_h = 25
    sy = py + ph - strip_h
    # the lower panel: anodised graphite with a fine brushing
    o.append(g([rect(px, sy, pw, strip_h, D.lin([(0, '#3b3936'), (1, '#252422')])),
                g([line(px, sy + k * 0.4, px + pw, sy + k * 0.4, '#ffffff', 0.06, opacity=0.08) for k in range(int(strip_h / 0.4))]),
                rect(px, sy, pw, 0.5, '#ffffff', opacity=0.28), rect(px, sy + 0.5, pw, 0.4, '#000', opacity=0.4)]))
    # screws
    for sx, sy_ in ((px + 2.6, py + 2.6), (px + pw - 2.6, py + 2.6), (px + 2.6, sy - 2.4), (px + pw - 2.6, sy - 2.4)):
        o.append(screw(D, sx, sy_, 0.85))
    # reels
    ry, R = py + 29, 25.5
    L, Rr = (px + 31, 22.5), (px + pw - 31, 12.5)
    # the tape path first, under the reels' flanges where it leaves the packs
    gl, gr_, gy = px + 50, px + pw - 50, sy - 8
    tape = '#4a2f1c'
    o.append(path('M%s,%s L%s,%s L%s,%s' % (f(L[0] - L[1] + 0.4), f(ry + 3), f(gl - 6), f(gy + 1.6), f(gl - 2), f(gy + 2.1)), 'none', stroke=tape, stroke_width=0.8))
    o.append(path('M%s,%s L%s,%s' % (f(gl), f(gy + 2.2), f(gr_), f(gy + 2.2)), 'none', stroke=tape, stroke_width=0.8))
    o.append(path('M%s,%s L%s,%s L%s,%s' % (f(gr_ + 2), f(gy + 2.1), f(gr_ + 6), f(gy + 1.6), f(Rr[0] + Rr[1] - 0.4), f(ry + 2)), 'none', stroke=tape, stroke_width=0.8))
    o += reel(D, L[0], ry, R, L[1], -78)
    o += reel(D, Rr[0], ry, R, Rr[1], -24)
    # tension arms and guide rollers
    for gx, arm in ((gl - 6, -1), (gr_ + 6, 1)):
        o.append(line(gx, gy + 1.6, gx + arm * 5, gy - 7, '#8f8c86', 1.1, stroke_linecap='round'))
        o.append(circle(gx + arm * 5, gy - 7, 1.1, D.rad([(0, '#ffffff'), (1, '#9a978f')], 0.35, 0.3, 0.8)))
        o.append(circle(gx, gy + 1.6, 1.6, D.rad([(0, '#fbfbf8'), (0.7, '#c2bfb7'), (1, '#8a877f')], 0.35, 0.3, 0.8)))
        o.append(circle(gx, gy + 1.6, 0.45, '#3a3833'))
    # the head cover, vented, and the capstan with its rubber pinch roller
    hx, hw = W / 2 - 13, 26
    o.append(soft_shadow(D, rrect(hx, gy - 4, hw, 10, (2.6, 2.6, 0.4, 0.4)), 0.6, 1.0, 0.8, 0.35))
    o.append(path(rrect(hx, gy - 4, hw, 10, (2.6, 2.6, 0.4, 0.4)), D.lin([(0, '#4a4844'), (0.15, '#33312e'), (1, '#1c1b19')])))
    for k in range(7):
        o.append(rect(hx + 4 + k * 2.6, gy - 2.2, 1.2, 3.4, '#0e0d0c'))
        o.append(rect(hx + 4 + k * 2.6, gy + 1.2, 1.2, 0.3, '#5a5853'))
    o.append(rect(hx, gy - 4, hw, 0.5, '#ffffff', opacity=0.25))
    o.append(text(hx + 3, gy + 4.6, 'REC', 1.4, '#c9c6bf', 'Jost', 600, 0.15))
    o.append(text(hx + hw - 3, gy + 4.6, 'PB', 1.4, '#c9c6bf', 'Jost', 600, 0.15, 'end'))
    o.append(circle(hx + hw / 2, gy + 3.4, 0.9, D.rad([(0, '#ffb39a'), (0.5, '#c4482b'), (1, '#6e1f10')], 0.4, 0.35, 0.7)))
    o.append(circle(gr_ - 3.2, gy + 2.2, 0.9, D.rad([(0, '#ffffff'), (1, '#7c7972')], 0.35, 0.3, 0.8)))
    o.append(circle(gr_ - 3.2, gy + 4.8, 2.0, D.rad([(0, '#4a4845'), (0.7, '#1c1b19'), (1, '#0c0b0a')], 0.35, 0.3, 0.8)))
    # the name strip at the top of the plate: anodised, engraved
    o.append(path(rrect(W / 2 - 15, py + 3.2, 30, 7.2, 0.6), D.lin([(0, '#2c2b29'), (1, '#1a1918')])))
    o.append(text(W / 2, py + 7.4, 'TAPE · STUDIO', 2.0, '#d9d6cf', 'Work Sans', 600, 0.38, 'middle'))
    o.append(text(W / 2, py + 9.3, '7½  ·  15  IPS', 1.2, '#a8a59d', 'Jost', 400, 0.3, 'middle'))
    # the lower panel: keys at the left, the knob and counter, the meters at the right
    kx = px + 4.5
    legends = ['◀◀', '■', '▶', '▶▶', '❚❚']
    for k in range(5):
        c = '#b5462b' if k == 2 else '#ece6d6'
        kh = 14.5 if k != 2 else 13.8
        o.append(path(rrect(kx + 0.3, sy + 5 + 0.6, 8.6, kh, (0.5, 0.5, 1.6, 1.6)), '#000', opacity=0.45, filter=D.blur(0.4)))
        o.append(path(rrect(kx, sy + 5, 8.6, kh, (0.5, 0.5, 1.6, 1.6)), D.lin([(0, light(c, 0.25)), (0.12, c), (0.82, c), (1, dark(c, 0.28))])))
        o.append(rect(kx + 0.5, sy + 5.3, 7.6, 0.6, '#ffffff', opacity=0.55))
        o.append(rect(kx + 7.2, sy + 6.2, 1.2, kh - 2.4, '#000', opacity=0.08))
        o.append(text(kx + 4.3, sy + 16.2, legends[k], 2.4, '#fff4ea' if k == 2 else '#55524c', 'Work Sans', 600, 0, 'middle'))
        kx += 9.6
    o.append(knob(D, px + 62, sy + 12.5, 4.6))
    o.append(text(px + 62, sy + 22.6, 'TEMPO', 1.2, '#a8a59d', 'Jost', 600, 0.25, 'middle'))
    # the counter: four white wheels in a window
    cx0 = px + 70.5
    o.append(path(rrect(cx0, sy + 9.2, 11.8, 6.4, 0.6), '#0f0f0e'))
    for k, dgt in enumerate('0428'):
        o.append(rect(cx0 + 0.8 + k * 2.6, sy + 10, 2.2, 4.8, D.lin([(0, '#9c9a94'), (0.3, '#f4f3ee'), (0.7, '#f4f3ee'), (1, '#9c9a94')])))
        o.append(text(cx0 + 1.9 + k * 2.6, sy + 13.7, dgt, 3.0, '#141414', 'Work Sans', 600, 0, 'middle'))
    o.append(glass_glare(D, cx0, sy + 9.2, 11.8, 6.4, 0.3))
    o.append(text(cx0 + 5.9, sy + 22.6, 'COUNTER', 1.2, '#a8a59d', 'Jost', 600, 0.25, 'middle'))
    # two meters, left and right channels
    for k, nd in enumerate((-12, -20)):
        o += vu(D, px + pw - 32 + k * 15.4, sy + 5, 13.2, 12, nd)
        o.append(text(px + pw - 25.4 + k * 15.4, sy + 22.6, 'LR'[k], 1.3, '#a8a59d', 'Jost', 600, 0.25, 'middle'))
    defs = D.out() + print_filter('pr', 1.4, 0.1, 31) + grain_filter('gr', 1.0, 0.02, 8)
    return render('tape-room', g(g(o, filter='url(#gr)'), filter='url(#pr)'), W, H, 6, OUT, defs=defs)

if __name__ == '__main__':
    room()
