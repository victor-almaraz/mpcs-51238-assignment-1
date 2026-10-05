#!/usr/bin/env python3
# Builds the Event decks as card images and writes decks-event.js.
import json, sys

OUT = sys.argv[1]

def C(t):
    s = "C     " + t
    assert len(s) <= 72, s
    return s

def S(stmt, label=None):
    """A statement, split over continuation cards at 66 columns, breaking at commas or blanks."""
    lab = ("%5d" % label) if label is not None else "     "
    cards, first, n = [], True, 0
    rest = stmt
    while rest:
        if len(rest) <= 66:
            chunk, rest = rest, ""
        else:
            cut = rest.rfind("),", 0, 65) + 2
            if cut < 30:
                cut = max(rest.rfind(",", 0, 66) + 1, rest.rfind(" ", 0, 66) + 1)
            # never break inside a quoted literal
            q = rest[:cut].count("'")
            while q % 2 == 1:
                cut = rest.rfind(",", 0, cut - 1) + 1
                q = rest[:cut].count("'")
            assert cut > 0, stmt
            chunk, rest = rest[:cut], rest[cut:]
        if first:
            cards.append(lab + " " + chunk)
            first = False
        else:
            n += 1
            cards.append("     " + "123456789ABCDEFGHIJ"[n - 1] + chunk)
    return cards

def D(*fields):
    return "".join("%5d" % f for f in fields)

def deck(id_, name, parts):
    cards = []
    for p in parts:
        if isinstance(p, list): cards.extend(p)
        else: cards.append(p)
    for c in cards:
        assert len(c) <= 80, c
    return {"id": id_, "name": name, "cards": cards}

DECKS = []
RND = "IX = MOD(171*IX, 30269)"

# ---------------------------------------------------------------- 1
mats = ["SAND", "DUST", "LEAVES", "PAPER", "TIN", "ROOTS", "BRICK", "STONE",
        "DISCARDED CLOTHING", "GLASS", "STEEL", "PLASTIC", "MUD", "BROKEN DISHES"]
places = ["IN A GREEN, MOSSY TERRAIN", "IN AN OVERPOPULATED AREA", "BY THE SEA",
          "BY AN ABANDONED LAKE", "IN A DESERTED FACTORY", "IN DENSE WOODS", "IN JAPAN",
          "AMONG SMALL HILLS", "AMONG HIGH MOUNTAINS", "ON AN ISLAND", "ON OPEN GROUND",
          "IN A COLD, WINDY CLIMATE", "IN A PLACE WITH BOTH HEAVY RAIN AND BRIGHT SUN",
          "IN A DESERTED AIRPORT", "IN A METROPOLIS", "UNDERWATER"]
lights = ["CANDLES", "ALL AVAILABLE LIGHTING", "ELECTRICITY", "NATURAL LIGHT"]
inhab = ["PEOPLE WHO SLEEP VERY LITTLE", "VEGETARIANS", "HORSES AND BIRDS",
         "CHILDREN AND OLD PEOPLE", "VARIOUS BIRDS AND FISH", "LOVERS",
         "PEOPLE WHO ENJOY EATING TOGETHER", "PEOPLE WHO EAT A GREAT DEAL",
         "COLLECTORS OF ALL TYPES", "FRIENDS AND ENEMIES",
         "PEOPLE WHO SLEEP ALMOST ALL THE TIME", "VERY TALL PEOPLE",
         "FISHERMEN AND FAMILIES", "PEOPLE WHO LOVE TO READ"]

def listblock(items, base, cc, prefix, comment):
    n = len(items)
    out = [C(comment), S(RND), S("I = MOD(IX, %d) + 1" % n)]
    for k in range(n):
        out += S("IF (I .EQ. %d) WRITE (6,%d)" % (k + 1, base + k + 1))
    return out

def listformats(items, base, cc, prefix):
    out = []
    for k, it in enumerate(items):
        out += S("FORMAT (%s'%s%s')" % (cc, prefix, it), base + k + 1)
    return out

