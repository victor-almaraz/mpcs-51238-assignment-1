# v24's swappable things, drawn in pixels as v23's room is (drawn.Canvas: design units of a
# sixth of an em, rasterized at the room's resolution): after v22's variations, each in the box
# of the thing it stands in for, so it takes the same place. Unlit; light.py lights them.
import os as _os; UTIL = _os.path.normpath(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..')); REPO = _os.path.dirname(UTIL)
import sys, os, math, random
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE + '/../v23')
import numpy as np
from PIL import Image
from drawn import Canvas, K, bez, leaf, finish, G_D, G_M, G_L, TERRA, TERRA_L, TERRA_D, TEAK, TEAK_D, BRASS, BRASS_L, WHITE, WHITE_D, WHITE_DD, INK
from room2 import frame, text, PAPER, CREAM

OAK = (200, 169, 126)
SLATE, SLATE_D, SLATE_L = (73, 85, 90), (49, 57, 61), (104, 118, 122)
BLUE, BLUE_L, NAVY = (43, 69, 96), (74, 104, 134), (30, 42, 58)
OCH, OCH_L, OCH_D = (201, 154, 46), (240, 196, 106), (154, 97, 54)
SAGE = (125, 138, 120)
GREY = (134, 123, 104)
GLOW = (255, 232, 170)
SOIL = (61, 43, 32)
VAR = (176, 170, 80)            # the snake plant's margins

def lerp(a, b, t): return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
def fan(cv, a, b, c, n, col):
    """string art: n + 1 lines from a point along a-b to the matching point along b-c"""
    for k in range(n + 1):
        t = k / n; p, q = lerp(a, b, t), lerp(b, c, t)
        cv.line(p[0], p[1], q[0], q[1], col)
def disc(cv, cx, cy, r, col):
    cv.fill(lambda x, y: col if (x - cx) ** 2 + (y - cy) ** 2 < r * r else None, (cx - r, cy - r, cx + r, cy + r))

# ---------------------------------------------------------------- the wide print (114 x 89)
def oak_frame(w, h):
    cv = Canvas(w, h)
    cv.rect(0, 0, w - 1, h - 1, OAK); frame(cv, 0, 0, w - 1, h - 1, OAK, 2)
    cv.rect(4, 4, w - 5, h - 5, PAPER)
    return cv
def caption(cv, x0, x1, y):
    cv.line(x0, y, x0 + 9, y, (150, 152, 136)); cv.line(x1 - 5, y, x1, y, (150, 152, 136))

def print_pavilion():
    # the Philips Pavilion: its shells as ruled surfaces against a pale sky, an ochre sun
    w, h = 114, 89
    cv = oak_frame(w, h)
    ix0, iy0, ix1, iy1 = 11, 10, w - 12, h - 17
    cv.rect(ix0, iy0, ix1, iy1, (214, 222, 220))
    cv.rect(ix0, iy1 - 8, ix1, iy1, (224, 205, 176))
    cv.line(ix0, iy1 - 8, ix1, iy1 - 8, (216, 189, 146))
    disc(cv, ix1 - 14, iy0 + 13, 6, OCH)
    fan(cv, (ix0 + 8, iy1 - 8), (ix0 + 34, iy0 + 4), (ix0 + 58, iy1 - 8), 12, BLUE_L)
    fan(cv, (ix0 + 34, iy0 + 4), (ix0 + 74, iy0 + 30), (ix0 + 84, iy1 - 8), 10, TERRA_L)
    cv.line(ix0 + 34, iy0 + 4, ix0 + 34, iy1 - 8, INK)
    for x in (ix0 + 20, ix0 + 23, ix0 + 66): cv.line(x, iy1 - 11, x, iy1 - 8, INK)
    caption(cv, ix0, ix1, h - 11)
    return cv.image()

def print_polytope():
    # a Polytope: cables hung across a dark hall, points of light along them
    rnd = random.Random(1967)
    w, h = 114, 89
    cv = oak_frame(w, h)
    ix0, iy0, ix1, iy1 = 11, 10, w - 12, h - 17
    cv.rect(ix0, iy0, ix1, iy1, NAVY)
    cv.fill(lambda x, y: BLUE if 0 < (x - ix0) - (y - iy0) * 0.9 < 22 and (int(x * K) + int(y * K)) % 2 == 0 else None, (ix0, iy0, ix1, iy1))
    cables = []
    for k in range(8):
        y0, sag = iy0 + 8 + k * 6, 6 + k * 0.6
        pts = [(x, y0 + sag * math.sin(math.pi * (x - ix0) / (ix1 - ix0)) - k * 0.8 * (x - ix0) / (ix1 - ix0) * 3) for x in np.linspace(ix0 + 1, ix1 - 1, 60)]
        cv.curve(pts, BLUE_L if k % 2 else (98, 120, 140))
        cables.append(pts)
    for k in range(34):
        pts = rnd.choice(cables); x, y = pts[rnd.randint(2, len(pts) - 3)]
        cv.dot(x, y, PAPER if rnd.random() < 0.6 else GLOW)
    caption(cv, ix0, ix1, h - 11)
    return cv.image()

# ---------------------------------------------------------------- the narrow print (68 x 86)
def black_frame(w, h, ground):
    cv = Canvas(w, h)
    cv.rect(0, 0, w - 1, h - 1, INK); cv.line(0, 0, w - 1, 0, (79, 73, 67)); cv.rect(2, 2, w - 3, h - 3, ground)
    return cv

def torn(cv, rnd, x, y, ww, hh, col):
    jit = [rnd.uniform(-0.6, 0.6) for _ in range(4)]
    def fn(px_, py_):
        u, v = px_ - x, py_ - y
        if not (jit[0] < u < ww + jit[1] and jit[2] < v < hh + jit[3]): return None
        X, Y = int(px_ * K), int(py_ * K)
        if (u < 0.9 or u > ww - 0.9 or v < 0.9 or v > hh - 0.9) and rnd.random() < 0.35: return None
        return col
    cv.fill(fn, (x - 1, y - 1, x + ww + 1, y + hh + 1))

