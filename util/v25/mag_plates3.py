# The plates of Cons (Lisp, set as a botanical journal: leaf greens on a cream laid paper, its ferns grown by recursion) and
# Silver (the optics of photography: line diagrams in black on white), drawn in pixels, 264 x 96 each, the covers'
# fields 300 x 225. Each plate is its article's subject made a picture by its own rule.
import os as _os; UTIL = _os.path.normpath(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..')); REPO = _os.path.dirname(UTIL)
import math, random
import numpy as np
from PIL import Image
from PIL import ImageDraw
from mag_plates2 import canvas, save, F, FM

PAPER, INK, GRN, PHOS, PHOS_D, DARK = (244, 241, 228), (22, 32, 26), (31, 122, 70), (120, 220, 140), (40, 110, 70), (16, 22, 18)

# ---------------------------------------------------------------- Cons
# a botanical journal's plates: leaf greens and a little bark on a cream laid paper, every
# fern grown by recursion, as a list is built
PAPER, INK = (246, 241, 226), (34, 48, 30)
LEAF = [(30, 64, 32), (47, 93, 42), (79, 138, 58), (122, 176, 84), (176, 210, 130), (216, 232, 186)]
BARK, BARK_L, WITHER = (110, 84, 52), (150, 118, 76), (176, 132, 70)
BAY = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]

def laid(im):
    """the paper's laid lines, faint, every fourth row"""
    px = im.load()
    for y in range(0, im.height, 4):
        for x in range(im.width):
            if px[x, y] == PAPER: px[x, y] = (238, 232, 214)
    return im

def leaflet(d, x, y, ang, L, W, cols):
    """a leaflet from (x, y): a pointed oval along ang, lit on its upper side, a midrib"""
    ux, uy = math.cos(ang), math.sin(ang)
    for i in range(int(L * 2) + 1):
        t = i / (L * 2)
        w = W * math.sin(math.pi * t) ** 0.8
        cx, cy = x + ux * L * t, y + uy * L * t
        for k in range(-int(w * 2), int(w * 2) + 1):
            s = k / 2
            qx, qy = round(cx - uy * s), round(cy + ux * s)
            d.point((qx, qy), fill=cols[2] if s < 0 else cols[1])
        d.point((round(cx), round(cy)), fill=cols[0])

def frond(d, x, y, ang, L, depth, rnd, cols=LEAF, curl=0.0):
    """a fern frond: a rachis bending as it goes, its pinnae smaller toward the tip, each
    pinna itself a frond one level down"""
    steps = 18
    px_, py_ = x, y
    for i in range(steps):
        t = i / steps
        a = ang + curl * t
        nx, ny = px_ + math.cos(a) * L / steps, py_ + math.sin(a) * L / steps
        d.line([(px_, py_), (nx, ny)], fill=cols[0])
        size = L * 0.32 * (1 - t) ** 0.9
        if i > 1 and size > 1.2:
            for side in (-1, 1):
                pa = a + side * (1.05 - 0.3 * t)
                if depth > 0: frond(d, nx, ny, pa, size, depth - 1, rnd, cols, curl * 0.5 * side)
                else: leaflet(d, nx, ny, pa, max(1.5, size), max(0.8, size * 0.32), cols)
        px_, py_ = nx, ny

def crozier(d, cx, cy, r, turns, cols):
    """a fiddlehead: the young frond rolled in a spiral, its stalk under it"""
    pts = []
    for i in range(int(turns * 60)):
        t = i / 60 * 2 * math.pi
        rr = r * math.exp(-0.18 * t)
        pts.append((cx + rr * math.cos(t), cy + rr * math.sin(t)))
    for k, (p, q) in enumerate(zip(pts, pts[1:])):
        w = max(1, int(3 * (1 - k / len(pts))) + 1)
        d.line([p, q], fill=cols[1], width=w)
    for k in range(0, len(pts), 7):
        x, y = pts[k]; d.point((round(x), round(y)), fill=cols[3])
    d.line([(cx + r, cy), (cx + r + 2, cy + 40)], fill=cols[1], width=3)

def cn_listing():
    # the contents: five fiddleheads unrolling, one a little further than the last
    im, d = canvas(264, 96, PAPER)
    for k in range(5):
        cx = 26 + k * 52
        crozier(d, cx, 34 - k * 2, 9 + k * 1.6, 2.6 - k * 0.35, LEAF)
    for x in range(0, 264, 2): d.point((x, 90), fill=LEAF[4])
    return laid(im)

