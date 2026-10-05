# The photo album's photographs, drawn in pixels, one to a page: black-and-white prints
# (192 x 144 inside a white border of 8, 208 x 160) and Polaroids (128 x 128 inside the white
# frame, its foot deep, 140 x 168), places and people. Each scene is painted in light and
# tone (a value from 0, black, to 1, white, or a colour) and the prints are then cut to nine
# greys by an ordered dither with a little grain, the Polaroids to their own faded colours.
import math, random
import numpy as np
from PIL import Image
OUT = '/Users/jesusaa/Desktop/mpcs-51238-assignment-1/v25/assets/st/'
BAYER = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16

class Scene:
    """a picture painted in values (one channel) or colours (three), with soft masks"""
    def __init__(self, w, h, colour=False):
        self.w, self.h = w, h
        self.a = np.zeros((h, w, 3 if colour else 1), dtype=np.float32)
        self.yy, self.xx = np.mgrid[0:h, 0:w].astype(np.float32)
    def put(self, mask, v, alpha=1.0):
        v = np.array(v, dtype=np.float32).reshape(-1)
        m = (mask.astype(np.float32) * alpha)[..., None]
        if np.ndim(v) and v.size == 1: v = v[0]
        self.a = self.a * (1 - m) + m * (v if np.ndim(v) else v)
    def field(self, fn):
        """every pixel set from fn(x, y) (arrays), e.g. a gradient"""
        v = fn(self.xx, self.yy)
        if v.ndim == 2: v = v[..., None]
        self.a[:] = np.broadcast_to(v, self.a.shape)
    def rect(self, x0, y0, x1, y1): return (self.xx >= x0) & (self.xx <= x1) & (self.yy >= y0) & (self.yy <= y1)
    def ell(self, cx, cy, rx, ry): return ((self.xx - cx) / rx) ** 2 + ((self.yy - cy) / ry) ** 2 <= 1
    def poly(self, pts):
        from PIL import ImageDraw
        m = Image.new('L', (self.w, self.h), 0); ImageDraw.Draw(m).polygon([tuple(p) for p in pts], fill=255)
        return np.array(m) > 127
    def line(self, pts, width=1):
        from PIL import ImageDraw
        m = Image.new('L', (self.w, self.h), 0); ImageDraw.Draw(m).line([tuple(p) for p in pts], fill=255, width=width)
        return np.array(m) > 127
    def below(self, fn): return self.yy >= fn(self.xx)
    def value(self): return self.a

def figure(s, x, y, h, coat, skin, hat=None, legs=None, sit=False, facing=0, arms='down'):
    """a person standing (or sitting), feet at (x, y), h tall: head, neck, shoulders and coat,
    arms, legs; lit from the left (the right side a step darker)"""
    hd = h * 0.13; sh = h * 0.24; top = y - h
    head = s.ell(x + facing * 0.6, top + hd * 0.55, hd * 0.42, hd * 0.55)
    body_top, body_bot = top + hd * 1.05, y - (h * 0.2 if sit else h * 0.47)
    torso = s.poly([(x - sh * 0.5, body_top + 1), (x + sh * 0.5, body_top + 1), (x + sh * 0.55, body_bot), (x - sh * 0.55, body_bot)])
    legs = legs if legs is not None else coat
    if sit:
        s.put(s.poly([(x - sh * 0.5, body_bot - 1), (x + sh * 1.3, body_bot - 1), (x + sh * 1.3, body_bot + 2), (x - sh * 0.5, body_bot + 2)]), legs)
        s.put(s.rect(x + sh * 1.1, body_bot, x + sh * 1.3, y), legs)
    else:
        s.put(s.poly([(x - sh * 0.45, body_bot - 1), (x - 0.5, body_bot - 1), (x - 1, y), (x - sh * 0.4, y)]), legs)
        s.put(s.poly([(x + 0.5, body_bot - 1), (x + sh * 0.45, body_bot - 1), (x + sh * 0.4, y), (x + 1, y)]), legs)
    s.put(torso, coat)
    s.put(torso & (s.xx > x + sh * 0.15), np.array(coat) * 0.72 if np.ndim(coat) else coat * 0.72)
    if arms == 'down':
        for side in (-1, 1):
            s.put(s.line([(x + side * sh * 0.52, body_top + 2), (x + side * sh * 0.62, body_top + h * 0.33)], max(1, int(h * 0.06))), coat)
    s.put(s.rect(x - hd * 0.18, top + hd * 0.9, x + hd * 0.18, body_top + 1), skin)
    s.put(head, skin)
    s.put(head & (s.xx > x + facing * 0.6 + hd * 0.12), np.array(skin) * 0.78 if np.ndim(skin) else skin * 0.78)
    if hat is not None:
        s.put(s.ell(x + facing * 0.6, top + hd * 0.18, hd * 0.6, hd * 0.2), hat)
        s.put(s.ell(x + facing * 0.6, top + hd * 0.05, hd * 0.38, hd * 0.3), hat)

