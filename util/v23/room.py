# v23's room as pixel art, 6 art pixels to the em (the room is 92em x 46em: 552 x 276).
# Every drawing of v21's room seeds its pixel art: each picture is pixelated at the size and
# place it has in the room (pix.pixelate), so the picture and the room agree. What v21 drew
# in CSS (the wall's paper, the floor, the walnut desk, its trestle, the window's light, the
# lamp's pool, the shadows) is drawn here in pixels, in the same palette.
#   the backdrop (assets/room.png): wall, floor, desk, trestle, the prints, the shelf, the
#     lamp, the plants, the pothos, the mug, the stool, and their light and shadows
#   the things that can be taken up (assets/px-*.png): spines, magazine, file box, deck
#     box, coding form, out tray, computer, tape player, each at its own size
#   the paper's tile (assets/wall-tile.png), so the wall runs on past the room
import os, math, subprocess
import numpy as np
from PIL import Image
from pix import pixelate, pal_array, snap, save, HERE, REPO
from shot import shot

PPE = 640 / 92                   # art pixels to the em: the room is 640 x 320, so it shows at 2x at 1280 x 720
W, H = 640, 320
V21 = REPO + '/v21/assets/'
OUT = REPO + '/v23/assets/'
P = pal_array().astype(int)

def rgb(h): h = h.lstrip('#'); return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)])
def near(c):
    """the palette colour nearest an RGB colour"""
    d = (((P - np.array(c)) ** 2) * [0.9, 1.77, 0.33]).sum(1)
    return P[d.argmin()]
def shade(c, k):
    """the palette colour nearest c darkened (k < 1) or lightened (k > 1)"""
    c = np.array(c, dtype=float)
    t = c * k if k < 1 else c + (255 - c) * (k - 1)
    return near(np.clip(t, 0, 255))

def px(e): return int(round(e * PPE))

def render_svg(path, w, h, scale=10):
    """an SVG file drawn large by the browser, for pixelating"""
    html = HERE + '/_svg.html'
    open(html, 'w').write('<!doctype html><html><head><style>html,body{margin:0;background:transparent}img{display:block}</style></head><body><img src="file://%s" width="%d" height="%d"></body></html>' % (path, w * scale, h * scale))
    out = HERE + '/_svg.png'
    shot('file://' + html, out, w * scale, h * scale, budget=2500)
    return Image.open(out).convert('RGBA')

def paste(canvas, im, x, y):
    canvas.alpha_composite(im, (x, y))

def drop(canvas, im, x, y, dx=1, dy=1, k=0.72):
    """a hard shadow: the shape's own outline, moved down and right, darkening what is under it"""
    a = np.array(canvas)
    m = np.array(im)[..., 3] > 0
    h, w = m.shape
    for j in range(h):
        yy = y + j + dy
        if not 0 <= yy < a.shape[0]: continue
        for i in range(w):
            if not m[j, i]: continue
            xx = x + i + dx
            if 0 <= xx < a.shape[1] and a[yy, xx, 3]:
                a[yy, xx, :3] = shade(a[yy, xx, :3], k)
    canvas.paste(Image.fromarray(a), (0, 0))

def sprite(src, w_em, h_em, name=None, svg=False, bias=0.2):
    w, h = px(w_em), px(h_em)
    im = render_svg(src, w, h) if svg else Image.open(src).convert('RGBA')
    p = pixelate(im, w, h, line_bias=bias)
    if name: save(p, OUT + name)
    return p

