# v25's second wall: round the corner from the desk, the reading corner. A bookcase of five
# shelves (its books drawn in the backdrop, but for the ones that can be taken down), a
# metronome on its second shelf, a pocket game console on its third, a 35 mm camera on top, a photo album on its bottom shelf, a chair to change (four) under a cat clock, a record player on a side table, and a planted fish tank on
# a teak cabinet under a print. Drawn directly in art pixels (no smoothing), in the same
# colours as the first wall, then lit by its own light (the ambient of the hour, the tank's
# glow, its top and far end falling away) and quantized into the room's one palette by build4.
# Every place is in the wall's own pixels (0..639); the page sets it 640 to the right.
import os as _os; UTIL = _os.path.normpath(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..')); REPO = _os.path.dirname(UTIL)
import sys, os, math, random, glob, io
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/../v23')
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from light import smooth
from room import W, H, drop

INK = (30, 29, 27)
TEAK, TEAK_L, TEAK_D, TEAK_DD = (168, 119, 83), (196, 150, 108), (128, 84, 56), (92, 58, 40)
WAL, WAL_D = (78, 55, 39), (52, 37, 28)
BACK = (58, 42, 32)
OAK = (200, 169, 126)
CREAM, PAPER = (239, 226, 194), (251, 248, 240)
SLATE, SLATE_D, SLATE_L = (73, 85, 90), (49, 57, 61), (104, 118, 122)
BLUE, BLUE_L, NAVY = (43, 69, 96), (74, 104, 134), (30, 42, 58)
TERRA, TERRA_L, TERRA_D = (181, 70, 43), (220, 110, 80), (116, 62, 43)
OCH, OCH_L = (201, 154, 46), (240, 196, 106)
SAGE, GREEN, GREEN_D, GREEN_L = (125, 138, 120), (90, 122, 70), (59, 106, 85), (126, 160, 98)
OX = (128, 44, 40)
GREY, GREY_L = (134, 123, 104), (216, 209, 195)
WATER, WATER_L, WATER_D = (92, 170, 168), (140, 206, 196), (46, 112, 122)
GRAVEL = [(150, 128, 98), (118, 100, 80), (190, 170, 136), (86, 76, 64)]
NEON_B, NEON_R, SILVER = (60, 170, 230), (210, 50, 52), (220, 226, 224)
FLOOR_TOP = 309

class C:
    """a picture drawn straight in pixels"""
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.im = Image.new('RGBA', (w, h), (0, 0, 0, 0)); self.d = ImageDraw.Draw(self.im)
    def rect(self, x0, y0, x1, y1, c): self.d.rectangle([x0, y0, x1, y1], fill=tuple(c) + (255,))
    def line(self, pts, c, w=1): self.d.line([tuple(p) for p in pts], fill=tuple(c) + (255,), width=w)
    def poly(self, pts, c): self.d.polygon([tuple(p) for p in pts], fill=tuple(c) + (255,))
    def ell(self, x0, y0, x1, y1, c): self.d.ellipse([x0, y0, x1, y1], fill=tuple(c) + (255,))
    def px(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h: self.im.putpixel((int(x), int(y)), tuple(c) + (255,))
    def clear(self, x0, y0, x1, y1): self.d.rectangle([x0, y0, x1, y1], fill=(0, 0, 0, 0))

def font():
    from fontTools.ttLib import TTFont
    t = TTFont(glob.glob(REPO + '/fonts/fusion-pixel-10px-proportional-jp/*.woff2')[0]); t.flavor = None
    b = io.BytesIO(); t.save(b); b.seek(0)
    return ImageFont.truetype(b, 10)
def text(cv, x, y, s, c):
    m = Image.new('L', (cv.w, cv.h), 0); d = ImageDraw.Draw(m); d.fontmode = '1'
    d.text((x, y), s, font=font(), fill=255)
    a = np.array(cv.im); a[np.array(m) > 127] = tuple(c) + (255,); cv.im = Image.fromarray(a); cv.d = ImageDraw.Draw(cv.im)

# ---------------------------------------------------------------- where things are
CASE = (36, 40, 235, 308)                 # the bookcase: left, top, right, bottom
BOARDS = [93, 144, 195, 246]              # the tops of its four shelves (4 px thick)
COMPS = [(46, 92), (97, 143), (148, 194), (199, 245), (250, 297)]   # its five compartments, top and bottom rows
INNER = (42, 229)
# the books that can be taken down: name, compartment, left, width, height
BOOKS = [('book-xenakis', 0, 92, 11, 41), ('book-hiller', 0, 152, 10, 43), ('book-cage', 1, 70, 9, 37),
         ('book-mccracken', 2, 120, 10, 39), ('book-knuth', 2, 178, 13, 42), ('book-reichardt', 3, 150, 31, 40)]
METRONOME = (186, 1, 21, 33)             # left, compartment, width, height
HANDHELD = (210, 149, 17, 26)
ALBUM = (193, 252, 17, 46)                # the photo album, on end on the bottom shelf: left, top, width, height
SIDE_TABLE = (375, 262, 31)               # the side table by the chair: left, top, width
PLAYER = (376, 230, 29, 32)                # the record player on it: left, top, width, height
CAMERA = (110, 13, 40, 27)               # the 35 mm camera, on the bookcase's top: left, top, width, height            # the pocket game, on the books lying flat: left, top, width, height
CAT = (296, 64, 42, 114)                   # the cat clock: left, top, width, height
CAT_FACE = (8, 47, 25)                     # its face's box in the cat: left, top, size
CHAIR_BOX = (262, 200, 111, 109)           # every chair's box: left, top, width, height
CABINET = (408, 228, 611, 308)
TANK = (418, 134, 184, 94)                # left, top, width, height
PRINT = (448, 30, 128, 86)                # the print over the tank: left, top, width, height
TANK_GLOW = (510, 180)

def book_box(name):
    for n, ci, x, w, h in BOOKS:
        if n == name: return x, COMPS[ci][1] - h + 1, w, h

# ---------------------------------------------------------------- the light
def light2(amb):
    """the reading corner's light: the hour's ambient, the tank's cool glow, and the corners
    (the top and the far end) falling away to the room's edge; at its left it runs straight
    on from the first wall, lit there as that is"""
    edge = amb * 0.8
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    L = np.zeros((H, W, 3), dtype=np.float32) + amb
    dx, dy = xx - TANK_GLOW[0], (yy - TANK_GLOW[1]) * 1.25
    d = np.hypot(dx, dy)
    L += (0.5 / (1 + (d / 64) ** 2))[..., None] * np.array([0.42, 0.78, 0.82])
    # the hood's lamp, straight down into the water and out over the cabinet's top
    inside = (xx >= TANK[0] + 2) & (xx < TANK[0] + TANK[2] - 2) & (yy >= TANK[1] + 9) & (yy < TANK[1] + TANK[3] - 8)
    L += (inside * 0.28 * smooth((TANK[1] + 70 - yy) / 60))[..., None] * np.array([0.8, 0.95, 0.9])
    de = np.minimum(W - 1 - xx, yy)
    t = smooth(de / 110)[..., None]
    return edge + (L - edge) * t

# ---------------------------------------------------------------- the backdrop
def wall2(tile, first):
    """the wall: the paper run on from the first wall (its tile in phase at column 640), the
    floor's boards in step with its, so the two walls are one"""
    a = np.zeros((H, W, 4), dtype=np.uint8)
    t = np.array(tile.convert('RGBA'))
    off = 640 % t.shape[1]
    for y in range(H):
        row = np.tile(t[y % t.shape[0]], (W // t.shape[1] + 2, 1))
        a[y] = row[off:off + W]
    yy, xx = np.mgrid[0:H, 0:W]
    m = (yy > H * 0.8) & ((xx + yy) % 2 == 0)
    a[m, :3] = (a[m, :3] * 0.82).astype(np.uint8)
    f = np.array(first.convert('RGBA'))
    for x in range(W):
        a[FLOOR_TOP:, x] = f[FLOOR_TOP:, 77 + (x + 640) % 77]
    return Image.fromarray(a)

def spine(cv, x, y1, w, h, c, rnd, band=None, label=None):
    """a book standing on a shelf: its cloth, a lit left edge, a shadowed right, the bands and
    the lettering of its spine"""
    y0 = y1 - h + 1
    cv.rect(x, y0, x + w - 1, y1, c)
    lite = tuple(min(255, int(v * 1.18 + 8)) for v in c); dark = tuple(int(v * 0.66) for v in c)
    cv.rect(x, y0, x, y1, lite)
    if w > 3: cv.rect(x + w - 1, y0, x + w - 1, y1, dark)
    cv.rect(x, y0, x + w - 1, y0, lite)
    if band:
        for by in (y0 + 3, y1 - 4):
            cv.rect(x + 1, by, x + w - 2, by + (1 if w > 6 else 0), band)
    if label and w >= 5:
        ly = y0 + int(h * 0.25)
        for k in range(int(h * 0.42)):
            if rnd.random() < 0.72: cv.px(x + w // 2, ly + k, label)

CLOTH = [TERRA, TERRA_D, BLUE, NAVY, OCH, CREAM, SLATE, SAGE, INK, OX, GREEN, GREY_L, (154, 97, 54), BLUE_L, (98, 96, 89)]
def bookcase(cv, rnd):
    x0, y0, x1, y1 = CASE
    # the carcass: teak sides, top and plinth, the back in shadow
    cv.rect(INNER[0], y0 + 6, INNER[1], y1 - 10, BACK)
    cv.rect(x0, y0, x1, y0 + 5, TEAK); cv.rect(x0, y0, x1, y0, TEAK_L); cv.rect(x0, y0 + 5, x1, y0 + 5, TEAK_D)
    for sx in (x0, x1 - 5):
        cv.rect(sx, y0 + 6, sx + 5, y1 - 2, TEAK); cv.rect(sx, y0 + 6, sx, y1 - 2, TEAK_L); cv.rect(sx + 5, y0 + 6, sx + 5, y1 - 2, TEAK_D)
    cv.rect(x0 + 6, y1 - 9, x1 - 6, y1 - 2, TEAK_DD); cv.rect(x0 + 6, y1 - 9, x1 - 6, y1 - 9, TEAK_D)
    cv.rect(x0 + 1, y1 - 1, x0 + 4, y1, INK); cv.rect(x1 - 4, y1 - 1, x1 - 1, y1, INK)
    for b in BOARDS:
        cv.rect(INNER[0], b, INNER[1], b + 3, TEAK); cv.rect(INNER[0], b, INNER[1], b, TEAK_L); cv.rect(INNER[0], b + 3, INNER[1], b + 3, TEAK_D)
    # under each board, its shadow on the back
    for top, bot in COMPS:
        cv.rect(INNER[0], top, INNER[1], top + 2, (40, 29, 23))
        cv.rect(INNER[0], top, INNER[0] + 1, bot, (44, 32, 25))
    # the books, compartment by compartment, around what stands on its own
    keep = {}
    for n, ci, x, w, h in BOOKS: keep.setdefault(ci, []).append((x - 1, x + w))
    keep.setdefault(METRONOME[1], []).append((METRONOME[0] - 2, METRONOME[0] + METRONOME[2] + 1))
    keep.setdefault(4, []).append((150, 228))          # the records and the vase
    keep.setdefault(2, []).append((206, 228))          # a stack lying flat
    keep.setdefault(3, []).append((44, 60))            # a bookend and a pot
    for ci, (top, bot) in enumerate(COMPS):
        x = INNER[0] + 2
        while x < INNER[1] - 2:
            hit = [k for k in keep.get(ci, []) if k[0] <= x + 9 and x <= k[1]]
            if hit: x = max(k[1] for k in hit) + 1; continue
            w = rnd.choice([4, 5, 5, 6, 6, 7, 8, 9])
            if x + w > INNER[1] - 1: break
            if any(k[0] <= x + w and x <= k[1] for k in keep.get(ci, [])): x += 1; continue
            h = rnd.randint(28, bot - top - 4)
            c = rnd.choice(CLOTH)
            band = rnd.choice([None, OCH_L, CREAM, INK]) if rnd.random() < 0.6 else None
            label = CREAM if sum(c) < 360 else INK
            spine(cv, x, bot, w, h, c, rnd, band if band != c else None, label if rnd.random() < 0.7 else None)
            x += w + (1 if rnd.random() < 0.18 else 0)
    # compartment 2's right end: books lying flat
    top, bot = COMPS[2]
    y = bot
    for k, (w, c) in enumerate(((22, NAVY), (20, CREAM), (21, TERRA), (18, SLATE))):
        x = 207 + (k % 2)
        cv.rect(x, y - 4, x + w - 1, y, c); cv.rect(x, y - 4, x + w - 1, y - 4, tuple(min(255, int(v * 1.2)) for v in c))
        cv.rect(x + w - 1, y - 4, x + w - 1, y, tuple(int(v * 0.65) for v in c))
        y -= 5
    # compartment 3's left: a bookend and a small cactus in a pot
    top, bot = COMPS[3]
    cv.rect(46, bot - 22, 47, bot, INK); cv.rect(46, bot, 58, bot, INK)
    cv.rect(50, bot - 9, 57, bot - 1, TERRA); cv.rect(49, bot - 10, 58, bot - 9, TERRA_L); cv.rect(57, bot - 9, 57, bot - 1, TERRA_D)
    cv.rect(52, bot - 22, 55, bot - 11, GREEN); cv.rect(52, bot - 22, 52, bot - 11, GREEN_L); cv.rect(55, bot - 20, 55, bot - 11, GREEN_D)
    cv.rect(50, bot - 18, 51, bot - 14, GREEN); cv.rect(50, bot - 20, 50, bot - 18, GREEN)
    cv.px(53, bot - 23, (230, 140, 160)); cv.px(54, bot - 23, (230, 140, 160))
    # compartment 4: records on end (thin sleeves), and a celadon vase of dried grass
    top, bot = COMPS[4]
    for k in range(13):
        x = 152 + k * 3
        c = rnd.choice([INK, CREAM, TERRA, OCH, SLATE, (98, 96, 89), BLUE, GREY_L])
        hh = rnd.randint(40, 44)
        cv.rect(x, bot - hh + 1, x + 1, bot, c); cv.rect(x + 2, bot - hh + 1, x + 2, bot, (int(c[0] * .6), int(c[1] * .6), int(c[2] * .6)))
    vx = 213
    cv.rect(vx, bot - 16, vx + 10, bot, (150, 176, 156)); cv.rect(vx + 1, bot - 18, vx + 9, bot - 16, (170, 196, 176))
    cv.rect(vx + 9, bot - 16, vx + 10, bot, (110, 136, 118)); cv.rect(vx + 3, bot - 20, vx + 7, bot - 18, (150, 176, 156))
    for k, (dx, ht, lean) in enumerate(((1, 26, -4), (3, 32, -1), (5, 30, 2), (7, 24, 5))):
        bx = vx + 2 + dx
        cv.line([(bx, bot - 20), (bx + lean, bot - 20 - ht)], (205, 180, 128))
        cv.px(bx + lean, bot - 21 - ht, (232, 208, 160)); cv.px(bx + lean - 1, bot - 19 - ht, (232, 208, 160))
    # on top of the case: a trailing plant in a white pot, and two boxes
    tx = 70
    cv.rect(tx, y0 - 13, tx + 15, y0 - 1, PAPER); cv.rect(tx + 12, y0 - 13, tx + 15, y0 - 1, GREY_L); cv.rect(tx - 1, y0 - 14, tx + 16, y0 - 13, PAPER)
    vines = [[(tx + 2, y0 - 12), (tx - 6, y0 - 4), (tx - 10, y0 + 14), (tx - 9, y0 + 30)], [(tx + 13, y0 - 12), (tx + 22, y0 - 2), (tx + 25, y0 + 16)],
             [(tx + 6, y0 - 14), (tx + 3, y0 - 22), (tx + 8, y0 - 26)], [(tx + 10, y0 - 14), (tx + 16, y0 - 20)]]
    for v in vines:
        cv.line(v, GREEN_D)
        for (ax, ay), (bx, by) in zip(v, v[1:]):
            for t in (0.2, 0.55, 0.9):
                lx, ly = ax + (bx - ax) * t, ay + (by - ay) * t
                s = 1 if rnd.random() < 0.5 else -1
                cv.rect(lx, ly, lx + 2, ly + 1, GREEN_L if s > 0 else GREEN); cv.px(lx + 1 - s, ly + 2, GREEN_D)
    for bx, bw, bh, c in ((160, 46, 12, (154, 97, 54)), (166, 36, 9, CREAM)):
        yb = y0 - 1 if bh == 12 else y0 - 13
        cv.rect(bx, yb - bh + 1, bx + bw, yb, c); cv.rect(bx, yb - bh + 1, bx + bw, yb - bh + 1, tuple(min(255, int(v * 1.15)) for v in c))
        cv.rect(bx + bw, yb - bh + 1, bx + bw, yb, tuple(int(v * 0.7) for v in c))
    cv.rect(178, y0 - 7, 188, y0 - 5, CREAM)

def chair(cv):
    # a teak lounge chair, straight on: a low seat on splayed legs, a teak frame round a slate
    # back cushion buttoned twice, arms on posts, a terracotta throw over its left arm and a
    # book left open on the seat
    l, r = CHAIR_BOX[0], CHAIR_BOX[0] + CHAIR_BOX[2] - 1; cx = (l + r) // 2
    seat_y = 268
    def soft(x0, y0, x1, y1, c, lite, dark):
        cv.rect(x0 + 1, y0, x1 - 1, y1, c); cv.rect(x0, y0 + 1, x1, y1 - 1, c)
        cv.rect(x0 + 1, y0, x1 - 1, y0, lite); cv.rect(x0, y0 + 1, x0, y1 - 1, lite)
        cv.rect(x0 + 1, y1, x1 - 1, y1, dark); cv.rect(x1, y0 + 1, x1, y1 - 1, dark)
    # the legs, splaying out to the floor
    for lx, d in ((l + 12, -1), (r - 14, 1)):
        n = FLOOR_TOP - seat_y - 8
        for k in range(n):
            x = lx + d * (k * 5 // n)
            cv.rect(x, seat_y + 8 + k, x + 2, seat_y + 8 + k, TEAK)
            cv.px(x + (2 if d > 0 else 0), seat_y + 8 + k, TEAK_D)
    # the frame: a rail under the seat, two uprights leaning back behind the cushion
    cv.rect(l + 10, seat_y + 5, r - 10, seat_y + 8, TEAK); cv.rect(l + 10, seat_y + 8, r - 10, seat_y + 8, TEAK_D)
    for ux in (l + 17, r - 20):
        cv.rect(ux, 214, ux + 3, seat_y, TEAK); cv.rect(ux + 3, 214, ux + 3, seat_y, TEAK_D); cv.rect(ux, 214, ux + 3, 214, TEAK_L)
    # the back cushion, its seam and two buttons a row
    soft(l + 20, 216, r - 20, seat_y - 3, SLATE, SLATE_L, SLATE_D)
    cv.rect(l + 22, 238, r - 22, 238, SLATE_D)
    for bx in (cx - 12, cx + 11):
        for by in (227, 250): cv.rect(bx, by, bx + 1, by, SLATE_D); cv.px(bx, by - 1, SLATE_L)
    # the seat cushion, deep and soft at its front edge
    soft(l + 12, seat_y - 6, r - 12, seat_y + 5, SLATE, SLATE_L, SLATE_D)
    cv.rect(l + 13, seat_y + 1, r - 13, seat_y + 1, (64, 75, 80))
    # the arms on their posts
    for ax, side in ((l + 2, 0), (r - 20, 1)):
        cv.rect(ax, 244, ax + 18, 247, TEAK); cv.rect(ax, 244, ax + 18, 244, TEAK_L); cv.rect(ax, 247, ax + 18, 247, TEAK_D)
        cv.rect(ax, 244, ax, 247, TEAK_L if side == 0 else TEAK); cv.rect(ax + 18, 244, ax + 18, 247, TEAK_D)
        px_ = ax + (6 if side == 0 else 11)
        cv.rect(px_, 248, px_ + 2, seat_y + 5, TEAK); cv.rect(px_ + 2, 248, px_ + 2, seat_y + 5, TEAK_D)
    # the throw over the left arm
    tl = l + 1
    cv.rect(tl, 242, tl + 15, 248, TERRA); cv.rect(tl, 242, tl + 15, 242, TERRA_L)
    cv.rect(tl, 249, tl + 7, 280, TERRA); cv.rect(tl + 7, 249, tl + 7, 280, TERRA_D); cv.rect(tl, 249, tl, 280, TERRA_L)
    for y in (254, 262, 270): cv.rect(tl + 1, y, tl + 6, y, OCH_L)
    for k in range(4): cv.px(tl + 1 + k * 2, 281, TERRA)
    # the open book, face down on the seat
    bx = cx + 4
    cv.poly([(bx, seat_y - 6), (bx + 9, seat_y - 11), (bx + 18, seat_y - 6)], CREAM)
    cv.line([(bx, seat_y - 6), (bx + 9, seat_y - 11), (bx + 18, seat_y - 6)], (154, 97, 54))
    cv.line([(bx + 9, seat_y - 11), (bx + 9, seat_y - 7)], TEAK_DD)

def chair_butterfly(cv):
    # a butterfly chair: a sling of tan leather hung by its four corners from a frame of black
    # iron rod, two loops crossing; its top corners stand up like ears
    TAN, TAN_L, TAN_D = (176, 120, 72), (206, 154, 100), (128, 82, 48)
    # the frame behind: the back legs
    for x0, x1 in ((300, 292), (334, 342)): cv.line([(x0, 236), (x1, FLOOR_TOP - 1)], INK)
    cv.poly([(268, 210), (366, 210), (354, 262), (317, 278), (280, 262)], TAN)
    cv.poly([(268, 210), (280, 210), (286, 232), (280, 262)], TAN_L)
    cv.poly([(354, 210), (366, 210), (354, 262), (348, 232)], TAN_D)
    cv.line([(286, 236), (317, 262), (348, 236)], TAN_D)
    cv.line([(296, 250), (317, 270), (338, 250)], TAN_D)
    cv.line([(280, 262), (317, 278), (354, 262)], (98, 62, 36))
    for x, y in ((269, 210), (365, 210)): cv.rect(x - 1, y - 2, x + 1, y, INK)
    # the frame in front: from each top corner down through the front corners to the floor
    for side in (-1, 1):
        tx = 317 + side * 49; fx = 317 + side * 37; lx = 317 + side * 46
        cv.line([(tx, 210), (fx, 262), (lx, FLOOR_TOP - 1)], INK, 2)
    cv.line([(280, 262), (354, 262)], INK)

def chair_wire(cv):
    # a diamond chair of welded steel wire: a wide shell of lattice, a red pad in it, on a
    # cradle of chrome rods
    CHROME, CHROME_D = (196, 200, 198), (120, 124, 124)
    l, r, top, seat = 266, 368, 212, 268
    def inside(x, y):
        if y < top or y > seat: return False
        t = (y - top) / (seat - top)
        hw = 51 - 34 * t ** 1.4
        return abs(x - 317) <= hw
    for y in range(top, seat + 1):
        for x in range(l, r + 1):
            if not inside(x, y): continue
            edge = not inside(x - 1, y) or not inside(x + 1, y) or y in (top, seat)
            if edge: cv.px(x, y, CHROME_D if x > 317 else CHROME)
            elif (x + y) % 4 == 0 or (x - y) % 4 == 0: cv.px(x, y, CHROME_D if (x - y) % 4 == 0 else CHROME)
    # the pad, wider at its back than its seat
    cv.poly([(292, 228), (342, 228), (336, 266), (298, 266)], TERRA)
    cv.line([(292, 228), (342, 228)], TERRA_L); cv.line([(342, 229), (336, 266)], TERRA_D)
    cv.line([(296, 250), (338, 250)], TERRA_D)
    # the cradle: two rods down to splayed feet, a rail between
    for x0, x1 in ((304, 284), (330, 350)): cv.line([(x0, seat + 1), (x1, FLOOR_TOP - 1)], CHROME_D)
    cv.line([(290, 296), (344, 296)], CHROME_D)
    cv.rect(282, FLOOR_TOP - 1, 286, FLOOR_TOP - 1, INK); cv.rect(348, FLOOR_TOP - 1, 352, FLOOR_TOP - 1, INK)

def chair_tub(cv):
    # a low tub chair in mustard bouclé: its back and arms one rounded wall, a deep seat
    # cushion, the nubbled weave in a dither, short tapered teak legs
    MU, MU_L, MU_D = (196, 150, 52), (226, 186, 90), (150, 108, 34)
    def rr(x0, y0, x1, y1, rad, c):
        cv.d.rounded_rectangle([x0, y0, x1, y1], radius=rad, fill=tuple(c) + (255,))
    rr(268, 226, 366, 290, 22, MU_D)
    rr(270, 228, 364, 288, 20, MU)
    rr(286, 238, 348, 262, 6, MU_D)                 # the inside of the back, in shadow
    rr(280, 258, 354, 286, 6, MU_L)                 # the seat cushion
    cv.rect(282, 284, 352, 286, MU)
    a = np.array(cv.im)
    for y in range(226, 291):
        for x in range(268, 367):
            if a[y, x, 3] and (x * 3 + y * 5) % 7 == 0:
                c = a[y, x, :3].astype(int)
                a[y, x, :3] = np.clip(c + (18 if (x + y) % 2 else -22), 0, 255)
    cv.im = Image.fromarray(a); cv.d = ImageDraw.Draw(cv.im)
    for lx, d in ((282, -1), (348, 1)):
        for k in range(FLOOR_TOP - 290):
            x = lx + d * (k // 6)
            cv.rect(x, 290 + k, x + (2 if k < 9 else 1), 290 + k, TEAK if k % 6 else TEAK_D)

CHAIRS = {'chair-lounge': chair, 'chair-butterfly': chair_butterfly, 'chair-wire': chair_wire, 'chair-tub': chair_tub}
def chair_pic(fn):
    cv = C(W, H); fn(cv)
    x, y, w, h = CHAIR_BOX
    return cv.im.crop((x, y, x + w, y + h))

def side_table(cv):
    # a small teak side table between the chair and the cabinet: a round-edged top, a shelf
    # under it, three splayed legs (two seen)
    x0, y0, w = SIDE_TABLE; x1 = x0 + w - 1
    cv.rect(x0, y0, x1, y0 + 2, TEAK); cv.rect(x0, y0, x1, y0, TEAK_L); cv.rect(x0, y0 + 2, x1, y0 + 2, TEAK_D)
    cv.rect(x0 + 4, y0 + 24, x1 - 4, y0 + 25, TEAK); cv.rect(x0 + 4, y0 + 25, x1 - 4, y0 + 25, TEAK_D)
    n = FLOOR_TOP - y0 - 3
    for lx, d in ((x0 + 3, -1), (x1 - 4, 1)):
        for k in range(n):
            x = lx + d * (k * 3 // n)
            cv.rect(x, y0 + 3 + k, x + 1, y0 + 3 + k, TEAK); cv.px(x + (1 if d > 0 else 0), y0 + 3 + k, TEAK_D)
    # two records leaning on the shelf under it
    cv.rect(x0 + 7, y0 + 12, x0 + 19, y0 + 23, (60, 110, 150)); cv.rect(x0 + 9, y0 + 11, x0 + 21, y0 + 23, (220, 200, 150))
    cv.rect(x0 + 13, y0 + 15, x0 + 17, y0 + 19, (180, 60, 50))

def record_player():
    # a portable record player in a two-tone case: its lid up behind, lined in cream, the
    # turntable's record seen nearly edge on with its red label, the tonearm resting on it,
    # the speaker grille and the knobs on the front
    w, h = PLAYER[2], PLAYER[3]
    CASE, CASE_L, CASE_D, LID = (72, 128, 132), (104, 160, 160), (48, 92, 98), (236, 226, 204)
    cv = C(w, h)
    cv.rect(1, 0, w - 2, 15, CASE); cv.rect(3, 2, w - 4, 14, LID); cv.rect(1, 0, w - 2, 0, CASE_L)
    for y in range(4, 14, 2): cv.rect(5, y, w - 6, y, (220, 208, 182))
    cv.rect(0, 16, w - 1, 18, (40, 38, 40))                         # the deck
    cv.ell(3, 14, w - 6, 18, (24, 22, 24)); cv.ell(10, 15, 16, 17, (190, 56, 46))
    cv.rect(13, 16, 13, 16, (240, 230, 210))
    cv.line([(w - 3, 13), (w - 4, 16), (16, 16)], (196, 198, 200)); cv.rect(w - 4, 12, w - 2, 13, (150, 152, 154))
    cv.rect(0, 19, w - 1, h - 1, CASE); cv.rect(0, 19, w - 1, 19, CASE_L); cv.rect(0, h - 1, w - 1, h - 1, CASE_D); cv.rect(w - 1, 19, w - 1, h - 1, CASE_D)
    for y in range(21, h - 2, 2):
        for x in range(2, 15, 2): cv.px(x, y, CASE_D)
    for x in (19, 24): cv.rect(x, 24, x + 2, 26, (220, 210, 190)); cv.px(x + 1, 24, (120, 110, 100))
    return cv.im

def spin(n=3):
    # the record turning: a glint that runs round the record, seen edge on, a frame at a time
    w, h = PLAYER[2], PLAYER[3]
    out = []
    for k in range(n):
        cv = C(w, h)
        for i, x in enumerate((5 + k * 6, 21 - k * 4)):
            cv.px(x, 15 + i * 2, (110, 108, 120)); cv.px(x + 1, 15 + i * 2, (80, 78, 90))
        out.append(cv.im)
    return out

def cabinet(cv):
    # a teak cabinet on a plinth, two sliding doors with round pulls; the tank stands on it
    x0, y0, x1, y1 = CABINET
    cv.rect(x0, y0, x1, y1 - 6, TEAK)
    cv.rect(x0, y0, x1, y0 + 2, TEAK_L); cv.rect(x0, y0 + 3, x1, y0 + 3, TEAK_D)
    cv.rect(x0, y0, x0, y1 - 6, TEAK_L); cv.rect(x1, y0, x1, y1 - 6, TEAK_DD)
    mid = (x0 + x1) // 2
    for a, b in ((x0 + 4, mid - 1), (mid + 1, x1 - 4)):
        cv.rect(a, y0 + 7, b, y1 - 11, (180, 130, 92)); cv.rect(a, y0 + 7, b, y0 + 7, TEAK_DD); cv.rect(a, y0 + 7, a, y1 - 11, TEAK_D)
        # the grain, long and pale
        for k in range(5):
            gy = y0 + 14 + k * 11
            cv.rect(a + 4 + (k * 7) % 20, gy, b - 6 - (k * 5) % 16, gy, (190, 140, 100))
    for px_ in (mid - 8, mid + 6):
        cv.rect(px_, y0 + 34, px_ + 2, y0 + 36, TEAK_DD); cv.px(px_, y0 + 34, TEAK_D)
    cv.rect(x0 + 6, y1 - 5, x1 - 6, y1, TEAK_DD)

# ---------------------------------------------------------------- the things that stand on their own
def tank():
    # the tank: a black hood with its lamp, the glass in a black frame, the water lit from above,
    # sand and gravel, two clumps of vallisneria, a sword plant, a piece of driftwood, a stone,
    # the airstone's tube in the corner; the fish and bubbles are laid over it by the page
    w, h = TANK[2], TANK[3]
    cv = C(w, h)
    cv.rect(0, 0, w - 1, 8, INK); cv.rect(1, 0, w - 2, 0, (79, 73, 67)); cv.rect(4, 8, w - 5, 8, (230, 236, 210))
    cv.rect(0, 9, w - 1, h - 1, INK)
    wx0, wy0, wx1, wy1 = 2, 9, w - 3, h - 4
    # the water: pale under the lamp, deeper toward the gravel, banded in a dither
    for y in range(wy0, wy1 + 1):
        t = (y - wy0) / (wy1 - wy0)
        for x in range(wx0, wx1 + 1):
            c = WATER_L if t < 0.22 else WATER if t < 0.62 else WATER_D
            if 0.18 < t < 0.26 and (x + y) % 2: c = WATER
            if 0.58 < t < 0.66 and (x + y) % 2: c = WATER_D
            cv.px(x, y, c)
    cv.rect(wx0, wy0, wx1, wy0 + 1, (200, 232, 220))        # the surface, under the lamp
    # the gravel, a bank rising to the back
    rnd = random.Random(1962)
    for x in range(wx0, wx1 + 1):
        top = wy1 - 9 - int(3 * math.sin(x / 23)) - (2 if 60 < x < 120 else 0)
        for y in range(top, wy1 + 1):
            cv.px(x, y, rnd.choice(GRAVEL) if y > top else (200, 180, 140))
    # driftwood and a stone
    cv.poly([(56, wy1 - 9), (78, wy1 - 26), (84, wy1 - 25), (66, wy1 - 9)], (110, 78, 52))
    cv.line([(70, wy1 - 18), (62, wy1 - 34)], (110, 78, 52), 2); cv.line([(78, wy1 - 26), (92, wy1 - 36)], (128, 92, 62))
    cv.ell(118, wy1 - 16, 136, wy1 - 6, (120, 124, 120)); cv.ell(120, wy1 - 16, 130, wy1 - 11, (150, 156, 150))
    # the plants: ribbons of vallisneria at each end, a broad sword plant in the middle
    for x0, n, hmax in ((6, 9, 62), (w - 30, 10, 64)):
        for k in range(n):
            bx = x0 + k * 2 + rnd.randint(0, 1); ht = rnd.randint(int(hmax * 0.55), hmax)
            lean = rnd.uniform(-0.25, 0.25)
            for j in range(ht):
                y = wy1 - 8 - j
                x = int(round(bx + lean * j + 1.4 * math.sin(j / 9 + k)))
                if y > wy0 + 2: cv.px(x, y, GREEN_L if k % 3 == 0 else GREEN if k % 3 == 1 else GREEN_D)
    for k, a in enumerate((-50, -25, -5, 15, 40, 60)):
        r = math.radians(a); L = 24 - abs(a) / 6
        for j in range(int(L)):
            cx = 104 + math.sin(r) * j; cy = wy1 - 10 - math.cos(r) * j
            wd = 2.5 * math.sin(math.pi * j / L)
            for u in np.arange(-wd, wd + 0.1, 0.5):
                cv.px(int(round(cx + u * math.cos(r))), int(round(cy + u * math.sin(r))), GREEN if u < 0 else GREEN_D if u > 0.8 else GREEN_L)
    # the air line, down the back corner to its stone
    cv.rect(w - 8, wy0 + 2, w - 8, wy1 - 9, (196, 220, 214)); cv.rect(w - 10, wy1 - 10, w - 6, wy1 - 8, GREY)
    # the glass: a streak of light across it, the frame's bottom rail
    for k in range(3): cv.line([(26 + k * 4, wy0 + 6), (14 + k * 4, wy0 + 30)], (176, 222, 214))
    cv.rect(0, h - 4, w - 1, h - 1, INK); cv.rect(4, h - 3, w - 5, h - 3, (79, 73, 67))
    return cv.im

SWIM = (TANK[0] + 6, TANK[1] + 14, TANK[2] - 12, 58)       # where the fish swim, in the wall's pixels

def fish_tetras():
    # a school of six neon tetras, facing right then left: a blue stripe over a red rear
    def one(cv, x, y, d):
        body = [(0, 1), (1, 1), (2, 1), (3, 1), (4, 1), (1, 0), (2, 0), (3, 0), (1, 2), (2, 2), (3, 2)]
        for bx, by in body:
            X = x + (bx if d > 0 else 4 - bx)
            c = NEON_B if by == 0 or (by == 1 and bx >= 2) else SILVER
            if by == 2 and bx <= 2: c = NEON_R
            if by == 1 and bx < 2: c = NEON_R
            cv.px(X, y + by, c)
        cv.px(x + (5 if d > 0 else -1), y + 1, INK)          # the eye side is the head; the tail is the far pixel
    spots = [(1, 2), (8, 0), (14, 3), (5, 6), (12, 8), (19, 5)]
    out = []
    for d in (1, -1):
        cv = C(26, 12)
        for x, y in spots: one(cv, x if d > 0 else 25 - x - 5, y, d)
        out.append(cv.im)
    return out

def fish_angel():
    # an angelfish, its tall fins and three dark bars, facing right then left
    rows = ['....i.....', '...iii....', '..isiss...', '.ississs..', 'isississe.', 'sissississ', 'isississe.', '.ississs..', '..isiss...', '...ii.....', '....i.....']
    out = []
    for d in (1, -1):
        cv = C(10, 11)
        for y, row in enumerate(rows):
            for x, ch in enumerate(row):
                if ch == '.': continue
                c = {'i': (60, 58, 56), 's': (226, 230, 224), 'e': INK}[ch]
                cv.px(x if d > 0 else 9 - x, y, c)
        out.append(cv.im)
    return out

def fish_cory():
    # a corydoras on the gravel, speckled grey with a dark eye, facing right then left
    rows = ['..gg...', '.gGgGg.', 'gGgGgGe', '.ggggg.']
    out = []
    for d in (1, -1):
        cv = C(7, 4)
        for y, row in enumerate(rows):
            for x, ch in enumerate(row):
                if ch == '.': continue
                cv.px(x if d > 0 else 6 - x, y, {'g': (170, 166, 150), 'G': (96, 92, 84), 'e': INK}[ch])
        out.append(cv.im)
    return out

def bubbles(n=8):
    # the airstone's bubbles, rising in a wobbling column, a frame at a time
    w, h = 7, 64
    frames = []
    for k in range(n):
        cv = C(w, h)
        for b in range(6):
            y = int(h - 2 - (b * 11 + k * 88 / n) % (h - 2))
            x = 3 + int(round(1.2 * math.sin((y + b * 7) / 6)))
            s = 2 if y < h * 0.4 else 1
            cv.px(x, y, (230, 246, 240))
            if s == 2: cv.px(x + 1, y, (190, 230, 222)); cv.px(x, y - 1, (190, 230, 222))
        frames.append(cv.im)
    return frames

def flakes(n=8):
    # food, scattered on the surface and sinking: a frame at a time, fewer as they are eaten
    rnd = random.Random(5)
    w, h = 80, 40
    pts = [(rnd.uniform(4, w - 4), rnd.uniform(0, 3), rnd.uniform(0.6, 1.4), rnd.choice([(210, 140, 70), (190, 90, 60), (230, 190, 100)])) for _ in range(22)]
    frames = []
    for k in range(n):
        cv = C(w, h)
        for i, (x, y, v, c) in enumerate(pts):
            if i % n < k - 3: continue                          # eaten
            yy = y + k * 4.2 * v
            xx = x + 1.5 * math.sin(k / 2 + i)
            if yy < h: cv.px(int(xx), int(yy), c)
        frames.append(cv.im)
    return frames

def metronome():
    # a wooden pyramid metronome, its front open on the scale, a brass weight on its rod
    w, h = METRONOME[2], METRONOME[3]
    cv = C(w, h)
    cv.poly([(4, h - 4), (w - 5, h - 4), (w // 2 + 3, 0), (w // 2 - 3, 0)], WAL)
    cv.poly([(4, h - 4), (w // 2 - 3, 0), (w // 2 - 2, 0), (6, h - 4)], (110, 78, 56))
    cv.rect(1, h - 4, w - 2, h - 1, WAL_D); cv.rect(1, h - 4, w - 2, h - 4, (110, 78, 56))
    cv.poly([(w // 2 - 3, 5), (w // 2 + 3, 5), (w // 2 + 4, h - 8), (w // 2 - 4, h - 8)], CREAM)
    for y in range(7, h - 9, 3): cv.px(w // 2 - 2, y, GREY); cv.px(w // 2 + 2, y, GREY)
    cv.rect(w // 2 - 2, h - 8, w // 2 + 2, h - 6, (79, 73, 67))
    return cv.im

def pendulum(n=4):
    # the rod and its weight swinging about the pivot near the foot: left, middle, right, middle
    w, h = METRONOME[2], METRONOME[3]
    out = []
    for a in (-16, 0, 16, 0)[:n]:
        cv = C(w, h)
        px_, py_ = w // 2, h - 8
        r = math.radians(a)
        tx, ty = px_ + math.sin(r) * 24, py_ - math.cos(r) * 24
        cv.line([(px_, py_), (tx, ty)], (150, 152, 146))
        wx, wy = px_ + math.sin(r) * 15, py_ - math.cos(r) * 15
        cv.rect(int(wx) - 1, int(wy) - 1, int(wx) + 1, int(wy) + 1, OCH_L); cv.px(int(wx) + 1, int(wy) + 1, OCH)
        out.append(cv.im)
    return out

def kitchen_timer():
    # (for the desk, by the tape player) a tomato kitchen timer: a red body, lit from the left,
    # its turning top banded with the minutes' marks, a green calyx and stem on top
    w, h = 17, 15
    R, R_L, R_D, R_DD = (206, 58, 46), (238, 118, 96), (160, 40, 34), (118, 28, 26)
    cv = C(w, h)
    cv.ell(0, 3, w - 1, h - 1, R_D); cv.ell(0, 3, w - 3, h - 2, R)
    cv.rect(3, 5, 5, 6, R_L); cv.px(2, 7, R_L)
    cv.rect(1, 8, w - 2, 8, R_DD)                                  # the seam under the turning top
    for x in range(3, 14, 2): cv.px(x, 7, (246, 236, 220))         # its minutes
    cv.px(8, 9, (246, 236, 220))                                   # the pointer
    cv.poly([(4, 3), (8, 1), (12, 3), (8, 4)], (90, 140, 60)); cv.px(5, 4, (70, 112, 52)); cv.px(11, 4, (70, 112, 52))
    cv.rect(8, 0, 8, 2, (60, 96, 46))
    return cv.im

def album():
    # a photo album on end: a deep spine in black cloth, two gilt bands and a gilt label, its
    # boards' edges a shade lighter
    w, h = ALBUM[2], ALBUM[3]
    CL, CL_L, CL_D, GILT = (40, 36, 40), (70, 64, 70), (22, 20, 24), (214, 178, 96)
    cv = C(w, h)
    cv.rect(0, 0, w - 1, h - 1, CL); cv.rect(0, 0, 1, h - 1, CL_L); cv.rect(w - 2, 0, w - 1, h - 1, CL_D)
    for y in (4, h - 6): cv.rect(2, y, w - 3, y, GILT); cv.rect(2, y + 2, w - 3, y + 2, GILT)
    cv.rect(4, 13, w - 5, 22, (120, 30, 34)); cv.rect(5, 15, w - 6, 15, GILT); cv.rect(5, 17, w - 8, 17, GILT); cv.rect(5, 19, w - 6, 19, GILT)
    for y in range(26, h - 9, 4): cv.px(w // 2, y, CL_L)
    return cv.im

def camera():
    # a 35 mm single-lens reflex, straight on: a chrome top plate and the prism's hump, the body
    # in black leatherette, the lens in its barrel at the middle, the shutter release and the
    # rewind knob on top, a strap lug at each end
    w, h = CAMERA[2], CAMERA[3]
    CHR, CHR_L, CHR_D, LEA, LEA_L = (196, 198, 200), (232, 234, 236), (130, 132, 136), (36, 34, 36), (58, 56, 60)
    cv = C(w, h)
    cv.rect(2, 10, w - 3, 12, CHR); cv.rect(2, 10, w - 3, 10, CHR_L); cv.rect(2, 12, w - 3, 12, CHR_D)
    cv.poly([(13, 10), (16, 1), (24, 1), (27, 10)], CHR); cv.line([(16, 1), (24, 1)], CHR_L); cv.line([(13, 10), (16, 1)], CHR_L)
    cv.line([(24, 1), (27, 10)], CHR_D); cv.rect(16, 5, 24, 7, INK); cv.rect(18, 6, 22, 6, CHR_D)
    cv.rect(4, 7, 9, 9, CHR_D); cv.rect(5, 6, 8, 6, CHR); cv.rect(30, 7, 33, 9, CHR_D); cv.rect(31, 6, 32, 6, CHR_L)
    cv.rect(2, 13, w - 3, h - 3, LEA)
    for y in range(14, h - 3, 2):
        for x in range(3 + y % 4, w - 3, 4): cv.px(x, y, LEA_L)
    cv.rect(2, h - 2, w - 3, h - 1, CHR); cv.rect(2, h - 1, w - 3, h - 1, CHR_D)
    cv.rect(0, 13, 1, 15, CHR_D); cv.rect(w - 2, 13, w - 1, 15, CHR_D)
    cx, cy = 20, 18
    cv.ell(cx - 9, cy - 9, cx + 9, cy + 9, (20, 20, 22)); cv.ell(cx - 7, cy - 7, cx + 7, cy + 7, (96, 98, 102))
    cv.ell(cx - 6, cy - 6, cx + 6, cy + 6, (24, 26, 30)); cv.ell(cx - 4, cy - 4, cx + 4, cy + 4, (44, 56, 84))
    cv.px(cx - 2, cy - 3, (170, 196, 230)); cv.px(cx - 3, cy - 2, (170, 196, 230)); cv.px(cx + 2, cy + 2, (110, 90, 150))
    cv.rect(31, 15, 32, 17, CHR_D)                    # the self-timer's lever
    return cv.im

def handheld():
    # a pocket game console standing on end: a pale grey case, its screen's grey-green glass in
    # a dark bezel, a cross of buttons and two round ones, a slanting grille at its foot
    w, h = HANDHELD[2], HANDHELD[3]
    CASE, CASE_L, CASE_D = (200, 198, 190), (226, 224, 216), (150, 148, 142)
    cv = C(w, h)
    cv.rect(0, 0, w - 1, h - 1, CASE); cv.rect(0, 0, w - 1, 0, CASE_L); cv.rect(0, 0, 0, h - 1, CASE_L)
    cv.rect(w - 1, 1, w - 1, h - 1, CASE_D); cv.rect(1, h - 1, w - 2, h - 1, CASE_D)
    cv.clear(w - 1, h - 1, w - 1, h - 1); cv.clear(w - 2, h - 1, w - 1, h - 1); cv.clear(w - 1, h - 2, w - 1, h - 1)
    cv.rect(2, 2, w - 3, 11, (84, 84, 104)); cv.rect(4, 3, w - 5, 10, (139, 172, 15))
    for x, y in ((5, 8), (6, 8), (7, 8), (6, 7), (9, 9), (10, 9), (10, 8), (11, 9)): cv.px(x, y, (48, 98, 48))
    cv.px(3, 5, (210, 60, 60))
    cv.rect(3, 15, 5, 15, INK); cv.rect(4, 14, 4, 16, INK)                  # the cross
    cv.rect(11, 15, 12, 16, (150, 40, 90)); cv.rect(13, 13, 14, 14, (150, 40, 90))
    cv.rect(6, 19, 7, 19, CASE_D); cv.rect(9, 19, 10, 19, CASE_D)
    for k in range(3): cv.line([(10 + k * 2, 24), (12 + k * 2, 21)], CASE_D)
    return cv.im

CAT_INK, CAT_INK_L = (34, 32, 34), (70, 66, 70)
def cat_body():
    # a black cat clock: its head with pointed ears, white muzzle and whiskers, eyes whose
    # pupils the page swings, a white bow tie, its face on its belly, white paws; its tail,
    # swinging, is laid over it by the page as its eyes are
    w, h = CAT[2], CAT[3]
    cv = C(w, h)
    cv.poly([(6, 13), (10, 0), (17, 7)], CAT_INK); cv.poly([(35, 13), (31, 0), (24, 7)], CAT_INK)
    cv.poly([(9, 8), (10, 4), (13, 7)], (200, 120, 130)); cv.poly([(32, 8), (31, 4), (28, 7)], (200, 120, 130))
    cv.ell(4, 4, 37, 34, CAT_INK)
    cv.ell(7, 6, 18, 14, CAT_INK_L)
    # the eyes: white, a black lid line over each
    for ex in (10, 23):
        cv.ell(ex, 12, ex + 8, 20, PAPER); cv.rect(ex + 1, 12, ex + 7, 12, CAT_INK)
    # the muzzle, the nose, the grin
    cv.ell(13, 21, 28, 31, PAPER); cv.poly([(19, 21), (22, 21), (21, 23), (20, 23)], (210, 110, 120))
    cv.line([(15, 27), (18, 29), (20, 28), (21, 28), (23, 29), (26, 27)], CAT_INK)
    for y, dy in ((23, -2), (26, 0), (29, 2)):
        cv.line([(0, y + dy), (12, y)], GREY_L); cv.line([(29, y), (41, y + dy)], GREY_L)
    # the bow tie
    cv.poly([(13, 34), (20, 37), (13, 40)], PAPER); cv.poly([(28, 34), (21, 37), (28, 40)], PAPER)
    cv.rect(19, 35, 22, 39, (210, 210, 200))
    # the body, its face, the paws
    cv.d.rounded_rectangle([6, 38, 35, 81], radius=10, fill=CAT_INK + (255,))
    cv.rect(8, 42, 9, 76, CAT_INK_L)
    fx, fy, fs = CAT_FACE
    cv.ell(fx, fy, fx + fs - 1, fy + fs - 1, PAPER)
    c = (fs - 1) / 2
    for k in range(12):
        a = k * math.pi / 6
        cv.px(fx + round(c + math.sin(a) * 10.5), fy + round(c - math.cos(a) * 10.5), CAT_INK)
        if k % 3 == 0: cv.px(fx + round(c + math.sin(a) * 9.5), fy + round(c - math.cos(a) * 9.5), CAT_INK)
    for px_ in (9, 25): cv.ell(px_, 77, px_ + 7, 83, PAPER)
    return cv.im

def cat_moves(n=4):
    # the tail swinging from under the body, and the eyes with it: left, middle, right, middle
    w, h = CAT[2], CAT[3]
    out = []
    for k, a in enumerate((-1, 0, 1, 0)[:n]):
        cv = C(w, h)
        for j in range(29):
            y = 83 + j
            x = 20.5 + a * (j * 0.42 + 0.014 * j * j)
            cv.rect(int(round(x)) - 1, y, int(round(x)) + 2, y, CAT_INK)
        tx = 20.5 + a * (28 * 0.42 + 0.014 * 784)
        cv.rect(int(round(tx)) - 1, 112, int(round(tx)) + 2, 113, CAT_INK_L)
        for ex in (10, 23):
            cx = ex + 3 + a * 2
            cv.rect(cx, 14, cx + 2, 19, CAT_INK)
        out.append(cv.im)
    return out

# the books: cloth, bands, lettering
BOOK_LOOK = {'book-xenakis': (CREAM, INK, INK), 'book-hiller': (NAVY, OCH_L, OCH_L), 'book-cage': (PAPER, None, INK),
             'book-mccracken': (BLUE, CREAM, CREAM), 'book-knuth': ((96, 128, 96), OCH_L, CREAM)}
def book(name):
    x, y, w, h = book_box(name)
    cv = C(w, h)
    if name == 'book-reichardt':
        # a catalogue standing face out against the back of the shelf: its cover of words
        # in black on white, set on a slant
        cv.rect(0, 0, w - 1, h - 1, PAPER); cv.rect(w - 1, 0, w - 1, h - 1, GREY_L); cv.rect(0, h - 1, w - 1, h - 1, GREY_L)
        rnd = random.Random(1968)
        for k in range(11):
            yy = 4 + k * 3
            x0 = 3 + (k * 5) % 9; x1 = min(w - 4, x0 + rnd.randint(8, 20))
            cv.line([(x0, yy + 2), (x1, yy - 1)], INK)
        cv.rect(3, h - 6, 16, h - 5, TERRA)
        return cv.im
    c, band, lab = BOOK_LOOK[name]
    spine(cv, 0, h - 1, w, h, c, random.Random(len(name)), band, lab)
    if name == 'book-xenakis': cv.rect(2, 7, w - 3, 10, TERRA)
    return cv.im

# ---------------------------------------------------------------- the print over the tank (128 x 86)
def frame_print(ground, mat=PAPER):
    w, h = PRINT[2], PRINT[3]
    cv = C(w, h)
    cv.rect(0, 0, w - 1, h - 1, INK); cv.rect(0, 0, w - 1, 0, (79, 73, 67)); cv.rect(2, 2, w - 3, h - 3, mat)
    cv.rect(9, 8, w - 10, h - 15, ground)
    cv.rect(w // 2 - 10, h - 9, w // 2 + 9, h - 9, GREY)
    return cv

def print_kelly():
    # after Kelly's Spectrum Colors Arranged by Chance: a grid of squares, each colour drawn
    # by chance from eighteen
    rnd = random.Random(1951)
    cv = frame_print(PAPER)
    cols = [(232, 196, 40), (240, 150, 40), (226, 90, 40), (200, 40, 50), (170, 40, 90), (120, 50, 120), (60, 60, 140), (40, 90, 170),
            (40, 140, 190), (40, 150, 140), (60, 140, 80), (120, 170, 60), (180, 190, 60), (250, 230, 120), INK, (98, 96, 89), PAPER, (230, 160, 150)]
    x0, y0, x1, y1 = 9, 8, PRINT[2] - 10, PRINT[3] - 15
    n, m = 22, 13
    cw, ch = (x1 - x0 + 1) / n, (y1 - y0 + 1) / m
    for j in range(m):
        for i in range(n):
            cv.rect(int(x0 + i * cw), int(y0 + j * ch), int(x0 + (i + 1) * cw) - 1, int(y0 + (j + 1) * ch) - 1, rnd.choice(cols))
    return cv.im

def print_fluxus():
    # a poster for a Fluxus concert: FLUXUS across a black band, the evening's events in boxes
    # of type, one box in yellow
    cv = frame_print((229, 224, 209))
    x0, y0, x1, y1 = 9, 8, PRINT[2] - 10, PRINT[3] - 15
    cv.rect(x0, y0, x1, y0 + 13, INK)
    text(cv, x0 + 4, y0 + 1, 'FLUXUS', (229, 224, 209))
    text(cv, x1 - 30, y0 + 1, '1962', (242, 183, 5))
    cv.rect(x0, y0 + 15, x1, y0 + 16, (242, 183, 5))
    rnd = random.Random(1962)
    boxes = [(x0, y0 + 19, x0 + 34, y0 + 40), (x0 + 37, y0 + 19, x0 + 74, y0 + 31), (x0 + 77, y0 + 19, x1, y0 + 40),
             (x0 + 37, y0 + 34, x0 + 74, y1), (x0, y0 + 43, x0 + 34, y1), (x0 + 77, y0 + 43, x1, y1)]
    for k, (a, b, c, d) in enumerate(boxes):
        if k == 3: cv.rect(a, b, c, d, (242, 183, 5)); ink = INK
        else: cv.line([(a, b), (c, b), (c, d), (a, d), (a, b)], INK); ink = (98, 96, 89)
        for yy in range(b + 3, d - 1, 3):
            cv.rect(a + 3, yy, c - 3 - rnd.randint(0, (c - a) // 3), yy, ink)
    return cv.im

def print_molnar():
    # after Molnár's (Des)Ordres: nested squares in ink, their corners moved by chance, more so
    # toward the lower right
    rnd = random.Random(1974)
    cv = frame_print(PAPER)
    x0, y0, x1, y1 = 9, 8, PRINT[2] - 10, PRINT[3] - 15
    n, m = 6, 4
    cs = min((x1 - x0) / n, (y1 - y0) / m)
    ox = x0 + ((x1 - x0) - cs * n) / 2; oy = y0 + ((y1 - y0) - cs * m) / 2
    for j in range(m):
        for i in range(n):
            cx, cy = ox + (i + 0.5) * cs, oy + (j + 0.5) * cs
            dis = (i / (n - 1) + j / (m - 1)) / 2
            for r in range(2, int(cs / 2), 2):
                if rnd.random() < dis * 0.35: continue
                pts = []
                for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
                    j_ = dis * 2.2
                    pts.append((cx + sx * r + rnd.uniform(-j_, j_), cy + sy * r + rnd.uniform(-j_, j_)))
                cv.line(pts + [pts[0]], INK)
    return cv.im

PRINTS = {'print-kelly': print_kelly, 'print-fluxus': print_fluxus, 'print-molnar': print_molnar}

# ---------------------------------------------------------------- the turns, and their cursors (unlit)
def turn_tab(d):
    # a tab of ink at the wall's edge, a paper chevron on it pointing round the corner
    w, h = 12, 22
    cv = C(w, h)
    cv.rect(0, 0, w - 1, h - 1, INK); cv.rect(0, 0, w - 1, 0, (79, 73, 67))
    for k in range(5):
        x = 4 + k if d > 0 else 7 - k
        cv.rect(x, 6 + k, x + 1, 6 + k, (255, 250, 240)); cv.rect(x, 15 - k, x + 1, 15 - k, (255, 250, 240))
    return cv.im

def turn_cursor(d):
    # a pixel arrow for the cursor, white in an ink line, at twice the room's pixel (as the others)
    rows = ['......X.......', '......XX......', 'XXXXXXXoX.....', 'XooooooooX....', 'XoooooooooX...', 'XooooooooooX..',
            'XoooooooooX...', 'XooooooooX....', 'XXXXXXXoX.....', '......XX......', '......X.......']
    w, h = len(rows[0]), len(rows)
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch == '.': continue
            X = x if d > 0 else w - 1 - x
            im.putpixel((X, y), (30, 29, 27, 255) if ch == 'X' else (255, 250, 240, 255))
    return im.resize((w * 2, h * 2), Image.NEAREST)

# ---------------------------------------------------------------- all together
def backdrop2(tile, first):
    """the second wall, for one paper: wall, floor, bookcase and its books, chair, cabinet, and
    their hard shadows"""
    bg = wall2(tile, first)
    for fn in (bookcase, cabinet, side_table):
        cv = C(W, H); fn(cv, random.Random(1971)) if fn is bookcase else fn(cv)
        drop(bg, cv.im, 0, 0, 2, 2); bg.alpha_composite(cv.im)
    # the print's and the tank's shadows fall on the wall whichever print hangs
    pr = C(PRINT[2], PRINT[3]); pr.rect(0, 0, PRINT[2] - 1, PRINT[3] - 1, INK)
    drop(bg, pr.im, PRINT[0], PRINT[1], 2, 2)
    tk = C(TANK[2], TANK[3]); tk.rect(0, 0, TANK[2] - 1, TANK[3] - 1, INK)
    drop(bg, tk.im, TANK[0], TANK[1], 2, 0)
    return bg

def sprites2():
    """the things that stand on their own: name -> (picture, place)"""
    S = {'px-tank.png': (tank(), TANK[:2]), 'px-metronome.png': (metronome(), (METRONOME[0], COMPS[METRONOME[1]][1] - METRONOME[3] + 1)),
         'px-cat-clock.png': (cat_body(), CAT[:2]), 'px-handheld.png': (handheld(), HANDHELD[:2]), 'px-camera.png': (camera(), CAMERA[:2]), 'px-album.png': (album(), ALBUM[:2]), 'px-record-player.png': (record_player(), PLAYER[:2])}
    for n, fn in CHAIRS.items(): S[n + '.png'] = (chair_pic(fn), CHAIR_BOX[:2])
    for n, *_ in BOOKS:
        x, y, w, h = book_box(n); S['px-' + n + '.png'] = (book(n), (x, y))
    for n, fn in PRINTS.items(): S[n + '.png'] = (fn(), PRINT[:2])
    return S

def anims2():
    """the loops: name -> (frames, place)"""
    t = fish_tetras(); a = fish_angel(); c = fish_cory()
    return {'tetras.png': (t, (SWIM[0] + 40, SWIM[1] + 18)), 'angel.png': (a, (SWIM[0] + 90, SWIM[1] + 10)),
            'cory.png': (c, (SWIM[0] + 60, TANK[1] + TANK[3] - 15)), 'bubbles.png': (bubbles(), (TANK[0] + TANK[2] - 11, TANK[1] + 10)),
            'flakes.png': (flakes(), (TANK[0] + 52, TANK[1] + 11)), 'pendulum.png': (pendulum(), (METRONOME[0], COMPS[METRONOME[1]][1] - METRONOME[3] + 1)),
            'cat.png': (cat_moves(), CAT[:2]), 'spin.png': (spin(), PLAYER[:2])}

if __name__ == '__main__':
    PROOF_CHAIR = sys.argv[1] if len(sys.argv) > 1 else 'chair-lounge.png'
    import room
    from build import backdrop
    from sheet import all_sprites
    HERE = UTIL + '/v25/'
    S = all_sprites()
    tile = room.wall_tile()
    first = backdrop(tile, S)
    bg = backdrop2(tile, first)
    for n, (im, xy) in sprites2().items():
        if (n.startswith('print-') and n != 'print-kelly.png') or (n.startswith('chair-') and n != PROOF_CHAIR): continue
        bg.alpha_composite(im, tuple(xy))
    for n, (fr, xy) in anims2().items():
        if n != 'flakes.png': bg.alpha_composite(fr[0], tuple(xy))
    both = Image.new('RGBA', (W * 2, H)); both.paste(first, (0, 0)); both.paste(bg, (W, 0))
    both.resize((W * 4, H * 2), Image.NEAREST).save(HERE + 'part2-proof.png')
    print('ok')
