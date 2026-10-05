# v21's shelf and what stands on it, drawn again in more detail: the manual's cloth volumes
# (rounded spines, raised bands, headbands, gilt or ink stamping, pasted labels), the
# magazine's walnut ledge and back issues, the miscellanea's enamel file box, and the shelf
# itself (an oak board on steel wire ladders, a steel bookend, the screen print pinned up).
import math, random
from mcm import *
from mcm2 import *
from render import render, REPO
OUT = REPO + '/v21/assets'
S = 6
KRAFT = '#c2ad86'

def fin(name, o, W, H, D, seed, extra=''):
    defs = D.out() + extra + print_filter('pr', 1.4, 0.1, seed) + grain_filter('gr', 1.1, 0.02, seed + 1)
    return render(name, g(g(o, filter='url(#gr)'), filter='url(#pr)'), W, H, S, OUT, defs=defs)

VOLS = [
    dict(n='1', title='FORTRAN', sub='THE LANGUAGE', w=32, h=98, cloth='#c7bba5', ink='#1e1d1b', gilt=False, emblem='card', head='#b5462b'),
    dict(n='2', title='SIEVES', sub='AFTER XENAKIS', w=29, h=91, cloth='#49555a', ink=None, gilt=True, emblem='sieve', head='#c99a2e'),
    dict(n='3', title='MUSIC', sub='AND TAPE', w=30.5, h=95, cloth='#a8402a', ink=None, gilt=True, emblem='reel', head='#e8dcc0'),
]

def emblem(kind, cx, y, ink, cloth):
    out = []
    if kind == 'card':
        for r in range(12):
            for c in range(3):
                x = cx - 4.6 + c * 3.6; yy = y + r * 1.45
                if (r * 7 + c * 5) % 4 == 0 or (r == 0 and c == 1): out.append(rect(x, yy, 2.0, 1.1, ink))
                else: out.append(rect(x, yy, 2.0, 1.1, 'none', stroke=ink, stroke_width=0.2, opacity=0.6))
        return out, 12 * 1.45
    if kind == 'sieve':
        out.append(line(cx, y - 0.6, cx, y + 14 * 1.25 + 0.6, ink, 0.18))
        for k in range(15):
            yy = y + k * 1.25
            out.append(circle(cx - 3.2, yy, 0.62 if k % 3 == 0 else 0.22, ink))
            if k % 5 == 2: out.append(circle(cx + 3.2, yy, 0.55, 'none', stroke=ink, stroke_width=0.28))
            else: out.append(circle(cx + 3.2, yy, 0.22, ink))
            if k % 3 == 0 or k % 5 == 2: out.append(rect(cx - 1.3, yy - 0.2, 2.6, 0.4, ink))
        return out, 14 * 1.25
    R1, R2 = 4.4, 3.0
    c1, c2 = y + R1, y + 2 * R1 + 1.6 + R2
    out.append(line(cx + R1 - 0.1, c1, cx + R2 - 0.1, c2, ink, 0.32))
    for cyy, R, pk in ((c1, R1, 0.72), (c2, R2, 0.42)):
        out.append(circle(cx, cyy, R, 'none', stroke=ink, stroke_width=0.32))
        out.append(circle(cx, cyy, R * pk, ink))
        for k in range(3):
            a = math.radians(-90 + k * 120)
            out.append(circle(cx + R * 0.36 * math.cos(a), cyy + R * 0.36 * math.sin(a), R * 0.13, cloth))
        out.append(circle(cx, cyy, R * 0.09, cloth))
    return out, c2 + R2 - y

