# The Long Dawn — independent play and save review

Release review, October 5, 2026. Scope: movement, exploration, progression, native save behavior, and runtime cadence. Separate critics assess art and audio. The final integrated ROM passes this review's controller and persistence checks. The scores remain scoped critic judgments; level variety and boss encounters remain below the requested nine. No measured 60–90 minute human duration or physical Chromatic test is claimed here.

Reviewed ROM SHA-256: `6ef653eba34dae18385501266ee266b689d857823db28ca5fd2c3d304f6a0721`.

## Evidence and boundaries

The [public provenance manifest](../dist/critic-expansion-provenance.json) binds nine reports and ten controller traces to this ROM. Earned SRAM bytes remain private; the published campaign and preparation traces regenerate them through actual native play and power cycles. Frozen working evidence is in `build/critic-expansion-runtime/6ef653eba34d/`. Earlier a04/3808 evidence stays private and is not relabeled as release evidence.

[check_expansion_runtime.py](../tools/check_expansion_runtime.py) copies ROM, symbols and route metadata before testing. Read-only symbol observers capture after physics; CPU hooks measure native cycle intervals. Actual joypad input earns progress. Native snapshots repeat isolated probes or search a jump; rejected search branches are discarded. Accepted opening, three-room, rank, replay and roof-network inputs then run linearly in separate fresh emulators. Blank SRAM is used except where a replay test starts from controller-earned SRAM regenerated through its supplied campaign/preparation inputs. Python never writes gameplay RAM or teleports the player.

The complete campaign test is an independent fresh replay of the level specialist's final accepted [controller recording](../dist/critic-expansion-campaign-inputs.json), not an independent blind human traversal. Its [profile report](../dist/critic-expansion-campaign-profile-report.json) observes all 24 clears, 72 rooms, four bosses, all 216 discoveries, every permanent seal word `0x1FF`, zero deaths and the ending. **Every native clear has current rank S.** Stage clocks range from 3,839 to 4,761 ticks, about 64.0–79.4 gameplay seconds per learned stage. The route takes 102,377 gameplay ticks (28.44 minutes), or 108,466 display frames including boot/menu/transitions (30.13 nominal minutes). These measurements cannot establish first-player human duration.

[check_expansion_save.py](../tools/check_expansion_save.py) separately compiles actual production `src/save.c` with GBDK. `GBDK` defaults to `/opt/gbdk` and produces a clear error when the compiler is missing. Native button presses invoke save/reset. Synthetic SRAM and sample states are deliberate standalone save-test inputs, never proof of gameplay progress. Python independently verifies the CRC and compares every other SRAM byte against its input; only two 192-byte slots and the four-byte generation fence may change. Original v1 slots and Signal Bloom-like sentinel data remain exact.

The [native save report](../dist/critic-expansion-save-report.json) contains twenty passing checks, no defects, and production source SHA-256 `a806bc7807b84d3fa7c60c286efc8a3130b6fa2fef102fea859c7c1b9d59120c`. The separate harness ROM hash is `6ff2990e16f83e3999216f425b28717f392a3016c45fb66cffa254b0235ef1bb`. Checks cover partial/completed v1 migration, first-room discoveries, expanded-world unlock, invalidated old speed medals/times, nine run seals, all 24 permanent seal words, 60,000 stage ticks, room/checkpoint/health/stars, pickup bitmaps, all four journey-counter bytes, sequence wrap, CRC fallback, safe invalid-save behavior, reset, bounds and pending-clear flag validation.

## Controls, persistence and UI

The [opening report](../dist/critic-expansion-opening-report.json) passes sixteen checks on the release ROM:

- One-frame tap and held jumps rise 18.875 and 59.375 pixels. Left/right dash initiation responds correctly.
- A controller-earned roof seal supplies a real one-way ledge. DOWN+A drops through it onto a broad lower catch without dying.
- All three opening-room seals are earned through input. The next room retains stage clock, stars and run discoveries; its completed transition save reboots and Continues in room one with those discoveries.
- Fresh blank-SRAM linear opening replay reaches the same state without deaths or snapshots.
- Pause freezes position and stage clock. Pause → Atlas → Back preserves the active checkpoint and discoveries.
- A real pit death and Select retry restore the checkpoint with earned discoveries retained.
- Sound OFF silences jump/dash effects and survives Back to Title, shutdown and reboot.

The independent [three-room run](../dist/critic-expansion-three-room-report.json) earns all nine stage-zero discoveries and S with zero deaths, then replays linearly from blank SRAM. It measures 3,610 gameplay ticks, about 60.2 seconds. Rebooting its earned clear and pressing Continue opens stage one/room zero with current-run discoveries reset and journey time preserved.

