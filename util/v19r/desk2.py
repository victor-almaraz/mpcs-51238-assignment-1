# v21's desk things drawn again in more detail: the lamp, the chair, the mug, the coding
# form on its clipboard, the out tray and the deck box. One light, from the upper left.
import math, random
from mcm import *
from mcm2 import *
from render import render, REPO
OUT = REPO + '/v21/assets'
S = 6
GREEN = '#3b6a55'
PENCIL = '#5b5853'

def fin(name, o, W, H, D, seed, grain=0.02, thr=0.1):
    defs = D.out() + print_filter('pr', 1.4, thr, seed) + grain_filter('gr', 1.1, grain, seed + 1)
    return render(name, g(g(o, filter='url(#gr)'), filter='url(#pr)'), W, H, S, OUT, defs=defs)

def brass(D): return D.lin([(0, '#f3dfa0'), (0.35, '#c9a14e'), (0.6, '#8d6a2a'), (1, '#d8b867')], 0, 0, 1, 1)
def lacquer(D, c='#1e1d1b'): return D.lin([(0, light(c, 0.35)), (0.35, c), (1, dark(c, 0.5))], 0, 0, 1, 0)

# ---- the lamp: a cast-iron foot, a black stem and arm, brass knuckles, a slant-cut shade
# whose white throat glows round the bulb
def lamp():
    W, H = 70, 106
    D = Defs(); o = []
    o.append(ellipse(16, 105.4, 13, 1.2, '#000', opacity=0.35, filter=D.blur(0.7)))
    # the cord, out of the foot and away behind the desk
    o.append(path('M22,104.4 C30,104.6 34,103 40,104.8', 'none', stroke='#151413', stroke_width=0.5))
    foot = 'M4,106 C4.6,101.6 9,100 16,100 C23,100 27.4,101.6 28,106 Z'
    o.append(path(foot, D.rad([(0, '#5a5752'), (0.5, '#262523'), (1, '#0d0c0b')], 0.35, 0.2, 0.9)))
    o.append(path('M7,103.6 C8.4,101.6 11.6,100.8 16,100.8', 'none', stroke='#ffffff', stroke_width=0.35, opacity=0.35))
    o.append(path(rrect(13.6, 98, 4.8, 2.4, 0.6), brass(D)))
    # the stem, lacquered, its light down the left
    o.append(path('M15,99 C15.5,80 17,52 19.5,30', 'none', stroke='#1b1a18', stroke_width=1.2, stroke_linecap='round'))
    o.append(path('M14.65,98 C15.15,80 16.65,52 19.15,31', 'none', stroke='#ffffff', stroke_width=0.25, opacity=0.35))
    # the arm, curving out over the desk
    o.append(path('M19.5,30 C27,22 38,19.5 48.5,21', 'none', stroke='#1b1a18', stroke_width=0.9, stroke_linecap='round'))
    o.append(path('M19.8,29.4 C27,21.6 38,19.1 48.4,20.5', 'none', stroke='#ffffff', stroke_width=0.2, opacity=0.4))
    for kx, ky in ((19.5, 30), (49, 21.2)):
        o.append(circle(kx, ky, 1.7, D.rad([(0, '#fff1c4'), (0.4, '#c9a14e'), (1, '#6e521e')], 0.35, 0.3, 0.8)))
        o.append(circle(kx, ky, 0.5, '#5a4318'))
    # the shade, turned toward the desk: its lacquered outside, its open throat
    cx, cy, ang = 53, 25, 38
    out_d = 'M-4,-5.5 C-1,-8 5,-7.5 10,-4 L17,4 C13,9 4,10.5 -2,7 C-5.5,4 -6.5,-2 -4,-5.5 Z'
    throat = 'M17,4 C13,9 4,10.5 -2,7 C3,6.8 11,4.6 17,4 Z'
    sh = [path(out_d, D.lin([(0, '#55524d'), (0.3, '#232220'), (1, '#0b0b0a')], 0, 0, 0.6, 1)),
          path('M-3.4,-4.6 C-0.6,-6.8 4.5,-6.6 8.8,-3.6', 'none', stroke='#ffffff', stroke_width=0.55, opacity=0.4, stroke_linecap='round'),
          path(throat, D.lin([(0, '#fff6dc'), (1, '#f0d9a0')], 0, 0, 1, 1)),
          ellipse(7.5, 6.6, 3.2, 1.3, D.rad([(0, '#ffffff'), (0.5, '#fff1c8'), (1, '#fff1c8', 0)])),
          path('M17,4 C14.2,5.6 9,6.6 4,6.9', 'none', stroke='#c99a2e', stroke_width=0.3, opacity=0.6),
          circle(-4.4, -1.2, 1.4, D.rad([(0, '#fff1c4'), (0.4, '#c9a14e'), (1, '#6e521e')], 0.35, 0.3, 0.8))]
    o.append(g(sh, transform='translate(%s %s) rotate(%s)' % (f(cx), f(cy), f(ang))))
    return fin('lamp', o, W, H, D, 51)

