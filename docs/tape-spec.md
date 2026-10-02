# Tape: Spec

`scripts/tape.js` plays punched cards as sound. It is shared code: any version can load it and build a tape player on it, the way every version loads the interpreter. It defines one global, `Tape`, uses the Web Audio API built into the browser, and loads nothing from outside the site.

## Cards on tape

A program writes music by punching **event cards**, one note per card, with `FORMAT (4I5)`:

| Columns | Field | Meaning |
|---|---|---|
| 1-5 | `TIME` | Onset, in pulses from 0 |
| 6-10 | `NOTE` | MIDI note number, 0-127 (60 is middle C) |
| 11-15 | `LEN` | Length in pulses; blank or 0 means 1 |
| 16-20 | `LOUD` | Loudness 1-9; blank or 0 means 7; above 9 counts as 9 |

A **bare card** has only columns 1-5 filled, as the sieve deck punches its members. Its meaning depends on the `bare` option:

- `'rhythm'` (default): the number is a `TIME`, played on `opts.note` (default 60). The sieve `5@2 | 5@3` plays as strokes on pulses 2, 3, 7, 8, 12, ...
- `'pitch'`: the number is semitones above `opts.base` (default 48). Bare cards then play one per pulse, in card order, so a sieve plays as a scale.

The `bare` option affects only bare cards. Event cards carry their own `TIME` and `NOTE`, so a tape made only of event cards plays the same either way; `parseCards` reports the number of bare cards it read, so a page can disable its switch when the count is 0.

A card is **skipped** (and counted) if any field is not an integer, if anything is punched past column 20, if `TIME` is blank, if an event card has no `NOTE`, or if `TIME` is negative or `NOTE` is outside 0-127. Cards of text or digit rows, such as those from the v11 and v12 decks, are skipped this way. Events play in time order; cards with equal times keep their card order.

## Time

A pulse is a quarter of a beat. At the default tempo of 120 beats per minute, a pulse lasts 0.125 s. The tape speed multiplies both time and pitch, as it does on a real machine: at speed 2 (15 ips against 7½), the music plays twice as fast and an octave higher.

## API

```js
Tape.parseCards(cards, opts)   // cards: array of strings (punched cards)
                               // opts: { bare: 'rhythm'|'pitch', note, base }
                               // -> { events: [{ time, note, len, loud }], skipped, length, bare }
                               //    (length in pulses; bare = how many bare cards were read)
Tape.schedule(events, opts)    // opts: { bpm, speed } -> [{ t, dur, hz, gain }] in seconds, gain 0-1
Tape.midiToHz(note)            // 69 -> 440
Tape.pulseSeconds(opts)        // { bpm: 120 } -> 0.125
Tape.createPlayer(opts)        // opts: { bpm, speed, hiss (0-1, default 0.15), onTick(state) }
```

`parseCards`, `schedule`, `midiToHz` and `pulseSeconds` are pure and need no browser. `tests/tape.test.js` tests them.

The player builds its audio graph on the first `play()`, so a page can create it at load without starting audio before the user asks. Browsers allow audio to start only after a user gesture, so `play()` should be called from a click or key handler.

| Method | Effect |
|---|---|
| `load(events)` | Stops, then threads a new tape |
| `play()` | Plays from the current position (from the start if at the end) |
| `pause()` | Stops sound and keeps the position |
| `stop()` | Stops sound and rewinds to the start |
| `seek(seconds)` | Moves the position; keeps playing if it was playing |
| `setTempo(bpm)`, `setSpeed(s)` | Retimes the tape and keeps the place in the music |
| `state()` | `{ playing, position, duration, bpm, speed }`, in seconds |
| `close()` | Stops and releases the audio context |

`onTick(state)` is called on every animation frame while playing, and once after each change of state, so a page can turn its reels and move its counter. Reels on a real machine change speed as tape passes from one to the other; a page can derive that from `position / duration`.

## Sound

Each note is a triangle wave with a quiet sine an octave above, under a short attack and a decay to a held level, released at the end of `LEN`. A slow shared wobble in pitch (wow, about 4 cents at 0.55 Hz), a low-pass filter around 5 kHz, and a faint high-passed hiss while the tape runs give the sound of a tape recording. The output goes through a compressor, so dense passages do not clip.
