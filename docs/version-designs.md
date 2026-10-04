# Version Designs (v04–v18)

`AGENTS.md` gives each themed version a short brief. This document records the finalized design of each one, which is more specific than its brief. Where the two differ, this document describes what the page actually is.

## Rules shared by every themed version

- **Core.** Every version keeps the Version 3 functional core: the editor, card viewer, output, stacker and sample menu, with the same element IDs and the same tab behavior. `scripts/` (the interpreter and the sieve deck) is never changed. The exceptions to the tabbed layout are v08, v15 and v16 (see below). v16 also drops punched cards for a text buffer.
- **Flow.** Layout and flow follow the theme. The About section is split into separately viewed parts (pages, frames, sheets, rooms, scenes or slips), and all of its prose stays available and keyboard accessible.
- **Interpretation.** Themes are expressed through mood, materials and design language, not through literal props or illustrations of objects.
- **Document-based versions** (v04, v05, v06, v09, v10, v11) use vertical tabs and show only things that could physically exist in their medium. Interactive controls are styled as plausibly as the medium allows.
- **Legibility.**
  - Body text is at least 16 px, with line-height of at least 1.4 and lines of no more than about 80 characters.
  - Body text contrast is at least 4.5:1, measured against the real background, texture included.
  - Display and handwriting faces are used only for headings, labels and short captions.
  - Body text is never rotated, skewed or warped.
  - No texture or pattern sits behind body text.
  - Textures never move.
- **Fonts.** Only SIL OFL fonts bundled in `fonts/` are used (see `repo-structure.md`).
- **Page-only decks.** A version may append its own sample decks after the engine's five, inside its own `index.html` (v11, v12, v15, v16).
- **Sound.** A version that plays cards uses the shared `scripts/tape.js` (see `tape-spec.md`): v15's recorder and v16's Player.
- **Version numbers.** No page names its own version; the URL identifies it.

## Per version

