# Moonwake: The Long Dawn soundtrack

Moonwake's expanded score contains fifteen original native four-channel Game
Boy Color themes. Every scene now has a 32-bar, 256-eighth-note phrase. The
original eight scene IDs and first sixteen bars remain recognizable; new
second acts develop their melodies rather than replaying the opening twice.
Seven additional themes accompany the four new worlds and three midgame
bosses. The production ROM plays the notes itself.

## Musical shape

Kip's signature is an open E–B leap, a step to C#, and an answer on G#. The
opening introduces that scarf motif; Saffron Harbor turns it into rooftop
pop, Dawn Archive recalls it inside a new melody, and the ending gives it
longer breaths. The remaining scenes have their own melody, harmony,
articulation and rhythm. All seven new themes have different interval and
rest/tie sequences from every earlier theme, verified from the score data.
They are not transpositions of an existing track.

Each 32-bar phrase has eight four-bar sections: introduction, answer,
register lift, cadence, a new second act, development, final lift and
turnaround. The lead uses explicit notes and rests across the entire phrase.
Chord inversions rotate between sections, the bass adds an octave pickup at
eight-bar boundaries, and percussion leaves extra room before cadences.
Tied notes hold their initial envelope volume for their full written duration;
short notes keep each scene's plucked decay. The arrangement can loop through
longer rooms without collapsing to a short repeated arpeggio.

| Scene | Use / title | Tonality | Approx. BPM | Captured phrase |
|---|---|---|---:|---:|
| 0 | Title — A Scarf for the Sleeping Sea | E major | 120 | 64.16 s |
| 1 | Saffron Harbor — Persimmon Postcard | E major | 150 | 51.33 s |
| 2 | Jade Monsoon — Rain on a Giant Lotus | D minor / Dorian | 128 | 59.88 s |
| 3 | Violet Engines — Brass Clock, Violet Sky | C# minor | 163 | 47.05 s |
| 4 | Moonwhale — The Whale That Carried Tomorrow | A major | 112 | 68.44 s |
| 5 | Dreamwhale — Wake Up, Sleepstorm! | C# minor | 179 | 42.77 s |
| 6 | Stage clear — A Little More Sky | E major | 150 | 51.33 s |
| 7 | Ending — Home in the Open Sky | E major | 105 | 72.72 s |
| 8 | Ember Festival — Paper Lanterns, Amber Sparks | G major | 150 | 51.33 s |
| 9 | Pearl Observatory — Constellations in a Teacup | B minor | 100 | 76.99 s |
| 10 | Aurora Orchard — Apples of the Northern Lights | F major | 138 | 55.61 s |
| 11 | Dawn Archive — Margins Full of Morning | E major | 112 | 68.44 s |
| 12 | Rainbell Warden — Ring the Rainbell | D Dorian | 163 | 47.05 s |
| 13 | Comet Manta — The Manta Writes a Meteor | F# minor | 179 | 42.77 s |
| 14 | Prism Sentinel — A Prism with No Shadow | C minor | 150 | 51.33 s |

Ember Festival dances around a three-plus-three-plus-two answering rhythm
with a bright low opening and quick upper-register turns. Pearl Observatory
uses patient, separated echoes with sustained notes and a quiet bass pulse.
Aurora Orchard flows through stepwise ribbons and major-sixth color, trading
high answers with a warm middle register. Dawn Archive starts with a new
low-to-high question before the scarf returns as a recollection.

The Rainbell Warden answers repeated bronze-like D notes with a raised-sixth
G-major response. Comet Manta climbs through wide F#-minor figures and brisk
pursuit bass. Prism Sentinel uses narrow pulse duty and angular mirrored
C-minor fragments. Dreamwhale keeps its established scene 5 theme, extended
with a higher second-act confrontation. These descriptions state composition
intent; they are not a claimed listening review.

## Native arrangement and effects

Channel 1 carries the lead. Channel 2 provides a quieter answering chord
voice and temporarily plays effects. Channel 3 plays a smooth 32-sample
triangle bass at half wave-channel output level. Channel 4 supplies gated
kick-like noise, snare and closed hats. Energy brightens the answering voice
and adds occasional hats without changing melody or tempo. All fifteen
scenes have distinct chord, bass and drum pattern assignments.

