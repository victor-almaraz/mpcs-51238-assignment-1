# Hugo Ball reciting at the Cabaret Voltaire, 1916, after the photograph: 240 x 200, drawn in
# pixels. A tall cylindrical hat striped blue and white; a high white collar; a great cape of
# cardboard, gold outside and scarlet within, stiff as wings, folded in pleats; hands in
# cardboard claws; legs in shining blue cardboard tubes. He stands in a spotlight on the
# small stage, a music stand before him with the poem on it.
import os as _os; UTIL = _os.path.normpath(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..')); REPO = _os.path.dirname(UTIL)
import math
import numpy as np
from pixart import Pic, near
OUT = REPO + '/v25/assets/pics/drawing-k.png'
W, H = 240, 200
INK, INK2 = (19, 16, 14), (30, 29, 27)
WALL0, WALL1 = (43, 69, 96), (74, 104, 134)
SPOT0, SPOT1 = (111, 140, 168), (150, 180, 205)
GOLD, GOLD_L, GOLD_D = (201, 154, 46), (240, 196, 106), (168, 119, 83)
RED, RED_D = (181, 70, 43), (116, 62, 43)
BLUE, BLUE_L, BLUE_D = (74, 104, 134), (150, 180, 205), (43, 69, 96)
WHITE, WHITE_D, WHITE_DD = (250, 250, 246), (216, 209, 195), (180, 175, 162)
SKIN, SKIN_D = (224, 205, 176), (185, 161, 132)
BOARD, BOARD_D, BOARD_L = (78, 55, 39), (61, 43, 32), (116, 62, 43)
p = Pic(W, H, WALL0)
yy, xx = np.mgrid[0:H, 0:W]
ALL = np.ones((H, W), bool)
CX = 128

# the wall, darker toward the corners; the spotlight's pool round him
r = np.hypot((xx - CX) / 1.05, (yy - 100) * 1.0)
p.dither(ALL, INK2, WALL0, np.clip(1.25 - r / 120, 0, 1))
p.dither(r < 78, WALL0, WALL1, np.clip(1 - r / 78, 0, 1) * 1.2)
p.dither(r < 52, WALL1, SPOT0, np.clip(1 - r / 52, 0, 1) * 0.9)
# the stage's boards and its front edge
p.rect(0, 178, W, H, BOARD)
for y in (182, 188, 195): p.rect(0, y, W, y, BOARD_D)
for x in range(6, W, 37): p.rect(x, 179, x, 199, BOARD_D)
p.rect(0, 178, W, 178, BOARD_L)
p.dither((yy > 178) & (np.abs(xx - CX) < 70), BOARD, BOARD_L, np.clip(1 - np.abs(xx - CX) / 70, 0, 1) * 0.5)

# the music stand: three legs, a column, a tilted desk with the poem's sheet on it
SX = 46
p.line([(SX, 120), (SX, 172)], INK, 2)
p.line([(SX, 170), (SX - 14, 186)], INK, 2); p.line([(SX, 170), (SX + 14, 186)], INK, 2); p.line([(SX, 170), (SX + 1, 188)], INK, 1)
p.poly([(SX - 26, 104), (SX + 26, 98), (SX + 28, 124), (SX - 24, 130)], INK)
p.poly([(SX - 23, 104), (SX + 23, 99), (SX + 25, 121), (SX - 21, 126)], WHITE)
p.poly([(SX + 23, 99), (SX + 25, 121), (SX + 22, 121.5), (SX + 20, 100)], WHITE_D)
for k, ln in enumerate((30, 22, 34, 14, 26, 18, 30)):        # the lines of the poem, in different weights
    y = 106 + k * 2.6
    p.line([(SX - 19, y - k * 0.25), (SX - 19 + ln, y - k * 0.25 - ln * 0.11)], INK if k % 3 else RED, 1)

# the legs: tubes of blue cardboard, shining down their fronts, banded where they were bent
for lx in (CX - 15, CX + 4):
    p.rect(lx, 150, lx + 11, 177, BLUE_D)
    p.rect(lx + 1, 150, lx + 10, 177, BLUE)
    p.rect(lx + 3, 150, lx + 4, 177, BLUE_L)
    p.rect(lx + 9, 150, lx + 10, 177, BLUE_D)
    for y in (158, 167): p.rect(lx, y, lx + 11, y, BLUE_D)
    p.rect(lx - 1, 176, lx + 13, 178, INK)                 # the shoe at its foot

# the cape: a great collar of cardboard falling from the shoulders to the knees, gold outside
# in stiff pleats, the scarlet lining showing where it parts in front and at its spread hems
cape = [(CX - 12, 64), (CX + 12, 64), (CX + 38, 76), (CX + 48, 92), (CX + 60, 150), (CX + 46, 140), (CX + 34, 154), (CX + 20, 144), (CX + 6, 156), (CX - 6, 156), (CX - 20, 144), (CX - 34, 154), (CX - 46, 140), (CX - 60, 150), (CX - 48, 92), (CX - 38, 76)]
cm = p.mask(lambda d: d.polygon(cape, fill=255))
p.fill(cm, GOLD)
# the pleats: strips running from the collar, lit on the left of each fold
for k in range(-6, 7):
    if k == 0: continue
    x0, x1 = CX + k * 5, CX + k * 9.5
    edge = p.mask(lambda d: d.line([(x0, 70), (x1, 156)], fill=255, width=2)) & cm
    p.fill(edge, GOLD_L if k < 0 else GOLD_D)
p.dither(cm & (xx > CX + 18), GOLD, GOLD_D, np.clip((xx - CX - 18) / 50, 0, 1) * 0.6)
# the scarlet within: the parting in front, and the lining turned up at both hems
p.poly([(CX - 4, 90), (CX + 4, 90), (CX + 9, 156), (CX - 9, 156)], RED)
p.poly([(CX - 2, 96), (CX + 2, 96), (CX + 4, 156), (CX - 4, 156)], RED_D)
p.poly([(CX - 60, 150), (CX - 54, 120), (CX - 46, 140)], RED)
p.poly([(CX + 60, 150), (CX + 54, 120), (CX + 46, 140)], RED)
# the shoulders' stiff edge, lit
p.line([(CX - 38, 77), (CX - 14, 66)], GOLD_L, 1); p.line([(CX + 14, 66), (CX + 38, 77)], GOLD_L, 1)
p.outline(cm, INK)
# the claws: his hands in cardboard, thrust out at the cape's hems, three hooked points each
for side in (-1, 1):
    hx, hy = CX + side * 58, 146
    for k in (-1, 0, 1):
        base = (hx + k * 4, hy)
        mid = (hx + side * 4 + k * 6, hy + 12)
        tip = (hx + side * 1 + k * 8, hy + 22 - abs(k) * 2)
        p.line([base, mid, tip], INK, 3)
        p.line([base, mid], GOLD_L if side < 0 else GOLD, 1)
        p.px(tip[0], tip[1], WHITE)
# the collar: a high ring of white card flaring up round the jaw
col = [(CX - 11, 66), (CX + 11, 66), (CX + 17, 48), (CX + 9, 54), (CX - 9, 54), (CX - 17, 48)]
colm = p.mask(lambda d: d.polygon(col, fill=255))
p.fill(colm, WHITE)
p.dither(colm & (xx > CX + 4), WHITE, WHITE_DD, 0.5)
p.outline(colm, INK)
p.ellipse(CX - 9, 31, CX + 9, 54, SKIN)
p.dither((yy > 31) & (yy < 53) & (np.hypot((xx - CX) / 9, (yy - 42) / 11) < 1) & (xx > CX + 3), SKIN, SKIN_D, 0.6)
p.outline(np.hypot((xx - CX) / 9.5, (yy - 42) / 11.5) < 1, INK)
for ex in (CX - 5, CX + 3): p.rect(ex, 41, ex + 2, 41, INK)          # eyes, lowered to the sheet
p.rect(CX - 1, 43, CX, 46, SKIN_D)                                   # the nose
p.rect(CX - 3, 48, CX + 2, 48, RED_D)                                # the mouth, open on a vowel
p.px(CX - 1, 49, RED_D)
# the hat: a tall cylinder striped blue and white, its brim a little flared
hat = [(CX - 11, 4), (CX + 11, 4), (CX + 12, 32), (CX - 12, 32)]
hm = p.mask(lambda d: d.polygon(hat, fill=255))
for k in range(8):
    band = hm & (yy >= 4 + k * 3.5) & (yy < 4 + (k + 1) * 3.5)
    p.fill(band, BLUE if k % 2 == 0 else WHITE)
for k in range(8):
    band = hm & (yy >= 4 + k * 3.5) & (yy < 4 + (k + 1) * 3.5) & (xx > CX + 6)
    p.fill(band, BLUE_D if k % 2 == 0 else WHITE_DD)
p.rect(CX - 13, 31, CX + 13, 33, BLUE_D)
p.outline(hm, INK)

p.graded().save(OUT, optimize=True)
p.graded().resize((W * 3, H * 3), 0).save(UTIL + '/v25/k-new.png')
print('saved')
