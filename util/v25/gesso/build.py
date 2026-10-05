#!/usr/bin/env python3
"""Builds the Gesso decks and writes them as a JS array literal."""
import json, sys

OUT = sys.argv[1]


def card(label, text, cont=' '):
    s = (str(label).rjust(5) if label != '' else '     ') + cont + text
    assert len(s) <= 72, (len(s), s)
    return s


def stmt(label, head, items, tail=''):
    """A statement HEAD followed by a comma list ITEMS, wrapped onto continuation cards."""
    cards = []
    cur = head
    first = True
    n = 0
    for i, it in enumerate(items):
        piece = it + (',' if i < len(items) - 1 else tail)
        if len(cur) + len(piece) > 66:
            cards.append(card(label if first else '', cur, ' ' if first else str(n)))
            first = False
            n += 1
            cur = ' ' + piece
        else:
            cur += piece
    cards.append(card(label if first else '', cur, ' ' if first else str(n)))
    return cards


def arr(name, n, start=1):
    return ['%s(%d)' % (name, k) for k in range(start, start + n)]


def C(*paras):
    """Comment cards: each argument is a paragraph, wrapped to column 72."""
    import textwrap
    out = []
    for para in paras:
        for l in textwrap.wrap(para, 66, break_on_hyphens=False):
            out.append('C     ' + l)
    return out


def L(*lines):
    out = []
    for l in lines:
        if isinstance(l, tuple):
            out.append(card(l[0], l[1]))
        elif l.startswith('C     '):
            assert len(l) <= 72, l
            out.append(l)
        else:
            out.append(card('', l))
    return out


decks = []

# ---------------------------------------------------------------- Morellet
lcg_state = [1961]


def rnd():
    lcg_state[0] = (lcg_state[0] * 16807) % 2147483647
    return lcg_state[0]


names = ['ARNAUD', 'AUBRY', 'BARBIER', 'BERNARD', 'BLANC', 'BONNET', 'BRUN',
         'CHEVALIER', 'CLEMENT', 'COLIN', 'DAVID', 'DUBOIS', 'DUPONT', 'DURAND',
         'FAURE', 'FOURNIER', 'GARNIER', 'GAUTIER', 'GIRARD', 'GUERIN', 'HENRY',
         'LAMBERT', 'LAURENT', 'LEFEBVRE', 'LEROY', 'MARTIN', 'MERCIER', 'MOREAU',
         'MOREL', 'PERRIN', 'PETIT', 'RICHARD', 'ROBERT', 'ROUSSEAU', 'ROUX',
         'VINCENT']
dirc = []
for nm in names:
    nums = []
    for k in range(10):
        nums.append('%06d' % (100000 + rnd() % 900000))
    c = nm.ljust(10)[:10] + ''.join(' ' + x for x in nums)
    assert len(c) == 80
    dirc.append(c)

m = []
m += C('RANDOM DISTRIBUTION OF SQUARES BY THE EVEN AND ODD DIGITS OF A TELEPHONE DIRECTORY, AFTER FRANCOIS MORELLET (1960)',
       'MORELLET LET THE NUMBERS OF A DIRECTORY, READ ONE DIGIT AT A TIME, CHOOSE THE COLOUR OF EACH SQUARE: AN EVEN DIGIT GAVE ONE COLOUR, AN ODD DIGIT THE OTHER. HERE EACH DIRECTORY CARD IS ONE ROW OF 60 SQUARES, READ FROM LEFT TO RIGHT. AN ASTERISK IS INK, A FULL STOP IS PAPER. THE PRINTOUT ENDS WITH A COUNT OF THE INK AND OF EVERY DIGIT READ.',
       'DATA CARDS: (10I1,I5) FOR EACH DIGIT FROM 0 TO 9, 1 TO INK IT OR 0 FOR PAPER, THEN HOW MANY DIRECTORY CARDS FOLLOW (1 TO 36); (10X,10(1X,6I1)) THE DIRECTORY, ONE CARD PER ROW: A NAME, THEN TEN SIX-DIGIT NUMBERS',
       'TRY 1000000000 TO INK ONLY THE ZEROS, ONE SQUARE IN TEN.')
