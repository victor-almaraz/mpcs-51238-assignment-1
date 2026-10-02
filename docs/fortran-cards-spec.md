# FORTRAN Punchcard Simulator: Spec

## What to build

A browser page where the user punches a deck of 80-column cards holding a FORTRAN IV / FORTRAN 66 program (plus data cards), feeds it to a "reader", and reads the output on a line printer. Plain HTML, CSS, and vanilla JavaScript. No dependencies, no build step, no storage, no network.

This spec defines one shared engine (in `scripts/`) plus the v1 page. Later versions reuse the engine unchanged and only change the interface and styling. The sieve generator is not a separate engine: it is a prewritten FORTRAN deck (sample 5) that runs on this interpreter. See `sieve-solver-spec.md`.

## Build order

Build and verify in this order. Each step has acceptance checks in "Acceptance criteria".

1. `scripts/hollerith.js` — character/punch tables and card encode/decode.
2. `scripts/fortran.js` — deck split, scanner, parser, interpreter, FORMAT, and the sample decks. Verify with the sample decks and the acceptance list (`tests/`) before touching the UI.
3. The v1 page — editor, card view, run, printer output, output stacker, sample menu.

## Definition of done (v1)

- `Fortran.run` produces the exact output shown for sample decks 1-4, and the sieve deck (sample 5) passes the checks in `sieve-solver-spec.md`.
- Every item in "Acceptance criteria" passes.
- `Fortran.run` never throws; every problem appears in `result.log` with a card number where one applies.
- The page has all six elements in "Page (v1)" and a link back to the gallery (`../`).
- No frameworks, no build step, no storage, no network calls.
- The tests in `tests/` pass (open `tests/index.html`).

## Page (v1)

1. **Instructions:** short explanation of the card format, the supported language, and how to use the simulator.
2. **Deck editor:** one card per line, each padded to 80 columns, with a column ruler and field shading (cols 1-5, 6, 7-72, 73-80).
3. **Card view:** the selected card as a 12 x 80 grid of punched holes, with the character printed above each column.
4. **Run button:** runs the deck; shows printer output (monospace, fixed width) and a job log (errors, STOP code).
5. **Output stacker:** cards punched by the program (`PUNCH`) shown as real cards and reusable. See "Punched output".
6. **Sample menu:** loads the five decks in "Sample decks" (read from `Fortran.samples`), including the sieve generator.

## Repo placement

The engine lives in `scripts/` as classic scripts (no ES modules, so pages work from `file://` too). Each version is a folder at the repo root (`v01/`, `v02/`, ...) whose `index.html` loads the engine with relative paths, e.g. `<script src="../scripts/hollerith.js"></script>` then `<script src="../scripts/fortran.js"></script>`. The root gallery `index.html` uses `scripts/...`. Load `hollerith.js` before `fortran.js`.

| File | Global | Purpose |
|---|---|---|
| `scripts/hollerith.js` | `Hollerith` | Character/punch tables, card encode/decode |
| `scripts/fortran.js` | `Fortran` | Deck split, scanner, parser, interpreter, FORMAT, and sample decks |

The engine has no DOM code. Pages use the `Fortran` global only; `fortran.js` re-exports the card helpers so a page never has to touch `Hollerith` directly.

### API

```js
Fortran.encodeCard(text)   // string -> array of 80 column masks (a mask is a Set of punched rows)
Fortran.decodeCard(masks)  // array of 80 masks -> 80-char string
Fortran.punches(ch)        // "A" -> [12, 1];  "." -> [12, 8, 3];  " " -> [];  unknown char -> []
                           // rows are listed in the notation of the table below (12-8-3)
Fortran.run(cards, opts)   // cards: array of strings (each padded/truncated to 80 internally)
Fortran.samples            // array of { name, cards: [strings] }
```

`Fortran.run` returns:

```js
{
  ok: boolean,        // false if the run stopped on an error
  printer: [string],  // line-printer lines, carriage control already applied.
                      // A new page is the entry "\f" on its own, followed by the page's first line.
  punched: [string],  // cards punched by PUNCH, each exactly 80 chars
  log: [string],      // diagnostics and messages, e.g. "card 7: undefined label 40"
  listing: [string]   // source listing with card numbers
}
```

`run` must never throw. `opts` is optional; the only defined field is `stmtLimit` (default 1000000).

## Card format

An 80-column card. Any input is padded with blanks or truncated to exactly 80 characters.

