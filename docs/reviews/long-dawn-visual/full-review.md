# The Long Dawn — independent visual and exploration-UX review

Review date: October 5, 2026. This reviewer is separate from the art,
campaign, runtime/UI, and save authors. Scores follow observed evidence;
the requested quality target is not a required conclusion.

## Final 6ef assessment

Reviewed final frozen ROM SHA-256:
`6ef653eba34dae18385501266ee266b689d857823db28ca5fd2c3d304f6a0721`.
The independent final-build probes are preserved under
`build/visual-review/network-check/`. They use a private frozen ROM and
symbols; every report binds that exact hash. The a04 assessment and its
late defect remain below as history rather than being relabeled as final
capture evidence.

| Category | Final scoped assessment | What this score covers |
|---|---:|---|
| Native visual art/readability | **9.0 / 10** | Eight strong native panoramas and four distinctive small silhouettes; final compiled upper routes and corrected Sentinel cues preserve readable cream collision lips and dark hero outlines. Handheld display observation is unscored. |
| Exploration/progression UI | **9.0 / 10** | Final title/help/pause, four Atlas pages, per-room fractions, separate ranks, named/wind arrivals, earned discovery retention and measured eight-frame dark room cut. Human fun and first-journey time are not this score. |
| World identity/presentation | **9.0 / 10** | Distinct world landmarks, invitations, room names and visibly invited upper crossings form a coherent expanded fantasy. A biome still repeats its 256-pixel panorama across nine rooms. |
| Composition structure/originality | **9.0 / 10** | Fifteen developed native 32-bar phrases with distinct new interval/rest/tie signatures and deliberate motifs, independently inspected as score data. This is not a listening verdict. |
| Native audio implementation | **9.0 / 10** | Actual sequencer/APU source, matching production render evidence and independent WAV hash/format/peak/clipping checks. Direct listening, whole-game cadence and physical speaker quality are separate. |

The scores follow concrete corrections and observed evidence; the user's
9.0 aspiration is not a required rating. **Subjective musical impact,
direct listening, unfamiliar-human enjoyment, physical Chromatic controls,
display and speaker remain unscored.** No sales or online-reception promise
follows from this review.

### Final upper networks and UI

`probe_networks.py` independently traverses all four appended one-way
bridge platforms in Jellydew Hollows (stage18/room1), Memory Margins
(21/1) and Last Lantern Walk (23/1), then reaches each destination.
`network-report.json` records exact ROM/routes/save-fixture hashes,
successful inputs and native image hashes. Stage numbering in these reports
is zero-based. Artificial QA Atlas access selects each stage; traversal of
its first room and the new junction uses real joypad input and planning
snapshots, with no running gameplay-RAM writes. This is explicitly not
whole-campaign-earned access or all-discovery proof.

I inspected each actual native source, bridge and destination capture.
The orchard crossing retains a bright cream edge against the dark jade
roots. Both archive bridges keep cream lips and dark undersides separate
from the warm sky, while Kip's dark edge/red scarf remain readable. The
stars and lanterns invite the new connections without obscuring the
landing edges. These are optional connections among existing routes,
not three wholly new background paintings. The probe verifies forward
traversal and visual invitation, not unfamiliar-human discovery or every
reverse path.

The campaign author's later `dist/junction-report.json` additionally binds
fresh blank-SRAM linear probes for **all four bridges in both directions,
all seven clue activations and the downstream seals**, on the same 6ef
ROM with zero deaths. I independently verify the three native capture
hashes/dimensions and inspect those earned screenshots. Their provenance
and controller assertions belong to the campaign author; I do not relabel
my QA forward test as an independent reverse-path replay. The three images
and report are preserved under `network-check/`.

Final `probe_ui.py` again operates fresh title/help/story/opening/pause
and the four Atlas pages/new-world invitations through joypad input.
The later presentation pages use clearly labeled synthetic SRAM; their
999-second best and 697-minute journey values are fixture data, not
measurements. Text fits at native resolution, including the longest stage
names, separate `R` rank header and `DOWN+A DROP LEDGES` teaching.
`probe_transitions.py` earns two seals/fourteen stars before the first room
boundary from fresh SRAM; the counts and `run_seal_bits=3` survive.
`probe_cadence.py` linearly replays that successful final-build input path:
**eight consecutive black frames (0.133 seconds at 60 Hz), zero white
frames, zero LCD-disabled frames** in the measured boundary window. Right
and left wind directions and the Paperboat Reach name remain readable in
the final compiled arrivals.

