# Tzara's recipe, 240 x 160, drawn in pixels: on a table, a newspaper with the article cut
# out of it, a pair of scissors lying open, and an upturned top hat standing in for the bag,
# the words cut from the article rising out of it on slips of paper, the last few still in
# the air, turning as they fall back.
import os as _os; UTIL = _os.path.normpath(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..')); REPO = _os.path.dirname(UTIL)
import glob, io, math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from fontTools.ttLib import TTFont
from pixart import Pic, near
OUT = REPO + '/v25/assets/pics/drawing-t.png'
REPO = REPO
W, H = 240, 160
INK, INK2 = (19, 16, 14), (30, 29, 27)
WALL, WALL_D = (201, 199, 191), (180, 175, 162)
TABLE, TABLE_L, TABLE_D = (168, 119, 83), (200, 169, 126), (116, 62, 43)
NEWS, NEWS_D, PRINT = (229, 224, 209), (198, 190, 173), (98, 96, 89)
SLIP, SLIP_D = (250, 250, 246), (216, 209, 195)
FELT, FELT_L, BAND = (30, 29, 27), (79, 73, 67), (181, 70, 43)
STEEL, STEEL_L, HANDLE = (148, 152, 136), (229, 224, 209), (181, 70, 43)
rnd = random.Random(1920)
p = Pic(W, H, WALL)
yy, xx = np.mgrid[0:H, 0:W]

def font(size=10):
    path = glob.glob(REPO + '/fonts/fusion-pixel-10px-proportional-jp/*.woff2')[0]
    t = TTFont(path); t.flavor = None
    b = io.BytesIO(); t.save(b); b.seek(0)
    return ImageFont.truetype(b, size)
F = font(10)
def text_mask(s, x, y):
    m = Image.new('L', (W, H), 0); d = ImageDraw.Draw(m); d.fontmode = '1'
    d.text((x, y), s, font=F, fill=255)
    return np.array(m) > 127
def text_w(s): l, t, r, b = F.getbbox(s); return r - l

# the wall, a little darker at the top; the table's edge and top
p.dither(yy < 112, WALL, WALL_D, np.clip(1 - yy / 112, 0, 1) * 0.45)
p.rect(0, 112, W, H, TABLE)
p.dither(yy >= 112, TABLE, TABLE_L, np.clip(1 - (yy - 112) / 30, 0, 1) * 0.35)
p.rect(0, 112, W, 112, TABLE_L); p.rect(0, 152, W, H, TABLE_D)
for x in range(0, W, 61): p.rect(x, 140, x + 30, 140, TABLE_D)        # the grain

# the newspaper, folded, the article cut out of its front page, the table showing through
nx0, ny0, nx1, ny1 = 10, 92, 92, 128
p.poly([(nx0, ny0 + 4), (nx1, ny0), (nx1 + 4, ny1), (nx0 + 2, ny1 + 3)], NEWS)
p.poly([(nx1, ny0), (nx1 + 4, ny1), (nx1 + 1, ny1), (nx1 - 2, ny0 + 1)], NEWS_D)
p.rect(nx0 + 4, ny0 + 5, nx1 - 4, ny0 + 9, INK2)                           # the masthead
for k, ln in enumerate((44, 30)): p.rect(nx0 + 4, ny0 + 12 + k * 3, nx0 + 4 + ln, ny0 + 13 + k * 3, PRINT)
for col in range(3):
    cx = nx0 + 4 + col * 26
    for r in range(6):
        y = ny0 + 20 + r * 2
        if col == 1 and 1 <= r <= 4: continue
        p.rect(cx, y, cx + 21 - (r * 5) % 7, y, PRINT)
p.rect(nx0 + 31, ny0 + 21, nx0 + 52, ny0 + 29, TABLE)                      # the hole the article left
p.rect(nx0 + 31, ny0 + 21, nx0 + 52, ny0 + 21, TABLE_D); p.rect(nx0 + 31, ny0 + 21, nx0 + 31, ny0 + 29, TABLE_D)
p.outline(p.mask(lambda d: d.polygon([(nx0, ny0 + 4), (nx1, ny0), (nx1 + 4, ny1), (nx0 + 2, ny1 + 3)], fill=255)), PRINT)

# the scissors, lying open, at the right
sx, sy = 192, 128
p.poly([(sx, sy - 2), (sx + 42, sy - 24), (sx + 44, sy - 22), (sx + 2, sy + 1)], STEEL)
p.poly([(sx, sy), (sx + 44, sy - 8), (sx + 44, sy - 5), (sx + 1, sy + 3)], STEEL)
p.line([(sx + 4, sy - 3), (sx + 41, sy - 23)], STEEL_L, 1); p.line([(sx + 4, sy), (sx + 42, sy - 7)], STEEL_L, 1)
for cx, cy in ((sx - 11, sy + 1), (sx - 5, sy + 11)):
    p.ellipse(cx - 8, cy - 6, cx + 8, cy + 6, HANDLE); p.ellipse(cx - 4, cy - 2, cx + 4, cy + 2, TABLE)
p.rect(sx - 1, sy - 1, sx + 1, sy + 1, INK)

# the hat, upturned: its crown standing on the table, its brim at the top, the opening dark
hx, top, bot = 140, 82, 120
crown = [(hx - 26, top), (hx + 26, top), (hx + 23, bot), (hx - 23, bot)]
cm = p.mask(lambda d: d.polygon(crown, fill=255))
p.fill(cm, FELT)
p.dither(cm & (xx < hx - 12), FELT, FELT_L, 0.45)
p.rect(hx - 25, top + 8, hx + 25, top + 13, BAND); p.rect(hx - 25, top + 13, hx + 25, top + 13, (116, 62, 43))
p.ellipse(hx - 24, bot - 4, hx + 24, bot + 4, FELT)                       # the crown's top, on the table
p.ellipse(hx - 36, top - 6, hx + 36, top + 6, FELT)                        # the brim, seen from a little above
p.ellipse(hx - 27, top - 4, hx + 27, top + 4, INK)                         # the opening
p.line([(hx - 35, top), (hx - 28, top + 3)], FELT_L, 1)
p.rect(hx - 30, bot + 2, hx + 30, bot + 3, TABLE_D)                        # its shadow

# the slips, rising out of the hat in a spray, each a word cut from the article
WORDS = ['machine', 'chance', 'music', 'brain', 'IBM', 'audience', 'notes', 'hour', 'applauded', 'electronic', 'laws', 'every']
placed = []
def free(x0, y0, x1, y1):
    return all(x1 + 3 < a or x0 > b + 3 or y1 + 2 < c or y0 > d + 2 for a, c, b, d in placed)
rows = [(64, 34), (49, 62), (34, 90), (19, 108), (4, 116)]          # each row's height and how far it fans out
order = WORDS[:]
rnd.shuffle(order)
k = 0
for y, spread in rows:
    xs = [hx + spread * f for f in (-1, -0.33, 0.33, 1)] if spread > 40 else [hx - spread, hx + spread * 0.2]
    for x in xs:
        if k >= len(order): break
        word = order[k]; w = text_w(word) + 6
        x0 = int(max(2, min(W - w - 2, x - w / 2))); y0 = y + rnd.randint(-2, 2)
        if not free(x0, y0, x0 + w, y0 + 12): continue
        placed.append((x0, y0, x0 + w, y0 + 12)); k += 1
        tilt = rnd.choice([-1, 0, 0, 1])
        pts = [(x0, y0 + tilt), (x0 + w, y0 - tilt), (x0 + w, y0 + 11 - tilt), (x0, y0 + 11 + tilt)]
        p.poly([(a + 1, b + 1) for a, b in pts], WALL_D)
        p.poly(pts, SLIP)
        p.line([(x0, y0 + 11 + tilt), (x0 + w, y0 + 11 - tilt)], SLIP_D, 1)
        p.fill(text_mask(word, x0 + 3, y0), INK)
# a few blank slips still turning in the air, edge on
for x, y in ((hx - 12, 72), (hx + 18, 74), (hx + 2, 68)):
    p.line([(x, y), (x + 6, y - 3)], SLIP, 2); p.px(x + 6, y - 3, SLIP_D)

p.graded().save(OUT, optimize=True)
p.graded().resize((W * 3, H * 3), 0).save(UTIL + '/v25/t-new.png')
print('saved')
