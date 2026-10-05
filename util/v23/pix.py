# v23's pixel-art pipeline: the vector drawings of v21 and v22 seed the pixel art.
#   palette()     one palette for the room and the computer, cut from the drawings themselves
#                 (median cut), with the room's named colours and pure ink and paper added
#   pixelate()    a picture rendered large is cut into cells, one cell an art pixel: every
#                 source pixel is snapped to the palette and each cell takes the colour most
#                 of its covered pixels have (a majority, not an average, so edges stay hard
#                 and thin dark lines survive where they are a cell's largest share); a cell
#                 is opaque where most of it is covered
import os as _os; UTIL = _os.path.normpath(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..')); REPO = _os.path.dirname(UTIL)
import json, os, glob
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = REPO
NAMED = ['#1e1d1b', '#fbf8f0', '#f7f4ec', '#ede4d4', '#2b4560', '#4a6886', '#6f8ca8', '#b5462b', '#c99a2e', '#7d8a78',
         '#49555a', '#c8a97e', '#a98b68', '#4e3727', '#3d2b20', '#d8d1c3', '#e6dcc4', '#b9a184', '#3b6a55', '#efe2c2']

def hexrgb(h): h = h.lstrip('#'); return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))

def palette(n=40, sources=None):
    path = HERE + '/palette.json'
    if os.path.exists(path) and sources is None:
        return [tuple(c) for c in json.load(open(path))]
    tiles = []
    for p in sources:
        im = Image.open(p).convert('RGBA')
        im.thumbnail((360, 360))
        a = np.array(im)
        rgb = a[a[..., 3] > 200][:, :3]
        if len(rgb): tiles.append(rgb)
    allpx = np.concatenate(tiles)
    strip = Image.fromarray(allpx.reshape(1, -1, 3).astype('uint8'))
    q = strip.quantize(colors=n, method=Image.Quantize.MEDIANCUT)
    pal = q.getpalette()[:3 * n]
    cols = [tuple(pal[i:i + 3]) for i in range(0, len(pal), 3)]
    for h in NAMED:
        c = hexrgb(h)
        if min(sum((a - b) ** 2 for a, b in zip(c, d)) for d in cols) > 120: cols.append(c)
    cols = sorted(set(cols), key=lambda c: (0.3 * c[0] + 0.59 * c[1] + 0.11 * c[2]))
    json.dump(cols, open(path, 'w'))
    return cols

_PAL = None
def pal_array():
    global _PAL
    if _PAL is None: _PAL = np.array(palette(), dtype=np.float32)
    return _PAL

def snap(rgb):
    """index of the nearest palette colour for each pixel (a weighted RGB distance)"""
    P = pal_array()
    w = np.array([0.30, 0.59, 0.11], dtype=np.float32) * 3
    flat = rgb.reshape(-1, 3).astype(np.float32)
    best = np.zeros(len(flat), dtype=np.int32); bestd = np.full(len(flat), 1e12, dtype=np.float32)
    for i, c in enumerate(P):
        d = (((flat - c) ** 2) * w).sum(1)
        m = d < bestd; bestd[m] = d[m]; best[m] = i
    return best.reshape(rgb.shape[:2])

def pixelate(im, out_w, out_h, alpha_cut=0.5, line_bias=0.2):
    """im: a large RGBA picture; returns an out_w x out_h RGBA picture in the palette"""
    im = im.convert('RGBA')
    W, H = im.size
    a = np.array(im)
    idx = snap(a[..., :3])
    op = a[..., 3] > 127
    P = pal_array().astype(np.uint8)
    LUM = (pal_array() * [0.3, 0.59, 0.11]).sum(1)
    out = np.zeros((out_h, out_w, 4), dtype=np.uint8)
    xs = np.linspace(0, W, out_w + 1).astype(int); ys = np.linspace(0, H, out_h + 1).astype(int)
    n = len(P)
    for j in range(out_h):
        y0, y1 = ys[j], max(ys[j] + 1, ys[j + 1])
        for i in range(out_w):
            x0, x1 = xs[i], max(xs[i] + 1, xs[i + 1])
            cell_op = op[y0:y1, x0:x1]
            cov = cell_op.mean()
            if cov < alpha_cut: continue
            votes = np.bincount(idx[y0:y1, x0:x1][cell_op], minlength=n)
            win = votes.argmax()
            # a dark line through a lighter cell keeps the cell if it covers a fair share of it
            if line_bias:
                tot = votes.sum(); wl = LUM[win]
                cand = np.where((votes >= line_bias * tot) & (LUM < wl - 70))[0]
                if len(cand): win = cand[np.argmin(LUM[cand])]
            out[j, i, :3] = P[win]; out[j, i, 3] = 255
    return Image.fromarray(out)

