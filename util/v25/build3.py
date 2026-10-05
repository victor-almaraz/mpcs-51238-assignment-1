# v24's room in motion: frames drawn in the room's palette and light, for CSS to step through.
#   reels      each of the tape player's reels turned through a third of a turn in four frames
#              (its three spokes repeat every 120 degrees), cut from the reel itself: enlarged,
#              turned, and cut back to pixels by majority, so its edges stay hard
#   screen     the Editor's window on the room's computer with output scrolling up through it
#   steam      two wisps rising from the mug, in each light
#   sway       each plant with its top leaves a pixel over, in each light it stands in
import os, json, math, random
import numpy as np
from PIL import Image
from art import Canvas, K, PAPER, INK
from light import quantize
from light24 import light_field, lit_in, STATES, reaches
from pix import pixelate, save
from build import KINDS, POS, OUT, U, HERE
from room import W, H

PAL = np.array(json.load(open(HERE + '/palette-v24.json')), dtype=np.float32)
F = {s: light_field(s) for s in STATES}
TAPE, COMP = (462, 135), (338, 119)

def lq(im, x, y, s='off'):
    r, a = lit_in(F[s], im, x, y)
    return quantize(r, a, PAL, x, y)

def sheet(frames):
    w, h = frames[0].size
    s = Image.new('RGBA', (w * len(frames), h))
    for i, f in enumerate(frames): s.paste(f, (i * w, 0))
    return s

def reels():
    src = Image.open(U + 'px-tape.png').convert('RGBA')
    out = {}
    for side, (cx, cy) in (('l', (25.5, 24.5)), ('r', (79, 25))):
        R = 16
        x0, y0 = int(cx - R), int(cy - R)
        crop = src.crop((x0, y0, x0 + 2 * R, y0 + 2 * R))
        big = crop.resize((crop.width * 8, crop.height * 8), Image.NEAREST)
        yy, xx = np.mgrid[0:2 * R, 0:2 * R]
        mask = ((xx + 0.5 - (cx - x0)) ** 2 + (yy + 0.5 - (cy - y0)) ** 2) < 15.2 ** 2
        frames = []
        for k in range(4):
            if k == 0: f = crop.copy()
            else:
                rb = big.rotate(-30 * k, resample=Image.NEAREST, center=((cx - x0) * 8, (cy - y0) * 8))
                f = pixelate(rb, 2 * R, 2 * R, line_bias=0.1)
                # where the turn left a pixel bare, the reel's own pixel stays
                fa, ca = np.array(f), np.array(crop)
                bare = fa[..., 3] == 0; fa[bare] = ca[bare]; f = Image.fromarray(fa)
            fa = np.array(f); fa[~mask, 3] = 0
            frames.append(lq(Image.fromarray(fa), TAPE[0] + x0, TAPE[1] + y0))
        save(sheet(frames), OUT + 'anim/reel-%s.png' % side)
        out[side] = (x0, y0, 2 * R)
    return out

def screen():
    # the Editor's text area (room2.computer: the window at 17, 14 in screen units, 32 x 24),
    # its lines of output climbing a pixel row at a time and new ones printing at the foot
    src = Image.open(U + 'px-computer.png').convert('RGBA')
    sx, sy = 21, 9                                  # the screen's corner in the sprite
    def at(u): return int(u * K)
    x0, y0, x1, y1 = sx + at(19), sy + at(20), sx + at(41), sy + at(35)
    w, h = x1 - x0, y1 - y0
    base = np.array(src.crop((x0, y0, x1, y1)))
    paper = base[h // 2, w - 2].copy()               # the window's paper, from the sprite
    rnd = random.Random(1956)
    lines = [rnd.choice([4, 9, 14, 18, 11, 6, 16, 20]) for _ in range(40)]
    frames = []
    for k in range(8):
        a = base.copy(); a[:, :, :3] = paper[:3]; a[:, :, 3] = 255
        for i, ln in enumerate(lines):
            y = 1 + i * 2 - k * 2 + (0)
            if 0 <= y < h - 1:
                L = min(ln, w - 3) if i < k + 6 else 0
                a[y, 2:2 + L, :3] = INK
                if i % 5 == 0: a[y, 1, :3] = (134, 123, 104)
        frames.append(lq(Image.fromarray(a), COMP[0] + x0, COMP[1] + y0))
    save(sheet(frames), OUT + 'anim/screen.png')
    return (x0, y0, w, h)

def steam():
    # two wisps that rise and sway, thinning to every other pixel as they climb
    mx, my = POS['mug']
    w, h = 14, 18
    x, y = mx + 3, my - h + 2
    frames = {s: [] for s in STATES}
    col = (236, 232, 226)
    for k in range(6):
        a = np.zeros((h, w, 4), dtype=np.uint8)
        for wisp, (bx, ph) in enumerate(((4, 0.0), (8, 2.4))):
            for j in range(h - 3):
                yy = h - 4 - j
                t = (j + k * 3) / 18 * 2 * math.pi
                xx = int(round(bx + 1.6 * math.sin(t + ph) * (0.4 + j / h)))
                life = ((j + k * 3 + wisp * 7) % 18) / 18
                if life > 0.75: continue
                if j > h * 0.45 and (xx + yy) % 2: continue
                if 0 <= xx < w: a[yy, xx, :3] = col; a[yy, xx, 3] = 255
        im = Image.fromarray(a)
        for s in STATES: frames[s].append(lq(im, x, y, s))
    for s in STATES: save(sheet(frames[s]), OUT + 'anim/lit/%s/steam.png' % s)
    return (x, y, w, h)

def sway():
    # every plant's second frame: its top leaves (the rows above a third of its height) a pixel
    # toward the room's centre, as if the air moved; from the picture already in the page
    done = []
    for k in ('floor-l', 'floor-r', 'desk-plant'):
        for n in KINDS[k]:
            for path in ['lit/%s/%s.png' % (s, n) for s in STATES] + [n + '.png']:
                p = OUT + path
                if not os.path.exists(p): continue
                a = np.array(Image.open(p).convert('RGBA'))
                rows = np.where(a[..., 3].any(1))[0]
                top = rows[0]; cut = top + int((rows[-1] - top) * (0.3 if k != 'desk-plant' else 0.35))
                b = a.copy()
                d = 1 if k == 'floor-l' else -1
                b[:cut] = 0
                b[:cut, max(0, d):a.shape[1] + min(0, d)] = a[:cut, max(0, -d):a.shape[1] - max(0, d)]
                q = OUT + 'anim/' + path.replace('.png', '-sway.png')
                os.makedirs(os.path.dirname(q), exist_ok=True)
                Image.fromarray(b).save(q, optimize=True)
                done.append(path)
    return done

if __name__ == '__main__':
    for s in STATES: os.makedirs(OUT + 'anim/lit/%s' % s, exist_ok=True)
    info = {'reels': reels(), 'screen': screen(), 'steam': steam(), 'sway': len(sway())}
    json.dump(info, open(HERE + '/info3.json', 'w'))
    print(info)