### Final controller-earned Sentinel regression

`probe_sentinel_earned.py` independently replays a frozen **same-ROM**
accepted controller prefix from **8,192 bytes of zero SRAM**, with no
snapshots or gameplay-memory writes. It reaches and defeats Sentinel with
zero deaths after **80,035 video frames**. The prefix source continued to
stage19/room0, but this critic stops at Sentinel; this is not a claim that
this focused probe independently completed the entire campaign.
`sentinel-cue-report.json` records ROM/input/image hashes and exact states.

The private countdown address is derived read-only from the same-source
GBDK `game-cue.asm` DATA layout, with every public DATA anchor checked
against the frozen symbol map and a compiled timer reference checked in
the frozen ROM. At the actual render hook:

| State | Countdown | Cooldown | Guard | Actual body palette |
|---|---:|---:|---:|---:|
| Guarded warning | 12 | 0 | 1 | **6, coral** |
| Unguarded warning | 12 | 0 | 0 | **3, teal** |

I inspected the actual native screenshots. The whole coral core remains
visible while shielded; the open warning uses the distinct teal body. The
late a04 ambiguity is corrected in final pixels, not merely in source.
Defeat shows HP0 and reveals the exit arch cleanly. Both observations are
controller-earned campaign combat, unlike the separate QA geometry
presentation checks.

### Final audio and limits

The guard/geometry/par revisions do not change native artwork, font/UI
assets, music arrays or APU implementation. I reran the independent music
file/data checker: the source remains
`fce56dc75f34e09f9d859dd22d27d27d19b6a12b5fbe7c5d5210eea31b5da4f6`;
all fifteen score shapes and sixteen WAV hashes/formats/peaks/clipping
counts match the renderer, with zero clipped PCM samples. The detailed
paper-composition and implementation rationale remains below. I have not
listened to or independently rerendered the audio.

### Final campaign/native capture review

The final same-hash campaign author has now published a successful fresh
blank-SRAM linear replay: **24 stages, 72 rooms, 216 seals, four bosses,
zero deaths and rebooted completion**, with **108,466 video frames**.
The exact matching artifacts are `dist/verified-inputs.json`,
`dist/playtest-report.json` and `dist/capture-manifest.json`.
The critic's validator independently checks **all 232 native image hashes
and 160×144 dimensions** in that manifest, including exactly one fresh
linear capture for every one of the 72 stage/room identities. Immutable
artifact copies and all native images are also preserved in
`network-check/`, including `preserved-capture-manifest.json`.

I inspected all eight final nine-room galleries. Cream surfaces, material
textures, room names and wind arrows remain readable; no new clipped
banner, missing material or panorama seam was found. These arrival samples
show room beginnings, not every route point; the separate network/scenic
and combat probes supply evidence at higher and later positions.

The critic also independently replays the **entire matching final**
accepted input recording from blank SRAM with no snapshots or running
memory writes. `probe_final_bosses.py` reaches the ending at **108,466
frames**, observes all four six-hit HP transitions to zero, and independently
asserts completed ending with **zero deaths**. Its capture report binds
ROM/input/native image hashes. I inspected all four actual fight galleries
and the ending: bell, swept manta, faceted core and dreamwhale remain clear;
warning/hit palettes preserve whole silhouettes, projectiles separate from
the scenes, HP text fits and exit arches appear cleanly. The ending sentence,
comma, thanks and Atlas/Title controls fit. This script checks fights and
ending; the author's separate all-discovery assertions establish all 216
seals, rather than this critic claiming an unperformed independent seal
count audit.

No unresolved visual/UI blocker remains in the final samples. Repeating
biome panoramas, related six-hit projectile/bounce boss grammar and the
absence of unfamiliar-human/hardware/listening observations remain real
limits. Source and emulator evidence cannot establish human enjoyment,
first-journey duration, online attention or commercial sales.

## Historical a04 assessment — qualified by the late cue finding

Reviewed optimized ROM SHA-256:
`a04ad0adb68ffb9d0d7e8654aeb09ffcae558f6c309c71be6e6e74a89901da7f`.
The matching controller campaign and fresh linear replay have passed. This
review additionally replayed the final accepted inputs independently from
blank SRAM to capture all four actual fights and the ending.

