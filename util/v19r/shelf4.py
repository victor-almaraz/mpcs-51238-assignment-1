# v22's shelf: v21's oak board on wire ladders without the screen print pinned above it, which
# is drawn apart so it can be swapped (decor.js): v21's ochre print of ruled surfaces, a
# print of Metastaseis's glissandi, and a print of the Psappha rhythm. Each print is drawn in
# the same box (204 x 108 units of the shelf's 400 x 152, from 164, 6), with its pins and its
# shadow on the wall.
import math, random, sys
from mcm import *
from mcm2 import *
from render import render, REPO
import shelf3
OUT = REPO + '/v22/assets'
S = 6
BX, BY, BW, BH = 164, 6, 204, 108

def shelf_bare():
    # shelf3.shelf with the print's part left out: drawn by running it and dropping the print
    src = open(shelf3.__file__).read()
    a = src.index('    # the print: ochre'); b = src.index('    # ladders: steel wire')
    ns = dict(shelf3.__dict__)
    code = src[src.index('def shelf():'):src.index('\nif __name__')]
    code = code.replace(src[a:b], '').replace("return fin('shelf'", "return fin_v22('shelf'")
    ns['fin_v22'] = lambda name, o, W, H, D, seed, extra='': render(name, g(g(o, filter='url(#gr)'), filter='url(#pr)'), W, H, S, OUT,
        defs=D.out() + extra + print_filter('pr', 1.4, 0.1, seed) + grain_filter('gr', 1.1, 0.02, seed + 1))
    exec(code, ns)
    return ns['shelf']()

def pinned(name, art_fn, caption, seed, ground=('#fbf8ef', '#efe9da')):
    D = Defs(); o = []
    x0, y0, w, h = 168, 10, 196, 100
    o.append(rect(x0 + 1.2, y0 + 1.8, w, h, '#000', opacity=0.22, filter=D.blur(1.2)))
    o.append(rect(x0, y0, w, h, D.lin([(0, ground[0]), (1, ground[1])])))
    ix, iy, iw, ih = x0 + 5, y0 + 5, w - 10, h - 10
    o.append(g(art_fn(D, ix, iy, iw, ih), clip_path=D.clip(rect(ix, iy, iw, ih, '#000'))))
    o.append(text(x0 + w - 6, y0 + h - 1.6, caption, 2.0, '#8a8478', 'Jost', 400, 0.08, 'end'))
    for px_ in (x0 + 4, x0 + w - 4):
        o.append(circle(px_ + 0.4, y0 + 3.4, 1.4, '#000', opacity=0.3, filter=D.blur(0.4)))
        o.append(circle(px_, y0 + 3, 1.3, D.rad([(0, '#fff2c8'), (0.5, '#c9a14e'), (1, '#6e521e')], 0.35, 0.3, 0.8)))
    body = '<g transform="translate(%d %d)">%s</g>' % (-BX, -BY, g(g(o, filter='url(#gr)'), filter='url(#pr)'))
    return render(name, body, BW, BH, S, OUT, defs=D.out() + print_filter('pr', 1.4, 0.1, seed) + grain_filter('gr', 1.1, 0.02, seed + 1))

def paraboloids():
    # v21's print: ochre, a terracotta disc, string-art saddles
    def art(D, ix, iy, iw, ih):
        G = iy + ih * 0.72
        a = [rect(ix, iy, iw, ih, P['ochre']), rect(ix, G, iw, ih - (G - iy), light(P['ochre'], 0.2)), circle(ix + 46, iy + 24, 13, P['accent']),
             halftone(ix, iy, ix + iw, G, lambda X, Y_: 0.18 * (1 - (Y_ - iy) / (G - iy)), 1.6, dark(P['ochre'], 0.25), angle=45)]
        a.append(g([ruled((ix + 14, G), (ix + 62, iy + 8), (ix + 112, G), (ix + 62, G), 34, P['ink'], 0.22, both=False),
                    ruled((ix + 62, iy + 8), (ix + 112, G), (ix + 168, iy + 22), (ix + 168, G), 28, P['ink'], 0.18, both=False),
                    ruled((ix + 116, G), (ix + 150, iy + 34), (ix + iw - 2, G), (ix + 150, G), 20, P['paper'], 0.24, both=False)], transform='translate(0.35 -0.25)'))
        return a
    return pinned('shelf-print-paraboloids', art, 'Paraboloïdes  4/20', 401)

def glissandi():
    # Metastaseis: the strings' glissandi as straight lines between two chords, slate on a
    # pale blue, the bundle crossing in terracotta, its envelope curving though every line is straight
    def art(D, ix, iy, iw, ih):
        a = [rect(ix, iy, iw, ih, '#cfdbe0')]
        for k in range(34):
            t = k / 33
            a.append(line(ix + 6, iy + ih * (0.08 + 0.84 * t), ix + iw - 6, iy + ih * (0.5 + 0.06 * (t - 0.5)), P['slate'], 0.28))
        for k in range(26):
            t = k / 25
            a.append(line(ix + 6, iy + ih * (0.46 + 0.08 * (t - 0.5)), ix + iw - 6, iy + ih * (0.1 + 0.8 * t), P['accent'], 0.26, opacity=0.9))
        a.append(rect(ix, iy + ih - 9, iw, 9, P['slate']))
        a.append(text(ix + 4, iy + ih - 3, 'METASTASEIS', 3.4, '#cfdbe0', 'Work Sans', 600, 0.5))
        return a
    return pinned('shelf-print-glissandi', art, 'Glissandi  2/15', 411)

def psappha():
    # the sieve of Psappha's first 40 pulses (27 struck, after Ellen Flint's reconstruction),
    # set in five rows of eight, as its modulus 8 lays them out: a struck pulse a black disc,
    # the first of each row in red, a rest a point; on a cream newsprint
    RM = {0, 1, 3, 4, 6, 8, 10, 11, 12, 13, 14, 16, 17, 19, 20, 22, 23, 25, 27, 28, 29, 31, 33, 35, 36, 37, 38}
    def art(D, ix, iy, iw, ih):
        a = [rect(ix, iy, iw, ih, '#efe7d4')]
        gx, gy, cw, rh = ix + 92, iy + 10, 11.2, 14
        for n in range(40):
            r, c = divmod(n, 8)
            x, y = gx + (c + 0.5) * cw, gy + (r + 0.5) * rh
            if n in RM: a.append(circle(x, y, 4.2, P['accent'] if c == 0 else P['ink']))
            else: a.append(circle(x, y, 0.7, P['ink'], opacity=0.6))
        a.append(text(ix + 8, iy + 30, 'PSAPPHA', 12, P['ink'], 'Archivo Black', 400, 0.02))
        a.append(text(ix + 8, iy + 40, '27 of 40 pulses', 4.2, P['ink'], 'Work Sans', 400, 0.06))
        a.append(text(ix + 8, iy + 46, 'percussion solo, 1975', 4.2, P['ink'], 'Work Sans', 400, 0.06))
        a.append(rect(ix + 8, iy + 52, 60, 1.6, P['accent']))
        return a
    return pinned('shelf-print-psappha', art, 'Psappha  9/30', 421)

if __name__ == '__main__':
    for w in (sys.argv[1:] or ['shelf_bare', 'paraboloids', 'glissandi', 'psappha']): globals()[w]()
