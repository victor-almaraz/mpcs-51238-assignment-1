/* Tape: plays punched cards as sound, for a reel-to-reel player on any page.
   Classic script, no dependencies. See docs/tape-spec.md.

   Tape.parseCards(cards, opts)  -> { events, skipped, length, bare } pure
   Tape.schedule(events, opts)   -> [{ t, dur, hz, gain }] in seconds  pure
   Tape.midiToHz(note)           -> frequency in Hz                    pure
   Tape.createPlayer(opts)       -> player (needs Web Audio; built lazily on first play)

   An event card holds I5 fields, as a FORTRAN PUNCH 10, ... with 10 FORMAT (4I5) makes them:
     columns  1-5   TIME  pulse number, from 0
     columns  6-10  NOTE  MIDI note number, 0-127 (60 is middle C)
     columns 11-15  LEN   length in pulses (blank or 0 means 1)
     columns 16-20  LOUD  loudness 1-9 (blank or 0 means 7)
   A card with only columns 1-5 filled is a bare number, such as a sieve member. opts.bare
   decides what it means: 'rhythm' (the default) plays it as a TIME on opts.note; 'pitch'
   plays it as a NOTE, opts.base plus the number, one bare card per pulse in card order.
   A card with anything past column 20, or a field that is not an integer, is skipped. */

