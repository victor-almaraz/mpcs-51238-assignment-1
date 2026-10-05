# v24's light: v23's evening (light.py) with the lamp's part drawn for each lamp, or none when
# it is switched off. Each lamp throws its own light from its own shade: the task lamp a broad
# cone to the desk, the balanced-arm lamp a tight one, the dome a pool straight down, the drum
# shade light up and down its open ends and a glow through its linen. The lamp's light ends
# within REACH of the lamp, so everything further off is lit the same whatever the lamp.
import numpy as np
from light import AMBIENT, EDGE, smooth, grade
from room import W, H

REACH = 245
LAMPS = {  # origin, cones [(direction, cos at edge, softness, weight)], spill, fall, strength, glow, glow radius, colour
    'task': ((115, 158), [((0.72, 0.69), 0.15, 0.75, 1)], 0.2, 85, 0.7, 0.1, 22, (1.0, 0.74, 0.46)),
    'angle': ((116, 160), [((0.74, 0.67), 0.5, 0.4, 1)], 0.08, 80, 0.9, 0.08, 16, (1.0, 0.76, 0.5)),
    'dome': ((108, 157), [((0, 1), 0.05, 0.6, 1)], 0.1, 70, 0.8, 0.12, 26, (1.0, 0.78, 0.54)),
    'ceramic': ((105, 150), [((0, 1), 0.4, 0.45, 1), ((0, -1), 0.45, 0.4, 0.75)], 0.4, 72, 0.6, 0.2, 28, (1.0, 0.7, 0.42)),
}
STATES = list(LAMPS) + ['off']
# the time of day: the night's ambient, and the window's light (its colour and strength)
TIMES = {
    'evening': (np.array([0.52, 0.52, 0.66]), (1.0, 0.62, 0.62), 0.32),
    'morning': (np.array([0.68, 0.66, 0.68]), (1.0, 0.88, 0.66), 0.55),
    'night': (np.array([0.33, 0.35, 0.56]), (0.6, 0.72, 1.0), 0.2),
}
AMB = AMBIENT
def at_time(t):
    global AMB
    AMB = TIMES[t][0]
    return AMB * 0.8

def light_field(state, time='evening'):
    amb, sky, sun = TIMES[time]
    edge = amb * 0.8
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    L = np.zeros((H, W, 3), dtype=np.float32) + amb
    if state != 'off':
        (ox, oy), cones, spill, fr, k, g, gr, warm = LAMPS[state]
        dx, dy = xx - ox, yy - oy
        d = np.hypot(dx, dy) + 1e-3
        cone = np.zeros_like(d)
        for (ux, uy), c0, soft, wgt in cones:
            cone = np.maximum(cone, smooth(((dx * ux + dy * uy) / d - c0) / soft) * wgt)
        fall = 1 / (1 + (d / fr) ** 2)
        glow = 1 / (1 + (d / gr) ** 2)
        cut = smooth((REACH - d) / 45)
        L += ((fall * (spill + (1 - spill) * cone) * k + glow * g) * cut)[..., None] * np.array(warm)
    # the screen and the window, as v23's
    dx, dy = xx - 397, (yy - 152) * 1.3
    d = np.hypot(dx, dy)
    L += (0.42 / (1 + (d / 46) ** 2))[..., None] * np.array([0.55, 0.78, 0.9])
    u = xx - (24 + yy * 0.55)
    shaft = smooth(u / 16) * smooth((96 - u) / 16) * smooth((170 - yy) / 60)
    L += (shaft * sun)[..., None] * np.array(sky)
    # (the room goes on past its right edge to the reading corner, part2, so it falls away only
    # at its left and its top)
    de = np.minimum(xx, yy)
    t = smooth(de / 110)[..., None]
    return edge + (L - edge) * t

def lit_in(F, im, x0, y0):
    a = np.array(im.convert('RGBA')).astype(np.float32)
    h, w = a.shape[:2]
    G = np.ones((h, w, 3), dtype=np.float32) * AMB
    ys0, xs0, ys1, xs1 = max(0, y0), max(0, x0), min(H, y0 + h), min(W, x0 + w)
    if ys1 > ys0 and xs1 > xs0:
        G[ys0 - y0:ys1 - y0, xs0 - x0:xs1 - x0] = F[ys0:ys1, xs0:xs1]
    return grade(a[..., :3] * G), a[..., 3]

def reaches(x, y, w, h):
    """whether any lamp's light can fall on a box"""
    for (ox, oy), *_ in LAMPS.values():
        cx, cy = min(max(ox, x), x + w), min(max(oy, y), y + h)
        if np.hypot(cx - ox, cy - oy) < REACH: return True
    return False
