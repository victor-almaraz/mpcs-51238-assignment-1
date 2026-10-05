# v21's shelf: one long oak board on two wire ladders, now holding the manual, the magazine
# in a walnut ledge with back issues, the miscellanea's folders upright in a sage file box,
# and the deck box; a screen print of ruled surfaces on the wall behind. Units are tenths
# of an em; the shelf picture's origin is the shelf unit's, moved up by TOP.
import math, random
from mcm import *
from render import render, REPO
OUT = REPO + '/v21/assets'
SCALE = 5
W, TOP, BOT = 400, 32, 120
H = TOP + BOT
PLANK = 96
GRAPH = '#2b2926'
KRAFT = '#bfae8e'
def Y(y): return y + TOP

def wall_print():
    # a sheet 196 × 104 behind the right half; its foot hidden by the magazine, the folders
    # and the deck box. Ochre, a terracotta disc, three string-art saddles in ink and paper
    x0, y0, w, h = 168, Y(-22), 196, 100
    out = [rect(x0 + 1.4, y0 + 1.8, w, h, '#28180c', opacity=0.16, filter='url(#soft)'), rect(x0, y0, w, h, P['paper'])]
    ix, iy, iw, ih = x0 + 5, y0 + 5, w - 10, h - 10
    G = iy + ih * 0.72
    art = [rect(ix, iy, iw, ih, P['ochre']), rect(ix, G, iw, ih - (G - iy), light(P['ochre'], 0.2)),
           circle(ix + 46, iy + 24, 13, P['accent'])]
    s1 = ruled((ix + 14, G), (ix + 62, iy + 8), (ix + 112, G), (ix + 62, G), 30, P['ink'], 0.24, both=False)
    s2 = ruled((ix + 62, iy + 8), (ix + 112, G), (ix + 168, iy + 22), (ix + 168, G), 24, P['ink'], 0.2, both=False)
    s3 = ruled((ix + 116, G), (ix + 150, iy + 34), (ix + iw - 2, G), (ix + 150, G), 18, P['paper'], 0.26, both=False)
    # the pavilion's plan as a hairline under the ground, a curve of nine points
    plan = path('M%s,%s C%s,%s %s,%s %s,%s' % (f(ix + 10), f(G + 9), f(ix + 60), f(G + 2), f(ix + 120), f(G + 16), f(ix + iw - 10), f(G + 6)), 'none', stroke=P['ink'], stroke_width=0.22, stroke_dasharray='1.2 1.2')
    art.append(g([s1, s2, s3, plan], transform='translate(0.35 -0.25)'))
    out.append(g(art, filter='url(#print)'))
    return out

def rails():
    out = []
    for x in (10, W - 19):
        lad = [rect(x, Y(0), 0.75, BOT, P['ink']), rect(x + 8.25, Y(0), 0.75, BOT, P['ink'])]
        for k in range(0, BOT, 6): lad.append(rect(x + 0.5, Y(k + 2.6), 8, 0.32, P['ink'], opacity=0.85))
        out.append(g(lad, opacity=0.9))
    return out

def plank():
    x0, y0, w, h = 0, Y(PLANK), W, 6.2
    out = [rect(4, y0 + 4, w - 2, 9, '#28180c', opacity=0.22, filter='url(#soft2)')]
    wood = [rect(x0, y0, w, h, P['oak']), rect(x0, y0, w, 1.3, P['oakl']), rect(x0, y0 + h - 0.8, w, 0.8, P['oakd'])]
    rnd = random.Random(14)
    for k in range(12):
        yy = y0 + 1.8 + rnd.random() * (h - 3); x1 = rnd.random() * w; x2 = x1 + 30 + rnd.random() * 90
        wood.append(path('M%s,%s C%s,%s %s,%s %s,%s' % (f(x1), f(yy), f(x1 + 20), f(yy - 0.8), f(x2 - 20), f(yy + 0.9), f(x2), f(yy + 0.2)), 'none', stroke=P['oakd'], stroke_width=0.22, opacity=0.6))
    wood.append(rect(0, y0, 1.2, h, P['oakd'])); wood.append(rect(w - 1.2, y0, 1.2, h, P['oakd']))
    out.append(g(wood, filter='url(#grain)'))
    return out