# ---- a molded-plywood side chair: shells of seven plies, their edges striped; the back on
# rubber mounts; splayed legs on glides
def chair():
    W, H = 96, 144
    D = Defs(); o = []
    ply, plyd, plyl = '#c49a6c', '#8f6a45', '#e2c49c'
    o.append(ellipse(48, 143.2, 40, 1.6, '#000', opacity=0.3, filter=D.blur(0.9)))
    def leg(x0, x1, top, back=False):
        c = dark(ply, 0.2) if back else ply
        d = 'M%s,%s L%s,%s L%s,%s L%s,%s Z' % (f(x0 - 2.2), f(top), f(x1 - 2.0), f(H - 1.2), f(x1 + 2.0), f(H - 1.2), f(x0 + 2.2), f(top))
        out = [path(d, D.lin([(0, light(c, 0.2)), (0.4, c), (1, dark(c, 0.3))], 0, 0, 1, 0))]
        for k in range(1, 4):
            t = k / 4
            out.append(line(x0 - 2.2 + 4.4 * t, top, x1 - 2.0 + 4.0 * t, H - 1.2, plyd, 0.12, opacity=0.5))
        out.append(path(rrect(x1 - 2.4, H - 1.6, 4.8, 1.6, 0.6), '#1b1a18'))
        return out
    o += leg(26, 18, 82, True) + leg(70, 78, 82, True)
    # the spine that carries the back, and its rubber mounts
    o.append(path('M45,40 L51,40 L52,82 L44,82 Z', D.lin([(0, '#d6b386'), (0.5, '#a57d52'), (1, '#7d5c38')], 0, 0, 1, 0)))
    for my in (24, 30):
        o.append(ellipse(48, my, 3.2, 1.6, D.rad([(0, '#3e3c39'), (1, '#0d0c0b')])))
    # the back: a wide shell, its face turning away at the ends, its top edge showing the plies
    back = 'M9,12 C9,6 15,4 48,4 C81,4 87,6 87,12 L87,30 C87,36 81,38 48,38 C15,38 9,36 9,30 Z'
    o.append(soft_shadow(D, back, 0.8, 1.4, 1.0, 0.3))
    o.append(path(back, D.lin([(0, dark(ply, 0.12)), (0.12, ply), (0.45, light(ply, 0.12)), (0.88, ply), (1, dark(ply, 0.25))], 0, 0, 1, 0)))
    o.append(path(back, D.lin([(0, '#ffffff', 0.25), (0.25, '#ffffff', 0), (0.85, '#000000', 0), (1, '#000000', 0.2)])))
    for k in range(5):
        y = 4.6 + k * 0.5
        o.append(path('M14,%s C24,%s 72,%s 82,%s' % (f(y + 1.4), f(y), f(y), f(y + 1.4)), 'none', stroke=plyl if k % 2 else plyd, stroke_width=0.22, opacity=0.8))
    o.append(path('M12,33 C20,37 76,37 84,33', 'none', stroke=plyd, stroke_width=0.4, opacity=0.6))
    # the seat, at its front edge: a shallow dish, the plies along its lip
    seat = 'M3,76 C3,72 12,70 48,70 C84,70 93,72 93,76 L93,80 C93,84 84,85 48,85 C12,85 3,84 3,80 Z'
    o.append(soft_shadow(D, seat, 0.6, 1.6, 1.0, 0.3))
    o.append(path(seat, D.lin([(0, light(ply, 0.22)), (0.35, ply), (1, dark(ply, 0.22))])))
    for k in range(7):
        y = 78.4 + k * 0.85
        o.append(path('M5,%s C16,%s 80,%s 91,%s' % (f(y), f(y + 3.6), f(y + 3.6), f(y)), 'none', stroke=plyl if k % 2 else plyd, stroke_width=0.24, opacity=0.75))
    o += leg(30, 15, 84) + leg(66, 81, 84)
    o.append(path('M20,118 L76,118 L76,120 L20,120 Z', D.lin([(0, '#d6b386'), (1, '#8f6a45')])))
    return fin('chair', o, W, H, D, 111)

