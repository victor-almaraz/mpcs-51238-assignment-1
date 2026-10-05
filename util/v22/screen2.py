# v22's computer pictures, second pass: more detail throughout, in the same flat poster
# manner. The desk picture adds the Milky Way, a moon with its maria, the mountain's facets
# and the royal tombs cut in its face, the torch-bearers' river of fire with its glow, soft
# searchlight beams with dust in them, the terrace's stepped parapet and stair, fluted
# columns with bull capitals, the Gate's piers with their winged bulls, bonfires, and the
# audience on the terrace. The plates carry real type (outlined from the bundled faces):
# code on the coding sheet, the program and its data, printer lines, numbers on the sieve.
import math, random
from screen import f, rect, circle, path, lin, rad, Type, save, P

def blur(id, sd):
    return '<filter id="%s" x="-50%%" y="-50%%" width="200%%" height="200%%"><feGaussianBlur stdDeviation="%s"/></filter>' % (id, sd)

# ---------------------------------------------------------------- the desk: Persepolis at night
def desktop():
    random.seed(1971)
    W, H = 1600, 1000
    D = [lin('sky', [(0, '#08111d'), (0.35, '#13243a'), (0.66, '#223a56'), (0.84, '#3a4f66'), (1, '#5b5a5a')]),
         lin('far', [(0, '#2c4058'), (1, '#1f3047')]), lin('mtn', [(0, '#1c2c40'), (1, '#121c2a')]),
         lin('mtnlit', [(0, '#3a3d44', 0), (1, '#6a4a32', 0.35)]),
         lin('gnd', [(0, '#121b27'), (1, '#090e16')]), lin('col', [(0, '#0e1722'), (0.75, '#0b131c'), (1, '#1a1814')], 1, 0),
         rad('glow', [(0, '#f2a94a', 0.6), (0.35, '#e08a3a', 0.2), (1, '#e08a3a', 0)]),
         rad('torch', [(0, '#fff1c4', 1), (0.3, '#f5b54f', 0.85), (1, '#f3b24c', 0)]),
         rad('fire', [(0, '#ffe7a8', 0.95), (0.25, '#f4a640', 0.6), (1, '#e0743a', 0)]),
         rad('moonhalo', [(0, '#f6efdc', 0.32), (0.4, '#f6efdc', 0.1), (1, '#f6efdc', 0)]),
         rad('moon', [(0, '#fbf6e6'), (0.8, '#ece2c8'), (1, '#d9ccad')], 0.42, 0.4, 0.6),
         lin('mw', [(0, '#c9d6e8', 0), (0.5, '#c9d6e8', 0.16), (1, '#c9d6e8', 0)], 1, 0.4),
         blur('b2', 2), blur('b6', 6), blur('b14', 14), blur('b30', 30)]
    o = [rect(0, 0, W, H, 'url(#sky)')]
    # the Milky Way: a soft band across the upper sky, thick with small stars
    o.append('<ellipse cx="900" cy="230" rx="900" ry="80" fill="url(#mw)" transform="rotate(-14 900 230)" filter="url(#b30)"/>')
    st, mw = [], []
    for k in range(260):
        x, y = random.uniform(0, W), random.uniform(0, 600)
        if random.random() < (y / 600) ** 1.6: continue
        st.append('M%s %sh0' % (f(x), f(y)))
    for k in range(320):
        t = random.uniform(-1, 1)
        x = 900 + t * 880; y = 230 - t * 220 * math.tan(math.radians(14)) * 1.0 + random.gauss(0, 34)
        mw.append('M%s %sh0' % (f(x), f(y)))
    o.append(path(''.join(st), stroke='#f2ead8', stroke_width='1.5', stroke_linecap='round', opacity='.5'))
    o.append(path(''.join(mw), stroke='#e6edf7', stroke_width='1.1', stroke_linecap='round', opacity='.45'))
    big = ''.join('M%s %sh0' % (f(random.uniform(0, W)), f(random.uniform(20, 380))) for k in range(30))
    o.append(path(big, stroke='#fff6e0', stroke_width='2.8', stroke_linecap='round', opacity='.85'))
    # the moon, low over the left, with its maria
    o.append(circle(250, 190, 150, 'url(#moonhalo)'))
    o.append(circle(250, 190, 27, 'url(#moon)'))
    for cx, cy, r in ((242, 182, 7), (258, 196, 5), (247, 201, 3.6), (262, 180, 3)):
        o.append(circle(cx, cy, r, '#cbbd9c', opacity='.45'))
    # searchlight beams from the terrace, soft-edged, crossing high over the mountain, with dust
    beams = [(1010, 772, 700), (1150, 776, 1580), (1080, 770, 1230)]
    for i, (bx, by, tx) in enumerate(beams):
        a = math.atan2(-by, tx - bx); L = 1300
        ex, ey = bx + L * math.cos(a), by + L * math.sin(a)
        nx, ny = -math.sin(a), math.cos(a)
        d = 'M%s %sL%s %sL%s %sL%s %sz' % (f(bx + nx * 4), f(by + ny * 4), f(ex + nx * 75), f(ey + ny * 75), f(ex - nx * 75), f(ey - ny * 75), f(bx - nx * 4), f(by - ny * 4))
        D.append('<linearGradient id="bm%d" gradientUnits="userSpaceOnUse" x1="%s" y1="%s" x2="%s" y2="%s"><stop offset="0" stop-color="#f4e8c8" stop-opacity=".36"/><stop offset=".6" stop-color="#f4e8c8" stop-opacity=".08"/><stop offset="1" stop-color="#f4e8c8" stop-opacity="0"/></linearGradient>' % (i, f(bx), f(by), f(ex), f(ey)))
        o.append(path(d, 'url(#bm%d)' % i, filter='url(#b6)'))
        o.append(path('M%s %sL%s %s' % (f(bx), f(by), f(bx + 900 * math.cos(a)), f(by + 900 * math.sin(a))), stroke='#fff3d6', stroke_width='3', opacity='.18', filter='url(#b2)'))
        dust = ''.join('M%s %sh0' % (f(bx + (s := random.uniform(80, 900)) * math.cos(a) + nx * random.uniform(-s * 0.05, s * 0.05)), f(by + s * math.sin(a) + ny * random.uniform(-s * 0.05, s * 0.05))) for k in range(40))
        o.append(path(dust, stroke='#fff6e0', stroke_width='1.2', stroke_linecap='round', opacity='.35'))
    # the far range
    def ridge(pts): return 'M' + 'L'.join('%s %s' % (f(x), f(y)) for x, y in pts)
    far = [(0, 640)] + [(k * 40, 620 - 55 * math.sin(k * 0.4) - 22 * math.sin(k * 1.3 + 1) + random.uniform(-7, 7)) for k in range(1, 41)]
    o.append(path(ridge(far) + 'L1600 1000L0 1000z', 'url(#far)'))
    o.append('<rect x="0" y="560" width="1600" height="120" fill="#4a5a6c" opacity=".12" filter="url(#b30)"/>')   # haze in the valley
    # Kuh-e Rahmat, the Mount of Mercy, behind the terrace: its ridge, its rock facets
    mt = [(0, 780), (160, 742), (320, 700), (470, 640), (600, 585), (720, 528), (820, 486), (905, 452), (960, 440), (1010, 448),
          (1090, 478), (1190, 520), (1300, 566), (1420, 610), (1520, 650), (1600, 672)]
    pts = []
    for i in range(len(mt) - 1):
        (x0, y0), (x1, y1) = mt[i], mt[i + 1]
        for t in (0, 0.25, 0.5, 0.75):
            pts.append((x0 + (x1 - x0) * t, y0 + (y1 - y0) * t + (random.uniform(-6, 6) if t else 0)))
    pts.append(mt[-1])
    o.append(path(ridge(pts) + 'L1600 1000L0 1000z', 'url(#mtn)'))
    facets = []
    for k in range(26):
        x = random.uniform(380, 1400); top = 470 + abs(x - 960) * 0.55 + random.uniform(10, 60)
        w = random.uniform(30, 90); h = random.uniform(40, 120)
        facets.append('M%s %sl%s %sl%s %sz' % (f(x), f(top), f(w * 0.5), f(h), f(-w), f(h * random.uniform(0.6, 1))))
    o.append(path(''.join(facets), '#24364c', opacity='.35'))
    o.append(path(ridge(pts) + 'L1600 1000L0 1000z', 'url(#mtnlit)'))
    # the royal tombs cut in the mountain's face: two cruciform façades, faintly lit
    for tx, ty, s in ((780, 590, 1.0), (1150, 600, 0.9)):
        d = ('M%s %sh%sv%sh%sv%sh%sv%sh%sv%sh%sv%sz' % (f(tx - 18 * s), f(ty), f(36 * s), f(22 * s), f(26 * s), f(26 * s), f(-26 * s), f(30 * s), f(-36 * s), f(-30 * s), f(-26 * s), f(-26 * s)))
        o.append(path(d, '#2c3646', opacity='.85'))
        o.append(path('M%s %sh%s' % (f(tx - 40 * s), f(ty + 34 * s), f(80 * s)), stroke='#5a4632', stroke_width='1.2', opacity='.6'))
        o.append(''.join(rect(tx - 34 * s + k * 15 * s, ty + 26 * s, 3 * s, 22 * s, '#1a2230') for k in range(5)))
    # the torch-bearers' path: switchbacks up the mountain, a river of fire with its glow
    sw = [(560, 770), (900, 742), (700, 712), (980, 682), (790, 650), (1040, 620), (860, 590), (1060, 560), (920, 530), (1010, 500), (955, 470)]
    route = 'M' + 'L'.join('%s %s' % xy for xy in sw)
    o.append(path(route, stroke='#f0a24a', stroke_width='14', stroke_linejoin='round', opacity='.22', filter='url(#b14)'))
    tor, core = [], []
    for i in range(len(sw) - 1):
        (x0, y0), (x1, y1) = sw[i], sw[i + 1]
        n = int(math.hypot(x1 - x0, y1 - y0) / 11)
        for k in range(n):
            t = k / n
            x, y = x0 + (x1 - x0) * t + random.uniform(-1.6, 1.6), y0 + (y1 - y0) * t + random.uniform(-1.6, 1.6)
            s = 1 - 0.55 * (770 - y) / 300
            tor.append(circle(x, y, 6 * s, 'url(#torch)'))
            core.append('M%s %sh0' % (f(x), f(y)))
    o.append(''.join(tor))
    o.append(path(''.join(core), stroke='#fff3cf', stroke_width='2.2', stroke_linecap='round'))
    # the light of the bonfires on the terrace
    o.append('<ellipse cx="820" cy="790" rx="560" ry="130" fill="url(#glow)"/>')
    # the terrace: its long wall with the stepped merlons of Persepolis along its parapet, the stair
    o.append(path('M0 794L1600 802V1000H0z', 'url(#gnd)'))
    o.append(rect(140, 772, 1120, 30, '#0e1622'))
    merl = ''
    for k in range(56):
        x = 146 + k * 20
        merl += 'M%s 772v-6h3v-3h3v-3h4v3h3v3h3v6z' % f(x)
    o.append(path(merl, '#0e1622'))
    o.append(rect(140, 772, 1120, 2.5, '#7a5a3a', opacity='.7'))
    o.append(path(''.join('M%s 778h14v4h-14z' % f(160 + k * 27) for k in range(41)), '#0a1119'))
    # the great stair: two flights rising to the terrace from either side
    o.append(path('M560 802L620 772h40L600 802zM760 802L700 772h-40L720 802z', '#101a26'))
    o.append(path(''.join('M%s %sh%s' % (f(600 + k * 6), f(800 - k * 3.6), f(14)) for k in range(8)), stroke='#6a4e33', stroke_width='.8', opacity='.5'))
    ruins = []
    # the Gate of All Nations: two piers, each with a winged bull in relief facing out
    for x, side in ((330, -1), (420, 1)):
        ruins.append(rect(x, 598, 46, 172, 'url(#col)'))
        ruins.append(rect(x, 598, 46, 3, '#7a5a3a', opacity='.55'))
        ruins.append(rect(x + 40, 602, 6, 168, '#5a4430', opacity='.35'))
        bx = x + 23
        ruins.append(path('M%s 700l%s -4 %s -18 %s 6 %s 4 %s 22 %s 0 %s 40h%sv-40z' % (f(bx - side * 14), f(side * 10), f(side * 4), f(side * 10), f(side * 4), f(-side * 6), f(-side * 6), f(side * 0), f(-side * 6)), '#1d2a38', opacity='.9'))
        ruins.append(path('M%s 684q%s -20 %s -26' % (f(bx), f(side * 12), f(side * 20)), stroke='#2c3a4a', stroke_width='3', fill='none'))
    # the Apadana's columns, standing and broken: bell bases, fluted shafts, bull capitals
    cols = [(560, 548), (610, 538), (660, 590), (710, 546), (770, 680), (820, 552), (870, 600), (930, 562), (990, 700), (1040, 580), (1100, 640), (1150, 594), (1195, 720)]
    for x, top in cols:
        whole = top < 650
        ruins.append(path('M%s 770q2 -8 6 -9h13q4 1 6 9z' % f(x - 6), '#0b131c'))
        ruins.append(rect(x, top, 13, 762 - top, 'url(#col)'))
        ruins.append(path(''.join('M%s %sV762' % (f(x + 3 + j * 3.4), f(top + 3)) for j in range(3)), stroke='#22303f', stroke_width='.7'))
        ruins.append(rect(x + 10, top + 4, 3, 758 - top, '#7a5a3a', opacity='.42'))
        if whole:
            # the capital: a block, then two bulls back to back, their heads and forelegs out
            ruins.append(rect(x - 3, top - 10, 19, 10, '#0b131c'))
            ruins.append(path('M%s %sh41l-4 -6h-8l-3 -5h-4l-2 3h-9l-2 -3h-4l-3 5h-8z' % f(x - 14) % () if False else
                              'M%s %sh41l-4 -6h-7l-2 -6h-4l-1 3h-5v4h-1v-4h-5l-1 -3h-4l-2 6h-7z' % (f(x - 14), f(top - 10)), '#0b131c'))
            ruins.append(rect(x - 14, top - 10, 41, 1.6, '#7a5a3a', opacity='.45'))
        else:
            ruins.append(path('M%s %sl4 -3 3 2 3 -4 3 3z' % (f(x), f(top)), '#0b131c'))
    o.append(''.join(ruins))
    # bonfires along the terrace, each a flame with its light on the stones
    for x in (250, 520, 760, 1000, 1240):
        o.append(circle(x, 764, 46, 'url(#fire)', opacity='.8'))
        o.append(path('M%s 772c-7 0 -9 -6 -6 -12c2 -4 1 -8 4 -12c1 5 4 6 5 9c1 -3 2 -5 1 -8c4 4 6 9 5 13c0 6 -3 10 -9 10z' % f(x), '#ffcf6e'))
        o.append(path('M%s 772c-3 0 -4 -3 -3 -6c1 -2 1 -4 2 -6c1 3 3 4 3 6c0 4 -1 6 -2 6z' % f(x + 1), '#fff3c6'))
    # the audience on the terrace's edge, in silhouette against the fires
    aud = []
    for k in range(160):
        x = 120 + k * 8.4 + random.uniform(-2, 2); y = 806 + random.uniform(-2, 3); s = random.uniform(0.85, 1.15)
        aud.append('M%s %sa%s %s 0 1 1 %s 0zM%s %sq%s %s %s 0v12h%sz' % (f(x - 2.4 * s), f(y), f(2.4 * s), f(2.6 * s), f(4.8 * s), f(x - 4.6 * s), f(y + 9 * s), f(4.6 * s), f(-7 * s), f(9.2 * s), f(-9.2 * s)))
    o.append(path(''.join(aud), '#070b11'))
    o.append(path('M0 900Q400 880 800 905T1600 895V1000H0z', '#05080d'))
    save('desktop', W, H, ''.join(o), ''.join(D), aspect='xMidYMid slice')

