/* The computer's end of its link to the room. Inside the room (in its frame) the computer
   takes texts from the card punch and the stacker into its Editor, punches the Editor's
   text back onto the coding form, and goes back to the room; opened alone it is the
   desktop and nothing more. Messages go by postMessage, which also works from disk:
     from the room   { type: 'open-text', name, text, kind, note }
     to the room     { type: 'ready' }, { type: 'punch', name, text }, { type: 'room' }
   Needs Desk (wm.js) and Workspace (workspace.js). */

(function () {
  'use strict';
  var room = window.parent;
  if (room === window) return;
  document.documentElement.classList.add('in-room');
  function tell(msg) { room.postMessage(msg, '*'); }

  window.addEventListener('message', function (e) {
    var d = e.data;
    if (e.source !== room || !d || d.type !== 'open-text') return;
    Workspace.openText(String(d.name), String(d.text), d.kind, d.note);
  });
  Desk.action('punch', function () {
    tell({ type: 'punch', name: Desk.$('ed-name').textContent, text: Desk.$('src').value });
  });
  Desk.action('room', function () { tell({ type: 'room' }); });
  tell({ type: 'ready' });
})();
