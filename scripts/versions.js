/* The genealogy of the site: every version, the versions it was made from, and what it was.
   The single source for the gallery (../index.html) and the genealogy (../genealogy/), taken
   from the briefs in AGENTS.md. One global, VERSIONS: a list of
     { id: 'v07', title, parents: [ids it builds on], borrows: [ids it takes a part from],
       note: what it is, in a sentence, status: 'complete' or 'in progress' }
   "parents" are the versions a brief names as its base or combines; "borrows" the ones it
   names for a single part (a set of decks, the miscellanea, a feature). A second global,
   CHAPTERS, groups the versions into the four stretches of the work, in order:
     { id, numeral, title, first: id, last: id, note } */

var VERSIONS = [
  { id: 'v01', title: 'The working core', parents: [], borrows: [], status: 'complete',
    note: 'The interpreter and the sieve solver made to work, in black text on white with the least styling.' },
  { id: 'v02', title: 'Sub-pages', parents: ['v01'], borrows: [], status: 'complete',
    note: 'The one long scroll split into sub-pages for the instructions, the editor, the card viewer and the output.' },
  { id: 'v03', title: 'Tabs', parents: ['v01'], borrows: [], status: 'complete',
    note: 'The same four parts behind tabs: the layout every themed version starts from.' },
  { id: 'v04', title: 'Thermal paper and typewriter', parents: ['v03'], borrows: [], status: 'complete',
    note: 'Printouts on thermal paper and typewritten documents: monochrome, serif, yellowed, with scanner dust.' },
  { id: 'v05', title: 'Microfiche', parents: ['v03'], borrows: [], status: 'complete',
    note: 'High contrast, monochromatic, grainy and ragged, as a frame of microfiche on a reader.' },
  { id: 'v06', title: 'Scrapbook', parents: ['v03'], borrows: [], status: 'complete',
    note: 'An eclectic scrapbook of collected paper artifacts, and the first of the miscellanea.' },
  { id: 'v07', title: 'Cray-2', parents: ['v03'], borrows: [], status: 'complete',
    note: 'The bold colours and geometric shapes of the Cray-2 supercomputer.' },
  { id: 'v08', title: 'Ordered dithering', parents: ['v03'], borrows: [], status: 'complete',
    note: 'Vintage computer graphics: ordered dithering with at most eight steps to a channel.' },
  { id: 'v09', title: 'Swiss style in hatching', parents: ['v03'], borrows: [], status: 'complete',
    note: 'The Swiss and International styles, with hatching in place of colour.' },
  { id: 'v10', title: 'Halftone', parents: ['v03'], borrows: [], status: 'complete',
    note: 'Everything printed through a halftone screen.' },
  { id: 'v11', title: 'Dada', parents: ['v03'], borrows: [], status: 'complete',
    note: 'The page as a Dada collage, with experimental decks of chance.' },
  { id: 'v12', title: 'The Backrooms', parents: ['v03'], borrows: [], status: 'complete',
    note: 'The look and feel of the Backrooms: the page as a liminal space, an echo of the past.' },
  { id: 'v13', title: 'German Expressionism', parents: ['v03'], borrows: [], status: 'complete',
    note: 'The look and cinematography of German Expressionist film.' },
  { id: 'v14', title: 'Reflection in a Dead Diamond', parents: ['v03'], borrows: [], status: 'complete',
    note: 'The cinematography and set design of Cattet and Forzani’s film: bold, slightly odd 1960s design.' },
  { id: 'v15', title: 'A physical workspace', parents: ['v04', 'v06'], borrows: [], status: 'complete',
    note: 'A skeuomorph of a desk, its materials in books, notebooks and decks, with music decks and a reel-to-reel player.' },
  { id: 'v16', title: 'A digital workspace', parents: ['v08'], borrows: ['v15'], status: 'complete',
    note: 'A vintage computer desktop with a buffer editor and a player program, and v15’s miscellanea as documents.' },
  { id: 'v17', title: 'A game of punch cards', parents: ['v09'], borrows: [], status: 'complete',
    note: 'v9’s style for a puzzle game that teaches how to write and use punch cards.' },
  { id: 'v18', title: 'Code art in halftone', parents: ['v10', 'v14'], borrows: ['v11', 'v12'], status: 'complete',
    note: 'v14’s graphics through v10’s halftone, and the experimental decks of v11 and v12, framed by code art.' },
  { id: 'v19', title: 'The workspace with a magazine', parents: ['v15', 'v18'], borrows: [], status: 'complete',
    note: 'v15’s desk tightened, with v18 as a magazine on it whose decks can be run.' },
  { id: 'v20', title: 'Puzzles on the desktop', parents: ['v16', 'v17'], borrows: [], status: 'complete',
    note: 'v17’s puzzles inside v16’s desktop, its graphics refined in v17’s design language.' },
  { id: 'v21', title: 'A desk with a computer', parents: ['v19', 'v20'], borrows: [], status: 'complete',
    note: 'One workspace: v19’s desk with a computer on it that runs v20’s desktop, each half in its own style.' },
  { id: 'v22', title: 'Vector', parents: ['v21'], borrows: [], status: 'complete',
    note: 'v21 in one style: the computer redrawn as a modern vector interface, and things in the room that can be changed.' },
  { id: 'v23', title: 'Pixel art', parents: ['v21'], borrows: [], status: 'complete',
    note: 'v21 in one style: the room as pixel art, the computer in full-colour pixels.' },
  { id: 'v24', title: 'Pixel art with variations', parents: ['v23', 'v22'], borrows: [], status: 'complete',
    note: 'v23’s pixel room with v22’s variations, lit for every lamp and every time of day.' },
  { id: 'v25', title: 'The room, perfected and expanded', parents: ['v24'], borrows: [], status: 'complete',
    note: 'v24 perfected and expanded into a space to wander: a reading corner round the corner, machines under the desk, and nooks to get lost in.' }
];

var CHAPTERS = [
  { id: 'core', numeral: 'I', title: 'The working core', first: 'v01', last: 'v03',
    note: 'The interpreter and the sieves made to work on a plain page, then laid out two ways.' },
  { id: 'styles', numeral: 'II', title: 'Eleven styles', first: 'v04', last: 'v14',
    note: 'The page with tabs dressed eleven ways, from thermal paper and microfiche to Dada and film.' },
  { id: 'crossings', numeral: 'III', title: 'Crossings', first: 'v15', last: 'v18',
    note: 'The styles crossed with one another into a desk, a desktop, a game and a magazine of code art.' },
  { id: 'workspace', numeral: 'IV', title: 'The workspace', first: 'v19', last: 'v25',
    note: 'The desk and the desktop brought into one room, then drawn again and again until it was a place to wander.' }
];
