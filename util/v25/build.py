# v24's room: v23's room with its swappable things lifted out of the backdrop. One backdrop
# per wallpaper (wall, floor, desk, shelf, stool, and the prints' and shelf's shadows, which
# fall the same for every print, each being a rectangle of the same size); a sprite for every
# variation of every place; all lit where they stand by v23's evening light and quantized
# together into one palette, so any choice of things shares the room's colours.
import os as _os; UTIL = _os.path.normpath(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..')); REPO = _os.path.dirname(UTIL)
import os, json
import numpy as np
from PIL import Image
from art import *
from sheet import all_sprites
import room, room2, drawn
from room import px, drop, floor, desk, W, H
from light import lit, make_palette, quantize, grade, EDGE
from pix import save

REPO = REPO
OUT = REPO + '/v25/assets/'
U = HERE + '/../v23/unlit/'
room.OUT = HERE + '/'                                    # room.wall_tile saves its tile here, not in v23
os.makedirs(OUT, exist_ok=True)

PLACES = {'print-wide': (9.4, 3), 'print-narrow': (31.2, 4.2), 'floor-l': (0.6, 24), 'floor-r': (77.6, 29),
          'lamp': (10.6, 19.4), 'desk-plant': (16.4, 21.8), 'mug': (33.4, 27)}
POS = {k: (px(l), px(t)) for k, (l, t) in PLACES.items()}
SHELF = (px(47), px(-0.8))
POS['print-shelf'] = (SHELF[0] + int(round(101 * K)), SHELF[1] + int(round(6 * K)))
KINDS = {'print-wide': ['print-sieve', 'print-pavilion', 'print-polytope'],
         'print-narrow': ['print-dada', 'print-arp', 'print-taeuber'],
         'print-shelf': ['shelf-print-paraboloids', 'shelf-print-glissandi', 'shelf-print-psappha'],
         'floor-l': ['plant-fig', 'plant-snake', 'plant-palm'],
         'floor-r': ['plant-monstera', 'plant-fern', 'plant-rubber'],
         'desk-plant': ['desk-pothos', 'desk-jade', 'desk-cacti'],
         'lamp': ['lamp-task', 'lamp-dome', 'lamp-angle', 'lamp-ceramic'],
         'mug': ['mug-dipped', 'mug-sage', 'mug-striped', 'mug-enamel', 'mug-sieve', 'mug-black', 'mug-cup']}
THINGS = {'px-vol-1.png': (345, 15), 'px-vol-2.png': (367, 20), 'px-vol-3.png': (387, 17), 'px-cover.png': (425, 24),
          'px-mag-back.png': (420, 20), 'px-mag-front.png': (420, 20), 'px-file-box.png': (479, 32), 'px-deck-box.png': (518, 38),
          'px-coding-form.png': (179, 144), 'px-out-tray.png': (262, 178), 'px-computer.png': (338, 119), 'px-tape.png': (462, 135)}

def backdrop(tile, S):
    a = np.zeros((H, W, 4), dtype=np.uint8)
    t = np.array(tile.convert('RGBA'))
    for y in range(H):
        a[y] = np.tile(t[y % t.shape[0]], (W // t.shape[1] + 1, 1))[:W]
    # the wall darkens a step toward the floor, every other pixel
    yy, xx = np.mgrid[0:H, 0:W]
    m = (yy > H * 0.8) & ((xx + yy) % 2 == 0)
    a[m, :3] = (a[m, :3] * 0.82).astype(np.uint8)
    cv = Image.fromarray(a)
    floor(cv); desk(cv)
    for k in ('print-wide', 'print-narrow', 'print-shelf'):
        drop(cv, S[KINDS[k][0]], *POS[k], 2, 2)
    shelf = drawn.shelf()
    drop(cv, shelf, *SHELF, 2, 2); cv.alpha_composite(shelf, SHELF)
    stool = room2.cut('stool.png', 8.4, 9.2, 5)
    cv.alpha_composite(stool, (px(53.1), px(35.8)))
    return cv

def main():
    S = all_sprites()
    tiles = {'ogee': room.wall_tile(), 'atomic': tile_atomic(), 'trellis': tile_trellis(), 'grass': tile_grass()}
    backs = {p: backdrop(t, S) for p, t in tiles.items()}
    floor_tile = backs['ogee'].crop((0, H - px(1.6), px(11), H))
    lits = {}                                            # name -> (unlit array, lit rgb, alpha, x, y)
    def add(name, im, x, y):
        r, al = lit(im, x, y); lits[name] = (np.array(im.convert('RGBA')), r, al, x, y)
    for p, b in backs.items(): add('room-%s.png' % p, b, 0, 0)
    for k, names in KINDS.items():
        for n in names: add(n + '.png', S[n], *POS[k])
    for n, (x, y) in THINGS.items(): add(n, Image.open(U + n), x, y)
    # the paper and the floor past the room, at the room's dark edge
    for p, t in tiles.items():
        ta = np.array(t.convert('RGBA')).astype(np.float32)
        lits['tile-%s.png' % p] = (ta.astype(np.uint8), grade(ta[..., :3] * EDGE), ta[..., 3], 0, 0)
    fa = np.array(floor_tile.convert('RGBA')).astype(np.float32)
    lits['floor-tile.png'] = (fa.astype(np.uint8), grade(fa[..., :3] * EDGE), fa[..., 3], 0, H - 11)
    # the palette by ramps, as v23's: an equal share for every colour of the unlit things
    groups = {}
    for raw, r, al, x, y in lits.values():
        m = al > 0
        keys = raw[..., :3][m].astype(np.int32); vals = r[m]
        code = keys[:, 0] * 65536 + keys[:, 1] * 256 + keys[:, 2]
        for c in np.unique(code): groups.setdefault(int(c), []).append(vals[code == c])
    rnd = np.random.RandomState(2); samples = []
    for c, parts in groups.items():
        v = np.concatenate(parts); samples.append(v[rnd.choice(len(v), 300, replace=len(v) < 300)])
    pal = make_palette(samples, 80)
    json.dump(pal.astype(int).tolist(), open(HERE + '/palette-v24.json', 'w'))
    out = {}
    for n, (raw, r, al, x, y) in lits.items():
        out[n] = quantize(r, al, pal, x, y); save(out[n], OUT + n)
    # the ground colour under each paper's tile, for the page behind the room
    def mode(im):
        a = np.array(im)[..., :3].reshape(-1, 3); v, n = np.unique(a, axis=0, return_counts=True); return '#%02x%02x%02x' % tuple(v[n.argmax()])
    grounds = {p: mode(out['tile-%s.png' % p]) for p in tiles}
    info = {'pos': POS, 'sizes': {n: S[n].size for n in S}, 'tiles': {p: t.size for p, t in tiles.items()}, 'grounds': grounds}
    json.dump(info, open(HERE + '/info.json', 'w'), indent=1)
    # proofs: each paper with a choice of things, at 2x
    for i, p in enumerate(tiles):
        pr = out['room-%s.png' % p].convert('RGBA')
        for k in ('print-wide', 'print-narrow', 'print-shelf', 'floor-l', 'floor-r', 'lamp', 'desk-plant', 'mug'):
            names = KINDS[k]; pr.alpha_composite(out[names[i % len(names)] + '.png'].convert('RGBA'), POS[k])
        for n, xy in THINGS.items():
            if n != 'px-mag-front.png': pr.alpha_composite(out[n].convert('RGBA'), xy)
        pr.resize((W * 2, H * 2), Image.NEAREST).save(HERE + '/proof-%s.png' % p)
    print(len(pal), 'colours', grounds, POS)

if __name__ == '__main__':
    main()
