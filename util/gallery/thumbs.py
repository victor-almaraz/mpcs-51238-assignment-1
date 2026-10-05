# The gallery's pictures of the rooms: each version screenshot in headless Chrome (served at
# localhost:8000, the repository's root: python3 -m http.server 8000), cut down to 192 x 120
# and to the last room's palette (v25's 96 colours) by an ordered dither, so each reads as a
# print made in the room. Writes ../../assets/rooms/vNN.png. Usage: thumbs.py [v01 v02 ...]
import os, sys, json
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'v23'))
from shot import shot
REPO = os.path.normpath(os.path.join(HERE, '..', '..'))
OUT = os.path.join(REPO, 'assets', 'rooms')
PAL = np.array(json.load(open(os.path.join(HERE, '..', 'v25', 'palette-v24.json'))), dtype=np.float32)
BAYER = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16 - 0.47
W, H = 192, 120

def cut(im):
    a = np.array(im.convert('RGB').resize((W, H), Image.LANCZOS)).astype(np.float32)
    yy, xx = np.mgrid[0:H, 0:W]
    v = (a + BAYER[yy % 4, xx % 4][..., None] * 24).reshape(-1, 3)
    d = (((v[:, None, :] - PAL[None]) ** 2) * np.array([3, 6, 1])).sum(-1)
    return Image.fromarray(PAL[d.argmin(1)].reshape(H, W, 3).astype(np.uint8))

if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    ids = sys.argv[1:] or ['v%02d' % k for k in range(1, 26)]
    for v in ids:
        raw = os.path.join(HERE, 'shot-%s.png' % v)
        shot('http://localhost:8000/%s/' % v, raw, 1280, 800, budget=6000)
        cut(Image.open(raw)).save(os.path.join(OUT, v + '.png'), optimize=True)
        print(v)