# ---- the mug: cream stoneware dipped in a terracotta glaze that runs at its edge
def mug():
    W, H = 32, 30
    D = Defs(); o = []
    o.append(ellipse(14, 29.6, 10, 0.8, '#000', opacity=0.3, filter=D.blur(0.5)))
    body = 'M4,4 L22,4 L21.4,28 C21.4,29 20,30 18,30 L8,30 C6,30 4.6,29 4.6,28 Z'
    handle = 'M21.6,9 C29.5,8 29.5,22.5 21.2,21.4 L21.3,18.6 C26.4,19.2 26.4,11 21.6,11.8 Z'
    cream = D.lin([(0, '#f9f4e8'), (0.5, '#ece4d2'), (1, '#c9bfa9')], 0, 0, 1, 0)
    o.append(path(handle, cream)); o.append(path(handle, 'none', stroke='#a59b87', stroke_width=0.25))
    o.append(path(body, cream))
    glaze = 'M4.3,17 C6,17.6 7,19.6 8.2,17.8 C9.6,16 11,16.4 12.4,17.2 C13.8,18.6 15,16.2 16.6,16.4 C18,16.6 19,18.2 21.7,15.6 L21.4,28 C21.4,29 20,30 18,30 L8,30 C6,30 4.6,29 4.6,28 Z'
    o.append(path(glaze, D.lin([(0, '#d0603f'), (0.45, '#b5462b'), (1, '#7a2b17')], 0, 0, 1, 0)))
    o.append(path('M6.4,19 C6.6,23 7,26 7.6,28', 'none', stroke='#ffffff', stroke_width=0.6, opacity=0.35, stroke_linecap='round'))
    o.append(ellipse(13, 4.1, 9, 0.9, '#3a2416'))
    o.append(ellipse(13, 4.1, 9, 0.9, 'none', stroke='#ffffff', stroke_width=0.35, opacity=0.8))
    o.append(path(body, 'none', stroke='#8f8673', stroke_width=0.22, opacity=0.8))
    return fin('mug', o, W, H, D, 141)

