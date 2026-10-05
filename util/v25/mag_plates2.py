# The plates of Event (a Fluxus newspaper: black and one yellow on newsprint) and Gesso (painting by
# rule and chance: painters' colours on a warm white), drawn in pixels, 264 x 96 each, the
# covers' fields 300 x 225. Each plate is its article's subject made a picture by its own rule.
import os as _os; UTIL = _os.path.normpath(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..')); REPO = _os.path.dirname(UTIL)
import math, random, glob, io
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from fontTools.ttLib import TTFont
OUT = REPO + '/v25/assets/st/'
REPO = REPO
NEWS, NEWS_D, K, YEL = (238, 232, 214), (214, 206, 186), (18, 18, 18), (242, 183, 5)    # Event's one ink, a yellow
WARM, CAD, ORA, CER, ALI, UMB, GRN = (247, 242, 232), (242, 194, 48), (226, 102, 44), (59, 127, 182), (184, 40, 60), (110, 76, 52), (70, 132, 92)

def font(size=10, face='proportional'):
    t = TTFont(glob.glob(REPO + '/fonts/fusion-pixel-10px-%s*/*.woff2' % face)[0]); t.flavor = None
    b = io.BytesIO(); t.save(b); b.seek(0); return ImageFont.truetype(b, size)
F = font(10)
FM = font(10, 'monospaced')      # the printer's type: every character the same width
def canvas(w, h, c): im = Image.new('RGB', (w, h), c); d = ImageDraw.Draw(im); d.fontmode = '1'; return im, d
def save(im, name): im.save(OUT + name, optimize=True)

# ---------------------------------------------------------------- Event
def ev_grid(w, h, seed, cover=False):
    """a front page in Maciunas's manner: a tight grid of boxes, black bars, red bars, lines of type"""
    rnd = random.Random(seed)
    im, d = canvas(w, h, NEWS)
    x = 4
    while x < w - 10:
        cw = rnd.choice([28, 36, 44, 52, 60]) if not cover else rnd.choice([36, 48, 60, 72])
        cw = min(cw, w - 4 - x)
        y = 4
        while y < h - 8:
            bh = rnd.choice([14, 20, 26, 34, 44])
            bh = min(bh, h - 4 - y)
            kind = rnd.random()
            if kind < 0.18: d.rectangle([x, y, x + cw - 3, y + bh - 3], fill=K)
            elif kind < 0.28: d.rectangle([x, y, x + cw - 3, y + bh - 3], fill=YEL)
            elif kind < 0.42:                       # a halftone picture
                for yy in range(y, y + bh - 2, 2):
                    for xx in range(x, x + cw - 2, 2):
                        if rnd.random() < 0.5 + 0.4 * math.sin((xx + yy) / 9.0): d.point((xx, yy), fill=K)
            else:                                    # lines of type
                for yy in range(y + 1, y + bh - 3, 3):
                    d.line([(x, yy), (x + rnd.randint(cw // 2, cw - 3), yy)], fill=K)
            d.rectangle([x - 1, y - 1, x + cw - 2, y + bh - 2], outline=K)
            y += bh
        x += cw
    return im

def ev_cards():
    # event cards laid out on red, each typed with its title, a rule and a line or two, after Brecht's
    rnd = random.Random(1959)
    im, d = canvas(264, 96, YEL)
    words = ['DRIP MUSIC', 'WORD EVENT', 'SOLO', 'EXIT', 'LAMP']
    spots = [(8, 8), (60, 46), (104, 6), (156, 44), (196, 10)]
    for wd, (x, y) in zip(words, spots):
        w = max(62, int(F.getlength(wd)) + 10)
        d.rectangle([x + 3, y + 3, x + w + 3, y + 41], fill=(176, 128, 0))
        d.rectangle([x, y, x + w, y + 38], fill=NEWS, outline=K)
        d.text((x + 5, y + 3), wd, font=F, fill=K)
        d.line([(x + 5, y + 16), (x + w - 5, y + 16)], fill=K)
        for j in range(2): d.line([(x + 5, y + 22 + j * 5), (x + 5 + rnd.randint(20, w - 14), y + 22 + j * 5)], fill=NEWS_D)
    save(im, 'ev-a1.png')

def ev_box():
    # a Fluxkit opened: a plastic case divided into compartments, each holding a thing
    rnd = random.Random(1964)
    im, d = canvas(264, 96, NEWS)
    d.rectangle([10, 8, 254, 88], fill=K)
    d.rectangle([14, 12, 250, 84], fill=(60, 60, 60))
    cells = [(14, 12, 74, 46), (76, 12, 148, 46), (150, 12, 250, 46), (14, 48, 110, 84), (112, 48, 180, 84), (182, 48, 250, 84)]
    for i, (a, b, c, e) in enumerate(cells):
        d.rectangle([a + 2, b + 2, c - 2, e - 2], fill=NEWS)
    # a die, a deck of cards, a ball, a whistle, a printed card, a key
    d.rectangle([28, 20, 52, 40], fill=NEWS, outline=K)
    for px, py in ((33, 25), (46, 25), (40, 30), (33, 35), (46, 35)): d.rectangle([px, py, px + 1, py + 1], fill=K)
    for k in range(4): d.rectangle([88 + k * 3, 18 - k, 128 + k * 3, 40 - k], fill=NEWS, outline=K)
    d.text((96, 22), 'FLUX', font=F, fill=K)
    d.ellipse([186, 16, 214, 42], fill=YEL); d.ellipse([192, 20, 200, 27], fill=(250, 226, 140))
    d.rectangle([24, 60, 96, 70], fill=K); d.ellipse([88, 56, 102, 74], fill=K)
    d.rectangle([122, 54, 170, 80], fill=(250, 248, 240), outline=K); d.text((126, 58), 'EVENT', font=F, fill=K)
    d.line([(126, 72), (162, 72)], fill=K)
    d.ellipse([196, 58, 212, 74], outline=K, width=3); d.rectangle([212, 64, 240, 67], fill=K); d.rectangle([232, 67, 235, 72], fill=K)
    save(im, 'ev-a2.png')

def ev_house():
    # a house built of line-printer type on a grid: the words of the poem's lists run on without
    # their spaces, through a pitched roof, two windows and a door
    im, d = canvas(264, 96, NEWS)
    text = 'AHOUSEOFDUSTINADESERTUSINGCANDLESINHABITEDBYVEGETARIANSAHOUSEOFSTEELBYARIVER'
    cw, ch, cols, rows = 6, 10, 30, 9
    x0, k = 132 - cols * cw // 2, 0
    for r in range(rows):
        for c in range(cols):
            if r < 4:                                       # the roof: a triangle, its apex in the middle
                if abs(c - (cols - 1) / 2) > (r + 1) * cols / 8: continue
            else:
                if c < 3 or c > cols - 4: continue          # the walls stand in from the eaves
                if r in (5, 6) and (6 <= c <= 9 or cols - 10 <= c <= cols - 7): continue   # windows
                if r >= 6 and 13 <= c <= 16: continue       # the door
            ch_ = text[k % len(text)]; k += 1
            d.text((x0 + c * cw, 1 + r * ch), ch_, font=FM, fill=K)
    d.line([(10, 93), (254, 93)], fill=K)
    save(im, 'ev-a3.png')

def ev_cards_stack():
    rnd = random.Random(1962)
    im, d = canvas(264, 96, K)
    for k in range(10):
        x, y = rnd.randint(-10, 210), rnd.randint(-6, 70)
        d.rectangle([x, y, x + 64, y + 28], fill=NEWS)
        d.polygon([(x, y), (x + 5, y), (x, y + 5)], fill=K)
        for c in range(3, 62, 2):
            for r in range(3, 26, 3):
                if rnd.random() < 0.1: d.point((x + c, y + r), fill=YEL if rnd.random() < 0.2 else K)
    save(im, 'ev-catalogue.png')

# ---------------------------------------------------------------- Gesso
def gs_kelly(w, h, cell, seed, name):
    # Kelly's spectrum colours placed by chance: a grid of squares, each colour drawn from a hat
    rnd = random.Random(seed)
    cols = [CAD, ORA, CER, ALI, GRN, UMB, (238, 140, 160), (120, 80, 150), (240, 220, 120), (30, 30, 30), (140, 190, 210), WARM]
    im, d = canvas(w, h, WARM)
    for y in range(0, h, cell):
        for x in range(0, w, cell):
            d.rectangle([x, y, x + cell - 1, y + cell - 1], fill=rnd.choice(cols))
    save(im, name)

def gs_palette():
    im, d = canvas(264, 96, WARM)
    chips = [CAD, ORA, ALI, (238, 140, 160), (120, 80, 150), CER, (140, 190, 210), GRN, UMB, (30, 30, 30)]
    for i, c in enumerate(chips):
        x = 8 + i * 25
        d.rectangle([x, 14, x + 20, 70], fill=c)
        d.rectangle([x, 74, x + 20, 76], fill=c)
    d.line([(8, 84), (256, 84)], fill=(30, 30, 30))
    save(im, 'gs-contents.png')

def gs_albers():
    # homage to the square: four squares nested, set low, as Albers set them, three times
    im, d = canvas(264, 96, WARM)
    sets = [((226, 102, 44), (242, 150, 60), (246, 194, 90), (242, 220, 140)), ((59, 90, 140), (80, 127, 182), (130, 170, 200), (190, 210, 220)),
            ((110, 76, 52), (160, 110, 70), (200, 150, 90), (230, 200, 140))]
    for i, cs in enumerate(sets):
        x0, s = 8 + i * 86, 80
        y0 = 8
        for k, c in enumerate(cs):
            inset = k * 10
            d.rectangle([x0 + inset, y0 + inset * 1.5, x0 + s - inset, y0 + s - inset * 0.5], fill=c)
    save(im, 'gs-a2.png')

def gs_molnar():
    # (des)ordres: squares nested in a grid, each corner a little out of true, more toward the right
    rnd = random.Random(1974)
    im, d = canvas(264, 96, WARM)
    for gx in range(11):
        for gy in range(4):
            cx, cy = 12 + gx * 22 + 10, 6 + gy * 22 + 10
            t = gx / 10
            for k in range(4):
                s = 10 - k * 2.5
                pts = [(cx + sx * s + rnd.uniform(-1, 1) * t * 4, cy + sy * s + rnd.uniform(-1, 1) * t * 4) for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
                if rnd.random() < 0.08 * t: continue          # a square left out, as Molnár's are
                d.polygon(pts, outline=ALI if (k == 0 and rnd.random() < 0.15) else (30, 30, 30))
    save(im, 'gs-a3.png')

def gs_morellet():
    # a random distribution of squares by the digits of a directory: even blue, odd red
    rnd = random.Random(1961)
    im, d = canvas(264, 96, WARM)
    for y in range(0, 96, 4):
        for x in range(0, 264, 4):
            d.rectangle([x, y, x + 3, y + 3], fill=CER if rnd.randint(0, 9) % 2 == 0 else ALI)
    save(im, 'gs-catalogue.png')

if __name__ == '__main__':
    save(ev_grid(264, 96, 1963), 'ev-contents.png')
    save(ev_grid(300, 225, 1964, cover=True), 'ev-cover-field.png')
    ev_cards(); ev_box(); ev_house(); ev_cards_stack()
    gs_palette(); gs_kelly(264, 96, 12, 1951, 'gs-a1.png'); gs_albers(); gs_molnar(); gs_morellet()
    gs_kelly(300, 225, 25, 1953, 'gs-cover-field.png')
    names = ['ev-contents', 'ev-a1', 'ev-a2', 'ev-a3', 'ev-catalogue', 'gs-contents', 'gs-a1', 'gs-a2', 'gs-a3', 'gs-catalogue']
    sheet = Image.new('RGB', (264 * 2 + 10, 106 * 5), (60, 60, 60))
    for i, n in enumerate(names): sheet.paste(Image.open(OUT + n + '.png'), ((i // 5) * 274, (i % 5) * 106))
    sheet.resize((sheet.width * 2, sheet.height * 2), 0).save(UTIL + '/v25/plates2.png')
    c = Image.new('RGB', (610, 225), (60, 60, 60)); c.paste(Image.open(OUT + 'ev-cover-field.png'), (0, 0)); c.paste(Image.open(OUT + 'gs-cover-field.png'), (310, 0))
    c.resize((1220, 450), 0).save(UTIL + '/v25/covers2.png')