def cn_boxes():
    # (A (B C) D) as a plant: each cons cell a node on the stem, its car a branch, the atoms
    # leaves with their letters, the list's end a bud
    im, d = canvas(264, 96, PAPER)
    d.line([(14, 70), (250, 70)], fill=LEAF[1], width=2)
    nodes = [(40, 'A'), (110, None), (180, 'D')]
    for x, atom in nodes:
        d.ellipse([x - 3, 67, x + 3, 73], fill=BARK)
        if atom:
            d.line([(x, 67), (x, 44)], fill=LEAF[1], width=2); leaflet(d, x, 44, -math.pi / 2, 16, 6, LEAF[1:])
            d.text((x + 6, 30), atom, font=FM, fill=INK)
    # the sublist (B C): a branch with two nodes of its own
    d.line([(110, 67), (110, 40), (176, 26)], fill=LEAF[1], width=2)
    for x, y, a in ((128, 36, 'B'), (156, 30, 'C')):
        d.ellipse([x - 2, y - 2, x + 2, y + 2], fill=BARK); leaflet(d, x, y, -math.pi / 2 - 0.3, 13, 5, LEAF[1:])
        d.text((x + 5, y - 16), a, font=FM, fill=INK)
    d.ellipse([244, 66, 252, 74], fill=LEAF[3]); d.ellipse([246, 68, 250, 72], fill=LEAF[4])      # NIL, a bud
    d.text((190, 82), '(A (B C) D)', font=FM, fill=INK)
    return laid(im)

def cn_heap():
    # a collection, as the autumn floor of a wood: the leaves still reached from a stem green,
    # the rest withered, to be swept up and grown again
    rnd = random.Random(1960)
    im, d = canvas(264, 96, PAPER)
    stems = [(40, 0), (130, 0), (210, 0)]
    for sx, _ in stems: d.line([(sx, 0), (sx + 10, 40)], fill=BARK, width=2)
    for k in range(70):
        x, y = rnd.randint(6, 256), rnd.randint(30, 90)
        near = min(abs(x - (sx + 10)) for sx, _ in stems) < 38 and y < 72
        cols = LEAF[1:] if near else [BARK, WITHER, (204, 164, 100)]
        leaflet(d, x, y, rnd.uniform(0, 2 * math.pi), rnd.randint(6, 10), rnd.uniform(2.5, 3.5), cols)
        if near and rnd.random() < 0.5: d.line([(x, y), (x + (stems[0][0] - x) * 0.1, y - 6)], fill=LEAF[0])
    return laid(im)

def barnsley(w, h, n, scale, ox, oy, seed):
    """Barnsley's fern: four affine maps chosen with their weights, the points counted"""
    rnd = random.Random(seed)
    counts = np.zeros((h, w))
    x = y = 0.0
    for i in range(n):
        r = rnd.random()
        if r < 0.01: x, y = 0.0, 0.16 * y
        elif r < 0.86: x, y = 0.85 * x + 0.04 * y, -0.04 * x + 0.85 * y + 1.6
        elif r < 0.93: x, y = 0.2 * x - 0.26 * y, 0.23 * x + 0.22 * y + 1.6
        else: x, y = -0.15 * x + 0.28 * y, 0.26 * x + 0.24 * y + 0.44
        X, Y = int(ox + x * scale), int(oy - y * scale)
        if i > 20 and 0 <= X < w and 0 <= Y < h: counts[Y, X] += 1
    return counts

def fern_paint(im, counts, cols, lean=0):
    px = im.load(); h, w = counts.shape
    top = np.percentile(counts[counts > 0], 92) if (counts > 0).any() else 1
    for y in range(h):
        for x in range(w):
            c = counts[y, x]
            if c <= 0: continue
            v = min(1.0, c / top)
            f = v * (len(cols) - 1)
            i = int(f)
            k = min(len(cols) - 1, i + (1 if (f - i) * 16 > BAY[y % 4][x % 4] else 0))
            px[x, y] = cols[len(cols) - 1 - k]
    return im

def cn_machine():
    # symbols at work: Barnsley's fern, a picture that is its own definition, four maps
    im, d = canvas(264, 96, PAPER)
    c = np.rot90(barnsley(96, 264, 160000, 24, 46, 262, 1988), 1)
    fern_paint(im, c[:96, :264], LEAF[:5])
    return laid(im)