# ---- the coding form on a hardboard clipboard: a FORTRAN coding sheet, its header boxes and
# fields, the program pencilled in; a yellow pencil under a chromed clip
def coding_form():
    W, H = 70, 94
    D = Defs(); o = []
    bx, by, bw, bh = 2, 3, 66, 90
    board = rrect(bx, by, bw, bh, 3)
    o.append(soft_shadow(D, board, 0.8, 1.2, 1.0, 0.35))
    o.append(path(board, D.lin([(0, '#a3876a'), (0.5, '#8c7258'), (1, '#6f5944')], 0, 0, 1, 1)))
    o.append(path(board, 'none', stroke='#ffffff', stroke_width=0.4, opacity=0.25))
    sx, sy, sw, sh = bx + 4, by + 8, bw - 8, bh - 12
    o.append(rect(sx + 0.6, sy + 0.9, sw, sh, '#000', opacity=0.3, filter=D.blur(0.6)))
    o.append(rect(sx, sy, sw, sh, D.lin([(0, '#fbf9f2'), (1, '#efeadc')])))
    sheet = []
    sheet.append(text(sx + 2.5, sy + 4.2, 'FORTRAN CODING FORM', 1.7, GREEN, 'Work Sans', 600, 0.2))
    for k, (lab, w) in enumerate((('PROGRAM', 22), ('PROGRAMMER', 16), ('PAGE', 9))):
        x = sx + 2.5 + sum((22, 16, 9)[:k]) + k * 0.8
        sheet.append(rect(x, sy + 5.4, w, 4.6, 'none', stroke=GREEN, stroke_width=0.15))
        sheet.append(text(x + 0.6, sy + 6.7, lab, 0.8, GREEN, 'Work Sans', 600, 0.15))
    sheet.append(text(sx + 3.4, sy + 9.2, 'SIEVE', 1.9, PENCIL, 'Courier Prime', 700, 0.04))
    sheet.append(text(sx + 39.4, sy + 9.2, '1 / 2', 1.9, PENCIL, 'Courier Prime', 700, 0.04))
    gx0, gx1, gy0 = sx + 2.5, sx + sw - 2.5, sy + 12.6
    rows, rh = 19, 3.25
    sheet.append(rect(gx0, gy0 - 2, gx1 - gx0, 2, light(GREEN, 0.82)))
    for lab, x in (('STMT', gx0 + 0.3), ('C', gx0 + 5.0), ('FORTRAN STATEMENT', gx0 + 12)):
        sheet.append(text(x, gy0 - 0.6, lab, 0.8, GREEN, 'Work Sans', 600, 0.12))
    for r in range(rows + 1):
        sheet.append(line(gx0, gy0 + r * rh, gx1, gy0 + r * rh, GREEN, 0.12, opacity=0.75))
    for x in (gx0, gx0 + 4.4, gx0 + 5.5, gx1):
        sheet.append(line(x, gy0 - 2, x, gy0 + rows * rh, GREEN, 0.18, opacity=0.9))
    for c in range(1, 44):
        sheet.append(line(gx0 + 5.5 + c * 0.88, gy0, gx0 + 5.5 + c * 0.88, gy0 + rows * rh, GREEN, 0.05, opacity=0.35))
    prog = [('C', 'SIEVE OF RESIDUES'), ('', 'READ (5,10) N, M'), ('10', 'FORMAT (2I5)'), ('', 'DO 30 I = 1, N'), ('', 'K = MOD(I, M)'),
            ('', 'IF (K) 30, 20, 30'), ('20', 'WRITE (6,40) I'), ('30', 'CONTINUE'), ('40', 'FORMAT (1X, I5)'), ('', 'STOP'), ('', 'END')]
    rnd = random.Random(5)
    for r, (lab, st) in enumerate(prog):
        yy = gy0 + r * rh + rh * 0.78
        jit = 'rotate(%s %s %s)' % (f(rnd.uniform(-0.6, 0.6)), f(gx0), f(yy))
        if lab == 'C': sheet.append(text(gx0 + 4.9, yy, 'C', 2.0, PENCIL, 'Courier Prime', 700, 0, transform=jit))
        elif lab: sheet.append(text(gx0 + 0.6, yy, lab, 2.0, PENCIL, 'Courier Prime', 700, 0, transform=jit))
        sheet.append(text(gx0 + 6.4 + rnd.uniform(-0.2, 0.2), yy, st, 2.0, PENCIL, 'Courier Prime', 700, -0.02, transform=jit, opacity=0.92))
    o.append(g(sheet))
    # the pencil: hexagonal, three faces in three tones, a ribbed ferrule, a pink eraser
    pen = [rect(-1.3, -22, 2.6, 40, D.lin([(0, '#f2cd5a'), (0.33, '#f2cd5a'), (0.34, '#d9a92f'), (0.66, '#d9a92f'), (0.67, '#b08223'), (1, '#b08223')], 0, 0, 1, 0)),
           rect(-1.3, 18, 2.6, 3.4, D.lin([(0, '#e8e6e0'), (0.4, '#ffffff'), (1, '#8d8a83')], 0, 0, 1, 0)),
           g([line(-1.3, 18.6 + k * 0.7, 1.3, 18.6 + k * 0.7, '#77736b', 0.15) for k in range(4)]),
           path(rrect(-1.3, 21.4, 2.6, 3.2, (0, 0, 0.8, 0.8)), D.lin([(0, '#e8a49a'), (1, '#b86f66')], 0, 0, 1, 0)),
           poly([(-1.3, -22), (1.3, -22), (0, -27.4)], D.lin([(0, '#f3d9b1'), (1, '#c79c68')], 0, 0, 1, 0)),
           poly([(-0.45, -25.6), (0.45, -25.6), (0, -27.4)], '#2c2b29'),
           text(0.3, 6, 'HB', 1.2, '#2c2b29', 'Work Sans', 600, 0.1, 'middle', transform='rotate(90 0.3 6)')]
    o.append(g([g(pen, transform='translate(0.6 0.8)', opacity=0.0)] + [rect(-1.3, -22, 2.6, 46, '#000', opacity=0.25, filter=D.blur(0.5), transform='translate(1.0 1.0)')] + pen,
               transform='translate(%s %s) rotate(-12)' % (f(bx + bw - 13), f(by + 36))))
    # the clip: a chromed jaw, rivets, and its wire lever
    cx = bx + bw / 2
    jaw = rrect(cx - 13, by - 1, 26, 10, (2, 2, 4, 4))
    o.append(soft_shadow(D, jaw, 0.4, 0.9, 0.6, 0.4))
    o.append(path(jaw, D.lin([(0, '#ffffff'), (0.3, '#cfcdc8'), (0.55, '#8e8b85'), (0.75, '#e4e2dd'), (1, '#9c9993')])))
    o.append(path('M%s,%s C%s,%s %s,%s %s,%s' % (f(cx - 8), f(by + 0.6), f(cx - 4), f(by - 4.2), f(cx + 4), f(by - 4.2), f(cx + 8), f(by + 0.6)), 'none', stroke='#7f7c76', stroke_width=1.3, stroke_linecap='round'))
    o.append(path('M%s,%s C%s,%s %s,%s %s,%s' % (f(cx - 7.6), f(by + 0.2), f(cx - 4), f(by - 3.8), f(cx + 4), f(by - 3.8), f(cx + 7.6), f(by + 0.2)), 'none', stroke='#ffffff', stroke_width=0.35, opacity=0.7))
    for rx in (cx - 9, cx + 9): o.append(screw(D, rx, by + 4, 0.9, False, 0))
    o.append(path(jaw, 'none', stroke='#5f5c56', stroke_width=0.25))
    return fin('coding-form', o, W, H, D, 71)

