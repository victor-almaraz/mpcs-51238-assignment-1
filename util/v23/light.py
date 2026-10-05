# v23's room at evening, lit after NORCO's pixel art: a cool night ambient, the room's practical
# lights as its key (the desk lamp's warm pool, the computer's cool screen, dusk through the
# window falling across the wall), the corners falling into dark, shadows coloured rather than
# black; then the whole scene quantized into one palette of its own, cut from the lit room, with
# an ordered dither whose matrix is fixed to the room's grid, so a gradient of light breaks into
# the same pattern on the wall, the desk and every sprite that lies in it.
import json
import numpy as np
from PIL import Image
from pix import HERE, save
from room import OUT, W, H

BAYER = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16 - 0.47

LAMP = (115, 158)                     # the lamp's throat, in room pixels
LAMP_DIR = np.array([0.72, 0.69])     # it points down and to the right, at the desk
SCREEN = (397, 152)                   # the middle of the computer's glass
AMBIENT = np.array([0.52, 0.52, 0.66])
EDGE = AMBIENT * 0.8

def smooth(t): t = np.clip(t, 0, 1); return t * t * (3 - 2 * t)

def light_field():
    """an RGB multiplier for every pixel of the room"""
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    L = np.zeros((H, W, 3), dtype=np.float32) + AMBIENT
    # the lamp: a warm cone toward the desk, and a softer glow all round the shade
    dx, dy = xx - LAMP[0], yy - LAMP[1]
    d = np.hypot(dx, dy) + 1e-3
    cosang = (dx * LAMP_DIR[0] + dy * LAMP_DIR[1]) / d
    cone = smooth((cosang - 0.15) / 0.75)
    fall = 1 / (1 + (d / 85) ** 2)
    glow = 1 / (1 + (d / 22) ** 2)
    warm = np.array([1.0, 0.74, 0.46])
    L += (fall * (0.2 + 0.85 * cone) * 0.7 + glow * 0.1)[..., None] * warm
    # the screen: a cool glow over the desk in front of it and the wall behind
    dx, dy = xx - SCREEN[0], (yy - SCREEN[1]) * 1.3
    d = np.hypot(dx, dy)
    L += (0.42 / (1 + (d / 46) ** 2))[..., None] * np.array([0.55, 0.78, 0.9])
    # dusk through the window, off to the left: a slanting shaft across the upper wall, pink
    u = xx - (24 + yy * 0.55)
    shaft = smooth(u / 16) * smooth((96 - u) / 16) * smooth((170 - yy) / 60)
    L += (shaft * 0.32)[..., None] * np.array([1.0, 0.62, 0.62])
    # toward the room's edges the light falls away to one value, EDGE, which the paper and the
    # floor that run on past the room are lit by, so the room's corners go dark and the room
    # meets what lies beyond it without a seam
    de = np.minimum(np.minimum(xx, W - 1 - xx), yy)
    t = smooth(de / 110)[..., None]
    return EDGE + (L - EDGE) * t

FIELD = None
def field():
    global FIELD
    if FIELD is None: FIELD = light_field()
    return FIELD

def lit(im, x0, y0):
    """a picture placed at (x0, y0) in the room, lit by the room's light (float RGB, alpha)"""
    a = np.array(im.convert('RGBA')).astype(np.float32)
    h, w = a.shape[:2]
    F = np.ones((h, w, 3), dtype=np.float32) * AMBIENT
    ys0, xs0 = max(0, y0), max(0, x0)
    ys1, xs1 = min(H, y0 + h), min(W, x0 + w)
    if ys1 > ys0 and xs1 > xs0:
        F[ys0 - y0:ys1 - y0, xs0 - x0:xs1 - x0] = field()[ys0:ys1, xs0:xs1]
    return grade(a[..., :3] * F), a[..., 3]

def grade(rgb):
    """after the light: the dark tones lean violet-blue, the highlights roll off"""
    # shadows and dark tones lean violet-blue, not black
    lum = rgb.mean(-1, keepdims=True)
    rgb = rgb + (np.array([18, 14, 34]) * np.clip(1 - lum / 90, 0, 1))
    # highlights roll off rather than burn out
    k = 1.3
    rgb = 255 * (1 - np.exp(-k * rgb / 255)) / (1 - np.exp(-k))
    return deepen(rgb)

def deepen(rgb, contrast=1.07, sat=0.22, dark=0.07):
    """a little more contrast about the middle, and the blues and greens deeper: wherever
    green or blue leads red, the colour is pushed further from grey and a step darker"""
    rgb = 128 + (rgb - 128) * contrast
    r, g, b = rgb[..., 0:1], rgb[..., 1:2], rgb[..., 2:3]
    cool = np.clip((np.maximum(g, b) - r) / 50, 0, 1)
    mean = rgb.mean(-1, keepdims=True)
    rgb = mean + (rgb - mean) * (1 + sat * cool)
    rgb = rgb * (1 - dark * cool)
    return np.clip(rgb, 0, 255)

def make_palette(samples, n=40):
    """the scene's palette: a median cut of the samples given (relight.py balances them, an
    equal share for every colour of the unlit room)"""
    sample = np.concatenate([s.reshape(-1, 3) for s in samples]).astype(np.uint8)
    q = Image.fromarray(sample.reshape(1, -1, 3)).quantize(colors=n, method=Image.Quantize.MEDIANCUT)
    p = q.getpalette()[:3 * n]
    return np.array([p[i:i + 3] for i in range(0, len(p), 3)], dtype=np.float32)

def quantize(rgb, alpha, pal, x0, y0, amount=12):
    h, w = rgb.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w]
    t = BAYER[(yy + y0) % 4, (xx + x0) % 4][..., None] * amount
    v = (rgb + t).reshape(-1, 3)
    wts = np.array([3, 6, 1], dtype=np.float32)
    best = np.zeros(len(v), dtype=np.int32); bd = np.full(len(v), 1e12, dtype=np.float32)
    for i, c in enumerate(pal):
        dd = (((v - c) ** 2) * wts).sum(1)
        m = dd < bd; bd[m] = dd[m]; best[m] = i
    out = np.zeros((h, w, 4), dtype=np.uint8)
    out[..., :3] = pal[best].reshape(h, w, 3).astype(np.uint8)
    out[..., 3] = np.where(alpha > 0, 255, 0)
    return Image.fromarray(out)