var Tape = (function () {
  'use strict';

  function field(card, k) {
    var s = card.slice(k * 5, k * 5 + 5).trim();
    if (s === '') return null;
    return /^[+-]?\d+$/.test(s) ? parseInt(s, 10) : NaN;
  }

  function parseCards(cards, opts) {
    opts = opts || {};
    var bare = opts.bare === 'pitch' ? 'pitch' : 'rhythm';
    var base = opts.base == null ? 48 : opts.base;
    var restNote = opts.note == null ? 60 : opts.note;
    var events = [], skipped = 0, nBare = 0;

    cards.forEach(function (raw) {
      var card = String(raw);
      var f = [0, 1, 2, 3].map(function (k) { return field(card, k); });
      var bad = f.some(function (x) { return x !== x; }) || card.slice(20).trim() !== '' || f[0] === null;
      if (bad) { skipped++; return; }
      var ev;
      if (f[1] === null && f[2] === null && f[3] === null) {
        ev = bare === 'pitch'
          ? { time: nBare, note: base + f[0], len: 1, loud: 7 }
          : { time: f[0], note: restNote, len: 1, loud: 7 };
        nBare++;
      } else {
        if (f[1] === null) { skipped++; return; }
        ev = { time: f[0], note: f[1], len: f[2] > 0 ? f[2] : 1, loud: f[3] > 0 ? Math.min(f[3], 9) : 7 };
      }
      if (ev.time < 0 || ev.note < 0 || ev.note > 127) { skipped++; return; }
      events.push(ev);
    });

    // stable sort by time, so cards punched in any order still play in time order
    events = events.map(function (e, i) { return { e: e, i: i }; })
      .sort(function (a, b) { return a.e.time - b.e.time || a.i - b.i; })
      .map(function (x) { return x.e; });
    var length = events.reduce(function (m, e) { return Math.max(m, e.time + e.len); }, 0);
    // bare: how many bare numbers were read, so a page can tell whether opts.bare mattered
    return { events: events, skipped: skipped, length: length, bare: nBare };
  }

  function midiToHz(note) { return 440 * Math.pow(2, (note - 69) / 12); }

  // A pulse is a quarter of a beat. opts.bpm (default 120) is the tempo at normal speed;
  // opts.speed (default 1) is the tape speed: 2 plays twice as fast and an octave higher.
  function pulseSeconds(opts) {
    opts = opts || {};
    var bpm = opts.bpm > 0 ? opts.bpm : 120, speed = opts.speed > 0 ? opts.speed : 1;
    return 60 / (bpm * 4) / speed;
  }

  function schedule(events, opts) {
    var p = pulseSeconds(opts), speed = opts && opts.speed > 0 ? opts.speed : 1;
    return events.map(function (e) {
      return { t: e.time * p, dur: e.len * p, hz: midiToHz(e.note) * speed, gain: e.loud / 9 };
    });
  }

  /* ---------------------------------------------------------------- player */

  // opts: { bpm, speed, hiss (0-1), onTick(state) }
  // player: load(events), play(), pause(), stop(), seek(seconds), setTempo(bpm), setSpeed(s),
  //         state() -> { playing, position, duration, bpm, speed }, close()
  function createPlayer(opts) {
    opts = opts || {};
    var bpm = opts.bpm > 0 ? opts.bpm : 120, speed = opts.speed > 0 ? opts.speed : 1;
    var hiss = opts.hiss == null ? 0.15 : opts.hiss;
    var ctx = null, master = null, wow = null, noise = null;
    var events = [], plan = [], duration = 0;
    var playing = false, startAt = 0, offset = 0, next = 0, timer = null, raf = null;
    var live = [];

    function build() {
      if (ctx) return;
      var AC = window.AudioContext || window.webkitAudioContext;
      ctx = new AC();
      var comp = ctx.createDynamicsCompressor();
      var tone = ctx.createBiquadFilter();
      tone.type = 'lowpass';
      tone.frequency.value = 5200;     // the softened top of a tape recording
      master = ctx.createGain();
      master.gain.value = 0.32;
      master.connect(tone).connect(comp).connect(ctx.destination);
      // wow: a slow wobble in pitch, shared by every note
      wow = { osc: ctx.createOscillator(), depth: ctx.createGain() };
      wow.osc.frequency.value = 0.55;
      wow.depth.gain.value = 4;          // cents
      wow.osc.connect(wow.depth);
      wow.osc.start();
    }

    function startHiss() {
      if (!hiss || noise) return;
      var len = ctx.sampleRate * 2, buf = ctx.createBuffer(1, len, ctx.sampleRate), d = buf.getChannelData(0);
      for (var i = 0; i < len; i++) d[i] = Math.random() * 2 - 1;
      var src = ctx.createBufferSource(), hp = ctx.createBiquadFilter(), g = ctx.createGain();
      src.buffer = buf; src.loop = true;
      hp.type = 'highpass'; hp.frequency.value = 3000;
      g.gain.value = 0.02 * hiss;
      src.connect(hp).connect(g).connect(master);
      src.start();
      noise = { src: src, gain: g };
    }
    function stopHiss() {
      if (!noise) return;
      noise.src.stop();
      noise = null;
    }

    function voice(ev, when) {
      var g = ctx.createGain(), a = ctx.createOscillator(), b = ctx.createOscillator();
      a.type = 'triangle'; b.type = 'sine';
      a.frequency.value = ev.hz; b.frequency.value = ev.hz * 2;
      wow.depth.connect(a.detune); wow.depth.connect(b.detune);
      var bg = ctx.createGain(); bg.gain.value = 0.25;
      a.connect(g); b.connect(bg).connect(g); g.connect(master);
      var peak = 0.6 * ev.gain, end = when + Math.max(ev.dur, 0.06);
      g.gain.setValueAtTime(0, when);
      g.gain.linearRampToValueAtTime(peak, when + 0.008);
      g.gain.setTargetAtTime(peak * 0.55, when + 0.01, 0.12);
      g.gain.setTargetAtTime(0, end, 0.06);
      a.start(when); b.start(when);
      a.stop(end + 0.4); b.stop(end + 0.4);
      var rec = { a: a, b: b, g: g };
      live.push(rec);
      a.onended = function () {
        var k = live.indexOf(rec);
        if (k >= 0) live.splice(k, 1);
        wow.depth.disconnect(a.detune); wow.depth.disconnect(b.detune);
      };
    }

    function silence() {
      live.forEach(function (r) { try { r.a.stop(); r.b.stop(); } catch (e) { /* already stopped */ } });
      live = [];
    }

    function replan() {
      plan = schedule(events, { bpm: bpm, speed: speed });
      var p = pulseSeconds({ bpm: bpm, speed: speed });
      duration = events.reduce(function (m, e) { return Math.max(m, (e.time + e.len) * p); }, 0);
    }

    function position() {
      if (!playing) return offset;
      // sound starts a moment after play(), so the position holds until it does
      return Math.min(duration, offset + Math.max(0, ctx.currentTime - startAt));
    }

    // look ahead a little and hand the notes in that window to the audio clock
    function pump() {
      var now = position(), horizon = now + 0.15;
      while (next < plan.length && plan[next].t < horizon) {
        var ev = plan[next++];
        if (ev.t >= now - 0.02) voice(ev, startAt + (ev.t - offset));
      }
      if (now >= duration && next >= plan.length && live.length === 0) finish();
    }

    function tick() {
      if (opts.onTick) opts.onTick(state());
      if (playing) raf = window.requestAnimationFrame(tick);
    }

    function firstAfter(t) {
      var i = 0;
      while (i < plan.length && plan[i].t < t) i++;
      return i;
    }

    function play() {
      if (playing || !plan.length) return;
      build();
      if (ctx.state === 'suspended') ctx.resume();
      if (offset >= duration) offset = 0;
      playing = true;
      startAt = ctx.currentTime + 0.05;
      next = firstAfter(offset);
      startHiss();
      pump();
      timer = window.setInterval(pump, 25);
      tick();
    }

    function halt() {
      window.clearInterval(timer); timer = null;
      window.cancelAnimationFrame(raf); raf = null;
      silence();
      stopHiss();
    }

    function pause() {
      if (!playing) return;
      offset = position();
      playing = false;
      halt();
      tick();
    }

    function finish() {
      playing = false;
      offset = duration;
      halt();
      tick();
    }

    function stop() {
      var was = playing;
      playing = false;
      offset = 0;
      if (was) halt();
      tick();
    }

    function seek(t) {
      var was = playing;
      if (was) { playing = false; halt(); }
      offset = Math.max(0, Math.min(duration, t));
      if (was) play(); else tick();
    }

    // changing tempo or speed keeps the place in the music, not the place in seconds
    function retime(fn) {
      var was = playing, frac = duration ? position() / duration : 0;
      if (was) { playing = false; halt(); }
      fn();
      replan();
      offset = frac * duration;
      if (was) play(); else tick();
    }

    function state() { return { playing: playing, position: position(), duration: duration, bpm: bpm, speed: speed }; }

    return {
      load: function (evs) { stop(); events = evs.slice(); replan(); tick(); },
      play: play,
      pause: pause,
      stop: stop,
      seek: seek,
      setTempo: function (v) { if (v > 0) retime(function () { bpm = v; }); },
      setSpeed: function (v) { if (v > 0) retime(function () { speed = v; }); },
      state: state,
      close: function () { stop(); if (ctx) ctx.close(); ctx = null; }
    };
  }

  return {
    parseCards: parseCards,
    schedule: schedule,
    midiToHz: midiToHz,
    pulseSeconds: pulseSeconds,
    createPlayer: createPlayer
  };
})();
