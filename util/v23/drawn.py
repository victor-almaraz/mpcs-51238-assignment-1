# v23's thin and leafy things drawn directly in pixels, after v21's drawings (their sizes and
# places, their parts and colours), where pixelating the drawings breaks thin lines and
# leaves into noise. Each is described in design units (a sixth of an em) and rasterized at
# the room's resolution (K art pixels to the design unit), sampling every pixel's centre:
# no smoothing, so edges are hard at any scale. Leaves have a light half toward the window,
# a dark half and a midrib, and the silhouette is closed by a darker green (pix.selout).
import math, random
import numpy as np
from PIL import Image
from pix import selout, orphans

K = (640 / 92) / 6          # art pixels to a design unit: the room is 640 art pixels across
INK = (30, 29, 27)
G_D, G_M, G_L = (59, 106, 85), (90, 122, 70), (126, 160, 98)
TERRA, TERRA_L, TERRA_D = (181, 70, 43), (220, 110, 80), (116, 62, 43)
TEAK, TEAK_D = (168, 119, 83), (116, 62, 43)
BRASS, BRASS_L = (201, 154, 46), (240, 196, 106)
WHITE, WHITE_D, WHITE_DD = (251, 248, 240), (216, 209, 195), (180, 175, 162)
STEEL_D = (30, 29, 27)

class Canvas:
    def __init__(self, w, h):
        self.W, self.H = int(round(w * K)), int(round(h * K))
        self.a = np.zeros((self.H, self.W, 4), dtype=np.uint8)
    def _set(self, X, Y, c):
        if 0 <= X < self.W and 0 <= Y < self.H: self.a[Y, X, :3] = c; self.a[Y, X, 3] = 255
    def fill(self, fn, box=None):
        """every art pixel whose centre fn(x, y) (in design units) gives a colour for"""
        x0, y0, x1, y1 = box or (0, 0, self.W / K, self.H / K)
        for Y in range(max(0, int(y0 * K) - 1), min(self.H, int(y1 * K) + 2)):
            for X in range(max(0, int(x0 * K) - 1), min(self.W, int(x1 * K) + 2)):
                c = fn((X + 0.5) / K, (Y + 0.5) / K)
                if c is not None: self._set(X, Y, c)
    def line(self, x0, y0, x1, y1, c, w=1):
        X0, Y0, X1, Y1 = x0 * K, y0 * K, x1 * K, y1 * K
        n = int(max(abs(X1 - X0), abs(Y1 - Y0))) + 1
        ww = max(1, int(round(w * K)))
        for k in range(n + 1):
            t = k / n
            X, Y = int(X0 + (X1 - X0) * t), int(Y0 + (Y1 - Y0) * t)
            for d in range(ww): self._set(X + d, Y, c)
    def curve(self, pts, c, w=1):
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]): self.line(x0, y0, x1, y1, c, w)
    def rect(self, x0, y0, x1, y1, c):
        self.fill(lambda x, y: c if x0 <= x < x1 + 1 and y0 <= y < y1 + 1 else None, (x0, y0, x1 + 1, y1 + 1))
    def dot(self, x, y, c): self._set(int(x * K), int(y * K), c)
    def image(self): return Image.fromarray(self.a)

def bez(p0, p1, p2, n=24):
    return [((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0], (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]) for t in (k / n for k in range(n + 1))]

def leaf(cv, bx, by, length, width, ang, shape, cols=(G_D, G_M, G_L), slits=0):
    """a leaf from its base (bx, by), pointing at ang (degrees, 0 up): shape(u, v) says whether
    the point u along (0..1) and v across (-1..1) is in"""
    a = math.radians(ang); ux, uy = math.sin(a), -math.cos(a); vx, vy = -uy, ux
    R = length + width
    dark, mid, lite = cols
    def fn(x, y):
        dx, dy = x - bx, y - by
        u = (dx * ux + dy * uy) / length; v = (dx * vx + dy * vy) / (width / 2)
        if not 0 <= u <= 1 or not shape(u, v): return None
        if slits:
            k = (u * slits) % 1
            if abs(v) > 0.38 and abs(k - 0.5) < 0.09 + 0.05 * abs(v): return None
        lit = (v < 0) == (math.sin(a) >= 0)
        if abs(v) < 0.12 and u < 0.92: return dark if lit else lite
        return lite if lit else mid
    cv.fill(fn, (bx - R, by - R, bx + R, by + R))

