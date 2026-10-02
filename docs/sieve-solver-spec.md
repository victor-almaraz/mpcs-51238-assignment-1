# Sieve Generator: Spec

## What to build

A prewritten FORTRAN deck that generates Xenakis-style sieves: sets of integers built from residual classes, combined by union, intersection, or complement. It is **not** a separate JavaScript engine. It is sample deck 5 in `Fortran.samples` (`scripts/fortran.js`) and runs on the same interpreter as the other samples, so it is limited to the language subset in `fortran-cards-spec.md`. The deck produces integers only. Mapping integers to pitch or rhythm is out of scope.

## Concepts

**Residual class** `m@s`: all integers n with `n - s` divisible by m (Xenakis writes m with subscript s). `3@0` is ..., -3, 0, 3, 6, 9, ...; `5@2` is ..., -3, 2, 7, 12, ...

- m is an integer >= 1. s is any integer, including negative; `3@-1` equals `3@2` (the shift is taken mod m).
- Use true mathematical modulo. FORTRAN `MOD` takes the sign of its first argument, so the deck computes `MOD(MOD(n - s, m) + m, m)`.

**Combining classes.** The deck combines its N classes in one of three ways, chosen by the mode:

| Mode | Sieve | Meaning |
|---|---|---|
| 1 | `c1 \| c2 \| ...` | union: in at least one class |
| 2 | `c1 & c2 & ...` | intersection: in every class |
| 3 | `!(c1 \| c2 \| ...)` | complement of the union: in no class |

Nested expressions (for example `(3@0 | 4@1) & !5@2`) are not supported by the deck. One deck run handles one flat combination.

**Period.** Every sieve is periodic with period equal to the least common multiple of its moduli (`3@0 | 4@1` has period 12). The deck does not compute it; the printed table lets you see it.

## Data cards

The deck reads its input after the `END` card.

| Card | Format | Fields |
|---|---|---|
| 1 | `3I5` | `MODE` (1, 2, or 3), `N` (number of classes, 1 to 10), `LIMIT` (tests the integers 0 to LIMIT-1) |
| 2 to N+1 | `2I5` | `M` (modulus, at least 1), `S` (shift, may be negative) |

## Output

Printer (the first line is on a new page, so `printer` begins with `"\f"`):

```
SIEVE  MODE = 1  N =  2  LIMIT =    20

     K   MEMBER   INTERVAL
     1        2
     2        3          1
     3        7          4
     ...
```

- Each member of the sieve in increasing order, numbered K, with its interval from the previous member (none for the first).
- A last line `n MEMBERS` after one blank line (`0 MEMBERS` if the sieve is empty).

Punch: one card per member, `I5` in columns 1-5, so the members can be loaded into the editor and read back as data by another deck.

## Limits

- N at most 10; a larger N stops the job with `subscript out of range`.
- Members and moduli must fit in `I5`/`I6` (up to 99999 for punched members); LIMIT up to 999999 prints.
- The statement limit applies (`opts.stmtLimit`, default 1000000). The deck runs about `LIMIT x N` inner steps, so a LIMIT of a few thousand is comfortable.

## Sample data

Sample 5 ships with the data cards for `5@2 | 5@3` over 0 to 19:

```
    1    2   20
    5    2
    5    3
```

## Acceptance criteria

All checked in `tests/sieve.test.js` against an independent JavaScript reference.

| Mode | Classes (m@s) | LIMIT | Members |
|---|---|---|---|
| 1 | `5@2`, `5@3` | 20 | 2, 3, 7, 8, 12, 13, 17, 18 (intervals 1, 4, 1, 4, 1, 4, 1) |
| 1 | `3@0`, `4@0` | 12 | 0, 3, 4, 6, 8, 9 |
| 2 | `3@0`, `4@0` | 24 | 0, 12 |
| 3 | `3@0` | 7 | 1, 2, 4, 5 |
| 1 | `3@-1` | 10 | 2, 5, 8 |
| 2 | `3@0`, `3@1` | 50 | none (`0 MEMBERS`) |

- The punched cards equal the printed members, one per card.
- Run the sample, load the stacker into the editor as data, and a deck that reads them with `10 FORMAT (I5)` gets the same members in order.
- N = 11 stops with a card-numbered `subscript out of range` in `log`.
