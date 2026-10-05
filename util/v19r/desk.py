# The other things on the desk, each a picture in the same manner as the shelf and the
# tape machine: the lamp, the folders under the magazine, the coding form on its
# clipboard, the deck box and the out tray. Units are tenths of an em; SCALE px a unit.
import math, random
from mcm import *
from render import render, REPO
OUT = REPO + '/v19/assets'
SCALE = 5
GRAPH = '#2b2926'
KRAFT = '#bfae8e'
GREEN = '#3b6a55'

def common(seed):
    return print_filter('pr', 1.4, 0.2, seed) + grain_filter('gr', 1.1, 0.05, seed + 1) + blur_filter('soft', 0.8)

# ---- the lamp: a thin black stem and arm, and a shade like a cone cut on the slant, after
# the lamps Serge Mouille made in the 1950s; its brass knuckle and white throat
def lamp():
    W, H = 70, 106
    o = []
    # the base: a low black dome
    o.append(path('M4,106 C5,101.5 9,100.5 15,100.5 C21,100.5 25,101.5 26,106 Z', P['ink']))
    o.append(path('M7,104 C8,102.3 10.5,101.6 14,101.6', 'none', stroke=light(P['ink'], 0.3), stroke_width=0.35))
    # the stem, leaning, and the arm, curving out over the desk
    o.append(path('M15,101 C15.5,80 17,52 19.5,30', 'none', stroke=P['ink'], stroke_width=1.0, stroke_linecap='round'))
    o.append(path('M19.5,30 C27,22 38,19.5 49,21', 'none', stroke=P['ink'], stroke_width=0.8, stroke_linecap='round'))
    o.append(circle(19.5, 30, 1.5, P['brass'])); o.append(circle(19.1, 29.6, 0.6, light(P['brass'], 0.4)))
    # the shade: its outside black, its open mouth to the lower right showing the white throat
    cx, cy, ang = 53, 25, 38
    shade = g([path('M-4,-5.5 C-1,-8 5,-7.5 10,-4 L17,4 C13,9 4,10.5 -2,7 C-5.5,4 -6.5,-2 -4,-5.5 Z', P['ink']),
               path('M17,4 C13,9 4,10.5 -2,7 C3,6.8 11,4.6 17,4 Z', P['cream']),
               path('M17,4 C14.2,5.6 9,6.6 4,6.9', 'none', stroke=P['ochre'], stroke_width=0.35, opacity=0.8),
               path('M-3.3,-4.4 C-1,-6.4 3,-6.4 6.5,-4.6', 'none', stroke=light(P['ink'], 0.35), stroke_width=0.45),
               circle(-4.4, -1.2, 1.4, P['brass'])],
              transform='translate(%s %s) rotate(%s)' % (f(cx), f(cy), f(ang)))
    o.append(shade)
    return render('lamp', g(g(o, filter='url(#gr)'), filter='url(#pr)'), W, H, SCALE, OUT, defs=common(51))

# ---- the folders: three, stacked flat, edge on; the top one's tab lettered
def folders():
    W, H = 126, 28
    o = []
    layers = [(0, 0, 126, P['stone']), (3.5, 6.6, 125, P['linen']), (1.2, 13.2, 124, KRAFT)]
    for x, b, w, c in layers:
        y = H - b - 6.2
        o.append(path(rrect(x, y, w - x, 6.2, 0.5), c))
        o.append(rect(x, y, w - x, 1.0, light(c, 0.2)))
        o.append(rect(x, y + 5.2, w - x, 1.0, dark(c, 0.14)))
        # the papers inside, a lighter edge between the boards
        o.append(rect(x + 2, y + 2.4, w - x - 5, 1.5, P['paper']))
        o.append(line(x + 2, y + 3.15, w - 3, y + 3.15, P['stone'], 0.12))
    # a string tie round the middle folder, and the top folder's tab
    o.append(rect(56, H - 13.0 - 6.6, 0.5, 6.4, P['accent']))
    tx, tw, ty = 84, 32, H - 13.2 - 6.2
    o.append(path(rrect(tx, ty - 5.4, tw, 6.0, (1.4, 1.4, 0, 0)), KRAFT))
    o.append(rect(tx + 2, ty - 4.2, tw - 4, 3.6, P['paper']))
    o.append(text(tx + tw / 2, ty - 1.3, 'XENAKIS', 2.5, P['ink'], 'Jost', 600, 0.24, 'middle'))
    return render('folders', g(g(o, filter='url(#gr)'), filter='url(#pr)'), W, H, SCALE, OUT, defs=common(61))

