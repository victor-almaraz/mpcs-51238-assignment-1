# v21's computer on the desk, drawn again in more detail: a moulded hood in a warm white
# that turns with the light, its bezel chamfered round a convex screen (glare, scan lines,
# a darkening curve), the maker's plate brushed, buttons and a glowing power lamp, a swivel
# stand, and a keyboard whose keys have tops, skirts and legends. 170 × 130 units.
import math, random
from mcm import *
from mcm2 import *
from render import render, REPO
OUT = REPO + '/v21/assets'
HOOD = '#e8e2d5'
GRAPH = '#2b2926'
DESKTOP = 'file://' + REPO + '/v20/assets/desktop.png'

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
    s = [rect(sx, sy, sw, sh, '#000'),
         '<image href="%s" x="%s" y="%s" width="%s" height="%s" preserveAspectRatio="xMidYMid slice" style="image-rendering:pixelated"/>' % (DESKTOP, f(sx), f(sy + 4), f(sw), f(sh - 4)),
         rect(sx, sy, sw, 4, '#fff'), rect(sx, sy + 4, sw, px * 0.6, '#000')]
    for k, wd in enumerate((5, 4.2, 4.6, 3.6, 4.4)): s.append(rect(sx + 8 + k * 8, sy + 1.5, wd, 1.0, '#000'))
    s.append(rect(sx + sw - 12, sy + 1.4, 8, 1.2, '#000'))
    def win(x, y, w, hgt, tw):
        out = [rect(x + 1, y + 1, w, hgt, '#000'), rect(x, y, w, hgt, '#fff'), rect(x, y, w, hgt, 'none', stroke='#000', stroke_width=px * 0.7)]
        for k in range(4): out.append(rect(x + 1, y + 1 + k * 0.9, w - 2, 0.45, '#000'))
        out += [rect(x + w / 2 - tw / 2, y + 0.6, tw, 3.4, '#fff'), rect(x, y + 4.4, w, px * 0.6, '#000')]
        return out
    s += win(sx + 10, sy + 12, 46, 34, 14)
    for r in range(6): s.append(rect(sx + 13, sy + 19.5 + r * 3.6, [30, 22, 34, 16, 27, 20][r], 1.1, '#000'))
    s += win(sx + 62, sy + 25, 40, 30, 12)
    for c in range(9): s.append(rect(sx + 64.5 + c * 4, sy + 32, 3, 2, '#00f' if c % 3 else '#ff0'))
    s.append(rect(sx + 64.5, sy + 37, 35, 14, '#fff', stroke='#000', stroke_width=0.4))
    for c in range(14):
        for r in range(4):
            if (c * 3 + r * 5) % 7 < 2: s.append(rect(sx + 66 + c * 2.4, sy + 39 + r * 2.8, 0.9, 1.6, '#000'))
    # the glass: faint scan lines, the tube's curve darkening the edges, a broad soft glare
    s.append(g([rect(sx, sy + k * 0.9, sw, 0.3, '#000', opacity=0.12) for k in range(int(sh / 0.9))]))
    s.append(rect(sx, sy, sw, sh, D.rad([(0, '#000000', 0), (0.62, '#000000', 0), (1, '#000000', 0.55)], 0.5, 0.5, 0.75)))
    s.append(ellipse(sx + sw * 0.3, sy + sh * 0.2, sw * 0.42, sh * 0.3, D.rad([(0, '#ffffff', 0.16), (1, '#ffffff', 0)])))
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
