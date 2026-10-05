# The computer, in the manner of the room's other drawings: a display in a stone-white hood
# on a graphite plinth, a low keyboard before it (after Sottsass's and Bellini's Olivetti
# machines), the desktop it runs on its screen; and the hood's face alone, as a nine-slice
# frame for the live desktop in the computer's station.
import math, random
from mcm import *
from render import render, REPO
OUT = REPO + '/v21/assets'
HOOD = '#e7e1d4'
GRAPH = '#2b2926'
DESKTOP = 'file://' + REPO + '/v20/assets/desktop.png'

def room():
    W, H, S = 170, 130, 5
    defs = [print_filter('pr', 1.4, 0.2, 61), grain_filter('gr', 1.1, 0.05, 62), blur_filter('soft', 0.8)]
    o = []
    # the plinth and its two feet
    o.append(rect(46, 100, 78, 10, GRAPH)); o.append(rect(46, 100, 78, 1.0, light(GRAPH, 0.2)))
    o.append(rect(52, 109.5, 10, 2.5, P['ink'])); o.append(rect(108, 109.5, 10, 2.5, P['ink']))
    # the hood: flat stone white, lit band at the left, a halftone shade at the right
    hx, hy, hw, hh = 18, 2, 134, 98
    hood = path(rrect(hx, hy, hw, hh, (9, 9, 5, 5)), '#000')
    defs.append(clip('hood', hood))
    h = [rect(hx, hy, hw, hh, HOOD), rect(hx, hy, 5, hh, light(HOOD, 0.4)),
         rect(hx + hw - 7, hy, 7, hh, dark(HOOD, 0.1)),
         halftone(hx + hw - 26, hy, hx + hw - 7, hy + hh, lambda x, y: (x - (hx + hw - 26)) / 19, 1.0, dark(HOOD, 0.1)),
         rect(hx, hy + hh - 4, hw, 4, dark(HOOD, 0.08)),
         rect(hx, hy, hw, 1.4, light(HOOD, 0.5))]
    o.append(g(h, clip_path='url(#hood)'))
    o.append(path(rrect(hx, hy, hw, hh, (9, 9, 5, 5)), 'none', stroke=P['ink'], stroke_width=0.3, transform='translate(-0.3 0.25)', opacity=0.65))
    # the screen: a graphite gasket, the glass, and on it the desktop: its picture, a white
    # menu bar and two windows, in screen pixels
    sx, sy, sw, sh = 28, 10, 114, 74
    o.append(path(rrect(sx - 2.2, sy - 2.2, sw + 4.4, sh + 4.4, 6.5), GRAPH))
    scr = path(rrect(sx, sy, sw, sh, 4.6), '#000')
    defs.append(clip('scr', scr))
    px = 0.9   # a screen pixel, at the drawing's size
    s = [rect(sx, sy, sw, sh, '#000'),
         '<image href="%s" x="%s" y="%s" width="%s" height="%s" preserveAspectRatio="xMidYMid slice" style="image-rendering:pixelated" opacity="0.95"/>' % (DESKTOP, f(sx), f(sy + 4), f(sw), f(sh - 4)),
         rect(sx, sy, sw, 4, '#fff'), rect(sx, sy + 4, sw, px * 0.6, '#000')]
    for k, wd in enumerate((5, 4.2, 4.6, 3.6, 4.4)):
        s.append(rect(sx + 7 + k * 8, sy + 1.5, wd, 1.0, '#000'))
    def win(x, y, w, hgt, title_w):
        out = [rect(x + 1, y + 1, w, hgt, '#000'), rect(x, y, w, hgt, '#fff'), rect(x, y, w, hgt, 'none', stroke='#000', stroke_width=px * 0.7)]
        for k in range(4): out.append(rect(x + 1, y + 1 + k * 0.9, w - 2, 0.45, '#000'))
        out.append(rect(x + w / 2 - title_w / 2, y + 0.6, title_w, 3.4, '#fff'))
        out.append(rect(x, y + 4.4, w, px * 0.6, '#000'))
        return out
    s += win(sx + 10, sy + 12, 46, 34, 14)
    for r in range(6): s.append(rect(sx + 13, sy + 19.5 + r * 3.6, [30, 22, 34, 16, 27, 20][r], 1.1, '#000'))
    s += win(sx + 62, sy + 26, 40, 30, 12)
    for c in range(9):
        s.append(rect(sx + 64.5 + c * 4, sy + 33, 3, 2, '#00f' if c % 3 else '#ff0'))
    s.append(rect(sx + 64.5, sy + 38, 35, 14, '#fff', stroke='#000', stroke_width=0.4))
    for c in range(14):
        for r in range(4):
            if (c * 3 + r * 5) % 7 < 2: s.append(rect(sx + 66 + c * 2.4, sy + 40 + r * 2.8, 0.9, 1.6, '#000'))
    # the glass: a pale sheen across, and its curve darkening the corners
    s.append(poly([(sx + 8, sy + sh), (sx + 30, sy), (sx + 46, sy), (sx + 24, sy + sh)], '#fff', opacity=0.07))
    s.append('<rect x="%s" y="%s" width="%s" height="%s" rx="4.6" fill="none" stroke="#000" stroke-width="5" opacity="0.28" filter="url(#soft)"/>' % (f(sx), f(sy), f(sw), f(sh)))
    screen = g(s, clip_path='url(#scr)')
    o0, o = o, []
    # the chin: the maker's line, three keys and the power lamp
    cy = sy + sh + 7.5
    o.append(rect(sx, cy - 3.2, sw, 0.3, dark(HOOD, 0.18)))
    o.append(text(sx + 1, cy + 2.6, 'ELABORATORE', 2.4, P['soft'], 'Work Sans', 600, 0.42))
    for k, c in enumerate((P['ochre'], P['slate'], P['stone'])):
        o.append(path(rrect(sx + sw - 30 + k * 6.2, cy - 1.4, 4.6, 4.6, 0.6), c))
    o.append(circle(sx + sw - 4, cy + 0.9, 1.5, P['accent']))
    o.append(circle(sx + sw - 4.4, cy + 0.5, 0.5, light(P['accent'], 0.5)))
    # the keyboard: a low graphite wedge, cream keys, terracotta and ochre for the few that matter
    ky = 112
    o.append(path('M2,%s L8,%s L162,%s L168,%s Z' % (f(H), f(ky), f(ky), f(H)), GRAPH))
    o.append(path('M8,%s L162,%s L162.6,%s L7.4,%s Z' % (f(ky), f(ky), f(ky + 1.4), f(ky + 1.4)), light(GRAPH, 0.25)))
    rnd = random.Random(4)
    for row in range(3):
        y = ky + 3.2 + row * 4.6
        inset = 10 + (2 - row) * 0
        x = 12 + row * 2.2
        keys = 21 - row
        for k in range(keys):
            w = 6.2
            c = P['cream']
            if row == 1 and k == keys - 1: c, w = P['accent'], 9
            elif row == 2 and k in (0, keys - 1): c = P['ochre']
            elif row == 0 and k < 2: c = P['stone']
            o.append(path(rrect(x, y, w, 3.4, 0.6), c))
            o.append(rect(x, y + 2.6, w, 0.8, dark(c, 0.18)))
            x += w + 0.9
    # the case and keyboard are printed; the screen, its pixels, is not
    body = g(g(o0, filter='url(#gr)'), filter='url(#pr)') + screen + g(g(o, filter='url(#gr)'), filter='url(#pr)')
    return render('computer-room', body, W, H, S, OUT, defs=''.join(defs))

