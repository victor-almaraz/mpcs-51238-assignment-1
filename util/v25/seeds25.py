# The record player and the tomato timer, drawn first as vectors and cut to pixels, as v19r's
# seeds were for the room before them (the tomato's body and calyx are painted from a solid, its
# stem drawn as a vector). Each drawing is SVG in its own pixels (one unit an art
# pixel), rendered large through headless Chrome (v19r/render.py), then cut cell by cell: every
# rendered pixel snaps to the drawing's own short palette and each cell takes the colour most
# of it has, so soft gradients in the vector come out as clean bands of colour.
#
#   python3.11 seeds25.py        writes seeds25/*.png (the room's two sprites, unlit, which
#                                part2.py and build4.py light) and the two stations' pictures
#                                into ../../v25/assets/st/ (rec-deck.png, pomo-body.png),
#                                and a proof, seeds25-proof.png
import os as _os; UTIL = _os.path.normpath(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..')); REPO = _os.path.dirname(UTIL)
import sys, os, math
sys.path.insert(0, UTIL + '/v19r'); sys.path.insert(0, UTIL + '/v23')
import numpy as np
from PIL import Image

HERE = UTIL + '/v25/'
OUT = HERE + 'seeds25/'
ST = REPO + '/v25/assets/st/'

def hexrgb(h): h = h.lstrip('#'); return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))

# ---------------------------------------------------------------- the palettes
# hue-shifted ramps: shadows lean cool, lights lean warm
TEAL = ['#16292e', '#22444a', '#2f5d62', '#3f7478', '#5a9294', '#80b2ae']
CREAM = ['#6f604c', '#9a8a6e', '#c3b291', '#e2d5b6', '#f5eedb', '#fffaee']
GOLD = ['#4f3a1e', '#87652c', '#be9446', '#e3c278', '#f7e6b0']
STEEL = ['#25272e', '#474b55', '#767b86', '#a7acb4', '#d3d6da', '#f4f5f6']
BLACK = ['#0b0a0d', '#141317', '#1e1d23', '#2c2b33', '#45444e', '#6a6974']
RED = ['#3e1022', '#651a24', '#8f2423', '#b53326', '#d84a30', '#ec7448', '#f7a774', '#fff1dc']
GREEN = ['#1b2e1e', '#2a4a26', '#3e6a2e', '#5b8c38', '#82b048', '#b4d670']
LABEL = ['#7c2420', '#b8382c', '#d9584a']

def pal(*ramps): return [hexrgb(c) for r in ramps for c in r]

# ---------------------------------------------------------------- render and cut
def render(name, body, w, h, scale, defs=''):
    import render as R
    return R.render(name, body, w, h, scale, OUT + 'big', fmt='png', defs=defs)

def cut(im, w, h, cols, alpha_cut=0.5):
    """im: w*s by h*s; returns w by h, each cell the colour most of it snaps to"""
    a = np.array(im.convert('RGBA')).astype(np.float32)
    P = np.array(cols, dtype=np.float32)
    rgb = a[..., :3].reshape(-1, 3)
    wt = np.array([0.30, 0.59, 0.11], dtype=np.float32) * 3
    best = np.zeros(len(rgb), dtype=np.int32); bestd = np.full(len(rgb), 1e12, dtype=np.float32)
    for i, c in enumerate(P):
        d = (((rgb - c) ** 2) * wt).sum(1); m = d < bestd; bestd[m] = d[m]; best[m] = i
    H_, W_ = a.shape[:2]; idx = best.reshape(H_, W_); op = a[..., 3] > 127
    xs = np.linspace(0, W_, w + 1).astype(int); ys = np.linspace(0, H_, h + 1).astype(int)
    out = np.zeros((h, w, 4), dtype=np.uint8)
    for j in range(h):
        for i in range(w):
            cell = op[ys[j]:ys[j + 1], xs[i]:xs[i + 1]]
            if cell.mean() < alpha_cut: continue
            v = np.bincount(idx[ys[j]:ys[j + 1], xs[i]:xs[i + 1]][cell], minlength=len(P))
            out[j, i, :3] = P[v.argmax()]; out[j, i, 3] = 255
    return Image.fromarray(out)

def orphans(im):
    """a lone pixel unlike all four neighbours takes the colour most of its eight have"""
    a = np.array(im); b = a.copy(); H_, W_ = a.shape[:2]
    for y in range(1, H_ - 1):
        for x in range(1, W_ - 1):
            me = a[y, x]
            if me[3] == 0: continue
            n4 = [a[y - 1, x], a[y + 1, x], a[y, x - 1], a[y, x + 1]]
            if any((n == me).all() for n in n4) or any(n[3] == 0 for n in n4): continue
            n8 = [tuple(a[yy, xx]) for yy in (y - 1, y, y + 1) for xx in (x - 1, x, x + 1) if (yy, xx) != (y, x)]
            top = max(set(n8), key=n8.count)
            if n8.count(top) >= 4: b[y, x] = top
    return Image.fromarray(b)

