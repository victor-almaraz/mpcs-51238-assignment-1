/* The room's sounds, made in the page with Web Audio (no recordings): the switch's click, the
   lamp's mains hum while it is on (and a buzz as it catches), a tock as a thing is set down
   in another's place, a rustle as the paper changes, the tape motor's whir under the music,
   the printer's chatter while the computer scrolls its output, and a blip when the narrator
   speaks. They answer the room's events (room:*, from decor.js, life.js and look.js) and the
   recorder's state. Nothing sounds until the page has been pressed, as browsers require;
   Room sounds in the menu turns them off and on. */

(function () {
  'use strict';
  var doc = document, scene = doc.querySelector('.overview'), room = doc.getElementById('desk');
  var recorder = doc.getElementById('recorder'), btn = doc.getElementById('sound-btn');
  if (!scene) return;
  var ac = null, out = null, noise = null, on = true, hum = null, whir = null;

  function ctx() {
    if (!on) return null;
    if (!ac) {
      var AC = window.AudioContext || window.webkitAudioContext;
      if (!AC) return null;
      ac = new AC();
      out = ac.createGain(); out.gain.value = 0.5; out.connect(ac.destination);
      // a second of white noise, the stuff of clicks, rustles and whirs
      noise = ac.createBuffer(1, ac.sampleRate, ac.sampleRate);
      var d = noise.getChannelData(0), seed = 7;
      for (var i = 0; i < d.length; i++) { seed = (seed * 16807) % 2147483647; d[i] = seed / 1073741823.5 - 1; }
    }
    if (ac.state === 'suspended') ac.resume();
    return ac;
  }
  function env(g, t, a, peak, decay) {
    g.gain.setValueAtTime(0.0001, t);
    g.gain.exponentialRampToValueAtTime(peak, t + a);
    g.gain.exponentialRampToValueAtTime(0.0001, t + a + decay);
  }
  function burst(t, dur, type, freq, q, peak) {
    var s = ac.createBufferSource(), f = ac.createBiquadFilter(), g = ac.createGain();
    s.buffer = noise; f.type = type; f.frequency.value = freq; f.Q.value = q || 1;
    s.connect(f); f.connect(g); g.connect(out);
    env(g, t, 0.002, peak, dur);
    s.start(t, Math.random() * 0.5, dur + 0.05);
  }
  function tone(t, hz, dur, peak, type, to) {
    var o = ac.createOscillator(), g = ac.createGain();
    o.type = type || 'sine'; o.frequency.setValueAtTime(hz, t);
    if (to) o.frequency.exponentialRampToValueAtTime(to, t + dur);
    o.connect(g); g.connect(out);
    env(g, t, 0.004, peak, dur);
    o.start(t); o.stop(t + dur + 0.05);
  }

  var SOUND = {
    click: function (t) { burst(t, 0.012, 'highpass', 2500, 0.7, 0.5); tone(t, 180, 0.05, 0.25, 'triangle', 90); },
    tock: function (t) { tone(t, 420, 0.07, 0.22, 'sine', 300); burst(t, 0.02, 'bandpass', 1800, 2, 0.12); },
    rustle: function (t) { for (var k = 0; k < 5; k++) burst(t + k * 0.045 + Math.random() * 0.02, 0.06, 'bandpass', 3000 + Math.random() * 2500, 0.8, 0.07); },
    buzz: function (t) { tone(t, 100, 0.06, 0.06, 'sawtooth'); burst(t, 0.03, 'highpass', 5000, 0.5, 0.05); },
    blip: function (t) { tone(t, 880, 0.05, 0.05, 'square'); tone(t + 0.06, 1320, 0.06, 0.04, 'square'); },
    chatter: function (t) { for (var k = 0; k < 40; k++) burst(t + k * 0.075 + (k % 3) * 0.012, 0.008, 'bandpass', 2200, 3, 0.09); }
  };
  function play(name) { if (!ctx()) return; SOUND[name](ac.currentTime + 0.01); }

  // a sound that lasts: the lamp's hum, the tape motor's whir
  function drone(build) {
    var g = ac.createGain(); g.gain.value = 0.0001; g.connect(out);
    var stop = build(g);
    return { g: g, stop: stop };
  }
  function fade(d, to, time) {
    var t = ac.currentTime;
    d.g.gain.cancelScheduledValues(t); d.g.gain.setValueAtTime(Math.max(0.0001, d.g.gain.value), t);
    d.g.gain.exponentialRampToValueAtTime(Math.max(0.0001, to), t + time);
  }
  function lampHum() {
    return drone(function (g) {
      var a = ac.createOscillator(), b = ac.createOscillator(), gb = ac.createGain();
      a.frequency.value = 100; b.frequency.value = 200; gb.gain.value = 0.4;
      a.connect(g); b.connect(gb); gb.connect(g); a.start(); b.start();
    });
  }
  function motor() {
    return drone(function (g) {
      var s = ac.createBufferSource(), f = ac.createBiquadFilter(), o = ac.createOscillator(), go = ac.createGain();
      s.buffer = noise; s.loop = true; f.type = 'lowpass'; f.frequency.value = 500;
      o.type = 'triangle'; o.frequency.value = 55; go.gain.value = 0.5;
      s.connect(f); f.connect(g); o.connect(go); go.connect(g); s.start(); o.start();
    });
  }
  // the hum is heard only in the room, while the lamp is on
  function steady() {
    if (!ac) return;
    var inRoom = room.getAttribute('data-at') === 'desk';
    if (!hum) hum = lampHum();
    fade(hum, on && inRoom && Decor.lampOn() ? 0.012 : 0.0001, 0.4);
    var playing = recorder.getAttribute('data-state') === 'playing';
    if (!whir) whir = motor();
    fade(whir, on && playing ? 0.05 : 0.0001, playing ? 0.3 : 0.6);
  }

  scene.addEventListener('room:switch', function () { play('click'); steady(); });
  scene.addEventListener('room:flicker', function (e) { if (e.detail.lit) play('buzz'); });
  scene.addEventListener('room:swap', function () { play('tock'); });
  scene.addEventListener('room:paper', function () { play('rustle'); });
  scene.addEventListener('room:look', function () { play('blip'); });
  scene.addEventListener('room:computing', function () { play('chatter'); });
  new MutationObserver(function () { if (ctx()) steady(); }).observe(recorder, { attributes: true, attributeFilter: ['data-state'] });
  new MutationObserver(steady).observe(room, { attributes: true, attributeFilter: ['data-at'] });
  // the first press anywhere wakes the sound, and the hum with it
  doc.addEventListener('pointerdown', function first() { if (ctx()) { steady(); doc.removeEventListener('pointerdown', first, true); } }, true);
  doc.addEventListener('keydown', function first() { if (ctx()) { steady(); doc.removeEventListener('keydown', first, true); } }, true);

  btn.addEventListener('click', function () {
    on = !on;
    btn.setAttribute('aria-pressed', String(on));
    btn.textContent = 'Room sounds: ' + (on ? 'on' : 'off');
    if (on) ctx();
    steady();
  });
})();