# ---------------------------------------------------------------- Read Me: two fans of glissandi
def hero():
    W, H = 640, 200
    T = Type()
    o = [rect(0, 0, W, H, P['paper'])]
    # graph paper: a fine grid, every fifth line heavier
    fine = ''.join('M%d 0v%d' % (x, H) for x in range(20, W, 10)) + ''.join('M0 %dh%d' % (y, W) for y in range(10, H, 10))
    o.append(path(fine, stroke='#d9cfbb', stroke_width='.4'))
    heavy = ''.join('M%d 0v%d' % (x, H) for x in range(20, W, 50)) + ''.join('M0 %dh%d' % (y, W) for y in range(10, H, 50))
    o.append(path(heavy, stroke='#c4b79c', stroke_width='.7'))
    a, b = [], []
    for k in range(32):
        t = k / 31
        a.append('M20 %sL620 %s' % (f(100 + (t - 0.5) * 12), f(12 + t * 176)))
        b.append('M20 %sL620 %s' % (f(14 + t * 172), f(100 + (0.5 - t) * 10)))
    o.append(path(''.join(b), stroke=P['blue'], stroke_width='.9', opacity='.9'))
    o.append(path(''.join(a), stroke=P['accent'], stroke_width='.9', opacity='.9'))
    # the bars along the foot and the pitches up the side, lettered as on Xenakis's graph
    for k, bar in enumerate(range(309, 315)):
        x = 20 + k * 120
        o.append(path('M%s 188v8' % f(x), stroke=P['ink'], stroke_width='.8'))
        o.append(T.text(x + 4, 196, str(bar), 8, P['soft'], 'work-sans', 400))
    for y, lab in ((20, 'C7'), (100, 'C4'), (180, 'C1')):
        o.append(T.text(4, y + 3, lab, 7, P['soft'], 'work-sans', 400))
    save('hero', W, H, ''.join(o), '', T, title='Two fans of glissandi')