def fig_shape(u, v):
    w = 0.35 + 0.65 * math.sin(math.pi * min(1, u * 1.15) ** 0.8) * (0.55 + 0.45 * u)
    return abs(v) <= w and (u < 0.93 or abs(v) < (1 - u) * 6)
def heart_shape(u, v):
    return abs(v) <= math.sin(math.pi * u ** 0.75) * (1.05 - 0.35 * u)
def mon_shape(u, v):
    return abs(v) <= math.sin(math.pi * u ** 0.7) and not (u < 0.12 and abs(v) < 0.3)

def finish(cv, out=True):
    im = orphans(cv.image(), 1)
    return selout(im) if out else im

# ---------------------------------------------------------------- the lamp (7 x 10.6 em)
def lamp():
    cv = Canvas(42, 64)
    cv.fill(lambda x, y: INK if 2 <= x < 17 and y >= 61 - 2.6 * math.sin(math.pi * (x - 2) / 14) else None, (2, 58, 17, 64))
    cv.rect(5, 60, 7, 60, (98, 96, 89)); cv.rect(8, 58, 10, 59, BRASS)
    cv.curve(bez((9, 58), (9.5, 40), (11.6, 18)), INK)
    cv.curve(bez((11.6, 18), (18, 11), (29, 12.5)), INK)
    cv.dot(11, 18, BRASS_L); cv.dot(12, 18, BRASS); cv.dot(29, 13, BRASS)
    def shade(x, y):
        dx, dy = x - 32, y - 14
        a = math.radians(38); u = dx * math.cos(a) + dy * math.sin(a); v = -dx * math.sin(a) + dy * math.cos(a)
        if not (-3 < u < 10 and abs(v) < 3.2 + u * 0.45): return None
        if v > 2.0 + u * 0.45 - 1.4 and u > 2: return (255, 232, 170)
        if v < -2.4 - u * 0.2 and u < 4: return (79, 73, 67)
        return INK
    cv.fill(shade, (24, 4, 42, 27))
    cv.dot(36, 21, (255, 250, 240)); cv.dot(35, 21, (255, 232, 170))
    return finish(cv, out=False)

# ---------------------------------------------------------------- the fiddle-leaf fig (11 x 21 em)
def fig():
    rnd = random.Random(21)
    cv = Canvas(66, 126)
    for x0, x1 in ((33, 33), (25, 18), (41, 49)):
        cv.line(x0, 100, x1, 125, TEAK if x0 != 33 else TEAK_D, 2)
    cv.rect(21, 99, 45, 101, TEAK); cv.line(21, 99, 45, 99, (216, 189, 146))
    def pot(x, y):
        if not 82 <= y < 99: return None
        hw = 10 - (y - 82) / 17 * 2.4
        if abs(x - 33) > hw: return None
        return TERRA_L if x < 33 - hw + 3 else TERRA_D if x > 33 + hw - 3 else TERRA
    cv.fill(pot, (20, 82, 46, 99))
    cv.rect(21, 78, 45, 82, TERRA); cv.line(21, 78, 45, 78, TERRA_L); cv.line(22, 82, 44, 82, TERRA_D)
    cv.line(23, 79, 43, 79, (61, 43, 32))
    cv.curve(bez((33, 79), (36, 50), (33, 10), 40), TEAK_D, 2)
    cv.curve(bez((33.6, 50), (26, 44), (18, 43)), TEAK_D)
    cv.curve(bez((34.4, 40), (42, 35), (49, 33)), TEAK_D)
    spots = [(33, 10, 0), (32, 16, -40), (35, 19, 45), (31, 25, -70), (36, 28, 70), (32, 34, -55), (35, 37, 50), (18, 43, -30), (24, 45, -100),
             (49, 33, 30), (43, 36, 100), (32, 47, -80), (36, 53, 85), (33, 60, -110), (35, 66, 115), (26, 44, 160), (41, 35, -160)]
    rnd.shuffle(spots)
    for x, y, a in spots:
        a += rnd.uniform(-10, 10)
        leaf(cv, x, y, rnd.uniform(14, 17), rnd.uniform(11, 13), a, fig_shape, (G_D, G_M, G_L) if rnd.random() < 0.6 else (G_D, G_D, G_M))
    return finish(cv)