def volume(v):
    w, h, cloth = v['w'], v['h'], v['cloth']
    D = Defs(); o = []
    shape = rrect(0, 0, w, h, (2.6, 2.6, 0.6, 0.6))
    cp = D.clip(path(shape, '#000'))
    ink = gilt(D) if v['gilt'] else v['ink']
    body = [rect(0, 0, w, h, cloth),
            # the round of the spine, lit from the left
            rect(0, 0, w, h, D.lin([(0, '#000000', 0.32), (0.08, '#000000', 0.05), (0.3, '#ffffff', 0.2), (0.5, '#ffffff', 0.05), (0.8, '#000000', 0.12), (1, '#000000', 0.38)], 0, 0, 1, 0)),
            # the weave
            hatch(0, 0, w, h, 0.45, dark(cloth, 0.3), 0.08, angle=0, opacity=0.25),
            hatch(0, 0, w, h, 0.45, light(cloth, 0.4), 0.08, angle=90, opacity=0.18)]
    # the headcap and its stitched headband, the tail likewise
    body.append(rect(0, 0, w, 2.2, D.lin([(0, dark(cloth, 0.35)), (1, dark(cloth, 0.1))])))
    for k in range(int(w / 0.8)):
        body.append(rect(k * 0.8, 0.4, 0.5, 1.2, v['head'] if k % 2 else '#f1e9d6', opacity=0.9))
    body.append(rect(0, h - 1.4, w, 1.4, dark(cloth, 0.3)))
    # raised bands: a ridge, lit above and shaded below
    for by in (8.2, h - 9.4):
        body.append(rect(0, by, w, 1.3, light(cloth, 0.14)))
        body.append(rect(0, by + 1.3, w, 0.5, dark(cloth, 0.35)))
        body.append(rect(0, by - 0.3, w, 0.3, '#ffffff', opacity=0.25))
    stamp = []
    for yy in (5.0, 6.1):
        stamp.append(rect(2.2, yy, w - 4.4, 0.3, ink))
    em, eh = emblem(v['emblem'], w / 2, 13, ink, cloth)
    stamp += em
    ty = 13 + eh + 3.6
    stamp.append(text(0, 0, v['title'], 5.9, ink, 'Work Sans', 600, 0.14, transform='translate(%s %s) rotate(90)' % (f(w / 2 + 0.2), f(ty))))
    stamp.append(text(0, 0, v['sub'], 2.6, ink, 'Jost', 400, 0.22, transform='translate(%s %s) rotate(90)' % (f(w / 2 - 5.4), f(ty + 0.4)), opacity=0.9))
    for yy in (h - 5.6, h - 4.5):
        stamp.append(rect(2.2, yy, w - 4.4, 0.3, ink))
    body.append(g(stamp, transform='translate(0.12 -0.1)'))
    # the stamping pressed in: a hair of shadow above each mark
    body.append(g(stamp, transform='translate(0 -0.18)', opacity=0.25, style='mix-blend-mode:multiply'))
    # the label, pasted on, its edge lifting a little
    lx, ly, lw, lh = w / 2 - 6.5, h - 21.5, 13, 11.5
    body += [rect(lx + 0.3, ly + 0.5, lw, lh, '#000', opacity=0.25, filter=D.blur(0.3)),
             rect(lx, ly, lw, lh, D.lin([(0, '#fbf7ec'), (1, '#e8e1cf')])),
             rect(lx + 0.9, ly + 0.9, lw - 1.8, lh - 1.8, 'none', stroke='#1e1d1b', stroke_width=0.18),
             text(w / 2, ly + lh - 3.0, v['n'], 7.2, '#1e1d1b', 'Arvo', 700, 0, 'middle')]
    o.append(g(body, clip_path=cp))
    o.append(path(shape, 'none', stroke=dark(cloth, 0.45), stroke_width=0.2, opacity=0.7))
    return fin('vol-' + v['n'], o, w, h, D, 11 + int(v['n']))

