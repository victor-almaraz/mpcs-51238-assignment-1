# Moiré's plates, drawn in pixels in its process inks (cyan, magenta, yellow, black and a spot
# orange) on paper, each at 264 x 96 (shown at 2x across a page's column), the cover's field at
# 300 x 225. Each is the article's subject made a picture, by the rule it describes:
#   cover, contents   moiré: two sets of rings printed over one another, beating
#   01  Schotter      Nees's squares in rows, more disordered row by row (here column by column)
#   02  chance        Arp's squares let fall, and Duchamp's metre of thread lying where it fell
#   03  Rule 30       the automaton grown from one black cell
#   04  27            the Collatz trajectory of 27, step by step, climbing to 9232 and falling
#   13  catalogue     a scatter of punched cards
import os as _os; UTIL = _os.path.normpath(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..')); REPO = _os.path.dirname(UTIL)
import math, random
import numpy as np
from PIL import Image, ImageDraw
OUT = REPO + '/v25/assets/st/'
PAPER, K, C, M, Y, O = (255, 250, 240), (19, 16, 14), (0, 166, 200), (220, 0, 120), (255, 212, 0), (255, 90, 31)
CARD, CARD_D = (239, 226, 194), (216, 189, 146)

def img(w, h, c):
    a = np.zeros((h, w, 3), np.uint8); a[:] = c; return a
def save(a, name): Image.fromarray(a).save(OUT + name, optimize=True)

def rings(w, h, ground, ink, centres, step=4, width=2):
    a = img(w, h, ground)
    yy, xx = np.mgrid[0:h, 0:w]
    for (cx, cy), col in centres:
        r = np.hypot(xx - cx, yy - cy)
        a[(r.astype(int) % step) < width] = col
    return a

def cover():
    a = rings(300, 225, O, K, [((112, 150), K), ((178, 132), M)], step=6, width=3)
    save(a, 'mag-cover-field.png')

def contents():
    a = rings(264, 96, M, K, [((90, 70), K), ((150, 40), PAPER)], step=5, width=2)
    save(a, 'mag-contents.png')

def schotter():
    # Nees's Schotter (1968) turned on its side: squares in columns, each column more tumbled
    w, h = 264, 96
    im = Image.new('RGB', (w, h), C); d = ImageDraw.Draw(im)
    rnd = random.Random(1965)
    cols, rows, s = 22, 7, 10
    for i in range(cols):
        for j in range(rows):
            t = i / (cols - 1)
            cx = 8 + i * 11.6 + rnd.uniform(-1, 1) * t * 6
            cy = 10 + j * 12.6 + rnd.uniform(-1, 1) * t * 6
            a = rnd.uniform(-1, 1) * t * math.pi / 3
            pts = [(cx + s / 2 * (math.cos(a + k * math.pi / 2) - math.sin(a + k * math.pi / 2)), cy + s / 2 * (math.sin(a + k * math.pi / 2) + math.cos(a + k * math.pi / 2))) for k in range(4)]
            d.polygon(pts, outline=K)
    save(np.array(im), 'mag-a1.png')

def chance():
    # torn squares let fall on magenta, and a metre of white thread across them
    w, h = 264, 96
    a = img(w, h, M)
    rnd = random.Random(1916)
    for k in range(16):
        s = rnd.randint(9, 18); x = rnd.randint(4, w - s - 4); y = rnd.randint(4, h - s - 4)
        col = rnd.choice([K, K, PAPER, Y])
        a[y + 2:y + s + 2, x + 2:x + s + 2] = (150, 0, 82) if col != PAPER else (180, 0, 100)
        a[y:y + s, x:x + s] = col
        for e in range(s):                    # the torn edges: a pixel here and there bitten away
            if rnd.random() < 0.3: a[y, x + e] = M
            if rnd.random() < 0.3: a[y + s - 1, x + e] = M
    # the thread: a heading that wanders as three slow waves, a pixel wide, in paper
    x, y, ph = 6.0, 50.0, [rnd.uniform(0, 6.3) for _ in range(3)]
    for i in range(500):
        t = i / 500
        th = 0.5 * math.sin(6.28 * 0.8 * t + ph[0]) + 0.3 * math.sin(6.28 * 1.9 * t + ph[1]) + 0.15 * math.sin(6.28 * 3.1 * t + ph[2])
        x += 0.5 * math.cos(th); y += 0.5 * math.sin(th)
        if 0 <= int(x) < w and 0 <= int(y) < h: a[int(y), int(x)] = PAPER
    save(a, 'mag-a2.png')

def rule30():
    w, h = 264, 96
    a = img(w, h, Y)
    n = w // 2; rows = h // 2
    cells = np.zeros(n, int); cells[n // 2] = 1
    for r in range(rows):
        for i in range(n):
            if cells[i]: a[r * 2:r * 2 + 2, i * 2:i * 2 + 2] = K
        L, R = np.roll(cells, 1), np.roll(cells, -1)
        cells = L ^ (cells | R)
    save(a, 'mag-a3.png')

def collatz():
    # 27's 111 steps, a bar for each, the height its value on a log scale; the peak in magenta
    w, h = 264, 96
    a = img(w, h, O)
    v, seq = 27, [27]
    while v != 1:
        v = v // 2 if v % 2 == 0 else 3 * v + 1; seq.append(v)
    top = math.log(max(seq))
    for i, v in enumerate(seq):
        x = 9 + i * 2; bh = int(round(math.log(v) / top * (h - 14)))
        a[h - 6 - bh:h - 6, x:x + 1] = M if v == max(seq) else K
    a[h - 5:h - 4, 6:w - 6] = K
    save(a, 'mag-a4.png')

def cards():
    w, h = 264, 96
    a = img(w, h, C)
    rnd = random.Random(80)
    for k in range(14):
        cw, ch = 46, 20; x = rnd.randint(-6, w - cw + 6); y = rnd.randint(-4, h - ch + 4)
        x0, y0 = max(0, x), max(0, y); x1, y1 = min(w, x + cw), min(h, y + ch)
        a[min(h - 1, y0 + 2):min(h, y1 + 2), min(w - 1, x0 + 2):min(w, x1 + 2)] = (0, 120, 150)
        a[y0:y1, x0:x1] = CARD
        if 0 <= y < h and 0 <= x < w: a[y:y + 3, x:x + 1] = C; a[y:y + 1, x:x + 3] = C   # the cut corner
        for cc in range(2, cw - 2, 2):
            for rr in range(3, ch - 2, 2):
                if rnd.random() < 0.12 and 0 <= y + rr < h and 0 <= x + cc < w: a[y + rr, x + cc] = K
        if 0 <= y + 1 < h: a[y + 1, max(0, x + 4):max(0, min(w, x + cw - 4))] = CARD_D
    save(a, 'mag-catalogue.png')

if __name__ == '__main__':
    cover(); contents(); schotter(); chance(); rule30(); collatz(); cards()
    from PIL import Image as I
    ims = [I.open(OUT + n) for n in ('mag-contents.png', 'mag-a1.png', 'mag-a2.png', 'mag-a3.png', 'mag-a4.png', 'mag-catalogue.png')]
    sheet = I.new('RGB', (264 * 2 + 10, 96 * 3 + 20), (60, 60, 60))
    for i, im in enumerate(ims): sheet.paste(im, ((i % 2) * 274, (i // 2) * 106))
    sheet.resize((sheet.width * 2, sheet.height * 2), 0).save(UTIL + '/v25/plates.png')
    I.open(OUT + 'mag-cover-field.png').resize((600, 450), 0).save(UTIL + '/v25/cover.png')
