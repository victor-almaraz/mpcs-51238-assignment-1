# Brief: cleaning up and elaborating the in-universe text of the workspace (v25)

## The project
`v25/` is a web page: a pixel-art composer's workroom at a
computing centre, around the 1960s–70s, built on FORTRAN punched cards and Iannis Xenakis's sieves. Its
audience is people interested in computer history and algorithmic music. Everything in the room is an
in-universe document or object:

- the **reference manual** on the shelf (three volumes: FORTRAN; Sieves; Music and tape), in `v25/index.html`
  in `<section ... data-station="manual">`;
- the **Xenakis miscellanea** in a file box (plates, photographs, notes), in `v25/index.html` in
  `<section ... data-station="portfolio">`;
- **Moiré**, a magazine of art and computing, in `v25/index.html` in `<section ... data-station="magazine">`;
- the **computer's desktop** (a separate page in an iframe), `v25/computer/index.html`: a Read Me, chapters of a
  course (`win-ch-*`), picture documents about Xenakis (`win-pf-*`), Dada miscellanea (`win-dd-*`), course
  sheets (`win-sheet-*`), and the windows of applications.

## What the room does now (so the manual describes it correctly)
The room is drawn straight on. Everything that can be taken up is a hotspot (white outline, a caption by the
cursor; arrow keys move between hotspots, Enter takes one up, H outlines all). Right-click (or L) *looks* at a
thing: a narrator line says what it is, and each print offers a related deck. The prints, plants, lamp and mug
can be swapped by pressing them; the bare wall (or the menu) changes the wallpaper; a switch on the wall turns
the lamp off and on. The light follows the visitor's clock (morning, evening, night), or the menu's *Light*. The
room's furnishing is kept in the address (`#room=…`), so *Copy a link to this room* shares it. The room has small
sounds (menu: *Room sounds*). On the shelf: the manual, the magazine, the miscellanea, the deck box. On the desk:
the coding form, the out tray, the computer, the tape player. Under the desk: the **card reader and line printer**
(every deck that is run passes through it: the reader takes the cards one by one, then the printer prints the
output line by line, then the printout goes to the out tray) and the **UPIC** (a drawing tablet after Xenakis's
UPIC of 1977: draw lines on a page, time across, pitch up from C2 to C6; each line is a voice in a wave drawn on a
pad; a page can be played, and punched as tape cards into the out tray's stacker for the tape player). The coding
form's card in hand is *at the keypunch*: a punch head follows the column being typed. The tape player plays tape
cards (TIME, NOTE, LEN, LOUD in four I5 fields) from the stacker.

## The goals
1. **Clean up.** Fix factual errors, awkward or stiff phrasing, repetition, inconsistent terms and spelling,
   sentences that are hard to follow, and anything that describes the room as it no longer is.
2. **Elaborate.** Add depth where it serves a curious reader: history, context, how a thing works, a worked
   example, a telling detail. Aim for roughly a third to a half more text overall, not padding: every added
   sentence should teach something or make a document more vivid as an object in the room.

## Voice and conventions
- Keep each document's own voice: the manual is clear, plain and instructional (IBM manual-like); the
  miscellanea and the computer's picture documents are a curator's captions; the magazine is a lively
  editorial voice of an art-and-computing magazine.
- British spelling, as the existing text uses (colour, programme for a concert programme but program for code,
  centre). Curly quotes and apostrophes as HTML entities as the file already does (`&rsquo;`, `&ldquo;`,
  `&ndash;` …). Titles of works in `<cite>`; foreign-language titles with `lang`.
- **Never** state a version number of this site or say "version"; the page must not know it is one of many.
- **Facts must be right.** Check every date, name, place, figure and claim you add or keep against reliable
  sources (use web search). If you cannot verify something, leave it out or say less. Do not invent quotations;
  quote only what you can source, and keep quotations short. Where a picture is a drawing made for the room, it
  may say "a drawing made for this album" (or the like) — do not present it as a historical document.

## Hard constraints (the page's scripts depend on these)
- Change **text content** only, plus adding new paragraphs, list items, headings or (where noted) chapters/pages.
- Keep every `id`, `class`, `data-*` attribute, `aria-*` attribute, `role`, button, form control, `<canvas>`,
  `<img>` (`src`, `width`, `height`; you may improve `alt` text), and the nesting the scripts rely on. Do not
  remove or rename any element that has an `id` or `data-*` attribute.
- Do not change program listings, FORTRAN code, card images, deck contents or anything inside `<pre>` blocks that
  shows code or output, except obvious typos in prose around them.
- Only HTML/CSS/JS; no external links, fonts, images or services.
- Keep markup valid and in the file's existing style (indentation, entity use).

## When you are done
Report back: what you changed (briefly, by document), what you added, any facts you corrected (with the
source you relied on), and anything you were unsure of and left alone.