Jump, star, hurt, lantern, dash, clear, spring and boss-hit cues retain IDs
0–7 and their original identities. Jump rises a fourth; dash falls in a
clean glissando; lantern climbs through open fifths; clear quotes the scarf.
They borrow channel 2, leaving the lead and bass running. The chord state
continues updating during an effect, so the current harmony returns when
it ends. Higher-priority cues can interrupt lower-priority cues. The clear
cue's retrigger times use fixed comparisons rather than division in the
per-frame audio path.

The implementation follows [Pan Docs' audio-register reference](https://github.com/gbdev/pandocs/blob/master/src/Audio_Registers.md).
Envelope pace zero holds tied tones. Wave RAM is loaded with its DAC off,
and the wave channel sounds one octave below a pulse at the same period.
Pulse rests keep their DAC powered with zero amplitude. Mute powers down
the APU, freezes score position and restores its instrument state on resume.

## Reproduction and evidence

Run from the repository root using the project Python environment:

```sh
GBDK=/path/to/gbdk /path/to/python tools/render_music.py
```

If `GBDK` is unset, the renderer finds the repository's portable `.tools/gbdk`
installation, then falls back to `/opt/gbdk`. It compiles the exact production
`src/music.c` in bank 7 into a CGB MBC5 harness and renders all fifteen complete
phrases at 24 kHz. An additional recording captures the eight effects and a
mute/resume sequence. PCM conversion uses the same fixed gain for every
recording and a fixed 20 Hz high-pass for the emulator's unsigned DAC DC
offset. No per-track normalization, limiter, reverb, sampled instruments or
host arrangement is added.

[The render report](audio/render-report.json) records source/harness/file
SHA-256 hashes, score checks, phrase completion, channel activation, clipping,
RMS, peak, mute/resume and CPU observations. Every phrase advances exactly
256 steps, completes one loop and maintains one harness update per requested
video frame. Each activates all four native channels and has zero clipped
PCM samples. Channel-status flags show generation-circuit activation, not
continuous audible output; zero-volume rests deliberately leave pulse DACs
powered.

For each scene, the harness records 480 consecutive sequencer updates both
with and without all eight effects. It compares every byte of NR10/NR11/NR12,
the observable played lead note and score step. Equal traces verify lead
instrument, pitch selection and score timing under this effect sequence.
Frequency registers are write-only and are not presented as readable pitch
evidence. Separate controls exercise 44 completely muted frames and resume
in every scene, check score position remains frozen, observe all four
channels after resume, and verify same-scene selection permits progression
and an invalid scene falls back to the title.

Music code and score data fit in bank 7, without borrowing another ROM bank.
The timing harness samples DIV directly around the BANKED `audio_tick` and
any `audio_sfx` call, outside its own effect-scheduling bookkeeping. The
report gives a conservative bound at 256-cycle resolution in normal CGB
speed; this isolates audio work and does not certify the full game frame
budget. Whole-game cadence remains an integration check.

The WAVs and numerical results are emulator evidence. They verify generation,
levels and the tested continuity behavior. They do not establish a subjective
score, physical Chromatic speaker quality or a hardware listening test.
The recordings are provided for independent listening.

## Integration API

The five entry points remain BANKED:

```c
void audio_init(void);
void audio_scene(uint8_t scene);
void audio_tick(uint8_t energy);
void audio_sfx(uint8_t effect);
void audio_enable(uint8_t enabled);
```

Call `audio_init` once, select a scene at a game-state change and call
`audio_tick` once per video frame. `AUDIO_SCENE_COUNT` is 15 and
`AUDIO_PHRASE_STEPS` is 256. `audio_step` remains an eight-bit observable
counter and wraps naturally after step 255. Re-selecting the current scene
does not restart it; invalid scenes select title and invalid effects are
ignored. World-to-scene order is `{1,2,3,4,8,9,10,11}`. Boss types 1–4 map
to scenes `{12,13,14,5}`. The final Dreamwhale therefore keeps scene 5.
