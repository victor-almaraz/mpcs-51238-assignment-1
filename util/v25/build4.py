# v24's room at three times of day (light24.TIMES): morning, evening and night, each with its
# own ambient and its own light through the window, and within each the five lights of the
# lamp (build2). Everything is lit for every time and quantized together into one palette;
# each time's pictures go in assets/<time>/, its loops in assets/<time>/anim/ (build3).
import os, json, shutil
import numpy as np
from PIL import Image
from art import *
from sheet import all_sprites
import room
from room import px, drop, W, H
from light import make_palette, quantize, grade
import light24
from light24 import light_field, lit_in, reaches, STATES, LAMPS, TIMES
from pix import save
from build import KINDS, POS, THINGS, backdrop, OUT as ROOT, U, HERE
from build2 import SPLIT, SWITCH, dark
import build3
import part2

def gather(t, S, sw, tiles, backs, floor_tile, backs2):
    edge = light24.at_time(t)
    F = {s: light_field(s, t) for s in STATES}
    pics = []
    for p, b in backs.items(): pics.append(('room-%s.png' % p, b, (0, 0), STATES))
    for k, names in KINDS.items():
        for n in names:
            im = S[n]; x, y = POS[k]
            if k == 'lamp':
                pics.append((n + '.png', im, (x, y), [n.split('-')[1]])); pics.append((n + '.png', dark(im), (x, y), ['off']))
            else:
                pics.append((n + '.png', im, (x, y), STATES if reaches(x, y, *im.size) else None))
    for n, xy in THINGS.items():
        im = back_issues() if n == 'px-mag-back.png' else Image.open(U + n)   # the back issues behind the one in front: the other two magazines
        pics.append((n, im, xy, STATES if reaches(*xy, *im.size) else None))
    # the other magazines' covers, for the one in front when it is the issue last opened
    for n, im in (('px-cover-event.png', cover_event()), ('px-cover-gesso.png', cover_gesso()), ('px-cover-cons.png', cover_cons()), ('px-cover-silver.png', cover_silver())):
        pics.append((n, im, THINGS['px-cover.png'], None))
    # under the desk: the card reader and line printer at the left, the UPIC's tablet at the right
    for n, im, xy in (('px-reader.png', reader(), (140, 247)), ('px-upic.png', upic(), (445, 229)), ('px-timer.png', part2.kitchen_timer(), (552, 193))):
        pics.append((n, im, xy, STATES if reaches(*xy, *im.size) else None))
    pics.append(('switch-on.png', sw[True], SWITCH, list(LAMPS))); pics.append(('switch-off.png', sw[False], SWITCH, ['off']))
    lits = []
    # the second wall, round the corner (part2): the lamp does not reach it, so it is drawn once
    # a time, in its own light; its loops' frames go in as anim2 and are put in sheets after
    F2 = part2.light2(TIMES[t][0])
    two = [('room2-%s.png' % p, b, (0, 0)) for p, b in backs2.items()] + [(n, im, xy) for n, (im, xy) in part2.sprites2().items()]
    for n, im, (x, y) in two:
        r, al = lit_in(F2, im, x, y); lits.append((n, np.array(im.convert('RGBA')), r, al, x, y))
    for n, (frames, (x, y)) in part2.anims2().items():
        for i, im in enumerate(frames):
            r, al = lit_in(F2, im, x, y); lits.append(('anim2/%s/%d' % (n, i), np.array(im.convert('RGBA')), r, al, x, y))
    for n, im, (x, y), states in pics:
        for s in (states or ['off']):
            r, al = lit_in(F[s], im, x, y)
            lits.append((('lit/%s/' % s if states else '') + n, np.array(im.convert('RGBA')), r, al, x, y))
    for p, ti in tiles.items():
        ta = np.array(ti.convert('RGBA')).astype(np.float32)
        lits.append(('tile-%s.png' % p, ta.astype(np.uint8), grade(ta[..., :3] * edge), ta[..., 3], 0, 0))
    fa = np.array(floor_tile.convert('RGBA')).astype(np.float32)
    lits.append(('floor-tile.png', fa.astype(np.uint8), grade(fa[..., :3] * edge), fa[..., 3], 0, H - 11))
    return F, lits

