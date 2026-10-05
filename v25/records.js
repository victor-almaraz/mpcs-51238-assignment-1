/* The record player in the reading corner, and its crate of seven records: renditions of
   music now in the public domain, from Pachelbel to Joplin, each played by the page with Web
   Audio (no recordings) in a voice of its own (a piano, strings, plucked strings, a violin),
   with a record's hiss, its crackle and a little wow. Taken up, the player is drawn from above
   in pixels, its platter turning and its tonearm crossing the side as it plays; a record is
   chosen from the crate, and plays on wherever the visitor goes in the room, turning in the
   room too, until it ends or is stopped. Needs Desk (desk.js). */

(function () {
  'use strict';
  var doc = document, station = doc.querySelector('.st-records');
  if (!station) return;
  var $ = function (id) { return doc.getElementById(id); };
  var scene = doc.querySelector('.overview'), roomBtn = doc.querySelector('.o-records');

  /* ---------------- the music: notes, each [beat, beats, midi, velocity, voice] ---------------- */
  var NAMES = { C: 0, D: 2, E: 4, F: 5, G: 7, A: 9, B: 11 };
  function m(s) { var r = /^([A-G])(#|b)?(-?\d)$/.exec(s); return 12 * (Number(r[3]) + 1) + NAMES[r[1]] + (r[2] === '#' ? 1 : r[2] === 'b' ? -1 : 0); }
  // a line of [note, length] (null a rest), from a beat, in units of a beat
  function line(ev, at, notes, unit, vel, voice) {
    notes.forEach(function (n) { if (n[0]) ev.push([at, n[1] * unit, m(n[0]), vel, voice]); at += n[1] * unit; });
    return at;
  }
  function chord(ev, at, notes, beats, vel, voice) { notes.split(' ').forEach(function (n) { ev.push([at, beats, m(n), vel, voice]); }); }

  function pachelbel() {
    // the ground of eight notes, its chords, and three of the canon's voices over it in turn
    var ev = [], BASS = 'D3 A2 B2 F#2 G2 D2 G2 A2'.split(' ');
    var CH = ['F#4 A4 D5', 'E4 A4 C#5', 'F#4 B4 D5', 'F#4 A4 C#5', 'G4 B4 D5', 'F#4 A4 D5', 'G4 B4 D5', 'E4 A4 C#5'];
    var V1 = 'F#5 E5 D5 C#5 B4 A4 B4 C#5'.split(' '), V2 = 'D5 C#5 B4 A4 G4 F#4 G4 E4'.split(' ');
    var V3 = 'D4 F#4 A4 G4 F#4 D4 F#4 E4 D4 B3 D4 A4 G4 B4 A4 G4 F#4 D4 E4 C#5 D5 F#5 A5 A4 B4 G4 A4 F#4 D4 D5 D5 C#5'.split(' ');
    for (var c = 0; c < 5; c++) {
      for (var k = 0; k < 8; k++) {
        var at = c * 16 + k * 2;
        ev.push([at, 2, m(BASS[k]), 0.5, 'cello']);
        if (c > 0) chord(ev, at, CH[k], 2, 0.16, 'strings');
        if (c === 1 || c === 4) ev.push([at, 2, m(V1[k]), 0.4, 'violin']);
        if (c === 2 || c === 4) ev.push([at, 2, m(V2[k]) + (c === 4 ? 12 : 0), 0.32, 'violin']);
        if (c === 3) for (var q = 0; q < 4; q++) ev.push([at + q * 0.5, 0.5, m(V3[k * 4 + q]) + 12, 0.36, 'violin']);
      }
    }
    ev.push([80, 4, m('D3'), 0.5, 'cello']); chord(ev, 80, 'F#4 A4 D5', 4, 0.2, 'strings');
    return { bpm: 56, ev: ev };
  }

  function bach() {
    // the Prelude in C: each bar one chord, broken in the same figure twice over
    var BARS = ['C3 E3 G3 C4 E4', 'C3 D3 A3 D4 F4', 'B2 D3 G3 D4 F4', 'C3 E3 G3 C4 E4', 'C3 E3 A3 E4 A4', 'C3 D3 F#3 A3 D4',
      'B2 D3 G3 D4 G4', 'B2 C3 E3 G3 C4', 'A2 C3 E3 G3 C4', 'D2 A2 D3 F#3 C4', 'G2 B2 D3 G3 B3', 'G2 Bb2 E3 G3 C#4', 'F2 A2 D3 A3 D4',
      'F2 Ab2 D3 F3 B3', 'E2 G2 C3 G3 C4', 'E2 F2 A2 C3 F3', 'D2 F2 A2 C3 F3', 'G1 D2 G2 B2 F3', 'C2 E2 G2 C3 E3', 'C2 G2 Bb2 C3 E3',
      'F1 F2 A2 C3 E3', 'G1 G2 B2 D3 F3', 'C2 E2 G2 C3 E3'];
    var ev = [];
    BARS.forEach(function (b, i) {
      var n = b.split(' ').map(m);
      for (var h = 0; h < 2; h++) {
        var at = i * 4 + h * 2;
        ev.push([at, 2, n[0], 0.42, 'piano']); ev.push([at + 0.25, 1.75, n[1], 0.36, 'piano']);
        [2, 3, 4, 2, 3, 4].forEach(function (j, k) { ev.push([at + 0.5 + k * 0.25, 0.25, n[j], 0.3, 'piano']); });
      }
    });
    chord(ev, BARS.length * 4, 'C2 C3 E3 G3 C4 E4', 4, 0.32, 'piano');
    return { bpm: 72, ev: ev };
  }

  function beethoven() {
    // Für Elise: its theme twice, in sixteenths, the left hand's broken chords under it
    var ev = [], at = 0;
    var A = [['E5', 1], ['D#5', 1], ['E5', 1], ['D#5', 1], ['E5', 1], ['B4', 1], ['D5', 1], ['C5', 1]];
    function bar(t, mel, bass) { line(ev, t, mel, 0.25, 0.4, 'piano'); line(ev, t, bass, 0.25, 0.25, 'piano'); }
    for (var r = 0; r < 2; r++) {
      at = line(ev, at, [['E5', 1], ['D#5', 1]], 0.25, 0.4, 'piano');
      at = line(ev, at, A, 0.25, 0.4, 'piano');
      bar(at, [['A4', 2], ['C4', 1], ['E4', 1], ['A4', 1]], [['A2', 1], ['E3', 1], ['A3', 1]]); at += 1.5;
      bar(at, [['B4', 2], ['E4', 1], ['G#4', 1], ['B4', 1]], [['E2', 1], ['E3', 1], ['G#3', 1]]); at += 1.5;
      bar(at, [['C5', 2], ['E4', 1], ['E5', 1], ['D#5', 1]], [['A2', 1], ['E3', 1], ['A3', 1]]); at += 1.5;
      at = line(ev, at, A, 0.25, 0.4, 'piano');
      bar(at, [['A4', 2], ['C4', 1], ['E4', 1], ['A4', 1]], [['A2', 1], ['E3', 1], ['A3', 1]]); at += 1.5;
      bar(at, [['B4', 2], ['E4', 1], ['C5', 1], ['B4', 1]], [['E2', 1], ['E3', 1], ['G#3', 1]]); at += 1.5;
      bar(at, [['A4', 4]], [['A2', 1], ['E3', 1], ['A3', 1]]); at += 1.5;
    }
    return { bpm: 76, ev: ev };
  }

  function grieg() {
    // In the Hall of the Mountain King: its theme over and over, louder, higher, and faster
    // each time (the tempo rises in the beats themselves), plucked strings under it
    var ev = [], at = 0;
    var T = [['B3', 1], ['C#4', 1], ['D4', 1], ['E4', 1], ['F#4', 1], ['D4', 1], ['F#4', 2], ['F4', 1], ['C#4', 1], ['F4', 2], ['E4', 1], ['C4', 1], ['E4', 2],
      ['B3', 1], ['C#4', 1], ['D4', 1], ['E4', 1], ['F#4', 1], ['D4', 1], ['F#4', 1], ['B4', 1], ['A4', 1], ['F#4', 1], ['D4', 1], ['F#4', 1], ['A4', 4]];
    for (var r = 0; r < 6; r++) {
      var u = 0.5 * Math.pow(0.86, r), up = r >= 3 ? 12 : 0, vel = 0.22 + r * 0.05;
      var start = at;
      T.forEach(function (n) { ev.push([at, n[1] * u, m(n[0]) + up, vel, r < 2 ? 'pizz' : 'violin']); at += n[1] * u; });
      for (var b = start, k = 0; b < at - 0.01; b += u * 2, k++) ev.push([b, u, m(k % 2 ? 'F#2' : 'B1') + (r >= 4 ? 12 : 0), 0.3 + r * 0.04, 'pizz']);
    }
    chord(ev, at, 'B1 B2 F#3 B3 D4', 2, 0.5, 'strings');
    return { bpm: 120, ev: ev };
  }

  function satie() {
    // the first Gymnopédie: its rocking chords, and the melody over them, slow and painful
    var ev = [];
    var MEL = [[null, 1], ['F#5', 1], ['A5', 1], ['G5', 1], ['F#5', 1], ['C#5', 1], ['B4', 1], ['C#5', 1], ['D5', 1], ['A4', 3], ['F#4', 3], ['F#4', 3],
      [null, 1], ['F#5', 1], ['A5', 1], ['G5', 1], ['F#5', 1], ['C#5', 1], ['B4', 1], ['C#5', 1], ['D5', 1], ['A4', 3], ['C#5', 3], ['F#5', 3], ['E5', 3]];
    var bars = 4 + Math.ceil(MEL.reduce(function (s, n) { return s + n[1]; }, 0) / 3) + 1;
    for (var b = 0; b < bars; b++) {
      var odd = b % 2 === 0;
      ev.push([b * 3, 3, m(odd ? 'G2' : 'D2'), 0.32, 'piano']);
      chord(ev, b * 3 + 1, odd ? 'B3 D4 F#4' : 'A3 C#4 F#4', 2, 0.18, 'piano');
    }
    line(ev, 12, MEL, 1, 0.36, 'piano');
    chord(ev, bars * 3, 'D2 A3 D4 F#4', 4, 0.22, 'piano');
    return { bpm: 66, ev: ev };
  }

  function bumblebee() {
    // Flight of the Bumblebee: the chromatic theme on a violin, over the strings' chords
    var G = [[7, 6, 5, 4, 5, 4, 3, 2], [3, 2, 1, 0, -1, -2, -3, -4], [-5, -6, -7, -8, -9, -4, -5, -6], [-5, -6, -7, -8, -9, -8, -7, -6],
      [-5, -6, -7, -8, -7, -8, -9, -10], [-9, -8, -7, -6, -5, -4, -5, -6], [-5, -6, -7, -8, -9, -4, -5, -6], [-5, -6, -7, -8, -9, -8, -7, -6],
      [-5, -4, -5, -6, -5, -4, -5, -6], [-5, -4, -3, -2, -1, 0, 1, 2], [3, 2, 1, 0, -1, 0, 1, 2], [3, 4, 5, 6, 7, 6, 5, 4]];
    var ROOT = [57, 57, 52, 52, 57, 50, 52, 52, 57, 57, 52, 52];
    var ev = [], at = 0;
    for (var r = 0; r < 3; r++) G.forEach(function (g, i) {
      g.forEach(function (n, k) { ev.push([at + k * 0.25, 0.25, 69 + n + 12, 0.3, 'violin']); });
      ev.push([at, 1, ROOT[i] - 12, 0.3, 'pizz']); ev.push([at + 1, 1, ROOT[i] - 12, 0.24, 'pizz']);
      at += 2;
    });
    ev.push([at, 1, 57, 0.4, 'pizz']); ev.push([at, 1, 81, 0.3, 'violin']);
    return { bpm: 144, ev: ev };
  }

  function joplin() {
    // The Entertainer: its first strain, twice, over the stride bass of a rag
    var ev = [], at = 0;
    var A1 = [['D5', 1], ['D#5', 1], ['E5', 1], ['C6', 2], ['E5', 1], ['C6', 2], ['E5', 1], ['C6', 5], ['C6', 1], ['D6', 1], ['D#6', 1], ['E6', 1],
      ['C6', 1], ['D6', 1], ['E6', 2], ['B5', 1], ['D6', 2], ['C6', 4]];
    var A2 = [['D5', 1], ['D#5', 1], ['E5', 1], ['C6', 2], ['E5', 1], ['C6', 2], ['E5', 1], ['C6', 5], ['A5', 1], ['G5', 1], ['F#5', 1], ['A5', 1],
      ['C6', 1], ['E6', 2], ['D6', 1], ['C6', 1], ['A5', 1], ['D6', 4]];
    var HARM = [['C2', 'E3 G3 C4'], ['C2', 'E3 G3 C4'], ['C2', 'E3 G3 C4'], ['G1', 'F3 G3 B3'], ['C2', 'E3 G3 C4'], ['C2', 'E3 G3 C4'], ['D2', 'F#3 A3 C4'], ['G1', 'F3 G3 B3']];
    for (var r = 0; r < 2; r++) {
      var start = at;
      at = line(ev, at, A1, 0.25, 0.36, 'piano');
      at = line(ev, at, A2, 0.25, 0.36, 'piano');
      for (var b = 0, t = start + 0.75; t < at - 0.01; b++, t += 2) {
        var h = HARM[b % HARM.length];
        ev.push([t, 0.5, m(h[0]), 0.3, 'piano']); chord(ev, t + 0.5, h[1], 0.5, 0.16, 'piano');
        ev.push([t + 1, 0.5, m(h[0]) + 12, 0.28, 'piano']); chord(ev, t + 1.5, h[1], 0.5, 0.16, 'piano');
      }
    }
    chord(ev, at, 'C2 C3 E4 G4 C5', 2, 0.3, 'piano');
    return { bpm: 76, ev: ev };
  }

  var RECORDS = [
    { title: 'Canon in D', who: 'Johann Pachelbel', when: 'the later 1600s', label: '#c9a53a', sleeve: ['#7a2c2a', '#e8d9b0'], build: pachelbel },
    { title: 'Prelude in C major, BWV 846', who: 'Johann Sebastian Bach', when: '1722', label: '#e8e2d0', sleeve: ['#24384f', '#d9cfae'], build: bach },
    { title: 'Für Elise', who: 'Ludwig van Beethoven', when: '1810', label: '#b8463a', sleeve: ['#e8e0cc', '#2a2a2e'], build: beethoven },
    { title: 'In the Hall of the Mountain King', who: 'Edvard Grieg', when: '1875', label: '#5a8a52', sleeve: ['#2f4a34', '#e3b04a'], build: grieg },
    { title: 'Gymnopédie No. 1', who: 'Erik Satie', when: '1888', label: '#8aa4b8', sleeve: ['#e8e4dc', '#6a7c8a'], build: satie },
    { title: 'Flight of the Bumblebee', who: 'Nikolai Rimsky-Korsakov', when: '1900', label: '#e2b53a', sleeve: ['#1f1f22', '#e2b53a'], build: bumblebee },
    { title: 'The Entertainer', who: 'Scott Joplin', when: '1902', label: '#d06a3a', sleeve: ['#e6c98a', '#7a3a24'], build: joplin }
  ];

  /* ---------------- the voices ---------------- */
  var ac = null, out = null, bus = null, hiss = null, noise = null;
  function ctx() {
    if (!ac) {
      var AC = window.AudioContext || window.webkitAudioContext;
      if (!AC) return null;
      ac = new AC(); out = ac.createGain(); out.gain.value = 0.5; out.connect(ac.destination);
      noise = ac.createBuffer(1, ac.sampleRate * 2, ac.sampleRate);
      var d = noise.getChannelData(0), s = 11;
      for (var i = 0; i < d.length; i++) { s = (s * 16807) % 2147483647; d[i] = s / 1073741823.5 - 1; }
    }
    if (ac.state === 'suspended') ac.resume();
    return ac;
  }
  function hz(n) { return 440 * Math.pow(2, (n - 69) / 12); }
  function osc(type, f, t, end, dest, detune) {
    var o = ac.createOscillator(); o.type = type; o.frequency.setValueAtTime(f, t); if (detune) o.detune.value = detune;
    o.connect(dest); o.start(t); o.stop(end);
    return o;
  }
  function env(t, a, peak, hold, rel) {
    var g = ac.createGain(); g.gain.setValueAtTime(0.0001, t); g.gain.exponentialRampToValueAtTime(peak, t + a);
    if (hold > 0) g.gain.setValueAtTime(peak, t + a + hold);
    g.gain.exponentialRampToValueAtTime(0.0001, t + a + hold + rel);
    return g;
  }
  // a record's wow: the whole side drifts a few cents, slowly, as a warped pressing does
  function wow(t) { return 6 * Math.sin(t * 2 * Math.PI * 0.55); }
  var VOICES = {
    piano: function (t, f, dur, v) {
      var decay = Math.min(3, 0.5 + 220 / f), g = env(t, 0.004, v, 0, Math.max(dur, 0.15) + decay * 0.5);
      var lp = ac.createBiquadFilter(); lp.type = 'lowpass'; lp.frequency.value = Math.min(6000, f * 6); lp.connect(g); g.connect(bus);
      var end = t + dur + decay;
      osc('triangle', f, t, end, lp, wow(t)); osc('sine', f * 2, t, end, lp, wow(t) + 3); osc('sine', f, t, end, lp, -4);
    },
    strings: function (t, f, dur, v) {
      var g = env(t, 0.18, v, Math.max(0, dur - 0.18), 0.4), lp = ac.createBiquadFilter(); lp.type = 'lowpass'; lp.frequency.value = 1800;
      lp.connect(g); g.connect(bus);
      osc('sawtooth', f, t, t + dur + 0.5, lp, wow(t) - 5); osc('sawtooth', f, t, t + dur + 0.5, lp, wow(t) + 5);
    },
    cello: function (t, f, dur, v) {
      var g = env(t, 0.08, v, Math.max(0, dur - 0.1), 0.3), lp = ac.createBiquadFilter(); lp.type = 'lowpass'; lp.frequency.value = 900;
      lp.connect(g); g.connect(bus); osc('sawtooth', f, t, t + dur + 0.4, lp, wow(t));
    },
    violin: function (t, f, dur, v) {
      var g = env(t, Math.min(0.06, dur * 0.3), v, Math.max(0, dur * 0.8 - 0.06), 0.12), lp = ac.createBiquadFilter(); lp.type = 'lowpass'; lp.frequency.value = 3800;
      lp.connect(g); g.connect(bus);
      var o = osc('sawtooth', f, t, t + dur + 0.2, lp, wow(t));
      if (dur > 0.4) { var lfo = ac.createOscillator(), d = ac.createGain(); lfo.frequency.value = 5.5; d.gain.value = f * 0.006; lfo.connect(d); d.connect(o.frequency); lfo.start(t + 0.15); lfo.stop(t + dur + 0.2); }
    },
    pizz: function (t, f, dur, v) {
      var g = env(t, 0.003, v, 0, 0.25 + 60 / f), lp = ac.createBiquadFilter(); lp.type = 'lowpass'; lp.frequency.value = Math.min(4000, f * 5);
      lp.connect(g); g.connect(bus); osc('triangle', f, t, t + 0.6, lp, wow(t)); osc('square', f, t, t + 0.12, lp);
    }
  };

  // the record's own noise: a hiss under it all, and a crackle now and then
  function surface(on) {
    if (hiss) { try { hiss.stop(); } catch (e) { /* stopped */ } hiss = null; }
    if (!on) return;
    var s = ac.createBufferSource(), f = ac.createBiquadFilter(), g = ac.createGain();
    s.buffer = noise; s.loop = true; f.type = 'bandpass'; f.frequency.value = 5000; f.Q.value = 0.6; g.gain.value = 0.012;
    s.connect(f); f.connect(g); g.connect(out); s.start(); hiss = s;
  }
  function crackle(t) {
    var s = ac.createBufferSource(), f = ac.createBiquadFilter(), g = ac.createGain();
    s.buffer = noise; f.type = 'highpass'; f.frequency.value = 2500; g.gain.setValueAtTime(0.08 + Math.random() * 0.08, t); g.gain.exponentialRampToValueAtTime(0.0001, t + 0.006);
    s.connect(f); f.connect(g); g.connect(out); s.start(t, Math.random() * 1.5, 0.01);
  }

  /* ---------------- playing a side ---------------- */
  var playing = null, timer = null;
  function play(i) {
    stop(true);
    if (!ctx()) return;
    var r = RECORDS[i], sc = r.build(), spb = 60 / sc.bpm;
    sc.ev.sort(function (a, b) { return a[0] - b[0]; });
    bus = ac.createGain(); bus.gain.value = 1; bus.connect(out);
    var t0 = ac.currentTime + 1.2;                      // the needle in the lead-in groove first
    var len = sc.ev.reduce(function (s, e) { return Math.max(s, e[0] + e[1]); }, 0) * spb + 2.5;
    playing = { i: i, t0: t0, len: len, ev: sc.ev, next: 0, spb: spb, bus: bus };
    surface(true);
    timer = setInterval(plan, 100); plan();
    show(); say('On the turntable: ' + r.title + ', by ' + r.who + '.');
  }
  function plan() {
    if (!playing) return;
    var p = playing, now = ac.currentTime;
    while (p.next < p.ev.length && p.t0 + p.ev[p.next][0] * p.spb < now + 0.5) {
      var e = p.ev[p.next++];
      VOICES[e[4]](p.t0 + e[0] * p.spb, hz(e[2]), e[1] * p.spb, e[3]);
    }
    if (Math.random() < 0.25) crackle(now + 0.1 + Math.random() * 0.3);
    if (now > p.t0 + p.len) { var was = p.i; stop(); say(RECORDS[was].title + ' has played to the end of the side; the tonearm lifts.'); }
  }
  function stop(quiet) {
    clearInterval(timer);
    if (playing) {
      var g = playing.bus.gain, t = ac.currentTime; g.cancelScheduledValues(t); g.setValueAtTime(g.value, t); g.exponentialRampToValueAtTime(0.0001, t + 0.3);
      setTimeout(function (b) { return function () { b.disconnect(); }; }(playing.bus), 500);
      playing = null; surface(false);
      if (!quiet) say('The record stops.');
    }
    show();
  }
  function say(msg) { $('rec-status').textContent = ''; setTimeout(function () { $('rec-status').textContent = msg; }, 30); }

  /* ---------------- the crate, and what shows ---------------- */
  var crate = $('rec-crate');
  RECORDS.forEach(function (r, i) {
    var li = doc.createElement('li'), b = doc.createElement('button'), sl = doc.createElement('span'), tx = doc.createElement('span');
    b.type = 'button'; b.className = 'rec-sleeve';
    sl.className = 'rec-art'; sl.setAttribute('aria-hidden', 'true');
    sl.style.setProperty('--a', r.sleeve[0]); sl.style.setProperty('--b', r.sleeve[1]);
    tx.className = 'rec-text'; tx.innerHTML = '<b></b><span></span>';
    tx.firstChild.textContent = r.title; tx.lastChild.textContent = r.who + ', ' + r.when;
    b.appendChild(sl); b.appendChild(tx);
    b.addEventListener('click', function () { if (playing && playing.i === i) stop(); else play(i); });
    li.appendChild(b); crate.appendChild(li);
  });
  $('rec-stop').addEventListener('click', function () { stop(); });
  function show() {
    Array.prototype.forEach.call(crate.querySelectorAll('.rec-sleeve'), function (b, i) {
      var on = !!playing && playing.i === i;
      b.setAttribute('aria-pressed', String(on));
      b.setAttribute('aria-label', (on ? 'Stop ' : 'Play ') + RECORDS[i].title + ', by ' + RECORDS[i].who);
    });
    $('rec-stop').disabled = !playing;
    $('rec-now').textContent = playing ? RECORDS[playing.i].title + ' · ' + RECORDS[playing.i].who : 'Nothing is playing. Choose a record from the crate.';
    if (scene) scene.classList.toggle('record-on', !!playing);
    if (roomBtn) roomBtn.setAttribute('data-say', playing ? 'The record player: ' + RECORDS[playing.i].title : 'Play a record');
  }

  /* ---------------- the player from above, drawn in pixels ---------------- */
  var canvas = $('rec-canvas'), g = canvas.getContext('2d'), W = 200, H = 140;
  function rect(x, y, w, h, c) { g.fillStyle = c; g.fillRect(x, y, w, h); }
  var CX = 78, CY = 70, R = 58;
  var angle = 0, last = 0;
  function draw(t) {
    var dt = last ? (t - last) / 1000 : 0; last = t;
    if (playing) angle += dt * 2 * Math.PI * (33.333 / 60);
    // the case: teal, its lid's cream lining behind, the deck in black
    rect(0, 0, W, H, '#3f7478'); rect(2, 2, W - 4, H - 4, '#48828a'); rect(6, 6, W - 12, H - 12, '#232124');
    for (var y = -R - 4; y <= R + 4; y++) for (var x = -R - 4; x <= R + 4; x++) {
      var d = Math.sqrt(x * x + y * y);
      if (d > R + 3.5) continue;
      var c = d > R ? '#8a8c90' : '#141315';
      if (d <= R && d > 22 && Math.round(d) % 3 === 0) c = '#1d1c20';                   // the grooves
      if (d <= R && d > 26 && (x + y) % 2 === 0 && Math.cos(Math.atan2(y, x) - angle - 0.8) > 0.9985) c = '#4a4a54';   // a glint on them, turning
      if (d <= 20) {
        var r = playing ? RECORDS[playing.i] : null;
        c = r ? r.label : '#8a8c90';
        var la = Math.atan2(y, x) - angle;
        if (r && d > 7 && d < 15 && Math.abs(Math.sin(la)) < 0.12 && Math.cos(la) > 0) c = '#f2ead8';   // the label's lettering, turning
      }
      if (d <= 1.5) c = '#d8d8dc';
      rect(CX + x, CY + y, 1, 1, c);
    }
    // the tonearm: at rest on its post beside the platter; playing, its needle in the groove,
    // from the outer edge to the label as the side plays
    var px = 168, py = 22, L = 88, armA = Math.PI / 2;
    if (playing) {
      var prog = Math.max(0, Math.min(1, (ac.currentTime - playing.t0) / (playing.len - 2.5)));
      var groove = R - 4 - prog * (R - 26);
      while (armA < 3 && Math.hypot(px + Math.cos(armA) * L - CX, py + Math.sin(armA) * L - CY) > groove) armA += 0.004;
    }
    rect(px - 6, py - 6, 13, 13, '#5a5c60'); rect(px - 4, py - 4, 9, 9, '#b8babe');
    var hx = px + Math.cos(armA) * L, hy = py + Math.sin(armA) * L;
    for (var k = 0; k <= L; k++) rect(Math.round(px + Math.cos(armA) * k), Math.round(py + Math.sin(armA) * k), 2, 2, '#c8cacd');
    rect(Math.round(hx) - 3, Math.round(hy) - 2, 7, 5, '#e8e8ea');
    // the speed switch and the knobs
    rect(150, 112, 30, 8, '#5a5c60'); rect(playing ? 152 : 164, 113, 14, 6, '#e8e2d0');
    rect(150, 92, 8, 8, '#e8e2d0'); rect(164, 92, 8, 8, '#e8e2d0');
  }
  var frame = null;
  function tick(t) { frame = null; if (Desk.current() !== 'records') { last = 0; return; } draw(t); frame = requestAnimationFrame(tick); }
  Desk.onShow('records', function () { show(); if (!frame) frame = requestAnimationFrame(tick); });
  show();
})();