# ---------------------------------------------------------------- the About plates, 720 x 120
def plate(name, body, T=None, defs='', ground=None):
    W, H = 720, 120
    save(name, W, H, rect(0, 0, W, H, ground or P['cream']) + body, defs, T)

PROG = ['C     SQUARES AND SQUARE ROOTS', '      WRITE (6,10)', '   10 FORMAT (1H1,5X,1HN,6X,6HSQUARE,5X,4HROOT)', '      DO 20 I = 1, 5',
        '      X = FLOAT(I)', '      Y = SQRT(X)', '      WRITE (6,30) I, I*I, Y', '   20 CONTINUE']

def plates():
    random.seed(57)
    U = 6.6   # one column: Plex Mono's 0.6 em at 11 units
    # 0 history: a coding sheet: fields shaded, the program in pencil, the margin at 72
    T = Type()
    o = rect(24, 0, 5 * U, 120, '#e7d8b8') + rect(24 + 5 * U, 0, U, 120, '#dcc28e')
    o += path(''.join('M%s 0v120' % f(24 + k * U * 10) for k in range(11)), stroke='#d2c4a8', stroke_width='.6')
    o += path(''.join('M24 %sh%s' % (f(9 + k * 13.4), f(80 * U)) for k in range(9)), stroke='#d9cdb3', stroke_width='.5')
    for i, line in enumerate(PROG):
        o += T.text(24 + 1, 19 + i * 13.4, line, 11, '#3f4a50', 'ibm-plex-mono', 400)
    o += rect(24 + 72 * U - 0.8, 0, 1.6, 120, P['accent'])
    o += rect(24 + 72 * U + 1, 0, 8 * U, 120, '#e8dcc6')
    o += T.text(24 + 76 * U, 114, '73–80', 7, P['soft'], 'work-sans', 400, 'middle')
    plate('plate-0', o, T)
    # 1 the job: the program, its END, and the data after it, in another ink
    T = Type()
    job = [('      READ (5,10) N', P['slate']), ('   10 FORMAT (I5)', P['slate']), ('      PRINT 20, N, N*N', P['slate']), ('   20 FORMAT (2I8)', P['slate']),
           ('      END', P['accent']), ('   12', P['blue_l']), ('  144', P['blue_l'])]
    for i, (line, c) in enumerate(job):
        o2 = T.text(30, 16 + i * 15, line, 12, c, 'ibm-plex-mono', 700 if c == P['accent'] else 400)
        o = (o if i else '') + o2
    o += path('M300 6v108', stroke='#cdbf9f', stroke_width='1', stroke_dasharray='3 4')
    o += T.text(316, 74, 'the program', 10, P['soft'], 'work-sans', 400) + T.text(316, 104, 'its data', 10, P['blue_l'], 'work-sans', 400)
    o += path('M312 18v58M312 84v26', stroke=P['soft'], stroke_width='1')
    plate('plate-1', o, T)
    # 2 using the workspace: windows over the desk, with their titles and their buttons
    T = Type()
    o = rect(0, 0, 720, 120, P['blue']) + ''.join(circle(random.uniform(0, 720), random.uniform(0, 120), 0.8, '#f2ead8', opacity='.6') for k in range(40))
    for x, y, w, title in [(40, 22, 230, 'Read Me'), (210, 46, 260, 'Editor'), (420, 14, 250, 'Player')]:
        o += rect(x + 3, y + 5, w, 120, '#000', 8, opacity='.28')
        o += rect(x, y, w, 120, P['paper'], 8) + rect(x, y, w, 18, '#e6dfd0', 8) + rect(x, y + 10, w, 8, '#e6dfd0') + rect(x, y + 18, w, 0.6, '#cfc5b2')
        o += circle(x + 11, y + 9, 3.6, P['accent']) + circle(x + 23, y + 9, 3.6, P['ochre'])
        o += T.text(x + w / 2, y + 12.5, title, 8, P['ink'], 'work-sans', 600, 'middle')
        if title == 'Editor':
            for i, line in enumerate(PROG[1:5]): o += T.text(x + 12, y + 32 + i * 11, line.strip(), 8, '#3f4a50', 'ibm-plex-mono', 400)
        else:
            o += ''.join(rect(x + 14, y + 28 + i * 11, w * l, 4, '#b9b0a0', 2) for i, l in enumerate((0.7, 0.55, 0.62, 0.4)))
    for k in range(4):
        o += rect(686, 14 + k * 26, 18, 14, ['#d6a540', '#2b4560', '#9a6136', '#7d8a78'][k], 3)
    plate('plate-2', o, T)
    # 3 the language: DO loops within loops, their labels and CONTINUE lines
    T = Type()
    o = ''
    for k, (c, w, lab) in enumerate([(P['ochre'], 640, 'DO 30'), (P['sage'], 480, 'DO 20'), (P['blue_l'], 320, 'DO 10'), (P['accent'], 160, 'X = X + 1')]):
        x, y, h = 360 - w / 2, 14 + k * 12, 92 - k * 24
        o += rect(x, y, w, h, 'none', h / 2, stroke=c, stroke_width='5')
        o += path('M%s %sh12l-6 9z' % (f(x + w - 6), f(y + h / 2 - 4)), c)
        o += T.text(360, y + 4 + (h / 2 if k == 3 else 0), lab, 9, c if k < 3 else P['ink'], 'ibm-plex-mono', 700, 'middle') if k == 3 else T.text(x + 26, y + h / 2 + 3, lab, 9, c, 'ibm-plex-mono', 700)
    plate('plate-3', o, T)
    # 4 the line printer: fan-fold paper, printed, green bars and sprocket holes, folded
    T = Type()
    printed = ['   N   SQUARE     ROOT', '   1        1   1.0000', '   2        4   1.4142', '   3        9   1.7321', '   4       16   2.0000', '   5       25   2.2361', '', ' STOP']
    o = ''
    for k in range(3):
        x = 30 + k * 230
        sk = 'translate(%d 0) skewY(%d)' % (x, -6 if k % 2 else 6)
        g = rect(0, 8, 210, 100, '#fffdf8', stroke='#cfc5b2') + ''.join(rect(16, 14 + j * 22, 178, 11, P['green']) for j in range(5))
        g += ''.join(circle(7, 14 + j * 9, 2.4, P['cream'], stroke='#b7ad99') + circle(203, 14 + j * 9, 2.4, P['cream'], stroke='#b7ad99') for j in range(11))
        g += path('M3 8v100M207 8v100', stroke='#cfc5b2', stroke_width='.6', stroke_dasharray='2 2')
        for i, line in enumerate(printed): g += T.text(20, 22 + i * 11, line, 8.4, '#4a4741', 'ibm-plex-mono', 400)
        o += '<g transform="%s">%s</g>' % (sk, g)
    plate('plate-4', o, T)
    # 5 Xenakis: a ruled surface, two families of straight lines, and its edges lettered
    T = Type()
    a, b = [], []
    for k in range(41):
        t = k / 40
        a.append('M%s 14L%s 106' % (f(40 + t * 640), f(360 + (t - 0.5) * 120)))
        b.append('M%s 106L%s 14' % (f(40 + t * 640), f(360 + (0.5 - t) * 520)))
    o = path(''.join(b), stroke=P['blue_l'], stroke_width='.8', opacity='.85') + path(''.join(a), stroke=P['accent'], stroke_width='.8')
    o += path('M40 14H680M40 106H680', stroke=P['ink'], stroke_width='1')
    for x, y, l in ((34, 12, 'A'), (684, 12, 'B'), (34, 112, 'D'), (684, 112, 'C')):
        o += T.text(x, y, l, 9, P['ink'], 'libre-caslon-text', 400, 'middle', style='italic')
    plate('plate-5', o, T)
    # 6 the sieve: 48 points, the members of 3@0 | 4@1 | 6@5 raised, numbered every 12
    T = Type()
    o = path('M24 88h672', stroke=P['soft'], stroke_width='1')
    for n in range(48):
        x = 30 + n * 14
        on = n % 3 == 0 or n % 4 == 1 or n % 6 == 5
        if on:
            hh = 18 + 46 * ((n % 3 == 0) + (n % 4 == 1) + (n % 6 == 5)) / 3
            o += rect(x - 4, 88 - hh, 8, hh, P['ochre'], 2) + rect(x - 4, 88 - hh, 2, hh, '#fff', 1, opacity='.25')
        o += circle(x, 88, 3 if on else 1.6, P['ink'] if on else P['soft'])
        if n % 12 == 0:
            o += path('M%s 92v6' % f(x), stroke=P['soft'], stroke_width='1') + T.text(x, 110, str(n), 9, P['soft'], 'ibm-plex-mono', 400, 'middle')
    o += T.text(696, 20, '3@0 | 4@1 | 6@5', 10, P['ink'], 'ibm-plex-mono', 400, 'end')
    plate('plate-6', o, T)
    # 7 the music programs: notes on a roll, coloured by loudness, the octaves lettered
    T = Type()
    o = ''.join(path('M30 %sh690' % f(y), stroke='#d6c9ad', stroke_width='.8', stroke_dasharray='2 3') + T.text(6, y + 3, l, 8, P['soft'], 'work-sans', 400) for y, l in ((24, 'C5'), (60, 'C4'), (96, 'C3')))
    o += ''.join(path('M%s 110v6' % f(30 + k * 56), stroke=P['soft'], stroke_width='.8') for k in range(13))
    q, l = (143, 176, 200), (181, 70, 43)
    t = 0
    while t < 670:
        n = random.randint(0, 20); ln = random.choice((14, 14, 28, 42)); v = random.random()
        c = '#%02x%02x%02x' % tuple(int(q[i] + (l[i] - q[i]) * v) for i in range(3))
        o += rect(30 + t, 100 - n * 4.2, ln - 3, 7, c, 3) + rect(30 + t, 100 - n * 4.2, ln - 3, 2, '#fff', 1, opacity='.3')
        t += random.choice((7, 14, 14, 21))
    plate('plate-7', o, T)
    # 8 the Player: two reels with their spokes and tape, the sound leaving them, a meter
    o = ''
    for cx, pack in ((80, 34), (210, 22)):
        o += circle(cx, 60, 46, P['teak']) + circle(cx, 60, 44, '#a86c40')
        o += circle(cx, 60, pack + 6, '#3b2a1d') + ''.join(circle(cx, 60, pack + 6 - j * 2, 'none', stroke='#4a3626', stroke_width='.5') for j in range(1, 6))
        o += ''.join(path('M%s %sL%s %s' % (f(cx + 9 * math.cos(a)), f(60 + 9 * math.sin(a)), f(cx + 40 * math.cos(a)), f(60 + 40 * math.sin(a))), stroke=P['teak'], stroke_width='7') for a in (0.5, 2.6, 4.7))
        o += circle(cx, 60, 13, P['cream']) + circle(cx, 60, 4, P['ink'])
        o += ''.join(rect(cx - 1, 60 - 12, 2, 4, P['ink'], transform='rotate(%d %d 60)' % (a, cx)) for a in (0, 120, 240))
    o += path('M80 106H210', stroke='#3b2a1d', stroke_width='3')
    d = 'M270 60' + ''.join('L%s %s' % (f(270 + k * 2), f(60 + 40 * math.sin(k * 0.21) * math.exp(-((k - 110) / 70) ** 2) * (0.6 + 0.4 * math.sin(k * 0.047)))) for k in range(1, 196))
    o += path('M270 60H660', stroke='#c9bc9f', stroke_width='1') + path(d, stroke=P['accent'], stroke_width='2.4', stroke_linejoin='round')
    o += rect(668, 26, 40, 68, '#f6efdc', 6, stroke='#c9bc9f') + ''.join(rect(676, 84 - k * 8, 24, 5, P['sage'] if k < 5 else P['ochre'] if k < 7 else P['accent'], 1.5) for k in range(8))
    plate('plate-8', o)