| Category | Current assessment | Evidence and limit |
|---|---:|---|
| Native visual art/readability | **9.0 / 10** | Eight panoramas, seventy-two matching native room captures, four actual boss fights, scenic upper routes, moving floats and the ending are strong. Physical handheld pixels were not observed. |
| Exploration/progression UI | **9.0 / 10** | Clear per-room seal fractions, separated ranks, readable help/pause, retained discoveries, explicit wind teaching, named arrivals and a measured short dark cut. This does not score human enjoyment or campaign duration. |
| World identity/presentation | **9.0 / 10** | Individual landmarks, invitations and named arrivals form a coherent longer journey. Each biome still repeats a 256-pixel panorama. |
| Expanded composition structure/originality | **9.0 / 10** | Independent score-data review finds fifteen developed 32-bar phrases, distinct new melodies/rhythms and deliberate recurring motifs. This is a paper composition assessment, not a listening score. |
| Native audio implementation | **9.0 / 10** | Source review, matching production-harness evidence and independently checked PCM hashes/format/peaks/clipping support the four-channel implementation. Whole-game cadence belongs to the play critic. |

The scores increased because the reported defects were corrected in actual
compiled pixels. They are not a requirement to rate every category 9.0.
**Direct listening, subjective musical impact and physical-Chromatic
speaker/display/control quality remain unscored.**

Independent evidence is preserved under `build/visual-review/a04-check/`.
The title, help, opening, pause, four atlas pages and four new-world
invitations were operated again through joypad input. Synthetic all-access
SRAM is still used only for later-stage presentation access. In a separate
fresh-RAM controller replay, two seals earned in Lantern Quay appear as
`SEALS 2/3 0/3 0/3` in the atlas after entering Paperboat Reach. The unlocked
row, sleeping stages, missing best time, and unearned rank all display
correctly. `earned-atlas-report.json` records the matching ROM hash and
successful inputs.

The 5ce intermediate build fixed the ambiguous fractions but initially put
rank immediately after the longest stage name, displaying
`SLEEPWHEEL EXPRESSS`. The a04 build moves rank to the seal row and adds an
`R` header. All four compiled atlas pages were inspected after this fix;
the longest names now retain proper separation.

A frame-by-frame linear replay of the a04 critic's own successful opening
path measures **eight consecutive all-black frames**, approximately
**0.133 seconds at 60 Hz**, at the first room boundary. There are **zero
all-white frames** and **zero LCD-disabled frames** in the observed
boundary window. The palette cut starts during one frame, then holds black
while the map changes. Scenery and `PAPERBOAT REACH` return cleanly.
`transition-cadence.json` includes the per-frame color/LCDC observations and
numbered images. This is materially better than the historical eighteen-
frame white flash. It is a short dark cut, not a claimed continuous-camera
pan or measured fade. Rightward and leftward wind arrivals also retain
their immediate direction banners in separate controller probes.

The later-world invitation captures now read, for example, `FESTIVAL LAMPS
DRIFT / WISHES RIDE FLOATS.`, `THE STARS NEED MAPS. / FIND THE LENS KEEPER`,
`JELLYDEW FEEDS FRUIT / FOLLOW ROOT LIGHTS.`, and `EVERY BOOK IS A SKY /
FIND MORNING MARGINS`. All fit the twenty-column window and strengthen the
phoenix fair, observatory, orchard and archive identities.

`probe_scenic.py` additionally uses synthetic atlas access, then controller-
only branch planning to traverse one optional scenic fork in each new
world. It reaches the Cinderpetal Fair and Pearl Meridian moving floats,
the Aurora Orchard upper gallery, and a Dawn Archive high gallery, collecting
the sampled seals. Cream collision lips and Kip's dark silhouette remain
legible against both dark and bright scenery. The cyan float is visually
distinct from stable scenery. These four sampled forks are not proof of all
216 discoveries; branch-planning snapshots and access provenance are
explicit in `scenic-report.json`.

## Final campaign and boss capture review

`build/visual-review/validate_campaign_captures.py` independently verifies
all **136 native image hashes and 160×144 dimensions** in
`dist/capture-manifest.json`. Its seventy-two fresh-linear room captures
cover every stage/room identity exactly once and explicitly identify blank-
SRAM controller replay with no snapshots or gameplay-memory writes.
`capture-validation.json` and eight three-by-three world galleries preserve
this check. I inspected every gallery. No new missing material, clipped
room banner, panorama seam or unreadable collision edge appeared in these
samples. Arrival captures show beginnings of rooms; they do not by
themselves establish the readability of every route segment. The separate
controller scenic probes above cover higher route positions.