# ---------------------------------------------------------------- the wall
def wall_tile():
    # v21's paper drawn again in pixels, from its own geometry (a 60 x 90 tile at 0.6 art
    # pixels a unit, 36 x 54): the half-drop ogee trellis in a pale blue line one pixel wide,
    # a cream seed pod with its dotted spine, stem and two pale leaves and a crown of ochre in
    # each cell, a small cream flower at each crossing, and seeds between
    TW, TH, k = 42, 63, 0.7
    G, LAT, CREAM, OCH, PALE = rgb('#2b4560'), near(rgb('#4a6886')), near(rgb('#e6dcc4')), near(rgb('#c9a45a')), near(rgb('#6f8ca8'))
    a = np.zeros((TH, TW, 4), dtype=np.uint8); a[..., :3] = near(G); a[..., 3] = 255
    def put(x, y, c):
        a[int(round(y)) % TH, int(round(x)) % TW, :3] = c
    def cubic(p0, p1, p2, p3, t):
        return tuple((1 - t) ** 3 * p0[i] + 3 * (1 - t) ** 2 * t * p1[i] + 3 * (1 - t) * t * t * p2[i] + t ** 3 * p3[i] for i in (0, 1))
    for ox in (0, 60):
        for oy in (-90, 0, 90):
            for sx in (1, -1):
                segs = [((ox, oy), (ox, oy + 20), (ox + sx * 30, oy + 25), (ox + sx * 30, oy + 45)),
                        ((ox + sx * 30, oy + 45), (ox + sx * 30, oy + 65), (ox + sx * 60, oy + 70), (ox + sx * 60, oy + 90))]
                for sg in segs:
                    for j in range(200):
                        x, y = cubic(*sg, t=j / 199)
                        put(x * k, y * k, LAT)
    def pod(cx, cy):
        cx, cy = cx * k, (cy - 2) * k
        for j in range(-6, 7):
            w = 3.6 * (1 - (j / 6.6) ** 2) ** 0.8
            put(cx - w, cy + j, CREAM); put(cx + w, cy + j, CREAM)
        for j in (-3, -1, 1, 3): put(cx, cy + j, CREAM)
        for j in range(7, 12): put(cx, cy + j, CREAM)
        for sd in (-1, 1):
            for (dx, dy) in ((1, 10), (2, 9), (3, 8), (4, 8), (2, 10), (3, 9)):
                put(cx + sd * dx, cy + dy, PALE)
        for dx, dy in ((0, -9), (-2, -8), (2, -8)): put(cx + dx, cy + dy, OCH)
    for x, y in ((30, 0), (30, 90), (0, 45), (60, 45)): pod(x, y)
    def flower(cx, cy):
        cx, cy = cx * k, cy * k
        for dx, dy in ((0, -1), (1, 0), (0, 1), (-1, 0)): put(cx + dx, cy + dy, CREAM)
        put(cx, cy, OCH)
    for x, y in ((0, 0), (60, 0), (0, 90), (60, 90), (30, 45)): flower(x, y)
    for x, y in ((15, 22), (45, 22), (15, 68), (45, 68)): put(x * k, y * k, PALE)
    p = Image.fromarray(a)
    save(p, OUT + 'wall-tile.png')
    return p

def wall(canvas, tile):
    for y in range(0, H, tile.height):
        for x in range(0, W, tile.width):
            canvas.paste(tile, (x, y))
    a = np.array(canvas)
    # the wall darkens a step toward the floor, in a dither of every other pixel
    def shaft(x, y, x0, w, top, bot, slant):
        if not top <= y < bot: return 0
        u = x - (x0 + (y - top) * slant)
        if not 0 <= u < w: return 0
        edge = min(u, w - 1 - u, y - top, bot - 1 - y)
        return 2 if edge >= 4 else 1
    for y in range(H):
        for x in range(W):
            c = a[y, x, :3]
            lit = 0
            if lit == 2 or (lit == 1 and (x + y) % 2 == 0): c = shade(c, 1.16)
            if y > H * 0.8 and (x + y) % 2 == 0: c = shade(c, 0.82)
            a[y, x, :3] = c
    canvas.paste(Image.fromarray(a), (0, 0))

def floor(canvas):
    a = np.array(canvas)
    top = H - px(1.6)
    oak, oakd = rgb('#b9a184'), rgb('#a98b68')
    for y in range(top, H):
        for x in range(W):
            c = oak if y > top + 1 else near((60, 40, 20))
            if y > top + 1 and (x % px(11)) == 0: c = near(oakd)
            if y > top + 1 and y >= H - 3: c = near(oakd)
            a[y, x, :3] = near(c); a[y, x, 3] = 255
    canvas.paste(Image.fromarray(a), (0, 0))

def desk(canvas):
    # the walnut top: a lit edge, the board with its grain, a dark lower edge, the apron below
    a = np.array(canvas)
    x0, x1, y0 = px(10), W - px(10), px(30)
    wl, wn, wd = near(rgb('#7a5a45')), near(rgb('#4e3727')), near(rgb('#3d2b20'))
    rows = [wl] + [wn] * 4 + [wd]
    for k, c in enumerate(rows):
        a[y0 + k, x0:x1, :3] = c; a[y0 + k, x0:x1, 3] = 255
    # the grain: long dark and light dashes along the board
    rnd = np.random.RandomState(7)
    for k in range(60):
        y = y0 + 1 + rnd.randint(0, 4); x = rnd.randint(x0, x1 - 20); L = rnd.randint(6, 24)
        a[y, x:x + L, :3] = wd if k % 3 else wl
    # the apron, set in by 4em at each end
    for y in range(y0 + 6, y0 + px(2)):
        a[y, x0 + px(4):x1 - px(4), :3] = wd; a[y, x0 + px(4):x1 - px(4), 3] = 255
    canvas.paste(Image.fromarray(a), (0, 0))
    # the trestle: each end an A of black steel, two pixels wide
    ink = tuple(near(rgb('#1e1d1b')))
    a = np.array(canvas)
    for cx in (x0 + px(5.5), x1 - px(5.5)):
        top_ = y0 + px(0.95); bot = H - px(1.6)
        for sx in (-1, 1):
            for y in range(top_, bot):
                t = (y - top_) / (bot - top_)
                x = int(round(cx + sx * t * (bot - top_) * math.tan(math.radians(9))))
                a[y, x:x + 2, :3] = ink; a[y, x:x + 2, 3] = 255
    canvas.paste(Image.fromarray(a), (0, 0))