def px(im, x, y, c):
    im.putpixel((x, y), hexrgb(c) + (255,))

# ---------------------------------------------------------------- SVG vocabulary
def E(cx, cy, rx, ry, fill, extra=''): return '<ellipse cx="%g" cy="%g" rx="%g" ry="%g" fill="%s" %s/>' % (cx, cy, rx, ry, fill, extra)
def C_(cx, cy, r, fill, extra=''): return E(cx, cy, r, r, fill, extra)
def Rr(x, y, w, h, fill, r=0, extra=''): return '<rect x="%g" y="%g" width="%g" height="%g" rx="%g" fill="%s" %s/>' % (x, y, w, h, r, fill, extra)
def P_(d, fill, extra=''): return '<path d="%s" fill="%s" %s/>' % (d, fill, extra)
def L_(pts, stroke, w, extra=''): return '<polyline points="%s" fill="none" stroke="%s" stroke-width="%g" stroke-linecap="round" stroke-linejoin="round" %s/>' % (' '.join('%g,%g' % p for p in pts), stroke, w, extra)
def radial(id_, cx, cy, r, stops, fx=None, fy=None):
    s = ''.join('<stop offset="%g" stop-color="%s"/>' % st for st in stops)
    return '<radialGradient id="%s" gradientUnits="userSpaceOnUse" cx="%g" cy="%g" r="%g" fx="%g" fy="%g">%s</radialGradient>' % (id_, cx, cy, r, fx if fx is not None else cx, fy if fy is not None else cy, s)
def linear(id_, x1, y1, x2, y2, stops):
    s = ''.join('<stop offset="%g" stop-color="%s"/>' % st for st in stops)
    return '<linearGradient id="%s" gradientUnits="userSpaceOnUse" x1="%g" y1="%g" x2="%g" y2="%g">%s</linearGradient>' % (id_, x1, y1, x2, y2, s)

# ================================================================ the record player, in the room
# A portable player in a two-tone case on the side table: its lid up behind, lined in cream;
# the deck seen from a little above, the record nearly edge on, its label red, the tonearm
# across it from its post; the front in teal leatherette with a gold-framed grille of woven
# cloth, two cream knobs, and little feet.
PW, PH = 30, 30
REC = (12.5, 16.2, 10, 2.6)          # the record's ellipse in the sprite: cx, cy, rx, ry
def room_player():
    # drawn on the whole-pixel grid: at this size every edge must fall on a pixel's edge
    T, Cr, G, S, K = TEAL, CREAM, GOLD, STEEL, BLACK
    d = (linear('lid', 3, 2, 27, 13, [(0, Cr[5]), (0.5, Cr[4]), (1, Cr[3])]) +
         linear('front', 0, 0, 30, 0, [(0, T[4]), (0.45, T[3]), (1, T[2])]))
    b = ''
    # the lid, open behind: the case's teal round its edge, the lining inside, shadowed low
    b += Rr(1, 0, 28, 15, T[3], 1.5) + Rr(2, 0, 26, 1, T[4]) + Rr(28, 1, 1, 14, T[2])
    b += Rr(3, 2, 24, 11, 'url(#lid)') + Rr(3, 12, 24, 2, Cr[2])
    b += Rr(10, 4, 10, 1, G[3]) + Rr(10, 5, 10, 1, G[2])                 # a gold plate in the lining
    b += Rr(26, 7, 1, 7, S[3])                                            # the lid's stay
    # the deck: a cream plate from a little above, gold along its front edge
    b += Rr(0, 14, 30, 5, Cr[3]) + Rr(0, 14, 30, 1, Cr[4]) + Rr(0, 18, 30, 1, G[2])
    cx, cy, rx, ry = REC
    b += E(cx + 0.5, cy + 0.8, rx + 1, ry + 0.6, Cr[1])                   # the platter's shadow on the plate
    b += E(cx, cy, rx + 1, ry + 0.6, S[3])                                # the platter's rim
    b += E(cx, cy, rx, ry, K[1])
    b += Rr(4, 15, 4, 1, K[4]) + Rr(17, 17, 4, 1, K[3])                   # the light lying in the grooves
    b += Rr(10, 15, 5, 3, LABEL[1]) + Rr(9, 16, 7, 1, LABEL[1]) + Rr(10, 15, 3, 1, LABEL[2])
    b += Rr(12, 14, 1, 2, S[5])                                           # the spindle
    # the tonearm: its post at the back right, the arm across to the record, the head on it
    b += Rr(24, 15, 3, 2, S[1]) + Rr(24, 15, 2, 1, S[4])
    b += Rr(19, 15, 6, 1, Cr[5]) + Rr(17, 16, 2, 1, Cr[5]) + Rr(15, 16, 2, 2, K[3]) + Rr(15, 16, 2, 1, S[3])
    # the front: leatherette lit from the left, a lighter edge at the top, its foot in shade
    b += Rr(0, 19, 30, 10, 'url(#front)') + Rr(0, 19, 30, 1, T[5]) + Rr(0, 28, 30, 1, T[1]) + Rr(29, 19, 1, 10, T[1])
    b += Rr(2, 21, 16, 6, G[2]) + Rr(2, 21, 16, 1, G[3]) + Rr(3, 22, 14, 4, Cr[3])
    for y in (23, 25): b += Rr(3, y, 14, 1, Cr[2])                       # the cloth's weave
    b += Rr(8, 23, 4, 1, G[3])                                            # its badge
    for kx in (21, 25):  # two small knobs
        b += Rr(kx, 22, 2, 1, Cr[4]) + Rr(kx, 23, 2, 1, Cr[2]) + Rr(kx, 22, 1, 1, Cr[5])
    b += Rr(2, 29, 3, 1, K[2]) + Rr(25, 29, 3, 1, K[2])                   # the feet
    cols = pal(T, Cr, G, S, K, LABEL)
    im = cut(render('player-room', b, PW, PH, 24, d), PW, PH, cols)
    # the deck, set by hand: at this size the record is five rows, and every pixel tells
    key = {'a': Cr[4], 'b': Cr[3], 'd': Cr[1], 'k': K[1], 'h': K[4], 'i': K[3], 'r': LABEL[1], 'R': LABEL[2], 'q': LABEL[0],
           's': S[5], 't': S[3], 'u': S[1], 'w': Cr[5], 'g': G[2]}
    rows = {14: 'aaaaaaaaaaaasaaaaaaaaaaaaaaaaa',
            15: 'bbbkkhhhkkRRsrkkkkwwwwwwtubbbb',
            16: 'bkkkkkkkkrrrrrritwwkkkkkbbbbbb',
            17: 'ddkkkkkkkkqqqqqkkiiiikkdbbbbbb',
            18: 'ggttttttttttttttttttttttgggggg'}
    for y, row in rows.items():
        for x, ch in enumerate(row): px(im, x, y, key[ch])
    return im

