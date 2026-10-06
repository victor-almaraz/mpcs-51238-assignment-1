# Brief: a new magazine for the workspace's shelf (v25)

First read the general brief, `BRIEF.md`, beside this file.
(the project, voice, British spelling, facts must be right and verified by web search, never say "version").

The shelf already holds **Moiré**, a magazine of art and computing. Read its text, written in the exact
format you will use, to see the voice, length and how decks are woven in:
util/v25/text/magazine.md

Two new magazines join it, each its own title with its own subject. Each is written as text in that same
Markdown structure (COVER, EDITORS, CONTENTS, ARTICLE 01 …, CATALOGUE), with these differences:
- **Three articles** (ARTICLE 01–03), each a proper feature of roughly 800–1,000 words, `##` subheadings welcome.
- CONTENTS lists 01, 02, 03 and the catalogue (use the number of decks as the catalogue's contents number,
  e.g. `- 05 | Five decks to punch | …`).
- **Four or five new decks** of its own, discussed in the articles and listed in its CATALOGUE.
- The COVER's `names:` line names the people the issue is about.
- EDITORS ends with a one-line colophon (how the issue is printed), as Moiré's does.

## The decks
A deck is FORTRAN on punched cards, run by the page's own interpreter. You must write each deck, run it, and make
sure it does what the article says it does.
- The language and the card format: docs/fortran-cards-spec.md
  (read it all; only what it describes is supported). The tape-card format (for decks that make music the tape
  player plays): docs/tape-spec.md
- Existing decks to learn from (their comment-card style, how they take their data cards, how they use a seed
  and the generator: multiply by 171 and keep the remainder after dividing by 30269, as Moiré explains):
  v25/decks.js (look at the `magazine` and `music` sections).
- Run a deck with the interpreter in JavaScriptCore, for example:
  ```
  JSC=/System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Helpers/jsc
  $JSC scripts/hollerith.js scripts/fortran.js yourtest.js
  ```
  where `yourtest.js` builds the deck (an array of strings, one per card) and calls `Fortran.run(deck)`, then
  prints `result.printer`, `result.punched`, `result.log`, `result.ok` (read scripts/fortran.js for the exact
  result shape). Check that every card is at most 80 columns, statements start in column 7, comment cards have
  `C` in column 1, the program ends with `END` and the data cards follow it.
- Each deck starts with comment cards, in capitals as the existing ones are, saying what it is, what it does and
  what each data card holds ("DATA CARDS: (…) …", "TRY …"). Printed output should look good on a line printer
  (the printer is 132 columns; pictures in characters should be at most about 72 wide). If it punches cards,
  say what they are for (tape cards for the tape player; or a card that carries the run on).
- Where chance is used, take a seed from a data card, so the same seed gives the same result.

## What to write, where
Write two files (do not edit anything in v25/):
1. The magazine text: the path given in your task.
2. The decks, as a JavaScript array literal of deck objects in exactly the existing format, in the path given in
   your task, e.g.
   ```
   [
     { id: "the-house-of-dust", name: "The house of dust (after Knowles and Tenney)", cards: [
       "C     ...",
       ...
     ] },
     ...
   ]
   ```
   Ids are lowercase words joined by hyphens and must not clash with any existing id in decks.js. In the
   magazine text, refer to each deck as `[deck: <id> | <name without the parenthesis>]`, exactly as Moiré does.

In your report: the decks (id, what each does), what you verified by running them (with a sample of each one's
output), and the facts you checked, with sources.
