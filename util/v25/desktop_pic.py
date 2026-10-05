# The computer's desk picture, 800 x 570, drawn in pixels: a night at Persepolis for the
# Polytope of 1971. The Milky Way across the sky and a low moon; searchlight beams crossing
# over Kuh-e Rahmat, the mountain behind the terrace, its rock facets and the cross-shaped
# royal tombs cut in its face lit from below; the torch-bearers' river of fire climbing it in
# switchbacks; and the terrace in silhouette against its bonfires: the stepped merlons of its
# parapet, the great double stair, the Gate's piers with their winged bulls, and the Apadana's
# tall columns, a few still standing with their bull capitals; the audience along its edge.
import os as _os; UTIL = _os.path.normpath(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..')); REPO = _os.path.dirname(UTIL)
import math, random
import numpy as np
from pixart import Pic, near
OUT = REPO + '/v25/assets/pics/desktop.png'
W, H = 800, 570
rnd = random.Random(1971)
NIGHT0, NIGHT1, NIGHT2, NIGHT3 = (19, 16, 14), (30, 29, 27), (43, 69, 96), (74, 104, 134)
ROCK0, ROCK1, ROCK2, ROCK3 = (30, 29, 27), (61, 43, 32), (79, 73, 67), (98, 96, 89)
FIRE0, FIRE1, FIRE2, FIRE3 = (116, 62, 43), (220, 110, 80), (240, 196, 106), (255, 232, 170)
STAR, STAR2, MOON, MOON_D = (250, 250, 246), (201, 199, 191), (239, 236, 225), (198, 190, 173)
BEAM, BEAM2 = (111, 140, 168), (150, 180, 205)
SIL = (19, 16, 14)
p = Pic(W, H, NIGHT0)
yy, xx = np.mgrid[0:H, 0:W]
ALL = np.ones((H, W), bool)

# ---------------- the sky: night deepening upward, a glow over the horizon from the fires
t = np.clip((yy - 40) / 360, 0, 1)
p.dither(ALL, NIGHT0, NIGHT1, np.clip(t * 1.6, 0, 1))
p.dither(yy > 200, NIGHT1, NIGHT2, np.clip((yy - 200) / 260, 0, 1) * 0.85)
# the Milky Way: a broad band falling from the upper right to the left, its cloud dithered in
# two blues with dark lanes along it, and stars thickest along its spine
def band(x, y):
    # distance from the band's spine, which runs from (820, 40) to (-20, 300)
    ax, ay, bx, by = 820, 30, -20, 330
    vx, vy = bx - ax, by - ay; L = math.hypot(vx, vy)
    return np.abs((x - ax) * vy - (y - ay) * vx) / L
d = band(xx, yy)
cloud = np.clip(1 - d / 70, 0, 1) ** 1.5
noise = np.random.RandomState(3).rand(H // 4 + 1, W // 4 + 1)
nz = np.kron(noise, np.ones((4, 4)))[:H, :W]
lane = np.abs(band(xx, yy - 14 + 9 * np.sin(xx / 60))) < 6
sky = yy < 330
p.dither(sky & (cloud > 0.05) & ~lane, NIGHT1, NIGHT2, np.clip(cloud * (0.55 + 0.6 * nz), 0, 1))
p.dither(sky & (cloud > 0.45) & ~lane, NIGHT2, NIGHT3, np.clip((cloud - 0.45) * 1.4 * (0.6 + 0.6 * nz), 0, 1))
for k in range(1400):
    x, y = rnd.randrange(W), rnd.randrange(0, 360)
    near_band = math.exp(-float(band(x, y)) / 50)
    if rnd.random() < 0.25 + 0.75 * near_band:
        p.px(x, y, STAR if rnd.random() < 0.35 else STAR2)
for k in range(28):     # a few bright stars, crossed
    x, y = rnd.randrange(20, W - 20), rnd.randrange(10, 300)
    p.px(x, y, STAR); p.px(x - 1, y, STAR2); p.px(x + 1, y, STAR2); p.px(x, y - 1, STAR2); p.px(x, y + 1, STAR2)

# ---------------- the moon, low at the left, a ring of its light round it
mx, my, mr = 96, 112, 22
r = np.hypot(xx - mx, yy - my)
p.dither((r < mr + 26) & (r >= mr), NIGHT1, NIGHT2, np.clip(1 - (r - mr) / 26, 0, 1) * 0.7)
p.fill(r < mr, MOON)
for cx, cy, rr in ((-7, -5, 6), (5, 3, 5), (-2, 9, 4), (8, -8, 3), (-10, 6, 3)):
    p.fill(np.hypot(xx - mx - cx, yy - my - cy) < rr, MOON_D)
p.dither((r < mr) & (xx - mx > mr * 0.45), MOON, MOON_D, 0.5)

# ---------------- the searchlights: beams from the terrace, crossing over the mountain
def beam(x0, y0, ang, level):
    a = math.radians(ang)
    ux, uy = math.sin(a), -math.cos(a)
    along = (xx - x0) * ux + (yy - y0) * uy
    across = np.abs((xx - x0) * uy - (yy - y0) * ux)
    w = 2 + along * 0.045                       # a beam widens slowly as it climbs
    m = (along > 0) & (across < w) & (yy < y0)
    edge = np.clip(1 - across / np.maximum(w, 1), 0, 1)
    fade = np.clip(1 - along / 900, 0, 1) * level * edge ** 0.8
    under = p.a.copy()
    p.dither(m, NIGHT2, BEAM, fade)
    # where the beam is faint, the sky shows through it
    thin = m & (fade < 0.12)
    p.a[thin] = under[thin]
    core = m & (across < w * 0.3) & (along < 300)
    p.dither(core, BEAM, BEAM2, np.clip(1 - along / 300, 0, 1) * 0.7)
for x0, ang in ((300, 24), (470, -22), (560, 12), (230, -16)):
    beam(x0, 470, ang, 0.42)

# ---------------- Kuh-e Rahmat: the mountain behind the terrace
ridge = [(-10, 400), (90, 360), (170, 330), (240, 300), (300, 262), (350, 246), (400, 238), (450, 252), (520, 276), (600, 300), (680, 330), (760, 352), (820, 370)]
p.poly(ridge + [(820, 490), (-10, 490)], ROCK0)
# its face: broad planes of rock in cool greys, the strata running across them, the foot warmed by the fire
RIDGE_Y = np.interp(xx, [q[0] for q in ridge], [q[1] for q in ridge])
face = yy > RIDGE_Y + 1
depth = np.clip((yy - RIDGE_Y) / 180, 0, 1)
p.dither(face, ROCK0, (60, 66, 66), np.clip(0.15 + 0.35 * np.cos(xx / 37.0 + yy / 23.0) ** 2 * (1 - depth), 0, 1))
strata = face & (((yy - RIDGE_Y * 0.4 + 4 * np.sin(xx / 41.0)).astype(int) % 23) == 0)
p.fill(strata & (xx % 2 == 0), (60, 66, 66))
p.dither(face & (depth > 0.55), ROCK0, ROCK1, np.clip((depth - 0.55) * 1.4, 0, 0.55))
# the ridge line, lit faintly by the moon
for x in range(W):
    y = int(np.interp(x, [q[0] for q in ridge], [q[1] for q in ridge]))
    p.px(x, y, ROCK2 if x % 3 else ROCK1)
# the royal tombs: cross-shaped façades cut in the face, their porticoes of four columns
def tomb(cx, cy, s):
    p.rect(cx - 3 * s, cy - 7 * s, cx + 3 * s, cy + 7 * s, (60, 66, 66))   # the upright of the cross
    p.rect(cx - 7 * s, cy - 2 * s, cx + 7 * s, cy + 2 * s, (60, 66, 66))   # its arms, the portico
    p.rect(cx - 6 * s, cy - 1 * s, cx + 6 * s, cy + 1 * s, ROCK1)
    for k in range(4): p.rect(cx - 5 * s + k * 3 * s, cy - s, cx - 5 * s + k * 3 * s, cy + 2 * s, ROCK2)
    p.rect(cx - 1, cy + 2 * s + 1, cx + 1, cy + 3 * s, SIL)               # the door
    p.rect(cx - 2 * s, cy - 6 * s, cx + 2 * s, cy - 3 * s, ROCK1)         # the relief over it
for cx, cy, s in ((300, 330, 2), (410, 300, 2), (520, 340, 2)):
    tomb(cx, cy, s)

# ---------------- the torch-bearers: a river of fire climbing the mountain in switchbacks
path = []
x, y, dirn = 660, 465, -1
for leg in range(9):
    span = 210 - leg * 14
    for k in range(int(span / 3)):
        x += dirn * 3; y -= 0.55 + leg * 0.03
        path.append((x, y))
    for k in range(6): y -= 2; path.append((x, y))
    dirn = -dirn
    if y < 262: break
RX, RY = [q[0] for q in ridge], [q[1] for q in ridge]
path = [(x, y) for (x, y) in path if y > np.interp(x, RX, RY) + 14]     # the path stays on the mountain
for i, (x, y) in enumerate(path):
    if i % 2 == 0:
        p.px(x, y, FIRE3 if i % 6 == 0 else FIRE2)
        p.px(x, y + 1, FIRE1)
    else:
        p.px(x, y, FIRE0)
# the glow the torches throw on the rock round them
glow = np.zeros((H, W))
for (x, y) in path[::3]:
    glow = np.maximum(glow, np.clip(1 - np.hypot(xx - x, (yy - y) * 1.6) / 10, 0, 1))
gm = (glow > 0.05) & (p.a == np.array(near(ROCK0))).all(-1)
p.dither(gm, ROCK0, FIRE0, glow * 0.6)

# ---------------- the terrace: its parapet of stepped merlons against the bonfires' glow
TY = 470                                   # the terrace's top edge
# the fires' glow on the air and the rock over the terrace
fires = [(70, TY + 2), (215, TY + 2), (380, TY + 2), (540, TY + 2), (700, TY + 2)]
glow = np.zeros((H, W))
for fx, fy in fires:
    glow = np.maximum(glow, np.clip(1 - np.hypot(xx - fx, (yy - fy) * 1.7) / 70, 0, 1))
gm = (glow > 0.02) & (yy < TY)
cur = p.a.copy()
p.dither(gm, (0, 0, 0), FIRE0, glow ** 1.3 * 0.75)
keep = gm & (p.a == np.array(near((0, 0, 0)))).all(-1)
p.a[keep] = cur[keep]
# the Gate of All Nations: two great piers, a winged bull in relief on each
def pier(x0, w, h, face):
    p.rect(x0, TY - h, x0 + w, TY, SIL)
    p.rect(x0 + w - 2, TY - h, x0 + w, TY, ROCK1)        # its edge, catching the fire
    # the bull: a body, a crowned human head, a wing sweeping up and back
    bx, by = x0 + 6, TY - 40
    p.line([(bx, by), (bx + 24, by)], ROCK1, 2)
    p.line([(bx + 2, by), (bx + 2, by + 18)], ROCK1, 2); p.line([(bx + 22, by), (bx + 22, by + 18)], ROCK1, 2)
    hx = bx + 26 if face > 0 else bx - 4
    p.rect(hx - 2, by - 12, hx + 3, by - 2, ROCK1); p.rect(hx - 3, by - 16, hx + 4, by - 13, ROCK2)
    for k in range(5):
        p.line([(bx + 4 + k * 3, by - 1), (bx - 2 + k * 5, by - 26 - k * 3)], ROCK1)
pier(118, 34, 128, 1); pier(176, 34, 128, -1)
# the Apadana's columns: tall and fluted, a few to their full height with a double-bull capital
def column(x, h, full):
    p.rect(x, TY - h, x + 7, TY, SIL)
    p.rect(x + 6, TY - h, x + 7, TY, ROCK1)
    for k in range(1, 3): p.rect(x + k * 2, TY - h + 6, x + k * 2, TY - 6, ROCK0)
    p.rect(x - 2, TY - 6, x + 9, TY, SIL)                 # the bell base
    if full:
        cy = TY - h
        p.rect(x - 8, cy - 8, x + 15, cy - 1, SIL)        # the bulls' backs
        p.rect(x - 12, cy - 12, x - 6, cy - 4, SIL); p.rect(x + 13, cy - 12, x + 19, cy - 4, SIL)   # their heads
        p.px(x - 12, cy - 13, SIL); p.px(x + 19, cy - 13, SIL)
        p.rect(x - 1, cy - 2, x + 8, cy, ROCK1)
for x, h, full in ((262, 150, True), (300, 160, True), (338, 130, False), (380, 165, True), (424, 95, False), (466, 170, True),
                   (510, 140, False), (552, 158, True), (596, 70, False), (640, 150, True)):
    column(x, h, full)
# fallen drums and capitals along the foot
for x in (440, 480, 610, 680, 720):
    p.rect(x, TY - 6, x + 12, TY, SIL)
# the parapet: a band of stepped merlons along the whole terrace
p.rect(0, TY, W, TY + 30, SIL)
p.dither((yy >= TY + 3) & (yy < TY + 30), SIL, ROCK1, 0.22)          # the parapet's face, warm in the firelight
for x in range(-4, W, 14):
    p.rect(x, TY - 6, x + 7, TY, SIL); p.rect(x + 2, TY - 9, x + 5, TY - 6, SIL)
# the great double stair at the left, its flights rising in steps toward each other
for k in range(12):
    p.rect(14 + k * 4, TY + 30 - k * 2.5, 18 + k * 4, TY + 30, SIL)
    p.rect(108 - k * 4, TY + 30 - k * 2.5, 112 - k * 4, TY + 30, SIL)
# ---------------- the bonfires on the terrace's edge
def flame(fx, fy, hgt, wid, col, lean=0):
    # a teardrop: widest at its foot, drawn up to a point that leans a little
    left, right = [], []
    for k in range(17):
        t = k / 16; half = wid * (1 - t) ** 0.75 * (0.75 + 0.25 * math.sin(math.pi * t))
        x = fx + lean * t * t
        left.append((x - half, fy - hgt * t)); right.append((x + half, fy - hgt * t))
    p.poly(left + right[::-1], col)
for fx, fy in fires:
    ln = rnd.uniform(-5, 5)
    flame(fx, fy, 38, 14, FIRE1, ln); flame(fx - 7, fy, 22, 6, FIRE1, ln - 3); flame(fx + 8, fy, 20, 6, FIRE1, ln + 3)
    flame(fx, fy, 26, 9, FIRE2, ln * 0.7); flame(fx, fy, 13, 5, FIRE3, ln * 0.3)
    for k in range(10):
        p.px(fx + rnd.randint(-10, 10), fy - rnd.randint(30, 52), FIRE2 if k % 2 else FIRE1)
    p.rect(fx - 14, fy, fx + 14, fy + 3, FIRE1); p.rect(fx - 9, fy - 1, fx + 9, fy + 1, FIRE2)
    # the fire's light on the parapet in front of it
    lit = (np.hypot(xx - fx, (yy - fy) * 2) < 60) & (yy >= TY) & (yy < TY + 30) & (p.a == np.array(near(SIL))).all(-1)
    p.dither(lit, SIL, FIRE0, np.clip(1 - np.hypot(xx - fx, (yy - fy) * 2) / 60, 0, 1) * 0.7)

# ---------------- the audience, sitting along the foot of the terrace, rimmed by the fires
# the forecourt before the terrace, lit warm by the fires, so the audience stands out on it
p.rect(0, TY + 30, W, H, NIGHT0)
court = (yy >= TY + 30) & (yy < TY + 70)
warm = np.zeros((H, W))
for fx, fy in fires: warm = np.maximum(warm, np.clip(1 - np.abs(xx - fx) / 110, 0, 1))
p.dither(court, ROCK0, ROCK1, np.clip(0.35 + 0.5 * warm - (yy - TY - 30) / 80, 0, 1))
lit1 = court & (warm > 0.55) & (p.a == np.array(near(ROCK1))).all(-1)
p.dither(lit1, ROCK1, FIRE0, np.clip((warm - 0.55) * 1.6, 0, 1) * np.clip(1 - (yy - TY - 30) / 40, 0, 1))
for x in range(rnd.randint(0, 8), W, 16):
    if rnd.random() < 0.15: continue                      # a gap in the crowd
    size = rnd.uniform(1.4, 1.7)
    sh, hw, hr = int(10 * size), int(5 * size), int(3 * size)
    yb = TY + 66 + rnd.randint(-2, 1)
    p.ellipse(x - hw - 1, yb - sh, x + hw + 1, yb + 10, SIL)                 # shoulders
    p.ellipse(x - hr, yb - sh - 2 * hr, x + hr, yb - sh + 2, SIL)             # head
    fl = min(abs(x - fx) for fx, _ in fires)
    if fl < 70:                                                               # the firelight on the crown
        for dx in range(-hr + 1, hr): p.px(x + dx, yb - sh - 2 * hr, FIRE0)
p.rect(0, TY + 68, W, H, SIL)
p.graded().save(OUT, optimize=True)
p.graded().resize((W, H)).save(UTIL + '/v25/desk-new.png')
print('saved')
