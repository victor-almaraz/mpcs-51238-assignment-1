# The photo album's photographs: eight black-and-white prints and four Polaroids, cut from
# reference photographs into pixels. A print is 192 by 144 pixels in a white border, cut to ten
# warm greys by an ordered dither fixed to its grid; a Polaroid is 128 square in its frame,
# its own faded colours cut to 32.
#
#   python3.11 album_pics.py [references]   writes ../../v25/assets/st/album-p*.png and
#                                            album-q*.png, and a contact sheet, album.png
#
# The references are not kept in the repository; by default they are read from Archive/ at
# its root. Each is named below with the part of it that is the photograph (left, top, right,
# bottom, in its own pixels), cropped to the print's or the Polaroid's shape.
import os as _os; UTIL = _os.path.normpath(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..')); REPO = _os.path.dirname(UTIL)
import os, sys
import numpy as np
from PIL import Image, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = REPO + '/v25/assets/st/'
SRC = sys.argv[1] if len(sys.argv) > 1 else REPO + '/Archive/'
W, H, P = 192, 144, 128
BAYER = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16

PRINTS = [('Duck-ai-image-2026-10-05-21-35(1).jpeg', (70, 300, 1170, 1125)),     # the roofs
          ('Duck-ai-image-2026-10-05-21-35(2).jpeg', (95, 368, 1185, 1185)),     # the shore in winter
          ('Duck-ai-image-2026-10-05-21-36.jpeg', (70, 356, 1175, 1185)),        # the gallery
          ('Duck-ai-image-2026-10-06-00-50(1).jpeg', (0, 150, 1277, 1108)),      # the train
          ('Duck-ai-image-2026-10-06-00-50(3).jpeg', (0, 180, 1254, 1120)),      # the bench
          ('Duck-ai-image-2026-10-06-00-50(4).jpeg', (0, 100, 1254, 1040)),      # the couple
          ('Duck-ai-image-2026-10-06-00-50(5).jpeg', (0, 150, 1254, 1090)),      # the street
          ('Duck-ai-image-2026-10-06-00-50(6).jpeg', (0, 120, 1254, 1060))]      # the market
POLAROIDS = [('Duck-ai-image-2026-10-05-21-35.jpeg', (230, 90, 1140, 1000)),     # the bowling alley
             ('Duck-ai-image-2026-10-05-21-36(1).jpeg', (80, 70, 1200, 1190)),   # the beach, a light leak
             ('Duck-ai-image-2026-10-06-00-50(2).jpeg', (180, 95, 1075, 990)),   # the hills from the train
             ('Duck-ai-image-2026-10-06-00-50.jpeg', (190, 95, 1095, 1000))]     # the sunset

def take(name, box, w, h):
    """the photograph's part, cut down to w by h and sharpened a little so it holds at that size"""
    im = Image.open(SRC + name).convert('RGB').crop(box).resize((w, h), Image.LANCZOS)
    return im.filter(ImageFilter.UnsharpMask(radius=1, percent=70, threshold=2))

INK, PAPER = np.array([20, 18, 17], dtype=np.float32), np.array([236, 232, 222], dtype=np.float32)
def greys(im, n=10):
    """the print: its tones stretched to the paper's range, then cut to n warm greys by an
    ordered dither"""
    a = np.array(im.convert('L')).astype(np.float32)
    lo, hi = np.percentile(a, 1), np.percentile(a, 99.5)
    v = np.clip((a - lo) / max(1, hi - lo), 0, 1)
    yy, xx = np.mgrid[0:a.shape[0], 0:a.shape[1]]
    q = np.clip(np.floor(v * (n - 1) + BAYER[yy % 4, xx % 4]), 0, n - 1) / (n - 1)
    return Image.fromarray((INK + (PAPER - INK) * q[..., None]).astype(np.uint8))

def faded(im, k=32):
    """the Polaroid: its own colours, cut to k by an ordered dither"""
    a = np.array(im).astype(np.float32)
    yy, xx = np.mgrid[0:a.shape[0], 0:a.shape[1]]
    a = a + (BAYER[yy % 4, xx % 4][..., None] - 0.5) * 14
    im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    return im.quantize(colors=k, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE).convert('RGB')

def mount_print(im):
    out = Image.new('RGB', (W + 16, H + 16), (238, 236, 228)); out.paste(im, (8, 8)); return out
def mount_polaroid(im):
    out = Image.new('RGB', (P + 12, P + 40), (240, 238, 230)); out.paste(im, (6, 6)); return out

if __name__ == '__main__':
    names = []
    for i, (n, box) in enumerate(PRINTS):
        f = 'album-p%d.png' % (i + 1); mount_print(greys(take(n, box, W, H))).save(OUT + f, optimize=True); names.append(f)
    for i, (n, box) in enumerate(POLAROIDS):
        f = 'album-q%d.png' % (i + 1); mount_polaroid(faded(take(n, box, P, P))).save(OUT + f, optimize=True); names.append(f)
    sheet = Image.new('RGB', (4 * 214, 3 * 174), (30, 30, 30))
    for i, f in enumerate(names): sheet.paste(Image.open(OUT + f), ((i % 4) * 214, (i // 4) * 174))
    sheet.save(HERE + '/album.png')
    print('\n'.join(names))