hod = [
    C("THE HOUSE OF DUST, AFTER ALISON KNOWLES AND JAMES TENNEY (1967)"),
    C("KNOWLES WROTE FOUR LISTS: WHAT A HOUSE IS MADE OF, WHERE IT"),
    C("STANDS, HOW IT IS LIT AND WHO LIVES IN IT. TENNEY HELPED HER"),
    C("PROGRAM A COMPUTER IN FORTRAN TO DRAW ONE LINE FROM EACH LIST,"),
    C("BY CHANCE, FOR EVERY STANZA. THE LISTS HERE ARE HERS, SHORTENED:"),
    C("14 MATERIALS, 16 PLACES, 4 LIGHTS AND 14 KINDS OF INHABITANT,"),
    C("WHICH MAKE 12544 DIFFERENT HOUSES."),
    C("DATA CARD (2I5): SEED (1 TO 30268), NUMBER OF STANZAS"),
    C("A NEW DATA CARD IS PUNCHED AT THE END, HOLDING THE SEED THE RUN"),
    C("HAS REACHED: PUT IT AFTER END IN PLACE OF THE OLD ONE AND THE"),
    C("NEXT RUN PRINTS THE STANZAS THAT FOLLOW."),
    C("TRY THE SEED 10763: ITS FIRST HOUSE IS THE ONE BUILT AT CALARTS."),
    S("READ (5,10) IX, N"),
    S("FORMAT (2I5)", 10),
    S("WRITE (6,15)"),
    S("FORMAT (1H1,'A HOUSE OF DUST')", 15),
    S("DO 90 K = 1, N"),
]
hod += listblock(mats, 100, None, None, "WHAT IT IS MADE OF")
hod += listblock(places, 200, None, None, "WHERE IT STANDS")
hod += listblock(lights, 300, None, None, "HOW IT IS LIT")
hod += listblock(inhab, 400, None, None, "WHO LIVES IN IT")
hod += [
    S("CONTINUE", 90),
    S("PUNCH 95, IX, N"),
    S("FORMAT (2I5,5X,'THE NEXT STANZAS OF A HOUSE OF DUST')", 95),
    S("STOP"),
]
hod += listformats(mats, 100, "1H0,", "A HOUSE OF ")
hod += listformats(places, 200, "1X,", "     ")
hod += listformats(lights, 300, "1X,", "     USING ")
hod += listformats(inhab, 400, "1X,", "     INHABITED BY ")
hod += ["      END", D(1967, 8)]
DECKS.append(deck("the-house-of-dust", "The house of dust (after Knowles and Tenney)", hod))

# ---------------------------------------------------------------- 2
titles = ["WATER EVENT", "LAMP EVENT", "CHAIR EVENT", "DOOR EVENT", "WINDOW EVENT",
          "CLOCK EVENT", "PAPER EVENT", "CARD EVENT", "PRINTER EVENT", "TAPE EVENT",
          "TABLE EVENT", "SHOE EVENT"]
items = ["ON.", "OFF.", "OPEN.", "SHUT.", "FILL.", "EMPTY.", "DRIPPING.", "ONCE.",
         "AGAIN.", "COUNT THEM.", "LISTEN.", "TURN IT OVER.", "IN THE DARK.", "SLOWLY.",
         "LEAVE THE ROOM.", "FOLD.", "PUNCH A HOLE.", "WAIT.", "EXIT.", "STOP."]
NT, NI = len(titles), len(items)
ev = [
    C("EVENT CARDS: A DECK OF EVENT SCORES DRAWN BY CHANCE"),
    C("AFTER GEORGE BRECHT, WHO FROM 1959 WROTE EVENTS AS A FEW WORDS"),
    C("ON A SMALL CARD. EACH CARD HERE HAS A TITLE, AN OBJECT FROM THE"),
    C("ROOM, AND ONE TO THREE LINES DRAWN FROM A LIST OF TWENTY, NEVER"),
    C("THE SAME LINE TWICE ON A CARD. THE CARDS ARE PRINTED IN FRAMES,"),
    C("AND EACH IS ALSO PUNCHED, TITLE AND LINES, ONE CARD TO A LINE,"),
    C("SO THE STACKER HOLDS THE DECK READY TO HAND OUT AND PERFORM."),
    C("DATA CARD (2I5): SEED (1 TO 30268), NUMBER OF CARDS (1 TO 50)"),
    S("DIMENSION IL(3)"),
    S("READ (5,10) IX, N"),
    S("FORMAT (2I5)", 10),
    S("WRITE (6,15)"),
    S("FORMAT (1H1,'EVENT CARDS, DRAWN BY CHANCE')", 15),
    S("DO 90 K = 1, N"),
    C("THE TITLE"),
    S(RND),
    S("IT = MOD(IX, %d) + 1" % NT),
    C("HOW MANY LINES, AND WHICH: A LINE ALREADY ON THE CARD IS DRAWN"),
    C("AGAIN"),
    S(RND),
    S("NL = MOD(IX, 3) + 1"),
    S("DO 30 L = 1, NL"),
    S(RND, 20),
    S("J = MOD(IX, %d) + 1" % NI),
    S("IF (L .EQ. 1) GO TO 30"),
    S("LL = L - 1"),
    S("DO 25 M = 1, LL"),
    S("IF (IL(M) .EQ. J) GO TO 20"),
    S("CONTINUE", 25),
    S("IL(L) = J", 30),
    C("PRINT THE CARD IN ITS FRAME, AND PUNCH IT"),
    S("WRITE (6,40)"),
    S("WRITE (6,41)"),
]
for k in range(NT):
    ev += S("IF (IT .EQ. %d) WRITE (6,%d)" % (k + 1, 101 + k))