The [menu report](../dist/critic-expansion-menu-report.json) verifies first-B reset arming, navigation cancellation, double-B reset and reboot, Help's DOWN+A instruction, and Back behavior. The [earned completion/replay report](../dist/critic-expansion-completed-replay-report.json) proves final-clear Continue returns to the ending, four Atlas pages are accessible, and an active Atlas replay saved after completion resumes its room normally. A current B clear preserves stored best S through clear → Atlas → Back. That B replay also passes a separate linear replay from its genuinely earned active-replay SRAM; its published preparation inputs explain where that SRAM came from.

## Fixed issues and remaining limits

**Save generation marker — verified fixed.** The initial harness reproduced resurrection of old v1 progress when both v2 leading magic bytes were damaged. `MW2!` at A3F0, written after a committed v2 save, now prevents this. Damaged slot headers with the fence intact yield safe initial progress. Destroying both headers and the fence remains indistinguishable from legacy-only SRAM without changing old data; this boundary is explicitly tested.

**Continue after clear — verified fixed.** Persisted `stage_clear_pending` at byte thirteen advances an intermediate clear to its next unlocked stage and routes a final clear to the ending. Validation rejects invalid flags, room combinations and missing unlock/completion. Earned integrated-ROM saves prove both clear cases and ordinary room resumes after campaign completion.

**Fatal-hit continuation — source fixed; actual recovery verified.** `world_tick` now returns when deaths changes after harmful contact and resets boss guard/position on restart. In a controller-earned Manta second-phase arena, three actual projectile hits reduce health 3→2→1, then refill it at checkpoint x1360. Deaths increases once, boss HP returns to six and all nine discoveries remain. No health writes are used. The exact fatal-contact/goal-overlap edge is source-reviewed rather than directly reproduced.

**Hazard freezing and tells — verified.** The [campaign probe report](../dist/critic-expansion-campaign-probes-report.json) branches only snapshots earned by the fresh linear path. Both phases of all four bosses, actual mover contact and a later wind room each pass 240 Pause plus 120 Atlas frames, resume the same room and retain exported player/boss/terrain phase. No physics or `world_tick` call occurs during those intervals. Private projectile counters are not read from guessed addresses. Visible warm-tell OAM samples are captured for all four bosses. The final Sentinel render priority also preserves guard color ahead of shot warning; the visual critic separately checks this cue.

**Wind teaching and occluded landings — improved.** Room notices name the room and show wind direction, Help includes ledge dropping, and the initial occluded Paperboat scenic landing has been raised. The release path covers wind rooms and corrected optional surfaces. Blind player sessions should still judge whether the brief wind cue teaches the mechanic clearly.

**Exploration connections — implemented and independently proved.** [Three roof-network probes](../dist/critic-expansion-network-report.json) make real contact with the four appended bridges, continue along their scenic fork and earn the downstream existing discovery. Each accepted prefix plus branch separately replays from blank SRAM without deaths:

| Room, zero-based stage/room | Actual bridge indices | Connected traversal |
|---|---|---|
| Jellydew Hollows, 18/1 | 24 | Main shelf → roof bridge → returning loop |
| Memory Margins, 21/1 | 24, 25 | Rear loop → paired roof steps → adjacent mover fork |
| Last Lantern Walk, 23/1 | 24 | Scenic ridge → upper bridge → spring fork |

Star and lantern clues reinforce these links. This critic's report proves bridge contact and downstream discovery, not collection of every new clue or both travel directions; the level specialist's separate junction report covers those broader checks. Existing discoveries, main routes and save identities remain stable.

**Level variety — the principal remaining design limitation.** Three taught main spring arcs, two main lantern transfers and a required mover ride improve forward traversal. Seven rooms include a spring/crumble/mover main surface; optional content includes 42 loops, 32 grottos, 32 lantern trails and 23 mover routes. However, roughly 91% of positive main-route gaps are still 24–40 pixels, and familiar shelf/fork families repeat across 72 rooms. The new roof networks add meaningful route choice, but three changed rooms do not erase campaign-wide repetition. A future content pass should vary safe forward rhythms and connect more adjacent forks rather than add compulsory danger or timer padding.

## Replay targets

Release S pars are grounded in observed clean stage times ×1.45, rounded up to five seconds. Stages zero through 23 use:

`95, 100, 100, 100, 100, 110, 100, 100, 95, 95, 105, 110, 105, 110, 115, 105, 110, 120, 110, 110, 105, 110, 105, 115`

These replace the previous 180–280 second targets. All 24 learned nine-discovery clears achieve S on the release ROM. The independent [rank report](../dist/critic-expansion-rank-report.json) additionally proves stage-zero fast all-nine S at 3,610 ticks and over-par all-nine A at 9,754 ticks, both from blank SRAM with zero deaths. The latter advances the real gameplay clock by safe idle input before the same learned route; it does not write the timer. Nine discoveries must be collected again this run. The earned replay also verifies current B cannot overwrite a stored S. Adventure progression remains untimed; fairness of optional S targets still needs blind human tuning.