def lamp_pool(canvas, lx, ly):
    # the lamp's pool of light: warm at its heart (every pixel lit a step toward the lamp's
    # colour), then a ring of one pixel in two, then one in four, fading out
    a = np.array(canvas)
    cx, cy, rx, ry = lx + px(5.0), ly + px(8.6), px(5.6), px(3.4)
    warm = np.array([255, 214, 150])
    for y in range(max(0, cy - ry), min(H, cy + ry)):
        for x in range(max(0, cx - rx), min(W, cx + rx)):
            d = ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2
            if d >= 1 or not a[y, x, 3]: continue
            if d < 0.35: on = True
            else: on = (x + y) % 2 == 0 and d < 0.75
            if on:
                c = a[y, x, :3].astype(float)
                a[y, x, :3] = near(np.clip(c * 0.7 + warm * 0.38, 0, 255))
    canvas.paste(Image.fromarray(a), (0, 0))

# ---------------------------------------------------------------- the room
DECOR = [  # file, left, top, width, height (em), shadow on the wall
    ('print-sieve.webp', 9.4, 3, 19, 19 * 840 / 1070, True),
    ('print-dada.webp', 31.2, 4.2, 11.4, 11.4 * 900 / 720, True),
    ('shelf.webp', 47, -0.8, 40, 15.2, True),
    ('stool.webp', 53.1, 35.8, 8.4, 9.2, False),
    ('plant-fig.webp', 0.6, 46 - 1 - 21, 11, 21, False),
    ('plant-monstera.webp', 92 - 0.4 - 14, 46 - 1 - 16, 14, 16, False),
    ('lamp.webp', 10.6, 19.4, 7, 10.6, True),
    ('pothos.webp', 16.4, 21.8, 10, 11.6, False),
    ('mug.webp', 33.4, 27, 3.2, 3, False)]

THINGS = [  # name, source, width, height (em)
    ('px-vol-1.png', 'vol-1.webp', 3.2, 9.8), ('px-vol-2.png', 'vol-2.webp', 2.9, 9.1), ('px-vol-3.png', 'vol-3.webp', 3.05, 9.5),
    ('px-mag-back.png', 'mag-back.webp', 7.6, 9), ('px-mag-front.png', 'mag-front.webp', 7.6, 9),
    ('px-file-box.png', 'file-box.webp', 4.6, 7.4), ('px-deck-box.png', 'deck-box.webp', 9.6, 6.4),
    ('px-coding-form.png', 'coding-form.webp', 7, 9.4), ('px-out-tray.png', 'out-tray.webp', 10.4, 4.4),
    ('px-computer.png', 'computer-room.webp', 17, 13), ('px-tape.png', 'tape-room.webp', 15, 10.6)]

def room():
    tile = wall_tile()
    canvas = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    wall(canvas, tile)
    floor(canvas)
    desk(canvas)
    for f, l, t, w, h, sh in DECOR:
        p = sprite(V21 + f, w, h, bias=0.08 if f == 'shelf.webp' else 0.2)
        x, y = px(l), px(t)
        if sh: drop(canvas, p, x, y, 2, 2)
        paste(canvas, p, x, y)
    save(canvas, OUT + 'room.png')
    canvas.resize((W * 3, H * 3), Image.NEAREST).save(HERE + '/room-px3.png')

def things():
    for name, src, w, h in THINGS:
        sprite(V21 + src, w, h, name)
    # the magazine's cover on the shelf, from its SVG
    sprite(V21 + 'mag/cover-thumb.svg', 6.2, 6.2 * 4 / 3, 'px-cover.png', svg=True)

if __name__ == '__main__':
    import sys
    for w in (sys.argv[1:] or ['room', 'things']): globals()[w]()
