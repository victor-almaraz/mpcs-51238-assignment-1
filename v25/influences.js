/* The folio of influences from the bookcase: a sheet for each kind of thing the room was made
   from (music, computing, art by chance and rule, photography, books, film and design), its
   entries set as a catalogue's cards. Its sheets turn as the manual's pages do (Desk.pager),
   by the buttons, the arrow keys or the index on its cover. The sheets themselves are set from
   util/v25/text/folio.md by util/v25/build_folio.py. Needs Desk (desk.js). */
(function () {
  'use strict';
  var box = document.getElementById('influences');
  if (!box) return;
  Desk.pager(box, Desk.$$('.fo-sheet', box), Desk.$('fo-folio'), 'Sheet', Desk.$$('#fo-index button', box));
})();