m += L('DIMENSION KEY(10), ID(60), P(60), NK(10)')
m += stmt('', 'READ (5,10) ', arr('KEY', 10) + ['NROW'])
m += L((10, 'FORMAT (10I1,I5)'),
       'NPC = 0',
       'DO 12 K = 1, 10',
       'NK(K) = 0',
       'NPC = NPC + 10*KEY(K)',
       (12, 'CONTINUE'),
       'NPP = 100 - NPC',
       'WRITE (6,15) NPC, NPP',
       (15, "FORMAT (1H1,'RANDOM DISTRIBUTION OF SQUARES BY THE EVEN AND ',"))
m.append(card('', " 'ODD DIGITS OF A TELEPHONE DIRECTORY'/1H ,I3,' PER CENT INK,',", '1'))
m.append(card('', " I4,' PER CENT PAPER'/1H )", '2'))
m += L('NINK = 0',
       'DO 50 IR = 1, NROW')
m += stmt('', 'READ (5,20) ', arr('ID', 60))
m += L((20, 'FORMAT (10X,10(1X,6I1))'),
       'DO 40 IC = 1, 60',
       'K = ID(IC) + 1',
       'NK(K) = NK(K) + 1',
       'P(IC) = FLOAT(KEY(K))',
       'NINK = NINK + KEY(K)',
       (40, 'CONTINUE'))
m += stmt('', 'WRITE (6,45) ', arr('P', 60))
m += L((45, 'FORMAT (1X,60F1.0)'),
       (50, 'CONTINUE'),
       'N = 60*NROW',
       'WRITE (6,60) N, NINK',
       (60, "FORMAT (1H0,I5,' SQUARES,',I5,' OF THEM INKED')"))
m += stmt('', 'WRITE (6,65) ', arr('NK', 10))
m += L((65, "FORMAT (1H ,'DIGITS 0 TO 9 READ',10I5)"),
       'STOP',
       'END')
m += ['0101010101' + '%5d' % 36]
m += dirc
decks.append({'id': 'random-distribution', 'name': 'Random distribution (after Morellet)', 'cards': m})

# ---------------------------------------------------------------- Kelly
colours = ['LEMON YELLOW', 'CHROME YELLOW', 'YELLOW ORANGE', 'ORANGE', 'VERMILION',
           'SCARLET', 'CRIMSON', 'MAGENTA', 'PURPLE', 'VIOLET', 'ULTRAMARINE',
           'COBALT BLUE', 'CERULEAN', 'TURQUOISE', 'BLUE GREEN', 'EMERALD',
           'GRASS GREEN', 'YELLOW GREEN']
k = []
k += C('SPECTRUM COLOURS ARRANGED BY CHANCE, AFTER ELLSWORTH KELLY (PARIS, 1951)',
       'KELLY NUMBERED HIS COLOURS ONE THROUGH EIGHTEEN AND LET NUMBERS DRAWN BY CHANCE DECIDE THE COLOUR OF EACH SQUARE OF A GRID. HERE, FOR EVERY SQUARE, A SLIP IS DRAWN FROM THE HAT AND PUT BACK. THE GRID IS PRINTED AS A CHART OF COLOUR NUMBERS, 24 SQUARES WIDE, WITH A KEY THAT COUNTS THE SQUARES OF EACH COLOUR. THE COLOURS RUN IN SPECTRUM ORDER, FROM 01 LEMON YELLOW ROUND TO 18 YELLOW GREEN. EACH ROW IS ALSO PUNCHED (24I3), A CARTOON TO PASTE THE SQUARES BY.',
       'DATA CARD (3I5): SEED (1 TO 30268), ROWS (1 TO 40), COLOURS IN THE HAT (1 TO 18, TAKEN FROM THE START OF THE SPECTRUM)',
       'TRY 3 COLOURS, OR 6, AND WATCH THE COUNTS EVEN OUT.')