# ---- the coding form: a FORTRAN coding sheet on a hardboard clipboard, a yellow pencil
# under the clip; the statements pencilled in as grey strokes in the columns
def coding_form():
    W, H = 70, 94
    o = []
    bx, by, bw, bh = 2, 3, 66, 90
    o.append(path(rrect(bx, by, bw, bh, 3), '#8c7258'))
    o.append(rect(bx, by, 1.6, bh, light('#8c7258', 0.12), clip_path='url(#board)'))
    sx, sy, sw, sh = bx + 4, by + 8, bw - 8, bh - 12
    o.append(rect(sx + 0.8, sy + 0.8, sw, sh, '#28180c', opacity=0.2, filter='url(#soft)'))
    sheet = [rect(sx, sy, sw, sh, P['paper'])]
    # the form's heading band and its column fields, in the form's green
    sheet.append(rect(sx + 2.5, sy + 5.5, sw - 5, 6, light(GREEN, 0.78)))
    sheet.append(text(sx + 3.6, sy + 9.6, 'FORTRAN CODING FORM', 2.0, GREEN, 'Work Sans', 600, 0.2))
    gx0, gx1, gy0 = sx + 2.5, sx + sw - 2.5, sy + 14
    rows, rh = 18, 3.4
    for r in range(rows + 1):
        sheet.append(line(gx0, gy0 + r * rh, gx1, gy0 + r * rh, GREEN, 0.14, opacity=0.7))
    for x in (gx0, gx0 + 5, gx0 + 6.2, gx0 + 44, gx1):
        sheet.append(line(x, gy0, x, gy0 + rows * rh, GREEN, 0.2 if x in (gx0, gx1) else 0.16, opacity=0.8))
    for c in range(1, 44):
        sheet.append(line(gx0 + 6.2 + c * 0.88, gy0, gx0 + 6.2 + c * 0.88, gy0 + rows * rh, GREEN, 0.05, opacity=0.35))
    # the pencilled statements, a stroke a word
    rnd = random.Random(5)
    prog = [(1, 'C', [9, 7, 5]), (0, '', [6, 9]), (0, '', [5, 3, 8]), (1, '10', [4, 6, 10]), (0, '', [8, 3, 4]), (0, '', [7]),
            (1, '20', [5, 7, 4]), (0, '', [9, 3]), (0, '', [6, 2, 6]), (1, '30', [8, 5]), (0, '', [4, 4, 4]), (0, '', [6]), (0, '', [4])]
    for r, (lab, num, words) in enumerate(prog):
        yy = gy0 + r * rh + rh * 0.62
        if num:
            sheet.append(path('M%s,%s l%s,%s' % (f(gx0 + 1), f(yy), f(len(num) * 1.2), f(rnd.uniform(-0.2, 0.2))), 'none', stroke='#5d5a57', stroke_width=0.42, stroke_linecap='round'))
        x = gx0 + 7.2 + (rnd.random() * 0.4)
        for wl in words:
            w = wl * 0.88 * 0.92
            d = 'M%s,%s c%s,%s %s,%s %s,%s' % (f(x), f(yy + rnd.uniform(-0.15, 0.15)), f(w * 0.3), f(-0.5), f(w * 0.7), f(0.5), f(w), f(rnd.uniform(-0.2, 0.2)))
            sheet.append(path(d, 'none', stroke='#5d5a57', stroke_width=0.42, stroke_linecap='round', opacity=0.9))
            x += w + 0.88 * 1.4
    o.append(g(sheet))
    # the pencil, under the clip and over the sheet
    pen = g([rect(-1.1, -22, 2.2, 40, P['ochre']), rect(-1.1, -22, 0.7, 40, light(P['ochre'], 0.3)),
             rect(-1.1, 18, 2.2, 3, P['steel']), rect(-1.1, 21, 2.2, 3, '#c98f86'),
             poly([(-1.1, -22), (1.1, -22), (0, -27)], P['oakl']), poly([(-0.4, -25.5), (0.4, -25.5), (0, -27)], P['ink'])],
            transform='translate(%s %s) rotate(-12)' % (f(bx + bw - 13), f(by + 34)))
    o.append(pen)
    # the clip: a rolled aluminium jaw, its lever and two rivets
    cx = bx + bw / 2
    o.append(path(rrect(cx - 13, by - 1, 26, 10, (2, 2, 4, 4)), P['alu']))
    o.append(rect(cx - 13, by + 6.6, 26, 2.4, P['steeld'], clip_path='url(#clipj)'))
    o.append(path('M%s,%s C%s,%s %s,%s %s,%s' % (f(cx - 8), f(by + 0.6), f(cx - 4), f(by - 3.8), f(cx + 4), f(by - 3.8), f(cx + 8), f(by + 0.6)), 'none', stroke=P['steeld'], stroke_width=1.2))
    for rx in (cx - 9, cx + 9): o.append(circle(rx, by + 4, 0.9, P['steel'], stroke=P['steeld'], stroke_width=0.2))
    o.append(path(rrect(cx - 13, by - 1, 26, 10, (2, 2, 4, 4)), 'none', stroke=P['ink'], stroke_width=0.22, transform='translate(-0.25 0.2)', opacity=0.7))
    defs = common(71) + clip('board', path(rrect(bx, by, bw, bh, 3), '#000')) + clip('clipj', path(rrect(cx - 13, by - 1, 26, 10, (2, 2, 4, 4)), '#000'))
    return render('coding-form', g(g(o, filter='url(#gr)'), filter='url(#pr)'), W, H, SCALE, OUT, defs=defs)