def bookend():
    x, b = 122, Y(PLANK)
    return [g([rect(x, b - 40, 2.4, 40, P['ink']), rect(x - 18, b - 1.6, 20.4, 1.6, P['ink']),
               rect(x + 0.5, b - 39.5, 0.5, 38, light(P['ink'], 0.25))], filter='url(#cast)')]

def shelf():
    defs = (print_filter('print', 1.2, 0.25, 23) + grain_filter('grain', 1.0, 0.06, 5) + shadow_filter('cast') +
            blur_filter('soft', 1.2) + blur_filter('soft2', 2.4))
    body = wall_print() + rails() + plank() + bookend()
    return render('shelf', ''.join(body), W, H, SCALE, OUT, defs=defs)

# ---- the magazine ledge: 76 × 90. Behind the live cover (62 × 83, its foot 2 above the
# board), two back issues; in front, the walnut lip that holds them
def cover(x, y, w, h, ground, ink, accent, seed, motif):
    out = [rect(x, y, w, h, ground)]
    if motif == 'disc':
        out.append(circle(x + w * 0.62, y + h * 0.58, w * 0.3, accent))
        out.append(halftone(x, y + h * 0.3, x + w, y + h, lambda X, Y_: 0.5 - abs((X - x) / w - 0.5), 1.1, ink, opacity=0.8))
    else:
        for k in range(7):
            out.append(rect(x + 4 + k * (w - 8) / 7, y + h * 0.38, (w - 8) / 14, h * 0.5 * (0.3 + 0.7 * ((k * 5 + seed) % 7) / 6), accent))
    out.append(rect(x + 3, y + 4, w * 0.62, 6.5, ink))
    out.append(rect(x + 3, y + 12, w * 0.3, 1.2, ink, opacity=0.8))
    return out

def mag_ledge():
    Wd, Hd = 76, 90
    defs = print_filter('pr', 1.4, 0.2, 31) + grain_filter('gr', 1.1, 0.05, 32) + blur_filter('soft', 0.8)
    back = [g(cover(1, 4, 58, 80, P['slate'], P['paper'], P['ochre'], 3, 'bars'), transform='rotate(-4 30 84)'),
            g(cover(16, 1, 58, 82, P['cream'], P['ink'], P['accent'], 5, 'disc'), transform='rotate(3 45 84)')]
    render('mag-back', g(g(back, filter='url(#gr)'), filter='url(#pr)'), Wd, Hd, SCALE, OUT, defs=defs)
    # the lip: a walnut board, its lit top, a brass rod across on two posts
    fy = Hd - 20
    front = [rect(4, fy + 6, 3, 14, P['walnutd']), rect(Wd - 7, fy + 6, 3, 14, P['walnutd']),
             path(rrect(0, fy + 8, Wd, 12, (0.8, 0.8, 1.2, 1.2)), P['walnut']), rect(0, fy + 8, Wd, 1.0, P['walnutl']),
             rect(0, fy + 8, 2.4, 12, light(P['walnut'], 0.08)), rect(Wd - 2.4, fy + 8, 2.4, 12, P['walnutd']),
             rect(1.5, fy + 1.6, Wd - 3, 1.2, P['brass']), rect(1.5, fy + 1.6, Wd - 3, 0.4, light(P['brass'], 0.45)),
             rect(5, fy + 1.6, 1.0, 6.6, dark(P['brass'], 0.25)), rect(Wd - 6, fy + 1.6, 1.0, 6.6, dark(P['brass'], 0.25))]
    rr = random.Random(6)
    for k in range(4):
        yy = rr.uniform(fy + 10, Hd - 2); x1 = rr.uniform(-5, 30); x2 = x1 + rr.uniform(30, 50)
        front.append(path('M%s,%s C%s,%s %s,%s %s,%s' % (f(x1), f(yy), f(x1 + 12), f(yy - 0.9), f(x2 - 12), f(yy + 0.8), f(x2), f(yy)), 'none', stroke=P['walnutd'], stroke_width=0.3, opacity=0.8))
    return render('mag-front', g(g(front, filter='url(#gr)'), filter='url(#pr)'), Wd, Hd, SCALE, OUT, defs=defs)

