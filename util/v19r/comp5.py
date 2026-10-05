# v22's computer on the desk, drawn again in detail: a modern all-in-one after the thin
# coloured machines of the 2020s, in the room's sage. The display: its glass edge to edge
# under a narrow black border with the camera at its head, a soft sheen across the glass, a
# chin of sage aluminium brushed across with the desktop's sieve of points engraved in it,
# and the rim of the shell showing along its sides. On the glass, the desktop itself (a
# capture of v22's computer page). The stand: one sheet of sage aluminium bent back to its
# foot, lit at its left edge, with the chin's shadow across its top. The keyboard: a slim
# slab with a function row, the full rows of low keys with their legends, the inverted T of
# arrows; and a glass trackpad. 170 x 130 units at 8 px a unit.
import os as _os; UTIL = _os.path.normpath(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..')); REPO = _os.path.dirname(UTIL)
import base64, io
from PIL import Image
from mcm import *
from mcm2 import *
from render import render, REPO
OUT = REPO + '/v22/assets'
SHOT = UTIL + '/v22/deskshot.png'
SAGE, SAGE_L, SAGE_D = '#b7c3b0', '#d2dbcc', '#8e9c88'

def shot_uri(w):
    im = Image.open(SHOT).convert('RGB')
    im = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
    b = io.BytesIO(); im.save(b, 'PNG')
    return 'data:image/png;base64,' + base64.b64encode(b.getvalue()).decode(), im.size

def keyboard(D, o, x0, x1, back, front, lip):
    """the keyboard on the desk, seen as the room is seen, from the front and a little above:
    a thin wedge, its top foreshortened from the back edge to the front, its rows of low keys
    foreshortened with it, and the slab's front lip on the desk"""
    inset = 1.6
    top = 'M%s,%s L%s,%s L%s,%s L%s,%s Z' % (f(x0 + inset), f(back), f(x1 - inset), f(back), f(x1), f(front), f(x0), f(front))
    o.append(ellipse((x0 + x1) / 2, lip + 0.4, (x1 - x0) / 2 + 2, 1.0, '#000', opacity=0.3, filter=D.blur(0.7)))
    o.append(path(top, D.lin([(0, '#cfccc5'), (1, '#ecebe6')])))
    o.append(path('M%s,%s L%s,%s L%s,%s Q%s,%s %s,%s L%s,%s Q%s,%s %s,%s Z' % (f(x0), f(front), f(x1), f(front), f(x1), f(lip - 0.6), f(x1), f(lip), f(x1 - 1), f(lip), f(x0 + 1), f(lip), f(x0), f(lip), f(x0), f(lip - 0.6)),
                  D.lin([(0, '#f4f3ef'), (0.4, '#d9d7d1'), (1, '#9f9c94')])))
    o.append(rect(x0 + 0.6, front, x1 - x0 - 1.2, 0.18, '#ffffff', opacity=0.8))
    # the keys: six rows, each a strip of key tops between the back and the front
    rows = 6
    span = front - back - 0.9
    rh = span / rows
    layouts = [[1.0] * 13 + [1.5], [1.0] * 13 + [1.5], [1.5] + [1.0] * 13, [1.75] + [1.0] * 11 + [1.75], [2.25] + [1.0] * 10 + [2.25], [1, 1, 1, 1.25, 5.0, 1.25, 1, 1, 1, 1]]
    for r, row in enumerate(layouts):
        y0 = back + 0.5 + r * rh
        t = (y0 - back) / (front - back)
        lx = x0 + inset * (1 - t) + 1.2; rx = x1 - inset * (1 - t) - 1.2
        units = sum(row); gap = 0.32
        u = (rx - lx - gap * (len(row) - 1)) / units
        x = lx
        kh = rh * (0.55 if r == 0 else 0.78)
        for j, ku in enumerate(row):
            kw = ku * u
            accent = (r, j) == (3, len(row) - 1)
            o.append(path(rrect(x, y0 + kh * 0.55, kw, kh * 0.6, 0.25), '#8a877f', opacity=0.6))
            o.append(path(rrect(x, y0, kw, kh, 0.3), D.lin([(0, '#ffffff'), (1, '#e9e7e1')]) if not accent else D.lin([(0, light(SAGE, 0.35)), (1, SAGE)])))
            x += kw + gap

def trackpad(D, o, x0, x1, back, front, lip):
    inset = 0.5
    top = 'M%s,%s L%s,%s L%s,%s L%s,%s Z' % (f(x0 + inset), f(back), f(x1 - inset), f(back), f(x1), f(front), f(x0), f(front))
    o.append(ellipse((x0 + x1) / 2, lip + 0.4, (x1 - x0) / 2 + 1.5, 0.9, '#000', opacity=0.3, filter=D.blur(0.6)))
    o.append(path(top, D.lin([(0, '#e6e4de'), (0.5, '#f7f6f2'), (1, '#dedcd6')])))
    o.append(path(top, D.lin([(0, '#ffffff', 0.5), (0.6, '#ffffff', 0)], 0, 0, 1, 1)))
    o.append(path('M%s,%s L%s,%s L%s,%s L%s,%s Z' % (f(x0), f(front), f(x1), f(front), f(x1 - 0.4), f(lip), f(x0 + 0.4), f(lip)), D.lin([(0, '#e6e4de'), (1, '#9f9c94')])))

def room():
    W, H = 170, 130
    D = Defs()
    o = []
    # ---- the stand: a sage sheet bent back to its foot, which rests on the desk behind the
    # keyboard; seen from the front, its upright face tapers a little as it leans back
    FOOT = 125.2                                      # the foot, on the desk behind the keyboard
    o.append(ellipse(85, FOOT + 1.2, 32, 1.6, '#000', opacity=0.35, filter=D.blur(1.0)))
    o.append(path('M70.5,96 L99.5,96 L97.6,%s L72.4,%s Z' % (f(FOOT - 3), f(FOOT - 3)), D.lin([(0, light(SAGE, 0.18)), (0.18, SAGE_L), (0.55, SAGE), (1, SAGE_D)], 0, 0, 1, 0)))
    o.append(path('M70.5,96 L99.5,96 L99.4,100 L70.6,100 Z', '#1c2218', opacity=0.35, filter=D.blur(0.9)))   # the chin's shadow
    o.append(path('M70.5,96 L71.2,96 L73,%s L72.4,%s Z' % (f(FOOT - 3), f(FOOT - 3)), '#ffffff', opacity=0.45))
    # where the sheet bends into the foot, and the foot's front edge on the desk
    o.append(path('M72.4,%s L97.6,%s C98.6,%s 103.6,%s 104.4,%s L65.6,%s C66.4,%s 71.4,%s 72.4,%s Z' % (
        f(FOOT - 3), f(FOOT - 3), f(FOOT - 3), f(FOOT - 2.4), f(FOOT - 1.4), f(FOOT - 1.4), f(FOOT - 2.4), f(FOOT - 3), f(FOOT - 3)), D.lin([(0, dark(SAGE, 0.05)), (1, SAGE_D)])))
    o.append(path(rrect(64.6, FOOT - 1.6, 40.8, 1.8, 0.8), D.lin([(0, SAGE_L), (0.5, SAGE), (1, dark(SAGE, 0.3))])))
    # ---- the display
    dx, dy, dw, dh = 13, 11.5, 144, 86
    chin_h = 12.5
    shell = rrect(dx, dy, dw, dh, 3.4)
    o.append(soft_shadow(D, shell, 1.0, 2.2, 1.8, 0.32))
    cp = D.clip(path(shell, '#000'))
    chin_y = dy + dh - chin_h
    face = [rect(dx, dy, dw, dh, '#121212'),
            rect(dx, dy, dw, chin_y - dy, D.lin([(0, '#ffffff', 0.05), (0.4, '#ffffff', 0), (1, '#ffffff', 0.02)], 0, 0, 1, 1)),
            rect(dx, chin_y, dw, chin_h, D.lin([(0, light(SAGE, 0.3)), (0.12, SAGE_L), (0.6, SAGE), (1, dark(SAGE, 0.2))]))]
    # the chin brushed across: hairlines of light and shade
    rnd = random.Random(5)
    for k in range(60):
        y = chin_y + 0.4 + rnd.uniform(0, chin_h - 0.8)
        face.append(rect(dx, y, dw, 0.08, '#ffffff' if rnd.random() < 0.5 else '#3c4636', opacity=rnd.uniform(0.04, 0.12)))
    face.append(rect(dx, chin_y, dw, 0.3, '#ffffff', opacity=0.55))
    face.append(rect(dx, chin_y - 0.2, dw, 0.2, '#000000', opacity=0.6))
    o.append(g(face, clip_path=cp))
    # the shell's rim, sage aluminium, showing along the edges, lit on the left and the top
    o.append(path(shell, 'none', stroke=D.lin([(0, SAGE_L), (0.5, SAGE), (1, SAGE_D)], 0, 0, 1, 0), stroke_width=0.8))
    o.append(path(rrect(dx + 0.4, dy + 0.4, dw - 0.8, dh - 0.8, 3.0), 'none', stroke='#ffffff', stroke_width=0.18, opacity=0.35))
    # the camera at the head of the border
    o.append(circle(85, dy + 1.25, 0.55, '#1f2326'))
    o.append(circle(85, dy + 1.25, 0.28, '#2e3a48'))
    o.append(circle(84.9, dy + 1.15, 0.09, '#9fb4c9', opacity=0.9))
    # the mark engraved in the chin: the sieve 5@2 | 5@3, fifteen points
    for r in range(3):
        for c in range(5):
            on = (r * 5 + c) % 5 in (2, 3)
            x, y = 85 - 3.6 + c * 1.8, chin_y + 4.4 + r * 1.75
            rr = 0.48 if on else 0.26
            o.append(circle(x, y + 0.1, rr, '#ffffff', opacity=0.6))
            o.append(circle(x, y, rr, '#b5462b' if on else '#6e7a68'))
    # ---- the screen: the desktop itself, under the glass
    sx, sy = dx + 2.2, dy + 2.6
    sw, sh = dw - 4.4, chin_y - sy - 2.0
    uri, (iw, ih) = shot_uri(1300)
    scp = D.clip(rect(sx, sy, sw, sh, '#000'))
    screen = [rect(sx, sy, sw, sh, '#0c1624'),
              '<image href="%s" x="%s" y="%s" width="%s" height="%s" preserveAspectRatio="xMidYMid slice"/>' % (uri, f(sx), f(sy), f(sw), f(sh)),
              # the glass: one broad reflection from the window, at the left, and a fall of light
              path('M%s,%s L%s,%s L%s,%s L%s,%s Z' % (f(sx), f(sy), f(sx + sw * 0.34), f(sy), f(sx + sw * 0.12), f(sy + sh), f(sx), f(sy + sh)), '#ffffff', opacity=0.07),
              path('M%s,%s L%s,%s L%s,%s L%s,%s Z' % (f(sx + sw * 0.38), f(sy), f(sx + sw * 0.43), f(sy), f(sx + sw * 0.21), f(sy + sh), f(sx + sw * 0.16), f(sy + sh)), '#ffffff', opacity=0.04),
              rect(sx, sy, sw, sh, D.lin([(0, '#000000', 0), (0.85, '#000000', 0), (1, '#000000', 0.12)]))]
    screen_g = g(screen, clip_path=scp)
    o0, o = o, []
    # ---- the keyboard and the trackpad
    keyboard(D, o, 16, 124, 119.6, 127.4, 129.3)
    trackpad(D, o, 129, 156, 120.6, 127.4, 128.9)
    body = g(o0, filter='url(#gr)') + screen_g + g(o, filter='url(#gr)')
    defs = D.out() + grain_filter('gr', 1.4, 0.008, 72)
    return render('computer-room', body, W, H, 8, OUT, defs=defs)

def bezel():
    # the frame of the display face on, for a nine-slice border: 12 units at the top and the
    # sides, 46 at the foot (the chin), the middle empty for the screen. 200 x 200 at 2 px.
    W, H = 200, 200
    D = Defs(); o = []
    chin = H - 46
    sh = rrect(0.5, 0.5, W - 1, H - 1, 8)
    cp = D.clip(path(sh, '#000'))
    rnd = random.Random(9)
    face = [rect(0, 0, W, H, '#121212'),
            rect(0, chin, W, H - chin, D.lin([(0, light(SAGE, 0.3)), (0.12, SAGE_L), (0.6, SAGE), (1, dark(SAGE, 0.2))]))]
    for k in range(70):
        y = chin + 0.5 + rnd.uniform(0, H - chin - 1)
        face.append(rect(0, y, W, 0.12, '#ffffff' if rnd.random() < 0.5 else '#3c4636', opacity=rnd.uniform(0.04, 0.1)))
    face += [rect(0, chin, W, 0.5, '#ffffff', opacity=0.55), rect(0, chin - 0.4, W, 0.4, '#000', opacity=0.6),
             rect(0, 0, W, 5, D.lin([(0, '#ffffff', 0.1), (1, '#ffffff', 0)]))]
    o.append(g(face, clip_path=cp))
    o.append(path(sh, 'none', stroke=D.lin([(0, SAGE_L), (0.5, SAGE), (1, SAGE_D)], 0, 0, 1, 0), stroke_width=1.2))
    o.append(path(rrect(1.2, 1.2, W - 2.4, H - 2.4, 7.4), 'none', stroke='#ffffff', stroke_width=0.3, opacity=0.35))
    render('bezel', g(o), W, H, 2, OUT, defs=D.out(), fmt='png')
    from PIL import ImageDraw
    import os
    p = OUT + '/bezel.png'
    im = Image.open(p).convert('RGBA')
    m = Image.new('L', im.size, 255)
    ImageDraw.Draw(m).rectangle([24, 24, im.width - 25, chin * 2 - 1], fill=0)
    im.putalpha(Image.composite(im.split()[3], Image.new('L', im.size, 0), m))
    im.save(OUT + '/bezel.webp', 'WEBP', quality=94, method=6, alpha_quality=100)
    os.remove(p)
    print('bezel.webp', im.size)

if __name__ == '__main__':
    import sys
    for w in (sys.argv[1:] or ['room', 'bezel']): globals()[w]()