def room_spin(n=6):
    """the record turning: one mark on the label going round, a frame at a time"""
    cx, cy = int(REC[0]), int(REC[1])
    ring = [(-2, 0), (-1, -1), (1, -1), (2, 0), (1, 1), (-1, 1)]
    out = []
    for k in range(n):
        im = Image.new('RGBA', (PW, PH)); dx, dy = ring[k % len(ring)]
        im.putpixel((cx + dx, cy + dy), hexrgb('#f5eedb') + (255,))
        out.append(im)
    return out

# ================================================================ the tomato timer, on the desk
TW, TH = 18, 16
def room_timer():
    # the same solid as the close-up's, small: its body and calyx painted, its band of minutes
    # laid round it at the same latitude, the stem set by hand
    Rd, Gr, Cr = RED, GREEN, CREAM
    SC, k = 16, 8.7 / TOM['rx']
    cx, cy = 8.9, 9.6
    big, (sx, sy) = tom_paint(SC, TW, TH, cx, cy, k, panes=False)
    a = np.array(big)
    BAND, BH = -0.2, 0.075
    for la in np.linspace(-np.pi, np.pi, 900):
        for ph in np.linspace(BAND - BH, BAND + BH, 24):
            X, Y, Z = tom_point(np.array([ph]), np.array([la]))
            if math.cos(la) < 0.5: continue
            x, y = int((cx + X[0] * k) * SC), int((cy + Y[0] * k) * SC)
            if 0 <= x < TW * SC and 0 <= y < TH * SC:
                a[max(0, y - 2):y + 2, max(0, x - 2):x + 2, :3] = hexrgb(Cr[4] if math.sin(la) < -0.2 else Cr[3] if math.sin(la) < 0.4 else Cr[1])
    im = cut(Image.fromarray(a), TW, TH, pal(Rd, Gr, Cr))
    im = outline(im, cx, cy, 8.7, 6.4)
    sx = int(round(sx))
    for y in range(0, 4): px(im, sx - 1, y, Gr[4]); px(im, sx, y, Gr[2])
    px(im, sx - 1, 0, Gr[5]); px(im, sx, 0, Gr[4])
    return im

