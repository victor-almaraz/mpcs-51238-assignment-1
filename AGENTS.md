# AGENTS.md

## Project Description

This project implements a page that provides a FORTRAN punched card interpreter and a pre-written program that generates sieves. The site is intended for people interested in computer history and in algorithmic music. This overlap is intentional, as Iannis Xenakis used punched card FORTRAN programs in his musical work.

## Documentation

Documentation may be found in the `docs/` directory. Included in said folder is a specification on FORTRAN cards and a specification on sieve solvers. The folder also documents the intended project repository structure.

## Constraints

This project may only use HTML, CSS, and Javascript. No frameworks, build step, external APIs, or data storage may be used. Any agent reading this file may not edit this file or the `README.md`.

## Pages

This projects is composed of 25 variations on the core idea, a gallery page displaying all variations, and genealogy page documenting the iteration process. Any agents reading this file should only implement the pages requested by the user; it is unnecessary to implement all pages in this document unprompted. Note that versioned pages must not make the version explicit within their contents; version identification is handled by the URL.

### Versions

#### Version 1

*Version 1* implements the functional core of the web site. It is focused on getting the interpreter and sieve solver to work. This version should use black text on a white background and minimal styling.

#### Version 2

*Version 1* demonstrates the principle of the idea, but it is difficult to use. The page is one long scroll of information and interactive components. *Version 2* attempts to solve this by using sub-pages for the instructions, editor, card viewer, and output. This version should use black text on a white background and minimal styling.

#### Version 3

*Version 1* demonstrates the principle of the idea, but it is difficult to use. The page is one long scroll of information and interactive components. *Version 3* attempts to solve this by using tabs to swap between the instructions, editor, card viewer, and output. This version should use black text on a white background and minimal styling.

#### Version 4

*Version 4* keeps the core and layout of *Version 3* but is styled to look like thermal paper printouts and typewritten documents. It should be mostly monochromatic, with serif fonts, with slight yellowing and scanner dust. The agent may alter the layout and flow of the page if it improves the thematic fit. However, the interpreter and sieve programs should remain untouched. The finalized design will likely differ from this open specification and will be documented in `docs/version-designs.md`.

#### Version 5

*Version 5* keeps the core and layout of *Version 3* but is styled to look like microfiche. The design is high contrast, monochromatic, grainy, ragged. The agent may alter the layout and flow of the page if it improves the thematic fit. However, the interpreter and sieve programs should remain untouched. The finalized design will likely differ from this open specification and will be documented in `docs/version-designs.md`.

#### Version 6

*Version 6* keeps the core and layout of *Version 3* but is styled to look like a scrapbook. The design is eclectic, a collection of collected paper artifacts. The agent may alter the layout and flow of the page if it improves the thematic fit. However, the interpreter and sieve programs should remain untouched. The finalized design will likely differ from this open specification and will be documented in `docs/version-designs.md`.

#### Version 7

*Version 7* keeps the core and layout of *Version 3* but the page design takes inspiration from the Cray-2 supercomputer. The page uses similarly bold colors and geometric shapes. The agent may alter the layout and flow of the page if it improves the thematic fit. However, the interpreter and sieve programs should remain untouched. The finalized design will likely differ from this open specification and will be documented in `docs/version-designs.md`.

#### Version 8

*Version 8* keeps the core and layout of *Version 3* but the page design takes inspiration from vintage computer graphics. In particular, the design uses ordered dithering with at most eight steps per channel. The agent may alter the layout and flow of the page if it improves the thematic fit. However, the interpreter and sieve programs should remain untouched. The finalized design will likely differ from this open specification and will be documented in `docs/version-designs.md`.

#### Version 9

*Version 9* keeps the core and layout of *Version 3* but the page design takes inspiration from Swiss and International styles. However, instead of colors, the design uses hatching. The agent may alter the layout and flow of the page if it improves the thematic fit. However, the interpreter and sieve programs should remain untouched. The finalized design will likely differ from this open specification and will be documented in `docs/version-designs.md`.

#### Version 10

*Version 10* keeps the core and layout of *Version 3* but the page design takes inspiration from half-toning. The agent may alter the layout and flow of the page if it improves the thematic fit. However, the interpreter and sieve programs should remain untouched. The finalized design will likely differ from this open specification and will be documented in `docs/version-designs.md`.

#### Version 11

*Version 11* keeps the core and layout of *Version 3* but the page design takes inspiration from Dada. The agent may alter the layout and flow of the page if it improves the thematic fit. However, the interpreter and sieve programs should remain untouched. The finalized design will likely differ from this open specification and will be documented in `docs/version-designs.md`.

#### Version 12