k += L('DIMENSION IG(24), IT(24), IU(24), NC(18)',
       'READ (5,10) IX, NROW, NCOL',
       (10, 'FORMAT (3I5)'),
       'DO 12 K = 1, 18',
       'NC(K) = 0',
       (12, 'CONTINUE'),
       'WRITE (6,15) NROW, NCOL',
       (15, "FORMAT (1H1,'SPECTRUM COLOURS ARRANGED BY CHANCE'/1H ,I3,"),
       )
k.append(card('', " ' ROWS OF 24 SQUARES,',I3,' COLOURS IN THE HAT'/1H )", '1'))
k += L('DO 50 IR = 1, NROW',
       'DO 40 IC = 1, 24',
       'C     DRAW A SLIP, READ ITS NUMBER, PUT IT BACK',
       'IX = MOD(171*IX, 30269)',
       'L = MOD(IX, NCOL) + 1',
       'IG(IC) = L',
       'IT(IC) = L/10',
       'IU(IC) = MOD(L, 10)',
       'NC(L) = NC(L) + 1',
       (40, 'CONTINUE'))
# fix the comment card that L() turned into a statement
k = [c if 'DRAW A SLIP' not in c else 'C     DRAW A SLIP, READ ITS NUMBER, PUT IT BACK' for c in k]
items = []
for j in range(1, 25):
    items += ['IT(%d)' % j, 'IU(%d)' % j]
k += stmt('', 'WRITE (6,45) ', items)
k += stmt('', 'PUNCH 46, ', arr('IG', 24))
k += L((45, 'FORMAT (1X,24(1X,2I1))'),
       (46, 'FORMAT (24I3)'),
       (50, 'CONTINUE'),
       'WRITE (6,55)',
       (55, "FORMAT (1H0,'KEY',8X,'SQUARES')"),
       'DO 90 L = 1, NCOL',
       'N = NC(L)',
       'LT = L/10',
       'LU = MOD(L, 10)')
k += stmt('', 'GO TO (', ['%d' % (100 + j) for j in range(1, 19)], '), L')
for j in range(1, 19):
    k += L((100 + j, 'WRITE (6,%d) LT, LU, N' % (200 + j)))
    if j < 18:
        k += L('GO TO 90')
k += L((90, 'CONTINUE'),
       'STOP')
for j, nm in enumerate(colours, 1):
    k += L((200 + j, "FORMAT (1X,2I1,2X,'%s',I%d)" % (nm, 20 - len(nm))))
k += L('END')
k += ['%5d%5d%5d' % (1951, 24, 18)]
# I2.0 is not a FORMAT descriptor here: print the number as two digits instead
decks.append({'id': 'spectrum-colors-by-chance', 'name': 'Spectrum colors arranged by chance (after Kelly)', 'cards': k})

# ---------------------------------------------------------------- Kenneth Martin
c = []
c += C('CHANCE AND ORDER, AFTER KENNETH MARTIN (1969 ONWARDS)',
       'THE CROSSINGS OF A GRID OF SQUARES ARE NUMBERED, THE NUMBERS ARE WRITTEN ON CARDS, AND THE CARDS ARE DRAWN AT RANDOM. EACH PAIR OF NUMBERS DRAWN IS JOINED BY A LINE. THE LINES ARE DRAWN AS SETS OF PARALLELS: ONE STROKE FOR THE FIRST LINE, TWO FOR THE SECOND, THREE FOR THE THIRD, ALWAYS ON THE SAME SIDE OF THE LINE. THE GRID HAS 4 BY 4 SQUARES, SO 25 CROSSINGS, NUMBERED ACROSS FROM THE TOP LEFT: 1 TO 5 ALONG THE TOP, 21 TO 25 ALONG THE BOTTOM. THE DRAWING IS 64 CHARACTERS BY 32 LINES; AN ASTERISK IS INK.',
       'DATA CARD (2I5): SEED (1 TO 30268), LINES TO DRAW (1 TO 12)',
       'TRY 3 LINES FOR A SPARE DRAWING, OR 9 FOR A CROWDED ONE.')