# ---- the magazine's ledge: back issues behind the live cover; in front, a walnut lip with
# a brass rail on two posts
def back_issue(D, x, y, w, h, ground, accent, ink, num, kind, seed):
    out = [rect(x, y, w, h, ground)]
    cp = D.clip(rect(x, y, w, h, '#000'))
    art = []
    if kind == 'disc':
        art.append(circle(x + w * 0.66, y + h * 0.6, w * 0.32, accent))
        art.append(halftone(x, y + h * 0.3, x + w, y + h, lambda X, Y: 0.55 - abs((X - x) / w - 0.5), 1.4, ink, angle=45, opacity=0.85))
    else:
        for k in range(7):
            art.append(rect(x + 4 + k * (w - 8) / 7, y + h * 0.42, (w - 8) / 14, h * 0.48 * (0.3 + 0.7 * ((k * 5 + seed) % 7) / 6), accent))
        art.append(halftone(x, y + h * 0.36, x + w, y + h, lambda X, Y: 0.3 * (Y - y - h * 0.36) / (h * 0.64), 1.3, ink, angle=15, opacity=0.7))
    out.append(g(art, clip_path=cp))
    out.append(text(x + 3, y + 10.5, 'Moiré', 8.2, ink, 'Playfair Display', 400, -0.02, style='font-style:italic'))
    out.append(text(x + w - 3, y + 5, num, 2.4, ink, 'Jost', 600, 0.2, 'end'))
    out.append(rect(x + 3, y + 13, w * 0.42, 1.0, ink, opacity=0.8))
    out.append(rect(x + 3, y + 15, w * 0.3, 0.8, ink, opacity=0.6))
    out.append(rect(x, y, w, h, D.lin([(0, '#ffffff', 0.1), (0.3, '#ffffff', 0), (1, '#000000', 0.15)], 0, 0, 1, 0)))
    return out

def mag_ledge():
    W, H = 76, 90
    D = Defs()
    back = [g([rect(1.5, 4.5, 58, 80, '#000', opacity=0.3, filter=D.blur(0.8))] + back_issue(D, 1, 4, 58, 80, '#49555a', '#c99a2e', '#f4efe2', 'No. 2', 'bars', 3), transform='rotate(-4 30 84)'),
            g([rect(16.5, 1.5, 58, 82, '#000', opacity=0.3, filter=D.blur(0.8))] + back_issue(D, 16, 1, 58, 82, '#efe6d2', '#b5462b', '#1e1d1b', 'No. 3', 'disc', 5), transform='rotate(3 45 84)')]
    fin('mag-back', back, W, H, D, 31)
    D = Defs()
    fy = H - 20
    lip = rrect(0, fy + 8, W, 12, (0.8, 0.8, 1.4, 1.4))
    front = [soft_shadow(D, lip, 0.4, 1.0, 0.8, 0.35),
             rect(4, fy + 6, 3, 14, '#2f1f15'), rect(W - 7, fy + 6, 3, 14, '#2f1f15'),
             g([wood(D, 0, fy + 8, W, 12, P['walnut'], seed=12, lines=10, arches=1, contrast=1.2),
                rect(0, fy + 8, W, 12, D.lin([(0, '#ffffff', 0.2), (0.12, '#ffffff', 0), (0.85, '#000000', 0), (1, '#000000', 0.3)]))], clip_path=D.clip(path(lip, '#000'))),
             rect(0, fy + 8, W, 0.5, '#ffffff', opacity=0.35)]
    rod = D.lin([(0, '#f7e7b4'), (0.4, '#c9a14e'), (1, '#6e521e')])
    for px_ in (5, W - 6):
        front.append(rect(px_, fy + 1.6, 1.0, 6.6, D.lin([(0, '#e8cf8a'), (1, '#7d5c22')], 0, 0, 1, 0)))
    front.append(rect(1.5, fy + 1.4, W - 3, 1.5, rod))
    for ex in (1.5, W - 1.5): front.append(circle(ex, fy + 2.15, 1.0, D.rad([(0, '#fff2c8'), (1, '#8d6a2a')], 0.35, 0.3, 0.8)))
    return fin('mag-front', front, W, H, D, 32)

