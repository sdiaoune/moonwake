# Moonwake: The Long Dawn — independent gameplay and reliability review

Historical first save/source pass, October 5, 2026. The current independent review is `docs/expansion-play-review.md`; it supersedes the provisional findings here. Scope: native save migration/recovery, movement, exploration, campaign progression, and runtime reliability. Art and audio belong to the other specialist critics. The 60–90 minute first-journey duration is a design target until actual human timing exists; neither a scripted learned route nor a synthetic save harness establishes that duration.

## Native save harness

`tools/check_expansion_save.py` compiles the actual production `src/save.c` with GBDK in a small native CGB ROM. It uses the production game/level declarations, defines the game globals separately, and lets real joypad presses invoke `save_write` and `save_reset`. Artificial sample states and cartridge SRAM fixtures are explicitly save-test inputs; they do not establish gameplay progress. The Python observer reads symbol-address RAM but does not write it. Fixtures are supplied as SRAM before boot.

The harness independently implements the CRC and checks production-written slot bytes against it. It compares every SRAM byte outside the expansion's owned storage with the input fixture, including both original Moonwake v1 slots and Signal Bloom-like sentinels. Output ROM, source snapshot, hashes, earned harness save files, and JSON results live in `build/critic-expansion-save/`.

The initial save source SHA-256 was `a75330bac876d04cafa95d371cd1c3b3e2cd2daf65ed726c70520c6f2e9bdb0c`; its native harness ROM SHA-256 was `7163e17149a2ddfd7baf77fbe9b218665fa451443fb4d9c5da6989b0e79acb29`. Thirteen initial checks passed. The source and report hashes must be refreshed after any save fix; this initial result is not approval of a later untested source.

Verified initial behaviors:

- Partial v1 migration preserves unlocks, first-room discovery bits, sound preference, and deaths. Expanded speed medals/times reset because three-room stages are incompatible with the original records.
- Completed v1 migration unlocks stage twelve, the first new world, and clears expanded completion. A migrated v2 save reboots without re-running migration.
- All twenty-four nine-bit seal words, nine current-run seals, room two, checkpoint state, health, stars, 60,000 stage ticks, and long best-time words persist through a native save/reboot.
- A second room-one transaction preserves five current-run seals, the full pickup bitmap, and a journey value `0x89ABCDEF`, exercising all four journey bytes.
- Sequence selection handles `65535 → 0` for both legacy and v2 slots.
- Latest v2 CRC damage restores the prior valid transaction. Damage to both v2 payload CRCs gives safe initial progress without importing the old v1 playthrough.
- New Game reset persists into v2, clears expanded progress, and leaves legacy and unrelated SRAM bytes untouched.
- CRC-valid records with invalid room or health bounds are rejected.

## Defects reported to integration

**P2 — Legacy resurrection after both v2 magic bytes are lost.** The first source checks for recognizable MW-v2 headers before permitting migration. If both leading magic bytes are damaged while legacy v1 remains valid, it re-migrates the old playthrough. A native pre-boot fixture reproduced this. Root is adding an independent four-byte generation fence after a committed v2 write. The final harness must test damaged headers with that fence intact. If both saves and the fence are destroyed, that SRAM is indistinguishable from never-migrated data while legacy bytes remain immutable; the limitation must be stated accurately.

**P2 — Post-death stale world coordinates.** `world_tick` caches player coordinates, then a fatal enemy/projectile collision can call `restart_checkpoint` inside `hurt`. Continuing the old tick can evaluate checkpoint/room-goal conditions using the pre-death coordinates. Root was asked to abort that world tick after a death; controller verification remains required.

**Teaching check — Room-specific lessons during continuous transitions.** The content API supplies `level_intro_room`, while the initial UI calls room-zero `level_intro` only and advances with a generic section notice. Wind first introduced in rooms one/two needs a brief readable direction cue or equivalent visual teaching. The uninterrupted room transitions should retain their pace.

## Remaining campaign review

The integrated ROM must be copied with its symbols before testing. Controller observations need post-physics hooks rather than intermediate RAM snapshots. Required checks include room transitions retaining stage clock/stars/run seal bits, checkpoint retry and power-cycle room resume, mover carrying and pause phase, wind teaching, four distinct boss tells and second phases, current-versus-best rank behavior, Atlas pages and back-navigation, mute/reset, busy-scene cadence, and the final linear campaign proof.

Exploration will be judged by real authored choices and discoverable side paths. More rooms or larger pixel distance alone does not establish a stronger adventure. Routes should contain memorable local landmarks, optional returns and alternate approaches, readable stable catches, and meaningful differences between worlds. No gameplay or design score is assigned before playing the integrated expansion.
