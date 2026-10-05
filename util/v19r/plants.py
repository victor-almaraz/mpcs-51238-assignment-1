# Two plants for the floor either side of v21's desk, and the wallpaper: a fiddle-leaf fig
# in a terracotta pot on a teak tripod stand, a monstera in a white pot on brass hairpin
# legs; a blue paper with a small half-drop motif of seed pods. Units are tenths of an em.
import math, random
from mcm import *
from render import render, REPO
OUT = REPO + '/v21/assets'
SCALE = 5
LEAF, LEAFD, LEAFL = '#5f7a4f', '#465d3b', '#86a06a'
TERRA = '#b86a45'

def common(seed):
    return print_filter('pr', 1.3, 0.22, seed) + grain_filter('gr', 1.1, 0.05, seed + 1)

def fiddle():
    W, H = 110, 210
    o = []
    rnd = random.Random(21)
    # the stand: a teak ring on three splayed legs
    for x0, x1 in ((42, 30), (55, 55), (68, 80)):
        o.append(poly([(x0 - 1.4, 168), (x0 + 1.4, 168), (x1 + 1.2, H), (x1 - 1.2, H)], P['teak'] if x0 != 55 else P['teakd']))
    o.append(rect(36, 166, 38, 3.2, P['teakl'])); o.append(rect(36, 168.6, 38, 0.8, P['teakd']))
    # the pot: terracotta, a rolled rim
    pot = 'M38,136 L72,136 L68,167 L42,167 Z'
    o.append(path(pot, TERRA)); o.append(rect(36, 132, 38, 6, light(TERRA, 0.12))); o.append(rect(36, 137.4, 38, 0.8, dark(TERRA, 0.2)))
    o.append(g(halftone(57, 136, 72, 167, lambda x, y: (x - 57) / 15 * 0.8, 1.0, dark(TERRA, 0.18)), clip_path='url(#fpot)'))
    # the trunk and its branches
    o.append(path('M55,134 C54,110 57,90 54,60 C53,45 56,30 55,18', 'none', stroke=P['walnut'], stroke_width=1.3))
    o.append(path('M54.6,88 C48,80 40,74 32,72', 'none', stroke=P['walnut'], stroke_width=0.8))
    o.append(path('M55.4,70 C62,62 70,58 78,56', 'none', stroke=P['walnut'], stroke_width=0.8))
    # the leaves: broad violins, each with its midrib, set along the stems
    def leaf(x, y, s, ang, c):
        d = 'M0,0 C%s,%s %s,%s %s,%s C%s,%s %s,%s 0,%s C%s,%s %s,%s %s,%s C%s,%s %s,%s 0,0 Z' % (
            f(s * 0.35), f(-s * 0.05), f(s * 0.5), f(s * 0.35), f(s * 0.36), f(s * 0.55), f(s * 0.62), f(s * 0.8), f(s * 0.3), f(s * 1.15), f(s * 1.2),
            f(-s * 0.3), f(s * 1.15), f(-s * 0.62), f(s * 0.8), f(-s * 0.36), f(s * 0.55), f(-s * 0.5), f(s * 0.35), f(-s * 0.35), f(-s * 0.05))
        return g([path(d, c), path('M0,%s L0,%s' % (f(s * 0.08), f(s * 1.1)), 'none', stroke=dark(c, 0.25), stroke_width=0.3),
                  path('M0,%s C%s,%s %s,%s %s,%s' % (f(s * 0.5), f(s * 0.1), f(s * 0.45), f(s * 0.22), f(s * 0.4), f(s * 0.32), f(s * 0.32)), 'none', stroke=dark(c, 0.2), stroke_width=0.2)],
                 transform='translate(%s %s) rotate(%s)' % (f(x), f(y), f(ang)))
    spots = [(55, 20, 13, 180), (50, 30, 14, 140), (61, 34, 14, 215), (47, 46, 15, 120), (63, 50, 15, 240), (52, 62, 15, 150), (60, 74, 14, 205),
             (33, 72, 14, 100), (40, 76, 13, 160), (78, 56, 14, 255), (71, 60, 13, 200), (49, 96, 14, 135), (61, 104, 13, 225), (53, 116, 12, 170)]
    for x, y, s, a in spots:
        o.append(leaf(x, y, s * 1.05, a + rnd.uniform(-10, 10), rnd.choice([LEAF, LEAFD, LEAFL, LEAF])))
    return render('plant-fig', g(g(o, filter='url(#gr)'), filter='url(#pr)'), W, H, SCALE, OUT,
                  defs=common(151) + clip('fpot', path(pot, '#000')))