# ================================================================ the record player, from above
# The station's pictures: the player seen from straight above, whole, twice: at rest, the arm
# on its post and the lever by Off; and playing, the stylus in the groove and the lever at 33.
# records.js shows the one or the other.
DW, DH = 240, 160
DECK = dict(cx=82, cy=80, rim=64, rec=60, pivot=(196, 36), rest=(196, 128))
def deck():
    T, Cr, G, S, K = TEAL, CREAM, GOLD, STEEL, BLACK
    cx, cy = DECK['cx'], DECK['cy']
    px_, py_ = DECK['pivot']
    d = (linear('plate', 0, 0, 240, 160, [(0, Cr[4]), (0.5, Cr[3]), (1, Cr[2])]) +
         radial('rim', cx - 30, cy - 30, 110, [(0, S[5]), (0.4, S[4]), (0.75, S[3]), (1, S[2])]) +
         radial('base', px_ - 6, py_ - 6, 20, [(0, S[5]), (0.35, S[4]), (0.7, S[3]), (1, S[2])]) +
         '<radialGradient id="knob" cx="0.38" cy="0.35" r="0.75"><stop offset="0" stop-color="%s"/><stop offset="0.5" stop-color="%s"/><stop offset="1" stop-color="%s"/></radialGradient>' % (Cr[5], Cr[4], Cr[3]) +
         linear('case', 0, 0, 240, 160, [(0, T[4]), (0.35, T[3]), (1, T[2])]))
    b = ''
    # the case: teal leatherette, lit at its top and left edges, shaded at its bottom and right
    b += Rr(0, 0, 240, 160, T[0], 9) + Rr(1, 1, 238, 158, T[2], 8) + Rr(1, 1, 236, 156, T[5], 8) + Rr(3, 3, 235, 155, T[1], 7)
    b += Rr(3, 3, 233, 153, 'url(#case)', 7)
    b += Rr(6.5, 6.5, 227, 147, 'none', 5, 'stroke="%s" stroke-width="1.4"' % G[2])     # the gold piping round the deck
    for hx in (56, 184): b += Rr(hx, 0, 18, 4, S[2], 1) + Rr(hx, 0, 18, 1.2, S[4]) + Rr(hx + 2, 2.6, 14, 1, S[1])   # the lid's hinges
    # the deck plate, set into the case: its top and left edges in the case's shadow
    b += Rr(10, 10, 220, 140, Cr[0], 4) + Rr(11.5, 11.8, 218.5, 138.2, 'url(#plate)', 3.5)
    b += Rr(11.5, 11.8, 218.5, 1.6, Cr[2]) + Rr(11.5, 11.8, 1.6, 138.2, Cr[2])
    for sx, sy in ((17, 16), (223, 16), (17, 144), (223, 144)):                         # the screws
        b += C_(sx, sy, 2.1, Cr[1]) + C_(sx - 0.3, sy - 0.3, 1.6, S[3]) + Rr(sx - 1.4, sy - 0.35, 2.8, 0.7, S[1])
    # the platter in its well: a shadow on the plate, the rim, the strobe ring
    b += C_(cx + 3, cy + 4, DECK['rim'] + 1.5, Cr[1])
    b += C_(cx, cy, DECK['rim'] + 1.5, S[1]) + C_(cx, cy, DECK['rim'], 'url(#rim)') + C_(cx, cy, DECK['rec'] + 1.5, S[1])
    # the tonearm's base: a turned steel boss, its shadow on the plate, a dark hub
    b += C_(px_ + 3, py_ + 4, 14, Cr[1]) + C_(px_, py_, 14, S[1]) + C_(px_, py_, 13, 'url(#base)')
    b += C_(px_, py_, 6.5, S[1]) + C_(px_, py_, 5, S[2])
    # the arm's rest: a steel post with a cream rubber cradle
    rx, ry = DECK['rest']
    b += Rr(rx - 3, ry + 9, 10, 9, Cr[1], 2) + Rr(rx - 5, ry + 6, 10, 10, S[1], 2) + Rr(rx - 4, ry + 6, 8, 8.5, S[3], 1.6) + Rr(rx - 3.2, ry + 6.6, 3, 7, S[4], 1)
    # the knobs, volume and tone, cream with a gold cap, their scales engraved round them
    for ky, ang in ((96, -40), (120, 25)):
        kx = 216
        for k in range(11):
            a = math.radians(-225 + k * 27)
            b += C_(kx + math.cos(a) * 12.5, ky + math.sin(a) * 12.5, 0.9 if k % 5 else 1.3, Cr[1])
        b += C_(kx + 2, ky + 3, 9.5, Cr[1]) + C_(kx, ky, 9.5, Cr[1]) + C_(kx, ky, 8.6, 'url(#knob)')
        b += C_(kx, ky, 4.4, G[1]) + C_(kx, ky, 3.8, G[2]) + C_(kx - 1.2, ky - 1.2, 1.6, G[4])
        a = math.radians(ang - 90)
        b += L_([(kx + math.cos(a) * 5, ky + math.sin(a) * 5), (kx + math.cos(a) * 8, ky + math.sin(a) * 8)], K[2], 1.4)
    # the speed lever's slot, with its four speeds marked (the lever is drawn live)
    b += Rr(152, 136, 34, 7, Cr[1], 3.5) + Rr(153, 137, 32, 5, K[2], 2.5) + Rr(153, 140.5, 32, 1.5, K[3], 0.75)
    for k in range(5): b += Rr(155.5 + k * 6.5, 145.5, 1.2, 2.4, Cr[0])
    # a gold badge, its name worn off
    b += Rr(206, 66.5, 22, 5, G[0], 1.4) + Rr(206, 66, 22, 4.4, G[2], 1.4) + Rr(207, 66.4, 20, 1.1, G[4], 0.5)
    cols = pal(T, Cr, G, S, K)
    im = cut(render('deck', b, DW, DH, 6, d), DW, DH, cols)
    im = orphans(im)
    # the leatherette's grain, a scatter fixed to the grid on the case's broad teal
    a = np.array(im)
    t3, t2, t4 = hexrgb(T[3]), hexrgb(T[2]), hexrgb(T[4])
    for y in range(DH):
        for x in range(DW):
            h = (x * 73856093 ^ y * 19349663) & 1023
            c = tuple(a[y, x, :3])
            if c == t3 and h < 90: a[y, x, :3] = t2
            elif c == t3 and h > 990: a[y, x, :3] = t4
    return Image.fromarray(a)