# ---------------------------------------------------------------- the monstera (14 x 16 em)
def monstera():
    rnd = random.Random(31)
    cv = Canvas(84, 96)
    cx = 42
    for x in (cx - 12, cx + 12):
        cv.line(x - 2, 77, x - 4, 95, BRASS); cv.line(x + 2, 77, x - 2, 95, BRASS)
        cv.dot(x - 4, 95, BRASS_L)
    stems = [(-62, 24, 0.9), (64, 24, 0.9), (-34, 22, 0.7), (32, 21, 0.7), (-14, 30, 0.4), (16, 30, 0.35), (0, 22, 0.1)]
    for ang, L, depth in stems:
        a = math.radians(ang)
        tx, ty = cx + math.sin(a) * L * 0.9, 62 - math.cos(a) * L * 1.5
        cv.curve(bez((cx, 62), (cx + math.sin(a) * L * 0.25, 62 - L * 0.8), (tx, ty)), G_D if depth > 0.5 else G_M)
    for ang, L, depth in sorted(stems, key=lambda s: -s[2]):
        a = math.radians(ang)
        tx, ty = cx + math.sin(a) * L * 0.9, 62 - math.cos(a) * L * 1.5
        size = 15 + (1 - depth) * 4
        leaf(cv, tx, ty, size, size * 1.15, ang * 1.15 + rnd.uniform(-6, 6), mon_shape, (G_D, G_D, G_M) if depth > 0.5 else (G_D, G_M, G_L), slits=4)
    def pot(x, y):
        if not 62 <= y < 78: return None
        hw = 14 if y < 75 else 14 - (y - 74)
        if abs(x - cx) > hw: return None
        return WHITE if x < cx - hw + 5 else WHITE_DD if x > cx + hw - 4 else WHITE_D if x > cx + 4 else WHITE
    cv.fill(pot, (cx - 15, 62, cx + 15, 78))
    cv.line(cx - 14, 62, cx + 14, 62, (61, 43, 32))
    return finish(cv)

# ---------------------------------------------------------------- the pothos (10 x 11.6 em; the desk at 49)
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
        leaf(cv, x, y, s, s * 1.3, a, heart_shape, (G_D, G_M, (158, 174, 84)) if rnd.random() < 0.5 else (G_D, G_M, G_L))
    def pot(x, y):
        if not DESK - 13 <= y < DESK: return None
        t = (y - DESK + 13) / 13; hw = 8 - t * t * 3
        if abs(x - cx) > hw: return None
        dip = y > DESK - 7 + (x - cx) * 0.15
        return ((73, 85, 90) if dip else WHITE) if x < cx + hw - 2 else ((60, 66, 66) if dip else WHITE_D)
    cv.fill(pot, (cx - 9, DESK - 13, cx + 9, DESK))
    cv.line(cx - 8, DESK - 13, cx + 8, DESK - 13, (61, 43, 32))
    return finish(cv)

# ---------------------------------------------------------------- the shelf (40 x 15.2 em)
def shelf():
    cv = Canvas(240, 91)
    for x in (6, 228):
        for ux in (x, x + 5): cv.line(ux, 19, ux, 90, STEEL_D)
        y = 21
        while y < 91: cv.line(x + 1, y, x + 4, y, (79, 73, 67)); y += 3
    cv.rect(0, 77, 239, 80, (200, 169, 126)); cv.line(0, 77, 239, 77, (224, 205, 176)); cv.line(0, 81, 239, 81, (169, 139, 104))
    cv.rect(73, 53, 74, 76, INK); cv.line(63, 76, 74, 76, INK)
    return cv.image()
