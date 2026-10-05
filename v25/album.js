/* The photo album from the bookcase: three openings of black pages, two to an opening, each
   with its photographs held by their corners and captioned in white pencil, black-and-white
   prints with their white borders and faded Polaroids, places and people. Its pages turn as
   the manual's do (Desk.pager): by the buttons or the arrow keys. Needs Desk (desk.js). */
(function () {
  'use strict';
  var box = document.getElementById('album');
  if (!box) return;
  Desk.pager(box, Desk.$$('.album-spread', box), Desk.$('album-folio'), 'Opening');
})();