for k in range(NT):
    ev += S("IF (IT .EQ. %d) PUNCH %d" % (k + 1, 101 + k))
ev += [
    S("WRITE (6,42)"),
    S("WRITE (6,41)"),
    S("DO 60 L = 1, NL"),
    S("J = IL(L)"),
]
for k in range(NI):
    ev += S("IF (J .EQ. %d) WRITE (6,%d)" % (k + 1, 201 + k))
for k in range(NI):
    ev += S("IF (J .EQ. %d) PUNCH %d" % (k + 1, 201 + k))
ev += [
    S("WRITE (6,42)"),
    S("CONTINUE", 60),
    S("WRITE (6,41)"),
    S("WRITE (6,43) K"),
    S("WRITE (6,42)"),
    S("WRITE (6,44)"),
    S("CONTINUE", 90),
    S("WRITE (6,45) N"),
    S("STOP"),
    S("FORMAT (1H0,'+------------------------------------+')", 40),
    S("FORMAT (1X,'|',36X,'|')", 41),
    S("FORMAT (1H+,'|',36X,'|')", 42),
    S("FORMAT (1X,28X,'NO.',I4)", 43),
    S("FORMAT (1X,'+------------------------------------+')", 44),
    S("FORMAT (1H0,I3,' CARDS PUNCHED. PERFORM ANY OF THEM.')", 45),
]
for k, t in enumerate(titles):
    ev += S("FORMAT (1X,'   %s')" % t, 101 + k)
for k, t in enumerate(items):
    ev += S("FORMAT (1X,'        . %s')" % t, 201 + k)
ev += ["      END", D(1959, 6)]
DECKS.append(deck("event-cards", "Event cards (a deck by chance, after George Brecht)", ev))