# ---------------------------------------------------------------- the black-and-white prints
W, H = 192, 144
def bw_tram(rnd):
    # the last tram home: a wet street at night, the tram's windows and their streaks on the road
    s = Scene(W, H)
    s.field(lambda x, y: 0.05 + 0.10 * (1 - y / 70).clip(0, 1))
    for x0, w, h in ((0, 30, 74), (32, 26, 96), (60, 40, 66), (102, 22, 88), (126, 34, 70), (162, 30, 82)):
        s.put(s.rect(x0, 92 - h, x0 + w, 92), 0.1 + 0.02 * (x0 % 3))
        for wy in range(92 - h + 6, 88, 9):
            for wx in range(x0 + 4, x0 + w - 4, 8):
                if rnd.random() < 0.35: s.put(s.rect(wx, wy, wx + 3, wy + 4), 0.55 + rnd.random() * 0.3)
    s.put(s.rect(0, 92, W, H), 0.12)
    # the tram: its body, the lit windows, its pole to the wire
    s.put(s.rect(46, 58, 146, 94), 0.42); s.put(s.rect(46, 58, 146, 61), 0.6); s.put(s.rect(46, 90, 146, 94), 0.2)
    for k in range(9): s.put(s.rect(51 + k * 10.6, 66, 58 + k * 10.6, 79), 0.92)
    for k in range(4): s.put(s.rect(58 + k * 26, 69, 60 + k * 26, 76), 0.25)        # passengers
    s.put(s.line([(96, 58), (108, 24)], 1), 0.5); s.put(s.line([(0, 24), (192, 20)], 1), 0.35)
    s.put(s.ell(48, 86, 3, 3), 1.0); s.put(s.ell(144, 86, 2.5, 2.5), 0.7)
    # their streaks on the wet road, broken by the setts
    for k in range(9):
        x = 51 + k * 10.6
        for y in range(98, 140, 2):
            if (y // 2 + k) % 3: s.put(s.rect(x, y, x + 6, y), 0.75 - (y - 98) * 0.013)
    for y in range(96, H, 6):
        s.put(s.line([(0, y), (W, y + 1)], 1), 0.08)
    # a street lamp and its halo, a figure under it
    s.put(s.rect(14, 40, 15, 96), 0.3); s.put(s.ell(15, 38, 4, 3), 1.0)
    s.put(s.ell(15, 40, 16, 14), 0.9, alpha=0.18)
    figure(s, 22, 96, 26, 0.16, 0.6, hat=0.1)
    return s, 'The last tram home, the street still wet'

def bw_ferry(rnd):
    # a woman in a headscarf at a ferry's rail, the morning's water and the far shore behind
    s = Scene(W, H)
    s.field(lambda x, y: 0.92 - 0.25 * (y / 54).clip(0, 1))
    s.put(s.poly([(0, 58), (30, 48), (60, 54), (98, 42), (140, 52), (192, 46), (192, 64), (0, 64)]), 0.55)
    s.put(s.poly([(0, 60), (40, 56), (100, 58), (150, 54), (192, 58), (192, 66), (0, 66)]), 0.45)
    s.field_water = None
    water = s.rect(0, 64, W, H)
    s.put(water, 0.66)
    for k in range(70):
        x, y = rnd.uniform(0, W), rnd.uniform(66, 136); L = rnd.uniform(4, 14)
        s.put(s.line([(x, y), (x + L, y)], 1), 0.85 if rnd.random() < 0.6 else 0.5)
    # the rail and its stanchions
    s.put(s.rect(0, 108, W, 111), 0.12); s.put(s.rect(0, 122, W, 123), 0.2)
    for x in range(6, W, 22): s.put(s.rect(x, 108, x + 2, H), 0.12)
    # her: head and shoulders from behind her left, the scarf's knot and its loose end in the wind
    s.put(s.poly([(70, 144), (78, 104), (100, 92), (128, 96), (138, 144)]), 0.24)
    s.put(s.poly([(112, 98), (128, 96), (138, 144), (118, 144)]), 0.16)
    s.put(s.ell(104, 70, 17, 22), 0.78)
    s.put(s.ell(104, 70, 17, 22) & (s.xx > 108), 0.62)
    s.put(s.poly([(84, 66), (92, 46), (110, 42), (124, 52), (126, 80), (118, 70), (112, 58), (96, 60), (90, 78)]), 0.14)
    s.put(s.poly([(124, 60), (154, 66), (148, 76), (126, 74)]), 0.2)
    s.put(s.poly([(150, 66), (168, 62), (160, 74)]), 0.26)
    s.put(s.rect(98, 82, 104, 83), 0.4); s.put(s.rect(94, 70, 96, 71), 0.3); s.put(s.rect(106, 70, 108, 71), 0.3)
    return s, 'On the morning ferry, the wind off the water'

def bw_chess(rnd):
    # two old men at chess in a park, a plane tree's dappled shade, a third standing to watch
    s = Scene(W, H)
    s.field(lambda x, y: 0.78 - 0.1 * (y / H))
    for k in range(40):
        s.put(s.ell(rnd.uniform(-10, 200), rnd.uniform(-10, 54), rnd.uniform(10, 24), rnd.uniform(8, 16)), rnd.choice([0.2, 0.28, 0.36]))
    s.put(s.poly([(90, 0), (98, 0), (102, 104), (86, 104)]), 0.3)
    for y in range(0, 104, 3):
        for x in (88, 92, 96):
            if rnd.random() < 0.4: s.put(s.rect(x, y, x + 2, y + 1), rnd.choice([0.5, 0.6]))
    s.put(s.rect(0, 100, W, H), 0.6)
    for k in range(120): s.put(s.ell(rnd.uniform(0, W), rnd.uniform(102, 144), rnd.uniform(1, 3), 1), rnd.choice([0.4, 0.75]))
    # the table and its board
    s.put(s.rect(64, 92, 128, 96), 0.16); s.put(s.rect(70, 96, 72, 124), 0.14); s.put(s.rect(120, 96, 122, 124), 0.14)
    for i in range(8):
        for j in range(2): s.put(s.rect(74 + i * 6, 90 - j * 2, 79 + i * 6, 91 - j * 2), 0.9 if (i + j) % 2 else 0.2)
    for x, v in ((80, 0.95), (88, 0.1), (100, 0.95), (110, 0.1)): s.put(s.rect(x, 85, x + 2, 89), v)
    # the players, seated each side, and the one who watches
    figure(s, 46, 124, 48, 0.22, 0.62, hat=0.12, sit=True, legs=0.3)
    figure(s, 150, 124, 48, 0.38, 0.66, sit=True, legs=0.2, facing=-1)
    figure(s, 172, 126, 56, 0.18, 0.6, hat=0.1)
    s.put(s.rect(26, 104, 60, 108), 0.2); s.put(s.rect(138, 104, 172, 108), 0.2)
    return s, 'Chess under the plane trees, Sunday'

def bw_lake(rnd):
    # a mountain lake: snow on the peaks, their reflection broken by a breeze, a figure on the jetty
    s = Scene(W, H)
    s.field(lambda x, y: 0.74 + 0.18 * (y / 40).clip(0, 1))
    for k in range(6): s.put(s.ell(rnd.uniform(0, W), rnd.uniform(6, 30), rnd.uniform(18, 34), rnd.uniform(4, 8)), 0.96, alpha=0.6)
    ridge = lambda x: 72 - 34 * np.exp(-((x - 64) / 26) ** 2) - 44 * np.exp(-((x - 128) / 22) ** 2) - 20 * np.exp(-((x - 178) / 18) ** 2) + 4 * np.sin(x / 5)
    s.put(s.below(ridge) & (s.yy < 84), 0.44)
    slope = ridge(s.xx + 1) - ridge(s.xx)                 # the flanks facing away from the light, darker
    s.put(s.below(ridge) & (s.yy < 84) & (slope < -0.2), 0.32)
    s.put(s.below(ridge) & (s.yy < ridge(s.xx) + 7) & (ridge(s.xx) < 48), 0.96)
    s.put(s.below(ridge) & (s.yy < ridge(s.xx) + 7) & (ridge(s.xx) < 48) & (slope < -0.2), 0.78)
    s.put(s.below(lambda x: 76 + 3 * np.sin(x / 9)) & (s.yy < 86), 0.18)
    for k in range(40): s.put(s.poly([(x0 := rnd.uniform(0, W), 86), (x0 + 3, 70 + rnd.uniform(0, 8)), (x0 + 6, 86)]), 0.12)
    s.put(s.rect(0, 86, W, H), 0.62)
    # the reflection: the shore's trees, then the ridge again upside down, darker than itself,
    # its snow at the far end, broken by the breeze into lines
    xs = s.xx[0]
    depth = (86 - ridge(xs)) * 0.75
    for y in range(87, 140):
        r = (y - 87) / depth                                   # 0 at the shore, 1 at the peak's reflection
        row = np.where(r < 0.12, 0.2, np.where(r < 0.9, 0.38, np.where((r < 1) & (depth > 38 * 0.75), 0.62, 0.66)))
        brk = ((np.arange(W) + (y * 7) % 11) % 9 < 2) & (y % 3 == 0)
        row = np.where(brk, 0.72, row)
        s.a[y, :, 0] = row
    s.put(s.rect(120, 116, W, 119), 0.2)
    for x in (126, 146, 166, 186): s.put(s.rect(x, 119, x + 1, 132), 0.15)
    figure(s, 176, 116, 22, 0.12, 0.5, hat=0.1)
    return s, 'The lake above the village, before the weather turned'

def bw_machine_room(rnd):
    # the machine room after midnight: tape drives in a row, the operator at the console
    s = Scene(W, H)
    s.field(lambda x, y: 0.3 + 0.08 * (y / H))
    s.put(s.rect(0, 0, W, 10), 0.85)                                     # the ceiling's lights
    for x in range(0, W, 16): s.put(s.rect(x + 2, 2, x + 12, 6), 1.0)
    for k in range(6):
        x = 4 + k * 31
        s.put(s.rect(x, 18, x + 26, 92), 0.72); s.put(s.rect(x + 25, 18, x + 26, 92), 0.5)
        s.put(s.rect(x + 2, 20, x + 24, 56), 0.2)
        for cx in (x + 7, x + 19):
            s.put(s.ell(cx, 30, 5, 5), 0.9); s.put(s.ell(cx, 30, 2, 2), 0.2)
            for a in range(3):
                t = a * 2.09 + k; s.put(s.line([(cx, 30), (cx + 4 * math.cos(t), 30 + 4 * math.sin(t))], 1), 0.35)
        s.put(s.rect(x + 4, 44, x + 22, 50), 0.6)
        for j in range(4): s.put(s.rect(x + 4 + j * 5, 62, x + 6 + j * 5, 64), 0.95 if rnd.random() < 0.5 else 0.4)
    s.put(s.rect(0, 92, W, H), 0.5)
    for k in range(9): s.put(s.line([(96 + (k - 4) * 22, 92), (96 + (k - 4) * 60, H)], 1), 0.42)
    # the console, its lamps and switches, the operator at it seen from behind
    s.put(s.poly([(40, 104), (152, 104), (160, 122), (32, 122)]), 0.8); s.put(s.rect(32, 122, 160, 130), 0.55)
    for k in range(18): s.put(s.rect(44 + k * 6, 108, 46 + k * 6, 110), 1.0 if rnd.random() < 0.4 else 0.3)
    for k in range(12): s.put(s.rect(48 + k * 8, 114, 50 + k * 8, 118), 0.25)
    figure(s, 96, 144, 54, 0.22, 0.55, sit=False)
    s.put(s.ell(96, 94, 8, 6), 0.12)                                       # her hair, pinned up
    s.put(s.rect(70, 130, 122, 144), 0.18)                                  # the chair's back
    return s, 'The machine room after midnight, the operator at the console'

def bw_lighthouse(rnd):
    # the light at the point in fog: its beam across the grey, the headland black, the sea pale
    s = Scene(W, H)
    s.field(lambda x, y: 0.7 + 0.12 * np.sin(x / 40 + y / 30))
    s.put(s.poly([(116, 34), (192, 6), (192, 30), (118, 40)]), 0.96, alpha=0.8)
    s.put(s.poly([(100, 34), (0, 12), (0, 28), (98, 40)]), 0.92, alpha=0.5)
    s.put(s.poly([(100, 32), (116, 32), (114, 92), (102, 92)]), 0.94)
    for y0 in (48, 70): s.put(s.rect(100, y0, 116, y0 + 8) & s.poly([(100, 32), (116, 32), (114, 92), (102, 92)]), 0.2)
    s.put(s.rect(98, 26, 118, 32), 0.15); s.put(s.rect(102, 18, 114, 26), 0.95); s.put(s.poly([(100, 18), (108, 10), (116, 18)]), 0.12)
    s.put(s.rect(118, 90, 128, 96), 0.3)
    s.put(s.poly([(56, 144), (70, 98), (96, 92), (150, 90), (192, 106), (192, 144)]), 0.12)
    s.put(s.poly([(0, 144), (0, 118), (36, 112), (60, 144)]), 0.3)
    s.put(s.rect(0, 120, W, H) & ~s.poly([(56, 144), (70, 98), (96, 92), (150, 90), (192, 106), (192, 144)]) & ~s.poly([(0, 144), (0, 118), (36, 112), (60, 144)]), 0.8)
    for k in range(30):
        x, y = rnd.uniform(0, 70), rnd.uniform(122, 142); s.put(s.line([(x, y), (x + rnd.uniform(4, 12), y)], 1), 0.95)
    return s, 'The light at the point, in fog'

def bw_platform(rnd):
    # a station platform under its iron roof, travellers with their cases, the train's steam
    s = Scene(W, H)
    s.field(lambda x, y: 0.5 + 0.35 * (y / 50).clip(0, 1) * (y < 60))
    s.put(s.rect(0, 0, W, 14), 0.2)
    for k in range(14): s.put(s.line([(k * 15, 0), (96, 20)], 1), 0.08)
    s.put(s.rect(0, 14, W, 18), 0.15)
    for x in range(0, W, 24): s.put(s.rect(x, 18, x + 2, 104), 0.18)
    s.put(s.ell(140, 40, 50, 30), 0.97, alpha=0.9); s.put(s.ell(170, 26, 36, 22), 0.9, alpha=0.8); s.put(s.ell(110, 54, 30, 18), 0.95, alpha=0.7)
    # the train at the left: its carriages, windows lit
    s.put(s.rect(0, 50, 88, 98), 0.12); s.put(s.rect(0, 50, 88, 53), 0.3)
    for x in range(4, 84, 14): s.put(s.rect(x, 60, x + 9, 72), 0.62)
    s.put(s.rect(0, 98, 92, 104), 0.06)
    s.put(s.rect(0, 104, W, H), 0.6); s.put(s.rect(0, 104, W, 106), 0.85)
    for k in range(30): s.put(s.rect(rnd.uniform(90, W), rnd.uniform(108, 140), 1, 1) if False else s.ell(rnd.uniform(90, W), rnd.uniform(108, 142), 1.5, 0.8), 0.5)
    for x, h, c, hat in ((104, 50, 0.1, 0.06), (122, 46, 0.3, None), (146, 52, 0.14, 0.08), (170, 44, 0.24, None)):
        figure(s, x, 136, h, c, 0.62, hat=hat)
    s.put(s.rect(112, 120, 120, 128), 0.25); s.put(s.rect(154, 122, 162, 130), 0.45)
    s.put(s.rect(40, 6, 60, 14), 0.9); s.put(s.rect(49, 14, 50, 20), 0.15)
    return s, 'Waiting for the night train, with the steam coming in'

# ---------------------------------------------------------------- the Polaroids (faded colour)
P = 128
def C(*c): return np.array(c, dtype=np.float32) / 255

def pol_beach(rnd):
    s = Scene(P, P, True)
    s.field(lambda x, y: (C(110, 172, 214) * (1 - (y / 60).clip(0, 1))[..., None] + C(196, 222, 228) * (y / 60).clip(0, 1)[..., None]))
    s.put(s.ell(98, 18, 9, 9), C(255, 244, 196))
    s.put(s.rect(0, 58, P, 76), C(38, 108, 152)); s.put(s.rect(0, 58, P, 59), C(90, 160, 196))
    for k in range(20): x = rnd.uniform(0, P); y = rnd.uniform(62, 75); s.put(s.line([(x, y), (x + rnd.uniform(4, 10), y)], 1), C(220, 238, 244))
    s.put(s.rect(0, 74, P, P), C(226, 204, 158))
    for k in range(80): s.put(s.ell(rnd.uniform(0, P), rnd.uniform(78, P), 1, 0.6), C(206, 182, 136))
    for k, c in enumerate((C(204, 64, 52), C(56, 106, 170), C(232, 190, 62))):
        x = 14 + k * 36
        s.put(s.rect(x, 62, x + 24, 96), c)
        for y in range(64, 96, 6): s.put(s.rect(x, y, x + 24, y + 2), C(244, 238, 226))
        s.put(s.poly([(x - 3, 62), (x + 12, 50), (x + 27, 62)]), C(240, 232, 220)); s.put(s.poly([(x + 12, 50), (x + 27, 62), (x + 20, 62)]), C(200, 192, 180))
        s.put(s.rect(x + 8, 82, x + 15, 96), C(70, 46, 34)); s.put(s.rect(x + 24, 64, x + 26, 98), c * 0.7)
    figure(s, 112, 112, 26, C(220, 70, 70), C(232, 180, 140))
    return s, 'The huts at the end of the beach'

def pol_rooftop(rnd):
    s = Scene(P, P, True)
    s.field(lambda x, y: C(232, 104, 86) * (1 - (y / 74).clip(0, 1))[..., None] + C(252, 196, 120) * (y / 74).clip(0, 1)[..., None])
    s.put(s.ell(84, 70, 16, 16), C(255, 226, 150)); s.put(s.ell(84, 70, 26, 26), C(255, 214, 140), alpha=0.35)
    for x0, w, h in ((0, 16, 34), (18, 12, 48), (32, 18, 28), (52, 10, 40), (64, 14, 22), (82, 18, 36), (102, 12, 50), (116, 12, 30)):
        s.put(s.rect(x0, 82 - h, x0 + w, 82), C(92, 56, 82))
        for wy in range(82 - h + 4, 80, 6):
            for wx in range(x0 + 2, x0 + w - 2, 4):
                if rnd.random() < 0.25: s.put(s.rect(wx, wy, wx + 1, wy + 2), C(255, 208, 120))
    s.put(s.rect(0, 82, P, P), C(118, 78, 70)); s.put(s.rect(0, 82, P, 84), C(170, 116, 92))
    for x in range(0, P, 10): s.put(s.rect(x, 84, x + 1, P), C(100, 64, 60))
    figure(s, 50, 120, 44, C(40, 62, 112), C(236, 186, 150), legs=C(40, 40, 52))
    figure(s, 70, 120, 42, C(156, 42, 52), C(226, 176, 140), legs=C(60, 50, 50))
    s.put(s.ell(60, 92, 3, 2), C(236, 186, 150))
    return s, 'Up on the roof, the evening it finally stopped raining'

def pol_balloon(rnd):
    s = Scene(P, P, True)
    s.field(lambda x, y: C(140, 192, 232) * (1 - (y / 80).clip(0, 1))[..., None] + C(216, 234, 242) * (y / 80).clip(0, 1)[..., None])
    for k in range(5): s.put(s.ell(rnd.uniform(0, P), rnd.uniform(8, 40), rnd.uniform(12, 22), rnd.uniform(4, 7)), C(248, 250, 252), alpha=0.8)
    # the tent, striped, its flag
    s.put(s.poly([(70, 86), (98, 40), (126, 86)]), C(240, 228, 196))
    for k in range(6): s.put(s.poly([(98, 40), (70 + k * 11, 86), (75 + k * 11, 86)]), C(200, 64, 64))
    s.put(s.rect(97, 30, 98, 40), C(80, 60, 50)); s.put(s.poly([(98, 30), (108, 33), (98, 36)]), C(230, 190, 60))
    s.put(s.rect(0, 86, P, P), C(104, 158, 76))
    for k in range(60): s.put(s.line([(x := rnd.uniform(0, P), y := rnd.uniform(88, P)), (x + 1, y - 2)], 1), C(78, 130, 60))
    # the balloon, its string to the child's hand, the grown-up beside
    s.put(s.ell(30, 26, 12, 14), C(222, 40, 58)); s.put(s.ell(26, 21, 3, 4), C(250, 150, 160)); s.put(s.poly([(28, 39), (32, 39), (30, 42)]), C(180, 30, 46))
    s.put(s.line([(30, 42), (40, 64), (44, 88)], 1), C(70, 70, 70))
    figure(s, 44, 118, 32, C(232, 184, 52), C(240, 196, 160), legs=C(60, 90, 150))
    figure(s, 62, 118, 54, C(64, 84, 140), C(230, 186, 150), legs=C(50, 50, 60), hat=C(140, 100, 60))
    return s, 'The fair on the common: the balloon was not lost'

def pol_cafe(rnd):
    s = Scene(P, P, True)
    s.field(lambda x, y: C(204, 200, 186) + 0 * x[..., None])
    for x in range(4, P, 24): s.put(s.rect(x, 12, x + 18, 46), C(150, 162, 172)); s.put(s.rect(x + 1, 13, x + 17, 45), C(196, 214, 224))
    s.put(s.rect(0, 0, P, 6), C(176, 66, 56))
    for x in range(0, P, 8): s.put(s.poly([(x, 6), (x + 4, 12), (x + 8, 6)]), C(244, 238, 226) if (x // 8) % 2 else C(176, 66, 56))
    s.put(s.rect(0, 50, P, 56), C(124, 104, 86))
    # the table from above, the cup, the saucer, the letter and its pen, the light across it
    s.put(s.ell(64, 96, 60, 34), C(232, 228, 218)); s.put(s.ell(64, 96, 56, 31), C(222, 216, 204))
    s.put(s.ell(40, 92, 14, 9), C(250, 248, 244)); s.put(s.ell(40, 91, 8, 5), C(92, 56, 34)); s.put(s.ell(38, 90, 3, 2), C(150, 100, 64))
    s.put(s.rect(54, 89, 58, 92), C(250, 248, 244))
    s.put(s.poly([(70, 82), (102, 78), (106, 104), (74, 108)]), C(246, 242, 232))
    for k in range(6): s.put(s.line([(76, 86 + k * 3.4), (98, 83 + k * 3.4)], 1), C(110, 104, 120))
    s.put(s.line([(96, 108), (112, 96)], 2), C(30, 40, 90))
    return s, 'A coffee on the square, and the letter home'

def pol_cellar(rnd):
    s = Scene(P, P, True)
    s.field(lambda x, y: C(58, 32, 38) * (1 - (y / P))[..., None] + C(26, 16, 20) * (y / P)[..., None])
    for y in range(0, 90, 8):
        for x in range((y // 8 % 2) * 8, P, 16): s.put(s.rect(x, y, x + 14, y + 6), C(74, 42, 44), alpha=0.6)
    s.put(s.poly([(46, 0), (82, 0), (110, 112), (18, 112)]), C(196, 150, 110), alpha=0.35)
    s.put(s.rect(0, 108, P, P), C(48, 28, 26))
    # the piano at the left, the saxophone in the light, the bass at the right
    s.put(s.rect(4, 70, 34, 108), C(30, 22, 22)); s.put(s.rect(4, 70, 34, 74), C(70, 50, 44))
    figure(s, 26, 108, 40, C(30, 34, 54), C(220, 170, 134), sit=True, legs=C(24, 24, 34))
    figure(s, 64, 110, 52, C(150, 44, 44), C(230, 180, 140), legs=C(40, 30, 30))
    s.put(s.line([(66, 74), (70, 92), (66, 98)], 3), C(220, 180, 80)); s.put(s.ell(65, 99, 4, 3), C(236, 196, 90))
    figure(s, 100, 110, 50, C(40, 66, 46), C(214, 166, 126), legs=C(30, 30, 30))
    s.put(s.ell(110, 92, 9, 14), C(170, 110, 60)); s.put(s.ell(110, 80, 6, 8), C(170, 110, 60)); s.put(s.rect(109, 46, 111, 74), C(60, 40, 30))
    return s, 'The trio in the cellar, the night the bass came'

PRINTS = [bw_tram, bw_ferry, bw_chess, bw_lake, bw_machine_room, bw_lighthouse, bw_platform]
POLAROIDS = [pol_beach, pol_rooftop, pol_balloon, pol_cafe, pol_cellar]

def greys(s, seed):
    """the print cut to nine greys by an ordered dither, a grain over it"""
    a = s.value()[..., 0]
    h, w = a.shape; yy, xx = np.mgrid[0:h, 0:w]
    rnd = np.random.RandomState(seed)
    v = np.clip(np.floor(a * 8 + BAYER[yy % 4, xx % 4] + rnd.uniform(-0.1, 0.1, a.shape)), 0, 8) / 8
    g = (14 + v * 226).astype(np.uint8)
    return Image.fromarray(np.stack([g, g, g], -1))

def faded(s, seed):
    """the Polaroid's colours: the blacks lifted, a warm cast, cut to 24 colours by a dither"""
    a = s.value() * 255
    a = 30 + a * (1 - 30 / 255) + np.array([16, 6, -10])
    h, w = a.shape[:2]; yy, xx = np.mgrid[0:h, 0:w]
    a = a + (BAYER[yy % 4, xx % 4][..., None] - 0.5) * 18
    im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    return im.quantize(colors=24, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE).convert('RGB')

def mount_print(im):
    out = Image.new('RGB', (W + 16, H + 16), (238, 236, 228)); out.paste(im, (8, 8)); return out
def mount_polaroid(im):
    out = Image.new('RGB', (P + 12, P + 40), (240, 238, 230)); out.paste(im, (6, 6)); return out

if __name__ == '__main__':
    caps = []
    for i, fn in enumerate(PRINTS):
        sc, cap = fn(random.Random(100 + i)); mount_print(greys(sc, i)).save(OUT + 'album-p%d.png' % (i + 1), optimize=True); caps.append(('album-p%d.png' % (i + 1), cap))
    for i, fn in enumerate(POLAROIDS):
        sc, cap = fn(random.Random(200 + i)); mount_polaroid(faded(sc, i)).save(OUT + 'album-q%d.png' % (i + 1), optimize=True); caps.append(('album-q%d.png' % (i + 1), cap))
    sheet = Image.new('RGB', (4 * 214, 3 * 174), (30, 30, 30))
    for i, (n, _) in enumerate(caps):
        sheet.paste(Image.open(OUT + n), ((i % 4) * 214, (i // 4) * 174))
    sheet.save('album.png')
    for n, c in caps: print(n, '|', c)
