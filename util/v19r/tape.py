# The tape machine, twice: as it stands on the desk in the room (one picture), and as the
# parts of the tape player's deck (a plate of guides and screws, a reel flange that turns,
# and the head cover that the tape runs under), which the page lays round its live tape.
import math, random
from mcm import *
from render import render, REPO
OUT = REPO + '/v19/assets'

GRAPH = '#2b2926'

def reel_flange(cx, cy, R, holes='windows', col=None, rim=None, ink=P['ink'], lw=0.3, hub_r=None, shade=True):
    """a seven-inch reel's front flange, its three windows open on the tape pack under it
       (drawn with fill-rule evenodd, so the windows are holes)"""
    col = col or P['alu']; rim = rim or dark(col, 0.18)
    hub_r = hub_r or R * 0.25
    d = ['M%s,%s a%s,%s 0 1 0 %s,0 a%s,%s 0 1 0 %s,0 Z' % (f(cx - R), f(cy), f(R), f(R), f(2 * R), f(R), f(R), f(-2 * R))]
    r0, r1 = R * 0.33, R * 0.88
    for i in range(3):
        a0 = math.radians(-90 + i * 120 + 16); a1 = math.radians(-90 + i * 120 + 104)
        # windows with rounded ends: an outer arc, a round corner, an inner arc
        d.append('M%s,%s A%s,%s 0 0 1 %s,%s L%s,%s A%s,%s 0 0 0 %s,%s Z' % (
            f(cx + r1 * math.cos(a0)), f(cy + r1 * math.sin(a0)), f(r1), f(r1), f(cx + r1 * math.cos(a1)), f(cy + r1 * math.sin(a1)),
            f(cx + r0 * math.cos(a1)), f(cy + r0 * math.sin(a1)), f(r0), f(r0), f(cx + r0 * math.cos(a0)), f(cy + r0 * math.sin(a0))))
    shape = ' '.join(d)
    reel_flange.n = getattr(reel_flange, 'n', 0) + 1
    cid = 'fl%d' % reel_flange.n
    out = ['<clipPath id="%s">%s</clipPath>' % (cid, path(shape, '#000', fill_rule='evenodd', clip_rule='evenodd')),
           path(shape, col, fill_rule='evenodd')]
    # the flange lit from the upper left: a crescent of shade on the lower right, in dots
    if shade: out.append(g(halftone(cx - R, cy - R, cx + R, cy + R,
                          lambda x, y: max(0, ((x - cx) + (y - cy)) / (2 * R) * 1.4 - 0.15), R * 0.045, rim),
                 clip_path='url(#%s)' % cid))
    out.append(path(shape, 'none', stroke=ink, stroke_width=lw, transform='translate(%s %s)' % (f(-lw * 0.9), f(lw * 0.6)), opacity=0.8))
    # the hub, its three drive slots
    out.append(circle(cx, cy, hub_r, light(col, 0.4)))
    out.append(circle(cx, cy, hub_r, 'none', stroke=ink, stroke_width=lw * 0.8))
    out.append(circle(cx, cy, hub_r * 0.34, ink))
    for i in range(3):
        a = math.radians(-90 + i * 120)
        out.append(rect(-hub_r * 0.1, -hub_r * 0.95, hub_r * 0.2, hub_r * 0.4, ink,
                        transform='translate(%s %s) rotate(%s)' % (f(cx), f(cy), f(-90 + i * 120 + 90))))
    return out, shape