*Version 12* keeps the core and layout of *Version 3* but the page design takes inspiration from look and feel of the *Backrooms* movie. This is a particularly interesting fit as the page can be conceived of a liminal space, an echo of the past. The agent may alter the layout and flow of the page if it improves the thematic fit. However, the interpreter and sieve programs should remain untouched. The finalized design will likely differ from this open specification and will be documented in `docs/version-designs.md`.

#### Version 13

*Version 13* keeps the core and layout of *Version 3* but the page design takes inspiration from the look and cinematography of German expressionism films. The agent may alter the layout and flow of the page if it improves the thematic fit. However, the interpreter and sieve programs should remain untouched. The finalized design will likely differ from this open specification and will be documented in `docs/version-designs.md`.

#### Version 14

*Version 14* keeps the core and layout of *Version 3* but the page design takes inspiration from the cinematography and set design of the film, *Reflections in a Dead Diamond*. The agent may alter the layout and flow of the page if it improves the thematic fit. However, the interpreter and sieve programs should remain untouched. The finalized design will likely differ from this open specification and will be documented in `docs/version-designs.md`.

#### Version 15

*Version 15* is a skeuomorph of a physical working space. It draws from the warm, tactile feeling of *Version 4* and *Version 6*. It breaks with the layout of *Version 3* and instead the design organizes materials in books, notebooks, decks, etc. This version keeps and expands on the miscellanea from *Version 6*. It also adds more music decks and a reel-to-reel player to play generated sieves. Note that the audio code should be `scripts/` as it may be reused by other versions.

#### Version 16

*Version 16* is a skeuomorph of a digital working space. It draws from the vintage computer desktop of *Version 8*. It breaks with the layout of *Version 3* and instead the design organizes materials like *Version 8* . It also adds more music decks and a player program to play generated sieves. This design also adds some of the miscellanea from *Version 15* as digital documents. Since this version relies on the metaphor of a computer desktop, the punch cards are superfluous and should be dropped in favor of a traditional buffer editor. The language can remain as FORTRAN.

#### Version 17

*Version 17* takes the design and style of *Version 9* but drops the framing device of Xenakis's sieves. Instead, this version implements a puzzle game centered around the mechanics of punch cards. The puzzles are intended to help the user learn how to write and use punch cards.

#### Version 18

*Version 18* combines the design of *Version 10* and *Version 14*. More concretely, it applies half-toning to the graphics of *Version 14*. This version also drops the framing device of Xenakis's sieves. Instead, it takes the more experimental decks from *Version 11* and *Version 12* and expands on them. Experimental card decks are framed by code art and computation theory.

#### Version 19

*Version 19* combines the design of *Version 15* and *Version 18*. *Version 18* is reintroduced as a magazine within the virtual desktop of *Version 15*. The cards from *Version 18* are included as actually usable programs in this version. *Version 19* tightens the virtual desktop concept from *Version 15* and cleans it up. This version also takes the efficiency of the code into consideration, taking care to clean up and refactor the code that gets imported into its implementation from past versions.

#### Version 20

*Version 20* combines *Version 16* and *Version 17*, where the puzzles now exist within the fantasy computer desktop. *Version 20* refines the graphics of *Version 16* by implementing some of the design language from *Version 17*. This version also takes the efficiency of the code into consideration, taking care to clean up and refactor the code that gets imported into its implementation from past versions.

#### Version 21

*Version 21* combines *Version 19* and *Version 20* into an unified workspace. Namely, a computer is added to the desk, enabling use of the simulated computer desktop. This iteration allows each half of the workspace to have its own style established in previous versions. This version also takes the efficiency of the code into consideration, taking care to clean up and refactor the code that gets imported into its implementation from past versions.

#### Version 22

*Version 22* builds on *Version 21* and removes the separation of styles between the desk and computer. This version moves the computer style to a more modern UI, using vector graphics instead of dithered pixel art.

#### Version 23

*Version 23* builds on *Version 21* and removes the separation of styles between the desk and computer. This version moves the room style to pixel art. It also revises the computer UI from 3-bit dithering to full color pixel art.

#### Version 24

*Version 24* combines the pixel-art look of *Version 23* with the variation feature from *Version 22*.

#### Version 25

*Version 25* is a perfection and expansion of *Version 24*.

### Gallery

While the gallery page is separate from the versioned pages, it should be style as if it existed within the fiction of *Version 25*. The gallery should be accessible from a folio in the bookshelf of *Version 25*.

### Genealogy

While the genealogy page is separate from the versioned pages, it should be style as if it existed within the fiction of *Version 25*. The genealogy should be accessible from a folio in the bookshelf of *Version 25*. The genealogy of the pages should be derived from the notes above.
