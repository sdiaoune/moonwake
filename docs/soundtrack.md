# Moonwake soundtrack

Moonwake's score is original, native four-channel Game Boy Color music. The
production ROM plays every note itself. The WAVs in `docs/audio/` are captures
of that same compiled C sequencer running on PyBoy's emulated APU, rather than
host instruments layered over silent gameplay.

## The musical idea

Kip's signature is an open E–B leap, a small step to C#, and an answer on G#.
That leap feels like setting out over the sleeping sea; the answering phrase
comes back down to earth. The title introduces it, Saffron Harbor makes it
springy and syncopated, and the ending returns it with longer breaths. The
other worlds use new melodies, rhythms, harmony and articulation.

The score uses sixteen-bar, 128-eighth-note phrases rather than a short
repeated arpeggio. A and B phrases trade short plucks against longer tones,
the third four-bar section lifts the register, and the last section turns
back toward the opening. Rests are part of the tune. Long notes use a slower
envelope so a tied quarter note remains audible; short notes keep their
percussive attack.

| Scene | Track | Tonality | Approximate tempo | Intent |
|---|---|---|---:|---|
| 0 | A Scarf for the Sleeping Sea | E major | 120 BPM | Warm invitation; the scarf melody comes into focus over spacious answers |
| 1 | Persimmon Postcard | E major | 150 BPM | Bright rooftop pop, offbeat chords and alternating root/fifth bass |
| 2 | Rain on a Giant Lotus | D minor / Dorian color | 129 BPM | Skipping rain rhythm, minor warmth and a raised sixth in the G-major answer |
| 3 | Brass Clock, Violet Sky | C# minor | 164 BPM | Ticking syncopation, sharp pulse timbre and asymmetrical bass pickups |
| 4 | The Whale That Carried Tomorrow | A major | 113 BPM | Floating melody, longer phrases and the most spacious drum pattern |
| 5 | Wake Up, Sleepstorm! | C# minor | 180 BPM | Urgent call and response, low openings and a rising confrontation phrase |
| 6 | A Little More Sky | E major | 150 BPM | A tonic fanfare and celebratory answer |
| 7 | Home in the Open Sky | E major | 106 BPM | The scarf theme returns with room to breathe |

## Hardware arrangement

Channel 1 carries the lead. Channel 2 carries a quieter answering chord
voice and temporarily plays effects. Channel 3 is a smooth 32-sample triangle
bass. Channel 4 supplies length-gated kick-like noise, snare and closed hats.
Energy adds a little chord brightness and occasional hats; it does not change
tempo or replace the melody. Every track has a distinct chord rhythm, bass
rhythm and drum pattern. The instruments remain restrained enough for long
portable sessions.

Jump, star, hurt, lantern, dash, clear, spring and boss-hit cues are original.
Jump rises a fourth; dash falls in a clean glissando; lantern climbs through
open fifths; the goal quotes the scarf motif. They borrow channel 2, leaving
the main tune and bass running. The chord state continues updating while an
effect plays, so the current harmony returns when the effect ends. Higher
priority cues can interrupt lower priority cues.

The register behavior follows [Pan Docs' audio register reference](https://github.com/gbdev/pandocs/blob/master/src/Audio_Registers.md).
Wave RAM is written with its DAC off. The wave channel sounds one octave below
the pulse channels at the same period. Pulse rests retain the powered DAC at
zero output rather than toggling it. Mute powers down the APU, freezes the
sequencer clock, and restores its instrument state on resume.

## Capture and verification

Run from the repository root:

```sh
GBDK=/path/to/gbdk .venv/bin/python tools/render_music.py
```

This builds a CGB MBC5 harness against the exact production `src/music.c` in
bank 7. It renders one complete phrase from each scene at 24 kHz, then captures
all eight effects and a mute/resume exercise. The output uses fixed gain and a
20 Hz high-pass filter to remove the emulator's unsigned DAC offset, matching
the purpose of the physical hardware's analog DC removal. There is no
per-track normalization, reverb, EQ, limiter, arrangement change or sampled
instrument. Source and harness SHA-256 hashes are saved in the report.

`docs/audio/render-report.json` records phrase completion, channel activation,
PCM peak, RMS, clipping, mute behavior and the actual file hashes. All eight
captures complete 128 steps and activate all four channels. The capture also
hashes NR10/NR11/NR12 and score position after each of 480 sequencer ticks with
and without the eight effects. Equal hashes demonstrate that this sequence of
effects preserves the channel 1 instrument/volume writes and score timing.
Frequency registers are write-only and are deliberately excluded from this
register comparison.

The WAVs and numerical checks are actual emulator evidence. They verify
generation, continuity and levels; they do not establish a subjective 9/10
rating or physical Chromatic speaker quality. No physical hardware listening
test is claimed here. The recordings are provided for independent listening.

## Integration API

All five entry points are `BANKED` and declared in `src/music.h`:

```c
void audio_init(void);
void audio_scene(uint8_t scene);
void audio_tick(uint8_t energy);
void audio_sfx(uint8_t effect);
void audio_enable(uint8_t enabled);
```

Call `audio_init` once, select a scene when the game state changes, and call
`audio_tick` once per video frame. Re-selecting the current scene does not
restart the score. Effect and scene numbers match the production contract.
Invalid scenes select the title; invalid effects are ignored.