c += L('DIMENSION IC(25), IA(64,32), P(64)',
       'READ (5,10) IX, NL',
       (10, 'FORMAT (2I5)'),
       'WRITE (6,12)',
       (12, "FORMAT (1H1,'CHANCE AND ORDER'/1H0,'LINE  FROM    TO  STROKES')"),
       'C     WRITE THE NUMBERS ON CARDS AND SHUFFLE THEM',
       'DO 14 K = 1, 25',
       'IC(K) = K',
       (14, 'CONTINUE'),
       'DO 16 L = 1, 24',
       'K = 26 - L',
       'IX = MOD(171*IX, 30269)',
       'J = MOD(IX, K) + 1',
       'IT = IC(K)',
       'IC(K) = IC(J)',
       'IC(J) = IT',
       (16, 'CONTINUE'),
       'DO 18 IR = 1, 32',
       'DO 18 ICOL = 1, 64',
       'IA(ICOL,IR) = 0',
       (18, 'CONTINUE'),
       'C     CROSSING N LIES AT COLUMN 8+12*I AND LINE 4+6*J',
       'DO 60 L = 1, NL',
       'NA = IC(2*L-1)',
       'NB = IC(2*L)',
       'WRITE (6,20) L, NA, NB, L',
       (20, 'FORMAT (1X,I4,I6,I6,I9)'),
       'XA = FLOAT(8 + 12*MOD(NA-1,5))',
       'YA = FLOAT(4 + 6*((NA-1)/5))',
       'XB = FLOAT(8 + 12*MOD(NB-1,5))',
       'YB = FLOAT(4 + 6*((NB-1)/5))',
       'C     A LINE ON THE PAGE IS 5/3 AS TALL AS A CHARACTER IS WIDE',
       'DX = XB - XA',
       'DY = (YB - YA)*5.0/3.0',
       'D = SQRT(DX*DX + DY*DY)',
       'C     THE PARALLELS STAND 2 LINES OR 3 1/3 CHARACTERS APART',
       'OX = -10.0/3.0*DY/D',
       'OY = 2.0*DX/D',
       'NS = INT(D) + 1',
       'DO 50 IS = 1, L',
       'S = FLOAT(IS - 1)',
       'DO 40 IP = 0, NS',
       'T = FLOAT(IP)/FLOAT(NS)',
       'IXP = INT(XA + T*(XB-XA) + S*OX + 0.5)',
       'IYP = INT(YA + T*(YB-YA) + S*OY + 0.5)',
       'IF (IXP .LT. 1 .OR. IXP .GT. 64) GO TO 40',
       'IF (IYP .LT. 1 .OR. IYP .GT. 32) GO TO 40',
       'IA(IXP,IYP) = 1',
       (40, 'CONTINUE'),
       (50, 'CONTINUE'),
       (60, 'CONTINUE'),
       'WRITE (6,65)',
       (65, 'FORMAT (1H )'),
       'DO 80 IR = 1, 32',
       'DO 70 ICOL = 1, 64',
       'P(ICOL) = FLOAT(IA(ICOL,IR))',
       (70, 'CONTINUE'))
c += stmt('', 'WRITE (6,75) ', arr('P', 64))
c += L((75, 'FORMAT (1X,64F1.0)'),
       (80, 'CONTINUE'),
       'STOP',
       'END',
       )
c = [x if not x.startswith('      C     ') else x[6:] for x in c]
c += ['%5d%5d' % (1969, 5)]
decks.append({'id': 'chance-and-order', 'name': 'Chance and order (after Kenneth Martin)', 'cards': c})