# ---- the file box: 46 × 74, sage enamel, three folders standing in it, the front one's
# tab lettered for the miscellanea, papers showing at their tops
def file_box():
    Wd, Hd = 46, 74
    defs = print_filter('pr', 1.4, 0.2, 41) + grain_filter('gr', 1.1, 0.05, 42)
    o = []
    folders = [(4, 10, 40, P['stone'], 26), (2, 6, 42, P['linen'], 8), (3, 14, 40, KRAFT, None)]
    for x, top, w, c, tab in folders:
        o.append(rect(x + 2, top - 2.2, w - 4, 5, P['paper']))
        o.append(line(x + 3, top - 1.2, x + w - 3, top - 1.2, P['stone'], 0.15))
        o.append(path(rrect(x, top, w, Hd - top, 0.6), c))
        o.append(rect(x, top, w, 1.0, light(c, 0.22)))
        if tab is not None: o.append(path(rrect(x + tab, top - 5, 13, 5.4, (1, 1, 0, 0)), c))
    # the front folder's tab, lettered
    tx, ty = 10, 14
    o.append(path(rrect(tx, ty - 7.6, 26, 8, (1.4, 1.4, 0, 0)), KRAFT))
    o.append(rect(tx + 1.6, ty - 6.2, 22.8, 4.2, P['paper']))
    o.append(text(tx + 13, ty - 3.0, 'XENAKIS', 2.5, P['ink'], 'Jost', 600, 0.2, 'middle'))
    o.append(rect(tx + 15, ty + 4, 0.5, 30, P['accent']))   # a string tie, down the folder
    # the box's front: low, sage, with a cut curve up its sides and a card holder
    fy = 34
    face = 'M0,%s L0,%s C6,%s 10,%s 14,%s L32,%s C36,%s 40,%s 46,%s L46,%s Z' % (
        f(Hd), f(fy + 4), f(fy + 4), f(fy), f(fy), f(fy), f(fy), f(fy + 4), f(fy + 4), f(Hd))
    o.append(path(face, P['sage']))
    o.append(path('M0,%s C6,%s 10,%s 14,%s L32,%s C36,%s 40,%s 46,%s' % (f(fy + 4), f(fy + 4), f(fy), f(fy), f(fy), f(fy), f(fy + 4), f(fy + 4)), 'none', stroke=light(P['sage'], 0.3), stroke_width=0.9))
    o.append(rect(Wd - 6, fy + 4, 6, Hd - fy - 4, dark(P['sage'], 0.14)))
    o.append(halftone(Wd - 14, fy + 4, Wd - 6, Hd, lambda x, y: (x - (Wd - 14)) / 8, 0.9, dark(P['sage'], 0.14)))
    o.append(rect(11, fy + 14, 24, 9, P['brass'])); o.append(rect(12.2, fy + 15.2, 21.6, 6.6, P['paper']))
    o.append(text(23, fy + 19.6, 'MISC.', 2.4, P['ink'], 'Work Sans', 600, 0.3, 'middle'))
    return render('file-box', g(g(o, filter='url(#gr)'), filter='url(#pr)'), Wd, Hd, SCALE, OUT, defs=defs)

if __name__ == '__main__':
    import sys
    for w in (sys.argv[1:] or ['shelf', 'mag_ledge', 'file_box']): globals()[w]()