# ---- a punched card, its corner cut, printed digits in rows and the holes punched through
def card(D, x, y, w, h, punches, fill='#efe2c2', edge='#a98b68', rows=12, digits=True):
    out = []
    shape = 'M%s,%s L%s,%s L%s,%s L%s,%s L%s,%s Z' % (f(x + 2.2), f(y), f(x + w), f(y), f(x + w), f(y + h), f(x), f(y + h), f(x), f(y + 2.2))
    out.append(path(shape, fill)); out.append(path(shape, 'none', stroke=edge, stroke_width=0.18))
    cols = int((w - 3) / 1.1)
    rh = (h - 2.6) / rows
    for row in range(rows):
        for c in range(cols):
            cx = x + 1.8 + c * 1.1; cy = y + 2.2 + row * rh + rh / 2
            if (c, row) in punches: out.append(rect(cx - 0.28, cy - rh * 0.36, 0.56, rh * 0.72, '#1d1712'))
            elif digits and row >= 2: out.append(rect(cx - 0.16, cy - rh * 0.2, 0.32, rh * 0.4, '#c98a7a', opacity=0.6))
    return out

# ---- the out tray: graphite steel with a rolled lip and a card holder; a fold of printout
# in it, the green bars and sprocket holes, its pages' edges down the front; cards on top
def out_tray():
    W, H = 104, 44
    D = Defs(); o = []
    o.append(ellipse(52, 43.6, 50, 1.0, '#000', opacity=0.35, filter=D.blur(0.7)))
    # the printout: the top page, then the folded pages' edges in front of it
    px, py, pw = 5, 6, 92
    o.append(rect(px, py, pw, 26, D.lin([(0, '#fbfaf3'), (1, '#efece2')])))
    for b in range(0, 26, 4):
        o.append(rect(px + 4, py + b + 0.6, pw - 8, 2, '#dce8d8'))
    rnd = random.Random(2)
    for b in range(1, 25, 2):
        x = px + 6
        while x < px + pw - 8:
            wd = rnd.uniform(2, 9)
            o.append(rect(x, py + b - 0.3, min(wd, px + pw - 8 - x), 0.6, '#6c6a64', opacity=0.55))
            x += wd + rnd.uniform(1, 3)
    for side in (px + 1.8, px + pw - 1.8):
        for b in range(1, 26, 2): o.append(circle(side, py + b, 0.5, '#d8d3c6'))
        o.append(line(side + (1.6 if side < 50 else -1.6), py, side + (1.6 if side < 50 else -1.6), py + 26, '#cfc9bb', 0.12, stroke_dasharray='0.6 0.4'))
    for k in range(12):
        o.append(line(px - 0.4 + k * 0.05, py + 26 + k * 0.42, px + pw + 0.4 - k * 0.05, py + 26 + k * 0.42, '#d9d4c7' if k % 2 else '#fbfaf3', 0.4))
    # two cards from the punch, laid in at a tilt
    p1 = set((c, rnd.choice([0, 1, 2, 3])) for c in range(34) if rnd.random() < 0.6)
    o.append(g([rect(0.6, 0.8, 40, 9, '#000', opacity=0.25, filter=D.blur(0.4))] + card(D, 0, 0, 40, 9, p1, rows=5, digits=False), transform='translate(50 5) rotate(-4)'))
    o.append(g([rect(0.6, 0.8, 40, 9, '#000', opacity=0.25, filter=D.blur(0.4))] + card(D, 0, 0, 40, 9, set(), fill='#f3e8cc', rows=5, digits=False), transform='translate(13 3) rotate(2.5)'))
    # the tray's front: graphite enamel, a rolled lip catching the light, a label holder
    fy = H - 14
    front = rrect(0, fy, W, 14, (1, 1, 1.8, 1.8))
    o.append(path(front, D.lin([(0, '#4a4844'), (0.15, '#34322f'), (1, '#1a1918')])))
    o.append(rect(0, fy, W, 1.6, D.lin([(0, '#8a8782'), (0.5, '#4e4c48'), (1, '#2a2927')])))
    o.append(rect(0, fy + 0.2, W, 0.35, '#ffffff', opacity=0.4))
    o.append(rect(0, fy, W, 14, D.lin([(0, '#ffffff', 0.08), (0.2, '#ffffff', 0), (1, '#000000', 0.2)], 0, 0, 1, 0)))
    hx, hy = W / 2 - 10, fy + 4.2
    o.append(rect(hx, hy, 20, 6.4, D.lin([(0, '#dcdad5'), (1, '#8e8b85')])))
    o.append(rect(hx + 1, hy + 1, 18, 4.4, '#f8f5ec'))
    o.append(text(W / 2, hy + 4.3, 'OUT', 2.6, '#1e1d1b', 'Work Sans', 600, 0.4, 'middle'))
    for sx in (hx + 0.5, hx + 19.5): o.append(circle(sx, hy + 3.2, 0.35, '#5c5a55'))
    return fin('out-tray', o, W, H, D, 91)