def bezel():
    # 480 × 360 px; the slices are 52 at the sides, 46 at the top and 90 at the foot (2x of
    # the station's 26, 23 and 45 CSS px); the middle is open for the glass
    W, H = 480, 360
    L, T, B = 52, 46, 90
    defs = [print_filter('pr', 0.6, 0.2, 71), grain_filter('gr', 0.5, 0.05, 72)]
    o = []
    outer = rrect(0, 0, W, H, (26, 26, 16, 16))
    hole = rrect(L, T, W - 2 * L, H - T - B, 16)
    defs.append(clip('face', path(outer + ' ' + hole, '#000', clip_rule='evenodd')))
    face = [rect(0, 0, W, H, HOOD), rect(0, 0, 14, H, light(HOOD, 0.4)), rect(0, 0, W, 5, light(HOOD, 0.5)),
            rect(W - 16, 0, 16, H, dark(HOOD, 0.1)),
            halftone(W - 40, 0, W - 16, H, lambda x, y: (x - (W - 40)) / 24, 3.0, dark(HOOD, 0.1)),
            rect(0, H - 12, W, 12, dark(HOOD, 0.08)),
            rect(L - 6, H - B + 38, W - 2 * L + 12, 1.2, dark(HOOD, 0.18))]
    o.append(g(face, clip_path='url(#face)'))
    # the graphite gasket round the glass
    o.append(path(rrect(L - 7, T - 7, W - 2 * L + 14, H - T - B + 14, 21) + ' ' + hole, GRAPH, fill_rule='evenodd'))
    o.append(path(outer, 'none', stroke=P['ink'], stroke_width=1.1, transform='translate(-1 0.8)', opacity=0.6))
    return render('bezel', g(g(o, filter='url(#gr)'), filter='url(#pr)'), W, H, 1, OUT, defs=''.join(defs))

if __name__ == '__main__':
    import sys
    for w in (sys.argv[1:] or ['room', 'bezel']): globals()[w]()
