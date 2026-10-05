/* The photo album from the bookcase: six openings of black pages, one photograph to a page,
   held by its corners and captioned in white pencil, black-and-white prints in their white
   borders and faded Polaroids, places and people. Its pages turn as
   the manual's do (Desk.pager): by the buttons or the arrow keys. Needs Desk (desk.js). */
(function () {
  'use strict';
  var box = document.getElementById('album');
  if (!box) return;
  Desk.pager(box, Desk.$$('.album-spread', box), Desk.$('album-folio'), 'Opening');
})();