def monstera():
    W, H = 140, 160
    cx = 70
    o = []
    masks = []
    rnd = random.Random(31)
    # the hairpin stand: two brass loops each side
    for x in (cx - 20, cx + 20):
        o.append(path('M%s,128 L%s,%s M%s,128 L%s,%s' % (f(x - 4), f(x - 7), f(H - 1), f(x + 4), f(x - 3), f(H - 1)), 'none', stroke=P['brass'], stroke_width=0.9))
        o.append(path('M%s,%s C%s,%s %s,%s %s,%s' % (f(x - 7), f(H - 1), f(x - 7), f(H + 0.6), f(x - 3), f(H + 0.6), f(x - 3), f(H - 1)), 'none', stroke=P['brass'], stroke_width=0.9))
    pot = 'M%s,104 L%s,104 L%s,126 C%s,129 %s,130 %s,130 L%s,130 C%s,130 %s,129 %s,126 Z' % (
        f(cx - 24), f(cx + 24), f(cx + 24), f(cx + 24), f(cx + 21), f(cx + 18), f(cx - 18), f(cx - 21), f(cx - 24), f(cx - 24))
    # stems, fanning up from the pot; a leaf on each, its sides cut into fingers by slits
    leaves = [(-52, 46, 24), (-26, 52, 28), (0, 50, 30), (24, 54, 28), (50, 44, 24), (-38, 30, 20), (36, 28, 20)]
    for n, (ang, length, size) in enumerate(leaves):
        a = math.radians(ang)
        tx, ty = cx + math.sin(a) * length * 0.9, 104 - math.cos(a) * length * 1.5
        o.append(path('M%s,104 Q%s,%s %s,%s' % (f(cx), f(cx + math.sin(a) * length * 0.25), f(104 - length * 0.8), f(tx), f(ty)), 'none', stroke=LEAFD, stroke_width=0.7))
        c = rnd.choice([LEAF, LEAFD, LEAF, LEAFL])
        R = size / 2
        shape = 'M0,0 C%s,%s %s,%s 0,%s C%s,%s %s,%s 0,0 Z' % (f(R * 1.3), f(-R * 0.5), f(R * 1.2), f(R * 1.6), f(R * 2.0), f(-R * 1.2), f(R * 1.6), f(-R * 1.3), f(-R * 0.5))
        slits = ' '.join('M%s,%s L%s,%s' % (f(sd * R * 1.5), f(R * (0.3 + k * 0.34)), f(sd * R * 0.24), f(R * (0.42 + k * 0.34))) for k in range(5) for sd in (-1, 1))
        mid = 'mk%d' % n
        masks.append('<mask id="%s" maskUnits="userSpaceOnUse" x="-50" y="-50" width="100" height="100"><path d="%s" fill="#fff"/><path d="%s" stroke="#000" stroke-width="%s" stroke-linecap="round"/></mask>' % (mid, shape, slits, f(R * 0.11)))
        rot = ang + 180 + rnd.uniform(-8, 8)
        o.append(g([path(shape, c, mask='url(#%s)' % mid), path('M0,%s L0,%s' % (f(R * 0.1), f(R * 1.9)), 'none', stroke=dark(c, 0.25), stroke_width=0.35)],
                   transform='translate(%s %s) rotate(%s)' % (f(tx), f(ty), f(rot))))
    o.append(path(pot, P['ivory']))
    o.append(g([halftone(cx + 6, 104, cx + 24, 130, lambda x, y: (x - cx - 6) / 18 * 0.8, 0.9, P['stone']), rect(cx - 24, 104, 48, 1.4, light(P['ivory'], 0.5))], clip_path='url(#mpot)'))
    o.append(path(pot, 'none', stroke=P['soft'], stroke_width=0.35, transform='translate(-0.4 0.3)'))
    return render('plant-monstera', g(g(o, filter='url(#gr)'), filter='url(#pr)'), W, H, SCALE, OUT,
                  defs=common(161) + clip('mpot', path(pot, '#000')) + ''.join(masks))

def wallpaper():
    # a 40 × 60 tile, half-drop: seed pods in a cream hairline, a pale dot above and below
    # each, and a small cluster of four dots between them, on a soft blue
    W, H = 40, 60
    ground, pale, cream = '#56768f', '#6f8ea6', '#e9dfca'
    def pod(x, y):
        return ('<path d="M%s,%s Q%s,%s %s,%s Q%s,%s %s,%s Z" fill="none" stroke="%s" stroke-width="0.7" opacity="0.75"/>'
                '<path d="M%s,%s L%s,%s" stroke="%s" stroke-width="0.45" opacity="0.6"/>'
                '<circle cx="%s" cy="%s" r="0.9" fill="%s" opacity="0.7"/><circle cx="%s" cy="%s" r="0.9" fill="%s" opacity="0.7"/>') % (
            f(x), f(y - 8), f(x + 5.5), f(y), f(x), f(y + 8), f(x - 5.5), f(y), f(x), f(y - 8), cream,
            f(x), f(y - 5.5), f(x), f(y + 5.5), cream, f(x), f(y - 11.5), pale, f(x), f(y + 11.5), pale)
    def four(x, y):
        return ''.join('<circle cx="%s" cy="%s" r="0.75" fill="%s"/>' % (f(x + dx), f(y + dy), pale) for dx, dy in ((0, -2), (2, 0), (0, 2), (-2, 0)))
    body = ('<rect width="%d" height="%d" fill="%s"/>' % (W, H, ground) + pod(20, 15) + pod(0, 45) + pod(40, 45) +
            four(0, 15) + four(40, 15) + four(20, 45) + four(0, -15) + four(40, -15) + four(20, 75) + pod(20, -45) + pod(20, 75))
    s = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">%s</svg>' % (W, H, W * 4, H * 4, body)
    open(OUT + '/wallpaper.svg', 'w').write(s)
    print('wallpaper', len(s), 'B')

if __name__ == '__main__':
    import sys
    for w in (sys.argv[1:] or ['fiddle', 'monstera', 'wallpaper']): globals()[w]()