# ================================================================ the tomato, close up
# The station's picture of the body, calyx and stem; timer.js draws the turning band over it,
# its geometry the same ellipsoid (centre 80, 78; radii 66, 46) and the band at row 58.
BW, BH = 160, 128
def deck_whole(playing):
    """the deck with its record, strobe ring, tonearm and lever laid over it, pixel by pixel"""
    im = deck(); a = np.array(im).astype(np.float32)
    H_, W_ = a.shape[:2]
    S = [np.array(hexrgb(c), dtype=np.float32) for c in STEEL]; K = [np.array(hexrgb(c), dtype=np.float32) for c in BLACK]
    Cr = [np.array(hexrgb(c), dtype=np.float32) for c in CREAM]
    lab = np.array(hexrgb(LABEL[1]), dtype=np.float32); labD = np.array(hexrgb(LABEL[0]), dtype=np.float32); labL = np.array(hexrgb(LABEL[2]), dtype=np.float32)
    CX, CY, R, RIM = DECK['cx'], DECK['cy'], DECK['rec'], DECK['rim']
    PX, PY = DECK['pivot']; L = 92; LIGHT = -2.3; turn = 0.6
    def put(x, y, c):
        if 0 <= x < W_ and 0 <= y < H_: a[y, x, :3] = c; a[y, x, 3] = 255
    def groove(d):
        if d > R - 1: return 2
        if d > R - 4 or d < 25: return 1
        if abs(d - 47) < 0.8 or abs(d - 37) < 0.8: return 0
        return 1 if int(d * 1.5) % 2 else 2
    for y in range(-RIM, RIM + 1):
        for x in range(-RIM, RIM + 1):
            d = math.hypot(x + 0.5, y + 0.5)
            if d > RIM: continue
            th = math.atan2(y + 0.5, x + 0.5)
            if d > R + 1.5:
                # the rim's strobe: a ring of dots
                if RIM - 2.6 < d < RIM - 0.6 and int(((th - turn) / (2 * math.pi) + 2) * 90) % 2 == 0: put(CX + x, CY + y, S[1] if d > RIM - 1.6 else S[2])
                continue
            if d > R + 0.5: put(CX + x, CY + y, K[0]); continue
            if d > 21:
                # the vinyl: its rings, and the light in two wedges across them
                ring = groove(d); f = abs(math.cos(th - LIGHT)); w = 0.9 + 0.08 * d / R
                c = K[ring]
                if ring and f > w: c = K[5 if f > w + 0.06 else 4 if f > w + 0.025 else 3]
                if d < 23.5: c = K[2]
            else:
                # the label: a darker edge, its lettering
                la = th - turn; co = math.cos(la)
                c = labD if d > 19.6 else lab
                if 11 < d < 14 and co > 0.3 and (int(la * 12 + 100) % 2 or d > 12.5): c = labL
                if 15 < d < 16.2 and co > 0: c = Cr[4]
                if 6 < d < 8 and co < -0.5: c = Cr[4]
                if d < 2.6: c = S[5] if d < 1.6 else S[2]
            put(CX + x, CY + y, c)
    # the tonearm: at rest on its post, or with its stylus a third of the way into the side
    ang = math.pi / 2
    if playing:
        gr = R - 3 - 0.33 * (R - 27)
        while ang < 3 and math.hypot(PX + math.cos(ang + 0.12) * (L + 8) - CX, PY + math.sin(ang + 0.12) * (L + 8) - CY) > gr: ang += 0.003
    def bar(ox, oy, ca, sa, s0, s1, hw, colour, shadow):
        xs = [ox + ca * u - sa * v for u in (s0, s1) for v in (-hw, hw)]; ys = [oy + sa * u + ca * v for u in (s0, s1) for v in (-hw, hw)]
        for y in range(int(min(ys)) - 1, int(max(ys)) + 2):
            for x in range(int(min(xs)) - 1, int(max(xs)) + 2):
                dx, dy = x + 0.5 - ox, y + 0.5 - oy; u = dx * ca + dy * sa; v = -dx * sa + dy * ca
                if u < s0 or u > s1 or abs(v) > hw: continue
                if shadow:
                    if 0 <= x + 4 < W_ and 0 <= y + 5 < H_: a[y + 5, x + 4, :3] *= 0.66
                else: put(x, y, colour(u, v))
    def tube(hw):
        def f(u, v):
            t = v / hw; return S[5 if t < -0.6 else 4 if t < -0.1 else 3 if t < 0.5 else 2 if t < 0.85 else 1]
        return f
    def arm(shadow):
        ca, sa = math.cos(ang), math.sin(ang)
        bar(PX, PY, ca, sa, -26, -11, 6.5, lambda u, v: S[1] if round(-u) % 4 == 0 else S[4 if v / 6.5 < -0.5 else 3 if v / 6.5 < 0.4 else 2], shadow)
        bar(PX, PY, ca, sa, -11, L - 6, 2.2, tube(2.2), shadow)
        hx, hy = PX + ca * (L - 6), PY + sa * (L - 6); ha = ang + 0.38; hc, hs = math.cos(ha), math.sin(ha)
        bar(hx, hy, hc, hs, -1, 15, 4.5, lambda u, v: S[2] if abs(v) > 3.6 or u > 14 else S[3] if u < 3 else K[3], shadow)
        bar(hx, hy, hc, hs, 9, 12, 8.5, lambda u, v: K[3] if v < 4.5 else S[4], shadow)
    arm(True); arm(False)
    for j in range(-5, 6):
        for i in range(-5, 6):
            q = math.hypot(i + 0.5, j + 0.5)
            if q < 5: put(PX + i, PY + j, S[5] if q < 2 else S[3] if q < 3.6 else S[1])
    # the speed lever: by Off at rest, at 33 playing
    lx = 163 if playing else 154
    for ly in range(134, 145):
        for k in range(7): put(lx + k, ly, S[5] if ly == 134 or k == 0 else S[1] if ly > 142 or k == 6 else S[3])
    return Image.fromarray(a.astype(np.uint8))