# ---------------------------------------------------------------- Hugo Ball, 1916
def ball():
    W, H = 480, 400
    T = Type()
    D = (lin('gold', [(0, '#ecc562'), (0.5, '#d5a53a'), (1, '#b88a26')], 1, 1) + lin('golddk', [(0, '#c2922c'), (1, '#93691b')]) +
         lin('red', [(0, '#c9533a'), (1, '#8f2e1e')]) + lin('tube', [(0, '#2b4560'), (0.35, '#7f9dbd'), (0.6, '#4f7194'), (1, '#22384f')], 1, 0) +
         lin('collar', [(0, '#ffffff'), (1, '#d9d2c2')], 1, 0) + lin('floor', [(0, '#e9dfcc'), (1, '#d8ccb4')]) +
         rad('spot', [(0, '#fff8e6', 0.9), (1, '#fff8e6', 0)]))
    o = [rect(0, 0, W, H, '#f3ede0'), '<ellipse cx="250" cy="200" rx="230" ry="200" fill="url(#spot)"/>',
         rect(0, 352, W, 48, 'url(#floor)'), path('M0 352h480', stroke='#bfb39d', stroke_width='1.5')]
    o.append('<ellipse cx="258" cy="354" rx="120" ry="7" fill="#000" opacity=".12"/>')
    # the music stand, its desk of poems
    o.append(path('M86 350l22-34 22 34M108 316V176', stroke=P['ink'], stroke_width='3', stroke_linecap='round'))
    o.append(path('M70 152l76 8-6 42-74-8z', P['cream'], stroke=P['ink'], stroke_width='2', stroke_linejoin='round'))
    o.append(path('M72 190l72 8', stroke=P['ink'], stroke_width='3'))
    o.append(path(''.join('M%s %sl%s %s' % (f(80), f(164 + k * 6.4), 54, 5.8) for k in range(5)), stroke='#8f8574', stroke_width='1.2'))
    # the legs, in cardboard tubes banded at the knee, the feet in dark shoes
    for x in (238, 272):
        o.append(rect(x, 262, 26, 86, 'url(#tube)', 3))
        o.append(path('M%s 290h26M%s 318h26' % (x, x), stroke='#f3ede0', stroke_width='2.5'))
        o.append(path('M%s 262v86' % (x + 8), stroke='#ffffff', stroke_width='1.4', opacity='.35'))
        o.append(path('M%s 348h34v6q-17 4-34 0z' % (x - 4), P['ink']))
    # the cape: two stiff wings, scarlet within, gold without, creased, with claws at the ends
    o.append(path('M255 150L150 214L190 286L255 230z', 'url(#red)'))
    o.append(path('M255 150L360 214L320 286L255 230z', 'url(#red)'))
    o.append(path('M255 140L176 196L130 270L196 300L255 238L314 300L380 270L334 196z', 'url(#gold)', stroke='#8f6a1f', stroke_width='1.5', stroke_linejoin='round'))
    o.append(path('M255 140L176 196L130 270L196 300L255 238z', 'url(#golddk)', opacity='.35'))
    o.append(path('M255 152V238M200 200L176 280M310 200L334 280M228 176L208 252M282 176L302 252', stroke='#9d7623', stroke_width='1.3'))
    o.append(path('M150 264l46 30M360 264l-46 30', stroke='#fff2c4', stroke_width='1.2', opacity='.6'))
    for sx in (-1, 1):
        cx = 255 + sx * 118
        o.append(path('M%s 268l%s 26M%s 270l%s 30M%s 266l%s 22M%s 268l%s 24' % (f(cx), f(sx * 6), f(cx - sx * 8), f(sx * 2), f(cx + sx * 8), f(sx * 12), f(cx + sx * 3), f(sx * 9)), stroke=P['ink'], stroke_width='3', stroke_linecap='round'))
    # the high collar, the face: a pale mask with dark brows, the mouth open to recite
    o.append(path('M220 150Q255 118 290 150L282 108Q255 96 228 108z', 'url(#collar)', stroke=P['ink'], stroke_width='2', stroke_linejoin='round'))
    o.append(path('M232 112Q255 104 278 112', stroke='#b9b0a0', stroke_width='1'))
    o.append('<ellipse cx="255" cy="94" rx="15" ry="18" fill="#ecd3b8" stroke="%s" stroke-width="1.6"/>' % P['ink'])
    o.append(path('M246 88q3 -2 6 0M258 88q3 -2 6 0', stroke=P['ink'], stroke_width='1.8', stroke_linecap='round'))
    o.append(path('M249 93h3M259 93h3', stroke=P['ink'], stroke_width='1.6', stroke_linecap='round'))
    o.append('<ellipse cx="255" cy="104" rx="3" ry="2.4" fill="#5a2a1e"/>')
    # the hat: a tall cylinder striped blue and white, its top an ellipse
    o.append(rect(236, 18, 38, 62, '#fbf8f0', 2, stroke=P['ink'], stroke_width='2'))
    o.append(''.join(rect(238, 22 + k * 12, 34, 6, P['blue']) for k in range(5)))
    o.append(rect(238, 20, 6, 58, '#ffffff', opacity='.3'))
    o.append('<ellipse cx="255" cy="18" rx="19" ry="3.4" fill="#fbf8f0" stroke="%s" stroke-width="2"/>' % P['ink'])
    o.append(rect(230, 76, 50, 6, P['ink'], 2))
    o.append(T.text(456, 36, 'Zürich, 1916', 15, P['soft'], 'jost', 400, 'end', ls=0.6))
    o.append(T.text(456, 54, 'Cabaret Voltaire', 11, P['soft'], 'jost', 400, 'end', ls=0.6))
    save('ball', W, H, ''.join(o), D, T, title='Hugo Ball in his cardboard costume at the Cabaret Voltaire')

