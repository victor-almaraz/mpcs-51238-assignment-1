# v23's thin and leafy things drawn directly in pixels, after v21's drawings (their sizes and
# places, their parts and colours), where pixelating the drawings breaks thin lines and
# leaves into noise. Leaves are rasterized from analytic shapes, pixel centre by pixel
# centre, without smoothing: a light half toward the window, a dark half, a midrib, and the
# silhouette closed by a darker green (pix.selout), so a few strong shapes suggest a plant.
import math, random
import numpy as np
from PIL import Image, ImageDraw
from pix import selout, orphans

INK = (30, 29, 27)
G_D, G_M, G_L, G_H = (59, 106, 85), (90, 122, 70), (126, 160, 98), (176, 198, 140)
TERRA, TERRA_L, TERRA_D = (181, 70, 43), (220, 110, 80), (116, 62, 43)
TEAK, TEAK_D = (168, 119, 83), (116, 62, 43)
BRASS, BRASS_L = (201, 154, 46), (240, 196, 106)
WHITE, WHITE_D, WHITE_DD = (251, 248, 240), (216, 209, 195), (180, 175, 162)
STEEL, STEEL_D = (98, 96, 89), (30, 29, 27)

class Canvas:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.a = np.zeros((h, w, 4), dtype=np.uint8)
    def put(self, x, y, c):
        x, y = int(round(x)), int(round(y))
        if 0 <= x < self.w and 0 <= y < self.h: self.a[y, x, :3] = c; self.a[y, x, 3] = 255
    def line(self, x0, y0, x1, y1, c, w=1):
        n = int(max(abs(x1 - x0), abs(y1 - y0))) + 1
        for k in range(n + 1):
            t = k / max(n, 1)
            x, y = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
            for d in range(w): self.put(x + d, y, c)
    def curve(self, pts, c, w=1):
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]): self.line(x0, y0, x1, y1, c, w)
    def rect(self, x0, y0, x1, y1, c):
        self.a[max(0, y0):y1 + 1, max(0, x0):x1 + 1, :3] = c; self.a[max(0, y0):y1 + 1, max(0, x0):x1 + 1, 3] = 255
    def image(self): return Image.fromarray(self.a)

def bez(p0, p1, p2, n=24):
    return [((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0], (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]) for t in (k / n for k in range(n + 1))]

def leaf(cv, bx, by, length, width, ang, shape, cols=(G_D, G_M, G_L), slits=0, rnd=None):
    """a leaf from its base (bx, by), pointing at ang (degrees, 0 up), rasterized at pixel
    centres: shape(u, v) says whether the point at u along (0..1) and v across (-1..1) is in"""
    a = math.radians(ang); ux, uy = math.sin(a), -math.cos(a); vx, vy = -uy, ux
    R = int(length + width) + 2
    dark, mid, lite = cols
    for y in range(int(by) - R, int(by) + R):
        for x in range(int(bx) - R, int(bx) + R):
            dx, dy = x + 0.5 - bx, y + 0.5 - by
            u = (dx * ux + dy * uy) / length; v = (dx * vx + dy * vy) / (width / 2)
            if not 0 <= u <= 1 or not shape(u, v): continue
            if slits:
                # the monstera's slits: from the edge in toward the rib, between the lobes
                k = (u * slits) % 1
                if abs(v) > 0.38 and abs(k - 0.5) < 0.09 + 0.05 * abs(v): continue
            lit = (v < 0) == (math.sin(a) >= 0)        # the half toward the window
            c = lite if lit else mid
            if abs(v) < 0.12 and u < 0.92: c = dark if lit else lite   # the midrib
            cv.put(x, y, c)

def fig_shape(u, v):        # fiddle-leaf: narrow at the stalk, broad toward the rounded tip
    w = 0.35 + 0.65 * math.sin(math.pi * min(1, u * 1.15) ** 0.8) * (0.55 + 0.45 * u)
    return abs(v) <= w and (u < 0.93 or abs(v) < (1 - u) * 6)
def heart_shape(u, v):      # a heart: broad and lobed at the base, pointed at the tip
    w = math.sin(math.pi * u ** 0.75) * (1.05 - 0.35 * u)
    return abs(v) <= w
def mon_shape(u, v):        # monstera: a broad heart, its base notched at the stalk
    w = math.sin(math.pi * u ** 0.7)
    return abs(v) <= w and not (u < 0.12 and abs(v) < 0.3)

def finish(cv, out=True):
    im = cv.image()
    im = orphans(im, 1)
    return selout(im) if out else im

