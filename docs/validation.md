# Release validation

v1.0.0 is 262,144 bytes, SHA-256 `9310fa3d598b72b41c56b46f1a99b373b7176dcb38d1fc5de795f1520ab38bc7`. Header/global checksums are valid. It is CGB-only, MBC5 with battery-backed 8 KiB SRAM.

The public source was rebuilt using GBDK-2020 4.5.0 and matched this ROM byte-for-byte. The same build was previously written with FlashGBX and independently read back from a ModRetro Chromatic cartridge, with all ROM bytes matching. Direct physical control, display, and speaker playtesting was not observed by the build team.

The controller-only planner clears twelve stages and earns thirty-six seals. A second fresh emulator replays the inputs linearly, reaches the ending, and restores completion after reboot. See the [campaign report](../dist/playtest-report.json) and [recording](../dist/verified-inputs.json).

Additional [replay probes](../dist/critic-replay-report.json) check CRC fallback and safe startup after corruption. Other critic reports cover checkpoint retention, reset confirmation, mute, rank rules, lantern cooldown across frame wrap, and boss-arena cadence. Actual arena combat missed one refresh in a 403-frame sample. Art checks cover decoded tiles, palettes, sprite reservations, fonts, and seams. APU capture verifies eight themes, channel activity, unclipped PCM, mute, and melody continuity during effects.

[Review scores](../dist/quality-review.json) are scoped feedback from separate agent critics, not human customer ratings. Not every category was certified at 9/10; level design and audio received provisional 8.8. Subjective listening and broad human playtesting remain unmeasured.

Private cartridge saves, earlier game backups, installation paths, and development snapshots are excluded from the public project.
