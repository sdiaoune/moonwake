# The Long Dawn release validation

The v2.0.0 ROM is **524,288 bytes**, SHA-256 `6ef653eba34dae18385501266ee266b689d857823db28ca5fd2c3d304f6a0721`. Header and global checksums are valid. It is a native **CGB-only, MBC5 ROM with battery-backed 8 KiB SRAM**, built with GBDK-2020 4.5.0. A standalone source rebuild in a fresh directory matches every ROM byte; the release source archive is checked against the same build-input hashes. See the [rebuild report](../dist/reproducible-build-report.json). All evidence below concerns this expansion unless explicitly labelled historical.

## Campaign and exploration

The [controller campaign report](../dist/playtest-report.json) verifies **24 completed stages, 72 sections, all 216 optional seals, all four bosses, and zero deaths**. The planner uses actual joypad inputs, with emulator snapshots to search possible routes. Rejected branches are discarded. A separate emulator then starts with blank SRAM and replays the [accepted recording](../dist/verified-inputs.json) linearly, without snapshots or gameplay-memory writes, reaches the ending, and checks saved completion after reboot. ROM hashes bind both stages of verification to this exact build. A separate [main-path recording](../dist/main-route-inputs.json) and [report](../dist/main-route-report.json) verify native contact with all 767 annotated landing surfaces. The [junction tests](../dist/junction-report.json) cross all four new bridges in both directions, activate all seven added clues, and reach a seal beyond each link; each path passes a blank-SRAM linear replay. All 24 S medals and 216 discoveries also survive [native reboot](../dist/rank-reboot-report.json).

The accepted recording contains 108,466 video frames, about **30.1 minutes of learned, preplanned controller play**. It is not a first-time human measurement. The requested **60–90 minute first journey remains a design target**; player pace and curiosity can make a run shorter or longer. Seals do not gate completion.

The [capture manifest](../dist/capture-manifest.json) binds 72 fresh linear-replay room images, title, and ending to the same ROM. Additional planning captures are separately labelled. Every native image is 160 × 144; enlargements use nearest-neighbor sampling. The [teaser manifest](screenshots/teaser-manifest.json) records the exact input hash and sampled source frames for eight world excerpts and four boss excerpts. The 24.8-second teaser comes from another fresh blank-SRAM replay of the accepted recording, with no composited gameplay or game-state edits.

## Saves and native sound

Twenty [native save-harness checks](../dist/expansion-save-report.json) compile the exact production save source and use explicitly synthetic SRAM fixtures supplied before boot. Controller presses invoke production save/reset; observers only read memory. Checks cover original-save migration, 24 nine-bit collections, current room/checkpoint/health/stars, room pickup bits, stage/journey clocks, pending clears, sequence wrap, CRC fallback, reset, and invalid-record bounds. All changed SRAM bytes stay within the new two 192-byte slots and four-byte generation fence; old Moonwake slots and Signal Bloom sentinel bytes remain exact.

The generation fence prevents damaged v2 slots from resurrecting an old v1 game. If both v2 headers **and the fence** are destroyed, that SRAM is indistinguishable from a legacy-only cartridge without changing the preserved older bytes. This limit is tested and documented.

[Native APU captures](audio/render-report.json) link the exact production music source into a CGB harness. All **15 themes develop over 32 bars**, advance through all 256 score steps, loop correctly, and show activity on all four channels. Captured PCM has no clipped samples. Additional checks cover eight effects, lead continuity during effects, mute/freeze/restart, and scene selection. These measurements verify implementation; they do not substitute for direct musical listening or physical-speaker evaluation.

## Art, runtime, and review

The art validator decodes checked-in native tile data, checks palette and VRAM limits, fonts, seams, sprite reservations, and verifies preservation of the original world's native pixels. Static campaign validation checks generated sources, data capacities, room coordinate limits, route surfaces, pickups, and preservation of the original twelve rooms. Static geometry alone is not evidence of successful dynamic traversal; the recorded controller runs supply that evidence for the paths actually traversed.

Independent [play/save review](expansion-play-review.md), [visual/audio review](expansion-visual-review.md), and [scoped ratings](../dist/quality-review.json) document observed strengths, concrete fixes, and remaining limits. Scores are agent assessments, not human customer ratings. Most scoped categories meet 9.0; level pacing/variety remains 8.6, boss encounters 8.8 and the provisional fun judgment 8.9. Those limits are reported rather than hidden. The independent full final replay measures 98.27% active-room cadence; the slowest whole room is 93.86%. Four boss arenas range 97.53–99.48%. Brief save-on-seal hitches remain. Subjective fun, first-player timing, direct musical listening, and physical display/control/speaker behavior remain separate from emulator verification.

## Chromatic installation

**FlashGBX currently detects no connected device**, so this expansion has not been written to the user's cartridge or independently read back from it. The original [v1.0.0 release](https://github.com/sdiaoune/moonwake/releases/tag/v1.0.0) was installed with FlashGBX and its ROM was independently read back byte-for-byte. That historical result does not certify a v2 hardware installation. Physical control, display, and speaker playtesting was not observed by the build team.

Private cartridge saves, earlier game backups, installation paths, and development snapshots are excluded from the public project. Public code/tools/docs use MIT; original art/font/music/captures use CC BY 4.0. Bundled browser and runtime notices retain their original licenses.
