# v23's room, second pass: shape before detail. Every sprite is cut from a clean seed (v21's
# drawing rendered without its grain), held to a few colours, cleared of stray pixels, and
# closed by a darker line of its own colour (pix.clean). The prints, whose detail is too fine
# for 6 pixels to the em, are drawn directly in pixels: a few strong shapes that suggest it.
import io, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from fontTools.ttLib import TTFont
from pix import pixelate, clean, save, HERE, REPO
from room import wall_tile, wall, floor, desk, drop, near, rgb, px, W, H, OUT

SEEDS = HERE + '/../v19r/seeds/'
INK, PAPER, CREAM = (30, 29, 27), (251, 248, 240), (239, 226, 194)

def font(slug, weight, size):
    t = TTFont('%s/fonts/%s/%s-latin-%d-normal.woff2' % (REPO, slug, slug, weight)); t.flavor = None
    b = io.BytesIO(); t.save(b); b.seek(0)
    return ImageFont.truetype(b, size)

def cut(seed, w_em, h_em, k=8, bias=0.2, outline=True):
    im = Image.open(SEEDS + seed).convert('RGBA')
    return clean(pixelate(im, px(w_em), px(h_em), line_bias=bias), k, outline)

def bevel(d, x0, y0, x1, y1, base, w=1):
    """a frame w pixels wide: lit along its top and left, shaded along its bottom and right"""
    lite, dark = tuple(near(np.clip(np.array(base) * 1.2, 0, 255))), tuple(near(np.array(base) * 0.7))
    for k in range(w):
        d.line([(x0 + k, y0 + k), (x1 - k, y0 + k)], fill=lite); d.line([(x0 + k, y0 + k), (x0 + k, y1 - k)], fill=lite)
        d.line([(x0 + k, y1 - k), (x1 - k, y1 - k)], fill=dark); d.line([(x1 - k, y0 + k), (x1 - k, y1 - k)], fill=dark)

# ---------------------------------------------------------------- the prints, drawn in pixels
# in design units (a sixth of an em), rasterized at the room's resolution by drawn.Canvas
from drawn import Canvas, K

def text(cv, x, y, s, size, c, slug='pixelify-sans', weight=700):
    """type set without smoothing at the room's resolution, then laid into the canvas"""
    f = font(slug, weight, max(6, int(round(size * K))))
    m = Image.new('L', (cv.W, cv.H), 0); d = ImageDraw.Draw(m); d.fontmode = '1'
    d.text((int(x * K), int(y * K)), s, font=f, fill=255)
    cv.a[np.array(m) > 127] = c + (255,)

def frame(cv, x0, y0, x1, y1, base, w=1):
    lite, dark = tuple(near(np.clip(np.array(base) * 1.2, 0, 255))), tuple(near(np.array(base) * 0.7))
    for k in range(w):
        cv.line(x0 + k, y0 + k, x1 - k, y0 + k, lite); cv.line(x0 + k, y0 + k, x0 + k, y1 - k, lite)
        cv.line(x0 + k, y1 - k, x1 - k, y1 - k, dark); cv.line(x1 - k, y0 + k, x1 - k, y1 - k, dark)

def print_sieve():
    # the oak frame, the mat, and the sieve: five rows of residue classes, each a colour, its
    # members bright dots and the rest a single dark point; their union in ink along the foot
    w, h = 114, 89
    cv = Canvas(w, h)
    oak = (200, 169, 126)
    cv.rect(0, 0, w - 1, h - 1, oak); frame(cv, 0, 0, w - 1, h - 1, oak, 2)
    cv.rect(4, 4, w - 5, h - 5, PAPER)
    ix0, iy0, ix1, iy1 = 11, 10, w - 12, h - 17
    cv.rect(ix0, iy0, ix1, iy1, CREAM)
    cx, cy, r = ix0 + 16, (iy0 + iy1) / 2, 15
    cv.fill(lambda x, y: (224, 205, 176) if (x - cx) ** 2 + (y - cy) ** 2 < r * r and (int(x * K) + int(y * K)) % 2 == 0 else None, (ix0, iy0, ix1, iy1))
    rows = [(2, 0, (201, 154, 46)), (3, 1, (181, 70, 43)), (4, 2, (73, 85, 90)), (5, 0, (125, 138, 120)), (7, 3, (168, 119, 83))]
    n = 24; cw = (ix1 - ix0 - 4) / (n - 1)
    for r_, (m, res, col) in enumerate(rows):
        y = iy0 + 5 + r_ * 6
        for k in range(n):
            x = ix0 + 2 + k * cw
            if k % m == res: cv.rect(x - 1, y - 1, x, y, col)
            else: cv.dot(x, y, (134, 123, 104))
    y = iy1 - 4
    cv.line(ix0 + 2, y + 1, ix1 - 2, y + 1, INK)
    for k in range(n):
        x = ix0 + 2 + k * cw
        if any(k % m == res for m, res, _ in rows): cv.rect(x - 1, y - 2, x, y, INK)
    cv.line(ix0, h - 11, ix0 + 9, h - 11, (150, 152, 136)); cv.line(ix1 - 5, h - 11, ix1, h - 11, (150, 152, 136))
    return cv.image()