# ---------------------------------------------------------------- the lamp (7 x 10.6 em: 42 x 64)
def lamp():
    cv = Canvas(42, 64)
    # the foot: a black dome with a light on its shoulder, a brass collar
    for x in range(2, 17):
        top = 61 - int(2.6 * math.sin(math.pi * (x - 2) / 14))
        for y in range(top, 64): cv.put(x, y, INK)
    for x in (5, 6, 7): cv.put(x, 60, (98, 96, 89))
    cv.rect(8, 58, 10, 59, BRASS)
    # the stem rising, a little bowed; the arm curving out over the desk; two brass knuckles
    cv.curve(bez((9, 58), (9.5, 40), (11.6, 18)), INK)
    cv.curve(bez((11.6, 18), (18, 11), (29, 12.5)), INK)
    cv.put(11, 18, BRASS_L); cv.put(12, 18, BRASS); cv.put(29, 13, BRASS)
    # the shade, turned toward the desk: black outside, its open throat lit, the bulb's glint
    s = Canvas(42, 64)
    for y in range(6, 26):
        for x in range(26, 42):
            dx, dy = x + 0.5 - 32, y + 0.5 - 14
            a = math.radians(38); u = dx * math.cos(a) + dy * math.sin(a); v = -dx * math.sin(a) + dy * math.cos(a)
            if -3 < u < 10 and abs(v) < 3.2 + u * 0.45:
                c = INK
                if v > 2.0 + u * 0.45 - 1.4 and u > 2: c = (255, 232, 170)
                if v < -2.4 - u * 0.2 and u < 4: c = (79, 73, 67)
                cv.put(x, y, c)
    cv.put(36, 21, (255, 250, 240)); cv.put(35, 21, (255, 232, 170))
    return finish(cv, out=False)

# ---------------------------------------------------------------- the fiddle-leaf fig (11 x 21 em: 66 x 126)
def fig():
    rnd = random.Random(21)
    cv = Canvas(66, 126)
    # the teak tripod: three legs splayed, a ring under the pot
    for x0, x1 in ((33, 33), (25, 18), (41, 49)):
        cv.line(x0, 100, x1, 125, TEAK if x0 != 33 else TEAK_D, 2)
    cv.rect(21, 99, 45, 101, TEAK); cv.line(21, 99, 45, 99, (216, 189, 146))
    # the pot: terracotta, a rolled rim, the soil
    for y in range(82, 99):
        t = (y - 82) / 17; hw = 10 - t * 2.4
        for x in range(int(33 - hw), int(33 + hw) + 1):
            cv.put(x, y, TERRA_L if x < 33 - hw + 3 else TERRA_D if x > 33 + hw - 3 else TERRA)
    cv.rect(21, 78, 45, 82, TERRA); cv.line(21, 78, 45, 78, TERRA_L); cv.line(22, 82, 44, 82, TERRA_D)
    cv.line(23, 79, 43, 79, (61, 43, 32))
    # the trunk, rising with a slight sway; two branches out from it
    trunk = bez((33, 79), (36, 50), (33, 10), 40)
    cv.curve(trunk, (116, 62, 43), 2)
    cv.curve(bez((33.6, 50), (26, 44), (18, 43)), (116, 62, 43))
    cv.curve(bez((34.4, 40), (42, 35), (49, 33)), (116, 62, 43))
    spots = [(33, 10, 0), (32, 16, -40), (35, 19, 45), (31, 25, -70), (36, 28, 70), (32, 34, -55), (35, 37, 50), (18, 43, -30), (24, 45, -100),
             (49, 33, 30), (43, 36, 100), (32, 47, -80), (36, 53, 85), (33, 60, -110), (35, 66, 115), (26, 44, 160), (41, 35, -160)]
    rnd.shuffle(spots)
    for x, y, a in spots:
        a += rnd.uniform(-10, 10)
        leaf(cv, x, y, rnd.uniform(14, 17), rnd.uniform(11, 13), a, fig_shape, (G_D, G_M, G_L) if rnd.random() < 0.6 else (G_D, G_D, G_M))
    return finish(cv)