## Runtime performance

The first dense-room profile exposed all-platform mover scanning even in rooms without movers. Active mover/crumble lists, terrain buckets and cached scenery offset removed this cost. On the release ROM, the independent learned first-three-room profile measures 98.76%, 98.56% and 98.85% cadence; empty mover-phase cost is about 0.7% of a double-speed frame instead of the initial 8.3%.

Full release linear profiling measures **102,377 physics ticks / 104,179 active-room display frames = 98.27% cadence**. Each room's first-to-last-physics interval excludes menu and room loading. The worst whole room is Dreamwhale Dawn (23/2) at 1,650 / 1,758 = 93.86%. Arena spans include all retreats after first apron entry, so leaving the apron does not masquerade as dropped CPU frames:

| Boss | Post-physics draw ticks / display frames | Cadence |
|---|---:|---:|
| Warden | 759 / 763 | 99.48% |
| Manta | 773 / 779 | 99.23% |
| Sentinel | 797 / 802 | 99.38% |
| Dreamwhale | 712 / 730 | 97.53% |

Save-on-discovery spikes reach about 2.8 double-speed frames. This supports strong sustained scrolling, not perfectly uninterrupted 60 Hz. The final map's WRAM heap/end is D20A and stack starts E000, leaving 3,574 bytes; the nested save buffers fit within that margin. Emulator cadence does not substitute for a physical Chromatic session.

## Final scoped scores

These are independent critic judgments informed by native input, source review and runtime evidence, not a prediction of sales or blind human approval. Overall fun is a judgment rather than the table's arithmetic average.

| Category | Score / 10 | Reason |
|---|---:|---|
| Movement and controls | 9.1 | Variable jump, locked dash, refill, ledge drop and mover carry give responsive choices. |
| Exploration | 9.0 | Substantial optional forks and returning loops, with proved connected roof networks in later worlds. |
| Level pacing and variety | 8.6 | Safe catches support flow; similar forward shelf phrases recur across the long campaign. |
| Boss encounters | 8.8 | Four readable identities and phase changes; six-hit dash/stomp combat shares a common rhythm. |
| Progression and UI | 9.1 | Durable room resumes, earned Atlas pages, clear recovery and replay ranks are verified. |
| Replay incentives | 9.0 | Grounded 95–120 second targets, re-earned discoveries, fast S/over-par A and preserved best ranks. |
| Save reliability | 9.3 | Twenty native persistence/migration/corruption checks and exact legacy preservation. |
| Runtime reliability | 9.0 | Full controller proof and good sustained cadence; brief saves and dense finale hitches remain. |
| Overall fun judgment | 8.9 | Inviting movement and discovery; repeated local phrases constrain sustained surprise. |

The remaining blind-player questions are discoverability, S fairness, natural difficulty growth and whether a first journey lasts 60–90 minutes. Those are distinct from native reachability, input responsiveness, persistence and menu behavior already tested. Physical Chromatic playback and cartridge deployment are outside this critic's scope.

## Reproduction

With GBDK installed and PyBoy/Pillow available, the standalone save suite runs with:

```sh
GBDK=/path/to/gbdk python tools/check_expansion_save.py
```

The default runtime command copies the current ROM/symbols/routes and executes the opening suite. Subsequent commands reuse that exact copy:

```sh
python tools/check_expansion_runtime.py
python tools/check_expansion_runtime.py --copy-hash 6ef653eba34d --three-rooms
python tools/check_expansion_runtime.py --copy-hash 6ef653eba34d --menu
python tools/check_expansion_runtime.py --copy-hash 6ef653eba34d --ranks
python tools/check_expansion_runtime.py --copy-hash 6ef653eba34d --profile --require-complete --trace dist/critic-expansion-campaign-inputs.json
python tools/check_expansion_runtime.py --copy-hash 6ef653eba34d --campaign-probes --trace dist/critic-expansion-campaign-inputs.json
python tools/check_expansion_runtime.py --copy-hash 6ef653eba34d --networks --trace dist/critic-expansion-campaign-inputs.json
python tools/check_expansion_runtime.py --copy-hash 6ef653eba34d --completed-replay --trace dist/critic-expansion-campaign-inputs.json
```

The final command first recreates completion SRAM from blank SRAM by replaying the complete campaign inputs, then boots a new emulator with that earned state. The public B-replay trace describes the campaign → power cycle → preparation → power cycle sequence; save bytes are omitted. The tools reject mismatched ROM/input hashes; they do not turn a trace for a different binary into passing release evidence.
