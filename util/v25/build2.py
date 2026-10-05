# v24's room lit for every state of the lamp (light24.py): each lamp lit as it lights, and the
# room with the lamp switched off. What the lamp's light can reach is drawn once for every
# state (assets/lit/<state>/): the left part of each paper's room, the sprites standing in it,
# the lamp itself (lit, or dark with its shade unlit) and the switch. What it cannot reach is
# drawn once. All are quantized together into one palette.
import os, json, shutil
import numpy as np
from PIL import Image
from art import *
from sheet import all_sprites
import room
from room import px, drop, W, H
from light import make_palette, quantize, grade, EDGE
from light24 import light_field, lit_in, reaches, STATES, LAMPS
from pix import save
from build import KINDS, POS, THINGS, backdrop, OUT, U, HERE
SPLIT = 368                      # the lamp's light ends left of this column
SWITCH = (40, 128)
UNLIT = {(255, 232, 170): (118, 106, 92), (255, 250, 240): (150, 140, 124), (250, 236, 200): (212, 200, 172), (242, 228, 196): (206, 194, 166)}

def dark(im):
    a = np.array(im.convert('RGBA'))
    for c, d in UNLIT.items():
        m = (a[..., :3] == c).all(-1); a[m, :3] = d
    return Image.fromarray(a)

def main():
    S = all_sprites()
    sw = {True: switch(True), False: switch(False)}
    tiles = {'ogee': room.wall_tile(), 'atomic': tile_atomic(), 'trellis': tile_trellis(), 'grass': tile_grass()}
    backs = {}
    for p, t in tiles.items():
        b = backdrop(t, S); drop(b, sw[True], *SWITCH, 2, 2); backs[p] = b
    floor_tile = backs['ogee'].crop((0, H - px(1.6), px(11), H))
    F = {s: light_field(s) for s in STATES}
    # every picture: name, unlit image, place, and the states it is drawn in (None: once)
    pics = []
    for p, b in backs.items(): pics.append(('room-%s.png' % p, b, (0, 0), STATES))
    for k, names in KINDS.items():
        for n in names:
            im = S[n]; x, y = POS[k]
            if k == 'lamp':
                kind = n.split('-')[1]
                pics.append((n + '.png', im, (x, y), [kind])); pics.append((n + '.png', dark(im), (x, y), ['off']))
            else:
                pics.append((n + '.png', im, (x, y), STATES if reaches(x, y, *im.size) else None))
    for n, xy in THINGS.items():
        im = Image.open(U + n); pics.append((n, im, xy, STATES if reaches(*xy, *im.size) else None))
    pics.append(('switch-on.png', sw[True], SWITCH, list(LAMPS))); pics.append(('switch-off.png', sw[False], SWITCH, ['off']))
    lits = []                    # (path, unlit array, lit, alpha, x, y)
    for n, im, (x, y), states in pics:
        for s in (states or ['off']):
            r, al = lit_in(F[s], im, x, y)
            path = ('lit/%s/' % s if states else '') + n
            lits.append((path, np.array(im.convert('RGBA')), r, al, x, y))
    for p, t in tiles.items():
        ta = np.array(t.convert('RGBA')).astype(np.float32)
        lits.append(('tile-%s.png' % p, ta.astype(np.uint8), grade(ta[..., :3] * EDGE), ta[..., 3], 0, 0))
    fa = np.array(floor_tile.convert('RGBA')).astype(np.float32)
    lits.append(('floor-tile.png', fa.astype(np.uint8), grade(fa[..., :3] * EDGE), fa[..., 3], 0, H - 11))
    groups = {}
    for _, raw, r, al, x, y in lits:
        m = al > 0
        keys = raw[..., :3][m].astype(np.int32); vals = r[m]
        code = keys[:, 0] * 65536 + keys[:, 1] * 256 + keys[:, 2]
        order = np.argsort(code); code, vals = code[order], vals[order]
        u, start = np.unique(code, return_index=True)
        for c, a, b in zip(u, start, list(start[1:]) + [len(code)]): groups.setdefault(int(c), []).append(vals[a:b])
    rnd = np.random.RandomState(2); samples = []
    for c, parts in groups.items():
        v = np.concatenate(parts); samples.append(v[rnd.choice(len(v), 300, replace=len(v) < 300)])
    pal = make_palette(samples, 80)
    json.dump(pal.astype(int).tolist(), open(HERE + '/palette-v24.json', 'w'))
    for d in ['lit'] + [n for n in os.listdir(OUT) if n.startswith('room-')]:
        q = OUT + d
        if os.path.isdir(q): shutil.rmtree(q)
        elif os.path.exists(q): os.remove(q)
    out = {}
    for path, raw, r, al, x, y in lits:
        im = quantize(r, al, pal, x, y)
        os.makedirs(os.path.dirname(OUT + path), exist_ok=True)
        if os.path.basename(path).startswith('room-'):
            # the room's left part for each state, its right part (beyond the lamp) once
            name = os.path.basename(path)
            save(im.crop((0, 0, SPLIT, H)), OUT + path)
            if path.startswith('lit/off/'): save(im.crop((SPLIT, 0, W, H)), OUT + name.replace('.png', '-r.png'))
        else:
            save(im, OUT + path)
        out[path] = im
    vary = sorted({os.path.basename(p) for p, *_ in lits if p.startswith('lit/')})
    json.dump({'vary': vary, 'split': SPLIT, 'switch': SWITCH, 'size': sw[True].size}, open(HERE + '/info2.json', 'w'), indent=1)
    # proofs: the ogee room in every state
    for s in STATES:
        pr = Image.new('RGBA', (W, H))
        pr.alpha_composite(out['lit/%s/room-ogee.png' % s].convert('RGBA'), (0, 0))
        pr.alpha_composite(Image.open(OUT + 'room-ogee-r.png').convert('RGBA'), (SPLIT, 0))
        def get(n): return out.get('lit/%s/%s' % (s, n)) or out.get(n)
        for k, names in KINDS.items():
            n = names[0] if k != 'lamp' else ('lamp-%s' % s if s != 'off' else 'lamp-task')
            pr.alpha_composite(get(n + '.png').convert('RGBA'), POS[k])
        for n, xy in THINGS.items():
            if n != 'px-mag-front.png': pr.alpha_composite(get(n).convert('RGBA'), xy)
        pr.alpha_composite(get('switch-%s.png' % ('off' if s == 'off' else 'on')).convert('RGBA'), SWITCH)
        pr.resize((W * 2, H * 2), Image.NEAREST).save(HERE + '/proof2-%s.png' % s)
    print(vary)

if __name__ == '__main__':
    main()