# ---- the deck box: walnut with finger-jointed corners and a brass card frame; the cards
# upright in it, their edges and guide tabs, the front card's printed digits and holes
def deck_box():
    W, H = 96, 64
    D = Defs(); o = []
    o.append(ellipse(48, 63.6, 47, 1.0, '#000', opacity=0.35, filter=D.blur(0.7)))
    # cards, their many top edges, behind the guide tabs
    for k in range(10):
        y = 10.5 + k * 0.5
        o.append(rect(4 + (k % 3) * 0.3, y, 88 - (k % 3) * 0.3, 20, '#efe4c8' if k % 2 else '#e3d6b6'))
        o.append(line(4, y, 92, y, '#b8a888', 0.12))
    tabs = [(10, 2.2, P['accent'], 'MUSIC', '#fff6ee'), (37, 3.4, P['ochre'], 'DADA', '#1e1d1b'), (64, 4.6, P['sage'], 'SIEVES', '#fff6ee')]
    for tx, ty, c, lab, ink in tabs:
        o.append(path(rrect(tx, ty, 20, 9, (1.2, 1.2, 0, 0)), D.lin([(0, light(c, 0.18)), (1, dark(c, 0.12))])))
        o.append(rect(tx + 1.6, ty + 1.2, 16.8, 4.2, '#fbf6ea', opacity=0.95 if ink == '#1e1d1b' else 0.0))
        o.append(text(tx + 10, ty + 4.4, lab, 2.3, ink, 'Jost', 600, 0.24, 'middle'))
        o.append(rect(tx, ty + 8, 20, 22, dark(c, 0.05)))
    rnd = random.Random(3)
    punches = set((c, rnd.choice([0, 1, 2, 3, 4, 5, 6])) for c in range(78) if rnd.random() < 0.5)
    o += card(D, 4, 12, 88, 24, punches)
    # the box: walnut, finger joints at its ends, its top edge lit, a brass frame and a pull
    fy = 28
    front = rrect(0, fy, W, H - fy, (0.8, 0.8, 1.4, 1.4))
    o.append(soft_shadow(D, front, 0.4, 0.8, 0.8, 0.35))
    o.append(g([wood(D, 0, fy, W, H - fy, P['walnut'], seed=9, lines=18, arches=1, contrast=1.2),
                rect(0, fy, W, H - fy, D.lin([(0, '#ffffff', 0.16), (0.08, '#ffffff', 0), (0.9, '#000000', 0), (1, '#000000', 0.25)])),
                rect(0, fy, W, H - fy, D.lin([(0, '#ffffff', 0.1), (0.06, '#ffffff', 0), (0.94, '#000000', 0), (1, '#000000', 0.2)], 0, 0, 1, 0))]
               + [rect(0 if s < 0 else W - 3, fy + k * 4.5, 3, 2.25, light(P['walnut'], 0.1) if s < 0 else dark(P['walnut'], 0.15)) for s in (-1, 1) for k in range(8)],
               clip_path=D.clip(path(front, '#000'))))
    o.append(rect(0, fy, W, 0.6, '#ffffff', opacity=0.3))
    hx, hy, hw, hh = 33, fy + 10, 30, 12
    o.append(rect(hx + 0.4, hy + 0.6, hw, hh, '#000', opacity=0.35, filter=D.blur(0.4)))
    o.append(rect(hx, hy, hw, hh, brass(D)))
    o.append(rect(hx + 1.5, hy + 1.5, hw - 3, hh - 3, '#f8f3e6'))
    o.append(rect(hx + 1.5, hy + 1.5, hw - 3, 0.8, '#000', opacity=0.12))
    o.append(text(hx + hw / 2, hy + hh / 2 + 1.0, 'DECKS', 2.8, '#1e1d1b', 'Work Sans', 600, 0.32, 'middle'))
    for sx in (hx + 0.8, hx + hw - 0.8): o.append(screw(D, sx, hy + hh / 2, 0.5, False, 30))
    o.append(path(rrect(W / 2 - 6, H - 7, 12, 2.6, 1.3), D.lin([(0, '#1b120c'), (1, '#4a3324')])))
    return fin('deck-box', o, W, H, D, 81)