def cn_cards():
    # the catalogue: a herbarium sheet of five pressed fronds, each with its label and its tape
    rnd = random.Random(1962)
    im, d = canvas(264, 96, PAPER)
    for k in range(5):
        x = 16 + k * 50
        spec = barnsley(40, 78, 24000, 7.2, 20, 77, 1960 + k)
        sub = Image.new('RGB', (40, 78), PAPER); fern_paint(sub, spec, LEAF[:5])
        mask = Image.fromarray(((spec > 0) * 255).astype(np.uint8))
        im.paste(sub, (x, 2), mask); d = ImageDraw.Draw(im)
        d.rectangle([x + 4, 82, x + 34, 91], fill=(250, 246, 232), outline=BARK_L)
        d.line([(x + 8, 86), (x + 28, 86)], fill=INK); d.line([(x + 8, 88), (x + 22, 88)], fill=(140, 130, 110))
        d.rectangle([x + 14, 60, x + 22, 63], fill=(232, 226, 204))
    return laid(im)

def cn_cover():
    # the cover: one great frond of Barnsley's fern across the field, on the paper
    im, d = canvas(300, 225, PAPER)
    c = barnsley(300, 225, 420000, 21, 150, 222, 1988)
    fern_paint(im, c, LEAF[:5])
    return laid(im)

# ---------------------------------------------------------------- Silver
# the optics of photography as line diagrams: black rules on white over a faint graph paper,
# in the manner of Xenakis's graphs in Formalized Music; thin rules for rays, heavier for
# lenses, walls and film, a dashed rule for the axis, labels in the room's face
SP, SK, SG, SM = (252, 252, 250), (20, 20, 20), (226, 226, 222), (120, 120, 118)

def paper(w, h):
    im, d = canvas(w, h, SP)
    for x in range(0, w, 8): d.line([(x, 0), (x, h)], fill=SG if x % 40 else (210, 210, 206))
    for y in range(0, h, 8): d.line([(0, y), (w, y)], fill=SG if y % 40 else (210, 210, 206))
    return im, d

