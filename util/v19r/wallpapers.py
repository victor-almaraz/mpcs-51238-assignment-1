# v22's other wallpapers, to hang in place of v21's blue ogee (decor.js): each a seamless
# tile, in tenths of an em (a 60 x 90 tile hangs at 6em x 9em).
#   atomic     deep sage, cream starbursts and ochre boomerangs, half-dropped
#   trellis    burnt umber, a diamond trellis in a pale hairline, a cream bud in each diamond
#   grass      an ivory grasscloth: fine vertical stripes in sand, slate and ochre
#   sieve      charcoal, rows of points with the members of a sieve picked out in ochre
import os as _os; UTIL = _os.path.normpath(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..')); REPO = _os.path.dirname(UTIL)
import math, random
from mcm import f
OUT = REPO + '/v22/assets/'

def save(name, W, H, body):
    s = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">%s</svg>' % (W, H, W * 4, H * 4, ''.join(body))
    open(OUT + 'wall-%s.svg' % name, 'w').write(s)
    print(name, len(s))

def atomic():
    W, H = 60, 60
    G, CREAM, OCHRE, PALE = '#4b5b49', '#e6dcc4', '#c9a45a', '#7f8f7a'
    b = ['<rect width="%d" height="%d" fill="%s"/>' % (W, H, G)]
    def star(x, y, r):
        o = []
        for k in range(8):
            a = k * math.pi / 4 + math.pi / 8
            rr = r if k % 2 else r * 0.62
            o.append('M%s,%sL%s,%s' % (f(x + math.cos(a) * 1.4), f(y + math.sin(a) * 1.4), f(x + math.cos(a) * rr), f(y + math.sin(a) * rr)))
        s = '<path d="%s" stroke="%s" stroke-width="0.55" stroke-linecap="round"/>' % (''.join(o), CREAM)
        s += ''.join('<circle cx="%s" cy="%s" r="0.9" fill="%s"/>' % (f(x + math.cos(k * math.pi / 4 + math.pi / 8) * r), f(y + math.sin(k * math.pi / 4 + math.pi / 8) * r), CREAM) for k in range(1, 8, 2))
        return s + '<circle cx="%s" cy="%s" r="1.3" fill="%s"/>' % (f(x), f(y), OCHRE)
    def boomerang(x, y, a):
        return ('<path d="M-5,2 Q0,-5 5,2 Q0,-1.6 -5,2 Z" fill="%s" transform="translate(%s %s) rotate(%s)"/>' % (OCHRE, f(x), f(y), f(a)))
    for x, y in ((15, 15), (45, 45), (15 + 60, 15), (45 - 60, 45), (15, 15 + 60), (45, 45 - 60)):
        b.append(star(x, y, 7.5))
    for x, y, a in ((45, 14, 20), (15, 44, -25), (45 - 60, 14, 20), (15 + 60, 44, -25)):
        b.append(boomerang(x, y, a))
    def sparkle(x, y, r):
        return ('<path d="M%s,%s Q%s,%s %s,%s Q%s,%s %s,%s Q%s,%s %s,%s Q%s,%s %s,%s Z" fill="%s" opacity="0.85"/>' % (
            f(x), f(y - r), f(x + r * 0.15), f(y - r * 0.15), f(x + r), f(y), f(x + r * 0.15), f(y + r * 0.15), f(x), f(y + r),
            f(x - r * 0.15), f(y + r * 0.15), f(x - r), f(y), f(x - r * 0.15), f(y - r * 0.15), f(x), f(y - r), CREAM))
    for x, y in ((30, 30), (0, 0), (60, 0), (0, 60), (60, 60)):
        b.append(sparkle(x, y, 3.2))
    for x, y in ((30, 0), (30, 60), (0, 30), (60, 30)):
        b.append(''.join('<circle cx="%s" cy="%s" r="0.7" fill="%s"/>' % (f(x + dx), f(y + dy), PALE) for dx, dy in ((0, -1.6), (1.4, 0.9), (-1.4, 0.9))))
    # fine orbits through each star, the period's atom
    for x, y in ((15, 15), (45, 45)):
        b.append('<ellipse cx="%s" cy="%s" rx="11" ry="3.2" fill="none" stroke="%s" stroke-width="0.35" opacity="0.6" transform="rotate(30 %s %s)"/>' % (x, y, PALE, x, y))
    save('atomic', W, H, b)

def trellis():
    W, H = 40, 60
    G, LINE, CREAM, OCHRE = '#5a3627', '#8a6150', '#e9dcc1', '#c99a2e'
    b = ['<rect width="%d" height="%d" fill="%s"/>' % (W, H, G)]
    d = 'M0,0L40,60M40,0L0,60M-20,30L20,-30M20,90L60,30M-20,30L20,90M20,-30L60,30'
    b.append('<path d="%s" stroke="%s" stroke-width="0.6"/>' % (d, LINE))
    for x, y in ((0, 0), (40, 0), (0, 60), (40, 60), (20, 30)):
        b.append('<circle cx="%s" cy="%s" r="1.6" fill="none" stroke="%s" stroke-width="0.5"/><circle cx="%s" cy="%s" r="0.6" fill="%s"/>' % (x, y, CREAM, x, y, OCHRE))
    def bud(x, y):
        return ('<path d="M%s,%s Q%s,%s %s,%s Q%s,%s %s,%s Z" fill="%s"/>' % (f(x), f(y - 6), f(x + 3.4), f(y), f(x), f(y + 4), f(x - 3.4), f(y), f(x), f(y - 6), CREAM) +
                '<path d="M%s,%sv4" stroke="%s" stroke-width="0.5"/>' % (f(x), f(y + 4), CREAM) +
                '<path d="M%s,%sq-3,-1 -4,-3M%s,%sq3,-1 4,-3" fill="none" stroke="%s" stroke-width="0.5"/>' % (f(x), f(y + 7), f(x), f(y + 7), OCHRE))
    for x, y in ((20, 4), (0, 34), (40, 34), (20, 64)):
        b.append(bud(x, y))
    leaf = lambda x, y, a: '<path d="M0,0 Q2.2,-1.4 4.4,0 Q2.2,1.4 0,0 Z" fill="%s" opacity="0.7" transform="translate(%s %s) rotate(%s)"/>' % (LINE, f(x), f(y), f(a))
    for (x, y, a) in ((10, 15, 236), (30, 15, -56), (10, 45, 124), (30, 45, 56), (10, 15, 56), (30, 45, 236)):
        b.append(leaf(x, y, a))
    for x, y in ((10, 15), (30, 15), (10, 45), (30, 45)):
        b.append('<circle cx="%s" cy="%s" r="0.55" fill="%s"/>' % (x, y, OCHRE))
    save('trellis', W, H, b)

def grass():
    W, H = 48, 12
    rnd = random.Random(4)
    b = ['<rect width="%d" height="%d" fill="#e6dccb"/>' % (W, H)]
    x = 0
    while x < W:
        w = rnd.choice((0.3, 0.3, 0.5, 0.8, 1.4))
        c = rnd.choice(('#d3c6ae', '#d3c6ae', '#cbbd9f', '#b9ab90', '#9aa2a2', '#d9c08a'))
        b.append('<rect x="%s" y="0" width="%s" height="%d" fill="%s" opacity="%s"/>' % (f(x), f(w), H, c, f(rnd.uniform(0.5, 0.9))))
        x += w + rnd.uniform(0.4, 2.2)
    # the weft: faint horizontal threads
    for y in range(0, H, 2):
        b.append('<rect x="0" y="%d" width="%d" height="0.25" fill="#ffffff" opacity="0.25"/>' % (y, W))
    b.append('<rect x="31" y="0" width="0.6" height="%d" fill="#49555a" opacity="0.35"/>' % H)
    save('grass', W, H, b)

def sieve():
    W, H = 72, 24
    G, DOT, OCHRE, CREAM = '#2c2b29', '#6f6a62', '#c99a2e', '#e6dcc4'
    b = ['<rect width="%d" height="%d" fill="%s"/>' % (W, H, G)]
    # two rows of twelve points, the first the sieve 3@0 | 4@1, the second 4@2 | 6@5, set off by half
    for row, (y, test) in enumerate(((6, lambda n: n % 3 == 0 or n % 4 == 1), (18, lambda n: n % 4 == 2 or n % 6 == 5))):
        for n in range(12):
            x = 3 + n * 6
            if test(n): b.append('<circle cx="%s" cy="%s" r="1.7" fill="%s"/>' % (f(x), y, OCHRE if row == 0 else CREAM))
            else: b.append('<circle cx="%s" cy="%s" r="0.5" fill="%s"/>' % (f(x % W), y, DOT))
    save('sieve', W, H, b)

if __name__ == '__main__':
    atomic(); trellis(); grass()
