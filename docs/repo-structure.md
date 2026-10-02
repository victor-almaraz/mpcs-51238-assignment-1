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
│   ...                   (v03 … v25, same shape)
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
│   └── versions.js       Genealogy data (id, parents, note, status)
├── tests/
│   ├── index.html        Test runner: open in a browser, no tools needed
│   ├── harness.js        Tiny test harness
│   ├── hollerith.test.js
│   ├── fortran.test.js
│   └── sieve.test.js     Tests for the sieve deck (Fortran.samples[4])
└── docs/
    ├── fortran-cards-spec.md   FORTRAN simulator spec
    └── sieve-solver-spec.md    Sieve generator deck spec
```

## Notes

- Each version is a folder with its own `index.html`, so Vercel serves clean URLs (`/v01`, `/v02`, …) with no build step.
- Every version loads the shared engine from `scripts/` and, optionally, `css/base.css`, using relative paths (`../scripts/...`, `../css/...`) so pages also work when opened directly from disk.
- Per-version look lives in each version's own `style.css`; `css/base.css` holds only a reset and shared tokens.
- Fonts are bundled, not loaded from a font service: themed versions link `../fonts/fonts.css` and put a bundled family first in each stack, so every visitor sees the same type regardless of what is installed. Only open-licensed (SIL OFL) fonts go in `fonts/`, each with its LICENSE file.
- `scripts/versions.js` is the single source of genealogy data, read by both the gallery and the genealogy page.
- Every version links back to `../` (the gallery).
- The sieve generator is a FORTRAN deck in `scripts/fortran.js` (`Fortran.samples`), not a separate engine.
- `tests/index.html` runs the engine tests in the browser. Like everything else it needs no build step.
- `docs/` holds the specs the agent works from.
