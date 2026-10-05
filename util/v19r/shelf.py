# The bookshelf and what stands on it, less the three volumes (separate pictures, as they
# are buttons): a screen print of ruled surfaces on the wall, a String-style shelf of one
# oak board on two wire ladders, a steel bookend, three books lying flat, a sounding
# sculpture of brass rods and a stoneware bottle with dry grass.
# Units are tenths of an em; the picture's origin is the shelf unit's, moved up by TOP.
import math, random
from mcm import *
from render import render, REPO
OUT = REPO + '/v19/assets'
SCALE = 5
W, TOP, BOT = 300, 32, 120
H = TOP + BOT
PLANK = 96   # the board's top, in shelf-unit units

def Y(y): return y + TOP

def wall_print():
    # a sheet 180 × 110, its lower left hidden by the volumes; ochre, two saddles of ruled
    # lines in ink after the Philips Pavilion's paraboloids, and a terracotta disc
    x0, y0, w, h = 50, Y(-26), 180, 110
    out = [rect(x0 + 1.4, y0 + 1.8, w, h, '#28180c', opacity=0.16, filter='url(#soft)')]
    out.append(rect(x0, y0, w, h, P['paper']))
    ix, iy, iw, ih = x0 + 5, y0 + 5, w - 10, h - 15
    art = [rect(ix, iy, iw, ih, P['ochre'])]
    art.append(circle(ix + iw * 0.74, iy + ih * 0.3, 15, P['accent']))
    # a strip of paper colour, the ground the saddles stand on
    art.append(rect(ix, iy + ih * 0.8, iw, ih * 0.2, light(P['ochre'], 0.22)))
    G = iy + ih * 0.8
    # string-art saddles: one family of straight lines between two edges, its envelope the curve
    s1 = ruled((ix + 58, G), (ix + 104, iy + 8), (ix + 150, G), (ix + 104, G), 30, P['ink'], 0.24, both=False)
    s1b = ruled((ix + 104, iy + 8), (ix + 150, G), (ix + iw - 4, iy + 36), (ix + iw - 4, G), 22, P['ink'], 0.2, both=False)
    s2 = ruled((ix + 8, G), (ix + 44, iy + 26), (ix + 84, G), (ix + 44, G), 22, P['paper'], 0.24, both=False)
    art.append(g([s2, s1, s1b], transform='translate(0.35 -0.25)'))
    out.append(g(art, filter='url(#print)'))
    return out

def rails():
    out = []
    for x in (12, 279):
        lad = [rect(x, Y(0), 0.75, BOT, P['ink']), rect(x + 8.25, Y(0), 0.75, BOT, P['ink'])]
        for k in range(0, BOT, 6):
            lad.append(rect(x + 0.5, Y(k + 2.6), 8, 0.32, P['ink'], opacity=0.85))
        out.append(g(lad, opacity=0.9))
    return out

def plank():
    x0, y0, w, h = 0, Y(PLANK), W, 6.2
    out = [rect(4, y0 + 4, w - 2, 9, '#28180c', opacity=0.22, filter='url(#soft2)')]
    wood = [rect(x0, y0, w, h, P['oak']), rect(x0, y0, w, 1.3, P['oakl']), rect(x0, y0 + h - 0.8, w, 0.8, P['oakd'])]
    rnd = random.Random(4)
    for k in range(9):
        yy = y0 + 1.8 + rnd.random() * (h - 3)
        x1 = rnd.random() * w; x2 = x1 + 30 + rnd.random() * 90
        d = 'M%s,%s C%s,%s %s,%s %s,%s' % (f(x1), f(yy), f(x1 + 20), f(yy - 0.8), f(x2 - 20), f(yy + 0.9), f(x2), f(yy + 0.2))
        wood.append(path(d, 'none', stroke=P['oakd'], stroke_width=0.22, opacity=0.6))
    # end grain at the board's two ends
    wood.append(rect(0, y0, 1.2, h, P['oakd'])); wood.append(rect(w - 1.2, y0, 1.2, h, P['oakd']))
    out.append(g(wood, filter='url(#grain)'))
    return out

def bookend():
    x, b = 136, Y(PLANK)
    return [g([rect(x, b - 42, 2.4, 42, P['ink']), rect(x, b - 1.8, 22, 1.8, P['ink']),
               rect(x + 0.5, b - 41.5, 0.5, 40, light(P['ink'], 0.25))], filter='url(#cast)')]

clips = []
def lying_books():
    # three books lying flat, spines out; the titles of the room's own library
    b = Y(PLANK) - 1.8
    books = [(147, 54, 8.6, P['sage'], P['paper'], 'MUSIQUES FORMELLES', ''),
             (150, 46, 6.2, P['paper'], P['ink'], 'LE MODULOR', 'II'),
             (145.5, 50, 8.0, P['ink'], P['ochre'], 'NEUE GRAFIK', '1958')]
    out = []; y = b
    for x, w, h, c, ink, t, a in books:
        if False: pass
        y -= h
        cid = 'bk%d' % len(out)
        clips.append(clip(cid, path(rrect(x, y, w, h, (0.8, 0.8, 0.8, 0.8)), '#000')))
        bk = [path(rrect(x, y, w, h, (0.8, 0.8, 0.8, 0.8)), c),
              rect(x, y, w, h * 0.28, light(c, 0.14)), rect(x, y + h * 0.8, w, h * 0.2, dark(c, 0.16)),
              halftone(x, y + h * 0.28, x + w, y + h * 0.48, lambda X, Y_: 1 - (Y_ - (y + h * 0.28)) / (h * 0.2), 0.7, light(c, 0.14)),
              rect(x + 3, y + h / 2 - 0.2, 0.3, 0.4, ink),
              text(x + 5, y + h / 2 + 0.85, t, 2.3, ink, 'Work Sans', 600, 0.14),
              text(x + w - 3, y + h / 2 + 0.85, a, 2.0, ink, 'Jost', 400, 0.16, 'end', opacity=0.85)]
        out.append(g(bk, clip_path='url(#%s)' % cid))
    return [g(out, filter='url(#cast)')]