# ---------------------------------------------------------------- the room picture --
def room():
    W, H = 150, 106
    S = 5
    defs = [print_filter('pr', 1.4, 0.2, 31), grain_filter('gr', 1.0, 0.06, 8), grain_filter('gr2', 1.6, 0.05, 9),
            blur_filter('soft', 0.8)]
    o = []
    # the teak case, on two black feet
    cx0, cy0, cw, chh = 0, 0, W, H - 3
    o.append(rect(16, H - 3.5, 8, 3.5, P['ink'])); o.append(rect(W - 24, H - 3.5, 8, 3.5, P['ink']))
    case = [path(rrect(cx0, cy0, cw, chh, 3.2), P['teak'])]
    case.append(rect(0, 0, cw, 2.2, P['teakl']))
    case.append(rect(0, chh - 2.4, cw, 2.4, P['teakd']))
    rnd = random.Random(12)
    for k in range(14):
        yy = rnd.uniform(3, chh - 4); x1 = rnd.uniform(-20, cw); x2 = x1 + rnd.uniform(40, 110)
        d = 'M%s,%s C%s,%s %s,%s %s,%s' % (f(x1), f(yy), f(x1 + 25), f(yy - 1.6), f(x2 - 25), f(yy + 1.4), f(x2), f(yy))
        case.append(path(d, 'none', stroke=P['teakd'], stroke_width=0.28, opacity=0.55))
    o.append(g(g(case, clip_path='url(#case)'), filter='url(#gr)'))
    defs.append(clip('case', path(rrect(cx0, cy0, cw, chh, 3.2), '#000')))
    # the deck plate: brushed aluminium above, a graphite strip below for the keys and meter
    px, py, pw, ph = 6, 5.5, W - 12, chh - 11
    strip_h = 25
    plate = [rect(px, py, pw, ph, P['alu'])]
    plate.append(hatch(px, py, px + pw, py + ph - strip_h, 0.6, '#ffffff', 0.12, angle=0, opacity=0.35))
    plate.append(hatch(px, py + 0.3, px + pw, py + ph - strip_h, 1.3, P['steeld'], 0.08, angle=0, opacity=0.35))
    plate.append(rect(px, py + ph - strip_h, pw, strip_h, GRAPH))
    plate.append(rect(px, py + ph - strip_h, pw, 0.5, light(GRAPH, 0.2)))
    o.append(g(plate, clip_path='url(#plate)'))
    defs.append(clip('plate', rect(px, py, pw, ph, '#000')))
    o.append(rect(px, py, pw, ph, 'none', stroke=dark(P['teakd'], 0.3), stroke_width=0.4))
    # screws at the corners of the plate
    for sx, sy in ((px + 3, py + 3), (px + pw - 3, py + 3)):
        o.append(circle(sx, sy, 1.0, P['steel'], stroke=P['steeld'], stroke_width=0.2)); o.append(line(sx - 0.7, sy - 0.4, sx + 0.7, sy + 0.4, P['steeld'], 0.22))
    # reels: their shadows on the plate, the tape packs, the flanges
    ry = py + 30
    R = 26
    reels = [(px + 33, 22.5), (px + pw - 33, 12.5)]
    for rx, pack in reels:
        o.append(circle(rx + 1.6, ry + 1.4, R + 0.3, '#28180c', opacity=0.22, filter='url(#soft)'))
        o.append(circle(rx, ry, R, dark(P['alu'], 0.35)))
        o.append(circle(rx, ry, pack, P['tape']))
        o.append(circle(rx, ry, pack, 'none', stroke=light(P['tape'], 0.2), stroke_width=0.25, opacity=0.8))
        for k in range(1, 6):
            o.append(circle(rx, ry, pack * (1 - k * 0.12), 'none', stroke=dark(P['tape'], 0.25), stroke_width=0.15, opacity=0.5))
    # the tape path: down from each pack to the guides, under the head cover
    gl, gr_, gy = px + 52, px + pw - 52, py + ph - strip_h - 7
    (lx, lp), (rx2, rp) = reels
    o.append(line(lx - lp + 0.3, ry, gl - 2.2, gy, P['tape'], 0.7))
    o.append(line(gl, gy + 2.2, gr_, gy + 2.2, P['tape'], 0.7))
    o.append(line(rx2 + rp - 0.3, ry, gr_ + 2.2, gy, P['tape'], 0.7))
    for rx, pack in reels:
        fl, _ = reel_flange(rx, ry, R, lw=0.32)
        o.append(g(fl, transform='rotate(%d %s %s)' % (17 if rx < W / 2 else 71, f(rx), f(ry))))
    for gx in (gl, gr_):
        o.append(circle(gx, gy, 2.2, P['steel'], stroke=P['ink'], stroke_width=0.3)); o.append(circle(gx, gy, 0.7, P['ink']))
    # the head cover, a graphite block with a slot and the record lamp
    hx, hw = W / 2 - 11, 22
    o.append(path(rrect(hx, gy - 2.5, hw, 8.5, (2.2, 2.2, 0, 0)), GRAPH))
    o.append(rect(hx + 3, gy - 0.8, hw - 6, 1.0, light(GRAPH, 0.25)))
    o.append(circle(hx + hw - 3, gy + 2.6, 0.8, P['accent']))
    # the speed marks, engraved between the reels
    o.append(text(W / 2, py + 9, 'TAPE', 2.6, P['ink'], 'Work Sans', 600, 0.42, 'middle'))
    o.append(text(W / 2, py + 13.2, '7½ · 15 IPS', 1.9, P['soft'], 'Jost', 400, 0.16, 'middle'))
    # the strip: the transport keys, two knobs and the level meter
    sy = py + ph - strip_h
    keys = []
    kx = px + 6
    for k in range(5):
        c = P['accent'] if k == 2 else P['cream']
        keys.append(path(rrect(kx, sy + 5, 9.2, 15, (0.6, 0.6, 1.4, 1.4)), c))
        keys.append(rect(kx, sy + 5, 9.2, 1.4, dark(c, 0.18)))
        keys.append(rect(kx + 7.6, sy + 6.4, 1.6, 13.6, dark(c, 0.1)))
        kx += 10.4
    glyphs = [('◀◀', 2.6), ('■', 3.2), ('▶', 3.2), ('▶▶', 2.6), ('❚❚', 2.6)]
    kx = px + 6
    for k, (gch, gs) in enumerate(glyphs):
        keys.append(text(kx + 4.6, sy + 16.6, gch, gs, P['paper'] if k == 2 else P['soft'], 'Work Sans', 600, 0, 'middle'))
        kx += 10.4
    o.append(g(keys, filter='url(#gr2)'))
    # two knobs: tempo and level
    for kk, nx in enumerate((px + 66, px + 78)):
        o.append(circle(nx, sy + 12.5, 4.6, P['ink'])); o.append(circle(nx - 0.6, sy + 11.9, 3.6, light(P['ink'], 0.12)))
        a = math.radians(-130 + kk * 95)
        o.append(line(nx, sy + 12.5, nx + 3.4 * math.sin(a), sy + 12.5 - 3.4 * math.cos(a), P['paper'], 0.45))
        for t in range(7):
            aa = math.radians(-135 + t * 45)
            o.append(line(nx + 5.6 * math.sin(aa), sy + 12.5 - 5.6 * math.cos(aa), nx + 6.5 * math.sin(aa), sy + 12.5 - 6.5 * math.cos(aa), P['steeld'], 0.22))
    # the meter: a cream window, an arc of marks running into terracotta, a needle
    mx, my, mw, mh = px + pw - 38, sy + 4, 32, 17
    met = [path(rrect(mx, my, mw, mh, 1.2), P['cream'])]
    acx, acy, ar = mx + mw / 2, my + mh + 5, 17
    for t in range(13):
        a = math.radians(-40 + t * 80 / 12)
        c = P['accent'] if t >= 9 else P['ink']
        L = 2.2 if t % 3 == 0 else 1.2
        met.append(line(acx + ar * math.sin(a), acy - ar * math.cos(a), acx + (ar - L) * math.sin(a), acy - (ar - L) * math.cos(a), c, 0.3))
    met.append(path('M%s,%s A%s,%s 0 0 1 %s,%s' % (f(acx + ar * math.sin(math.radians(-40))), f(acy - ar * math.cos(math.radians(-40))), f(ar), f(ar),
                                                  f(acx + ar * math.sin(math.radians(40))), f(acy - ar * math.cos(math.radians(40)))), 'none', stroke=P['ink'], stroke_width=0.2))
    a = math.radians(-14)
    met.append(line(acx, acy, acx + (ar + 0.5) * math.sin(a), acy - (ar + 0.5) * math.cos(a), P['ink'], 0.35))
    met.append(text(mx + 2.4, my + mh - 2.2, 'VU', 2.2, P['ink'], 'Work Sans', 600, 0.1))
    met.append(rect(mx, my, mw, 3, '#000', opacity=0.08))
    o.append(g(g(met, clip_path='url(#meter)'), filter='url(#gr2)'))
    defs.append(clip('meter', path(rrect(mx, my, mw, mh, 1.2), '#000')))
    o.append(path(rrect(mx, my, mw, mh, 1.2), 'none', stroke=P['ink'], stroke_width=0.5))
    return render('tape-room', g(o, filter='url(#pr)'), W, H, S, OUT, defs=''.join(defs))

