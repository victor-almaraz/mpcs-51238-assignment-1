# v23's room relit for evening (light.py): the unlit backdrop and sprites (unlit/), each lit
# where it stands in the room, then all quantized together into the lit room's own palette.
import json
import numpy as np
from PIL import Image
from light import lit, make_palette, quantize, field, grade, AMBIENT, EDGE
from pix import HERE, save
from room import OUT, W, H
U = HERE + '/unlit/'
PLACES = {'px-vol-1.png': (345, 15), 'px-vol-2.png': (367, 20), 'px-vol-3.png': (387, 17), 'px-cover.png': (425, 24),
          'px-mag-back.png': (420, 20), 'px-mag-front.png': (420, 20), 'px-file-box.png': (479, 32), 'px-deck-box.png': (518, 38),
          'px-coding-form.png': (179, 144), 'px-out-tray.png': (262, 178), 'px-computer.png': (338, 119), 'px-tape.png': (462, 135)}
back_rgb, back_a = lit(Image.open(U + 'room.png'), 0, 0)
sprites = {n: lit(Image.open(U + n), x, y) for n, (x, y) in PLACES.items()}
# the paper and floor that run on past the room take the light at the room's dark edges
tile = Image.open(U + 'wall-tile.png').convert('RGBA'); ta = np.array(tile).astype(np.float32)
edge = EDGE
tile_rgb = grade(ta[..., :3] * edge)
fl = Image.open(U + 'floor-tile.png').convert('RGBA'); fa = np.array(fl).astype(np.float32)
fedge = EDGE
floor_rgb = grade(fa[..., :3] * fedge)
# the palette by ramps: every colour of the unlit room gets the same share of the cut, taken
# from the light it actually stands in, so each keeps its ramp from shadow to lamplight
src = [(np.array(Image.open(U + 'room.png').convert('RGBA')), back_rgb, back_a)] + \
      [(np.array(Image.open(U + n).convert('RGBA')), sprites[n][0], sprites[n][1]) for n in PLACES]
groups = {}
for raw, rgbl, al in src:
    m = al > 0
    keys = raw[..., :3][m].astype(np.int32); vals = rgbl[m]
    code = keys[:, 0] * 65536 + keys[:, 1] * 256 + keys[:, 2]
    for c in np.unique(code):
        groups.setdefault(int(c), []).append(vals[code == c])
rnd = np.random.RandomState(2); samples = []
for c, parts in groups.items():
    v = np.concatenate(parts)
    samples.append(v[rnd.choice(len(v), 400, replace=len(v) < 400)])
pal = make_palette(samples, 56)
json.dump(pal.astype(int).tolist(), open(HERE + '/palette-evening.json', 'w'))
save(quantize(back_rgb, back_a, pal, 0, 0), OUT + 'room.png')
for n, (x, y) in PLACES.items():
    r, a = sprites[n]; save(quantize(r, a, pal, x, y), OUT + n)
save(quantize(tile_rgb, ta[..., 3], pal, 0, 0), OUT + 'wall-tile.png')
save(quantize(floor_rgb, fa[..., 3], pal, 0, H - 11), OUT + 'floor-tile.png')
# a proof: the room with its sprites, at 2x
proof = Image.open(OUT + 'room.png').convert('RGBA')
for n, (x, y) in PLACES.items(): proof.alpha_composite(Image.open(OUT + n).convert('RGBA'), (x, y))
proof.resize((W * 2, H * 2), Image.NEAREST).save(HERE + '/evening2x.png')
print(len(pal), 'colours')