# ---------------------------------------------------------------- the tomato as a solid
# Not an ellipse: a squat sphere whose radius swells in five lobes round its shoulders, dips
# into a well at the top where the calyx sits, and flattens where it stands; seen from a little
# above (TILT), so the well and the top show and a ring round it sags at the front. timer.js
# draws the band of minutes round the same solid (its TOMATO constants must match these).
TOM = dict(cx=80, cy=76, rx=66, ry=46, tilt=0.36, lobes=0.055, well=0.2)
def tom_radius(ph, la):
    """the solid's radius at latitude ph (-pi/2 the top) and longitude la (0 toward the viewer)"""
    up = np.clip((0.75 - np.sin(ph)) / 1.5, 0, 1)                      # the lobes, strongest on the shoulders
    r = 1 + TOM['lobes'] * np.cos(5 * la + 0.4) * up
    r -= TOM['well'] * np.exp(-((ph + np.pi / 2) / 0.42) ** 2)           # the well at the top
    return r

def tom_point(ph, la):
    r = tom_radius(ph, la)
    X = r * np.cos(ph) * np.sin(la) * TOM['rx']; Y = r * np.sin(ph) * TOM['ry']; Z = r * np.cos(ph) * np.cos(la) * TOM['rx']
    Y = np.where(Y > 0.8 * TOM['ry'], 0.8 * TOM['ry'] + (Y - 0.8 * TOM['ry']) * 0.35, Y)   # flattened where it stands
    t = TOM['tilt']; c, s_ = math.cos(t), math.sin(t)
    return X, Y * c + Z * s_, Z * c - Y * s_                              # screen x, screen y (down), depth (toward the viewer)

SEPALS = [(k * 2 * math.pi / 5 + 0.3, 0.86 + 0.14 * math.sin(k * 2.1)) for k in range(5)]
def sepal_at(ph, la):
    """how far into a sepal a point is (0 outside, else 0..1 across from its edge to its rib),
    whether it is on the rib's lit side, and how far along it lies"""
    t = (ph + np.pi / 2) / 1.12
    best = np.zeros_like(ph); side = np.zeros_like(ph); along = np.zeros_like(ph)
    for lk, ln in SEPALS:
        tt = t / ln
        w = 0.2 * np.sin(np.pi * np.clip(tt * 1.6, 0, 1) ** 0.8) * (1 - 0.8 * np.clip(tt, 0, 1)) + 0.04 * (1 - np.clip(tt * 3, 0, 1)) + 0.002
        d = np.angle(np.exp(1j * (la - lk))) * np.maximum(np.cos(ph), 0.08)
        inn = (tt >= 0) & (tt <= 1) & (np.abs(d) < w)
        f = np.where(inn, 1 - np.abs(d) / w, 0)
        m = f > best
        best = np.where(m, f, best); side = np.where(m, np.sign(d), side); along = np.where(m, tt, along)
    return best, side, along

