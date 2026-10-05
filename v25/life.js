/* The room answers what is done in it. While the tape plays (the recorder's data-state), its
   reels turn and its meter jumps in the room as well as on the recorder; after a deck has
   run, the room's computer scrolls the output for a few seconds when the room is next seen.
   The loops themselves are in style.css ("the room alive"). Needs Desk (desk.js). */

(function () {
  'use strict';
  var doc = document, scene = doc.querySelector('.overview'), room = doc.getElementById('desk');
  var recorder = doc.getElementById('recorder'), run = doc.getElementById('run-deck');
  if (!scene) return;

  function tape() { scene.classList.toggle('tape-on', recorder.getAttribute('data-state') === 'playing'); }
  new MutationObserver(tape).observe(recorder, { attributes: true, attributeFilter: ['data-state'] });
  tape();

  var ran = false, timer = null;
  run.addEventListener('click', function () { ran = true; });
  new MutationObserver(function () {
    if (room.getAttribute('data-at') !== 'desk' || !ran) return;
    ran = false;
    scene.classList.add('computing');
    scene.dispatchEvent(new CustomEvent('room:computing'));
    clearTimeout(timer);
    timer = setTimeout(function () { scene.classList.remove('computing'); }, 3600);
  }).observe(room, { attributes: true, attributeFilter: ['data-at'] });
})();