The resumed planner's bound phase images begin at stage eighteen, so its
manifest does not contain boss-one/two fight images. I did not substitute
unbound legacy screenshots. Instead,
`a04-check/probe_final_bosses.py` runs the final matching
`dist/verified-inputs.json` in a separate emulator with **8,192 bytes of
zero SRAM**, using only the accepted joypad inputs, no snapshots and no
running-RAM writes. The replay totals **108,449 video frames**, records six
hit transitions to HP0 for **each of the four bosses**, reaches the ending
and has **zero deaths**. Its input-file/ROM/image hashes, frame numbers and
observed states are in `final-boss-capture-report.json`. These findings do
not replace the campaign author's separate all-216-seal validation or
represent a first-time human traversal.

I inspected the four independent fight galleries and ending. The bell,
swept manta, faceted sentinel and side-profile dreamwhale are recognizable
against their actual moving scenery. Dark outlines preserve the shapes;
cyan normal bodies, green/teal pre-shot tells and amber hit flashes retain
whole silhouettes. The sentinel's coral guard state is visibly distinct
from its cyan open state when it is not warning of a shot. A late
frame/state audit found the exception described below. Coral projectiles remain separate from the
teal/blue scenes and visible against the warm archive sky. HP numbers fit,
and defeat reveals the exit arch cleanly. The ending's complete Long Dawn
sentence, comma, thanks and Atlas/Title controls fit the compiled window.

The four fights still use related six-hit, projectile-and-bounce grammar.
Distinct silhouettes and state colors do not by themselves make four
radically different combat systems. This review scores their presentation
and readability; difficulty, fairness and variety belong to the independent
play assessment. All eight worlds also reuse their biome panorama across
nine rooms. The artwork's strong quality and readable foreground support
9.0 here, while this repetition is a real limit rather than seventy-two
unique background paintings.

## Expanded audio composition and implementation

I read the actual `src/music.c`, the soundtrack notes and the production
APU render report. `build/visual-review/check_music_evidence.py` independently
confirms the current music source SHA-256 is
`fce56dc75f34e09f9d859dd22d27d27d19b6a12b5fbe7c5d5210eea31b5da4f6`,
matching the renderer. All fifteen arrays have 256 eighth-note steps and
32 valid harmony bars; notes/rests/ties are within the sequencer's supported
range. The first 128 melody steps of the original eight themes are unchanged
from the preserved original game source. Each of the seven new themes has
a distinct interval/rest/tie signature from every preceding theme.

The structure has substantive development rather than a sixteen-bar phrase
copied twice: the title grows through C# and upper E figures, Ember Festival
uses alternating short G-major turns and breaths, the B-minor observatory
leaves longer tied echoes, the F-major orchard trades stepwise ribbons with
register lifts, and Dawn Archive places the familiar scarf motif inside a
new opening question. The three added boss themes use different contours,
rests, bass/chord masks and percussion: repeated D challenges for Rainbell,
wide F#-minor climbing figures for Manta, and angular C-minor fragments with
narrow pulse duty for Sentinel. The returning motif unifies the journey
without replacing those identities. These are observations of written
composition data, not claims about how enjoyable the recordings sound.

The source runs a leading pulse, answering chord pulse, triangle wave bass
and gated noise percussion on the native APU. Effects borrow the answering
pulse and restore its current harmony; they do not write the lead's
frequency or envelope. Rest DAC handling, tied-note envelope pace, wave-
RAM loading with its DAC off, mute/resume state and eight-bit phrase wrap
are coherent in code. Reselecting a biome scene returns without restarting
its phrase, preserving musical position across ordinary rooms. The source
fits the renderer's bank-seven budget of 7,471 / 16,384 bytes.

I independently check every one of the sixteen provided WAV hashes, stereo
16-bit/24-kHz format, absolute PCM peak and clipped-sample count against the
report. All match; every PCM file has zero clipped samples. I have **not
rerendered** the sequencer or listened to these files. The production
renderer separately records full phrase completion, all four active
channels, per-scene SFX lead-state continuity, mute silence and resume.
Those reported checks are useful implementation evidence, not this critic's
own playback experiment. Its conservative audio-plus-SFX bound is 12.76%
of a normal-speed video frame and excludes game/render work; it is not a
whole-game 60-Hz certificate.

No implementation or composition-data defect found in this pass requires
another production change. Direct listening could still reveal balance,
fatigue, timbral or loop-transition weaknesses that source/PCM checks cannot
settle. Musical impact and the physical Chromatic speaker therefore remain
unscored. The two 9.0 audio assessments above must not be advertised as an
independent 9.0 listening verdict.

