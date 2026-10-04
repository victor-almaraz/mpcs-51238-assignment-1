/* Moving the things on the desk. The coding form, the out tray, the computer, the tape
   player, the lamp, the desk's plant and the mug slide along the desk, and the stool along
   the floor: drag one, and it follows the pointer within the desk's length; a press that
   does not move still takes it up (or swaps it) as before. With the keyboard, Alt (Option)
   with the left or right arrow moves the focused thing an em, Shift with them four. Places
   are in em, so they scale with the room; nothing is kept once the page is closed. */

(function () {
  'use strict';
  var doc = document;
  var scene = doc.querySelector('.overview'), status = doc.getElementById('swap-status');
  var LIST = window.matchMedia('(max-width: 1011px), (max-height: 505px)');
  var DESK = [10.3, 81.7], FLOOR = [11, 81];   // the desk's top and the floor under it, in em
  var MOVERS = [['.desk-top > li', DESK], ['.swap.pothos', DESK], ['.swap.mug', DESK], ['.lamp', DESK], ['.stool', FLOOR]];
  var top = 3, eatClick = false;

  function em() { return parseFloat(getComputedStyle(scene).fontSize) || 16; }
  function leftOf(el) { return el.offsetLeft / em(); }
  function nameOf(el) {
    var b = el.matches('button') ? el : el.querySelector('button');
    var t = b && (b.querySelector('.obj-tag') || b);
    return t ? (t.getAttribute('aria-label') || t.textContent).split(':')[0].trim().replace(/^Change /, '') : 'it';
  }
  function place(el, x, range) {
    var w = el.offsetWidth / em();
    x = Math.max(range[0], Math.min(range[1] - w, x));
    el.style.left = x.toFixed(2) + 'em';
    return x;
  }
  function say(msg) { status.textContent = ''; setTimeout(function () { status.textContent = msg; }, 30); }

  MOVERS.forEach(function (m) {
    Array.prototype.forEach.call(doc.querySelectorAll(m[0]), function (el) {
      var range = m[1];
      el.classList.add('movable');
      el.addEventListener('pointerdown', function (e) {
        if (e.button !== 0 || LIST.matches) return;
        var x0 = e.clientX, start = leftOf(el), moved = false, size = em();
        function mv(e2) {
          var dx = e2.clientX - x0;
          if (!moved && Math.abs(dx) < 5) return;
          if (!moved) { moved = true; el.classList.add('moving'); el.style.zIndex = ++top; try { el.setPointerCapture(e.pointerId); } catch (err) { /* synthetic */ } }
          place(el, start + dx / size, range);
        }
        function up() {
          el.removeEventListener('pointermove', mv); el.removeEventListener('pointerup', up); el.removeEventListener('pointercancel', up);
          if (moved) { el.classList.remove('moving'); eatClick = true; setTimeout(function () { eatClick = false; }, 0); }
        }
        el.addEventListener('pointermove', mv); el.addEventListener('pointerup', up); el.addEventListener('pointercancel', up);
      });
      // a thing that can be focused moves with Alt and the arrows
      var b = el.matches('button') ? el : el.querySelector('button');
      if (!b) return;
      b.setAttribute('aria-describedby', 'move-hint');
      b.addEventListener('keydown', function (e) {
        if (!e.altKey || (e.key !== 'ArrowLeft' && e.key !== 'ArrowRight') || LIST.matches) return;
        e.preventDefault();
        var step = (e.shiftKey ? 4 : 1) * (e.key === 'ArrowLeft' ? -1 : 1), was = leftOf(el);
        el.style.zIndex = ++top;
        var now = place(el, was + step, range), w = el.offsetWidth / em();
        var end = now <= range[0] + 0.01 ? ', at the left end of the desk' : now >= range[1] - w - 0.01 ? ', at the right end of the desk' : '';
        say(nameOf(el).charAt(0).toUpperCase() + nameOf(el).slice(1) + ' moved ' + (step < 0 ? 'left' : 'right') + end + '.');
      });
    });
  });
  // the click that ends a drag does not also take the thing up
  window.addEventListener('click', function (e) { if (eatClick) { eatClick = false; e.stopPropagation(); e.preventDefault(); } }, true);
})();