def print_dada():
    # Ball's sound poem as a Dada poster: DADA in red block letters across it, lines of the
    # poem in black, a black disc, a red ring, an arrow, a torn scrap
    w, h = 68, 86
    cv = Canvas(w, h)
    red = (181, 70, 43)
    cv.rect(0, 0, w - 1, h - 1, INK); cv.rect(2, 2, w - 3, h - 3, (239, 226, 194))
    text(cv, 5, 9, 'DADA', 22, red)
    for (x, y, ln) in ((6, 6, 30), (40, 6, 18), (8, 37, 22), (36, 39, 24), (44, 46, 16)):
        cv.line(x, y, x + ln, y, INK)
        for k in range(0, ln, 3): cv.dot(x + k, y + 1, INK)
    cv.line(4, 33, 60, 31, INK, 2); cv.line(37, 27, 37, 58, INK, 2)
    cv.fill(lambda x, y: red if 3.6 < math.hypot(x - 53, y - 33) < 6.2 else INK if abs(x - 53) < 1.6 and abs(y - 33) < 1.6 else None, (46, 26, 60, 40))
    cv.fill(lambda x, y: INK if math.hypot(x - 13, y - 60) < 6 else None, (6, 53, 20, 67))
    cv.rect(41, 52, 58, 60, (216, 209, 195))
    for y in range(53, 60, 2): cv.line(42, y, 56, y, (134, 123, 104))
    cv.line(26, 68, 40, 62, INK, 2); cv.fill(lambda x, y: INK if 40 <= x <= 44 and abs(y - 62) <= (44 - x) * 0.75 else None, (40, 58, 45, 66))
    text(cv, 20, 70, 'glandride', 10, red, weight=400)
    cv.line(6, 80, w - 7, 80, (134, 123, 104))
    return cv.image()

def print_shelf():
    # the ochre screen print pinned above the shelf: a red sun, string-art saddles in ink
    # and in paper over a ground a shade paler, brass pins at its corners
    w, h = 118, 60
    cv = Canvas(w, h)
    och, och_l = (201, 154, 46), (240, 196, 106)
    cv.rect(0, 0, w - 1, h - 1, PAPER); cv.rect(3, 3, w - 4, h - 4, och)
    g = 3 + int((h - 7) * 0.72)
    cv.rect(3, g, w - 4, h - 4, och_l)
    cv.fill(lambda x, y: (181, 70, 43) if math.hypot(x - 26, y - 17) < 8 else None, (17, 8, 35, 26))
    def strings(a, b, c, dd, n, col):
        for k in range(n + 1):
            t = k / n
            p = (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t); q = (dd[0] + (c[0] - dd[0]) * t, dd[1] + (c[1] - dd[1]) * t)
            cv.line(p[0], p[1], q[0], q[1], col)
    strings((10, g), (38, 6), (66, g), (38, g), 9, INK)
    strings((38, 6), (66, g), (100, 14), (100, g), 8, INK)
    strings((70, g), (90, 22), (w - 6, g), (90, g), 6, PAPER)
    for x in (2, w - 3): cv.dot(x, 2, (240, 196, 106)); cv.dot(x, 3, (168, 119, 83))
    return cv.image()

# ---------------------------------------------------------------- the room
DECOR = [  # seed, left, top, width, height (em), colours, shadow on the wall
    ('shelf.png', 47, -0.8, 40, 15.2, 6, True),
    ('stool.png', 53.1, 35.8, 8.4, 9.2, 5, False),
    ('plant-fig.png', 0.6, 46 - 1 - 21, 11, 21, 7, False),
    ('plant-monstera.png', 92 - 0.4 - 14, 46 - 1 - 16, 14, 16, 7, False),
    ('lamp.png', 10.6, 19.4, 7, 10.6, 5, True),
    ('pothos.png', 16.4, 21.8, 10, 11.6, 7, False),
    ('mug.png', 33.4, 27, 3.2, 3, 4, False)]
THINGS = [  # name, seed, width, height (em), colours
    ('px-vol-1.png', 'vol-1.png', 3.2, 9.8, 6), ('px-vol-2.png', 'vol-2.png', 2.9, 9.1, 6), ('px-vol-3.png', 'vol-3.png', 3.05, 9.5, 6),
    ('px-mag-back.png', 'mag-back.png', 7.6, 9, 8), ('px-mag-front.png', 'mag-front.png', 7.6, 9, 6),
    ('px-file-box.png', 'file-box.png', 4.6, 7.4, 7), ('px-deck-box.png', 'deck-box.png', 9.6, 6.4, 7),
    ('px-coding-form.png', 'coding-form.png', 7, 9.4, 7), ('px-out-tray.png', 'out-tray.png', 10.4, 4.4, 7),
    ('px-tape.png', 'tape-room.png', 15, 10.6, 9)]