def main():
    S = all_sprites()
    sw = {True: switch(True), False: switch(False)}
    tiles = {'ogee': room.wall_tile(), 'atomic': tile_atomic(), 'trellis': tile_trellis(), 'grass': tile_grass()}
    backs = {}
    for p, ti in tiles.items():
        b = backdrop(ti, S); drop(b, sw[True], *SWITCH, 2, 2); backs[p] = b
    backs2 = {p: part2.backdrop2(tiles[p], b) for p, b in backs.items()}
    floor_tile = backs['ogee'].crop((0, H - px(1.6), px(11), H))
    every = {t: gather(t, S, sw, tiles, backs, floor_tile, backs2) for t in TIMES}
    # one palette for all three times, an equal share for every colour of the unlit things
    groups = {}
    for t, (F, lits) in every.items():
        for _, raw, r, al, x, y in lits:
            m = al > 0
            keys = raw[..., :3][m].astype(np.int32); vals = r[m]
            code = keys[:, 0] * 65536 + keys[:, 1] * 256 + keys[:, 2]
            order = np.argsort(code, kind='stable'); code, vals = code[order], vals[order]
            u, start = np.unique(code, return_index=True)
            for c, a, b in zip(u, start, list(start[1:]) + [len(code)]): groups.setdefault(int(c), []).append(vals[a:b])
    rnd = np.random.RandomState(2); samples = []
    for c, parts in groups.items():
        v = np.concatenate(parts); samples.append(v[rnd.choice(len(v), 360, replace=len(v) < 360)])
    pal = make_palette(samples, 96)
    json.dump(pal.astype(int).tolist(), open(HERE + '/palette-v24.json', 'w'))
    # the old single-time pictures go
    for n in os.listdir(ROOT):
        if n in ('st', 'pics', 'cursor-arrow.png', 'cursor-hand.png', 'oak-tile.png'): continue
        q = ROOT + n
        shutil.rmtree(q) if os.path.isdir(q) else os.remove(q)
    # the turns round the corner, and their cursors: the page's own, unlit
    for d, n in ((1, 'r'), (-1, 'l')):
        save(part2.turn_tab(d), ROOT + 'turn-%s.png' % n); save(part2.turn_cursor(d), ROOT + 'cursor-turn-%s.png' % n)
    grounds = {}
    for t, (F, lits) in every.items():
        OUT = ROOT + t + '/'
        sheets = {}
        for path, raw, r, al, x, y in lits:
            im = quantize(r, al, pal, x, y)
            if path.startswith('anim2/'):
                _, n, i = path.split('/'); sheets.setdefault(n, {})[int(i)] = im; continue
            os.makedirs(os.path.dirname(OUT + path), exist_ok=True)
            if os.path.basename(path).startswith('room-'):
                save(im.crop((0, 0, SPLIT, H)), OUT + path)
                if path.startswith('lit/off/'): save(im.crop((SPLIT, 0, W, H)), OUT + os.path.basename(path).replace('.png', '-r.png'))
            else:
                save(im, OUT + path)
            if path.startswith('tile-'):
                a = np.array(im)[..., :3].reshape(-1, 3); v, c = np.unique(a, axis=0, return_counts=True)
                grounds.setdefault(t, {})[path[5:-4]] = '#%02x%02x%02x' % tuple(v[c.argmax()])
        for n, fr in sheets.items():
            fr = [fr[i] for i in sorted(fr)]
            sh = Image.new('RGBA', (fr[0].width * len(fr), fr[0].height))
            for i, f in enumerate(fr): sh.paste(f, (i * f.width, 0))
            os.makedirs(OUT + 'anim', exist_ok=True); save(sh, OUT + 'anim/' + n)
        # the loops, in this time's light
        light24.at_time(t)
        build3.OUT, build3.F, build3.PAL = OUT, F, pal
        for s in STATES: os.makedirs(OUT + 'anim/lit/%s' % s, exist_ok=True)
        build3.reels(); build3.screen(); build3.steam(); build3.sway()
        print(t, 'done')
    json.dump(grounds, open(HERE + '/grounds.json', 'w'), indent=1)
    print(grounds)

if __name__ == '__main__':
    main()