def tom_solid(sc, W_, H_, cx, cy, scale=1.0, nph=1100, nla=2200):
    """splat the solid into an sc-times picture: for each covered pixel its normal, its
    latitude and longitude, frontmost first"""
    ph, la = np.meshgrid(np.linspace(-np.pi / 2, np.pi / 2, nph), np.linspace(-np.pi, np.pi, nla), indexing='ij')
    ph = ph.ravel(); la = la.ravel()
    e = 1e-3
    X, Y, Z = tom_point(ph, la)
    Xa, Ya, Za = tom_point(ph + e, la); Xb, Yb, Zb = tom_point(ph, la + e)
    tu = np.stack([Xa - X, Ya - Y, Za - Z], -1); tv = np.stack([Xb - X, Yb - Y, Zb - Z], -1)
    n = np.cross(tv, tu); n /= np.linalg.norm(n, axis=-1, keepdims=True) + 1e-9
    n = np.where(n[:, 2:3] < 0, -n, n)
    keep = n[:, 2] > -0.05
    px_ = ((cx + X * scale) * sc).astype(int); py_ = ((cy + Y * scale) * sc).astype(int)
    ok = keep & (px_ >= 0) & (px_ < W_ * sc) & (py_ >= 0) & (py_ < H_ * sc)
    idx = py_[ok] * (W_ * sc) + px_[ok]
    order = np.argsort(Z[ok])
    N = np.zeros((H_ * sc * W_ * sc, 3), dtype=np.float32); PH = np.full(H_ * sc * W_ * sc, np.nan, dtype=np.float32); LA = np.zeros_like(PH)
    N[idx[order]] = n[ok][order]; PH[idx[order]] = ph[ok][order]; LA[idx[order]] = la[ok][order]
    N = N.reshape(H_ * sc, W_ * sc, 3); PH = PH.reshape(H_ * sc, W_ * sc); LA = LA.reshape(H_ * sc, W_ * sc)
    # fill the odd pinhole the splat leaves, from the pixel to the left
    for _ in range(2):
        hole = np.isnan(PH); hole[:, 0] = False
        left = np.roll(PH, 1, 1); fill = hole & ~np.isnan(left)
        PH[fill] = left[fill]; LA[fill] = np.roll(LA, 1, 1)[fill]; N[fill] = np.roll(N, 1, 1)[fill]
    return N, PH, LA

def tom_paint(sc, W_, H_, cx, cy, scale=1.0, panes=True):
    """the solid lit from the upper left and painted: skin in the red ramp, the calyx in green,
    each sepal's shadow on the skin; every pixel a step of its ramp"""
    N, PH, LA = tom_solid(sc, W_, H_, cx, cy, scale)
    inside = ~np.isnan(PH); ph = np.nan_to_num(PH); la = LA
    L = np.array([-0.55, -0.68, 0.48]); L /= np.linalg.norm(L)
    dif = N[..., 0] * L[0] + N[..., 1] * L[1] + N[..., 2] * L[2]
    v = 0.06 + 0.9 * np.clip((dif + 0.3) / 1.3, 0, 1) ** 1.25
    v += 0.16 * np.clip(N[..., 1] - 0.35, 0, 1) * N[..., 2]                # the desk's light thrown back up
    v *= 0.72 + 0.28 * np.clip((ph + np.pi / 2) / 0.55, 0, 1)            # the well's own shade
    h = L + np.array([0, 0, 1.0]); h /= np.linalg.norm(h)
    spec = np.clip(N[..., 0] * h[0] + N[..., 1] * h[1] + N[..., 2] * h[2], 0, 1) ** 70
    sep, side, along = sepal_at(ph, la)
    shadow, _, _ = sepal_at(ph - 0.07, la + 0.06)                        # the sepals' shadow, cast down and right
    idx = 1 + sum((v > t).astype(int) for t in [0.2, 0.34, 0.5, 0.66, 0.82])
    idx = np.where((shadow > 0) & (sep == 0), np.maximum(idx - 2, 1), idx)
    idx = np.where((spec > 0.25) & (sep == 0), 6, idx); idx = np.where((spec > 0.6) & (sep == 0), 7, idx)
    if panes:
        j, i = np.unravel_index(np.argmax(np.where(inside & (sep == 0), spec, 0)), spec.shape)
        yy, xx = np.mgrid[0:H_ * sc, 0:W_ * sc]
        bars = ((np.abs(xx - i) < 0.55 * sc) | (np.abs(yy - j) < 0.5 * sc)) & (np.hypot(xx - i, yy - j) < 4 * sc)
        idx = np.where((spec > 0.25) & bars & (sep == 0), 5, idx)
    Rd = [np.array(hexrgb(c)) for c in RED]; Gn = [np.array(hexrgb(c)) for c in GREEN]
    out = np.zeros((H_ * sc, W_ * sc, 4), dtype=np.uint8)
    for i in range(8):
        m = inside & (sep == 0) & (idx == i); out[m, :3] = Rd[i]; out[m, 3] = 255
    # a sepal: green by the light on it, lighter on its lit half and along its rib, dark at its edge
    gv = 0.25 + 0.75 * np.clip((dif + 0.2) / 1.2, 0, 1) + np.where(side < 0, 0.12, -0.12) + np.where(sep > 0.86, 0.18, 0)
    gi = np.clip((gv * 4.2).astype(int), 1, 5)
    gi = np.where(sep < 0.16, 0, gi)
    for i in range(6):
        m = inside & (sep > 0) & (gi == i); out[m, :3] = Gn[i]; out[m, 3] = 255
    pole = tom_point(np.array([-np.pi / 2]), np.array([0.0]))
    return Image.fromarray(out), (cx + pole[0][0] * scale, cy + pole[1][0] * scale)