## Late Sentinel cue conflict and final limits

The a04 fight capture `3-tell` records `boss_guard=1` with body palette 3
(green), whereas `3-guard` records guard 1 with palette 6 (coral). The
source chose shot warning before the guard palette. Its countdown warning
therefore temporarily hid the invulnerability cue; a green warning body
could be guarded or open. This is a concrete readability defect, despite
the otherwise strong silhouettes. The historical 9.0 art/readability
assessment above was provisional with respect to this combined state.
The final source prioritizes hit flash, then guard 6, then unguarded
warning 3, then normal 7. That change requires actual final-ROM state and
pixel proof rather than source-only acceptance.

Apart from that identified combined-state defect, no other unresolved
visual/UI blocker was found in the reviewed a04 samples. The
remaining limits are the repeating biome panoramas, related small-boss
combat grammar, and the scope of automated evidence. I did not perform
physical Chromatic observation, direct listening, unfamiliar-human fun
assessment or a 60–90 minute first-journey measurement. The latter is a
design target. Emulator input proof and attractive artwork cannot establish
commercial sales, online reception or those human outcomes.

## Historical first integrated-build assessment

Reviewed ROM SHA-256:
`11a9995a61a18bbbfb8787b66b343f4039884e244a85dd0b88c0b18c9dd7f971`.
This is an early integrated expansion build, not the final release.

| Category | Current assessment | Limit |
|---|---:|---|
| Native visual art/readability | **9.0 / 10** | Four new panoramas and playable-world beginnings are excellent; full upper-route/boss combat captures remain to be reviewed. |
| Exploration/progression UI | **7.8 / 10** | Room/seal state is retained, but the actual atlas label is ambiguous and every sampled room arrival produces a conspicuous white flash. |
| World identity/presentation | **8.8 / 10** | The new landmarks extend the fantasy well; repetitive new-world invitations and unnamed live arrivals undersell the authored room identities. |

These are separate assessments. They do not certify full campaign fun,
all-room reachability, physical Chromatic behavior, musical impact, or a
60–90 minute human playthrough. No direct sound or physical-device test
occurred in this review.

## Evidence and provenance

I read `docs/expansion-contract.md`, `docs/design.md`, `docs/art.md`, route
metadata, and the integrated renderer/UI. I inspected the decoded eight-
world contact sheet and 32×32 boss gallery. Native galleries are generated
art evidence, not gameplay screenshots.

`build/visual-review/probe_ui.py` snapshots the actual ROM and symbols
before operating a fresh RAM emulator through joypad input. Its images
and `ui-report.json` cover title, help, opening story/play, and pause.
No running game RAM was edited.

The four atlas pages and beginnings of Ember Festival, Pearl Observatory,
Aurora Orchard, and Dawn Archive were operated through the same controller
interface using the save critic's explicitly synthetic all-access v2 QA
fixture. The fixture is recorded by path/hash and labelled
`not_campaign_completion_evidence` in the report. Access, completion flags,
697-minute journey value, and nine-seal fields in those seeded screenshots
are **presentation fixtures**, not earned player progress or a duration
measurement. The save fixture was not changed on disk.

`probe_transitions.py` records successful joypad paths for the opening
room and two wind-room arrivals. The opening uses fresh RAM and earns
two seals and fourteen stars before entering Paperboat Reach. The wind
samples use QA access only to select Ribbon Skybridge and Cloudfruit
Groves, then traverse their first rooms by actual controller input.
Branch planning uses emulator snapshots; it never writes player state.
The successful paths and provenance are in `transition-report.json`.
They are focused presentation probes, not a complete campaign test.

## What works well

The phoenix kite, ivory shell observatory, jewel orchard beneath aurora,
and immense book cathedral are clearly different compositions rather than
recolored versions of the original worlds. They remain recognizable at
native resolution and in the actual ROM. The new foreground shingles,
shell carvings, root weave, and parchment layers maintain the original
bright collision lips and simpler playable surfaces. Kip's cream body,
red scarf, and dark edge remain legible in the quiet lower play space.
The Dawn Archive's warm sky is especially attractive; its lower dark
water keeps the hero clear despite the bright scenery above.

The four boss silhouettes are meaningfully different in native data:
a hanging bell with clapper, swept comet manta, faceted core with orbit
brackets, and the familiar side-profile dreamwhale. Static silhouette
quality is strong. It is too early to infer combat readability, attack
telegraph quality, or complete sprite-budget behavior from this gallery.