# ------------------------------------------------------------ the tape player's deck --
# in the units of the deck's SVG (viewBox 0 0 520 250): reels at (120,112) and (400,112),
# flange radius 100, guides at (200,232) and (320,232)
def deck_parts():
    S = 3
    # the flange that turns, drawn round its own centre (102, 102), 204 square; unshaded, as
    # shading would turn with it
    fl, _ = reel_flange(102, 102, 100, lw=1.0, shade=False)
    render('reel', g(fl, filter='url(#pr)'), 204, 204, S, OUT, defs=print_filter('pr', 0.5, 0.21, 41))
    # the plate under the reels: their spindle shadows, tension arms, guides and screws
    o = []
    for cx in (120, 400):
        o.append(circle(cx + 5, 117, 102, '#28180c', opacity=0.18, filter='url(#soft)'))
        o.append(circle(cx, 112, 100, dark(P['alu'], 0.35)))
    for gx in (200, 320):
        o.append(line(gx, 232, gx + (-46 if gx < 260 else 46), 196, P['steeld'], 4, stroke_linecap='round'))
        o.append(circle(gx + (-46 if gx < 260 else 46), 196, 4, P['steel'], stroke=P['ink'], stroke_width=0.8))
        o.append(circle(gx, 232, 8.5, P['steel'], stroke=P['ink'], stroke_width=1))
        o.append(circle(gx, 232, 2.6, P['ink']))
    o.append(text(120, 236, 'SUPPLY', 7, P['soft'], 'Jost', 400, 0.32, 'middle'))
    o.append(text(400, 236, 'TAKE-UP', 7, P['soft'], 'Jost', 400, 0.32, 'middle'))
    render('deck', g(o, filter='url(#pr)'), 520, 250, S, OUT,
           defs=print_filter('pr', 0.6, 0.21, 43) + blur_filter('soft', 3))
    # the head cover over the tape, with the capstan and the record lamp
    hs = rrect(226, 214, 68, 32, (8, 8, 2, 2))
    h = ['<clipPath id="hc">%s</clipPath>' % path(hs, '#000'), path(hs, GRAPH),
         rect(234, 220, 52, 4, light(GRAPH, 0.28)),
         g([rect(226, 214, 68, 3, light(GRAPH, 0.12)),
            halftone(260, 214, 294, 246, lambda x, y: (x - 260) / 34 * 0.8, 1.6, '#000', opacity=0.5)], clip_path='url(#hc)'),
         circle(284, 236, 2.4, P['accent']),
         text(236, 240, 'REC · PB', 5, P['steeld'], 'Jost', 400, 0.2)]
    render('head', g(h, filter='url(#pr)'), 520, 250, S, OUT, defs=print_filter('pr', 0.6, 0.21, 47))

if __name__ == '__main__':
    room(); deck_parts()
