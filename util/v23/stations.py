# v23's stations as pixel art: the pictures seen when a thing is taken up, in the room's
# palette. Line drawings (the miscellanea's plates, the magazine's plates, the tape deck's
# parts, the computer's frame) are pixelated by majority; photographs are dithered in an
# ordered (Bayer) pattern, as pixel art shows a photograph; the magazine's halftone screens
# become ordered dithers of each ink on the paper.
import json, os
import numpy as np
from PIL import Image
from pix import pixelate, snap, pal_array, save, HERE, REPO
from room import render_svg

OUT = REPO + '/v23/assets/st/'
V21 = REPO + '/v21/assets/'
BAYER4 = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16 - 0.5

def add_inks():
    path = HERE + '/palette.json'
    cols = [tuple(c) for c in json.load(open(path))]
    for h in ('#dc0078', '#ff5a1f', '#00a6c8', '#ffd400', '#fffaf0'):
        c = tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))
        if c not in cols: cols.append(c)
    json.dump(cols, open(path, 'w'))

def dither(im, w, h, amount=48):
    """a photograph at w x h, dithered into the palette by an ordered 4x4 matrix"""
    im = im.convert('RGB').resize((w, h), Image.LANCZOS)
    a = np.array(im).astype(np.float32)
    yy, xx = np.mgrid[0:h, 0:w]
    a += BAYER4[yy % 4, xx % 4][..., None] * amount
    idx = snap(np.clip(a, 0, 255))
    P = pal_array().astype(np.uint8)
    return Image.fromarray(P[idx])

def misc():
    for n, (w, h) in {'a1': (560, 360), 'a2': (420, 280), 'b1': (560, 340), 'c1': (560, 320), 'd1': (440, 330), 'e1': (600, 300),
                      'f1': (560, 320), 'i1': (640, 330), 'j1': (640, 344), 'l1': (520, 470)}.items():
        big = render_svg(V21 + 'misc/%s.svg' % n, w // 2, h // 2, 6)
        save(pixelate(big, w // 2, h // 2, line_bias=0.12), OUT + 'misc-%s.png' % n)

def photos():
    for n, (w, h) in {'cluny': (1200, 964), 'concret': (1200, 854), 'montreal': (957, 1200), 'persepolis': (1200, 856)}.items():
        im = Image.open(REPO + '/v15/assets/misc-%s.jpeg' % n)
        save(dither(im, w // 4, h // 4), OUT + 'photo-%s.png' % n)

def mag():
    for n, (w, h) in {'a1': (600, 460), 'a2': (600, 430), 'a3': (600, 430), 'a4': (600, 460), 'catalogue': (600, 150), 'contents': (600, 150),
                      'cover-field': (600, 450), 'wash': (600, 170)}.items():
        big = render_svg(V21 + 'mag/%s.svg' % n, w // 3, h // 3, 6)
        save(pixelate(big, w // 3, h // 3, line_bias=0.15), OUT + 'mag-%s.png' % n)
    # the screens: each ink at about a third, in a 4x4 ordered pattern on the paper
    paper = (255, 250, 240)
    for k, (ink, cover) in {'c': ((0, 166, 200), 0.4), 'm': ((220, 0, 120), 0.4), 'y': ((255, 212, 0), 0.45), 'o': ((255, 90, 31), 0.4), 'k': ((13, 13, 13), 0.3)}.items():
        t = np.zeros((4, 4, 3), dtype=np.uint8)
        for y in range(4):
            for x in range(4):
                t[y, x] = ink if BAYER4[y, x] + 0.5 < cover else paper
        save(Image.fromarray(t), OUT + 'screen-%s.png' % k)

def tape():
    for n, (w, h) in {'deck': (1560, 750), 'head': (1560, 750), 'reel': (612, 612)}.items():
        im = Image.open(V21 + n + '.webp')
        save(pixelate(im, w // 6, h // 6), OUT + n + '.png')

def bezel():
    im = Image.open(V21 + 'bezel.webp')
    save(pixelate(im, im.width // 2, im.height // 2, line_bias=0), OUT + 'bezel.png')

if __name__ == '__main__':
    import sys
    if not sys.argv[1:]: add_inks()
    for w in (sys.argv[1:] or ['misc', 'photos', 'mag', 'tape', 'bezel']): globals()[w]()