The title preserves a strong recognizable whale composition and adds the
Long Dawn subtitle. The expanded help screen fits, retains readable font
heads, and now states `DOWN+A DROP LEDGES` and `SEALS HIDE OFF ROAD`.
Pause exposes the current room name and `SECTION 2/3`; the stage's nine-
seal total fits the regular HUD. Four atlas pages navigate correctly in
the controller presentation probe.

The fresh first-room transition retains discoveries and the full-stage
clock: immediately before the exit, two seals, fourteen stars, and 854
active ticks were present; after arrival, two seals, fourteen stars, and
882 ticks were present. `run_seal_bits` remains 3. Pause correctly names
Paperboat Reach as section two. This demonstrates one actual cross-room
retention case, not all seventy-two rooms.

The settled wind arrivals display `WIND CARRIES RIGHT >` and
`< WIND CARRIES LEFT`, with a directionally moving scarf cue above the
playfield. These cues are legible in the actual compiled build. Rightward
and leftward examples preserve their current-run seal counts across the
boundary. Movement/play critics must assess the force and timing; this
review confirms its presentation.

## Concrete issues and requested fixes

1. **Room arrivals produce a long white flash.** A frame-by-frame linear
   replay of this critic's fresh-earned opening path observed **eighteen
   consecutive all-white emulator frames** with the LCD disabled after
   `room_id` changed to one: approximately **0.30 seconds at 60 Hz**.
   `transition-cadence.json` and numbered frames preserve that measurement.
   The same immediate white arrival is present in the right-wind sample.
   Since all three rooms share a biome, re-uploading scenery, font, palette,
   sprites, and terrain is redundant. Reuse the uploaded world art, batch
   the new map/object work, and make the transition a controlled dark cut
   or brief fade. Across a seventy-two-room campaign, this flash matters
   more than it did between the original short stages.
2. **The atlas's `ROOMS 3 3 3 R S` label is ambiguous.** The three digits are
   seal counts in individual rooms, not room completion or visitation.
   Explicit `SEALS 0/3 0/3 0/3` is clearer; rank can occupy the otherwise
   unused right edge of the stage-name row. This supports exploration by
   showing where discoveries remain rather than asking the player to
   decode three unexplained numbers.
3. **The arriving room's identity is hidden during normal play.** The
   opening's live cue says `SECTION 2/3 - ONWARD`; its evocative name appears
   only when paused. Showing Paperboat Reach, Drifting Floats, or Windfall
   Lanes on arrival would make the substantial new rooms feel like places.
   Wind direction should retain immediate priority in wind rooms.
4. **New-world invitations repeat generic text.** Cinderpetal Fair, Pearl
   Meridian, Aurora Orchard, and Dawn Archive all repeat their name below
   the heading, followed by `FOLLOW SMALL STARS.` and `EXPLORE YOUR WAY.`
   Those instructions fit but do little to distinguish the phoenix fair,
   lens sanctuary, living orchard, and memory archive. Brief individual
   invitations would strengthen the longer journey without adding menus.

The runtime owner has already applied the explicit seal label, same-world
VRAM reuse/dark transition, and ordinary arriving-room name to production
source; the campaign author has added distinct later-world introductions.
At this writing those changes were **not yet in the reviewed ROM**, so
the ratings above do not silently assume they are verified. The next pass
must inspect their actual compiled pixels and quantify the new transition.

## Historical remaining coverage (superseded above)

After the next stable build, recheck all four atlas pages, wind and ordinary
arrivals, readable room names, full-width glyphs, and the disappearance of
the white screen. Record the measured blackout duration rather than merely
calling it smooth.

Later inspect final-controller screenshots of upper forks, lower alcoves,
moving balconies, jellies, all four boss fights, and the ending. The dark
lower quarter is a good readability decision; pale upper scenery and dense
orchard branches still deserve actual route screenshots. The eight
panoramas repeat every 256 world pixels, which becomes more noticeable
over nine rooms per world. Authored foreground shapes and distinct room
invitations help, but the expanded route geometry—not these beginnings—
must prove that exploration feels varied rather than extended repetition.

A complete campaign recording must match the exact tested ROM hash before
it is treated as replay proof. Human completion time, physical controls,
speaker quality, and enjoyment are separate evidence requirements. This
review should be updated from final captures, not promoted to an automatic
all-category 9.0 while that coverage is still outstanding.