| Version | Brief (`AGENTS.md`) | Final design |
|---|---|---|
| **v04** | Thermal paper and typewritten documents; mostly monochromatic, serif fonts, slight yellowing, scanner dust | A **black-and-white photocopy** of a working file, with no yellowing. A typed folder label sits on the folder front. Folder tabs stick out of the left edge with labels typed vertically. About is a typed memorandum, one sheet per section, with a pencil-circled page number. The Editor is a printed FORTRAN coding form, and Output is a typed run report with narrow thermal-paper strips. The mess is restrained: toner specks, fibre, a faint drum streak, a staple, tape. Fonts: Courier Prime, Gelasio, IBM Plex Mono. |
| **v05** | Microfiche; high contrast, monochromatic, grainy, ragged | An enlarged negative fiche with an eye-readable header strip. The tabs are the fiche's row index (A–D) down the left edge. About is row A, a strip of 7 frame thumbnails with one frame read at a time. Output is row D, in the style of computer-output microfilm. The film has multi-scale grain, scratches and dust, while the frame being read stays sharp. Neutral greys only. Fonts: Barlow Condensed, Charis SIL, IBM Plex Mono. |
| **v06** | Scrapbook; an eclectic collection of paper artifacts | A **maximalist** ring-bound album with leather spine and corners and label-maker-tape tabs on the page edge. **Image assets in `v06/assets/`:** marbled papers (stone desk, nonpareil cover boards, curl scrap, Spanish jacket) and Morris-style prints (Strawberry Thief, Willow Bough, acanthus frieze). About pages are glued-in papers. **Eight extra album pages (A–H) of Xenakis miscellanea:** *Metastaseis* and the Philips Pavilion, *Pithoprakta*, arborescences, *Nomos Alpha*, three sieves, UPIC and *Mycènes Alpha*, *Polytope de Montréal*, and an ST printout with *Formalized Music*. Handwriting is used only for captions. |
| **v07** | Cray-2; bold colors and geometric shapes | Drawn from the **machine's industrial design, not a picture of it**. The header band of slabs comes from the 14-column C geometry (20° spacing, widths proportional to cosine). The palette is **anchored on red**, with smoked black, copper and aluminium and no blue. **Everything is left-aligned.** The tabs sit on a rail, and the panels are smoked-glass frames. About is a "module stack" of boards, one section at a time. Fonts: Manrope, IBM Plex Mono. |
| **v08** | Vintage computer graphics; ordered dithering, at most 8 steps per channel | A **1-bit black-and-white classic Macintosh (System 1–7) desktop** with an 8×8 Bayer dither. **It drops the tabbed layout entirely** and is the one version that does not keep Version 3's layout. It has a menu bar with working menus, desktop icons, and windows that open, close, drag and come to the front. The About folder holds 7 documents, and there is a Trash and an alert dialog. It has a full keyboard and focus model, full-screen sheets on narrow screens, and a static fallback without JS. Fonts: Pixelify Sans (menus and titles), Atkinson Hyperlegible (body), IBM Plex Mono. |
| **v09** | Swiss/International style, with hatching instead of color | A strict 12-column grid, flush-left, black and white only, with **a 7-step hatch tonal scale** from single hatching through cross, triple and quadruple to solid, plus a hatch ramp. The tabs are a numbered thumb index down the right edge of the sheet. About is 7 sheets (1.1–1.7), each with an engraved-style hatched figure. Hatching is never behind text. Fonts: Inter (standing in for Helvetica), IBM Plex Mono. |
| **v10** | Half-toning | A **press-proof sheet, not a newspaper**. A CMYK cover plate is screened at the classic angles (C 15°, M 75°, Y 0°, K 45°), with crop and registration marks and a colour bar. Die-cut thumb-index tabs sit on the fore-edge, one per process ink. About is a contents list plus pages whose duotone screen coarsens page by page. There is a little paper grain. Fonts: Oswald, Source Serif 4, IBM Plex Mono. |
| **v11** | Dada | A ransom-note title and black plus one red. The tabs are pasted paper slips down the left edge. About works like Tzara's hat: "Draw a slip" pulls sections in random order, with an index for picking one. Grain and mess: tears, glue stains, off-register prints. **Page-only decks:** *Tzara's hat*, *Erratum musical* and *3 standard stoppages*. Prose stays plain. Fonts: Archivo Black, Bodoni Moda, Playfair Display, Arvo, Courier Prime, Gelasio. |
| **v12** | The look and feel of the *Backrooms* movie; a liminal space, an echo of the past | **Mood, not props** (no doors, no camcorder): a faded yellow wall with an off-centre column. **The title and headings fade into echoes in shifting typefaces,** while body text stays in one face (Work Sans). Echo faces: Libre Caslon Text, Cutive Mono, Overpass, Instrument Serif, Old Standard TT. About is rooms that loop and remember visits, and small details are slightly off. **Page-only decks:** *An echo in an empty room*, *I am sitting in a room* (after Lucier), *Erosion*, *The corridor*. |
| **v13** | The look and cinematography of German expressionist films | **Curvature and flow balanced against angular tension.** A hard diagonal beam falls alongside soft light pools, and the page is tinted per tab (amber, steel blue, green, rose). The tabs are a staircase with sagging edges, and the panels are pointed, bowed arches. The painted set has a spiral sky, a winding street, spires and a hand shadow. About is numbered intertitles. **Grain and wear are static:** film grain, canvas weave, paint mottling. Fonts: Big Shoulders Display, Libre Caslon Text. |
| **v14** | The cinematography and set design of *Reflection in a Dead Diamond* (2025, Hélène Cattet and Bruno Forzani) | **Bold, slightly odd 1960s design, not gems.** A split-screen opening sets a huge italic Didone title (Playfair Display) on black beside an orange field with a black disc and an op-art target. Vertical tabs sit on a colour band that changes per tab. About plays like a title sequence, with giant cropped numerals, a different op-art pattern for each section, and a wipe. Body font: Jost. |
| **v15** | A skeuomorph of a physical working space, warm and tactile like v04 and v06; breaks with v03's layout; organizes materials in books, notebooks, decks; keeps and expands v06's miscellanea; adds music decks and a reel-to-reel player | A **walnut desk with a green leather top**; no tabs. Each object holds part of the site:
- **Brass nameplate:** "A desk for cards and sieves", the page's only title, with no introduction.
- **Red cloth reference manual:** the About text, 9 chapters on a two-page spread, including new chapters on the music decks and the tape recorder.
- **Marbled portfolio:** the Xenakis miscellanea A–N, v06's eight plus six new: the *Achorripsis* matrix, *Analogique A* and *B* screens, *Concret PH*, *Terretektorh*, *Polytope de Cluny*, *Polytope de Persépolis*. The four atmospheric sheets (G, K, M, N: Montréal, *Concret PH*, Cluny, Persépolis) are imagined photographs in `v15/assets/`, mounted as prints and captioned as imagined renderings, not photographs of the works; the rest are drawings.
- **Oak card tray:** all 10 decks as banded stacks, in Programs and Music sections; picking one loads it.
- **Coding-form pad:** the editor.
- **Card on the desk:** the card viewer.
- **Out tray:** green-bar printout, job ticket, folded listing and a wooden stacker box.
- **Teak reel-to-reel recorder:** built on the shared `scripts/tape.js`. It threads the stacker, plays bare sieve members as rhythm or scale, and has turning reels, a counter, transport keys, tempo and a 7½/15 ips speed switch.