def print_arp():
    # torn squares let fall after Arp: ink, greys and blue on a pale grey-green field
    rnd = random.Random(1917)
    w, h = 68, 86
    cv = black_frame(w, h, PAPER)
    cv.rect(7, 7, w - 8, h - 17, (206, 210, 204))
    for x, y, s, c in ((14, 22, 8, BLUE), (36, 18, 10, (150, 152, 146)), (44, 13, 7, INK), (26, 34, 9, INK), (38, 36, 11, (150, 152, 146)),
                       (50, 30, 6, INK), (12, 46, 7, PAPER), (30, 52, 8, (176, 178, 170)), (46, 54, 7, BLUE), (20, 58, 6, (98, 96, 89))):
        torn(cv, rnd, x, y, s, s * rnd.uniform(0.85, 1.15), c)
    cv.line(24, h - 10, 43, h - 10, GREY)
    return cv.image()

def print_taeuber():
    # a grid of rectangles and circles after Sophie Taeuber-Arp
    w, h = 68, 86
    cv = black_frame(w, h, (239, 226, 194))
    C, I, B, O, S, R = (239, 226, 194), INK, BLUE, OCH, (125, 145, 128), TERRA
    grid = ['BICIC', 'OCCCI', 'CSCCS', 'CCIpI', 'rOOBC', 'ISICI', 'kCICI']
    x0, y0, x1, y1 = 6, 6, w - 7, h - 15
    cw, ch = (x1 - x0) / 5, (y1 - y0) / 7
    cv.rect(x0, y0, x1, y1, (216, 209, 195))
    cols = {'C': C, 'I': I, 'B': B, 'O': O, 'S': S, 'r': R, 'p': C, 'k': C}
    for r_, row in enumerate(grid):
        for c_, ch_ in enumerate(row):
            a, b = x0 + c_ * cw + 0.6, y0 + r_ * ch + 0.6
            cv.rect(a, b, a + cw - 1.9, b + ch - 1.9, cols[ch_])
            if ch_ in 'rpk':
                disc(cv, a + cw / 2 - 0.6, b + ch / 2 - 0.6, min(cw, ch) * 0.32, I if ch_ in 'rk' else PAPER)
    cv.line(24, h - 9, 43, h - 9, GREY)
    return cv.image()

# ---------------------------------------------------------------- the shelf's print (118 x 60)
def pinned(w, h, ground):
    cv = Canvas(w, h)
    cv.rect(0, 0, w - 1, h - 1, PAPER); cv.rect(3, 3, w - 4, h - 4, ground)
    return cv
def pins(cv, w):
    for x in (2, w - 3): cv.dot(x, 2, OCH_L); cv.dot(x, 3, (168, 119, 83))

def print_glissandi():
    # the string glissandi of Metastaseis: lines sliding across one another, terracotta from
    # the left and slate from the right, over a pale blue; the title's band at the foot
    w, h = 118, 60
    cv = pinned(w, h, (206, 218, 224))
    for k in range(11):
        a, b = (6, 8 + k * 3.6), (w - 7, 44 - k * 3.6)
        m = lerp(a, b, 0.5)
        cv.line(a[0], a[1], m[0], m[1], TERRA_L if k % 2 else TERRA)
        cv.line(m[0], m[1], b[0], b[1], SLATE if k % 2 else INK)
    cv.rect(3, h - 12, w - 4, h - 4, (49, 57, 61))
    cv.line(8, h - 8, 34, h - 8, PAPER)
    pins(cv, w)
    return cv.image()

def print_psappha():
    # the rhythm of Psappha: its title, a red rule, and 27 of its first 36 pulses struck
    w, h = 118, 60
    cv = pinned(w, h, (239, 226, 194))
    text(cv, 7, 5, 'PSAPPHA', 11, INK)
    for y, ln in ((24, 26), (28, 20)): cv.line(8, y, 8 + ln, y, GREY)
    cv.line(8, 35, 40, 35, TERRA); cv.line(8, 36, 40, 36, TERRA)
    struck = '110111' '011011' '111010' '101111' '011101' '110110'
    for r_ in range(6):
        for c_ in range(6):
            x, y = 66 + c_ * 8, 9 + r_ * 7.6
            if struck[r_ * 6 + c_] == '1':
                disc(cv, x, y, 2.4, TERRA if c_ == 0 else INK)
    pins(cv, w)
    return cv.image()

# ---------------------------------------------------------------- the floor at the left (66 x 126)
def snake():
    # a snake plant in a tall slate pot: stiff swords banded in two greens, edged in yellow
    rnd = random.Random(5)
    cv = Canvas(66, 126)
    cv.rect(20, 122, 46, 125, TEAK_D); cv.line(20, 122, 46, 122, TEAK)
    def pot(x, y):
        if not 80 <= y < 122 or abs(x - 33) > 11: return None
        return SLATE_L if x < 26 else SLATE_D if x > 40 else SLATE
    cv.fill(pot, (21, 80, 45, 122))
    cv.line(22, 80, 44, 80, SLATE_D); cv.line(22, 81, 44, 81, SOIL)
    blades = [(-9, 38, 24, -14), (8, 30, 22, 12), (-3, 12, 30, -4), (4, 20, 28, 6), (-6, 28, 27, -9), (10, 44, 20, 16), (-12, 50, 18, -18), (1, 6, 32, 1)]
    for dx, top, half, lean in blades:
        bx, tx = 33 + dx * 0.5, 33 + dx + lean * 0.3
        L = 81 - top
        def fn(x, y, bx=bx, tx=tx, L=L, top=top, half=half):
            if not top <= y <= 81: return None
            u = (81 - y) / L
            cx = bx + (tx - bx) * u ** 1.4
            wd = (half / 6.0) * (1 - u) ** 0.55 + 0.4
            v = x - cx
            if abs(v) > wd: return None
            if abs(v) > wd - 0.9 and u < 0.92: return VAR
            band = math.sin(u * L / 2.6 + v * 0.9) > 0.35
            return (G_M if band else G_L) if v < 0 else (G_M if band else G_D)
        cv.fill(fn, (min(bx, tx) - 6, top, max(bx, tx) + 6, 82))
    return finish(cv)

