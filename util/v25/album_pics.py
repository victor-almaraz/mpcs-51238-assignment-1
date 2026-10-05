# The photo album's photographs, drawn in pixels: black-and-white prints (96 x 72 inside a
# white border of 4, 104 x 80) and Polaroids (62 x 62 inside the white frame, its foot deep,
# 72 x 88), places and people. Skies and light are ordered dithers between two colours; the
# prints are cut to seven greys and a little grain, the Polaroids to their own faded colours.
import os as _os; UTIL = _os.path.normpath(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..')); REPO = _os.path.dirname(UTIL)
import math, random
import numpy as np
from PIL import Image, ImageDraw
OUT = REPO + '/v25/assets/st/'
BAYER = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16 + 1 / 32

class Pic:
    def __init__(self, w, h, c):
        self.im = Image.new('RGB', (w, h), c); self.d = ImageDraw.Draw(self.im); self.w, self.h = w, h
    def grad(self, box, c0, c1, horiz=False):
        """from c0 to c1 across a box, as an ordered dither of the two"""
        x0, y0, x1, y1 = box
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                t = (x - x0) / max(1, x1 - x0) if horiz else (y - y0) / max(1, y1 - y0)
                self.im.putpixel((x, y), c1 if t > BAYER[y % 4, x % 4] else c0)
    def rect(self, box, c): self.d.rectangle(box, fill=c)
    def poly(self, pts, c): self.d.polygon(pts, fill=c)
    def ell(self, box, c): self.d.ellipse(box, fill=c)
    def line(self, pts, c, w=1): self.d.line(pts, fill=c, width=w)
    def px(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h: self.im.putpixel((int(x), int(y)), c)

def G(v): return (v, v, v)
K, D, M, L, P, W = G(18), G(58), G(104), G(152), G(196), G(236)

def person(p, x, y, h, coat=D, skin=P, hat=None):
    """a figure standing, its feet at (x, y), h tall"""
    hd = max(2, h // 6)
    p.rect([x - 1, y - h + hd, x + 1, y - h // 2], coat); p.rect([x - 2, y - h + hd + 1, x + 2, y - h // 3], coat)
    p.rect([x - 1, y - h // 3, x - 1, y], coat); p.rect([x + 1, y - h // 3, x + 1, y], coat)
    p.ell([x - hd // 2 - 1, y - h, x + hd // 2, y - h + hd], skin)
    if hat: p.rect([x - hd // 2 - 1, y - h - 1, x + hd // 2, y - h + 1], hat)

# ---------------------------------------------------------------- the black-and-white prints
def bw_tram():
    # the last tram home: a wet street at night, the tram's lit windows and their reflection
    p = Pic(96, 72, K)
    p.grad([0, 0, 95, 30], K, D)
    for x0, w, h in ((0, 18, 40), (20, 14, 52), (36, 22, 34), (62, 16, 46), (80, 16, 38)):
        p.rect([x0, 46 - h, x0 + w, 46], G(30))
        for wy in range(46 - h + 4, 44, 6):
            for wx in range(x0 + 2, x0 + w - 2, 5):
                if (wx * 7 + wy * 3) % 5 < 2: p.rect([wx, wy, wx + 1, wy + 2], P)
    p.rect([0, 46, 95, 71], G(26))
    p.rect([24, 30, 70, 48], M); p.rect([24, 30, 70, 31], L)
    for k in range(6): p.rect([27 + k * 7, 34, 31 + k * 7, 40], W)
    p.rect([24, 47, 70, 48], K); p.line([(46, 30), (52, 14)], L); p.line([(0, 14), (95, 12)], M)
    for k in range(6):
        for y in range(52, 70, 2):
            if (y + k) % 3: p.rect([27 + k * 7, y, 31 + k * 7, y], G(110 - (y - 52) * 4))
    p.ell([4, 40, 10, 44], P); p.line([(7, 44), (7, 50)], M)
    return p.im, 'The last tram home, the street still wet'

def bw_ferry():
    # a woman in a headscarf at a ferry's rail, the water and a far shore behind her
    p = Pic(96, 72, L)
    p.grad([0, 0, 95, 26], W, P)
    p.poly([(0, 30), (20, 24), (44, 27), (70, 22), (95, 28), (95, 34), (0, 34)], M)
    p.grad([0, 34, 95, 71], L, M)
    for k in range(20): x, y = (k * 37) % 96, 38 + (k * 11) % 30; p.line([(x, y), (x + 5, y)], P)
    p.rect([0, 54, 95, 56], K); p.rect([0, 60, 95, 61], D)
    for x in range(4, 96, 10): p.rect([x, 54, x + 1, 71], K)
    # her head and shoulders, from the left, her scarf blowing
    p.poly([(30, 71), (34, 50), (46, 44), (60, 46), (66, 71)], D)
    p.ell([40, 22, 58, 44], P); p.poly([(38, 26), (48, 16), (60, 22), (62, 40), (56, 30), (42, 32)], K)
    p.poly([(60, 26), (76, 30), (70, 36), (62, 34)], D)
    p.rect([46, 33, 49, 34], M); p.px(52, 30, D); p.px(45, 30, D)
    return p.im, 'On the morning ferry, the wind off the water'

def bw_chess():
    # two old men at chess in a park, a plane tree's shade over them, a third watching
    p = Pic(96, 72, P)
    p.grad([0, 0, 95, 40], L, P)
    p.ell([-10, -20, 60, 30], D); p.ell([40, -14, 110, 26], M)
    p.rect([46, 10, 52, 50], K)
    p.rect([0, 50, 95, 71], L)
    for k in range(30): p.px((k * 29) % 96, 52 + (k * 7) % 18, M)
    p.rect([30, 46, 66, 48], K); p.rect([32, 48, 33, 62], K); p.rect([63, 48, 64, 62], K)
    for i in range(6):
        for j in range(2): p.rect([36 + i * 4, 44 - j, 37 + i * 4, 44 - j], K if (i + j) % 2 else W)
    person(p, 24, 62, 24, D, P, K); p.rect([18, 50, 30, 62], D)
    person(p, 72, 62, 24, M, P); p.rect([66, 50, 78, 62], M)
    person(p, 86, 62, 28, D, P, K)
    return p.im, 'Chess under the plane trees, Sunday'

def bw_lake():
    # a mountain lake: snow on the peaks, their reflection broken by a breeze, a jetty
    p = Pic(96, 72, W)
    p.grad([0, 0, 95, 22], P, W)
    p.poly([(0, 40), (16, 18), (28, 30), (46, 8), (64, 28), (78, 16), (95, 34), (95, 40)], M)
    p.poly([(40, 15), (46, 8), (52, 15), (48, 14), (44, 17)], W); p.poly([(74, 20), (78, 16), (82, 21)], W)
    p.poly([(0, 40), (12, 34), (30, 38), (50, 33), (70, 37), (95, 34), (95, 42), (0, 42)], D)
    p.grad([0, 42, 95, 71], L, P)
    for y in range(44, 66, 2):
        for x in range(0, 96, 3):
            if (x * 5 + y * 3) % 11 < 4: p.px(x, y, M)
    p.rect([60, 58, 95, 60], D)
    for x in (64, 74, 84, 94): p.rect([x, 60, x, 66], K)
    person(p, 88, 58, 12, K, M)
    return p.im, 'The lake above the village, before the weather turned'

def bw_machine_room():
    # the computing centre at night: the operator at the console, tape drives behind her
    p = Pic(96, 72, G(40))
    p.rect([0, 0, 95, 48], G(48))
    for k in range(5):
        x = 4 + k * 19
        p.rect([x, 6, x + 15, 48], L); p.rect([x + 1, 7, x + 14, 8], P)
        for cx in (x + 4, x + 11): p.ell([cx - 3, 12, cx + 3, 18], K); p.px(cx, 15, P)
        p.rect([x + 3, 24, x + 12, 34], G(80))
    p.rect([0, 48, 95, 71], G(70))
    for k in range(8): p.line([(k * 14, 48), (k * 20 - 20, 71)], G(60))
    p.rect([20, 50, 70, 60], P); p.rect([20, 50, 70, 51], W)
    for k in range(10): p.px(24 + k * 4, 54, K if k % 3 else W); p.px(26 + k * 4, 56, D)
    p.rect([30, 60, 32, 71], D); p.rect([58, 60, 60, 71], D)
    person(p, 46, 60, 26, D, P)
    p.poly([(42, 34), (50, 34), (52, 40), (40, 40)], K)
    return p.im, 'The machine room after midnight, the operator at the console'

def bw_lighthouse():
    # a lighthouse on cliffs in the fog, its beam across the grey
    p = Pic(96, 72, L)
    p.grad([0, 0, 95, 40], L, P)
    p.poly([(56, 18), (95, 4), (95, 12), (58, 20)], W)
    p.rect([50, 14, 58, 44], W); p.rect([50, 24, 58, 28], D); p.rect([50, 34, 58, 38], D)
    p.rect([49, 10, 59, 14], D); p.rect([51, 8, 57, 10], K)
    p.poly([(28, 71), (36, 44), (70, 42), (95, 54), (95, 71)], D)
    p.poly([(0, 71), (0, 58), (20, 56), (32, 71)], M)
    p.grad([0, 60, 95, 71], P, L)
    for k in range(14): x, y = (k * 41) % 96, 61 + (k * 5) % 10; p.line([(x, y), (x + 7, y)], W)
    return p.im, 'The light at the point, in fog'

def bw_platform():
    # a station platform under its roof, travellers with cases, the train's steam
    p = Pic(96, 72, M)
    p.rect([0, 0, 95, 10], D)
    for k in range(9): p.line([(k * 12, 0), (48, 14)], K)
    p.grad([0, 10, 95, 30], P, L)
    p.ell([50, 12, 90, 40], W); p.ell([62, 6, 95, 30], P)
    p.rect([0, 30, 46, 52], K); p.rect([4, 34, 40, 40], M)
    for x in range(6, 40, 8): p.rect([x, 35, x + 5, 39], P)
    p.rect([0, 52, 95, 71], L); p.line([(0, 52), (95, 52)], W)
    for x, h, c in ((54, 26, K), (62, 24, D), (74, 27, K), (86, 22, D)):
        person(p, x, 66, h, c, P, K if h > 24 else None)
    p.rect([57, 60, 61, 64], D); p.rect([77, 61, 82, 65], M)
    p.rect([20, 4, 30, 8], W); p.rect([24, 8, 25, 12], K)
    return p.im, 'Waiting for the night train, with the steam coming in'

# ---------------------------------------------------------------- the Polaroids (faded colour)
def fade(im, warm=(18, 8, -10), lift=34):
    a = np.array(im).astype(np.float32)
    a = lift + a * (1 - lift / 255) + np.array(warm)
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))

def pol_beach():
    p = Pic(62, 62, (120, 180, 200))
    p.grad([0, 0, 61, 26], (110, 170, 210), (190, 214, 220))
    p.rect([0, 27, 61, 36], (40, 110, 150)); p.line([(0, 27), (61, 27)], (90, 150, 180))
    p.grad([0, 37, 61, 61], (226, 206, 160), (210, 186, 140))
    for k in range(8): x = 4 + (k * 13) % 56; p.line([(x, 34), (x + 6, 34)], (220, 236, 240))
    for k, c in enumerate(((200, 60, 50), (60, 110, 170), (230, 190, 60))):
        x = 8 + k * 16
        p.rect([x, 30, x + 10, 44], c); p.poly([(x - 1, 30), (x + 5, 25), (x + 11, 30)], (240, 236, 226))
        for y in range(31, 44, 3): p.line([(x, y), (x + 10, y)], (240, 236, 226))
        p.rect([x + 4, 38, x + 6, 44], (60, 40, 30))
    p.ell([44, 4, 54, 14], (250, 236, 180))
    return fade(p.im), 'The huts at the end of the beach'

def pol_rooftop():
    p = Pic(62, 62, (240, 150, 90))
    p.grad([0, 0, 61, 34], (230, 110, 90), (250, 190, 110))
    p.ell([36, 22, 54, 40], (255, 220, 140))
    for x0, w, h in ((0, 10, 20), (12, 8, 26), (22, 12, 16), (40, 10, 22), (52, 10, 18)):
        p.rect([x0, 40 - h, x0 + w, 40], (90, 60, 80))
    p.rect([0, 40, 61, 61], (120, 80, 70)); p.rect([0, 40, 61, 41], (160, 110, 90))
    for x, c in ((22, (40, 60, 110)), (34, (150, 40, 50))):
        person(p, x, 56, 22, c, (230, 180, 140))
    p.line([(24, 42), (32, 42)], (230, 180, 140))
    return fade(p.im, (14, 4, -14)), 'Up on the roof, the evening it finally stopped raining'

def pol_balloon():
    p = Pic(62, 62, (150, 200, 230))
    p.grad([0, 0, 61, 40], (140, 190, 230), (210, 230, 240))
    p.rect([40, 10, 41, 40], (180, 60, 60)); p.poly([(30, 12), (41, 2), (52, 12)], (200, 70, 70))
    for k in range(6): p.line([(41, 2), (30 + k * 4, 12)], (240, 230, 200))
    p.ell([8, 4, 24, 22], (220, 40, 60)); p.px(12, 8, (250, 160, 170)); p.line([(16, 22), (22, 40)], (80, 80, 80))
    p.rect([0, 44, 61, 61], (110, 160, 80))
    person(p, 22, 58, 18, (230, 180, 50), (240, 196, 160))
    person(p, 34, 58, 28, (60, 80, 140), (230, 186, 150))
    p.rect([46, 36, 58, 50], (240, 220, 180)); p.poly([(44, 36), (52, 30), (60, 36)], (210, 60, 60))
    return fade(p.im), 'The fair on the common: the balloon was not lost'

def pol_cafe():
    p = Pic(62, 62, (220, 210, 190))
    p.rect([0, 0, 61, 30], (200, 196, 180))
    for x in range(0, 62, 12): p.rect([x, 4, x + 8, 22], (150, 160, 170)); p.rect([x + 1, 5, x + 7, 21], (190, 210, 220))
    p.rect([0, 0, 61, 3], (180, 70, 60))
    for x in range(0, 62, 6): p.poly([(x, 3), (x + 3, 7), (x + 6, 3)], (240, 236, 226) if (x // 6) % 2 else (180, 70, 60))
    p.ell([4, 34, 58, 58], (236, 232, 224)); p.ell([6, 36, 56, 56], (226, 220, 210))
    p.ell([16, 40, 30, 50], (250, 248, 244)); p.ell([19, 42, 27, 48], (90, 54, 34)); p.rect([30, 44, 32, 46], (250, 248, 244))
    p.rect([36, 42, 48, 48], (240, 236, 226)); p.line([(37, 44), (46, 44)], (120, 110, 100)); p.line([(37, 46), (43, 46)], (120, 110, 100))
    p.rect([0, 30, 61, 33], (130, 110, 90))
    return fade(p.im, (16, 6, -6)), 'A coffee on the square, and the letter home'

def pol_cellar():
    p = Pic(62, 62, (40, 26, 30))
    p.grad([0, 0, 61, 61], (60, 34, 40), (30, 20, 24))
    p.poly([(20, 0), (42, 0), (54, 61), (8, 61)], (90, 60, 50))
    for x, c, h in ((16, (30, 30, 50), 26), (31, (140, 40, 40), 30), (46, (40, 60, 40), 26)):
        person(p, x, 54, h, c, (230, 180, 140))
    p.rect([38, 30, 40, 46], (200, 160, 70)); p.ell([36, 44, 42, 48], (220, 180, 80))
    p.rect([10, 36, 22, 40], (120, 70, 40)); p.ell([44, 34, 54, 44], (180, 150, 110)); p.rect([48, 24, 49, 34], (60, 40, 30))
    p.rect([0, 54, 61, 61], (50, 30, 26))
    return fade(p.im, (24, 6, 0), 26), 'The trio in the cellar, the night the bass came'

PRINTS = [bw_tram, bw_ferry, bw_chess, bw_lake, bw_machine_room, bw_lighthouse, bw_platform]
POLAROIDS = [pol_beach, pol_rooftop, pol_balloon, pol_cafe, pol_cellar]

def grey7(im):
    """the print cut to seven greys by an ordered dither, a grain over it"""
    a = np.array(im.convert('L')).astype(np.float32) / 255
    h, w = a.shape; yy, xx = np.mgrid[0:h, 0:w]
    rnd = np.random.RandomState(7)
    v = np.clip(np.floor(a * 6 + BAYER[yy % 4, xx % 4] + rnd.uniform(-0.12, 0.12, a.shape)), 0, 6) / 6
    g = (16 + v * 222).astype(np.uint8)
    return Image.fromarray(np.stack([g, g, g], -1))

def mount_print(im):
    out = Image.new('RGB', (104, 80), (238, 236, 228)); out.paste(grey7(im), (4, 4)); return out
def mount_polaroid(im):
    out = Image.new('RGB', (72, 88), (240, 238, 230))
    q = im.quantize(colors=16, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE).convert('RGB')
    out.paste(q, (5, 5)); return out

if __name__ == '__main__':
    caps = []
    for i, fn in enumerate(PRINTS):
        im, cap = fn(); mount_print(im).save(OUT + 'album-p%d.png' % (i + 1), optimize=True); caps.append(('album-p%d.png' % (i + 1), cap))
    for i, fn in enumerate(POLAROIDS):
        im, cap = fn(); mount_polaroid(im).save(OUT + 'album-q%d.png' % (i + 1), optimize=True); caps.append(('album-q%d.png' % (i + 1), cap))
    sheet = Image.new('RGB', (6 * 110, 2 * 96), (30, 30, 30))
    for i, (n, _) in enumerate(caps):
        im = Image.open(OUT + n); sheet.paste(im, ((i % 6) * 110, (i // 6) * 96))
    sheet.resize((sheet.width * 2, sheet.height * 2), Image.NEAREST).save(UTIL + '/v25/album.png')
    for n, c in caps: print(n, '|', c)