# ---------------------------------------------------------------- LeWitt
w = []
w += C('WALL DRAWING 11, AFTER SOL LEWITT (1969), CARRIED OUT BY THE MACHINE',
       'THE INSTRUCTION READS: A WALL DIVIDED HORIZONTALLY AND VERTICALLY INTO FOUR EQUAL PARTS. WITHIN EACH PART, THREE OF THE FOUR KINDS OF LINES ARE SUPERIMPOSED. THE FOUR KINDS ARE 1 VERTICAL, 2 HORIZONTAL, 3 DIAGONAL RIGHT, 4 DIAGONAL LEFT. THE WALL IS 64 CHARACTERS BY 32 LINES AND AN ASTERISK IS PENCIL. A LINE ON THE PAGE IS 5/3 AS TALL AS A CHARACTER IS WIDE, SO SPACING IS MEASURED IN CHARACTER WIDTHS BOTH WAYS AND THE DIAGONALS COME OUT AT 45 DEGREES.',
       'DATA CARDS: (I5) SPACING OF THE LINES IN CHARACTER WIDTHS (3 TO 9); (4(4I1,1X)) FOR EACH PART IN TURN (TOP LEFT, TOP RIGHT, BOTTOM LEFT, BOTTOM RIGHT), 1 OR 0 FOR EACH OF THE FOUR KINDS',
       'TRY ALL FOUR KINDS IN ONE PART, OR ONLY ONE, OR A SPACING OF 4.')
w += L('DIMENSION KD(4,4), P(64)',
       'READ (5,10) IS',
       (10, 'FORMAT (I5)'))
w += stmt('', 'READ (5,11) ', ['KD(%d,%d)' % (kk, pp) for pp in range(1, 5) for kk in range(1, 5)])
w += L((11, 'FORMAT (4(4I1,1X))'),
       'S = FLOAT(IS)',
       'WRITE (6,12)',
       (12, "FORMAT (1H1,'WALL DRAWING 11'/1H0,'A WALL DIVIDED HORIZONTALLY',"))
w.append(card('', " ' AND VERTICALLY INTO FOUR EQUAL PARTS.'/1H ,'WITHIN EACH PART,',", '1'))
w.append(card('', " ' THREE OF THE FOUR KINDS OF LINES ARE SUPERIMPOSED.'/1H )", '2'))
w += L('DO 60 IR = 1, 32',
       'C     WHICH PART: THE TOP TWO FOR THE FIRST 16 LINES',
       'IPT = 1',
       'IF (IR .GT. 16) IPT = 3',
       'Y = (FLOAT(IR) - 0.5)*5.0/3.0',
       'DO 50 IC = 1, 64',
       'IP = IPT',
       'IF (IC .GT. 32) IP = IPT + 1',
       'X = FLOAT(IC - 1)',
       'P(IC) = 0.0',
       'C     1 VERTICAL: EVERY S COLUMNS',
       'IF (KD(1,IP) .EQ. 1 .AND. MOD(IC-1,IS) .EQ. 0) P(IC) = 1.0',
       'C     2 HORIZONTAL: A LINE AT A MULTIPLE OF S CROSSES THE ROW',
       'YT = (FLOAT(IR) - 1.0)*5.0/3.0',
       'IF (KD(2,IP) .EQ. 1 .AND. AMOD(YT,S) .LT. 5.0/3.0) P(IC) = 1.0',
       'C     3 DIAGONAL RIGHT, RISING TO THE RIGHT: X + Y A MULTIPLE OF S',
       'IF (KD(3,IP) .EQ. 1 .AND. AMOD(X+Y,S) .LT. 1.0) P(IC) = 1.0',
       'C     4 DIAGONAL LEFT, FALLING TO THE RIGHT: X - Y A MULTIPLE OF S',
       'IF (KD(4,IP) .EQ. 1 .AND. AMOD(X-Y+100.0*S,S) .LT. 1.0) P(IC)=1.0',
       (50, 'CONTINUE'))