# ---- a stool after Aalto's Stool 60 (1933): a round birch seat with a slate linoleum top,
# on three legs of laminated birch, each bent through a right angle under the seat
def stool():
    W, H = 84, 92
    D = Defs(); o = []
    birch, birchd, birchl = '#d9bd92', '#a9895f', '#f0dcb8'
    o.append(ellipse(42, 91.2, 36, 1.4, '#000', opacity=0.32, filter=D.blur(0.9)))
    def leg(x, bend, back=False):
        # one strip of laminated birch: up from the floor and, for the outer legs, bent through
        # a right angle to run in under the seat
        c0 = dark(birch, 0.22) if back else birch
        w, r, top = 3.4, 5.5, 10.6
        if bend == 0:
            d_ = 'M%s,%s L%s,%s' % (f(x), f(H - 1.4), f(x), f(top))
        else:
            d_ = 'M%s,%s L%s,%s A%s,%s 0 0 %d %s,%s L%s,%s' % (f(x), f(H - 1.4), f(x), f(top + r), f(r), f(r), 1 if bend > 0 else 0,
                                                            f(x + bend * r), f(top), f(x + bend * (r + 7)), f(top))
        out = [path(d_, 'none', stroke=dark(c0, 0.3), stroke_width=w + 0.4),
               path(d_, 'none', stroke=c0, stroke_width=w),
               path(d_, 'none', stroke=light(c0, 0.35), stroke_width=w * 0.3, transform='translate(-0.9 0)' if bend == 0 else 'translate(-0.8 -0.4)', opacity=0.8),
               path(d_, 'none', stroke=birchd, stroke_width=0.15, opacity=0.6, transform='translate(0.8 0)')]
        out.append(path(rrect(x - 2.0, H - 1.6, 4.0, 1.6, 0.6), '#2a2826'))
        return out
    o += leg(42, 0, True)
    o += leg(10, 1) + leg(74, -1)
    # the seat: its slate top, the birch rim and the plies along its edge
    o.append(soft_shadow(D, rrect(2, 2, 80, 8, 2.4), 0.4, 1.2, 0.8, 0.3))
    o.append(path(rrect(2, 4.2, 80, 5.8, (0, 0, 2.4, 2.4)), D.lin([(0, light(birch, 0.3)), (0.4, birch), (1, dark(birch, 0.25))])))
    for k in range(5):
        o.append(line(3.4, 5.4 + k * 0.9, 80.6, 5.4 + k * 0.9, birchl if k % 2 else birchd, 0.2, opacity=0.7))
    o.append(path(rrect(2, 1.6, 80, 3.0, (2.4, 2.4, 0, 0)), D.lin([(0, '#6d7a80'), (0.5, '#49555a'), (1, '#323b3f')], 0, 0, 1, 0)))
    o.append(rect(4, 1.8, 76, 0.5, '#ffffff', opacity=0.35))
    o.append(rect(2, 10, 80, 0.8, '#000', opacity=0.25, filter=D.blur(0.5)))
    return fin('stool', o, W, H, D, 115)

if __name__ == '__main__':
    import sys
    for w in (sys.argv[1:] or ['lamp', 'chair', 'mug', 'coding_form', 'out_tray', 'deck_box']): globals()[w]()
