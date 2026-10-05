# Drawing tools for the computer's pictures, drawn directly in pixels (no smoothing) in the
# room's base palette, then mapped colour for colour to the screen's graded palette.
import os as _os; UTIL = _os.path.normpath(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..')); REPO = _os.path.dirname(UTIL)
import json, math, random
import numpy as np
from PIL import Image, ImageDraw
HERE23 = UTIL + '/v23'
BASE = [tuple(c) for c in json.load(open(HERE23 + '/palette.json'))]
GRADED = [tuple(c) for c in json.load(open(HERE23 + '/palette-screen.json'))]
MAP = dict(zip(BASE, GRADED))
BAYER = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16 + 1 / 32

def near(c):
    """the base palette's colour nearest c"""
    c = np.array(c, dtype=float)
    d = [((np.array(p) - c) ** 2 * [0.9, 1.77, 0.33]).sum() for p in BASE]
    return BASE[int(np.argmin(d))]

class Pic:
    def __init__(self, w, h, ground):
        self.w, self.h = w, h
        self.a = np.zeros((h, w, 3), dtype=np.uint8); self.a[:] = near(ground)
    def mask(self, draw_fn):
        m = Image.new('L', (self.w, self.h), 0); draw_fn(ImageDraw.Draw(m))
        return np.array(m) > 127
    def fill(self, m, c):
        self.a[m] = near(c)
    def dither(self, m, c1, c2, level):
        """c2 over c1 at the given share (0..1, a number or an array the size of the picture)"""
        yy, xx = np.mgrid[0:self.h, 0:self.w]
        t = BAYER[yy % 4, xx % 4]
        lv = level if np.ndim(level) == 0 else level
        on = m & (t < lv)
        self.a[m & ~on] = near(c1); self.a[on] = near(c2)
    def poly(self, pts, c):
        self.fill(self.mask(lambda d: d.polygon([tuple(map(float, p)) for p in pts], fill=255)), c)
    def rect(self, x0, y0, x1, y1, c):
        self.a[max(0, int(y0)):int(y1) + 1, max(0, int(x0)):int(x1) + 1] = near(c)
    def ellipse(self, x0, y0, x1, y1, c):
        self.fill(self.mask(lambda d: d.ellipse([x0, y0, x1, y1], fill=255)), c)
    def line(self, pts, c, w=1):
        self.fill(self.mask(lambda d: d.line([tuple(map(float, p)) for p in pts], fill=255, width=w)), c)
    def px(self, x, y, c):
        if 0 <= int(x) < self.w and 0 <= int(y) < self.h: self.a[int(y), int(x)] = near(c)
    def get(self, x, y): return tuple(self.a[int(y), int(x)])
    def outline(self, m, c):
        """a one-pixel line round the outside of a shape"""
        g = m.copy(); g[1:] |= m[:-1]; g[:-1] |= m[1:]; g[:, 1:] |= m[:, :-1]; g[:, :-1] |= m[:, 1:]
        self.fill(g & ~m, c)
    def graded(self):
        out = np.zeros_like(self.a)
        for b, g in MAP.items():
            m = (self.a == b).all(-1); out[m] = g
        return Image.fromarray(out)