# ---------------------------------------------------------------- Tzara's hat
def hat():
    W, H = 480, 320
    T = Type()
    random.seed(1920)
    D = (lin('felt', [(0, '#3a3733'), (0.5, '#1e1d1b'), (1, '#0f0e0d')], 1, 0) + lin('floor', [(0, '#e9dfcc'), (1, '#d8ccb4')]) +
         lin('steel', [(0, '#e4e3df'), (0.5, '#a9a7a1'), (1, '#6f6d68')], 1, 1))
    o = [rect(0, 0, W, H, '#f3ede0'), rect(0, 268, W, 52, 'url(#floor)'), path('M0 268h480', stroke='#bfb39d', stroke_width='1.5')]
    # the newspaper, folded, a column cut away: masthead, headline, columns of text
    o.append('<ellipse cx="76" cy="270" rx="62" ry="4" fill="#000" opacity=".12"/>')
    o.append(path('M18 190h96l18 18v60H18z', '#fbf8f0', stroke='#a59b88', stroke_width='1.4', stroke_linejoin='round'))
    o.append(path('M114 190v18h18', stroke='#a59b88', stroke_width='1.2'))
    o.append(T.text(24, 202, 'LE JOURNAL', 9, P['ink'], 'libre-caslon-text', 700))
    o.append(path('M24 206h88', stroke=P['ink'], stroke_width='.8'))
    o.append(rect(24, 210, 60, 5, '#4a4741'))
    for c in range(3):
        for k in range(6):
            if c == 1 and 1 < k < 5: continue          # the article cut out
            o.append(rect(24 + c * 34, 220 + k * 7, 28 - (k % 3) * 3, 2.4, '#8f8574'))
    o.append(path('M58 232h28v20h-28z', '#f3ede0', stroke='#a59b88', stroke_width='.8', stroke_dasharray='2 1.5'))
    # the hat, upturned: the brim, the felt crown below it, its band and bow
    o.append('<ellipse cx="236" cy="268" rx="62" ry="5" fill="#000" opacity=".15"/>')
    o.append(path('M182 200L194 266h84l12-66z', 'url(#felt)'))
    o.append(path('M188 232h96', stroke=P['accent'], stroke_width='9'))
    o.append(path('M268 228l10 4-10 4z', '#8f2e1e'))
    o.append('<ellipse cx="236" cy="200" rx="78" ry="14" fill="#1e1d1b"/>')
    o.append('<ellipse cx="236" cy="199" rx="56" ry="8" fill="#3a3733"/>')
    o.append('<ellipse cx="236" cy="197" rx="76" ry="12" fill="none" stroke="#5a5650" stroke-width="1"/>')
    # the scissors, open: two blades, two rings
    o.append(path('M372 252L446 194l4 3-68 62zM384 258L454 216l2 4-66 42z', 'url(#steel)', stroke='#5f5d58', stroke_width='.8'))
    o.append(circle(386, 256, 2.2, '#5f5d58'))
    o.append(circle(366, 258, 11, 'none', stroke=P['accent'], stroke_width='5') + circle(388, 268, 10, 'none', stroke=P['accent'], stroke_width='5'))
    # the words, cut from the article, rising out of the hat, each slip with its shadow
    words = ['brain', 'chance', 'music', 'electronic', 'applauded', 'hour', 'machine', 'audience', 'IBM', 'notes']
    spots = [(236, 176, -3), (292, 150, 5), (198, 140, -6), (150, 112, 4), (300, 106, -4), (220, 86, 7), (160, 58, -5), (290, 42, 3), (356, 72, 8), (110, 160, -8)]
    for w, (x, y, a) in zip(words, spots):
        width = len(w) * 8.6 + 14
        o.append('<g transform="rotate(%d %s %s)">%s%s%s</g>' % (a, f(x), f(y), rect(x - width / 2 + 1.5, y - 10, width, 20, '#000', opacity='.1'), rect(x - width / 2, y - 12, width, 20, '#fffdf8', stroke='#a59b88', stroke_width='1'),
                                                                T.text(x, y + 3, w, 14, P['ink'], 'ibm-plex-mono', 400, 'middle')))
    save('hat', W, H, ''.join(o), D, T, title='An upturned hat with words rising out of it, a newspaper and scissors')

if __name__ == '__main__':
    import sys
    for w in (sys.argv[1:] or ['desktop', 'hero', 'plates', 'ball', 'hat']): globals()[w]()
