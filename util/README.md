# util: the offline tools behind the pictures

The site itself is plain HTML, CSS and JavaScript with no build step: every picture, plate and
generated passage it uses is committed in its version's folder. This folder holds the Python
tools that drew and assembled those files. Nothing here is loaded by a page; run them only to
change or regenerate an asset, then commit what they write.

Each folder is named for the version whose work it was made for, and several build on the ones
before (v24 and v25 import v23's drawing and lighting code, v23 cuts its sprites from v19r's
seeds). Keep the folders side by side: the scripts find one another by relative paths.

## Requirements

- Python 3.11 with `numpy`, `Pillow` and `fontTools` (with `brotli`, to read the bundled
  `.woff2` pixel fonts in `../fonts/`).
- Google Chrome, for the scripts that render SVG or take screenshots (`v19r/render.py`,
  `v22/shot.py`, `v23/shot.py`, which run it headless with a scratch profile). `fx/` drives
  Firefox through Marionette instead.
- A local server at the repository's root for the scripts that read a running page
  (`python3 -m http.server 8000`).

Paths are relative: each script that needs them sets `UTIL` (this folder) and `REPO` (the
repository) from its own location. Scripts write their proofs, contact sheets and renders beside
themselves; `.gitignore` keeps those out of the repository.

## v25: the room, its corner and its papers

The current pipeline. Run from `v25/`:

| Script | Writes | What it does |
| --- | --- | --- |
| `build4.py` | `v25/assets/<time>/` (deletes and rewrites them) | The whole room at three times of day (morning, evening, night) and in each light of the lamp (task, angle, dome, ceramic, off): the backdrop for every wallpaper, every sprite, the loops in `anim/`, the second wall (`part2.py`), all lit and cut to one palette of 96 colours (`palette-v24.json`). About four minutes. Also writes `grounds.json`. |
| `sync_grounds.py` | `v25/decor.js`, `v25/style.css` | After `build4.py`: copies each paper's ground colour (`grounds.json`) into the room's script and stylesheet. |
| `part2.py` | (a proof, `part2-proof.png`) | The reading corner, round the corner from the desk: wall, bookcase and books, cabinet, tank and fish, chairs, cat clock, metronome, camera, album, pocket game, side table and record player, the turn tabs and their cursors, and its light. Imported by `build4.py`; run alone, it draws a proof. |
| `seeds25.py` | `seeds25/`, `v25/assets/st/rec-deck.png`, `rec-deck-playing.png`, `pomo-body.png` | The record player and the tomato timer, drawn as SVG in their own pixels, rendered large through headless Chrome (`../v19r/render.py`) and cut cell by cell to each drawing's own hue-shifted ramps: the two room sprites (unlit; `part2.py` and `build4.py` read them from `seeds25/`, with the record's turning frames) the record player's two pictures from above (at rest and playing), and the tomato's body, over which `timer.js` draws its band of minutes. Run it before `build4.py`. |
| `art.py`, `sheet.py` | | The swappable things (prints, plants, lamps, mugs, papers, the switch), the reader and printer, the UPIC, the magazines' covers on the shelf. Imported by the builds. |
| `build.py`, `build2.py`, `build3.py`, `light24.py` | | v24's backdrop, the lamp's light for each state, the loops (reels, screen, steam, sway), the light of each time of day. Imported by `build4.py`. |
| `build_mags.py` | `v25/index.html` (the magazine station) | Sets every magazine from its text in `text/<issue>.md` (cover, contents and editors, three or four articles, catalogue), with its rack. Reads `text/magazine.md`, `event.md`, `gesso.md`, `cons.md`, `silver.md`. |
| `mag_plates.py`, `mag_plates2.py`, `mag_plates3.py` | `v25/assets/st/` | The magazines' plates and cover fields, drawn in pixels: Moiré; Event and Gesso; Cons and Silver. |
| `album_pics.py` | `v25/assets/st/album-*.png` | The photo album's black-and-white prints and Polaroids, one to a page. |
| `build_folio.py` | `v25/index.html` (the folio of influences) | Sets the folio's sheets from `text/folio.md`. |
| `desktop_pic.py`, `karawane_pic.py`, `tzara_pic.py`, `pixart.py` | `v25/assets/pics/` | The computer's desk picture (Persepolis), Ball's *Karawane* and Tzara's hat, drawn in pixels and graded for the screen. |
| `gesso/build.py` | (a JavaScript array) | Builds the Gesso decks and writes them as a JavaScript array. |
| `proof_times.py` | `times.png` | A proof of the room at the three times of day. |