def room():
    tile = wall_tile()
    canvas = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    wall(canvas, tile); floor(canvas); desk(canvas)
    for p, l, t in ((print_sieve(), 9.4, 3), (print_dada(), 31.2, 4.2)):
        x, y = px(l), px(t); drop(canvas, p, x, y, 2, 2); canvas.alpha_composite(p, (x, y))
    import drawn
    DRAWN = {'shelf.png': drawn.shelf, 'lamp.png': drawn.lamp, 'plant-fig.png': drawn.fig, 'plant-monstera.png': drawn.monstera, 'pothos.png': drawn.pothos}
    for seed, l, t, w, h, k, sh in DECOR:
        p = DRAWN[seed]() if seed in DRAWN else cut(seed, w, h, k)
        x, y = px(l), px(t)
        if seed == 'shelf.png':
            sx, sy = x + int(round(101 * K)), y + int(round(6 * K))
            sp = print_shelf(); drop(canvas, sp, sx, sy, 2, 2); canvas.alpha_composite(sp, (sx, sy))
        if sh: drop(canvas, p, x, y, 2, 2)
        canvas.alpha_composite(p, (x, y))
    save(canvas, OUT + 'room.png')
    canvas.crop((0, H - px(1.6), px(11), H)).save(OUT + 'floor-tile.png')
    canvas.resize((W * 3, H * 3), Image.NEAREST).save(HERE + '/room-px3.png')

def cover():
    # the magazine's cover on the shelf: its orange field, the title in paper, a target of rings
    w, h = 37, 50
    cv = Canvas(w, h)
    cv.rect(0, 0, w - 1, h - 1, (255, 90, 31)); cv.rect(0, 0, w - 1, 8, INK)
    text(cv, 3, -1, 'Moiré', 10, PAPER)
    cv.fill(lambda x, y: (INK if int(math.hypot(x - 18, y - 30) / 3) % 2 else (220, 0, 120)) if math.hypot(x - 18, y - 30) < 13 else None, (4, 16, 32, 44))
    cv.fill(lambda x, y: INK if math.hypot(x - 18, y - 30) < 3 else None, (14, 26, 22, 34))
    cv.rect(3, h - 6, 20, h - 5, PAPER)
    return cv.image()

def things():
    for name, seed, w, h, k in THINGS:
        save(cut(seed, w, h, k), OUT + name)
    save(cover(), OUT + 'px-cover.png')

def computer():
    # v21's computer, cut from its seed, its screen drawn in pixels: the night picture, the
    # menu bar, the Read Me and the Editor, the column of icons
    spr = cut('computer-room.png', 17, 13, 8)
    x0, y0, w, h = 18, 8, 66, 41
    sc = Canvas(w, h)
    bg = Image.open(OUT + 'pics/desktop.png').convert('RGBA').crop((180, 60, 180 + 568, 60 + 353)).resize((sc.W, sc.H), Image.NEAREST)
    sc.a[:] = np.array(bg)
    STR, BLUE, TERRA, SAGE, MAN = (134, 123, 104), (43, 69, 96), (181, 70, 43), (126, 160, 98), (240, 196, 106)
    sc.rect(0, 0, w - 1, 2, PAPER); sc.line(0, 3, w - 1, 3, INK)
    for xx in (4, 9, 14, 19, 24): sc.line(xx, 1, xx + 2, 1, INK)
    def win(x, y, ww, hh, active=False):
        sc.rect(x + 1, y + 1, x + ww, y + hh, INK); sc.rect(x, y, x + ww - 1, y + hh - 1, INK); sc.rect(x + 1, y + 1, x + ww - 2, y + hh - 2, PAPER)
        sc.line(x, y + 3, x + ww - 1, y + 3, INK)
        if active:
            for yy in (y + 1, y + 2): sc.line(x + 2, yy, x + ww - 3, yy, STR)
            sc.rect(x + ww // 2 - 4, y + 1, x + ww // 2 + 4, y + 2, PAPER)
    win(3, 6, 27, 26)
    for k, c in enumerate((TERRA, BLUE, TERRA)): sc.line(5, 10 + k, 27, 8 + k * 2, c)
    for i, yy in enumerate((17, 19, 21, 23, 25, 27)): sc.line(5, yy, 5 + [20, 16, 22, 12, 18, 9][i], yy, STR)
    win(17, 14, 32, 24, active=True)
    for k, ln in enumerate((10, 6, 14, 8, 5, 12)):
        yy = 21 + k * 2; sc.dot(19, yy, STR); sc.line(22, yy, 22 + ln, yy, INK)
    sc.line(42, 18, 42, 36, TERRA)
    for k, c in enumerate((MAN, PAPER, BLUE, MAN, (154, 97, 54), MAN, SAGE)):
        yy = 6 + k * 5; sc.rect(w - 8, yy, w - 4, yy + 3, INK); sc.rect(w - 7, yy + 1, w - 5, yy + 2, c)
    scr = sc.image()
    mask = Image.new('L', scr.size, 0); ImageDraw.Draw(mask).rounded_rectangle([0, 0, scr.width - 1, scr.height - 1], radius=2, fill=255)
    spr.paste(scr, (int(round(x0 * K)), int(round(y0 * K))), mask)
    save(spr, OUT + 'px-computer.png')

if __name__ == '__main__':
    import sys
    for w in (sys.argv[1:] or ['room', 'things', 'computer']): globals()[w]()