# ---- the deck box: a walnut card tray, cards upright in it; the front card's printed
# digits and punches, the guide cards' tabs, a brass label holder
def card_face(x, y, w, h, punches, seed, cut=True, fill=None, edge=None):
    out = []
    fill = fill or P['cream']
    shape = 'M%s,%s L%s,%s L%s,%s L%s,%s L%s,%s Z' % (f(x + 2.2), f(y), f(x + w), f(y), f(x + w), f(y + h), f(x), f(y + h), f(x), f(y + 2.2)) if cut else None
    out.append(path(shape, fill, stroke=edge, stroke_width=0.25 if edge else None) if cut else rect(x, y, w, h, fill))
    rnd = random.Random(seed)
    cols = int((w - 3) / 1.15)
    for row in range(int((h - 2.4) / 2.2)):
        for c in range(cols):
            cx = x + 1.8 + c * 1.15; cy = y + 3.2 + row * 2.2
            if (c, row) in punches: out.append(rect(cx - 0.3, cy - 0.65, 0.6, 1.2, P['ink']))
            elif row >= 1: out.append(rect(cx - 0.18, cy - 0.3, 0.36, 0.6, light(P['accent'], 0.45), opacity=0.7))
    return out

def deck_box():
    W, H = 96, 64
    o = []
    # cards behind the front, a little higher and lower, buff and stone; two guide cards
    for x, top, c in ((5, 9, P['stone']), (6, 7.5, P['cream']), (4.5, 10.5, '#e3d7bd')):
        o.append(rect(x, top, 86, 30, c)); o.append(rect(x, top, 86, 0.5, dark(c, 0.1)))
    o.append(path(rrect(12, 2.2, 20, 6.6, (1.2, 1.2, 0, 0)), P['accent']))
    o.append(text(22, 6.6, 'MUSIC', 2.3, P['paper'], 'Jost', 600, 0.24, 'middle'))
    o.append(path(rrect(40, 3.6, 20, 5.4, (1.2, 1.2, 0, 0)), P['ochre']))
    o.append(text(50, 7.6, 'DADA', 2.3, P['ink'], 'Jost', 600, 0.24, 'middle'))
    o.append(rect(4, 8.6, 88, 30, '#e8dfca'))
    o.append(path(rrect(66, 5.2, 20, 5.4, (1.2, 1.2, 0, 0)), P['sage']))
    o.append(text(76, 9.2, 'SIEVES', 2.3, P['paper'], 'Jost', 600, 0.24, 'middle'))
    rnd = random.Random(3)
    punches = set()
    for c in range(70):
        if rnd.random() < 0.55: punches.add((c, rnd.choice([0, 1, 2, 3, 4, 5])))
    o += card_face(5, 11, 86, 26, punches, 4)
    # the box: walnut front, its lit top edge, end grain and a brass card holder
    fy = 28
    box = [path(rrect(0, fy, W, H - fy, (0.6, 0.6, 1.2, 1.2)), P['walnut']),
           rect(0, fy, W, 1.2, P['walnutl']),
           rect(0, fy, 3.2, H - fy, light(P['walnut'], 0.08)), rect(W - 3.2, fy, 3.2, H - fy, P['walnutd'])]
    rr = random.Random(8)
    for k in range(8):
        yy = rr.uniform(fy + 3, H - 3); x1 = rr.uniform(-10, W - 30); x2 = x1 + rr.uniform(30, 70)
        box.append(path('M%s,%s C%s,%s %s,%s %s,%s' % (f(x1), f(yy), f(x1 + 15), f(yy - 1.2), f(x2 - 15), f(yy + 1), f(x2), f(yy)), 'none', stroke=P['walnutd'], stroke_width=0.3, opacity=0.8))
    o.append(g(box, clip_path='url(#box)'))
    hx, hy, hw, hh = 33, fy + 11, 30, 11.5
    o.append(rect(hx, hy, hw, hh, P['brass']))
    o.append(rect(hx + 1.4, hy + 1.4, hw - 2.8, hh - 2.8, P['paper']))
    o.append(rect(hx, hy, hw, 0.6, light(P['brass'], 0.4)))
    o.append(text(hx + hw / 2, hy + hh / 2 + 1.0, 'DECKS', 2.8, P['ink'], 'Work Sans', 600, 0.3, 'middle'))
    for sx in (hx + 0.7, hx + hw - 0.7): o.append(circle(sx, hy + hh / 2, 0.45, dark(P['brass'], 0.3)))
    o.append(path('M%s,%s h%s' % (f(hx + hw / 2 - 5), f(H - 6), f(10)), 'none', stroke=P['walnutd'], stroke_width=1.6, stroke_linecap='round'))
    defs = common(81) + clip('box', path(rrect(0, fy, W, H - fy, (0.6, 0.6, 1.2, 1.2)), '#000'))
    return render('deck-box', g(g(o, filter='url(#gr)'), filter='url(#pr)'), W, H, SCALE, OUT, defs=defs)