# ---- the file box: sage enamel with a gloss, its rim rolled, three kraft folders standing
# in it with papers showing; the front folder's typed tab
def file_box():
    W, H = 46, 74
    D = Defs(); o = []
    o.append(ellipse(23, 73.6, 22, 0.8, '#000', opacity=0.35, filter=D.blur(0.6)))
    folders = [(4, 10, 40, '#d8d1c3', 26), (2, 6, 42, '#c7bba5', 8), (3, 14, 40, KRAFT, None)]
    for x, top, w, c, tab in folders:
        rnd = random.Random(top)
        for k in range(3):
            px = x + 2 + k * 1.2
            o.append(rect(px, top - 2.6 + k * 0.6, w - 4 - k * 2, 5, '#fbfaf3' if k % 2 else '#f1ede2'))
            o.append(line(px + 1, top - 1.6 + k * 0.6, px + w * 0.6, top - 1.6 + k * 0.6, '#9a978f', 0.12, opacity=0.6))
        o.append(path(rrect(x, top, w, H - top, 0.6), D.lin([(0, light(c, 0.15)), (1, dark(c, 0.15))], 0, 0, 1, 0)))
        o.append(rect(x, top, w, 0.7, '#ffffff', opacity=0.35))
        if tab is not None: o.append(path(rrect(x + tab, top - 5, 13, 5.4, (1, 1, 0, 0)), D.lin([(0, light(c, 0.15)), (1, c)])))
    tx, ty = 10, 14
    o.append(path(rrect(tx, ty - 7.6, 26, 8, (1.4, 1.4, 0, 0)), D.lin([(0, light(KRAFT, 0.15)), (1, KRAFT)])))
    o.append(rect(tx + 1.6, ty - 6.2, 22.8, 4.2, '#fbf8ef'))
    o.append(text(tx + 13, ty - 3.0, 'XENAKIS', 2.4, '#2a2826', 'Courier Prime', 700, 0.12, 'middle'))
    o.append(rect(tx + 15, ty + 4, 0.5, 30, '#b5462b'))
    fy = 34
    face = 'M0,%s L0,%s C6,%s 10,%s 14,%s L32,%s C36,%s 40,%s 46,%s L46,%s Z' % (f(H), f(fy + 4), f(fy + 4), f(fy), f(fy), f(fy), f(fy), f(fy + 4), f(fy + 4), f(H))
    o.append(soft_shadow(D, face, 0.3, 0.8, 0.6, 0.35))
    o.append(path(face, D.lin([(0, '#a1ad99'), (0.15, '#86937f'), (0.7, '#7d8a78'), (1, '#55604f')], 0, 0, 1, 0)))
    o.append(path(face, D.lin([(0, '#ffffff', 0.25), (0.25, '#ffffff', 0), (1, '#000000', 0.15)])))
    o.append(path('M0,%s C6,%s 10,%s 14,%s L32,%s C36,%s 40,%s 46,%s' % (f(fy + 4), f(fy + 4), f(fy), f(fy), f(fy), f(fy), f(fy + 4), f(fy + 4)), 'none', stroke='#d4dccf', stroke_width=0.9))
    o.append(rect(4, fy + 9, 2.6, 26, '#ffffff', opacity=0.25, filter=D.blur(0.8)))
    hx, hy = 11, fy + 14
    o.append(rect(hx, hy, 24, 9, D.lin([(0, '#f3dfa0'), (0.5, '#c9a14e'), (1, '#8d6a2a')], 0, 0, 1, 1)))
    o.append(rect(hx + 1.2, hy + 1.2, 21.6, 6.6, '#fbf8ef'))
    o.append(text(hx + 12, hy + 5.6, 'MISC.', 2.3, '#2a2826', 'Courier Prime', 700, 0.2, 'middle'))
    return fin('file-box', o, W, H, D, 41)

