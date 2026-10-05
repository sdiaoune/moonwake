# Moonwake independent play critic — round 1

Reviewed October 4, 2026. Scope: movement/fun, level design, progression/replay, technical reliability. Visual and audio scores belong to the separate critic; their assets were still being polished during this review. A 9.0 target is an aspiration, not a score requirement.

## Evidence and limits

I tested copied native ROM builds with PyBoy, actual joypad inputs, screenshots, and symbol-address RAM reads. No player coordinates, unlocks, health, pickups, enemy flags, or boss state were written. Emulator snapshots repeated opening probes and searched ordinary controller jumps. They do not substitute for a fresh linear completion trace.

The repeatable critic script is `tools/critic_play.py`; its isolated artifacts are in `build/critic-play/`. Early build SHA-256 was `04cdb1aa128eb5c55ad889fd065601e67ed8ce4e7e38048b94a457a255976ce8`. Latest retest SHA-256 was `94462da52a5263a43e832b115fc12599b8b3b302844c0aea04784e9af64e7f6a`; the JSON report records the exact copied ROM hash on each run. I completed the first stage with two earned seals, no deaths, and an 18-second game timer, then replayed the accepted inputs from a fresh emulator without snapshots. The replay reached the same clear state. Separate controller probes walked into a real pit and used Select: both returned to x840 with checkpoint active, three health, and the two earned seals intact. A complete campaign review remains conditional on the root's fresh-input replay. This review makes no physical Chromatic test claim.

## Changes prompted by this review

1. **Wrong-way dash, fixed in controller retest.** On the early build, LEFT+B from the initial right-facing pose moved right at 5.75 px/tick; RIGHT+B from left-facing moved left. Input direction now selects the initial dash direction; the source also locks facing during an active burst.
2. **Atlas Back discarded an active run, fixed in controller retest.** Before the first save, Pause → Atlas → B returned to the title. After two seals and the checkpoint, the same sequence restarted at x24 and cleared checkpoint activation. The later build preserves checkpoint activation, two seals, nine stars, and x843.6875 when returning. Atlas entry now uses a descriptor-only loader and preserves gameplay arrays.
3. **Replay goals were invisible, fixed.** Best times were saved but never displayed, and the numeric S-rank par was absent. Atlas and clear screens now show BEST/PAR. The rank label was shortened to fit its native text width.
4. **Cache buffer overflow, fixed in source.** A new scrolling cache indexed 18×32 entries through buffers declared for a 20×18 title map. Both buffers are now 576 bytes; title uploads still copy their own 360 entries.
5. **Moving cadence, resolved in opening retest.** Early running probes measured 60/75 and 61/75 game ticks per emulator frame. A later build that checks local pickup buckets measured 75/75 running and 120/120 idle. Busy later-world routes and the boss still need measurement before making a whole-game 60 Hz claim.
6. **Save test harness flush, fixed.** The shared tester originally appended updated SRAM after the input BytesIO's 8192-byte cursor, so reboot read the original blank prefix. Seeking to zero before emulator stop fixes this test artifact. With an actually earned save, reboot restored the next-stage unlock, seal bits, and medal. Corrupting the latest earned slot selected the prior valid slot; invalidating both signatures produced a safe fresh start.
7. **Spring jump cut, fixed in source.** A passive spring landing originally set velocity to −126, then the ordinary released-A jump cut clipped it to −48 on the next tick. A spring timer now exempts that automatic bounce from the variable-jump cut. Later spring stages still need controller verification.

## Remaining priorities

**P1: finish native campaign validation.** The opening now runs at full measured cadence, the first stage has a fresh linear replay, and checkpoint pit-death/Select retries pass. The full twelve-stage route, all optional seals, the revised boss, and later-world busy-scene cadence must be covered before technical sign-off. A failed shared planner must not be mislabeled as an impossible jump; in this review, direct A+dash inputs crossed the first-stage gaps that the planner initially failed to solve.

**P2: campaign variety is still conservative.** All twelve main routes use solid platforms exclusively. Eight stages overwhelmingly repeat 24-pixel gaps; rises are usually ±16 pixels. Optional branches add springs, crumble, and lanterns, but every stage follows the same three-seal upper-route structure. This is accessible and pleasant, yet the campaign risks feeling like the same short phrase played against four beautiful paintings. Preserve a safe main route, while giving each world one memorable encounter that changes the player's rhythm: a lantern chain with clear reward feedback, a recoverable timed crumble sequence, an enemy bounce crossing, or a later thorn arrangement introduced safely.

**P2: retest the revised finale.** The original stationary six-hit boss repeated one low projectile stream. Root has added a second phase below three HP: higher drift, faster shots, and alternating shot heights. This addresses escalation in source; the opening and readability still need actual boss play. A visible tell and a deliberate opening for an aerial dash would help the finale feel authored.

**P2: tune S-rank targets against measured runs.** The first-stage two-seal run took 18 seconds against a 48-second par. The full all-seal run should establish a reference for each stage; then add a deliberate allowance for a good human run. Current pars may award the top rank without meaningful time pressure. An S target around 25–40% above a clean representative all-seal run is a tuning starting point, not an automatic rule.

**P3: collection feedback can explain the game's hook better.** Lantern touches and enemy bounces build a combo, but the counter is invisible. The soundtrack responds to it; a small readable chain indicator or a brief achievement pulse would connect action to reward. The checkpoint notice counter is also present in the source without a visible notice. Players should immediately understand when a risky line has become a safe retry.

**P3: native UI still has small ambiguities.** The Atlas footer clips PAGE to PAG at 20 columns. An unplayed level displays BEST 000S, which can look like a zero-second record; show a dash until a time exists. Continue currently loads the last stage written by a seal/checkpoint/clear save; starting the next unlocked stage does not immediately save that new stage selection. Confirm the intended resume behavior before polishing the label.

## What works

The variable jump is clear and useful. The opening measured about 18.875 px for a tap. The original held-jump probe started sampling after thirty frames and missed the apex; its reported 45.3125 px was an undersampling error. Round 2 samples every frame and measures a 59.375 px held jump. Six-tick coyote time and jump buffering are appropriate for a portable screen. Air dash refresh through lantern contact is a promising expressive movement hook. The character settles quickly when direction is released, broad first-stage surfaces allow experimentation, and the optional first roof seal can be reached without damage or a death.

Three health points, unlimited retries, checkpoint healing, permanent seal collection, and stage replay reduce punishment without removing goals. Separate best times and collection ranks make it possible to learn a route gradually. The CRC save uses two alternating slots and writes the signature last. Earned-save reboot and corruption fallback checks passed; the full rebooted campaign report remains necessary before final sign-off.

## Provisional scores

These scores assess the playable build and actual evidence, not the commercial ambition. They should be updated only after fixes and broader play.

| Category | Score | Reason |
|---|---:|---|
| Movement / fun | 8.8 / 10 | Strong jump contrast, useful dash, direction/menu fixes, and measured full opening cadence; broader play still needed. |
| Level design | 7.8 / 10 | Fair introductory geometry and optional routes; twelve-stage rhythm remains highly repetitive, final encounter unplayed. |
| Progression / replay | 8.3 / 10 | Persistent optional seals, ranks, times, unlimited retry; new BEST/PAR display helps, but feedback and Continue semantics need refinement. |
| Technical reliability | 8.8 / 10 provisional | Integration fixes, first-stage fresh replay, and earned-save resilience pass; full campaign and busy-scene cadence remain. |

I cannot honestly certify 9.0 in these categories yet. A successful end-to-end replay establishes reachability and persistence; it does not by itself raise the fun or level-design score.
