# The plates of Cons (Lisp: a listing's paper, the printer's ink and a terminal's green) and
# Silver (black-and-white photography: greys only), drawn in pixels, 264 x 96 each, the covers'
# fields 300 x 225. Each plate is its article's subject made a picture by its own rule.
import os as _os; UTIL = _os.path.normpath(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..')); REPO = _os.path.dirname(UTIL)
import math, random
from PIL import Image
from mag_plates2 import canvas, save, F, FM

PAPER, INK, GRN, PHOS, PHOS_D, DARK = (244, 241, 228), (22, 32, 26), (31, 122, 70), (120, 220, 140), (40, 110, 70), (16, 22, 18)

# ---------------------------------------------------------------- Cons
def cn_listing():
    # a pretty-printed function, its parentheses in green: the evaluator's own definition of append
    im, d = canvas(264, 96, PAPER)
    lines = ['(DEFINE (APPEND X Y)', '  (COND ((NULL X) Y)', '        (T (CONS (CAR X)', '                 (APPEND (CDR X) Y)))))',
             '', '(APPEND (QUOTE (A B)) (QUOTE (C D)))', '  => (A B C D)']
    for i, ln in enumerate(lines):
        x = 8
        for ch in ln:
            d.text((x, 4 + i * 13), ch, font=FM, fill=GRN if ch in '()' else INK)
            x += 6
    return im

def cons_cell(d, x, y, car=None, cdr_nil=False):
    d.rectangle([x, y, x + 33, y + 15], outline=INK); d.line([x + 17, y, x + 17, y + 15], fill=INK)
    if car: d.text((x + 5, y + 2), car, font=FM, fill=INK)
    else: d.rectangle([x + 7, y + 6, x + 10, y + 9], fill=GRN)
    if cdr_nil: d.line([x + 17, y + 15, x + 33, y], fill=INK)
    else: d.rectangle([x + 24, y + 6, x + 27, y + 9], fill=GRN)

def cn_boxes():
    # box-and-pointer: (A B C) as three cells, and ((A) B) beside it, the pointers in green
    im, d = canvas(264, 96, PAPER)
    for k, s in enumerate('ABC'):
        x = 10 + k * 50; cons_cell(d, x, 20, s, k == 2)
        if k < 2: d.line([x + 26, 28, x + 50, 28], fill=GRN); d.polygon([(x + 50, 28), (x + 46, 25), (x + 46, 31)], fill=GRN)
    d.text((10, 50), '(A B C)', font=FM, fill=INK)
    cons_cell(d, 170, 20, None, False); cons_cell(d, 220, 20, 'B', True); cons_cell(d, 170, 58, 'A', True)
    d.line([196, 28, 220, 28], fill=GRN); d.polygon([(220, 28), (216, 25), (216, 31)], fill=GRN)
    d.line([178, 36, 178, 58], fill=GRN); d.polygon([(178, 58), (175, 54), (181, 54)], fill=GRN)
    d.text((206, 64), '((A) B)', font=FM, fill=INK)
    return im

def cn_heap():
    # a heap of cells at a collection: those reached from the roots marked green, the rest swept
    rnd = random.Random(1960)
    im, d = canvas(264, 96, PAPER)
    for j in range(5):
        for i in range(16):
            x, y = 6 + i * 16, 6 + j * 17
            live = rnd.random() < 0.45
            d.rectangle([x, y, x + 12, y + 12], outline=INK, fill=GRN if live else PAPER)
            if not live and rnd.random() < 0.5: d.line([x + 2, y + 10, x + 10, y + 2], fill=(150, 146, 130))
    return im

def cn_machine():
    # a Lisp machine's console: a tall screen of text in a dark case, a keyboard under it
    im, d = canvas(264, 96, PAPER)
    d.rectangle([90, 4, 174, 78], fill=DARK); d.rectangle([96, 9, 168, 72], fill=(30, 44, 34))
    rnd = random.Random(1974)
    for k in range(15):
        y = 12 + k * 4; L = rnd.choice([20, 34, 48, 60, 26, 40])
        d.line([100, y, 100 + L, y], fill=PHOS if k % 4 else PHOS_D)
    d.rectangle([60, 82, 204, 92], fill=(70, 74, 70))
    for k in range(22): d.rectangle([63 + k * 6, 84, 67 + k * 6, 87], fill=(200, 200, 190))
    d.rectangle([63, 89, 200, 90], fill=(170, 170, 160))
    return im

def cn_cards():
    # the catalogue: a deck of cards, each a line of a program, parentheses punched in green
    im, d = canvas(264, 96, PAPER)
    for k in range(5):
        x, y = 20 + k * 44, 10 + (k % 2) * 8
        d.rectangle([x, y, x + 64, y + 72], fill=(236, 222, 188), outline=(170, 150, 110))
        d.polygon([(x, y), (x + 8, y), (x, y + 8)], fill=PAPER)
        for r in range(9):
            for c in range(12):
                if (r * 7 + c * 5 + k) % 9 == 0: d.rectangle([x + 5 + c * 5, y + 8 + r * 7, x + 6 + c * 5, y + 10 + r * 7], fill=GRN if c % 4 == 0 else INK)
    return im

def cn_cover():
    # a terminal's screen: a lambda drawn in phosphor, a listing scrolling under it
    im, d = canvas(300, 225, DARK)
    rnd = random.Random(1958)
    for k in range(40):
        y = 6 + k * 5; L = rnd.choice([30, 60, 90, 120, 150, 70])
        x = 10 + rnd.choice([0, 12, 24])
        d.line([x, y, x + L, y], fill=(28, 52, 36))
    # the lambda, two strokes four pixels wide, its shadow a step down
    for off, col in ((4, PHOS_D), (0, PHOS)):
        for t in range(120):
            x = 110 + t * 0.6 + off; y = 40 + t * 1.2 + off
            d.rectangle([x, y, x + 5, y + 5], fill=col)
        for t in range(70):
            x = 146 - t * 0.6 + off; y = 112 + t * 1.2 + off
            d.rectangle([x, y, x + 5, y + 5], fill=col)
    return im

# ---------------------------------------------------------------- Silver
GREYS = [(int(255 * (1 - k / 10) ** 1.1) if k < 10 else 6,) * 3 for k in range(11)]
SP, SK = (251, 251, 249), (20, 20, 20)

def sv_contact():
    # a contact sheet: three strips of six frames, sprocket holes along them, the frames in greys
    rnd = random.Random(1952)
    im, d = canvas(264, 96, SP)
    for s in range(3):
        y = 4 + s * 31
        d.rectangle([4, y, 259, y + 28], fill=(26, 26, 26))
        for k in range(32): d.rectangle([8 + k * 8, y + 2, 11 + k * 8, y + 4], fill=SP); d.rectangle([8 + k * 8, y + 24, 11 + k * 8, y + 26], fill=SP)
        for f in range(6):
            x = 8 + f * 42
            sky, ground = rnd.choice(GREYS[1:4]), rnd.choice(GREYS[5:9])
            d.rectangle([x, y + 7, x + 37, y + 21], fill=sky)
            h = rnd.randint(4, 10)
            d.rectangle([x, y + 21 - h, x + 37, y + 21], fill=ground)
            px = x + rnd.randint(6, 30); d.rectangle([px, y + 21 - h - rnd.randint(3, 7), px + 2, y + 21 - h], fill=GREYS[9])
    return im

def sv_zones():
    # the Zone System's scale: eleven zones from black to white, each a stop from the next
    im, d = canvas(264, 96, SP)
    for k in range(11):
        x = 6 + k * 23
        d.rectangle([x, 10, x + 21, 66], fill=GREYS[10 - k])
        num = ['0', 'I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X'][k]
        d.text((x + 11 - 3 * len(num), 72), num, font=FM, fill=SK)
    d.rectangle([6, 9, 258, 9], fill=SK); d.rectangle([6, 67, 258, 67], fill=SK)
    return im

def sv_curve():
    # a film's characteristic curve: density against the log of exposure, toe, straight line
    # and shoulder, drawn for two developments, the longer one steeper
    im, d = canvas(264, 96, SP)
    for x in range(20, 252, 20): d.line([x, 8, x, 86], fill=(222, 222, 220))
    for y in range(8, 88, 13): d.line([20, y, 250, y], fill=(222, 222, 220))
    d.line([20, 8, 20, 86], fill=SK); d.line([20, 86, 250, 86], fill=SK)
    for gamma, col in ((0.7, (130, 130, 128)), (1.0, SK)):
        pts = []
        for i in range(231):
            le = i / 230 * 3.4
            dens = 0.15 + 2.2 * gamma / (1 + math.exp(-2.6 * (le - 1.7))) - 0.04 * gamma
            pts.append((20 + i, 86 - dens * 32))
        d.line(pts, fill=col, width=2)
    d.text((24, 4), 'D', font=FM, fill=SK); d.text((214, 76), 'LOG E', font=FM, fill=SK)
    return im

def sv_photogram():
    # a photogram: things laid on the paper and the light let in; their shadows stay white
    im, d = canvas(264, 96, (18, 18, 18))
    d.ellipse([20, 18, 60, 58], fill=(236, 236, 232)); d.ellipse([30, 28, 50, 48], fill=(18, 18, 18))     # a ring
    d.line([84, 70, 128, 20], fill=(236, 236, 232), width=4); d.ellipse([122, 10, 138, 26], fill=(236, 236, 232)); d.ellipse([127, 15, 133, 21], fill=(18, 18, 18))   # a key
    for k in range(9): d.ellipse([150 + k * 6, 40 + int(8 * math.sin(k)), 156 + k * 6, 46 + int(8 * math.sin(k))], fill=(200, 200, 196))   # a string of beads
    d.polygon([(214, 80), (226, 14), (238, 80)], fill=(236, 236, 232)); d.line([226, 20, 226, 78], fill=(120, 120, 118))          # a leaf
    for x in range(0, 264, 3):
        for y in range(0, 96, 3):
            if (x * 7 + y * 13) % 29 == 0: d.point((x, y), fill=(70, 70, 70))
    return im

def sv_screen():
    # the catalogue: a halftone screen enlarged, its dots growing from the highlights to the shadows
    im, d = canvas(264, 96, SP)
    for i in range(33):
        for j in range(12):
            x, y = 4 + i * 8, 4 + j * 8
            r = 0.4 + 3.6 * (i / 32)
            d.ellipse([x + 4 - r, y + 4 - r, x + 4 + r, y + 4 + r], fill=SK)
    return im

def sv_cover():
    # a landscape in eleven greys: a pale sky, three ranges of hills each a zone darker, a lake
    im, d = canvas(300, 225, GREYS[2])
    rnd = random.Random(1941)
    for y in range(0, 90): d.line([0, y, 300, y], fill=GREYS[1 if y < 40 else 2])
    for k, (base, amp, z) in enumerate(((110, 26, 4), (140, 20, 6), (170, 14, 8))):
        pts = [(x, base - amp * (0.6 * math.sin(x / (37 + k * 9) + k) + 0.4 * math.sin(x / 13 + k * 2))) for x in range(0, 301, 3)]
        d.polygon(pts + [(300, 225), (0, 225)], fill=GREYS[z])
    d.rectangle([0, 192, 300, 225], fill=GREYS[3])
    for k in range(60):
        x = rnd.randint(0, 296); y = rnd.randint(194, 222); d.line([x, y, x + rnd.randint(4, 16), y], fill=GREYS[2])
    return im

if __name__ == '__main__':
    for name, fn in (('cn-contents.png', cn_listing), ('cn-a1.png', cn_boxes), ('cn-a2.png', cn_heap), ('cn-a3.png', cn_machine),
                     ('cn-catalogue.png', cn_cards), ('cn-cover-field.png', cn_cover),
                     ('sv-contents.png', sv_contact), ('sv-a1.png', sv_zones), ('sv-a2.png', sv_curve), ('sv-a3.png', sv_photogram),
                     ('sv-catalogue.png', sv_screen), ('sv-cover-field.png', sv_cover)):
        save(fn(), name)
    names = ['cn-contents', 'cn-a1', 'cn-a2', 'cn-a3', 'cn-catalogue', 'sv-contents', 'sv-a1', 'sv-a2', 'sv-a3', 'sv-catalogue']
    sheet = Image.new('RGB', (264 * 2 + 6, 96 * 5 + 24), (90, 90, 90))
    for i, n in enumerate(names):
        sheet.paste(Image.open(REPO + '/v25/assets/st/%s.png' % n), ((i // 5) * 270, (i % 5) * 100))
    sheet.save(UTIL + '/v25/plates3.png')
    c = Image.new('RGB', (606, 225)); c.paste(Image.open(REPO + '/v25/assets/st/cn-cover-field.png'), (0, 0)); c.paste(Image.open(REPO + '/v25/assets/st/sv-cover-field.png'), (306, 0))
    c.save(UTIL + '/v25/covers4.png')
    print('ok')