w += stmt('', 'WRITE (6,55) ', arr('P', 64))
w += L((55, 'FORMAT (1X,64F1.0)'),
       (60, 'CONTINUE'),
       'WRITE (6,62)',
       (62, "FORMAT (1H0,13X,'VERTICAL  HORIZONTAL  DIAG RIGHT   DIAG LEFT')"),
       'NOK = 0',
       'DO 70 IP = 1, 4',
       'N = KD(1,IP) + KD(2,IP) + KD(3,IP) + KD(4,IP)',
       'IF (N .EQ. 3) NOK = NOK + 1',
       'GO TO (63,64,65,66), IP',
       (63, 'WRITE (6,67) KD(1,IP),KD(2,IP),KD(3,IP),KD(4,IP)'),
       'GO TO 70',
       (64, 'WRITE (6,68) KD(1,IP),KD(2,IP),KD(3,IP),KD(4,IP)'),
       'GO TO 70',
       (65, 'WRITE (6,69) KD(1,IP),KD(2,IP),KD(3,IP),KD(4,IP)'),
       'GO TO 70',
       (66, 'WRITE (6,71) KD(1,IP),KD(2,IP),KD(3,IP),KD(4,IP)'),
       (70, 'CONTINUE'),
       'IF (NOK .EQ. 4) WRITE (6,72)',
       'IF (NOK .LT. 4) WRITE (6,73)',
       'STOP',
       (67, "FORMAT (1X,'TOP LEFT    ',4I12)"),
       (68, "FORMAT (1X,'TOP RIGHT   ',4I12)"),
       (69, "FORMAT (1X,'BOTTOM LEFT ',4I12)"),
       (71, "FORMAT (1X,'BOTTOM RIGHT',4I12)"),
       (72, "FORMAT (1H0,'THE INSTRUCTION HAS BEEN CARRIED OUT.')"),
       (73, "FORMAT (1H0,'THIS IS NOT WALL DRAWING 11. IT MAY BE ANOTHER.')"),
       'END')
w = [x if not x.startswith('      C     ') else x[6:] for x in w]
w += ['    6', '0111 1011 1101 1110']
decks.append({'id': 'wall-drawing-11', 'name': 'Wall drawing 11 (after LeWitt)', 'cards': w})

# ---------------------------------------------------------------- Molnar
d = []
d += C('(DES)ORDRES, AFTER VERA MOLNAR (1974)',
       'A GRID OF 4 BY 4 CELLS, EACH HOLDING SQUARES NESTED ONE INSIDE ANOTHER. EVERY CORNER OF EVERY SQUARE IS MOVED BY CHANCE, AND THE DISORDER GROWS ACROSS THE SHEET: THE TOP LEFT CELL IS IN PERFECT ORDER, AND THE BOTTOM RIGHT CELL MAY MOVE ITS CORNERS BY THE FULL AMOUNT ON THE DATA CARD. THE SHEET IS 72 CHARACTERS BY 40 LINES, EACH CELL 18 BY 10; AN ASTERISK IS THE PEN.',
       'DATA CARD (3I5): SEED (1 TO 30268), LARGEST MOVE OF A CORNER IN CHARACTER WIDTHS (0 TO 5), SQUARES IN EACH CELL (1 TO 3)',
       'TRY A LARGEST MOVE OF 0 FOR PERFECT ORDER, OR 5 FOR DISORDER.')
d += L('DIMENSION IA(72,40), P(72), CX(4), CY(4), SX(4), SY(4)',
       'READ (5,10) IX, MOVE, NSQ',
       (10, 'FORMAT (3I5)'),
       'WRITE (6,12) MOVE',
       (12, "FORMAT (1H1,'(DES)ORDRES'/1H ,'ORDER AT THE TOP LEFT, CORNERS',"))
