# v23's computer at evening: the screen lights itself, so it is not dimmed by the room's
# light, but it is graded as the room is (light.grade): dark tones lean violet-blue, highlights
# roll off, and a faint cool cast lies over it, as a screen's does in a dark room. Each of the
# palette's 46 colours maps to its graded colour, so the screen keeps its ramps and its paper.
import json
import numpy as np
from light import grade
from pix import HERE
COOL = np.array([0.95, 0.97, 1.03]) * 0.78   # a little dimmer than daylight, and cool
base = np.array(json.load(open(HERE + '/palette.json')), dtype=np.float32)
graded = np.clip(np.round(grade(base * COOL)), 0, 255).astype(int)
MAP = {tuple(int(v) for v in b): tuple(int(v) for v in g) for b, g in zip(base, graded)}
def hexc(c): return '#%02x%02x%02x' % tuple(c)
if __name__ == '__main__':
    json.dump([list(g) for g in graded.tolist()], open(HERE + '/palette-screen.json', 'w'))
    for b, g in list(MAP.items())[:46]: print(hexc(b), '->', hexc(g))