The manual and portfolio open as modal dialogs, with focus managed and Escape to close. The page uses images from `../v06/assets/` and its own photographed materials in `v15/assets/`: walnut, green leather, oak, teak, red book cloth, brushed plate and laid paper. Each is a seamless tile with its baked-in shading flattened. **Things on the desk:** cut-out photographs (WebP with transparency, the backdrop's own shadows removed, one CSS shadow from the upper left), placed round each station on wide screens only (at least 1100 × 700) and hidden from assistive technology:
- the overview: coffee, a pen, paper clips and a banded stack of punched cards;
- the coding form: an inkwell and a stamp pad, in a gutter that appears only from 1600 px, so the form keeps all 80 columns in view;
- the card viewer: a loupe and a banded stack of punched cards;
- the printout: pencils and clips, under the ticket column;
- the stacker: a pen, under the note;
- the recorder: the tape box and a cup, under the case.

**Page-only music decks:** *Sieve scale*, *Two rhythm sieves*, *Stochastic cloud* (after *Achorripsis*), *Markov melody* (after *Analogique*), *String glissandi* (after *Metastaseis*), punched as tape cards. Fonts: Gelasio, Libre Caslon Text, Bodoni Moda, Courier Prime, IBM Plex Mono, Caveat, Barlow Condensed. |
| **v16** | A skeuomorph of a digital working space, drawn from v08's desktop and organized like it; adds music programs, a player program and some of v15's miscellanea as digital documents; punched cards are dropped for a traditional buffer editor; the language stays FORTRAN | v08's classic Mac desktop and window manager, grown into a **fully digital** workspace on a **3-bit colour screen**.
- **Palette:** eight colours (R, G and B each 0 or 255); every tone comes from dithering each channel separately against the same 8×8 Bayer matrix.
- **One screen pixel (2 CSS px) for everything:**
  - dither cells, 2 px rules and borders
  - drawn boxes, radios, scroll arrows and check marks
  - 32×32 icons shown at 64 px
  - pictures and the piano roll, rasterised at screen resolution and scaled 2× pixelated
  - window positions and sizes, kept on even pixels
- **Fonts:** bitmap faces only.
  - Fusion Pixel 10px Proportional for chrome and prose; Fusion Pixel 10px Monospaced for the editor, code and output.
  - Both have a 0.1 em design pixel and are set at 20 px, so one design pixel equals one screen pixel.
  - The mono face is 10 CSS px per column, and line heights are multiples of 4 px.
  - Headings stand out by inversion, rules or spacing, and emphasis by underline.
  - The pictures' lettering uses the same faces, embedded in each SVG.
- **Colour roles:**
  - a steel-blue desk; white windows with black chrome
  - lilac folders and scroll tracks; blue selection and focus
  - yellow behind editor warnings
  - red for the column-72 margin, page breaks and the playhead
  - green on black for the Player's time
  - text only on flat colours that pass 4.5:1
- **Icons:** Workspace HD, Read Me, About, Programs, Xenakis miscellanea, Results, Editor, Player, Gallery, Trash.
  - **About:** "A short history of FORTRAN" is the only place cards appear, in the past tense; "Using the workspace", the language and the music documents are all digital.
  - **Programs:** page-local copies of the 5 samples plus 7 music programs (v15's five, *Brownian melody* after *Mikka*, *Arborescence* after *Evryali*). Their comments are digital and `PUNCH` is written as `WRITE (7,…)`, which writes to the program's output; the output is identical to the originals, and the sieve program's logic and data are unchanged.
  - **Xenakis miscellanea:** 7 pictures, rasterised from v15's coloured SVGs and dithered, plus the ST printout as text.
  - **Trash:** holds replaced texts, with Put Back.
- **Editor:** a `<textarea>` buffer with a gutter, a field ruler, margins at 72 and 80, line, column and field status, over-72/80 warnings, Tab to columns 7 and 73, Run, Revert and Download. There is no storage.
- **Results folder:** Printout, Job Log, Listing, and the program's **Output** (play, replace or append to the editor as data, copy, download). The engine's log text is translated for display (line, data line, output); no unit numbers or card terms are shown.
- **Text is never dithered:** disabled controls are solid blue with a dotted 2 px frame or rule. Picture labels are drawn after dithering, in solid colours on white patches.
- **Player:** on the shared `scripts/tape.js`, with a 1-bit-per-channel piano roll from pale blue (quiet) to red (loud), a red playhead (click or arrow keys to seek), transport, tempo, Normal/Double speed, and a Rhythm/Scale switch disabled for note-record files. |
| **v17** | v09's design and style, without the Xenakis framing; a puzzle game about the mechanics of punched cards, meant to teach writing and using them | v09's Swiss grid in black and white, with Inter and IBM Plex Mono. The masthead is a giant "80" beside "columns." The 7-step hatch scale now codes **difficulty**, on each tab edge, each sheet's head band and a 10-cell progress index; it is never behind text. A numbered thumb index on the right holds sheets 00–10 and a **Workbench** (the full simulator with four samples, no sieve). The ten sheets:
1. read a card
2. punch a character (a digit, then one letter from each zone, then a sign; keypunch off)
3. punch a word
4. the card's fields
5. continuation
6. the dropped deck (re-sort by columns 73–80 with a one-column-per-pass sorter)
7. data cards
8. FORMAT and carriage control
9. punch, then feed back to a second program
10. a deck of your own

Every answer is checked with the real engine (`decodeCard`, `punches`, `run`), with explained feedback, hints and a solved stamp. Progress lasts for the session only; nothing is stored. The card is a 13-row ARIA grid: each cell announces its row, column and state, arrow keys move, Space toggles, and from sheet 4 typing punches like a keypunch. |
| **v18** | v10's design combined with v14's: half-toning applied to v14's graphics; no Xenakis framing; the experimental decks of v11 and v12, expanded and framed by code art and computation theory | **v14's layout grammar** printed through **v10's halftone**:
- **v14's grammar:** the black split screen with a huge italic Playfair "FORTRAN", a colour band with vertical tabs that changes per tab, About as a title sequence with cropped numerals, op-art swatches and a wipe, and Jost body text.
- **v10's halftone:** a canvas plate renderer with round dots on rotated CMYK screens (15°/75°/0°/45°) plus a spot orange at 60°, area-true dot sizes with about 12% dot gain, fractional misregistration, multiplied overlaps (moiré) and paper specks.
- **What is screened:** the title's orange field, black disc and magenta target; About's numerals and its 9 op-art swatches (rings, stripes, quadrants, bars, crossed rings, warped checker, rays, nested squares, spiral); the band's rings; the cards' zone rows and the viewer card's shadow.
- **Large surfaces are halftone print:**
  - the band, a screen in the current tab's ink fading toward its foot, with black rings overprinted
  - the title plate, which breaks into dots at its edges
  - the lede ground, where yellow and cyan overprint into green
  - a tall colour block per About section
  - the printer's yellow frame
  - a magenta and cyan footer
- **Halftoned display headings (40 px and up):**
  - *FORTRAN* is knocked out to paper, with a yellow dot ramp over a magenta shadow printed out of register.
  - Panel and section titles are filled with a black screen of at least 88% coverage over an offset ink plate.
  - Dots are clipped to the glyph outlines, effective contrast is 5.9:1 or better, and the real heading text stays in the DOM, transparent.
- **Screen pitch (CSS px):**
  - op-art swatches about 1.6–2.2, and the opening target and band rings 3, so the spirals and rings read as smooth curves
  - large fields 4–8; headings at font size ÷ 30
  - plates rendered at device pixel ratio
- **Text:** body text, controls, tables, the editor and output sit only on flat plates of ink or paper.
- **About:** code art and computation theory, sourced:
  - Nees (Stuttgart, February 1965); Julesz and Noll (Howard Wise, April 1965); Nake and Nees (Niedlich, November 1965)
  - Knowlton and Harmon's *Studies in Perception I*; Cybernetic Serendipity (1968)
  - Fluxus instructions; LeWitt (1967)
  - Turing (1936); Radó (1962); Lin and Radó; Brady
  - Wolfram (1983); Cook (2004); Gardner's Life column (1970)
  - Collatz; Pollard's rho method (1975)
- **Decks:** 17 in the menu: the engine's samples 1–4 (no sieve); the seven v11 and v12 decks unchanged; and six new ones, each checked against a JS reference:
  - *Studies in perception*: a 64×32 ordered-dither line-printer picture
  - *Rule 30*
  - *Life*: a glider, blinker and block on a wrapping grid
  - *A busy beaver*: a table-driven Turing machine; 3-state: 14 steps, six 1s; 4-state: 107 steps, 13 ones
  - *The 3x+1 problem*: 27 takes 111 steps and peaks at 9232
  - *Euclid, read aloud*: prints its own instructions and punches a 16-card program that runs

Fonts: Playfair Display, Jost, IBM Plex Mono. |
| **v19** | v15's design combined with v18's: v18 returns as a magazine on v15's desk; v18's cards become usable programs; v15's desk tightened and cleaned up; the code imported from earlier versions cleaned up and refactored for efficiency | v15's working desk, **refurnished and drawn as an architecture review would show it**: a plaster wall, one oak shelf on hairline steel rails, a thin walnut desk on a black steel trestle with an architect's lamp, drawn straight on as an elevation in quiet materials (plaster, oak, walnut, linen, stoneware, aluminium), with soft contact shadows and one muted accent, a terracotta. Things are named as plates are captioned: small tracked capitals on the plaster under the desk, each on a hairline leader. Type: Instrument Serif for display, Jost in small tracked capitals for labels, Source Serif 4 for reading, IBM Plex Mono for cards and code. Buttons are hairline outlines with square corners.
- **The room** (the first station) is one drawing set in em, sized to fit the screen; below a readable size it becomes a list of what is on the shelf and the desk. The room is the way round: the list of places is kept in a *Menu* in the top corner (with the link back to the gallery), and inside a station a *Back to the room* button sits beside it.
  - **The bookshelf:** the reference manual in three linen volumes (FORTRAN, chapters 1–5; Sieves, 6–7; Music and tape, 8–9). Each spine opens the manual at its first chapter; the manual's contents are grouped by volume.
  - **The stack on the desk:** the magazine stood on a pile of folders, the top one the Xenakis miscellanea.
  - **The deck box:** a walnut card box with a brass card frame; its decks stand behind tabbed dividers (Programs, Music, From the magazine). It opens the coding form with the focus on the box.
  - The **coding form** on a clipboard, the **out tray**, a low tray of black steel, and the **tape player**, a reel-to-reel machine in a walnut case.
- **Inside a station** the desk is seen from above, pale oak under the papers: the manual in a slate linen case, the miscellanea in an open folder, the coding form beside the walnut deck box with the card in hand under it, the out tray (fan-fold printout, a buff job ticket with a terracotta band, the listing, the stacker in a walnut box) and the tape player (brushed aluminium deck plate, pale keys, a terracotta play key and run lamp).
- **The magazine:** v18 printed as a saddle-stitched art-and-computing magazine, *FORTRAN*, in v18's halftone (CMYK screens at 15°/75°/0°/45° and a spot orange at 60°, dot gain, misregistration, overprint, specks). Seven openings: the cover, contents and an editors' note, one article for each of v18's scenes on code art and computation theory (pictures from programs; chance and instructions; machines that follow rules; loops and returns), and a catalogue of the thirteen decks. Body text sits only on flat paper or ink; only display type of 40 px and up is screened. v18's first five scenes are left out: the manual already holds them.
- **v18's decks as programs:** the deck box has a third group, *From the magazine*, with v18's thirteen decks; every deck the magazine discusses has a button that puts it on the coding form, and they run, print, punch and thread like any other deck.
- **Code** (classic scripts, no build): `decks.js` (the music and magazine decks) and `drawings.js` (the miscellanea's drawings, set into a sheet the first time it is shown) hold data; `desk.js` the stations, the pager and the deck registry; `form.js`, `out.js` and `recorder.js` the objects; `halftone.js` a reusable plate renderer refactored from v18 (plates drawn in batched paths, cached by size and only when visible) and `magazine.js`/`magazine.css` the magazine. The room is drawn in CSS only; the miscellanea's four photographs come from `../v15/assets/`. The editor, card drawing and job code that v15 and v18 each carried exist once; the form's cards share one listener of each kind; the card in hand redraws at most once a frame; each punched card in the stacker is one canvas. |
