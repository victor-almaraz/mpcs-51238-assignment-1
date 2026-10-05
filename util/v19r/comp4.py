# v22's computer, a modern one, drawn in the room's manner: a thin all-in-one display, its
# glass edge to edge within a narrow black border, an aluminium rim and a sage chin, on an
# aluminium stand that bends back to its foot; a slim aluminium keyboard with pale low keys
# and a glass trackpad. On its screen, v22's vector desktop. 170 x 130 units, as v21's.
# Also the nine-slice frame of the display seen face on in its station (bezel.webp).
import math
from mcm import *
from mcm2 import *
from render import render, REPO
OUT = REPO + '/v22/assets'
DESKTOP = 'file://' + REPO + '/v22/assets/screen/desktop.svg'
SAGE = '#b4c0ad'
ALU = [(0, '#f1f0ec'), (0.5, '#d4d2cc'), (1, '#a9a69f')]

def screen(D, sx, sy, sw, sh):
    """the desktop, scaled into the glass: the night picture, menu bar, two windows, icons"""
    k = sw / 114.0
    def X(v): return sx + v * k
    def Yy(v): return sy + v * k
    s = [rect(sx, sy, sw, sh, '#0c1624'),
         '<image href="%s" x="%s" y="%s" width="%s" height="%s" preserveAspectRatio="xMidYMax slice"/>' % (DESKTOP, f(sx), f(sy + 3 * k), f(sw), f(sh - 3 * k)),
         rect(sx, sy, sw, 3 * k, '#f3efe6')]
    s.append(g([circle(X(2.6 + j * 0.9), Yy(1.5), 0.28 * k, '#b5462b' if j in (2, 3) else '#1e1d1b') for j in range(5)]))
    for j, wd in enumerate((2.6, 2.4, 2.6, 2.0, 3.6, 3.2)): s.append(path(rrect(X(8 + j * 5.2), Yy(1.1), wd * k, 0.75 * k, 0.37 * k), '#1e1d1b', opacity=0.7))
    def win(x, y, w, hgt, active):
        x, y, w, hgt = X(x), Yy(y), w * k, hgt * k
        return [path(rrect(x + 0.6, y + 1.4, w, hgt, 1.6 * k), '#000', opacity=0.35, filter=D.blur(0.9)),
                path(rrect(x, y, w, hgt, 1.6 * k), '#f7f4ec'),
                path(rrect(x, y, w, 4.4 * k, (1.6 * k, 1.6 * k, 0, 0)), '#e7e0d2'),
                circle(x + 2.2 * k, y + 2.2 * k, 0.85 * k, '#b5462b' if active else '#cfc7b8'), circle(x + 4.6 * k, y + 2.2 * k, 0.85 * k, '#c99a2e' if active else '#cfc7b8'),
                path(rrect(x + w / 2 - 6 * k, y + 1.8 * k, 12 * k, 0.8 * k, 0.4 * k), '#1e1d1b', opacity=0.6)]
    s += win(6, 8, 44, 50, False)
    for j in range(9):
        t = j / 8
        s.append(line(X(9), Yy(18 + (t - .5) * 2), X(47), Yy(14 + t * 8), '#b5462b', 0.25 * k))
        s.append(line(X(9), Yy(14 + t * 8), X(47), Yy(18 - (t - .5) * 2), '#2b4560', 0.25 * k))
    s.append(path(rrect(X(9), Yy(26), 22 * k, 2.2 * k, 0.5 * k), '#2b4560', opacity=0.75))
    for r in range(7): s.append(path(rrect(X(9), Yy(31 + r * 2.7), [36, 34, 37, 30, 36, 33, 20][r] * k, 0.9 * k, 0.45 * k), '#6b665e', opacity=0.7))
    s += win(30, 18, 58, 46, True)
    s.append(rect(X(30), Yy(22.6), 58 * k, 4.4 * k, '#ebe5d8'))
    s.append(path(rrect(X(32), Yy(23.6), 6 * k, 2.4 * k, 0.7 * k), '#2b4560'))
    s.append(rect(X(30), Yy(27), 58 * k, 32.6 * k, '#fffdf8'))
    s.append(rect(X(30), Yy(27), 5 * k, 32.6 * k, '#f3efe6'))
    s.append(rect(X(79), Yy(27), 0.25 * k, 32.6 * k, '#b5462b'))
    code = [(0, 20), (5, 9), (2, 26), (5, 12), (5, 8), (5, 9), (5, 7), (5, 18), (2, 10), (2, 22), (5, 4), (5, 3)]
    for r, (ind, ln) in enumerate(code):
        y = 28.4 + r * 2.5
        s.append(rect(X(31.6), Yy(y), 1.6 * k, 0.8 * k, '#a39b8e'))
        s.append(path(rrect(X(36.2 + ind * 0.62), Yy(y), ln * 0.62 * k, 0.8 * k, 0.3 * k), '#1e1d1b' if r else '#7d8a78', opacity=0.85))
    s.append(path(rrect(X(30), Yy(59.8), 58 * k, 4.2 * k, (0, 0, 1.6 * k, 1.6 * k)), '#ebe5d8'))
    cols = ['#d6a540', '#e6e3dc', '#2b4560', '#f4efe3', '#9a6136', '#d6a540', '#7d8a78', '#d6a540', '#49555a', '#d6a540']
    for j, c in enumerate(cols):
        x, y = 114 - 16 + (j % 2) * 7.4, 7 + (j // 2) * 9.6
        s.append(path(rrect(X(x), Yy(y), 4.2 * k, 3.8 * k, 0.9 * k), c))
        s.append(path(rrect(X(x - 0.4), Yy(y + 5), 5 * k, 0.7 * k, 0.35 * k), '#f3efe6', opacity=0.75))
    # the glass: one broad soft reflection across it, from the window at the left
    s.append(path('M%s,%s L%s,%s L%s,%s L%s,%s Z' % (f(sx), f(sy), f(sx + sw * 0.42), f(sy), f(sx + sw * 0.18), f(sy + sh), f(sx), f(sy + sh)), '#ffffff', opacity=0.06))
    return s

def room():
    W, H = 170, 130
    D = Defs()
    o = []
    # the stand: a sheet of aluminium bent back to its foot, seen from the front as a tapering
    # column with its foot's edge in front of it
    o.append(ellipse(85, 111.2, 28, 1.6, '#000', opacity=0.3, filter=D.blur(1.0)))
    o.append(path('M73,84 L97,84 L95,108 L75,108 Z', D.lin([(0, '#b9b6af'), (0.4, '#e9e7e2'), (0.7, '#c9c6bf'), (1, '#8f8c85')], 0, 0, 1, 0)))
    o.append(rect(73, 84, 24, 6, '#000', opacity=0.18, filter=D.blur(1.2)))
    o.append(path(rrect(66, 107.4, 38, 3.4, 1.4), D.lin(ALU)))
    o.append(rect(67, 107.5, 36, 0.4, '#ffffff', opacity=0.8))
    # the display: an aluminium rim round a black border round the glass, a sage chin below
    dx, dy, dw, dh = 14, 1, 142, 88
    shape = rrect(dx, dy, dw, dh, 4.2)
    o.append(soft_shadow(D, shape, 1.2, 2.0, 1.8, 0.35))
    cp = D.clip(path(shape, '#000'))
    chin_y = dy + dh - 12
    o.append(g([rect(dx, dy, dw, dh, '#141414'),
                rect(dx, chin_y, dw, dh - (chin_y - dy), D.lin([(0, light(SAGE, 0.25)), (0.4, SAGE), (1, dark(SAGE, 0.25))])),
                rect(dx, chin_y, dw, 0.35, '#ffffff', opacity=0.5)], clip_path=cp))
    o.append(path(shape, 'none', stroke=D.lin(ALU, 0, 0, 1, 1), stroke_width=0.9))
    # the maker's mark on the chin: a small sieve of points, as the desktop's menu glyph
    for r in range(3):
        for c in range(5):
            on = (r * 5 + c) % 5 in (2, 3)
            o.append(circle(85 - 4 + c * 2, chin_y + 4.2 + r * 1.7, 0.55 if on else 0.3, '#b5462b' if on else '#5f6a5a'))
    sx, sy, sw, sh = dx + 2.6, dy + 2.6, dw - 5.2, chin_y - dy - 4.2
    scr = rrect(sx, sy, sw, sh, 0.8)
    screen_g = g(screen(D, sx, sy, sw, sh), clip_path=D.clip(path(scr, '#000')))
    o0, o = o, []
    # the keyboard: a slim aluminium slab with low pale keys, and the trackpad beside it
    ky = 116
    o.append(ellipse(70, H - 0.4, 62, 1.2, '#000', opacity=0.28, filter=D.blur(0.7)))
    kb = rrect(10, ky, 120, 13, 2.2)
    o.append(path(kb, D.lin([(0, '#f1f0ec'), (0.6, '#d9d7d1'), (1, '#a9a69f')])))
    o.append(path(kb, 'none', stroke='#8f8c85', stroke_width=0.3))
    rows = [(14, 14, 7.0), (15.6, 13, 7.0), (17.4, 12, 7.0)]
    for r, (x0, n, w) in enumerate(rows):
        y = ky + 1.6 + r * 3.7
        x = x0
        for j in range(n):
            ww = w
            c = '#f7f6f2'
            if r == 1 and j == n - 1: ww, c = 11, '#f7f6f2'
            o.append(path(rrect(x, y + 0.25, ww - 0.9, 3.0, 0.6), '#9c998f', opacity=0.6))
            o.append(path(rrect(x, y, ww - 0.9, 2.9, 0.6), D.lin([(0, '#ffffff'), (1, '#e8e6e0')])))
            x += ww
    o.append(path(rrect(46, ky + 1.6 + 3 * 3.7 - 0.6, 48, 1.4, 0.5), D.lin([(0, '#ffffff'), (1, '#e8e6e0')])))
    tp = rrect(136, ky + 0.6, 26, 12.4, 2.0)
    o.append(path(tp, D.lin([(0, '#f4f3ef'), (1, '#c9c6bf')])))
    o.append(path(rrect(137.2, ky + 1.6, 23.6, 10.4, 1.6), D.lin([(0, '#ffffff', 0.5), (1, '#ffffff', 0)])))
    o.append(path(tp, 'none', stroke='#8f8c85', stroke_width=0.3))
    body = g(g(o0, filter='url(#gr)'), filter='url(#pr)') + screen_g + g(g(o, filter='url(#gr)'), filter='url(#pr)')
    defs = D.out() + print_filter('pr', 1.4, 0.06, 71) + grain_filter('gr', 1.1, 0.015, 72)
    return render('computer-room', body, W, H, 6, OUT, defs=defs)

def bezel():
    # the frame of the display seen face on, for a nine-slice border: 12 units at the top and
    # sides, 44 at the foot (the chin, with the mark), the middle left empty for the screen.
    # 200 x 200 units at 2 px a unit.
    W, H = 200, 200
    D = Defs(); o = []
    sh = rrect(0.6, 0.6, W - 1.2, H - 1.2, 9)
    cp = D.clip(path(sh, '#000'))
    chin = H - 44
    o.append(g([rect(0, 0, W, H, '#141414'),
                rect(0, chin, W, H - chin, D.lin([(0, light(SAGE, 0.25)), (0.4, SAGE), (1, dark(SAGE, 0.2))])),
                rect(0, chin, W, 0.6, '#ffffff', opacity=0.5),
                rect(0, 0, W, 6, D.lin([(0, '#ffffff', 0.12), (1, '#ffffff', 0)]))], clip_path=cp))
    o.append(path(sh, 'none', stroke=D.lin(ALU, 0, 0, 1, 1), stroke_width=1.2))
    # the glass's own edge, a hairline inside the border
    o.append(path(rrect(11.4, 11.4, W - 22.8, chin - 13, 1.4), 'none', stroke='#2a2a2a', stroke_width=0.8))
    body = g(o)
    out = render('bezel', body, W, H, 2, OUT, defs=D.out(), fmt='png')
    # the middle must be clear so the screen shows through: cut it out
    from PIL import Image, ImageDraw
    p = OUT + '/bezel.png'
    im = Image.open(p).convert('RGBA')
    m = Image.new('L', im.size, 255)
    ImageDraw.Draw(m).rounded_rectangle([24, 24, im.width - 25, (chin - 2) * 2 - 1], radius=3, fill=0)
    im.putalpha(Image.composite(im.split()[3], Image.new('L', im.size, 0), m))
    im.save(OUT + '/bezel.webp', 'WEBP', quality=92, method=6, alpha_quality=100)
    import os; os.remove(p)
    print('bezel.webp', im.size)

if __name__ == '__main__':
    import sys
    for w in (sys.argv[1:] or ['room', 'bezel']): globals()[w]()