def outline(im, color=(30, 29, 27), only_dark_bg=False):
    """a one-pixel outline round the opaque shape, outside it, where it meets transparency"""
    a = np.array(im.convert('RGBA'))
    op = a[..., 3] > 0
    grown = op.copy()
    grown[1:] |= op[:-1]; grown[:-1] |= op[1:]; grown[:, 1:] |= op[:, :-1]; grown[:, :-1] |= op[:, 1:]
    edge = grown & ~op
    a[edge, :3] = color; a[edge, 3] = 255
    return Image.fromarray(a)

def save(im, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    im.save(path, optimize=True)
    return path

if __name__ == '__main__':
    srcs = sorted(glob.glob(REPO + '/v21/assets/*.webp')) + [HERE + '/room-all.png']
    cols = palette(40, srcs)
    print(len(cols), 'colours')
    sw = Image.new('RGB', (len(cols) * 24, 24))
    for i, c in enumerate(cols): sw.paste(c, (i * 24, 0, i * 24 + 24, 24))
    sw.save(HERE + '/palette.png')

# ---------------------------------------------------------------- the cleanup pass
# Pixel art reads by shape, not by detail: a few colours to a thing, no stray pixels, and a
# silhouette closed by a line one shade darker than what it bounds.
def _nearest_idx(c, cols):
    d = ((cols.astype(int) - np.array(c, dtype=int)) ** 2 * [3, 6, 1]).sum(1)
    return int(d.argmin())

def reduce(im, k):
    """keep the k colours a picture uses most; every other pixel takes its nearest of those"""
    a = np.array(im.convert('RGBA'))
    op = a[..., 3] > 0
    cols, counts = np.unique(a[op][:, :3], axis=0, return_counts=True)
    if len(cols) <= k: return im
    keep = cols[np.argsort(-counts)[:k]]
    for c in cols:
        m = op & (a[..., :3] == c).all(-1)
        a[m, :3] = keep[_nearest_idx(c, keep)]
    return Image.fromarray(a)

def orphans(im, passes=2):
    """a pixel unlike all four of its neighbours takes the colour most of its eight neighbours
    have; a lone opaque pixel goes, a lone hole fills"""
    a = np.array(im.convert('RGBA'))
    H, W = a.shape[:2]
    for _ in range(passes):
        b = a.copy()
        for y in range(H):
            for x in range(W):
                n4 = [a[yy, xx] for yy, xx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)) if 0 <= yy < H and 0 <= xx < W]
                me = a[y, x]
                if any((n == me).all() for n in n4): continue
                n8 = [tuple(a[yy, xx]) for yy in range(y - 1, y + 2) for xx in range(x - 1, x + 2) if (yy, xx) != (y, x) and 0 <= yy < H and 0 <= xx < W]
                if me[3] == 0:
                    if sum(1 for n in n4 if n[3]) == len(n4) == 4:
                        b[y, x] = max(set(n8), key=n8.count)
                    continue
                if sum(1 for n in n4 if n[3]) == 0: b[y, x] = 0; continue
                best = max(set(n8), key=n8.count)
                if n8.count(best) >= 3: b[y, x] = best
        a = b
    return Image.fromarray(a)

def selout(im, k=0.62):
    """the silhouette closed from within: each opaque pixel at the edge takes a darker shade of
    its own colour (the palette's nearest), so the line is the thing's own, not a black one"""
    a = np.array(im.convert('RGBA'))
    op = a[..., 3] > 0
    edge = op.copy()
    inner = op.copy()
    inner[1:] &= op[:-1]; inner[:-1] &= op[1:]; inner[:, 1:] &= op[:, :-1]; inner[:, :-1] &= op[:, 1:]
    edge &= ~inner
    P = pal_array()
    for y, x in zip(*np.where(edge)):
        c = a[y, x, :3].astype(float) * k
        a[y, x, :3] = P[_nearest_idx(c, P)].astype(np.uint8)
    return Image.fromarray(a)

def clean(im, k=8, outline=True):
    im = orphans(reduce(im, k))
    return selout(im) if outline else im