# ---- the out tray: a low graphite tray; fan-folded printout in it, green-barred, its
# sprocket holes down the edges; two cards from the punch on top
def out_tray():
    W, H = 104, 44
    o = []
    # the printout: a fold of sheets, each a little out of line
    for k, (x, y, w) in enumerate(((5, 10, 90), (6.5, 7.5, 88), (4.2, 5, 91))):
        hgt = 32 - y + 5
        sh = [rect(x, y, w, hgt, P['paper'])]
        for b in range(0, int(hgt), 4):
            if (b // 4) % 2 == 0: sh.append(rect(x + 4, y + 1 + b, w - 8, 2, '#dfe9dc'))
        for side in (x + 1.9, x + w - 1.9):
            for b in range(1, int(hgt), 2): sh.append(circle(side, y + b, 0.5, P['stone']))
            sh.append(line(side + (1.6 if side < x + 5 else -1.6), y, side + (1.6 if side < x + 5 else -1.6), y + hgt, P['stone'], 0.12))
        sh.append(rect(x, y, w, 0.5, P['stone']))
        o.append(g(sh))
    # two punched cards, laid in at a tilt, one with the corner cut
    rnd = random.Random(11)
    p1 = set((c, rnd.choice([0, 1, 2])) for c in range(30) if rnd.random() < 0.6)
    o.append(g(card_face(0, 0, 40, 9, p1, 12, fill='#e9d9b4', edge=P['oakd']), transform='translate(48 6.5) rotate(-4)'))
    o.append(g(card_face(0, 0, 40, 9, set(), 13, fill='#efe2c2', edge=P['oakd']), transform='translate(14 3.2) rotate(2.5)'))
    # the tray's front: graphite enamel, a lit lip and a little label
    fy = H - 14
    o.append(path(rrect(0, fy, W, 14, (1, 1, 1.6, 1.6)), GRAPH))
    o.append(rect(0, fy, W, 1.2, light(GRAPH, 0.22)))
    o.append(rect(0, fy + 1.2, W, 0.4, '#000', opacity=0.25))
    o.append(rect(W / 2 - 9, fy + 4.6, 18, 5.4, P['paper']))
    o.append(text(W / 2, fy + 8.4, 'OUT', 2.8, P['ink'], 'Work Sans', 600, 0.4, 'middle'))
    return render('out-tray', g(g(o, filter='url(#gr)'), filter='url(#pr)'), W, H, SCALE, OUT, defs=common(91))

if __name__ == '__main__':
    import sys
    which = sys.argv[1:] or ['lamp', 'folders', 'coding_form', 'deck_box', 'out_tray']
    for w in which: globals()[w]()