# ---------------------------------------------------------------- the monstera (14 x 16 em: 84 x 96)
def monstera():
    rnd = random.Random(31)
    cv = Canvas(84, 96)
    cx = 42
    # brass hairpin legs under a white pot
    for x in (cx - 12, cx + 12):
        cv.line(x - 2, 77, x - 4, 95, BRASS); cv.line(x + 2, 77, x - 2, 95, BRASS)
        cv.put(x - 4, 95, BRASS_L)
    stems = [(-62, 24, 0.9), (64, 24, 0.9), (-34, 22, 0.7), (32, 21, 0.7), (-14, 30, 0.4), (16, 30, 0.35), (0, 22, 0.1)]
    for ang, L, depth in stems:
        a = math.radians(ang)
        tx, ty = cx + math.sin(a) * L * 0.9, 62 - math.cos(a) * L * 1.5
        cv.curve(bez((cx, 62), (cx + math.sin(a) * L * 0.25, 62 - L * 0.8), (tx, ty)), (59, 106, 85) if depth > 0.5 else G_M)
    order = sorted(stems, key=lambda s: -s[2])
    for ang, L, depth in order:
        a = math.radians(ang)
        tx, ty = cx + math.sin(a) * L * 0.9, 62 - math.cos(a) * L * 1.5
        size = 15 + (1 - depth) * 4
        cols = (G_D, G_D, G_M) if depth > 0.5 else (G_D, G_M, G_L)
        leaf(cv, tx, ty, size, size * 1.15, ang * 1.15 + rnd.uniform(-6, 6), mon_shape, cols, slits=4)
    # the pot: white, lit at its left, its rim
    for y in range(62, 78):
        hw = 14 if y < 75 else 14 - (y - 74)
        for x in range(cx - hw, cx + hw + 1):
            cv.put(x, y, WHITE if x < cx - hw + 5 else WHITE_DD if x > cx + hw - 4 else WHITE_D if x > cx + 4 else WHITE)
    cv.line(cx - 14, 62, cx + 14, 62, (61, 43, 32))
    return finish(cv)

# ---------------------------------------------------------------- the pothos (10 x 11.6 em: 60 x 70; the desk at 49)
def pothos():
    rnd = random.Random(8)
    cv = Canvas(60, 70)
    DESK, cx = 49, 30
    vines = [((cx - 4, DESK - 13), [(-9, -12), (-12, -23), (-10, -31)]), ((cx + 3, DESK - 13), [(6, -13), (12, -22), (14, -28)]),
             ((cx + 6, DESK - 12), [(12, -3), (17, 6), (19, 18)]), ((cx - 6, DESK - 12), [(-11, -1), (-14, 8), (-13, 19)]),
             ((cx, DESK - 14), [(0, -14), (-2, -26)]), ((cx + 7, DESK - 12), [(12, -7), (18, -5), (20, 0)])]
    leaves = []
    for (x0, y0), pts in vines:
        px_, py_ = x0, y0
        path_ = [(x0, y0)]
        for dx, dy in pts:
            nx, ny = x0 + dx, y0 + dy
            path_ += bez((px_, py_), ((px_ + nx) / 2 + rnd.uniform(-2, 2), (py_ + ny) / 2), (nx, ny), 8)[1:]
            ang = math.degrees(math.atan2(dx, -dy))
            leaves.append((nx, ny, rnd.uniform(6, 7.5), ang + 180 if dy > 0 else ang + rnd.choice([-60, 60])))
            leaves.append(((px_ + nx) / 2, (py_ + ny) / 2, rnd.uniform(5, 6.5), rnd.uniform(0, 360)))
            px_, py_ = nx, ny
        cv.curve(path_, G_D)
    for k in range(8):
        leaves.append((cx + rnd.uniform(-7, 7), DESK - 13 + rnd.uniform(-3, 1), rnd.uniform(6.5, 8), -150 + k * 40 + rnd.uniform(-8, 8)))
    for x, y, s, a in leaves:
        leaf(cv, x, y, s, s * 1.3, a, heart_shape, (G_D, G_M, (196, 206, 120)) if rnd.random() < 0.5 else (G_D, G_M, G_L))
    # the pot: stoneware, its lower half dipped in slate
    for y in range(DESK - 13, DESK):
        t = (y - DESK + 13) / 13; hw = 8 - int(t * t * 3)
        for x in range(cx - hw, cx + hw + 1):
            dip = y > DESK - 7 + (x - cx) * 0.15
            base = (73, 85, 90) if dip else WHITE
            cv.put(x, y, base if x < cx + hw - 2 else (60, 66, 66) if dip else WHITE_D)
    cv.line(cx - 8, DESK - 13, cx + 8, DESK - 13, (61, 43, 32))
    return finish(cv)

# ---------------------------------------------------------------- the shelf (40 x 15.2 em: 240 x 91)
def shelf():
    cv = Canvas(240, 91)
    # the ladders: two steel uprights each, rungs every third pixel
    for x in (6, 228):
        for ux in (x, x + 5):
            cv.line(ux, 19, ux, 90, STEEL_D)
        for y in range(21, 91, 3): cv.line(x + 1, y, x + 4, y, (79, 73, 67))
    # the board: oak, lit along its top edge, darker underneath
    cv.rect(0, 77, 239, 80, (200, 169, 126)); cv.line(0, 77, 239, 77, (224, 205, 176)); cv.line(0, 81, 239, 81, (169, 139, 104))
    # the bookend: folded steel
    cv.rect(73, 53, 74, 76, INK); cv.line(63, 76, 74, 76, INK)
    return cv.image()
