# Moonwake independent play critic — final native build

Reviewed October 4–5, 2026. Scope: movement/fun, level design, progression/replay, and technical reliability. Art, world originality, and audio are evaluated by the other critics. Scores reflect the actual compact game and the evidence below; the requested 9.0 target does not determine a score.

Final ROM SHA-256: `9310fa3d598b72b41c56b46f1a99b373b7176dcb38d1fc5de795f1520ab38bc7`.

## Outcome

The final native ROM is playable from a blank save through all twelve stages, all thirty-six seals, six boss hits, and the ending. My independent fresh replay recorded every clear event, earned twelve actual S ranks, and finished with zero deaths. Completion, unlocks, seals, and best medals survived emulator shutdown and reboot. No coordinates, health, unlocks, collected items, or running RAM were changed to produce this result.

The movement, replay loop, and emulator reliability now meet a 9.0 aspiration in my judgment. Level design remains 8.8: the late mechanics substantially improve it, but several stages still use the same broad-ground and upper-seal rhythm. I do not certify a commercial hit or physical Chromatic behavior from an emulator test.

| Category | Final score | Basis |
|---|---:|---|
| Movement / fun | 9.0 / 10 | Responsive variable jump, direction-correct dash, useful refresh/bounce interactions, forgiving recovery, chain reward, and measured native cadence. |
| Level design | 8.8 / 10 | Fair routes and clear optional goals; late mandatory spring/crumble/dash-gap encounters improve pacing, while stage structure and combat strategy still repeat. |
| Progression / replay | 9.0 / 10 | Permanent collection, per-run ranks, calibrated targets, current-versus-best distinction, Atlas replay, immediate Continue persistence, and unlimited checkpoint retries. |
| Technical reliability | 9.1 / 10 in emulator | Full linear completion and save reboot, actual checkpoint death/retry, menu-state preservation, mute/reset handling, CRC fallback, and busy-finale profiling passed. |

## Test evidence

`tools/critic_play.py` copies the ROM and symbols before testing. Reports live in `build/critic-play/` and `build/critic-play-round2/`; every final report contains the ROM hash above.

1. **Full fresh linear replay.** `replay-report.json` consumes the final joypad recording with blank SRAM, without snapshots or further planner decisions. All twelve clear callbacks reported three seals and current rank S. All twelve saved seal bytes were 7 and medals were 3. The 16,969-video-frame trace includes menus and story/clear pauses; its roughly 4 minute 43 second duration at nominal 60 Hz is an optimized learned route, not a claim about a first-time player's campaign length.
2. **Independent opening play.** `report.json` records tap/held jumps, both dash direction changes, two genuinely collected seals, a real pit death, Select checkpoint retry, Pause → Atlas → Back before and after the checkpoint, a direct-controller safe-route clear, and a second fresh linear replay of that opening route. Checkpoint retries preserved earned seals and restored health. Atlas Back preserved the active run.
3. **Rank behavior.** `rank-report.json` earns three seals and S on stage zero, then reboots and replays with zero seals. That replay shows B ARRIVED while the best medal stays S. Permanent seal collection therefore cannot substitute for collecting the three seals in the current S-rank run.
4. **UI and audio settings.** `ui-report.json` verifies Help/Back, an earned next-stage Atlas selection, New Game's two-press confirmation, navigation canceling the armed reset, reset persistence, immediate Continue persistence when starting stage one, sound OFF muting both music and jump/dash SFX, mute persistence after reboot, and sound ON restoring APU power. Reset cancellation explicitly captures the normal prompt before a new first B press; an earlier report label had captured after that new press.
5. **Earned-save fault injection.** Only copies of actually earned SRAM were damaged. Corrupting the latest transaction's payload selects the prior valid CRC slot. At completion, slot 72 contains completed=1 and slot 71 contains completed=0: fallback correctly restores stage eleven and all thirty-six seals, losing only the final completion transaction. Damaging both slots' payloads produces safe fresh progress. Ordinary undamaged completion reboot restores completed=1.
6. **Lantern return.** `lantern-report.json` traverses to an authored lantern with controller input, touches it near the eight-bit frame wrap, leaves for more than 220 frames, and returns. An actual contact at the lantern's location increments the combo and restores charge again. The observer discards events belonging to rejected planner branches. Source review also confirms cooldowns decrement independently of player proximity; the old signed-deadline wrap hazard is gone.

## Movement and performance

Per-frame opening sampling measures 18.875 px jump height for a one-frame tap and 59.375 px when held. The previous round's 45.3125 px held value missed the apex because sampling began after thirty frames; this was a critic measurement error, not a physics limitation. A six-tick buffer/coyote window, fast dash, broad landings, and lantern refills give the small screen room for expressive play. Passive springs now retain their full launch rather than being clipped by released A. Three-hit chains visibly heal, and checkpoints visibly report their save.

Opening cadence is 120/120 idle and 75/75 running. `arena-report.json` measures the actual controller-earned final arena, including motion away from the right wall:

| Probe | Game ticks / video frames |
|---|---:|
| Arena idle | 120 / 120 |
| Run left or right | 45 / 45 |
| Ground dash left or right | 40 / 40 |
| Held jump | 90 / 90 |
| Air dash left or right | 90 / 90 |
| Actual six-hit finale input trace | 402 / 403 |

The complete fight has one missed refresh rather than sustained slowdown. Its six hits, retreat/recoil landings, phase change, and chain healing occur without losing health or a life. The camera's largest measured span is about 31% of a frame and drawing through the HUD entry about 25%. These hooks locate the previously costly pickup rendering; they are not a universal worst-case CPU proof. Death/checkpoint redraws and scene loads intentionally pause normal play and should not be counted as ordinary movement frame drops.

## What improved after round 1

Mandatory spring use in Glasswater Run, recoverable main-route crumble in Pendulum Steps and Sleepwheel Express, and Stardrift Current's wider dash/lantern crossing add real rhythm changes. Every seal route and those altered main routes are represented in the successful fresh replay. The finale now has a warm twelve-tick shot tell, a higher second phase, faster shot cadence, alternating projectile heights, and an intact flashing boss body. Atlas/clear screens expose targets and best times; S requires fresh collection. Continue saves the stage immediately. These changes address the largest reliability, feedback, and repetition concerns from the first review.

## Remaining design limits

The campaign remains a short arcade adventure. Most stages offer three upper seal excursions off broad static ground, and many enemies are solved with the same dash approach. Late spring/crumble/gap changes help, but they do not completely distinguish each world's play rhythm. To raise level design above 9, I would author one characteristic encounter per world using existing mechanics: a safely introduced thorn to interrupt dash repetition, a short lantern relay with a visible stable catch, and an enemy-bounce crossing that rewards deliberate timing. Such data changes need a new native replay, rather than a score increase on paper.

The boss's shots travel left. Crossing to its right is a legitimate, readable counterstrategy and the clean six-hit trace uses it; that side largely neutralizes projectile pressure. A later revision could aim one explicitly telegraphed second-phase lane toward the player's side while preserving a safe landing window. The present fight escalates visually and in shot timing, but its successful retreat/attack cycle remains similar across all six hits.

The calibrated pars leave room for a good human run; all-seal proof times range from about 18 to 28 seconds per stage and pars from 26 to 42. Earning S is now a meaningful fresh-collection task, although a practiced player can beat these targets comfortably. Broader human play is still needed to tune challenge and first-play duration. Physical cartridge readback and Chromatic input/display/audio tests belong to the deployment pass; this review claims only the native emulator results.