# ---- the shelf: an oak board on two steel wire ladders, a steel bookend, the screen print
W, TOP, BOT = 400, 32, 120
SH = TOP + BOT
PLANK = 96
def Y(y): return y + TOP
def shelf():
    D = Defs(); o = []
    # the print: ochre, a terracotta disc, string-art saddles; pinned at its top corners
    x0, y0, w, h = 168, Y(-22), 196, 100
    o.append(rect(x0 + 1.2, y0 + 1.8, w, h, '#000', opacity=0.22, filter=D.blur(1.2)))
    o.append(rect(x0, y0, w, h, D.lin([(0, '#fbf8ef'), (1, '#efe9da')])))
    ix, iy, iw, ih = x0 + 5, y0 + 5, w - 10, h - 10
    G = iy + ih * 0.72
    art = [rect(ix, iy, iw, ih, P['ochre']), rect(ix, G, iw, ih - (G - iy), light(P['ochre'], 0.2)), circle(ix + 46, iy + 24, 13, P['accent']),
           halftone(ix, iy, ix + iw, G, lambda X, Y_: 0.18 * (1 - (Y_ - iy) / (G - iy)), 1.6, dark(P['ochre'], 0.25), angle=45)]
    art.append(g([ruled((ix + 14, G), (ix + 62, iy + 8), (ix + 112, G), (ix + 62, G), 34, P['ink'], 0.22, both=False),
                  ruled((ix + 62, iy + 8), (ix + 112, G), (ix + 168, iy + 22), (ix + 168, G), 28, P['ink'], 0.18, both=False),
                  ruled((ix + 116, G), (ix + 150, iy + 34), (ix + iw - 2, G), (ix + 150, G), 20, P['paper'], 0.24, both=False)], transform='translate(0.35 -0.25)'))
    o.append(g(art))
    o.append(text(x0 + w - 6, y0 + h - 1.6, 'Paraboloïdes  4/20', 2.0, '#8a8478', 'Jost', 400, 0.08, 'end'))
    for px_ in (x0 + 4, x0 + w - 4):
        o.append(circle(px_ + 0.4, y0 + 3.4, 1.4, '#000', opacity=0.3, filter=D.blur(0.4)))
        o.append(circle(px_, y0 + 3, 1.3, D.rad([(0, '#fff2c8'), (0.5, '#c9a14e'), (1, '#6e521e')], 0.35, 0.3, 0.8)))
    # ladders: steel wire, a lit edge on each upright and rung
    for x in (10, W - 19):
        for ux in (x, x + 8.25):
            o.append(rect(ux, Y(0), 0.8, BOT, D.lin([(0, '#6b6863'), (0.4, '#2a2927'), (1, '#121110')], 0, 0, 1, 0)))
        for k in range(0, BOT, 6):
            o.append(rect(x + 0.5, Y(k + 2.6), 8, 0.36, '#1d1c1a'))
            o.append(rect(x + 0.5, Y(k + 2.6), 8, 0.12, '#8a8782'))
    # the board: oak, its front edge lit, its shadow on the wall
    bx, by, bw, bh = 0, Y(PLANK), W, 6.2
    o.append(rect(4, by + 4, bw - 2, 9, '#000', opacity=0.25, filter=D.blur(2.2)))
    o.append(g([wood(D, bx, by, bw, bh, P['oak'], seed=31, lines=9, arches=3, contrast=1.1),
                rect(bx, by, bw, 1.3, D.lin([(0, '#f0dcbc'), (1, P['oak'])])),
                rect(bx, by, bw, bh, D.lin([(0, '#ffffff', 0), (0.6, '#000000', 0), (1, '#000000', 0.25)])),
                rect(0, by, 1.2, bh, P['oakd']), rect(bw - 1.2, by, 1.2, bh, P['oakd'])], clip_path=D.clip(rect(bx, by, bw, bh, '#000'))))
    # the bookend: folded steel, its edge lit
    x, b = 122, Y(PLANK)
    o.append(rect(x + 1.4, b - 39, 2.4, 39, '#000', opacity=0.25, filter=D.blur(0.8)))
    o.append(rect(x, b - 40, 2.4, 40, D.lin([(0, '#5a5853'), (0.35, '#262523'), (1, '#121110')], 0, 0, 1, 0)))
    o.append(rect(x - 18, b - 1.6, 20.4, 1.6, D.lin([(0, '#4a4844'), (1, '#121110')])))
    o.append(rect(x + 0.3, b - 39.6, 0.4, 38, '#ffffff', opacity=0.3))
    return fin('shelf', o, W, SH, D, 23)

if __name__ == '__main__':
    import sys
    which = sys.argv[1:] or ['vols', 'mag_ledge', 'file_box', 'shelf']
    for w in which:
        if w == 'vols':
            for v in VOLS: volume(v)
        else: globals()[w]()