| Columns | Meaning |
|---|---|
| 1 | `C` or `*` here makes the whole card a comment |
| 1-5 | Statement label: unsigned integer, blanks ignored (ignored on comment cards) |
| 6 | Continuation: any character except blank or `0` continues the previous statement |
| 7-72 | Statement text |
| 73-80 | Ignored by the compiler (sequence numbers). If non-blank on a source card, add a warning to `log` |

A statement's text is columns 7-72 of its first card, joined with columns 7-72 of each following continuation card.

## Hollerith punch codes (IBM 029)

Card rows, top to bottom: 12, 11, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9. A column is the set of rows punched in it. These are the IBM 029 (EBCDIC, System/360) codes; all values below were verified against Douglas W. Jones's punched-card code tables, DEC's 029 table, and mass:werk's 029 chart.

| Characters | Punches |
|---|---|
| space | none |
| 0-9 | that digit's row only |
| A-I | 12 plus 1..9 (A = 12-1 ... I = 12-9) |
| J-R | 11 plus 1..9 (J = 11-1 ... R = 11-9) |
| S-Z | 0 plus 2..9 (S = 0-2 ... Z = 0-9) |

| Char | Punches | Char | Punches | Char | Punches |
|---|---|---|---|---|---|
| `&` | 12 | `-` | 11 | `/` | 0-1 |
| `.` | 12-8-3 | `$` | 11-8-3 | `,` | 0-8-3 |
| `(` | 12-8-5 | `*` | 11-8-4 | `%` | 0-8-4 |
| `+` | 12-8-6 | `)` | 11-8-5 | `_` | 0-8-5 |
| `<` | 12-8-4 | `;` | 11-8-6 | `>` | 0-8-6 |
| `:` | 8-2 | `=` | 8-6 | `?` | 0-8-7 |
| `#` | 8-3 | `'` | 8-5 | `"` | 8-7 |
| `@` | 8-4 | `¢` | 12-8-2 | `!` | 11-8-2 |
| `\|` | 12-8-7 | `¬` | 11-8-7 | | |

The characters a FORTRAN program actually needs are a subset: the letters, the digits, and blank `=` `+` `-` `*` `/` `(` `)` `,` `.` `$` and `'`. The rest of the table is for completeness (comment text, printed labels). The full 029 set is 64 characters.

`encodeCard` converts lowercase to uppercase. A character not in the table encodes as no punches (a blank column); the deck editor should prevent entering such characters rather than silently blanking them.

## Language subset

Main program only (no SUBROUTINE or FUNCTION). The program ends at the `END` card.

**Blanks are insignificant.** Strip all blanks from a statement before parsing, except inside Hollerith (`nH...`) and apostrophe (`'...'`) literals. There are no reserved words. (Apostrophe literals are an IBM System/360 FORTRAN IV extension; standard FORTRAN 66 uses only `nH` Hollerith. Support both.)