d.append(card('', " ' MOVED UP TO',I2,' CHARACTERS AT THE BOTTOM RIGHT'/1H )", '1'))
d += L('C     THE CORNERS, CLOCKWISE FROM THE TOP LEFT',
       'SX(1) = -1.0',
       'SY(1) = -1.0',
       'SX(2) = 1.0',
       'SY(2) = -1.0',
       'SX(3) = 1.0',
       'SY(3) = 1.0',
       'SX(4) = -1.0',
       'SY(4) = 1.0',
       'DO 14 IR = 1, 40',
       'DO 14 IC = 1, 72',
       'IA(IC,IR) = 0',
       (14, 'CONTINUE'),
       'DO 80 JC = 1, 4',
       'DO 80 IC4 = 1, 4',
       'C     THE DISORDER OF THIS CELL, FROM 0 TO MOVE',
       'DM = FLOAT(MOVE)*FLOAT(IC4 + JC - 2)/6.0',
       'X0 = FLOAT(18*IC4 - 9) + 0.5',
       'Y0 = FLOAT(10*JC - 5) + 0.5',
       'DO 70 K = 1, NSQ',
       'C     HALF THE SIDE OF THE SQUARE, IN CHARACTER WIDTHS',
       'H = 7.5 - 2.5*FLOAT(K - 1)',
       'DO 20 J = 1, 4',
       'IX = MOD(171*IX, 30269)',
       'U = FLOAT(IX)/30269.0',
       'IX = MOD(171*IX, 30269)',
       'V = FLOAT(IX)/30269.0',
       'CX(J) = X0 + SX(J)*H + DM*(2.0*U - 1.0)',
       'C     A LINE ON THE PAGE IS 5/3 AS TALL AS A CHARACTER IS WIDE',
       'CY(J) = Y0 + (SY(J)*H + DM*(2.0*V - 1.0))*3.0/5.0',
       (20, 'CONTINUE'),
       'C     DRAW THE FOUR SIDES',
       'DO 60 J = 1, 4',
       'J2 = MOD(J,4) + 1',
       'DX = CX(J2) - CX(J)',
       'DY = CY(J2) - CY(J)',
       'NS = INT(AMAX1(ABS(DX),ABS(DY))) + 1',
       'DO 50 IP = 0, NS',
       'T = FLOAT(IP)/FLOAT(NS)',
       'IXP = INT(CX(J) + T*DX)',
       'IYP = INT(CY(J) + T*DY)',
       'IF (IXP .LT. 1 .OR. IXP .GT. 72) GO TO 50',
       'IF (IYP .LT. 1 .OR. IYP .GT. 40) GO TO 50',
       'IA(IXP,IYP) = 1',
       (50, 'CONTINUE'),
       (60, 'CONTINUE'),
       (70, 'CONTINUE'),
       (80, 'CONTINUE'),
       'DO 95 IR = 1, 40',
       'DO 90 IC = 1, 72',
       'P(IC) = FLOAT(IA(IC,IR))',
       (90, 'CONTINUE'))
d += stmt('', 'WRITE (6,92) ', arr('P', 72))
d += L((92, 'FORMAT (1X,72F1.0)'),
       (95, 'CONTINUE'),
       'STOP',
       'END')
d = [x if not x.startswith('      C     ') else x[6:] for x in d]
d += ['%5d%5d%5d' % (1974, 3, 3)]
decks.append({'id': 'order-and-disorder', 'name': 'Order and disorder (after Molnár)', 'cards': d})

# ---------------------------------------------------------------- write
for dk in decks:
    for cc in dk['cards']:
        assert len(cc) <= 80, cc
lines = ['[']
for i, dk in enumerate(decks):
    lines.append('  { id: %s, name: %s, cards: [' % (json.dumps(dk['id']), json.dumps(dk['name'], ensure_ascii=False)))
    for j, cc in enumerate(dk['cards']):
        lines.append('    ' + json.dumps(cc) + (',' if j < len(dk['cards']) - 1 else ''))
    lines.append('  ] }' + (',' if i < len(decks) - 1 else ''))
lines.append(']')
open(OUT, 'w').write('\n'.join(lines) + '\n')
print('wrote', len(decks), 'decks')