def dashed(d, p0, p1, on=4, off=3, fill=SK):
    (x0, y0), (x1, y1) = p0, p1
    L = math.hypot(x1 - x0, y1 - y0); n = int(L // (on + off)) + 1
    for k in range(n):
        a = k * (on + off) / L; b = min(1, (k * (on + off) + on) / L)
        d.line([(x0 + (x1 - x0) * a, y0 + (y1 - y0) * a), (x0 + (x1 - x0) * b, y0 + (y1 - y0) * b)], fill=fill)

def arrow(d, x, y0, y1, fill=SK):
    """an arrow standing from the axis at y0 to its tip at y1"""
    d.line([(x, y0), (x, y1)], fill=fill, width=2)
    s = -1 if y1 < y0 else 1
    d.polygon([(x - 3, y1 - 3 * s), (x + 3, y1 - 3 * s), (x, y1)], fill=fill)

def ray_head(d, p0, p1, fill=SK):
    """a small arrowhead at the middle of a ray, pointing the way the light goes"""
    (x0, y0), (x1, y1) = p0, p1
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2; a = math.atan2(y1 - y0, x1 - x0)
    d.polygon([(mx + 3 * math.cos(a), my + 3 * math.sin(a)), (mx - 3 * math.cos(a) + 2 * math.sin(a), my - 3 * math.sin(a) - 2 * math.cos(a)),
               (mx - 3 * math.cos(a) - 2 * math.sin(a), my - 3 * math.sin(a) + 2 * math.cos(a))], fill=fill)

def ray(d, pts, fill=SK, heads=True):
    d.line(pts, fill=fill)
    if heads:
        for p0, p1 in zip(pts, pts[1:]): ray_head(d, p0, p1, fill)

def lens(d, x, y0, y1, w=3):
    """a biconvex lens in outline, tall and narrow"""
    cy, h = (y0 + y1) / 2, (y1 - y0) / 2
    pts = [(x + w * math.cos(t) * 1.0, cy + h * math.sin(t)) for t in np.linspace(-math.pi / 2, math.pi / 2, 24)]
    pts += [(x - w * math.cos(t), cy + h * math.sin(t)) for t in np.linspace(math.pi / 2, -math.pi / 2, 24)]
    d.polygon(pts, outline=SK, fill=(236, 240, 244))

def label(d, x, y, s, anchor='l', fill=SK):
    w = d.textlength(s, font=F)
    d.text((x - (w if anchor == 'r' else w / 2 if anchor == 'c' else 0), y), s, font=F, fill=fill)

def dim(d, x0, x1, y, s):
    d.line([(x0, y), (x1, y)], fill=SM); d.line([(x0, y - 2), (x0, y + 2)], fill=SM); d.line([(x1, y - 2), (x1, y + 2)], fill=SM)
    label(d, (x0 + x1) / 2, y - 1, s, 'c')

def sv_cover():
    # the cover: a pinhole above, a thin lens below, the subject, the image and the formula
    im, d = paper(300, 225)
    # the pinhole: the subject, the wall with its hole, the film, two rays crossing
    ax = 52
    dashed(d, (16, ax), (284, ax), fill=SM)
    arrow(d, 40, ax, ax - 30); label(d, 18, ax + 4, 'SUBJECT')
    d.rectangle([150, 14, 153, ax - 2], fill=SK); d.rectangle([150, ax + 2, 153, 92], fill=SK); label(d, 128, 2, 'PINHOLE')
    d.rectangle([250, 14, 252, 92], fill=SK); label(d, 238, 2, 'FILM')
    ray(d, [(40, ax - 30), (151.5, ax), (251, ax + 26)])
    arrow(d, 246, ax, ax + 26)
    dim(d, 40, 151, 98, 'u'); dim(d, 152, 251, 98, 'f')
    # the lens: the three principal rays meeting at the image's tip
    ay, ly, lx, fx, vx = 168, 30, 140, 50, 240
    dashed(d, (16, ay), (284, ay), fill=SM)
    arrow(d, 40, ay, ay - ly)
    lens(d, lx, ay - 36, ay + 36); label(d, lx, ay - 50, 'LENS', 'c')
    d.rectangle([vx, ay - 36, vx + 2, ay + 36], fill=SK)
    tip = (40, ay - ly); img = (vx, ay + int(ly * (vx - lx) / (lx - 40)))
    ray(d, [tip, (lx, ay - ly), img]); ray(d, [tip, img]); ray(d, [tip, (lx, img[1]), img])
    arrow(d, vx - 4, ay, img[1] - 1)
    for x, t in ((lx - fx, 'F'), (lx + fx, "F'")): d.line([(x, ay - 3), (x, ay + 3)], fill=SK); label(d, x - 2, ay + 2, t)
    dim(d, 40, lx, 206, 'u'); dim(d, lx, vx, 206, 'v')
    label(d, 18, 112, '1/f = 1/u + 1/v')
    return im

def sv_stops():
    # the contents: the stops seen face on, each half the area of the one before
    im, d = paper(264, 96)
    names = ['f/2', 'f/2.8', 'f/4', 'f/5.6', 'f/8', 'f/11', 'f/16', 'f/22']
    r = 14.0
    xs = []
    for k, n in enumerate(names):
        cx = 20 + k * 31; xs.append((cx, r))
        d.ellipse([cx - r, 44 - r, cx + r, 44 + r], outline=SK, fill=(236, 240, 244)); d.ellipse([cx - 1, 43, cx + 1, 45], fill=SK)
        label(d, cx, 62, n, 'c')
        r /= 1.4142
    d.line([(xs[0][0], 26), (xs[0][0], 22), (xs[1][0], 22), (xs[1][0], 26)], fill=SM); label(d, xs[0][0] - 6, 8, 'HALF THE AREA')
    d.line([(xs[0][0], 76), (xs[0][0], 80), (xs[2][0], 80), (xs[2][0], 76)], fill=SM); label(d, xs[1][0], 80, 'D/2', 'c')
    label(d, 258, 80, 'N = f/D', 'r')
    return im

def graph_axes(d, x0, y0, x1, y1):
    d.line([(x0, y0), (x0, y1), (x1, y1)], fill=SK)

def sv_pinhole():
    # article 01: the blur of a pinhole, by its geometry and by diffraction, against its size
    im, d = paper(264, 96)
    X0, Y1, X1, Y0 = 26, 76, 180, 8
    sx = (X1 - X0) / 1.0; sy = (Y1 - Y0) / 1.6
    graph_axes(d, X0, Y0, X1, Y1)
    for k in range(1, 11):
        x = X0 + k * 0.1 * sx; d.line([(x, Y1), (x, Y1 + 2)], fill=SK)
    for k in (0.5, 1.0, 1.5):
        y = Y1 - k * sy; d.line([(X0 - 2, y), (X0, y)], fill=SK); label(d, X0 - 4, y - 6, str(k), 'r')
    d.line([(X0, Y1), (X0 + 1.0 * sx, Y1 - 1.0 * sy)], fill=SK); label(d, X0 + 0.95 * sx, Y1 - 0.95 * sy - 14, 'GEOMETRY', 'r')
    pts = [(X0 + dd * sx, Y1 - min(1.6, 0.134 / dd) * sy) for dd in np.linspace(0.085, 1.0, 80)]
    d.line(pts, fill=SK); label(d, X0 + 0.15 * sx, Y1 - 0.9 * sy - 4, 'DIFFRACTION')
    for v, t in ((0.33, 'PETZVAL'), (0.47, 'RAYLEIGH')):
        dashed(d, (X0 + v * sx, Y0 + 2), (X0 + v * sx, Y1), fill=SM); label(d, X0 + v * sx + (-2 if t == 'PETZVAL' else 2), Y0 - 3, t, 'r' if t == 'PETZVAL' else 'l', SM)
    label(d, (X0 + X1) / 2, 82, 'HOLE DIAMETER d (MM)', 'c')
    # the box camera, inset at the right
    d.rectangle([200, 12, 252, 40], outline=SK); d.rectangle([199, 24, 201, 28], fill=SP); d.line([(250, 14), (250, 38)], fill=SK, width=2)
    dim(d, 201, 250, 48, 'f = 100 MM')
    label(d, 258, 70, 'd = 2 × sqrt(fλ)', 'r')
    return im

def sv_depth():
    # article 02: the cones of light about the film, and the sharp zone at three stops
    im, d = paper(264, 96)
    ay, lx, fx = 24, 96, 176
    dashed(d, (4, ay), (196, ay), fill=SM)
    lens(d, lx, ay - 18, ay + 18); d.rectangle([lx + 6, ay - 18, lx + 8, ay - 12], fill=SK); d.rectangle([lx + 6, ay + 12, lx + 8, ay + 18], fill=SK)
    d.line([(fx, ay - 20), (fx, ay + 20)], fill=SK, width=2)
    # the far subject's rays meet in front of the film, the near one's behind it, S's on it
    for sx_, meet, t, ly in ((12, fx - 16, 'FAR', ay + 3), (40, fx, 'S', ay + 13), (68, fx + 16, 'NEAR', ay + 3)):
        col = SK if t == 'S' else SM
        for e in (-12, 12):
            d.line([(sx_, ay), (lx, ay + e)], fill=col)
            end = max(meet, fx)
            d.line([(lx, ay + e), (end, ay + e * (1 - (end - lx) / (meet - lx)))], fill=col)
            if meet < fx: d.line([(meet, ay), (fx + 4, ay - e * (fx + 4 - meet) / (meet - lx))], fill=col)
        d.ellipse([sx_ - 1, ay - 1, sx_ + 1, ay + 1], fill=col)
        label(d, sx_, ly, t, 'c', col)
    d.rectangle([fx - 1, ay - 4, fx + 1, ay + 4], fill=SK); label(d, fx + 5, ay - 6, 'c')
    # the zone: a log scale from 1 m to infinity, the bars for f/8, f/16 and f/32
    def X(m): return 30 + (math.log10(m) / math.log10(20)) * 190 if m < 999 else 240
    y = 86
    d.line([(X(1), y), (X(20), y)], fill=SK)
    for m in (1, 2, 3, 5, 10, 20): d.line([(X(m), y), (X(m), y + 2)], fill=SK); label(d, X(m), y - 1, str(m), 'c')
    label(d, 240, y - 6, 'INF', 'c')
    for k, (n, a, b) in enumerate((('f/8', 2.34, 4.19), ('f/16', 1.92, 6.92), ('f/32', 1.41, 1e9))):
        yy = 56 + k * 9
        d.rectangle([X(a), yy, min(X(b), 238), yy + 5], outline=SK, fill=(236, 240, 244)); label(d, 6, yy - 3, n)
    dashed(d, (X(3), 52), (X(3), 82), fill=SM); label(d, X(3) + 2, 46, 'FOCUS', 'l', SM)
    label(d, 258, 0, 'H = f²/(Nc) + f', 'r')
    return im

def sv_aberration():
    # article 03: spherical aberration, rays through a plano-convex lens, curved face first
    im, d = paper(264, 96)
    ay, lx = 46, 40
    dashed(d, (4, ay), (258, ay), fill=SM)
    # the lens in section: a curved face at the left, flat at the right
    pts = [(lx - 7 * math.cos(t), ay + 38 * math.sin(t)) for t in np.linspace(-math.pi / 2, math.pi / 2, 30)] + [(lx + 2, ay + 38), (lx + 2, ay - 38)]
    d.polygon(pts, outline=SK, fill=(236, 240, 244))
    paraxial, short = 236, 0.2 * (236 - lx)
    cross = []
    for k in range(1, 6):
        h = k * 6.6; frac = (k / 5) ** 2
        fxk = paraxial - short * frac
        cross.append(fxk)
        for s_ in (-1, 1):
            y = ay + s_ * h
            d.line([(4, y), (lx - 7 * math.sqrt(max(0, 1 - (h / 38) ** 2)), y)], fill=SK)
            ray_head(d, (4, y), (lx - 6, y))
            end = min(258, fxk + 22)
            d.line([(lx + 2, y), (end, ay + (ay - y) * (end - fxk) / (fxk - lx - 2) * -1 + 0 if False else ay - s_ * h * (end - fxk) / (fxk - lx - 2))], fill=SK)
    label(d, 258, ay + 20, 'PARAXIAL FOCUS', 'r')
    waist = cross[-1] + (paraxial - cross[-1]) * 0.35
    d.line([(waist, ay - 6), (waist, ay + 6)], fill=SK, width=2); label(d, waist, ay - 30, 'SMALLEST SPOT', 'c')
    dim(d, cross[-1], paraxial, 84, 'ABERRATION')
    label(d, 6, 82, 'f = R/(n - 1)')
    return im

def sv_angles():
    # the catalogue: the angle of view of three lenses, fanning out from the film's diagonal
    im, d = paper(264, 96)
    ay, film = 44, 250
    dashed(d, (4, ay), (258, ay), fill=SM)
    d.line([(film, ay - 22), (film, ay + 22)], fill=SK, width=3); label(d, film, ay + 24, '24 × 36', 'r')
    for fl, t, reach in ((28, '28 MM: 75°', 46), (50, '50 MM: 47°', 70), (135, '135 MM: 18°', 96)):
        x = film - fl * 1.15
        half = math.atan(21.6 / fl)
        for s_ in (-1, 1):
            d.line([(film, ay + s_ * 22), (x, ay)], fill=(190, 190, 186))
            d.line([(x, ay), (x - reach, ay - s_ * reach * math.tan(half))], fill=SK)
        d.line([(x, ay - 3), (x, ay + 3)], fill=SK)
        ex, ey = x - reach, ay - reach * math.tan(half)
        if fl == 28: label(d, ex + 4, ay + reach * math.tan(half) - 2, t, 'c')
        else: label(d, max(30, ex + 4), max(0, ey - 12), t, 'c')
    lens(d, film - 28 * 1.15, ay - 10, ay + 10, 2)
    dim(d, film - 50, film - 6, 86, 'd = 43.27 MM')
    label(d, 6, 82, 'A = 2 × arctan(d/2f)')
    return im

if __name__ == '__main__':
    for name, fn in (('cn-contents.png', cn_listing), ('cn-a1.png', cn_boxes), ('cn-a2.png', cn_heap), ('cn-a3.png', cn_machine),
                     ('cn-catalogue.png', cn_cards), ('cn-cover-field.png', cn_cover),
                     ('sv-contents.png', sv_stops), ('sv-a1.png', sv_pinhole), ('sv-a2.png', sv_depth), ('sv-a3.png', sv_aberration),
                     ('sv-catalogue.png', sv_angles), ('sv-cover-field.png', sv_cover)):
        save(fn(), name)
    names = ['cn-contents', 'cn-a1', 'cn-a2', 'cn-a3', 'cn-catalogue', 'sv-contents', 'sv-a1', 'sv-a2', 'sv-a3', 'sv-catalogue']
    sheet = Image.new('RGB', (264 * 2 + 6, 96 * 5 + 24), (90, 90, 90))
    for i, n in enumerate(names):
        sheet.paste(Image.open(REPO + '/v25/assets/st/%s.png' % n), ((i // 5) * 270, (i % 5) * 100))
    sheet.save(UTIL + '/v25/plates3.png')
    c = Image.new('RGB', (606, 225)); c.paste(Image.open(REPO + '/v25/assets/st/cn-cover-field.png'), (0, 0)); c.paste(Image.open(REPO + '/v25/assets/st/sv-cover-field.png'), (306, 0))
    c.save(UTIL + '/v25/covers4.png')
    print('ok')