# ---------------------------------------------------------------- 3
held = [
    C("TO BE HELD FOR A LONG TIME, AFTER LA MONTE YOUNG"),
    C("THE WHOLE SCORE OF YOUNG'S COMPOSITION 1960 #7 IS A B AND THE"),
    C("F SHARP ABOVE IT, AND THE WORDS TO BE HELD FOR A LONG TIME."),
    C("FIRST THE DECK WORKS OUT THE INTERVAL: THE TWO FREQUENCIES (A"),
    C("ABOVE MIDDLE C IS 440 HZ), ITS SIZE IN CENTS, THE NEAREST SIMPLE"),
    C("RATIO, AND THE TWO HARMONICS THAT NEARLY MEET AND BEAT. THEN EACH"),
    C("PLAYER HOLDS A NOTE IN BOWS OF 3 TO 9 SECONDS, EACH BOW A LITTLE"),
    C("LOUDER OR SOFTER BY CHANCE, SO THE SOUND NEVER STOPS. EACH BOW IS"),
    C("PUNCHED AS A TAPE CARD (4I5): TIME IN PULSES, NOTE (MIDI NUMBER,"),
    C("60 IS MIDDLE C), LENGTH IN PULSES, LOUDNESS 1 TO 9. AT 120 BEATS"),
    C("A MINUTE A PULSE IS AN EIGHTH OF A SECOND."),
    C("DATA CARD 1 (3I5): SEED, LENGTH IN PULSES (72 TO 9999), PLAYERS"),
    C("   (2 TO 6). THEN ONE CARD (I5) PER PLAYER: THE NOTE HE OR SHE"),
    C("   HOLDS. THE FIRST TWO PLAYERS' NOTES ARE THE INTERVAL."),
    C("THE CHART: ONE ROW PER PLAYER, 72 COLUMNS FOR THE WHOLE LENGTH;"),
    C("A DIGIT IS THE LOUDNESS OF THE BOW SOUNDING, AN ASTERISK BELOW"),
    C("MARKS A CHANGE OF BOW. COLUMNS PAST THE END SHOW 0; A LENGTH OF"),
    C("72 TIMES A WHOLE NUMBER FILLS THE ROW."),
    S("DIMENSION NOTE(6), IC(6,72), B(72), IB(72)"),
    S("REAL B"),
    S("READ (5,10) IX, LEN, NP"),
    S("FORMAT (3I5)", 10),
    S("DO 12 P1 = 1, 1"),  # placeholder removed below
]
held = held[:-1]
held += [
    S("DO 12 K = 1, NP"),
    S("READ (5,11) NOTE(K)"),
    S("CONTINUE", 12),
    S("FORMAT (I5)", 11),
    S("WRITE (6,15)"),
    S("FORMAT (1H1,'TO BE HELD FOR A LONG TIME'/1H0,'  NOTE    FREQUENCY')", 15),
    S("NL = MIN0(NOTE(1), NOTE(2))"),
    S("NH = MAX0(NOTE(1), NOTE(2))"),
    S("FL = 440.0*2.0**(FLOAT(NL-69)/12.0)"),
    S("FH = 440.0*2.0**(FLOAT(NH-69)/12.0)"),
    S("WRITE (6,16) NL, FL"),
    S("WRITE (6,16) NH, FH"),
    S("FORMAT (1X,I6,F11.2,' HZ')", 16),
    S("CENTS = 1200.0*ALOG(FH/FL)/ALOG(2.0)"),
    C("THE TWO HARMONICS, ONE OF EACH NOTE, UP TO THE EIGHTH, THAT LIE"),
    C("CLOSEST TOGETHER"),
    S("BEAT = 99999.0"),
    S("DO 20 I = 1, 8"),
    S("DO 20 J = 1, 8"),
    S("D = ABS(FLOAT(I)*FL - FLOAT(J)*FH)"),
    S("IF (D .GE. BEAT) GO TO 20"),
    S("BEAT = D"),
    S("IH = I"),
    S("JH = J"),
    S("CONTINUE", 20),
    S("PURE = 1200.0*ALOG(FLOAT(IH)/FLOAT(JH))/ALOG(2.0)"),
    S("HL = FLOAT(IH)*FL"),
    S("HH = FLOAT(JH)*FH"),
    S("WRITE (6,25) CENTS, IH, JH, PURE"),
    S("FORMAT (1H0,'THE INTERVAL IS',F8.2,' CENTS. ITS NEAREST SIMPLE RATIO "
      "IS',I2,':',I1,', WHICH WOULD BE',F8.2,' CENTS.')", 25),
    S("WRITE (6,26) IH, HL, JH, HH, BEAT"),
    S("FORMAT (1X,'HARMONIC',I2,' OF THE LOW NOTE IS',F8.2,' HZ AND HARMONIC',"
      "I2,' OF THE HIGH NOTE IS',F8.2,' HZ:'/1X,'THEY BEAT',F6.2,' TIMES A SECOND.')", 26),
    C("THE BOWS"),
    S("IW = (LEN + 71)/72"),
    S("NB = 0"),
    S("WRITE (6,30) LEN, IW"),
    S("FORMAT (1H0,'THE PLAYERS, OVER',I5,' PULSES,',I3,' PULSES TO A COLUMN')", 30),
    S("DO 70 K = 1, NP"),
    S("DO 35 L = 1, 72"),
    S("IB(L) = 0"),
    S("B(L) = 0.0", 35),
    S("IT = 0"),
    S(RND, 40),
    S("IS = 24 + MOD(IX, 49)"),
    S("IF (IT + IS .GT. LEN) IS = LEN - IT"),
    S(RND),
    S("LOUD = 3 + MOD(IX, 5)"),
    S("PUNCH 45, IT, NOTE(K), IS, LOUD"),
    S("FORMAT (4I5)", 45),
    S("NB = NB + 1"),
    S("L1 = IT/IW + 1"),
    S("L2 = (IT + IS - 1)/IW + 1"),
    S("B(L1) = 1.0"),
    S("DO 50 L = L1, L2"),
    S("IF ((L-1)*IW .GE. IT) IC(K,L) = LOUD"),
    S("CONTINUE", 50),
    S("IT = IT + IS"),
    S("IF (IT .LT. LEN) GO TO 40"),
    S("NC = (LEN - 1)/IW + 1"),
    S("WRITE (6,55) K, NOTE(K)"),
    S("FORMAT (1H0,'PLAYER',I2,', NOTE',I4)", 55),
    S("WRITE (6,56) (IC(K,L), L = 1, 72)") if False else None,
]
held = [h for h in held if h is not None]
# implied DO loops are not in the subset: write the 72 elements out
row = ",".join("IC(K,%d)" % l for l in range(1, 73))
brow = ",".join("B(%d)" % l for l in range(1, 73))
held += S("WRITE (6,56) " + row)
held += S("WRITE (6,57) " + brow)
held += [
    S("FORMAT (1X,72I1)", 56),
    S("FORMAT (1X,72F1.0)", 57),
    S("CONTINUE", 70),
    S("SEC = FLOAT(LEN)/8.0"),
    S("WRITE (6,75) NB, SEC"),
    S("FORMAT (1H0,I4,' BOWS PUNCHED AS TAPE CARDS. AT 120 BEATS A MINUTE THE',"
      "' TAPE LASTS',F7.1,' SECONDS.')", 75),
    S("STOP"),
    "      END",
    D(1960, 1008, 4), D(59), D(66), D(59), D(66),
]
DECKS.append(deck("to-be-held-for-a-long-time",
                  "To be held for a long time (after La Monte Young)", held))

