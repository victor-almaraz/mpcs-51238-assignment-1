# The reference manual's three cloth volumes, drawn spine on. Units are tenths of an em of
# the room drawing; rendered at SCALE px a unit.
import sys, math
from mcm import *
from render import render, REPO
OUT = REPO + '/v19/assets'
SCALE = 5

VOLS = [
    dict(n='1', title='FORTRAN', sub='The language', w=32, h=98, cloth=P['linen'], ink=P['ink'], foil=P['ink'], label=P['paper'], emblem='card'),
    dict(n='2', title='SIEVES', sub='After Xenakis', w=29, h=91, cloth=P['slate'], ink=P['paper'], foil=P['ochre'], label=P['paper'], emblem='sieve'),
    dict(n='3', title='MUSIC', sub='And tape', w=30.5, h=95, cloth=P['accent'], ink=P['paper'], foil=P['paper'], label=P['paper'], emblem='reel'),
]

def emblem(kind, cx, y, ink, foil, cloth):
    out = []
    if kind == 'card':
        # a column of a punched card: twelve rows, two columns, the punches cut through
        rows, rh = 12, 1.45
        for r in range(rows):
            for c in range(3):
                x = cx - 4.6 + c * 3.6; yy = y + r * rh
                punched = (r * 7 + c * 5) % 4 == 0 or (r == 0 and c == 1) or (r == 11 and c == 0)
                out.append(rect(x, yy, 2.0, 1.1, ink if punched else 'none', stroke=None if punched else ink, stroke_width=0.22 if not punched else None, opacity=1 if punched else 0.55))
        return ''.join(out), rows * rh
    if kind == 'sieve':
        # the sieve 3@0 | 5@2 on the integers 0..14: the residues of 3 as dots, of 5 as rings,
        # the union marked on the rule between them
        out.append(line(cx, y - 0.6, cx, y + 14 * 1.25 + 0.6, ink, 0.18, opacity=0.6))
        for k in range(15):
            yy = y + k * 1.25
            if k % 3 == 0: out.append(circle(cx - 3.2, yy, 0.62, foil))
            else: out.append(circle(cx - 3.2, yy, 0.2, foil, opacity=0.6))
            if k % 5 == 2: out.append(circle(cx + 3.2, yy, 0.55, 'none', stroke=foil, stroke_width=0.28))
            else: out.append(circle(cx + 3.2, yy, 0.2, foil, opacity=0.6))
            if k % 3 == 0 or k % 5 == 2: out.append(rect(cx - 1.3, yy - 0.2, 2.6, 0.4, ink))
        return ''.join(out), 14 * 1.25
    if kind == 'reel':
        # two reels, one over the other, and the tape running between them on a tangent
        R1, R2 = 4.4, 3.0
        c1, c2 = y + R1, y + 2 * R1 + 1.6 + R2
        out.append(line(cx + R1 - 0.1, c1, cx + R2 - 0.1, c2, ink, 0.32))
        for cyy, R, pack in ((c1, R1, 0.72), (c2, R2, 0.42)):
            out.append(circle(cx, cyy, R, 'none', stroke=ink, stroke_width=0.32))
            out.append(circle(cx, cyy, R * pack, ink))
            for k in range(3):
                a = math.radians(-90 + k * 120)
                out.append(circle(cx + R * 0.36 * math.cos(a), cyy + R * 0.36 * math.sin(a), R * 0.13, cloth))
            out.append(circle(cx, cyy, R * 0.09, cloth))
        return ''.join(out), c2 + R2 - y
    return '', 0

def volume(v, i):
    w, h, cloth = v['w'], v['h'], v['cloth']
    lit, shade = light(cloth, 0.16), dark(cloth, 0.24)
    cid = 'sp%d' % i
    shape = rrect(0, 0, w, h, (2.2, 2.2, 0.6, 0.6))
    defs = clip(cid, path(shape, '#000')) + print_filter('pr%d' % i, 1.5, 0.3, 11 + i) + grain_filter('gr%d' % i, 1.1, 0.055, 5 + i)
    body = []
    # the cloth: flat, then the round of the spine as two flat bands (lit left, shade right)
    # joined by halftone, not by a gradient
    body.append(rect(0, 0, w, h, cloth))
    body.append(rect(0, 0, w * 0.06, h, shade))
    body.append(rect(w * 0.06, 0, w * 0.2, h, lit))
    body.append(halftone(w * 0.26, 0, w * 0.42, h, lambda x, y: 1 - (x - w * 0.26) / (w * 0.16), 0.9, lit, angle=45))
    body.append(rect(w * 0.82, 0, w * 0.18, h, shade))
    body.append(halftone(w * 0.62, 0, w * 0.82, h, lambda x, y: (x - w * 0.62) / (w * 0.2), 0.9, shade, angle=45))
    # the weave
    body.append(hatch(0, 0, w, h, 0.55, dark(cloth, 0.3), 0.1, angle=0, opacity=0.18))
    body.append(hatch(0, 0, w, h, 0.55, light(cloth, 0.4), 0.1, angle=90, opacity=0.12))
    # the headcap, pressed darker
    body.append(rect(0, 0, w, 2.4, dark(cloth, 0.2), opacity=0.7))
    body.append(rect(0, h - 1.2, w, 1.2, dark(cloth, 0.2), opacity=0.6))
    # stamped work, in foil or ink, out of register a hair from the cloth
    stamp = []
    for yy in (5.2, 6.4):
        stamp.append(rect(2.2, yy, w - 4.4, 0.32, v['foil']))
    em, eh = emblem(v['emblem'], w / 2, 10.5, v['ink'], v['foil'], cloth)
    stamp.append(em)
    ty = 10.5 + eh + 3.6
    # the title down the spine, and the subtitle in light capitals beside it
    stamp.append(text(0, 0, v['title'], 5.9, v['ink'], 'Work Sans', 600, 0.14,
                      transform='translate(%s %s) rotate(90)' % (f(w / 2 + 0.2), f(ty))))
    stamp.append(text(0, 0, v['sub'].upper(), 2.7, v['foil'], 'Jost', 400, 0.22,
                      transform='translate(%s %s) rotate(90)' % (f(w / 2 - 5.4), f(ty + 0.4)), opacity=0.9))
    for yy in (h - 6.6, h - 5.4):
        stamp.append(rect(2.2, yy, w - 4.4, 0.32, v['foil']))
    body.append(g(stamp, transform='translate(0.18 -0.14)', filter='url(#pr%d)' % i))
    # the volume's number on a pasted paper label at the foot
    lx, ly, lw, lh = w / 2 - 6.5, h - 20, 13, 11.5
    lab = [rect(lx, ly, lw, lh, v['label']),
           rect(lx + 0.9, ly + 0.9, lw - 1.8, lh - 1.8, 'none', stroke=P['ink'], stroke_width=0.18),
           text(w / 2, ly + lh - 3.0, v['n'], 7.2, P['ink'], 'Arvo', 700, 0, 'middle'),
           rect(lx, ly, 1.4, lh, P['ink'], opacity=0.06)]
    body.append(g(lab))
    body = g(g(body, filter='url(#gr%d)' % i), clip_path='url(#%s)' % cid)
    return render('vol-%s' % v['n'], body, w, h, SCALE, OUT, defs=defs)

if __name__ == '__main__':
    for i, v in enumerate(VOLS): volume(v, i)