def palm():
    # a kentia palm in a rattan basket: arching fronds of drooping leaflets
    rnd = random.Random(9)
    cv = Canvas(66, 126)
    fronds = [(-28, 52), (-24, 30), (-12, 14), (0, 8), (13, 16), (24, 32), (29, 54), (-6, 34), (8, 38)]
    for k, (dx, ty) in enumerate(sorted(fronds, key=lambda f: -abs(f[0]))):
        base, tip = (33, 92), (33 + dx, ty)
        ctrl = (33 + dx * 0.25, ty - 8 if abs(dx) < 20 else ty - 18)
        pts = bez(base, ctrl, tip, 30)
        stem = G_D
        cv.curve(pts, stem)
        for i in range(8, len(pts) - 1):
            (x0, y0), (x1, y1) = pts[i], pts[i + 1]
            tx_, ty_ = x1 - x0, y1 - y0; n = math.hypot(tx_, ty_) or 1; tx_, ty_ = tx_ / n, ty_ / n
            L = 7 * (1 - (i - 8) / (len(pts) - 8)) + 2.5
            for sd in (-1, 1):
                nx, ny = -ty_ * sd, tx_ * sd
                ex, ey = nx * 0.7 + 0, ny * 0.7 + 0.75
                m = math.hypot(ex, ey); ex, ey = ex / m, ey / m
                col = G_L if (sd < 0) == (dx >= 0) and i % 2 else G_M if i % 2 else G_D
                cv.line(x0, y0, x0 + ex * L, y0 + ey * L, col)
    def basket(x, y):
        if not 90 <= y < 124: return None
        hw = 13 - (y - 90) / 34 * 3
        if abs(x - 33) > hw: return None
        X, Y = int(x * K), int(y * K)
        weave = ((X // 2) + (Y // 2)) % 2 == 0
        c = (216, 189, 146) if weave else (186, 152, 108)
        if x > 33 + hw - 3: c = (168, 139, 104) if weave else (150, 118, 84)
        return c
    cv.fill(basket, (19, 90, 47, 124))
    cv.rect(19, 89, 47, 92, (168, 119, 83)); cv.line(19, 89, 47, 89, (216, 189, 146))
    cv.rect(23, 124, 43, 125, (150, 118, 84))
    return finish(cv)

# ---------------------------------------------------------------- the floor at the right (84 x 96)
def legs(cv, cx):
    for x in (cx - 12, cx + 12):
        cv.line(x - 2, 77, x - 4, 95, BRASS); cv.line(x + 2, 77, x - 2, 95, BRASS)
        cv.dot(x - 4, 95, BRASS_L)

def fern():
    # a Boston fern in an ochre pot on brass legs: fronds arch out and fall past the pot
    rnd = random.Random(14)
    cv = Canvas(84, 96)
    cx = 42
    legs(cv, cx)
    fr = []
    for k in range(16):
        side = -1 if k % 2 else 1
        reach = rnd.uniform(14, 38)
        rise = rnd.uniform(8, 28) * (1 - reach / 60)
        drop = rnd.uniform(4, 30) * reach / 38
        fr.append((side, reach, rise, drop))
    fr.sort(key=lambda f: f[2])
    for side, reach, rise, drop in fr:
        b = (cx + side * rnd.uniform(0, 6), 60)
        tip = (cx + side * reach, 60 - rise + drop)
        ctrl = (cx + side * reach * 0.45, 60 - rise - 14)
        pts = bez(b, ctrl, tip, 26)
        cv.curve(pts, G_D)
        for i in range(3, len(pts) - 1):
            (x0, y0), (x1, y1) = pts[i], pts[i + 1]
            tx_, ty_ = x1 - x0, y1 - y0; n = math.hypot(tx_, ty_) or 1; tx_, ty_ = tx_ / n, ty_ / n
            L = 3.4 * (1 - i / len(pts)) + 1.2
            for sd in (-1, 1):
                nx, ny = -ty_ * sd, tx_ * sd
                col = G_L if sd * side < 0 and i % 2 == 0 else G_M
                cv.line(x0, y0, x0 + (nx + tx_ * 0.5) * L, y0 + (ny + ty_ * 0.5) * L + 0.6, col)
    def pot(x, y):
        if not 58 <= y < 78: return None
        hw = 13 if y < 70 else 13 - (y - 70) * 0.9
        if abs(x - cx) > hw: return None
        return OCH_L if x < cx - hw + 4 else OCH_D if x > cx + hw - 4 else OCH
    cv.fill(pot, (cx - 14, 58, cx + 14, 78))
    cv.line(cx - 13, 58, cx + 13, 58, OCH_D)
    # the front fronds fall over the pot's rim
    for side in (-1, 1):
        pts = bez((cx + side * 3, 59), (cx + side * 12, 54), (cx + side * 17, 72), 16)
        cv.curve(pts, G_D)
        for i in range(2, len(pts) - 1, 1):
            x0, y0 = pts[i]
            for sd in (-1, 1): cv.line(x0, y0, x0 + sd * 2.2, y0 + 1.6, G_M if i % 2 else G_L)
    return finish(cv)

def rubber():
    # a rubber plant in a white pot: broad dark leaves on a reddish stem, a red sheath at its tip
    cv = Canvas(84, 96)
    cx = 42
    cv.rect(cx - 13, 93, cx + 13, 95, TEAK_D); cv.line(cx - 13, 93, cx + 13, 93, TEAK)
    stem = bez((cx, 66), (cx - 3, 36), (cx + 1, 6), 40)
    cv.curve(stem, (116, 62, 43), 2)
    DK, MD, LT = (40, 64, 54), (59, 92, 72), (96, 128, 96)
    def ovate(u, v): return abs(v) <= math.sin(math.pi * u ** 0.85) * (1.0 - 0.15 * u)
    spots = [(0.12, -1, 116), (0.2, 1, 64), (0.3, -1, 128), (0.38, 1, 52), (0.48, -1, 110), (0.56, 1, 60), (0.66, -1, 128), (0.74, 1, 50), (0.84, -1, 95), (0.9, 1, 40)]
    for t, sd, ang in spots:
        i = int(t * (len(stem) - 1)); x, y = stem[i]
        L = 24 - t * 9
        leaf(cv, x, y, L, L * 0.6, sd * ang, ovate, (DK, MD, LT) if t > 0.3 else (DK, DK, MD))
    x, y = stem[-1]
    cv.line(x, y, x + 0.6, y - 5, TERRA, 1); cv.dot(x + 0.6, y - 5, TERRA_L)
    def pot(x, y):
        if not 64 <= y < 93: return None
        hw = 12 if y < 90 else 12 - (y - 89)
        if abs(x - cx) > hw: return None
        return WHITE if x < cx - hw + 5 else WHITE_DD if x > cx + hw - 4 else WHITE_D if x > cx + 4 else WHITE
    cv.fill(pot, (cx - 13, 64, cx + 13, 93))
    cv.line(cx - 12, 64, cx + 12, 64, SOIL)
    return finish(cv)

# ---------------------------------------------------------------- the desk's plant (60 x 70, the desk at 49)
DESK = 49
def jade():
    # a jade plant in a celadon bowl: thick branching stems and fleshy leaves, red at their rims
    cv = Canvas(60, 70)
    cx = 30
    CEL, CEL_L, CEL_D = (160, 190, 164), (196, 216, 196), (118, 148, 126)
    TRUNK = (112, 98, 62)
    branches = [((cx, DESK - 8), (cx - 2, DESK - 20), (cx - 10, DESK - 32)), ((cx, DESK - 8), (cx + 3, DESK - 22), (cx + 12, DESK - 30)),
                ((cx - 1, DESK - 18), (cx - 1, DESK - 30), (cx + 1, DESK - 40)), ((cx - 6, DESK - 26), (cx - 14, DESK - 26), (cx - 19, DESK - 22)),
                ((cx + 8, DESK - 25), (cx + 16, DESK - 24), (cx + 20, DESK - 17))]
    tips = []
    for a, b, c in branches:
        pts = bez(a, b, c, 18)
        cv.curve(pts, TRUNK, 2 if a[1] > DESK - 12 else 1)
        tips += [pts[-1], pts[len(pts) * 2 // 3], pts[len(pts) // 3]]
    rnd = random.Random(3)
    def blob(u, v): return u * u * 0.0 + (2 * u - 1) ** 2 + v * v <= 1
    for x, y in tips:
        for k in range(3):
            ang = rnd.uniform(-160, 160)
            L = rnd.uniform(4.2, 5.4)
            leaf(cv, x, y, L, L * 0.75, ang, blob, ((90, 132, 84), (106, 150, 92), (146, 182, 112)))
    for x, y in tips:
        ang = rnd.uniform(-60, 60); a = math.radians(ang)
        cv.dot(x + math.sin(a) * 5, y - math.cos(a) * 5, TERRA_L)
    def bowl(x, y):
        if not DESK - 9 <= y < DESK: return None
        t = (y - DESK + 9) / 9; hw = 13 - t * t * 6
        if abs(x - cx) > hw: return None
        return CEL_L if x < cx - hw + 3 else CEL_D if x > cx + hw - 4 else CEL
    cv.fill(bowl, (cx - 14, DESK - 9, cx + 14, DESK))
    cv.line(cx - 12, DESK - 9, cx + 12, DESK - 9, SOIL)
    return finish(cv)

def cacti():
    # three cacti in a terracotta pot: a tall one with an arm, a round one, a small one in flower
    cv = Canvas(60, 70)
    cx = 30
    def ribbed(x0, x1, y0, y1, round_top=True):
        def fn(x, y):
            if not (x0 <= x <= x1 and y0 <= y <= y1): return None
            w = (x1 - x0) / 2; c = (x0 + x1) / 2
            if round_top and y < y0 + w and (x - c) ** 2 + (y - y0 - w) ** 2 > w * w: return None
            u = (x - x0) / (x1 - x0)
            rib = int(u * 5)
            return [G_L, G_M, G_L, G_M, G_D][min(4, rib)] if u < 0.8 else G_D
        cv.fill(fn, (x0, y0, x1, y1))
        for y in np.arange(y0 + 3, y1, 3.2):
            for x in (x0 + (x1 - x0) * 0.3, x0 + (x1 - x0) * 0.7): cv.dot(x, y, (224, 205, 176))
    ribbed(cx - 3, cx + 4, 8, DESK - 8)
    ribbed(cx + 4, cx + 13, 26, 29, round_top=False)
    ribbed(cx + 9, cx + 14, 17, 29)
    ribbed(cx - 11, cx - 7, 22, 30)
    cv.rect(cx - 9, 28, cx - 3, 30, G_M)
    disc(cv, cx - 9, DESK - 13, 4.6, G_M)
    cv.fill(lambda x, y: G_L if (x - cx + 10.5) ** 2 + (y - DESK + 14.5) ** 2 < 5 else None, (cx - 14, DESK - 18, cx - 6, DESK - 10))
    disc(cv, cx + 9, DESK - 12, 3.4, G_D); disc(cv, cx + 8.6, DESK - 12.4, 2.4, G_M)
    disc(cv, cx + 9, DESK - 16, 1.8, (232, 120, 120)); cv.dot(cx + 9, DESK - 16, OCH_L)
    def pot(x, y):
        if not DESK - 9 <= y < DESK: return None
        hw = 14 - (y - DESK + 9) / 9 * 3
        if abs(x - cx) > hw: return None
        return TERRA_L if x < cx - hw + 3 else TERRA_D if x > cx + hw - 3 else TERRA
    cv.fill(pot, (cx - 15, DESK - 9, cx + 15, DESK))
    cv.rect(cx - 15, DESK - 10, cx + 15, DESK - 8, TERRA); cv.line(cx - 15, DESK - 10, cx + 15, DESK - 10, TERRA_L)
    return finish(cv)

# ---------------------------------------------------------------- the lamp (42 x 64; its light at about (35, 20))
def dome():
    # a white dome lamp on a flared stem, the dome's underside lit
    cv = Canvas(42, 64)
    cx = 29
    def stem(x, y):
        if not 19 <= y < 64: return None
        t = (y - 19) / 45; hw = 1.3 + t ** 3.2 * 9
        if abs(x - cx) > hw: return None
        return WHITE if x < cx - hw * 0.3 else WHITE_D if x < cx + hw * 0.5 else WHITE_DD
    cv.fill(stem, (cx - 11, 19, cx + 11, 64))
    def shade(x, y):
        dx, dy = (x - cx) / 12.5, (y - 19) / 13
        if dy > 0.12 or dx * dx + dy * dy > 1: return None
        if dy > -0.02: return GLOW if abs(dx) < 0.85 else WHITE_D
        if dx < -0.35 and dy < -0.4: return PAPER
        return WHITE if dx < 0.4 else WHITE_D if dx < 0.75 else WHITE_DD
    cv.fill(shade, (cx - 13, 5, cx + 13, 21))
    cv.line(cx - 13, 63, cx + 13, 63, WHITE_DD)
    return finish(cv, out=False)

def angle():
    # a terracotta balanced-arm lamp: a heavy base, two arms on springs, a cone turned to the desk
    cv = Canvas(42, 64)
    cv.fill(lambda x, y: (TERRA_L if y < 59.5 else TERRA if y < 62 else TERRA_D) if 3 <= x < 18 and 58 <= y < 64 and not ((x < 4 or x > 17) and y < 59) else None, (3, 58, 18, 64))
    cv.rect(9, 55, 11, 57, INK)
    for (a, b) in (((10, 56), (19, 33)), ((19, 33), (28, 14))):
        cv.line(a[0], a[1], b[0], b[1], INK); cv.line(a[0] + 1.6, a[1] + 0.4, b[0] + 1.6, b[1] + 0.4, INK)
    for k in range(8):
        t = k / 8; x, y = lerp((12.6, 50), (18.6, 36), t)
        cv.dot(x + (1 if k % 2 else -0.4), y, (98, 96, 89))
    for x, y in ((19.6, 33), (28.6, 14)): cv.dot(x, y, BRASS_L); cv.dot(x + 1, y, BRASS)
    def shade(x, y):
        dx, dy = x - 31, y - 14
        a = math.radians(42); u = dx * math.cos(a) + dy * math.sin(a); v = -dx * math.sin(a) + dy * math.cos(a)
        if not (-2.5 < u < 9 and abs(v) < 2.6 + u * 0.55): return None
        if u > 7.5: return GLOW
        if v < -1.2 - u * 0.25: return TERRA_L
        if v > 1.4 + u * 0.4: return TERRA_D
        return TERRA
    cv.fill(shade, (24, 6, 42, 28))
    cv.dot(36.5, 21.5, PAPER)
    return finish(cv, out=False)

def ceramic():
    # an ochre ceramic lamp, its belly ringed with grooves, under a linen drum shade lit within
    cv = Canvas(42, 64)
    cx = 27
    def base(x, y):
        if not 40 <= y < 64: return None
        t = (y - 40) / 24
        hw = 2.2 + 8.8 * math.sin(math.pi * 0.5 * min(1, t / 0.7)) ** 1.6 if t < 0.7 else 11 - (t - 0.7) / 0.3 * 4
        if abs(x - cx) > hw: return None
        if y >= 62: return OCH_D
        groove = any(abs(y - g) < 0.5 for g in (51, 54.5, 58))
        if groove: return OCH_D
        return OCH_L if x < cx - hw * 0.45 else OCH_D if x > cx + hw * 0.6 else OCH
    cv.fill(base, (cx - 12, 37, cx + 12, 64))
    cv.line(cx, 23, cx, 41, BRASS); cv.dot(cx, 38, BRASS_L)
    def drum(x, y):
        if not 3 <= y < 24: return None
        t = (y - 3) / 21; x0, x1 = cx - 11 - t * 2.5, cx + 11 + t * 2.5
        if not x0 <= x <= x1: return None
        if y < 4.2: return (216, 189, 146)
        if y > 22.6: return (216, 189, 146)
        if x < x0 + 2.2: return (230, 214, 182)
        if x > x1 - 3: return (224, 205, 176)
        return (250, 236, 200) if y > 9 else (242, 228, 196)
    cv.fill(drum, (cx - 14, 3, cx + 14, 24))
    return finish(cv)

# ---------------------------------------------------------------- the mug (3.2 x 3 em: 19.2 x 18)
def mug_body(cv, body, lite, dark, handle=None, rim=None):
    handle = handle or body
    for y in (6, 13):
        pass
    cv.curve([(13.4, 6.4), (17.2, 6.6), (17.6, 10), (16.6, 13), (13.4, 13.6)], handle, 1.2)
    cv.rect(2, 3, 13.4, 17, body)
    cv.rect(2, 3, 3.6, 17, lite); cv.rect(11.8, 3, 13.4, 17, dark)
    cv.line(2, 3, 13.4, 3, rim or dark); cv.line(3, 4, 12.6, 4, SOIL)
    cv.line(3, 17, 12.6, 17, dark)

def mugs():
    out = {}
    def m(name, fn):
        cv = Canvas(19.2, 18); fn(cv); out[name] = finish(cv)
    def sage(cv):
        mug_body(cv, (125, 160, 130), (160, 190, 160), (92, 122, 100))
        cv.line(5, 6, 5, 14, (176, 204, 176))
    def striped(cv):
        mug_body(cv, CREAM, PAPER, (216, 189, 146), handle=CREAM)
        for y in (8, 9.2, 11.4): cv.line(2, y, 13.4, y, OCH)
        cv.line(2, 14.6, 13.4, 14.6, SLATE)
    def enamel(cv):
        mug_body(cv, PAPER, PAPER, (216, 209, 195), handle=BLUE_L, rim=BLUE_L)
        cv.rect(2, 15.4, 13.4, 17, BLUE_L)
        for x, y in ((5, 6), (9, 8), (6, 11), (10, 12.6), (7.6, 14), (4, 9)): cv.dot(x, y, GREY)
    def sieve(cv):
        mug_body(cv, CREAM, PAPER, (216, 189, 146), handle=CREAM)
        for x in np.arange(3.4, 13, 2.2): cv.dot(x, 7.4, TERRA if int(x) % 2 else GREY)
        for x in np.arange(4.4, 13, 2.2): cv.dot(x, 10, TERRA if int(x) % 3 else GREY)
        cv.line(2, 12.6, 13.4, 12.6, INK)
        for x in (4, 7.4, 10.6): cv.rect(x, 14.2, x + 0.9, 15.1, INK)
    def black(cv):
        mug_body(cv, (44, 42, 40), (79, 73, 67), INK, handle=(44, 42, 40))
        cv.line(2, 6.4, 13.4, 6.4, PAPER)
    def cup(cv):
        cv.curve([(14, 8.6), (17, 9), (16.4, 12.4), (13.4, 12.6)], WHITE_D, 1.2)
        def body(x, y):
            if not 7 <= y < 15.4: return None
            t = (y - 7) / 8.4; x0, x1 = 2.2 + t ** 2.4 * 3, 14.2 - t ** 2.4 * 3
            if not x0 <= x <= x1: return None
            if 8.6 <= y < 9.6 or 10.6 <= y < 11.4: return BLUE
            return PAPER if x < x0 + 1.8 else WHITE_DD if x > x1 - 1.8 else WHITE
        cv.fill(body, (2, 7, 15, 15.4))
        cv.line(3, 7, 13.4, 7, SOIL)
        cv.fill(lambda x, y: (WHITE if y < 16.4 else WHITE_DD) if ((x - 8.2) / 8.6) ** 2 + ((y - 16) / 1.4) ** 2 <= 1 else None, (-1, 14, 18, 18))
    for n, f in (('mug-sage', sage), ('mug-striped', striped), ('mug-enamel', enamel), ('mug-sieve', sieve), ('mug-black', black), ('mug-cup', cup)): m(n, f)
    return out

# ---------------------------------------------------------------- the wallpapers
def tile_from(fn, w, h, ground):
    a = np.zeros((h, w, 4), dtype=np.uint8); a[..., :3] = ground; a[..., 3] = 255
    def put(x, y, c): a[int(round(y)) % h, int(round(x)) % w, :3] = c
    fn(put)
    return Image.fromarray(a)

def tile_atomic():
    # sage, cream starbursts of eight rays with an ochre heart, ochre boomerangs, cream sparks
    G, CR, OC, MOSS = (72, 98, 66), (230, 220, 196), (201, 164, 90), (112, 128, 108)
    k = 0.7
    def draw(put):
        for cx, cy in ((15, 15), (45, 45)):
            for i in range(8):
                a = math.radians(22.5 + i * 45); L = 7 if i % 2 else 4.5
                for s in np.linspace(1.6, L, 8): put((cx + math.cos(a) * s) * k, (cy + math.sin(a) * s) * k, CR)
                put((cx + math.cos(a) * (L + 0.8)) * k, (cy + math.sin(a) * (L + 0.8)) * k, CR)
            put(cx * k, cy * k, OC); put(cx * k + 1, cy * k, OC)
        for cx, cy, r in ((45, 14, 20), (15, 44, -25)):
            a = math.radians(r)
            for t in np.linspace(-4.5, 4.5, 10):
                put((cx + t * math.cos(a)) * k, (cy + t * math.sin(a) - 1.4 * (1 - (t / 4.5) ** 2)) * k, OC)
        for cx, cy in ((30, 30), (0, 0)):
            for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)): put(cx * k + dx, cy * k + dy, CR)
        for cx, cy in ((30, 0), (0, 30)):
            for dx in (-1, 1): put(cx * k + dx, cy * k + 1, MOSS)
            put(cx * k, cy * k - 1, MOSS)
    return tile_from(draw, 42, 42, G)

def tile_trellis():
    # burnt umber, a diamond trellis in a paler brown, cream buds on stems, ochre at the crossings
    G, LN, CR, OC = (90, 54, 39), (138, 97, 80), (233, 220, 193), (201, 154, 46)
    k = 0.7
    def draw(put):
        for t in np.linspace(0, 1, 80):
            for (x0, y0, x1, y1) in ((0, 0, 40, 60), (40, 0, 0, 60)):
                put((x0 + (x1 - x0) * t) * k, (y0 + (y1 - y0) * t) * k, LN)
        for cx, cy in ((0, 0), (20, 30)):
            for dx, dy in ((0, -1), (1, 0), (0, 1), (-1, 0)): put(cx * k + dx, cy * k + dy, CR)
            put(cx * k, cy * k, OC)
        for cx, cy in ((20, 0), (0, 30)):
            for j in range(-2, 4):
                w = 1 if -1 <= j <= 2 else 0
                for dx in range(-w, w + 1): put(cx * k + dx, cy * k + j, CR)
            for j in (4, 5): put(cx * k, cy * k + j, CR)
            put(cx * k - 1, cy * k + 6, OC); put(cx * k + 1, cy * k + 6, OC)
        for cx, cy in ((10, 15), (30, 15), (10, 45), (30, 45)): put(cx * k, cy * k, OC)
    return tile_from(draw, 28, 42, G)

def tile_grass():
    # an ivory grasscloth: fibres in fine vertical stripes of straw and grey, slubs across them
    G = (230, 220, 203)
    rnd = random.Random(48)
    TONES = [(218, 206, 186), (212, 199, 174), (222, 204, 160), (204, 192, 170)]
    def draw(put):
        for x in range(34):
            if rnd.random() < 0.3:
                c = rnd.choice(TONES)
                for y in range(12):
                    if rnd.random() < 0.9: put(x, y, c)
        for k in range(10):
            y = rnd.randint(0, 11); x = rnd.randint(0, 33)
            for d in range(rnd.randint(2, 5)): put(x + d, y, (240, 233, 218))
        for y in range(12): put(22, y, (206, 200, 186))
    return tile_from(draw, 34, 12, G)

# ---------------------------------------------------------------- the light switch (9 x 14)
def switch(on):
    # a cream toggle plate, bevelled, its two screws, the lever up (on) or down (off) in its slot
    cv = Canvas(9, 14)
    plate = (236, 228, 212)
    cv.rect(0, 0, 8, 13, plate)
    cv.line(0, 0, 8, 0, PAPER); cv.line(0, 0, 0, 13, PAPER)
    cv.line(0, 13, 8, 13, WHITE_DD); cv.line(8, 0, 8, 13, WHITE_DD)
    cv.dot(4.3, 1.6, GREY); cv.dot(4.3, 12.2, GREY)
    cv.rect(3.1, 4.4, 5.6, 9.4, (79, 73, 67))
    if on: cv.rect(3.1, 3.2, 5.6, 6.6, PAPER); cv.line(3.1, 6.6, 5.6, 6.6, WHITE_DD)
    else: cv.rect(3.1, 7.4, 5.6, 10.6, WHITE_D); cv.line(3.1, 7.4, 5.6, 7.4, PAPER)
    return cv.image()

# ---------------------------------------------------------------- the card reader and line printer (130 x 62 px)
STEEL, STEEL_L, STEEL_D = (104, 116, 128), (150, 160, 170), (70, 80, 90)
GREENBAR = (205, 222, 200)
def reader():
    # a desk-side cabinet in blue-grey steel: at the left the reader, a deck in its hopper and
    # the read cards in its stacker, its keys; at the right the printer under its smoked lid,
    # fan-fold paper (green-bar) rising from the lid and folded in a pile at its foot
    w, h = 112.2, 53.5
    cv = Canvas(w, h)
    def body(x0, x1, y0, y1):
        cv.rect(x0, y0, x1, y1, STEEL)
        cv.line(x0, y0, x1, y0, STEEL_L); cv.line(x0, y0, x0, y1, STEEL_L)
        cv.line(x1, y0, x1, y1, STEEL_D)
    body(0, 50, 9, 50); body(52, 111, 6, 50)
    cv.rect(0, 50, 111, 53, SLATE_D)
    # the reader: hopper and stacker on its deck
    cv.rect(2, 9, 48, 11, STEEL_L)
    cv.rect(5, 1, 27, 9, (239, 226, 194))
    for y in np.arange(2, 9, 1.8): cv.line(5, y, 27, y, (216, 209, 195))
    cv.rect(4, 0.5, 5, 9, STEEL_D); cv.rect(27, 0.5, 28, 9, STEEL_D)
    cv.rect(33, 5, 45, 9, (239, 226, 194)); cv.line(33, 7, 45, 7, (216, 209, 195)); cv.rect(32, 4.5, 33, 9, STEEL_D)
    # its keys and lamps
    for i, c in enumerate(((126, 160, 98), (240, 196, 106), (251, 248, 240), (181, 70, 43))):
        cv.rect(5 + i * 6, 16, 9 + i * 6, 19, c); cv.line(5 + i * 6, 19, 9 + i * 6, 19, STEEL_D)
    cv.rect(5, 25, 45, 26, STEEL_D)                            # the read slot
    cv.rect(5, 32, 45, 47, (92, 104, 116)); cv.line(5, 32, 45, 32, STEEL_D)   # the door
    cv.rect(23, 38, 27, 39, STEEL_L)
    # the printer: its lid of smoked glass, the paper rising behind it
    cv.rect(58, 0, 104, 6, PAPER)
    for y in (1.5, 4): cv.line(58, y, 104, y, GREENBAR)
    cv.rect(55, 6, 108, 15, (49, 57, 61)); cv.line(57, 8, 70, 8, (98, 110, 122)); cv.line(55, 15, 108, 15, STEEL_D)
    cv.rect(58, 19, 76, 22, INK); cv.line(60, 20.5, 70, 20.5, (150, 152, 136))   # its plate
    for i, c in enumerate(((240, 196, 106), (126, 160, 98))): cv.rect(96 + i * 6, 19, 99 + i * 6, 22, c)
    cv.rect(58, 26, 105, 27, STEEL_D)                         # the paper's exit
    # the printout folded at its foot
    for k in range(5):
        y = 45 - k * 1.6
        cv.rect(62 + (k % 2), y, 102 + (k % 2), y + 1.2, PAPER if k % 2 else GREENBAR)
    return finish(cv)

# ---------------------------------------------------------------- the UPIC's tablet (66 x 80 px)
def upic():
    # Xenakis's UPIC: a large drawing tablet in a slate frame, a page on it drawn with arcs
    # and glissandi, its stylus on a coiled cord, leaning against the wall under the desk
    w, h = 56.95, 69
    cv = Canvas(w, h)
    cv.rect(0, 0, w - 1, h - 3, SLATE)
    cv.line(0, 0, w - 1, 0, SLATE_L); cv.line(0, 0, 0, h - 3, SLATE_L); cv.line(w - 1, 0, w - 1, h - 3, SLATE_D)
    cv.rect(0, h - 3, w - 1, h - 1, SLATE_D)
    x0, y0, x1, y1 = 4, 4, w - 5, h - 12
    cv.rect(x0, y0, x1, y1, (239, 226, 194))
    for x in np.arange(x0 + 6, x1, 6): cv.line(x, y0, x, y1, (224, 214, 190))
    for y in np.arange(y0 + 8, y1, 8): cv.line(x0, y, x1, y, (224, 214, 190))
    # what is drawn on it: an arborescence in ink, a glissando in terracotta
    cv.curve(bez((x0 + 2, y1 - 10), (x0 + 18, y1 - 30), (x1 - 4, y0 + 8)), INK)
    cv.curve(bez((x0 + 14, y1 - 22), (x0 + 24, y1 - 22), (x1 - 6, y1 - 18)), INK)
    cv.curve(bez((x0 + 22, y0 + 26), (x0 + 30, y0 + 14), (x1 - 2, y0 + 16)), INK)
    cv.curve(bez((x0 + 2, y0 + 6), (x0 + 22, y0 + 30), (x1 - 2, y1 - 4)), TERRA)
    # the stylus and its cord; the maker's plate
    cv.line(w - 9, h - 10, w - 4, h - 7, INK); cv.dot(w - 9, h - 10, (150, 152, 136))
    for k in range(6): cv.dot(w - 12 - k * 2.5, h - 8 + (k % 2), (79, 73, 67))
    cv.rect(6, h - 9, 18, h - 7, (150, 152, 136))
    from pix import selout
    return selout(cv.image())        # no orphan pass: it would eat the drawn lines' diagonals

# ---------------------------------------------------------------- the other magazines' covers (37 x 50, as Moiré's)
NEWSP, RED2 = (229, 224, 209), (240, 196, 106)     # Event's one ink, a yellow
def text_px(cv, x, y, s, c):
    # type in the site's own 10-pixel face, set at its true size so every pixel is the font's
    import glob, io
    from fontTools.ttLib import TTFont
    from PIL import ImageFont, ImageDraw
    t = TTFont(glob.glob(REPO + '/fonts/fusion-pixel-10px-proportional-jp/*.woff2')[0]); t.flavor = None
    b = io.BytesIO(); t.save(b); b.seek(0)
    f = ImageFont.truetype(b, 10)
    m = Image.new('L', (cv.W, cv.H), 0); d = ImageDraw.Draw(m); d.fontmode = '1'
    d.text((x, y), s, font=f, fill=255)
    cv.a[np.array(m) > 127] = c + (255,)
def cover_event():
    # Event: a newspaper's front page, EVENT across a black band, a grid of boxes of type under it
    w, h = 37, 50
    cv = Canvas(w, h)
    cv.rect(0, 0, w - 1, h - 1, NEWSP)
    cv.rect(0, 0, w - 1, 9, INK)
    text(cv, 2, -1, 'EVENT', 10, NEWSP)
    cv.rect(0, 10, w - 1, 11, RED2)
    for x0, x1 in ((2, 16), (19, 34)):
        for y in range(14, 46, 3): cv.line(x0, y, x1 - (y * 7) % 5, y, (98, 96, 89))
    cv.rect(19, 14, 34, 24, INK); cv.rect(2, 34, 16, 40, RED2)
    return cv.image()

def cover_gesso():
    # Gesso: its title small on white over one painting, squares of colour placed by chance
    rnd = random.Random(1953)
    w, h = 37, 50
    cv = Canvas(w, h)
    cv.rect(0, 0, w - 1, h - 1, (247, 242, 232))
    text_px(cv, 3, -1, 'GESSO', INK)
    cols = [(242, 194, 48), (226, 102, 44), (59, 127, 182), (184, 40, 60), (70, 132, 92), INK, (247, 242, 232)]
    for gy in range(6):
        for gx in range(5):
            x, y = 3 + gx * 6.2, 12.4 + gy * 6.0
            cv.rect(x, y, x + 5.6, y + 5.4, rnd.choice(cols))
    return cv.image()

def cover_cons():
    # Cons: a botanical journal's cover, its title in a deep green over a fern frond on cream
    w, h = 37, 50
    DEEP, MID, LITE, CRM = (47, 93, 42), (79, 138, 58), (140, 186, 96), (246, 241, 226)
    cv = Canvas(w, h)
    cv.rect(0, 0, w - 1, h - 1, CRM)
    text_px(cv, 4, -1, 'CONS', DEEP)
    cv.rect(2, 10, w - 3, 10.6, MID)
    # the frond: Barnsley's fern, as on the issue's own cover, small
    from mag_plates3 import barnsley
    c = barnsley(w, h - 13, 30000, 3.4, w // 2, h - 14, 1988)
    top = np.percentile(c[c > 0], 85)
    for y in range(c.shape[0]):
        for x in range(w):
            if c[y, x] > 0:
                v = c[y, x] / top
                cv.a[y + 12, x] = (DEEP if v > 0.9 else MID if v > 0.35 else LITE) + (255,)
    return cv.image()

def cover_silver():
    # Silver: its title in white on black over one photograph, a landscape in greys under a pale sky
    w, h = 37, 50
    cv = Canvas(w, h)
    cv.rect(0, 0, w - 1, h - 1, (14, 14, 14))
    text_px(cv, 2, -1, 'SILVER', (240, 240, 236))
    cv.rect(2, 11, w - 3, 46, (196, 196, 192))
    cv.fill(lambda x, y: (120, 120, 118) if y > 24 - 7 * math.sin(x / 6) - x * 0.1 else None, (2, 14, w - 3, 34))
    cv.fill(lambda x, y: (60, 60, 60) if y > 32 - 3 * math.sin(x / 3) else None, (2, 24, w - 3, 46))
    cv.rect(2, 40, w - 3, 46, (34, 34, 34))
    return cv.image()

def back_issues():
    # the back issues behind the one in front: a newspaper's edge and a painting's, peeking past it
    w, h = 45.7, 54.3        # 53 x 63 art pixels, the ledge's box
    cv = Canvas(w, h)
    cv.rect(9, 0, 44.5, 52, NEWSP); cv.rect(9, 0, 44.5, 3, INK); cv.rect(40, 4, 44.5, 52, (210, 204, 188))
    cv.rect(2, 2.4, 38, 53, (247, 242, 232))
    for k, c in enumerate(((242, 194, 48), (59, 127, 182), (184, 40, 60), (70, 132, 92))): cv.rect(34, 6 + k * 10, 38, 15 + k * 10, c)
    cv.rect(2, 2.4, 30, 3.4, INK)
    cv.rect(39, 1, 41, 52, (246, 241, 226)); cv.rect(39, 1, 41, 2, (79, 138, 58))          # Cons, and Silver behind it
    cv.rect(42, 0.4, 44.5, 52, (14, 14, 14)); cv.rect(42, 8, 44.5, 20, (196, 196, 192))
    return finish(cv)