# ---------------------------------------------------------------- 4
row = ",".join("R(%d)" % l for l in range(1, 73))
met = [
    C("POEME SYMPHONIQUE, AFTER GYORGY LIGETI (1962)"),
    C("LIGETI'S PIECE IS FOR 100 METRONOMES, WOUND UP, SET TO DIFFERENT"),
    C("SPEEDS AND STARTED TOGETHER; IT ENDS WHEN THE LAST ONE STOPS."),
    C("HERE ONE PERFORMER TENDS UP TO TWENTY. EACH METRONOME GETS A"),
    C("SPEED BY CHANCE (A TICK EVERY 2 TO 8 PULSES), A WINDING GOOD FOR"),
    C("20 TO 35 TICKS, SO THE FAST ONES RUN DOWN FIRST, AND A START UP"),
    C("TO 3 PULSES LATE, SINCE NO ONE CAN START THEM ALL AT ONCE. EACH"),
    C("METRONOME TICKS ON ITS OWN HIGH NOTE. EVERY TICK IS PUNCHED AS A"),
    C("TAPE CARD (4I5): TIME IN PULSES, NOTE (MIDI NUMBER), LENGTH 1,"),
    C("LOUDNESS 1 TO 9. AT 120 BEATS A MINUTE A PULSE IS 1/8 SECOND."),
    C("DATA CARD (2I5): SEED (1 TO 30268), METRONOMES (1 TO 20)"),
    C("THE CHART: ONE ROW PER METRONOME, AN ASTERISK WHILE IT TICKS AND"),
    C("A FULL STOP ONCE IT HAS STOPPED."),
    S("DIMENSION IP(20), NT(20), IS(20), IE(20), R(72)"),
    S("READ (5,10) IX, M"),
    S("FORMAT (2I5)", 10),
    S("WRITE (6,15) M"),
    S("FORMAT (1H1,'POEME SYMPHONIQUE FOR',I3,' METRONOMES'/1H0,"
      "' METRONOME  TICKS A MINUTE  TICKS  STARTS  STOPS')", 15),
    S("LAST = 0"),
    S("NTOT = 0"),
    S("DO 30 K = 1, M"),
    S(RND),
    S("IP(K) = 2 + MOD(IX, 7)"),
    S(RND),
    S("NT(K) = 20 + MOD(IX, 16)"),
    S(RND),
    S("IS(K) = MOD(IX, 4)"),
    S("IE(K) = IS(K) + (NT(K) - 1)*IP(K)"),
    S("LAST = MAX0(LAST, IE(K))"),
    S("NTOT = NTOT + NT(K)"),
    S("NOTE = 84 + K"),
    S("N = NT(K)"),
    S("DO 20 J = 1, N"),
    S("IT = IS(K) + (J - 1)*IP(K)"),
    S("LOUD = 5"),
    S("IF (J .EQ. 1) LOUD = 7"),
    S("PUNCH 18, IT, NOTE, 1, LOUD"),
    S("FORMAT (4I5)", 18),
    S("CONTINUE", 20),
    S("IPM = 480/IP(K)"),
    S("WRITE (6,25) K, IPM, NT(K), IS(K), IE(K)"),
    S("FORMAT (1X,I10,I16,I7,I8,I7)", 25),
    S("CONTINUE", 30),
    S("IW = LAST/72 + 1"),
    S("WRITE (6,35) IW"),
    S("FORMAT (1H0,'THE METRONOMES RUNNING,',I3,' PULSES TO A COLUMN')", 35),
    S("DO 50 K = 1, M"),
    S("DO 45 L = 1, 72"),
    S("R(L) = 0.0"),
    S("IF ((L-1)*IW .LE. IE(K)) R(L) = 1.0"),
    S("CONTINUE", 45),
]
met += S("WRITE (6,46) K, " + row)
met += [
    S("FORMAT (1X,I3,2X,72F1.0)", 46),
    S("CONTINUE", 50),
    S("SEC = FLOAT(LAST)/8.0"),
    S("WRITE (6,55) LAST, SEC, NTOT"),
    S("FORMAT (1H0,'THE LAST METRONOME STOPS AT PULSE',I5,', AFTER',F6.1,"
      "' SECONDS'/1X,'AT 120 BEATS A MINUTE.',I5,' TICKS PUNCHED AS TAPE CARDS.')", 55),
    S("STOP"),
    "      END",
    D(1962, 10),
]
DECKS.append(deck("poeme-symphonique", "Poème symphonique (ten metronomes, after Ligeti)", met))

