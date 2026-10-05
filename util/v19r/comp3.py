# v22's computer on the desk (v21's, its screen showing v22's vector desktop), drawn again in more detail: a moulded hood in a warm white
# that turns with the light, its bezel chamfered round a convex screen (glare, scan lines,
# a darkening curve), the maker's plate brushed, buttons and a glowing power lamp, a swivel
# stand, and a keyboard whose keys have tops, skirts and legends. 170 × 130 units.
import math, random
from mcm import *
from mcm2 import *
from render import render, REPO
OUT = REPO + '/v22/assets'
HOOD = '#e8e2d5'
GRAPH = '#2b2926'
DESKTOP = 'file://' + REPO + '/v22/assets/screen/desktop.svg'

def room():
    W, H = 170, 130
    D = Defs()
    o = []
    # the stand: a neck and a round foot, graphite, lit along its top
    o.append(ellipse(85, 109.5, 30, 2.6, '#000', opacity=0.3, filter=D.blur(1.0)))
    o.append(path('M70,99 L100,99 L96,106 L74,106 Z', D.lin([(0, '#47443f'), (1, '#1d1c1a')])))
    o.append(path(rrect(56, 105, 58, 4.6, 2.2), D.lin([(0, '#55524c'), (0.35, '#2e2c29'), (1, '#121110')])))
    o.append(rect(58, 105.3, 54, 0.5, '#ffffff', opacity=0.25))
    # the hood
    hx, hy, hw, hh = 18, 2, 134, 98
    hood = rrect(hx, hy, hw, hh, (10, 10, 6, 6))
    o.append(soft_shadow(D, hood, 1.8, 2.4, 2.0, 0.38))
    cp = D.clip(path(hood, '#000'))
    o.append(g([rect(hx, hy, hw, hh, D.lin([(0, light(HOOD, 0.45)), (0.12, HOOD), (0.85, dark(HOOD, 0.04)), (1, dark(HOOD, 0.16))])),
                rect(hx, hy, hw, hh, D.lin([(0, '#ffffff', 0.35), (0.1, '#ffffff', 0), (0.86, '#000000', 0), (1, '#000000', 0.14)], 0, 0, 1, 0)),
                # the parting line between the front and the shell
                rect(hx, hy + 4.2, hw, 0.35, dark(HOOD, 0.2)), rect(hx, hy + 4.6, hw, 0.3, '#ffffff', opacity=0.6),
                # vents along the top
                g([path(rrect(hx + 92 + k * 3.4, hy + 1.2, 2.0, 2.2, 1.0), dark(HOOD, 0.3)) for k in range(8)])], clip_path=cp))
    o.append(path(hood, 'none', stroke='#6f685c', stroke_width=0.3))
    # the bezel: a chamfer falling to the glass, light on its lower edge and dark on its upper
    sx, sy, sw, sh = 28, 12, 114, 72
    bz = rrect(sx - 5, sy - 5, sw + 10, sh + 10, 9)
    o.append(path(bz, D.lin([(0, dark(HOOD, 0.22)), (0.5, dark(HOOD, 0.08)), (1, light(HOOD, 0.4))])))
    o.append(path(rrect(sx - 2.2, sy - 2.2, sw + 4.4, sh + 4.4, 7), D.lin([(0, '#141312'), (1, '#2c2a27')])))
    # the screen, its pixels untouched by the print (the caller keeps it out of the filters)
    scr = rrect(sx, sy, sw, sh, 6)
    scp = D.clip(path(scr, '#000'))
    px = 0.9
    # the desktop it runs, in vector as it is: the night picture, a pale menu bar, two
    # windows of paper with their buttons, and the column of icons at the right
    s = [rect(sx, sy, sw, sh, '#0c1624'),
         '<image href="%s" x="%s" y="%s" width="%s" height="%s" preserveAspectRatio="xMidYMax slice"/>' % (DESKTOP, f(sx), f(sy + 3), f(sw), f(sh - 3)),
         rect(sx, sy, sw, 3, '#f3efe6')]
    s.append(g([circle(sx + 2.6 + k * 0.9, sy + 1.5, 0.28, '#b5462b' if k in (2, 3) else '#1e1d1b') for k in range(5)]))
    for k, wd in enumerate((2.6, 2.4, 2.6, 2.0, 3.6, 3.2)): s.append(path(rrect(sx + 8 + k * 5.2, sy + 1.1, wd, 0.75, 0.37), '#1e1d1b', opacity=0.7))
    s.append(path(rrect(sx + sw - 9, sy + 1.1, 6, 0.75, 0.37), '#1e1d1b', opacity=0.5))
    def win(x, y, w, hgt, active):
        out = [path(rrect(x + 0.6, y + 1.4, w, hgt, 1.6), '#000', opacity=0.35, filter=D.blur(0.9)),
               path(rrect(x, y, w, hgt, 1.6), '#f7f4ec'),
               path(rrect(x, y, w, 4.4, (1.6, 1.6, 0, 0)), '#e7e0d2'), rect(x, y + 4.4, w, 0.2, '#c9c0ae'),
               circle(x + 2.2, y + 2.2, 0.85, '#b5462b' if active else '#cfc7b8'), circle(x + 4.6, y + 2.2, 0.85, '#c99a2e' if active else '#cfc7b8'),
               path(rrect(x + w / 2 - 6, y + 1.8, 12, 0.8, 0.4), '#1e1d1b', opacity=0.6)]
        return out
    # the Read Me behind: the fans of glissandi and its prose
    s += win(sx + 6, sy + 8, 44, 50, False)
    for k in range(9):
        t = k / 8
        s.append(line(sx + 9, sy + 18 + (t - .5) * 2, sx + 47, sy + 14 + t * 8, '#b5462b', 0.25))
        s.append(line(sx + 9, sy + 14 + t * 8, sx + 47, sy + 18 - (t - .5) * 2, '#2b4560', 0.25))
    s.append(path(rrect(sx + 9, sy + 26, 22, 2.2, 0.5), '#2b4560', opacity=0.75))
    for r in range(7): s.append(path(rrect(sx + 9, sy + 31 + r * 2.7, [36, 34, 37, 30, 36, 33, 20][r], 0.9, 0.45), '#6b665e', opacity=0.7))
    # the Editor in front: the ruler, the gutter, the lines of a program, the margin at 72
    ex, ey, ew, eh = sx + 30, sy + 18, 58, 46
    s += win(ex, ey, ew, eh, True)
    s.append(rect(ex, ey + 4.6, ew, 4.4, '#ebe5d8'))
    s.append(path(rrect(ex + 2, ey + 5.6, 6, 2.4, 0.7), '#2b4560'))
    s.append(path(rrect(ex + 9, ey + 5.6, 7, 2.4, 0.7), '#fffdf8', stroke='#bfb5a2', stroke_width=0.15))
    s.append(rect(ex, ey + 9, ew, eh - 13.4, '#fffdf8'))
    s.append(rect(ex, ey + 9, 5, eh - 13.4, '#f3efe6'))
    s.append(rect(ex + 5 + 44, ey + 9, 0.25, eh - 13.4, '#b5462b'))
    code = [(0, 20), (5, 9), (2, 26), (5, 12), (5, 8), (5, 9), (5, 7), (5, 18), (2, 10), (2, 22), (5, 4), (5, 3)]
    for r, (ind, ln) in enumerate(code):
        y = ey + 10.4 + r * 2.5
        s.append(rect(ex + 1.6, y, 1.6, 0.8, '#a39b8e'))
        s.append(path(rrect(ex + 6.2 + ind * 0.62, y, ln * 0.62, 0.8, 0.3), '#1e1d1b' if r else '#7d8a78', opacity=0.85))
    s.append(rect(ex, ey + eh - 4.2, ew, 4.2, '#ebe5d8'))
    # the icons at the right of the desk, in two columns
    cols = ['#d6a540', '#e6e3dc', '#2b4560', '#f4efe3', '#9a6136', '#d6a540', '#7d8a78', '#d6a540', '#49555a', '#d6a540']
    for k, c in enumerate(cols):
        y = sy + 7 + (k // 2) * 9.6
        x = sx + sw - 16 + (k % 2) * 7.4
        s.append(path(rrect(x, y, 4.2, 3.8, 0.9), c))
        s.append(path(rrect(x - 0.4, y + 5, 5, 0.7, 0.35), '#f3efe6', opacity=0.75))
    s.append(path(rrect(sx + sw - 8.6, sy + sh - 9, 4, 4.4, 0.6), '#cfccc4'))
    # the glass: flat, with one soft glare and a faint fall-off at its edges
    s.append(rect(sx, sy, sw, sh, D.rad([(0, '#000000', 0), (0.75, '#000000', 0), (1, '#000000', 0.32)], 0.5, 0.5, 0.75)))
    s.append(ellipse(sx + sw * 0.3, sy + sh * 0.2, sw * 0.42, sh * 0.3, D.rad([(0, '#ffffff', 0.12), (1, '#ffffff', 0)])))
    screen = g(s, clip_path=scp)
    o0, o = o, []
    # the chin: the maker's plate, a speaker grille, three buttons and the power lamp
    cy = sy + sh + 8
    for r in range(3):
        for c in range(10): o.append(circle(sx + 2 + c * 1.6, cy - 1.6 + r * 1.6, 0.4, dark(HOOD, 0.35)))
    o.append(path(rrect(sx + 22, cy - 2.6, 30, 5.2, 0.6), D.lin([(0, '#ebe9e3'), (0.5, '#c9c6be'), (1, '#a9a69e')], 0, 0, 0, 1)))
    o.append(g([line(sx + 22, cy - 2.6 + k * 0.35, sx + 52, cy - 2.6 + k * 0.35, '#ffffff', 0.06, opacity=0.4) for k in range(15)]))
    o.append(text(sx + 37, cy + 1.0, 'ELABORATORE', 2.2, '#3a3833', 'Work Sans', 600, 0.42, 'middle'))
    o.append(text(sx + 37.12, cy + 1.12, 'ELABORATORE', 2.2, '#ffffff', 'Work Sans', 600, 0.42, 'middle', opacity=0.35))
    for k, c in enumerate((P['ochre'], P['slate'], '#d8d1c3')):
        bx = sx + sw - 31 + k * 6.6
        o.append(path(rrect(bx + 0.3, cy - 1.6, 5, 5, 0.8), '#000', opacity=0.35, filter=D.blur(0.35)))
        o.append(path(rrect(bx, cy - 2.0, 5, 5, 0.8), D.lin([(0, light(c, 0.3)), (0.2, c), (1, dark(c, 0.25))])))
        o.append(rect(bx + 0.6, cy - 1.7, 3.8, 0.5, '#ffffff', opacity=0.5))
    o.append(circle(sx + sw - 4, cy + 0.5, 3.2, D.rad([(0, '#ff8a5c', 0.55), (1, '#ff8a5c', 0)])))
    o.append(circle(sx + sw - 4, cy + 0.5, 1.3, D.rad([(0, '#ffd2bd'), (0.45, '#e2603a'), (1, '#8a2a14')], 0.4, 0.35, 0.7)))
    # the keyboard: a graphite case, its sloped top lit, keys with tops and skirts
    ky = 111
    o.append(ellipse(85, H - 0.6, 86, 1.6, '#000', opacity=0.3, filter=D.blur(0.8)))
    o.append(path('M1,%s L9,%s L161,%s L169,%s Z' % (f(H), f(ky), f(ky), f(H)), D.lin([(0, '#4a4743'), (0.2, '#34322f'), (1, '#1a1918')])))
    o.append(path('M9,%s L161,%s L161.8,%s L8.2,%s Z' % (f(ky), f(ky), f(ky + 1.2), f(ky + 1.2)), '#ffffff', opacity=0.18))
    legends = ['QWERTYUIOP', 'ASDFGHJKL', 'ZXCVBNM']
    for row in range(3):
        y = ky + 2.8 + row * 5.0
        x = 13 + row * 2.4
        keys = 20 - row
        for k in range(keys):
            w = 6.0
            c = '#efe8d8'
            if row == 1 and k == keys - 1: c, w = P['accent'], 9.4
            elif row == 2 and k in (0, keys - 1): c = P['ochre']
            elif row == 0 and k < 2: c = '#d4ccbb'
            o.append(path(rrect(x, y, w, 4.2, 0.8), dark(c, 0.3)))
            o.append(path(rrect(x + 0.45, y + 0.2, w - 0.9, 3.0, 0.7), D.lin([(0, light(c, 0.3)), (1, c)])))
            o.append(rect(x + 0.8, y + 0.4, w - 1.6, 0.35, '#ffffff', opacity=0.5))
            idx = k - 3
            if 0 <= idx < len(legends[row]) and c == '#efe8d8':
                o.append(text(x + w / 2, y + 2.4, legends[row][idx], 1.5, '#6a645a', 'Work Sans', 600, 0, 'middle'))
            x += w + 0.7
    body = (g(g(o0, filter='url(#gr)'), filter='url(#pr)') + screen + g(g(o, filter='url(#gr)'), filter='url(#pr)'))
    defs = D.out() + print_filter('pr', 1.4, 0.1, 61) + grain_filter('gr', 1.1, 0.02, 62)
    return render('computer-room', body, W, H, 6, OUT, defs=defs)

if __name__ == '__main__':
    room()