`text/` holds the magazines' sources: one Markdown file per issue in the structure
`build_mags.py` reads (`# COVER`, `# EDITORS`, `# CONTENTS`, `# ARTICLE 01` …, `# CATALOGUE`;
`[deck: id | name]` puts a deck's button in the text). The `decks-*.js` files are each issue's
decks as written and checked; they are copied by hand into `v25/decks.js`. `BRIEF.md` and
`BRIEF-MAG.md` are the briefs the texts were written to (voice, spelling, sourcing, the deck rules).

A typical change to the room: edit `part2.py` or `art.py`, run `python3.11 part2.py` to proof
it, then `python3.11 build4.py && python3.11 sync_grounds.py`, and look at the page.

## The gallery and the genealogy

Run from `gallery/`, with the local server running:

- `thumbs.py [v01 …]`: screenshots each version and cuts it to the gallery's print (192 × 120, in the last room's palette), into `../../assets/rooms/`.
- `build_pages.py`: sets the gallery (`../../index.html`) and the genealogy's written lineage (`../../genealogy/index.html`) from `scripts/versions.js`. Edit the data there, then run this.

## Earlier versions

- **v24/**: v24's room (its own copies of the build scripts; they write `v24/assets/`).
  `sheet.py` and `proof_times.py` draw proofs.
- **v23/**: the pixel-art pipeline v24 and v25 rest on. `pix.py` (pixelating, palettes, clean-up),
  `room.py` and `room2.py` (the room and its sprites, cut from `../v19r/seeds/`), `drawn.py`
  (thin and leafy things drawn directly in pixels; `drawn_6ppe.py` is the earlier six-pixel
  version), `light.py` and `relight.py` (the evening light and the palette), `pics.py` and
  `screen_grade.py` (the computer's pictures and their grading), `stations.py` (the stations'
  pictures), `shot.py` (headless Chrome). `unlit/` holds the unlit sprites the builds light,
  and the `.json` files are its palettes.
- **v22/**: `screen.py` and `screen2.py` draw v22's computer pictures as SVG
  (`v22/assets/screen/`); `shot.py` screenshots a page.
- **v19r/**: the vector drawings of v21's and v22's room, made as SVG and rendered through
  Chrome (`render.py`): shelf, books, desk things, tape machine, computer, plants, wallpapers,
  the miscellanea's drawings, the magazine's plates, and the swappable variations (`decor.py`).
  `mcm.py` and `mcm2.py` are the drawing vocabulary. Numbered files (`shelf2.py`, `comp4.py` …)
  are successive passes at the same drawing, kept as they were. `seeds.py` renders the clean
  seeds in `seeds/` that v23 pixelates.
- **fx/**: `dada_gen.py` draws v20's two chance pictures (the stoppages and Arp's squares)
  offline; `gen.py` saves the pictures v20's page draws, through Firefox (`mn.py` is a minimal
  Marionette client; pass this folder's path as the first argument).
- **ev/**: `gen.py` built the Event decks as card images (its output path is the argument).
- **eph/**: `key.py` cuts photographed ephemera out of their green backdrops; its source
  photographs are not kept here.
- **bg/**: experiments in hatching and dithering a night picture; they write into the current
  folder.
- `sim.py` simulates the busy beaver the magazine's deck runs; `dec.py` and `dec8.py` decode a
  region of a PNG for inspection.
