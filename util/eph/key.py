"""Cut the ephemera out of their green backdrops.
alpha comes from a brightness-independent green ratio, so the backdrop's own shadows go too
(the page adds one consistent shadow in CSS). Holes inside an object are filled (glass
and patina that picked up green), except where an option says otherwise."""
import sys, os, numpy as np
from PIL import Image
from scipy import ndimage as nd
D = os.path.dirname(os.path.abspath(__file__))

OPTS = {
    'coffee':   {'stain': True},             # the ring: a translucent brown stain
    'loupe':    {'lens': True},              # the lens: clear glass with white highlights
    'tape-box': {'min_part': 0.02},          # drop the stray tail of tape
    'paperclips': {'fill': False},           # the loops of wire are real holes
    'card-stack': {'fill': False, 'min_part': 0.02},   # the punched holes are real holes
    # the screw cap is a cylinder (top ellipse centre, radii, side height, in source pixels):
    # solid, its green reflections redrawn as grey sheen on black knurling
    'inkwell':  {'cylinder': (627, 352, 197, 136, 118)},
}
STAIN = np.array([165, 110, 45.])           # the colour of dried coffee

def greenness(a):
    R, G, B = a[..., 0], a[..., 1], a[..., 2]
    return (G - np.maximum(R, B)) / (G + 8)

def key(name, lo=0.25, hi=0.75, maxside=760):
    o = OPTS.get(name, {})
    a = np.asarray(Image.open(f'{D}/orig/{name}.jpeg').convert('RGB')).astype(float)
    h, w, _ = a.shape
    border = np.concatenate([a[:6].reshape(-1, 3), a[-6:].reshape(-1, 3), a[:, :6].reshape(-1, 3), a[:, -6:].reshape(-1, 3)])
    bg = np.median(border, 0)
    eb = np.median(greenness(border))
    e = greenness(a)
    t = np.clip((e - lo * eb) / ((hi - lo) * eb), 0, 1)
    alpha = 1 - t * t * (3 - 2 * t)

    # despill, then turn what green tint is left grey (not teal) in proportion to the spill
    R, G, B = a[..., 0], a[..., 1], a[..., 2]
    rgb = np.dstack([R, np.minimum(G, np.maximum(R, B) + 4), B])
    grey = rgb.mean(2, keepdims=True)
    k = np.clip(e / eb, 0, 1)[..., None]
    rgb = rgb * (1 - k) + grey * k

    # the object: everything not reachable from the border through backdrop
    back = alpha < 0.5
    lab, n = nd.label(back)
    edge = np.unique(np.r_[lab[0], lab[-1], lab[:, 0], lab[:, -1]])
    outside = np.isin(lab, edge[edge > 0])
    holes = back & ~outside
    inside = ~nd.binary_dilation(outside, iterations=2)

    if o.get('lens'):
        # the biggest hole is the lens; the rest of the object is solid
        hl, hn = nd.label(holes)
        sizes = nd.sum(holes, hl, range(1, hn + 1))
        ys, xs = np.nonzero(hl == (np.argmax(sizes) + 1))
        cy, cx = (ys.min() + ys.max()) / 2, (xs.min() + xs.max()) / 2
        ry, rx = (ys.max() - ys.min()) / 2 + 8, (xs.max() - xs.min()) / 2 + 8
        yy, xx = np.mgrid[:h, :w]
        disk = ((yy - cy) / ry) ** 2 + ((xx - cx) / rx) ** 2 <= 1
        brass = (R > G + 12) & (R > 90)
        lens = disk & ~nd.binary_dilation(brass, iterations=1)
        alpha = np.where(inside & ~lens, 1, alpha)
        L = a.mean(2); Lb = np.median(L[lens])
        hi_ = np.clip((L - Lb) / 70, 0, 1)
        alpha = np.where(lens, 0.10 + 0.65 * hi_, alpha)
        rgb = np.where(lens[..., None], 255 - 20 * (1 - hi_[..., None]), rgb)
    elif o.get('stain'):
        # a stain darkens the backdrop; it is drawn as brown with that darkness as its alpha
        # each pixel is unmixed as stain over backdrop; the cup (white, black, brown) is left alone
        white = (a.min(2) > 175) & (a.max(2) - a.min(2) < 40)
        wl, wn = nd.label(white)
        rim = wl == (1 + np.argmax(nd.sum(white, wl, range(1, wn + 1))))
        cup = nd.binary_dilation(nd.binary_fill_holes(rim), iterations=3)
        stain = ((B < 0.5 * np.minimum(R, G)) | (e > lo * eb)) & ~cup
        d = STAIN - bg
        amt = np.clip(((a - bg) @ d) / (d @ d), 0, 1)
        alpha = np.where(stain, 0.5 * amt, np.where(cup, 1, 0))
        rgb = np.where(stain[..., None], STAIN * 0.8, rgb)
    elif o.get('fill', True):
        alpha = np.where(inside, 1, alpha)
    if 'cylinder' in o:
        cx, cy, rx, ry, hh = o['cylinder']
        yy, xx = np.mgrid[:h, :w].astype(float)
        dx = ((xx - cx) / rx) ** 2
        # inside the swept ellipse: some centre between cy and cy+hh lies within ry*sqrt(1-dx) of y
        half = ry * np.sqrt(np.clip(1 - dx, 0, None))
        solid = (dx <= 1) & (yy >= cy - half) & (yy <= cy + hh + half)
        edge = nd.gaussian_filter(solid.astype(float), 1.0)
        alpha = np.maximum(alpha, edge)
        if True:
            # black knurling: keep the light and dark of the reflections, drop their colour and blocks
            m = np.clip(k * 2.5, 0, 1) * solid[..., None]
            lum = nd.gaussian_filter(a.mean(2), 2.5)[..., None]
            sheen = 18 + 0.55 * lum
            rgb = rgb * (1 - m) + sheen * m

    if 'min_part' in o:
        lab, n = nd.label(alpha > 0.3)
        sizes = nd.sum(np.ones_like(alpha), lab, range(1, n + 1))
        keep = np.isin(lab, 1 + np.nonzero(sizes >= o['min_part'] * sizes.max())[0])
        keep = nd.binary_dilation(keep, iterations=3)
        alpha = np.where(keep, alpha, 0)

    out = np.dstack([rgb, alpha * 255])
    ys, xs = np.nonzero(alpha > 0.06)
    pad = 10
    y0, y1 = max(ys.min() - pad, 0), min(ys.max() + pad, h); x0, x1 = max(xs.min() - pad, 0), min(xs.max() + pad, w)
    im = Image.fromarray(np.round(np.clip(out[y0:y1, x0:x1], 0, 255)).astype('uint8'), 'RGBA')
    s = maxside / max(im.size)
    if s < 1: im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    im.save(f'{D}/out/{name}.webp', quality=88, method=6)
    return im.size

for n in sys.argv[1:]:
    print(n, key(n))
