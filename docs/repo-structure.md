# Repository Structure

```
.
├── index.html            Gallery — site entry point (/), links to every version
├── README.md             Short summary of the project + link to the live site on Vercel
├── AGENTS.md             Context for the coding agent (loaded every run)
├── genealogy/
│   └── index.html        Genealogy page (/genealogy), reads scripts/versions.js
├── v01/
│   ├── index.html        Version 1 (/v01)
│   └── style.css         Version 1 styles only
├── v02/
│   ├── index.html        Version 2 (/v02)
│   └── style.css
│   ...                   (v03 … v25, same shape, except v06)
├── v06/
│   ├── index.html
│   ├── style.css
│   └── assets/           Marbled and Morris-style paper images (JPEG), used only by v06
├── v25/
│   ├── index.html        Version 25 (/v25)
│   └── style.css
├── css/
│   └── base.css          Shared reset + design tokens (kept minimal)
├── fonts/
│   ├── fonts.css         @font-face rules for every bundled font
│   └── <family>/         WOFF2 files (Latin subset) + the font's LICENSE (SIL OFL)
├── scripts/
│   ├── hollerith.js      Character ↔ punch-code tables, card encode/decode
│   ├── fortran.js        Deck split, scanner, parser, interpreter, FORMAT
│   ├── tape.js           Punched cards → notes, and a Web Audio tape player (reel-to-reel)
│   └── versions.js       Genealogy data (id, parents, note, status)
├── tests/
│   ├── index.html        Test runner: open in a browser, no tools needed
│   ├── harness.js        Tiny test harness
│   ├── hollerith.test.js
│   ├── fortran.test.js
│   ├── sieve.test.js     Tests for the sieve deck (Fortran.samples[4])
│   └── tape.test.js      Tests for the pure parts of tape.js
└── docs/
    ├── fortran-cards-spec.md   FORTRAN simulator spec
    ├── sieve-solver-spec.md    Sieve generator deck spec
    ├── tape-spec.md            Tape card format and player API
    └── version-designs.md      Finalized design of each themed version (v04–v14)
```

## Notes

- Each version is a folder with its own `index.html`, so Vercel serves clean URLs (`/v01`, `/v02`, …) with no build step.
- Every version loads the shared engine from `scripts/` and, optionally, `css/base.css`, using relative paths (`../scripts/...`, `../css/...`) so pages also work when opened directly from disk.
- Per-version look lives in each version's own `style.css`; `css/base.css` holds only a reset and shared tokens.
- `v06/assets/` is the one exception to the two-file shape. Two of its images are sources kept for reference: the page uses `marble-nonpareil-tile.jpg` and `morris-acanthus-band.jpg`, made seamless from `marble-nonpareil.jpeg` and `morris-acanthus-border.jpeg`.
- Some versions add page-only sample decks after the engine's samples (v11, v12); they live in that version's `index.html`, and `scripts/` is not changed for them.
- Fonts are bundled, not loaded from a font service: themed versions link `../fonts/fonts.css` and put a bundled family first in each stack, so every visitor sees the same type regardless of what is installed. Only open-licensed (SIL OFL) fonts go in `fonts/`, each with its LICENSE file.
- `scripts/versions.js` is the single source of genealogy data, read by both the gallery and the genealogy page.
- Every version links back to `../` (the gallery).
- The sieve generator is a FORTRAN deck in `scripts/fortran.js` (`Fortran.samples`), not a separate engine.
- `scripts/tape.js` is shared audio code: a version that plays cards loads it after the engine (`../scripts/tape.js`). It turns punched cards into notes (see `tape-spec.md`).
- `tests/index.html` runs the engine tests in the browser. Like everything else it needs no build step.
- `docs/` holds the specs the agent works from. `docs/version-designs.md` records the finalized design of each themed version, which is more specific than the briefs in `AGENTS.md`.