**Classifying a statement** (test in this order):
1. **Assignment**, if the text is `NAME = expr` or `NAME(subscripts) = expr`, where `=` follows the name (or its subscript's closing `)`) and `expr` has no comma at parenthesis depth 0.
2. Otherwise match the leading keyword: `DO`, `IF(`, `GOTO`, `READ`, `WRITE`, `PRINT`, `PUNCH`, `FORMAT`, `DIMENSION`, `INTEGER`, `REAL`, `CONTINUE`, `STOP`, `PAUSE`, `END`.

So `DO 10 I = 1, 10` is a loop, but `DO 10 I = 1.10` is an assignment to `DO10I`.

**Types.** Names are a letter followed by up to 5 more letters or digits (6 total). Names beginning I-N are INTEGER; all others REAL, unless declared. Integers are 32-bit; integer division truncates toward zero. Reals are single precision (`Math.fround`). Mixed integer/real arithmetic promotes to REAL. Uninitialized variables are 0.

**Statements**

| Statement | Behavior |
|---|---|
| `V = expr` | Assignment, converted to V's type. `V` may be an array element |
| `INTEGER a, b` / `REAL a, b` | Declare variable types, overriding the I-N rule |
| `DIMENSION A(n), B(m,n)` | Arrays, 1-based, column-major, up to 2 dimensions |
| `GO TO n` | Jump to label n |
| `GO TO (n1,n2,...), I` | Computed GO TO; out-of-range I falls through |
| `IF (e) n1, n2, n3` | Arithmetic IF: branch on e negative / zero / positive |
| `IF (cond) stmt` | Logical IF; runs stmt if cond is true |
| `DO n I = m1, m2 [, m3]` | Loop through labelled statement n; runs at least once (one-trip); step defaults to 1 |
| `CONTINUE` | No-op (usual loop terminator) |
| `READ (5,f) list` / `READ f, list` | Read data cards under FORMAT f |
| `WRITE (6,f) list` / `PRINT f, list` | Line printer |
| `PUNCH f, list` / `WRITE (7,f) list` | Punch one card per record. Required. See "Punched output" |
| `FORMAT (...)` | See "FORMAT" |
| `PAUSE [n]` | Log `PAUSE n`, then continue (v1 does not halt for input) |
| `STOP [n]` | End the job; log `STOP n` if n is given |
| `END` | End of the source deck |

Logical/relational operators: `.LT. .LE. .EQ. .NE. .GT. .GE. .AND. .OR. .NOT. .TRUE. .FALSE.`

**Expressions.** `+ - * / **`, standard precedence, `**` right-associative, unary minus, parentheses, array elements.

**Intrinsics.** `SQRT ABS IABS FLOAT INT IFIX MOD AMOD SIN COS ATAN EXP ALOG ALOG10 MAX0 MIN0 AMAX1 AMIN1 SIGN`.

## FORMAT

Edit descriptors: `Iw`, `Fw.d`, `Ew.d`, `nX`, `nHtext`, `'text'` (IBM extension; equivalent to `nH`), `/`, with repeat counts (`3I5`) and groups (`2(I3,F6.2)`).

- **Output** fields are right-justified. A value that does not fit in width w prints as w asterisks. `Ew.d` prints in a normalized form such as `0.1234E+05`.
- **Input:** for `F` with no decimal point in the field, apply the implied d; an explicit point overrides d. Leading and trailing blanks are ignored, embedded blanks read as zeros (as on the IBM machines), and an all-blank numeric field reads as 0.
- **Reversion:** if list items remain when the closing `)` is reached, start a new record and rescan from the last top-level group, or from the start if there is none.
- `/` ends the current record.
- FORMAT statements may appear anywhere in the program, before or after their use.

## Carriage control (printer only)

The first character of every printed record is a carriage control character. It is consumed, not printed. It does not apply to punched cards.

| First char | Action |
|---|---|
| space | Single space |
| `0` | Double space (one blank line first) |
| `-` | Triple space |
| `1` | New page |
| `+` | Overprint the previous line |

Render page breaks visibly. Printer lines are at most 132 characters. Do not hide carriage-control mistakes: a FORMAT whose first printed character is `1` causes a page break, as on real machines.

## Punched output

`PUNCH` is a core feature: a program produces new cards the user can read back in or hand to another tool.

Engine:
- Each `PUNCH` (or `WRITE (7,f)`) record becomes one card, padded with blanks to exactly 80 characters.
- No carriage control on punched records: the first character the FORMAT produces is column 1.
- A record longer than 80 characters is truncated to 80, with a warning in `log` (with the card number).
- Punched cards are returned in order in `result.punched` as 80-character strings, usable directly as editor input or with `encodeCard`.
- A program does not read back what it punches during the same run.

Page:
- Show punched cards in an output stacker, rendered as cards (holes and printed characters), separate from printer output.
- Offer an action to load the stacker into the deck editor (replace or append), so a second run reads them as data cards.
- Offer copy/download of the stacker as plain text, one 80-character line per card (Blob download, no storage).
- Clear the stacker at the start of each run.

## Deck structure

The deck is the source cards through the first `END` card, then data cards.

- No job-control cards are needed; everything after `END` is data.
- Reading past the last data card ends the job with the log message `END OF FILE ON UNIT 5`.
- Build `listing` as the source with card numbers; append diagnostics to `log`; program output goes to `printer`.

## Errors and limits

Report with a card number where one applies: unknown statement, unbalanced parentheses, undefined label, missing FORMAT, bad Hollerith count, DO terminator not found, subscript out of range, integer division by zero, invalid input data. After `opts.stmtLimit` executed statements (default 1000000), stop with `TIME LIMIT EXCEEDED`.

## Sample decks

Stored in `Fortran.samples`. Labels in columns 1-5; statements from column 7.

**1. Squares and roots**
```
C     SQUARES AND SQUARE ROOTS
      WRITE (6,10)
   10 FORMAT (1H1,5X,1HN,6X,6HSQUARE,5X,4HROOT)
      DO 20 I = 1, 5
      X = FLOAT(I)
      Y = SQRT(X)
      ISQ = I*I
      WRITE (6,30) I, ISQ, Y
   20 CONTINUE
   30 FORMAT (1X,I6,I12,F9.4)
      STOP
      END
```
Output (on a new page):
```
     N      SQUARE     ROOT
     1           1   1.0000
     2           4   1.4142
     3           9   1.7321
     4          16   2.0000
     5          25   2.2361
```

**2. Heron's formula**
```
C     AREA OF A TRIANGLE BY HERONS FORMULA
      READ (5,10) IA, IB, IC
   10 FORMAT (3I5)
      S = FLOAT(IA+IB+IC)/2.0
      AREA = SQRT(S*(S-FLOAT(IA))*(S-FLOAT(IB))*(S-FLOAT(IC)))
      WRITE (6,20) IA, IB, IC, AREA
   20 FORMAT (1H0,3HA =,I5,5H  B =,I5,5H  C =,I5,8H  AREA =,F10.2)
      STOP
      END
```
Data card: `    3    4    5`

Output (preceded by one blank line):
```
A =    3  B =    4  C =    5  AREA =      6.00
```

**3. Largest of N values**
```
C     LARGEST VALUE IN A SET OF NUMBERS
      DIMENSION A(100)
      READ (5,100) N
  100 FORMAT (I5)
      DO 5 I = 1, N
      READ (5,101) A(I)
    5 CONTINUE
  101 FORMAT (F10.2)
      BIGA = A(1)
      DO 20 I = 2, N
      IF (BIGA - A(I)) 10, 20, 20
   10 BIGA = A(I)
   20 CONTINUE
      WRITE (6,102) N, BIGA
  102 FORMAT (1H ,10HLARGEST OF,I4,8H VALUES:,F10.2)
      STOP
      END
```
Data cards: `    5`, then one value per card: `3.5`, `-2.0`, `17.25`, `9.0`, `17.0`.

Output:
```
LARGEST OF   5 VALUES:     17.25
```

**4. Punch the multiples of 3 below 20**
```
C     PUNCH THE MULTIPLES OF 3 BELOW 20, ONE PER CARD
      DO 10 N = 0, 19
      IF (MOD(N,3)) 10, 5, 10
    5 PUNCH 20, N
   10 CONTINUE
   20 FORMAT (I5)
      STOP
      END
```
Punches 7 cards (each 80 columns): `    0`, `    3`, `    6`, `    9`, `   12`, `   15`, `   18`. Printer output is empty. Loading these as data cards for a program that runs `READ (5,10) N` with `10 FORMAT (I5)` reads 0, 3, 6, ... in order.

**5. Sieve generator (after Xenakis)**

A longer prewritten program that generates sieves: sets of integers built from residual classes. It reads a mode, a number of classes and a range, then one card per class, and prints and punches the members. The card layout, data format, and expected output are in `sieve-solver-spec.md`. Its source is in `Fortran.samples[4]`, followed by the data cards for the sieve `5@2 | 5@3` over 0 to 19.

## Acceptance criteria

Engine:
- Sample decks 1-3 produce exactly the output shown; sample 4 produces exactly 7 cards in `result.punched` and empty `printer`; sample 5 produces the output in `sieve-solver-spec.md`.
- `DO 10 I = 1.10` on one card parses as an assignment to `DO10I`, not a loop.
- `G O T O 20` behaves like `GOTO 20` (blanks insignificant).
- A `0` in column 6 is not a continuation; `1` or `*` is.
- Text in columns 73-80 is ignored (and warned).
- `WRITE (6,10) 123` with `10 FORMAT (I5)` prints ` 123` on a normal line (`I5` gives `  123`; the first blank is carriage control); with `10 FORMAT (I3)` the leading `1` is carriage control, causing a page break (`printer` is `["\f", "23"]`).
- `3/2*2` evaluates to 2 (integer arithmetic).
- `DO 5 I = 3, 1` runs its body once (one-trip).
- `PUNCH 20, N` with `20 FORMAT (I5)`, N = 3, punches `    3` then 75 blanks (no carriage-control removal).
- `PUNCH 20, N` with `20 FORMAT (1X,I5)` punches a card with a blank column 1 and the number in columns 2-6.
- A `PUNCH` record over 80 characters is truncated to 80 with a warning.
- `Fortran.run` never throws; a deck with an undefined label returns `ok: false` with a card-numbered log entry.

Page:
- Running a deck twice clears the stacker between runs.
- The stacker can be loaded back into the editor and re-run as data.
- Every version links back to the gallery (`../`).