def stem_svg(x, y, h, w):
    """the stem rising from the well, a little bent, cut square, its cut face pale"""
    Gr = GREEN
    d = linear('stem', x - w, 0, x + w, 0, [(0, Gr[4]), (0.45, Gr[3]), (1, Gr[1])])
    b = P_('M%g %g L%g %g Q%g %g %g %g Q%g %g %g %g L%g %g Q%g %g %g %g Z' % (
        x - w, y, x - w + 0.4, y - h + 3, x - w + 0.8, y - h, x + 0.3, y - h - 0.6, x + w + 0.6, y - h - 0.8, x + w + 0.4, y - h + 3,
        x + w, y, x, y + 1.6, x - w, y), 'url(#stem)', 'stroke="%s" stroke-width="%g"' % (Gr[0], max(0.6, w / 3)))
    b += E(x + 0.3, y - h + 0.6, w * 0.95, w * 0.45, Gr[5], 'stroke="%s" stroke-width="%g"' % (Gr[1], max(0.5, w / 4)))
    return d, b

def outline(im, cx, cy, rx, ry):
    """the silhouette closed in the body's own darkest red, a step lighter where the light falls"""
    a = np.array(im); op = a[..., 3] > 0
    inner = op.copy(); inner[1:] &= op[:-1]; inner[:-1] &= op[1:]; inner[:, 1:] &= op[:, :-1]; inner[:, :-1] &= op[:, 1:]
    reds = {hexrgb(c) for c in RED}
    for y, x in zip(*np.where(op & ~inner)):
        if tuple(a[y, x, :3]) not in reds: continue
        a[y, x, :3] = hexrgb(RED[1] if (x - cx) / rx + (y - cy) / ry < -0.55 else RED[0])
    return Image.fromarray(a)

def tomato():
    SC = 6
    big, (sx, sy) = tom_paint(SC, BW, BH, TOM['cx'], TOM['cy'])
    d, b = stem_svg(sx, sy + 1, 21, 3.8)
    big.alpha_composite(render('tomato', b, BW, BH, SC, d).convert('RGBA'))
    im = orphans(cut(big, BW, BH, pal(RED, GREEN)))
    return outline(im, TOM['cx'], TOM['cy'], TOM['rx'], TOM['ry'])

# ---------------------------------------------------------------- write everything, and a proof
if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    pics = {'px-record-player.png': room_player(), 'px-timer.png': room_timer()}
    for n, im in pics.items(): im.save(OUT + n)
    sp = room_spin(); sheet = Image.new('RGBA', (PW * len(sp), PH))
    for k, f in enumerate(sp): sheet.paste(f, (k * PW, 0))
    sheet.save(OUT + 'spin.png')
    dk = deck_whole(False); dk.save(ST + 'rec-deck.png', optimize=True)
    deck_whole(True).save(ST + 'rec-deck-playing.png', optimize=True)
    tm = tomato(); tm.save(ST + 'pomo-body.png', optimize=True)
    pr = Image.new('RGBA', (DW * 2 + BW * 2 + PW * 8 + TW * 8 + 40, DH * 2), (90, 80, 72, 255))
    pr.alpha_composite(dk.resize((DW * 2, DH * 2), Image.NEAREST), (0, 0))
    pr.alpha_composite(tm.resize((BW * 2, BH * 2), Image.NEAREST), (DW * 2 + 10, 0))
    pr.alpha_composite(pics['px-record-player.png'].resize((PW * 8, PH * 8), Image.NEAREST), (DW * 2 + BW * 2 + 20, 0))
    pr.alpha_composite(pics['px-timer.png'].resize((TW * 8, TH * 8), Image.NEAREST), (DW * 2 + BW * 2 + PW * 8 + 30, 0))
    pr.save(HERE + 'seeds25-proof.png')
    print('ok')