# ---------------------------------------------------------------- 5
names = ["PAWN", "KNIGHT", "BISHOP", "ROOK", "QUEEN", "KING"]
sc = [
    C("SOUND CHESS: A LISTENING GAME, AFTER TAKAKO SAITO"),
    C("SAITO MADE CHESS SETS FOR FLUXUS IN WHICH EVERY PIECE IS THE SAME"),
    C("PLAIN BOX AND ONLY ITS SOUND SAYS WHAT IT IS. HERE THE 32 BOXES"),
    C("ARE MIXED BY CHANCE AND SHAKEN ONE BY ONE ON TAPE. A PAWN HOLDS"),
    C("ONE GRAIN, A KNIGHT 2, A BISHOP 3, A ROOK 4, THE QUEEN 5 AND THE"),
    C("KING 6; WHITE BOXES RATTLE HIGH AND BLACK ONES LOW. PLAY THE"),
    C("STACKER ON THE TAPE PLAYER, COUNT THE GRAINS IN EACH SHAKE, WRITE"),
    C("DOWN THE PIECES, THEN TURN TO THE ANSWERS ON THE SECOND PAGE."),
    C("EACH GRAIN IS PUNCHED AS A TAPE CARD (4I5): TIME IN PULSES, NOTE"),
    C("(MIDI NUMBER), LENGTH 1, LOUDNESS 1 TO 9. A BOX IS SHAKEN FOR 16"),
    C("PULSES, TWO SECONDS AT 120 BEATS A MINUTE, ITS GRAINS FALLING ON"),
    C("DIFFERENT EVEN PULSES SO THAT THEY CAN BE COUNTED."),
    C("DATA CARD (3I5): SEED (1 TO 30268), BOXES TO SHAKE (1 TO 32),"),
    C("   PULSES FROM ONE BOX TO THE NEXT (AT LEAST 18)"),
    S("DIMENSION KT(32), KC(32), IP(32), IQ(8)"),
    S("READ (5,10) IX, NB, IG"),
    S("FORMAT (3I5)", 10),
    C("THE SET: 8 PAWNS, 2 KNIGHTS, 2 BISHOPS, 2 ROOKS, A QUEEN AND A"),
    C("KING OF EACH COLOUR. KT IS THE KIND (1 PAWN TO 6 KING), KC THE"),
    C("COLOUR (1 WHITE, 2 BLACK)"),
    S("DO 15 L = 1, 2"),
    S("DO 12 J = 1, 16"),
    S("K = (L - 1)*16 + J"),
    S("KC(K) = L"),
    S("KT(K) = 1"),
    S("IF (J .GT. 8) KT(K) = 2 + (J - 9)/2"),
    S("IF (J .EQ. 15) KT(K) = 5"),
    S("IF (J .EQ. 16) KT(K) = 6"),
    S("IP(K) = K", 12),
    S("CONTINUE", 15),
    C("MIX THE BOXES"),
    S("DO 20 L = 1, 31"),
    S("K = 33 - L"),
    S(RND),
    S("J = MOD(IX, K) + 1"),
    S("IT = IP(K)"),
    S("IP(K) = IP(J)"),
    S("IP(J) = IT", 20),
    S("WRITE (6,25)"),
    S("FORMAT (1H1,'SOUND CHESS, A LISTENING GAME'/1H0,'A PAWN HOLDS ONE GRAIN,',"
      "' A KNIGHT 2, A BISHOP 3, A ROOK 4, THE QUEEN 5, THE KING 6.'/1X,"
      "'WHITE BOXES RATTLE HIGH, BLACK ONES LOW.'/1H0,"
      "'  BOX  SHAKEN AT PULSE   WHAT DID YOU HEAR?')", 25),
    C("SHAKE EACH BOX: ITS GRAINS FALL ON DIFFERENT SLOTS OF THE 8"),
    S("NG = 0"),
    S("DO 50 IBX = 1, NB"),
    S("K = IP(IBX)"),
    S("IT0 = (IBX - 1)*IG"),
    S("WRITE (6,30) IBX, IT0"),
    S("FORMAT (1H0,I5,I17,'   ____________________')", 30),
    S("NOTE = 84"),
    S("IF (KC(K) .EQ. 2) NOTE = 67"),
    S("DO 35 J = 1, 8"),
    S("IQ(J) = J - 1", 35),
    S("N = KT(K)"),
    S("DO 45 J = 1, N"),
    S("JJ = 9 - J"),
    S(RND),
    S("L = MOD(IX, JJ) + 1"),
    S("IT = IQ(L)"),
    S("IQ(L) = IQ(JJ)"),
    S("IQ(JJ) = IT"),
    S("IT = IT0 + 2*IT"),
    S(RND),
    S("LOUD = 5 + MOD(IX, 3)"),
    S("PUNCH 40, IT, NOTE, 1, LOUD"),
    S("FORMAT (4I5)", 40),
    S("NG = NG + 1"),
    S("CONTINUE", 45),
    S("CONTINUE", 50),
    C("THE ANSWERS, ON A NEW PAGE"),
    S("WRITE (6,55)"),
    S("FORMAT (1H1,'SOUND CHESS: THE ANSWERS'/1H0,'  BOX  PIECE')", 55),
    S("DO 70 IBX = 1, NB"),
    S("K = IP(IBX)"),
    S("I = KT(K) + 6*(KC(K) - 1)"),
]
for i in range(12):
    sc += S("IF (I .EQ. %d) WRITE (6,%d) IBX" % (i + 1, 101 + i))
sc += [
    S("CONTINUE", 70),
    S("WRITE (6,75) NG"),
    S("FORMAT (1H0,I4,' GRAINS PUNCHED AS TAPE CARDS.')", 75),
    S("STOP"),
]
for i in range(12):
    col = "WHITE" if i < 6 else "BLACK"
    sc += S("FORMAT (1X,I5,2X,'%s %s')" % (col, names[i % 6]), 101 + i)
sc += ["      END", D(1965, 12, 24)]
DECKS.append(deck("sound-chess", "Sound chess (a listening game, after Takako Saito)", sc))

# ---------------------------------------------------------------- write
def js_str(s):
    return json.dumps(s, ensure_ascii=False)

lines = ["["]
for i, d in enumerate(DECKS):
    lines.append('  { id: %s, name: %s, cards: [' % (js_str(d["id"]), js_str(d["name"])))
    for j, c in enumerate(d["cards"]):
        lines.append("    " + js_str(c) + ("," if j < len(d["cards"]) - 1 else ""))
    lines.append("  ] }" + ("," if i < len(DECKS) - 1 else ""))
lines.append("]")
open(OUT, "w").write("\n".join(lines) + "\n")
for d in DECKS:
    print(d["id"], len(d["cards"]))