def sonambient():
    # a cluster of brass rods on a block, each capped with a small cylinder, that sound when
    # they touch: after Harry Bertoia's Sonambient sculptures of the 1960s and 70s
    x0, b = 206, Y(PLANK) - 1.8 + 1.8
    out = [rect(x0, b - 3.4, 24, 3.4, dark(P['brass'], 0.35)), rect(x0, b - 3.4, 24, 0.7, dark(P['brass'], 0.15))]
    rnd = random.Random(9)
    rods = []
    n = 11
    for k in range(n):
        x = x0 + 2 + k * 2.0
        hgt = 34 + 6 * math.sin(k / (n - 1) * math.pi) + rnd.uniform(-1.5, 1.5)
        lean = rnd.uniform(-0.6, 0.6) + (k - n / 2) * 0.12
        tx, ty = x + lean, b - 3.4 - hgt
        rods.append(line(x, b - 3.4, tx, ty + 2.4, P['brass'], 0.34))
        rods.append(path(rrect(tx - 0.75, ty, 1.5, 3.2, 0.3), P['brass']))
        rods.append(rect(tx - 0.75, ty, 0.5, 3.2, light(P['brass'], 0.35)))
    out.append(g(rods))
    return [g(out, filter='url(#cast)')]

def bottle():
    # a stoneware bottle in a matt white glaze, a band of slate at the shoulder, and three
    # stalks of dry grass
    cx, b = 256, Y(PLANK)
    out = []
    rnd = random.Random(2)
    for k, (dx, hh, lean) in enumerate([(-0.8, 44, -7), (0.4, 52, 2.5), (1.0, 40, 9)]):
        x1, y1 = cx + dx, b - 30
        x2, y2 = cx + dx + lean, b - 30 - hh * 0.5
        d = 'M%s,%s Q%s,%s %s,%s' % (f(x1), f(y1), f(x1 + lean * 0.2), f(y1 - hh * 0.3), f(x2), f(y2))
        out.append(path(d, 'none', stroke=P['oakd'], stroke_width=0.3))
        for j in range(7):
            t = 0.55 + j * 0.07
            px = x1 + (x2 - x1) * t; py = y1 + (y2 - y1) * t
            for s in (-1, 1):
                out.append(line(px, py, px + s * 1.6 + lean * 0.06, py - 1.8, P['oakd'], 0.24))
    body = 'M%s,%s C%s,%s %s,%s %s,%s L%s,%s C%s,%s %s,%s %s,%s Z' % (
        f(cx - 1.6), f(b - 31), f(cx - 2), f(b - 24), f(cx - 9.5), f(b - 22), f(cx - 9.5), f(b - 11), f(cx - 8.5), f(b),
        f(cx + 9.5), f(b + 0.0001), f(cx + 9.5), f(b - 22), f(cx + 1.6), f(b - 31))
    body = 'M%s,%s L%s,%s C%s,%s %s,%s %s,%s L%s,%s L%s,%s C%s,%s %s,%s %s,%s L%s,%s Z' % (
        f(cx - 1.7), f(b - 32), f(cx - 1.7), f(b - 25), f(cx - 2.5), f(b - 21), f(cx - 9.5), f(b - 20), f(cx - 9.5), f(b - 12),
        f(cx - 8.6), f(b), f(cx + 8.6), f(b), f(cx + 9.5), f(b - 20), f(cx + 2.5), f(b - 21), f(cx + 1.7), f(b - 25), f(cx + 1.7), f(b - 32))
    v = [path(body, P['ivory'])]
    v.append(g([rect(cx - 10, b - 20.5, 20, 3.0, P['slate']), rect(cx - 10, b - 16.5, 20, 0.6, P['slate']),
                halftone(cx + 1, b - 32, cx + 10, b, lambda X, Y_: (X - cx - 1) / 9 * 0.9, 0.75, P['stone'])], clip_path='url(#bottle)'))
    v.append(path(body, 'none', stroke=P['ink'], stroke_width=0.18, transform='translate(-0.3 0.2)', opacity=0.7))
    out.append(g(v))
    return [g(out, filter='url(#cast)')], clip('bottle', path(body, '#000'))

def main():
    bt, bclip = bottle()
    defs = (print_filter('print', 1.2, 0.27, 21) + grain_filter('grain', 1.0, 0.06, 4) + shadow_filter('cast') +
            blur_filter('soft', 1.2) + blur_filter('soft2', 2.4) + bclip)
    body = wall_print() + rails() + plank() + bookend() + lying_books() + sonambient() + bt
    defs += ''.join(clips)
    return render('shelf', ''.join(body), W, H, SCALE, OUT, defs=defs)

if __name__ == '__main__':
    main()
